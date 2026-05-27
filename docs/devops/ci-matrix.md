# Deterministic Validation Matrix

Hosted GitHub Actions now cover the continuous push and nightly packaging
edges, while the deeper deterministic target matrix remains available as a
local/manual runbook. The same three gameplay flavours remain the expected
validation surface: bytecode, native, and reverse-engineered targets.

## Hosted lanes

- **Push Verification** – `.github/workflows/push-verification.yml` runs on
  every push, fanning out across the module, renderer, UI, client, qcommon,
  server, and engine host/support parity gates plus Linux/macOS native
  source builds. It uploads the existing subsystem evidence roots and build outputs
  with a 14-day retention window.
- **Nightly Build** – `.github/workflows/nightly-build.yml` runs daily at
  `03:17 UTC`, resolves shared version metadata up front, builds Linux/macOS
  native outputs, builds the Windows `v143` modern compatibility profile,
  generates a manifest version like `nightly-YYYYMMDD.<run>-g<shortsha>`,
  uploads versioned workflow artifacts for 30 days, and creates or updates a
  prerelease GitHub Release containing the Linux tarball, macOS tarball,
  Windows zip, release manifest, checksum file, version manifest, and release
  notes. The package excludes retail pk3 files, retail launcher DLL payloads,
  and any live-service credentials.

## Matrix jobs

- **QVM** – Run on a Unix-like host, re-validate the legacy toolchain, reuse the clean-room build helper, and drive the deterministic harness suite against the VM output.【F:tests/run_harnesses.py†L24-L112】
- **DLL** – Run on Windows, provision the Visual Studio 2010 components as needed, verify the `v100` toolset, validate the retail-aligned Windows native pipeline, and then execute the shared harness runner.【F:tests/run_harnesses.py†L24-L112】
- **Reverse** – Run on a Unix-like host, rebuild the clean-room modules via `tools/ci/build-cleanroom.sh`, and extend the harness invocation with the reverse build root so the trace harness can diff the clean-room binaries against the expected transcript.【F:tests/run_harnesses.py†L24-L112】
- **POSIX native builds** – Run on hosted Linux and macOS through
  `tools/ci/build-posix-native.sh` to compile the current baseq3 native modules
  from the real `src/code`/`src/game` source lists and the dedicated-host
  makefile target into `.so`/`.dylib` packages without launching the game or
  requiring retail assets.

## Artefacts

`tests/run_harnesses.py` emits deterministic match timelines, HUD hash captures, weapon timing baselines, and text summaries for every target, while the reverse leg adds normalised trace logs and diffs.【F:tests/run_harnesses.py†L27-L116】 These artefacts land underneath `artifacts/tests/<suite>/<target>/latest/` when run locally. In particular:

- `logs/<target>/latest/*.log` – Harness summaries for the match, client regression, and trace suites.
- `match_sim/<target>/latest/<slug>/timeline.json` – Deterministic bot timelines for each bundled scenario (`duel`, `overtime`, and `loadouts`).
- `match_sim/<target>/latest/index.json` – Inventory of published match simulations with metadata (frame counts, seeds, etc.).
- `client_regression/<target>/latest/hud_hashes.json` – Stable HUD hashes replayed from the regression snapshots.
- `weapon_timings/<target>/latest/baseline.json` – Reload/refire and ammo pickup baselines diffed against HLIL tables.
- `trace/<target>/latest/*` – Reverse-only logs and diffs that compare the clean-room output with the expectation.

Re-run the harness locally with the shared entry points:

```bash
python tests/run_harnesses.py --target qvm
python tests/run_harnesses.py --target dll
python tests/run_harnesses.py --target re --reverse-build-root build/re/linux
```

## Status reporting

Capture local run logs and artefacts alongside the relevant audit or implementation note when a matrix leg is re-run. With hosted workflows disabled, those checked-in artefacts are now the authoritative validation evidence.
