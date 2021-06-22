import os

from config.settings import *


# Points to the mock-sso docker container
AUTHBROKER_URL = "http://localhost:8080"
TEST_SSO_PROVIDER_SET_RETURNED_ACCESS_TOKEN = "token"

os.environ["FEEDBACK_GROUP_EMAIL"] = "feedback@email"
