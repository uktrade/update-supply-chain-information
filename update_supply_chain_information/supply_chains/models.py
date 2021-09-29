import uuid
from datetime import datetime, date, timedelta

import reversion
from dateutil.relativedelta import relativedelta
from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from django.template.defaultfilters import slugify
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from accounts.models import GovDepartment
from activity_stream.models import ActivityStreamQuerySetMixin
from supply_chains.utils import (
    get_last_working_day_of_previous_month,
    get_last_working_day_of_a_month,
)

MAX_SLUG_LENGTH = 75


class RAGRating(models.TextChoices):
    RED = ("RED", "Red")
    AMBER = ("AMBER", "Amber")
    GREEN = ("GREEN", "Green")


class NullableRAGRating(models.TextChoices):
    RED = ("RED", "Red")
    AMBER = ("AMBER", "Amber")
    GREEN = ("GREEN", "Green")
    NONE = (None, "—")


class SupplyChainUmbrellaQuerySet(ActivityStreamQuerySetMixin, models.QuerySet):
    pass


class SupplyChainUmbrella(models.Model):
    objects = SupplyChainUmbrellaQuerySet.as_manager()
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=settings.CHARFIELD_MAX_LENGTH, unique=True)
    description = models.TextField(blank=True, default="")
    last_modified = models.DateTimeField(auto_now=True)
    gov_department = models.ForeignKey(
        GovDepartment,
        on_delete=models.PROTECT,
        related_name="supply_chain_umbrellas",
        null=True,
        blank=True,
    )

    def __str__(self) -> str:
        if self.gov_department:
            return f"{self.name}, {self.gov_department.name}"
        else:
            return f"{self.name}"


class SupplyChainQuerySet(ActivityStreamQuerySetMixin, models.QuerySet):
    def submitted_since(self, deadline):
        return self.filter(last_submission_date__gt=deadline)


class SupplyChain(models.Model):
    class StatusRating(models.TextChoices):
        LOW = ("low", "Low")
        MEDIUM = ("medium", "Medium")
        HIGH = ("high", "High")

    objects = SupplyChainQuerySet.as_manager()
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=settings.CHARFIELD_MAX_LENGTH)
    description = models.TextField(blank=True, default="")
    last_submission_date = models.DateField(null=True, blank=True)
    gov_department = models.ForeignKey(
        GovDepartment,
        on_delete=models.PROTECT,
        related_name="supply_chains",
    )

    supply_chain_umbrella = models.ForeignKey(
        SupplyChainUmbrella,
        on_delete=models.PROTECT,
        related_name="supply_chains",
        blank=True,
        null=True,
    )

    contact_name = models.CharField(
        max_length=settings.CHARFIELD_MAX_LENGTH, blank=True
    )
    contact_email = models.CharField(
        max_length=settings.CHARFIELD_MAX_LENGTH, blank=True
    )
    vulnerability_status = models.CharField(
        choices=RAGRating.choices,
        max_length=6,
    )
    vulnerability_status_disagree_reason = models.TextField(blank=True)
    risk_severity_status = models.CharField(
        choices=StatusRating.choices,
        max_length=6,
        blank=True,
        default="",
    )
    risk_severity_status_disagree_reason = models.TextField(blank=True)
    slug = models.SlugField(
        null=True, blank=True, unique=True, max_length=MAX_SLUG_LENGTH
    )
    is_archived = models.BooleanField(default=False)
    archived_reason = models.TextField(blank=True)
    archived_date = models.DateField(null=True, blank=True)
    last_modified = models.DateTimeField(auto_now=True)

    def clean(self) -> None:
        error_dict = {}
        if self.supply_chain_umbrella and self.supply_chain_umbrella.gov_department:
            if self.supply_chain_umbrella.gov_department != self.gov_department:
                error_dict.update(
                    {
                        "supply_chain_umbrella": ValidationError(
                            _("Department should match for supply chain and umbrella."),
                            code="invalid",
                        ),
                    }
                )

        if self.is_archived and self.archived_reason == "":
            error_dict.update(
                {
                    "archived_reason": ValidationError(
                        _(
                            "An archived_reason must be given when archiving a supply chain."
                        ),
                        code="required",
                    ),
                }
            )

        if error_dict:
            raise ValidationError(error_dict)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)

        if self.is_archived and self.archived_date is None:
            self.archived_date = timezone.now().date()

        if self.supply_chain_umbrella:
            if not self.supply_chain_umbrella.gov_department:
                # this must be the first link
                self.supply_chain_umbrella.gov_department = self.gov_department
                self.supply_chain_umbrella.save()

        return super().save(*args, **kwargs)

    def __str__(self):
        return self.name


