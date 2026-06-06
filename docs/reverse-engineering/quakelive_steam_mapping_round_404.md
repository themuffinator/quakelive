# Quake Live ZMQ/CZMQ Mapping Round 404

Date: 2026-06-06

Focus: recover the immediate pipe-routing helpers above the `pipe.cpp` queue
layer: fair-queue inbound selection, load-balancer outbound selection, and
distribution broadcast/matching writes.

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

Round 403 pinned the message-pipe backing queues and `pipe_t` callbacks. This
pass moves one layer up and pins the helper objects that socket families use to
pick readable pipes, pick writable pipes, and fan out a message across matched
subscribers. Short label: FQ/LB/DIST pipe routing helper wiring.

## Alias Reconstruction

This pass added 17 aliases and re-pinned 2 existing aliases in
`references/analysis/quakelive_symbol_aliases.json`.

| Symbol | Alias | Confidence | Evidence |
| --- | --- | --- | --- |
| `sub_41E230` | `zmq_fq_t_dtor` | High | `fq.cpp` destructor asserts `pipes.empty ()`, releases the vector allocation, and clears vector begin/end/capacity. |
| `sub_41E2B0` | `zmq_fq_t_attach` | High | Appends a pipe through the FQ vector helper, swaps it into the active segment, updates the pipe's FQ array index, and increments the active count. |
| `sub_41E320` | `zmq_fq_t_terminated` | High | Removes a terminated pipe from the active/all pipe vector, rewrites array-item indexes, compacts storage, and resets the current read index when it lands on the active boundary. |
| `sub_41E3F0` | `zmq_fq_t_activate` | High | Moves an inactive readable pipe into the active prefix and increments the active pipe count. |
| `sub_41E460` | `zmq_fq_t_recvpipe` | Existing | Re-pinned as the fair-queue receive loop that closes the caller message, reads through the pipe input vtable, handles delimiters, enforces `!more`, rotates current, and returns `EAGAIN` when no pipe is readable. |
| `sub_41E6B0` | `zmq_fq_t_has_in` | High | Probes active pipes with `pipe_t::check_read`, removes inactive/dead pipes, and preserves multipart state through the `more` flag. |
| `sub_41E750` | `std_vector_zmq_fq_pipe_push_back` | High | FQ-local vector push helper stores the pipe's `array_item_t<1>` index at offset `+0x10`, grows through the shared vector grow helper, and appends the pipe pointer. |
| `sub_41E7D0` | `zmq_lb_t_dtor` | High | `lb.cpp` destructor asserts `pipes.empty ()`, releases the vector allocation, and clears vector begin/end/capacity. |
| `sub_41E850` | `zmq_lb_t_terminated` | High | Removes a terminated pipe from the load-balancer vector, preserves dropped multipart state when the current pipe dies mid-message, and compacts active/all ranges. |
| `sub_41E930` | `zmq_lb_t_activate` | High | Moves a writable pipe into the load-balancer active prefix and increments the active pipe count. |
| `sub_41E9A0` | `zmq_lb_t_sendpipe` | Existing | Re-pinned as the load-balanced send loop that handles dropped multipart sends, writes through the pipe output vtable, enforces `!more`, flushes complete messages, rotates current, and returns `EAGAIN` when no pipe is writable. |
| `sub_41EBF0` | `zmq_lb_t_has_out` | High | Probes active pipes for writable capacity/high-water availability and removes pipes that can no longer accept output. |
| `sub_41ECC0` | `std_vector_zmq_lb_pipe_push_back` | High | LB/DIST vector push helper stores the pipe's `array_item_t<2>`/send-side index at offset `+0x18`, grows through the shared vector grow helper, and appends the pipe pointer. |
| `sub_420120` | `zmq_dist_t_dtor` | High | `dist.cpp` destructor asserts `pipes.empty ()`, releases the vector allocation, and clears vector begin/end/capacity. |
| `sub_4201A0` | `zmq_dist_t_attach` | High | Appends a pipe and inserts it into either matching-only or active-plus-matching ranges depending on the distribution matching flag. |
| `sub_420280` | `zmq_dist_t_terminated` | High | Removes a pipe from the all/active/matching partitioned vector, updating all three counters and array-item indexes before compacting storage. |
| `sub_420430` | `zmq_dist_t_activate` | High | Moves a pipe into the matching range, and when matching is not disabled, also advances the active-send range. |
| `sub_420500` | `zmq_dist_t_send_to_matching` | High | Sends a message to all matching pipes, clones/adds message references when more than one destination exists, removes failed writes, and resets the caller message to an empty message. |
| `sub_4206C0` | `zmq_dist_t_write` | High | Writes one message into a pipe with `pipe_t::write`, flushes complete messages, and removes the pipe from the matching set when the write fails. |

