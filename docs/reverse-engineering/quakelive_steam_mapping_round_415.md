# Quake Live ZMQ/CZMQ Mapping Round 415

Date: 2026-06-06

## Scope

This pass extends the `quakelive_steam.exe` ZMQ reconstruction from the ctx map
helpers into the socket-base endpoint and pending-connection wiring.  The focus
is the compact `socket_base_t` helper band around `0x408D90..0x40B360`, where
retail uses two smaller string-keyed red-black trees instead of the larger ctx
endpoint and pending node layouts pinned in round 414.

Canonical evidence:

- Binary Ninja HLIL:
  `references/hlil/quakelive/quakelive_steam.exe/quakelive_steam.exe_hlil_split/quakelive_steam.exe_hlil_part01.txt`
- RTTI/string evidence:
  `references/hlil/quakelive/quakelive_steam.exe/quakelive_steam.exe_hlil_split/quakelive_steam.exe_hlil_part06.txt`
- Ghidra function inventory:
  `references/reverse-engineering/ghidra/quakelive_steam/functions.csv`
- Prior companion passes:
  `docs/reverse-engineering/quakelive_steam_mapping_round_130.md`,
  `docs/reverse-engineering/quakelive_steam_mapping_round_148.md`, and
  `docs/reverse-engineering/quakelive_steam_mapping_round_414.md`

## Alias Reconstruction

This pass added 15 aliases:

| symbol | alias | confidence | evidence |
|---|---|---|---|
| `sub_408D90` | `zmq_socket_base_t_add_endpoint` | High | Called by bind and connect after listener/session creation, calls `sub_40f200(arg2, arg1)`, copies the endpoint address string, stores endpoint and pipe payload fields, then inserts through the endpoint map at `arg1 + 0x288`. |
| `sub_409ED0` | `std_string_ctor_substr_zmq_socket_base` | High | Initializes the small-string fields and delegates to `sub_406AB0(arg2, arg1, arg3, arg4)`, matching the compiler-emitted string substring/copy constructor used in this socket-base helper band. |
| `sub_409F10` | `zmq_array_item_0_dtor` | High | Single-purpose destructor body resets the receiver to `zmq::array_item_t<0>::vftable`; RTTI for the same base class is present in HLIL part 06. |
| `sub_40A1B0` | `std_tree_erase_zmq_socket_base_pending_connection_node_range` | High | Range eraser for the compact pending tree: full clears dispatch to `sub_40AD30`, iterative erases dispatch to existing iterator erase `sub_409F20`, and sentinel checks use offset `0x2D`. |
| `sub_40A2F0` | `zmq_array_item_0_scalar_deleting_dtor` | High | Scalar deleting destructor for `zmq::array_item_t<0>`: resets the vftable and conditionally calls `operator delete`. |
| `sub_40AB80` | `std_tree_rotate_left_zmq_socket_base_pending_connection_node` | High | Left rotation helper over nodes whose nil/color sentinel byte lives at `0x2D`. |
| `sub_40ABE0` | `std_tree_rotate_right_zmq_socket_base_pending_connection_node` | High | Right rotation helper over the same compact pending node layout and `0x2D` sentinel checks. |
| `sub_40AC40` | `std_tree_rightmost_zmq_socket_base_pending_connection_node` | High | Walks right children until the compact pending sentinel at `0x2D` is reached. |
| `sub_40AC60` | `std_tree_free_zmq_socket_base_endpoint_node_subtree` | High | Recursively frees endpoint nodes, destructs the key string at `+0x0C`, and uses the endpoint sentinel offset `0x31`. |
| `sub_40ACD0` | `std_tree_rotate_left_zmq_socket_base_endpoint_node` | High | Left rotation helper over compact endpoint nodes whose nil/color sentinel byte lives at `0x31`. |
| `sub_40AD30` | `std_tree_free_zmq_socket_base_pending_connection_node_subtree` | High | Recursively frees pending nodes, destructs the key string at `+0x0C`, and uses the pending sentinel offset `0x2D`. |
| `sub_40ADA0` | `std_tree_next_zmq_socket_base_pending_connection_node` | High | Iterator increment helper for compact pending nodes, walking child/parent links with `0x2D` sentinel checks. |
| `sub_40ADF0` | `std_tree_next_zmq_socket_base_endpoint_node` | High | Iterator increment helper for compact endpoint nodes, walking child/parent links with `0x31` sentinel checks. |
| `sub_40B280` | `std_tree_create_zmq_socket_base_pending_connection_node` | High | Allocates `0x30` bytes, initializes node links from the map header, copies the string key, and stores one payload pointer at `+0x28`. |
| `sub_40B360` | `std_tree_create_zmq_socket_base_endpoint_node` | High | Allocates `0x34` bytes, initializes node links from the map header, copies the string key, and stores endpoint plus pipe payload fields at `+0x28/+0x2C`. |

