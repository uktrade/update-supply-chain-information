from django import forms
from django.contrib import admin
from django.contrib.admin import AdminSite
from django.contrib.postgres.forms.array import SplitArrayField
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.template.defaultfilters import linebreaks_filter

from accounts.models import GovDepartment, User
from supply_chains.models import (
    SupplyChain,
    StrategicAction,
    StrategicActionUpdate,
    Country,
    CountryDependency,
    SupplyChainCriticality,
    SupplyChainStage,
    SupplyChainStageSection,
    SupplyChainMaturity,
    ScenarioAssessment,
    SupplyChainUmbrella,
    VulnerabilityAssessment,
    VulAssessmentSupplyStage,
    VulAssessmentReceiveStage,
    VulAssessmentMakeStage,
    VulAssessmentStoreStage,
    VulAssessmentDeliverStage,
)


class CustomAdminSite(AdminSite):
    site_header = "Update supply chain information admin"

    def login(self, request, extra_context=None):
        if request.user.is_authenticated:
            if request.user.is_staff:
                index_path = reverse(
                    "admin:index",
                    current_app=self.name,
                )
                return HttpResponseRedirect(index_path)

        return HttpResponseRedirect(reverse("index"))


admin_site = CustomAdminSite(name="admin")


class GovDepartmentForm(forms.ModelForm):
    email_domains = SplitArrayField(
        base_field=forms.fields.CharField(max_length=255, required=False),
        remove_trailing_nulls=True,
        size=5,
        help_text="An email domain is the section of the email address after the '@' sign. E.g. trade.gov.uk.",
    )


class GovDepartmentAdmin(admin.ModelAdmin):
    readonly_fields = ("id",)
    list_display = ("name",)
    form = GovDepartmentForm


class UserAdmin(admin.ModelAdmin):
    readonly_fields = ("id",)
    list_display = (
        "__str__",
        "gov_department",
    )


class SupplyChainAdmin(admin.ModelAdmin):
    readonly_fields = (
        "slug",
        "id",
    )
    list_display = ("name", "gov_department", "last_submission_date", "is_archived")

    list_filter = ("is_archived",)


class StrategicActionAdmin(admin.ModelAdmin):
    readonly_fields = (
        "slug",
        "id",
    )
    list_display = (
        "name",
        "supply_chain",
        "is_archived",
        "gov_department",
        "gsc_notes",
    )

    list_filter = (
        "is_archived",
        "supply_chain",
        "supply_chain__gov_department",
    )

    @admin.display(ordering="supply_chain__gov_department")
    def gov_department(self, obj):
        return obj.supply_chain.gov_department


class StrategicActionUpdateAdmin(admin.ModelAdmin):
    readonly_fields = (
        "slug",
        "id",
    )

    list_display = (
        "date_created",
        "submission_date",
        "strategic_action",
        "supply_chain",
        "status",
        "gov_department",
    )

    list_filter = (
        "supply_chain",
        "strategic_action",
    )

    @admin.display(ordering="supply_chain__gov_department")
    def gov_department(self, obj):
        return obj.supply_chain.gov_department


class ScenarioAssessmentAdmin(admin.ModelAdmin):
    fields = (
        "supply_chain",
        "borders_closed_rag_rating",
        "borders_closed_impact",
        "borders_closed_is_critical",
        "borders_closed_critical_scenario",
        "storage_full_rag_rating",
        "storage_full_impact",
        "storage_full_is_critical",
        "storage_full_critical_scenario",
        "ports_blocked_rag_rating",
        "ports_blocked_impact",
        "ports_blocked_is_critical",
        "ports_blocked_critical_scenario",
        "raw_material_shortage_rag_rating",
        "raw_material_shortage_impact",
        "raw_material_shortage_is_critical",
        "raw_material_shortage_critical_scenario",
        "labour_shortage_rag_rating",
        "labour_shortage_impact",
        "labour_shortage_is_critical",
        "labour_shortage_critical_scenario",
        "demand_spike_rag_rating",
        "demand_spike_impact",
        "demand_spike_is_critical",
        "demand_spike_critical_scenario",
        "gsc_updated_on",
        "gsc_last_changed_by",
        "gsc_review_on",
    )

    list_filter = (
        "supply_chain__gov_department",
        "supply_chain",
    )


