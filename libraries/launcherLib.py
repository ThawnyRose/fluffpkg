from pathlib import Path
from libraries import manageInstalledLib
from libraries import sourcesLib


def format_categories_arg(args: list[str]) -> list[str]:
    if len(args) == 1:
        return args[0].split(";")
    return args


def add_categories(package: str, new_categories: list[str]) -> None:
    new_categories = format_categories_arg(new_categories)

    install = manageInstalledLib.query(package)
    if not install:
        print("Could not update launcher, package not installed")
        exit()
    if not install.launcher:
        print("Could not update launcher, package does not have launcher")
        exit()

    launcherName = package + ".desktop"
    launcherPath = (
        Path("~/.fluffpkg/data/appimage/launcher/").expanduser() / launcherName
    )
    found_category_line = False
    with open(launcherPath, "r") as f:
        launcher_contents = f.read()
    lines = launcher_contents.split("\n")
    for i in range(len(lines)):
        if lines[i].startswith("Categories="):
            old_categories = [x for x in lines[i][11:].split(";") if x != ""]
            c_list = list(set(old_categories + new_categories))
            lines[i] = "Categories=" + (";".join(c_list) + ";")
            if install.source.kind == "manual":
                sourcesLib.update_categories(install.package_name, c_list)
            found_category_line = True
    launcher_contents = "\n".join(lines)
    if not found_category_line:
        if not launcher_contents.endswith("\n"):
            launcher_contents += "\n"
        launcher_contents += f"Categories={';'.join(new_categories)};\n"
    with open(launcherPath, "w+") as f:
        f.write(launcher_contents)
    print("Categories Added")


def remove_categories(package: str, new_categories: list[str]) -> None:
    new_categories = format_categories_arg(new_categories)

    install = manageInstalledLib.query(package)
    if not install:
        print("Could not update launcher, package not installed")
        exit()
    if not install.launcher:
        print("Could not update launcher, package does not have launcher")
        exit()

    launcherName = package + ".desktop"
    launcherPath = (
        Path("~/.fluffpkg/data/appimage/launcher/").expanduser() / launcherName
    )
    found_category_line = False
    with open(launcherPath, "r") as f:
        launcher_contents = f.read()
    lines = launcher_contents.split("\n")
    for i in range(len(lines)):
        if lines[i].startswith("Categories="):
            old_categories = [x for x in lines[i][11:].split(";") if x != ""]
            c_list = list(set(old_categories).difference(new_categories))
            lines[i] = "Categories=" + (";".join(c_list) + ";")
            if install.source.kind == "manual":
                sourcesLib.update_categories(install.package_name, c_list)
            found_category_line = True
    launcher_contents = "\n".join(lines)
    if not found_category_line:
        if not launcher_contents.endswith("\n"):
            launcher_contents += "\n"
        launcher_contents += f"Categories={';'.join(new_categories)};\n"
    with open(launcherPath, "w+") as f:
        f.write(launcher_contents)
    print("Categories Removed")


def add_launcher(
    package: str,
    name: str,
    executable: str,
    categories: list[str] | str,
    force: bool = False,
) -> None:
    if isinstance(categories, list):
        categories = ";".join(categories) + ";"

    launcherName = package + ".desktop"
    launcherPath = (
        Path("~/.fluffpkg/data/appimage/launcher/").expanduser() / launcherName
    )
    launcherDest = Path("~/.local/share/applications/").expanduser() / launcherName
    with open(launcherPath, "w+") as f:
        f.write("[Desktop Entry]\n")
        f.write(f"Name={name}\n")
        f.write(f"Exec={executable}\n")
        f.write(f"Categories={categories}\n")
        f.write("Type=Application\n")
        f.write("Terminal=false\n")
    launcherSuccess = True
    try:
        launcherDest.symlink_to(launcherPath)
    except FileExistsError:
        if force:
            launcherDest.unlink()
            launcherDest.symlink_to(launcherPath)
        else:
            print(
                f"Warning: file exists, failed to sync launcher file. Use --force to override.\n{launcherDest}"
            )
            launcherSuccess = False

    if launcherSuccess:
        print("Launcher .desktop added")
        manageInstalledLib.mark_attribute(package, "launcher", True)


def add_launcher_later(package: str, force: bool = False) -> None:
    install = manageInstalledLib.query(package)
    if not install:
        print("Could not add launcher, package not installed")
        exit()
    if install.launcher:
        print("Could not add launcher, package already has launcher")
        exit()
    add_launcher(
        package,
        install.name,
        install.executable_path,
        install.categories,
        force,
    )


def remove_launcher(package: str) -> None:
    launcherName = package + ".desktop"
    launcherPath = (
        Path("~/.fluffpkg/data/appimage/launcher/").expanduser() / launcherName
    )
    launcherDest = Path("~/.local/share/applications/").expanduser() / launcherName
    launcherPath.unlink()
    launcherDest.unlink()
    print("Launcher .desktop removed")
    manageInstalledLib.mark_attribute(package, "launcher", False)


def list_categories(package: str) -> None:
    install = manageInstalledLib.query(package)
    if not install:
        print("Could not read launcher, package not installed")
        exit()
    if not install.launcher:
        print("Could not read launcher, package does not have launcher")
        exit()

    launcherName = package + ".desktop"
    launcherPath = (
        Path("~/.fluffpkg/data/appimage/launcher/").expanduser() / launcherName
    )
    found_category_line = False
    with open(launcherPath, "r") as f:
        launcher_contents = f.read()
    lines = launcher_contents.split("\n")
    for i in range(len(lines)):
        if lines[i].startswith("Categories="):
            print(
                ", ".join(
                    c
                    for c in lines[i].replace("Categories=", "", 1).split(";")
                    if c.strip() != ""
                )
            )
