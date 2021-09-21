from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import FormView, TemplateView
from django.urls import reverse
from django.shortcuts import get_object_or_404
from django.views.generic import FormView, DetailView

from chain_details.forms import SCDForm
from accounts.models import GovDepartment
from supply_chains.models import SupplyChain
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

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context["dept"] = self.kwargs.get("dept", None)
        context["sc_slug"] = self.kwargs.get("supply_chain_slug", None)

        context["sc"] = get_object_or_404(
            SupplyChain,
            slug=context["sc_slug"],
        )

        return context


class TestSassView(DetailView):
    model = ScenarioAssessment
    template_name = "test-sass-view.html"
    pk_url_kwarg = "sasspk"

    @property
    def scenario_assessments(self):
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
            yield {
                "title": title,
                "rag_rating": getattr(self.object, f"{attr_prefix}_rag_rating"),
                "impact": getattr(self.object, f"{attr_prefix}_impact"),
            }

    def get_context_data(self, **kwargs):
        kwargs = super().get_context_data(**kwargs)
        kwargs["scenario_assessments"] = self.scenario_assessments
        return kwargs
