from random import randint, sample, choice

import pytest
from django.db.utils import IntegrityError
from django.db import transaction

from supply_chains.models import (
    SupplyChainStage,
    SupplyChainStageSection,
)
from supply_chains.models import SupplyChain
from supply_chains.test.factories import (
    SupplyChainFactory,
    SupplyChainStageFactory,
    SupplyChainStageSectionFactory,
)

pytestmark = pytest.mark.django_db


def get_stage_names(n: int):
    values = [x[0] for x in SupplyChainStage.StageName.choices]
    return sample(values, n)


def get_section_names(n: int):
    values = [x[0] for x in SupplyChainStageSection.SectionName.choices]
    return sample(values, n)


@pytest.fixture
def sc_stub():
    SupplyChainFactory.create_batch(5)

    yield SupplyChain.objects.all()


@pytest.fixture
def stage_stub(sc_stub):
    stage_count = 5
    stage_names = get_stage_names(stage_count)

    for i in range(sc_stub.count()):
        order_list = sample(range(10), stage_count)
        for j in range(stage_count):
            SupplyChainStageFactory(
                name=stage_names[j], order=order_list[j], supply_chain=sc_stub[i]
            )

    yield SupplyChainStage.objects.all()


class TestSCStage:
    def test_stage_save_object(self):
        # Arrange
        stage_names = get_stage_names(2)
        order_list = sample(range(10), 2)

        # Act
        for i in range(2):
            SupplyChainStageFactory(name=stage_names[i], order=order_list[i])

        # Assert
        assert SupplyChainStage.objects.count() == 2
        assert SupplyChainStage.objects.distinct("name", "order").count() == 2

    def test_stage_validate_name(self, sc_stub):
        # Arrange
        stage_name = SupplyChainStage.StageName.DELIVERY

        # Act
        SupplyChainStageFactory(name=stage_name, supply_chain=sc_stub[0])

        # Assert
        with transaction.atomic():
            with pytest.raises(IntegrityError, match="duplicate key value violates"):
                SupplyChainStageFactory(name=stage_name, supply_chain=sc_stub[0])
        assert SupplyChainStage.objects.count() == 1

    def test_stage_validate_order(self, sc_stub):
        # Arrange
        order_number = randint(1, 50)

        # Act
        SupplyChainStageFactory(order=order_number, supply_chain=sc_stub[0])

        # Assert
        with transaction.atomic():
            with pytest.raises(IntegrityError, match="duplicate key value violates"):
                SupplyChainStageFactory(order=order_number, supply_chain=sc_stub[0])
        assert SupplyChainStage.objects.count() == 1

    def test_multiple_stage_object(self, sc_stub):
        # Arrange
        stage_names = get_stage_names(4)

        # Act
        for i in range(5):
            order_list = sample(range(10), 4)
            for j in range(4):
                SupplyChainStageFactory(
                    name=stage_names[j], order=order_list[j], supply_chain=sc_stub[i]
                )

        # Assert
        assert SupplyChainStage.objects.count() == 20
        assert (
            SupplyChainStage.objects.filter(supply_chain=sc_stub[choice(range(5))])
            .distinct("order")
            .count()
            == 4
        )
        assert (
            SupplyChainStage.objects.filter(supply_chain=sc_stub[choice(range(5))])
            .distinct("name")
            .count()
            == 4
        )
        assert SupplyChain.objects.count() == 5


class TestSCStageSection:
    def test_secton_save_object(self):
        # Arrange
        sec_names = get_section_names(2)

        # Act
        for i in range(2):
            SupplyChainStageSectionFactory(name=sec_names[i])

        # Assert
        assert SupplyChainStageSection.objects.count() == 2
        assert (
            SupplyChainStageSection.objects.distinct("name", "description").count() == 2
        )

    def test_section_validate_name(self, stage_stub):
        # Arrange
        sec_name = SupplyChainStageSection.SectionName.OVERVIEW

        # Act
        SupplyChainStageSectionFactory(name=sec_name, chain_stage=stage_stub[0])

        # Assert
        with transaction.atomic():
            with pytest.raises(IntegrityError, match="duplicate key value violates"):
                SupplyChainStageSectionFactory(name=sec_name, chain_stage=stage_stub[0])
        assert SupplyChainStageSection.objects.count() == 1

    def test_multiple_section_object(self, stage_stub):
        # Arrange
        sec_names = get_section_names(4)

        # Act
        for i in range(5):
            for j in range(4):
                SupplyChainStageSectionFactory(
                    name=sec_names[j], chain_stage=stage_stub[i]
                )

        # Assert
        assert SupplyChainStageSection.objects.count() == 20
        assert (
            SupplyChainStageSection.objects.filter(
                chain_stage=stage_stub[choice(range(5))]
            )
            .distinct("name")
            .count()
            == 4
        )
        assert (
            SupplyChainStageSection.objects.filter(
                chain_stage=stage_stub[choice(range(5))]
            )
            .distinct("description")
            .count()
            == 4
        )
        assert SupplyChain.objects.count() == 5
