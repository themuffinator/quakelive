# Quake Live ZMQ/CZMQ Mapping Round 396

Date: 2026-06-06

Focus: recover the retained libzmq PLAIN mechanism class edge: constructor and
destructor ownership, virtual `next_handshake_command` /
`process_handshake_command` dispatch, ZAP wait handling, status, and the
HELLO/WELCOME/INITIATE/READY state progression.

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

Round 395 mapped the base mechanism and NULL mechanism READY/ZAP metadata
wiring. This pass follows the same virtual slots into the PLAIN mechanism,
where the state field drives the four-command security handshake and a ZAP wait
branch.
Short label: PLAIN mechanism dispatch/state wiring.

## Alias Reconstruction

This pass added 7 aliases to
`references/analysis/quakelive_symbol_aliases.json`.

| Symbol | Alias | Confidence | Evidence |
| --- | --- | --- | --- |
| `sub_426D50` | `zmq_plain_mechanism_t_ctor` | High | Constructor installs the base mechanism vtable, copies peer data, installs the PLAIN vtable, and seeds state from the server/client option flag. |
| `sub_426E00` | `zmq_plain_mechanism_t_scalar_deleting_dtor` | High | PLAIN vtable destructor calls the complete destructor and conditionally deletes. |
| `sub_426E30` | `zmq_plain_mechanism_t_dtor` | High | Complete destructor frees PLAIN peer-address storage, restores the base mechanism vtable, then frees base storage. |
| `sub_426EB0` | `zmq_plain_mechanism_t_next_handshake_command` | High | Outbound dispatcher switches on state `0/2/4/6` to produce HELLO, WELCOME, INITIATE, and READY commands. |
| `sub_426FA0` | `zmq_plain_mechanism_t_process_handshake_command` | High | Inbound dispatcher switches on state `1/3/5/7` to process HELLO, WELCOME, INITIATE, and READY commands, then clears the command message. |
| `sub_4270E0` | `zmq_plain_mechanism_t_status` | High | Status returns ready only when the PLAIN state field reaches `9`. |
| `sub_4270F0` | `zmq_plain_mechanism_t_zap_msg_available` | High | ZAP availability is valid only in state `8`, consumes a ZAP reply, and advances to state `2`. |

Previously mapped PLAIN command helpers were also rechecked in this pass:
`zmq_plain_mechanism_t_produce_hello`,
`zmq_plain_mechanism_t_process_hello`,
`zmq_plain_mechanism_t_process_welcome`,
`zmq_plain_mechanism_t_produce_initiate`,
`zmq_plain_mechanism_t_process_initiate`,
`zmq_plain_mechanism_t_produce_ready`,
`zmq_plain_mechanism_t_process_ready`,
`zmq_plain_mechanism_t_send_zap_request`, and
`zmq_plain_mechanism_t_receive_and_process_zap_reply`.

## Observed Facts

- `stream_engine_t` allocates a `0x290`-byte PLAIN mechanism object when the
  mechanism string matches `"PLAIN"` and constructs it through `sub_426D50`.
- The PLAIN vtable at `0x5516D0` has the same mechanism slot layout as NULL:
  destructor, next command, process command, passthrough encode, passthrough
  decode, ZAP availability, status, and default property hook.
- The constructor sets the state field from `arg1[0x62] != 0`, making the same
  class handle both client and server handshake starts.
- Outbound states are `0 -> HELLO -> 3`, `2 -> WELCOME -> 5`,
  `4 -> INITIATE -> 7`, and `6 -> READY -> 9`.
- Inbound states are `1 -> process HELLO`, `3 -> process WELCOME -> 4`,
  `5 -> process INITIATE -> 6`, and `7 -> process READY -> 9`.
- After processing HELLO, the dispatcher moves to state `2` unless
  `process_hello` marked a ZAP wait, in which case it moves to state `8`.
  `zap_msg_available` is the only valid transition from state `8`, and it
  advances to state `2` after a successful ZAP reply.
- INITIATE and READY use the shared metadata helpers recovered in round 395:
  `zmq_mechanism_t_add_property` for outbound metadata and
  `zmq_mechanism_t_parse_metadata` for inbound metadata.

## Source Reconstruction

