# Quake Live Reverse Engineering Project

[![Native DLL (VS2010)](https://github.com/quakelive-reverse/quakelive-reverse/actions/workflows/windows-native.yml/badge.svg?branch=main)](https://github.com/quakelive-reverse/quakelive-reverse/actions/workflows/windows-native.yml)
[![QVM Toolchain](https://github.com/quakelive-reverse/quakelive-reverse/actions/workflows/toolchain.yml/badge.svg?branch=main)](https://github.com/quakelive-reverse/quakelive-reverse/actions/workflows/toolchain.yml)

This repository documents and reconstructs the Quake Live gameplay stack on top of the
open-source Quake III Arena codebase. Use the documentation under `docs/` to navigate
build pipelines, testing harnesses, and reverse-engineering references.

## Mentorship rotation schedule

| Week | Mentor | Focus Area |
|------|--------|------------|
| 1    | Alex Rivera (@alex-r) | Tooling setup, QVM toolchain verification |
| 2    | Priya Desai (@pdesai) | HLIL diffing workflow, Binary Ninja projects |
| 3    | Morgan Lee (@mlee)    | Deterministic harness deep dive |
| 4    | Casey Nguyen (@cnguyen) | Gameplay parity audits, documentation standards |

- The rotation restarts after Week 4; ping the current mentor in #reverse-engineering.
- Swap weeks as needed by opening a short PR that updates this table.
- Pairings default to a 30-minute weekly sync plus ad-hoc Slack support.

## How to get started

- Read [`docs/onboarding/re-track.md`](docs/onboarding/re-track.md) for the full
  onboarding flow.
- Review the slide decks in [`docs/media/`](docs/media/) before your first mentor
  sync so you can ask targeted questions about the harness and reconstruction
  workflow.
- Consult the [`Native Toolchain Support Matrix`](docs/platform/toolchain-matrix.md)
  for host requirements, build status, and the 32-bit runtime payloads needed to
  exercise the native DLLs on each platform.【F:docs/platform/toolchain-matrix.md†L1-L60】

For calendar integration, subscribe to the shared "QL Reverse Mentorship" calendar
which mirrors this rotation for visibility across time zones.
