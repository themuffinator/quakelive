# Quake Live Ghidra Reference Workflow

## Scope

This repository now keeps an OpenAlice-style Ghidra reference corpus alongside the
existing Binary Ninja HLIL dumps so reverse-engineering work has both:

- the retail Quake Live binaries as the primary evidence base
- committed, structured Ghidra exports for fast triage and repeatable analysis

Reference binaries:

- `assets/quakelive/quakelive_steam.exe`
- `assets/quakelive/awesomium_process.exe`
- `assets/quakelive/baseq3/cgamex86.dll`
- `assets/quakelive/baseq3/qagamex86.dll`
- `assets/quakelive/baseq3/uix86.dll`

## Canonical Reference Location

Generated outputs are committed under:

- `references/reverse-engineering/ghidra/quakelive_steam/`
- `references/reverse-engineering/ghidra/awesomium_process/`
- `references/reverse-engineering/ghidra/cgamex86/`
- `references/reverse-engineering/ghidra/qagamex86/`
- `references/reverse-engineering/ghidra/uix86/`

Each folder contains:

- `metadata.txt`
- `functions.csv`
- `imports.txt`
- `exports.txt`
- `analysis_symbols.txt`
- `decompile_top_functions.c`

The `uix86/` folder additionally contains:

- `decompile_annotated.c` — `decompile_top_functions.c` with every raw
  `FUN_XXXXXXXX` token replaced by its normalized name from
  `references/symbol-maps/ui.json`.  All 275 of the 276 unique `FUN_`
  tokens in the top-functions decompile are resolved; the single
  exception (`PTR_FUN_1002a01c`) is a data-pointer label, not a function
  entry point.  Regenerate with:

  ```
  python3 scripts/ghidra/build_ui_annotated.py
  ```

## Companion Binary Ninja / Mapping Material

Use the committed Ghidra corpus with the existing Binary Ninja material rather than
instead of it:

- `references/hlil/quakelive/quakelive_steam.exe/`
- `references/hlil/quakelive/cgamex86.dll/`
- `references/hlil/quakelive/qagamex86.dll/`
- `references/hlil/quakelive/uix86.all/`
- `references/symbol-maps/`
- `docs/reverse-engineering/ghidra-module-mapping.md`

`awesomium_process.exe` still only has the committed Ghidra companion corpus plus
the PE/toolchain metadata in `references/analysis/quakelive_toolchain_metadata.json`
on the reverse-engineering side; there is no committed Binary Ninja HLIL dump for
that helper yet. The current source reconstruction for the thin bootstrap lives in
`src/code/win32/awesomium_process.cpp`, `src/code/win32/awesomium.def`, and
`src/code/awesomium_process.vcxproj`.

Precedence rule:

- Treat retail binaries in `assets/quakelive/` plus the committed HLIL dumps under
  `references/hlil/` as canonical for parity claims.
- Treat the committed Ghidra corpus under `references/reverse-engineering/ghidra/`
  as the primary structured companion corpus for day-to-day recovery work.
- Treat live MCP output and ad-hoc decompiler sessions as advisory until they are
  revalidated against committed corpus files and, when needed, the HLIL dumps.

## UI Module: Ghidra-Readable Reference and Separate Source Recreation

The UI module has a dedicated workflow built on top of the standard Ghidra
export:

### Step 0 — Build the committed Ghidra-readable reference

```
python3 scripts/ghidra/build_ui_ghidra_reference.py
```

This generates:

```
references/reverse-engineering/ghidra/uix86/ui_ghidra_reference.h
```

The header is self-contained on purpose so Ghidra and the generated C export can
consume it without depending on the production include graph. It combines:

- the committed `ui.json` symbol-address catalog
- curated exact prototypes recovered in `src-re/ui/`
- the retail syscall-slot constants already bounded through the committed UI
  reverse-engineering work

### Step 1 — Apply symbol map to a live Ghidra project

```
analyzeHeadless <project_dir> <project_name> \
    -process uix86.dll \
    -postScript ghidra_scripts/ApplyUISymbolMap.py
```

`ApplyUISymbolMap.py` renames every `FUN_XXXXXXXX` function in the open
Ghidra database using the `normalized_name` from
`references/symbol-maps/ui.json` and appends the `comment` field as a
plate comment on the function entry point.

### Step 2 — Export annotated C source from Ghidra

Run after Step 1:

```
analyzeHeadless <project_dir> <project_name> \
    -process uix86.dll \
    -postScript ghidra_scripts/ExportUISourceRecreation.py \
    [<output_root>] [<reference_path>]
```

`ExportUISourceRecreation.py` decompiles every non-external function and writes
the result to:

