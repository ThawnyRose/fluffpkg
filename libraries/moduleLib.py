from types import FunctionType
from libraries.dataClasses import Candidate, Installation, Command

_API_LIST = {}
_COMMANDS: list[tuple[Command, FunctionType]] = []


def register(module: str, funcs: dict) -> None:
    global _COMMANDS
    _API_LIST[module] = funcs
    _COMMANDS = _COMMANDS + funcs.get("commands", [])


def install(module: str, candidate: Candidate, cmd_args: dict):
    _API_LIST[module]["install"](candidate, cmd_args)


def remove(module: str, installation: Installation, cmd_args: dict) -> None:
    _API_LIST[module]["remove"](installation, cmd_args)


def upgrade(module: str, installation: Installation, cmd_args: dict) -> None:
    _API_LIST[module]["upgrade"](installation, cmd_args)


def versions(module: str, candidate: Candidate, cmd_args: dict) -> None:
    _API_LIST[module]["versions"](candidate, cmd_args)


def hasCommand(module: str, command: str) -> bool:
    return command in _API_LIST[module].keys()


def commandNames() -> list[str]:
    return [c[0].name for c in _COMMANDS]


def getCommands() -> list[Command]:
    return [c[0] for c in _COMMANDS]


def command(command: str, cmd_args: dict) -> None:
    cmd = [c[1] for c in _COMMANDS if c[0].name == command][0]
    cmd(cmd_args)
