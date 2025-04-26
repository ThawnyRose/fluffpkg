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
