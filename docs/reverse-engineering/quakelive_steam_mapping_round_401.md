# Quake Live ZMQ/CZMQ Mapping Round 401

Date: 2026-06-06

Focus: recover the retained libzmq PAIR and STREAM socket-family wiring at the
two outer edges of `socket_base_t::create`.

## Retail Evidence

- Owning binary: `assets/quakelive/quakelive_steam.exe`.
- Canonical HLIL:
  `references/hlil/quakelive/quakelive_steam.exe/quakelive_steam.exe_hlil_split/quakelive_steam.exe_hlil_part01.txt`
  and
  `references/hlil/quakelive/quakelive_steam.exe/quakelive_steam.exe_hlil_split/quakelive_steam.exe_hlil_part06.txt`.
- Structured companion corpus:
  `references/reverse-engineering/ghidra/quakelive_steam/functions.csv` and
  `references/reverse-engineering/ghidra/quakelive_steam/analysis_symbols.txt`.
- Symbol/name support:
  `references/analysis/quakelive_symbol_aliases.json`.
- Source wiring context: `src/code/server/sv_zmq.c` currently uses the retained
  REP, PUB, and ROUTER service paths; PAIR and STREAM remain bundled libzmq
  socket families reachable through the same retail factory but not exposed as
  active reconstructed server service endpoints.

Round 400 pinned the publication family. This pass closes the factory's case
`0` and case `0xb`: PAIR as the single-peer bidirectional pipe socket, and
STREAM as the identity-framed raw TCP stream socket.
Short label: PAIR/STREAM socket-family wiring.

## Alias Reconstruction

This pass added 22 aliases and re-pinned 5 existing aliases in
`references/analysis/quakelive_symbol_aliases.json`.

| Symbol | Alias | Confidence | Evidence |
| --- | --- | --- | --- |
| `sub_4136F0` | `zmq_pair_t_ctor` | High | Socket factory case `0` allocates `0x388`, constructs socket base, installs PAIR vtables, clears the lone pipe pointer, and stores socket type `0`. |
| `sub_413740` | `zmq_pair_t_scalar_deleting_dtor` | High | PAIR vtable destructor calls the complete PAIR destructor and conditionally deletes. |
| `sub_413770` | `zmq_pair_t_dtor` | High | Complete destructor restores PAIR vtables, asserts the singleton pipe pointer is clear, and unwinds `socket_base_t`. |
| `sub_4137F0` | `zmq_pair_t_xattach_pipe` | High | PAIR attach asserts a non-null pipe, records it if no pipe is currently attached, and terminates extra pipes. |
| `sub_413860` | `zmq_pair_t_xterminated` | High | PAIR termination clears the singleton pipe pointer when the terminated pipe matches. |
| `sub_413880` | `zmq_pair_t_xread_write_activated_noop` | High | The PAIR vtable uses this empty callback for both read-activated and write-activated slots. |
| `sub_413890` | `zmq_pair_t_xsend` | High | PAIR send writes to the singleton pipe, flushes/reactivates on final frames, and returns `EAGAIN` when no writable pipe exists. |
| `sub_413910` | `zmq_pair_t_xrecv` | High | PAIR receive closes the destination message, reads from the singleton pipe, and writes an empty delimiter-style message plus `EAGAIN` on failure. |
| `sub_4139C0` | `zmq_pair_t_xhas_in` | High | PAIR has-in returns the attached pipe's read availability or false when detached. |
| `sub_4139E0` | `zmq_pair_t_xhas_out` | High | PAIR has-out probes the attached pipe's outbound state and high-water behavior, returning false when detached. |
| `sub_413A30` | `zmq_pair_t_array_item_scalar_deleting_dtor` | High | PAIR array-item subobject destructor thunk tail-calls the PAIR scalar destructor with a `-0x278` adjustment. |
| `sub_413A40` | `zmq_pair_t_i_poll_events_scalar_deleting_dtor` | High | PAIR poll-events subobject destructor thunk tail-calls the PAIR scalar destructor with a `-0x280` adjustment. |
| `sub_413A50` | `zmq_pair_t_i_pipe_events_scalar_deleting_dtor` | High | PAIR pipe-events subobject destructor thunk tail-calls the PAIR scalar destructor with a `-0x284` adjustment. |
| `sub_418B70` | `zmq_stream_t_ctor` | High | Socket factory case `0xb` allocates `0x400`, installs STREAM vtables, initializes fair-queue and outpipe-map state, seeds routing identity, and stores socket type `11`. |
| `sub_418CE0` | `zmq_stream_t_scalar_deleting_dtor` | High | STREAM vtable destructor calls the complete STREAM destructor and conditionally deletes. |
| `sub_418D10` | `zmq_stream_t_dtor` | High | Complete destructor asserts the outpipe map is empty, closes prefetched messages, destroys the outpipe tree, unwinds fair-queue state, and tears down socket base. |
| `sub_418E20` | `zmq_stream_t_xattach_pipe` | High | STREAM attach asserts `pipe_` from `src/stream.cpp` and attaches it to the fair queue at object offset `+0x380`. |
| `sub_418E90` | `zmq_stream_t_xterminated` | High | STREAM termination finds the pipe's identity entry, removes the outpipe-map node, removes the pipe from the fair queue, and clears current output when needed. |
| `sub_418FD0` | `zmq_stream_t_xwrite_activated` | High | STREAM write activation finds the outpipe by pipe pointer and marks its outpipe entry active, asserting it was inactive first. |
| `sub_419D60` | `zmq_stream_t_array_item_scalar_deleting_dtor` | High | STREAM array-item subobject destructor thunk tail-calls the STREAM scalar destructor with a `-0x278` adjustment. |
| `sub_419D70` | `zmq_stream_t_i_poll_events_scalar_deleting_dtor` | High | STREAM poll-events subobject destructor thunk tail-calls the STREAM scalar destructor with a `-0x280` adjustment. |
| `sub_419D80` | `zmq_stream_t_i_pipe_events_scalar_deleting_dtor` | High | STREAM pipe-events subobject destructor thunk tail-calls the STREAM scalar destructor with a `-0x284` adjustment. |
| `sub_416C10` | `zmq_xsub_t_xread_activated` | Existing | Re-pinned as the shared fair-queue read-activation callback also used by STREAM's vtable. |
| `sub_417780` | `empty_output_buffer` | Existing | Re-pinned as STREAM's always-output-ready vtable slot, matching the existing pure true helper label. |
| `sub_4190C0` | `zmq_stream_t_xsend` | Existing | Re-pinned as STREAM's identity/data send implementation. |
| `sub_4193B0` | `zmq_stream_t_xrecv` | Existing | Re-pinned as STREAM's staged identity/data receive implementation. |
| `sub_419640` | `zmq_stream_t_xhas_in` | Existing | Re-pinned as STREAM's prefetching input probe. |

