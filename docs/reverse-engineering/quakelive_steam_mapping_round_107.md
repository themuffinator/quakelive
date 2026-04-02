# Quake Live Steam Host Mapping Round 107

## Scope

This round continues directly from
[Round 106](./quakelive_steam_mapping_round_106.md) and closes the retained
UI VM lifecycle seam in `quakelive_steam.exe`, plus the last two stable
advertisement-compatibility wrappers in the native UI import table.

The evidence order for this pass was:

- `src/code/ui/ui_public.h`
- `src/code/client/cl_ui.c`
- `references/hlil/quakelive/quakelive_steam.exe/quakelive_steam.exe_hlil.txt`
- retail disassembly from `assets/quakelive/quakelive_steam.exe`

The existing anchors that made this pass stable were:

- `sub_4F20C0 -> AdvertisementBridge_InitUI`
- `sub_4BEEF0 -> QLUIImport_SetupAdvertCellShader`
- `sub_4BEF00 -> QLUIImport_RefreshAdvertCellShader`
- `sub_4BEF30 -> QLUIImport_ActivateAdvert`
- `sub_4BF5B0 -> QLUIImport_GetCDKey`
- `sub_4BF5C0 -> QLUIImport_SetCDKey`

## UI VM Lifecycle And Retained Command Owners

The first stable block is the retained UI VM lifecycle and the two adjacent UI
helper owners.

Observed local facts:

1. `sub_4BF360` clears the UI keycatcher bit, zeroes the retained UI-started
   flag, conditionally calls the UI VM shutdown thunk, frees the UI VM handle,
   and nulls the retained VM pointers. That is the exact `CL_ShutdownUI`
   owner.
2. `sub_4BF3B0` reads `"vm_ui"`, creates `"ui"` through `sub_4E9FF0`, throws
   `"VM_Create on UI failed"` on failure, accepts API versions `4` and `8`,
   and initializes the VM with the same `cls.state >= CA_AUTHORIZING &&
   cls.state < CA_ACTIVE` gate used by the writable `CL_InitUI` source.
3. `sub_4BF470` returns `0` when the UI VM is absent and otherwise tailcalls
   the retained `UI_HASUNIQUECDKEY` VM entry. Its call sites in
   `sub_4BF4C0`, `sub_4BF530`, and `sub_4CB440` line up with the writable
   `UI_usesUniqueCDKey()` owner.
4. `sub_4BF490` calls the retained UI VM console-command entry with
   `cls.realtime` when the UI VM exists, and the command-dispatch call site at
   `0x004C83CA` matches the writable `UI_GameCommand()` owner exactly.

| Raw symbol | Alias candidate | Basis | Observed role |
| --- | --- | --- | --- |
| `sub_4BF360` (`0x004BF360`) | `CL_ShutdownUI` | Observed + exact source match | Clears retained UI state, calls `UI_SHUTDOWN`, and frees the UI VM. |
| `sub_4BF3B0` (`0x004BF3B0`) | `CL_InitUI` | Observed + exact source match | Creates the UI VM, checks the API version, and runs `UI_INIT`. |
| `sub_4BF470` (`0x004BF470`) | `UI_usesUniqueCDKey` | Observed + exact source match | Returns the retained `UI_HASUNIQUECDKEY` VM result when the UI VM exists. |
| `sub_4BF490` (`0x004BF490`) | `UI_GameCommand` | Observed + exact source match | Forwards console-command ownership checks into the UI VM. |

## Native UI Advertisement Compatibility Stubs

The second stable block is the remaining advertisement-compatibility slice in
the native UI import table.

Observed local facts:

1. HLIL lines up `data_567478` through `data_567494` with the exact
   `UI_QL_IMPORT_SETUP_ADVERT_CELL_SHADER` through
   `UI_QL_IMPORT_GET_CURSOR_POS` order in `ui_public.h` and the writable
   `ql_ui_imports[...] = ...` publisher in `cl_ui.c`.
2. `data_567480` points at raw `.text` address `0x004BEEE0`. Retail
   disassembly resolves that stub as a direct jump to `0x004F20C0`, which is
   already mapped as `AdvertisementBridge_InitUI`. That makes the stable slot
   name `QLUIImport_InitAdvertisementBridge`.
3. `data_56748C` points at `j_sub_4D7980`, and the writable source publishes
   that exact slot as `UI_QL_IMPORT_UNUSED_85 = QL_UI_trap_Unused85`.
   `sub_4D7980` itself is still a shared no-op target, so the stable name
   belongs on the dedicated wrapper, not on the shared callee.

| Raw symbol | Alias candidate | Basis | Observed role |
| --- | --- | --- | --- |
| `sub_4BEEE0` (`0x004BEEE0`) | `QLUIImport_InitAdvertisementBridge` | Observed + import-slot match | Raw native UI import stub that jumps straight to `AdvertisementBridge_InitUI`. |
| `j_sub_4D7980` | `QLUIImport_Unused85` | Observed + import-slot match | Dedicated no-op wrapper for the retained native UI slot 85. |

## New High-Confidence Aliases Added This Round

- `sub_4BEEE0 -> QLUIImport_InitAdvertisementBridge`
- `sub_4BF360 -> CL_ShutdownUI`
- `sub_4BF3B0 -> CL_InitUI`
- `sub_4BF470 -> UI_usesUniqueCDKey`
- `sub_4BF490 -> UI_GameCommand`
- `j_sub_4D7980 -> QLUIImport_Unused85`

## Open Questions

1. `sub_4D7980` remains intentionally unnamed. The direct callee is still a
   shared no-op target for multiple retained slots, including the unresolved
   `UI_QL_IMPORT_UNUSED_83` / update-advert path and the cached-server no-op
   collapse.
2. `sub_4BF340`, `sub_4B03B0`, `sub_4B03C0`, `sub_4B03D0`, and `sub_4B0420`
   now show cross-table reuse between the retained cgame and UI import slabs,
   but I still do not have a source-stable owner name for those shared wrappers.
3. `sub_4B9430`, `sub_4B9940`, `sub_4B81F0`, `sub_4ECDF0`, `sub_4F1290`,
   `sub_4F2900`, and `sub_4F4640` remain the highest-value unresolved client
   and host leftovers outside this seam.

## Verification

I validated the alias artifact directly:

- `references/analysis/quakelive_symbol_aliases.json` parses cleanly through
  `ConvertFrom-Json`
- recount after this pass: `1124` raw alias entries, `1123` address-backed
  alias entries

## Completion Stats After Round 107

- Ghidra baseline: `5473` functions, `351` imports, `2` exports, `4377`
  analysis symbols
- Current mapping coverage: `1124` raw alias entries, `1123` address-backed
  aliases
- Address-backed coverage: `20.519%` of `5473` functions
- Alias delta this round: `6`
- Estimated parity for this round: `94% -> 94%`

This was a mapping-only pass. It closes the retained UI VM lifecycle seam and
the last two clean advertisement compatibility wrappers, but it does not change
the writable-source parity estimate by itself.
