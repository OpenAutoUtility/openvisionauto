import math

from openvisionauto.input import Input


class _FakePyAutoGui:
    def __init__(self):
        self.calls = []

    def write(self, text):
        self.calls.append(("write", text))

    def press(self, key):
        self.calls.append(("press", key))

    def hotkey(self, *keys):
        self.calls.append(("hotkey", keys))

    def keyDown(self, key):
        self.calls.append(("down", key))

    def keyUp(self, key):
        self.calls.append(("up", key))


def _approx_equal(actual, expected):
    return math.isclose(actual, expected, rel_tol=1e-6, abs_tol=1e-6)


def test_type_text_deterministic_sleep_pattern(monkeypatch):
    input_api = Input(deterministic=True)
    fake_gui = _FakePyAutoGui()
    sleeps = []

    monkeypatch.setattr(input_api, "_get_pyautogui", lambda: fake_gui)
    monkeypatch.setattr("openvisionauto.input.time.sleep", lambda sec: sleeps.append(sec))

    input_api.type_text("a/b")

    assert fake_gui.calls == [("write", "a"), ("write", "/"), ("write", "b")]
    assert len(sleeps) == 4
    assert _approx_equal(sleeps[0], 0.08)
    assert _approx_equal(sleeps[1], 0.08)
    assert _approx_equal(sleeps[2], 0.03)
    assert _approx_equal(sleeps[3], 0.08)


def test_press_deterministic(monkeypatch):
    input_api = Input(deterministic=True)
    fake_gui = _FakePyAutoGui()
    sleeps = []

    monkeypatch.setattr(input_api, "_get_pyautogui", lambda: fake_gui)
    monkeypatch.setattr("openvisionauto.input.time.sleep", lambda sec: sleeps.append(sec))

    input_api.press("enter")

    assert fake_gui.calls == [("press", "enter")]
    assert len(sleeps) == 2
    assert _approx_equal(sleeps[0], 0.025)
    assert _approx_equal(sleeps[1], 0.055)
