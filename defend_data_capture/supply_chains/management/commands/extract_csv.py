import csv
import json
from typing import List
from io import StringIO

from django.core import management
from django.core.management.commands import dumpdata
from django.core.management.base import BaseCommand, CommandError

from supply_chains.management.commands.ingest_csv import ALL_MODELS, MODEL_GOV_DEPT


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

    def _serialise_gov_department(self, rows: List) -> List:
        """Serialise model to a generic CSV format

        With email_domains field added as ArrayField to the GovDepartment model, built-in
        serialiser would leave additional escape chars in the chosen format(CSV)
        This helper would strip those chars and flatten the list.

        @param List rows: data extracted from chosen model
        @return: List of rows formatted for CSV
        """
        formatted_rows = list()
        domains_size = 0

        # iterate through the rows,
        # - Remove escape/meta chars - []""
        # - Add email_domains_$i field for every domain encountered
        # - Push largest domains to the top of the list - This will be header for CSV
        for row in rows:
            formatted_row = {}
            for k, v in row.items():
                if k == "email_domains":
                    # ["trade.gov.uk", "digital.trade.gov.uk"] -> trade.gov.uk, digital.trade.gov.uk
                    domains = v[1:-1]
                    domains = domains.replace('"', "")

                    domain_tokens = domains.split(",")

                    for index in range(len(domain_tokens)):
                        formatted_row[f"email_domains_{index}"] = domain_tokens[
                            index
                        ].strip()
                else:
                    formatted_row[k] = v

            if len(domain_tokens) > domains_size:
                domains_size = len(domain_tokens)
                formatted_rows.insert(0, formatted_row)
            else:
                formatted_rows.append(formatted_row)

        return formatted_rows

    def handle(self, **options):
        if options["model"] not in ALL_MODELS:
            raise CommandError(
                f"Unknown model {options['model']}. \n\nRefer to help for supported values"
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

                if options["model"] == MODEL_GOV_DEPT:
                    data = self._serialise_gov_department(data)

                with open(options["csvfile"], "w", newline="") as fp:
                    if len(data):
                        header = list(data[0].keys())
                        writer = csv.DictWriter(fp, fieldnames=header)
                        writer.writeheader()

                        writer.writerows(data)

                self.stdout.write(
                    self.style.SUCCESS(
                        f"Successfully extracted data from {options['model']} to {options['csvfile']}"
                    )
                )
        except Exception as e:
            raise CommandError(f"\n{str(e)}")
