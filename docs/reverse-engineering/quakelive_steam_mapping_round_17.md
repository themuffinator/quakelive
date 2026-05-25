# Quake Live Steam Host Mapping Round 17

## Scope

This round closes the remaining straightforward native `cgamex86.dll` state/query import seam in `quakelive_steam.exe`.

The unresolved cluster from the last pass was the host slab at `data_565A9C..data_565AC8`. A fresh correlation pass through the retail `cgamex86.dll` HLIL, the host HLIL, and the local `cl_cgame.c` / `ql_cgame_imports.inc` reconstruction now pins that band as:

- the renderer model/tag query callbacks behind native cgame player-model layout work
- the core `GetGlconfig` / `GetGameState` / snapshot / server-command getters
- the `GetCurrentCmdNumber` / `GetUserCmd` pair
- the retail `SetUserCmdValue` host shim
- the `MemoryRemaining` import and its exact host-side hunk helper

The primary local evidence for this round is:

- `references/hlil/quakelive/quakelive_steam.exe/quakelive_steam.exe_hlil.txt`
- `references/hlil/quakelive/cgamex86.dll/cgamex86.dll_hlil.txt`
- `src/code/client/cl_cgame.c`
- `src/code/client/ql_cgame_imports.inc`
- `src/code/qcommon/common.c`

## Native Cgame Import Slab At `0x144..0x170`

The owning host slab is now stable enough to document directly.

Observed local facts:

1. The host cgame import slab resolves:
   - `data_565A9C = sub_4BEF90`
   - `data_565AA0 = sub_4B00D0`
   - `data_565AA8 = sub_4BF070`
   - `data_565AAC = sub_4B0110`
   - `data_565AB0 = sub_4B0130`
   - `data_565AB4 = sub_4B0150`
   - `data_565AB8 = sub_4B0160`
   - `data_565ABC = sub_4B0170`
   - `data_565AC0 = sub_4B0180`
   - `data_565AC4 = sub_4B01E0`
   - `data_565AC8 = sub_4B0210`
2. Retail `cgamex86.dll` calls those offsets with stable signatures:
   - `+0x144` as `(model, mins, maxs)`
   - `+0x148` as `(tagOut, model, startFrame, endFrame, frac, "tag_*")`
   - `+0x150` as a single pointer during startup
   - `+0x154` as a single `gameState_t*`
   - `+0x158` as two out-pointers
   - `+0x15C` as `(snapshotNumber, snapshotOut)`
   - `+0x160` as `(serverCommandNumber)`
   - `+0x164` as a no-arg integer getter
   - `+0x168` as `(cmdNumber, usercmdOut)`
   - `+0x16C` once per frame with two integers, one float, and one trailing integer
   - `+0x170` as a no-arg integer getter compared against `0x3D0900`
3. `ql_cgame_imports.inc` still exposes the matching native wrappers for:
   - `QL_CG_trap_R_ModelBounds`
   - `QL_CG_trap_R_LerpTag`
   - `QL_CG_trap_GetGlconfig`
   - `QL_CG_trap_GetGameState`
   - `QL_CG_trap_GetCurrentSnapshotNumber`
   - `QL_CG_trap_GetSnapshot`
   - `QL_CG_trap_GetServerCommand`
   - `QL_CG_trap_GetCurrentCmdNumber`
   - `QL_CG_trap_GetUserCmd`
   - `QL_CG_trap_SetUserCmdValue`
   - `QL_CG_trap_MemoryRemaining`

That is enough to treat this slab as a coherent native cgame import cluster rather than a leftover advertisement seam.

## Imports `0x144` And `0x148`: Renderer Model Queries

The first two unresolved entries are now exact.

### `sub_4BEF90`

Observed local facts:

1. `sub_4BEF90` is a pure jump through `data_146CCC4`.
2. Retail cgame player-model sizing paths call `(*(data_1074CCCC + 0x144))(modelHandle, &mins, &maxs)`.
3. `ql_cgame_imports.inc` exposes `QL_CG_trap_R_ModelBounds( clipHandle_t model, vec3_t mins, vec3_t maxs )`.

That call shape is exact for the native `R_ModelBounds` import wrapper.

### `sub_4B00D0`

