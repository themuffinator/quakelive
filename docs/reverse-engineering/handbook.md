# Quake Live Reverse Engineering Handbook

This handbook aggregates the major reverse-engineering stages completed so far and surfaces the artefacts each stage produced. Use it as the single entry point when onboarding contributors, preparing reviews, or scheduling refresh work.

## Stage output index

| Stage focus | Primary notes | Key artefacts |
| --- | --- | --- |
| Symbol export baseline | [Reverse Engineering Baseline](./baseline.md) | [`references/symbol-maps/`](../../references/symbol-maps/), [`references/analysis/quakelive_symbol_aliases.json`](../../references/analysis/quakelive_symbol_aliases.json), [`ghidra_scripts/ExportSymbolMap.py`](../../ghidra_scripts/ExportSymbolMap.py) |
| Build recapture | [Quake Live Build Recapture](./build-recapture.md) | [`tools/scripts/dump_toolchain_info.py`](../../tools/scripts/dump_toolchain_info.py), [`references/analysis/quakelive_toolchain_metadata.json`](../../references/analysis/quakelive_toolchain_metadata.json), [`tools/containers/msvc-2010.Dockerfile`](../../tools/containers/msvc-2010.Dockerfile), [`tools/containers/mingw-ld220.Dockerfile`](../../tools/containers/mingw-ld220.Dockerfile) |
| Asset coverage | [Asset map gaps](./asset-map-notes.md) | [`docs/reverse-engineering/asset-map.csv`](./asset-map.csv), HLIL excerpts under [`artifacts/`](../../artifacts/) |
| Deterministic gameplay loop | [Gameplay Loop Validation Notes](./gameplay-loop.md) | [`src-re/prototypes/`](../../src-re/prototypes/), [`logs/re/native-shim.log`](../../logs/re/native-shim.log) (via shim), [`tests`](../../tests) harness inputs |
| Native shim prototyping | [Native Prototype Shim Notes](./native-shim.md) | [`src-re/prototypes/common/native_shim.c`](../../src-re/prototypes/common/native_shim.c), [`src-re/prototypes/`](../../src-re/prototypes/), [`logs/re/native-shim.log`](../../logs/re/native-shim.log), [`logs/syscall_contract.log`](../../logs/syscall_contract.log), [`tools/tests/validate_syscall_contract.py`](../../tools/tests/validate_syscall_contract.py) |
| Network handshake reconstruction | [Network Handshake Reconstruction](./network-handshake.md) | Annotated sources under [`src-re/annotated/net/`](../../src-re/annotated/net/), canonical sources in [`src/code/`](../../src/code/) |
| Behaviour parity diffing | [Behaviour Diff Ledger](./diff-ledger.md) | [`tools/analysis/behaviour_diff.py`](../../tools/analysis/behaviour_diff.py), [`artifacts/tests/analysis/qvm_vs_dll/`](../../artifacts/tests/analysis/qvm_vs_dll/) |
| Deterministic trace harness | [Trace harness for deterministic regression testing](./trace-harness.md) | [`tools/trace/`](../../tools/trace/), sample captures under [`artifacts/tests/`](../../artifacts/tests/) |
| Platform services abstraction | [Steam Platform Abstraction Plan](../steam_platform_abstraction.md)<br>[Online Authentication Lifecycle](../platform/authentication.md) | [`src/common/platform/`](../../src/common/platform/), [`src/common/auth_credentials.c`](../../src/common/auth_credentials.c), [`src/common/auth_credentials.h`](../../src/common/auth_credentials.h), [`tests/test_platform_services.py`](../../tests/test_platform_services.py), [`tools/integration/auth_flow_trace.py`](../../tools/integration/auth_flow_trace.py), [`docs/qa/credential-matrix.md`](../qa/credential-matrix.md), [`docs/platform/credentials.md`](../platform/credentials.md) |
| Reconstruction sign-off | [Reconstruction Tracker](./reconstruction-tracker.md) | [`src-re/clean/`](../../src-re/clean/), shared headers in [`src-re/clean/include/`](../../src-re/clean/include/) |