## Observed Facts

- `socket_base_t::create` case `0` constructs PAIR and case `0xb` constructs
  STREAM. Both are retained in the retail factory even though the reconstructed
  server service path currently constructs only REP, PUB, and ROUTER sockets.
- PAIR owns exactly one pipe pointer at `+0x380`. Attach accepts the first pipe
  and terminates later pipes; termination clears the pointer only when the
  matching pipe terminates.
- PAIR uses normal pipe read/write helpers directly. Its activation callbacks
  are both empty because the single pipe is probed synchronously by has-in and
  has-out.
- STREAM owns fair-queue state, two prefetched messages, an outpipe map, a
  current output pipe, and generated routing identity fields. Its constructor
  seeds type `0xb` and the message flag bytes used for identity/body staging.
- STREAM receive exposes identity and body as separate message stages. If no
  identity is already staged, it fetches from the fair queue and caches the
  pipe identity before exposing the body.
- STREAM send consumes an identity frame first, resolves it through the outpipe
  map, then writes following data frames to the current output pipe. Empty data
  terminates the addressed pipe, matching STREAM's raw-connection semantics.

## Source Reconstruction

This is static/source-shape reconstruction only. The recovered socket families
give the following source-level model:

```c
// conceptual reconstruction, not checked-in engine C source
void pair_t::xattach_pipe(pipe_t *pipe)
{
	assert(pipe != NULL);
	if (!this->pipe)
		this->pipe = pipe;
	else
		pipe->terminate(false);
}

int pair_t::xsend(msg_t *msg)
{
	if (pipe && pipe->write(msg)) {
		if (!msg->more())
			pipe->flush();
		msg->init();
		return 0;
	}

	errno = EAGAIN;
	return -1;
}

int pair_t::xrecv(msg_t *msg)
{
	msg->close();
	if (pipe && pipe->read(msg))
		return 0;

	msg->init();
	errno = EAGAIN;
	return -1;
}

int stream_t::xsend(msg_t *msg)
{
	if (!current_out) {
		assert(msg->more());
		current_out = outpipes.find(identity(msg));
		if (!current_out) {
			errno = ECONNRESET;
			return -1;
		}
		return 0;
	}

	if (msg->size() == 0)
		current_out->terminate(false);
	else if (current_out->write(msg))
		current_out->flush();

	current_out = NULL;
	msg->init();
	return 0;
}

int stream_t::xrecv(msg_t *msg)
{
	if (!prefetched_identity) {
		pipe_t *pipe = NULL;
		if (fq.recv(&prefetched_msg, &pipe) != 0)
			return -1;
		prefetched_identity = identity_msg(pipe);
	}

	// Returns identity first, then prefetched data.
}
```

## Inference Boundary

This pass does not rename the lower-level red-black-tree traversal helpers
around `sub_419990..sub_419D00`. Their behavior is cited only as STREAM
outpipe-map support from the caller context. It also keeps the existing
`zmq_xsub_t_xread_activated` label for `sub_416C10` rather than introducing a
second alias for the same shared fair-queue callback.

## Verification

Local verification for this pass:

- `Get-Content -Raw references/analysis/quakelive_symbol_aliases.json | ConvertFrom-Json | Out-Null`
- `python -m pytest -q tests/test_platform_services.py::test_zmq_pair_stream_round_401_aliases_are_pinned`
- `python -m pytest -q tests/test_platform_services.py -k zmq`

## Parity Estimate

- Focused PAIR/STREAM socket-family wiring:
  **before 35% -> after 88%**.
- ZMQ-related source reconstruction confidence, including retained
  publication/RCON ownership, public wrappers, socket/message helpers,
  command-delivery support, queue backing-store evidence, object lifecycle
  ownership, event-loop timer/fd-watch wiring, option/default storage, TCP
  connecter reconnect/stream-engine handoff, TCP listener bind/accept handoff,
  shared TCP/IP helper wiring, stream-engine class-edge/peer-address helpers,
  stream-engine message-state callbacks, raw/v1/v2 codec wiring, NULL
  mechanism READY/ZAP metadata wiring, PLAIN mechanism dispatch/state wiring,
  session lifecycle/pipe/ZAP/engine wiring, REQ/dealer socket plus
  req-session wiring, REP/router socket-family wiring, PUB/SUB/PULL/PUSH plus
  XPUB/XSUB wiring, and PAIR/STREAM socket-family wiring:
  **before 90.4% -> after 90.7%**.
- Overall Quake Live source parity:
  **before 55.64% -> after 55.65%**.
