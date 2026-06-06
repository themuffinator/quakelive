# Botlib ROQ Cinematic Continuation Boundary Mapping - 2026-06-06

## Scope

This pass extends the botlib structure-tail boundary check beyond the first ROQ
helper slab and into the adjacent retail cinematic decode/control range
`0x004B1010..0x004B3510`. The goal is still ownership classification: these
rows live immediately after the botlib/cgame boundary work, but they belong to
client cinematic playback in `cl_cin.c`, not to botlib parser, structure, or AI
source.

No C source body change was needed.

## Evidence

- `references/analysis/quakelive_symbol_aliases.json`
- `references/reverse-engineering/ghidra/quakelive_steam/functions.csv`
- `references/hlil/quakelive/quakelive_steam.exe/quakelive_steam.exe_hlil_split/quakelive_steam.exe_hlil_part04.txt`
- `src/code/client/cl_cin.c`
- `tests/test_botlib_structure_tail_cgame_boundary_parity.py`

## Observed Rows

| Address | Classification |
| --- | --- |
| `0x004B1010` | `yuv_to_rgb` |
| `0x004B1080` | `yuv_to_rgb24` |
| `0x004B1100` | `decodeCodeBook` |
| `0x004B1DA0` | `recurseQuad` |
| `0x004B1EB0` | `setupQuad` |
| `0x004B1FC0` | `readQuadInfo` |
| `0x004B2110` | `RoQPrepMcomp` |
| `0x004B21C0` | `initRoQ` |
| `0x004B2220` | `RoQ_init` |
| `0x004B2300` | `RoQShutdown` |
| `0x004B2400` | `CIN_StopCinematic` |
| `0x004B2480` | `CIN_SetExtents` |
| `0x004B24D0` | `CIN_DrawCinematic` |
| `0x004B2790` | `SCR_DrawCinematic` |
| `0x004B27B0` | `SCR_StopCinematic` |
| `0x004B27E0` | `CIN_UploadCinematic` |
| `0x004B2890` | `CIN_CloseAllVideos` |
| `0x004B2910` | `RoQReset` |
| `0x004B29D0` | `RoQInterrupt` |
| `0x004B2F40` | `CIN_RunCinematic` |
| `0x004B3160` | `CIN_PlayCinematic` |
| `0x004B3510` | `SCR_RunCinematic` |

## Boundary Finding

The post-`ReadStructure` retail range now has a longer continuous
botlib-boundary classification:

- `0x004AE830..0x004AECD0` contains the final promoted botlib structure reader
  owners.
- `0x004AF050..0x004AF820` contains adjacent non-botlib C++/client rows plus
  cgame snapshot/configstring/server-command owners.
- `0x004B0610..0x004B0F60` contains client cgame command/timing/rendering
  owners plus the first ROQ helper slab.
- `0x004B1010..0x004B3510` contains the remaining ROQ codebook, motion
  compensation, streamed interrupt, and cinematic control owners.

That keeps the final botlib structure-reader region from absorbing the
client-side cinematic playback implementation that follows it in the retail
binary.

## Source Reconstruction Notes

The new gate adds direct source anchors for the two largest previously thin
spots in this range:

- `decodeCodeBook` is pinned by its `roq_flags` defaulting and split, 2/4/1
  sample-depth branches, YUV conversion calls, and `VQ2TO4` / `VQ2TO2`
  expansion paths.
- `RoQInterrupt` is pinned by streamed-frame reads, EOF/loop handling, `ROQ_*`
  dispatch cases, codebook decode, mono/stereo audio decode, quad-info setup,
  packet/header parsing, oversized-frame guard, in-memory redump handling, and
  `RoQPlayed` advancement.

The surrounding smaller owners are tied to RGB conversion, quad setup, motion
compensation table preparation, stream initialization/reset/shutdown, extents,
draw/upload calls, and the `SCR_*` wrappers that drive the global cinematic
handle.

## Coverage Result

`tests/test_botlib_structure_tail_cgame_boundary_parity.py` now pins:

- promoted aliases and Ghidra row sizes for the ROQ cinematic continuation;
- source anchors in `yuv_to_rgb`, `yuv_to_rgb24`, `decodeCodeBook`,
  `recurseQuad`, `setupQuad`, `readQuadInfo`, `RoQPrepMcomp`, `initRoQ`,
  `RoQ_init`, `RoQShutdown`, `RoQReset`, `RoQInterrupt`, and the public
  `CIN_*` / `SCR_*` wrappers;
- HLIL signatures, constants, calls, and branch anchors for the continuation
  range from `0x004B1010` through `0x004B3510`;
- a full promoted-alias coverage scan confirming no aliases in
  `0x004A83C0..0x004B3510` lack direct `test_botlib_*.py` coverage.

## Parity Estimate

- Focused ROQ cinematic continuation boundary classification:
  **before 68% -> after 99%**
- Focused `decodeCodeBook` / `RoQInterrupt` source and HLIL coverage inside
  botlib boundary gates:
  **before 0% -> after 98%**
- Overall botlib plus adjacent client/cinematic wiring:
  **before 86% -> after 87%**

No runtime launch was needed. The evidence is static and covered by committed
HLIL, Ghidra row data, the alias map, and source bodies.
