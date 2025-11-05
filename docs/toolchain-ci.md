# Toolchain CI Checks

Two dedicated GitHub Actions workflows cover the legacy QVM toolchain and the Windows-native DLL pipeline so regressions are caught early.【F:.github/workflows/toolchain.yml†L1-L18】【F:.github/workflows/windows-native.yml†L1-L26】 The jobs remain intentionally lightweight, focusing on prerequisite validation and export-surface checks instead of running full gameplay tests.

## QVM toolchain guard

The `Toolchain (QVM)` workflow exposes a single `qvm-prereqs` job that runs on Ubuntu and executes `tools/ci/verify-qvm-toolchain.sh`, ensuring that the legacy QVM builders can still be produced on demand.【F:.github/workflows/toolchain.yml†L1-L18】【F:tools/ci/verify-qvm-toolchain.sh†L1-L45】 The script checks that `perl`, `make`, and `gcc` are available, dry-runs the `src/q3asm/` and `src/lcc/` makefiles, and confirms that the wrapper scripts (`game.sh`, `cgame.sh`, `q3_ui.sh`) are still present in the expected locations. Any missing prerequisite fails the job immediately.

## Native DLL validation

The `Native DLL (VS2010)` workflow runs on GitHub’s `windows-latest` image and builds the Quake Live gameplay DLLs with the `v100` toolset before verifying their export surface.【F:.github/workflows/windows-native.yml†L1-L26】 The pipeline performs four steps:

1. `tools/ci/install-vs-v100.ps1` installs the optional Visual Studio 2010 component (`Microsoft.VisualStudio.Component.VC.v100.x86.x64`) if it is not already present on the runner.【F:tools/ci/install-vs-v100.ps1†L1-L63】
2. `tools/ci/verify-vs-toolchain.ps1 -RequireV100` confirms that the `v100` toolset and `dumpbin.exe` are now available, failing the build if the prerequisites remain missing.【F:tools/ci/verify-vs-toolchain.ps1†L1-L74】
3. `tools/ci/build-windows-dlls.ps1` drives `msbuild` against `src/code/quake3.sln` with the Win32/Release configuration and forces the `v100` platform toolset so the produced DLLs match the historical binaries.【F:tools/ci/build-windows-dlls.ps1†L1-L36】【F:src/code/quake3.sln†L1-L4】
4. `tools/ci/assert-dll-exports.ps1` scans the built artefacts, runs `dumpbin` (or `objdump` as a fallback) across each DLL, and compares the discovered exports against the manifest stored in `tools/ci/manifests/native-dll-exports.json` so regressions are surfaced immediately.【F:tools/ci/assert-dll-exports.ps1†L1-L152】【F:tools/ci/manifests/native-dll-exports.json†L1-L14】

Each workflow now reports its status independently, enabling separate CI badges for the QVM and native build legs as outlined in the build migration plan.【F:docs/build-pipeline.md†L64-L69】
