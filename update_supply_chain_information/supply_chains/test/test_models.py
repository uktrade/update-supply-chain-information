from datetime import date, timedelta
from dateutil.relativedelta import relativedelta

import pytest
from reversion.models import Version
from django.core.exceptions import ValidationError
from django.template.defaultfilters import slugify

from supply_chains.models import (
    StrategicAction,
    RAGRating,
)
from supply_chains.models import SupplyChain, StrategicActionUpdate
from supply_chains.test.factories import (
    SupplyChainFactory,
    StrategicActionFactory,
    StrategicActionUpdateFactory,
)
from accounts.models import GovDepartment

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


def test_no_archived_reason_save_supply_chain():
    """Validate that no supply chain can be archived w/o archive_reason"""
    msg = "An archived_reason must be given when archiving a supply chain."
    with pytest.raises(ValidationError) as excifno:
        SupplyChainFactory(is_archived=True)
        assert msg in excifno.value.messages


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
