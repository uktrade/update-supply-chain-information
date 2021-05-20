from io import StringIO
from unittest import mock
from uuid import UUID
from datetime import date
from dateutil.relativedelta import relativedelta

import pytest
from django.core.management import call_command
from django.conf import settings

from supply_chains.models import StrategicActionUpdate
from supply_chains.management.commands.loaddata import Command

pytestmark = pytest.mark.django_db


class TestFixtureFixup:
    def call_command(self, *args, **kwargs):
        out = StringIO()
        call_command("loaddata", *args, stdout=out, stderr=StringIO(), **kwargs)
        return out.getvalue()

    def setup_method(self):
        self.ROOT_DIR = settings.BASE_DIR.parent
        self.fixtures = [
            f"{self.ROOT_DIR}/cypress/fixtures/govDepartment.json",
            f"{self.ROOT_DIR}/cypress/fixtures/user.json",
            f"{self.ROOT_DIR}/cypress/fixtures/supplyChains.json",
            f"{self.ROOT_DIR}/cypress/fixtures/strategicActions.json",
            f"{self.ROOT_DIR}/cypress/fixtures/strategicActionUpdates.json",
        ]

    def test_updates_in_month_of_base_date(self):
        """ Should leave the dates unaltered. """
        base_date = Command.BASE_DATE
        # leap_year_day = date(year=2020, month=2, day=29)
        expected_submission_dates = {
            UUID("3ac4b5ac-bba3-47e5-9964-7613aa2fcd88"): None,
            UUID("7c18ca98-5947-4ea1-9e2d-2a834462a453"): None,
            UUID("c9325de0-8233-4758-a908-b31042b0cb66"): None,
            UUID("f49fddb2-02e1-4ea2-a3bb-e8a20a107fc9"): None,
            UUID("e3fcd971-1d5a-4eab-a891-ba634d9703f3"): date(
                year=2021, month=5, day=1
            ),
            UUID("1303cbce-82c5-4cb9-b1d6-d96519f40882"): date(
                year=2021, month=4, day=22
            ),
            UUID("1c18c53b-2f7a-4539-8b34-6a12d7ba371e"): date(
                year=2021, month=4, day=22
            ),
        }
        with mock.patch(
            "supply_chains.management.commands.loaddata.date",
            mock.Mock(today=mock.Mock(return_value=base_date)),
        ):
            out = self.call_command(*self.fixtures)
            updated_submission_dates = {
                sau.pk: sau.submission_date
                for sau in StrategicActionUpdate.objects.all()
            }
            updated_last_submission_dates = {
                sau.pk: sau.supply_chain.last_submission_date
                for sau in StrategicActionUpdate.objects.all()
            }
            for pk, updated_date in updated_submission_dates.items():
                assert updated_date == expected_submission_dates[pk]
            for pk, updated_date in updated_last_submission_dates.items():
                if expected_submission_dates[pk]:
                    assert updated_date == expected_submission_dates[pk]

    def test_updates_one_month_after_base_date(self):
        """ Should set the dates one month later. """
        base_date = Command.BASE_DATE + relativedelta(months=1)
        # leap_year_day = date(year=2020, month=2, day=29)
        expected_submission_dates = {
            UUID("3ac4b5ac-bba3-47e5-9964-7613aa2fcd88"): None,
            UUID("7c18ca98-5947-4ea1-9e2d-2a834462a453"): None,
            UUID("c9325de0-8233-4758-a908-b31042b0cb66"): None,
            UUID("f49fddb2-02e1-4ea2-a3bb-e8a20a107fc9"): None,
            UUID("e3fcd971-1d5a-4eab-a891-ba634d9703f3"): date(
                year=2021, month=6, day=1
            ),
            UUID("1303cbce-82c5-4cb9-b1d6-d96519f40882"): date(
                year=2021, month=5, day=22
            ),
            UUID("1c18c53b-2f7a-4539-8b34-6a12d7ba371e"): date(
                year=2021, month=5, day=22
            ),
        }
        with mock.patch(
            "supply_chains.management.commands.loaddata.date",
            mock.Mock(today=mock.Mock(return_value=base_date)),
        ):
            out = self.call_command(*self.fixtures)
            updated_submission_dates = {
                sau.pk: sau.submission_date
                for sau in StrategicActionUpdate.objects.all()
            }
            updated_last_submission_dates = {
                sau.pk: sau.supply_chain.last_submission_date
                for sau in StrategicActionUpdate.objects.all()
            }
            for pk, updated_date in updated_submission_dates.items():
                assert updated_date == expected_submission_dates[pk]
            for pk, updated_date in updated_last_submission_dates.items():
                if expected_submission_dates[pk]:
                    assert updated_date == expected_submission_dates[pk]

    def test_updates_one_year_after_base_date(self):
        """ Should set the dates one month later. """
        base_date = Command.BASE_DATE + relativedelta(years=1)
        # leap_year_day = date(year=2020, month=2, day=29)
        expected_submission_dates = {
            UUID("3ac4b5ac-bba3-47e5-9964-7613aa2fcd88"): None,
            UUID("7c18ca98-5947-4ea1-9e2d-2a834462a453"): None,
            UUID("c9325de0-8233-4758-a908-b31042b0cb66"): None,
            UUID("f49fddb2-02e1-4ea2-a3bb-e8a20a107fc9"): None,
            UUID("e3fcd971-1d5a-4eab-a891-ba634d9703f3"): date(
                year=2022, month=5, day=1
            ),
            UUID("1303cbce-82c5-4cb9-b1d6-d96519f40882"): date(
                year=2022, month=4, day=22
            ),
            UUID("1c18c53b-2f7a-4539-8b34-6a12d7ba371e"): date(
                year=2022, month=4, day=22
            ),
        }
        with mock.patch(
            "supply_chains.management.commands.loaddata.date",
            mock.Mock(today=mock.Mock(return_value=base_date)),
        ):
            out = self.call_command(*self.fixtures)
            updated_submission_dates = {
                sau.pk: sau.submission_date
                for sau in StrategicActionUpdate.objects.all()
            }
            updated_last_submission_dates = {
                sau.pk: sau.supply_chain.last_submission_date
                for sau in StrategicActionUpdate.objects.all()
            }
            for pk, updated_date in updated_submission_dates.items():
                assert updated_date == expected_submission_dates[pk]
            for pk, updated_date in updated_last_submission_dates.items():
                if expected_submission_dates[pk]:
                    assert updated_date == expected_submission_dates[pk]

    def test_updates_one_year_before_base_date(self):
        """ Should set the dates one month later. """
        base_date = Command.BASE_DATE + relativedelta(years=-1)
        # leap_year_day = date(year=2020, month=2, day=29)
        expected_submission_dates = {
            UUID("3ac4b5ac-bba3-47e5-9964-7613aa2fcd88"): None,
            UUID("7c18ca98-5947-4ea1-9e2d-2a834462a453"): None,
            UUID("c9325de0-8233-4758-a908-b31042b0cb66"): None,
            UUID("f49fddb2-02e1-4ea2-a3bb-e8a20a107fc9"): None,
            UUID("e3fcd971-1d5a-4eab-a891-ba634d9703f3"): date(
                year=2020, month=5, day=1
            ),
            UUID("1303cbce-82c5-4cb9-b1d6-d96519f40882"): date(
                year=2020, month=4, day=22
            ),
            UUID("1c18c53b-2f7a-4539-8b34-6a12d7ba371e"): date(
                year=2020, month=4, day=22
            ),
        }
        with mock.patch(
            "supply_chains.management.commands.loaddata.date",
            mock.Mock(today=mock.Mock(return_value=base_date)),
        ):
            out = self.call_command(*self.fixtures)
            updated_submission_dates = {
                sau.pk: sau.submission_date
                for sau in StrategicActionUpdate.objects.all()
            }
            updated_last_submission_dates = {
                sau.pk: sau.supply_chain.last_submission_date
                for sau in StrategicActionUpdate.objects.all()
            }
            for pk, updated_date in updated_submission_dates.items():
                assert updated_date == expected_submission_dates[pk]
            for pk, updated_date in updated_last_submission_dates.items():
                if expected_submission_dates[pk]:
                    assert updated_date == expected_submission_dates[pk]