Observed local facts:

1. `sub_4B00D0` forwards six arguments through `data_146CCC0`, preserving one float.
2. Retail cgame model assembly calls `(*(data_1074CCCC + 0x148))(&tag, model, startFrame, endFrame, 1.0f, "tag_torso")` and the same form for `"tag_head"`.
3. `ql_cgame_imports.inc` exposes `QL_CG_trap_R_LerpTag( orientation_t *tag, clipHandle_t mod, int startFrame, int endFrame, float frac, const char *tagName )`.

That makes `sub_4B00D0` the native `R_LerpTag` wrapper.

## Imports `0x150..0x170`: Core Cgame State And Command Queries

The remaining slab entries line up tightly with the standard cgame host query cluster.

### `sub_4BF070`

Observed local facts:

1. `sub_4BF070` copies `0x2C58` bytes from `0x15EB714` into the caller buffer.
2. Retail cgame startup calls `(*(data_1074CCCC + 0x150))(0x10A3D2A4)` before using the resulting display metrics.
3. `ql_cgame_imports.inc` exposes `QL_CG_trap_GetGlconfig( glconfig_t *glconfig )`.

This is the native `GetGlconfig` wrapper.

### `sub_4B0110`

Observed local facts:

1. `sub_4B0110` copies `0x4E84` bytes from `data_146CFD4` into the destination.
2. Retail cgame startup calls `(*(data_1074CCCC + 0x154))(&data_10A38420)`.
3. The copied block is the same host gamestate/configstring backing store also used by the local configstring helpers.

This is the native `GetGameState` wrapper.

### `sub_4B0130`

Observed local facts:

1. `sub_4B0130` writes `data_146CD30` and `data_146CD2C` through two out-pointers.
2. `sub_4AF570` later treats `data_146CD30` as the current snapshot message number.
3. Retail cgame calls `(*(data_1074CCCC + 0x158))(&snapshotNumber, &serverTime)`.

This is the native `GetCurrentSnapshotNumber` wrapper.

### `sub_4B0150`

Observed local facts:

1. `sub_4B0150` is a pure tailcall to `sub_4AF570`.
2. `sub_4AF570` matches `CL_GetSnapshot`: it bounds against the current message number, checks the packet ring age, validates the snapshot slot, copies the playerstate/areamask/entity list, and truncates to `0x180` entities with the `CL_GetSnapshot: truncated %i entities to %i` message.
3. Retail cgame calls `(*(data_1074CCCC + 0x15C))(snapshotNumber, snapshotOut)`.
4. The 2026-05-25 snapshot playerState transport re-audit keeps that import
   path source-pinned: `CL_ParseSnapshot` reads areamask, `MSG_ReadDeltaPlayerstate`,
   and packet entities before accepting the frame, stores valid frames in the
   client snapshot ring, derives ping from `cl.snap.ps.commandTime`, and
   `CL_GetSnapshot` copies the playerState into the cgame-visible snapshot that
   `trap_GetSnapshot` retrieves.

This is the native `GetSnapshot` wrapper.

### `sub_4B0160`

Observed local facts:

1. `sub_4B0160` is a pure tailcall to `sub_4AF820`.
2. `sub_4AF820` matches `CL_GetServerCommand`, including the exact error strings for cycled-out and not-yet-received reliable commands.
3. Retail cgame drains server commands through `(*(data_1074CCCC + 0x160))(i + 1, snapshotOrCgPtr)`.

This is the native `GetServerCommand` wrapper.

### `sub_4B0170` And `sub_4B0180`

Observed local facts:

1. `sub_4B0170` returns `data_14725D0`.
2. `sub_4B0180` bounds the requested command number against the same `data_14725D0`, rejects commands older than `0x40`, and copies `0x1C` bytes from a circular buffer at `data_1471ED0`.
3. Retail cgame prediction paths call `(*(data_1074CCCC + 0x168))((*(data_1074CCCC + 0x164))(), &cmd)` and nearby `cmdNum - 0x3F` variants.

That pair matches the native `GetCurrentCmdNumber` / `GetUserCmd` import pair exactly.

### `sub_4B01E0`

Observed local facts:

1. `sub_4B01E0` stores three integers into `data_1471EC0`, `data_1471EC4`, and `data_1471EC8`, plus one float into `data_1471ECC`.
2. Retail cgame calls `(*(data_1074CCCC + 0x16C))(data_10A9C7A0, data_10A9C7A4, float(data_10A9C9A4), data_10A9C9A8)` once per active frame.
3. The import position and frame-time ownership match the `SetUserCmdValue` seam, but retail Quake Live clearly carries a wider host signature than the GPL two-argument form.

This is best named as the native `SetUserCmdValue` wrapper, with the explicit note that the retail signature is extended.

### `sub_4B0210` And `sub_4C92A0`

Observed local facts:

1. `sub_4B0210` is a pure tailcall to `sub_4C92A0`.
2. `sub_4C92A0` returns `data_11FF9C4 - max(data_1205DFC, data_1205E00) - max(data_1205DE8, data_1205DEC)`.
3. `common.c` implements `Hunk_MemoryRemaining` as `s_hunkTotal - ( max(low.permanent, low.temp) + max(high.permanent, high.temp) )`.
4. Retail cgame compares `(*(data_1074CCCC + 0x170))()` against `0x3D0900` in the deferred-model-loading path, which matches the `trap_MemoryRemaining() < 4000000` logic in the local cgame source.

This closes both the native import wrapper and its exact host-side hunk helper.

## Promoted Aliases

| Raw symbol | Alias candidate | Basis | Observed role |
| --- | --- | --- | --- |
| `sub_4BEF90` (`0x004BEF90`) | `QLCGImport_R_ModelBounds` | Observed | Native cgame import wrapper for renderer model bounds queries. |
| `sub_4B00D0` (`0x004B00D0`) | `QLCGImport_R_LerpTag` | Observed | Native cgame import wrapper for renderer tag interpolation. |
| `sub_4BF070` (`0x004BF070`) | `QLCGImport_GetGlconfig` | Observed | Native cgame import wrapper that copies the host `glconfig_t` block. |
| `sub_4B0110` (`0x004B0110`) | `QLCGImport_GetGameState` | Observed | Native cgame import wrapper that copies the host gamestate/configstring block. |
| `sub_4B0130` (`0x004B0130`) | `QLCGImport_GetCurrentSnapshotNumber` | Observed | Native cgame import wrapper for `(snapshotNumber, serverTime)`. |
| `sub_4B0150` (`0x004B0150`) | `QLCGImport_GetSnapshot` | Observed | Native cgame import wrapper for snapshot retrieval. |
| `sub_4B0160` (`0x004B0160`) | `QLCGImport_GetServerCommand` | Observed | Native cgame import wrapper for reliable server-command retrieval. |
| `sub_4B0170` (`0x004B0170`) | `QLCGImport_GetCurrentCmdNumber` | Observed | Native cgame import wrapper returning the latest generated usercmd number. |
| `sub_4B0180` (`0x004B0180`) | `QLCGImport_GetUserCmd` | Observed | Native cgame import wrapper copying one `usercmd_t` from the host circular buffer. |
| `sub_4B01E0` (`0x004B01E0`) | `QLCGImport_SetUserCmdValue` | Observed plus bounded inference | Native cgame import wrapper for the retail extended `SetUserCmdValue` path. |
| `sub_4B0210` (`0x004B0210`) | `QLCGImport_MemoryRemaining` | Observed | Native cgame import wrapper over the host hunk-memory query. |
| `sub_4C92A0` (`0x004C92A0`) | `Hunk_MemoryRemaining` | Observed | Exact host-side hunk-memory remaining helper used by the cgame import wrapper. |

## Open Questions

1. Import `0x14C` (`sub_4B0100`) remains intentionally unnamed. It sits between the now-identified `R_LerpTag` and `GetGlconfig` entries, but I do not yet have a stable retail cgame callsite proving its ownership.
2. The next cgame slab entries after `0x170` still need a separate pass, especially the `0x174+` band that feeds the local callback table built in `sub_10029210`.
3. `QLCGImport_SetUserCmdValue` is now stable at the name level, but its four-field retail payload should be compared against the Binary Ninja HLIL and reconstructed client state before promoting field names for the stored globals.
