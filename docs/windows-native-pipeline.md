# Visual Studio 2010 Native Build Guidance

Quake Live’s retail gameplay modules were compiled as Win32 DLLs with the Visual Studio 2010 (`v100`) toolset and import the Visual C++ 2010 CRT pair (`MSVCR100.dll`, `MSVCP100.dll`). The retail-facing project files under `src/code/` now default back to that legacy toolset so Release builds continue to emit Quake Live-style binaries with the same CRT bindings and PE header shape.

## Required project files

Open `src/code/quakelive.sln` inside Visual Studio and load the following projects:

- `game/qagamex86.vcxproj` – Produces `build/win32/<Config>/modules/qagamex86/qagamex86.dll` and loads its export table from `game.def` (`dllEntry`, `vmMain`).
- `cgame/cgamex86.vcxproj` – Produces `build/win32/<Config>/modules/cgamex86/cgamex86.dll` and wires the same export pair via `cgame.def`.
- `ui/ui.vcxproj` – Produces `build/win32/<Config>/bin/baseq3/uix86.dll` and loads `ui.def` so the UI DLL exports `dllEntry` and `vmMain`.
- `quakelive_steam.vcxproj` – Produces the native retail-style host executable under `build/win32/<Config>/bin/quakelive_steam.exe`.
- The default `.vscode/build.ps1` wrapper also emits `build/win32/<Config>/bin/qzeroded.exe` as the dedicated-server host alias. This matches the retained retail dedicated-tool basename `qzeroded` from the Linux `qzeroded.x86` package while keeping the Windows build policy-friendly.
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

## Windows DPI behavior

The native `quakelive_steam.exe` host intentionally diverges from the retail
launcher by opting into modern DPI awareness. The embedded manifest declares
per-monitor DPI awareness with a legacy `true/pm` fallback, and `WinMain` calls
the runtime DPI-awareness shim before creating the loading window, console, or
OpenGL window. This keeps fullscreen mode dimensions in physical pixels on
scaled Windows desktops and avoids the cropped fullscreen viewport caused by
system-DPI virtualization.

## Log files

The engine writes a console log when `logfile` is enabled (for example `+set logfile 1` for buffered output or `+set logfile 2` to flush on each print). The log is created under:

- `<fs_homepath>\\baseq3\\qconsole.log`

With a Steam install and the Quake Live SteamID homepath detected, this typically resolves to:

- `C:\\Program Files (x86)\\Steam\\steamapps\\common\\Quake Live\\<steamid>\\baseq3\\qconsole.log`

The default VS Code `Launch Quake Live` configuration launches through
`.vscode\\launch.ps1`, which sets the working directory to the Steam Quake Live
install root so the native UI can locate `awesomium.dll`,
`awesomium_process.exe`, and `web.pak` at runtime. The launcher also passes
`+set fs_basepath <Steam Quake Live install root>` explicitly, and it validates
that `baseq3\\pak00.pk3` exists before the process is started.

The same launcher overrides `fs_homepath` to the repo-local runtime tree:

- `<repo>\\build\\win32\\Debug\\bin`

This writes the console log to:

- `<repo>\\build\\win32\\Debug\\bin\\baseq3\\qconsole.log`

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

