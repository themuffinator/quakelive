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

## Reverse-Engineering Workflow Notes
- The HLIL exports are available for both Quake III (`references/hlil/quake3/`) and Quake Live (`references/hlil/quakelive/`). Keeping the two sets side-by-side enables systematic diffing between the retail Quake III code and the decompiled Quake Live functions when porting behavior.
- Quake Live assets under `references/original-assets/quakelive/` expose binary modules (`cgamex86.dll`, `qagamex86.dll`, `uix86.dll`, etc.) and supporting data (fonts, icons, maps) to validate assumptions or reproduce file formats.
- The active `src/` tree should evolve from the Quake III baseline towards Quake Live parity. Build scripts and auxiliary tools from the original release remain in place to facilitate compiling both the native engine and the QVMs as changes are introduced.

## Next Steps for Contributors
1. Familiarize yourself with the HLIL dump organization so that Quake Live specific behaviors can be tracked back to decompiled functions.
2. Compare modules in `src/code/` against their HLIL equivalents to identify divergences that must be ported.
3. Keep the documentation in this overview updated as the project introduces new directories, tooling, or reverse-engineered components.
4. Use the living build notes in [`docs/qvmtools.md`](qvmtools.md) and [`docs/windows-native-pipeline.md`](windows-native-pipeline.md) when reproducing the legacy QVM toolchain or the Visual Studio DLL workflow so that outputs stay aligned with the archived Quake Live binaries.
