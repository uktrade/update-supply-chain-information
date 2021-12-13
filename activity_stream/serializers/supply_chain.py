from supply_chains.models import SupplyChain

from accounts.models import GovDepartment

from activity_stream.serializers.base_serialzier import (
    ActivityStreamSerializer,
)


class GovDepartmentSerializer(ActivityStreamSerializer):
    class Meta:
        model = GovDepartment
        fields = ['name', 'visualisation_url', ]


class GSCUpdateSerializer(ActivityStreamSerializer):
    gov_department = GovDepartmentSerializer(read_only=True)

    class Meta:
        model = SupplyChain
        fields = [
            'name',
            'description',
            'last_submission_date',
            'contact_name',
            'gov_department',
        ]
