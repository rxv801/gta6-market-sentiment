from pathlib import Path

import pytest

from maintenance.retention import DEFAULT_KEEP_DAYS, MAX_KEEP_DAYS, keep_days_from

SQL = (Path(__file__).parent.parent / "sql" / "003_retention.sql").read_text()


@pytest.mark.parametrize("value", [None, ""])
def test_unset_means_the_strict_30_day_rule(value):
    assert keep_days_from(value) == DEFAULT_KEEP_DAYS == 30


def test_approved_limit_is_36_months():
    assert keep_days_from("1095") == MAX_KEEP_DAYS


@pytest.mark.parametrize("value", ["0", "-5", "1096"])
def test_out_of_range_is_refused(value):
    with pytest.raises(ValueError, match="between 1 and 1095"):
        keep_days_from(value)


def test_database_function_only_touches_youtube_and_checks_range():
    assert "where source = 'youtube'" in SQL
    assert "keep_days < 1 or keep_days > 1095" in SQL
    assert "security definer" in SQL
