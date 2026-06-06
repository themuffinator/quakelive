# Quake Live ZMQ/CZMQ Mapping Round 398

Date: 2026-06-06

Focus: recover the retained libzmq REQ socket edge: `req_t` request/reply
state machine, `dealer_t` fair-queue/load-balancer base wiring, and the
`req_session_t` special session branch used by `session_base_t::create`.

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

Round 397 recovered `session_base_t` lifecycle and showed that socket type `3`
uses the `req_session_t` subclass path. This pass maps the companion socket
side for the same REQ branch, plus the `dealer_t` base class that provides the
fair queue and load balancer used by REQ.
Short label: REQ/dealer socket and req_session_t wiring.

## Alias Reconstruction

This pass added 25 aliases and re-pinned 1 existing alias in
`references/analysis/quakelive_symbol_aliases.json`.

| Symbol | Alias | Confidence | Evidence |
| --- | --- | --- | --- |
| `sub_413E10` | `zmq_req_t_ctor` | High | Socket factory case `3` allocates `0x3d8` bytes and calls this constructor; body chains into `dealer_t`, installs all REQ vtables, initializes request state, seeds the request id, and stores socket type `3`. |
| `sub_413E90` | `zmq_req_t_xsend` | High | REQ send rejects sends while waiting for a reply, optionally emits correlation and empty delimiter frames through the dealer load balancer, drains stale replies, then sends the user message. |
| `sub_414050` | `zmq_req_t_xrecv` | Existing | Existing round-135 alias re-pinned here; body rejects receives before a request is sent, optionally matches the correlation id, skips stale reply frames, and returns to send-ready state on final frames. |
| `sub_414290` | `zmq_req_t_xhas_in` | High | REQ has-in returns false until a reply is expected, then delegates to the dealer/fair-queue input probe. |
| `sub_4142B0` | `zmq_req_t_xhas_out` | High | REQ has-out returns false while a reply is expected, then delegates to the dealer/load-balancer output probe. |
| `sub_4142D0` | `zmq_req_t_xsetsockopt` | High | Handles REQ-specific option ids `0x34` and `0x35`, and the dealer probe-router option `0x33`, with boolean/non-negative validation. |
| `sub_414370` | `zmq_req_t_xterminated` | High | Clears the current reply pipe when it terminates, then removes the pipe from both dealer FQ and LB structures. |
| `sub_4143B0` | `zmq_req_t_recv_reply_from_fq` | High | Private helper receives from the dealer fair queue while skipping messages from the saved current pipe until the matching pipe is reached. |
| `sub_414410` | `zmq_req_session_t_ctor` | High | `session_base_t::create` REQ branch allocates `0x2c0` bytes and calls this constructor; body chains into `session_base_t`, installs three req-session vtables, and clears the extra field at `0x2b8`. |
| `sub_414460` | `zmq_req_session_t_scalar_deleting_dtor` | High | Req-session vtable destructor restores all three req-session vtables, calls `session_base_t` complete destructor, and conditionally deletes. |
| `sub_4144A0` | `zmq_req_session_t_reset` | High | Req-session-only virtual slot clears the extra field at `0x2b8`. |
| `sub_4144B0` | `zmq_req_session_t_i_pipe_events_scalar_deleting_dtor` | High | `i_pipe_events` req-session subobject destructor thunk tail-calls `sub_414460` with a `-0x280` this adjustment. |
| `sub_4144C0` | `zmq_dealer_t_array_item_scalar_deleting_dtor` | High | Dealer/REQ array-item subobject destructor thunk tail-calls the dealer scalar destructor with a `-0x278` this adjustment. |
| `sub_4144D0` | `zmq_dealer_t_i_poll_events_scalar_deleting_dtor` | High | Dealer/REQ poll-events subobject destructor thunk tail-calls the dealer scalar destructor with a `-0x280` this adjustment. |
| `sub_4144E0` | `zmq_req_session_t_io_object_scalar_deleting_dtor` | High | Req-session io-object subobject destructor thunk tail-calls `sub_414460` with a `-0x278` this adjustment. |
| `sub_414770` | `zmq_dealer_t_ctor` | High | Socket factory case `5` allocates `0x3c0` bytes and calls this constructor; body chains into `socket_base_t`, installs dealer vtables, initializes FQ/LB state, and stores socket type `5`. |
| `sub_414810` | `zmq_dealer_t_scalar_deleting_dtor` | High | Dealer vtable destructor restores dealer vtables, destroys the LB/FQ helpers, unwinds `socket_base_t`, and conditionally deletes. REQ reuses this base destructor because REQ adds no owned storage. |
| `sub_414870` | `zmq_dealer_t_xattach_pipe` | High | Pipe attach asserts `pipe_`, optionally sends the probe-router empty message, then attaches the pipe to both fair-queue and load-balancer structures. |
| `sub_4149B0` | `zmq_dealer_t_xsetsockopt` | High | Dealer option handler validates option id `0x33` and stores the probe-router flag. |
| `sub_414A00` | `zmq_dealer_t_xsend` | High | Thin send path delegates to the dealer load balancer. |
| `sub_414A20` | `zmq_dealer_t_xrecv` | High | Thin receive path delegates to the dealer fair queue. |
| `sub_414A40` | `zmq_dealer_t_xhas_in` | High | Thin has-in path delegates to the dealer fair queue. |
| `sub_414A50` | `zmq_dealer_t_xhas_out` | High | Thin has-out path delegates to the dealer load balancer. |
| `sub_414A60` | `zmq_dealer_t_xwrite_activated` | High | Pipe write activation reactivates the pipe in the dealer load balancer. |
| `sub_414A80` | `zmq_dealer_t_xterminated` | High | Pipe termination removes the pipe from both dealer FQ and LB structures. |
| `sub_414AB0` | `zmq_dealer_t_i_pipe_events_scalar_deleting_dtor` | High | Dealer/REQ pipe-events subobject destructor thunk tail-calls the dealer scalar destructor with a `-0x284` this adjustment. |

