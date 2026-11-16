# Highlighter API

## Highlighter

Draw temporary highlight boxes around matches.

### Constructor

```python
from openvisionauto import Highlighter

hl = Highlighter()
```

### Methods

#### show(match, duration=None, color=None, thickness=None) -> None

Draw highlight overlay.

- Raises `OverlayError` on failures.

#### safe_show(match, duration=None, color=None, thickness=None) -> None

Best-effort highlight.

- Suppresses `OverlayError` and logs warnings.

## Example

```python
from openvisionauto import Highlighter
from openvisionauto.models import Match

hl = Highlighter()
hl.safe_show(Match(x=100, y=120, w=80, h=24, score=0.95))
```