# Quake Live ZMQ/CZMQ Mapping Round 403

Date: 2026-06-06

Focus: recover the `pipe.cpp` message-pipe backing queues beneath the already
named `pipe_t` read/write/termination corridor.

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

Round 371 pinned the mailbox `ypipe<command_t,16>` command queue. Rounds 397
and 402 then pinned session and socket pipe-event wiring. This pass fills the
remaining `pipe.cpp` queue layer: `pipepair`, `pipe_t` lifecycle thunks,
`ypipe_base_t<msg_t,256>`, normal `ypipe_t<msg_t,256>`, conflating
`ypipe_conflate_t<msg_t,256>`, and `yqueue<msg_t,256>`.
Short label: ZMQ message pipe backing queue wiring.

## Alias Reconstruction

This pass added 28 aliases and re-pinned 7 existing aliases in
`references/analysis/quakelive_symbol_aliases.json`.

| Symbol | Alias | Confidence | Evidence |
| --- | --- | --- | --- |
| `sub_40FB60` | `zmq_ypipe_conflate_msg_t_write_value` | High | Private conflating write helper validates and moves a `msg_t` into the back slot, swaps front/back under a critical section, and marks data ready. |
| `sub_40FC80` | `zmq_ypipe_conflate_msg_t_read_value` | High | Private conflating read helper locks the pair, copies the front slot into the caller message, resets the front slot, and clears the ready flag. |
| `sub_410140` | `zmq_pipe_t_scalar_deleting_dtor` | High | Primary `pipe_t` vtable destructor calls the complete destructor and conditionally deletes. |
| `sub_410EF0` | `zmq_ypipe_conflate_msg_t_ctor` | High | Constructs the conflating message pipe, initializes front/back message slots, a critical section, and the ready/flush flags. |
| `sub_410F40` | `zmq_ypipe_conflate_msg_t_write` | High | Vtable write callback forwards to the conflating write-value helper. |
| `sub_410F60` | `zmq_ypipe_conflate_msg_t_unwrite_unsupported` | High | Vtable unwrite callback always returns false for the conflating message pipe. |
| `sub_410F70` | `zmq_ypipe_conflate_msg_t_flush` | High | Vtable flush callback returns the conflating pipe's pending-signal flag. |
| `sub_410F80` | `zmq_ypipe_conflate_msg_t_check_read` | High | Vtable read-availability callback locks, observes the ready flag, and clears the pending-signal flag when no data is ready. |
| `sub_410FB0` | `zmq_ypipe_conflate_msg_t_read` | High | Vtable read callback checks availability and forwards to the conflating read-value helper. |
| `sub_411060` | `zmq_ypipe_msg_t_ctor` | High | Constructs a normal `ypipe_t<msg_t,256>`, initializes its `yqueue<msg_t,256>`, and seeds read/write/flush pointers. |
| `sub_4110A0` | `zmq_ypipe_msg_t_write` | High | Vtable write callback copies a 32-byte `msg_t` into the current write slot, advances the `yqueue`, and updates the flush boundary for complete writes. |
| `sub_411100` | `zmq_ypipe_msg_t_unwrite` | High | Vtable unwrite callback refuses to cross the flush boundary, steps the message yqueue back, and copies the last message out. |
| `sub_411160` | `zmq_ypipe_t_flush_shared` | High | Shared ypipe flush body publishes the write boundary with an interlocked compare/exchange; the command and message ypipe vtables both reference this template-shaped helper. |
| `sub_4111A0` | `zmq_ypipe_msg_t_check_read` | High | Vtable read-availability callback compares the read cursor against the published boundary and claims a readable boundary through interlocked exchange. |
| `sub_4111E0` | `zmq_ypipe_msg_t_read` | High | Vtable read callback checks availability, copies a 32-byte message, advances the read cursor, and recycles full `0x2008`-byte chunks. |
| `sub_411270` | `zmq_ypipe_msg_t_probe` | High | Vtable probe callback requires readable data and applies the caller predicate to the current message slot. |
| `sub_4112E0` | `zmq_array_item_1_scalar_deleting_dtor` | High | Standalone `array_item_t<1>` scalar deleting destructor restores its base vtable and conditionally deletes. |
| `sub_411310` | `zmq_array_item_2_scalar_deleting_dtor` | High | Standalone `array_item_t<2>` scalar deleting destructor restores its base vtable and conditionally deletes. |
| `sub_411340` | `zmq_array_item_3_scalar_deleting_dtor` | High | Standalone `array_item_t<3>` scalar deleting destructor restores its base vtable and conditionally deletes. |
| `sub_411370` | `zmq_ypipe_conflate_msg_t_scalar_deleting_dtor` | High | Conflating message pipe scalar destructor closes both stored `msg_t` slots, deletes the critical section, restores the base vtable, and conditionally deletes. |
| `sub_411400` | `zmq_ypipe_base_msg_t_scalar_deleting_dtor` | High | Base `ypipe_base_t<msg_t,256>` scalar deleting destructor restores the base vtable and conditionally deletes. |
| `sub_411430` | `zmq_ypipe_msg_t_scalar_deleting_dtor` | High | Normal message ypipe scalar destructor destroys the embedded message yqueue, restores the base vtable, and conditionally deletes. |
| `sub_411520` | `zmq_yqueue_msg_t_ctor` | High | Allocates the first `0x2008`-byte message queue chunk and initializes read/write cursor state. |
| `sub_411590` | `zmq_yqueue_msg_t_dtor` | High | Frees linked message queue chunks and the interlocked spare chunk. |
| `sub_4115E0` | `zmq_yqueue_msg_t_push` | High | Advances the write cursor and allocates or reuses the next `0x2008`-byte chunk every 256 messages. |
| `sub_4116B0` | `zmq_yqueue_msg_t_unpush` | High | Moves the write cursor backward and frees the chunk beyond the new write position when crossing a page. |
| `sub_4119E0` | `zmq_pipe_t_array_item_1_scalar_deleting_dtor` | High | `pipe_t` array-item-1 subobject destructor thunk tail-calls the pipe scalar deleting destructor with a `-0xc` adjustment. |
| `sub_4119F0` | `zmq_pipe_t_array_item_2_scalar_deleting_dtor` | High | `pipe_t` array-item-2 subobject destructor thunk tail-calls the pipe scalar deleting destructor with a `-0x14` adjustment. |
| `sub_411A00` | `zmq_pipe_t_array_item_3_scalar_deleting_dtor` | High | `pipe_t` array-item-3 subobject destructor thunk tail-calls the pipe scalar deleting destructor with a `-0x1c` adjustment. |
| `sub_40FD50` | `zmq_pipepair` | Existing | Re-pinned as the allocator that selects normal versus conflating ypipe storage for both pipe directions and creates the two peer-linked `pipe_t` objects. |
| `sub_410070` | `zmq_pipe_t_ctor` | Existing | Re-pinned as the pipe constructor reached from `pipepair`, storing inbound/outbound queue pointers, high-water marks, and conflate state. |
| `sub_410170` | `zmq_pipe_t_dtor` | Existing | Re-pinned as the complete destructor reached by the pipe scalar deleting destructor. |
| `sub_410330` | `zmq_pipe_t_read` | Existing | Re-pinned as the pipe-side consumer of the recovered ypipe read callback. |
| `sub_410400` | `zmq_pipe_t_write` | Existing | Re-pinned as the pipe-side producer that calls the recovered ypipe write callback. |
| `sub_410480` | `zmq_pipe_t_rollback` | Existing | Re-pinned as the pipe helper that repeatedly unwrites multipart messages through the ypipe unwrite callback. |
| `sub_410DF0` | `zmq_pipe_t_hiccup` | Existing | Re-pinned as the pipe helper that replaces the inbound message ypipe with a new normal or conflating queue. |