## Observed Facts

- `socket_base_t::create` case `3` allocates `0x3d8` bytes and constructs
  `req_t`; case `5` allocates `0x3c0` bytes and constructs `dealer_t`.
- `req_t` inherits the dealer destructor and pipe attach implementation but
  overrides option, send, receive, has-in, has-out, and terminated slots.
- `req_t::xsend` uses a two-byte empty delimiter frame and, when the correlate
  option is active, a four-byte request-id frame before the user message.
- `req_t::xrecv` refuses to receive before a request was sent, validates
  correlation when enabled, discards stale reply chunks from non-current pipes,
  and clears the waiting-for-reply state after the final reply frame.
- `dealer_t` owns the fair queue at `+0x380` and the load balancer at `+0x39c`;
  its send/recv/has methods are direct delegation into those helpers.
- `dealer_t::xattach_pipe` shares the probe-router empty-message behavior used
  by REQ and DEALER before attaching the pipe to both queue helpers.
- `req_session_t` is a thin `session_base_t` subclass: it adds one extra field at
  `+0x2b8`, clears it in the constructor, and exposes a reset virtual that also
  clears that field.

## Source Reconstruction

This is static/source-shape reconstruction only. The recovered wiring gives the
following source-level model:

```c
// conceptual reconstruction, not checked-in engine C source
int dealer_t::xsend(msg_t *msg)
{
	return lb.send(msg);
}

int dealer_t::xrecv(msg_t *msg)
{
	return fq.recv(msg, NULL);
}

void dealer_t::xattach_pipe(pipe_t *pipe)
{
	assert(pipe);

	if (probe_router)
		send_probe_router_message(pipe);

	fq.attach(pipe);
	lb.attach(pipe);
}

int req_t::xsend(msg_t *msg)
{
	if (receiving_reply) {
		if (!relaxed) {
			errno = EFSM;
			return -1;
		}
		terminate_current_reply_pipe_if_any();
		receiving_reply = false;
	}

	if (!message_begins) {
		if (correlate)
			lb.send(request_id_frame());
		lb.send(empty_delimiter_frame());
		message_begins = false;
		discard_stale_replies();
	}

	if (lb.send(msg) == 0 && !msg->more())
		receiving_reply = true;
	return 0;
}

int req_t::xrecv(msg_t *msg)
{
	if (!receiving_reply) {
		errno = EFSM;
		return -1;
	}

	do {
		recv_reply_from_fq(msg);
		if (correlate)
			match_request_id_or_skip_old_reply(msg);
		skip_delimiter_frames_until_body(msg);
	} while (stale_reply);

	if (!msg->more())
		receiving_reply = false;
	return 0;
}

void req_session_t::reset()
{
	req_state = 0;
}
```

