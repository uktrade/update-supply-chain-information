from django.contrib import admin
from django.urls import path, include
from rest_framework import routers

from api.accounts.views import UserViewSet
from api.supply_chain_update.views import StrategicActionViewset, SupplyChainViewset

router = routers.DefaultRouter()
router.register(r"users", UserViewSet, basename="user")
router.register(
    r"strategic-actions", StrategicActionViewset, basename="strategic-action"
)
router.register(r"supply-chains", SupplyChainViewset, basename="supply-chain")

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", include(router.urls)),
]
