from pathlib import Path
import json

_installed = []
installed_path = Path("~/.fluffpkg/installed").expanduser()
loaded = False


def load():
    global _installed, loaded
    loaded = True
    if installed_path.exists():
        with open(installed_path, "r") as f:
            _installed = json.load(f)
    else:
        print(
            "Warning: No 'installed' list found. This is OK if you have just installed fluffpkg, otherwise it is a MAJOR ISSUE!"
        )
        with open(installed_path, "w+") as f:
            default = "[]"
            f.write(default)
            _installed = json.loads(default)


def checkload():
    if not loaded:
        load()


def savechanges():
    with open(installed_path, "w+") as f:
        json.dump(_installed, f)


def mark_installed(candidate, version, launcher, path, **kwargs):
    checkload()
    _installed.append(
        {
            "name": candidate["name"],
            "version": version,
            "package_name": candidate["package_name"],
            "launcher": launcher,
            "path": path,
            "module": candidate["module"],
            "source": candidate.get("source", "unknown unknown"),
            **kwargs,
        }
    )
    savechanges()


def unmark_installed(package):
    checkload()
    global _installed
    _installed = [pkg for pkg in _installed if pkg["name"] != package]
    savechanges()


def check_installed(candidate):
    checkload()
    for i in _installed:
        if i["package_name"] == candidate["package_name"]:
            return True
    return False


def query(package):
    checkload()
    for i in _installed:
        if i["package_name"] == package:
            return i
    return False


def list():
    checkload()
    return _installed


if __name__ == "__main__":
    load()
