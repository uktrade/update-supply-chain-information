from datetime import date
from typing import List, Dict, Tuple
from itertools import groupby

from django.db.models import Sum
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models.expressions import Q, F
from django.http import HttpResponseRedirect
from django.template.defaultfilters import date as date_filter, first
from django.db.models import Count, When, Case, Value
from django.shortcuts import redirect, render
from django.urls import reverse, reverse_lazy
from django.template.defaultfilters import date as date_tag
from django.views.generic import (
    ListView,
    UpdateView,
    CreateView,
    TemplateView,
)

from supply_chains.forms import (
    MonthlyUpdateInfoForm,
    MonthlyUpdateSubmissionForm,
    YesNoChoices,
    ApproximateTimings,
    MonthlyUpdateStatusForm,
    MonthlyUpdateTimingForm,
    MonthlyUpdateModifiedTimingForm,
)
from supply_chains.models import (
    SupplyChain,
    SupplyChainUmbrella,
    StrategicAction,
    StrategicActionUpdate,
    RAGRating,
)
from supply_chains.utils import (
    get_last_day_of_this_month,
    get_last_working_day_of_a_month,
    get_last_working_day_of_previous_month,
)
from supply_chains.mixins import PaginationMixin, GovDepPermissionMixin
from supply_chains.templatetags.supply_chain_tags import get_tasklist_link


class SCHomePageView(LoginRequiredMixin, PaginationMixin, ListView):
    model = SupplyChain
    context_object_name = "supply_chains"
    template_name = "sc_home.html"

    def get_queryset(self):
        supply_chains = self.request.user.gov_department.supply_chains.filter(
            is_archived=False
        )
        return supply_chains.annotate(
            strategic_action_count=Count(
                Case(When(strategic_actions__is_archived=False, then=Value(1)))
            )
        ).order_by("name")

    def get_unique_umbrella_tuples(self) -> List:
        # Due to annotate within get_queryset, distinct can't be used
        i = self.object_list.filter(supply_chain_umbrella__isnull=False)
        tuples = [(x.supply_chain_umbrella, x.id) for x in i]
        unique_umbrellas = set(e[0] for e in tuples)
        unique_tuples = []

        for u in unique_umbrellas:
            for t in tuples:
                if u == t[0]:
                    unique_tuples.append(t)
                    break

        return unique_tuples

    def _get_umbrella_sa_count(self, u: SupplyChainUmbrella) -> int:
        sum = u.supply_chains.annotate(
            strategic_action_count=Count(
                Case(When(strategic_actions__is_archived=False, then=Value(1)))
            )
        )
        return sum.aggregate(Sum("strategic_action_count"))[
            "strategic_action_count__sum"
        ]

    def _inject_sc_umbrellas(self):
        """Update supply chain list with umbrella details

        This method over-rides supply chain list with removing chains that are part of an umbrella
        and inserting unique umbrella details in their place, which is expected to be 1, per
        department.
        """
        unique_tuples = self.get_unique_umbrella_tuples()

        qs = self.object_list.filter(
            Q(supply_chain_umbrella__isnull=True)
            | Q(id__in=[x[1] for x in unique_tuples])
        )

        # Tried to unify the query set with required fields like name, slug etc which
        # worked fine for pure supply chains while for chains under umbrella annotation queries
        # got bigger and needed Subquery as Djnago doesn't support expressions. Even with
        # subqueries, there were exceptions being thrown. Further investigation could resolve this
        # However in the interest of time left and per KISS priciples, retuning list of dicts
        # with info required for the page!

        chains = list()

        for item in qs.iterator():
            if item.supply_chain_umbrella:
                u = item.supply_chain_umbrella
                sc = u.supply_chains.all().order_by("-last_submission_date").first()
                last_updated = date_tag(sc.last_submission_date, "j M Y")
                sa_count = self._get_umbrella_sa_count(u)

                chains.append(
                    {
                        "name": u.name,
                        "slug": u.slug,
                        "sa_count": sa_count,
                        "last_updated": last_updated,
                    }
                )
            else:
                chains.append(
                    {
                        "name": item.name,
                        "slug": item.slug,
                        "sa_count": item.strategic_action_count,
                        "last_updated": date_tag(item.last_submission_date, "j M Y"),
                    }
                )

        return chains

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        last_deadline = get_last_working_day_of_previous_month()

        context["deadline"] = get_last_working_day_of_a_month(
            get_last_day_of_this_month()
        )
        context["num_updated_supply_chains"] = self.object_list.submitted_since(
            last_deadline
        ).count()

        # Total supply chains are aways sum of supply chains with active SAs.
        # Though SC with 0 active SA are listed, no action is required and hence not included
        # for to be completed
        total_sc_with_active_sa = self.object_list.filter(
            strategic_actions__is_archived=False
        ).count()
        context["update_complete"] = (
            context["num_updated_supply_chains"] == total_sc_with_active_sa
        )

        context["num_in_prog_supply_chains"] = (
            total_sc_with_active_sa - context["num_updated_supply_chains"]
        )
        context["gov_department_name"] = self.request.user.gov_department.name

        chain_list = self._inject_sc_umbrellas()

        context["supply_chains"] = self.paginate(chain_list, 5)

        return context


