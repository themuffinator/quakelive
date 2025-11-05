# Quake Live Build Recapture

This document captures the toolchain evidence embedded in the retail Quake Live
binaries, the containerized environments we assembled to mirror those
configurations, and the current status of the build reproduction effort.

## Captured binary metadata

The table below summarises the linker signatures, version resources, and PDB
breadcrumbs that were harvested with `tools/scripts/dump_toolchain_info.py`.

| Binary | Timestamp (UTC) | Linker | File version | PDB path | Linker flags |
| ------ | --------------- | ------ | ------------ | -------- | ------------ |
| `quakelive_steam.exe` | 2016-06-03 | `LINK 10.00` | `0.1.0.739` | `W:\quakelive_clean\quakelive_steam.pdb` | `/DYNAMICBASE /NXCOMPAT /TSAWARE` |
| `awesomium.dll` | 2014-03-28 | `LINK 10.00` | `1.7.4.2` | `C:\dev\chromium2\chromium\src\build\Release\awesomium.pdb` | `/DYNAMICBASE /NXCOMPAT` |
| `awesomium_process.exe` | 2014-03-28 | `LINK 10.00` | `1.7.4.1` | `C:\dev\chromium2\chromium\src\build\Release\awesomium_process.pdb` | `/DYNAMICBASE /NXCOMPAT /TSAWARE` |
| `libGLESv2.dll` | 2014-02-11 | `LINK 10.00` | `1.0.0.939` | `C:\dev\chromium2\chromium\src\build\Release\libGLESv2.pdb` | `/DYNAMICBASE /NXCOMPAT` |
| `libEGL.dll` | 2014-02-11 | `LINK 10.00` | `1.0.0.939` | `C:\dev\chromium2\chromium\src\build\Release\libEGL.pdb` | `/DYNAMICBASE /NXCOMPAT` |
| `avcodec-53.dll` | 2011-11-29 | `GNU ld 2.20` | *(no resource)* | *(missing)* | `/DYNAMICBASE /NXCOMPAT /NOSEH` |
| `avformat-53.dll` | 2011-11-29 | `GNU ld 2.20` | *(no resource)* | *(missing)* | `/DYNAMICBASE /NXCOMPAT /NOSEH` |
| `avutil-51.dll` | 2011-11-29 | `GNU ld 2.20` | *(no resource)* | *(missing)* | `/DYNAMICBASE /NXCOMPAT /NOSEH` |

Full JSON output, including CodeView GUIDs and DLL characteristics, lives at
`references/analysis/quakelive_toolchain_metadata.json` for scripted reuse.

Additional observations:

* `quakelive_steam.exe` carries a Rich header showing VC++ 2010 object
  contributions, confirming the MSVC10 lineage implied by the 10.00 linker
  version and `/DYNAMICBASE` profile. The embedded application manifest still
  references `Microsoft.VC80.CRT`, so a legacy CRT redistributable must be
  staged alongside the VS2010 toolset.
* The third-party Chromium-derived components (`awesomium*`, `libEGL.dll`,
  `libGLESv2.dll`) point to a Windows build host at `C:\dev\chromium2`, giving
  us the directory layout that upstream scripts expect.
* The FFmpeg 0.8-era DLLs were built with MinGW32 binutils 2.20 and stripped of
  PDB data, so symbol repro requires building our own debug variants.

## Containerized toolchains

Two container definitions have been added under `tools/containers/`:

* **`msvc-2010.Dockerfile`** (Windows container): provisions Visual Studio 2010
  Professional and the Windows 7.1 SDK on top of `mcr.microsoft.com/windows/servercore:ltsc2019`,
  exposing an x86 `vcvars32` shell that matches the 10.00 linker observed in the
  game executable and Chromium-derived helpers.
* **`mingw-ld220.Dockerfile`** (Linux container): builds GNU binutils 2.20 for
  the `i686-w64-mingw32` target so MinGW-based projects can link with the same
  vintage tools used for the bundled FFmpeg DLLs while reusing Debian’s modern
  GCC front-end.

Both Dockerfiles can be built with the standard `docker build -f <file> .`
workflow. The MSVC image requires a Windows host (or Windows container support)
and will download large Microsoft installers during the build; the MinGW image
builds entirely from open-source components on Linux.

## Reproduction status

1. **Visual C++ pipeline**
   * Build the Windows container: `docker build -f tools/containers/msvc-2010.Dockerfile -t quakelive/msvc10 .`
   * Launch the developer prompt: `docker run -it --rm quakelive/msvc10`.
   * Inside the shell, verify the linker version with `link /?` and confirm it
     reports 10.00 to match the retail binaries. Install the legacy VC80 CRT
     redistributable before attempting a full game build to satisfy the manifest
     dependency.

2. **Chromium/Awesomium components**
   * Reuse the MSVC container; the PDB paths show a monorepo rooted at
     `C:\dev\chromium2`. Recreate this layout inside the container and point the
     Awesomium build scripts at it. Vendor drops are versioned 1.7.4.x, so use
     the SDK matching those versions to avoid ABI drift.

3. **FFmpeg MinGW pipeline**
   * Build the Linux container: `docker build -f tools/containers/mingw-ld220.Dockerfile -t quakelive/mingw220 .`
   * Run the environment and ensure `/opt/toolchain/bin` precedes the Debian
     MinGW tools so `ld --version` yields 2.20.
   * Rebuild FFmpeg 0.8.x with the exact configuration flags used by Awesomium
     (still TODO—no command-line artefacts survived). Enable debug symbols to
     recover usable PDBs.

## Outstanding mismatches / follow-ups

* **CRT manifest skew** – Retail binaries request the VC80 CRT while linking
  with VC10; verify at build time that the legacy redistributable is installed,
  or adjust manifests if newer CRTs are acceptable.
* **Missing FFmpeg build recipes** – No linker command line or configure cache
  survived in the DLLs; reverse-engineer the compilation flags from the shipped
  binaries (e.g. by diffing exported symbols) before attempting a rebuild.
* **Unsigned PDB stubs** – All PDB references point to local developer paths and
  age 1; confirm whether symbol servers ever hosted official PDBs or if we must
  archive freshly generated ones during the recapture process.
