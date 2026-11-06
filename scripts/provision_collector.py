"""Give the collector role a new random password and store its login as a GitHub secret.

The password is never printed. Re-running rotates it.

Usage:
    uv run --env-file .env python scripts/provision_collector.py
"""

import os
import secrets
import subprocess
from urllib.parse import urlsplit, urlunsplit

import psycopg
from psycopg import sql


def collector_url(admin_url: str, password: str) -> str:
    """Swap the admin login in a Session pooler URL for the collector login."""
    parts = urlsplit(admin_url)
    _, _, project_ref = parts.username.partition(".")
    if not project_ref:
        raise ValueError("Expected a Session pooler URL with a postgres.<project-ref> username")
    netloc = f"collector.{project_ref}:{password}@{parts.hostname}:{parts.port}"
    return urlunsplit((parts.scheme, netloc, parts.path, parts.query, parts.fragment))


if __name__ == "__main__":
    admin_url = os.environ["SUPABASE_ADMIN_URL"]
    password = secrets.token_hex(32)
    with psycopg.connect(admin_url) as conn:
        conn.execute(sql.SQL("alter role collector password {}").format(sql.Literal(password)))
    subprocess.run(
        ["gh", "secret", "set", "DATABASE_URL"], input=collector_url(admin_url, password), text=True, check=True
    )
    print("Collector password set and DATABASE_URL stored in GitHub secrets.")
