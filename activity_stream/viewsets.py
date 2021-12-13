from rest_framework import mixins
from rest_framework.viewsets import GenericViewSet
from activity_stream.serializers.supply_chain import GSCUpdateSerializer

from supply_chains.models import SupplyChain


class SupplyChainActivityStreamViewSet(
    mixins.ListModelMixin,
    GenericViewSet
):
    permission_classes = ()  # as long authed, can view
    authentication_classes = ()
    #pagination_class = ActivityStreamCursorPagination
    serializer_class = GSCUpdateSerializer

    def get_queryset(self):
        return SupplyChain.objects.all()
