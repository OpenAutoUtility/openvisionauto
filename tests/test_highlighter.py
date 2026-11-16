import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parents[1]
SRC_DIR = ROOT_DIR / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))


def main() -> int:
    from openvisionauto import Screen
    from openvisionauto.errors import OpenVisionAutoError, WaitTimeoutError

    image_path = Path(__file__).with_name("calc_num_8.png")
    screen = Screen()

    print(f"Using template: {image_path}")
    print("Make sure the calculator digit 8 is visible on screen before running.")

    try:
        handle = screen.wait(image_path, timeout=10)
        print(f"Matched at center={handle.center}, score={handle.score:.4f}")
        handle.highlight(duration=3, show_center=True)
        print("Highlight displayed with center cross.")
        return 0
    except WaitTimeoutError as exc:
        print(f"Timed out waiting for template: {exc}")
        return 1
    except OpenVisionAutoError as exc:
        print(f"OpenVisionAuto error: {exc}")
        return 2
    except FileNotFoundError as exc:
        print(f"Required file not found: {exc}")
        return 3


if __name__ == "__main__":
    raise SystemExit(main())