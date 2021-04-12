import pytest

from datetime import date

from supply_chains.utils import (
    get_last_working_day_of_a_month,
    get_last_working_day_of_previous_month,
)


@pytest.mark.parametrize(
    ("input_date, expected_date"),
    (
        (date(2021, 3, 31), date(2021, 3, 31)),
        (date(2021, 2, 28), date(2021, 2, 26)),
        (date(2021, 5, 31), date(2021, 5, 28)),
    ),
)
def test_get_last_working_day_of_a_month(input_date, expected_date):
    assert get_last_working_day_of_a_month(input_date) == expected_date