class SCTaskListView(
    LoginRequiredMixin, GovDepPermissionMixin, PaginationMixin, TemplateView
):
    template_name = "task_list.html"
    tasks_per_page = 5

    # This value, used for request processing, is initialised in dispatch()
    last_deadline = None

    def _update_review_routes(self) -> None:
        for update in self.sa_updates:
            url_kwargs = {
                "update_slug": update["update_slug"],
                "action_slug": update["action_slug"],
            }
            url_kwargs.update(self.kwargs)
            url = reverse("monthly-update-review", kwargs=url_kwargs)
            update["route"] = url

    def _sort_updates(self, updates: List) -> List:
        SORT_ORDER = {
            "Not started": 0,
            "In progress": 1,
            "Ready to submit": 2,
            "Submitted": 3,
        }

        updates.sort(key=lambda val: SORT_ORDER[val["status"].label])

        return updates

    def _get_sa_update_list(self, sa_qset, supply_chain: SupplyChain) -> List[Dict]:
        sa_updates = list()

        for sa in sa_qset.iterator():
            update = dict()

            update["name"] = sa.name
            update["description"] = sa.description

            sau = StrategicActionUpdate.objects.since(
                self.last_deadline,
                supply_chain=supply_chain,
                strategic_action=sa,
            )

            if sau:
                update["status"] = StrategicActionUpdate.Status(sau[0].status)
                update["update_slug"] = sau[0].slug
                update["action_slug"] = sa.slug
                update["route"] = reverse(
                    "monthly-update-info-edit",
                    kwargs={
                        "supply_chain_slug": supply_chain.slug,
                        "action_slug": sa.slug,
                        "update_slug": sau[0].slug,
                    },
                )
            else:
                update["status"] = StrategicActionUpdate.Status.NOT_STARTED
                update["route"] = reverse(
                    "monthly-update-create",
                    kwargs={
                        "supply_chain_slug": supply_chain.slug,
                        "action_slug": sa.slug,
                    },
                )

            sa_updates.append(update)

        return self._sort_updates(sa_updates)

    def _process_umbrella(self, umbrella) -> None:
        scs = umbrella.supply_chains.all()
        sa_qset = StrategicAction.objects.none()
        self.sa_updates = []
        self.submitted_only_updates = self.ready_to_submit_updates = 0

        for sc in scs:
            qs = StrategicAction.objects.filter(supply_chain=sc, is_archived=False)
            self.sa_updates.extend(self._get_sa_update_list(qs, sc))

            self.ready_to_submit_updates += (
                StrategicActionUpdate.objects.since(
                    self.last_deadline,
                    supply_chain=sc,
                    status__in=[
                        StrategicActionUpdate.Status.READY_TO_SUBMIT,
                        StrategicActionUpdate.Status.SUBMITTED,
                    ],
                )
                .filter(strategic_action__is_archived=False)
                .count()
            )

            self.submitted_only_updates += (
                StrategicActionUpdate.objects.since(
                    self.last_deadline,
                    supply_chain=sc,
                    status=StrategicActionUpdate.Status.SUBMITTED,
                )
                .filter(strategic_action__is_archived=False)
                .count()
            )

            sa_qset |= qs
        self.total_sa = len(sa_qset)
        self.sa_updates = self._sort_updates(self.sa_updates)

        return

    def _extract_view_data(self, *args, **kwargs):
        supply_chain_slug = kwargs.get("supply_chain_slug", "DEFAULT")

        try:
            self.supply_chain = SupplyChain.objects.get(
                slug=supply_chain_slug, is_archived=False
            )
            self.supply_chain_name = self.supply_chain.name
        except SupplyChain.DoesNotExist:
            umbrella = SupplyChainUmbrella.objects.get(slug=supply_chain_slug)
            self.supply_chain_name = umbrella.name
            self._process_umbrella(umbrella)

        else:
            sa_qset = StrategicAction.objects.filter(
                supply_chain=self.supply_chain, is_archived=False
            )
            self.total_sa = sa_qset.count()
            self.sa_updates = self._get_sa_update_list(sa_qset, self.supply_chain)

            self.ready_to_submit_updates = (
                StrategicActionUpdate.objects.since(
                    self.last_deadline,
                    supply_chain=self.supply_chain,
                    status__in=[
                        StrategicActionUpdate.Status.READY_TO_SUBMIT,
                        StrategicActionUpdate.Status.SUBMITTED,
                    ],
                )
                .filter(strategic_action__is_archived=False)
                .count()
            )

            self.submitted_only_updates = (
                StrategicActionUpdate.objects.since(
                    self.last_deadline,
                    supply_chain=self.supply_chain,
                    status=StrategicActionUpdate.Status.SUBMITTED,
                )
                .filter(strategic_action__is_archived=False)
                .count()
            )

        self.incomplete_updates = self.total_sa - self.ready_to_submit_updates

        self.update_complete = (
            self.total_sa == self.ready_to_submit_updates and self.total_sa != 0
        )
        self.update_submitted = (
            self.total_sa == self.submitted_only_updates and self.total_sa != 0
        )

        if self.update_submitted:
            self._update_review_routes()

    def dispatch(self, *args, **kwargs):
        # initialise value of last_deadline for this request
        # Although this is a class attribute for ease of access in various methods,
        # it's only needed by methods involved in request processing
        # so it makes more sense to initialise it here rather than declaring it in the class definition.
        self.last_deadline = get_last_working_day_of_previous_month()
        self._extract_view_data(*args, **kwargs)
        self.sa_updates = self.paginate(self.sa_updates, self.tasks_per_page)

        return super().dispatch(*args, **kwargs)

    def post(self, *args, **kwargs):
        if self.total_sa == self.ready_to_submit_updates and self.total_sa:
            supply_chain_slug = kwargs.get("supply_chain_slug", None)
            scs = list()
            try:
                self.supply_chain = SupplyChain.objects.get(
                    slug=supply_chain_slug, is_archived=False
                )
                scs.append(self.supply_chain)
            except SupplyChain.DoesNotExist:
                umbrella = SupplyChainUmbrella.objects.get(slug=supply_chain_slug)

                if umbrella:
                    scs.extend(umbrella.supply_chains.all())
                else:
                    raise

            for sc in scs:
                sc.last_submission_date = date.today()
                sc.save()

                updates = StrategicActionUpdate.objects.since(
                    self.last_deadline,
                    supply_chain=sc,
                    status=StrategicActionUpdate.Status.READY_TO_SUBMIT,
                )

                for update in updates.iterator():
                    update.submission_date = date.today()
                    update.status = StrategicActionUpdate.Status.SUBMITTED
                    update.save()

            return redirect(
                "supply-chain-update-complete", supply_chain_slug=supply_chain_slug
            )
        else:
            self.submit_error = True
            kwargs.setdefault("view", self)
            return render(self.request, self.template_name, context=kwargs)


