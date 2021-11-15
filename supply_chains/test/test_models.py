from datetime import date
from typing import Dict, Final

import pytest
from django.core.exceptions import ValidationError
from django.template.defaultfilters import slugify
from accounts.test.factories import GovDepartmentFactory
from activity_stream.test.conftest import supply_chain

from supply_chains.models import (
    VulnerabilityAssessment,
    VulAssessmentSupplyStage,
    VulAssessmentReceiveStage,
    VulAssessmentMakeStage,
    VulAssessmentStoreStage,
    VulAssessmentDeliverStage,
)
from supply_chains.models import SupplyChain
from supply_chains.test.factories import (
    SupplyChainFactory,
    StrategicActionFactory,
    SupplyChainUmbrellaFactory,
    VulnerabilityAssessmentFactory,
    VulAssessmentSupplyStageFactory,
    VulAssessmentReceiveStageFactory,
    VulAssessmentMakeStageFactory,
    VulAssessmentStoreStageFactory,
    VulAssessmentDeliverStageFactory,
)

pytestmark = pytest.mark.django_db


def test_supply_chain_submitted_since_query():
    """
    Tests that that the custom 'submitted_since' query method
    on the SupplyChain model returns only supply chain objects
    with a last_submission_date after the given deadline.
    """
    SupplyChainFactory.create_batch(3, last_submission_date=date(2021, 4, 7))
    SupplyChainFactory.create_batch(3, last_submission_date=date(2021, 3, 7))
    SupplyChainFactory.create_batch(3, last_submission_date=None)
    supply_chains = SupplyChain.objects.all()
    assert supply_chains.submitted_since(date(2021, 4, 1)).count() == 3


def test_archived_date_set_when_save_supply_chain():
    """Test archived_date is set when archived supply chain saved."""
    reason = "No reason"
    sc = SupplyChainFactory(is_archived=True, archived_reason=reason)
    assert sc.archived_date == date.today()
    assert sc.archived_reason == reason


def test_no_archived_date_save_strategic_action():
    """
    Test validation error is raised if an archived strategic action
    is saved without an archived_reason.
    """
    with pytest.raises(ValidationError) as excifno:
        StrategicActionFactory(is_archived=True)
    assert (
        "An archived_reason must be given when archiving a strategic action."
        in excifno.value.messages
    )


def test_archived_date_set_save_strategic_action():
    """Test archived_date is set when archived strategic action saved."""
    sa = StrategicActionFactory(is_archived=True, archived_reason="A reason")
    assert sa.archived_date == date.today()


def test_long_slug():
    # Arrange
    long_slug_75_chars = slugify(
        "Strategic action 1: Incentives to pivot API sourcing abdcfe asdfadsf asdfs"
    )

    # Act
    sc = SupplyChainFactory(slug=long_slug_75_chars)

    # Assert
    assert sc.slug == long_slug_75_chars


def test_sc_risk_status():
    # Arrange
    sc_name = "optional"

    # Act
    sc = SupplyChainFactory.create(name=sc_name)

    # Assert
    assert SupplyChain.objects.count() == 1
    assert SupplyChain.objects.get(name=sc_name).risk_severity_status == ""


ArcReason: Final = "archived_reason"
SCUmbrella: Final = "supply_chain_umbrella"

ERROR_MSGS = {
    ArcReason: ["An archived_reason must be given when archiving a supply chain."],
    SCUmbrella: ["Department should match for supply chain and umbrella."],
}


