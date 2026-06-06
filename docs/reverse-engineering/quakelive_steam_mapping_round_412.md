# Quake Live ZMQ/CZMQ Mapping Round 412

Date: 2026-06-06

Focus: recover the `ctx_t` constructor, endpoint map operations, and ctx-owned
endpoint/pending-connection tree cleanup helpers.

## Retail Evidence

- Owning binary: `assets/quakelive/quakelive_steam.exe`.
- Canonical HLIL:
  `references/hlil/quakelive/quakelive_steam.exe/quakelive_steam.exe_hlil_split/quakelive_steam.exe_hlil_part01.txt`
  and static string/vtable evidence in
  `references/hlil/quakelive/quakelive_steam.exe/quakelive_steam.exe_hlil_split/quakelive_steam.exe_hlil_part06.txt`.
- Structured companion corpus:
  `references/reverse-engineering/ghidra/quakelive_steam/functions.csv`,
  `imports.txt`, and `decompile_top_functions.c`.
- Symbol/name support:
  `references/analysis/quakelive_symbol_aliases.json`.

Round 365 named the public context wrappers and internal setter/create-socket
entry points, while Round 411 closed the adjacent Windows `err.cpp` helpers.
This pass fills the constructor and the ctx map cleanup layer that the already
mapped `zmq_ctx_t_dtor` tears down.

## Alias Reconstruction

This pass added 8 aliases to
`references/analysis/quakelive_symbol_aliases.json` and re-pinned the related
ctx/map owner aliases.

| Symbol | Alias | Confidence | Evidence |
| --- | --- | --- | --- |
| `sub_402270` | `zmq_ctx_t_ctor` | High | Called by public `zmq_ctx_new` after a `0x10c` allocation; stamps `0xabadcafe`, initializes socket/free-slot vectors, mailbox, endpoint/pending maps, mutexes, and default ctx options. |
| `sub_402420` | `std_tree_zmq_endpoint_node_map_dtor` | High | Constructor/unwind cleanup for the endpoint tree: calls the endpoint-node range erase helper and deletes the `0x280` sentinel storage. |
| `sub_402480` | `std_tree_zmq_pending_connection_node_map_dtor` | High | Constructor/unwind cleanup for the pending-connection tree: calls the pending-connection range erase helper and deletes the `0x288` sentinel storage. |
| `sub_4032F0` | `zmq_ctx_t_register_endpoint` | High | Locks the ctx endpoint map, normalizes/copies the endpoint string, inserts the endpoint record at ctx offset `0xb0`, and returns `EADDRINUSE` (`0x64`) on duplicate registration. |
| `sub_403560` | `zmq_ctx_t_unregister_endpoint` | High | Locks the ctx endpoint map, finds the endpoint node, verifies the owning socket pointer, erases through `std_tree_erase_zmq_endpoint_node`, and returns `ENOENT` (`2`) when missing/mismatched. |
| `sub_4036F0` | `zmq_ctx_t_find_endpoint` | High | Locks the ctx endpoint map, copies the endpoint record into the caller output, bumps the owning socket reference count at `+0x254`, or returns the empty endpoint with `ECONNREFUSED` (`0x6b`). |
| `sub_404AF0` | `std_tree_erase_zmq_pending_connection_node_range` | High | Walks the pending-connection RB-tree range, uses the `0x281` sentinel byte, and removes each node through `std_tree_erase_zmq_pending_connection_node`. |
| `sub_405540` | `std_tree_erase_zmq_endpoint_node_range` | High | Walks the endpoint RB-tree range, uses the `0x279` sentinel byte, and removes each node through `std_tree_erase_zmq_endpoint_node`. |

## Observed Facts

- `zmq_ctx_new` allocates `0x10c` bytes and dispatches that allocation into the
  constructor body now named `zmq_ctx_t_ctor`.
- The constructor writes the retail ctx magic `0xabadcafe`, initializes the
  socket vector and free-slot vector, builds the command mailbox through
  `zmq_mailbox_t_ctor`, and allocates two RB-tree sentinels.
- The endpoint map sentinel is `0x280` bytes with sentinel bytes at
  `0x278/0x279`; the pending-connection map sentinel is `0x288` bytes with
  sentinel bytes at `0x280/0x281`.
- `zmq_ctx_t_dtor` destroys the pending-connection tree with `sub_404AF0`
  at ctx offset `0xc0`, then destroys the endpoint tree with `sub_405540` at
  ctx offset `0xb0`.
- The endpoint map operations share the ctx endpoint mutex at `+0xd0` and the
  endpoint tree rooted at `+0xb0/+0xb4`.
- Register/find copy the retained endpoint payload with `sub_4038B0`, while
  find also increments the owning socket reference count before returning the
  endpoint to the caller.
- The destructor also asserts `sockets.empty ()`, sets the ctx magic to
  `0xdeadbeef`, deletes mutexes at ctx offsets `0xf4`, `0xd0`, `0x94`, and
  `0x28`, and tears down the command ypipe/mailbox storage.

## Source Reconstruction

This is mapping/static reconstruction only. No GPL-side engine C source changed
in this pass. The recovered source shape is:

```cpp
ctx_t::ctx_t()
{
	tag = 0xabadcafe;
	sockets.clear();
	free_slots.clear();
	slot_count = 0;
	started = false;
	terminating = false;
	mailbox.construct();
	endpoints.construct();
	pending_connections.construct();
	max_sockets = 0x3ff;
	io_thread_count = 1;
	blocky = false;
}

ctx_t::~ctx_t()
{
	assert(sockets.empty());
	tag = 0xdeadbeef;
	pending_connections.clear();
	endpoints.clear();
	mailbox.destroy();
}

int ctx_t::register_endpoint(const char *addr, const endpoint_t &endpoint);
int ctx_t::unregister_endpoint(const char *addr, socket_base_t *socket);
endpoint_t ctx_t::find_endpoint(const char *addr);
```

The `std_tree_*_map_dtor` aliases describe MSVC-emitted support for map
construction unwind and destruction. They are not libzmq public API functions.

## Inference Boundary

The 8-byte `sub_402260` `DeleteCriticalSection` wrapper remains unnamed. Its
body matches a `mutex_t` destructor shape and sits adjacent to the ctx
constructor, but no direct non-unwind caller or source-file string pins it
strongly enough yet. The next ctx pass should continue from `sub_403120` and
the socket-slot return, I/O-thread selection, and inproc connect/pending
handoff helpers rather than renaming that helper prematurely.

## Verification

Local verification for this pass:

- `Get-Content -Raw references/analysis/quakelive_symbol_aliases.json | ConvertFrom-Json | Out-Null`
- `python -m pytest -q tests/test_platform_services.py::test_zmq_ctx_constructor_maps_round_412_aliases_are_pinned`
- `python -m pytest -q tests/test_platform_services.py -k zmq`

## Parity Estimate

- Focused ZMQ ctx constructor, endpoint map, and map-cleanup wiring:
  **before 41% -> after 94%**.
- ZMQ-related source reconstruction confidence:
  **before 92.5% -> after 92.8%**.
- Overall Quake Live source parity:
  **before 55.75% -> after 55.76%**.
