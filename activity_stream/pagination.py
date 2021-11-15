from django.core.exceptions import ImproperlyConfigured
from rest_framework.pagination import CursorPagination
from rest_framework.response import Response


class ActivityStreamCursorPagination(CursorPagination):
    """
    Cursor pagination for activities.

    The activity stream service scrapes specified endpoints at regular intervals to get the
    activity feed from various services. It scrapes all the pages and more frequently: the
    last page only. If the last page has a "next" link, it scrapes that and updates the pointer
    to the last page.

    The default LIMIT-ORDER pagination gets slower as you progress through the pages so we
    decided to use cursor pagination here because we needed to render the last page quite
    frequently.

    According to the docs (See ref), cursor pagination required an ordering field that amongst
    other things:

        "Should be an unchanging value, such as a timestamp, slug, or other
        field that is only set once, on creation."

    Ref: https://www.django-rest-framework.org/api-guide/pagination/#cursorpagination
    """

    summary = "Update Supply Chain Information"
    ordering = (
        "last_modified",
        "id",
    )

    def paginate_queryset(self, queryset, request, view=None):
        """
        Our requirements differ from those supported by the standard DRF cursor pagination class:
            * We always want a last page bereft of items, other than when some item has been modified,
              and thus has a later last-modified date than ended the previous page;
            * We are always ordered ascending, so have no need of "reverse" pagination.
            * Although it would be nice to have, we don't need a "previous" link.

        """
        results = super().paginate_queryset(queryset, request, view)
        # if there are results but no next page, we're on the last page that will have content
        # so spoof a "next page" link
        # but if there are no results, we're already on the empty last page,
        # so we mustn't (and, indeed, can't) fabricate a "next" link
        if results and not self.has_next:
            self.next_position = self._get_position_from_instance(
                results[-1], self.ordering
            )
            self.has_next = True
            if self.template is not None:
                self.display_page_controls = True
        return results

    def _get_url(self):
        return self.encode_cursor(self.cursor) if self.cursor else self.base_url

    def get_paginated_response(self, data):
        """
        Overriding this function to re-format the response according to
        activity stream spec.
        """
        response = {
            "@context": "https://www.w3.org/ns/activitystreams",
            "name": "dit:UpdateSupplyChainInformation",
            "summary": self.summary,
            "type": "OrderedCollectionPage",
            "id": self._get_url(),
            "partOf": self.base_url,
            "orderedItems": data,
        }
        if self.has_next:
            response["next"] = self.get_next_link()
        return Response(response)
