# Quake Live Steam Host Mapping Round 275

## Scope

- Continued the client-host mapping pass around the native cgame bridge in
  `quakelive_steam.exe`.
- Focused on the `data_565958` cgame import slab, cgame VM load/init/render
  owners, the first-snapshot/server-time helpers, and the browser comm-notice
  helper reached by native cgame serverinfo refresh.

## Evidence

- `references/reverse-engineering/ghidra/quakelive_steam/metadata.txt`
  reports `5473` functions, `351` imports, `2` exports, and `4377` analysis
  symbols for the retail client host.
- `references/reverse-engineering/ghidra/quakelive_steam/functions.csv`
  confirms address-backed rows for the promoted owners:
  - `FUN_004b03b0`, `FUN_004b03c0`, `FUN_004b03d0`
  - `FUN_004b0460`, `FUN_004b04c0`, `FUN_004b0610`,
    `FUN_004b0630`, `FUN_004b0660`, `FUN_004b0760`
  - `FUN_004bf5d0`, `FUN_004ec6d0`, plus the already-promoted
    `FUN_004f2950`
- `references/hlil/quakelive/quakelive_steam.exe/quakelive_steam.exe_hlil.txt`
  provides the host-side control flow:
  - `0x004B03B0` tailcalls `sub_4BF5D0`.
  - `0x004B03C0` and `0x004B03D0` jump through renderer bridge pointers
    `data_146CCE8` and `data_146CCEC`.
  - `0x004B0460` creates the cgame VM for startup cvar registration through
    `VM_Create("cgame", &data_146CC38, &data_565958, &apiVersion)`.
  - `0x004B04C0` is the full `CL_InitCGame` owner: it closes the console,
    builds `maps/%s.bsp`, creates the cgame VM, hides the browser, calls the
    cgame init export, pumps the screen/update loop, and prints
    `CL_InitCGame: %5.2f seconds`.
  - `0x004B0610` dispatches the cgame console-command export at
    `data_146CC38 + 0x0C`.
  - `0x004B0630` dispatches the cgame active-frame export at
    `data_146CC38 + 0x10` with client server time, stereo frame, and demo flag.
  - `0x004B0660` is the `CL_SetCGameTime` delta-adjust helper with the retail
    reset/fast/smoothing branches and `timescale` guard.
  - `0x004B0760` is the first-snapshot transition: it skips pure demo playback,
    sets the active client state, seeds the server-time delta, executes
    `activeAction`, and returns through the retail no-op userinfo reservation.
  - `0x004BF5D0` builds a message object, writes `MSG_TYPE`, tokenizes the
    supplied info string with `Info_NextPair`, serializes the object, and calls
    `0x004EC6D0`.
  - `0x004EC6D0` is a tail thunk to the already-promoted
    `QLWebView_InvokeCommNotice` at `0x004F2950`.
- `references/hlil/quakelive/cgamex86.dll/cgamex86.dll_hlil.txt` provides
  caller-side confirmation:
  - native cgame calls import offset `0x1D0` with the literal
    `"serverinfo"` and the current serverinfo string.
  - native cgame calls import offsets `0x1E0` and `0x1E4` for the mirror point
    and mirror vector helpers.
- `src/code/cgame/cg_public.h` matches the relevant offset math:
  - slot `116` is the tagged-info-string lane currently retained under the
    compatibility name `CG_QL_IMPORT_TAGGED_CVAR_STRING_BUFFER`.
  - slots `120` and `121` are `CG_QL_IMPORT_R_MIRROR_POINT` and
    `CG_QL_IMPORT_R_MIRROR_VECTOR`.

## Promoted Aliases

Updated `references/analysis/quakelive_symbol_aliases.json`:

| Address | Alias | Confidence | Evidence |
| --- | --- | --- | --- |
| `sub_4B03B0` | `QLCGImport_PublishTaggedInfoString` | High | Native import slot 116 tailcalls the tagged info-string publisher. |
| `sub_4B03C0` | `QLCGImport_R_MirrorPoint` | High | Native import slot 120 jumps through the renderer mirror-point pointer. |
| `sub_4B03D0` | `QLCGImport_R_MirrorVector` | High | Native import slot 121 jumps through the renderer mirror-vector pointer. |
| `sub_4B0460` | `CL_LoadCGameForCvarRegistration` | High | Startup-only cgame VM load with API version check before cvar registration. |
| `sub_4B04C0` | `CL_InitCGame` | High | Full map/cgame init body and retail print string. |
| `sub_4B0610` | `CL_GameCommand` | High | cgame console-command export dispatch at `+0x0C`. |
| `sub_4B0630` | `CL_CGameRendering` | High | cgame active-frame export dispatch at `+0x10`. |
| `sub_4B0660` | `CL_AdjustServerTimeDelta` | High | Called only from `CL_SetCGameTime` when the server-time-delta adjustment latch is active. |
| `sub_4B0760` | `CL_FirstSnapshot` | High | Active-state transition, server-time seeding, and `activeAction` execution. |
| `sub_4BF5D0` | `QLWebView_PublishTaggedInfoString` | High | Builds the `MSG_TYPE` plus info-pair payload and forwards it to comm notice. |
| `sub_4EC6D0` | `QLWebView_InvokeCommNoticeThunk` | High | Direct tail thunk to `sub_4F2950` / `QLWebView_InvokeCommNotice`. |

## Source Notes

- No runtime source behavior was changed in this round.
- The source-side slot 116 naming still uses
  `CG_QL_IMPORT_TAGGED_CVAR_STRING_BUFFER` and
  `QL_CG_trap_TaggedCvarStringBuffer` for compatibility. Retail HLIL shows
  the host function publishes a tagged info string to the browser comm-notice
  path rather than reading a cvar string into a caller buffer. Because current
  source cgame does not call this helper, this pass records the corrected
  symbol ownership without changing the fallback browser shim behavior.
- The already-reconstructed mirror-point and mirror-vector source wiring in
  `src/code/client/cl_cgame.c` is now backed by direct retail offset evidence.

## Still Open

- `sub_4B00C0` remains an import-table gap at slot `80`; adjacent renderer
  slots identify its neighborhood, but this pass did not recover a stable
  source name.
- `sub_4B0350`, raw `0x004B0360`, and `sub_4B0370` remain open native cgame
  utility slots. Source enum names suggest the two advertisement bridge slots
  at `114` and `115`, but the committed HLIL still leaves their exact host-side
  helper names weaker than the aliases promoted above.
- `sub_4B0A50` remains a small import-table integrity check rather than a
  promoted public owner.

## Guardrail

- Added
  `tests/test_engine_client_command_parity.py::test_client_cgame_native_bridge_mapping_round_275_promotes_hlil_backed_symbols`.
- The guard checks:
  - promoted aliases in `quakelive_symbol_aliases.json`;
  - matching Ghidra function rows;
  - host HLIL snippets for the cgame VM, render, timing, first-snapshot, and
    comm-notice owners;
  - cgame HLIL call offsets `0x1D0`, `0x1E0`, and `0x1E4`;
  - source-side import slot wiring for slots `116`, `120`, and `121`.

## Parity Estimate

- Before: client/cgame native bridge symbol confidence was high but still had
  several address-backed owners sitting outside the alias ledger, about `92%`
  for this focused lane.
- After: the cgame VM, render, timing, first-snapshot, mirror, and tagged
  info-string/browser notice owners are explicitly mapped and guarded, about
  `96%` for this focused lane.
- Overall strict Windows replacement parity remains `100%`; repo-wide parity
  remains `98%`. This pass improves evidence freshness and symbol precision
  rather than closing a new runtime gap.
