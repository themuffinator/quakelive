# Residual Policy Spot-Check

Last updated: 2026-06-05

Status: dated spot-check complete; manifest guard added; policy call-site and
ownerdraw follow-up inventories added; ongoing guardrails remain open.

This note records the current spot-check for the two ongoing policy rows in
`docs/plans/2026-06-05-outstanding-work-checklist.md`. No runtime launch was
needed, and no files under `src/ui/` were edited.

## Online Services

No default-policy drift was found.

Observed facts:

- `src/common/platform/platform_config.h` still defaults
  `QL_BUILD_ONLINE_SERVICES` to `0`.
- When that flag is false, `platform_config.h` forces both
  `QL_BUILD_STEAMWORKS` and `QL_BUILD_OPEN_STEAM` to `0`.
- `QL_BuildServiceTable` still publishes
  `Build-disabled (QL_BUILD_ONLINE_SERVICES=0)` descriptors for auth,
  matchmaking, workshop, overlay, and stats in the default build.
- Retained legacy service calls remain behind
  `QL_PLATFORM_HAS_ONLINE_SERVICES && QL_ENABLE_LEGACY_Q3_SERVICES` guards.
- Known Steamworks, open-adapter, Awesomium, and Steam-resource bridge lanes
  are now inventoried and guarded by compile-time or runtime policy checks.
- Online-service call sites in auth, common startup/frame, client Steam
  frame/init, and Windows net restart route through compile-time stubs or
  `CL_SteamServicesEnabled()` runtime checks in the default build.

Policy lane inventory:

| Lane | Source path | Guard |
| --- | --- | --- |
| Steamworks platform wrapper | `src/common/platform/platform_steamworks.c` | `#if QL_BUILD_STEAMWORKS` |
| Steamworks auth backend | `src/common/platform/backends/platform_backend_steamworks.c` | `#if QL_BUILD_STEAMWORKS` |
| Open-adapter auth backend | `src/common/platform/backends/platform_backend_open_steam.c` | `#if QL_BUILD_OPEN_STEAM` |
| Awesomium host adapter | `src/code/client/cl_awesomium_win32.cpp` | `#if QL_BUILD_ONLINE_SERVICES` |
| Awesomium child process | `src/code/win32/awesomium_process.cpp` | `#if QL_PLATFORM_HAS_ONLINE_SERVICES` |
| Steam resource URI bridge | `src/code/client/cl_steam_resources.c` | `CL_SteamServicesEnabled()` runtime checks before live Steam avatar callback/request paths |

Call-site/stub inventory:

| Lane | Source paths | Default guard |
| --- | --- | --- |
| Auth backend dispatch stubs | `src/common/auth_credentials.c`, `src/common/platform/platform_backend_auth.h` | `QL_Auth_ExecuteRequest` tries Open Steam and Steamworks backends, but `platform_backend_auth.h` returns `qfalse` inline when `QL_BUILD_OPEN_STEAM` or `QL_BUILD_STEAMWORKS` are disabled. |
| Steamworks header default stubs | `src/common/platform/platform_steamworks.h` | Live declarations exist only under `#if QL_BUILD_STEAMWORKS`; the default `#else` surface returns `qfalse` for init/server-init calls and no-ops shutdown/callback calls. |
| Common Steam GameServer bootstrap | `src/code/qcommon/common.c` | `Com_InitSteamGameServer` is called from startup/restart paths, but live Steam GameServer calls execute only inside `#if QL_BUILD_STEAMWORKS`. |
| Client Steam frame/init | `src/code/client/cl_main.c` | `SteamClient_Frame` returns unless `CL_SteamServicesEnabled()` and the retained `SteamClient_IsInitialized()` flag succeed; `SteamClient_Init` logs a compatibility fallback when services are disabled. |
| Windows net restart Steam hooks | `src/code/win32/win_net.c` | `NET_Restart` calls Steam shutdown/init hooks, which resolve to the Steamworks no-op stubs and the `Com_InitSteamGameServer` build gate in default builds. |

Targeted source scan:

- Paths: `src/common`, `src/code`.
- Patterns: `QL_BUILD_ONLINE_SERVICES`, `QL_PLATFORM_HAS_ONLINE_SERVICES`,
  `QL_BUILD_STEAMWORKS`, `QL_BUILD_OPEN_STEAM`, `Awesomium`, `Steam`,
  `steam`, `advert`, `matchmaking`, `workshop`, `overlay`, `stats`.
- Classification: policy drift scan; gameplay uses of `stats`/`overlay` were
  treated as search noise unless they touched live service bridges.
- Result: no new default-enabled Quake Live online-service lane was found.

The remaining boundary is unchanged: any Steamworks, open-adapter, browser,
advert, matchmaking, workshop, stats, or other Quake Live-only online-service
replacement remains bounded compatibility unless it is intentionally opted in
and backed by a documented open replacement path.

## Ownerdraw Index

The UI ownerdraw parity index was reviewed before new UI work. Current index
state:

| Bucket | Count |
| --- | ---: |
| Checked | 36 |
| Partial | 1 |
| Needs check | 0 |
| Retail no-op/source legacy | 8 |
| No-op/missing | 1 |
| Sentinel | 1 |

Remaining actions from the index:

1. Complete `UI_KEYBINDSTATUS` from partial coverage to full parity.
2. Audit the retail no-op/source legacy set before any menu-owner changes.
3. Confirm `UI_VOTE_KICK` has no shipped UI ownerdraw usage before marking it
   closed as a no-op.

Follow-up lane inventory:

| Lane | Ownerdraw IDs | Evidence gate |
| --- | --- | --- |
| Keybind status full parity pass | `542` / `UI_KEYBINDSTATUS` | Add the full normal/pending prompt parity pass with the retail `UI_OwnerDraw` and `UI_OwnerDrawWidth` evidence attached before moving the index from partial to checked. |
| Retail no-op/source legacy audit | `521`, `523`, `524`, `525`, `526`, `527`, `543`, `546` | Confirm reachability or unused status for each legacy route, then document whether it stays as compatibility, is gated, or is removed for strict retail parity. |
| Vote-kick no-op reachability | `530` / `UI_VOTE_KICK` | Confirm no shipped menu depends on the ID as a UI ownerdraw before closing it as a documented no-op. |

This does not close the ongoing ownerdraw guardrail; it records that the index
was checked and that the documentation-first path remains correct because
`src/ui/` is read-only for agents.

## Manifest Guard

The spot-check is now backed by
`tests/test_netcode_parity_manifest.py::test_residual_policy_spot_check_guardrails_remain_manifest_backed`.
That assertion ties the narrative note and JSON record back to the source
default-policy macros, the default build-disabled service descriptors, the
legacy Quake III service dual gate, the online-service lane and call-site
stub inventories, the ownerdraw index counts, and the remaining
documentation-first ownerdraw rows. It also asserts that the ownerdraw
follow-up lane inventory still matches the index rows that make the guardrail
ongoing.

No `src/ui/` files were edited for this guard pass.

Repo-wide parity estimate remains **99% -> 99%**.
