# All Gametype Wiring Reconstruction - 2026-06-12

## Scope

This pass rechecked the complete Quake Live gametype matrix across shared enum
identity, retail factory/default selection, qagame lifecycle hooks, qagame
frame-tail dispatch, exit-rule ownership, scoreboard transports, cgame
scoreboard parsers, HUD feeder leaves, flag/objective configstrings, and the
client gametype info/icon surfaces.

The retail mode set in this repo is:

- `GT_FFA`
- `GT_TOURNAMENT`
- `GT_SINGLE_PLAYER` / `GT_RACE`
- `GT_TEAM`
- `GT_CLAN_ARENA`
- `GT_CTF`
- `GT_1FCTF`
- `GT_OBELISK`
- `GT_HARVESTER`
- `GT_FREEZE`
- `GT_DOMINATION`
- `GT_ATTACK_DEFEND`
- `GT_RED_ROVER`

## Evidence Used

Primary qagame evidence:

- qagame HLIL scoreboard strings and builders around `0x1003D28A` through
  `0x1003F48A`: `scores_ffa`, `scores_duel`, `scores_race`, `scores_tdm`,
  `tdmstats`, `scores_ca`, `castats`, `scores_ctf`, `ctfstats`, `scores_ft`,
  and `scores_rr`.
- qagame HLIL round-controller diagnostics:
  `AD_RoundStateTransition: invalid state`,
  `CA_RoundStateTransition: invalid state`,
  `Freeze_RoundStateTransition: invalid state`, and
  `RR_RoundStateTransition: invalid state`.
- qagame symbol map owners for `DeathmatchScoreboardMessage`,
  `CheckExitRules`, `G_UpdateTeamCountConfigstrings`,
  `G_UpdateDominationPointCountConfigstrings`, `Team_SetFlagStatus`,
  `CA_RoundStateTransition`, `AD_RoundStateTransition`,
  `Freeze_RoundStateTransition`, and `RR_RoundStateTransition`.

Primary cgame evidence:

- cgame HLIL command-token checks around `0x1004B610` through `0x1004B8C9`:
  `scores_ffa`, `scores_duel`, `scores_race`, `scores_tdm`, `scores_ca`,
  `scores_ctf`, `scores_ft`, `scores_ad`, and `scores_rr`.
- cgame symbol map owners for `CG_ParseFFAScores`, `CG_ParseDuelScores`,
  `CG_ParseRaceScores`, `CG_ParseTdmScores`, `CG_ParseClanArenaScores`,
  `CG_ParseCtfScores`, `CG_ParseFreezeScores`, `CG_ParseADScores`,
  `CG_ParseRedRoverScores`, `CG_SetGameInfoCvars`,
  `CG_FeederItemText*`, `CG_ParseMatchState`, and `CG_OwnerDrawVisible`.

Secondary evidence:

- `src/code/game/bg_public.h` enum order and the Quake Live `GT_RACE` alias.
- `src/code/game/g_factory.c` base gametype token map and retail default
  factory ids.
- The already-closed focused gametype reconstruction notes under
  `docs/reverse-engineering/*gametype*wiring-reconstruction-2026-06-12.md`
  plus the 2026-06-05 Race closure notes.

## Retail Wiring Matrix

| Mode | Factory/default | qagame scoreboard | cgame parser/HUD family | Shared runtime owner |
| --- | --- | --- | --- | --- |
| FFA | `ffa` | `scores_ffa` | non-team scoreboard, FFA icon/info | ordinary fraglimit path, Quad Hog frame hook |
| Duel | `duel` | `scores_duel` | duel parser, duel score assets | duel lifecycle warmup/spawn loadout, tournament queue |
| Race | `race` in `GT_SINGLE_PLAYER` slot | `scores_race` | race parser, race feeder, race info/status slots | race lifecycle begin/spawn and race command/event paths |
| TDM | `tdm` | `scores_tdm`, `tdmstats` | TDM/Freeze team-list and stats feeders | team fraglimit, team warmup, team count/status paths |
| Clan Arena | `ca` | `scores_ca`, `castats` | CA parser and CA stats feeders | round controller, compact match-state, team counts |
| CTF | `ctf` | `scores_ctf`, `ctfstats` | CTF-family feeders, red/blue flag HUD | capturelimit, flag-status, missing-flag return |
| One Flag | `oneflag` | `scores_ctf`, `ctfstats` | CTF-family feeders, neutral flag HUD | capturelimit and neutral flag-status wiring |
| Overload | default `ovl`, base token `obelisk` | generic `scores` via Overload builder | generic team scoreboard, Overload media | capturelimit, obelisk entity/objective paths |
| Harvester | `har` | `scores_ctf`, `ctfstats` | CTF-family feeders, skull HUD/media | capturelimit, skull drop/capture, obelisk-style objective |
| Freeze | `ft` | `scores_ft`, `tdmstats` | TDM/Freeze feeders and Freeze parser | Freeze round controller and thaw/freeze state |
| Domination | `dom` | `scores_ctf`, `ctfstats` | CTF-family feeders, point-count HUD | point controller, scorelimit, owned-count configstrings |
| Attack and Defend | `ad` | `scores_ad`, CTF-style stats | A/D parser plus CTF-family feeders | A/D round controller, compact match-state, flag/status paths |
| Red Rover | `rr` | `scores_rr` | RR parser and RR icon/info | RR round controller, infection role, non-team score tie path |

