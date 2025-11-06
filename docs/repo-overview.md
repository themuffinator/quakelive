# Repository Overview

## Purpose
This repository aims to reverse-engineer Quake Live by starting from the public Quake III Arena source code and progressively reshaping it to match the Quake Live codebase as closely as possible. Supporting reference material extracted from game binaries and assets is included to guide the reconstruction effort.

## Top-Level Layout
- `docs/`: Living documentation covering build pipelines, reverse-engineering stages,
  gameplay audits, onboarding flows, and testing playbooks. Begin with the
  onboarding overview and reverse-engineering handbook to discover current
  processes and artefact indices.【F:docs/onboarding/overview.md†L1-L89】【F:docs/reverse-engineering/handbook.md†L1-L56】
- `references/`: Archival material gathered from both Quake III Arena and Quake Live
  to inform the reverse-engineering process. It is split into HLIL exports and
  extracted assets used during parity checks.【F:docs/onboarding/overview.md†L6-L19】
- `src/`: The active working tree for the reconstructed codebase. It mirrors the
  Quake III Arena GPL drop and is the foundation for porting Quake Live features,
  including engine, game VM, renderer, and bundled tool sources.【F:docs/onboarding/overview.md†L6-L15】
- `src-re/`: Clean-room reconstruction space containing annotated walkthroughs,
  prototype shims, and signed-off clean sources compiled via the clean-room
  helpers and traced against Quake Live baselines.【F:docs/onboarding/overview.md†L11-L18】【F:docs/reverse-engineering/handbook.md†L7-L36】
- `tests/`: Deterministic harness entry points and fixtures that back the CI matrix
  for QVM, native DLL, and reverse builds.【F:docs/onboarding/overview.md†L12-L20】【F:tests/run_harnesses.py†L27-L116】
- `tools/`: Automation that powers CI guardrails, deterministic harness execution,
  and container definitions for historical toolchains.【F:docs/onboarding/overview.md†L18-L24】【F:docs/toolchain-ci.md†L1-L24】
- `artifacts/` & `logs/`: Captured outputs from deterministic harnesses, trace runs,
  and reverse build shims published by CI for review.【F:docs/onboarding/overview.md†L21-L27】【F:docs/devops/ci-matrix.md†L1-L34】
- `.github/workflows/`: Automation wiring for the toolchain guard, native DLL, and
  deterministic harness pipelines that enforce reproducibility on every push.【F:.github/workflows/toolchain.yml†L1-L15】【F:.github/workflows/windows-native.yml†L1-L27】【F:.github/workflows/deterministic-harnesses.yml†L10-L93】

## Reverse-Engineering Workflow Notes
- The HLIL exports are available for both Quake III (`references/hlil/quake3/`) and
  Quake Live (`references/hlil/quakelive/`). Keeping the two sets side-by-side
  enables systematic diffing between the retail Quake III code and the decompiled
  Quake Live functions when porting behaviour.【F:docs/onboarding/overview.md†L6-L19】
- Quake Live assets under `references/original-assets/quakelive/` expose binary
  modules (`cgamex86.dll`, `qagamex86.dll`, `uix86.dll`, etc.) and supporting data
  (fonts, icons, maps) to validate assumptions or reproduce file formats.【F:docs/onboarding/overview.md†L6-L19】
- The active `src/` tree should evolve from the Quake III baseline towards Quake
  Live parity while the clean-room `src-re/` prototypes and sign-off drops are
  traced through the deterministic harness for regression coverage.【F:docs/reverse-engineering/handbook.md†L11-L36】【F:docs/devops/ci-matrix.md†L1-L34】
- Tests under `tests/` and automation under `tools/ci/` feed the deterministic
  harness workflow, publishing artefacts into `artifacts/` and `logs/` so
  reviewers can inspect parity evidence without rerunning the suites locally.【F:docs/devops/ci-matrix.md†L1-L34】【F:tests/run_harnesses.py†L27-L116】
- CI workflows enforce the toolchain and harness guardrails on Linux and Windows
  hosts, mirroring the scripts documented in the onboarding guide to keep the
  reconstructed builds reproducible.【F:.github/workflows/toolchain.yml†L1-L15】【F:.github/workflows/windows-native.yml†L1-L27】【F:.github/workflows/deterministic-harnesses.yml†L10-L93】

## Next Steps for Contributors
1. Skim the onboarding overview and reverse-engineering handbook to understand the
   repository layout, stage outputs, and review cadence before diving into code or
   artefacts.【F:docs/onboarding/overview.md†L1-L89】【F:docs/reverse-engineering/handbook.md†L1-L60】
2. Familiarise yourself with the HLIL dump organisation in `references/hlil/` and
   compare modules in `src/` and `src-re/` against their Quake Live counterparts to
   identify behaviour gaps that must be ported.【F:docs/onboarding/overview.md†L6-L19】【F:docs/reverse-engineering/handbook.md†L11-L36】
3. Run `tests/run_harnesses.py` locally (QVM, DLL, and reverse targets) to align
   with the deterministic harness matrix and inspect the artefacts emitted under
   `artifacts/` and `logs/`.【F:tests/run_harnesses.py†L27-L116】【F:docs/devops/ci-matrix.md†L1-L34】
4. Keep this overview updated as the project introduces new directories, tooling,
   or automation, and reference the living build notes in [`docs/qvmtools.md`](qvmtools.md),
   [`docs/windows-native-pipeline.md`](windows-native-pipeline.md), and the
   [`Native Toolchain Support Matrix`](platform/toolchain-matrix.md) when
   reproducing legacy toolchains.【F:docs/platform/toolchain-matrix.md†L1-L18】

## Controls & Configuration Defaults
- **Reference bindings** – The Quake Live snapshot in `references/original-assets/quakelive/baseq3/default.cfg` captures the modernized control scheme (weapon toggle on `F`, dedicated drop bindings, vote shortcuts, etc.).【68ce2a†L215-L224】【fcaf97†L1-L86】 Ported builds should ship this file—alongside curated training configs such as `tim.cfg` and `sponge.cfg`—so the engine can execute `exec default.cfg` during bootstrap without diverging from retail expectations.【F:src/code/qcommon/common.c†L2389-L2405】【F:src/code/ui/ui_main.c†L3223-L3263】
- **Packaging requirement** – Ensure any PK3 or installer produced from this repo places the Quake Live `default.cfg` at the data root; the filesystem layer treats its absence as a fatal error.【F:src/code/qcommon/files.c†L3260-L3314】 Coordinate asset packaging with the workflow outlined in `docs/quakelive_asset_audit.md` so HUD/menu assets and configuration defaults stay in sync.

## Documentation Backlog
A curated backlog of in-progress documentation efforts lives in `docs/documentation-backlog.md`. New contributors should review it to understand pending write-ups for behaviour deltas, platform support notes, and HUD/menu follow-ups before starting related work.
