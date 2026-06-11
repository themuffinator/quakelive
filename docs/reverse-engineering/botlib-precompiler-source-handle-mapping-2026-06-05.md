# Botlib Precompiler Source Handle Mapping - 2026-06-05

## Scope

This pass selects `src/code/botlib/l_precomp.c` public source-handle wrappers
as the next botlib slice after the structure/character/weight parser corridor.
The slice owns the small API surface that qagame and related VM/native callers
use to load a precompiler source, read tokens, free handles, and report source
file/line information.

No runtime launch was needed. The committed Binary Ninja HLIL exposes the
retail wrapper bodies directly, and the Ghidra `functions.csv` rows corroborate
the function sizes and addresses.

## Owning Retail Binary

Owning binary:

- `assets/quakelive/quakelive_steam.exe`

Reference corpus used:

- `references/hlil/quakelive/quakelive_steam.exe/quakelive_steam.exe_hlil_split/quakelive_steam.exe_hlil_part03.txt`
- `references/hlil/quakelive/quakelive_steam.exe/quakelive_steam.exe_hlil_split/quakelive_steam.exe_hlil_part04.txt`
- `references/reverse-engineering/ghidra/quakelive_steam/functions.csv`
- `references/analysis/quakelive_symbol_aliases.json`
- `src/code/botlib/l_precomp.c`
- `src/code/botlib/be_interface.c`
- `src/code/game/botlib.h`
- `src/code/game/g_public.h`
- `src/code/game/g_syscalls.c`
- `src/code/server/sv_game.c`
- `src/code/server/ql_game_imports.inc`
- `src/code/client/cl_cgame.c`
- `src/code/client/ql_cgame_imports.inc`
- `src/code/cgame/cg_public.h`
- `src/code/cgame/cg_syscalls.c`
- `src/code/cgame/cg_main.c`

## Why This Slice

This is the next useful botlib slice because it is the public token-handle API
that sits immediately above the resource parsers already mapped:

- item, weapon, projectile, character, and weight resources all depend on the
  same precompiler/source machinery
- `PC_ReadTokenHandle` converts internal `token_t` data into exported
  `pc_token_t`
- qagame exposes the PC handle calls through legacy VM syscalls and the retained
  compatibility import table
- shutdown uses `PC_CheckOpenSourceHandles` as the leak detector after parser
  teardown

## Retail Evidence

Observed facts:

- Alias map promotions cover:
  - `sub_4AC260 -> PC_LoadSourceHandle`
  - `sub_4AC350 -> PC_FreeSourceHandle`
  - `sub_4AC390 -> PC_SourceFileAndLine`
  - `sub_4AC400 -> PC_SetBaseFolder`
  - `sub_4AC410 -> PC_CheckOpenSourceHandles`
  - `sub_4ACB10 -> PC_ReadTokenHandle`
- Ghidra `functions.csv` lists the same functions as unknown bodies with sizes:
  `230`, `59`, `100`, `9`, `48`, and `163` bytes respectively.
- Retail HLIL for `0x004AC260` scans `sourceFiles` style storage from handle
  `1` up to `0x3f`, resets the script base folder, constructs a source object,
  and stores it in the selected slot.
- Retail HLIL for `0x004AC350` validates `handle - 1 <= 0x3e`, frees the
  source, clears the slot, and returns `1`.
- Retail HLIL for `0x004AC390` validates the same handle range, copies the
  source filename, reports the current script line if a script stack exists,
  otherwise writes line `0`, and returns `1`.
- Retail HLIL for `0x004AC400` is a tailcall to the script-layer base-folder
  setter.
- Retail HLIL for `0x004AC410` walks the open source slots and prints the
  `file %s still open in precompiler` diagnostic.
- Retail HLIL for `0x004ACB10` validates the handle, reads a token, copies
  string/type/subtype/int/float fields into `pc_token_t`, and strips double
  quotes when the exported token type is `TT_STRING`.
- Retail HLIL for `GetBotLibAPI` assigns the exported PC slots in the order:
  add global define, load source, free source, read token, source file and line.

## Source Confirmation

The checked-in source matches the retail shape:

- `MAX_SOURCEFILES` remains `64`, with valid public handles `1..63`.
- `PC_LoadSourceHandle` resets the base folder to `""`, calls `LoadSourceFile`,
  stores the result, and returns the selected handle.
- `PC_FreeSourceHandle`, `PC_ReadTokenHandle`, and `PC_SourceFileAndLine` share
  the same range and null-slot guard.
- `PC_ReadTokenHandle` strips quotes for exported string tokens after copying
  the raw internal token string.
- `PC_CheckOpenSourceHandles` is called during botlib shutdown after
  `Log_Shutdown`, matching the existing lifecycle mapping.
- `botlib_export_t` and `GetBotLibAPI` expose exactly the four source-handle
  calls plus `PC_AddGlobalDefine`.

## Related Wiring

The qagame/server wiring split is important:

