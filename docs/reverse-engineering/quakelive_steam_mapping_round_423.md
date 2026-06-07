# Quake Live Steam Mapping Round 423

Date: 2026-06-07

## Scope

This round reconstructs the retail Steam wrapper surface adjacent to the
already-recovered SteamID and auth-ticket owners. The focus is the small
wrapper cluster for subscription checks, workshop download-info queries, and
SteamUtils IP-country lookup.

## Evidence

- `references/analysis/quakelive_symbol_aliases.json` promotes:
  - `sub_460590` as `SteamApps_BIsSubscribedApp`
  - `sub_460660` as `SteamUGC_GetItemDownloadInfo`
  - `sub_460690` as `SteamUtils_GetIPCountry`
- Ghidra `functions.csv` carries the corresponding rows at `00460590`,
  `00460660`, and `00460690`.
- Binary Ninja HLIL for `quakelive_steam.exe` shows:
  - `sub_460590` checking the retained Steam initialisation flag before calling
    `SteamApps()->BIsSubscribedApp` at vtable slot `0x1c`.
  - `sub_460660` forwarding the item low/high words and counters to
    `SteamUGC()->GetItemDownloadInfo` at vtable slot `0xd8`.
  - `sub_460690` checking the retained Steam initialisation flag before
    tailcalling `SteamUtils()->GetIPCountry` at vtable slot `0x10`.
- Retail `CL_Init` later seeds the `"country"` cvar from `sub_460690` only
  when the current cvar is blank.

## Source Reconstruction

- Added client-owned wrappers:
  - `SteamApps_BIsSubscribedApp(...)`
  - `SteamUGC_GetItemDownloadInfo(...)`
  - `SteamUtils_GetIPCountry(...)`
- The wrappers live beside `SteamClient_GetSteamID(...)` and
  `SteamClient_GetAuthSessionTicket(...)`, refresh the retained Steam service
  state if needed, and return deterministic fallbacks when Steam is disabled or
  unavailable.
- UI import `QL_UI_trap_IsSubscribedApp`, cgame import
  `QL_CG_trap_IsSubscribedApp`, UI workshop download-info import, retained
  client workshop progress polling, and country cvar seeding now route through
  the named retail-style wrapper surface instead of calling the low-level
  platform wrapper directly.
- `qcommon.h`, `null_client.c`, and the C test stubs expose fallback surfaces
  for non-client or default-disabled builds.

## Parity

Focused Steam wrapper-surface confidence moves from 82% to 93%.
The broader Steam launch/runtime integration slice moves from 75% to 76%.
