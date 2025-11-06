# Native Prototype Shim Notes

## Overview
The native prototypes for the Quake Live client and gameplay frame loops now
live under `src-re/prototypes/`. They are thin C99 translations of the annotated
reverse-engineering notes and mirror the original VM entry point signatures
(`CL_Frame` and `G_RunFrame`). Both functions rely on bindable context
structures instead of the engine’s globals so that unit tests or harnesses can
inject deterministic state when exercising the routines.

## Logging shim
A reusable shim (`src-re/prototypes/common/native_shim.c`) writes structured
trace lines to `logs/re/native-shim.log`. The helper truncates the log on first
use, ensures the directory exists, and exposes `qlr_native_shim_logf`/`_syscall`
for routine-level and syscall-level instrumentation. Prototype bindings call the
logger around every outward hook invocation, allowing side-by-side comparison
with the QVM trace output without patching the engine binaries. Syscall
contracts are also mirrored to `logs/syscall_contract.log`, which shares the
same origin/module/argument schema as the engine-side
`SyscallContract_LogEvent` helper. Run `python
tools/tests/validate_syscall_contract.py` to compare the shim output against the
baseline in `tests/expectations/syscall_contract.expect` when auditing changes.

## Delta analysis
- **Client frame sequencing:** The prototype preserves the cddialog/menu
  bootstrap, AVI demo timing clamp, and autopause guard observed in the retail
  binary while swapping global references for the context struct. Hook calls are
  wrapped with logging so their sequencing remains visible when ported to
  native code.
- **Gameplay frame loop:** The translation maintains the negative `msec`
  clamp, think scheduling semantics, entity iteration, and warmup/intermission
  timers. Optional hook delegates (physics, event dispatch, client end-frame)
  let the harness substitute bespoke behavior while the default path mimics the
  annotated VM flow.

## Compatibility notes
- Call `QLR_ClientFrame_BindContext` / `QLR_Game_BindFrameContext` before
  invoking the exported frame functions. Passing `NULL` mirrors the VM’s
  early-out behavior and emits a diagnostic log line.
- The shim only records when hooks are present; leave function pointers unset
  to disable segments of the loop during incremental porting.
- Use `qlr_native_shim_reset_log()` at the start of a capture window to clear
  the log and `qlr_native_shim_close()` when tearing down the harness to flush
  buffered output.
