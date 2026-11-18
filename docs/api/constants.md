# Constants

## Exported Constants

### DEFAULT_CONFIDENCE

Default match confidence threshold.

Current value: `0.88`

### DEFAULT_POLL_INTERVAL

Default polling interval (seconds) for wait loops.

Current value: `0.5`

## Related Internal Highlight Settings

These values are in configuration but not currently exported from package root:

- `HIGHLIGHT_COLOR` (default `#ff0000`)
- `HIGHLIGHT_THICKNESS` (default `3`)
- `HIGHLIGHT_DURATION_SEC` (default `0.5`)

## Related Internal Timing Default

`DEFAULT_TIMING` is the default `TimingProfile` used by `Input`.

Use custom timing by passing your own profile:

```python
from openvisionauto import Input
from openvisionauto.models import TimingProfile

timing = TimingProfile(
    typing_delay_min=0.02,
    typing_delay_max=0.05,
    special_char_extra_delay=0.01,
    key_press_delay_min=0.01,
    key_press_delay_max=0.03,
    key_post_delay_min=0.02,
    key_post_delay_max=0.05,
    hotkey_gap_min=0.01,
    hotkey_gap_max=0.03,
)

inp = Input(timing=timing)
```