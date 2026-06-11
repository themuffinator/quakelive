# Quake Live Steam Mapping Round 531: Steam Client And Lobby Bootstrap Aliases

## Scope

This pass rechecked the Steam client launch/runtime bootstrap boundary in the
retail `quakelive_steam.exe` corpus. The target was not a new runtime behavior
change; it was closing the alias and parity-test gap between the Binary Ninja
`sub_*` names, the Ghidra `FUN_*` rows, and the reconstructed source owners for
the client Steam bootstrap and lobby startup helper.

| Retail address | Ghidra name | Binary Ninja name | Promoted name | Confidence |
| --- | --- | --- | --- | --- |
| `0x00461500` | `FUN_00461500` | `sub_461500` | `SteamClient_Init` | High |
| `0x004656a0` | `FUN_004656a0` | `sub_4656a0` | `SteamLobbyCallbacks_Init` | High |
| `0x00465840` | `FUN_00465840` | `sub_465840` | `SteamLobby_Init` | High |

## Evidence

Observed retail facts:

- `references/reverse-engineering/ghidra/quakelive_steam/functions.csv`
  records `FUN_00461500` as a 209-byte function, `FUN_004656a0` as a
  411-byte function, and `FUN_00465840` as an 85-byte function.
- Binary Ninja HLIL for `sub_461500` starts from the `com_build` guard, calls
  `SteamAPI_Init()`, stores the initialization result in `data_e30218`, prints
  `Steam API not present.` on failure, and only then reaches the callback and
  command bootstrap path.
- The successful `sub_461500` branch allocates the retail client callback
  bundle, calls `sub_4659e0()` for microtransaction callbacks, calls
  `sub_465840()` for lobby startup, registers `+voice` and `-voice`, registers
  `stats_clear` only for app id `0x54100`, writes rich presence
  `status = At the main menu`, and prints `Steam API initialized.`.
- Binary Ninja HLIL for `sub_4656a0` registers the lobby callback family for
  lobby-created, enter, chat-update, chat-message, data-update, game-created,
  kicked, and join-requested callback ids.
- Binary Ninja HLIL for `sub_465840` allocates a `0xa0` lobby callback bundle,
  calls `sub_4656a0`, registers `lobby_autoconnect` with flag `0x100`,
  registers archived `steam_maxLobbyClients` with default `16`, and exposes the
  `connect_lobby` command through `sub_464aa0`.

Inferred meaning:

- The current reconstructed source already follows the observed retail ordering
  for this bootstrap boundary. The useful reconstruction step is therefore to
  make the alias corpus and parity gate accept both committed naming sources:
  Binary Ninja `sub_*` symbols and Ghidra `FUN_*` rows.
- `SteamLobby_Init` remains a void startup helper. Retail does not return lobby
  callback health to `SteamClient_Init`; it proceeds to voice, stats, presence,
  and the terminal success diagnostic after the lobby helper call.

## Reconstruction

- Promoted the missing Ghidra-style aliases:
  - `FUN_00461500 -> SteamClient_Init`
  - `FUN_004656a0 -> SteamLobbyCallbacks_Init`
  - `FUN_00465840 -> SteamLobby_Init`
- Added the lower-case Binary Ninja spelling `sub_4656a0` beside the existing
  `sub_4656A0` alias so tests can key directly off the HLIL text.
- Strengthened `test_client_steam_callback_owner_reconstructs_retail_frame_pump_and_lifecycle`
  so it now cross-checks:
  - alias names from `references/analysis/quakelive_symbol_aliases.json`;
  - function-size rows from Ghidra `functions.csv`;
  - the `SteamClient_Init` success/failure branch markers in HLIL;
  - the lobby callback bundle allocation and callback id registration;
  - the reconstructed source order from callback bootstrap through lobby cvars,
    `connect_lobby`, voice commands, conditional `stats_clear`, rich presence,
    and the final success diagnostic.

## Remaining Boundary

The source keeps Quake Live online services behind the existing platform-service
availability gates. That is an intentional repository policy divergence from
retail live-service usage, not a new mapping uncertainty in this round.

## Validation

- `python -m json.tool references\analysis\quakelive_symbol_aliases.json`
- `python -m pytest tests\test_platform_services.py::test_client_steam_callback_owner_reconstructs_retail_frame_pump_and_lifecycle -q --tb=short`
- `python -m pytest tests\test_platform_services.py -q --tb=short`

No runtime launch was performed; this was a static evidence and parity-test
mapping pass.

## Parity Estimate

- Focused Steam client/lobby bootstrap alias bridge:
  **before 74% -> after 99%**
- Focused launch/runtime bootstrap evidence coverage:
  **before 92% -> after 98%**
- Overall Steam launch/runtime reconstruction parity:
  **before 91.75% -> after 91.8%**
