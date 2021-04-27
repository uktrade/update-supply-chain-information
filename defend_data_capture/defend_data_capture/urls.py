from django.contrib import admin
from django.urls import path, include
from rest_framework import routers

from accounts.api_views import UserViewSet
from supply_chains.api_views import (
    StrategicActionViewset,
    StrategicActionUpdateViewset,
    SupplyChainViewset,
)
from supply_chains.views import (
    HomePageView,
    SCTaskListView,
    SCCompleteView,
    SASummaryView,
    SCSummary,
)

router = routers.DefaultRouter()
router.register(r"users", UserViewSet, basename="user")
router.register(
    r"strategic-actions", StrategicActionViewset, basename="strategic-action"
)
router.register(r"supply-chains", SupplyChainViewset, basename="supply-chain")
router.register(
    r"strategic-action-updates",
    StrategicActionUpdateViewset,
    basename="strategic-action-update",
)

urlpatterns = [
    path("auth/", include("authbroker_client.urls")),
    path("admin/", admin.site.urls),
    path("api/", include(router.urls)),
    path("", HomePageView.as_view(), name="index"),
    path("<slug:sc_slug>/summary", SCSummary.as_view(), name="sc_summary"),
    path("", views.index, name="index"),
    path(
        "<slug:supply_chain_slug>/strategic-actions/",
        views.StrategicActionListView.as_view(),
        name="strategic-actions",
    ),
    path(
        "<slug:supply_chain_slug>/strategic-actions/<slug:strategic_action_slug>/update/start/",
        views.MonthlyUpdateInfoCreateView.as_view(),
        name="monthly-update-create",
    ),
    path(
        "<slug:supply_chain_slug>/strategic-actions/<slug:strategic_action_slug>/update/<slug:update_slug>/info/",
        views.MonthlyUpdateInfoEditView.as_view(),
        name="monthly-update-info-edit",
    ),
    path(
        "<slug:supply_chain_slug>/strategic-actions/<slug:strategic_action_slug>/update/<slug:update_slug>/timing/",
        views.MonthlyUpdateTimingEditView.as_view(),
        name="monthly-update-timing-edit",
    ),
    path(
        "<slug:supply_chain_slug>/strategic-actions/<slug:strategic_action_slug>/update/<slug:update_slug>/delivery-status/",
        views.MonthlyUpdateStatusEditView.as_view(),
        name="monthly-update-status-edit",
    ),
    path(
        "<slug:supply_chain_slug>/strategic-actions/<slug:strategic_action_slug>/update/<slug:update_slug>/revised-timing/",
        views.MonthlyUpdateRevisedTimingEditView.as_view(),
        name="monthly-update-revised-timing-edit",
    ),
    path(
        "<slug:supply_chain_slug>/strategic-actions/<slug:strategic_action_slug>/update/<slug:update_slug>/summary/",
        views.MonthlyUpdateSummaryView.as_view(),
        name="monthly-update-summary",
    ),
    path("<slug:sc_slug>", SCTaskListView.as_view(), name="tlist"),
    path("<slug:sc_slug>/complete", SCCompleteView.as_view(), name="update_complete"),
    # path("strategic-actions/", views.StrategicActionListView.as_view(), name="strategic-actions"),
    # path("strategic-actions/<slug:strategic_action_slug>/update/start/", views.MonthlyUpdateInfoCreateView.as_view(), name="monthly-update-create"),
    # path("strategic-actions/<slug:strategic_action_slug>/update/<slug:update_slug>/info/", views.MonthlyUpdateInfoEditView.as_view(), name="monthly-update-info-edit"),
    # path("strategic-actions/<slug:strategic_action_slug>/update/<slug:update_slug>/timing/", views.MonthlyUpdateTimingEditView.as_view(), name="monthly-update-info-edit"),
    # path("strategic-actions/<slug:strategic_action_slug>/update/<slug:update_slug>/delivery-status/", views.MonthlyUpdateStatusEditView.as_view(), name="monthly-update-status-edit"),
    # path("strategic-actions/<uuid:strategic_action_id>/update/start/", views.MonthlyUpdateInfoCreateView.as_view(), name="monthly-update-create"),
    # path("strategic-actions/<uuid:strategic_action_id>/update/<uuid:id>/info/", views.MonthlyUpdateInfoEditView.as_view(), name="monthly-update-info-edit"),
    # path("strategic-actions/<uuid:strategic_action_id>/update/<uuid:id>/timing/", views.MonthlyUpdateTimingEditView.as_view(), name="monthly-update-info-edit"),
    # path("strategic-actions/<uuid:strategic_action_id>/update/<uuid:id>/delivery-status/", views.MonthlyUpdateStatusEditView.as_view(), name="monthly-update-status-edit"),
    path("strategic-actions/", views.StrategicActionListView.as_view(), name="strategic-actions"),
    path("strategic-actions/<uuid:strategic_action_id>/update/start/", views.MonthlyUpdateInfoCreateView.as_view(), name="monthly-update-create"),
    path("strategic-actions/<uuid:strategic_action_id>/update/<uuid:id>/info/", views.MonthlyUpdateInfoEditView.as_view(), name="monthly-update-info-edit"),
    path("strategic-actions/<uuid:strategic_action_id>/update/<uuid:id>/timing/", views.MonthlyUpdateTimingEditView.as_view(), name="monthly-update-info-edit"),
    path("strategic-actions/<uuid:strategic_action_id>/update/<uuid:id>/delivery-status/", views.MonthlyUpdateStatusEditView.as_view(), name="monthly-update-status-edit"),
    path(
        "<slug:sc_slug>/strategic-actions",
        SASummaryView.as_view(),
        name="strat_action_summary",
    ),
]
