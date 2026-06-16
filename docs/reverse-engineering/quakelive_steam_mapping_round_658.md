# quakelive_steam.exe Mapping Round 658

Date: 2026-06-15

Scope: focused ZMQ checked zsock lifecycle provenance for the retained
`idZMQ` stats and RCON sockets. This round documents Quake Live-owned wiring
only and does not reconstruct libzmq/CZMQ internals.

## Summary

Retail wraps CZMQ socket construction/destruction with checked helpers that
carry source-file and line metadata from `zmq\id_zmq.cpp`. The four `idZMQ`
socket lifecycle sites are stable:

- stats PUB creation: `zsock_new_checked(..., "zmq\id_zmq.cpp", 0x5c)`
- stats PUB destruction: `zsock_destroy_checked(..., "zmq\id_zmq.cpp", 0x73)`
- RCON ROUTER creation: `zsock_new_checked(..., "zmq\id_zmq.cpp", 0xc7)`
- RCON ROUTER destruction: `zsock_destroy_checked(..., "zmq\id_zmq.cpp", 0xe2)`

SRP uses external libzmq dynamically rather than reconstructing CZMQ's checked
`zsock_*` implementation. This round pins the retail provenance in explicit
source constants so future ZMQ work keeps the stats/RCON lifecycle sites tied
to the right retail owners without adding libzmq/CZMQ code.

## Evidence Table

| Function | Alias | Confidence | Notes |
| --- | --- | --- | --- |
| `sub_4F5100` | `zsock_new_checked` | High | Checked socket constructor carrying socket type, file, and source line. |
| `sub_4F5190` | `zsock_destroy_checked` | High | Checked socket destructor carrying pointer, file, and source line. |
| `sub_4F5200` | `zsock_bind` | High | Bind helper consumed after each retained socket is stored. |
| `sub_4F5750` | `zsock_set_zap_domain` | High | Assigns `rcon` or `stats` ZAP domain before bind. |
| `sub_4F5790` | `zsock_set_plain_server` | High | Enables PLAIN server mode when the corresponding password is non-empty. |
| `sub_4F5980` | `zsock_set_router_mandatory` | High | RCON-only ROUTER mandatory option before bind. |

## Observed Facts

- `sub_4F4210` calls `sub_4F5100(1, "zmq\id_zmq.cpp", 0x5c)` before assigning
  the stats socket slot at `arg1 + 8`.
- `sub_4F3DD0` calls `sub_4F5190(&data_575704, "zmq\id_zmq.cpp", 0x73)` when
  shutting down the stats PUB socket.
- `sub_4F3F80` calls `sub_4F5100(6, "zmq\id_zmq.cpp", 0xc7)` before assigning
  the RCON socket slot at `arg1 + 0xc`.
- `sub_4F3DF0` clears `data_57570c` and calls
  `sub_4F5190(&data_575708, "zmq\id_zmq.cpp", 0xe2)` during runtime RCON
  shutdown.
- Both create paths set ZAP domain and PLAIN mode before bind; the RCON path
  also sets ROUTER mandatory.

Observed fact: these `zsock_*` rows are CZMQ/libzmq-derived helper evidence
around the retained Quake Live `idZMQ` lifecycle sites.

Inferred source boundary: SRP should preserve the source-line provenance as
mapping constants and ownership tests, but it should not implement or vendor
the checked zsock helpers.

## Source Reconstruction

- Added `QL_ZMQ_RETAIL_SOURCE_FILE` and per-site retail source-line constants
  for stats create/destroy and RCON create/destroy.
- Kept live runtime behavior on the existing external libzmq dynamic-symbol
  path rather than introducing `zsock_new_checked`, `zsock_destroy_checked`, or
  any CZMQ source.
- Added a focused parity gate that cross-checks the constants, aliases, HLIL
  call sites, and current source lifecycle owners.

## Validation

- `python -m pytest -q tests/test_platform_services.py -k zmq_checked_zsock_lifecycle_provenance_round_658`
  - `1 passed, 203 deselected in 0.09s`
- `python -m pytest -q tests/test_platform_services.py -k zmq`
  - `62 passed, 142 deselected in 1.15s`
- `python -m pytest -q tests/test_server_full_parity_gate.py`
  - `2 passed, 1 skipped in 0.15s`
- `rg --files src/libs/libzmq`
  - `src/libs/libzmq\README.md`

## Parity Estimate

- Focused checked zsock lifecycle provenance confidence:
  **before 91% -> after 98%**.
- Focused ZMQ wiring/source reconstruction confidence:
  **before 97.3% -> after 97.4%**.
- Repo-wide parity remains **99%** because this pass closes a local retained
  ZMQ socket-lifecycle provenance gap without changing the strict-retail
  Windows replacement score.
