![Build Status][build-badge]

[build-badge]: https://github.com/pawel-slowik/redmine-log-work/workflows/tests/badge.svg

# redmine-log-work

This is a CLI utility for logging work time in
[Redmine](https://www.redmine.org/) via its REST API.


# Installation

This utility requires Python 3.x.

It is not packaged yet.

You will need to clone this repository and probably add a shell alias, e.g.:

	alias log-work="$HOME/path/redmine_log_work.py"

Only the Python standard library is required, there's no need to install any
additional packages.

If you want to automatically extract issue ID from current
[Git](https://git-scm.com/) branch name, you will also need Git installed.


# Configuration

Copy the included example configuration file into the `$HOME/.config` directory
and edit it to include your Redmine URL and API key. You can also define aliases
for issue IDs.


# Usage

	usage: redmine_log_work.py [-h] issue time activity [comment]

	Log time spent on a Redmine issue.

	positional arguments:
	  issue       issue ID or alias, use . (dot) to extract from current branch name
	  time        amount of time spent, formats accepted:
	              • 15 is 15 minutes,
	              • 1:15 is one hour and 15 minutes
	              • 9:00-10:00 is a time range spanning one hour
	              • 9:00-now is a relative time range
	              • 9:00- and ~9:00 are shortcuts for 9:00-now
	  activity    activity type, can be a shortcut, e.g. CR instead of Code Review
	              as long as it identifies an activity unambiguously
	  comment     optional comment

	options:
	  -h, --help  show this help message and exit

The script displays time and issue details and asks for confirmation before
actually saving a time tracking entry.


# Other tools

This utility is very simple - basically it only covers my single personal use
case. If you're looking for a full blown Redmine CLI, take a look at
[arcli](https://github.com/mightymatth/arcli).


# Tests

Install packages required for running test:

	pip install -U -r requirements-test.txt

Run tests with:

	pytest
