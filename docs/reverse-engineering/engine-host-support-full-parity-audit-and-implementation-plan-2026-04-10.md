# `Remaining Engine Host/Support` Full Parity Audit And Closure Implementation Plan

Last updated: 2026-04-21

Scope: remaining engine-owned support layers outside `src/code/qcommon/*`, `src/code/server/*`, `src/code/client/*`, and `src/code/renderer/*`; primarily `src/common/platform/*`, `src/code/win32/*` host seams not already owned by the qcommon/client/renderer audits, `src/code/botlib/*`, `src/code/unix/*`, `src/code/null/*`, and `src/code/win32/awesomium_process.cpp` versus retail `quakelive_steam.exe` plus the committed `awesomium_process.exe` reference corpus.

Purpose: publish a strict retail-facing audit for the remaining engine host/support surface, separate the already-strong Win32 and Steamworks carries from deliberate compatibility layers and lightly bounded subsystems, and turn the confirmed residual debt into an execution-ordered closure plan.

## Audit Method And Evidence

Owning retail binaries:

- `assets/quakelive/quakelive_steam.exe`
- committed `awesomium_process.exe` Ghidra corpus for the helper executable

Canonical committed evidence used for this audit:

- Binary Ninja HLIL corpus:
  - `references/hlil/quakelive/quakelive_steam.exe/quakelive_steam.exe_hlil.txt`
  - `references/hlil/quakelive/quakelive_steam.exe/quakelive_steam.exe_hlil_split/*`
- Ghidra companion corpus:
  - `references/reverse-engineering/ghidra/quakelive_steam/metadata.txt`
  - `references/reverse-engineering/ghidra/quakelive_steam/imports.txt`
  - `references/reverse-engineering/ghidra/quakelive_steam/exports.txt`
  - `references/reverse-engineering/ghidra/quakelive_steam/functions.csv`
  - `references/reverse-engineering/ghidra/quakelive_steam/analysis_symbols.txt`
  - `references/reverse-engineering/ghidra/quakelive_steam/decompile_top_functions.c`
- Symbol and mapping support:
  - `references/analysis/quakelive_symbol_aliases.json`
  - `docs/reverse-engineering/quakelive_steam_mapping_round_61.md`
  - `docs/reverse-engineering/quakelive_steam_mapping_round_98.md`
  - `docs/reverse-engineering/quakelive_steam_mapping_round_99.md`
  - `docs/reverse-engineering/quakelive_steam_mapping_round_101.md`
  - `docs/reverse-engineering/quakelive_steam_mapping_round_109.md`
  - `docs/reverse-engineering/awesomium_process-mapping.md`
- Supplemental architecture notes:
  - `docs/architecture/input-retail-mapping.md`
  - `docs/launcher_awesomium_audit.md`
  - `docs/platform/authentication.md`
  - `docs/platform/retail-dependencies.md`
  - `docs/platform/toolchain-matrix.md`
- Writable source under audit:
  - `src/common/platform/platform_config.h`
  - `src/common/platform/platform_services.c`
  - `src/common/platform/platform_steamworks.c`
  - `src/common/platform/backends/platform_backend_open_steam.c`
  - `src/common/platform/backends/platform_backend_steamworks.c`
  - `src/code/win32/win_main.c`
  - `src/code/win32/win_syscon.c`
  - `src/code/win32/win_wndproc.c`
  - `src/code/win32/win_input.c`
  - `src/code/win32/win_shared.c`
  - `src/code/win32/awesomium_process.cpp`
  - `src/code/botlib/*`
  - `src/code/unix/*`
  - `src/code/null/*`
- Existing validation surface:
  - `tests/test_platform_services.py`
  - `tests/test_steamworks_harness.py`
  - `tests/test_renderer_win32_host_glue_parity.py`
  - `tests/test_input_translation.py`
  - `tests/test_bot_resource_loading.py`

Method:

1. Start with the owning Windows retail binary and the committed metadata/import/export inventories before interpreting any source carry as a parity closure.
2. Use promoted aliases and mapping rounds to bound exact Win32 host wrappers and startup owners before treating those seams as open.
3. Treat focused source-backed tests and native harnesses as strong secondary proof for the Steamworks wrapper and Win32 host glue.
4. Distinguish three classes of work instead of scoring them as one bucket:
   - strict retail Windows host behavior
   - deliberate compatibility layers required by current repo policy
   - non-retail Unix/null portability code
5. Separate observed facts from inference when the best evidence is retail imports plus current-source absence, especially in the raw-input lane.

## Committed Corpus Snapshot

Retail `quakelive_steam.exe` metadata still reports:

- function corpus: `5473`
- imports: `351`
- exports: `2`
- promoted analysis symbols: `4377`

Retail imports directly relevant to this remaining host/support scope include:

