# Authentication Flow Overview

## Legacy CD-Key Handling

Quake Live inherited Quake III Arena's CD-key workflow. The client stores a 32 character key in `cl_cdkey` and forwards a sanitized version to the authorization service via the `getKeyAuthorize` out-of-band packet. The filtering previously lived entirely inside `CL_RequestAuthorization` in `cl_main.c`, which trimmed non-alphanumeric characters from `cl_cdkey` before contacting the master server.【F:src/code/client/cl_main.c†L888-L928】

The CD-key values themselves are persisted and validated in the common layer. `Com_ReadCDKey` and `Com_AppendCDKey` pull data from `q3key` files and rely on `CL_CDKeyValidate` to guard against malformed input, while `Com_WriteCDKey` saves a sanitized value back to disk.【F:src/code/qcommon/common.c†L2238-L2312】

## New Credential Abstraction

To support modern distribution platforms, `src/common/auth_credentials.{c,h}` introduces a unified representation for credentials sourced from CD-keys, Steam tickets, or other platform tokens.【F:src/common/auth_credentials.h†L3-L46】【F:src/common/auth_credentials.c†L1-L120】 Key entry points include:

- `QL_ParseCredentialString` – Detects credential prefixes like `steam:` or `standalone:` and dispatches to the appropriate parser, defaulting to the legacy CD-key sanitizer.【F:src/common/auth_credentials.c†L56-L75】
- `QL_FormatCredentialForAuthorize` – Produces the payload used in authorization requests, allowing `steam:` or `standalone:` namespacing while preserving the legacy behavior for CD-keys.【F:src/common/auth_credentials.c†L97-L120】
- `QL_RequestExternalAuth` – Stubbed hook for future API calls to Steam or other services. It currently records that no backend is available, giving callers a consistent failure path.【F:src/common/auth_credentials.c†L82-L96】

The client now invokes these helpers when preparing an authorization packet. The legacy CD-key sanitizer has been replaced with `QL_ParseCredentialString` and `QL_FormatCredentialForAuthorize`, making the outbound payload source-agnostic while keeping the `fs_restrict` override intact.【F:src/code/client/cl_main.c†L888-L928】 This is the primary integration point for migrating from CD-key checks to modern token flows.

## Future Backend Integration Points

`QL_RequestExternalAuth` is deliberately designed to encapsulate remote validation. Implementations can exchange platform-specific tickets for `QL_AUTH_RESULT_*` responses without modifying callers in the game client. When the Quake Live backend is reconstructed, expected REST or UDP endpoints include:

- Steam session validation (e.g., exchange of `steam:<auth_ticket>` for a signed session token).
- Standalone launcher token verification (e.g., `standalone:<opaque_jwt>`).
- Legacy CD-key fallback for offline or LAN play.

Documenting these entry points ensures future reverse-engineering work can focus on the transport and backend semantics rather than plumbing new credential types through the client.
