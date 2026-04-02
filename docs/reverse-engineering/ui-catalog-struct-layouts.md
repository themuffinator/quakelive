# UI Catalog Struct Layouts

This note maps the small catalog- and selection-side helper structs that sit
under `uiInfo_t`: `characterInfo`, `aliasInfo`, `teamInfo`, `gameTypeInfo`,
`mapInfo`, and `tierInfo`.

These records are structurally stable across the Team Arena baseline and the
current Quake Live-compatible tree. The strongest retail anchors come from the
already-promoted `uix86.dll` loaders and selection helpers around
`UI_LoadArenasFromFile`, `UI_LoadArenas`, `UI_LoadBotsFromFile`,
`UI_LoadBots`, `Character_Parse`, `UI_ParseTeamInfo`, `GameType_Parse`,
`MapList_Parse`, `UI_ParseGameInfo`, and `UI_DrawSelectedPlayer`. The main
remaining weak band is the older team/alias/tier side; the character, gametype,
and map producers are now directly retail-backed.

## Method

- Layout facts come from local x86 `sizeof` and `offsetof` probes compiled with
  `clang -m32 -target i686-pc-windows-msvc` against
  `src/code/ui/ui_local.h`.
- Legacy comparison comes from the Team Arena-era
  `assets/quake3/src/code/ui/ui_local.h`.
- Current member roles were cross-checked against the catalog and selection
  owners in `src/code/ui/ui_main.c`, `src/code/ui/ui_gameinfo.c`, and
  the preserved Team Arena single-player paths in
  `assets/quake3/src/code/q3_ui/ui_gameinfo.c`.
- Retail parity is strongest for the already-mapped `uix86.dll` helpers
  `UI_LoadArenasFromFile`, `UI_LoadArenas`, `UI_LoadBotsFromFile`,
  `UI_LoadBots`, `Character_Parse`, `UI_ParseTeamInfo`, `GameType_Parse`,
  `MapList_Parse`, `UI_ParseGameInfo`, and `UI_DrawSelectedPlayer`.
- `UI_LoadTeams`, the team/alias loaders outside the character band, and the
  `tierInfo` producer path are currently source-backed rather than directly
  retail-mapped, so those role descriptions are weaker and called out as such
  where needed.

## Hard Layout Facts

- Target layout is 32-bit x86: pointers, `qhandle_t`, `qboolean`, and `int`
  slots are `4` bytes.
- All six requested structs keep the same x86 size and member ordering as the
  Team Arena baseline:
  - `sizeof(characterInfo) = 0x18`
  - `sizeof(aliasInfo) = 0x0C`
  - `sizeof(teamInfo) = 0x2C`
  - `sizeof(gameTypeInfo) = 0x08`
  - `sizeof(mapInfo) = 0x64`
  - `sizeof(tierInfo) = 0x28`
- `mapInfo` is the only aggregate here with a mixed ownership story:
  - arena/browser-facing identity and preview fields are strongly owned by
    `UI_LoadArenas` and the map preview draw path
  - single-player roster and par-time fields are still strongest through the
    legacy `UI_ParseGameInfo` path

## `characterInfo`

Current x86 size: `0x18`

This is a single bot/head catalog row used by the addbot flow, the player model
preview, and the team-filtered head feeder.

| Offset | Member | Type | Role |
| --- | --- | --- | --- |
| `0x00` | `name` | `const char *` | Canonical character/bot display name. Used by the addbot flow, bot feeder text, and player preview selection. |
| `0x04` | `imageName` | `const char *` | Head-icon shader path. `Character_Parse` seeds this as `models/players/heads/<name>/icon_default.tga`. |
| `0x08` | `headImage` | `qhandle_t` | Lazily-registered head icon handle. `-1` means not yet registered. |
| `0x0C` | `base` | `const char *` | Backing model base used for team skin checks and `team_model` / `team_headmodel` setup. `Character_Parse` maps `"female"` to `"Janet"`, `"male"` to `"James"`, or keeps the explicit token. |
| `0x10` | `active` | `qboolean` | Team-filter visibility latch. `UI_HeadCountByTeam` recomputes this when filtering the head list for the selected team. |
| `0x14` | `reference` | `int` | Team-availability bitmask. `UI_HeadCountByTeam` sets one bit per team that has skins for this character base. |

## `aliasInfo`

Current x86 size: `0x0C`

This is the team-roster alias table used to translate a visible member name
into a concrete AI/bot definition.

| Offset | Member | Type | Role |
| --- | --- | --- | --- |
| `0x00` | `name` | `const char *` | Alias token as it appears in `teamMembers[]`. |
| `0x04` | `ai` | `const char *` | Concrete bot/character identifier returned by `UI_AIFromName`. |
| `0x08` | `action` | `const char *` | Parsed preferred-role token (`a`, `d`, `o` in the legacy comments). Structurally present, but no active current consumer was found in the committed tree. |

## `teamInfo`

Current x86 size: `0x2C`

This is a single team-definition row for team selection, opponent selection,
and clan/team preview surfaces.

