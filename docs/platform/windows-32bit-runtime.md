# Windows 32-bit Runtime Guide

This guide covers how to prepare and verify a 32-bit runtime on modern Windows hosts, including WOW64 notes specific to Quake Live’s native DLLs.

## WOW64 considerations

* **Execution model:** The shipped gameplay DLLs are x86 targets. On 64-bit Windows they execute under WOW64, so ensure the `Program Files (x86)` path is used for tooling, and avoid forcing 64-bit host binaries into the pipeline.
* **File system redirection:** Installer paths and runtime probes should reference `%SystemRoot%\SysWOW64` for 32-bit system DLLs. Avoid copying artifacts into `%SystemRoot%\System32`, which hosts 64-bit binaries on WOW64 machines.
* **Registry redirection:** 32-bit registry keys land under `HKLM\Software\WOW6432Node`. If you depend on registry-based codec discovery or DirectX caps, read/write through the WOW6432 node to avoid mismatched capability checks.
* **Environment separation:** Keep 32-bit build outputs isolated (for example, `build\win32\Debug\`) and confirm MSBuild is invoked with `/p:Platform=Win32` so the correct compiler/linker frontends are used.

## Dependency installation

1. **Visual C++ 2010 SP1 x86 runtime** – Required for the MSVC v100 toolset outputs. Install the x86 redistributable (`vcredist_x86.exe`) on WOW64 hosts; the x64 package does not provide the 32-bit CRT.
2. **DirectX 9.0c runtime (June 2010)** – The launcher expects legacy D3DX and XAudio2 DLLs that are not shipped on newer Windows versions. Run the DirectX web installer or `DXSETUP.exe` from the redist package to seed the 32-bit copies into `%SystemRoot%\SysWOW64`.
3. **Vorbis/OGG codecs** – For local development, place the SDK headers and import libraries under `src\libs\vorbis\` and ensure the 32-bit `vorbisfile.dll`/`ogg.dll` variants are discoverable on the PATH or alongside the built DLLs.
4. **.NET Framework 4.x (Client profile)** – Needed only for auxiliary tools (e.g., launcher helpers). Install the 32-bit capable runtime on WOW64 hosts to keep the helper utilities aligned with the native client.

## Environment validation

Perform these checks after installing prerequisites:

1. **Confirm WOW64 status:** Run `wmic OS get OSArchitecture` or `set PROCESSOR_ARCHITECTURE` and verify `AMD64` with `WOW64` enabled; `PROCESSOR_ARCHITEW6432` should be set when spawning a 32-bit shell (`%SystemRoot%\SysWOW64\cmd.exe`).
2. **Verify redistributables:** Use `sigcheck -q -nobanner %SystemRoot%\SysWOW64\msvcr100.dll` (from Sysinternals) to ensure the 32-bit CRT is present and signed. If missing, reinstall the x86 Visual C++ runtime.
3. **Check DirectX presence:** Run `dxdiag /whql:off` and inspect the `DirectX Files` tab for `d3dx9_43.dll` under `SysWOW64`. Absence indicates the June 2010 runtime is not installed for 32-bit binaries.
4. **MSBuild targeting:** From a Visual Studio x86 Native Tools prompt, execute `msbuild src\code\quakelive.sln /t:qagamex86 /p:Platform=Win32 /p:Configuration=Debug` and verify outputs land in `build\win32\Debug\modules\qagamex86`. Any `“64-bit tools are not available”` warnings indicate the wrong developer prompt was used.

## Troubleshooting launch failures

| Symptom | Likely cause | Resolution |
| --- | --- | --- |
| `This application was unable to start correctly (0xc000007b)` | Mixing 64-bit CRT/DirectX DLLs with 32-bit binaries | Reinstall the x86 Visual C++ 2010 runtime and DirectX 9.0c; confirm DLL search order points at `SysWOW64` or co-located 32-bit copies. |
| Missing `d3dx9_43.dll` or `xinput1_3.dll` | DirectX 9.0c redist not installed for WOW64 | Run the June 2010 DirectX installer; confirm files appear under `SysWOW64` and rerun the launcher. |
| `MSVCR100.dll was not found` | x86 CRT not present | Install `vcredist_x86.exe` and rerun; avoid installing only the x64 redistributable. |
| Launcher closes immediately with no logs | 32-bit helper fails to load dependent DLLs | Capture `ProcMon` traces filtered to the launcher process, verify DLL load paths, and co-locate missing 32-bit codecs or reroute `PATH` to the SDK directory. |
| `Failed to initialize renderer` | Running from 64-bit tools or GPU driver blocking DX9 | Rebuild using `/p:Platform=Win32`, launch from `SysWOW64\cmd.exe`, and update GPU drivers; if Secure Boot enforcement blocks unsigned DX9 components, install the signed June 2010 package. |

Capture Event Viewer `Application` log entries after each failure and attach `ProcMon` traces when escalating issues so the build team can reproduce the WOW64 environment.
