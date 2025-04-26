from types import FunctionType
from libraries.dataClasses import Candidate, Installation, Command, PosArg

_API_LIST = {}
_MODIFICATIONS: dict[str, list[tuple[Command, FunctionType]]] = {}
_SHOWS: dict[str, list[tuple[Command, FunctionType]]] = {}
_COMMANDS: list[tuple[Command, FunctionType]] = []


def register(module: str, funcs: dict) -> None:
    global _COMMANDS
    _API_LIST[module] = funcs
    _COMMANDS = _COMMANDS + funcs.get("commands", [])
    _MODIFICATIONS[module] = []
    _SHOWS[module] = []
    for name, help, mod, show in funcs.get("attributes", []):
        _MODIFICATIONS[module].append(
            (Command(name, help, args=[PosArg(name, help)]), mod)
        )
        _SHOWS[module].append((Command(name, help, []), show))


def install(module: str, candidate: Candidate, cmd_args: dict):
    _API_LIST[module]["install"](candidate, cmd_args)


def remove(module: str, installation: Installation, cmd_args: dict) -> None:
    _API_LIST[module]["remove"](installation, cmd_args)


def upgrade(module: str, installation: Installation, cmd_args: dict) -> None:
    _API_LIST[module]["upgrade"](installation, cmd_args)


def versions(module: str, candidate: Candidate, cmd_args: dict) -> None:
    _API_LIST[module]["versions"](candidate, cmd_args)


def execpath(module: str, installation: Installation, cmd_args: dict) -> None:
    _API_LIST[module]["execpath"](installation, cmd_args)


def hasCommand(module: str, command: str) -> bool:
    return command in _API_LIST[module].keys()


def commandNames() -> list[str]:
    return [c[0].name for c in _COMMANDS]


def getModifications(module: str) -> list[Command]:
    return [m[0] for m in _MODIFICATIONS[module]]


def getShows(module: str) -> list[Command]:
    return [s[0] for s in _SHOWS[module]]


def modificationNames(module: str) -> list[str]:
    return [s[0].name for s in _SHOWS[module]]


def showNames(module: str) -> list[str]:
    return [s[0].name for s in _SHOWS[module]]


def modify(package: str, module: str, attribute: str, newval: str) -> None:
    mod = [m[1] for m in _MODIFICATIONS[module] if m[0].name == attribute][0]
    mod(package, newval)


def show(package: str, module: str, attribute: str) -> None:
    sho = [s[1] for s in _SHOWS[module] if s[0].name == attribute][0]
    sho(package)


def getCommands() -> list[Command]:
    return [c[0] for c in _COMMANDS]


def command(command: str, cmd_args: dict) -> None:
    cmd = [c[1] for c in _COMMANDS if c[0].name == command][0]
    cmd(cmd_args)
