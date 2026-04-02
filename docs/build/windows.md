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

## Building from the command line

Use the new project names as MSBuild targets when producing the native DLL set.
These `/t:` selectors are the switches that route MSBuild toward the
corresponding pipeline:

```powershell
msbuild src\code\quakelive.sln /t:qagamex86;cgamex86;awesomium_process /p:Configuration=Release /p:Platform=x86 /p:PlatformToolset=v100
```

The original VM builds remain available under the historical target names. For
example, the following command rebuilds the interpreted modules while leaving
the native DLLs untouched:

```powershell
msbuild src\code\quakelive.sln /t:game;cgame /p:Configuration=Release /p:Platform=x86
```

## Modern compatibility override

If you want to keep the checked-in `v100` project defaults but build the native
targets with the Visual Studio 2017 compiler on a newer host, install the
optional `v141` toolset and pass it on the command line:

```powershell
pwsh tools\ci\install-vs-toolset.ps1 -PlatformToolset v141
pwsh tools\ci\verify-vs-toolchain.ps1 -PlatformToolset v141 -RequireToolset
msbuild src\code\quakelive.sln /t:qagamex86;cgamex86;awesomium_process /p:Configuration=Release /p:Platform=x86 /p:PlatformToolset=v141
```

This path is a deliberate compatibility exception. It improves buildability on
modern systems, but it no longer reproduces the retail VC10 compiler/linker or
CRT import surface.

`awesomium_process.exe` respects the same online-services policy as the rest of
the launcher stack. `QLBuildOnlineServices` defaults to `0`, which produces an
offline-safe stub that exits cleanly without loading `awesomium.dll`. Set
`/p:QLBuildOnlineServices=1` if you want the helper to forward into the retail
Awesomium child-process entry point:

```powershell
msbuild src\code\awesomium_process.vcxproj /p:Configuration=Release /p:Platform=Win32 /p:PlatformToolset=v100 /p:QLBuildOnlineServices=1
```

For a parity-oriented rebuild of the helper, keep `QLBuildOnlineServices=1` and
run the dedicated verifier after the build. This checks the retail-facing
version resource, import surface, and linker/header profile for the executable:

```powershell
pwsh tools\ci\verify-awesomium-process-parity.ps1
```

## Codec SDK prerequisites

The Visual Studio projects now assume the Vorbis headers and import libraries
are available so the client’s Ogg decoder can link successfully. Place the
official Xiph.Org SDK (or any build that ships `vorbisfile.lib`, `vorbis.lib`,
`ogg.lib`, and the matching `include/vorbis/` headers) under
`src/libs/vorbis/` and the MSBuild files will automatically pull them in for
both Debug and Release outputs. If you keep the SDK somewhere else, define the
`VorbisSdkDir` property when invoking MSBuild:

```powershell
msbuild src\code\quakelive.sln /t:quakelive_steam /p:Configuration=Debug /p:VorbisSdkDir=C:\SDKs\vorbis-1.3.7
```

Without these libraries the linker fails fast, mirroring the Unix makefile’s
`OGG_CFLAGS`/`OGG_LDFLAGS` checks.

The repo also carries libpng/zlib development copies under `src/libs/libpng/`.
These codec SDK layouts are build-time conveniences, not part of the retail
runtime surface: the Steam install does not ship `vorbisfile.dll`, `ogg.dll`,
`libpng16.dll`, or `zlib1.dll`. Use
`pwsh tools/ci/audit-retail-dependencies.ps1 -Strict` to verify that the staged
runtime still matches the retail DLL payload.

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
