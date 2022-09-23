from datetime import datetime
from redmine_log_work import hours_from_description


NOW = datetime(year=2022, month=6, day=17, hour=10)


def test_minutes_only() -> None:
    assert hours_from_description(NOW, ":45") == 0.75
    assert hours_from_description(NOW, "30") == 0.5


def test_hours_and_minutes() -> None:
    assert hours_from_description(NOW, "0:15") == 0.25
    assert hours_from_description(NOW, "3:12") == 3.2
    assert hours_from_description(NOW, "4:00") == 4


def test_absolute_range() -> None:
    assert hours_from_description(NOW, "8:30-9:50") == 1 + 1 / 3


def test_relative_range() -> None:
    assert hours_from_description(NOW, "8:00-now") == 2


def test_relative_range_default() -> None:
    assert hours_from_description(NOW, "8:30-") == 1.5


def test_relative_range_default_mnemonic() -> None:
    assert hours_from_description(NOW, "~9:00") == 1
