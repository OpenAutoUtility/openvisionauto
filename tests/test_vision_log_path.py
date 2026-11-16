from pathlib import Path

from openvisionauto.vision import to_log_path


def test_to_log_path_absolute_path_under_cwd_returns_dot_relative(monkeypatch):
    monkeypatch.setattr("openvisionauto.vision.Path.cwd", lambda: Path("/repo"))

    result = to_log_path(Path("/repo/assets/images/button.png"))

    assert result == "./assets/images/button.png"


def test_to_log_path_outside_cwd_keeps_original_path(monkeypatch):
    monkeypatch.setattr("openvisionauto.vision.Path.cwd", lambda: Path("/repo"))

    result = to_log_path("/opt/data/button.png")

    assert result == "/opt/data/button.png"


def test_to_log_path_accepts_str_and_path(monkeypatch):
    monkeypatch.setattr("openvisionauto.vision.Path.cwd", lambda: Path("/repo"))

    result_from_str = to_log_path("/repo/assets/images/dialog.png")
    result_from_path = to_log_path(Path("/repo/assets/images/dialog.png"))

    assert result_from_str == "./assets/images/dialog.png"
    assert result_from_path == "./assets/images/dialog.png"