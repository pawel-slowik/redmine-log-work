#!/usr/bin/env python3

from dataclasses import dataclass
from datetime import date, datetime
from typing import Optional, Iterable, Any
import os.path
import subprocess
import configparser
import urllib.parse
import urllib.request
import json
import argparse


@dataclass(frozen=True)
class Issue:
    id_: int
    title: str
    project: str


@dataclass(frozen=True)
class Activity:
    id_: int
    name: str

    def matches(self, search: str) -> bool:
        if str(self.id_) == search:
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


@dataclass(frozen=True)
class ApiConfig:
    url: str
    key: Optional[str]


@dataclass(frozen=True)
class ApiResponse:
    status: int
    data: Any


def issue_id_from_description(description: str) -> int:
    if description == ".":
        return issue_id_from_branch_name(branch_name_from_directory(current_directory()))
    return int(description)


def issue_id_from_branch_name(branch_name: str) -> int:
    parts = branch_name.split("/", 1).pop().split("-")
    for index in (0, -1):
        try:
            return int(parts[index])
        except ValueError:
            pass
    raise ValueError(f"can not extract issue ID from branch name: `{branch_name}`")


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
        hours = None if parts in ([], [""]) else int(parts.pop())
        if minutes < 0:
            raise ValueError(f"number of minutes must not be negative: `{description}`")
        if hours is not None and hours < 0:
            raise ValueError(f"number of hours must not be negative: `{description}`")
        if hours is None:
            if minutes < 1:
                raise ValueError(f"can not log an interval `{description}` shorter than one minute")
            return minutes / 60
        if minutes > 59:
            raise ValueError(
                f"number of minutes must be lower than 60" \
                f" for the hours:minutes format: `{description}`"
            )
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


def get_issue(id_: int) -> Issue:
    issue = api_request("/issues/" + str(id_)).data["issue"]
    return Issue(id_=id_, title=issue["subject"], project=issue["project"]["name"])


def list_allowed_activities() -> Iterable[Activity]:
    activities = api_request("/enumerations/time_entry_activities").data["time_entry_activities"]
    return [Activity(id_=activity["id"], name=activity["name"]) for activity in activities]


def add_time_entry(time_entry: TimeEntry) -> None:
    time_entry_data = {
        "issue_id": time_entry.issue.id_,
        "spent_on": time_entry.date.isoformat(),
        "hours": time_entry.hours,
        "activity_id": time_entry.activity.id_,
    }
    if time_entry.comment:
        time_entry_data["comments"] = time_entry.comment
    response = api_request("/time_entries", {"time_entry": time_entry_data})
    if response.status != 201:
        raise ValueError(f"unexpected API response status: `{response.status}`")


def api_request(endpoint: str, data: Optional[Any]=None) -> ApiResponse:
    config = api_config()
    endpoint_url = urllib.parse.urljoin(config.url, endpoint + ".json")
    request = urllib.request.Request(
        endpoint_url,
        json.dumps(data).encode("ascii") if data else None
    )
    if data:
        request.add_header("Content-Type", "application/json")
    if config.key:
        request.add_header("X-Redmine-API-Key", config.key)
    with urllib.request.urlopen(request) as response:
        return ApiResponse(status=response.code, data=json.loads(response.read()))


def api_config() -> ApiConfig:
    cfg = configparser.ConfigParser()
    cfg.read(os.path.expanduser("~/.config/redmine_log_work.ini"))
    return ApiConfig(url=cfg.get("api", "url"), key=cfg.get("api", "key", fallback=None))


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
