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

## Runbook Quick Reference

- Re-run the QVM prerequisite guard locally with `tools/ci/verify-qvm-toolchain.sh`.
- Re-run the native DLL guard locally with `pwsh tools/ci/install-vs-v100.ps1`, `pwsh tools/ci/verify-vs-toolchain.ps1 -RequireV100`, and `pwsh tools/ci/validate-windows-native.ps1 -PlatformToolset v100`.
- Re-run the shared harness bundle with `python tests/run_harnesses.py --target qvm` or `python tests/run_harnesses.py --target dll` after the prerequisite steps above.
