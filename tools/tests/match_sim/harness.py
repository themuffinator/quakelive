"""Match simulation harness for scripted bot inputs."""

from __future__ import annotations

import json
import math
import random
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Mapping, MutableMapping, Optional, Sequence

from .config import BotConfig, CommandConfig, MatchConfig


@dataclass
class BotState:
    """Represents the state of a bot at a given moment."""

    name: str
    team: Optional[str]
    position: Sequence[float]
    velocity: Sequence[float]
    facing: Sequence[float]
    health: float
    ammo: MutableMapping[str, float]
    inventory: MutableMapping[str, int]
    custom: MutableMapping[str, Any]
    last_action: Optional[str] = None
    last_message: Optional[str] = None

    def snapshot(self) -> Dict[str, Any]:
        """Produce a JSON-serialisable snapshot of the bot state."""

        return {
            "name": self.name,
            "team": self.team,
            "position": list(self.position),
            "velocity": list(self.velocity),
            "facing": list(self.facing),
            "health": self.health,
            "ammo": dict(self.ammo),
            "inventory": dict(self.inventory),
            "custom": dict(self.custom),
            "last_action": self.last_action,
            "last_message": self.last_message,
        }


@dataclass
class TimelineFrame:
    """A single time slice recorded by the simulator."""

    tick: int
    time: float
    events: List[Dict[str, Any]]
    bots: Dict[str, Dict[str, Any]]


@dataclass
class SimulationResult:
    """Outcome of a simulated match."""

    config: MatchConfig
    frames: List[TimelineFrame]

    def to_json(self, *, indent: int = 2) -> str:
        """Serialise the result to JSON."""

        payload = {
            "config": self.config.as_dict(),
            "frames": [
                {
                    "tick": frame.tick,
                    "time": frame.time,
                    "events": frame.events,
                    "bots": frame.bots,
                }
                for frame in self.frames
            ],
        }
        return json.dumps(payload, indent=indent)

    def write_json(self, path: Path) -> None:
        """Write the result to *path* in JSON format."""

        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(self.to_json(indent=2), encoding="utf-8")


