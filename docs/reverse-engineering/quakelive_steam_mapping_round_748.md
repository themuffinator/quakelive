# Quake Live Steam Mapping Round 748: Steam Browser Ping Response Filtered Completion

Date: 2026-06-16

## Scope

This round pins the native Steam browser detail ping-response completion
boundary. Retail `JSBrowserDetails_OnServerResponded` filters the
`gameserveritem_t` response by the active Steam app id before publishing
`servers.details.<ip>_<port>.response` and incrementing the retained
`JSBrowserDetails` terminal counter. Retail `JSBrowserDetails_OnServerFailedToRespond`
uses a separate failed terminal callback that increments the same counter
without a response payload.

Focused native Steam browser ping response filtered-completion confidence:
**86% -> 99%**.

overall Steam launch/runtime integration mapping confidence **94.40% -> 94.42%**

Repo-wide parity remains **99%** because this pass pins a retained native
Steam browser callback boundary without enabling live Steam behavior by default
or changing the strict-retail Windows replacement score.

## Retail Evidence

Observed promoted symbol anchors:

- `FUN_00461fe0` maps to `JSBrowserDetails_OnServerResponded`
- `FUN_00462340` maps to `JSBrowserDetails_OnServerFailedToRespond`
- `FUN_00461f70` maps to `JSBrowserDetails_RequestServerDetails`

Observed Ghidra import anchors:

- `STEAM_API.DLL!SteamUtils @ 0015914c`
- `STEAM_API.DLL!SteamMatchmakingServers @ 0015928c`

Observed Binary Ninja HLIL anchors:

```text
00461fe0    struct _EXCEPTION_REGISTRATION_RECORD** __thiscall sub_461fe0
00462024      result = (*(*SteamUtils(data_584520 ^ &__saved_ebp) + 0x24))()
0046202c      if (*(arg2 + 0x90) == result)
004622ff          sub_4f3260(arg2, arg1, sub_4d9220("servers.details.%u_%u.response"), &var_20)
00462304          *(arg1 + 0x4c) += 1
00462311          if (*(arg1 + 0x4c) == 3)
00462340    void* __fastcall sub_462340(void* arg1)
00462340  *(arg1 + 0x4c) += 1
```

Observed vtable anchors:

```text
00532b0c  struct ISteamMatchmakingPingResponse::JSBrowserDetails::VTable
00532b0c      int32_t (* const _purecall)() = sub_461fe0
00532b10      int32_t (* const _purecall)() = sub_462340
```

Observed facts:

- Retail `JSBrowserDetails_OnServerResponded` reads the current app id through
  `SteamUtils + 0x24`.
- The response callback publishes `servers.details.%u_%u.response` only after
  the raw server item app id equals the current app id.
- The same app-id-matched branch increments the retained terminal counter and
  deletes the detail object when the counter reaches three.
- Retail `JSBrowserDetails_OnServerFailedToRespond` has no payload filter and
  increments the retained counter directly.

Inference:

- SRP's `QL_Steamworks_ReadServerBrowserPingResponseForApp` app-id filter is
  the source-owned equivalent of the retail `SteamUtils + 0x24` check.
- SRP should keep `CL_SteamBrowser_CompleteNativeDetailTerminal(...PING)` in
  the successful app-filtered response branch for `ServerResponded`, while
  retaining the unconditional ping terminal completion in the failed callback.

## Reconstruction

This pass is a mapping and guardrail round. The existing SRP source shape is
retained because it matches the retail control-flow boundary:

```c
if ( QL_Steamworks_ReadServerBrowserPingResponseForApp( serverDetails, detail->appId, &response ) ) {
	CL_SteamBrowser_PublishNativeServerResponse( &response );
	CL_SteamBrowser_CompleteNativeDetailTerminal( detail, QL_STEAM_SERVER_BROWSER_DETAIL_TERMINAL_PING );
}
```

`CL_SteamBrowser_NativePingFailedImpl` remains the failed-terminal path:

```c
CL_SteamBrowser_CompleteNativeDetailTerminal( CL_SteamBrowser_NativeDetailFromPing( self ), QL_STEAM_SERVER_BROWSER_DETAIL_TERMINAL_PING );
```

The new static evidence gate prevents future refactors from moving the
successful ping terminal completion outside the app-filtered publish branch.

## Tests

`tests/test_platform_services.py` now pins:

- the `JSBrowserDetails_OnServerResponded` and
  `JSBrowserDetails_OnServerFailedToRespond` alias/function rows;
- the `SteamUtils` and `SteamMatchmakingServers` import anchors;
- the app-id filter, publish event, counter increment, and delete-on-third
  HLIL rows;
- the ping-response vtable entries;
- the SRP `QL_Steamworks_ReadServerBrowserPingResponseForApp` app-id check;
- the filtered `CL_SteamBrowser_NativePingRespondedImpl` completion shape and
  the unconditional failed-ping terminal completion.

## Validation

Completed for this pass:

- `python -m tabnanny tests/test_platform_services.py`
  - Passed.
- `python -m pytest -q tests/test_platform_services.py -k steam_browser_ping_response_filtered_completion_round_748 --tb=short`
  - `1 passed, 285 deselected in 0.15s`
- `python -m pytest -q tests/test_platform_services.py -k steamworks --tb=short`
  - `22 passed, 264 deselected in 1.82s`
- `python -m pytest -q tests/test_steamworks_harness.py --tb=short`
  - `208 passed in 1.29s`
- `python -m pytest -q tests/test_platform_services.py --tb=short`
  - `286 passed in 16.68s`
- `git diff --check`
  - Passed; Git reported existing LF-to-CRLF working-copy warnings only.
