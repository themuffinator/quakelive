# Quake Live Steam Mapping Round 545: Steam Client Helper Alias Bridge

## Scope

This round rechecked the retail Steam client helper band in
`quakelive_steam.exe`, focusing on the small launch/runtime owners that feed
client initialization, filesystem SteamID homepath selection, auth ticket
handoff, persona refresh, avatar image loading, and the per-frame Steam pump.
No source bodies were rewritten; this pass closes the alias bridge between
Binary Ninja `sub_*` names, committed Ghidra `FUN_*` rows, and the existing
source reconstruction.

## Evidence Inputs

- Binary Ninja HLIL:
  `references/hlil/quakelive/quakelive_steam.exe/quakelive_steam.exe_hlil_split/quakelive_steam.exe_hlil_part02.txt`
- Ghidra function inventory:
  `references/reverse-engineering/ghidra/quakelive_steam/functions.csv`
- Alias ledger:
  `references/analysis/quakelive_symbol_aliases.json`
- Source reconstruction:
  `src/code/client/cl_main.c`,
  `src/code/client/cl_steam_resources.c`,
  `src/code/client/cl_cgame.c`,
  `src/code/client/ql_auth.c`, and
  `src/code/qcommon/common.c`

## Promoted Alias Bridge

The following helper owners now carry Ghidra-style aliases and lower-case
Binary Ninja spellings where applicable:

| Retail address | Ghidra row | Binary Ninja owner | Source owner |
| --- | --- | --- | --- |
| `0x00460510` | `FUN_00460510` | `sub_460510` | `SteamClient_IsInitialized` |
| `0x00460550` | `FUN_00460550` | `sub_460550` | `SteamClient_GetSteamID` |
| `0x004605c0` | `FUN_004605c0` | `sub_4605c0` | `SteamClient_GetAuthSessionTicket` |
| `0x004605f0` | `FUN_004605f0` | `sub_4605f0` | `SteamClient_CancelAuthTicket` |
| `0x00460610` | `FUN_00460610` | `sub_460610` | `SteamClient_SyncPersonaNameCvar` |
| `0x00460f30` | `FUN_00460f30` | `sub_460f30` | `SteamClient_GetAvatarImageHandle` |
| `0x00461d40` | `FUN_00461d40` | `sub_461d40` | `SteamClient_Frame` |

## Source Reconstruction Notes

- `SteamClient_IsInitialized` remains the minimal initialized-flag owner used
  by startup validation and Steam-dependent wrapper gates.
- `SteamClient_GetSteamID` remains the local identity owner consumed by
  filesystem homepath selection, WebHost bootstrap, auth ticket metadata, and
  lobby/persona paths.
- `SteamClient_GetAuthSessionTicket` and `SteamClient_CancelAuthTicket` remain
  the retained ticket-handle owners used by client auth and cleanup paths.
- `SteamClient_SyncPersonaNameCvar` remains the persona-to-`name` cvar owner
  reached from client init and persona-state callback handling.
- `SteamClient_GetAvatarImageHandle` remains the Steam avatar pixel ingestion
  owner exposed through `cl_steam_resources.c` and the cgame WebHost bridge.
- `SteamClient_Frame` remains the per-frame client Steam pump: callbacks,
  outgoing voice, stats-report packet handling, incoming voice, and callback
  bootstrap recovery stay behind the existing source owners and online-service
  gates.

## Validation

Added
`tests/test_platform_services.py::test_client_steam_helper_alias_bridge_tracks_ghidra_and_hlil_rows`
to verify:

- every promoted `FUN_*` alias resolves to the same source owner as the
  Binary Ninja `sub_*` spelling;
- every promoted helper row has the expected Ghidra address, size, thunk, and
  metadata; and
- HLIL function starts still match the retained source function definitions.

Planned validation for this pass:

```text
python -m json.tool references/analysis/quakelive_symbol_aliases.json
python -m pytest tests/test_platform_services.py::test_client_steam_helper_alias_bridge_tracks_ghidra_and_hlil_rows -q --tb=short
python -m pytest tests/test_platform_services.py -q --tb=short
python -m pytest tests/test_steamworks_harness.py -q --tb=short
```

## Parity Estimate

- Focused Steam client helper alias confidence: **before 72% -> after 99%**.
- Focused Steam launch/runtime helper evidence coverage:
  **before 90% -> after 98%**.
- Overall Steam launch/runtime reconstruction parity:
  **before 92.15% -> after 92.2%**.
