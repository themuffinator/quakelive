# Visual Studio 2010 Native Build Guidance

Quake Live’s retail gameplay modules were compiled as Win32 DLLs with the Visual Studio 2010 (`v100`) toolset and import the Visual C++ 2010 CRT pair (`MSVCR100.dll`, `MSVCP100.dll`).【F:docs/hlil_comparison.md†L8-L17】 The Visual Studio solution under `src/code/` now pins the supported gameplay projects (`game` and `cgame`) to that legacy toolset so Release builds continue to emit Quake Live–style binaries (`qagamex86.dll`, `cgamex86.dll`) with the same exports and CRT bindings.

## Required project files

Open `src/code/quake3.sln` inside Visual Studio and load the following projects:

- `game/game.vcxproj` – Produces `../Release/qagamex86.dll` for the Release Win32 configuration and loads its export table from `game.def` (which lists `dllEntry` and `vmMain`).【F:src/code/game/game.vcxproj†L285-L313】【F:src/code/game/game.def†L1-L4】
- `cgame/cgame.vcxproj` – Produces `../Release/cgamex86.dll` and wires the same export pair via `cgame.def`.【F:src/code/cgame/cgame.vcxproj†L171-L199】【F:src/code/cgame/cgame.def†L1-L4】
- `ui/ui.vcxproj` – Build the `Release TA|Win32` (or equivalent retargeted Release) configuration to emit `../Release_TA/uix86.dll` and load `ui.def` so the UI DLL exports `dllEntry`/`vmMain` just like the VM loader expects.【F:src/code/ui/ui.vcxproj†L12-L193】【F:src/code/ui/ui.def†L1-L3】

Each project already sets a Win32 dynamic-library configuration with explicit output paths and map/PDB generation so no additional post-build steps are required.【F:src/code/game/game.vcxproj†L285-L355】【F:src/code/cgame/cgame.vcxproj†L171-L240】【F:src/code/ui/ui.vcxproj†L126-L193】 Building the solution with the proper toolset will drop the DLLs into the `src/code/<project>/Release*/` directories alongside their `.lib`, `.pdb`, and `.map` files.

## Retargeting to the `v100` toolset

1. Install Visual Studio 2010 SP1 or a newer Visual Studio release that includes the “Visual Studio 2010 (v100) toolset” optional component. Confirm that `vcvarsall.bat` accepts `-vcvars_ver=10.0` to load the toolchain.
2. The game and cgame project files checked into source control already pin **ToolsVersion** to `4.0` and **Platform Toolset** to `v100`, ensuring MSBuild treats them as Visual Studio 2010 projects even when opened in newer IDEs.【F:src/code/game/game.vcxproj†L2-L64】【F:src/code/cgame/cgame.vcxproj†L2-L46】 The UI project still targets a newer toolset and must be retargeted to `v100` to match the retail import tables before building native UI DLLs.【F:src/code/ui/ui.vcxproj†L1-L60】
3. Release configurations are locked to the `/MD` runtime (`MultiThreadedDLL`) so the shipped binaries keep importing the legacy CRT pair (`MSVCR100.dll`, `MSVCP100.dll`).【F:src/code/game/game.vcxproj†L285-L350】【F:src/code/cgame/cgame.vcxproj†L171-L206】 The UI project currently uses `/MT`; update its `RuntimeLibrary` to `MultiThreadedDLL` so `uix86.dll` links against the same CRT as the game modules.【F:src/code/ui/ui.vcxproj†L126-L207】 Package the x86 redistributable alongside the DLLs when deploying to clean machines.
4. Build the `Release|Win32` configuration (plus the UI Release TA/retargeted UI configuration) to generate the DLLs with aligned exports. The `.def` files enforce the two-function export tables required by the game engine loader.【F:src/code/game/game.def†L1-L4】【F:src/code/cgame/cgame.def†L1-L4】【F:src/code/ui/ui.def†L1-L3】

## Distribution staging

Once `uix86.dll` is built with the correct toolset/runtime, stage it beside the UI script tree (`baseq3/ui/*.menu`, `baseq3/ui/*.txt`) in the distribution layout so the native module and its menu assets ship together.【F:docs/reference-mapping.md†L14-L21】

## Command-line builds and MSBuild overrides

From a “Developer Command Prompt for VS2010” session (or any environment bootstrapped with `vcvarsall.bat -vcvars_ver=10.0`), invoke MSBuild with the legacy toolset explicitly to avoid host/target mismatches:

```
msbuild src\code\quake3.sln /m /p:Configuration=Release /p:Platform=Win32 /p:PlatformToolset=v100 /p:PreferredToolArchitecture=x86
```

The helper script `tools/ci/build-windows-dlls.ps1` wraps this command line and defaults to the `v100` toolset, ensuring the gameplay DLLs are compiled with the correct compiler/linker pair even on newer Visual Studio installations.【F:tools/ci/build-windows-dlls.ps1†L1-L37】

## Validating against the reference DLLs

The repository ships Quake Live’s original binaries under `assets/quakelive/baseq3/`. Compare the newly built artefacts against those DLLs using `dumpbin /exports` and `dumpbin /imports` to ensure the export table is identical (`dllEntry`, `vmMain`) and that the only CRT dependencies are `MSVCR100.dll`/`MSVCP100.dll`.【F:docs/reference-mapping.md†L14-L21】【F:tools/ci/verify-dll-exports.ps1†L40-L72】 The CI helpers described in [`docs/toolchain-ci.md`](toolchain-ci.md) automate these checks for pull requests, including an export manifest enforced by `tools/ci/assert-dll-exports.ps1`.【F:tools/ci/assert-dll-exports.ps1†L1-L152】【F:tools/ci/manifests/native-dll-exports.json†L1-L14】
