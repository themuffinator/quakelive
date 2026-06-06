# Quake Live ZMQ/CZMQ Mapping Round 409

Date: 2026-06-06

Focus: close the deferred `io_object_t` default event callback surface left by
Round 377.

## Retail Evidence

- Owning binary: `assets/quakelive/quakelive_steam.exe`.
- Canonical HLIL:
  `references/hlil/quakelive/quakelive_steam.exe/quakelive_steam.exe_hlil_split/quakelive_steam.exe_hlil_part01.txt`
  and vtable evidence in
  `references/hlil/quakelive/quakelive_steam.exe/quakelive_steam.exe_hlil_split/quakelive_steam.exe_hlil_part06.txt`.
- Structured companion corpus:
  `references/reverse-engineering/ghidra/quakelive_steam/functions.csv`.
- Symbol/name support:
  `references/analysis/quakelive_symbol_aliases.json`.

Round 377 named the poller-base timer tree and `io_object_t` fd-watch helpers
but intentionally left the assertion-only virtual callbacks unnamed. This pass
returns to that exact gap. The bodies are short `assert(false)` handlers in
`io_object.cpp`, and the vtable slots show how concrete owners override only
the event callbacks they actually consume.

## Alias Reconstruction

This pass added 3 aliases to
`references/analysis/quakelive_symbol_aliases.json` and re-pinned the related
Round 377 `io_object_t` helper names.

| Symbol | Alias | Confidence | Evidence |
| --- | --- | --- | --- |
| `sub_41E140` | `zmq_io_object_t_in_event_assert` | High | The first event callback after the `io_object_t`/`i_poll_events` destructor slot; the body asserts `false` at `io_object.cpp:0x5f`. Sessions and REQ sessions inherit it when they have no direct read-fd event. |
| `sub_41E190` | `zmq_io_object_t_out_event_assert` | High | The second event callback slot; the body asserts `false` at `io_object.cpp:0x64`. TCP listener and session vtables reuse it where write readiness is not meaningful. |
| `sub_41E1E0` | `zmq_io_object_t_timer_event_assert` | High | The third event callback slot; the body asserts `false` at `io_object.cpp:0x69`. TCP listener and stream-engine vtables reuse it when no timer callback is installed. |

## Observed Facts

- The base `io_object_t` vtable at `0x00550EB8` is destructor,
  `sub_41E140`, `sub_41E190`, and `sub_41E1E0`.
- `req_session_t` and `session_base_t` reuse the default `in_event` and
  `out_event` assertion callbacks, while overriding the timer callback with
  their session timer handler.
- `tcp_listener_t` overrides `in_event` with its accept path but keeps the
  default `out_event` and `timer_event` assertions.
- `stream_engine_t` overrides `in_event` and `out_event`, but keeps the default
  `timer_event` assertion.
- The nearby `io_object_t::plug`, `set_pollin`, `reset_pollin`, and
  `set_pollout` aliases from Round 377 remain the positive fd-watch helpers;
  this pass names only the fail-fast default virtual callbacks.

## Source Reconstruction

This is mapping/static reconstruction only. No GPL-side engine C source changed
in this pass. The recovered source shape is:

```cpp
void io_object_t::in_event()
{
	assert(false);
}

void io_object_t::out_event()
{
	assert(false);
}

void io_object_t::timer_event(int)
{
	assert(false);
}
```

These defaults explain why concrete owners selectively override only the
events they schedule into the select poller.

## Inference Boundary

The aliases are intentionally scoped to `io_object_t` default event callbacks.
This pass does not name adjacent STL/tree helpers, SEH catch fragments, or the
raw `select_t` fd-set helper at `0x0040C1B0`; those remain generic helper
territory unless a later pass can tie them to a stable owner contract.

## Verification

Local verification for this pass:

- `Get-Content -Raw references/analysis/quakelive_symbol_aliases.json | ConvertFrom-Json | Out-Null`
- `python -m pytest -q tests/test_platform_services.py::test_zmq_io_object_default_callbacks_round_409_aliases_are_pinned`
- `python -m pytest -q tests/test_platform_services.py -k zmq`

## Parity Estimate

- Focused ZMQ `io_object_t` default callback-surface mapping:
  **before 45% -> after 94%**.
- ZMQ-related source reconstruction confidence:
  **before 92.2% -> after 92.3%**.
- Overall Quake Live source parity:
  **before 55.72% -> after 55.73%**.
