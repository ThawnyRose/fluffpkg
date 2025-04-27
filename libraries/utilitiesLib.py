def user_pick(options: list[str], prompt="Selection"):
    for i, opt in enumerate(options):
        print(f"[{i}] {opt}")
    num = -1
    while not (num >= 0 and num < len(options)):
        try:
            num = int(input(f"{prompt} [0-{len(options)-1}]: "))
        except ValueError:
            pass
    return num


def pathwarn():
    import os

    path = os.environ.get("PATH", "")
    if ".fluffpkg/bin" not in path:
        print(
            "Warning: fluffpkg isn't currently in your path.\nAdd `~/.fluffpkg/bin` to your .bashrc to run commands installed by fluffpkg!"
        )


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
