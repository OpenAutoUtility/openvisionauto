# EnvCheck API

## EnvCheck

Validate runtime prerequisites for Linux (X11) and Windows automation.

### Constructor

```python
from openvisionauto import EnvCheck

checker = EnvCheck()
```

### Methods

#### check(strict=True) -> EnvironmentReport

Run compatibility checks:

- platform support (Linux or Windows)
- tkinter availability
- Linux only: DISPLAY availability and X11 session
- Linux only: window activation tools (`xdotool` or `wmctrl`)
- optional tools (`ibus`, `ffmpeg`)

Behavior:

- `strict=True`: raises `EnvironmentNotSupportedError` when unsupported.
- `strict=False`: returns report even when unsupported.

## Functional Helper

```python
from openvisionauto.envcheck import check_env

report = check_env(strict=False)
```

`check_env(strict=True) -> EnvironmentReport` is equivalent to `EnvCheck().check(...)`.

## Example

```python
from openvisionauto import EnvCheck

report = EnvCheck().check(strict=False)
print(report.is_supported, report.messages)
```