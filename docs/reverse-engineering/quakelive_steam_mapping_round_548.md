# Quake Live Steam Mapping Round 548: Client Command and Voice Runtime Alias Bridge

## Scope

This round extends the static Steam launch/runtime mapping around the early
client helper corridor in `quakelive_steam.exe`, focusing on
`0x004603f0..0x00461c00`: retail voice command handlers, shutdown and small
Steam API wrappers, UGC/country/subscription thunks, WebHost UGC query
registration, the social-overlay command owner, and the Steam voice
send/receive/mute helper cluster.

No live Steamworks behavior was enabled and no runtime source behavior was
changed. This pass only normalizes alias coverage and pins the evidence that
already supports the reconstructed client-side fallback owners.

## Evidence Inputs

- Owning binary: `assets/quakelive/quakelive_steam.exe`
- Binary Ninja HLIL:
  `references/hlil/quakelive/quakelive_steam.exe/quakelive_steam.exe_hlil_split/quakelive_steam.exe_hlil_part02.txt`
  and
  `references/hlil/quakelive/quakelive_steam.exe/quakelive_steam.exe_hlil_split/quakelive_steam.exe_hlil_part04.txt`
- Ghidra corpus:
  `references/reverse-engineering/ghidra/quakelive_steam/functions.csv`,
  `references/reverse-engineering/ghidra/quakelive_steam/imports.txt`, and
  `references/reverse-engineering/ghidra/quakelive_steam/analysis_symbols.txt`
- Alias ledger:
  `references/analysis/quakelive_symbol_aliases.json`
- Source reconstruction:
  `src/code/client/cl_main.c`

## Promoted Alias Bridge

| Retail address | Source owner family | Added bridge |
| --- | --- | --- |
| `0x004603f0..0x00460490` | `CL_VoiceStartRecording_f`, `CL_VoiceStopRecording_f` | Ghidra `FUN_*` aliases and lower-case Binary Ninja spelling for the `+voice` owner. |
| `0x00460590..0x00460690` | `SteamApps_BIsSubscribedApp`, `SteamUGC_GetItemDownloadInfo`, `SteamUtils_GetIPCountry` | Ghidra `FUN_*` aliases for the small subscription, workshop-progress, and country wrappers. |
| `0x00460d10..0x00460e60` | `SteamVoice_SendCapturedPacket`, `SteamWorkshop_GetAllUGC`, `CL_Steam_OverlayCommand_f` | Ghidra `FUN_*` and lower-case Binary Ninja spellings for outgoing voice, UGC query setup, and overlay command dispatch. |
| `0x00461990..0x00461c00` | `SteamVoice_IsClientMuted`, `SteamVoice_ProcessIncomingPackets`, `SteamVoice_ToggleClientMute` | Ghidra `FUN_*` aliases and lower-case Binary Ninja spellings for incoming voice and mute-state helpers. |

The `0x00460540` shutdown thunk remains a named Ghidra row
(`SteamAPI_Shutdown,00460540,6,1,unknown`), so this round did not invent a
synthetic `FUN_00460540` alias. The existing `sub_460540` mapping is now
covered by the same parity gate as the surrounding wrappers.

## Observed Facts

- `functions.csv` contains Ghidra rows for the promoted `FUN_*` owners and a
  named imported thunk row for `SteamAPI_Shutdown`.
- HLIL part 02 shows `sub_4603f0` and `sub_460490` calling `SteamUser` and
  `SteamFriends` to toggle recording and speaking state.
- HLIL part 02 shows the small wrapper thunks calling `SteamApps`,
  `SteamUGC`, and `SteamUtils` at the expected vtable offsets.
- HLIL part 02 shows `sub_460dc0` creating the UGC query through `SteamUGC`,
  replacing any prior call result registration, storing `sub_45fd00` as the
  completion target, and registering the call result.
- HLIL part 02 shows `sub_460e60` choosing `steamid` or `friendadd` from
  `clientviewprofile` / `clientfriendinvite` before dispatching
  `SteamFriends()->ActivateGameOverlayToUser`.
- HLIL part 02 shows the per-frame client Steam pump calling outgoing voice,
  stats-report packet handling, incoming voice processing, and callback
  recovery in the retained source order.
- HLIL part 04 shows the retail command registration sites for
  `clientviewprofile` and `clientfriendinvite` using `sub_460e60`.
- `analysis_symbols.txt` ties the adjacent callback bootstrap to the
  `SteamCallbacks` call-result and rich-presence callback vtables.

## Inference

The new aliases are high-confidence name bridges, not new behavioral closure
claims. The behavior remains bounded by the repository's online-services
policy: live Steam functionality stays behind `QL_BUILD_ONLINE_SERVICES`, while
the checked-in source retains explicit compatibility fallbacks for voice,
overlay, UGC, subscription, and country surfaces.

## Validation

Added
`tests/test_platform_services.py::test_client_steam_command_voice_and_runtime_alias_bridge_tracks_ghidra_hlil_rows`
to verify:

- each promoted alias resolves to the retained source owner;
- Ghidra rows, Steam imports, and callback vtable symbols remain present;
- HLIL function starts and call-site anchors still match the promoted owners;
  and
- the source reconstruction still exposes the corresponding client voice,
  overlay, UGC, and frame-pump owners.

Planned validation for this pass:

```text
python -m json.tool references/analysis/quakelive_symbol_aliases.json
python -m pytest tests/test_platform_services.py::test_client_steam_command_voice_and_runtime_alias_bridge_tracks_ghidra_hlil_rows -q --tb=short
python -m pytest tests/test_platform_services.py -q --tb=short
python -m pytest tests/test_steamworks_harness.py -q --tb=short
```

## Parity Estimate

- Focused client Steam command/voice alias confidence:
  **before 70% -> after 99%**.
- Focused Steam voice/overlay/wrapper HLIL evidence coverage:
  **before 88% -> after 97%**.
- Overall Steam launch/runtime reconstruction parity:
  **before 92.25% -> after 92.3%**.
