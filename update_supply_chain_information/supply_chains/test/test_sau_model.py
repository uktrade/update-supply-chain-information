from datetime import date
from dateutil.relativedelta import relativedelta
from typing import Dict, Final

import pytest
from django.core.exceptions import ValidationError

from supply_chains.test.factories import (
    SupplyChainFactory,
    GovDepartmentFactory,
    UserFactory,
    StrategicActionFactory,
    StrategicActionUpdateFactory,
)
from supply_chains.models import StrategicActionUpdate, RAGRating


pytestmark = pytest.mark.django_db
Staus = StrategicActionUpdate.Status


SubDate: Final = "submission_date"
Content: Final = "content"
RagRating: Final = "implementation_rag_rating"
RagReason: Final = "reason_for_delays"
CompletionDateChangeReason: Final = "reason_for_completion_date_change"
ObjectLevelError: Final = "__all__"

ERROR_MSGS = {
    SubDate: ["Missing submission_date."],
    Content: ["Missing content."],
    RagRating: ["Missing implementation_rag_rating."],
    RagReason: ["Missing reason_for_delays."],
    CompletionDateChangeReason: ["Missing reason_for_completion_date_change."],
    ObjectLevelError: [""],
}


@pytest.fixture
def sau_stub(test_user):
    sc_name = "carbon"
    sa_name = "Source raw packaging"
    sc = SupplyChainFactory(name=sc_name, gov_department=test_user.gov_department)
    sa = StrategicActionFactory(name=sa_name, supply_chain=sc)

    yield {
        "user": test_user,
        "sc_name": sc_name,
        "sa_name": sa_name,
        "sc": sc,
        "sa": sa,
    }