class StrategicActionQuerySet(ActivityStreamQuerySetMixin, models.QuerySet):
    pass


@reversion.register()
class StrategicAction(models.Model):
    class Category(models.TextChoices):
        CREATE = ("create", "Create")
        DIVERSIFY = ("diversify", "Diversify")
        EXPAND = ("expand", "Expand")
        PARTNER = ("partner", "Partner")

    class GeographicScope(models.TextChoices):
        UK_WIDE = ("uk_wide", "UK-wide")
        ENGLAND_ONLY = ("england_only", "England only")

    objects = StrategicActionQuerySet.as_manager()
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=settings.CHARFIELD_MAX_LENGTH)
    start_date = models.DateField(null=True, blank=True)
    description = models.TextField()
    impact = models.TextField(blank=True)
    category = models.CharField(
        choices=Category.choices,
        max_length=9,
    )
    geographic_scope = models.CharField(
        choices=GeographicScope.choices,
        max_length=12,
    )

    supporting_organisations = models.CharField(
        max_length=settings.CHARFIELD_MAX_LENGTH, blank=True, default=""
    )

    is_ongoing = models.BooleanField(default=False)
    target_completion_date = models.DateField(null=True, blank=True)
    is_archived = models.BooleanField(default=False)
    archived_date = models.DateField(null=True, blank=True)
    archived_reason = models.TextField(blank=True)
    specific_related_products = models.TextField(
        help_text="Details of specific products within the supply chain which the action applies to, if applicable.",
        blank=True,
    )
    other_dependencies = models.TextField(
        help_text="Any other dependencies or requirements for completing the action.",
        blank=True,
    )
    gsc_notes = models.TextField(
        help_text="Free text area to record observations, notes by admin/gsc",
        blank=True,
        default="",
    )
    supply_chain = models.ForeignKey(
        SupplyChain,
        on_delete=models.PROTECT,
        related_name="strategic_actions",
    )
    slug = models.SlugField(null=True, blank=True, max_length=MAX_SLUG_LENGTH)
    last_modified = models.DateTimeField(auto_now=True)

    def clean_fields(self, exclude=None):
        super().clean_fields(exclude=exclude)
        if self.is_archived and self.archived_reason == "":
            raise ValidationError(
                "An archived_reason must be given when archiving a strategic action."
            )

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        if self.is_archived and not self.archived_date:
            self.archived_date = timezone.now().date()
        self.full_clean()
        # Log changes in reversion
        reversion_message = None
        reason_for_completion_date_change = kwargs.pop(
            "reason_for_completion_date_change", ""
        )
        user = kwargs.pop("user", None)
        if self.pk is not None:
            # the test item factory appears to create a PK for the model, so it might not really exist
            try:
                # existing instance so see if target_completion_date/is_ongoing combo has changed
                previous_self = StrategicAction.objects.get(pk=self.pk)
                if (
                    self.target_completion_date != previous_self.target_completion_date
                    or self.is_ongoing != previous_self.is_ongoing
                ):
                    prefix = "TIMING"
                    change_type = ""
                    if previous_self.is_ongoing:
                        # must be moving from "Ongoing" to having a target completion date
                        change_type = "Stopped being 'Ongoing'"
                    else:
                        # either changing to "Ongoing" or date has changed
                        if self.is_ongoing:
                            change_type = "Becoming 'Ongoing'"
                        else:
                            change_type = "Target completion date changed"

                    reversion_message = (
                        f"{prefix}: {change_type}: {reason_for_completion_date_change}"
                    )
            except StrategicAction.DoesNotExist:
                pass
        with reversion.create_revision():
            result = super().save(*args, **kwargs)
            if reversion_message is not None:
                reversion.set_comment(reversion_message)
            if user is not None:
                reversion.set_user(user)
        return result

    def last_submitted_update(self):
        return self.monthly_updates.last_month()

    def has_timing_info(self):
        return self.target_completion_date or self.is_ongoing

    def __str__(self):
        if __debug__:
            return f"{self.name}, {self.supply_chain}"
        else:
            return self.name


