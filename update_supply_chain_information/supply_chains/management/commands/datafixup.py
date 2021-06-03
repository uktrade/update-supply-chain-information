from datetime import date

from dateutil.relativedelta import relativedelta
from django.core.management import BaseCommand
from django.db import connection

from supply_chains.models import SupplyChain, StrategicActionUpdate

Status = StrategicActionUpdate.Status

# exclude_update_list = [
#     "ae9a9de0-1e98-4c36-96bd-1cc98b0eaf51", # Supply Chain 7, SA Title Test
# ]


class Command(BaseCommand):
    BASE_DATE = date(year=2021, month=5, day=1)

    def add_arguments(self, parser):
        parser.add_argument("--dev", action="store_true")

    def handle(self, **options):
        db_instance = "Dev"

        if not options["dev"]:
            connection.creation.create_test_db(keepdb=True)
            db_instance = "Test"

        months_to_add = relativedelta(months=self.calculate_months_to_add())
        updates = StrategicActionUpdate.objects.all()
        self.update_submission_and_created_dates(updates, months_to_add)
        self.stdout.write(self.style.SUCCESS(f"Fixtures fixed on {db_instance} db"))

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
                    # if update.id in exclude_update_list:
                    #     continue
                    update.date_created += months_to_add
                    print(
                        f"----- ID : {update.id}\t{update.status}\tDate created: {update.date_created} ----"
                    )
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
