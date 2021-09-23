from io import StringIO
from unittest import mock

import pytest
from django.core.management import call_command
from django.core.management.base import CommandError

from supply_chains.management.commands import ingestscenarioassessments
from accounts.models import GovDepartment
from supply_chains.models import (
    StrategicAction,
    StrategicActionUpdate,
    SupplyChain,
    ScenarioAssessment,
    NullableRAGRating,
)

from supply_chains.test.data import scenario_assessments
from supply_chains.test.factories import SupplyChainFactory

pytestmark = pytest.mark.django_db


class TestIngestScenarioAssessment:
    @mock.patch(
        "supply_chains.management.commands.ingestscenarioassessments.open",
        mock.mock_open(
            read_data=scenario_assessments.two_full_scenario_assessments_csv
        ),
    )
    def test_source_data_generator_yields_all_lines(self):
        command = ingestscenarioassessments.Command()
        data_read = list(command.source_data)
        # as the generator sends back a final empty thing
        # for the use of `source_assessments` final count will be +1
        assert len(data_read) == 13

    @mock.patch(
        "supply_chains.management.commands.ingestscenarioassessments.open",
        mock.mock_open(
            read_data=scenario_assessments.scenario_assessment_with_transition_period_scenario_csv
        ),
    )
    def test_source_redundant_transition_period_scenario_ignored(self):
        SupplyChainFactory(name="Supply Chain Two")
        command = ingestscenarioassessments.Command()
        assessments = list(command.source_assessments)
        assessment = assessments[0]
        transition_period_values = [
            key for key in assessment.keys() if key.startswith("End_of_transition")
        ]
        assert len(transition_period_values) == 0

    @mock.patch(
        "supply_chains.management.commands.ingestscenarioassessments.open",
        mock.mock_open(
            read_data=scenario_assessments.two_full_scenario_assessments_csv
        ),
    )
    def test_command_execution_imports_scenario_assessments(self):
        supply_chain_one: SupplyChain = SupplyChainFactory(name="Supply Chain One")
        supply_chain_two: SupplyChain = SupplyChainFactory(name="Supply Chain Two")
        call_command("ingestscenarioassessments", "no_value_needed_due_to_mock_open")

        assert supply_chain_one.scenario_assessment
        assert supply_chain_two.scenario_assessment

        scenario_assessment_one: ScenarioAssessment = (
            supply_chain_one.scenario_assessment
        )
        assert (
            scenario_assessment_one.ports_blocked_rag_rating == NullableRAGRating.NONE
        )
        assert (
            scenario_assessment_one.storage_full_impact
            == "One storage full implication"
        )
        assert scenario_assessment_one.labour_shortage_is_critical == False
        assert scenario_assessment_one.demand_spike_critical_scenario == ""

        scenario_assessment_two: ScenarioAssessment = (
            supply_chain_two.scenario_assessment
        )
        assert (
            scenario_assessment_two.ports_blocked_rag_rating == NullableRAGRating.AMBER
        )
        assert (
            scenario_assessment_two.raw_material_shortage_impact
            == "Two raw material shortage implication"
        )
        assert scenario_assessment_two.labour_shortage_is_critical == True
        assert (
            scenario_assessment_two.demand_spike_critical_scenario
            == "Two demand spike critical scenario"
        )

    @mock.patch(
        "supply_chains.management.commands.ingestscenarioassessments.open",
        mock.mock_open(
            read_data=scenario_assessments.two_full_scenario_assessments_csv
        ),
    )
    def test_invalid_supply_chain_names_are_recorded(self):
        command_output = StringIO()
        call_command(
            "ingestscenarioassessments",
            "no_value_needed_due_to_mock_open",
            stdout=command_output,
        )
        output = command_output.getvalue()
        assert "Unrecognised supply chains: 2" in output
        assert "Supply Chain One" in output
        assert "Supply Chain Two" in output