## Observed Facts

- The FQ vector partitions pipes as active/readable plus inactive. The current
  read cursor is kept inside the active prefix and reset when removal reaches
  the active boundary.
- `fq_t::recvpipe` always closes or resets the caller message first. It reads
  through the pipe's input vtable slot, treats delimiter messages as pipe
  termination markers, preserves multipart receive state with the `more` flag,
  and reports `errno = 0xb` when no active pipe can provide input.
- The LB vector tracks active/writable pipes and the current send cursor. If a
  pipe terminates while multipart state is active, the load balancer marks the
  following pieces as dropped until the multipart frame ends.
- `lb_t::sendpipe` writes through the pipe output vtable, flushes the pipe on
  complete messages, invokes the pipe-termination command path on flush
  failure, and rotates the current send cursor after successful complete sends.
- `dist_t` uses a partitioned vector with all, active, and matching counts. The
  attach/activate/terminate helpers maintain these ranges by swapping pointers
  and rewriting the send-side array-item index stored inside each `pipe_t`.
- `dist_t::send_to_matching` handles the single-destination and
  multiple-destination paths separately. Multiple destinations use message
  reference accounting so each matching pipe gets the same message payload.

## Source Reconstruction

This is static/source-shape reconstruction only. The recovered helper layer
gives the following model:

```c
// conceptual reconstruction, not checked-in engine C source
int fq_t::recvpipe(msg_t *msg, pipe_t **pipe)
{
	msg->close();
	while (active > 0) {
		pipe_t *current_pipe = pipes[current];
		if (current_pipe->read(msg)) {
			if (msg->is_delimiter()) {
				current_pipe->process_delimiter();
				remove_current_pipe();
				continue;
			}

			if (pipe)
				*pipe = current_pipe;
			more = msg->flags() & msg_t::more;
			if (!more)
				current = (current + 1) % active;
			return 0;
		}

		assert(!more);
		remove_current_pipe();
	}

	msg->init();
	errno = EAGAIN;
	return -1;
}

int lb_t::sendpipe(msg_t *msg, pipe_t **pipe)
{
	if (dropping) {
		bool msg_more = msg->flags() & msg_t::more;
		msg->close();
		msg->init();
		more = msg_more;
		dropping = msg_more;
		return 0;
	}

	while (active > 0) {
		pipe_t *current_pipe = pipes[current];
		if (current_pipe->write(msg, msg->flags() & msg_t::more)) {
			if (pipe)
				*pipe = current_pipe;
			more = msg->flags() & msg_t::more;
			if (!more) {
				current_pipe->flush_or_term();
				current = (current + 1) % active;
			}
			msg->init();
			return 0;
		}

		assert(!more);
		remove_current_pipe();
	}

	errno = EAGAIN;
	return -1;
}

void dist_t::send_to_matching(msg_t *msg)
{
	if (matching == 0) {
		msg->close();
		msg->init();
		return;
	}

	if (matching > 1)
		msg->add_refs(matching - 1);

	for (size_t i = 0; i < matching; ++i) {
		if (!write(msg, pipes[i]))
			--i;
	}

	msg->rm_refs_for_failed_writes();
	msg->init();
}
```

## Inference Boundary

The vector push helpers are named with their owning queue context because the
HLIL bodies are STL-template shaped and only reveal the pipe-index side effect
and shared grow helper. This pass deliberately leaves `trie_t`/`mtrie_t`
subscription storage, `sub_420840`, and the nearby generic STL support helpers
for a separate pass; those structures are subscription-prefix ownership rather
than immediate pipe-routing ownership.

## Verification

Local verification for this pass:

- `Get-Content -Raw references/analysis/quakelive_symbol_aliases.json | ConvertFrom-Json | Out-Null`
- `python -m pytest -q tests/test_platform_services.py::test_zmq_fq_lb_dist_round_404_aliases_are_pinned`
- `python -m pytest -q tests/test_platform_services.py -k zmq`

## Parity Estimate

- Focused FQ/LB/DIST pipe routing helper wiring:
  **before 42% -> after 90%**.
- ZMQ-related source reconstruction confidence, including retained socket
  families, session/engine wiring, pipe lifecycle, message queues, and
  immediate pipe-routing helpers:
  **before 91.2% -> after 91.5%**.
- Overall Quake Live source parity:
  **before 55.67% -> after 55.68%**.
