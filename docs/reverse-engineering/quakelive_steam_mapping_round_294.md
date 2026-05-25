# Quake Live Steam Mapping Round 294

Date: 2026-05-25

Scope: `CL_Frame` demo-freeze frame-delta ownership.

## Evidence

Primary retail signals:

- `references/reverse-engineering/ghidra/quakelive_steam/functions.csv`
  keeps the owner rows used in the previous run-loop round:
  `FUN_004bc3e0,004bc3e0,674` for `CL_Frame`.
- HLIL for `sub_4BC3E0` shows the frame delta in `esi_1`;
  `data_1528ccc = esi_1` captures the pre-freeze frame sample before applying
  the demo-freeze gate.
- The same HLIL checks `data_16177e0` and
  `*(data_1627c50 + 0x30)`, then writes `esi_1 = 0`.  Later it advances
  `data_1528cc8 += esi_1` and stores `data_1528cc4 = esi_1`.
- The cvar registration window maps `data_1627c50` to
  `Cvar_Get( "cl_freezeDemo", "0", CVAR_TEMP )`, and the existing
  `CL_SetCGameTime` reconstruction already uses
  `clc.demoplaying && cl_freezeDemo->integer` for the same demo-freeze mode.
- The timegraph call still consumes the pre-freeze value through
  `data_1528ccc * 0.25`, so retail preserves the visual/debug frame sample
  while freezing simulation/realtime advancement.

## Source Reconstruction

`src/code/client/cl_main.c` now mirrors that split:

- `cls.realFrametime = msec` captures the pre-freeze frame sample.
- `clc.demoplaying && cl_freezeDemo->integer` zeroes `msec` before
  `cls.frametime` and `cls.realtime` are advanced.
- `SCR_DebugGraph( cls.realFrametime * 0.25, 0 )` remains after the realtime
  update and still reports the original frame sample.

The native reconstruction mirrors now carry the same gate:

- `src-re/prototypes/c_client/cl_frame.c`
- `src-re/annotated/c_client/cl_frame.c`
- `src-re/clean/client/frame.c`

`src-re/clean/include/qlr_client_frame.h` now exposes `cl_freezeDemo` in the
clean cvar context so the clean mirror can represent the same frame-delta
split as the prototype and source mirrors.

## Guardrails

`tests/test_client_run_loop_mapping.py` now pins:

- the HLIL sequence where `data_1528ccc = esi_1` captures the pre-freeze frame
  sample before the `cl_freezeDemo` cvar gate;
- the source order of `cls.realFrametime`, demo-freeze zeroing,
  `cls.frametime`, `cls.realtime`, and `SCR_DebugGraph`; and
- the prototype shim's `clc.demoplaying && cl_freezeDemo` hook.

## Parity Movement

Before this round, the focused client run-loop lane was about `97%`
source-visible and `98%` mapped: the host/client ownership was correct, but
demo-freeze still lived only in `CL_SetCGameTime`, so `cls.realtime` advanced
while frozen demos were held.

After this round, the focused lane is about `98%` source-visible and `98%`
mapped.  Remaining known deltas stay bounded to source-only compatibility
refresh work and exact naming for tiny native release-marker helpers adjacent
to the frame body.
