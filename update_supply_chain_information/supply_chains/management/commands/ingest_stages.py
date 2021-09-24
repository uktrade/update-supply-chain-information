import csv
import json
from os import name
from typing import List, Dict
from datetime import date, datetime
import typing

from django.core import management
from django.core.management.commands import loaddata
from django.core.management.base import BaseCommand, CommandError
from django.core.files.temp import NamedTemporaryFile

from supply_chains.models import (
    SupplyChain,
    StrategicAction,
    StrategicActionUpdate,
    SupplyChainStage,
    SupplyChainStageSection,
)
from accounts.models import GovDepartment


SC_LIST = r"temp/etl/data/latest_desc.json"

STAGE_NAME_VALUE_LOOKUP = {
    item[1]: item[0] for item in SupplyChainStage.StageName.choices
}

SECTION_NAME_VALUE_LOOKUP = {
    item[1]: item[0] for item in SupplyChainStageSection.SectionName.choices
}


def _update_stage(sc: SupplyChain, row: Dict) -> object:
    # print(f'SC: {sc.name}\nStage: {row["Stage"]}\nOrder: {row["Order"]}')
    stage, _ = SupplyChainStage.objects.get_or_create(
        supply_chain=sc,
        order=row["Order"],
        name=STAGE_NAME_VALUE_LOOKUP[row["Stage"]],
    )

    # print(stage.get_name_display())
    # print(stage.order)
    stage.save()

    return stage


def _update_section(sc: SupplyChain, stage: SupplyChainStage, row: Dict) -> object:
    # print(f'SC: {sc.name}\nStage: {stage}\nSection: {row["Stage-section"]}')

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
    help = "Ingest CSV formatted resilience tool data"

    def add_arguments(self, parser):
        parser.add_argument(
            "stages_file",
            help="CSV formatted file with stage data",
        )

    def handle(self, **options):
        with open(options["stages_file"], "r") as fp:
            reader = csv.DictReader(fp)
            stage_mappings = list(reader)

        print(len(stage_mappings))
        print("\n")

        stage_mappings.sort(key=lambda x: x["Supply Chain"])

        for i, row in enumerate(stage_mappings):
            row["Supply Chain"] = row["Supply Chain"].strip()
            row["Stage"] = row["Stage"].strip()

            try:
                sc = SupplyChain.objects.get(name=row["Supply Chain"])
            except SupplyChain.DoesNotExist:
                print(f'Unknown supply chain : {row["Supply Chain"]}')
                pass
            else:
                print(f'SC: {sc.name}\nStage: {row["Stage"]}\nOrder: {row["Order"]}')
                stage = _update_stage(sc, row)
                section = _update_section(sc, stage, row)

            if i == 100:
                break

        # unique_scs = sorted(set([x["Supply Chain"] for x in stage_mappings]))

        # with open(SC_LIST, "r") as fp:
        #     obj = json.load(fp)
        #     scs = sorted(set(([x["name"] for _, x in obj.items()])))

        # print(set(unique_scs) - set(scs))

        # print(unique_scs)
