# Qcommon Validation And Runtime Evidence (2026-04-10)

Scope: `QC-P6` / `QC-G05` closure for the engine `qcommon` host layer

## Purpose

This note records the final verification tranche for the qcommon parity audit. The goal is not to reopen earlier source-reconstruction work from `QC-P1` through `QC-P5`; it is to make that recovered qcommon behavior enforceable with one dedicated parity gate and one tracked runtime-evidence bundle.

## Runtime Evidence Bundle

Tracked artifact:

- `artifacts/qcommon_validation/logs/qcommon_runtime_evidence_20260410.json`

Probe owner:

- `tools/qcommon/run_qcommon_runtime_probe.ps1`

Observed closure evidence from the tracked bundle:

1. A windowed main-menu probe now archives an authoritative engine screenshot while proving retail `qzconfig.cfg` / `repconfig.cfg` bootstrap, the active `Current search path:` block, the current writable-homepath UI DLL loading contract, and the default-disabled browser markers captured by the current debug build (`web_showBrowser` ignored, `web_changeHash` ignored, published `game.error`, and the native `stopRefresh` fallback log).
2. A windowed local-map probe now reaches `Going from CS_PRIMED to CS_ACTIVE` on `bloodrun` through the current `map <name> ffa` command shape, captures an authoritative engine screenshot, and records the same writable-homepath DLL loading contract for `qagamex86.dll` and `cgamex86.dll`.
3. The tracked runtime bundle therefore closes the last low-cost qcommon proof tail: bootstrap config execution, chosen filesystem roots, writable-homepath DLL loading, and service-disabled launcher/resource fallback behavior are now archived in one machine-readable artifact instead of being inferred from scattered historical logs.

## Dedicated Qcommon Parity Gate

Tracked status artifact:

- `artifacts/qcommon_validation/logs/qcommon_full_parity_gate.json`

Gate owner:

- `tests/test_qcommon_full_parity_gate.py`

The unified qcommon gate now records the full qcommon gap register (`QC-G01`..`QC-G05`) in one machine-readable report. It treats the Win32 homepath lane, collision-leaf ownership, fallback-VM ownership, Windows-host validation portability, and the final ledger/runtime-evidence closure lane as one audited tranche instead of leaving qcommon verification fragmented across focused suites and prose.

## Workflow Wiring

CI owner:

- `.github/workflows/qcommon-validation.yml`

The workflow runs the focused qcommon regression surface:

- `tests/test_cvar_parity.py`
- `tests/test_cvar_alias_console.py`
- `tests/test_fs_search_paths.py`
- `tests/test_qcommon_collision_leaf_parity.py`
- `tests/test_qcommon_vm_fallback_parity.py`
- `tests/test_playerstate_replication.py`
- `tests/test_client_config_parity.py`
- `tests/test_platform_services.py`
- `tests/test_cgame_event_transport_parity.py`
- `tests/test_qcommon_full_parity_gate.py`

and uploads `artifacts/qcommon_validation/**` so the tracked runtime and gate artifacts stay reviewable outside local machines.

## Closure

`QC-P6` is now considered complete.

`QC-G05` is now considered closed.

With the dedicated gate, the tracked runtime-evidence bundle, the reconciled mapping notes, and the refreshed top-level ledger wiring in place, the strict engine `qcommon` parity estimate now closes at **100%** for the current audited register.
