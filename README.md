# OpenVisionAuto

[![PyPI version](https://img.shields.io/pypi/v/openvisionauto.svg)](https://pypi.org/project/openvisionauto/)
![Python](https://img.shields.io/pypi/pyversions/openvisionauto)
![Platform](https://img.shields.io/badge/platform-Linux%20%7C%20Windows-blue)

Desktop automation toolkit built around visual image matching: locate a template on screen, then click, type, wait, or record. Runs on Linux (X11) and Windows with a real display.

## Install

```bash
pip install openvisionauto
```

## Requirements

- Python ≥ 3.10
- tkinter — highlight overlay (`python3-tk` on Linux)
- `xdotool` or `wmctrl` — window activation on Linux
- `ffmpeg` — screen recording (`x11grab` on Linux, `gdigrab` on Windows)

`Screen().check_env(strict=True)` verifies the runtime in one call.

## API

| API | Purpose |
|---|---|
| `Screen.find / wait / wait_vanish` | match once, or poll until the image appears / disappears |
| `Screen.click / click_and_wait_vanish` | wait for an image, click its center, optionally wait for it to vanish |
| `Screen.region(x, y, w, h)` | scope any operation to a sub-area |
| `Screen.activate_window(title)` | bring a window to the foreground |
| `MatchHandle` | `.highlight() .click() .double_click() .right_click() .hover() .wait_vanish()`, plus `.center` / `.score` |
| `Input` | `type_text() press() hotkey() click() move_to() clear_text()` |
| `Recorder` | `start(file, fps=15)` / `stop()`, backed by ffmpeg |

## Example

```python
from openvisionauto import Recorder, Screen

screen = Screen()
screen.check_env(strict=True)

recorder = Recorder()
recorder.start("demo.mp4")
try:
    screen.activate_window("Calculator")  # Linux/X11: activate before typing
    screen.wait("button_1.png", timeout=10).click()
    screen.input.type_text("5")
    screen.wait("button_equals.png", timeout=5).click().highlight()
    screen.region(0, 0, 800, 600).wait("result.png", timeout=3)
finally:
    recorder.stop()
```
