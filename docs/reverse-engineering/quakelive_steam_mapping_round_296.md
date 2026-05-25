# Quake Live Steam Mapping Round 296

Date: 2026-05-25

Scope: `CL_Frame` release-marker reliable-command mutation.

## Evidence

Primary retail signals:

- HLIL for `sub_4BC3E0` checks `sub_4EC640() != 0` while
  `data_1528cc0 == 0`, immediately after the avidemo fixed-step branch and
  before the frame timing fields are advanced.
- `data_1528cc0` is the retained `cls.framecount` field, incremented at the
  tail of `CL_Frame`, so the branch is one-shot on the first client frame.
- `sub_4EC640` is a six-byte helper returning `data_12d0084`; the retained
  source names this release-marker predicate `Sys_MonkeyShouldBeSpanked`.
- When the predicate passes, retail samples `rand() & 0x7fff`, compares the
  normalized value against `0.1`, and calls `sub_4B8250` when the random value
  is at least that threshold.
- The alias ledger maps `sub_4B8250 -> CL_ChangeReliableCommand`, and round
  102 already documented that helper as the retained reliable-command newline
  mutation.

Promoted names for this slice:

- `sub_4EC640 -> Sys_MonkeyShouldBeSpanked`
- `sub_4B8250 -> CL_ChangeReliableCommand`

## Source Reconstruction

`src/code/client/cl_main.c` now restores the retail first-frame branch:

- `Sys_MonkeyShouldBeSpanked()` gates the behavior.
- `cls.framecount == 0` keeps it one-shot.
- `random() >= 0.1f` mirrors the retail threshold.
- `CL_ChangeReliableCommand()` remains the existing source owner for the
  mutation.

The host shims now cover the new link surface:

- `src/code/win32/win_main.c` reconstructs the same `q3monkeyid` release-marker
  probe already used by the Unix helper.
- `src/code/null/null_main.c` returns `qfalse`, keeping null-host behavior
  inert.

The reverse-engineering mirrors now expose the branch explicitly:

- `src-re/prototypes/c_client/cl_frame.c`
- `src-re/annotated/c_client/cl_frame.c`
- `src-re/clean/client/frame.c`
- `src-re/include/ql_types.h`
- `src-re/clean/include/qlr_client_frame.h`

## Guardrails

`tests/test_client_run_loop_mapping.py` now pins:

- the HLIL order `sub_4EC640`, `sub_4B8250`, and pre-timing frame sample;
- the production source order before `cls.realFrametime`;
- Win32/null `Sys_MonkeyShouldBeSpanked` linkage; and
- the prototype hook names for the branch.

The native trace expectation now exercises this branch deterministically with
`monkeyShouldBeSpanked() == 1` and `randomFloat() == 0.50`, expecting
`changeReliableCommand()` before the timegraph hook.

## Parity Movement

Before this round, the focused client run-loop lane was about `98%`
source-visible and `99%` mapped in the scaffolding, but the first-frame
release-marker branch existed only as a mapped helper and was not wired into
`CL_Frame`.

After this round, the focused lane remains about `98%` source-visible and is
about `99%` mapped.  Remaining known deltas are tiny native helper naming
details and source-only compatibility refresh work outside the retail frame
spine.
