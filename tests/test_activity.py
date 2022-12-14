import pytest
from redmine_log_work import Activity, match_activity


def test_match_id() -> None:
    activities = [
        Activity(id_=1, name="business analysis"),
        Activity(id_=2, name="development"),
        Activity(id_=3, name="code review"),
    ]
    activity = match_activity("2", activities)
    assert activity == activities[1]


def test_match_name() -> None:
    activities = [
        Activity(id_=1, name="business analysis"),
        Activity(id_=2, name="development"),
        Activity(id_=3, name="code review"),
    ]
    activity = match_activity("code review", activities)
    assert activity == activities[2]


def test_match_case_insensitive_name() -> None:
    activities = [
        Activity(id_=1, name="Business Analysis"),
        Activity(id_=2, name="Development"),
        Activity(id_=3, name="Code Review"),
    ]
    activity = match_activity("code review", activities)
    assert activity == activities[2]


def test_match_partial() -> None:
    activities = [
        Activity(id_=1, name="business analysis"),
        Activity(id_=2, name="development"),
        Activity(id_=3, name="code review"),
    ]
    activity = match_activity("dev", activities)
    assert activity == activities[1]


def test_match_case_insensitive_partial() -> None:
    activities = [
        Activity(id_=1, name="Business Analysis"),
        Activity(id_=2, name="Development"),
        Activity(id_=3, name="Code Review"),
    ]
    activity = match_activity("dev", activities)
    assert activity == activities[1]


def test_match_acronym() -> None:
    activities = [
        Activity(id_=1, name="business analysis"),
        Activity(id_=2, name="development"),
        Activity(id_=3, name="code review"),
    ]
    activity = match_activity("cr", activities)
    assert activity == activities[2]


def test_match_case_insensitive_acronym() -> None:
    activities = [
        Activity(id_=1, name="Business Analysis"),
        Activity(id_=2, name="Development"),
        Activity(id_=3, name="Code Review"),
    ]
    activity = match_activity("cr", activities)
    assert activity == activities[2]


def test_match_not_found() -> None:
    activities = [
        Activity(id_=1, name="business analysis"),
        Activity(id_=2, name="development"),
        Activity(id_=3, name="code review"),
    ]
    with pytest.raises(Exception):
        match_activity("foo", activities)


def test_match_inconclusive() -> None:
    activities = [
        Activity(id_=1, name="business analysis"),
        Activity(id_=2, name="development"),
        Activity(id_=3, name="code review"),
    ]
    with pytest.raises(Exception):
        match_activity("de", activities)
