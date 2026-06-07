# Quake Live Steam Mapping Round 421

Date: 2026-06-07

## Scope

This round tightens the Steam launch/runtime identity lane around the retail
`SteamClient_GetSteamID` owner and its early filesystem use.

## Evidence

- Binary Ninja HLIL for `quakelive_steam.exe` shows `sub_460550` returning
  zero while `data_e30218` is clear, then calling `SteamUser()->GetSteamID()`
  through vtable slot `0x08` when the retained Steam API flag is live.
- The same HLIL `FS_Startup` region checks `sub_460510()` before deriving the
  Win32 `fs_homepath`; when Steam is live it calls `sub_460550()` and formats
  `"%s/%llu"` from `fs_basepath` plus the local SteamID.
- The promoted symbol map already names `sub_460510` as
  `SteamClient_IsInitialized` and `sub_460550` as `SteamClient_GetSteamID`.

## Source Reconstruction

- `cl_main.c` now exposes `SteamClient_GetSteamID()` as the client-owned
  wrapper. It returns `0` while the retained Steam flag is unavailable,
  refreshes platform services if the flag is stale, latches the refreshed Steam
  state, and returns the local SteamID64 from `QL_Steamworks_GetUserSteamID(...)`.
- `files.c` now asks `SteamClient_GetSteamID()` for the Win32
  `fs_homepath` SteamID suffix instead of reaching directly into the
  Steamworks wrapper.
- Client auth, web-host bootstrap, voice speaking state, persona refresh, and
  lobby ownership checks now share the same retained Steam identity owner.
- `null_client.c` carries a zero-return stub so non-client builds keep the same
  qcommon surface without enabling live Steam.

## Parity

Focused Steam launch/runtime identity ownership confidence moves from 72% to
88%. The broader Steam launch/runtime integration slice moves from 70% to 73%.
