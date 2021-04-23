import calendar
from datetime import date, datetime, timedelta

import holidays
from django.core.exceptions import PermissionDenied
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

from accounts.models import User
from supply_chains.models import SupplyChain


def get_last_working_day_of_a_month(last_day_of_month: date) -> date:
    """
    When provided with a date object representing the last day of a month,
    this function will return the last working day of that month.
    """
    uk_holidays = holidays.UnitedKingdom()
    if last_day_of_month in uk_holidays or last_day_of_month.weekday() > 4:
        return get_last_working_day_of_a_month(last_day_of_month - timedelta(days=1))
    else:
        return last_day_of_month


def get_last_day_of_this_month() -> date:
    """Returns the last day of the current month"""
    today = datetime.today()
    return date(
        today.year, today.month, calendar.monthrange(today.year, today.month)[1]
    )


class PaginationMixin:
    def paginate(self, paged_object: object, entries_per_page: int) -> object:
        page = self.request.GET.get("page", 1)
        paginator = Paginator(paged_object, entries_per_page)

        try:
            paged_object = paginator.page(page)
        except PageNotAnInteger:
            paged_object = paginator.page(1)
        except EmptyPage:
            paged_object = paginator.page(paginator.num_pages)

        return paged_object


def check_matching_gov_department(user: User, supply_chain: SupplyChain):
    """Check user's gov department matches that of a supply chain."""
    return user.gov_department == supply_chain.gov_department


class GovDepPermissionMixin:
    """
    A mixin which will rasie a 403 forbidden error if
    a user tries to access a URL for a supply chain not
    linked to their gov department.
    """

    def dispatch(self, *args, **kwargs):
        supply_chain = SupplyChain.objects.get(slug=kwargs.get("sc_slug"))

        if not check_matching_gov_department(self.request.user, supply_chain):
            raise PermissionDenied
        return super().dispatch(*args, **kwargs)


def get_last_working_day_of_previous_month() -> date:
    """
    Returns the last working day of the previous month.
    """
    last_day_of_previous_month = date.today().replace(day=1) - timedelta(1)
    previous_month_deadline = get_last_working_day_of_a_month(
        last_day_of_previous_month
    )
    return previous_month_deadline
