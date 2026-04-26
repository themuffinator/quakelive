# `src/common/platform/platform_config.h` Divergence Note

Last updated: 2026-04-22

Gap family: `RW-G01`
- Owning retail binary: `assets/quakelive/quakelive_steam.exe` for engine-owned surfaces, or the corresponding committed module corpus when this file sits in a module tree.
- Current classification: Documented repo-wide divergence; strict-retail Windows closure intentionally excludes this default-disabled compatibility-only build lane.

## Why this file remains a documented divergence

This header defaults `QL_BUILD_ONLINE_SERVICES` to `0` and forces both provider macros off in the default build, which keeps the checked-in online-service story explicitly bounded instead of over-claiming retail-equivalent behavior.

## Observed facts

- `QL_BUILD_ONLINE_SERVICES` defaults to `0` when no override is supplied.
- When online services are disabled, both `QL_BUILD_STEAMWORKS` and `QL_BUILD_OPEN_STEAM` are forced to `0` as well.
- The derived `QL_PLATFORM_HAS_*` and `QL_PLATFORM_BUILD_HYBRID` macros therefore advertise a bounded compatibility story instead of retail live-service parity in default builds.

## Surface-by-surface status

| Surface | Status | Notes |
| --- | --- | --- |
| `QL_BUILD_ONLINE_SERVICES` | `divergence owner` | Defaults to `0`, which keeps the whole online-service lane explicitly bounded by policy. |
| `QL_BUILD_STEAMWORKS` | `bounded compatibility` | Forced off in the default build unless online services are explicitly enabled. |
| `QL_BUILD_OPEN_STEAM` | `bounded compatibility` | Forced off in the default build unless online services are explicitly enabled. |
| `QL_PLATFORM_HAS_ONLINE_SERVICES` | `derived divergence flag` | Mirrors the bounded build policy rather than proving a retail-equivalent service surface. |
| `QL_PLATFORM_HAS_STEAMWORKS` | `derived divergence flag` | Only reports an opted-in build capability. |
| `QL_PLATFORM_HAS_OPEN_STEAM` | `derived divergence flag` | Only reports an opted-in build capability. |
| `QL_PLATFORM_BUILD_HYBRID` | `derived divergence flag` | Advertises a hybrid fallback lane rather than a retail live-service closure claim. |
| `QL_PLATFORM_HAS_STEAM_SERVICES` | `derived divergence flag` | Reports bounded Steam-facing service availability, not repo-wide parity closure. |

## Maintenance expectations

- Keep the default-disabled policy documented as an intentional divergence unless a real open service path becomes a target.
- When the policy changes, the surrounding service table, auth dispatch, and runtime evidence need to be refreshed together so this header does not drift from the rest of the lane.
