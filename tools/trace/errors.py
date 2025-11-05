"""Custom exceptions for trace tooling."""

class TraceCaptureError(RuntimeError):
    """Raised when trace capture encounters a fatal error."""


class TraceReplayMismatch(RuntimeError):
    """Raised when replay verification diverges from the recorded trace."""
