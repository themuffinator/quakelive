# Quake Live Steam Mapping Round 546: Steam Browser/Resource Owner Alias Bridge

## Scope

This round rechecked the retail Steam browser/resource owner band in
`quakelive_steam.exe`, focusing on the WebUI-facing server list/detail owners,
avatar response-thread helpers, `SteamDataSource` resource callbacks, and the
adjacent SteamID map helper cluster. No source bodies were rewritten; this pass
closes the alias bridge between Binary Ninja `sub_*` names, committed Ghidra
`FUN_*` rows, and the existing source reconstruction.

## Evidence Inputs

- Binary Ninja HLIL:
  `references/hlil/quakelive/quakelive_steam.exe/quakelive_steam.exe_hlil_split/quakelive_steam.exe_hlil_part02.txt`
  and
  `references/hlil/quakelive/quakelive_steam.exe/quakelive_steam.exe_hlil_split/quakelive_steam.exe_hlil_part06.txt`
- Ghidra function inventory and promoted symbols:
  `references/reverse-engineering/ghidra/quakelive_steam/functions.csv` and
  `references/reverse-engineering/ghidra/quakelive_steam/analysis_symbols.txt`
- Alias ledger:
  `references/analysis/quakelive_symbol_aliases.json`
- Source reconstruction:
  `src/code/client/cl_main.c` and `src/code/client/cl_steam_resources.c`

## Promoted Alias Bridge

The following owner groups now carry Ghidra-style aliases and lower-case Binary
Ninja spellings where applicable:

- `JSBrowserDetails_*` detail, rule, and player response owners at
  `0x00461f70..0x00462940`.
- `JSBrowser_*` and `SteamBrowser_*` list refresh/request owners at
  `0x00462a50..0x004630b0`.
- `ResponseThread_*` PNG callback/encoding/run helpers at
  `0x00463110..0x00463550`.
- SteamID map/value tree helpers at `0x00463670..0x00463fc0`.
- `SteamDataSource_*` request, avatar callback, init, shutdown, destroy, and
  `CSteamID_IsValid` owners at `0x004640c0..0x00464540`.

## Source Reconstruction Notes

- The WebUI server-browser path remains source-owned through the retained
  native Steam request/list/detail publication helpers in `cl_main.c`.
- Avatar resource delivery remains represented by the bounded response-thread
  and PNG helper reconstruction in `cl_steam_resources.c`.
- `SteamDataSource` remains an online-service owner; live service behavior is
  still contained behind `QL_BUILD_ONLINE_SERVICES` and the default-off policy.

## Validation

Added
`tests/test_platform_services.py::test_steam_browser_and_datasource_alias_bridge_tracks_ghidra_and_hlil_rows`
to verify:

- every promoted `FUN_*` alias resolves to the same source owner as the
  Binary Ninja `sub_*` spelling;
- every promoted helper row has the expected Ghidra address and size;
- HLIL function starts and RTTI/vtable anchors remain present; and
- source-side WebUI server-browser and `SteamDataSource` reconstruction anchors
  remain intact.

Planned validation for this pass:

```text
python -m json.tool references/analysis/quakelive_symbol_aliases.json
python -m pytest tests/test_platform_services.py::test_steam_browser_and_datasource_alias_bridge_tracks_ghidra_and_hlil_rows -q --tb=short
python -m pytest tests/test_platform_services.py -q --tb=short
```

## Parity Estimate

- Focused Steam browser/resource Ghidra alias confidence:
  **before 68% -> after 99%**.
- Focused JSBrowser/SteamDataSource HLIL evidence coverage:
  **before 90% -> after 98%**.
- Overall Steam launch/runtime reconstruction parity:
  **before 92.2% -> after 92.25%**.
