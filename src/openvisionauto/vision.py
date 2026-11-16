from __future__ import annotations

import os
import time
from pathlib import Path
import logging

import cv2
import mss
import numpy as np

from .config import DEFAULT_CONFIDENCE, DEFAULT_POLL_INTERVAL
from .errors import TemplateNotFoundError, VanishTimeoutError, WaitTimeoutError
from .highlighter import Highlighter
from .models import Match, Region


LOGGER = logging.getLogger(__name__)


def to_log_path(path_like: str | Path) -> str:
    """Format image path for logs without changing matching behavior.

    If a path is within the current working directory, return it as
    ``./relative/path``. Otherwise return the original representation.
    """
    original = str(path_like)
    try:
        path = Path(path_like).resolve(strict=False)
        cwd = Path.cwd().resolve(strict=False)
        rel_path = path.relative_to(cwd)
    except (OSError, RuntimeError, ValueError):
        return original

    rel_str = str(rel_path)
    if rel_str == ".":
        return "."
    return f".{os.sep}{rel_str}"


def _as_region(region: Region | tuple[int, int, int, int] | None) -> Region | None:
    """Normalize region input into a ``Region`` instance.

    Accepts either an existing ``Region`` object or a tuple ``(x, y, w, h)``.
    """
    if region is None:
        return None
    if isinstance(region, Region):
        return region
    x, y, w, h = region
    return Region(int(x), int(y), int(w), int(h))


