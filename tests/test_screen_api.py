from openvisionauto.models import Match
from openvisionauto.screen import Screen


class _FakeVision:
    def __init__(self):
        self.wait_vanish_calls = []

    def find(self, image, confidence=None, region=None):
        return Match(x=10, y=20, w=30, h=40, score=0.95)

    def wait(self, image, timeout, confidence=None, poll=None, region=None):
        return Match(x=10, y=20, w=30, h=40, score=0.95)

    def wait_vanish(self, image, timeout, confidence=None, poll=None, region=None, strict=True):
        self.wait_vanish_calls.append(
            {
                "image": image,
                "timeout": timeout,
                "confidence": confidence,
                "poll": poll,
                "region": region,
                "strict": strict,
            }
        )
        return True


class _FakeHighlighter:
    def __init__(self):
        self.calls = []

    def safe_show(self, match, duration=None, color=None, thickness=None, show_center=False):
        self.calls.append(
            {
                "match": match,
                "duration": duration,
                "color": color,
                "thickness": thickness,
                "show_center": show_center,
            }
        )


class _FakePyAutoGui:
    def __init__(self):
        self.calls = []

    def click(self, x=None, y=None, button="left"):
        self.calls.append(("click", x, y, button))

    def doubleClick(self, x=None, y=None):
        self.calls.append(("double", x, y))

    def mouseDown(self, x=None, y=None, button="left"):
        self.calls.append(("down", x, y, button))

    def mouseUp(self, x=None, y=None, button="left"):
        self.calls.append(("up", x, y, button))

    def moveTo(self, x, y):
        self.calls.append(("move", x, y))


def _new_screen():
    screen = Screen.__new__(Screen)
    screen.vision = _FakeVision()
    screen.highlighter = _FakeHighlighter()
    screen.input = None
    return screen


def test_wait_does_not_highlight_implicitly(monkeypatch):
    screen = _new_screen()
    fake_gui = _FakePyAutoGui()
    monkeypatch.setattr("openvisionauto.screen._get_pyautogui", lambda: fake_gui)

    screen.wait("button.png", timeout=3)

    assert screen.highlighter.calls == []


def test_click_without_highlight_flag_does_not_highlight(monkeypatch):
    screen = _new_screen()
    fake_gui = _FakePyAutoGui()
    monkeypatch.setattr("openvisionauto.screen._get_pyautogui", lambda: fake_gui)

    screen.click("button.png", timeout=3)

    assert screen.highlighter.calls == []
    assert fake_gui.calls == [("click", 25, 40, "left")]


def test_click_with_highlight_flag_highlights_once(monkeypatch):
    screen = _new_screen()
    fake_gui = _FakePyAutoGui()
    monkeypatch.setattr("openvisionauto.screen._get_pyautogui", lambda: fake_gui)

    screen.click("button.png", timeout=3, highlight=True)

    assert len(screen.highlighter.calls) == 1
    assert fake_gui.calls == [("click", 25, 40, "left")]


def test_handle_click_highlight_flag_highlights_once(monkeypatch):
    screen = _new_screen()
    fake_gui = _FakePyAutoGui()
    monkeypatch.setattr("openvisionauto.screen._get_pyautogui", lambda: fake_gui)

    handle = screen.wait("button.png", timeout=3)
    handle.click(highlight=True)

    assert len(screen.highlighter.calls) == 1
    assert fake_gui.calls == [("click", 25, 40, "left")]


def test_handle_highlight_can_request_center_marker():
    screen = _new_screen()

    handle = screen.wait("button.png", timeout=3)
    handle.highlight(show_center=True)

    assert screen.highlighter.calls[-1]["show_center"] is True


def test_handle_highlight_accepts_show_center_alias():
    screen = _new_screen()

    handle = screen.wait("button.png", timeout=3)
    handle.highlight(showCenter=True)

    assert screen.highlighter.calls[-1]["show_center"] is True


def test_handle_click_hold_seconds_uses_mouse_down_up(monkeypatch):
    screen = _new_screen()
    fake_gui = _FakePyAutoGui()
    sleeps = []
    monkeypatch.setattr("openvisionauto.screen._get_pyautogui", lambda: fake_gui)
    monkeypatch.setattr("openvisionauto.screen.time.sleep", lambda sec: sleeps.append(sec))

    handle = screen.wait("button.png", timeout=3)
    handle.click(button="right", hold_seconds=0.25)

    assert fake_gui.calls == [("down", 25, 40, "right"), ("up", 25, 40, "right")]
    assert sleeps == [0.25]


def test_screen_click_hold_seconds_pass_through(monkeypatch):
    screen = _new_screen()
    fake_gui = _FakePyAutoGui()
    sleeps = []
    monkeypatch.setattr("openvisionauto.screen._get_pyautogui", lambda: fake_gui)
    monkeypatch.setattr("openvisionauto.screen.time.sleep", lambda sec: sleeps.append(sec))

    screen.click("button.png", timeout=3, hold_seconds=0.1)

    assert fake_gui.calls == [("down", 25, 40, "left"), ("up", 25, 40, "left")]
    assert sleeps == [0.1]


def test_handle_right_click_hold_seconds_uses_mouse_down_up(monkeypatch):
    screen = _new_screen()
    fake_gui = _FakePyAutoGui()
    sleeps = []
    monkeypatch.setattr("openvisionauto.screen._get_pyautogui", lambda: fake_gui)
    monkeypatch.setattr("openvisionauto.screen.time.sleep", lambda sec: sleeps.append(sec))

    handle = screen.wait("button.png", timeout=3)
    handle.right_click(hold_seconds=0.2)

    assert fake_gui.calls == [("down", 25, 40, "right"), ("up", 25, 40, "right")]
    assert sleeps == [0.2]


def test_wait_vanish_defaults_to_strict_true():
    screen = _new_screen()

    screen.wait_vanish("dialog.png", timeout=5)

    assert screen.vision.wait_vanish_calls[-1]["strict"] is True


def test_handle_wait_vanish_keeps_region_tuple_as_region_object():
    screen = _new_screen()

    handle = screen.wait("dialog.png", timeout=5, region=(1, 2, 3, 4))
    handle.wait_vanish(timeout=2)

    region = screen.vision.wait_vanish_calls[-1]["region"]
    assert (region.x, region.y, region.w, region.h) == (1, 2, 3, 4)
