from pathlib import Path
import sqlite3
import json

from libraries.dataClasses import Candidate, QueryResult
from libraries import manageInstalledLib

db_path = Path("~/.fluffpkg/database.sqlite3").expanduser()

conn = sqlite3.connect(db_path)
cursor = conn.cursor()

cursor.execute(
    """
CREATE TABLE IF NOT EXISTS candidates (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    module TEXT,
    name TEXT,
    package_name TEXT UNIQUE NOT NULL,
    categories TEXT,
    source TEXT,
    download_url TEXT
)
"""
)
cursor.execute(
    """
CREATE TABLE IF NOT EXISTS sources (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    kind TEXT,
    url TEXT
)
"""
)
conn.commit()


def query(package: str) -> None | QueryResult:
    cursor.execute("SELECT * FROM candidates WHERE package_name = ?", (package,))
    matches = cursor.fetchall()
    if len(matches) != 0:
        return QueryResult("found", [Candidate(*match[1:]) for match in matches])

    cursor.execute(
        "SELECT * FROM candidates WHERE package_name LIKE ? OR name LIKE ?",
        ("%" + package + "%", "%" + package + "%"),
    )
    matches = cursor.fetchall()
    if len(matches) != 0:
        return QueryResult(
            "strong_recommend", [Candidate(*match[1:]) for match in matches]
        )

    return None


def check_existing_source(package: str) -> bool:
    q = query(package)
    return type(q) is QueryResult and q.kind == "found"


def add_candidate(candidate: Candidate, failExists: bool = True) -> None:
    if check_existing_source(candidate.package_name):
        if failExists:
            print(
                f"Package '{candidate.package_name}' is already sourced. Try `install`."
            )
            exit()
        else:
            return

    cursor.execute(
        "INSERT INTO candidates (module, name, package_name, categories, source, download_url) VALUES (?, ?, ?, ?, ?, ?)",
        (
            candidate.module,
            candidate.name,
            candidate.package_name,
            json.dumps(candidate.categories),
            f"{candidate.source.kind}:{candidate.source.url}",
            candidate.download_url,
        ),
    )
    conn.commit()


def remove_candidate(package: str) -> None:
    if not check_existing_source(package):
        print(f"Package '{package}' isn't sourced.")
        exit()
    if manageInstalledLib.check_installed(package):
        print(f"Cannot remove installation candidate for installed package '{package}'")
        exit()

    cursor.execute(
        "DELETE FROM candidates WHERE package_name = ?",
        (package,),
    )
    conn.commit()


def list() -> list[Candidate]:
    cursor.execute("SELECT * FROM candidates")
    rows = cursor.fetchall()
    return [Candidate(*row[1:]) for row in rows]
