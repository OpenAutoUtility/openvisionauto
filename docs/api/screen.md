# Screen API

## Screen

Main high-level API for image-based UI automation.

### Constructor

```python
screen = Screen()
```

### Methods

#### region(x, y, w, h) -> RegionScreen

Create a region-scoped screen helper.

- `x`: absolute screen X coordinate of the region's top-left corner.
- `y`: absolute screen Y coordinate of the region's top-left corner.
- `w`: region width in pixels.
- `h`: region height in pixels.

The resulting `RegionScreen` limits all later `find`, `wait`, `click`, and
`wait_vanish` operations to that rectangle.

#### find(image, confidence=None, region=None) -> MatchHandle | None

Find a template image once.

- Returns `None` when not found.
- Returns `MatchHandle` when found.
- `region` accepts either `Region` or a tuple `(x, y, w, h)`.

#### wait(image, timeout, confidence=None, poll=None, region=None) -> MatchHandle

Poll until the image appears or timeout occurs.

- Raises `WaitTimeoutError` on timeout.
- `region` accepts either `Region` or a tuple `(x, y, w, h)`.

#### wait_vanish(image, timeout, confidence=None, poll=None, region=None, strict=True) -> bool

Poll until the image disappears.

- Returns `True` on success.
- If `strict=True`, raises `VanishTimeoutError` on timeout.
- If `strict=False`, returns `False` on timeout.
- `region` accepts either `Region` or a tuple `(x, y, w, h)`.

#### click(image, timeout=10, confidence=None, poll=None, highlight=False, region=None) -> MatchHandle

Wait for a match and click it.

- `region` accepts either `Region` or a tuple `(x, y, w, h)`.

#### click_and_wait_vanish(click_image, vanish_image=None, timeout=10, confidence=None, poll=None, highlight=False, region=None, strict=True) -> bool

Click one image and then wait for another image (or itself) to disappear.

#### activate_window(title_substring) -> bool

Try to focus a window using `xdotool`, fallback to `wmctrl`.

#### check_env(strict=True) -> EnvironmentReport

Run environment compatibility checks.

## MatchHandle

Returned by `Screen.find` and `Screen.wait`.

### Properties

- `center -> tuple[int, int]`: absolute screen coordinates of the match center.
- `score -> float`

### Methods (chainable)

- `highlight(duration=None, color=None, thickness=None) -> MatchHandle`
- `click(button="left", highlight=False) -> MatchHandle`
- `double_click(highlight=False) -> MatchHandle`
- `right_click(highlight=False) -> MatchHandle`
- `hover(highlight=True) -> MatchHandle`
- `wait_vanish(timeout, confidence=None, poll=None, strict=True) -> bool`

## RegionScreen

Created by `Screen.region(...)` and automatically scopes operations.

The region rectangle always uses absolute screen coordinates:

- `x`, `y`: top-left corner.
- `w`, `h`: width and height in pixels.

### Methods

- `find(image, confidence=None) -> MatchHandle | None`
- `wait(image, timeout, confidence=None, poll=None) -> MatchHandle`
- `click(image, timeout=10, confidence=None, poll=None, highlight=False) -> MatchHandle`
- `wait_vanish(image, timeout, confidence=None, poll=None, strict=True) -> bool`

## Example

```python
from openvisionauto import Screen

screen = Screen()
menu = screen.region(0, 0, 400, 900)
menu.click("start.png", timeout=8)
```