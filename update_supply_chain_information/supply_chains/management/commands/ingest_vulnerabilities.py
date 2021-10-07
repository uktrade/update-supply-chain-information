import csv
from typing import List, Tuple

from django.core.management.base import BaseCommand
from django.forms.models import ALL_FIELDS

from supply_chains.models import (
    SupplyChain,
    VulnerabilityAssessment,
    VulAssessmentSupplyStage,
    VulAssessmentReceiveStage,
    VulAssessmentMakeStage,
    VulAssessmentStoreStage,
    VulAssessmentDeliverStage,
    NullableRAGRating,
)

EXPECTED_VUL_ROWS_PER_SC = 14
EXPECTED_RAG_ROWS_PER_SC = 5

ALL_FIELDS = list()

for m in [
    VulnerabilityAssessment,
    VulAssessmentSupplyStage,
    VulAssessmentReceiveStage,
    VulAssessmentMakeStage,
    VulAssessmentStoreStage,
    VulAssessmentDeliverStage,
]:
    ALL_FIELDS.extend([f.name for f in m._meta.get_fields()])

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


def _get_sub_model_by_stage(stage: str, vul: VulnerabilityAssessment) -> object:
    stage = stage.lower().strip()
    if stage == "supply":
        obj = VulAssessmentSupplyStage.objects.get(vulnerability=vul)
    elif stage == "receive":
        obj = VulAssessmentReceiveStage.objects.get(vulnerability=vul)
    elif stage == "make":
        obj = VulAssessmentMakeStage.objects.get(vulnerability=vul)
    elif stage == "store":
        obj = VulAssessmentStoreStage.objects.get(vulnerability=vul)
    elif stage == "deliver":
        obj = VulAssessmentDeliverStage.objects.get(vulnerability=vul)
    else:
        raise Exception(
            f"Unknown stage {stage} encountered within supplay chain {vul.supply_chain.name}"
        )

    return obj


def _get_sub_model(char_id: int, vul: VulnerabilityAssessment) -> object:
    if char_id in [1, 2, 3]:
        obj, _ = VulAssessmentSupplyStage.objects.get_or_create(vulnerability=vul)
    elif char_id in [4, 5, 6]:
        obj, _ = VulAssessmentReceiveStage.objects.get_or_create(vulnerability=vul)
    elif char_id in [7, 8, 9, 10]:
        obj, _ = VulAssessmentMakeStage.objects.get_or_create(vulnerability=vul)
    elif char_id in [11, 12, 13]:
        obj, _ = VulAssessmentStoreStage.objects.get_or_create(vulnerability=vul)
    elif char_id == 14:
        obj, _ = VulAssessmentDeliverStage.objects.get_or_create(vulnerability=vul)
    else:
        raise Exception(
            f"Unknown charecterstic_id {char_id} encountered within supplay chain {vul.supply_chain.name}"
        )

    return obj


def _ingest_vul_object(sc_name: SupplyChain, vul_data: List, rag_data: List):
    sc = SupplyChain.objects.get(name=sc_name)

    obj = VulnerabilityAssessment.objects.create(supply_chain=sc)

    for v in vul_data:
        vul_char_id = v["sc_vulnerability_stage"]
        sub_obj = _get_sub_model(int(vul_char_id), obj)

        rag_field, summary_field, rationale_field = _get_vul_attributes(vul_char_id)

        rag_val, summary_val, rationale_val = (
            v["vulnerability_stage_rating"].title(),
            v["vulnerability_stage_summary"],
            v["vulnerability_stage_rationale"],
        )

        setattr(sub_obj, rag_field, _lookup_rag_value(rag_val))
        setattr(sub_obj, summary_field, summary_val)
        setattr(sub_obj, rationale_field, rationale_val)

        sub_obj.save()

    for rag in rag_data:
        stage, val = (
            rag["sc_stage"],
            rag["overall_vulnerability_assessement_rating"].title(),
        )
        sub_obj = _get_sub_model_by_stage(stage, obj)
        setattr(sub_obj, _get_rag_attribute(stage), _lookup_rag_value(val))

        sub_obj.save()

    obj.save()

    return


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
        for _, sc in enumerate(sc_list):
            vul = [x for x in vul_data if x["supply_chain_reporting_name"] == sc]
            rag = [x for x in overall_data if x["supply_chain_reporting_name"] == sc]

            if (
                len(vul) != EXPECTED_VUL_ROWS_PER_SC
                or len(rag) != EXPECTED_RAG_ROWS_PER_SC
            ):
                raise Exception(
                    f"Inconsistent data for {sc} with {len(vul)}(expected {EXPECTED_VUL_ROWS_PER_SC}) rows and {len(rag)}(expected {EXPECTED_RAG_ROWS_PER_SC}) RAG ratings."
                )
            _ingest_vul_object(sc, vul, rag)
            success_count += 1

        self.stdout.write(
            self.style.SUCCESS(
                f"Vulnerability data for {success_count} supply chains ingested into the system\n"
            )
        )
