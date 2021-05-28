import pytest
from django.test import Client
from django.urls import reverse

from update_supply_chain_information import settings


def test_correct_middleware_exists():
    assert settings.MIDDLEWARE == [
        "django.middleware.security.SecurityMiddleware",
        "update_supply_chain_information.middleware.add_cache_control_header_middleware",
        "django.contrib.sessions.middleware.SessionMiddleware",
        "django.middleware.common.CommonMiddleware",
        "django.middleware.csrf.CsrfViewMiddleware",
        "django.contrib.auth.middleware.AuthenticationMiddleware",
        "django.contrib.messages.middleware.MessageMiddleware",
        "django.middleware.clickjacking.XFrameOptionsMiddleware",
        "whitenoise.middleware.WhiteNoiseMiddleware",
        "reversion.middleware.RevisionMiddleware",
    ]


class TestCustomMiddleware:
    def test_custom_cache_control_middleware(self):
        """
        Tests that the custom middleware add_cache_control_header_middleware
        adds the correct cache_control header to a response.
        """
        headers = {"HTTP_CONTENT_TYPE": "text/html", "HTTP_ACCEPT": "text/html"}
        client = Client()
        response = client.get(reverse("index"), **headers)
        assert (
            response["Cache-Control"]
            == "max-age=0, no-cache, no-store, must-revalidate, private"
        )
        assert response["Pragma"] == "no-cache"
