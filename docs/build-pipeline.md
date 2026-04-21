# Build Pipeline Migration Plan

## Current Quake III VM Toolchain

The existing repository retains the Quake III Arena virtual machine pipeline so that game logic, client, and UI modules can still be cross-compiled into QVM bytecode:

- The `src/lcc/` subtree packages the Quake-specific fork of the LCC compiler along with helper drivers (`q3lcc`, `q3rcc`, `q3cpp`). On Windows hosts it is built by `buildnt.sh`, which generates an `out` directory and drives `nmake` against `makefile.nt` to emit the toolchain binaries.【F:src/lcc/buildnt.sh†L1-L4】 The `makefile.nt` recipe invokes Microsoft `cl` in debug/`/MDd` mode to compile and link the individual compiler stages (`q3rcc`, `q3cpp`, `lcc`, etc.), then archives them into the deliverables consumed by the VM build scripts.【F:src/lcc/makefile.nt†L1-L118】
- The root engine `Construct` script still knows how to build these tools on demand. When a build requests `q3lcc` or `q3asm`, the script creates a `qvmtools/` staging directory, runs the appropriate `make` command inside `src/lcc/` or `src/q3asm/`, and copies the resulting executables back into `code/qvmtools/` for reuse by the per-module build scripts.【F:src/code/Construct†L260-L308】
- Each gameplay VM (game, cgame) is then compiled by thin shell/batch wrappers such as `src/code/game/game.sh`, which drive `q3lcc` in `-Wf-target=bytecode` mode across the module’s C sources before invoking `q3asm` to assemble the final `.qvm` payload.【F:src/code/game/game.sh†L1-L48】 The assembler itself lives under `src/q3asm/` and is built with a minimal GNU makefile that targets the host’s C compiler (`gcc`).【F:src/q3asm/Makefile†L1-L12】
- Shared support code for these tools is provided in `src/libs/` (for example `libs/cmdlib/` centralises logging, file IO, and allocation helpers that are linked into `q3asm`).【F:src/libs/cmdlib/cmdlib.cpp†L1-L158】 The q3asm readme confirms these files were copied from the engine’s common utilities for portability.【F:src/q3asm/README.Id†L1-L10】

This pipeline remains functional and should keep shipping alongside any new native-focused workflow to preserve bytecode compatibility for legacy mod builds and regression testing.

Additional background on the `code/qvmtools/` staging area—including the binaries copied there, the wrapper scripts that consume them, and platform-specific rebuild prerequisites—is collected in [`docs/qvmtools.md`](qvmtools.md).

## Native Quake Live Binary Observations

Binary Ninja HLIL exports and the curated tooling documentation already highlight that the shipped Quake Live gameplay DLLs were produced with Microsoft’s Visual Studio 2010 SP1 toolchain and link against the Visual C++ 2010 CRT pair (`MSVCR100`, `MSVCP100`).【F:docs/hlil_comparison.md†L8-L17】 This aligns with the `MinimumVisualStudioVersion = 10.0.40219.1` metadata embedded in the stock Visual Studio solution files, confirming the expectation of the `v100` compiler and linker stack for native targets.【F:src/code/quakelive.sln†L1-L4】

In practice this means that reproducing Quake Live style binaries requires:

- A 32-bit (Win32) build of the modules so the produced DLLs mirror the shipped `qagamex86.dll`, `cgamex86.dll`, and `uix86.dll` layouts documented in the reference material.【F:docs/hlil_comparison.md†L1-L17】【F:docs/reference-mapping.md†L19-L21】
- Access to the Visual Studio 2010 compiler, linker, and CRT import libraries (either via an actual VS2010 SP1 installation or the “v100 toolset” shipped with newer Visual Studio releases through the “Visual Studio 2010 Tools” components).
- CRT deployment that links dynamically against `MSVCR100.dll`/`MSVCP100.dll`, mirroring the imports seen in the reference binaries.

For a step-by-step walkthrough of the retargeting process (including the relevant `.vcxproj` files, `.def` exports, and verification commands), refer to [`docs/windows-native-pipeline.md`](windows-native-pipeline.md).

