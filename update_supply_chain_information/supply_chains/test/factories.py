import factory.fuzzy
from datetime import date

from accounts.test.factories import GovDepartmentFactory, UserFactory
from supply_chains.models import (
    StrategicAction,
    RAGRating,
    SupplyChain,
    SupplyChainStage,
    SupplyChainStageSection,
)


class SupplyChainFactory(factory.django.DjangoModelFactory):
    name = factory.Sequence(lambda n: f"Product {n}")
    description = factory.Faker("paragraph", nb_sentences=6)
    last_submission_date = factory.Faker("date_object")
    gov_department = factory.SubFactory(GovDepartmentFactory)
    contact_name = factory.Faker("name")
    contact_email = factory.Faker("email")
    vulnerability_status = factory.fuzzy.FuzzyChoice(RAGRating)
    vulnerability_status_disagree_reason = factory.Faker("sentence")
    risk_severity_status_disagree_reason = factory.Faker("sentence")

    class Meta:
        model = "supply_chains.SupplyChain"


class StrategicActionFactory(factory.django.DjangoModelFactory):
    name = factory.Sequence(lambda n: f"Strategic action {n}")
    start_date = factory.Faker("date_object")
    description = factory.Faker("paragraph", nb_sentences=6)
    impact = factory.Faker("text")
    category = factory.fuzzy.FuzzyChoice(StrategicAction.Category)
    geographic_scope = factory.fuzzy.FuzzyChoice(StrategicAction.GeographicScope)
    supporting_organisations = ["DIT"]
    target_completion_date = factory.Faker("date_object")
    is_archived = False
    specific_related_products = factory.Faker("text")
    other_dependencies = factory.Faker("text")
    supply_chain = factory.SubFactory(SupplyChainFactory)

    class Meta:
        model = "supply_chains.StrategicAction"


class StrategicActionUpdateFactory(factory.django.DjangoModelFactory):
    submission_date = factory.Faker("date_object")
    date_created = date.today()
    content = factory.Faker("text")
    implementation_rag_rating = factory.fuzzy.FuzzyChoice(
        RAGRating,
    )
    user = factory.SubFactory(UserFactory)
    strategic_action = factory.SubFactory(StrategicActionFactory)
    supply_chain = factory.SubFactory(SupplyChainFactory)

    class Meta:
        model = "supply_chains.StrategicActionUpdate"


class SupplyChainStageFactory(factory.django.DjangoModelFactory):
    name = factory.fuzzy.FuzzyChoice(
        SupplyChainStage.StageName,
    )
    supply_chain = factory.SubFactory(SupplyChainFactory)
    order = factory.Faker("pyint", min_value=0, max_value=50)

    class Meta:
        model = "supply_chains.SupplyChainStage"


class SupplyChainStageSectionFactory(factory.django.DjangoModelFactory):
    name = factory.fuzzy.FuzzyChoice(
        SupplyChainStageSection.SectionName,
    )
    chain_stage = factory.SubFactory(SupplyChainStageFactory)
    description = factory.Faker("sentence")

    class Meta:
        model = "supply_chains.SupplyChainStageSection"
