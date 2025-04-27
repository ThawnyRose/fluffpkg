from libraries import moduleLib
from libraries.dataClasses import (
    Candidate,
)
from libraries.exceptions import (
    APICallFailed,
)
from datetime import datetime
import requests
import re


def read_index_page(url: str, line_regex: str, regex_groups: str):
    response = requests.get(url)
    if response.status_code != 200:
        raise APICallFailed(f"Failed to get index page by url: {url}")

    matches = []
    for line in response.text.split("\n"):
        match = re.match(line_regex, line.strip())
        if match is None:
            continue
        groups = match.groups()
        #     # enforce semver
        #     semver = re.match(semverReg, groups[1])
        #     if semver is None:
        #         continue
        match_contents = {}
        for i, k in enumerate(regex_groups):
            match_contents[k] = groups[i]
        match_contents["semver"] = (
            match_contents.get("sv3", "0")
            + "."
            + match_contents.get("sv2", "0")
            + "."
            + match_contents.get("sv1", "0")
        )
        matches.append(match_contents)

    sorted_matches = sorted(
        matches,
        key=lambda x: int(x["sv1"]) + int(x["sv2"]) * 100 + int(x["sv3"]) * 100 * 100,
        reverse=True,
    )

    return sorted_matches

    # for m in sorted_matches:
    #     if m is None:
    #         continue
    #     print(m)


def install_cmd(candidate: Candidate, cmd_args: dict) -> None:
    url_type = candidate.module_data.get("url_type", None)
    if url_type == "indexpage":
        line_regex = candidate.module_data["line_regex"]
        regex_groups = candidate.module_data["regex_groups"]
        index_page = read_index_page(candidate.download_url, line_regex, regex_groups)
        newest_entry = index_page[0]
    pass


moduleLib.register(
    "dotdeb",
    {
        "install": install_cmd,
        # "remove": remove_cmd,
        # "upgrade": upgrade_cmd,
        # "versions": versions_cmd,
        # "execpath": execpath_cmd,
        # "commands": [],
        # "attributes": [],
    },
)