- `DINPUT8.DLL!DirectInput8Create`
- `KERNEL32.DLL!WideCharToMultiByte`
- `USER32.DLL!GetClipboardData`
- `USER32.DLL!GetRawInputData`
- `USER32.DLL!GetRawInputDeviceInfoA`
- `USER32.DLL!GetRawInputDeviceList`
- `USER32.DLL!RegisterRawInputDevices`

Observed Win32 host mapping anchors are materially stronger than the old top-level audit implied:

- mapping rounds `98` and `99` close the `win_main.c`, `win_syscon.c`, and `win_wndproc.c` console/bootstrap wrapper families around `Sys_Error`, `Sys_Quit`, `Sys_Print`, `Sys_Mkdir`, `Sys_Cwd`, `Sys_DefaultCDPath`, `Sys_ListFiles`, `Sys_LoadDll`, `Sys_QueEvent`, `Sys_GetEvent`, `Sys_CreateConsole`, `Sys_ShowConsole`, `Sys_CreateLoadingWindow`, `WIN_DisableAltTab`, `VID_AppActivate`, and `MapKey`
- mapping round `101` bounds the retail Unicode text-entry path tightly enough to prove that `Field_Paste` uses a Unicode clipboard helper adjacent to `Sys_GetClipboardData`
- mapping round `109` closes the retained `Sys_Init` anchor and bounds the larger startup/event-loop relationship

Observed helper-executable facts from `awesomium_process.exe`:

- committed Ghidra metadata reports `139` functions, `54` imports, and a single executable-owned entry body
- the executable-owned behavior reduces to `WinMain -> Awesomium::ChildProcessMain(hInstance)`

Interpretation:

- this remaining scope is no longer in a broad discovery phase
- the remaining debt is concentrated in a narrow Win32 input/clipboard tail, deliberate compatibility abstractions, botlib proof, and validation/governance work

## Scope Boundary And Scoring Rules

This audit intentionally excludes the four engine layers the user asked to leave out:

- `qcommon`
- `server`
- `client`
- `renderer`

It also does not rescore the module-layer trees:

- `game`
- `cgame`
- `ui`

Boundary notes:

1. `src/code/win32/win_glimp.c` and `src/code/win32/win_gamma.c` are treated as renderer-owned and stay under the renderer audit.
2. `src/code/win32/win_net.c` is treated as qcommon/server-owned and stays under the qcommon and server audits.
3. `src/code/win32/win_snd.c` is adjacent to the client sound runtime; this audit only references it as a low-risk carry and does not reopen the client sound closure lane.
4. `src/code/unix/*` and `src/code/null/*` are tracked as compatibility lanes, not as part of the strict retail Windows replacement target.

Strict score policy used below:

- the headline parity estimate tracks the remaining retail-facing Windows host/support work that still matters if the rebuilt engine is to replace retail `quakelive_steam.exe`
- Unix/null compatibility code is tracked explicitly, but it is not allowed to dominate the strict retail Windows score
- compatibility abstractions such as `Open Steam Adapter`, `Hybrid`, and build-disabled fallbacks are treated as deliberate divergences unless they leak into the strict-retail path

## EH-P1 Boundary Contract

The final host/support gate now carries explicit `EH-P1` boundary metadata in
addition to the gap register itself. That metadata records the scope boundary,
the compatibility-only surfaces, and the per-gap classifications so the
headline score can be interpreted without relying on prose alone.

Machine-readable `EH-P1` boundary metadata now published by
`tests/test_engine_host_support_full_parity_gate.py` includes:

- `scope_boundary`
- `boundary_formalisation`
- `classification_summary`

Interpretation:

- `EH-G03` and `EH-G05` remain visible as compatibility-only lanes, but they no longer masquerade as open strict-retail Windows parity debt
- `EH-G06` remains a validation/governance tranche, separate from the compatibility-only exclusions
- future ledger refreshes now have one machine-readable boundary contract to reuse instead of re-inferring the split from narrative text

## Validation Snapshot

Validation rerun for this audit on 2026-04-10:

1. `pytest tests/test_platform_services.py tests/test_steamworks_harness.py tests/test_renderer_win32_host_glue_parity.py tests/test_bot_resource_loading.py tests/test_botlib_internal_parity.py tests/test_win32_clipboard_parity.py tests/test_win32_raw_input_parity.py tests/test_input_translation.py tests/test_engine_host_support_full_parity_gate.py -q --tb=no`

Observed result:

- `123 passed, 1 skipped in 4.78s`

Interpretation:

