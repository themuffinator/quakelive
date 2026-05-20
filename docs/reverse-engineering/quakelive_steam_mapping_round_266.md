# Quake Live Steam Host Mapping Round 266

## Scope

This pass tightened the `cg_main.c` print/error bridge around the display-context
callback table and local cgame trap wrappers.

The directly checked helpers were:

- `0x10020A90 -> Com_Printf`
- `0x10020AF0 -> Com_Error`
- `0x10020B50 -> CG_Error`
- `cg_main.c::CG_Printf`

## Evidence

- `references/hlil/quakelive/cgamex86.dll/cgamex86.dll_hlil.txt` shows
  `0x10020A90` formatting the varargs message into a stack buffer with
  `vsprintf`, then forwarding directly through the base syscall pointer
  `data_1074cccc`.
- The same HLIL file shows `0x10020AF0` formatting through `vsprintf`, then
  forwarding directly through `data_1074cccc + 4`, the error trap slot.
- `references/symbol-maps/cgame.json` records `Com_Printf`, `Com_Error`, and
  `CG_Error` as recovered helpers with the current source analogues.
- The committed display-context bootstrap assigns `cgDC.Error = &Com_Error` and
  `cgDC.Print = &Com_Printf`, so the direct-trap wrappers are the important
  callback contract rather than the chat-beep path in `CG_Printf`.

## Source Updates

- Added the required function headers above `CG_Printf`, `CG_Error`,
  `Com_Error`, and `Com_Printf`.
- Normalized the local `va_start`, `vsprintf`, and `va_end` call spacing in
  those four wrappers.
- Preserved behavior:
  - `CG_Printf` still keeps the existing cgame chat-beep side path.
  - `CG_Error` still forwards to `trap_Error`.
  - `Com_Printf` and `Com_Error` still match retail by forwarding directly to
    the print/error traps.

## Tests

- `tests/test_cgame_displaycontext_parity.py` now checks the source-side
  normalized varargs calls and validates the committed HLIL evidence for
  `0x10020A90` and `0x10020AF0` direct trap forwarding.

## Parity Estimate

- Before: print/error bridge source-compliance and evidence parity was about
  98%.
- After: about 98.5%.

This round was intentionally behavior-neutral.
