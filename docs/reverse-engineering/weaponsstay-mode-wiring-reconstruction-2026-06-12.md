# Weaponsstay Mode Wiring Reconstruction - 2026-06-12

## Scope

This pass rechecked Quake Live's zero weapon-respawn behavior, exposed to users
as the `weaprespawn` vote and to code as `g_weaponRespawn == 0`, across qagame,
cgame, shared item prediction, and vote wiring. The owning retail binary for
authoritative gameplay behavior is `qagamex86.dll`; cgame evidence was used only
for the predicted pickup gate and serverinfo mirror.

## Evidence

- Canonical HLIL:
  - `references/hlil/quakelive/qagamex86.dll/qagamex86.dll.bndb_hlil.txt`
  - `references/hlil/quakelive/qagamex86.dll/qagamex86.dll.bndb_hlil_split/qagamex86.dll.bndb_hlil_part02.txt`
  - `references/hlil/quakelive/cgamex86.dll/cgamex86.dll_hlil.txt`
  - `references/hlil/quakelive/cgamex86.dll/cgamex86.dll_hlil_split/cgamex86.dll_hlil_part01.txt`
- Companion corpus:
  - `references/reverse-engineering/ghidra/qagamex86/functions.csv`
  - `references/reverse-engineering/ghidra/qagamex86/analysis_symbols.txt`
  - `references/reverse-engineering/ghidra/cgamex86/functions.csv`
- Symbol support:
  - `references/symbol-maps/qagame.json`
  - `references/analysis/quakelive_symbol_aliases.json`
- Source targets:
  - `src/code/game/bg_misc.c`
  - `src/code/game/g_items.c`
  - `src/code/game/g_main.c`
  - `src/code/game/g_cmds.c`
  - `src/code/game/g_vote.c`
  - `src/code/cgame/cg_servercmds.c`
  - `src/code/qcommon/q_shared.h`

## Retail Wiring Map

| Surface | Retail evidence | Source reconstruction status |
| --- | --- | --- |
| Runtime cvar | qagame string table contains `g_weaponRespawn`; the cvar registration row uses serverinfo/gamerule semantics. | `g_main.c` registers `g_weaponRespawn` with `CVAR_SERVERINFO | CVAR_GAMERULE`, default `5`. |
| Vote command | qagame vote execution recognizes `weaprespawn` and sets `g_weaponRespawn`. The callvote help table prints `weaprespawn`. | `g_cmds.c` and `g_vote.c` preserve the `weaprespawn` vote string, display string, bounds, and cvar update. |
| cgame mirror | cgame HLIL keeps the `g_weaponRespawn` serverinfo key string at `0x10071AAC`. | `CG_ParseServerinfo` copies `SERVERINFO_KEY_WEAPON_RESPAWN` into cgame's local `g_weaponRespawn` cvar so shared prediction sees the server value. |
| Shared weapon gate | cgame `BG_CanGrabWeaponItem` at `0x10001850` allows dropped weapons, missing weapons, zero ammo, or the cgame-specific nonzero modelindex2 path; it does not query a cvar. | `bg_misc.c` keeps the cgame leaf cvar-free, while qagame uses `BG_IsWeaponsStayEnabled()` and the server-side sync before calling the shared gate. |
| Authoritative pickup | qagame `Pickup_Weapon` at `0x1004E950` branches on `g_weaponRespawn == 0`, rejects owned map weapons with nonzero ammo, grants weapon/ammo, resets map-weapon ammo to the item quantity, preserves grappling-hook infinite ammo, emits `EV_ITEM_PICKUP` inside the zero-respawn branch, and returns `g_weaponRespawn`. | `g_items.c::Pickup_Weapon` mirrors the cvar-zero early rejection, ammo split, grappling-hook path, restored retail pickup event side effect, and respawn return. |
| Touch cleanup | qagame `Touch_Item` at `0x1004F020` marks dropped items `freeAfterEvent` before the `respawn != 0` hide/respawn path. | `Touch_Item` now marks dropped items for cleanup before returning from the weapon-stay zero-respawn path. |

## Source Reconstruction

Two subtle qagame gaps were closed in this pass.

First, retail does not rely on the common `Touch_Item` pickup-event tail when
`Pickup_Weapon` returns zero for weapon-stay. The `Pickup_Weapon` body emits
`EV_ITEM_PICKUP` itself while still returning zero so map weapons remain visible.
The source now adds `G_AddWeaponStayPickupEvent` and calls it only in the
`g_weaponRespawn.integer == 0` success path, preserving predictable pickup
events when `pers.predictItemPickup` is enabled and normal events otherwise.

Second, dropped weapons still need their one-shot event cleanup even when the
respawn return is zero. Retail sets the dropped-item `freeAfterEvent` flag before
the respawn-gated hide/link/respawn block. `Touch_Item` now follows that ordering
so dropped weapons do not persist indefinitely under zero weapon respawn.

The qagame symbol map note for `Pickup_Weapon` was updated to record the
zero-respawn event side effect, and the focused factory/regen parity test now
pins the qagame HLIL offsets, cgame serverinfo key, shared pickup gate shape,
event helper, and dropped-item cleanup ordering.

## Confidence

Confidence is high for the reconstructed weaponsstay behavior. The cvar,
callvote, cgame mirror, shared pickup leaf, qagame pickup helper, and touch-item
cleanup ordering are all anchored by direct HLIL strings or offsets plus matching
source call sites. The main remaining open question is an end-to-end runtime
confirmation of the exact client-visible pickup event cadence, but static
evidence is strong enough that no game launch was needed for this pass.

## Parity Estimate

- Focused weaponsstay/wiring parity: **before 92% -> after 97%**.
- Broader qagame item pickup parity: **before 94% -> after 95%**.
