# Input API

## Input

Keyboard typing and key operations with optional human-like delays.

### Constructor

```python
from openvisionauto import Input

input_api = Input()
```

```python
Input(timing: TimingProfile | None = None, deterministic: bool | None = None)
```

- `timing`: custom typing/key timing profile.
- `deterministic`: override deterministic mode. When true, pauses use midpoint delays.

### Methods

#### type_text(text, human_like=None, delay_min=None, delay_max=None) -> None

Type text character-by-character (human-like) or in one call.

#### press(key, human_like=None) -> None

Press one key.

#### hotkey(*keys, human_like=None) -> None

Press key combinations (for example `ctrl+s`).

#### clear_text() -> None

Equivalent of `Ctrl+A` then `Backspace`.

## Example

```python
from openvisionauto import Input

inp = Input(deterministic=True)
inp.type_text("hello")
inp.press("enter")
```