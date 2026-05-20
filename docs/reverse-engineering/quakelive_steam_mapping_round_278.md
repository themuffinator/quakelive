# Quake Live Steam Host Mapping Round 278

## Scope

- Continued the renderer-focused Ghidra symbol pass in `quakelive_steam.exe`.
- Focused on the renderer command-buffer core, the private `GetRefAPI` tail,
  the post-process init/shutdown/enabled/restart lane, and the FontStash host
  text exports now wired through the reconstructed renderer source.
- No runtime source behavior was changed in this round.

## Evidence

- `references/reverse-engineering/ghidra/quakelive_steam/functions.csv`
  confirms committed Ghidra function rows for the promoted starts that Ghidra
  recovered as functions:
  - `FUN_004386d0`
  - `FUN_0043c480`, `FUN_0043c540`, `FUN_0043c570`
  - `FUN_0043cbe0`, `FUN_0043cc50`
  - `FUN_00450710`, `FUN_00450780`, `FUN_004507c0`
  - `FUN_00451420`, `FUN_00451460`
- `0x00449f10` is exposed by the committed HLIL as `sub_449f10` and is stored
  directly in the retail `GetRefAPI` tail, but the current Ghidra CSV export
  did not recover it as a separate function row.
- `references/hlil/quakelive/quakelive_steam.exe/quakelive_steam.exe_hlil_split/quakelive_steam.exe_hlil_part01.txt`
  anchors the bloom-program uniform setter:
  - `sub_4386d0` guards on `sub_4507c0`, the active post-process state, and
    the bloom enable cvar before writing `p_brightthreshold`,
    `p_bloomsaturation`, `p_bloomintensity`, `p_scenesaturation`, and
    `p_sceneintensity`.
  - `sub_4384d0` is adjacent command-buffer evidence for the exported bloom
    command lane, but this pass leaves its exact source name open.
- `references/hlil/quakelive/quakelive_steam.exe/quakelive_steam.exe_hlil_split/quakelive_steam.exe_hlil_part02.txt`
  anchors the renderer tail and command-buffer lane:
  - `sub_43c480` appends the command-list terminator, optionally runs
    `R_PerformanceCounters`, and dispatches the backend command list.
  - `sub_43c540` calls `sub_43c480(0)` and sleeps or synchronizes the render
    thread when the renderer is registered.
  - `sub_43c570` allocates from the active command list and uses the retail
    fatal string `R_GetCommandBuffer: bad size %i`.
  - `sub_43cbe0` and `sub_43cc50` set the retained FontStash size/font and
    then call `fonsDrawText`, `fonsTextBounds`, and `fonsVertMetrics`.
  - `sub_449f10` synchronizes the render thread, shuts down post-process
    resources, rebuilds them, and then reapplies color mappings.
  - `GetRefAPI` stores `sub_449f10`, `sub_451420`, `sub_451460`,
    `R_TransformClipToWindow`, `sub_43cbe0`, and `sub_43cc50` in the private
    renderer export tail.
  - `sub_450710`, `sub_450780`, and `sub_4507c0` match the post-process
    rebuild/init, shutdown, and enabled-query roles.
  - `sub_451420` marks the renderer state dirty and tailcalls `sub_4386d0`
    with five bloom tuning floats.
  - `sub_451460` calls `R_TransformModelToClip` with the active backend model
    and projection matrices, then rejects points outside `-w..w` clip bounds.
- Source-side cross-checks:
  - `src/code/renderer/tr_cmds.c` owns `R_IssueRenderCommands`,
    `R_SyncRenderThread`, and `R_GetCommandBuffer`.
  - `src/code/renderer/tr_backend.c` owns `RB_PostProcessEnabled`,
    `RBPP_RebuildState`, and `RBPP_Shutdown`.
  - `src/code/renderer/tr_init.c` owns the source-side
    `R_PostProcessRestart` wrapper and private tail assignment for the
    reconstructed slots already safe to expose.
  - `src/code/renderer/tr_font.c` owns `RE_DrawScaledText` and
    `RE_MeasureScaledText`.

## Promoted Aliases

Updated `references/analysis/quakelive_symbol_aliases.json`:

| Address | Alias | Confidence | Evidence |
| --- | --- | --- | --- |
| `sub_4386D0` | `RBPP_SetBloomUniforms` | High | Writes the five recovered bloom uniforms after the post-process/bloom guards. |
| `sub_43C480` | `R_IssueRenderCommands` | High | Terminates and dispatches the active render command list; optional performance-counter pass. |
| `sub_43C540` | `R_SyncRenderThread` | High | Registered-renderer sync wrapper around `sub_43C480(0)`. |
| `sub_43C570` | `R_GetCommandBuffer` | High | Active command-list allocator with the exact retail bad-size fatal string. |
| `sub_43CBE0` | `RE_DrawScaledText` | High | FontStash size/font setup followed by `fonsDrawText`. |
| `sub_43CC50` | `RE_MeasureScaledText` | High | FontStash size/font setup followed by `fonsTextBounds` and `fonsVertMetrics`. |
| `sub_449F10` | `R_PostProcessRestart` | High | Private export-tail restart path: sync, shutdown, rebuild, color mappings. |
| `sub_450710` | `RBPP_RebuildState` | Medium-high | Retail post-process rebuild/init body; source folds this with cleanup in `RBPP_RebuildState`. |
| `sub_450780` | `RBPP_Shutdown` | High | Clears post-process state, releases color/bloom resources, and resets `r_postProcessActive`. |
| `sub_4507C0` | `RB_PostProcessEnabled` | High | Returns the runtime enabled state from `r_enablePostProcess` plus active support state. |
| `sub_451420` | `R_SetPostProcessBloomParameters` | Medium-high | Private export-tail wrapper that dirties renderer state and forwards five bloom tuning floats. |
| `sub_451460` | `R_ProjectPointToClipBounds` | Medium-high | Private export-tail model-to-clip helper that returns whether a point survives clip-bound tests. |

## Source Notes

- This was a symbol/evidence round only. The current source already has the
  command-buffer, host-text, post-process restart, transform, and safe refexport
  wiring needed by active callers.
- The source `refexport_t` still keeps generic placeholder names for the
  remaining private tail slots. The committed HLIL now clearly identifies the
  bloom parameter setter and clip-bound projector, but the command-id `0xa`,
  `0xb`, and `0xd` slots still need a separate backend-command reconstruction
  pass before they should be exposed as callable source behavior.

## Still Open

- `j_sub_43cba0` / `sub_43cba0` remains an unpromoted private tail slot. It
  allocates command id `0xb`, but the exact backend command role is not yet
  source-stable.
- `j_sub_4384d0` / `sub_4384d0` remains an unpromoted private tail slot. It is
  bounded to the bloom/post-process command lane and emits command id `0xa`,
  but its exact retail source name is still weaker than the aliases promoted
  above.
- `sub_43c750` is present in the current dirty alias ledger as
  `RE_RetailStretchPicCommand`, but this renderer round did not revalidate that
  name. Its command id `0xd` with four integer fields still needs a future
  backend-executor pass before source behavior should be exposed.

## Guardrail

- Added
  `tests/test_renderer_internal_helper_mapping_parity.py::test_renderer_mapping_round_278_promotes_tail_postprocess_and_command_symbols`.
- The guard checks:
  - every promoted alias in `quakelive_symbol_aliases.json`;
  - matching Ghidra function rows where available, plus direct HLIL coverage
    for the `0x00449F10` tail helper;
  - HLIL evidence for the bloom uniform setter, command-buffer core,
    post-process restart/rebuild/shutdown/enabled helpers, private export-tail
    slot assignments, host text exports, and clip-bound projector;
  - source-side owners in `tr_cmds.c`, `tr_backend.c`, `tr_init.c`, and
    `tr_font.c`.

## Parity Estimate

- Before: renderer private-tail and post-process symbol confidence was high,
  but these twelve address-backed owners still sat outside the shared alias
  ledger, about `88%` for this focused Ghidra mapping lane.
- After: the command-buffer core, host text exports, post-process restart and
  lifecycle helpers, bloom parameter setter, and clip-bound projector are
  promoted and guarded, about `94%` for this focused lane.
- Renderer runtime/source parity remains `100%` from the prior source pass.
  Repo-wide parity remains `98%`; this round improves evidence precision rather
  than claiming a new runtime closure.
