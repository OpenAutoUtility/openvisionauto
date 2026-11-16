from __future__ import annotations

import importlib
import logging
import platform
import subprocess
import time
from dataclasses import dataclass
from pathlib import Path
from typing import TYPE_CHECKING

from .config import HIGHLIGHT_ENABLED
from .envcheck import check_env
from .highlighter import Highlighter
from .input import Input
from .models import Match, Region

if TYPE_CHECKING:
    from .vision import Vision

LOGGER = logging.getLogger(__name__)


def _get_pyautogui():
    """Lazily import pyautogui to keep module import cross-platform friendly."""
    return importlib.import_module("pyautogui")


@dataclass
class MatchHandle:
    """Chainable handle around a resolved image match.

    A handle stores the matched rectangle and allows fluent follow-up actions
    such as highlight, click, hover, and waiting for disappearance.
    """

    screen: "Screen"
    image: str
    match: Match
    region: Region | None = None

    @property
    def center(self) -> tuple[int, int]:
        """Return the match center in absolute screen coordinates."""
        return self.match.center

    @property
    def score(self) -> float:
        """Return normalized match confidence in the range [0.0, 1.0]."""
        return self.match.score

    def highlight(
        self,
        duration: float | None = None,
        color: str | None = None,
        thickness: int | None = None,
        show_center: bool = False,
        showCenter: bool | None = None,
    ) -> MatchHandle:
        """Render a temporary highlight overlay around the current match.

        Args:
            duration: Overlay lifetime in seconds. ``None`` uses config default.
            color: Border color string (for example ``"#ff0000"``). ``None`` uses default.
            thickness: Border thickness in pixels. ``None`` uses default.
            show_center: Whether to mark the rectangle center with a short cross.
            showCenter: Alias for ``show_center``.

        Returns:
            The current handle for method chaining.
        """
        if showCenter is not None:
            show_center = showCenter
        self.screen._highlight_match(
            self.match,
            duration=duration,
            color=color,
            thickness=thickness,
            show_center=show_center,
        )
        return self

    def click(
        self,
        button: str = "left",
        highlight: bool = False,
        hold_seconds: float | None = None,
    ) -> MatchHandle:
        """Click at the current match center.

        Args:
            button: Mouse button name accepted by pyautogui (``"left"``, ``"right"``, etc.).
            highlight: Whether to show highlight overlay after clicking.
            hold_seconds: How long to keep the mouse button pressed before release.
                ``None`` or non-positive values use a normal click.

        Returns:
            The current handle for method chaining.
        """
        x, y = self.match.center
        pyautogui = _get_pyautogui()
        if hold_seconds is not None and hold_seconds > 0:
            pyautogui.mouseDown(x=x, y=y, button=button)
            time.sleep(hold_seconds)
            pyautogui.mouseUp(x=x, y=y, button=button)
        else:
            pyautogui.click(x=x, y=y, button=button)
        if highlight:
            self.highlight()
        return self

    def double_click(self, highlight: bool = False) -> MatchHandle:
        """Double-click at the current match center.

        Args:
            highlight: Whether to show highlight overlay after the action.

        Returns:
            The current handle for method chaining.
        """
        x, y = self.match.center
        pyautogui = _get_pyautogui()
        pyautogui.doubleClick(x=x, y=y)
        if highlight:
            self.highlight()
        return self

    def right_click(
        self,
        highlight: bool = False,
        hold_seconds: float | None = None,
    ) -> MatchHandle:
        """Right-click at the current match center.

        Args:
            highlight: Whether to show highlight overlay after the action.
            hold_seconds: How long to keep the right button pressed before release.
                ``None`` or non-positive values use a normal click.

        Returns:
            The current handle for method chaining.
        """
        return self.click(button="right", highlight=highlight, hold_seconds=hold_seconds)

    def hover(self, highlight: bool = True, duration: float | None = None) -> "MatchHandle":
        """Move the pointer to the current match center and optionally hold it there.

        Args:
            highlight: Whether to show highlight overlay before pointer move.
            duration: How many seconds to keep the pointer at the match center.
                ``None`` means move and return immediately.

        Returns:
            The current handle for method chaining.
        """
        if highlight:
            self.highlight()
        x, y = self.match.center
        pyautogui = _get_pyautogui()
        pyautogui.moveTo(x, y)
        if duration is not None and duration > 0:
            time.sleep(duration)
        return self

    def wait_vanish(
        self,
        timeout: float,
        confidence: float | None = None,
        poll: float | None = None,
        strict: bool = True,
    ) -> bool:
        """Wait until this handle's image is no longer detected.

        Args:
            timeout: Max wait duration in seconds.
            confidence: Match threshold. ``None`` uses configured default.
            poll: Poll interval in seconds. ``None`` uses configured default.
            strict: If ``True``, raise on timeout. If ``False``, return ``False``.

        Returns:
            ``True`` if vanished before timeout; ``False`` only when ``strict=False``.
        """
        return self.screen.wait_vanish(
            self.image,
            timeout=timeout,
            confidence=confidence,
            poll=poll,
            region=self.region,
            strict=strict,
        )