class SAUQuerySet(ActivityStreamQuerySetMixin, models.QuerySet):
    def since(self, deadline, *args, **kwargs):
        return self.filter(date_created__gt=deadline, *args, **kwargs)

    def last_month(self, before_date=None):
        if before_date is None:
            before_date = datetime.now().date()
        last_month_deadline = get_last_working_day_of_previous_month()
        return (
            self.filter(submission_date__lte=last_month_deadline)
            .order_by("-submission_date")
            .first()
        )

    def for_activity_stream(self):
        return (
            super()
            .for_activity_stream()
            .filter(status=StrategicActionUpdate.Status.SUBMITTED)
        )

    def given_month(self, month: date, *args, **kwargs):
        # RT-489: current month should include the whole period and not upto given day.
        lastday = month.replace(day=1) + relativedelta(months=1) - timedelta(days=1)
        given_deadline = get_last_working_day_of_a_month(lastday)
        last_day_of_previous_month = month.replace(day=1) - timedelta(1)
        last_deadline = get_last_working_day_of_a_month(last_day_of_previous_month)

        return self.filter(
            date_created__gt=last_deadline,
            date_created__lte=given_deadline,
            *args,
            **kwargs,
        ).order_by("date_created")


class StrategicActionUpdate(models.Model):
    class Status(models.TextChoices):
        NOT_STARTED = ("not_started", "Not started")
        IN_PROGRESS = ("in_progress", "In progress")
        READY_TO_SUBMIT = ("ready_to_submit", "Ready to submit")
        SUBMITTED = ("submitted", "Submitted")

    objects = SAUQuerySet.as_manager()
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    status = models.CharField(
        max_length=15,
        choices=Status.choices,
        default=Status.IN_PROGRESS,
        help_text="""The 'ready_to_submit' and 'in_progress' statuses are used to help
 users know whether they have completed all required fields for an update.
 The 'submitted' status refers to when a user can no longer edit an update.""",
    )
    submission_date = models.DateField(null=True, blank=True)
    date_created = models.DateField(default=date.today)
    content = models.TextField(blank=True)
    implementation_rag_rating = models.CharField(
        max_length=5,
        choices=reversed(RAGRating.choices),
        blank=True,
        default=None,
        null=True,
    )
    reason_for_delays = models.TextField(blank=True)
    changed_value_for_target_completion_date = models.DateField(null=True, blank=True)
    reason_for_completion_date_change = models.TextField(blank=True)
    changed_value_for_is_ongoing = models.BooleanField(null=True, default=False)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        on_delete=models.SET_NULL,
        related_name="monthly_updates",
    )
    strategic_action = models.ForeignKey(
        StrategicAction,
        on_delete=models.PROTECT,
        related_name="monthly_updates",
    )
    supply_chain = models.ForeignKey(
        SupplyChain,
        on_delete=models.PROTECT,
        related_name="monthly_updates",
    )
    slug = models.SlugField(null=True, blank=True, max_length=MAX_SLUG_LENGTH)
    last_modified = models.DateTimeField(auto_now=True)

    def validate_unique(self, exclude=None):
        # we want to allow just one update for a period, on a strategic action
        # At times this could be too rigid condition to have, say during testing, which can be
        # refactored, when required
        given_updates = StrategicActionUpdate.objects.given_month(
            self.date_created, strategic_action=self.strategic_action
        )

        if given_updates and self != given_updates[0]:
            raise ValidationError(
                f"Monthly update already exist for the period: {given_updates[0]}"
            )

        super().validate_unique(exclude=exclude)

    def clean(self) -> None:
        error_dict = {}
        if self.status == StrategicActionUpdate.Status.SUBMITTED:
            if not self.submission_date:
                error_dict.update(
                    {
                        "submission_date": ValidationError(
                            _("Missing submission_date."), code="required"
                        ),
                    }
                )

            if not self.content:
                error_dict.update(
                    {
                        "content": ValidationError(
                            _("Missing content."), code="required"
                        ),
                    }
                )

            if not self.implementation_rag_rating:
                error_dict.update(
                    {
                        "implementation_rag_rating": ValidationError(
                            _("Missing implementation_rag_rating."), code="required"
                        ),
                    }
                )
            else:
                if self.implementation_rag_rating != RAGRating.GREEN:
                    if not self.reason_for_delays:
                        error_dict.update(
                            {
                                "reason_for_delays": ValidationError(
                                    _("Missing reason_for_delays."), code="required"
                                ),
                            }
                        )

                    if (
                        self.implementation_rag_rating == RAGRating.RED
                        and self.changed_value_for_target_completion_date
                    ):
                        if not self.reason_for_completion_date_change:
                            error_dict.update(
                                {
                                    "reason_for_completion_date_change": ValidationError(
                                        _("Missing reason_for_completion_date_change."),
                                        code="required",
                                    ),
                                }
                            )

            if error_dict:
                raise ValidationError(error_dict)

    def save(self, *args, **kwargs):

        if self.status == StrategicActionUpdate.Status.SUBMITTED:
            """
            To finalise the update we must:
            1. Copy a revised target completion date to the strategic action, or copy is ongoing and clear the SA's date;
            2. If there is a revised target completion date, record the change in reversion.
            """
            strategic_action_changed = False
            if self.changed_value_for_target_completion_date is not None:
                self.strategic_action.target_completion_date = (
                    self.changed_value_for_target_completion_date
                )
                self.strategic_action.is_ongoing = False
                self.changed_value_for_target_completion_date = None
                strategic_action_changed = True
            if self.changed_value_for_is_ongoing:
                self.strategic_action.is_ongoing = self.changed_value_for_is_ongoing
                self.strategic_action.target_completion_date = None
                self.changed_value_for_is_ongoing = False
                strategic_action_changed = True
            if strategic_action_changed:
                self.strategic_action.save(
                    reason_for_completion_date_change=self.reason_for_completion_date_change,
                    user=self.user,
                )
        super().save(*args, **kwargs)
        if not self.slug:
            self.slug = self.date_created.strftime("%m-%Y")
            try:
                kwargs.pop("force_insert")
            except KeyError:
                pass
            self.save(*args, **kwargs)

    @property
    def has_existing_target_completion_date(self):
        return self.strategic_action.target_completion_date is not None

    @property
    def has_changed_target_completion_date(self):
        return self.changed_value_for_target_completion_date is not None

    @property
    def has_updated_target_completion_date(self):
        return (
            self.changed_value_for_target_completion_date is not None
            and self.has_existing_target_completion_date
        )

    @property
    def has_new_target_completion_date(self):
        return (
            self.changed_value_for_target_completion_date is not None
            and not self.has_existing_target_completion_date
        )

    @property
    def has_no_target_completion_date(self):
        return (
            not self.has_changed_target_completion_date
            and not self.has_existing_target_completion_date
        )

    @property
    def is_currently_ongoing(self):
        return self.strategic_action.is_ongoing

    @property
    def is_becoming_ongoing(self):
        return self.changed_value_for_is_ongoing

    @property
    def has_no_is_ongoing(self):
        return not self.is_currently_ongoing and not self.is_becoming_ongoing

    @property
    def is_changing_is_ongoing(self):
        return self.is_becoming_ongoing and (
            self.is_currently_ongoing or self.has_existing_target_completion_date
        )

    @property
    def has_new_is_ongoing(self):
        return self.is_becoming_ongoing and not (
            self.is_currently_ongoing or self.has_existing_target_completion_date
        )

    @property
    def is_changing_target_completion_date(self):
        return self.has_updated_target_completion_date or self.is_changing_is_ongoing

    @property
    def has_no_timing_information(self):
        return self.has_no_target_completion_date and self.has_no_is_ongoing

    @property
    def has_new_timing(self):
        return self.has_new_target_completion_date or self.has_new_is_ongoing

    @property
    def has_existing_timing(self):
        return self.has_existing_target_completion_date or self.is_currently_ongoing

    @property
    def has_revised_timing(self):
        return self.has_existing_timing and (
            self.changed_value_for_target_completion_date
            or self.changed_value_for_is_ongoing
        )

    @property
    def needs_initial_timing(self):
        return not self.has_existing_timing

    @property
    def content_complete(self):
        return bool(self.content)

    @property
    def initial_timing_complete(self):
        return self.has_existing_timing or self.has_new_timing

    @property
    def action_status_complete(self):
        return self.implementation_rag_rating is not None and (
            self.implementation_rag_rating == RAGRating.GREEN or self.reason_for_delays
        )

    @property
    def revised_timing_complete(self):
        # there's no clear way to know if revised timing is needed;
        # if it's been provided, then it was needed, but if it wasn't
        # it still might have been needed.
        # But other code assumes if it doesn't exist, it isn't needed.
        # However, if it does exist, we do need a reason for it.
        return (not self.has_revised_timing) or self.reason_for_completion_date_change

    @property
    def complete(self):
        """
        Tells us if all required information has been provided
        """
        return (
            self.content_complete
            and self.initial_timing_complete
            and self.action_status_complete
            and self.revised_timing_complete
        )

    def has_timing_info(self):
        return (
            self.changed_value_for_target_completion_date
            or self.changed_value_for_is_ongoing
        )

    def __str__(self):
        return f"Update {self.slug} for {self.strategic_action}"