## Inference Boundary

The option numbers are described by observed ids and by their upstream libzmq
roles, but this pass does not rename the numeric option constants in source.
The REP/router socket family starts immediately after this cluster and remains a
separate follow-up target.

## Verification

Local verification for this pass:

- `Get-Content -Raw references/analysis/quakelive_symbol_aliases.json | ConvertFrom-Json | Out-Null`
- `python -m pytest -q tests/test_platform_services.py::test_zmq_req_dealer_round_398_aliases_are_pinned`
- `python -m pytest -q tests/test_platform_services.py::test_zmq_req_dealer_round_398_aliases_are_pinned tests/test_platform_services.py::test_zmq_session_base_round_397_aliases_are_pinned tests/test_platform_services.py::test_zmq_plain_mechanism_round_396_aliases_are_pinned tests/test_platform_services.py::test_zmq_null_mechanism_round_395_aliases_are_pinned tests/test_platform_services.py::test_zmq_codec_round_394_aliases_are_pinned tests/test_platform_services.py::test_zmq_stream_engine_state_machine_round_393_aliases_are_pinned tests/test_platform_services.py::test_zmq_stream_engine_peer_round_392_aliases_are_pinned tests/test_platform_services.py::test_zmq_tcp_socket_and_endpoint_round_391_aliases_are_pinned tests/test_platform_services.py::test_zmq_tcp_listener_round_390_aliases_are_pinned tests/test_platform_services.py::test_zmq_tcp_connecter_round_379_aliases_are_pinned tests/test_platform_services.py::test_zmq_options_default_and_mask_vector_round_378_aliases_are_pinned tests/test_platform_services.py::test_zmq_poller_base_io_object_round_377_aliases_are_pinned tests/test_platform_services.py::test_zmq_public_api_aliases_and_round_365_evidence_are_pinned`
- `python -m pytest -q tests/test_platform_services.py::test_server_zmq_runtime_reconstructs_retail_publication_and_rcon_owners tests/test_server_full_parity_gate.py::test_server_full_parity_gate_writes_status_artifact`

## Parity Estimate

- Focused REQ/dealer socket and req-session wiring:
  **before 42% -> after 87%**.
- ZMQ-related source reconstruction confidence, including retained
  publication/RCON ownership, public wrappers, socket/message helpers,
  command-delivery support, queue backing-store evidence, object lifecycle
  ownership, event-loop timer/fd-watch wiring, option/default storage, TCP
  connecter reconnect/stream-engine handoff, TCP listener bind/accept handoff,
  shared TCP/IP helper wiring, stream-engine class-edge/peer-address helpers,
  stream-engine message-state callbacks, raw/v1/v2 codec wiring, NULL
  mechanism READY/ZAP metadata wiring, PLAIN mechanism dispatch/state wiring,
  session lifecycle/pipe/ZAP/engine wiring, and REQ/dealer socket plus
  req-session wiring:
  **before 89.4% -> after 89.7%**.
- Overall Quake Live source parity:
  **before 55.61% -> after 55.62%**.
