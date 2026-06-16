# Quake Live Steam Mapping Round 692: ZMQ External Runtime Export-Name Boundary

Date: 2026-06-16

## Scope

This pass rechecked the ZMQ external runtime export-name boundary in SRP's
server-owned `idZMQ` wiring. Retail Quake Live embeds libzmq/CZMQ inside
`quakelive_steam.exe`; SRP intentionally keeps that library evidence external
to source reconstruction and uses dynamic export resolution only for opted-in
online-service builds.

Focused parity estimate: **before 94% -> after 99%** for external runtime
export-name source-boundary confidence. Focused ZMQ wiring/source
reconstruction confidence moves from **99.3% -> 99.35%**. Repo-wide parity
remains **99%** because this pass names an SRP portability contract without
changing the strict-retail Windows replacement score.

## Evidence

| Retail symbol | Current alias | Confidence | Notes |
| --- | --- | --- | --- |
| `sub_401000` | `zmq_ctx_new` | High | Retail embedded libzmq context constructor wrapper. |
| `sub_401140` | `zmq_ctx_term` | High | Retail embedded libzmq context termination wrapper. |
| `sub_4012C0` | `zmq_socket` | High | Retail embedded libzmq socket creation wrapper. |
| `sub_4012F0` | `zmq_close` | High | Retail embedded libzmq socket close wrapper. |
| `sub_401390` | `zmq_setsockopt` | High | Retail embedded libzmq socket-option setter wrapper. |
| `sub_4013D0` | `zmq_getsockopt` | High | Retail embedded libzmq socket-option getter wrapper. |
| `sub_401410` | `zmq_bind` | High | Retail embedded libzmq bind wrapper. |
| `sub_4014D0` | `zmq_msg_send` | High | Retail embedded libzmq message send wrapper used below CZMQ helpers. |
| `sub_401520` | `zmq_msg_recv` | High | Retail embedded libzmq message receive wrapper used below CZMQ helpers. |
| `sub_401600` | `zmq_poll` | High | Retail embedded libzmq poll wrapper. |

Observed facts:

- The committed alias map and Ghidra function rows identify retail embedded
  libzmq public-wrapper code inside `quakelive_steam.exe`.
- SRP does not link `libzmq.lib`, include `zmq.h`, or reconstruct the embedded
  libzmq/CZMQ implementation under `src/code` or `src/libs/libzmq`.
- SRP's dynamic loader resolves a small required export set before any ZMQ
  socket path can run, and resolves `zmq_setsockopt`/`zmq_getsockopt`
  optionally so default-disabled builds still retain fallback behavior.

Inference:

- retail embedded libzmq/CZMQ remains evidence only. SRP's named export strings
  are a portability boundary for an external runtime drop, not a reconstructed
  copy of retail libzmq source.
- Retail evidence names `zmq_msg_send` and `zmq_msg_recv` below the CZMQ string
  helpers. SRP resolves `zmq_send` and `zmq_recv` directly as the equivalent
  external runtime boundary for its retained stack-buffer implementation.

## Source Reconstruction

The loader export names are now named in source:

- Required exports:
  `QL_ZMQ_EXPORT_CTX_NEW`, `QL_ZMQ_EXPORT_CTX_TERM`,
  `QL_ZMQ_EXPORT_SOCKET`, `QL_ZMQ_EXPORT_CLOSE`, `QL_ZMQ_EXPORT_BIND`,
  `QL_ZMQ_EXPORT_SEND`, `QL_ZMQ_EXPORT_RECV`, `QL_ZMQ_EXPORT_POLL`,
  `QL_ZMQ_EXPORT_ERRNO`, and `QL_ZMQ_EXPORT_STRERROR`.
- Optional exports:
  `QL_ZMQ_EXPORT_SETSOCKOPT` and `QL_ZMQ_EXPORT_GETSOCKOPT`.

`idZMQ_LoadLibrary` now routes all required and optional symbol resolution
through those names. Raw export strings remain only in the constant definitions
so future source review can distinguish SRP dynamic-loader wiring from retail
embedded libzmq/CZMQ implementation evidence.

This pass does not reconstruct libzmq/CZMQ internals and does not add
`zsock_*`, `zstr_*`, `zauth`, or lower `zmq::*` source bodies to the
repository.

## Validation

Passed for this pass:

- `python -m pytest -q tests/test_platform_services.py -k "zmq_external_runtime_export_names_round_692 or zmq_external_runtime_loader_boundary_round_666" --tb=short` - 2 passed, 232 deselected.
- `python -m pytest -q tests/test_platform_services.py -k zmq --tb=short` - 85 passed, 149 deselected.
- `python -m pytest -q tests/test_server_full_parity_gate.py --tb=short` - 2 passed, 1 skipped.
- `rg --files src/libs/libzmq` - only `src/libs/libzmq\README.md`.
- `git diff --check` - passed.
