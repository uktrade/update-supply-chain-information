from django.urls import path, include
from rest_framework import routers

from accounts.api_views import UserViewSet
from supply_chains.admin import admin_site
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
    SAUReview,
    MonthlyUpdateInfoCreateView,
    MonthlyUpdateInfoEditView,
    MonthlyUpdateTimingEditView,
    MonthlyUpdateStatusEditView,
    MonthlyUpdateRevisedTimingEditView,
    MonthlyUpdateSummaryView,
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

monthly_update_urlpatterns = [
    path(
        "info/",
        MonthlyUpdateInfoEditView.as_view(),
        name="monthly-update-info-edit",
    ),
    path(
        "timing/",
        MonthlyUpdateTimingEditView.as_view(),
        name="monthly-update-timing-edit",
    ),
    path(
        "delivery-status/",
        MonthlyUpdateStatusEditView.as_view(),
        name="monthly-update-status-edit",
    ),
    path(
        "revised-timing/",
        MonthlyUpdateRevisedTimingEditView.as_view(),
        name="monthly-update-revised-timing-edit",
    ),
    path(
        "confirm/",
        MonthlyUpdateSummaryView.as_view(),
        name="monthly-update-summary",
    ),
    path(
        "review/",
        SAUReview.as_view(),
        name="update_review",
    ),
]

strategic_action_urlpatterns = [
    path(
        "strategic-actions/",
        SASummaryView.as_view(),
        name="strat_action_summary",
    ),
    path(
        "<slug:action_slug>/update/",
        include(
            [
                path(
                    "start/",
                    MonthlyUpdateInfoCreateView.as_view(),
                    name="monthly-update-create",
                ),
                path("<slug:update_slug>/", include(monthly_update_urlpatterns)),
            ]
        ),
    ),
]

supply_chain_urlpatterns = [
    path("", HomePageView.as_view(), name="index"),
    path(
        "<slug:supply_chain_slug>/",
        include(
            [
                path("", SCTaskListView.as_view(), name="tlist"),
                path("summary/", SCSummary.as_view(), name="sc_summary"),
                path(
                    "complete/",
                    SCCompleteView.as_view(),
                    name="update_complete",
                ),
                path("", include(strategic_action_urlpatterns)),
            ]
        ),
    ),
]

urlpatterns = [
    path("auth/", include("authbroker_client.urls")),
    path("admin/", admin_site.urls),
    path("api/", include(router.urls)),
    path("", include(supply_chain_urlpatterns)),
]
