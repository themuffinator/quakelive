# Repository Overview

## Purpose
This repository aims to reverse-engineer Quake Live by starting from the public Quake III Arena source code and progressively reshaping it to match the Quake Live codebase as closely as possible. Supporting reference material extracted from game binaries and assets is included to guide the reconstruction effort.

## Top-Level Layout
- `references/`: Archival material gathered from both Quake III Arena and Quake Live to inform the reverse-engineering process. It is split into:
  - `hlil/`: High Level Intermediate Language (HLIL) output produced by Binary Ninja for a range of Quake Live and Quake III binaries. Each binary has a monolithic HLIL text dump (`*.txt`) and a `*_split/` directory containing per-function files for easier comparison and diffing.
  - `reverse-engineering/ghidra/`: OpenAlice-style committed Ghidra exports for the retail Quake Live binaries, including metadata, imports/exports, function inventories, analyst-promoted symbols, and top-function decompiles.
- `assets/`: A snapshot of upstream assets. The `quake3/src/` subtree mirrors the original Quake III Arena source distribution, while `quakelive/` collects extracted Quake Live game assets (e.g. DLLs, bot files, maps) for reference while rebuilding features. Treat this directory as read-only so it continues to reflect the shipping data layout.
- `src/`: The active working tree for the reconstructed codebase. It currently matches the Quake III Arena source and provides the starting point for Quake Live specific changes. Key subdirectories include:
  - `code/`: Engine and game VM sources. This houses the client (`client/`), game logic (`game/`), UI module (`ui/`), bot library (`botlib/`), renderer (`renderer/`), and supporting build files for different platforms (e.g. `win32/`, `unix/`, Visual Studio project files).
  - `common/`: Shared utilities and cross-cutting support code. This directory still carries the classic Quake III tool-side helpers (`cmdlib`, `mathlib`, BSP/image helpers, threading helpers) used by `q3map` and related tools, and it now also carries active Quake Live runtime layers such as credential parsing and platform/authentication services consumed by the engine and gameplay DLLs.
  - `game/`: Writable Quake Live gameplay support sources that sit beside, rather than directly inside, the original GPL-era `src/code/game/` tree. The current contents are active build inputs (`g_config.c`, `g_match_config.c`, related headers) plus gameplay fixture utilities under `src/game/tests/` that are shared by native and QVM harnesses.
  - `lcc/`, `q3asm/`: Toolchain components for compiling the Quake Virtual Machine (QVM) bytecode.
  - `libs/`: Third-party libraries bundled with the original Quake III source (JPEG, zlib, etc.).
  - `q3map/`, `q3radiant/`: Level compilation and editing tools that ship with the Quake III source release.
  - `ui/`: Original mission pack UI sources included with the id Software release.
- `src-re/`: Clean-room reconstruction workspace that holds annotated walkthroughs, vetted shims, and the replayable clean builds compiled by the reverse CI legs. Treat it as a separate staging area: `src-re/include/` already provides active reverse-engineered headers consumed by `src/code/`, `src-re/prototypes/` is built by the reverse clean-room CI legs, and `src-re/annotated/` plus `src-re/clean/` remain analysis/review artefacts rather than production runtime sources. See [`docs/reverse-engineering/src-re-workspace.md`](reverse-engineering/src-re-workspace.md) for the directory policy and promotion rules.【F:docs/reverse-engineering/handbook.md†L7-L34】
- `tests/`: Deterministic harness entry points plus committed expectations that back the regression workflows across QVM, native DLL, and reverse targets.【F:tests/run_harnesses.py†L27-L116】【F:docs/devops/ci-matrix.md†L1-L18】
- `tools/`: Automation and CI helpers used to stand up historical toolchains, build clean-room artefacts, and publish comparison data during review.【F:docs/toolchain-ci.md†L1-L24】【F:tools/ci/build-cleanroom.sh†L1-L44】
- `artifacts/`: Structured output from the deterministic harnesses, including timelines, HUD hashes, and trace diffs organised per suite/target for downstream analysis.【F:docs/devops/ci-matrix.md†L15-L38】
- `logs/`: Harness and workflow logs mirrored from CI so reviewers can inspect failure evidence without rerunning suites locally.【F:docs/devops/ci-matrix.md†L15-L34】
- `ghidra_scripts/`: Legacy automation used during symbol extraction and binary analysis passes, notably the export script that seeds the normalised symbol maps for the clean-room stages.【F:docs/reverse-engineering/handbook.md†L31-L37】
- `scripts/ghidra/`: OpenAlice-style Ghidra tooling for generating the committed Quake Live reference corpus and bootstrapping optional GhidrAssistMCP integration.
- `docs/`: Living documentation covering build pipelines, reverse-engineering stages, gameplay audits, and test harnesses. Start with the reverse-engineering handbook, CI matrix, and documentation backlog when orienting yourself.【F:docs/reverse-engineering/handbook.md†L1-L37】【F:docs/devops/ci-matrix.md†L1-L38】【F:docs/documentation-backlog.md†L1-L29】