## Artefact directory

* **Symbol exports:** Normalised manifests live in [`references/symbol-maps/`](../../references/symbol-maps/) with alias configuration at [`references/analysis/quakelive_symbol_aliases.json`](../../references/analysis/quakelive_symbol_aliases.json).
* **Toolchain captures:** Raw dumps sit in [`references/analysis/quakelive_toolchain_metadata.json`](../../references/analysis/quakelive_toolchain_metadata.json); rebuild containers under [`tools/containers/`](../../tools/containers/).
* **Asset inventory:** Structured list maintained in [`docs/reverse-engineering/asset-map.csv`](./asset-map.csv); HLIL transcripts referenced in [Asset map gaps](./asset-map-notes.md).
* **Gameplay prototypes:** C99 reconstructions and shims under [`src-re/prototypes/`](../../src-re/prototypes/) with logging output at [`logs/re/native-shim.log`](../../logs/re/native-shim.log) and syscall contract snapshots in [`logs/syscall_contract.log`](../../logs/syscall_contract.log); validate against [`tools/tests/validate_syscall_contract.py`](../../tools/tests/validate_syscall_contract.py).
* **Networking references:** Use annotated walkthroughs in [`src-re/annotated/net/`](../../src-re/annotated/net/) alongside production sources in [`src/code/`](../../src/code/).
* **Trace captures:** Deterministic artefacts produced by [`tools/trace/`](../../tools/trace/) land beneath [`artifacts/tests/`](../../artifacts/tests/).
* **Review tracker:** Clean reconstructions and approver list located at [`src-re/clean/`](../../src-re/clean/) and [Reconstruction Tracker](./reconstruction-tracker.md).
* **Platform services & authentication:** Abstraction notes in [Steam Platform Abstraction Plan](../steam_platform_abstraction.md) and [Online Authentication Lifecycle](../platform/authentication.md), credential persistence guidance in [Credential persistence and migration](../platform/credentials.md), implementations under [`src/common/platform/`](../../src/common/platform/) and [`src/common/auth_credentials.c`](../../src/common/auth_credentials.c), coverage matrix in [`docs/qa/credential-matrix.md`](../qa/credential-matrix.md), and supporting automation via [`tools/integration/auth_flow_trace.py`](../../tools/integration/auth_flow_trace.py) and [`tests/test_platform_services.py`](../../tests/test_platform_services.py).

## Working glossary

**Baseline export** – The symbol extraction pass orchestrated by [`ghidra_scripts/ExportSymbolMap.py`](../../ghidra_scripts/ExportSymbolMap.py) to seed [`references/symbol-maps/`](../../references/symbol-maps/) with normalised manifests used across reverse-engineering tasks.

**Build recapture containers** – Docker images defined in [`tools/containers/msvc-2010.Dockerfile`](../../tools/containers/msvc-2010.Dockerfile) and [`tools/containers/mingw-ld220.Dockerfile`](../../tools/containers/mingw-ld220.Dockerfile) that reproduce the MSVC10 and MinGW 2.20 environments inferred from toolchain metadata.

**Deterministic trace harness** – Python utilities under [`tools/trace/`](../../tools/trace/) that ingest instrumented Quake Live runs, generate JSONL channel streams (`SYS`, `RNG`, `ENT`, `META`), and replay them to detect divergence.

**Frame context shim** – Native prototypes in [`src-re/prototypes/`](../../src-re/prototypes/) that wrap `CL_Frame`/`G_RunFrame` logic with bindable contexts and structured logging to compare VM and native execution.

**Handshake sequence** – The client/server timeline documented in [Network Handshake Reconstruction](./network-handshake.md) covering `getchallenge` → `connectResponse` and subsequent `netchan` setup using headers defined in [`src/code/qcommon/net_chan.c`](../../src/code/qcommon/net_chan.c).

**HLIL transcript** – Decompiled text exports (for example the `_hlil_part*.txt` files referenced in [Asset map gaps](./asset-map-notes.md)) catalogued under [`artifacts/`](../../artifacts/) and used to trace asset references.

