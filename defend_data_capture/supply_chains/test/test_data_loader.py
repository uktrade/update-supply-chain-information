from datetime import date, timedelta
from io import StringIO
import re
import os

import pytest
from django.test import Client
from django.urls import reverse
from django.template.defaultfilters import slugify
from django.core.management import call_command
from django.core.management.base import CommandError

from supply_chains.management.commands import data_loader as sut
from accounts.models import GovDepartment
from supply_chains.models import SupplyChain

# from supply_chains.test.factories import SupplyChainFactory, GovDepartmentFactory


pytestmark = pytest.mark.django_db
DATA_FILES_LOC = "defend_data_capture/supply_chains/test/data"


class TestDataLoader:
    LOAD_CMD = "data_loader"
    ACCOUNTS_FILE = os.path.join(DATA_FILES_LOC, "accounts_sample.csv")
    SC_FILE = os.path.join(DATA_FILES_LOC, "supply_chain_sample.csv")
    INV_ACCOUNTS_FILE = os.path.join(DATA_FILES_LOC, "accounts_sample_no_ids.csv")

    def invoke_load(self, *args):
        with StringIO() as status:
            call_command(self.LOAD_CMD, *args, stdout=status, stderr=status)
            return status.getvalue()

    def test_load_accounts_data(self):
        # Arrange
        # Act
        res = self.invoke_load(sut.MODEL_GOV_DEPT, self.ACCOUNTS_FILE)

        # Assert
        assert re.match(f".*(Successfully) .* {sut.MODEL_GOV_DEPT}.*", res)
        assert GovDepartment.objects.count() is 7

    def test_load_accounts_no_data(self):
        # Arrange
        # Act
        # Assert
        with pytest.raises(CommandError):
            self.invoke_load(sut.MODEL_GOV_DEPT)

    def test_load_accounts_inv_data_no_ids(self):
        # Arrange
        # Act
        # Assert
        with pytest.raises(KeyError, match=r"'id'"):
            self.invoke_load(sut.MODEL_GOV_DEPT, self.INV_ACCOUNTS_FILE)

    def test_load_sc_data(self):
        # Arrange
        self.invoke_load(sut.MODEL_GOV_DEPT, self.ACCOUNTS_FILE)

        # Act
        res = self.invoke_load(sut.MODEL_SUPPLY_CHAIN, self.SC_FILE)

        # Assert
        assert re.match(f".*(Successfully) .* {sut.MODEL_SUPPLY_CHAIN}.*", res)
        assert SupplyChain.objects.count() is 9
        assert SupplyChain.objects.filter(name__startswith="medic").count() is 2

    def test_load_sc_inv_model(self):
        # Arrange
        inv_model = "hello world"

        # Act
        # Assert
        with pytest.raises(CommandError, match=f"Unknown model {inv_model}"):
            self.invoke_load(inv_model, self.SC_FILE)
