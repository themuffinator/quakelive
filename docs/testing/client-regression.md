# Client regression harness

The client regression harness lives under `tools/tests/client_regression/` and
provides a deterministic way to replay recorded snapshots. For each snapshot the
harness executes the client prediction pipeline, derives the resulting
Heads-Up Display (HUD) state, and computes a stable hash. These hashes can be
compared against known baselines to detect behavioural or rendering regressions
introduced by engine changes.

## Snapshot archives

Snapshot captures are stored as JSON documents with the following top-level
keys:

| Key | Type | Description |
| --- | ---- | ----------- |
| `metadata` | object | Optional descriptive information such as the map name or recording build. |
| `snapshots` | array | Chronologically ordered snapshot payloads (see below). |

Each snapshot entry requires the fields listed in the table below. Additional
keys are ignored and preserved in the output payload printed by the CLI.

| Key | Type | Description |
| --- | ---- | ----------- |
| `sequence` | integer | Sequential identifier of the snapshot. |
| `serverTime` | integer | Authoritative server time in milliseconds. |
| `playerState` | object | Authoritative player state (health, armor, weapon, ammo, origin, etc.). |
| `commands` | array | List of client commands applied between this and the previous snapshot. |

The `playerState` block is used to seed and correct the prediction state, while
`commands` influence how the harness advances movement, weapon changes, damage,
and ammo consumption. The synthetic fixture used by the unit tests is available
at `tools/tests/client_regression/sample_snapshots.json` and can be used as a
reference when authoring new captures.

## Running the harness

The harness exposes a simple CLI entry point and can be invoked directly using
Python. The command below replays the bundled sample capture:

```bash
python -m tools.tests.client_regression tools/tests/client_regression/sample_snapshots.json
```

The tool prints one JSON document per line containing the original sequence
number, server time, deterministic HUD payload, and its SHA-256 hash. For
example, the sample capture yields:

```jsonl
{"hash": "db0c582635b0d000b8d8cc623979b0f556776ff168c4baf9717f6f2802632a11", "hud": {"ammo": {"rocket_launcher": 10}, "armor": 50, "health": 125, "position": [0.0, 0.0, 0.0], "weapon": "rocket_launcher"}, "sequence": 1, "serverTime": 1000}
{"hash": "638c3a5679231de7caf143f388431effe769e912152bbd56f75a019ee5ab0e56", "hud": {"ammo": {"rocket_launcher": 9}, "armor": 40, "health": 115, "position": [0.0, 0.0, 0.0], "weapon": "rocket_launcher"}, "sequence": 2, "serverTime": 1016}
{"hash": "fc456828d2c7d69712cee52bec1faa968bf274d60442ca33ef7f412badd2d1de", "hud": {"ammo": {"lightning_gun": 120, "rocket_launcher": 9}, "armor": 45, "health": 120, "position": [2.0, 0.0, 0.0], "weapon": "lightning_gun"}, "sequence": 3, "serverTime": 1032}
```

Use the `--limit` flag to restrict playback to the first *N* snapshots. This is
particularly useful when iterating on large captures.

## Interpreting hashes

Each hash corresponds to the canonical JSON representation of the HUD payload.
Re-running the harness against the same snapshot archive is expected to produce
the exact same hash series. When a change in the client prediction or HUD code
causes an unexpected difference, a simple diff against the previous hash log will
highlight the offending snapshot. Inspect the expanded `hud` payload in the CLI
output to understand which field changed and why. The JSON lines are already in a
canonical ordering, making them suitable for direct comparison with previously
recorded baselines via tools like `diff`.
