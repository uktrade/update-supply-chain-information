from django.test import Client
from django.urls import reverse


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
