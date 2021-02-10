import factory

from api.accounts.test.factories import GovDepartmentFactory


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
