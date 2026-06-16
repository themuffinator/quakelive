# Quake Live Steam Mapping Round 739: Steamworks Runtime Disable Reason Wiring

Date: 2026-06-16

## Scope

This round pins the runtime-disable reason wiring for SRP's opted-in
Steamworks platform-service lane. Retail Quake Live imports Steam directly and
uses the Steam client startup state as part of launch-time control flow; SRP
keeps the live-service path behind `QL_BUILD_ONLINE_SERVICES` and
`QL_BUILD_STEAMWORKS`, default-disabled, with runtime kill switches that make
the retained compatibility boundary explicit.

Before this round, `QL_DISABLE_STEAMWORKS` disabled the service table but the
published provider and policy labels collapsed that result into the generic
`QL_DISABLE_EXTERNAL_ECOSYSTEMS` explanation. This pass keeps the same
fail-closed behavior while making the Steamworks-specific reason visible to
the service descriptors, mode labels, and parity reason labels.

Focused Steamworks runtime-disable reason wiring confidence:
**82% -> 99%**.

Overall Steam launch/runtime integration mapping confidence moves from
**94.34% -> 94.36%**. Repo-wide parity remains **99%** because this pass only
clarifies a default-disabled SRP compatibility lane and does not enable live
Steam behavior by default.
overall Steam launch/runtime integration mapping confidence **94.34% -> 94.36%**

## Retail Evidence

Observed Ghidra import anchors:

- `STEAM_API.DLL!SteamAPI_Init @ 00159264`
- `STEAM_API.DLL!SteamAPI_Shutdown @ 001591cc`
- `STEAM_API.DLL!SteamAPI_RunCallbacks @ 00159274`
- `STEAM_API.DLL!SteamUser @ 0015916a`
- `STEAM_API.DLL!SteamFriends @ 0015915a`
- `STEAM_API.DLL!SteamApps @ 001591e0`

Observed promoted symbol anchors:

- `FUN_00461500` maps to `SteamClient_Init`
- `FUN_00460510` maps to `SteamClient_IsInitialized`

Observed Binary Ninja HLIL anchors:

```text
0046151b      uint32_t eax_1 = zx.d(SteamAPI_Init())
0046151e      data_e30218 = eax_1
004cc16e          sub_461500()
004cc5fd      if (sub_460510() == 0 && sub_4ccd80("com_build") == 0 && sub_4ccd80("dedicated") == 0)
```

Observed SRP policy anchors:

- `Com_ApplyOnlineServicesBuildPolicy` sets
  `QL_DISABLE_EXTERNAL_ECOSYSTEMS=1` when online services are build-disabled.
- The same build policy sets `QL_DISABLE_STEAMWORKS=1`, so the proprietary
  Steamworks lane stays explicitly disabled in default builds.
- `QL_PlatformExternalEcosystemsDisabled` already treated
  `QL_DISABLE_STEAMWORKS` as a runtime service-table disable signal.

Inference: the generic and Steamworks-specific runtime disable flags share the
same fail-closed platform-service boundary, but the public descriptor labels
should preserve the actual reason that reached that boundary. If both flags
are set, the broad `QL_DISABLE_EXTERNAL_ECOSYSTEMS` reason remains first
because it owns the more general policy decision.

## Reconstruction

`platform_services.c` now separates reason discovery from the boolean gate:

- `QL_PlatformExternalEcosystemsDisableReason` returns
  `QL_DISABLE_EXTERNAL_ECOSYSTEMS`, `QL_DISABLE_STEAMWORKS`, or `NULL`.
- `QL_PlatformExternalEcosystemsDisabled` remains the boolean gate used by the
  service-table builder.
- `QL_PlatformExternalEcosystemsDisableProviderLabel` maps the active reason
  to either `Disabled by QL_DISABLE_EXTERNAL_ECOSYSTEMS` or
  `Disabled by QL_DISABLE_STEAMWORKS`.
- `QL_BuildServiceTable` applies that provider label consistently to auth,
  matchmaking, workshop, overlay, and stats when the runtime policy disables
  the retained platform lane.
- `QL_DescribePlatformFeaturePolicy` now emits
  `compatibility-disabled (QL_DISABLE_STEAMWORKS)` for Steamworks-specific
  runtime disables.
- `QL_GetOnlineServicesModeLabel` now reports
  `Steamworks-disabled compatibility lane` for that specific path.
- `QL_GetOnlineServicesParityReasonLabel` now explains that the opted-in
  Steamworks compatibility lane was disabled by runtime policy.

The change deliberately does not alter default behavior: live Steamworks usage
remains off unless the build opts into online services and Steamworks.

## Tests

`tests/test_platform_services.py` now covers both runtime disable flags through
compiled C probes:

- `QL_DISABLE_EXTERNAL_ECOSYSTEMS=1` still publishes the generic external
  disable provider and policy.
- `QL_DISABLE_STEAMWORKS=1` now publishes
  `Disabled by QL_DISABLE_STEAMWORKS`,
  `compatibility-disabled (QL_DISABLE_STEAMWORKS)`,
  `Steamworks-disabled compatibility lane`, and the Steamworks-specific parity
  reason.

The Round 739 static parity gate pins the retail Steam import/HLIL anchors,
the build-policy environment variables, the new reason/helper source shape,
the service-table provider wiring, this mapping note, and the implementation
plan entry.

## Validation

Completed for this pass:

- `python -m pytest -q tests/test_platform_services.py -k "platform_service_table_respects_runtime_steamworks_disable_env or online_services_mode_labels_track_build_flags_and_runtime_policy" --tb=short`
  - `2 passed, 276 deselected in 3.02s`
- `python -m pytest -q tests/test_platform_services.py -k steamworks_runtime_disable_reason_labels_track_round_739 --tb=short`
  - `1 passed, 277 deselected in 0.16s`
- `python -m pytest -q tests/test_platform_services.py -k steamworks --tb=short`
  - `22 passed, 256 deselected in 2.25s`
- `python -m pytest -q tests/test_platform_services.py --tb=short`
  - `278 passed in 13.72s`
- `git diff --check`
  - Passed; Git reported only existing LF-to-CRLF working-copy warnings.
