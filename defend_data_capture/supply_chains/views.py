from datetime import date
from typing import List, Dict

from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponse
from django.template import loader
from django.db.models import Count
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.views.generic import ListView, TemplateView
from django.shortcuts import redirect, render
from django.urls import reverse
from django.views.generic import (
    ListView,
    UpdateView,
    CreateView,
    TemplateView,
)

from supply_chains.models import (
    SupplyChain,
    StrategicAction,
    StrategicActionUpdate,
    RAGRating,
)
from supply_chains import forms

from supply_chains.utils import (
    get_last_day_of_this_month,
    get_last_working_day_of_a_month,
    get_last_working_day_of_previous_month,
    PaginationMixin,
    GovDepPermissionMixin,
)


class HomePageView(LoginRequiredMixin, PaginationMixin, ListView):
    model = SupplyChain
    context_object_name = "supply_chains"
    template_name = "index.html"

    def get_queryset(self):
        return self.request.user.gov_department.supply_chains.annotate(
            strategic_action_count=Count("strategic_actions")
        ).order_by("name")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        last_deadline = get_last_working_day_of_previous_month()

        context["supply_chains"] = self.paginate(self.object_list, 5)
        context["deadline"] = get_last_working_day_of_a_month(
            get_last_day_of_this_month()
        )
        context["num_updated_supply_chains"] = self.object_list.submitted_since(
            last_deadline
        ).count()
        context["gov_department_name"] = self.request.user.gov_department.name
        context["update_complete"] = (
            context["num_updated_supply_chains"] == self.object_list.count()
        )

        return context


    context = {
        "supply_chains": supply_chains,
        "gov_department_name": request.user.gov_department.name,
        "deadline": deadline,
        "num_updated_supply_chains": num_updated_supply_chains,
        "update_complete": num_updated_supply_chains == all_supply_chains.count(),
    }
    return HttpResponse(template.render(context, request))



class SCTaskListView(
    LoginRequiredMixin, GovDepPermissionMixin, PaginationMixin, TemplateView
):
    template_name = "task_list.html"
    tasks_per_page = 5
    last_deadline = get_last_working_day_of_previous_month()

    def _sort_updates(self, updates: List) -> List:
        SORT_ORDER = {
            "Not started": 0,
            "In progress": 1,
            "Completed": 2,
            "Submitted": 3,
        }

        updates.sort(key=lambda val: SORT_ORDER[val["status"].label])

        return updates

    def _get_sa_update_list(self, sa_qset) -> List[Dict]:
        sa_updates = list()

        for sa in sa_qset.iterator():
            update = dict()

            update["name"] = sa.name
            update["description"] = sa.description

            sau = StrategicActionUpdate.objects.since(
                self.last_deadline,
                supply_chain=self.supply_chain,
                strategic_action=sa,
            )

            # Note: route property could be replaced with URL of StrategicActionUpdate view
            # method, when its available
            if sau:
                update["status"] = StrategicActionUpdate.Status(sau[0].status)
                update["route"] = f"{self.supply_chain.slug}/{sa.slug}/{sau[0].slug}"
            else:
                update["status"] = StrategicActionUpdate.Status.NOT_STARTED
                update["route"] = f"{self.supply_chain.slug}/{sa.slug}/new"

            sa_updates.append(update)

        return self._sort_updates(sa_updates)

    def _extract_view_data(self, *args, **kwargs):
        sc_slug = kwargs.get("sc_slug", "DEFAULT")
        self.supply_chain = SupplyChain.objects.get(slug=sc_slug, is_archived=False)

        sa_qset = StrategicAction.objects.filter(supply_chain=self.supply_chain)
        self.total_sa = sa_qset.count()

        self.sa_updates = self._get_sa_update_list(sa_qset)

        self.completed_updates = StrategicActionUpdate.objects.since(
            self.last_deadline,
            supply_chain=self.supply_chain,
            status__in=[
                StrategicActionUpdate.Status.COMPLETED,
                StrategicActionUpdate.Status.SUBMITTED,
            ],
        ).count()

        self.submitted_only_updates = StrategicActionUpdate.objects.since(
            self.last_deadline,
            supply_chain=self.supply_chain,
            status=StrategicActionUpdate.Status.SUBMITTED,
        ).count()

        self.update_complete = (
            self.total_sa == self.completed_updates and self.total_sa != 0
        )
        self.update_submitted = (
            self.total_sa == self.submitted_only_updates and self.total_sa != 0
        )

    def dispatch(self, *args, **kwargs):
        self._extract_view_data(*args, **kwargs)
        self.sa_updates = self.paginate(self.sa_updates, self.tasks_per_page)

        return super().dispatch(*args, **kwargs)

    def post(self, *args, **kwargs):
        if self.total_sa == self.completed_updates and self.total_sa:
            self.supply_chain.last_submission_date = date.today()
            self.supply_chain.save()

            updates = StrategicActionUpdate.objects.since(
                self.last_deadline,
                supply_chain=self.supply_chain,
                status=StrategicActionUpdate.Status.COMPLETED,
            )

            for update in updates.iterator():
                update.submission_date = date.today()
                update.status = StrategicActionUpdate.Status.SUBMITTED
                update.save()

            return redirect("update_complete", sc_slug=self.supply_chain.slug)
        else:
            self.submit_error = True
            kwargs.setdefault("view", self)
            return render(self.request, self.template_name, context=kwargs)


