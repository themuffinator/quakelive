# Quake Live Steam Mapping Round 704: Stats Descriptor Count Guards

Date: 2026-06-16

## Scope

This pass rechecked the client `SteamCallbacks_OnUserStatsReceived` descriptor
tables used to publish `users.stats.%llu.received`. The stat and achievement
catalogs were already reconstructed in source, but their recovered counts were
plain decimal values and the arrays had no compile-time guard tying the source
catalogs back to the retail table lengths.

Focused parity estimate: **before 91% -> after 99%** for focused Steam stats
descriptor-count source-shape confidence. Overall Steam launch/runtime integration mapping confidence moves from **93.90% -> 93.92%**.
Repo-wide parity remains **99%** because this pass clarifies opt-in Steamworks
wiring without changing the strict-retail Windows replacement score and does not enable live Steam behavior by default.

## Evidence

Observed Ghidra and import facts:

- `metadata.txt` identifies the owner as 32-bit Windows `quakelive_steam.exe`.
- `functions.csv` preserves `FUN_0045ffd0,0045ffd0,783,0,unknown` for
  `SteamCallbacks_OnUserStatsReceived`.
- `functions.csv` preserves `FUN_004613a0,004613a0,344,0,unknown` for
  `SteamCallbacks_Init`.
- `imports.txt` confirms the Steam callback, SteamFriends, and SteamUserStats
  imports used by this path.
- `analysis_symbols.txt` exposes the
  `CCallback<class_SteamCallbacks,struct_UserStatsReceived_t,0>` vtable and
  RTTI metadata.
- `references/analysis/quakelive_symbol_aliases.json` maps
  `FUN_0045ffd0`, `sub_45FFD0`, and `sub_45ffd0` to
  `SteamCallbacks_OnUserStatsReceived`.

Observed Binary Ninja HLIL facts:

- `sub_45ffd0` builds the retained stats/achievements payload.
- The stat row count is stored at `data_55da8c = 0x58`.
- The stat descriptor cursor starts at `&data_55da98`, tests the previous
  dword as the int/float discriminator, and advances by seven dwords per row.
- The achievement pointer walk spans `0x0055E630..0x0055E71C`, immediately
  before the `CCallbackBase` RTTI descriptor. That span is `0xEC` bytes, or
  `0x3b` four-byte pointers.
- The retained publication event remains `users.stats.%llu.received`.

Observed data-section facts:

- The 88-row stat table starts with `version`, includes `medal_accuracy`, and
  ends with `total_deaths`.
- All currently shipped stat discriminator dwords are zero, matching the
  integer readback path reconstructed in earlier rounds.
- The 59-name achievement table starts with `AW_MIDAIR` and ends with
  `AW_MAX`.

Inference: the source constants should represent the recovered retail table
lengths, not merely convenient decimal array sizes. A C source static-assert
macro is the nearest low-noise reconstruction of the original table-size
contract because the retail binary stores the stat count and bounds the
achievement walk by adjacent static data.

## Source Reconstruction

`src/code/client/cl_main.c` now names the descriptor counts as the recovered
retail constants:

- `CL_STEAM_STATS_FIELD_COUNT 0x58`
- `CL_STEAM_ACHIEVEMENT_COUNT 0x3b`

The stat descriptor array and achievement-name array continue to use those
counts directly. A local `CL_STEAM_STATIC_ASSERT_ARRAY_LEN` macro now checks:

- `s_clSteamStatDescriptors` has exactly `CL_STEAM_STATS_FIELD_COUNT` rows.
- `s_clSteamAchievementNames` has exactly `CL_STEAM_ACHIEVEMENT_COUNT` rows.

The JSON builders still iterate with `ARRAY_LEN`, preserving their existing
source-side safety if the catalog is intentionally edited in a later
reconstruction pass.

No Steam callback registration, readback wrapper, JSON field, event name,
opt-in Steamworks guard, or live service policy changed in this pass.

## Validation

Completed for this pass:

- `python -m pytest -q tests/test_platform_services.py -k "steam_stats_descriptor_count_constants_round_704 or steam_user_stats_float_descriptor_round_383 or client_stats_callback_lane_stays_explicit or steam_user_stats_presence_callbacks_track_round_616" --tb=short` - 4 passed, 239 deselected.
- `python -m pytest -q tests/test_steamworks_harness.py --tb=short` - 132 passed.
- `python -m pytest -q tests/test_platform_services.py --tb=short` - 242 passed, 1 failed because the pre-existing ZMQ Round 698 gate references missing `docs/reverse-engineering/quakelive_steam_mapping_round_698.md`.
- `git diff --check` - passed with existing LF-to-CRLF working-copy warnings only.