## Browser Overlay Runtime Requirements

Quake Live's streamlined menu flow now depends on the embedded browser bridge. Transitional builds must bundle the Awesomium runtime (or a compatible replacement) and expose it to the client so the UI VM can advertise the capability. The `ui_browserAwesomium` cvar gates the new `ui_menuFlow` toggle—if the browser layer is absent the VM automatically falls back to legacy menus and server-browser logic for stability.【F:src/code/ui/ui_main.c†L178-L214】【F:src/code/ui/ui_atoms.c†L329-L368】

The dedicated `UI Validation` workflow now also runs a unified parity gate after
the bundle build and headless panel validation. That gate is implemented in
`tests/test_ui_full_parity_gate.py`, writes
`artifacts/ui_validation/logs/ui_full_parity_gate.json`, and the workflow now
executes it in enforced release mode with `UI_FULL_PARITY_GATE_ENFORCE=1`, so
CI publishes one authoritative pass/fail summary across the current UI gap
register (`UI-G01`..`UI-G06`) instead of leaving reviewers to reconcile
multiple independent UI logs by hand. The final windowed runtime confirmation
evidence for the current parity milestone is tracked separately in
`artifacts/ui_validation/logs/ui_runtime_evidence_20260406.json`.

The dedicated `Renderer Validation` workflow now does the equivalent for the renderer stack. It runs the focused renderer tranche tests together with `tests/test_renderer_full_parity_gate.py`, which writes `artifacts/renderer_validation/logs/renderer_full_parity_gate.json` so the current renderer gap register (`RG-G01`..`RG-G09`) is machine-readable instead of living only in prose. The tracked windowed runtime evidence for the final renderer text-closure milestone now lives at the stable alias `artifacts/renderer_validation/logs/renderer_runtime_evidence_latest.json`; the probe only promotes that alias when a rerun remains sufficient, and the current alias was refreshed on 2026-04-21 from the clean `renderer_runtime_evidence_20260421.json` bundle. Contributors can refresh it locally with `tools/renderer/run_renderer_runtime_probe.ps1`.

The dedicated `Module Validation` workflow now does the same for the strict
retail game-module lane. It runs
`tests/test_platform_services.py` together with
`tests/test_game_module_retail_parity_gate.py`, which writes
`artifacts/module_validation/logs/retail_module_parity_gate.json` as the
current `GMR-P8` closure artifact across the combined module gap register first
unified in `GMR-P5` (`GMR-G01`, `GMR-G02`, `GMR-G05`). The tracked retail
runtime evidence used by that gate now lives at the stable alias
`artifacts/module_validation/logs/retail_module_runtime_evidence_latest.json`;
that alias is only promoted when a rerun remains sufficient. It currently
points at the refreshed bounded `GMR-P1` artifact
`retail_module_runtime_evidence_20260421.json`, because the 2026-04-21 rerun
recovered the current `map <name> ffa` path, proved retail module loads again,
and reduced the remaining live-map shortfall to the renderer-owned
`R_fonsErrorCallback` font-atlas saturation blocker outside module scope.
Contributors can refresh that runtime artifact locally with
`tools/modules/run_retail_module_runtime_probe.ps1`.

The dedicated `Client Validation` workflow now gives the native client host the
same machine-readable closure lane. It runs
`tests/test_client_full_parity_gate.py`, which writes
`artifacts/client_validation/logs/client_full_parity_gate.json` across the
current client gap register (`CL-G01`..`CL-G05`). The tracked runtime evidence
for that gate is
`artifacts/client_validation/logs/client_runtime_evidence_20260410.json`, and
contributors can refresh it locally with
`tools/client/run_client_runtime_probe.ps1`.

