from collections import defaultdict

from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import FormView, TemplateView
from django.urls import reverse
from django.shortcuts import get_object_or_404
from django.views.generic import FormView, DetailView

from chain_details.forms import SCDForm
from accounts.models import GovDepartment
from supply_chains.models import SupplyChain, SupplyChainStage
from supply_chains.mixins import PaginationMixin
from supply_chains.models import ScenarioAssessment


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

        return context
