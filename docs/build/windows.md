# Windows Native Build Targets

The Visual Studio solution under `src/code/quakelive.sln` now ships with dedicated
native builds for the Quake Live gameplay modules plus the reconstructed
`awesomium_process.exe` helper. The native module projects are copies of their VM
counterparts, but the output is redirected to
`build/win32/<Config>/modules/<ProjectName>/`, while the helper executable lands in
`build/win32/<Config>/bin/`. The Visual Studio 2010 (`v100`) toolset is enforced so
the produced binaries stay aligned with the shipping runtime.【F:src/code/game/qagamex86.vcxproj†L2-L135】【F:src/code/cgame/cgamex86.vcxproj†L2-L110】【F:src/code/awesomium_process.vcxproj†L1-L177】

The checked-in project defaults stay on `v100` for parity, but the build scripts
also support a `v141` override for contributors on modern Windows hosts who do
not have a working VS2010-compatible toolchain installed.
Local build and launch helpers default to `Debug|x86` so runtime debugging,
PDB loading, crash logs, and dump capture remain available during reconstruction.

For runtime prerequisites and validation steps on WOW64 hosts, see the
[Windows 32-bit Runtime Guide](../platform/windows-32bit-runtime.md).
For the exact retail dependency matrix and a Steam-install verifier, see
[Retail Windows Dependency Audit](../platform/retail-dependencies.md). For the
retail compiler/linker configuration evidence, see
[Retail Windows Toolchain Audit](../platform/retail-toolchain.md). For the
retail font-system evidence and remaining source gaps, see
[Retail Font Stack Audit](../platform/retail-font-stack.md).

## Available targets

| Target name | Project file | Output artifact |
|-------------|--------------|-----------------|
| `qagamex86` | `src/code/game/qagamex86.vcxproj` | `build/win32/<Config>/modules/qagamex86/qagamex86.dll` |
| `cgamex86`  | `src/code/cgame/cgamex86.vcxproj` | `build/win32/<Config>/modules/cgamex86/cgamex86.dll` |
| `awesomium_process` | `src/code/awesomium_process.vcxproj` | `build/win32/<Config>/bin/awesomium_process.exe` |
| `qzeroded` | emitted by `.vscode/build.ps1` after `quakelive_steam.vcxproj` completes | `build/win32/<Config>/bin/qzeroded.exe` |

The dedicated server alias intentionally follows the retail Quake Live dedicated
tool basename `qzeroded`, which is preserved in the shipped Linux dedicated
binary name `qzeroded.x86`. The repository’s Windows build emits
`qzeroded.exe` as the matching host-side adaptation so server scripts and
runtime probes can target the retail-aligned dedicated name even though no
retail Windows dedicated executable has been recovered in the local corpus.

## Building from the command line

Use the new project names as MSBuild targets when producing the native DLL set.
These `/t:` selectors are the switches that route MSBuild toward the
corresponding pipeline:

```powershell
msbuild src\code\quakelive.sln /t:qagamex86;cgamex86;awesomium_process /p:Configuration=Debug /p:Platform=x86 /p:PlatformToolset=v100
```

The default VS Code build wrapper emits `build/win32/Debug/bin/qzeroded.exe`
after a successful solution build by copying the reconstructed host binary and
its matching debug artifacts (`.pdb`, `.map`) to the retail-aligned dedicated
name.
VS Code launches set `QLR_DUMP_PATH=build\win32\Debug\dumps` and
`QLR_FULL_DUMP=1`; debug-build unhandled crashes show a confirmation dialog
before writing a timestamped `.dmp` plus a matching `.log` file with the
exception, register snapshot, dump type, and loaded module list.

The original VM builds remain available under the historical target names. For
example, the following command rebuilds the interpreted modules while leaving
the native DLLs untouched:

```powershell
msbuild src\code\quakelive.sln /t:game;cgame /p:Configuration=Debug /p:Platform=x86
```

## Modern compatibility override

If you want to keep the checked-in `v100` project defaults but build the native
targets with the Visual Studio 2017 compiler on a newer host, install the
optional `v141` toolset and pass it on the command line:

```powershell
pwsh tools\ci\install-vs-toolset.ps1 -PlatformToolset v141
pwsh tools\ci\verify-vs-toolchain.ps1 -PlatformToolset v141 -RequireToolset
msbuild src\code\quakelive.sln /t:qagamex86;cgamex86;awesomium_process /p:Configuration=Debug /p:Platform=x86 /p:PlatformToolset=v141
```

This path is a deliberate compatibility exception. It improves buildability on
modern systems, but it no longer reproduces the retail VC10 compiler/linker or
CRT import surface.

`awesomium_process.exe` respects the same online-services policy as the rest of
the launcher stack. Debug and ad hoc source builds still default
`QLBuildOnlineServices` to `0`, producing an offline-safe stub that exits
cleanly without loading `awesomium.dll`. Windows Release-family configurations
now default the helper to `QLBuildOnlineServices=1`, so release packages carry a
WebUI-capable child-process launcher that resolves the retail
`Awesomium::ChildProcessMain` entry point dynamically from an external
`awesomium.dll` at runtime.

