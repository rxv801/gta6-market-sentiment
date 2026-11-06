import importlib.util
from pathlib import Path

import pytest

spec = importlib.util.spec_from_file_location(
    "provision_collector", Path(__file__).parent.parent / "scripts" / "provision_collector.py"
)
provision = importlib.util.module_from_spec(spec)
spec.loader.exec_module(provision)


def test_collector_url_swaps_login():
    url = provision.collector_url("postgresql://postgres.abc:adminpw@host.pooler.supabase.com:5432/postgres", "newpw")
    assert url == "postgresql://collector.abc:newpw@host.pooler.supabase.com:5432/postgres"


def test_collector_url_rejects_direct_login():
    with pytest.raises(ValueError, match="Session pooler"):
        provision.collector_url("postgresql://postgres:adminpw@db.abc.supabase.co:5432/postgres", "newpw")
