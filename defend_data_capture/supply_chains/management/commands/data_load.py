import csv
import json
from typing import List
from datetime import date, datetime
from pprint import pprint

from django.core import management
from django.core.management.commands import loaddata
from django.core.management.base import BaseCommand, CommandError
from django.core.files.temp import NamedTemporaryFile

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


class Command(BaseCommand):
    help = "Ingest CSV formatted data"

    def add_arguments(self, parser):
        parser.add_argument(
            "--model",
            help=f"model to which data is being ingested.{', '.join(ALL_MODELS)}",
        )

        parser.add_argument(
            "--csvfile",
            help="The file system path to the CSV file with the data to import",
        )

    def _get_json_object(self, csv_file: str) -> object:
        with open(csv_file) as f:
            reader = csv.DictReader(f)
            rows = list(reader)

            print(f"Row[0]: {rows[0]}")

        return json.dumps(rows)

    def _format_json_object(self, model: str, rows: object) -> object:
        formatted_obj = list()

        for row in rows:
            formatted_row = {}
            formatted_row["model"] = model
            # print(f'Row: {row}')
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

    def _format_per_model(self, rows: List) -> List:

        for row in rows:
            # TODO: Refactor code to minimise comparisons
            if row["model"] == MODEL_SUPPLY_CHAIN:
                row["fields"]["archived_date"] = self._reformat_date(
                    row["fields"]["archived_date"]
                )
                row["fields"]["last_submission_date"] = self._reformat_date(
                    row["fields"]["last_submission_date"]
                )

            elif row["model"] == MODEL_STRAT_ACTION:
                row["fields"]["start_date"] = self._reformat_date(
                    row["fields"]["start_date"]
                )
                row["fields"]["target_completion_date"] = self._reformat_date(
                    row["fields"]["target_completion_date"]
                )
                row["fields"]["archived_date"] = self._reformat_date(
                    row["fields"]["archived_date"]
                )

                row["fields"].pop("str( not required in database)", None)

            elif row["model"] == MODEL_STRAT_ACTION_UPDATE:
                row["fields"]["submission_date"] = self._reformat_date(
                    row["fields"]["submission_date"]
                )
                row["fields"]["date_created"] = self._reformat_date(
                    row["fields"]["date_created"]
                )

            elif row["model"] == MODEL_GOV_DEPT:
                row["fields"]["email_domains"] = [row["fields"]["email_domains"]]

        return rows

    def handle(self, *args, **options):
        obj = json.loads(self._get_json_object(options["csvfile"]))
        json_obj = self._format_json_object(options["model"], obj)

        with NamedTemporaryFile(suffix=".json", mode="w") as fp:
            json.dump(json_obj, fp)
            fp.seek(0)
            management.call_command(loaddata.Command(), fp.name, format="json")

        self.stdout.write(
            self.style.SUCCESS(f"Successfully ingested data into {options['model']}")
        )
