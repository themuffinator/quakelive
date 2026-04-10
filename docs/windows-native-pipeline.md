# Visual Studio 2010 Native Build Guidance

Quake Live’s retail gameplay modules were compiled as Win32 DLLs with the Visual Studio 2010 (`v100`) toolset and import the Visual C++ 2010 CRT pair (`MSVCR100.dll`, `MSVCP100.dll`). The retail-facing project files under `src/code/` now default back to that legacy toolset so Release builds continue to emit Quake Live-style binaries with the same CRT bindings and PE header shape.

## Required project files

Open `src/code/quakelive.sln` inside Visual Studio and load the following projects:

- `game/qagamex86.vcxproj` – Produces `build/win32/<Config>/modules/qagamex86/qagamex86.dll` and loads its export table from `game.def` (`dllEntry`, `vmMain`).
- `cgame/cgamex86.vcxproj` – Produces `build/win32/<Config>/modules/cgamex86/cgamex86.dll` and wires the same export pair via `cgame.def`.
- `ui/ui.vcxproj` – Produces `build/win32/<Config>/bin/baseq3/uix86.dll` and loads `ui.def` so the UI DLL exports `dllEntry` and `vmMain`.
- `quakelive_steam.vcxproj` – Produces the native retail-style host executable under `build/win32/<Config>/bin/quakelive_steam.exe`.
- `awesomium_process.vcxproj` – Produces the retail-style browser subprocess helper under `build/win32/<Config>/bin/awesomium_process.exe`.

Each project already sets a Win32 dynamic-library configuration with explicit output paths and map/PDB generation so no additional post-build steps are required. Building the solution with the proper toolset will drop the DLLs into the `src/code/<project>/Release*/` directories alongside their `.lib`, `.pdb`, and `.map` files.

## Retargeting to the `v100` toolset

1. Install Visual Studio 2010 SP1 or a newer Visual Studio release that includes the “Visual Studio 2010 (v100) toolset” optional component. Confirm that `vcvarsall.bat` accepts `-vcvars_ver=10.0` to load the toolchain.
2. The checked-in retail-facing project files now pin **ToolsVersion** to `4.0` and **Platform Toolset** to `v100`, so MSBuild and newer IDEs stay on the Visual Studio 2010 compiler/linker stack by default.
3. Release configurations for `qagamex86`, `cgamex86`, `uix86`, and `quakelive_steam.exe` are locked to `/MD` (`MultiThreadedDLL`) so the shipped binaries keep importing the legacy CRT pair (`MSVCR100.dll`, `MSVCP100.dll`). Debug configurations use `/MDd`.
4. `awesomium_process.exe` intentionally stays on the retail static CRT path; the retail helper imports only `KERNEL32.dll` and `awesomium.dll`.
5. The retail PE headers also matter: subsystem version `5.1`, module base address `0x10000000`, ASLR/NX enabled, SafeSEH on the gameplay/UI DLLs and `awesomium_process.exe`, and the retail launcher’s `1 MB` stack reserve are now encoded directly in the project files.
6. Build the `Release|Win32` configuration to generate the DLLs and host executables with aligned exports, CRT bindings, and linker metadata. The `.def` files enforce the two-function export tables required by the game engine loader.

## Distribution staging

Once `uix86.dll` is built with the correct toolset/runtime, stage it beside the UI script tree (`baseq3/ui/*.menu`, `baseq3/ui/*.txt`) in the distribution layout so the native module and its menu assets ship together.

## Log files

The engine writes a console log when `logfile` is enabled (for example `+set logfile 1` for buffered output or `+set logfile 2` to flush on each print). The log is created under:

- `<fs_homepath>\\baseq3\\qconsole.log`

With a Steam install and the Quake Live SteamID homepath detected, this typically resolves to:

- `C:\\Program Files (x86)\\Steam\\steamapps\\common\\Quake Live\\<steamid>\\baseq3\\qconsole.log`

The default VS Code `Launch Quake Live` configuration sets the working directory to the Steam Quake Live install root so the native UI can locate `awesomium.dll`, `awesomium_process.exe`, and `web.pak` at runtime.

The default VS Code `Launch Quake Live` configuration does not override `fs_homepath`. If you prefer keeping logs in the repository, set:

- `+set fs_homepath <repo>\\run`

This writes the console log to:

- `<repo>\\run\\baseq3\\qconsole.log`

The syscall contract trace (used for validating VM/DLL boundaries) is written alongside it at:

- `<fs_homepath>\\baseq3\\logs\\syscall_contract.log`

When debugging native UI startup and file lookups, the engine also records failed/satisfied `UI_FS_FOPENFILE` requests to:

- `<fs_homepath>\\baseq3\\logs\\ui_fs.log`

With the repo-local `fs_homepath` override, this resolves to:

- `<repo>\\run\\baseq3\\logs\\syscall_contract.log`

## Command-line builds and MSBuild overrides

From a “Developer Command Prompt for VS2010” session (or any environment bootstrapped with `vcvarsall.bat -vcvars_ver=10.0`), invoke MSBuild with the legacy toolset explicitly to avoid host/target mismatches:

```
msbuild src\code\quakelive.sln /m /p:Configuration=Release /p:Platform=Win32 /p:PlatformToolset=v100 /p:PreferredToolArchitecture=x86
```

The helper script `tools/ci/build-windows-dlls.ps1` wraps this command line and defaults to the `v100` toolset, ensuring the gameplay DLLs are compiled with the correct compiler/linker pair even on newer Visual Studio installations.

Run `pwsh tools/ci/audit-retail-dependencies.ps1 -Strict` after staging the
launcher payload to confirm the local Steam install still matches the committed
retail dependency set.

Run `pwsh tools/ci/audit-retail-toolchain.ps1 -Strict` to confirm the checked-in
project metadata still matches the recovered retail VC10-era settings.

Run `pwsh tools/ci/audit-retail-metadata.ps1` to confirm the executable version
resources and embedded manifests still mirror the retail launcher and helper.

The native client host now also has a dedicated closure lane. Refresh the
tracked client runtime bundle with:

- `pwsh -NoProfile -ExecutionPolicy Bypass -File tools/client/run_client_runtime_probe.ps1`

This writes `artifacts/client_validation/logs/client_runtime_evidence_20260410.json`.
Then run:

- `pytest tests/test_client_full_parity_gate.py -q`

to publish `artifacts/client_validation/logs/client_full_parity_gate.json`,
which is the machine-readable `CL-P6` closure artifact consumed by the client
validation workflow.

## Validating against the reference DLLs

The repository ships Quake Live’s original binaries under `assets/quakelive/baseq3/`. Compare the newly built artefacts against those DLLs using `dumpbin /exports` and `dumpbin /imports` to ensure the export table is identical (`dllEntry`, `vmMain`) and that the only CRT dependencies are `MSVCR100.dll`/`MSVCP100.dll`. The CI helpers described in [`docs/toolchain-ci.md`](toolchain-ci.md) automate these checks for pull requests, including an export manifest enforced by `tools/ci/assert-dll-exports.ps1`.
