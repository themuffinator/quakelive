# Quake Live ZMQ/CZMQ Mapping Round 397

Date: 2026-06-06

Focus: recover the retained libzmq `session_base_t` lifecycle and the wiring
between pipe attachment, ZAP pipe writes, stream-engine attachment, and reconnect
detach handling.

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

Rounds 394-396 closed the raw/v1/v2 codec and NULL/PLAIN mechanism edges. This
pass moves one layer outward to the session object that owns the live pipe,
drives ZAP traffic through a dedicated pipe, accepts the stream engine, and
re-enters connector startup after engine detach.
Short label: session_base_t lifecycle/pipe/ZAP/engine wiring.

## Alias Reconstruction

This pass added 8 aliases and corrected 1 existing alias in
`references/analysis/quakelive_symbol_aliases.json`.

| Symbol | Alias | Confidence | Evidence |
| --- | --- | --- | --- |
| `sub_41B0E0` | `zmq_session_base_t_ctor` | High | Constructor chains through `own_t` and `io_object_t`, installs all three session vtables, initializes pipe/engine/ZAP fields, stores options, and allocates the terminating-pipes tree sentinel. |
| `sub_41B230` | `zmq_session_base_t_scalar_deleting_dtor` | High | Own-vtable destructor calls the complete destructor and conditionally frees the object. |
| `sub_41B260` | `zmq_session_base_t_dtor` | High | Complete destructor restores the session vtables, asserts `!pipe` and `!zap_pipe`, cancels the linger timer, releases connector/endpoint storage, destroys the terminating-pipes tree, and unwinds base classes. |
| `sub_41B430` | `zmq_session_base_t_attach_pipe` | High | Pipe attachment asserts non-terminating state, asserts no existing pipe, stores the pipe at offset `0x288`, and installs the session `i_pipe_events` sink at offset `0x280`. |
| `sub_41B570` | `zmq_session_base_t_write_zap_msg` | High | ZAP writer requires the ZAP pipe at offset `0x28c`, writes a message through `pipe_t::write`, wakes the pipe when the message is not multipart, and reinitializes the message as empty. |
| `sub_41BEB0` | `zmq_session_base_t_attach_engine` | High | Corrects the prior round-131 name: the body asserts `engine_ != NULL`, creates/attaches the session pipepair if needed, stores the engine at offset `0x2a4`, and calls the engine plug callback. |
| `sub_41C320` | `zmq_session_base_t_detach` | High | Detach path terminates immediately for non-connect sessions, hiccups/terminates the pipe for reconnectable TCP-style sessions, invokes the owner detach slot, and restarts connecting when reconnect interval is enabled. |
| `sub_41C6F0` | `zmq_session_base_t_io_object_scalar_deleting_dtor` | High | `io_object_t` subobject vtable destructor thunk tail-calls the session scalar destructor with a `-0x278` this adjustment. |
| `sub_41C700` | `zmq_session_base_t_i_pipe_events_scalar_deleting_dtor` | High | `i_pipe_events` subobject vtable destructor thunk tail-calls the session scalar destructor with a `-0x280` this adjustment. |

Previously mapped session methods were rechecked as context:
`zmq_session_base_t_create`, `zmq_session_base_t_flush`,
`zmq_session_base_t_clean_pipes`, `zmq_session_base_t_pipe_terminated`,
`zmq_session_base_t_read_activated`, `zmq_session_base_t_write_activated`,
`zmq_session_base_t_hiccuped`, `zmq_session_base_t_process_plug`,
`zmq_session_base_t_zap_connect`, `zmq_session_base_t_zap_enabled`,
`zmq_session_base_t_process_term`, `zmq_session_base_t_timer_event`, and
`zmq_session_base_t_start_connecting`.

## Observed Facts

- `zmq_session_base_t_create` allocates `0x2b8` bytes for most socket types and
  calls `sub_41B0E0`; only the REQ socket branch allocates the `req_session_t`
  subclass and calls `sub_414410`.
- The constructor installs three session vtables: own object at `0x550d4c`,
  `io_object_t` subobject at `0x550d9c`, and `i_pipe_events` subobject at
  `0x550db0`.
- The own-vtable slot for engine attachment points to `sub_41BEB0`. HLIL shows
  the `"engine_ != NULL"` assertion and the later `(*(*engine + 4))(...)` call,
  so the earlier `attach_pipe` label for this function was too broad.
- The true pipe attachment body is `sub_41B430`: it stores `pipe_`, then assigns
  the session sink pointer into the pipe's sink field.
- `sub_41B570` is the shared ZAP message egress used by the recovered NULL and
  PLAIN mechanism ZAP request builders; it fails with errno `0x7e` when no ZAP
  pipe is present.
