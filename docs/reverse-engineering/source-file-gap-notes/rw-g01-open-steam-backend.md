# `src/common/platform/backends/platform_backend_open_steam.c` Divergence Note

Last updated: 2026-04-22

Gap family: `RW-G01`
- Owning retail binary: `assets/quakelive/quakelive_steam.exe` for engine-owned surfaces, or the corresponding committed module corpus when this file sits in a module tree.
- Current classification: Documented repo-wide divergence; this backend intentionally remains a heuristic compatibility surface.

## Why this file remains a documented divergence

The open adapter backend still decides accept, retry, and deny outcomes from token length and substring heuristics rather than from a transport-backed exchange with a documented open replacement service.

## Observed facts

- Standalone launcher tokens are accepted, retried, or denied based on payload length and substring checks such as `refresh`, `revoke`, and `denied`.
- Steam fallback tickets are also accepted or denied from local string inspection rather than an external validation path.
- The file is honest about being a bounded compatibility path, but it is still not a retail-equivalent service implementation.

## Function-by-function status

| Function | Status | Notes |
| --- | --- | --- |
| `QL_PlatformBackendOpenSteam_Authenticate` | `divergence owner` | This file is entirely the current heuristic open-adapter compatibility backend. |

## Maintenance expectations

- If this lane stays bounded, keep the heuristic token-shape logic documented as intentional compatibility behavior.
- If a documented open transport path is adopted later, replace the heuristics and refresh the surrounding auth evidence together.