class GSCUpdateModel(models.Model):
    gsc_last_changed_by = models.CharField(
        max_length=64,
        blank=True,
        default="",
        verbose_name="last updated by",
        help_text="The entity responsible for the most recent change",
    )
    gsc_updated_on = models.DateField(
        null=True,
        blank=True,
        verbose_name="last updated",
        help_text="The date of the most recent change",
    )
    gsc_review_on = models.DateField(
        null=True,
        blank=True,
        verbose_name="review on",
        help_text="The date when a review should be carried out",
    )

    class Meta:
        abstract = True


class MaturitySelfAssessmentQuerySet(ActivityStreamQuerySetMixin, models.QuerySet):
    pass


class MaturitySelfAssessment(GSCUpdateModel):
    class RatingLevel(models.TextChoices):
        LEVEL_1 = ("level_1", "Level 1")
        LEVEL_2 = ("level_2", "Level 2")
        LEVEL_3 = ("level_3", "Level 3")
        LEVEL_4 = ("level_4", "Level 4")
        LEVEL_5 = ("level_5", "Level 5")

    objects = MaturitySelfAssessmentQuerySet.as_manager()
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    date_created = models.DateField(auto_now_add=True)
    maturity_rating_reason = models.TextField()
    maturity_rating_level = models.CharField(
        choices=RatingLevel.choices,
        max_length=7,
    )
    supply_chain = models.ForeignKey(
        SupplyChain,
        on_delete=models.PROTECT,
        related_name="maturity_self_assessment",
    )
    last_modified = models.DateTimeField(auto_now=True)


