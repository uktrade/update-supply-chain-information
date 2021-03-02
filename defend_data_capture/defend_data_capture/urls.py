from django.contrib import admin
from django.urls import path, include
from rest_framework import routers

from accounts.api_views import UserViewSet
from supply_chains.api_views import (
    StrategicActionViewset,
    StrategicActionUpdateViewset,
    SupplyChainViewset,
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
    path("admin/", admin.site.urls),
    path("api/", include(router.urls)),
]
