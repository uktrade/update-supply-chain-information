from uuid import UUID

import pytest

from activity_stream.serializers import ActivityStreamSerializer
from supply_chains.models import *

pytestmark = pytest.mark.django_db


class TestActivityStreamSerializer:
    def test_serializer_updates_foreign_key(self, strategic_action_queryset):
        serializer = ActivityStreamSerializer()
        strategic_action = StrategicAction.objects.order_by("last_modified").first()
        supply_chain_id = strategic_action.supply_chain_id
        expected_supply_chain_key = (
            f"{serializer.app_key_prefix}:{SupplyChain.__name__}:{supply_chain_id}"
        )

        strategic_action_for_serialisation = (
            StrategicAction.objects.order_by("last_modified")
            .for_activity_stream()
            .first()
        )
        representation = serializer.to_representation(
            strategic_action_for_serialisation
        )

        assert representation["object"]["es_supply_chain"] == expected_supply_chain_key
        assert UUID(representation["object"]["supply_chain"]) == supply_chain_id

    def test_announcement_id_in_serialisation(self, supply_chain):
        serializer = ActivityStreamSerializer()
        queryset = SupplyChain.objects.for_activity_stream()
        instance = queryset.first()

        representation = serializer.to_representation(instance)

        assert (
            representation["id"]
            == f"{serializer.app_key_prefix}:SupplyChain:{supply_chain.pk}:Announce"
        )
