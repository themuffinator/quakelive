# Toolchain CI Checks

The repository includes a GitHub Actions workflow that exercises both sides of the build tooling so regressions are caught early.【F:.github/workflows/toolchain.yml†L1-L26】 The jobs are intentionally lightweight and focus on prerequisites and reference artefacts instead of performing full builds.

## QVM toolchain guard

The `qvm-prereqs` job runs on Ubuntu and executes `tools/ci/verify-qvm-toolchain.sh`, which ensures that the legacy QVM builders can still be produced on demand.【F:.github/workflows/toolchain.yml†L11-L15】【F:tools/ci/verify-qvm-toolchain.sh†L1-L45】 The script checks that `perl`, `make`, and `gcc` are available, dry-runs the `src/q3asm/` and `src/lcc/` makefiles, and confirms that the wrapper scripts (`game.sh`, `cgame.sh`, `q3_ui.sh`) are still present in the expected locations. Any missing prerequisite fails the job immediately.

## Windows reference validation

The optional `windows-reference` job runs on GitHub’s `windows-latest` image and performs two PowerShell checks.【F:.github/workflows/toolchain.yml†L17-L25】 First, `tools/ci/verify-vs-toolchain.ps1` searches the host for a Visual Studio installation that exposes the `v100` toolset and reports (or fails) if it cannot be located.【F:tools/ci/verify-vs-toolchain.ps1†L1-L74】 Second, `tools/ci/verify-dll-exports.ps1` locates `dumpbin.exe` and validates that the archived Quake Live binaries still advertise the expected exports and CRT imports.【F:tools/ci/verify-dll-exports.ps1†L1-L83】 The job is marked `continue-on-error` so that missing VS2010 components surface as warnings without blocking other automation until a proper runner is configured.
