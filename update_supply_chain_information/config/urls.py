from django.urls import path, include
from django.utils.decorators import decorator_from_middleware
from rest_framework import routers

from accounts.api_views import UserViewSet
from healthcheck.middleware import StatsMiddleware
from healthcheck.views import HealthCheckView
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
    SAEditView,
    SASummaryView,
    SCSummary,
    SAUReview,
    MonthlyUpdateInfoCreateView,
    MonthlyUpdateInfoEditView,
    MonthlyUpdateTimingEditView,
    MonthlyUpdateStatusEditView,
    MonthlyUpdateRevisedTimingEditView,
    MonthlyUpdateSummaryView,
    PrivacyNoticeView,
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
        name="monthly-update-review",
    ),
]

strategic_action_urlpatterns = [
    path(
        "strategic-actions/",
        SASummaryView.as_view(),
        name="strategic-action-summary",
    ),
    path(
        "strategic-actions/<slug:action_slug>/edit/",
        SAEditView.as_view(),
        name="edit-strategic-action",
    ),
    path(
        "<slug:action_slug>/updates/",
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
    path("summary/", SCSummary.as_view(), name="supply-chain-summary"),
    path("privacy-notice/", PrivacyNoticeView.as_view(), name="privacy"),
    path(
        "<slug:supply_chain_slug>/",
        include(
            [
                path("", SCTaskListView.as_view(), name="supply-chain-task-list"),
                path("summary/", SCSummary.as_view(), name="supply-chain-summary"),
                path(
                    "complete/",
                    SCCompleteView.as_view(),
                    name="supply-chain-update-complete",
                ),
                path("", include(strategic_action_urlpatterns)),
            ]
        ),
    ),
]

healthcheck_urlpatterns = [
    path(
        "healthcheck/",
        decorator_from_middleware(StatsMiddleware)(HealthCheckView.as_view()),
        name="healthcheck",
    )
]

urlpatterns = [
    path("auth/", include("authbroker_client.urls")),
    path("admin/", admin_site.urls),
    path("api/", include(router.urls)),
    path("", include(healthcheck_urlpatterns)),
    path("", include(supply_chain_urlpatterns)),
]
