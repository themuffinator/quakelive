# Quake Live ZMQ/CZMQ Mapping Round 395

Date: 2026-06-06

Focus: recover the retained libzmq mechanism layer that sits between
`stream_engine_t` and the raw/ZMTP codecs: the base `mechanism_t` virtual
surface, NULL mechanism READY command flow, ZAP availability wiring, and shared
metadata helpers.

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

Rounds 392 and 393 pinned stream-engine delivery into the mechanism vtable.
Round 394 pinned the codec layer underneath it. This pass fills the mechanism
class bridge used by the NULL security mode and by shared metadata parsing.
Short label: NULL mechanism READY/ZAP metadata wiring.

## Alias Reconstruction

This pass added 14 aliases to
`references/analysis/quakelive_symbol_aliases.json`.

| Symbol | Alias | Confidence | Evidence |
| --- | --- | --- | --- |
| `sub_426010` | `zmq_mechanism_t_passthrough_encode_decode` | High | NULL, PLAIN, and base `mechanism_t` vtables all use this pure no-op for encode/decode slots. |
| `sub_426020` | `zmq_null_mechanism_t_ctor` | High | Constructor installs the base mechanism vtable, copies options/peer address fields, then installs the NULL mechanism vtable. |
| `sub_426100` | `zmq_null_mechanism_t_scalar_deleting_dtor` | High | NULL vtable destructor calls `sub_426130` and conditionally deletes the object. |
| `sub_426130` | `zmq_null_mechanism_t_dtor` | High | Complete destructor frees NULL peer-address storage, restores the base mechanism vtable, then frees base mechanism storage. |
| `sub_4261B0` | `zmq_null_mechanism_t_next_handshake_command` | High | Builds the `READY` command, optionally performs ZAP first, appends `Socket-Type` and `Identity` metadata, and marks READY sent. |
| `sub_426370` | `zmq_null_mechanism_t_process_handshake_command` | High | Validates an inbound `READY` command and sends remaining bytes to `zmq_mechanism_t_parse_metadata`. |
| `sub_426480` | `zmq_null_mechanism_t_zap_msg_available` | High | NULL vtable ZAP slot gates duplicate availability notification and calls the ZAP reply processor. |
| `sub_4264B0` | `zmq_null_mechanism_t_status` | High | Returns ready only after both inbound and outbound READY flags are set. |
| `sub_4283A0` | `zmq_mechanism_t_scalar_deleting_dtor` | High | Base mechanism vtable destructor frees stored user id/options state and conditionally deletes. |
| `sub_428400` | `zmq_mechanism_t_dtor` | High | Base complete destructor frees the same state without object deletion. |
| `sub_428450` | `zmq_mechanism_t_get_user_id` | High | Copies the stored user-id string into a message and marks it as a command/property-style message. |
| `sub_4284F0` | `zmq_mechanism_t_socket_type_string` | High | Bounds-checks socket type `0..10` and returns the corresponding socket-type string table entry. |
| `sub_428550` | `zmq_mechanism_t_add_property` | High | Encodes metadata as one-byte name length, name bytes, four-byte big-endian value length, and value bytes. |
| `sub_428AC0` | `zmq_mechanism_t_property` | High | Default final mechanism virtual is reached from metadata parsing for unhandled properties and returns success. |

Previously mapped NULL/metadata symbols were also rechecked in this pass:
`zmq_null_mechanism_t_send_zap_request`, `zmq_null_mechanism_t_receive_and_process_zap_reply`,
`zmq_mechanism_t_parse_metadata`, and `zmq_mechanism_t_check_socket_type`.

## Observed Facts

- The NULL mechanism vtable at `0x551630` has destructor,
  `next_handshake_command`, `process_handshake_command`, encode, decode,
  `zap_msg_available`, `status`, and `property` slots. The encode and decode
  slots both point at the shared `sub_426010` no-op.
- `sub_4261B0` refuses a second outbound READY (`errno = EAGAIN`), optionally
  sends and consumes ZAP before READY, writes `0x05 "READY"`, and encodes
  metadata with `Socket-Type` first.
