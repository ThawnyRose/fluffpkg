import json

from tabulate import tabulate


class Source:
    def __init__(self, kind: str, url: str):
        self.kind = kind
        self.url = url

    def __str__(self):
        return f"{self.kind}:{self.url}"


class Installation:
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
        version_locked: bool,
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
        self.version_locked = version_locked


class Candidate:
    categories: list[str]
    source: Source
    module_data: dict

    def __init__(
        self,
        module: str,
        name: str,
        package_name: str,
        categories: str | list[str],
        source: Source | str,
        download_url: str,
        module_data: dict | str,
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
        if isinstance(module_data, str):
            if module_data == "":
                self.module_data = {}
            else:
                self.module_data = json.loads(module_data)
        else:
            self.module_data = module_data


class QueryResult:
    def __init__(self, kind: str, candidates: list[Candidate]):
        self.kind = kind
        self.candidates = candidates


## ArgumentsLib:


class Arg:
    name: str
    help: str

    def usage(self) -> str:
        return "ERROR"


class FlagArg(Arg):
    value: bool = False

    def __init__(self, short: str, name: str, help: str):
        self.short = short
        self.name = name
        self.help = help

    def usage(self) -> str:
        return f"[{self.name}]"


class ValueArg(Arg):
    value: str | None = None

    def __init__(self, short: str, name: str, help: str):
        self.short = short
        self.name = name
        self.help = help

    def usage(self) -> str:
        return f"[{self.name} = ]"


class PosArg(Arg):
    def __init__(self, name: str, help: str, optional: bool = False):
        self.name = name
        self.optional = optional
        self.help = help

    def usage(self) -> str:
        return f"[{self.name}]" if self.optional else f"<{self.name}>"


class PosArgs(Arg):
    values: list[str] = []

    def __init__(self, name: str, help: str, optional: bool = False):
        self.name = name
        self.optional = optional
        self.help = help

    def usage(self) -> str:
        return f"[{self.name}...]" if self.optional else f"<{self.name}...>"


class Command:
    def __init__(self, name: str, help: str, args: list[Arg]):
        self.name = name
        self.help = help
        self.args = args

    def usage(self) -> str:
        output = f"Usage: {self.name} {' '.join(a.usage() for a in self.args)}\n"
        if len(self.args) != 0:
            output += "Arguments:\n"
        table_data = [["", arg.name, "", "", arg.help] for arg in self.args]
        output += tabulate(table_data, tablefmt="plain")
        return output

    def __repr__(self):
        return self.name


class CmdArg(Arg):
    def __init__(self, name: str, help: str, cmds: list[Command]):
        self.name = name
        self.cmds = cmds
        self.handled = False
        self.help = help

    def usage(self) -> str:
        output = f"<{self.name}> ...\n"
        output += "Attributes:\n"

        table_data = [["", command.name, "", "", command.help] for command in self.cmds]
        output += tabulate(table_data, tablefmt="plain")

        return output
