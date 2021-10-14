from collections import defaultdict

from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import FormView, TemplateView
from django.urls import reverse
from django.shortcuts import get_object_or_404
from django.views.generic import FormView, DetailView

from chain_details.forms import SCDForm
from accounts.models import GovDepartment
from supply_chains.mixins import PaginationMixin
from supply_chains.models import (
    ScenarioAssessment,
    SupplyChain,
    SupplyChainStage,
    CRITICALITY_RATING,
)


class ChainDetailsView(LoginRequiredMixin, FormView):
    template_name = "chain_details_base.html"
    form_class = SCDForm

    def get_success_url(self):

        form = self.get_form()
        form.is_valid()

        return reverse(
            "chain-details-list",
            kwargs={
                "dept": form.cleaned_data["department"],
            },
        )


class ChainDetailsListView(PaginationMixin, ChainDetailsView):
    template_name = "chain_details_list.html"

    def get_initial(self):
        form_value = self.initial.copy()
        dept = self.kwargs.get("dept", None)

        if dept:
            form_value["department"] = get_object_or_404(GovDepartment, name=dept)

        return form_value

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context["dept"] = self.kwargs.get("dept", None)
        context["chains"] = self.paginate(
            SupplyChain.objects.filter(gov_department__name=context["dept"])
            .order_by("name")
            .values("name", "slug", "description"),
            5,
        )

        return context


class ChainDetailsInfoView(LoginRequiredMixin, TemplateView):
    template_name = "chain_details_info.html"
    VUL_STAGE_TITLES = [
        None,
        "Dependence on foreign suppliers for product",
        "Ability to source alternative products",
        "Resilience of supply base",
        "Reliance on long shipping lead times",
        "Susceptibility to port congestion",
        "Size of product stockpile held in UK",
        "Ability to substitute planned replacement",
        "Dependence on foreign contractors",
        "Ability to ramp up UK production capacity",
        "Susceptibility to labour shortage",
        "Size of stock buffer held in UK",
        "Feasibility of stockpiling",
        "Availability of storage in UK",
        "Ability to ramp up UK delivery capacity",
    ]

    def scenario_assessment_sections(self, scenario_assessment: ScenarioAssessment):
        sections = []
        for title, attr_prefix in (
            (
                "Borders closed",
                "borders_closed",
            ),
            (
                "Storage full",
                "storage_full",
            ),
            (
                "Ports blocked",
                "ports_blocked",
            ),
            (
                "Raw material shortage",
                "raw_material_shortage",
            ),
            (
                "Labour shortage",
                "labour_shortage",
            ),
            (
                "Demand spike",
                "demand_spike",
            ),
        ):
            rag_rating = getattr(scenario_assessment, f"{attr_prefix}_rag_rating")
            sections.append(
                {
                    "title": title,
                    "rag_rating": rag_rating,
                    "impact": getattr(scenario_assessment, f"{attr_prefix}_impact"),
                }
            )
        return sections

    def critical_scenario_paragraphs(self, scenario_assessment: ScenarioAssessment):
        is_critical_field_names = [
            field.name
            for field in scenario_assessment._meta.fields
            if field.name.endswith("_is_critical")
        ]

        critical_scenarios = defaultdict(list)
        for field_name in is_critical_field_names:
            if getattr(scenario_assessment, field_name):
                field_prefix = field_name.replace("_is_critical", "")
                critical_scenario_field_name = f"{field_prefix}_critical_scenario"
                critical_scenarios[
                    getattr(scenario_assessment, critical_scenario_field_name)
                ].append(field_prefix)

        critical_scenario_paragraphs = []
        for scenario, field_prefixes in critical_scenarios.items():
            fields = [
                field_prefix.replace("_", " ").capitalize()
                for field_prefix in field_prefixes
            ]
            field_text = " / ".join(fields)
            critical_scenario_paragraphs.append(f"{field_text}: {scenario}")
        return critical_scenario_paragraphs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context["dept"] = self.kwargs.get("dept", None)
        context["sc_slug"] = self.kwargs.get("supply_chain_slug", None)

        supply_chain = get_object_or_404(
            SupplyChain,
            slug=context["sc_slug"],
        )

        context["sc"] = supply_chain
        if hasattr(supply_chain, "scenario_assessment"):
            context["scenario_assessment_sections"] = self.scenario_assessment_sections(
                supply_chain.scenario_assessment
            )
            context["critical_scenario_paragraphs"] = self.critical_scenario_paragraphs(
                supply_chain.scenario_assessment
            )
        context["stages"] = SupplyChainStage.objects.filter(
            supply_chain=context["sc"]
        ).order_by("order")
        context["stage_notes"] = context["stages"].order_by("-gsc_updated_on").first()

        if hasattr(supply_chain, "vulnerability_assessment"):
            vul = supply_chain.vulnerability_assessment
            context["vul"] = vul
            context["vul_supply"] = vul.vulnerability_supply_stage
            context["vul_receive"] = vul.vulnerability_receive_stage
            context["vul_make"] = vul.vulnerability_make_stage
            context["vul_store"] = vul.vulnerability_store_stage
            context["vul_deliver"] = vul.vulnerability_deliver_stage

            context["vul_title_list"] = self.VUL_STAGE_TITLES

        context["criticality_rating_types"] = CRITICALITY_RATING
        context["criticality_rating_details"] = {
            CRITICALITY_RATING[0]: {
                "human_health": "Limited risk of loss of life or damage to health (<10 casualties)",
                "national_security": "Limited threat to national security, defence or functioning of the UK",
                "economic": "Limited impact on UK economy (£millions) and/or net zero goal",
                "essential_services": "Limited impact ability to deliver essential services",
            },
            CRITICALITY_RATING[1]: {
                "human_health": "Minor risk of loss of life or damage to health (recoverable in the short term) (10-50 casualties)",
                "national_security": "Minor threat to national security, defence or functioning of the UK",
                "economic": "Minor impact on UK economy (£10s of millions) and/or net zero goals",
                "essential_services": "Minor impact on ability to deliver essential services",
            },
            CRITICALITY_RATING[2]: {
                "human_health": "Moderate risk to loss of life or damage to health (50-100 casualties)",
                "national_security": "Moderate threat to national security, defence or functioning of the UK",
                "economic": "Moderate impact on UK economy (£100s of millions) and/or net zero goals ",
                "essential_services": "Moderate impact on ability to deliver essential services",
            },
            CRITICALITY_RATING[3]: {
                "human_health": "Significant risk to loss of life or serious damage to health (100s casualties)",
                "national_security": "Significant threat to national security, defence or functioning of the UK",
                "economic": "Significant impact on UK economy (£billions) and/or net zero goals",
                "essential_services": "Significant impact on ability to deliver essential services ",
            },
            CRITICALITY_RATING[4]: {
                "human_health": "Catastrophic risk to loss of life or permanent serious damage to health (1000s casualties)",
                "national_security": "Catastrophic threat to national security, defence or functioning of the UK ",
                "economic": "Catastrophic impact on UK economy (£10s of billions) and/or net zero goals ",
                "essential_services": "Catastrophic impact on ability to deliver essential services ",
            },
        }

        return context