class RegionScreen:
    """A Screen proxy that automatically scopes all operations to one region."""

    def __init__(self, screen: Screen, region: Region) -> None:
        self._screen = screen
        self._region = region

    def find(self, image: str | Path, confidence: float | None = None) -> MatchHandle | None:
        """Find one image inside this pre-scoped region."""
        return self._screen.find(image=image, confidence=confidence, region=self._region)

    def wait(
        self,
        image: str | Path,
        timeout: float,
        confidence: float | None = None,
        poll: float | None = None,
    ) -> MatchHandle:
        """Wait for an image to appear inside this pre-scoped region."""
        return self._screen.wait(
            image=image,
            timeout=timeout,
            confidence=confidence,
            poll=poll,
            region=self._region,
        )

    def click(
        self,
        image: str | Path,
        timeout: float = 10,
        confidence: float | None = None,
        poll: float | None = None,
        highlight: bool = False,
        hold_seconds: float | None = None,
    ) -> MatchHandle:
        """Wait for and click an image inside this pre-scoped region."""
        return self._screen.click(
            image=image,
            timeout=timeout,
            confidence=confidence,
            poll=poll,
            highlight=highlight,
            hold_seconds=hold_seconds,
            region=self._region,
        )

    def wait_vanish(
        self,
        image: str | Path,
        timeout: float,
        confidence: float | None = None,
        poll: float | None = None,
        strict: bool = True,
    ) -> bool:
        """Wait for an image to disappear inside this pre-scoped region."""
        return self._screen.wait_vanish(
            image=image,
            timeout=timeout,
            confidence=confidence,
            poll=poll,
            region=self._region,
            strict=strict,
        )


