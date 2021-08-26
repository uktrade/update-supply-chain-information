from typing import List

from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import FormView
from django.urls import reverse
from django.template.defaultfilters import slugify
from django.shortcuts import get_object_or_404
from django.contrib.auth.mixins import UserPassesTestMixin
from django.views.generic.base import TemplateView

from accounts.models import GovDepartment
from action_progress.forms import SAPForm
from supply_chains.models import StrategicAction, StrategicActionUpdate, SupplyChain
from supply_chains.mixins import PaginationMixin


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
        context["is_admin"] = self.request.user.is_admin

        return context

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()

        # As this class only deal with department filter.
        kwargs["supply_chain_required"] = False
        return kwargs


class ActionProgressDeptView(UserPassesTestMixin, ActionProgressView):
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

    def test_func(self):
        """Custom auth for the resource.

        Note: As UserPassesTestMixin has been used in this base class which over-rides
        LoginRequiredMixin(by the looks of it). Hence condition also include user login.
        """
        claimed_dept = self.kwargs.get("dept", None)
        return self.request.user.is_authenticated and (
            self.request.user.is_admin
            or self.request.user.gov_department.name == claimed_dept
        )

    def get_success_url(self):

        form = self.get_form()
        form.is_valid()

        return reverse(
            "action-progress-list",
            kwargs={
                "dept": form.cleaned_data["department"],
                "supply_chain_slug": slugify(form.cleaned_data["supply_chain"]),
            },
        )


class ActionProgressListView(PaginationMixin, ActionProgressDeptView):
    template_name = "action_progress_list.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        all_actions = StrategicAction.objects.filter(
            supply_chain__slug=context["sc_slug"]
        )
        context["active_actions"] = self.paginate(
            (
                all_actions.filter(is_archived=False)
                .order_by("name")
                .values("name", "description")
            ),
            5,
        )

        context["inactive_actions"] = self.paginate(
            (
                all_actions.filter(is_archived=True)
                .order_by("name")
                .values("name", "description")
            ),
            5,
        )

        context["supply_chain_name"] = SupplyChain.objects.get(slug=context["sc_slug"])
        return context


class ActionProgressDetailView(LoginRequiredMixin, TemplateView):
    template_name = "action_progress_details.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context["dept"] = self.kwargs.get("dept", None)
        context["sc_slug"] = self.kwargs.get("supply_chain_slug", None)
        context["sa_slug"] = self.kwargs.get("action_slug", None)

        context["action"] = StrategicAction.objects.get(
            slug=context["sa_slug"], supply_chain__slug=context["sc_slug"]
        )

        context["update"] = StrategicActionUpdate.objects.filter(
            supply_chain__slug=context["sc_slug"],
            strategic_action__slug=context["sa_slug"],
        ).last_month()

        print(context["update"])
        return context