class SCCompleteView(LoginRequiredMixin, GovDepPermissionMixin, TemplateView):
    template_name = "task_complete.html"

    def _extract_umbrella_details(self, umbrella) -> Tuple:
        # TODO: Move this to a until function
        sum = umbrella.supply_chains.annotate(
            strategic_action_count=Count(
                Case(When(strategic_actions__is_archived=False, then=Value(1)))
            )
        )

        total_sa = sum.aggregate(Sum("strategic_action_count"))[
            "strategic_action_count__sum"
        ]

        submitted = 0
        for sc in umbrella.supply_chains.all():
            submitted += StrategicActionUpdate.objects.since(
                self.last_deadline,
                supply_chain=sc,
                status=StrategicActionUpdate.Status.SUBMITTED,
            ).count()

        return (total_sa, submitted)

    def _validate(self, umbrella: SupplyChainUmbrella = None) -> bool:
        if umbrella:
            total_sa, submitted = self._extract_umbrella_details(umbrella)
        else:
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
        self.supply_chain_slug = kwargs.get("supply_chain_slug", None)
        self.last_deadline = get_last_working_day_of_previous_month()
        umbrella = None

        try:
            self.supply_chain = SupplyChain.objects.get(
                slug=self.supply_chain_slug, is_archived=False
            )
            self.supply_chain_name = self.supply_chain.name
        except SupplyChain.DoesNotExist:
            umbrella = SupplyChainUmbrella.objects.get(slug=self.supply_chain_slug)
            self.supply_chain_name = umbrella.name

        # This is to gaurd manual access if not actually complete, help them to complete
        if not self._validate(umbrella):
            return redirect(
                "supply-chain-task-list", supply_chain_slug=self.supply_chain_slug
            )

        supply_chains = request.user.gov_department.supply_chains.filter(
            is_archived=False
        ).order_by("name")

        self.sum_of_supply_chains = supply_chains.filter(
            supply_chain_umbrella__isnull=True
        ).count()

        self.num_updated_supply_chains = (
            supply_chains.filter(supply_chain_umbrella__isnull=True)
            .submitted_since(self.last_deadline)
            .count()
        )

        if umbrella:
            # There can be one umbrella per department
            self.sum_of_supply_chains += 1
            self.num_updated_supply_chains += 1

        kwargs.setdefault("view", self)
        return render(request, self.template_name, context=kwargs)


