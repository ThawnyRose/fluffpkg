from libraries import moduleLib

program_name = "fluffpkg"
program_usage = "fluffpkg [options] command"
program_desc = "The Fluffy Multipurpose Package Installer :3 - ThawnyRose"
arguments = [
    ("-h", "--help", "Show this help message"),
    ("-l", "--nolauncher", "Don't install .desktop files"),
    # (None, "--launcher", "Install .desktop files to ~/.local/share/applications/"),
    ("-p", "--path", "Add executable to path (NYI)"),
    ("-i", "--installed", "Only list installed packages"),
    ("-f", "--force", "Force a command, overrides some protections"),
    # ("-y", "--notinteractive", "Don't use any interactive prompts, assume defaults"),
    # ("-m", "--module", "Specify which module to use"),
]

value_arguments = []
# value_arguments = ["--module"]

builtin_commands = ["install", "list", "upgrade", "modify", "remove"]

commandLength = {  # Defaults to 'All', so those aren't listed
    "list": "None",
}


def print_help() -> None:
    print(program_usage)
    print(program_desc)
    print(f"Commands: {', '.join(builtin_commands + moduleLib.commandNames())}")
    print("Options:")
    for i in arguments:
        print(f"\t{i}")


def parse_args(args: list[str]) -> dict:
    o_args = args
    args = [x.lower() for x in args]

    output = {}
    # command = args[-1]
    # args = args[:-1]
    skip_next = False
    for i, a in enumerate(args):
        if type(skip_next) is bool and skip_next:
            continue
        elif type(skip_next) is int and skip_next > 0:
            skip_next -= 1
            continue
        this_arg = ""
        this_val = ""
        for possible_arg in arguments:
            # print(a, possible_arg)
            if a in possible_arg[0:2]:
                this_arg = possible_arg[1]
                this_val = True
            elif "=" in a:
                # print(a.split("=", 1)[0], possible_arg[0:2])
                if a.split("=", 1)[0] in possible_arg[0:2]:
                    # print("Found")
                    if possible_arg[1] not in value_arguments:
                        print(f'Argument "{possible_arg[1]}" does not take a value.')
                        exit()
                    this_arg = possible_arg[1]
                    this_val = a.split("=", 1)[1]

        if this_arg == "":
            if a in builtin_commands or a in moduleLib.commandNames():
                output["command"] = a
                length = commandLength.get(a, "All")
                if length == "All":
                    output["command_args"] = o_args[i + 1 :]
                    skip_next = True
                    continue
                if length == "None":
                    continue

        if this_arg == "":
            print(f"Unknown Command: {a}")
            exit()

        # print(this_arg)
        output[this_arg] = this_val
        # print(args)
    for possible_arg in arguments:
        if possible_arg[1] not in output.keys():
            output[possible_arg[1]] = False

    return output


if __name__ == "__main__":
    print_help()
