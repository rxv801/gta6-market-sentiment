"""Apply every file in sql/ in name order using the admin login in SUPABASE_ADMIN_URL.

Each file is safe to re-run.

Usage:
    uv run --env-file .env python scripts/apply_schema.py
"""

import os
from pathlib import Path

import psycopg

SQL_DIR = Path(__file__).resolve().parent.parent / "sql"

if __name__ == "__main__":
    with psycopg.connect(os.environ["SUPABASE_ADMIN_URL"]) as conn:
        for sql_file in sorted(SQL_DIR.glob("*.sql")):
            conn.execute(sql_file.read_text())
            print(f"Applied {sql_file.name}")
