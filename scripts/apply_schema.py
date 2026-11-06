"""Apply sql/001_bronze.sql using the admin login in SUPABASE_ADMIN_URL.

Usage:
    uv run --env-file .env python scripts/apply_schema.py
"""

import os
from pathlib import Path

import psycopg

SQL_FILE = Path(__file__).resolve().parent.parent / "sql" / "001_bronze.sql"

if __name__ == "__main__":
    with psycopg.connect(os.environ["SUPABASE_ADMIN_URL"]) as conn:
        conn.execute(SQL_FILE.read_text())
    print("Schema applied.")
