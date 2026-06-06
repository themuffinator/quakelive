# Quake Live ZMQ/CZMQ Mapping Round 394

Date: 2026-06-06

Focus: recover the retained libzmq codec layer below `stream_engine_t`: the
encoder/decoder interfaces, raw encoder/decoder, v1 encoder/decoder, v2
encoder/decoder, and their state callbacks.

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

Rounds 392 and 393 finished the stream-engine class edge and message-state
callbacks. This pass follows those callbacks into the encoder/decoder objects
constructed by the raw-socket path and by the ZMTP v1/v2 greeting branches.

## Alias Reconstruction

This pass added 49 aliases to
`references/analysis/quakelive_symbol_aliases.json`.

| Symbol | Alias | Confidence | Evidence |
| --- | --- | --- | --- |
| `sub_424940` | `zmq_i_encoder_t_scalar_deleting_dtor` | High | `i_encoder` vtable slot restores the `zmq::i_encoder::vftable` and conditionally deletes. |
| `sub_424970` | `zmq_raw_encoder_t_scalar_deleting_dtor` | High | Raw encoder vtable destructor frees the encoder scratch buffer and unwinds to `i_encoder`. |
| `sub_4249B0` | `zmq_raw_encoder_t_message_ready` | High | Raw encoder state callback exposes the current message body and re-arms itself for the next message. |
| `sub_424A10` | `zmq_raw_encoder_t_ctor` | High | Raw encoder constructor installs the raw encoder-base vtable and allocates the 0x2000 scratch buffer. |
| `sub_424A80` | `zmq_encoder_base_t_encode` | High | Shared encoder-base virtual reads staged bytes, invokes the next-step callback, and closes the in-progress message. |
| `sub_424BF0` | `zmq_i_decoder_t_dtor` | High | Tiny `i_decoder` complete destructor writes the base decoder vtable. |
| `sub_424C00` | `zmq_i_decoder_t_scalar_deleting_dtor` | High | `i_decoder` vtable deleting destructor restores the base vtable and conditionally deletes. |
| `sub_424C30` | `zmq_raw_decoder_t_msg` | High | Raw decoder message-access slot returns the embedded message object at offset 4. |
| `sub_424C40` | `zmq_raw_decoder_t_ctor` | High | Raw decoder constructor installs the raw decoder vtable, initializes the embedded message marker, and allocates the 0x2000 read buffer. |
| `sub_424CC0` | `zmq_raw_decoder_t_scalar_deleting_dtor` | High | Raw decoder deleting destructor calls the complete raw decoder destructor and conditionally deletes. |
| `sub_424CF0` | `zmq_raw_decoder_t_dtor` | High | Raw decoder destructor closes the embedded message, frees the read buffer, and unwinds to `i_decoder`. |
| `sub_424DB0` | `zmq_raw_decoder_t_get_buffer` | High | Raw decoder `get_buffer` slot returns the internal read buffer pointer and capacity. |
| `sub_424DD0` | `zmq_raw_decoder_t_decode` | High | Raw decoder `decode` slot initializes a message of the received size, copies the bytes, and reports consumption. |
| `sub_424E60` | `zmq_v1_encoder_t_ctor` | High | Stream-engine ZMTP v1 path constructs this object and installs the v1 encoder vtable plus `message_ready`. |
| `sub_424EB0` | `zmq_v1_encoder_t_scalar_deleting_dtor` | High | v1 encoder vtable destructor frees the encoder buffer and unwinds to `i_encoder`. |
| `sub_424EF0` | `zmq_v1_encoder_t_size_ready` | High | v1 encoder state callback exposes the message body and re-arms `message_ready`. |
| `sub_424F50` | `zmq_v1_encoder_t_message_ready` | High | v1 encoder state callback builds the one-byte or 0xff-plus-64-bit size header and more flag. |
| `sub_425030` | `zmq_encoder_base_v1_encoder_t_ctor` | High | v1 encoder-base constructor installs the v1 encoder-base vtable and allocates the 0x2000 scratch buffer. |
| `sub_4250A0` | `zmq_v1_decoder_t_msg` | High | v1 decoder message-access slot returns the embedded message object. |
| `sub_4250B0` | `zmq_get_uint64` | High | Big-endian 8-byte helper used by v1/v2 decoder large-size callbacks. |
| `sub_425130` | `zmq_v1_decoder_t_ctor` | High | Stream-engine ZMTP v1 path constructs this object, stores max-message-size bounds, and seeds the first size-byte read. |
| `sub_4251A0` | `zmq_v1_decoder_t_scalar_deleting_dtor` | High | v1 decoder complete-object deleting destructor calls the v1 decoder destructor and conditionally deletes. |
| `sub_4251D0` | `zmq_v1_decoder_t_dtor` | High | v1 decoder destructor closes the embedded message, frees the read buffer, and unwinds to `i_decoder`. |
| `sub_425290` | `zmq_v1_decoder_t_one_byte_size_ready` | High | v1 decoder state callback handles the first size byte, rejects zero-size frames, or switches to the 8-byte size path. |
| `sub_4253E0` | `zmq_v1_decoder_t_eight_byte_size_ready` | High | v1 decoder large-size callback reads the 8-byte length, checks max size, and allocates the message. |
| `sub_425520` | `zmq_v1_decoder_t_flags_ready` | High | v1 decoder flags callback copies the more flag into the message and schedules the body read. |
| `sub_425580` | `zmq_v1_decoder_t_message_ready` | High | v1 decoder final callback re-arms the next first-size-byte read and returns a complete message. |
| `sub_4255C0` | `zmq_decoder_base_v1_decoder_t_ctor` | High | v1 decoder-base constructor installs the decoder-base vtable and allocates the 0x2000 read buffer. |
| `sub_425660` | `zmq_decoder_base_v1_decoder_t_dtor` | High | v1 decoder-base destructor frees the read buffer and restores the `i_decoder` vtable. |
| `sub_425680` | `zmq_decoder_base_t_decode` | High | Shared decoder-base virtual advances the read pointer, copies partial data when needed, and invokes state callbacks. |
| `sub_425780` | `zmq_decoder_base_v1_decoder_t_scalar_deleting_dtor` | High | i_decoder-side v1 decoder-base deleting destructor frees the read buffer and conditionally deletes. |
| `sub_4257C0` | `zmq_v2_encoder_t_ctor` | High | Stream-engine ZMTP v2 path constructs this object and seeds v2 `message_ready`. |
| `sub_425810` | `zmq_v2_encoder_t_scalar_deleting_dtor` | High | v2 encoder vtable destructor frees the encoder buffer and unwinds to `i_encoder`. |
| `sub_425850` | `zmq_v2_encoder_t_message_ready` | High | v2 encoder callback builds the flags byte, one-byte or eight-byte size field, command bit, and more bit. |
| `sub_425940` | `zmq_v2_encoder_t_size_ready` | High | v2 encoder state callback exposes the body and re-arms `message_ready`. |
| `sub_4259A0` | `zmq_encoder_base_v2_encoder_t_ctor` | High | v2 encoder-base constructor installs the v2 encoder-base vtable and allocates the 0x2000 scratch buffer. |
| `sub_425A10` | `zmq_encoder_base_t_load_msg` | High | Shared encoder-base `load_msg` virtual asserts no message is in progress and starts the next-step callback. |
| `sub_425A80` | `zmq_v2_decoder_t_msg` | High | v2 decoder message-access slot returns the embedded message object. |
| `sub_425A90` | `zmq_v2_decoder_t_ctor` | High | Stream-engine ZMTP v2 path constructs this object, stores max-message-size bounds, and seeds the flags-byte read. |
| `sub_425B00` | `zmq_v2_decoder_t_scalar_deleting_dtor` | High | v2 decoder complete-object deleting destructor calls the v2 decoder destructor and conditionally deletes. |
| `sub_425B30` | `zmq_v2_decoder_t_dtor` | High | v2 decoder destructor closes the embedded message, frees the read buffer, and unwinds to `i_decoder`. |
| `sub_425BF0` | `zmq_v2_decoder_t_flags_ready` | High | v2 decoder flags callback maps more/command flags and chooses one-byte or eight-byte size parsing. |
| `sub_425C60` | `zmq_v2_decoder_t_one_byte_size_ready` | High | v2 decoder short-size callback validates max size, allocates the message, and schedules body reading. |
| `sub_425D70` | `zmq_v2_decoder_t_eight_byte_size_ready` | High | v2 decoder large-size callback uses the shared big-endian helper, validates max size, and allocates the message. |
| `sub_425E90` | `zmq_v2_decoder_t_message_ready` | High | v2 decoder final callback re-arms the flags-byte read and returns a complete message. |
| `sub_425ED0` | `zmq_decoder_base_v2_decoder_t_ctor` | High | v2 decoder-base constructor installs the decoder-base vtable and allocates the 0x2000 read buffer. |
| `sub_425F70` | `zmq_decoder_base_v2_decoder_t_dtor` | High | v2 decoder-base destructor frees the read buffer and restores the `i_decoder` vtable. |
| `sub_425F90` | `zmq_decoder_base_t_get_buffer` | High | Shared decoder-base `get_buffer` virtual returns either the active target pointer or the scratch buffer/capacity. |
| `sub_425FD0` | `zmq_decoder_base_v2_decoder_t_scalar_deleting_dtor` | High | i_decoder-side v2 decoder-base deleting destructor frees the read buffer and conditionally deletes. |

