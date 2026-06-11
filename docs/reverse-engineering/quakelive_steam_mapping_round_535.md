# Quake Live Steam Mapping Round 535: Botlib Cgame PC Source-Handle Bridge

## Scope

This pass tightens the botlib/precompiler source-handle bridge used by native
cgame imports in `quakelive_steam.exe`. The earlier botlib source-handle pass
closed the engine-owned `PC_LoadSourceHandle`, `PC_FreeSourceHandle`,
`PC_ReadTokenHandle`, and `PC_SourceFileAndLine` bodies; this round verifies
the retail cgame wrapper lane that reaches those botlib exports.

| Retail address | Ghidra name | Promoted name | Confidence |
| --- | --- | --- | --- |
| `0x004b0270` | `FUN_004b0270` / `sub_4B0270` | `QLUIImport_PC_LoadSource` | High |
| `0x004b0290` | `FUN_004b0290` / `sub_4B0290` | `QLUIImport_PC_FreeSource` | High |
| `0x004b02b0` | `FUN_004b02b0` / `sub_4B02B0` | `QLUIImport_PC_ReadToken` | High |
| `0x004b02d0` | `FUN_004b02d0` / `sub_4B02D0` | `QLUIImport_PC_SourceFileAndLine` | High |

## Evidence

Observed retail facts:

- Ghidra `functions.csv` lists the four host wrappers at sizes `18`, `18`,
  `18`, and `17` bytes.
- Binary Ninja HLIL shows the wrappers as import-table jumps through
  `data_13e1844 + 0x204`, `+0x208`, `+0x20c`, and `+0x210`.
- The retail native import tables contain the same four callbacks at
  `data_565b08..data_565b14` and `data_56749c..data_5674a8`.
- The reconstructed native import enum keeps the matching cgame slots at
  `CG_QL_IMPORT_PC_LOAD_SOURCE = 108` through
  `CG_QL_IMPORT_PC_SOURCE_FILE_AND_LINE = 111`.
- `CL_CgameSystemCallsImpl` dispatches the legacy `CG_PC_*` calls directly to
  the botlib export table, preserving the same source-handle contract as the
  earlier `l_precomp.c` reconstruction.
- The retail `cgamex86.dll` companion evidence for `0x10025ac0` confirms
  `CG_ParseMenu` consumes this lane: it loads through callback offset `+0x1b0`,
  falls back to `ui/testhud.menu`, reads tokens through `+0x1b8`, dispatches
  `assetGlobalDef` and `menudef`, and frees through `+0x1b4`.

Inferred meaning:

- The four names are safe to promote in both Binary Ninja and Ghidra spelling
  forms because the function rows, HLIL jump offsets, table slots, reconstructed
  import enum, host syscall dispatch, and cgame parser consumer all agree.
- The `QLUIImport_*` prefix is retained as the existing stable retail name even
  though this round proves the same parser bridge is also used by native cgame
  HUD/menu parsing.

## Reconstruction

- Promoted the four Ghidra-style `FUN_*` aliases in
  `references/analysis/quakelive_symbol_aliases.json`.
- Extended `tests/test_botlib_cgame_native_import_slab_parity.py` so the
  native cgame slab gate now pins:
  - Binary Ninja and Ghidra alias spellings for the four PC source-handle
    callbacks;
  - Ghidra row sizes;
  - host HLIL jump offsets and retail table placements;
  - cgame import slot ordering and `CG_MapNativeImport` mapping;
  - native host wrappers in `ql_cgame_imports.inc`;
  - legacy `CL_CgameSystemCallsImpl` dispatch into `botlib_export->PC_*`;
  - `cg_syscalls.c` trap wrappers and `cg_local.h` declarations;
  - the `CG_ParseMenu` source consumer and retail `cgamex86.dll` HLIL anchors.

No C source body change was needed.

## Validation

- `python -m pytest tests/test_botlib_cgame_native_import_slab_parity.py -q --tb=short`

No game launch was performed. Static source, HLIL, Ghidra, and pytest evidence
answer this mapping question.

## Parity Estimate

- Focused cgame PC source-handle bridge confidence:
  **before 78% -> after 98%**.
- Focused botlib precompiler-to-cgame wiring evidence:
  **before 88% -> after 96%**.
- Overall botlib plus adjacent parser/import wiring:
  **before 69.0% -> after 69.2%**.
