# Quake Live Steam Mapping Round 705: Server Browser Row Layout Guards

Date: 2026-06-16

## Scope

This pass rechecked the Steam server-browser row projection that feeds the
Awesomium-era JavaScript events reconstructed as `JSBrowser_OnServerResponded`
and `JSBrowserDetails_OnServerResponded`. The source already had a practical
`gameserveritem_t` mirror for tests and compatibility adapters, but the final
Steam ID field still depended on host `CSteamID` alignment instead of the exact
retail byte layout observed in the callbacks.

Focused parity estimate: **before 90% -> after 99%** for focused Steam
server-browser row layout source-shape confidence. Overall Steam launch/runtime integration mapping confidence moves from **93.92% -> 93.94%**.
Repo-wide parity remains **99%** because this pass clarifies opt-in Steamworks
wiring without changing the strict-retail Windows replacement score and does not enable live Steam behavior by default.

## Evidence

Observed Ghidra and import facts:

- `functions.csv` preserves `FUN_00461f10,00461f10,92,0,unknown` for the
  fallback address formatter now tracked as `SteamBrowser_FormatServerListFallbackName`.
- `functions.csv` preserves `FUN_00461fe0,00461fe0,863,0,unknown` for
  `JSBrowserDetails_OnServerResponded`.
- `functions.csv` preserves `FUN_00462a50,00462a50,860,0,unknown` for
  `JSBrowser_OnServerResponded`.
- `imports.txt` confirms this lane owns the `SteamMatchmakingServers` and
  `SteamUtils` imports.
- `references/analysis/quakelive_symbol_aliases.json` maps the promoted
  `FUN_00461f10`, `FUN_00461fe0`, and `FUN_00462a50` names, plus their
  `sub_*` spellings, to the server-browser aliases above.

Observed Binary Ninja HLIL facts:

- `SteamBrowser_FormatServerListFallbackName` emits the fallback
  `%u.%u.%u.%u:%i` address string.
- `JSBrowserDetails_OnServerResponded` rejects rows whose app ID at `0x90` does
  not match the expected Quake Live app.
- The details payload reads `numPlayers`, `maxPlayers`, `map`, `botPlayers`,
  password, secure, and the split Steam ID words from the raw row.
- The detail callback reads the Steam ID high dword at `0x170` and the low
  dword at `0x16c`, then formats `steam_id` as `%u_%u`.
- `JSBrowser_OnServerResponded` obtains a fresh row through the
  `SteamMatchmakingServers` vtable slot and repeats the same `0x90`,
  `0x16c`, and `0x170` layout expectations.
- The data-section strings around `data_53293c..data_5329c4` preserve the
  fallback address format, detail-response event name, `steam_id`, `%u_%u`,
  `botPlayers`, `maxPlayers`, and `numPlayers` names used by the callbacks.

Inference: the raw server-browser row should be pinned as the retail 32-bit
Steamworks layout, not as a host-aligned SDK struct. The observed final Steam ID
words prove that source needs explicit `steamIdLow` and `steamIdHigh` dwords at
`0x16c` and `0x170`; allowing a host `CSteamID` member to align itself can move
the low word to `0x170` on non-retail layouts.

## Source Reconstruction

`src/common/platform/platform_steamworks.c` now names the recovered raw row
offsets, including:

- `QL_STEAM_GAMESERVERITEM_CONNECTION_PORT_OFFSET 0x00`
- `QL_STEAM_GAMESERVERITEM_APP_ID_OFFSET 0x90`
- `QL_STEAM_GAMESERVERITEM_STEAM_ID_LOW_OFFSET 0x16c`
- `QL_STEAM_GAMESERVERITEM_STEAM_ID_HIGH_OFFSET 0x170`
- `QL_STEAM_GAMESERVERITEM_SIZE 0x174`

The internal `ql_steam_gameserveritem_raw_t` mirror now stores the Steam ID as
two explicit `uint32_t` words, with `QL_STEAM_GAMESERVERITEM_STEAM_ID_LOW_OFFSET`
anchoring the retail low dword. Local compile-time guards check the observed
offsets and the full `0x174` row size, and
`QL_Steamworks_CopyServerListDetails` reconstructs the public `CSteamID` value
from `(high << 32) | low` before projecting the row into the compatibility
server-browser item.

`tests/steamworks_harness.c` mirrors the same low/high word split so the mock
server-browser detail row exercises the reconstructed projection instead of a
host-aligned SDK convenience field.

No Steam server query, live Steamworks initialization, JavaScript event, or
online-service policy changed in this pass.

## Validation

Completed for this pass:

- `python -m pytest -q tests/test_platform_services.py -k "steam_server_browser_gameserveritem_layout_round_705 or steam_matchmaking_servers_slot_constants_round_696 or steam_browser_detail_datasource_helper_aliases_track_retail_reference_rows" --tb=short` - 3 passed, 241 deselected.
- `python -m pytest -q tests/test_steamworks_harness.py::test_server_browser_detail_reader_projects_retail_gameserveritem_row tests/test_steamworks_harness.py::test_server_browser_ping_response_projection_matches_retail_jsbrowserdetails_payload_shape --tb=short` - 4 passed.
- `python -m pytest -q tests/test_steamworks_harness.py --tb=short` - 132 passed.
- `python -m pytest -q tests/test_platform_services.py --tb=short` - 243 passed, 1 failed because the pre-existing ZMQ Round 698 gate references missing `docs/reverse-engineering/quakelive_steam_mapping_round_698.md`.
- `git diff --check` - passed with existing LF-to-CRLF working-copy warnings only.
