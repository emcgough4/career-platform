"""Copy every row from one database into another, empty one on the same migration.

Usage: python -m app.copy_data <source_url> <target_url>
"""

import sys

from sqlalchemy import create_engine, func, select, text

import app.models  # noqa: F401  registers every table on Base.metadata
from app.config import normalize_database_url
from app.db import Base

VERSION = text("SELECT version_num FROM alembic_version")


def copy_database(source_url: str, target_url: str) -> dict[str, int]:
    """Copy all tables in foreign-key order inside one target transaction."""
    source = create_engine(normalize_database_url(source_url))
    target = create_engine(normalize_database_url(target_url))
    tables = Base.metadata.sorted_tables
    counts: dict[str, int] = {}
    with source.connect() as src, target.begin() as dst:
        if src.scalar(VERSION) != dst.scalar(VERSION):
            raise ValueError("source and target are on a different Alembic revision; nothing was copied")
        for table in tables:
            if dst.scalar(select(func.count()).select_from(table)):
                raise ValueError(f"{table.name} in the target already has rows; nothing was copied")
        for table in tables:
            rows = [dict(row._mapping) for row in src.execute(select(table))]
            if rows:
                dst.execute(table.insert(), rows)
            counts[table.name] = len(rows)
        if dst.dialect.name == "postgresql":
            # Rows kept their ids, so move each id sequence past the highest one.
            for table in tables:
                if "id" in table.c:
                    dst.execute(text(
                        f"SELECT setval(pg_get_serial_sequence('{table.name}', 'id'), "
                        f"GREATEST(MAX(id), 1), MAX(id) IS NOT NULL) FROM {table.name}"
                    ))
    source.dispose()
    target.dispose()
    return counts


if __name__ == "__main__":
    if len(sys.argv) != 3:
        raise SystemExit("usage: python -m app.copy_data <source_url> <target_url>")
    for name, count in copy_database(sys.argv[1], sys.argv[2]).items():
        print(name, count)
