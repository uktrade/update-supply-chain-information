from datetime import date, timedelta

from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.template import loader
from django.db.models import Count, QuerySet
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

from supply_chains.models import SupplyChain
from supply_chains.utils import (
    get_last_day_of_this_month,
    get_last_working_day_of_a_month,
    get_last_working_day_of_previous_month,
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
