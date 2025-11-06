# Deterministic CI Matrix

The **Deterministic Harnesses** workflow executes the regression harnesses against every gameplay flavour on each push and pull request. A matrix fans the workflow out across the bytecode, native, and reverse-engineered targets so they execute the same pipeline in parallel.【F:.github/workflows/deterministic-harnesses.yml†L10-L33】

## Matrix jobs

- **Harnesses (QVM)** – Runs on `ubuntu-latest`, re-validates the legacy toolchain, reuses the clean-room build helper, and drives the deterministic harness suite against the VM output.【F:.github/workflows/deterministic-harnesses.yml†L16-L47】【F:.github/workflows/deterministic-harnesses.yml†L74-L79】
- **Harnesses (DLL)** – Runs on `windows-latest`, provisions the Visual Studio 2010 components, verifies the `v100` toolset, rebuilds the gameplay DLLs, checks their export table, and then executes the shared harness runner.【F:.github/workflows/deterministic-harnesses.yml†L22-L79】
- **Harnesses (Reverse)** – Shares the Linux leg and extends the harness invocation with the reverse build root so the trace harness can diff the clean-room binaries against the expected transcript.【F:.github/workflows/deterministic-harnesses.yml†L28-L47】【F:.github/workflows/deterministic-harnesses.yml†L74-L79】

## Artefacts

`tests/run_harnesses.py` emits a deterministic match timeline, HUD hash capture, and text summaries for every target, while the reverse leg adds normalised trace logs and diffs.【F:tests/run_harnesses.py†L27-L111】 These artefacts land underneath `artifacts/tests/<suite>/<target>/`, and the workflow uploads them even when a harness fails so the evidence is always available.【F:.github/workflows/deterministic-harnesses.yml†L81-L93】 In particular:

- `logs/<target>/*.log` – Harness summaries for the match, client regression, and trace suites.
- `match_sim/<target>/timeline.json` – The deterministic bot timeline from the scripted match.
- `client_regression/<target>/hud_hashes.json` – Stable HUD hashes replayed from the regression snapshots.
- `trace/<target>/*` – Reverse-only logs and diffs that compare the clean-room output with the expectation.

Re-run the harness locally with the same entry point used by CI:

```bash
python tests/run_harnesses.py --target qvm
python tests/run_harnesses.py --target dll
```

## Status badges

Embed the workflow badges anywhere documentation surfaces build health (for example, in dashboards or the repository overview):

- ![Harnesses (QVM)](https://github.com/quakelive-reverse/quakelive-reverse/actions/workflows/deterministic-harnesses.yml/badge.svg?branch=main&job=Harnesses%20(QVM))
- ![Harnesses (DLL)](https://github.com/quakelive-reverse/quakelive-reverse/actions/workflows/deterministic-harnesses.yml/badge.svg?branch=main&job=Harnesses%20(DLL))

Because the badge `job` parameter targets a single matrix leg, the status of each gameplay flavour is visible at a glance.
