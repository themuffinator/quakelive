# Quake Live Steam Mapping Round 685: Client SteamUserStats Slot Constants

Date: 2026-06-16

## Scope

This pass rechecked the retail client `SteamUserStats` value/readback wrappers
and named the remaining client stats vtable slots used by SRP's production
Steamworks shim. Earlier rounds reconstructed stats callback publication,
readback wrappers, float handling, and the `stats_clear` command. This round
closes the source-shape gap where those wrappers still carried raw `0x30`
through `0x54` vtable indices.

Focused parity estimate: **before 90% -> after 99%** for client SteamUserStats
value ABI source-shape confidence. Overall Steam launch/runtime integration mapping confidence moves from **93.72% -> 93.74%**. Repo-wide parity remains
**99%** because this pass clarifies the opt-in Steamworks lane without changing
the strict-retail Windows replacement score.

## Evidence

| Retail symbol | Current alias | Observed slot evidence |
| --- | --- | --- |
| `FUN_0045ffd0` / `sub_45ffd0` | `SteamCallbacks_OnUserStatsReceived` | Builds the user stats and achievements browser payload using client `SteamUserStats` get-float, get-int, achievement display attribute, and get-achievement slots. |
| `sub_460520` | `CL_Steam_ClearStats_f` | The retained `stats_clear` command calls `SteamUserStats + 0x54` with achievements enabled. |
| `FUN_004613a0` / `sub_4613a0` | `SteamCallbacks_Init` | Registers `UserStatsReceived_t` with callback id `0x44d`. |

Observed facts:

- `functions.csv` contains the mapped callback owner at `0045ffd0` and the
  callback initialization owner at `004613a0`.
- `imports.txt` confirms `STEAM_API.DLL!SteamUserStats` and
  `SteamAPI_RegisterCallback`.
- `analysis_symbols.txt` contains the
  `CCallback<class_SteamCallbacks,struct_UserStatsReceived_t,0>::vftable`
  anchor.
- Binary Ninja HLIL shows get-float, get-int, display-attribute,
  get-achievement, and reset dispatches through `SteamUserStats + 0x44`,
  `SteamUserStats + 0x48`, `SteamUserStats + 0x30`,
  `SteamUserStats + 0x50`, and `SteamUserStats + 0x54`.
- SRP's Steamworks harness exposes the same mock `SteamUserStats` vtable
  layout; Round 709 later promoted that mock mirror from raw offsets to named
  harness-local constants.

Inference: the public client stats wrappers should continue resolving the same
vtable entries, but the production shim should name the client stats ABI slots
so the client callback, web publication, and command wiring can reason about
the interface directly.

## Source Reconstruction

SRP now names the client `SteamUserStats` slots:

- `QL_STEAM_USERSTATS_GET_ACHIEVEMENT_DISPLAY_ATTRIBUTE_SLOT`
- `QL_STEAM_USERSTATS_REQUEST_USER_STATS_SLOT`
- `QL_STEAM_USERSTATS_GET_USER_STAT_FLOAT_SLOT`
- `QL_STEAM_USERSTATS_GET_USER_STAT_INT_SLOT`
- `QL_STEAM_USERSTATS_GET_USER_ACHIEVEMENT_SLOT`
- `QL_STEAM_USERSTATS_RESET_ALL_STATS_SLOT`

`QL_Steamworks_ClearStats`, `QL_Steamworks_RequestUserStats`,
`QL_Steamworks_GetUserStatInt`, `QL_Steamworks_GetUserStatFloat`,
`QL_Steamworks_GetUserAchievement`, and
`QL_Steamworks_GetAchievementDisplayAttribute` now resolve through the named
slots while retaining their existing initialization checks, argument
validation, SteamID word split, default values, and disabled-build fallbacks.

This pass does not enable live Steam behavior by default. It preserves the
existing `QL_BUILD_STEAMWORKS` and default-disabled `QL_BUILD_ONLINE_SERVICES`
policy.

## Validation

Validation completed:

- `python -m pytest -q tests/test_platform_services.py -k "steam_userstats_client_value_slot_constants_round_685 or steam_clear_stats_round_375 or steam_user_stats_readback_round_382 or steam_user_stats_float_descriptor_round_383 or steam_user_stats_and_presence_callback_publications" --tb=short`
  4 passed.
- `python -m pytest -q tests/test_platform_services.py --tb=short`: 228
  passed.
- `python -m pytest -q tests/test_steamworks_harness.py --tb=short`: 132
  passed.
- `git diff --check`: passed with CRLF conversion warnings only.
