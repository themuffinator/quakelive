# Quake Live Steam Host Mapping Round 108

## Scope

This round continues directly from
[Round 107](./quakelive_steam_mapping_round_107.md) and closes the retained
config-write / CD-key persistence seam in `quakelive_steam.exe`, plus the
adjacent frame-timing clamp owner in `common.c`.

The evidence order for this pass was:

- `src/code/qcommon/common.c`
- `src/code/client/cl_ui.c`
- `references/hlil/quakelive/quakelive_steam.exe/quakelive_steam.exe_hlil.txt`
- retail disassembly from `assets/quakelive/quakelive_steam.exe`

The existing anchors that made this pass stable were:

- `sub_4BB1B0 -> CL_CDKeyValidateLegacyValue`
- `sub_4BF470 -> UI_usesUniqueCDKey`
- `sub_4BF5B0 -> QLUIImport_GetCDKey`
- `sub_4BF5C0 -> QLUIImport_SetCDKey`
- `sub_4C81D0 -> Cmd_AddCommand`
- `sub_4CF320 -> FS_FCloseFile`
- `sub_4CF3E0 -> FS_FOpenFileWrite`
- `sub_4D00F0 -> FS_Write`
- `sub_4D01D0 -> FS_Printf`

## Config Write And Persistence Owners

The first stable block is the retained config-write and credential-persistence
path in `common.c`.

Observed local facts:

1. `sub_4CB2B0` builds `"%s/q3key"`, truncates the incoming value to `0x11`
   bytes, validates it through the retained `CL_CDKeyValidateLegacyValue`
   owner, writes the first `0x10` bytes to disk, and appends the stock
   generated-by warnings before closing the file. That is the retained
   `Com_WriteCDKey` owner, even though Steam still keeps the legacy 16-byte
   write path instead of the current credential-file implementation.
2. `sub_4CB370` opens one mandatory output file plus one optional replicate
   file, writes the Quake Live `// Hardware cfg` and `// Replicate cfg`
   headers, then emits bindings and archived variables through the same owner
   cluster used by the writable `Com_WriteConfigToFile`. The retail helper has
   a wider Quake Live signature, but the owning source role is still
   `Com_WriteConfigToFile`.
3. `sub_4CB440` checks the retained fully-initialized flag plus the archive
   dirty bit, clears that bit, writes `qzconfig.cfg` and `repconfig.cfg` when
   not dedicated, then chooses the base or mod CD-key placeholder through
   `UI_usesUniqueCDKey()` and `fs_game` before tailcalling `sub_4CB2B0`. That
   is the retained `Com_WriteConfiguration` owner with Quake Live filename
   divergence.
4. `sub_4CB4D0` is registered under the exact `"writeconfig"` command,
   validates `Cmd_Argc() == 2 || Cmd_Argc() == 3`, appends `.cfg`, prints the
   expected `Writing %s.\n` / hardware-plus-replica messages, and then writes
   the requested config output. The single-file path is partly inlined, but
   the owner is still clearly `Com_WriteConfig_f`.

| Raw symbol | Alias candidate | Basis | Observed role |
| --- | --- | --- | --- |
| `sub_4CB2B0` (`0x004CB2B0`) | `Com_WriteCDKey` | Observed + retained owner match | Validates and writes the retained legacy `q3key` file plus warning trailer. |
| `sub_4CB370` (`0x004CB370`) | `Com_WriteConfigToFile` | Observed + retained owner match | Writes the Quake Live hardware config and optional replicate config output. |
| `sub_4CB440` (`0x004CB440`) | `Com_WriteConfiguration` | Observed + retained owner match | Flushes archived config changes and writes the retained CD-key placeholder file. |
| `sub_4CB4D0` (`0x004CB4D0`) | `Com_WriteConfig_f` | Observed + exact command-owner match | Console command that writes one or two retained config outputs. |

## UI CD-Key Helper Owners

The second stable block is the retained native UI CD-key helper pair behind
the already-mapped `QLUIImport_GetCDKey` / `QLUIImport_SetCDKey` wrappers.

Observed local facts:

