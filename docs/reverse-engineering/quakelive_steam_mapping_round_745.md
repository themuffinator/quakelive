# Quake Live Steam Mapping Round 745: Steam Browser Detail Terminal Channel Ownership

Date: 2026-06-16

## Scope

This round pins native `SteamMatchmakingServers` detail-request terminal
ownership in SRP's opt-in Steamworks compatibility lane. Retail
`JSBrowserDetails_RequestServerDetails` issues three native detail queries from
one retained object: ping, rules, and players. SRP already reconstructed the
three callback views and the release-after-three lifecycle, but the shared
completion helper only counted terminal callbacks. This pass records the
terminal channel that actually completed so duplicate rules or players terminal
callbacks cannot consume another channel's release slot.

Focused native Steam browser detail terminal-channel ownership confidence:
**84% -> 99%**.

overall Steam launch/runtime integration mapping confidence **94.38% -> 94.40%**

Repo-wide parity remains **99%** because this pass tightens a retained native
Steam browser wrapper while keeping Quake Live-only online services behind
`QL_BUILD_ONLINE_SERVICES` and disabled by default.

## Retail Evidence

Observed promoted symbol anchors:

- `FUN_00461f70` maps to `JSBrowserDetails_RequestServerDetails`
- `FUN_004630b0` maps to `SteamBrowser_RequestServerDetails`
- `FUN_00462eb0` maps to `JSBrowser_RequestServers`

Observed Ghidra import anchor:

- `STEAM_API.DLL!SteamMatchmakingServers @ 0015928c`

Observed Binary Ninja HLIL anchors:

```text
00461fab  (*(*SteamMatchmakingServers() + 0x34))(arg2, arg3, arg1 + 8)
00461fbd  (*(*SteamMatchmakingServers() + 0x3c))(arg2, arg3, arg1)
00461fd8  return (*(*SteamMatchmakingServers() + 0x38))(arg2, arg3, arg1 + 4)
004630b0    int32_t sub_4630b0(int32_t arg1, int32_t arg2)
004630f3  return sub_461f70(eax, arg1, arg2)
```

Observed facts:

- Retail calls three separate `ISteamMatchmakingServers` detail-query vtable
  slots from `JSBrowserDetails_RequestServerDetails`.
- The response object offsets are distinct: rules at the base object, players
  at `base + 4`, and ping at `base + 8`.
- SRP's native client wrapper mirrors those three views with separate ping,
  rules, and players callback structs before forwarding terminal callbacks to
  a shared request lifecycle.

Inference:

- Because retail owns three separate native callback views, SRP should model
  terminal completion as three unique channels rather than a raw count.
- The legacy sequential callback API is still useful for tests and older
  harness paths, but it should map through ping, rules, then players channel
  bits so the canonical lifecycle state remains channel-aware.

## Reconstruction

`platform_steamworks.h` now names the terminal-channel bit set:

- `QL_STEAM_SERVER_BROWSER_DETAIL_TERMINAL_PING`
- `QL_STEAM_SERVER_BROWSER_DETAIL_TERMINAL_RULES`
- `QL_STEAM_SERVER_BROWSER_DETAIL_TERMINAL_PLAYERS`
- `QL_STEAM_SERVER_BROWSER_DETAIL_TERMINAL_ALL`

`ql_steam_server_browser_detail_lifecycle_t` now carries
`completedTerminalChannels` beside the retained `completedCallbacks` field.
`QL_Steamworks_InitServerBrowserDetailLifecycle` clears both values when a
detail request starts.

`QL_Steamworks_CompleteServerBrowserDetailTerminal` is the new canonical
completion path. It accepts only one named terminal channel, rejects duplicate
terminal bits, updates the legacy count from the bit set, and marks release
ready only after all three channels have completed.

`QL_Steamworks_CompleteServerBrowserDetailCallback` remains as a compatibility
entry point, but it now delegates to the next missing terminal channel.
`QL_Steamworks_CompleteServerBrowserDetailRequestTerminal` applies the same
channel ownership to the retained request bundle and clears the native query
handles only after all three channels are present.

`CL_SteamBrowser_CompleteNativeDetailTerminal` now receives the terminal
channel from the concrete native callback path:

- ping success and ping failure use the ping terminal channel;
- rules failure and rules refresh-complete use the rules terminal channel;
- players failure and players refresh-complete use the players terminal
  channel.

## Tests

`tests/test_steamworks_harness.py` now proves:

- disabled builds clear `completedTerminalChannels` through the same fail-closed
  stubs as the rest of the Steamworks wrapper;
- the legacy sequential callback path still releases on the third completion
  while filling ping, rules, and players channel bits;
- the canonical channel-aware lifecycle rejects duplicate and invalid terminal
  channels;
- the retained request bundle stays active after duplicate terminal callbacks
  and releases only when ping, rules, and players have all completed.

`tests/test_platform_services.py` pins the retail HLIL rows, the named channel
bit definitions, lifecycle/request source shape, client callback wiring,
harness exports, this mapping note, and the implementation-plan entry.

## Validation

Completed for this pass:

- `python -m tabnanny tests/test_platform_services.py tests/test_steamworks_harness.py`
  - Passed.
- `python -m pytest -q tests/test_steamworks_harness.py -k "server_browser_detail_lifecycle_reconstructs_retail_three_callback_release_counter or server_browser_detail_request_owner_reconstructs_retail_response_views_and_release" --tb=short`
  - `4 passed, 204 deselected in 2.64s`
- `python -m pytest -q tests/test_platform_services.py -k steam_browser_detail_terminal_channels_round_745 --tb=short`
  - `1 passed, 283 deselected in 0.13s`
- `python -m pytest -q tests/test_steamworks_harness.py --tb=short`
  - `208 passed in 1.39s`
- `python -m pytest -q tests/test_platform_services.py -k steamworks --tb=short`
  - `22 passed, 262 deselected in 2.06s`
- `python -m pytest -q tests/test_platform_services.py --tb=short`
  - `284 passed in 17.43s`
- `git diff --check`
  - Passed; Git reported existing LF-to-CRLF working-copy warnings only.
