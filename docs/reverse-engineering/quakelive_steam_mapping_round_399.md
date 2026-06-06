# Quake Live ZMQ/CZMQ Mapping Round 399

Date: 2026-06-06

Focus: recover the retained libzmq REP/router socket-family wiring adjacent to
the REQ/dealer pass: REP's request/reply state flags, ROUTER's pipe attachment,
identity lookup, outpipe activation, multipart send/receive state, and the
ROUTER socket used by the retained RCON path.

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
- Source wiring check: `src/code/server/sv_zmq.c` constructs the RCON socket as
  `QL_ZMQ_ROUTER` (`6`), matching the retained libzmq factory branch pinned in
  this pass.

Round 398 finished the REQ/dealer branch. This pass follows the next two
factory cases: case `4` constructs REP as a router subclass and case `6`
constructs ROUTER directly.
Short label: REP/router socket-family wiring.

## Alias Reconstruction

This pass added 20 aliases and re-pinned 4 existing aliases in
`references/analysis/quakelive_symbol_aliases.json`.

| Symbol | Alias | Confidence | Evidence |
| --- | --- | --- | --- |
| `sub_4144F0` | `zmq_rep_t_ctor` | High | Socket factory case `4` allocates `0x420` bytes and calls this constructor, which chains into `router_t`, installs REP vtables, seeds the state word, and stores socket type `4`. |
| `sub_414540` | `zmq_rep_t_scalar_deleting_dtor` | High | REP vtable destructor restores REP vtables, calls the router complete destructor, and conditionally deletes. |
| `sub_414590` | `zmq_rep_t_xsend` | High | REP send rejects sends before a request has been received, delegates multipart output to `router_t::xsend`, and clears the reply-ready flag after the final frame. |
| `sub_4145E0` | `zmq_rep_t_xrecv` | High | REP receive rejects receives while a reply is pending, pulls through `router_t::xrecv`, echoes identity frames back through router send, and rolls back the current output pipe when the request body finishes. |
| `sub_414710` | `zmq_rep_t_xhas_in` | High | REP has-in only probes router input while not waiting to send a reply. |
| `sub_414730` | `zmq_rep_t_xhas_out` | High | REP has-out returns true only while the reply-ready state is set. |
| `sub_414740` | `zmq_rep_t_array_item_scalar_deleting_dtor` | High | REP array-item subobject destructor thunk tail-calls the REP scalar destructor with a `-0x278` adjustment. |
| `sub_414750` | `zmq_rep_t_i_poll_events_scalar_deleting_dtor` | High | REP poll-events subobject destructor thunk tail-calls the REP scalar destructor with a `-0x280` adjustment. |
| `sub_414760` | `zmq_rep_t_i_pipe_events_scalar_deleting_dtor` | High | REP pipe-events subobject destructor thunk tail-calls the REP scalar destructor with a `-0x284` adjustment. |
| `sub_414CB0` | `zmq_router_t_scalar_deleting_dtor` | High | ROUTER vtable destructor calls the complete router destructor and conditionally deletes. |
| `sub_414DA0` | `zmq_router_t_dtor` | High | Complete destructor asserts empty anonymous/outpipe maps, closes prefetched messages, destroys the identity/outpipe trees, and unwinds the socket base. |
| `sub_414F20` | `zmq_router_t_xattach_pipe` | High | Pipe attach asserts `pipe_`, optionally sends the probe-router message, identifies the peer, and either attaches to the fair queue or records an anonymous pipe. |
| `sub_415090` | `zmq_router_t_xsetsockopt` | High | Option handler accepts ids `0x21`, `0x29`, and `0x33`, mapping to mandatory/identity-handover/probe-router-style boolean fields. |
| `sub_415130` | `zmq_router_t_xterminated` | High | Termination removes pipes from anonymous and named outpipe maps, clears current output when needed, and removes the fair-queue pipe. |
| `sub_4152A0` | `zmq_router_t_xread_activated` | High | Read activation reactivates anonymous pipes directly or identifies named pipes before reattaching them to the fair queue. |
| `sub_415320` | `zmq_router_t_xwrite_activated` | High | Write activation locates the outpipe tree entry by pipe id and marks the corresponding outpipe active. |
| `sub_415A80` | `zmq_router_t_xhas_in` | High | Input probe returns true for pending prefetched identity/body state or fetches a new identity frame from the fair queue. |
| `sub_416AB0` | `zmq_router_t_array_item_scalar_deleting_dtor` | High | ROUTER array-item subobject destructor thunk tail-calls the router scalar destructor with a `-0x278` adjustment. |
| `sub_416AC0` | `zmq_router_t_i_poll_events_scalar_deleting_dtor` | High | ROUTER poll-events subobject destructor thunk tail-calls the router scalar destructor with a `-0x280` adjustment. |
| `sub_416AD0` | `zmq_router_t_i_pipe_events_scalar_deleting_dtor` | High | ROUTER pipe-events subobject destructor thunk tail-calls the router scalar destructor with a `-0x284` adjustment. |
| `sub_414AC0` | `zmq_router_t_ctor` | Existing | Re-pinned as the direct case-`6` factory target and REP base constructor; initializes fair queue, anonymous-pipe tree, outpipe tree, probe/mandatory flags, and socket type `6`. |
| `sub_415420` | `zmq_router_t_xsend` | Existing | Re-pinned as the ROUTER send vtable slot and REP output delegate; consumes identity frames, finds current outpipe, and sends multipart body frames. |
| `sub_415770` | `zmq_router_t_xrecv` | Existing | Re-pinned as the ROUTER receive vtable slot and REP input delegate; emits identity frames, body frames, and prefetched state. |
| `sub_415C30` | `zmq_router_t_identify_peer` | Existing | Re-pinned as the peer identity helper used from pipe attach and read activation; generates routing ids when needed and inserts outpipe map entries. |

