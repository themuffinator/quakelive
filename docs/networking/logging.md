# Connection Logging and Authentication Telemetry

## Steam credential capture during `SV_DirectConnect`
* `client_t` now tracks the platform credential label, raw token, most recent status message, and the presented SteamID so the server can describe what happened during each stage of the handshake.【F:src/code/server/server.h†L124-L150】
* `SV_CapturePlatformAuthFromUserinfo` normalises the userinfo keys used by Quake Live (`auth`, `author`, `author2`, and `steamid`) and preserves the results before the VM gets a chance to mutate the string. Each transition (`connect`, `denied`, `accepted`) is reported through `NET_LogAuthTelemetry`, producing a consolidated log that mirrors the native binaries. Even when the join packet lacks a Steam ticket, the telemetry line is tagged with `credential=steam`, ensuring host-side traces clearly identify Steam-aware sessions.【F:src/code/server/sv_client.c†L28-L127】【F:src/code/server/sv_client.c†L525-L561】

## Game-side validation via `ClientConnect`
* `G_RunPlatformAuthChecks` reconstructs the Steam ticket from userinfo, converts it into a `ql_auth_credential_t`, and forwards the request to the platform abstraction (`QL_RequestExternalAuth`). Any rejection bubbles back to the engine as "Failed to verify Steam auth token", matching the Quake Live denial string. Successful validations emit a `SteamAuthAccepted` telemetry line for the server log.【F:src/code/game/g_client.c†L37-L146】
* When the backend denies the ticket—or when the ticket cannot be parsed in the first place—the helper now writes a `SteamAuthRejected` log before returning the denial string so the server trace mirrors Quake Live's failure hooks.【F:src/code/game/g_client.c†L123-L139】
* `ClientConnect` invokes the helper before bot setup, short-circuiting the join when validation fails and only advertising the `steamid` once the credential passes the external check. When Steam metadata is present, the server prints the numeric 64-bit ID (falling back to the raw string if parsing fails) to match the native logging format.【F:src/code/game/g_client.c†L1032-L1124】

## Shared telemetry emitter
* `NET_LogAuthTelemetry` is a new qcommon utility that formats the direction, address, credential label, SteamID, and status string in a single line, giving both the dedicated server and in-process host the same visibility without duplicating string handling.【F:src/code/qcommon/net_chan.c†L744-L763】