class TestSAUModel:
    """Test class to focus mainly on creation of SAU objects from admin panel

    See RT-449 for more info.
    """

    def validate(self, update, expected_errors: Dict, objects_saved: int = 0):
        try:
            update.full_clean()
            update.save()
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
            assert StrategicActionUpdate.objects.all().count() == objects_saved

    def test_SAU_save(self, sau_stub):
        # Arrange
        # Act
        sau = StrategicActionUpdateFactory.build(
            user=sau_stub["user"],
            strategic_action=sau_stub["sa"],
            supply_chain=sau_stub["sc"],
            status=Staus.SUBMITTED,
            implementation_rag_rating=RAGRating.GREEN,
        )

        # Assert
        self.validate(sau, {}, objects_saved=1)

    def test_SAU_missing_sub_date(self, sau_stub):
        # Arrange
        # Act
        sau = StrategicActionUpdateFactory.build(
            user=sau_stub["user"],
            strategic_action=sau_stub["sa"],
            supply_chain=sau_stub["sc"],
            status=Staus.SUBMITTED,
            submission_date=None,
        )

        # Assert
        self.validate(sau, {SubDate: ERROR_MSGS[SubDate]})

    def test_SAU_missing_content(self, sau_stub):
        # Arrange
        # Act
        sau = StrategicActionUpdateFactory.build(
            user=sau_stub["user"],
            strategic_action=sau_stub["sa"],
            supply_chain=sau_stub["sc"],
            status=Staus.SUBMITTED,
            content=None,
        )

        # Assert
        self.validate(sau, {Content: ERROR_MSGS[Content]})

    def test_SAU_missing_RAG(self, sau_stub):
        # Arrange
        # Act
        sau = StrategicActionUpdateFactory.build(
            user=sau_stub["user"],
            strategic_action=sau_stub["sa"],
            supply_chain=sau_stub["sc"],
            status=Staus.SUBMITTED,
            implementation_rag_rating=None,
        )

        # Assert
        self.validate(sau, {RagRating: ERROR_MSGS[RagRating]})

    def test_SAU_RAG_reason(self, sau_stub):
        # Arrange
        # Act
        sau = StrategicActionUpdateFactory.build(
            user=sau_stub["user"],
            strategic_action=sau_stub["sa"],
            supply_chain=sau_stub["sc"],
            status=Staus.SUBMITTED,
            implementation_rag_rating=RAGRating.GREEN,
        )

        # Assert
        self.validate(sau, {}, objects_saved=1)

    def test_SAU_missing_RAG_reason(self, sau_stub):
        # Arrange
        # Act
        sau = StrategicActionUpdateFactory.build(
            user=sau_stub["user"],
            strategic_action=sau_stub["sa"],
            supply_chain=sau_stub["sc"],
            status=Staus.SUBMITTED,
            implementation_rag_rating=RAGRating.AMBER,
            reason_for_delays=None,
        )

        # Assert
        self.validate(sau, {RagReason: ERROR_MSGS[RagReason]})

    def test_SAU_missing_RAG_reason_red(self, sau_stub):
        # Arrange
        # Act
        sau = StrategicActionUpdateFactory.build(
            user=sau_stub["user"],
            strategic_action=sau_stub["sa"],
            supply_chain=sau_stub["sc"],
            status=Staus.SUBMITTED,
            implementation_rag_rating=RAGRating.RED,
            reason_for_delays=None,
        )

        # Assert
        self.validate(sau, {RagReason: ERROR_MSGS[RagReason]})

    def test_SAU_missing_completion_change_reason(self, sau_stub):
        # Arrange
        # Act
        sau = StrategicActionUpdateFactory.build(
            user=sau_stub["user"],
            strategic_action=sau_stub["sa"],
            supply_chain=sau_stub["sc"],
            status=Staus.SUBMITTED,
            implementation_rag_rating=RAGRating.RED,
            reason_for_delays="some text",
            changed_value_for_target_completion_date=date.today().replace(day=20)
            + relativedelta(years=1, months=1),
            reason_for_completion_date_change=None,
        )

        # Assert
        self.validate(
            sau, {CompletionDateChangeReason: ERROR_MSGS[CompletionDateChangeReason]}
        )

    def test_back_dating_update(self, sau_stub):
        # Arrange
        # Act
        sau = StrategicActionUpdateFactory.build(
            user=sau_stub["user"],
            strategic_action=sau_stub["sa"],
            supply_chain=sau_stub["sc"],
            status=Staus.SUBMITTED,
            implementation_rag_rating=RAGRating.GREEN,
            reason_for_delays="some text",
            date_created=date.today().replace(day=20) - relativedelta(months=3),
            submission_date=date.today().replace(day=20) - relativedelta(months=3),
        )

        # Assert
        self.validate(sau, {}, objects_saved=1)
        assert (
            StrategicActionUpdate.objects.given_month(
                date.today().replace(day=20) - relativedelta(months=3)
            ).count()
            == 1
        )

    def test_back_dating_update_in_gap(self, sau_stub):
        # Arrange
        StrategicActionUpdateFactory.create(
            user=sau_stub["user"],
            strategic_action=sau_stub["sa"],
            supply_chain=sau_stub["sc"],
            status=Staus.SUBMITTED,
            implementation_rag_rating=RAGRating.GREEN,
            reason_for_delays="some text",
            date_created=date.today().replace(day=20) - relativedelta(months=4),
            submission_date=date.today().replace(day=20) - relativedelta(months=4),
        )

        StrategicActionUpdateFactory.create(
            user=sau_stub["user"],
            strategic_action=sau_stub["sa"],
            supply_chain=sau_stub["sc"],
            status=Staus.SUBMITTED,
            implementation_rag_rating=RAGRating.GREEN,
            reason_for_delays="some text",
            date_created=date.today().replace(day=20) - relativedelta(months=2),
            submission_date=date.today().replace(day=20) - relativedelta(months=2),
        )

        # Act
        sau = StrategicActionUpdateFactory.build(
            user=sau_stub["user"],
            strategic_action=sau_stub["sa"],
            supply_chain=sau_stub["sc"],
            status=Staus.SUBMITTED,
            implementation_rag_rating=RAGRating.GREEN,
            reason_for_delays="some text",
            date_created=date.today().replace(day=20) - relativedelta(months=3),
            submission_date=date.today().replace(day=20) - relativedelta(months=3),
        )

        # Assert
        self.validate(sau, {}, objects_saved=3)
        assert (
            StrategicActionUpdate.objects.given_month(
                date.today().replace(day=20) - relativedelta(months=3)
            ).count()
            == 1
        )

    def test_back_dating_fail(self, sau_stub):
        # Arrange
        sau1 = StrategicActionUpdateFactory.create(
            user=sau_stub["user"],
            strategic_action=sau_stub["sa"],
            supply_chain=sau_stub["sc"],
            status=Staus.SUBMITTED,
            implementation_rag_rating=RAGRating.GREEN,
            reason_for_delays="some text",
            date_created=date.today().replace(day=20) - relativedelta(months=3),
            submission_date=date.today().replace(day=20) - relativedelta(months=3),
        )

        # Act
        new = StrategicActionUpdateFactory.build(
            user=sau_stub["user"],
            strategic_action=sau_stub["sa"],
            supply_chain=sau_stub["sc"],
            status=Staus.IN_PROGRESS,
            date_created=date.today().replace(day=20) - relativedelta(months=3),
        )

        # Assert
        self.validate(new, {ObjectLevelError: ""}, objects_saved=1)
        assert (
            StrategicActionUpdate.objects.given_month(
                date.today().replace(day=20) - relativedelta(months=3)
            ).count()
            == 1
        )

    def test_back_dating_change_state(self, sau_stub):
        # Arrange
        StrategicActionUpdateFactory.create(
            user=sau_stub["user"],
            strategic_action=sau_stub["sa"],
            supply_chain=sau_stub["sc"],
            status=Staus.IN_PROGRESS,
            implementation_rag_rating=RAGRating.GREEN,
            date_created=date.today().replace(day=20) - relativedelta(months=3),
        )
        StrategicActionUpdateFactory.create_batch(10)

        # Act
        sau = StrategicActionUpdate.objects.get(strategic_action=sau_stub["sa"])
        sau.status = Staus.SUBMITTED
        sau.submission_date = date.today().replace(day=20) - relativedelta(months=3)
        sau.save()

        # Assert
        assert (
            StrategicActionUpdate.objects.given_month(
                date.today().replace(day=20) - relativedelta(months=3)
            ).count()
            == 1
        )

    def test_back_dating_update_with_earlier_days(self, sau_stub):
        """For RT-489, specifically"""
        # Arrange
        StrategicActionUpdateFactory.create(
            user=sau_stub["user"],
            strategic_action=sau_stub["sa"],
            supply_chain=sau_stub["sc"],
            status=Staus.SUBMITTED,
            implementation_rag_rating=RAGRating.GREEN,
            reason_for_delays="some text",
            date_created=date.today().replace(day=10) - relativedelta(months=3),
            submission_date=date.today().replace(day=10) - relativedelta(months=3),
        )
        # Act
        sau = StrategicActionUpdateFactory.build(
            user=sau_stub["user"],
            strategic_action=sau_stub["sa"],
            supply_chain=sau_stub["sc"],
            status=Staus.SUBMITTED,
            implementation_rag_rating=RAGRating.GREEN,
            reason_for_delays="some text",
            date_created=date.today().replace(day=20) - relativedelta(months=3),
            submission_date=date.today().replace(day=20) - relativedelta(months=3),
        )

        # Assert
        self.validate(sau, {ObjectLevelError: ""}, objects_saved=1)

        assert (
            StrategicActionUpdate.objects.given_month(
                date.today().replace(day=20) - relativedelta(months=3)
            ).count()
            == 1
        )
