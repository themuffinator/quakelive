# Quake Live Steam Host Mapping Round 106

## Scope

This round continues directly from
[Round 105](./quakelive_steam_mapping_round_105.md) and closes a large retained
native-UI import slab in `quakelive_steam.exe`, plus two adjacent
`cl_main.c` owners that now clear the source-match bar.

The evidence order for this pass was:

- `src/code/ui/ui_public.h`
- `src/code/client/cl_ui.c`
- `references/hlil/quakelive/quakelive_steam.exe/quakelive_steam.exe_hlil.txt`
- retail disassembly from `assets/quakelive/quakelive_steam.exe`
- writable terminology in `src/code/client/cl_main.c`

The existing anchors that made this pass stable were:

- `sub_4B0270 -> QLUIImport_PC_LoadSource`
- `sub_4B0290 -> QLUIImport_PC_FreeSource`
- `sub_4B02B0 -> QLUIImport_PC_ReadToken`
- `sub_4B02D0 -> QLUIImport_PC_SourceFileAndLine`
- `sub_4B0340 -> QLUIImport_SetCursorPos`
- `sub_4BEF20 -> QLUIImport_GetCursorPos`
- `sub_4BEE50 -> Key_KeynumToStringBuf`
- `sub_4BEE80 -> Key_GetBindingBuf`
- `sub_4BA760 -> CL_ServerStatus`
- `sub_4BAE10 -> CL_GetPingQueueCount`
- `sub_4BACB0 -> CL_GetPing`
- `sub_4BADB0 -> CL_GetPingInfo`
- `sub_4BADF0 -> CL_ClearPing`
- `sub_4BAE60 -> CL_UpdateVisiblePings_f`

From those anchors, the retained `data_5673d8` through `data_56747c` slab in
HLIL lines up directly with the native UI import order in
`ui_public.h::uiQlImport_t` and the writable `ql_ui_imports[...] = ...`
publisher in `cl_ui.c`.

## UI Key, State, And Clipboard Imports

The first stable block is the retained UI import surface around key state,
clipboard access, client state, and configstring reads.

Observed local facts:

1. `data_5673d0` through `data_5673f8` matches the exact retail/native UI
   order in `ui_public.h`: key binding, overstrike helpers, key clear/catcher,
   clipboard, client state, glconfig, and configstring.
2. `sub_4BEFC0` is a thin wrapper to `sub_4B6C10`, which is already mapped as
   `Key_SetBinding`; in the UI native table that slot is
   `UI_QL_IMPORT_KEY_SETBINDING`.
3. `j_sub_4B6AF0` is the matching wrapper for
   `UI_QL_IMPORT_KEY_GETOVERSTRIKEMODE`.
4. `sub_4BEFF0` is the matching wrapper for
   `UI_QL_IMPORT_KEY_SETOVERSTRIKEMODE`. Binary Ninja HLIL currently mislabels
   the tailcall, but retail PE disassembly shows a direct jump to
   `0x004B6B00`, the retained `Key_SetOverstrikeMode` owner.
5. `j_sub_4B80E0` is the matching `UI_QL_IMPORT_KEY_CLEARSTATES` wrapper.
6. `sub_4BF010` returns the `cls.keyCatchers` field directly, which is the
   exact `UI_QL_IMPORT_KEY_GETCATCHER` role.
7. `sub_4BF020`, `sub_4BF060`, and `sub_4BF090` match the writable source
   helpers `CL_UI_GetClipboardData`, `GetClientState`, and `GetConfigString`
   respectively, but in this slab the stable owner names are the native import
   roles.

| Raw symbol | Alias candidate | Basis | Observed role |
| --- | --- | --- | --- |
| `sub_4BEFC0` (`0x004BEFC0`) | `QLUIImport_Key_SetBinding` | Observed + import-slot match | Native UI wrapper for `Key_SetBinding`. |
| `j_sub_4B6AF0` | `QLUIImport_Key_GetOverstrikeMode` | Observed + import-slot match | Native UI wrapper for `Key_GetOverstrikeMode`. |
| `sub_4BEFF0` (`0x004BEFF0`) | `QLUIImport_Key_SetOverstrikeMode` | Observed + import-slot match | Native UI wrapper for `Key_SetOverstrikeMode`; raw disassembly resolves the true jump target. |
| `j_sub_4B80E0` | `QLUIImport_Key_ClearStates` | Observed + import-slot match | Native UI wrapper for `Key_ClearStates`. |
| `sub_4BF010` (`0x004BF010`) | `QLUIImport_Key_GetCatcher` | Observed + import-slot match | Returns the retained key-catcher field for native UI. |
| `sub_4BF020` (`0x004BF020`) | `QLUIImport_GetClipboardData` | Observed + import-slot match | Native UI clipboard bridge. |
| `sub_4BF060` (`0x004BF060`) | `QLUIImport_GetClientState` | Observed + import-slot match | Publishes `uiClientState_t` to native UI. |
| `sub_4BF090` (`0x004BF090`) | `QLUIImport_GetConfigString` | Observed + import-slot match | Bounds-checked native UI configstring accessor. |

