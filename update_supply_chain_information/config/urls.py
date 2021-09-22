from django.urls import path, include
from django.utils.decorators import decorator_from_middleware
from rest_framework import routers

from healthcheck.middleware import StatsMiddleware
from healthcheck.views import HealthCheckView
from supply_chains.admin import admin_site
from supply_chains.views import (
    HomePageView,
    SCHomePageView,
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
    PrivacyNoticeView,
)
from activity_stream.viewsets import (
    ActivityStreamViewSet,
)
from action_progress.views import (
    ActionProgressView,
    ActionProgressDeptView,
    ActionProgressListView,
    ActionProgressDetailView,
)
from chain_details.views import (
    ChainDetailsView,
    ChainDetailsListView,
    ChainDetailsInfoView,
)


router = routers.DefaultRouter()
router.register(r"activity-stream", ActivityStreamViewSet, basename="activity-stream")

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
    path("", SCHomePageView.as_view(), name="sc-home"),
    path("summary/", SCSummary.as_view(), name="supply-chain-summary"),
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

action_progress_urlpatterns = [
    path("", ActionProgressView.as_view(), name="action-progress"),
    path(
        "<str:dept>/",
        ActionProgressDeptView.as_view(),
        name="action-progress-department",
    ),
    path(
        "<str:dept>/<slug:supply_chain_slug>/",
        ActionProgressListView.as_view(),
        name="action-progress-list",
    ),
    path(
        "<str:dept>/<slug:supply_chain_slug>/<slug:action_slug>/detail/",
        ActionProgressDetailView.as_view(),
        name="action-progress-detail",
    ),
]

chain_details_urlpatterns = [
    path("", ChainDetailsView.as_view(), name="chain-details"),
    path(
        "<str:dept>/",
        ChainDetailsListView.as_view(),
        name="chain-details-list",
    ),
    path(
        "<str:dept>/<slug:supply_chain_slug>/",
        ChainDetailsInfoView.as_view(),
        name="chain-details-info",
    ),
]

urlpatterns = [
    path("auth/", include("authbroker_client.urls")),
    path("admin/", admin_site.urls),
    path("api/", include(router.urls)),
    path("", include(healthcheck_urlpatterns)),
    path("supply-chains/", include(supply_chain_urlpatterns)),
    path("privacy-notice/", PrivacyNoticeView.as_view(), name="privacy"),
    path("", HomePageView.as_view(), name="index"),
    path("action-progress/", include(action_progress_urlpatterns)),
    path("chain-details/", include(chain_details_urlpatterns)),
]
