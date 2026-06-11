# Botlib Cgame PC Source-Handle Bridge Recheck - 2026-06-11

## Scope

This pass rechecks the native cgame parser bridge that forwards cgame PC
source-handle calls into the reconstructed botlib precompiler API. It is a
wiring round, not a parser-body rewrite: the botlib `l_precomp.c` source-handle
bodies were already reconstructed and the current source bridge already matches
the retail shape.

## Owning Retail Binaries

Canonical host evidence:

- `assets/quakelive/quakelive_steam.exe`
- `references/hlil/quakelive/quakelive_steam.exe/quakelive_steam.exe_hlil_split/quakelive_steam.exe_hlil_part04.txt`
- `references/hlil/quakelive/quakelive_steam.exe/quakelive_steam.exe_hlil_split/quakelive_steam.exe_hlil_part07.txt`
- `references/reverse-engineering/ghidra/quakelive_steam/functions.csv`

Companion cgame consumer evidence:

- `references/hlil/quakelive/cgamex86.dll/cgamex86.dll_hlil.txt`
- `references/reverse-engineering/ghidra/cgamex86/functions.csv`

Source surfaces checked:

- `src/code/client/cl_cgame.c`
- `src/code/client/ql_cgame_imports.inc`
- `src/code/cgame/cg_public.h`
- `src/code/cgame/cg_syscalls.c`
- `src/code/cgame/cg_local.h`
- `src/code/cgame/cg_main.c`
- `references/analysis/quakelive_symbol_aliases.json`

## Retail Evidence

Observed facts:

- `0x004b0270`, `0x004b0290`, `0x004b02b0`, and `0x004b02d0` have Ghidra
  function rows and stable sizes of `18`, `18`, `18`, and `17` bytes.
- Binary Ninja HLIL shows these wrappers jumping through
  `data_13e1844 + 0x204`, `+0x208`, `+0x20c`, and `+0x210`.
- The host import tables store the callbacks consecutively at
  `data_565b08..data_565b14` and again at `data_56749c..data_5674a8`.
- Retail `cgamex86.dll` row `FUN_10025ac0` (`383` bytes) is the HUD/menu
  source parser. HLIL loads sources through callback offset `+0x1b0`, reads
  tokens through `+0x1b8`, frees through `+0x1b4`, and contains the
  `ui/testhud.menu`, `assetGlobalDef`, and `menudef` string anchors.

## Source Confirmation

The checked-in source preserves the retail bridge:

- `cg_public.h` keeps `CG_QL_IMPORT_PC_ADD_GLOBAL_DEFINE = 107`, followed by
  the four source-handle slots `108..111` and reserved slots `112..113`.
- `CL_InitCGameImports` assigns the four direct native parser callbacks to
  `QL_CG_trap_PC_LoadSource`, `QL_CG_trap_PC_FreeSource`,
  `QL_CG_trap_PC_ReadToken`, and `QL_CG_trap_PC_SourceFileAndLine`.
- The wrappers in `ql_cgame_imports.inc` forward into `CG_Import_Syscall`
  using the legacy `CG_PC_*` constants.
- `CG_MapNativeImport` maps the same legacy `CG_PC_*` constants to the native
  `CG_QL_IMPORT_PC_*` slots.
- `CL_CgameSystemCallsImpl` handles the legacy path by calling
  `botlib_export->PC_LoadSourceHandle`, `PC_FreeSourceHandle`,
  `PC_ReadTokenHandle`, and `PC_SourceFileAndLine`.
- `cg_syscalls.c` still exposes the public `trap_PC_*` functions used by cgame
  source.
- `CG_ParseMenu` uses the bridge to load the requested menu file, falls back to
  `ui/testhud.menu`, consumes `assetGlobalDef` and `menudef` tokens, and frees
  the source handle.

## Changes

- Promoted:
  - `FUN_004b0270 -> QLUIImport_PC_LoadSource`
  - `FUN_004b0290 -> QLUIImport_PC_FreeSource`
  - `FUN_004b02b0 -> QLUIImport_PC_ReadToken`
  - `FUN_004b02d0 -> QLUIImport_PC_SourceFileAndLine`
- Added `test_cgame_pc_source_handle_bridge_matches_botlib_precompiler_contract`
  to `tests/test_botlib_cgame_native_import_slab_parity.py`.
- Expanded the existing cgame-native slab parity gate so the PC source-handle
  wrapper band is pinned by both Binary Ninja and Ghidra spellings.
- Added `docs/reverse-engineering/quakelive_steam_mapping_round_535.md`.

## Boundary

This round does not touch `src/ui/`; that tree is read-only under the current
repo instructions. It also does not rename the existing `QLUIImport_*` labels:
the labels remain the stable promoted names, while the new evidence documents
that native cgame uses the same parser bridge.

## Validation

- `python -m pytest tests/test_botlib_cgame_native_import_slab_parity.py -q --tb=short`

No runtime launch was needed.

## Parity Estimate

- Focused cgame PC source-handle bridge confidence:
  **before 78% -> after 98%**.
- Focused botlib precompiler-to-cgame wiring evidence:
  **before 88% -> after 96%**.
- Overall botlib plus adjacent parser/import wiring:
  **before 69.0% -> after 69.2%**.
