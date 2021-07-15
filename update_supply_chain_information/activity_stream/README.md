# Activity Stream

## Purpose
This app provides a feed of data from the Update Supply Chain Information application in Activity Streams 2.0 format.

## Overview

The Data Infrastructure team's 
[Activity Stream tool](https://readme.trade.gov.uk/docs/playbooks/activity-stream/index.html)
>is a service presenting an Elasticsearch-compatible interface, filled with documents with a consistent structure, 
> pulled from DIT and 3rd party applications by making HTTP GET requests.

In order to pull data from an application, Activity Stream requires it to be structured as defined in
the W3C's [Activity Streams 2.0](https://www.w3.org/TR/activitystreams-core/) specification (W3C AS),
using the [Activity Vocabulary](https://www.w3.org/TR/activitystreams-vocabulary/).

Although Activity Stream can be configured to consume multiple feeds from the same application,
the preferred approach is to provide a single feed containing all the data the application wishes to make available.
Further requirements are also imposed on this representation:
* It should be ordered by some field;
* It should be paginated, with some suitable page size such as 100 items;
* Each page should include a "next" link to the next page;
* The final page should include no items (in the usual case);
* When an item in the collection represented by the feed has been modified, 
  it should appear on the previously-empty final page;
* The pagination is best implemented using a `last_modified + offset` cursor rather than by `limit + offset`.

The last point concerning the technique for implementing pagination is not a strict requirement;
Activity Stream is agnostic about the method of pagination used.
However, `limit + offset` pagination is documented to have performance problems as the data grow larger
and later pages in the sequence are accessed, which can be averted by using cursor pagination as recommended.


In practice, this means that we need a way to present all the data contained within our application,
in JSON format, with additional structure to conform to the specification, ordered by modification date.

## Requirements and restrictions of implementation

### Django

As we wish to provide data from instances of models of many different classes in a single feed,
we need a way to combine querysets. In addition, the unified collection of model instances must be
ordered by the `last_modified` field of the individual instances without regard to their underlying class.

A naive approach would involve gathering all the required querysets, converting them to sequence types,
combining those sequences into one, and applying the required sorting. However, this has certain disadvantages:
* It is necessary for the entirety of the data contained within the application to be brought into memory;
* It is not possible to use the database's native capability for ordering data in any useful way.

To illustrate these points, consider the case where querysets of model `A` and model `B` need to be combined.
Although each of those querysets may be ordered by `last_modified`, it is still necessary to order
them again, as any instance of model `A` could have been modified after any instance of model `B`.
The only way to handle this when they exist as individual querysets is by evaluating both querysets,
then sorting them in application code.

#### Using `QuerySet.union()`

Django querysets do have a method allowing them to be combined into a single queryset without
causing them to be immediately evaluated (which would bring their entire contents into memory):
[`union()`](https://docs.djangoproject.com/en/3.2/ref/models/querysets/#union).
However, this method places restrictions on the structure of the querysets to be combined:

>Passing different models works as long as the SELECT list is the same in all QuerySets 
> (at least the types, the names don’t matter as long as the types are in the same order).

In addition, it places many restrictions on the further processing that can then be carried out on the
resulting queryset (the union queryset):
> …only LIMIT, OFFSET, COUNT(*), ORDER BY, and specifying columns 
> (i.e. slicing, count(), exists(), order_by(), and values()/values_list()) 
> are allowed on the resulting QuerySet. 
> Further, databases place restrictions on what operations are allowed in the combined queries. 
> For example, most databases don’t allow LIMIT or OFFSET in the combined queries.

So if we are to use `union()` to obtain a unified queryset suitable for creating the individual pages
of the Activity Stream feed, we need to deal with those limitations.

### Django REST Framework

The primary advantage of using Django REST Framework (DRF) is that it includes support for almost all our requirements,
or can be made to support them with trivial overrides of various methods. In particular, it has full support
for cursor pagination.

However, the internal mechanics of its implementation of cursor pagination impose further requirements on
the queryset we provide:
* It must, in fact, be a queryset: various queryset methods will be called on it, so passing any other kind of sequence
type will not work;
* It must be possible to apply the `QuerySet.filter()` method to it.

The latter requirement arises because of the approach used to ensure that only the necessary portion
of the queryset is evaluated, thereby averting the problem of the entirety of the data having to be fetched
from the database into memory. Specifically:
* The queryset is filtered by the `last_modified` value at the end of the previous page,
which ensures that all model instances from earlier pages are not considerd;
* The queryset is then sliced, which causes it to finally be evaluated. Within Django's `QuerySet`
implementation, this will ultimately result in a SQL query that applies the specified filter as a `WHERE` clause, 
then applies a `LIMIT` to that result set, which is much more efficient at the database level than
applying a limit with offset.

So it is now necessary not only to deal with Django's requirements for creating a union queryset,
but also with DRF's requirement that the union queryset support filtering; and to do so in a way which
prevents the queryset being evaluated until DRF's pagination finally has to - otherwise,
we have fallen into the trap of bringing all our data into memory.

Note that `filter()` is not one of the operations that can be applied to a union queryset,
and attempting to do so will raise an exception.

## Implementation

### Configuration

#### settings.ACTIVITY_STREAM_APPS

This setting is a sequence type which specifies which of the apps in the project 
will have their models included in the Activity Stream feed.

### activity_stream.models.ActivityStreamQuerySetMixin

This mixin must be added to the superclass chain of all queryset classes used by models that are
to be included in the Activity Stream feed.

#### for_activity_stream()

Uses `annotate()` to augment the queryset with JSON versions of its contents and certain other useful values,
and uses `values()` to restrict its fields to a consistent subset, thereby allowing any model class's queryset on which
this method has been called to be combined with any other such queryset with `union()`.

The fields returned for each model instance when this queryset is evaluated are:
* `last_modified` - the `datetime` value on which the queryset will be ordered and filtered.
* `json` - a JSON serialisation of the model instance, created with the `JSONObject()` method.
* `foreign_keys` - Activity Stream imposes certain requirements for the ID fields of objects; specifically,
they are by convention structured in the form `dit:{application name}:{object type}:{id}`. By identifying foreign key fields within
models, the serializer is able to augment the IDs of related objects in the feed with a corresponding representation,
which will allow cross-referencing of related objects within ElasticSearch.
* `object_type` - the class name of the model, which is used:
  * by the serializer to construct the ID required by Activity Stream;
  * by Data Flow to construct ElasticSearch queries for specific types of object.

Of particular note here is the `json` field. As a W3C AS feed is JSON, we are able to delegate the JSON serialisation
of the model instances to the database, which means that our DRF Serializer class need not know what type
of object it is serialising: the model-specific work has already been done.

As the instance's `id` field will be modified to comply with Activity Stream's requirements
but the original UUID value is preferable when the data is extracted from Activity Stream
by Data Flow, that value is added to the JSON serialisation in its original form under the name `pk`.

#### modified_after(datetime=datetime.datetime(year=1, month=1, day=1))

Convenience method to filter on `last_modified__gt`. Only currently used by unit tests.

### activity_stream.models.ActivityStreamQuerySetWrapper

Creates a union queryset containing all models from the apps specified in `ACTIVITY_STREAM_APPS`,
and provides support for filtering the union queryset as required by DRF's `CursorPagination` implementation.

Note that this implementation only provides the minimal support necessary for this specific use case.
In particular, applying multiple filters to the union queryset by multiple calls to `filter()`
will only result in the last such call being applied (though multiple filters passed in a single call
would work as expected). A more general solution would cache the querysets that make up the union queryset 
to allow chaining of filters.

#### _ordering

Used to keep track of any ordering that has been applied to the union queryset, as it
will be necessary to re-apply that ordering at certain times. Default: `None`.

#### _models

Internal cache of all models in the specified apps, initialised by `_get_models()`.

#### _queryset

Union queryset, initialised by `_union_of_all_querysets()`

#### _all_querysets

Produces a list of all querysets for all models with `for_activity_stream()` applied to each one.

#### get_models()

Returns a list of all models in the apps specified in `ACTIVITY_STREAM_APPS`.

#### _union_of_all_querysets()

Returns a union queryset combining `_all_querysets`.

#### _union_of_querysets(querysets)

Returns a union queryset combining all `querysets` passed. If any ordering has previously been applied,
it is re-applied to the new union queryset.

#### \_\_getitem\_\_(item)

Standard Python magic method which supports slicing applied to this wrapper
by delegating to the internal union queryset.

#### \_\_getattr\_\_(item)

Standard Python magic method which is called when an attempt is made to access an attribute
of an object which does not exist on that object.

This method checks to see if the union queryset has the requested attribute by calling `getattr`:
* If the attribute is not found on the union queryset, `AttributeError` is raised.
* If the attribute is found, and it is not a callable, then the value of the attribute is returned.
* If the attribute is found and _is_ a callable, it is called:
  * If its return value is a queryset, it replaces this wrapper's queryset and this wrapper is returned.
  * If its return value is of any other type, that value is returned.

By this process, all attributes and methods of the union queryset are supported by this wrapper and the correct
value returned, or exception raised, when they are invoked. In particular:
* Invoking a method that does not return a queryset, such as `count()`, will return the correct value;
* Invoking an operation that Django does not support on union querysets will raise the expected exception.

By this process, the wrapper appears to exhibit the same properties and behaviours as the union queryset.

#### order_by(*field_names)

Records the ordering that the caller wishes to apply to the queryset, then delegates
to the union queryset. Returns this wrapper, so method chaining will work.

#### filter(*args, **kwargs)

Applies the supplied filter or filters to `_all_querysets`, creates a new union queryset,
and returns this wrapper.

Note that `_all_querysets` applies the `for_activity_stream()` method to each of the querysets,
so they will still be in the required form for being combined by `union()`. Furthermore,
any ordering that has been applied will be re-applied.

This method is really the entire point of this class, as it allows the DRF `CursorPagination`
to filter the union queryset by `last_modified`. Thus, the requirement that an ordered collection
of all of our models can be filtered so that only the required subset will be returned
without having to first evaluate every queryset, thereby potentially placing excessive load on the database
and on application server memory, is satisfied.

### activity_stream.serializers.ActivityStreamSerializer

Subclass of `rest_framework.serializers.ModelSerializer`.

#### department_prefix
#### app_name
#### app_key_prefix
#### name
#### _get_generator()

Used to augment the serialization of objects with additional values required by the W3C AS specification.

#### to_representation()

Called by DRF to obtain the JSON serialization of a model instance. It constructs the object metadata
structure required by W3C AS, with the payload in the `object` property then being updated with the JSON
representation created by the database. This is the step that allows instances of any model to be serialized
without the serializer being aware of its type.

#### update_foreign_keys()

Adds a version of any foreign keys in the model in Activity Stream ID format, to support
cross-referencing of object instances in ElasticSearch queries, as outlined under
`ActivityStreamQuerySetMixin.for_activity_stream()`. The original values are retained
within the serialisation for use in Data Flow and thereby in Data Workspace.

#### build_item_id(instance_id, object_type)

Returns an ID value in the form required by Activity Stream.

### activity_stream.pagination.ActivityStreamCursorPagination

Subclass of `rest_framework.pagination.CursorPagination`.

#### summary

Required by W3C AS.

#### ordering

Field(s) used by the superclass for ordering the queryset.

#### paginate_queryset(self, queryset, request, view=None)

Extends the superclass method to provide the empty final page required by Activity Stream.

The cursor created by the superclass methods encodes the values `last_modified`
and `offset`. The `last_modified` value is the timestamp from which the page should start, which
will generally be a value greater than the last value on the previous page. In the case where two or more
values spanning a page boundary have the same `last_modified` value, the `offset` is used to indicate
how many such values were on the previous page and should therefore be discarded.

When the last page is reached, the superclass method will return a non-empty value for `results`
and its `has_next` property will be false, as the default behaviour of DRF is that there are no pages
beyond the last page that contained any values.

By checking for these two conditions, we can determine that the page that has just been created
is the last page containing any results. By then calculating a value for the cursor and changing
`has_next` to be `True`, we allow the serialization to contain a `next` link to an empty page.
If the value of `results` is empty, then we are already on that empty last page and no `next` link will be shown.

Activity Stream will repeatedly fetch the empty last page, in order to see if any of the data in the stream
has been modified since it last fetched the stream from the beginning. When some item is modified,
the cursor pagination means it will appear on the empty last page, which will have a `next` link to what will be
the new empty last page - that is, a page which will only show items modified after the item that has just been
modified. This triggers Activity Stream to do two things:
* Update the current ElasticSearch index with the new item or items, so they are immediately available
to consumers of the index;
* Start reading the feed from its start page again, and add the results to a new ElasticSearch index.
When this process is complete (all pages have been read and the current page is empty), the current index
is replaced with the new index, thereby ensuring that the data presented in ElasticSearch is
eventually consistent with the current state of the application's data.

### activity_stream.viewsets.ActivityStreamViewSet

Subclass of `rest_framework.mixins.ListModelMixin` and `rest_framework.viewsets.GenericViewSet`.

#### pagination_class
#### serializer_class

Use our subclasses for pagination and serialization.

#### get_queryset()

Use our `ActivityStreamQuerySetWrapper` to allow the pagination to process our union queryset.