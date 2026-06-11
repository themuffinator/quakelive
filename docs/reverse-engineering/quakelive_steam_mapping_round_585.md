# Quake Live Steam Mapping Round 585: Stats Report Zlib Packet Inflate

Date: 2026-06-11

## Scope

This round reconstructs the missing decompression step in the client Steam
runtime frame lane that publishes server match-stat reports to the browser
event surface.

Focused retail owners:

- `SteamClient_Frame`: `sub_461d40` / `FUN_00461d40`
- zlib whole-buffer decompress helper: `sub_4fda50` / `FUN_004fda50`
- WebUI publish bridge: `sub_4f3260` / `QLWebView_PublishEvent`

## Evidence

Observed facts:

- Binary Ninja HLIL for `sub_461d40` drains SteamNetworking channel `0` after
  `SteamAPI_RunCallbacks()` and captured-voice send, then before incoming voice
  packet processing.
- The retail frame body allocates the incoming packet with `malloc(var_a8)`,
  reads it through the SteamNetworking receive slot, allocates a `0x100000`
  output buffer, and calls `sub_4fda50(esi_1, &var_b0, edi_1, var_ac)`.
- On successful decompress, the same retail body builds a JS string payload and
  publishes `"game.stats.report"` through `sub_4f3260`.
- Ghidra `functions.csv` records `FUN_004fda50,004fda50,175,0,unknown`.
- Binary Ninja HLIL for `sub_4fda50` is the standard zlib whole-buffer
  `uncompress` shape: initialize stream with version `"1.2.3"`, inflate with
  flush `4`, write the output length through `arg2`, and end the stream.

Inferred mapping:

- `0x004FDA50`: `zlib_uncompress`.
- `0x004FDA50` is support-library code, but naming it as `zlib_uncompress`
  matters because it explains the Steam stats-report packet format.
- Source should not publish the raw Steam P2P packet bytes. The retained source
  should inflate the packet into a retail-sized scratch buffer, then queue the
  existing capped browser-event payload.
- The source wrapper uses the already bundled qcommon zlib implementation. Its
  zlib version string differs from retail's linked `"1.2.3"` helper, but the
  zlib format and whole-buffer `inflate(..., Z_FINISH)` behavior are the
  source-relevant contract.

## Reconstruction

Implemented in `src/code/qcommon/unzip.c` and `src/code/qcommon/unzip.h`:

- Added `QZ_Uncompress`, a small exported wrapper around the existing bundled
  zlib `inflateInit2`, `inflate(..., Z_FINISH)`, and `inflateEnd` path.

Implemented in `src/code/client/cl_main.c`:

- Included `../qcommon/unzip.h`.
- Added `CL_STEAM_STATS_REPORT_DECOMPRESSED_BYTES` as `0x100000`, matching the
  retail scratch buffer.
- Changed `CL_Steam_ProcessStatsReportPackets` so channel-0 Steam packets are
  decompressed through `QZ_Uncompress` before publishing
  `"game.stats.report"`.
- Preserved the existing `CL_STEAM_BROWSER_EVENT_PAYLOAD_LENGTH` queue cap and
  explicit NUL termination before dispatching the browser event.

Updated `references/analysis/quakelive_symbol_aliases.json`:

- `FUN_004fda50 -> zlib_uncompress`
- `sub_4FDA50 -> zlib_uncompress`
- `sub_4fda50 -> zlib_uncompress`

Strengthened `tests/test_platform_services.py`:

- Added a focused gate that ties the Steam frame HLIL packet lane, zlib helper
  HLIL, alias map, Ghidra row, qcommon wrapper, and client source path together.

## Confidence

- High that the retail channel-0 stats-report packet is zlib-compressed:
  independent frame HLIL, zlib helper HLIL, and Ghidra row evidence agree.
- High that the source now reconstructs the behaviorally important step:
  packet receive, zlib inflate, browser-event publish, and retained payload cap
  are pinned together.
- Medium that the exact retail zlib version should be reconstructed as a
  source dependency: the source uses the bundled qcommon zlib API rather than
  introducing a new runtime dependency only to match the retail version string.

## Validation

Completed validation:

```text
python -c "import json; json.load(open(r'references/analysis/quakelive_symbol_aliases.json', encoding='utf-8'))"
python -m pytest tests/test_platform_services.py::test_client_stats_report_packet_lane_inflates_retail_zlib_payload -q --tb=short
1 passed
python -m pytest tests/test_platform_services.py::test_client_steam_callback_owner_reconstructs_retail_frame_pump_and_lifecycle tests/test_client_sound_voice_parity.py::test_client_steam_voice_frame_reconstructs_retail_transport_path -q --tb=short
2 passed
python -m pytest tests/test_platform_services.py -q --tb=short
146 passed
git diff --check -- src/code/client/cl_main.c src/code/qcommon/unzip.c src/code/qcommon/unzip.h references/analysis/quakelive_symbol_aliases.json tests/test_platform_services.py docs/reverse-engineering/quakelive_steam_mapping_round_585.md IMPLEMENTATION_PLAN.md
clean except Git LF-to-CRLF working-copy notices
powershell -NoProfile -ExecutionPolicy Bypass -File .vscode\build.ps1 -Configuration Debug -Platform x86 -Targets quakelive_steam
Build succeeded; 0 warnings; 0 errors
```

No game launch is required for this static source reconstruction and mapping
round.

## Parity Estimate

- Focused stats-report packet payload reconstruction confidence:
  **before 72% -> after 98%**.
- Focused `SteamClient_Frame` channel-0 packet lane confidence:
  **before 94% -> after 98%**.
- Overall Steam launch/runtime integration mapping confidence: **92.95% -> 93.05%**.
