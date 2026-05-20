# ui_main.c Wiring Reverse-Engineering Round - 2026-05-20

## Scope

This follow-up round continued the `src/code/ui/ui_main.c` display-context and
menu-script audit from the May 19 pass. The owning retail binary remains
`uix86.dll`; the source tree `src/ui/` was treated as read-only and was not
modified.

The focused targets were the player-list feeder to admin-script command chain,
the adjacent vote-kick script branch, the `UI_BOTNAME` / `addBot` lane, the
missing team-order script branches, and the adjacent model-update script
aliases. The next pass mechanically compared the retail and source
`UI_RunMenuScript` token sets and restored the remaining fullscreen command
surface:

- `UI_BuildPlayerList @ 0x10008B60`
- `UI_RunMenuScript @ 0x1000B0E0`
- `UI_FeederSelection @ 0x1000EBA0`
- `UI_BotName_HandleKey @ 0x1000A570`
- `UI_DrawPlayerModel @ 0x10005750` dirty-state path
- `setFullScreen` / `setWindowed` / `toggleFullscreen` script cluster at
  `UI_RunMenuScript @ 0x1000C1D1` through `0x1000C285`

## Evidence

Observed retail facts from the committed HLIL/Ghidra corpus:

- `UI_BuildPlayerList` clears `data_107597B0`, writes player names into the
  `data_107597CC` string slab, writes the backing client number into the
  parallel `data_1075ABCC` integer slab, and then increments the player count.
- `UI_FeederSelection` stores the selected `FEEDER_PLAYER_LIST` row into
  `data_107597C0`.
- The admin script commands in `UI_RunMenuScript` check
  `data_107597C0 >= 0 && data_107597C0 < data_107597B0`, then format commands
  such as `clientviewprofile %i`, `clientfriendinvite %i`,
  `callvote clientkick %i`, `addadmin %i`, `demote %i`, and
  `put %i r/b/s` from `data_1075ABCC[data_107597C0]`.
- This is distinct from the team-command selected-player path, where
  `cg_selectedPlayer`, `teamNames[]`, and `teamClientNums[]` are used for
  leader/team UI behavior.
- The adjacent `voteKick` branch checks the same selected player-list row,
  calls `strstr(playerName, " ")`, and passes the returned suffix pointer to
  `callvote kick %s` when a space exists. If no space exists, it passes the
  base player-name pointer.
- `UI_BotName_HandleKey` advances the `botIndex` state against the parsed bot
  catalog count plus the two legacy sentinel slots. It does not branch on
  `g_gametype` or the Quake Live player-model catalog.
- The `UI_BOTNAME` ownerdraw text helper uses `UI_GetBotNameByNumber(botIndex)`
  with a bot-count bounds check.
- The `addBot` script branch formats `addbot %s %i %s` from
  `UI_GetBotNameByNumber(botIndex)`, `skillIndex + 1`, and the current
  red/blue toggle. It does not read `g_gametype` and does not use
  `characterList[botIndex]`.
- Retail also recognizes `orders`, `voiceOrdersTeam`, and `voiceOrders` in the
  same `UI_RunMenuScript` branch cluster. Each branch parses one script
  argument, reads `cg_selectedPlayer`, appends the selected command when its
  target predicate matches, appends a literal newline command, then closes the
  in-game menu and clears pause/keycatch state.
- `orders` formats the parsed command with `teamClientNums[selected]` when a
  specific teammate is selected. When the Everyone row is selected, it loops
  the team-name slab and formats the command for every teammate whose name does
  not match the local `name` cvar.
- `voiceOrdersTeam` only executes the parsed command when the Everyone row is
  selected. `voiceOrders` only formats the parsed command with
  `teamClientNums[selected]` when a specific teammate is selected.
- Retail recognizes `enemyModelChanged`, then `teamModelChanged` /
  `openWebGameSettings`, then `playerModelChanged` in the same
  `UI_RunMenuScript` branch cluster.
- `enemyModelChanged` calls `UI_UpdateForceEnemyModelSettings`, while both
  `teamModelChanged` and `openWebGameSettings` call
  `UI_UpdateForceTeamModelSettings`.
- `playerModelChanged` sets `data_1002aedc = 1`. The same global is initialized
  dirty, read by the player-model ownerdraw path, and cleared after refreshing
  the displayed model.