class SCCompleteView(LoginRequiredMixin, GovDepPermissionMixin, TemplateView):
    template_name = "task_complete.html"

    def _validate(self) -> bool:
        total_sa = StrategicAction.objects.filter(
            supply_chain=self.supply_chain
        ).count()
        submitted = StrategicActionUpdate.objects.since(
            self.last_deadline,
            supply_chain=self.supply_chain,
            status=StrategicActionUpdate.Status.SUBMITTED,
        ).count()

        return total_sa == submitted

    def get(self, request, *args, **kwargs):
        sc_slug = kwargs.get("sc_slug", "DEFAULT")
        self.last_deadline = get_last_working_day_of_previous_month()
        self.supply_chain = SupplyChain.objects.filter(slug=sc_slug, is_archived=False)[
            0
        ]

        # This is to gaurd manual access if not actually complete, help them to complete
        if not self._validate():
            return redirect("tlist", sc_slug=self.supply_chain.slug)

        supply_chains = request.user.gov_department.supply_chains.order_by("name")

        self.sum_of_supply_chains = supply_chains.count()

        self.num_updated_supply_chains = supply_chains.submitted_since(
            self.last_deadline
        ).count()

        kwargs.setdefault("view", self)
        return render(request, self.template_name, context=kwargs)


# @login_required
# class MonthlyUpdate
class StrategicActionListView(ListView):
    model = StrategicAction
    template_name = "supply_chains/temp-sa-list.html"
    context_object_name = "strategic_actions"


class MonthlyUpdateMixin:
    model = StrategicActionUpdate
    context_object_name = "strategic_action_update"
    pk_url_kwarg = "id"

    def get_strategic_action(self, strategic_action_id):
        return StrategicAction.objects.get(id=strategic_action_id)

    def get_success_url(self):
        # This method needs to be implemented by the pages
        # so as to express their rules for what the "next" page is
        raise NotImplementedError(
            f"get_success_url() not implemented by {self.__class__}"
        )

    def get_navigation_links(self):
        return []


class MonthlyUpdateInfoCreateView(MonthlyUpdateMixin, CreateView):
    template_name = "supply_chains/monthly-update-info-form.html"
    form_class = forms.MonthlyUpdateInfoForm

    def get(self, request, *args, **kwargs):
        last_deadline = get_last_working_day_of_previous_month()
        strategic_action: StrategicAction = self.get_strategic_action(
            kwargs["strategic_action_id"]
        )
        current_month_updates = strategic_action.monthly_updates.since(last_deadline)
        if current_month_updates.exists():
            current_month_update: StrategicActionUpdate = (
                current_month_updates.order_by("date_created").last()
            )
        else:
            current_month_update: StrategicActionUpdate = (
                strategic_action.monthly_updates.create(
                    status=StrategicActionUpdate.Status.IN_PROGRESS,
                    supply_chain=strategic_action.supply_chain,
                )
            )
        update_url = reverse(
            "monthly-update-info-edit",
            kwargs={
                "strategic_action_id": current_month_update.strategic_action.pk,
                "id": current_month_update.id,
            },
        )
        return redirect(update_url)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["strategic_action"] = self.get_strategic_action(
            self.kwargs["strategic_action_id"]
        )
        return context

    def form_valid(self, form):
        strategic_action = self.get_strategic_action(self.kwargs["strategic_action_id"])
        form.instance.strategic_action = strategic_action
        form.instance.supply_chain = strategic_action.supply_chain
        return super().form_valid(form)

    # def get_success_url(self):
    #     return super().get_success_url()
    #


class MonthlyUpdateInfoEditView(MonthlyUpdateMixin, UpdateView):
    template_name = "supply_chains/monthly-update-info-form.html"
    form_class = forms.MonthlyUpdateInfoForm

    def get_success_url(self):
        if self.object.strategic_action.target_completion_date is None:
            next_page_url = "monthly-update-timing-edit"
        else:
            next_page_url = "monthly-update-status-edit"
        url_kwargs = {
            "id": self.object.id,
            "strategic_action_id": self.object.strategic_action.id,
        }
        return reverse(next_page_url, kwargs=url_kwargs)