## Observed Facts

- The raw path in `stream_engine_t::plug` allocates a raw encoder at size
  `0x40` and a raw decoder at size `0x38`, then installs direct
  session pull/push callbacks. That ties `sub_424A10` and `sub_424C40` to the
  raw codec pair.
- The ZMTP greeting path allocates v1 codecs through `sub_424E60` /
  `sub_425130` and v2 codecs through `sub_4257C0` / `sub_425A90`, depending on
  the negotiated revision.
- Every encoder class reuses the same encoder-base virtuals:
  `zmq_encoder_base_t_encode` and `zmq_encoder_base_t_load_msg`. The concrete
  encoder state functions only decide the wire header and body staging.
- v1 encoding writes the legacy size-plus-flags format. v2 encoding separates
  flags from size and preserves both the MORE bit and COMMAND bit.
- Every decoder class uses either a raw decode callback or the shared
  decoder-base read pump. The v1/v2 state functions match the wire protocol:
  v1 starts with size, v2 starts with flags, and both have one-byte and
  eight-byte size branches.
- `zmq_get_uint64` is intentionally promoted as a shared helper rather than a
  decoder method because both v1 and v2 large-size paths call it with a pointer
  to the eight-byte wire-size field.

## Source Reconstruction

This is static/source-shape reconstruction only. The recovered codec layer is
private retained libzmq implementation underneath the public ZMQ calls used by
`src/code/server/sv_zmq.c`.

