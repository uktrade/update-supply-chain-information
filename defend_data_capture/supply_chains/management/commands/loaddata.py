from datetime import date

from dateutil.relativedelta import relativedelta
from django.core.management.commands.loaddata import Command as OriginalCommand

from supply_chains.models import StrategicActionUpdate


class Command(OriginalCommand):
    BASE_DATE = date(year=2021, month=5, day=1)

    def handle(self, *fixture_labels, **options):
        super().handle(*fixture_labels, **options)
        months_to_add = relativedelta(months=self.calculate_months_to_add())
        updates = StrategicActionUpdate.objects.all()
        self.update_submission_dates(updates, months_to_add)

    def update_submission_dates(self, updates, months_to_add):
        updated_updates = []
        for update in updates:
            if update.submission_date is not None:
                update.submission_date += months_to_add
                updated_updates.append(update)
        StrategicActionUpdate.objects.bulk_update(updated_updates, ["submission_date"])

    def calculate_months_to_add(self):
        today = date.today()
        month_difference = today.month - self.BASE_DATE.month
        year_difference = today.year - self.BASE_DATE.year
        months_to_add = month_difference + (year_difference * 12)
        return months_to_add