- the Steamworks wrapper surface and the mapped Win32 host-glue lane already have strong low-cost validation
- input translation behavior is now covered by the same shared compiler-discovery helper used by the other Windows-friendly native harnesses
- the Win32 clipboard lane now also has dedicated focused coverage through `tests/test_win32_clipboard_parity.py`
- the botlib internal helper lane now also has deterministic AAS/reachability/goal-state proof through `tests/test_botlib_internal_parity.py`
- the combined remaining-engine host/support scope now has a dedicated machine-readable parity gate plus a tracked evidence bundle for the closed Win32 host lanes

## Current Verified State

The current remaining engine host/support surface is split between strongly recovered active-runtime owners, deliberate compatibility abstractions, and a narrower set of lightly bounded tails.

Observed source-backed strengths:

1. The Win32 console/bootstrap/system-wrapper lane is materially strong.
   - `win_main.c`, `win_syscon.c`, and `win_wndproc.c` now sit on a large exact-source-match alias base.
   - The retained loading-window wrappers exist in writable source.
   - The current host owns the crash-dump pipeline through `MiniDumpWriteDump` and the `QLR_DUMP_PATH` contract.
   - `Sys_GetClipboardData()` now prefers `CF_UNICODETEXT`, converts through retained `WideCharToMultiByte`-backed helpers, trims control characters in one shared place, and only falls back to `CF_TEXT` as a compatibility lane.
2. The Steamworks wrapper core is materially stronger than the old top-level audit implied.
   - `platform_steamworks.c` dynamically loads the Steam API library.
   - It owns callback bundles, auth ticket request/cancel/validate, overlay helpers, friends/avatar/resource helpers, lobby/UGC helpers, server bootstrap setters, and stats/session wrappers.
   - The wrapper surface is strongly exercised by `tests/test_platform_services.py` and `tests/test_steamworks_harness.py`.
3. The helper executable lane is effectively closed.
   - `src/code/win32/awesomium_process.cpp` mirrors the executable-owned `WinMain -> Awesomium::ChildProcessMain(hInstance)` body.
   - The remaining browser-runtime behavior belongs to `awesomium.dll`, not to the helper executable itself.
4. The downstream Unicode/CPI-aware input translation path already exists in writable source.
   - `docs/architecture/input-retail-mapping.md` matches the retained Win32 message-pump story.
   - the manual `clang` probe confirms `cl_input_translation.c` still produces the expected Unicode and CPI outputs.

Observed source-backed weaknesses:

1. `platform_services.c` and the open/hybrid auth backends are repo abstractions rather than retail reconstructions.
   - provider labels such as `Build-disabled (QL_BUILD_ONLINE_SERVICES=0)`, `Open Steam Adapter`, and `Hybrid` are not retail contracts
   - `platform_backend_steamworks.c` and `platform_backend_open_steam.c` currently decide outcomes from token-substring heuristics, not retail service behavior
2. Unix/null remain explicit compatibility ports, not retail-parity implementations.
   - `src/code/unix/unix_main.c` now restores `Sys_LowPhysicalMemory()` plus Linux/glibc `Sys_FunctionCmp()` / `Sys_FunctionCheckSum()` coverage, reconstructs `Sys_MonkeyShouldBeSpanked()` as a retained `q3monkeyid` release-marker probe, and exposes a bounded `gprof`-compatible profiling control path when the Unix engine is built with `QL_ENABLE_GPROF=1`
   - `src/code/null/*` now carries current executable/timer/path/network contract scaffolding, but it still keeps no-op client/webview/platform stubs that are useful for compatibility and irrelevant to the retail Windows target

## Refreshed Strict `Remaining Engine Host/Support` Parity Estimate

- Current strict `remaining engine host/support` estimate: **100%**
- Historical checkpoint before `EH-P4` completion: **92%**
- Historical checkpoint before `EH-P6` completion: **89%**
- Historical checkpoint before `EH-P3` completion: **83%**

This final uplift is still mostly governance rather than new runtime recovery:
the dedicated remaining-engine host/support parity gate, the tracked evidence
bundle, the compiler-agnostic input-translation harness, the later botlib
internal proof lane, and now the explicit compatibility-only classifications
mean the audited register no longer has any open strict-retail gap. The
platform-service abstractions plus the Unix/null lanes still exist, but they
are now bounded as documented compatibility-only divergences rather than left
as ambiguous parity debt.

Rationale:

1. The highest-traffic remaining Windows host seams are already much stronger than the old top-level “native launcher and platform host: low parity” bucket suggested.
   - Win32 bootstrap, console, file-list, event-queue, and error/quit wrappers are strongly bounded.
   - the Steamworks wrapper core is broad, source-backed, and test-backed.
   - the helper executable lane is effectively closed.
2. The former remaining losses are now explicitly classified instead of left open:
   - deliberate non-retail compatibility layers in `platform_services.c` are policy-gated, default-disabled, and excluded from the strict-retail score
   - Unix/null compatibility-port governance is now machine-visible and excluded from the strict-retail score
