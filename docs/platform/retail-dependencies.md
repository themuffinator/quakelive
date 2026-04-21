# Retail Windows Dependency Audit

This document records the external Windows dependencies exposed by the retail
Steam build of Quake Live, using the committed payload in `assets/quakelive/`
and a local Steam install under
`C:\Program Files (x86)\Steam\steamapps\common\Quake Live` as evidence.

## Key findings

- The local Steam install contained 15 `.dll` files: 9 launcher/runtime DLLs in
  the install root plus 2 per-user copies of each gameplay module under the
  SteamID homepaths.
- After normalizing the SteamID homepath layout back to `baseq3\*.dll`, all 15
  installed DLLs matched the committed `assets/quakelive/` copies byte-for-byte.
- The retail gameplay DLLs have a minimal external surface:
  - `cgamex86.dll` imports `KERNEL32.dll` and `MSVCR100.dll`
  - `qagamex86.dll` imports `KERNEL32.dll`, `MSVCR100.dll`, and `MSVCP100.dll`
  - `uix86.dll` imports `KERNEL32.dll` and `MSVCR100.dll`
- `quakelive_steam.exe` imports `awesomium.dll`, `steam_api.dll`, the Visual
  C++ 2010 CRT pair, and ordinary Win32 system DLLs.
- `awesomium_process.exe` imports only `KERNEL32.dll` and `awesomium.dll`; it
  does not import `MSVCR100.dll` or `MSVCP100.dll`.
- `awesomium.dll` is the primary dependency concentrator for the browser stack:
  it imports ANGLE/WinHTTP/crypto/input/media support from the OS and
  delay-loads `avcodec-53.dll`, `avformat-53.dll`, `avutil-51.dll`, `d3d9.dll`,
  `d3dx9_43.dll`, `dxva2.dll`, `MF.dll`, and `MFPlat.dll`.

## Bundled retail payload

These files are present in both the committed retail payload and the current
Steam install.

| File | Observed version | Status |
| --- | --- | --- |
| `quakelive_steam.exe` | `0.1.0.739` | Exact retail binary present in `assets/quakelive/` |
| `awesomium_process.exe` | `1.7.4.1` | Exact retail binary present in `assets/quakelive/` |
| `awesomium.dll` | `1.7.4.2` | Exact retail binary present in `assets/quakelive/` |
| `steam_api.dll` | `02.89.45.04` | Exact retail binary present in `assets/quakelive/` |
| `libEGL.dll` | `1.0.0.939` | Exact retail binary present in `assets/quakelive/` |
| `libGLESv2.dll` | `1.0.0.939` | Exact retail binary present in `assets/quakelive/` |
| `icudt.dll` | `4.6.0.0` | Exact retail binary present in `assets/quakelive/` |
| `xinput9_1_0.dll` | `9.10.455.0000` | Exact retail binary present in `assets/quakelive/` |
| `avcodec-53.dll` | no Win32 version resource | Exact retail binary present in `assets/quakelive/`; soname proven, upstream tag unresolved locally |
| `avformat-53.dll` | no Win32 version resource | Exact retail binary present in `assets/quakelive/`; string banner shows `Lavf53.5.0` |
| `avutil-51.dll` | no Win32 version resource | Exact retail binary present in `assets/quakelive/`; soname proven, upstream tag unresolved locally |
| `baseq3\cgamex86.dll` | no Win32 version resource | Exact retail binary present in `assets/quakelive/` |
| `baseq3\qagamex86.dll` | no Win32 version resource | Exact retail binary present in `assets/quakelive/` |
| `baseq3\uix86.dll` | no Win32 version resource | Exact retail binary present in `assets/quakelive/` |

## Per-DLL import summary

Observed fact: the installed retail DLLs split into a few clear dependency bands.

- Gameplay DLLs:
  - `cgamex86.dll` imports only `KERNEL32.dll` and `MSVCR100.dll`
  - `qagamex86.dll` imports only `KERNEL32.dll`, `MSVCR100.dll`, and `MSVCP100.dll`
  - `uix86.dll` imports only `KERNEL32.dll` and `MSVCR100.dll`
- FFmpeg helper DLLs:
  - `avutil-51.dll` imports `KERNEL32.dll` and `msvcrt.dll`
  - `avcodec-53.dll` imports `avutil-51.dll`, `KERNEL32.dll`, `msvcrt.dll`, and `WS2_32.dll`
  - `avformat-53.dll` imports `avcodec-53.dll`, `avutil-51.dll`, `KERNEL32.dll`, and `msvcrt.dll`
- ANGLE/OpenGL translation DLLs:
  - `libEGL.dll` imports `libGLESv2.dll`, `d3d9.dll`, `dwmapi.dll`, `GDI32.dll`, `KERNEL32.dll`, and `USER32.dll`
  - `libGLESv2.dll` imports `d3d9.dll`, `D3DCOMPILER_43.dll`, `d3dx9_43.dll`, and `KERNEL32.dll`
- Launcher/browser support DLLs:
  - `steam_api.dll` imports `ADVAPI32.dll`, `KERNEL32.dll`, and `SHELL32.dll`
  - `xinput9_1_0.dll` imports `ADVAPI32.dll`, `KERNEL32.dll`, `ntdll.dll`, and `SETUPAPI.dll`
  - `icudt.dll` exposes no further import table entries; it behaves like a pure data payload
- Browser core:
  - `awesomium.dll` concentrates the largest dependency surface and imports the bundled FFmpeg DLLs, Direct3D/Media Foundation helpers, `XINPUT9_1_0.dll`, WinHTTP/crypto/UI stacks, and ordinary Win32 system DLLs

