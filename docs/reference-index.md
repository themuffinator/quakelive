# Reference Index

This document catalogs the material checked into the `references/` directory and links each artifact to the corresponding Quake Live or Quake III Arena module in `src/`. "Gap status" indicates whether we already have matching source in this repo or if additional recovery work is required.

## HLIL dumps

| Reference path | Contents & purpose | Implied module(s) | Matching source location(s) | Gap status | Suggested follow-up owner |
| --- | --- | --- | --- | --- | --- |
| `references/hlil/quakelive/cgamex86.dll/` (`cgamex86.dll_hlil.txt` and split parts) | High Level IL disassembly of the Quake Live client game module. | Client Game VM | `src/code/cgame/` | **Covered** – source tree present, needs parity checks only. | Game VM reverse engineering |
| `references/hlil/quakelive/qagamex86.dll/` (`qagamex86.dll.bndb_hlil_part*.txt`) | HLIL dump of the dedicated game logic VM used by the server. | Game VM (server) | `src/code/game/` | **Covered** – source available for comparison. | Game VM reverse engineering |
| `references/hlil/quakelive/uix86.all/` (`uix86.dll_hlil.txt` and part files) | HLIL reconstruction of the UI dynamic library that drives menus/HUD. | UI VM | `src/code/ui/`, supplemental menu defs in `src/ui/` | **Covered** – sources mirror binary, diff audit recommended. | UI systems |
| `references/hlil/quakelive/quakelive_steam.exe/` (`quakelive_steam.exe_hlil_part*.txt`) | HLIL export of the Windows launcher that hosts the game and Steam hooks. | Native launcher & platform glue | _No equivalent in `src/`_ | **Missing** – native host code absent from repo. | Platform integration (Windows/Steam) |
| `references/hlil/quake3/quake3.exe/` (`quake3.exe_hlil_part*.txt`) | HLIL of the original Quake III Arena executable for historical parity. | Engine (client/server/renderer) | `src/code/client/`, `src/code/qcommon/`, `src/code/server/`, `src/code/renderer/` | **Covered** – open-source engine already imported. | Engine maintainers |

## Extracted assets

| Reference path | Contents & purpose | Implied module(s) | Matching source location(s) | Gap status | Suggested follow-up owner |
| --- | --- | --- | --- | --- | --- |
| `assets/quakelive/baseq3/cgamex86.dll` | Shipped client VM binary. Useful for binary-to-source diffing. | Client Game VM | `src/code/cgame/` | **Covered** – rebuilds possible from current source. | Game VM reverse engineering |
| `assets/quakelive/baseq3/qagamex86.dll`, `qagamex64.so`, `qagamei386.so` | Windows and Linux server VM binaries. | Game VM (server) | `src/code/game/` | **Covered** – cross-platform sources present; verify Linux build scripts. | Game VM reverse engineering |
| `assets/quakelive/baseq3/uix86.dll` | Shipping UI VM binary. | UI VM | `src/code/ui/`, `src/ui/` | **Covered** – source available; investigate UI asset diffs. | UI systems |
| `assets/quakelive/baseq3/ui/` | Extracted menu definitions and UI assets (`*.menu`, `assets/`, etc.). | UI data layer | `src/ui/` | **Covered** – text assets match repo copy; ensure localization parity. | UI systems |
| `assets/quakelive/baseq3/botfiles/` | Bot chat scripts and behavior configs. | Bot AI | `src/code/botlib/` | **Covered** – botlib source available; needs data verification. | AI/bot maintainer |
| `assets/quakelive/baseq3/scripts/`, `maps/`, `fonts/`, `icons/`, config samples (`*.cfg`) | Gameplay scripts, map metadata, HUD fonts/icons, shipping config baselines. | Game content pipeline | `src/code/game/` (script loaders), `src/code/client/` (HUD/font usage) | **Partial** – runtime loaders exist, but actual art/map sources are not present. | Content pipeline |
| `assets/quake3/src/` | Snapshot of the GPL Quake III Arena source release used as upstream. | Whole engine & toolchain | `src/` (mirrors this layout) | **Covered** – repository already seeded with same tree. | Engine maintainers |

## Notable gaps & suggested actions

- **Native launcher / platform services:** `quakelive_steam.exe` HLIL shows we lack the Windows host executable, Steam API bindings, and any anti-cheat/bootstrap logic. Recommend assigning to the Platform integration team to recover or reimplement the launcher layer.
- **Art & map source assets:** While compiled assets (`maps/`, `icons/`, fonts) are preserved, we do not have the editable source files (map `.map`, vector art, PSDs). Content pipeline owners should source original asset repositories or recreate tooling to regenerate them.
- **Service-side integrations:** No references for Quake Live backend services (authentication, stats) were found. If these are required, coordination with LiveOps/Backend is needed to locate service definitions.
