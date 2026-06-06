# Quake Live ZMQ/CZMQ Mapping Round 400

Date: 2026-06-06

Focus: recover the retained libzmq PUB/SUB/PULL/PUSH socket-family wiring and
the XPUB/XSUB base thunks that back the server stats publisher path.

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
- Source wiring check: `src/code/server/sv_zmq.c` constructs the stats socket
  as `QL_ZMQ_PUB` (`1`) and sends `MATCH_REPORT`/player-event JSON through
  `idZMQ_Publish`.

Round 399 finished the REP/router branch used by retained RCON. This pass
follows the publication side of the same socket factory: case `1` constructs
PUB, case `2` constructs SUB, case `7` constructs PULL, case `8` constructs
PUSH, case `9` constructs XPUB, and case `10` constructs XSUB.
Short label: PUB/SUB/PULL/PUSH and XPUB/XSUB socket-family wiring.

## Alias Reconstruction

This pass added 39 aliases and re-pinned 23 existing aliases in
`references/analysis/quakelive_symbol_aliases.json`.

| Symbol | Alias | Confidence | Evidence |
| --- | --- | --- | --- |
| `sub_413A60` | `zmq_pub_t_ctor` | High | Socket factory case `1` allocates `0x3e8`, chains into XPUB construction, installs PUB vtables, and stores socket type `1`. |
| `sub_413AB0` | `zmq_pub_t_scalar_deleting_dtor` | High | PUB vtable destructor restores PUB subobject vtables, calls the XPUB complete destructor, and conditionally deletes. |
| `sub_413B00` | `zmq_pub_t_xattach_pipe` | High | PUB attach asserts `pipe_`, clears the pipe identity byte at `+0x5c`, and delegates into XPUB attach from `src/pub.cpp`. |
| `sub_413B70` | `zmq_socket_false` | High | Shared pure false predicate used by one-way socket vtable slots such as PUB has-in, SUB has-out, PULL has-out, and PUSH has-in. |
| `sub_413B80` | `zmq_pub_t_array_item_scalar_deleting_dtor` | High | PUB array-item subobject destructor thunk tail-calls the PUB scalar destructor with a `-0x278` adjustment. |
| `sub_413B90` | `zmq_pub_t_i_poll_events_scalar_deleting_dtor` | High | PUB poll-events subobject destructor thunk tail-calls the PUB scalar destructor with a `-0x280` adjustment. |
| `sub_413BA0` | `zmq_pub_t_i_pipe_events_scalar_deleting_dtor` | High | PUB pipe-events subobject destructor thunk tail-calls the PUB scalar destructor with a `-0x284` adjustment. |
| `sub_413BB0` | `zmq_sub_t_ctor` | High | Socket factory case `2` allocates `0x3f8`, chains into XSUB construction, installs SUB vtables, stores socket type `2`, and enables filtering. |
| `sub_413C00` | `zmq_sub_t_scalar_deleting_dtor` | High | SUB vtable destructor restores SUB subobject vtables, calls the XSUB complete destructor, and conditionally deletes. |
| `sub_413C50` | `zmq_sub_t_xsetsockopt` | High | SUB option handler accepts subscribe/unsubscribe ids `6` and `7`, encodes a leading `1` or `0`, copies the topic bytes, and delegates into XSUB send. |
| `sub_413DE0` | `zmq_sub_t_i_pipe_events_scalar_deleting_dtor` | High | SUB pipe-events subobject destructor thunk tail-calls the SUB scalar destructor with a `-0x284` adjustment. |
| `sub_413DF0` | `zmq_sub_t_array_item_scalar_deleting_dtor` | High | SUB array-item subobject destructor thunk tail-calls the SUB scalar destructor with a `-0x278` adjustment. |
| `sub_413E00` | `zmq_sub_t_i_poll_events_scalar_deleting_dtor` | High | SUB poll-events subobject destructor thunk tail-calls the SUB scalar destructor with a `-0x280` adjustment. |
| `sub_416AE0` | `zmq_pull_t_ctor` | High | Socket factory case `7` allocates `0x3a0`, installs PULL vtables, initializes fair-queue state, and stores socket type `7`. |
| `sub_416B50` | `zmq_pull_t_scalar_deleting_dtor` | High | PULL vtable destructor unwinds the fair-queue member and socket base before optional delete. |
| `sub_416BB0` | `zmq_pull_t_xattach_pipe` | High | PULL attach asserts `pipe_` from `src/pull.cpp` and attaches the pipe to the fair queue at object offset `+0x380`. |
| `sub_416C30` | `zmq_pull_t_xterminated` | High | PULL termination tail-calls fair-queue pipe removal for the queue at `+0x380`. |
| `sub_416C40` | `zmq_pull_t_xrecv` | High | PULL receive delegates to the fair queue receive helper at `+0x380` with no identity output pointer. |
| `sub_416C60` | `zmq_pull_t_i_pipe_events_scalar_deleting_dtor` | High | PULL pipe-events subobject destructor thunk tail-calls the PULL scalar destructor with a `-0x284` adjustment. |
| `sub_416C70` | `zmq_pull_t_array_item_scalar_deleting_dtor` | High | PULL array-item subobject destructor thunk tail-calls the PULL scalar destructor with a `-0x278` adjustment. |
| `sub_416C80` | `zmq_pull_t_i_poll_events_scalar_deleting_dtor` | High | PULL poll-events subobject destructor thunk tail-calls the PULL scalar destructor with a `-0x280` adjustment. |
| `sub_416C90` | `zmq_push_t_ctor` | High | Socket factory case `8` allocates `0x3a0`, installs PUSH vtables, initializes load-balancer state, and stores socket type `8`. |
| `sub_416D00` | `zmq_push_t_scalar_deleting_dtor` | High | PUSH vtable destructor unwinds the load-balancer member and socket base before optional delete. |
| `sub_416D60` | `zmq_push_t_xattach_pipe` | High | PUSH attach clears the pipe identity byte and attaches the pipe to the load-balancer at object offset `+0x380`. |
| `sub_416D90` | `zmq_push_t_xwrite_activated` | High | PUSH write activation reactivates a pipe in the load-balancer at `+0x380`. |
| `sub_416DB0` | `zmq_push_t_xterminated` | High | PUSH termination tail-calls load-balancer pipe removal for the queue at `+0x380`. |
| `sub_416DC0` | `zmq_push_t_xsend` | High | PUSH send delegates to the load-balancer send helper at `+0x380` with no identity output pointer. |
| `sub_416DE0` | `zmq_push_t_xhas_out` | High | PUSH has-out tail-calls the load-balancer output probe at `+0x380`. |
| `sub_416DF0` | `zmq_push_t_array_item_scalar_deleting_dtor` | High | PUSH array-item subobject destructor thunk tail-calls the PUSH scalar destructor with a `-0x278` adjustment. |
| `sub_416E00` | `zmq_push_t_i_poll_events_scalar_deleting_dtor` | High | PUSH poll-events subobject destructor thunk tail-calls the PUSH scalar destructor with a `-0x280` adjustment. |
| `sub_416E10` | `zmq_push_t_i_pipe_events_scalar_deleting_dtor` | High | PUSH pipe-events subobject destructor thunk tail-calls the PUSH scalar destructor with a `-0x284` adjustment. |
| `sub_416FB0` | `zmq_xpub_t_scalar_deleting_dtor` | High | XPUB vtable destructor thunk calls the complete XPUB destructor and conditionally deletes. |
| `sub_418280` | `zmq_xpub_t_array_item_scalar_deleting_dtor` | High | XPUB array-item subobject destructor thunk tail-calls the XPUB scalar destructor with a `-0x278` adjustment. |
| `sub_418290` | `zmq_xpub_t_i_poll_events_scalar_deleting_dtor` | High | XPUB poll-events subobject destructor thunk tail-calls the XPUB scalar destructor with a `-0x280` adjustment. |
| `sub_4182A0` | `zmq_xpub_t_i_pipe_events_scalar_deleting_dtor` | High | XPUB pipe-events subobject destructor thunk tail-calls the XPUB scalar destructor with a `-0x284` adjustment. |
| `sub_418380` | `zmq_xsub_t_scalar_deleting_dtor` | High | XSUB vtable destructor thunk calls the complete XSUB destructor and conditionally deletes. |
| `sub_418B40` | `zmq_xsub_t_array_item_scalar_deleting_dtor` | High | XSUB array-item subobject destructor thunk tail-calls the XSUB scalar destructor with a `-0x278` adjustment. |
| `sub_418B50` | `zmq_xsub_t_i_poll_events_scalar_deleting_dtor` | High | XSUB poll-events subobject destructor thunk tail-calls the XSUB scalar destructor with a `-0x280` adjustment. |
| `sub_418B60` | `zmq_xsub_t_i_pipe_events_scalar_deleting_dtor` | High | XSUB pipe-events subobject destructor thunk tail-calls the XSUB scalar destructor with a `-0x284` adjustment. |
| `sub_416C10` | `zmq_xsub_t_xread_activated` | Existing | Re-pinned as the shared read-activation helper used by SUB, PULL, and XSUB vtables to reactivate fair-queue input. |
| `sub_416E20` | `zmq_xpub_t_ctor` | Existing | Re-pinned as factory case `9` and PUB base construction. |
| `sub_416FE0` | `zmq_xpub_t_dtor` | Existing | Re-pinned as the complete XPUB destructor used by PUB and XPUB scalar destructors. |
| `sub_4170B0` | `zmq_xpub_t_xattach_pipe` | Existing | Re-pinned as the XPUB attach implementation reused by PUB after PUB clears pipe identity metadata. |
| `sub_417130` | `zmq_xpub_t_xread_activated` | Existing | Re-pinned as the XPUB subscription-drain/read-activation vtable slot. |
| `sub_417650` | `zmq_xpub_t_xwrite_activated` | Existing | Re-pinned as the XPUB distribution write-activation vtable slot. |
| `sub_417670` | `zmq_xpub_t_xsetsockopt` | Existing | Re-pinned as the XPUB verbose-subscription option handler inherited by PUB. |
| `sub_4176B0` | `zmq_xpub_t_xterminated` | Existing | Re-pinned as the XPUB termination callback inherited by PUB. |
| `sub_417700` | `zmq_xpub_t_xsend` | Existing | Re-pinned as the XPUB/PUB message distribution send implementation. |
| `sub_417780` | `empty_output_buffer` | Existing | Re-pinned as the existing pure true output-ready helper used by XPUB/PUB and XSUB where the vtable advertises output availability. |
| `sub_417790` | `zmq_xpub_t_xrecv` | Existing | Re-pinned as the XPUB subscription-notification receive implementation. |
| `sub_4179A0` | `zmq_xpub_t_xhas_in` | Existing | Re-pinned as XPUB's pending-subscription notification probe. |
| `sub_4179B0` | `zmq_xpub_t_send_unsubscription` | Existing | Re-pinned as the helper that queues unsubscription notifications. |
| `sub_4182B0` | `zmq_xsub_t_ctor` | Existing | Re-pinned as factory case `10` and SUB base construction. |
| `sub_4183B0` | `zmq_xsub_t_dtor` | Existing | Re-pinned as the complete XSUB destructor used by SUB and XSUB scalar destructors. |
| `sub_4184B0` | `zmq_xsub_t_xattach_pipe` | Existing | Re-pinned as the XSUB attach implementation inherited by SUB. |
| `sub_418570` | `zmq_xsub_t_xwrite_activated` | Existing | Re-pinned as XSUB distribution write-activation. |
| `sub_418590` | `zmq_xsub_t_xterminated` | Existing | Re-pinned as XSUB termination over fair queue and distributor members. |
| `sub_4185C0` | `zmq_xsub_t_xhiccuped` | Existing | Re-pinned as XSUB hiccup handling that resends subscription state. |
| `sub_418620` | `zmq_xsub_t_xsend` | Existing | Re-pinned as the XSUB subscription/unsubscription send path used by SUB setsockopt. |
| `sub_418750` | `zmq_xsub_t_xrecv` | Existing | Re-pinned as the XSUB filtered receive path. |
| `sub_418900` | `zmq_xsub_t_xhas_in` | Existing | Re-pinned as XSUB's pending-message/filter-aware input probe. |
| `sub_418A80` | `zmq_xsub_t_send_subscription` | Existing | Re-pinned as the helper that rebuilds subscription frames for new or hiccuped pipes. |

