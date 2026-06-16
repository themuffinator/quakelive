# Quake Live Steam Mapping Round 740: ZMQ Context Shutdown Slot-Clear Boundary

## Scope

This round pins the ZMQ context shutdown slot-clear boundary in the retained
server `idZMQ` integration. Retail Quake Live embeds libzmq/CZMQ inside
`quakelive_steam.exe`; SRP keeps those embedded library bodies as evidence only
and uses an external libzmq runtime drop. This pass does not reconstruct
libzmq/CZMQ internals.

This pass does not reconstruct libzmq/CZMQ internals.

Focused parity estimate: **before 94% -> after 99%** for the context shutdown
slot-clear boundary. Focused ZMQ wiring/source reconstruction estimate:
**before 99.90% -> after 99.92%**. Repo-wide parity remains **99%** because the
change is a named SRP dynamic `zmq_ctx_term` adaptation at the retained runtime
context boundary.

This is an SRP dynamic zmq_ctx_term adaptation.

## Evidence

| Symbol | Promoted name | Evidence |
| --- | --- | --- |
| `sub_401140` | `zmq_ctx_term` | Embedded libzmq context termination export. |
| `sub_4012B0` | `zmq_term` | Legacy embedded libzmq term wrapper tailcalling `zmq_ctx_term`. |
| `sub_402790` | `zmq_ctx_t_term` | Embedded libzmq context implementation teardown. |
| `sub_4F3DD0` | `Zmq_ShutdownStatsPublisher` | Retail stats socket shutdown wrapper. |
| `sub_4F3DF0` | `Zmq_ShutdownRuntime` | Retail RCON/auth runtime shutdown wrapper. |
| `sub_4F5190` | `zsock_destroy_checked` | Checked zsock destroy helper used by retail socket slots. |
| `sub_4F5B50` | `zactor_destroy` | CZMQ auth actor destroy helper used by runtime shutdown. |

Primary HLIL anchors:

```text
00401140    int32_t sub_401140(int32_t* arg1)
00401162  int32_t result = sub_402790(eax)
004012b0    int32_t sub_4012b0()
004012b4  return sub_401140() __tailcall
00402790    int32_t __stdcall sub_402790(void* arg1)
004f3dd0    void sub_4f3dd0()
004f3de5      sub_4f5190(&data_575704, "zmq\id_zmq.cpp", 0x73)
004f3df0    void sub_4f3df0()
004f3e08      data_57570c = 0
004f3e12      sub_4f5190(&data_575708, "zmq\id_zmq.cpp", 0xe2)
004f3e21  if (data_575700 != 0)
004f3e28      sub_4f5b50(&data_575700)
```

Observed facts:

- Retail `Zmq_ShutdownRuntime` clears the retained RCON poll slot, destroys the
  RCON zsock slot, and then destroys the retained auth actor.
- Retail embedded libzmq exposes `zmq_ctx_term`; the legacy `zmq_term` wrapper
  tailcalls it, and `zmq_ctx_term` reaches `zmq_ctx_t_term`.
- SRP deliberately does not carry the embedded libzmq/CZMQ implementation in
  source. It dynamically resolves `zmq_ctx_term` from the external runtime.

Inference:

- SRP's `s_zmq.context` field is an external-runtime accommodation for the
  retained `idZMQ` host. After calling dynamic `zmq_ctx_term`, the caller-owned
  context slot should be explicitly named as empty, matching the already pinned
  socket slot-clear boundary.

## Reconstruction

`sv_zmq.c` now names the local context empty state:

```c
#define QL_ZMQ_CONTEXT_SLOT_EMPTY NULL
```

`Zmq_ShutdownRuntime` now clears the dynamic runtime context with:

```c
s_zmq.context = QL_ZMQ_CONTEXT_SLOT_EMPTY;
```

The direct `zmq_ctx_term` call remains an external runtime call through the
resolved function pointer. The source still avoids `zmq_ctx_t_term`, `zmq_term`,
`zactor_destroy`, embedded CZMQ code, and any committed libzmq/CZMQ
implementation files.

## Validation

Validation run:

```text
python -m pytest -q tests/test_platform_services.py -k zmq_context_shutdown_slot_clear_round_740 --tb=short
1 passed, 278 deselected

python -m pytest -q tests/test_platform_services.py -k zmq --tb=short
100 passed, 179 deselected

python -m pytest -q tests/test_server_full_parity_gate.py --tb=short
2 passed, 1 skipped

rg --files src/libs/libzmq
src/libs/libzmq\README.md

git diff --check
passed with existing CRLF conversion warnings only
```

`artifacts/server_validation/logs/server_full_parity_gate.json` now records
`context_shutdown_slot_clear_present: true`.
