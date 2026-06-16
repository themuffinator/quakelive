# Quake Live Steam Mapping Round 714: Mock SteamApps Subscription Wiring

Date: 2026-06-16

## Scope

This pass rechecked the retained SteamApps subscription wrapper and closed the
remaining harness-side gap around `QL_Steamworks_IsSubscribedApp`. Round 699
already named the production `SteamApps + 0x1c` ABI slot, but the Steamworks
harness did not yet expose a mock `SteamApps` interface that could exercise the
same wrapper path.

Focused parity estimate: **before 85% -> after 99%** for focused SteamApps
harness subscription source-shape confidence. Overall Steam launch/runtime integration mapping confidence moves from **94.10% -> 94.12%**. Repo-wide
parity remains **99%** because this pass only clarifies test-harness Steamworks
ABI wiring, leaves the strict-retail Windows replacement score unchanged, and
does not enable live Steam behavior by default.

## Evidence

Observed Ghidra and import facts:

- `references/analysis/quakelive_symbol_aliases.json` maps
  `FUN_00460590` / `sub_460590` to `SteamApps_BIsSubscribedApp`.
- `functions.csv` preserves `FUN_00460590,00460590,40,0,unknown`.
- `imports.txt` confirms the retained `STEAM_API.DLL!SteamApps @ 001591e0`
  import used by the retail subscription check.

Observed Binary Ninja HLIL fact:

- `004605b7` returns through `SteamApps + 0x1c`, matching the
  `BIsSubscribedApp` app-subscription query.

Observed production source facts:

- `platform_steamworks.c` keeps both `SteamApps` and `SteamAPI_SteamApps`
  export names and loads them through `QL_Steamworks_LoadSymbolAlias`.
- `QL_Steamworks_IsSubscribedApp` guards the offline/uninitialised cases,
  obtains `state.SteamApps()`, and calls the named
  `QL_STEAM_APPS_BIS_SUBSCRIBED_APP_SLOT`.

Inference: the harness should mirror the same `ISteamApps` ABI vocabulary used
by production so subscription bridge tests can prove wrapper behavior without
needing a live Steam runtime.

## Source Reconstruction

`tests/steamworks_harness.c` now defines:

- `QLR_STEAM_APPS_BIS_SUBSCRIBED_APP_SLOT`
- `QLR_STEAM_APPS_VTABLE_SLOT_COUNT`
- `QLR_SteamAPI_SteamApps`
- `QLR_SteamApps_BIsSubscribedApp`

The mock loader now resolves both `SteamApps` and `SteamAPI_SteamApps` to
`QLR_SteamAPI_SteamApps`, and `QLR_SteamworksMock_PrimeState` injects the same
mock interface into `state.SteamApps`. The mock records the forwarded app id and
returns a configurable subscription result through the named slot.

`tests/test_steamworks_harness.py` now exercises the wrapper with both true and
false subscription results and verifies that the app id reaches the mock
`SteamApps` vtable method. Disabled Steamworks builds still return `qfalse`.

## Validation

Completed for this pass:

- `python -m pytest -q tests/test_steamworks_harness.py -k "steam_apps_subscription_wrapper_uses_mock_vtable or all_ugc_query_forwards_filter_to_retail_query_slot" --tb=short`
  - `8 passed, 126 deselected in 1.61s`
- `python -m pytest -q tests/test_platform_services.py -k "steam_apps_mock_slot_mirroring_round_714 or steam_ugc_apps_workshop_slot_constants_round_699 or steamworks_runtime_export_boundary_round_701" --tb=short`
  - `3 passed, 250 deselected in 0.15s`
- `python -m pytest -q tests/test_steamworks_harness.py --tb=short`
  - `134 passed in 0.93s`
- `python -m pytest -q tests/test_platform_services.py --tb=short`
  - `252 passed, 1 failed in 10.05s`; the failure is the pre-existing Round
    698 gate referencing missing
    `docs/reverse-engineering/quakelive_steam_mapping_round_698.md`.
- `git diff --check`
  - Passed; Git reported only existing LF-to-CRLF working-copy warnings.