## Observed Facts

- `socket_base_t::create` case `4` allocates REP (`0x420`) and calls
  `sub_4144F0`; case `6` allocates ROUTER (`0x418`) and calls `sub_414AC0`.
- REP inherits ROUTER's pipe attach, options, termination, read/write
  activation, and routing identity storage, but overrides send/receive and
  has-in/has-out to enforce the REP request/reply alternation.
- REP uses the flag pair at `+0x418/+0x419` to decide whether send or receive
  is legal. Its receive path forwards routing envelope frames back through
  `router_t::xsend` before exposing the request body.
- ROUTER owns two map-like trees: one for anonymous pipes and one for named
  outpipes. The destructor asserts both are empty before tearing them down.
- `router_t::xsend` first consumes an identity frame, looks up the matching
  outpipe, handles mandatory/probe behavior, and then sends the body frames
  through the current output pipe.
- `router_t::xrecv` uses the fair queue, filters command frames, emits an
  identity frame before body delivery, and keeps prefetched state while
  multipart messages are still being delivered.
- The retained server runtime builds its ZMQ RCON endpoint on `QL_ZMQ_ROUTER`,
  making this private libzmq branch the closest evidence for the socket type
  that backs `Zmq_PumpRcon`.

## Source Reconstruction

This is static/source-shape reconstruction only. The recovered socket family
gives the following source-level model:

```c
// conceptual reconstruction, not checked-in engine C source
int rep_t::xsend(msg_t *msg)
{
	if (!request_begins) {
		errno = EFSM;
		return -1;
	}

	int rc = router_t::xsend(msg);
	if (rc == 0 && !msg->more())
		request_begins = false;
	return rc;
}

int rep_t::xrecv(msg_t *msg)
{
	if (request_begins) {
		errno = EFSM;
		return -1;
	}

	while (receiving_envelope) {
		router_t::xrecv(msg);
		router_t::xsend(msg);
		if (!msg->size())
			receiving_envelope = false;
	}

	int rc = router_t::xrecv(msg);
	if (rc == 0 && !msg->more()) {
		current_out->rollback();
		current_out = NULL;
		request_begins = true;
	}
	return rc;
}

void router_t::xattach_pipe(pipe_t *pipe)
{
	assert(pipe);
	if (probe_router)
		pipe->write(empty_msg);

	if (identify_peer(pipe))
		fq.attach(pipe);
	else
		anonymous_pipes.insert(pipe);
}
```

## Inference Boundary

This pass does not rename the adjacent STL red-black-tree helper bodies beyond
the existing support aliases. Their behavior is cited only where ROUTER calls
them for anonymous-pipe and outpipe storage. The next socket-family pass should
handle PULL/PUSH and the PUB/SUB-derived XPUB/XSUB family separately rather
than overloading this REP/router round.

## Verification

Local verification for this pass:

- `Get-Content -Raw references/analysis/quakelive_symbol_aliases.json | ConvertFrom-Json | Out-Null`
- `python -m pytest -q tests/test_platform_services.py::test_zmq_rep_router_round_399_aliases_are_pinned`
- `python -m pytest -q tests/test_platform_services.py::test_zmq_rep_router_round_399_aliases_are_pinned tests/test_platform_services.py::test_zmq_req_dealer_round_398_aliases_are_pinned tests/test_platform_services.py::test_zmq_session_base_round_397_aliases_are_pinned tests/test_platform_services.py::test_zmq_plain_mechanism_round_396_aliases_are_pinned tests/test_platform_services.py::test_zmq_null_mechanism_round_395_aliases_are_pinned tests/test_platform_services.py::test_zmq_codec_round_394_aliases_are_pinned tests/test_platform_services.py::test_zmq_stream_engine_state_machine_round_393_aliases_are_pinned tests/test_platform_services.py::test_zmq_stream_engine_peer_round_392_aliases_are_pinned tests/test_platform_services.py::test_server_zmq_runtime_reconstructs_retail_publication_and_rcon_owners`

## Parity Estimate

- Focused REP/router socket-family wiring:
  **before 39% -> after 88%**.
- ZMQ-related source reconstruction confidence, including retained
  publication/RCON ownership, public wrappers, socket/message helpers,
  command-delivery support, queue backing-store evidence, object lifecycle
  ownership, event-loop timer/fd-watch wiring, option/default storage, TCP
  connecter reconnect/stream-engine handoff, TCP listener bind/accept handoff,
  shared TCP/IP helper wiring, stream-engine class-edge/peer-address helpers,
  stream-engine message-state callbacks, raw/v1/v2 codec wiring, NULL
  mechanism READY/ZAP metadata wiring, PLAIN mechanism dispatch/state wiring,
  session lifecycle/pipe/ZAP/engine wiring, REQ/dealer socket plus
  req-session wiring, and REP/router socket-family wiring:
  **before 89.7% -> after 90.0%**.
- Overall Quake Live source parity:
  **before 55.62% -> after 55.63%**.
