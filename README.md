# Quake Live Reverse Engineering Project

[![Native DLL (VS2010)](https://github.com/quakelive-reverse/quakelive-reverse/actions/workflows/windows-native.yml/badge.svg?branch=main)](https://github.com/quakelive-reverse/quakelive-reverse/actions/workflows/windows-native.yml)
[![QVM Toolchain](https://github.com/quakelive-reverse/quakelive-reverse/actions/workflows/toolchain.yml/badge.svg?branch=main)](https://github.com/quakelive-reverse/quakelive-reverse/actions/workflows/toolchain.yml)

This repository documents and reconstructs the Quake Live gameplay stack on top of the
open-source Quake III Arena codebase. Use the documentation under `docs/` to navigate
build pipelines, testing harnesses, and reverse-engineering references.

## Current status

> Snapshot dates: parity audit updated on 2026-03-26, implementation queue refreshed on 2026-03-06, and UI mapping notes tightened on 2026-04-01.

The project is past the "basic bring-up" stage. Source-built native `ui`, `qagame`,
and `cgame` DLLs load through the recovered Quake Live-style `dllEntry` seam, major
gameplay and cgame systems are in the medium-high parity range, and the remaining gaps
are now concentrated in the retail launcher/platform host, retail UI asset/menu
behavior, and the final ownerdraw/stat payload edges.

### Reconstruction snapshot

| Area | Status | Current reading |
|------|--------|-----------------|
| Native game-module ABI | High parity for source-built DLLs | The engine loads native `ui`, `qagame`, and `cgame` DLLs through the recovered Quake Live import/export seam. The remaining gap is strict compatibility validation against the retail DLLs themselves rather than only reconstructed source-built binaries. |
| Core gameplay and cgame | Medium-high parity | Most baseline gameplay systems are reconstructed and working. Current effort is focused on targeted retail validation, sequencing fixes, and smaller subsystem gaps instead of wholesale feature bring-up. |
| Native launcher and platform host | Low parity | The retail `quakelive_steam.exe` bootstrap, Steam-backed platform flows, web/Awesomium-style navigation, and launcher-owned state publication remain the single largest structural gap. |
| Retail UI asset and menu stack | Low-medium parity | Engine-side compatibility has improved materially, but many retail assets, fonts, and menu assumptions still fall back or warn at runtime because the retail UI stack is not fully reconstructed here. |
| Ownerdraw and stat payloads | Medium parity | Scorestats, placement, and team telemetry are substantially farther along than before, but the repo is still finishing the last retail-aligned payload fields and validating them against runtime evidence. |

### Latest audited progress

- `Task 20` closed the match-flow configstring gap by publishing and consuming the
  retail-side sudden-death, ready-up, and warmup-ready channels instead of partially
  mirroring them.
- `Task 25` restored the compact retail-backed cgame particle runtime, removing the
  split between the compiled path and the stale duplicate source copy.
- `Task 26` recovered the native `dllEntry` import/export contract for `ui`,
  `qagame`, and `cgame`, validated the rebuilt export tables, and proved the normal
  startup and gameplay map paths work with source-built DLLs.
- The latest UI documentation pass on 2026-04-01 reports that the committed `uix86`
  map now covers the full current anchor corpus at `444 / 444` anchors, shifting the
  remaining UI uncertainty toward runtime behavior, asset coverage, and parser or
  compatibility details rather than basic function ownership.

### Active work queue

1. Reconstruct the native launcher/platform host behavior and tighten validation
   against the retail gameplay DLLs.
2. Continue UI/menu compatibility work in writable engine-side layers, including UI
   bridge and fallback validation, while `src/ui/` remains read-only.
3. Finish ownerdraw/stat payload parity and keep runtime validation fixtures aligned
   with the recovered data model.
4. Run targeted gameplay validation sweeps, including PQL/CPMA air control,
   movement, Race, and gametype-specific rules where retail sequencing still needs
   confirmation.

### Latest verification snapshot

- `Debug|x86` solution build succeeded on 2026-03-26.
- `tools/ci/assert-dll-exports.ps1` passed for rebuilt `uix86.dll`,
  `qagamex86.dll`, and `cgamex86.dll`.
- A normal runtime pass reached the native `ui` main-menu path.
- A gameplay runtime pass on `campgrounds` loaded native `ui`, `qagame`, and
  `cgame`, then shut down cleanly.
- A forced-crash validation pass produced a fresh dump under
  `build\\win32\\Debug\\dumps`.

### Constraints that shape progress

- `references/hlil/` remains the canonical parity reference; the committed Ghidra
  exports and symbol maps act as the structured companion evidence base.
- `src/ui/` is read-only, so retail UI progress is currently driven by engine-side
  compatibility work, bridge validation, and documentation rather than direct UI VM
  rewrites.
- Quake Live-only online services stay behind `QL_BUILD_ONLINE_SERVICES`, default
  disabled, until an open replacement path exists.

For the full parity breakdown and the live reconstruction queue, see
[`AUDIT.md`](AUDIT.md) and [`IMPLEMENTATION_PLAN.md`](IMPLEMENTATION_PLAN.md).

## Reverse-engineering references

The repository now carries two complementary reverse-engineering corpora:

- Binary Ninja HLIL dumps under `references/hlil/`, which remain the canonical
  parity reference for retail Quake Live behavior.
- OpenAlice-style committed Ghidra exports under
  `references/reverse-engineering/ghidra/`, which provide structured
  `metadata.txt`, `functions.csv`, `imports.txt`, `exports.txt`,
  `analysis_symbols.txt`, and `decompile_top_functions.c` snapshots for the retail
  Quake Live binaries in `assets/quakelive/`.

Primary workflow docs:

- `docs/reverse-engineering/ghidra-reference-workflow.md`
- `docs/reverse-engineering/ghidra-module-mapping.md`
- `docs/reverse-engineering/ghidrassist-mcp.md`

Refresh the committed Ghidra corpus with:

```powershell
scripts\ghidra\run_quakelive_reference.ps1
```

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