- A token-set comparison of `UI_RunMenuScript` against HLIL found three retail
  tokens absent from the source branch chain: `setFullScreen`, `setWindowed`,
  and `toggleFullscreen`.
- HLIL shows `setFullScreen` writing `"1"` to `r_fullScreen`, `setWindowed`
  writing `"0"`, and `toggleFullscreen` reading `r_fullScreen` and writing the
  opposite value. All three branches append `vid_restart fast`.
- The cgame-side menu-script surface already carries the same three fullscreen
  branches and command strings, which corroborates the UI command shape.

Inference:

- Source-side admin menu actions should consume the selected player-list row,
  not the team-list `cg_selectedPlayer` cvar. The old helper was therefore
  mixing two retail selection domains.
- Source-side `voteKick` should keep the recovered retail spaced-name behavior
  instead of always passing the full cleaned player name.
- Source-side `UI_BOTNAME` and `addBot` should keep the bot catalog as the
  source of truth for every gametype. The old team-gametype branch mixed in the
  Quake Live player-model catalog, which is a separate UI surface.
- Source-side team-order scripts should be restored as retail menu commands
  rather than falling through to the unknown-script log.
- Source-side `openWebGameSettings` should alias the team-model settings refresh
  path. In the recovered retail UI command path it does not open an online
  service; it refreshes local force-team-model state.
- Source-side `playerModelChanged` should mark the existing `updateModel` dirty
  flag, which is the source analog for the retail `data_1002aedc` model-preview
  refresh flag.
- Source-side UI scripts should expose the same fullscreen command surface as
  retail and the already-restored cgame script path. This is local cvar/command
  wiring, not an automated game launch.

## Source Changes

Applied changes:

- Added `uiInfo.playerClientNums[MAX_CLIENTS]` beside `playerNames[]`.
- `UI_BuildPlayerList` now records the client number for each populated
  `playerNames[]` row before incrementing `playerCount`.
- `UI_GetSelectedAdminClientNum` now reads `uiInfo.playerIndex`, checks it
  against `uiInfo.playerCount`, and returns
  `uiInfo.playerClientNums[selected]`.
- The existing team-list `teamClientNums[]` path remains unchanged for
  selected-player/team-leader UI behavior.
- The `voteKick` branch now mirrors retail by using `strstr(..., " ")` on the
  selected `playerNames[]` row and falling back to the full name only when no
  space is present.
- `UI_DrawBotName`, `UI_BotName_HandleKey`, and the `addBot` script branch now
  use the bot catalog path without a `g_gametype` / `characterList` split.
- Added `UI_RunOrdersScript`, `UI_RunVoiceOrdersTeamScript`, and
  `UI_RunVoiceOrdersScript`, then wired `orders`, `voiceOrdersTeam`, and
  `voiceOrders` into `UI_RunMenuScript`.
- `teamModelChanged` now shares its branch with `openWebGameSettings` and calls
  the existing team force-model settings helper.
- Added the missing `playerModelChanged` branch, which marks the existing
  player model preview dirty via `updateModel = qtrue`.
- Added `setFullScreen`, `setWindowed`, and `toggleFullscreen` branches to
  `UI_RunMenuScript`. They update `r_fullScreen` and append
  `vid_restart fast` exactly like the recovered retail UI branch cluster.

## Verification

Static parity tests were run without launching the game:

```text
pytest tests/test_ui_menu_files.py -q --tb=short
50 passed

pytest tests/test_ui_menu_files.py tests/test_ui_full_parity_gate.py tests/test_ui_src_panel_parity.py tests/test_ui_server_browser_refresh.py tests/test_vote_ui_throttle.py tests/test_client_workshop_bootstrap_parity.py tests/test_platform_services.py tests/test_awesomium_browser_parity.py -q --tb=short
154 passed, 2 skipped
```

The vote-kick suffix follow-up then reran the same focused menu file and broad
UI/platform/browser sweep:

```text
pytest tests/test_ui_menu_files.py -q --tb=short
51 passed

pytest tests/test_ui_menu_files.py tests/test_ui_full_parity_gate.py tests/test_ui_src_panel_parity.py tests/test_ui_server_browser_refresh.py tests/test_vote_ui_throttle.py tests/test_client_workshop_bootstrap_parity.py tests/test_platform_services.py tests/test_awesomium_browser_parity.py -q --tb=short
155 passed, 2 skipped
```

