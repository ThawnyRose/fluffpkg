import json


class Source:
    def __init__(self, kind: str, url: str):
        self.kind = kind
        self.url = url

    def __str__(self):
        return f"{self.kind}:{self.url}"


class Installation:
    categories: list[str]
    source: Source

    def __init__(
        self,
        package_name: str,
        name: str,
        version: str,
        launcher: bool,
        path: bool,
        module: str,
        source: Source | str,
        executable_path: str,
        categories: list[str] | str,
    ):
        self.name = name
        self.version = version
        self.package_name = package_name
        self.launcher = bool(launcher)
        self.path = bool(path)
        self.module = module
        self.source = (
            source if isinstance(source, Source) else Source(*(source.split(":", 1)))
        )
        self.executable_path = executable_path
        self.categories = (
            json.loads(categories) if isinstance(categories, str) else categories
        )


class Candidate:
    categories: list[str]
    source: Source

    def __init__(
        self,
        module: str,
        name: str,
        package_name: str,
        categories: str | list[str],
        source: Source | str,
        download_url: str,
    ):
        self.module = module
        self.name = name
        self.package_name = package_name
        self.categories = (
            json.loads(categories) if isinstance(categories, str) else categories
        )
        self.source = (
            source if isinstance(source, Source) else Source(*(source.split(":", 1)))
        )
        self.download_url = download_url


class QueryResult:
    def __init__(self, kind: str, candidates: list[Candidate]):
        self.kind = kind
        self.candidates = candidates
