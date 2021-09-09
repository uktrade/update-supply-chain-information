import pytest
from django.http import HttpRequest
from django.template import Context, Template

from accounts.models import GovDepartment
from accounts.test.factories import UserFactory

pytestmark = pytest.mark.django_db

dummy_visualisation_url = "https://example.com/"


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
    return request


class TestQuickSightURLTemplateTagTestCase:
    def test_quicksight_url_obtained_from_user_department(self, dit_user_request):
        context = Context(
            {
                "request": dit_user_request,
            }
        )
        template_to_render = Template(
            "{% load visualisation_link %}{% visualisation_link %}"
        )
        rendered_template = template_to_render.render(context)
        assert dummy_visualisation_url in rendered_template
