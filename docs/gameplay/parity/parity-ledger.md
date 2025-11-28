# Gameplay Parity Ledger

This ledger tracks the implementation status of Quake Live gameplay behaviours relative to the upstream Quake III Arena codebase. It is intended as a quick reference for maintainers and feature owners who need to understand the current coverage and remaining gaps for production readiness. Refer to the [Gameplay Parity Documentation Hub](./README.md) for the latest list of code owners to ping when updating these entries.

> **Owner cross-check:** Validated with Gameplay Systems (@gamedev-lead) and QA Lead (@qa-automation) on 2024-09-22 after the weapon constant port and capture review. Owners should update this note after each review pass.

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

### Weapon balance delta verification (2024-09-22)

- **Before/after snapshot**
  | Aspect | Before (Q3 fallback) | After (Quake Live HLIL) |
  | --- | --- | --- |
  | Reload timings | Unverified Q3 defaults; no parity captures logged. | Gauntlet 400 ms; Machinegun 100 ms; Shotgun 1000 ms; Grenade 800 ms; Rocket 800 ms; Lightning 50 ms; Railgun 1500 ms; Plasma 100 ms; BFG 300 ms; Grapple 100 ms; Heavy MG 75 ms; Nailgun 1000 ms; Prox 800 ms; Chaingun 50 ms.【F:references/hlil/quakelive/qagamex86.dll_split/bg_pmove.md†L1-L22】【F:src/code/game/bg_pmove.c†L133-L149】 |
  | Ammo pickup + max stacks | Unverified Q3 defaults; ammo caps not referenced in the ledger. | Pickup/max pairs now tracked as: Machinegun 50/200, Heavy MG 50/200, Shotgun 10/40, Grenade 5/20, Rocket 5/20, Lightning 60/240, Railgun 10/40, Plasma 30/120, BFG 15/60, Nailgun 20/80, Prox 10/40, Chaingun 100/400, Grapple 0/-1.【F:references/hlil/quakelive/qagamex86.dll_split/bg_pmove.md†L24-L41】【F:src/code/game/bg_misc.c†L28-L63】 |
  | Handicap scalars | Untracked in ledger. | HLIL-aligned pickup/armor/health/respawn multipliers now mirrored in `bg_weaponStats` (e.g., Machinegun 1.0/1.0/0.0/1.0; Lightning 1.0/1.0/0.7289/1.0; Prox Launcher 1.0/0.0/0.486/1.0).【F:src/code/game/bg_misc.c†L28-L42】 |
- **Capture demos:** `artifacts/tests/weapon-balance-deltas.md` documents the rocket, rail, and lightning scrims generated for this pass so QA can replay the parity captures.【F:artifacts/tests/weapon-balance-deltas.md†L1-L9】
- **HLIL reference:** Alignment validated against `references/hlil/quakelive/qagamex86.dll_split/bg_pmove.md` and mirrored in `bg_pmove.c`/`bg_misc.c` defaults for release builds.
- **Owner approval:** Gameplay Systems (@gamedev-lead) and QA Lead (@qa-automation) acknowledged the capture review on 2024-09-22; status promoted to ✅ per the parity plan.

### Race/CTF timer verification (2024-12-09)

- **Evidence:** Replay notes in [`artifacts/tests/race-ctf-timer-verification.md`](../../artifacts/tests/race-ctf-timer-verification.md) capture scoreboard and HUD clocks staying aligned with race splits, CTF overtime rollovers, and sudden-death ticks.
- **Approvals:** HUD Taskforce (@hud-taskforce) and QA Lead (@qa-automation) reviewed the demo timestamps and approved promoting the entry to ✅ after confirming timeout clamping and overtime sequencing matched the captured references.

## UI-Driven Gameplay Flags
| Feature | Status | Source Modules | Reference | Owner |
|---------|--------|----------------|-----------|-------|
| Competitive rulesets (PQL/Classic/Standard) | ⚠️ In Progress | `src/code/game/g_main.c`, `src/code/ui/ui_gameinfo.c` | `references/hlil/quakelive/uix86.dll_split/UI_FeederSelection.md` | Rulesets (@ui-systems) |
| Instagib mutator toggles | ✅ Complete | `src/code/game/g_weapons.c`, `src/code/game/bg_misc.c` | `references/hlil/quakelive/qagamex86.dll_split/FireWeapon.md` | Modes (@mutator-crew) |
| Race/CTF timers | ✅ Complete | `src/code/cgame/cg_scoreboard.c`, `src/code/cgame/cg_event.c`, `src/code/cgame/cg_newdraw.c` | `references/hlil/quakelive/cgamex86.dll_split/CG_DrawScoreboard.md`, `artifacts/tests/race-ctf-timer-verification.md` | HUD (@hud-taskforce) |
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
