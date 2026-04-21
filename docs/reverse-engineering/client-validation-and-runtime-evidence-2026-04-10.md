# Client Validation And Runtime Evidence (2026-04-10)

Scope: `CL-P6` / `CL-G05` closure for the native `client` host

## Purpose

This note records the final verification tranche for the client parity audit. The goal is not to reopen earlier source-reconstruction work from `CL-P1` through `CL-P5`; it is to make that recovered client behavior enforceable with one dedicated parity gate and one tracked runtime-evidence bundle.

## 2026-04-17 Revalidation Note

The client closure lane was rerun on 2026-04-17 after the tracked client
workflow went missing and the older checked-in runtime bundle no longer proved
the full `CL-P6` contract on the current worktree.

The refreshed pass restored `.github/workflows/client-validation.yml` and
reran `tools/client/run_client_runtime_probe.ps1` against the default
build-disabled client configuration. The probe now uses the valid
`map bloodrun ffa` startup form, retries transient `pak_uiql.pk3` rewrite
locks, and caps probe pacing at `com_maxfps 30` so the local-map tranche
reliably reaches `CS_ACTIVE` before issuing the demo/screenshot/disconnect
sequence.

## 2026-04-21 Runtime Evidence Refresh

The tracked client runtime bundle was refreshed again on 2026-04-21 after the
UI runtime-package proof path was hardened.

The refreshed pass reran `tools/client/run_client_runtime_probe.ps1` against
the current `Debug|x86` client build and the local retail install. The tracked
artifact now records the emitted `ui_runtime_packages` block, including
`artifacts/ui_bundle/runtime_ui_package_manifest.json`,
`build/win32/Debug/bin/baseq3/pak_uiql.pk3`, and the bounded overlay-package
slot, which currently remains unmaterialized because `drift_files` is empty.
The main-menu/browser-policy proof is also now keyed to the current
fallback markers the runtime actually emits:
`web_showBrowser ignored`, `web_changeHash ignored`,
`steam_event game.error {"text":"codex_client_p6_error"}`, and the UI-side
`stopRefresh` offline fallback log.

## Runtime Evidence Bundle

Tracked artifact:

- `artifacts/client_validation/logs/client_runtime_evidence_20260410.json`

Probe owner:

- `tools/client/run_client_runtime_probe.ps1`

Observed closure evidence from the tracked bundle:

1. A windowed main-menu probe now captures an authoritative engine screenshot while proving the retail `qzconfig.cfg` / `repconfig.cfg` bootstrap, `writeClientConfig` output, the emitted UI runtime-package manifest/main-package hashes, and the default-disabled browser-policy behavior for `web_showBrowser`, `web_changeHash`, `game.error`, and the UI-side `stopRefresh` fallback.
2. A windowed local-map probe now reaches `Going from CS_PRIMED to CS_ACTIVE` on `bloodrun`, captures both engine and process-bound runtime screenshots, records a flushed demo artifact, and proves client-lifecycle end markers through `steam_event game.end` plus `----- CL_Shutdown -----`.
3. The runtime probe now follows the real launched `quakelive_steam` process instead of assuming the first returned process handle owns the full game lifetime, which keeps the archived logs and capture artifacts aligned with the actual client session.

## Dedicated Client Parity Gate

Tracked status artifact:

- `artifacts/client_validation/logs/client_full_parity_gate.json`

Gate owner:

- `tests/test_client_full_parity_gate.py`

The unified client gate now records the full client gap register (`CL-G01`..`CL-G05`) in one machine-readable report. It treats the browser-host lane, Steam callback lifecycle, workshop bootstrap lane, config/bootstrap persistence lane, and final validation/runtime-evidence lane as one audited tranche instead of leaving client verification fragmented across targeted suites.

## Workflow Wiring

CI owner:

- `.github/workflows/client-validation.yml`

The workflow runs the focused client regression surface:

- `tests/test_platform_services.py`
- `tests/test_steamworks_harness.py`
- `tests/test_client_config_parity.py`
- `tests/test_client_workshop_bootstrap_parity.py`
- `tests/test_ui_menu_files.py`
- `tests/test_client_full_parity_gate.py`

and uploads `artifacts/client_validation/**` so the runtime and gate artifacts stay reviewable outside local machines.

## Closure

`CL-P6` is now considered complete.

`CL-G05` is now considered closed.

With the dedicated gate, the tracked runtime-evidence bundle, and the refreshed top-level ledger wiring in place, the strict native `client` parity estimate now closes at **100%** for the current audited register.
