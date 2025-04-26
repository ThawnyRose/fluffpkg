from pathlib import Path
from libraries import manageInstalledLib
from libraries.utilitiesLib import pathwarn


def add_path(package: str):
    install = manageInstalledLib.query(package)
    if not install:
        print("Could not add to path, package not installed")
        exit()
    if install.path:
        print("Could not add to path, package already added")
        exit()

    destination = Path("~/.fluffpkg/bin/").expanduser() / package
    destination.symlink_to(install.executable_path)
    manageInstalledLib.mark_attribute(package, "path", True)
    pathwarn()


def remove_path(package: str):
    install = manageInstalledLib.query(package)
    if not install:
        print("Could not remove from path, package not installed")
        exit()
    if not install.path:
        print("Could not remove from path, package is not added")
        exit()

    destination = Path("~/.fluffpkg/bin/").expanduser() / package
    destination.unlink()
    manageInstalledLib.mark_attribute(package, "path", False)
