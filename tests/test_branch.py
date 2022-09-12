from redmine_log_work import issue_id_from_branch_name


def test_id_as_suffix() -> None:
    assert issue_id_from_branch_name("dev-123") == "123"


def test_id_as_prefix_with_type() -> None:
    assert issue_id_from_branch_name("feature/123-foo-bar") == "123"


def test_id_with_type() -> None:
    assert issue_id_from_branch_name("bugfix/123") == "123"


def test_id_as_prefix() -> None:
    assert issue_id_from_branch_name("123-baz-qux") == "123"