class MatchHarness:
    """Runs scripted match simulations producing deterministic timelines."""

    def __init__(self, config: MatchConfig, *, seed: Optional[int] = None) -> None:
        self.config = config
        self.seed = self._resolve_seed(seed, config.seed)
        self.rng = random.Random(self.seed)

    @staticmethod
    def _resolve_seed(*seeds: Optional[int]) -> int:
        for candidate in seeds:
            if candidate is not None:
                return int(candidate)
        # Use a deterministic default seed to guarantee stability across runs.
        return 1337

    def run(self) -> SimulationResult:
        """Execute the simulation and produce a timeline."""

        tick_rate = self.config.tick_rate
        total_ticks = int(math.ceil(self.config.duration * tick_rate)) + 1
        delta = 1.0 / float(tick_rate)

        bots = {bot.name: self._initialise_bot(bot) for bot in self.config.bots}
        scripts = {
            bot_config.name: sorted(bot_config.script, key=lambda command: command.time)
            for bot_config in self.config.bots
        }
        script_indices = {name: 0 for name in bots}

        frames: List[TimelineFrame] = []
        for tick in range(total_ticks):
            current_time = tick * delta
            events: List[Dict[str, Any]] = []
            for bot_name, bot_state in bots.items():
                idx = script_indices[bot_name]
                bot_script = scripts.get(bot_name, [])
                while idx < len(bot_script) and bot_script[idx].time <= current_time + 1e-6:
                    command = bot_script[idx]
                    idx += 1
                    event = self._apply_command(bot_state, command, delta)
                    events.append(event)
                script_indices[bot_name] = idx
            frame = TimelineFrame(
                tick=tick,
                time=round(current_time, 6),
                events=events,
                bots={name: state.snapshot() for name, state in bots.items()},
            )
            frames.append(frame)
        return SimulationResult(self.config, frames)

    # ------------------------------------------------------------------
    # Bot initialisation and command handling
    # ------------------------------------------------------------------

    def _initialise_bot(self, bot: BotConfig) -> BotState:
        position = self._resolve_state_vector(bot.spawn.get("position"), default=(0.0, 0.0, 0.0))
        random_spawns = bot.spawn.get("random_positions")
        if random_spawns:
            candidates = []
            for candidate in random_spawns:
                if isinstance(candidate, Mapping) and "position" in candidate:
                    candidates.append(self._resolve_state_vector(candidate["position"]))
                else:
                    candidates.append(self._resolve_state_vector(candidate))
            position = self.rng.choice(candidates)
        velocity = self._resolve_state_vector(bot.initial_state.get("velocity"), default=(0.0, 0.0, 0.0))
        facing = self._resolve_state_vector(bot.initial_state.get("facing"), default=(1.0, 0.0, 0.0))
        health = float(bot.initial_state.get("health", 100.0))
        ammo = {
            key: float(value)
            for key, value in self._resolve_mapping(bot.initial_state.get("ammo", {})).items()
        }
        inventory = {
            key: int(value)
            for key, value in self._resolve_mapping(bot.initial_state.get("inventory", {})).items()
        }
        custom = dict(self._resolve_mapping(bot.initial_state.get("custom", {})))
        return BotState(
            name=bot.name,
            team=bot.team,
            position=position,
            velocity=velocity,
            facing=facing,
            health=health,
            ammo=ammo,
            inventory=inventory,
            custom=custom,
        )

    def _apply_command(self, state: BotState, command: CommandConfig, delta: float) -> Dict[str, Any]:
        params = self._resolve_mapping(command.params)
        action = command.action.lower()
        handler = getattr(self, f"_handle_{action}", None)
        if handler is None:
            return self._record_event(state, command, {"status": "ignored", "reason": "unknown action"})
        details = handler(state, params, delta)
        state.last_action = action
        return self._record_event(state, command, details)

    def _record_event(
        self, state: BotState, command: CommandConfig, details: Mapping[str, Any]
    ) -> Dict[str, Any]:
        event: Dict[str, Any] = {
            "bot": state.name,
            "team": state.team,
            "time": command.time,
            "action": command.action,
            "details": dict(details),
        }
        return event

    # ------------------------------------------------------------------
    # Command handlers
    # ------------------------------------------------------------------

    def _handle_move(self, state: BotState, params: Mapping[str, Any], delta: float) -> Dict[str, Any]:
        direction = self._resolve_state_vector(params.get("direction"), default=state.velocity)
        speed = float(params.get("speed", self._vector_length(direction)))
        normalised = self._normalise(direction)
        displacement = tuple(component * speed * delta for component in normalised)
        state.position = tuple(state.position[i] + displacement[i] for i in range(3))
        state.velocity = tuple(displacement[i] / delta for i in range(3))
        return {"position": list(state.position), "velocity": list(state.velocity)}

    def _handle_look(self, state: BotState, params: Mapping[str, Any], delta: float) -> Dict[str, Any]:
        facing = self._resolve_state_vector(params.get("direction"), default=state.facing)
        state.facing = self._normalise(facing)
        return {"facing": list(state.facing)}

    def _handle_shoot(self, state: BotState, params: Mapping[str, Any], delta: float) -> Dict[str, Any]:
        weapon = str(params.get("weapon", "machinegun"))
        ammo_cost = float(params.get("cost", 1.0))
        remaining = state.ammo.get(weapon, 0.0) - ammo_cost
        state.ammo[weapon] = max(0.0, remaining)
        return {"weapon": weapon, "ammo": state.ammo[weapon]}

    def _handle_item(self, state: BotState, params: Mapping[str, Any], delta: float) -> Dict[str, Any]:
        item = str(params.get("name", "unknown"))
        count = int(params.get("count", 1))
        state.inventory[item] = state.inventory.get(item, 0) + count
        return {"item": item, "count": state.inventory[item]}

    def _handle_damage(self, state: BotState, params: Mapping[str, Any], delta: float) -> Dict[str, Any]:
        amount = float(params.get("amount", 0.0))
        state.health = max(0.0, state.health - amount)
        return {"health": state.health, "amount": amount}

    def _handle_heal(self, state: BotState, params: Mapping[str, Any], delta: float) -> Dict[str, Any]:
        amount = float(params.get("amount", 0.0))
        state.health = state.health + amount
        return {"health": state.health, "amount": amount}

    def _handle_say(self, state: BotState, params: Mapping[str, Any], delta: float) -> Dict[str, Any]:
        message = str(params.get("message", ""))
        state.last_message = message
        return {"message": message}

    def _handle_custom(self, state: BotState, params: Mapping[str, Any], delta: float) -> Dict[str, Any]:
        state.custom.update(params)
        return {"custom": dict(state.custom)}

    def _handle_wait(self, state: BotState, params: Mapping[str, Any], delta: float) -> Dict[str, Any]:
        return {"status": "idle"}

    def _handle_set_state(self, state: BotState, params: Mapping[str, Any], delta: float) -> Dict[str, Any]:
        for key, value in params.items():
            if key == "position":
                state.position = self._resolve_state_vector(value, default=state.position)
            elif key == "velocity":
                state.velocity = self._resolve_state_vector(value, default=state.velocity)
            elif key == "facing":
                state.facing = self._resolve_state_vector(value, default=state.facing)
            elif key == "health":
                state.health = float(value)
            elif key == "ammo" and isinstance(value, Mapping):
                for weapon, amount in value.items():
                    state.ammo[str(weapon)] = float(amount)
            elif key == "inventory" and isinstance(value, Mapping):
                for item, count in value.items():
                    state.inventory[str(item)] = int(count)
            else:
                state.custom[str(key)] = value
        return {"state": state.snapshot()}

    def _handle_teleport(self, state: BotState, params: Mapping[str, Any], delta: float) -> Dict[str, Any]:
        destination = self._resolve_state_vector(params.get("position"), default=state.position)
        state.position = destination
        state.velocity = (0.0, 0.0, 0.0)
        return {"position": list(state.position)}

    # ------------------------------------------------------------------
    # Helpers for deterministic value resolution
    # ------------------------------------------------------------------

    def _resolve_mapping(self, value: Any) -> Dict[str, Any]:
        if value is None:
            return {}
        if isinstance(value, Mapping):
            return {str(key): self._resolve_value(val) for key, val in value.items()}
        raise TypeError(f"Expected mapping, received {type(value)!r}")

    def _resolve_state_vector(self, value: Any, *, default: Sequence[float] = (0.0, 0.0, 0.0)) -> Sequence[float]:
        if value is None:
            return tuple(default)
        resolved = self._resolve_value(value)
        if isinstance(resolved, Sequence) and len(resolved) == 3:
            return tuple(float(component) for component in resolved)
        raise ValueError(f"Expected a 3-element sequence, got {resolved!r}")

    def _resolve_value(self, value: Any) -> Any:
        if isinstance(value, Mapping) and "random" in value:
            return self._resolve_random(value["random"])
        if isinstance(value, Mapping):
            return {key: self._resolve_value(val) for key, val in value.items()}
        if isinstance(value, list):
            return [self._resolve_value(item) for item in value]
        return value

    def _resolve_random(self, spec: Mapping[str, Any]) -> Any:
        mode = spec.get("mode", "choice")
        if mode == "choice":
            options = spec.get("options")
            if not isinstance(options, Sequence) or not options:
                raise ValueError("random choice requires a non-empty 'options' sequence")
            return self._resolve_value(self.rng.choice(list(options)))
        if mode == "uniform":
            low = float(spec.get("low", 0.0))
            high = float(spec.get("high", 1.0))
            return self.rng.uniform(low, high)
        if mode == "randint":
            low = int(spec.get("low", 0))
            high = int(spec.get("high", low))
            return self.rng.randint(low, high)
        if mode == "normal":
            mu = float(spec.get("mu", 0.0))
            sigma = float(spec.get("sigma", 1.0))
            return self.rng.normalvariate(mu, sigma)
        if mode == "vector":
            dimensions = int(spec.get("dimensions", 3))
            length = float(spec.get("length", 1.0))
            vector = [self.rng.uniform(-1.0, 1.0) for _ in range(dimensions)]
            normalised = self._normalise(vector)
            return [component * length for component in normalised]
        raise ValueError(f"Unsupported random mode: {mode}")

    @staticmethod
    def _vector_length(vector: Sequence[float]) -> float:
        return math.sqrt(sum(component * component for component in vector))

    @staticmethod
    def _normalise(vector: Sequence[float]) -> Sequence[float]:
        length = MatchHarness._vector_length(vector)
        if length == 0:
            return tuple(0.0 for _ in vector)
        return tuple(component / length for component in vector)


