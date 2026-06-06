# Quake Live ZMQ/CZMQ Mapping Round 402

Date: 2026-06-06

Focus: recover the shared `socket_base_t` default virtual and interface
callback wiring that every retained libzmq socket family inherits.

## Retail Evidence

- Owning binary: `assets/quakelive/quakelive_steam.exe`.
- Canonical HLIL:
  `references/hlil/quakelive/quakelive_steam.exe/quakelive_steam.exe_hlil_split/quakelive_steam.exe_hlil_part01.txt`
  and
  `references/hlil/quakelive/quakelive_steam.exe/quakelive_steam.exe_hlil_split/quakelive_steam.exe_hlil_part06.txt`.
- Structured companion corpus:
  `references/reverse-engineering/ghidra/quakelive_steam/functions.csv`.
- Symbol/name support:
  `references/analysis/quakelive_symbol_aliases.json`.

Rounds 399 through 401 pinned the active REP/ROUTER/PUB families and the
retained PAIR/STREAM edges. This pass closes the common socket-base defaults
that those concrete socket families share through the primary `socket_base_t`
vtable and the `array_item_t<0>`, `i_poll_events`, and `i_pipe_events`
subobject vtables. Short label: socket_base_t default virtual/interface wiring.

## Alias Reconstruction

This pass added 17 aliases and re-pinned 4 existing aliases in
`references/analysis/quakelive_symbol_aliases.json`.

| Symbol | Alias | Confidence | Evidence |
| --- | --- | --- | --- |
| `sub_407700` | `zmq_socket_base_t_scalar_deleting_dtor` | High | Primary `socket_base_t` vtable destructor calls the complete destructor and conditionally deletes the object. |
| `sub_409860` | `zmq_socket_base_t_process_destroy` | High | Vtable slot 17 marks the socket destroyed flag at offset `+0x2ad`; `check_destroy` later consumes that flag. |
| `sub_409870` | `zmq_socket_base_t_xsetsockopt_default` | High | Default xsetsockopt slot stores `EINVAL` (`0x16`) in `errno` and returns `-1`. |
| `sub_409890` | `zmq_socket_base_t_xsend_recv_unsupported` | High | Default xsend/xrecv slots store `ENOTSUP` (`0x81`) in `errno` and return `-1`. |
| `sub_4098B0` | `zmq_socket_base_t_xread_activated_assert` | High | Default read-activation callback asserts false in `src/socket_base.cpp` at line `0x3ea`. |
| `sub_409900` | `zmq_socket_base_t_xwrite_activated_assert` | High | Default write-activation callback asserts false in `src/socket_base.cpp` at line `0x3ee`. |
| `sub_409950` | `zmq_socket_base_t_xhiccuped_assert` | High | Default hiccup callback asserts false in `src/socket_base.cpp` at line `0x3f3`. |
| `sub_4099A0` | `zmq_socket_base_t_i_poll_events_in_event` | High | Poll-event in callback pumps socket commands and immediately calls `check_destroy` on the owning socket. |
| `sub_4099C0` | `zmq_socket_base_t_i_poll_events_out_event_assert` | High | Poll-event out callback asserts false in `src/socket_base.cpp` at line `0x402`. |
| `sub_409A10` | `zmq_socket_base_t_i_poll_events_timer_event_assert` | High | Poll-event timer callback asserts false in `src/socket_base.cpp` at line `0x407`. |
| `sub_409AF0` | `zmq_socket_base_t_i_pipe_events_read_activated` | High | Pipe-event read activation adjusts from the `i_pipe_events` subobject and forwards to the primary vtable slot at `+0x60`. |
| `sub_409B10` | `zmq_socket_base_t_i_pipe_events_write_activated` | High | Pipe-event write activation adjusts from the `i_pipe_events` subobject and forwards to the primary vtable slot at `+0x64`. |
| `sub_409B30` | `zmq_socket_base_t_i_pipe_events_hiccuped` | High | Pipe-event hiccup forwards to primary vtable slot `+0x68` unless the inbound pipe is already in the special attached state, where it terminates the pipe. |
| `sub_409B60` | `zmq_socket_base_t_i_pipe_events_pipe_terminated` | High | Pipe termination forwards to the concrete socket callback, removes the matching pending-connection node, updates the pipe-vector tail, and decrements termination acks. |
| `sub_40B450` | `zmq_socket_base_t_array_item_scalar_deleting_dtor` | High | Array-item subobject destructor thunk tail-calls the socket-base scalar deleting destructor with a `-0x278` adjustment. |
| `sub_40B460` | `zmq_socket_base_t_i_poll_events_scalar_deleting_dtor` | High | Poll-events subobject destructor thunk tail-calls the socket-base scalar deleting destructor with a `-0x280` adjustment. |
| `sub_40B470` | `zmq_socket_base_t_i_pipe_events_scalar_deleting_dtor` | High | Pipe-events subobject destructor thunk tail-calls the socket-base scalar deleting destructor with a `-0x284` adjustment. |
| `sub_407790` | `zmq_socket_base_t_dtor` | Existing | Re-pinned as the complete destructor target reached by the scalar deleting destructor and all three subobject destructor thunks. |
| `sub_409510` | `zmq_socket_base_t_process_commands` | Existing | Re-pinned as the mailbox command pump called by the socket-base poll in-event callback. |
| `sub_409A60` | `zmq_socket_base_t_check_destroy` | Existing | Re-pinned as the destroyed-flag consumer called after command pumping. |
| `sub_409F20` | `std_tree_erase_zmq_pending_connection_node_iter` | Existing | Re-pinned as the pending-connection erase helper called from pipe-terminated cleanup. |

