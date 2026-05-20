# Renderer Wiring Reverse-Engineering Round - 2026-05-20

## Scope

This round re-audited `src/code/renderer/` and the renderer-facing host wiring
that feeds it:

- native renderer exports and client import slabs in `src/code/client/`
- Win32 renderer host glue in `src/code/win32/`
- renderer parity gates and runtime evidence under `tests/`, `tools/renderer/`,
  and `artifacts/renderer_validation/`
- retail-module evidence under `artifacts/module_validation/`

Owning retail binary:

- `assets/quakelive/quakelive_steam.exe`

Committed evidence used:

- `references/reverse-engineering/ghidra/quakelive_steam/metadata.txt`
- `references/reverse-engineering/ghidra/quakelive_steam/imports.txt`
- `references/reverse-engineering/ghidra/quakelive_steam/exports.txt`
- `references/reverse-engineering/ghidra/quakelive_steam/functions.csv`
- `references/reverse-engineering/ghidra/quakelive_steam/analysis_symbols.txt`
- `references/hlil/quakelive/quakelive_steam.exe/quakelive_steam.exe_hlil_split/`
- `references/analysis/quakelive_symbol_aliases.json`

## Corpus Snapshot

Observed facts:

- `metadata.txt` still reports `5473` functions, `351` imports, `2` exports,
  and `4377` promoted analysis symbols for `quakelive_steam.exe`.
- The current worktree alias ledger contains `4239` raw aliases and `4090`
  strict address-backed aliases, about `74.730%` of the Ghidra function corpus.
- The `quakelive_steam` bucket currently carries `370` renderer or
  renderer-wiring aliases across `R_*`, `RE_*`, `RB_*`, `GL_*`, `GLimp_*`,
  `QGL_*`, `AdvertisementBridge_*`, `QLUIImport_*`, and `QLCGImport_*`.
- The checked source-file ledger still counts `23` tracked renderer source
  entries with about `471` renderer function definitions.

Inference:

- The renderer source is no longer a broad unmapped surface. The highest-value
  work is validating hidden ownership mismatches under already-promoted
  subsystems, especially host text and native-module wiring.

## Renderer Core And Wiring Walk

Observed facts:

- Export and loading bridge closure still holds through the promoted
  `AdvertisementBridge_UpdateLoadingViewParameters` tail and the client
  wrappers that expose it to native modules.
- Memory-image ingestion is still bounded by `R_CreateImageWithTarget`,
  `R_DetectImageTypeFromMemory`, `R_LoadImageFromMemory`, and the Steam/live
  resource wrapper lane.
- Post-process and color-correction ownership still matches the HLIL strings
  for `brightpass`, `downsample1`, `blurvertical`, `blurhoriz`, `combine`, and
  `colorcorrect`, plus the `r_contrast` cvar registration.
- Win32 renderer host glue remains a closed strict-retail Windows surface on
  current evidence; the remaining non-Windows graphics debt stays under
  `RW-G02`, not the renderer source tree.
- Native `ui` and `cgame` host text imports route through
  `RE_DrawScaledText` and `RE_MeasureScaledText`, and those renderer helpers
  now own UTF-8 decode, digit-only color escapes, fallback-face probing, and
  codepoint-plus-size glyph keys.

Inference:

- No new file-level gap should be opened against the scene, world/model,
  shader, post-process, export ABI, or Win32 host-glue renderer surfaces.

## FontStash Lazy Atlas Correction

Observed facts:

- Retail `R_InitFontStash` HLIL at `0x00443FE0` creates the retained context
  at `512 x 512`, installs `sub_442300` as the `R_fonsErrorCallback` callback,
  loads `normal`, `sans`, `mono`, `sans-fallback`, and
  `sans-windows-fallback`, and assigns the preferred sans/fallback slots.
- That retail init path does not prebuild every `GLYPH_START..GLYPH_END` glyph
  for every retained face.
- Retail `R_fonsErrorCallback` at `0x00442300` doubles the atlas toward
  `2048 x 1024`, then flushes the cache at the maximum size.
- The tracked retail-module artifact from 2026-04-21 still records
  `R_fonsErrorCallback: repeated font atlas saturation prevented CS_ACTIVE
  after retail module load`.

Source change:

- Removed the eager `R_PrebuildFontStashAtlas` startup sweep and the
  `R_FONTSTASH_PREBUILD_ATTEMPTS` scaffolding from `src/code/renderer/tr_font.c`.
- Left retained glyph caching lazy through `R_GetFontStashGlyph` during
  `RE_DrawScaledText` and `RE_MeasureScaledText`.
- Matched the retail expand-versus-flush split in `R_ResizeFontStashAtlas`:
  atlas growth now copies old alpha rows into the larger buffer and rescales
  cached glyph UVs, while the existing max-size flush path remains the only
  path that clears retained glyph state.