class MonthlyUpdateStatusEditView(MonthlyUpdateMixin, UpdateView):
    template_name = "supply_chains/monthly-update-status-form.html"
    form_class = forms.MonthlyUpdateStatusForm

    completion_date_change_form = None

    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)

    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        if "RED-will_completion_date_change" in self.request.POST:
            self.completion_date_change_form = form.fields[
                "implementation_rag_rating"
            ].widget.details["RED"]["form"]
        return form

    def get_form_kwargs(self):
        form_kwargs = super().get_form_kwargs()
        return form_kwargs

    def form_valid(self, form):
        return super().form_valid(form)

    def get_success_url(self):
        next_page_url = "monthly-update-summary"
        if self.completion_date_change_form:
            if self.completion_date_change_form.is_valid():
                if (
                    self.completion_date_change_form.cleaned_data[
                        "will_completion_date_change"
                    ]
                    == "True"
                ):
                    next_page_url = "monthly-update-revised-timing-edit"
        url_kwargs = {
            "id": self.object.id,
            "strategic_action_id": self.object.strategic_action.id,
        }
        return reverse(next_page_url, kwargs=url_kwargs)


class MonthlyUpdateTimingEditView(MonthlyUpdateMixin, UpdateView):
    template_name = "supply_chains/monthly-update-timing-form.html"
    form_class = forms.MonthlyUpdateTimingForm

    def get_object(self, queryset=None):
        return super().get_object(queryset)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        instance = kwargs.get("instance", None)
        if instance is not None:
            kwargs["instance"] = instance.strategic_action
        return kwargs

    def form_valid(self, form):
        # The superclass form_valid will overwrite our object as it's saving to a StrategicAction
        # and in a superclass higher up, it calls get_success_url
        # so save it
        self.original_object = self.object
        response = super().form_valid(form)
        # then restore it
        self.object = self.original_object
        return response

    def form_invalid(self, form):
        return super().form_invalid(form)

    def get_success_url(self):
        next_page_url = "monthly-update-status-edit"
        url_kwargs = {
            "id": self.object.id,
            "strategic_action_id": self.object.strategic_action.id,
        }
        return reverse(next_page_url, kwargs=url_kwargs)


class MonthlyUpdateRevisedTimingEditView(MonthlyUpdateTimingEditView):
    template_name = "supply_chains/monthly-update-revised-timing-form.html"
    form_class = forms.MonthlyUpdateModifiedTimingForm

    def get_success_url(self):
        next_page_url = "monthly-update-summary"
        # see form_valid() for an explanation of original_object
        url_kwargs = {
            "id": self.object.id,
            "strategic_action_id": self.object.strategic_action.id,
        }
        return reverse(next_page_url, kwargs=url_kwargs)


class MonthlyUpdateSummaryView(MonthlyUpdateMixin, UpdateView):
    template_name = "supply_chains/monthly-update-summary.html"
    fields = []

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["has_revised_date_of_completion"] = bool(
            all(
                [
                    self.object.strategic_action.target_completion_date,
                    not (self.object.strategic_action.is_ongoing),
                    self.object.changed_target_completion_date,
                ]
            )
        )
        context["has_date_of_completion"] = bool(
            all(
                [
                    self.object.strategic_action.target_completion_date,
                    not (self.object.strategic_action.is_ongoing),
                ]
            )
        )
        return context

    def post(self, request, *args, **kwargs):
        """
        To finalise the update we must:
        1. Copy a revised target completion date to the strategic action, or copy is ongoing and clear the SA's date;
        2. If there is a revised target completion date, record the change in reversion;
        3. Change the update's status to "Completed"
        """
        return super().post(request, *args, **kwargs)


class SASummaryView(
    LoginRequiredMixin, GovDepPermissionMixin, PaginationMixin, TemplateView
):
    template_name = "strategic_action_summary.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        supply_chain = SupplyChain.objects.get(slug=kwargs.get("sc_slug"))

        context["strategic_actions"] = self.paginate(
            supply_chain.strategic_actions.filter(is_archived=False).order_by("name"),
            5,
        )
        context["supply_chain"] = supply_chain
        return context


class SCSummary(LoginRequiredMixin, GovDepPermissionMixin, TemplateView):
    template_name = "sc_summary.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        sc_slug = kwargs.get("sc_slug", "DEFAULT")

        context["supply_chain"] = SupplyChain.objects.filter(
            slug=sc_slug, is_archived=False
        )[0]
        return context
