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

### Seeding practices

Always declare an explicit `seed` in your scenario JSON and override it via the
`--seed` CLI flag (or the `seed=` argument in `run_from_file()`) when you need to
reproduce a specific timeline. The harness resolves the effective seed in this
order:

1. CLI / function override
2. Scenario `seed`
3. Deterministic fallback (`1337`)

The resolved value is written back to the exported configuration so archived
timelines capture exactly which seed produced the output. Pick memorable seeds
for common workflows (e.g. `2024` in CI) so differences are easy to cross
reference across runs.

### Bundled scenarios

Three ready-to-use scenarios ship alongside the harness and are exercised by the
test suite as well as CI artefact generation:

| Slug | File | Description | Suggested seed | Frames | Duration (s) |
| ---- | ---- | ----------- | -------------- | ------ | ------------- |
| `duel` | `tools/tests/match_sim/sample_scenario.json` | Baseline two-bot duel showcasing movement, combat, and randomised dodges. | `2024` | 101 | 10.0 |
| `overtime` | `tools/tests/match_sim/overtime_scenario.json` | Sudden-death duel that flips into overtime with scripted scoreboard metadata. | `3141` | 126 | 12.5 |
| `loadouts` | `tools/tests/match_sim/complex_loadouts.json` | Free-for-all stress test with stacked inventories, heavy ammo usage, and randomised loadouts. | `9001` | 161 | 8.0 |
| `factory` | `tools/tests/match_sim/factory_cvars.json` | Factory CVar coverage exercising loadout toggles, spawn delays, and item drop rules. | `4242` | 161 | 8.0 |

Run any scenario via:

```bash
python -m tools.tests.match_sim tools/tests/match_sim/overtime_scenario.json --seed 3141 \
  --output build/match-timelines/overtime.json
```

Each command materialises a `frames` array whose length matches the values in the
table above (frames = duration × tick rate + 1). The CLI writes the resulting
timeline to the provided output path or prints it to stdout when omitted.

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