```
<output_root>/
    ui_reconstruction.c   -- full annotated decompile of all 348 functions
    include/
        ui_ghidra_reference.h -- copied committed reference header
        ui_prototypes.h       -- forward declarations for all decompiled functions
```

`<output_root>` defaults to
`references/reverse-engineering/ghidra/uix86/source-recreation/`.

`<reference_path>` defaults to
`references/reverse-engineering/ghidra/uix86/ui_ghidra_reference.h`.

The generated source recreation now stays separate from the hand-authored
`src-re/ui/` workspace. `src-re/ui/` remains the manual reconstruction area;
the machine-generated Ghidra export lives under the committed Ghidra corpus.

### One-shot wrapper

For the UI-only flow, run:

```powershell
scripts\ghidra\run_ui_source_recreation.ps1
```

This wrapper:

1. regenerates `ui_ghidra_reference.h`
2. imports `uix86.dll` into a temporary headless project
3. applies `ApplyUISymbolMap.py`
4. exports the separate C recreation with `ExportUISourceRecreation.py`

### Offline annotation (no Ghidra required)

The committed `decompile_top_functions.c` (top 180 functions by body size)
can be re-annotated offline using the Python helper:

```
python3 scripts/ghidra/build_ui_annotated.py
```

This regenerates `references/reverse-engineering/ghidra/uix86/decompile_annotated.c`.

### Source reconstruction workspace

`src-re/ui/` is the active reconstruction workspace:

- `include/ui_local.h` — Quake Live-specific types, syscall-table slot
  constants, and prototypes recovered from the symbol map.
- `ui_main.c` — Initial reconstruction stubs for the module entry point
  and all `_UI_*` engine-facing API functions.

Machine-generated Ghidra exports are intentionally kept out of this tree and now
live in `references/reverse-engineering/ghidra/uix86/source-recreation/`.

## Tooling

- Headless exporter script: `scripts/ghidra/ExportQuakeLiveReference.java`
- Runner wrapper: `scripts/ghidra/run_quakelive_reference.ps1`
- UI reference builder: `scripts/ghidra/build_ui_ghidra_reference.py`
- UI-only recreation wrapper: `scripts/ghidra/run_ui_source_recreation.ps1`
- UI symbol-map application: `ghidra_scripts/ApplyUISymbolMap.py`
- UI source-recreation export: `ghidra_scripts/ExportUISourceRecreation.py`
- Offline UI annotation helper: `scripts/ghidra/build_ui_annotated.py`
- Optional GhidrAssistMCP bootstrap: `scripts/ghidra/setup_ghidrassist_mcp.ps1`
- Default Ghidra install path used by the wrapper:
  - `C:\Users\djdac\Tools\ghidra_12.0.4_PUBLIC`

## Optional Live MCP Analysis

Quake Live can use GhidrAssistMCP as an interactive analysis aid while keeping the
committed exports and HLIL corpus as the evidence base.

Quick setup:

```powershell
scripts\ghidra\setup_ghidrassist_mcp.ps1 -Mode release
```

Full setup and usage details:

- `docs/reverse-engineering/ghidrassist-mcp.md`

## Regeneration

Run from repository root:

```powershell
scripts\ghidra\run_quakelive_reference.ps1
```

Optional parameters:

- `-GhidraHome` to point at another Ghidra install
- `-QuakeLiveRoot` to point at another retail binary snapshot
- `-OutputRoot` to write to a different output directory
- `-MaxDecompFunctions` to change how many large functions are exported

## Fingerprints

Reference binary MD5 values:

- `quakelive_steam.exe`: `B8E404E377AB33E482DF9D6063F67DA5`
- `awesomium_process.exe`: `C4B3D8ED06ECBEC2B2FD0D1FAEDB1FEF`
- `cgamex86.dll`: `375A1CC258A7432DF35EBBE0A5215B9B`
- `qagamex86.dll`: `005D0C49D4190FE82F325E4FB6437AD0`
- `uix86.dll`: `64321E7C6357A59063AE8900E2A20732`

## Reconstruction Guidelines

These guidelines are intentionally imported from the OpenAlice workflow and adapted
to Quake Live:

- Treat the artifacts as evidence for behavior and interfaces, not as drop-in
  source code.
- Start with `metadata.txt`, `imports.txt`, `exports.txt`, and `functions.csv`
  before reading large decompile output.
- Treat `decompile_top_functions.c` as a hint set, not ground truth.
- Build each semantic claim from at least two signals when possible:
  - call relationships and symbol context
  - strings, imports, exports, and constants
  - repeated offsets and data access patterns
- Separate observed facts from inferred meaning in notes and reviews.
- Track confidence and open questions instead of forcing unstable names.
- Validate engine-facing assumptions against the Binary Ninja HLIL dumps whenever
  there is disagreement or uncertainty.
- Do not claim certainty without direct evidence from the retail corpus.
