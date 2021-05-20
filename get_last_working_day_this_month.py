#!/usr/bin/env python3

from datetime import date

from defend_data_capture.supply_chains.utils import (
    get_last_day_of_this_month,
    get_last_working_day_of_a_month,
)


def get_date_suffix(day):
    if 4 <= day <= 20 or 24 <= day <= 30:
        return "th"
    else:
        return ["st", "nd", "rd"][day % 10 - 1]


def get_formatted_deadline():
    deadline = get_last_working_day_of_a_month(get_last_day_of_this_month())
    suffix = get_date_suffix(deadline.day)
    print(deadline.strftime(f"%A %d{suffix} %B %Y"))


if __name__ == "__main__":
    get_formatted_deadline()
