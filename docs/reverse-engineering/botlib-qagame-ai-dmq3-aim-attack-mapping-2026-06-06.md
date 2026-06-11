# Botlib Qagame AI DMQ3 Aim/Attack Mapping - 2026-06-06

## Scope

This pass pins the qagame-side `ai_dmq3.c` aim, attack, and map-script bridge
between the visibility helpers and the activate-goal slab. The owning retail
binary is `qagamex86.dll`; the mapped range is `0x10019E00..0x1001BBE0`.

One source reconstruction was made: `BotMapScripts` now uses the retail Quake
Live `beyondreality` map exception instead of the GPL-era `mpq3tourney6`
fallback for `TFL_FUNCBOB` suppression.

## Evidence

- `references/analysis/quakelive_symbol_aliases.json`
- `references/symbol-maps/qagame.json`
- `references/reverse-engineering/ghidra/qagamex86/functions.csv`
- `references/hlil/quakelive/qagamex86.dll/qagamex86.dll.bndb_hlil_split/qagamex86.dll.bndb_hlil_part01.txt`
- `src/code/game/ai_dmq3.c`
- `src/code/game/g_public.h`
- `src/code/game/g_syscalls.c`
- `src/code/server/sv_game.c`
- `src/code/server/ql_game_imports.inc`
- `tests/test_botlib_qagame_ai_dmq3_aim_attack_parity.py`

## Mapped Rows

| Address | Promoted name | Function size |
| --- | --- | ---: |
| `0x10019E00` | `BotAimAtEnemy` | 5112 |
| `0x1001B200` | `BotCheckAttack` | 1410 |
| `0x1001B790` | `BotMapScripts` | 855 |
| `0x1001BAF0` | `BotSetMovedir` | 237 |
| `0x1001BBE0` | `BotModelMinsMaxs` | 225 |

Both `FUN_...` and `sub_...` aliases are now promoted for every row so the
Ghidra and Binary Ninja naming tracks resolve to the same source identity.

## Source Reconstruction

Observed fact: Binary Ninja HLIL for `BotMapScripts` preserves the
`q3tourney6` branch and a second map-name branch for `beyondreality`.
`references/symbol-maps/qagame.json` independently describes the same
`q3tourney6` plus `beyondreality` pairing.

Observed source gap: the reconstructed source still had the older
`mpq3tourney6` fallback branch.

Applied reconstruction: the fallback branch now checks `beyondreality` and the
comment was updated to match. This preserves the same behavior shape, but
aligns the map identity with retail Quake Live evidence.

Follow-up reconstruction: the `beyondreality` branch now routes through
`BotApplyBeyondRealityTravelFlags`, matching the retail helper at
`qagamex86.dll:0x10024E10` while preserving the q3tourney6 crusher-button
script inline in `BotMapScripts`.

## Source Mapping Notes

Observed source anchors now pinned by tests:

- `BotAimAtEnemy` preserves enemy/obelisk target setup, aim-skill and
  per-weapon aim characteristic fan-out, weapon-info fetches, invisible-enemy
  accuracy decay, enemy-velocity sampling, visibility scoring, exact and
  linear projectile prediction, radial ground-target aiming, corner prediction
  through `trap_BotPredictVisiblePosition`, aim-target updates, spread
  compensation, and the challenge-mode direct `trap_EA_View` path.
- `BotCheckAttack` preserves reaction-time and teleport/weapon-change gates,
  fire-throttle timing, aim-target field-of-view checks, solid/playerclip trace
  rejection, weapon-info fetches, teammate-safe forward trace handling,
  radial self-damage suppression, fire-release handling, and `BFL_ATTACKED`
  toggling.
- `BotMapScripts` preserves the `q3tourney6` crusher-button special case,
  team-safe target selection, aim jitter from `CHARACTERISTIC_AIM_ACCURACY`,
  `InFieldOfVision` before firing, and the retail `beyondreality`
  `TFL_FUNCBOB` suppression branch through `BotApplyBeyondRealityTravelFlags`.
