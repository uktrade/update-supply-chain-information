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

template_to_render = Template("{% load visualisation_link %}{% visualisation_link %}")


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

    def test_quicksight_url_has_current_url_in_querystring(self, dit_user_request):
        context = Context(
            {
                "request": dit_user_request,
            }
        )

        rendered_template = template_to_render.render(context)

        rendered_link_components = re.match(expected_output_re, rendered_template)
        rendered_url = rendered_link_components.group("url")
        parsed_rendered_url = urlparse(rendered_url)
        parsed_querystring = parse_qs(parsed_rendered_url.query)
        assert "back" in parsed_querystring
        back_url = parsed_querystring["back"][0]
        parsed_back_url = urlparse(
            f"http://{back_url}"
        )  # add scheme back at start as QS doesn't like it being there
        assert parsed_back_url.hostname == dummy_from_domain
        assert parsed_back_url.path == dummy_from_path

    def test_quicksight_url_has_schemeless_url_in_querystring(self, dit_user_request):
        context = Context(
            {
                "request": dit_user_request,
            }
        )

        rendered_template = template_to_render.render(context)

        rendered_link_components = re.match(expected_output_re, rendered_template)
        rendered_url = rendered_link_components.group("url")
        parsed_rendered_url = urlparse(rendered_url)
        parsed_querystring = parse_qs(parsed_rendered_url.query)
        back_url = parsed_querystring["back"][0]
        assert not back_url.startswith("http")
