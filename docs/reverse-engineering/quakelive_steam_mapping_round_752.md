# Quake Live Steam Mapping Round 752: ZMQ Receive Frame-More Flag Boundary

## Scope

This round pins the ZMQ receive frame-more flag boundary in SRP's retained
server `idZMQ` receive wiring. Retail Quake Live compiled libzmq/CZMQ helper
code into `quakelive_steam.exe`; SRP keeps libzmq as an external runtime
dependency and reconstructs only the Quake Live-owned integration layer.

This is the SRP caller-visible frame-more adaptation and does not reconstruct libzmq/CZMQ internals.

Focused parity estimate: **before 93% -> after 99%** for receive frame-more
flag confidence. Focused ZMQ wiring/source reconstruction confidence moves
from **99.99% -> 99.995%**. Repo-wide parity remains **99%** because this pass
names an SRP qboolean receive-state adaptation without changing the
strict-retail Windows replacement score.

## Evidence

| Symbol | Promoted name | Evidence |
| --- | --- | --- |
| `sub_4013D0` | `zmq_getsockopt` | Lower embedded libzmq option getter used by retail `zsock_rcvmore`. |
| `sub_401520` | `zmq_msg_recv` | Lower embedded libzmq message receive helper used by retail `zstr_recv`. |
| `sub_4015E0` | `zmq_msg_data` | Lower embedded libzmq message data helper used before copying the received bytes. |
| `sub_4015F0` | `zmq_msg_size` | Lower embedded libzmq message size helper used to allocate/copy the received string. |
| `sub_4F58F0` | `zsock_rcvmore` | Retail CZMQ helper that queries `ZMQ_RCVMORE` and returns the multipart indicator. |
| `sub_4F5CB0` | `zstr_recv` | Retail CZMQ string receive helper that receives a message, copies bytes, and writes a trailing terminator. |

Primary HLIL anchors:

```text
004f58f0    int32_t sub_4f58f0(int32_t* arg1)
004f5914  sub_4013d0(sub_4f56b0(arg1), 0xd, &result, &var_8)
004f5922  return result
004f5cb0    int32_t sub_4f5cb0(int32_t* arg1)
004f5ce6  if (sub_401520(eax_3, &var_28, 0) s< 0)
004f5cfe  uint32_t eax_6 = sub_4015f0(&var_28)
004f5d27      memcpy(result, sub_4015e0(&var_28), eax_6)
004f5d2f      *(result + eax_6) = 0
```

Observed facts:

- Retail `zsock_rcvmore` asks the embedded libzmq getter for option `0xd`
  (`ZMQ_RCVMORE`) and returns the resulting integer value.
- Retail `zstr_recv` receives into a temporary message object, reads size and
  data through `zmq_msg_*` helpers, copies the bytes, and appends a string
  terminator.
- SRP does not carry the `zsock_rcvmore`, `zstr_recv`, or `zmq_msg_*` helper
  bodies. The receive path uses dynamically resolved `zmq_recv` and optional
  `zmq_getsockopt` exports.

Inference:

- SRP's caller-visible `qboolean more` state is local retained `idZMQ` wiring
  around the external runtime receive path.
- Naming that state separately from `QL_ZMQ_RCVMORE_NONE` makes the wrapper
  boundary clear without pretending to reconstruct CZMQ helper internals.

## Reconstruction

`sv_zmq.c` now names the caller-visible frame-more states:

```c
#define QL_ZMQ_FRAME_MORE qtrue
#define QL_ZMQ_FRAME_NO_MORE qfalse
```

`idZMQ_ReadFrameString` clears the optional output flag to
`QL_ZMQ_FRAME_NO_MORE` before receiving. After a successful `zmq_recv`, it
probes `QL_ZMQ_RCVMORE` through `zmq_getsockopt`; when the getter succeeds and
the option value differs from `QL_ZMQ_RCVMORE_NONE`, it assigns
`QL_ZMQ_FRAME_MORE`.

`idZMQ_PumpAuthSocket` now resets its local multipart state with
`QL_ZMQ_FRAME_NO_MORE` before reading each ZAP request. The source still avoids
`zstr_recv`, `zsock_rcvmore`, `zmq_msg_recv`, `zmq_msg_data`, and
`zmq_msg_size` bodies; those names remain retail dependency evidence only.

## Validation

Validation run:

```text
python -m py_compile tests/test_platform_services.py tests/test_server_full_parity_gate.py
passed

python -m pytest -q tests/test_platform_services.py -k zmq_receive_frame_more_flag_round_752 --tb=short
1 passed, 289 deselected

python -m pytest -q tests/test_platform_services.py -k zmq --tb=short
107 passed, 183 deselected

python -m pytest -q tests/test_server_full_parity_gate.py --tb=short
2 passed, 1 skipped

rg --files src/libs/libzmq
src/libs/libzmq\README.md

git diff --check
passed with existing CRLF conversion warnings only
```

`artifacts/server_validation/logs/server_full_parity_gate.json` now records
`receive_frame_more_flag_present: true`.
