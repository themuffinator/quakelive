# Deterministic CI Matrix

The deterministic harness workflow runs both gameplay targets (QVM bytecode and Windows DLLs) so regressions surface regardless of build flavour. The workflow fans out into two jobs using a `target` matrix:

- **Harnesses (QVM)** runs on `ubuntu-latest`, verifies the legacy toolchain, and executes the harness suite against the bytecode output.
- **Harnesses (DLL)** runs on `windows-latest`, installs the Visual Studio 2010 components, verifies the `v100` toolset, builds the gameplay DLLs, asserts their export tables against the manifest, and executes the same harness suite.

Each job drives `tests/run_harnesses.py`, which materialises deterministic artefacts underneath the shared `ARTIFACT_ROOT` (`artifacts/tests/<suite>/<target>/`):

- `match_sim/<target>/timeline.json` – JSON timeline from the scripted match simulation.
- `client_regression/<target>/hud_hashes.json` – Stable HUD hash captures from the client regression harness.
- `logs/<target>/*.log` – Text summaries confirming the harness outcomes and runtime metadata.

The upload step now runs with `if: always()` so the logs survive failing harness runs, and [`actions/upload-artifact`](https://github.com/actions/upload-artifact) explicitly targets the JSON timelines, HUD hashes, and log outputs for quick discovery.【F:.github/workflows/deterministic-harnesses.yml†L15-L64】 Artefacts are retained for seven days, providing a convenient paper trail for triage. The harness driver itself lives alongside the repository tests and can be invoked locally:

```bash
python tests/run_harnesses.py --target qvm
python tests/run_harnesses.py --target dll
```

## Status badges

Embed the workflow badges anywhere documentation surfaces build health (e.g., the repository overview or internal dashboards):

- ![Harnesses (QVM)](https://github.com/quakelive-reverse/quakelive-reverse/actions/workflows/deterministic-harnesses.yml/badge.svg?branch=main&job=Harnesses%20(QVM))
- ![Harnesses (DLL)](https://github.com/quakelive-reverse/quakelive-reverse/actions/workflows/deterministic-harnesses.yml/badge.svg?branch=main&job=Harnesses%20(DLL))

These badges reflect the status of each matrix leg independently thanks to the `job` query parameter, making it easy to spot which target failed.
