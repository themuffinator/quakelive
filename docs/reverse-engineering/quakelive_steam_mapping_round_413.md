# Quake Live ZMQ/CZMQ Mapping Round 413

Date: 2026-06-06

Focus: recover the remaining `ctx.cpp` runtime helpers for socket destruction,
I/O-thread selection, inproc pending connection handoff, and `options_t`
copy/destruction.

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

Round 412 named the ctx constructor, endpoint map operations, and ctx-owned map
cleanup. This pass closes the adjacent ctx runtime band and corrects two older
compiler-noise classifications that are contradicted by the now-stable ctx and
options call graph.

## Alias Reconstruction

This pass added 6 aliases and corrected 2 stale aliases in
`references/analysis/quakelive_symbol_aliases.json`. It also re-pinned the
existing `zmq_ctx_t_connect_inproc_sockets` alias as the handoff target for the
new pending-connection helpers.

| Symbol | Alias | Confidence | Evidence |
| --- | --- | --- | --- |
| `sub_403120` | `zmq_ctx_t_destroy_socket` | High | Returns a socket slot to the free-slot vector, clears the slot table entry, compacts the socket vector, and notifies the reaper when termination drains the last socket. |
| `sub_403260` | `zmq_ctx_t_choose_io_thread` | High | Scans the ctx I/O-thread vector, applies the affinity mask with a shifted bit test, and returns the least-loaded thread by reading each poller load counter. |
| `sub_403470` | `zmq_ctx_endpoint_t_dtor` | High | Thin endpoint-record destructor wrapper that destroys the embedded options payload at record offset `+8`. |
| `sub_403480` | `zmq_options_t_dtor` | High | Destroys the dynamic strings/vectors inside an `options_t` layout and zeroes the owned vector triplets. |
| `sub_4035E0` | `zmq_ctx_t_unregister_endpoints` | High | Walks the endpoint tree under the ctx endpoint mutex and erases every endpoint node owned by the supplied socket. |
| `sub_403E40` | `zmq_ctx_t_connect_pending` | High | Finds pending inproc connections for a newly registered endpoint, calls `zmq_ctx_t_connect_inproc_sockets`, then erases the consumed pending range. |
| `sub_4038B0` | `zmq_options_t_copy_ctor` | High | Corrected from `std_Locinfo_copy_ctor`; copies the full options layout, including identity bytes, string fields, and address-mask vectors. |
| `sub_403BB0` | `zmq_ctx_t_pend_connection` | High | Corrected from a bogus `std::money_get` name; if a bound endpoint exists it connects immediately, otherwise it inserts a pending inproc connection record. |

## Observed Facts

- `socket_base_t::check_destroy` calls `zmq_ctx_t_destroy_socket` before sending
  the final `done` command, matching ctx-owned socket slot release.
- `socket_base_t::connect`, `session_base_t`, and `tcp_listener_t` all call
  `zmq_ctx_t_choose_io_thread`; call sites assert or fail when no I/O thread is
  available.
- `zmq_ctx_t_pend_connection` shares the endpoint mutex and endpoint tree from
  Round 412. It connects immediately when a bind endpoint already exists, or
  stores the caller endpoint/options pair in the pending-connection tree.
- `zmq_ctx_t_connect_pending` walks pending-connection entries matching a newly
  registered endpoint, resolves the registered endpoint through the endpoint
  tree, calls `zmq_ctx_t_connect_inproc_sockets`, and erases the consumed
  pending range with `std_tree_erase_zmq_pending_connection_node_range`.
- `zmq_options_t_copy_ctor` and `zmq_options_t_dtor` now line up with the
  default constructor, set/get switch, and default-own constructor aliases from
  Round 378.
- The previous `std_Locinfo_copy_ctor` and `std::money_get...::_Getmfld`
  aliases were decompiler symbol noise: both functions lock the ctx endpoint
  mutex or copy/destroy ZMQ options storage and are reached from ZMQ call sites.

## Source Reconstruction

This is mapping/static reconstruction only. No GPL-side engine C source changed
in this pass. The recovered source shape is:

```cpp
void ctx_t::destroy_socket(socket_base_t *socket);
io_thread_t *ctx_t::choose_io_thread(uint64_t affinity);
void ctx_t::unregister_endpoints(socket_base_t *socket);
void ctx_t::pend_connection(const char *addr, endpoint_t endpoint, pipe_t **pipes);
void ctx_t::connect_pending(const char *addr, endpoint_t endpoint);

options_t::options_t(const options_t &other);
options_t::~options_t();
```

The inproc handoff path still uses the existing
`zmq_ctx_t_connect_inproc_sockets` alias. This round gives its callers stable
names and ties them to endpoint registration from Round 412.

## Inference Boundary

This pass does not rename the small string/vector helper thunks used inside
`options_t` copy/destruction. It also leaves `sub_403DD0`, an MSVC destructor
wrapper around a string plus embedded `options_t`, unnamed until its owning
container is pinned separately.

## Verification

Local verification for this pass:

- `Get-Content -Raw references/analysis/quakelive_symbol_aliases.json | ConvertFrom-Json | Out-Null`
- `python -m pytest -q tests/test_platform_services.py::test_zmq_ctx_runtime_inproc_round_413_aliases_are_pinned`
- `python -m pytest -q tests/test_platform_services.py -k zmq`

## Parity Estimate

- Focused ZMQ ctx runtime and inproc-pending wiring:
  **before 36% -> after 93%**.
- ZMQ-related source reconstruction confidence:
  **before 92.8% -> after 93.0%**.
- Overall Quake Live source parity:
  **before 55.76% -> after 55.77%**.
