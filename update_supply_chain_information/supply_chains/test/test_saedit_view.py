import pytest

from django.test import Client
from django.urls import reverse
from django.template.defaultfilters import slugify

from supply_chains.forms import StrategicActionEditForm
from supply_chains.test.factories import (
    SupplyChainFactory,
    StrategicActionFactory,
    GovDepartmentFactory,
)
from supply_chains.views import SAEditView

pytestmark = pytest.mark.django_db


@pytest.fixture
def saedit_stub(test_user):
    sc_name = "Supply Chain 1"
    sa_description = "1234567890qweertyuiodfsfgfgggsf"
    sa_name = "SA 00"
    sc = SupplyChainFactory(name=sc_name, gov_department=test_user.gov_department)
    sa = StrategicActionFactory(
        name=sa_name, description=sa_description, supply_chain=sc
    )

    yield {
        "sc_name": sc_name,
        "sa_description": sa_description,
        "sa_name": sa_name,
        "url": reverse(
            "edit-strategic-action",
            kwargs={
                "supply_chain_slug": slugify(sc_name),
                "action_slug": slugify(sa_name),
            },
        ),
        "sc": sc,
        "sa": sa,
    }


class TestSAEditView:
    def test_auth(self, saedit_stub):
        # Arrange
        # Act
        resp = Client().get(saedit_stub["url"])

        # Assert
        assert resp.status_code == 302

    def test_auth_no_perm(self, logged_in_client):
        # Arrange
        sc_name = "ceramics"
        sa_name = "action"
        dep = GovDepartmentFactory()
        sc = SupplyChainFactory(gov_department=dep, name=sc_name)
        StrategicActionFactory(supply_chain=sc)

        # Act
        resp = logged_in_client.get(
            reverse(
                "edit-strategic-action",
                kwargs={
                    "supply_chain_slug": slugify(sc_name),
                    "action_slug": slugify(sa_name),
                },
            )
        )

        # Assert
        assert resp.status_code == 403

    def test_auth_logged_in(self, saedit_stub, logged_in_client):
        # Arrange
        # Act
        resp = logged_in_client.get(saedit_stub["url"])

        # Assert
        assert resp.status_code == 200

    def test_edit_objects(self, logged_in_client, saedit_stub):
        # Arrange
        # Act
        resp = logged_in_client.get(saedit_stub["url"])

        # Assert
        assert isinstance(resp.context_data["form"], StrategicActionEditForm)
        assert resp.context_data["object"] == saedit_stub["sa"]
        assert resp.context_data["supply_chain"] == saedit_stub["sc"]
        assert isinstance(resp.context_data["view"], SAEditView)

    def test_form_objects(self, logged_in_client, saedit_stub):
        # Arrange
        # Act
        resp = logged_in_client.get(saedit_stub["url"])
        fields = resp.context_data["form"].fields
        form_objects = fields.keys()

        # Assert
        assert all(
            [
                x in form_objects
                for x in [
                    "category",
                    "description",
                    "geographic_scope",
                    "impact",
                    "is_ongoing",
                    "other_dependencies",
                    "related_to_whole_sc",
                    "supporting_organisations",
                ]
            ]
        )
