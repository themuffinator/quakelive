# Quake Live Steam Mapping Round 746: ZMQ Resolved RCON Poll Slot-Clear Boundary

## Scope

This round pins the ZMQ resolved RCON poll slot-clear boundary in the retained
server `idZMQ` integration. Retail Quake Live embeds libzmq/CZMQ inside
`quakelive_steam.exe`; SRP keeps those embedded dependency bodies as evidence
only and reconstructs the Quake Live-owned RCON/publication wiring around an
external runtime. This pass does not reconstruct libzmq/CZMQ internals.

This pass does not reconstruct libzmq/CZMQ internals.

Focused parity estimate: **before 94% -> after 99%** for the resolved RCON
poll slot-clear boundary. Focused ZMQ wiring/source reconstruction estimate:
**before 99.95% -> after 99.96%**. Repo-wide parity remains **99%** because
the change is a named SRP retained RCON poll slot adaptation at the `idZMQ`
runtime boundary.

This is an SRP retained RCON poll slot adaptation.

## Evidence

| Symbol | Promoted name | Evidence |
| --- | --- | --- |
| `sub_401600` | `zmq_poll` | Embedded libzmq poll wrapper used by the RCON pump. |
| `sub_4F3DF0` | `Zmq_ShutdownRuntime` | Retail runtime shutdown wrapper for RCON/auth state. |
| `sub_4F4ED0` | `idZMQ_PumpRcon` | Retail RCON pump requiring both wrapper and resolved poll slot. |
| `sub_4F5190` | `zsock_destroy_checked` | Retail checked destroy helper for retained zsock slots. |
| `sub_4F56B0` | `zsock_resolve` | Retail CZMQ helper resolving a zsock wrapper to the underlying pollable socket. |

Primary HLIL anchors:

```text
00401600    void* const sub_401600(uint64_t arg1[0x2] @ xmm0, uint32_t arg2, int64_t arg3)
004f3df0    void sub_4f3df0()
004f3df7  if (data_575708 != 0)
004f3e08      data_57570c = 0
004f3e12      sub_4f5190(&data_575708, "zmq\id_zmq.cpp", 0xe2)
004f4119      result = sub_4f56b0(*(arg1 + 0xc))
004f4121      *(arg1 + 0x10) = result
004f4ed0    void* __fastcall sub_4f4ed0(void* arg1)
004f4ede  if (*(arg1 + 0xc) != 0)
004f4ee4      int32_t ecx = *(arg1 + 0x10)
004f4ee9      if (ecx != 0)
004f4f0d          result = sub_401600(xmm0, &var_20, 1)
```

Observed facts:

- Retail stores a resolved RCON poll slot separately from the retained RCON
  zsock wrapper.
- Retail populates that resolved slot after the RCON bind-result log path via
  `zsock_resolve`.
- Retail `idZMQ_PumpRcon` checks both the RCON wrapper slot and the resolved
  poll slot before calling `zmq_poll`, then continues to receive frames through
  the wrapper-owned RCON socket path.
- Retail `Zmq_ShutdownRuntime` clears `data_57570c` before destroying the RCON
  socket wrapper at `data_575708`.

Inference:

- SRP's `s_zmq.rconPollSocket` field is the retained resolved poll slot for
  the RCON pump. It is Quake Live-owned integration state, not libzmq/CZMQ
  source.
- Because SRP intentionally does not reconstruct CZMQ's `zsock_resolve`, the
  retained adaptation stores the external runtime socket pointer as the poll
  slot after bind logging. The slot clear should still mirror the retail
  ownership order by clearing the resolved poll slot before closing the RCON
  socket wrapper slot.

## Reconstruction

`sv_zmq.c` now names the resolved RCON poll slot empty state:

```c
#define QL_ZMQ_RCON_POLL_SLOT_EMPTY NULL
```

RCON-disabled cleanup and runtime shutdown now use:

```c
s_zmq.rconPollSocket = QL_ZMQ_RCON_POLL_SLOT_EMPTY;
```

`Zmq_ShutdownRuntime` now clears the resolved poll slot before closing
`s_zmq.rconSocket`, matching the retail `data_57570c = 0` before
`zsock_destroy_checked(&data_575708, ...)` order. The source still avoids
direct `zsock_resolve`, `zsock_destroy_checked`, embedded CZMQ code, and any
committed libzmq/CZMQ implementation files.

## Validation

Validation run:

```text
python -m py_compile tests/test_platform_services.py
passed

python -m pytest -q tests/test_platform_services.py -k zmq_rcon_poll_slot_clear_order_round_746 --tb=short
1 passed, 283 deselected

python -m pytest -q tests/test_platform_services.py -k zmq --tb=short
103 passed, 181 deselected

python -m pytest -q tests/test_server_full_parity_gate.py --tb=short
2 passed, 1 skipped

rg --files src/libs/libzmq
src/libs/libzmq\README.md

git diff --check
passed with existing CRLF conversion warnings only
```

`artifacts/server_validation/logs/server_full_parity_gate.json` now records
`rcon_poll_slot_clear_present: true`.
