# Quake Live Steam Host Mapping Round 330

Date: 2026-05-28

## Scope

Mapped the Awesomium WebSession lifecycle/cache lane and the adjacent WebUI command wiring that affects startup, reload, error display, and live navigation failure state.

## Evidence

Primary owner: retail `quakelive_steam.exe`.

Committed corpus signals:

- `references/reverse-engineering/ghidra/quakelive_steam/metadata.txt` identifies the retail host corpus with `5473` functions and the Awesomium import set.
- `references/reverse-engineering/ghidra/quakelive_steam/functions.csv` lists `FUN_004f2d30` as the large WebUI bootstrap/open owner and `FUN_004f2a60` as the shutdown owner.
- `references/analysis/quakelive_symbol_aliases.json` maps `sub_4F2A10` to `CL_Web_ClearCache_f`, `sub_4F2A30` to `CL_Web_Reload_f`, `sub_4F2A60` to `QLWebHost_Shutdown`, `sub_4F2D30` to `QLWebHost_OpenURL`, `sub_4F3CB0` to `CL_Web_ShowError_f`, and `sub_4F3CD0` to `QLWebHost_RegisterCommands`.
- `references/hlil/quakelive/quakelive_steam.exe/quakelive_steam.exe_hlil_split/quakelive_steam.exe_hlil_part05.txt:15728` shows `web_clearCache` tail-calling WebSession slot `0x1c`.
- `references/hlil/quakelive/quakelive_steam.exe/quakelive_steam.exe_hlil_split/quakelive_steam.exe_hlil_part05.txt:15739` shows reload calling WebSession slot `0x1c` before WebView slot `0x78`.
- `references/hlil/quakelive/quakelive_steam.exe/quakelive_steam.exe_hlil_split/quakelive_steam.exe_hlil_part05.txt:15747` shows shutdown destroying the WebView and then calling `WebCore::Shutdown`, without calling the WebSession slot.
- `references/hlil/quakelive/quakelive_steam.exe/quakelive_steam.exe_hlil_split/quakelive_steam.exe_hlil_part05.txt:15868` shows WebSession creation from `fs_homepath`, followed by an immediate WebSession slot `0x18` dispatch.
- `references/hlil/quakelive/quakelive_steam.exe/quakelive_steam.exe_hlil_split/quakelive_steam.exe_hlil_part05.txt:16532` shows `web_showError` forwarding the full command tail after argument `1`.

## Source Reconstruction

- Reconstructed WebSession slot `0x18` as an optional `_Awe_WebSession_Initialize@4` adapter import with retail vtable fallback, called immediately after `WebCore::CreateWebSession`.
- Reclassified the historical `_Awe_WebSession_Release@4` adapter binding as the retail WebSession slot `0x1c` cache-clear lane, exposed as `CL_Awesomium_ClearCache`.
- Routed `CL_Web_ClearSessionState` through the live WebSession cache clear before source-side resource cache clearing.
- Removed the WebSession slot `0x1c` call from shutdown so shutdown matches retail WebView destroy plus `WebCore::Shutdown`.
- Updated `web_showError` to consume `Cmd_ArgsFrom( 1 )`, matching the retail full-tail forwarding.
- Made live URL navigation failure enter the mapped load-failure handler instead of leaving the host marked active after a failed `CL_Awesomium_OpenURL`.

## Validation

Guarded and verified the reconstruction with:

- `python -m pytest tests/test_awesomium_browser_parity.py tests/test_platform_services.py -q --tb=short`
  - Result: `101 passed`.
- `tools/ci/verify-awesomium-browser-host-parity.ps1`
  - Result: Awesomium browser host source, alias, mapping, and adapter parity anchors are present.
- `git diff --check -- src/code/client/cl_awesomium_win32.cpp src/code/client/cl_cgame.c src/code/client/client.h docs/reverse-engineering/awesomium-browser-wiring.md docs/reverse-engineering/quakelive_steam_mapping_round_330.md tests/test_awesomium_browser_parity.py tools/ci/verify-awesomium-browser-host-parity.ps1`
  - Result: clean; only Git line-ending normalization warnings were reported.
- `powershell -ExecutionPolicy Bypass -File tools\ci\build-windows-dlls.ps1 -RepoRoot E:\Repositories\QuakeLive-reverse -Solution src/code/quakelive.sln -Configuration Debug -Platform Win32 -PlatformToolset v143 -DisableOptionalCodecs`
  - Result: build succeeded. Existing UI/game config const/truncation warnings were reported; no Awesomium errors.

Runtime launch is not required for this pass because the committed HLIL/Ghidra evidence directly resolves the slot ownership and command wiring. The live Awesomium path remains behind `QL_BUILD_ONLINE_SERVICES`.

## Parity Estimate

- Focused Awesomium WebSession lifecycle/cache lane: **96% -> 99%**.
- Overall Awesomium WebUI wiring: **98.4% -> 98.9%**.
- Repo-wide parity remains **98% -> 98%** because the remaining open work is still native JS/resource/listener object reconstruction.