class MonthlyUpdateMixin:
    model = StrategicActionUpdate
    context_object_name = "strategic_action_update"
    slug_url_kwarg = "update_slug"
    object: StrategicActionUpdate = None

    def get_queryset(self):
        supply_chain_slug = self.kwargs.get("supply_chain_slug")
        action_slug = self.kwargs.get("action_slug")
        return (
            super()
            .get_queryset()
            .filter(
                supply_chain__slug=supply_chain_slug,
                strategic_action__slug=action_slug,
            )
        )

    def get_strategic_action(self):
        supply_chain_slug = self.kwargs.get("supply_chain_slug")
        action_slug = self.kwargs.get("action_slug")
        return StrategicAction.objects.get(
            supply_chain__slug=supply_chain_slug, slug=action_slug
        )

    def get_success_url(self):
        # This method needs to be implemented by the pages
        # so as to express their rules for what the "next" page is
        raise NotImplementedError(
            f"get_success_url() not implemented by {self.__class__}"
        )

    def get_navigation_links(self):
        url_kwargs = {
            "supply_chain_slug": self.object.strategic_action.supply_chain.slug,
            "action_slug": self.object.strategic_action.slug,
            "update_slug": self.object.slug,
        }

        navigation_links = {
            "Info": {
                "label": "Update information",
                "url": reverse_lazy("monthly-update-info-edit", kwargs=url_kwargs),
                "view": MonthlyUpdateInfoEditView,
                "complete": self.object.content_complete,
            },
            "Timing": {
                "label": "Timing",
                "url": reverse_lazy("monthly-update-timing-edit", kwargs=url_kwargs),
                "view": MonthlyUpdateTimingEditView,
                "complete": self.object.initial_timing_complete,
            },
            "Status": {
                "label": "Action status",
                "url": reverse_lazy("monthly-update-status-edit", kwargs=url_kwargs),
                "view": MonthlyUpdateStatusEditView,
                "complete": self.object.action_status_complete,
            },
            "RevisedTiming": {
                "label": "Revised timing",
                "url": reverse_lazy(
                    "monthly-update-revised-timing-edit", kwargs=url_kwargs
                ),
                "view": MonthlyUpdateRevisedTimingEditView,
                "complete": self.object.revised_timing_complete,
            },
            "Summary": {
                "label": "Confirm",
                "url": reverse_lazy("monthly-update-summary", kwargs=url_kwargs),
                "view": MonthlyUpdateSummaryView,
                "complete": self.object.complete,
            },
        }
        if self.object.has_existing_target_completion_date:
            navigation_links.pop("Timing")
            if not self.object.is_changing_target_completion_date and not isinstance(
                self, MonthlyUpdateRevisedTimingEditView
            ):
                navigation_links.pop("RevisedTiming")
        else:
            navigation_links.pop("RevisedTiming")
        found_current_page = False
        for title, info in navigation_links.items():
            is_current_page = isinstance(self, info["view"])
            if is_current_page:
                found_current_page = True
                info["is_current_page"] = True
            if (found_current_page and not info["complete"]) or is_current_page:
                info["not_a_link"] = True
        # special case: there's nothing on the model to tell us that the user wants to change timing
        # for an update with existing timing information, i.e. via the Revised Timing page
        # so we have to rely on that page being the view for this case
        if isinstance(self, MonthlyUpdateRevisedTimingEditView):
            # on the Revised Timing page…
            if not self.object.is_changing_target_completion_date:
                # but no values for revised timing have been provided yet
                navigation_links["Summary"]["not_a_link"] = True
        return navigation_links

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["navigation_links"] = self.get_navigation_links()
        return context


