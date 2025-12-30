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
and ammo consumption. The repository ships with several pre-recorded captures
that exercise distinct HUD flows:

| Scenario | Path | Highlights |
| --- | --- | --- |
| Baseline | `tools/tests/client_regression/sample_snapshots.json` | Minimal rocket launcher loop used by unit tests. |
| Weapons and items | `tools/tests/client_regression/weapons_and_items_snapshots.json` | Rapid weapon swaps with mixed ammo adjustments. |
| Server correction | `tools/tests/client_regression/server_correction_snapshots.json` | Demonstrates server authoritative overrides mid-run. |
| Resource drain | `tools/tests/client_regression/resource_drain_snapshots.json` | Attrition and recovery across stacked resources. |

Use these archives as templates when capturing additional scenarios; all follow
the canonical format described above.

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

The additional captures follow the same output format. Their reference hashes
are listed below for quick validation:

```jsonl
// weapons_and_items_snapshots.json
{"hash": "50cc3bf0beb765c921b9cc3975cc611356ead31c522ffa9510963d3468ebf28d", "hud": {"ammo": {"machinegun": 70, "rocket_launcher": 5}, "armor": 50, "health": 125, "position": [128.0, -64.0, 32.0], "weapon": "rocket_launcher"}, "sequence": 10, "serverTime": 5000}
{"hash": "d50a4ede5b09d25864802265283488288b5227f8f5fa53e32eba76e3f8224ef3", "hud": {"ammo": {"machinegun": 70, "rocket_launcher": 4}, "armor": 35, "health": 110, "position": [136.0, -60.0, 32.0], "weapon": "rocket_launcher"}, "sequence": 11, "serverTime": 5016}
{"hash": "b0d4bc9d00594d0e65346d309f2cec2733a6d8d80c2801576f836f50378d3af1", "hud": {"ammo": {"lightning_gun": 150, "machinegun": 70, "rocket_launcher": 3}, "armor": 25, "health": 100, "position": [156.0, -44.0, 32.0], "weapon": "lightning_gun"}, "sequence": 12, "serverTime": 5032}
{"hash": "822dc1c14922b22b10010c58e9356d09fc37455599208f1509d5e02cff22db98", "hud": {"ammo": {"lightning_gun": 130, "machinegun": 70, "railgun": 5, "rocket_launcher": 3}, "armor": 50, "health": 120, "position": [160.0, -32.0, 48.0], "weapon": "railgun"}, "sequence": 13, "serverTime": 5048}

// server_correction_snapshots.json
{"hash": "b8f8c3a4ee5da098cb9742ee0ea7d223031a028a501be204cbf04addfeeaa9ea", "hud": {"ammo": {"shotgun": 8}, "armor": 0, "health": 100, "position": [-256.0, 128.0, 64.0], "weapon": "shotgun"}, "sequence": 20, "serverTime": 8000}
{"hash": "88169c344538663fe617fff5f766e93a9861da1c17189a07d14a868205ee1e6d", "hud": {"ammo": {"shotgun": 7}, "armor": 5, "health": 95, "position": [-240.0, 144.0, 64.0], "weapon": "shotgun"}, "sequence": 21, "serverTime": 8016}
{"hash": "e79954ecd8b60788ba3f29caf923f9a305421434975c9649d031db1dbc931357", "hud": {"ammo": {"shotgun": 7}, "armor": 5, "health": 95, "position": [-190.0, 200.0, 80.0], "weapon": "shotgun"}, "sequence": 22, "serverTime": 8032}
{"hash": "eb79d52ca2a24dd508f66a0a538b68b13e2e5e42df845222c7e66cfc8151d9e5", "hud": {"ammo": {"rocket_launcher": 5, "shotgun": 7}, "armor": 75, "health": 130, "position": [-184.0, 208.0, 96.0], "weapon": "rocket_launcher"}, "sequence": 23, "serverTime": 8048}
{"hash": "b03c5b2c6821be17da30c244636ddc65ed2f4d6b5df0004130a9d768ac7e314f", "hud": {"ammo": {"rocket_launcher": 4, "shotgun": 7}, "armor": 60, "health": 90, "position": [-150.0, 240.0, 96.0], "weapon": "rocket_launcher"}, "sequence": 24, "serverTime": 8064}

// resource_drain_snapshots.json
{"hash": "36e4b60a34bf875d6b457ee4db3cd806be8b9efa5208314ba8d0d4d21cd0d630", "hud": {"ammo": {"grenade_launcher": 10, "plasma_gun": 150}, "armor": 100, "health": 200, "position": [320.0, 64.0, 96.0], "weapon": "plasma_gun"}, "sequence": 30, "serverTime": 16000}
{"hash": "dfe4acd3d186ad813f469da5a267c538289a6faa5c0542766bafa69736004101", "hud": {"ammo": {"grenade_launcher": 9, "plasma_gun": 130}, "armor": 80, "health": 160, "position": [324.0, 68.0, 96.0], "weapon": "plasma_gun"}, "sequence": 31, "serverTime": 16016}
{"hash": "503a6129457b9fae4ae216d262037a6e3b559bdbe5b714180164d26af4b59664", "hud": {"ammo": {"grenade_launcher": 9, "plasma_gun": 120}, "armor": 70, "health": 155, "position": [332.0, 74.0, 92.0], "weapon": "grenade_launcher"}, "sequence": 32, "serverTime": 16032}
{"hash": "f50331e421913018229f3c6bbf140f48347162d8a2bac38d24ef00b7d0e1e4eb", "hud": {"ammo": {"grenade_launcher": 7, "plasma_gun": 110, "rocket_launcher": 2}, "armor": 35, "health": 130, "position": [348.0, 90.0, 92.0], "weapon": "grenade_launcher"}, "sequence": 33, "serverTime": 16048}
{"hash": "abcf77c69e98c7792800435c09229ea664e912cde7376742e11ddcb4f614b94c", "hud": {"ammo": {"grenade_launcher": 6, "plasma_gun": 110, "rocket_launcher": 5}, "armor": 90, "health": 180, "position": [360.0, 108.0, 92.0], "weapon": "rocket_launcher"}, "sequence": 34, "serverTime": 16064}
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

In continuous integration the harness aggregates the results under
`artifacts/tests/client_regression/<target>/latest/hud_hashes.json`. The file maps each
scenario name to its metadata and ordered frame payloads, making it easy to
compare archives across builds without having to re-run the harness locally.
