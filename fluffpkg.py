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
    NoCandidate,
    SpecificVersion,
    UsageError,
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

combinedCommands = argumentsLib.builtin_commands + moduleLib.getCommands()

args = argumentsLib.parse_args(args, combinedCommands)

if not args:
    exit()

if args["command"] == "help":
    argumentsLib.print_help(args["command_help"], commandList=combinedCommands)
    exit()
if args["command"] == "install":
    for package_name in args["packages"]:
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
    for package_name in args["packages"]:
        install = manageInstalledLib.query(package_name)
        if install is None:
            print(f"{package_name} is not installed.")
            exit()
        moduleLib.remove(install.module, install, args)
elif args["command"] == "upgrade":
    if len(args["packages"]) == 0:
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
            (package, manageInstalledLib.query(package)) for package in args["packages"]
        ]
        for package, install in packages:
            if install is None:
                print(f"{package} is not installed.")
                exit()
            moduleLib.upgrade(install.module, install, args)
elif args["command"] == "versions":
    package_name = args["package"]
    candidate = sourcesLib.get_source(package_name)
    if candidate is None:
        print(f"{package_name} has no source.")
        exit()
    if not moduleLib.hasCommand(candidate.module, "versions"):
        print(f"Module {candidate.module} does not support getting available versions")
        exit()

    moduleLib.versions(candidate.module, candidate, args)
elif args["command"] == "execpath":
    package_name = args["package"]
    install = manageInstalledLib.query(package_name)
    if install is None:
        print(f"{package_name} is not installed.")
        exit()
    if not moduleLib.hasCommand(install.module, "execpath"):
        print(f"Module {install.module} does not support getting executable path")
        exit()

    moduleLib.execpath(install.module, install, args)
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
                "Package Name",
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
                    candidate.source,
                ]
            )
        table = tabulate(
            table_data, headers=["Name", "Package Name", "Module", "Source"]
        )
        print(table)
elif args["command"] == "modify":
    package = args["package"]
    attribute = args["attribute"]["command"]
    if attribute == "add-categories":
        new_categories = args["attribute"]["categories"]
        launcherLib.add_categories(package, new_categories)
    elif attribute == "remove-categories":
        new_categories = args["attribute"]["categories"]
        launcherLib.remove_categories(package, new_categories)
    elif attribute == "add-launcher":
        launcherLib.add_launcher_later(package, args["attribute"]["--force"])
    elif attribute == "remove-launcher":
        launcherLib.remove_launcher(package)
    else:
        source = sourcesLib.get_source(package)
        if source is None:
            raise NoCandidate()
        if attribute in moduleLib.modificationNames(source.module):
            moduleLib.modify(
                package, source.module, attribute, args["attribute"][attribute]
            )
        else:
            raise InternalError(f"Unknown Attribute: {attribute}")
elif args["command"] == "show":
    package = args["package"]
    attribute = args["attribute"]["command"]
    if attribute == "categories":
        launcherLib.list_categories(package)
    else:
        source = sourcesLib.get_source(package)
        if source is None:
            raise NoCandidate()
        if attribute in moduleLib.showNames(source.module):
            moduleLib.show(package, source.module, attribute)
        else:
            raise InternalError(f"Unknown Attribute: {attribute}")
elif args["command"] in moduleLib.commandNames():
    moduleLib.command(args["command"], args)
else:
    raise InternalError("Unknown Command: " + args["command"])
