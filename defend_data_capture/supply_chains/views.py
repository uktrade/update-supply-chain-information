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

    def _get_sa_update_list(self, sa_qset) -> List[Dict]:
        sa_updates = list()

        for sa in sa_qset.iterator():
            update = dict()

            update["description"] = sa.description[: self.sa_desc_limit]

            if len(update["description"]) is self.sa_desc_limit:
                update["description"] += "..."

            sau = StrategicActionUpdate.objects.filter(
                supply_chain__name=self.sc_name,
                strategic_action__id=sa.id,
                date_created__gt=datetime(2019, 3, 31),
            )

            if sau:
                update["status"] = sau[0].status
            else:
                update["status"] = StrategicActionUpdate.Status.NOT_STARTED

            sa_updates.append(update)

        return sorted(sa_updates, key=lambda x: x["description"], reverse=True)

    def _extract_view_data(self, *args, **kwargs):
        self.sc_name = kwargs.get("chain", "DEFAULT")

        sa_qset = StrategicAction.objects.filter(supply_chain__name=self.sc_name)
        self.total_sa = sa_qset.count()

        self.sa_updates = self._get_sa_update_list(sa_qset)

        self.completed_sa = StrategicActionUpdate.objects.filter(
            supply_chain__name=self.sc_name,
            status=StrategicActionUpdate.Status.COMPLETED,
        ).count()

        self.enable_submit = self.total_sa == self.completed_sa

    def dispatch(self, request, *args, **kwargs):
        print("DISPATCH")
        self._extract_view_data(*args, **kwargs)
        self.sa_updates = self.paginate(self.sa_updates, self.tasks_per_page)

        return super().dispatch(request, *args, **kwargs)

    def post(self, *args, **kwargs):
        print("POST")
        print(f"Total : {self.total_sa}")

        print()
        if self.total_sa == self.completed_sa:
            sc = SupplyChain.objects.get(name=self.sc_name)
            sc.last_submission_date = date.today()
            sc.save()

            sau = StrategicActionUpdate.objects.get(
                supply_chain=sc,
                status=StrategicActionUpdate.Status.COMPLETED,
            )  # Include since condition

            sau.submission_date = date.today()
            sau.status = StrategicActionUpdate.Status.SUBMITTED
            sau.save()

            print("Post processing done!")
            # return HttpResponse('Done')
            return redirect("tcomplete", chain=self.sc_name)


class SCCompleteView(LoginRequiredMixin, TemplateView):
    template_name = "task_complete.html"

    def dispatch(self, request, *args, **kwargs):
        self.sc_name = kwargs.get("chain", None)

        return super().dispatch(request, *args, **kwargs)
