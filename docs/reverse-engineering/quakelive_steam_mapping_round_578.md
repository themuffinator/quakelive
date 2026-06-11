# Quake Live Steam Mapping Round 578: Steam API Import Table Loader Contract

Date: 2026-06-11

## Scope

This round closes the core Steam API import-table contract used by the retail
`quakelive_steam.exe` launch/runtime path and ties it to the reconstructed
dynamic loader in `platform_steamworks.c`.

Focused retail functions:

- `SteamClient_IsInitialized`: `sub_460510` / `FUN_00460510`
- `SteamAPI_Shutdown` thunk: `sub_460540` / Ghidra row `SteamAPI_Shutdown`
- `SteamClient_Init`: `sub_461500` / `FUN_00461500`
- `SteamClient_Frame`: `sub_461D40` / `FUN_00461d40`

Focused import-table band:

- `0x00558508`: `SteamAPI_Shutdown`
- `0x00558510`: `SteamAPI_RegisterCallResult`
- `0x00558514`: `SteamAPI_UnregisterCallResult`
- `0x00558518`: `SteamAPI_UnregisterCallback`
- `0x0055851C`: `SteamAPI_RegisterCallback`
- `0x00558524`: `SteamAPI_RunCallbacks`
- `0x00558554`: `SteamAPI_Init`

## Evidence

Observed facts:

- Ghidra `imports.txt` lists the seven Steam API process/runtime imports at
  `001591cc`, `001591ec`, `0015920a`, `0015922a`, `00159248`, `00159264`, and
  `00159274`.
- Binary Ninja HLIL pins the matching import lookup rows at `0x00558508`,
  `0x00558510`, `0x00558514`, `0x00558518`, `0x0055851C`, `0x00558524`, and
  `0x00558554`, with import-name rows under `0x005591cc` through
  `0x00559276`.
- Binary Ninja HLIL shows `sub_461500` calling `SteamAPI_Init()` before setting
  the client-initialized global, and `sub_461d40` calling
  `SteamAPI_RunCallbacks()` only when that global is non-zero.
- Binary Ninja HLIL shows the retail quit path calling `SteamAPI_Shutdown()`;
  the Ghidra row for `0x00460540` is a 6 byte import thunk rather than a large
  policy-bearing helper.
- `SteamAPI_RestartAppIfNecessary` remains absent from Ghidra imports, Binary
  Ninja import rows, and the reconstructed source loader.
- `QL_BUILD_ONLINE_SERVICES` remains default-disabled, and that default forces
  `QL_BUILD_STEAMWORKS` off unless the build explicitly opts into online
  services.

Inferred mapping:

- The source-level dynamic loader is the correct reconstruction boundary for
  this repository: it preserves the retail API surface while keeping retired
  online service behavior behind `QL_BUILD_ONLINE_SERVICES`.
- Required loader entries are limited to the retail process/runtime core
  (`SteamAPI_Init`, `SteamAPI_Shutdown`, `SteamAPI_RunCallbacks`) plus the
  source-owned auth/session interface calls needed by the reconstructed service
  abstraction.
- Callback registration imports stay optional in source because default builds
  intentionally stub the live Steam path, but the loader still resolves the
  retail names first whenever the Steamworks path is enabled.

## Reconstruction

No runtime behavior was changed in this round.

Strengthened `tests/test_platform_services.py` so the loader parity gate now
proves:

- the exact retail Steam API import lookup/name-table rows in Binary Ninja
  HLIL;
- the matching Ghidra `STEAM_API.DLL!SteamAPI_*` imports;
- the absence of `SteamAPI_RestartAppIfNecessary`;
- the source loader order from `SteamAPI_Init` through shutdown, callbacks,
  optional callback registration, and retail interface aliases;
- the default-disabled online-service gate that prevents accidental live Steam
  launch behavior in normal builds.

## Confidence

- High that the core Steam API launch/runtime import surface is now fully
  pinned: Ghidra imports, Binary Ninja import lookup rows, and source loader
  entries agree.
- High that no Steam launcher restart import should be reconstructed: all
  committed retail evidence checked here is negative for
  `SteamAPI_RestartAppIfNecessary`.
- Medium-high that optional callback registration remains the right source
  shape: retail imports prove the names exist, while source policy requires
  graceful stubs and disabled default live services.

## Validation

Completed validation:

```text
python -m pytest tests/test_platform_services.py::test_platform_steamworks_loader_reconstructs_retail_import_surface_and_launch_contract -q --tb=short
1 passed

python -m pytest tests/test_platform_services.py::test_client_steam_api_shutdown_wrapper_reconstructs_retail_quit_thunk tests/test_platform_services.py::test_client_steam_startup_initialized_guard_reconstructs_retail_common_check -q --tb=short
2 passed

python -m pytest tests/test_steamworks_harness.py -q --tb=short
128 passed

python -m pytest tests/test_platform_services.py -q --tb=short
145 passed

git diff --check -- tests/test_platform_services.py docs/reverse-engineering/quakelive_steam_mapping_round_578.md IMPLEMENTATION_PLAN.md
passed with repository line-ending normalization warnings only
```

No game launch is required for this static import-table/source-contract mapping
round.

## Parity Estimate

- Focused Steam API import-table confidence: **before 94% -> after 99%**.
- Focused Steamworks dynamic-loader source-contract confidence:
  **before 96% -> after 98%**.
- Overall Steam launch/runtime integration mapping confidence: **92.9% -> 92.95%**.
