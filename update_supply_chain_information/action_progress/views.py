from typing import List

from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import FormView
from django.urls import reverse
from django.template.defaultfilters import slugify
from django.shortcuts import get_object_or_404, redirect, render

from accounts.models import GovDepartment
from action_progress.forms import SAPForm
from supply_chains.models import SupplyChain
from supply_chains.templatetags.supply_chain_tags import get_action_progress_route


class ActionProgressView(LoginRequiredMixin, FormView):
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

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context["dept"] = self.kwargs.get("dept", None)
        context["sc_slug"] = self.kwargs.get("supply_chain_slug", None)

        return context

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()

        # As this class only deal with department filter.
        kwargs["supply_chain_required"] = False
        return kwargs

    # def post(self, request, *args, **kwargs):
    #     print('++++++++ POST +++++++')
    #     form = self.get_form()
    #     form.is_valid()
    #     print(f'Form DEPT: { form.cleaned_data["department"]}')
    #     print(f'Validity: { form.is_valid()}')
    #     if form.is_valid():

    #         return self.form_valid(form)
    #     else:
    #         print(form.errors)
    #         return self.form_invalid(form)


class ActionProgressDeptView(ActionProgressView):
    template_name = "action_progress_dept.html"

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()

        # With form having 2 post routes, chosen supply chain would come through but not department.
        # To validate the form, inject department from url.
        if "data" in kwargs:
            dept_id = str(
                GovDepartment.objects.get(name=self.kwargs.get("dept", None)).id
            )
            d = {"department": dept_id}
            d.update(kwargs["data"])
            if isinstance(d["supply_chain"], List):
                d["supply_chain"] = d["supply_chain"][0]

            kwargs["data"] = d

        # Pull those supply chains from chosen department
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

    def get(self, request, *args, **kwargs):
        # Validate the department, if non-admin user manually forcing entry into other departments
        if not request.user.is_admin:
            actual_dept = request.user.gov_department.name

            if self.kwargs["dept"] != actual_dept:
                return redirect(get_action_progress_route(request.user))
            else:
                return render(
                    request, self.template_name, context=self.get_context_data()
                )

    # def post(self, request, *args, **kwargs):
    #     print('++++++++ POST +++++++')
    #     form = self.get_form()
    #     form.is_valid()
    #     # print(f'Form DEPT: { form.cleaned_data["department"]}')
    #     # print(f'Form SC: { form.cleaned_data["supply_chain"]}')
    #     print(f'Validity: { form.is_valid()}')
    #     if form.is_valid():

    #         return self.form_valid(form)
    #     else:
    #         print(form.errors)
    #         return self.form_invalid(form)


class ActionProgressSCView(ActionProgressDeptView):
    template_name = "action_progress_sc.html"
