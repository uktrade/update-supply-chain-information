import pytest

pytestmark = pytest.mark.django_db

from reversion.models import Version

from supply_chains.models import ScenarioAssessment, NullableRAGRating
from supply_chains.test.factories import ScenarioAssessmentFactory


class TestScenarioAssessmentVersioning:
    def test_creation_registered_with_reversion(self):
        scenario_assessment: ScenarioAssessment = ScenarioAssessmentFactory()
        version = None
        try:
            version = Version.objects.get(object_id=scenario_assessment.pk)
        except Version.DoesNotExist:
            pass
        assert version is not None
        comment = version.revision.comment
        assert comment.startswith("Created:")
        assert comment.endswith(scenario_assessment.supply_chain.name)

    def test_modification_registered_with_reversion(self):
        scenario_assessment: ScenarioAssessment = ScenarioAssessmentFactory(
            borders_closed_rag_rating=NullableRAGRating.NONE
        )
        versions = None
        scenario_assessment.borders_closed_rag_rating = NullableRAGRating.AMBER
        scenario_assessment.save()
        try:
            versions = Version.objects.filter(object_id=scenario_assessment.pk)
        except Version.DoesNotExist:
            pass
        assert versions.exists()
        assert versions.count() == 2
        latest_version = versions.order_by("revision__date_created").last()
        comment = latest_version.revision.comment
        assert comment.startswith("Edited:")
        assert comment.endswith(scenario_assessment.supply_chain.name)
