#!/usr/bin/env python3
from pathlib import Path
from tabulate import tabulate
from libraries import argumentsLib
from libraries import sourcesLib
from libraries import manageInstalledLib
from libraries import launcherLib
import modules
import sys

Path("~/.fluffpkg").expanduser().mkdir(parents=True, exist_ok=True)

sourcesLib.load()

# args = ["remove", "cura"]  # DEBUG
# args = ["-i", "list"]  # DEBUG
args = sys.argv[1:]

if len(args) == 0:
    argumentsLib.print_help()
    exit()

args = argumentsLib.parse_args(args)

if not args:
    exit()

if args["--help"]:
    argumentsLib.print_help()
    exit()

if args["--path"]:
    print("Warning: '--path' not yet implemented")

if args["command"] == "install":
    if len(args["command_args"]) == 0:
        print("Usage: fluffpkg install <packages...>")
        exit()
    for cmd_arg in args["command_args"]:
        package_name = cmd_arg
        q = sourcesLib.query(package_name)
        if len(q) == 0:
            print(f"Could not find installation candidate for {package_name}")
            exit()
        type_of_candidate = q[0]
        if type_of_candidate == "weak_recommend":
            names = [candidate["package_name"] for candidate in q[1]]
            print("Some weak matches were found:", ", ".join(names))
            exit()
        if type_of_candidate == "strong_recommend":
            names = [candidate["package_name"] for candidate in q[1]]
            print("Did you mean:", ", ".join(names))
            exit()
        if type_of_candidate != "found":
            print("Internal error:", "Unknown match type:", type_of_candidate)
            exit()
        to_install = q[1]
        if to_install["module"] == "github-appimage":
            modules.github_appimage.install(
                to_install,
                nolauncher=args["--nolauncher"],
                path=args["--path"],
            )
elif args["command"] == "remove":
    if len(args["command_args"]) == 0:
        print("Usage: fluffpkg remove <packages...>")
        exit()
    for cmd_arg in args["command_args"]:
        package_name = cmd_arg
        q = manageInstalledLib.query(package_name)
        if not q:
            print(f"{package_name} is not installed.")
            exit()
        to_remove = q

        if to_remove["module"] == "github-appimage":
            modules.github_appimage.remove(to_remove)
elif args["command"] == "list":
    if args["--installed"]:
        installed = manageInstalledLib.list()
        print("Installed packages:")
        table_data = []
        for install in installed:
            table_data.append(
                [
                    install["name"],
                    install["version"],
                    install["package_name"],
                    install["launcher"],
                    install["path"],
                    install["module"],
                    install["source"].split(" ", 1)[1],
                ]
            )
        table = tabulate(
            table_data,
            headers=[
                "Name",
                "Version",
                "Executable Name",
                "Launcher",
                "Path",
                "Module",
                "Source",
            ],
        )
        print(table)
    else:
        candidates = sourcesLib.list()
        print("Installation candidates:")
        table_data = []
        for candidate in candidates:
            table_data.append(
                [
                    candidate["name"],
                    candidate["package_name"],
                    candidate["module"],
                    candidate["source"].split(" ", 1)[1],
                ]
            )
        table = tabulate(
            table_data, headers=["Name", "Executable Name", "Module", "Source"]
        )
        print(table)
elif args["command"] == "modify":
    if len(args["command_args"]) <= 1:
        print("Usage: fluffpkg modify <package> <field> [values...]")
        exit()
    package = args["command_args"][0]
    field = args["command_args"][1]
    if field == "add-categories":
        if len(args["command_args"]) <= 2:
            print("Usage: fluffpkg modify package add-categories <categories>")
            exit()
        new_categories = args["command_args"][2:]
        launcherLib.add_categories(package, new_categories)
        print("Categories Added")
    else:
        print(f"Unknown field {field}")

elif args["command"] == "add-github-appimage":
    for cmd_arg in args["command_args"]:
        owner, repo = cmd_arg.split("/")
        modules.github_appimage.add(owner, repo)
elif args["command"] == "install-github-appimage":
    for cmd_arg in args["command_args"]:
        owner, repo = cmd_arg.split("/")
        modules.github_appimage.add_install(
            owner, repo, nolauncher=args["--nolauncher"], path=args["--path"]
        )
else:
    print("Internal error:", "Unknown command:", args["command"])
    exit()
