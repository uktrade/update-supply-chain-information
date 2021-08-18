import factory


class GovDepartmentFactory(factory.django.DjangoModelFactory):
    name = factory.Sequence(lambda n: f"GovDepartment{n}")
    email_domains = factory.Sequence(lambda n: [f"department{n}.gov.uk"])

    class Meta:
        model = "accounts.GovDepartment"


class UserFactory(factory.django.DjangoModelFactory):
    sso_email_user_id = factory.Sequence(lambda n: f"foo-{n}@sso.com")
    first_name = factory.Faker("first_name")
    last_name = factory.Faker("last_name")
    email = factory.Faker("email")
    gov_department = factory.SubFactory(GovDepartmentFactory)

    class Meta:
        model = "accounts.User"
        django_get_or_create = ("sso_email_user_id",)
