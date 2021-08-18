from django.views.generic import FormView
from django.urls import reverse
from django.template.defaultfilters import slugify
from django.shortcuts import get_object_or_404

from accounts.models import GovDepartment
from action_progress.forms import SAPForm
from supply_chains.models import SupplyChain


class ActionProgressView(FormView):
    template_name = "action_progress_base.html"
    form_class = SAPForm

    def get_initial(self):
        """Base implementation of form initialisation"""
        form_value = self.initial.copy()
        dept = self.kwargs.get("dept", None)
        sc_slug = self.kwargs.get("supply_chain_slug", None)

        if dept:
            form_value["department"] = get_object_or_404(GovDepartment, name=dept)

        if sc_slug:
            form_value["supply_chain"] = get_object_or_404(SupplyChain, slug=sc_slug)

        return form_value

    def get_success_url(self):

        form = self.get_form()
        form.is_valid()

        return reverse(
            "action-progress-department",
            kwargs={
                "dept": form.cleaned_data["department"],
            },
        )


class ActionProgressDeptView(ActionProgressView):
    template_name = "action_progress_dept.html"

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()

        if kwargs["initial"]:
            dept_name = kwargs["initial"]["department"]
            if dept_name:
                kwargs["supply_chain_qs"] = SupplyChain.objects.filter(
                    gov_department__name=dept_name
                )

        kwargs["supply_chain_required"] = True
        return kwargs

    def get_success_url(self):

        form = self.get_form()
        form.is_valid()

        return reverse(
            "action-progress-supply-chain",
            kwargs={
                "dept": form.cleaned_data["department"],
                "supply_chain_slug": slugify(form.cleaned_data["supply_chain"]),
            },
        )


class ActionProgressSCView(ActionProgressDeptView):
    template_name = "action_progress_sc.html"
