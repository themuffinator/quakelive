# Native Toolchain Support Matrix

This matrix tracks the host expectations for rebuilding Quake Live’s native gameplay modules and highlights the 32-bit runtime payloads required to exercise those binaries on each platform.

| Platform | Preferred toolchain | Build status | 32-bit runtime dependencies | Notes |
| --- | --- | --- | --- | --- |
| Windows 10/11 (Win32) | Visual Studio 2010 SP1 or a newer release with the optional `v100` component | Validate locally with `tools/ci/validate-windows-native.ps1`, building `Release\|Win32`, asserting the export manifest, and staging `build\win32\<Config>\retail-runtime\` for a strict retail DLL audit after confirming the `v100` toolset is installed | Visual C++ 2010 CRT (`MSVCR100.dll`, `MSVCP100.dll`)<br>Launcher payload: Awesomium (`awesomium.dll`, `awesomium_process.exe`), Chromium/FFmpeg helpers (`libEGL.dll`, `libGLESv2.dll`, `avcodec-53.dll`, `avformat-53.dll`, `avutil-51.dll`), Steamworks loader (`steam_api.dll`), ICU data (`icudt.dll`), XInput shim (`xinput9_1_0.dll`) | The retail-facing project files now default to the recovered VC10/MSBuild 4.0 shape: `ToolsVersion=4.0`, `PlatformToolset=v100`, XP (`5.1`) subsystem targeting, retail CRT linkage, retail DLL base addresses, and the matching ASLR/NX/SafeSEH flags. Verify that with `tools/ci/audit-retail-toolchain.ps1`, and confirm both the local Steam payload and the staged strict runtime root with `tools/ci/audit-retail-dependencies.ps1`.【F:docs/platform/retail-toolchain.md†L1-L72】【F:docs/platform/retail-dependencies.md†L1-L84】 |
| Windows 7 (WOW64) | Visual Studio 2010 SP1 targeting Win32 | Local scripted smoke revalidated on 2026-04-21; still not covered by CI | Visual C++ 2010 CRT (`MSVCR100.dll`, `MSVCP100.dll`)<br>Same launcher payload as modern Windows | The retained WOW64 harness now prefers the retail DLLs from `assets\quakelive\baseq3\` when present and otherwise falls back to the current Win32 build outputs under `build\win32\Debug\bin\baseq3\`. A 2026-04-21 local run from 32-bit PowerShell loaded `qagamex86.dll`, `cgamex86.dll`, and `uix86.dll` successfully and resolved both `dllEntry` and `vmMain`; the current log is `artifacts\wow64-smoketest\wow64-smoketest.log`.【F:docs/testing/wow64-smoketest.md†L1-L51】【F:docs/build-pipeline.md†L18-L34】【F:docs/platform/retail-dependencies.md†L1-L79】 |
| Linux (x86, glibc) | GCC toolchain producing 32-bit `qagamei386.so` | Documented build/parity script under `docs/build/linux-glibc-32bit.md` + `tools/build/linux32_qagame.sh` | glibc-based userland (`libc6`)<br>X11 with DGA & VidMode extensions<br>Vendor OpenGL drivers (Mesa + Glide for 3dfx era) | Historical README documents the 32-bit runtime expectations; the new preset installs the matching 32-bit headers, emits `qagamei386.so`, and diffs it against the archived shared object for symbol parity. Treat that preset as server-module-only evidence rather than Linux client/runtime parity proof.【F:docs/build/linux-glibc-32bit.md†L1-L41】【F:docs/reference-mapping.md†L18-L24】【F:src/code/unix/README.Linux†L68-L155】【F:src/README.txt†L180-L188】【F:tools/build/linux32_qagame.sh†L1-L36】 |

## Windows requirements

- Install Visual Studio 2010 SP1 or a modern release that bundles the optional “Visual Studio 2010 (v100) toolset,” then build the checked-in retail-facing projects with `/p:PlatformToolset=v100`.【F:docs/windows-native-pipeline.md†L1-L24】
- Keep the `/MD` runtime library selection so the DLLs continue to import `MSVCR100.dll` and `MSVCP100.dll`, matching the reference binaries analysed in the migration notes.【F:docs/windows-native-pipeline.md†L17-L24】【F:docs/hlil_comparison.md†L8-L15】
- Stage the Visual C++ 2010 CRT next to the launcher payload (`awesomium.dll`, Chromium/FFmpeg helpers, `steam_api.dll`, `icudt.dll`, `xinput9_1_0.dll`) so runtime imports resolve exactly as observed in the reference dump.【F:docs/quakelive_asset_audit.md†L17-L25】
- Use `dumpbin /exports` and `dumpbin /imports` (or the CI helpers) to verify the rebuilt DLLs expose only `dllEntry` and `vmMain` while depending solely on the Visual C++ 2010 CRT plus the Steam/Awesomium launcher payload recorded in the asset audit.【F:docs/windows-native-pipeline.md†L22-L24】【F:docs/toolchain-ci.md†L11-L18】
- Run `pwsh tools\ci\audit-retail-dependencies.ps1 -Strict` to confirm a local Steam install still matches the committed retail payload, and use `pwsh tools\ci\audit-retail-dependencies.ps1 -RuntimeRoot build\win32\Release\retail-runtime -SkipSteamInstall -Strict` when you want to re-check the staged strict runtime root directly.【F:docs/platform/retail-dependencies.md†L80-L84】
- Run `pwsh tools\ci\audit-retail-toolchain.ps1 -Strict` to confirm the project files still encode the recovered retail compiler/linker settings and that a `v100` toolset is actually installed on the machine.【F:docs/platform/retail-toolchain.md†L66-L72】

## Linux requirements

- Target a glibc-based distribution capable of producing 32-bit binaries; the archived guidance calls for GCC along with the original OpenGL/X11 development headers used by the Quake III Unix port.【F:src/code/unix/README.Linux†L68-L155】【F:src/README.txt†L180-L188】
- Ensure runtime hosts provide X11 with DGA and VidMode extensions, plus vendor-specific OpenGL drivers (or Mesa/Glide for 3dfx hardware) so the 32-bit `qagamei386.so` and other shared objects can load as they did in Quake Live.【F:src/code/unix/README.Linux†L84-L155】
- Reference `qagamei386.so` from `assets/quakelive/baseq3/` when validating the rebuilt library to confirm symbol parity with the original Quake Live server module.【F:docs/reference-mapping.md†L18-L24】

### 32-bit runtime payload reference

- **Windows hosts:** Visual C++ 2010 CRT (`MSVCR100.dll`, `MSVCP100.dll`), launcher binaries (`quakelive_steam.exe`, `awesomium_process.exe`), and supporting DLLs for Awesomium, Chromium/FFmpeg, Steamworks, ICU, and XInput as catalogued in the asset audit.【F:docs/quakelive_asset_audit.md†L17-L25】
- **Linux hosts:** glibc-based userland (`libc6`), X11 stack with DGA and VidMode extensions, and vendor OpenGL drivers (Mesa/Glide for 3dfx hardware) per the historical Linux README.【F:src/code/unix/README.Linux†L68-L155】

## Outstanding follow-ups

- Publish the retained WOW64 smoke harness in a self-hosted or other 32-bit-capable validation lane if we want the current local 2026-04-21 log to become continuously enforced evidence instead of a manual refresh point.【F:docs/testing/wow64-smoketest.md†L1-L51】
- Capture additional automated or scripted coverage for the 32-bit glibc preset if we want parity checks beyond the manual helper script.【F:docs/build/linux-glibc-32bit.md†L1-L39】【F:tools/build/linux32_qagame.sh†L1-L36】

## Non-Windows native status

For the remaining engine host/support audit, the Unix and null trees are
compatibility-only ports rather than part of the retail replacement target.
That means the strict retail Windows engine-host/support score tracks them as documented divergences,
not as missing Windows parity. They stay visible in the ledger so portability
work is not forgotten, but they are excluded from the strict-retail parity score and the final `EH-P5` gate result.

- **Linux rebuilds remain server-only.** The documented glibc preset and helper script exclusively target the 32-bit `qagamei386.so` server module and explicitly disable Vorbis while diffing exports against the archived server binary, leaving the client and renderer unbuilt on Linux.【F:docs/build/linux-glibc-32bit.md†L1-L36】
- **Legacy rendering/input stack is unported.** The Unix makefile still advertises X11/GLX/DGA-era client builds tied to `/usr/X11R6` headers and Glide-era Mesa copies, while the legacy README calls for XFree86 with DGA/VidMode mouse paths and Glide-specific OpenGL drivers—none of which are wired into current automated validation or available on modern distributions.【F:src/code/unix/Makefile†L4-L198】【F:src/code/unix/README.Linux†L68-L177】
- **Audio path is anchored to OSS `/dev/dsp`.** The shipped Linux instructions require mmap’ing `/dev/dsp` with permissive device permissions, so there is no ALSA/PulseAudio shim or SDL abstraction to satisfy the sound backend on contemporary systems.【F:src/code/unix/README.Linux†L161-L177】
- **Platform syscall coverage remains partial, but the old Unix profiling no-op is now bounded.** `Sys_LowPhysicalMemory()` now queries physical page counts through `sysconf()`, and `Sys_FunctionCmp()` / `Sys_FunctionCheckSum()` now use Linux/glibc symbol metadata (`dladdr1(..., RTLD_DL_SYMENT)`) plus `Com_BlockChecksum()` to compare and checksum function bodies when symbol sizes are available. `Sys_MonkeyShouldBeSpanked()` now reconstructs the retained `q3monkeyid` release-marker probe from the historical Unix build lane, and `Sys_BeginProfiling()` / `Sys_EndProfiling()` now pause or resume `moncontrol()` and flush `_mcleanup()` when the Unix engine is built with `QL_ENABLE_GPROF=1`. The null host/runtime now carries current executable-name, path, timer, and loopback-network scaffolding plus browser/advert/input shim entry points, input bootstrap cvars and a no-op key-event pump, and silent sound/device activation/voice stubs instead of the old stale `FILE *`, `NET_StringToAdr`, `Com_Init( argc, argv )`, and missing web-host/audio/input entry points.【F:src/code/unix/unix_main.c†L102-L208】

### Blockers and next steps

- Modernise the Unix client toolchain by replacing the XFree86/GLX/DGA assumptions with SDL2 or a contemporary GL loader, then gate Linux client builds in a reproducible validation lane once the dependency chain works on current distros.【F:src/code/unix/Makefile†L4-L198】【F:src/code/unix/README.Linux†L68-L155】 Document interim skips for any renderer/input tests that assume GLX or DGA until the migration lands.
- Add an audio shim layer that can select ALSA/PulseAudio backends (or a null sink for headless runs) so `/dev/dsp` is no longer required; skip Linux sound validation tests until this adapter exists.【F:src/code/unix/README.Linux†L161-L177】
- Decide whether BSD/macOS-style Unix ports need equivalents of the current Linux/glibc compare/checksum and `gprof`-control helper paths before broadening non-Windows validation claims. The retained `q3monkeyid` marker detection is now reconstructed, but the external `spank.sh` checksuming script itself remains historical release tooling rather than a checked-in runtime dependency.【F:src/code/unix/unix_main.c†L102-L208】
