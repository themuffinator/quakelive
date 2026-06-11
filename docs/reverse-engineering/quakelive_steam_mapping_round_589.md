# Quake Live Steam Mapping Round 589: Client P2P Session Request Peer Gate

Date: 2026-06-11

## Scope

This round closes a behavior-level mapping detail in the client-side Steam
`P2PSessionRequest_t` callback path. The goal is to pin why the source accepts
only the currently tracked game-server Steam peer instead of accepting every
incoming client-side SteamNetworking session request.

Focused retail owners:

- client callback target: `sub_45fef0` / `FUN_0045fef0`
- client callback bundle: `sub_4613a0` / `SteamCallbacks_Init`
- source callback owner: `CL_Steam_Client_OnP2PSessionRequest`
- SteamNetworking wrapper: `QL_Steamworks_AcceptP2PSession`

## Evidence

Observed facts:

- Ghidra records `FUN_0045fef0,0045fef0,93,0,unknown`.
- Binary Ninja HLIL for `sub_4613a0` wires the
  `P2PSessionRequest_t` callback slot to `sub_45fef0` and registers it with
  callback id `0x4b2`.
- Binary Ninja HLIL for `sub_45fef0` reads the tracked peer identity through
  `sscanf(ecx + 0x146dfd4, "%llu", &var_c)`, compares the callback SteamID
  words against that parsed peer, and returns without accepting when either
  word differs.
- The accept path calls `SteamNetworking()` and dispatches
  `AcceptP2PSessionWithUser` at SteamNetworking vtable slot `0x0c`.

Inferred mapping:

- `data_146dafc + 0x146dfd4` is the retail client-side storage used to remember
  the current game-server Steam peer. The source equivalent is the retained
  server SteamID configstring, resolved by `CL_GetServerSteamId`.
- The source gate is intentionally narrow and retail-aligned: accept the P2P
  session only when `event->remoteId` equals the tracked server SteamID.
- The compatibility wrapper remains a direct SteamNetworking vtable call and
  does not introduce a modern `ISteamNetworkingSockets` replacement.

## Reconstruction

No runtime source behavior changed in this round. The existing source already
matches the behaviorally important retail branch:

- `CL_GetServerSteamId` parses `CL_STEAM_SERVER_ID_CONFIGSTRING`.
- `CL_Steam_Client_OnP2PSessionRequest` logs and ignores missing or mismatched
  tracked peers.
- `QL_Steamworks_AcceptP2PSession` dispatches SteamNetworking vtable slot
  `0x0c / 4` only after the source callback admits the tracked peer.

Updated `tests/test_platform_services.py`:

- Added a focused parity gate tying the alias map, Ghidra function row, Binary
  Ninja HLIL branch, source tracked-peer gate, SteamNetworking accept wrapper,
  and this mapping note together.

## Confidence

- High that the retail client callback is not a blanket P2P acceptor: the
  parsed tracked-peer comparison dominates the accept call.
- High that the source admission policy matches the retail behavior at the
  reconstructed level: a single retained game-server SteamID controls whether
  the callback calls `AcceptP2PSessionWithUser`.
- Medium that the exact retail backing store for `data_146dafc + 0x146dfd4`
  has been fully named: the source-equivalent configstring role is clear, but
  the retail field owner remains an inferred struct offset.

## Validation

Completed validation:

```text
python -m pytest tests/test_platform_services.py::test_client_p2p_session_request_tracks_retail_peer_accept_gate -q --tb=short
1 passed
python -m pytest tests/test_platform_services.py::test_client_lobby_bootstrap_reconstructs_retail_connect_surface tests/test_platform_services.py::test_platform_steamworks_reconstructs_retail_callback_bundle_registration_surface -q --tb=short
2 passed
python -m pytest tests/test_platform_services.py -q --tb=short
147 passed
git diff --check -- tests/test_platform_services.py docs/reverse-engineering/quakelive_steam_mapping_round_589.md IMPLEMENTATION_PLAN.md
clean except Git LF-to-CRLF working-copy notices
```

No game launch is required for this static mapping round.

## Parity Estimate

- Focused client P2P session-request admission confidence: **before 94% -> after 99%**.
- Focused client callback bundle source/evidence confidence: **before 98% -> after 99%**.
- Overall Steam launch/runtime integration mapping confidence: **93.05% -> 93.08%**.
