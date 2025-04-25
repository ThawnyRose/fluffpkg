from tabulate import tabulate
import sys

from libraries.exceptions import UnknownCommand

from libraries import moduleLib

program_desc = "The Fluffy Multipurpose Package Installer :3 - ThawnyRose"


class arg:
    pass

    def usage(self) -> str:
        return "ERROR"


class flag_arg(arg):
    value: bool = False

    def __init__(self, short: str, name: str, help: str):
        self.short = short
        self.name = name
        self.help = help

    def usage(self) -> str:
        return f"[{self.name}]"


class value_arg(arg):
    value: str | None = None

    def __init__(self, short: str, name: str, help: str):
        self.short = short
        self.name = name
        self.help = help

    def usage(self) -> str:
        return f"[{self.name} = ]"


class pos_arg(arg):
    def __init__(self, name: str, optional: bool = False):
        self.name = name
        self.optional = optional

    def usage(self) -> str:
        return f"[{self.name}]" if self.optional else f"<{self.name}>"


class pos_args(arg):
    values: list[str] = []

    def __init__(self, name: str, optional: bool = False):
        self.name = name
        self.optional = optional

    def usage(self) -> str:
        return f"[{self.name}...]" if self.optional else f"<{self.name}...>"


class command:
    def __init__(self, name: str, help: str, args: list[arg]):
        self.name = name
        self.help = help
        self.args = args

    def usage(self) -> str:
        return f"Usage: {self.name} {' '.join(a.usage() for a in self.args)}"


class cmd_arg(arg):
    def __init__(self, name: str, cmds: list[command]):
        self.name = name
        self.cmds = cmds
        self.handled = False

    def usage(self) -> str:
        output = f"<{self.name}> ...\n"
        output += "Attributes:\n"
        output += help_all_cmds(self.cmds)
        return output


builtin_commands: list[command] = [
    command(
        "help",
        "Gives usage for each command",
        [
            pos_arg("command_help", optional=True),
        ],
    ),
    command(
        "install",
        "Install packages",
        [
            flag_arg("-l", "--nolauncher", "Dont install .desktop files"),
            value_arg("-v", "--version", "Specify a version for installation"),
            pos_args("packages"),
        ],
    ),
    command(
        "list",
        "List packages",
        [
            flag_arg("-i", "--installed", "Only list installed packages"),
        ],
    ),
    command(
        "upgrade",
        "Upgrade packages",
        [
            flag_arg("-f", "--force", "Overrides version lock"),
            pos_args("packages", optional=True),
        ],
    ),
    command(
        "modify",
        "Modify a package",
        [
            pos_arg("package"),
            cmd_arg(
                "attribute",
                [
                    command(
                        "add-launcher",
                        "Add a launcher entry for the package",
                        [
                            flag_arg(
                                "-f", "--force", "Overrides existing .desktop files"
                            )
                        ],
                    ),
                    command(
                        "remove-launcher",
                        "Remove the launcher entry for the package",
                        [],
                    ),
                    command(
                        "add-categories",
                        "Add categories to the launcher entry",
                        [pos_arg("categories")],
                    ),
                    command(
                        "remove-categories",
                        "Remove categories from the launcher entry",
                        [pos_arg("categories")],
                    ),
                ],
            ),
        ],
    ),
    command(
        "remove",
        "Remove packages",
        [
            pos_args("packages"),
        ],
    ),
    command("versions", "Get available versions for a package", [pos_arg("package")]),
]


def help_cmd(command_name: str, commandList: list[command] = builtin_commands) -> str:
    command = None

    for bc in commandList:
        if bc.name == command_name:
            command = bc
            break

    if command is None:
        print(f"Help failed to help {command_name}")
        raise UnknownCommand(command_name)

    return command.usage()


def help_all_cmds(commandList) -> str:
    table_data = []
    for command in commandList:
        table_data.append(
            [
                "",
                command.name,
                "",
                "",
                command.help,
            ]
        )
    table = tabulate(table_data, tablefmt="plain")
    return table


def print_help(command_name: str | None = None) -> None:
    if command_name is not None:
        print(help_cmd(command_name))
    else:
        print(program_desc)
        print("Available commands:")
        print(help_all_cmds(builtin_commands))


def parse_args(cmd_args: list[str], commandList=builtin_commands) -> dict:
    o_args = cmd_args
    cmd_args = [x.lower() for x in cmd_args]

    command_name = cmd_args[0]
    cmd_args = cmd_args[1:]
    command = None

    for bc in commandList:
        if bc.name == command_name:
            command = bc
            break

    if command is None:
        raise UnknownCommand(command_name)

    flags: list[flag_arg] = []
    values: list[value_arg] = []
    positionals: list[pos_arg] = []
    cmd_positional: cmd_arg | None = None
    star_positional: pos_args | None = None

    for arg in command.args:
        if isinstance(arg, flag_arg):
            flags.append(arg)
        elif isinstance(arg, value_arg):
            values.append(arg)
        elif isinstance(arg, pos_arg):
            positionals.append(arg)
        elif isinstance(arg, cmd_arg):
            cmd_positional = arg
        elif isinstance(arg, pos_args):
            star_positional = arg

    output = {}
    output["command"] = command.name

    skip_next = 0
    handlingStar: bool = False

    for i in range(len(cmd_args)):
        if handlingStar and star_positional is not None:
            star_positional.values.append(cmd_args[i])
            continue

        if skip_next > 0:
            skip_next -= 1
            continue

        arg = cmd_args[i]
        done: bool = False
        # print(arg)
        if "=" in arg:
            arg_k, arg_v = arg.split("=", 1)
            for f in values:
                if arg_k == f.name or arg_k == f.short:
                    f.value = arg_v
                    done = True
        if done:
            continue

        for f in flags:
            if arg == f.name or arg == f.short:
                f.value = True
                done = True
        if done:
            continue

        for v in values:
            if arg == v.name or arg == v.short:
                v.value = cmd_args[i + 1]
                done = True
                skip_next = 1
        if done:
            continue

        if len(positionals) > 0:
            pos = positionals.pop(0)
            output[pos.name] = arg
            continue

        if cmd_positional is not None:
            try:
                recurse = parse_args(o_args[i + 1 :], commandList=cmd_positional.cmds)
                cmd_positional.handled = True
            except UnknownCommand:
                print(f"Unknown {cmd_positional.name} '{cmd_args[i]}'")
                print(help_cmd(command.name, commandList))
                exit()
            output[cmd_positional.name] = recurse
            break

        if star_positional is not None:
            handlingStar = True
            star_positional.values.append(arg)
            continue

        print(f"Unknown argument: {arg}")
        print(help_cmd(command.name, commandList))
        exit()

    if (
        star_positional is not None
        and not star_positional.optional
        and len(star_positional.values) == 0
    ):
        print(f"Missing argument '{star_positional.name}'")
        print(help_cmd(command.name, commandList))
        exit()

    if cmd_positional is not None and not cmd_positional.handled:
        print(f"Missing argument '{cmd_positional.name}'")
        print(help_cmd(command.name, commandList))
        exit()

    for p in positionals:
        if not p.optional:
            print(f"Missing argument '{p.name}'")
            print(help_cmd(command.name, commandList))
            exit()
        output[p.name] = None

    for i in flags + values:
        if i.value is not None:
            output[i.name] = i.value
    if star_positional is not None:
        output[star_positional.name] = star_positional.values
    return output


# if __name__ == "__main__":
# print_help()
# print_help("install")
# print(parse_args(["install", "abc", "def", "ghi"]))
# print(parse_args(["modify", "pkg", "add-categories", "cata;cata;"]))