| Offset | Member | Type | Role |
| --- | --- | --- | --- |
| `0x00` | `teamName` | `const char *` | Canonical team name. Matched by `UI_TeamIndexFromName` and stored in `ui_teamName`, `ui_blueTeam`, `ui_redTeam`, and `ui_opponentName`. |
| `0x04` | `imageName` | `const char *` | Base path for the team icon and cinematic assets. |
| `0x08` | `teamMembers` | `const char *[TEAM_MEMBERS]` | Fixed five-name roster used by skirmish setup, addbot generation, and alias resolution. |
| `0x1C` | `teamIcon` | `qhandle_t` | Cached base team icon shader. |
| `0x20` | `teamIcon_Metal` | `qhandle_t` | Cached metallic icon variant (`<imageName>_metal`). |
| `0x24` | `teamIcon_Name` | `qhandle_t` | Cached text/nameplate icon variant (`<imageName>_name`). |
| `0x28` | `cinematic` | `int` | Team cinematic handle. `-1` means not yet started, `-2` means fallback-to-static-art after failure, and non-negative values are active cinematic handles. |

## `gameTypeInfo`

Current x86 size: `0x08`

This is the compact gametype catalog row shared by the offline/start-server and
join/browser gametype tables.

| Offset | Member | Type | Role |
| --- | --- | --- | --- |
| `0x00` | `gameType` | `const char *` | Human-readable gametype label shown by the gametype ownerdraws. |
| `0x04` | `gtEnum` | `int` | Engine gametype enum used for `g_gametype`, map filtering, and `mapInfo.timeToBeat[]` indexing. |

## `mapInfo`

Current x86 size: `0x64`

This is the main map-catalog row used by map feeders, levelshot/cinematic
preview, skirmish launch setup, and single-player best-score lookups.

| Offset | Member | Type | Role |
| --- | --- | --- | --- |
| `0x00` | `mapName` | `const char *` | Human-readable map title. Used in map ownerdraws and best-score labels. |
| `0x04` | `mapLoadName` | `const char *` | Canonical BSP/map token used for launching, vote commands, levelshot lookup, and demo/best-score keys. |
| `0x08` | `imageName` | `const char *` | Levelshot shader path. `UI_LoadArenas` seeds `levelshots/<mapLoadName>`; the legacy `UI_ParseGameInfo` map path expects the same role even though it registers a small-shot handle directly. |
| `0x0C` | `opponentName` | `const char *` | Default opponent model/name token for single-player or skirmish setup. `UI_StartSkirmish` pushes this into `ui_opponentModel`. |
| `0x10` | `teamMembers` | `int` | Team-size hint for scripted skirmish launch setup. Strongly owned by the legacy `UI_ParseGameInfo` map block; `UI_LoadArenas` does not actively refresh it. |
| `0x14` | `typeBits` | `int` | Bitmask of supported gametypes. Used by `UI_MapCountByGameType` and seeded by both the arena loader and the legacy gameinfo parser. |
| `0x18` | `cinematic` | `int` | Map preview cinematic handle with the usual `-1` not-started / `-2` failed sentinels. |
| `0x1C` | `timeToBeat` | `int[MAX_GAMETYPES]` | Per-gametype par/best-time values indexed by `gtEnum`. Drawn by `UI_DrawMapTimeToBeat`; strongest ownership is the legacy `UI_ParseGameInfo` map block. |
| `0x5C` | `levelShot` | `qhandle_t` | Cached levelshot shader handle. |
| `0x60` | `active` | `qboolean` | Gametype-filter visibility flag. `UI_MapCountByGameType` recomputes this before feeders enumerate maps. |

## `tierInfo`

Current x86 size: `0x28`

This is the preserved single-player tier row used by the old tier ownerdraws
and map-selection launch path.

| Offset | Member | Type | Role |
| --- | --- | --- | --- |
| `0x00` | `tierName` | `const char *` | Human-readable single-player tier title drawn by `UI_DrawTier`. |
| `0x04` | `maps` | `const char *[MAPS_PER_TIER]` | Three backing map tokens for the tier. `UI_DrawTierMap`, `UI_DrawTierMapName`, and the skirmish launch path read these entries. |
| `0x10` | `gameTypes` | `int[MAPS_PER_TIER]` | Per-slot gametype enum used by the tier gametype draw path and by the single-player launch flow. |
| `0x1C` | `mapHandles` | `qhandle_t[MAPS_PER_TIER]` | Lazily-registered levelshot handles for the tier preview surfaces. |

## Open Questions

1. Recover the current retail-compatible producer for `uiInfo.tierList[]` and
   `uiInfo.tierCount`, or confirm that Quake Live left these as dormant
   Team Arena carry-overs with only residual consumers.
2. Revisit `aliasInfo.action` if later retail evidence or menu logic shows it
   still participates in bot-role selection.
3. Tighten the observed precedence between `MapList_Parse` / `UI_ParseGameInfo`
   and `UI_LoadArenas` for `mapInfo.imageName`, `mapInfo.teamMembers`, and
   `mapInfo.timeToBeat` during the various menu reload paths.
