import datetime
from functools import wraps

from django.apps import apps
from django.conf import settings
from django.db.models import Value, QuerySet
from django.db.models.functions import JSONObject


class ActivityStreamQuerySetMixin:
    def for_activity_stream(self):
        """
        Convert a queryset into a form suitable for serialisation in the activity stream feed.
        """
        fields = self.model._meta.get_fields()
        # Find all fields that are foreign keys or one-to-one keys, as their values will be adjusted on serialisation
        # to match the `id` values required by Activity Stream.
        # NOTE: check other relations, such as ManyToMany, just in case any show up in future models.
        foreign_key_fields = [
            [field.name, field.related_model.__name__]
            for field in fields
            if field.is_relation and (field.many_to_one or field.one_to_one)
        ]
        # Get all non-foreign-key field names so they can be serialised by the database.
        field_names = [
            field.name
            for field in fields
            if not field.is_relation or (field.many_to_one or field.one_to_one)
        ]
        # `JSONObject` expects a dict of JSON names mapped to field names;
        # we just want all fields to have the same name in JSON as they do in the DB.
        json_object_kwargs = dict(zip(field_names, field_names))
        # Add the raw ID value for use in Data Flow,
        # as we modify it when serialising to match Activity Stream's definition of ID
        json_object_kwargs["pk"] = json_object_kwargs["id"]
        return (
            self
            # Get the DB to serialise all non-foreign-key fields to JSON;
            .annotate(json=JSONObject(**json_object_kwargs))
            # Add the list of foreign key field names for later handling as noted above;
            .annotate(foreign_keys=JSONObject(keys=Value(foreign_key_fields)))
            # Add the model class name, as we need that info at feed serialisation time
            # so we can make sense of the foreign key field names
            .annotate(object_type=Value(self.model.__name__))
            # Finally, select the values we want to have in the dict that will ultimately be serialised.
            # This ensures that all querysets present the same model structure,
            # which is a requirement for constructiong a union of all the querysets,
            # which in turn is necessary for delivering a feed containing all objects
            # ordered by their `last_modified` timestamps
            # without pulling everything into memory and processing it all there.
            .values("id", "last_modified", "json", "foreign_keys", "object_type")
        )

    def modified_after(self, datetime=datetime.datetime(year=1, month=1, day=1)):
        """
        N.B. default value will cause failure if used on dates from BCE
        """
        return self.filter(last_modified__gt=datetime)


class ActivityStreamQuerySetWrapper:
    """
    This wraps a queryset that is a union of querysets from
    all models in the apps specified in `settings.ACTIVITY_STREAM_APPS`.
    Each queryset has the `for_activity_stream()` method applied;
    see `ActivityStreamQuerySetMixin` for this method.
    It provides special implementations of `order_by()` and `filter()`
    as those methods are used by Django REST Framework's CursorPagination,
    but `filter()` can't normally be used on a union queryset,
    and `order_by()` returns a queryset without this wrapper.
    Other methods and properties are delegated to the union queryset via `__getattr__`
    so should still work as expected, though with the other limitations of union querysets.
    Methods that return a queryset will return it inside this wrapper,
    with any existing ordering applied.
    Note that no exhaustive testing has been done of the result of applying such methods
    as the current requirement is only to support filtering and ordering,
    though `count()` is used by some unit tests and has been found to work correctly.
    """

    _ordering = None
    _queryset = None

    def __init__(self) -> None:
        super().__init__()
        self._models = self._get_models()
        self._queryset = self._union_of_all_querysets()

    def _get_models(self):
        apps_to_stream = settings.ACTIVITY_STREAM_APPS
        models = []
        for app_label in apps_to_stream:
            app = apps.get_app_config(app_label)
            app_models = app.get_models()
            models += app_models
        return models

    def _union_of_all_querysets(self):
        return self._union_of_querysets(self._all_querysets)

    def _union_of_querysets(self, querysets):
        base_queryset = querysets[0]
        union_queryset = base_queryset.union(*querysets[1:])
        if self._ordering:
            union_queryset = union_queryset.order_by(*self._ordering)
        return union_queryset

    @property
    def _all_querysets(self):
        return [
            model.objects.for_activity_stream()
            for model in self._models
            if hasattr(
                model.objects,
                "for_activity_stream",
            )
        ]

    def __getattr__(self, item):
        """
        If this is getting a method that the queryset has, we need to give it a wrapped version.
        This will break for many methods because of the union(), raising the usual Django exception.
        We implement order_by and filter specially, as those are the ones used by DRF pagination.
        But we might as well try to support others too.
        If this is used on a method supported by a union queryset, all will be well,
        and methods like count that don't return a queryset should work too.
        """
        if hasattr(self._queryset, item):
            attr = getattr(self._queryset, item)
            if hasattr(attr, "__call__"):

                @wraps(attr)
                def _wrapped_queryset_method(*args, **kwargs):
                    result = getattr(self._queryset, item)(*args, **kwargs)
                    if isinstance(result, QuerySet):
                        self._queryset = result
                        return self
                    return result

                return _wrapped_queryset_method
            return attr
        return self.__getattribute__(item)

    def __getitem__(self, item):
        """
        Implementing this method supports slicing of the queryset.
        """
        return self._queryset[item]

    def order_by(self, *field_names):
        """
        It's necessary to keep track of any ordering that has been applied
        as when `filter()` is applied, a new union queryset is constructed from the querysets
        originally used, which doesn't retain any ordering that was appplied to
        the original union queryset. So we record the ordering, apply it to the current queryset,
        and can then re-apply it as necessary.
        """
        self._ordering = field_names
        self._queryset = self._queryset.order_by(*field_names)
        return self

    def filter(self, *args, **kwargs):
        """
        Deceptively simple: this reconstructs the union queryset
        by applying the specified filter(s) to all the original querysets used to create the union,
        then constructing a new union queryset.
        This avoids the problem of causing the entire union queryset to be evaluated to extract a single page,
        which would place heavy demands on both the database and the app server's memory.
        Known limitation: any previous filtering will be lost. This could be dealt with
        by recording all filters applied and re-applying them, but that isn't necessary
        for current purposes, as only one filter is applied by DRF before the queryset is sliced
        and ceases to be filterable.
        """
        filtered_querysets = [
            queryset.filter(*args, **kwargs) for queryset in self._all_querysets
        ]
        self._queryset = self._union_of_querysets(filtered_querysets)
        return self