class Vision:
    """Low-level OpenCV template matching and polling engine."""

    def __init__(self) -> None:
        """Initialize screen capture backend."""
        self._mss = mss.mss()
        self._highlighter = Highlighter()

    def _load_template(self, image: str | Path) -> np.ndarray:
        """Load a template image from disk.

        Args:
            image: Template image path.

        Returns:
            BGR image array.

        Raises:
            TemplateNotFoundError: If the file does not exist or cannot be decoded.
        """
        image_path = Path(image)
        if not image_path.exists():
            raise TemplateNotFoundError(f"Template not found: {image_path}")
        template = cv2.imread(str(image_path), cv2.IMREAD_COLOR)
        if template is None:
            raise TemplateNotFoundError(f"Unable to load template: {image_path}")
        return template

    def _capture_screen(self, region: Region | None = None) -> np.ndarray:
        """Capture the full screen or a specific region.

        Args:
            region: Optional capture region. ``None`` captures primary monitor.

        Returns:
            Captured BGR frame as a numpy array.
        """
        if region is None:
            monitor = self._mss.monitors[1]
            frame = self._mss.grab(monitor)
            return np.array(frame)[:, :, :3]

        monitor = {
            "left": region.x,
            "top": region.y,
            "width": region.w,
            "height": region.h,
        }
        frame = self._mss.grab(monitor)
        return np.array(frame)[:, :, :3]

    def find(
        self,
        image: str | Path,
        confidence: float | None = None,
        region: Region | tuple[int, int, int, int] | None = None,
    ) -> Match | None:
        """Run one template match operation.

        Args:
            image: Template image path.
            confidence: Match threshold in [0.0, 1.0]. ``None`` uses configured default.
            region: Search region as ``Region`` or ``(x, y, w, h)`` tuple.

        Returns:
            ``Match`` on success, otherwise ``None``.
        """
        resolved_region = _as_region(region)
        threshold = confidence if confidence is not None else DEFAULT_CONFIDENCE
        template = self._load_template(image)
        screen = self._capture_screen(resolved_region)

        result = cv2.matchTemplate(screen, template, cv2.TM_CCOEFF_NORMED)
        _, max_val, _, max_loc = cv2.minMaxLoc(result)

        if max_val < threshold:
            return None

        h, w = template.shape[:2]
        abs_x = max_loc[0] + (resolved_region.x if resolved_region else 0)
        abs_y = max_loc[1] + (resolved_region.y if resolved_region else 0)
        return Match(x=abs_x, y=abs_y, w=w, h=h, score=float(max_val))

    def wait(
        self,
        image: str | Path,
        timeout: float,
        confidence: float | None = None,
        poll: float | None = None,
        region: Region | tuple[int, int, int, int] | None = None,
    ) -> Match:
        """Poll until an image appears or timeout occurs.

        Args:
            image: Template image path.
            timeout: Max wait duration in seconds.
            confidence: Match threshold in [0.0, 1.0]. ``None`` uses configured default.
            poll: Poll interval in seconds. ``None`` uses configured default.
            region: Search region as ``Region`` or ``(x, y, w, h)`` tuple.

        Returns:
            The first successful ``Match``.

        Raises:
            WaitTimeoutError: If timeout elapses before any match reaches threshold.
        """
        interval = poll if poll is not None else DEFAULT_POLL_INTERVAL
        deadline = time.time() + timeout
        last_score = 0.0
        resolved_region = _as_region(region)
        threshold = confidence if confidence is not None else DEFAULT_CONFIDENCE
        template = self._load_template(image)
        h, w = template.shape[:2]

        while time.time() < deadline:
            screen = self._capture_screen(resolved_region)
            result = cv2.matchTemplate(screen, template, cv2.TM_CCOEFF_NORMED)
            _, max_val, _, max_loc = cv2.minMaxLoc(result)
            score = float(max_val)
            last_score = max(last_score, score)
            if score >= threshold:
                abs_x = max_loc[0] + (resolved_region.x if resolved_region else 0)
                abs_y = max_loc[1] + (resolved_region.y if resolved_region else 0)
                LOGGER.debug(
                    "wait matched image=%s score=%.4f threshold=%.4f",
                    to_log_path(image),
                    score,
                    threshold,
                )
                return Match(x=abs_x, y=abs_y, w=w, h=h, score=score)
            time.sleep(interval)

        LOGGER.debug(
            "wait timeout image=%s timeout=%ss threshold=%.4f best_score=%.4f gap=%.4f",
            to_log_path(image),
            timeout,
            threshold,
            last_score,
            threshold - last_score,
        )
        raise WaitTimeoutError(
            f"wait timeout image={image} timeout={timeout}s confidence={threshold} last_score={last_score:.4f}"
        )

    def wait_vanish(
        self,
        image: str | Path,
        timeout: float,
        confidence: float | None = None,
        poll: float | None = None,
        region: Region | tuple[int, int, int, int] | None = None,
        strict: bool = True,
    ) -> bool:
        """Poll until an image can no longer be matched.

        Args:
            image: Template image path.
            timeout: Max wait duration in seconds.
            confidence: Match threshold in [0.0, 1.0]. ``None`` uses configured default.
            poll: Poll interval in seconds. ``None`` uses configured default.
            region: Search region as ``Region`` or ``(x, y, w, h)`` tuple.
            strict: If ``True``, raise on timeout. If ``False``, return ``False``.

        Returns:
            ``True`` if image vanishes before timeout; otherwise ``False`` when ``strict=False``.

        Raises:
            VanishTimeoutError: If timeout occurs while ``strict=True``.
        """
        interval = poll if poll is not None else DEFAULT_POLL_INTERVAL
        threshold = confidence if confidence is not None else DEFAULT_CONFIDENCE
        deadline = time.time() + timeout

        while time.time() < deadline:
            loop_started = time.time()
            match = self.find(image=image, confidence=threshold, region=region)
            if match is None:
                return True

            LOGGER.debug(
                "wait_vanish still matched image=%s score=%.4f threshold=%.4f",
                to_log_path(image),
                match.score,
                threshold,
            )

            # Target is still visible: draw a yellow border (transparent center),
            # then wait the normal poll interval before the next retry.
            highlight_duration = max(0.05, min(interval, 0.3))
            self._highlighter.safe_show(match, duration=highlight_duration, color="#ffff00")

            elapsed = time.time() - loop_started
            remaining = interval - elapsed
            if remaining > 0:
                time.sleep(remaining)

        if strict:
            raise VanishTimeoutError(
                f"wait_vanish timeout image={image} timeout={timeout}s confidence={threshold}"
            )
        return False
