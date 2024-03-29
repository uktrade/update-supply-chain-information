from datetime import date

from dateutil.relativedelta import relativedelta
from django.core.management import BaseCommand
from django.db import connection

from supply_chains.models import SupplyChain, StrategicActionUpdate

Status = StrategicActionUpdate.Status


class Command(BaseCommand):
    """Utility to manipulate sample data/fixtures

    Note: This command will write into database and update mostly date related fileds.
    Hence care must be taken while running this command.
    """

    BASE_DATE = date(year=2021, month=5, day=1)

    def get_confirmtion(self):
        answer = ""
        while answer not in ["y", "n"]:
            answer = input("Continue to modify exisitng data [Y/N]? ").lower()
        return answer == "y"

    def add_arguments(self, parser):
        parser.add_argument(
            "--noinput",
            action="store_true",
            help="do not prompt for confimation",
        )

    def handle(self, **options):
        db_name = connection.settings_dict["NAME"]

        if not options["noinput"]:
            if not self.get_confirmtion():
                return

        months_to_add = relativedelta(months=self.calculate_months_to_add())
        updates = StrategicActionUpdate.objects.all()
        self.update_submission_and_created_dates(updates, months_to_add)
        self.stdout.write(self.style.SUCCESS(f"Fixtures fixed on {db_name} db"))

    def update_submission_and_created_dates(self, updates, months_to_add):
        updated_updates = []
        updated_supply_chains = []
        for update in updates:
            if update.status in [Status.SUBMITTED, Status.READY_TO_SUBMIT]:
                if update.submission_date:
                    update.submission_date += months_to_add
                    update.date_created += months_to_add
                    update.supply_chain.last_submission_date = update.submission_date
                    updated_updates.append(update)
                    updated_supply_chains.append(update.supply_chain)
                else:
                    update.date_created += months_to_add
                    updated_updates.append(update)

        StrategicActionUpdate.objects.bulk_update(
            updated_updates, ["submission_date", "date_created"]
        )
        SupplyChain.objects.bulk_update(updated_supply_chains, ["last_submission_date"])

    def calculate_months_to_add(self):
        today = date.today()
        month_difference = today.month - self.BASE_DATE.month
        year_difference = today.year - self.BASE_DATE.year
        months_to_add = month_difference + (year_difference * 12)
        return months_to_add
