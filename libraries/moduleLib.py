from libraries.dataClasses import Candidate, Installation

# from libraries import manageInstalledLib
# from libraries import sourcesLib


_API_LIST = {}
_COMMANDS = {}


def register(module: str, funcs: dict) -> None:
    global _COMMANDS
    _API_LIST[module] = funcs
    _COMMANDS = {**_COMMANDS, **(funcs.get("commands", {}))}


def install(module: str, candidate: Candidate, nolauncher=False, path=False) -> None:
    _API_LIST[module]["install"](candidate, nolauncher, path)


def remove(module: str, installation: Installation) -> None:
    _API_LIST[module]["remove"](installation)


def commandNames() -> list[str]:
    return list(_COMMANDS.keys())


def command(module: str, cmd_args: dict) -> None:
    _COMMANDS[module](cmd_args)
