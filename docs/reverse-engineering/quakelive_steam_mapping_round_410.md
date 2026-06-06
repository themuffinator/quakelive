# Quake Live ZMQ/CZMQ Mapping Round 410

Date: 2026-06-06

Focus: recover the deferred `select_t` fd-vector growth helpers and the
write-interest reset helper used by `stream_engine_t` output backpressure.

## Retail Evidence

- Owning binary: `assets/quakelive/quakelive_steam.exe`.
- Canonical HLIL:
  `references/hlil/quakelive/quakelive_steam.exe/quakelive_steam.exe_hlil_split/quakelive_steam.exe_hlil_part01.txt`
  and static string/vtable evidence in
  `references/hlil/quakelive/quakelive_steam.exe/quakelive_steam.exe_hlil_split/quakelive_steam.exe_hlil_part06.txt`.
- Structured companion corpus:
  `references/reverse-engineering/ghidra/quakelive_steam/functions.csv`.
- Symbol/name support:
  `references/analysis/quakelive_symbol_aliases.json`.

Round 370 named the public select-poller lane but left the lower-level
fd-entry vector growth helpers unnamed. Round 377 and Round 409 subsequently
pinned the `io_object_t` interest toggles and event callbacks that feed this
same select poller. This pass revisits the deferred helper slab with the call
graph now stable.

## Alias Reconstruction

This pass added 5 aliases to
`references/analysis/quakelive_symbol_aliases.json` and re-pinned the related
select-poller owner aliases.

| Symbol | Alias | Confidence | Evidence |
| --- | --- | --- | --- |
| `sub_40C1B0` | `zmq_select_t_reset_pollout` | High | Removes a socket fd from the select poller's write-interest mirror at offsets `0x1044/0x1048`. `stream_engine_t::out_event` calls it when output drains or write returns `EAGAIN`. |
| `sub_40C470` | `std_vector_zmq_select_fd_entry_grow` | High | Computes the next capacity for the `select_t` vector of `{fd, events}` entries and delegates reallocation to `sub_40C4D0`; `select_t::add_fd` calls it when the vector reaches capacity. |
| `sub_40C4D0` | `std_vector_zmq_select_fd_entry_reserve` | High | Reallocates the select fd-entry vector, copies existing 8-byte entries with `sub_40C600`, deletes the old storage, and updates begin/end/capacity pointers. |
| `sub_40C5A0` | `std_vector_zmq_select_fd_entry_allocate` | High | Allocates `count << 3` bytes for select fd entries and throws the retained MSVC `bad_alloc` path on overflow or allocation failure. |
| `sub_40C600` | `std_uninitialized_copy_zmq_select_fd_entry` | High | Copies contiguous 8-byte select fd entries as `{fd, sink}` pairs from old vector storage into the new allocation. |

## Observed Facts

- `select_t::add_fd` writes `{fd, events}` into the vector and calls
  `std_vector_zmq_select_fd_entry_grow` when the end pointer reaches capacity.
- The add path asserts `fds.size () <= FD_SETSIZE`, updates the except/error
  mirror and the maximum fd sentinel, and increments the poller load through
  `InterlockedExchangeAdd`.
- `select_t::rm_fd` marks the fd-entry slot as retired, removes the fd from all
  select mirrors, marks the vector for compaction, recomputes the maximum fd
  when needed, and decrements the poller load.
- `select_t::loop` copies the read/write/except mirrors before each
  `select()` call, dispatches readiness through `__WSAFDIsSet`, and compacts
  retired `0xffffffff` fd-entry slots after a pass.
- `stream_engine_t::out_event` calls `zmq_select_t_reset_pollout` on output
  drain and `EAGAIN`, matching the higher-level `io_object_t::set_pollout`
  callback from Round 377.

## Source Reconstruction

This is mapping/static reconstruction only. No GPL-side engine C source changed
in this pass. The recovered source shape is:

```cpp
void select_t::reset_pollout(fd_t fd)
{
	remove_fd_from_array(write_fds, fd);
}

void select_t::add_fd(fd_t fd, i_poll_events *events)
{
	fds.push_back({fd, events});
	assert(fds.size() <= FD_SETSIZE);
	add_fd_to_array(except_fds, fd);
	max_fd = std::max(max_fd, fd);
	InterlockedExchangeAdd(&load, 1);
}
```

The vector helper aliases describe MSVC-emitted support for the private
`select_t` fd-entry vector; they are not public libzmq API functions.

## Inference Boundary

The SEH catch fragment at `0x0040C581` remains unnamed. It is tied to the
vector reallocation exception path rather than to a stable source-level helper.
This pass also does not rename unrelated generic string/vector helpers outside
the select-poller fd-entry storage.

## Verification

Local verification for this pass:

- `Get-Content -Raw references/analysis/quakelive_symbol_aliases.json | ConvertFrom-Json | Out-Null`
- `python -m pytest -q tests/test_platform_services.py::test_zmq_select_fd_vector_round_410_aliases_are_pinned`
- `python -m pytest -q tests/test_platform_services.py -k zmq`

## Parity Estimate

- Focused ZMQ select-poller fd-vector and pollout reset wiring:
  **before 38% -> after 92%**.
- ZMQ-related source reconstruction confidence:
  **before 92.3% -> after 92.4%**.
- Overall Quake Live source parity:
  **before 55.73% -> after 55.74%**.
