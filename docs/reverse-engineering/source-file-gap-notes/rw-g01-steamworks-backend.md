# `src/common/platform/backends/platform_backend_steamworks.c` Gap Note

Last updated: 2026-04-22

Gap family: `RW-G01`
- Owning retail binary: `assets/quakelive/quakelive_steam.exe` for engine-owned surfaces, or the corresponding committed module corpus when this file sits in a module tree.
- Current classification: Open repo-wide gap; this backend still resolves auth outcomes heuristically.

## Why this file is still open

The Steamworks auth backend currently uses local ticket-length and substring heuristics to decide accepted, pending, or denied outcomes, so it remains a bounded compatibility surface rather than direct proof of retail-equivalent live-service behavior.

## Observed facts

- Short tickets are denied immediately as malformed.
- The backend returns `PENDING` on string matches such as `retry` and denies tickets containing `denied` or `invalid`.
- Accepted responses are still generated locally from ticket shape rather than a live validation exchange.
- The response payloads now explicitly call themselves a `Steamworks heuristic compatibility backend`, which keeps the bounded lane visible in auth logs and scripted QA traces.

## Function-by-function status

| Function | Status | Notes |
| --- | --- | --- |
| `QL_PlatformBackendSteamworks_Authenticate` | `gap owner` | Entire heuristic Steamworks auth backend; its response payloads now self-identify as such. |

## Closure target

- Replace the heuristic accept or retry mapping with a real validated path if repo-wide online-service parity becomes a target.
- Until then, keep the file documented as a compatibility backend and leave the repo-wide gap open.
