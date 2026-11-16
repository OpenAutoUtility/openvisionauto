class OpenVisionAutoError(Exception):
    """Base exception for OpenVisionAuto."""


class TemplateNotFoundError(OpenVisionAutoError):
    """Raised when an image template file path does not exist."""


class WaitTimeoutError(OpenVisionAutoError):
    """Raised when waiting for a match times out."""


class VanishTimeoutError(OpenVisionAutoError):
    """Raised when waiting for an image to vanish times out."""


class EnvironmentNotSupportedError(OpenVisionAutoError):
    """Raised when runtime prerequisites are not met."""


class OverlayError(OpenVisionAutoError):
    """Raised when highlight overlay cannot be rendered."""


class RecorderError(OpenVisionAutoError):
    """Raised when recording actions fail."""
