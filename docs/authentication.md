# Authentication Overview

This note is now a lightweight landing page rather than a second detailed
ledger. The authentication surface spans three different concerns, and each
has an authoritative home:

- `docs/platform/authentication.md`:
  current runtime dispatch, provider labels, and the
  `QL_BUILD_ONLINE_SERVICES` compatibility-only policy boundary.
- `docs/platform/credentials.md`:
  credential persistence, `q3key` layout, and migration behavior for
  `cl_cdkey` / `cl_cdkey_mod`.
- `docs/steam_platform_abstraction.md`:
  the broader build-time/provider plan for Steamworks, open adapters, and
  hybrid compatibility builds.

## Current shape

The reconstructed engine still preserves Quake III Arena's legacy CD-key
heritage, but the active credential path is now typed rather than implicitly
CD-key-only. `src/common/auth_credentials.{c,h}` owns parsing and formatting,
while `src/code/client/ql_auth.c` dispatches external auth requests through the
platform-service table.

That dispatch is intentionally not treated as strict retail reconstruction.
Per the repo policy, Quake Live-only online services remain behind
`QL_BUILD_ONLINE_SERVICES`, default disabled, until a documented open
replacement path exists.

## Code map

- `src/common/auth_credentials.c` and `src/common/auth_credentials.h`:
  credential parsing, formatting, and response/result types.
- `src/code/client/ql_auth.c`:
  client-side request dispatch and provider-specific lifecycle logging.
- `src/common/platform/platform_services.c` and
  `src/common/platform/platform_config.h`:
  provider discovery plus build/runtime policy gating.
- `src/common/platform/backends/`:
  compatibility-only backend shims for Steamworks and open/hybrid flows.
- `src/code/qcommon/common.c`:
  on-disk credential persistence through the `q3key` helpers.

## Verification

- `tests/test_platform_services.py` checks provider-table publication and the
  build-disabled / open / Steam / hybrid policy paths.
- `tools/integration/auth_flow_trace.py` exercises the lifecycle logging and
  outcome mapping used by the client dispatcher.

Use the platform and credential documents above as the canonical detailed
references so this file does not drift out of sync with the active parity
notes.