## Shared Buckets

- Factory identity is split between parser tokens and default ids. Most tokens
  are identical, while Overload keeps `obelisk` as a base token and `ovl` as the
  default shipped factory id.
- Qagame scoreboard sending keeps Race as an early special case, then uses a
  command token switch. The shared CTF-style serializer covers CTF, One Flag,
  Harvester, Domination, and Attack and Defend, while Overload deliberately
  stays outside the CTF-style postgame stats bucket.
- Cgame command parsing mirrors the qagame transport names exactly, with
  `adscores` retained as an A/D alias and `smscores` retained as the compact
  fallback.
- HUD feeders use four major leaves: non-team, Race, TDM/Freeze,
  Clan Arena, and CTF-family. Generic team fallback remains available for
  team modes outside the richer families.
- Exit rules keep CA, A/D, and Red Rover delegated to their round controllers,
  gate Freeze on `g_freezeRoundDelay`, keep fraglimit ownership on FFA/Duel/TDM,
  capturelimit ownership on CTF/One Flag/Overload/Harvester, and scorelimit
  ownership on Domination.
- Frame-tail hooks keep mode-specific side effects narrow: FFA Quad Hog,
  CA/Freeze/A-D round controller advancement, Red Rover activity tracking, CTF
  missing-flag recovery, and Domination point-count publication.
- `CS_FLAGSTATUS` remains a compact mode-specific payload: qagame publishes
  CTF/A-D red-blue state or One Flag neutral state, while cgame also accepts
  Overload's red-blue objective-status client branch.

## Source Reconstruction

No gameplay source rewrite was required during this aggregate pass. The
individual 2026-06-12 mode passes had already reconstructed the risky source
differences for Duel, TDM, Clan Arena, CTF/One Flag, Harvester, Freeze,
Domination, Attack and Defend, and Red Rover.

This pass added one broad executable parity gate:

- `tests/test_all_gametype_wiring_parity.py`

That test pins:

- enum order and the `GT_RACE` alias;
- factory base tokens and retail default factory ids;
- cgame `cg_gameInfo*` text and gametype icon coverage;
- qagame scoreboard command selection and cgame command parser coverage;
- retail HLIL scoreboard token evidence on both qagame and cgame sides;
- HUD feeder family dispatch;
- lifecycle, frame-tail, exit-rule, team-count, CTF-style stats, flag-status,
  and shared Race/Domination configstring buckets.

## Open Questions

- Race remains covered by the earlier 2026-06-05 closure rather than a fresh
  per-function source rewrite in this pass.
- Overload retains the older generic scoreboard command token with a dedicated
  qagame builder. That is consistent with the recovered command matrix, but it
  remains visually less freshly exercised than the richer CTF-family modes.
- The remaining uncertainty called out by the focused mode notes still applies:
  mostly visual freshness, exact lower award tails, and a few mode-specific
  presentation details rather than known qagame/cgame routing mismatches.

## Parity Estimate

Focused all-gametype integration wiring moves approximately **98% -> 99%**.
The main change is confidence: the individual mode closures now have a single
cross-mode parity gate proving that the shared dispatch buckets agree across
enum identity, factories, qagame, cgame, and HUD surfaces.

Repo-wide parity remains approximately **99%**. Strict retail Windows
replacement remains at the existing **100%** target posture for the scoped
retail module gates; this pass does not claim new runtime visual validation.
