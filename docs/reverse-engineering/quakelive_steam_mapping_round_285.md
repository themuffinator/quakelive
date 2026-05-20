# Quake Live Steam Host Mapping Round 285

Date: 2026-05-20

## Scope

This client mapping round closes the next high-confidence cinematic and
browser-activation tranche in `quakelive_steam.exe`. The promoted symbols cover
the `cl_cin.c` RoQ helper island from the audio delta decoders through quad
setup, reset, shutdown, screen wrappers, and renderer upload wiring, plus the
small Awesomium activation-key helper used by the retained client browser host.

Round 284 is already occupied by renderer patch-grid helper mapping in this
worktree, so this client continuation uses round 285. No source behavior
changed.

## Evidence Used

- `references/reverse-engineering/ghidra/quakelive_steam/functions.csv`
- `references/reverse-engineering/ghidra/quakelive_steam/decompile_top_functions.c`
- `references/hlil/quakelive/quakelive_steam.exe/quakelive_steam.exe_hlil.txt`
- `references/analysis/quakelive_symbol_aliases.json`
- `src/code/client/cl_cin.c`
- `src/code/client/cl_cgame.c`
- `src/code/client/cl_main.c`
- `tests/test_platform_services.py`
- `docs/reverse-engineering/quakelive_steam_mapping_round_18.md`
- `docs/reverse-engineering/awesomium-browser-host-parity-audit-and-implementation-plan-2026-04-16.md`

## Cinematic Helper Island

The unknown block from `0x004B0A70` through `0x004B2910` lines up with the
stock `cl_cin.c` RoQ implementation:

1. `sub_4B0A70` decodes stereo RLL sound by splitting the header flag into
   left/right seeds, accumulating through the square table, and returning
   `size >> 1`, matching `RllDecodeStereoToStereo`.
2. `sub_4B0AF0` and `sub_4B0BD0` are the 32-bit block copy helpers
   `move8_32` and `blit8_32`. Their different source strides distinguish
   motion-copy from VQ source blit.
3. `sub_4B0F60`, `sub_4B1010`, and `sub_4B1080` are the YUV table and RGB
   conversion helpers. HLIL preserves the same `57.203998`, `45.363998`,
   `-11.512479`, and `-23.352479` table constants used by the source.
4. `sub_4B1DA0`, `sub_4B1EB0`, and `sub_4B1FC0` recover the quad setup chain:
   recursive quad status population, cached setup, and quad-info reads from
   the RoQ frame header.
5. `sub_4B2110`, `sub_4B21C0`, `sub_4B2220`, `sub_4B2300`, and `sub_4B2910`
   complete the RoQ prep/init/shutdown/reset owners. The observed calls to
   `CL_ScaledMilliseconds`, streamed file reset, `finished cinematic`, and
   `nextmap` handling match the source responsibilities.
6. `sub_4B2790`, `sub_4B27B0`, and `sub_4B3510` are the tiny `SCR_*`
   cinematic wrappers over the global `CL_handle`.
7. `sub_4B27E0` is the renderer-facing `CIN_UploadCinematic` hook assigned in
   `CL_InitRef`, while `sub_4B2890` is the all-handles shutdown helper used by
   hunk and client cleanup.

## Browser Activation Helper

`sub_4F2900` constructs an `Awesomium::WebKeyboardEvent` with fixed key values
`0`, `0x11`, and `0x1d0001`, then forwards it through the current web view slot
at `+0xE0` when `data_12d3050` is live. That is the native host half of
`QLWebView_InjectActivationKeyboardEvent`, which the source already routes from
`CL_WebHost_NotifyAppActivation`.

Nearby functions at `0x004F2320`, `0x004F2330`, `0x004F2380`, and
`0x004F3E30..0x004F3EC0` remain intentionally unpromoted in this round. Their
HLIL bodies look like C++ library random-state and tree-iterator support rather
than client-owned browser source.

## Promoted Symbols

