from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from django.db.models import Count

from api.supply_chain_update.models import StrategicAction, SupplyChain
from api.supply_chain_update.serializers import (
    StrategicActionSerializer,
    SupplyChainSerializer,
)


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


class SupplyChainViewset(viewsets.ModelViewSet):
    """
    A viewset that returns Supply Chain objects
    """

    serializer_class = SupplyChainSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        queryset = SupplyChain.objects.all()
        gov_department_id = self.request.query_params.get("gov_department_id")

        if gov_department_id:
            queryset = queryset.filter(gov_department__id=gov_department_id)
            queryset = queryset.annotate(
                strategic_action_count=Count("strategic_actions")
            )
        return queryset
