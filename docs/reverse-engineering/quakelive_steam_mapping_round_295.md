# Quake Live Steam Mapping Round 295

Date: 2026-05-25

Scope: client run-loop state enum identity.

## Evidence

Primary retail signals:

- HLIL for `sub_4BC3E0` checks `data_1528ba0 == 1` for the disconnected
  menu path, which matches source `CA_DISCONNECTED`.
- The same `CL_Frame` body checks `data_1528ba0 s>= 4` before sending the
  userinfo reliable command, matching source `CA_CHALLENGING` and later states.
- The avidemo capture branch checks `data_1528ba0 == 8`, matching source
  `CA_ACTIVE`.
- Nearby retail input/demo paths use the same state singleton with
  `data_1528ba0 != 9` and other comparisons, matching source `CA_CINEMATIC`.
- The retained source enum in `src/code/game/q_shared.h` includes
  `CA_AUTHORIZING` and `CA_LOADING`, so compacting the reconstruction enum
  shifted every state after `CA_DISCONNECTED`.

Observed state ids:

- `CA_UNINITIALIZED == 0`
- `CA_DISCONNECTED == 1`
- `CA_AUTHORIZING == 2`
- `CA_CONNECTING == 3`
- `CA_CHALLENGING == 4`
- `CA_CONNECTED == 5`
- `CA_LOADING == 6`
- `CA_PRIMED == 7`
- `CA_ACTIVE == 8`
- `CA_CINEMATIC == 9`

## Source Reconstruction

The production source already had the retained enum values.  This round fixes
the reverse-engineering mirrors so their branch labels and trace harness state
ids no longer describe a compressed enum:

- `src-re/include/ql_types.h`
- `src-re/clean/include/qlr_client_frame.h`
- `tools/tests/re_trace_harness.py`
- `tests/expectations/re/native-shim.log`

The native trace context now starts the client in `state=8`, the retail active
state, instead of the stale compressed `state=5`.

## Guardrails

`tests/test_client_run_loop_mapping.py` now pins:

- the HLIL state comparisons for disconnected, challenging-or-later, and
  active paths;
- the full `QLR_CA_*` mirror enum including `AUTHORIZING` and `LOADING`;
- the clean mirror's active/cinematic ids; and
- this mapping note's state-id summary.

## Parity Movement

Before this round, the focused client run-loop lane was about `98%`
source-visible and `98%` mapped, but the reverse-engineering mirror enum still
compressed historical states and made active-frame harness logs claim
`state=5`.

After this round, the focused lane remains about `98%` source-visible and rises
to about `99%` mapped for the run-loop scaffolding.  Remaining deltas stay
bounded to exact naming/coverage for very small adjacent native helpers and
source-only compatibility refresh work.
