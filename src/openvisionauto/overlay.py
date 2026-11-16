from __future__ import annotations

import argparse
import sys
import tkinter as tk


def parse_args() -> argparse.Namespace:
    """Parse command-line arguments for overlay configuration."""
    parser = argparse.ArgumentParser(
        description="Draw a temporary highlight rectangle overlay"
    )
    parser.add_argument("--x", type=int, required=True)
    parser.add_argument("--y", type=int, required=True)
    parser.add_argument("--w", type=int, required=True)
    parser.add_argument("--h", type=int, required=True)
    parser.add_argument("--duration-ms", type=int, default=700)
    parser.add_argument("--color", default="#ff0000")
    parser.add_argument("--thickness", type=int, default=3)
    parser.add_argument("--show-center", action="store_true")
    return parser.parse_args()


def main() -> int:
    """Create temporary highlight border windows.
    
    Uses 4 separate top-level windows for borders instead of transparent
    backgrounds, which is more reliable across Linux/X11 environments.
    """
    args = parse_args()

    x = max(0, args.x)
    y = max(0, args.y)
    w = max(8, args.w)
    h = max(8, args.h)
    thickness = max(1, args.thickness)
    duration_ms = max(50, args.duration_ms)

    root = tk.Tk()
    root.withdraw()

    # Ensure border thickness doesn't exceed half the rectangle dimensions
    border_thickness = min(thickness, max(1, min(w, h) // 2))

    # Define 4 border rectangles: top, bottom, left, right.
    rectangles: list[tuple[int, int, int, int]] = [
        (x, y, w, border_thickness),  # Top border
        (x, y + h - border_thickness, w, border_thickness),  # Bottom border
        (x, y, border_thickness, h),  # Left border
        (x + w - border_thickness, y, border_thickness, h),  # Right border
    ]

    if args.show_center:
        center_x = x + w // 2
        center_y = y + h // 2
        arm_half_length = max(border_thickness * 2, min(w, h) // 8)
        horizontal_w = max(border_thickness, min(w, arm_half_length * 2 + border_thickness))
        vertical_h = max(border_thickness, min(h, arm_half_length * 2 + border_thickness))

        rectangles.extend(
            [
                (
                    center_x - horizontal_w // 2,
                    center_y - border_thickness // 2,
                    horizontal_w,
                    border_thickness,
                ),
                (
                    center_x - border_thickness // 2,
                    center_y - vertical_h // 2,
                    border_thickness,
                    vertical_h,
                ),
            ]
        )

    windows: list[tk.Toplevel] = []
    for border_x, border_y, border_w, border_h in rectangles:
        win = tk.Toplevel(root)
        win.overrideredirect(True)
        win.attributes("-topmost", True)
        win.configure(bg=args.color)
        win.geometry(f"{border_w}x{border_h}+{border_x}+{border_y}")
        windows.append(win)

    root.after(duration_ms, root.destroy)
    root.mainloop()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
