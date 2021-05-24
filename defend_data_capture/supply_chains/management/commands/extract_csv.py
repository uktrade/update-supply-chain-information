import csv
import json
from typing import List
from io import StringIO

from django.core import management
from django.core.management.commands import dumpdata
from django.core.management.base import BaseCommand, CommandError

from supply_chains.management.commands.ingest_csv import ALL_MODELS


class Command(BaseCommand):
    help = "Extract CSV formatted resilience tool data"

    def add_arguments(self, parser):
        parser.add_argument(
            "model",
            help=f"model from which data is being extracted. Supported models {ALL_MODELS}",
        )

        parser.add_argument(
            "csvfile",
            help="The file system path to the CSV file to save data",
        )

    def _format_from_django_object(self, rows: List) -> List:
        """Format data from Django style object.

        :param List rows: data from model structured as list

        Refer https://docs.djangoproject.com/en/3.2/topics/serialization/#serialization-formats-json
        for more info.
        """
        formatted_obj = list()

        for row in rows:
            formatted_row = {}
            formatted_row["id"] = row["pk"]

            for k, v in row["fields"].items():
                formatted_row[k] = v

            formatted_obj.append(formatted_row)

        return formatted_obj

    def handle(self, **options):
        if options["model"] not in ALL_MODELS:
            raise CommandError(
                f"Unknown model {options['model']}. \n\nRefer help for supported values"
            )

        try:
            with StringIO() as status:
                management.call_command(
                    dumpdata.Command(),
                    options["model"],
                    format="json",
                    indent=2,
                    stdout=status,
                )

                json_obj = json.loads(status.getvalue())
                data = self._format_from_django_object(json_obj)

                with open(options["csvfile"], "w", newline="") as fp:
                    if len(data):
                        header = list(data[0].keys())
                        writer = csv.DictWriter(fp, fieldnames=header)
                        writer.writeheader()

                        writer.writerows(data)

                    else:
                        pass

                self.stdout.write(
                    self.style.SUCCESS(
                        f"Successfully extracted data from {options['model']} to {options['csvfile']}"
                    )
                )
        except Exception as e:
            raise CommandError(f"\n{str(e)}")
