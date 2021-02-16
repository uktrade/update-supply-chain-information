import factory

from api.accounts.test.factories import GovDepartmentFactory, UserFactory


class SupplyChainFactory(factory.django.DjangoModelFactory):
    name = "Product"
    last_submission_date = factory.Faker("date_object")
    gov_department = factory.SubFactory(GovDepartmentFactory)

    class Meta:
        model = "supply_chain_update.SupplyChain"


class StrategicActionFactory(factory.django.DjangoModelFactory):
    name = factory.Sequence(lambda n: f"Strategic action {n}")
    start_date = factory.Faker("date_object")
    description = factory.Faker("sentence")
    is_archived = False
    supply_chain = factory.SubFactory(SupplyChainFactory)

    class Meta:
        model = "supply_chain_update.StrategicAction"


class StrategicActionUpdateFactory(factory.django.DjangoModelFactory):
    submission_date = factory.Faker("date_object")
    content = factory.Faker("sentence")
    implementation_rag_rating = "Green"
    user = factory.SubFactory(UserFactory)
    strategic_action = factory.SubFactory(StrategicActionFactory)
    supply_chain = factory.SubFactory(SupplyChainFactory)

    class Meta:
        model = "supply_chain_update.StrategicActionUpdate"