1. `sub_4BF5B0` and `sub_4BF5C0` remain thin wrappers that tailcall
   `sub_4BF4C0` and `sub_4BF530`, exactly matching the writable
   `ql_ui_imports[UI_QL_IMPORT_GET_CDKEY]` and
   `ql_ui_imports[UI_QL_IMPORT_SET_CDKEY]` publication in `cl_ui.c`.
2. `sub_4BF4C0` selects between the base and mod path through
   `UI_usesUniqueCDKey()` plus `fs_game`, then copies either a `16`-space or
   `32`-space placeholder into the caller buffer. Steam retail no longer
   exposes the writable credential strings here, but this is still the
   retained `CLUI_GetCDKey` owner.
3. `sub_4BF530` uses the same gate, copies incoming bytes into the retained
   `16`- or `32`-byte storage slot, and sets the archive dirty flag so
   `Com_WriteConfiguration` will flush later. That preserves the writable
   `CLUI_SetCDKey` owner role even though the retail storage contents differ
   from the current source.

| Raw symbol | Alias candidate | Basis | Observed role |
| --- | --- | --- | --- |
| `sub_4BF4C0` (`0x004BF4C0`) | `CLUI_GetCDKey` | Observed + retained owner match | Native UI helper behind `UI_GET_CDKEY`; returns the retained placeholder CD-key buffer. |
| `sub_4BF530` (`0x004BF530`) | `CLUI_SetCDKey` | Observed + retained owner match | Native UI helper behind `UI_SET_CDKEY`; updates retained placeholder storage and marks config dirty. |

## Frame-Timing Clamp Owner

The last stable owner in this pass is the adjacent frame-timing clamp helper.

Observed local facts:

1. `sub_4CB710` applies `com_fixedtime`, otherwise multiplies by
   `com_timescale` or `com_cameraMode`.
2. It enforces the `msec >= 1` floor only when timescaling is active.
3. It prints the exact retained `Hitch warning: %i msec frame time\n` when
   dedicated frame time exceeds `500`.
4. It clamps to `5000` for dedicated or remote-client paths and to `200` for
   local-server play before returning the final frame time.

That is an exact retained `Com_ModifyMsec` match.

| Raw symbol | Alias candidate | Basis | Observed role |
| --- | --- | --- | --- |
| `sub_4CB710` (`0x004CB710`) | `Com_ModifyMsec` | Observed + exact source match | Applies timescale/fixedtime rules and the stock frame-time clamps. |

## New High-Confidence Aliases Added This Round

- `sub_4BF4C0 -> CLUI_GetCDKey`
- `sub_4BF530 -> CLUI_SetCDKey`
- `sub_4CB2B0 -> Com_WriteCDKey`
- `sub_4CB370 -> Com_WriteConfigToFile`
- `sub_4CB440 -> Com_WriteConfiguration`
- `sub_4CB4D0 -> Com_WriteConfig_f`
- `sub_4CB710 -> Com_ModifyMsec`

## Open Questions

1. `sub_4CB630` is still intentionally unnamed. The retail command string
   `"writeClientConfig"` is clear, but I do not yet have a writable owner
   name in the repo to promote with the same confidence as the stock
   `Com_WriteConfig_f` path.
2. `sub_4B9430`, `sub_4B9940`, `sub_4B81F0`, `sub_4ECDF0`, `sub_4F1290`,
   `sub_4F2900`, and `sub_4F4640` remain the highest-value unresolved client
   and host leftovers outside this seam.

## Verification

I validated the alias artifact directly:

- `references/analysis/quakelive_symbol_aliases.json` parses cleanly through
  `ConvertFrom-Json`
- recount after this pass: `1131` raw alias entries, `1130` address-backed
  alias entries

## Completion Stats After Round 108

- Ghidra baseline: `5473` functions, `351` imports, `2` exports, `4377`
  analysis symbols
- Current mapping coverage: `1131` raw alias entries, `1130` address-backed
  aliases
- Address-backed coverage: `20.647%` of `5473` functions
- Alias delta this round: `7`
- Estimated parity for this round: `94% -> 94%`

This was a mapping-only pass. It closes the retained config persistence seam
and the adjacent frame-timing owner, but it does not change the writable-source
parity estimate by itself.
