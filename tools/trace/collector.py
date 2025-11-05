"""Helpers for parsing streamed trace events."""

from __future__ import annotations

import hashlib
import json
import logging
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, Iterable, Mapping, MutableMapping, TextIO

from .errors import TraceCaptureError

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class EventChannel:
    """Description of a supported trace channel."""

    name: str
    filename: str
    digest_key: str


SUPPORTED_CHANNELS: Mapping[str, EventChannel] = {
    channel.name: channel
    for channel in (
        EventChannel("SYS", "syscalls.jsonl", "syscalls"),
        EventChannel("RNG", "rng_seeds.jsonl", "rng_seeds"),
        EventChannel("ENT", "entities.jsonl", "entities"),
    )
}


@dataclass
class TraceCollector:
    """Collects trace events from a streaming source.

    The collector is responsible for splitting the raw trace stream into per-channel
    JSONL artefacts, while also computing a deterministic digest for each channel so
    that replays can confirm determinism.
    """

    output_dir: Path
    event_channels: Mapping[str, EventChannel] = field(
        default_factory=lambda: SUPPORTED_CHANNELS
    )
    metadata: MutableMapping[str, object] = field(default_factory=dict)

    def __post_init__(self) -> None:
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self._files: Dict[str, TextIO] = {}
        self._hashers: Dict[str, Any] = {}
        self._counts: Dict[str, int] = {}

        for channel_key, channel in self.event_channels.items():
            path = self.output_dir / channel.filename
            file_handle = path.open("w", encoding="utf-8")
            self._files[channel_key] = file_handle
            self._hashers[channel_key] = hashlib.sha256()
            self._counts[channel_key] = 0

        self._unknown_lines: list[str] = []

    @property
    def counts(self) -> Mapping[str, int]:
        """Return the number of events observed per channel."""

        return dict(self._counts)

    @property
    def unknown_lines(self) -> Iterable[str]:
        """Return lines that could not be parsed into known trace channels."""

        return tuple(self._unknown_lines)

    def handle_line(self, line: str) -> None:
        """Parse and persist a trace line.

        Lines that do not conform to the ``TRACE:<CHANNEL>:<JSON>`` structure are
        recorded so they can be surfaced to the caller for debugging.
        """

        stripped = line.strip()
        if not stripped:
            return

        if not stripped.startswith("TRACE:"):
            self._unknown_lines.append(stripped)
            return

        try:
            channel_key, payload = stripped[6:].split(":", 1)
        except ValueError as exc:  # pragma: no cover - defensive branch
            raise TraceCaptureError(f"Malformed trace line: {stripped!r}") from exc

        channel_key = channel_key.upper()
        if channel_key == "META":
            self._consume_metadata(payload)
            return

        channel = self.event_channels.get(channel_key)
        if channel is None:
            logger.debug("Ignoring unsupported trace channel: %s", channel_key)
            self._unknown_lines.append(stripped)
            return

        try:
            data = json.loads(payload)
        except json.JSONDecodeError as exc:  # pragma: no cover - defensive branch
            raise TraceCaptureError(
                f"Failed to decode {channel_key} payload: {payload!r}"
            ) from exc

        serialized = json.dumps(data, sort_keys=True, separators=(",", ":"))
        file_handle = self._files[channel_key]
        assert file_handle is not None
        file_handle.write(serialized)
        file_handle.write("\n")
        file_handle.flush()

        hasher = self._hashers[channel_key]
        hasher.update((serialized + "\n").encode("utf-8"))

        self._counts[channel_key] += 1

    def _consume_metadata(self, payload: str) -> None:
        try:
            data = json.loads(payload)
        except json.JSONDecodeError as exc:  # pragma: no cover - defensive branch
            raise TraceCaptureError(f"Invalid META payload: {payload!r}") from exc

        logger.debug("Updating trace metadata with keys: %%s", sorted(data))
        self.metadata.update(data)

    def finalize(self) -> Dict[str, str]:
        """Close resources and return a mapping of digest names to hexdigests."""

        digests: Dict[str, str] = {}
        for channel_key, channel in self.event_channels.items():
            file_handle = self._files.pop(channel_key)
            if file_handle is not None:
                file_handle.close()
            digest = self._hashers[channel_key].hexdigest()
            digests[channel.digest_key] = digest
        return digests
