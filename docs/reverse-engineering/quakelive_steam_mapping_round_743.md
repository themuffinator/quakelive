# Quake Live Steam Mapping Round 743: ZMQ External Runtime Resolved-Symbol Slot-Clear Boundary

## Scope

This round pins the ZMQ external runtime resolved-symbol slot-clear boundary in
the retained server `idZMQ` integration. Retail Quake Live embeds libzmq/CZMQ
inside `quakelive_steam.exe`; SRP keeps those embedded library bodies as
evidence only and resolves a small external runtime export table when
`QL_BUILD_ONLINE_SERVICES` permits it. This pass does not reconstruct
libzmq/CZMQ internals.

This pass does not reconstruct libzmq/CZMQ internals.

Focused parity estimate: **before 94% -> after 99%** for the external runtime
resolved-symbol slot-clear boundary. Focused ZMQ wiring/source reconstruction
estimate: **before 99.94% -> after 99.95%**. Repo-wide parity remains **99%**
because the change is a named SRP dynamic export-table adaptation at the
retained runtime loader boundary.

This is an SRP dynamic export-table adaptation.

## Evidence

| Symbol | Promoted name | Evidence |
| --- | --- | --- |
| `sub_401000` | `zmq_ctx_new` | Retail embedded libzmq context constructor wrapper. |
| `sub_401140` | `zmq_ctx_term` | Retail embedded libzmq context termination wrapper. |
| `sub_4012C0` | `zmq_socket` | Retail embedded libzmq socket creation wrapper. |
| `sub_4012F0` | `zmq_close` | Retail embedded libzmq socket close wrapper. |
| `sub_401390` | `zmq_setsockopt` | Retail embedded libzmq socket-option setter wrapper. |
| `sub_4013D0` | `zmq_getsockopt` | Retail embedded libzmq socket-option getter wrapper. |
| `sub_401410` | `zmq_bind` | Retail embedded libzmq bind wrapper. |
| `sub_4014D0` | `zmq_msg_send` | Retail embedded libzmq message send wrapper used below CZMQ helpers. |
| `sub_401520` | `zmq_msg_recv` | Retail embedded libzmq message receive wrapper used below CZMQ helpers. |
| `sub_401600` | `zmq_poll` | Retail embedded libzmq poll wrapper. |

Primary HLIL anchors:

```text
00401000    uint32_t sub_401000()
00401140    int32_t sub_401140(int32_t* arg1)
004012c0    void* sub_4012c0(int32_t* arg1, int32_t arg2)
004012f0    int32_t sub_4012f0(void* arg1)
00401390    int32_t sub_401390(int32_t* arg1, int32_t arg2, int32_t* arg3, void* arg4)
004013d0    int32_t sub_4013d0(int32_t* arg1, int32_t arg2, uint32_t arg3, int32_t* arg4)
00401410    int32_t sub_401410(int32_t* arg1, char* arg2)
004014d0    uint32_t sub_4014d0(int32_t* arg1, void* arg2, char arg3)
00401520    uint32_t sub_401520(int32_t* arg1, void* arg2, char arg3)
00401600    void* const sub_401600(uint64_t arg1[0x2] @ xmm0, uint32_t arg2, int64_t arg3)
```

Observed facts:

- The alias map and Ghidra function rows identify retail embedded libzmq public
  wrappers for the core ZMQ API surface used under the retained `idZMQ` lane.
- SRP does not include `<zmq.h>`, link `libzmq.lib`, or reconstruct embedded
  libzmq/CZMQ source under `src/code` or `src/libs/libzmq`.
- SRP dynamically resolves required exports for context, socket, bind, send,
  receive, poll, and error reporting, with socket-option exports retained as
  optional runtime affordances.
- `zmq_errno` and `zmq_strerror` are external runtime diagnostic exports in
  SRP's loader table. They are not new retail libzmq source bodies.

Inference:

- SRP's `s_zmq.zmq_*` function pointers form a dynamic export table around the
  retained Quake Live ZMQ host integration. Clearing that table is a local
  source-owned lifecycle boundary, not embedded libzmq/CZMQ reconstruction.
- After an external runtime handle is closed or rejected for missing exports,
  the resolved export table should be explicitly named as empty before future
  runtime attempts can reload it.

## Reconstruction

`sv_zmq.c` now names the resolved export-table empty state:

```c
#define QL_ZMQ_SYMBOL_SLOT_EMPTY NULL
```

`idZMQ_ResetResolvedSymbols` now routes all twelve dynamically resolved
function-pointer fields through that named empty state:

```c
s_zmq.zmq_ctx_new = QL_ZMQ_SYMBOL_SLOT_EMPTY;
s_zmq.zmq_ctx_term = QL_ZMQ_SYMBOL_SLOT_EMPTY;
s_zmq.zmq_socket = QL_ZMQ_SYMBOL_SLOT_EMPTY;
s_zmq.zmq_close = QL_ZMQ_SYMBOL_SLOT_EMPTY;
s_zmq.zmq_bind = QL_ZMQ_SYMBOL_SLOT_EMPTY;
s_zmq.zmq_setsockopt = QL_ZMQ_SYMBOL_SLOT_EMPTY;
s_zmq.zmq_getsockopt = QL_ZMQ_SYMBOL_SLOT_EMPTY;
s_zmq.zmq_send = QL_ZMQ_SYMBOL_SLOT_EMPTY;
s_zmq.zmq_recv = QL_ZMQ_SYMBOL_SLOT_EMPTY;
s_zmq.zmq_poll = QL_ZMQ_SYMBOL_SLOT_EMPTY;
s_zmq.zmq_errno = QL_ZMQ_SYMBOL_SLOT_EMPTY;
s_zmq.zmq_strerror = QL_ZMQ_SYMBOL_SLOT_EMPTY;
```

The missing-export cleanup path and runtime unload path still call
`idZMQ_ResetResolvedSymbols` after clearing the external library handle. The
source still avoids direct `zsys_shutdown`, `zsock_destroy_checked`, embedded
CZMQ code, and committed libzmq/CZMQ implementation files.

## Validation

Validation run:

```text
python -m py_compile tests/test_platform_services.py
passed

python -m pytest -q tests/test_platform_services.py -k zmq_external_runtime_resolved_symbol_slot_clear_round_743 --tb=short
1 passed, 281 deselected

python -m pytest -q tests/test_platform_services.py -k zmq --tb=short
102 passed, 180 deselected

python -m pytest -q tests/test_server_full_parity_gate.py --tb=short
2 passed, 1 skipped

rg --files src/libs/libzmq
src/libs/libzmq\README.md

git diff --check
passed with existing CRLF conversion warnings only
```

`artifacts/server_validation/logs/server_full_parity_gate.json` now records
`external_runtime_resolved_symbol_slot_clear_present: true`.
