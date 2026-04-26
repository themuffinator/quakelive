# `src/common/platform/backends/platform_backend_steamworks.c` Divergence Note

Last updated: 2026-04-22

Gap family: `RW-G01`
- Owning retail binary: `assets/quakelive/quakelive_steam.exe` for engine-owned surfaces, or the corresponding committed module corpus when this file sits in a module tree.
- Current classification: Documented repo-wide divergence; this backend intentionally resolves auth outcomes heuristically.

## Why this file remains a documented divergence

The Steamworks auth backend currently uses local ticket-length and substring heuristics to decide accepted, pending, or denied outcomes, so it remains a bounded compatibility surface rather than direct proof of retail-equivalent live-service behavior.

## Observed facts

- Short tickets are denied immediately as malformed.
- The backend returns `PENDING` on string matches such as `retry` and denies tickets containing `denied` or `invalid`.
- Accepted responses are still generated locally from ticket shape rather than a live validation exchange.

## Function-by-function status

| Function | Status | Notes |
| --- | --- | --- |
| `QL_PlatformBackendSteamworks_Authenticate` | `divergence owner` | This file is entirely the current heuristic Steamworks auth backend. |

## Maintenance expectations

- If repo-wide online-service parity ever becomes a target, replace the heuristic accept or retry mapping with a real validated path.
- Until then, keep the file documented as a bounded compatibility backend.
