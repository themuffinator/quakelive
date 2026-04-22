# `src/common/platform/backends/platform_backend_open_steam.c` Gap Note

Last updated: 2026-04-22

Gap family: `RW-G01`
- Owning retail binary: `assets/quakelive/quakelive_steam.exe` for engine-owned surfaces, or the corresponding committed module corpus when this file sits in a module tree.
- Current classification: Open repo-wide gap; this backend is currently a heuristic compatibility surface.

## Why this file is still open

The open adapter backend still decides accept, retry, and deny outcomes from token length and substring heuristics rather than from a transport-backed exchange with a documented open replacement service.

## Observed facts

- Standalone launcher tokens are accepted, retried, or denied based on payload length and substring checks such as `refresh`, `revoke`, and `denied`.
- Steam fallback tickets are also accepted or denied from local string inspection rather than an external validation path.
- The response payloads now explicitly call themselves an `Open adapter heuristic compatibility backend`, which keeps the bounded lane visible in auth logs and scripted QA traces.
- The file is honest about being a bounded compatibility path, but it is still not a retail-equivalent service implementation.

## Function-by-function status

| Function | Status | Notes |
| --- | --- | --- |
| `QL_PlatformBackendOpenSteam_Authenticate` | `gap owner` | Entire heuristic open-adapter compatibility backend; its response payloads now self-identify as such. |

## Closure target

- Replace the heuristic token-shape logic with a documented open transport path if this lane is meant to count toward repo-wide closure.
- If the lane remains bounded permanently, keep this note open as the explicit evidence that the repo-wide score still excludes real online-service parity.