## Observed Facts

- `socket_base_t::create` dispatches PUB/SUB/PULL/PUSH/XPUB/XSUB through
  cases `1`, `2`, `7`, `8`, `9`, and `10`.
- PUB is a thin XPUB-derived wrapper. It disables inbound availability,
  always reports outbound availability through the existing XPUB helper, clears
  pipe identity metadata during attach, and sets socket type `1`.
- SUB is a thin XSUB-derived wrapper. It disables outbound availability,
  encodes subscribe/unsubscribe options as a one-byte command prefix plus topic
  bytes, forwards the frame through `xsub_t::xsend`, and sets socket type `2`.
- PULL and PUSH are symmetric one-way wrappers around the same fair-queue and
  load-balancer helper families already seen in DEALER/ROUTER wiring. PULL
  receives from the fair queue and never sends; PUSH sends through the
  load-balancer and never receives.
- XPUB and XSUB already had most core aliases. This pass fills in the scalar
  destructor and interface-subobject destructor thunks so their vtables are
  fully named and pinned.
- The retained server source builds its stats endpoint with `QL_ZMQ_PUB`,
  then uses `idZMQ_Publish` for `MATCH_REPORT` and other player-event payloads.

## Source Reconstruction

This is static/source-shape reconstruction only. The recovered publication
family gives the following source-level model:

```c
// conceptual reconstruction, not checked-in engine C source
pub_t::pub_t(ctx_t *parent, uint32_t tid, int sid) :
	xpub_t(parent, tid, sid)
{
	type = ZMQ_PUB;
}

void pub_t::xattach_pipe(pipe_t *pipe, bool subscribe_to_all)
{
	assert(pipe);
	pipe->set_identity(NULL, 0);
	xpub_t::xattach_pipe(pipe, subscribe_to_all);
}

int sub_t::xsetsockopt(int option, const void *optval, size_t optvallen)
{
	if (option != ZMQ_SUBSCRIBE && option != ZMQ_UNSUBSCRIBE) {
		errno = EINVAL;
		return -1;
	}

	msg_t msg(optvallen + 1);
	data(msg)[0] = option == ZMQ_SUBSCRIBE ? 1 : 0;
	memcpy(data(msg) + 1, optval, optvallen);
	xsub_t::xsend(&msg);
	msg.close();
	return 0;
}

int pull_t::xrecv(msg_t *msg)
{
	return fq.recv(msg, NULL);
}

int push_t::xsend(msg_t *msg)
{
	return lb.send(msg, NULL);
}
```

## Inference Boundary

This pass does not rename the lower-level fair-queue/load-balancer helper
family around `sub_41E2B0..sub_41EBF0`; those helpers are cited only as the
queue/distribution members called by PULL and PUSH. It also keeps the existing
`empty_output_buffer` alias for `sub_417780` because this round re-pins, but
does not reinterpret, that earlier label.

