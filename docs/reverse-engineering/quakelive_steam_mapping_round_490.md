# Quake Live Steam Mapping Round 490: UGC Call-Result Rebind Lifecycle

## Scope

This round tightens the Steam UGC query call-result lifecycle used by the
retail `GetAllUGC` browser/runtime path. Retail binds
`SteamUGCQueryCompleted_t` as a `CCallResult` owned by the main
`SteamCallbacks` bundle, unregisters any prior call result before registering a
new query call handle, and then lets the callback pump deliver the completion
payload.

The source already modeled the retail call-result owner and normal
unregister-before-register path. This pass reconstructs the retained local
state cleanup for the compatibility fallback where the optional dynamic
`SteamAPI_UnregisterCallResult` export is unavailable, while preserving the
retail runtime call when the export exists.

## Evidence

Primary evidence:

- `references/hlil/quakelive/quakelive_steam.exe/quakelive_steam.exe_hlil_split/quakelive_steam.exe_hlil_part02.txt`
- `references/reverse-engineering/ghidra/quakelive_steam/imports.txt`
- `references/reverse-engineering/ghidra/quakelive_steam/functions.csv`
- `references/reverse-engineering/ghidra/quakelive_steam/analysis_symbols.txt`
- `src/common/platform/platform_steamworks.c`
- `tests/test_platform_services.py`
- `tests/test_steamworks_harness.py`

Observed facts:

- Ghidra imports record both `SteamAPI_RegisterCallResult` and
  `SteamAPI_UnregisterCallResult` from `STEAM_API.DLL`.
- `functions.csv` records `FUN_00460dc0` at `0x00460DC0`, size `158`, for the
  retail UGC query request helper.
- `functions.csv` records `FUN_004613a0` at `0x004613A0`, size `344`, for the
  callback bundle constructor path.
- `analysis_symbols.txt` promotes the imported
  `CCallResult<class_SteamCallbacks,struct_SteamUGCQueryCompleted_t>` vtable
  and RTTI symbols.
- Retail `0x00460DC0` reads the app id through `SteamUtils`, creates an all-UGC
  query through `SteamUGC` slot `0x04`, sends it through slot `0x0C`, calls
  `SteamAPI_UnregisterCallResult` at `0x00460E25`, and finally calls
  `SteamAPI_RegisterCallResult` at `0x00460E4E`.
- Retail `0x004613A0` constructs the
  `CCallResult<class SteamCallbacks, struct SteamUGCQueryCompleted_t>` vtable,
  confirming that UGC query completion is a call result, not a normal
  `RegisterCallback` entry.

## Source Reconstruction

Implemented source-side changes:

- Updated `QL_Steamworks_UnbindCallResultObject` so it always clears the
  retained local call handle and bound flag once a bound object is being
  unbound.
- Kept the retail `SteamAPI_UnregisterCallResult( object, callHandle )` call in
  place whenever the optional dynamic export is available.
- Left `QL_Steamworks_BindUGCQueryCallResult` ordering intact:
  `QL_Steamworks_UnbindCallResultObject` runs before
  `SteamAPI_RegisterCallResult`.
- Added harness probes for toggling the optional unregister export and reading
  the retained UGC call-result handle/bound state.
- Added functional harness coverage proving the local state clears even when
  the unregister export is unavailable.
- Extended the static platform-service parity test with Ghidra import anchors,
  HLIL unregister/register ordering, and source ordering assertions.

This remains behind the existing Steamworks/online-services build gates. The
default disabled online-services configuration does not start using live Steam
services.

## Validation

Focused validation passed:

- `python -m pytest tests/test_platform_services.py::test_platform_steamworks_reconstructs_retail_callback_bundle_registration_surface -q --tb=short`
  - 1 passed.
- `python -m pytest tests/test_steamworks_harness.py::test_ugc_call_result_binding_routes_through_registered_client_bundle tests/test_steamworks_harness.py::test_ugc_call_result_unbind_clears_local_state_without_optional_unregister_symbol tests/test_steamworks_harness.py::test_ugc_call_result_failure_projection_preserves_retail_callback_shape -q --tb=short`
  - 6 passed across disabled and enabled Steamworks harness builds.
- `pwsh -NoProfile -ExecutionPolicy Bypass -File .vscode/build.ps1 -Configuration Debug -Platform x86 -Targets quakelive_steam`
  - Build succeeded with 0 warnings and 0 errors.

No game launch was performed. The question was settled by committed retail
references, source-level parity assertions, the Steamworks harness, and the
normal engine build.

## Confidence

High confidence for the retail call-result ownership and ordering:

- Import evidence, HLIL call order, function metadata, and `CCallResult`
  symbol/RTTI evidence all point to the same owner.
- The source wrapper already had the retail ordering; this pass only separates
  retained local-state cleanup from an optional dynamic export guard.

Medium confidence for live Steam backend timing:

- The exact timing of backend UGC completion remains live-service dependent and
  is intentionally not tested as part of the default disabled-online-services
  policy.

## Parity Estimate

Focused UGC call-result rebind lifecycle:

- Before: 86%
- After: 98%

Overall Steam launch/runtime integration:

- Before: 89%
- After: 89.2%
