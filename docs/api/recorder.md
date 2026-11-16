# Recorder API

## Recorder

Screen recording helper using `ffmpeg` with platform-specific capture backends.

### Constructor

```python
from openvisionauto import Recorder

rec = Recorder(display=":0")
```

```python
Recorder(display: str | None = None)
```

- `display`: X11 display string. Defaults to environment `DISPLAY` or `:0`.
	This value is used on Linux. On Windows, desktop capture uses `gdigrab`.

### Methods

#### start(output_file, fps=15) -> None

Start recording.

- Requires `ffmpeg` in system PATH.
- Raises `RecorderError` if ffmpeg is missing.
- Raises `RecorderError` if recorder is already running.

#### stop() -> None

Stop recording if active. Safe to call repeatedly.

## Example

```python
from openvisionauto import Recorder

rec = Recorder()
rec.start("run.mp4", fps=20)
# do automation...
rec.stop()
```