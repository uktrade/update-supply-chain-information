import pytest

from activity_stream.models import ActivityStreamQuerySetWrapper
from activity_stream.viewsets import ActivityStreamViewSet

pytestmark = pytest.mark.django_db


class TestActivityStreamViewset:
    def test_activity_stream_viewset_uses_queryset_wrapper(
        self, wrapped_union_queryset
    ):
        viewset = ActivityStreamViewSet()
        queryset = viewset.get_queryset()
        assert isinstance(queryset, ActivityStreamQuerySetWrapper)
