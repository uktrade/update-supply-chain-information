from collections import namedtuple
from datetime import date

import pytest
from django.template import Context, Template

pytestmark = pytest.mark.django_db


@pytest.fixture(scope="session")
def gsc_last_changed_by():
    return "test"


@pytest.fixture(scope="session")
def gsc_updated_on():
    return date(year=2021, month=9, day=17)


@pytest.fixture(scope="session")
def gsc_review_on():
    return date(year=2021, month=9, day=17)


@pytest.fixture
def template():
    template = Template(
        """
    {% load gsc_notes %}
    {% gsc_notes instance=instance %}
    """
    )
    return template


GSCProperties = namedtuple(
    "GSCProperties", ["gsc_last_changed_by", "gsc_updated_on", "gsc_review_on"]
)


class TestGSCNotesTemplateTag:
    def test_no_gsc_properties_returns_empty_string(self, template):
        context = Context(
            {
                "instance": GSCProperties(
                    gsc_last_changed_by=None, gsc_updated_on=None, gsc_review_on=None
                )
            }
        )
        rendered_template: str = template.render(context)
        assert rendered_template.strip() == ""

    def test_gsc_review_on_returns_only_that(self, gsc_review_on, template):
        context = Context(
            {
                "instance": GSCProperties(
                    gsc_last_changed_by=None,
                    gsc_updated_on=None,
                    gsc_review_on=gsc_review_on,
                )
            }
        )
        rendered_template: str = template.render(context)
        assert (
            rendered_template.strip()
            == '<p class="govuk-body">To be reviewed on Friday 17 Sep 2021</p>'
        )

    def test_gsc_updated_on_returns_only_that(self, gsc_updated_on, template):
        context = Context(
            {
                "instance": GSCProperties(
                    gsc_last_changed_by=None,
                    gsc_updated_on=gsc_updated_on,
                    gsc_review_on=None,
                )
            }
        )
        rendered_template: str = template.render(context)
        assert (
            rendered_template.strip()
            == '<p class="govuk-body">Last updated on Friday 17 Sep 2021</p>'
        )

    def test_gsc_updated_on_with_gsc_last_changed_by_returns_only_those(
        self, gsc_last_changed_by, gsc_updated_on, template
    ):
        context = Context(
            {
                "instance": GSCProperties(
                    gsc_last_changed_by=gsc_last_changed_by,
                    gsc_updated_on=gsc_updated_on,
                    gsc_review_on=None,
                )
            }
        )
        rendered_template: str = template.render(context)
        assert (
            rendered_template.strip()
            == '<p class="govuk-body">Last updated by test on Friday 17 Sep 2021</p>'
        )

    def test_gsc_last_changed_by_returns_only_that(self, gsc_last_changed_by, template):
        context = Context(
            {
                "instance": GSCProperties(
                    gsc_last_changed_by=gsc_last_changed_by,
                    gsc_updated_on=None,
                    gsc_review_on=None,
                )
            }
        )
        rendered_template: str = template.render(context)
        assert (
            rendered_template.strip()
            == '<p class="govuk-body">Last updated by test</p>'
        )
