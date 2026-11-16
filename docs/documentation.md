# OpenVisionAuto Documentation

This documentation covers all currently exported public APIs of `openvisionauto`.

## Start Here

- [API Overview](api/index.md)
- [Screen API](api/screen.md)
- [Input API](api/input.md)
- [Vision API](api/vision.md)
- [Recorder API](api/recorder.md)
- [Highlighter API](api/highlighter.md)
- [EnvCheck API](api/envcheck.md)
- [Models and Errors](api/models-and-errors.md)
- [Constants](api/constants.md)

## Scope

- Linux (X11 session) and Windows
- Real display required

## Install

```bash
pip install openvisionauto
```

## Quick Example

```python
from openvisionauto import Screen

screen = Screen()
screen.wait("login_button.png", timeout=10).highlight().click()
```