# Building QuakeLive-reverse

This file is the short entry point for building the reconstructed codebase.
Use it for the common commands, then follow the deeper docs under `docs/build/`
when you need platform-specific detail or parity validation.

Build success does not currently imply a fully playable Quake Live clone. This
repository is still reconstructing retail behavior and uses build output as one
part of the parity workflow.

## Windows native build

Windows is the primary native build path in this repository.

Requirements:

- Retail-faithful path: Visual Studio 2010 SP1, or a newer Visual Studio
  install with the `v100` toolset available
- Modern-host compatibility path: a newer Visual Studio install with the
  Visual Studio 2017 `v141` toolset available
- MSBuild on `PATH`
- CMake on `PATH` for the repo-managed codec bootstrap
- Repo-managed third-party codec sources under `src/libs/_deps/`
  The Windows projects now bootstrap `libogg`, `libvorbis`, `zlib`, and
  `libpng` from that tree instead of probing system SDK or Vcpkg installs.

Build the recovered native gameplay modules and helper executable with the
retail-default toolset:

```powershell
msbuild src\code\quakelive.sln /t:qagamex86;cgamex86;awesomium_process /p:Configuration=Debug /p:Platform=x86 /p:PlatformToolset=v100
```

Build the same native targets with the supported modern compatibility override:

```powershell
pwsh tools\ci\install-vs-toolset.ps1 -PlatformToolset v141
pwsh tools\ci\verify-vs-toolchain.ps1 -PlatformToolset v141 -RequireToolset
msbuild src\code\quakelive.sln /t:qagamex86;cgamex86;awesomium_process /p:Configuration=Debug /p:Platform=x86 /p:PlatformToolset=v141
```

Main outputs:

- `build/win32/Debug/modules/qagamex86/qagamex86.dll`
- `build/win32/Debug/modules/cgamex86/cgamex86.dll`
- `build/win32/Debug/bin/awesomium_process.exe`

The legacy VM targets remain available:

```powershell
msbuild src\code\quakelive.sln /t:game;cgame /p:Configuration=Debug /p:Platform=x86
```

Useful validation commands:

```powershell
pwsh tools\ci\audit-retail-toolchain.ps1 -Strict
pwsh tools\ci\audit-retail-dependencies.ps1 -Strict
pwsh tools\ci\audit-retail-metadata.ps1
```

Modern-host validation command:

```powershell
pwsh tools\ci\validate-windows-native.ps1 -PlatformToolset v141 -RuntimeProfile modern
```

Notes:

- Solution builds use `/p:Platform=x86`; direct `.vcxproj` builds use
  `/p:Platform=Win32`.
- The checked-in project defaults remain on `v100` for parity. `v141` is a
  deliberate command-line override for contributor compatibility on modern
  Windows hosts.
- On Windows, non-retail third-party dependencies are now expected to come from
  the repo-managed bootstrap flow only. The retail DLL payload remains a
  runtime concern under `assets/quakelive/`; it is no longer part of the
  non-retail codec build detection story.
- `QLBuildOnlineServices` defaults to `0`. Keep it disabled unless you are
  explicitly validating online-service parity or the Awesomium helper path.

See the full Windows guide at [`docs/build/windows.md`](docs/build/windows.md).

## Linux glibc 32-bit build

Linux support is currently limited to the 32-bit `qagamei386.so` server module.

On Debian/Ubuntu-style hosts, install the 32-bit glibc and X11/OpenGL
development stack described in the platform guide, then run:

```bash
BUILD_DIR=build/linux-i386-glibc tools/build/linux32_qagame.sh
```

Key outputs:

- `build/linux-i386-glibc/baseq3/qagamei386.so`
- `build/linux-i386-glibc/qagame.exports`
- `build/linux-i386-glibc/qagame-reference.exports`
- `build/linux-i386-glibc/qagame.exports.diff`

See the full Linux guide at
[`docs/build/linux-glibc-32bit.md`](docs/build/linux-glibc-32bit.md).

## More build references

- [`docs/platform/toolchain-matrix.md`](docs/platform/toolchain-matrix.md)
- [`docs/build/windows.md`](docs/build/windows.md)
- [`docs/build/linux-glibc-32bit.md`](docs/build/linux-glibc-32bit.md)
- [`docs/build-pipeline.md`](docs/build-pipeline.md)
