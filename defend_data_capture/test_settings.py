from defend_data_capture.settings import *

# Points to the mock-sso docker container
AUTHBROKER_URL = "http://localhost:8080"
TEST_SSO_PROVIDER_SET_RETURNED_ACCESS_TOKEN = "token"

# To disable CSRF during testing
MIDDLEWARE.remove(
    "django.middleware.csrf.CsrfViewMiddleware",
)
