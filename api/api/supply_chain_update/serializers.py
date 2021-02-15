from rest_framework import serializers

from api.supply_chain_update.models import StrategicAction, SupplyChain


class StrategicActionSerializer(serializers.ModelSerializer):
    class Meta:
        model = StrategicAction
        fields = [
            "id",
            "name",
            "start_date",
            "description",
            "is_archived",
            "supply_chain",
        ]
        depth = 1


class SupplyChainSerializer(serializers.ModelSerializer):
    strategic_action_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = SupplyChain
        fields = [
            "id",
            "name",
            "last_submission_date",
            "gov_department",
            "strategic_action_count",
        ]
        depth = 1