- Matched the retail `*fontstash` texture-storage callback: retained atlas
  uploads now use `GL_ALPHA` storage/data directly, with the RGBA seed image
  reserved for initial renderer image creation.

Inference:

- The 2026-04-21 retail-module blocker is now best treated as stale runtime
  evidence for `FG-04` until the retail-module probe is rerun. The source-side
  behavior that most plausibly caused the saturation no longer matches the
  current renderer tree.
- Retained host text growth is now closer to the FontStash lifetime recovered
  from HLIL: growth preserves cache contents, while flush is an explicit
  max-atlas fallback rather than a side effect of ordinary expansion.
- Retained host text upload is now closer to the retail texture path recovered
  from HLIL: the source no longer treats the live atlas as a synthetic RGBA
  image after the `*fontstash` handle exists.

## Refexport ABI Tail Correction

Observed facts:

- Retail `GetRefAPI` (`sub_449F70`) copies the import slab, rejects any
  renderer API version other than `9`, zeroes the export table at
  `data_587848` with size `0x9c`, and returns that table to `CL_InitRef`.
- The retail export run places `AdvertisementBridge_UpdateLoadingViewParameters`
  at offset `0x40`, immediately between `RenderScene` and `SetColor`.
- The post-`ModelBounds` offset `0x68` is the pure no-op `sub_4D7980`, not the
  client/module `RE_RegisterFont` compatibility lane.
- Retail `CL_PostProcessRestart_f` (`sub_4B9060`) calls the copied function
  pointer at `data_146CCE0`, which is the export-table offset `0x80`.
- The private tail after `inPVS` continues through the recovered post-process,
  projection, host text draw/measure, and stretch-pic command helpers before
  the `0x9c` copy boundary.

Source change:

- Updated `REF_API_VERSION` to `9`.
- Restored the public `refexport_t` order so `SetColor` follows the
  loading-view bridge, `RegisterFont` occupies the legacy no-op slot after
  `ModelBounds`, and `PostProcessRestart` sits in the private tail after
  `inPVS`.
- Added the no-op `R_NoopRegisterFont` assignment for the legacy slot while
  keeping native UI/cgame font registration on the client wrappers that call
  the classic `RE_RegisterFont` path directly.
- Added a three-argument `R_TransformClipToWindowExport` wrapper for the
  private retail tail slot; the local helper still keeps its explicit
  `viewParms_t` argument for internal renderer call sites.

Inference:

- This was a hidden ABI exactness issue rather than a visible in-tree crash,
  because the reconstructed client and renderer shared the same shifted header.
  Retail-module and source-compatibility work need the table shape itself to
  match the committed retail copy semantics.

## Parity Estimate

- Scoped renderer source/wiring estimate before this round: **99%** after
  reopening the eager-retained-atlas, retained atlas upload, and export-tail
  ABI mismatches from the retail HLIL.
- Scoped renderer source/wiring estimate after this round: **100%** structural
  source parity restored for the retained host-text atlas lifetime and
  renderer export wiring.
- Repo-wide estimate remains **98%** until fresh native/runtime artifacts close
  the broader `RW-G04` evidence-freshness lane.

## Verification

Static validation performed in this round:

- Source and docs now pin that retained host glyphs are cached lazily as text
  is measured or drawn, retained atlas refreshes use `GL_ALPHA`, and the
  renderer export table preserves the retail API version plus private tail
  order.
- The function-level gap audit now distinguishes the source-side fix from the
  still-stale retail-module runtime artifact.
- `pytest tests/test_renderer_export_tail_parity.py
  tests/test_engine_client_command_parity.py
  tests/test_renderer_host_text_core_parity.py
  tests/test_renderer_full_parity_gate.py -q`: `27 passed, 1 skipped`.
- `$tests = Get-ChildItem tests -Filter 'test_renderer_*.py' | ForEach-Object {
  $_.FullName }; pytest $tests -q`: `43 passed, 1 skipped`.
- `pwsh -NoProfile -ExecutionPolicy Bypass -File
  tools\ci\audit-retail-font-stack.ps1`: completed and verified retained
  FontStash atlas growth, `GL_ALPHA` uploads, and refexport tail order. The
  existing cgame ownership warnings remain unrelated to this renderer pass.
- `pytest tests/test_source_file_audit_generator.py -q`: `21 passed`.
- `pytest tests/test_client_full_parity_gate.py
  tests/test_engine_host_support_full_parity_gate.py
  tests/test_qcommon_full_parity_gate.py tests/test_server_full_parity_gate.py
  tests/test_game_module_retail_parity_gate.py -q`: `10 passed, 5 skipped`.
- `git diff --check` over the touched renderer/docs/test/audit files completed
  without whitespace errors.

Runtime validation not performed:

- No game launch was run in this pass. The next evidence-producing step is a
  windowed retail-module runtime rerun with the standard `+set r_fullscreen 0`
  probe contract.
