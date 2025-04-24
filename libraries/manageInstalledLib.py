from pathlib import Path
import sqlite3
import json

from libraries.dataClasses import Candidate, Installation

db_path = Path("~/.fluffpkg/database.sqlite3").expanduser()

conn = sqlite3.connect(db_path)
cursor = conn.cursor()

cursor.execute(
    """
CREATE TABLE IF NOT EXISTS installed (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    package_name TEXT UNIQUE NOT NULL,
    name TEXT,
    version TEXT,
    launcher BOOL,
    path BOOL,
    module TEXT,
    source TEXT,
    executable_path TEXT,
    categories TEXT
)
"""
)
conn.commit()


def mark_installed(candidate: Candidate, version: str, executable_path: str):
    cursor.execute(
        "INSERT INTO installed (package_name, name, version, launcher, path, module, source, executable_path, categories) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
        (
            candidate.package_name,
            candidate.name,
            version,
            False,
            False,
            candidate.module,
            candidate.source.__str__(),
            executable_path,
            json.dumps(candidate.categories),
        ),
    )
    conn.commit()


def unmark_installed(package: str) -> None:
    cursor.execute("DELETE FROM installed WHERE package_name = ?", (package,))
    conn.commit()


def check_installed(candidate: Candidate | str) -> bool:
    package = candidate.package_name if isinstance(candidate, Candidate) else candidate
    return query(package) is not None


def query(package: str) -> None | Installation:
    cursor.execute("SELECT * FROM installed WHERE package_name = ?", (package,))
    matches = cursor.fetchall()
    if len(matches) == 0:
        return None
    return Installation(*matches[0][1:])


def list() -> list[Installation]:
    cursor.execute("SELECT * FROM installed")
    rows = cursor.fetchall()
    return [Installation(*row[1:]) for row in rows]


def mark_attribute(package: str, name: str, value) -> None:
    if name == "launcher":
        cursor.execute(
            "UPDATE installed SET launcher = ? WHERE package_name = ?",
            (bool(value), package),
        )
        conn.commit()
        return

    print(
        f"Internal Error: Installation record {name} does not exist or cannot be changed by the mark_attribute function."
    )
    exit()
