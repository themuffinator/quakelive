# Quake Live Steam Host Mapping Round 282

Date: 2026-05-20

## Scope

This renderer pass extends the command-buffer closure from rounds 279 and 281 into the front-end draw-surf enqueue path and the Win32 GLimp threading boundary. The goal was to connect the renderer command ABI to the functions that start, stop, sleep, and wake the backend render thread.

No source behavior changed in this round.

## Evidence Used

- `references/reverse-engineering/ghidra/quakelive_steam/functions.csv`
- `references/hlil/quakelive/quakelive_steam.exe/quakelive_steam.exe_hlil_split/quakelive_steam.exe_hlil_part02.txt`
- `src/code/renderer/tr_cmds.c`
- `src/code/renderer/tr_backend.c`
- `src/code/win32/win_glimp.c`

## Promoted Symbols

| Address | Alias | Confidence | Evidence |
| --- | --- | --- | --- |
| `sub_43C400` | `R_InitCommandBuffers` | High | Checks `r_smp`, prints the SMP startup messages, spawns `RB_RenderThread`, and sets the SMP-active flag on success. |
| `sub_43C460` | `R_ShutdownCommandBuffers` | High | Wakes the renderer with a null payload and clears the SMP-active flag. |
| `sub_43C5D0` | `R_AddDrawSurfCmd` | High | Queues command ID 3, stores draw-surf pointer/count, and copies the current `refdef` and `viewParms` payloads. |
| `sub_46B840` | `GLimp_EndFrame` | High | Handles optional `SwapBuffers`, loggable end-frame behavior, and calls the logging toggle helper just like `GLimp_EndFrame`. |
| `sub_46B8F0` | `GLimp_Shutdown` | High | Tears down gamma, GL context, device context, window, log file, display settings, QGL, `glConfig`, and `glState`. |
| `sub_46BAA0` | `GLimp_LogComment` | High | Thin wrapper around `fprintf( glw_state.log_fp, "%s", comment )` guarded by a non-null log file. |
| `sub_46BAD0` | `GLimp_RenderThreadWrapper` | Medium-high | Calls the stored render-thread function pointer and unbinds the WGL context before the thread exits. It appears in HLIL/source2 but is absent from `functions.csv`, so the guard treats it as compiler/export-shape evidence. |
| `sub_46BAF0` | `GLimp_SpawnRenderThread` | High | Creates the three SMP events, stores the render-thread function pointer, and starts a Win32 thread using the wrapper. |
| `sub_46BB60` | `GLimp_RendererSleep` | High | Releases the WGL context, resets/sets renderer events, waits for command work, restores the context, returns the queued SMP data pointer, and signals the frontend. |
| `sub_46BBF0` | `GLimp_FrontEndSleep` | High | Waits for render completion and restores the frontend WGL context. |
| `sub_46BC20` | `GLimp_WakeRenderer` | High | Stores the command payload, releases the frontend WGL context, signals render work, and waits for the renderer to become active. |

## Wiring Notes

- `R_InitCommandBuffers` now resolves the `RB_RenderThread` startup edge through `GLimp_SpawnRenderThread`.
- `R_IssueRenderCommands` now has a named cross-thread path: frontend sleep through `GLimp_FrontEndSleep`, backend wake through `GLimp_WakeRenderer`, and direct execution through `RB_ExecuteRenderCommands`.
- `RB_RenderThread` now has a named backend wait path through `GLimp_RendererSleep`.
- `R_ShutdownCommandBuffers` now documents the null wake payload used to terminate the render thread.
- Command ID 3 is fully named on both sides: `R_AddDrawSurfCmd` emits it, and `RB_DrawSurfs` consumes it.

## Open Follow-Up

- `RB_DrawBuffer` is inlined in the retail executor rather than present as a standalone function in the Ghidra corpus, so this pass leaves it documented as executor case behavior instead of forcing a symbol.
- `R_AddAdvertisementQueryCmd` remains unresolved as a standalone retail function; the backend consumer is already named as `RB_DrawAdvertisementQueries`, but the enqueue path should be revisited with the advertisement update corpus.

## Guard Coverage

`tests/test_renderer_internal_helper_mapping_parity.py` now checks this round's command-buffer and GLimp aliases against the alias ledger, Ghidra `functions.csv`, HLIL call/state evidence, and the source-side functions in `tr_cmds.c` and `win_glimp.c`.

## Parity Estimate

- Renderer command-buffer front-end/back-end symbol mapping: before 97%, after 98%.
- Renderer SMP/GLimp threading wiring documentation: before 88%, after 96%.
- Retail behavior parity: unchanged by this mapping-only round.