class MonthlyUpdateInfoCreateView(
    LoginRequiredMixin, GovDepPermissionMixin, MonthlyUpdateMixin, CreateView
):
    template_name = "supply_chains/monthly_update_info_form.html"
    form_class = MonthlyUpdateInfoForm

    def get(self, request, *args, **kwargs):
        last_deadline = get_last_working_day_of_previous_month()
        strategic_action: StrategicAction = self.get_strategic_action()
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
                    user=request.user,
                )
            )
        update_url = reverse(
            "monthly-update-info-edit",
            kwargs={
                "supply_chain_slug": current_month_update.strategic_action.supply_chain.slug,
                "action_slug": current_month_update.strategic_action.slug,
                "update_slug": current_month_update.slug,
            },
        )
        return redirect(update_url)


class MonthlyUpdateInfoEditView(
    LoginRequiredMixin, GovDepPermissionMixin, MonthlyUpdateMixin, UpdateView
):
    template_name = "supply_chains/monthly_update_info_form.html"
    form_class = MonthlyUpdateInfoForm

    def get_success_url(self):
        if self.object.strategic_action.target_completion_date is None:
            next_page_url = "monthly-update-timing-edit"
        else:
            next_page_url = "monthly-update-status-edit"
        url_kwargs = {
            "supply_chain_slug": self.object.strategic_action.supply_chain.slug,
            "update_slug": self.object.slug,
            "action_slug": self.object.strategic_action.slug,
        }
        return reverse(next_page_url, kwargs=url_kwargs)


class MonthlyUpdateStatusEditView(
    LoginRequiredMixin, GovDepPermissionMixin, MonthlyUpdateMixin, UpdateView
):
    template_name = "supply_chains/monthly_update_status_form.html"
    form_class = MonthlyUpdateStatusForm

    completion_date_change_form = None

    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)

    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        if "RED-will_completion_date_change" in self.request.POST:
            self.completion_date_change_form = form.detail_form_for_key(RAGRating.RED)
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
                    == YesNoChoices.YES
                ):
                    next_page_url = "monthly-update-revised-timing-edit"
        url_kwargs = {
            "supply_chain_slug": self.object.strategic_action.supply_chain.slug,
            "update_slug": self.object.slug,
            "action_slug": self.object.strategic_action.slug,
        }
        return reverse(next_page_url, kwargs=url_kwargs)


class MonthlyUpdateTimingEditView(
    LoginRequiredMixin, GovDepPermissionMixin, MonthlyUpdateMixin, UpdateView
):
    template_name = "supply_chains/monthly_update_timing_form.html"
    form_class = MonthlyUpdateTimingForm

    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)

    def get_success_url(self):
        next_page_url = "monthly-update-status-edit"
        url_kwargs = {
            "supply_chain_slug": self.object.strategic_action.supply_chain.slug,
            "update_slug": self.object.slug,
            "action_slug": self.object.strategic_action.slug,
        }
        return reverse(next_page_url, kwargs=url_kwargs)


