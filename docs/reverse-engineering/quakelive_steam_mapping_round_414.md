# Quake Live ZMQ/CZMQ Mapping Round 414

Date: 2026-06-06

Focus: recover the MSVC `std::map` and vector helper layer backing the
`ctx_t` endpoint and pending inproc connection maps.

## Retail Evidence

- Owning binary: `assets/quakelive/quakelive_steam.exe`.
- Canonical HLIL:
  `references/hlil/quakelive/quakelive_steam.exe/quakelive_steam.exe_hlil_split/quakelive_steam.exe_hlil_part01.txt`
  and static string evidence in
  `references/hlil/quakelive/quakelive_steam.exe/quakelive_steam.exe_hlil_split/quakelive_steam.exe_hlil_part06.txt`.
- Structured companion corpus:
  `references/reverse-engineering/ghidra/quakelive_steam/functions.csv`.
- Symbol/name support:
  `references/analysis/quakelive_symbol_aliases.json`.

Rounds 412 and 413 named the ctx constructor, endpoint map owners, options
copy/destruction, and inproc pending handoff. This pass names the support-code
band those owners use for the ctx endpoint and pending inproc connection maps:
endpoint tree lookup/insertion/rotation helpers, pending-connection tree
copy/erase/rotation helpers, and the address-mask vector copy/destruction
helpers reached from `options_t`.

## Alias Reconstruction

This pass added 27 aliases to
`references/analysis/quakelive_symbol_aliases.json` and re-pinned the existing
ctx map owner aliases from Rounds 412 and 413.

| Symbol | Alias | Confidence | Evidence |
| --- | --- | --- | --- |
| `sub_404380` | `std_vector_zmq_tcp_address_mask_copy_ctor` | High | Copies 0x24-byte `tcp_address_mask_t` elements and is called by `zmq_options_t_copy_ctor`. |
| `sub_404450` | `std_vector_zmq_tcp_address_mask_dtor` | High | Walks 0x24-byte vector elements, dispatches each element destructor, deletes vector storage, and zeroes the triplet. |
| `sub_404550` | `std_tree_get_or_insert_zmq_endpoint_node` | High | Performs endpoint-map lower_bound, inserts a default endpoint/options payload when absent, and returns the endpoint payload pointer. |
| `sub_404A60` | `std_tree_find_zmq_endpoint_node` | High | Lower-bounds the endpoint tree and returns the matching node or the sentinel when the string key differs. |
| `sub_404C20` | `std_tree_rotate_left_zmq_endpoint_node` | High | Endpoint-tree RB rotation using the `0x279` sentinel flag and right-child promotion. |
| `sub_404C80` | `std_tree_rotate_right_zmq_endpoint_node` | High | Endpoint-tree RB rotation using the `0x279` sentinel flag and left-child promotion. |
| `sub_404CE0` | `std_tree_rightmost_zmq_endpoint_node` | High | Walks right links until the endpoint sentinel flag at `0x279` is set. |
| `sub_404D00` | `std_tree_leftmost_zmq_endpoint_node` | High | Walks left links until the endpoint sentinel flag at `0x279` is set. |
| `sub_404D80` | `std_tree_zmq_pending_connection_node_map_copy_ctor` | High | Allocates a `0x288` pending-map sentinel, marks `0x280/0x281`, and copies a pending tree through `sub_405710`. |
| `sub_405610` | `std_tree_lower_bound_zmq_endpoint_node` | High | Performs endpoint lower_bound against string keys using the `0x279` sentinel layout. |
| `sub_405710` | `std_tree_copy_zmq_pending_connection_node_map` | High | Copies the pending tree into a fresh map header and repairs leftmost/rightmost links. |
| `sub_4057A0` | `std_tree_free_zmq_pending_connection_node_subtree` | High | Recursively destroys pending nodes, their embedded options, and string storage using the `0x281` sentinel flag. |
| `sub_405860` | `std_tree_rotate_left_zmq_pending_connection_node` | High | Pending-tree RB left rotation with the `0x281` sentinel flag. |
| `sub_4058C0` | `std_tree_rotate_right_zmq_pending_connection_node` | High | Pending-tree RB right rotation with the `0x281` sentinel flag. |
| `sub_405920` | `std_tree_rightmost_zmq_pending_connection_node` | High | Walks right links until the pending sentinel flag at `0x281` is set. |
| `sub_405940` | `std_tree_leftmost_zmq_pending_connection_node` | High | Walks left links until the pending sentinel flag at `0x281` is set. |
| `sub_405960` | `std_tree_next_zmq_pending_connection_node` | High | Implements pending-tree iterator increment using right-subtree leftmost or parent climb. |
| `sub_4059C0` | `std_tree_next_zmq_endpoint_node` | High | Implements endpoint-tree iterator increment using the `0x279` sentinel layout. |
| `sub_405A80` | `std_tree_copy_zmq_pending_connection_node_subtree` | High | Recursively allocates and copies pending nodes via `sub_4066F0`. |
| `sub_405B40` | `std_tree_free_zmq_endpoint_node_subtree` | High | Recursively destroys endpoint nodes, embedded options, and string storage using the `0x279` sentinel flag. |
| `sub_405C00` | `std_tree_find_or_insert_zmq_endpoint_node` | High | Implements unique endpoint insertion, returning an existing node when the key already compares equal. |
| `sub_405D90` | `std_tree_insert_zmq_endpoint_node_with_hint` | High | Hint-aware endpoint insertion wrapper that dispatches to `std_tree_insert_zmq_endpoint_node`. |
| `sub_4061B0` | `std_tree_prev_zmq_endpoint_node` | High | Implements endpoint-tree iterator decrement using the `0x279` sentinel layout. |
| `sub_406230` | `std_tree_create_zmq_endpoint_node` | High | Allocates a `0x280` endpoint node, copies the string key, and copy-constructs the embedded endpoint/options payload. |
| `sub_406330` | `std_tree_insert_zmq_pending_connection_node_unique` | High | Finds the pending insertion position by string key and inserts through `std_tree_insert_zmq_pending_connection_node`. |
| `sub_4066F0` | `std_tree_create_zmq_pending_connection_node` | High | Allocates a `0x288` pending node and copy-constructs the pending payload. |
| `sub_406820` | `zmq_ctx_pending_connection_t_copy_ctor` | High | Copies the pending key/options payload plus the two retained pipe pointers at payload offsets `+0x268/+0x26c`. |

