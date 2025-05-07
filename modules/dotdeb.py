from pathlib import Path
import requests
import re
import copy
import os
from libraries.dataClasses import (
    Candidate,
    Installation,
)
from libraries.exceptions import (
    APICallFailed,
    ModuleError,
    AlreadyInstalled,
    SpecificVersion,
    NoCandidate,
    AlreadyNewest,
)
from libraries.utilitiesLib import download_file
from libraries import manageInstalledLib
from libraries import launcherLib
from libraries import pathLib
from libraries import moduleLib
from libraries import sourcesLib


def get_page(url: str):
    response = requests.get(url)
    if response.status_code != 200:
        raise APICallFailed(f"Failed to get index page by url: {url}")
    return response.text


amd_arch = {"x86_64": "amd64"}


def run_search(
    searches: list[dict], data: dict, target: str, version_filter: str = ""
) -> dict:
    searches = copy.deepcopy(searches)
    search = searches.pop(0)
    if search["kind"] == "per_line":
        data[target] = []
        for line in get_page(search["url"]).split("\n"):
            line = line.strip()
            match = re.search(search["regex"], line.strip())
            if match is None:
                continue
            groups = match.groups()
            match_contents = {}
            for i, k in enumerate(search["regex_groups"]):
                match_contents[k] = groups[i]
            data[target].append(match_contents)

    elif search["kind"] == "filter_version":
        if version_filter == "":
            return data
        elif version_filter == "install-newest":
            data = sorted(
                data[target],
                key=lambda x: x["version"],
                reverse=True,
            )[0]
        else:
            data = [x for x in data[target] if x["version"] == version_filter][0]

    elif search["kind"] == "populate_system":
        import platform

        p = platform.freedesktop_os_release()
        data["system_id"] = p["ID"].lower()
        data["System_Id"] = p["ID"].title()
        data["system_version_name"] = p["VERSION_CODENAME"].lower()
        data["System_Version_Name"] = p["VERSION_CODENAME"].title()

        m = platform.machine()
        data["system_arch"] = m.lower()
        data["System_Arch"] = m.title()
        data["system_arch_amd"] = amd_arch.get(m.lower(), "none").lower()
        data["System_Arch_Amd"] = amd_arch.get(m.lower(), "none").title()

    elif search["kind"] == "one_shot":
        page = get_page(search["url"].format(**data))
        match = re.search(search["regex"], page)
        if match is None:
            raise ModuleError("Unable to match one-shot regex")
        groups = match.groups()
        for i, k in enumerate(search["regex_groups"]):
            data[k] = groups[i]

    elif search["kind"] == "construct":
        data[search["name"]] = search["value"].format(**data)

    elif search["kind"] == "target":
        if search["target"] == "versions":
            for i in range(len(data[target])):
                item = data[target][i]
                if "sv1" in item or "sv2" in item or "sv3" in item:
                    data[target][i]["semver"] = (
                        item.get("sv3", "0")
                        + "."
                        + item.get("sv2", "0")
                        + "."
                        + item.get("sv1", "0")
                    )
                if "semver" in item:
                    data[target][i]["version"] = item["semver"]
        elif search["target"] == "download_url":
            url = search["url"].format(**data)
            data["download_url"] = url
            # if "filename" not in data:
            #     data["filename"] = url.rsplit("/", 1)[1]
        else:
            ModuleError(f"Unknown target: {search['target']}")
        if target == search["target"]:
            return data

    else:
        ModuleError(f"Unknown kind: {search['kind']}")

    if len(searches) != 0:
        data = run_search(searches, data, target, version_filter=version_filter)
    return data