3. The highest-value remaining Win32 input exactness loss from the publication audit, raw-input ownership, is now closed without discarding the retained DirectInput and classic Win32 fallback lanes.
4. The remaining validation/governance gap is now also closed, and botlib is no longer only a bridge-level confidence story: the scope has a dedicated machine-readable gate, a tracked evidence bundle, Windows-friendly input harness coverage, and a deterministic botlib internal proof lane.
5. A strict `100%` claim is now defensible for this audited register specifically because the remaining tails are no longer counted as silent strict-retail owners: they are explicit compatibility-only exclusions in both the ledgers and the machine-readable gate.

Confidence:

- high for Win32 bootstrap wrappers, Steamworks wrapper core, and `awesomium_process.exe`
- medium-high for Win32 input exactness and botlib internals
- low relevance for Unix/null to the strict retail Windows target

## Subsystem Coverage Matrix

| Area | Current status | Writable files in scope | Strongest retail evidence | Audit conclusion |
| --- | --- | --- | --- | --- |
| Win32 bootstrap, console frontend, filesystem wrappers, event queue, and crash path | High parity | `win_main.c`, `win_syscon.c`, `win_wndproc.c`, `win_shared.c` | mapping rounds `98`, `99`, `109`; alias ledger; current crash-dump source | The classic Win32 host/bootstrap lane is strongly source-backed and should no longer be treated as a major unknown. |
| Win32 input capture and clipboard exactness | High parity | `win_input.c`, `win_main.c`, `win_wndproc.c` | retail imports for raw-input and `WideCharToMultiByte`; committed HLIL for `sub_4eab90`, `sub_4eb830`, `sub_4ebaa0`, `sub_4ebb20`, and `sub_4f1a95`; mapping rounds `99` and `101`; `docs/architecture/input-retail-mapping.md` | The Unicode clipboard and raw-input lanes are now source-backed and test-backed; the remaining open host debt has moved away from active Win32 text/input ownership. |
| Steamworks wrapper core | High parity | `platform_steamworks.c`, `platform_steamworks.h` | `tests/test_platform_services.py`; `tests/test_steamworks_harness.py`; retail import surface | The retained Steamworks wrapper family is broad, active, and strongly validated. |
| Platform service descriptor table and open/hybrid auth backends | Closed as compatibility-only policy lane | `platform_services.c`, `platform_config.h`, `backends/platform_backend_open_steam.c`, `backends/platform_backend_steamworks.c` | `docs/platform/authentication.md`; source inspection; `tests/test_platform_services.py` | This lane remains non-retail by design, but it is now explicitly policy-gated, default-disabled, and excluded from the strict-retail Windows score. |
| Helper executable `awesomium_process.exe` | High parity | `awesomium_process.cpp` | `docs/reverse-engineering/awesomium_process-mapping.md` | The executable-owned surface is effectively closed. |
| Botlib internal implementation | High parity | `src/code/botlib/*` | `docs/reverse-engineering/quakelive_steam_mapping_round_61.md`; `docs/reverse-engineering/botlib-internal-parity-audit-and-implementation-plan-2026-04-10.md`; `tests/test_botlib_internal_parity.py` | The bridge and representative internal helper lanes are now retail-backed and test-backed, with remaining map/game-specific tuning explicitly bounded outside this register. |
| Unix portability layer | Closed as compatibility-only policy lane | `src/code/unix/*` | `docs/platform/toolchain-matrix.md`; source inventory | Useful for compatibility, but now explicitly excluded from the strict-retail Windows score instead of being carried as open parity debt. |
| Null portability layer | Closed as compatibility-only policy lane | `src/code/null/*` | source inventory | Intentional no-op compatibility lane, explicitly bounded outside the retail target. |
| Unified validation and ledger surface for this combined scope | High parity | `tests/test_engine_host_support_full_parity_gate.py`, tracked artifacts under `artifacts/engine_host_support_validation/` | focused tests plus tracked evidence bundle and workflow wiring | The scope now has a dedicated machine-readable gate and tracked evidence bundle, and the final artifact reports `pass` because the remaining compatibility-only lanes are classified as documented exclusions rather than open debt. |

## What Already Looks Closed

This audit did not reopen the following remaining-host/support tranches:

- `Sys_Error`, `Sys_Quit`, `Sys_Print`, `Sys_Cwd`, `Sys_Mkdir`, `Sys_ListFiles`, `Sys_LoadDll`, `Sys_QueEvent`, and `Sys_GetEvent`
- the shared `Q3 WinConsole` frontend and the retained loading-window wrapper family
- `WIN_DisableAltTab`, `WIN_EnableAltTab`, `VID_AppActivate`, and `MapKey`
- the Win32 raw-input registration, `WM_INPUT` dispatch, retained bounded sample buffer, and `ListInputDevices` enumeration lane
- `Sys_Init` as the startup-side anchor
- the crash-dump pipeline and retained dump-path ownership in `win_main.c`
- the broad `platform_steamworks.c` wrapper family already covered by the current Steamworks tests
- the executable-owned `awesomium_process.exe` bootstrap surface
- the server-owned botlib import bridge in `sv_bot.c` documented by mapping round `61`