class SCStageSectionInline(admin.StackedInline):
    model = SupplyChainStageSection
    extra = 1


class SupplyChainStageAdmin(admin.ModelAdmin):
    fields = (
        "name",
        "supply_chain",
        "order",
        "gsc_last_changed_by",
        "gsc_updated_on",
        "gsc_review_on",
    )
    inlines = [
        SCStageSectionInline,
    ]

    ordering = [
        "supply_chain",
    ]
    list_display = (
        "name",
        "order",
        "supply_chain",
    )

    list_filter = ("supply_chain__name",)


class CountryDependencyAdmin(admin.ModelAdmin):
    readonly_fields = (
        "id",
        "supply_chain",
        "country",
    )

    list_display = (
        "supply_chain",
        "country",
        "dependency_level",
    )

    list_filter = (
        "supply_chain",
        "country",
        "dependency_level",
    )

    list_editable = ("dependency_level",)

    list_select_related = (
        "supply_chain",
        "country",
    )

    ordering = (
        "supply_chain",
        "country",
    )
    radio_fields = {"dependency_level": admin.HORIZONTAL}


class SupplyChainUmbrellaAdmin(admin.ModelAdmin):
    readonly_fields = ("id", "slug")

    list_display = ("name", "gov_department", "supply_chains")

    def supply_chains(self, obj):
        scs = obj.supply_chains.values("name").order_by("name")
        names = [x["name"] for x in scs]
        return linebreaks_filter("\n".join(names))


class VulSupplyStageInline(admin.StackedInline):
    model = VulAssessmentSupplyStage
    extra = 0
    min_num = 1
    max_num = 1


class VulReceiveStageInline(admin.StackedInline):
    model = VulAssessmentReceiveStage
    extra = 0
    min_num = 1
    max_num = 1


class VulMakeStageInline(admin.StackedInline):
    model = VulAssessmentMakeStage
    extra = 0
    min_num = 1
    max_num = 1


class VulStoreStageInline(admin.StackedInline):
    model = VulAssessmentStoreStage
    extra = 0
    min_num = 1
    max_num = 1


class VulDeliverStageInline(admin.StackedInline):
    model = VulAssessmentDeliverStage
    extra = 0
    min_num = 1
    max_num = 1


class VulnerabilityAssessmentAdmin(admin.ModelAdmin):
    fields = (
        "supply_chain",
        "gsc_updated_on",
        "gsc_last_changed_by",
        "gsc_review_on",
    )

    list_filter = (
        "supply_chain__gov_department",
        "supply_chain",
    )

    inlines = (
        VulSupplyStageInline,
        VulReceiveStageInline,
        VulMakeStageInline,
        VulStoreStageInline,
        VulDeliverStageInline,
    )


admin_site.register(GovDepartment, GovDepartmentAdmin)
admin_site.register(User, UserAdmin)
admin_site.register(SupplyChain, SupplyChainAdmin)
admin_site.register(StrategicAction, StrategicActionAdmin)
admin_site.register(StrategicActionUpdate, StrategicActionUpdateAdmin)
admin_site.register(SupplyChainStage, SupplyChainStageAdmin)
admin_site.register(ScenarioAssessment, ScenarioAssessmentAdmin)
admin_site.register(Country)
admin_site.register(CountryDependency, CountryDependencyAdmin)
admin_site.register(SupplyChainUmbrella, SupplyChainUmbrellaAdmin)
admin_site.register(VulnerabilityAssessment, VulnerabilityAssessmentAdmin)
admin_site.register(SupplyChainCriticality)
admin_site.register(SupplyChainMaturity)