class VulnerabilityAssessmentQuerySet(ActivityStreamQuerySetMixin, models.QuerySet):
    pass


class VulnerabilityAssessment(GSCUpdateModel):
    objects = VulnerabilityAssessmentQuerySet.as_manager()
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    date_created = models.DateField(auto_now_add=True)
    supply_rag_rating = models.CharField(
        max_length=5,
        choices=RAGRating.choices,
    )
    supply_rating_reason = models.TextField(
        help_text="""This field collects information about the characteristics that
        contribute to the vulnerability of the supply element of the chain.""",
    )
    make_rag_rating = models.CharField(
        max_length=5,
        choices=RAGRating.choices,
    )
    make_rating_reason = models.TextField(
        help_text="""This field collects information about the characteristics that
        contribute to the vulnerability of the make element of the chain.""",
    )
    receive_rag_rating = models.CharField(
        max_length=5,
        choices=RAGRating.choices,
    )
    receive_rating_reason = models.TextField(
        help_text="""This field collects information about the characteristics that
        contribute to the vulnerability of the receive element of the chain.""",
    )
    store_rag_rating = models.CharField(
        max_length=5,
        choices=RAGRating.choices,
    )
    store_rating_reason = models.TextField(
        help_text="""This field collects information about the characteristics that
        contribute to the vulnerability of the store element of the chain.""",
    )
    deliver_rag_rating = models.CharField(
        max_length=5,
        choices=RAGRating.choices,
    )
    deliver_rating_reason = models.TextField(
        help_text="""This field collects information about the characteristics that
        contribute to the vulnerability of the deliver element of the chain.""",
    )
    supply_chain = models.ForeignKey(
        SupplyChain,
        on_delete=models.PROTECT,
        related_name="vulnerability_assessment",
    )
    last_modified = models.DateTimeField(auto_now=True)


