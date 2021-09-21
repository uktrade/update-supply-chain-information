import csv
import os

from django.conf import settings
from django.core.management import BaseCommand

from supply_chains.models import SupplyChain, Country, CountryDependency


class Command(BaseCommand):
    """Utility to ingest country dependency spreadsheet data"""

    class EmptyNameError(Exception):
        pass

    filepath = None

    unrecognised_supply_chains = []
    countries_ingested = 0
    supply_chains_found = 0
    dependencies_ingested = 0

    FIRST_COUNTRY_COLUMN = 7
    SUPPLY_CHAIN_NAME_FIELD = "Supply Chain Name"
    source_dependency_level_to_choice_value = {
        # Spreadsheet has an empty string for "No dependency" so munge the label in the value lookup table
        choice[1].lower() if choice[1] != "No" else "": choice[0]
        for choice in CountryDependency.DependencyLevel.choices
    }

    def add_arguments(self, parser):
        parser.add_argument(
            "csvfile",
            help="The file system path to the CSV file with the data to import",
        )

    def handle(self, **options):
        self.filepath = options["csvfile"]
        if not os.path.isabs(self.filepath):
            self.filepath = settings.BASE_DIR / self.filepath
        self.ingest_countries()
        self.ingest_supply_chain_country_dependencies()
        self.stdout.write(
            self.style.ERROR(f"Countries ingested: {self.countries_ingested}")
        )
        self.stdout.write(
            self.style.SUCCESS(f"Supply chains found: {self.supply_chains_found}")
        )
        self.stdout.write(
            self.style.SUCCESS(f"Dependencies ingested: {self.dependencies_ingested}")
        )
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

    def ingest_countries(self):
        for country_name in self.source_country_names:
            Country.objects.get_or_create(name=country_name)
            self.countries_ingested += 1

    def ingest_supply_chain_country_dependencies(self):
        for row in self.supply_chain_country_dependencies:
            try:
                self.ingest_row(row)
            except self.EmptyNameError:
                return

    def ingest_row(self, source_country_dependencies):
        supply_chain_name = source_country_dependencies[self.SUPPLY_CHAIN_NAME_FIELD]
        if not supply_chain_name:
            raise self.EmptyNameError
        try:
            supply_chain = SupplyChain.objects.get(name__iexact=supply_chain_name)
            self.supply_chains_found += 1
        except SupplyChain.DoesNotExist:
            self.unrecognised_supply_chains.append(supply_chain_name)
            return
        for country in self.known_countries:
            source_dependency_level = source_country_dependencies[country.name]
            dependency_level = self.source_dependency_level_to_choice_value[
                source_dependency_level.lower()
            ]
            CountryDependency.objects.get_or_create(
                country=country,
                supply_chain=supply_chain,
                dependency_level=dependency_level,
            )
            self.dependencies_ingested += 1

    _known_countries = None

    @property
    def known_countries(self):
        if self._known_countries is None:
            self._known_countries = Country.objects.all()
        return self._known_countries

    @property
    def source_country_names(self):
        return self.fieldnames[self.FIRST_COUNTRY_COLUMN :]

    @property
    def fieldnames(self):
        with open(
            self.filepath, "r", encoding="utf-8-sig"
        ) as country_file:  # encoding specified as export has BOM
            reader = csv.DictReader(country_file)
            return reader.fieldnames

    @property
    def supply_chain_country_dependencies(self):
        with open(
            self.filepath, "r", encoding="utf-8-sig"
        ) as country_file:  # encoding specified as export has BOM
            reader = csv.DictReader(country_file)
            for row in reader:
                yield row
