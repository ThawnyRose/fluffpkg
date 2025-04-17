from pathlib import Path
from libraries import manageInstalledLib


def add_categories(package, new_categories):
    if type(new_categories) is str:
        if ";" in new_categories:
            new_categories = new_categories.split(";")
        else:
            new_categories = new_categories.split(" ")

    install = manageInstalledLib.query(package)
    if not install:
        print("Could not update launcher, package not installed")
        exit()
    if not install["launcher"]:
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
            lines[i] = "Categories=" + (
                ";".join(list(set(old_categories + new_categories))) + ";"
            )
            found_category_line = True
    launcher_contents = "\n".join(lines)
    if not found_category_line:
        if not launcher_contents.endswith("\n"):
            launcher_contents += "\n"
        launcher_contents += f"Categories={';'.join(new_categories)};\n"
    with open(launcherPath, "w+") as f:
        f.write(launcher_contents)


def add_launcher(package, name, executable, categories):
    if type(categories) is list:
        categories = ";".join(categories)

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
        print(f"Warning: file exists, failed to sync launcher file. {launcherDest}")
        launcherSuccess = False

    if launcherSuccess:
        print("Launcher .desktop added")