Observed fact:

- the remaining debt now sits below or beside those closed active-runtime owners, not inside them

Inference:

- the closure plan should focus on Win32 text/input exactness, compatibility-lane hygiene, botlib proof, and unified validation rather than reopening the already-strong bootstrap/Steamworks/helper-executable carries

## Gap Register

## EH-G01 - Win32 clipboard path remains ANSI while retail paste flow is Unicode

**Type:** Behavioral + host I/O  
**Priority:** P0  
**Status:** Closed on 2026-04-10 by `EH-P2`

Retail evidence anchors:

- `references/reverse-engineering/ghidra/quakelive_steam/imports.txt`
- `docs/reverse-engineering/quakelive_steam_mapping_round_99.md`
- `docs/reverse-engineering/quakelive_steam_mapping_round_101.md`

Observed retail facts:

1. Retail imports `WideCharToMultiByte` and `GetClipboardData`.
2. Mapping round `99` bounds `sub_4ECD80` as the ANSI clipboard-adjacent path and leaves `sub_4ECDF0` as a separate retail Unicode clipboard helper.
3. Mapping round `101` shows `Field_Paste` calling the retail Unicode helper and replaying its UTF-16 data through `WideCharToMultiByte`.

Observed current-source facts:

1. `src/code/win32/win_main.c` now implements retained Unicode and ANSI clipboard clone helpers, with `Sys_GetClipboardData()` preferring `CF_UNICODETEXT`.
2. The Win32 host now converts clipboard UTF-16 text to UTF-8 via shared `WideCharToMultiByte` helpers in `src/code/win32/win_clipboard_shared.h`.
3. Control-character trimming is now retained through `QLR_Win32ClipboardTrimText()` instead of the earlier `strtok( data, "\n\r\b" )` call.
4. `Field_Paste`, the UI VM bridge, and the browser clipboard-return path continue to consume `Sys_GetClipboardData()`, which now returns the Unicode-first UTF-8 result instead of the ANSI-only compatibility path.

Validation:

- `pytest tests/test_platform_services.py tests/test_win32_clipboard_parity.py -q --tb=no`
- observed result: `60 passed in 4.30s`

Conclusion:

- the strict Win32 Unicode clipboard gap is now closed at the host fetch seam while preserving the ANSI compatibility fallback for non-Unicode clipboard owners

## EH-G02 - Retail raw-input ownership is now source-backed in the Win32 host

**Type:** Behavioral + ownership confidence  
**Priority:** P0  
**Status:** Closed on 2026-04-10 by `EH-P3`

Retail evidence anchors:

- `references/reverse-engineering/ghidra/quakelive_steam/imports.txt`
- `docs/architecture/input-retail-mapping.md`

Observed retail facts:

1. Retail imports `GetRawInputData`, `GetRawInputDeviceInfoA`, `GetRawInputDeviceList`, and `RegisterRawInputDevices`.
2. The committed HLIL for `sub_4ebb20` registers a raw mouse device, sets `in_mouseMode` to `"win32(Raw)"`, and emits the retained `RAW MOUSE INIT FAIL!` fallback text.
3. The committed HLIL for `sub_4ebaa0`, `sub_4eb830`, `sub_4eab90`, and `sub_4f1a95` shows a bounded raw-sample queue, `ListInputDevices`, `WM_INPUT` / `GetRawInputData` handling, and raw button/wheel translation.
4. The retail input architecture note confirms the normal Win32 message-pump path and Unicode character delivery expectations.

Observed current-source facts:

1. `src/code/win32/win_input.c` now registers/unregisters raw input, drains a bounded raw-sample buffer, exposes the retained `in_mouseMode`, `in_debugMouse`, `in_nograb`, and `in_raw_useWindowHandle` cvars, and keeps the DirectInput and classic Win32 lanes as compatibility fallbacks.
2. `src/code/win32/win_wndproc.c` now dispatches `WM_INPUT` to `IN_RawInputEvent()` and suppresses duplicate legacy wheel/button events while raw input owns the active lane.
3. `src/code/win32/win_rawinput_shared.h` and `tests/win_raw_input_harness.c` retain shared helper coverage for registration shape, sample extraction, and button/wheel translation.
4. `tests/test_win32_raw_input_parity.py` now validates registration semantics, synthetic sample extraction, button translation, raw-input source ownership in `win_input.c`, and `WM_INPUT` dispatch in `win_wndproc.c`.