class ScenarioAssessmentQuerySet(ActivityStreamQuerySetMixin, models.QuerySet):
    pass


@reversion.register()
class ScenarioAssessment(GSCUpdateModel):
    objects = ScenarioAssessmentQuerySet.as_manager()
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    date_created = models.DateField(auto_now_add=True)
    borders_closed_impact = models.TextField(
        blank=True,
        help_text="""This field collects information about the potential impacts that would occur should
        the borders close.""",
    )
    borders_closed_rag_rating = models.CharField(
        blank=True,
        max_length=5,
        choices=NullableRAGRating.choices,
    )
    borders_closed_is_critical = models.BooleanField(default=False)
    borders_closed_critical_scenario = models.TextField(
        blank=True,
        help_text="""This field collects information about the scenarios envisaged should the lack of storage facilities become critical.""",
    )
    storage_full_impact = models.TextField(
        blank=True,
        help_text="""This field collects information about the potential impacts that would occur should
        storage facilities be full.""",
    )
    storage_full_rag_rating = models.CharField(
        blank=True,
        max_length=5,
        choices=NullableRAGRating.choices,
    )
    storage_full_is_critical = models.BooleanField(default=False)
    storage_full_critical_scenario = models.TextField(
        blank=True,
        help_text="""This field collects information about the scenarios envisaged should the lack of storage facilities become critical.""",
    )
    ports_blocked_impact = models.TextField(
        blank=True,
        help_text="""This field collects information about the potential impacts that would occur should
        the ports be blocked.""",
    )
    ports_blocked_rag_rating = models.CharField(
        blank=True,
        max_length=5,
        choices=NullableRAGRating.choices,
    )
    ports_blocked_is_critical = models.BooleanField(default=False)
    ports_blocked_critical_scenario = models.TextField(
        blank=True,
        help_text="""This field collects information about the scenarios envisaged should the port blockages become critical.""",
    )
    raw_material_shortage_impact = models.TextField(
        blank=True,
        help_text="""This field collects information about the potential impacts that would occur should
        there be a raw material shortage.""",
    )
    raw_material_shortage_rag_rating = models.CharField(
        blank=True,
        max_length=5,
        choices=NullableRAGRating.choices,
    )
    raw_material_shortage_is_critical = models.BooleanField(default=False)
    raw_material_shortage_critical_scenario = models.TextField(
        blank=True,
        help_text="""This field collects information about the scenarios envisaged should the raw materials shortage become critical.""",
    )
    labour_shortage_impact = models.TextField(
        blank=True,
        help_text="""This field collects information about the potential impacts that would occur should
        there be a labour shortage.""",
    )
    labour_shortage_rag_rating = models.CharField(
        blank=True,
        max_length=5,
        choices=NullableRAGRating.choices,
    )
    labour_shortage_is_critical = models.BooleanField(default=False)
    labour_shortage_critical_scenario = models.TextField(
        blank=True,
        help_text="""This field collects information about the scenarios envisaged should the labour shortages become critical.""",
    )
    demand_spike_impact = models.TextField(
        blank=True,
        help_text="""This field collects information about the potential impacts that would occur should
        the demand spike.""",
    )
    demand_spike_rag_rating = models.CharField(
        blank=True,
        max_length=5,
        choices=NullableRAGRating.choices,
    )
    demand_spike_is_critical = models.BooleanField(default=False)
    demand_spike_critical_scenario = models.TextField(
        blank=True,
        help_text="""This field collects information about the scenarios envisaged should the demand spike become critical.""",
    )
    start_date = models.DateField(null=True, blank=True)
    supply_chain = models.OneToOneField(
        SupplyChain,
        on_delete=models.PROTECT,
        related_name="scenario_assessment",
    )
    last_modified = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        # Log changes in reversion
        user = kwargs.pop("user", None)
        # Assume this is a new one
        prefix = "Created"
        if self.pk is not None:
            # The test item factory appears to create a PK for the model, so it might not really exist
            try:
                ScenarioAssessment.objects.get(pk=self.pk)
                # existing instance so record as Edit
                prefix = "Edited"
            except ScenarioAssessment.DoesNotExist:
                pass
        reversion_message = (
            f"{prefix}: scenario assessment for {self.supply_chain.name}"
        )
        with reversion.create_revision():
            result = super().save(*args, **kwargs)
            if reversion_message is not None:
                reversion.set_comment(reversion_message)
            if user is not None:
                reversion.set_user(user)
        return result

    def __str__(self):
        return f"{self.supply_chain.name} scenario assessment"


