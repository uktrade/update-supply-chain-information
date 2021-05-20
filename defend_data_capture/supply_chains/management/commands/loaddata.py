from datetime import date

from dateutil.relativedelta import relativedelta
from django.core.management.commands.loaddata import Command as OriginalCommand

from supply_chains.models import SupplyChain, StrategicActionUpdate


class Command(OriginalCommand):
    BASE_DATE = date(year=2021, month=5, day=1)

    def handle(self, *fixture_labels, **options):
        super().handle(*fixture_labels, **options)
        months_to_add = relativedelta(months=self.calculate_months_to_add())
        updates = StrategicActionUpdate.objects.all()
        self.update_submission_and_created_dates(updates, months_to_add)

    def update_submission_and_created_dates(self, updates, months_to_add):
        updated_updates = []
        updated_supply_chains = []
        for update in updates:
            if update.status == StrategicActionUpdate.Status.SUBMITTED:
                if update.submission_date is not None:
                    update.submission_date += months_to_add
                    update.date_created += months_to_add
                    update.supply_chain.last_submission_date = update.submission_date
                    updated_updates.append(update)
                    updated_supply_chains.append(update.supply_chain)
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
