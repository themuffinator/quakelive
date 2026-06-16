# Quake Live Steam Mapping Round 710: Mock SteamNetworking Slot Mirroring

Date: 2026-06-16

## Scope

This pass rechecked the legacy SteamNetworking and SteamGameServerNetworking
mock vtables used by the Steamworks harness. Round 670 named the production
client/server P2P send, availability, read, and accept slots, but the harness
still installed those same mock methods through raw `0x?? / 4` indices. This
pass promotes both test doubles to the same shared vocabulary without changing
production behavior.

Focused parity estimate: **before 88% -> after 99%** for focused
SteamNetworking harness slot-mirroring source-shape confidence. Overall Steam launch/runtime integration mapping confidence moves from **94.02% -> 94.04%**.
Repo-wide parity remains **99%** because this pass only clarifies test-harness
Steamworks ABI wiring, does not change the strict-retail Windows replacement
score, and does not enable live Steam behavior by default.

## Evidence

Observed Ghidra and import facts:

- `functions.csv` preserves `FUN_0045fef0,0045fef0,93,0,unknown` for
  `SteamCallbacks_OnP2PSessionRequest`.
- `functions.csv` preserves `FUN_00460d10,00460d10,170,0,unknown` for
  `SteamVoice_SendCapturedPacket`.
- `functions.csv` preserves `FUN_00461a60,00461a60,400,0,unknown` for
  `SteamVoice_ProcessIncomingPackets`.
- `functions.csv` preserves `FUN_00465b70,00465b70,146,0,unknown` for
  `SteamServerCallbacks_OnP2PSessionRequest`.
- `functions.csv` preserves `FUN_00466850,00466850,827,0,unknown` for
  `SteamServer_Frame`.
- `imports.txt` confirms the retained `SteamNetworking` and
  `SteamGameServerNetworking` imports.
- `analysis_symbols.txt` preserves both P2P session callback vtables:
  `CCallback<class_SteamCallbacks,struct_P2PSessionRequest_t,0>::vftable`
  and
  `CCallback<class_SteamServerCallbacks,struct_P2PSessionRequest_t,1>::vftable`.
- `references/analysis/quakelive_symbol_aliases.json` maps the same owners,
  plus their `sub_*` spellings, to the promoted client and GameServer P2P
  aliases.

Observed Binary Ninja HLIL facts:

- `SteamCallbacks_OnP2PSessionRequest` accepts the tracked client peer through
  `SteamNetworking + 0x0c`.
- `SteamVoice_SendCapturedPacket` sends captured voice through the client
  `SteamNetworking` slot 0.
- `SteamVoice_ProcessIncomingPackets` polls the client interface through
  `SteamNetworking + 4` and reads packets through `SteamNetworking + 8`.
- `SteamServerCallbacks_OnP2PSessionRequest` accepts tracked GameServer peers
  through `SteamGameServerNetworking + 0x0c`.
- `SteamServer_Frame` drains GameServer P2P packets through
  `SteamGameServerNetworking` slots 0, 4, and 8.

Inference: the legacy client and GameServer networking interfaces share the
same low-slot ABI shape for send, availability, read, and accept. Keeping
`QLR_STEAM_NETWORKING_SEND_P2P_PACKET_SLOT` and
`QLR_STEAM_NETWORKING_VTABLE_SLOT_COUNT` local to the harness preserves the
mock boundary while making the ABI mirror explicit.

## Source Reconstruction

`tests/steamworks_harness.c` now names the shared mock SteamNetworking slots:

- `QLR_STEAM_NETWORKING_SEND_P2P_PACKET_SLOT`
- `QLR_STEAM_NETWORKING_IS_P2P_PACKET_AVAILABLE_SLOT`
- `QLR_STEAM_NETWORKING_READ_P2P_PACKET_SLOT`
- `QLR_STEAM_NETWORKING_ACCEPT_P2P_SESSION_SLOT`

`QLR_SteamAPI_SteamNetworking` and
`QLR_SteamAPI_SteamGameServerNetworking` now size their mock vtables with
`QLR_STEAM_NETWORKING_VTABLE_SLOT_COUNT`, derived from the terminal
accept-session slot, and install every method through the named harness slots.

SteamMatchmaking, SteamGameServer, and SteamGameServerStats mock vtables remain
outside this pass.

## Validation

Completed for this pass:

- `python -m pytest -q tests/test_platform_services.py -k "steam_networking_mock_slot_mirroring_round_710 or legacy_p2p_read_boundary_round_366 or client_p2p_session_request_tracks_retail_peer_accept_gate or steam_gameserver_p2p_networking_wrapper_guards_track_round_630 or steam_gameserver_p2p_accept_wrapper_guard_tracks_round_634 or legacy_steam_p2p_voice_packet_slot_constants_round_670" --tb=short` - 6 passed, 243 deselected.
- `python -m pytest -q tests/test_steamworks_harness.py --tb=short` - 132 passed.
- `python -m pytest -q tests/test_platform_services.py --tb=short` - 248 passed, 1 failed because the pre-existing ZMQ Round 698 gate references missing `docs/reverse-engineering/quakelive_steam_mapping_round_698.md`.
- `git diff --check` - passed with existing LF-to-CRLF working-copy warnings only.
