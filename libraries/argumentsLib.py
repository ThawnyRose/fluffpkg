program_name = "fluffpkg"
program_usage = "fluffpkg [options] command"
program_desc = "The Fluffy Multipurpose Package Installer :3 - ThawnyRose"
arguments = [
    ("-h", "--help", "Show this help message"),
    ("-l", "--nolauncher", "Don't install .desktop files"),
    # (None, "--launcher", "Install .desktop files to ~/.local/share/applications/"),
    ("-p", "--path", "Add executable to path (NYI)"),
    ("-i", "--installed", "Only list installed packages"),
    # ("-y", "--notinteractive", "Don't use any interactive prompts, assume defaults"),
    # ("-m", "--module", "Specify which module to use"),
]

value_arguments = []
# value_arguments = ["--module"]

commands = ["install", "list", "upgrade", "modify", "remove"]


def print_help():
    print(program_usage)
    print(program_desc)
    print(f"Commands: {', '.join(commands)}")
    print("Options:")
    for i in arguments:
        print(f"\t{i}")


def parse_args(args):
    args = [x.lower() for x in args]
    output = {}
    # command = args[-1]
    # args = args[:-1]
    skip_next = False
    for i, a in enumerate(args):
        if skip_next:
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
            if a in commands:
                output["command"] = a
                output["command_args"] = args[i + 1 :]
                skip_next = True
                continue

        if this_arg == "":
            print(f"Unknown argument: {a}")
            return False

        # print(this_arg)
        output[this_arg] = this_val
        # print(args)
    for possible_arg in arguments:
        if possible_arg[1] not in output.keys():
            output[possible_arg[1]] = False

    return output


if __name__ == "__main__":
    print_help()
