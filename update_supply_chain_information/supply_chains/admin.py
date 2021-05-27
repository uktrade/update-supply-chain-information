from django import forms
from django.contrib import admin
from django.contrib.admin import AdminSite
from django.contrib.postgres.forms.array import SplitArrayField
from django.http import HttpResponseRedirect
from django.urls import reverse

from accounts.models import GovDepartment, User
from supply_chains.models import SupplyChain, StrategicAction, StrategicActionUpdate


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
    list_display = (
        "name",
        "gov_department",
        "last_submission_date",
    )


class StrategicActionAdmin(admin.ModelAdmin):
    readonly_fields = (
        "slug",
        "id",
    )
    list_display = (
        "name",
        "supply_chain",
    )


class StrategicActionUpdateAdmin(admin.ModelAdmin):
    readonly_fields = (
        "slug",
        "id",
    )
    list_display = (
        "submission_date",
        "strategic_action",
        "supply_chain",
    )


admin_site.register(GovDepartment, GovDepartmentAdmin)
admin_site.register(User, UserAdmin)
admin_site.register(SupplyChain, SupplyChainAdmin)
admin_site.register(StrategicAction, StrategicActionAdmin)
admin_site.register(StrategicActionUpdate, StrategicActionUpdateAdmin)