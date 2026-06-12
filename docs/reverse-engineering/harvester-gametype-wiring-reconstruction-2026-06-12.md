# Harvester Gametype Wiring Reconstruction - 2026-06-12

## Scope

This pass rechecked the Harvester (`GT_HARVESTER`) gametype across qagame
objective setup, skull pickup/drop behavior, scoring, scoreboard transports,
bot goal wiring, and cgame HUD/scoreboard consumers. The concrete source
reconstruction is the retail Harvester skull-drop path: Quake Live names the
pickup rows `Red Skull` / `Blue Skull`, clears only the carried-count bits in
`ps.generic1`, drops carried skulls only behind `g_dropSkulls`, and skips the
drop helper for `MOD_SWITCHTEAM` cleanup deaths.

## Evidence

- qagame symbol map:
  - `0x10046970 -> TossClientCubes`
  - `0x10047110 -> CheckAlmostScored`
  - `0x1003E6D0 -> G_BuildCTFStyleScoreboardMessage`
  - `0x1003EC40 -> G_SendCTFStatsMessage`
  - `0x1004FD30 -> G_CheckTeamItems`
  - `0x1006B050 -> CheckObeliskAttack`
  - `SP_team_redobelisk`, `SP_team_blueobelisk`, and
    `SP_team_neutralobelisk`
- qagame Ghidra `decompile_top_functions.c`:
  - `FUN_10046970` reads `ps.generic1 & 0x3f`, clears with `&= 0xc0`,
    launches the generated skull, then loops over carried skulls while the
    `g_dropSkulls` cvar is enabled.
  - `G_ApplyTeamChange` feeds team-change cleanup through
    `player_die(..., 0x1d)`.
  - The death path calls `FUN_10046970` only for
    `GT_HARVESTER && meansOfDeath != 0x1d`; `0x1d` is `MOD_SWITCHTEAM` in the
    committed enum.
  - Harvester objective validation binds `Red Obelisk`, `Blue Obelisk`, and
    `Neutral Obelisk`, with `team_redobelisk`, `team_blueobelisk`, and
    `team_neutralobelisk` classnames.
  - `G_CheckTeamItems` warns independently for missing red, blue, and neutral
    obelisks in Harvester.
- cgame symbol map:
  - `0x10030DF0 -> CG_HarvesterSkulls`
  - CTF-family team-list and stats feeders include `GT_HARVESTER`.
  - `CG_ParseCtfScores` consumes `scores_ctf`; `CG_ParseCTFStats` consumes
    `ctfstats`.
- Existing source targets:
  - `src/code/game/g_combat.c`
  - `src/code/game/g_active.c`
  - `src/code/game/g_items.c`
  - `src/code/game/g_team.c`
  - `src/code/game/g_cmds.c`
  - `src/code/game/g_spawn.c`
  - `src/code/game/ai_dmq3.c`
  - `src/code/cgame/cg_newdraw.c`
  - `src/code/cgame/cg_servercmds.c`
  - `src/code/cgame/cg_main.c`

## Retail Wiring Map