Validation:

- `pytest tests/test_win32_raw_input_parity.py tests/test_win32_clipboard_parity.py tests/test_platform_services.py tests/test_renderer_win32_host_glue_parity.py -q --tb=no`
- observed result: `72 passed in 3.04s`

Conclusion:

- the retail raw-input host lane is now source-backed and test-backed, and the remaining strict-retail host/support debt no longer hinges on unresolved Win32 input ownership

## EH-G03 - `platform_services.c` and the open/hybrid backends are deliberate non-retail compatibility abstractions

**Type:** Intentional divergence + architecture boundary  
**Priority:** P1  
**Status:** Closed on 2026-04-10 by `EH-P5`

Retail evidence anchors:

- `docs/platform/authentication.md`
- current source in `platform_services.c`
- current source in `platform_backend_open_steam.c`
- current source in `platform_backend_steamworks.c`

Observed current-source facts:

1. `platform_services.c` publishes provider labels such as `Build-disabled (QL_BUILD_ONLINE_SERVICES=0)`, `Steamworks`, `Open Steam Adapter`, and `Hybrid`.
2. `platform_backend_steamworks.c` and `platform_backend_open_steam.c` currently decide auth outcomes from token-length and substring heuristics such as `retry`, `refresh`, `denied`, and `invalid`.
3. Repo policy intentionally keeps Quake Live-only online services behind `QL_BUILD_ONLINE_SERVICES`, default disabled.

Conclusion:

- this lane is not “missing retail behavior” in the same sense as the Unicode clipboard or raw-input gaps
- `EH-P5` now closes the boundary work by making the strict-retail versus compatibility-only split machine-visible in the gate, the platform docs, and the top-level ledgers

## EH-G04 - Botlib internals now have a dedicated retail-backed audit and parity gate

**Type:** Ownership confidence + validation  
**Priority:** P1  
**Status:** Closed on 2026-04-10 by `EH-P4`

Retail evidence anchors:

- `docs/reverse-engineering/quakelive_steam_mapping_round_61.md`
- `docs/reverse-engineering/botlib-internal-parity-audit-and-implementation-plan-2026-04-10.md`
- current source under `src/code/botlib/*`
- `tests/test_botlib_internal_parity.py`
- `tests/botlib_internal_harness.c`
- `tests/test_bot_resource_loading.py`

Observed facts:

1. The server-owned botlib bridge is strongly mapped and no longer ambiguous.
2. `EH-P4` now publishes a dedicated botlib internal audit that ties representative helper ownership back to mapping round `61`, retained retail strings, and the public export wiring in `be_interface.c`.
3. `tests/test_botlib_internal_parity.py` now proves representative AAS/sample, reachability, and goal-state helpers through `tests/botlib_internal_harness.c` instead of leaving botlib bounded only by the bridge/resource lane.
4. Historical `FIXME` markers still exist in the inherited botlib tree, but they are now treated as bounded implementation notes rather than as proof that the whole subsystem remains unaudited.

Conclusion:

- the internal botlib helper lane is now sufficiently bounded for this remaining host/support register
- the still-open remaining-engine host/support debt is now limited to the deliberate compatibility-only lanes

## EH-G05 - Unix and null ports are still over-broad compatibility lanes rather than explicitly bounded non-retail paths

**Type:** Compatibility governance  
**Priority:** P2  
**Status:** Closed on 2026-04-10 by `EH-P5`

Retail evidence anchors:

- `docs/platform/toolchain-matrix.md`
- `src/code/unix/unix_main.c`
- `src/code/null/*`

Observed current-source facts:

1. `src/code/unix/unix_main.c` still contains placeholder returns for several `Sys_*` helpers.
2. `src/code/null/null_client.c`, `src/code/null/null_snddma.c`, and `src/code/null/null_input.c` now expose the current browser/advert/input, silent-audio, and input-bootstrap compatibility entry points, but the null tree still remains a bounded compatibility host rather than a real client/webview/platform implementation.
3. These lanes are useful for compatibility and tooling, but they are not part of the retail Windows host target.

Conclusion:

- the closure work was never to force retail parity onto Unix/null immediately
- `EH-P5` now constrains these lanes clearly enough that they no longer pollute strict-retail scoring or validation claims

## EH-G06 - Dedicated remaining-engine host/support parity gate and evidence lane

**Type:** Validation + governance  
**Priority:** P1  
**Status:** Closed on 2026-04-10 by `EH-P6`

Observed facts:

1. Strong focused tests already exist for Steamworks, Win32 host glue, and some bot resource loading.
2. `tests/test_input_translation.py` now reuses the shared compiler-discovery helper in `tests/compiler_support.py`, so the lane no longer depends on `gcc` being present on the default Windows host.
3. `tests/test_engine_host_support_full_parity_gate.py` now writes `artifacts/engine_host_support_validation/logs/engine_host_support_full_parity_gate.json` as the machine-readable gap-register artifact for `EH-G01` through `EH-G06`.
4. `artifacts/engine_host_support_validation/logs/engine_host_support_runtime_evidence_20260410.json` now tracks the closed Win32 clipboard, raw-input, loading-window, input-translation, and later botlib-internal proof in one evidence bundle.
5. `.github/workflows/engine-host-support-validation.yml` now keeps the focused host/support validation lane CI-visible and uploads `artifacts/engine_host_support_validation/**`.

Conclusion:

- the remaining-engine host/support validation surface is now unified and machine-readable
- after `EH-P5`, the gate now reports the compatibility-only tranches as closed documented exclusions instead of leaving the overall scope `blocked`

## Closure Implementation Plan

## EH-P1 - Formalise strict-retail versus compatibility-lane boundaries [COMPLETED 2026-04-10]

Goal:

- make the repo’s remaining-engine host/support score and ledgers impossible to misread

Tasks:

1. Publish a machine-readable gap register for this scope, separate from client/server/qcommon/renderer gates.
2. Mark `platform_services.c`, open/hybrid auth backends, Unix, and null as compatibility lanes in the gate output rather than as silent strict-retail owners.
3. Cross-link the top-level ledgers so future work does not re-collapse this scope into the generic “launcher/platform host” bucket.

Status:

- Complete on 2026-04-10.

Completed work:

1. `EH-P6` published the machine-readable gap register for this scope, separate from the other engine and module gates.
2. `EH-P5` then classified `platform_services.c`, the open/hybrid auth backends, Unix, and null as compatibility-only lanes in both the gate output and the supporting platform docs.
3. `tests/test_engine_host_support_full_parity_gate.py` now also publishes explicit `EH-P1` boundary metadata through `scope_boundary`, `boundary_formalisation`, and `classification_summary` so the artifact itself carries the classification contract.
4. The top-level ledgers and pipeline notes now cross-link the same classification so this scope no longer collapses back into a generic launcher/platform-host bucket.

Expected effect:

- better scoring accuracy and less risk of overstating non-retail compatibility lanes as retail closures (complete)

## EH-P2 - Close the Win32 Unicode clipboard gap

Goal:

- mirror the retail clipboard-to-UTF-8 paste path closely enough that field editing no longer relies on the ANSI compatibility helper

Status:

- Complete on 2026-04-10.

Completed work:

1. Rechecked the `sub_4ECD80` / `sub_4ECDF0` split against the published mapping notes and kept the retail-shaped distinction between the Unicode owner and the ANSI compatibility path.
2. Added retained shared helpers in `src/code/win32/win_clipboard_shared.h` for UTF-16 sizing, UTF-16-to-UTF-8 conversion, and control-character trimming.
3. Reconstructed `Sys_GetClipboardData()` in `src/code/win32/win_main.c` so it now prefers `CF_UNICODETEXT`, converts through `WideCharToMultiByte`, and only falls back to `CF_TEXT` when Unicode clipboard data is unavailable.
4. Kept `Field_Paste`, the UI VM bridge, and the browser clipboard-return path routed through `Sys_GetClipboardData()`, which now exposes the Unicode-first UTF-8 result without widening the public caller surface.
5. Added `tests/win_clipboard_harness.c` and `tests/test_win32_clipboard_parity.py` as the focused regression lane for UTF-16 conversion, control-character trimming, Unicode-first source ownership, and preserved consumer routing.

Expected effect:

- closes `EH-G01` (complete)

## EH-P3 - Prove and close the raw-input host path

Goal:

- determine whether retail uses raw input only for enumeration, or for the actual mouse path, and then reconstruct the exact active owner

Status:

- Complete on 2026-04-10.

Completed work:

1. Performed a targeted committed-HLIL pass around the retail raw-input imports and their call sites, confirming that retail uses raw input as an active mouse owner rather than only as a device-enumeration side path.
2. Added the retained `RegisterRawInputDevices` / `GetRawInputData` / `WM_INPUT` ownership into the Win32 host path, including the bounded raw-sample queue, `ListInputDevices`, `in_mouseMode`, `in_debugMouse`, `in_nograb`, and `in_raw_useWindowHandle`.
3. Kept the current DirectInput and cursor-warp paths only as explicit fallback lanes when raw input is unavailable or intentionally not selected.
4. Added `tests/win_raw_input_harness.c` and `tests/test_win32_raw_input_parity.py` as the focused regression lane that proves raw-input registration/dispatch ownership on Windows.

Expected effect:

- closes `EH-G02` (complete)

## EH-P4 - Publish a dedicated botlib internal audit and proof surface [COMPLETED 2026-04-10]

Goal:

- move botlib from bridge-level confidence to subsystem-level confidence

Status:

- Complete on 2026-04-10.

Completed work:

1. Published `docs/reverse-engineering/botlib-internal-parity-audit-and-implementation-plan-2026-04-10.md`, which anchors the internal botlib tree back to mapping round `61`, retained retail strings, and the public export wiring in `be_interface.c`.
2. Added `tests/botlib_internal_harness.c` plus `tests/test_botlib_internal_parity.py`, giving the remaining-engine host/support lane deterministic proof for representative AAS presence bounds, projection math, reachability jump/fall helpers, team travel-flag translation, and goal-state lifecycle behavior.
3. Wired the new proof lane into `tests/test_engine_host_support_full_parity_gate.py`, the tracked evidence artifacts under `artifacts/engine_host_support_validation/`, and `.github/workflows/engine-host-support-validation.yml`.
4. Refreshed the host/support ledgers so `EH-G04` is now machine-readable as closed, the strict remaining-engine host/support estimate moves to **95%**, and the remaining blocked work is limited to the deliberate compatibility-only lanes.

Expected effect:

- closes `EH-G04` (complete)

## EH-P5 - Contain compatibility-only lanes explicitly [COMPLETED 2026-04-10]

Goal:

- keep Unix/null and open/hybrid service abstractions useful without letting them blur the strict Windows retail target

Status:

- Complete on 2026-04-10.

Completed work:

1. Added explicit compatibility-only ownership notes for Unix/null in `docs/platform/toolchain-matrix.md`, the dedicated validation note, and the remaining host/support audit.
2. Strengthened the platform-service proof lane by documenting the compatibility-only auth surface in `docs/platform/authentication.md` and by extending `tests/test_platform_services.py` so the runtime `QL_DISABLE_EXTERNAL_ECOSYSTEMS` policy path is regression-tested.
3. Reclassified `EH-G03` and `EH-G05` inside `tests/test_engine_host_support_full_parity_gate.py` so the final artifact now records those lanes as closed documented exclusions rather than leaving the overall host/support scope blocked.
4. Refreshed `AUDIT.md`, `IMPLEMENTATION_PLAN.md`, the build/windows-native pipeline notes, and the tracked host/support artifact so the strict remaining-engine host/support estimate now records **100%** for this audited register.

Expected effect:

- closes `EH-G03` and `EH-G05` as documented divergences instead of ambiguous parity debt (complete)

## EH-P6 - Add the final remaining-engine host/support parity gate [COMPLETED 2026-04-10]

Goal:

- give this remaining scope the same closure discipline already used by qcommon/client/renderer

Status:

- Complete on 2026-04-10.

Completed work:

1. Added `tests/test_engine_host_support_full_parity_gate.py`, which now writes `artifacts/engine_host_support_validation/logs/engine_host_support_full_parity_gate.json` as the machine-readable artifact across `EH-G01` through `EH-G06`.
2. Made `tests/test_input_translation.py` compiler-agnostic by reusing `tests/compiler_support.py` for compiler discovery, shared-library naming, and cross-platform shared-harness compilation.
3. Added the tracked evidence bundle at `artifacts/engine_host_support_validation/logs/engine_host_support_runtime_evidence_20260410.json`, which records the closed Win32 clipboard, raw-input, loading-window, and input-translation proof without requiring a fresh live runtime probe.
4. Added `.github/workflows/engine-host-support-validation.yml` plus the dedicated validation note at `docs/reverse-engineering/engine-host-support-validation-and-runtime-evidence-2026-04-10.md`.
5. Refreshed `AUDIT.md`, `IMPLEMENTATION_PLAN.md`, this document, and the pipeline notes so `EH-P6` is recorded complete and `EH-G06` is recorded closed.

Expected effect:

- closes `EH-G06` (complete)

## Recommended Execution Order

No remaining open execution phases remain in this audited register.

Reasoning:

- the validation/governance lane and the botlib internal proof lane are both in place
- the compatibility-only platform-service plus Unix/null lanes are now explicitly bounded and machine-visible
- no remaining-engine host/support gap remains open after `EH-P5`

## Bottom Line

The remaining engine host/support surface is materially stronger than the old
top-level audit implied. The Win32 bootstrap wrappers, the Steamworks wrapper
core, the helper executable lane, the Unicode clipboard path, the raw-input
host path, the botlib internal helper lane, and the final validation/gate lane
are now all in solid shape. The deliberate compatibility-only lanes are still
present, but they are now explicitly bounded as non-retail exclusions instead
of carrying open parity debt.

That means this audited remaining engine host/support register is now closed.