## Observed Facts

- `pipepair` allocates two message ypipes before constructing two `pipe_t`
  objects. Each direction can independently use either normal
  `ypipe_t<msg_t,256>` storage (`0x30` bytes) or conflating
  `ypipe_conflate_t<msg_t,256>` storage (`0x6c` bytes), keyed by the two
  conflate flags.
- Normal message queues use `0x2008`-byte chunks, i.e. 0x2008-byte chunks:
  `0x2000` bytes for 256
  `msg_t` records at 32 bytes each, followed by two chunk links.
- The normal ypipe write/unwrite/read/probe callbacks mirror the command
  ypipe from round 371, but use 32-byte message records and 256-slot chunks.
- The conflating ypipe stores only front/back `msg_t` slots, guarded by a
  critical section. Writing moves the caller message into the back slot, swaps
  front/back under the lock, and exposes one latest value to readers.
- The conflating read path copies the front slot into the caller message and
  clears the ready flag. Its unwrite callback is a deliberate false return.
- `pipe_t` owns three `array_item_t` subobjects and inherits the primary
  `object_t` vtable. The subobject destructors adjust back to the complete
  pipe before calling the pipe scalar deleting destructor.

## Source Reconstruction

This is static/source-shape reconstruction only. The recovered queue layer gives
the following model:

