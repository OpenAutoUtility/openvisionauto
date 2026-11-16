from openvisionauto import Screen


def main() -> None:
    screen = Screen()
    screen.check_env(strict=True)

    # Example: wait -> auto-highlight -> click -> wait vanish
    screen.wait("assets/login_button.png", timeout=10).click().wait_vanish(timeout=8)

    # Region-constrained search for visual matching.
    screen.region(100, 200, 500, 300).wait("assets/ok_button.png", timeout=6).click()


if __name__ == "__main__":
    main()
