"""Data models for match simulation scenarios."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, Mapping, MutableMapping, Optional, Sequence


@dataclass
class CommandConfig:
    """Represents a scripted command issued by a bot."""

    time: float
    action: str
    params: Mapping[str, Any] = field(default_factory=dict)

    def as_dict(self) -> Dict[str, Any]:
        """Return a JSON-serialisable representation of the command."""

        return {
            "time": self.time,
            "action": self.action,
            "params": dict(self.params),
        }


@dataclass
class BotConfig:
    """Configuration for a bot participating in the simulation."""

    name: str
    team: Optional[str] = None
    script: Sequence[CommandConfig] = field(default_factory=tuple)
    initial_state: Mapping[str, Any] = field(default_factory=dict)
    spawn: Mapping[str, Any] = field(default_factory=dict)

    def as_dict(self) -> Dict[str, Any]:
        """Return a JSON-serialisable representation of the bot configuration."""

        return {
            "name": self.name,
            "team": self.team,
            "initial_state": dict(self.initial_state),
            "spawn": dict(self.spawn),
            "script": [command.as_dict() for command in self.script],
        }


@dataclass
class MatchConfig:
    """Top-level configuration for a match simulation."""

    map: str
    duration: float
    tick_rate: int = 20
    seed: Optional[int] = None
    bots: Sequence[BotConfig] = field(default_factory=tuple)
    metadata: MutableMapping[str, Any] = field(default_factory=dict)

    def as_dict(self) -> Dict[str, Any]:
        """Return a JSON-serialisable representation of the match configuration."""

        return {
            "map": self.map,
            "duration": self.duration,
            "tick_rate": self.tick_rate,
            "seed": self.seed,
            "metadata": dict(self.metadata),
            "bots": [bot.as_dict() for bot in self.bots],
        }
