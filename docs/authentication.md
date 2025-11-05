# Authentication Flow Overview

## Legacy CD-Key Handling

Quake Live inherited Quake III Arena's CD-key workflow. The client stores a 32 character key in `cl_cdkey` and forwards a sanitized version to the authorization service via the `getKeyAuthorize` out-of-band packet. The filtering previously lived entirely inside `CL_RequestAuthorization` in `cl_main.c`, which trimmed non-alphanumeric characters from `cl_cdkey` before contacting the master server.【F:src/code/client/cl_main.c†L888-L928】

The CD-key values themselves are persisted and validated in the common layer. `Com_ReadCDKey` and `Com_AppendCDKey` pull data from `q3key` files and rely on `CL_CDKeyValidate` to guard against malformed input, while `Com_WriteCDKey` saves a sanitized value back to disk.【F:src/code/qcommon/common.c†L2238-L2312】

## New Credential Abstraction

### Credential Structures and Enums

`src/common/auth_credentials.{c,h}` formalizes every credential-related data structure that higher layers interact with.【F:src/common/auth_credentials.h†L7-L47】 Key items include:

- `qlAuthCredentialKind` enumerates supported credential sources. The initial set covers the legacy CD-key plus Steam- and standalone-launcher tokens, with `QL_AUTH_CREDENTIAL_EMPTY` reserved for blank/invalid states.【F:src/common/auth_credentials.h†L7-L21】
- `ql_auth_credential_t` couples a `kind`, byte buffer, and tracked length so calling code can treat credentials generically while preserving platform-specific prefixes.【F:src/common/auth_credentials.h†L17-L21】
- `qlAuthResult` and `ql_auth_response_t` define a uniform contract for future external validation attempts, giving clients a place to propagate user-facing status messages even when no backend exists yet.【F:src/common/auth_credentials.h†L23-L33】

Helper routines centralize conversions between raw strings and the new structures:

- `QL_ParseCredentialString` resolves user-provided text into a typed credential, detecting `steam:` or `standalone:` prefixes before falling back to the CD-key sanitizer used in older builds.【F:src/common/auth_credentials.c†L68-L82】
- `QL_FormatCredentialForAuthorize` serializes a credential for network transport, re-applying prefixes only when needed so that legacy servers still see bare CD-key payloads.【F:src/common/auth_credentials.c†L137-L164】
- `QL_RequestExternalAuth` currently returns `QL_AUTH_RESULT_ERROR` with a descriptive message, but the signature and response container are ready for platform-specific implementations once reverse-engineered endpoints are available.【F:src/common/auth_credentials.c†L119-L135】

### Integration with Existing Client/Server Code

The client’s authorization path (`CL_RequestAuthorization`) now builds its payload through the new abstraction. After honoring `fs_restrict`, the code parses `cl_cdkey` into a `ql_auth_credential_t` and formats it for the out-of-band `getKeyAuthorize` request, allowing Steam or standalone tokens to flow through unchanged.【F:src/code/client/cl_main.c†L886-L918】

On the server side, the authorize challenge code continues to expect raw strings returned by the master server (`SV_GetChallenge` / `SV_AuthorizeIpPacket`). Once external validation is available, these functions will be responsible for interpreting the credential labels and handling non-CD-key responses coming back from the backend.【F:src/code/server/sv_client.c†L52-L205】【F:src/code/server/sv_client.c†L142-L204】

## Credential Consumers That Require Updates

Several legacy code paths still assume CD-keys are the only credential format. Migrating them to the new abstraction will unblock platform tokens and reduce duplicated sanitization logic:

- **Disk persistence (`Com_ReadCDKey`, `Com_AppendCDKey`, `Com_WriteCDKey`)** – These helpers currently store two 16-character halves of a CD-key and rely on `CL_CDKeyValidate`. They need to learn how to serialize credential kind metadata (e.g., prefixes or structured files) and skip CD-key specific validation when non-legacy kinds are present.【F:src/code/qcommon/common.c†L2238-L2342】
- **Client configuration (`cl_cdkey` cvar and mutation helpers)** – The cvar still holds raw CD-key text, and UI utilities swap 16-character blocks around the buffer. Both the cvar definition and helper routines (such as the swapper in `cl_ui.c`) should be reworked to store full credential strings, including platform prefixes, without chunking them into CD-key segments.【F:src/code/qcommon/cvar.c†L642-L668】【F:src/code/client/cl_ui.c†L693-L716】
- **In-game UI (`ui_cdkey.c`, setup and menu flows)** – Menu widgets validate and split CD-keys into four 4-character sections before calling `trap_SetCDKey`. Updating these screens to surface credential type selectors (or entirely hiding the entry fields when external platforms supply tokens) will align the UI with the new abstraction.【F:src/code/q3_ui/ui_cdkey.c†L73-L253】
- **Server authorization messages** – `SV_GetChallenge` and `SV_AuthorizeIpPacket` implicitly treat credentials as CD-keys when composing status strings (`demo`, `accept`, `unknown`). Once the backend starts returning typed credentials or richer denial reasons, these handlers should inspect the credential label and forward human-readable errors to clients, instead of hard-coding CD-key terminology.【F:src/code/server/sv_client.c†L117-L205】

Addressing the above components centralizes credential awareness and prevents legacy assumptions from leaking into platform-specific integrations.

## Prototype External Auth Flows

The stubbed `QL_RequestExternalAuth` function will front every platform-specific authenticator. The following request/response prototypes outline how Steam and standalone backends can plug into the existing data structures while providing actionable errors:

### Steam Backend

1. **Input:** `ql_auth_credential_t` with `kind == QL_AUTH_CREDENTIAL_STEAM` and `value` containing the raw Steam authentication ticket.
2. **Request:** POST (or UDP packet) to a Steam-compatible validation service with fields `{ credentialKind: "steam", ticket: <value>, clientIp, buildId }`.
3. **Success Response:** `{ result: "accepted", sessionToken, expiresAt }` – map to `QL_AUTH_RESULT_ACCEPTED` and store the returned token in `response->message` or a future session cache for later reuse.
4. **Denial Response:** `{ result: "denied", reasonCode, detail }` – map to `QL_AUTH_RESULT_DENIED`, surface `detail` via `response->message`, and let callers fall back to local denial messaging.
5. **Transport/Parsing Errors:** map to `QL_AUTH_RESULT_ERROR` with a generic message; retry policies live with the caller.

### Standalone Launcher Backend

1. **Input:** `ql_auth_credential_t` with `kind == QL_AUTH_CREDENTIAL_STANDALONE_TOKEN` and `value` holding the launcher-issued token (JWT or signed blob).
2. **Request:** POST to the Quake Live backend `{ credentialKind: "standalone", token: <value>, clientIp, hwid? }`.
3. **Success Response:** `{ result: "accepted", profileId, entitlements }` – return `QL_AUTH_RESULT_ACCEPTED` and include entitlement data in `response->message` until richer plumbing exists.
4. **Denial Response:** `{ result: "denied", reasonCode, message }` – map to `QL_AUTH_RESULT_DENIED`, copying `message` into the response buffer for UI display.
5. **Expired/Invalid Tokens:** treat as `QL_AUTH_RESULT_ERROR` with `"Token expired"` or similar copy so the caller can prompt the launcher for a refresh.

Both backends should adhere to the `ql_auth_response_t` contract by always populating a short status string, enabling legacy callers to print informative console text without additional parsing logic.【F:src/common/auth_credentials.h†L23-L33】
