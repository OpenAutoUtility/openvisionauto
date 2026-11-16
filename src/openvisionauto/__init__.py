import logging

from .config import DEFAULT_CONFIDENCE, DEFAULT_POLL_INTERVAL
from .envcheck import EnvCheck
from .errors import (
    EnvironmentNotSupportedError,
    OverlayError,
    OpenVisionAutoError,
    RecorderError,
    TemplateNotFoundError,
    VanishTimeoutError,
    WaitTimeoutError,
)
from .highlighter import Highlighter
from .input import Input
from .models import EnvironmentReport, Match, TimingProfile
from .recorder import Recorder
from .screen import Screen


def set_log_level(level: int | str) -> None:
    """Set log level for ``openvisionauto`` logs and active handlers.

    Accepts either logging level integers or standard level names,
    such as ``"DEBUG"``, ``"INFO"`` and ``"WARNING"``.
    """
    if isinstance(level, str):
        normalized = level.upper()
        if normalized not in logging._nameToLevel:
            raise ValueError(f"Unknown log level: {level}")
        resolved_level = int(logging._nameToLevel[normalized])
    else:
        resolved_level = int(level)

    logger = logging.getLogger("openvisionauto")
    logger.setLevel(resolved_level)

    # Ensure existing handlers in the propagation chain won't filter records.
    current = logger
    while current is not None:
        for handler in current.handlers:
            handler.setLevel(resolved_level)
        if not current.propagate:
            break
        current = current.parent

__all__ = [
    "DEFAULT_CONFIDENCE",
    "DEFAULT_POLL_INTERVAL",
    "EnvCheck",
    "EnvironmentNotSupportedError",
    "EnvironmentReport",
    "Highlighter",
    "Input",
    "Match",
    "OverlayError",
    "OpenVisionAutoError",
    "Recorder",
    "RecorderError",
    "Screen",
    "set_log_level",
    "TemplateNotFoundError",
    "TimingProfile",
    "VanishTimeoutError",
    "WaitTimeoutError",
]
