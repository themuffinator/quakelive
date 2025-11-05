"""Replay trace artefacts back into a VM/DLL implementation."""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, Mapping, Optional, Protocol

from .errors import TraceReplayMismatch


class TraceVMDriver(Protocol):
    """Interface expected by :class:`TraceReplayer` to drive a VM implementation."""

    def apply_syscall(self, event: Mapping[str, Any]) -> None:  # pragma: no cover - protocol
        ...

    def apply_rng_seed(self, event: Mapping[str, Any]) -> None:  # pragma: no cover - protocol
        ...

    def apply_entity_state(self, event: Mapping[str, Any]) -> None:  # pragma: no cover - protocol
        ...


class NoOpVMDriver:
    """Fallback VM driver used when none is provided."""

    def apply_syscall(self, event: Mapping[str, Any]) -> None:  # pragma: no cover - trivial
        return

    def apply_rng_seed(self, event: Mapping[str, Any]) -> None:  # pragma: no cover - trivial
        return

    def apply_entity_state(self, event: Mapping[str, Any]) -> None:  # pragma: no cover - trivial
        return


@dataclass
class TraceReplayResult:
    """Summary of a trace replay pass."""

    manifest_path: Path
    digests: Mapping[str, str]
    counts: Mapping[str, int]


class TraceReplayer:
    """Replays captured traces to assert deterministic behaviour."""

    def __init__(self, trace_dir: Path, vm_driver: Optional[TraceVMDriver] = None) -> None:
        self.trace_dir = trace_dir
        self.vm_driver = vm_driver or NoOpVMDriver()

    def replay(self) -> TraceReplayResult:
        manifest_path = self.trace_dir / "manifest.json"
        if not manifest_path.exists():
            raise FileNotFoundError(f"Missing manifest: {manifest_path}")

        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        expected_digests = manifest.get("digests", {})
        counts: Dict[str, int] = {}

        digests = {
            "syscalls": self._replay_channel("syscalls.jsonl", self.vm_driver.apply_syscall, counts, "syscalls"),
            "rng_seeds": self._replay_channel("rng_seeds.jsonl", self.vm_driver.apply_rng_seed, counts, "rng_seeds"),
            "entities": self._replay_channel("entities.jsonl", self.vm_driver.apply_entity_state, counts, "entities"),
        }

        for key, expected in expected_digests.items():
            actual = digests.get(key)
            if actual is None:
                raise TraceReplayMismatch(f"Digest missing during replay: {key}")
            if expected != actual:
                raise TraceReplayMismatch(
                    f"Digest mismatch for {key}: expected {expected}, observed {actual}"
                )

        return TraceReplayResult(manifest_path=manifest_path, digests=digests, counts=counts)

    def _replay_channel(
        self,
        filename: str,
        consumer,
        counts: Dict[str, int],
        counter_key: str,
    ) -> str:
        path = self.trace_dir / filename
        hasher = hashlib.sha256()
        observed = 0

        if not path.exists():
            counts[counter_key] = 0
            return hasher.hexdigest()

        with path.open("r", encoding="utf-8") as handle:
            for raw_line in handle:
                line = raw_line.rstrip("\n")
                hasher.update((line + "\n").encode("utf-8"))
                payload = json.loads(line)
                consumer(payload)
                observed += 1

        counts[counter_key] = observed
        return hasher.hexdigest()
