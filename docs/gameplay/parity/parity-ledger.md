# Gameplay Parity Ledger

This ledger tracks the implementation status of Quake Live gameplay behaviours relative to the upstream Quake III Arena codebase. It is intended as a quick reference for maintainers and feature owners who need to understand the current coverage and remaining gaps for production readiness. Refer to the [Gameplay Parity Documentation Hub](./README.md) for the latest list of code owners to ping when updating these entries.

> **Owner cross-check:** Validated with Gameplay Systems (@gamedev-lead) and QA Lead (@qa-automation) on 2024-11-09 after refreshing weapon capture seeds and the deterministic timing harness. Owners should update this note after each review pass.

## Legend
- **Status**
  - ✅ *Complete* – Behaviour is fully validated against Quake Live references.
  - ⚠️ *In Progress* – Work is partially merged; follow up with the listed owner before shipping changes.
  - ❌ *Not Started* – No active implementation exists in `src/`.
- **Reference** – HLIL or asset material that was used to port or validate the behaviour.
- **Owner** – Primary code owner that should be consulted before modifying the feature.

## Core Systems
| Feature | Status | Source Modules | Reference | Owner |
|---------|--------|----------------|-----------|-------|
| Weapon balance deltas (damage, refire, ammo) | ✅ Complete | `src/code/game/bg_pmove.c`, `src/code/game/bg_misc.c` | `references/hlil/quakelive/qagamex86.dll_split/bg_pmove.md` | Gameplay Systems (@gamedev-lead) |
| Loadout unlock rules | ❌ Not Started | `src/code/game/g_items.c` | `references/hlil/quakelive/qagamex86.dll_split/g_items.md` | Progression (@live-ops) |
| Physics adjustments (air control, stair smoothing) | ✅ Complete | `src/code/game/bg_pmove.c` | `references/hlil/quakelive/qagamex86.dll_split/PmoveSingle_*.md` | Movement (@physics-guild) |
| Domination capture volumes & metadata entities | ✅ Complete | `src/code/game/g_trigger.c`, `src/code/game/g_team.c` | `references/hlil/quakelive/qagamex86.dll/qagamex86.dll.bndb_hlil_split/qagamex86.dll.bndb_hlil_part01.txt†L39210-L39410` | Modes (@mutator-crew) |
| Matchmaking skill scaling hooks | ❌ Not Started | `src/code/game/g_active.c`, `src/code/game/g_client.c` | `references/hlil/quakelive/qagamex86.dll_split/g_active.md` | Backend Integrations (@services-team) |

### Weapon balance delta verification (2024-11-09 refresh)

- **Before/after snapshot**
  | Aspect | Before (2024-09-22 ledger) | After (2024-11-09 refresh) |
  | --- | --- | --- |
  | Reload timings | HLIL-aligned reloads documented with 2024-09-22 captures. | Reload timings unchanged: Gauntlet 400 ms; Machinegun 100 ms; Shotgun 1000 ms; Grenade 800 ms; Rocket 800 ms; Lightning 50 ms; Railgun 1500 ms; Plasma 100 ms; BFG 300 ms; Grapple 100 ms; Heavy MG 75 ms; Nailgun 1000 ms; Prox 800 ms; Chaingun 50 ms.【F:references/hlil/quakelive/qagamex86.dll_split/bg_pmove.md†L1-L22】【F:src/code/game/bg_pmove.c†L133-L149】 |
  | Ammo pickup + max stacks | HLIL-aligned pickup/max stacks documented with 2024-09-22 captures. | Pickup/max stacks unchanged: Machinegun 50/200, Heavy MG 50/200, Shotgun 10/40, Grenade 5/20, Rocket 5/20, Lightning 60/240, Railgun 10/40, Plasma 30/120, BFG 15/60, Nailgun 20/80, Prox 10/40, Chaingun 100/400, Grapple 0/-1.【F:references/hlil/quakelive/qagamex86.dll_split/bg_pmove.md†L24-L41】【F:src/code/game/bg_misc.c†L28-L63】 |
  | Handicap scalars | HLIL-aligned pickup/armor/health/respawn multipliers mirrored in `bg_weaponStats`. | Scalars unchanged; captured alongside ammo stacks for traceability.【F:src/code/game/bg_misc.c†L28-L42】 |
