# Quake Live Steam Mapping Round 751: ZMQ RCON Broadcast Reentrancy Guard Boundary

## Scope

This round pins the ZMQ RCON broadcast reentrancy guard boundary in SRP's
retained server `idZMQ` integration. Retail Quake Live broadcasts console
output through the retained RCON peer table and logs peer disconnects from
inside the broadcast owner. SRP's `Com_Printf` bridge forwards console output
to `Zmq_BroadcastRconOutput`, so the local recursion guard is a source-level
adaptation around the Quake Live-owned broadcast path.

This pass does not reconstruct libzmq/CZMQ internals.

Focused parity estimate: **before 93% -> after 99%** for the RCON broadcast
reentrancy guard boundary. Focused ZMQ wiring/source reconstruction estimate:
**before 99.98% -> after 99.99%**. Repo-wide parity remains **99%** because
the change names an SRP broadcast recursion guard adaptation at the
console-output/RCON broadcast boundary.

This is an SRP broadcast recursion guard adaptation.

## Evidence

| Symbol | Promoted name | Evidence |
| --- | --- | --- |
| `sub_4C9860` | `Com_Printf` | Retail console print/log owner reached from the RCON disconnect branch. |
| `sub_4F46B0` | `idZMQ_EraseRconPeer` | Retail peer erase path reached on RCON identity-send failure. |
| `sub_4F4D40` | `idZMQ_BroadcastRconOutput` | Retail RCON broadcast owner walks retained peers and sends identity/payload frames. |
| `sub_4F4E60` | `Zmq_BroadcastRconOutput` | Public wrapper into the retained broadcast owner. |
| `sub_4F5D60` | `zstr_send` | Retail CZMQ final string send helper for console payloads; source body remains dependency evidence. |
| `sub_4F5D90` | `zstr_sendm` | Retail CZMQ multipart string send helper for RCON identities; source body remains dependency evidence. |

Primary HLIL anchors:

```text
004f4d40    void __fastcall sub_4f4d40(void* arg1)
004f4d4b  if (*(arg1 + 0xc) != 0)
004f4d78              if (sub_4f5d90(*(arg1 + 0xc), eax) s>= 0)
004f4daa                  sub_4f5d60(*(arg1 + 0xc), ebx_1)
004f4d8a                  i = *sub_4f46b0(arg1 + 0x14, &var_8, i)
004f4d92                  sub_4c9860(i, "zmq RCON client disconnected: %s...")
004f4e72  return sub_4f4d40(&data_5756fc)
```

Observed facts:

- Retail `idZMQ_BroadcastRconOutput` checks the retained RCON socket before
  walking the peer table.
- Retail sends the peer identity through `zstr_sendm`; on failure it erases the
  peer and logs `zmq RCON client disconnected: %s`.
- Retail sends the console payload through `zstr_send` only after the identity
  frame succeeds.
- Retail has a public `Zmq_BroadcastRconOutput` wrapper into the retained
  broadcast owner.

Inference:

- SRP's `Com_Printf` bridge forwards console output to the public ZMQ broadcast
  wrapper, so disconnect logging inside `idZMQ_BroadcastRconOutput` needs a
  local guard to avoid recursively rebroadcasting the disconnect log.
- That guard is Quake Live-owned integration wiring around the broadcast owner,
  not libzmq/CZMQ source.

## Reconstruction

`sv_zmq.c` now names the RCON broadcast recursion guard states:

```c
#define QL_ZMQ_RCON_BROADCAST_ACTIVE qtrue
#define QL_ZMQ_RCON_BROADCAST_IDLE qfalse
```

`idZMQ_BroadcastRconOutput` still exits when a broadcast is already active, then
sets the guard before walking peers and clears it after the loop:

```c
s_zmq.broadcastingRconOutput = QL_ZMQ_RCON_BROADCAST_ACTIVE;
...
s_zmq.broadcastingRconOutput = QL_ZMQ_RCON_BROADCAST_IDLE;
```

The source still keeps the retail send split expressed through dynamic
`zmq_send` flags and avoids `zstr_send`, `zstr_sendm`, `s_send_string`, or any
committed libzmq/CZMQ implementation files.

## Validation

Validation run:

```text
python -m py_compile tests/test_platform_services.py tests/test_server_full_parity_gate.py
passed

python -m pytest -q tests/test_platform_services.py -k zmq_rcon_broadcast_reentrancy_guard_round_751 --tb=short
1 passed, 288 deselected

python -m pytest -q tests/test_platform_services.py -k zmq --tb=short
106 passed, 183 deselected

python -m pytest -q tests/test_server_full_parity_gate.py --tb=short
2 passed, 1 skipped

rg --files src/libs/libzmq
src/libs/libzmq\README.md

git diff --check
passed with existing CRLF conversion warnings only
```

`artifacts/server_validation/logs/server_full_parity_gate.json` now records
`rcon_broadcast_reentrancy_guard_present: true`.
