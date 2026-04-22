# `src/common/platform/platform_config.h` Gap Note

Last updated: 2026-04-22

Gap family: `RW-G01`
- Owning retail binary: `assets/quakelive/quakelive_steam.exe` for engine-owned surfaces, or the corresponding committed module corpus when this file sits in a module tree.
- Current classification: Open repo-wide gap; strict-retail Windows closure intentionally excludes this compatibility-only build lane.

## Why this file is still open

This header defaults `QL_BUILD_ONLINE_SERVICES` to `0` and forces both provider macros off in the default build, so the repo still does not claim retail-equivalent online-service behavior in the checked-in default configuration.

## Observed facts

- `QL_BUILD_ONLINE_SERVICES` defaults to `0` when no override is supplied.
- When online services are disabled, both `QL_BUILD_STEAMWORKS` and `QL_BUILD_OPEN_STEAM` are forced to `0` as well.
- The derived `QL_PLATFORM_HAS_*` and `QL_PLATFORM_BUILD_HYBRID` macros therefore advertise a bounded compatibility story instead of retail live-service parity in default builds.
- The surrounding service layer now mirrors those macro-derived states into overall mode/policy summary labels and ROM cvars, which makes the default-disabled and opt-in heuristic lanes explicit at runtime without changing the underlying repo-wide gap.

## Surface-by-surface status

| Surface | Status | Notes |
| --- | --- | --- |
| `QL_BUILD_ONLINE_SERVICES` | `gap owner` | Defaults to `0`, which keeps the whole online-service lane outside repo-wide closure. |
| `QL_BUILD_STEAMWORKS` | `bounded compatibility` | Forced off in the default build unless online services are explicitly enabled. |
| `QL_BUILD_OPEN_STEAM` | `bounded compatibility` | Forced off in the default build unless online services are explicitly enabled. |
| `QL_PLATFORM_HAS_ONLINE_SERVICES` | `derived compatibility flag` | Mirrors the bounded build policy rather than proving a retail-equivalent service surface. |
| `QL_PLATFORM_HAS_STEAMWORKS` | `derived compatibility flag` | Only reports an opted-in build capability. |
| `QL_PLATFORM_HAS_OPEN_STEAM` | `derived compatibility flag` | Only reports an opted-in build capability. |
| `QL_PLATFORM_BUILD_HYBRID` | `derived compatibility flag` | Advertises a hybrid fallback lane rather than a retail live-service closure claim. |
| `QL_PLATFORM_HAS_STEAM_SERVICES` | `derived compatibility flag` | Reports bounded Steam-facing service availability, not repo-wide parity closure. |

## Closure target

- Either keep the default-disabled policy as a permanent documented divergence or replace it with a real open service path that can be claimed as equivalent for the repo-wide score.
- When the policy changes, the surrounding service table, auth dispatch, and runtime evidence need to be refreshed together so this header does not drift from the rest of the lane.