def load_config(path: Path, *, seed: Optional[int] = None) -> MatchConfig:
    """Load a :class:`MatchConfig` from *path* and return it."""

    payload = json.loads(path.read_text(encoding="utf-8"))
    bots: List[BotConfig] = []
    for bot_payload in payload.get("bots", []):
        script = [
            CommandConfig(
                time=float(command["time"]),
                action=str(command["action"]),
                params=command.get("params", {}),
            )
            for command in bot_payload.get("script", [])
        ]
        bots.append(
            BotConfig(
                name=str(bot_payload["name"]),
                team=bot_payload.get("team"),
                script=tuple(script),
                initial_state=bot_payload.get("initial_state", {}),
                spawn=bot_payload.get("spawn", {}),
            )
        )
    config = MatchConfig(
        map=str(payload.get("map", "unknown")),
        duration=float(payload.get("duration", 0.0)),
        tick_rate=int(payload.get("tick_rate", 20)),
        seed=payload.get("seed"),
        bots=tuple(bots),
        metadata=payload.get("metadata", {}),
    )
    if seed is not None:
        config.seed = seed
    return config


def run_from_file(
    input_path: Path, *, seed: Optional[int] = None, output_path: Optional[Path] = None
) -> SimulationResult:
    """Convenience helper to load a config, run the harness, and optionally write JSON."""

    config = load_config(input_path, seed=seed)
    harness = MatchHarness(config, seed=seed)
    result = harness.run()
    if output_path is not None:
        result.write_json(output_path)
    return result


def main(argv: Optional[Sequence[str]] = None) -> int:
    """CLI entry point for match simulations."""

    import argparse

    parser = argparse.ArgumentParser(description="Run a scripted Quake Live match simulation.")
    parser.add_argument("scenario", type=Path, help="Path to a JSON scenario file.")
    parser.add_argument(
        "-o",
        "--output",
        type=Path,
        help="Optional destination for the resulting JSON timeline (defaults to stdout).",
    )
    parser.add_argument(
        "--seed",
        type=int,
        help="Override the seed used for deterministic random number generation.",
    )
    parser.add_argument(
        "--no-pretty",
        action="store_true",
        help="Disable pretty-printed JSON when writing to stdout.",
    )
    args = parser.parse_args(argv)

    result = run_from_file(args.scenario, seed=args.seed, output_path=args.output)
    if args.output is None:
        json_str = result.to_json(indent=None if args.no_pretty else 2)
        print(json_str)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
