import csv
import os

from django.conf import settings
from django.core.management import BaseCommand
from django.utils.text import slugify

from supply_chains.models import SupplyChain, ScenarioAssessment, NullableRAGRating


class Command(BaseCommand):
    """Utility to ingest country dependency spreadsheet data"""

    filepath = None
    unrecognised_supply_chains = set()

    def add_arguments(self, parser):
        parser.add_argument(
            "csvfile",
            help="The file system path to the CSV file with the data to import",
        )

    def handle(self, **options):
        self.filepath = options["csvfile"]
        if not os.path.isabs(self.filepath):
            self.filepath = settings.BASE_DIR / self.filepath
        self.ingest_scenario_assessments()

    def ingest_scenario_assessments(self):
        for assessment_kwargs in self.source_assessments:
            ScenarioAssessment.objects.get_or_create(**assessment_kwargs)
        if self.unrecognised_supply_chains:
            self.stdout.write(
                self.style.ERROR(
                    f"Unrecognised supply chains: {len(self.unrecognised_supply_chains)}"
                )
            )
            for supply_chain_name in sorted(self.unrecognised_supply_chains):
                self.stdout.write(self.style.ERROR(supply_chain_name))
        else:
            self.stdout.write(self.style.SUCCESS("No unrecognised supply chains."))

    @property
    def source_assessments(self):
        supply_chains_by_name = {
            supply_chain.name: supply_chain
            for supply_chain in SupplyChain.objects.all()
        }
        supply_chain_names = supply_chains_by_name.keys()
        current_supply_chain_name = None
        current_assessment_kwargs = {}
        for assessment_row in self.source_data:
            supply_chain_name = assessment_row["supply_chain_name"].strip()
            if (
                supply_chain_name != current_supply_chain_name
                and current_assessment_kwargs
            ):
                yield current_assessment_kwargs
                current_assessment_kwargs = {}
            if not supply_chain_name:
                # The CSV can have empty rows after the data, giving "" as the supply chain name
                break
            if supply_chain_name not in supply_chain_names:
                self.unrecognised_supply_chains.add(supply_chain_name)
                continue
            if not current_assessment_kwargs:
                current_supply_chain_name = supply_chain_name
                try:
                    current_assessment_kwargs = {
                        "supply_chain": supply_chains_by_name[
                            current_supply_chain_name
                        ],
                    }
                except KeyError:
                    continue
            # the data contains a scenario that's no longer relavent
            if assessment_row["scenario_name"].startswith("End of transition"):
                continue
            scenario_type = assessment_row["scenario_name"].replace(" ", "_")
            kwargs = {
                f"{scenario_type}_impact": assessment_row["impact"],
                f"{scenario_type}_rag_rating": assessment_row["rag_rating"],
                f"{scenario_type}_is_critical": int(assessment_row["is_critical"]),
                f"{scenario_type}_critical_scenario": assessment_row[
                    "critical_scenario"
                ],
            }
            # Handle anomalous values in initial data dump
            rag_rating_key = f"{scenario_type}_rag_rating"
            if kwargs[rag_rating_key] == "n/a" or kwargs[rag_rating_key] == "tbc":
                kwargs[rag_rating_key] = "none"
            # Need to turn the RAG rating into a value from the choices
            kwargs[rag_rating_key] = getattr(
                NullableRAGRating, kwargs[rag_rating_key].upper()
            )
            for kwarg, value in kwargs.items():
                if kwarg in current_assessment_kwargs:
                    raise ValueError(
                        f"{supply_chain_name} already has value for {kwarg}"
                    )
                current_assessment_kwargs[kwarg] = value

    @property
    def source_data(self):
        with open(
            self.filepath, "r", encoding="utf-8-sig"
        ) as country_file:  # encoding specified as export has BOM
            reader = csv.DictReader(
                country_file,
                fieldnames=(
                    "supply_chain_identifier",
                    "supply_chain_name",
                    "scenario_type",
                    "scenario_name",
                    "rag_rating",
                    "impact",
                    "is_critical",
                    "critical_scenario",
                ),
            )
            # As fieldnames has been supplied, the first row will appear as a  data row, so discard it
            next(reader)
            for row in reader:
                yield row
        # make sure we send an empty thing back to the consumer so they know we're at the end
        # this might be avoidable if the logic in 'source_assessments' didn't have to be so complicated ;)
        yield {"supply_chain_name": ""}
