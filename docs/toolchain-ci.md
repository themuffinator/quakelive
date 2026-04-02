# Toolchain CI Checks

[![Harnesses (QVM)](https://github.com/quakelive-reverse/quakelive-reverse/actions/workflows/deterministic-harnesses.yml/badge.svg?branch=main&job=Harnesses%20(QVM))](https://github.com/quakelive-reverse/quakelive-reverse/actions/workflows/deterministic-harnesses.yml)
[![Harnesses (DLL)](https://github.com/quakelive-reverse/quakelive-reverse/actions/workflows/deterministic-harnesses.yml/badge.svg?branch=main&job=Harnesses%20(DLL))](https://github.com/quakelive-reverse/quakelive-reverse/actions/workflows/deterministic-harnesses.yml)

GitHub Actions now keeps the QVM and native DLL toolchain guards inside the `Deterministic Harnesses` matrix. That preserves separate status visibility for the QVM and DLL lanes without maintaining redundant standalone workflows.

## QVM toolchain guard

The `Harnesses (QVM)` job runs on Ubuntu, executes `tools/ci/verify-qvm-toolchain.sh`, rebuilds the clean-room shared objects, and then runs `tests/run_harnesses.py --target qvm`. The prerequisite script still validates `perl`, `make`, `gcc`, the legacy `src/q3asm/` and `src/lcc/` makefiles, and the historical wrapper scripts before the harnesses start.

## Native DLL validation

The `Harnesses (DLL)` job runs on `windows-latest` and keeps the old native guard coverage inside the matrix lane before it executes the shared harness bundle. The lane now:

1. Installs the optional Visual Studio 2010 `v100` component.
2. Verifies that the `v100` toolset and `dumpbin.exe` are available.
3. Runs `tools/ci/validate-windows-native.ps1 -PlatformToolset v100`, which audits project metadata, checks the retail launcher payload and CRT availability, builds `Release|Win32`, validates `awesomium_process.exe`, and asserts the gameplay DLL export manifest.
4. Runs `tests/test_default_cfg_presence.py` and `tests/run_harnesses.py --target dll` so the parity harnesses operate on the same verified native pipeline.

## Optional modern-host path

The checked-in native project defaults remain on `v100`, but local contributors
can also validate a compatibility-oriented `v141` override on current Windows
hosts:

1. Install the Visual Studio 2017 `v141` component with `pwsh tools/ci/install-vs-toolset.ps1 -PlatformToolset v141`.
2. Verify that the toolset and `dumpbin.exe` are available with `pwsh tools/ci/verify-vs-toolchain.ps1 -PlatformToolset v141 -RequireToolset`.
3. Run `pwsh tools/ci/validate-windows-native.ps1 -PlatformToolset v141 -RuntimeProfile modern`, which keeps the checked-in project defaults on `v100`, validates the launcher payload plus modern CRT availability, builds the native targets with a command-line toolset override, and checks the rebuilt gameplay DLL export manifest.

## Runbook Quick Reference

- Re-run the QVM prerequisite guard locally with `tools/ci/verify-qvm-toolchain.sh`.
- Re-run the native DLL guard locally with `pwsh tools/ci/install-vs-v100.ps1`, `pwsh tools/ci/verify-vs-toolchain.ps1 -RequireV100`, and `pwsh tools/ci/validate-windows-native.ps1 -PlatformToolset v100`.
- Re-run the modern-host compatibility guard locally with `pwsh tools/ci/install-vs-toolset.ps1 -PlatformToolset v141`, `pwsh tools/ci/verify-vs-toolchain.ps1 -PlatformToolset v141 -RequireToolset`, and `pwsh tools/ci/validate-windows-native.ps1 -PlatformToolset v141 -RuntimeProfile modern`.
- Re-run the shared harness bundle with `python tests/run_harnesses.py --target qvm` or `python tests/run_harnesses.py --target dll` after the prerequisite steps above.
