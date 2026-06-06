# Quake Live ZMQ/CZMQ Mapping Round 416

Date: 2026-06-06

## Scope

This pass closes the default ZMQ object-command and poll-event assertion
surface left intentionally unnamed by earlier io-thread/reaper mapping.  Round
376 pinned the live io-thread and reaper constructors, destructors, command
drains, stop/reap/reaped overrides, and command send helpers.  Round 416 adds
the base/default fail-fast handlers that fill the remaining object and
`i_poll_events` vtable slots.

Canonical evidence:

- Binary Ninja HLIL:
  `references/hlil/quakelive/quakelive_steam.exe/quakelive_steam.exe_hlil_split/quakelive_steam.exe_hlil_part01.txt`
- RTTI/vtable evidence:
  `references/hlil/quakelive/quakelive_steam.exe/quakelive_steam.exe_hlil_split/quakelive_steam.exe_hlil_part06.txt`
- Ghidra function inventory:
  `references/reverse-engineering/ghidra/quakelive_steam/functions.csv`
- Companion pass:
  `docs/reverse-engineering/quakelive_steam_mapping_round_376.md`

## Alias Reconstruction

This pass added 20 aliases:

| symbol | alias | confidence | evidence |
|---|---|---|---|
| `sub_40CF60` | `zmq_io_thread_t_out_event_assert` | High | `io_thread_t` `i_poll_events` vtable slot after `in_event`; body asserts `false` at `io_thread.cpp:0x54`. |
| `sub_40CFB0` | `zmq_io_thread_t_timer_event_assert` | High | `io_thread_t` `i_poll_events` timer slot; body asserts `false` at `io_thread.cpp:0x5A`. |
| `sub_40D2E0` | `zmq_reaper_t_out_event_assert` | High | `reaper_t` `i_poll_events` vtable slot after `in_event`; body asserts `false` at `reaper.cpp:0x59`. |
| `sub_40D330` | `zmq_reaper_t_timer_event_assert` | High | `reaper_t` `i_poll_events` timer slot; body asserts `false` at `reaper.cpp:0x5E`. |
| `sub_40DA50` | `zmq_object_t_process_stop_assert` | High | Base `object_t` vtable slot 1, reached by command opcode `0`; body asserts `false` at `object.cpp:0x157`. |
| `sub_40DAA0` | `zmq_object_t_process_plug_assert` | High | Base `object_t` vtable slot 2, reached by command opcode `1` and then followed by the sequence-number slot; body asserts `false` at `object.cpp:0x15C`. |
| `sub_40DAF0` | `zmq_object_t_process_own_assert` | High | Base `object_t` vtable slot 3, reached by command opcode `2`; body asserts `false` at `object.cpp:0x161`. |
| `sub_40DB40` | `zmq_object_t_process_attach_assert` | High | Base `object_t` vtable slot 4, reached by command opcode `3`; body asserts `false` at `object.cpp:0x166`. |
| `sub_40DB90` | `zmq_object_t_process_bind_assert` | High | Base `object_t` vtable slot 5, reached by command opcode `4` and overridden by `socket_base_t::process_bind`; body asserts `false` at `object.cpp:0x16B`. |
| `sub_40DBE0` | `zmq_object_t_process_activate_read_assert` | High | Base `object_t` vtable slot 6, reached by command opcode `5`; body asserts `false` at `object.cpp:0x170`. |
| `sub_40DC30` | `zmq_object_t_process_activate_write_assert` | High | Base `object_t` vtable slot 7, reached by command opcode `6`; body asserts `false` at `object.cpp:0x175`. |
| `sub_40DC80` | `zmq_object_t_process_hiccup_assert` | High | Base `object_t` vtable slot 8, reached by command opcode `7`; body asserts `false` at `object.cpp:0x17A`. |
| `sub_40DCD0` | `zmq_object_t_process_pipe_term_assert` | High | Base `object_t` vtable slot 9, reached by command opcode `8`; body asserts `false` at `object.cpp:0x17F`. |
| `sub_40DD20` | `zmq_object_t_process_pipe_term_ack_assert` | High | Base `object_t` vtable slot 10, reached by command opcode `9`; body asserts `false` at `object.cpp:0x184`. |
| `sub_40DD70` | `zmq_object_t_process_term_req_assert` | High | Base `object_t` vtable slot 11, reached by command opcode `0xA`; body asserts `false` at `object.cpp:0x189`. |
| `sub_40DDC0` | `zmq_object_t_process_term_assert` | High | Base `object_t` vtable slot 12, reached by command opcode `0xB`; body asserts `false` at `object.cpp:0x18E`. |
| `sub_40DE10` | `zmq_object_t_process_term_ack_assert` | High | Base `object_t` vtable slot 13, reached by command opcode `0xC`; body asserts `false` at `object.cpp:0x193`. |
| `sub_40DE60` | `zmq_object_t_process_reap_assert` | High | Base `object_t` vtable slot 14, reached by command opcode `0xD` and overridden by `reaper_t::process_reap`; body asserts `false` at `object.cpp:0x198`. |
| `sub_40DEB0` | `zmq_object_t_process_reaped_assert` | High | Base `object_t` vtable slot 15, reached by command opcode `0xE` and overridden by `reaper_t::process_reaped`; body asserts `false` at `object.cpp:0x19D`. |
| `sub_40DF00` | `zmq_object_t_process_seqnum_assert` | High | Base `object_t` vtable slot 16, reached directly by command opcode `0xF` and as the post-handler sequence-number callback for opcodes `1..4`; body asserts `false` at `object.cpp:0x1A2`. |

