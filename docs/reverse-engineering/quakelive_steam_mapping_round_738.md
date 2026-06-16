# Quake Live Steam Mapping Round 738: ZMQ Auth Bind Failure Close-Slot Boundary

## Scope

This round pins the ZMQ auth bind failure close-slot boundary in the retained
server `idZMQ` integration. Retail Quake Live embeds libzmq/CZMQ inside
`quakelive_steam.exe`; SRP keeps those embedded library bodies as evidence only
and uses an external libzmq runtime drop. This round therefore maps the
Quake Live-owned auth wiring and cleanup boundary without reconstructing
libzmq/CZMQ internals, and explicitly does not reconstruct libzmq/CZMQ
internals.

This pass does not reconstruct libzmq/CZMQ internals.

Focused parity estimate: **before 94% -> after 99%** for the auth bind failure
close-slot boundary. Focused ZMQ wiring/source reconstruction estimate:
**before 99.88% -> after 99.90%**. Repo-wide parity remains **99%** because the
change is a named SRP manual ZAP bind failure cleanup at the retained dynamic
`zmq_close` boundary.

## Evidence

| Symbol | Promoted name | Evidence |
| --- | --- | --- |
| `sub_4012F0` | `zmq_close` | Embedded libzmq close export; used through `zsys_close`. |
| `sub_4F5190` | `zsock_destroy_checked` | Checked zsock destroy helper stamps and clears the owner slot. |
| `sub_4F5200` | `zsock_bind` | CZMQ bind wrapper used by the ZAP actor socket. |
| `sub_4F5EA0` | `zauth_self_destroy` | Retail auth actor teardown destroys the ZAP socket slot. |
| `sub_4F5F10` | `zauth_self_new` | Retail auth actor creation binds the ZAP socket endpoint. |
| `sub_4F6AA0` | `zsys_close` | CZMQ close shim that reaches embedded `zmq_close`. |

Primary HLIL anchors:

```text
004f5190    void sub_4f5190(int32_t* arg1, int32_t arg2, int32_t arg3)
004f51b1      sub_4f6aa0(edx_1)
004f51ce      *arg1 = 0
004f5200    int32_t sub_4f5200(void* arg1, int32_t arg2)
004f5270      if (sub_401410(*(arg1 + 4), var_8) != 0)
004f5ea0    void sub_4f5ea0()
004f5ee8          sub_4f5410(eax_3, edx_2, ecx_3, eax_3, "inproc://zeromq.zap.01")
004f5ef5          sub_4f5190(esi + 4, "..\..\..\..\src\zauth.c", 0x39)
004f5f10    int32_t sub_4f5f10(int32_t arg1)
004f5f8e  int32_t eax_9 = sub_4f5100(4, "..\..\..\..\src\zauth.c", 0x4c)
004f5f9c  sub_4f5200(eax_9, "inproc://zeromq.zap.01")
004f6aa0    int32_t sub_4f6aa0(void* arg1)
004f6b09  sub_4012f0(arg1)
```

Observed facts:

- Retail `zauth_self_new` creates a REP-like zsock at `zauth.c:0x4c` and binds
  it to `inproc://zeromq.zap.01` through `zsock_bind`.
- Retail `zauth_self_destroy` unbinds that endpoint and then calls
  `zsock_destroy_checked` on the owning ZAP socket slot at `zauth.c:0x39`.
- Retail `zsock_destroy_checked` reaches `zsys_close`, which reaches embedded
  `zmq_close`, then clears the owner slot with `*arg1 = 0`.

Inference:

- SRP's manual ZAP socket is an intentional replacement for the retail CZMQ
  auth actor. When the manual `zmq_bind` call fails, the local socket owner
  should still route through the same retained close-slot abstraction rather
  than directly invoking the external runtime close function.

## Reconstruction

SRP now routes the manual ZAP bind failure cleanup through:

```c
idZMQ_CloseSocket( &socket );
```

This keeps all Quake Live-owned socket cleanup paths behind the named
`idZMQ_CloseSocket` shim. The only direct `s_zmq.zmq_close` call remains inside
that shim, and the shim clears the caller's slot with `QL_ZMQ_SOCKET_SLOT_EMPTY`.

This is an SRP manual ZAP bind failure cleanup, not a CZMQ source
reconstruction. The source still avoids `zsock_bind`, `zsock_destroy_checked`,
`zauth_self_new`, `zauth_self_destroy`, and any committed libzmq/CZMQ
implementation files.

## Validation

Validation run:

```text
python -m pytest -q tests/test_platform_services.py -k zmq_auth_bind_failure_close_slot_round_738 --tb=short
1 passed, 277 deselected

python -m pytest -q tests/test_platform_services.py -k zmq --tb=short
99 passed, 179 deselected

python -m pytest -q tests/test_server_full_parity_gate.py --tb=short
2 passed, 1 skipped

rg --files src/libs/libzmq
src/libs/libzmq\README.md

git diff --check
passed with existing CRLF conversion warnings only
```

`artifacts/server_validation/logs/server_full_parity_gate.json` now records
`auth_bind_failure_close_slot_present: true`.
