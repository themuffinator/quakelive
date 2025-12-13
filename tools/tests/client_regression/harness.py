"""Snapshot replay harness used for client regression testing.

The harness focuses on deterministic playback of previously captured snapshots
and produces stable hashes representing the Heads-Up Display (HUD) state. The
hashes are later compared against known-good baselines to detect rendering or
prediction regressions.
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, Iterable, Iterator, List, Mapping, MutableMapping, Sequence


def _canonicalise(value: Any) -> Any:
    """Recursively convert sequences and mappings into hashable primitives."""

    if isinstance(value, dict):
        return {str(key): _canonicalise(sub) for key, sub in sorted(value.items(), key=lambda item: str(item[0]))}
    if isinstance(value, (list, tuple)):
        return [_canonicalise(item) for item in value]
    if isinstance(value, float):
        return round(value, 6)
    return value


@dataclass(frozen=True)
class Snapshot:
    """Represents a single captured client snapshot."""

    sequence: int
    server_time: int
    player_state: Mapping[str, Any]
    match_state: Mapping[str, Any]
    commands: Sequence[Mapping[str, Any]]
    user_cmd: Mapping[str, Any] | None = None

    @classmethod
    def from_payload(cls, payload: Mapping[str, Any]) -> "Snapshot":
        try:
            sequence = int(payload["sequence"])
            server_time = int(payload["serverTime"])
        except KeyError as exc:  # pragma: no cover - defensive programming
            raise ValueError("Snapshot payload missing required key") from exc

        player_state = payload.get("playerState", {})
        match_state = payload.get("matchState", {})
        commands = payload.get("commands", [])
        user_cmd = payload.get("userCmd") or payload.get("usercmd")
        if not isinstance(player_state, Mapping):
            raise TypeError("playerState must be a mapping")
        if not isinstance(match_state, Mapping):
            raise TypeError("matchState must be a mapping")
        if not isinstance(commands, Sequence):
            raise TypeError("commands must be a sequence")
        if user_cmd is not None and not isinstance(user_cmd, Mapping):
            raise TypeError("userCmd must be a mapping when provided")

        return cls(
            sequence=sequence,
            server_time=server_time,
            player_state=dict(player_state),
            match_state=dict(match_state),
            commands=[dict(command) for command in commands],
            user_cmd=dict(user_cmd) if user_cmd is not None else None,
        )


@dataclass(frozen=True)
class HUDState:
    """Minimal HUD description derived from the predicted state."""

    health: int
    armor: int
    weapon: str
    ammo: Mapping[str, int]
    position: Sequence[float]
    match_state: Mapping[str, Any] | None = None

    def to_dict(self) -> Dict[str, Any]:
        payload: Dict[str, Any] = {
            "health": int(self.health),
            "armor": int(self.armor),
            "weapon": str(self.weapon),
            "ammo": {weapon: int(amount) for weapon, amount in sorted(self.ammo.items())},
            "position": [round(float(coord), 6) for coord in self.position],
        }

        if self.match_state:
            payload["matchState"] = {
                str(key): _canonicalise(value) for key, value in sorted(self.match_state.items())
            }

        return payload


@dataclass(frozen=True)
class PlaybackFrame:
    """Result of replaying a single snapshot."""

    sequence: int
    server_time: int
    hud: HUDState
    hud_hash: str
    usercmd: Mapping[str, Any]
    usercmd_hash: str | None


class HUDHasher:
    """Utility responsible for producing deterministic hashes from HUD payloads."""

    def __init__(self, *, digest: str = "sha256") -> None:
        self.digest = digest

    def hash(self, hud_state: Mapping[str, Any]) -> str:
        canonical = _canonicalise(hud_state)
        payload = json.dumps(canonical, sort_keys=True, separators=(",", ":")).encode("utf-8")
        return hashlib.new(self.digest, payload).hexdigest()


class ClientRegressionHarness:
    """High level orchestrator for snapshot playback and HUD hashing."""

    def __init__(self, predictor: "ClientPredictor", *, hasher: HUDHasher | None = None) -> None:
        self.predictor = predictor
        self.hasher = hasher or HUDHasher()

    def frame_to_payload(self, frame: PlaybackFrame) -> Dict[str, Any]:
        """Convert a :class:`PlaybackFrame` into a serialisable payload."""

        payload: Dict[str, Any] = {
            "sequence": frame.sequence,
            "serverTime": frame.server_time,
            "hash": frame.hud_hash,
            "hud": frame.hud.to_dict(),
        }

        if frame.usercmd:
            payload["usercmd"] = frame.usercmd
            if frame.usercmd_hash:
                payload["usercmdHash"] = frame.usercmd_hash

        return payload

    @staticmethod
    def load_snapshots(path: Path) -> List[Snapshot]:
        """Load snapshots from *path*.

        The file is expected to contain JSON with a top-level ``snapshots`` list.
        Each entry is converted into :class:`Snapshot` instances.
        """

        payload = json.loads(Path(path).read_text(encoding="utf-8"))
        try:
            raw_snapshots = payload["snapshots"]
        except KeyError as exc:
            raise ValueError("Snapshot archive missing 'snapshots' key") from exc

        if not isinstance(raw_snapshots, Sequence):
            raise TypeError("'snapshots' must be a sequence")

        snapshots = [Snapshot.from_payload(item) for item in raw_snapshots]
        snapshots.sort(key=lambda snap: (snap.server_time, snap.sequence))
        return snapshots

    @staticmethod
    def load_netdump(path: Path) -> tuple[List[Snapshot], Mapping[str, Any]]:
        """Load retail snapshot frames and associated metadata from *path*."""

        payload = json.loads(Path(path).read_text(encoding="utf-8"))
        metadata = payload.get("metadata", {})
        frames = payload.get("frames") or payload.get("snapshots")
        if frames is None:
            raise ValueError("Netdump archives must define a 'frames' collection")
        if not isinstance(frames, Sequence):
            raise TypeError("'frames' must be a sequence of snapshot payloads")

        snapshots = [Snapshot.from_payload(frame) for frame in frames]
        snapshots.sort(key=lambda snap: (snap.server_time, snap.sequence))

        if not isinstance(metadata, Mapping):  # pragma: no cover - defensive guard
            raise TypeError("'metadata' must be a mapping when provided")

        return snapshots, metadata

    def replay(self, snapshots: Iterable[Snapshot]) -> Iterator[PlaybackFrame]:
        """Replay *snapshots* through the predictor, yielding playback frames."""

        self.predictor.reset()
        for snapshot in snapshots:
            prediction = self.predictor.predict(snapshot)
            hud_payload = prediction.hud.to_dict()
            hud_hash = self.hasher.hash(hud_payload)
            usercmd_payload = prediction.user_cmd
            usercmd_hash = self.hasher.hash(usercmd_payload) if usercmd_payload else None
            yield PlaybackFrame(
                sequence=snapshot.sequence,
                server_time=snapshot.server_time,
                hud=prediction.hud,
                hud_hash=hud_hash,
                usercmd=usercmd_payload,
                usercmd_hash=usercmd_hash,
            )

    def replay_to_payloads(self, snapshots: Iterable[Snapshot]) -> List[Dict[str, Any]]:
        """Replay *snapshots* and return a list of canonical payload dictionaries."""

        return [self.frame_to_payload(frame) for frame in self.replay(snapshots)]


# Import at the end to avoid circular dependencies at type-check time.
from .predict import ClientPredictor  # noqa: E402  # pylint: disable=wrong-import-position

