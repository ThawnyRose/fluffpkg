_API_LIST = {}
_COMMANDS = {}


def register(module, funcs):
    global _COMMANDS
    _API_LIST[module] = funcs
    _COMMANDS = {**_COMMANDS, **(funcs.get("commands", {}))}


def install(module, candidate, nolauncher=False, path=False):
    _API_LIST[module]["install"](candidate, nolauncher, path)


def remove(module, installation):
    _API_LIST[module]["remove"](installation)


def commandNames():
    return list(_COMMANDS.keys())


def command(module, cmd_args):
    _COMMANDS[module](cmd_args)