- **Deterministic harness baseline:** `tests/run_harnesses.py` now emits `weapon_baselines/<target>/weapon_baselines.json` during the CI matrix runs so reload/refire/ammo pickups are archived with the other deterministic artefacts.【F:tests/run_harnesses.py†L37-L121】【F:tests/run_harnesses.py†L210-L269】
- **Capture demos:** `artifacts/tests/weapon-balance-deltas.md` lists the refreshed rocket, rail, and lightning scrims with commands/seeds for reproduction.【F:artifacts/tests/weapon-balance-deltas.md†L1-L10】
- **HLIL reference:** Alignment remains anchored to `references/hlil/quakelive/qagamex86.dll_split/bg_pmove.md` and the mirrored defaults in `bg_pmove.c`/`bg_misc.c`.
- **Owner approval:** Gameplay Systems (@gamedev-lead) and QA Lead (@qa-automation) approved the refreshed captures and harness baseline publication on 2024-11-09; status remains ✅ per the parity plan.

## UI-Driven Gameplay Flags
| Feature | Status | Source Modules | Reference | Owner |
|---------|--------|----------------|-----------|-------|
| Competitive rulesets (PQL/Classic/Standard) | ⚠️ In Progress | `src/code/game/g_main.c`, `src/code/ui/ui_gameinfo.c` | `references/hlil/quakelive/uix86.dll_split/UI_FeederSelection.md` | Rulesets (@ui-systems) |
| Instagib mutator toggles | ✅ Complete | `src/code/game/g_weapons.c`, `src/code/game/bg_misc.c` | `references/hlil/quakelive/qagamex86.dll_split/FireWeapon.md` | Modes (@mutator-crew) |
| Race/CTF timers | ❌ Not Started | `src/code/cgame/cg_scoreboard.c`, `src/code/cgame/cg_event.c` | `references/hlil/quakelive/cgamex86.dll_split/CG_DrawScoreboard.md` | HUD (@hud-taskforce) |
| Item timer/training HUD overrides | ⚠️ In Progress | `docs/gameplay/cvars.md`, `src/game/tests/cosmetics_fixtures.c` | `references/hlil/quakelive/qagamex86.dll/qagamex86.dll.bndb_hlil_split/qagamex86.dll.bndb_hlil_part03.txt†L1100-L1138` | Coaching UX (@hud-taskforce) |

## Entity Targets

- **`target_remove_keys`** – Drops any carried key items from the activator, clearing the bitmask used by scripted door logic. Map authors do not need any additional keys: the helper simply inspects the activator’s inventory when triggered. 【F:src/code/game/g_target.c†L94-L138】
- **`target_cvar`** – Accepts `cvar`/`value` pairs (or numbered variants such as `cvar1`/`value1`) and applies up to eight server cvar updates in one go. Values fall back to the legacy `cvarValue` keys so existing map sources remain compatible, and every trigger automatically refreshes the cached match factory config so sudden-death and timeout CVars remain in sync. 【F:src/code/game/g_target.c†L172-L274】
- **`target_achievement`** – Emits achievement IDs (from `achievement`/`award` keys) to the triggering player so backend listeners or HUD scripts can raise notifications. Multiple IDs are allowed per entity, letting a single trigger report a bundle of awards. 【F:src/code/game/g_target.c†L466-L535】

## Validation Checklist
- [ ] Confirm new ports against the linked HLIL snippets prior to merging.
- [ ] Update the ledger when new gameplay deltas are documented or shipped.
- [ ] Notify the release manager if a ⚠️ item is promoted to ✅ so the change can be tracked in release notes.

## Domination Mapping Entities
- **`team_dom_point`** – Point entity that names each control point via `targetname`, optional `message` label, and an optional `target` string that should reference nearby `info_player_deathmatch` spawn pads. The game now records the metadata, chains the referenced spawn nodes, and exposes the data through `Team_RegisterDominationPoint` so announcer, scoring, and distress logic can reason about individual capture points.
- **`trigger_capturezone`** – Brush trigger that must `target` the desired `team_dom_point`. When occupied the volume feeds Domination scoring through `Team_RegisterDominationTrigger` and `Team_DominationPointTouch`, enabling the capture timers, contention rules, and periodic score ticks introduced in Quake Live.

## Contacts
- **Primary Maintainer:** @gamedev-lead
- **Escalation:** @technical-director
