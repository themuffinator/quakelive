# Quake Live Steam Mapping Round 422

Date: 2026-06-07

## Scope

This round tightens the Steam launch/runtime auth-ticket lane around the
retail `SteamClient_GetAuthSessionTicket` and `SteamClient_CancelAuthTicket`
owners.

## Evidence

- Binary Ninja HLIL for `quakelive_steam.exe` shows `sub_4605c0` calling
  `SteamUser()->GetAuthSessionTicket`, storing the returned handle in
  `data_e2c208`, and returning the ticket length.
- The adjacent `sub_4605f0` wrapper calls `SteamUser()->CancelAuthTicket` with
  `data_e2c208`.
- Retail `CL_CheckForResend` calls `sub_4605c0(...)`, then
  `SteamClient_GetSteamID()`, then builds the binary `"getchallenge "` payload
  containing the two SteamID words and ticket bytes.
- Retail error cleanup calls `sub_4605f0()` before the deeper client/system
  shutdown lane.
- Ghidra metadata confirms the 32-bit Windows retail corpus shape
  (`function_count=5473`, `import_count=351`) and imports `SteamUser`,
  `SteamApps`, `SteamAPI_Init`, and `SteamAPI_Shutdown`. The function inventory
  carries the wrapper rows at `FUN_004605c0` and `FUN_004605f0`.

## Source Reconstruction

- `cl_main.c` now owns `cl_steamAuthTicketHandle` beside the retained Steam
  client initialization flag.
- `SteamClient_GetAuthSessionTicket(...)` refreshes and latches the Steam
  service state if needed, requests the ticket through the low-level
  Steamworks wrapper, retains the handle, and cancels any previously retained
  handle before replacing it.
- `SteamClient_CancelAuthTicket()` cancels and clears the retained handle.
- `ql_auth.c` no longer owns the live Steam ticket handle. It requests auth
  ticket material through `SteamClient_GetAuthSessionTicket(...)` for both the
  backend credential path and the retail binary getchallenge payload path.
- Disconnect, Steam callback shutdown, and decode-failure cleanup now share
  the same client Steam cancellation owner.
- `null_client.c` and the C probe stubs carry zero-return/fallback
  implementations so non-client and default-disabled builds keep the same
  qcommon surface without enabling live Steam.

## Parity

Focused Steam auth-ticket lifetime ownership confidence moves from 74% to 90%.
The broader Steam launch/runtime integration slice moves from 73% to 75%.
