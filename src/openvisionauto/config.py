from .models import TimingProfile

DEFAULT_CONFIDENCE = 0.88
DEFAULT_POLL_INTERVAL = 0.5

HIGHLIGHT_ENABLED = True
HIGHLIGHT_COLOR = "#ff0000"
HIGHLIGHT_THICKNESS = 3
HIGHLIGHT_DURATION_SEC = 0.5

DEFAULT_TIMING = TimingProfile(
    typing_delay_min=0.04,
    typing_delay_max=0.12,
    special_char_extra_delay=0.03,
    key_press_delay_min=0.01,
    key_press_delay_max=0.04,
    key_post_delay_min=0.03,
    key_post_delay_max=0.08,
    hotkey_gap_min=0.02,
    hotkey_gap_max=0.06,
    human_like_default=True,
    deterministic_mode=False,
)
