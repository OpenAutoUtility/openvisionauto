from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True)
class Match:
    """Rectangle and confidence returned by template matching.

    Attributes:
        x: Absolute screen X of the matched top-left corner.
        y: Absolute screen Y of the matched top-left corner.
        w: Matched width in pixels.
        h: Matched height in pixels.
        score: Normalized confidence score in [0.0, 1.0].
    """

    x: int
    y: int
    w: int
    h: int
    score: float

    @property
    def center(self) -> tuple[int, int]:
        """Return center point ``(x + w // 2, y + h // 2)``."""
        return (self.x + self.w // 2, self.y + self.h // 2)


@dataclass(frozen=True)
class TimingProfile:
    """Timing configuration used by :class:`openvisionauto.input.Input`."""

    typing_delay_min: float
    typing_delay_max: float
    special_char_extra_delay: float
    key_press_delay_min: float
    key_press_delay_max: float
    key_post_delay_min: float
    key_post_delay_max: float
    hotkey_gap_min: float
    hotkey_gap_max: float
    human_like_default: bool = True
    deterministic_mode: bool = False


@dataclass
class EnvironmentReport:
    """Result container for environment compatibility checks."""

    is_supported: bool
    platform_ok: bool
    display_ok: bool
    x11_ok: bool
    tk_ok: bool
    xdotool_ok: bool
    wmctrl_ok: bool
    ibus_ok: bool
    ffmpeg_ok: bool
    messages: list[str] = field(default_factory=list)


@dataclass(frozen=True)
class Region:
    """Search/capture rectangle in absolute screen coordinates.

    Attributes:
        x: Absolute screen X of the region top-left corner.
        y: Absolute screen Y of the region top-left corner.
        w: Region width in pixels.
        h: Region height in pixels.
    """

    x: int
    y: int
    w: int
    h: int
