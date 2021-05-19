from datetime import date, timedelta
from io import StringIO

import pytest
from django.test import Client
from django.urls import reverse
from django.template.defaultfilters import slugify
from django.core.management import call_command

# from supply_chains.models import SupplyChain
# from supply_chains.test.factories import SupplyChainFactory, GovDepartmentFactory


pytestmark = pytest.mark.django_db


class TestDataLoader:
    LOAD_CMD = "data_loader"

    def invoke_load(self, *args, **kwargs):
        out = StringIO()
        call_command(self.LOAD_CMD, *args, stdout=out, stderr=StringIO(), **kwargs)
        return out.getvalue()

    def test_loader_help(self):
        res = self.invoke_load("--help")
        print(res)

        # assert False

    def test_load_accounts_data(self):
        pass