## Observed Facts

- `zmq_command_t_process` switches over command opcodes `0..0xF` and dispatches
  to consecutive object vtable slots from `+0x04` through `+0x40`.
- The existing send helpers pin several command opcodes independently:
  `send_plug` emits opcode `1`, `send_own` emits opcode `2`, `send_bind` emits
  opcode `4`, `send_activate_read` emits opcode `5`, `send_activate_write`
  emits opcode `6`, `send_pipe_term` emits opcode `8`,
  `send_pipe_term_ack` emits opcode `9`, and `send_term_ack` emits opcode
  `0xC`.
- For opcodes `1..4`, the retail dispatcher calls the command-specific handler
  and then the slot at `+0x40`, which identifies the tail slot as
  `process_seqnum`.
- `socket_base_t`, `own_t`, `pipe_t`, `reaper_t`, `session_base_t`,
  `tcp_listener_t`, and `tcp_connecter_t` vtables override only the slots they
  can legally receive.  The shared `object_t` defaults are retained as
  fail-fast assertion handlers.
- The io-thread and reaper `i_poll_events` subobject vtables override only
  `in_event`.  Their `out_event` and `timer_event` slots point at local
  fail-fast assertion handlers rather than the generic `io_object_t` defaults,
  preserving source-file-specific assertion lines.

## Source Reconstruction Shape

The retail command surface now supports this base-class shape:

```cpp
class object_t {
public:
	virtual ~object_t();
	virtual void process_stop();
	virtual void process_plug();
	virtual void process_own(own_t *object);
	virtual void process_attach(i_engine *engine);
	virtual void process_bind(pipe_t *pipe);
	virtual void process_activate_read();
	virtual void process_activate_write(uint64_t msgs_read);
	virtual void process_hiccup(void *pipe);
	virtual void process_pipe_term();
	virtual void process_pipe_term_ack();
	virtual void process_term_req(own_t *object);
	virtual void process_term(int linger);
	virtual void process_term_ack();
	virtual void process_reap(socket_base_t *socket);
	virtual void process_reaped();
	virtual void process_seqnum();
};
```

The bodies named in this round are the base/default assertion implementations.
Concrete implementations remain owned by the already mapped `socket_base_t`,
`own_t`, `pipe_t`, `reaper_t`, session, listener, and connecter aliases.

## Inference Boundary

- `process_attach` is named from the command-dispatch slot order used by the
  upstream ZMQ object command surface and its neighboring payload-bearing slots.
  No retail send-helper alias for opcode `3` is promoted in this pass.
- The assertion aliases are behavioral identities for the retail fail-fast
  default methods.  They do not imply these handlers should be reached during a
  valid command flow.
- Earlier notes that left these rows unnamed were conservative at the time; this
  round supersedes that gap with RTTI/vtable and command-dispatch evidence.

## Verification

- `Get-Content -Raw references/analysis/quakelive_symbol_aliases.json | ConvertFrom-Json | Out-Null`
- `python -m pytest -q tests/test_platform_services.py::test_zmq_object_default_command_round_416_aliases_are_pinned`
- `python -m pytest -q tests/test_platform_services.py -k zmq`

No runtime launch was needed; this was a static mapping pass over committed
HLIL/Ghidra evidence.

## Parity Estimate

- Focused ZMQ object-command default callback surface confidence:
  **before 35% -> after 96%**.
- ZMQ-related source reconstruction confidence:
  **before 93.4% -> after 93.6%**.
- Overall Quake Live source parity:
  **before 55.79% -> after 55.80%**.
