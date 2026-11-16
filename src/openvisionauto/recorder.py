from __future__ import annotations

import os
import platform
import shutil
import subprocess
from pathlib import Path

from .errors import RecorderError


class Recorder:
    """Simple ffmpeg-based screen recorder for Linux and Windows desktops."""

    def __init__(self, display: str | None = None) -> None:
        """Create recorder.

        Args:
            display: X11 display string (for example ``":0"``).
                     Only used on Linux. ``None`` reads ``DISPLAY`` env var.
        """
        self.display = display or os.environ.get("DISPLAY", ":0")
        self._proc: subprocess.Popen[bytes] | None = None

    def _build_cmd(self, output_file: str, fps: int) -> list[str]:
        """Build ffmpeg command with platform-specific capture source."""
        system = platform.system()
        if system == "Windows":
            return [
                "ffmpeg",
                "-y",
                "-framerate",
                str(fps),
                "-f",
                "gdigrab",
                "-i",
                "desktop",
                output_file,
            ]
        return [
            "ffmpeg",
            "-y",
            "-video_size",
            "1920x1080",
            "-framerate",
            str(fps),
            "-f",
            "x11grab",
            "-i",
            self.display,
            output_file,
        ]

    def start(self, output_file: str | Path, fps: int = 15) -> None:
        """Start recording the desktop.

        Args:
            output_file: Video file output path.
            fps: Capture frame rate.

        Raises:
            RecorderError: If ffmpeg is missing or recorder is already running.
        """
        if shutil.which("ffmpeg") is None:
            raise RecorderError("ffmpeg is required for recording APIs")
        if self._proc is not None and self._proc.poll() is None:
            raise RecorderError("Recorder is already running")

        cmd = self._build_cmd(str(output_file), fps)
        self._proc = subprocess.Popen(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    def stop(self) -> None:
        """Stop recording if active. Safe to call repeatedly."""
        if self._proc is None:
            return
        if self._proc.poll() is None:
            self._proc.terminate()
            self._proc.wait(timeout=3)
        self._proc = None
