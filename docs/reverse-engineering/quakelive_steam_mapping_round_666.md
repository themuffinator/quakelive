# Quake Live Steam Mapping Round 666: ZMQ External Runtime Loader Boundary

Date: 2026-06-15

## Scope

This pass rechecked the external runtime loader boundary around SRP's retained
ZMQ wiring. Retail Quake Live appears to have libzmq/CZMQ compiled into
`quakelive_steam.exe`, so this is not a claim that retail used SRP's dynamic
loader. Instead, this round pins the SRP external-libzmq accommodation that
keeps Quake Live-owned ZMQ integration in `sv_zmq.c` while keeping the libzmq
implementation outside the source tree.

Focused parity estimate: **before 93% -> after 98%** for the external runtime
loader boundary/source-boundary confidence. Focused ZMQ wiring/source
reconstruction confidence moves from **98.1% -> 98.2%**. Repo-wide parity
remains **99%** because this pass closes a local dependency-boundary gap
without changing the strict-retail Windows replacement score.

## Evidence

Observed retail and source facts:

- The promoted retail aliases keep the Quake Live-owned public ZMQ wrapper,
  auth/password, stats publication, and RCON paths in `quakelive_steam.exe`.
- Earlier ZMQ rounds map CZMQ/libzmq helper symbols such as `zsock_new`,
  `zsock_set_plain_server`, `zsock_set_zap_domain`, `zstr_send`, and
  `zstr_sendx` as dependency evidence, not SRP-owned source bodies.
- `src/code/server/sv_zmq.c` is the only ZMQ-named C/C++ source file under
  `src/code`, and it dynamically resolves the external runtime entry points.
- `src/libs/libzmq/README.md`, `README.md`, `BUILD.md`, `.gitignore`, and the
  dependency ownership note all document `src/libs/libzmq` as a runtime-drop
  location rather than a source reconstruction area.

Observed SRP loader signals:

- Windows candidate names: `libzmq.dll`, `zmq.dll`.
- Unix candidate names: `libzmq.so.5`, `libzmq.so`.
- Required symbols: `zmq_ctx_new`, `zmq_ctx_term`, `zmq_socket`, `zmq_close`,
  `zmq_bind`, `zmq_send`, `zmq_recv`, `zmq_poll`, `zmq_errno`,
  `zmq_strerror`.
- Optional symbols: `zmq_setsockopt`, `zmq_getsockopt`.
- Default `QL_BUILD_ONLINE_SERVICES=0` builds report the disabled runtime
  policy and leave retained fallback paths available without requiring libzmq.

Inference:

SRP should continue to reconstruct Quake Live's ZMQ ownership and message
wiring, but it does not reconstruct libzmq/CZMQ internals. The loader is
therefore a compatibility boundary: it lets online-service-enabled local builds
use an installed runtime while preserving the repo's GPL source reconstruction
focus and default offline build policy.

## Source Reconstruction

This round named the loader/fallback strings and routed the source through
those constants:

- `QL_ZMQ_LAST_ERROR_UNKNOWN`
- `QL_ZMQ_RUNTIME_UNAVAILABLE_FORMAT`
- `QL_ZMQ_RUNTIME_DISABLED_MESSAGE`
- `QL_ZMQ_RUNTIME_LOAD_FAILED_REASON`
- `QL_ZMQ_RUNTIME_EXPORTS_MISSING_REASON`
- `QL_ZMQ_CONTEXT_CREATE_FAILED_FORMAT`
- `QL_ZMQ_AUTH_SOCKET_CREATE_FAILED_FORMAT`
- `QL_ZMQ_AUTH_SOCKET_BIND_FAILED_FORMAT`
- `QL_ZMQ_RCON_SOCKET_CREATE_FAILED_FORMAT`
- `QL_ZMQ_STATS_SOCKET_CREATE_FAILED_FORMAT`

The constants make the external runtime loader boundary testable without
changing emitted text or socket behavior. They also clarify that SRP's runtime
fallback logs and dynamic symbol resolution are source-owned adaptation points,
not reconstructed libzmq source.

The source tree still contains no committed libzmq/CZMQ implementation files
under `src/libs/libzmq`, does not include `<zmq.h>` from `sv_zmq.c`, and does
not link `libzmq.lib` from the Visual Studio project. The runtime DLL remains a
local install/drop dependency only.

## Validation

Completed 2026-06-15:

- `python -m pytest -q tests/test_platform_services.py -k zmq_external_runtime_loader_boundary_round_666`
  - `1 passed, 211 deselected in 0.16s`
- `python -m pytest -q tests/test_platform_services.py -k zmq`
  - `70 passed, 142 deselected in 2.11s`
- `python -m pytest -q tests/test_server_full_parity_gate.py`
  - `2 passed, 1 skipped in 0.20s`
- `git diff --check`
  - Passed; Git reported only the existing LF-to-CRLF working-copy warnings.
- `rg --files src/libs/libzmq`
  - `src/libs/libzmq\README.md`
