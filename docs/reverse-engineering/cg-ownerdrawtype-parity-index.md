# CGame Ownerdrawtype Parity Index

Last updated: 2026-05-29

Scope: the cgame ownerdraw block in `src/ui/menudef.h`, from `CG_SERVER_SETTINGS` (`1`) through `CG_MATCH_STATE` (`339`). This index intentionally excludes `CG_SHOW_*` visibility flags, `UI_*` ownerdraws beginning at `UI_OWNERDRAW_BASE` (`512`), and the `src/code/ui/ui_shared.h` source-only legacy aliases after `339`.

State meanings:

- `Checked`: current cgame wiring has a committed retail-evidence parity note and focused structural coverage.
- `Checked no-op`: retail has no draw/helper route for the raw id, or routes it to the common no-op return path; current source preserves that inert behavior.
- `Partial`: source is wired, but one focused behavior detail still needs a retail recheck before this row should be treated as closed.

Summary:

- `Checked`: 327
- `Checked no-op`: 12
- `Partial`: 0
- Total indexed menudef cgame ownerdraws: 339
- Open parity-review rows: none

## Index

| ID | Ownerdraw type | Current implementation | Parity state | Next action |
|---:|---|---|---|---|
| 1 | `CG_SERVER_SETTINGS` | Direct switch: CG_DrawServerSettings custom-settings text plus modified-weapon icon strip. | Checked | No action unless source changes. |
| 2 | `CG_STARTING_WEAPONS` | Direct switch: CG_DrawStartingWeapons CS_LOADOUT_MASK icon strip plus queued-primary preview. | Checked | No action unless source changes. |
| 3 | `CG_GAME_LIMIT` | Direct switch: CG_DrawGameLimit retail Cap/Frag/Round/Score limit label. | Checked | No action unless source changes. |
| 4 | `CG_GAME_TYPE` | Direct switch: CG_DrawGameType; only gametype member of CG_OwnerDrawWidth. | Checked | No action unless source changes. |
| 5 | `CG_GAME_TYPE_ICON` | Direct switch: CG_DrawGameTypeIcon using pre-registered retail HUD `.tga` shaders. | Checked | No action unless source changes. |
| 6 | `CG_GAME_TYPE_MAP` | Direct switch: CG_DrawGameTypeMap using the shared intro-panel detail string and ownerdraw alignment. | Checked | No action unless source changes. |
| 7 | `CG_GAME_STATUS` | Direct switch: CG_DrawGameStatus. | Checked | No action unless source changes. |
| 8 | `CG_MATCH_DETAILS` | Direct switch: CG_DrawMatchDetails. | Checked | No action unless source changes. |
| 9 | `CG_MATCH_END_CONDITION` | Direct switch: CG_DrawMatchEndCondition. | Checked | No action unless source changes. |
| 10 | `CG_MATCH_STATUS` | Direct switch: CG_DrawMatchStatus. | Checked | No action unless source changes. |
| 11 | `CG_CAPFRAGLIMIT` | Direct switch: CG_DrawCapFragLimit. | Checked | No action unless source changes. |
| 12 | `CG_LEVELTIMER` | Direct switch: CG_DrawLevelTimer. | Checked | No action unless source changes. |
| 13 | `CG_ROUND` | Direct switch gated by CG_ShowPlayersRemaining, then CG_DrawRoundLabel. | Checked | No action unless source changes. |
| 14 | `CG_ROUNDTIMER` | Direct switch: CG_DrawRoundTimer. | Checked | No action unless source changes. |
| 15 | `CG_OVERTIME` | Direct switch gated by cg.warmup == 0, then CG_DrawOvertime. | Checked | No action unless source changes. |
| 16 | `CG_LOCALTIME` | Direct switch: CG_DrawLocalTime. | Checked | No action unless source changes. |
| 17 | `CG_PLAYER_COUNTS` | Direct switch: CG_DrawPlayerCounts. | Checked | No action unless source changes. |
| 18 | `CG_MAP_NAME` | Direct switch: CG_DrawMapName. | Checked | No action unless source changes. |
| 19 | `CG_VOTEGAMETYPE1` | Direct switch: CG_DrawVoteGametype slot 1 with retail ownerdraw alignment and `ui_voteGametype1` payload. | Checked | No action unless source changes. |
| 20 | `CG_VOTEGAMETYPE2` | Direct switch: CG_DrawVoteGametype slot 2 with retail ownerdraw alignment and `ui_voteGametype2` payload. | Checked | No action unless source changes. |
| 21 | `CG_VOTEGAMETYPE3` | Direct switch: CG_DrawVoteGametype slot 3 with retail ownerdraw alignment and `ui_voteGametype3` payload. | Checked | No action unless source changes. |
| 22 | `CG_VOTEMAP1` | Direct switch: CG_DrawVoteMapSlot slot 1 with retail ownerdraw alignment and `ui_voteMap1` payload. | Checked | No action unless source changes. |
| 23 | `CG_VOTEMAP2` | Direct switch: CG_DrawVoteMapSlot slot 2 with retail ownerdraw alignment and `ui_voteMap2` payload. | Checked | No action unless source changes. |
| 24 | `CG_VOTEMAP3` | Direct switch: CG_DrawVoteMapSlot slot 3 with retail ownerdraw alignment and `ui_voteMap3` payload. | Checked | No action unless source changes. |
| 25 | `CG_VOTESHOT1` | Direct switch: CG_DrawVoteShot slot 1 with `ui_voteShot1`, default preview fallback, and `levelshots/preview/%s`. | Checked | No action unless source changes. |
| 26 | `CG_VOTESHOT2` | Direct switch: CG_DrawVoteShot slot 2 with `ui_voteShot2`, default preview fallback, and `levelshots/preview/%s`. | Checked | No action unless source changes. |
| 27 | `CG_VOTESHOT3` | Direct switch: CG_DrawVoteShot slot 3 with `ui_voteShot3`, default preview fallback, and `levelshots/preview/%s`. | Checked | No action unless source changes. |
| 28 | `CG_VOTENAME1` | Direct switch: CG_DrawVoteName slot 1 with retail ownerdraw alignment and `ui_voteName1` / map fallback payload. | Checked | No action unless source changes. |
| 29 | `CG_VOTENAME2` | Direct switch: CG_DrawVoteName slot 2 with retail ownerdraw alignment and `ui_voteName2` / map fallback payload. | Checked | No action unless source changes. |
| 30 | `CG_VOTENAME3` | Direct switch: CG_DrawVoteName slot 3 with retail ownerdraw alignment and `ui_voteName3` / map fallback payload. | Checked | No action unless source changes. |
| 31 | `CG_VOTECOUNT1` | Direct switch: CG_DrawVoteCount slot 1 with retail `Votes: %s` text and ownerdraw alignment. | Checked | No action unless source changes. |
| 32 | `CG_VOTECOUNT2` | Direct switch: CG_DrawVoteCount slot 2 with retail `Votes: %s` text and ownerdraw alignment. | Checked | No action unless source changes. |
| 33 | `CG_VOTECOUNT3` | Direct switch: CG_DrawVoteCount slot 3 with retail `Votes: %s` text and ownerdraw alignment. | Checked | No action unless source changes. |
| 34 | `CG_VOTETIMER` | Direct switch: CG_DrawVoteTimer with retail `cgs.voteTime - cg.time + 20000` countdown text and ownerdraw alignment. | Checked | No action unless source changes. |
| 35 | `CG_SPEC_MESSAGES` | Direct switch: CG_DrawSpectatorMessages with the retail Round In Progress/SPECTATOR MODE/join-hint copy family. | Checked | No action unless source changes. |
| 36 | `CG_PLAYER_HEAD` | Direct switch: CG_DrawPlayerHead with the local head damage kick and idle yaw/pitch interpolation. | Checked | No action unless source changes. |
| 37 | `CG_PLAYERMODEL` | Direct switch: CG_DrawPlayerModel tracked/local preview with 5/210/0 preview angles. | Checked | No action unless source changes. |
| 38 | `CG_PLAYER_ARMOR_ICON` | Direct switch: CG_DrawPlayerArmorIcon; CG_SHOW_2DONLY selects flat icon instead of the spinning 3D armor model. | Checked | No action unless source changes. |
| 39 | `CG_PLAYER_ARMOR_ICON2D` | Direct switch: CG_DrawPlayerArmorIcon forced to the flat 2D armor icon path. | Checked | No action unless source changes. |
| 40 | `CG_PLAYER_ARMOR_VALUE` | Direct switch: CG_DrawPlayerArmorValue; value callback returns STAT_ARMOR and draw path matches retail shader-or-aligned-number behavior. | Checked | No action unless source changes. |
| 41 | `CG_PLAYER_ARMOR_BAR_100` | Direct switch: CG_DrawPlayerArmorBar100, clamping armor to the primary 0-100 right-clipped team-color bar. | Checked | No action unless source changes. |
| 42 | `CG_PLAYER_ARMOR_BAR_200` | Direct switch: CG_DrawPlayerArmorBar200, subtracting 100 armor and drawing only the bottom-clipped excess segment. | Checked | No action unless source changes. |
| 43 | `CG_ARMORTIERED_COLORIZED` | Direct switch: CG_DrawArmorTieredColorized using replicated STAT_ARMOR_TIER and half-alpha fill. | Checked | No action unless source changes. |
| 44 | `CG_PLAYER_HEALTH` | Direct switch: CG_DrawPlayerHealth; value callback returns STAT_HEALTH and draw path matches retail shader-or-aligned-number behavior. | Checked | No action unless source changes. |
| 45 | `CG_PLAYER_HEALTH_BAR_100` | Direct switch: CG_DrawPlayerHealthBar100, clamping STAT_HEALTH against STAT_MAX_HEALTH for the primary team-color bar. | Checked | No action unless source changes. |
| 46 | `CG_PLAYER_HEALTH_BAR_200` | Direct switch: CG_DrawPlayerHealthBar200, subtracting STAT_MAX_HEALTH and drawing only the bottom-clipped excess-health segment. | Checked | No action unless source changes. |
| 47 | `CG_PLAYER_AMMO_ICON` | Direct switch: CG_DrawPlayerAmmoIcon; CG_SHOW_2DONLY selects the 2D ammo icon, otherwise retail can draw the current ammo model. | Checked | No action unless source changes. |
| 48 | `CG_PLAYER_AMMO_ICON2D` | Direct switch: CG_DrawPlayerAmmoIcon forced to the 2D ammo icon path. | Checked | No action unless source changes. |
| 49 | `CG_PLAYER_AMMO_VALUE` | Direct switch: CG_DrawPlayerAmmoValue; value callback returns current weapon ammo and draw path preserves finite text, shader, and infinite-ammo icon fallback. | Checked | No action unless source changes. |
| 50 | `CG_PLAYER_ITEM` | Direct switch: CG_DrawPlayerItem; renders the active holdable item and the invulnerability timer percent from the replicated holdable timer stats. | Checked | No action unless source changes. |
| 51 | `CG_PLAYER_SCORE` | Direct switch: CG_DrawScoreValue; value callback returns PERS_SCORE while draw uses the retail Race client score/time formatter when appropriate. | Checked | No action unless source changes. |
| 52 | `CG_RACE_STATUS` | Direct switch: shared CG_DrawRaceStatusAndTimes status branch with the recovered respawn/status text source. | Checked | No action unless source changes. |
| 53 | `CG_RACE_TIMES` | Direct switch: shared CG_DrawRaceStatusAndTimes timing branch with current/last/best/leader Race timing strings. | Checked | No action unless source changes. |
| 54 | `CG_ONEFLAG_STATUS` | Direct switch: CG_OneFlagStatus using the retail flag-status shader bank, white draw color, and stolen-flag score-dependent y offset. | Checked | No action unless source changes. |
| 55 | `CG_PLAYER_HASFLAG` | Direct switch: CG_DrawPlayerHasFlag in model/icon mode. | Checked | No action unless source changes. |
| 56 | `CG_PLAYER_HASFLAG2D` | Direct switch: CG_DrawPlayerHasFlag forced 2D. | Checked | No action unless source changes. |
| 57 | `CG_HARVESTER_SKULLS` | Direct switch: CG_HarvesterSkulls in 3D-capable mode. | Checked | No action unless source changes. |
| 58 | `CG_HARVESTER_SKULLS2D` | Direct switch: CG_HarvesterSkulls forced 2D. | Checked | No action unless source changes. |
| 59 | `CG_PLAYER_HASKEY` | Direct switch: CG_DrawPlayerHasKey using retail IT_KEY tag lookup. | Checked | No action unless source changes. |
| 60 | `CG_CTF_POWERUP` | Direct switch: CG_DrawCTFPowerUp using STAT_PERSISTANT_POWERUP item icon lookup. | Checked | No action unless source changes. |
| 61 | `CG_AREA_POWERUP` | Direct switch: CG_DrawPowerupSpriteStack; retail has no cg_drawSprites or cg_drawSpriteSelf ownerdraw gate. | Checked | No action unless source changes. |
| 62 | `CG_TEAM_COLOR` | Direct switch: CG_DrawTeamColor. | Checked | No action unless source changes. |
| 63 | `CG_KILLER` | Direct switch gated by cg.killerName, then CG_DrawKiller. | Checked | No action unless source changes. |
| 64 | `CG_ACCURACY` | Direct switch: CG_DrawMedal. | Checked | No action unless source changes. |
| 65 | `CG_ASSISTS` | Direct switch: CG_DrawMedal. | Checked | No action unless source changes. |
| 66 | `CG_CAPTURES` | Direct switch: CG_DrawMedal. | Checked | No action unless source changes. |
| 67 | `CG_COMBOKILLS` | Explicit retail no-op case; no medal/helper route. | Checked no-op | Keep inert; no width/value/key route. |
| 68 | `CG_DEFEND` | Direct switch: CG_DrawMedal. | Checked | No action unless source changes. |
| 69 | `CG_EXCELLENT` | Direct switch: CG_DrawMedal. | Checked | No action unless source changes. |
| 70 | `CG_GAUNTLET` | Direct switch: CG_DrawMedal. | Checked | No action unless source changes. |
| 71 | `CG_IMPRESSIVE` | Direct switch: CG_DrawMedal. | Checked | No action unless source changes. |
| 72 | `CG_RAMPAGES` | Explicit retail no-op case; no medal/helper route. | Checked no-op | Keep inert; no width/value/key route. |
| 73 | `CG_MIDAIRS` | Explicit retail no-op case; no medal/helper route. | Checked no-op | Keep inert; no width/value/key route. |
| 74 | `CG_PERFECT` | Direct switch: CG_DrawMedal. | Checked | No action unless source changes. |
| 75 | `CG_MOST_VALUABLE_OFFENSIVE_PLYR` | Pre-switch award player helper: CS_AWARD_MOST_VALUABLE_OFFENSIVE profile image. | Checked | No action unless source changes. |
| 76 | `CG_MOST_VALUABLE_DEFENSIVE_PLYR` | Pre-switch award player helper: CS_AWARD_MOST_VALUABLE_DEFENSIVE profile image. | Checked | No action unless source changes. |
| 77 | `CG_MOST_VALUABLE_PLYR` | Pre-switch award player helper: CS_AWARD_MOST_VALUABLE profile image. | Checked | No action unless source changes. |
| 78 | `CG_BEST_ITEMCONTROL_PLYR` | Pre-switch award player helper: CS_AWARD_BEST_ITEMCONTROL profile image. | Checked | No action unless source changes. |
| 79 | `CG_MOST_ACCURATE_PLYR` | Pre-switch award player helper: CS_AWARD_MOST_ACCURATE profile image. | Checked | No action unless source changes. |
| 80 | `CG_MOST_DAMAGEDEALT_PLYR` | Pre-switch award player helper: CS_AWARD_MOST_DAMAGEDEALT. | Checked | No action unless source changes. |
| 81 | `CG_SPECTATORS` | Direct switch gated by spectatorEntryCount, then CG_DrawTeamSpectators. | Checked | No action unless source changes. |
| 82 | `CG_MATCH_WINNER` | Direct switch: CG_DrawMatchWinner. | Checked | No action unless source changes. |
| 83 | `CG_1STPLACE` | Direct switch: CG_DrawScoreValue compact score helper, including Race `[-]Ns` formatting; touches competitive score cache. | Checked | No action unless source changes. |
| 84 | `CG_1ST_PLACE_SCORE` | Direct switch: CG_Draw1stPlaceScore wide score line. | Checked | No action unless source changes. |
| 85 | `CG_1STPLACE_PLYR_MODEL` | Direct switch: CG_DrawFirstPlaceModel inactive variant. | Checked | No action unless source changes. |
| 86 | `CG_2NDPLACE` | Direct switch: CG_DrawScoreValue compact score helper, including Race `[-]Ns` formatting; touches competitive score cache. | Checked | No action unless source changes. |
| 87 | `CG_2ND_PLACE_SCORE` | Direct switch: CG_Draw2ndPlaceScore wide score line with retail spectator/local-row selection. | Checked | No action unless source changes. |
| 88 | `CG_PLAYER_OBIT` | Direct switch: CG_DrawPlayerObituary. | Checked | No action unless source changes. |
| 89 | `CG_AREA_NEW_CHAT` | Direct switch: CG_DrawNewChatArea. | Checked | No action unless source changes. |
| 90 | `CG_PLYR_END_GAME_SCORE` | Direct switch: CG_DrawEndGameScore. | Checked | No action unless source changes. |
| 91 | `CG_PLYR_BEST_WEAPON_NAME` | Direct switch: CG_DrawSelectedPlayerBestWeapon. | Checked | No action unless source changes. |
| 92 | `CG_SELECTED_PLYR_TEAM_COLOR` | Direct switch: CG_DrawSelectedPlayerTeamColor. | Checked | No action unless source changes. |
| 93 | `CG_SELECTED_PLYR_ACCURACY` | Direct switch: CG_DrawSelectedPlayerAccuracy. | Checked | No action unless source changes. |
| 94 | `CG_FOLLOW_PLAYER_NAME` | Direct switch: CG_DrawFollowPlayerNameEx. | Checked | No action unless source changes. |
| 95 | `CG_FOLLOW_PLAYER_NAME_EX` | Direct switch: CG_DrawFollowPlayerNameEx. | Checked | No action unless source changes. |
| 96 | `CG_SPEEDOMETER` | Direct switch: CG_DrawSpeedometerOwnerDraw. | Checked | No action unless source changes. |
| 97 | `CG_WP_VERTICAL` | Direct switch: CG_DrawWeaponVertical. | Checked | No action unless source changes. |
| 98 | `CG_ACC_VERTICAL` | Direct switch: CG_DrawAccVertical. | Checked | No action unless source changes. |
| 99 | `CG_TEAM_COLORIZED` | Direct switch: CG_DrawTeamColorized with competitive HUD shader fallback. | Checked | No action unless source changes. |
| 100 | `CG_TEAM_PLYR_COUNT` | Direct switch gated by CG_ShowPlayersRemaining, then CG_DrawPlayerCount friendly side at the raw ownerdraw origin. | Checked | No action unless source changes. |
| 101 | `CG_ENEMY_PLYR_COUNT` | Direct switch gated by CG_ShowPlayersRemaining, then CG_DrawPlayerCount enemy side at the raw ownerdraw origin. | Checked | No action unless source changes. |
| 102 | `CG_1STPLACE_PLYR_MODEL_ACTIVE` | Explicit retail no-op case for raw 0x66. | Checked no-op | Keep inert; no width/value/key route. |
| 103 | `CG_1ST_PLYR` | Direct switch: CG_DrawSpectatorPlayerName slot 0. | Checked | No action unless source changes. |
| 104 | `CG_1ST_PLYR_READY` | Pre-switch placement helper: primary ready/status. | Checked | No action unless source changes. |
| 105 | `CG_1ST_PLYR_SCORE` | Direct switch: CG_DrawSpectatorPlayerScore slot 0. | Checked | No action unless source changes. |
| 106 | `CG_1ST_PLYR_FRAGS` | Pre-switch placement helper: frags slot 0. | Checked | No action unless source changes. |
| 107 | `CG_1ST_PLYR_DEATHS` | Pre-switch placement helper: deaths slot 0, `%i` from retail score death offset, baseline paint. | Checked | No action unless source changes. |
| 108 | `CG_1ST_PLYR_DMG` | Pre-switch placement helper: damage slot 0, `%i` from retail score damage offset, baseline paint. | Checked | No action unless source changes. |
| 109 | `CG_1ST_PLYR_TIME` | Explicit retail no-op case for raw 0x6d. | Checked no-op | Keep inert; no width/value/key route. |
| 110 | `CG_1ST_PLYR_PING` | Pre-switch placement helper: ping slot 0, `%i` with retail `>40`/`>80` RGB warning tint and `0.8` alpha. | Checked | No action unless source changes. |
| 111 | `CG_1ST_PLYR_WINS` | Pre-switch placement helper: wins/losses slot 0, matching retail's preformatted `%d/%d` string path and baseline paint. | Checked | No action unless source changes. |
| 112 | `CG_1ST_PLYR_ACC` | Pre-switch placement helper: total accuracy slot 0, retail `%d%%` text and baseline paint. | Checked | No action unless source changes. |
| 113 | `CG_1ST_PLYR_FLAG` | Pre-switch placement helper: flag icon slot 0 from cached country-flag shader / `CG_RegisterCountryFlag` fallback. | Checked | No action unless source changes. |
| 114 | `CG_1ST_PLYR_AVATAR` | Direct switch: CG_DrawPlacementAvatarOwnerDraw slot 0, using the native avatar handle when profile images and identity are available before falling back to the model icon. | Checked | No action unless source changes. |
| 115 | `CG_1ST_PLYR_TIMEOUT_COUNT` | Explicit retail no-op case for raw 0x73. | Checked no-op | Keep inert; no width/value/key route. |
| 116 | `CG_1ST_PLYR_HEALTH_ARMOR` | Direct switch: CG_DrawSpectatorComparison slot family, `cg_specDuelHealthArmor` gated with local playerState stat wiring, tracked-client fallback, retail color constants, damage-loss segment, right-aligned primary health/armor bands, and no synthetic text/marker overlay. | Checked | No action unless source changes. |
| 117 | `CG_1ST_PLYR_FRAGS_G` | Pre-switch placement helper: weapon frags G slot 0, retail `0x100368A0` / `%d` paint path fed by the compact `scorestats` weapon order. | Checked | Guard weapon mapping, server send, cgame parse, and formatter together. |
| 118 | `CG_1ST_PLYR_FRAGS_MG` | Pre-switch placement helper: weapon frags MG slot 0, retail `0x100368A0` / `%d` paint path fed by the compact `scorestats` weapon order. | Checked | Guard weapon mapping, server send, cgame parse, and formatter together. |
| 119 | `CG_1ST_PLYR_FRAGS_SG` | Pre-switch placement helper: weapon frags SG slot 0, retail `0x100368A0` / `%d` paint path fed by the compact `scorestats` weapon order. | Checked | Guard weapon mapping, server send, cgame parse, and formatter together. |
| 120 | `CG_1ST_PLYR_FRAGS_GL` | Pre-switch placement helper: weapon frags GL slot 0, retail `0x100368A0` / `%d` paint path fed by the compact `scorestats` weapon order. | Checked | Guard weapon mapping, server send, cgame parse, and formatter together. |
| 121 | `CG_1ST_PLYR_FRAGS_RL` | Pre-switch placement helper: weapon frags RL slot 0, retail `0x100368A0` / `%d` paint path fed by the compact `scorestats` weapon order. | Checked | Guard weapon mapping, server send, cgame parse, and formatter together. |
| 122 | `CG_1ST_PLYR_FRAGS_LG` | Pre-switch placement helper: weapon frags LG slot 0, retail `0x100368A0` / `%d` paint path with resolver return `6` and compact `scorestats` wiring. | Checked | Guard weapon mapping, server send, cgame parse, and formatter together. |
| 123 | `CG_1ST_PLYR_FRAGS_RG` | Pre-switch placement helper: weapon frags RG slot 0, retail `0x100368A0` / `%d` paint path with resolver return `7` and compact `scorestats` wiring. | Checked | Guard weapon mapping, server send, cgame parse, and formatter together. |
| 124 | `CG_1ST_PLYR_FRAGS_PG` | Pre-switch placement helper: weapon frags PG slot 0, retail `0x100368A0` / `%d` paint path with resolver return `8` and compact `scorestats` wiring. | Checked | Guard weapon mapping, server send, cgame parse, and formatter together. |
| 125 | `CG_1ST_PLYR_FRAGS_BFG` | Pre-switch placement helper: weapon frags BFG slot 0, retail `0x100368A0` / `%d` paint path with resolver return `9` and compact `scorestats` wiring. | Checked | Guard weapon mapping, server send, cgame parse, and formatter together. |
| 126 | `CG_1ST_PLYR_FRAGS_CG` | Pre-switch placement helper: weapon frags CG slot 0, retail `0x100368A0` / `%d` paint path with resolver return `0xd` and compact `scorestats` wiring. | Checked | Guard weapon mapping, server send, cgame parse, and formatter together. |
| 127 | `CG_1ST_PLYR_FRAGS_NG` | Pre-switch placement helper: weapon frags NG slot 0. | Checked | No action unless source changes. |
| 128 | `CG_1ST_PLYR_FRAGS_PL` | Pre-switch placement helper: weapon frags PL slot 0. | Checked | No action unless source changes. |
| 129 | `CG_1ST_PLYR_FRAGS_HMG` | Pre-switch placement helper: weapon frags HMG slot 0. | Checked | No action unless source changes. |
| 130 | `CG_1ST_PLYR_HITS_MG` | Pre-switch placement helper: weapon hits MG slot 0. | Checked | No action unless source changes. |
| 131 | `CG_1ST_PLYR_HITS_SG` | Pre-switch placement helper: weapon hits SG slot 0. | Checked | No action unless source changes. |
| 132 | `CG_1ST_PLYR_HITS_GL` | Pre-switch placement helper: weapon hits GL slot 0. | Checked | No action unless source changes. |
| 133 | `CG_1ST_PLYR_HITS_RL` | Pre-switch placement helper: weapon hits RL slot 0. | Checked | No action unless source changes. |
| 134 | `CG_1ST_PLYR_HITS_LG` | Pre-switch placement helper: weapon hits LG slot 0. | Checked | No action unless source changes. |
| 135 | `CG_1ST_PLYR_HITS_RG` | Pre-switch placement helper: weapon hits RG slot 0. | Checked | No action unless source changes. |
| 136 | `CG_1ST_PLYR_HITS_PG` | Pre-switch placement helper: weapon hits PG slot 0. | Checked | No action unless source changes. |
| 137 | `CG_1ST_PLYR_HITS_BFG` | Pre-switch placement helper: weapon hits BFG slot 0. | Checked | No action unless source changes. |
| 138 | `CG_1ST_PLYR_HITS_CG` | Pre-switch placement helper: weapon hits CG slot 0. | Checked | No action unless source changes. |
| 139 | `CG_1ST_PLYR_HITS_NG` | Pre-switch placement helper: weapon hits NG slot 0. | Checked | No action unless source changes. |
| 140 | `CG_1ST_PLYR_HITS_PL` | Pre-switch placement helper: weapon hits PL slot 0. | Checked | No action unless source changes. |
| 141 | `CG_1ST_PLYR_HITS_HMG` | Pre-switch placement helper: weapon hits HMG slot 0. | Checked | No action unless source changes. |
| 142 | `CG_1ST_PLYR_SHOTS_MG` | Pre-switch placement helper: weapon shots MG slot 0. | Checked | No action unless source changes. |
| 143 | `CG_1ST_PLYR_SHOTS_SG` | Pre-switch placement helper: weapon shots SG slot 0. | Checked | No action unless source changes. |
| 144 | `CG_1ST_PLYR_SHOTS_GL` | Pre-switch placement helper: weapon shots GL slot 0. | Checked | No action unless source changes. |
| 145 | `CG_1ST_PLYR_SHOTS_RL` | Pre-switch placement helper: weapon shots RL slot 0. | Checked | No action unless source changes. |
| 146 | `CG_1ST_PLYR_SHOTS_LG` | Pre-switch placement helper: weapon shots LG slot 0. | Checked | No action unless source changes. |
| 147 | `CG_1ST_PLYR_SHOTS_RG` | Pre-switch placement helper: weapon shots RG slot 0. | Checked | No action unless source changes. |
| 148 | `CG_1ST_PLYR_SHOTS_PG` | Pre-switch placement helper: weapon shots PG slot 0. | Checked | No action unless source changes. |
| 149 | `CG_1ST_PLYR_SHOTS_BFG` | Pre-switch placement helper: weapon shots BFG slot 0. | Checked | No action unless source changes. |
| 150 | `CG_1ST_PLYR_SHOTS_CG` | Pre-switch placement helper: weapon shots CG slot 0. | Checked | No action unless source changes. |
| 151 | `CG_1ST_PLYR_SHOTS_NG` | Pre-switch placement helper: weapon shots NG slot 0. | Checked | No action unless source changes. |
| 152 | `CG_1ST_PLYR_SHOTS_PL` | Pre-switch placement helper: weapon shots PL slot 0. | Checked | No action unless source changes. |
| 153 | `CG_1ST_PLYR_SHOTS_HMG` | Pre-switch placement helper: weapon shots HMG slot 0. | Checked | No action unless source changes. |
| 154 | `CG_1ST_PLYR_DMG_G` | Pre-switch placement helper: weapon damage G slot 0. | Checked | No action unless source changes. |
| 155 | `CG_1ST_PLYR_DMG_MG` | Pre-switch placement helper: weapon damage MG slot 0. | Checked | No action unless source changes. |
| 156 | `CG_1ST_PLYR_DMG_SG` | Pre-switch placement helper: weapon damage SG slot 0. | Checked | No action unless source changes. |
| 157 | `CG_1ST_PLYR_DMG_GL` | Pre-switch placement helper: weapon damage GL slot 0. | Checked | No action unless source changes. |
| 158 | `CG_1ST_PLYR_DMG_RL` | Pre-switch placement helper: weapon damage RL slot 0. | Checked | No action unless source changes. |
| 159 | `CG_1ST_PLYR_DMG_LG` | Pre-switch placement helper: weapon damage LG slot 0. | Checked | No action unless source changes. |
| 160 | `CG_1ST_PLYR_DMG_RG` | Pre-switch placement helper: weapon damage RG slot 0. | Checked | No action unless source changes. |
| 161 | `CG_1ST_PLYR_DMG_PG` | Pre-switch placement helper: weapon damage PG slot 0. | Checked | No action unless source changes. |
| 162 | `CG_1ST_PLYR_DMG_BFG` | Pre-switch placement helper: weapon damage BFG slot 0. | Checked | No action unless source changes. |
| 163 | `CG_1ST_PLYR_DMG_CG` | Pre-switch placement helper: weapon damage CG slot 0. | Checked | No action unless source changes. |
| 164 | `CG_1ST_PLYR_DMG_NG` | Pre-switch placement helper: weapon damage NG slot 0. | Checked | No action unless source changes. |
| 165 | `CG_1ST_PLYR_DMG_PL` | Pre-switch placement helper: weapon damage PL slot 0. | Checked | No action unless source changes. |
| 166 | `CG_1ST_PLYR_DMG_HMG` | Pre-switch placement helper: weapon damage HMG slot 0. | Checked | No action unless source changes. |
| 167 | `CG_1ST_PLYR_ACC_MG` | Pre-switch placement helper: weapon accuracy MG slot 0. | Checked | No action unless source changes. |
| 168 | `CG_1ST_PLYR_ACC_SG` | Pre-switch placement helper: weapon accuracy SG slot 0. | Checked | No action unless source changes. |
| 169 | `CG_1ST_PLYR_ACC_GL` | Pre-switch placement helper: weapon accuracy GL slot 0. | Checked | No action unless source changes. |
| 170 | `CG_1ST_PLYR_ACC_RL` | Pre-switch placement helper: weapon accuracy RL slot 0. | Checked | No action unless source changes. |
| 171 | `CG_1ST_PLYR_ACC_LG` | Pre-switch placement helper: weapon accuracy LG slot 0. | Checked | No action unless source changes. |
| 172 | `CG_1ST_PLYR_ACC_RG` | Pre-switch placement helper: weapon accuracy RG slot 0. | Checked | No action unless source changes. |
| 173 | `CG_1ST_PLYR_ACC_PG` | Pre-switch placement helper: weapon accuracy PG slot 0. | Checked | No action unless source changes. |
| 174 | `CG_1ST_PLYR_ACC_BFG` | Pre-switch placement helper: weapon accuracy BFG slot 0. | Checked | No action unless source changes. |
| 175 | `CG_1ST_PLYR_ACC_CG` | Pre-switch placement helper: weapon accuracy CG slot 0. | Checked | No action unless source changes. |
| 176 | `CG_1ST_PLYR_ACC_NG` | Pre-switch placement helper: weapon accuracy NG slot 0. | Checked | No action unless source changes. |
| 177 | `CG_1ST_PLYR_ACC_PL` | Pre-switch placement helper: weapon accuracy PL slot 0. | Checked | No action unless source changes. |
| 178 | `CG_1ST_PLYR_ACC_HMG` | Pre-switch placement helper: weapon accuracy HMG slot 0. | Checked | No action unless source changes. |
| 179 | `CG_1ST_PLYR_PICKUPS` | Pre-switch placement helper: pickup summary slot 0. | Checked | No action unless source changes. |
| 180 | `CG_1ST_PLYR_PICKUPS_RA` | Pre-switch placement helper: RA pickup count slot 0. | Checked | No action unless source changes. |
| 181 | `CG_1ST_PLYR_PICKUPS_YA` | Pre-switch placement helper: YA pickup count slot 0. | Checked | No action unless source changes. |
| 182 | `CG_1ST_PLYR_PICKUPS_GA` | Pre-switch placement helper: GA pickup count slot 0. | Checked | No action unless source changes. |
| 183 | `CG_1ST_PLYR_PICKUPS_MH` | Pre-switch placement helper: MH pickup count slot 0. | Checked | No action unless source changes. |
| 184 | `CG_1ST_PLYR_AVG_PICKUP_TIME_RA` | Pre-switch placement helper: RA average pickup time slot 0. | Checked | No action unless source changes. |
| 185 | `CG_1ST_PLYR_AVG_PICKUP_TIME_YA` | Pre-switch placement helper: YA average pickup time slot 0. | Checked | No action unless source changes. |
| 186 | `CG_1ST_PLYR_AVG_PICKUP_TIME_GA` | Pre-switch placement helper: GA average pickup time slot 0. | Checked | No action unless source changes. |
| 187 | `CG_1ST_PLYR_AVG_PICKUP_TIME_MH` | Pre-switch placement helper: MH average pickup time slot 0. | Checked | No action unless source changes. |
| 188 | `CG_1ST_PLYR_EXCELLENT` | Pre-switch placement helper: excellent count slot 0. | Checked | No action unless source changes. |
| 189 | `CG_1ST_PLYR_IMPRESSIVE` | Pre-switch placement helper: impressive count slot 0. | Checked | No action unless source changes. |
| 190 | `CG_1ST_PLYR_HUMILIATION` | Pre-switch placement helper: humiliation count slot 0. | Checked | No action unless source changes. |
| 191 | `CG_1ST_PLYR_PR` | Implicit default no-op; absent from retail placement helper and switch route. | Checked no-op | Keep inert; no width/value/key route. |
| 192 | `CG_1ST_PLYR_TIER` | Implicit default no-op; absent from retail placement helper and switch route. | Checked no-op | Keep inert; no width/value/key route. |
| 193 | `CG_2ND_PLYR` | Direct switch: CG_DrawSpectatorPlayerName slot 1. | Checked | No action unless source changes. |
| 194 | `CG_2ND_PLYR_READY` | Pre-switch placement helper: secondary ready/status. | Checked | No action unless source changes. |
| 195 | `CG_2ND_PLYR_SCORE` | Direct switch: CG_DrawSpectatorPlayerScore slot 1. | Checked | No action unless source changes. |
| 196 | `CG_2ND_PLYR_FRAGS` | Pre-switch placement helper: frags slot 1. | Checked | No action unless source changes. |
| 197 | `CG_2ND_PLYR_DEATHS` | Pre-switch placement helper: deaths slot 1. | Checked | No action unless source changes. |
| 198 | `CG_2ND_PLYR_DMG` | Pre-switch placement helper: damage slot 1. | Checked | No action unless source changes. |
| 199 | `CG_2ND_PLYR_TIME` | Implicit default no-op; absent from retail placement helper and switch route. | Checked no-op | Keep inert; no width/value/key route. |
| 200 | `CG_2ND_PLYR_PING` | Pre-switch placement helper: ping slot 1, sharing the retail `>40`/`>80` RGB warning tint and `0.8` alpha. | Checked | No action unless source changes. |
| 201 | `CG_2ND_PLYR_WINS` | Pre-switch placement helper: wins/losses slot 1, sharing the retail `%d/%d` string path. | Checked | No action unless source changes. |
| 202 | `CG_2ND_PLYR_ACC` | Pre-switch placement helper: total accuracy slot 1, sharing the retail `%d%%` text path. | Checked | No action unless source changes. |
| 203 | `CG_2ND_PLYR_FLAG` | Pre-switch placement helper: flag icon slot 1 from cached country-flag shader / `CG_RegisterCountryFlag` fallback. | Checked | No action unless source changes. |
| 204 | `CG_2ND_PLYR_AVATAR` | Direct switch: CG_DrawPlacementAvatarOwnerDraw slot 1, sharing the avatar-handle then model-icon fallback path. | Checked | No action unless source changes. |
| 205 | `CG_2ND_PLYR_TIMEOUT_COUNT` | Explicit retail no-op case for raw 0xcd. | Checked no-op | Keep inert; no width/value/key route. |
| 206 | `CG_2ND_PLYR_HEALTH_ARMOR` | Direct switch: CG_DrawSpectatorComparison slot family, sharing the cvar/stat/fallback band drawing, damage-loss segment, and left-aligned secondary bars. | Checked | No action unless source changes. |
| 207 | `CG_2ND_PLYR_FRAGS_G` | Pre-switch placement helper: weapon frags G slot 1. | Checked | No action unless source changes. |
| 208 | `CG_2ND_PLYR_FRAGS_MG` | Pre-switch placement helper: weapon frags MG slot 1. | Checked | No action unless source changes. |
| 209 | `CG_2ND_PLYR_FRAGS_SG` | Pre-switch placement helper: weapon frags SG slot 1. | Checked | No action unless source changes. |
| 210 | `CG_2ND_PLYR_FRAGS_GL` | Pre-switch placement helper: weapon frags GL slot 1. | Checked | No action unless source changes. |
| 211 | `CG_2ND_PLYR_FRAGS_RL` | Pre-switch placement helper: weapon frags RL slot 1. | Checked | No action unless source changes. |
| 212 | `CG_2ND_PLYR_FRAGS_LG` | Pre-switch placement helper: weapon frags LG slot 1. | Checked | No action unless source changes. |
| 213 | `CG_2ND_PLYR_FRAGS_RG` | Pre-switch placement helper: weapon frags RG slot 1. | Checked | No action unless source changes. |
| 214 | `CG_2ND_PLYR_FRAGS_PG` | Pre-switch placement helper: weapon frags PG slot 1. | Checked | No action unless source changes. |
| 215 | `CG_2ND_PLYR_FRAGS_BFG` | Pre-switch placement helper: weapon frags BFG slot 1. | Checked | No action unless source changes. |
| 216 | `CG_2ND_PLYR_FRAGS_CG` | Pre-switch placement helper: weapon frags CG slot 1. | Checked | No action unless source changes. |
| 217 | `CG_2ND_PLYR_FRAGS_NG` | Pre-switch placement helper: weapon frags NG slot 1. | Checked | No action unless source changes. |
| 218 | `CG_2ND_PLYR_FRAGS_PL` | Pre-switch placement helper: weapon frags PL slot 1. | Checked | No action unless source changes. |
| 219 | `CG_2ND_PLYR_FRAGS_HMG` | Pre-switch placement helper: weapon frags HMG slot 1. | Checked | No action unless source changes. |
| 220 | `CG_2ND_PLYR_HITS_MG` | Pre-switch placement helper: weapon hits MG slot 1. | Checked | No action unless source changes. |
| 221 | `CG_2ND_PLYR_HITS_SG` | Pre-switch placement helper: weapon hits SG slot 1. | Checked | No action unless source changes. |
| 222 | `CG_2ND_PLYR_HITS_GL` | Pre-switch placement helper: weapon hits GL slot 1. | Checked | No action unless source changes. |
| 223 | `CG_2ND_PLYR_HITS_RL` | Pre-switch placement helper: weapon hits RL slot 1. | Checked | No action unless source changes. |
| 224 | `CG_2ND_PLYR_HITS_LG` | Pre-switch placement helper: weapon hits LG slot 1. | Checked | No action unless source changes. |
| 225 | `CG_2ND_PLYR_HITS_RG` | Pre-switch placement helper: weapon hits RG slot 1. | Checked | No action unless source changes. |
| 226 | `CG_2ND_PLYR_HITS_PG` | Pre-switch placement helper: weapon hits PG slot 1. | Checked | No action unless source changes. |
| 227 | `CG_2ND_PLYR_HITS_BFG` | Pre-switch placement helper: weapon hits BFG slot 1. | Checked | No action unless source changes. |
| 228 | `CG_2ND_PLYR_HITS_CG` | Pre-switch placement helper: weapon hits CG slot 1. | Checked | No action unless source changes. |
| 229 | `CG_2ND_PLYR_HITS_NG` | Pre-switch placement helper: weapon hits NG slot 1. | Checked | No action unless source changes. |
| 230 | `CG_2ND_PLYR_HITS_PL` | Pre-switch placement helper: weapon hits PL slot 1. | Checked | No action unless source changes. |
| 231 | `CG_2ND_PLYR_HITS_HMG` | Pre-switch placement helper: weapon hits HMG slot 1. | Checked | No action unless source changes. |
| 232 | `CG_2ND_PLYR_SHOTS_MG` | Pre-switch placement helper: weapon shots MG slot 1. | Checked | No action unless source changes. |
| 233 | `CG_2ND_PLYR_SHOTS_SG` | Pre-switch placement helper: weapon shots SG slot 1. | Checked | No action unless source changes. |
| 234 | `CG_2ND_PLYR_SHOTS_GL` | Pre-switch placement helper: weapon shots GL slot 1. | Checked | No action unless source changes. |
| 235 | `CG_2ND_PLYR_SHOTS_RL` | Pre-switch placement helper: weapon shots RL slot 1. | Checked | No action unless source changes. |
| 236 | `CG_2ND_PLYR_SHOTS_LG` | Pre-switch placement helper: weapon shots LG slot 1. | Checked | No action unless source changes. |
| 237 | `CG_2ND_PLYR_SHOTS_RG` | Pre-switch placement helper: weapon shots RG slot 1. | Checked | No action unless source changes. |
| 238 | `CG_2ND_PLYR_SHOTS_PG` | Pre-switch placement helper: weapon shots PG slot 1. | Checked | No action unless source changes. |
| 239 | `CG_2ND_PLYR_SHOTS_BFG` | Pre-switch placement helper: weapon shots BFG slot 1. | Checked | No action unless source changes. |
| 240 | `CG_2ND_PLYR_SHOTS_CG` | Pre-switch placement helper: weapon shots CG slot 1. | Checked | No action unless source changes. |
| 241 | `CG_2ND_PLYR_SHOTS_NG` | Pre-switch placement helper: weapon shots NG slot 1. | Checked | No action unless source changes. |
| 242 | `CG_2ND_PLYR_SHOTS_PL` | Pre-switch placement helper: weapon shots PL slot 1. | Checked | No action unless source changes. |
| 243 | `CG_2ND_PLYR_SHOTS_HMG` | Pre-switch placement helper: weapon shots HMG slot 1. | Checked | No action unless source changes. |
| 244 | `CG_2ND_PLYR_DMG_G` | Pre-switch placement helper: weapon damage G slot 1. | Checked | No action unless source changes. |
| 245 | `CG_2ND_PLYR_DMG_MG` | Pre-switch placement helper: weapon damage MG slot 1. | Checked | No action unless source changes. |
| 246 | `CG_2ND_PLYR_DMG_SG` | Pre-switch placement helper: weapon damage SG slot 1. | Checked | No action unless source changes. |
| 247 | `CG_2ND_PLYR_DMG_GL` | Pre-switch placement helper: weapon damage GL slot 1. | Checked | No action unless source changes. |
| 248 | `CG_2ND_PLYR_DMG_RL` | Pre-switch placement helper: weapon damage RL slot 1. | Checked | No action unless source changes. |
| 249 | `CG_2ND_PLYR_DMG_LG` | Pre-switch placement helper: weapon damage LG slot 1. | Checked | No action unless source changes. |
| 250 | `CG_2ND_PLYR_DMG_RG` | Pre-switch placement helper: weapon damage RG slot 1. | Checked | No action unless source changes. |
| 251 | `CG_2ND_PLYR_DMG_PG` | Pre-switch placement helper: weapon damage PG slot 1. | Checked | No action unless source changes. |
| 252 | `CG_2ND_PLYR_DMG_BFG` | Pre-switch placement helper: weapon damage BFG slot 1. | Checked | No action unless source changes. |
| 253 | `CG_2ND_PLYR_DMG_CG` | Pre-switch placement helper: weapon damage CG slot 1. | Checked | No action unless source changes. |
| 254 | `CG_2ND_PLYR_DMG_NG` | Pre-switch placement helper: weapon damage NG slot 1. | Checked | No action unless source changes. |
| 255 | `CG_2ND_PLYR_DMG_PL` | Pre-switch placement helper: weapon damage PL slot 1. | Checked | No action unless source changes. |
| 256 | `CG_2ND_PLYR_DMG_HMG` | Pre-switch placement helper: weapon damage HMG slot 1. | Checked | No action unless source changes. |
| 257 | `CG_2ND_PLYR_ACC_MG` | Pre-switch placement helper: weapon accuracy MG slot 1. | Checked | No action unless source changes. |
| 258 | `CG_2ND_PLYR_ACC_SG` | Pre-switch placement helper: weapon accuracy SG slot 1. | Checked | No action unless source changes. |
| 259 | `CG_2ND_PLYR_ACC_GL` | Pre-switch placement helper: weapon accuracy GL slot 1. | Checked | No action unless source changes. |
| 260 | `CG_2ND_PLYR_ACC_RL` | Pre-switch placement helper: weapon accuracy RL slot 1. | Checked | No action unless source changes. |
| 261 | `CG_2ND_PLYR_ACC_LG` | Pre-switch placement helper: weapon accuracy LG slot 1. | Checked | No action unless source changes. |
| 262 | `CG_2ND_PLYR_ACC_RG` | Pre-switch placement helper: weapon accuracy RG slot 1. | Checked | No action unless source changes. |
| 263 | `CG_2ND_PLYR_ACC_PG` | Pre-switch placement helper: weapon accuracy PG slot 1. | Checked | No action unless source changes. |
| 264 | `CG_2ND_PLYR_ACC_BFG` | Pre-switch placement helper: weapon accuracy BFG slot 1. | Checked | No action unless source changes. |
| 265 | `CG_2ND_PLYR_ACC_CG` | Pre-switch placement helper: weapon accuracy CG slot 1. | Checked | No action unless source changes. |
| 266 | `CG_2ND_PLYR_ACC_NG` | Pre-switch placement helper: weapon accuracy NG slot 1. | Checked | No action unless source changes. |
| 267 | `CG_2ND_PLYR_ACC_PL` | Pre-switch placement helper: weapon accuracy PL slot 1. | Checked | No action unless source changes. |
| 268 | `CG_2ND_PLYR_ACC_HMG` | Pre-switch placement helper: weapon accuracy HMG slot 1. | Checked | No action unless source changes. |
| 269 | `CG_2ND_PLYR_PICKUPS` | Pre-switch placement helper: pickup summary slot 1. | Checked | No action unless source changes. |
| 270 | `CG_2ND_PLYR_PICKUPS_RA` | Pre-switch placement helper: RA pickup count slot 1. | Checked | No action unless source changes. |
| 271 | `CG_2ND_PLYR_PICKUPS_YA` | Pre-switch placement helper: YA pickup count slot 1. | Checked | No action unless source changes. |
| 272 | `CG_2ND_PLYR_PICKUPS_GA` | Pre-switch placement helper: GA pickup count slot 1. | Checked | No action unless source changes. |
| 273 | `CG_2ND_PLYR_PICKUPS_MH` | Pre-switch placement helper: MH pickup count slot 1. | Checked | No action unless source changes. |
| 274 | `CG_2ND_PLYR_AVG_PICKUP_TIME_RA` | Pre-switch placement helper: RA average pickup time slot 1. | Checked | No action unless source changes. |
| 275 | `CG_2ND_PLYR_AVG_PICKUP_TIME_YA` | Pre-switch placement helper: YA average pickup time slot 1. | Checked | No action unless source changes. |
| 276 | `CG_2ND_PLYR_AVG_PICKUP_TIME_GA` | Pre-switch placement helper: GA average pickup time slot 1. | Checked | No action unless source changes. |
| 277 | `CG_2ND_PLYR_AVG_PICKUP_TIME_MH` | Pre-switch placement helper: MH average pickup time slot 1. | Checked | No action unless source changes. |
| 278 | `CG_2ND_PLYR_EXCELLENT` | Pre-switch placement helper: excellent count slot 1. | Checked | No action unless source changes. |
| 279 | `CG_2ND_PLYR_IMPRESSIVE` | Pre-switch placement helper: impressive count slot 1. | Checked | No action unless source changes. |
| 280 | `CG_2ND_PLYR_HUMILIATION` | Pre-switch placement helper: humiliation count slot 1. | Checked | No action unless source changes. |
| 281 | `CG_2ND_PLYR_PR` | Explicit retail no-op case; no raw 0x119 helper route. | Checked no-op | Keep inert; no width/value/key route. |
| 282 | `CG_2ND_PLYR_TIER` | Explicit retail no-op case; no raw 0x11a helper route. | Checked no-op | Keep inert; no width/value/key route. |
| 283 | `CG_RED_FLAGSTATUS` | Direct switch: CG_DrawTeamFlagOrBaseStatus red flag status. | Checked | No action unless source changes. |
| 284 | `CG_RED_SCORE` | Direct switch: CG_DrawTeamScore red. | Checked | No action unless source changes. |
| 285 | `CG_RED_NAME` | Direct switch: CG_DrawTeamName red. | Checked | No action unless source changes. |
| 286 | `CG_RED_OWNED_FLAGS` | Direct switch gated to Domination and Attack/Defend, then CG_DrawDominationOwnedFlags red. | Checked | No action unless source changes. |
| 287 | `CG_RED_AVG_PING` | Direct switch: CG_DrawTeamAveragePing red. | Checked | No action unless source changes. |
| 288 | `CG_RED_BASESTATUS` | Direct switch: CG_DrawTeamFlagOrBaseStatus red base status. | Checked | No action unless source changes. |
| 289 | `CG_RED_PLAYER_COUNT` | Direct switch: CG_DrawTeamPlayerCount red. | Checked | No action unless source changes. |
| 290 | `CG_RED_CLAN_PLYRS` | Direct switch gated by CG_ShowPlayersRemaining, then CG_DrawClanArenaPlayers red. | Checked | No action unless source changes. |
| 291 | `CG_RED_TIMEOUT_COUNT` | Direct switch gated by cgs.playerCountTeamSize, then CG_DrawTeamTimeoutCount red. | Checked | No action unless source changes. |
| 292 | `CG_RED_TEAM_MAP_PICKUPS` | Direct switch: CG_DrawTeamPickupOwnerDraw red map pickup summary. | Checked | No action unless source changes. |
| 293 | `CG_RED_TEAM_PICKUPS_RA` | Direct switch: CG_DrawTeamPickupOwnerDraw red RA pickup count. | Checked | No action unless source changes. |
| 294 | `CG_RED_TEAM_PICKUPS_YA` | Direct switch: CG_DrawTeamPickupOwnerDraw red YA pickup count. | Checked | No action unless source changes. |
| 295 | `CG_RED_TEAM_PICKUPS_GA` | Direct switch: CG_DrawTeamPickupOwnerDraw red GA pickup count. | Checked | No action unless source changes. |
| 296 | `CG_RED_TEAM_PICKUPS_MH` | Direct switch: CG_DrawTeamPickupOwnerDraw red MH pickup count. | Checked | No action unless source changes. |
| 297 | `CG_RED_TEAM_PICKUPS_QUAD` | Direct switch: CG_DrawTeamPickupOwnerDraw red Quad pickup count. | Checked | No action unless source changes. |
| 298 | `CG_RED_TEAM_PICKUPS_BS` | Direct switch: CG_DrawTeamPickupOwnerDraw red Battle Suit pickup count. | Checked | No action unless source changes. |
| 299 | `CG_RED_TEAM_TIMEHELD_QUAD` | Direct switch: CG_DrawTeamTimeHeldOwnerDraw red Quad time held. | Checked | No action unless source changes. |
| 300 | `CG_RED_TEAM_TIMEHELD_BS` | Direct switch: CG_DrawTeamTimeHeldOwnerDraw red Battle Suit time held. | Checked | No action unless source changes. |
| 301 | `CG_RED_TEAM_PICKUPS_FLAG` | Direct switch: CG_DrawTeamPickupOwnerDraw red flag pickup count. | Checked | No action unless source changes. |
| 302 | `CG_RED_TEAM_PICKUPS_MEDKIT` | Direct switch: CG_DrawTeamPickupOwnerDraw red Medkit pickup count. | Checked | No action unless source changes. |
| 303 | `CG_RED_TEAM_PICKUPS_REGEN` | Direct switch: CG_DrawTeamPickupOwnerDraw red Regeneration pickup count. | Checked | No action unless source changes. |
| 304 | `CG_RED_TEAM_PICKUPS_HASTE` | Direct switch: CG_DrawTeamPickupOwnerDraw red Haste pickup count. | Checked | No action unless source changes. |
| 305 | `CG_RED_TEAM_PICKUPS_INVIS` | Direct switch: CG_DrawTeamPickupOwnerDraw red Invisibility pickup count. | Checked | No action unless source changes. |
| 306 | `CG_RED_TEAM_TIMEHELD_FLAG` | Direct switch: CG_DrawTeamTimeHeldOwnerDraw red flag time held. | Checked | No action unless source changes. |
| 307 | `CG_RED_TEAM_TIMEHELD_REGEN` | Direct switch: CG_DrawTeamTimeHeldOwnerDraw red Regeneration time held. | Checked | No action unless source changes. |
| 308 | `CG_RED_TEAM_TIMEHELD_HASTE` | Direct switch: CG_DrawTeamTimeHeldOwnerDraw red Haste time held. | Checked | No action unless source changes. |
| 309 | `CG_RED_TEAM_TIMEHELD_INVIS` | Direct switch: CG_DrawTeamTimeHeldOwnerDraw red Invisibility time held. | Checked | No action unless source changes. |
| 310 | `CG_BLUE_FLAGSTATUS` | Direct switch: CG_DrawTeamFlagOrBaseStatus blue flag status. | Checked | No action unless source changes. |
| 311 | `CG_BLUE_NAME` | Direct switch: CG_DrawTeamName blue. | Checked | No action unless source changes. |
| 312 | `CG_BLUE_SCORE` | Direct switch: CG_DrawTeamScore blue. | Checked | No action unless source changes. |
| 313 | `CG_BLUE_OWNED_FLAGS` | Direct switch gated to Domination and Attack/Defend, then CG_DrawDominationOwnedFlags blue. | Checked | No action unless source changes. |
| 314 | `CG_BLUE_AVG_PING` | Direct switch: CG_DrawTeamAveragePing blue. | Checked | No action unless source changes. |
| 315 | `CG_BLUE_BASESTATUS` | Direct switch: CG_DrawTeamFlagOrBaseStatus blue base status. | Checked | No action unless source changes. |
| 316 | `CG_BLUE_PLAYER_COUNT` | Direct switch: CG_DrawTeamPlayerCount blue. | Checked | No action unless source changes. |
| 317 | `CG_BLUE_CLAN_PLYRS` | Direct switch gated by CG_ShowPlayersRemaining, then CG_DrawClanArenaPlayers blue. | Checked | No action unless source changes. |
| 318 | `CG_BLUE_TIMEOUT_COUNT` | Direct switch gated by cgs.playerCountTeamSize, then CG_DrawTeamTimeoutCount blue. | Checked | No action unless source changes. |
| 319 | `CG_BLUE_TEAM_MAP_PICKUPS` | Direct switch: CG_DrawTeamPickupOwnerDraw blue map pickup summary. | Checked | No action unless source changes. |
| 320 | `CG_BLUE_TEAM_PICKUPS_RA` | Direct switch: CG_DrawTeamPickupOwnerDraw blue RA pickup count. | Checked | No action unless source changes. |
| 321 | `CG_BLUE_TEAM_PICKUPS_YA` | Direct switch: CG_DrawTeamPickupOwnerDraw blue YA pickup count. | Checked | No action unless source changes. |
| 322 | `CG_BLUE_TEAM_PICKUPS_GA` | Direct switch: CG_DrawTeamPickupOwnerDraw blue GA pickup count. | Checked | No action unless source changes. |
| 323 | `CG_BLUE_TEAM_PICKUPS_MH` | Direct switch: CG_DrawTeamPickupOwnerDraw blue MH pickup count. | Checked | No action unless source changes. |
| 324 | `CG_BLUE_TEAM_PICKUPS_QUAD` | Direct switch: CG_DrawTeamPickupOwnerDraw blue Quad pickup count. | Checked | No action unless source changes. |
| 325 | `CG_BLUE_TEAM_PICKUPS_BS` | Direct switch: CG_DrawTeamPickupOwnerDraw blue Battle Suit pickup count. | Checked | No action unless source changes. |
| 326 | `CG_BLUE_TEAM_TIMEHELD_QUAD` | Direct switch: CG_DrawTeamTimeHeldOwnerDraw blue Quad time held. | Checked | No action unless source changes. |
| 327 | `CG_BLUE_TEAM_TIMEHELD_BS` | Direct switch: CG_DrawTeamTimeHeldOwnerDraw blue Battle Suit time held. | Checked | No action unless source changes. |
| 328 | `CG_BLUE_TEAM_PICKUPS_FLAG` | Direct switch: CG_DrawTeamPickupOwnerDraw blue flag pickup count. | Checked | No action unless source changes. |
| 329 | `CG_BLUE_TEAM_PICKUPS_MEDKIT` | Direct switch: CG_DrawTeamPickupOwnerDraw blue Medkit pickup count. | Checked | No action unless source changes. |
| 330 | `CG_BLUE_TEAM_PICKUPS_REGEN` | Direct switch: CG_DrawTeamPickupOwnerDraw blue Regeneration pickup count. | Checked | No action unless source changes. |
| 331 | `CG_BLUE_TEAM_PICKUPS_HASTE` | Direct switch: CG_DrawTeamPickupOwnerDraw blue Haste pickup count. | Checked | No action unless source changes. |
| 332 | `CG_BLUE_TEAM_PICKUPS_INVIS` | Direct switch: CG_DrawTeamPickupOwnerDraw blue Invisibility pickup count. | Checked | No action unless source changes. |
| 333 | `CG_BLUE_TEAM_TIMEHELD_FLAG` | Direct switch: CG_DrawTeamTimeHeldOwnerDraw blue flag time held. | Checked | No action unless source changes. |
| 334 | `CG_BLUE_TEAM_TIMEHELD_REGEN` | Direct switch: CG_DrawTeamTimeHeldOwnerDraw blue Regeneration time held. | Checked | No action unless source changes. |
| 335 | `CG_BLUE_TEAM_TIMEHELD_HASTE` | Direct switch: CG_DrawTeamTimeHeldOwnerDraw blue Haste time held. | Checked | No action unless source changes. |
| 336 | `CG_BLUE_TEAM_TIMEHELD_INVIS` | Direct switch: CG_DrawTeamTimeHeldOwnerDraw blue Invisibility time held. | Checked | No action unless source changes. |
| 337 | `CG_FLAG_STATUS` | Direct switch: CG_DrawObjectiveStatus. | Checked | No action unless source changes. |
| 338 | `CG_HEALTH_COLORIZED` | Direct switch: CG_DrawHealthColorized with competitive HUD shader fallback. | Checked | No action unless source changes. |
| 339 | `CG_MATCH_STATE` | Direct switch: CG_DrawMatchState. | Checked | No action unless source changes. |

## Out-of-Scope Adjacent Constants

`src/code/ui/ui_shared.h` still carries source-only legacy cgame ownerdraw aliases after the menudef cgame range, including `CG_SPEC_FOLLOW_PRIMARY` through `CG_AREA_CHAT` (`340..367`). Those aliases are not part of this menudef index. Current cgame parity notes treat that legacy corridor as retail no-op coverage, but new parity-picking from this document should use only rows `1..339` above.
