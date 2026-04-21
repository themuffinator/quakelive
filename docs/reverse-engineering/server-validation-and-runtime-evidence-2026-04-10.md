# Server Validation And Runtime Evidence (2026-04-10)

Scope: `SV-P7` / `SV-G06` closure for the engine `server` host

## Purpose

This note records the final verification tranche for the server parity audit. The goal is not to reopen earlier source-reconstruction work from `SV-P1` through `SV-P6`; it is to make that recovered server behavior enforceable with one dedicated parity gate and one tracked dedicated runtime-evidence bundle.

## Runtime Evidence Bundle

Tracked artifact:

- `artifacts/server_validation/logs/server_runtime_evidence_20260410.json`

Probe owner:

- `tools/server/run_server_runtime_probe.ps1`

Observed closure evidence from the tracked bundle:

1. A dedicated/headless server probe now boots `bloodrun` through the current `map <name> ffa` command shape, loads `qagamex86.dll` from the writable homepath, archives the dedicated `qconsole.log`, and records the end-to-end startup plus clean-exit path as one tracked runtime artifact instead of leaving server validation spread across ad hoc local logs.
2. The probe now sends a local `getstatus` query and records the parsed serverinfo publication surface, proving network-visible metadata publication for `sv_hostname = SVP7 Probe`, `mapname = bloodrun`, `sv_vac = 1`, the retained server-type slot (`sv_serverType` or `serverType`) at `0`, `sv_maxclients = 8`, and the retained `sv_warmupReadyPercentage` default.
3. The same probe now drives a clean dedicated shutdown through local RCON (`status`, then `quit`) and records the resulting `Rcon from 127.0.0.1` control path, clean process exit, and any observed legacy shutdown markers so the shutdown path is part of the tracked evidence instead of being inferred.
4. The runtime artifact also records optional live-service startup state explicitly:
   - master-heartbeat and `NET: server auth` telemetry markers when observed
   - Steam GameServer callback markers when observed
   - requested `zmq_*` enablement plus whether any live ZMQ startup markers or transcript artifacts appeared in the tracked debug build

That explicit optional-marker capture matters because `SV-P7` closes a verification gap, not a new behavior gap: the underlying Steam GameServer, stats, auth, rankings, and ZMQ owners were already reconstructed in `SV-P1` through `SV-P6`, and this final lane exists so the repo can track dedicated runtime evidence honestly even when optional live-service markers are absent in one probe environment.

## Dedicated Server Parity Gate

Tracked status artifact:

- `artifacts/server_validation/logs/server_full_parity_gate.json`

Gate owner:

- `tests/test_server_full_parity_gate.py`

The unified server gate now records the full server gap register (`SV-G01`..`SV-G06`) in one machine-readable report. It treats the Steam GameServer lifecycle/auth lane, the retained `idZMQ` runtime, the qagame-facing Steam stat/achievement owner, the default-disabled rankings compatibility surface, the control-plane cvar/policy surface, and the final dedicated verification/runtime-evidence lane as one audited tranche instead of leaving server verification fragmented across source-shape tests and prose.

## Workflow Wiring

CI owner:

- `.github/workflows/server-validation.yml`

The workflow runs the focused server regression surface:

- `tests/test_platform_services.py`
- `tests/test_fake_vacban.py`
- `tests/test_server_full_parity_gate.py`

and uploads `artifacts/server_validation/**` so the dedicated runtime and gate artifacts stay reviewable outside local machines.

## Closure

`SV-P7` is now considered complete.

`SV-G06` is now considered closed.

With the dedicated gate, the tracked dedicated runtime-evidence bundle, and the refreshed top-level ledger wiring in place, the strict engine `server` parity estimate now closes at **100%** for the current audited register.