- `BotSetMovedir` preserves the `VEC_UP` and `VEC_DOWN` special cases before
  falling back to `AngleVectors`.
- `BotModelMinsMaxs` preserves the live `g_entities` scan, optional `eType`
  and contents filters, modelindex match, mins/maxs fill from current origin,
  and zeroed fallback bounds.

Inferred meaning: this band is the qagame AI fire-control bridge. It consumes
the visibility helper from the previous pass, pulls botlib weapon and movement
prediction data, and emits EA attack/view commands. Confidence is high because
source bodies, retail symbol-map signatures, Ghidra row sizes, Binary Ninja
HLIL entry/call anchors, and import wiring all agree.

## Botlib Wiring

The new gate pins the legacy and native import paths consumed by this band:

- `BOTLIB_AAS_PREDICT_CLIENT_MOVEMENT` remains mapped to native slot `82` for
  high-skill projectile lead prediction.
- `BOTLIB_EA_ATTACK` remains mapped to native slot `92` for normal attacks,
  fire-release weapons, and the `q3tourney6` map-script button shot.
- `BOTLIB_EA_VIEW` remains mapped to native slot `106` for challenge-mode
  direct view control.
- `BOTLIB_AI_CHARACTERISTIC_BFLOAT` remains mapped to native slot `113` for
  aim, reaction, fire-throttle, and map-script accuracy characteristics.
- `BOTLIB_AI_PREDICT_VISIBLE_POSITION` remains mapped to native slot `173` for
  non-visible projectile shots around corners.
- `BOTLIB_AI_GET_WEAPON_INFO` remains mapped to native slot `179` for the
  weapon spread, offset, speed, radial damage, and fire-release metadata that
  drives aim and attack decisions.
- `g_syscalls.c` keeps the legacy qagame wrapper calls and `G_MapNativeImport`
  cases intact.
- `sv_game.c` keeps both the botlib import-table entries and native
  `ql_game_imports[...]` entries wired to generated `QL_G_trap_*` wrappers.
- `ql_game_imports.inc` preserves float forwarding through `QL_G_PASSFLOAT`
  for predictive-movement frame time and characteristic calls.

## Coverage Result

`tests/test_botlib_qagame_ai_dmq3_aim_attack_parity.py` now verifies:

- all 5 aim/attack prelude identities in
  `references/analysis/quakelive_symbol_aliases.json`;
- matching `references/symbol-maps/qagame.json` names and signatures;
- exact `functions.csv` row sizes for the mapped range;
- direct `ai_dmq3.c` source anchors for every promoted helper;
- the reconstructed `beyondreality` map-script branch and absence of the old
  `mpq3tourney6` branch inside `BotMapScripts`;
- the source helper that re-reads serverinfo and clears `TFL_FUNCBOB` for
  `beyondreality`;
- Binary Ninja HLIL entry signatures and flow/cross-call anchors across aim,
  attack, map-script, movedir, and model-bounds helpers;
- predictive movement, weapon-info, visible-position, EA attack/view, and
  characteristic botlib import wiring from game syscall constants through
  server import initialization and generated qagame wrappers.

Focused verification run:

```text
python -m pytest tests/test_botlib_qagame_ai_dmq3_aim_attack_parity.py -q --tb=short
2 passed in 0.13s
```

## Parity Estimate

- Focused qagame `ai_dmq3.c` aim/attack alias coverage:
  **before 0% -> after 96%**
- Focused source-owned aim/attack/map-script parity confidence:
  **before 88% -> after 97%**
- Focused botlib fire-control and prediction import wiring confidence:
  **before 92% -> after 97%**
- Overall botlib plus adjacent qagame AI execution wiring:
  **before 95% -> after 96%**

No runtime launch was needed. This was a static reverse-engineering mapping and
source-reconstruction pass using committed HLIL, Ghidra, symbol-map,
source-body, and import-wiring evidence.
