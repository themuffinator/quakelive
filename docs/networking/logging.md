# Connection Logging and Authentication Telemetry

## Steam credential capture during `SV_DirectConnect`
* `client_t` now tracks the platform credential label, raw token, most recent status message, and the presented SteamID so the server can describe what happened during each stage of the handshake.【F:src/code/server/server.h†L124-L150】
* `SV_CapturePlatformAuthFromUserinfo` normalises the userinfo keys used by Quake Live (`auth`, `author`, `author2`, and `steamid`) and preserves the results before the VM gets a chance to mutate the string. Each transition (`connect`, `denied`, `accepted`) is reported through `NET_LogAuthTelemetry`, producing a consolidated log that mirrors the native binaries.【F:src/code/server/sv_client.c†L28-L127】【F:src/code/server/sv_client.c†L525-L561】

## Game-side validation via `ClientConnect`
* `G_RunPlatformAuthChecks` reconstructs the Steam ticket from userinfo, converts it into a `ql_auth_credential_t`, and forwards the request to the platform abstraction (`QL_RequestExternalAuth`). Any rejection bubbles back to the engine as "Failed to verify Steam auth token", matching the Quake Live denial string. Successful validations emit a `SteamAuthAccepted` telemetry line for the server log.【F:src/code/game/g_client.c†L25-L107】
* `ClientConnect` invokes the helper before bot setup, short-circuiting the join when validation fails and only advertising the `steamid` once the credential passes the external check.【F:src/code/game/g_client.c†L1035-L1077】

## Shared telemetry emitter
* `NET_LogAuthTelemetry` is a new qcommon utility that formats the direction, address, credential label, SteamID, and status string in a single line, giving both the dedicated server and in-process host the same visibility without duplicating string handling.【F:src/code/qcommon/net_chan.c†L744-L763】
