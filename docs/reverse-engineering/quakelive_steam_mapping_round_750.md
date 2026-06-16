# Quake Live Steam Mapping Round 750: Steam Browser Rules And Players Terminal Event Boundary

Date: 2026-06-16

## Scope

This round pins the native Steam browser detail rules/players terminal-event
boundary. Retail `JSBrowserDetails` treats streamed rules and players response
rows differently from terminal failed/end callbacks: response rows publish data
events without advancing the shared release counter, while failed/end callbacks
publish their terminal event and then increment the retained counter.

Focused native Steam browser rules/players terminal-event boundary confidence:
**87% -> 99%**.

overall Steam launch/runtime integration mapping confidence **94.42% -> 94.44%**

Repo-wide parity remains **99%** because this pass pins retained native
`SteamMatchmakingServers` callback wiring while keeping Quake Live-only online
services behind `QL_BUILD_ONLINE_SERVICES` and disabled by default.

## Retail Evidence

Observed promoted symbol anchors:

- `FUN_00462360` maps to `JSBrowserDetails_OnRuleResponded`
- `FUN_00462490` maps to `JSBrowserDetails_OnRulesFailed`
- `FUN_004625a0` maps to `JSBrowserDetails_OnRulesRefreshComplete`
- `FUN_004626b0` maps to `JSBrowserDetails_OnPlayerResponded`
- `FUN_00462830` maps to `JSBrowserDetails_OnPlayersFailed`
- `FUN_00462940` maps to `JSBrowserDetails_OnPlayersRefreshComplete`

Observed import anchor:

- `STEAM_API.DLL!SteamMatchmakingServers @ 0015928c`

Observed Binary Ninja HLIL anchors:

```text
0046245d  sub_4f3260(arg1, arg1 + 0x14, sub_4d9220("servers.rules.%s.response"), &var_20)
0046255d  sub_4f3260(arg1, arg1 + 0x14, sub_4d9220("servers.rules.%s.failed"), &var_20)
00462562  *(arg1 + 0x54) += 1
0046256c  if (*(arg1 + 0x54) == 3)
0046266d  sub_4f3260(arg1, arg1 + 0x14, sub_4d9220("servers.rules.%s.end"), &var_20)
00462672  *(arg1 + 0x54) += 1
0046267c  if (*(arg1 + 0x54) == 3)
004627fc  sub_4f3260(arg1, arg1 + 0x10, sub_4d9220("servers.players.%s.response"), &var_20)
004628fd  sub_4f3260(arg1, arg1 + 0x10, sub_4d9220("servers.players.%s.failed"), &var_20)
00462902  *(arg1 + 0x50) += 1
0046290f  if (*(arg1 + 0x50) == 3)
00462a0d  sub_4f3260(arg1, arg1 + 0x10, sub_4d9220("servers.players.%s.end"), &var_20)
00462a12  *(arg1 + 0x50) += 1
00462a1f  if (*(arg1 + 0x50) == 3)
```

Observed vtable anchors:

```text
00532b18  struct ISteamMatchmakingPlayersResponse::JSBrowserDetails::VTable
00532b18      int32_t (* const _purecall)() = sub_4626b0
00532b1c      int32_t (* const _purecall)() = sub_462830
00532b20      int32_t (* const _purecall)() = sub_462940
00532b28  struct ISteamMatchmakingRulesResponse::JSBrowserDetails::VTable
00532b28      int32_t (__thiscall* const vFunc_0)(class Awesomium::JSArray* arg1, int32_t arg2, int32_t arg3) = sub_462360
00532b2c      int32_t (__fastcall* const vFunc_1)(class Awesomium::JSArray* arg1) = sub_462490
00532b30      int32_t (__fastcall* const vFunc_2)(class Awesomium::JSArray* arg1) = sub_4625a0
```

Observed facts:

- Retail rules and players response callbacks publish `servers.rules.*.response`
  and `servers.players.*.response` without incrementing the shared
  `JSBrowserDetails` completion counter.
- Retail rules failed/end callbacks publish their terminal event, then
  increment the counter at the rules callback view offset.
- Retail players failed/end callbacks publish their terminal event, then
  increment the counter at the players callback view offset.
- The delete-on-third check follows the terminal counter increment in each
  failed/end callback.

Inference:

- SRP should keep streamed rules/player response callbacks non-terminal.
- SRP should publish failed/end terminal events before advancing the retained
  channel-aware lifecycle for rules and players.

## Reconstruction

This pass is a mapping and guardrail round. The existing SRP source shape is
retained because it matches the retail callback boundary:

- `CL_SteamBrowser_NativeRuleRespondedImpl` publishes rule response rows only.
- `CL_SteamBrowser_NativePlayerRespondedImpl` publishes player response rows
  only.
- `CL_SteamBrowser_NativeRulesFailedImpl` and
  `CL_SteamBrowser_NativeRulesRefreshCompleteImpl` publish failed/end events
  and then complete `QL_STEAM_SERVER_BROWSER_DETAIL_TERMINAL_RULES`.
- `CL_SteamBrowser_NativePlayersFailedImpl` and
  `CL_SteamBrowser_NativePlayersRefreshCompleteImpl` publish failed/end events
  and then complete `QL_STEAM_SERVER_BROWSER_DETAIL_TERMINAL_PLAYERS`.

The static parity gate now protects this ordering and prevents streamed
response callbacks from being treated as terminal completions.

## Tests

`tests/test_platform_services.py` now pins:

- the six rules/player callback alias and Ghidra function rows;
- the rules/player vtable rows for response, failed, and refresh-complete
  callbacks;
- the retail HLIL distinction between streamed response events and terminal
  failed/end counter increments;
- the SRP source event-name formatter and response builders;
- the non-terminal source shape for streamed rule/player responses;
- the publish-before-complete ordering for rules and players failed/end
  terminal callbacks.

## Validation

Completed for this pass:

- `python -m tabnanny tests/test_platform_services.py`
  - Passed.
- `python -m pytest -q tests/test_platform_services.py -k steam_browser_rules_players_terminal_event_boundary_round_750 --tb=short`
  - `1 passed, 287 deselected in 0.13s`
- `python -m pytest -q tests/test_platform_services.py -k steamworks --tb=short`
  - `22 passed, 266 deselected in 2.17s`
- `python -m pytest -q tests/test_steamworks_harness.py --tb=short`
  - `208 passed in 1.52s`
- `python -m pytest -q tests/test_platform_services.py --tb=short`
  - `288 passed in 27.30s`
- `git diff --check`
  - Passed; Git reported existing LF-to-CRLF working-copy warnings only.
