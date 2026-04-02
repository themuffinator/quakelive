# Quake Live Reverse Engineering Project

[![Accuracy First](https://img.shields.io/badge/Accuracy-First-1f6feb)](AUDIT.md)
[![Current Status](https://img.shields.io/badge/Status-Non--Playable-b22222)](AUDIT.md)
[![Implementation Plan](https://img.shields.io/badge/Work%20Queue-Implementation%20Plan-2ea44f)](IMPLEMENTATION_PLAN.md)
[![Getting Started](https://img.shields.io/badge/Docs-Getting%20Started-6f42c1)](docs/onboarding/overview.md)

[![Deterministic Harnesses](https://github.com/quakelive-reverse/quakelive-reverse/actions/workflows/deterministic-harnesses.yml/badge.svg?branch=main)](https://github.com/quakelive-reverse/quakelive-reverse/actions/workflows/deterministic-harnesses.yml)

This project aims to reconstruct the full Quake Live source code as faithfully as possible.
It starts from the public Quake III Arena GPL source release and then rebuilds Quake Live
behavior piece by piece using retail binaries, Binary Ninja HLIL exports, committed Ghidra
references, symbol maps, and runtime validation.

Accuracy is the top priority. This repository is not trying to make a "Quake Live-like"
fork or a rough gameplay approximation. The goal is to recover how the retail game actually
works, document what is known, and close the remaining gaps in a way that stays grounded in
evidence instead of guesswork.

## What "accuracy first" means here

- Retail Quake Live behavior is the target, not convenience or approximation.
- Reverse-engineering evidence is treated as the source of truth when the open GPL baseline
  and the retail game differ.
- Where evidence is incomplete, small intuitive fixes or compatibility wiring may still be
  needed to keep the reconstruction working, but they should stay minimal and give way to
  stronger evidence when it appears.
- Unclear areas are tracked as open gaps instead of being filled in with confident-looking
  assumptions.
- Quake Live-specific online services can be disabled in builds when the retail dependency
  cannot yet be reconstructed cleanly or does not have an open replacement.
- Progress is measured by parity with the retail game, not just by whether the code builds
  or runs.

## Current status

The project is well past basic bring-up. Source-built native `ui`, `qagame`, and `cgame`
DLLs load through the recovered Quake Live-style interfaces, and a large amount of gameplay
and cgame behavior has already been reconstructed.

That said, the current codebase is not yet playable end to end. Some important wiring is
still absent, so a successful build does not currently mean a fully working game.

The biggest remaining gaps are still the hard ones: the retail launcher and platform host,
the full retail UI and menu behavior, and the last rounds of parity validation against the
shipping game. For the detailed parity breakdown and current task queue, see
[`AUDIT.md`](AUDIT.md) and [`IMPLEMENTATION_PLAN.md`](IMPLEMENTATION_PLAN.md).

## Repository guide

- `src/` contains the active reconstructed codebase built on top of the Quake III Arena GPL
  source layout.
- `src-re/` is the clean-room reconstruction workspace used for staged reverse-engineering
  work, prototypes, and promoted headers.
- `references/` holds the main reverse-engineering evidence, including HLIL exports and the
  committed Ghidra corpus.
- `assets/` stores upstream and retail reference material used for validation and comparison.
- `docs/` contains onboarding notes, workflow guides, parity documentation, and subsystem
  research.
- `tests/`, `tools/`, `artifacts/`, and `logs/` support the deterministic validation and CI
  workflows used to check reconstruction progress.

## Reverse-engineering references

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
  and related notes if you are working through the reverse-engineering reference workflow.

## Credits

- This project builds on the public Quake III Arena GPL source release from id Software:
  [id-Software/Quake-III-Arena](https://github.com/id-Software/Quake-III-Arena)
- This project exists to reconstruct the retail Quake Live codebase as accurately as
  possible: [Quake Live](https://www.quakelive.com/)
