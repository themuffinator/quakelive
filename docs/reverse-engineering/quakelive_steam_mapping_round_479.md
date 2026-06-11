# Quake Live Steam Mapping Round 479: SteamID Homepath Module Roots

## Scope

This round maps the Steam launch path that lets the executable resolve native
game modules from the Steam-user scoped `baseq3` tree. No C source edit was
needed: the current source already keeps the repository's policy-adjusted
replacement-launch behavior, and this pass hardens the retail evidence and
regression assertions around that behavior.

## Evidence

Primary evidence:

- `references/hlil/quakelive/quakelive_steam.exe/quakelive_steam.exe_hlil_split/quakelive_steam.exe_hlil_part04.txt`
- `references/hlil/quakelive/quakelive_steam.exe/quakelive_steam.exe_hlil_split/quakelive_steam.exe_hlil_part05.txt`
- `references/reverse-engineering/ghidra/quakelive_steam/functions.csv`
- `references/analysis/quakelive_symbol_aliases.json`
- `src/code/qcommon/files.c`
- `src/code/win32/win_main.c`

Observed facts:

- The alias map promotes `sub_4ECEB0` to `Sys_LoadDll`.
- `functions.csv` records `FUN_004eceb0` at `0x004ECEB0`, size `358`.
- Retail `FS_Startup` checks `SteamClient_IsInitialized()`, calls
  `SteamClient_GetSteamID()` when live, formats `"%s/%llu"`, and registers the
  result as `fs_homepath`.
- Retail `Sys_LoadDll` builds `"%sx86.dll"` and probes `fs_basepath`,
  `fs_homepath`, and `fs_cdpath` through `LoadLibraryA`.
- The source intentionally adjusts the load order for replacement launches:
  the SteamID-scoped homepath is searched before the immutable retail basepath,
  while the retail probe order remains captured as evidence.

## Source Reconstruction

Implemented source-side changes:

- Extended `tests/test_application_initialization_mapping.py` to pin the HLIL
  `fs_homepath = fs_basepath/<SteamID>` sequence.
- Extended the same test to protect the policy-adjusted `Sys_LoadDll` source
  behavior:
  - homepath before basepath for replacement launches,
  - `baseq3/bin.pk3` extraction after direct DLL probes,
  - `uix86.dll`, `cgamex86.dll`, and `qagamex86.dll` as the only extractable
    module names,
  - no extraction for non-`baseq3` game directories,
  - extracted DLLs are written to the preferred SteamID-scoped cache path and
    loaded through the same export validation path.

No C source edit was needed for this slice.

## Confidence

High confidence:

- Retail homepath derivation from the active SteamID.
- Retail `Sys_LoadDll` ownership and direct DLL probe order.
- Source replacement-launch divergence is explicit, bounded, and test-covered.
- `baseq3/bin.pk3` extraction is limited to the three retail native module DLLs.

Medium confidence:

- Retail does not itself materialize DLLs from `bin.pk3` in the mapped
  `Sys_LoadDll` owner. The extraction path is a source-side compatibility
  bridge for modern replacement launches where the retail install keeps module
  DLLs packaged.

## Validation

- `python -m pytest tests/test_application_initialization_mapping.py::test_policy_adjusted_steamid_native_dll_root_precedes_retail_basepath -q --tb=short`
  - 1 passed.
- `python -m pytest tests/test_application_initialization_mapping.py tests/test_fs_search_paths.py tests/test_qcommon_full_parity_gate.py tests/test_platform_services.py::test_client_steam_id_owner_reconstructs_retail_homepath_and_identity_gate -q --tb=short`
  - 18 passed, 1 skipped.
- `dumpbin /dependents build\win32\Debug\bin\quakelive_steam.exe`
  - No dynamic `steam_api`, `libpng`, `vorbis`, or `ogg` dependency was present.

No runtime launch was needed. This pass was deterministic mapping and
regression coverage from committed HLIL/Ghidra evidence plus existing source
loader behavior.

## Parity Estimate

- Focused SteamID homepath/native module-root mapping parity: 88% -> 97%.
- Steam launch/runtime integration parity: 83% -> 84%.