Representative recovered shape:

```c
// conceptual reconstruction, not checked-in engine C source
int encoder_base_t::encode(unsigned char **data, size_t size)
{
	while (bytes_staged == 0) {
		if (in_progress && close_after_body)
			msg_close(in_progress);
		next_step();
	}
	return copy_or_expose_staged_bytes(data, size);
}

int v2_decoder_t::flags_ready()
{
	msg_flags = 0;
	if (flags & MORE)
		msg_flags |= ZMQ_MSG_MORE;
	if (flags & COMMAND)
		msg_flags |= ZMQ_MSG_COMMAND;
	next_step = (flags & LARGE) ? eight_byte_size_ready : one_byte_size_ready;
}
```

## Inference Boundary

This pass does not rename adjacent NULL/PLAIN mechanism lifecycle helpers. The
codec constructors are referenced from the mechanism-greeting branch only as
call-site evidence; mechanism ownership remains for a later pass.

## Verification

Local verification for this pass:

- `Get-Content -Raw references/analysis/quakelive_symbol_aliases.json | ConvertFrom-Json | Out-Null`
- `python -m pytest -q tests/test_platform_services.py::test_zmq_codec_round_394_aliases_are_pinned`
- `python -m pytest -q tests/test_platform_services.py::test_zmq_codec_round_394_aliases_are_pinned tests/test_platform_services.py::test_zmq_stream_engine_state_machine_round_393_aliases_are_pinned tests/test_platform_services.py::test_zmq_stream_engine_peer_round_392_aliases_are_pinned tests/test_platform_services.py::test_zmq_tcp_socket_and_endpoint_round_391_aliases_are_pinned tests/test_platform_services.py::test_zmq_tcp_listener_round_390_aliases_are_pinned tests/test_platform_services.py::test_zmq_tcp_connecter_round_379_aliases_are_pinned tests/test_platform_services.py::test_zmq_options_default_and_mask_vector_round_378_aliases_are_pinned tests/test_platform_services.py::test_zmq_poller_base_io_object_round_377_aliases_are_pinned tests/test_platform_services.py::test_zmq_public_api_aliases_and_round_365_evidence_are_pinned`
- `python -m pytest -q tests/test_platform_services.py::test_server_zmq_runtime_reconstructs_retail_publication_and_rcon_owners tests/test_server_full_parity_gate.py::test_server_full_parity_gate_writes_status_artifact`

## Parity Estimate

- Focused ZMQ codec-layer mapping:
  **before 35% -> after 88%**.
- ZMQ-related source reconstruction confidence, including retained
  publication/RCON ownership, public wrappers, socket/message helpers,
  command-delivery support, queue backing-store evidence, object lifecycle
  ownership, event-loop timer/fd-watch wiring, option/default storage, TCP
  connecter reconnect/stream-engine handoff, TCP listener bind/accept handoff,
  shared TCP/IP helper wiring, stream-engine class-edge/peer-address helpers,
  stream-engine message-state callbacks, and raw/v1/v2 codec wiring:
  **before 87.7% -> after 88.3%**.
- Overall Quake Live source parity:
  **before 55.57% -> after 55.58%**.
