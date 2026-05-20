# Quake Live Steam Host Mapping Round 281

Date: 2026-05-20

## Scope

This renderer round continued the command-buffer and post-process wiring closure started in rounds 278 and 279. It focused on backend command handlers that were already visible through `RB_ExecuteRenderCommands`, plus the scene-target framebuffer helpers used by bloom, screenshots, and retail private refexport tail commands.

Round 280 was already occupied by an untracked client-side note in this worktree, so this renderer continuation uses round 281.

No renderer source behavior changed.

## Evidence Used

- `references/reverse-engineering/ghidra/quakelive_steam/functions.csv`
- `references/hlil/quakelive/quakelive_steam.exe/quakelive_steam.exe_hlil_split/quakelive_steam.exe_hlil_part01.txt`
- `references/hlil/quakelive/quakelive_steam.exe/quakelive_steam.exe_hlil_split/quakelive_steam.exe_hlil_part02.txt`
- `src/code/renderer/tr_backend.c`
- `src/code/renderer/tr_cmds.c`
- `src/code/renderer/tr_local.h`

## Promoted Symbols

| Address | Alias | Confidence | Evidence |
| --- | --- | --- | --- |
| `sub_436280` | `RB_SetGL2D` | High | Sets 2D projection, viewport/scissor, GL state, and backend frame time. This matches `void RB_SetGL2D( void )`. |
| `sub_4367F0` | `RB_SetColor` | High | Consumes a set-color render command, scales four RGBA floats by 255, stores the backend 2D color bytes, and returns the next command. |
| `sub_436DC0` | `RBPP_ApplyColorCorrectPass` | High | Copies the default framebuffer into the color-correct rectangle texture, binds the color-correct program, draws the full-screen quad, and returns command size `0x10`. |
| `sub_437450` | `RB_DrawSurfs` | High | Flushes pending 2D work, copies `refdef`/`viewParms`, calls `RB_RenderDrawSurfList`, and advances by the draw-surfs command payload. |
| `sub_437920` | `RB_SetViewportAndScissorCommand` | High | Executes retail command ID 13 by either resetting to the full backbuffer or storing an override rectangle and calling the viewport/scissor proc. |
| `sub_4379B0` | `RB_DrawFontStashTextCommand` | Medium-high | Executes retail command ID 12 by setting a 24-point FontStash size/color and drawing the payload text at command x/y coordinates. Source keeps the public text path in `tr_font.c`, so this is a command ABI name rather than an exact GPL helper. |
| `sub_437BC0` | `RB_RenderThread` | High | Sleeps for queued renderer work, executes render commands, toggles render-thread active state, and exits on null work. This matches `void RB_RenderThread( void )`. |
| `sub_438790` | `RBPP_BindSceneRenderTarget` | High | Binds the scene framebuffer when present. The executor uses it for command ID 11, and screenshot paths release/rebind the scene target around readback. |
| `sub_4387B0` | `RBPP_BindBloomRenderTargetByIndex` | Medium-high | Bounds an index to 0..7 and binds the corresponding bloom framebuffer array slot. The recovered source currently expresses this through typed render-target calls inside `RBPP_ApplyBloom`. |
| `sub_4387D0` | `RBPP_ReleaseSceneRenderTarget` | High | Binds framebuffer 0. Screenshot and bloom paths call it before reading/presenting from the default framebuffer. |
| `sub_4387E0` | `RBPP_GetBloomMode` | High | Returns the stored bloom mode used by `RBPP_ApplyBloom`. The source has `static int RBPP_GetBloomMode( void )`. |
| `sub_43CBA0` | `R_AddBindSceneRenderTargetCommand` | High | Private refexport tail command emitter installed at `data_5878c0`; queues command ID 11, which `RB_ExecuteRenderCommands` executes by calling `RBPP_BindSceneRenderTarget`. |

## Command ABI Notes

- Command ID 1 is now fully paired as `RE_SetColor` -> `RB_SetColor`.
- Command ID 3 is now fully paired as `R_AddDrawSurfCmd` -> `RB_DrawSurfs`.
- Command ID 9 is now fully paired as `R_AddColorCorrectPostProcessCommand` -> `RBPP_ApplyColorCorrectPass`.
- Command ID 11 is now documented as the scene-target rebind command emitted by the private refexport tail slot at `data_5878c0`.
- Command ID 12 is the retail FontStash text payload command. It is kept separate from `RE_DrawScaledText`, which is an immediate refexport tail helper.
- Command ID 13 is the viewport/scissor override command emitted by `sub_43C750`; the existing alias `RE_RetailStretchPicCommand` remains in the ledger, but this round records the backend executor side as viewport/scissor state.

## Open Follow-Up

- Resolve the human-facing retail name for the `data_5878e0` / `sub_43C750` private export slot. Current evidence proves the command ID 13 payload shape, but not the original name.
- Continue the same command ABI table outward into screenshot, advertisement-query, draw-buffer, and raw-cinematic commands to make the renderer command stream self-documenting.

## Guard Coverage

`tests/test_renderer_internal_helper_mapping_parity.py` now checks the round 281 aliases, validates every CSV-backed function except the compiler-shaped `sub_43CBA0` private tail shim, and anchors the source/HLIL evidence for backend command handlers, render-thread execution, scene-target release/rebind, and retail text/viewport commands.

## Parity Estimate

- Renderer command-buffer symbol mapping: before 94%, after 97%.
- Renderer post-process scene-target wiring documentation: before 94%, after 97%.
- Retail behavior parity: unchanged by this mapping-only round.
