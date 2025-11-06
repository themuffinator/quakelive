# Match simulation harness

The match simulation harness lives under `tools/tests/match_sim/` and provides a
scriptable way to orchestrate bot behaviour for deterministic test matches. The
harness translates a scenario description into a per-tick JSON timeline that can
be consumed by integration tests or analysis tooling.

## Running a simulation

```bash
python -m tools.tests.match_sim path/to/scenario.json \
  --seed 1337 \
  --output build/match-timelines/sample.json
```

When `--output` is omitted, the resulting timeline is printed to stdout. Pretty
printing is enabled by default; use `--no-pretty` to stream compact JSON.

### Scenario files

Scenarios are authored as JSON and contain the following top-level keys:

| Key | Type | Description |
| --- | ---- | ----------- |
| `map` | string | Identifier of the arena the match targets. |
| `duration` | number | Duration of the simulation in seconds. |
| `tick_rate` | integer | Number of simulation ticks per second (defaults to `20`). |
| `seed` | integer | Optional RNG seed. Overridden by the `--seed` CLI flag. |
| `metadata` | object | Free-form metadata copied to the JSON timeline. |
| `bots` | array | Collection of bot definitions (see below). |

Each bot definition accepts:

| Key | Type | Description |
| --- | ---- | ----------- |
| `name` | string | Bot identifier. |
| `team` | string | Optional team label (e.g. `red`, `blue`). |
| `spawn` | object | Spawn information, supporting either `position` or a `random_positions` array. |
| `initial_state` | object | Initial bot state (`health`, `ammo`, `inventory`, `facing`, `velocity`, etc.). |
| `script` | array | Chronologically ordered commands that drive the bot. |

Commands contain a floating-point `time`, an `action` string, and optional
`params` object. Supported actions include:

- `move`: Adjusts position using a direction vector and optional `speed`.
- `look`: Sets the facing direction.
- `shoot`: Consumes ammo for the supplied `weapon`.
- `item`: Adds an inventory entry or increments counts.
- `damage` / `heal`: Modifies `health`.
- `say`: Stores a message alongside the emitted event.
- `teleport`: Instantly relocates the bot.
- `custom`: Merges arbitrary key/value pairs into the bot's `custom` payload.
- `set_state`: Bulk update of position, velocity, facing, ammo, inventory, and
  other custom fields.
- `wait`: Explicit no-op, useful for readability.

Commands are executed once their `time` is reached (to the current tick). The
harness emits a timeline frame for every tick, containing a snapshot of all bots
and any events triggered at that moment.

### Deterministic randomness

Any field may opt into deterministic randomness by using the `{ "random": ... }`
helper. The following modes are available:

- `choice`: Pick from an `options` array.
- `uniform`: Sample from [`low`, `high`] using `random.uniform`.
- `randint`: Sample an integer between `low` and `high`.
- `normal`: Sample from a normal distribution using `mu` and `sigma`.
- `vector`: Generate a random unit vector (scaled by `length`).

The harness initialises a dedicated RNG with the scenario seed (or the
CLI-provided override). This ensures that repeated runs with the same seed yield
identical timelines, including spawn picks and randomised command parameters.

### Sample scenario

A ready-to-use scenario is provided at
`tools/tests/match_sim/sample_scenario.json`. Running it via

```bash
python -m tools.tests.match_sim tools/tests/match_sim/sample_scenario.json --seed 2024
```

will produce a `frames` array with 101 entries (10 seconds at 10 Hz). Each frame
contains per-bot state snapshots as well as any events that occurred during the
corresponding tick.

## Working with the JSON timeline

The resulting JSON document uses the following structure:

```json
{
  "config": { ... original scenario with resolved seed ... },
  "frames": [
    {
      "tick": 0,
      "time": 0.0,
      "events": [ { "bot": "sarge", "action": "look", ... } ],
      "bots": {
        "sarge": { "position": [ ... ], "health": 125, ... },
        "anarki": { "position": [ ... ], "health": 100, ... }
      }
    },
    { "tick": 1, ... }
  ]
}
```

Consumers can diff timelines between builds to verify deterministic behaviour or
feed the frames into replay tooling to drive visualisations.

## Programmatic usage

The harness can also be driven directly from Python for use in automated tests
or bespoke tooling:

```python
from pathlib import Path

from tools.tests.match_sim import run_from_file

result = run_from_file(Path("tools/tests/match_sim/sample_scenario.json"), seed=2024)
print(result.frames[0].events)
```

The returned `SimulationResult` exposes the original `MatchConfig`, an ordered
list of timeline frames, and helpers such as `write_json()` for exporting the
payload.