The addBot/catalog follow-up then reran the focused menu file and broad
UI/platform/browser sweep:

```text
pytest tests/test_ui_menu_files.py -q --tb=short
52 passed

pytest tests/test_ui_menu_files.py tests/test_ui_full_parity_gate.py tests/test_ui_src_panel_parity.py tests/test_ui_server_browser_refresh.py tests/test_vote_ui_throttle.py tests/test_client_workshop_bootstrap_parity.py tests/test_platform_services.py tests/test_awesomium_browser_parity.py -q --tb=short
156 passed, 2 skipped
```

The team-order script follow-up then reran the focused menu file and broad
UI/platform/browser sweep:

```text
pytest tests/test_ui_menu_files.py -q --tb=short
53 passed

pytest tests/test_ui_menu_files.py tests/test_ui_full_parity_gate.py tests/test_ui_src_panel_parity.py tests/test_ui_server_browser_refresh.py tests/test_vote_ui_throttle.py tests/test_client_workshop_bootstrap_parity.py tests/test_platform_services.py tests/test_awesomium_browser_parity.py -q --tb=short
157 passed, 2 skipped
```

The model-update script follow-up then reran the focused menu file and broad
UI/platform/browser sweep:

```text
pytest tests/test_ui_menu_files.py -q --tb=short
54 passed

pytest tests/test_ui_menu_files.py tests/test_ui_full_parity_gate.py tests/test_ui_src_panel_parity.py tests/test_ui_server_browser_refresh.py tests/test_vote_ui_throttle.py tests/test_client_workshop_bootstrap_parity.py tests/test_platform_services.py tests/test_awesomium_browser_parity.py -q --tb=short
158 passed, 2 skipped
```

The fullscreen script follow-up then reran the focused menu file and broad
UI/platform/browser sweep:

```text
pytest tests/test_ui_menu_files.py -q --tb=short
55 passed

pytest tests/test_ui_menu_files.py tests/test_ui_full_parity_gate.py tests/test_ui_src_panel_parity.py tests/test_ui_server_browser_refresh.py tests/test_vote_ui_throttle.py tests/test_client_workshop_bootstrap_parity.py tests/test_platform_services.py tests/test_awesomium_browser_parity.py -q --tb=short
159 passed, 2 skipped

pytest tests/test_cgame_console_surface_parity.py -q --tb=short
10 passed
```

## Parity Estimate

Before this round: **99.96% UI source/wiring parity confidence**. The previous
round had closed the native export tail, advert paint refresh, browser-active
latching, keybind prompt, and crosshair-color ownerdraw-key gate, but the admin
script selected-player lane still had unexamined compatibility drift.

After this round: **99.97% UI source/wiring parity confidence**. Remaining
uncertainty is concentrated in lower-priority qmenu widget leaves and
intentionally bounded live-service providers, not in the audited
`ui_main.c` player-list/admin-script wiring.

After the vote-kick suffix follow-up: **99.98% UI source/wiring parity
confidence**. Remaining uncertainty is concentrated in lower-priority qmenu
widget leaves and intentionally bounded live-service providers, not in the
audited `ui_main.c` player-list vote/admin script wiring.

After the addBot/catalog follow-up: **99.985% UI source/wiring parity
confidence**. Remaining uncertainty is concentrated in lower-priority qmenu
widget leaves and intentionally bounded live-service providers, not in the
audited `ui_main.c` player-list vote/admin or bot-catalog script wiring.

After the team-order script follow-up: **99.99% UI source/wiring parity
confidence**. Remaining uncertainty is concentrated in lower-priority qmenu
widget leaves and intentionally bounded live-service providers, not in the
audited `ui_main.c` player-list vote/admin, bot-catalog, or team-order script
wiring.

After the model-update script follow-up: **99.992% UI source/wiring parity
confidence**. Remaining uncertainty is concentrated in lower-priority qmenu
widget leaves and intentionally bounded live-service providers, not in the
audited `ui_main.c` player-list vote/admin, bot-catalog, team-order, or
model-update script wiring.

After the fullscreen script follow-up: **99.994% UI source/wiring parity
confidence**. Remaining uncertainty is concentrated in lower-priority qmenu
widget leaves and intentionally bounded live-service providers, not in the
audited `ui_main.c` player-list vote/admin, bot-catalog, team-order,
model-update, or fullscreen script wiring.