## System-provided imports

These dependencies are not shipped inside the Quake Live install, but the
retail binaries import them from the operating system.

### Required by the gameplay/host layer

- `MSVCR100.dll`
- `MSVCP100.dll`
- `KERNEL32.dll`
- `WS2_32.dll`
- `COMCTL32.dll`
- `WINMM.dll`
- `DINPUT8.dll`
- `IPHLPAPI.dll`
- `USER32.dll`
- `GDI32.dll`
- `ADVAPI32.dll`
- `SHELL32.dll`
- `ole32.dll`

### Required by the browser/media layer

- `OLEAUT32.dll`
- `USERENV.dll`
- `urlmon.dll`
- `RPCRT4.dll`
- `WINHTTP.dll`
- `dhcpcsvc.dll`
- `SETUPAPI.dll`
- `MSIMG32.dll`
- `USP10.dll`
- `PSAPI.dll`
- `SHLWAPI.dll`
- `IMM32.dll`
- `OLEACC.dll`
- `Secur32.dll`
- `CRYPT32.dll`
- `VERSION.dll`
- Delay-loaded `USER32.dll`
- Delay-loaded `SHELL32.dll`
- Delay-loaded `d3d9.dll`
- Delay-loaded `d3dx9_43.dll`
- Delay-loaded `dxva2.dll`
- Delay-loaded `MF.dll`
- Delay-loaded `MFPlat.dll`

## Exactness decisions in this repo

### Exact retail binaries we can and should use

- The proprietary launcher/browser/media DLLs already shipped in
  `assets/quakelive/` should remain the canonical exact-version payload.
- `tools/ci/audit-retail-dependencies.ps1` now verifies that a local Steam
  install still matches the committed retail payload.
- Retail-facing project files should stay on the Visual Studio 2010 `v100`
  toolset.
- Retail gameplay/host outputs should keep the Visual C++ 2010 CRT binding
  where the retail binaries imported it.

### Dependencies that are OS-owned rather than repo-owned

- `MSVCR100.dll` and `MSVCP100.dll` are required, but the exact file build is a
  machine/runtime concern rather than a repository asset.
- DirectX, Media Foundation, WinHTTP, crypto, and other Win32 system DLLs are
  likewise resolved from the host OS.

### Open-source codec libraries that are not retail runtime DLLs

The repo currently vendors development copies of these libraries:

| Library | Current repo version | Retail external-DLL evidence |
| --- | --- | --- |
| libvorbis | `1.3.7` | None |
| libogg | `1.3.6` | None |
| libpng | `1.6.53` | None |
| zlib | `1.3.1` | None |

Observed fact: the retail Steam install does not ship `vorbisfile.dll`,
`vorbis.dll`, `ogg.dll`, `libpng16.dll`, or `zlib1.dll`.

Inference: these codec stacks were either statically linked into the retail
game binaries or replaced by different in-tree code, so the repo’s dynamic SDK
layout should be treated as a development convenience rather than as the retail
dependency surface.

## Staged retail runtime boundary

Observed fact: the repo-managed Windows build output under
`build\win32\<Config>\bin\` can legitimately contain extra dependency DLLs
copied from the in-repo Vorbis/libpng/FreeType bootstrap lanes
(`vorbisfile.dll`, `vorbis.dll`, `ogg.dll`, `libpng16.dll`, `zlib1.dll`,
`freetype.dll`, and related helper DLLs). That mixed build root is useful for
development, but it is not the strict retail payload boundary.

The parity-oriented Windows validator now resolves that ambiguity by staging a
clean runtime root at `build\win32\<Config>\retail-runtime\`:

- rebuilt host executables are copied in from `build\win32\<Config>\bin\`
- rebuilt gameplay/UI DLLs are copied in from the native module outputs
- only the exact retail browser/media/Steam/XInput DLL payload from
  `assets\quakelive\` is copied beside them

`tools/ci/validate-windows-native.ps1 -RuntimeProfile retail` then runs
`tools/ci/audit-retail-dependencies.ps1 -RuntimeRoot <stage> -SkipSteamInstall -Strict`
against that staged root so parity validation fails fast if an extra
non-retail DLL is introduced or a required retail DLL goes missing. The
external launcher/media payload is hash-matched against retail; the rebuilt
`cgamex86.dll`, `qagamex86.dll`, and `uix86.dll` slots are required to be
present in the staged root but are intentionally allowed to differ from retail
hashes because they are the outputs under validation.

## Current repository adjustments

- Retail-facing `.vcxproj` files now default back to `v100`.
- Retail gameplay/host targets now default to `/MD` or `/MDd` where the retail
  binaries imported the Visual C++ CRT.
- `awesomium_process.exe` remains `/MT`-based, matching its retail import
  surface, which does not include `MSVCR100.dll`.
- The Windows runtime docs now distinguish retail runtime payloads from the
  repo’s non-retail codec SDK convenience copies.

## Reproducing the audit

Run the audit script from the repo root:

```powershell
pwsh tools\ci\audit-retail-dependencies.ps1
```

Use `-Strict` to fail the run when the Steam install differs from the committed
retail payload. When the committed DLL corpus is not present locally, the
script falls back to the installed Steam payload as its reference source.

To audit the strict staged runtime root instead of a local Steam install, run:

```powershell
pwsh tools\ci\audit-retail-dependencies.ps1 -RuntimeRoot build\win32\Release\retail-runtime -SkipSteamInstall -Strict
```

The retail validation lane assembles that `retail-runtime` tree
automatically. Use the command above when you want to re-check an already
staged runtime root directly without rerunning the full native build wrapper.
