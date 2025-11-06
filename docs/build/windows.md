# Windows Native Build Targets

The Visual Studio solution under `src/code/quake3.sln` now ships with dedicated
native builds for the Quake Live gameplay modules. Each native project is a
copy of its VM counterpart, but the output is redirected to
`build/win32-native/` and the Visual Studio 2010 (`v100`) toolset is enforced so
the produced DLLs match the shipping runtime.【F:src/code/game/qagamex86.vcxproj†L2-L135】【F:src/code/cgame/cgamex86.vcxproj†L2-L110】【F:src/code/q3_ui/uix86.vcxproj†L1-L120】

## Available targets

| Target name | Project file | Output artifact |
|-------------|--------------|-----------------|
| `qagamex86` | `src/code/game/qagamex86.vcxproj` | `build/win32-native/qagamex86/<Config>/qagamex86.dll` |
| `cgamex86`  | `src/code/cgame/cgamex86.vcxproj` | `build/win32-native/cgamex86/<Config>/cgamex86.dll` |
| `uix86`     | `src/code/q3_ui/uix86.vcxproj`     | `build/win32-native/uix86/<Config>/uix86.dll` |

## Building from the command line

Use the new project names as MSBuild targets when producing the native DLL set.
These `/t:` selectors are the switches that route MSBuild toward the
corresponding pipeline:

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

To confirm that MSBuild’s tracking stays intact for both pipelines, run each set
of switches twice in a row. The second invocation should report that every
project is already up to date (look for "Project is up-to-date" or "Skipping
project" in the output):

```powershell
msbuild src\code\quake3.sln /t:qagamex86;cgamex86;uix86 /p:Configuration=Debug /p:Platform=Win32
msbuild src\code\quake3.sln /t:qagamex86;cgamex86;uix86 /p:Configuration=Debug /p:Platform=Win32
msbuild src\code\quake3.sln /t:game;cgame;q3_ui /p:Configuration=Debug /p:Platform=Win32
msbuild src\code\quake3.sln /t:game;cgame;q3_ui /p:Configuration=Debug /p:Platform=Win32
```

Successful “up-to-date” messages on the second pass confirm incremental builds
are working for both the native DLLs and the legacy VMs.【F:src/code/game/qagamex86.vcxproj†L88-L135】【F:src/code/cgame/cgamex86.vcxproj†L67-L104】【F:src/code/q3_ui/uix86.vcxproj†L64-L117】
