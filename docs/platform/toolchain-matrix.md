# Native Toolchain Support Matrix

This matrix tracks the host expectations for rebuilding Quake Live’s native gameplay modules and highlights the 32-bit runtime payloads required to exercise those binaries on each platform.

| Platform | Preferred toolchain | Build status | 32-bit runtime dependencies | Notes |
| --- | --- | --- | --- | --- |
| Windows 10/11 (Win32) | Visual Studio 2010 SP1 or newer with the legacy `v100` toolset | Solution projects are present but still default to `v143`; rebuilds rely on manual retargeting | Visual C++ 2010 CRT (`MSVCR100.dll`, `MSVCP100.dll`); launcher payload including Awesomium (`awesomium.dll`, `awesomium_process.exe`), Chromium/FFmpeg helpers (`libEGL.dll`, `libGLESv2.dll`, `avcodec-53.dll`, `avformat-53.dll`, `avutil-51.dll`), Steamworks loader (`steam_api.dll`), ICU data (`icudt.dll`), and XInput shim (`xinput9_1_0.dll`) | `game`, `cgame`, and `q3_ui` already ship as Win32 DLL projects; retarget each to `v100` before building `Release|Win32` to mirror Quake Live’s exports.【F:docs/windows-native-pipeline.md†L1-L24】【F:docs/quakelive_asset_audit.md†L19-L31】【F:docs/reference-mapping.md†L18-L24】 |
| Windows 7 (WOW64) | Visual Studio 2010 SP1 targeting Win32 | Expected to work once the solution is retargeted; no automated coverage | Same CRT and launcher payload as modern Windows; relies on Steamworks/Awesomium stack to satisfy loader imports | WOW64 continues to load the Win32 DLLs provided the Visual C++ 2010 redistributable and launcher support files are installed alongside the modules.【F:docs/build-pipeline.md†L16-L25】【F:docs/quakelive_asset_audit.md†L19-L31】【F:docs/reference-mapping.md†L18-L24】 |
| Linux (x86, glibc) | GCC toolchain producing 32-bit `qagamei386.so` | Reference `.so` files exist; rebuild flow not yet validated | glibc-based userland (libc6), X11 stack with DGA/VidMode extensions, vendor OpenGL drivers (Mesa + Glide for 3dfx era) | Historical README documents the 32-bit runtime expectations; aligning the build with those requirements remains future work.【F:docs/reference-mapping.md†L18-L24】【F:src/code/unix/README.Linux†L84-L153】 |

## Windows requirements

- Install Visual Studio 2010 SP1 or a modern release that bundles the optional “Visual Studio 2010 (v100) toolset,” then retarget each gameplay project (`game`, `cgame`, `q3_ui`) to that toolset before building the `Release|Win32` configuration.【F:docs/windows-native-pipeline.md†L1-L24】
- Keep the `/MD` runtime library selection so the DLLs continue to import `MSVCR100.dll` and `MSVCP100.dll`, matching the reference binaries analysed in the migration notes.【F:docs/windows-native-pipeline.md†L17-L24】【F:docs/hlil_comparison.md†L8-L15】
- Use `dumpbin /exports` and `dumpbin /imports` (or the CI helpers) to verify the rebuilt DLLs expose only `dllEntry` and `vmMain` while depending solely on the Visual C++ 2010 CRT plus the Steam/Awesomium launcher payload recorded in the asset audit.【F:docs/windows-native-pipeline.md†L24-L24】【F:docs/quakelive_asset_audit.md†L19-L31】

## Linux requirements

- Target a glibc-based distribution capable of producing 32-bit binaries; the archived guidance calls for GCC along with the original OpenGL/X11 development headers used by the Quake III Unix port.【F:src/code/unix/README.Linux†L68-L153】【F:src/README.txt†L180-L188】
- Ensure runtime hosts provide X11 with DGA and VidMode extensions, plus vendor-specific OpenGL drivers (or Mesa/Glide for 3dfx hardware) so the 32-bit `qagamei386.so` and other shared objects can load as they did in Quake Live.【F:src/code/unix/README.Linux†L84-L153】
- Reference `qagamei386.so` from `references/original-assets/quakelive/baseq3/` when validating the rebuilt library to confirm symbol parity with the original Quake Live server module.【F:docs/reference-mapping.md†L18-L24】

## Outstanding follow-ups

- Automate retargeting or validation so the Visual Studio projects default to the `v100` toolset and fail fast if the required CRT or launcher runtime is missing.【F:docs/windows-native-pipeline.md†L15-L24】【F:docs/quakelive_asset_audit.md†L19-L31】
- Capture WOW64-specific smoke tests (e.g., on Windows 7) to ensure the 32-bit DLLs load once the Visual C++ redistributable and launcher payload are staged.【F:docs/build-pipeline.md†L16-L25】
- Define and document a reproducible Linux 32-bit build configuration that emits `qagamei386.so` against a known glibc baseline, mirroring the archived binaries in the repository.【F:docs/reference-mapping.md†L18-L24】【F:src/code/unix/README.Linux†L68-L153】
