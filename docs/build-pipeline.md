# Build Pipeline Migration Plan

## Current Quake III VM Toolchain

The existing repository retains the Quake III Arena virtual machine pipeline so that game logic, client, and UI modules can still be cross-compiled into QVM bytecode:

- The `src/lcc/` subtree packages the Quake-specific fork of the LCC compiler along with helper drivers (`q3lcc`, `q3rcc`, `q3cpp`). On Windows hosts it is built by `buildnt.sh`, which generates an `out` directory and drives `nmake` against `makefile.nt` to emit the toolchain binaries.【F:src/lcc/buildnt.sh†L1-L4】 The `makefile.nt` recipe invokes Microsoft `cl` in debug/`/MDd` mode to compile and link the individual compiler stages (`q3rcc`, `q3cpp`, `lcc`, etc.), then archives them into the deliverables consumed by the VM build scripts.【F:src/lcc/makefile.nt†L1-L118】
- The root engine `Construct` script still knows how to build these tools on demand. When a build requests `q3lcc` or `q3asm`, the script creates a `qvmtools/` staging directory, runs the appropriate `make` command inside `src/lcc/` or `src/q3asm/`, and copies the resulting executables back into `code/qvmtools/` for reuse by the per-module build scripts.【F:src/code/Construct†L260-L308】
- Each VM (game, cgame, UI) is then compiled by thin shell/batch wrappers such as `src/code/game/game.sh`, which drive `q3lcc` in `-Wf-target=bytecode` mode across the module’s C sources before invoking `q3asm` to assemble the final `.qvm` payload.【F:src/code/game/game.sh†L1-L48】 The assembler itself lives under `src/q3asm/` and is built with a minimal GNU makefile that targets the host’s C compiler (`gcc`).【F:src/q3asm/Makefile†L1-L12】
- Shared support code for these tools is provided in `src/libs/` (for example `libs/cmdlib/` centralises logging, file IO, and allocation helpers that are linked into `q3asm`).【F:src/libs/cmdlib/cmdlib.cpp†L1-L158】 The q3asm readme confirms these files were copied from the engine’s common utilities for portability.【F:src/q3asm/README.Id†L1-L10】

This pipeline remains functional and should keep shipping alongside any new native-focused workflow to preserve bytecode compatibility for legacy mod builds and regression testing.

Additional background on the `code/qvmtools/` staging area—including the binaries copied there, the wrapper scripts that consume them, and platform-specific rebuild prerequisites—is collected in [`docs/qvmtools.md`](qvmtools.md).

## Native Quake Live Binary Observations

Binary Ninja HLIL exports and the curated tooling documentation already highlight that the shipped Quake Live gameplay DLLs were produced with Microsoft’s Visual Studio 2010 SP1 toolchain and link against the Visual C++ 2010 CRT pair (`MSVCR100`, `MSVCP100`).【F:docs/hlil_comparison.md†L8-L17】 This aligns with the `MinimumVisualStudioVersion = 10.0.40219.1` metadata embedded in the stock Visual Studio solution files, confirming the expectation of the `v100` compiler and linker stack for native targets.【F:src/code/quake3.sln†L1-L4】

In practice this means that reproducing Quake Live style binaries requires:

- A 32-bit (Win32) build of the modules so the produced DLLs mirror the shipped `qagamex86.dll` layout documented in the reference material.【F:docs/hlil_comparison.md†L1-L17】
- Access to the Visual Studio 2010 compiler, linker, and CRT import libraries (either via an actual VS2010 SP1 installation or the “v100 toolset” shipped with newer Visual Studio releases through the “Visual Studio 2010 Tools” components).
- CRT deployment that links dynamically against `MSVCR100.dll`/`MSVCP100.dll`, mirroring the imports seen in the reference binaries.

For a step-by-step walkthrough of the retargeting process (including the relevant `.vcxproj` files, `.def` exports, and verification commands), refer to [`docs/windows-native-pipeline.md`](windows-native-pipeline.md).

## Migration Strategy

The goal is to preserve the Quake III VM pipeline while layering in a native DLL build suitable for Quake Live parity. The following phased plan keeps the bytecode toolchain intact and introduces the new workflow in parallel:

1. **Document and encapsulate the existing QVM toolchain.**
   - Freeze the current LCC/q3asm outputs under `code/qvmtools/` and continue to drive them through the existing `Construct` helpers so mod builds remain unaffected.
   - Capture minimal host requirements (Perl, GNU make, Microsoft CL for the Windows variant) in repository docs so contributors can continue producing `.qvm` artefacts.

2. **Introduce a dedicated native build configuration.**
   - Add a CMake or MSBuild definition under `build/native/` (or extend `src/code/quake3.sln`) that produces `qagamex86.dll`, `cgamex86.dll`, and `uix86.dll` with the `v100` toolset while leaving the existing VM projects untouched.
   - Configure each target for Win32, `/MD` runtime linkage, and export lists consistent with the legacy DLLs.
   - Ensure the configuration sets the same preprocessor symbols used by the VM build (`Q3_VM`, platform macros) so source compatibility is maintained during the transition.

3. **Share source and headers safely between pipelines.**
   - Refactor any VM-only glue (e.g., syscall stubs) into reusable headers so that both the bytecode and native projects consume the same implementation without divergence.
   - Keep VM-specific wrappers isolated (for example, continue invoking `q3asm` through the existing scripts) while the native build references the same `src/code/` tree directly.

4. **Automate toolchain selection and validation.**
   - Extend the top-level build instructions to include a Windows job that checks for the `v100` toolset and downloads/install instructions when missing.
   - Add CI targets or local scripts that can build both the `.qvm` set and the native DLLs, verifying symbol exports and CRT dependencies (e.g., via `dumpbin /imports`) against the Quake Live references. The initial guardrails for these checks are documented in [`docs/toolchain-ci.md`](toolchain-ci.md).

5. **Gradually transition runtime testing.**
   - Retain `.qvm` builds as the default test vehicle while the native DLL path is under construction, using them for logic regression tests.
   - Once the native modules reach feature parity, gate new development on running the same test suite against both bytecode and DLL outputs to ensure behaviour stays aligned.

By running the VM and native workflows side by side, the project can continue leveraging the deterministic QVM toolchain for compatibility checks while enabling contributors to move toward the Visual Studio 2010-style DLLs required to truly mirror Quake Live.
