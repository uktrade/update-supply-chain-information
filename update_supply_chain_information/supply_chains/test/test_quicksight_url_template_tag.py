import re
from urllib.parse import urlparse, parse_qs

import pytest
from django.conf import settings
from django.http import HttpRequest
from django.template import Context, Template

from accounts.models import GovDepartment
from accounts.test.factories import UserFactory

pytestmark = pytest.mark.django_db

dummy_visualisation_url = "https://example.com/"
dummy_from_domain = settings.ALLOWED_HOSTS[
    0
]  # request.get_absolute_uri() will raise if domain not in ALLOWED_HOSTS
dummy_from_path = "/path/from/here/"

expected_output_re = re.compile(
    r'(?P<link><a\s+(?P<href>href="(?P<url>[^"]*)")[^>]*>.*</a>)'
)

template_to_render = Template("{% load supply_chain_tags %}{% visualisation_link %}")


@pytest.fixture
def gov_department():
    gov_department = GovDepartment.objects.get(name="DIT")
    gov_department.visualisation_url = dummy_visualisation_url
    gov_department.save()
    return gov_department


@pytest.fixture
def dit_user_request(gov_department):
    user = UserFactory(gov_department=gov_department)
    request = HttpRequest()
    request.user = user
    request.path = dummy_from_path
    request.META = {
        "HTTP_HOST": dummy_from_domain,
    }
    return request


class TestQuickSightURLTemplateTag:
    def test_quicksight_url_obtained_from_user_department(self, dit_user_request):
        context = Context(
            {
                "request": dit_user_request,
            }
        )

        rendered_template = template_to_render.render(context)

        assert dummy_visualisation_url in rendered_template
