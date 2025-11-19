"""Match simulation harness for scripted bot inputs."""

from __future__ import annotations

import copy
import json
import math
import random
import heapq
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Mapping, MutableMapping, Optional, Sequence, Tuple

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
    bot_profiles: Mapping[str, Mapping[str, Any]] = field(default_factory=dict)
    spawn_schedule: List[Mapping[str, Any]] = field(default_factory=list)
    access_permissions: Mapping[str, Any] = field(default_factory=dict)

    def to_json(self, *, indent: int = 2) -> str:
        """Serialise the result to JSON."""

        payload = {
            "config": self.config.as_dict(),
            "bot_profiles": {key: dict(value) for key, value in self.bot_profiles.items()},
            "spawn_schedule": [dict(entry) for entry in self.spawn_schedule],
            "access_permissions": dict(self.access_permissions),
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
        # Store the resolved seed on the configuration so serialised timelines
        # reflect the actual deterministic inputs used for the run.
        self.config.seed = self.seed
        self.factory_settings: Mapping[str, Any] = dict(self.config.metadata.get("factory", {}))
        self.freeze_settings: Mapping[str, Any] = self._load_freeze_settings(
            self.config.metadata.get("freeze")
        )
        self.ctf_settings: Mapping[str, Any] = self._load_ctf_settings(
            self.config.metadata.get("ctf")
        )
        self.clanarena_settings: Mapping[str, Any] = self._load_clanarena_settings(
            self.config.metadata.get("clanarena")
        )
        self.duel_settings: Mapping[str, Any] = dict(self.config.metadata.get("duel", {}))
        (
            self.bot_profiles,
            self.spawn_schedule,
            self.access_permissions,
        ) = self._load_bot_resources(self.config.metadata.get("bot_resources"))
        self._bot_configs: Dict[str, BotConfig] = {bot.name: bot for bot in self.config.bots}
        self._active_bots: Mapping[str, BotState] = {}
        self._current_time: float = 0.0
        self._spawn_queue: list[tuple[float, int, Dict[str, Any]]] = []
        self._item_queue: list[tuple[float, int, Dict[str, Any]]] = []
        self._pending_freeze_events: list[Dict[str, Any]] = []
        self._event_counter = 0
        self._next_warmup_spawn_time: float = 0.0
        self._freeze_round_state: Optional[str] = None
        self._freeze_round_index: int = 0
        self._flag_positions: Dict[str, str] = {}
        self._flag_carriers: Dict[str, str] = {}
        self._flag_return_deadlines: Dict[str, float] = {}
        self._warmup_deadline: float = 0.0
        self._shuffle_countdown_deadline: Optional[float] = None
        self._clanarena_population: Dict[str, int] = {"red": 0, "blue": 0}
        self._flood_counters: Dict[str, Dict[str, float]] = {}

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
        self._active_bots = bots
        scripts = {
            bot_config.name: sorted(bot_config.script, key=lambda command: command.time)
            for bot_config in self.config.bots
        }
        script_indices = {name: 0 for name in bots}
        self._reset_queued_events()
        self._prime_spawn_schedule()
        self._prime_duel_events()

        frames: List[TimelineFrame] = []
        for tick in range(total_ticks):
            current_time = tick * delta
            self._current_time = current_time
            events: List[Dict[str, Any]] = []
            events.extend(self._collect_scheduled_spawns(current_time, bots))
            events.extend(self._collect_scheduled_items(current_time, bots))
            self._advance_freeze_state(current_time, bots)
            events.extend(self._collect_freeze_events())
            for bot_name, bot_state in bots.items():
                idx = script_indices[bot_name]
                bot_script = scripts.get(bot_name, [])
                while idx < len(bot_script) and bot_script[idx].time <= current_time + 1e-6:
                    command = bot_script[idx]
                    idx += 1
                    event = self._apply_command(bot_state, command, delta)
                    events.append(event)
                script_indices[bot_name] = idx
            # Commands executed during the tick may have scheduled additional
            # delayed events. Collect any that are now due so they appear within
            # the same timeline frame.
            events.extend(self._collect_scheduled_spawns(current_time, bots))
            events.extend(self._collect_scheduled_items(current_time, bots))
            self._advance_freeze_state(current_time, bots)
            events.extend(self._collect_freeze_events())
            frame = TimelineFrame(
                tick=tick,
                time=round(current_time, 6),
                events=events,
                bots={name: state.snapshot() for name, state in bots.items()},
            )
            frames.append(frame)
        return SimulationResult(
            self.config,
            frames,
            bot_profiles=copy.deepcopy(self.bot_profiles),
            spawn_schedule=[dict(entry) for entry in self.spawn_schedule],
            access_permissions=copy.deepcopy(self.access_permissions),
        )

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
        state = BotState(
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
        self._apply_factory_loadout(state, bot)
        self._snapshot_factory_defaults(state)
        return state

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

    def _handle_pickup(self, state: BotState, params: Mapping[str, Any], delta: float) -> Dict[str, Any]:
        pickup_type = str(params.get("type", "generic")).lower()
        if pickup_type == "ammo":
            return self._pickup_ammo(state, params)
        if pickup_type == "armor":
            return self._pickup_armor(state, params)
        if pickup_type == "flag":
            return self._pickup_flag(state, params)
        return {"type": pickup_type, "status": "ignored", "reason": "unsupported pickup"}

    def _handle_damage(self, state: BotState, params: Mapping[str, Any], delta: float) -> Dict[str, Any]:
        target_state = self._resolve_target_state(params.get("target"), state)
        if target_state is None:
            return {"status": "missing_target"}
        amount = float(params.get("amount", 0.0))
        if self._freeze_should_block_damage(target_state):
            expires = target_state.custom.get("freeze_protected_until")
            return {
                "status": "blocked",
                "reason": "spawn_protection",
                "target": target_state.name,
                "expires": expires,
            }
        target_state.health = max(0.0, target_state.health - amount)
        details: Dict[str, Any] = {"health": target_state.health, "amount": amount}
        if target_state is not state:
            details["target"] = target_state.name
        return details

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

    def _handle_request_spawn(
        self, state: BotState, params: Mapping[str, Any], delta: float
    ) -> Dict[str, Any]:
        warmup = bool(params.get("warmup", False))
        reason = params.get("reason")
        issuer = params.get("issuer")
        command_name = str(params.get("command", "request_spawn"))
        target_reference = params.get("bot")
        target_name, target_alias = self._resolve_spawn_target(state.name, target_reference)
        allowed, denial_reason = self._evaluate_access(issuer, command_name, target_name)
        if not allowed:
            return {
                "status": "rejected",
                "reason": denial_reason,
                "issuer": issuer,
                "command": command_name,
                "target": target_name,
                "alias": target_alias,
            }
        delay_ms_key = "warmup_ms" if warmup else "live_ms"
        delay_ms = self._get_factory_setting("spawn_delays", delay_ms_key, default=0)
        delay_seconds = max(0.0, float(delay_ms) / 1000.0)
        if warmup:
            base_time = max(self._current_time, self._next_warmup_spawn_time)
        else:
            base_time = self._current_time
        scheduled_time = round(base_time + delay_seconds, 6)
        if warmup:
            self._next_warmup_spawn_time = scheduled_time
        payload = {
            "bot": target_name,
            "warmup": warmup,
            "delay": delay_seconds,
            "scheduled_time": scheduled_time,
            "reason": reason,
            "issuer": issuer,
            "command": command_name,
            "alias": target_alias,
            "source": "command",
        }
        self._schedule_spawn_event(scheduled_time, payload)
        return {
            "status": "queued",
            "warmup": warmup,
            "scheduled_time": scheduled_time,
            "delay": delay_seconds,
            "reason": reason,
            "issuer": issuer,
            "command": command_name,
            "target": target_name,
            "alias": target_alias,
        }

    def _handle_drop_item(
        self, state: BotState, params: Mapping[str, Any], delta: float
    ) -> Dict[str, Any]:
        item = str(params.get("name", "unknown"))
        allow_drops = bool(self._get_factory_setting("items", "allow_drops", default=True))
        allow_bounce = bool(self._get_factory_setting("items", "allow_bounce", default=False))
        respawn_seconds = self._get_factory_setting("items", "respawn_seconds")
        return_seconds = self._get_factory_setting("items", "return_seconds")
        details: Dict[str, Any] = {"item": item}
        if not allow_drops:
            details["status"] = "suppressed"
            if return_seconds is None:
                scheduled_time = round(self._current_time, 6)
            else:
                scheduled_time = round(self._current_time + float(return_seconds), 6)
            self._schedule_item_event(
                scheduled_time,
                {
                    "bot": state.name,
                    "action": "item_return",
                    "item": item,
                    "return_time": scheduled_time,
                },
            )
            return details
        details["status"] = "dropped"
        details["bounce"] = allow_bounce
        if respawn_seconds is not None:
            scheduled_time = round(self._current_time + float(respawn_seconds), 6)
            self._schedule_item_event(
                scheduled_time,
                {
                    "bot": state.name,
                    "action": "item_respawn",
                    "item": item,
                    "respawn_time": scheduled_time,
                },
            )
        return details

    def _handle_set_warmup(self, state: BotState, params: Mapping[str, Any], delta: float) -> Dict[str, Any]:
        seconds = max(0.0, float(params.get("seconds", 0.0)))
        self._warmup_deadline = round(self._current_time + seconds, 6)
        return {"warmup_deadline": self._warmup_deadline, "seconds": seconds}

    def _handle_set_team_counts(
        self, state: BotState, params: Mapping[str, Any], delta: float
    ) -> Dict[str, Any]:
        red = max(0, int(params.get("red", 0)))
        blue = max(0, int(params.get("blue", 0)))
        self._clanarena_population = {"red": red, "blue": blue}
        return {"red": red, "blue": blue, "total": red + blue}

    def _handle_tick_shuffle(
        self, state: BotState, params: Mapping[str, Any], delta: float
    ) -> Dict[str, Any]:
        return self._update_shuffle_state()

    def _handle_check_warmup_gate(
        self, state: BotState, params: Mapping[str, Any], delta: float
    ) -> Dict[str, Any]:
        return self._evaluate_warmup_gate()

    def _handle_shuffle_vote(
        self, state: BotState, params: Mapping[str, Any], delta: float
    ) -> Dict[str, Any]:
        issuer = str(params.get("issuer", "")).strip()
        label = str(params.get("label", "shuffle"))
        if not issuer:
            return {"status": "ignored", "reason": "missing_issuer"}
        allowed, wait = self._apply_flood_gate(issuer)
        if allowed:
            return {"status": "accepted", "issuer": issuer, "label": label}
        return {
            "status": "denied",
            "issuer": issuer,
            "label": label,
            "penalty_remaining": wait,
        }

    def _handle_set_round_state(
        self, state: BotState, params: Mapping[str, Any], delta: float
    ) -> Dict[str, Any]:
        round_state = str(params.get("state", "warmup")).lower()
        previous_state = self._freeze_round_state
        self._freeze_round_state = round_state
        details: Dict[str, Any] = {"state": round_state, "previous": previous_state}
        if round_state == "active":
            self._freeze_round_index += 1
            details["round"] = self._freeze_round_index
            self._freeze_reset_for_round()
        return details

    def _handle_freeze_target(
        self, state: BotState, params: Mapping[str, Any], delta: float
    ) -> Dict[str, Any]:
        target_state = self._resolve_target_state(params.get("target"), state)
        if target_state is None:
            return {"status": "missing_target"}
        reason = str(params.get("reason", "damage"))
        environmental = bool(params.get("environmental", False))
        details = self._freeze_apply_freeze(target_state, reason, environmental)
        details["target"] = target_state.name
        return details

    def _handle_assist_thaw(
        self, state: BotState, params: Mapping[str, Any], delta: float
    ) -> Dict[str, Any]:
        target_state = self._resolve_target_state(params.get("target"), None)
        if target_state is None:
            return {"status": "missing_target"}
        if not target_state.custom.get("freeze_frozen"):
            return {"status": "not_frozen", "target": target_state.name}
        distance = self._distance(state.position, target_state.position)
        thaw_radius = float(self.freeze_settings.get("thaw_radius", 0.0))
        if thaw_radius and distance > thaw_radius:
            return {
                "status": "out_of_range",
                "target": target_state.name,
                "distance": distance,
                "radius": thaw_radius,
            }
        line_of_sight = bool(params.get("line_of_sight", True))
        if (not line_of_sight) and not bool(self.freeze_settings.get("thaw_through_surface")):
            return {
                "status": "blocked",
                "target": target_state.name,
                "reason": "line_of_sight",
            }
        progress = target_state.custom.get("freeze_progress", 0.0)
        thaw_tick = float(self.freeze_settings.get("thaw_tick", 0.0))
        thaw_time = float(self.freeze_settings.get("thaw_time", 1.0))
        progress += thaw_tick
        target_state.custom["freeze_progress"] = progress
        details = {
            "status": "progress",
            "target": target_state.name,
            "progress": progress,
            "required": thaw_time,
        }
        if thaw_time and progress >= thaw_time:
            target_state.custom["freeze_progress"] = 0.0
            self._freeze_thaw_bot(target_state, reason="assist", source=state.name)
            details["status"] = "completed"
        return details

    def _handle_complete_round(
        self, state: BotState, params: Mapping[str, Any], delta: float
    ) -> Dict[str, Any]:
        winner = params.get("winner")
        if not winner:
            return {"status": "missing_winner"}
        team = str(winner)
        thawed: List[str] = []
        if bool(self.freeze_settings.get("thaw_winning_team")):
            for target_state in self._active_bots.values():
                if target_state.team == team and target_state.custom.get("freeze_frozen"):
                    self._freeze_thaw_bot(target_state, reason="round_win", source=team)
                    thawed.append(target_state.name)
        return {"winner": team, "thawed": thawed}

    # ------------------------------------------------------------------
    # Pickup helpers
    # ------------------------------------------------------------------

    def _pickup_ammo(self, state: BotState, params: Mapping[str, Any]) -> Dict[str, Any]:
        weapon = str(params.get("weapon", "unknown"))
        request = float(params.get("amount", 0.0))
        max_amount = float(params.get("max", state.ammo.get(weapon, 0.0) + request))
        current = float(state.ammo.get(weapon, 0.0))
        capacity = max(0.0, max_amount - current)
        granted = min(capacity, max(0.0, request))
        denied = max(0.0, request - granted)
        new_total = current + granted
        state.ammo[weapon] = new_total
        saturated = new_total >= max_amount - 1e-6
        return {
            "type": "ammo",
            "weapon": weapon,
            "requested": request,
            "granted": granted,
            "denied": denied,
            "total": new_total,
            "max": max_amount,
            "saturated": saturated,
        }

    def _pickup_armor(self, state: BotState, params: Mapping[str, Any]) -> Dict[str, Any]:
        requested = float(params.get("amount", 0.0))
        max_armor = float(params.get("max", 0.0)) or float(state.inventory.get("armor", 0.0) + requested)
        handicap = params.get("handicap")
        if handicap is None:
            handicap = state.custom.get("handicap")
        effective_max = max_armor
        handicap_applied = False
        if handicap is not None:
            try:
                scale = float(handicap)
            except (TypeError, ValueError):
                scale = 1.0
            effective_max = max_armor * max(0.0, min(scale, 1.0))
            handicap_applied = True
        current = float(state.inventory.get("armor", 0.0))
        capacity = max(0.0, effective_max - current)
        granted = min(capacity, max(0.0, requested))
        denied = max(0.0, requested - granted)
        new_total = current + granted
        state.inventory["armor"] = new_total
        saturated = new_total >= effective_max - 1e-6
        return {
            "type": "armor",
            "requested": requested,
            "granted": granted,
            "denied": denied,
            "total": new_total,
            "max": max_armor,
            "effective_max": effective_max,
            "handicap_applied": handicap_applied,
            "saturated": saturated,
        }

    def _pickup_flag(self, state: BotState, params: Mapping[str, Any]) -> Dict[str, Any]:
        flag = str(params.get("flag", "neutral")).lower()
        event_type = str(params.get("event", "pickup")).lower()
        mode = str(params.get("mode", "ctf")).lower()
        score_delta = int(params.get("score", 1))
        context = str(params.get("context", params.get("reason", ""))).lower()
        suicide = bool(params.get("suicide"))
        self._flag_positions.setdefault(flag, "base")
        details: Dict[str, Any] = {
            "type": "flag",
            "flag": flag,
            "mode": mode,
            "event": event_type,
        }
        ctf_enabled = bool(self.ctf_settings.get("enabled"))
        carrier = self._flag_carriers.get(flag)
        current_flag = state.custom.get("flag_carried")
        if event_type == "pickup":
            if current_flag:
                details.update({"status": "already_carrying", "carrying": current_flag})
                return details
            if carrier:
                details.update({"status": "already_carried", "carrier": carrier})
                return details
            self._flag_carriers[flag] = state.name
            state.custom["flag_carried"] = flag
            self._flag_positions[flag] = f"carried:{state.name}"
            details.update({"status": "picked", "carrier": state.name})
            return details
        if event_type == "drop":
            if current_flag != flag:
                details.update({"status": "not_carrier"})
                return details
            if ctf_enabled and (context == "forced_return" or (suicide and bool(self.ctf_settings.get("return_on_suicide")))):
                self._flag_carriers.pop(flag, None)
                state.custom.pop("flag_carried", None)
                self._flag_positions[flag] = "base"
                self._cancel_flag_timeout(flag)
                details.update({"status": "forced_return", "reason": context or "suicide"})
                return details
            self._flag_carriers.pop(flag, None)
            state.custom.pop("flag_carried", None)
            self._flag_positions[flag] = "dropped"
            if ctf_enabled:
                trajectory = self._compute_flag_trajectory(state)
                physics = self._flag_physics_details()
                details.update({"physics": physics, "trajectory": trajectory})
                deadline = self._schedule_flag_timeout(flag, state.name)
                if deadline is not None:
                    details["return_deadline"] = deadline
            details.update({"status": "dropped"})
            return details
        if event_type == "return":
            previous = self._flag_positions.get(flag, "base")
            if carrier:
                holder = self._flag_carriers.pop(flag, None)
                if holder:
                    for bot in self._active_bots.values():
                        if bot.name == holder:
                            bot.custom.pop("flag_carried", None)
                            break
            self._flag_positions[flag] = "base"
            self._cancel_flag_timeout(flag)
            details.update({"status": "returned", "previous": previous})
            return details
        if event_type == "capture":
            if current_flag != flag:
                details.update({"status": "no_flag"})
                return details
            self._flag_carriers.pop(flag, None)
            state.custom.pop("flag_carried", None)
            self._flag_positions[flag] = "base" if mode == "ctf" else "respawned"
            self._cancel_flag_timeout(flag)
            details.update({"status": "captured", "score_delta": score_delta})
            return details
        details.update({"status": "unknown_event"})
        return details

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

    # ------------------------------------------------------------------
    # Factory configuration helpers
    # ------------------------------------------------------------------

    def _reset_queued_events(self) -> None:
        self._spawn_queue = []
        self._item_queue = []
        self._event_counter = 0
        self._next_warmup_spawn_time = 0.0
        self._pending_freeze_events = []
        self._flag_positions = {}
        self._flag_carriers = {}
        self._flag_return_deadlines = {}
        self._warmup_deadline = 0.0
        self._shuffle_countdown_deadline = None
        self._clanarena_population = {"red": 0, "blue": 0}
        self._flood_counters = {}

    def _prime_spawn_schedule(self) -> None:
        for entry in self.spawn_schedule:
            time_point = float(entry.get("time", 0.0))
            payload = {
                "bot": entry.get("bot"),
                "warmup": bool(entry.get("warmup", False)),
                "delay": float(entry.get("delay", 0.0)),
                "scheduled_time": time_point,
                "reason": entry.get("reason"),
                "issuer": entry.get("issuer"),
                "command": entry.get("command", "schedule"),
                "alias": entry.get("alias"),
                "source": entry.get("source", "g_botSpawnList"),
                "count": entry.get("count"),
            }
            self._schedule_spawn_event(time_point, payload)

    def _get_factory_setting(self, *keys: str, default: Any = None) -> Any:
        value: Any = self.factory_settings
        for key in keys:
            if not isinstance(value, Mapping) or key not in value:
                return default
            value = value[key]
        return value

    def _load_bot_resources(
        self, payload: Any
    ) -> Tuple[Mapping[str, Mapping[str, Any]], List[Mapping[str, Any]], Mapping[str, Any]]:
        if not isinstance(payload, Mapping):
            return {}, [], {}
        bot_profiles = self._parse_bot_profiles(payload.get("g_botsFile"))
        spawn_schedule = self._parse_spawn_schedule(payload.get("g_botSpawnList"), bot_profiles)
        access_permissions = self._parse_access_permissions(payload.get("g_accessFile"))
        return bot_profiles, spawn_schedule, access_permissions

    def _parse_bot_profiles(self, payload: Any) -> Dict[str, Dict[str, Any]]:
        if payload is None:
            return {}
        data = self._ensure_sequence_or_mapping(payload, key="bots")
        entries: Sequence[Any]
        if isinstance(data, Mapping):
            entries = data.get("bots", [])
        else:
            entries = data
        profiles: Dict[str, Dict[str, Any]] = {}
        for raw in entries:
            if not isinstance(raw, Mapping):
                continue
            alias = str(raw.get("alias") or raw.get("name") or raw.get("bot") or "")
            if not alias:
                continue
            profile = {str(key): raw[key] for key in raw}
            if "name" not in profile:
                profile["name"] = alias
            profiles[alias] = profile
        return profiles

    def _parse_spawn_schedule(
        self, payload: Any, bot_profiles: Mapping[str, Mapping[str, Any]]
    ) -> List[Dict[str, Any]]:
        if payload is None:
            return []
        data = self._ensure_sequence_or_mapping(payload, key="schedule")
        if isinstance(data, Mapping):
            entries = data.get("schedule", [])
        else:
            entries = data
        schedule: List[Dict[str, Any]] = []
        cumulative = 0.0
        for index, raw in enumerate(entries):
            alias: Optional[str] = None
            warmup = False
            issuer = None
            command = None
            reason = None
            count: Optional[int] = None
            if isinstance(raw, Mapping):
                alias = str(raw.get("bot") or raw.get("alias") or raw.get("name") or "")
                warmup = bool(raw.get("warmup", False))
                issuer = raw.get("issuer")
                command = raw.get("command")
                reason = raw.get("reason")
                count = raw.get("count")
                if "time" in raw:
                    time_point = float(raw["time"])
                    delay_seconds = max(0.0, time_point - cumulative)
                    cumulative = time_point
                else:
                    delay_ms = raw.get("delay_ms")
                    if delay_ms is not None:
                        delay_seconds = float(delay_ms) / 1000.0
                    else:
                        delay_seconds = float(raw.get("delay", 0.0))
                    cumulative += delay_seconds
                    time_point = cumulative
            elif isinstance(raw, str):
                parts = raw.strip().split()
                if not parts:
                    continue
                alias = parts[0]
                delay_seconds = 0.0
                time_point = cumulative
                if len(parts) > 1:
                    token = parts[1]
                    if token.startswith("@"):
                        time_point = float(token[1:])
                        delay_seconds = max(0.0, time_point - cumulative)
                        cumulative = time_point
                    else:
                        delay_seconds = float(token) / 1000.0
                        cumulative += delay_seconds
                        time_point = cumulative
                if len(parts) > 2:
                    reason = " ".join(parts[2:])
            else:
                continue
            if not alias:
                continue
            profile = bot_profiles.get(alias)
            bot_name = str(profile.get("name") if profile else alias)
            schedule.append(
                {
                    "alias": alias,
                    "bot": bot_name,
                    "time": round(time_point, 6),
                    "delay": round(float(delay_seconds), 6),
                    "warmup": warmup,
                    "issuer": issuer,
                    "command": command,
                    "reason": reason or "scripted_spawn",
                    "index": index,
                    "source": "g_botSpawnList",
                    "count": count,
                }
            )
        return schedule

    def _parse_access_permissions(self, payload: Any) -> Dict[str, Any]:
        if payload is None:
            return {"commands": {}, "spawns": {}}
        if isinstance(payload, str):
            try:
                payload = json.loads(payload)
            except json.JSONDecodeError as exc:
                raise ValueError("g_accessFile payload must be valid JSON or mapping") from exc
        if not isinstance(payload, Mapping):
            raise TypeError("g_accessFile payload must be a mapping")
        commands_raw = payload.get("commands", {})
        spawns_raw = payload.get("spawns", {})
        commands = {
            str(key): self._normalise_access_entry(value)
            for key, value in self._iterate_mapping(commands_raw)
        }
        spawns = {
            str(key): self._normalise_access_entry(value)
            for key, value in self._iterate_mapping(spawns_raw)
        }
        return {"commands": commands, "spawns": spawns}

    def _normalise_access_entry(self, value: Any) -> Dict[str, List[str]]:
        if isinstance(value, str):
            tokens = value.split()
            return {"allow": tokens}
        if isinstance(value, Sequence) and not isinstance(value, Mapping):
            return {"allow": [str(token) for token in value]}
        if not isinstance(value, Mapping):
            raise TypeError("Access entry must be a mapping, string, or sequence")
        entry: Dict[str, List[str]] = {}
        allow = value.get("allow")
        deny = value.get("deny")
        if allow is not None:
            entry["allow"] = [str(token) for token in self._ensure_sequence(allow)]
        if deny is not None:
            entry["deny"] = [str(token) for token in self._ensure_sequence(deny)]
        return entry

    def _ensure_sequence_or_mapping(self, payload: Any, key: str) -> Any:
        if payload is None:
            return []
        if isinstance(payload, str):
            try:
                payload = json.loads(payload)
            except json.JSONDecodeError:
                lines = [
                    line.strip()
                    for line in payload.splitlines()
                    if line.strip() and not line.strip().startswith("#")
                ]
                return lines
        if isinstance(payload, (Mapping, list, tuple)):
            return payload
        raise TypeError(f"Expected mapping or sequence for {key} payload")

    @staticmethod
    def _ensure_sequence(value: Any) -> Sequence[str]:
        if isinstance(value, str):
            return value.split()
        if isinstance(value, Sequence):
            return [str(token) for token in value]
        raise TypeError("Access list entries must be sequences or strings")

    @staticmethod
    def _iterate_mapping(value: Any) -> Sequence[Tuple[str, Any]]:
        if isinstance(value, Mapping):
            return list(value.items())
        if isinstance(value, Sequence):
            entries: List[Tuple[str, Any]] = []
            for item in value:
                if isinstance(item, Mapping) and "name" in item and "rules" in item:
                    entries.append((str(item["name"]), item["rules"]))
            return entries
        return []

    def _resolve_spawn_target(
        self, default_name: str, target_reference: Optional[Any]
    ) -> Tuple[str, Optional[str]]:
        if target_reference is None:
            return default_name, default_name
        alias = str(target_reference)
        profile = self.bot_profiles.get(alias)
        if profile:
            target_name = str(profile.get("name", alias))
            return target_name, alias
        return alias, alias

    def _evaluate_access(
        self, issuer: Any, command_name: str, target_name: str
    ) -> Tuple[bool, Optional[str]]:
        issuer_key = str(issuer) if issuer is not None else None
        allowed, reason = self._check_command_access(issuer_key, command_name)
        if not allowed:
            return False, reason
        allowed, reason = self._check_spawn_access(issuer_key, target_name)
        if not allowed:
            return False, reason
        return True, None

    def _check_command_access(
        self, issuer: Optional[str], command_name: str
    ) -> Tuple[bool, Optional[str]]:
        permissions = self.access_permissions.get("commands", {})
        entry = permissions.get(command_name) or permissions.get("*")
        if not entry:
            return True, None
        return self._check_access_entry(entry, issuer, f"command '{command_name}'")

    def _check_spawn_access(
        self, issuer: Optional[str], target_name: str
    ) -> Tuple[bool, Optional[str]]:
        permissions = self.access_permissions.get("spawns", {})
        entry = permissions.get(target_name) or permissions.get("*")
        if not entry:
            return True, None
        return self._check_access_entry(entry, issuer, f"spawn '{target_name}'")

    def _check_access_entry(
        self, entry: Mapping[str, Sequence[str]], issuer: Optional[str], context: str
    ) -> Tuple[bool, Optional[str]]:
        allowed = entry.get("allow")
        denied = entry.get("deny")
        if allowed is not None:
            if issuer is None or issuer not in allowed:
                return False, f"issuer '{issuer}' not permitted for {context}"
        if denied is not None and issuer is not None and issuer in denied:
            return False, f"issuer '{issuer}' denied for {context}"
        return True, None

    def _apply_factory_loadout(self, state: BotState, bot: BotConfig) -> None:
        loadouts = self._get_factory_setting("loadouts", default={})
        if not isinstance(loadouts, Mapping):
            return
        loadout_id = bot.spawn.get("factory_loadout")
        if loadout_id is None:
            loadout_id = self._get_factory_setting("bot_loadouts", default={}).get(bot.name)
        if loadout_id is None:
            loadout_id = self._get_factory_setting("active_loadout")
        if not loadout_id:
            return
        loadout = loadouts.get(loadout_id)
        if not isinstance(loadout, Mapping):
            return
        ammo = loadout.get("ammo", {})
        inventory = loadout.get("inventory", {})
        if isinstance(ammo, Mapping):
            for weapon, amount in ammo.items():
                state.ammo[str(weapon)] = float(amount)
        if isinstance(inventory, Mapping):
            for item, count in inventory.items():
                state.inventory[str(item)] = int(count)

    def _schedule_spawn_event(self, time_point: float, payload: Dict[str, Any]) -> None:
        entry = (time_point, self._event_counter, payload)
        heapq.heappush(self._spawn_queue, entry)
        self._event_counter += 1

    def _schedule_item_event(self, time_point: float, payload: Dict[str, Any]) -> None:
        entry = (time_point, self._event_counter, payload)
        heapq.heappush(self._item_queue, entry)
        self._event_counter += 1

    def _prime_duel_events(self) -> None:
        duel = self.duel_settings
        if not isinstance(duel, Mapping):
            return

        loadout = duel.get("loadout_grant")
        if loadout:
            self._schedule_item_event(
                0.0,
                {
                    "action": "duel_loadout",
                    "script": str(loadout),
                },
            )

        ready = duel.get("ready_up")
        if isinstance(ready, Mapping) and ready:
            payload = {"action": "duel_ready_up"}
            payload.update({key: value for key, value in ready.items()})
            self._schedule_item_event(0.0, payload)

        sudden_death = duel.get("sudden_death")
        if isinstance(sudden_death, Mapping) and sudden_death:
            payload = {"action": "duel_sudden_death"}
            payload.update({key: value for key, value in sudden_death.items()})
            self._schedule_item_event(0.0, payload)

    def _collect_scheduled_spawns(
        self, current_time: float, bots: Mapping[str, BotState]
    ) -> List[Dict[str, Any]]:
        events: List[Dict[str, Any]] = []
        while self._spawn_queue and self._spawn_queue[0][0] <= current_time + 1e-6:
            scheduled_time, _, payload = heapq.heappop(self._spawn_queue)
            bot_name = payload.get("bot")
            bot_state = bots.get(bot_name) if bot_name else None
            team = bot_state.team if bot_state else None
            protection = None
            if bot_state is not None:
                protection = self._freeze_apply_spawn_protection(bot_state, scheduled_time)
            events.append(
                {
                    "bot": bot_name,
                    "team": team,
                    "time": round(scheduled_time, 6),
                    "action": "client_spawn",
                    "details": {
                        "warmup": bool(payload.get("warmup", False)),
                        "delay": float(payload.get("delay", 0.0)),
                        "scheduled_time": round(scheduled_time, 6),
                        "reason": payload.get("reason"),
                        "issuer": payload.get("issuer"),
                        "command": payload.get("command"),
                        "alias": payload.get("alias"),
                        "source": payload.get("source"),
                        "count": payload.get("count"),
                        "freeze_protection_expires": protection,
                    },
                }
            )
        return events

    def _collect_scheduled_items(
        self, current_time: float, bots: Mapping[str, BotState]
    ) -> List[Dict[str, Any]]:
        events: List[Dict[str, Any]] = []
        while self._item_queue and self._item_queue[0][0] <= current_time + 1e-6:
            scheduled_time, _, payload = heapq.heappop(self._item_queue)
            bot_name = payload.get("bot")
            bot_state = bots.get(bot_name) if bot_name else None
            team = bot_state.team if bot_state else None
            action = payload.get("action", "item_event")
            details = {key: value for key, value in payload.items() if key not in {"bot", "action"}}
            details["time"] = round(scheduled_time, 6)
            if action == "flag_return":
                flag = payload.get("flag")
                if flag is None:
                    continue
                deadline = self._flag_return_deadlines.get(flag)
                if deadline is None or abs(deadline - scheduled_time) > 1e-6:
                    continue
                self._flag_positions[flag] = "base"
                self._flag_carriers.pop(flag, None)
                self._flag_return_deadlines.pop(flag, None)
                details.setdefault("flag", flag)
                details.setdefault("status", "returned")
            events.append(
                {
                    "bot": bot_name,
                    "team": team,
                    "time": round(scheduled_time, 6),
                    "action": action,
                    "details": details,
                }
            )
        return events

    def _collect_freeze_events(self) -> List[Dict[str, Any]]:
        events = list(self._pending_freeze_events)
        self._pending_freeze_events = []
        return events

    # ------------------------------------------------------------------
    # Freeze Tag helpers
    # ------------------------------------------------------------------

    def _load_freeze_settings(self, payload: Any) -> Mapping[str, Any]:
        if not isinstance(payload, Mapping):
            return {"enabled": False}
        cvars = payload.get("cvars", payload)
        if not isinstance(cvars, Mapping):
            return {"enabled": False}
        settings = {
            "enabled": bool(payload.get("enabled", True)),
            "protected_spawn_time": self._convert_ms(cvars.get("g_freezeProtectedSpawnTime"), default=0.0),
            "auto_thaw_time": self._convert_ms(cvars.get("g_freezeAutoThawTime"), default=0.0),
            "environmental_respawn_delay": self._convert_ms(
                cvars.get("g_freezeEnvironmentalRespawnDelay"), default=0.0
            ),
            "thaw_time": self._convert_ms(cvars.get("g_freezeThawTime"), default=2.0),
            "thaw_tick": self._convert_ms(cvars.get("g_freezeThawTick"), default=0.25),
            "thaw_radius": float(cvars.get("g_freezeThawRadius", 0.0)),
            "thaw_through_surface": bool(cvars.get("g_freezeThawThroughSurface", 0)),
            "thaw_winning_team": bool(cvars.get("g_freezeThawWinningTeam", 0)),
            "reset_weapons": bool(cvars.get("g_freezeResetWeaponsOnRound", 0)),
            "reset_health": bool(cvars.get("g_freezeResetHealthOnRound", 0)),
            "reset_armor": bool(cvars.get("g_freezeResetArmorOnRound", 0)),
            "remove_powerups": bool(cvars.get("g_freezeRemovePowerupsOnRound", 0)),
        }
        return settings

    @staticmethod
    def _convert_ms(value: Any, *, default: float = 0.0) -> float:
        if value is None:
            return float(default)
        return max(0.0, float(value) / 1000.0)

    def _advance_freeze_state(self, current_time: float, bots: Mapping[str, BotState]) -> None:
        if not bool(self.freeze_settings.get("enabled")):
            return
        for bot_state in bots.values():
            if not bot_state.custom.get("freeze_frozen"):
                continue
            deadline = bot_state.custom.get("freeze_thaw_deadline")
            if deadline is None:
                continue
            if current_time + 1e-6 >= deadline:
                reason = "auto_thaw"
                if bot_state.custom.get("freeze_environmental"):
                    reason = "environmental"
                self._freeze_thaw_bot(bot_state, reason=reason, source="timer")

    def _freeze_apply_freeze(
        self, state: BotState, reason: str, environmental: bool
    ) -> Dict[str, Any]:
        state.custom["freeze_frozen"] = True
        state.custom["freeze_progress"] = 0.0
        state.custom["freeze_environmental"] = environmental
        state.custom["freeze_applied_at"] = self._current_time
        auto_thaw = float(self.freeze_settings.get("auto_thaw_time", 0.0))
        env_delay = float(self.freeze_settings.get("environmental_respawn_delay", 0.0))
        if environmental and env_delay > 0:
            deadline = self._current_time + env_delay
        elif auto_thaw > 0:
            deadline = self._current_time + auto_thaw
        else:
            deadline = None
        state.custom["freeze_thaw_deadline"] = deadline
        state.health = 0.0
        return {
            "status": "frozen",
            "reason": reason,
            "deadline": deadline,
            "environmental": environmental,
        }

    def _freeze_thaw_bot(self, state: BotState, *, reason: str, source: Any) -> None:
        if not state.custom.get("freeze_frozen"):
            return
        state.custom["freeze_frozen"] = False
        state.custom["freeze_progress"] = 0.0
        state.custom["freeze_environmental"] = False
        state.custom["freeze_thaw_deadline"] = None
        self._freeze_reset_player(state, source="thaw")
        expires = self._freeze_apply_spawn_protection(state, self._current_time)
        event = {
            "bot": state.name,
            "team": state.team,
            "time": round(self._current_time, 6),
            "action": "freeze_thaw",
            "details": {
                "reason": reason,
                "source": source,
                "protected_until": expires,
            },
        }
        self._pending_freeze_events.append(event)

    def _freeze_apply_spawn_protection(
        self, state: BotState, timestamp: float
    ) -> Optional[float]:
        if not bool(self.freeze_settings.get("enabled")):
            return None
        duration = float(self.freeze_settings.get("protected_spawn_time", 0.0))
        if duration <= 0.0:
            state.custom.pop("freeze_protected_until", None)
            return None
        expires = round(timestamp + duration, 6)
        state.custom["freeze_protected_until"] = expires
        return expires

    def _freeze_should_block_damage(self, state: BotState) -> bool:
        if not bool(self.freeze_settings.get("enabled")):
            return False
        expires = state.custom.get("freeze_protected_until")
        if expires is None:
            return False
        return self._current_time + 1e-6 < float(expires)

    def _freeze_reset_for_round(self) -> None:
        if not bool(self.freeze_settings.get("enabled")):
            return
        for bot_state in self._active_bots.values():
            self._freeze_reset_player(bot_state, source="round_reset")

    def _freeze_reset_player(self, state: BotState, *, source: str) -> None:
        defaults = state.custom.get("factory_defaults")
        if not isinstance(defaults, Mapping):
            return
        if bool(self.freeze_settings.get("reset_weapons")):
            ammo_defaults = defaults.get("ammo") or {}
            state.ammo = {weapon: float(amount) for weapon, amount in ammo_defaults.items()}
            inventory_defaults = defaults.get("inventory") or {}
            preserved_armor = state.inventory.get("armor")
            new_inventory = {
                key: int(value)
                for key, value in inventory_defaults.items()
                if key != "armor"
            }
            state.inventory = new_inventory
            if preserved_armor is not None:
                state.inventory["armor"] = int(preserved_armor)
        if bool(self.freeze_settings.get("reset_health")):
            state.health = float(defaults.get("health", state.health))
        if bool(self.freeze_settings.get("reset_armor")):
            armor_default = defaults.get("inventory", {}).get("armor", 0)
            state.inventory["armor"] = int(armor_default)
        if bool(self.freeze_settings.get("remove_powerups")):
            self._strip_powerups(state)

    def _strip_powerups(self, state: BotState) -> None:
        removals = []
        for key in list(state.inventory.keys()):
            if key.startswith("powerup") or key.endswith("powerup"):
                removals.append(key)
            elif key in {"quad_damage", "regeneration", "haste", "invisibility", "battle_suit"}:
                removals.append(key)
        for key in removals:
            state.inventory.pop(key, None)

    # ------------------------------------------------------------------
    # CTF helpers
    # ------------------------------------------------------------------

    def _load_ctf_settings(self, payload: Any) -> Mapping[str, Any]:
        if not isinstance(payload, Mapping):
            return {"enabled": False}
        cvars = payload.get("cvars", payload)
        if not isinstance(cvars, Mapping):
            return {"enabled": False}
        return {
            "enabled": bool(payload.get("enabled", True)),
            "flag_physics": bool(cvars.get("g_flagPhysics", 0)),
            "flag_bounce": float(cvars.get("g_flagBounce", 0.0)),
            "throw_forward": float(cvars.get("g_throwFlagForwardMult", 150.0)),
            "throw_velocity": float(cvars.get("g_throwFlagVelocity", 200.0)),
            "drop_timeout": self._convert_ms(cvars.get("g_flagDroppedTimeout"), default=0.0),
            "return_on_suicide": bool(cvars.get("g_returnFlagOnSuicide", 0)),
            "neutral_ping": self._convert_ms(cvars.get("g_neutralFlagPingTime"), default=0.0),
        }

    def _flag_physics_details(self) -> Dict[str, Any]:
        bounce = float(self.ctf_settings.get("flag_bounce", 0.0))
        bounce = max(0.0, min(1.0, bounce))
        return {
            "enabled": bool(self.ctf_settings.get("flag_physics")),
            "bounce": bounce,
        }

    def _compute_flag_trajectory(self, state: BotState) -> Dict[str, Any]:
        forward_speed = float(self.ctf_settings.get("throw_forward", 150.0))
        vertical_speed = float(self.ctf_settings.get("throw_velocity", 200.0))
        facing = self._normalise(state.facing)
        velocity = (
            facing[0] * forward_speed,
            facing[1] * forward_speed,
            facing[2] * forward_speed + vertical_speed,
        )
        return {
            "forward_speed": forward_speed,
            "vertical_speed": vertical_speed,
            "velocity": [round(component, 6) for component in velocity],
        }

    def _schedule_flag_timeout(self, flag: str, bot_name: str) -> Optional[float]:
        timeout = float(self.ctf_settings.get("drop_timeout", 0.0))
        if timeout <= 0.0:
            self._flag_return_deadlines.pop(flag, None)
            return None
        scheduled = round(self._current_time + timeout, 6)
        self._flag_return_deadlines[flag] = scheduled
        self._schedule_item_event(
            scheduled,
            {
                "bot": bot_name,
                "action": "flag_return",
                "flag": flag,
                "reason": "timeout",
            },
        )
        return scheduled

    def _cancel_flag_timeout(self, flag: str) -> None:
        self._flag_return_deadlines.pop(flag, None)

    # ------------------------------------------------------------------
    # Clan Arena helpers
    # ------------------------------------------------------------------

    def _load_clanarena_settings(self, payload: Any) -> Mapping[str, Any]:
        if not isinstance(payload, Mapping):
            return {"enabled": False}
        cvars = payload.get("cvars", payload)
        if not isinstance(cvars, Mapping):
            return {"enabled": False}
        return {
            "enabled": bool(payload.get("enabled", True)),
            "shuffle": {
                "automatic": bool(cvars.get("g_shuffleAutomatic", 0)),
                "timedelay": float(cvars.get("g_shuffleTimedelay", 0.0)),
                "min_players": int(cvars.get("g_shuffleMinPlayers", 0)),
                "auto_min_players": int(cvars.get("g_shuffleAutomaticMinPlayers", 0)),
            },
            "teams": {
                "min_size": int(cvars.get("g_teamSizeMin", 0)),
                "force_present": bool(cvars.get("g_teamForcePresent", 0)),
            },
            "flood": {
                "maxcount": int(cvars.get("g_floodprot_maxcount", 0)),
                "decay": self._convert_ms(cvars.get("g_floodprot_decay"), default=0.0),
                "penalty": self._convert_ms(cvars.get("g_floodprot_penalty"), default=0.0),
            },
        }

    def _update_shuffle_state(self) -> Dict[str, Any]:
        if not bool(self.clanarena_settings.get("enabled")):
            self._shuffle_countdown_deadline = None
            return {"status": "disabled"}
        shuffle = self.clanarena_settings.get("shuffle", {})
        if not bool(shuffle.get("automatic")):
            self._shuffle_countdown_deadline = None
            return {"status": "disabled"}
        red = self._clanarena_population.get("red", 0)
        blue = self._clanarena_population.get("blue", 0)
        total = red + blue
        delta = abs(red - blue)
        threshold = shuffle.get("auto_min_players") or shuffle.get("min_players") or 4
        warmup_active = self._warmup_deadline > self._current_time
        should_shuffle = warmup_active and total >= threshold and delta >= 2
        if self._shuffle_countdown_deadline and self._current_time >= self._shuffle_countdown_deadline:
            deadline = self._shuffle_countdown_deadline
            self._shuffle_countdown_deadline = None
            return {
                "status": "executed",
                "deadline": deadline,
                "total": total,
                "delta": delta,
            }
        if should_shuffle:
            if self._shuffle_countdown_deadline:
                return {
                    "status": "countdown_active",
                    "deadline": self._shuffle_countdown_deadline,
                    "total": total,
                    "delta": delta,
                }
            delay = max(0.0, float(shuffle.get("timedelay", 0.0)))
            if delay <= 0.0:
                return {
                    "status": "executed",
                    "deadline": self._current_time,
                    "total": total,
                    "delta": delta,
                }
            deadline = round(self._current_time + delay, 6)
            self._shuffle_countdown_deadline = deadline
            warmup_clamped = False
            if self._warmup_deadline < deadline:
                self._warmup_deadline = deadline
                warmup_clamped = True
            return {
                "status": "armed",
                "deadline": deadline,
                "delay": delay,
                "total": total,
                "delta": delta,
                "warmup_clamped": warmup_clamped,
                "warmup_deadline": self._warmup_deadline,
            }
        if self._shuffle_countdown_deadline:
            cancelled = self._shuffle_countdown_deadline
            self._shuffle_countdown_deadline = None
            return {
                "status": "cancelled",
                "deadline": cancelled,
                "total": total,
                "delta": delta,
            }
        return {"status": "idle", "total": total, "delta": delta}

    def _evaluate_warmup_gate(self) -> Dict[str, Any]:
        if not bool(self.clanarena_settings.get("enabled")):
            return {"status": "disabled"}
        teams = self.clanarena_settings.get("teams", {})
        required = max(0, int(teams.get("min_size", 0)))
        force_present = bool(teams.get("force_present"))
        red = self._clanarena_population.get("red", 0)
        blue = self._clanarena_population.get("blue", 0)
        ready = False
        if red >= 1 and blue >= 1:
            if required <= 1:
                ready = True
            elif force_present:
                ready = red >= required and blue >= required
            else:
                ready = red >= required or blue >= required
        status = "ready" if ready else "waiting"
        return {"status": status, "red": red, "blue": blue, "required": required}

    def _apply_flood_gate(self, issuer: str) -> Tuple[bool, float]:
        flood = self.clanarena_settings.get("flood", {})
        maxcount = int(flood.get("maxcount", 0))
        decay = float(flood.get("decay", 0.0))
        if maxcount <= 0 or decay <= 0.0:
            return True, 0.0
        now = self._current_time
        counter = self._flood_counters.setdefault(
            issuer, {"count": 0, "last": 0.0, "penalty": 0.0}
        )
        if counter["penalty"] > now:
            return False, round(counter["penalty"] - now, 6)
        if counter["last"] > 0.0:
            elapsed = now - counter["last"]
            if elapsed > 0.0:
                reduction = int(elapsed / decay)
                if reduction > 0:
                    counter["count"] = max(0, counter["count"] - reduction)
        counter["last"] = now
        counter["count"] += 1
        if counter["count"] > maxcount:
            penalty = float(flood.get("penalty", 0.0))
            if penalty <= 0.0:
                penalty = decay * maxcount
                if penalty <= 0.0:
                    penalty = decay
            counter["penalty"] = now + penalty
            counter["count"] = 0
            return False, round(penalty, 6)
        return True, 0.0


    def _snapshot_factory_defaults(self, state: BotState) -> None:
        state.custom["factory_defaults"] = {
            "health": state.health,
            "ammo": copy.deepcopy(state.ammo),
            "inventory": copy.deepcopy(state.inventory),
        }

    def _resolve_target_state(
        self, target_reference: Any, default: Optional[BotState]
    ) -> Optional[BotState]:
        if target_reference is None:
            return default
        target_name = str(target_reference)
        return self._active_bots.get(target_name)

    @staticmethod
    def _distance(a: Sequence[float], b: Sequence[float]) -> float:
        return math.sqrt(sum((a[i] - b[i]) ** 2 for i in range(3)))


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
