# Quake Live Steam Mapping Round 292

Date: 2026-05-25

Scope: client run-loop ownership and frame-adjacent browser/Steam/workshop
wiring.

## Evidence

Primary retail signals:

- `references/reverse-engineering/ghidra/quakelive_steam/functions.csv`
  contains the owning host rows:
  - `FUN_004cc6c0` size `1465` -> `Com_Frame`
  - `FUN_004bc3e0` size `674` -> `CL_Frame`
  - `FUN_004f2590` size `46` -> `QLWebCore_Update`
  - `FUN_00461d40` size `442` -> `SteamClient_Frame`
  - `FUN_004bc320` size `187` -> `CL_Workshop_Frame`
- HLIL for `sub_4CC6C0` shows the non-dedicated frame path running the second
  event loop, command-buffer execution, `sub_4F2590`, `sub_461D40`, and then
  `sub_4BC3E0`.  That places browser-core update and Steam callback pumping
  outside `CL_Frame`, immediately before the client frame owner.
- HLIL for `sub_4BC3E0` shows the client-frame body preserving the retained
  menu/cd gate, avidemo latch/rate handling, frame-time accumulation,
  userinfo/timeout handling, `sub_4BC320`, `sub_4B62A0`, `sub_4B9150`,
  `sub_4B07C0`, `sub_4BE3A0`, `sub_4DB680`, `sub_4B3510`, `sub_4B4800`, and
  the framecount increment.
- The alias ledger already backs the key owners:
  `sub_4CC6C0 -> Com_Frame`, `sub_4BC3E0 -> CL_Frame`,
  `sub_4F2590 -> QLWebCore_Update`, `sub_461D40 -> SteamClient_Frame`,
  `sub_4BC320 -> CL_Workshop_Frame`, `sub_4B62A0 -> CL_SendCmd`,
  `sub_4B9150 -> CL_CheckForResend`, `sub_4B07C0 -> CL_SetCGameTime`,
  `sub_4BE3A0 -> SCR_UpdateScreen`, `sub_4DB680 -> S_Update`,
  `sub_4B3510 -> SCR_RunCinematic`, and `sub_4B4800 -> Con_RunConsole`.

## Source Reconstruction

`src/code/qcommon/common.c` now owns the retail frame-adjacent service pumps:

- `CL_WebHost_Frame()` runs after the second `Com_EventLoop()`/`Cbuf_Execute()`
  pass.
- `SteamClient_Frame()` runs immediately after the browser host pump.
- `CL_Frame( msec )` remains the client frame owner and now starts after both
  host-level pumps, matching the retail `sub_4CC6C0` call order.

`src/code/client/cl_main.c` now exposes `SteamClient_Frame()` to the common
frame owner and leaves `CL_Frame()` focused on client-owned work:

- userinfo and timeout checks
- workshop/download completion
- user command send
- compatibility Steam server-browser refresh
- connect resend, cgame timing, screen, audio, cinematic, console, and
  framecount advancement

The source-only `CL_SteamBrowser_Frame()` remains in `CL_Frame()` because it is
a compatibility reconstruction over the existing source browser/status systems,
not the retail Steam callback pump at `sub_461D40`.

`src-re/prototypes/c_client/cl_frame.c`,
`src-re/annotated/c_client/cl_frame.c`, and the clean frame mirror now match
the retained client frame sequence instead of the older packet/prediction shim:

- packet dispatch stays with `Com_EventLoop()`/`CL_PacketEvent`
- pause handling stays inside `CL_SetCGameTime`
- workshop, sendcmd, browser-refresh, resend, timing, screen, sound,
  cinematic, console, and framecount wiring are explicit harness hooks
- avidemo latch, min/max capture windows, screenshot execution, and timegraph
  debug graph hooks are represented in the frame context

## Guardrails

Added `tests/test_client_run_loop_mapping.py` to pin:

- alias-ledger rows for the run-loop owners
- Ghidra function inventory rows for `Com_Frame`, `CL_Frame`,
  `QLWebCore_Update`, `SteamClient_Frame`, and `CL_Workshop_Frame`
- HLIL call order for the host frame and client frame bodies
- source call order in `common.c` and `cl_main.c`
- this mapping note's evidence summary

Updated `tests/expectations/re/native-shim.log` so the native trace harness
expects the reconstructed client-frame hook sequence:
`checkUserinfo`, `checkTimeout`, `workshopFrame`, `sendCmd`,
`steamBrowserFrame`, `checkForResend`, `setCGameTime`, `updateScreen`,
`soundUpdate`, `runCinematic`, `runConsole`, and framecount advancement.

Verification run:

- focused client run-loop/static parity group: `9 passed, 1 skipped`
- Linux-side native trace harness with `build/re/linux` shared objects:
  expectation matched
- `tools/tests/test_trace_harness.py` still fails under Windows Python because
  its generic launcher uses `select` on subprocess pipe handles
  (`WinError 10038`); Linux-side pytest was unavailable in this workspace

Updated existing platform/workshop/voice tests so the Steam callback pump is
validated at the `Com_Frame` seam while the workshop helper remains validated
inside `CL_Frame`.

## Parity Movement

Before this round, the focused client run-loop lane was about `92%`
source-visible: the main owners were mapped, but the source placed the
browser-core and Steam callback pumps inside `CL_Frame`, and the reverse
engineering shims still described obsolete packet/prediction work inside the
client frame.

After this round, the focused lane is about `97%` source-visible and `98%`
mapped.  The remaining delta is bounded to source-only compatibility work
(`CL_SteamBrowser_Frame`) and unresolved exact naming for small native
integrity/release-marker helpers adjacent to the frame body.