class SupplyChainStageQuerySet(ActivityStreamQuerySetMixin, models.QuerySet):
    pass


class SupplyChainStage(GSCUpdateModel):
    class StageName(models.TextChoices):
        DEMAND_REQ = ("demand requirements", "Demand Requirements")
        RAW_MATERIAL_EXT = (
            "raw materials extraction/mining",
            "Raw Materials Extraction/Mining",
        )
        REFINING = ("refining", "Refining")
        RAW_MATERIAL_PROC = (
            "raw materials processing/refining",
            "Raw Materials Processing/Refining",
        )
        CHEMICAL_PROC = ("chemical processing", "Chemical Processing")
        OTH_MATERIAL_PROC = (
            "other material-conversion process",
            "Other Material-Conversion Process",
        )
        RAW_MATERIAL_SUP = ("raw materials suppliers", "Raw Materials Suppliers")
        INT_GOODS = ("intermediate goods/capital", "Intermediate Goods/Capital")
        INBOUND_LOG = ("inbound logistics", "Inbound Logistics")
        DELIVERY = ("delivery/shipping ", "Delivery/Shipping")
        MANUFACTURING = ("manufacturing", "Manufacturing")
        COMP_SUP = ("component suppliers", "Component Suppliers")
        FINISHED_GOODS_SUP = ("finished goods supplier", "Finished Goods Supplier")
        ASSEMBLY = ("assembly", "Assembly")
        TESTING = (
            "testing/verification/approval/release",
            "Testing/Verification/Approval/Release",
        )
        FINISHED_PRODUCT = ("finished product", "Finished Product")
        PACKAGING = ("packaging/repackaging", "Packaging/Repackaging")
        OUTBOUND_LOG = ("outbound logistics", "Outbound Logistics")
        STORAGE = ("storage/store", "Storage/Store")
        DISTRIBUTORS = ("distributors", "Distributors")
        ENDPOINT = (
            "end point (retailer, hospital, grid, etc)",
            "End Point (Retailer, Hospital, Grid, etc)",
        )
        ENDUSE = ("end use/consumer", "End Use/Consumer")
        SERVICE_PROVIDER = ("service provider", "Service Provider")
        INSTALLATION = ("installation", "Installation")
        DECOMMISSION = ("decommission  assets", "Decommission  Assets")
        RECYCLING = ("recycling", "Recycling")
        WASTE_DISPOSAL = (
            "waste disposal/asset disposal",
            "Waste Disposal/Asset Disposal",
        )
        MAINTENANCE = ("maintenance", "Maintenance")
        OTHER = ("other - please describe", "Other - Please Describe")

    objects = SupplyChainStageQuerySet.as_manager()
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(
        max_length=50,
        choices=StageName.choices,
        default="",
    )
    supply_chain = models.ForeignKey(
        SupplyChain,
        on_delete=models.PROTECT,
        related_name="chain_stages",
    )
    order = models.PositiveSmallIntegerField(
        help_text="Order number of this stage", default=""
    )
    last_modified = models.DateTimeField(auto_now=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["supply_chain", "order"], name="unique order per supply chain"
            ),
            models.UniqueConstraint(
                fields=["supply_chain", "name"],
                name="unique stage name per supply chain",
            ),
        ]

    def __str__(self):
        return self.get_name_display()


