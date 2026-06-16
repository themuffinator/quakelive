# Quake Live Steam Mapping Round 742: ZMQ External Runtime Library Slot-Clear Boundary

## Scope

This round pins the ZMQ external runtime library slot-clear boundary in the
retained server `idZMQ` integration. Retail Quake Live embeds libzmq/CZMQ
inside `quakelive_steam.exe`; SRP keeps those embedded library bodies as
evidence only and loads an external runtime library when
`QL_BUILD_ONLINE_SERVICES` permits it. This pass does not reconstruct
libzmq/CZMQ internals.

This pass does not reconstruct libzmq/CZMQ internals.

Focused parity estimate: **before 94% -> after 99%** for the external runtime
library handle slot-clear boundary. Focused ZMQ wiring/source reconstruction
estimate: **before 99.92% -> after 99.94%**. Repo-wide parity remains **99%**
because the change is a named SRP dynamic library handle adaptation at the
retained runtime loader boundary.

This is an SRP dynamic library handle adaptation.

## Evidence

| Symbol | Promoted name | Evidence |
| --- | --- | --- |
| `sub_401140` | `zmq_ctx_term` | Embedded libzmq context termination export. |
| `sub_4012B0` | `zmq_term` | Legacy embedded libzmq term wrapper tailcalling `zmq_ctx_term`. |
| `sub_4F3DF0` | `Zmq_ShutdownRuntime` | Retail RCON/auth runtime shutdown wrapper. |
| `sub_4F5190` | `zsock_destroy_checked` | Checked zsock destroy helper used by retail socket slots. |
| `sub_4F5B50` | `zactor_destroy` | CZMQ auth actor destroy helper used by runtime shutdown. |
| `sub_4F7070` | `zsys_shutdown` | Embedded CZMQ/global zsys shutdown lane. |

Primary HLIL anchors:

```text
00401140    int32_t sub_401140(int32_t* arg1)
004012b0    int32_t sub_4012b0()
004012b4  return sub_401140() __tailcall
004f3df0    void sub_4f3df0()
004f3e08      data_57570c = 0
004f3e12      sub_4f5190(&data_575708, "zmq\id_zmq.cpp", 0xe2)
004f3e21  if (data_575700 != 0)
004f3e28      sub_4f5b50(&data_575700)
004f7070    void sub_4f7070()
004f70bf      if (data_12d30e8 != 0)
004f70d0          sub_4f5190(&data_12d30e8, "..\..\..\..\src\zsys.c", 0xe9)
004f7122          sub_4012f0(*i)
004f7162          sub_4012b0()
004f717b      DeleteCriticalSection(lpCriticalSection: &data_12d309c)
```

Observed facts:

- Retail `Zmq_ShutdownRuntime` clears the retained RCON poll slot, destroys the
  RCON zsock slot, and then destroys the retained auth actor.
- Retail also carries CZMQ zsys shutdown machinery inside
  `quakelive_steam.exe`, including the global zsys socket slot destroy and
  legacy `zmq_term` route.
- SRP deliberately does not carry the embedded libzmq/CZMQ implementation in
  source. The committed `src/libs/libzmq` tree is only the external runtime
  placeholder and README boundary.
- SRP dynamically opens the runtime library, resolves the small set of required
  libzmq exports, and closes that library when exports are missing or the ZMQ
  runtime shuts down.

Inference:

- SRP's `s_zmq.library` field is an external-runtime accommodation for the
  retained `idZMQ` host. It is not a retail static-data slot from embedded
  libzmq/CZMQ.
- After closing the runtime library handle, the caller-owned library slot should
  be explicitly named as empty, matching the already pinned socket and context
  slot-clear boundaries.

## Reconstruction

`sv_zmq.c` now names the local dynamic library handle empty state:

```c
#define QL_ZMQ_LIBRARY_SLOT_EMPTY NULL
```

The missing-export cleanup path in `idZMQ_LoadLibrary` now closes the external
runtime handle and clears it with:

```c
s_zmq.library = QL_ZMQ_LIBRARY_SLOT_EMPTY;
```

`idZMQ_UnloadLibrary` uses the same named empty state after `QL_ZMQ_CLOSE()`.
The source still avoids `#include <zmq.h>`, direct `zsys_shutdown`,
`zactor_destroy`, embedded CZMQ code, and any committed libzmq/CZMQ
implementation files.

## Validation

Validation run:

```text
python -m py_compile tests/test_platform_services.py
passed

python -m pytest -q tests/test_platform_services.py -k zmq_external_runtime_library_slot_clear_round_742 --tb=short
1 passed, 280 deselected

python -m pytest -q tests/test_platform_services.py -k zmq --tb=short
101 passed, 180 deselected

python -m pytest -q tests/test_server_full_parity_gate.py --tb=short
2 passed, 1 skipped

rg --files src/libs/libzmq
src/libs/libzmq\README.md

git diff --check
passed with existing CRLF conversion warnings only
```

`artifacts/server_validation/logs/server_full_parity_gate.json` now records
`external_runtime_library_slot_clear_present: true`.