## UI LAN And Browser Imports

The next stable block is the native UI LAN browser slab.

Observed local facts:

1. `data_5673fc` through `data_567444` matches the contiguous LAN/browser slice
   in `ui_public.h`, and `cl_ui.c` publishes the same order with
   `QL_UI_trap_LAN_*` assignments.
2. `sub_4BF0E0` switches across the four retained browser sources and returns
   the exact server counts, which matches `LAN_GetServerCount`.
3. `sub_4BF130`, `sub_4BF150`, and `sub_4BF170` forward directly into the
   retained browser helpers that expose address strings, info strings, and
   ping values for one browser row.
4. `j_sub_4BAE10`, `sub_4BF1B0`, `sub_4BF1C0`, `sub_4BF1D0`, `sub_4BF190`,
   and `sub_4BF210` tailcall already-mapped `CL_*` browser owners:
   `CL_GetPingQueueCount`, `CL_ClearPing`, `CL_GetPing`, `CL_GetPingInfo`,
   `CL_ServerStatus`, and `CL_UpdateVisiblePings_f`.
5. `sub_4BF1A0`, `sub_4BF1E0`, `sub_4BF200`, `sub_4BF220`, `sub_4BF240`, and
   `sub_4BF260` are the retained native wrappers for reset/visibility/add/
   remove/compare browser operations.
6. `j_sub_4C92A0` is the direct native UI wrapper for `Hunk_MemoryRemaining`.

| Raw symbol | Alias candidate | Basis | Observed role |
| --- | --- | --- | --- |
| `sub_4BF0E0` (`0x004BF0E0`) | `QLUIImport_LAN_GetServerCount` | Observed + import-slot match | Returns the retained server count for one UI browser source. |
| `sub_4BF130` (`0x004BF130`) | `QLUIImport_LAN_GetServerAddressString` | Observed + import-slot match | Native UI wrapper for one browser row address string. |
| `sub_4BF150` (`0x004BF150`) | `QLUIImport_LAN_GetServerInfo` | Observed + import-slot match | Native UI wrapper for one browser row info string. |
| `sub_4BF170` (`0x004BF170`) | `QLUIImport_LAN_GetServerPing` | Observed + import-slot match | Native UI wrapper for one browser row ping. |
| `j_sub_4BAE10` | `QLUIImport_LAN_GetPingQueueCount` | Observed + import-slot match | Native UI wrapper for `CL_GetPingQueueCount`. |
| `sub_4BF1B0` (`0x004BF1B0`) | `QLUIImport_LAN_ClearPing` | Observed + import-slot match | Native UI wrapper for `CL_ClearPing`. |
| `sub_4BF1C0` (`0x004BF1C0`) | `QLUIImport_LAN_GetPing` | Observed + import-slot match | Native UI wrapper for `CL_GetPing`. |
| `sub_4BF1D0` (`0x004BF1D0`) | `QLUIImport_LAN_GetPingInfo` | Observed + import-slot match | Native UI wrapper for `CL_GetPingInfo`. |
| `sub_4BF1E0` (`0x004BF1E0`) | `QLUIImport_LAN_MarkServerVisible` | Observed + import-slot match | Native UI visibility marker for browser rows. |
| `sub_4BF200` (`0x004BF200`) | `QLUIImport_LAN_ServerIsVisible` | Observed + import-slot match | Native UI visibility query for browser rows. |
| `sub_4BF210` (`0x004BF210`) | `QLUIImport_LAN_UpdateVisiblePings` | Observed + import-slot match | Native UI wrapper for `CL_UpdateVisiblePings_f`. |
| `sub_4BF220` (`0x004BF220`) | `QLUIImport_LAN_AddServer` | Observed + import-slot match | Native UI wrapper for adding a retained browser row. |
| `sub_4BF240` (`0x004BF240`) | `QLUIImport_LAN_RemoveServer` | Observed + import-slot match | Native UI wrapper for removing a retained browser row. |
| `sub_4BF1A0` (`0x004BF1A0`) | `QLUIImport_LAN_ResetPings` | Observed + import-slot match | Native UI wrapper for resetting retained browser ping state. |
| `sub_4BF190` (`0x004BF190`) | `QLUIImport_LAN_ServerStatus` | Observed + import-slot match | Native UI wrapper for `CL_ServerStatus`. |
| `sub_4BF260` (`0x004BF260`) | `QLUIImport_LAN_CompareServers` | Observed + import-slot match | Native UI wrapper for retained server sorting/comparison. |
| `j_sub_4C92A0` | `QLUIImport_MemoryRemaining` | Observed + import-slot match | Native UI wrapper for `Hunk_MemoryRemaining`. |

## UI CD-Key, Cinematic, And Adjacent Client Owners

The last stable block is the UI CD-key/cinematic seam plus two adjacent
`cl_main.c` owners.

Observed local facts:

1. `sub_4BF290` prints `"UI_CIN_PlayCinematic\n"` and tailcalls
   `CIN_PlayCinematic`, which is the exact native UI import role at slot 73.
