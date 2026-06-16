# Quake Live Steam Mapping Round 709: Mock SteamUser And SteamUserStats Slot Mirroring

Date: 2026-06-16

## Scope

This pass rechecked the SteamUser and SteamUserStats mock vtables used by the
Steamworks harness. Rounds 670, 685, and 690 named the production identity,
voice, and client stats ABI slots, but the harness still installed those same
methods through raw `0x?? / 4` indices. This pass promotes the test double to
the same auditable vocabulary without changing production behavior.

Focused parity estimate: **before 88% -> after 99%** for focused
SteamUser/SteamUserStats harness slot-mirroring source-shape confidence. Overall Steam launch/runtime integration mapping confidence moves from **94.00% -> 94.02%**.
Repo-wide parity remains **99%** because this pass only clarifies test-harness
Steamworks ABI wiring, does not change the strict-retail Windows replacement
score, and does not enable live Steam behavior by default.

## Evidence

Observed Ghidra and import facts:

- `functions.csv` preserves `FUN_0045ffd0,0045ffd0,783,0,unknown` for
  `SteamCallbacks_OnUserStatsReceived`.
- `functions.csv` preserves `FUN_00460550,00460550,53,0,unknown` for
  `SteamClient_GetSteamID`.
- `functions.csv` preserves `FUN_00460d10,00460d10,170,0,unknown` for
  `SteamVoice_SendCapturedPacket`.
- `functions.csv` preserves `FUN_004613a0,004613a0,344,0,unknown` for
  `SteamCallbacks_Init`.
- `functions.csv` preserves `FUN_00461a60,00461a60,400,0,unknown` for
  `SteamVoice_ProcessIncomingPackets`.
- `imports.txt` confirms the retained `SteamUser` and `SteamUserStats`
  imports.
- `analysis_symbols.txt` preserves the
  `CCallback<class_SteamCallbacks,struct_UserStatsReceived_t,0>::vftable`
  anchor used by the client stats callback lane.
- `references/analysis/quakelive_symbol_aliases.json` maps the same owners,
  plus their `sub_*` spellings, to the promoted client identity, voice, stats,
  and callback aliases.

Observed Binary Ninja HLIL facts:

- `SteamClient_GetSteamID` reaches `SteamUser + 0x08`.
- The voice capture lane starts capture through `SteamUser + 0x1c`, stops
  capture through `SteamUser + 0x20`, pulls compressed bytes through
  `SteamUser + 0x28`, reads the optimal sample rate through
  `SteamUser + 0x30`, and decompresses incoming voice through
  `SteamUser + 0x2c`.
- The client stats readback lane requests user stats through
  `SteamUserStats + 0x40`, reads float stats through `SteamUserStats + 0x44`,
  reads integer stats through `SteamUserStats + 0x48`, reads display
  attributes through `SteamUserStats + 0x30`, reads achievements through
  `SteamUserStats + 0x50`, and clears stats through `SteamUserStats + 0x54`.

Inference: once production source names the SteamUser and SteamUserStats ABI
slots, the harness should mirror that vocabulary instead of retaining a second
raw-offset table. Keeping `QLR_STEAM_USER_BLOGGED_ON_SLOT`,
`QLR_STEAM_USER_VTABLE_SLOT_COUNT`,
`QLR_STEAM_USERSTATS_REQUEST_USER_STATS_SLOT`, and
`QLR_STEAM_USERSTATS_VTABLE_SLOT_COUNT` local to the harness preserves the
mock boundary while making the ABI mirror explicit.

## Source Reconstruction

`tests/steamworks_harness.c` now names the mock SteamUser slots:

- `QLR_STEAM_USER_BLOGGED_ON_SLOT`
- `QLR_STEAM_USER_GET_STEAM_ID_SLOT`
- `QLR_STEAM_USER_START_VOICE_RECORDING_SLOT`
- `QLR_STEAM_USER_STOP_VOICE_RECORDING_SLOT`
- `QLR_STEAM_USER_GET_VOICE_SLOT`
- `QLR_STEAM_USER_DECOMPRESS_VOICE_SLOT`
- `QLR_STEAM_USER_GET_VOICE_OPTIMAL_SAMPLE_RATE_SLOT`

`QLR_SteamAPI_SteamUser` now sizes the mock vtable with
`QLR_STEAM_USER_VTABLE_SLOT_COUNT`, derived from the terminal
get-voice-optimal-sample-rate slot, and installs every method through the
named harness slots.

`tests/steamworks_harness.c` also names the mock SteamUserStats slots:

- `QLR_STEAM_USERSTATS_GET_ACHIEVEMENT_DISPLAY_ATTRIBUTE_SLOT`
- `QLR_STEAM_USERSTATS_REQUEST_USER_STATS_SLOT`
- `QLR_STEAM_USERSTATS_GET_USER_STAT_FLOAT_SLOT`
- `QLR_STEAM_USERSTATS_GET_USER_STAT_INT_SLOT`
- `QLR_STEAM_USERSTATS_GET_USER_ACHIEVEMENT_SLOT`
- `QLR_STEAM_USERSTATS_RESET_ALL_STATS_SLOT`

`QLR_SteamAPI_SteamUserStats` now sizes the mock vtable with
`QLR_STEAM_USERSTATS_VTABLE_SLOT_COUNT`, derived from the reset-all-stats
slot, and installs every method through the named harness slots.

SteamNetworking, SteamMatchmaking, SteamGameServer, SteamGameServerStats, and
SteamGameServerNetworking mock vtables remain outside this pass.

## Validation

Completed for this pass:

- `python -m pytest -q tests/test_platform_services.py -k "steam_user_userstats_mock_slot_mirroring_round_709 or steam_user_voice_wrapper_round_367 or steam_client_identity_utils_round_373 or steam_clear_stats_round_375 or steam_user_stats_readback_round_382 or steam_user_stats_float_descriptor_round_383 or steam_userstats_client_value_slot_constants_round_685 or steam_client_identity_social_slot_constants_round_690" --tb=short` - 8 passed, 240 deselected.
- `python -m pytest -q tests/test_steamworks_harness.py --tb=short` - 132 passed.
- `python -m pytest -q tests/test_platform_services.py --tb=short` - 247 passed, 1 failed because the pre-existing ZMQ Round 698 gate references missing `docs/reverse-engineering/quakelive_steam_mapping_round_698.md`.
- `git diff --check` - passed with existing LF-to-CRLF working-copy warnings only.