class SupplyChainStageSectionQuerySet(ActivityStreamQuerySetMixin, models.QuerySet):
    pass


class SupplyChainStageSection(models.Model):
    class SectionName(models.TextChoices):
        OVERVIEW = ("overview", "Overview")
        KEYPRODUCTS = ("key products", "Key Products")
        KEYSERVICES = ("key services", "Key Services")
        KEYACTIVITIES = ("key activities", "Key Activities")
        KEYCOUNTRIES = ("key countries", "Key Countries")
        KEYTRANSPTS = ("key transport points", "Key Transport Points")
        KEYCOMPANIES = ("key companies", "Key Companies")
        KEYSECTORS = ("key sectors", "Key Sectors")
        KEYOTHINFO = ("other relevant information", "Other Relevant Information")

    objects = SupplyChainStageSectionQuerySet.as_manager()
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(
        max_length=50,
        choices=SectionName.choices,
        default="",
    )
    description = models.TextField(default="")
    chain_stage = models.ForeignKey(
        SupplyChainStage,
        on_delete=models.PROTECT,
        related_name="stage_sections",
    )
    last_modified = models.DateTimeField(auto_now=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["chain_stage", "name"], name="Unique section within a stage"
            )
        ]

    def __str__(self):
        return f"{self.get_name_display()}, {self.chain_stage.name}"


class CountryQuerySet(ActivityStreamQuerySetMixin, models.QuerySet):
    pass


class Country(models.Model):
    objects = CountryQuerySet.as_manager()
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=64)
    last_modified = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = "Countries"


class CountryDependencyQuerySet(ActivityStreamQuerySetMixin, models.QuerySet):
    pass


class CountryDependency(models.Model):
    class DependencyLevel(models.TextChoices):
        NONE = ("none", "No")
        LOW = ("low", "Low")
        MEDIUM = ("medium", "Medium")
        HIGH = ("high", "High")
        VERY_HIGH = ("very_high", "Very high")

    objects = CountryDependencyQuerySet.as_manager()
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    dependency_level = models.CharField(
        choices=DependencyLevel.choices,
        max_length=9,
    )
    supply_chain = models.ForeignKey(
        SupplyChain,
        on_delete=models.PROTECT,
        related_name="country_dependencies",
    )
    country = models.ForeignKey(
        Country, on_delete=models.PROTECT, related_name="supply_chain_dependencies"
    )
    last_modified = models.DateTimeField(auto_now=True)

    def __str__(self):
        choice_label = self.get_dependency_level_display()
        return f"{choice_label} dependency on {self.country} for {self.supply_chain}"

    class Meta:
        verbose_name_plural = "Country dependencies"
        ordering = ("supply_chain", "country")
