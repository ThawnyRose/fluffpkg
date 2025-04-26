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
