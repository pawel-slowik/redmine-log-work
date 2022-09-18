#!/usr/bin/env python3

from dataclasses import dataclass
from datetime import date, datetime
from typing import Optional, Iterable
import os.path
import string
import subprocess
import argparse


@dataclass(frozen=True)
class Issue:
    id_: str
    title: str
    project: str

    @staticmethod
    def id_is_valid(check: str) -> bool:
        return check.strip(string.digits) == ""


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
    parts = branch_name.split("/", 1).pop().split("-")
    for index in (0, -1):
        if Issue.id_is_valid(parts[index]):
            return parts[index]
    raise ValueError(f"can not extract issue ID from branch name: `{branch_name}`")


def get_issue(id_: str) -> Issue:
    # TODO: fetch from REST API
    return Issue(id_=id_, title="issue title", project="project title")


def branch_name_from_directory(directory_name: str) -> str:
    process = subprocess.run(
        ["git", "status", "-z", "--porcelain=v2", "--branch"],
        cwd=directory_name,
        capture_output=True,
        check=True,
    )
    parts = process.stdout.split(b"\0")
    for part in parts:
        if part.startswith(b"# branch.head "):
            return part[14:].decode("utf-8")
    raise ValueError(f"can not read branch name in directory: `{directory_name}`")


def current_directory() -> str:
    return os.path.abspath(os.path.curdir)


def hours_from_description(date_time: datetime, description: str) -> float:

    def from_range(date_time: datetime, description: str) -> float:

        def dt_hour_minute(date_time: datetime, timespec: str) -> datetime:
            hour, minute = map(int, timespec.split(":", 1))
            return date_time.replace(hour=hour, minute=minute, second=0, microsecond=0)

        if description and description[0] == "~":
            return from_range(date_time, description[1:] + "-now")
        parts = description.split("-", 1)
        begin = dt_hour_minute(date_time, parts[0])
        end = date_time if parts[1] in ("", "now") else dt_hour_minute(date_time, parts[1])
        if begin >= end:
            raise ValueError(f"time range must not end before it begins: `{description}`")
        return (end - begin).total_seconds() / 3600

    def from_length(description: str) -> float:
        parts = description.split(":", 1)
        minutes = int(parts.pop())
        if minutes < 1:
            raise ValueError(f"can not log an interval `{description}` shorter than one minute")
        if not parts:
            return minutes / 60
        if minutes > 59:
            raise ValueError(
                f"number of minutes must be lower than 60" \
                f" for the hours:minutes format: `{description}`"
            )
        hours = 0 if parts == [""] else int(parts.pop())
        if hours < 0:
            raise ValueError(f"can not log negative hours: `{description}`")
        return hours + minutes / 60

    if "-" in description or "~" in description:
        return from_range(date_time, description)
    return from_length(description)


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
