#!/usr/bin/env python3
from pathlib import Path
from tabulate import tabulate
from libraries import sourcesLib
from libraries import manageInstalledLib
from libraries import launcherLib
import modules
from libraries import moduleLib
from libraries import argumentsLib
from libraries.exceptions import (
    AlreadyNewest,
    InternalError,
    MultipleCandidates,
    SpecificVersion,
)
import sys

Path("~/.fluffpkg").expanduser().mkdir(parents=True, exist_ok=True)

# import sys
# import traceback


# class TracePrints(object):
#     def __init__(self):
#         self.stdout = sys.stdout

#     def write(self, s):
#         self.stdout.write("Writing %r\n" % s)
#         traceback.print_stack(file=self.stdout)


# sys.stdout = TracePrints()


# args = ["remove", "cura"]  # DEBUG
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
        query = sourcesLib.query(package_name)
        if type(query) is not sourcesLib.QueryResult:
            print(f"Could not find installation candidate for {package_name}")
            exit()
        if query.kind == "weak_recommend":
            names = [candidate.package_name for candidate in query.candidates]
            print("Some weak matches were found:", ", ".join(names))
            exit()
        if query.kind == "strong_recommend":
            names = [candidate.package_name for candidate in query.candidates]
            print("Did you mean:", ", ".join(names))
            exit()
        if query.kind != "found":
            raise InternalError("Unknown match type: " + query.kind)

        if len(query.candidates) != 1:
            raise MultipleCandidates()
            # print(f"Multiple candidates were found: {query.candidates}")

        to_install = query.candidates[0]
        moduleLib.install(
            to_install.module,
            to_install,
            args,
        )
elif args["command"] == "remove":
    if len(args["command_args"]) == 0:
        print("Usage: fluffpkg remove <packages...>")
        exit()
    for package_name in args["command_args"]:
        install = manageInstalledLib.query(package_name)
        if install is None:
            print(f"{package_name} is not installed.")
            exit()
        moduleLib.remove(install.module, install, args)
elif args["command"] == "upgrade":
    if len(args["command_args"]) == 0:
        print("Upgrading all packages")
        installed = manageInstalledLib.list()
        max_name_len = max(len(i.name) for i in installed)
        for install in installed:
            try:
                moduleLib.upgrade(install.module, install, args)
            except AlreadyNewest:
                print(
                    f"Skipping {install.package_name},",
                    " " * (max_name_len - len(install.package_name)),
                    "already newest",
                )
            except SpecificVersion:
                print(
                    f"Skipping {install.package_name},",
                    " " * (max_name_len - len(install.package_name)),
                    "specific version",
                )
    else:
        packages = [
            (package, manageInstalledLib.query(package))
            for package in args["command_args"]
        ]
        for package, install in packages:
            if install is None:
                print(f"{package} is not installed.")
                exit()
            moduleLib.upgrade(install.module, install, args)
elif args["command"] == "list":
    if args["--installed"]:
        installed = manageInstalledLib.list()
        print("Installed packages:")
        table_data = []
        for install in installed:
            table_data.append(
                [
                    install.name,
                    install.version + (" [L]" if install.version_locked else ""),
                    install.package_name,
                    install.launcher,
                    install.path,
                    install.module,
                    install.source,
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
                    candidate.name,
                    candidate.package_name,
                    candidate.module,
                    candidate.source.kind + " " + candidate.source.url,
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
            print("Usage: fluffpkg modify <package> add-categories <categories>")
            exit()
        new_categories = args["command_args"][2:]
        launcherLib.add_categories(package, new_categories)
    elif field == "remove-categories":
        if len(args["command_args"]) <= 2:
            print("Usage: fluffpkg modify <package> remove-categories <categories>")
            exit()
        new_categories = args["command_args"][2:]
        launcherLib.remove_categories(package, new_categories)
    elif field == "add-launcher":
        if len(args["command_args"]) != 2:
            print("Usage: fluffpkg modify <package> add-launcher")
            exit()
        launcherLib.add_launcher_later(package, args["--force"])
    elif field == "remove-launcher":
        if len(args["command_args"]) != 2:
            print("Usage: fluffpkg modify <package> remove-launcher")
            exit()
        launcherLib.remove_launcher(package)
    else:
        print(f"Unknown modification {field}")
elif args["command"] in moduleLib.commandNames():
    moduleLib.command(args["command"], args)
else:
    raise InternalError("Unknown command: " + args["command"])
