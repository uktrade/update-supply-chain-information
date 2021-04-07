from datetime import date, datetime, timedelta
from typing import List, Dict

from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponse
from django.template import loader
from django.db.models import Count, QuerySet
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.views.generic import TemplateView
from django.shortcuts import redirect, render
from django.urls import reverse
from django.views import View
from django.views.generic import ListView, UpdateView, CreateView

from supply_chains.models import SupplyChain, StrategicAction, StrategicActionUpdate
from accounts.models import User, GovDepartment
from supply_chains.utils import (
    get_last_day_of_this_month,
    get_last_working_day_of_a_month,
    get_last_working_day_of_previous_month,
    PaginationMixin,
    GovDepPermissionMixin,
)


@login_required
def index(request):
    supply_chains = request.user.gov_department.supply_chains.order_by("name")
    all_supply_chains = supply_chains.annotate(
        strategic_action_count=Count("strategic_actions")
    )

    deadline = get_last_working_day_of_a_month(get_last_day_of_this_month())
    last_deadline = get_last_working_day_of_previous_month()

    num_updated_supply_chains = all_supply_chains.submitted_since(last_deadline).count()

    page = request.GET.get("page", 1)
    paginator = Paginator(all_supply_chains, 5)

    try:
        supply_chains = paginator.page(page)
    except PageNotAnInteger:
        supply_chains = paginator.page(1)
    except EmptyPage:
        supply_chains = paginator.page(paginator.num_pages)

    template = loader.get_template("index.html")

    context = {
        "supply_chains": supply_chains,
        "gov_department_name": request.user.gov_department.name,
        "deadline": deadline,
        "num_updated_supply_chains": num_updated_supply_chains,
        "update_complete": num_updated_supply_chains == all_supply_chains.count(),
    }
    return HttpResponse(template.render(context, request))


class SCTaskListView(LoginRequiredMixin, TemplateView, PaginationMixin):
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
        self.supply_chain = SupplyChain.objects.get(slug=sc_slug)

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

        self.total_sa == self.completed_updates and self.completed_updates != 0

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


class SCCompleteView(LoginRequiredMixin, TemplateView):
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
        self.supply_chain = SupplyChain.objects.filter(slug=sc_slug)[0]

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
    model = models.StrategicAction
    template_name = 'supply_chains/temp-sa-list.html'
    context_object_name = 'strategic_actions'


class MonthlyUpdateMixin:
    def get_strategic_action(self, strategic_action_id):
        return models.StrategicAction.objects.get(id=strategic_action_id)

    def get_success_url(self):
        # TODO: decide which the next page is according to current state of affairs
        url_kwargs = {
            'id': self.object.id,
            'strategic_action_id': self.object.strategic_action.id
        }
        return reverse('monthly-update-status-edit', kwargs=url_kwargs)


class MonthlyUpdateInfoCreateView(MonthlyUpdateMixin, CreateView):
    model = models.StrategicActionUpdate
    pk_url_kwarg = 'id'
    template_name = 'supply_chains/temp_mu_info_form.html'
    form_class = forms.MonthlyUpdateInfoForm
    context_object_name = 'strategic_action_update'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['strategic_action'] = self.get_strategic_action(self.kwargs['strategic_action_id'])
        return context

    def form_valid(self, form):
        strategic_action = self.get_strategic_action(self.kwargs['strategic_action_id'])
        form.instance.strategic_action = strategic_action
        form.instance.supply_chain = strategic_action.supply_chain
        return super().form_valid(form)


class MonthlyUpdateInfoEditView(MonthlyUpdateMixin, UpdateView):
    model = models.StrategicActionUpdate
    pk_url_kwarg = 'id'
    template_name = 'supply_chains/temp_mu_info_form.html'
    form_class = forms.MonthlyUpdateInfoForm
    context_object_name = 'strategic_action_update'


class MonthlyUpdateStatusEditView(MonthlyUpdateMixin, UpdateView):
    model = models.StrategicActionUpdate
    pk_url_kwarg = 'id'
    template_name = 'supply_chains/temp_mu_status_form.html'
    form_class = forms.MonthlyUpdateInfoForm
    context_object_name = 'strategic_action_update'




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
