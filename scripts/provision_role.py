"""Give a database role a new random password and store its login as a GitHub secret.

The password is never printed. Re-running rotates it.

Usage:
    uv run --env-file .env python scripts/provision_role.py collector DATABASE_URL
    uv run --env-file .env python scripts/provision_role.py monitor MONITOR_DATABASE_URL
"""

import argparse
import os
import secrets
import subprocess
from urllib.parse import urlsplit, urlunsplit

import psycopg
from psycopg import sql

ROLES = {"collector", "monitor"}


def role_url(admin_url: str, role: str, password: str) -> str:
    """Swap the admin login in a Session pooler URL for another role's login."""
    parts = urlsplit(admin_url)
    _, _, project_ref = parts.username.partition(".")
    if not project_ref:
        raise ValueError("Expected a Session pooler URL with a postgres.<project-ref> username")
    netloc = f"{role}.{project_ref}:{password}@{parts.hostname}:{parts.port}"
    return urlunsplit((parts.scheme, netloc, parts.path, parts.query, parts.fragment))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("role", choices=sorted(ROLES))
    parser.add_argument("secret_name")
    args = parser.parse_args()

    admin_url = os.environ["SUPABASE_ADMIN_URL"]
    password = secrets.token_hex(32)
    with psycopg.connect(admin_url) as conn:
        conn.execute(sql.SQL("alter role {} password {}").format(sql.Identifier(args.role), sql.Literal(password)))
    subprocess.run(
        ["gh", "secret", "set", args.secret_name],
        input=role_url(admin_url, args.role, password),
        text=True,
        check=True,
    )
    print(f"{args.role} password set and {args.secret_name} stored in GitHub secrets.")