def setup() -> None:
    Path("~/.fluffpkg/data/dotdeb/files/").expanduser().mkdir(
        parents=True, exist_ok=True
    )

    Path("~/.fluffpkg/data/dotdeb/launcher/").expanduser().mkdir(
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
    data=None,
) -> None:
    if manageInstalledLib.check_installed(candidate) and not upgrade:
        raise AlreadyInstalled(candidate.package_name)
    setup()
    assert candidate.module == "dotdeb"

    version_locked = False if version is None else True
    version_filter = "install-newest" if version is None else version
    if data is None:
        searches = candidate.module_data["info_gathering"]
        data = run_search(searches, {}, "download_url", version_filter=version_filter)
    download_url = data["download_url"]
    filename = (
        data["filename"] if "filename" in data else download_url.rsplit("/", 1)[1]
    )
    executable_path = Path("~/.fluffpkg/data/dotdeb/files/").expanduser() / filename
    try:
        download_file(download_url, output=executable_path, prettyname=filename)
    except requests.exceptions.HTTPError:
        print()
        raise ModuleError(
            "Failed to download. This could be an error in the package definitions, or this package may not be available for your system."
        )

    print("This module requires sudo to install packages.")
    cmd = f"sudo apt install -y {executable_path}"
    print(f"Executing command: {cmd}")
    exit_code = os.WEXITSTATUS(os.system(cmd))

    if exit_code != 0:
        raise ModuleError(f"dpkg failed to install, aborting (exit code {exit_code})")

    candidate.name = data["deb_package_name"]
    manageInstalledLib.mark_installed(
        candidate,
        data["version"],
        str(executable_path.resolve()),
        version_locked=version_locked,
    )
    print(f"{candidate.name} successfully installed!")

    own_launcher = candidate.module_data["manages_own_launcher"]
    own_path = candidate.module_data["manages_own_path"]

    if nolauncher and own_launcher and not upgrade:
        print(
            "--nolauncher ignored: this package manages it's own launcher on installation"
        )

    if not nolauncher and not own_launcher:
        launcherLib.add_launcher(
            candidate.package_name,
            candidate.name,
            candidate.package_name,
            candidate.categories,
        )

    if path and own_path and not upgrade:
        print(
            "--path ignored: this package manages it's own path entries on installation"
        )

    if path and not own_path:
        pathLib.add_path(candidate.package_name)


def remove_cmd(installation: Installation, cmd_args: dict) -> None:
    remove(installation)


def remove(installation: Installation, upgrade: bool = False) -> None:
    assert installation.module == "dotdeb"
    package = installation.package_name

    if installation.launcher:
        launcherLib.remove_launcher(package)
    if installation.path:
        pathLib.remove_path(package)

    try:
        dotdeb = Path(installation.executable_path)
        dotdeb.unlink()
    except FileNotFoundError:
        pass

    print("This module requires sudo to remove packages.")
    cmd = f"sudo apt remove -y {installation.name}"
    print(f"Executing command: {cmd}")
    exit_code = os.WEXITSTATUS(os.system(cmd))

    if exit_code != 0:
        raise ModuleError(f"dpkg failed to remove, aborting (exit code {exit_code})")

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
        raise NoCandidate()

    searches = candidate.module_data["info_gathering"]
    data = run_search(searches, {}, "download_url", version_filter="install-newest")

    new_version = data["version"]
    if new_version == installation.version:
        raise AlreadyNewest(installation.package_name)
    remove(installation, upgrade=True)
    install(
        candidate, not installation.launcher, installation.path, upgrade=True, data=data
    )


def versions_cmd(candidate: Candidate, cmd_args: dict) -> None:
    searches = candidate.module_data["info_gathering"]
    data = {}
    data = run_search(searches, data, target="versions")
    versions = [v["version"] for v in data["versions"][::-1]]
    if len(versions) > 15:
        versions = versions[:15] + ["..."]
    print("\n".join(versions))


moduleLib.register(
    "dotdeb",
    {
        "install": install_cmd,
        "remove": remove_cmd,
        "upgrade": upgrade_cmd,
        "versions": versions_cmd,
        # "execpath": execpath_cmd,
        # "commands": [],
        # "attributes": [],
    },
)