## Observed Facts

- The primary `socket_base_t` vtable has default slot coverage for destruction,
  process-destroy, xsetsockopt, xsend, xrecv, and pipe activation callbacks.
  Concrete socket vtables override only the callbacks they need.
- `process_destroy` is a tiny state transition: it sets the destroyed byte at
  object offset `+0x2ad`.
- The default xsetsockopt callback is unsupported-by-option and returns
  `EINVAL`; the default xsend and xrecv callbacks return `ENOTSUP`.
- Default xread-activated, xwrite-activated, xhiccuped, poll out-event, and
  poll timer-event callbacks are assert-false thunks tied to
  `src/socket_base.cpp`.
- The `i_poll_events` in-event callback bridges the poller back into the socket
  command pump, then calls `check_destroy`. If the destroyed flag was set, the
  socket removes its poll fd, asks the context to destroy the socket, signals
  the destination mailbox when needed, and finally invokes the scalar deleting
  destructor through the socket vtable.
- The `i_pipe_events` callbacks are subobject-adjusting bridges. Read and write
  activation forward to primary vtable slots; hiccup forwards unless the pipe
  is in the special attached state; termination forwards to the concrete socket
  xterminated callback first.
- The pipe-terminated path then removes any pending-connection node matching
  the terminated pipe, compacts the adjacent pipe-vector tail, and, if the
  owner is terminating, decrements term acks before calling the own_t
  termination-progress helper. The `term_acks > 0` assertion is sourced from
  `src/own.cpp`. This is the shared pending-connection cleanup path for socket
  pipes that die during or around connection setup.

## Source Reconstruction

This is static/source-shape reconstruction only. The recovered shared defaults
give the following source-level model:

```c
// conceptual reconstruction, not checked-in engine C source
void socket_base_t::process_destroy()
{
	destroyed = true;
}

int socket_base_t::xsetsockopt(int option, const void *value, size_t size)
{
	errno = EINVAL;
	return -1;
}

int socket_base_t::xsend(msg_t *msg)
{
	errno = ENOTSUP;
	return -1;
}

int socket_base_t::xrecv(msg_t *msg)
{
	errno = ENOTSUP;
	return -1;
}

void socket_base_t::in_event()
{
	process_commands(0, false);
	check_destroy();
}

void socket_base_t::pipe_terminated(pipe_t *pipe)
{
	xterminated(pipe);
	pending_connections.erase(pipe);
	erase_pipe_from_pipe_vector(pipe);

	if (terminating) {
		assert(term_acks > 0);
		--term_acks;
		check_term_acks();
	}
}
```

## Inference Boundary

This pass does not rename the local vector-compaction helpers embedded in
`sub_409B60`, nor does it split the red-black-tree traversal around the
pending-connection erase helper. The only container helper re-pinned here is
the already promoted `std_tree_erase_zmq_pending_connection_node_iter` because
the pipe-terminated caller supplies a clear pending-connection owner context.

## Verification

Local verification for this pass:

- `Get-Content -Raw references/analysis/quakelive_symbol_aliases.json | ConvertFrom-Json | Out-Null`
- `python -m pytest -q tests/test_platform_services.py::test_zmq_socket_base_default_callbacks_round_402_aliases_are_pinned`
- `python -m pytest -q tests/test_platform_services.py -k zmq`

## Parity Estimate

- Focused `socket_base_t` default virtual/interface wiring:
  **before 54% -> after 91%**.
- ZMQ-related source reconstruction confidence, including retained publication,
  RCON, socket-family, and shared socket-base lifecycle evidence:
  **before 90.7% -> after 90.9%**.
- Overall Quake Live source parity:
  **before 55.65% -> after 55.66%**.
