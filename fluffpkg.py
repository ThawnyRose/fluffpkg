#!/usr/bin/env python3
from pathlib import Path
from tabulate import tabulate
from libraries import argumentsLib
from libraries import sourcesLib
from libraries import manageInstalledLib
import modules
import sys

Path("~/.fluffpkg").expanduser().mkdir(parents=True, exist_ok=True)

sourcesLib.load()

# args = ["-l", "install", "cura"]  # DEBUG
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
        print("Usage: fluffpkg install package")
        exit()
    for cmd_arg in args["command_args"]:
        executable_name = cmd_arg
        q = sourcesLib.query(executable_name)
        if len(q) == 0:
            print(f"Could not find installation candidate for {executable_name}")
            exit()
        type_of_candidate = q[0]
        if type_of_candidate == "weak_recommend":
            names = [candidate["binary_name"] for candidate in q[1]]
            print("Some weak matches were found:", ", ".join(names))
            exit()
        if type_of_candidate == "strong_recommend":
            names = [candidate["binary_name"] for candidate in q[1]]
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
                    install["binary_name"],
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
                    candidate["binary_name"],
                    candidate["module"],
                    candidate["source"].split(" ", 1)[1],
                ]
            )
        table = tabulate(
            table_data, headers=["Name", "Executable Name", "Module", "Source"]
        )
        print(table)
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
