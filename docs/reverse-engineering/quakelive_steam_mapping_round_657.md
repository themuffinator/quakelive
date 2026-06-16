# quakelive_steam.exe Mapping Round 657

Date: 2026-06-15

Scope: focused retained `idZMQ` object layout and vtable/destructor boundary.
This round documents Quake Live-owned ZMQ wiring only and does not reconstruct libzmq/CZMQ internals.

## Summary

Retail stores the server ZMQ host as a retained global `idZMQ` object starting
at `data_5756fc`. The committed HLIL gives a compact layout row:
`data_5756fc = idZMQ::vftable`, followed by `data_575700`,
`data_575704`, `data_575708`, `data_57570c`, and the peer-table storage at
`data_575710` / `data_575714`.

This round pins the portable retained idZMQ layout boundary. SRP does not need
to reconstruct the C++ vtable object or MSVC `std::tree` ABI, but its
`idZMQ_t` state now carries the explicit source annotation for the retail slot
owners: auth actor, stats PUB socket, RCON socket, resolved poll socket, and
the decomposed peer-table fields.

## Evidence Table

| Function/Data | Alias/Meaning | Confidence | Notes |
| --- | --- | --- | --- |
| `sub_4F3D70` | `idZMQ_ApplyPasswords` | High | Uses `arg1 + 4` as the shared auth actor slot before applying passwords. |
| `sub_4F3DD0` | `Zmq_ShutdownStatsPublisher` | High | Checks and destroys the stats PUB slot at `data_575704`. |
| `sub_4F3DF0` | `Zmq_ShutdownRuntime` | High | Checks and destroys the RCON slot at `data_575708`, clears `data_57570c`, then destroys the auth actor. |
| `sub_4F4E80` | `idZMQ_ClearRconPeers` | High | Clears the peer-table header/sentinel state and zeroes the retained count. |
| `sub_4F4FE0` | `idZMQ_EraseRconPeerRange` | High | Range erase helper over the peer-table object at `arg1 + 0x14`. |
| `sub_4F5080` | `idZMQ_Destroy` | High | Destructor-shaped cleanup owner for the retained object peer-table storage. |
| `idZMQ::vftable` | `sub_4F5080` destructor entry | High | Vtable row at `0x005483f0` points to the destructor-shaped cleanup owner. |
| `data_5756fc` | retained `idZMQ` object start | High | Global object starts with `idZMQ::vftable`. |
| `data_575700` | auth actor slot | High | Methods test `*(arg1 + 4)` before password apply or actor setup. |
| `data_575704` | stats PUB socket slot | High | Stats shutdown calls `zsock_destroy_checked(&data_575704, ..., 0x73)`. |
| `data_575708` | RCON socket slot | High | Runtime shutdown calls `zsock_destroy_checked(&data_575708, ..., 0xe2)`. |
| `data_57570c` | resolved RCON poll socket slot | High | Runtime shutdown clears the slot before destroying the RCON socket wrapper. |
| `arg1 + 0x14` / `arg1[5]` | peer-table object | High | RCON lookup/insert/erase and destructor range-erase all receive this address. |
| `arg1 + 0x18` / `arg1[6]` | peer-table header/sentinel | High | Broadcast/pump compare against the end sentinel; destructor deletes it. |

## Observed Facts

- `analysis_symbols.txt` names `idZMQ::vftable` at `0x005483f0`, and HLIL
  part 06 shows its only vtable entry is `sub_4F5080`.
- HLIL part 07 shows the retained global object starts at `data_5756fc` with
  `idZMQ::vftable`, then zero-initialized slots through `data_575714`.
- `sub_4F3D70`, `sub_4F3F80`, and `sub_4F4210` use `arg1 + 4` as the shared
  auth actor slot.
- `sub_4F3DD0` destroys the stats socket slot at `data_575704`; `sub_4F3DF0`
  destroys the RCON socket slot at `data_575708` and clears `data_57570c`.
- `sub_4F4D40`, `sub_4F4ED0`, `sub_4F4FE0`, and `sub_4F5080` consistently use
  `arg1 + 0x14` and `arg1 + 0x18` as the peer-table object and header/sentinel
  boundary.

Observed fact: the retained object layout is Quake Live host state wrapped
around CZMQ/libzmq socket objects. The layout evidence is not a request to
reconstruct libzmq/CZMQ internals.

Inferred source boundary: SRP should keep the retained host state readable and
test-pinned while representing the C++ vtable and `std::tree` header with
portable C fields.

## Source Reconstruction

- Added a focused source annotation to `idZMQ_t` tying the portable fields to
  the retail slots: auth actor, stats PUB, RCON socket, resolved RCON poll
  socket, and peer table.
- Kept the peer table as a portable root/list/count decomposition instead of
  reconstructing the MSVC `std::tree` header or vtable mechanics.
- Kept `idZMQ_Destroy` as the portable destructor analogue that owns peer-table
  cleanup, without adding a retail C++ vtable object or libzmq/CZMQ source.

## Validation

- `python -m pytest -q tests/test_platform_services.py -k zmq_retained_idzmq_layout_boundary_round_657`
  - `1 passed, 202 deselected in 5.76s`
- `python -m pytest -q tests/test_platform_services.py -k zmq`
  - `61 passed, 142 deselected in 1.02s`
- `python -m pytest -q tests/test_server_full_parity_gate.py`
  - `2 passed, 1 skipped in 0.12s`
- `rg --files src/libs/libzmq`
  - `src/libs/libzmq\README.md`

## Parity Estimate

- Focused retained `idZMQ` layout/source-boundary confidence:
  **before 90% -> after 98%**.
- Focused ZMQ wiring/source reconstruction confidence:
  **before 97.2% -> after 97.3%**.
- Repo-wide parity remains **99%** because this pass closes a local retained
  object-layout evidence gap without changing the strict-retail Windows
  replacement score.