For strict SDK/import-table parity of the helper, set
`/p:QLBuildOnlineServices=1 /p:QLUseAwesomiumSdk=1` and point
`AwesomiumSdkDir` or `AWESOMIUM_SDK_DIR` at an external Awesomium SDK:

```powershell
msbuild src\code\awesomium_process.vcxproj /p:Configuration=Release /p:Platform=Win32 /p:PlatformToolset=v100 /p:QLBuildOnlineServices=1 /p:QLUseAwesomiumSdk=1 /p:AwesomiumSdkDir=C:\SDKs\Awesomium
```

For a parity-oriented rebuild of the helper, keep `QLBuildOnlineServices=1` and
run the dedicated verifier after the build. This checks the import surface and
linker/header profile for the executable while keeping the proprietary SDK
outside the repository:

```powershell
pwsh tools\ci\verify-awesomium-process-parity.ps1
```

The VS Code default `Build` task and the `Launch Debug Awesomium` task both use
the local online-services launch lane. That build enables the client's dynamic
Awesomium loader with
`QLRequireAwesomiumSdk=0`, writes
`build\win32\<Configuration>\bin\ql_build_settings.txt`, and stages the retail
Awesomium runtime payload from the Steam install root. The C/MSBuild project
properties still default Debug builds to `QLBuildOnlineServices=0`; the VS Code
task is an explicit local opt-in, while Release builds opt in by default. The
`Launch Quake Live` debugger profile does not use a
`preLaunchTask`, so run the build task explicitly before launching. The
standalone `launch.ps1 -EnableAwesomium` path also refuses to start if the stamp
reports `QLBuildOnlineServices=0`, because that offline build will always fall
back to the menu path instead of showing the WebUI.

## Repo-Managed Codec Bootstrap

The Windows MSBuild projects no longer probe Vcpkg or arbitrary system SDK
locations for the non-retail codec stack. Instead, they bootstrap the
repo-managed `libogg`, `libvorbis`, `zlib`, and `libpng` trees through
`tools/build_internal_deps.ps1`, staging the resulting headers and import
libraries under `src/libs/vorbis/` and `src/libs/libpng/`.

That bootstrap expects `cmake` and `git` on `PATH`. Missing dependency sources
under `src/libs/_deps/` are cloned automatically into that cache before MSBuild
continues, so solution or project builds can prepare codec prerequisites
without a manual pre-sync step.

These staged codec trees are still build-time conveniences, not part of the
retail runtime surface: the Steam install does not ship `vorbisfile.dll`,
`ogg.dll`, `libpng16.dll`, or `zlib1.dll`. Use
`pwsh tools/ci/validate-windows-native.ps1 -PlatformToolset v100 -RuntimeProfile retail`
to assemble and audit `build\win32\<Config>\retail-runtime\`, or rerun
`pwsh tools/ci/audit-retail-dependencies.ps1 -RuntimeRoot build\win32\Release\retail-runtime -SkipSteamInstall -Strict`
to re-check an existing staged runtime root directly. The mixed
`build\win32\<Config>\bin\` output can still carry those build-time codec DLLs,
so the strict retail payload boundary now lives in the dedicated
`retail-runtime` stage instead of the raw build directory.

Run `pwsh tools/ci/audit-retail-toolchain.ps1 -Strict` to verify that the
retail-facing project files still match the recovered VC10-era build settings
and that the local machine actually has the `v100` toolset installed.
Run `pwsh tools/ci/audit-retail-metadata.ps1` to verify that the launcher
version resources and embedded manifests still match the retail executables.

For a modern-host build verification pass that keeps the checked-in `v100`
defaults intact but compiles with `v141`, run:

```powershell
pwsh tools\ci\validate-windows-native.ps1 -PlatformToolset v141 -RuntimeProfile modern
```

For the strict retail validation lane, run:

```powershell
pwsh tools\ci\validate-windows-native.ps1 -PlatformToolset v100 -RuntimeProfile retail
```

That lane now stages `build\win32\<Config>\retail-runtime\` from the rebuilt
executables and gameplay/UI DLLs plus the exact retail launcher DLL payload in
`assets\quakelive\`, then fails fast if an extra non-retail DLL appears in that
staged runtime root.

When you target a `.vcxproj` directly, keep using `/p:Platform=Win32`. The
solution-level builds use `x86` because that is the platform name advertised by
`src/code/quakelive.sln`.

## Verifying incremental builds

To confirm that MSBuild’s tracking stays intact for both pipelines, run each set
of switches twice in a row. The second invocation should report that every
project is already up to date (look for "Project is up-to-date" or "Skipping
project" in the output):

```powershell
msbuild src\code\quakelive.sln /t:qagamex86;cgamex86;awesomium_process /p:Configuration=Debug /p:Platform=x86
msbuild src\code\quakelive.sln /t:qagamex86;cgamex86;awesomium_process /p:Configuration=Debug /p:Platform=x86
msbuild src\code\quakelive.sln /t:game;cgame /p:Configuration=Debug /p:Platform=x86
msbuild src\code\quakelive.sln /t:game;cgame /p:Configuration=Debug /p:Platform=x86
```

Successful “up-to-date” messages on the second pass confirm incremental builds
are working for both the native DLLs and the legacy VMs.【F:src/code/game/qagamex86.vcxproj†L88-L135】【F:src/code/cgame/cgamex86.vcxproj†L67-L104】