| Address | Alias | Confidence | Evidence |
| --- | --- | --- | --- |
| `sub_4B0A70` | `RllDecodeStereoToStereo` | High | Stereo seed split, square-table accumulation, and `size >> 1` return match `cl_cin.c`. |
| `sub_4B0AF0` | `move8_32` | High | Copies eight rows from motion-compensated source using the caller stride for both source and destination. |
| `sub_4B0BD0` | `blit8_32` | High | Copies eight contiguous VQ source rows into a caller-strided destination. |
| `sub_4B0F60` | `ROQ_GenYUVTables` | High | Generates the same YUV conversion tables and constants as source. |
| `sub_4B1010` | `yuv_to_rgb` | High | Converts through 5:6:5 clamps and returns the packed 16-bit value. |
| `sub_4B1080` | `yuv_to_rgb24` | High | Converts and clamps to 8-bit channels, returning the 32-bit packed pixel. |
| `sub_4B1DA0` | `recurseQuad` | High | Recursively halves quad size, fills both `qStatus` buffers, and stops at the minimum quad size. |
| `sub_4B1EB0` | `setupQuad` | High | Caches offsets/sizes, calls `recurseQuad`, and null-terminates the status arrays. |
| `sub_4B1FC0` | `readQuadInfo` | High | Reads `xsize`, `ysize`, max/min size, buffer stride, and draw-size fallback fields from the RoQ header. |
| `sub_4B2110` | `RoQPrepMcomp` | High | Fills the 16x16 motion-compensation table from `normalBuffer0`, `xoff`, `yoff`, and pixel/line stride. |
| `sub_4B21C0` | `initRoQ` | High | Assigns VQ callbacks, sets four-byte samples, then generates YUV/RLL tables. |
| `sub_4B2220` | `RoQ_init` | High | Seeds start/last time, `RoQPlayed`, FPS, frame ID, frame size, and flags from the header bytes. |
| `sub_4B2300` | `RoQShutdown` | High | Emits `finished cinematic`, closes the streamed file, handles `nextmap`, clears `CL_handle`, and resets current handle. |
| `sub_4B2790` | `SCR_DrawCinematic` | High | Bounds-checks `CL_handle` and calls `CIN_DrawCinematic`. |
| `sub_4B27B0` | `SCR_StopCinematic` | High | Bounds-checks `CL_handle`, calls `CIN_StopCinematic`, stops sounds, and clears the handle. |
| `sub_4B27E0` | `CIN_UploadCinematic` | High | Assigned into `ri.CIN_UploadCinematic` and calls the renderer upload function with draw size, buffer, handle, and dirty flag. |
| `sub_4B2890` | `CIN_CloseAllVideos` | High | Walks the sixteen cinematic handles, logs close messages, and shuts down active videos. |
| `sub_4B2910` | `RoQReset` | High | Ends/closes/reopens the streamed file, begins read-ahead, reads 16 bytes, calls `RoQ_init`, and marks the status looped. |
| `sub_4B3510` | `SCR_RunCinematic` | High | Bounds-checks `CL_handle` and calls `CIN_RunCinematic`. |
| `sub_4F2900` | `QLWebView_InjectActivationKeyboardEvent` | High | Constructs the fixed activation keyboard event and injects it into the live Awesomium view. |

## Still Open

- `sub_4B0A50` remains a native import-table integrity check. Its behavior is
  clear enough to describe but still too synthetic for a stable source-style
  public name.
- The remaining `0x004F23xx` random-state helpers and `0x004F3Exx` tree
  helpers are tracked as runtime/library support, not browser-host ownership.
- This pass does not attempt to recover the inlined mono-audio RoQ path as a
  separate function, because retail HLIL does not expose a standalone Ghidra row
  for `RllDecodeMonoToStereo`.

## Guard Coverage

`tests/test_engine_client_command_parity.py` now checks the round 285 alias
set, validates the Ghidra function rows, anchors the key HLIL snippets, verifies
the `CL_InitRef` upload-slot assignment, and cross-checks the source owners in
`cl_cin.c`, `cl_cgame.c`, and the existing browser parity note.

## Parity Estimate

- Client cinematic helper symbol coverage: before 58%, after 96%.
- Client browser activation-helper symbol coverage: before 93%, after 96%.
- Retail behavior parity: unchanged by this mapping-only round.
