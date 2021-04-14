from datetime import date, timedelta

import pytest

from supply_chains.models import SupplyChain, StrategicActionUpdate
from supply_chains.test.factories import (
    SupplyChainFactory,
    StrategicActionFactory,
    StrategicActionUpdateFactory,
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


class TestSAUModel:
    def test_since_with_filter(self):
        # Arrange
        sc = SupplyChainFactory.create(name="Supply Chain 1")
        sa = StrategicActionFactory.create(name="SA 01", supply_chain=sc)
        sau = StrategicActionUpdateFactory.create(
            status=StrategicActionUpdate.Status.IN_PROGRESS,
            supply_chain=sc,
            strategic_action=sa,
        )

        # Act
        sau_prog = StrategicActionUpdate.modified_objects.since(
            deadline=date.today() - timedelta(days=1),
            supply_chain=sc,
            status=StrategicActionUpdate.Status.IN_PROGRESS,
        )

        sau_comp = StrategicActionUpdate.modified_objects.since(
            deadline=date.today() - timedelta(days=1),
            supply_chain=sc,
            status=StrategicActionUpdate.Status.COMPLETED,
        )

        # Assert
        assert sau_prog[0] == sau
        assert sau_comp.count() == 0

    def test_slug_init(self):
        # Arrange
        sau = StrategicActionUpdateFactory.create(
            status=StrategicActionUpdate.Status.IN_PROGRESS,
        )

        # Act
        # Assert
        assert date.today().strftime("%m-%Y") == sau.slug