- `sub_41C320` is the stream-engine detach callback target. It either terminates
  the session, hiccups and terminates the attached pipe, or calls
  `zmq_session_base_t_start_connecting` when reconnect is enabled.
- The two 11-byte functions at `sub_41C6F0` and `sub_41C700` are not independent
  behavior; they are multiple-inheritance destructor thunks for the two session
  subobjects.

## Source Reconstruction

This is static/source-shape reconstruction only. The recovered object edge gives
the expected source-level split:

```c
// conceptual reconstruction, not checked-in engine C source
void session_base_t::attach_pipe(pipe_t *pipe_)
{
	assert(!is_terminating());
	assert(!pipe);
	assert(pipe_);

	pipe = pipe_;
	pipe->set_event_sink(this);
}

void session_base_t::write_zap_msg(msg_t *msg_)
{
	if (!zap_pipe) {
		errno = EFSM;
		return -1;
	}

	assert(zap_pipe->write(msg_));
	if (!msg_->more())
		zap_pipe->flush();

	msg_->init();
	return 0;
}

void session_base_t::attach_engine(i_engine *engine_)
{
	assert(engine_ != NULL);

	if (!pipe && !is_terminating())
		create_pipepair_and_attach_session_pipe();

	assert(!engine);
	engine = engine_;
	engine->plug(io_thread, this);
}

void session_base_t::detach()
{
	if (!connect)
		terminate();
	else {
		hiccup_and_drop_pipe_when_applicable();
		owner_detach();
		if (reconnect_ivl != -1)
			start_connecting(true);
	}
}
```

## Inference Boundary

The alias correction for `sub_41BEB0` is high confidence because of the direct
engine assertion, engine storage, and engine virtual call. The exact libzmq
socket-type enum names are not renamed in this pass; the detach branch is
described in terms of observed pipe/reconnect behavior and left for a later
socket-type-specific reconstruction round.

## Verification

Local verification for this pass:

- `Get-Content -Raw references/analysis/quakelive_symbol_aliases.json | ConvertFrom-Json | Out-Null`
- `python -m pytest -q tests/test_platform_services.py::test_zmq_session_base_round_397_aliases_are_pinned`
- `python -m pytest -q tests/test_platform_services.py::test_zmq_session_base_round_397_aliases_are_pinned tests/test_platform_services.py::test_zmq_plain_mechanism_round_396_aliases_are_pinned tests/test_platform_services.py::test_zmq_null_mechanism_round_395_aliases_are_pinned tests/test_platform_services.py::test_zmq_codec_round_394_aliases_are_pinned tests/test_platform_services.py::test_zmq_stream_engine_state_machine_round_393_aliases_are_pinned tests/test_platform_services.py::test_zmq_stream_engine_peer_round_392_aliases_are_pinned tests/test_platform_services.py::test_zmq_tcp_socket_and_endpoint_round_391_aliases_are_pinned tests/test_platform_services.py::test_zmq_tcp_listener_round_390_aliases_are_pinned tests/test_platform_services.py::test_zmq_tcp_connecter_round_379_aliases_are_pinned tests/test_platform_services.py::test_zmq_options_default_and_mask_vector_round_378_aliases_are_pinned tests/test_platform_services.py::test_zmq_poller_base_io_object_round_377_aliases_are_pinned tests/test_platform_services.py::test_zmq_public_api_aliases_and_round_365_evidence_are_pinned`
- `python -m pytest -q tests/test_platform_services.py::test_server_zmq_runtime_reconstructs_retail_publication_and_rcon_owners tests/test_server_full_parity_gate.py::test_server_full_parity_gate_writes_status_artifact`

## Parity Estimate

- Focused `session_base_t` lifecycle/pipe/ZAP/engine wiring:
  **before 55% -> after 88%**.
- ZMQ-related source reconstruction confidence, including retained
  publication/RCON ownership, public wrappers, socket/message helpers,
  command-delivery support, queue backing-store evidence, object lifecycle
  ownership, event-loop timer/fd-watch wiring, option/default storage, TCP
  connecter reconnect/stream-engine handoff, TCP listener bind/accept handoff,
  shared TCP/IP helper wiring, stream-engine class-edge/peer-address helpers,
  stream-engine message-state callbacks, raw/v1/v2 codec wiring, NULL
  mechanism READY/ZAP metadata wiring, PLAIN mechanism dispatch/state wiring,
  and session lifecycle/pipe/ZAP/engine wiring:
  **before 89.1% -> after 89.4%**.
- Overall Quake Live source parity:
  **before 55.60% -> after 55.61%**.
