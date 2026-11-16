from __future__ import annotations

import os
import platform
import shutil
import subprocess

from .errors import EnvironmentNotSupportedError
from .models import EnvironmentReport


class EnvCheck:
    """Validate runtime prerequisites for OpenVisionAuto on Linux and Windows desktops."""

    def check(self, strict: bool = True) -> EnvironmentReport:
        """Run platform and dependency checks.

        Args:
            strict: If ``True``, raise when environment is not supported.

        Returns:
            Structured environment report.

        Raises:
            EnvironmentNotSupportedError: If ``strict=True`` and checks fail.
        """
        system = platform.system().lower()
        is_linux = system == "linux"
        is_windows = system == "windows"
        platform_ok = is_linux or is_windows

        tk_ok = True
        try:
            import tkinter  # noqa: F401
        except Exception:
            tk_ok = False

        if is_linux:
            return self._check_linux(strict, platform_ok, tk_ok)
        if is_windows:
            return self._check_windows(strict, platform_ok, tk_ok)

        report = EnvironmentReport(
            is_supported=False,
            platform_ok=False,
            display_ok=False,
            x11_ok=False,
            tk_ok=tk_ok,
            xdotool_ok=False,
            wmctrl_ok=False,
            ibus_ok=False,
            ffmpeg_ok=False,
            messages=["Only Linux and Windows are supported"],
        )
        if strict:
            raise EnvironmentNotSupportedError("; ".join(report.messages))
        return report

    @staticmethod
    def _check_linux(strict: bool, platform_ok: bool, tk_ok: bool) -> EnvironmentReport:
        has_display = bool(os.environ.get("DISPLAY"))

        x11_ok = False
        if has_display:
            try:
                out = subprocess.run(
                    ["sh", "-lc", "echo ${XDG_SESSION_TYPE:-unknown}"],
                    capture_output=True,
                    text=True,
                    check=False,
                )
                x11_ok = out.stdout.strip().lower() in {"x11", "unknown"}
            except Exception:
                x11_ok = False

        xdotool_ok = shutil.which("xdotool") is not None
        wmctrl_ok = shutil.which("wmctrl") is not None
        ibus_ok = shutil.which("ibus") is not None
        ffmpeg_ok = shutil.which("ffmpeg") is not None

        messages: list[str] = []
        if not has_display:
            messages.append("DISPLAY is missing")
        if not x11_ok:
            messages.append("X11 session not detected")
        if not tk_ok:
            messages.append("tkinter is unavailable (install python3-tk)")
        if not (xdotool_ok or wmctrl_ok):
            messages.append("Neither xdotool nor wmctrl is installed")

        supported = platform_ok and has_display and x11_ok and tk_ok and (xdotool_ok or wmctrl_ok)
        report = EnvironmentReport(
            is_supported=supported,
            platform_ok=platform_ok,
            display_ok=has_display,
            x11_ok=x11_ok,
            tk_ok=tk_ok,
            xdotool_ok=xdotool_ok,
            wmctrl_ok=wmctrl_ok,
            ibus_ok=ibus_ok,
            ffmpeg_ok=ffmpeg_ok,
            messages=messages,
        )

        if strict and not report.is_supported:
            raise EnvironmentNotSupportedError("; ".join(report.messages) or "Unsupported environment")
        return report

    @staticmethod
    def _check_windows(strict: bool, platform_ok: bool, tk_ok: bool) -> EnvironmentReport:
        ffmpeg_ok = shutil.which("ffmpeg") is not None

        messages: list[str] = []
        if not tk_ok:
            messages.append("tkinter is unavailable")

        supported = platform_ok and tk_ok
        report = EnvironmentReport(
            is_supported=supported,
            platform_ok=platform_ok,
            display_ok=True,
            x11_ok=False,
            tk_ok=tk_ok,
            xdotool_ok=False,
            wmctrl_ok=False,
            ibus_ok=False,
            ffmpeg_ok=ffmpeg_ok,
            messages=messages,
        )

        if strict and not report.is_supported:
            raise EnvironmentNotSupportedError("; ".join(report.messages) or "Unsupported environment")
        return report


def check_env(strict: bool = True) -> EnvironmentReport:
    """Convenience wrapper for :meth:`EnvCheck.check`."""
    return EnvCheck().check(strict=strict)
