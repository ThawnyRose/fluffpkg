from tabulate import tabulate
import sys

from libraries.dataClasses import FlagArg, ValueArg, PosArg, PosArgs, CmdArg, Command
from libraries.exceptions import UnknownCommand

from libraries import moduleLib

program_desc = "The Fluffy Multipurpose Package Installer :3 - ThawnyRose"


builtin_commands: list[Command] = [
    Command(
        "help",
        "Gives usage for each command",
        [
            PosArg("command_help", optional=True),
        ],
    ),
    Command(
        "install",
        "Install packages",
        [
            FlagArg("-l", "--nolauncher", "Don't install .desktop files"),
            ValueArg("-v", "--version", "Specify a version for installation"),
            PosArgs("packages"),
        ],
    ),
    Command(
        "list",
        "List packages",
        [
            FlagArg("-i", "--installed", "Only list installed packages"),
        ],
    ),
    Command(
        "upgrade",
        "Upgrade packages",
        [
            FlagArg("-f", "--force", "Overrides version lock"),
            PosArgs("packages", optional=True),
        ],
    ),
    Command(
        "modify",
        "Modify a package",
        [
            PosArg("package"),
            CmdArg(
                "attribute",
                [
                    Command(
                        "add-launcher",
                        "Add a launcher entry for the package",
                        [FlagArg("-f", "--force", "Overrides existing .desktop files")],
                    ),
                    Command(
                        "remove-launcher",
                        "Remove the launcher entry for the package",
                        [],
                    ),
                    Command(
                        "add-categories",
                        "Add categories to the launcher entry",
                        [PosArgs("categories")],
                    ),
                    Command(
                        "remove-categories",
                        "Remove categories from the launcher entry",
                        [PosArgs("categories")],
                    ),
                    Command(
                        "list-categories",
                        "List categories in a launcher entry",
                        [],
                    ),
                ],
            ),
        ],
    ),
    Command(
        "remove",
        "Remove packages",
        [
            PosArgs("packages"),
        ],
    ),
    Command("versions", "Get available versions for a package", [PosArg("package")]),
]


def help_cmd(command_name: str, commandList: list[Command] = builtin_commands) -> str:
    command = None

    for bc in commandList:
        if bc.name == command_name:
            command = bc
            break

    if command is None:
        print(f"Help failed to help {command_name}")
        raise UnknownCommand(command_name)

    return command.usage()


def help_all_cmds(commandList: list[Command] = builtin_commands) -> str:
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


def print_help(
    command_name: str | None = None, commandList: list[Command] = builtin_commands
) -> None:
    if command_name is not None:
        print(help_cmd(command_name, commandList))
    else:
        print(program_desc)
        print("Available commands:")
        print(help_all_cmds(commandList))


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

    flags: list[FlagArg] = []
    values: list[ValueArg] = []
    positionals: list[PosArg] = []
    cmd_positional: CmdArg | None = None
    star_positional: PosArgs | None = None

    for arg in command.args:
        if isinstance(arg, FlagArg):
            flags.append(arg)
        elif isinstance(arg, ValueArg):
            values.append(arg)
        elif isinstance(arg, PosArg):
            positionals.append(arg)
        elif isinstance(arg, CmdArg):
            cmd_positional = arg
        elif isinstance(arg, PosArgs):
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