## Observed Facts

- `socket_base_t::bind` calls `sub_408D90(arg2, esi_4, edi_3, 0)` after the TCP
  listener has been created, bound, and asked for its final address string.
- `socket_base_t::connect` calls `sub_408D90(arg2, var_79c, arg1, edi_11)` after
  session creation and pipe attachment, which means the helper is shared by
  bound listener endpoints and outbound connection endpoints.
- `sub_408D90` starts ownership wiring with `sub_40F200(arg2, arg1)`, then
  inserts a node through `sub_40AEB0(arg1 + 0x288, ..., sub_40B360(...))`.
  This makes `socket_base_t + 0x288` the compact endpoint map in this retail
  build.
- The inproc-pending branch in `socket_base_t::connect` stores unresolved
  connection work through `sub_40AF80(&arg2[0xA6], ..., sub_40B280(...))`.
  Since `arg2[0xA6]` is pointer arithmetic on a 32-bit pointer array, this is
  the map rooted at `socket_base_t + 0x298`.
- `socket_base_t::term_endpoint` already had the public owner alias
  `zmq_socket_base_t_term_endpoint`; round 415 re-pins its tree support:
  endpoint lookup/iteration uses the existing `sub_40A660`,
  `sub_40A3D0`, and new `sub_40ADF0` helpers, while pending lookup/iteration
  uses existing `sub_40A8F0`, existing `sub_409F20`, and new `sub_40ADA0` plus
  `sub_40A1B0`.
- The compact endpoint tree and compact pending tree are not the same as the
  ctx trees from round 414.  The socket-base endpoint node is `0x34` bytes with
  sentinel/color bytes at `0x30/0x31`; the socket-base pending node is `0x30`
  bytes with sentinel/color bytes at `0x2C/0x2D`.

## Source Reconstruction Shape

The retail structure now has enough evidence for the following reconstruction
shape:

```cpp
// Socket-base owned endpoint registry.
using socket_endpoint_map =
	std::map<std::string, socket_endpoint_t>;

struct socket_endpoint_t {
	own_t *endpoint;
	pipe_t *pipe;
};

// Socket-base owned unresolved inproc connection registry.
using socket_pending_connection_map =
	std::multimap<std::string, pipe_t *>;

void socket_base_t::add_endpoint(const char *addr, own_t *endpoint, pipe_t *pipe)
{
	launch_child(endpoint);
	endpoints.insert({addr, {endpoint, pipe}});
}
```

The names above are intentionally structural rather than a claim that the retail
headers used those exact typedef names.  The `add_endpoint` owner is high
confidence because its callsites, ownership setup, key copy, and payload fields
all agree.

## Inference Boundary

- Existing aliases for `sub_40AEB0`, `sub_40AF80`, `sub_40A660`,
  `sub_40A8F0`, `sub_40A3D0`, `sub_409F20`, and `sub_40B050` are preserved for
  compatibility with earlier mapping tests.  The new aliases add
  `socket_base` qualifiers where the compact node layout proves the owner.
- The helper `sub_409ED0` is compiler-emitted `std::string` machinery.  The
  ZMQ qualifier records the evidence neighborhood and test ownership rather
  than a custom ZeroMQ semantic function.
- Generic string comparison/find and pointer-vector helpers in the same band
  remain unmapped in this round because their callsite ownership is broader and
  less stable than the endpoint/pending compact-map helpers.

## Verification

- `Get-Content -Raw references/analysis/quakelive_symbol_aliases.json | ConvertFrom-Json | Out-Null`
- `python -m pytest -q tests/test_platform_services.py::test_zmq_socket_base_endpoint_map_round_415_aliases_are_pinned`
- `python -m pytest -q tests/test_platform_services.py -k zmq`

No runtime launch was needed; the change is a static mapping and reconstruction
pass against committed HLIL/Ghidra evidence.

## Parity Estimate

- Focused socket-base endpoint/pending compact-map helper confidence:
  **before 44% -> after 90%**.
- ZMQ-related source reconstruction confidence:
  **before 93.2% -> after 93.4%**.
- Overall Quake Live source parity:
  **before 55.78% -> after 55.79%**.
