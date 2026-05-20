# Quake Live Source Reconstruction Project

[![Accuracy First](https://img.shields.io/badge/Accuracy-First-1f6feb)](AUDIT.md)
[![Ongoing Reconstruction](https://img.shields.io/badge/Reconstruction-Ongoing-b8860b)](AUDIT.md)
[![Reconstruction Plan](https://img.shields.io/badge/Work%20Queue-Reconstruction%20Plan-2ea44f)](IMPLEMENTATION_PLAN.md)
[![Getting Started](https://img.shields.io/badge/Docs-Getting%20Started-6f42c1)](docs/onboarding/overview.md)

This project reconstructs the full Quake Live source code as faithfully as possible.
It starts from the public Quake III Arena GPL source release and then rebuilds the
retail engine and game code piece by piece using retail binaries, committed HLIL and
Ghidra reference corpora, symbol maps, and runtime validation.

Accurate reconstruction is the top priority. This repository is not trying to make a
"Quake Live-like" fork or a rough gameplay approximation. The goal is to reconstruct how
the retail game actually works, document what is known, and close the remaining gaps in a
way that stays grounded in evidence instead of guesswork.

## What accurate reconstruction means here

- Retail Quake Live behavior is the target, not convenience or approximation.
- The committed retail reference corpus is treated as the source of truth when the open GPL
  baseline and the retail game differ.
- Where evidence is incomplete, small intuitive fixes or compatibility wiring may still be
  needed to keep the reconstruction working, but they should stay minimal and give way to
  stronger evidence when it appears.
- Unclear areas are tracked as open gaps instead of being filled in with confident-looking
  assumptions.
- Quake Live-specific online services can be disabled in builds when the retail dependency
  cannot yet be reconstructed cleanly or does not have an open replacement.
- Progress is measured by evidence-backed movement toward retail parity, not just by
  whether the code builds or runs.

## Current reconstruction state

This repository is an active reconstruction effort, not a retail-equivalent codebase.
The audit files, task plan, and validation artifacts record what has been
reconstructed, what has supporting evidence, and what still needs sharper verification.
Older finality language in historical audit notes should be read as evidence for bounded
checkpoints, not as a project-wide claim that reconstruction is done.

The current work is focused on rebuilding retail behavior area by area from the committed
Binary Ninja HLIL dumps, Ghidra exports, symbol maps, and targeted runtime evidence. Some
subsystems have strong validation coverage, while others still need
function-level mapping, edge-case tests, data-layout confirmation, or refreshed runtime
proof.

The active work queue remains the source of truth for what should be reconstructed next.
At the time of this README update, the leading tracks are physics reconstruction,
UI bridge/fallback verification, Race and gametype validation, and continued cleanup of
audited subsystem gaps as new evidence is promoted.

### Game reconstruction

| Area | Current reconstruction focus |
| --- | --- |
| `cgame` | Continue validating predicted movement, ownerdraw/stat payloads, UI-facing imports, and gameplay presentation against retail evidence. |
| `qagame` | Continue reconstructing server-side gameplay rules, match flow, awards, voting, team logic, and gametype-specific behavior. |
| `ui` | Keep the retail UI bridge, menu data, fallback paths, and panel/runtime assumptions under evidence-backed review. |

### Engine reconstruction

| Area | Current reconstruction focus |
| --- | --- |
| `client` | Continue mapping client/game/UI ownership, workshop and download behavior, command routing, prediction handoff, and runtime evidence freshness. |
| `renderer` | Continue validating text/font behavior, exported renderer ABI details, host wiring, and reference-backed helper ownership. |
| `qcommon` | Continue verifying filesystem, VM loading, message parsing, collision, CVar, command, and bootstrap behavior against retail references. |
| `server` | Continue validating dedicated-server behavior, Steam-compatible boundaries, game-state messaging, ranking/stat hooks, and control-plane CVars. |
| `engine host/support` | Continue refining Win32 host behavior, botlib ownership, platform services, crash/logging paths, and explicit compatibility boundaries. |

Compatibility-only surfaces are called out explicitly so they are not mistaken for retail
reconstruction: `platform_services.c`, the open/hybrid auth backends, the `unix`/`null`
ports, and live online-service activation behind `QL_BUILD_ONLINE_SERVICES`.

For the detailed audit trail and current task queue, see [`AUDIT.md`](AUDIT.md),
[`IMPLEMENTATION_PLAN.md`](IMPLEMENTATION_PLAN.md), and the historical engine audit in
[`docs/reverse-engineering/engine-full-parity-audit-and-implementation-plan-2026-04-10.md`](docs/reverse-engineering/engine-full-parity-audit-and-implementation-plan-2026-04-10.md).

## Repository guide

- `src/` contains the active reconstructed codebase built on top of the Quake III Arena GPL
  source layout.
- `src-re/` is the clean-room reconstruction workspace used for staged reconstruction work,
  prototypes, and promoted headers.
- `references/` holds the main reconstruction reference corpus, including HLIL exports and
  the committed Ghidra corpus.
- `assets/` stores upstream and retail reference material used for validation and comparison.
- `docs/` contains onboarding notes, workflow guides, parity documentation, and subsystem
  research.
- `tests/`, `tools/`, `artifacts/`, and `logs/` support the deterministic validation and CI
  workflows used to check reconstruction progress.

## Reference corpus

The project keeps its main evidence base in the repository so work can be reviewed and
replayed:

- `references/hlil/` contains Binary Ninja HLIL dumps for both Quake III Arena and Quake
  Live binaries.
- `references/reverse-engineering/ghidra/` contains the committed Ghidra exports used as a
  structured companion corpus.
- `references/symbol-maps/` and `references/analysis/quakelive_symbol_aliases.json` support
  naming, ownership, and symbol recovery work.

If you are tracing a subsystem, start with the committed reference material before making new
assumptions. The canonical workflow is documented in
[`docs/reverse-engineering/ghidra-reference-workflow.md`](docs/reverse-engineering/ghidra-reference-workflow.md).

## Getting started

- Read [`docs/onboarding/overview.md`](docs/onboarding/overview.md) for the quickest project
  orientation.
- Read [`BUILDING.md`](BUILDING.md) for the top-level build guide and the most
  common Windows and Linux build commands.
- Read [`docs/repo-overview.md`](docs/repo-overview.md) for a fuller explanation of the
  repository layout.
- Use [`docs/platform/toolchain-matrix.md`](docs/platform/toolchain-matrix.md) to understand
  build requirements and supported toolchains.
- Use [`docs/reverse-engineering/ghidrassist-mcp.md`](docs/reverse-engineering/ghidrassist-mcp.md)
  and related notes if you are working through the reconstruction reference workflow.

## Credits

- This project builds on the public Quake III Arena GPL source release from id Software:
  [id-Software/Quake-III-Arena](https://github.com/id-Software/Quake-III-Arena)
- This project exists to reconstruct the retail Quake Live codebase as accurately as
  possible: [Quake Live](https://www.quakelive.com/)