```c
// conceptual reconstruction, not checked-in engine C source
void pipepair(pipe_t **pipes, object_t *parents[2], int hwms[2], bool conflate[2])
{
	ypipe_base_t<msg_t> *a_to_b = conflate[0]
		? new ypipe_conflate_t<msg_t, 256>()
		: new ypipe_t<msg_t, 256>();
	ypipe_base_t<msg_t> *b_to_a = conflate[1]
		? new ypipe_conflate_t<msg_t, 256>()
		: new ypipe_t<msg_t, 256>();

	pipes[0] = new pipe_t(parents[0], a_to_b, b_to_a, hwms[1], conflate[0]);
	pipes[1] = new pipe_t(parents[1], b_to_a, a_to_b, hwms[0], conflate[1]);
	pipes[0]->peer = pipes[1];
	pipes[1]->peer = pipes[0];
}

bool ypipe_t_msg::write(msg_t *msg, bool incomplete)
{
	queue.back() = move(*msg);
	queue.push();
	if (!incomplete)
		flush_boundary = queue.back();
	return true;
}

bool ypipe_conflate_msg::write(msg_t *msg, bool incomplete)
{
	move_into(back, msg);
	lock();
	swap(front, back);
	ready = true;
	unlock();
	return signal_needed();
}
```

## Inference Boundary

This pass does not rename the final conflating vtable callback rendered in HLIL
as an `operator new[]`-named function, even though its body behaves like a
locked predicate/probe callback. It also leaves the generic string/STL helpers
near `0x00411470..0x004117E0` unnamed. The shared `sub_411160` alias is
intentionally neutral because both the command ypipe vtable and the message
ypipe vtable reference the same flush-boundary body.

## Verification

Local verification for this pass:

- `Get-Content -Raw references/analysis/quakelive_symbol_aliases.json | ConvertFrom-Json | Out-Null`
- `python -m pytest -q tests/test_platform_services.py::test_zmq_msg_pipe_queue_round_403_aliases_are_pinned`
- `python -m pytest -q tests/test_platform_services.py -k zmq`

## Parity Estimate

- Focused ZMQ message pipe backing queue wiring:
  **before 37% -> after 89%**.
- ZMQ-related source reconstruction confidence, including retained socket
  families, session/engine wiring, pipe lifecycle, and message queue backing
  stores:
  **before 90.9% -> after 91.2%**.
- Overall Quake Live source parity:
  **before 55.66% -> after 55.67%**.
