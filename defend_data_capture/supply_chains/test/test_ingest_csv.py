from io import StringIO
import re
import os

import pytest
from django.core.management import call_command
from django.core.management.base import CommandError

from supply_chains.management.commands import ingest_csv as sut
from accounts.models import GovDepartment
from supply_chains.models import StrategicAction, StrategicActionUpdate, SupplyChain


pytestmark = pytest.mark.django_db
DATA_FILES_LOC = "defend_data_capture/supply_chains/test/data"


class TestDataLoader:
    LOAD_CMD = "ingest_csv"
    ACCOUNTS_FILE = os.path.join(DATA_FILES_LOC, "accounts_sample.csv")
    SC_FILE = os.path.join(DATA_FILES_LOC, "supply_chain_sample.csv")
    SA_FILE = os.path.join(DATA_FILES_LOC, "strat_action_sample.csv")
    SAU_FILE = os.path.join(DATA_FILES_LOC, "action_update_sample.csv")
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
        assert GovDepartment.objects.count() == 8

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
        assert SupplyChain.objects.count() == 3
        assert SupplyChain.objects.filter(name__startswith="medic").count() == 2

    def test_load_sc_data_twice(self):
        # Arrange
        self.invoke_load(sut.MODEL_GOV_DEPT, self.ACCOUNTS_FILE)
        self.invoke_load(sut.MODEL_SUPPLY_CHAIN, self.SC_FILE)

        # Act
        res = self.invoke_load(sut.MODEL_SUPPLY_CHAIN, self.SC_FILE)

        # Assert
        assert re.match(f".*(Successfully) .* {sut.MODEL_SUPPLY_CHAIN}.*", res)
        assert SupplyChain.objects.count() == 3
        assert SupplyChain.objects.filter(name__startswith="medic").count() == 2

    def test_load_sc_inv_model(self):
        # Arrange
        inv_model = "hello world"

        # Act
        # Assert
        with pytest.raises(CommandError, match=f"Unknown model {inv_model}"):
            self.invoke_load(inv_model, self.SC_FILE)

    def test_load_sa_data(self):
        # Arrange
        self.invoke_load(sut.MODEL_GOV_DEPT, self.ACCOUNTS_FILE)
        self.invoke_load(sut.MODEL_SUPPLY_CHAIN, self.SC_FILE)

        # Act
        res = self.invoke_load(sut.MODEL_STRAT_ACTION, self.SA_FILE)

        # Assert
        assert re.match(f".*(Successfully) .* {sut.MODEL_STRAT_ACTION}.*", res)
        assert StrategicAction.objects.count() == 4
        assert (
            StrategicAction.objects.filter(name__startswith="Strategic action").count()
            == 4
        )

    def test_load_sau_data(self):
        # Arrange
        self.invoke_load(sut.MODEL_GOV_DEPT, self.ACCOUNTS_FILE)
        self.invoke_load(sut.MODEL_SUPPLY_CHAIN, self.SC_FILE)
        self.invoke_load(sut.MODEL_STRAT_ACTION, self.SA_FILE)

        # Act
        res = self.invoke_load(sut.MODEL_STRAT_ACTION_UPDATE, self.SAU_FILE)

        # Assert
        assert re.match(f".*(Successfully) .* {sut.MODEL_STRAT_ACTION_UPDATE}.*", res)
        assert StrategicActionUpdate.objects.count() == 4
        assert StrategicActionUpdate.objects.filter(status="submitted").count() == 4