class Screen:
    """High-level image-driven automation API for Linux and Windows desktops."""

    def __init__(self) -> None:
        from .vision import Vision

        self.vision = Vision()
        self.highlighter = Highlighter()
        self.input = Input()

    def region(self, x: int, y: int, w: int, h: int) -> RegionScreen:
        """Create a region-scoped helper.

        Args:
            x: Absolute screen X coordinate of the region's top-left corner.
            y: Absolute screen Y coordinate of the region's top-left corner.
            w: Region width in pixels.
            h: Region height in pixels.

        Returns:
            A ``RegionScreen`` instance that limits find/wait/click operations
            to ``Region(x, y, w, h)``.
        """
        return RegionScreen(self, Region(x, y, w, h))

    def _highlight_match(
        self,
        match: Match,
        duration: float | None = None,
        color: str | None = None,
        thickness: int | None = None,
        show_center: bool = False,
    ) -> None:
        """Display a temporary highlight for one match rectangle."""
        self.highlighter.safe_show(
            match,
            duration=duration,
            color=color,
            thickness=thickness,
            show_center=show_center,
        )

    @staticmethod
    def _normalize_region(region: Region | tuple[int, int, int, int] | None) -> Region | None:
        """Convert tuple region values to ``Region`` while preserving ``None``."""
        if region is None:
            return None
        if isinstance(region, Region):
            return region
        x, y, w, h = region
        return Region(int(x), int(y), int(w), int(h))

    def find(
        self,
        image: str | Path,
        confidence: float | None = None,
        region: Region | tuple[int, int, int, int] | None = None,
    ) -> MatchHandle | None:
        """Find an image once and return a chainable handle when matched.

        Args:
            image: Template image path.
            confidence: Match threshold. ``None`` uses configured default.
            region: Search region as ``Region`` or ``(x, y, w, h)`` tuple.

        Returns:
            ``MatchHandle`` when found, otherwise ``None``.
        """
        normalized_region = self._normalize_region(region)
        match = self.vision.find(image=image, confidence=confidence, region=region)
        if match is None:
            return None
        return MatchHandle(screen=self, image=str(image), match=match, region=normalized_region)

    def wait(
        self,
        image: str | Path,
        timeout: float,
        confidence: float | None = None,
        poll: float | None = None,
        region: Region | tuple[int, int, int, int] | None = None,
    ) -> MatchHandle:
        """Wait until an image appears and return a chainable handle.

        Args:
            image: Template image path.
            timeout: Max wait duration in seconds.
            confidence: Match threshold. ``None`` uses configured default.
            poll: Poll interval in seconds. ``None`` uses configured default.
            region: Search region as ``Region`` or ``(x, y, w, h)`` tuple.

        Returns:
            A ``MatchHandle`` for fluent actions.
        """
        normalized_region = self._normalize_region(region)
        match = self.vision.wait(image=image, timeout=timeout, confidence=confidence, poll=poll, region=region)
        return MatchHandle(screen=self, image=str(image), match=match, region=normalized_region)

    def wait_vanish(
        self,
        image: str | Path,
        timeout: float,
        confidence: float | None = None,
        poll: float | None = None,
        region: Region | tuple[int, int, int, int] | None = None,
        strict: bool = True,
    ) -> bool:
        """Wait until an image disappears from the screen or region.

        Args:
            image: Template image path.
            timeout: Max wait duration in seconds.
            confidence: Match threshold. ``None`` uses configured default.
            poll: Poll interval in seconds. ``None`` uses configured default.
            region: Search region as ``Region`` or ``(x, y, w, h)`` tuple.
            strict: If ``True``, raise on timeout. If ``False``, return ``False``.

        Returns:
            ``True`` if image vanished before timeout.
        """
        return self.vision.wait_vanish(
            image=image,
            timeout=timeout,
            confidence=confidence,
            poll=poll,
            region=region,
            strict=strict,
        )

    def click(
        self,
        image: str | Path,
        timeout: float = 10,
        confidence: float | None = None,
        poll: float | None = None,
        highlight: bool = False,
        hold_seconds: float | None = None,
        region: Region | tuple[int, int, int, int] | None = None,
    ) -> MatchHandle:
        """Wait for an image and click its center.

        Args:
            image: Template image path.
            timeout: Max wait duration in seconds.
            confidence: Match threshold. ``None`` uses configured default.
            poll: Poll interval in seconds. ``None`` uses configured default.
            highlight: Whether to show highlight overlay after clicking.
            hold_seconds: How long to keep the mouse button pressed before release.
                ``None`` or non-positive values use a normal click.
            region: Search region as ``Region`` or ``(x, y, w, h)`` tuple.

        Returns:
            A ``MatchHandle`` representing the clicked match.
        """
        handle = self.wait(
            image=image,
            timeout=timeout,
            confidence=confidence,
            poll=poll,
            region=region,
        )
        return handle.click(highlight=highlight, hold_seconds=hold_seconds)

    def click_and_wait_vanish(
        self,
        click_image: str | Path,
        vanish_image: str | Path | None = None,
        timeout: float = 10,
        confidence: float | None = None,
        poll: float | None = None,
        highlight: bool = False,
        hold_seconds: float | None = None,
        region: Region | tuple[int, int, int, int] | None = None,
        strict: bool = True,
    ) -> bool:
        """Click one image and wait for an image to disappear.

        Args:
            click_image: Image used for click targeting.
            vanish_image: Image to monitor for disappearance. ``None`` uses ``click_image``.
            timeout: Max wait duration in seconds.
            confidence: Match threshold. ``None`` uses configured default.
            poll: Poll interval in seconds. ``None`` uses configured default.
            highlight: Whether to highlight before click.
            hold_seconds: How long to keep the mouse button pressed before release.
                ``None`` or non-positive values use a normal click.
            region: Search region as ``Region`` or ``(x, y, w, h)`` tuple.
            strict: If ``True``, raise on timeout. If ``False``, return ``False``.

        Returns:
            ``True`` if the vanish target disappears before timeout.
        """
        self.click(
            image=click_image,
            timeout=timeout,
            confidence=confidence,
            poll=poll,
            highlight=highlight,
            hold_seconds=hold_seconds,
            region=region,
        )
        target = vanish_image if vanish_image is not None else click_image
        return self.wait_vanish(
            image=target,
            timeout=timeout,
            confidence=confidence,
            poll=poll,
            region=region,
            strict=strict,
        )

    def activate_window(self, title_substring: str) -> bool:
        """Attempt to activate a window by title fragment.

        On Windows, uses ``pyautogui.getWindowsWithTitle`` (sub-string match).
        On Linux, tries ``xdotool`` first and falls back to ``wmctrl``.

        Args:
            title_substring: Case-sensitive title fragment used to locate the window.

        Returns:
            ``True`` when activation succeeds, otherwise ``False``.
        """
        system = platform.system()
        if system == "Windows":
            return self._activate_window_win32(title_substring)
        return self._activate_window_linux(title_substring)

    @staticmethod
    def _activate_window_win32(title_substring: str) -> bool:
        """Activate a window on Windows via pyautogui (pygetwindow)."""
        pyautogui = _get_pyautogui()
        try:
            windows = pyautogui.getWindowsWithTitle(title_substring)
        except Exception:
            LOGGER.debug("pyautogui.getWindowsWithTitle failed for: %s", title_substring)
            return False

        if not windows:
            LOGGER.debug("No window found with title containing: %s", title_substring)
            return False

        try:
            windows[0].activate()
            return True
        except Exception:
            LOGGER.debug("Failed to activate window: %s", title_substring)
            return False

    @staticmethod
    def _activate_window_linux(title_substring: str) -> bool:
        """Activate a window on Linux using xdotool or wmctrl."""
        xdotool_cmd = ["xdotool", "search", "--name", title_substring, "windowactivate"]
        wmctrl_cmd = ["wmctrl", "-a", title_substring]

        try:
            proc = subprocess.run(xdotool_cmd, capture_output=True, check=False)
            if proc.returncode == 0:
                return True
        except FileNotFoundError:
            LOGGER.debug("xdotool not available")

        try:
            proc = subprocess.run(wmctrl_cmd, capture_output=True, check=False)
            return proc.returncode == 0
        except FileNotFoundError:
            LOGGER.debug("wmctrl not available")
            return False

    def check_env(self, strict: bool = True):
        """Run environment checks for platform, display, and required tools."""
        return check_env(strict=strict)
