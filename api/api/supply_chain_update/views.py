from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from django.db.models import Count

from api.supply_chain_update.models import (
    StrategicAction,
    StrategicActionUpdate,
    SupplyChain,
)
from api.supply_chain_update.serializers import (
    StrategicActionSerializer,
    StrategicActionUpdateSerializer,
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
        is_archived = self.request.query_params.get(
            "is_archived",
        )
        if supply_chain_id:
            queryset = queryset.filter(supply_chain__id=supply_chain_id)
        if is_archived:
            queryset = queryset.filter(is_archived=is_archived.capitalize())
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


class StrategicActionUpdateViewset(viewsets.ModelViewSet):
    """
    A viewset that returns Strategic Action update objects.
    """

    serializer_class = StrategicActionUpdateSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        queryset = StrategicActionUpdate.objects.all()
        is_draft = self.request.query_params.get("is_draft")
        if is_draft:
            queryset = queryset.filter(is_draft=True)
        return queryset
