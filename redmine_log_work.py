#!/usr/bin/env python3

from dataclasses import dataclass
from datetime import date, datetime
from typing import Optional, Iterable
import os.path
import argparse


@dataclass(frozen=True)
class Issue:
    id_: str
    title: str
    project: str


@dataclass(frozen=True)
class Activity:
    id_: str
    name: str

    def matches(self, search: str) -> bool:
        if self.id_ == search:
            return True
        if self.name == search:
            return True
        words = self.name.split()
        for word in words:
            if search in word:
                return True
        acronym = "".join(word[0] for word in words)
        if acronym == search:
            return True
        return False


@dataclass(frozen=True)
class TimeEntry:
    issue: Issue
    date: date
    hours: float
    activity: Activity
    comment: Optional[str]

    def describe(self) -> Iterable[str]:
        labels_and_values = [
            ("issue ID", f"#{self.issue.id_}"),
            ("issue title", self.issue.title),
            ("project", self.issue.project),
            ("date", self.date),
            ("time spent", f"{self.hours} hours"),
            ("activity", self.activity.name),
        ]
        if self.comment:
            labels_and_values.append(("comment", self.comment))
        return (f"{label:<11}: {value}" for (label, value) in labels_and_values)


def issue_id_from_description(description: str) -> str:
    if description == ".":
        return issue_id_from_branch_name(branch_name_from_directory(current_directory()))
    return description


def issue_id_from_branch_name(branch_name: str) -> str:
    # TODO: implement
    return "456"


def get_issue(id_: str) -> Issue:
    # TODO: fetch from REST API
    return Issue(id_=id_, title="issue title", project="project title")


def branch_name_from_directory(directory_name: str) -> str:
    # TODO: implement
    return "bugfix-456"


def current_directory() -> str:
    return os.path.abspath(os.path.curdir)


def hours_from_description(date_time: datetime, description: str) -> float:
    # TODO: implement
    return 1.2


def lookup_activity(description: str) -> Activity:
    return match_activity(description, list_allowed_activities())


def match_activity(search: str, activities: Iterable[Activity]) -> Activity:
    matching_activities = set(
        activity for activity in activities if activity.matches(search)
    )
    count = len(matching_activities)
    if count == 1:
        return matching_activities.pop()
    raise ValueError(f"{'multiple' if count else 'no'} activities matching `{search}`")


def list_allowed_activities() -> Iterable[Activity]:
    # TODO: fetch from REST API
    return [
        Activity(id_="1", name="business analysis"),
        Activity(id_="2", name="development"),
        Activity(id_="3", name="code review"),
    ]


def add_time_entry(time_entry: TimeEntry) -> None:
    # TODO: implement via REST API
    pass


def main() -> None:
    parser = argparse.ArgumentParser(description="Log time spent on a Redmine issue.")
    parser.add_argument("issue", help="issue ID")
    parser.add_argument("time", help="amount of time spent, e.g. 1:30")
    parser.add_argument("activity", help="activity type")
    parser.add_argument("comment", nargs="?", help="optional comment")
    args = parser.parse_args()

    issue = get_issue(issue_id_from_description(args.issue))
    activity = lookup_activity(args.activity)
    time_entry = TimeEntry(
        issue=issue,
        date=date.today(),
        hours=hours_from_description(datetime.now(), args.time),
        activity=activity,
        comment=args.comment,
    )

    for line in time_entry.describe():
        print(line)
    answer = input("confirm time entry? ")
    if answer.lower() in ("y", "yes"):
        add_time_entry(time_entry)
        print("added")
    else:
        print("cancelled")


if __name__ == "__main__":
    main()
