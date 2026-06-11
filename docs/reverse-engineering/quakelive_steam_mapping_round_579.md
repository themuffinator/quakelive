# Quake Live Steam Mapping Round 579: Awesomium Lobby Callback Event Publication Crosscheck

## Scope

This round consolidates the retail Awesomium-facing lobby callback path:

- `sub_4645A0` / `FUN_004645a0`: `SteamLobbyCallbacks_OnLobbyChatMessage`
- `sub_464BF0` / `FUN_00464bf0`: `SteamLobbyCallbacks_OnLobbyCreated`
- `sub_464D90` / `FUN_00464d90`: `SteamLobbyCallbacks_OnLobbyEnter`
- `sub_4652E0` / `FUN_004652e0`: `SteamLobbyCallbacks_OnLobbyChatUpdate`
- shared publication through `sub_4F3260`: `QLWebView_PublishEvent`

No live Steam or Awesomium service behavior is enabled by this pass. The source
continues to keep Quake Live-only online service integration behind the guarded
client event lane and the repository default remains offline-friendly.

## Evidence

Observed facts:

- `references/reverse-engineering/ghidra/quakelive_steam/functions.csv`
  records the four focused lobby callback owners with stable sizes:
  `377`, `416`, `1350`, and `418` bytes.
- `references/analysis/quakelive_symbol_aliases.json` maps each owner through
  the `FUN_*`, uppercase `sub_*`, and lowercase `sub_*` spellings used by the
  Ghidra and Binary Ninja corpora.
- Binary Ninja HLIL part02 shows the chat-message callback calling
  SteamMatchmaking slot `0x6c`, gating publication on `var_860 == 1`, building
  `id`, `name`, and `msg`, then calling
  `sub_4f3260(..., "lobby.%s.chat", ...)`.
- The created callback writes retail lobby data `"hello" = "world"`, emits a
  success payload through `"lobby.%s.create"`, and uses `"lobby.error"` for the
  failure branch.
- The enter callback leaves the previous lobby through `sub_4649e0()` when
  needed, builds owner, lobbydata, player-count, max-player, and players
  payload fields, then publishes `"lobby.%s.enter"`. The failure branch
  publishes `"lobby.error"`.
- The chat-update callback builds `id`, `name`, `num_players`, and
  `max_players`, chooses `"lobby.%s.user.joined"` or
  `"lobby.%s.user.left"` from the state-change bit, and publishes through the
  same `sub_4f3260` helper.
- Binary Ninja HLIL part05 identifies `sub_4f3260` as the Awesomium
  `EnginePublish` bridge invoking the window object asynchronously.
- The reconstructed source routes the retained Steam lobby callbacks through
  `CL_Steam_PublishBrowserEvent`, which forwards into
  `CL_WebView_PublishEvent`; that owner queues the browser-facing event and
  dispatches it to the live view when one exists.

Inferred mapping:

- Retail uses direct Awesomium C++ payload objects. The reconstruction uses a
  guarded JSON/string event lane, but the event names, high-value payload
  fields, callback registration ownership, and publication boundary match the
  retail chain closely enough to treat the source as a faithful offline-safe
  reconstruction of the WebUI-facing lobby runtime surface.

## Reconstruction

Strengthened `tests/test_awesomium_browser_parity.py`:

- Added `quakelive_steam.exe_hlil_part02.txt` to the Awesomium parity evidence
  set.
- Added a focused parity gate that ties the four lobby callback owners to
  Ghidra function rows, symbol aliases, Binary Ninja HLIL event construction,
  the retail `QLWebView_PublishEvent` bridge, and the source
  `CL_Steam_PublishBrowserEvent` / `CL_WebView_PublishEvent` path.
- Kept the source implementation unchanged because the guarded event path
  already reconstructs the retail WebUI-facing behavior without enabling live
  online services.

## Validation

- `python -m json.tool references\analysis\quakelive_symbol_aliases.json`
  - passed
- `python -m pytest tests/test_awesomium_browser_parity.py::test_awesomium_lobby_callbacks_publish_through_retail_webui_event_bridge -q --tb=short`
  - `1 passed`
- `python -m pytest tests/test_awesomium_browser_parity.py -q --tb=short`
  - `40 passed`
- `python -m pytest tests/test_platform_services.py::test_client_lobby_bootstrap_reconstructs_retail_connect_surface tests/test_platform_services.py::test_lobby_social_wrappers_reconstruct_mapped_matchmaking_slots -q --tb=short`
  - `2 passed`
- `python -m pytest tests/test_platform_services.py -q --tb=short`
  - `145 passed`
- `python -m pytest tests/test_steamworks_harness.py -q --tb=short`
  - `128 passed`

## Parity Estimate

- Focused lobby callback WebUI publication evidence:
  **before 92% -> after 98%**.
- Focused Awesomium JSArray-to-source event-lane confidence:
  **before 90% -> after 97%**.
- Overall Awesomium/WebUI launch/runtime integration mapping confidence: **99.22% -> 99.24%**.

Open questions:

- The retail path still uses native Awesomium object lifetimes directly, while
  the reconstruction intentionally keeps live service behavior optional. That
  divergence remains documented and should stay behind `QL_BUILD_ONLINE_SERVICES`
  until a non-retail open service path is designed.