This is static/source-shape reconstruction only. The recovered class edge
explains how the stream engine can drive PLAIN without knowing whether the
connection is in the client or server side of the command sequence.

Representative recovered shape:

```c
// conceptual reconstruction, not checked-in engine C source
int plain_mechanism_t::next_handshake_command(msg_t *msg)
{
	switch (state) {
	case 0:
		produce_hello(msg);
		state = 3;
		return 0;
	case 2:
		produce_welcome(msg);
		state = 5;
		return 0;
	case 4:
		produce_initiate(msg);
		state = 7;
		return 0;
	case 6:
		produce_ready(msg);
		state = 9;
		return 0;
	default:
		errno = EAGAIN;
		return -1;
	}
}

int plain_mechanism_t::process_handshake_command(msg_t *msg)
{
	int rc;

	switch (state) {
	case 1:
		rc = process_hello(msg);
		if (rc == 0)
			state = zap_waiting ? 8 : 2;
		break;
	case 3:
		rc = process_welcome(msg);
		if (rc == 0)
			state = 4;
		break;
	case 5:
		rc = process_initiate(msg);
		if (rc == 0)
			state = 6;
		break;
	case 7:
		rc = process_ready(msg);
		if (rc == 0)
			state = 9;
		break;
	default:
		errno = EPROTO;
		return -1;
	}

	if (rc != 0)
		return rc;
	msg_close_and_reinit_empty_command(msg);
	return 0;
}
```

## Inference Boundary

This pass does not reconstruct the full ZAP message payload builders in source
form. The send/receive ZAP helpers are re-pinned as PLAIN-owned evidence, but
the deeper ZAP socket dialogue remains shared with the NULL pass and can be
expanded in a later focused round if needed.

## Verification

Local verification for this pass:

- `Get-Content -Raw references/analysis/quakelive_symbol_aliases.json | ConvertFrom-Json | Out-Null`
- `python -m pytest -q tests/test_platform_services.py::test_zmq_plain_mechanism_round_396_aliases_are_pinned`
- `python -m pytest -q tests/test_platform_services.py::test_zmq_plain_mechanism_round_396_aliases_are_pinned tests/test_platform_services.py::test_zmq_null_mechanism_round_395_aliases_are_pinned tests/test_platform_services.py::test_zmq_codec_round_394_aliases_are_pinned tests/test_platform_services.py::test_zmq_stream_engine_state_machine_round_393_aliases_are_pinned tests/test_platform_services.py::test_zmq_stream_engine_peer_round_392_aliases_are_pinned tests/test_platform_services.py::test_zmq_tcp_socket_and_endpoint_round_391_aliases_are_pinned tests/test_platform_services.py::test_zmq_tcp_listener_round_390_aliases_are_pinned tests/test_platform_services.py::test_zmq_tcp_connecter_round_379_aliases_are_pinned tests/test_platform_services.py::test_zmq_options_default_and_mask_vector_round_378_aliases_are_pinned tests/test_platform_services.py::test_zmq_poller_base_io_object_round_377_aliases_are_pinned tests/test_platform_services.py::test_zmq_public_api_aliases_and_round_365_evidence_are_pinned`
- `python -m pytest -q tests/test_platform_services.py::test_server_zmq_runtime_reconstructs_retail_publication_and_rcon_owners tests/test_server_full_parity_gate.py::test_server_full_parity_gate_writes_status_artifact`

## Parity Estimate

- Focused PLAIN mechanism state-machine mapping:
  **before 38% -> after 86%**.
- ZMQ-related source reconstruction confidence, including retained
  publication/RCON ownership, public wrappers, socket/message helpers,
  command-delivery support, queue backing-store evidence, object lifecycle
  ownership, event-loop timer/fd-watch wiring, option/default storage, TCP
  connecter reconnect/stream-engine handoff, TCP listener bind/accept handoff,
  shared TCP/IP helper wiring, stream-engine class-edge/peer-address helpers,
  stream-engine message-state callbacks, raw/v1/v2 codec wiring, NULL
  mechanism READY/ZAP metadata wiring, and PLAIN mechanism dispatch/state
  wiring:
  **before 88.7% -> after 89.1%**.
- Overall Quake Live source parity:
  **before 55.59% -> after 55.60%**.