The dedicated `Qcommon Validation` workflow now does the same for the shared
engine-common layer. It runs the focused qcommon tranche together with
`tests/test_qcommon_full_parity_gate.py`, which writes
`artifacts/qcommon_validation/logs/qcommon_full_parity_gate.json` across the
current qcommon gap register (`QC-G01`..`QC-G05`). The focused tranche now
includes the collision-leaf probe in
`tests/test_qcommon_collision_leaf_parity.py` and the fallback-VM harness in
`tests/test_qcommon_vm_fallback_parity.py`, plus the recovered shared-helper
audit in `tests/test_qshared_retail_parity.py`, so the lane covers the
remaining strict source-confidence seams in addition to the older
cvar/filesystem/message checks. The tracked qcommon runtime bundle is now
`artifacts/qcommon_validation/logs/qcommon_runtime_evidence_20260410.json`,
and contributors can refresh it locally with
`tools/qcommon/run_qcommon_runtime_probe.ps1`.

The dedicated `Server Validation` workflow now gives the engine `server` host
the same closure lane. It runs `tests/test_platform_services.py`,
`tests/test_fake_vacban.py`, and `tests/test_server_full_parity_gate.py`, which
write `artifacts/server_validation/logs/server_full_parity_gate.json` as the
machine-readable status artifact across the full audited server gap register
(`SV-G01`..`SV-G06`). The tracked dedicated runtime evidence for that final
server closure is
`artifacts/server_validation/logs/server_runtime_evidence_20260410.json`, and
contributors can refresh it locally with
`tools/server/run_server_runtime_probe.ps1`.

The dedicated `Engine Host Support Validation` workflow now does the same for
the remaining engine-owned host/support surface outside `qcommon`, `server`,
`client`, and `renderer`. It runs
`tests/test_platform_services.py`,
`tests/test_steamworks_harness.py`,
`tests/test_renderer_win32_host_glue_parity.py`,
`tests/test_bot_resource_loading.py`,
`tests/test_botlib_internal_parity.py`,
`tests/test_win32_clipboard_parity.py`,
`tests/test_win32_raw_input_parity.py`,
`tests/test_input_translation.py`, and
`tests/test_engine_host_support_full_parity_gate.py`, which write
`artifacts/engine_host_support_validation/logs/engine_host_support_full_parity_gate.json`
as the machine-readable gap-register artifact across `EH-G01`..`EH-G06`. The
tracked evidence bundle for that lane is
`artifacts/engine_host_support_validation/logs/engine_host_support_runtime_evidence_20260410.json`.
Because this lane was introduced by `EH-P6`, later extended by `EH-P4`, and
finally classified by `EH-P5` rather than by a fresh runtime owner, that
bundle is source-backed evidence for the closed Win32 clipboard, raw-input,
loading-window, input-translation, and botlib-internal proof seams rather than
a new live probe. The final `EH-P5` gate result treats the platform-service
compatibility backends and the Unix/null portability trees as documented
compatibility-only exclusions, so the host/support artifact can report
`overall_status: pass` without mislabeling those lanes as retail Windows
reconstructions.

`EH-P1` boundary metadata now rides in that same host/support artifact through
`scope_boundary` and `classification_summary`, so downstream ledgers can reuse
the same strict-retail versus compatibility split instead of re-describing it
in prose each time the host/support note is refreshed.

## Migration Strategy

The goal is to preserve the Quake III VM pipeline while layering in a native DLL build suitable for Quake Live parity. The following phased plan keeps the bytecode toolchain intact and introduces the new workflow in parallel:

1. **Document and encapsulate the existing QVM toolchain.**
   - Freeze the current LCC/q3asm outputs under `code/qvmtools/` and continue to drive them through the existing `Construct` helpers so mod builds remain unaffected.
   - Capture minimal host requirements (Perl, GNU make, Microsoft CL for the Windows variant) in repository docs so contributors can continue producing `.qvm` artefacts.

