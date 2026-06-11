# Quake Live Steam Mapping Round 481: Client Startup Fatal-Guard Boundary

## Scope

This round maps the retail common-startup Steam client guard that follows the
client bootstrap during `quakelive_steam.exe` launches. The pass focuses on the
relationship between the early `SteamClient_Init` call, the `com_build` and
`dedicated` escape hatches, the retained Steam initialized flag, and SRP's
documented compatibility divergence from retail's fatal abort.

## Evidence

Primary evidence:

- `references/hlil/quakelive/quakelive_steam.exe/quakelive_steam.exe_hlil_split/quakelive_steam.exe_hlil_part02.txt`
- `references/hlil/quakelive/quakelive_steam.exe/quakelive_steam.exe_hlil_split/quakelive_steam.exe_hlil_part04.txt`
- `references/analysis/quakelive_symbol_aliases.json`

Observed facts:

- The alias map promotes `sub_460510` to `SteamClient_IsInitialized`.
- Retail `sub_460510` returns the retained client initialized flag at
  `data_e30218`.
- Retail `sub_461500` first checks `com_build`; when not building it calls
  `SteamAPI_Init`, stores the result in `data_e30218`, and returns after
  logging `Steam API not present.` if initialization fails.
- In common startup, retail registers `dedicated` before the initial
  `sub_461500` Steam client bootstrap.
- Retail registers `com_build` later in the common cvar block.
- Retail calls `CL_Init` (`sub_4bc690`) before the final Steam startup guard.
- The final guard aborts only when all three checks fail:
  `sub_460510() == 0`, `sub_4ccd80("com_build") == 0`, and
  `sub_4ccd80("dedicated") == 0`.
- The fatal retail branch calls `sub_4ec6e0("Failed to initialize Steam.")`.

## Source Reconstruction

Implemented source-side changes:

- Hardened `tests/test_application_initialization_mapping.py` with direct HLIL
  assertions for the retail `dedicated -> sub_461500 -> com_build -> CL_Init ->
  fatal guard` order.
- Hardened `tests/test_platform_services.py` with the same retail ordering
  anchors in the Steam initialized-guard owner test.
- Added source assertions that `Com_VerifySteamClientStartup` checks
  `SteamClient_IsInitialized()`, `com_buildScript`, and `dedicated` in the
  mapped order before reaching the SRP compatibility diagnostic.
- Added negative source assertions that the compatibility guard does not call
  `Com_Error` or `Sys_Error`.
- Retained the existing SRP policy divergence: retail aborts with
  `Failed to initialize Steam.`, while SRP logs the retail abort point and keeps
  the default-disabled online-services fallback.

No C source edit was needed. The current source already reconstructs the
startup owner boundary while preserving the repository's online-services
fallback policy.

## Validation

Focused validation passed:

- `python -m pytest tests/test_application_initialization_mapping.py::test_policy_adjusted_common_client_server_wiring_matches_mapped_retail_chain -q --tb=short`
- `python -m pytest tests/test_platform_services.py::test_client_steam_startup_initialized_guard_reconstructs_retail_common_check -q --tb=short`

## Parity Estimate

Scoped Steam client startup fatal-guard boundary:

- Before: 86%
- After: 97%

Overall Steam launch/runtime integration:

- Before: 85%
- After: 86%
