"""Deterministic client prediction helpers for the regression harness."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Mapping, MutableMapping, Sequence

from .harness import HUDState, Snapshot


@dataclass(frozen=True)
class PredictionResult:
    """Aggregate predicted HUD state and generated user command."""

    hud: HUDState
    user_cmd: Mapping[str, Any]


@dataclass
class _PlayerState:
    """Mutable representation of the simulated player state."""

    origin: MutableMapping[str, float]
    health: int
    armor: int
    weapon: str
    ammo: MutableMapping[str, int] = field(default_factory=dict)

    @classmethod
    def from_snapshot(cls, snapshot: Snapshot) -> "_PlayerState":
        ps = snapshot.player_state
        origin = _vector_to_mapping(ps.get("origin", [0.0, 0.0, 0.0]))
        ammo = {
            str(weapon): int(amount)
            for weapon, amount in ps.get("ammo", {}).items()
        }
        return cls(
            origin=origin,
            health=int(ps.get("health", 100)),
            armor=int(ps.get("armor", 0)),
            weapon=str(ps.get("weapon", "unknown")),
            ammo=ammo,
        )

    def clone(self) -> "_PlayerState":
        return _PlayerState(
            origin=dict(self.origin),
            health=int(self.health),
            armor=int(self.armor),
            weapon=str(self.weapon),
            ammo=dict(self.ammo),
        )


def _vector_to_mapping(vector: Sequence[float]) -> MutableMapping[str, float]:
    if len(vector) != 3:
        raise ValueError("Position vectors must contain exactly 3 components")
    return {axis: float(component) for axis, component in zip(("x", "y", "z"), vector)}


class ClientPredictor:
    """Lightweight state machine approximating the cgame prediction pipeline."""

    def __init__(self) -> None:
        self._state: _PlayerState | None = None
        self._last_server_time: int | None = None
        self._match_state: Mapping[str, Any] | None = None

    def reset(self) -> None:
        self._state = None
        self._last_server_time = None
        self._match_state = None

    def predict(self, snapshot: Snapshot) -> PredictionResult:
        """Consume *snapshot* and return HUD and usercmd outputs."""

        if self._state is None:
            self._state = _PlayerState.from_snapshot(snapshot)
            self._last_server_time = snapshot.server_time
        else:
            delta = snapshot.server_time - (self._last_server_time or snapshot.server_time)
            self._state = self._advance(self._state, snapshot, delta)
            self._last_server_time = snapshot.server_time

        self._match_state = self._normalise_match_state(snapshot.match_state)

        hud_state = HUDState(
            health=self._state.health,
            armor=self._state.armor,
            weapon=self._state.weapon,
            ammo=self._state.ammo,
            position=list(self._state.origin.values()),
            match_state=self._match_state,
        )

        user_cmd = self._normalise_user_cmd(snapshot.user_cmd)

        return PredictionResult(hud=hud_state, user_cmd=user_cmd)

    def _advance(self, state: _PlayerState, snapshot: Snapshot, delta: int) -> _PlayerState:
        next_state = state.clone()

        for command in snapshot.commands:
            action = command.get("action")
            if action == "move":
                self._apply_move(next_state, command, delta)
            elif action == "weapon":
                self._apply_weapon(next_state, command)
            elif action == "damage":
                self._apply_damage(next_state, command)
            elif action == "heal":
                self._apply_heal(next_state, command)
            elif action == "ammo":
                self._apply_ammo(next_state, command)
            elif action == "override_state":
                next_state = _PlayerState.from_snapshot(snapshot)
            else:
                # Unknown commands are ignored but keep determinism intact.
                continue

        # Merge in authoritative player state fields from the snapshot.
        authoritative = _PlayerState.from_snapshot(snapshot)
        next_state.health = authoritative.health
        next_state.armor = authoritative.armor
        next_state.weapon = authoritative.weapon
        for weapon, amount in authoritative.ammo.items():
            next_state.ammo[weapon] = amount
        next_state.origin.update(authoritative.origin)

        return next_state

    @staticmethod
    def _apply_move(state: _PlayerState, command: Mapping[str, Any], delta: int) -> None:
        scale = float(command.get("scale", 1.0)) * max(delta, 1)
        direction = command.get("direction", [0.0, 0.0, 0.0])
        if len(direction) != 3:
            raise ValueError("move command direction must have 3 components")
        for axis, component in zip(("x", "y", "z"), direction):
            state.origin[axis] = state.origin.get(axis, 0.0) + float(component) * scale

    @staticmethod
    def _apply_weapon(state: _PlayerState, command: Mapping[str, Any]) -> None:
        weapon = command.get("weapon")
        if weapon:
            state.weapon = str(weapon)

    @staticmethod
    def _apply_damage(state: _PlayerState, command: Mapping[str, Any]) -> None:
        amount = int(command.get("amount", 0))
        state.health = max(state.health - amount, 0)

    @staticmethod
    def _apply_heal(state: _PlayerState, command: Mapping[str, Any]) -> None:
        amount = int(command.get("amount", 0))
        state.health = state.health + amount

    @staticmethod
    def _apply_ammo(state: _PlayerState, command: Mapping[str, Any]) -> None:
        weapon = str(command.get("weapon", state.weapon))
        amount = int(command.get("amount", 0))
        state.ammo[weapon] = state.ammo.get(weapon, 0) + amount

    @staticmethod
    def _normalise_match_state(match_state: Mapping[str, Any] | None) -> Mapping[str, Any] | None:
        if match_state is None:
            return None
        if not isinstance(match_state, Mapping):  # pragma: no cover - defensive guard
            raise TypeError("match_state must be a mapping when provided")
        return {str(key): value for key, value in match_state.items()}

    @staticmethod
    def _normalise_user_cmd(user_cmd: Mapping[str, Any] | None) -> Mapping[str, Any]:
        if user_cmd is None:
            return {}
        if not isinstance(user_cmd, Mapping):  # pragma: no cover - defensive guard
            raise TypeError("user_cmd must be a mapping when provided")
        canonical: dict[str, Any] = {}
        for key, value in user_cmd.items():
            if isinstance(value, (list, tuple)):
                canonical[str(key)] = [value_part for value_part in value]
            else:
                canonical[str(key)] = value
        return canonical