- `sub_426370` refuses a second inbound READY, requires the exact six-byte
  READY command prefix, and passes the remaining payload to
  `zmq_mechanism_t_parse_metadata`.
- `sub_428650` treats `Identity` specially, validates `Socket-Type` through
  `sub_428AE0`, and calls the final mechanism virtual for other metadata
  properties.
- `sub_428450` is called from `stream_engine_t::mechanism_ready`, making the
  mechanism user-id storage the data source that gets delivered to the session
  once handshaking completes.

## Source Reconstruction

This is static/source-shape reconstruction only. The recovered class edge
explains the READY flow that `stream_engine_t` drives through its mechanism
pointer.

Representative recovered shape:

```c
// conceptual reconstruction, not checked-in engine C source
int null_mechanism_t::next_handshake_command(msg_t *msg)
{
	if (ready_sent)
		return errno = EAGAIN, -1;

	if (zap_required && !zap_ready) {
		if (zap_sent)
			return errno = EAGAIN, -1;
		send_zap_request();
		zap_sent = true;
		if (receive_and_process_zap_reply() != 0)
			return -1;
		zap_ready = true;
	}

	unsigned char command[0x200];
	write_ready_prefix(command);
	size_t size = add_property(command + 6, "Socket-Type", socket_type_string(options.type));
	if (options.type == ROUTER || options.type == DEALER || options.type == REQ)
		size += add_property(command + 6 + size, "Identity", identity);

	msg_init_size(msg, size + 6);
	memcpy(msg_data(msg), command, size + 6);
	ready_sent = true;
	return 0;
}
```

## Inference Boundary

This pass deliberately stops at the NULL mechanism and shared base helpers.
PLAIN mechanism lifecycle and PLAIN-specific state transitions remain a later
mapping target even though they share the same passthrough encode/decode and
property virtuals.

## Verification

Local verification for this pass:

- `Get-Content -Raw references/analysis/quakelive_symbol_aliases.json | ConvertFrom-Json | Out-Null`
- `python -m pytest -q tests/test_platform_services.py::test_zmq_null_mechanism_round_395_aliases_are_pinned`
- `python -m pytest -q tests/test_platform_services.py::test_zmq_null_mechanism_round_395_aliases_are_pinned tests/test_platform_services.py::test_zmq_codec_round_394_aliases_are_pinned tests/test_platform_services.py::test_zmq_stream_engine_state_machine_round_393_aliases_are_pinned tests/test_platform_services.py::test_zmq_stream_engine_peer_round_392_aliases_are_pinned tests/test_platform_services.py::test_zmq_tcp_socket_and_endpoint_round_391_aliases_are_pinned tests/test_platform_services.py::test_zmq_tcp_listener_round_390_aliases_are_pinned tests/test_platform_services.py::test_zmq_tcp_connecter_round_379_aliases_are_pinned tests/test_platform_services.py::test_zmq_options_default_and_mask_vector_round_378_aliases_are_pinned tests/test_platform_services.py::test_zmq_poller_base_io_object_round_377_aliases_are_pinned tests/test_platform_services.py::test_zmq_public_api_aliases_and_round_365_evidence_are_pinned`
- `python -m pytest -q tests/test_platform_services.py::test_server_zmq_runtime_reconstructs_retail_publication_and_rcon_owners tests/test_server_full_parity_gate.py::test_server_full_parity_gate_writes_status_artifact`

## Parity Estimate

- Focused NULL mechanism and mechanism metadata mapping:
  **before 44% -> after 90%**.
- ZMQ-related source reconstruction confidence, including retained
  publication/RCON ownership, public wrappers, socket/message helpers,
  command-delivery support, queue backing-store evidence, object lifecycle
  ownership, event-loop timer/fd-watch wiring, option/default storage, TCP
  connecter reconnect/stream-engine handoff, TCP listener bind/accept handoff,
  shared TCP/IP helper wiring, stream-engine class-edge/peer-address helpers,
  stream-engine message-state callbacks, raw/v1/v2 codec wiring, and NULL
  mechanism READY/ZAP metadata wiring:
  **before 88.3% -> after 88.7%**.
- Overall Quake Live source parity:
  **before 55.58% -> after 55.59%**.
