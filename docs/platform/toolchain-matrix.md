# Native Toolchain Support Matrix

This matrix summarizes the build hosts and runtime components required to reproduce Quake Live's native (DLL/SO) modules alongside the project's current readiness for each platform.

| Platform | Preferred toolchain | Build status | 32-bit runtime dependencies | Notes |
| --- | --- | --- | --- | --- |
| Windows 10/11 (Win32) | Visual Studio 2010 SP1 or newer with the `v100` toolset | Documentation ready; projects still default to `v143` | Visual C++ 2010 CRT (`MSVCR100.dll`, `MSVCP100.dll`); Awesomium runtime (`awesomium.dll`, `awesomium_process.exe`); Chromium/FFmpeg support DLLs (`libEGL.dll`, `libGLESv2.dll`, `avcodec-53.dll`, `avformat-53.dll`, `avutil-51.dll`); Steamworks loader (`steam_api.dll`); ICU and XInput shims (`icudt.dll`, `xinput9_1_0.dll`) | Solution already contains Win32 DLL projects (`game`, `cgame`, `q3_ui`). Retarget to `v100` and rebuild Release|Win32 to match Quake Live exports. 【F:docs/windows-native-pipeline.md†L1-L24】【F:docs/reference-mapping.md†L18-L24】 |
| Windows 7 (WOW64) | Visual Studio 2010 SP1 with Win32 configuration | Legacy-compatible once retargeted | Visual C++ 2010 CRT (`MSVCR100.dll`, `MSVCP100.dll`); Steamworks launcher payload (same DLL set as above) | WOW64 hosts can load the same Win32 DLLs once the CRT and launcher payloads are installed; plan still requires retargeting the projects to `v100`. 【F:docs/build-pipeline.md†L16-L25】【F:docs/reference-mapping.md†L18-L24】 |
| Linux (x86, glibc) | GCC toolchain targeting 32-bit `qagamei386.so` | Untested; reference binaries only | glibc-based userland (libc6), X11 OpenGL stack, vendor-specific GL drivers | Legacy README confirms glibc requirement; native `.so` builds exist in reference assets but no automated pipeline yet. 【F:docs/reference-mapping.md†L18-L24】【F:src/code/unix/README.Linux†L68-L112】 |

## Key follow-ups
- Retarget the Visual Studio projects under `src/code/` to the `v100` toolset and automate dependency validation (CRT, Steamworks, Awesomium).【F:docs/windows-native-pipeline.md†L15-L24】
- Capture WOW64-specific smoke tests to ensure 32-bit DLLs run correctly on modern 64-bit Windows installations once the redistributables are present.【F:docs/build-pipeline.md†L16-L25】
- Define a reproducible Linux native build that emits `qagamei386.so` with a documented glibc baseline, mirroring the archived binaries. 【F:docs/reference-mapping.md†L18-L24】【F:src/code/unix/README.Linux†L68-L112】
