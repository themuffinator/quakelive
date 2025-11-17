# Repository Overview

## Purpose
This repository aims to reverse-engineer Quake Live by starting from the public Quake III Arena source code and progressively reshaping it to match the Quake Live codebase as closely as possible. Supporting reference material extracted from game binaries and assets is included to guide the reconstruction effort.

## Top-Level Layout
- `references/`: Archival material gathered from both Quake III Arena and Quake Live to inform the reverse-engineering process. It is split into:
  - `hlil/`: High Level Intermediate Language (HLIL) output produced by Binary Ninja for a range of Quake Live and Quake III binaries. Each binary has a monolithic HLIL text dump (`*.txt`) and a `*_split/` directory containing per-function files for easier comparison and diffing.
  - `original-assets/`: A snapshot of upstream assets. The `quake3/src/` subtree mirrors the original Quake III Arena source distribution, while `quakelive/` collects extracted Quake Live game assets (e.g. DLLs, bot files, maps) for reference while rebuilding features.
- `src/`: The active working tree for the reconstructed codebase. It currently matches the Quake III Arena source and provides the starting point for Quake Live specific changes. Key subdirectories include:
  - `code/`: Engine and game VM sources. This houses the client (`client/`), game logic (`game/`), UI module (`ui/`), bot library (`botlib/`), renderer (`renderer/`), and supporting build files for different platforms (e.g. `win32/`, `unix/`, Visual Studio project files).
  - `common/`: Shared utilities (math, BSP parsing, command handling, etc.) used by tools and the engine during asset processing.
  - `lcc/`, `q3asm/`: Toolchain components for compiling the Quake Virtual Machine (QVM) bytecode.
  - `libs/`: Third-party libraries bundled with the original Quake III source (JPEG, zlib, etc.).
  - `q3map/`, `q3radiant/`: Level compilation and editing tools that ship with the Quake III source release.
  - `ui/`: Original mission pack UI sources included with the id Software release.
- `src-re/`: Clean-room reconstruction workspace that holds annotated walkthroughs, vetted shims, and the replayable clean builds compiled by the reverse CI legs.【F:docs/reverse-engineering/handbook.md†L7-L34】
- `tests/`: Deterministic harness entry points plus committed expectations that back the regression workflows across QVM, native DLL, and reverse targets.【F:tests/run_harnesses.py†L27-L116】【F:docs/devops/ci-matrix.md†L1-L18】
- `tools/`: Automation and CI helpers used to stand up historical toolchains, build clean-room artefacts, and publish comparison data during review.【F:docs/toolchain-ci.md†L1-L24】【F:tools/ci/build-cleanroom.sh†L1-L44】
- `artifacts/`: Structured output from the deterministic harnesses, including timelines, HUD hashes, and trace diffs organised per suite/target for downstream analysis.【F:docs/devops/ci-matrix.md†L15-L38】
- `logs/`: Harness and workflow logs mirrored from CI so reviewers can inspect failure evidence without rerunning suites locally.【F:docs/devops/ci-matrix.md†L15-L34】
- `ghidra_scripts/`: Automation used during symbol extraction and binary analysis passes, notably the export script that seeds the normalised symbol maps for the clean-room stages.【F:docs/reverse-engineering/handbook.md†L31-L37】
- `docs/`: Living documentation covering build pipelines, reverse-engineering stages, gameplay audits, and test harnesses. Start with the reverse-engineering handbook, CI matrix, and documentation backlog when orienting yourself.【F:docs/reverse-engineering/handbook.md†L1-L37】【F:docs/devops/ci-matrix.md†L1-L38】【F:docs/documentation-backlog.md†L1-L29】

## Reverse-Engineering Workflow Notes
- The HLIL exports are available for both Quake III (`references/hlil/quake3/`) and
  Quake Live (`references/hlil/quakelive/`). Keeping the two sets side-by-side
  enables systematic diffing between the retail Quake III code and the decompiled
  Quake Live functions when porting behaviour.【F:docs/onboarding/overview.md†L6-L19】
- Quake Live assets under `references/original-assets/quakelive/` expose binary
  modules (`cgamex86.dll`, `qagamex86.dll`, etc.) and supporting data
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

## CI & Workflow References
- **Toolchain (QVM):** Exercises the GPL-era QVM toolchain on every push/PR via `tools/ci/verify-qvm-toolchain.sh`, ensuring the legacy bytecode pipeline stays reproducible.【F:.github/workflows/toolchain.yml†L1-L15】【F:tools/ci/verify-qvm-toolchain.sh†L1-L45】
- **Native DLL (VS2010):** Provisions Visual Studio 2010, rebuilds the Win32 gameplay DLLs, and validates their export surface with the shared PowerShell helpers.【F:.github/workflows/windows-native.yml†L1-L27】【F:tools/ci/build-windows-dlls.ps1†L1-L36】【F:tools/ci/assert-dll-exports.ps1†L1-L152】
- **Deterministic Harnesses:** Fans out across QVM, DLL, and reverse targets, reusing the clean-room build helper and uploading artefacts/logs under `artifacts/` and `logs/` for review.【F:.github/workflows/deterministic-harnesses.yml†L10-L93】【F:docs/devops/ci-matrix.md†L15-L38】

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
