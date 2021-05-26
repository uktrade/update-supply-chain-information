from io import StringIO
from typing import List
import os
import csv
import re

import pytest
from django.core.management import call_command
from django.core.management.base import CommandError
from django.core.files.temp import NamedTemporaryFile

from supply_chains.management.commands.ingest_csv import (
    MODEL_GOV_DEPT,
    MODEL_SUPPLY_CHAIN,
    MODEL_STRAT_ACTION,
    MODEL_STRAT_ACTION_UPDATE,
)

from supply_chains.test.factories import (
    SupplyChainFactory,
    StrategicActionFactory,
    StrategicActionUpdateFactory,
    GovDepartmentFactory,
)

pytestmark = pytest.mark.django_db


class TestExtractCSV:
    DUMP_CMD = "extract_csv"

    def setup_method(self):
        self.data_file = NamedTemporaryFile(suffix=".csv", delete=False)

    def teardown_method(self):
        os.remove(self.data_file.name)

    def load_csv(self) -> List:
        with open(self.data_file.name) as f:
            reader = csv.DictReader(f)
            rows = list(reader)

        return rows

    def invoke_dump(self, *args):
        with StringIO() as status:
            call_command(self.DUMP_CMD, *args, stdout=status)
            return status.getvalue()

    def test_dump_accounts_data(self):
        # Arrange
        trade_domian = "trade.gov.uk"
        trade_name = "DiT"
        hmrc_domain = "hmrc.gov.uk"
        hmrc_name = "HMRC"
        GovDepartmentFactory(email_domains=[trade_domian], name=trade_name)
        GovDepartmentFactory(email_domains=[hmrc_domain], name=hmrc_name)

        # Act
        self.invoke_dump(MODEL_GOV_DEPT, self.data_file.name)
        rows = self.load_csv()

        # Assert
        assert len(rows) == 2

        lookup = {x["name"]: x for x in rows}
        assert (
            lookup[trade_name]["name"] == trade_name
            and lookup[trade_name]["email_domain_0"] == trade_domian
        )
        assert (
            lookup[hmrc_name]["name"] == hmrc_name
            and lookup[hmrc_name]["email_domain_0"] == hmrc_domain
        )

    def test_dump_accounts_data_multi_domain(self):
        # Arrange
        trade_domians = "trade.gov.uk", "digital.trade.gov.uk"
        trade_name = "DiT"
        GovDepartmentFactory(email_domains=trade_domians, name=trade_name)

        # Act
        self.invoke_dump(MODEL_GOV_DEPT, self.data_file.name)
        rows = self.load_csv()

        # Assert
        assert len(rows) == 1
        assert all(k in rows[0] for k in ("email_domain_0", "email_domain_1"))

    def test_dump_accounts_no_data(self):
        # Arrange
        # Act
        self.invoke_dump(MODEL_GOV_DEPT, self.data_file.name)

        # Assert
        assert os.path.exists(self.data_file.name)
        assert os.stat(self.data_file.name).st_size == 0

    def test_dump_sc_data(self):
        # Arrange
        SupplyChainFactory()

        # Act
        self.invoke_dump(MODEL_SUPPLY_CHAIN, self.data_file.name)
        rows = self.load_csv()

        # Assert
        assert len(rows) == 1
        assert re.match(f"Product ", rows[0]["name"])

    def test_dump_sc_data_multiple(self):
        # Arrange
        SupplyChainFactory.create_batch(5)

        # Act
        self.invoke_dump(MODEL_SUPPLY_CHAIN, self.data_file.name)
        rows = self.load_csv()

        # Assert
        assert len(rows) == 5

        names = [x["name"] for x in rows]
        assert all([x.startswith("Product ") for x in names])

        ids = [x["id"] for x in rows]
        assert len(ids) == len(set(ids))

    def test_dump_sa_data(self):
        # Arrange
        sc = SupplyChainFactory()
        StrategicActionFactory(supply_chain=sc)

        # Act
        self.invoke_dump(MODEL_STRAT_ACTION, self.data_file.name)
        rows = self.load_csv()

        # Assert
        assert len(rows) == 1
        assert re.match(f"Strategic action ", rows[0]["name"])
        assert rows[0]["supply_chain"] == str(sc.id)

    def test_dump_sa_data_multiple(self):
        # Arrange
        exp_sc_ids = list()
        for _ in range(4):
            sc = SupplyChainFactory()
            StrategicActionFactory(supply_chain=sc)
            exp_sc_ids.append(str(sc.id))

        # Act
        self.invoke_dump(MODEL_STRAT_ACTION, self.data_file.name)
        rows = self.load_csv()

        # Assert
        assert len(rows) == 4

        ids = [x["id"] for x in rows]
        assert len(ids) == len(set(ids))

        sc_ids = [x["supply_chain"] for x in rows]
        assert all([a == b for a, b in zip(sorted(sc_ids), sorted(exp_sc_ids))])

        names = [x["name"] for x in rows]
        assert all([x.startswith("Strategic action ") for x in names])

    def test_dump_sau_data(self):
        # Arrange
        sc = SupplyChainFactory()
        sa = StrategicActionFactory(supply_chain=sc)
        StrategicActionUpdateFactory(supply_chain=sc, strategic_action=sa)

        # Act
        self.invoke_dump(MODEL_STRAT_ACTION_UPDATE, self.data_file.name)
        rows = self.load_csv()

        # Assert
        assert len(rows) == 1
        assert rows[0]["supply_chain"] == str(sc.id)
        assert rows[0]["strategic_action"] == str(sa.id)

    def test_dump_sau_data_multiple(self):
        # Arrange
        exp_sc_ids = list()
        exp_sa_ids = list()
        for _ in range(4):
            sc = SupplyChainFactory()
            sa = StrategicActionFactory(supply_chain=sc)
            StrategicActionUpdateFactory(supply_chain=sc, strategic_action=sa)
            exp_sc_ids.append(str(sc.id))
            exp_sa_ids.append(str(sa.id))

        # Act
        self.invoke_dump(MODEL_STRAT_ACTION_UPDATE, self.data_file.name)
        rows = self.load_csv()

        # Assert
        assert len(rows) == 4

        ids = [x["id"] for x in rows]
        assert len(ids) == len(set(ids))

        sc_ids = [x["supply_chain"] for x in rows]
        assert all([a == b for a, b in zip(sorted(sc_ids), sorted(exp_sc_ids))])

        sa_ids = [x["strategic_action"] for x in rows]
        assert all([a == b for a, b in zip(sorted(sa_ids), sorted(exp_sa_ids))])

    def test_dump_inv_model(self):
        # Arrange
        inv_model = "hello world"

        # Act
        # Assert
        with pytest.raises(CommandError, match=f"Unknown model {inv_model}"):
            self.invoke_dump(inv_model, self.data_file.name)
