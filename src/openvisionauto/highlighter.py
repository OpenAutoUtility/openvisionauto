from __future__ import annotations

import logging
import subprocess
import sys

from .config import HIGHLIGHT_COLOR, HIGHLIGHT_DURATION_SEC, HIGHLIGHT_THICKNESS
from .errors import OverlayError
from .models import Match

LOGGER = logging.getLogger(__name__)


class Highlighter:
    """Overlay helper used to draw temporary highlight borders for matches."""

    def show(
        self,
        match: Match,
        duration: float | None = None,
        color: str | None = None,
        thickness: int | None = None,
        show_center: bool = False,
    ) -> None:
        """Spawn overlay process to highlight one match rectangle.

        Args:
            match: Match rectangle to visualize.
            duration: Overlay lifetime in seconds. ``None`` uses default.
            color: Border color. ``None`` uses default.
            thickness: Border width in pixels. ``None`` uses default.
            show_center: Whether to draw a short cross at the rectangle center.

        Raises:
            OverlayError: If the overlay process cannot be started.
        """
        resolved_duration_sec = duration if duration is not None else HIGHLIGHT_DURATION_SEC
        resolved_duration_ms = int(resolved_duration_sec * 1000)
        resolved_color = color if color is not None else HIGHLIGHT_COLOR
        resolved_thickness = thickness if thickness is not None else HIGHLIGHT_THICKNESS

        cmd = [
            sys.executable,
            "-m",
            "openvisionauto.overlay",
            "--x",
            str(match.x),
            "--y",
            str(match.y),
            "--w",
            str(match.w),
            "--h",
            str(match.h),
            "--duration-ms",
            str(resolved_duration_ms),
            "--color",
            resolved_color,
            "--thickness",
            str(resolved_thickness),
        ]
        if show_center:
            cmd.append("--show-center")

        try:
            # Use subprocess.run with timeout to ensure cleanup
            timeout_sec = max(2.0, resolved_duration_sec + 1.0)
            subprocess.run(
                cmd,
                check=False,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                timeout=timeout_sec,
            )
        except subprocess.TimeoutExpired:
            # Overlay took too long but don't block workflow
            LOGGER.debug("Overlay display timed out after %.1f seconds", timeout_sec)
        except Exception as exc:  # pragma: no cover
            raise OverlayError(str(exc)) from exc

    def safe_show(
        self,
        match: Match,
        duration: float | None = None,
        color: str | None = None,
        thickness: int | None = None,
        show_center: bool = False,
    ) -> None:
        """Best-effort highlight wrapper that never interrupts user actions."""
        try:
            self.show(
                match,
                duration=duration,
                color=color,
                thickness=thickness,
                show_center=show_center,
            )
        except OverlayError as exc:
            LOGGER.warning("Highlight failed but action continues: %s", exc)
