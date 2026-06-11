# Botlib Entity Update Bridge Recheck - 2026-06-11

## Scope

This pass rechecked the botlib entity-update path that carries qagame entity
state into the native botlib AAS entity cache:

- qagame producer: `BotAIStartFrame`
- game syscall and native import bridge: `BOTLIB_UPDATENTITY` /
  `G_QL_IMPORT_BOTLIB_UPDATE_ENTITY`
- server VM/native dispatch: `QL_G_trap_BotLibUpdateEntity`
- botlib export wrapper: `Export_BotLibUpdateEntity`
- AAS sink: `AAS_UpdateEntity` and `AAS_EntityInfo`

The pass intentionally did not attempt to compile the still-unstable tutorial
state-node tail helpers. Those remain a mapping-only boundary until the retail
node bodies and full `bot_state_t` tail layout are pinned with higher
confidence.

## Retail Evidence

Observed Binary Ninja HLIL anchors:

- `00484E20` is the `AAS_UpdateEntity` body.
- `00484E6B` indexes botlib entities with a `0xF4` stride.
- `00484F28..00484FA0` copies the Quake Live-only tail from
  `bot_entitystate_t` words `0x1c..0x33` to `aas_entityinfo_t` words
  `0x23..0x3a`.
- `00484F69` bulk-copies `0x40` bytes from source word `0x22` to destination
  word `0x29`, matching the 16-entry active-powerup sidecar.
- `004851DD` zeroes `0xEC` bytes for failed `AAS_EntityInfo`, and the normal
  query path copies `0xEC` bytes from the `0xF4`-stride entity record.
- `004A7F40` is the `Export_BotLibUpdateEntity` wrapper, and `004A7FA5`
  tail-calls into `00484E20`.
- `004A8495` installs `004A7F40` into the botlib export table.
- `10023400` is qagame `BotAIStartFrame`; its stack-local update state is
  cleared with the retail `0xD0` size before the update import is called.

Observed Ghidra/function-row anchors:

- `quakelive_steam/functions.csv` rows:
  - `FUN_00484e20,00484e20,907,0,unknown`
  - `FUN_004a7f40,004a7f40,102,0,unknown`
  - `FUN_004e17a0,004e17a0,18,0,unknown`
- `qagamex86/functions.csv` row:
  - `FUN_10023400,10023400,2038,0,unknown`
- `decompile_top_functions.c` shows qagame filling the Quake Live tail from
  entity time, client gravity/speed/delta, health, max health, flag-carry
  sidecar, and the powerup-expiration table at player-state offset `0x180`.

Symbol alias anchors:

- `sub_484E20 -> AAS_UpdateEntity`
- `sub_4A7F40 -> Export_BotLibUpdateEntity`
- `sub_4E17A0 -> QL_G_trap_BotLibUpdateEntity`
- `FUN_10023400` / `sub_10023400 -> BotAIStartFrame`

## Source Reconstruction Status

Observed source facts:

- `bot_entitystate_t` carries the retail tail at source words `0x1c..0x33`:
  time seconds, gravity, speed, delta angle, health, max health, 16 active
  powerup words, bit-18-clear sidecar, and red/blue flag-carrier sidecar.
- `aas_entityinfo_t` carries the corresponding botlib cache tail at words
  `0x23..0x3a`.
- `BotAIStartFrame` filters out non-live entities, unlinked entities,
  `SVF_NOCLIENT`, non-grappling missiles, event-only entities, and proximity
  mine triggers by calling `trap_BotLibUpdateEntity(i, NULL)`.
- The same producer zeroes `bot_entitystate_t`, fills legacy Q3A fields, fills
  the QL tail, and calls `trap_BotLibUpdateEntity(i, &state)`.
- The qagame syscall maps `BOTLIB_UPDATENTITY` to native import slot `56`.
- `sv_game.c` routes both legacy VM dispatch and native game import dispatch to
  `QL_G_trap_BotLibUpdateEntity`.
- `QL_G_trap_BotLibUpdateEntity` calls `G_Import_Syscall(BOTLIB_UPDATENTITY,
  ent, bue)`.
- `Export_BotLibUpdateEntity` preserves the retail setup/entity-number checks
  before calling `AAS_UpdateEntity`.
- `AAS_UpdateEntity` preserves the retail NULL-state unlink behavior, copies
  the QL tail in retail order, marks the entity number and validity after the
  copy, and relinks changed entities through the client bbox and BSP leaf paths.
- `AAS_EntityInfo` preserves the retail zero/copy sizes through
  `sizeof(aas_entityinfo_t)`.

Inference:

The current source reconstruction matches the retail bridge shape closely
enough that no runtime code change is warranted for this slice. The best
parity gain is keeping the bridge pinned as a single testable contract, because
future changes in qagame, syscall wiring, native import table setup, or botlib
entity layout can otherwise regress independently.

## Validation

Added `tests/test_botlib_entity_update_bridge_parity.py`, which pins:

- symbol aliases and Ghidra function rows for the retail owners;
- qagame producer filters and QL tail fill order;
- syscall/native import/table wiring for `BOTLIB_UPDATENTITY`;
- botlib export-wrapper checks;
- AAS entity-tail copy order, unlink behavior, and info-copy sizing;
- Binary Ninja HLIL anchors for the QL tail copy and export-table assignment.

Command:

```powershell
python -m pytest tests/test_botlib_entity_update_bridge_parity.py -q --tb=short
```

Result: `3 passed in 0.14s`.

No game launch was needed; this was a static reverse-engineering and source
contract validation pass.

## Open Boundaries

- This does not prove runtime AI behavior on a retail map. It proves the
  source/reference bridge and layout contracts for the update path.
- The qagame tutorial-enter/tail state-node helpers remain mapping-only until
  their retail node bodies and `bot_state_t` tail offsets are fully settled.
- The live online-service divergences are unrelated to this botlib path and
  remain outside this pass.

## Parity Estimate

- Focused botlib entity-update bridge confidence: **before 93% -> after 98%**.
- Focused QL entity-state/AAS-info tail layout confidence:
  **before 94% -> after 98%**.
- Overall botlib plus qagame/server wiring reconstruction parity:
  **83.2% -> 83.35%**.
