import csv
from typing import List, Tuple

from django.core.management.base import BaseCommand
from django.forms.models import ALL_FIELDS

from supply_chains.models import (
    SupplyChain,
    VulnerabilityAssessment,
    NullableRAGRating,
)

EXPECTED_VUL_ROWS_PER_SC = 14
EXPECTED_RAG_ROWS_PER_SC = 5
ALL_FIELDS = [f.name for f in VulnerabilityAssessment._meta.get_fields()]

RAG_VALUE_LOOKUP = {item[1]: item[0] for item in NullableRAGRating.choices}


def _lookup_rag_value(label: str) -> str:
    try:
        value = RAG_VALUE_LOOKUP[label]
    except KeyError:
        if label.title() == "None":
            value = NullableRAGRating.NONE

    return value


def _get_vul_attributes(index: int) -> Tuple:
    matched_fields = [x for x in ALL_FIELDS if x.endswith(f"_{index}")]

    return matched_fields


def _get_rag_attribute(stage: str) -> str:
    return f"{stage.lower()}_stage_rag_rating"


def _create_vul_object(sc_name: SupplyChain, vul_data: List, rag_data: List) -> object:
    sc = SupplyChain.objects.get(name=sc_name)

    obj = VulnerabilityAssessment(supply_chain=sc)

    for v in vul_data:
        vul_char_id = v["sc_vulnerability_stage"]

        rag_field, summary_field, rationale_field = _get_vul_attributes(vul_char_id)

        rag_val, summary_val, rationale_val = (
            v["vulnerability_stage_rating"].title(),
            v["vulnerability_stage_summary"],
            v["vulnerability_stage_rationale"],
        )

        setattr(obj, rag_field, _lookup_rag_value(rag_val))
        setattr(obj, summary_field, summary_val)
        setattr(obj, rationale_field, rationale_val)

    for rag in rag_data:
        stage, val = (
            rag["sc_stage"],
            rag["overall_vulnerability_assessement_rating"].title(),
        )
        setattr(obj, _get_rag_attribute(stage), _lookup_rag_value(val))

    return obj


class Command(BaseCommand):
    help = "Ingest CSV formatted resilience tool vulnerabilities data"

    def add_arguments(self, parser):
        parser.add_argument(
            "vulnerabilities_file",
            help="CSV formatted file with data",
        )
        parser.add_argument(
            "overall_rags",
            help="CSV formatted file with overall stage RAG data",
        )

    def handle(self, **options):
        with open(options["vulnerabilities_file"], "r") as fp:
            reader = csv.DictReader(fp)
            vul_data = list(reader)

        with open(options["overall_rags"], "r") as fp:
            reader = csv.DictReader(fp)
            overall_data = list(reader)

        vul_data.sort(key=lambda x: x["supply_chain_reporting_name"])
        overall_data.sort(key=lambda x: x["supply_chain_reporting_name"])

        sc_from_vul_data = set([x["supply_chain_reporting_name"] for x in vul_data])
        sc_from_overall_data = set(
            [x["supply_chain_reporting_name"] for x in overall_data]
        )

        if len(sc_from_vul_data.difference(sc_from_overall_data)) != 0:
            raise Exception("Data(supply chains) doesn't match within files provided")
        else:
            sc_list = sorted(sc_from_vul_data)

        self.stdout.write(
            self.style.HTTP_INFO(
                f"\nIngesting {len(vul_data)} rows for {len(sc_list)} supply chains\n"
            )
        )

        success_count = 0
        for sc in sc_list:
            vul = [x for x in vul_data if x["supply_chain_reporting_name"] == sc]
            rag = [x for x in overall_data if x["supply_chain_reporting_name"] == sc]

            if (
                len(vul) != EXPECTED_VUL_ROWS_PER_SC
                or len(rag) != EXPECTED_RAG_ROWS_PER_SC
            ):
                raise Exception(
                    f"Inconsistent data for {sc} with {len(vul)}(expected {EXPECTED_VUL_ROWS_PER_SC}) rows and {len(rag)}(expected {EXPECTED_RAG_ROWS_PER_SC}) RAG ratings."
                )
            vul_object = _create_vul_object(sc, vul, rag)
            vul_object.save()
            success_count += 1

        self.stdout.write(
            self.style.SUCCESS(
                f"Vulnerability data for {success_count} supply chains ingested into the system\n"
            )
        )
