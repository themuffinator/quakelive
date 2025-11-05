# Visual Studio 2010 Native Build Guidance

Quake Live’s retail gameplay modules were compiled as Win32 DLLs with the Visual Studio 2010 (`v100`) toolset and import the Visual C++ 2010 CRT pair (`MSVCR100.dll`, `MSVCP100.dll`).【F:docs/hlil_comparison.md†L8-L17】 The existing Visual Studio solution under `src/code/` already contains project files for the three gameplay DLLs—`game`, `cgame`, and `q3_ui`—but they currently default to the modern `v143` toolset. The steps below capture how to retarget those projects so that they emit Quake Live–style binaries (`qagamex86.dll`, `cgamex86.dll`, `uix86.dll`) with matching exports.

## Required project files

Open `src/code/quake3.sln` inside Visual Studio and load the following projects:

- `game/game.vcxproj` – Produces `../Release/qagamex86.dll` for the Release Win32 configuration and loads its export table from `game.def` (which lists `dllEntry` and `vmMain`).【F:src/code/game/game.vcxproj†L328-L355】【F:src/code/game/game.def†L1-L4】
- `cgame/cgame.vcxproj` – Produces `../Release/cgamex86.dll` and wires the same export pair via `cgame.def`.【F:src/code/cgame/cgame.vcxproj†L87-L115】【F:src/code/cgame/cgame.def†L1-L4】
- `q3_ui/q3_ui.vcxproj` – Produces `../Release/uix86.dll` while referencing `ui.def` for its export list.【F:src/code/q3_ui/q3_ui.vcxproj†L188-L235】【F:src/code/q3_ui/ui.def†L1-L3】

Each project already sets a Win32 dynamic-library configuration with explicit output paths and map/PDB generation so no additional post-build steps are required.【F:src/code/game/game.vcxproj†L332-L353】【F:src/code/cgame/cgame.vcxproj†L91-L114】【F:src/code/q3_ui/q3_ui.vcxproj†L188-L235】 Building the solution with the proper toolset will drop the DLLs into the `src/code/<project>/Release/` directories alongside their `.lib`, `.pdb`, and `.map` files.

## Retargeting to the `v100` toolset

1. Install Visual Studio 2010 SP1 or a newer Visual Studio release that includes the “Visual Studio 2010 (v100) toolset” optional component. Confirm that `vcvarsall.bat` accepts `-vcvars_ver=10.0` to load the toolchain.
2. In Visual Studio, open each project’s **Property Pages → General** settings for the desired configuration (e.g., `Release|Win32`) and set **Platform Toolset** to `v100`. The current XML still references `v143`, so ensure the change is saved back into source control when creating dedicated build branches.【F:src/code/game/game.vcxproj†L36-L64】【F:src/code/cgame/cgame.vcxproj†L28-L46】【F:src/code/q3_ui/q3_ui.vcxproj†L28-L48】
3. Leave the runtime library setting at `/MD` for Release (already present in the project files) so that the resulting binaries continue to import `MSVCR100.dll` and `MSVCP100.dll` just like the Quake Live originals.【F:src/code/game/game.vcxproj†L328-L334】【F:src/code/cgame/cgame.vcxproj†L87-L94】【F:src/code/q3_ui/q3_ui.vcxproj†L188-L214】
4. Build the `Release|Win32` configuration to generate the DLLs with aligned exports. The `.def` files enforce the two-function export tables required by the game engine loader.【F:src/code/game/game.def†L1-L4】【F:src/code/cgame/cgame.def†L1-L4】【F:src/code/q3_ui/ui.def†L1-L3】

## Validating against the reference DLLs

The repository ships Quake Live’s original binaries under `references/original-assets/quakelive/baseq3/`. Compare the newly built artefacts against those DLLs using `dumpbin /exports` and `dumpbin /imports` to ensure the export table is identical (`dllEntry`, `vmMain`) and that the only CRT dependencies are `MSVCR100.dll`/`MSVCP100.dll`.【F:docs/reference-mapping.md†L14-L21】 The CI helpers described in [`docs/toolchain-ci.md`](toolchain-ci.md) automate these checks for pull requests.
