from pathlib import Path
import requests
from libraries.dataClasses import (
    Installation,
    Candidate,
    Command,
    PosArgs,
    FlagArg,
    ValueArg,
)
from libraries.exceptions import (
    AlreadyNewest,
    NoCandidate,
    SpecificVersion,
    AlreadyInstalled,
    APICallFailed,
)
from libraries.utilitiesLib import user_pick, pathwarn
from libraries import manageInstalledLib
from libraries import sourcesLib
from libraries import launcherLib
from libraries import pathLib
from libraries import moduleLib
import time
import os
import stat
import platform
import re


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


def get_github_release(api_url: str, appimage_filter: str) -> dict:
    response = requests.get(api_url)
    if response.status_code != 200:
        raise APICallFailed(f"Failed to get repository by url: {api_url}")

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

    original_appimages = appimages

    new_appimage_filter = None

    if len(appimages) != 1 and appimage_filter != "":
        print("Searching by filter:", appimage_filter)
        appimages = [
            a
            for a in appimages
            if re.search(appimage_filter, a["name"], re.IGNORECASE) is not None
        ]

    if len(appimages) == 0:
        print("Warning: user filter left no options. Ignoring...")
        appimages = original_appimages

    if len(appimages) != 1:
        arch = platform.machine()
        # print(f"Warning: multiple appimages found. Filtering by architecture: {arch}")
        appimages = [a for a in appimages if arch in a["name"]]

    if len(appimages) != 1:
        appimage = appimages[
            user_pick(
                [a["name"] for a in appimages],
                "Which appimage would you like to install",
            )
        ]
        appimages = [appimage]
        new_appimage_filter = re.escape(
            appimage["name"]
            .replace(release["tag_name"], "&&")
            .lower()
            .replace(".appimage", "")
        ).replace("\\&\\&", ".*")
        print(f"Adding appimage filter: {new_appimage_filter}")

    appimage = appimages[0]

    return {
        "Tag": release["tag_name"],
        "Name": release["name"],
        "Appimage": {
            "Name": appimage["name"],
            "DownloadUrl": appimage["browser_download_url"],
        },
        "filter": new_appimage_filter,
    }


def try_get_by_tag(api_url: str, appimage_filter: str) -> dict | None:
    try:
        return get_github_release(api_url, appimage_filter=appimage_filter)
    except APICallFailed:
        return None


def get_github_by_tag(url: str, tag: str, appimage_filter: str) -> dict:
    owner, repo = url.split("/")
    output = try_get_by_tag(
        f"https://api.github.com/repos/{owner}/{repo}/releases/tags/{tag}",
        appimage_filter=appimage_filter,
    )
    if output is not None:
        return output
    output = try_get_by_tag(
        f"https://api.github.com/repos/{owner}/{repo}/releases/tags/v{tag}",
        appimage_filter=appimage_filter,
    )
    if output is not None:
        return output
    output = try_get_by_tag(
        f"https://api.github.com/repos/{owner}/{repo}/releases/tags/V{tag}",
        appimage_filter=appimage_filter,
    )
    if output is not None:
        return output
    raise APICallFailed(f"Failed to get version {tag}")


def get_github_latest_release(url: str, appimage_filter: str) -> dict:
    owner, repo = url.split("/")
    api_url = f"https://api.github.com/repos/{owner}/{repo}/releases/latest"
    return get_github_release(api_url, appimage_filter=appimage_filter)


def setup() -> None:
    Path("~/.fluffpkg/data/appimage/files/").expanduser().mkdir(
        parents=True, exist_ok=True
    )
    Path("~/.fluffpkg/data/appimage/launcher/").expanduser().mkdir(
        parents=True, exist_ok=True
    )


def install_cmd(candidate: Candidate, cmd_args: dict) -> None:
    install(
        candidate,
        nolauncher=cmd_args["--nolauncher"],
        path=cmd_args["--path"],
        version=cmd_args["--version"],
    )


def install(
    candidate: Candidate,
    nolauncher: bool = False,
    path: bool = False,
    version: str | None = None,
    upgrade=False,
) -> None:
    if manageInstalledLib.check_installed(candidate) and not upgrade:
        raise AlreadyInstalled(candidate.package_name)
    setup()
    assert candidate.module == "github-appimage"
    # print(candidate)
    if version is None or isinstance(version, bool):
        release = get_github_latest_release(
            candidate.download_url,
            appimage_filter=candidate.module_data.get("user_select_filter", ""),
        )
        version_locked = False
    else:
        release = get_github_by_tag(
            candidate.download_url,
            version,
            appimage_filter=candidate.module_data.get("user_select_filter", ""),
        )
        version_locked = True

    if release.get("filter", None) is not None:
        candidate.module_data["user_select_filter"] = release["filter"]
        sourcesLib.set_module_data(candidate.package_name, candidate.module_data)

    # print(release)
    url = release["Appimage"]["DownloadUrl"]
    name = release["Appimage"]["Name"]
    executable_path = Path("~/.fluffpkg/data/appimage/files/").expanduser() / name
    download_file(url, output=executable_path, prettyname=name)
    os.chmod(
        executable_path, os.stat(executable_path).st_mode | stat.S_IXUSR | stat.S_IXGRP
    )
    manageInstalledLib.mark_installed(
        candidate,
        release["Tag"],
        str(executable_path.resolve()),
        version_locked=version_locked,
    )
    print(f"{candidate.name} successfully installed!")

    if not nolauncher:
        launcherLib.add_launcher(
            candidate.package_name,
            candidate.name,
            executable_path,
            candidate.categories,
        )
    if path:
        pathLib.add_path(candidate.package_name)


