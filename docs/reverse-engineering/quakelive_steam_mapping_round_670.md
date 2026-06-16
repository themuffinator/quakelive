# Quake Live Steam Mapping Round 670: Legacy Steam P2P, Voice, And Packet Slot Constants

Date: 2026-06-16

## Scope

This pass rechecked the legacy Steamworks wiring that SRP keeps for Quake Live's
retail Steam voice, P2P relay, and GameServer UDP packet bridge. The goal was
not to enable live online services by default, but to name the retail vtable
slots already reconstructed in `platform_steamworks.c` so later Steamworks work
can distinguish observed retail ABI shape from SRP compatibility plumbing.

Focused parity estimate: **before 90% -> after 99%** for legacy
SteamNetworking, ISteamUser voice, and ISteamGameServer packet slot
source-shape confidence. Overall Steam launch/runtime integration mapping
confidence moves from **93.64% -> 93.66%**. Repo-wide parity remains **99%**
because this pass closes a source mapping gap inside the opt-in Steamworks lane
without changing the strict-retail Windows replacement score.

## Evidence

| Retail symbol | Current alias | Observed slot evidence |
| --- | --- | --- |
| `FUN_00460d10` / `sub_460d10` | `SteamVoice_SendCapturedPacket` | Captures voice with `SteamUser + 0x28` and sends the compressed payload through `SteamNetworking` slot `0`. |
| `FUN_00461a60` / `sub_461a60` | `SteamVoice_ProcessIncomingPackets` | Polls `SteamNetworking + 4`, reads with `SteamNetworking + 8`, and decompresses through `SteamUser + 0x2c`. |
| `FUN_00465b70` / `sub_465b70` | `SteamServerCallbacks_OnP2PSessionRequest` | Accepts tracked GameServer P2P peers through `SteamGameServerNetworking + 0x0c`. |
| `FUN_00465d50` / `sub_465d50` | `SteamServer_HandleIncomingPacket` | Guards on the GameServer initialized flag before forwarding host UDP data through `SteamGameServer + 0x94`. |
| `FUN_00466850` / `sub_466850` | `SteamServer_Frame` | Drains GameServer P2P packets through slots `0`, `4`, and `8`, then drains outgoing UDP packets through `SteamGameServer + 0x98`. |
| `FUN_004605c0` | `SteamClient_GetAuthSessionTicket` | Uses `SteamUser + 0x34` in retail; SRP keeps the existing exported API wrapper path. |
| `FUN_004605f0` | `SteamClient_CancelAuthTicket` | Uses `SteamUser + 0x40` in retail; SRP keeps the existing exported API wrapper path. |
| `FUN_00465fd0` | `SteamServer_BeginAuthSession` | Uses `SteamGameServer + 0x74` after duplicate-auth checks. |
| `FUN_004661e0` | `SteamServer_EndAuthSession` | Uses `SteamGameServer + 0x78` while draining authenticated client state. |

Observed facts:

- `imports.txt` includes `SteamUser`, `SteamNetworking`,
  `SteamGameServer`, and `SteamGameServerNetworking`.
- `functions.csv` contains all mapped retail owners above with stable
  quakelive_steam addresses.
- Binary Ninja HLIL confirms the client voice send/read path, the
  GameServer P2P callback accept slot, the incoming UDP packet bridge slot,
  and the outgoing UDP packet drain slot.
- The same low legacy `ISteamNetworking` slot pattern appears on both the
  client and GameServer networking interfaces, supporting a shared
  `0/1/2/0x0c` constant set for send, availability, read, and accept. Round
  710 later promoted the SteamNetworking and SteamGameServerNetworking harness
  mirror from raw offsets to named harness-local constants.

Inference: the source constants are retail ABI labels for legacy
SteamNetworking and voice/GameServer packet slots, not new behavior. The auth
session ticket wrappers remain intentionally unchanged because the current SRP
source resolves the flat Steam API exports for that path and changing those
calls would be a separate compatibility decision.

## Source Reconstruction

SRP now names the slots used by the reconstructed wrappers:

- `QL_STEAM_NETWORKING_SEND_P2P_PACKET_SLOT`
- `QL_STEAM_NETWORKING_IS_P2P_PACKET_AVAILABLE_SLOT`
- `QL_STEAM_NETWORKING_READ_P2P_PACKET_SLOT`
- `QL_STEAM_NETWORKING_ACCEPT_P2P_SESSION_SLOT`
- `QL_STEAM_USER_START_VOICE_RECORDING_SLOT`
- `QL_STEAM_USER_STOP_VOICE_RECORDING_SLOT`
- `QL_STEAM_USER_GET_VOICE_SLOT`
- `QL_STEAM_USER_DECOMPRESS_VOICE_SLOT`
- `QL_STEAM_USER_GET_VOICE_OPTIMAL_SAMPLE_RATE_SLOT`
- `QL_STEAM_GAMESERVER_HANDLE_INCOMING_PACKET_SLOT`
- `QL_STEAM_GAMESERVER_GET_NEXT_OUTGOING_PACKET_SLOT`

The client and server P2P send/available/read wrappers, client and server P2P
session accept wrappers, voice capture/decompress wrappers, and GameServer
incoming/outgoing UDP packet bridge wrappers now use those names instead of raw
vtable indices.

This pass preserves the existing Steamworks and online-service policy gates.
No live service fallback was added, and the default-disabled
`QL_BUILD_ONLINE_SERVICES` stance remains unchanged.

## Validation

Planned validation for this round:

- `python -m pytest -q tests/test_platform_services.py -k legacy_steam_p2p_voice_packet_slot_constants_round_670`
- `python -m pytest -q tests/test_platform_services.py`
- `python -m pytest -q tests/test_steamworks_harness.py`
- `git diff --check`
