# Quake Live ZMQ/CZMQ Mapping Round 408

Date: 2026-06-06

Focus: close the last deferred `ypipe_base_t<msg_t,256>` and
`ypipe_conflate_t<msg_t,256>` helper names from the retained libzmq message
pipe backing-store reconstruction.

## Retail Evidence

- Owning binary: `assets/quakelive/quakelive_steam.exe`.
- Canonical HLIL:
  `references/hlil/quakelive/quakelive_steam.exe/quakelive_steam.exe_hlil_split/quakelive_steam.exe_hlil_part01.txt`
  and vtable/RTTI evidence in
  `references/hlil/quakelive/quakelive_steam.exe/quakelive_steam.exe_hlil_split/quakelive_steam.exe_hlil_part06.txt`.
- Structured companion corpus:
  `references/reverse-engineering/ghidra/quakelive_steam/functions.csv`.
- Symbol/name support:
  `references/analysis/quakelive_symbol_aliases.json` and promoted
  `ypipe_conflate_t<class_zmq::msg_t,256>` symbols in
  `references/reverse-engineering/ghidra/quakelive_steam/analysis_symbols.txt`.

Round 403 recovered the message pipe queue bodies but intentionally left the
final conflating vtable callback unnamed because Binary Ninja rendered it as an
`operator new[]` entry. This pass pins that body from vtable position and
control flow, and names the adjacent non-deleting base destructor.

## Alias Reconstruction

This pass added 2 aliases to
`references/analysis/quakelive_symbol_aliases.json` and re-pinned the related
round-403 queue aliases.
It closes the deferred `ypipe_conflate_t<msg_t,256> helper names` slab from
the prior queue mapping round.

| Symbol | Alias | Confidence | Evidence |
| --- | --- | --- | --- |
| `sub_410FE0` | `zmq_ypipe_conflate_msg_t_probe` | High | The `ypipe_conflate_t<msg_t,256>` vtable's final callback slot points here. The body locks the conflating pipe critical section, calls the supplied probe callback against the stored front/back message slot, unlocks, and returns the boolean result. |
| `sub_411050` | `zmq_ypipe_base_msg_t_dtor` | High | Tiny non-deleting base destructor body restores the `ypipe_base_t<msg_t,256>` vtable. The scalar deleting base destructor remains the already pinned `sub_411400`. |

## Observed Facts

- The conflating message-pipe vtable is ordered as destructor, write, unwrite,
  flush, check-read, read, and probe. The first six function slots already
  point at round-403 aliases; the seventh slot is the Binary Ninja
  `operator new[]` rendering of `sub_410FE0`.
- `sub_410FE0` receives the conflating pipe object and a function pointer,
  enters the critical section at object offset `0x4c`, invokes the callback
  with the stored message slot at object offset `0x48`, leaves the critical
  section, and returns the callback's byte result.
- `sub_411050` is the non-deleting destructor body for the abstract
  `ypipe_base_t<msg_t,256>` subobject. The scalar-deleting vtable slot still
  points at `sub_411400`, matching MSVC's destructor split.
- The standard-library string helpers at `0x00411470..0x00411990` remain
  intentionally unmapped; they are reused formatting support, not queue-owned
  ZMQ source functions.

## Source Reconstruction

This is static/source-shape reconstruction only. The recovered probe path is:

```c
// conceptual reconstruction, not checked-in engine C source
bool ypipe_conflate_t_msg::probe(bool (*fn)(msg_t *))
{
	bool result;

	EnterCriticalSection(&sync);
	result = fn(front);
	LeaveCriticalSection(&sync);
	return result;
}
```

This further documents the retained C++ libzmq message-pipe backing store used
under the repo-facing public ZMQ API. No GPL-side source clone is needed for
these private templates.

## Inference Boundary

The `operator new[]` name is a decompiler artifact in this context; the alias
is grounded in vtable position, nearby callback naming, and the locked
message-slot probe body. No assertion is made about global C++ allocation
behavior.

## Verification

Local verification for this pass:

- `Get-Content -Raw references/analysis/quakelive_symbol_aliases.json | ConvertFrom-Json | Out-Null`
- `python -m pytest -q tests/test_platform_services.py::test_zmq_msg_pipe_queue_tail_round_408_aliases_are_pinned`
- `python -m pytest -q tests/test_platform_services.py -k zmq`

## Parity Estimate

- Focused ZMQ message pipe queue tail wiring:
  **before 70% -> after 94%**.
- ZMQ-related source reconstruction confidence, including retained socket
  families, session/engine wiring, pipe lifecycle, routing, subscription
  prefixes, TCP transport, endpoint object lifetime, and message queue backing
  stores:
  **before 92.1% -> after 92.2%**.
- Overall Quake Live source parity:
  **before 55.71% -> after 55.72%**.