| Surface | Retail evidence | Source state after this pass |
| --- | --- | --- |
| Gametype id | `GT_HARVESTER` is enum slot 8 and is labeled `HAR` by qagame short-name helpers. | Source enum, factory defaults, spawn gametype aliases, and scoreboard dispatch use `GT_HARVESTER`. |
| Objective setup | Retail locates red, blue, and neutral obelisks and binds all three classnames for Harvester. | `SP_team_redobelisk`, `SP_team_blueobelisk`, and `SP_team_neutralobelisk` spawn the matching obelisk entities; `G_CheckTeamItems` validates all three. |
| Spawn filtering | The recovered spawn-filter exemption helper is a narrow retail whitelist for `item_armor_shard` and Overload red/blue obelisks. | Source preserves that narrow helper; Harvester's neutral obelisk is handled by its normal spawn function and objective validation rather than forced into the exemption. |
| Skull pickup rows | Retail item metadata names `item_redcube` / `item_bluecube` as `Red Skull` / `Blue Skull`. | Harvester registration, teleporter drops, and death drops now resolve those pickup names instead of the stale `Red Cube` / `Blue Cube` strings. |
| Generated skull on death | Retail always launches the dead player's team skull at the neutral obelisk when Harvester death cleanup is not `MOD_SWITCHTEAM`. | `G_ApplyTeamChange` now uses `MOD_SWITCHTEAM`; `player_die` gates `TossClientCubes` with `meansOfDeath != MOD_SWITCHTEAM`, and `TossClientCubes` launches the death skull from `neutralObelisk`. |
| Carried skull count | Retail stores carried skulls in the low six bits of `ps.generic1`, then clears only those bits with `&= 0xc0`. | Source now uses `carriedSkulls = ps.generic1 & 0x3f` and preserves upper bits through `ps.generic1 &= 0xc0`. |
| Carried skull drops | Retail loops over the carried count only when `g_dropSkulls` is enabled, uses the enemy skull item, flips the spawnflags to the enemy team, and uses `g_cubeTimeout` for auto-free. | Source now mirrors that loop with `G_LaunchHarvesterSkull`, `g_dropSkulls.integer`, and `g_cubeTimeout.integer * 1000`. |
| Near-score award | `CheckAlmostScored` checks `ps.generic1`, resolves the opposing obelisk, and toggles `PLAYEREVENT_HOLYSHIT` when the carrier dies within 200 units. | Source already matched the helper shape and remains unchanged. |
| Scoring | Harvester obelisk touch uses the carried skull count as the score delta and clears `ps.generic1`. | `g_team.c` keeps the existing carried-token score path and `AddTeamScore` call. |
| Scoreboard transport | Retail reuses the CTF-family `scores_ctf` serializer and intermission `ctfstats` publisher. | `DeathmatchScoreboardMessage` routes Harvester through `G_BuildCTFStyleScoreboardMessage`; intermission sends `G_SendCTFStatsMessage`. |
| cgame HUD | `CG_HarvesterSkulls` formats `ps.generic1 & 0x3f`, right-aligns the number, and draws the team-opposite skull icon/model. | `cg_newdraw.c` already matches the count mask and icon/model selection. |
| cgame scoreboard/feeders | Retail CTF-family team-list and stats feeders include Harvester. | cgame parser and feeder dispatch route Harvester through the CTF-family rows and stats cache. |
| Bot goals | Symbol evidence names `EntityCarriesCubes`, `BotHarvesterCarryingCubes`, `BotHarvesterSeekGoals`, `BotHarvesterRetreatGoals`, and `BotHarvesterOrders`. | `ai_dmq3.c` keeps Harvester in the objective dispatcher and uses `generic1 > 0`/obelisk goals for seek and retreat logic. |

## Source Reconstruction

- Rebuilt `g_combat.c::TossClientCubes` around the retail count contract:
  `ps.generic1 & 0x3f`, `ps.generic1 &= 0xc0`, generated death skull, and
  `g_dropSkulls`-gated carried-skull loop.
- Added the local `G_LaunchHarvesterSkull` helper so generated and carried
  skull launches share the same neutral-obelisk origin, velocity, timeout, and
  spawnflag setup.
- Added `G_OtherHarvesterTeam` for the carried-skull spawnflag flip.
- Changed all Harvester skull item lookups in gameplay code from
  `Red Cube` / `Blue Cube` to the retail item names `Red Skull` / `Blue Skull`:
  - `g_combat.c::TossClientCubes`
  - `g_active.c::ClientEvents`
  - `g_items.c::ClearRegisteredItems`
- Added the retail `MOD_SWITCHTEAM` skip around the `player_die` call to
  `TossClientCubes`.
- Changed `g_cmds.c::G_ApplyTeamChange` to pass `MOD_SWITCHTEAM` into
  `player_die` for team-change cleanup, matching retail `FUN_10040440` and
  making the Harvester skip effective on that path.
- Added a static parity gate in
  `tests/test_game_active_pmove_wiring_parity.py` that pins the item names,
  count mask, upper-bit clear, `g_dropSkulls` loop, `g_cubeTimeout` timeout,
  and `MOD_SWITCHTEAM` death-path condition.

## Confidence

Confidence is high for the source changes. The Ghidra body for
`FUN_10046970` exposes the count mask, clear mask, `g_dropSkulls` branch,
team-flipped carried-skull spawnflags, `g_cubeTimeout` free time, and
`MOD_SWITCHTEAM` death-path exclusion. The item-table evidence independently
confirms the pickup names as `Red Skull` and `Blue Skull`.

Confidence is high for the scoreboard/HUD map: qagame `scores_ctf` /
`ctfstats`, cgame parser symbols, CTF-family feeders, and `CG_HarvesterSkulls`
all agree. Confidence is medium-high for the bot goal map because the symbol
names and source control flow agree, but this pass did not run live bot probes.

## Open Questions

- The committed Binary Ninja HLIL slice for qagame currently does not include a
  full text body for `0x10046970`; the exact loop was cross-checked through the
  committed Ghidra decompile and symbol map. A future HLIL export of this
  function would retire that evidence caveat.
- The Harvester cgame intro/instruction text was observed in cgame string
  tables but not reconstructed in this pass; no source divergence was confirmed
  beyond the skull-drop and item-name wiring.

## Parity Estimate

- Focused Harvester qagame/cgame wiring parity: **before 94% -> after 97%**.
- Broader gameplay/gametype parity: **before 99% -> after 99%**.
