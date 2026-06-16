# Quake Live Steam Mapping Round 741: Steam Browser Owner Completion Guard

Date: 2026-06-16

## Scope

This round pins the native `SteamMatchmakingServers` browser owner completion
guard in SRP's opt-in Steamworks compatibility lane. The retained owner wraps
the live Steam server-list request handle used by the browser refresh path.
Retail Quake Live publishes the refresh-complete event from the browser object
after the native callback; SRP also has to protect against duplicate or stale
native callbacks because the request owner is reconstructed in open source
instead of being the retail object body.

Focused native Steam browser owner completion guard confidence:
**86% -> 99%**.

overall Steam launch/runtime integration mapping confidence **94.36% -> 94.38%**

Repo-wide parity remains **99%** because this pass tightens a retained
Steamworks compatibility wrapper without enabling live Steam behavior by
default or changing the strict-retail Windows replacement score.

## Retail Evidence

Observed promoted symbol anchors:

- `FUN_00462e60` maps to `JSBrowser_OnRefreshComplete`
- `FUN_00462e80` maps to `SteamBrowser_RefreshList`
- `FUN_00462eb0` maps to `JSBrowser_RequestServers`
- `FUN_00463090` maps to `SteamBrowser_RequestServers`

Observed Ghidra import anchor:

- `STEAM_API.DLL!SteamMatchmakingServers @ 0015928c`

Observed Binary Ninja HLIL anchors:

```text
00462e67  *(arg1 + 4) = 0
00462e73  return sub_4f3260(esi, edi, "servers.refresh.end", nullptr)
00462e8b  if (*(esi + 8) != 0)
00462e9e      (*(*eax_1 + 0x24))(*(esi + 8))
00462eca  if (*(arg1 + 4) == 0)
00462eed          *(arg1 + 8) = 0
00463058      result = sub_4f3260(arg1, edi_1, "servers.refresh.start", nullptr)
```

Observed facts:

- Retail `SteamBrowser_RefreshList` refreshes the retained request handle
  through `SteamMatchmakingServers + 0x24` only when the handle slot is live.
- Retail `JSBrowser_RequestServers` refuses to start a new native list request
  while the active flag is set.
- Retail `JSBrowser_RequestServers` releases the previous handle through
  `SteamMatchmakingServers + 0x18` before storing a replacement request.
- Retail `JSBrowser_OnRefreshComplete` clears the active flag and publishes
  `servers.refresh.end`.

Inference:

- SRP's owner wrapper should complete only when the owner is currently active.
  A duplicate native `RefreshComplete` callback with the same retained request
  handle should not publish a second browser refresh-end event.
- Completion should leave the request handle in place until the next request
  replaces it or shutdown releases it, matching the existing retained owner
  lifecycle.

## Reconstruction

`QL_Steamworks_CompleteServerBrowserOwnerRequest` now rejects non-active
owners before clearing `refreshActive`. The request handle remains owned by the
browser owner; completion marks the refresh idle but does not release or clear
the handle.

`CL_SteamBrowser_CompleteNativeRefresh` now checks the completion result before
clearing the client-side native refresh state and publishing
`servers.refresh.end`. This prevents duplicate or stale
`ISteamMatchmakingServerListResponse::RefreshComplete` callbacks from sending
extra browser events after the owner has already transitioned idle.

The native callback still validates `self` and the request handle before
calling the completion helper.

## Tests

`tests/test_steamworks_harness.py` now proves:

- completing an idle owner returns false and leaves it idle;
- completing a live owner returns true, clears `refreshActive`, and keeps the
  request handle;
- completing the same owner a second time returns false without clearing the
  retained request handle.

`tests/test_platform_services.py` now pins the retail HLIL rows, source guard
shape, client publish-once gate, harness assertions, this mapping note, and
the implementation-plan entry.

## Validation

Completed for this pass:

- `python -m pytest -q tests/test_steamworks_harness.py -k server_browser_owner_reconstructs_retail_refresh_lifecycle --tb=short`
  - `2 passed, 206 deselected in 2.99s`
- `python -m pytest -q tests/test_platform_services.py -k steam_browser_owner_completion_guard_round_741 --tb=short`
  - `1 passed, 279 deselected in 21.34s`
- `python -m pytest -q tests/test_steamworks_harness.py --tb=short`
  - `208 passed in 1.24s`
- `python -m pytest -q tests/test_platform_services.py -k steamworks --tb=short`
  - `22 passed, 258 deselected in 2.53s`
- `python -m pytest -q tests/test_platform_services.py --tb=short`
  - `280 passed in 11.28s`
- `git diff --check`
  - Passed; Git reported only existing LF-to-CRLF working-copy warnings.