class TestSCModel:
    def validate(self, chain, expected_errors: Dict, objects_saved: int = 0):
        try:
            chain.full_clean()
            chain.save()
        except ValidationError as err:
            details = dict(err)

            assert all(
                [
                    [key in details for key in expected_errors],
                    [expected_errors[key] == details[key] for key in expected_errors],
                ]
            )
        else:
            if expected_errors:
                pytest.fail(f"No expections were raised out of {expected_errors}")
        finally:
            assert SupplyChain.objects.count() == objects_saved

    def test_SC_no_umbrella(self, test_user):
        # Arrange
        # Act
        sc = SupplyChainFactory.build(
            gov_department=test_user.gov_department, supply_chain_umbrella=None
        )

        # Assert
        self.validate(sc, {}, objects_saved=1)

    def test_SC_with_umbrella(self, test_user):
        # Arrange
        umbrella = SupplyChainUmbrellaFactory.create(
            gov_department=test_user.gov_department
        )

        # Act
        sc = SupplyChainFactory.build(
            gov_department=test_user.gov_department, supply_chain_umbrella=umbrella
        )

        # Assert
        self.validate(sc, {}, objects_saved=1)

    def test_SC_with_inv_umbrella(self, test_user):
        # Arrange
        dept = GovDepartmentFactory.create()
        umbrella = SupplyChainUmbrellaFactory.create(gov_department=dept)

        # Act
        sc = SupplyChainFactory.build(
            gov_department=test_user.gov_department, supply_chain_umbrella=umbrella
        )

        # Assert
        self.validate(sc, {SCUmbrella: ERROR_MSGS[SCUmbrella]}, objects_saved=0)

    def test_SC_unlink_umbrella(self, test_user):
        # Arrange
        umbrella = SupplyChainUmbrellaFactory.create(
            gov_department=test_user.gov_department,
        )
        sc = SupplyChainFactory.create(
            gov_department=test_user.gov_department, supply_chain_umbrella=umbrella
        )

        # Act
        sc.supply_chain_umbrella = None

        # Assert
        self.validate(sc, {}, objects_saved=1)

    def test_archived_SC(self, test_user):
        # Arrange
        # Act
        sc = SupplyChainFactory.build(
            gov_department=test_user.gov_department,
            is_archived=True,
            archived_reason="Hello World",
        )

        # Assert
        self.validate(sc, {}, objects_saved=1)

    def test_archived_no_reason(self, test_user):
        # Arrange
        # Act
        sc = SupplyChainFactory.build(
            gov_department=test_user.gov_department,
            is_archived=True,
        )

        # Assert
        self.validate(sc, {ArcReason: ERROR_MSGS[ArcReason]}, objects_saved=0)


class TestVulAssessmentModel:
    def test_vul_object_save(self):
        # Arrage
        # Act
        sc = SupplyChainFactory.create()
        vul_obj = VulnerabilityAssessmentFactory.create(supply_chain=sc)
        VulAssessmentSupplyStageFactory.create(vulnerability=vul_obj)
        VulAssessmentReceiveStageFactory.create(vulnerability=vul_obj)
        VulAssessmentMakeStageFactory.create(vulnerability=vul_obj)
        VulAssessmentDeliverStageFactory.create(vulnerability=vul_obj)
        VulAssessmentStoreStageFactory.create(vulnerability=vul_obj)

        # Assert
        assert SupplyChain.objects.count() == 1
        assert VulnerabilityAssessment.objects.count() == 1
        assert VulAssessmentSupplyStage.objects.count() == 1
        assert VulAssessmentReceiveStage.objects.count() == 1
        assert VulAssessmentMakeStage.objects.count() == 1
        assert VulAssessmentStoreStage.objects.count() == 1
        assert VulAssessmentDeliverStage.objects.count() == 1

    def test_vul_object_sc_required(self):
        # Arrage
        vul_obj = VulnerabilityAssessmentFactory.build()

        # Act
        # Assert
        vul_obj.supply_chain = None

        with pytest.raises(ValidationError) as exc_info:
            vul_obj.full_clean()
            vul_obj.save()

    def test_supply_stage_missing_RAG(self):
        # Arrage
        sc = SupplyChainFactory.create()
        vul_obj = VulnerabilityAssessmentFactory.build(supply_chain=sc)

        # Act
        supply = VulAssessmentSupplyStageFactory.build(
            supply_stage_rag_rating=None, vulnerability=vul_obj
        )

        # Assert
        with pytest.raises(ValidationError) as exc_info:
            supply.full_clean()
            supply.save()

        assert VulAssessmentSupplyStage.objects.count() == 0

    def test_receive_stage_missing_summary(self):
        # Arrage
        sc = SupplyChainFactory.create()
        vul_obj = VulnerabilityAssessmentFactory.build(supply_chain=sc)

        # Act
        receive = VulAssessmentReceiveStageFactory.build(
            receive_stage_summary_4=None, vulnerability=vul_obj
        )

        # Assert
        with pytest.raises(ValidationError) as exc_info:
            receive.full_clean()
            receive.save()

        assert VulAssessmentReceiveStage.objects.count() == 0
