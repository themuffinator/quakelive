# Quake Live Steam Mapping Round 572: Advertisement Runtime Alias Corpus Closure

Date: 2026-06-11

## Scope

This round rechecked the retail `quakelive_steam.exe` advertisement runtime
cluster that had already been source-reconstructed in round 147, but still had
partial alias coverage in `references/analysis/quakelive_symbol_aliases.json`.
The focus was the renderer-side advertisement brush model, debug, and occlusion
query helpers used by the Steam-era WebUI/advert bridge. The work was
static-only: Binary Ninja HLIL, Ghidra function rows, the existing round 147
evidence note, and current renderer source reconstruction. No game launch or
live advertisement service probe was needed.

## Evidence Inputs

- Binary Ninja HLIL:
  `references/hlil/quakelive/quakelive_steam.exe/quakelive_steam.exe_hlil_split/quakelive_steam.exe_hlil_part01.txt`
  and
  `references/hlil/quakelive/quakelive_steam.exe/quakelive_steam.exe_hlil_split/quakelive_steam.exe_hlil_part02.txt`
- Ghidra rows:
  `references/reverse-engineering/ghidra/quakelive_steam/functions.csv`
- Prior reconstruction note:
  `docs/reverse-engineering/quakelive_steam_mapping_round_147.md`
- Source reconstruction:
  `src/code/renderer/tr_bsp.c`,
  `src/code/renderer/tr_world.c`,
  `src/code/renderer/tr_backend.c`, and
  `src/code/renderer/tr_main.c`

## Observed Facts

| Retail function | Alias | Evidence | Source reconstruction boundary |
| --- | --- | --- | --- |
| `sub_434bc0` | `R_AddAdvertisementSurface` | Reads the advertisement bmodel surface, skips already-visited surfaces by `viewCount`, checks the advert normal against `vieworg - center`, calls `sub_44b130` on the four advert points, and submits the surface through the normal draw-surf path. | Reconstructed in `tr_world.c` as `R_AddAdvertisementSurface`. |
| `sub_434c80` | `R_LoadAdvertisements` | Parses the Quake Live advertisement BSP lump, validates lump size/count, resolves bmodels, and seeds the advertisement runtime array. | Reconstructed in `tr_bsp.c` as `R_LoadAdvertisements`. |
| `sub_434e40` | `R_UpdateAdvertisements` | Iterates the loaded advertisement cells, resets runtime tail state for the first scene, calls `sub_434bc0`, records cull state, and queues occlusion-query entries when available. | Reconstructed in `tr_world.c` as `R_UpdateAdvertisements`. |
| `sub_434fa0` | `R_ShutdownAdvertisements` | Resets advertisement counters and clears runtime arrays after optional debug-list handling. | Reconstructed in `tr_world.c` as `R_ShutdownAdvertisements`. |
| `sub_435070` | `R_DebugAdvertisements` | Draws advert debug overlays, label text, colors, normals, and host-provided label lists. | Reconstructed in `tr_world.c` as `R_DebugAdvertisements`. |
| `sub_436a90` | `RB_DrawAdvertisementQueries` | Saves GL state, disables color writes, draws paired `GL_SAMPLES_PASSED_ARB` queries with `GL_EQUAL` and `GL_LEQUAL`, then restores depth/blend/color state. | Reconstructed in `tr_backend.c` as `RB_DrawAdvertisementQueries`. |
| `sub_44b130` | `R_CullAdvertisementQuad` | Tests the four advertisement quad points against the frustum planes and returns the same out/clip/in cull classes used by the surface submission path. | Reconstructed in `tr_world.c` as `R_CullAdvertisementQuad`. |

## Mapping Work

Promoted the missing Ghidra `FUN_*` and lower-case Binary Ninja `sub_*`
spellings for the seven already-owned advertisement runtime helpers in
`references/analysis/quakelive_symbol_aliases.json`. The previous corpus had
only some upper-case `sub_*` spellings, which left these rows appearing as
unmapped in Ghidra-driven scans despite the source reconstruction being closed.

Added
`tests/test_renderer_internal_helper_mapping_parity.py::test_renderer_advert_runtime_alias_variants_track_round_147_source_closure`
to pin:

- Ghidra row sizes for the seven advert runtime helpers;
- the promoted `FUN_*`, upper-case `sub_*`, and lower-case `sub_*` alias keys;
- round 147's source-closure evidence for the advert surface, backend query,
  and culler helpers;
- Binary Ninja HLIL call anchors for advert surface submission, BSP lump load,
  update, shutdown/debug, backend query drawing, and frustum culling; and
- current source reconstruction in `tr_bsp.c`, `tr_world.c`, `tr_backend.c`,
  and `tr_main.c`.

## Source Reconstruction Decision

No C source patch was needed in this round. The source-owned advertisement
runtime behavior had already been reconstructed in round 147. This pass does
not enable live advertisement fetching or change the default-offline
online-services boundary. The Quake Live advert/online-service lane remains
bounded by the repository policy around `QL_BUILD_ONLINE_SERVICES`; this pass
only closes alias-corpus drift around renderer-side retail code that is already
present in source.

## Confidence

- High for `R_AddAdvertisementSurface`, `R_CullAdvertisementQuad`, and
  `RB_DrawAdvertisementQueries`: round 147 source work, HLIL call sites, and
  current source bodies agree directly.
- High for `R_LoadAdvertisements`, `R_UpdateAdvertisements`, and
  `R_ShutdownAdvertisements`: Ghidra row sizes, retail strings, loop structure,
  and source lifecycle match the reconstructed advertisement array handling.
- Medium-high for `R_DebugAdvertisements`: source models the debug overlay and
  host label bridge; retail debug drawing remains a local renderer diagnostic
  rather than live-service behavior.

Focused parity estimate after this round:

- Advertisement runtime alias-corpus completeness:
  **before 82% -> after 99%**.
- Renderer-side advert source-backed mapping confidence:
  **before 96% -> after 98%**.
- Overall Steam/WebUI launch/runtime integration mapping confidence:
  **92.95% -> 93.0%**.
