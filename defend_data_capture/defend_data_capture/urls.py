from django.contrib import admin
from django.urls import path, include
from rest_framework import routers

from accounts.api_views import UserViewSet
from supply_chains.api_views import (
    StrategicActionViewset,
    StrategicActionUpdateViewset,
    SupplyChainViewset,
)
from supply_chains import views
from supply_chains.views import (
    SCTaskListView,
    SCCompleteView,
    SASummaryView,
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
    path("", views.index, name="index"),
    path("<slug:sc_slug>", SCTaskListView.as_view(), name="tlist"),
    path("<slug:sc_slug>/complete", SCCompleteView.as_view(), name="update_complete"),
    path(
        "<slug:sc_slug>/strategic-actions",
        SASummaryView.as_view(),
        name="strat_action_summary",
    ),
]
