import importlib.util
from pathlib import Path

import pytest

spec = importlib.util.spec_from_file_location(
    "provision_role", Path(__file__).parent.parent / "scripts" / "provision_role.py"
)
provision = importlib.util.module_from_spec(spec)
spec.loader.exec_module(provision)

ADMIN = "postgresql://postgres.abc:adminpw@host.pooler.supabase.com:5432/postgres"


@pytest.mark.parametrize("role", ["collector", "monitor"])
def test_role_url_swaps_login(role):
    assert (
        provision.role_url(ADMIN, role, "newpw")
        == f"postgresql://{role}.abc:newpw@host.pooler.supabase.com:5432/postgres"
    )


def test_role_url_rejects_direct_login():
    with pytest.raises(ValueError, match="Session pooler"):
        provision.role_url("postgresql://postgres:adminpw@db.abc.supabase.co:5432/postgres", "collector", "newpw")
