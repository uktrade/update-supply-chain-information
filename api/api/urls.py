from django.contrib import admin
from django.urls import path, include
from rest_framework import routers
from api.accounts import views as accounts_views

router = routers.DefaultRouter()
router.register(r"users", accounts_views.UserViewSet, basename="user")

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", include(router.urls)),
]
