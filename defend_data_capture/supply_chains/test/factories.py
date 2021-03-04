import factory
import factory.fuzzy

from accounts.test.factories import GovDepartmentFactory, UserFactory
from supply_chains.models import StrategicAction, StrategicActionUpdate


class SupplyChainFactory(factory.django.DjangoModelFactory):
    name = "Product"
    last_submission_date = factory.Faker("date_object")
    gov_department = factory.SubFactory(GovDepartmentFactory)

    class Meta:
        model = "supply_chains.SupplyChain"


class StrategicActionFactory(factory.django.DjangoModelFactory):
    name = factory.Sequence(lambda n: f"Strategic action {n}")
    start_date = factory.Faker("date_object")
    description = factory.Faker("sentence")
    impact = factory.Faker("sentence")
    category = factory.fuzzy.FuzzyChoice(StrategicAction.Category)
    geographic_scope = factory.fuzzy.FuzzyChoice(StrategicAction.GeographicScope)
    supporting_organisations = factory.fuzzy.FuzzyChoice(StrategicAction.SupportingOrgs)
    target_completion_date = factory.Faker("date_object")
    is_archived = False
    supply_chain = factory.SubFactory(SupplyChainFactory)

    class Meta:
        model = "supply_chains.StrategicAction"


class StrategicActionUpdateFactory(factory.django.DjangoModelFactory):
    submission_date = factory.Faker("date_object")
    content = factory.Faker("sentence")
    implementation_rag_rating = factory.fuzzy.FuzzyChoice(
        StrategicActionUpdate.RAGRating,
    )
    user = factory.SubFactory(UserFactory)
    strategic_action = factory.SubFactory(StrategicActionFactory)
    supply_chain = factory.SubFactory(SupplyChainFactory)

    class Meta:
        model = "supply_chains.StrategicActionUpdate"
