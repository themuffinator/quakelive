# Native Toolchain Support Matrix

This matrix tracks the host expectations for rebuilding Quake Live’s native gameplay modules and highlights the 32-bit runtime payloads required to exercise those binaries on each platform.

| Platform | Preferred toolchain | Build status | 32-bit runtime dependencies | Notes |
| --- | --- | --- | --- | --- |
| Windows 10/11 (Win32) | Visual Studio 2010 SP1 or a newer release with the optional `v100` component | GitHub Actions’ “Native DLL (VS2010)” job installs `v100`, builds `Release\|Win32`, and asserts the export manifest; local developers must still retarget the projects manually | Visual C++ 2010 CRT (`MSVCR100.dll`, `MSVCP100.dll`)<br>Launcher payload: Awesomium (`awesomium.dll`, `awesomium_process.exe`), Chromium/FFmpeg helpers (`libEGL.dll`, `libGLESv2.dll`, `avcodec-53.dll`, `avformat-53.dll`, `avutil-51.dll`), Steamworks loader (`steam_api.dll`), ICU data (`icudt.dll`), XInput shim (`xinput9_1_0.dll`) | `game` and `cgame` already ship as Win32 DLL projects; retarget each to `v100`, keep the `/MD` runtime, and build `Release\|Win32` to mirror Quake Live’s exports.【F:docs/windows-native-pipeline.md†L1-L24】【F:docs/toolchain-ci.md†L1-L18】【F:docs/quakelive_asset_audit.md†L19-L31】【F:docs/reference-mapping.md†L18-L24】 |
| Windows 7 (WOW64) | Visual Studio 2010 SP1 targeting Win32 | Not covered by CI; expected to function once the solution is retargeted to `v100` | Visual C++ 2010 CRT (`MSVCR100.dll`, `MSVCP100.dll`)<br>Same launcher payload as modern Windows | WOW64 continues to load the Win32 DLLs when the redistributable and launcher support files accompany the modules; capturing smoke tests remains a follow-up.【F:docs/build-pipeline.md†L18-L34】【F:docs/quakelive_asset_audit.md†L19-L31】【F:docs/reference-mapping.md†L18-L24】 |
| Linux (x86, glibc) | GCC toolchain producing 32-bit `qagamei386.so` | Documented build/parity script under `docs/build/linux-glibc-32bit.md` + `tools/build/linux32_qagame.sh` | glibc-based userland (`libc6`)<br>X11 with DGA & VidMode extensions<br>Vendor OpenGL drivers (Mesa + Glide for 3dfx era) | Historical README documents the 32-bit runtime expectations; the new preset installs the matching 32-bit headers, emits `qagamei386.so`, and diffs it against the archived shared object for symbol parity.【F:docs/build/linux-glibc-32bit.md†L1-L39】【F:docs/reference-mapping.md†L18-L24】【F:src/code/unix/README.Linux†L68-L155】【F:src/README.txt†L180-L188】【F:tools/build/linux32_qagame.sh†L1-L36】 |

## Windows requirements

- Install Visual Studio 2010 SP1 or a modern release that bundles the optional “Visual Studio 2010 (v100) toolset,” then retarget each gameplay project (`game`, `cgame`) to that toolset before building the `Release|Win32` configuration.【F:docs/windows-native-pipeline.md†L1-L24】
- Keep the `/MD` runtime library selection so the DLLs continue to import `MSVCR100.dll` and `MSVCP100.dll`, matching the reference binaries analysed in the migration notes.【F:docs/windows-native-pipeline.md†L17-L24】【F:docs/hlil_comparison.md†L8-L15】
- Stage the Visual C++ 2010 CRT next to the launcher payload (`awesomium.dll`, Chromium/FFmpeg helpers, `steam_api.dll`, `icudt.dll`, `xinput9_1_0.dll`) so runtime imports resolve exactly as observed in the reference dump.【F:docs/quakelive_asset_audit.md†L17-L25】
- Use `dumpbin /exports` and `dumpbin /imports` (or the CI helpers) to verify the rebuilt DLLs expose only `dllEntry` and `vmMain` while depending solely on the Visual C++ 2010 CRT plus the Steam/Awesomium launcher payload recorded in the asset audit.【F:docs/windows-native-pipeline.md†L22-L24】【F:docs/toolchain-ci.md†L11-L18】

## Linux requirements

- Target a glibc-based distribution capable of producing 32-bit binaries; the archived guidance calls for GCC along with the original OpenGL/X11 development headers used by the Quake III Unix port.【F:src/code/unix/README.Linux†L68-L155】【F:src/README.txt†L180-L188】
- Ensure runtime hosts provide X11 with DGA and VidMode extensions, plus vendor-specific OpenGL drivers (or Mesa/Glide for 3dfx hardware) so the 32-bit `qagamei386.so` and other shared objects can load as they did in Quake Live.【F:src/code/unix/README.Linux†L84-L155】
- Reference `qagamei386.so` from `assets/quakelive/baseq3/` when validating the rebuilt library to confirm symbol parity with the original Quake Live server module.【F:docs/reference-mapping.md†L18-L24】

### 32-bit runtime payload reference

- **Windows hosts:** Visual C++ 2010 CRT (`MSVCR100.dll`, `MSVCP100.dll`), launcher binaries (`quakelive_steam.exe`, `awesomium_process.exe`), and supporting DLLs for Awesomium, Chromium/FFmpeg, Steamworks, ICU, and XInput as catalogued in the asset audit.【F:docs/quakelive_asset_audit.md†L17-L25】
- **Linux hosts:** glibc-based userland (`libc6`), X11 stack with DGA and VidMode extensions, and vendor OpenGL drivers (Mesa/Glide for 3dfx hardware) per the historical Linux README.【F:src/code/unix/README.Linux†L68-L155】

## Outstanding follow-ups

- Automate retargeting or validation so the Visual Studio projects default to the `v100` toolset and fail fast if the required CRT or launcher runtime is missing.【F:docs/windows-native-pipeline.md†L15-L24】【F:docs/quakelive_asset_audit.md†L19-L31】
- Capture WOW64-specific smoke tests (e.g., on Windows 7) to ensure the 32-bit DLLs load once the Visual C++ redistributable and launcher payload are staged.【F:docs/build-pipeline.md†L16-L25】
- Capture additional CI coverage for the 32-bit glibc preset if we want automated parity checks beyond the manual helper script.【F:docs/build/linux-glibc-32bit.md†L1-L39】【F:tools/build/linux32_qagame.sh†L1-L36】