## Verification

Local verification for this pass:

- `Get-Content -Raw references/analysis/quakelive_symbol_aliases.json | ConvertFrom-Json | Out-Null`
- `python -m pytest -q tests/test_platform_services.py::test_zmq_pub_sub_pipeline_round_400_aliases_are_pinned`
- `python -m pytest -q tests/test_platform_services.py::test_zmq_pub_sub_pipeline_round_400_aliases_are_pinned tests/test_platform_services.py::test_zmq_rep_router_round_399_aliases_are_pinned tests/test_platform_services.py::test_zmq_req_dealer_round_398_aliases_are_pinned tests/test_platform_services.py::test_server_zmq_runtime_reconstructs_retail_publication_and_rcon_owners`

## Parity Estimate

- Focused PUB/SUB/PULL/PUSH and XPUB/XSUB socket-family wiring:
  **before 46% -> after 89%**.
- ZMQ-related source reconstruction confidence, including retained
  publication/RCON ownership, public wrappers, socket/message helpers,
  command-delivery support, queue backing-store evidence, object lifecycle
  ownership, event-loop timer/fd-watch wiring, option/default storage, TCP
  connecter reconnect/stream-engine handoff, TCP listener bind/accept handoff,
  shared TCP/IP helper wiring, stream-engine class-edge/peer-address helpers,
  stream-engine message-state callbacks, raw/v1/v2 codec wiring, NULL
  mechanism READY/ZAP metadata wiring, PLAIN mechanism dispatch/state wiring,
  session lifecycle/pipe/ZAP/engine wiring, REQ/dealer socket plus
  req-session wiring, REP/router socket-family wiring, and PUB/SUB/PULL/PUSH
  plus XPUB/XSUB wiring:
  **before 90.0% -> after 90.4%**.
- Overall Quake Live source parity:
  **before 55.63% -> after 55.64%**.
