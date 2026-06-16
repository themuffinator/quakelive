# Quake Live Steam Mapping Round 713: Mock SteamGameServerStats Slot Mirroring

Date: 2026-06-16

## Scope

This pass rechecked the SteamGameServerStats mock vtable used by the
Steamworks harness. Round 681 named the production `ISteamGameServerStats`
value ABI slots, but the harness still installed the implemented mock methods
through raw `0x?? / 4` indices. This round promotes the mock interface to the
same auditable vocabulary without changing production behavior.

Focused parity estimate: **before 88% -> after 99%** for focused
SteamGameServerStats harness slot-mirroring source-shape confidence. Overall Steam launch/runtime integration mapping confidence moves from **94.08% -> 94.10%**.
Repo-wide parity remains **99%** because this pass only clarifies test-harness
Steamworks ABI wiring, does not change the strict-retail Windows replacement
score, and does not enable live Steam behavior by default.

## Evidence

Observed Ghidra and import facts:

- `functions.csv` preserves the GameServerStats owners at `004670c0`,
  `004671d0`, `004672d0`, `00467360`, `00467560`, and `00467850`.
- `imports.txt` confirms the retained `SteamGameServerStats` import alongside
  the `SteamGameServer` logged-on gate used by request dispatch.
- `analysis_symbols.txt` preserves the `GSStatsReceived_t` and
  `GSStatsStored_t` callback vtables for the server stats owner.
- `references/analysis/quakelive_symbol_aliases.json` maps the same owners,
  plus their `sub_*` spellings, to the promoted stats aliases.

Observed Binary Ninja HLIL facts:

- `SteamStats_FlushPendingValues` flushes dirty int, float, average-rate,
  achievement, and store work through `SteamGameServerStats`.
- `SteamStats_OnServersConnected` checks `SteamGameServerStats()`, gates on
  `SteamGameServer + 0x20`, reacquires `SteamGameServerStats()`, then requests
  stats through slot `0x00`.
- `SteamStats_OnStatsReceived` reads float and int values through
  `SteamGameServerStats + 0x04` and `+0x08`.
- `SteamStats_SetAchievement` dispatches through
  `SteamGameServerStats + 0x1c` before flushing pending values.
- `SteamStats_OnStatsStored` handles the store callback and reuses the stats
  received path when some values fail to validate.
- `SteamStats_Init` installs the server stats callbacks and uses the same
  `SteamGameServerStats()` plus `SteamGameServer + 0x20` request gate.

Inference: once production source names the `ISteamGameServerStats` ABI slots,
the harness should mirror that vocabulary instead of retaining a second
raw-offset table. Keeping `QLR_STEAM_GAMESERVERSTATS_REQUEST_USER_STATS_SLOT`
and `QLR_STEAM_GAMESERVERSTATS_VTABLE_SLOT_COUNT` local to the harness
preserves the mock boundary while making the ABI mirror explicit.

## Source Reconstruction

`tests/steamworks_harness.c` now names the mock SteamGameServerStats slots:

- `QLR_STEAM_GAMESERVERSTATS_REQUEST_USER_STATS_SLOT`
- `QLR_STEAM_GAMESERVERSTATS_GET_USER_STAT_FLOAT_SLOT`
- `QLR_STEAM_GAMESERVERSTATS_GET_USER_STAT_INT_SLOT`
- `QLR_STEAM_GAMESERVERSTATS_GET_USER_ACHIEVEMENT_SLOT`
- `QLR_STEAM_GAMESERVERSTATS_SET_USER_STAT_FLOAT_SLOT`
- `QLR_STEAM_GAMESERVERSTATS_SET_USER_STAT_INT_SLOT`
- `QLR_STEAM_GAMESERVERSTATS_UPDATE_AVG_RATE_STAT_SLOT`
- `QLR_STEAM_GAMESERVERSTATS_SET_USER_ACHIEVEMENT_SLOT`
- `QLR_STEAM_GAMESERVERSTATS_STORE_USER_STATS_SLOT`

`QLR_SteamAPI_SteamGameServerStats` now sizes the mock vtable with
`QLR_STEAM_GAMESERVERSTATS_VTABLE_SLOT_COUNT`, derived from the terminal
store-user-stats slot, and installs the implemented request, read, write,
average-rate, achievement, and store methods through named slots.

SteamGameServerStats production wrappers were already named by Round 681; this
pass only mirrors that vocabulary in the harness.

## Validation

Completed for this pass:

- `python -m pytest -q tests/test_platform_services.py -k "steam_gameserverstats_mock_slot_mirroring_round_713 or steam_gameserverstats_value_slot_constants_round_681 or steam_gameserver_stats_wrapper_guards_track_round_633 or server_steam_stats_owner_reconstructs_retail_gameserverstats_bridge" --tb=short`
  - `4 passed, 248 deselected in 4.29s`
- `python -m pytest -q tests/test_steamworks_harness.py --tb=short`
  - `132 passed in 1.37s`
- `python -m pytest -q tests/test_platform_services.py --tb=short`
  - `251 passed, 1 failed in 10.40s`; the failure is the pre-existing ZMQ Round 698 gate referencing missing `docs/reverse-engineering/quakelive_steam_mapping_round_698.md`.
- `git diff --check`
  - Passed; Git reported only existing LF-to-CRLF working-copy warnings.