- Legacy VM syscalls in `SV_GameSystemCallsImpl` dispatch
  `BOTLIB_PC_LOAD_SOURCE`, `BOTLIB_PC_FREE_SOURCE`, `BOTLIB_PC_READ_TOKEN`, and
  `BOTLIB_PC_SOURCE_FILE_AND_LINE` directly to the botlib export table.
- `ql_game_compat_imports` keeps the same four PC calls for compatibility-mode
  qagame import dispatch.
- `ql_game_imports` has a named direct native slot for
  `G_QL_IMPORT_BOTLIB_PC_ADD_GLOBAL_DEFINE`, but there are no named direct
  native slots for the four source-handle calls.
- `ql_game_imports[G_QL_IMPORT_COMPAT_BASE]` receives the compatibility table,
  so the source-handle calls remain intentionally served through the retained
  legacy ID surface.
- `src/code/game/g_syscalls.c` still exposes the classic `trap_PC_*` wrappers
  using the legacy `BOTLIB_PC_*` constants.

Inference:

- The selected slice is a compact but important ABI boundary. It should be
  treated as closed unless future work touches precompiler token layout,
  qagame import packing, or VM/native import compatibility.

## 2026-06-11 Cgame Bridge Recheck

Follow-up mapping closed the native cgame side of the same PC source-handle
bridge:

- `FUN_004b0270` / `sub_4B0270 -> QLUIImport_PC_LoadSource`
- `FUN_004b0290` / `sub_4B0290 -> QLUIImport_PC_FreeSource`
- `FUN_004b02b0` / `sub_4B02B0 -> QLUIImport_PC_ReadToken`
- `FUN_004b02d0` / `sub_4B02D0 -> QLUIImport_PC_SourceFileAndLine`

Observed facts:

- Host HLIL shows the four wrappers as table jumps through
  `data_13e1844 + 0x204`, `+0x208`, `+0x20c`, and `+0x210`.
- The retail native import tables store the callbacks at
  `data_565b08..data_565b14` and `data_56749c..data_5674a8`.
- Source slots `CG_QL_IMPORT_PC_LOAD_SOURCE = 108` through
  `CG_QL_IMPORT_PC_SOURCE_FILE_AND_LINE = 111` map through
  `CG_MapNativeImport`, `ql_cgame_imports.inc`, and
  `CL_CgameSystemCallsImpl` back to `botlib_export->PC_*`.
- Companion cgame DLL HLIL for `FUN_10025ac0` confirms `CG_ParseMenu` consumes
  the same callback lane for HUD/menu source parsing, including the
  `ui/testhud.menu` fallback and the `assetGlobalDef` / `menudef` token
  dispatch.

The detailed round note is
`docs/reverse-engineering/botlib-cgame-pc-source-handle-bridge-recheck-2026-06-11.md`.

## Changes

- Added `test_botlib_precompiler_source_handle_slice_matches_retail_references`
  to `tests/test_botlib_internal_parity.py`.
- The new test pins:
  - source-handle wrapper source shape
  - `botlib_export_t` and `GetBotLibAPI` PC slot order
  - legacy `SV_GameSystemCallsImpl` dispatch
  - qagame compatibility import table entries
  - absence of named direct native PC source-handle slots
  - qagame `trap_PC_*` wrappers
  - retail HLIL body anchors and Ghidra `functions.csv` rows
- No C source body change was needed.

## Follow-On Work

Good next botlib slices:

- `l_precomp.c` macro expansion and directive handling, starting with
  `PC_ReadToken`, `PC_ExpandDefineIntoSource`, and include handling.
- `l_script.c::PS_ReadNumber` and punctuation handling, especially where bot
  resource parsers rely on permissive legacy token behavior.
- The remaining UI-side PC source-handle import wrappers, if a future task
  explicitly includes UI work. `src/ui/` remains read-only under the current
  repository instructions.

## Validation

Targeted validation for this pass:

- `python -m pytest tests/test_botlib_internal_parity.py -k "precompiler_source_handle_slice or precompiler_and_script_internal_aliases or lifecycle_parser" -q`
- `python -m pytest tests/test_botlib_internal_parity.py -q`
- `python -m pytest tests/test_game_native_export_helper_parity.py -q`
- `python -m pytest tests/test_bot_resource_loading.py -q`

Observed result:

- focused source-handle selection: `3 passed, 28 deselected`
- full botlib internal parity file: `31 passed`
- native export/import helper parity: `11 passed`
- adjacent bot resource loading: `3 passed`

No game launch was performed. Static source, HLIL, Ghidra, and pytest coverage
answer this mapping question.

## Parity Estimate

- Focused precompiler source-handle slice: `76% -> 96%`. Before this round,
  the names were present in aliases and export-table coverage, but the wrapper
  bodies, handle range, token copy semantics, and compatibility import boundary
  were not pinned together.
- Overall botlib plus related parser/API wiring: approximately `68% -> 69%`.
- Strict-retail Windows replacement target: unchanged at `100%`.
