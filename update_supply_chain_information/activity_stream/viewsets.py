from rest_framework import mixins
from rest_framework.viewsets import GenericViewSet

from activity_stream.models import ActivityStreamQuerySetWrapper
from activity_stream.pagination import (
    ActivityStreamCursorPagination,
)
from activity_stream.serializers import ActivityStreamSerializer


class ActivityStreamViewSet(mixins.ListModelMixin, GenericViewSet):
    pagination_class = ActivityStreamCursorPagination
    serializer_class = ActivityStreamSerializer

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def get_queryset(self):
        queryset = ActivityStreamQuerySetWrapper()
        return queryset
