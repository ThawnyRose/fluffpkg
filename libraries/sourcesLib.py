from pathlib import Path
import sqlite3
import json

from libraries.exceptions import (
    MultipleCandidates,
    AlreadySourced,
    SourceAlreadyExists,
    SourceNotFound,
)
from libraries.dataClasses import Candidate, QueryResult, Source
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
    download_url TEXT,
    module_data TEXT
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


def get_source(package: str) -> Candidate | None:
    original_source = query(package)
    # if isinstance(original_source, type(None)):
    if original_source is None:
        return None
    if len(original_source.candidates) != 1:
        candidates = [
            c for c in original_source.candidates if c.source == "github-appimage"
        ]
        if len(candidates) != 1:
            raise MultipleCandidates()
        candidate = candidates[0]
    else:
        candidate = original_source.candidates[0]
    return candidate


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


def add_candidate(
    candidate: Candidate, update: bool = False, update_source: str = ""
) -> None:
    if update:
        cursor.execute(
            "UPDATE candidates SET module = ?, name = ?, package_name = ?, categories = ?, source = ?, download_url = ?, module_data = ? WHERE source = ? AND package_name = ?",
            (
                candidate.module,
                candidate.name,
                candidate.package_name,
                json.dumps(candidate.categories),
                f"{candidate.source.kind}:{candidate.source.url}",
                candidate.download_url,
                json.dumps(candidate.module_data),
                update_source,
                candidate.package_name,
            ),
        )
        conn.commit()
    else:
        if check_existing_source(candidate.package_name):
            raise AlreadySourced(candidate.package_name)

        cursor.execute(
            "INSERT INTO candidates (module, name, package_name, categories, source, download_url, module_data) VALUES (?, ?, ?, ?, ?, ?, ?)",
            (
                candidate.module,
                candidate.name,
                candidate.package_name,
                json.dumps(candidate.categories),
                f"{candidate.source.kind}:{candidate.source.url}",
                candidate.download_url,
                json.dumps(candidate.module_data),
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


def update_categories(package: str, categories: list[str]) -> None:
    cursor.execute(
        "UPDATE candidates SET categories = ? WHERE package_name = ?",
        (json.dumps(categories), package),
    )
    conn.commit()


# def get_module_data(package: str):
#     cursor.execute(
#         "SELECT module_data FROM candidates WHERE package_name = ?",
#         (package,),
#     )
#     match = cursor.fetchall()[0][0]
#     match = {} if match is None else json.loads(match)
#     return match


def set_module_data(package: str, module_data: dict) -> None:
    cursor.execute(
        "UPDATE candidates SET module_data = ? WHERE package_name = ?",
        (json.dumps(module_data), package),
    )
    conn.commit()


def list() -> list[Candidate]:
    cursor.execute("SELECT * FROM candidates")
    rows = cursor.fetchall()
    return [Candidate(*row[1:]) for row in rows]


def add_source(sourcepath: str) -> None:
    if sourcepath.startswith("https://") or sourcepath.startswith("http://"):
        raise NotImplementedError("Remote sources not yet supported")
        source = Source("remote", sourcepath)
    else:
        path = Path(sourcepath)
        if not path.exists():
            print(f"Failed to read source file: file does not exist '{sourcepath}'")
            exit()
        if not path.is_file():
            print(f"Failed to read source file: file is a directory '{sourcepath}'")
            exit()
        with open(path, "r") as f:
            new_source_data = json.load(f)

        source = Source("local", sourcepath)

    cursor.execute(
        "SELECT * FROM sources WHERE kind = ? AND url = ?", (source.kind, source.url)
    )
    rows = cursor.fetchall()
    if len(rows) != 0:
        raise SourceAlreadyExists()

    cursor.execute(
        "INSERT INTO sources (kind, url) VALUES (?, ?)",
        (source.kind, source.url),
    )
    conn.commit()

    for item in new_source_data:
        candidate = Candidate(
            item["module"],
            item["name"],
            item["package_name"],
            item["categories"],
            source,
            item["download_url"],
            item["module_data"],
        )
        try:
            add_candidate(candidate)
        except AlreadySourced:
            print(
                f"Skipping package {candidate.package_name} which already has a source"
            )


def remove_source(sourcepath: str) -> None:
    if sourcepath == "_":
        print("Cannot remove builtin source")
        exit()
    try:
        _id = int(sourcepath)
        cursor.execute("SELECT kind, url FROM sources WHERE id = ?", (_id,))
    except ValueError:
        cursor.execute("SELECT kind, url FROM sources WHERE url = ?", (sourcepath,))

    rows = cursor.fetchall()
    if len(rows) == 0:
        raise SourceNotFound(sourcepath)

    source = Source(*rows[0])
    source_string = str(source)

    cursor.execute(
        "SELECT package_name FROM installed WHERE source = ?", (source_string,)
    )
    rows = cursor.fetchall()
    if len(rows) != 0:
        print("Could not remove source, packages depend on it:")
        for r in rows:
            print("   ", r[0])
        exit()

    try:
        _id = int(sourcepath)
        cursor.execute("DELETE FROM sources WHERE id = ?", (_id,))
    except ValueError:
        cursor.execute("DELETE FROM sources WHERE url = ?", (sourcepath,))
    cursor.execute("DELETE FROM candidates WHERE source = ?", (source_string,))
    conn.commit()


def update_source(sourcepath: str) -> None:
    if sourcepath == "_":
        print("Cannot update builtin source")
        exit()
    try:
        _id = int(sourcepath)
        cursor.execute("SELECT kind, url FROM sources WHERE id = ?", (_id,))
    except ValueError:
        cursor.execute("SELECT kind, url FROM sources WHERE url = ?", (sourcepath,))
    rows = cursor.fetchall()
    if len(rows) == 0:
        raise SourceNotFound(sourcepath)

    source = Source(*rows[0])
    if source.kind == "local":
        path = Path(source.url)
        if not path.exists():
            print(f"Failed to read source file: file does not exist '{source.url}'")
            exit()
        if not path.is_file():
            print(f"Failed to read source file: file is a directory '{source.url}'")
            exit()
        with open(path, "r") as f:
            new_source_data = json.load(f)
    else:
        print("Unhandled source kind (for updates):", source.kind)
        exit()

    for item in new_source_data:
        candidate = Candidate(
            item["module"],
            item["name"],
            item["package_name"],
            item["categories"],
            source,
            item["download_url"],
            item["module_data"],
        )
        add_candidate(candidate, update=True, update_source=str(source))
    print("Source updated")


def list_sources() -> None:
    cursor.execute("SELECT id, kind, url FROM sources")
    rows = cursor.fetchall()
    for r in rows:
        print(f"[{r[0]}] {r[1]} : {r[2]}")