Run `pwsh tools/ci/validate-windows-native.ps1 -PlatformToolset v100 -RuntimeProfile retail`
to execute the full strict retail validation lane. In addition to the metadata,
toolchain, and export checks, that wrapper now assembles
`build\win32\<Config>\retail-runtime\` from the rebuilt executables/modules plus
the exact retail launcher DLL payload and then audits that staged root for
missing or extra DLLs.

Run `pwsh tools/ci/audit-retail-dependencies.ps1 -Strict` when you want to
confirm the local Steam install still matches the committed retail dependency
set.

Run
`pwsh tools/ci/audit-retail-dependencies.ps1 -RuntimeRoot build\win32\Release\retail-runtime -SkipSteamInstall -Strict`
when you want to re-audit an already staged strict runtime root directly.

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

The shared `qcommon` layer now also has a dedicated Windows-native validation
lane. Run:

- `pwsh -NoProfile -ExecutionPolicy Bypass -File tools/qcommon/run_qcommon_runtime_probe.ps1`

This writes `artifacts/qcommon_validation/logs/qcommon_runtime_evidence_20260410.json`.
Then run:

- `pytest tests/test_cvar_parity.py tests/test_cvar_alias_console.py tests/test_fs_search_paths.py tests/test_qcommon_collision_leaf_parity.py tests/test_qcommon_vm_fallback_parity.py tests/test_playerstate_replication.py tests/test_client_config_parity.py tests/test_platform_services.py tests/test_cgame_event_transport_parity.py tests/test_qshared_retail_parity.py tests/test_qcommon_full_parity_gate.py -q`

to compile and execute the Windows-friendly native harness probes and publish
`artifacts/qcommon_validation/logs/qcommon_full_parity_gate.json`. The
dedicated CI lane for that artifact is
`.github/workflows/qcommon-validation.yml`. The tracked runtime bundle plus the
gate artifact now close the audited qcommon register at `QC-P6`. The added
fallback harness in `tests/test_qcommon_vm_fallback_parity.py` keeps the
native-to-qvm selection, compiled fallback, interpreted syscall logging,
restart fallback, and pointer boundary lanes covered on the default Windows
host, while `tests/test_qshared_retail_parity.py` keeps the recovered
`q_shared.c` / `q_math.c` helper surface tied back to the retail alias and
mapping corpus.

The engine `server` host now also has a dedicated Windows-native validation
lane. Run:

- `pwsh -NoProfile -ExecutionPolicy Bypass -File tools/server/run_server_runtime_probe.ps1`

This writes `artifacts/server_validation/logs/server_runtime_evidence_20260410.json`.
Then run:

- `pytest tests/test_platform_services.py tests/test_fake_vacban.py tests/test_server_full_parity_gate.py -q`

to publish `artifacts/server_validation/logs/server_full_parity_gate.json`,
which is the machine-readable `SV-P7` closure artifact for the final audited
server gap register.

When present, the runtime probe prefers `qzeroded.exe` from
`build/win32/Debug/bin/` over `quakelive_steam.exe` so the dedicated
validation lane exercises the retail-aligned dedicated executable name by
default.

The remaining engine-owned host/support surface outside `qcommon`, `server`,
`client`, and `renderer` now also has a dedicated Windows-native validation
lane. Run:

- `pytest tests/test_platform_services.py tests/test_steamworks_harness.py tests/test_renderer_win32_host_glue_parity.py tests/test_bot_resource_loading.py tests/test_botlib_internal_parity.py tests/test_win32_clipboard_parity.py tests/test_win32_raw_input_parity.py tests/test_input_translation.py tests/test_engine_host_support_full_parity_gate.py -q`

to publish
`artifacts/engine_host_support_validation/logs/engine_host_support_full_parity_gate.json`.
The tracked evidence bundle for the same lane is
`artifacts/engine_host_support_validation/logs/engine_host_support_runtime_evidence_20260410.json`.
That bundle does not come from a separate live probe: `EH-P6` closes the
Windows-host evidence and governance lane by publishing the focused
clipboard/raw-input/loading-window/input-translation proof already present in
source-backed tests, `EH-P4` extends the same validation lane with
deterministic botlib-internal AAS/reachability/goal-state coverage, and
`EH-P5` closes the final host/support register by classifying the
platform-service compatibility backends plus the Unix/null portability trees as
documented compatibility-only exclusions rather than open strict-retail gaps.

`EH-P1` boundary metadata is now published in the same artifact through
`scope_boundary` and `classification_summary`, so the Windows-native ledgers
and validation notes can point at one machine-readable source for the audited
scope boundary instead of keeping that split only in narrative documentation.

## Validating against the reference DLLs

The repository ships Quake Live’s original binaries under `assets/quakelive/baseq3/`. Compare the newly built artefacts against those DLLs using `dumpbin /exports` and `dumpbin /imports` to ensure the export table is identical (`dllEntry`, `vmMain`) and that the only CRT dependencies are `MSVCR100.dll`/`MSVCP100.dll`. The CI helpers described in [`docs/toolchain-ci.md`](toolchain-ci.md) automate these checks for pull requests, including an export manifest enforced by `tools/ci/assert-dll-exports.ps1`.