## Observed Facts

- Endpoint nodes use a `0x280` allocation and RB bookkeeping bytes at
  `0x278/0x279`; pending-connection nodes use a `0x288` allocation and
  bookkeeping bytes at `0x280/0x281`.
- `zmq_ctx_t_register_endpoint`, `zmq_ctx_t_unregister_endpoint`, and
  `zmq_ctx_t_find_endpoint` all dispatch through the endpoint tree helpers at
  ctx offset `+0xb0`.
- `zmq_ctx_t_pend_connection` stores missing inproc connects through the
  pending tree helper path at ctx offset `+0xc0`; `zmq_ctx_t_connect_pending`
  lower-bounds that pending tree, consumes matching entries, and erases the
  range.
- The endpoint tree's insertion path creates a default `options_t` payload
  when `connect_pending` needs a map `operator[]`-style lookup.
- The pending copy constructor and subtree-copy helpers are compiler-emitted
  support for value-copying pending map payloads. They are still useful
  reconstruction evidence because they expose the pending payload layout.
- The `tcp_address_mask_t` vector helpers are not ctx map nodes, but they are
  reached directly from `zmq_options_t_copy_ctor` and confirm the 0x24-byte
  vector element stride used by the options address-mask fields.

## Source Reconstruction

This is mapping/static reconstruction only. No GPL-side engine C source changed
in this pass. The recovered source shape is:

```cpp
typedef std::map<std::string, endpoint_t> endpoint_map_t;
typedef std::map<std::string, pending_connection_t> pending_connection_map_t;

endpoint_map_t::iterator endpoint_map_t::find_or_insert(const std::string &addr);
endpoint_map_t::iterator endpoint_map_t::find(const std::string &addr);
pending_connection_map_t::iterator pending_connection_map_t::lower_bound(const std::string &addr);

struct pending_connection_t {
	endpoint_t endpoint;
	pipe_t *connect_pipe;
	pipe_t *bind_pipe;
};
```

These names intentionally describe compiler-emitted `std::map` machinery rather
than source-level libzmq API functions. They make the ctx owner functions from
Rounds 412 and 413 readable without pretending the helper layer was handwritten
ZMQ source.

## Inference Boundary

This pass does not rename generic `std::string` allocation, erase, assign, or
comparison helpers such as `sub_404D20`, `sub_406970`, and `sub_406AB0`. Those
helpers are shared compiler support and are less useful than the ctx-specific
map node families. It also leaves the small `sub_402260` critical-section
destructor wrapper unnamed for the same reason as Round 412.

## Verification

Local verification for this pass:

- `Get-Content -Raw references/analysis/quakelive_symbol_aliases.json | ConvertFrom-Json | Out-Null`
- `python -m pytest -q tests/test_platform_services.py::test_zmq_ctx_map_helper_round_414_aliases_are_pinned`
- `python -m pytest -q tests/test_platform_services.py -k zmq`

## Parity Estimate

- Focused ZMQ ctx endpoint/pending tree helper wiring:
  **before 46% -> after 91%**.
- ZMQ-related source reconstruction confidence:
  **before 93.0% -> after 93.2%**.
- Overall Quake Live source parity:
  **before 55.77% -> after 55.78%**.
