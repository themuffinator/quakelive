# Quake Live Steam Host Mapping Round 279

Date: 2026-05-20

## Scope

This pass continued the renderer post-process and command-buffer mapping from round 278. It focused on the retail backend command executor, bloom/color-correct command emitters, and the Ghidra program/texture lifecycle helpers that wire those commands to the current `tr_backend.c` reconstruction.

No renderer source behavior changed in this round. The output is symbol promotion, evidence notes, and a focused guard test.

## Evidence Used

- `references/reverse-engineering/ghidra/quakelive_steam/functions.csv`
- `references/hlil/quakelive/quakelive_steam.exe/quakelive_steam.exe_hlil_split/quakelive_steam.exe_hlil_part01.txt`
- `references/hlil/quakelive/quakelive_steam.exe/quakelive_steam.exe_hlil_split/quakelive_steam.exe_hlil_part02.txt`
- `src/code/renderer/tr_backend.c`
- `src/code/renderer/tr_cmds.c`

## Promoted Symbols

| Address | Alias | Confidence | Evidence |
| --- | --- | --- | --- |
| `sub_437A50` | `RB_ExecuteRenderCommands` | High | Ghidra function `FUN_00437a50` walks render command IDs 1..13 and dispatches to draw-surf, swap, screenshot, post-process, text, and viewport handlers. Source has `void RB_ExecuteRenderCommands( const void *data )`. |
| `sub_437DA0` | `RBPP_ShutdownBloomResources` | High | Destroys the bloom program range through `RBPP_DestroyProgram`, deletes bloom textures/FBOs/depth buffers, and clears `r_bloomActive`. Source has `static void RBPP_ShutdownBloomResources( void )`. |
| `sub_4384A0` | `RBPP_BloomEnabled` | High | Predicate checks `RB_PostProcessEnabled`, extension/post-process state, and the bloom cvar pointer before returning 1. The same predicate guards bloom command emission and command 11 framebuffer restore. |
| `sub_4384D0` | `R_AddBloomPostProcessCommand` | High | Allocates a `0x38` command buffer with command ID `0xa`, stores bloom program handles and render targets, and is installed into the refexport tail through the jump thunk at `0x451410`. The executor dispatches command ID 10 to `RBPP_ApplyBloom`. |
| `sub_438590` | `RBPP_SetBloomUniformsFromCvars` | High | Uses the bloom predicate, binds brightpass/combine programs, clamps the bloom cvar values to non-negative floats, and writes the bright threshold, bloom saturation, scene saturation, bloom intensity, and scene intensity uniforms. |
| `sub_43CCD0` | `RBPP_DestroyColorCorrectProgram` | High | Thin wrapper around `sub_4506A0(&data_586210)`, matching `RBPP_DestroyColorCorrectProgram` calling `RBPP_DestroyProgram( &s_postProcess.colorCorrectProgram )`. |
| `sub_43CCE0` | `RBPP_ColorCorrectEnabled` | High | Predicate checks `RB_PostProcessEnabled`, extension/post-process state, and the color-correct cvar pointer before returning 1. |
| `sub_43CD10` | `R_AddColorCorrectPostProcessCommand` | High | Allocates a `0x10` command buffer with command ID `9`, stores the color-correct texture/program handles, and the executor dispatches command ID 9 to the color-correct pass. |
| `sub_43CD60` | `RBPP_SetColorCorrectUniformsFromCvars` | High | Binds the color-correct program and writes `p_gammaRecip`, `p_overbright`, and `p_contrast` uniforms from renderer cvars/state. |
| `sub_43CE50` | `RBPP_CreateColorCorrectTexture` | High | Creates the rectangle texture used by color correction, checks maximum rectangle texture size, emits the retail `Color Correct Failure` diagnostic, and disables `r_colorCorrectActive` on failure. |
| `sub_43CFE0` | `RBPP_InitColorCorrectResources` | High | Clears the color-correct program struct, loads `scripts/colorcorrect.fs` and `scripts/posteffect.vs`, resolves uniforms, creates the texture, and sets `r_colorCorrectActive`. |
| `sub_450640` | `RBPP_LoadProgram` | High | Checks shader/program availability and chains fragment load, vertex load, and program link helpers. Source has `static qboolean RBPP_LoadProgram(...)`. |
| `sub_4506A0` | `RBPP_DestroyProgram` | High | Detaches shaders, deletes the program object, deletes fragment/vertex shader objects, and clears handles. Source has `static void RBPP_DestroyProgram(...)`. |

## Wiring Notes

- Command ID 9 is the color-correct post-process pass. `sub_43CD10` emits it, and `sub_437A50` dispatches it to the color-correct executor.
- Command ID 10 is the bloom pass. `sub_4384D0` emits it, and `sub_437A50` dispatches it to `RBPP_ApplyBloom`.
- Command ID 11 remains a small bloom framebuffer restore command guarded by `RBPP_BloomEnabled`; it is related but was not promoted this round because the source-level ownership seam is less explicit.
- The color-correct lifecycle has a clean source-backed chain: load program -> resolve uniforms/create texture -> emit command -> apply pass -> destroy program.

## Open Follow-Up

- Resolve the command ID 11 framebuffer restore helper and the command ID 13 viewport/scissor helper once the surrounding command structs are documented.
- Continue tracing the refexport tail slots that call into `sub_4384D0` and the text/viewport command helpers so the command-buffer ABI can be documented as a full table.

## Guard Coverage

`tests/test_renderer_internal_helper_mapping_parity.py` now checks the round 279 aliases, confirms all Ghidra CSV-backed functions except the compiler-shaped `sub_4384D0` helper, and anchors the mapping to HLIL/source strings for the executor, bloom/color-correct command emitters, uniforms, and program lifecycle helpers.

## Parity Estimate

- Renderer post-process symbol mapping: before 94%, after 97%.
- Renderer command-buffer wiring documentation: before 90%, after 94%.
- Retail behavior parity: unchanged by this mapping-only round.
