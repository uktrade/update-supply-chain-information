from django.contrib import admin
from django.urls import path, include
from rest_framework import routers

from api.accounts import views as accounts_views
from api.supply_chain_update.views import StrategicActionViewset

router = routers.DefaultRouter()
router.register(r"users", accounts_views.UserViewSet, basename="user")
router.register(
    r"strategic-actions", StrategicActionViewset, basename="strategic-action"
)

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", include(router.urls)),
]
