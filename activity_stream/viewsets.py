from rest_framework import mixins
from rest_framework.viewsets import GenericViewSet

from activity_stream.models import ActivityStreamQuerySetWrapper
from activity_stream.pagination import (
    ActivityStreamCursorPagination,
)
from activity_stream.serializers import ActivityStreamSerializer


class ActivityStreamViewSet(mixins.ListModelMixin, GenericViewSet):
    permission_classes = ()  # as long authed, can view
    pagination_class = ActivityStreamCursorPagination
    serializer_class = ActivityStreamSerializer

    def get_queryset(self):
        queryset = ActivityStreamQuerySetWrapper()
        return queryset
