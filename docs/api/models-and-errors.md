# Models and Errors

## Data Models

### Match

```python
@dataclass(frozen=True)
class Match:
    x: int
    y: int
    w: int
    h: int
    score: float

    @property
    def center(self) -> tuple[int, int]:
        ...
```

Represents one template match rectangle and confidence score.

- `x`: absolute screen X of the matched top-left corner.
- `y`: absolute screen Y of the matched top-left corner.
- `w`: matched width in pixels.
- `h`: matched height in pixels.
- `score`: normalized confidence in `[0.0, 1.0]`.

`match.center` returns `(x + w // 2, y + h // 2)`.

### Region

```python
@dataclass(frozen=True)
class Region:
    x: int
    y: int
    w: int
    h: int
```

Represents a screen rectangle used for capture or search scoping.

- `x`: absolute screen X of the region top-left corner.
- `y`: absolute screen Y of the region top-left corner.
- `w`: region width in pixels.
- `h`: region height in pixels.

### TimingProfile

```python
@dataclass(frozen=True)
class TimingProfile:
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
```

Defines timing behavior for `Input` operations.

### EnvironmentReport

```python
@dataclass
class EnvironmentReport:
    is_supported: bool
    platform_ok: bool
    display_ok: bool
    x11_ok: bool
    tk_ok: bool
    xdotool_ok: bool
    wmctrl_ok: bool
    ibus_ok: bool
    ffmpeg_ok: bool
    messages: list[str]
```

Structured environment diagnostics.

## Exceptions

All project-specific exceptions inherit from `OpenVisionAutoError`.

- `OpenVisionAutoError`: base exception.
- `TemplateNotFoundError`: template path missing or unreadable.
- `WaitTimeoutError`: waiting for appearance timed out.
- `VanishTimeoutError`: waiting for disappearance timed out.
- `EnvironmentNotSupportedError`: runtime prerequisites not met.
- `OverlayError`: highlight overlay failed.
- `RecorderError`: recorder start/stop failed.

## Typical Handling

```python
from openvisionauto import Screen, WaitTimeoutError

screen = Screen()
try:
    screen.wait("submit.png", timeout=5)
except WaitTimeoutError:
    print("Image not found before timeout")
```