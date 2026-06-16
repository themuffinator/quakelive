# Quake Live Steam Mapping Round 749: ZMQ Stats Transcript Handle-Clear Boundary

## Scope

This round pins the ZMQ stats transcript handle-clear boundary in SRP's
retained server `idZMQ` integration. Retail Quake Live publishes stats through
the retained stats PUB socket and embedded CZMQ/libzmq helpers inside
`quakelive_steam.exe`. SRP keeps a local newline-delimited transcript as a
fallback for default-disabled or runtime-unavailable builds, so this pass names
the fallback transcript handle empty state without treating it as retail
dependency source.

This pass does not reconstruct libzmq/CZMQ internals.

Focused parity estimate: **before 92% -> after 99%** for the stats transcript
handle-clear boundary. Focused ZMQ wiring/source reconstruction estimate:
**before 99.97% -> after 99.98%**. Repo-wide parity remains **99%** because
the change is a named SRP fallback transcript handle adaptation beside the
Quake Live-owned stats PUB lifecycle boundary.

This is an SRP fallback transcript handle adaptation.

## Evidence

| Symbol | Promoted name | Evidence |
| --- | --- | --- |
| `sub_4F3DD0` | `Zmq_ShutdownStatsPublisher` | Retail stats shutdown owner checks the retained stats PUB slot and destroys that socket wrapper. |
| `sub_4F4210` | `idZMQ_InitStatsPublisher` | Retail stats publisher init creates the PUB socket and stores it at `this + 8`. |
| `sub_4F4B20` | `idZMQ_ReportPlayerEvent` | Retail dynamic player-event publication sends only when the retained stats PUB socket exists. |
| `sub_4F4C30` | `idZMQ_SubmitMatchReport` | Retail match-report publication sends only when the retained stats PUB socket exists. |
| `sub_4F5190` | `zsock_destroy_checked` | Retail checked CZMQ socket destroy helper for the stats PUB slot; source body remains dependency evidence. |
| `sub_4F5D60` | `zstr_send` | Retail CZMQ string send helper for serialized publication strings; source body remains dependency evidence. |

Primary HLIL anchors:

```text
004f3dd0    void sub_4f3dd0()
004f3dd7  if (data_575704 != 0)
004f3de5      sub_4f5190(&data_575704, "zmq\id_zmq.cpp", 0x73)
004f4210    int32_t __fastcall sub_4f4210(void* arg1)
004f424c  if (*(result + 0x30) s> 0 && *(arg1 + 8) == 0)
004f4327      int32_t eax_11 = sub_4f5100(1, "zmq\id_zmq.cpp", 0x5c)
004f4332      *(arg1 + 8) = eax_11
004f4b57  if (*(arg1 + 8) != 0)
004f4bd2      sub_4f5d60(*(arg1 + 8), eax_6)
004f4c65  if (*(arg1 + 8) != 0)
004f4cdf      sub_4f5d60(*(arg1 + 8), eax_6)
```

Observed facts:

- Retail stats shutdown is limited to the retained stats PUB socket slot at
  `data_575704`.
- Retail stats publisher initialization creates the PUB socket when stats are
  enabled and the retained socket slot is empty.
- Retail publication helpers only serialize and send when the retained stats
  PUB socket exists.
- Retail sends serialized publication strings through embedded CZMQ `zstr_send`
  and destroys the socket through `zsock_destroy_checked`; these helpers remain
  evidence, not SRP source to reconstruct.

Inference:

- SRP's `s_zmq.statsTranscript` is a local fallback sidecar for the stats
  publication lane, not a retail libzmq/CZMQ object.
- Because the transcript is owned by SRP's stats shutdown lane, its empty handle
  state should be named alongside the existing stats transcript path and record
  terminator boundaries.
- Naming the transcript handle clear keeps the fallback lifecycle explicit
  while preserving the retail stats PUB owner split from runtime RCON/auth
  shutdown.

## Reconstruction

`sv_zmq.c` now names the fallback transcript handle empty state:

```c
#define QL_ZMQ_STATS_TRANSCRIPT_HANDLE_EMPTY 0
```

`idZMQ_CloseStatsTranscript` still closes only when a transcript handle is
present, then clears the handle through the named boundary:

```c
FS_FCloseFile( s_zmq.statsTranscript );
s_zmq.statsTranscript = QL_ZMQ_STATS_TRANSCRIPT_HANDLE_EMPTY;
```

`Zmq_ShutdownStatsPublisher` remains the stats transcript/PUB socket shutdown
owner, and `Zmq_ShutdownRuntime` remains focused on RCON/auth/context/library
runtime shutdown. The source still avoids `zstr_send`, `zsock_destroy_checked`,
and any committed libzmq/CZMQ implementation files.

## Validation

Validation run:

```text
python -m py_compile tests/test_platform_services.py tests/test_server_full_parity_gate.py
passed

python -m pytest -q tests/test_platform_services.py -k zmq_stats_transcript_handle_clear_round_749 --tb=short
1 passed, 287 deselected

python -m pytest -q tests/test_platform_services.py -k zmq --tb=short
105 passed, 183 deselected

python -m pytest -q tests/test_server_full_parity_gate.py --tb=short
2 passed, 1 skipped

rg --files src/libs/libzmq
src/libs/libzmq\README.md

git diff --check
passed with existing CRLF conversion warnings only
```

`artifacts/server_validation/logs/server_full_parity_gate.json` now records
`stats_transcript_handle_clear_present: true`.
