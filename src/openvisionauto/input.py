from __future__ import annotations

import importlib
import random
import time

from .config import DEFAULT_TIMING
from .models import TimingProfile


class Input:
    """Keyboard text/input helper with optional human-like timing behavior."""

    def __init__(self, timing: TimingProfile | None = None, deterministic: bool | None = None) -> None:
        """Create input helper.

        Args:
            timing: Timing profile. ``None`` uses ``DEFAULT_TIMING``.
            deterministic: Override deterministic mode. ``None`` follows timing profile.
        """
        self.timing = timing or DEFAULT_TIMING
        self.deterministic = self.timing.deterministic_mode if deterministic is None else deterministic

    def _get_pyautogui(self):
        """Lazily import pyautogui to reduce module import constraints."""
        return importlib.import_module("pyautogui")

    def _pause(self, low: float, high: float) -> None:
        """Sleep for a delay interval, deterministic or random based on settings."""
        if self.deterministic:
            time.sleep((low + high) / 2.0)
            return
        time.sleep(random.uniform(low, high))

    def move_to(self, x: int, y: int) -> None:
        """Move the mouse pointer to an absolute screen coordinate."""
        pyautogui = self._get_pyautogui()
        pyautogui.moveTo(x=x, y=y)

    def hover(self, x: int, y: int) -> None:
        """Alias for ``move_to`` for semantic clarity in tests."""
        self.move_to(x, y)

    def click(self, x: int, y: int, button: str = "left") -> None:
        """Click at an absolute screen coordinate."""
        pyautogui = self._get_pyautogui()
        pyautogui.click(x=x, y=y, button=button)

    def type_text(
        self,
        text: str,
        human_like: bool | None = None,
        delay_min: float | None = None,
        delay_max: float | None = None,
    ) -> None:
        """Type text into the active UI control.

        Args:
            text: Text content to type.
            human_like: Whether to use per-character delays. ``None`` uses timing default.
            delay_min: Minimum delay between characters in seconds.
            delay_max: Maximum delay between characters in seconds.
        """
        pyautogui = self._get_pyautogui()
        use_human = self.timing.human_like_default if human_like is None else human_like
        if not use_human:
            pyautogui.write(text)
            return

        low = self.timing.typing_delay_min if delay_min is None else delay_min
        high = self.timing.typing_delay_max if delay_max is None else delay_max

        for ch in text:
            pyautogui.write(ch)
            self._pause(low, high)
            if ch in "/-_.":
                time.sleep(self.timing.special_char_extra_delay)

    def press(self, key: str, human_like: bool | None = None) -> None:
        """Press one key.

        Args:
            key: Key name understood by pyautogui (for example ``"enter"``).
            human_like: Whether to apply pre/post action delays.
        """
        pyautogui = self._get_pyautogui()
        use_human = self.timing.human_like_default if human_like is None else human_like
        if use_human:
            self._pause(self.timing.key_press_delay_min, self.timing.key_press_delay_max)
        pyautogui.press(key)
        if use_human:
            self._pause(self.timing.key_post_delay_min, self.timing.key_post_delay_max)

    def hotkey(self, *keys: str, human_like: bool | None = None) -> None:
        """Send a key combination.

        Args:
            *keys: Ordered key sequence, for example ``("ctrl", "v")``.
            human_like: Whether to apply delay between key down/up events.
        """
        pyautogui = self._get_pyautogui()
        use_human = self.timing.human_like_default if human_like is None else human_like
        if not use_human:
            pyautogui.hotkey(*keys)
            return

        for key in keys:
            pyautogui.keyDown(key)
            self._pause(self.timing.hotkey_gap_min, self.timing.hotkey_gap_max)
        for key in reversed(keys):
            pyautogui.keyUp(key)
            self._pause(self.timing.hotkey_gap_min, self.timing.hotkey_gap_max)

    def clear_text(self) -> None:
        """Clear active input field using Ctrl+A followed by Backspace."""
        self.hotkey("ctrl", "a")
        self.press("backspace")
