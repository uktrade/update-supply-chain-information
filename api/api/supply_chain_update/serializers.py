from rest_framework import serializers

from api.supply_chain_update.models import StrategicAction


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