## Reverse-Engineering Workflow Notes
- The HLIL exports are available for both Quake III (`references/hlil/quake3/`) and
  Quake Live (`references/hlil/quakelive/`). Keeping the two sets side-by-side
  enables systematic diffing between the retail Quake III code and the decompiled
  Quake Live functions when porting behaviour.【F:docs/onboarding/overview.md†L6-L19】
- The committed Ghidra corpus under `references/reverse-engineering/ghidra/`
  mirrors the OpenAlice reverse-engineering workflow: start from metadata,
  imports/exports, and function inventory, then descend into targeted decompile
  output only after the owning subsystem is clear.
- Quake Live assets under `assets/quakelive/` expose binary
  modules (`cgamex86.dll`, `qagamex86.dll`, etc.) and supporting data
  (fonts, icons, maps) to validate assumptions or reproduce file formats.【F:docs/onboarding/overview.md†L6-L19】
- The active `src/` tree should evolve from the Quake III baseline towards Quake
  Live parity while the clean-room `src-re/` prototypes, shared ABI mirrors, and sign-off drops are
  traced through the deterministic harness for regression coverage.【F:docs/reverse-engineering/handbook.md†L11-L36】【F:docs/devops/ci-matrix.md†L1-L34】
- Tests under `tests/` and automation under `tools/ci/` feed the deterministic
  harness workflow, publishing artefacts into `artifacts/` and `logs/` so
  reviewers can inspect parity evidence without rerunning the suites locally.【F:docs/devops/ci-matrix.md†L1-L34】【F:tests/run_harnesses.py†L27-L116】
- CI workflows enforce the toolchain, filesystem, UI, and deterministic harness
  guardrails on Linux and Windows hosts, mirroring the scripts documented in the
  onboarding guide to keep the reconstructed builds reproducible.【F:.github/workflows/deterministic-harnesses.yml†L10-L89】【F:.github/workflows/filesystem-search.yml†L1-L20】【F:.github/workflows/ui-freeze.yml†L1-L17】【F:.github/workflows/ui-validation.yml†L1-L37】

## CI & Workflow References
- **Deterministic Harnesses:** Fans out across QVM, DLL, and reverse targets, runs the QVM prerequisite guard plus the retail-aligned Windows native validation inside the matrix, and uploads artefacts/logs under `artifacts/` and `logs/` for review.【F:.github/workflows/deterministic-harnesses.yml†L10-L89】【F:docs/devops/ci-matrix.md†L15-L38】
- **Filesystem Search Paths:** Runs the dedicated filesystem mount-order regression test on Ubuntu so `FS_FOpenFileRead` precedence stays stable across directory and PK3 search paths.【F:.github/workflows/filesystem-search.yml†L1-L20】【F:tests/test_fs_search_paths.py†L1-L115】
- **UI Freeze Guard:** Enforces the repository rule that the retail `src/ui/` tree remains immutable during routine reconstruction work.【F:.github/workflows/ui-freeze.yml†L1-L17】
- **UI Validation:** Builds the staged UI bundle, runs the headless validation pass, and publishes the resulting bundle/log artefacts for review.【F:.github/workflows/ui-validation.yml†L1-L37】【F:tests/run_ui_validation.py†L1-L66】

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
- **Reference bindings** – The Quake Live snapshot in `assets/quakelive/baseq3/default.cfg` captures the modernized control scheme and should ship with curated training configs (`tim.cfg`, `sponge.cfg`, `ttimo.cfg`, `syncerror.cfg`) so `exec default.cfg` during bootstrap mirrors retail expectations.【F:src/code/qcommon/common.c†L2389-L2405】【F:src/code/ui/ui_main.c†L3223-L3263】 Key Quake Live deltas from the Quake III baseline include:
  - `F` bound to `weapon toggle`, with mouse wheel/`[`/`]` handling `weapprev`/`weapnext`.
  - Arrow keys bound to item drops (`dropflag`, `dropweapon`, `droppowerup`, `droprune`).
  - Dedicated vote/ready shortcuts (`F1` vote yes, `F2` vote no, `F3` readyup).
  - `MOUSE2` for `+zoom`, `MOUSE3`/`ENTER` for `+button2`, `g` for `+button3`.
  - Utility bindings like `+acc` on `p`, `+chat` on `h`, and `F11` for `screenshotJPEG`.
- **Packaging requirement** – Ensure any PK3 or installer produced from this repo places the Quake Live `default.cfg` at the data root; the filesystem layer treats its absence as a fatal error.【F:src/code/qcommon/files.c†L3260-L3314】 The UI bundle recipe in `tools/packaging/ui_bundle_manifest.json` now stages `default.cfg`, `syncerror.cfg`, and the training profiles into `pak_uiql.pk3` via `tools/build_ui_bundle.sh`, keeping the `Cbuf_AddText("exec default.cfg\n")` bootstrap satisfied.【F:tools/packaging/ui_bundle_manifest.json†L3-L29】【F:tests/run_ui_validation.py†L16-L66】 Coordinate asset packaging with the workflow outlined in `docs/quakelive_asset_audit.md` so HUD/menu assets and configuration defaults stay in sync.

## Documentation Backlog
A curated backlog of in-progress documentation efforts lives in `docs/documentation-backlog.md`. New contributors should review it to understand pending write-ups for behaviour deltas, platform support notes, and HUD/menu follow-ups before starting related work.
