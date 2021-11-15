import csv
import json
from typing import List, Dict
from datetime import date, datetime

from django.core import management
from django.core.management.commands import loaddata
from django.core.management.base import BaseCommand, CommandError
from django.core.files.temp import NamedTemporaryFile

from supply_chains.models import SupplyChain, StrategicAction, StrategicActionUpdate
from accounts.models import GovDepartment

MODEL_GOV_DEPT = "accounts.govdepartment"
MODEL_SUPPLY_CHAIN = "supply_chains.supplychain"
MODEL_STRAT_ACTION = "supply_chains.strategicaction"
MODEL_STRAT_ACTION_UPDATE = "supply_chains.strategicactionupdate"

ALL_MODELS = [
    MODEL_GOV_DEPT,
    MODEL_SUPPLY_CHAIN,
    MODEL_STRAT_ACTION,
    MODEL_STRAT_ACTION_UPDATE,
]

GENERIC_ARCHIVE_REASON = "Archived with generic reason"


class Command(BaseCommand):
    help = "Ingest CSV formatted resilience tool data"

    def add_arguments(self, parser):
        parser.add_argument(
            "model",
            help=f"model to which data is being ingested. Supported models {ALL_MODELS}",
        )

        parser.add_argument(
            "csvfile",
            help="The file system path to the CSV file with the data to import",
        )

    def _get_json_object(self, csv_file: str) -> object:
        with open(csv_file) as f:
            reader = csv.DictReader(f)
            rows = list(reader)

        return json.dumps(rows)

    def _format_to_django_object(self, model: str, rows: List) -> List:
        """Format ingest data as per Django expectation.

        :param str model: specify the model to which data will be imported
        :param object rows: json object with parsed data from CSV file

        Refer https://docs.djangoproject.com/en/3.2/topics/serialization/#serialization-formats-json
        for more info.
        """
        formatted_obj = list()

        for row in rows:
            formatted_row = {}
            formatted_row["model"] = model
            formatted_row["pk"] = row["id"]
            formatted_row["fields"] = {}

            for k, v in row.items():
                if k != "id":
                    formatted_row["fields"][k] = v

            formatted_obj.append(formatted_row)

        return self._format_per_model(formatted_obj)

    def _reformat_date(self, in_date: str) -> str:
        if in_date:
            d = datetime.strptime(in_date, r"%m/%d/%y")
            return d.strftime(r"%Y-%m-%d")
        else:
            return None

    def _update_date_fields(self, row: Dict, *fields):
        for f in fields:
            row[f] = self._reformat_date(row[f])

    def _update_archive_fields(self, row: Dict) -> Dict:
        if row["fields"]["is_archived"] == "0":
            row["fields"]["is_archived"] = False
        elif row["fields"]["is_archived"] == "1":
            row["fields"]["is_archived"] = True

        if row["fields"]["is_archived"]:
            # As archive for supply chain is added recently, historic data may not have all the properties
            try:
                row["fields"]["archived_reason"]
            except KeyError:
                row["fields"]["archived_reason"] = ""

            if row["fields"]["archived_reason"] == "":
                row["fields"]["archived_reason"] = GENERIC_ARCHIVE_REASON

        return row

    def _format_per_model(self, rows: List) -> List:

        for row in rows:
            if row["model"] == MODEL_SUPPLY_CHAIN:
                self._update_date_fields(
                    row["fields"], "archived_date", "last_submission_date"
                )

                row["fields"]["vulnerability_status"] = row["fields"][
                    "vulnerability_status"
                ].upper()

                row = self._update_archive_fields(row)

            elif row["model"] == MODEL_STRAT_ACTION:
                self._update_date_fields(
                    row["fields"],
                    "start_date",
                    "target_completion_date",
                    "archived_date",
                )

                row["fields"].pop("str( not required in database)", None)

                orgs = row["fields"]["supporting_organisations"]
                row["fields"]["supporting_organisations"] = [
                    x.strip() for x in orgs.split(",")
                ]

                row = self._update_archive_fields(row)

            elif row["model"] == MODEL_STRAT_ACTION_UPDATE:
                self._update_date_fields(
                    row["fields"], "submission_date", "date_created"
                )

                row["fields"]["date_created"] = (
                    row["fields"]["date_created"] or row["fields"]["submission_date"]
                )

                row["fields"]["user"] = row["fields"]["user"] or None
                row["fields"].pop("actual supply chain name (not in database)", None)

            elif row["model"] == MODEL_GOV_DEPT:
                row["fields"]["email_domains"] = [row["fields"]["email_domains"]]

        return rows

    def _save_objects(self, model: str) -> None:
        """Save objects being ingested

        :param str model: specify the model to which data will be imported

        This method is necessary to trigger our save over-rides within models as exisitng
        admin command loaddata doesn't invoke that.
        """
        if model == MODEL_GOV_DEPT:
            ingested_model = GovDepartment

        if model == MODEL_SUPPLY_CHAIN:
            ingested_model = SupplyChain

        if model == MODEL_STRAT_ACTION:
            ingested_model = StrategicAction

        if model == MODEL_STRAT_ACTION_UPDATE:
            ingested_model = StrategicActionUpdate

        try:
            for obj in ingested_model.objects.all():
                obj.save()
        except Exception:
            print(f"Deleting ingested data for {model}")
            ingested_model.objects.all().delete()
            raise

    def handle(self, **options):
        if options["model"] not in ALL_MODELS:
            raise CommandError(
                f"Unknown model {options['model']}. \n\nRefer help for supported values"
            )

        obj = json.loads(self._get_json_object(options["csvfile"]))
        # As an `auto_now` field cannot be null, but `loaddata` (which is used by this command)
        # bypasses both `Model.save()` and 'QuerySet.update()` by going directly to the database,
        # data ingestion causes an IntegrityError unless the `last_modified` field's value is explicitly set.
        # The value used is `datetime.now()` to replicate the normal behaviour
        # when an object with an `auto_now` field is created.
        for row in obj:
            if "last_modified" not in row:
                row["last_modified"] = datetime.now().strftime(r"%Y-%m-%dT%H:%M:%S.%f")
        json_obj = self._format_to_django_object(options["model"], obj)

        with NamedTemporaryFile(suffix=".json", mode="w") as fp:
            json.dump(json_obj, fp)
            fp.seek(0)
            management.call_command(loaddata.Command(), fp.name, format="json")
            self._save_objects(options["model"])
            self.stdout.write(
                self.style.SUCCESS(
                    f"Successfully ingested data into {options['model']}"
                )
            )
