from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated

from api.supply_chain_update.models import StrategicAction
from api.supply_chain_update.serializers import StrategicActionSerializer


class StrategicActionViewset(viewsets.ModelViewSet):
    """
    A viewset that returns Strategic Action objects.
    """

    serializer_class = StrategicActionSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        queryset = StrategicAction.objects.all()
        supply_chain_id = self.request.query_params.get(
            "supply_chain_id",
        )
        if supply_chain_id:
            queryset = queryset.filter(supply_chain__id=supply_chain_id)
        return queryset