2. **Introduce a dedicated native build configuration.**
   - Add a CMake or MSBuild definition under `build/native/` (or extend `src/code/quakelive.sln`) that produces `qagamex86.dll`, `cgamex86.dll`, and `uix86.dll` with the `v100` toolset while leaving the existing VM projects untouched.【F:src/code/quakelive.sln†L1-L20】【F:src/code/ui/ui.vcxproj†L1-L63】
   - Configure each target for Win32, `/MD` runtime linkage, and export lists consistent with the legacy DLLs; the UI project currently links with `/MT` and must be switched to `/MD` to match retail imports.【F:src/code/game/game.vcxproj†L285-L350】【F:src/code/cgame/cgame.vcxproj†L171-L206】【F:src/code/ui/ui.vcxproj†L126-L207】
   - Ensure the configuration sets the same preprocessor symbols used by the VM build (`Q3_VM`, platform macros) so source compatibility is maintained during the transition.

3. **Share source and headers safely between pipelines.**
   - Refactor any VM-only glue (e.g., syscall stubs) into reusable headers so that both the bytecode and native projects consume the same implementation without divergence.
   - Keep VM-specific wrappers isolated (for example, continue invoking `q3asm` through the existing scripts) while the native build references the same `src/code/` tree directly.

4. **Stage UI DLLs alongside menu assets.**
   - When assembling distribution layouts, place the freshly built `uix86.dll` next to the staged UI scripts under `baseq3/ui/` so the native module and menu definitions ship together.【F:docs/reference-mapping.md†L14-L21】

5. **Automate toolchain selection and validation.**
   - Extend the top-level build instructions to include a Windows job that checks for the `v100` toolset and downloads/install instructions when missing.
   - Add CI targets or local scripts that can build both the `.qvm` set and the native DLLs, verifying symbol exports and CRT dependencies (e.g., via `dumpbin /imports`) against the Quake Live references. The initial guardrails for these checks are documented in [`docs/toolchain-ci.md`](toolchain-ci.md).

6. **Gradually transition runtime testing.**
   - Retain `.qvm` builds as the default test vehicle while the native DLL path is under construction, using them for logic regression tests.
   - Once the native modules reach feature parity, gate new development on running the same test suite against both bytecode and DLL outputs to ensure behaviour stays aligned.

By running the VM and native workflows side by side, the project can continue leveraging the deterministic QVM toolchain for compatibility checks while enabling contributors to move toward the Visual Studio 2010-style DLLs required to truly mirror Quake Live.

## Test Automation and CI Expectations

To support the gameplay testing strategy, CI must offer the following automation:

- **Dual-Target Build Matrix:** Configure workflows with a `target` axis (`qvm`, `dll`). The QVM leg invokes the existing `Construct` scripts, while the DLL leg drives MSBuild or CMake presets configured for the Visual Studio 2010 toolset.
- **Harness Bootstrapping:** Before running tests, stage the shared harness utilities from `tests/` (Python dependencies, data packs) and compile the native/QVM fixture runners. Package the compiled shims (`tests/bin/qvm/*`, `tests/bin/dll/*`) for reuse across suites.
- **Test Execution:** For each leg, run `python tests/run_all.py --target <target>` which fans out to the deterministic match, rules engine, client regression, weapon timing, and syscall verification suites. Failures must surface unified diff snippets plus a link to the archived artefacts.
- **Artefact Publication:** Upload JSON logs, baseline diffs, syscall traces, and weapon timing baselines to the CI job artefacts directory under `artifacts/tests/<suite>/<target>/latest/`. These provide reviewers with parity evidence without reproducing the run locally.
- **Status Badges:** Expose separate build badges (e.g., `Tests (QVM)`, `Tests (DLL)`) so contributors can quickly see which target failed.

### Expected Contributor Outputs

When contributors run the suites locally they should capture and attach the following to pull requests:

1. Summary table emitted by `tests/run_all.py` indicating pass/fail per suite for both targets.
2. Any updated baseline hashes committed alongside the change, with justification in the PR description.
3. Notes in `docs/behaviour-deltas.md` describing intentional divergences that caused baseline updates.
4. For syscall contract changes, an updated `tests/syscall_contract.expect` outlining the new interface surface.

This workflow ensures gameplay changes demonstrate target parity and codifies the artefacts maintainers require during reviews.
