# Windows Native Build Targets

The Visual Studio solution under `src/code/quake3.sln` now exposes dedicated
projects for compiling the Quake Live gameplay DLLs with the legacy Visual
Studio 2010 (`v100`) toolset. The duplicated projects live alongside the
original VM projects and share the same source lists, but they drop their
outputs in `build/win32-native/` so native builds no longer collide with the
existing QVM intermediates.【F:src/code/game/qagamex86.vcxproj†L91-L132】【F:src/code/cgame/cgamex86.vcxproj†L67-L86】【F:src/code/q3_ui/uix86.vcxproj†L71-L98】

## Available targets

| Target name | Project file | Output artifact |
|-------------|--------------|-----------------|
| `qagamex86` | `src/code/game/qagamex86.vcxproj` | `build/win32-native/qagamex86/<Config>/qagamex86.dll` |
| `cgamex86`  | `src/code/cgame/cgamex86.vcxproj` | `build/win32-native/cgamex86/<Config>/cgamex86.dll` |
| `uix86`     | `src/code/q3_ui/uix86.vcxproj`     | `build/win32-native/uix86/<Config>/uix86.dll` |

All three projects are pinned to the `v100` toolset and build as Win32 dynamic
libraries so they match the runtime ABI used by the shipping Quake Live
modules.【F:src/code/game/qagamex86.vcxproj†L30-L64】【F:src/code/cgame/cgamex86.vcxproj†L28-L46】【F:src/code/q3_ui/uix86.vcxproj†L28-L46】

## Building from the command line

Use the project names as MSBuild targets to build the native DLL set without
touching the VM toolchain:

```powershell
msbuild src\code\quake3.sln /t:qagamex86;cgamex86;uix86 /p:Configuration=Release /p:Platform=Win32
```

The original VM builds remain available under the historical target names. For
example, the following command rebuilds the interpreted modules while leaving
the native DLLs untouched:

```powershell
msbuild src\code\quake3.sln /t:game;cgame;q3_ui /p:Configuration=Release /p:Platform=Win32
```

## Verifying incremental builds

Run the native build twice in a row and confirm that MSBuild reports “up-to-date”
for each of the new targets on the second invocation. Repeat the same check for
the legacy VM projects to ensure both pipelines respect incremental rebuilds:

```powershell
msbuild src\code\quake3.sln /t:qagamex86;cgamex86;uix86 /p:Configuration=Debug /p:Platform=Win32
msbuild src\code\quake3.sln /t:qagamex86;cgamex86;uix86 /p:Configuration=Debug /p:Platform=Win32
msbuild src\code\quake3.sln /t:game;cgame;q3_ui /p:Configuration=Debug /p:Platform=Win32
msbuild src\code\quake3.sln /t:game;cgame;q3_ui /p:Configuration=Debug /p:Platform=Win32
```

When the second pass reports that all targets are already up-to-date, both the
native and VM configurations are respecting MSBuild’s incremental build
tracking.
