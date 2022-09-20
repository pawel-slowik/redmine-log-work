import subprocess
from redmine_log_work import issue_id_from_branch_name, branch_name_from_directory


def test_id_as_suffix() -> None:
    assert issue_id_from_branch_name("dev-123") == 123


def test_id_as_prefix_with_type() -> None:
    assert issue_id_from_branch_name("feature/123-foo-bar") == 123


def test_id_with_type() -> None:
    assert issue_id_from_branch_name("bugfix/123") == 123


def test_id_as_prefix() -> None:
    assert issue_id_from_branch_name("123-baz-qux") == 123


def test_name_can_be_read() -> None:
    name = branch_name_from_directory(".")
    assert name
    assert isinstance(name, str)


def test_name_is_parsed_correctly(mocker) -> None:
    git_info = (
        b"# branch.oid b57a1c3bc3c7c8de6792863f4b91f155c686c419\0"
        b"# branch.head master\0"
        b"1 .M N... 100644 100644 100644 "
        b"2bdaa2bde719e7781828c7fa6da29172ac26ea16 "
        b"2bdaa2bde719e7781828c7fa6da29172ac26ea16 "
        b"tests/test_branch.py\0"
        b"? .coverage\0"
        b"? README.md\0"
    )
    process = subprocess.CompletedProcess([], 0, stdout=git_info)
    mocker.patch("subprocess.run", return_value=process)
    name = branch_name_from_directory(".")
    assert name == "master"
