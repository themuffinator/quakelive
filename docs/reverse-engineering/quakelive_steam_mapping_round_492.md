# Quake Live Steam Mapping Round 492: Callback Unregister Local-State Fallback

## Scope

This round tightens the normal Steam callback unregister helper used by the
client, avatar, lobby, microtransaction, workshop, and server callback bundles.
Retail callback destructors check the Steam callback registration flag and call
`SteamAPI_UnregisterCallback` for live callback objects. The SRP wrapper keeps
that runtime call when the dynamic export is available, while now also clearing
the retained local registration bit when the export is unavailable.

This is adjacent to round 490's UGC call-result cleanup, but covers ordinary
`CCallback` objects rather than `CCallResult` objects.

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

- Ghidra imports record `STEAM_API.DLL!SteamAPI_UnregisterCallback`.
- `functions.csv` records `FUN_00467430` at `0x00467430`, size `21`, for a
  single `idSteamStats` callback destructor helper.
- `functions.csv` records `FUN_00467560` at `0x00467560`, size `88`, for the
  grouped `idSteamStats` destructor that unregisters multiple callback objects.
- Retail HLIL at `0x00467430` checks the callback flags byte before calling
  `SteamAPI_UnregisterCallback(arg1)`.
- Retail HLIL at `0x00467560` repeats the same pattern for the stored,
  received, and connected stats callbacks, including calls at `0x00467586`,
  `0x0046759B`, and `0x004675B0`.
- `analysis_symbols.txt` promotes imported `CCallback` vtables and RTTI for
  the main `SteamCallbacks`, `SteamServerCallbacks`, and `idSteamStats`
  callback object families.

## Source Reconstruction

Implemented source-side changes:

- Updated `QL_Steamworks_UnregisterCallbackObject` so its guard only rejects a
  missing object or an object without the retained registered bit.
- Kept `state.SteamAPI_UnregisterCallback( object )` in place whenever the
  optional dynamic export is available.
- Moved the retained `callbackFlags &= ~0x01` cleanup outside the optional
  export guard so local callback state is cleared consistently.
- Added Steamworks harness probes to toggle the optional unregister export,
  unregister a representative `RichPresenceJoinRequested` callback object, and
  read that object's retained callback flag.
- Added functional harness coverage proving the local flag clears even when
  the optional unregister export is unavailable.
- Extended static platform-service parity coverage with Ghidra import anchors,
  HLIL destructor-order anchors, and source ordering assertions.

The change remains inside the Steamworks/online-services wrapper. It does not
enable live Steam services in the default disabled-online-services build.

## Validation

Focused validation passed:

- `python -m pytest tests/test_platform_services.py::test_platform_steamworks_reconstructs_retail_callback_bundle_registration_surface -q --tb=short`
  - 1 passed.
- `python -m pytest tests/test_steamworks_harness.py::test_callback_bundle_registration_and_dispatch_reconstructs_retail_client_owner tests/test_steamworks_harness.py::test_callback_unregister_clears_local_flag_without_optional_unregister_symbol -q --tb=short`
  - 4 passed across disabled and enabled Steamworks harness builds.
- `pwsh -NoProfile -ExecutionPolicy Bypass -File .vscode/build.ps1 -Configuration Debug -Platform x86 -Targets quakelive_steam`
  - Build succeeded with 0 warnings and 0 errors.

No game launch was performed. The change was settled by committed retail
references, focused source assertions, harness coverage, and the normal engine
build.

## Confidence

High confidence for the retail callback-unregister contract:

- Import evidence, HLIL flag checks, destructor call order, function metadata,
  and imported `CCallback` symbols all agree on the owner and runtime thunk.
- The source already grouped callback unregistration by bundle; this pass only
  separates retained local-state cleanup from the optional dynamic export guard.

Medium confidence for live Steam backend timing:

- If a runtime genuinely lacks `SteamAPI_UnregisterCallback`, SRP cannot remove
  registrations from that runtime. The reconstruction only prevents SRP's local
  retained callback bit from staying stale in that fallback.

## Parity Estimate

Focused callback unregister local-state fallback:

- Before: 84%
- After: 98%

Overall Steam launch/runtime integration:

- Before: 89.2%
- After: 89.3%
