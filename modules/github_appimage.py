from pathlib import Path
import requests
from libraries.dataClasses import Installation, Candidate
from libraries import manageInstalledLib
from libraries import sourcesLib
from libraries import launcherLib
from libraries import moduleLib
import time
import os
import stat
import platform


# https://stackoverflow.com/a/16696317
def download_file(url: str, output: str | None = None, prettyname: str = "") -> str:
    timeMark = time.time() + 1
    print(f"Downloading '{prettyname}' .", end="", flush=True)
    local_filename = output if output is not None else url.split("/")[-1]
    with requests.get(url, stream=True) as r:
        r.raise_for_status()
        with open(local_filename, "wb") as f:
            for chunk in r.iter_content(chunk_size=81920):
                if time.time() > timeMark:
                    print(".", end="", flush=True)
                    timeMark = time.time() + 1
                f.write(chunk)
    print()
    return local_filename


def get_github_latest_release(url: str) -> dict:
    owner, repo = url.split("/")
    api_url = f"https://api.github.com/repos/{owner}/{repo}/releases/latest"
    # print(api_url)
    response = requests.get(api_url)
    if response.status_code != 200:
        print(
            f"Error: Failed to get GitHub releases: {response.status_code} - {response.text}"
        )
        exit()
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
        # import json
        # print(json.dumps(release["assets"]))
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


def setup() -> None:
    Path("~/.fluffpkg/data/appimage/files/").expanduser().mkdir(
        parents=True, exist_ok=True
    )
    Path("~/.fluffpkg/data/appimage/launcher/").expanduser().mkdir(
        parents=True, exist_ok=True
    )


def install(candidate: Candidate, nolauncher: bool, path: bool) -> None:
    if manageInstalledLib.check_installed(candidate):
        print(
            f"Package '{candidate.package_name}' is already installed. Try `upgrade`."
        )
        exit()
    setup()
    assert candidate.module == "github-appimage"
    # print(candidate)
    release = get_github_latest_release(candidate.download_url)
    # print(release)
    url = release["Appimage"]["DownloadUrl"]
    name = release["Appimage"]["Name"]
    outPath = Path("~/.fluffpkg/data/appimage/files/").expanduser() / name
    download_file(url, output=outPath, prettyname=name)
    os.chmod(outPath, os.stat(outPath).st_mode | stat.S_IXUSR | stat.S_IXGRP)
    manageInstalledLib.mark_installed(
        candidate,
        release["Tag"],
        str(outPath.resolve()),
    )
    print(f"{candidate.name} successfully installed!")

    if not nolauncher:
        launcherLib.add_launcher(
            candidate.package_name,
            candidate.name,
            outPath,
            candidate.categories,
        )
    if path:
        print(".appimage files aren't currently added to the path.")


def add_cmd(args: dict) -> None:
    for cmd_arg in args["command_args"]:
        if "/" not in cmd_arg:
            print("Github packages are formatted: owner/repo")
            continue
        owner, repo = cmd_arg.split("/")
        add(owner, repo)


def add(owner: str, repo: str) -> Candidate:
    api_url = f"https://api.github.com/repos/{owner}/{repo}"

    response = requests.get(api_url)
    if response.status_code != 200:
        print(
            f"Error: Failed to get GitHub repository: {response.status_code} - {response.text}"
        )
        exit()
    repository = response.json()

    candidate = Candidate(
        "github-appimage",
        repository["name"],
        repository["name"].replace(" ", "_").lower(),
        "[]",
        "manual:_",
        repository["full_name"],
    )

    sourcesLib.add_candidate(candidate, failExists=False)
    return candidate


def add_install_cmd(args: dict) -> None:
    for cmd_arg in args["command_args"]:
        if "/" not in cmd_arg:
            print("Github packages are formatted: owner/repo")
            continue
        owner, repo = cmd_arg.split("/")
        add_install(owner, repo, nolauncher=args["--nolauncher"], path=args["--path"])


def add_install(
    owner: str, repo: str, nolauncher: bool = False, path: bool = False
) -> None:
    candidate = add(owner, repo)
    install(candidate, nolauncher, path)


def remove_cmd(args: dict) -> None:
    for package in args["command_args"]:
        sourcesLib.remove_candidate(package)


def remove(installation: Installation) -> None:
    assert installation.module == "github-appimage"
    package = installation.package_name
    if installation.launcher:
        launcherLib.remove_launcher(
            package,
        )
    appimage = Path(installation.executable_path)
    appimage.unlink()
    manageInstalledLib.unmark_installed(package)


moduleLib.register(
    "github-appimage",
    {
        "install": install,
        "remove": remove,
        "commands": {
            "add-github-appimage": add_cmd,
            "remove-github-appimage": remove_cmd,
            "install-github-appimage": add_install_cmd,
        },
    },
)