def add_cmd(cmd_args: dict) -> None:
    for cmd_arg in cmd_args["owner/repo"]:
        if "/" not in cmd_arg:
            print("Github packages are formatted: owner/repo")
            continue
        owner, repo = cmd_arg.split("/")
        add(owner, repo, failExists=True)


def add(owner: str, repo: str, failExists=False) -> Candidate:
    api_url = f"https://api.github.com/repos/{owner}/{repo}"

    response = requests.get(api_url)
    if response.status_code != 200:
        # print(
        #     f"Error: Failed to get GitHub repository: {response.status_code} - {response.text}"
        # )
        print("Failed to get repository")
        exit()
    repository = response.json()

    candidate = Candidate(
        "github-appimage",
        repository["name"],
        repository["name"].replace(" ", "_").lower(),
        "[]",
        "manual:_",
        repository["full_name"],
        {},
    )

    sourcesLib.add_candidate(candidate, failExists=failExists)
    return candidate


def add_install_cmd(cmd_args: dict) -> None:
    for cmd_arg in cmd_args["owner/repo"]:
        if "/" not in cmd_arg:
            print("Github packages are formatted: owner/repo")
            continue
        owner, repo = cmd_arg.split("/")
        add_install(
            owner,
            repo,
            nolauncher=cmd_args["--nolauncher"],
            path=cmd_args["--path"],
            version=cmd_args["--version"],
        )


def add_install(
    owner: str,
    repo: str,
    nolauncher: bool = False,
    path: bool = False,
    version: str | None = None,
) -> None:
    candidate = add(owner, repo)
    install(
        candidate,
        nolauncher=nolauncher,
        path=path,
        version=version,
    )


# def remove_source_cmd(cmd_args: dict) -> None:
#     for package in cmd_args["owner/repo"]:
#         sourcesLib.remove_candidate(package)


def remove_cmd(installation: Installation, cmd_args: dict) -> None:
    remove(installation)


def remove(installation: Installation, upgrade: bool = False) -> None:
    assert installation.module == "github-appimage"
    package = installation.package_name
    if installation.launcher:
        launcherLib.remove_launcher(package)
    if installation.path:
        pathLib.remove_path(package)
    appimage = Path(installation.executable_path)
    appimage.unlink()
    manageInstalledLib.unmark_installed(package)
    print(f"{package} successfully removed")


def upgrade_cmd(installation: Installation, cmd_args: dict) -> None:
    upgrade(installation, cmd_args["--force"])


def upgrade(installation: Installation, force: bool = False) -> None:
    # print(installation.package_name)
    # print(installation.version)

    if installation.version_locked and not force:
        raise SpecificVersion()

    candidate = sourcesLib.get_source(installation.package_name)

    if candidate is None:
        raise NoCandidate

    new_version = get_github_latest_release(
        candidate.download_url,
        appimage_filter=candidate.module_data.get("user_select_filter", ""),
    )["Tag"]
    if new_version == installation.version:
        raise AlreadyNewest(installation.package_name)
    remove(installation, upgrade=True)
    install(candidate, not installation.launcher, installation.path, upgrade=True)


def versions_cmd(candidate: Candidate, cmd_args: dict) -> None:
    versions(candidate)


def versions(candidate: Candidate) -> None:
    owner, repo = candidate.download_url.split("/", 1)
    api_url = f"https://api.github.com/repos/{owner}/{repo}/tags"

    response = requests.get(api_url)
    if response.status_code != 200:
        print(
            f"Error: Failed to get GitHub tags: {response.status_code} - {response.text}"
        )
        exit()
    tags = response.json()
    tag_names = []
    for tag in [t["name"] for t in tags]:
        if tag.startswith("v"):
            tag_names.append(tag.replace("v", "", 1))
        elif tag.startswith("V"):
            tag_names.append(tag.replace("V", "", 1))
        else:
            tag_names.append(tag)
    print("\n".join(tag_names))


def execpath_cmd(installation: Installation, cmd_args: dict) -> None:
    print(execpath(installation, cmd_args["--noversion"]))


def execpath(installation: Installation, noVersion: bool = False) -> str:
    execpath = installation.executable_path
    if noVersion:
        execpath = execpath.replace(installation.version, "*")
    return execpath


def user_select_filter_modify(package: str, value: str):
    source = sourcesLib.get_source(package)
    if source is None:
        raise NoCandidate
    source.module_data["user_select_filter"] = value
    sourcesLib.set_module_data(package, source.module_data)
    user_select_filter_show(package)


def user_select_filter_show(package: str):
    source = sourcesLib.get_source(package)
    if source is None:
        raise NoCandidate
    print("user_select_filter:", source.module_data.get("user_select_filter", ""))


moduleLib.register(
    "github-appimage",
    {
        "install": install_cmd,
        "remove": remove,
        "upgrade": upgrade_cmd,
        "versions": versions_cmd,
        "execpath": execpath_cmd,
        "commands": [
            (
                Command(
                    "add-github-appimage",
                    "Adds installation candidates for github appimages",
                    [PosArgs("owner/repo", "Package to add to sources")],
                ),
                add_cmd,
            ),
            (
                Command(
                    "install-github-appimage",
                    "Adds and installs github appimages",
                    [
                        FlagArg("-l", "--nolauncher", "Don't install .desktop files"),
                        FlagArg("-p", "--path", "Add installed package to the path"),
                        ValueArg(
                            "-v", "--version", "Specify a version for installation"
                        ),
                        PosArgs("owner/repo", "Package to add to sources and install"),
                    ],
                ),
                add_install_cmd,
            ),
        ],
        "attributes": [
            (
                "user_select_filter",
                "Filter for appimage downloads",
                user_select_filter_modify,
                user_select_filter_show,
            )
        ],
    },
)
