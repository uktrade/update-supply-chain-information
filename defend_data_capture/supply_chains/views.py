from datetime import date, datetime, timedelta
from typing import List, Dict

from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponse
from django.template import loader
from django.db.models import Count, QuerySet
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.views.generic import TemplateView
from django.shortcuts import redirect

from supply_chains.models import SupplyChain, StrategicAction, StrategicActionUpdate
from supply_chains.utils import (
    get_last_day_of_this_month,
    get_last_working_day_of_a_month,
    get_last_working_day_of_previous_month,
    PageMixin,
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


class SCTaskListView(LoginRequiredMixin, TemplateView, PageMixin):
    template_name = "task_list.html"
    sa_desc_limit = 50
    tasks_per_page = 5
    last_deadline = get_last_working_day_of_previous_month()

    def _get_sa_update_list(self, sa_qset) -> List[Dict]:
        sa_updates = list()

        for sa in sa_qset.iterator():
            update = dict()

            update["description"] = sa.description[: self.sa_desc_limit]

            if len(update["description"]) is self.sa_desc_limit:
                update["description"] += "..."

            sau = StrategicActionUpdate.modified_objects.since(
                self.last_deadline,
                supply_chain=self.supply_chain,
                strategic_action=sa,
            )

            # Note: route property could be replaced with URL of StrategicActionUpdate view
            # method, when its available
            if sau:
                update["status"] = sau[0].status
                update["route"] = f"{self.supply_chain.slug}/{sa.slug}/{sau[0].slug}"
            else:
                update["status"] = StrategicActionUpdate.Status.NOT_STARTED
                update["route"] = f"{self.supply_chain.slug}/{sa.slug}/new"

            sa_updates.append(update)

        return sorted(sa_updates, key=lambda x: x["description"], reverse=True)

    def _extract_view_data(self, *args, **kwargs):
        sc_slug = kwargs.get("sc_slug", "DEFAULT")
        self.supply_chain = SupplyChain.objects.get(slug=sc_slug)

        sa_qset = StrategicAction.objects.filter(supply_chain=self.supply_chain)
        self.total_sa = sa_qset.count()

        self.sa_updates = self._get_sa_update_list(sa_qset)
        print(self.sa_updates)

        self.completed_sa = StrategicActionUpdate.objects.filter(
            supply_chain=self.supply_chain,
            status=StrategicActionUpdate.Status.COMPLETED,
        ).count()

        self.enable_submit = self.total_sa == self.completed_sa and self.completed_sa

        current_submissions = StrategicActionUpdate.modified_objects.since(
            self.last_deadline,
            supply_chain=self.supply_chain,
            status=StrategicActionUpdate.Status.SUBMITTED,
        ).count()

        self.update_complete = self.total_sa == current_submissions

        if self.update_complete:
            self.update_message = "Update Complete"

            # TODO : Would it affect below post handling.. ?
            # To keep the template code light, (re)set completed actions with total actions
            self.completed_sa = self.total_sa
        else:
            self.update_message = "Update Incomplete"

    def dispatch(self, request, *args, **kwargs):
        self._extract_view_data(*args, **kwargs)
        self.sa_updates = self.paginate(self.sa_updates, self.tasks_per_page)

        return super().dispatch(request, *args, **kwargs)

    def post(self, *args, **kwargs):
        print("POST")
        print(f"Total : {self.total_sa}")

        print()
        if self.total_sa == self.completed_sa:
            self.supply_chain.last_submission_date = date.today()
            self.supply_chain.save()

            updates = StrategicActionUpdate.modified_objects.since(
                self.last_deadline,
                supply_chain=self.supply_chain,
                status=StrategicActionUpdate.Status.COMPLETED,
            )

            for update in updates.iterator():
                update.submission_date = date.today()
                update.status = StrategicActionUpdate.Status.SUBMITTED
                update.save()

            return redirect("tcomplete", sc_slug=self.supply_chain.name)


class SCCompleteView(LoginRequiredMixin, TemplateView):
    template_name = "task_complete.html"

    def dispatch(self, request, *args, **kwargs):
        sc_slug = kwargs.get("sc_slug", "DEFAULT")
        self.supply_chain = SupplyChain.objects.get(slug=sc_slug)

        supply_chains = self.request.user.gov_department.supply_chains.order_by("name")

        self.sum_of_supply_chains = supply_chains.count()

        last_deadline = get_last_working_day_of_previous_month()
        self.num_updated_supply_chains = supply_chains.submitted_since(
            last_deadline
        ).count()

        return super().dispatch(request, *args, **kwargs)
