# Vision API

## Vision

Low-level image matching and polling utilities.

This class is mainly used internally by `Screen`, but can be used directly when needed.

### Constructor

```python
from openvisionauto.vision import Vision

vision = Vision()
```

### Methods

#### find(image, confidence=None, region=None) -> Match | None

Run one template match.

- Uses `cv2.matchTemplate(..., cv2.TM_CCOEFF_NORMED)`.
- Returns `None` if score is below threshold.
- `region` accepts `Region | tuple[int, int, int, int] | None`.

#### wait(image, timeout, confidence=None, poll=None, region=None) -> Match

Poll until matched.

- Raises `WaitTimeoutError` on timeout.
- `region` accepts `Region | tuple[int, int, int, int] | None`.

#### wait_vanish(image, timeout, confidence=None, poll=None, region=None, strict=True) -> bool

Poll until image disappears.

- Returns `True` if vanished in time.
- Raises `VanishTimeoutError` when `strict=True` and timeout occurs.
- Returns `False` when `strict=False` and timeout occurs.
- `region` accepts `Region | tuple[int, int, int, int] | None`.

## Notes

- `image` accepts `str | pathlib.Path`.
- `region` accepts `Region | tuple[int, int, int, int] | None`.
- For region tuples, values mean `(x, y, w, h)`:
    absolute top-left X, absolute top-left Y, width, and height in pixels.
- Coordinates in returned `Match` are absolute screen coordinates.
- Returned `Match(x, y, w, h, score)` uses `x` and `y` as the matched top-left corner.

## Example

```python
from openvisionauto.vision import Vision

vision = Vision()
match = vision.find("login_button.png", confidence=0.9)
if match:
    print(match.center, match.score)
```