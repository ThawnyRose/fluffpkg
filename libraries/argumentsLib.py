from tabulate import tabulate

from libraries.dataClasses import FlagArg, ValueArg, PosArg, PosArgs, CmdArg, Command
from libraries.exceptions import UnknownCommand

from libraries import sourcesLib
from libraries import moduleLib

program_desc = "The Fluffy Multipurpose Package Installer :3 - ThawnyRose"


builtin_commands: list[Command] = [
    Command(
        "help",
        "Gives usage for each command",
        [
            PosArg("command_help", "Command to get help for", optional=True),
        ],
    ),
    Command(
        "install",
        "Install packages",
        [
            FlagArg("-l", "--nolauncher", "Don't install .desktop files"),
            FlagArg("-p", "--path", "Add installed package to the path"),
            ValueArg("-v", "--version", "Specify a version for installation"),
            PosArgs("packages", "Packages to install"),
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
            PosArgs("packages", "Packages to upgrade", optional=True),
        ],
    ),
    Command(
        "modify",
        "Modify a package",
        [
            PosArg("package", "Package to modify"),
            CmdArg(
                "attribute",
                "Attribute to be modified",
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
                        "add-path",
                        "Add a the package to the path",
                        [],
                    ),
                    Command(
                        "remove-path",
                        "Remove the package from the path",
                        [],
                    ),
                    Command(
                        "add-categories",
                        "Add categories to the launcher entry",
                        [PosArgs("categories", "Categories to add")],
                    ),
                    Command(
                        "remove-categories",
                        "Remove categories from the launcher entry",
                        [PosArgs("categories", "Categories to remove")],
                    ),
                ],
            ),
        ],
    ),
    Command(
        "show",
        "Show a package's attributes",
        [
            PosArg("package", "Package to modify"),
            CmdArg(
                "attribute",
                "Attribute to be shown",
                [
                    Command(
                        "categories",
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
            PosArgs("packages", "Packages to remove"),
        ],
    ),
    Command(
        "versions",
        "Get available versions for a package",
        [PosArg("package", "Package to get versions for")],
    ),
    Command(
        "execpath",
        "Get executable path for a package",
        [
            PosArg("package", "Package to find path for"),
            FlagArg("-v", "--noversion", "Return with a glob for the file version"),
        ],
    ),
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


def parse_modify(
    package: str, attribute: list[str], commandList: list[Command]
) -> dict | None:
    source = sourcesLib.get_source(package)
    if source is None:
        return parse_args(attribute, commandList)

    newCommandList = commandList + moduleLib.getModifications(source.module)

    # print("MODIFY", package, source.module, attribute, newCommandList)
    try:
        return parse_args(attribute, newCommandList)
    except UnknownCommand:
        print(f"Unknown Attribute '{attribute[0]}'")
        modify_cmd = [c for c in builtin_commands if c.name == "modify"][0]
        modify_cmd.args[0].name = f"package from {source.module}"
        assert isinstance(modify_cmd.args[1], CmdArg)
        modify_cmd.args[1].cmds += moduleLib.getModifications(source.module)
        try:
            print(modify_cmd.usage())
        except Exception:
            pass
        return None


def parse_show(
    package: str, attribute: list[str], commandList: list[Command]
) -> dict | None:
    source = sourcesLib.get_source(package)
    if source is None:
        return parse_args(attribute, commandList)

    newCommandList = commandList + moduleLib.getShows(source.module)

    # print("MODIFY", package, source.module, attribute, newCommandList)
    try:
        return parse_args(attribute, newCommandList)
    except UnknownCommand:
        print(f"Unknown Attribute '{attribute[0]}'")
        show_cmd = [c for c in builtin_commands if c.name == "show"][0]
        show_cmd.args[0].name = f"package from {source.module}"
        assert isinstance(show_cmd.args[1], CmdArg)
        show_cmd.args[1].cmds += moduleLib.getShows(source.module)
        try:
            print(show_cmd.usage())
        except Exception:
            pass
        return None


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
            for v in values:
                if arg_k == v.name or arg_k == v.short:
                    v.value = arg_v
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
            if command.name == "modify":
                recurse = parse_modify(
                    output["package"],
                    o_args[i + 1 :],
                    commandList=cmd_positional.cmds,
                )
                if recurse is None:
                    exit()
            elif command.name == "show":
                recurse = parse_show(
                    output["package"],
                    o_args[i + 1 :],
                    commandList=cmd_positional.cmds,
                )
                if recurse is None:
                    exit()
            else:
                try:
                    recurse = parse_args(
                        o_args[i + 1 :], commandList=cmd_positional.cmds
                    )
                except UnknownCommand:
                    print(f"Unknown {cmd_positional.name} '{cmd_args[i]}'")
                    print(help_cmd(command.name, commandList))
                    exit()
            cmd_positional.handled = True
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
        output[i.name] = i.value
    if star_positional is not None:
        output[star_positional.name] = star_positional.values
    return output
