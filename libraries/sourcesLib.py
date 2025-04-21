from pathlib import Path
import json

_candidates = []
loaded = False

defaultSourcePath = "~/.fluffpkg/source"
defaultSource = f"File {defaultSourcePath}"


def load():
    global _candidates, loaded
    loaded = True
    candidates = []
    src_path = Path("~/.fluffpkg/sources.lst").expanduser()
    if src_path.exists():
        with open(src_path, "r") as f:
            sourcesText = f.read()
    else:
        sourcesText = defaultSource + "\n"
        with open(src_path, "w+") as f:
            f.write(sourcesText)
        src_file_path = Path(defaultSourcePath).expanduser()
        if not src_file_path.exists():
            with open(src_file_path, "w+") as f:
                f.write("")
    for line in sourcesText.split("\n"):
        if len(line) == 0:
            continue
        source_type, url = line.split(" ", 1)
        if source_type == "File":
            with open(Path(url).expanduser(), "r") as f:
                these_candidates = json.load(f)
                for candidate in these_candidates:
                    candidate["source"] = line
                candidates += these_candidates
        else:
            print(f"Unknown source type: {source_type}")
    _candidates = candidates


def checkload():
    if not loaded:
        load()


def query(package):
    checkload()
    package = package.lower()
    strong_recommend = []
    weak_recommend = []
    for candidate in _candidates:
        if package == candidate["package_name"]:
            return ("found", candidate)
        if package in candidate["name"].lower():
            strong_recommend.append(candidate)

    if len(strong_recommend) != 0:
        return ("strong_recommend", strong_recommend)
    if len(weak_recommend) != 0:
        return ("weak_recommend", weak_recommend)
    return ()


def check_existing_source(package):
    for candidate in _candidates:
        if package == candidate["package_name"]:
            return True
    return False


def add(candidate, checkExists=True):
    checkload()

    if check_existing_source(candidate["package_name"]):
        if checkExists:
            print(
                f"Package '{candidate['package_name']}' is already sourced. Try `install`."
            )
            exit()
        else:
            return

    default_source = Path(defaultSourcePath).expanduser()

    with open(default_source, "r") as f:
        default_candidates = json.load(f)

    default_candidates.append(candidate)

    with open(default_source, "w") as f:
        json.dump(default_candidates, f)

    global loaded
    loaded = False


def list():
    checkload()
    return _candidates


if __name__ == "__main__":
    load()
    print(query("Ultimaker"))
