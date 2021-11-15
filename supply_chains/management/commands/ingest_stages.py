import csv
from typing import Dict

from django.core.management.base import BaseCommand

from supply_chains.models import (
    SupplyChain,
    SupplyChainStage,
    SupplyChainStageSection,
)


STAGE_NAME_VALUE_LOOKUP = {
    item[1]: item[0] for item in SupplyChainStage.StageName.choices
}

SECTION_NAME_VALUE_LOOKUP = {
    item[1]: item[0] for item in SupplyChainStageSection.SectionName.choices
}


def _update_stage(sc: SupplyChain, row: Dict) -> object:
    stage, _ = SupplyChainStage.objects.get_or_create(
        supply_chain=sc,
        order=row["Order"],
        name=STAGE_NAME_VALUE_LOOKUP[row["Stage"]],
    )

    stage.save()

    return stage


def _update_section(sc: SupplyChain, stage: SupplyChainStage, row: Dict) -> object:
    section, created = SupplyChainStageSection.objects.get_or_create(
        chain_stage=stage,
        name=SECTION_NAME_VALUE_LOOKUP[row["Stage-section"]],
        description=row["Description"],
    )

    if created is False:
        raise Exception(
            f"Unexpected: Pre-existing section:  {sc}:{stage}:{section.name}"
        )

    section.save()

    return section


class Command(BaseCommand):
    help = "Ingest CSV formatted resilience tool stage data"

    def add_arguments(self, parser):
        parser.add_argument(
            "stages_file",
            help="CSV formatted file with stage data",
        )

    def handle(self, **options):
        with open(options["stages_file"], "r") as fp:
            reader = csv.DictReader(fp)
            stage_mappings = list(reader)

        self.stdout.write(
            self.style.HTTP_INFO(f"\nIngesting {len(stage_mappings)} rows...\n")
        )

        stage_mappings.sort(key=lambda x: x["Supply Chain"])

        unknown_chains = set()
        success_rows = error_count = 0

        try:
            for _, row in enumerate(stage_mappings):
                row["Supply Chain"] = row["Supply Chain"].strip()
                row["Stage"] = row["Stage"].strip()

                try:
                    sc = SupplyChain.objects.get(name=row["Supply Chain"])
                except SupplyChain.DoesNotExist:
                    error_count += 1
                    unknown_chains.add(row["Supply Chain"])
                    continue
                else:
                    stage = _update_stage(sc, row)
                    section = _update_section(sc, stage, row)
                    success_rows += 1
        except:
            print(
                f'Inserting SC: {sc.name}\nStage: {row["Stage"]}\nOrder: {row["Order"]}'
            )
            raise

        self.stdout.write(
            self.style.SUCCESS(f"{success_rows} rows ingested into the system\n")
        )

        if error_count:
            self.stdout.write(
                self.style.HTTP_INFO(
                    f"\nFailed to ingest {error_count} rows due to below unknown supply chains\n"
                )
            )
            print("\n".join(unknown_chains))
            print("\n")
