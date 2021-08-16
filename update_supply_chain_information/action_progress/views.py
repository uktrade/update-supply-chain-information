from django.shortcuts import redirect
from django.views.generic import FormView
from django.http import HttpResponse
from django.urls import reverse
from django.template.defaultfilters import slugify

from accounts.models import GovDepartment
from action_progress.forms import SAPForm
from supply_chains.models import SupplyChain


class ActionProgressView(FormView):
    template_name = "action_progress_base.html"
    form_class = SAPForm

    def get_initial(self):
        print("++++++ GET INIT +++++++++")
        form_value = self.initial.copy()
        dept = self.kwargs.get("dept", None)
        sc_slug = self.kwargs.get("supply_chain_slug", None)

        if dept:
            form_value["department"] = GovDepartment.objects.get(name=dept)

        if sc_slug:
            form_value["supply_chain"] = SupplyChain.objects.get(slug=sc_slug)

        return form_value

    def get_form_kwargs(self):
        print("++++++ GET KWARGS +++++++++")
        kwargs = super().get_form_kwargs()

        if kwargs["initial"]:
            dept_name = kwargs["initial"]["department"]
            if dept_name:
                kwargs["supply_chain_qs"] = SupplyChain.objects.filter(
                    gov_department__name=dept_name
                )

        return kwargs

    def get_success_url(self):
        print("++++++ GET SUCCESS URL +++++++++")

        form = self.get_form()
        valid = form.is_valid()
        print(f"Form: {valid}")

        return reverse(
            "action-progress",
            kwargs={
                "dept": form.cleaned_data["department"],
                "supply_chain_slug": slugify(form.cleaned_data["supply_chain"]),
            },
        )

    def post(self, request, dept: str = None):
        print("++++++ POST +++++++++")
        form = self.get_form()
        form_valid = form.is_valid()
        print(f"Form: {form_valid}")

        if not form_valid:
            # Try to read the form's value
            form_dept = request.POST.get("department", None)
            print(f"DEPT: {form_dept}")

        if form_valid:
            return self.form_valid(form)
        elif form_dept:
            return redirect(
                reverse(
                    "action-progress",
                    kwargs={"dept": GovDepartment.objects.get(id=form_dept).name},
                )
            )
        else:
            return self.form_invalid(form)
