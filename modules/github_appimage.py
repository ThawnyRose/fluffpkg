from pathlib import Path
import requests
from libraries import manageInstalledLib
from libraries import sourcesLib
from libraries import argumentsLib
import time
import os
import stat
import platform

argumentsLib.commands += ["add-github-appimage", "install-github-appimage"]


# https://stackoverflow.com/a/16696317
def download_file(url, output=None, prettyname=""):
    timeMark = time.time() + 1
    print(f"Downloading '{prettyname}' .", end="", flush=True)
    local_filename = output if output is not None else url.split("/")[-1]
    # NOTE the stream=True parameter below
    with requests.get(url, stream=True) as r:
        r.raise_for_status()
        with open(local_filename, "wb") as f:
            for chunk in r.iter_content(chunk_size=81920):
                if time.time() > timeMark:
                    print(".", end="", flush=True)
                    timeMark = time.time() + 1
                # If you have chunk encoded response uncomment if
                # and set chunk_size parameter to None.
                # if chunk:
                f.write(chunk)
    print()
    return local_filename


def get_github_latest_release(url):
    url = url.split("/")
    owner, repo = url
    api_url = f"https://api.github.com/repos/{owner}/{repo}/releases/latest"
    # print(api_url)
    response = requests.get(api_url)
    if response.status_code != 200:
        print(
            f"Error: Failed to get GitHub releases: {response.status_code} - {response.text}"
        )
    release = response.json()
    # print(release["assets"])
    appimages = []
    for a in release["assets"]:
        # print(f"{a['name']}, {a['content_type']}, {a['browser_download_url']}")
        if a["content_type"] == "application/vnd.appimage" or a[
            "name"
        ].lower().endswith(".appimage"):
            appimages.append(a)
        # else:
        #     print(a["content_type"], a["name"])

    if len(appimages) == 0:
        print("No release assets of content type 'appimage'")
        exit()

    if len(appimages) != 1:
        arch = platform.machine()
        print(f"Warning: multiple appimages found. Filtering by architecture: {arch}")
        f_appimages = [a for a in appimages if arch in a["name"]]
        if len(f_appimages) != 1:
            print("Failed to find a unique appimage.")
            exit()

        appimages = f_appimages

    appimage = appimages[0]

    return {
        "Tag": release["tag_name"],
        "Name": release["name"],
        "Appimage": {
            "Name": appimage["name"],
            "DownloadUrl": appimage["browser_download_url"],
        },
    }


def setup():
    Path("~/.fluffpkg/data/appimage/files/").expanduser().mkdir(
        parents=True, exist_ok=True
    )
    Path("~/.fluffpkg/data/appimage/launcher/").expanduser().mkdir(
        parents=True, exist_ok=True
    )


def install(candidate, nolauncher=False, path=False):
    if manageInstalledLib.check_installed(candidate):
        print(f"Package '{candidate['name']}' is already installed. Try `upgrade`.")
        exit()
    setup()
    assert candidate["module"] == "github-appimage"
    if candidate["module_version"] != 0:
        print(
            f'Unknown module version {candidate["module_version"]} for module github-appimage'
        )
    # print(candidate)
    release = get_github_latest_release(candidate["download_url"])
    # print(release)
    url = release["Appimage"]["DownloadUrl"]
    name = release["Appimage"]["Name"]
    outPath = Path("~/.fluffpkg/data/appimage/files/").expanduser() / name
    download_file(url, output=outPath, prettyname=name)
    os.chmod(outPath, os.stat(outPath).st_mode | stat.S_IXUSR | stat.S_IXGRP)
    manageInstalledLib.mark_installed(candidate, release["Tag"], not nolauncher, path)
    print(f"{candidate['name']} successfully installed!")

    if not nolauncher:
        launcherName = candidate["binary_name"] + ".desktop"
        launcherPath = (
            Path("~/.fluffpkg/data/appimage/launcher/").expanduser() / launcherName
        )
        launcherDest = Path("~/.local/share/applications/").expanduser() / launcherName
        with open(launcherPath, "w+") as f:
            f.write("[Desktop Entry]\n")
            f.write(f"Name={candidate['name']}\n")
            f.write(f"Exec={outPath}\n")
            f.write(f"Categories={candidate['categories']}\n")
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

    if path:
        print(".appimage files aren't currently added to the path.")


def add(owner, repo):
    api_url = f"https://api.github.com/repos/{owner}/{repo}"

    response = requests.get(api_url)
    if response.status_code != 200:
        print(
            f"Error: Failed to get GitHub repository: {response.status_code} - {response.text}"
        )
    repository = response.json()

    candidate = {
        "module": "github-appimage",
        "module_version": 0,
        "name": repository["name"],
        "binary_name": repository["name"].replace(" ", "_").lower(),
        "categories": ";",
        "download_url": repository["full_name"],
    }
    sourcesLib.add(candidate)
    return candidate


def add_install(owner, repo, nolauncher=False, path=False):
    candidate = add(owner, repo)
    install(candidate, nolauncher, path)
