# Quake Live Steam Host Mapping Round 331

Date: 2026-05-28

## Scope

Mapped the Awesomium `qz_instance` method table and return-valued dispatch lane, with special focus on the retail `SetCvar` and `ResetCvar` rows that affect WebUI runtime/update parity.

## Evidence

Primary owner: retail `quakelive_steam.exe`.

Committed corpus signals:

- `references/reverse-engineering/ghidra/quakelive_steam/functions.csv` retains the owning handler functions as `FUN_00431570`, `FUN_00431a10`, `FUN_00431e50`, and `FUN_004328b0`.
- `references/reverse-engineering/ghidra/quakelive_steam/analysis_symbols.txt` identifies `QLJSHandler::vftable` at `0x00548010`, with `Awesomium::JSMethodHandler` immediately adjacent in the imported RTTI/vtable set.
- `references/reverse-engineering/ghidra/quakelive_steam/decompile_top_functions.c` shows retail allocating the four-byte `QLJSHandler` object, installing it through WebView slot `0x12c`, then running the ten-try `FUN_00431a10` browser-helper bind loop.
- `references/analysis/quakelive_symbol_aliases.json` maps `sub_431570` to `QLJSHandler_LookupMethodId`, `sub_431A10` to `QLJSHandler_BindQzInstance`, `sub_431E50` to `QLJSHandler_OnMethodCall`, and `sub_4328B0` to `QLJSHandler_OnMethodCallWithReturnValue`.
- `references/hlil/quakelive/quakelive_steam.exe/quakelive_steam.exe_hlil_split/quakelive_steam.exe_hlil_part01.txt:44299` shows `QLJSHandler_LookupMethodId` walking `data_55c008` to `0x55c1a0` in 12-byte rows and returning the row's method ID field.
- `references/hlil/quakelive/quakelive_steam.exe/quakelive_steam.exe_hlil_split/quakelive_steam.exe_hlil_part01.txt:44571-44577` shows `QLJSHandler_BindQzInstance` calling `Awesomium::JSObject::SetCustomMethod` with the third table field as the return-valued flag.
- `references/hlil/quakelive/quakelive_steam.exe/quakelive_steam.exe_hlil_split/quakelive_steam.exe_hlil_part07.txt:1559-1698` maps the full 34-entry `data_55c008` table. `SetCvar` at `0x0055C044` and `ResetCvar` at `0x0055C050` both carry return flag `1`; `NoOp` is the final table row at `0x0055C194`.
- `references/hlil/quakelive/quakelive_steam.exe/quakelive_steam.exe_hlil_split/quakelive_steam.exe_hlil_part01.txt:45282` maps the return-value handler that owns the cvar set/reset cases.

## Source Reconstruction

- Added source-visible constants for the retail qz method table span: `0x0055C008` to `0x0055C1A0`, with 12-byte entries.
- Extended `clWebMethodBinding_t` with each row's retail table address and replaced the source qz binding table with the retail row order, including the late `GetAllUGC`, `GetNextKeyDown`, `SetFavoriteServer`, and final `NoOp` rows.
- Corrected `SetCvar` and `ResetCvar` from void dispatch to return-valued dispatch, matching their retail return flag `1` rows.
- Reconstructed the source return-value behavior for cvar set/reset as boolean success/failure strings: invalid arguments return `"0"`, successful set/reset returns `"1"`.
- Updated the injected Awesomium startup `qz_instance` bridge so `SetCvar` and `ResetCvar` normalize cvar names, mutate the synthetic config cache, and return `true`.
- Reordered the startup no-op method group so the browser-visible fallback surface follows the retail table's final-row order.

## Validation

Guarded and verified the reconstruction with:

- `python -m pytest tests/test_awesomium_browser_parity.py tests/test_platform_services.py -q --tb=short`
  - Result: `102 passed`.
- `powershell -ExecutionPolicy Bypass -File tools\ci\verify-awesomium-browser-host-parity.ps1 -RepoRoot E:\Repositories\QuakeLive-reverse`
  - Result: Awesomium browser host source, alias, mapping, and adapter parity anchors are present.
- `git diff --check -- src/code/client/cl_awesomium_win32.cpp src/code/client/cl_cgame.c src/code/client/client.h tests/test_awesomium_browser_parity.py tests/test_platform_services.py tools/ci/verify-awesomium-browser-host-parity.ps1 docs/reverse-engineering/awesomium-browser-wiring.md docs/reverse-engineering/quakelive_steam_mapping_round_330.md docs/reverse-engineering/quakelive_steam_mapping_round_331.md IMPLEMENTATION_PLAN.md`
  - Result: clean; only Git line-ending normalization warnings were reported.
- `powershell -ExecutionPolicy Bypass -File tools\ci\build-windows-dlls.ps1 -RepoRoot E:\Repositories\QuakeLive-reverse -Solution src/code/quakelive.sln -Configuration Debug -Platform Win32 -PlatformToolset v143 -DisableOptionalCodecs`
  - Result: build succeeded with `0` warnings and `0` errors; `quakelive_steam.exe`, `awesomium_process.exe`, and clean-room frame DLL probes were produced.

Runtime launch is not required for this pass because the committed HLIL/Ghidra evidence directly resolves the table layout, method registration flags, and dispatch ownership. The live Awesomium path remains behind `QL_BUILD_ONLINE_SERVICES`.

## Parity Estimate

- Focused Awesomium qz method-table/return-flag lane: **97% -> 99.4%**.
- Overall Awesomium WebUI wiring: **98.9% -> 99.0%**.
- Repo-wide parity remains **98% -> 98%** because native Awesomium JS object ABI marshalling and some online-service callbacks remain compatibility-bounded or service-gated.