**Behaviour diff ledger** – The comparison log in [Behaviour Diff Ledger](./diff-ledger.md) plus underlying harness [`tools/analysis/behaviour_diff.py`](../../tools/analysis/behaviour_diff.py) that verifies parity between QVM and DLL builds.

**Reconstruction tracker** – Status board maintained in [Reconstruction Tracker](./reconstruction-tracker.md) to record clean-room source drops, shared header adoption, and pending reviewer sign-offs per subsystem.

**Credential abstraction** – Typed credential helpers in [`src/common/auth_credentials.h`](../../src/common/auth_credentials.h) and [`src/common/auth_credentials.c`](../../src/common/auth_credentials.c) that parse, normalise, and dispatch Steam, standalone, and legacy CD-key payloads documented in [Online Authentication Lifecycle](../platform/authentication.md).

**Platform service table** – Capability descriptor exposed by [`src/common/platform/platform_services.c`](../../src/common/platform/platform_services.c) that reports active authentication, matchmaking, workshop, overlay, and statistics providers derived from [`platform_config.h`](../../src/common/platform/platform_config.h).

**Open Steam Adapter** – The fallback authentication backend implemented in [`src/common/platform/backends/platform_backend_open_steam.c`](../../src/common/platform/backends/platform_backend_open_steam.c) and described in [Steam Platform Abstraction Plan](../steam_platform_abstraction.md) to mirror Steamworks flows with open transports.

**Auth flow trace** – Scripted lifecycle capture driven by [`tools/integration/auth_flow_trace.py`](../../tools/integration/auth_flow_trace.py) and catalogued in [Credential Validation Matrix](../qa/credential-matrix.md) to document Steam-only, open-only, and hybrid dispatch outcomes.

**Hybrid fallback** – Steam-first authentication path in [`src/code/client/ql_auth.c`](../../src/code/client/ql_auth.c) that automatically retries pending Steam tickets against the open adapter, emitting the “Hybrid fallback accepted credential” log noted in [Credential Validation Matrix](../qa/credential-matrix.md).

## Review cadence and ownership

| Subsystem | Owner | Artefacts to review | Cadence | Next session |
| --- | --- | --- | --- | --- |
| Gameplay reconstruction | Gameplay systems reviewer | [`src-re/clean/gameplay/frame.c`](../../src-re/clean/gameplay/frame.c), [Gameplay Loop Validation Notes](./gameplay-loop.md), native shim logs | Monthly | First Tuesday each month |
| Client runtime | Client runtime reviewer | [`src-re/clean/client/frame.c`](../../src-re/clean/client/frame.c), [Native Prototype Shim Notes](./native-shim.md), trace captures | Monthly | Second Tuesday each month |
| Networking protocol | Networking protocol reviewer | [`src-re/clean/net/handshake.c`](../../src-re/clean/net/handshake.c), [Network Handshake Reconstruction](./network-handshake.md), [Behaviour Diff Ledger](./diff-ledger.md) | Bi-weekly | Next Thursday following release drop |
| Toolchain recapture | Build infrastructure reviewer | [`tools/containers/msvc-2010.Dockerfile`](../../tools/containers/msvc-2010.Dockerfile), [`tools/containers/mingw-ld220.Dockerfile`](../../tools/containers/mingw-ld220.Dockerfile), [Quake Live Build Recapture](./build-recapture.md) | Quarterly | First week of each quarter |
| Platform services | Platform integration reviewer | [`src/common/platform/`](../../src/common/platform/), [Steam Platform Abstraction Plan](../steam_platform_abstraction.md), [Credential Validation Matrix](../qa/credential-matrix.md), [`tests/test_platform_services.py`](../../tests/test_platform_services.py), [`tools/integration/auth_flow_trace.py`](../../tools/integration/auth_flow_trace.py) | Bi-weekly | Friday following QA matrix refresh |

Schedule review invites on the stated cadence and capture outcomes in the corresponding stage documents. If scope or artefacts shift, update this handbook alongside the source document to keep the index authoritative.