class MonthlyUpdateRevisedTimingEditView(MonthlyUpdateTimingEditView):
    template_name = "supply_chains/monthly_update_revised_timing_form.html"
    form_class = MonthlyUpdateModifiedTimingForm

    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)

    def get_success_url(self):
        next_page_url = "monthly-update-summary"
        url_kwargs = {
            "supply_chain_slug": self.object.strategic_action.supply_chain.slug,
            "update_slug": self.object.slug,
            "action_slug": self.object.strategic_action.slug,
        }
        return reverse(next_page_url, kwargs=url_kwargs)


class MonthlyUpdateSummaryView(
    LoginRequiredMixin, GovDepPermissionMixin, MonthlyUpdateMixin, UpdateView
):
    template_name = "supply_chains/monthly_update_summary.html"
    form_class = MonthlyUpdateSubmissionForm

    def get_object(self, queryset=None):
        return super().get_object(queryset)

    def get_form_kwargs(self):
        form_kwargs = super().get_form_kwargs()
        form_kwargs["data"] = self.build_form_data()
        if (
            self.object.changed_value_for_is_ongoing
            or self.object.changed_value_for_target_completion_date is not None
        ):
            form_kwargs["initial"]["will_completion_date_change"] = YesNoChoices.YES
        return form_kwargs

    def build_form_data(self):
        """
        As this page won't really display the form but needs to show error messages for missing or invalid values,
        we have to build a representation of the form data that would have caused the current state of our instance
        had a form been submitted to us.
        When this is passed into the "form" constructor via form_kwargs, it takes care of instantiating
        the forms we actually need with this data. Then the form is validated (in get_context_data)
        which gives us the valid or invalid forms we use to build the page.
        """
        # we always have the content field and the delivery status
        form_data = {
            "content": self.object.content,
            "implementation_rag_rating": self.object.implementation_rag_rating,
        }
        # we always have the action status form, but we need to determine how to configure it
        if (
            self.object.implementation_rag_rating is not None
            and self.object.implementation_rag_rating != RAGRating.GREEN
        ):
            # Red or Amber, so must include the reason for delays
            if self.object.implementation_rag_rating == RAGRating.AMBER:
                form_data[
                    f"{RAGRating.AMBER}-reason_for_delays"
                ] = self.object.reason_for_delays
            elif self.object.implementation_rag_rating == RAGRating.RED:
                form_data[
                    f"{RAGRating.RED}-reason_for_delays"
                ] = self.object.reason_for_delays
                # if the status is RED and the timing is changing, include the revised timing fields
                if (
                    self.object.implementation_rag_rating == RAGRating.RED
                    and self.object.is_changing_target_completion_date
                ):
                    form_data[
                        f"reason_for_completion_date_change"
                    ] = self.object.reason_for_completion_date_change
                    if self.object.has_changed_target_completion_date:
                        additional_form_data = {
                            f"is_completion_date_known": YesNoChoices.YES,
                            f"{RAGRating.RED}-will_completion_date_change": YesNoChoices.YES,
                            f"{YesNoChoices.YES}-changed_value_for_target_completion_date_day": self.object.changed_value_for_target_completion_date.day,
                            f"{YesNoChoices.YES}-changed_value_for_target_completion_date_month": self.object.changed_value_for_target_completion_date.month,
                            f"{YesNoChoices.YES}-changed_value_for_target_completion_date_year": self.object.changed_value_for_target_completion_date.year,
                        }
                        form_data.update(additional_form_data)
                    elif self.object.changed_value_for_is_ongoing:
                        additional_form_data = {
                            f"is_completion_date_known": YesNoChoices.NO,
                            f"{RAGRating.RED}-will_completion_date_change": YesNoChoices.YES,
                            f"{YesNoChoices.NO}-surrogate_is_ongoing": ApproximateTimings.ONGOING,
                        }
                        form_data.update(additional_form_data)
        # we only have the timing form if the instance either didn't already know its target completion date
        # or didn't already know it was ongoing
        # or still doesn't know either of those things from pending changes
        if (
            self.object.has_new_target_completion_date
            or self.object.has_new_is_ongoing
            or self.object.is_becoming_ongoing
            or self.object.has_no_timing_information
        ):
            if self.object.has_new_target_completion_date:
                additional_form_data = {
                    "is_completion_date_known": YesNoChoices.YES,
                    f"{YesNoChoices.YES}-changed_value_for_target_completion_date_day": self.object.changed_value_for_target_completion_date.day,
                    f"{YesNoChoices.YES}-changed_value_for_target_completion_date_month": self.object.changed_value_for_target_completion_date.month,
                    f"{YesNoChoices.YES}-changed_value_for_target_completion_date_year": self.object.changed_value_for_target_completion_date.year,
                }
                form_data.update(additional_form_data)
            elif self.object.is_becoming_ongoing or self.object.has_new_is_ongoing:
                additional_form_data = {
                    "is_completion_date_known": YesNoChoices.NO,
                    f"{YesNoChoices.NO}-surrogate_is_ongoing": ApproximateTimings.ONGOING,
                }
                form_data.update(additional_form_data)
        return form_data

    def get_context_data(self, **kwargs):
        kwargs = super().get_context_data(**kwargs)
        if "form" in kwargs.keys():
            kwargs["form"].is_valid()
        return kwargs

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        form = self.get_form()
        if not form.is_valid():
            return self.get(request, *args, **kwargs)
        """
        To finalise the update we must change the update's status to "Ready to submit"
        This only goes to "Submitted" when the Supply Chain's entire round of updates for the month is submitted.
        """
        strategic_action_update = self.get_object()
        self.object = strategic_action_update
        strategic_action: StrategicAction = strategic_action_update.strategic_action
        strategic_action_update.status = StrategicActionUpdate.Status.READY_TO_SUBMIT
        strategic_action_update.save()
        return HttpResponseRedirect(self.get_success_url())

    def get_success_url(self):
        return get_tasklist_link(self.object.supply_chain.slug)


