from libraries.dataClasses import Candidate, Installation

# from libraries import manageInstalledLib
# from libraries import sourcesLib


_API_LIST = {}
_COMMANDS = {}


def register(module: str, funcs: dict) -> None:
    global _COMMANDS
    _API_LIST[module] = funcs
    _COMMANDS = {**_COMMANDS, **(funcs.get("commands", {}))}


def install(module: str, candidate: Candidate, cmd_args: dict):
    _API_LIST[module]["install"](candidate, cmd_args)


def remove(module: str, installation: Installation, cmd_args: dict) -> None:
    _API_LIST[module]["remove"](installation)


def upgrade(module: str, installation: Installation, cmd_args: dict) -> None:
    _API_LIST[module]["upgrade"](installation, cmd_args)


def versions(module: str, installation: Installation, cmd_args: dict) -> None:
    _API_LIST[module]["versions"](installation, cmd_args)


def hasCommand(module: str, command: str) -> bool:
    return command in _API_LIST[module].keys()


def commandNames() -> list[str]:
    return list(_COMMANDS.keys())


def command(command: str, cmd_args: dict) -> None:
    _COMMANDS[command](cmd_args)
