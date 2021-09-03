from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import FormView
from django.urls import reverse
from django.shortcuts import get_object_or_404

from chain_details.forms import SCDForm
from accounts.models import GovDepartment
from supply_chains.models import SupplyChain
from supply_chains.mixins import PaginationMixin


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
            .values("name", "slug"),
            5,
        )

        return context