class SASummaryView(
    LoginRequiredMixin, GovDepPermissionMixin, PaginationMixin, TemplateView
):
    template_name = "strategic_action_summary.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        supply_chain = SupplyChain.objects.get(slug=kwargs.get("supply_chain_slug"))

        context["strategic_actions"] = self.paginate(
            supply_chain.strategic_actions.filter(is_archived=False).order_by("name"),
            5,
        )
        context["supply_chain"] = supply_chain
        return context


class SCSummary(LoginRequiredMixin, PaginationMixin, TemplateView):
    template_name = "sc_summary.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context["supply_chains"] = self.paginate(
            SupplyChain.objects.filter(
                is_archived=False, gov_department=self.request.user.gov_department
            ).order_by("name"),
            5,
        )

        return context


class SAUReview(LoginRequiredMixin, GovDepPermissionMixin, TemplateView):
    template_name = "sau_review.html"
    last_deadline = None

    def get_context_data(self, **kwargs):
        self.last_deadline = get_last_working_day_of_previous_month()
        context = super().get_context_data(**kwargs)

        self.supply_chain_slug, sa_slug, update_slug = (
            kwargs.get("supply_chain_slug"),
            kwargs.get("action_slug"),
            kwargs.get("update_slug"),
        )

        # Now that umbrella can be passed in place of supply chain, better not look for
        # supply_chain_slug for this look up
        sau = StrategicActionUpdate.objects.since(
            deadline=self.last_deadline,
            status=StrategicActionUpdate.Status.SUBMITTED,
            slug=update_slug,
            strategic_action__slug=sa_slug,
        ).first()

        try:
            sc = SupplyChain.objects.get(slug=self.supply_chain_slug)
            context["supply_chain_name"] = sc.name
        except SupplyChain.DoesNotExist:
            u = SupplyChainUmbrella.objects.get(slug=self.supply_chain_slug)
            context["supply_chain_name"] = u.name

        context["strategic_action"] = sau.strategic_action
        context["update"] = sau

        if sau.strategic_action.is_ongoing:
            context["completion_estimation"] = "Ongoing"
        else:
            context["completion_estimation"] = date_filter(
                sau.strategic_action.target_completion_date, "j F Y"
            )

        return context


class PrivacyNoticeView(LoginRequiredMixin, TemplateView):
    template_name = "privacy_notice.html"


class HomePageView(LoginRequiredMixin, TemplateView):
    template_name = "index.html"