2. `sub_4BF5B0` and `sub_4BF5C0` are the retained native UI wrappers for the
   CD-key get/set slab immediately before the verified-cdkey import.
3. `sub_4BF2D0` occupies the exact `UI_QL_IMPORT_VERIFY_CDKEY` slot in the
   retained native table and tailcalls `sub_4BB1B0`. The current retail
   implementation is still the legacy 16-character validator, so the stable
   name here is the import role, not the wider source-side
   `CL_CDKeyValidate` owner.
4. `sub_4BB1B0` is the exact `CL_CDKeyValidateLegacyValue` owner: it checks for
   a 16-character key, an optional 2-character checksum, uppercases letters,
   rejects characters outside the classic Quake III allowlist, accumulates the
   byte sum, formats `"%02x"`, and compares the checksum when provided.
5. `sub_4B9450` is now a clean `CL_DisconnectPacket` match. The HLIL body
   checks `cls.state < CA_AUTHORIZING`, rejects mismatched server addresses,
   ignores packets received within 3000 ms of the last live packet, and then
   drops with `"Server disconnected for unknown reason"`, which matches the
   writable source exactly.

| Raw symbol | Alias candidate | Basis | Observed role |
| --- | --- | --- | --- |
| `sub_4BF290` (`0x004BF290`) | `QLUIImport_CIN_PlayCinematic` | Observed + import-slot match | Native UI cinematic-play wrapper. |
| `sub_4BF5B0` (`0x004BF5B0`) | `QLUIImport_GetCDKey` | Observed + import-slot match | Native UI CD-key getter wrapper. |
| `sub_4BF5C0` (`0x004BF5C0`) | `QLUIImport_SetCDKey` | Observed + import-slot match | Native UI CD-key setter wrapper. |
| `sub_4BF2D0` (`0x004BF2D0`) | `QLUIImport_VerifyCDKey` | Observed + import-slot match | Native UI verify-cdkey wrapper; retail currently tailcalls the legacy validator. |
| `sub_4BB1B0` (`0x004BB1B0`) | `CL_CDKeyValidateLegacyValue` | Observed + exact source match | Validates a retained legacy Quake III CD key plus optional 2-byte checksum. |
| `sub_4B9450` (`0x004B9450`) | `CL_DisconnectPacket` | Observed + exact source match | Drops a stale server connection after validating source address and timeout window. |

## New High-Confidence Aliases Added This Round

- native UI key/state helpers:
  - `sub_4BEFC0`
  - `j_sub_4B6AF0`
  - `sub_4BEFF0`
  - `j_sub_4B80E0`
  - `sub_4BF010`
  - `sub_4BF020`
  - `sub_4BF060`
  - `sub_4BF090`
- native UI LAN/browser helpers:
  - `sub_4BF0E0`
  - `sub_4BF130`
  - `sub_4BF150`
  - `sub_4BF170`
  - `j_sub_4BAE10`
  - `sub_4BF1B0`
  - `sub_4BF1C0`
  - `sub_4BF1D0`
  - `sub_4BF1E0`
  - `sub_4BF200`
  - `sub_4BF210`
  - `sub_4BF220`
  - `sub_4BF240`
  - `sub_4BF1A0`
  - `sub_4BF190`
  - `sub_4BF260`
  - `j_sub_4C92A0`
- native UI CD-key/cinematic helpers:
  - `sub_4BF290`
  - `sub_4BF5B0`
  - `sub_4BF5C0`
  - `sub_4BF2D0`
- adjacent `cl_main.c` owners:
  - `sub_4BB1B0`
  - `sub_4B9450`

## Open Questions

1. `data_56741c` and `data_567420` still collapse onto the same pure no-op
   `sub_4D7980`, so I did not force a single alias for the paired
   `QLUIImport_LAN_LoadCachedServers` / `QLUIImport_LAN_SaveCachedServers`
   slots.
2. `data_567480` still points at a raw jump stub (`0x004BEEE0`) without a
   committed function symbol in the reference corpus, so I left the
   `QLUIImport_InitAdvertisementBridge` slot unmapped for now.
3. `sub_4B9430`, `sub_4B9940`, `sub_4B81F0`, `sub_4ECDF0`, `sub_4F1290`,
   `sub_4F2900`, and `sub_4F4640` remain the highest-value unresolved leftovers
   across the recent client and host passes.

## Verification

I validated the alias artifact directly:

- `references/analysis/quakelive_symbol_aliases.json` parses cleanly through
  `ConvertFrom-Json`
- recount after this pass: `1118` raw alias entries, `1117` address-backed
  alias entries

## Completion Stats After Round 106

- Ghidra baseline: `5473` functions, `351` imports, `2` exports, `4377`
  analysis symbols
- Current mapping coverage: `1118` raw alias entries, `1117` address-backed
  aliases
- Address-backed coverage: `20.409%` of `5473` functions
- Alias delta this round: `31`
- Estimated parity for this round: `94% -> 94%`

This was a mapping-only pass. It closes most of the retained native UI LAN /
CD-key import slab and the adjacent dropped-connection / legacy-CD-key owners,
but it does not change the writable-source parity estimate by itself.
