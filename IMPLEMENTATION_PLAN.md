# Implementation Plan

Last updated: 2026-06-06

This file now tracks only active repo-level work. Detailed closure narratives
live in the dedicated subsystem audits under `docs/reverse-engineering/`.
Historical task headings that existing parity gates still check are preserved in
the appendix as compact archival anchors instead of repeated full narratives.

## Strategic goal

The long-term parity target remains the same: the reconstructed engine should,
in theory, be able to replace the retail Quake Live engine, load retail
`cgamex86.dll`, `qagamex86.dll`, and `uix86.dll`, present the retail main menu,
and interoperate with the retail Windows host/runtime contracts. Quake
Live-only online services remain behind `QL_BUILD_ONLINE_SERVICES`, default
disabled, until a documented open replacement path exists.

## Current planning baseline

- Treat `AUDIT.md` and
  `docs/reverse-engineering/repo-wide-parity-audit-2026-04-21.md` as the
  current cross-subsystem truth.
- Treat the 2026-04-10 engine-wide **100%** report as the strict-retail
  Windows closure milestone, not as a whole-repo all-green claim.
- The strict-retail Windows replacement target remains **100%** on the current
  worktree, and the current repo-wide parity estimate is **99%** after the
  non-Windows portability lanes were closed as explicit compatibility-only
  containment. Remaining repo-wide uncertainty is validation freshness rather
  than active non-Windows source parity debt.
- The new file-by-file audit campaign now lives in
  `docs/reverse-engineering/source-file-parity-ledger-2026-04-22.md` and
  `docs/reverse-engineering/source-file-parity-audit-plan-2026-04-22.md`.
  It tracks `567` source entries, seeds concrete per-file notes for the
  documented `RW-G01` divergence owners plus the active `RW-G02` gap owners,
  and keeps the older
  subsystem ledgers as inherited baselines until each file is walked again.
- Top-level planning is reopened in this file because the 2026-04-21 repo-wide
  audit identified active gaps outside the strict-retail score.
- The older broad planning notes under `docs/parity-plan.md`,
  `docs/ui_deltas.md`, and `docs/ui_followup_issues.md` are historical
  snapshots, not current gap ledgers.
- The ownerdraw index checklists live in
  `docs/reverse-engineering/ui-ownerdrawtype-parity-index.md` and
  `docs/reverse-engineering/cg-ownerdrawtype-parity-index.md`; use them to
  pick and close remaining `src/ui/menudef.h` ownerdraw IDs.

## Active work

### Task A334: Pin qagame ai_team modal order and leader dispatcher wiring [COMPLETED]
Priority: High
Primary areas: `references/analysis/quakelive_symbol_aliases.json`,
`tests/test_botlib_qagame_ai_team_modal_order_parity.py`,
`docs/reverse-engineering/botlib-qagame-ai-team-modal-order-mapping-2026-06-06.md`
Parity estimate: **before 0% -> after 100%** for focused qagame
`ai_team.c` Obelisk/Harvester/leader/BotTeamAI alias coverage, **before 88%
-> after 98%** for focused source-owned modal team-order reconstruction
confidence, **before 94% -> after 98%** for focused
leader/chat/EA/import-wiring confidence, and overall botlib plus qagame AI
wiring confidence **98.3% -> 98.6%**.

Completed work:

1. Promoted both `FUN_...` and `sub_...` aliases for `BotObeliskOrders`,
   `BotHarvesterOrders`, `FindHumanTeamLeader`, and `BotTeamAI` at
   `0x10029df0..0x1002aef0`.
2. Cross-checked the checked-in source against HLIL evidence for
   defend/attack/harvest order splits, passive/aggressive caps, human leader
   discovery, `whoisteamleader` / `iamteamleader` chat, `startleader` voice
   emission, and the gametype-specific order dispatcher cadence.
3. Added a parity regression covering aliases, Ghidra function inventory,
   symbol-map signatures/comments, source anchors, Binary Ninja HLIL
   entry/flow anchors, Ghidra top-function anchors, and the
   configstring/AAS/chat/EA import bridge used by this band.
4. Documented that the source reconstruction already matches this retail slice,
   so no C source edits were required in this round.

### Task A333: Pin ZMQ idZMQ host lifecycle and source wiring [COMPLETED]
Priority: High
Primary areas: `docs/reverse-engineering/quakelive_steam_mapping_round_420.md`,
`tests/test_platform_services.py`,
`src/code/server/sv_zmq.c`
Parity estimate: **before 76% -> after 95%** for focused `idZMQ` host
lifecycle/publication/RCON wiring confidence, **before 94.1% -> after 94.2%**
for ZMQ-related source reconstruction confidence, and overall Quake Live
source parity **55.83% -> 55.84%**.

Completed work:

1. Rechecked the older retail `idZMQ` host aliases from Rounds 94 through 97
   against current HLIL, function inventory, and the source reconstruction.
2. Re-pinned the server-facing match-report/player-event wrappers, retained
   object methods, thin global wrappers, RCON broadcast/pump helpers, shutdown
   split, and peer-table ownership helpers.
3. Tied the retail wrapper and string evidence back to the current
   `sv_zmq.c`, `sv_init.c`, `sv_main.c`, `sv_game.c`, and `common.c` call
   sites without changing C source behavior.
4. Documented the CZMQ/libzmq inference boundary: retail uses embedded helper
   bands, while this repository keeps Quake Live's server integration source
   and dynamically resolves public `zmq_*` symbols for opted-in live transport.

### Task A332: Pin qagame ai_team one-flag order and team dispatcher wiring [COMPLETED]
Priority: High
Primary areas: `references/analysis/quakelive_symbol_aliases.json`,
`tests/test_botlib_qagame_ai_team_oneflag_order_parity.py`,
`docs/reverse-engineering/botlib-qagame-ai-team-oneflag-order-mapping-2026-06-06.md`
Parity estimate: **before 0% -> after 100%** for focused qagame
`ai_team.c` dispatcher/group/1FCTF alias coverage, **before 87% -> after
97%** for focused source-owned one-flag and team-order reconstruction
confidence, **before 94% -> after 98%** for focused
Cvar/configstring/chat/EA import-wiring confidence, and overall botlib plus
qagame AI wiring confidence **98.0% -> 98.3%**.

Completed work:

1. Promoted both `FUN_...` and `sub_...` aliases for `BotCTFOrders`,
   `BotCreateGroup`, `BotTeamOrders`, the four `Bot1FCTFOrders_*` helpers, and
   `Bot1FCTFOrders` at `0x10027750..0x10029d90`.
2. Cross-checked the checked-in source against HLIL evidence for the CTF
   flag-status dispatcher, group leader follow commands, cached
   `sv_maxclients` team enumeration, 1FCTF percentage splits, return/getflag
   voice order quirks, and `neutralflagstatus` dispatch.
3. Added a parity regression covering aliases, Ghidra function inventory,
   symbol-map signatures/comments, source anchors, Binary Ninja HLIL
   entry/flow anchors, Ghidra top-function anchors, `BotTeamAI` gametype
   dispatch, and the Cvar/configstring/chat/EA import bridge used by the band.
4. Documented that the source reconstruction already matches this retail slice,
   so no C source edits were required in this round.

### Task A331: Pin ZMQ option switch source-constant wiring [COMPLETED]
Priority: High
Primary areas: `docs/reverse-engineering/quakelive_steam_mapping_round_419.md`,
`tests/test_platform_services.py`,
`src/code/server/sv_zmq.c`
Parity estimate: **before 68% -> after 93%** for focused ZMQ
option-switch/source-constant linkage confidence, **before 94.0% -> after
94.1%** for ZMQ-related source reconstruction confidence, and overall Quake
Live source parity **55.82% -> 55.83%**.

Completed work:

1. Rechecked the retail `options_t::setsockopt` / `options_t::getsockopt`
   switch tables at `0x40E0E0` and `0x40E690` against the committed HLIL.
2. Pinned the option range, jump/lookup-table shapes, `EINVAL` rejection path,
   and the entries for ROUTER mandatory delivery (`0x21`), PLAIN server mode
   (`0x2c`), and ZAP domain strings (`0x37`).
3. Tied those retail option ids to the reconstructed `QL_ZMQ_*` constants used
   by the server-owned RCON and stats socket setup in `src/code/server/sv_zmq.c`.
4. Added a focused regression so future ZMQ edits cannot drift the source
   constants away from the retail option switch evidence.

### Task A330: Classify ZMQ dependency ownership boundary [COMPLETED]
Priority: High
Primary areas: `docs/reverse-engineering/zmq-dependency-ownership-2026-06-06.md`,
`tests/test_platform_services.py`,
`README.md`
Parity estimate: **before 61% -> after 92%** for focused ZMQ dependency
ownership confidence, **before 94.0% -> after 94.0%** for ZMQ-related source
reconstruction confidence, and overall Quake Live source parity **55.82% ->
55.82%**.

Completed work:

1. Investigated whether writable source contains actual libzmq implementation
   code or only the Quake Live server-owned `idZMQ` integration.
2. Confirmed the only ZMQ-named source file under `src/code/` is
   `src/code/server/sv_zmq.c`, and that it dynamically resolves external
   libzmq symbols for opted-in online-service builds.
3. Documented the conclusion that no dependency should be installed under
   `src/libs/` in this pass and no `sv_zmq.c` code should be cut from
   `src/code/`.
4. Added a regression guard against accidentally treating `src/code` as a
   vendored libzmq implementation space.

### Task A329: Pin qagame ai_team CTF order and botlib wiring [COMPLETED]
Priority: High
Primary areas: `references/analysis/quakelive_symbol_aliases.json`,
`tests/test_botlib_qagame_ai_team_ctf_order_parity.py`,
`docs/reverse-engineering/botlib-qagame-ai-team-ctf-order-mapping-2026-06-06.md`
Parity estimate: **before 0% -> after 100%** for focused qagame
`ai_team.c` CTF order-band alias coverage, **before 88% -> after 97%** for
focused source-owned team-order reconstruction confidence, **before 94% ->
after 98%** for focused AAS/chat/EA import-wiring confidence, and overall
botlib plus qagame AI wiring confidence **97.6% -> 98.0%**.

Completed work:

1. Promoted both `FUN_...` and `sub_...` aliases for the retail teammate
   counting, base travel-time sorting, CTF task-preference, team-order chat,
   voice-chat, and first four CTF order helpers at `0x10025390..0x10026f20`.
2. Cross-checked the source reconstruction against HLIL evidence for
   `sv_maxclients` caching, player configstring walks, AAS travel-time calls,
   task-preference name validation, defender/roamer/attacker partitioning,
   `vsay`/`vtell` and `vosay`/`votell` EA formatting, and the `BotCTFOrders`
   dispatcher edges.
3. Added a parity regression covering aliases, Ghidra function sizes,
   symbol-map signatures/comments, source anchors, Binary Ninja HLIL
   entry/flow anchors, Ghidra decompiler anchors, and the game/server import
   bridge for the AAS, chat, and EA calls used by the slice.
4. Documented `FUN_100269d0` as a medium-high confidence mapping because HLIL
   reports unresolved stack usage, while the surrounding dispatcher,
   command-string, sort/preference, and symbol-map evidence still strongly
   support `BotCTFOrders_EnemyFlagNotAtBase`.

### Task A328: Pin ZMQ clock and thread runtime wiring [COMPLETED]
Priority: High
Primary areas: `references/analysis/quakelive_symbol_aliases.json`,
`tests/test_platform_services.py`,
`docs/reverse-engineering/quakelive_steam_mapping_round_418.md`
Parity estimate: **before 48% -> after 93%** for focused ZMQ clock/thread
runtime wiring confidence, **before 93.8% -> after 94.0%** for ZMQ-related
source reconstruction confidence, and overall Quake Live source parity
**55.81% -> 55.82%**.

Completed work:

1. Rechecked the cached millisecond clock helper, Windows tick-count fallback,
   thread trampoline, start wrapper, stop wrapper, and fallback lock atexit
   cleanup against HLIL around `0x40B950..0x40BB30` and `0x52A9E0..0x52B070`.
2. Added aliases for the address-backed clock/thread helpers that connect
   `socket_base_t` timeout loops, `select_t`, `io_thread_t`, and `reaper_t` to
   the retail runtime scaffolding.
3. Documented the `GetTickCount64` resolver/fallback path while leaving
   `sub_40B950` as supporting evidence because it is not exposed as a normal
   Ghidra inventory row.
4. Added a parity regression covering alias rows, clock cache anchors, thread
   assertion anchors, select/io-thread/reaper callsites, and static initializer
   evidence for the fallback tick-count lock.

### Task A327: Pin qagame ai_main lifecycle and training helper wiring [COMPLETED]
Priority: High
Primary areas: `references/analysis/quakelive_symbol_aliases.json`,
`tests/test_botlib_qagame_ai_main_lifecycle_training_parity.py`,
`docs/reverse-engineering/botlib-qagame-ai-main-lifecycle-training-mapping-2026-06-06.md`
Parity estimate: **before 8% -> after 100%** for focused qagame
`ai_main.c` lifecycle and training-helper alias coverage, **before 92% ->
after 98%** for focused source-owned lifecycle reconstruction confidence,
**before 58% -> after 87%** for focused retail-only training/dynamic-skill
helper mapping confidence, and overall botlib plus qagame AI execution wiring
confidence **97.1% -> 97.6%**.

Completed work:

1. Promoted both `FUN_...` and `sub_...` aliases for the source-owned
   `BotTestAAS`, interbreed, team-leader, view-angle, input translation,
   per-bot think, scheduling, session, setup, shutdown, reset, map-load,
   botlib setup, and botlib shutdown rows.
2. Promoted mapped training and tutorial helper aliases for
   `BotEntityBoundsGap`, `BotSetIdealViewAnglesToPoint`,
   `BotSetTrainingBotState`, `BotAppendDynamicSkillSample`,
   `BotUpdateDynamicSkill`, `BotApplyBeyondRealityTravelFlags`, local/bot
   client selectors, training cvar helpers, and the training-state tail.
3. Added a parity regression covering aliases, Ghidra row sizes, symbol-map
   signatures/comments, reconstructed source anchors, Binary Ninja HLIL
   entry/flow anchors, Ghidra decompiler anchors for the larger retail-only
   helpers, and the botlib lifecycle, EA, chat, move, goal, weapon, entity,
   and user-command import wiring used by the slice.
4. Documented the source-reconstruction boundary for the retail-only
   dynamic-skill island, where names and call sites are now pinned but exact
   C reconstruction remains open.

### Task A326: Pin ZMQ own_t owned pointer-set lifecycle wiring [COMPLETED]
Priority: High
Primary areas: `references/analysis/quakelive_symbol_aliases.json`,
`tests/test_platform_services.py`,
`docs/reverse-engineering/quakelive_steam_mapping_round_417.md`
Parity estimate: **before 42% -> after 94%** for focused ZMQ `own_t`
owned pointer-set lifecycle confidence, **before 93.6% -> after 93.8%** for
ZMQ-related source reconstruction confidence, and overall Quake Live source
parity **55.80% -> 55.81%**.

Completed work:

1. Rechecked `own_t` construction, destruction, `process_own`,
   `process_term_req`, and `process_term` against HLIL around
   `0x40F050..0x40FAE0`.
2. Added aliases for the pointer-node create/find/predecessor/rightmost,
   subtree free, right-rotation, range-erase, and full-tree clear helpers that
   back the `owned` child set.
3. Preserved the Round 148 shared pointer-set insert/erase/rebalance aliases
   while tying the remaining helper surface to the observed `own.cpp`
   lifecycle flow.
4. Documented the reconstructed container-level source shape and the inference
   boundary for the inline command opcode `0xB` termination send sequence.

### Task A325: Pin ZMQ object default command and poll-event assertion wiring [COMPLETED]
Priority: High
Primary areas: `references/analysis/quakelive_symbol_aliases.json`,
`tests/test_platform_services.py`,
`docs/reverse-engineering/quakelive_steam_mapping_round_416.md`
Parity estimate: **before 35% -> after 96%** for focused ZMQ object-command
default callback surface confidence, **before 93.4% -> after 93.6%** for
ZMQ-related source reconstruction confidence, and overall Quake Live source
parity **55.79% -> 55.80%**.

Completed work:

1. Rechecked `object_t`, `io_thread_t`, and `reaper_t` default callback slots
   against HLIL around `0x40CF60..0x40DF00`.
2. Added aliases for io-thread/reaper `out_event` and `timer_event` assertion
   callbacks with their source-file-specific assertion anchors.
3. Added aliases for all 16 base `object_t::process_*` fail-fast command
   handlers, matching the `zmq_command_t_process` opcode dispatch table and
   existing command send helpers.
4. Documented the reconstructed command vtable surface and the inference
   boundary for the `process_attach` slot.

### Task A324: Pin qagame DMQ3 deathmatch setup and ai_main wrapper wiring [COMPLETED]
Priority: High
Primary areas: `references/analysis/quakelive_symbol_aliases.json`,
`references/symbol-maps/qagame.json`,
`tests/test_botlib_qagame_ai_dmq3_deathmatch_setup_parity.py`,
`docs/reverse-engineering/botlib-qagame-ai-dmq3-deathmatch-setup-mapping-2026-06-06.md`
Parity estimate: **before 0% -> after 100%** for focused qagame
deathmatch/setup and adjacent ai_main alias coverage, **before 91% -> after
98%** for focused source-owned deathmatch/setup/wrapper parity confidence,
**before 45% -> after 82%** for focused retail-only tutorial helper mapping
confidence, and overall botlib plus qagame AI execution wiring confidence
**96.7% -> 97.1%**.

Completed work:

1. Promoted both `FUN_...` and `sub_...` aliases for the source-owned
   `BotDeathmatchAI`, `BotSetEntityNumForGoal`, `BotSetupDeathmatchAI`,
   `BotAI_Print`, `BotAI_Trace`, `BotAI_GetClientState`,
   `BotClientHasNoTargetFlag`, `BotAI_GetEntityState`, and
   `BotAI_BotInitialChat` rows.
2. Promoted mapped-only retail helper aliases for `BotSelectTormentTarget`,
   `BotResolveTourPoint`, `BotAcceptOffscreenEnemyCandidate`, and
   `BotCanSpawnTourPoint`, without claiming source reconstruction for those
   retail-only bodies.
3. Corrected the `BotSetEntityNumForGoal` symbol-map comment to document the
   retail-preserved classname guard that skips exact classname matches and
   falls through for absent or non-matching classnames.
4. Added a parity regression covering aliases, Ghidra row sizes, symbol-map
   signatures/comments, source-body anchors, Binary Ninja HLIL entry/flow
   anchors, and the cvar, userinfo, trace, AAS/BSP, EA command, chat, stack
   dump, and level-item botlib wiring used by the slice.

### Task A323: Pin ZMQ socket-base endpoint and pending compact-map wiring [COMPLETED]
Priority: High
Primary areas: `references/analysis/quakelive_symbol_aliases.json`,
`tests/test_platform_services.py`,
`docs/reverse-engineering/quakelive_steam_mapping_round_415.md`
Parity estimate: **before 44% -> after 90%** for focused ZMQ socket-base
endpoint and pending compact-map helper wiring, **before 93.2% -> after
93.4%** for ZMQ-related source reconstruction confidence, and overall Quake
Live source parity **55.78% -> 55.79%**.

Completed work:

1. Rechecked `socket_base_t::bind`, `socket_base_t::connect`, and
   `socket_base_t::term_endpoint` against HLIL around `0x408D90..0x40B360`.
2. Added aliases for the shared `socket_base_t::add_endpoint` helper and the
   compact endpoint/pending node creation, subtree cleanup, iterator, range
   erase, and rotation helpers.
3. Preserved the older ctx and socket-base map aliases while distinguishing the
   socket-base compact layouts by their `0x30/0x31` endpoint and `0x2C/0x2D`
   pending node sentinel offsets.
4. Documented the inferred source reconstruction shape for endpoint registration
   and unresolved inproc pending-connection storage.

### Task A322: Pin qagame DMQ3 activate-goal, obstacle, snapshot, and alternate-route wiring [COMPLETED]
Priority: High
Primary areas: `references/analysis/quakelive_symbol_aliases.json`,
`tests/test_botlib_qagame_ai_dmq3_activate_obstacle_parity.py`,
`docs/reverse-engineering/botlib-qagame-ai-dmq3-activate-obstacle-mapping-2026-06-06.md`
Parity estimate: **before 80% -> after 100%** for focused qagame
`ai_dmq3.c` activate/obstacle/alternate-route alias coverage, **before 92% ->
after 98%** for focused source-owned activate/obstacle/event parity confidence,
**before 91% -> after 98%** for focused botlib activation, route, movement,
avoid, and chat import wiring confidence, and overall botlib plus qagame AI
execution wiring confidence **96.0% -> 96.7%**.

Completed work:

1. Promoted the remaining retail qagame `FUN_...` and `sub_...` names for
   `BotCheckConsoleMessages`, `BotAlternateRoute`,
   `BotGetAlternateRouteGoal`, and `BotSetupAlternativeRouteGoals`.
2. Added a parity regression covering the contiguous
   `0x1001BCD0..0x1001EE30` qagame band from activate-goal builders through
   alternate-route setup.
3. Pinned the source bodies against Binary Ninja HLIL entries and flow anchors,
   Ghidra function sizes, symbol-map signatures, and representative botlib AAS,
   chat, movement, avoid, and alternate-route import wiring.
4. Documented the observed facts, inferred subsystem role, import wiring, and
   remaining confidence limits in the reverse-engineering notes.

### Task A321: Pin ZMQ ctx endpoint and pending tree helper wiring [COMPLETED]
Priority: High
Primary areas: `references/analysis/quakelive_symbol_aliases.json`,
`tests/test_platform_services.py`,
`docs/reverse-engineering/quakelive_steam_mapping_round_414.md`
Parity estimate: **before 46% -> after 91%** for focused ZMQ ctx endpoint and
pending tree helper wiring, **before 93.0% -> after 93.2%** for ZMQ-related
source reconstruction confidence, and overall Quake Live source parity
**55.77% -> 55.78%**.

Completed work:

1. Rechecked the ctx endpoint and pending inproc connection map helper band
   against HLIL around `0x404380..0x406820`.
2. Added aliases for endpoint-tree find, get-or-insert, lower-bound,
   insertion, subtree cleanup, iterator, and rotation helpers.
3. Added aliases for pending-connection tree copy, creation, insertion,
   iterator, subtree cleanup, and rotation helpers, preserving the retail
   `0x280/0x281` pending-node layout distinction from endpoint nodes.
4. Re-pinned the `options_t` address-mask vector copy/destruction helpers
   reached by the ctx endpoint payload copy path.

### Task A320: Pin ZMQ ctx runtime and inproc handoff wiring [COMPLETED]
Priority: High
Primary areas: `references/analysis/quakelive_symbol_aliases.json`,
`tests/test_platform_services.py`,
`docs/reverse-engineering/quakelive_steam_mapping_round_413.md`
Parity estimate: **before 36% -> after 93%** for focused ZMQ ctx runtime and
inproc-pending wiring, **before 92.8% -> after 93.0%** for ZMQ-related source
reconstruction confidence, and overall Quake Live source parity
**55.76% -> 55.77%**.

Completed work:

1. Rechecked the ctx runtime helper band around `0x403120..0x404010`
   against socket destruction, I/O-thread selection, endpoint map cleanup, and
   inproc pending-connection call sites.
2. Added aliases for socket destruction, I/O-thread selection, endpoint-record
   destruction, options destruction, endpoint bulk-unregistration, and
   pending-connection delivery.
3. Corrected two stale compiler-noise aliases: `sub_4038B0` is the
   `options_t` copy constructor, and `sub_403BB0` is the ctx pending inproc
   connection helper rather than an STL locale helper.

### Task A319: Pin qagame DMQ3 aim, attack, and map-script bridge [COMPLETED]
Priority: High
Primary areas: `src/code/game/ai_dmq3.c`,
`references/analysis/quakelive_symbol_aliases.json`,
`tests/test_botlib_qagame_ai_dmq3_aim_attack_parity.py`,
`docs/reverse-engineering/botlib-qagame-ai-dmq3-aim-attack-mapping-2026-06-06.md`
Parity estimate: **before 0% -> after 96%** for focused qagame
`ai_dmq3.c` aim/attack alias coverage, **before 88% -> after 97%** for
focused source-owned aim/attack/map-script parity confidence, **before 92% ->
after 97%** for fire-control and prediction import wiring confidence, and
overall botlib plus adjacent qagame AI execution wiring **95% -> 96%**.

Completed work:

1. Mapped the retail `qagamex86.dll` `0x10019E00..0x1001BBE0`
   `ai_dmq3.c` bridge from `BotAimAtEnemy` through `BotModelMinsMaxs`.
2. Promoted both `FUN_...` and `sub_...` aliases for the aim controller,
   attack gate, map-script helper, movedir helper, and model-bounds helper.
3. Reconstructed the retail `BotMapScripts` fallback branch from
   `mpq3tourney6` to `beyondreality`, matching HLIL and symbol-map evidence.
4. Added a parity gate covering aliases, Ghidra row sizes, symbol-map
   signatures, source-body anchors, Binary Ninja HLIL entry/flow anchors, and
   the predictive movement, weapon-info, visible-position, characteristic, EA
   attack, and EA view botlib wiring used by the slice.

### Task A318: Pin ZMQ ctx constructor and endpoint-map wiring [COMPLETED]
Priority: High
Primary areas: `references/analysis/quakelive_symbol_aliases.json`,
`tests/test_platform_services.py`,
`docs/reverse-engineering/quakelive_steam_mapping_round_412.md`
Parity estimate: **before 41% -> after 94%** for focused ZMQ ctx constructor,
endpoint-map, and map-cleanup wiring, **before 92.5% -> after 92.8%** for ZMQ-related
source reconstruction confidence, and overall Quake Live source parity
**55.75% -> 55.76%**.

Completed work:

1. Rechecked the `ctx_t` constructor body against the public `zmq_ctx_new`
   wrapper, ctx magic constants, mailbox setup, map sentinels, mutex
   initialization, and default option writes.
2. Added aliases for the ctx constructor, endpoint registration/removal/lookup,
   endpoint/pending-connection map constructor-unwind destructors, and the
   endpoint/pending range-erase helpers.
3. Added a static parity guard tying the constructor and cleanup aliases to
   `ctx.cpp` strings, the existing ctx destructor, Ghidra rows, endpoint map
   errno behavior, map sentinel sizes, and command-mailbox teardown evidence.

### Task A317: Pin qagame DMQ3 roaming, visibility, and carrier helpers [COMPLETED]
Priority: High
Primary areas: `references/analysis/quakelive_symbol_aliases.json`,
`tests/test_botlib_qagame_ai_dmq3_visibility_parity.py`,
`docs/reverse-engineering/botlib-qagame-ai-dmq3-visibility-mapping-2026-06-06.md`
Parity estimate: **before 0% -> after 95%** for focused qagame
`ai_dmq3.c` visibility-band alias coverage, **before 90% -> after 97%**
for focused source-owned visibility-band parity confidence, **before 91% ->
after 96%** for movement/visibility import wiring confidence, and overall
botlib plus adjacent qagame AI execution wiring **94% -> 95%**.

Completed work:

1. Mapped the retail `qagamex86.dll` `0x10017D20..0x10019D30`
   `ai_dmq3.c` slice from `BotRoamGoal` through
   `BotEnemyCubeCarrierVisible`.
2. Promoted both `FUN_...` and `sub_...` aliases for the roam,
   attack-movement, same-team, field-of-view, entity-visibility,
   enemy-acquisition, flag-carrier, and cube-carrier helper rows.
3. Added a parity gate covering aliases, Ghidra row sizes, symbol-map
   signatures, source-body anchors, Binary Ninja HLIL entry/flow anchors, and
   the AAS contents, characteristic, move-to-goal, and move-in-direction botlib
   import wiring used by the slice.

### Task A316: Pin ZMQ Windows err.cpp helper wiring [COMPLETED]
Priority: High
Primary areas: `references/analysis/quakelive_symbol_aliases.json`,
`tests/test_platform_services.py`,
`docs/reverse-engineering/quakelive_steam_mapping_round_411.md`
Parity estimate: **before 34% -> after 91%** for focused ZMQ Windows
`err.cpp` helper wiring, **before 92.4% -> after 92.5%** for ZMQ-related
source reconstruction confidence, and overall Quake Live source parity
**55.74% -> 55.75%**.

Completed work:

1. Rechecked the early ZMQ Windows `err.cpp` helper band against HLIL bodies,
   Ghidra function rows, imports, and source-file string anchors.
2. Added aliases for the fatal abort helper, WSA last-error string dispatch,
   Win32 `FormatMessageA` formatter, and Winsock-to-errno mapper.
3. Added a static parity guard tying the helpers to public `zmq_poll`,
   stream-engine send/recv handling, TCP listener setup, and retained
   `err.cpp` assertion lines.

### Task A315: Pin ZMQ select fd-vector and pollout reset wiring [COMPLETED]
Priority: High
Primary areas: `references/analysis/quakelive_symbol_aliases.json`,
`tests/test_platform_services.py`,
`docs/reverse-engineering/quakelive_steam_mapping_round_410.md`
Parity estimate: **before 38% -> after 92%** for focused ZMQ select-poller
fd-vector and pollout reset wiring, **before 92.3% -> after 92.4%** for
ZMQ-related source reconstruction confidence, and overall Quake Live source
parity **55.73% -> 55.74%**.

Completed work:

1. Rechecked the deferred `select_t` fd-entry vector helper slab left by
   Round 370 against `select.cpp` HLIL, Ghidra rows, and the select vtable/
   source-file anchors.
2. Added aliases for the stream-engine-facing pollout reset helper and the
   fd-entry vector grow/reserve/allocate/copy helpers.
3. Added a static parity guard tying the aliases to add/remove fd behavior,
   select-loop fd-set copies, retired-slot compaction, and stream-engine
   output backpressure call sites.

### Task A314: Pin qagame AI DMQ3 support-band mapping [COMPLETED]
Priority: High
Primary areas: `references/analysis/quakelive_symbol_aliases.json`,
`tests/test_botlib_qagame_ai_dmq3_support_parity.py`,
`docs/reverse-engineering/botlib-qagame-ai-dmq3-support-mapping-2026-06-06.md`,
`src/code/game/ai_dmq3.c`, `src/code/game/g_public.h`,
`src/code/game/g_syscalls.c`, `src/code/server/sv_game.c`,
`src/code/server/ql_game_imports.inc`
Parity estimate: **before 0% -> after 95%** for focused qagame `ai_dmq3.c`
support-band alias coverage, **before 90% -> after 97%** for source-owned
support-band parity confidence, **before 90% -> after 96%** for focused
botlib support import wiring confidence, and overall botlib plus adjacent
qagame AI execution wiring **93% -> 94%**.

Completed work:

1. Promoted the retail qagame `ai_dmq3.c` support-band identities over
   `0x10015A40..0x10017CD0`, covering AAS point-area helpers, client-name
   helpers, weapon and movement setup, inventory and battle-inventory updates,
   item use, observer and hazard probes, waypoints, aggression/retreat/chase,
   rocket-jump, persistent-powerup, camping, avoid-goal, and powerup helpers.
2. Added a parity gate that checks alias promotion against Ghidra rows,
   symbol-map names/signatures, Binary Ninja HLIL entry and flow anchors, and
   direct source-body anchors for every promoted helper.
3. Pinned the related AAS, EA, characteristic, avoid-goal, camp-spot,
   level-item, movement-state, and weapon botlib import wiring from qagame
   syscall constants through native Quake Live import slots and generated
   `QL_G_trap_*` wrappers.

### Task A313: Pin ZMQ io_object default callback wiring [COMPLETED]
Priority: High
Primary areas: `references/analysis/quakelive_symbol_aliases.json`,
`tests/test_platform_services.py`,
`docs/reverse-engineering/quakelive_steam_mapping_round_409.md`
Parity estimate: **before 45% -> after 94%** for focused ZMQ `io_object_t`
default callback-surface mapping, **before 92.2% -> after 92.3%** for
ZMQ-related source reconstruction confidence, and overall Quake Live source
parity **55.72% -> 55.73%**.

Completed work:

1. Rechecked the deferred Round 377 assertion-only `io_object_t` callbacks
   against retained `io_object.cpp` HLIL bodies and the shared
   `i_poll_events`/`io_object_t` vtable order.
2. Added aliases for the default `in_event`, `out_event`, and `timer_event`
   fail-fast callback handlers.
3. Added a static parity guard tying the names to Ghidra rows, HLIL
   `assert(false)` bodies, and reuse by REQ/session, TCP listener, and
   stream-engine subobject vtables.

### Task A312: Pin qagame AI DMQ3 team-goal mapping [COMPLETED]
Priority: High
Primary areas: `references/analysis/quakelive_symbol_aliases.json`,
`tests/test_botlib_qagame_ai_dmq3_team_goal_parity.py`,
`docs/reverse-engineering/botlib-qagame-ai-dmq3-team-goal-mapping-2026-06-06.md`,
`src/code/game/ai_dmq3.c`, `src/code/game/g_public.h`,
`src/code/game/g_syscalls.c`, `src/code/server/sv_game.c`,
`src/code/server/ql_game_imports.inc`
Parity estimate: **before 0% -> after 95%** for focused qagame `ai_dmq3.c`
team-goal alias coverage, **before 88% -> after 96%** for source-owned
team-goal source parity confidence, **before 90% -> after 96%** for focused
botlib/AAS/EA wiring into team-goal selection, and overall botlib plus adjacent
qagame AI execution wiring **92% -> 93%**.

Completed work:

1. Promoted the retail qagame `ai_dmq3.c` team-goal helper identities over
   `0x10013BE0..0x10015960`, covering team predicates, ordered-task restore,
   refusal/status helpers, CTF/1FCTF/Obelisk/Harvester seek and retreat
   dispatchers, and `BotTeamGoals`.
2. Added a parity gate that checks alias promotion against Ghidra rows,
   symbol-map names/signatures, Binary Ninja HLIL entry and cross-call anchors,
   and direct source-body anchors for every promoted helper.
3. Pinned the related AAS travel-time and EA action botlib import wiring from
   qagame syscall constants through native Quake Live import slots and generated
   `QL_G_trap_*` wrappers.

### Task A311: Pin ZMQ message pipe queue tail wiring [COMPLETED]
Priority: High
Primary areas: `references/analysis/quakelive_symbol_aliases.json`,
`tests/test_platform_services.py`,
`docs/reverse-engineering/quakelive_steam_mapping_round_408.md`
Parity estimate: **before 70% -> after 94%** for focused ZMQ message pipe
queue tail wiring, **before 92.1% -> after 92.2%** for ZMQ-related source
reconstruction confidence, and overall Quake Live source parity
**55.71% -> 55.72%**.

Completed work:

1. Rechecked the deferred `ypipe_conflate_t<msg_t,256>` final vtable callback
   that Binary Ninja renders as `operator new[]`.
2. Added aliases for the conflating message-pipe probe callback and the
   non-deleting `ypipe_base_t<msg_t,256>` destructor.
3. Added a static parity guard tying the aliases to Ghidra rows, HLIL
   lock/probe body, vtable slot order, and analysis-symbol RTTI/vtable anchors.

### Task A310: Pin ZMQ endpoint container lifecycle wiring [COMPLETED]
Priority: High
Primary areas: `references/analysis/quakelive_symbol_aliases.json`,
`tests/test_platform_services.py`,
`docs/reverse-engineering/quakelive_steam_mapping_round_407.md`
Parity estimate: **before 48% -> after 93%** for focused ZMQ endpoint
container lifecycle wiring, **before 91.9% -> after 92.1%** for ZMQ-related
source reconstruction confidence, and overall Quake Live source parity
**55.70% -> 55.71%**.

Completed work:

1. Rechecked the deferred endpoint lifecycle helpers against socket-base
   endpoint allocation, TCP protocol detection, concrete TCP address ownership,
   endpoint URI rendering, and session-base destructor cleanup.
2. Added aliases for the endpoint container constructor/destructor at
   `sub_41AAE0` and `sub_41AB60`.
3. Added a static parity guard tying the aliases to Ghidra rows, retained HLIL
   constructor/destructor bodies, the `tcp` literal, renderer dispatch, and
   session cleanup evidence.

### Task A309: Pin qagame AI DMNet tutorial-tail mapping [COMPLETED]
Priority: High
Primary areas: `references/analysis/quakelive_symbol_aliases.json`,
`references/symbol-maps/qagame.json`,
`tests/test_botlib_qagame_ai_dmnet_tutorial_tail_parity.py`,
`tests/test_ctf_oneflag_retail_parity.py`,
`docs/reverse-engineering/botlib-qagame-ai-dmnet-tutorial-tail-mapping-2026-06-06.md`,
`src/code/game/ai_dmq3.c`, `src/code/game/ai_main.c`,
`src/code/game/g_cmds.c`, `src/code/game/g_public.h`,
`src/code/game/g_syscalls.c`, `src/code/server/sv_game.c`,
`src/code/server/ql_game_imports.inc`
Parity estimate: **before 0% -> after 94%** for focused qagame tutorial-tail
alias coverage, **before 85% -> after 98%** for source-owned
`BotCTFCarryingFlag` retail predicate parity, **before 87% -> after 94%** for
focused training/botlib movement and EA wiring confidence, and overall botlib
plus adjacent qagame AI execution wiring **91% -> 92%**.

Completed work:

1. Promoted the retail-only qagame `ai_dmnet.c` tutorial-tail identities over
   `0x1000ECC0..0x10013B00`, including teammate seeking, teammate leading,
   torment-human, fragbait lead, instagib, `BotCTFCarryingFlag`, and `BotTeam`.
2. Reconstructed the safe source-owned `BotCTFCarryingFlag` predicate so it
   accepts the retail second CTF-like gametype slot, represented in current
   source as `GT_ATTACK_DEFEND`, alongside `GT_CTF`.
3. Added a parity gate that checks alias promotion against Ghidra rows,
   symbol-map names/signatures, Binary Ninja HLIL entry/call anchors, Ghidra
   decompile strings, source-owned helper bodies, training cvars, and botlib
   movement/EA import wiring.
4. Documented the remaining source gap: the retail tutorial node bodies require
   a future `bot_state_t` tail-layout reconstruction before they can be compiled
   accurately into `ai_dmnet.c`.

### Task A308: Pin ZMQ TCP address endpoint parser wiring [COMPLETED]
Priority: High
Primary areas: `references/analysis/quakelive_symbol_aliases.json`,
`tests/test_platform_services.py`,
`docs/reverse-engineering/quakelive_steam_mapping_round_406.md`
Parity estimate: **before 57% -> after 91%** for focused ZMQ TCP address
endpoint parser wiring, **before 91.7% -> after 91.9%** for ZMQ-related
source reconstruction confidence, and overall Quake Live source parity
**55.69% -> 55.70%**.

Completed work:

1. Rechecked `tcp_address.cpp` endpoint parsing against HLIL source-file
   strings, promoted `tcp_address_t`/`tcp_address_mask_t` vtable symbols,
   Ghidra function rows, and existing listener/connecter call-site evidence.
2. Added 5 aliases for NIC-name resolution, default and sockaddr-backed
   address construction, the address destructor body, and listener-side address
   mask matching.
3. Re-pinned existing TCP address resolve/stringify and address-mask
   resolve/stringify aliases so listener `getsockname` reporting, accept
   filtering, and options mask parsing remain tied to retail evidence.

### Task A307: Pin qagame AI DMNet seek/battle node mapping [COMPLETED]
Priority: High
Primary areas: `references/analysis/quakelive_symbol_aliases.json`,
`tests/test_botlib_qagame_ai_dmnet_battle_parity.py`,
`docs/reverse-engineering/botlib-qagame-ai-dmnet-battle-node-mapping-2026-06-06.md`,
`src/code/game/ai_dmnet.c`, `src/code/game/g_public.h`,
`src/code/game/g_syscalls.c`, `src/code/server/sv_game.c`,
`src/code/server/ql_game_imports.inc`
Parity estimate: **before 50% -> after 96%** for focused qagame `ai_dmnet.c`
seek/battle node alias coverage, **before 88% -> after 96%** for focused
botlib goal-stack/movement import wiring into qagame battle flow, and overall
botlib plus adjacent qagame AI execution wiring **90% -> 91%**.

Completed work:

1. Completed the qagame `ai_dmnet.c` seek/battle decision-network alias set over
   `0x1000C6E0..0x1000E700`, filling the missing `AIEnter_*` aliases around
   the already-promoted seek and battle node functions.
2. Added a parity gate that checks alias promotion against Ghidra rows,
   symbol-map names/signatures, Binary Ninja HLIL entry/call anchors,
   reconstructed source anchors, and botlib goal-stack/movement import wiring.
3. Documented the evidence trail and the observed qagame-to-botlib movement
   wiring in the dedicated reverse-engineering note for this slice.

### Task A306: Pin ZMQ subscription trie/mtrie wiring [COMPLETED]
Priority: High
Primary areas: `references/analysis/quakelive_symbol_aliases.json`,
`tests/test_platform_services.py`,
`docs/reverse-engineering/quakelive_steam_mapping_round_405.md`
Parity estimate: **before 40% -> after 88%** for focused ZMQ subscription
trie/mtrie wiring, **before 91.5% -> after 91.7%** for ZMQ-related source
reconstruction confidence, and overall Quake Live source parity
**55.68% -> 55.69%**.

Completed work:

1. Rechecked XPUB/XSUB subscription-prefix ownership against HLIL call sites,
   source-file strings, Ghidra rows, and the round-404 DIST routing aliases.
2. Added 8 aliases covering `mtrie_t` teardown, pipe-set destruction,
   node deletion, redundancy testing, XPUB mtrie-to-DIST matching, `trie_t`
   teardown, trie node deletion, and trie apply/walk behavior.
3. Re-pinned existing `mtrie_t` add/remove and `trie_t` add/remove aliases so
   prefix insertion, recursive pruning, compressed child-range maintenance, and
   XSUB subscription replay remain tied to retail evidence.

### Task A305: Pin qagame AI DMNet goal-prelude mapping [COMPLETED]
Priority: High
Primary areas: `references/analysis/quakelive_symbol_aliases.json`,
`tests/test_botlib_qagame_ai_dmnet_goal_parity.py`,
`docs/reverse-engineering/botlib-qagame-ai-dmnet-goal-prelude-mapping-2026-06-06.md`,
`src/code/game/ai_dmnet.c`, `src/code/game/g_public.h`,
`src/code/game/g_syscalls.c`, `src/code/server/sv_game.c`,
`src/code/server/ql_game_imports.inc`
Parity estimate: **before 5% -> after 96%** for focused qagame `ai_dmnet.c`
LTG/node prelude alias coverage, **before 86% -> after 95%** for focused
botlib goal/movement import wiring into qagame node flow, and overall botlib
plus adjacent qagame AI execution wiring **89% -> 90%**.

Completed work:

1. Promoted the qagame `ai_dmnet.c` long-term-goal and node-entry prelude over
   `0x100083C0..0x1000C640`, including air-goal selection, nearby-goal
   selection, LTG fallback, intermission/stand/respawn entry, path clearing,
   activate-entity seeking, and seek-NBG entry.
2. Added a parity gate that checks alias promotion against Ghidra rows,
   symbol-map names/signatures, Binary Ninja HLIL entry/call anchors,
   reconstructed source anchors, and botlib goal/movement import wiring.
3. Documented the evidence trail and the observed qagame-to-botlib wiring in
   the dedicated reverse-engineering note for this slice.

### Task A304: Pin ZMQ FQ/LB/DIST pipe routing helper wiring [COMPLETED]
Priority: High
Primary areas: `references/analysis/quakelive_symbol_aliases.json`,
`tests/test_platform_services.py`,
`docs/reverse-engineering/quakelive_steam_mapping_round_404.md`
Parity estimate: **before 42% -> after 90%** for focused ZMQ FQ/LB/DIST
pipe routing helper wiring, **before 91.2% -> after 91.5%** for ZMQ-related
source reconstruction confidence, and overall Quake Live source parity
**55.67% -> 55.68%**.

Completed work:

1. Rechecked `fq.cpp`, `lb.cpp`, and `dist.cpp` helper bodies against HLIL
   entry points, source-file strings, Ghidra function rows, and existing
   `pipe_t`/queue aliases.
2. Added 17 aliases covering fair-queue attach/activate/terminate/probe,
   load-balancer terminate/activate/probe, distribution attach/activate/
   terminate/send/write, and the FQ/LB vector push helpers.
3. Re-pinned existing `zmq_fq_t_recvpipe` and `zmq_lb_t_sendpipe` names so
   the recovered routing layer remains tied to read/write vtable dispatch,
   multipart state handling, flush/termination behavior, and `EAGAIN`
   fallbacks.

### Task A303: Pin qagame AI command team-order mapping [COMPLETED]
Priority: High
Primary areas: `references/analysis/quakelive_symbol_aliases.json`,
`tests/test_botlib_qagame_ai_cmd_parity.py`,
`docs/reverse-engineering/botlib-qagame-ai-cmd-team-order-mapping-2026-06-06.md`,
`src/code/game/ai_cmd.c`, `src/code/server/sv_game.c`,
`src/code/server/ql_game_imports.inc`
Parity estimate: **before 0% -> after 95%** for focused qagame `ai_cmd.c`
team-order alias coverage, **before 82% -> after 94%** for focused botlib
match-parser wiring into qagame command handling, and overall botlib plus
adjacent qagame AI/chat command wiring **88% -> 89%**.

Completed work:

1. Promoted 39 qagame team-message and team-order identities, with both
   `FUN_...` and `sub_...` aliases, across `0x10004930..0x100080A0`.
2. Cross-checked the slice against symbol-map names/signatures, Ghidra function
   rows, HLIL entry/call anchors, and reconstructed `ai_cmd.c` source bodies.
3. Added a focused parity gate for team-goal lookup, time parsing, addressed
   message filtering, patrol waypoint parsing, team-order LTG transitions,
   subteam/checkpoint/formation/leadership handlers, CTF status handling, and
   the central `BotMatchMessage` dispatcher.
4. Pinned the botlib match parser import wiring used by the command layer:
   `BOTLIB_AI_FIND_MATCH` and `BOTLIB_AI_MATCH_VARIABLE` through game syscall
   mapping, server import initialization, and generated qagame wrappers.

### Task A302: Pin ZMQ message pipe backing queue wiring [COMPLETED]
Priority: High
Primary areas: `references/analysis/quakelive_symbol_aliases.json`,
`tests/test_platform_services.py`,
`docs/reverse-engineering/quakelive_steam_mapping_round_403.md`
Parity estimate: **before 37% -> after 89%** for focused ZMQ message pipe
backing queue wiring, **before 90.9% -> after 91.2%** for ZMQ-related source
reconstruction confidence, and overall Quake Live source parity
**55.66% -> 55.67%**.

Completed work:

1. Rechecked `pipe.cpp` queue allocation and vtable evidence for `pipepair`,
   `pipe_t`, normal `ypipe_t<msg_t,256>`, conflating
   `ypipe_conflate_t<msg_t,256>`, and `yqueue<msg_t,256>`.
2. Added 28 aliases covering conflating write/read helpers, pipe scalar and
   array-item destructor thunks, normal and conflating message ypipe
   constructors/destructors/callbacks, shared ypipe flush publishing, and
   message yqueue chunk allocation/destruction/push/unpush.
3. Re-pinned 7 existing `pipe_t` owners so the recovered queue callbacks remain
   tied to pipepair allocation, pipe construction/destruction, read/write,
   rollback, and hiccup queue replacement.

### Task A301: Pin qagame bot chat prologue mapping [COMPLETED]
Priority: High
Primary areas: `references/analysis/quakelive_symbol_aliases.json`,
`tests/test_botlib_chat_parity.py`,
`docs/reverse-engineering/botlib-qagame-chat-prologue-mapping-2026-06-06.md`,
`src/code/game/ai_chat.c`
Parity estimate: **before 0% -> after 96%** for focused qagame bot
chat/ranking prologue alias coverage, **before 90% -> after 93%** for focused
botlib plus qagame chat wiring confidence, and overall botlib plus adjacent
qagame AI/chat wiring **87% -> 88%**.

Completed work:

1. Promoted 24 qagame bot chat/ranking prologue identities, with both
   `FUN_...` and `sub_...` aliases, across `0x10001000..0x100033F0`.
2. Cross-checked the slice against qagame owner metadata, imports, exports,
   symbol-map names/signatures, Ghidra function rows, HLIL entry/call anchors,
   and the reconstructed `ai_chat.c` source bodies.
3. Added a focused parity gate for the active-player, ranking, opponent-name,
   map-title, weapon-name, visible-enemy, valid-chat-position, chat-handler,
   chat-time, and chat-test source/HLIL shapes.

### Task A300: Pin ZMQ socket-base default virtual/interface wiring [COMPLETED]
Priority: High
Primary areas: `references/analysis/quakelive_symbol_aliases.json`,
`tests/test_platform_services.py`,
`docs/reverse-engineering/quakelive_steam_mapping_round_402.md`
Parity estimate: **before 54% -> after 91%** for focused `socket_base_t`
default virtual/interface wiring, **before 90.7% -> after 90.9%** for
ZMQ-related source reconstruction confidence, and overall Quake Live source
parity **55.65% -> 55.66%**.

Completed work:

1. Rechecked the shared `socket_base_t` primary vtable and the
   `array_item_t<0>`, `i_poll_events`, and `i_pipe_events` subobject vtables
   against the retail HLIL and Ghidra function rows.
2. Added 17 aliases covering the socket-base scalar deleting destructor,
   process-destroy state transition, default unsupported xsetsockopt/xsend/xrecv
   callbacks, assert-false activation/timer callbacks, poll in-event command
   pumping, pipe-event forwarding, pipe-terminated cleanup, and subobject
   destructor thunks.
3. Re-pinned 4 existing socket-base and pending-connection helpers so
   command-pump, destroyed-flag teardown, complete destruction, and pending
   connection erase behavior remain tied to the shared callback evidence.

### Task A299: Pin ZMQ PAIR/STREAM socket-family wiring [COMPLETED]
Priority: High
Primary areas: `references/analysis/quakelive_symbol_aliases.json`,
`tests/test_platform_services.py`,
`docs/reverse-engineering/quakelive_steam_mapping_round_401.md`,
`src/code/server/sv_zmq.c`
Parity estimate: **before 35% -> after 88%** for focused PAIR/STREAM
socket-family wiring, **before 90.4% -> after 90.7%** for ZMQ-related source
reconstruction confidence, and overall Quake Live source parity
**55.64% -> 55.65%**.

Completed work:

1. Rechecked the Quake Live Steam libzmq factory edges for PAIR (`0`) and
   STREAM (`11`) against HLIL, Ghidra function rows, promoted vtable symbols,
   existing stream aliases, and the reconstructed server ZMQ service context.
2. Added 22 aliases covering PAIR constructor/destructor, singleton-pipe
   attach/termination, send/receive/probe callbacks, PAIR interface thunks,
   STREAM constructor/destructor, pipe attachment, termination, write
   activation, and STREAM interface thunks.
3. Re-pinned 5 existing shared/STREAM aliases so identity-framed STREAM
   send/receive/prefetch behavior remains tied to factory-call evidence,
   source-file strings, vtable slots, and function rows.

### Task A298: Pin ROQ cinematic continuation beyond botlib boundary [COMPLETED]
Priority: High
Primary areas: `tests/test_botlib_structure_tail_cgame_boundary_parity.py`,
`src/code/client/cl_cin.c`,
`references/analysis/quakelive_symbol_aliases.json`,
`docs/reverse-engineering/botlib-roq-cinematic-continuation-boundary-mapping-2026-06-06.md`
Parity estimate: **before 68% -> after 99%** for focused ROQ cinematic
continuation boundary classification, **before 0% -> after 98%** for direct
`decodeCodeBook`/`RoQInterrupt` source and HLIL coverage inside botlib
boundary gates, and overall botlib plus adjacent client/cinematic wiring
**86% -> 87%**.

Completed work:

1. Extended the botlib structure-tail/cgame-boundary gate from
   `ROQ_GenYUVTables` through the adjacent retail
   `0x004B1010..0x004B3510` cinematic decode/control slab.
2. Pinned the promoted adjacent owners from `yuv_to_rgb` and
   `decodeCodeBook` through `RoQInterrupt`, `CIN_RunCinematic`,
   `CIN_PlayCinematic`, and `SCR_RunCinematic`.
3. Added direct source anchors for the large ROQ codebook and interrupt
   dispatch bodies, including sample-depth branches, VQ expansion calls,
   streamed-read loop handling, audio decode branches, quad-info dispatch, and
   oversized-frame guard behavior.
4. Rechecked the continuation against committed Ghidra function rows, HLIL
   call/constant anchors, and `cl_cin.c` source ownership.
5. Verified that promoted aliases from the botlib support tail through this
   full cinematic continuation now all have direct `test_botlib_*.py`
   mentions.

### Task A297: Pin ZMQ publication socket-family wiring [COMPLETED]
Priority: High
Primary areas: `references/analysis/quakelive_symbol_aliases.json`,
`tests/test_platform_services.py`,
`docs/reverse-engineering/quakelive_steam_mapping_round_400.md`,
`src/code/server/sv_zmq.c`
Parity estimate: **before 46% -> after 89%** for focused
PUB/SUB/PULL/PUSH and XPUB/XSUB socket-family wiring, **before 90.0% -> after
90.4%** for ZMQ-related source reconstruction confidence, and overall Quake
Live source parity **55.63% -> 55.64%**.

Completed work:

1. Rechecked the Quake Live Steam libzmq factory cases for PUB (`1`),
   SUB (`2`), PULL (`7`), PUSH (`8`), XPUB (`9`), and XSUB (`10`) against
   HLIL, Ghidra function rows, vtable symbols, existing aliases, and the
   retained server stats `QL_ZMQ_PUB` source usage.
2. Added 39 aliases covering PUB/SUB wrappers, PULL fair-queue receive,
   PUSH load-balancer send, and the XPUB/XSUB scalar/interface destructor
   thunks that complete their vtable coverage.
3. Re-pinned 23 existing XPUB/XSUB and shared activation/output aliases so
   the publication pipeline remains tied to factory-call evidence, source-file
   strings, vtable slots, function rows, and retained stats publication code.

### Task A296: Pin post-structure botlib boundary into client timing and ROQ [COMPLETED]
Priority: High
Primary areas: `tests/test_botlib_structure_tail_cgame_boundary_parity.py`,
`src/code/client/cl_cgame.c`, `src/code/client/cl_cin.c`,
`references/analysis/quakelive_symbol_aliases.json`,
`docs/reverse-engineering/botlib-post-structure-client-cinematic-boundary-mapping-2026-06-06.md`
Parity estimate: **before 86% -> after 99%** for focused post-structure
botlib/client ownership-boundary classification, **before 72% -> after 99%**
for focused cgame timing and ROQ cinematic helper coverage inside botlib
boundary gates, and overall botlib plus adjacent parser/client wiring
**85% -> 86%**.

Completed work:

1. Extended the botlib structure-tail/cgame-boundary gate past
   `CL_GetServerCommand` into the retail `0x004B0610..0x004B0F60` slab.
2. Pinned the promoted adjacent owners: `CL_GameCommand`,
   `CL_CGameRendering`, `CL_AdjustServerTimeDelta`, `CL_FirstSnapshot`,
   `CL_SetCGameTime`, `RllDecodeStereoToStereo`, `move8_32`, `blit8_32`,
   `blitVQQuad32fs`, and `ROQ_GenYUVTables`.
3. Explicitly bounded retail `0x004B0A50` as the source-modeled cgame native
   import integrity guard row, not as a botlib owner or promoted alias.
4. Rechecked source anchors in `cl_cgame.c` and `cl_cin.c` against the
   committed Quake Live HLIL and Ghidra function rows.
5. Verified that promoted aliases from the botlib support tail through this
   adjacent boundary range now all have direct `test_botlib_*.py` mentions.

### Task A295: Pin ZMQ REP/router socket-family wiring [COMPLETED]
Priority: High
Primary areas: `references/analysis/quakelive_symbol_aliases.json`,
`tests/test_platform_services.py`,
`docs/reverse-engineering/quakelive_steam_mapping_round_399.md`,
`src/code/server/sv_zmq.c`
Parity estimate: **before 39% -> after 88%** for focused REP/router
socket-family wiring, **before 89.7% -> after 90.0%** for ZMQ-related source
reconstruction confidence, and overall Quake Live source parity
**55.62% -> 55.63%**.

Completed work:

1. Rechecked the Quake Live Steam libzmq factory cases for REP (`4`) and
   ROUTER (`6`) against HLIL, Ghidra function rows, vtable symbols, existing
   aliases, and the retained server RCON `QL_ZMQ_ROUTER` source usage.
2. Added 20 REP/router aliases and re-pinned 4 existing ROUTER aliases covering
   constructor/destructor ownership, REP send/receive state gating, ROUTER pipe
   attachment, option handling, termination, activation, identity lookup, and
   multipart send/receive callbacks.
3. Added a focused regression guard tying the aliases to factory-call evidence,
   source-file strings, vtable slots, function rows, and the retained RCON
   ROUTER socket construction.

### Task A294: Reconstruct botlib import callback surface delete identity [COMPLETED]
Priority: High
Primary areas: `src/code/server/sv_bot.c`,
`src/code/game/botlib.h`,
`tests/test_botlib_import_callback_surface_parity.py`,
`tests/test_botlib_server_game_bridge_parity.py`,
`tests/test_botlib_internal_parity.py`,
`tests/test_engine_cvar_retail_parity.py`,
`docs/reverse-engineering/botlib-import-callback-surface-mapping-2026-06-06.md`
Parity estimate: **before 94% -> after 99%** for focused botlib import
callback surface mapping, **before 85% -> after 99%** for focused debug
line/polygon callback identity, and overall botlib plus related server/game
wiring **97% -> 97%**.

Completed work:

1. Rechecked the `SV_BotInitBotLib` callback table at retail
   `0x004DD940` against the Quake Live HLIL locals, promoted aliases, Ghidra
   rows, `botlib_import_t` field order, and source assignment order.
2. Reconstructed the retail delete callback identity by assigning
   `botlib_import.DebugLineDelete` directly to `BotImport_DebugPolygonDelete`,
   matching retail's shared `sub_4dd430` table entry for both line and polygon
   delete.
3. Preserved the compatibility `BotImport_DebugLineDelete` wrapper while
   keeping the runtime callback table faithful to retail pointer identity.
4. Added focused parity coverage for trace copying, BSP metadata callbacks,
   memory/hunk callbacks, filesystem callback placement, and debug
   line/polygon callback behavior.
5. Normalized the botlib parity gates' Ghidra `functions.csv` references to
   the committed `references/reverse-engineering/ghidra/quakelive_steam/`
   corpus while keeping alias-map lookups on the existing
   `quakelive_steam_srp` key.

### Task A293: Pin botlib debug draw native micro-slab [COMPLETED]
Priority: High
Primary areas: `src/code/game/g_public.h`,
`src/code/game/g_syscalls.c`, `src/code/game/ai_main.c`,
`src/code/game/botlib.h`, `src/code/server/sv_game.c`,
`src/code/botlib/be_interface.c`, `src/code/botlib/be_ai_move.c`,
`tests/test_botlib_debug_draw_native_micro_slab_parity.py`,
`docs/reverse-engineering/botlib-debug-draw-native-micro-slab-mapping-2026-06-06.md`
Parity estimate: **before 72% -> after 99%** for focused botlib debug
draw native micro-slab mapping, **before 90% -> after 97%** for focused
direct-only botlib native import classification, and overall botlib plus
qagame native import wiring **96% -> 97%**.

Completed work:

1. Rechecked native slots 83 and 84 against the Quake Live HLIL native import
   table, Ghidra row sizes, source native enum, qagame direct import wrappers,
   and the server native import initializer.
2. Pinned the odd retail relationship where these native table slots sit
   between the AAS tail and EA slab, while their botlib export offsets follow
   the AI movement/weapon/genetic tail at `0x1e8` and `0x1ec`.
3. Verified that the helpers are direct-native only and do not belong in
   `G_MapNativeImport` as legacy syscall-compatible IDs.
4. Tied the qagame `BotTestAAS` caller to the botlib AI export bodies for
   `BotDrawDebugAreas` and `BotDrawAvoidSpots`.

### Task A292: Pin botlib AI movement/weapon native tail [COMPLETED]
Priority: High
Primary areas: `src/code/game/g_public.h`,
`src/code/game/g_syscalls.c`, `src/code/server/sv_game.c`,
`src/code/server/ql_game_imports.inc`,
`tests/test_botlib_ai_movement_weapon_native_tail_parity.py`,
`docs/reverse-engineering/botlib-ai-movement-weapon-native-tail-mapping-2026-06-06.md`
Parity estimate: **before 78% -> after 99%** for focused AI
movement/weapon/genetic native tail mapping, **before 95% -> after 97%** for
focused botlib native import table coverage, and overall botlib plus qagame
native import wiring **95% -> 96%**.

Completed work:

1. Rechecked native slots 166 through 184 against the Quake Live HLIL import
   table, Ghidra row sizes where present, source native enum, legacy syscall
   map, server import initializer, and generated qagame wrappers.
2. Pinned the non-linear `AddAvoidSpot` ordering: wrapper order before
   `BotMoveToGoal`, retail native slot 177 after `InitMoveState`, and retail
   trampoline address `0x004e23d0`.
3. Preserved the raw-thunk classifications for `AllocMoveState` at `0x4e2500`
   and `AllocWeaponState` at `0x4e25b0`.
4. Verified the movement float ABI paths for `AddAvoidSpot`,
   `MoveInDirection`, and `MovementViewTarget`.
5. Added focused parity coverage to keep botlib AI slot 184 from drifting into
   the adjacent Quake Live service import slab.

### Task A291: Reconstruct botlib AI goal native slab float marshaling [COMPLETED]
Priority: High
Primary areas: `src/code/game/g_syscalls.c`,
`src/code/server/ql_game_imports.inc`,
`tests/test_botlib_ai_goal_native_slab_parity.py`,
`docs/reverse-engineering/botlib-ai-goal-native-slab-mapping-2026-06-06.md`
Parity estimate: **before 76% -> after 99%** for focused AI goal/item native
slab mapping, **before 90% -> after 96%** for focused botlib float
syscall/native marshaling coverage, and overall botlib plus qagame native
import wiring **94% -> 95%**.

Completed work:

1. Rechecked native slots 137 through 165 against the Quake Live HLIL import
   table, Ghidra row sizes where present, source native enum, legacy syscall
   map, server import initializer, and generated qagame wrappers.
2. Pinned the retail native table-order differences for avoid-goal reset/remove
   wrappers and camp/map/level goal lookup wrappers.
3. Preserved the non-row classifications for `BotInitLevelItems` at
   `0x4e22a0` and raw `BotUpdateEntityItems` table address `0x4e22b0`.
4. Reconstructed `BotMutateGoalFuzzyLogic` float argument marshaling through
   `PASSFLOAT(range)` and `QL_G_PASSFLOAT(range)`.
5. Added focused parity coverage to prevent the goal/item native slab from
   being reordered by legacy export offset or losing float ABI conversions.

### Task A290: Reconstruct botlib AI character/chat native slots [COMPLETED]
Priority: High
Primary areas: `src/code/game/g_public.h`,
`src/code/game/g_syscalls.c`, `src/code/server/sv_game.c`,
`src/code/server/ql_game_imports.inc`,
`tests/test_botlib_ai_character_chat_native_slab_parity.py`,
`tests/test_botlib_chat_parity.py`,
`tests/test_game_native_export_helper_parity.py`,
`docs/reverse-engineering/botlib-ai-character-chat-native-slab-mapping-2026-06-06.md`
Parity estimate: **before 74% -> after 99%** for focused AI character/chat
native slab mapping, **before 88% -> after 95%** for focused botlib native
import direct-vs-compat classification, and overall botlib plus qagame native
import wiring **93% -> 94%**.

Completed work:

1. Rechecked native slots 110 through 136 against the Quake Live HLIL import
   table, Ghidra row sizes, source native enum, legacy syscall map, server
   import initializer, and generated qagame wrappers.
2. Reconstructed `G_QL_IMPORT_BOTLIB_AI_CHAT_LENGTH = 126` and mapped
   `BOTLIB_AI_CHAT_LENGTH` directly to `QL_G_trap_BotChatLength`.
3. Reconstructed `G_QL_IMPORT_BOTLIB_AI_STRING_CONTAINS = 129` and mapped
   `BOTLIB_AI_STRING_CONTAINS` directly to `QL_G_trap_StringContains`.
4. Preserved the raw-thunk classification for `BotAllocChatState` at
   `0x4e1d80` instead of promoting a fake Ghidra function row.
5. Updated stale compatibility-only coverage and added focused parity coverage
   to prevent the character/chat native import slab from regressing.

### Task A289: Reconstruct client SteamUserStats float descriptor lane [COMPLETED]
Priority: High
Primary areas: `src/code/client/cl_main.c`,
`src/common/platform/platform_steamworks.c`,
`src/common/platform/platform_steamworks.h`,
`tests/steamworks_harness.c`, `tests/test_steamworks_harness.py`,
`tests/test_platform_services.py`,
`docs/reverse-engineering/quakelive_steam_mapping_round_383.md`
Parity estimate: **before 86% -> after 99%** for focused client
`STATS` descriptor-control-flow parity, **before 99% -> after 99.5%**
for client `SteamUserStats` readback wrapper coverage, and broader
Steamworks parity remains approximately **99%** because live backend values,
localized achievement metadata, and production service availability are
outside this deterministic source/harness pass.

Completed work:

1. Rechecked the retained `users.stats` callback descriptor walk at HLIL
   anchors `0x0046006b`, `0x00460074`, `0x004600ef`, `0x00460103`,
   `0x0046010e`, `0x0046008d`, and `0x00460149`.
2. Parsed the committed HLIL data table rooted at `data_55da98` and confirmed
   `data_55da8c = 0x58`, seven-dword rows, and all 88 shipped descriptor
   discriminators set to zero.
3. Added `QL_Steamworks_GetUserStatFloat` for the client `SteamUserStats`
   vtable slot `0x44 / 4`, plus the disabled output-clearing fallback.
4. Converted the retained client stat catalog into explicit `{ name, isFloat }`
   descriptors and preserved the current catalog as integer rows.
5. Updated the `STATS` JSON builder to retain the retail float/int branch while
   keeping the shipped row behavior unchanged.
6. Extended the executable Steamworks harness and ctypes coverage for the
   float readback slot, including invalid-input guards, output clearing,
   forwarding, failure propagation, and disabled fallback behavior.

### Task A288: Pin botlib AAS native wrapper slab [COMPLETED]
Priority: High
Primary areas: `src/code/game/g_public.h`,
`src/code/game/g_syscalls.c`, `src/code/server/sv_game.c`,
`src/code/server/ql_game_imports.inc`,
`tests/test_botlib_aas_native_wrapper_slab_parity.py`,
`docs/reverse-engineering/botlib-aas-native-wrapper-slab-mapping-2026-06-06.md`
Parity estimate: **before 70% -> after 98%** for focused AAS native wrapper
slab mapping, **before 92% -> after 94%** for focused qagame botlib native
import table coverage, and overall botlib plus qagame native import wiring
**92% -> 93%**.

Completed work:

1. Rechecked native slots 61 through 82 against the Quake Live HLIL import
   table, Ghidra row sizes, source native enum, legacy syscall map, server
   import initializer, and generated qagame wrappers.
2. Pinned the retail table-order detail where `AAS_BBoxAreas` and
   `AAS_AreaInfo` occupy slots 61 and 62 before the earlier-addressed
   `AAS_EntityInfo` trampoline at slot 63.
3. Preserved the raw-thunk classification for `AAS_Initialized` at `0x4e1840`
   and `AAS_Time` at `0x4e1860` instead of promoting fake Ghidra function rows.
4. Verified the wrapper marshaling details for `AAS_Time` and
   `AAS_PredictClientMovement`, including the float bit-cast and
   `QL_G_PASSFLOAT(frametime)` handoff.
5. Added focused parity coverage to prevent AAS native imports from being
   reordered by name/address or disconnected from the legacy syscall bridge.

### Task A287: Extend SteamUserStats readback harness coverage [COMPLETED]
Priority: High
Primary areas: `src/common/platform/platform_steamworks.c`,
`tests/steamworks_harness.c`, `tests/test_steamworks_harness.py`,
`tests/test_platform_services.py`,
`docs/reverse-engineering/quakelive_steam_mapping_round_382.md`
Parity estimate: **before 58% -> after 98%** for focused client
SteamUserStats readback harness parity, **before 96% -> after 99%** for
retained `users.stats` readback wrapper evidence confidence, and broader
Steamworks parity remains approximately **99%** because live backend values,
localized achievement metadata, and the observed-but-unwrapped float-stat lane
are outside this deterministic harness pass.

Completed work:

1. Rechecked the retained `users.stats` callback JSON builder at HLIL anchors
   `0x0046008d`, `0x0046018e`, `0x004601a6`, and `0x004601c6`.
2. Added deterministic mock state for user stat value, achievement state,
   unlock time, display attribute text, last SteamID, last stat/achievement
   name, last display-attribute key, call counts, and result toggles.
3. Added client `SteamUserStats` harness slots for display attributes,
   integer stat reads, and achievement reads at `0x30 / 4`, `0x48 / 4`, and
   `0x50 / 4`.
4. Exported enabled/disabled harness wrappers for
   `QL_Steamworks_GetUserStatInt`, `QL_Steamworks_GetUserAchievement`, and
   `QL_Steamworks_GetAchievementDisplayAttribute`.
5. Added ctypes and static parity coverage tying the HLIL evidence, Round 188
   source reconstruction note, production wrappers, mock vtable slots,
   executable test, plan entry, and Round 382 note together.

### Task A286: Pin native-only botlib EA action slab [COMPLETED]
Priority: High
Primary areas: `src/code/game/g_public.h`,
`src/code/game/g_syscalls.c`, `src/code/game/g_local.h`,
`src/code/game/botlib.h`, `src/code/botlib/be_ea.c`,
`src/code/botlib/be_interface.c`, `src/code/server/sv_game.c`,
`src/code/server/ql_game_imports.inc`,
`tests/test_botlib_ea_native_action_slab_parity.py`,
`docs/reverse-engineering/botlib-ea-native-action-slab-mapping-2026-06-06.md`
Parity estimate: **before 78% -> after 99%** for focused EA native action
slab mapping, **before 84% -> after 96%** for focused native-only botlib import
classification, and overall botlib plus qagame native import wiring
**91% -> 92%**.

Completed work:

1. Rechecked native slots 85 through 109 against the Quake Live HLIL import
   table, Ghidra row sizes, source native enum, server import initializer, and
   generated qagame wrappers.
2. Pinned `G_QL_IMPORT_BOTLIB_EA_WALK = 89` as a direct-native-only import.
3. Verified that no legacy `BOTLIB_EA_WALK` enum member or `trap_EA_Walk`
   wrapper should be reconstructed in `g_syscalls.c` / `g_local.h`.
4. Cross-checked the `ea_export_t` source chain from `ACTION_WALK` through
   `EA_Walk`, `Init_EA_Export`, and `QL_G_trap_EA_Walk`.
5. Added focused parity coverage to prevent the native EA slab from being
   reordered by name or backfilled with a fake legacy syscall.

### Task A285: Extend SteamUserStats clear/reset harness coverage [COMPLETED]
Priority: High
Primary areas: `src/common/platform/platform_steamworks.c`,
`tests/steamworks_harness.c`, `tests/test_steamworks_harness.py`,
`tests/test_platform_services.py`,
`docs/reverse-engineering/quakelive_steam_mapping_round_375.md`
Parity estimate: **before 45% -> after 98%** for focused SteamUserStats
clear/reset harness parity, **before 96% -> after 99%** for retained
`stats_clear` wrapper evidence confidence, and broader Steamworks parity
remains approximately **99%** because live backend behavior is outside this
opt-in reconstruction pass.

Completed work:

1. Rechecked the retained `stats_clear` command owner at `0x00460520` and its
   `SteamUserStats()` slot `0x54` call at `0x00460531`.
2. Added deterministic mock state for reset-call count, last
   `achievementsToo` value, and configurable reset result.
3. Added `QLR_SteamUserStats_ResetAllStats` to the mock SteamUserStats vtable
   at `0x54 / 4` and exported enabled/disabled harness wrappers for
   `QL_Steamworks_ClearStats`.
4. Added ctypes coverage for the pre-initialisation guard, boolean forwarding,
   failure propagation, and disabled-build fallback behavior.
5. Added static parity coverage and
   `docs/reverse-engineering/quakelive_steam_mapping_round_375.md` to pin the
   HLIL evidence, production offset, mock vtable, executable test, and plan
   note together.

### Task A284: Correct botlib-adjacent qagame world import slots [COMPLETED]
Priority: High
Primary areas: `src/code/game/g_public.h`,
`src/code/game/g_syscalls.c`, `src/code/server/sv_game.c`,
`src/code/server/ql_game_imports.inc`,
`tests/test_botlib_qagame_world_import_slab_parity.py`,
`docs/reverse-engineering/botlib-qagame-world-import-slab-mapping-2026-06-06.md`
Parity estimate: **before 76% -> after 98%** for focused qagame world/import
slab native slot parity, **before 90% -> after 91%** for focused
botlib-adjacent qagame import environment coverage, and overall botlib plus
related server/game wiring **90% -> 91%**.

Completed work:

1. Rechecked the qagame world/import native table at
   `0x0056CFFC..0x0056D02C` against Quake Live HLIL and promoted aliases.
2. Reconstructed direct native import slots for `G_IN_PVS_IGNORE_PORTALS`,
   `G_AREAS_CONNECTED`, and `G_ENTITY_CONTACT`.
3. Corrected the native enum/server import order so slot 39 is
   `G_QL_IMPORT_LINKENTITY` and slot 40 is `G_QL_IMPORT_UNLINK_ENTITY`.
4. Bound the recovered slots in `G_MapNativeImport` and `SV_InitGameImports`
   while leaving `EntityContactCapsule` on the legacy compatibility path.
5. Added focused parity coverage for aliases, Ghidra row sizes, HLIL wrapper
   shapes, native table order, syscall remap, qagame wrappers, and source
   initializer assignments.

### Task A283: Extend client Steam identity and SteamUtils harness coverage [COMPLETED]
Priority: High
Primary areas: `src/common/platform/platform_steamworks.c`,
`tests/steamworks_harness.c`, `tests/test_steamworks_harness.py`,
`tests/test_platform_services.py`,
`docs/reverse-engineering/quakelive_steam_mapping_round_373.md`
Parity estimate: **before 68% -> after 98%** for focused client Steam
identity/SteamUtils harness parity, **before 96% -> after 99%** for bootstrap
identity/app-id wrapper evidence confidence, and broader Steamworks parity
remains approximately **99%** because live backend behavior is outside this
opt-in reconstruction pass.

Completed work:

1. Rechecked the retained local SteamID helper at `0x00460550`, persona cvar
   sync helper at `0x00460610`, IP-country helper at `0x00460690`, and
   `SteamUtils()->GetAppID` callsites at `0x00431c48` and `0x00460dd6`.
2. Added deterministic mock call counters for SteamFriends persona name,
   SteamUser identity, SteamUtils IP country, and SteamUtils app ID.
3. Exported enabled/disabled harness wrappers for persona-name, IP-country,
   app-id, and user-SteamID lookup.
4. Added ctypes coverage for persona/country copying, app-id forwarding,
   SteamID low/high projection, unavailable-user failure behavior, and
   disabled-build output clearing.
5. Added static parity coverage and
   `docs/reverse-engineering/quakelive_steam_mapping_round_373.md` to pin the
   HLIL evidence, production offsets, mock vtable, executable test, and plan
   note together.

### Task A282: Bind and pin server/qagame botlib bridge slots [COMPLETED]
Priority: High
Primary areas: `src/code/game/g_public.h`,
`src/code/game/g_syscalls.c`, `src/code/server/sv_game.c`,
`src/code/server/sv_bot.c`,
`tests/test_botlib_server_game_bridge_parity.py`,
`docs/reverse-engineering/botlib-server-game-bridge-mapping-2026-06-06.md`
Parity estimate: **before 72% -> after 100%** for focused server/qagame
botlib bridge alias coverage, **before 82% -> after 98%** for focused native
qagame botlib import-slot source parity, and focused botlib plus server/game
wiring **89% -> 90%**.

Completed work:

1. Cross-checked the promoted `SV_Bot*`, `BotImport_*`, and `QL_G_trap_Bot*`
   aliases against the committed Ghidra row sizes and Quake Live HLIL.
2. Reconstructed native qagame import slots 44, 47, and 48 as
   `G_QL_IMPORT_BOT_FREE_CLIENT`, `G_QL_IMPORT_DEBUG_POLYGON_CREATE`, and
   `G_QL_IMPORT_DEBUG_POLYGON_DELETE`.
3. Routed `G_BOT_FREE_CLIENT`, `G_DEBUG_POLYGON_CREATE`, and
   `G_DEBUG_POLYGON_DELETE` through `G_MapNativeImport` and
   `SV_InitGameProgs`.
4. Added focused source/HLIL/table coverage for the server bot lifecycle,
   botlib setup/shutdown, reliable command consumption, snapshot entity lookup,
   and qagame native import table.
5. Added a dedicated mapping note and a range scan requiring direct
   `test_botlib_*.py` mentions for the promoted bridge aliases.

### Task A281: Extend SteamFriends enumeration harness coverage [COMPLETED]
Priority: High
Primary areas: `src/common/platform/platform_steamworks.c`,
`tests/steamworks_harness.c`, `tests/test_steamworks_harness.py`,
`tests/test_platform_services.py`,
`docs/reverse-engineering/quakelive_steam_mapping_round_372.md`
Parity estimate: **before 72% -> after 98%** for focused SteamFriends
friend-list harness parity, **before 98% -> after 99%** for retained browser
friend-summary wrapper evidence confidence, and broader Steamworks parity
remains approximately **99%** because live backend behavior is outside this
opt-in reconstruction pass.

Completed work:

1. Rechecked the retained `GetFriendList` HLIL block at `0x0043355d` through
   `0x00433a00`, confirming SteamFriends slots `0x0c`, `0x10`, `0x1c`,
   `0x18`, `0x14`, `0x2c`, `0xb4`, and `0x20`.
2. Added deterministic SteamFriends mock enumeration state plus
   `GetFriendCount` and `GetFriendByIndex` vtable slots at `0x0c / 4` and
   `0x10 / 4`.
3. Exported enabled/disabled harness wrappers for friend count, by-index
   identity lookup, friend summary, and persona-name lookup.
4. Added ctypes coverage for flag forwarding, SteamID projection,
   invalid-index clearing, persona-name copying, full friend-summary
   projection, and offline fallback behavior.
5. Added static parity coverage and
   `docs/reverse-engineering/quakelive_steam_mapping_round_372.md` to pin the
   HLIL evidence, production offsets, mock vtable, executable test, and plan
   note together.

### Task A280: Split Freeze winning-team thaw respawn path [COMPLETED]
Priority: High
Primary areas: `src/code/game/g_active.c`,
`tests/test_game_active_pmove_wiring_parity.py`,
`tests/test_game_round_controller_helper_parity.py`,
`docs/reverse-engineering/freeze-tag-winning-thaw-respawn-mapping-2026-06-06.md`,
`docs/reverse-engineering/freeze-tag-mapping-2026-06-06.md`,
`docs/reverse-engineering/qagame-mapping.md`
Parity estimate: **before 55% -> after 96%** for the focused configured
winning-team thaw respawn lane. The broader Freeze thaw-respawn tail moves
approximately **88% -> 94%**, while broader Freeze Tag gametype wiring moves
approximately **95% -> 96%**.

Completed work:

1. Rechecked `FUN_1004C1B0` / `Freeze_RoundStateTransition` in the committed
   qagame Ghidra corpus and pinned the `pm_type == PM_FREEZE` branch that
   emits `EV_THAW_PLAYER`, writes `PM_NORMAL`, and tailcalls `ClientSpawn`.
2. Added `G_FreezeRespawnThawedWinner` in `g_active.c` to mirror that direct
   round-controller thaw visual and respawn handoff.
3. Routed `G_FreezeThawWinningPlayers` through the new helper instead of
   `G_FreezeThawClient`, keeping winning-team thaw distinct from assisted,
   admin, and auto-thaw paths.
4. Added focused source/evidence tests for the direct helper and updated Freeze
   round-controller parity coverage.
5. Added a dedicated mapping note and updated the umbrella Freeze/qagame maps.

### Task A279: Pin botlib-adjacent native cgame import slab [COMPLETED]
Priority: High
Primary areas: `src/code/client/cl_cgame.c`,
`src/code/cgame/cg_public.h`,
`references/analysis/quakelive_symbol_aliases.json`,
`tests/test_botlib_cgame_native_import_slab_parity.py`,
`docs/reverse-engineering/botlib-cgame-native-import-slab-mapping-2026-06-06.md`
Parity estimate: **before 45% -> after 100%** for focused native cgame
import-slab alias coverage, **before 78% -> after 97%** for focused
import-table source initializer coverage, and focused botlib plus cgame-boundary
related wiring **88% -> 89%**.

Completed work:

1. Widened the botlib-related alias/test scan to the native cgame slab at
   `0x004AF820..0x004B0500`.
2. Pinned all promoted aliases in that range against
   `quakelive_symbol_aliases.json` and Ghidra row sizes where rows exist.
3. Added HLIL wrapper-shape anchors for command, collision-model, sound,
   renderer, advertisement bridge, snapshot/input, parser, cinematic, social,
   avatar, and adjacent lifecycle owners.
4. Cross-checked `CG_QL_IMPORT_COUNT = 128` and the reconstructed
   `CL_InitCGameImports` source initializer assignments.
5. Added a final scan gate confirming no promoted names in this slab remain
   without direct `test_botlib_*.py` coverage; reserved retail-only rows remain
   fail-closed rather than overpromoted.

### Task A278: Close botlib parser-tail promoted alias coverage [COMPLETED]
Priority: High
Primary areas: `src/code/botlib/l_precomp.c`,
`src/code/botlib/l_script.c`, `src/code/botlib/l_script.h`,
`references/analysis/quakelive_symbol_aliases.json`,
`tests/test_botlib_parser_tail_coverage_parity.py`,
`docs/reverse-engineering/botlib-parser-tail-coverage-mapping-2026-06-06.md`
Parity estimate: **before 82% -> after 100%** for focused parser-tail
promoted-alias test coverage, **before 78% -> after 97%** for focused
`PC_EvaluateTokens` source-shape coverage, **before 74% -> after 96%** for
focused `l_script.c` escape/number/expect-type source-shape coverage, and
overall botlib parser/support static mapping **88% -> 89%**.

Completed work:

1. Widened the botlib alias/test scan to `0x004A83C0..0x004AF820` and isolated
   the four remaining promoted parser-tail aliases without direct botlib test
   mentions: `PC_EvaluateTokens`, `PS_ReadEscapeCharacter`, `PS_ReadNumber`,
   and `PS_ExpectTokenType`.
2. Pinned those helpers against `quakelive_symbol_aliases.json`,
   `functions.csv`, HLIL function headers, and retail callsites in the
   `quakelive_steam.exe` part03/part04 HLIL split.
3. Cross-checked reconstructed source shape for the precompiler expression
   evaluator, script escape decoder, numeric token scanner, and token-type
   validator.
4. Added a final support-tail scan gate confirming no aliases in this botlib
   parser/support band remain without a direct `test_botlib_*.py` mention.
5. Added a focused mapping note; no C source body changes or alias changes
   were justified.

### Task A277: Extend SteamFriends voice-speaking wrapper coverage [COMPLETED]
Priority: High
Primary areas: `tests/steamworks_harness.c`,
`tests/test_steamworks_harness.py`, `tests/test_platform_services.py`,
`docs/reverse-engineering/quakelive_steam_mapping_round_368.md`,
`docs/plans/steamworks-parity-plan.md`
Parity estimate: **before 60% -> after 97%** for focused SteamFriends
voice-speaking wrapper harness parity, **before 98% -> after 99%** for
retained client voice command wrapper evidence confidence, and broader
Steamworks parity remains approximately **99%** because live Steam backend
behavior and modern networking replacement work remain outside this opt-in
reconstruction pass.

Completed work:

1. Rechecked the retained SteamFriends voice-speaking evidence at `0x00460441`
   and `0x004604dc`.
2. Added mock state and a `SteamFriends` vtable slot at `0x6c / 4` for
   `SetInGameVoiceSpeaking`.
3. Exported stable enabled and disabled harness wrappers for
   `QL_Steamworks_SetInGameVoiceSpeaking`.
4. Added ctypes coverage for SteamID word-combination, speaking-on/off
   forwarding, call counts, and the offline fallback contract.
5. Added static parity coverage tying the source wrapper slot, mock vtable,
   executable coverage, HLIL evidence, and round 368 mapping note together.

### Task A276: Close residual promoted botlib alias test coverage [COMPLETED]
Priority: High
Primary areas: `src/code/botlib/be_aas_cluster.c`,
`src/code/botlib/be_aas_debug.c`, `src/code/botlib/be_ai_chat.c`,
`references/analysis/quakelive_symbol_aliases.json`,
`tests/test_botlib_residual_promoted_alias_coverage.py`,
`docs/reverse-engineering/botlib-residual-promoted-alias-coverage-2026-06-06.md`
Parity estimate: **before 70% -> after 100%** for focused residual
promoted-alias test coverage, **before 82% -> after 96%** for focused AAS
cluster/debug residual source-shape coverage, **before 84% -> after 97%** for
focused chat match-piece and integrity-tail source-shape coverage, and overall
botlib static mapping/test coverage **87% -> 88%**.

Completed work:

1. Rescanned the promoted core botlib alias band from `0x004829C0` through
   `0x004A83C0` and isolated the five remaining direct test-mention gaps:
   `AAS_CheckAreaForPossiblePortals`, `AAS_ShowFacePolygon`,
   `BotFreeMatchPieces`, `BotCheckInitialChatIntegrety`, and
   `BotCheckReplyChatIntegrety`.
2. Pinned those helpers against `quakelive_symbol_aliases.json`,
   `functions.csv`, HLIL function headers, and their retail callsites in
   `quakelive_steam.exe_hlil_part03.txt`.
3. Cross-checked the reconstructed source shape for cluster portal candidate
   detection, debug face polygon drawing, chat match-piece cleanup, and the
   initial/reply chat integrity walkers.
4. Added a final promoted-core botlib scan gate confirming no aliases in this
   band remain without a direct `test_botlib_*.py` mention.
5. Added a focused mapping note; no C source body changes or alias changes
   were justified.

### Task A275: Extend SteamUser voice wrapper harness coverage [COMPLETED]
Priority: High
Primary areas: `tests/steamworks_harness.c`,
`tests/test_steamworks_harness.py`, `tests/test_platform_services.py`,
`docs/reverse-engineering/quakelive_steam_mapping_round_367.md`,
`docs/plans/steamworks-parity-plan.md`
Parity estimate: **before 72% -> after 97%** for focused SteamUser voice
wrapper harness parity, **before 96% -> after 98%** for client Steam voice
transport evidence confidence, and broader Steamworks parity remains
approximately **99%** because live Steam microphone/backend behavior and modern
networking replacement work remain outside this opt-in reconstruction pass.

Completed work:

1. Rechecked the retained SteamUser voice slot evidence at `0x0046044c`,
   `0x00460459`, `0x004604b1`, `0x00460d4b`, and `0x00461b07`.
2. Added deterministic harness mock state and `SteamUser` vtable slots for
   start, stop, compressed voice, decompression, and optimal sample rate.
3. Exported stable enabled and disabled harness wrappers for the production
   Steam voice API family.
4. Added ctypes coverage for payload projection, output-size failure zeroing,
   compressed/uncompressed flags, sample-rate forwarding, call counts, and the
   offline fallback contract.
5. Added static parity coverage tying the source wrapper slots, mock vtable,
   harness coverage, HLIL evidence, and round 367 mapping note together.

### Task A274: Pin late botlib movement support mapping [COMPLETED]
Priority: High
Primary areas: `src/code/botlib/be_aas_move.c`,
`src/code/botlib/be_aas_reach.c`, `src/code/botlib/be_ai_move.c`,
`references/analysis/quakelive_symbol_aliases.json`,
`tests/test_botlib_movement_late_support_parity.py`,
`docs/reverse-engineering/botlib-movement-late-support-mapping-2026-06-06.md`
Parity estimate: **before 68% -> after 96%** for focused late AAS
movement/support mapping, **before 72% -> after 96%** for focused late travel
dispatch coverage, and overall botlib plus movement/reachability wiring
**86% -> 87%**.

Completed work:

1. Recomputed the botlib row coverage and confirmed the direct core remains
   closed except for the documented libjpeg false leads and folded
   `0x00486F40` weapon-jump thunk.
2. Identified promoted movement/reachability aliases that lacked focused
   parity-test coverage.
3. Pinned `AAS_DropToFloor`, `AAS_AgainstLadder`, `AAS_OnGround`,
   `AAS_ApplyFriction`, `AAS_ClipToBBox`, `AAS_GetJumpPadInfo`,
   `AAS_Reachability_EqualFloorHeight`, and `AAS_FindFaceReachabilities`
   against aliases, Ghidra rows, HLIL anchors, and source shape.
4. Pinned the late travel handlers `BotTravel_Elevator`,
   `BotTravel_FuncBobbing`, `BotFinishTravel_WeaponJump`,
   `BotTravel_JumpPad`, `BotFinishTravel_JumpPad`, `BotReachabilityTime`, and
   `BotMoveInGoalArea`, plus their `BotMoveToGoal` dispatch wiring.
5. Added a focused parity gate and mapping note; no C source body changes or
   alias changes were justified.

### Task A273: Extend legacy Steam P2P read-boundary coverage [COMPLETED]
Priority: High
Primary areas: `tests/test_steamworks_harness.py`,
`tests/test_platform_services.py`,
`docs/reverse-engineering/quakelive_steam_mapping_round_366.md`,
`docs/plans/steamworks-parity-plan.md`
Parity estimate: **before 96% -> after 98%** for focused legacy P2P
read-boundary harness parity, **before 98% -> after 98.5%** for legacy Steam
P2P wrapper evidence confidence, and broader Steamworks parity remains
approximately **99%** with live backend behavior and modern networking
replacement design still outside this opt-in reconstruction pass.

Completed work:

1. Rechecked the retained `SteamNetworking` and
   `SteamGameServerNetworking` availability/read slot evidence in the retail
   HLIL and existing Steamworks mapping rounds.
2. Extended the client P2P harness path so a staged packet rejected by a
   too-small read buffer clears stale output size and remote SteamID values.
3. Extended the server P2P harness path with the matching too-small buffer
   rejection coverage.
4. Added static parity coverage for import names, client/server vtable slots,
   mock read-output clearing, and the round 366 evidence note.
5. Left production Steamworks wrappers unchanged because this pass proved local
   harness boundary behavior rather than a new retail slot or live SDK edge.

### Task A272: Close botlib-adjacent cgame shutdown import boundary [COMPLETED]
Priority: High
Primary areas: `src/code/client/cl_cgame.c`, `src/code/client/cl_main.c`,
`src/code/client/client.h`, `src/code/qcommon/common.c`,
`src/code/cgame/cg_public.h`, `references/analysis/quakelive_symbol_aliases.json`,
`tests/test_botlib_cgame_shutdown_import_boundary_parity.py`,
`docs/reverse-engineering/botlib-cgame-shutdown-import-boundary-mapping-2026-06-06.md`
Parity estimate: **before 70% -> after 98%** for focused cgame shutdown owner
mapping, **before 80% -> after 92%** for adjacent cgame native residual import
classification, and overall botlib plus related parser/import/lifecycle wiring
**85% -> 86%**.

Completed work:

1. Rechecked `0x004AF820..0x004B0500` across HLIL, Ghidra `functions.csv`,
   source lifecycle owners, and native cgame import wiring.
2. Promoted `0x004AFBF0 -> CL_ShutdownCGame`, matching the source
   `KEYCATCH_CGAME`, `CG_SHUTDOWN`, `VM_Free`, and `cgvm = NULL` lifecycle
   sequence.
3. Bounded the remaining unaliased cgame-native import rows at `0x004AFFC0`,
   `0x004B00C0`, and `0x004B0370` as residual table trampolines whose exact
   public meanings remain weaker than their slot neighborhoods.
4. Confirmed the current source keeps the unresolved retail-only slots behind
   `QL_CG_trap_RetailReservedImport`, preserving fail-closed behavior instead
   of inventing live service or renderer behavior.
5. Added a focused parity gate and mapping note for the botlib-adjacent cgame
   shutdown/import boundary; no C source body changes were justified.

### Task A271: Extend Steam UGC call-result failure projection coverage [COMPLETED]
Priority: High
Primary areas: `tests/steamworks_harness.c`,
`tests/test_steamworks_harness.py`, `tests/test_platform_services.py`,
`docs/reverse-engineering/quakelive_steam_mapping_round_364.md`,
`docs/plans/steamworks-parity-plan.md`
Parity estimate: **before 58% -> after 96%** for focused UGC call-result
failure projection coverage, **before 94% -> after 98%** for combined UGC
query callback pump projection, and broader Steamworks parity remains
approximately **99%** because live backend timing, workshop availability, and
the raw filter semantic remain intentionally bounded.

Completed work:

1. Rechecked the retained `SteamUGC` create/send query slots and the
   `SteamUGCQueryCompleted_t` call-result owner.
2. Added a harness queue helper for UGC call-result payloads with explicit
   `ioFailure` and payload-presence controls.
3. Added executable coverage for raw failed results, `ioFailure`, no-payload
   failure, and no-payload non-IO failure projections.
4. Pinned call-handle preservation and zeroed no-payload event projection.
5. Added static dispatcher assertions for the mapped call-result fields and
   failure branches.

### Task A270: Close botlib structure-tail and cgame boundary mapping [COMPLETED]
Priority: High
Primary areas: `src/code/botlib/l_struct.c`, `src/code/client/cl_cgame.c`,
`src/code/client/ql_cgame_imports.inc`, `src/code/cgame/cg_syscalls.c`,
`references/analysis/quakelive_symbol_aliases.json`,
`tests/test_botlib_structure_tail_cgame_boundary_parity.py`,
`docs/reverse-engineering/botlib-structure-tail-cgame-boundary-mapping-2026-06-06.md`
Parity estimate: **before 78% -> after 98%** for focused botlib
structure-tail boundary classification, **before 72% -> after 97%** for
adjacent cgame snapshot/configstring owner naming, and overall botlib plus
related parser/import wiring **84% -> 85%**.

Completed work:

1. Rechecked `0x004AE830..0x004AF820` across HLIL, Ghidra `functions.csv`,
   botlib source, and client/cgame import wiring.
2. Promoted `0x004AF570 -> CL_GetSnapshot` and
   `0x004AF690 -> CL_ConfigstringModified`, separating true client owners from
   the existing native cgame import wrappers.
3. Confirmed `ReadStructure` remains the final promoted botlib structure-reader
   owner in this seam.
4. Classified `ReadChar`, `ReadString`, `WriteIndent`, `WriteFloat`,
   `WriteStructWithIndent`, and `WriteStructure` as source-visible but
   unpromoted in this retail address band.
5. Added a focused parity gate and mapping note for the structure-tail to
   cgame-import boundary; no C source body changes were justified.

### Task A269: Extend Steam UGC query result readback coverage [COMPLETED]
Priority: High
Primary areas: `tests/steamworks_harness.c`,
`tests/test_steamworks_harness.py`,
`docs/reverse-engineering/quakelive_steam_mapping_round_363.md`,
`docs/plans/steamworks-parity-plan.md`
Parity estimate: **before 55% -> after 94%** for focused UGC query
result/preview/release harness coverage, **before 96% -> after 98%** for
combined UGC query wrapper and call-result projection, and broader Steamworks
parity remains approximately **99%** because live backend timing, workshop
availability, and the raw filter semantic remain intentionally bounded.

Completed work:

1. Rechecked the retained `SteamUGC` query/readback HLIL slots at
   `0x00460DF3`, `0x00460E04`, `0x0045FD88`, and `0x0045FDAA`.
2. Extended the Steamworks harness with mocked `GetQueryUGCResult`,
   `GetQueryUGCPreviewURL`, and `ReleaseQueryUGCRequest` vtable slots.
3. Added mock state for published-file ID, title, description, preview URL,
   result/preview success flags, query handles, and row indexes.
4. Exported enabled and disabled harness wrappers for the retained UGC query
   readback/release surface.
5. Added ctypes coverage for success, release, failure zeroing, and disabled
   offline fallback behavior.

### Task A268: Promote botlib CRC and libvar runtime owners [COMPLETED]
Priority: High
Primary areas: `src/code/botlib/l_crc.c`, `src/code/botlib/l_libvar.c`,
`src/code/botlib/be_aas_route.c`,
`references/analysis/quakelive_symbol_aliases.json`,
`tests/test_botlib_crc_libvar_alias_closure_parity.py`,
`docs/reverse-engineering/botlib-crc-libvar-alias-closure-2026-06-06.md`
Parity estimate: **before 76% -> after 99%** for focused CRC/libvar alias
ownership, **before 88% -> after 98%** for route-cache CRC owner mapping, and
overall botlib support/runtime mapping **83% -> 84%**.

Completed work:

1. Rechecked the unpromoted `0x004A84B0..0x004A8790` support-runtime block
   immediately after `GetBotLibAPI`.
2. Promoted `CRC_ProcessString` and nine libvar runtime helpers in the retail
   symbol-alias map.
3. Captured `LibVarGet` and `LibVarDeAlloc` as source-visible readability
   helpers that retail folded into emitted callers, so they remain
   intentionally unpromoted.
4. Tied the CRC helper to AAS route-cache area and cluster CRC write/read
   wiring.
5. Added a focused regression gate and mapping note; no C source body changes
   were justified for this slice.

### Task A267: Close WebUI server-browser retained refresh parity [COMPLETED]
Priority: High
Primary areas: `src/code/client/cl_main.c`,
`tests/test_platform_services.py`, `tests/test_netcode_parity_manifest.py`,
`docs/reverse-engineering/steam-retail-server-browser-appid-interop-2026-06-06.md`
Parity estimate: **before 96% -> after 100%** for the focused WebUI
server-browser list/refresh support lane. Broader Steam server-browser parity
remains approximately **99%** because live Steam backend timing and
server-side Steam GameServer public-app publication still require opt-in
runtime validation.

Completed work:

1. Rechecked the retained WebUI `RequestServers`, `RefreshList`,
   list-response, list-failure, and refresh-complete HLIL against
   `quakelive_steam.exe`.
2. Confirmed retail `RefreshList` only refreshes the retained
   `ISteamMatchmakingServers` query handle and does not publish a new
   `servers.refresh.start` event or rearm browser active/timeout state.
3. Removed the SRP-only active-refresh gate from native list response/failure
   callbacks so retained-handle refresh rows publish like retail rows.
4. Kept native timeout protection for SRP's frame-driven initial request path
   while allowing callback-driven `RefreshComplete` to publish the retail
   `servers.refresh.end` event after retained-handle refreshes.
5. Re-audited the SRP-to-retail publication side and confirmed the existing
   Steam GameServer bootstrap/state path mirrors retail product, game-dir,
   identity, metadata, and heartbeat publication; public-retail app identity
   remains a runtime Steam context requirement because retail has no source-side
   app-id argument in `SteamGameServer_Init`.
6. Added static parity gates and mapping notes for the retained refresh
   callback semantics.

### Task A266: Extend Steam GameServer callback pump coverage [COMPLETED]
Priority: High
Primary areas: `tests/steamworks_harness.c`,
`tests/test_steamworks_harness.py`, `tests/test_platform_services.py`,
`docs/reverse-engineering/quakelive_steam_mapping_round_360.md`,
`docs/plans/steamworks-parity-plan.md`
Parity estimate: **before 63% -> after 97%** for the focused Steam
GameServer callback pump coverage lane. Steam GameServer callback registration
plus payload projection moves approximately **92% -> 98%**, while broader
Steamworks parity remains approximately **99%** because live backend connection
timing, auth policy, VAC behavior, and transport behavior remain intentionally
bounded behind opt-in online services.

Completed work:

1. Rechecked `SteamServerCallbacks_Init` (`0x00466DB0`) against the mapping
   report, promoted server callback aliases, and imported `SteamServerCallbacks`
   vtables in the Ghidra symbols corpus.
2. Confirmed the platform layer already prepares retained callback objects for
   `SteamServersConnected_t`, `SteamServerConnectFailure_t`,
   `SteamServersDisconnected_t`, `ValidateAuthTicketResponse_t`, server-side
   `P2PSessionRequest_t`, `GSStatsReceived_t`, and `GSStatsStored_t`.
3. Extended the Steamworks harness with retained targets for the four server
   callbacks that were not previously executable-test-backed.
4. Added queue helpers and ctypes coverage proving those payloads cross
   `QL_Steamworks_RunServerCallbacks`, including result, retry, and SteamID
   projection.
5. Tightened static parity coverage for all seven server callback IDs, object
   preparations, object registrations, and unregister calls.

### Task A265: Reconstruct Freeze Tag thaw respawn tail [COMPLETED]
Priority: High
Primary areas: `src/code/game/g_freeze.c`, `src/code/game/g_combat.c`,
`src/code/game/g_local.h`, `tests/test_game_active_pmove_wiring_parity.py`,
`tests/test_cgame_event_transport_parity.py`,
`docs/reverse-engineering/freeze-tag-thaw-respawn-tail-mapping-2026-06-06.md`
Parity estimate: **before 38% -> after 88%** for the focused Freeze
`EV_THAW_PLAYER` / `PM_NORMAL` / `ClientSpawn` respawn tail. The broader
Freeze thaw-completion event lane moves approximately **86% -> 93%**, while
broader Freeze Tag gametype wiring moves approximately **94% -> 95%**.

Completed work:

1. Rechecked `FUN_1004CD40` / `G_FreezeClientEndFrame` and confirmed assisted
   thaw falls into `FUN_10046d80` after helper reward, obituary, and team-sound
   publication.
2. Rechecked `FUN_1004C1B0` / `Freeze_RoundStateTransition` and pinned the
   independent winning-team thaw sequence: `EV_THAW_PLAYER`, `PM_NORMAL`, then
   `ClientSpawn`.
3. Reconstructed the Freeze marker branch in `GibEntity`: the normal
   `EV_GIB_PLAYER` event remains first, then marked frozen clients emit
   `EV_THAW_PLAYER`, restore `PM_NORMAL`, and rerun `ClientSpawn`.
4. Split helper assist credit into `G_FreezeAwardThawAssist` so score, assist
   medal, and centerprint side effects survive before the thawed client state
   is rebuilt through `ClientSpawn`.
5. Added focused parity tests and mapping notes for the retail thaw respawn
   tail, while retaining the old direct thaw visual only as a stale-marker
   fallback.

### Task A264: Close botlib residual address and native import wiring audit [COMPLETED]
Priority: High
Primary areas: `references/analysis/quakelive_symbol_aliases.json`,
`references/reverse-engineering/ghidra/quakelive_steam/functions.csv`,
`src/code/botlib/be_interface.c`, `src/code/game/g_syscalls.c`,
`src/code/server/sv_game.c`, `src/code/server/ql_game_imports.inc`,
`tests/test_botlib_residual_gap_and_wiring_parity.py`,
`docs/reverse-engineering/botlib-residual-gap-and-wiring-audit-2026-06-06.md`
Parity estimate: **before 70% -> after 98%** for focused residual botlib
address classification and **before 90% -> after 98%** for native botlib
import bridge closure. Overall botlib plus related wiring moves approximately
**82% -> 83%** because this round locks down classification and bridge
consistency without changing source behavior.

Completed work:

1. Recomputed the `0x00482000..0x004A8400` botlib-neighborhood function scan
   against the nested `quakelive_steam` symbol alias map.
2. Captured the exact residual set as fifteen pre-`AAS_Trace` libjpeg
   memory-manager false-lead rows plus the compiler-folded
   `sub_486F40` weapon-jump thunk.
3. Added a regression gate proving the neighborhood has `417` Ghidra rows,
   `401` row-backed promoted aliases, `407` promoted aliases in the band
   overall, and only the documented residual addresses left.
4. Added a bridge-wide native import check proving all `134`
   `G_QL_IMPORT_BOTLIB_*` slots are registered and backed by generated/local
   `QL_G_trap_*` wrappers, with the three intentional direct-native slots
   called out explicitly.
5. Documented why no new source reconstruction or alias promotion is justified
   for this residual pass.

### Task A263: Extend main Steam client callback pump coverage [COMPLETED]
Priority: High
Primary areas: `tests/steamworks_harness.c`,
`tests/test_steamworks_harness.py`, `tests/test_platform_services.py`,
`docs/reverse-engineering/quakelive_steam_mapping_round_359.md`,
`docs/plans/steamworks-parity-plan.md`
Parity estimate: **before 62% -> after 97%** for the focused main client
callback pump coverage lane. Steam client callback registration plus payload
projection moves approximately **91% -> 98%**, while broader Steamworks parity
remains approximately **99%** because live Steam backend timing, stats
validity, presence cadence, and P2P networking behavior remain intentionally
bounded behind opt-in online services.

Completed work:

1. Rechecked `SteamCallbacks_Init` (`0x004613A0`) against the mapping report,
   promoted callback handler aliases, and imported `SteamCallbacks`
   callback/call-result vtables in the Ghidra symbols corpus.
2. Confirmed the platform layer already prepares the retained client callback
   objects for rich presence, user stats, persona state, client P2P session,
   game-server change, friend rich presence, and UGC query completion.
3. Extended the Steamworks harness with retained callback targets for the five
   normal client callbacks that were not previously executable-test-backed.
4. Added queue helpers and ctypes coverage proving those payloads cross
   `QL_Steamworks_RunCallbacks`, including friend-summary enrichment and
   server/password string projection.
5. Tightened static parity coverage for all client callback IDs, normal
   callback registrations, and the UGC call-result preparation.

### Task A262: Restore public retail Steam server-browser AppID interop [COMPLETED]
Priority: High
Primary areas: `src/common/platform/platform_steamworks.c`,
`src/common/platform/platform_steamworks.h`, `src/code/client/cl_main.c`,
`src/code/client/cl_cgame.c`, `tests/steamworks_harness.c`,
`tests/test_steamworks_harness.py`,
`docs/reverse-engineering/steam-retail-server-browser-appid-interop-2026-06-06.md`
Parity estimate: **before 72% -> after 96%** for the focused public-retail
Steam server-browser AppID interop lane. Broader WebUI server-browser parity
remains approximately **99%** because live Steam backend timing and server-side
Steam GameServer app-context publication still require opt-in runtime
validation.

Completed work:

1. Traced the empty WebUI list to the native Steam browser path filtering list
   requests and returned rows by the running Steam app id while the legacy
   Quake III master fallback is policy-disabled.
2. Added explicit `ForApp` Steam browser and favorite helpers so the recovered
   current-app wrappers remain intact while the WebUI browser can target public
   retail Quake Live discovery.
3. Added `cl_steamServerBrowserAppId`, defaulting to public retail app id
   `282440`, and stored the selected app id on native list/detail state for
   callback-time validation.
4. Routed WebUI favorite add/remove through the same discovery app id used by
   Favorites/History list requests.
5. Added executable harness coverage and source-parity assertions for
   current-app behavior, public-retail request app id, public-retail row
   validation, ping/detail projection, and favorites.

### Task A261: Map botlib edge math and grapple helper owners [COMPLETED]
Priority: High
Primary areas: `src/code/botlib/be_aas_reach.c`,
`src/code/botlib/be_aas_move.c`, `src/code/botlib/be_ai_move.c`,
`references/analysis/quakelive_symbol_aliases.json`,
`tests/test_botlib_move_edge_grapple_helper_parity.py`,
`docs/reverse-engineering/botlib-move-edge-grapple-helper-mapping-2026-06-06.md`
Parity estimate: **before 70% -> after 97%** for focused AAS edge helper
mapping and **before 78% -> after 97%** for focused move-AI angle/grapple
helper mapping. Overall botlib plus movement/reachability helper wiring moves
approximately **81% -> 82%** because this pass closes static helper ownership
without changing live-map movement behavior.

Completed work:

1. Rechecked the remaining real botlib-neighborhood gaps after the route
   prelude pass and separated them from the known libjpeg false lead.
2. Promoted `VectorDistance`, `VectorBetweenVectors`, `AngleDiff`,
   `GrappleState`, and `BotResetGrapple` from HLIL/Ghidra evidence.
3. Pinned their source consumers in `AAS_ClosestEdgePoints`,
   `BotTravel_Grapple`, rocket/BFG jump travel, and `BotMoveToGoal`.
4. Preserved `sub_486F40` as an explicit non-promotion because retail folds the
   identical rocket/BFG `AAS_WeaponJumpZVelocity(origin, 120)` wrappers into a
   single thunk.

### Task A260: Reconstruct Freeze Tag assisted-thaw obituary and team sound [COMPLETED]
Priority: High
Primary areas: `src/code/game/g_freeze.c`, `src/code/cgame/cg_event.c`,
`tests/test_game_active_pmove_wiring_parity.py`,
`tests/test_cgame_event_transport_parity.py`,
`docs/reverse-engineering/freeze-tag-thaw-obituary-sound-mapping-2026-06-06.md`,
`docs/reverse-engineering/freeze-tag-mapping-2026-06-06.md`,
`docs/reverse-engineering/qagame-mapping.md`,
`docs/reverse-engineering/cgame-mapping.md`
Parity estimate: **before 45% -> after 91%** for the focused assisted-thaw
obituary/global-team-sound corridor. The broader Freeze thaw-completion event
lane moves approximately **72% -> 86%**, while broader Freeze Tag gametype
wiring moves approximately **93% -> 94%** because the deeper retail
`GibEntity`/`ClientSpawn` thaw visual tail remains a separate source
reconstruction target.

Completed work:

1. Rechecked `FUN_1004CD40` in the committed qagame Ghidra/HLIL corpus and
   confirmed assisted thaw emits `EV_OBITUARY` with `MOD_THAW`, thawed client,
   helper client, and `SVF_BROADCAST` immediately after assist credit.
2. Mapped the following `EV_GLOBAL_TEAM_SOUND` payload to the existing
   `G_BroadcastGlobalTeamSound` bridge, using `GTS_RED_RETURN` for blue-team
   clients and `GTS_BLUE_RETURN` otherwise.
3. Added `G_FreezeEmitThawCompletionEvents` and routed non-auto thaw completion
   through it before the existing direct `EV_THAW_PLAYER` visual handoff.
4. Rechecked cgame `CG_Obituary` strings in the committed cgame HLIL and symbol
   map, then restored `MOD_THAW` text for world auto-thaw, local helper thaw,
   and remote helper thaw.
5. Added static parity coverage and a dedicated mapping note that records the
   reconstructed assisted-thaw layer and leaves the retail `GibEntity` respawn
   tail as the next explicit gap.

### Task A259: Map AAS route prelude helpers [COMPLETED]
Priority: High
Primary areas: `src/code/botlib/be_aas_route.c`,
`src/code/botlib/be_aas_route.h`, `src/code/botlib/be_aas_main.c`,
`src/code/botlib/be_ai_move.c`,
`references/analysis/quakelive_symbol_aliases.json`,
`tests/test_botlib_route_prelude_parity.py`,
`docs/reverse-engineering/botlib-route-prelude-mapping-2026-06-06.md`
Parity estimate: **before 55% -> after 96%** for focused AAS route-prelude
helper mapping. Route-cache invalidation and travel-flag wiring moves
approximately **72% -> 97%**, while overall botlib plus related AAS route/import
wiring moves approximately **80% -> 81%** because later route runtime and
alternative-route work was already mapped in the prior tranche.

Completed work:

1. Rechecked the retail `quakelive_steam.exe` HLIL range
   `0x004925F0..0x00492F20` and separated actual AAS route helpers from the
   adjacent libjpeg memory-manager false lead at `0x00482150..0x004829A0`.
2. Promoted eleven missing route-prelude aliases for routing debug info,
   cluster-local area numbering, travel-flag table initialization/access,
   routing-cache invalidation, area-content flag table access, reversed
   reachability creation, area travel time, and portal max travel-time
   initialization.
3. Documented which source helpers remain unpromoted because retail inlines or
   fuses them into larger route-cache functions.
4. Added focused parity coverage tying aliases to Ghidra rows, HLIL anchors,
   debug strings, source structures, AAS init order, and move-AI consumers.

### Task A258: Extend Steam lobby callback pump coverage [COMPLETED]
Priority: High
Primary areas: `tests/steamworks_harness.c`,
`tests/test_steamworks_harness.py`, `tests/test_platform_services.py`,
`docs/reverse-engineering/quakelive_steam_mapping_round_358.md`,
`docs/plans/steamworks-parity-plan.md`
Parity estimate: **before 58% -> after 96%** for the focused lobby callback
pump coverage lane. Steam lobby callback registration plus payload projection
moves approximately **90% -> 98%**, while broader Steamworks parity remains
approximately **99%** because live Steam backend timing and browser event
ordering remain intentionally bounded behind opt-in online services.

Completed work:

1. Rechecked the retail `SteamLobbyCallbacks_Init` HLIL constructor at
   `0x004656A0`, the Ghidra imported `SteamLobbyCallbacks` callback vtables,
   and the mapping report row for the eight lobby callback payload types.
2. Confirmed the platform layer already prepares and registers callback
   objects for `LobbyCreated_t`, `LobbyEnter_t`, `LobbyChatUpdate_t`,
   `LobbyChatMsg_t`, `LobbyDataUpdate_t`, `LobbyGameCreated_t`,
   `LobbyKicked_t`, and `GameLobbyJoinRequested_t`.
3. Extended the Steamworks harness with retained callback targets and raw queue
   helpers for the seven lobby callback payloads that were not previously
   executable-test-backed.
4. Expanded ctypes callback-pump coverage so all eight lobby payloads cross
   `QL_Steamworks_RunCallbacks`, including the chat-message body retrieval
   through the mocked `GetLobbyChatEntry` slot.
5. Tightened static parity coverage for all eight callback IDs, object
   preparations, and object registrations.

### Task A257: Reconstruct Freeze Tag frozen powerup marker producer [COMPLETED]
Priority: High
Primary areas: `src/code/game/g_freeze.c`,
`src/code/cgame/cg_players.c`, `src/code/cgame/cg_draw.c`,
`tests/test_game_active_pmove_wiring_parity.py`,
`docs/reverse-engineering/freeze-tag-frozen-marker-mapping-2026-06-06.md`,
`docs/reverse-engineering/freeze-tag-mapping-2026-06-06.md`,
`docs/reverse-engineering/qagame-mapping.md`
Parity estimate: **before 35% -> after 94%** for the focused qagame
frozen-marker producer lane. The combined Freeze Tag qagame/cgame
presentation bridge moves approximately **88% -> 94%**, while broader Freeze
Tag gametype wiring moves approximately **92% -> 93%** because the larger
`FUN_1004BC80` thaw obituary/team-sound/GibEntity split remains open.

Completed work:

1. Rechecked the retail qagame death/freeze path against committed Ghidra and
   confirmed `client + 0x17c = 0x7fffffff` plus `gentity + 0xc4 = 0x8000`
   when Freeze Tag records a frozen player.
2. Cross-checked `FUN_1004BC80` HLIL and confirmed the `arg2 == 1`
   thaw/respawn branch clears the same client marker and entitystate bit.
3. Added `G_FreezeSetClientFrozenPowerupMarker` so qagame now publishes
   `ps.powerups[PW_NUM_POWERUPS] = INT_MAX` and
   `ent->s.powerups = ( 1 << PW_NUM_POWERUPS )` on freeze entry, and clears
   both surfaces during init/thaw.
4. Anchored the bridge against existing cgame consumers in `CG_IsFrozenPlayer`,
   `CG_PlayerSprites`, and the team overlay frozen bit.
5. Added a dedicated mapping note and static parity coverage for the retail
   offsets, source helper, and remaining thaw-event reconstruction gap.

### Task A256: Map botlib chat private helper owners [COMPLETED]
Priority: Medium
Primary areas: `src/code/botlib/be_ai_chat.c`,
`src/code/botlib/be_interface.c`, `src/code/game/botlib.h`,
`references/analysis/quakelive_symbol_aliases.json`,
`tests/test_botlib_chat_private_helper_parity.py`,
`docs/reverse-engineering/botlib-chat-private-helper-mapping-2026-06-06.md`
Parity estimate: **before 82% -> after 96%** for the focused chat
private-helper corridor and **before 90% -> after 91%** for overall botlib
chat mapping plus public chat export/import wiring. Remaining uncertainty is
live chat-data behavior across retail `syn.c`, `rnd.c`, `match.c`, `rchat.c`,
and per-bot initial chat files rather than private helper ownership.

Completed work:

1. Rechecked the `be_ai_chat.c` private-helper band against committed
   `quakelive_steam.exe` HLIL and Ghidra function rows.
2. Promoted `InitConsoleMessageHeap`, `BotRemoveTildes`,
   `BotReplaceWeightedSynonyms`, `BotReplaceReplySynonyms`, and
   `StringsMatch`.
3. Preserved source bodies unchanged; the current reconstruction already
   matches the retail static shape for heap setup, tilde scrubbing, synonym
   replacement, and match-piece variable capture.
4. Documented why `BotChatStateFromHandle`, `AllocConsoleMessage`,
   `FreeConsoleMessage`, and `StringReplaceWords` remain source-visible but
   unpromoted: the observed retail rows fold those operations into callers or
   do not expose standalone owners.
5. Added focused parity coverage for aliases, Ghidra sizes, HLIL helper call
   sites, source helper bodies, setup/shutdown/matching/expansion wiring, and
   the private/public AI export boundary.

### Task A255: Normalize Steam GameServer and P2P vtable ABI wrappers [COMPLETED]
Priority: High
Primary areas: `src/common/platform/platform_steamworks.c`,
`tests/steamworks_harness.c`, `tests/test_platform_services.py`,
`docs/reverse-engineering/quakelive_steam_mapping_round_356.md`,
`docs/plans/steamworks-parity-plan.md`
Parity estimate: **before 70% -> after 96%** for the focused
GameServer/P2P vtable ABI wrapper family. The combined Steam GameServer
metadata, identity, packet bridge, and legacy P2P wrapper surfaces move
approximately **95% -> 98%**, while broader Steamworks parity remains
approximately **99%** because live backend validation remains intentionally
bounded behind opt-in online services.

Completed work:

1. Rechecked the committed HLIL around `0x00465A40`, `0x00465A60`,
   `0x00465B00`, `0x00465B70`, and `0x00465D50` and confirmed the affected
   lanes are Steam C++ interface vtable dispatches.
2. Added `QL_STEAMWORKS_FASTCALL` and converted the retained
   `ISteamNetworking`, `ISteamGameServer`, and `ISteamGameServerNetworking`
   typedefs to the same `self, unused, ...` ABI shape used elsewhere in the
   Steam wrapper layer.
3. Updated GameServer metadata, identity, logged-on, public-IP,
   incoming/outgoing packet, and legacy P2P call sites to pass the explicit
   unused second argument before mapped retail parameters.
4. Updated Steamworks harness vtable mocks to the corrected ABI shape so
   argument ordering remains executable-test-backed.
5. Tightened static parity assertions for the ABI macro, representative
   typedefs, and mapped call sites.

### Task A254: Map botlib goal item heap and avoid-goal wiring [COMPLETED]
Priority: Medium
Primary areas: `src/code/botlib/be_ai_goal.c`,
`src/code/botlib/be_interface.c`, `src/code/game/botlib.h`,
`src/code/game/g_local.h`, `src/code/game/g_public.h`,
`src/code/game/g_syscalls.c`, `src/code/game/ai_dmq3.c`,
`src/code/server/sv_game.c`, `src/code/server/ql_game_imports.inc`,
`references/analysis/quakelive_symbol_aliases.json`,
`tests/test_botlib_goal_item_parity.py`,
`docs/reverse-engineering/botlib-goal-item-mapping-2026-06-06.md`
Parity estimate: **before 79% -> after 95%** for the focused goal item
heap/info-entity/avoid-selection corridor. Overall botlib plus goal item
export/import wiring moves approximately **88% -> 89%** because this pass
closes static ownership and routing gaps without claiming live map-specific
AAS item behavior, dynamic dropped-item behavior, or tactical item-selection
quality.

Completed work:

1. Rechecked the retail `be_ai_goal.c` item config, fuzzy-weight index,
   level-item heap, info-entity, avoid-goal, dynamic entity-item update, and
   LTG/NBG selection band against the committed HLIL and Ghidra function rows.
2. Promoted the missing private-owner aliases `ItemWeightIndex`,
   `InitLevelItemHeap`, `BotFreeInfoEntities`, and `BotAddToAvoidGoals`.
3. Confirmed no C source rewrite is currently justified; small source-visible
   level-item helpers remain unaliased because the evidence supports them as
   inlined operations inside larger retail owners.
4. Added focused parity coverage for the source shape, botlib export block,
   qagame legacy/native syscall bridge, server VM dispatch, direct native
   import wrappers, and qagame level-item/camp-spot consumers.
5. Added a dedicated mapping note for the goal-item heap and avoid-goal
   wiring tranche.

### Task A253: Reconstruct Steam GameServer P2P active-client gate [COMPLETED]
Priority: High
Primary areas: `src/code/server/sv_client.c`, `tests/test_platform_services.py`,
`docs/reverse-engineering/quakelive_steam_mapping_round_355.md`,
`docs/plans/steamworks-parity-plan.md`,
`docs/reverse-engineering/quakelive_steam_mapping_round_01.md`,
`docs/mapping-ref/quakelive_steam_mapping_report.md`
Parity estimate: **before 72% -> after 96%** for the focused server-side
`P2PSessionRequest_t` admission gate. The broader Steam GameServer callback
bundle moves approximately **98% -> 99%**, while broader Steamworks parity
remains approximately **99%** because live backend callback cadence and NAT
behavior stay intentionally bounded behind opt-in online services.

Completed work:

1. Rechecked retail `SteamServerCallbacks_OnP2PSessionRequest`
   (`0x00465B70`) in the committed HLIL and confirmed the callback scans
   client slots for `*client == 4`, matching `CS_ACTIVE`, plus a two-word
   SteamID match before dispatching `SteamGameServerNetworking` slot `0x0c`.
2. Added `SV_FindActiveClientBySteamId` beside the broader SteamID finder so
   auth-ticket responses can still locate pre-active clients while P2P session
   admission mirrors the retail active-slot gate.
3. Updated `SV_SteamServerP2PSessionRequestCallback` to remove the extra
   `platformAuthSucceeded` condition, reject missing active SteamID matches,
   log accepted matches, and then call the retained server P2P accept wrapper.
4. Tightened static parity coverage for the active-client finder, callback
   dispatch, removed auth-success gate, accepted diagnostic, and missing-player
   rejection path.
5. Corrected stale Steamworks mapping language that described the callback as
   authenticated-client gated rather than active-client gated.

### Task A252: Reconstruct Freeze Tag thaw-progress eFlag buckets [COMPLETED]
Priority: High
Primary areas: `src/code/game/g_client.c`, `src/code/game/g_freeze.c`,
`tests/test_game_active_pmove_wiring_parity.py`,
`docs/reverse-engineering/freeze-tag-thaw-progress-eflags-mapping-2026-06-06.md`,
`docs/reverse-engineering/freeze-tag-mapping-2026-06-06.md`,
`docs/reverse-engineering/qagame-mapping.md`, `docs/gameplay/cvars.md`
Parity estimate: **before 40% -> after 92%** for the focused Freeze
thaw-progress low-bit producer lane. The broader Freeze thaw/end-frame lane
moves approximately **94% -> 96%**, while broader Freeze Tag gametype wiring
moves approximately **91% -> 92%** because this pass closes a static
producer-side bucket mismatch without claiming live client visual validation.

Completed work:

1. Rechecked `FUN_1004CD40` / `G_FreezeClientEndFrame` in the committed Ghidra
   corpus and pinned the top-of-function comparisons against
   `DAT_105a472c / 3` and `(DAT_105a472c / 3) * 2`.
2. Mapped the retail `gclient + 0x1c0` bit writes to the shared
   `EF_DEAD` (`0x1`) and `EF_TICKING` (`0x2`) constants, preserving the retail
   clear-high-bucket and OR-only middle/final bucket behavior.
3. Reconstructed `G_FreezeUpdateThawProgressFlags` and called it at the top of
   `G_FreezeClientEndFrame`, before helper lookup and remaining-time mutation,
   matching the recovered retail ordering.
4. Cleared the reused low Freeze progress bits on freeze entry and thaw exit so
   stale progress state does not leak across reconstructed source transitions.
5. Added static parity coverage and mapping notes for the Ghidra anchors,
   source bucket helper, transition cleanup, and related `EV_THAW_TICK`
   producer wiring.

### Task A251: Map botlib character cache and characteristic export wiring [COMPLETED]
Priority: Medium
Primary areas: `src/code/botlib/be_ai_char.c`,
`src/code/botlib/be_interface.c`, `src/code/game/be_ai_char.h`,
`src/code/game/botlib.h`, `src/code/game/g_local.h`,
`src/code/game/g_public.h`, `src/code/game/g_syscalls.c`,
`src/code/server/sv_game.c`, `src/code/server/ql_game_imports.inc`,
`references/analysis/quakelive_symbol_aliases.json`,
`tests/test_botlib_character_cache_parity.py`,
`docs/reverse-engineering/botlib-character-cache-mapping-2026-06-06.md`
Parity estimate: **before 80% -> after 96%** for the focused
character cache/default/interpolation/accessor helper corridor and
**before 87% -> after 88%** for overall botlib plus related character
export/import wiring. Remaining uncertainty is live bot-character data behavior
across maps and character files, not the static helper ownership or API routing
covered here.

Completed work:

1. Rechecked `quakelive_steam.exe` HLIL and Ghidra rows for the
   `be_ai_char.c` helper band from `BotDumpCharacter` through
   `BotShutdownCharacters`.
2. Promoted missing private helper aliases for character dumping, string
   cleanup, unconditional cleanup, default merge, cache lookup, interpolation,
   and characteristic index validation.
3. Verified that no C source rewrite is currently justified; the existing
   source already preserves the retail cache fallback ladder, default-character
   merge, float-only interpolation, characteristic conversion/clamping, and
   parser/runtime index-check split.
4. Added `tests/test_botlib_character_cache_parity.py` to pin aliases, Ghidra
   sizes, HLIL anchors, source shape, botlib export order, legacy syscall
   dispatch, native qagame import wrappers, and bot AI consumer wiring.
5. Added a focused mapping note documenting observed evidence, inferred helper
   names, confidence, and residual live-data risk.

### Task A250: Recheck demo record/playback and browser demo-list wiring [COMPLETED]
Priority: Medium
Primary areas: `src/code/client/cl_main.c`, `src/code/client/cl_cgame.c`,
`src/code/client/cl_keys.c`, `src/code/cgame/cg_draw.c`,
`src/code/cgame/cg_view.c`,
`tests/test_demo_record_playback_mapping_parity.py`,
`docs/reverse-engineering/demo-record-playback-mapping-2026-06-06.md`
Parity estimate: **before 96% -> after 99%** for the focused protocol-91 demo
recording/playback, browser `GetDemoList`, console completion, and cgame demo
HUD/control wiring surface. Remaining uncertainty is live `.dm_91` replay
freshness across third-party captures, not a known static source mismatch.

Completed work:

1. Rechecked the `quakelive_steam.exe` HLIL and Ghidra rows for
   `CL_WriteDemoMessage`, `CL_StopRecord_f`, `CL_DemoFilename`, `CL_Record_f`,
   `CL_WalkDemoExt`, `CL_NextDemo`, `CL_DemoCompleted`,
   `CL_ReadDemoMessage`, and `CL_PlayDemo_f`.
2. Verified that the core packet envelope and playback reader already match
   retail: little-endian server sequence and payload length, post-header
   payload writes, `MAX_MSGLEN` rejection, truncation handling, protocol-list
   fallback, and the `-1/-1` terminator.
3. Reconstructed the browser-facing demo-list return shape by preserving raw
   `.dm_91` file-list entries from `CL_WebHost_BuildDemoListJson` instead of
   stripping the protocol suffix before returning the JSON array.
4. Added static parity coverage that pins the retail aliases, HLIL anchors,
   protocol-91 extension path, browser `dm_91` listing, retained console
   `.dm_73` completion quirk, cgame `demoPlayback` draw handoff, demo HUD
   controls, and the new mapping note.

### Task A249: Reconstruct Freeze Tag helper entity-query topology [COMPLETED]
Priority: High
Primary areas: `src/code/game/g_freeze.c`,
`tests/test_game_active_pmove_wiring_parity.py`,
`tests/test_game_round_controller_helper_parity.py`,
`tests/test_game_helper_seam_parity.py`,
`docs/reverse-engineering/freeze-tag-helper-query-mapping-2026-06-06.md`,
`docs/reverse-engineering/freeze-tag-mapping-2026-06-06.md`,
`docs/reverse-engineering/qagame-mapping.md`, `docs/gameplay/cvars.md`
Parity estimate: **before 72% -> after 94%** for the focused Freeze
thaw-helper search topology. The broader Freeze thaw/end-frame lane moves
approximately **91% -> 94%**, while broader Freeze Tag gametype wiring moves
approximately **90% -> 91%** because this pass closes helper enumeration
topology without claiming live match validation.

Completed work:

1. Rechecked `FUN_1004CD40` / `G_FreezeClientEndFrame` in Ghidra and HLIL,
   including the thaw-radius mins/maxs build and qagame import call at
   `DAT_104b13ac + 0xa4`.
2. Identified the import as the recovered `trap_EntitiesInBox` /
   `QL_G_trap_EntitiesInBox` bridge with a `0x400` entity-list limit.
3. Reconstructed `G_FreezeCountThawHelpers` to enumerate the thaw-radius AABB
   through `trap_EntitiesInBox` before applying the shared thaw-helper
   predicate, replacing the previous source-only flat `level.maxclients` scan.
4. Kept the public count-returning helper API stable while selecting the first
   valid entity-list helper, matching retail's per-frame helper choice more
   closely than the previous nearest-client selection.
5. Updated Freeze mapping notes, gameplay cvar notes, and static parity tests
   to pin the retail entity-query topology.

### Task A248: Map botlib genetic-selection wiring [COMPLETED]
Priority: Medium
Primary areas: `src/code/botlib/be_ai_gen.c`,
`src/code/botlib/be_interface.c`, `src/code/game/be_ai_gen.h`,
`src/code/game/botlib.h`, `src/code/game/ai_main.c`,
`src/code/game/g_local.h`, `src/code/game/g_public.h`,
`src/code/game/g_syscalls.c`, `src/code/server/sv_game.c`,
`src/code/server/ql_game_imports.inc`,
`references/analysis/quakelive_symbol_aliases.json`,
`tests/test_botlib_genetic_selection_parity.py`,
`docs/reverse-engineering/botlib-genetic-selection-mapping-2026-06-06.md`
Parity estimate: **before 72% -> after 96%** for the focused
genetic-selection helper/export corridor and **before 86% -> after 87%** for
overall botlib plus fuzzy/genetic interbreed wiring. Remaining uncertainty is
live interbreed behavior quality and map/bot-data effects rather than the
static selector ownership or import/export routing covered here.

Completed work:

1. Rechecked `quakelive_steam.exe` HLIL and Ghidra function rows for the
   `be_ai_gen.c` helper pair around `GeneticSelection` and
   `GeneticParentsAndChildSelection`.
2. Promoted the missing `sub_49C6C0 -> GeneticSelection` alias and rechecked
   the existing `sub_49C810 -> GeneticParentsAndChildSelection` export owner.
3. Verified no C body change is currently justified; the checked-in genetic
   selector source already matches the retail static shape for weighted
   selection, fallback selection, parent exclusion, rank reversal, child
   selection, and failure-output zeroing.
4. Added `tests/test_botlib_genetic_selection_parity.py` to pin aliases,
   Ghidra sizes, HLIL anchors, source shape, AI export order, qagame consumer
   behavior, legacy syscall dispatch, server VM dispatch, and Quake Live native
   import wrapper wiring.

### Task A247: Reconstruct Steam GameServerStats logged-on request gate [COMPLETED]
Priority: Medium
Primary areas: `src/common/platform/platform_steamworks.c`,
`src/common/platform/platform_steamworks.h`, `tests/steamworks_harness.c`,
`tests/test_steamworks_harness.py`, `tests/test_platform_services.py`,
`docs/plans/steamworks-parity-plan.md`,
`docs/reverse-engineering/quakelive_steam_mapping_round_354.md`
Parity estimate: **before 40% -> after 94%** for the focused
GameServerStats logged-on request gate, **before 97% -> after 98%** for the
combined `idSteamStats` callback/value/descriptor/request-bootstrap lane, and
approximately **99%** for broader Steamworks parity. Remaining uncertainty is
live backend timing and callback cadence, which stay intentionally bounded
behind `QL_BUILD_ONLINE_SERVICES` / `QL_BUILD_STEAMWORKS` opt-in behavior.

Completed work:

1. Rechecked the retail `quakelive_steam.exe` HLIL for
   `SteamStats_OnServersConnected` (`0x00467190`) and the repeated
   constructor/bootstrap gate at `0x004679d9`.
2. Reconstructed `QL_Steamworks_ServerIsLoggedOn` through the observed
   `SteamGameServer` vtable slot `0x20`, with the disabled-build stub returning
   `qfalse`.
3. Gated `QL_Steamworks_ServerRequestUserStats` behind the logged-on check
   before issuing `SteamGameServerStats::RequestUserStats` through slot `0x00`.
4. Extended the Steamworks harness with a mocked `SteamGameServer::BLoggedOn`
   slot, result control, call counting, and enabled/disabled exports.
5. Added regression coverage proving the logged-off path suppresses the
   `SteamGameServerStats` request while the logged-on path reaches the retail
   request slot.

### Task A246: Map botlib AAS lifecycle wiring [COMPLETED]
Priority: Medium
Primary areas: `src/code/botlib/be_aas_bspq3.c`,
`src/code/botlib/be_aas_cluster.c`, `src/code/botlib/be_aas_entity.c`,
`src/code/botlib/be_aas_file.c`, `src/code/botlib/be_aas_main.c`,
`src/code/botlib/be_interface.c`, `src/code/game/botlib.h`,
`src/code/game/g_syscalls.c`, `src/code/server/sv_game.c`,
`src/code/server/ql_game_imports.inc`,
`references/analysis/quakelive_symbol_aliases.json`,
`tests/test_botlib_aas_lifecycle_parity.py`,
`docs/reverse-engineering/botlib-aas-lifecycle-mapping-2026-06-06.md`
Parity estimate: **before 78% -> after 94%** for the focused AAS
BSP/file/entity lifecycle corridor and **before 85% -> after 86%** for overall
botlib plus AAS lifecycle/import wiring. Remaining uncertainty is live-map
`.aas` content, map-dependent clustering/reachability quality, and runtime bot
behavior rather than the static lifecycle ownership or public wiring covered
here.

Completed work:

1. Rechecked `quakelive_steam.exe` HLIL and Ghidra function rows for the AAS
   BSP wrapper, BSP entity parser, cluster initialization, entity query, AAS
   file/lump, and main setup/start-frame/load-map/shutdown bands.
2. Promoted missing aliases for `AAS_Trace`, `AAS_EntityCollision`,
   `AAS_inPVS`, `AAS_BSPModelMinsMaxsOrigin`, `AAS_FreeBSPEntities`,
   `AAS_EntityModelindex`, `AAS_EntityType`, `AAS_EntityModelNum`,
   `AAS_OriginOfMoverWithModelNum`, `AAS_NextEntity`, `AAS_SwapAASData`,
   `AAS_LoadAASLump`, and `AAS_WriteAASLump`.
3. Verified no C body change is currently justified; the checked-in AAS
   lifecycle source already matches the retail static shape for the mapped
   owners.
4. Added `tests/test_botlib_aas_lifecycle_parity.py` to pin aliases, Ghidra
   sizes, HLIL anchors, lifecycle source shape, BSP/AAS export order, server VM
   syscall dispatch, Quake Live native import slab entries, and qagame syscall
   wrappers.

### Task A245: Reconstruct Grappling Hook impact media and consolidate hook wiring [COMPLETED]
Priority: Medium
Primary areas: `src/code/cgame/cg_local.h`,
`src/code/cgame/cg_main.c`, `src/code/cgame/cg_weapons.c`,
`references/analysis/quakelive_symbol_aliases.json`,
`references/symbol-maps/cgame.json`,
`tests/test_grappling_hook_mapping_parity.py`,
`docs/reverse-engineering/grappling-hook-wiring-mapping-2026-06-06.md`
Parity estimate: **before 93% -> after 98%** for the focused Grappling Hook
wiring and cgame-impact lane. Broader repo-wide parity remains approximately
**99%**; the remaining grapple uncertainty is the qagame hook temp-event
weapon-field question and any untested live-map bot grapple path quality.

Completed work:

1. Rechecked `quakelive_steam.exe`, `qagamex86.dll`, and `cgamex86.dll`
   Ghidra/HLIL evidence for bot grapple reachability/travel, qagame hook
   projectile lifecycle, shared grapple pmove pull, cgame hook rendering, and
   cgame impact media.
2. Reconstructed the missing cgame grapple-impact media branch: registered the
   retail `gfx/damage/cracked_mrk` shader and `sound/weapons/grapple/grhit.ogg`
   sound, then routed `CG_MissileHitWall` `WP_GRAPPLING_HOOK` impacts through
   that sound, cracked mark, and the retail 16-unit mark radius.
3. Promoted qagame hook lifecycle aliases for `fire_grapple`,
   `G_MissileImpact`, `Weapon_GrapplingHook_Fire`, `Weapon_HookFree`,
   `Weapon_HookThink`, `FireWeapon`, and `TeleportPlayer`, while retaining the
   existing cgame and botlib hook aliases.
4. Added a focused mapping document and regression test covering source,
   symbol-map comments, alias promotion, and Ghidra/HLIL anchors across the
   Grappling Hook corridor.

### Task A244: Reconstruct Freeze Tag thaw-helper timer and wiring [COMPLETED]
Priority: High
Primary areas: `src/code/game/g_freeze.c`, `src/code/game/g_client.c`,
`src/code/game/g_local.h`, `src/code/game/g_main.c`,
`tools/tests/match_sim/harness.py`,
`tests/test_game_active_pmove_wiring_parity.py`,
`tests/test_game_round_controller_helper_parity.py`,
`tests/test_game_runframe_parity.py`,
`docs/reverse-engineering/freeze-tag-mapping-2026-06-06.md`,
`docs/reverse-engineering/qagame-mapping.md`, `docs/gameplay/cvars.md`
Parity estimate: **before 71% -> after 91%** for the focused Freeze
thaw-helper/end-frame lane. Broader Freeze Tag gametype wiring moves
approximately **88% -> 90%** because round-state, scoreboard, last-alive, and
death wiring were already mostly reconstructed. The follow-up A249 pass closes
the exact helper entity-query topology; live retail DLL validation remains open.

Completed work:

1. Rechecked `qagamex86.dll` Ghidra and HLIL evidence for the retail Freeze
   helper band, especially `FUN_1004CD40` / `G_FreezeClientEndFrame` and the
   small retained-helper lookup at `FUN_1004CD00`.
2. Replaced the source-only accumulated thaw/tick-deadline model with the
   retail-shaped remaining-time counter and helper-active latch.
3. Reworked per-frame thaw handling to decrement by `level.msec` while a valid
   helper remains in range, refill toward `g_freezeThawTime` when abandoned,
   retain helper credit through the recovered lookup boundary, and treat
   `g_freezeThawTick` as the non-zero `EV_THAW_TICK` event gate.
4. Centralized helper validity checks for same-team connected live clients,
   `PM_NORMAL` state, radius, and line of sight, then shared that predicate
   between counting and retained-helper lookup.
5. Refreshed the lightweight match-simulation harness, cvar notes, qagame
   mapping notes, and static parity tests to pin the corrected retail
   interpretation.

### Task A243: Reconstruct CG_Missile renderer wiring [COMPLETED]
Priority: Medium
Primary areas: `src/code/cgame/cg_ents.c`,
`src/code/cgame/cg_weapons.c`, `src/code/cgame/cg_local.h`,
`tests/test_cgame_displaycontext_parity.py`,
`tests/test_game_weapon_parity.py`,
`docs/reverse-engineering/cgame-mapping.md`
Parity estimate: **before 86% -> after 96%** for the focused
`CG_Missile` renderer and related color/axis wiring. Overall cgame mapping
coverage remains **854 / 854 committed anchors (100%)**; repo-wide parity
remains approximately **98%** because this pass tightens an already mapped
renderer rather than opening new corpus coverage.

Completed work:

1. Rechecked `0x100175F0 -> CG_Missile` in cgame HLIL, the Ghidra
   `FUN_100175f0` function row, and the adjacent weapon-color helper evidence.
2. Reconstructed the retail invalid-weapon guard as `CG_Error` without mutating
   `s1->weapon`, matching the `>= 16` retail table boundary.
3. Removed the source-only `cent->lerpAngles` rewrite from `CG_Missile` and
   aligned stationary proximity-mine axis setup to `currentState.angles`.
4. Exposed the shared weapon-color override helper and routed grenade missile
   entity colors through forced team/enemy weapon color before falling back to
   `cg_weaponColor_grenade`.

### Task A242: Reconstruct Steam GameServer incoming UDP packet bridge [COMPLETED]
Priority: High
Primary areas: `src/common/platform/platform_steamworks.c`,
`src/common/platform/platform_steamworks.h`, `src/code/server/sv_main.c`,
`tests/steamworks_harness.c`, `tests/test_steamworks_harness.py`,
`tests/test_platform_services.py`,
`docs/reverse-engineering/quakelive_steam_mapping_round_353.md`,
`docs/plans/steamworks-parity-plan.md`
Parity estimate: **before 35% -> after 92%** for the focused incoming
Steam GameServer UDP handoff lane. The combined incoming/outgoing GameServer
UDP bridge moves approximately **82% -> 96%**, while broader Steamworks parity
remains approximately **99%** because live backend validation and online
service replacement remain intentionally bounded.

Completed work:

1. Rechecked `SteamServer_HandleIncomingPacket` (`0x00465d50`) in HLIL, the
   Ghidra `FUN_00465d50` row, the Round 04 alias promotion, and the adjacent
   outgoing packet drain at `SteamGameServer` slot `0x98`.
2. Added `QL_Steamworks_ServerHandleIncomingPacket` for slot `0x94`, plus the
   matching disabled inline stub.
3. Wired `SV_PacketEvent` through `SV_SteamServerHandleIncomingPacket`, packing
   IPv4 bytes in the retail order and forwarding the original packet payload
   and source port into the Steam GameServer wrapper.
4. Extended the Steamworks harness and source-bound tests to cover incoming
   packet payload capture, endpoint capture, result propagation, and disabled
   fallback behavior.

### Task A241: Map botlib AAS sample/query wiring [COMPLETED]
Priority: Medium
Primary areas: `src/code/botlib/be_aas_sample.c`,
`src/code/botlib/be_interface.c`, `src/code/game/botlib.h`,
`src/code/game/g_public.h`, `src/code/game/g_syscalls.c`,
`src/code/server/sv_game.c`, `src/code/server/ql_game_imports.inc`,
`references/analysis/quakelive_symbol_aliases.json`,
`tests/test_botlib_aas_sample_parity.py`,
`docs/reverse-engineering/botlib-aas-sample-mapping-2026-06-06.md`
Parity estimate: **before 79% -> after 95%** for the focused AAS
sample/query helper corridor and **before 84% -> after 85%** for overall
botlib plus AAS sample/import wiring. Remaining uncertainty is live-map `.aas`
content and map-dependent bot behavior, not the static sample/query ownership
or qagame-facing import surface covered here.

Completed work:

1. Rechecked `quakelive_steam.exe` HLIL and Ghidra function rows for the AAS
   sample/query band from `AAS_PresenceTypeBoundingBox` through
   `AAS_PlaneFromNum`, including link heap lifecycle, point/area presence
   queries, client bbox tracing, trace-area collection, face/plane helpers,
   entity linking, bbox area enumeration, and area info copy-out.
2. Promoted missing aliases for `AAS_AreaPresenceType`,
   `AAS_PointPresenceType`, `AAS_AreaEntityCollision`, `AAS_InsideFace`,
   `AAS_BoxOnPlaneSide2`, `AAS_UnlinkFromAreas`, `AAS_AASLinkEntity`,
   `AAS_LinkEntityClientBBox`, and `AAS_PlaneFromNum`.
3. Verified no `be_aas_sample.c` C body change is currently justified; the
   checked-in source already matches the retail static shape for the mapped
   sample/query corridor.
4. Added `tests/test_botlib_aas_sample_parity.py` to pin aliases, Ghidra
   sizes, HLIL anchors, source helper shape, public AAS export order, server VM
   syscall dispatch, legacy qagame imports, Quake Live native import slab,
   qagame direct wrappers, and qagame syscall wrappers.

### Task A240: Reconstruct Steam GameServerStats descriptor replay owner [COMPLETED]
Priority: High
Primary areas: `src/code/server/sv_client.c`,
`tests/test_platform_services.py`,
`docs/reverse-engineering/quakelive_steam_mapping_round_352.md`,
`docs/plans/steamworks-parity-plan.md`
Parity estimate: **before 54% -> after 86%** for the focused descriptor-table
replay lane. The combined `idSteamStats` callback/value/descriptor lane moves
approximately **98% -> 99%**, while broader Steamworks parity remains
approximately **99%** because online services stay opt-in and exact non-int
descriptor promotion plus live backend validation remain bounded.

Completed work:

1. Rechecked `SteamStats_FlushPendingValues` (`0x004670c0`),
   `SteamStats_OnStatsReceived` (`0x004671d0`), `data_561060`,
   `data_561c00`, the promoted symbol aliases, and the Ghidra rows for the
   retained `idSteamStats` descriptor owner.
2. Reconstructed the server stats descriptor shape: count at owner `+0x10`,
   pointer at `+0x18`, stride `0x1c`, type at descriptor `+0x04`, name at
   `+0x08`, int value at `+0x0c`, float/current value at `+0x10`, and
   average-rate count/session fields at `+0x14`/`+0x18`.
3. Converted the server stats owner from a bare name table to typed descriptor
   records and added type-aware load/flush dispatch for int, float, and
   average-rate Steam GameServerStats slots.
4. Kept all 88 currently recovered qagame-facing stat names as int descriptors
   and made the qagame `AddSteamStat` import decline non-int descriptors until
   stronger retail evidence identifies the public float/average-rate update
   owner.

### Task A239: Reconstruct botlib AAS reachability-generation support [COMPLETED]
Priority: Medium
Primary areas: `src/code/botlib/be_aas_move.c`,
`src/code/botlib/be_aas_optimize.c`, `src/code/botlib/be_aas_reach.c`,
`references/analysis/quakelive_symbol_aliases.json`,
`tests/test_botlib_reachability_generation_parity.py`,
`docs/reverse-engineering/botlib-reachability-generation-mapping-2026-06-06.md`
Parity estimate: **before 82% -> after 96%** for the focused
reachability-generation support corridor and **before 82% -> after 84%** for
overall botlib plus related movement/route wiring. Remaining uncertainty is
live-map `.aas` content and generated reachability quality, not the static
runtime helper ownership covered here.

Completed work:

1. Rechecked `quakelive_steam.exe` HLIL and Ghidra function rows for the
   reachability-generation utility band around jump velocity solving, jump
   reach run-start probing, geometry helpers, area predicates, reachability
   heap allocation, store/flattening, best-link selection, weapon-jump area
   flags, and reachability initialization.
2. Promoted missing aliases from `AAS_ClientMovementHitBBox` through
   `AAS_BestReachableLinkArea`, including `AAS_HorizontalVelocityForJump`,
   `AAS_JumpReachRunStart`, `AAS_FaceArea`, `AAS_AreaVolume`,
   `AAS_SetupReachabilityHeap`, `AAS_AllocReachability`,
   `AAS_FaceCenter`, fall/jump-distance math, liquid/damage area predicates,
   `AAS_ReachabilityExists`, and `AAS_StoreReachability`.
3. Reconstructed the retail non-`BSPC` `AAS_Optimize` body as the observed
   no-op diagnostic stub while retaining the previous GPL optimizer under the
   `BSPC` map-compiler/tooling path.
4. Added `tests/test_botlib_reachability_generation_parity.py` to pin aliases,
   Ghidra sizes, HLIL anchors, source shape, the runtime optimizer stub, and
   retained `BSPC` optimizer branch.

### Task A238: Reconstruct Steam GameServerStats value wrappers [COMPLETED]
Priority: High
Primary areas: `src/common/platform/platform_steamworks.[ch]`,
`tests/steamworks_harness.c`, `tests/test_steamworks_harness.py`,
`tests/test_platform_services.py`,
`docs/reverse-engineering/quakelive_steam_mapping_round_351.md`,
`docs/plans/steamworks-parity-plan.md`
Parity estimate: **before 72% -> after 94%** for the focused
`SteamGameServerStats` int/float/average-rate value-wrapper lane. The combined
`idSteamStats` callback plus value-wrapper reconstruction moves approximately
**97% -> 98%** for the focused lane, while broader Steamworks parity remains
approximately **99%** because live backend behavior and full descriptor-table
replay remain explicit validation boundaries.

Completed work:

1. Rechecked `SteamStats_FlushPendingValues` (`0x004670c0`),
   `SteamStats_OnStatsReceived` (`0x004671d0`), the `SteamGameServerStats`
   import row, and promoted symbol aliases for the server stats owner.
2. Reconstructed the observed `SteamGameServerStats` float get slot `0x04`,
   float set slot `0x10`, and average-rate update slot `0x18`, alongside the
   already reconstructed request, int, achievement, and store slots.
3. Extended disabled stubs so the online-services-off build keeps a stable
   API while returning clean fallbacks and zeroed outputs.
4. Built a full `SteamGameServerStats` harness mock vtable and executable
   coverage for request, int/float read, int/float write, average-rate update,
   achievement, store, and failure zeroing.

### Task A237: Map botlib movement travel runtime parity [COMPLETED]
Priority: Medium
Primary areas: `src/code/botlib/be_ai_move.c`,
`src/code/botlib/be_interface.c`, `src/code/game/botlib.h`,
`src/code/game/g_syscalls.c`, `src/code/server/sv_game.c`,
`src/code/server/ql_game_imports.inc`,
`references/analysis/quakelive_symbol_aliases.json`,
`tests/test_botlib_move_travel_parity.py`,
`docs/reverse-engineering/botlib-move-travel-mapping-2026-06-06.md`
Parity estimate: **before 73% -> after 94%** for the focused
`be_ai_move.c` movement/travel helper corridor and **before 80% -> after 82%**
for overall botlib plus movement/import wiring. Remaining uncertainty is
live-map `.aas` behavior and bot tactical movement quality, not the static
runtime owner mapping covered here.

Completed work:

1. Rechecked `quakelive_steam.exe` HLIL and Ghidra function rows for mover
   helpers, reachability selection, direct movement, travel methods, finish
   handlers, and `BotMoveToGoal` dispatch.
2. Promoted missing movement/travel aliases from `BotOnMover` through
   `BotFuncBobStartEnd`, including low-level gap/barrier/blocking helpers and
   jump, ladder, teleport, elevator, func_bobbing, waterjump, and walk-off-ledge
   owners.
3. Corrected the stale `sub_4A2620` alias from
   `BotFinishTravel_WalkOffLedge` to `BotTravel_Jump`; the walk-off-ledge pair
   is now mapped as `sub_4A21A0 -> BotTravel_WalkOffLedge` and
   `sub_4A24E0 -> BotFinishTravel_WalkOffLedge`.
4. Verified no `be_ai_move.c` C body change is currently justified; the current
   source already matches the retail travel dispatch and helper shape for this
   static slice.
5. Added `tests/test_botlib_move_travel_parity.py` to pin aliases, Ghidra
   sizes, HLIL anchors, source shape, public botlib export order, server VM
   syscall dispatch, Quake Live native import slab, qagame direct wrappers, and
   qagame syscall wrappers.

### Task A236: Reconstruct Steam GameServer stats callback wiring [COMPLETED]
Priority: High
Primary areas: `src/common/platform/platform_steamworks.[ch]`,
`src/code/server/sv_client.c`, `tests/steamworks_harness.c`,
`tests/test_steamworks_harness.py`, `tests/test_platform_services.py`,
`docs/reverse-engineering/quakelive_steam_mapping_round_350.md`,
`docs/plans/steamworks-parity-plan.md`
Parity estimate: **before 84% -> after 97%** for the focused
`idSteamStats` GameServer stats callback/bootstrap lane. Broader Steamworks
parity remains approximately **99%** because online services remain opt-in and
live Steam backend behavior plus full descriptor-table callback replay remain
explicit validation boundaries.

Completed work:

1. Rechecked `SteamGameServerUtils` import evidence, `idSteamStats`
   `GSStatsReceived_t` / `GSStatsStored_t` callback vtables, and HLIL
   registrations at callback IDs `0x708` and `0x709`.
2. Added public GS stats callback event structs, binding slots, raw payload
   dispatchers, retained registration/unregistration, and the optional
   `QL_Steamworks_ServerGetAppID` wrapper through server-utils slot `0x24`.
3. Wired the server stats owner to retain the server app id, observe
   received/stored callback results, and re-request values for the retail
   partial-validation result `8`.
4. Extended the Steamworks harness with mock `SteamGameServerUtils`, queueable
   GS stats payloads, and full enabled/disabled regression coverage for the
   callback pump and server app-id wrapper.

### Task A235: Map botlib AAS route runtime parity [COMPLETED]
Priority: Medium
Primary areas: `src/code/botlib/be_aas_route.c`,
`src/code/botlib/be_aas_routealt.c`, `src/code/botlib/be_interface.c`,
`src/code/game/botlib.h`, `src/code/game/g_syscalls.c`,
`src/code/server/sv_game.c`, `src/code/server/ql_game_imports.inc`,
`references/analysis/quakelive_symbol_aliases.json`,
`tests/test_botlib_route_runtime_parity.py`,
`docs/reverse-engineering/botlib-route-runtime-mapping-2026-06-06.md`
Parity estimate: **before 70% -> after 96%** for the focused AAS
route-cache/readback helper mapping and **before 82% -> after 97%** for the
focused route query, prediction, and alternative-route-goal source mapping.
Overall botlib plus related AAS route/import wiring moves approximately
**78% -> 80%** because this pass promotes a cohesive route-runtime tranche
without claiming exhaustive live-map `.aas` graph behavior.

Completed work:

1. Rechecked `quakelive_steam.exe` HLIL, Ghidra function rows, and existing
   mapping rounds for the AAS route-cache, route-query, prediction, and
   alternative-route helper corridor.
2. Promoted missing route-cache helper aliases for `AAS_FreeOldestCache`,
   `AAS_FreeAllClusterAreaCache`, `AAS_InitClusterAreaCache`,
   `AAS_FreeAllPortalCache`, `AAS_InitRoutingUpdate`, `AAS_ReadCache`,
   `AAS_ReadRouteCache`, and `AAS_InitReachabilityAreas`.
3. Verified the current source shape already matches retail for `.rcd`
   route-cache persistence, readback validation, initialization/shutdown
   ordering, area/portal route lookup, `AAS_PredictRoute`,
   reachability copy/iteration, model reachability, and
   `AAS_AlternativeRouteGoals`.
4. Added `tests/test_botlib_route_runtime_parity.py` to pin the new aliases,
   Ghidra sizes, Binary Ninja HLIL anchors, source body shape, public AAS
   export order, server import wrappers, qagame syscall wrappers, and qagame
   alternative-route consumers.
5. Documented the negative check that no route algorithm C body change is
   currently justified; the remaining uncertainty is live-map route data and
   broader bot behavior, not the mapped route-runtime source owner.

### Task A234: Pin legacy Steam P2P networking vtables [COMPLETED]
Priority: High
Primary areas: `tests/steamworks_harness.c`,
`tests/test_steamworks_harness.py`,
`docs/reverse-engineering/quakelive_steam_mapping_round_349.md`,
`docs/plans/steamworks-parity-plan.md`
Parity estimate: **before 82% -> after 96%** for the focused legacy
`ISteamNetworking` client/server wrapper and harness lane. Broader Steamworks
parity remains approximately **99%** because the retained retail-era P2P path
is now executable evidence while live Steam runtime behavior and a documented
modern `ISteamNetworkingSockets` / `ISteamNetworkingMessages` adapter remain
explicitly open.

Completed work:

1. Rechecked the `SteamNetworking` and `SteamGameServerNetworking` import
   evidence plus HLIL availability/read/send call sites for the legacy P2P
   wrapper slots.
2. Added a mock `SteamAPI_SteamNetworking` provider with send, availability,
   read, and accept slots matching the reconstructed wrapper offsets.
3. Replaced the null game-server networking mock with equivalent server-side
   P2P slots and added a one-shot `SteamGameServer::GetNextOutgoingPacket`
   harness path.
4. Added enabled/disabled ctypes wrappers and focused tests proving payload,
   SteamID, channel, send-type, failure, read, accept, and outgoing UDP packet
   behavior.

### Task A233: Pin Steam favorite-server matchmaking wiring [COMPLETED]
Priority: High
Primary areas: `src/code/client/cl_cgame.c`,
`tests/steamworks_harness.c`, `tests/test_steamworks_harness.py`,
`tests/test_platform_services.py`,
`docs/reverse-engineering/quakelive_steam_mapping_round_348.md`,
`docs/plans/steamworks-parity-plan.md`
Parity estimate: **before 88% -> after 98%** for the focused
`SetFavoriteServer` SteamMatchmaking add/remove wrapper and client fallback
lane. Broader Steam server-browser and WebUI bridge parity remains
approximately **99%** because live friends/history/recent-mode behavior and
live Steam favorite persistence remain validation uncertainties.

Completed work:

1. Rechecked the retail `qz_instance` method row at `0x0055C188`, the
   `0x00432681` dispatcher case, and the Ghidra import evidence for
   `SteamMatchmaking` plus `SteamUtils`.
2. Extended the Steamworks harness with mock `SteamMatchmaking` favorite-game
   add/remove slots at vtable offsets `0x08` and `0x0c`, capture getters, result
   controls, and disabled-build stubs.
3. Added executable coverage proving app ID, IP, shared connection/query port,
   favorite flag, add timestamp, remove timestamp absence, and provider failure
   propagation.
4. Made the client local favorites cache mirror an explicit compatibility
   fallback when an opted-in Steam provider cannot update favorites.

### Task A232: Close Attack and Defend retail parity wiring [COMPLETED]
Priority: High
Primary areas: `src/code/game/g_team.c`, `src/code/game/g_items.c`,
`src/code/cgame/cg_main.c`, `tests/test_attack_defend_retail_parity.py`
Parity estimate: **before 97% -> after 100%** for the focused Attack and
Defend gametype rules, flag-status transport, map item validation, score
history, round controller, spawn/reset, media registration, POI, scoreboard,
and HUD wiring surface. Broader gameplay/gametype parity remains approximately
**99%** repo-wide because this pass closes AD-specific drift while leaving
unrelated gametype and validation-freshness boundaries unchanged.

Completed work:

1. Rechecked `qagamex86.dll` and `cgamex86.dll` symbol maps plus Binary Ninja
   HLIL and Ghidra evidence for `Team_SetFlagStatus`, `G_CheckTeamItems`,
   `Team_TouchOurFlag`, `Team_TouchEnemyFlag`, `G_ADHandleDamageScore`,
   `AD_RoundStateTransition`, `G_ADUpdateScoreHistory`,
   `CG_ParseADScores`, `CG_DrawADRoundScoreboard`,
   `CG_DrawObjectiveStatus`, `CG_PlayerObjectiveSprite`, and
   `CG_RegisterGraphics`.
2. Restored the retail CTF-family AD flag-status path so `Team_InitGame`
   initializes red/blue status for `GT_ATTACK_DEFEND` and
   `Team_SetFlagStatus` publishes the two-character `CS_FLAGSTATUS` payload
   for both CTF and Attack and Defend.
3. Restored AD map-item validation in `G_CheckTeamItems`, matching the retail
   red/blue flag warning branch for gametype `0xb`.
4. Restored AD client media registration for the red/blue flag model bank and
   neutral/dropped flag model bank in `CG_RegisterGraphics`, matching the
   retail cgame evidence that includes gametype `0xb` in those assets.
5. Added `tests/test_attack_defend_retail_parity.py` to pin the AD symbol-map
   owners, retail evidence snippets, server flag/status and item-validation
   gates, round controller, damage/bonus flow, spawn/frame hooks,
   `scores_ad`/`adscores` transport, cgame flag media, POI, and HUD wiring.

### Task A231: Label invalid Steam browser request modes as internet default [COMPLETED]
Priority: High
Primary areas: `src/code/client/cl_main.c`,
`tests/test_platform_services.py`,
`docs/reverse-engineering/quakelive_steam_mapping_round_347.md`,
`docs/plans/steamworks-parity-plan.md`
Parity estimate: **before 85% -> after 99%** for the focused
invalid/default WebUI server-browser request-mode labeling path. Broader
Steam server-browser parity remains approximately **99%** because native
list/detail owners are already reconstructed and the remaining uncertainty is
live friends/history result parity plus any distinct recent-mode UI evidence,
not the observed invalid/default `RequestServers` dispatch.

Completed work:

1. Rechecked the retail `JSBrowser_RequestServers` HLIL branch
   `arg2 - 1 u> 3`, which routes mode `0` and out-of-range retained values to
   the internet `ISteamMatchmakingServers` request slot with the
   `gamedir=baseq3` filter.
2. Confirmed the source dispatch helpers already agreed with retail:
   invalid/default modes enter `QL_STEAM_SERVER_BROWSER_INTERNET` natively and
   `AS_GLOBAL` in the source-browser fallback path.
3. Updated `CL_SteamBrowser_RequestModeLabel` so the retained default case now
   reports `internet` instead of `unknown`, aligning diagnostics and fallback
   telemetry with the actual dispatch path.
4. Added a platform-service parity assertion that the request-mode label block
   has the explicit mode-0 and default `internet` returns and no longer
   contains an `unknown` request-mode label.

### Task A230: Lock CTF and One Flag retail parity wiring [COMPLETED]
Priority: High
Primary areas: `src/code/game/g_team.c`, `src/code/game/g_combat.c`,
`src/code/game/g_cmds.c`, `src/code/game/ai_dmq3.c`,
`src/code/game/ai_team.c`, `src/code/cgame/cg_servercmds.c`,
`src/code/cgame/cg_main.c`, `src/code/cgame/cg_newdraw.c`,
`tests/test_ctf_oneflag_retail_parity.py`
Parity estimate: **before 99% -> after 100%** for the focused CTF and One
Flag gametype rules, scoring, status, bot, scoreboard, and HUD wiring surface.
Broader gameplay/gametype parity remains approximately **99%** repo-wide
because this pass found the source behavior already aligned with the committed
retail references and converted the audit into focused regression coverage
without changing unrelated gametype lanes.

Completed work:

1. Rechecked `qagamex86.dll` and `cgamex86.dll` symbol maps plus Binary Ninja
   HLIL evidence for `Team_SetFlagStatus`, `Team_TouchOurFlag`,
   `Team_TouchEnemyFlag`, `Pickup_Team`, `Team_FragBonuses`,
   `Team_CheckHurtCarrier`, `CheckAlmostCapture`, `CG_ParseCtfScores`,
   `CG_ParseCTFStats`, `CG_OneFlagStatus`, `CG_OtherTeamHasFlag`,
   `CG_YourTeamHasFlag`, and `CG_DrawPlayerHasFlag`.
2. Verified qagame CTF and One Flag initialization/status configstrings,
   dropped-flag return/reset handling, neutral-flag pickup/capture flow,
   capture assist accounting, near-capture event selection, and the retail
   carrier-bonus split where `Team_CheckHurtCarrier` only stamps red/blue flag
   or Harvester skull carrier damage while `Team_FragBonuses` handles One Flag
   neutral-carrier frags.
3. Verified score transports and client parsing stay on the retail
   `scores_ctf`/`ctfstats` family path, including the two-character CTF flag
   status payload versus the single-character One Flag payload.
4. Verified client HUD/objective wiring for One Flag neutral status icons,
   CTF/One Flag ownerdraw visibility predicates, local carried-flag rendering,
   and CTF-family feeder rows.
5. Verified bot inventory, flag-state event handling, and team-order dispatch
   keep CTF red/blue flag state separate from One Flag neutral-flag state.
6. Added `tests/test_ctf_oneflag_retail_parity.py` to pin the audited retail
   surface across qagame, cgame, and bot wiring.

### Task A229: Tighten native Steam detail query-handle fallback [COMPLETED]
Priority: High
Primary areas: `src/common/platform/platform_steamworks.c`,
`tests/steamworks_harness.c`, `tests/test_steamworks_harness.py`,
`tests/test_netcode_parity_manifest.py`,
`docs/reverse-engineering/quakelive_steam_mapping_round_346.md`
Parity estimate: **before 86% -> after 98%** for the focused native
server-browser detail query-handle failure path. Broader WebUI server-browser
ownership remains approximately **99%** because the list and detail native
owners were already wired; this pass closes the partial ping/rules/players
query allocation hole and preserves the documented source status-query
fallback. Repo-wide parity remains **99%** because the
`QL_BUILD_ONLINE_SERVICES` default-disabled policy boundary is unchanged.

Completed work:

1. Rechecked the `JSBrowserDetails_RequestServerDetails` evidence for the
   retained `PingServer -> ServerRules -> PlayerDetails` dispatch order and
   the adjacent `CancelServerQuery` vtable slot.
2. Updated `QL_Steamworks_RequestServerDetails` so the three-detail-probe
   bundle is all-or-nothing: any non-positive query handle cancels the valid
   partial handles, leaves output handles zeroed, and returns false.
3. Verified `QL_Steamworks_BeginServerBrowserDetailRequest` stays inactive on
   partial native detail allocation failure, allowing the client's existing UDP
   status-query fallback to run.
4. Added a Steamworks harness detail-query result setter plus enabled-build
   regression coverage for the low-level wrapper and retained detail owner.
5. Pinned the new lifecycle invariant in the netcode parity manifest and
   documented the source-side inference boundary in round 346.

### Task A228: Close Race gametype retail parity [COMPLETED]
Priority: High
Primary areas: `src/code/game/g_race.c`,
`tests/test_racepoint_commands.py`,
`tests/test_game_nonteam_scoreboard_helper_parity.py`,
`tests/test_game_helper_seam_parity.py`
Parity estimate: **before 98% -> after 100%** for the focused Race gametype
server command, checkpoint, timing, score transport, admin-point, and
scoreboard wiring surface. Broader gameplay/gametype parity remains
approximately **99%** repo-wide because this pass closes the remaining
Race-specific qagame scoreboard/start-predicate drift without changing the
known compatibility-only lanes.

Completed work:

1. Rechecked qagame and cgame retail evidence for `race_info`, `race_init`,
   `admin_race_point_N`, Race touch events, finish ranking, and
   `scores_race` row transport.
2. Aligned `G_RaceBuildScoreString` with retail qagame ownership by consuming
   `level.numPlayingClients` and `level.sortedClients` instead of rebuilding a
   local Race order with a private `qsort` comparator.
3. Tightened the Race start predicate to the retail targetname-free authored
   map behavior while preserving the command-spawned `arp*` admin chain for
   immediate testing/editing.
4. Extended the compiled Race command probe and static parity guards to pin the
   retail score row shape: client number, personal best/PERS_SCORE, clamped
   ping, and session seconds in the sorted-client order.

### Task A227: Close Red Rover retail gametype parity [COMPLETED]
Priority: High
Primary areas: `src/code/game/g_client.c`, `src/code/game/g_cmds.c`,
`src/code/game/g_combat.c`, `src/code/game/g_local.h`, `src/code/game/g_rr.c`,
`tests/test_game_round_controller_helper_parity.py`,
`tests/test_game_active_pmove_wiring_parity.py`,
`tests/test_game_helper_seam_parity.py`,
`docs/reverse-engineering/qagame-setteam-reconstruction-2026-05-25.md`
Parity estimate: **before 90% -> after 100%** for the focused Red Rover
gametype server surface: damage-score/active-round gating, infected
spawn/loadout ownership, and SetTeam warmup/pre-release wiring. Broader Red
Rover gametype wiring moves approximately **95% -> 100%** because the round
controller, infection seeding/spread, survivor bonus, autojoin, scoreboard,
cgame HUD, and last-alive paths were already source-owned while the retail
boolean damage helper dispatch and direct Red Rover SetTeam spawn branch still
needed to be closed. Repo-wide parity remains **99%**.

Completed work:

1. Rechecked `qagamex86.dll` symbols, Ghidra function inventory, Binary Ninja
   HLIL `0x100643E0`, and the `G_Damage` gametype-12 call site.
2. Converted `G_RRHandleDamageScore` to the retail helper shape:
   same-team suppression, active-round gating, health/armor damage caps, and
   100-damage score buckets for the non-infected lane.
3. Preserved the already recovered infected-survivor score policy inside the
   active-round helper after retail damage capping.
4. Wired `G_Damage` so Red Rover calls the helper at the retail post-armor
   split point and aborts inactive-round damage when the helper returns false.
5. Split the Red Rover spawn/loadout finalizer so infected clients consume the
   zombie gauntlet/health path before the generic loadout finalizer, matching
   the retail survivor-vs-infected branch.
6. Restored the Red Rover seed/spread forced-conversion shortcut so RR team
   mutations rerun `G_RRResetClientForRound` directly, matching the retail
   internal team-change latch without broadening external `SetTeam`.
7. Retired the stale non-owning `g_rr.c` stub so the source tree no longer
   carries a second, divergent Red Rover implementation.
8. Extended the Red Rover parity tests to pin the source helper, public
   prototypes, combat/SetTeam dispatch, loadout split, build-owner boundary,
   and HLIL offsets used for reconstruction.

### Task A226: Close Domination gametype retail parity [COMPLETED]
Priority: High
Primary areas: `src/code/game/g_team.c`, `src/code/game/g_local.h`,
`src/code/game/g_main.c`, `tests/test_game_domination_parity.py`
Parity estimate: **before 93% -> after 100%** for the focused Domination
gametype server and client-wiring surface. Broader gameplay/gametype parity
remains approximately **99%** repo-wide because this pass closes the known
Domination-specific qagame reward, point activation, and defense routing gaps
without changing unrelated gametype lanes.

Completed work:

1. Rechecked `qagamex86.dll` Binary Ninja HLIL and symbol-map evidence for
   `Team_SelectDominationSpawnPoint`, `G_DominationRewardCaptureParticipants`,
   `G_DominationSelectPrimaryCapturer`, `G_DominationPointActivate`,
   `G_UpdateDominationPointCountConfigstrings`,
   `G_DominationCheckDefenseBonus`, `SP_team_dom_point`, and the
   `Team_FragBonuses` Domination branch.
2. Restored the retail qagame five-point registration cap and delayed
   `team_dom_point` floor-settling activation trace while preserving delayed
   spawn-target retry wiring.
3. Added current-frame Domination participant lists, primary-capturer
   retention, and retail capture/assist reward fan-out with the 25/15 score
   bonuses, award sprites, persistent counters, and rank medal events.
4. Routed Domination frags through the retail owned-point defense check before
   CTF flag logic and accepted the retail `DEFENSE` medal token in the rank
   resolver.
5. Added focused Domination parity tests and validated them with the existing
   Domination count and gametype lifecycle fixtures plus a Debug Win32 native
   solution build.

### Task A225: Tighten native Steam browser request-handle fallback [COMPLETED]
Priority: High
Primary areas: `src/common/platform/platform_steamworks.c`,
`src/code/client/cl_main.c`, `tests/steamworks_harness.c`,
`tests/test_steamworks_harness.py`, `tests/test_platform_services.py`,
`tests/test_netcode_parity_manifest.py`,
`docs/reverse-engineering/quakelive_steam_mapping_round_345.md`
Parity estimate: **before 88% -> after 98%** for the focused native
server-browser request-owner failure path. Broader WebUI server-browser
ownership remains approximately **99%** because the list and detail native
owners were already wired; this pass closes the null-handle fallback hole and
relabels friends/history compatibility telemetry as fallback-only. Repo-wide
parity remains **99%** because the `QL_BUILD_ONLINE_SERVICES` default-disabled
policy boundary is unchanged.

Completed work:

1. Rechecked `quakelive_steam.exe` HLIL and alias evidence for
   `JSBrowser_RequestServers`, `SteamBrowser_RefreshList`,
   `JSBrowser_OnRefreshComplete`, and the retained
   `ISteamMatchmakingServers` request-mode slots.
2. Confirmed the current client list path is native-first for internet, LAN,
   friends, favorites, and history modes when an opted-in Steamworks provider
   exposes the native server-browser interface.
3. Updated `QL_Steamworks_BeginServerBrowserOwnerRequest` so a zero native
   request handle returns false, leaves the owner idle, and lets the existing
   source-browser fallback run instead of timing out an active-but-handleless
   native refresh.
4. Added a Steamworks harness request-result setter and lifecycle coverage for
   the zero-handle path.
5. Relabeled the browser compatibility diagnostics so friends/history now read
   as source fallback mappings after native request-handle failure, not as
   permanently source-owned modes.

### Task A224: Wire Clan Arena retail damage-score helper [COMPLETED]
Priority: High
Primary areas: `src/code/game/g_team.c`, `src/code/game/g_combat.c`,
`src/code/game/g_local.h`, `tests/test_game_round_controller_helper_parity.py`
Parity estimate: **before 92% -> after 98%** for the focused Clan Arena
damage-score and active-round damage gate lane. Broader Clan Arena gametype
wiring moves approximately **96% -> 98%** because the round controller,
spectator reset/release, compact scoreboard, castats, and last-alive event
surfaces were already reconstructed while the dedicated retail CA damage helper
was still absent. Repo-wide parity remains **99%**.

Completed work:

1. Rechecked `qagamex86.dll` Ghidra metadata/function inventory and Binary
   Ninja HLIL for `0x10037F80`, `0x10037FD0`, `0x10038230`, and the sibling
   Attack & Defend damage helper.
2. Added `G_CAHandleDamageScore` to mirror the retail CA post-armor damage
   helper: same-team suppression, active-round gating, health/armor damage
   caps, and 100-damage score bucket conversion through direct `PERS_SCORE`
   increments plus `CalculateRanks`.
3. Wired `G_Damage` so Clan Arena calls the CA helper at the retail
   post-armor split point and aborts inactive-round damage when the helper
   returns false.
4. Extended the round-controller parity test to pin the source helper,
   `G_Damage` dispatch, and the HLIL evidence offsets used for reconstruction.

### Task A223: Name the SteamDataSource non-avatar fallback owner [COMPLETED]
Priority: High
Primary areas: `src/code/client/cl_steam_resources.c`,
`src/code/client/cl_main.c`, `tests/test_platform_services.py`,
`tests/test_awesomium_browser_parity.py`,
`tools/ci/verify-awesomium-browser-host-parity.ps1`,
`docs/reverse-engineering/quakelive_steam_mapping_round_344.md`
Parity estimate: **before 82% -> after 96%** for the focused
SteamDataSource fallback-owner diagnostic surface. Broader SteamDataSource
resource-bridge source visibility moves approximately **93% -> 95%** because
the fallback owner is now named and cvar-published, while exact live Awesomium
delayed-response ownership remains bounded. Repo-wide parity remains **99%**
because the `QL_BUILD_ONLINE_SERVICES` default-disabled policy boundary is
unchanged.

Completed work:

1. Rechecked `quakelive_steam.exe` symbols and HLIL for
   `SteamDataSource`, `QLResourceInterceptor`, the
   `Awesomium::DataSource::SendResponse` boundary, and prior mapping rounds 91
   and 289.
2. Added a source-visible `QLResourceInterceptor launcher/web fallback` owner
   label for non-avatar `steam://` requests outside the avatar-native
   SteamDataSource subset.
3. Published SteamDataSource subset, native-gap, and fallback-owner labels
   through the retained resource-bridge ROM cvar surface.
4. Updated non-avatar Steam resource diagnostics to say they are routed to the
   launcher/web fallback owner rather than leaving the route as a generic
   missing-owner message.
5. Extended platform-service, Awesomium parity, and verifier-script anchors to
   pin the label and cvars.

### Task A222: Wire WebUI server browser native Steam detail owner [COMPLETED]
Priority: High
Primary areas: `src/code/client/cl_main.c`,
`src/common/platform/platform_steamworks.[ch]`,
`tests/test_steamworks_harness.py`, `tests/steamworks_harness.c`,
`tests/test_platform_services.py`, `tests/test_netcode_parity_manifest.py`,
`docs/reverse-engineering/quakelive_steam_mapping_round_343.md`
Parity estimate: **before 74% -> after 98%** for the focused WebUI
server-detail request dispatch lane. Broader server-browser/details parity
moves approximately **98% -> 99%** because native detail callbacks are now
wired while provider-disabled and failed native requests still retain explicit
source-owned fallbacks. Repo-wide parity remains **99%** because the
`QL_BUILD_ONLINE_SERVICES` default-disabled policy boundary is unchanged.

Completed work:

1. Rechecked `quakelive_steam.exe` HLIL, alias, and prior mapping evidence for
   `SteamBrowser_RequestServerDetails`, `JSBrowserDetails_RequestServerDetails`,
   the `0x58`-byte callback object, the base/base+4/base+8 callback views, and
   the `PingServer -> ServerRules -> PlayerDetails` query order.
2. Added `QL_Steamworks_ReadServerBrowserPingResponse` so raw Steam
   `gameserveritem_t` ping payloads project into the retained
   `servers.details.<ip>_<port>.response` WebUI shape.
3. Added a client-owned native detail object with ping, rules, and players
   callbacks that publish the retained detail response/failed/end event
   families.
4. Made `CL_Steam_RequestServerDetails` native-first for opted-in Steamworks
   builds, keeping the existing UDP status query as an explicit fallback.
5. Extended harness, platform-service, and netcode parity tests to pin the new
   native detail owner, projection helper, and source fallback boundary.

### Task A221: Allow retail LAN clients through server auth fallback [COMPLETED]
Priority: High
Primary areas: `src/code/server/sv_game.c`, `src/code/server/sv_client.c`,
`tests/test_platform_services.py`
Parity estimate: **before 92% -> after 100%** for the focused retail-client
LAN dedicated-server auth slice. Repo-wide parity remains **99%** because this
closes a narrow policy mismatch without changing the broader default-disabled
online-service boundary.

Completed work:

1. Aligned the qagame-facing `trap_VerifySteamAuth` fallback with the existing
   `Sys_IsLANAddress` challenge fast path so retail clients on a private LAN no
   longer fail with `Failed to verify Steam auth token`.
2. Kept LAN joins out of the live Steam GameServer auth-session bootstrap even
   if userinfo happens to carry an auth token.
3. Updated platform-service coverage so the LAN fallback and auth-session skip
   remain pinned.

### Task A220: Wire WebUI server browser native Steam list owner [COMPLETED]
Priority: High
Primary areas: `src/code/client/cl_main.c`, `tests/test_platform_services.py`,
`tests/test_netcode_parity_manifest.py`,
`docs/reverse-engineering/webui-server-browser-native-steamworks-2026-06-05.md`
Parity estimate: **before 82% -> after 100%** for the focused WebUI
server-list dispatch slice. Broader server-browser/details parity moves
approximately **96% -> 98%** because native list callbacks are now wired while
detail requests still retain the existing UDP status fallback. Repo-wide parity
remains **99%** because the `QL_BUILD_ONLINE_SERVICES` default-disabled policy
boundary is unchanged.

Completed work:

1. Rechecked the `quakelive_steam.exe` HLIL and alias evidence for
   `JSBrowser_RequestServers`, `SteamBrowser_RequestServers`,
   `JSBrowser_OnServerResponded`, `JSBrowser_OnServerFailedToRespond`,
   `JSBrowser_OnRefreshComplete`, and the `SteamMatchmakingServers` import.
2. Confirmed the empty WebUI Internet list was caused by routing through the
   policy-disabled legacy UDP master query rather than by missing Steam auth.
3. Added a native `ISteamMatchmakingServerListResponse` owner in `cl_main.c`
   so opted-in Steamworks builds publish `servers.details.*.response`,
   `servers.details.*.failed`, and `servers.refresh.end` events into the WebUI.
4. Kept default builds and runtime-disabled profiles on the explicit fallback
   path; Steam and other Quake Live online services remain opt-in behind
   `QL_BUILD_ONLINE_SERVICES`.
5. Updated focused platform and netcode parity guards so the browser request
   surface is pinned as native-first with source-owned fallback.

### Task A219: Map botlib precompiler source-handle API parity [COMPLETED]
Priority: Medium
Primary areas: `src/code/botlib/l_precomp.c`,
`src/code/botlib/be_interface.c`, `src/code/game/botlib.h`,
`src/code/game/g_public.h`, `src/code/game/g_syscalls.c`,
`src/code/server/sv_game.c`, `src/code/server/ql_game_imports.inc`,
`tests/test_botlib_internal_parity.py`,
`docs/reverse-engineering/botlib-precompiler-source-handle-mapping-2026-06-05.md`
Parity estimate: **before 76% -> after 96%** for the focused precompiler
source-handle API slice. Overall botlib plus related parser/API wiring moves
approximately **68% -> 69%** because this pass closes a compact ABI boundary
without changing broader macro expansion, script lexing, AAS, or gameplay
heuristics.

Completed work:

1. Selected `l_precomp.c` public source-handle wrappers as the next botlib
   slice after the structure/character/weight parser corridor.
2. Rechecked retail `quakelive_steam.exe` HLIL and Ghidra `functions.csv`
   evidence for `PC_LoadSourceHandle`, `PC_FreeSourceHandle`,
   `PC_ReadTokenHandle`, `PC_SourceFileAndLine`, `PC_SetBaseFolder`, and
   `PC_CheckOpenSourceHandles`.
3. Pinned source and retail behavior for `MAX_SOURCEFILES == 64`, valid handle
   range `1..63`, token field copying, `TT_STRING` quote stripping, source
   file/line reporting, base-folder forwarding, and open-source leak warnings.
4. Confirmed related wiring through `botlib_export_t`, `GetBotLibAPI`, legacy
   `SV_GameSystemCallsImpl` dispatch, qagame compatibility import table
   wrappers, and classic `trap_PC_*` syscall stubs.
5. Documented that `BOTLIB_PC_ADD_GLOBAL_DEFINE` has a named direct native
   qagame import slot while the four PC source-handle calls intentionally
   remain behind the retained compatibility import surface.

### Task A218: Extend botlib parser-resource sibling mapping [COMPLETED]
Priority: Medium
Primary areas: `src/code/botlib/be_ai_char.c`,
`src/code/botlib/be_ai_weight.c`,
`tests/test_botlib_internal_parity.py`,
`docs/reverse-engineering/botlib-structure-resource-reader-mapping-2026-06-05.md`
Parity estimate: **before 97% -> after 98%** for the focused botlib
parser-resource corridor selected around `l_struct.c` and its adjacent
resource loaders. Overall botlib plus related parser wiring moves
approximately **67% -> 68%** because this pass adds characteristic and
fuzzy-weight parser evidence without changing broader AAS, movement, or combat
heuristics.

Completed work:

1. Extended the selected botlib parser section from structure-table resources
   into the closest source siblings: `be_ai_char.c` character resources and
   `be_ai_weight.c` fuzzy-weight resources.
2. Rechecked retail `quakelive_steam.exe` HLIL and Ghidra evidence for
   `BotLoadCharacterFromFile`, `BotLoadCachedCharacter`,
   `BotLoadCharacterSkill`, `ReadValue`, `ReadFuzzyWeight`,
   `ReadFuzzySeperators_r`, `ReadWeightConfig`, and `FindFuzzyWeight`.
3. Pinned retail allocation/layout evidence: character load allocation
   `0x2cc`, weight config allocation `0x444`, `MAX_CHARACTERISTICS == 80`,
   `MAX_WEIGHT_FILES == 128`, and the weight filename copy at offset `0x404`.
4. Preserved parser quirks as retail parity facts, including the characteristic
   upper-bound check shape and fuzzy-switch missing-default fallback.
5. Documented that `be_ai_weight.c` writer helpers remain inside `#if 0`,
   reinforcing that active retail evidence belongs to the read-side parser
   surface for this round.

### Task A217: Map botlib structure resource reader parity [COMPLETED]
Priority: Medium
Primary areas: `src/code/botlib/l_struct.c`,
`src/code/botlib/be_ai_goal.c`, `src/code/botlib/be_ai_weap.c`,
`references/analysis/quakelive_symbol_aliases.json`,
`tests/test_botlib_internal_parity.py`,
`docs/reverse-engineering/botlib-structure-resource-reader-mapping-2026-06-05.md`
Parity estimate: **before 72% -> after 97%** for the focused
`l_struct.c` resource-reader plus item/weapon/projectile consumer-table mapping
slice. Overall botlib plus related parser wiring moves approximately
**65% -> 67%** because this pass tightens a narrow resource-parser proof
surface without changing broader bot movement, AAS, or gameplay heuristics.

Completed work:

1. Selected botlib structure resource parsing as the next productive forward
   section because it gates bot item, weapon, and projectile resource data.
2. Rechecked retail `quakelive_steam.exe` HLIL and Ghidra evidence for
   `FindField`, `ReadNumber`, and `ReadStructure`, including diagnostic
   strings, numeric bounds behavior, nested-structure handling, and consumer
   call sites.
3. Confirmed the checked-in C source already matches the observed retail shape,
   including the source-local `ReadChar`/`ReadString` helpers that retail folds
   into `ReadStructure`.
4. Added focused regression coverage that pins the structure-reader source
   contract, bot item/weapon consumers, alias map entries, HLIL anchors, and
   Ghidra call-site evidence.
5. Extended the pass to the concrete `iteminfo`, `weaponinfo`, and
   `projectileinfo` field tables, retail allocation sizes, table data
   addresses, top-level resource tokens, and weapon/projectile fix-up wiring.
   Documented the adjacent writer helpers as source-real but not yet safely
   retail-aliased because the visible `WriteStructure` caller is debug-gated.

### Task A216: Verify server snapshot related wiring parity [COMPLETED]
Priority: High
Primary areas: `src/code/server/sv_snapshot.c`, `src/code/server/sv_bot.c`,
`src/code/server/sv_game.c`, `src/code/game/g_syscalls.c`,
`src/code/game/ai_main.c`, `src/code/client/cl_parse.c`,
`src/code/client/cl_cgame.c`, `src/code/cgame/cg_snapshot.c`,
`tests/test_netcode_parity_manifest.py`
Parity estimate: **before 100% -> after 100%** for the focused server
snapshot related-wiring slice. Repo-wide parity remains **99%** because this
pass confirmed adjacent retail wiring and added a missing guard without
changing the broader compatibility-only or validation-freshness boundaries.

Completed work:

1. Rechecked the server snapshot construction/send path, client parse/readback
   path, cgame snapshot pump, qagame visibility exports, and bot snapshot
   entity bridge against the committed HLIL aliases and existing parity tests.
2. Confirmed no additional source behavior drift after the `SV_SendClientSnapshot`
   wrapper closure: snapshot body writing still flows directly to overflow
   handling/send, client/cgame readback remains ordered, and bot clients query
   the built snapshot ring without packet emission.
3. Added a focused parity guard that pins `SV_BotGetSnapshotEntity` and
   `QL_G_trap_BotGetSnapshotEntity` to retail `sub_4DDAC0`/`sub_4E17E0`,
   including the legacy syscall, native import slot, qagame syscall mapping,
   and `BotAI_GetSnapshotEntity` handoff.

### Task A215: Verify client connection adjacent wiring parity [COMPLETED]
Priority: High
Primary areas: `src/code/client/cl_main.c`, `src/code/client/cl_net_chan.c`,
`src/code/server/sv_client.c`, `src/code/server/sv_main.c`,
`src/code/cgame/cg_newdraw.c`, `tests/test_engine_netcode_parity.py`
Parity estimate: **before 96% -> after 100%** for the adjacent client
connection wiring slice. Repo-wide parity remains **99%** because this pass
confirmed the focused wiring and corrected a stale guard rather than changing
the broader online-service or validation-freshness boundaries.

Completed work:

1. Rechecked the related connection corridor around client connect/retry,
   challenge and connect responses, packet dispatch, client netchan setup, and
   server challenge/direct-connect acceptance.
2. Confirmed the cgame serverinfo handoff still pulls the retail map-name
   ownerdraw label from `CS_SERVERINFO` through `SERVERINFO_KEY_MAPNAME`.
3. Corrected the broad engine-netcode parity guard so it matches the stricter
   retail-backed cgame ownerdraw tests for the `CG_MapNameText` helper.
4. Reran the focused and adjacent parity tests covering netcode manifest,
   engine netcode, client full-parity gate, client command/netchan wrappers,
   command registration/run-loop mapping, platform challenge/direct-connect
   wiring, and cgame map-name display wiring.

### Task A214: Close client connection-response protocol parity [COMPLETED]
Priority: High
Primary areas: `src/code/client/client.h`, `src/code/client/cl_main.c`,
`tests/test_netcode_parity_manifest.py`,
`docs/reverse-engineering/netcode-parity-manifest.json`
Parity estimate: **before 94% -> after 100%** for the focused client
connection-response protocol slice. Repo-wide parity remains **99%** because
the online-service policy and broader external validation freshness boundaries
are unchanged.

Completed work:

1. Rechecked `CL_Connect_f`, `CL_CheckForResend`, and
   `CL_ConnectionlessPacket` against the committed `quakelive_steam.exe` HLIL
   and Ghidra corpus.
2. Restored the retail bad-address path by publishing
   `CL_WebView_PublishGameError( "Bad server address" )` after the failed
   address parse, matching retail `sub_4F3570`.
3. Added the missing 0x400-byte `challengeResponse` sideband text slot before
   `clc.netchan` and copied `Cmd_Argv(2)` into it before entering
   `CA_CHALLENGING`, matching the retail `0x016177fc` -> `0x01617bfc`
   layout/order.
4. Tightened the netcode parity guard so the retail sideband copy, client
   connection layout, and connectionless state transition order remain pinned.

### Task A213: Close server snapshot retail send parity [COMPLETED]
Priority: High
Primary areas: `src/code/server/sv_snapshot.c`,
`src/code/server/sv_client.c`, `tests/test_netcode_parity_manifest.py`,
`docs/reverse-engineering/netcode-parity-manifest.json`
Parity estimate: **before 95% -> after 100%** for the focused
`SV_SendClientSnapshot` retail send-wrapper slice. Repo-wide parity remains
**99%** because broader compatibility-only and online-service boundaries are
unchanged.

Completed work:

1. Rechecked the `quakelive_steam.exe` HLIL for `0x004E5AC0` and the Ghidra
   `functions.csv` row for `SV_SendClientSnapshot`.
2. Removed the classic `SV_WriteDownloadToClient` injection from
   `SV_SendClientSnapshot`, matching the retail order from
   `SV_WriteSnapshotToClient` directly to overflow handling and
   `SV_SendMessageToClient`.
3. Kept legacy UDP download requests from arming stale `downloadName` state now
   that QL snapshots no longer carry `svc_download` blocks.
4. Updated the netcode manifest and parity guard so reintroducing
   snapshot-side classic download payloads is treated as a regression.

### Task A212: Recheck client-side prediction retail parity [COMPLETED]
Priority: High
Primary areas: `src/code/cgame/cg_predict.c`,
`src/code/cgame/cg_view.c`, `src/code/cgame/cg_ents.c`,
`src/code/cgame/cg_snapshot.c`, `tests/test_cgame_snapshot_parity.py`,
`references/symbol-maps/cgame.json`, `docs/reverse-engineering/cgame-mapping.md`,
`docs/reverse-engineering/cgame-client-prediction-parity-recheck-2026-06-05.md`
Parity estimate: **before 100% -> after 100%** for the focused cgame
client-side prediction and related wiring slice. Repo-wide parity remains
**99%** because this pass strengthened validation for an already-closed
strict-retail corridor rather than closing a new whole-repo gap.

Completed work:

1. Rechecked the `cgamex86.dll` Ghidra metadata, symbol map, and cgame mapping
   notes for the retail prediction corridor.
2. Confirmed no gameplay source patch was needed: `cg_predict.c` already keeps
   the retail replay shape for interpolation fallbacks, local `pmove_t` setup,
   command replay, item/trigger prediction, mover adjustment, step smoothing,
   projectile nudge, predicted rail replay, and transition handoff.
3. Tightened `tests/test_cgame_snapshot_parity.py` to pin the mapped solid-list,
   box/capsule trace, point-contents, interpolation, red/blue-flag predicate,
   high-value item skip, and complete prediction symbol-map evidence set.
4. Rechecked and pinned related wiring around prediction: `CG_DrawActiveFrame`
   caller order, `CG_AddPacketEntities` predicted-player proxy,
   non-predicted local-player refresh, mover compensation, initial/next/
   transition snapshot handoffs, snapshot pump, native draw wrapper, snapshot
   import, usercmd import, pmove settings, and the mapped retail symbols for
   those edges.

### Task A211: Close server browser protocol and master heartbeat parity [COMPLETED]
Priority: High
Primary areas: `src/code/client/cl_main.c`, `src/code/client/cl_cgame.c`,
`src/code/server/sv_main.c`, `src/code/server/sv_init.c`,
`src/code/server/sv_client.c`, `src/code/qcommon/common.c`,
`src/common/platform/platform_steamworks.c`, `tests/test_netcode_parity_manifest.py`,
`docs/reverse-engineering/network-server-browser-master-heartbeat-parity-2026-06-05.md`
Parity estimate: **before 96% -> after 100%** for the focused server browser
protocol and master heartbeat slice. Repo-wide parity remains **99%** because
the online-service boundary and broader native Steam product-integration policy
are unchanged.

Completed work:

1. Rechecked the `quakelive_steam.exe` HLIL and Ghidra corpus for
   `getserversResponse`, `getinfo xxx`, `getstatus`, `sv_master`, protocol
   `91`, and the Steam GameServer / SteamMatchmakingServers imports.
2. Confirmed the active profile owns the Quake Live browser/status tokens and
   info keys, while legacy UDP master traffic remains policy-gated.
3. Fixed `SV_MasterHeartbeat` so explicit configured `host:port` master entries
   keep their port instead of being overwritten with `PORT_MASTER`.
4. Added a focused regression guard for the QL browser parser, request grammar,
   heartbeat token, Steam heartbeat owner, and committed retail evidence.
5. Rechecked the related `qz_instance` browser dispatch, browser event
   publication, native `ISteamMatchmakingServers` wrapper, server info/status
   key publication, Steam GameServer published state, spawn/frame/reconnect/
   shutdown heartbeat lifecycle, and default-disabled legacy UDP service gate.
6. Added a wiring-level parity guard so the related browser/heartbeat source
   graph remains pinned at **100%** for this focused source-owned and
   policy-gated slice.

### Task A210: Close selected 335-339 cgame ownerdraw parity [COMPLETED]
Priority: High
Primary areas: `tests/test_cgame_displaycontext_parity.py`,
`docs/reverse-engineering/cg-ownerdrawtype-parity-index.md`,
`docs/reverse-engineering/cgame-mapping.md`
Parity estimate: **before 99% -> after 100%** for the selected
`CG_BLUE_TEAM_TIMEHELD_HASTE`, `CG_BLUE_TEAM_TIMEHELD_INVIS`,
`CG_FLAG_STATUS`, `CG_HEALTH_COLORIZED`, and `CG_MATCH_STATE` ownerdraw set.
Repo-wide parity remains **98%** because unrelated compatibility,
source-legacy, online-service, and packaging surfaces are unchanged.

Completed work:

1. Rechecked the retail `cgamex86.dll` dispatcher for raw ownerdraw cases
   `0x14F` through `0x153`.
2. Confirmed blue Haste and Invisibility time-held ownerdraws normalize
   through `0x10039AE0` selector cases `4` and `5`, select the blue
   `scorestats_team` row, accumulate qagame hold-stat seconds through the
   Haste/Invisibility powerup mappings, and format through the recovered
   `%i:%i%i` minute-second helper.
3. Confirmed `CG_FLAG_STATUS` routes to the recovered retail objective-status
   graphic strip, with source parity covering the CTF-family, one-flag,
   Harvester, and Domination strip paths plus the preserved fallback label
   route for unsupported states.
4. Confirmed `CG_HEALTH_COLORIZED` resolves local or followed-client
   health/armor color, preserves the competitive HUD `scorebox_follow` shader
   fallback, and keeps both shader-tint and filled-rect draw paths.
5. Confirmed `CG_MATCH_STATE` paints only the compact uppercase phase banner
   (`MATCH SUMMARY`, `MATCH WARMUP`, or `MATCH IN PROGRESS`) and leaves
   timeout/overtime text to their dedicated ownerdraws.
6. Added focused structural coverage and refreshed the cgame ownerdraw and
   mapping ledgers for the selected five.

### Task A209: Close selected 330-334 cgame ownerdraw parity [COMPLETED]
Priority: High
Primary areas: `tests/test_cgame_displaycontext_parity.py`,
`docs/reverse-engineering/cg-ownerdrawtype-parity-index.md`,
`docs/reverse-engineering/cgame-mapping.md`
Parity estimate: **before 99% -> after 100%** for the selected
`CG_BLUE_TEAM_PICKUPS_REGEN`, `CG_BLUE_TEAM_PICKUPS_HASTE`,
`CG_BLUE_TEAM_PICKUPS_INVIS`, `CG_BLUE_TEAM_TIMEHELD_FLAG`, and
`CG_BLUE_TEAM_TIMEHELD_REGEN` ownerdraw set. Repo-wide parity remains **98%**
because unrelated compatibility, source-legacy, online-service, and
packaging surfaces are unchanged.

Completed work:

1. Rechecked the retail `cgamex86.dll` dispatcher, `0x10037F80`
   sparse pickup-count helper, and `0x10039AE0` time-held helper for raw
   ownerdraw cases `0x14A` through `0x14E`.
2. Confirmed blue Regeneration, Haste, and Invisibility pickup ownerdraws
   select the blue team-stat row, normalize through retail pickup selector
   cases `9`, `10`, and `11`, and paint direct integer counts from the parsed
   `scorestats_team` payload.
3. Confirmed blue flag and Regeneration time-held ownerdraws select the blue
   row, accumulate qagame hold-stat seconds through the flag/Regen powerup
   mappings, and format through the recovered `%i:%i%i` minute-second helper.
4. Confirmed the selected rows keep retail TDM/CTF payload membership, route
   through the correct pickup versus time-held draw helpers, refresh
   competitive scorestats through `CG_IsTeamPickupOwnerDraw`, and have no
   value, width, or key callback routes.
5. Added focused structural coverage and refreshed the cgame ownerdraw and
   mapping ledgers for the selected five.

### Task A208: Close selected 325-329 cgame ownerdraw parity [COMPLETED]
Priority: High
Primary areas: `tests/test_cgame_displaycontext_parity.py`,
`docs/reverse-engineering/cg-ownerdrawtype-parity-index.md`,
`docs/reverse-engineering/cgame-mapping.md`
Parity estimate: **before 99% -> after 100%** for the selected
`CG_BLUE_TEAM_PICKUPS_BS`, `CG_BLUE_TEAM_TIMEHELD_QUAD`,
`CG_BLUE_TEAM_TIMEHELD_BS`, `CG_BLUE_TEAM_PICKUPS_FLAG`, and
`CG_BLUE_TEAM_PICKUPS_MEDKIT` ownerdraw set. Repo-wide parity remains **98%**
because unrelated compatibility, source-legacy, online-service, and
packaging surfaces are unchanged.

Completed work:

1. Rechecked the retail `cgamex86.dll` dispatcher, `0x10037F80`
   pickup-count helper, and `0x10039AE0` time-held helper for raw ownerdraw
   cases `0x145` through `0x149`.
2. Confirmed blue Battle Suit, flag, and Medkit pickup ownerdraws select the
   blue team-stat row, normalize through the retail pickup selector, and paint
   direct integer counts from the parsed `scorestats_team` payload.
3. Confirmed blue Quad and Battle Suit time-held ownerdraws select the blue
   row, accumulate qagame hold-stat seconds, and format through the recovered
   `%i:%i%i` minute-second helper.
4. Confirmed the selected rows keep retail TDM/CTF payload membership, route
   through the correct pickup versus time-held draw helpers, refresh
   competitive scorestats through `CG_IsTeamPickupOwnerDraw`, and have no
   value, width, or key callback routes.
5. Added focused structural coverage and refreshed the cgame ownerdraw and
   mapping ledgers for the selected five.

### Task A207: Close selected 308-312 cgame ownerdraw parity [COMPLETED]
Priority: High
Primary areas: `tests/test_cgame_displaycontext_parity.py`,
`docs/reverse-engineering/cg-ownerdrawtype-parity-index.md`,
`docs/reverse-engineering/cgame-mapping.md`
Parity estimate: **before 99% -> after 100%** for the selected
`CG_RED_TEAM_TIMEHELD_HASTE`, `CG_RED_TEAM_TIMEHELD_INVIS`,
`CG_BLUE_FLAGSTATUS`, `CG_BLUE_NAME`, and `CG_BLUE_SCORE` ownerdraw set.
Repo-wide parity remains **98%** because unrelated compatibility,
source-legacy, online-service, and packaging surfaces are unchanged.

Completed work:

1. Rechecked the retail `cgamex86.dll` dispatcher for raw ownerdraw cases
   `0x134` through `0x138`.
2. Confirmed red Haste and Invisibility time-held ownerdraws normalize
   through `0x10039AE0` selector cases `4` and `5`, read the retail
   `scorestats_team` caches, and format with the minute-second helper.
3. Confirmed the blue flag-status, team-name, and score ownerdraws route to
   retail leaves `0x10030A80`, `0x10030090`, and `0x1002FF50` with matching
   team selection, fallback, alignment, and score value callback behavior.
4. Confirmed only the time-held pair refreshes competitive scorestats through
   the team-pickup ownerdraw predicate and that all selected width/key
   callback boundaries match retail.
5. Added focused structural coverage and refreshed the cgame ownerdraw and
   mapping ledgers for the selected five.

### Task A206: Close selected 315-319 cgame ownerdraw parity [COMPLETED]
Priority: High
Primary areas: `tests/test_cgame_displaycontext_parity.py`,
`docs/reverse-engineering/cg-ownerdrawtype-parity-index.md`,
`docs/reverse-engineering/cgame-mapping.md`
Parity estimate: **before 99% -> after 100%** for the selected
`CG_BLUE_BASESTATUS`, `CG_BLUE_PLAYER_COUNT`, `CG_BLUE_CLAN_PLYRS`,
`CG_BLUE_TIMEOUT_COUNT`, and `CG_BLUE_TEAM_MAP_PICKUPS` ownerdraw set.
Repo-wide parity remains **98%** because unrelated compatibility,
source-legacy, online-service, and packaging surfaces are unchanged.

Completed work:

1. Rechecked the retail `cgamex86.dll` dispatcher for raw ownerdraw cases
   `0x13B` through `0x13F`.
2. Confirmed `CG_BLUE_BASESTATUS` stays on the shared
   `0x10030A80` flag/base-status helper with blue/base semantics and the
   expected competitive refresh boundary.
3. Confirmed `CG_BLUE_PLAYER_COUNT`, `CG_BLUE_CLAN_PLYRS`, and
   `CG_BLUE_TIMEOUT_COUNT` preserve the retail player-count formatter,
   round-family players-remaining gate, positive-team-size timeout gate,
   blue cached team-count source, blue timeout source, and alignment paths.
4. Confirmed `CG_BLUE_TEAM_MAP_PICKUPS` enters the zero-offset blue aggregate
   pickup strip, consumes the parsed blue `scorestats_team` row, and refreshes
   competitive scorestats through `CG_IsTeamPickupOwnerDraw`.
5. Added focused structural coverage and refreshed the cgame ownerdraw and
   mapping ledgers for the selected five.

### Task A205: Close selected 320-324 cgame ownerdraw parity [COMPLETED]
Priority: High
Primary areas: `tests/test_cgame_displaycontext_parity.py`,
`docs/reverse-engineering/cg-ownerdrawtype-parity-index.md`,
`docs/reverse-engineering/cgame-mapping.md`
Parity estimate: **before 99% -> after 100%** for the selected
`CG_BLUE_TEAM_PICKUPS_RA`, `CG_BLUE_TEAM_PICKUPS_YA`,
`CG_BLUE_TEAM_PICKUPS_GA`, `CG_BLUE_TEAM_PICKUPS_MH`, and
`CG_BLUE_TEAM_PICKUPS_QUAD` ownerdraw set. Repo-wide parity remains **98%**
because unrelated compatibility, source-legacy, online-service, and
packaging surfaces are unchanged.

Completed work:

1. Rechecked the retail `cgamex86.dll` dispatcher and `0x10037F80`
   team-pickup helper for raw ownerdraw cases `0x140` through `0x144`.
2. Confirmed the selected blue pickup ownerdraws normalize from
   `CG_BLUE_TEAM_MAP_PICKUPS` to offsets `1` through `5`, consume the blue
   row of parsed `scorestats_team` fields, and paint RA/YA/GA/MH/Quad counts
   through the retail direct integer text path.
3. Confirmed qagame publishes red then blue team-stat rows, cgame parses both
   rows into `cg.teamScoreStats.values`, and the retail TDM/CTF field order
   backs the selected RA/YA/GA/MH/Quad cache slots.
4. Confirmed the selected rows route through `CG_DrawTeamPickupOwnerDraw`,
   refresh competitive scorestats through `CG_IsTeamPickupOwnerDraw`, and
   have no value, width, or key callback routes.
5. Added focused structural coverage and refreshed the cgame ownerdraw and
   mapping ledgers for the selected five.

### Task A204: Close selected 303-307 cgame ownerdraw parity [COMPLETED]
Priority: High
Primary areas: `src/code/cgame/cg_servercmds.c`,
`tests/test_cgame_displaycontext_parity.py`,
`docs/reverse-engineering/cg-ownerdrawtype-parity-index.md`,
`docs/reverse-engineering/cgame-mapping.md`
Parity estimate: **before 96% -> after 100%** for the selected
`CG_RED_TEAM_PICKUPS_REGEN`, `CG_RED_TEAM_PICKUPS_HASTE`,
`CG_RED_TEAM_PICKUPS_INVIS`, `CG_RED_TEAM_TIMEHELD_FLAG`, and
`CG_RED_TEAM_TIMEHELD_REGEN` ownerdraw set. Repo-wide parity remains
**98%** because unrelated compatibility, source-legacy, online-service, and
packaging surfaces are unchanged.

Completed work:

1. Rechecked the retail `cgamex86.dll` dispatcher, pickup helper
   `0x10037F80`, time-held helper `0x10039AE0`, retail selector tables, and
   team scoreboard parsers for raw ownerdraw cases `0x12f` through `0x133`.
2. Confirmed red Regen/Haste/Invis pickup ownerdraws normalize through the
   sparse retail selector to caches `data_10aa687c`, `data_10aa6880`, and
   `data_10aa6884`, then paint through the direct integer text path.
3. Confirmed red flag and Regeneration time-held ownerdraws normalize through
   the retail time-held selector to `data_10aa68a4` and `data_10aa6898`, then
   use the shared `%i:%i%i` minute-second formatter.
4. Corrected the source TDM/CTF scoreboard aggregate header order so retail
   scoreboard payloads populate the same sparse cache slots; the synthetic
   `CG_TEAMSTAT_MAP_PICKUPS` slot remains limited to the compact
   `scorestats_team` path.
5. Added focused structural coverage and refreshed the cgame ownerdraw and
   mapping ledgers for the selected five.

### Task A203: Close selected 282 cgame ownerdraw parity [COMPLETED]
Priority: High
Primary areas: `tests/test_cgame_displaycontext_parity.py`,
`docs/reverse-engineering/cg-ownerdrawtype-parity-index.md`,
`docs/reverse-engineering/cgame-mapping.md`
Parity estimate: **before 99% -> after 100%** for
`CG_2ND_PLYR_TIER`. Repo-wide parity remains **98%** because unrelated
compatibility, source-legacy, online-service, and packaging surfaces are
unchanged.

Completed work:

1. Rechecked the retail `cgamex86.dll` ownerdraw target set for raw ownerdraw
   `0x11A` and confirmed `CG_2ND_PLYR_TIER` has no retail draw helper route.
2. Confirmed source keeps `CG_2ND_PLYR_TIER` as an explicit direct no-op with
   the neighboring `CG_2ND_PLYR_PR` boundary while leaving the broad
   second-player resolver range intact for adjacent ids.
3. Confirmed compact scorestats may still parse progression tier for data
   parity, but the tier ownerdraw has no placement guard, metric dispatcher,
   competitive refresh, value, width, key, or direct draw route.
4. Added focused structural coverage and refreshed the cgame ownerdraw and
   mapping ledgers for the selected id.

### Task A202: Close selected 277-281 cgame ownerdraw parity [COMPLETED]
Priority: High
Primary areas: `tests/test_cgame_displaycontext_parity.py`,
`docs/reverse-engineering/cg-ownerdrawtype-parity-index.md`,
`docs/reverse-engineering/cgame-mapping.md`
Parity estimate: **before 99% -> after 100%** for the selected
`CG_2ND_PLYR_AVG_PICKUP_TIME_MH`, `CG_2ND_PLYR_EXCELLENT`,
`CG_2ND_PLYR_IMPRESSIVE`, `CG_2ND_PLYR_HUMILIATION`, and
`CG_2ND_PLYR_PR` ownerdraw set. Repo-wide parity remains **98%** because
unrelated compatibility, source-legacy, online-service, and packaging surfaces
are unchanged.

Completed work:

1. Rechecked the retail `cgamex86.dll` dispatcher, pickup-average helper
   `0x10037730`, award-count helper `0x10037990`, and raw no-route boundary
   for ownerdraw cases `0x115` through `0x119`.
2. Confirmed `CG_2ND_PLYR_AVG_PICKUP_TIME_MH` selects slot 1, consumes the
   compact MH pickup-average scorestats payload, paints through retail
   `%3.2f`, and preserves the `"-"` fallback when the MH pickup count is zero.
3. Confirmed `CG_2ND_PLYR_EXCELLENT`, `CG_2ND_PLYR_IMPRESSIVE`, and
   `CG_2ND_PLYR_HUMILIATION` select slot 1, consume parsed duel-score award
   counts, and paint through the retail `%d` formatter.
4. Confirmed `CG_2ND_PLYR_PR` remains an explicit no-op ownerdraw boundary:
   progression PR is still parsed from compact scorestats, but retail has no
   raw `0x119` draw helper, placement guard, competitive refresh, value,
   width, or key callback route.
5. Added focused structural coverage and refreshed the cgame ownerdraw and
   mapping ledgers for the selected five.

### Task A201: Close selected 237-241 cgame ownerdraw parity [COMPLETED]
Priority: High
Primary areas: `tests/test_cgame_displaycontext_parity.py`,
`docs/reverse-engineering/cg-ownerdrawtype-parity-index.md`,
`docs/reverse-engineering/cgame-mapping.md`
Parity estimate: **before 99% -> after 100%** for the selected
`CG_2ND_PLYR_SHOTS_RG`, `CG_2ND_PLYR_SHOTS_PG`,
`CG_2ND_PLYR_SHOTS_BFG`, `CG_2ND_PLYR_SHOTS_CG`, and
`CG_2ND_PLYR_SHOTS_NG` ownerdraw set. Repo-wide parity remains **98%**
because unrelated compatibility, source-legacy, online-service, and
packaging surfaces are unchanged.

Completed work:

1. Rechecked the retail `cgamex86.dll` dispatcher, `0x10036B00`
   weapon-shot leaf, and `0x1002E2B0` weapon resolver for raw ownerdraw
   cases `0xed` through `0xf1`.
2. Confirmed the selected second-player shot ownerdraws select slot 1,
   resolve RG/PG/BFG/CG/NG to weapon indexes `7`, `8`, `9`, `0xd`, and
   `0xb`, read `data_10A6038C`, and paint through the retail `%d`
   formatter.
3. Confirmed source normalization, metric dispatch, qagame scorestats
   emission, cgame scorestats parsing, competitive placement refresh, and
   ownerdraw/value/width/key callback absence match the retail wiring.
4. Added focused structural coverage and refreshed the cgame ownerdraw and
   mapping ledgers for the selected five.

### Task A200: Close selected 272-276 cgame ownerdraw parity [COMPLETED]
Priority: High
Primary areas: `tests/test_cgame_displaycontext_parity.py`,
`docs/reverse-engineering/cg-ownerdrawtype-parity-index.md`,
`docs/reverse-engineering/cgame-mapping.md`
Parity estimate: **before 99% -> after 100%** for the selected
`CG_2ND_PLYR_PICKUPS_GA`, `CG_2ND_PLYR_PICKUPS_MH`,
`CG_2ND_PLYR_AVG_PICKUP_TIME_RA`, `CG_2ND_PLYR_AVG_PICKUP_TIME_YA`,
and `CG_2ND_PLYR_AVG_PICKUP_TIME_GA` ownerdraw set. Repo-wide parity
remains **98%** because unrelated compatibility, source-legacy,
online-service, and packaging surfaces are unchanged.

Completed work:

1. Rechecked the retail `cgamex86.dll` dispatcher, pickup-count helper
   `0x10036EB0`, and pickup-average helper `0x10037730` for raw ownerdraw
   cases `0x110` through `0x114`.
2. Confirmed `CG_2ND_PLYR_PICKUPS_GA` and `CG_2ND_PLYR_PICKUPS_MH` select
   slot 1, consume compact GA/MH pickup-count `scorestats` payloads, and paint
   through the retail `%d` formatter.
3. Confirmed `CG_2ND_PLYR_AVG_PICKUP_TIME_RA`,
   `CG_2ND_PLYR_AVG_PICKUP_TIME_YA`, and
   `CG_2ND_PLYR_AVG_PICKUP_TIME_GA` select slot 1, consume compact pickup
   average payloads, paint through retail `%3.2f`, and preserve the retail
   `"-"` fallback when the associated pickup count is zero.
4. Confirmed source normalization, placement metric dispatch, qagame
   scorestats emission, cgame scorestats parsing, competitive placement
   refresh, and ownerdraw/value/width/key callback absence match the retail
   wiring.
5. Added focused structural coverage and refreshed the cgame ownerdraw and
   mapping ledgers for the selected five.

### Task A198: Close selected 232-236 cgame ownerdraw parity [COMPLETED]
Priority: High
Primary areas: `tests/test_cgame_displaycontext_parity.py`,
`docs/reverse-engineering/cg-ownerdrawtype-parity-index.md`,
`docs/reverse-engineering/cgame-mapping.md`
Parity estimate: **before 99% -> after 100%** for the selected
`CG_2ND_PLYR_SHOTS_MG`, `CG_2ND_PLYR_SHOTS_SG`,
`CG_2ND_PLYR_SHOTS_GL`, `CG_2ND_PLYR_SHOTS_RL`, and
`CG_2ND_PLYR_SHOTS_LG` ownerdraw set. Repo-wide parity remains **98%**
because unrelated compatibility, source-legacy, online-service, and
packaging surfaces are unchanged.

Completed work:

1. Rechecked the retail `cgamex86.dll` dispatcher, `0x10036B00`
   weapon-shot leaf, and `0x1002E2B0` weapon resolver for raw ownerdraw
   cases `0xe8` through `0xec`.
2. Confirmed the selected second-player shot ownerdraws select slot 1,
   resolve MG/SG/GL/RL/LG to weapon indexes `2`, `3`, `4`, `5`, and `6`,
   read `data_10A6038C`, and paint through the retail `%d` formatter.
3. Confirmed source normalization, metric dispatch, qagame scorestats
   emission, cgame scorestats parsing, competitive placement refresh, and
   ownerdraw/value/width/key callback absence match the retail wiring.
4. Added focused structural coverage and refreshed the cgame ownerdraw and
   mapping ledgers for the selected five.

### Task A199: Close selected 267-271 cgame ownerdraw parity [COMPLETED]
Priority: High
Primary areas: `tests/test_cgame_displaycontext_parity.py`,
`docs/reverse-engineering/cg-ownerdrawtype-parity-index.md`,
`docs/reverse-engineering/cgame-mapping.md`
Parity estimate: **before 99% -> after 100%** for the selected
`CG_2ND_PLYR_ACC_PL`, `CG_2ND_PLYR_ACC_HMG`, `CG_2ND_PLYR_PICKUPS`,
`CG_2ND_PLYR_PICKUPS_RA`, and `CG_2ND_PLYR_PICKUPS_YA` ownerdraw set.
Repo-wide parity remains **98%** because unrelated compatibility,
source-legacy, online-service, and packaging surfaces are unchanged.

Completed work:

1. Rechecked the retail `cgamex86.dll` dispatcher, HLIL weapon-accuracy leaf,
   pickup-count/summary leaf, and shared placement weapon resolver for raw
   ownerdraw cases `0x10B` through `0x10F`.
2. Confirmed `CG_2ND_PLYR_ACC_PL` and `CG_2ND_PLYR_ACC_HMG` stay on the
   pre-switch `0x10036D60` accuracy helper, normalize through the retail
   `0x1002E2B0` weapon resolver, preserve the Quake Live enum gaps for PL/HMG,
   and consume hit/shot-derived `scorestats` accuracy payloads.
3. Confirmed `CG_2ND_PLYR_PICKUPS`, `CG_2ND_PLYR_PICKUPS_RA`, and
   `CG_2ND_PLYR_PICKUPS_YA` stay on the pre-switch `0x10036EB0` pickup helper,
   select slot 1, and consume compact RA/YA/GA/MH pickup count and average
   scorestats payloads.
4. Confirmed the selected pickup summary/count ownerdraws preserve retail
   placement summary icon/text layout, direct `%d` count formatting for RA/YA,
   competitive refresh, and absence from direct `CG_OwnerDraw`, value, width,
   and key callback routes.
5. Added focused structural coverage for constants, retail target-group
   membership, HLIL resolver/cache/format/layout signals, server/client
   `scorestats` transport, weapon and pickup mapping, dispatcher routing,
   callback absence, and competitive refresh wiring.
6. Refreshed the cgame ownerdraw and mapping ledgers for the selected five.

### Task A197: Close selected 298-302 cgame ownerdraw parity [COMPLETED]
Priority: High
Primary areas: `tests/test_cgame_displaycontext_parity.py`,
`docs/reverse-engineering/cg-ownerdrawtype-parity-index.md`,
`docs/reverse-engineering/cgame-mapping.md`
Parity estimate: **before 99% -> after 100%** for the selected
`CG_RED_TEAM_PICKUPS_BS`, `CG_RED_TEAM_TIMEHELD_QUAD`,
`CG_RED_TEAM_TIMEHELD_BS`, `CG_RED_TEAM_PICKUPS_FLAG`, and
`CG_RED_TEAM_PICKUPS_MEDKIT` ownerdraw set. Repo-wide parity remains
**98%** because unrelated compatibility, source-legacy, online-service, and
packaging surfaces are unchanged.

Completed work:

1. Rechecked the retail `cgamex86.dll` dispatcher, `0x10037F80`
   pickup-count leaf, and `0x10039AE0` time-held leaf for raw ownerdraw
   cases `0x12a` through `0x12e`.
2. Confirmed `CG_RED_TEAM_PICKUPS_BS`, `CG_RED_TEAM_PICKUPS_FLAG`, and
   `CG_RED_TEAM_PICKUPS_MEDKIT` stay in the `arg5 - 0x124` retail pickup
   range and paint the direct red team integer fields for offsets `6`,
   `9`, and `0xa`.
3. Confirmed `CG_RED_TEAM_TIMEHELD_QUAD` and `CG_RED_TEAM_TIMEHELD_BS`
   route through `0x10039AE0`, resolve offsets `0` and `1`, and format
   seconds through the recovered `%i:%i%i` minute-second helper.
4. Confirmed source metadata, team-scorestats transports, pickup/time-held
   dispatcher split, competitive refresh, and value/width/key callback
   absence match retail wiring.
5. Added focused structural coverage and refreshed the cgame ownerdraw and
   mapping ledgers for the selected five.

### Task A196: Close selected 227-231 cgame ownerdraw parity [COMPLETED]
Priority: High
Primary areas: `tests/test_cgame_displaycontext_parity.py`,
`docs/reverse-engineering/cg-ownerdrawtype-parity-index.md`,
`docs/reverse-engineering/cgame-mapping.md`
Parity estimate: **before 99% -> after 100%** for the selected
`CG_2ND_PLYR_HITS_BFG`, `CG_2ND_PLYR_HITS_CG`,
`CG_2ND_PLYR_HITS_NG`, `CG_2ND_PLYR_HITS_PL`, and
`CG_2ND_PLYR_HITS_HMG` ownerdraw set. Repo-wide parity remains **98%**
because unrelated compatibility, source-legacy, online-service, and
packaging surfaces are unchanged.

Completed work:

1. Rechecked the retail `cgamex86.dll` dispatcher, `0x100369D0`
   weapon-hit leaf, and `0x1002E2B0` weapon resolver for raw ownerdraw
   cases `0xe3` through `0xe7`.
2. Confirmed the selected second-player hit ownerdraws select slot 1,
   resolve BFG/CG/NG/PL/HMG to weapon indexes `9`, `0xd`, `0xb`, `0xc`,
   and `0xe`, read `data_10A603CC`, and paint through the retail `%d`
   formatter.
3. Confirmed source normalization, metric dispatch, qagame scorestats
   emission, cgame scorestats parsing, competitive placement refresh, and
   ownerdraw/value/width/key callback absence match the retail wiring.
4. Added focused structural coverage and refreshed the cgame ownerdraw and
   mapping ledgers for the selected five.

### Task A195: Close selected 293-297 cgame ownerdraw parity [COMPLETED]
Priority: High
Primary areas: `tests/test_cgame_displaycontext_parity.py`,
`docs/reverse-engineering/cg-ownerdrawtype-parity-index.md`,
`docs/reverse-engineering/cgame-mapping.md`
Parity estimate: **before 99% -> after 100%** for the selected
`CG_RED_TEAM_PICKUPS_RA`, `CG_RED_TEAM_PICKUPS_YA`,
`CG_RED_TEAM_PICKUPS_GA`, `CG_RED_TEAM_PICKUPS_MH`, and
`CG_RED_TEAM_PICKUPS_QUAD` ownerdraw set. Repo-wide parity remains **98%**
because unrelated compatibility, source-legacy, online-service, and
packaging surfaces are unchanged.

Completed work:

1. Rechecked the retail `cgamex86.dll` dispatcher and `0x10037F80`
   team-pickup leaf for raw ownerdraw cases `0x125` through `0x129`.
2. Confirmed all five selected ownerdraws stay in the `arg5 - 0x124`
   retail range, resolve to offsets `1` through `5`, and paint the direct
   red team pickup-count fields through the common integer text path.
3. Confirmed source metadata maps the selected rows to
   `CG_TEAMSTAT_PICKUPS_RA`, `CG_TEAMSTAT_PICKUPS_YA`,
   `CG_TEAMSTAT_PICKUPS_GA`, `CG_TEAMSTAT_PICKUPS_MH`, and
   `CG_TEAMSTAT_PICKUPS_QUAD`, backed by the retail team-scorestats header
   and `scorestats_team` transports.
4. Confirmed the selected rows route through `CG_DrawTeamPickupOwnerDraw`,
   refresh competitive scorestats through `CG_IsTeamPickupOwnerDraw`, and
   have no value, width, key, or time-held callback routes.
5. Added focused structural coverage and refreshed the cgame ownerdraw and
   mapping ledgers for the selected five.

### Task A194: Close selected 262-266 cgame ownerdraw parity [COMPLETED]
Priority: High
Primary areas: `tests/test_cgame_displaycontext_parity.py`,
`docs/reverse-engineering/cg-ownerdrawtype-parity-index.md`,
`docs/reverse-engineering/cgame-mapping.md`
Parity estimate: **before 99% -> after 100%** for the selected
`CG_2ND_PLYR_ACC_RG`, `CG_2ND_PLYR_ACC_PG`, `CG_2ND_PLYR_ACC_BFG`,
`CG_2ND_PLYR_ACC_CG`, and `CG_2ND_PLYR_ACC_NG` ownerdraw set. Repo-wide
parity remains **98%** because unrelated compatibility, source-legacy,
online-service, and packaging surfaces are unchanged.

Completed work:

1. Rechecked the retail `cgamex86.dll` dispatcher and HLIL weapon-accuracy
   leaf for raw ownerdraw cases `0x106` through `0x10A`.
2. Confirmed all five selected ownerdraws stay on the pre-switch `0x10036D60`
   accuracy helper, normalize through the retail `0x1002E2B0` weapon resolver,
   and consume hit/shot-derived `scorestats` accuracy payloads.
3. Confirmed the selected accuracy ownerdraws resolve to Railgun, Plasmagun,
   BFG, Chaingun, and Nailgun, preserving the Quake Live enum gaps for CG and
   NG.
4. Confirmed all five selected ownerdraws preserve the retail best-row white
   `0.8` alpha override, refresh the competitive score cache, draw through the
   placement metric dispatcher instead of direct `CG_OwnerDraw` cases, and
   have no value, width, or key callback routes.
5. Added focused structural coverage for constants, retail target-group
   membership, HLIL resolver/cache/format/color/paint signals, server/client
   `scorestats` transport, weapon mapping, dispatcher routing, callback
   absence, and competitive refresh wiring.
6. Refreshed the cgame ownerdraw and mapping ledgers for the selected five.

### Task A193: Close selected 222-226 cgame ownerdraw parity [COMPLETED]
Priority: High
Primary areas: `tests/test_cgame_displaycontext_parity.py`,
`docs/reverse-engineering/cg-ownerdrawtype-parity-index.md`,
`docs/reverse-engineering/cgame-mapping.md`
Parity estimate: **before 99% -> after 100%** for the selected
`CG_2ND_PLYR_HITS_GL`, `CG_2ND_PLYR_HITS_RL`,
`CG_2ND_PLYR_HITS_LG`, `CG_2ND_PLYR_HITS_RG`, and
`CG_2ND_PLYR_HITS_PG` ownerdraw set. Repo-wide parity remains **98%**
because unrelated compatibility, source-legacy, online-service, and
packaging surfaces are unchanged.

Completed work:

1. Rechecked the retail `cgamex86.dll` dispatcher, `0x100369D0`
   weapon-hit leaf, and `0x1002E2B0` weapon resolver for raw ownerdraw
   cases `0xde` through `0xe2`.
2. Confirmed the selected second-player hit ownerdraws select slot 1,
   resolve GL/RL/LG/RG/PG to weapon indexes `4`, `5`, `6`, `7`, and `8`,
   read `data_10A603CC`, and paint through the retail `%d` formatter.
3. Confirmed source normalization, metric dispatch, qagame scorestats
   emission, cgame scorestats parsing, competitive placement refresh, and
   ownerdraw/value/width/key callback absence match the retail wiring.
4. Added focused structural coverage and refreshed the cgame ownerdraw and
   mapping ledgers for the selected five.

### Task A192: Close selected 257-261 cgame ownerdraw parity [COMPLETED]
Priority: High
Primary areas: `tests/test_cgame_displaycontext_parity.py`,
`docs/reverse-engineering/cg-ownerdrawtype-parity-index.md`,
`docs/reverse-engineering/cgame-mapping.md`
Parity estimate: **before 99% -> after 100%** for the selected
`CG_2ND_PLYR_ACC_MG`, `CG_2ND_PLYR_ACC_SG`, `CG_2ND_PLYR_ACC_GL`,
`CG_2ND_PLYR_ACC_RL`, and `CG_2ND_PLYR_ACC_LG` ownerdraw set. Repo-wide
parity remains **98%** because unrelated compatibility, source-legacy,
online-service, and packaging surfaces are unchanged.

Completed work:

1. Rechecked the retail `cgamex86.dll` dispatcher and HLIL weapon-accuracy
   leaf for raw ownerdraw cases `0x101` through `0x105`.
2. Confirmed all five selected ownerdraws stay on the pre-switch `0x10036D60`
   accuracy helper, normalize through the retail `0x1002E2B0` weapon resolver,
   and consume hit/shot-derived `scorestats` accuracy payloads.
3. Confirmed the selected accuracy ownerdraws resolve to Machinegun, Shotgun,
   Grenade Launcher, Rocket Launcher, and Lightning Gun.
4. Confirmed all five selected ownerdraws preserve the retail best-row white
   `0.8` alpha override, refresh the competitive score cache, draw through the
   placement metric dispatcher instead of direct `CG_OwnerDraw` cases, and
   have no value, width, or key callback routes.
5. Added focused structural coverage for constants, retail target-group
   membership, HLIL resolver/cache/format/color/paint signals, server/client
   `scorestats` transport, weapon mapping, dispatcher routing, callback
   absence, and competitive refresh wiring.
6. Refreshed the cgame ownerdraw and mapping ledgers for the selected five.

### Task A191: Close selected 288-292 cgame ownerdraw parity [COMPLETED]
Priority: High
Primary areas: `tests/test_cgame_displaycontext_parity.py`,
`docs/reverse-engineering/cg-ownerdrawtype-parity-index.md`,
`docs/reverse-engineering/cgame-mapping.md`
Parity estimate: **before 99% -> after 100%** for the selected
`CG_RED_BASESTATUS`, `CG_RED_PLAYER_COUNT`, `CG_RED_CLAN_PLYRS`,
`CG_RED_TIMEOUT_COUNT`, and `CG_RED_TEAM_MAP_PICKUPS` ownerdraw set.
Repo-wide parity remains **98%** because unrelated compatibility,
source-legacy, online-service, and packaging surfaces are unchanged.

Completed work:

1. Rechecked the retail `cgamex86.dll` dispatcher paths for raw ownerdraw
   cases `0x120` through `0x124`.
2. Confirmed red base status shares `0x10030A80` with flag status, red
   player count routes to `0x100333C0`, red clan-player count routes to
   `0x100335F0` behind the players-remaining gate, and red timeout count
   routes to `0x10033530` behind the positive team-size gate.
3. Confirmed red map pickups enter the `0x10037F80` aggregate pickup strip
   as the zero-offset red range case, preserving parsed `scorestats_team`
   fields, icon selection, visible positive-count filtering, and the retail
   `25`/`28` slot strides.
4. Added focused structural coverage and refreshed the cgame ownerdraw and
   mapping ledgers for the selected five.

### Task A190: Close selected 217-221 cgame ownerdraw parity [COMPLETED]
Priority: High
Primary areas: `tests/test_cgame_displaycontext_parity.py`,
`docs/reverse-engineering/cg-ownerdrawtype-parity-index.md`,
`docs/reverse-engineering/cgame-mapping.md`
Parity estimate: **before 99% -> after 100%** for the selected
`CG_2ND_PLYR_FRAGS_NG`, `CG_2ND_PLYR_FRAGS_PL`,
`CG_2ND_PLYR_FRAGS_HMG`, `CG_2ND_PLYR_HITS_MG`, and
`CG_2ND_PLYR_HITS_SG` ownerdraw set. Repo-wide parity remains **98%**
because unrelated compatibility, source-legacy, online-service, and
packaging surfaces are unchanged.

Completed work:

1. Rechecked the retail `cgamex86.dll` dispatcher, `0x100368A0`
   weapon-frag leaf, `0x100369D0` weapon-hit leaf, and `0x1002E2B0`
   weapon resolver for raw ownerdraw cases `0xd9` through `0xdd`.
2. Confirmed `CG_2ND_PLYR_FRAGS_NG`, `CG_2ND_PLYR_FRAGS_PL`, and
   `CG_2ND_PLYR_FRAGS_HMG` select slot 1, resolve to weapon indexes
   `0xb`, `0xc`, and `0xe`, read `data_10A6030C`, and paint through
   the retail `%d` formatter.
3. Confirmed `CG_2ND_PLYR_HITS_MG` and `CG_2ND_PLYR_HITS_SG` select
   slot 1, resolve to weapon indexes `2` and `3`, read
   `data_10A603CC`, and paint through the retail `%d` formatter.
4. Confirmed source normalization, metric dispatch, qagame scorestats
   emission, cgame scorestats parsing, competitive placement refresh, and
   ownerdraw/value/width/key callback absence match the retail wiring across
   the frag-order and accuracy-order payload split.
5. Added focused structural coverage and refreshed the cgame ownerdraw and
   mapping ledgers for the selected five.

### Task A189: Close selected 252-256 cgame ownerdraw parity [COMPLETED]
Priority: High
Primary areas: `tests/test_cgame_displaycontext_parity.py`,
`docs/reverse-engineering/cg-ownerdrawtype-parity-index.md`,
`docs/reverse-engineering/cgame-mapping.md`
Parity estimate: **before 99% -> after 100%** for the selected
`CG_2ND_PLYR_DMG_BFG`, `CG_2ND_PLYR_DMG_CG`, `CG_2ND_PLYR_DMG_NG`,
`CG_2ND_PLYR_DMG_PL`, and `CG_2ND_PLYR_DMG_HMG` ownerdraw set. Repo-wide
parity remains **98%** because unrelated compatibility, source-legacy,
online-service, and packaging surfaces are unchanged.

Completed work:

1. Rechecked the retail `cgamex86.dll` dispatcher and HLIL damage leaf for raw
   ownerdraw cases `0xfc` through `0x100`.
2. Confirmed all five selected ownerdraws stay on the pre-switch `0x10036C30`
   damage helper, normalize through the retail `0x1002E2B0` weapon resolver,
   and consume the parsed `scorestats` damage payload.
3. Confirmed the selected damage ownerdraws resolve to BFG, Chaingun, Nailgun,
   Proximity Launcher, and Heavy Machinegun, preserving the Quake Live enum
   gaps for CG/NG/PL/HMG.
4. Confirmed all five selected ownerdraws refresh the competitive score cache,
   draw through the placement metric dispatcher instead of direct
   `CG_OwnerDraw` cases, and have no value, width, or key callback routes.
5. Added focused structural coverage for constants, retail target-group
   membership, HLIL resolver/cache/format/paint signals, server/client
   `scorestats` transport, weapon mapping, dispatcher routing, callback
   absence, and competitive refresh wiring.
6. Refreshed the cgame ownerdraw and mapping ledgers for the selected five.

### Task A188: Close selected 212-216 cgame ownerdraw parity [COMPLETED]
Priority: High
Primary areas: `tests/test_cgame_displaycontext_parity.py`,
`docs/reverse-engineering/cg-ownerdrawtype-parity-index.md`,
`docs/reverse-engineering/cgame-mapping.md`
Parity estimate: **before 99% -> after 100%** for the selected
`CG_2ND_PLYR_FRAGS_LG`, `CG_2ND_PLYR_FRAGS_RG`,
`CG_2ND_PLYR_FRAGS_PG`, `CG_2ND_PLYR_FRAGS_BFG`, and
`CG_2ND_PLYR_FRAGS_CG` ownerdraw set. Repo-wide parity remains **98%**
because unrelated compatibility, source-legacy, online-service, and
packaging surfaces are unchanged.

Completed work:

1. Rechecked the retail `cgamex86.dll` dispatcher, `0x100368A0`
   weapon-frag leaf, and `0x1002E2B0` weapon resolver for raw ownerdraw
   cases `0xd4` through `0xd8`.
2. Confirmed the selected second-player frag ownerdraws select slot 1,
   resolve LG/RG/PG/BFG/CG to weapon indexes `6`, `7`, `8`, `9`, and
   `0xd`, read `data_10A6030C`, and paint through the retail `%d`
   formatter.
3. Confirmed source normalization, metric dispatch, qagame scorestats
   emission, cgame scorestats parsing, competitive placement refresh, and
   ownerdraw/value/width/key callback absence match the retail wiring.
4. Added focused structural coverage and refreshed the cgame ownerdraw and
   mapping ledgers for the selected five.

### Task A187: Close selected 247-251 cgame ownerdraw parity [COMPLETED]
Priority: High
Primary areas: `tests/test_cgame_displaycontext_parity.py`,
`docs/reverse-engineering/cg-ownerdrawtype-parity-index.md`,
`docs/reverse-engineering/cgame-mapping.md`
Parity estimate: **before 99% -> after 100%** for the selected
`CG_2ND_PLYR_DMG_GL`, `CG_2ND_PLYR_DMG_RL`, `CG_2ND_PLYR_DMG_LG`,
`CG_2ND_PLYR_DMG_RG`, and `CG_2ND_PLYR_DMG_PG` ownerdraw set. Repo-wide
parity remains **98%** because unrelated compatibility, source-legacy,
online-service, and packaging surfaces are unchanged.

Completed work:

1. Rechecked the retail `cgamex86.dll` dispatcher and HLIL damage leaf for raw
   ownerdraw cases `0xf7` through `0xfb`.
2. Confirmed all five selected ownerdraws stay on the pre-switch `0x10036C30`
   damage helper, normalize through the retail `0x1002E2B0` weapon resolver,
   and consume the parsed `scorestats` damage payload.
3. Confirmed the selected damage ownerdraws resolve to Grenade Launcher,
   Rocket Launcher, Lightning Gun, Railgun, and Plasmagun in the same order as
   the qagame producer and cgame parser.
4. Confirmed all five selected ownerdraws refresh the competitive score cache,
   draw through the placement metric dispatcher instead of direct
   `CG_OwnerDraw` cases, and have no value, width, or key callback routes.
5. Added focused structural coverage for constants, retail target-group
   membership, HLIL resolver/cache/format/paint signals, server/client
   `scorestats` transport, weapon mapping, dispatcher routing, callback
   absence, and competitive refresh wiring.
6. Refreshed the cgame ownerdraw and mapping ledgers for the selected five.

### Task A186: Close selected 283-287 cgame ownerdraw parity [COMPLETED]
Priority: High
Primary areas: `src/code/cgame/cg_newdraw.c`,
`tests/test_cgame_displaycontext_parity.py`,
`docs/reverse-engineering/cg-ownerdrawtype-parity-index.md`,
`docs/reverse-engineering/cgame-mapping.md`
Parity estimate: **before 99% -> after 100%** for the selected
`CG_RED_FLAGSTATUS`, `CG_RED_SCORE`, `CG_RED_NAME`,
`CG_RED_OWNED_FLAGS`, and `CG_RED_AVG_PING` ownerdraw set. Repo-wide
parity remains **98%** because unrelated compatibility, source-legacy,
online-service, and packaging surfaces are unchanged.

Completed work:

1. Rechecked the retail `cgamex86.dll` dispatcher and HLIL leaves for raw
   ownerdraw cases `0x11b` through `0x11f`.
2. Confirmed `CG_RED_FLAGSTATUS` stays on the shared team flag/base-status
   icon leaf, including red status selection and shader fallback behavior.
3. Confirmed `CG_RED_SCORE` stays on the aligned team-score leaf and remains
   the only selected ownerdraw with a `CG_GetValue` callback route.
4. Confirmed `CG_RED_NAME` stays on the aligned team-name leaf with the
   configured-name and default-name fallback path.
5. Confirmed `CG_RED_OWNED_FLAGS` stays behind the retail Domination /
   Attack-Defend gate before drawing the red owned-point count.
6. Restored the shared `CG_DrawTeamAveragePing` leaf to retail behavior:
   matching score rows are averaged without a negative-ping skip, no matching
   rows still paint `(0)`, thresholds are `>40` and `>80`, alpha is `0.8`,
   and text formats as `(%d)`.
7. Added focused structural coverage for constants, retail target-group
   membership, HLIL branch/format/color signals, local dispatcher routes,
   value/width/key callback membership, competitive-refresh absence, and the
   selected ownerdraw ledger rows.
8. Refreshed the cgame ownerdraw and mapping ledgers for the selected five.

### Task A185: Close selected 242-246 cgame ownerdraw parity [COMPLETED]
Priority: High
Primary areas: `tests/test_cgame_displaycontext_parity.py`,
`docs/reverse-engineering/cg-ownerdrawtype-parity-index.md`,
`docs/reverse-engineering/cgame-mapping.md`
Parity estimate: **before 99% -> after 100%** for the selected
`CG_2ND_PLYR_SHOTS_PL`, `CG_2ND_PLYR_SHOTS_HMG`, `CG_2ND_PLYR_DMG_G`,
`CG_2ND_PLYR_DMG_MG`, and `CG_2ND_PLYR_DMG_SG` ownerdraw set. Repo-wide
parity remains **98%** because unrelated compatibility, source-legacy,
online-service, and packaging surfaces are unchanged.

Completed work:

1. Rechecked the retail `cgamex86.dll` dispatcher and HLIL leaves for raw
   ownerdraw cases `0xf2` through `0xf6`.
2. Confirmed `CG_2ND_PLYR_SHOTS_PL` and `CG_2ND_PLYR_SHOTS_HMG` stay on the
   pre-switch `0x10036B00` shot-count helper, normalize through the retail
   weapon resolver, and consume the parsed `scorestats` shot-count payload.
3. Confirmed `CG_2ND_PLYR_DMG_G`, `CG_2ND_PLYR_DMG_MG`, and
   `CG_2ND_PLYR_DMG_SG` stay on the pre-switch `0x10036C30` damage helper,
   normalize to Gauntlet/Machinegun/Shotgun, and consume the parsed
   `scorestats` damage payload.
4. Confirmed all five selected ownerdraws refresh the competitive score cache,
   draw through the placement metric dispatcher instead of direct
   `CG_OwnerDraw` cases, and have no value, width, or key callback routes.
5. Added focused structural coverage for constants, retail target-group
   membership, HLIL helper-field signals, server/client `scorestats` transport,
   weapon mapping, dispatcher routing, callback absence, and competitive
   refresh wiring.
6. Refreshed the cgame ownerdraw and mapping ledgers for the selected five.

### Task A184: Close selected 207-211 cgame ownerdraw parity [COMPLETED]
Priority: High
Primary areas: `tests/test_cgame_displaycontext_parity.py`,
`docs/reverse-engineering/cg-ownerdrawtype-parity-index.md`,
`docs/reverse-engineering/cgame-mapping.md`
Parity estimate: **before 99% -> after 100%** for the selected
`CG_2ND_PLYR_FRAGS_G`, `CG_2ND_PLYR_FRAGS_MG`,
`CG_2ND_PLYR_FRAGS_SG`, `CG_2ND_PLYR_FRAGS_GL`, and
`CG_2ND_PLYR_FRAGS_RL` ownerdraw set. Repo-wide parity remains **98%**
because unrelated compatibility, source-legacy, online-service, and
packaging surfaces are unchanged.

Completed work:

1. Rechecked the retail `cgamex86.dll` dispatcher, `0x100368A0` weapon-frag
   leaf, and `0x1002E2B0` placement weapon resolver for raw ownerdraw cases
   `0xcf` through `0xd3`.
2. Confirmed the selected second-player frag head resolves to G/MG/SG/GL/RL
   weapon indexes `1` through `5`, reads the slot-1 weapon-frag cells, and
   formats through the retail `%d` literal.
3. Confirmed the source placement resolver normalizes the selected second-slot
   ownerdraws back to the first-player family before weapon lookup and text
   construction.
4. Confirmed the qagame-to-cgame compact `scorestats` transport uses the same
   G/MG/SG/GL/RL-leading weapon-frag order before the ownerdraws read
   `cg.scoreStats[clientNum].weaponFrags`.
5. Added focused structural coverage for constants, retail target-group
   membership, HLIL resolver/cache/format/paint signals, source weapon
   mapping, server send path, cgame parse path, placement dispatch, competitive
   refresh wiring, and callback/direct-switch absence.
6. Refreshed the cgame ownerdraw and mapping ledgers for the selected five.

### Task A183: Close selected 202-206 cgame ownerdraw parity [COMPLETED]
Priority: High
Primary areas: `tests/test_cgame_displaycontext_parity.py`,
`docs/reverse-engineering/cg-ownerdrawtype-parity-index.md`,
`docs/reverse-engineering/cgame-mapping.md`
Parity estimate: **before 99% -> after 100%** for the selected
`CG_2ND_PLYR_ACC`, `CG_2ND_PLYR_FLAG`, `CG_2ND_PLYR_AVATAR`,
`CG_2ND_PLYR_TIMEOUT_COUNT`, and `CG_2ND_PLYR_HEALTH_ARMOR` ownerdraw
set. Repo-wide parity remains **98%** because unrelated compatibility,
source-legacy, online-service, and packaging surfaces are unchanged.

Completed work:

1. Rechecked the retail `cgamex86.dll` dispatcher and HLIL leaves for raw
   ownerdraw cases `0xca` through `0xce`.
2. Confirmed `CG_2ND_PLYR_ACC` stays on the pre-switch placement accuracy
   helper and uses the retail `%d%%` total-accuracy path.
3. Confirmed `CG_2ND_PLYR_FLAG` stays on the pre-switch placement flag helper
   and draws the cached country-flag shader or `CG_RegisterCountryFlag`
   fallback without team-flag powerup logic.
4. Confirmed `CG_2ND_PLYR_AVATAR` directly calls the slot-1 avatar/model-icon
   path and preserves the avatar-handle-before-model-icon fallback.
5. Confirmed `CG_2ND_PLYR_TIMEOUT_COUNT` remains an explicit retail no-op,
   with no placement guard, competitive refresh, value, width, or key callback
   route.
6. Confirmed `CG_2ND_PLYR_HEALTH_ARMOR` directly calls the secondary
   health/armor comparison bars, including local-client stat fallback,
   damage-loss segment, left-anchored secondary bars, and no text paint.
7. Added focused structural coverage for constants, retail target-group
   membership, HLIL offset/format/fallback signals, local helper routes,
   competitive refresh wiring, callback absence, and direct no-op behavior.
8. Refreshed the cgame ownerdraw and mapping ledgers for the selected five.

### Task A182: Feed retail arena catalog into live Awesomium start-server map list [COMPLETED]
Priority: High
Primary areas: `src/code/client/cl_cgame.c`,
`src/code/client/cl_awesomium_win32.cpp`,
`tests/test_awesomium_browser_parity.py`
Parity estimate: **before 99.1% -> after 99.2%** for the focused Awesomium
WebUI arena-listing lane. Repo-wide parity remains **98%** because unrelated
compatibility, source-legacy, online-service, and packaging surfaces are
unchanged.

Completed work:

1. Rechecked the retail `GetMapList` HLIL, the map-pool loader notes, and the
   shipped WebUI bundle: Start Match synchronously imports `GetMapList()` and
   `GetFactoryList()`, then filters maps by the selected factory's numeric
   `basegt`.
2. Switched the native WebUI map builder to prefer Quake Live's retail
   `mappool.txt` rotation source, merging duplicate `map|factory` rows into
   one descriptor per unique map and deriving the 13-slot `gametypes` table
   from parsed factory `basegt` definitions; arena files now provide display
   metadata and fallback descriptors.
3. Added startup-time map/factory JSON payloads plus post-document-ready map
   and factory catalog sync. The map catalog still streams in bounded batches,
   and the factory catalog sync keeps the WebUI factory filter from staying on
   the one-entry fallback.
4. Hardened the injected bridge so factory `basegt` tokens map to retail
   `gametype_t` ids, the full bridge reinstalls after Awesomium document
   context resets, and Browserify/CommonJS `mapdb`/`factories` module exports
   are refreshed in place when the native catalog changes.
5. Added runtime diagnostics for qz/module map and factory counts, updated
   focused Awesomium parity coverage, and revalidated the windowed live client:
   the retail map pool loaded 173 rotation entries and the WebUI exposed 93
   unique maps plus 22 factories.

### Task A181: Close selected 197-201 cgame ownerdraw parity [COMPLETED]
Priority: High
Primary areas: `src/code/cgame/cg_newdraw.c`,
`tests/test_cgame_displaycontext_parity.py`,
`docs/reverse-engineering/cg-ownerdrawtype-parity-index.md`,
`docs/reverse-engineering/cgame-mapping.md`
Parity estimate: **before 99% -> after 100%** for the selected
`CG_2ND_PLYR_DEATHS`, `CG_2ND_PLYR_DMG`, `CG_2ND_PLYR_TIME`,
`CG_2ND_PLYR_PING`, and `CG_2ND_PLYR_WINS` ownerdraw set. Repo-wide
parity remains **98%** because unrelated compatibility, source-legacy,
online-service, and packaging surfaces are unchanged.

Completed work:

1. Rechecked the retail `cgamex86.dll` dispatcher and HLIL leaves for raw
   ownerdraw cases `0xc5` through `0xc9`.
2. Confirmed `CG_2ND_PLYR_DEATHS` and `CG_2ND_PLYR_DMG` stay on the
   second-slot placement deaths/damage leaves and now use the retail `%d`
   formatter literal.
3. Confirmed `CG_2ND_PLYR_TIME` remains an inert ownerdraw boundary: retail
   exposes no raw `0xc7` switch case, placement guard, value, width, or key
   callback route.
4. Confirmed `CG_2ND_PLYR_PING` stays on the retail ping leaf, including
   `%d` text formatting, `>40`/`>80` color thresholds, zero blue component,
   and `0.8` alpha.
5. Confirmed `CG_2ND_PLYR_WINS` stays on the slot-1 wins/losses string path
   fed by the retail `%d/%d` scorestats payload.
6. Added focused structural coverage for constants, retail target-group
   membership, HLIL cache/format/color signals, local dispatcher routes,
   competitive score refresh wiring, callback absence, and the inert time
   boundary.
7. Refreshed the cgame ownerdraw and mapping ledgers for the selected five.

### Task A180: Close selected 192-196 cgame ownerdraw parity [COMPLETED]
Priority: High
Primary areas: `src/code/cgame/cg_newdraw.c`,
`tests/test_cgame_displaycontext_parity.py`,
`tests/test_cgame_ownerdraw_text_parity.py`,
`docs/reverse-engineering/cg-ownerdrawtype-parity-index.md`,
`docs/reverse-engineering/cgame-mapping.md`
Parity estimate: **before 99% -> after 100%** for the selected
`CG_1ST_PLYR_TIER`, `CG_2ND_PLYR`, `CG_2ND_PLYR_READY`,
`CG_2ND_PLYR_SCORE`, and `CG_2ND_PLYR_FRAGS` ownerdraw set. Repo-wide
parity remains **98%** because unrelated compatibility, source-legacy,
online-service, and packaging surfaces are unchanged.

Completed work:

1. Rechecked the retail `cgamex86.dll` dispatcher and HLIL leaves for raw
   ownerdraw cases `0xc0` through `0xc4`.
2. Confirmed `CG_1ST_PLYR_TIER` remains an inert boundary: compact scorestats
   can still carry progression tier, but retail exposes no raw `0xc0`
   ownerdraw, placement guard, value, width, or key callback route.
3. Confirmed `CG_2ND_PLYR` and `CG_2ND_PLYR_SCORE` use the direct slot-1 name
   and score helpers, including cached second-player text, `"-"` fallback,
   retail `%d` score formatting, and alignment.
4. Confirmed `CG_2ND_PLYR_READY` stays on the secondary status/ready helper,
   preserving `LEADS`/`TIED`/`TRAILS` and `READY`/`NOT READY` behavior.
5. Restored the retail `%d` literal for placement frag ownerdraw text so
   `CG_2ND_PLYR_FRAGS` matches the `0x100361F0` slot-1 frag path.
6. Added focused structural coverage for constants, retail target-group
   membership, HLIL cache/status/format signals, local dispatcher routes,
   competitive score refresh wiring, callback absence, and the inert tier
   boundary.
7. Refreshed the cgame ownerdraw and mapping ledgers for the selected five.

### Task A179: Close selected 187-191 cgame ownerdraw parity [COMPLETED]
Priority: High
Primary areas: `src/code/cgame/cg_newdraw.c`,
`src/code/cgame/cg_servercmds.c`, `src/code/game/g_cmds.c`,
`tests/test_cgame_displaycontext_parity.py`,
`docs/reverse-engineering/cg-ownerdrawtype-parity-index.md`,
`docs/reverse-engineering/cgame-mapping.md`
Parity estimate: **before 99% -> after 100%** for the selected
`CG_1ST_PLYR_AVG_PICKUP_TIME_MH`, `CG_1ST_PLYR_EXCELLENT`,
`CG_1ST_PLYR_IMPRESSIVE`, `CG_1ST_PLYR_HUMILIATION`, and
`CG_1ST_PLYR_PR` ownerdraw set. Repo-wide parity remains **98%** because
unrelated compatibility, source-legacy, online-service, and packaging
surfaces are unchanged.

Completed work:

1. Rechecked the retail `cgamex86.dll` dispatcher, `0x10037730`
   pickup-average leaf, and `0x10037990` award-count leaf for raw ownerdraw
   cases `0xbb` through `0xbf`.
2. Confirmed `CG_1ST_PLYR_AVG_PICKUP_TIME_MH` closes the first-player pickup
   average band, reads the MH average cache, and shares the retail `"-"`
   zero-count fallback.
3. Confirmed `CG_1ST_PLYR_EXCELLENT`, `CG_1ST_PLYR_IMPRESSIVE`, and
   `CG_1ST_PLYR_HUMILIATION` stay on the retail award-count path and are fed
   by the qagame duel score row plus cgame score parsing.
4. Restored the retail `%d` literal for placement award-count ownerdraw text.
5. Confirmed `CG_1ST_PLYR_PR` remains an inert ownerdraw boundary: compact
   scorestats still transport progression PR/tier, but retail does not route
   raw `0xbf` through ownerdraw, guard, value, width, or key callbacks.
6. Added focused structural coverage for constants, retail target-group
   membership, HLIL average/award cache signals, qagame send path, cgame parse
   path, formatter, dispatcher guard, callback absence, and direct-switch
   absence.
7. Refreshed the cgame ownerdraw and mapping ledgers for the selected five.

### Task A178: Close selected 182-186 cgame ownerdraw parity [COMPLETED]
Priority: High
Primary areas: `src/code/cgame/cg_newdraw.c`,
`src/code/cgame/cg_servercmds.c`, `src/code/game/g_cmds.c`,
`tests/test_cgame_displaycontext_parity.py`,
`docs/reverse-engineering/cg-ownerdrawtype-parity-index.md`,
`docs/reverse-engineering/cgame-mapping.md`
Parity estimate: **before 98% -> after 100%** for the selected
`CG_1ST_PLYR_PICKUPS_GA`, `CG_1ST_PLYR_PICKUPS_MH`,
`CG_1ST_PLYR_AVG_PICKUP_TIME_RA`,
`CG_1ST_PLYR_AVG_PICKUP_TIME_YA`, and
`CG_1ST_PLYR_AVG_PICKUP_TIME_GA` ownerdraw set. Repo-wide parity remains
**98%** because unrelated compatibility, source-legacy, online-service, and
packaging surfaces are unchanged.

Completed work:

1. Rechecked the retail `cgamex86.dll` dispatcher, `0x10036EB0` pickup-count
   leaf, and `0x10037730` pickup-average leaf for raw ownerdraw cases `0xb6`
   through `0xba`.
2. Confirmed `CG_1ST_PLYR_PICKUPS_GA` and `CG_1ST_PLYR_PICKUPS_MH` stay on
   the direct retail pickup-count path and consume the same compact GA/MH
   pickup order used by qagame send and cgame parse.
3. Restored the retail pickup-average zero-count fallback: RA/YA/GA average
   ownerdraws now paint `"-"` when the corresponding count is zero and `%3.2f`
   when a pickup interval is available.
4. Pinned both compact `scorestats` and legacy duel-score parsing for the
   selected pickup counts and average intervals.
5. Added focused structural coverage for constants, retail target-group
   membership, HLIL count/average cache signals, qagame send path, cgame parse
   path, visible average fallback, dispatcher guard, callback absence, and
   direct-switch absence.
6. Refreshed the cgame ownerdraw and mapping ledgers for the selected five.

### Task A177: Close selected 177-181 cgame ownerdraw parity [COMPLETED]
Priority: High
Primary areas: `src/code/cgame/cg_newdraw.c`,
`src/code/cgame/cg_servercmds.c`, `src/code/game/g_cmds.c`,
`tests/test_cgame_displaycontext_parity.py`,
`docs/reverse-engineering/cg-ownerdrawtype-parity-index.md`,
`docs/reverse-engineering/cgame-mapping.md`
Parity estimate: **before 97% -> after 100%** for the selected
`CG_1ST_PLYR_ACC_PL`, `CG_1ST_PLYR_ACC_HMG`,
`CG_1ST_PLYR_PICKUPS`, `CG_1ST_PLYR_PICKUPS_RA`, and
`CG_1ST_PLYR_PICKUPS_YA` ownerdraw set. Repo-wide parity remains
**98%** because unrelated compatibility, source-legacy, online-service, and
packaging surfaces are unchanged.

Completed work:

1. Rechecked the retail `cgamex86.dll` dispatcher, `0x10036D60`
   weapon-accuracy leaf, `0x10036EB0` pickup leaf, and `0x1002E2B0`
   placement weapon resolver for raw ownerdraw cases `0xb1` through `0xb5`.
2. Confirmed the selected accuracy tail resolves to PL/HMG weapon indexes
   `0xc` and `0xe`, reads the `data_10A6034C` accuracy cache, formats through
   the retail `%d%%` literal, and inherits the best-row color override.
3. Restored the retail `CG_1ST_PLYR_PICKUPS` summary strip: nonzero
   RA/YA/GA/MH pickups draw the retail pickup shader, count text, and `%3.2f`
   average interval from the compact scorestats payload.
4. Confirmed `CG_1ST_PLYR_PICKUPS_RA` and `CG_1ST_PLYR_PICKUPS_YA` stay on
   the direct retail pickup-count path and now use the retail `%d` formatter.
5. Pinned qagame-to-cgame compact pickup wiring: qagame sends RA/YA/GA/MH
   counts and average intervals, cgame parses them into `pickupCounts` and
   `pickupAvgSeconds`, and the ownerdraws consume the same order.
6. Added focused structural coverage for constants, retail target-group
   membership, resolver returns, pickup shader handles, server send path,
   cgame parse path, summary drawing, direct count drawing, dispatcher guard,
   callback absence, and direct-switch absence.
7. Refreshed the cgame ownerdraw and mapping ledgers for the selected five.

### Task A176: Close selected 6-10 cgame front-panel status ownerdraw parity [COMPLETED]
Priority: High
Primary areas: `src/code/cgame/cg_newdraw.c`,
`src/code/cgame/cg_main.c`, `tests/test_cgame_ownerdraw_text_parity.py`,
`docs/reverse-engineering/cg-ownerdrawtype-parity-index.md`,
`docs/reverse-engineering/cgame-mapping.md`
Parity estimate: **before 99% -> after 100%** for the selected
`CG_GAME_TYPE_MAP`, `CG_GAME_STATUS`, `CG_MATCH_DETAILS`,
`CG_MATCH_END_CONDITION`, and `CG_MATCH_STATUS` ownerdraw set. Repo-wide
parity remains **98%** because unrelated compatibility, source-legacy,
online-service, and packaging surfaces are unchanged.

Completed work:

1. Rechecked the retail `cgamex86.dll` dispatcher for raw ownerdraw cases
   `0x06` through `0x0A`.
2. Confirmed `CG_GAME_TYPE_MAP`, `CG_GAME_STATUS`, `CG_MATCH_DETAILS`,
   `CG_MATCH_END_CONDITION`, and `CG_MATCH_STATUS` route to the recovered
   intro-panel detail, standalone game-status, match-details,
   match-end-condition, and match-status helpers respectively.
3. Confirmed the selected batch preserves the intended callback boundary:
   `CG_GAME_STATUS` and `CG_MATCH_STATUS` participate in the width callback,
   while all five stay out of value and key callbacks.
4. Added focused structural coverage for constants, retail target membership,
   source switch routes, helper behavior, shipped menu reachability,
   display-context wiring, and width callback splits for the selected five.
5. Refreshed the cgame ownerdraw and mapping ledgers for this selected batch.

### Task A175: Close selected 172-176 cgame ownerdraw parity [COMPLETED]
Priority: High
Primary areas: `src/code/cgame/cg_newdraw.c`,
`src/code/cgame/cg_servercmds.c`, `src/code/game/g_cmds.c`,
`tests/test_cgame_displaycontext_parity.py`,
`docs/reverse-engineering/cg-ownerdrawtype-parity-index.md`,
`docs/reverse-engineering/cgame-mapping.md`
Parity estimate: **before 99% -> after 100%** for the selected
`CG_1ST_PLYR_ACC_RG`, `CG_1ST_PLYR_ACC_PG`,
`CG_1ST_PLYR_ACC_BFG`, `CG_1ST_PLYR_ACC_CG`, and
`CG_1ST_PLYR_ACC_NG` ownerdraw set. Repo-wide parity remains **98%**
because unrelated compatibility, source-legacy, online-service, and packaging
surfaces are unchanged.

Completed work:

1. Rechecked the retail `cgamex86.dll` dispatcher, `0x10036D60`
   weapon-accuracy leaf, and `0x1002E2B0` placement weapon resolver for raw
   ownerdraw cases `0xac` through `0xb0`.
2. Confirmed the selected accuracy band resolves to RG/PG/BFG/CG/NG weapon
   indexes `7`, `8`, `9`, `0xd`, and `0xb`, reads the `data_10A6034C`
   accuracy cache, and formats through the retail `%d%%` literal.
3. Confirmed the selected ownerdraws inherit the restored retail comparison
   color path: the row whose weapon accuracy beats the opposing placement
   slot paints white with `0.8` alpha.
4. Pinned the qagame-to-cgame compact accuracy wiring: qagame sends
   `accuracy_hits` and `accuracy_shots`, cgame parses both in the same weapon
   order, then derives `weaponAccuracy` before the ownerdraw reads it.
5. Added focused structural coverage for constants, retail target-group
   membership, resolver returns, cache reads, weapon mapping, server send
   path, cgame parse path, formatter, comparison color, dispatcher guard,
   callback absence, and direct-switch absence.
6. Refreshed the cgame ownerdraw and mapping ledgers for the selected five.

### Task A174: Close selected 1-5 cgame front-panel ownerdraw parity [COMPLETED]
Priority: High
Primary areas: `src/code/cgame/cg_newdraw.c`,
`src/code/cgame/cg_servercmds.c`, `src/code/cgame/cg_main.c`,
`tests/test_cgame_ownerdraw_text_parity.py`,
`docs/reverse-engineering/cg-ownerdrawtype-parity-index.md`,
`docs/reverse-engineering/cgame-mapping.md`
Parity estimate: **before 99% -> after 100%** for the selected
`CG_SERVER_SETTINGS`, `CG_STARTING_WEAPONS`, `CG_GAME_LIMIT`,
`CG_GAME_TYPE`, and `CG_GAME_TYPE_ICON` ownerdraw set. Repo-wide parity
remains **98%** because unrelated compatibility, source-legacy,
online-service, and packaging surfaces are unchanged.

Completed work:

1. Rechecked the retail `cgamex86.dll` dispatcher for raw ownerdraw cases
   `0x01` through `0x05`.
2. Confirmed `CG_SERVER_SETTINGS`, `CG_STARTING_WEAPONS`, `CG_GAME_LIMIT`,
   `CG_GAME_TYPE`, and `CG_GAME_TYPE_ICON` route to the recovered settings,
   starting-weapon icon strip, game-limit label, gametype text, and gametype
   icon helpers respectively.
3. Confirmed the selected batch preserves the intended callback boundary:
   `CG_GAME_TYPE` alone participates in the width callback, while all five
   stay out of value and key callbacks.
4. Added focused structural coverage for constants, retail target membership,
   source switch routes, helper behavior, shipped menu reachability,
   display-context wiring, and configstring inputs for the selected five.
5. Refreshed the cgame ownerdraw and mapping ledgers for this selected batch.

### Task A173: Close selected 167-171 cgame ownerdraw parity [COMPLETED]
Priority: High
Primary areas: `src/code/cgame/cg_newdraw.c`,
`src/code/cgame/cg_servercmds.c`, `src/code/game/g_cmds.c`,
`tests/test_cgame_displaycontext_parity.py`,
`docs/reverse-engineering/cg-ownerdrawtype-parity-index.md`,
`docs/reverse-engineering/cgame-mapping.md`
Parity estimate: **before 98% -> after 100%** for the selected
`CG_1ST_PLYR_ACC_MG`, `CG_1ST_PLYR_ACC_SG`,
`CG_1ST_PLYR_ACC_GL`, `CG_1ST_PLYR_ACC_RL`, and
`CG_1ST_PLYR_ACC_LG` ownerdraw set. Repo-wide parity remains **98%**
because unrelated compatibility, source-legacy, online-service, and packaging
surfaces are unchanged.

Completed work:

1. Rechecked the retail `cgamex86.dll` dispatcher, `0x10036D60`
   weapon-accuracy leaf, and `0x1002E2B0` placement weapon resolver for raw
   ownerdraw cases `0xa7` through `0xab`.
2. Confirmed the selected accuracy head resolves to MG/SG/GL/RL/LG weapon
   indexes `2` through `6`, reads the `data_10A6034C` accuracy cache, and
   formats through the retail `%d%%` literal.
3. Restored the retail per-weapon accuracy comparison color: the row whose
   accuracy beats the opposing placement slot for the same weapon paints
   white with `0.8` alpha.
4. Pinned the qagame-to-cgame compact accuracy wiring: qagame sends
   `accuracy_hits` and `accuracy_shots`, cgame parses both in the same weapon
   order, then derives `weaponAccuracy` before the ownerdraw reads it.
5. Added focused structural coverage for constants, retail target-group
   membership, resolver returns, cache reads, weapon mapping, server send
   path, cgame parse path, formatter, comparison color, dispatcher guard,
   callback absence, and direct-switch absence.
6. Refreshed the cgame ownerdraw and mapping ledgers for the selected five.

### Task A172: Close selected 90-94 cgame endgame/selected-player ownerdraw parity [COMPLETED]
Priority: High
Primary areas: `src/code/cgame/cg_newdraw.c`,
`tests/test_cgame_ownerdraw_text_parity.py`,
`docs/reverse-engineering/cg-ownerdrawtype-parity-index.md`,
`docs/reverse-engineering/cgame-mapping.md`
Parity estimate: **before 99% -> after 100%** for the selected
`CG_PLYR_END_GAME_SCORE`, `CG_PLYR_BEST_WEAPON_NAME`,
`CG_SELECTED_PLYR_TEAM_COLOR`, `CG_SELECTED_PLYR_ACCURACY`, and
`CG_FOLLOW_PLAYER_NAME` ownerdraw set. Repo-wide parity remains **98%**
because unrelated compatibility, source-legacy, online-service, and packaging
surfaces are unchanged.

Completed work:

1. Rechecked the retail `cgamex86.dll` dispatcher for raw ownerdraw cases
   `0x5A` through `0x5E`.
2. Confirmed `CG_PLYR_END_GAME_SCORE`, `CG_PLYR_BEST_WEAPON_NAME`,
   `CG_SELECTED_PLYR_TEAM_COLOR`, `CG_SELECTED_PLYR_ACCURACY`, and
   `CG_FOLLOW_PLAYER_NAME` route to the endgame score, selected best weapon,
   selected team color, selected accuracy, and follow-name helpers
   respectively.
3. Confirmed the selected batch preserves the intended competitive-score
   refresh boundary: only the endgame score row refreshes, while the
   selected-player and follow-name ownerdraws do not.
4. Added focused structural coverage for constants, retail target membership,
   source switch routes, helper behavior, shipped menu reachability,
   competitive refresh, and callback absence for the selected five.
5. Refreshed the cgame ownerdraw and mapping ledgers for this selected batch.

### Task A171: Close selected 162-166 cgame ownerdraw parity [COMPLETED]
Priority: High
Primary areas: `src/code/cgame/cg_newdraw.c`,
`src/code/cgame/cg_servercmds.c`, `src/code/game/g_cmds.c`,
`tests/test_cgame_displaycontext_parity.py`,
`docs/reverse-engineering/cg-ownerdrawtype-parity-index.md`,
`docs/reverse-engineering/cgame-mapping.md`
Parity estimate: **before 99% -> after 100%** for the selected
`CG_1ST_PLYR_DMG_BFG`, `CG_1ST_PLYR_DMG_CG`,
`CG_1ST_PLYR_DMG_NG`, `CG_1ST_PLYR_DMG_PL`, and
`CG_1ST_PLYR_DMG_HMG` ownerdraw set. Repo-wide parity remains **98%**
because unrelated compatibility, source-legacy, online-service, and packaging
surfaces are unchanged.

Completed work:

1. Rechecked the retail `cgamex86.dll` dispatcher, `0x10036C30` weapon-damage
   leaf, and `0x1002E2B0` placement weapon resolver for raw ownerdraw cases
   `0xa2` through `0xa6`.
2. Confirmed the selected damage tail resolves to BFG/CG/NG/PL/HMG weapon
   indexes `9`, `0xd`, `0xb`, `0xc`, and `0xe`, reads the
   `data_10A6040C` damage cache, and formats through the retail `%d` literal.
3. Pinned the qagame-to-cgame compact weapon-damage wiring for the selected
   tail weapon band.
4. Added focused structural coverage for constants, retail target-group
   membership, resolver returns, cache reads, weapon mapping, server send
   path, cgame parse path, dispatcher guard, callback absence, and
   direct-switch absence.
5. Refreshed the cgame ownerdraw and mapping ledgers for the selected five.

### Task A170: Close selected 85-89 cgame model/second-place/chat ownerdraw parity [COMPLETED]
Priority: High
Primary areas: `src/code/cgame/cg_newdraw.c`,
`tests/test_cgame_ownerdraw_text_parity.py`,
`docs/reverse-engineering/cg-ownerdrawtype-parity-index.md`,
`docs/reverse-engineering/cgame-mapping.md`
Parity estimate: **before 99% -> after 100%** for the selected
`CG_1STPLACE_PLYR_MODEL`, `CG_2NDPLACE`, `CG_2ND_PLACE_SCORE`,
`CG_PLAYER_OBIT`, and `CG_AREA_NEW_CHAT` ownerdraw set. Repo-wide
parity remains **98%** because unrelated compatibility, source-legacy,
online-service, and packaging surfaces are unchanged.

Completed work:

1. Rechecked the retail `cgamex86.dll` dispatcher for raw ownerdraw cases
   `0x55` through `0x59`.
2. Confirmed `CG_1STPLACE_PLYR_MODEL`, `CG_2NDPLACE`, `CG_2ND_PLACE_SCORE`,
   `CG_PLAYER_OBIT`, and `CG_AREA_NEW_CHAT` route to the first-place model,
   compact score, wide second-place score, obituary feed, and new-chat helpers
   respectively.
3. Confirmed the selected batch preserves the intended competitive-score
   refresh boundary: first-place model and second-place score rows refresh,
   while obituary and chat ownerdraws do not.
4. Added focused structural coverage for constants, retail target membership,
   source switch routes, helper behavior, shipped menu reachability,
   competitive refresh, and callback absence for the selected five.
5. Refreshed the cgame ownerdraw and mapping ledgers for this selected batch.

### Task A169: Close selected 80-84 cgame award/scoreboard ownerdraw parity [COMPLETED]
Priority: High
Primary areas: `src/code/cgame/cg_newdraw.c`,
`src/code/game/g_main.c`,
`tests/test_cgame_ownerdraw_text_parity.py`,
`docs/reverse-engineering/cg-ownerdrawtype-parity-index.md`,
`docs/reverse-engineering/cgame-mapping.md`
Parity estimate: **before 99% -> after 100%** for the selected
`CG_MOST_DAMAGEDEALT_PLYR`, `CG_SPECTATORS`, `CG_MATCH_WINNER`,
`CG_1STPLACE`, and `CG_1ST_PLACE_SCORE` ownerdraw set. Repo-wide
parity remains **98%** because unrelated compatibility, source-legacy,
online-service, and packaging surfaces are unchanged.

Completed work:

1. Rechecked the retail `cgamex86.dll` dispatcher, `0x1003A0D0` award-player
   HLIL leaf, and adjacent scoreboard call targets for raw ownerdraw cases
   `0x50` through `0x54`.
2. Confirmed `CG_MOST_DAMAGEDEALT_PLYR` remains the final pre-switch
   award-player image route fed by `CS_AWARD_MOST_DAMAGEDEALT`.
3. Confirmed `CG_SPECTATORS`, `CG_MATCH_WINNER`, `CG_1STPLACE`, and
   `CG_1ST_PLACE_SCORE` route to the spectator list, match winner, compact
   score, and wide first-place score helpers respectively.
4. Added focused structural coverage for constants, retail target membership,
   pre-switch/switch separation, configstring producer/consumer wiring,
   shipped menu reachability, competitive refresh, and callback absence for
   the selected five.
5. Refreshed the cgame ownerdraw and mapping ledgers for this selected batch.

### Task A168: Close selected 157-161 cgame ownerdraw parity [COMPLETED]
Priority: High
Primary areas: `src/code/cgame/cg_newdraw.c`,
`src/code/cgame/cg_servercmds.c`, `src/code/game/g_cmds.c`,
`tests/test_cgame_displaycontext_parity.py`,
`docs/reverse-engineering/cg-ownerdrawtype-parity-index.md`,
`docs/reverse-engineering/cgame-mapping.md`
Parity estimate: **before 99% -> after 100%** for the selected
`CG_1ST_PLYR_DMG_GL`, `CG_1ST_PLYR_DMG_RL`,
`CG_1ST_PLYR_DMG_LG`, `CG_1ST_PLYR_DMG_RG`, and
`CG_1ST_PLYR_DMG_PG` ownerdraw set. Repo-wide parity remains **98%**
because unrelated compatibility, source-legacy, online-service, and packaging
surfaces are unchanged.

Completed work:

1. Rechecked the retail `cgamex86.dll` dispatcher, `0x10036C30` weapon-damage
   leaf, and `0x1002E2B0` placement weapon resolver for raw ownerdraw cases
   `0x9d` through `0xa1`.
2. Confirmed the selected damage band resolves to GL/RL/LG/RG/PG weapon
   indexes `4` through `8`, reads the `data_10A6040C` damage cache, and
   formats through the retail `%d` literal.
3. Pinned the qagame-to-cgame compact weapon-damage wiring for the selected
   middle weapon band.
4. Added focused structural coverage for constants, retail target-group
   membership, resolver returns, cache reads, weapon mapping, server send
   path, cgame parse path, dispatcher guard, callback absence, and
   direct-switch absence.
5. Refreshed the cgame ownerdraw and mapping ledgers for the selected five.

### Task A167: Close selected 75-79 cgame award-player ownerdraw parity [COMPLETED]
Priority: High
Primary areas: `src/code/cgame/cg_newdraw.c`,
`src/code/game/g_main.c`,
`tests/test_cgame_ownerdraw_text_parity.py`,
`docs/reverse-engineering/cg-ownerdrawtype-parity-index.md`,
`docs/reverse-engineering/cgame-mapping.md`
Parity estimate: **before 99% -> after 100%** for the selected
`CG_MOST_VALUABLE_OFFENSIVE_PLYR`,
`CG_MOST_VALUABLE_DEFENSIVE_PLYR`, `CG_MOST_VALUABLE_PLYR`,
`CG_BEST_ITEMCONTROL_PLYR`, and `CG_MOST_ACCURATE_PLYR` ownerdraw
set. Repo-wide parity remains **98%** because unrelated compatibility,
source-legacy, online-service, and packaging surfaces are unchanged.

Completed work:

1. Rechecked the retail `cgamex86.dll` dispatcher and `0x1003A0D0` award-player
   HLIL leaf for raw ownerdraw cases `0x4B` through `0x4F`.
2. Confirmed the selected ownerdraws route through the pre-switch award-player
   helper rather than the ordinary `CG_OwnerDraw` switch body.
3. Confirmed the selected award-player helpers are fed by qagame-published
   `CS_AWARD_*` configstrings and cgame resolves them before drawing the
   profile image for the winning client.
4. Added focused structural coverage for constants, retail target membership,
   pre-switch ordering, configstring producer/consumer wiring, shipped menu
   reachability, competitive refresh, and callback absence for the selected
   five.
5. Refreshed the cgame ownerdraw and mapping ledgers for this selected batch.

### Task A166: Close selected 152-156 cgame ownerdraw parity [COMPLETED]
Priority: High
Primary areas: `src/code/cgame/cg_newdraw.c`,
`src/code/cgame/cg_servercmds.c`, `src/code/game/g_cmds.c`,
`tests/test_cgame_displaycontext_parity.py`,
`docs/reverse-engineering/cg-ownerdrawtype-parity-index.md`,
`docs/reverse-engineering/cgame-mapping.md`
Parity estimate: **before 99% -> after 100%** for the selected
`CG_1ST_PLYR_SHOTS_PL`, `CG_1ST_PLYR_SHOTS_HMG`,
`CG_1ST_PLYR_DMG_G`, `CG_1ST_PLYR_DMG_MG`, and
`CG_1ST_PLYR_DMG_SG` ownerdraw set. Repo-wide parity remains **98%**
because unrelated compatibility, source-legacy, online-service, and packaging
surfaces are unchanged.

Completed work:

1. Rechecked the retail `cgamex86.dll` dispatcher, `0x10036B00` weapon-shot
   leaf, `0x10036C30` weapon-damage leaf, and `0x1002E2B0` placement weapon
   resolver for raw ownerdraw cases `0x98` through `0x9c`.
2. Tightened placement weapon-damage formatting to the retail `%d` literal,
   matching the shared `data_10068E44` format used by the damage helper.
3. Confirmed the selected shot tail resolves to PL/HMG weapon indexes `0xc`
   and `0xe`, while the selected damage head resolves to G/MG/SG weapon
   indexes `1`, `2`, and `3`.
4. Pinned the qagame-to-cgame compact `accuracy_shots` and weapon-damage
   wiring used by the selected ownerdraws.
5. Added focused structural coverage for constants, retail target-group
   membership, resolver returns, cache reads, weapon mapping, server send
   path, cgame parse path, dispatcher guard, callback absence, and
   direct-switch absence.
6. Refreshed the cgame ownerdraw and mapping ledgers for the selected five.

### Task A165: Close gauntlet/impressive/rampage/midair/perfect cgame ownerdraw parity [COMPLETED]
Priority: High
Primary areas: `src/code/cgame/cg_newdraw.c`,
`tests/test_cgame_ownerdraw_text_parity.py`,
`docs/reverse-engineering/cg-ownerdrawtype-parity-index.md`,
`docs/reverse-engineering/cgame-mapping.md`
Parity estimate: **before 99% -> after 100%** for the selected
`CG_GAUNTLET`, `CG_IMPRESSIVE`, `CG_RAMPAGES`, `CG_MIDAIRS`, and
`CG_PERFECT` ownerdraw set. Repo-wide parity remains **98%** because
unrelated compatibility, source-legacy, online-service, and packaging surfaces
are unchanged.

Completed work:

1. Rechecked the retail `cgamex86.dll` dispatcher and `0x10035340` medal HLIL
   leaf for raw ownerdraw cases `0x46` through `0x4A`.
2. Confirmed `CG_GAUNTLET`, `CG_IMPRESSIVE`, and `CG_PERFECT` route through
   the real medal target group and read the selected-score gauntlet,
   impressive, and perfect fields.
3. Confirmed `CG_RAMPAGES` and `CG_MIDAIRS` remain retail no-ops between medal
   IDs with no authored menu usage and no helper route.
4. Added focused structural coverage for constants, retail switch membership,
   source medal/no-op separation, selected-score field reads, menu reachability,
   and callback absence for the selected five.
5. Refreshed the cgame ownerdraw and mapping ledgers for this selected batch.

### Task A164: Close assist/capture/combo/defend/excellent cgame ownerdraw parity [COMPLETED]
Priority: High
Primary areas: `src/code/cgame/cg_newdraw.c`,
`tests/test_cgame_ownerdraw_text_parity.py`,
`docs/reverse-engineering/cg-ownerdrawtype-parity-index.md`,
`docs/reverse-engineering/cgame-mapping.md`
Parity estimate: **before 99% -> after 100%** for the selected
`CG_ASSISTS`, `CG_CAPTURES`, `CG_COMBOKILLS`, `CG_DEFEND`, and
`CG_EXCELLENT` ownerdraw set. Repo-wide parity remains **98%**
because unrelated compatibility, source-legacy, online-service, and packaging
surfaces are unchanged.

Completed work:

1. Rechecked the retail `cgamex86.dll` dispatcher and `0x10035340` medal HLIL
   leaf for raw ownerdraw cases `0x41` through `0x45`.
2. Confirmed `CG_ASSISTS`, `CG_CAPTURES`, `CG_DEFEND`, and `CG_EXCELLENT`
   route through the real medal target group and read the selected-score
   assist, capture, defend, and excellent fields.
3. Confirmed `CG_COMBOKILLS` remains a retail no-op between medal IDs with no
   authored menu usage and no helper route.
4. Added focused structural coverage for constants, retail switch membership,
   source medal/no-op separation, selected-score field reads, menu reachability,
   and callback absence for the selected five.
5. Refreshed the cgame ownerdraw and mapping ledgers for this selected batch.

### Task A163: Close selected 147-151 cgame ownerdraw parity [COMPLETED]
Priority: High
Primary areas: `src/code/cgame/cg_newdraw.c`,
`src/code/cgame/cg_servercmds.c`, `src/code/game/g_cmds.c`,
`tests/test_cgame_displaycontext_parity.py`,
`docs/reverse-engineering/cg-ownerdrawtype-parity-index.md`,
`docs/reverse-engineering/cgame-mapping.md`
Parity estimate: **before 99% -> after 100%** for the selected
`CG_1ST_PLYR_SHOTS_RG`, `CG_1ST_PLYR_SHOTS_PG`,
`CG_1ST_PLYR_SHOTS_BFG`, `CG_1ST_PLYR_SHOTS_CG`, and
`CG_1ST_PLYR_SHOTS_NG` ownerdraw set. Repo-wide parity remains **98%**
because unrelated compatibility, source-legacy, online-service, and packaging
surfaces are unchanged.

Completed work:

1. Rechecked the retail `cgamex86.dll` dispatcher, `0x10036B00` weapon-shot
   leaf, and `0x1002E2B0` placement weapon resolver for raw ownerdraw cases
   `0x93` through `0x97`.
2. Confirmed the selected shot band resolves to RG/PG/BFG/CG/NG weapon indexes
   `7`, `8`, `9`, `0xd`, and `0xb`, reads the `data_10A6038C` shot cache,
   and formats through the retail `%d` literal.
3. Pinned the qagame-to-cgame compact `accuracy_shots` wiring for the selected
   middle/tail weapon band.
4. Added focused structural coverage for constants, retail target-group
   membership, resolver returns, cache reads, weapon mapping, server send
   path, cgame parse path, dispatcher guard, callback absence, and
   direct-switch absence.
5. Refreshed the cgame ownerdraw and mapping ledgers for the selected five.

### Task A162: Close selected 142-146 cgame ownerdraw parity [COMPLETED]
Priority: High
Primary areas: `src/code/cgame/cg_newdraw.c`,
`src/code/cgame/cg_servercmds.c`, `src/code/game/g_cmds.c`,
`tests/test_cgame_displaycontext_parity.py`,
`docs/reverse-engineering/cg-ownerdrawtype-parity-index.md`,
`docs/reverse-engineering/cgame-mapping.md`
Parity estimate: **before 99% -> after 100%** for the selected
`CG_1ST_PLYR_SHOTS_MG`, `CG_1ST_PLYR_SHOTS_SG`,
`CG_1ST_PLYR_SHOTS_GL`, `CG_1ST_PLYR_SHOTS_RL`, and
`CG_1ST_PLYR_SHOTS_LG` ownerdraw set. Repo-wide parity remains **98%**
because unrelated compatibility, source-legacy, online-service, and packaging
surfaces are unchanged.

Completed work:

1. Rechecked the retail `cgamex86.dll` dispatcher, `0x10036B00` weapon-shot
   leaf, and `0x1002E2B0` placement weapon resolver for raw ownerdraw cases
   `0x8e` through `0x92`.
2. Tightened placement weapon-shot formatting to the retail `%d` literal,
   matching the shared `data_10068E44` format used by the shot helper.
3. Confirmed the selected shot head resolves to MG/SG/GL/RL/LG weapon indexes
   `2` through `6`, reads the `data_10A6038C` shot cache, and is backed by
   compact `accuracy_shots` qagame-to-cgame wiring.
4. Added focused structural coverage for constants, retail target-group
   membership, resolver returns, cache reads, weapon mapping, server send
   path, cgame parse path, dispatcher guard, callback absence, and
   direct-switch absence.
5. Refreshed the cgame ownerdraw and mapping ledgers for the selected five.

### Task A161: Close powerup/teamcolor/killer/accuracy cgame ownerdraw parity [COMPLETED]
Priority: High
Primary areas: `src/code/cgame/cg_newdraw.c`,
`tests/test_cgame_ownerdraw_text_parity.py`,
`tests/test_cgame_displaycontext_parity.py`,
`docs/reverse-engineering/cg-ownerdrawtype-parity-index.md`,
`docs/reverse-engineering/cgame-mapping.md`
Parity estimate: **before 99% -> after 100%** for the selected
`CG_CTF_POWERUP`, `CG_AREA_POWERUP`, `CG_TEAM_COLOR`, `CG_KILLER`,
and `CG_ACCURACY` ownerdraw set. Repo-wide parity remains **98%**
because unrelated compatibility, source-legacy, online-service, and packaging
surfaces are unchanged.

Completed work:

1. Rechecked the retail `cgamex86.dll` dispatcher and HLIL leaves for raw
   ownerdraw cases `0x3C` through `0x40`.
2. Confirmed `CG_CTF_POWERUP` uses the persisted powerup item icon path,
   `CG_AREA_POWERUP` uses the retail powerup sprite stack, and `CG_TEAM_COLOR`
   lands on the lower team-background helper with the local team value.
3. Corrected the powerup frag badge format to the retail `x %i` literal for
   the quad and battlesuit badge path.
4. Confirmed `CG_KILLER` is draw-gated by the cached killer name and shares the
   same `Fragged by %s` text with the width callback.
5. Confirmed `CG_ACCURACY` remains in the real medal switch group with `%i%%`
   text and alpha promotion for nonzero accuracy.
6. Added focused structural coverage for constants, retail targets, source
   dispatcher wiring, callback participation, menu reachability, and helper
   literals for the selected five.

### Task A160: Close selected 137-141 cgame ownerdraw parity [COMPLETED]
Priority: High
Primary areas: `src/code/cgame/cg_newdraw.c`,
`src/code/cgame/cg_servercmds.c`, `src/code/game/g_cmds.c`,
`tests/test_cgame_displaycontext_parity.py`,
`docs/reverse-engineering/cg-ownerdrawtype-parity-index.md`,
`docs/reverse-engineering/cgame-mapping.md`
Parity estimate: **before 99% -> after 100%** for the selected
`CG_1ST_PLYR_HITS_BFG`, `CG_1ST_PLYR_HITS_CG`,
`CG_1ST_PLYR_HITS_NG`, `CG_1ST_PLYR_HITS_PL`, and
`CG_1ST_PLYR_HITS_HMG` ownerdraw set. Repo-wide parity remains **98%**
because unrelated compatibility, source-legacy, online-service, and packaging
surfaces are unchanged.

Completed work:

1. Rechecked the retail `cgamex86.dll` dispatcher, `0x100369D0` weapon-hit
   leaf, and `0x1002E2B0` placement weapon resolver for raw ownerdraw cases
   `0x89` through `0x8d`.
2. Confirmed the selected hit tail resolves to BFG/CG/NG/PL/HMG weapon indexes
   `9`, `0xd`, `0xb`, `0xc`, and `0xe`, reads the `data_10A603CC` hit cache,
   and formats through the retail `%d` literal.
3. Pinned the qagame-to-cgame compact `accuracy_hits` wiring for the selected
   tail weapon band.
4. Added focused structural coverage for constants, retail target-group
   membership, resolver returns, cache reads, weapon mapping, server send
   path, cgame parse path, dispatcher guard, callback absence, and
   direct-switch absence.
5. Refreshed the cgame ownerdraw and mapping ledgers for the selected five.

### Task A159: Close selected 132-136 cgame ownerdraw parity [COMPLETED]
Priority: High
Primary areas: `src/code/cgame/cg_newdraw.c`,
`src/code/cgame/cg_servercmds.c`, `src/code/game/g_cmds.c`,
`tests/test_cgame_displaycontext_parity.py`,
`docs/reverse-engineering/cg-ownerdrawtype-parity-index.md`,
`docs/reverse-engineering/cgame-mapping.md`
Parity estimate: **before 99% -> after 100%** for the selected
`CG_1ST_PLYR_HITS_GL`, `CG_1ST_PLYR_HITS_RL`,
`CG_1ST_PLYR_HITS_LG`, `CG_1ST_PLYR_HITS_RG`, and
`CG_1ST_PLYR_HITS_PG` ownerdraw set. Repo-wide parity remains **98%**
because unrelated compatibility, source-legacy, online-service, and packaging
surfaces are unchanged.

Completed work:

1. Rechecked the retail `cgamex86.dll` dispatcher, `0x100369D0` weapon-hit
   leaf, and `0x1002E2B0` placement weapon resolver for raw ownerdraw cases
   `0x84` through `0x88`.
2. Confirmed the selected hit band resolves to GL/RL/LG/RG/PG weapon indexes
   `4` through `8`, reads the `data_10A603CC` hit cache, and formats through
   the retail `%d` literal.
3. Pinned the qagame-to-cgame compact `accuracy_hits` wiring for the selected
   middle weapon band.
4. Added focused structural coverage for constants, retail target-group
   membership, resolver returns, cache reads, weapon mapping, server send
   path, cgame parse path, dispatcher guard, callback absence, and
   direct-switch absence.
5. Refreshed the cgame ownerdraw and mapping ledgers for the selected five.

### Task A158: Close flag/harvester/key cgame ownerdraw parity [COMPLETED]
Priority: High
Primary areas: `src/code/cgame/cg_newdraw.c`,
`tests/test_cgame_displaycontext_parity.py`,
`tests/test_cgame_ownerdraw_text_parity.py`,
`docs/reverse-engineering/cg-ownerdrawtype-parity-index.md`,
`docs/reverse-engineering/cgame-mapping.md`
Parity estimate: **before 99% -> after 100%** for the selected
`CG_PLAYER_HASFLAG`, `CG_PLAYER_HASFLAG2D`, `CG_HARVESTER_SKULLS`,
`CG_HARVESTER_SKULLS2D`, and `CG_PLAYER_HASKEY` ownerdraw set.
Repo-wide parity remains **98%** because unrelated compatibility,
source-legacy, online-service, and packaging surfaces are unchanged.

Completed work:

1. Rechecked the retail `cgamex86.dll` dispatcher and HLIL leaves for raw
   ownerdraw cases `0x37`, `0x38`, `0x39`, `0x3A`, and `0x3B`.
2. Corrected the Harvester 3D cube ownerdraw geometry to match the retail
   `rect->y + 5` offset while preserving the forced-2D `x + 3, y + 16`
   cube-icon path.
3. Confirmed the carried-flag ownerdraw keeps the retail 4-pixel 3D inset,
   forced-2D zero inset, and 1FCTF neutral-flag `dropflag` prompt.
4. Confirmed the carried-key ownerdraw uses the replicated key-mask stat,
   `IT_KEY` tag lookup, item visual registration, and half-width icon overlap.
5. Added focused structural coverage for constants, dispatcher routes,
   `CG_GetValue` participation, width/key callback absence, display-context
   wiring, retail HLIL anchors, and menu reachability.
6. Refreshed the cgame ownerdraw and mapping ledgers for the selected five.

### Task A157: Close selected 127-131 cgame ownerdraw parity [COMPLETED]
Priority: High
Primary areas: `src/code/cgame/cg_newdraw.c`,
`src/code/cgame/cg_servercmds.c`, `src/code/game/g_cmds.c`,
`tests/test_cgame_displaycontext_parity.py`,
`docs/reverse-engineering/cg-ownerdrawtype-parity-index.md`,
`docs/reverse-engineering/cgame-mapping.md`
Parity estimate: **before 99% -> after 100%** for the selected
`CG_1ST_PLYR_FRAGS_NG`, `CG_1ST_PLYR_FRAGS_PL`,
`CG_1ST_PLYR_FRAGS_HMG`, `CG_1ST_PLYR_HITS_MG`, and
`CG_1ST_PLYR_HITS_SG` ownerdraw set. Repo-wide parity remains **98%**
because unrelated compatibility, source-legacy, online-service, and packaging
surfaces are unchanged.

Completed work:

1. Rechecked the retail `cgamex86.dll` dispatcher, `0x100368A0`
   weapon-frag leaf, `0x100369D0` weapon-hit leaf, and `0x1002E2B0`
   placement weapon resolver for raw ownerdraw cases `0x7f` through `0x83`.
2. Tightened placement weapon-hit formatting to the retail `%d` literal,
   matching the shared `data_10068E44` format used by the hit helper.
3. Confirmed the selected frag tail is backed by the compact frag order and
   the selected hit head is backed by the compact `accuracy_hits` order across
   qagame send and cgame parse paths.
4. Added focused structural coverage for constants, retail target-group
   membership, resolver returns, cache reads, weapon mapping, server send
   path, cgame parse path, dispatcher guard, callback absence, and
   direct-switch absence.
5. Refreshed the cgame ownerdraw and mapping ledgers for the selected five.

### Task A156: Harden selected 86-90 cgame endgame ownerdraw parity [COMPLETED]
Priority: High
Primary areas: `src/code/cgame/cg_newdraw.c`,
`src/code/cgame/cg_main.c`,
`tests/test_cgame_displaycontext_parity.py`,
`docs/reverse-engineering/cg-ownerdrawtype-parity-index.md`,
`docs/reverse-engineering/cgame-mapping.md`
Parity estimate: **before 99% -> after 100%** for the selected
`CG_2NDPLACE`, `CG_2ND_PLACE_SCORE`, `CG_PLAYER_OBIT`,
`CG_AREA_NEW_CHAT`, and `CG_PLYR_END_GAME_SCORE` ownerdraw set.
Repo-wide parity remains **98%** because unrelated compatibility,
source-legacy, online-service, and packaging surfaces are unchanged.

Completed work:

1. Rechecked the retail `cgamex86.dll` dispatcher and HLIL call sites for raw
   ownerdraw cases `0x56`, `0x57`, `0x58`, `0x59`, and `0x5A`.
2. Confirmed current source preserves the compact second-place score helper,
   wide second-place score branch, obituary feed renderer, timed chat stack,
   and local endgame summary text family.
3. Added focused structural coverage for source switch wiring,
   display-context callback absence, shipped menu reachability, competitive
   cache refresh, and helper behavior for the selected endgame slice.
4. Refreshed the ownerdraw parity index and cgame mapping notes for this
   selected batch.

### Task A155: Harden selected 91-95 cgame selected/follow ownerdraw parity [COMPLETED]
Priority: High
Primary areas: `src/code/cgame/cg_newdraw.c`,
`src/code/cgame/cg_main.c`,
`tests/test_cgame_displaycontext_parity.py`,
`docs/reverse-engineering/cg-ownerdrawtype-parity-index.md`,
`docs/reverse-engineering/cgame-mapping.md`
Parity estimate: **before 99% -> after 100%** for the selected
`CG_PLYR_BEST_WEAPON_NAME`, `CG_SELECTED_PLYR_TEAM_COLOR`,
`CG_SELECTED_PLYR_ACCURACY`, `CG_FOLLOW_PLAYER_NAME`, and
`CG_FOLLOW_PLAYER_NAME_EX` ownerdraw set. Repo-wide parity remains
**98%** because unrelated compatibility, source-legacy, online-service, and
packaging surfaces are unchanged.

Completed work:

1. Rechecked the retail `cgamex86.dll` dispatcher and HLIL call sites for raw
   ownerdraw cases `0x5B`, `0x5C`, `0x5D`, `0x5E`, and `0x5F`.
2. Confirmed current source preserves the selected-score bounds checks,
   selected-client team-color fill, selected accuracy text path, best-weapon
   label table, and shared follow-name prefix/tint/alignment helper.
3. Added focused structural coverage for source switch wiring,
   display-context callback absence, shipped menu reachability, and the helper
   behavior that backs each selected ownerdraw.
4. Refreshed the ownerdraw parity index and cgame mapping notes for this
   selected/follow-player slice.

### Task A154: Harden selected 81-85 cgame scoreboard ownerdraw parity [COMPLETED]
Priority: High
Primary areas: `src/code/cgame/cg_newdraw.c`,
`src/code/cgame/cg_main.c`,
`src/code/cgame/cg_servercmds.c`,
`src/code/game/g_main.c`,
`tests/test_cgame_displaycontext_parity.py`,
`docs/reverse-engineering/cg-ownerdrawtype-parity-index.md`,
`docs/reverse-engineering/cgame-mapping.md`
Parity estimate: **before 99% -> after 100%** for the selected
`CG_SPECTATORS`, `CG_MATCH_WINNER`, `CG_1STPLACE`,
`CG_1ST_PLACE_SCORE`, and `CG_1STPLACE_PLYR_MODEL` ownerdraw set.
Repo-wide parity remains **98%** because unrelated compatibility,
source-legacy, online-service, and packaging surfaces are unchanged.

Completed work:

1. Rechecked the retail `cgamex86.dll` dispatcher and HLIL call sites for raw
   ownerdraw cases `0x51`, `0x52`, `0x53`, `0x54`, and `0x55`.
2. Confirmed current source preserves the retail spectator-cache gate,
   match-winner text branch, compact score helper, wide first-place
   configstring line, and first-place model/profile preview path.
3. Added focused structural coverage for source switch wiring, display-context
   callback absence, qagame/cgame configstring producer-consumer paths, and
   shipped menu reachability.
4. Refreshed the ownerdraw parity index and cgame mapping notes for this
   selected scoreboard/endgame slice.

### Task A153: Close renderer post-process command payload wiring [COMPLETED]
Priority: High
Primary areas: `src/code/renderer/tr_backend.c`,
`tests/test_renderer_post_process_parity.py`,
`tests/test_renderer_internal_helper_mapping_parity.py`
Parity estimate: **before 99.99% -> after 100%** for the scoped renderer
post-process command payload wiring lane. The strict renderer estimate remains
**100%** and repo-wide parity remains **98%** because unrelated portability,
online-service, packaging, and source-legacy surfaces are unchanged.

Completed work:

1. Rechecked the retail `quakelive_steam.exe` HLIL for
   `RB_ColorCorrectPostProcessCommand @ 0x00436DC0`,
   `RB_BloomPostProcessCommand @ 0x00436EC0`,
   `R_AddBloomPostProcessCommand @ 0x004384D0`, and
   `R_AddColorCorrectPostProcessCommand @ 0x0043CD10`.
2. Rewired the color-correct pass to consume the queued command texture and
   program handles instead of re-reading the live `s_postProcess` handles.
3. Rewired the bloom downsample, bright-pass, blur, quarter-pass, combine, and
   fallback blit path to consume the queued bloom command payload while keeping
   framebuffer binding under the recovered retail render-target owner.
4. Added focused structural coverage that pins command payload consumption for
   color-correct and bloom execution.

### Task A152: Close referenced-pak publication parity [COMPLETED]
Priority: High
Primary areas: `src/code/qcommon/files.c`,
`tests/fs_searchpath_harness.c`, `tests/test_fs_search_paths.py`,
`tests/test_engine_cvar_retail_parity.py`
Parity estimate: **before 99% -> after 100%** for the scoped
`sv_referencedPaks` / `sv_referencedPakNames` filesystem publication and
client autodownload decision lane. Repo-wide parity remains **98%** because
unrelated compatibility, portability, online-service, packaging, and
source-legacy surfaces are unchanged.

Completed work:

1. Rechecked the retail `quakelive_steam.exe` HLIL for
   `FS_ReferencedPakChecksums` at `0x004D1DC0` and
   `FS_ReferencedPakNames` at `0x004D1E20`.
2. Removed the legacy Quake III fs_game-wide publication rule from the
   referenced-pak checksum and name builders so Quake Live now publishes only
   pk3s whose retail reference flags are nonzero.
3. Kept the existing server `sv_referencedPaks` /
   `sv_referencedPakNames` publication and client
   `FS_PureServerSetReferencedPaks` parse wiring intact.
4. Added filesystem-harness coverage proving an unreferenced mod pk3 is not
   published until its reference flag is set, plus source-visible HLIL guards
   for the recovered retail flag-only condition.

### Task A151: Tighten native game API handoff parity [COMPLETED]
Priority: High
Primary areas: `src/code/server/sv_game.c`,
`src/code/client/cl_cgame.c`,
`tests/test_game_native_export_helper_parity.py`
Parity estimate: **before 99.9% -> after 100%** for the scoped native
qagame/cgame API-version handoff and retained QVM fallback ownership slice.
Repo-wide parity remains **98%** because unrelated portability,
online-service, packaging, and source-legacy surfaces are unchanged.

Completed work:

1. Rechecked the retail `qagamex86.dll` and `cgamex86.dll` `dllEntry`
   evidence: qagame reports native API `10`, and cgame reports native API `8`.
2. Split the native-load API constants from the legacy VM fallback constants
   at the qagame and cgame loader call sites.
3. Added structural coverage that pins native API handoff, legacy fallback API
   handoff, and the retained retail QVM fallback ownership note.
4. Revalidated the focused native-export and qcommon fallback-VM parity probes.

### Task A150: Close item/score/race cgame ownerdraw parity [COMPLETED]
Priority: High
Primary areas: `src/code/cgame/cg_newdraw.c`,
`tests/test_cgame_ownerdraw_text_parity.py`,
`tests/test_cgame_displaycontext_parity.py`,
`docs/reverse-engineering/cg-ownerdrawtype-parity-index.md`,
`docs/reverse-engineering/cgame-mapping.md`
Parity estimate: **before 99% -> after 100%** for the selected
`CG_PLAYER_ITEM`, `CG_PLAYER_SCORE`, `CG_RACE_STATUS`, `CG_RACE_TIMES`,
and `CG_ONEFLAG_STATUS` ownerdraw set. Repo-wide parity remains **98%**
because unrelated compatibility, source-legacy, and packaging surfaces are
unchanged.

Completed work:

1. Rechecked the retail `cgamex86.dll` dispatcher and HLIL leaves for raw
   ownerdraw cases `0x32`, `0x33`, `0x34`, `0x35`, and `0x36`.
2. Confirmed current source preserves the retail holdable item branch, compact
   score wrapper, Race status/timing shared leaf, callback participation, and
   shipped menu reachability for the selected five.
3. Restored the `CG_ONEFLAG_STATUS` visible leaf to the retail
   `gfx/2d/flag_status/*` shader bank, white draw color, and stolen-flag
   score-dependent y offset.
4. Added focused structural coverage for constants, dispatcher routes,
   `CG_GetValue` participation, width/key callback absence, display-context
   wiring, retail HLIL anchors, and menu reachability.
5. Refreshed the cgame ownerdraw and mapping ledgers for the selected five.

### Task A149: Close selected 122-126 cgame ownerdraw parity [COMPLETED]
Priority: High
Primary areas: `src/code/cgame/cg_newdraw.c`,
`src/code/cgame/cg_servercmds.c`, `src/code/game/g_cmds.c`,
`tests/test_cgame_displaycontext_parity.py`,
`docs/reverse-engineering/cg-ownerdrawtype-parity-index.md`,
`docs/reverse-engineering/cgame-mapping.md`
Parity estimate: **before 99% -> after 100%** for the selected
`CG_1ST_PLYR_FRAGS_LG`, `CG_1ST_PLYR_FRAGS_RG`,
`CG_1ST_PLYR_FRAGS_PG`, `CG_1ST_PLYR_FRAGS_BFG`, and
`CG_1ST_PLYR_FRAGS_CG` ownerdraw set. Repo-wide parity remains **98%**
because unrelated compatibility, source-legacy, and packaging surfaces are
unchanged.

Completed work:

1. Rechecked the retail `cgamex86.dll` dispatcher, `0x100368A0` weapon-frag
   leaf, and `0x1002E2B0` placement weapon resolver for raw ownerdraw cases
   `0x7a` through `0x7e`.
2. Confirmed the retail resolver maps LG/RG/PG/BFG to weapon indexes `6`
   through `9` and maps CG to `0xd`, preserving the Quake Live enum gap before
   nailgun/prox/chaingun.
3. Pinned the qagame-to-cgame compact `scorestats` weapon-frag wiring around
   the retail LG, RG, PG, BFG, CG lane inside the full frag order.
4. Added focused structural coverage for constants, retail target-group
   membership, resolver returns, weapon mapping, server send path, cgame parse
   path, dispatcher guard, callback absence, and direct-switch absence.
5. Refreshed the cgame ownerdraw and mapping ledgers for the selected five.

### Task A148: Harden selected 75-79 cgame award ownerdraw parity [COMPLETED]
Priority: High
Primary areas: `tests/test_cgame_displaycontext_parity.py`,
`docs/reverse-engineering/cg-ownerdrawtype-parity-index.md`,
`docs/reverse-engineering/cgame-mapping.md`
Parity estimate: **before 99% -> after 100%** for the selected
`CG_MOST_VALUABLE_OFFENSIVE_PLYR`,
`CG_MOST_VALUABLE_DEFENSIVE_PLYR`, `CG_MOST_VALUABLE_PLYR`,
`CG_BEST_ITEMCONTROL_PLYR`, and `CG_MOST_ACCURATE_PLYR` ownerdraw set.
Repo-wide parity remains **98%** because unrelated compatibility,
source-legacy, and packaging surfaces are unchanged.

Completed work:

1. Rechecked the retail `cgamex86.dll` ownerdraw dispatcher route for raw
   cases `0x4b` through `0x4f`, all landing on the shared award-player image
   leaf at `0x1003A0D0`.
2. Verified the selected ownerdraws are handled before the source
   `CG_OwnerDraw` switch by `CG_DrawAwardPlayer`, fed by qagame-produced
   `CS_AWARD_*` configstrings and rendered through the profile-image helper.
3. Added focused structural coverage for constants, retail target routing,
   qagame producer wiring, cgame configstring consumption, shipped
   end-scoreboard menu reachability, display-context callbacks, and absence
   from value/width/key callback routes.
4. Refreshed the cgame ownerdraw and mapping ledgers so the award lane now
   documents the recovered configstring-backed profile-image path.

### Task A147: Close selected 117-121 cgame ownerdraw parity [COMPLETED]
Priority: High
Primary areas: `src/code/cgame/cg_newdraw.c`,
`src/code/cgame/cg_servercmds.c`, `src/code/game/g_cmds.c`,
`tests/test_cgame_displaycontext_parity.py`,
`docs/reverse-engineering/cg-ownerdrawtype-parity-index.md`,
`docs/reverse-engineering/cgame-mapping.md`
Parity estimate: **before 99% -> after 100%** for the selected
`CG_1ST_PLYR_FRAGS_G`, `CG_1ST_PLYR_FRAGS_MG`,
`CG_1ST_PLYR_FRAGS_SG`, `CG_1ST_PLYR_FRAGS_GL`, and
`CG_1ST_PLYR_FRAGS_RL` ownerdraw set. Repo-wide parity remains **98%**
because unrelated compatibility, source-legacy, and packaging surfaces are
unchanged.

Completed work:

1. Rechecked the retail `cgamex86.dll` dispatcher and HLIL leaf at
   `0x100368A0`, including the placement weapon-index helper, weapon-frag
   cache read, `%d` format literal, and baseline text paint.
2. Tightened the placement weapon-frag formatter to the retail `%d` literal.
3. Pinned the qagame-to-cgame compact `scorestats` weapon-frag wiring around
   the retail G, MG, SG, GL, RL prefix order.
4. Added focused structural coverage for constants, retail target-group
   membership, weapon mapping, server send path, cgame parse path, dispatcher
   guard, callback absence, and direct-switch absence.
5. Refreshed the cgame ownerdraw and mapping ledgers for the selected five.

### Task A146: Close health/ammo cgame ownerdraw parity [COMPLETED]
Priority: High
Primary areas: `tests/test_cgame_ownerdraw_text_parity.py`,
`docs/reverse-engineering/cg-ownerdrawtype-parity-index.md`,
`docs/reverse-engineering/cgame-mapping.md`
Parity estimate: **before 99% -> after 100%** for the selected
`CG_PLAYER_HEALTH_BAR_100`, `CG_PLAYER_HEALTH_BAR_200`,
`CG_PLAYER_AMMO_ICON`, `CG_PLAYER_AMMO_ICON2D`, and `CG_PLAYER_AMMO_VALUE`
ownerdraw set. Repo-wide parity remains **98%** because unrelated
compatibility, source-legacy, and packaging surfaces are unchanged.

Completed work:

1. Rechecked the retail `cgamex86.dll` dispatcher and HLIL leaves for raw
   ownerdraw cases `0x2d`, `0x2e`, `0x2f`, `0x30`, and `0x31`.
2. Confirmed current source preserves the retail primary/excess health-bar
   split, ammo icon 2D/3D branches, finite ammo text/shader rendering, and
   infinite-ammo icon fallback.
3. Added focused structural coverage for constants, dispatcher routes,
   `CG_GetValue` participation, width/key callback absence, display-context
   wiring, and shipped menu reachability.

### Task A145: Close local status cgame ownerdraw parity [COMPLETED]
Priority: High
Primary areas: `tests/test_cgame_ownerdraw_text_parity.py`,
`docs/reverse-engineering/cg-ownerdrawtype-parity-index.md`,
`docs/reverse-engineering/cgame-mapping.md`
Parity estimate: **before 99% -> after 100%** for the selected
`CG_PLAYER_ARMOR_VALUE`, `CG_PLAYER_ARMOR_BAR_100`,
`CG_PLAYER_ARMOR_BAR_200`, `CG_ARMORTIERED_COLORIZED`, and
`CG_PLAYER_HEALTH` ownerdraw set. Repo-wide parity remains **98%** because
unrelated compatibility, source-legacy, and packaging surfaces are unchanged.

Completed work:

1. Rechecked the retail `cgamex86.dll` dispatcher and HLIL leaves for raw
   ownerdraw cases `0x28`, `0x29`, `0x2a`, `0x2b`, and `0x2c`.
2. Confirmed current source preserves the retail armor/health
   shader-or-aligned-number paths, armor primary/excess bar clipping, and
   replicated armor-tier color fill.
3. Added focused structural coverage for constants, dispatcher routes,
   `CG_GetValue` participation, width/key callback absence, display-context
   wiring, and shipped menu reachability.

### Task A144: Close selected 112-116 cgame ownerdraw parity [COMPLETED]
Priority: High
Primary areas: `src/code/cgame/cg_newdraw.c`,
`tests/test_cgame_displaycontext_parity.py`,
`docs/reverse-engineering/cg-ownerdrawtype-parity-index.md`,
`docs/reverse-engineering/cgame-mapping.md`
Parity estimate: **before 96% -> after 100%** for the selected
`CG_1ST_PLYR_ACC`, `CG_1ST_PLYR_FLAG`, `CG_1ST_PLYR_AVATAR`,
`CG_1ST_PLYR_TIMEOUT_COUNT`, and `CG_1ST_PLYR_HEALTH_ARMOR` ownerdraw
set. Repo-wide parity remains **98%** because unrelated compatibility,
source-legacy, and packaging surfaces are unchanged.

Completed work:

1. Rechecked the retail `cgamex86.dll` dispatcher and HLIL leaves for
   `0x10036570`, `0x10036720`, `0x100366A0`, `0x10033040`, plus the raw
   `0x73` no-op gap.
2. Tightened total accuracy formatting to the retail `%d%%` literal and kept
   the placement flag route on the cached country-flag shader path.
3. Restored the placement avatar selection order: native avatar handle when
   `cg_drawProfileImages` and a replicated identity are available, then the
   cached model icon fallback, with no source-only dimming or armor fallback.
4. Rebuilt the spectator comparison ownerdraw around retail-style health and
   armor bands, including local playerState stat reads, tracked-client
   fallback, fixed retail colors, the short-lived damage-loss segment,
   primary-slot right alignment, cvar color gating, and removal of the
   non-retail text/marker overlay.
5. Added focused structural coverage for the five selected ownerdraw IDs and
   refreshed the cgame ownerdraw and mapping ledgers.

### Task A143: Close spectator/player-preview cgame ownerdraw parity [COMPLETED]
Priority: High
Primary areas: `tests/test_cgame_ownerdraw_text_parity.py`,
`docs/reverse-engineering/cg-ownerdrawtype-parity-index.md`,
`docs/reverse-engineering/cgame-mapping.md`
Parity estimate: **before 99% -> after 100%** for the selected
`CG_SPEC_MESSAGES`, `CG_PLAYER_HEAD`, `CG_PLAYERMODEL`,
`CG_PLAYER_ARMOR_ICON`, and `CG_PLAYER_ARMOR_ICON2D` ownerdraw set.
Repo-wide parity remains **98%** because unrelated compatibility,
source-legacy, and packaging surfaces are unchanged.

Completed work:

1. Rechecked the retail `cgamex86.dll` dispatcher and HLIL leaves for raw
   ownerdraw cases `0x23`, `0x24`, `0x25`, `0x26`, and `0x27`.
2. Confirmed current source preserves the spectator message copy family, local
   head damage/idle interpolation, tracked/local model preview, and shared
   armor 2D/3D icon behavior.
3. Added focused structural coverage for constants, dispatcher routes, shipped
   menu reachability, and absence from the value/width/key callback paths.

### Task A142: Close vote shot/timer cgame ownerdraw parity [COMPLETED]
Priority: High
Primary areas: `tests/test_cgame_ownerdraw_text_parity.py`,
`docs/reverse-engineering/cg-ownerdrawtype-parity-index.md`,
`docs/reverse-engineering/cgame-mapping.md`
Parity estimate: **before 99% -> after 100%** for the selected
`CG_VOTESHOT1`, `CG_VOTESHOT2`, `CG_VOTESHOT3`, `CG_VOTECOUNT3`, and
`CG_VOTETIMER` ownerdraw set. Repo-wide parity remains **98%** because
unrelated compatibility, source-legacy, and packaging surfaces are unchanged.

Completed work:

1. Rechecked the retail `cgamex86.dll` dispatcher and HLIL leaves for raw
   ownerdraw cases `0x19`, `0x1a`, `0x1b`, `0x21`, and `0x22`.
2. Confirmed current source preserves the retail vote preview path, default
   preview fallback, third vote-count label, timer text family, cvar payload
   wiring, and absence of value/width/key callback participation.
3. Added focused structural coverage for dispatcher slots, shipped menu usage,
   `ui_vote%s%i` shot/count payload transport, and vote active/string bridge
   state used by the timer menu.

### Task A141: Close vote name/count cgame ownerdraw parity [COMPLETED]
Priority: High
Primary areas: `src/code/cgame/cg_newdraw.c`,
`tests/test_cgame_ownerdraw_text_parity.py`,
`tests/test_cgame_displaycontext_parity.py`,
`docs/reverse-engineering/cg-ownerdrawtype-parity-index.md`,
`docs/reverse-engineering/cgame-mapping.md`
Parity estimate: **before 95% -> after 100%** for the selected
`CG_VOTENAME1`, `CG_VOTENAME2`, `CG_VOTENAME3`, `CG_VOTECOUNT1`, and
`CG_VOTECOUNT2` ownerdraw set. Repo-wide parity remains **98%** because
unrelated compatibility, source-legacy, and packaging surfaces are unchanged.

Completed work:

1. Rechecked the retail `cgamex86.dll` dispatcher and HLIL leaves for raw
   ownerdraw cases `0x1c` through `0x20`.
2. Restored the retail text-width alignment path for vote-name labels while
   preserving the `Name` then `Map` fallback payload order and raw rect-y
   paint origin.
3. Added focused structural coverage for dispatcher slots, display-context
   callbacks, `ui_vote%s%i` name/count payload wiring, shipped menu usage, and
   absence of value/width/key callback participation.

### Task A140: Close selected 107-111 cgame ownerdraw parity [COMPLETED]
Priority: High
Primary areas: `src/code/cgame/cg_newdraw.c`,
`tests/test_cgame_displaycontext_parity.py`,
`docs/reverse-engineering/cg-ownerdrawtype-parity-index.md`,
`docs/reverse-engineering/cgame-mapping.md`
Parity estimate: **before 98% -> after 100%** for the selected
`CG_1ST_PLYR_DEATHS`, `CG_1ST_PLYR_DMG`, `CG_1ST_PLYR_TIME`,
`CG_1ST_PLYR_PING`, and `CG_1ST_PLYR_WINS` ownerdraw set. Repo-wide
parity remains **98%** because unrelated compatibility, source-legacy, and
packaging surfaces are unchanged.

Completed work:

1. Rechecked the retail `cgamex86.dll` dispatcher and HLIL leaves for
   `0x10036320`, `0x10036770`, `0x10036070`, and `0x10036450`, plus the raw
   `0x6d` no-op gap.
2. Tightened the placement ping ownerdraw to use the retail `>40` and `>80`
   warning-color thresholds, forced blue to `0.0`, and forced alpha to `0.8`
   before painting.
3. Restored the wins slot to the retail preformatted `%d/%d` wins/losses text
   path rather than the source-only bare wins count.
4. Added focused structural coverage for the five selected ownerdraw IDs,
   including dispatcher routes, metric helpers, the no-op time case, retail
   color evidence, and the absence of value/width/key callback wiring.
5. Updated the cgame ownerdraw and mapping ledgers with the exact placement
   metric and ping-color evidence.

### Task A139: Close vote gametype/map cgame ownerdraw parity [COMPLETED]
Priority: High
Primary areas: `src/code/cgame/cg_newdraw.c`,
`tests/test_cgame_ownerdraw_text_parity.py`,
`tests/test_cgame_displaycontext_parity.py`,
`docs/reverse-engineering/cg-ownerdrawtype-parity-index.md`,
`docs/reverse-engineering/cgame-mapping.md`
Parity estimate: **before 94% -> after 100%** for the selected
`CG_VOTEGAMETYPE1`, `CG_VOTEGAMETYPE2`, `CG_VOTEGAMETYPE3`,
`CG_VOTEMAP1`, and `CG_VOTEMAP2` ownerdraw set. Repo-wide parity remains
**98%** because unrelated compatibility, source-legacy, and packaging
surfaces are unchanged.

Completed work:

1. Rechecked the retail `cgamex86.dll` dispatcher and HLIL leaves for raw
   ownerdraw cases `0x13` through `0x17`.
2. Restored the retail text-width alignment path for vote gametype and raw-map
   labels while preserving the gametype row's `rect->y - 8.0f` paint bias.
3. Added focused structural coverage for dispatcher slots, display-context
   callbacks, `ui_vote%s%i` cvar payload wiring, menu reachability, and the
   absence of value/width/key callback participation.

### Task A138: Tighten 83-87 cgame placement ownerdraw parity [COMPLETED]
Priority: High
Primary areas: `src/code/cgame/cg_newdraw.c`,
`tests/test_cgame_displaycontext_parity.py`,
`docs/reverse-engineering/cg-ownerdrawtype-parity-index.md`,
`docs/reverse-engineering/cgame-mapping.md`
Parity estimate: **before 98% -> after 100%** for the selected
`CG_1STPLACE`, `CG_1ST_PLACE_SCORE`, `CG_1STPLACE_PLYR_MODEL`,
`CG_2NDPLACE`, and `CG_2ND_PLACE_SCORE` ownerdraw set. Repo-wide parity
remains **98%** because unrelated compatibility, source-legacy, and packaging
surfaces are unchanged.

Completed work:

1. Rechecked the retail `cgamex86.dll` HLIL and committed Ghidra dispatcher for
   raw ownerdraw cases `0x53` through `0x57`.
2. Restored compact placement score formatting through the shared retail score
   helper, including Race `[-]Ns` text and the `SCORE_NOT_PRESENT` skip.
3. Wired the compact placement ownerdraws into the competitive score-cache
   touch path used by HUD-only placement layouts.
4. Tightened the wide second-place row to use the retail spectator-team gate
   before choosing between the local player row and cached runner-up row.
5. Refreshed focused structural tests and ownerdraw/mapping ledgers for the
   completed placement lane.

### Task A137: Close selected 100-105 cgame ownerdraw parity [COMPLETED]
Priority: High
Primary areas: `src/code/cgame/cg_newdraw.c`,
`tests/test_cgame_displaycontext_parity.py`,
`docs/reverse-engineering/cg-ownerdrawtype-parity-index.md`
Parity estimate: **before 98% -> after 100%** for the selected
`CG_TEAM_PLYR_COUNT`, `CG_ENEMY_PLYR_COUNT`, `CG_1ST_PLYR`,
`CG_1ST_PLYR_READY`, and `CG_1ST_PLYR_SCORE` ownerdraw set. Repo-wide
parity remains **98%** because unrelated compatibility, source-legacy, and
packaging surfaces are unchanged.

Completed work:

1. Rechecked the retail `cgamex86.dll` dispatcher and HLIL leaves for
   `0x10033650`, `0x10035BD0`, `0x10037BA0`, and `0x10035F30`.
2. Corrected the friendly/enemy round player-count ownerdraws to paint the
   cached team count at the raw ownerdraw origin, matching the retail
   `sub_10033650` text path instead of the older centered source behavior.
3. Added focused structural coverage for the five selected ownerdraw IDs,
   including dispatcher routes, pre-switch `CG_1ST_PLYR_READY` handling, raw
   text origins, and the absence of value/width/key callback wiring.
4. Updated the cgame ownerdraw and mapping ledgers with the raw-origin
   player-count evidence.

### Task A136: Close gametype cgame ownerdraw parity [COMPLETED]
Priority: High
Primary areas: `tests/test_cgame_ownerdraw_text_parity.py`,
`docs/reverse-engineering/cg-ownerdrawtype-parity-index.md`,
`docs/reverse-engineering/cgame-mapping.md`
Parity estimate: **before 98% -> after 100%** for the selected
`CG_GAME_TYPE`, `CG_GAME_TYPE_ICON`, and `CG_GAME_TYPE_MAP` ownerdraw trio.
Repo-wide parity remains **98%** because unrelated compatibility,
source-legacy, and packaging surfaces are unchanged.

Completed work:

1. Rechecked the retail `cgamex86.dll` dispatcher evidence for raw ownerdraw
   cases `4`, `5`, and `6`, mapped to `CG_DrawGameType`,
   `CG_DrawGameTypeIcon`, and `CG_DrawGameTypeMap`.
2. Confirmed the current source preserves the direct draw routes, keeps only
   `CG_GAME_TYPE` on the ownerdraw-width callback, and leaves the trio out of
   the value and key-handler callbacks.
3. Added focused structural coverage for the dispatcher, display-context
   callbacks, shipped menu reachability, gametype icon registration path, and
   intro-panel gametype-map wiring.

### Task A135: Restore retail post-process gamma capture path [COMPLETED]
Priority: High
Primary areas: `src/code/renderer/tr_init.c`,
`docs/renderer_cvar_matrix.md`, `tests/test_engine_cvar_retail_parity.py`
Parity estimate: **before 99% -> after 100%** for the selected
renderer post-process gamma ownership lane. Repo-wide parity remains **98%**
because unrelated compatibility, source-legacy, and packaging surfaces are
unchanged.

Completed work:

1. Rechecked the retail `quakelive_steam.exe` HLIL/Ghidra evidence for
   `r_enablePostProcess`, `r_enableColorCorrect`, the `p_gammaRecip`
   color-correct uniform, and the legacy Win32 gamma ramp fallback.
2. Removed the reconstruction-only `r_enablePostProcess` force-off so the
   shader-backed color-correct pass owns final `r_gamma` output by default,
   matching retail and improving Windows desktop/PrintScreen capture parity.
3. Updated cvar parity tests and renderer cvar documentation to reflect the
   restored retail default and fallback boundary.

### Task A134: Close player/opponent UI ownerdraw parity [COMPLETED]
Priority: High
Primary areas: `src/code/ui/ui_main.c`, `tests/test_ui_menu_files.py`,
`docs/reverse-engineering/ui-ownerdrawtype-parity-index.md`
Parity estimate: **before 76% -> after 100%** for the selected
`UI_PLAYERMODEL`, `UI_OPPONENTMODEL`, and `UI_OPPONENT_NAME` ownerdraw trio.
Repo-wide parity remains **98%** because unrelated compatibility,
source-legacy, and packaging surfaces are unchanged.

Completed work:

1. Rechecked the retail `uix86.dll` HLIL/Ghidra evidence for
   `UI_DrawPlayerModel` at `0x10005690`, `UI_DrawOpponent` at `0x10006730`,
   `UI_DrawOpponentName` at `0x100068F0`, and `UI_OwnerDrawHandleKey` at
   `0x1000A820`.
2. Rebuilt `UI_PLAYERMODEL` around the retail `model`/`headmodel` cvar reads,
   empty team name, `cg_loadout`/`cg_weaponPrimary` primary weapon selection,
   weapon item validation, heavy-machinegun fallback for invalid primary
   weapon values, retail `5/210/0` view angles, and the pre-draw cached
   `playerInfo_t` reset observed in HLIL.
3. Tightened `UI_OPPONENTMODEL` cvar refresh to use buffered
   `ui_opponentModel` reads before rebuilding and drawing the cached
   `playerInfo_t`, including the retail `0/170/0` view angles and pre-draw
   cached preview reset.
4. Tightened `UI_OPPONENT_NAME` to the retail buffered `ui_opponentName` paint
   path, kept the empty width-helper case, and removed the source-only
   ownerdraw key route that retail does not dispatch.
5. Updated the UI ownerdraw parity index so all retail-routed `Needs check`
   rows are now checked.

Verification:

- `python -m pytest tests/test_ui_menu_files.py -k "player_opponent_ownerdraws or handicap_netsource_netfilter"`
  - Result: `2 passed, 76 deselected`.
- `python -m pytest tests/test_ui_menu_files.py`
  - Result: `78 passed`.

### Task A133: Close front-panel cgame ownerdraw parity [COMPLETED]
Priority: High
Primary areas: `tests/test_cgame_ownerdraw_text_parity.py`,
`docs/reverse-engineering/cg-ownerdrawtype-parity-index.md`,
`docs/reverse-engineering/cgame-mapping.md`
Parity estimate: **before 98% -> after 100%** for the selected
`CG_SERVER_SETTINGS`, `CG_STARTING_WEAPONS`, and `CG_GAME_LIMIT` ownerdraw
trio. Repo-wide parity remains **98%** because no unrelated compatibility or
runtime-evidence surfaces changed.

Completed work:

1. Rechecked the retail `CG_OwnerDraw` dispatcher cases `1`, `2`, and `3`
   against the committed Ghidra/HLIL evidence.
2. Confirmed `CG_SERVER_SETTINGS` stays on the custom-settings text and
   modified-weapon icon-strip leaf.
3. Confirmed `CG_STARTING_WEAPONS` stays on the `CS_LOADOUT_MASK` icon-strip
   and queued-primary loadout preview leaf.
4. Confirmed `CG_GAME_LIMIT` stays on the narrowed retail
   `Cap Limit` / `Frag Limit` / `Round Limit` / `Score Limit` label family.
5. Added focused structural coverage that guards switch wiring, display-context
   callback non-participation, menudef constants, and shipped menu reachability
   for the two shipped front-panel menu users.

### Task A132: Close objective/powerup cgame ownerdraw parity [COMPLETED]
Priority: High
Primary areas: `src/code/cgame/cg_newdraw.c`,
`tests/test_cgame_displaycontext_parity.py`,
`tests/test_cgame_hud_parity.py`,
`tests/test_game_key_item_parity.py`,
`docs/reverse-engineering/cg-ownerdrawtype-parity-index.md`,
`docs/reverse-engineering/cgame-mapping.md`
Parity estimate: **before 98% -> after 100%** for the selected
`CG_PLAYER_HASKEY`, `CG_CTF_POWERUP`, and `CG_AREA_POWERUP` ownerdraw trio.
Repo-wide parity remains **98%** because unrelated dirty worktree and runtime
evidence surfaces are unchanged.

Completed work:

1. Rechecked the retail cgame `CG_OwnerDraw` switch and leaves at
   `0x10031F90`, `0x100310F0`, and `0x10031160`.
2. Reconstructed `CG_PLAYER_HASKEY` to use the retail
   `BG_FindItemByTypeAndTag( IT_KEY, tag )` path for silver, gold, and master
   keys instead of a classname detour.
3. Confirmed `CG_CTF_POWERUP` remains the direct
   `STAT_PERSISTANT_POWERUP` item-icon ownerdraw.
4. Confirmed `CG_AREA_POWERUP` is directly wired to the retail powerup stack
   helper and has no `cg_drawSprites` or `cg_drawSpriteSelf` ownerdraw gate.
5. Updated the cgame ownerdraw index so all menudef cgame rows are now checked
   or checked retail no-ops.

### Task A131: Add full cgame ownerdraw parity index [COMPLETED]
Priority: High
Primary areas: `docs/reverse-engineering/cg-ownerdrawtype-parity-index.md`,
`tests/test_cgame_displaycontext_parity.py`
Parity estimate: **before 0% -> after 100%** for durable index coverage of
the `src/ui/menudef.h` cgame ownerdraw block. The current ledger has `327`
checked rows, `12` checked retail no-ops, and no open partial rows after the
objective/powerup ownerdraw follow-up.

Completed work:

1. Added a full tabulated listing for menudef cgame ownerdraw IDs `1..339`,
   excluding `CG_SHOW_*` flags, `UI_*` ownerdraws, and `ui_shared.h`-only
   source aliases outside the menudef range.
2. Recorded the current cgame implementation route and parity state for every
   row so future parity-picking has a stable index.
3. Added a structural test that compares the ledger rows back to the menudef
   cgame block and rejects accidental UI/visibility-flag leakage.

### Task A130: Close medal-adjacent cgame ownerdraw no-op parity [COMPLETED]
Priority: High
Primary areas: `src/code/cgame/cg_newdraw.c`,
`tests/test_cgame_displaycontext_parity.py`,
`docs/reverse-engineering/cgame-mapping.md`
Parity estimate: **before 95% -> after 100%** for the focused
`CG_COMBOKILLS`, `CG_RAMPAGES`, and `CG_MIDAIRS` cgame ownerdraw lane.
Repo-wide parity remains **98%** because unrelated dirty worktree changes and
non-Windows/runtime-evidence lanes are unchanged.

Completed work:

1. Rechecked the committed cgame ownerdraw switch evidence for
   `0x1003B0F0 -> CG_OwnerDraw` and the medal helper route at
   `0x10035340 -> CG_DrawMedal`.
2. Confirmed retail routes only `CG_ACCURACY`, `CG_ASSISTS`, `CG_CAPTURES`,
   `CG_DEFEND`, `CG_EXCELLENT`, `CG_GAUNTLET`, `CG_IMPRESSIVE`, and
   `CG_PERFECT` to the medal helper; `CG_COMBOKILLS` (`0x43`),
   `CG_RAMPAGES` (`0x48`), and `CG_MIDAIRS` (`0x49`) are absent from the
   retail ownerdraw switch.
3. Made the three absent ownerdraws explicit no-op cases in
   `CG_OwnerDraw`, preserving no menu usage, no `CG_GetValue` route, no
   `CG_OwnerDrawWidth` route, and the retail null key-handler behavior.
4. Added focused structural coverage for the retail switch absence, medal
   helper exclusion, display-context callback non-participation, and shipped
   menu reachability.

Verification:

- `python -m pytest tests/test_cgame_displaycontext_parity.py -k "combo_rampage_midair or team_pickup_timeheld_and_medal_dispatch_groups" -q`
  - Result: `2 passed, 145 deselected`.
- `python -m pytest tests/test_cgame_displaycontext_parity.py -k "combo_rampage_midair or ownerdraw_dispatch_covers_committed_retail_switch_cases or ownerdraw_width_callback" -q`
  - Result: `3 passed, 144 deselected`.

### Task A129: Close team overlay transport and drawing parity [COMPLETED]
Priority: High
Primary areas: `src/code/game/g_team.c`,
`src/code/cgame/cg_servercmds.c`, `src/code/game/bg_public.h`,
`src/code/cgame/cg_draw.c`, `tests/test_cgame_hud_parity.py`
Parity estimate: **before 98% -> after 100%** for the focused team-overlay
transport/cache and classic HUD drawing lane. Repo-wide parity remains **98%**
because unrelated dirty worktree changes and non-Windows/runtime-evidence lanes
are unchanged.

Completed work:

1. Rechecked the retail evidence for cgame `CG_DrawTeamOverlay` at
   `0x10009DA0`, cgame `CG_ParseTeamInfo` at `0x100487B0`, and qagame
   `TeamplayInfoMessage` at `0x10068490`.
2. Restored the retail eight-player overlay cap and made qagame format the
   sorted top-eight teammate set it already selected from `level.sortedClients`.
3. Kept the emitted `tinfo` row count tied to successfully serialized rows and
   guarded the cgame receiver against oversized, truncated, or invalid client
   rows before updating `sortedTeamPlayers`.
4. Matched the retail drawing gates and row body: invulnerability-expand early
   return, integer row placement, `ITEM_TEXTSTYLE_SHADOWED` host text, sans
   name/location columns, mono health/armor columns, `EF_DEAD` dead-row gating,
   and a powerup icon ladder that suppresses the neutral flag and frozen
   sentinel while preserving the invulnerability item path.
5. Added a focused parity test covering the eight-row cap, sorted top-eight
   payload order, `tinfo` row count, and receiver-side bounds.

Verification:

- `python -m pytest tests/test_cgame_hud_parity.py -k "team_overlay" -q`
  - Result: `3 passed, 29 deselected`.
- `python -m pytest tests/test_cgame_hud_parity.py tests/test_game_runframe_parity.py -q`
  - Result: `35 passed, 2 failed`; the two failures are unrelated existing
    HUD assertions for `CG_DrawTeamInfoRow` width and `CG_DrawAreaPowerUp`
    sprite gating on the dirty worktree.

### Task A128: Close map selection UI ownerdraw parity [COMPLETED]
Priority: High
Primary areas: `src/code/ui/ui_main.c`, `tests/test_ui_menu_files.py`,
`docs/reverse-engineering/ui-ownerdrawtype-parity-index.md`
Parity estimate: **before 98% -> after 100%** for the focused
`UI_ALLMAPS_SELECTION`, `UI_MAPS_SELECTION`, and `UI_STARTMAPCINEMATIC`
ownerdraw lane. Repo-wide parity remains **98%** because unrelated
compatibility and packaging surfaces are unchanged.

Completed work:

1. Rechecked the retail `uix86.dll` HLIL/Ghidra evidence for
   `UI_DrawAllMapsSelection` at `0x10006890` and `UI_DrawMapCinematic` at
   `0x10005560`.
2. Confirmed `UI_ALLMAPS_SELECTION` uses the retail shared map-name draw path
   with the net/current selector flag, guards the map index against the retail
   active map count, and has an empty width-helper case with no key handler.
3. Confirmed `UI_MAPS_SELECTION` matches the retail current-map name paint
   path and is reconstructed through the shared source helper with the current
   map selector flag.
4. Confirmed `UI_STARTMAPCINEMATIC` uses the retail map cinematic helper with
   the start/net selector flag, including map index reset, `%s.roq` lazy
   start, run/extents/draw behavior, and preview fallback.
5. Updated the ownerdraw parity index so the three selected IDs are now marked
   checked and the unchecked retail-routed set is down to
   `UI_PLAYERMODEL`, `UI_OPPONENTMODEL`, and `UI_OPPONENT_NAME`.

Verification:

- `python -m pytest tests/test_ui_menu_files.py -k "map_selection_ownerdraws"`
  - Result: `1 passed, 76 deselected`.
- `python -m pytest tests/test_ui_menu_files.py`
  - Result: `77 passed`.

### Task A127: Close server info UI ownerdraw parity [COMPLETED]
Priority: High
Primary areas: `src/code/ui/ui_main.c`, `tests/test_ui_menu_files.py`,
`docs/reverse-engineering/ui-ownerdrawtype-parity-index.md`
Parity estimate: **before 98% -> after 100%** for the focused
`UI_SERVERREFRESHDATE`, `UI_SERVERMOTD`, and `UI_GLINFO` ownerdraw lane.
Repo-wide parity remains **98%** because unrelated compatibility and packaging
surfaces are unchanged.

Completed work:

1. Rechecked the retail `uix86.dll` HLIL/Ghidra evidence for
   `UI_DrawServerRefreshDate` at `0x10008F20`, `UI_DrawServerMOTD` at
   `0x10009080`, and `UI_DrawGLInfo` at `0x100093B0`.
2. Confirmed `UI_SERVERREFRESHDATE` matches the retail active-refresh pulse
   path, server-count message, cached `ui_lastServerRefresh_%i` timestamp
   path, draw dispatcher route, and `UI_OwnerDrawWidth` route.
3. Confirmed `UI_SERVERMOTD` matches the retail MOTD scroll state,
   wraparound dual-paint behavior, and the `cl_motdString` fallback seeding to
   `Welcome to Team Arena!` before drawing.
4. Confirmed `UI_GLINFO` matches the retail vendor/version/pixel-format paint
   lines and the extension-string split/wrap behavior.
5. Confirmed none of the three selected ownerdraws has retail key-handler
   wiring, and only `UI_SERVERREFRESHDATE` participates in the width helper.
6. Updated the ownerdraw parity index so the three selected IDs are now marked
   checked and the unchecked retail-routed set reflects the remaining work.

Verification:

- `python -m pytest tests/test_ui_menu_files.py -k "server_info_ownerdraws"`
  - Result: `1 passed, 75 deselected`.
- `python -m pytest tests/test_ui_menu_files.py`
  - Result: `76 passed`.

### Task A126: Close map media UI ownerdraw parity [COMPLETED]
Priority: High
Primary areas: `src/code/ui/ui_main.c`, `tests/test_ui_menu_files.py`,
`docs/reverse-engineering/ui-ownerdrawtype-parity-index.md`
Parity estimate: **before 98% -> after 100%** for the focused
`UI_NETMAPPREVIEW`, `UI_MAPCINEMATIC`, and `UI_NETMAPCINEMATIC` ownerdraw
lane. Repo-wide parity remains **98%** because unrelated compatibility and
packaging surfaces are unchanged.

Completed work:

1. Rechecked the retail `uix86.dll` HLIL/Ghidra evidence for
   `UI_DrawMapCinematic` at `0x10005560`, `UI_DrawNetMapPreview` at
   `0x100065B0`, and `UI_DrawNetMapCinematic` at `0x10006600`.
2. Confirmed `UI_NETMAPPREVIEW` matches the retail current-server preview
   shader draw path and the `menu/art/unknownmap` fallback when no preview
   shader is available.
3. Confirmed `UI_MAPCINEMATIC` matches the retail map selector validation,
   lazy `%s.roq` cinematic start, run/extents/draw sequence, failure marker,
   preview fallback, and ownerdraw dispatcher route.
4. Confirmed `UI_NETMAPCINEMATIC` matches the retail current-server cinematic
   run/extents/draw sequence, current-net-map reset guard, preview fallback,
   and ownerdraw dispatcher route.
5. Locked the shared cinematic cleanup wiring: `_UI_Init` installs
   `UI_StopCinematic`, positive handles stop directly, and ownerdraw cleanup
   handles `UI_MAPCINEMATIC` and `UI_NETMAPCINEMATIC` by resetting their
   backing cinematic handles to `-1`.
6. Updated the ownerdraw parity index so the three selected IDs are now marked
   checked and the unchecked retail-routed set reflects the remaining work.

Verification:

- `python -m pytest tests/test_ui_menu_files.py -k "map_media_ownerdraws"`
  - Result: `1 passed, 74 deselected`.
- `python -m pytest tests/test_ui_menu_files.py`
  - Result: `75 passed`.

### Task A125: Close skill and map preview UI ownerdraw parity [COMPLETED]
Priority: High
Primary areas: `src/code/ui/ui_main.c`, `tests/test_ui_menu_files.py`
Parity estimate: **before 98% -> after 100%** for the focused `UI_SKILL`,
`UI_MAPPREVIEW`, and `UI_MAP_TIMETOBEAT` ownerdraw lane. Repo-wide parity
remains **98%** because unrelated compatibility and packaging surfaces are
unchanged.

Completed work:

1. Rechecked the retail `uix86.dll` HLIL/Ghidra evidence for `UI_DrawSkill` at
   `0x10005350`, `UI_DrawMapPreview` at `0x100053C0`,
   `UI_DrawMapTimeToBeat` at `0x100054A0`, and `UI_Skill_HandleKey` at
   `0x1000A390`.
2. Confirmed `UI_SKILL` clamps `g_spSkill` into the retail one-to-five range,
   paints the matching skill table entry, and wires the ownerdraw key handler
   to the retail click/enter cycle behavior.
3. Confirmed `UI_MAPPREVIEW` validates the selected map slot, resets the
   current map cvars on invalid indexes, lazily caches levelshot shaders, falls
   back to `menu/art/unknownmap`, and uses the net-map preview path from the
   ownerdraw dispatcher.
4. Confirmed `UI_MAP_TIMETOBEAT` validates `ui_currentMap`, resolves the
   retail gametype enum before indexing the per-map time table, formats the
   value as `%02i:%02i`, and paints it through the ownerdraw dispatcher.
5. Added regression coverage binding all three ownerdraws to the promoted
   retail evidence addresses, draw dispatch wiring, key dispatch wiring, and
   fallback/reset behavior.

Verification:

- `python -m pytest tests/test_ui_menu_files.py -k "skill_mappreview_maptime"`
  - Result: `1 passed, 73 deselected`.
- `python -m pytest tests/test_ui_menu_files.py`
  - Result: `74 passed`.

### Task A124: Close bot selector UI ownerdraw parity [COMPLETED]
Priority: High
Primary areas: `src/code/ui/ui_main.c`, `tests/test_ui_menu_files.py`
Parity estimate: **before 97% -> after 100%** for the focused `UI_BOTNAME`,
`UI_BOTSKILL`, and `UI_REDBLUE` ownerdraw lane. Repo-wide parity remains
**98%** because unrelated compatibility and packaging surfaces are unchanged.

Completed work:

1. Rechecked the retail `uix86.dll` HLIL/Ghidra evidence for
   `UI_DrawBotName` at `0x10006b30`, `UI_DrawBotSkill` at `0x10006bc0`,
   `UI_DrawRedBlue` at `0x10006c10`, and the bot-name/bot-skill key handlers
   at `0x1000a570` and `0x1000a5d0`.
2. Made the `UI_BOTNAME` draw path explicitly mirror the retail invalid-index
   behavior: clamp high indexes back to zero, print the retail invalid bot
   warning for remaining invalid indexes, and paint the `Sarge` fallback while
   keeping the add-bot selector bound to the bot catalog rather than the
   character roster.
3. Confirmed `UI_BOTSKILL` already matches the retail five-entry skill table
   paint path and wraparound key cycling.
4. Confirmed `UI_REDBLUE` already matches the retail `Red`/`Blue` paint path,
   toggle handler, and non-returning ownerdraw key dispatch.
5. Locked all three ownerdraw draw dispatches, key dispatches, key wrap paths,
   fallback behavior, and add-bot catalog wiring with focused regression
   coverage.

Verification:

- `python -m pytest tests/test_ui_menu_files.py -k "botname_botskill_redblue or addbot_uses_bot_catalog"`
  - Result: `2 passed, 71 deselected`.
- `python -m pytest tests/test_ui_menu_files.py`
  - Result: `73 passed`.

### Task A123: Close handicap and server-browser selector UI ownerdraw parity [COMPLETED]
Priority: High
Primary areas: `src/code/ui/ui_main.c`, `tests/test_ui_menu_files.py`
Parity estimate: **before 96% -> after 99%** for the focused
`UI_HANDICAP`, `UI_NETSOURCE`, and `UI_NETFILTER` ownerdraw lane. Repo-wide
parity remains **98%** because unrelated compatibility and packaging surfaces
are unchanged.

Completed work:

1. Rechecked the retail `uix86.dll` HLIL/Ghidra evidence for the handicap draw
   and key handler, plus the browser source/filter draw, width, and key
   handlers at `0x1000a040`, `0x1000a420`, and `0x1000a4f0`.
2. Confirmed `UI_HANDICAP` already matched the retail `5..100` clamp, label
   table indexing, five-point key steps, and wrap behavior, then locked that
   draw/width/key-dispatch path with focused tests.
3. Corrected `UI_NETSOURCE` draw and ownerdraw-width bounds to reject
   `index == numNetSources`, and replaced the stale width check against
   `uiInfo.numJoinGameTypes` with the retail browser-source count.
4. Corrected `UI_NETFILTER` draw and ownerdraw-width bounds to reject
   `index == numServerFilters`, matching the retail seven-filter table limit.
5. Locked the Mplayer-skip source cycling, global-refresh gate, server-list
   rebuilds, non-returning ownerdraw key dispatch, and filter wrap behavior
   with focused regression coverage.

Verification:

- `python -m pytest tests/test_ui_menu_files.py -q --tb=short`
  - Result: `72 passed`.

### Task A122: Close crosshair, next-map, and selected-player UI ownerdraw parity [COMPLETED]
Priority: High
Primary areas: `src/code/ui/ui_main.c`, `tests/test_ui_menu_files.py`
Parity estimate: **before 93% -> after 99%** for the focused
`UI_CROSSHAIR`, `UI_NEXTMAP`, and `UI_SELECTEDPLAYER` ownerdraw lane.
Repo-wide parity remains **98%** because unrelated compatibility and packaging
surfaces are unchanged.

Completed work:

1. Rechecked the retail `uix86.dll` HLIL/Ghidra evidence for the crosshair
   preview, next-map label, selected-player draw, player-list refresh, and
   selected-player key-handler paths.
2. Reconstructed `UI_CROSSHAIR` preview placement to use the retail
   `24..40` size clamp and fixed `rect->x - 2`, `rect->y - rect->h + 2`
   anchor instead of scaling/centering within the ownerdraw rect.
3. Reconstructed `UI_NEXTMAP` to paint only the retail configstring `0x29A`
   payload and removed the compatibility fallback through rotation-title
   configstrings from that ownerdraw.
4. Reconstructed `UI_SELECTEDPLAYER` drawing to use the retail buffered cvar
   read for either `cg_selectedPlayerName` or `name`, while preserving the
   player-list refresh and selected-player key cycling semantics.
5. Locked draw dispatch, key dispatch, cvar reads/writes, configstring reads,
   selected-player cache refresh, wrap behavior, and removed fallback paths
   with focused regression coverage.

Verification:

- `python -m pytest tests/test_ui_menu_files.py -q --tb=short`
  - Result: `71 passed`.

### Task A121: Close retail gametype-selector UI ownerdraw parity [COMPLETED]
Priority: High
Primary areas: `src/code/ui/ui_main.c`, `tests/test_ui_menu_files.py`
Parity estimate: **before 95% -> after 99%** for the focused
`UI_GAMETYPE`, `UI_NETGAMETYPE`, and `UI_JOINGAMETYPE` ownerdraw lane.
Repo-wide parity remains **98%** because unrelated compatibility and packaging
surfaces are unchanged.

Completed work:

1. Rechecked the retail `uix86.dll` HLIL/Ghidra evidence for the gametype
   ownerdraw dispatch cases and their key handlers at `0x1000a110`,
   `0x1000a210`, and `0x1000a300`.
2. Removed the old non-retail `ui_Q3Model` side effect from the
   `UI_GAMETYPE` key path while preserving retail cycling, cap/frag refresh,
   best-score reload, and map-feeder reset wiring.
3. Reconstructed the retail `UI_NETGAMETYPE` hidden-enum skip so the selector
   cycles past One Flag CTF, Overload, and Harvester before updating
   `ui_netGameType`, `ui_actualnetGameType`, `ui_currentNetMap`, and the map
   feeder.
4. Locked the `UI_GAMETYPE`, `UI_NETGAMETYPE`, and `UI_JOINGAMETYPE`
   draw-dispatch, key-dispatch, cvar, feeder, and server-list wiring with
   focused regression coverage.

Verification:

- `python -m pytest tests/test_ui_menu_files.py -q --tb=short`
  - Result: `70 passed`.

### Task A120: Close three retail UI ownerdraw parity seams [COMPLETED]
Priority: High
Primary areas: `src/code/ui/ui_main.c`, `tests/test_ui_menu_files.py`
Parity estimate: **before 94% -> after 99%** for the focused
`UI_VOTESTRING`, `UI_STARTING_WEAPONS`, and `UI_ADVERT` ownerdraw lane.
Repo-wide parity remains **98%** because the remaining non-ownerdraw
compatibility and packaging surfaces are unchanged.

Completed work:

1. Rechecked the retail `uix86.dll` HLIL/Ghidra ownerdraw dispatch evidence for
   `UI_VOTESTRING`, `UI_STARTING_WEAPONS`, and `UI_ADVERT`.
2. Reconstructed `UI_VOTESTRING` to use the retail buffered cvar read and
   integer x-anchor centering behavior instead of centering inside the rect
   width.
3. Reconstructed `UI_STARTING_WEAPONS` to parse the loadout mask through the
   retail decimal `atoi` path and to draw the loadout `+` marker at the retail
   x-offset before the queued-primary icon.
4. Locked the advert ownerdraw parse/setup/refresh/paint/activate bridge with
   focused regression coverage, including default content, cell id,
   hidden-menu refresh rectangles, shader assignment, draw/update ordering, and
   activation script forwarding.

Verification:

- `python -m pytest tests/test_ui_menu_files.py -q --tb=short`
  - Result: `69 passed`.

### Task A119: Reconstruct retail ownership for `ui_*` cvars [COMPLETED]
Priority: High
Primary areas: `src/code/ui/ui_main.c`, `src/code/ui/ui_local.h`,
`src/code/client/cl_ui.c`, `tests/test_ui_menu_files.py`,
`tests/test_cgame_hud_parity.py`, `tests/test_platform_services.py`,
`docs/reverse-engineering/ui-cvar-mapping-round-2026-05-28.md`
Parity estimate: **before 93% -> after 98%** for the focused `ui_*` cvar
callback and ownership lane. Repo-wide parity remains **98%** because the
source still carries bounded GPL-era and compatibility cvar rows outside the
retail `uix86.dll` table.

Completed work:

1. Rechecked `uix86.dll` Ghidra and HLIL evidence for the retail UI cvar table,
   including the `0x82` row count, row field order, `UI_RegisterCvars`,
   `UI_UpdateCvars`, and the callback owners at `sub_10011240`,
   `sub_10011630`, `sub_10011660`, and `sub_10011690`.
2. Reconstructed the source cvar table callback lane with a retail-shaped row
   order of `vmCvar`, cvar name, default string, update callback, and flags.
3. Replaced ad hoc color modification-count checks with the retail
   `UI_UpdateCvars` callback rule and added the missing bulk `ui_teamColor` and
   `ui_enemyColor` rows.
4. Routed retail slider-color, force-model, and `cg_announcer` rows through
   source-visible callbacks that mirror the committed HLIL behavior.
5. Corrected the native UI `S_RegisterSound` host shim so the retail
   announcer callback's non-zero `7` argument remains true after qboolean
   normalization.
6. Documented the full retail `0x82` row table, host-owned `ui_*` bridge cvars,
   and compatibility-only source cvars, then refreshed focused parity tests.

### Task A118: Reconstruct cached retail ownership for `web_*` cvars [COMPLETED]
Priority: High
Primary areas: `src/code/qcommon/common.c`,
`src/code/client/cl_cgame.c`, `tests/test_engine_cvar_retail_parity.py`,
`tests/test_engine_client_command_parity.py`,
`tests/test_awesomium_browser_parity.py`,
`tests/test_platform_services.py`,
`tools/ci/verify-awesomium-browser-host-parity.ps1`,
`docs/reverse-engineering/awesomium-browser-wiring.md`,
`docs/reverse-engineering/quakelive_steam_mapping_round_333.md`
Parity estimate: **before 96% -> after 99%** for the focused `web_*` cvar
ownership lane. Overall Awesomium WebUI wiring remains **99.1% -> 99.1%**;
repo-wide parity remains **98%**.

Completed work:

1. Rechecked the committed Ghidra and HLIL corpus for all retail `web_*` cvar
   names and confirmed the supported set is `web_zoom`, `web_console`, and
   `web_browserActive`; the other `web_*` names in this subsystem are command
   registrations.
2. Reconstructed the core cached `web_browserActive` cvar pointer in
   `common.c` and routed the frame idle-sleep browser-active test through that
   pointer instead of a repeated name lookup.
3. Reconstructed cached browser-host cvar pointers for `web_zoom`,
   `web_console`, and `web_browserActive`, added a source-visible mapping table
   with recovered retail globals/defaults/flags, and routed console-message and
   live zoom consumers through the cached cvars.
4. Matched the retail `web_zoom` modified-latch consumption path by clearing
   the cvar latch after the live Awesomium view consumes a zoom update.
5. Refreshed focused tests, verifier anchors, and mapping notes for the new
   cvar-owner evidence.

### Task A117: Stop no-op Awesomium bridge cvar churn and guard Awesomium launches [COMPLETED]
Priority: High
Primary areas: `src/code/client/cl_cgame.c`, `.vscode/build.ps1`,
`.vscode/launch.ps1`, `tests/test_awesomium_browser_parity.py`,
`tests/test_platform_services.py`,
`tools/ci/verify-awesomium-browser-host-parity.ps1`,
`docs/reverse-engineering/awesomium-browser-wiring.md`
Parity estimate: **before 99.0% -> after 99.1%** for the focused Awesomium
WebUI wiring lane. Repo-wide parity remains **98%** because default
online-service exclusion is policy-bounded.

Completed work:

1. Rechecked the Ghidra/HLIL evidence for `Cvar_Set2` and confirmed that the
   retail debug string is emitted before the unchanged-value return path, so
   the core cvar setter must not be softened to hide compatibility publisher
   spam.
2. Added a client-side `CL_SetCvarIfChanged()` guard and routed repeated
   browser/advert bridge telemetry plus frame-loop `web_browserActive` mirrors
   through it, while keeping retail-style open/hide cvar writes direct.
3. Added a build-settings stamp to the VS Code build wrapper and made
   `launch.ps1 -EnableAwesomium` refuse a launch when the last build used
   `QLBuildOnlineServices=0`, making accidental default-off WebUI tests fail
   early with a clear message.
4. Refreshed focused tests, verifier anchors, and the Awesomium wiring notes so
   the no-op cvar publish behavior and explicit Awesomium build path stay
   pinned.

### Task A116: Remove Awesomium SDK replication and require external SDK dependencies [COMPLETED]
Priority: High
Primary areas: `src/code/client/cl_awesomium_win32.cpp`,
`src/code/awesomium_process.vcxproj`,
`src/code/quakelive_steam.vcxproj`,
`src/code/win32/awesomium_process.cpp`,
`src/code/win32/awesomium_process.rc`,
`tests/test_awesomium_browser_parity.py`,
`tests/test_platform_services.py`,
`tools/ci/verify-awesomium-browser-host-parity.ps1`,
`tools/ci/verify-awesomium-process-parity.ps1`,
`docs/reverse-engineering/awesomium-browser-wiring.md`,
`docs/reverse-engineering/awesomium_process-mapping.md`,
`docs/reverse-engineering/quakelive_steam_mapping_round_332.md`
Parity estimate: **before 64% -> after 94%** for the focused
Awesomium SDK-clean integration lane. Overall Awesomium WebUI wiring remains
estimated at **99.0% -> 99.0%**; repo-wide parity remains **98%**.

Completed work:

1. Audited the Awesomium client/backend/helper build surface and found local
   SDK-like replication in the C++ ABI fallback layer, generated `.def` import
   library, local `ChildProcessMain` declaration, and vendor-owned helper
   metadata.
2. Removed local Awesomium object storage, `__thiscall` thunks, decorated C++
   import fallbacks, vtable-dispatch fallbacks, and raw `BitmapSurface` field
   offset reads from the live backend.
3. Corrected live SDK export usage for transparent-state setup and keyboard
   event injection, using the SDK-owned WebKeyboardEvent object path.
4. Deleted `src/code/win32/awesomium.def`, required external
   `AwesomiumSdkDir`/`AWESOMIUM_SDK_DIR` for online Awesomium builds, linked
   `awesomium.lib` from that SDK for the helper, and declared the external
   runtime dependency for the launcher.
5. Updated documentation, mapping notes, pytest coverage, and verifier guards
   so SDK replication does not re-enter silently.

Verification:

- `python -m pytest tests/test_awesomium_browser_parity.py tests/test_platform_services.py -q --tb=short`
  - Result: `103 passed`.
- `powershell -ExecutionPolicy Bypass -File tools\ci\verify-awesomium-browser-host-parity.ps1 -RepoRoot E:\Repositories\QuakeLive-reverse`
  - Result: all Awesomium browser host parity and SDK-clean dependency anchors present.
- `git diff --check -- ...`
  - Result: clean; only Git line-ending normalization warnings were reported.
- `powershell -ExecutionPolicy Bypass -File tools\ci\build-windows-dlls.ps1 -RepoRoot E:\Repositories\QuakeLive-reverse -Solution src/code/quakelive.sln -Configuration Debug -Platform Win32 -PlatformToolset v143 -DisableOptionalCodecs`
  - Result: build succeeded with `29` existing warnings and `0` errors.

### Task A115: Reconstruct Awesomium qz method table return flags [COMPLETED]
Priority: High
Primary areas: `src/code/client/cl_cgame.c`,
`src/code/client/cl_awesomium_win32.cpp`,
`tests/test_awesomium_browser_parity.py`,
`tests/test_platform_services.py`,
`tools/ci/verify-awesomium-browser-host-parity.ps1`,
`docs/reverse-engineering/awesomium-browser-wiring.md`,
`docs/reverse-engineering/quakelive_steam_mapping_round_331.md`
Parity estimate: **before 97% -> after 99.4%** for the focused
Awesomium qz method-table/return-flag lane. Overall Awesomium WebUI wiring is
estimated at **98.9% -> 99.0%**; repo-wide parity remains **98%**.

Completed work:

1. Rechecked `QLJSHandler_LookupMethodId`, `QLJSHandler_BindQzInstance`,
   `QLJSHandler_OnMethodCall`, and `QLJSHandler_OnMethodCallWithReturnValue`
   against HLIL with Ghidra function/vtable ownership support.
2. Added source-visible retail bounds and row addresses for the `data_55c008`
   qz method table.
3. Corrected `SetCvar` and `ResetCvar` to follow the retail return-valued
   method lane and return boolean success/failure values.
4. Updated the injected startup `qz_instance` bridge so local cvar set/reset
   helpers normalize cvar names and return truthy values.
5. Added parity coverage and CI verifier anchors for the qz method table,
   return flags, startup bridge behavior, and mapping-round evidence.

Verification:

- `python -m pytest tests/test_awesomium_browser_parity.py tests/test_platform_services.py -q --tb=short`
  - Result: `102 passed`.
- `powershell -ExecutionPolicy Bypass -File tools\ci\verify-awesomium-browser-host-parity.ps1 -RepoRoot E:\Repositories\QuakeLive-reverse`
  - Result: all Awesomium browser host parity anchors present.
- `git diff --check -- src/code/client/cl_awesomium_win32.cpp src/code/client/cl_cgame.c src/code/client/client.h tests/test_awesomium_browser_parity.py tests/test_platform_services.py tools/ci/verify-awesomium-browser-host-parity.ps1 docs/reverse-engineering/awesomium-browser-wiring.md docs/reverse-engineering/quakelive_steam_mapping_round_330.md docs/reverse-engineering/quakelive_steam_mapping_round_331.md IMPLEMENTATION_PLAN.md`
  - Result: clean; only Git line-ending normalization warnings were reported.
- `powershell -ExecutionPolicy Bypass -File tools\ci\build-windows-dlls.ps1 -RepoRoot E:\Repositories\QuakeLive-reverse -Solution src/code/quakelive.sln -Configuration Debug -Platform Win32 -PlatformToolset v143 -DisableOptionalCodecs`
  - Result: build succeeded with `0` warnings and `0` errors.

### Task A114: Reconstruct Awesomium WebSession lifecycle/cache wiring [COMPLETED]
Priority: High
Primary areas: `src/code/client/cl_awesomium_win32.cpp`,
`src/code/client/cl_cgame.c`, `src/code/client/client.h`,
`tests/test_awesomium_browser_parity.py`,
`tools/ci/verify-awesomium-browser-host-parity.ps1`,
`docs/reverse-engineering/awesomium-browser-wiring.md`,
`docs/reverse-engineering/quakelive_steam_mapping_round_330.md`
Parity estimate: **before 96% -> after 99%** for the focused
Awesomium WebSession lifecycle/cache lane. Overall Awesomium WebUI wiring is
estimated at **98.4% -> 98.9%**; repo-wide parity remains **98%**.

Completed work:

1. Rechecked `sub_4F2A10`, `sub_4F2A30`, `sub_4F2A60`,
   `sub_4F2D30`, `sub_4F3CB0`, and `sub_4F3CD0` against HLIL with
   Ghidra metadata and symbol-alias support.
2. Reconstructed WebSession slot `0x18` initialization immediately after
   `WebCore::CreateWebSession`.
3. Reclassified WebSession slot `0x1c` as cache clear for `web_clearCache`
   and reload, removed it from shutdown, and routed live clear-cache through
   `CL_Awesomium_ClearCache`.
4. Matched retail command-tail behavior for `web_showError` and made live
   navigation failures enter the mapped load-failure handler.
5. Updated Awesomium wiring notes, mapping-round evidence, pytest coverage,
   and the browser-host parity verifier.

Verification:

- `python -m pytest tests/test_awesomium_browser_parity.py tests/test_platform_services.py -q --tb=short`
  - Result: `101 passed`.
- `powershell -ExecutionPolicy Bypass -File tools\ci\verify-awesomium-browser-host-parity.ps1 -RepoRoot E:\Repositories\QuakeLive-reverse`
  - Result: all Awesomium browser host parity anchors present.
- `git diff --check -- src/code/client/cl_awesomium_win32.cpp src/code/client/cl_cgame.c src/code/client/client.h docs/reverse-engineering/awesomium-browser-wiring.md docs/reverse-engineering/quakelive_steam_mapping_round_330.md tests/test_awesomium_browser_parity.py tools/ci/verify-awesomium-browser-host-parity.ps1`
  - Result: clean; only Git line-ending normalization warnings were reported.
- `powershell -ExecutionPolicy Bypass -File tools\ci\build-windows-dlls.ps1 -RepoRoot E:\Repositories\QuakeLive-reverse -Solution src/code/quakelive.sln -Configuration Debug -Platform Win32 -PlatformToolset v143 -DisableOptionalCodecs`
  - Result: build succeeded; existing UI/game config warnings were reported.

### Task A113: Reconstruct application initialization host wiring [COMPLETED]
Priority: High
Primary areas: `src/code/win32/win_main.c`,
`references/analysis/quakelive_symbol_aliases.json`,
`tests/test_application_initialization_mapping.py`,
`docs/reverse-engineering/application-initialization-wiring-reconstruction-2026-05-27.md`
Parity estimate: **before 96.5% -> after 98.0%** for the scoped
application-initialization wiring lane. The repo-wide parity estimate remains
**98%**.

Completed work:

1. Rechecked `WinMain @ 0x004ED830`, `Com_Init @ 0x004CBFD0`,
   `Sys_Init @ 0x004ED400`, `NET_Init @ 0x004EF320`,
   `CL_Init @ 0x004BC690`, `SV_Init @ 0x004E3AD0`, and the adjacent ZMQ/browser
   startup handoffs against Binary Ninja HLIL with Ghidra metadata support.
2. Promoted `sub_4EC580` to `Sys_WinkeyHookProc` and reconstructed the
   WinMain-owned low-level keyboard hook that gates `VK_LWIN` / `VK_RWIN`
   behind `winkey_disable`.
3. Added shutdown unhook wiring to both `Sys_Error` and `Sys_Quit`, matching
   the retail unhook sites in the error and normal-exit paths.
4. Documented policy-aware startup divergences for Steam, ZMQ, and Awesomium
   so Quake Live-only online services remain behind the repository's disabled
   defaults.
5. Added static parity coverage for the retail owner map, host call order,
   hook predicate, shutdown unhook, and policy-adjusted common/client/server
   startup wiring.

Verification:

- `python -m pytest tests/test_application_initialization_mapping.py -q --tb=short`
  - Result: `3 passed`.
- `python -m pytest tests/test_renderer_win32_host_glue_parity.py tests/test_win32_raw_input_parity.py tests/test_engine_client_command_parity.py -q --tb=short`
  - Result: `46 passed`.
- `python -m pytest tests/test_platform_services.py::test_client_steam_callback_owner_reconstructs_retail_frame_pump_and_lifecycle tests/test_platform_services.py::test_client_browser_host_core_reconstructs_retained_runtime_owner tests/test_platform_services.py::test_server_zmq_runtime_reconstructs_retail_publication_and_rcon_owners -q --tb=short`
  - Result: `3 passed`.
- `python -m pytest tests/test_awesomium_browser_parity.py::test_awesomium_runtime_bootstrap_and_surface_pump_reconstruct_retail_host_contract tests/test_awesomium_browser_parity.py::test_awesomium_view_callbacks_reconstruct_tooltip_and_console_contracts -q --tb=short`
  - Result: `2 passed`.
- `MSBuild.exe src\code\quakelive_steam.vcxproj /p:Configuration=Debug /p:Platform=Win32 /m /v:minimal`
  - Result: succeeded; existing `cl_cgame.c` unused-local warnings were reported.
- `git diff --check`
  - Result: clean; only Git line-ending normalization warnings were reported.

### Task A112: Retire generated UI bridge menu assets [COMPLETED]
Priority: High
Primary areas: `src/code/ui/ui_main.c`, `src/code/ui/ui_atoms.c`,
`src/code/ui/ui_cdkey.c`, `src/code/ui/ui_local.h`,
`src/code/ui/ui.vcxproj`, `src/code/ui/Conscript`,
`tests/test_ui_menu_files.py`, `tests/test_platform_services.py`,
`docs/ui/scripting-guide.md`
Parity estimate: **before 99.90% -> after 99.96%** for the scoped
retail UI menu-root purity lane. The strict-retail Windows module target
remains **100%** and the repo-wide parity estimate remains **98%**.

Completed work:

1. Rechecked retail `uix86.dll` evidence: HLIL/Ghidra both show the default
   menu root opening `ui/menus.txt`, and the checked-in `src/ui/menus.txt`
   loads retail `ui/main.menu`.
2. Removed the generated `ql_bridge_*` menu-script owner and its build entries
   so offline browser-service handling no longer writes replacement menu
   assets into the homepath.
3. Kept disabled browser verbs policy-compliant by swallowing unavailable
   `web_showBrowser` / `web_changeHash` paths while the existing retail menu
   tree remains active.
4. Reframed the native CD-key command as an explicit unavailable-command stub
   in native UI builds instead of preferring generated credentials menus.
5. Updated parity tests, platform-service tests, docs, and CI font/build
   references to assert that retail menu files are used directly.

Verification:

- `python -m pytest tests/test_ui_menu_files.py tests/test_platform_services.py tests/test_non_windows_portability.py tests/test_ui_full_parity_gate.py -q --tb=short`
  - Result: `165 passed, 1 skipped`.

### Task A111: Reconstruct spectator client-state resync wiring [COMPLETED]
Priority: High
Primary areas: `src/code/game/bg_public.h`, `src/code/game/g_cmds.c`,
`src/code/game/g_client.c`, `src/code/game/g_active.c`,
`src/code/cgame/cg_playerstate.c`, `src/code/cgame/cg_local.h`,
`tests/test_spectator_client_state_wiring_parity.py`,
`docs/reverse-engineering/spectator-client-state-wiring-reconstruction-2026-05-27.md`,
`docs/reverse-engineering/qagame-mapping.md`,
`docs/reverse-engineering/cgame-mapping.md`,
`references/symbol-maps/qagame.json`, `references/symbol-maps/cgame.json`
Parity estimate: **before 99.90% -> after 99.97%** for the scoped
spectator client-state and item-state resync lane. The repo-wide parity
estimate remains **98%**.

Completed work:

1. Rechecked qagame `G_ApplyTeamChange @ 0x10040440` and
   `ClientSpawn @ 0x1003BC30` against Binary Ninja HLIL/Ghidra for the retail
   `0x4000` spectator client-state eFlag writes.
2. Added `EF_SPECTATOR_RESPAWN` as the Quake Live alias for that network bit,
   intentionally sharing the GPL `EF_VOTED` value because retail uses the same
   bit as the cgame `specresp` cue.
3. Reconstructed qagame set/clear wiring in `G_ApplyTeamChange` and
   `ClientSpawn`, and preserved the observer bit when `SpectatorClientEndFrame`
   copies followed-player snapshots.
4. Replaced the raw cgame `0x00004000` `CG_Respawn` check with
   `EF_SPECTATOR_RESPAWN`, keeping the retail `specresp` command handoff.
5. Mapped the surrounding spectator item-state responder: `specresp` and
   spectator team entry call `G_SyncSpectatorItemStatesForClient`, while item
   pickup broadcast still packs `EV_ITEM_PICKUP_SPEC` for the cgame cache.
6. Added cross-binary static coverage plus qagame/cgame mapping and symbol-map
   notes for the eFlag, command, event payload, cache decoder, and overlay
   update/draw path.

Verification:

- `python -m pytest tests/test_spectator_client_state_wiring_parity.py -q --tb=short`
  - Result: `8 passed`.
- `python -m pytest tests/test_spectator_client_state_wiring_parity.py tests/test_game_spectator_connection_parity.py tests/test_game_active_pmove_wiring_parity.py tests/test_game_helper_seam_parity.py tests/test_cgame_spectator_parity.py tests/test_cgame_snapshot_parity.py tests/test_cgame_event_transport_parity.py tests/test_cgame_hud_parity.py::test_spectator_item_timer_text_uses_retail_default_font_lane tests/test_game_vote_clear_parity.py -q --tb=short`
  - Result: `111 passed, 1 skipped`.
- `git diff --check`
  - Result: clean; only Git line-ending normalization warnings were reported.
- Broader context: the full `tests/test_cgame_hud_parity.py` file still has
  an unrelated `test_team_info_overlay_restores_fixed_retail_row_renderer`
  assertion failure outside this spectator client-state lane.

### Task A110: Reconstruct StepSlideMove down-clip and wiring map [COMPLETED]
Priority: High
Primary areas: `src/code/game/bg_slidemove.c`, `src/code/game/bg_pmove.c`,
`src/code/game/g_pmove.c`, `src/code/cgame/cg_servercmds.c`,
`src/code/cgame/cg_predict.c`, `tests/pmove_validation_harness.c`,
`tests/test_pmove_validation_fixtures.py`,
`tests/test_step_jump_gate_parity.py`,
`docs/reverse-engineering/pmove-stepslidemove-wiring-reconstruction-2026-05-27.md`
Parity estimate: **before 98.8% -> after 99.9%** for the scoped
StepSlideMove lane. The repo-wide parity estimate remains **98%**.

Completed work:

1. Rechecked qagame `PM_StepSlideMove @ 0x1002EFE0` and cgame
   `PM_StepSlideMove @ 0x100034B0` against Binary Ninja HLIL, with Ghidra
   companion confirmation for the matching helper call graph.
2. Tightened the down-trace clip guard to the retail dot-product epsilon:
   `DotProduct(velocity, plane.normal) < 0.0f || fabs(dot) < 0.001f`.
3. Preserved the retail direct reachability trace before recording step side
   effects, plus the `startsolid` rejection on the projected step-jump support
   probe.
4. Documented the full movement call matrix, step-jump latch split, and cgame
   prediction smoothing handoff.
5. Added executable and structural parity coverage for the down-clip guard,
   call-site wiring, normal/crouch takeoff latches, and `pmove_t::stepUp`
   prediction export.
6. Pinned the `pmove_AirStepFriction`, `pmove_AirSteps`, and
   `pmove_StepHeight` server-to-cgame tuning transport that feeds the private
   step-move globals.

Verification:

- `python -m pytest tests/test_step_jump_gate_parity.py tests/test_pmove_validation_fixtures.py -q --tb=short`
  - Result: `22 passed`.
- `python -m pytest tests/test_step_jump_gate_parity.py tests/test_pmove_helper_parity.py tests/test_pmove_validation_fixtures.py tests/test_pmove_movement_fixtures.py tests/test_pmove_selected_cvar_parity.py tools/tests/test_pmove_settings_configstring.py -q --tb=short`
  - Result: `134 passed, 107 subtests passed`.
- `git diff --check`
  - Result: clean; only Git line-ending normalization warnings were reported.

### Task A109: Reconstruct CA/A-D spectator respawn handoff [COMPLETED]
Priority: High
Primary areas: `src/code/game/g_team.c`, `src/code/game/g_client.c`,
`tests/test_game_attack_defend_parity.py`,
`tests/test_game_spectator_connection_parity.py`,
`tests/test_game_active_pmove_wiring_parity.py`,
`docs/reverse-engineering/qagame-spectator-state-movement-reconstruction-2026-05-26.md`,
`docs/reverse-engineering/qagame-client-spawn-reconstruction-2026-05-26.md`,
`docs/reverse-engineering/qagame-mapping.md`,
`references/symbol-maps/qagame.json`
Parity estimate: **before 99.8% -> after 99.9%** for the scoped qagame
spectator state/movement lane. The repo-wide parity estimate remains **98%**.

Completed work:

1. Rechecked `G_CAADRespawnAsSpectator @ 0x10035960` and the dependent
   `ClientSpawn @ 0x1003BC30` spectator branch against Binary Ninja HLIL.
2. Collapsed the CA/A-D eliminated-player spectator helper back to the retail
   sequence: `CopyToBodyQue`, pre-seed `PM_SPECTATOR`, `ClientSpawn`, active
   team counts, and `FollowCycle` only when both teams still have players.
3. Removed the source-only direct follow-target picker, post-spawn relink, and
   free/scoreboard fallback assignment from that helper.
4. Taught `ClientSpawn` to preserve a pre-existing `PM_SPECTATOR` state as the
   spectator-spawn selector, so active-team CA/A-D eliminations can reuse the
   retail spectator placement path without pretending the session team changed.
5. Updated attack/defend, spectator, and active-pmove static parity coverage,
   plus the qagame mapping, client-spawn note, spectator note, and symbol map.

Verification:

- `python -m pytest tests/test_game_attack_defend_parity.py tests/test_game_spectator_connection_parity.py -q --tb=short`
  - Result: `10 passed`.
- `python -m pytest tests/test_game_active_pmove_wiring_parity.py::test_first_18_g_cvars_match_retail_defaults_flags_and_wiring tests/test_game_active_pmove_wiring_parity.py::test_spectator_impacts_and_predictable_event_sidecars_match_retail_wiring -q --tb=short`
  - Result: `2 passed`.
- `python -m pytest tests/test_game_attack_defend_parity.py tests/test_game_spectator_connection_parity.py tests/test_game_active_pmove_wiring_parity.py tests/test_game_helper_seam_parity.py tests/test_pmove_helper_parity.py tests/test_game_factory_regen_parity.py tests/test_bg_misc_validation_fixtures.py tests/test_spawn_spec_cvars.py tests/test_cgame_spectator_parity.py -q --tb=short`
  - Result: `164 passed`.
- `git diff --check`
  - Result: clean; only Git line-ending normalization warnings were reported.

### Task A108: Reconstruct initial and team-begin spawn fallback modes [COMPLETED]
Priority: High
Primary areas: `src/code/game/g_client.c`, `src/code/game/g_team.c`,
`tests/test_game_active_pmove_wiring_parity.py`,
`tests/test_game_helper_seam_parity.py`,
`docs/reverse-engineering/qagame-client-spawn-reconstruction-2026-05-26.md`,
`docs/reverse-engineering/qagame-mapping.md`,
`references/hlil/quakelive/qagamex86.dll/qagamex86.dll.bndb_hlil.txt`,
`references/reverse-engineering/ghidra/qagamex86/decompile_top_functions.c`
Parity estimate: **before 98.8% -> after 99.0%** for the scoped qagame
client-spawn band. The repo-wide parity estimate remains **98%**.

Completed work:

1. Rechecked `G_SelectRankedSpawnPoint @ 0x10039080` and
   `G_SelectClientSpawnPoint @ 0x10039730` against Binary Ninja HLIL and the
   committed Ghidra companion body.
2. Reconstructed the neutral initial-spawn admission mode: ranked neutral
   initial selection now requires spawnflags bit 1 while still excluding bit 2.
3. Added a ranked initial-spawn wrapper so `SelectInitialSpawnPoint` ranks all
   eligible initial `info_player_deathmatch` starts instead of taking the first
   matching entity from `G_Find`.
4. Restored the team `TEAM_BEGIN` fallback retry from `team_CTF_*player` to
   the same team's `team_CTF_*spawn` class before neutral deathmatch fallback.
5. Updated helper/active parity coverage and the qagame client-spawn mapping
   notes, leaving the training-map-specific ranked-spawn path as the next
   explicit follow-up.

Verification:

- `python -m pytest tests/test_game_helper_seam_parity.py tests/test_game_active_pmove_wiring_parity.py -q --tb=short`
  - Result: `63 passed`.
- `python -m pytest tests/test_game_spectator_connection_parity.py tests/test_game_active_pmove_wiring_parity.py tests/test_game_helper_seam_parity.py tests/test_pmove_helper_parity.py tests/test_game_factory_regen_parity.py tests/test_bg_misc_validation_fixtures.py tests/test_spawn_spec_cvars.py tests/test_cgame_spectator_parity.py -q --tb=short`
  - Result: `161 passed`.
- `git diff --check -- src/code/game/g_client.c src/code/game/g_team.c tests/test_game_helper_seam_parity.py tests/test_game_active_pmove_wiring_parity.py docs/reverse-engineering/qagame-client-spawn-reconstruction-2026-05-26.md docs/reverse-engineering/qagame-mapping.md`
  - Result: pass; only repository LF-to-CRLF conversion warnings.

### Task A107: Correct spectator follow command surface [COMPLETED]
Priority: High
Primary areas: `src/code/game/g_cmds.c`,
`tests/test_game_spectator_connection_parity.py`,
`docs/reverse-engineering/qagame-spectator-state-movement-reconstruction-2026-05-26.md`,
`docs/reverse-engineering/qagame-spectator-follow-reconstruction-2026-05-22.md`,
`docs/reverse-engineering/qagame-mapping.md`,
`references/symbol-maps/qagame.json`
Parity estimate: **before 99.5% -> after 99.8%** for the scoped qagame
spectator command surface. The repo-wide parity estimate remains **98%**.

Completed work:

1. Rechecked `Cmd_Follow_f @ 0x10040F30` and `Cmd_FollowCycle_f @
   0x100412E0` against the committed Binary Ninja HLIL after the broader
   spectator-state pass.
2. Corrected `Cmd_Follow_f` so `follow1` and `follow2` remain owned by
   `SetTeam`, while the `follow` command resolves player strings through
   `ClientNumberFromString`.
3. Restored the retail cgame `"pw"` suffix guard that preserves the current
   followed flag carrier via `BG_PlayerCarryingFlag`, and changed explicit
   target rejection to the retail `ps.pm_type == PM_SPECTATOR` check.
4. Removed source-only training-map print gates from `Cmd_Follow_f` and
   `Cmd_FollowCycle_f`; no-arg follow cleanup remains handled by the retail
   follow/end-frame paths.
5. Rebuilt the public follow-cycle entry around the retail `sess.sessionTeam`
   spectator handoff before tailcalling the inner `FollowCycle` worker.
6. Updated static parity coverage, the spectator reconstruction notes, the
   qagame mapping ledger, and the qagame symbol-map comments.

Verification:

- `python -m pytest tests/test_game_spectator_connection_parity.py tests/test_spawn_spec_cvars.py tests/test_cgame_spectator_parity.py -q --tb=short`
  - Result: `18 passed`.
- `python -m pytest tests/test_game_active_pmove_wiring_parity.py::test_spectator_impacts_and_predictable_event_sidecars_match_retail_wiring tests/test_pmove_helper_parity.py -q --tb=short`
  - Result: `41 passed`.
- `python -m pytest tests/test_game_helper_seam_parity.py::test_last_alive_alert_helpers_match_recovered_retail_boundaries -q --tb=short`
  - Result: `1 passed`.
- Wider adjacent suite note:
  `python -m pytest tests/test_game_spectator_connection_parity.py tests/test_game_active_pmove_wiring_parity.py tests/test_game_helper_seam_parity.py tests/test_pmove_helper_parity.py tests/test_game_factory_regen_parity.py tests/test_bg_misc_validation_fixtures.py tests/test_spawn_spec_cvars.py tests/test_cgame_spectator_parity.py -q --tb=short`
  currently reports `159 passed, 2 failed`; both failures are in unrelated
  ranked-spawn assertions in `tests/test_game_active_pmove_wiring_parity.py`
  and `tests/test_game_helper_seam_parity.py`.
- `git diff --check`
  - Result: pass; only repository LF-to-CRLF conversion warnings.

### Task A106: Reconstruct ranked-spawn spawnflag exclusion [COMPLETED]
Priority: High
Primary areas: `src/code/game/g_client.c`,
`tests/test_game_active_pmove_wiring_parity.py`,
`tests/test_game_helper_seam_parity.py`,
`docs/reverse-engineering/qagame-client-spawn-reconstruction-2026-05-26.md`,
`docs/reverse-engineering/qagame-mapping.md`,
`references/hlil/quakelive/qagamex86.dll/qagamex86.dll.bndb_hlil.txt`,
`references/reverse-engineering/ghidra/qagamex86/decompile_top_functions.c`
Parity estimate: **before 98.7% -> after 98.8%** for the scoped qagame
client-spawn band. The repo-wide parity estimate remains **98%**.

Completed work:

1. Rechecked `G_SelectRankedSpawnPoint @ 0x10039080` against Binary Ninja
   HLIL and the committed Ghidra companion body.
2. Identified the retail candidate admission guard that reads spawnflags at
   `entity + 0x248` and rejects candidates with bit 2 set before distance
   scoring.
3. Added `RANKED_SPAWN_EXCLUDE_FLAG` and `G_RankedSpawnPointAllowed`, then
   routed both the ranked-scoring path and the no-ranked-candidate fallback
   through the recovered filter.
4. Pinned the helper, constant, and ranked-picker call sites in the qagame
   helper and active pmove/spawn parity tests.
5. Updated the client-spawn reconstruction note and qagame mapping ledger with
   the HLIL/Ghidra evidence and the remaining bit-1 fallback question.

Verification:

- `python -m pytest tests/test_game_helper_seam_parity.py tests/test_game_active_pmove_wiring_parity.py -q --tb=short`
  - Result: `63 passed`.
- `git diff --check -- src/code/game/g_client.c src/code/game/g_local.h tests/test_game_helper_seam_parity.py tests/test_game_active_pmove_wiring_parity.py docs/reverse-engineering/qagame-client-spawn-reconstruction-2026-05-26.md docs/reverse-engineering/qagame-mapping.md IMPLEMENTATION_PLAN.md`
  - Result: pass; only repository LF-to-CRLF conversion warnings.

### Task A105: Split renderer framebuffer and shader procedure gates [COMPLETED]
Priority: High
Primary areas: `src/code/renderer/tr_backend.c`,
`tests/test_renderer_internal_helper_mapping_parity.py`,
`docs/reverse-engineering/quakelive_steam_mapping_round_328.md`,
`docs/reverse-engineering/renderer-full-parity-audit-and-implementation-plan-2026-04-09.md`,
`docs/reverse-engineering/source-file-parity-ledger-2026-04-22.md`,
`references/hlil/quakelive/quakelive_steam.exe/quakelive_steam.exe_hlil_split/`
Parity estimate: **before 99.985% -> after 99.99%** for the scoped
post-process proc gate lane. The strict renderer estimate remains **100%** and
the repo-wide parity estimate remains **98%**.

Completed work:

1. Rechecked retail `sub_4500B0` and `sub_450640` against HLIL to separate
   framebuffer target prerequisites from post-effect shader/program
   prerequisites.
2. Added `RBPP_LoadFramebufferProcs` for the retail framebuffer-only target
   lane: FBO/renderbuffer/rectangle entry points plus max rectangle texture
   size.
3. Added independent framebuffer procedure loaded/supported state to
   `ppState_t`.
4. Rewired `RBPP_CreateRenderTarget` to call the framebuffer-only loader,
   while `RBPP_LoadProgram` remains behind the full shader/uniform
   `RBPP_LoadProcs` gate.
5. Updated the renderer mapping, audit, and source-file ledger; `tr_backend.c`
   now tracks `79` functions.

Verification:

- `python -m pytest tests/test_renderer_post_process_parity.py tests/test_renderer_internal_helper_mapping_parity.py tests/test_renderer_export_tail_parity.py tests/test_renderer_full_parity_gate.py -q --tb=short`
  - Result: `46 passed, 1 skipped`.
- `python -m pytest tests/test_engine_cvar_retail_parity.py::test_engine_cvar_fortysecond_renderer_postprocess_state_tranche_matches_retail_contracts tests/test_engine_cvar_retail_parity.py::test_engine_cvar_twentyninth_renderer_postprocess_extension_tranche_matches_retail_contracts tests/test_engine_cvar_retail_parity.py::test_engine_cvar_thirtysecond_renderer_bloom_picmip_tranche_matches_retail_contracts -q --tb=short`
  - Result: `3 passed`.
- `python -m pytest tests/test_engine_client_command_parity.py::test_postprocess_restart_routes_through_renderer_export_not_renderer_cmd_registration -q --tb=short`
  - Result: `1 passed`.
- `git diff --check`
  - Result: pass; only repository LF-to-CRLF conversion warnings.

### Task A104: Reconstruct renderer post-process GL error and link wiring [COMPLETED]
Priority: High
Primary areas: `src/code/renderer/tr_backend.c`,
`src/code/renderer/tr_init.c`, `src/code/renderer/tr_local.h`,
`tests/test_renderer_internal_helper_mapping_parity.py`,
`tests/test_renderer_post_process_parity.py`,
`docs/reverse-engineering/quakelive_steam_mapping_round_327.md`,
`docs/reverse-engineering/renderer-full-parity-audit-and-implementation-plan-2026-04-09.md`,
`docs/reverse-engineering/source-file-parity-ledger-2026-04-22.md`,
`references/analysis/quakelive_symbol_aliases.json`,
`references/hlil/quakelive/quakelive_steam.exe/quakelive_steam.exe_hlil_split/`,
`references/reverse-engineering/ghidra/quakelive_steam/functions.csv`
Parity estimate: **before 99.97% -> after 99.985%** for the scoped
post-process GL error and link lane. The strict renderer estimate remains
**100%** and the repo-wide parity estimate remains **98%**.

Completed work:

1. Rechecked retail `sub_447E40`, `sub_4500B0`, `sub_4505F0`, and
   `sub_450640` against HLIL and the committed Ghidra function inventory.
2. Restored `GL_CheckErrors` as a return-valued helper so post-process callers
   can branch on unignored GL errors while existing callers may ignore the
   result.
3. Rewired `RBPP_CreateRenderTarget` to use `GL_CheckErrors()` after rectangle
   texture allocation and after framebuffer completeness, and removed the
   source-only renderbuffer bind from the attachment path.
4. Promoted `sub_4505F0` as `RBPP_LinkProgram`, moving post-effect program
   create/attach/link and GL-error-gated success into its own retail-shaped
   helper.
5. Dropped the source-only `GL_OBJECT_LINK_STATUS_ARB` link-status query from
   `RBPP_LoadProgram` and routed color-correct texture allocation through
   `GL_CheckErrors()`.

Verification:

- `python -m pytest tests/test_renderer_post_process_parity.py tests/test_renderer_internal_helper_mapping_parity.py tests/test_renderer_export_tail_parity.py tests/test_renderer_full_parity_gate.py -q --tb=short`
  - Result: `45 passed, 1 skipped`.
- `python -m pytest tests/test_engine_cvar_retail_parity.py::test_engine_cvar_fortysecond_renderer_postprocess_state_tranche_matches_retail_contracts tests/test_engine_cvar_retail_parity.py::test_engine_cvar_twentyninth_renderer_postprocess_extension_tranche_matches_retail_contracts tests/test_engine_cvar_retail_parity.py::test_engine_cvar_thirtysecond_renderer_bloom_picmip_tranche_matches_retail_contracts -q --tb=short`
  - Result: `3 passed`.
- `python -m pytest tests/test_engine_client_command_parity.py::test_postprocess_restart_routes_through_renderer_export_not_renderer_cmd_registration -q --tb=short`
  - Result: `1 passed`.
- `git diff --check`
  - Result: pass; only repository LF-to-CRLF conversion warnings.

### Task A103: Tighten spectator follow state and POI divergence [COMPLETED]
Priority: High
Primary areas: `src/code/game/g_active.c`, `src/code/game/g_cmds.c`,
`src/code/game/g_local.h`, `references/symbol-maps/qagame.json`,
`docs/reverse-engineering/qagame-mapping.md`,
`docs/reverse-engineering/qagame-spectator-state-movement-reconstruction-2026-05-26.md`,
`tests/test_game_spectator_connection_parity.py`,
`tests/test_game_active_pmove_wiring_parity.py`,
`tests/test_game_helper_seam_parity.py`
Parity estimate: **before 96% -> after 99.5%** for scoped qagame spectator
follow-state and end-frame parity; repo-wide remains **98%** pending the
active portability/runtime-evidence gaps.

Completed work:

1. Rechecked `SpectatorClientEndFrame @ 0x10035470`,
   `StopFollowing @ 0x10040D10`, `Cmd_Follow_f @ 0x10040F30`, and
   `FollowCycle @ 0x10041130` against the committed Binary Ninja HLIL.
2. Removed the source-only POI spectator camera storage and direct admin
   commands; retail follow cycling is client-only.
3. Rebuilt `StopFollowing` around the retail `SPECTATOR_FREE` reset with
   `PM_SPECTATOR`, `PMF_FOLLOW` clearing, self `spectatorClient/clientNum`,
   and linked-entity unlinking.
4. Routed `SpectatorThink` and stale end-frame targets through the recovered
   inner `FollowCycle` worker, including active-team fallback cycling when both
   teams still have live players.
5. Tightened `FollowCycle` filters for disconnected, `PM_SPECTATOR`,
   `PMF_FOLLOW`, and cross-team targets.

Verification:

- `python -m pytest tests/test_game_spectator_connection_parity.py tests/test_game_active_pmove_wiring_parity.py tests/test_game_helper_seam_parity.py tests/test_pmove_helper_parity.py tests/test_game_factory_regen_parity.py tests/test_bg_misc_validation_fixtures.py -q --tb=short`
  - Result: `149 passed`.
- `python -m pytest tests/test_spawn_spec_cvars.py tests/test_cgame_spectator_parity.py -q --tb=short`
  - Result: `11 passed`.
- `git diff --check`
  - Result: pass; only repository LF-to-CRLF conversion warnings.

### Task A102: Reconstruct renderer post-process renderbuffer cache [COMPLETED]
Priority: High
Primary areas: `src/code/renderer/tr_backend.c`,
`tests/test_renderer_internal_helper_mapping_parity.py`,
`docs/reverse-engineering/quakelive_steam_mapping_round_326.md`,
`docs/reverse-engineering/renderer-full-parity-audit-and-implementation-plan-2026-04-09.md`,
`docs/reverse-engineering/source-file-parity-ledger-2026-04-22.md`,
`references/analysis/quakelive_symbol_aliases.json`,
`references/hlil/quakelive/quakelive_steam.exe/quakelive_steam.exe_hlil_split/`,
`references/reverse-engineering/ghidra/quakelive_steam/functions.csv`
Parity estimate: **before 99.95% -> after 99.97%** for the scoped
post-process depth-stencil renderbuffer cache lane. The strict renderer
estimate remains **100%** and the repo-wide parity estimate remains **98%**.

Completed work:

1. Rechecked retail `sub_44FFD0`, `sub_4500B0`, `sub_450710`, and
   `sub_450780` against HLIL and the committed Ghidra function inventory.
2. Promoted `sub_44FFD0` as `RBPP_CreateDepthStencilRenderbuffer` and added
   the retail eight-entry width/height renderbuffer cache to `ppState_t`.
3. Routed `RBPP_CreateRenderTarget` through the cached
   `GL_DEPTH24_STENCIL8_EXT` renderbuffer helper before rectangle-texture and
   framebuffer creation.
4. Reset the reconstructed renderbuffer cache metadata during bloom resource
   shutdown, matching the retail rebuild/shutdown cache reset lane.
5. Updated the renderer mapping, audit, source-file ledger, and symbol alias
   evidence; `tr_backend.c` now tracks `77` functions.

Verification:

- `python -m pytest tests/test_renderer_post_process_parity.py tests/test_renderer_internal_helper_mapping_parity.py tests/test_renderer_export_tail_parity.py tests/test_renderer_full_parity_gate.py -q --tb=short`
  - Result: `44 passed, 1 skipped`.
- `python -m pytest tests/test_engine_cvar_retail_parity.py::test_engine_cvar_fortysecond_renderer_postprocess_state_tranche_matches_retail_contracts tests/test_engine_cvar_retail_parity.py::test_engine_cvar_twentyninth_renderer_postprocess_extension_tranche_matches_retail_contracts tests/test_engine_cvar_retail_parity.py::test_engine_cvar_thirtysecond_renderer_bloom_picmip_tranche_matches_retail_contracts -q --tb=short`
  - Result: `3 passed`.
- `python -m pytest tests/test_engine_client_command_parity.py::test_postprocess_restart_routes_through_renderer_export_not_renderer_cmd_registration -q --tb=short`
  - Result: `1 passed`.
- `git diff --check`
  - Result: pass; only repository LF-to-CRLF conversion warnings.

### Task A101: Correct ranked spawn candidate window [COMPLETED]
Priority: High
Primary areas: `src/code/game/g_client.c`,
`tests/test_game_active_pmove_wiring_parity.py`,
`tests/test_game_helper_seam_parity.py`,
`docs/reverse-engineering/qagame-client-spawn-reconstruction-2026-05-26.md`,
`docs/reverse-engineering/qagame-mapping.md`
Parity estimate: **before 98.5% -> after 98.7%** for the scoped qagame
client-spawn band. The repo-wide parity estimate remains **98%**.

Completed work:

1. Rechecked `G_SelectRankedSpawnPoint @ 0x10039080` against HLIL and the
   Ghidra companion body.
2. Restored the retail `0x1a` retained ranked-spawn candidate cap by changing
   `MAX_RANKED_SPAWN_POINTS` from 32 to 26.
3. Pinned the cap in the active pmove/spawn wiring and helper seam parity
   tests.
4. Updated the qagame client-spawn reconstruction note and mapping ledger with
   the ranked-picker evidence.

Verification:

- `python -m pytest tests/test_game_helper_seam_parity.py tests/test_game_active_pmove_wiring_parity.py -q --tb=short`
  - Result: `1 failed, 62 passed`; failure is an unrelated pre-existing
    `g_cmds.c` spectator free-cam expectation in
    `test_team_loadout_bot_and_drop_cvars_keep_retail_behavioral_wiring`.
- `python -m pytest tests/test_game_helper_seam_parity.py::test_client_spawn_uses_recovered_loadout_and_rr_helpers tests/test_game_active_pmove_wiring_parity.py::test_first_18_g_cvars_match_retail_defaults_flags_and_wiring -q --tb=short`
  - Result: `2 passed`.

### Task A100: Reconstruct renderer bloom teardown and program cleanup ordering [COMPLETED]
Priority: High
Primary areas: `src/code/renderer/tr_backend.c`,
`tests/test_renderer_post_process_parity.py`,
`tests/test_renderer_internal_helper_mapping_parity.py`,
`docs/reverse-engineering/quakelive_steam_mapping_round_325.md`,
`docs/reverse-engineering/renderer-full-parity-audit-and-implementation-plan-2026-04-09.md`,
`docs/reverse-engineering/source-file-parity-ledger-2026-04-22.md`,
`references/hlil/quakelive/quakelive_steam.exe/quakelive_steam.exe_hlil_split/`,
`src2/ghidra/quakelive_steam/quakelive_steam_decomp.cpp`
Parity estimate: **before 99.93% -> after 99.95%** for the scoped
post-process bloom teardown lane. The strict renderer estimate remains
**100%** and the repo-wide parity estimate remains **98%**.

Completed work:

1. Rechecked retail `sub_437DA0` and `sub_4506A0` against HLIL and the Ghidra
   companion corpus.
2. Updated `RBPP_DestroyBloomPrograms` to destroy bloom programs in retail
   memory order: brightpass, downsample, blurvertical, blurhoriz, combine.
3. Rebuilt `RBPP_ShutdownBloomResources` around the retail grouped delete
   order: all textures, then all framebuffers, then all depth-stencil
   renderbuffers, followed by target slot clearing.
4. Added the retail `glDetachObjectARB` path to `RBPP_DestroyProgram` so
   shader objects detach before program deletion.
5. Kept `tr_backend.c` at `76` tracked functions while tightening lifecycle
   parity in place.

Verification:

- `python -m pytest tests/test_renderer_post_process_parity.py tests/test_renderer_internal_helper_mapping_parity.py tests/test_renderer_export_tail_parity.py tests/test_renderer_full_parity_gate.py -q --tb=short`
  - Result: `43 passed, 1 skipped`.
- `python -m pytest tests/test_engine_cvar_retail_parity.py::test_engine_cvar_fortysecond_renderer_postprocess_state_tranche_matches_retail_contracts tests/test_engine_cvar_retail_parity.py::test_engine_cvar_twentyninth_renderer_postprocess_extension_tranche_matches_retail_contracts tests/test_engine_cvar_retail_parity.py::test_engine_cvar_thirtysecond_renderer_bloom_picmip_tranche_matches_retail_contracts -q --tb=short`
  - Result: `3 passed`.
- `python -m pytest tests/test_engine_client_command_parity.py::test_postprocess_restart_routes_through_renderer_export_not_renderer_cmd_registration -q --tb=short`
  - Result: `1 passed`.
- `git diff --check`
  - Result: pass; only repository LF-to-CRLF conversion warnings.

### Task A99: Restore client-spawn team gametype selection band [COMPLETED]
Priority: High
Primary areas: `src/code/game/g_client.c`,
`tests/test_game_helper_seam_parity.py`,
`docs/reverse-engineering/qagame-client-spawn-reconstruction-2026-05-26.md`,
`docs/reverse-engineering/qagame-mapping.md`
Parity estimate: **before 98% -> after 98.5%** for the scoped qagame
client-spawn band. The repo-wide parity estimate remains **98%**.

Completed work:

1. Rechecked `G_SelectClientSpawnPoint @ 0x10039730` against the HLIL
   `gametype - 4 <= 7` branch and the current source gametype enum.
2. Replaced the broad source `g_gametype >= GT_CTF` spawn-class shortcut with
   `G_GametypeUsesTeamSpawnSelection`.
3. Restored the retail edge cases: Clan Arena now uses team spawn classes, and
   Red Rover no longer routes through the CTF-style team spawn family before
   its Red Rover role/loadout finalizer.
4. Extended the client-spawn reconstruction note and qagame mapping ledger.

Verification:

- `python -m pytest tests/test_game_helper_seam_parity.py tests/test_game_spectator_connection_parity.py tests/test_game_active_pmove_wiring_parity.py -q --tb=short`
  - Result: `69 passed`.

### Task A98: Reconstruct spectator state and fly-move parity [COMPLETED]
Priority: High
Primary areas: `src/code/game/g_active.c`,
`src/code/game/bg_pmove.c`, `src/code/game/g_items.c`,
`src/code/game/g_main.c`, `src/code/game/bg_public.h`,
`references/symbol-maps/qagame.json`,
`docs/reverse-engineering/qagame-mapping.md`,
`docs/reverse-engineering/qagame-spectator-state-movement-reconstruction-2026-05-26.md`,
`tests/test_game_active_pmove_wiring_parity.py`,
`tests/test_game_factory_regen_parity.py`,
`tests/test_pmove_helper_parity.py`
Parity estimate: **before 93% -> after 99%** for scoped spectator
state/movement and shared fly-move parity; repo-wide remains **98%** pending
the active portability/runtime-evidence gaps.

Completed work:

1. Rechecked qagame `SpectatorThink` at `0x10033E30`, adjacent spectator
   helpers, qagame/cgame `PM_FlyMove`, and `Pickup_Powerup` against the
   committed HLIL and symbol maps.
2. Restored the retail spectator pmove ordering: unlink linked spectators
   before pmove, set `PM_SPECTATOR` with speed `480`, run `Pmove`, copy the
   moved origin, and touch triggers afterward.
3. Restored the retail spectator input edge split: attack-edge follow cycling
   returns before the later `BUTTON_ANY` edge can drop follow state.
4. Collapsed shared `PM_FlyMove` back to the retail four-call path and removed
   source-only Flight fuel/thrust stat seeding from powerup pickup while
   keeping the retail cvar registrations.

Verification:

- `python -m pytest tests/test_game_spectator_connection_parity.py tests/test_game_active_pmove_wiring_parity.py tests/test_pmove_helper_parity.py tests/test_game_factory_regen_parity.py tests/test_bg_misc_validation_fixtures.py -q --tb=short`
  - Result: `118 passed`.
- `git diff --check`
  - Result: pass; only repository LF-to-CRLF conversion warnings.

### Task A97: Reconstruct client-spawn no-spawn retry path [COMPLETED]
Priority: High
Primary areas: `src/code/game/g_client.c`, `src/code/game/g_local.h`,
`tests/test_game_helper_seam_parity.py`,
`docs/reverse-engineering/qagame-client-spawn-reconstruction-2026-05-26.md`,
`docs/reverse-engineering/qagame-mapping.md`
Parity estimate: **before 96% -> after 98%** for the scoped qagame
client-spawn band. The repo-wide parity estimate remains **98%**.

Completed work:

1. Rechecked `ClientSpawn @ 0x1003BC30`, `G_SelectClientSpawnPoint @
   0x10039730`, `G_SelectRankedSpawnPoint @ 0x10039080`,
   `Team_SelectDominationSpawnPoint @ 0x10038B60`, `G_InitClientSpawnState @
   0x1003B6C0`, `G_FinalizeSpawnLoadout @ 0x1003B5A0`, and
   `G_GiveItemByName @ 0x1003BB90` against HLIL, Ghidra, and the curated
   symbol map.
2. Restored the retail active-player no-spawn branch: `ClientSpawn` now
   defers for 600 ms, writes `PM_SPECTATOR`, increments the retry counter, and
   returns before the full client reset when the spawn wrapper cannot produce
   an eligible point.
3. Replaced the inherited unbounded spawnpoint eligibility loop with a bounded
   `FL_NO_BOTS` / `FL_NO_HUMANS` guard and a scheduled retry callback.
4. Added a dedicated reconstruction note and expanded qagame mapping coverage
   for the client-spawn helper family.

Verification:

- `python -m pytest tests/test_game_helper_seam_parity.py tests/test_game_spectator_connection_parity.py tests/test_game_active_pmove_wiring_parity.py -q --tb=short`
  - Result: `69 passed`.

### Task A96: Reconstruct renderer framebuffer owner and retire legacy scratch path [COMPLETED]
Priority: High
Primary areas: `src/code/renderer/tr_backend.c`,
`tests/test_renderer_post_process_parity.py`,
`tests/test_renderer_internal_helper_mapping_parity.py`,
`docs/reverse-engineering/quakelive_steam_mapping_round_324.md`,
`docs/reverse-engineering/renderer-full-parity-audit-and-implementation-plan-2026-04-09.md`,
`docs/reverse-engineering/source-file-parity-ledger-2026-04-22.md`,
`references/hlil/quakelive/quakelive_steam.exe/quakelive_steam.exe_hlil_split/`,
`src2/ghidra/quakelive_steam/quakelive_steam_decomp.cpp`
Parity estimate: **before 99.9% -> after 99.93%** for the scoped
post-process framebuffer owner lane. The strict renderer estimate remains
**100%** and the repo-wide parity estimate remains **98%**.

Completed work:

1. Rechecked retail `sub_4500B0`, `sub_437E40`, `sub_438790`, and
   `sub_4387D0` against HLIL, the Ghidra companion corpus, and the alias
   ledger.
2. Confirmed the live retail-shaped framebuffer owner is the
   `GL_TEXTURE_RECTANGLE_ARB` `RBPP_CreateRenderTarget` path with shared
   depth-stencil renderbuffer attachment.
3. Removed the disconnected legacy `GL_TEXTURE_2D` scene-target structs,
   FBO-loader helpers, and fixed-function scratch-bloom helper family from
   `tr_backend.c`.
4. Rewired end-of-frame release and queued post-process reset handling to call
   `RBPP_ReleaseSceneRenderTarget` and `RBPP_ResetIfNeeded` directly.
5. Updated the renderer audit and source-file ledger; `tr_backend.c` now
   tracks `76` functions after retiring the duplicate helper family.

Verification:

- `python -m pytest tests/test_renderer_post_process_parity.py tests/test_renderer_internal_helper_mapping_parity.py tests/test_renderer_export_tail_parity.py tests/test_renderer_full_parity_gate.py -q --tb=short`
  - Result: `42 passed, 1 skipped`.
- `python -m pytest tests/test_engine_cvar_retail_parity.py::test_engine_cvar_fortysecond_renderer_postprocess_state_tranche_matches_retail_contracts tests/test_engine_cvar_retail_parity.py::test_engine_cvar_twentyninth_renderer_postprocess_extension_tranche_matches_retail_contracts tests/test_engine_cvar_retail_parity.py::test_engine_cvar_thirtysecond_renderer_bloom_picmip_tranche_matches_retail_contracts -q --tb=short`
  - Result: `3 passed`.
- `python -m pytest tests/test_engine_client_command_parity.py::test_postprocess_restart_routes_through_renderer_export_not_renderer_cmd_registration -q --tb=short`
  - Result: `1 passed`.
- `git diff --check`
  - Result: pass; only repository LF-to-CRLF conversion warnings.

### Task A95: Reconstruct teleporting state and related wiring [COMPLETED]
Priority: High
Primary areas: `src/code/game/g_misc.c`,
`tests/test_teleport_state_reconstruction.py`,
`docs/reverse-engineering/qagame-teleport-state-reconstruction-2026-05-26.md`,
`docs/reverse-engineering/qagame-mapping.md`,
`docs/reverse-engineering/cgame-mapping.md`,
`references/symbol-maps/qagame.json`,
`references/hlil/quakelive/qagamex86.dll/qagamex86.dll.bndb_hlil_split/`,
`references/hlil/quakelive/cgamex86.dll/cgamex86.dll_hlil_split/`
Parity estimate: **before 96% -> after 99%** for the scoped teleporting
state and related wiring lane. The repo-wide parity estimate remains **98%**.

Completed work:

1. Rechecked retail `TeleportPlayer` at `0x1005A420`, `Weapon_HookFree` at
   `0x1006E330`, target/trigger teleporter callbacks, holdable teleporter
   event handling, spectator-door teleporting, respawn teleport-in effects,
   dropped-powerup teleporter handling, bot movement flags, and cgame
   teleport consumers against HLIL, Ghidra, and symbol-map evidence.
2. Restored the missing `TeleportPlayer` active-hook cleanup edge:
   `Weapon_HookFree( player->client->hook )` now runs after
   `EF_TELEPORT_BIT` toggles and before destination view-angle / killbox
   handling.
3. Added focused parity tests pinning the server helper, server producers,
   cgame prediction/snapshot/view/event consumers, bot
   `PMF_TIME_KNOCKBACK` -> `MFL_TELEPORTED` bridge, and dropped-powerup
   teleporter movement side path.
4. Added a dedicated reconstruction note and updated qagame/cgame mapping
   ledgers with the observed facts, source delta, confidence, and open
   evidence boundary.

Verification:

- `python -m pytest tests/test_teleport_state_reconstruction.py -q --tb=short`
  - Result: `4 passed`.
- `python -m pytest tests/test_teleport_state_reconstruction.py tests/test_pmove_helper_parity.py tests/test_game_item_runframe_parity.py tests/test_game_target_parity.py tests/test_game_runthink_parity.py tests/test_cgame_snapshot_parity.py tests/test_cgame_event_transport_parity.py -q --tb=short`
  - Result: `88 passed`.
- `git diff --check`
  - Result: pass; only repository LF-to-CRLF conversion warnings.

### Task A94: Split renderer color-correct init and live browser override [COMPLETED]
Priority: High
Primary areas: `src/code/renderer/tr_backend.c`,
`tests/test_renderer_post_process_parity.py`,
`tests/test_renderer_internal_helper_mapping_parity.py`,
`tests/test_engine_cvar_retail_parity.py`,
`docs/reverse-engineering/quakelive_steam_mapping_round_323.md`,
`references/hlil/quakelive/quakelive_steam.exe/quakelive_steam.exe_hlil_split/`,
`src2/ghidra/quakelive_steam/quakelive_steam_decomp.cpp`
Parity estimate: **before 99.85% -> after 99.9%** for the scoped
post-process color-correct browser override lane. The strict renderer estimate
remains **100%** and the repo-wide parity estimate remains **98%**.

Completed work:

1. Rechecked retail `sub_43CD60` and `sub_43CFE0` against HLIL and the Ghidra
   companion corpus.
2. Confirmed that the browser-active override belongs to the live uniform
   refresh helper, while the init helper seeds gamma reciprocal and contrast
   directly from cvars.
3. Added a `browserOverride` parameter to the shared source uniform writer so
   `RBPP_InitColorCorrectResources` passes `qfalse` and
   `RBPP_SetColorCorrectUniformsFromCvars` passes `qtrue`.

Verification:

- `python -m pytest tests/test_renderer_post_process_parity.py tests/test_renderer_internal_helper_mapping_parity.py tests/test_renderer_export_tail_parity.py tests/test_renderer_full_parity_gate.py -q --tb=short`
  - Result: `41 passed, 1 skipped`.
- `python -m pytest tests/test_engine_cvar_retail_parity.py::test_engine_cvar_fortysecond_renderer_postprocess_state_tranche_matches_retail_contracts tests/test_engine_cvar_retail_parity.py::test_engine_cvar_twentyninth_renderer_postprocess_extension_tranche_matches_retail_contracts tests/test_engine_cvar_retail_parity.py::test_engine_cvar_thirtysecond_renderer_bloom_picmip_tranche_matches_retail_contracts -q --tb=short`
  - Result: `3 passed`.
- `python -m pytest tests/test_engine_cvar_retail_parity.py::test_engine_cvar_twentythird_renderer_runtime_tuning_tranche_matches_retail_contracts tests/test_engine_cvar_retail_parity.py::test_engine_cvar_thirtyeighth_renderer_image_quality_tranche_matches_retail_contracts -q --tb=short`
  - Result: `2 passed`.
- `python -m pytest tests/test_engine_client_command_parity.py::test_postprocess_restart_routes_through_renderer_export_not_renderer_cmd_registration -q --tb=short`
  - Result: `1 passed`.
- `git diff --check`
  - Result: pass; only repository LF-to-CRLF conversion warnings.

### Task A93: Reconstruct renderer live post-process cvar refresh [COMPLETED]
Priority: High
Primary areas: `src/code/renderer/tr_cmds.c`,
`src/code/renderer/tr_backend.c`,
`src/code/renderer/tr_init.c`,
`src/code/renderer/tr_local.h`,
`tests/test_renderer_post_process_parity.py`,
`tests/test_renderer_internal_helper_mapping_parity.py`,
`tests/test_engine_cvar_retail_parity.py`,
`docs/reverse-engineering/quakelive_steam_mapping_round_322.md`,
`references/hlil/quakelive/quakelive_steam.exe/quakelive_steam.exe_hlil_split/`,
`src2/ghidra/quakelive_steam/quakelive_steam_decomp.cpp`
Parity estimate: **before 99.7% -> after 99.85%** for the scoped
post-process live cvar refresh lane. The strict renderer estimate remains
**100%** and the repo-wide parity estimate remains **98%**.

Completed work:

1. Rechecked the retail `RE_BeginFrame` post-texture-mode branch against HLIL
   and the Ghidra companion corpus.
2. Moved live post-process modified-latch consumption out of
   `R_UpdatePostProcessCvars`, preserving that function as the enable/restart
   state owner.
3. Added `R_RefreshLivePostProcessCvars` in `tr_cmds.c` so frame-begin now
   refreshes color-correct uniforms from `r_gamma/r_contrast`, refreshes bloom
   uniforms from the five live bloom cvars, and leaves `r_gamma->modified` for
   the later `R_SetColorMappings` path.
4. Exposed the two active-state guarded backend uniform helpers through
   `tr_local.h` while keeping the low-level uniform writers private.

Verification:

- `python -m pytest tests/test_renderer_post_process_parity.py tests/test_renderer_internal_helper_mapping_parity.py tests/test_renderer_export_tail_parity.py tests/test_renderer_full_parity_gate.py -q --tb=short`
  - Result: `40 passed, 1 skipped`.
- `python -m pytest tests/test_engine_cvar_retail_parity.py::test_engine_cvar_fortysecond_renderer_postprocess_state_tranche_matches_retail_contracts tests/test_engine_cvar_retail_parity.py::test_engine_cvar_twentyninth_renderer_postprocess_extension_tranche_matches_retail_contracts tests/test_engine_cvar_retail_parity.py::test_engine_cvar_thirtysecond_renderer_bloom_picmip_tranche_matches_retail_contracts -q --tb=short`
  - Result: `3 passed`.
- `python -m pytest tests/test_engine_client_command_parity.py::test_postprocess_restart_routes_through_renderer_export_not_renderer_cmd_registration -q --tb=short`
  - Result: `1 passed`.
- Direct source sentinel for the `test_engine_cvar_fortyfirst_renderer_platform_scene_tranche_matches_retail_contracts` post-process assertions:
  - Result: passed.
- `python -m pytest tests/test_engine_cvar_retail_parity.py::test_engine_cvar_fortyfirst_renderer_platform_scene_tranche_matches_retail_contracts -q --tb=short`
  - Result: failed before the new post-process assertions on an unrelated
    read-only `src/ui/ui_main.c` `r_inGameVideo` expectation.
- `git diff --check`
  - Result: pass; only repository LF-to-CRLF conversion warnings.

### Task A92: Reconstruct renderer color-correct uniform helper [COMPLETED]
Priority: High
Primary areas: `src/code/renderer/tr_backend.c`,
`tests/test_renderer_post_process_parity.py`,
`tests/test_renderer_internal_helper_mapping_parity.py`,
`docs/reverse-engineering/quakelive_steam_mapping_round_321.md`,
`references/hlil/quakelive/quakelive_steam.exe/quakelive_steam.exe_hlil_split/`,
`src2/ghidra/quakelive_steam/quakelive_steam_decomp.cpp`
Parity estimate: **before 99.5% -> after 99.7%** for the scoped
post-process color-correct uniform helper lane. The strict renderer estimate
remains **100%** and the repo-wide parity estimate remains **98%**.

Completed work:

1. Rechecked `sub_43CD60`, `sub_43CFE0`, and `sub_436DC0` against HLIL and
   the Ghidra companion corpus.
2. Split color-correct cvar-to-uniform writes out of the draw pass into
   `RBPP_SetColorCorrectUniforms` and the active-state guarded
   `RBPP_SetColorCorrectUniformsFromCvars` helper.
3. Seeded the color-correct program uniforms during
   `RBPP_InitColorCorrectResources`, matching the initialization write sequence
   recovered from `sub_43CFE0`.
4. Left `RBPP_ApplyColorCorrectPass` focused on framebuffer copy, live uniform
   refresh through the recovered helper, and full-screen draw execution.

Verification:

- `python -m pytest tests/test_renderer_post_process_parity.py tests/test_renderer_internal_helper_mapping_parity.py tests/test_renderer_export_tail_parity.py tests/test_renderer_full_parity_gate.py -q --tb=short`
  - Result: `39 passed, 1 skipped`.
- `python -m pytest tests/test_engine_client_command_parity.py::test_postprocess_restart_routes_through_renderer_export_not_renderer_cmd_registration -q --tb=short`
  - Result: `1 passed`.
- `python -m pytest tests/test_engine_cvar_retail_parity.py::test_engine_cvar_fortysecond_renderer_postprocess_state_tranche_matches_retail_contracts tests/test_engine_cvar_retail_parity.py::test_engine_cvar_twentyninth_renderer_postprocess_extension_tranche_matches_retail_contracts -q --tb=short`
  - Result: `2 passed`.
- `git diff --check`
  - Result: pass; only repository LF-to-CRLF conversion warnings.

### Task A91: Correct renderer post-process bloom uniform slot order [COMPLETED]
Priority: High
Primary areas: `src/code/renderer/tr_backend.c`,
`src/code/renderer/tr_local.h`,
`tests/test_renderer_post_process_parity.py`,
`tests/test_renderer_internal_helper_mapping_parity.py`,
`docs/reverse-engineering/quakelive_steam_mapping_round_320.md`,
`references/hlil/quakelive/quakelive_steam.exe/quakelive_steam.exe_hlil_split/`,
`src2/ghidra/quakelive_steam/quakelive_steam_decomp.cpp`
Parity estimate: **before 99% -> after 99.5%** for the scoped
post-process bloom uniform naming lane. The strict renderer estimate remains
**100%** and the repo-wide parity estimate remains **98%**.

Completed work:

1. Rechecked `sub_4380F0`, `sub_438590`, and `sub_4386D0` against HLIL and
   the Ghidra companion corpus for the combine uniform slot order.
2. Corrected the private five-float source signature so the last two arguments
   are `sceneSaturation` and then `sceneIntensity`.
3. Reordered the source-side combine uniform fields, uniform lookup, and uniform
   write path to mirror the retail slots:
   `p_bloomsaturation`, `p_scenesaturation`, `p_bloomintensity`,
   `p_sceneintensity`.
4. Added a dedicated mapping note and parity sentinels so the argument/slot
   order cannot drift back to shader-declaration order.

Verification:

- `python -m pytest tests/test_renderer_post_process_parity.py tests/test_renderer_internal_helper_mapping_parity.py tests/test_renderer_export_tail_parity.py tests/test_renderer_full_parity_gate.py -q --tb=short`
  - Result: `38 passed, 1 skipped`.
- `python -m pytest tests/test_engine_client_command_parity.py::test_postprocess_restart_routes_through_renderer_export_not_renderer_cmd_registration -q --tb=short`
  - Result: `1 passed`.
- `python -m pytest tests/test_engine_cvar_retail_parity.py::test_engine_cvar_thirtysecond_renderer_bloom_picmip_tranche_matches_retail_contracts -q --tb=short`
  - Result: `1 passed`.
- `git diff --check`
  - Result: pass; only repository LF-to-CRLF conversion warnings.

### Task A90: Reconstruct qagame knockback application and blocking [COMPLETED]
Priority: High
Primary areas: `src/code/game/g_combat.c`, `src/game/g_config.c`,
`tests/test_game_weapon_parity.py`, `tests/test_pmove_helper_parity.py`,
`docs/reverse-engineering/qagame-knockback-reconstruction-2026-05-26.md`,
`docs/reverse-engineering/qagame-mapping.md`, `docs/gameplay/cvars.md`,
`docs/gameplay-cvars-and-steam.md`, `references/symbol-maps/qagame.json`,
`references/symbol-maps/cgame.json`,
`src/code/game/ai_dmq3.c`, `src/code/game/g_target.c`,
`src/code/game/g_missile.c`, `src/code/botlib/be_aas_move.c`,
`src/code/botlib/be_ai_move.c`,
`references/hlil/quakelive/qagamex86.dll/qagamex86.dll.bndb_hlil_split/`
Parity estimate: **before 82% -> after 98%** for the scoped qagame
knockback application, no-knockback producer, and movement-blocking lane. The repo-wide parity
estimate remains **98%**.

Completed work:

1. Rechecked retail `G_KnockbackScaleForMOD` at `0x10048A10` and `G_Damage`
   at `0x10048C30` against HLIL, Ghidra, and the existing symbol map.
2. Reconstructed signed knockback application so negative scalars invert the
   damage direction and still latch `PMF_TIME_KNOCKBACK`.
3. Kept `FL_NO_KNOCKBACK` and `DAMAGE_NO_KNOCKBACK` as zeroing gates before
   velocity or timer side effects.
4. Removed non-retail `G_Damage` vertical boost and crouch/low-health cripple
   velocity reduction; `g_knockback_cripple` now remains only as the retail
   knockback timer floor.
5. Added focused source/evidence sentinels and a dedicated reconstruction
   note for the signed knockback and blocking seam, including the shared
   pmove friction, walk acceleration, drop-timer, spawn-side timer wiring, and
   teleport-side timer wiring.
6. Removed the inherited Quake III `damage_knockback` feedback slot/write/reset
   after rechecking retail `G_Damage` and `P_DamageFeedback`: Quake Live stores
   only armor, blood, `damage_from`, and `damage_fromWorld` in that record.
7. Pinned the bot-side move initializer wiring where active
   `PMF_TIME_KNOCKBACK` plus positive `pm_time` raises `MFL_TELEPORTED` before
   the waterjump movement flag.
8. Pinned the no-knockback producers (`target_laser_think` and juiced prox
   discharge), the null-direction `DAMAGE_NO_KNOCKBACK` conversion, the fatal
   `FL_NO_KNOCKBACK` ordering, and the companion botlib weapon-jump predictor.
9. Aligned the `g_max_knockback` help text in both registration tables with
   the reconstructed positive-only clamp behavior.
10. Rechecked reconstructed source style: added the required function headers
    for `G_ReadKnockbackCvar` and `G_UpdateKnockbackConfig`, clarified the
    `G_Damage` knockback comment, and tab-indented `knockbackConfig_t`.
11. Added a graph-level wiring map to the reconstruction note and pinned the
    live knockback, no-knockback, pmove, feedback, bot bridge, and botlib
    predictor nodes in the focused parity suite.
12. Removed the source-only `g_debugDamage` knockback summary instrumentation
    after the committed HLIL/string corpus showed only the retail
    health/damage/armor debug print in `G_Damage`.

Verification:

- `python -m pytest tests/test_game_weapon_parity.py -q --tb=short`
  - Result: `35 passed`.
- `python -m pytest tests/test_game_active_pmove_wiring_parity.py -q --tb=short`
  - Result: `32 passed`.
- `python -m pytest tests/test_pmove_helper_parity.py -q --tb=short`
  - Result: `40 passed`.
- `python -m pytest tests/test_game_target_parity.py -q --tb=short`
  - Result: `11 passed`.
- `python -m pytest tests/test_game_weapon_parity.py tests/test_game_active_pmove_wiring_parity.py tests/test_pmove_helper_parity.py tests/test_game_target_parity.py -q --tb=short`
  - Result: `118 passed`.
- `git diff --check`
  - Result: pass; only repository LF-to-CRLF warnings were reported.

### Task A89: Reconstruct renderer post-process private refexport tail [COMPLETED]
Priority: High
Primary areas: `src/code/renderer/tr_backend.c`,
`src/code/renderer/tr_init.c`, `src/code/renderer/tr_local.h`,
`src/code/renderer/tr_public.h`,
`tests/test_renderer_export_tail_parity.py`,
`tests/test_renderer_post_process_parity.py`,
`tests/test_renderer_internal_helper_mapping_parity.py`,
`docs/reverse-engineering/quakelive_steam_mapping_round_319.md`,
`references/hlil/quakelive/quakelive_steam.exe/quakelive_steam.exe_hlil_split/`
Parity estimate: **before 96% -> after 99%** for the scoped post-process
private-tail lane. The strict renderer estimate remains **100%** and the
repo-wide parity estimate remains **98%**.

Completed work:

1. Rechecked the retail `GetRefAPI` tail assignments around `data_5878c0`
   through `data_5878cc`, including `j_sub_4384D0` and `sub_451420`.
2. Added the missing `RetailBloomPostProcessCommand` refexport slot between
   scene-target capture and post-process restart.
3. Assigned the bloom command and five-float bloom uniform setter through
   `GetRefAPI`.
4. Factored the bloom uniform writes into `RBPP_SetBloomUniforms` and added the
   cvar-refresh helper matching `sub_438590`.
5. Mirrored the retail dirty-flag behavior so temporary tail-set bloom uniforms
   are restored from cvars after the next bloom command.

Verification:

- `python -m pytest tests/test_renderer_post_process_parity.py tests/test_renderer_internal_helper_mapping_parity.py tests/test_renderer_export_tail_parity.py tests/test_renderer_full_parity_gate.py -q --tb=short`
  - Result: `37 passed, 1 skipped`.
- `python -m pytest tests/test_engine_client_command_parity.py::test_postprocess_restart_routes_through_renderer_export_not_renderer_cmd_registration -q --tb=short`
  - Result: `1 passed`.
- `git diff --check`
  - Result: pass; only repository LF-to-CRLF conversion warnings.

### Task A88: Reconstruct renderer post-process backend command ABI [COMPLETED]
Priority: High
Primary areas: `src/code/renderer/tr_backend.c`,
`src/code/renderer/tr_cmds.c`, `src/code/renderer/tr_init.c`,
`src/code/renderer/tr_local.h`, `src/code/renderer/tr_shader.c`,
`tests/test_renderer_post_process_parity.py`,
`tests/test_renderer_internal_helper_mapping_parity.py`,
`docs/reverse-engineering/quakelive_steam_mapping_round_318.md`,
`references/analysis/quakelive_symbol_aliases.json`,
`references/hlil/quakelive/quakelive_steam.exe/quakelive_steam.exe_hlil_split/`
Parity estimate: **before 88% -> after 96%** for the scoped post-process
command ABI lane. The strict renderer estimate remains **100%** and the
repo-wide parity estimate remains **98%**.

Completed work:

1. Rechecked the retail command emitter and executor evidence around
   `sub_43CD10`, `sub_4384D0`, `sub_43CBA0`, `sub_436DC0`,
   `sub_436EC0`, and the `sub_437A50` backend dispatch table.
2. Reconstructed command payloads for color correction (`0x10` bytes), bloom
   (`0x38` bytes), and scene-target binding (`0x04` bytes), preserving retail
   command IDs `9`, `10`, and `11`.
3. Added frontend emitters and backend handlers for the post-process command
   lane, then routed draw-surface scene capture and end-frame post-processing
   through queued commands instead of the swap-buffer shortcut.
4. Updated command-list repair walking and the private refexport capture slot
   so the newly reconstructed commands are visible in related wiring.
5. Promoted command-handler aliases for `sub_436DC0` and `sub_436EC0` to match
   their observed command-size returns.

Verification:

- `python -m pytest tests/test_renderer_post_process_parity.py
  tests/test_renderer_internal_helper_mapping_parity.py
  tests/test_renderer_export_tail_parity.py tests/test_renderer_full_parity_gate.py
  -q --tb=short` passed: `35 passed, 1 skipped`.
- `python -m pytest
  tests/test_engine_client_command_parity.py::test_postprocess_restart_routes_through_renderer_export_not_renderer_cmd_registration
  -q --tb=short` passed: `1 passed`.
- `git diff --check` completed without whitespace errors; Git reported only
  line-ending normalization warnings for modified text files.

### Task A87: Reconstruct renderer post-process bloom scene-target wiring [COMPLETED]
Priority: High
Primary areas: `src/code/renderer/tr_backend.c`,
`src/code/renderer/tr_image.c`, `src/code/renderer/tr_local.h`,
`tests/test_renderer_post_process_parity.py`,
`tests/test_renderer_internal_helper_mapping_parity.py`,
`docs/reverse-engineering/quakelive_steam_mapping_round_317.md`,
`docs/reverse-engineering/renderer-full-parity-audit-and-implementation-plan-2026-04-09.md`,
`references/hlil/quakelive/quakelive_steam.exe/quakelive_steam.exe_hlil_split/`
Parity estimate: **before 98% -> after 99.5%** for the scoped renderer
post-process scene-target and bloom/color-correct owner boundary. The strict
renderer estimate remains **100%** and the repo-wide parity estimate remains
**98%**.

Completed work:

1. Rechecked the retail `quakelive_steam.exe` post-process evidence around
   `sub_4384A0`, `sub_4380F0`, `sub_438790`, screenshot readback, and the
   backend command ID `0x0b` scene-target rebind path.
2. Promoted the source-side `RBPP_BloomEnabled()` predicate so the scene
   render target is gated by the same broad post-process, shader-support, and
   `r_bloomActive` checks recovered from retail.
3. Moved the full-resolution scene target into the bloom resource lifecycle,
   matching the retail split where color correction owns a default-framebuffer
   copy/pass and bloom owns offscreen scene capture.
4. Rewired scene-target binding, screenshot release/rebind, and post-process
   submission so color-correct-only frames no longer route world rendering
   through the bloom scene framebuffer.
5. Added focused parity sentinels and a dedicated mapping note for the
   bloom-owned scene-target boundary.

Verification:

- `python -m pytest tests/test_renderer_post_process_parity.py
  tests/test_renderer_internal_helper_mapping_parity.py
  tests/test_renderer_full_parity_gate.py -q --tb=short` passed:
  `27 passed, 1 skipped`.
- `python -m pytest tests/test_renderer_export_tail_parity.py
  tests/test_engine_client_command_parity.py::test_postprocess_restart_routes_through_renderer_export_not_renderer_cmd_registration
  -q --tb=short` passed: `7 passed`.
- `git diff --check` completed without whitespace errors; Git reported only
  line-ending normalization warnings for modified text files.

### Task A86: Reconstruct retail qagame score, vote, and cheat command ladder [COMPLETED]
Priority: High
Primary areas: `src/code/game/g_cmds.c`,
`tests/test_game_helper_seam_parity.py`,
`docs/reverse-engineering/qagame-score-vote-cheat-command-reconstruction-2026-05-25.md`,
`docs/reverse-engineering/qagame-mapping.md`,
`references/hlil/quakelive/qagamex86.dll/qagamex86.dll.bndb_hlil_split/`
Parity estimate: **before 72% -> after 93%** for the scoped ten-command
score/stat/ready/vote/cheat `ClientCommand` surface (`score`, `acc`,
`pstats`, `readyup`, `vote`, `give`, `god`, `notarget`, `noclip`, and `kill`)
plus the adjacent `ragequit` boundary and next-map vote wiring. The repo-wide
parity estimate remains **98%**.

Completed work:

1. Rechecked the qagame HLIL `ClientCommand` ladder at `sub_10045DEC`, the
   command strings around `data_10084EF8` through `data_10084F40`, and helper
   strings for accuracy payloads, vote handling, cheat toggles, and kill
   rejection.
2. Revalidated symbol-map ownership for `Cmd_Score_f`, `Cmd_Acc_f`,
   `Cmd_Pstats_f`, `Cmd_ReadyUp_f`, `Cmd_Vote_f`, `Cmd_Give_f`, `Cmd_God_f`,
   `Cmd_Notarget_f`, `Cmd_Noclip_f`, `Cmd_Kill_f`, and `ClientCommand`.
3. Reordered `ClientCommand` so `acc`, `pstats`, `readyup`, and `vote` sit in
   the recovered retail pre-intermission cluster after `score`.
4. Moved source-local compatibility branches (`ready`, `notready`, `unready`,
   `players`, `teams`, and `cvar`) after the retail `vote` branch.
5. Removed the later post-intermission `vote` branch, making
   `G_HandleNextMapVote` reachable during intermission through `Cmd_Vote_f`.
6. Added a focused parity sentinel tying the ten command names to source
   dispatch order, helper bodies, HLIL command strings, and recovered
   vote/cheat/self-kill messages.

Open boundary:

- Retail `ragequit` is visible between `readyup` and `vote`, but its target is
  a one-argument native import at `data_104B13AC + 0x300`. This pass leaves it
  documented rather than reconstructing behavior before the import owner is
  cross-validated.

Verification:

- `python -m pytest tests/test_game_helper_seam_parity.py -q --tb=short -k
  "score_vote_cheat_client_command_tranche"` passed:
  `1 passed, 29 deselected`.
- `python -m pytest tests/test_game_helper_seam_parity.py -q --tb=short`
  passed: `30 passed`.
- `python -m pytest
  tests/test_game_exit_rules_parity.py::test_nextmap_vote_pipeline_matches_retail_intermission_vote_flow
  tests/test_vote_ui_throttle.py::test_vote_ui_throttle_transitions -q
  --tb=short` passed/skipped: `1 passed, 1 skipped`.

### Task A85: Reconstruct retail qagame chat and voice command ladder [COMPLETED]
Priority: High
Primary areas: `src/code/game/g_cmds.c`,
`tests/test_game_helper_seam_parity.py`,
`docs/reverse-engineering/qagame-chat-voice-command-reconstruction-2026-05-25.md`,
`docs/reverse-engineering/qagame-mapping.md`,
`references/hlil/quakelive/qagamex86.dll/qagamex86.dll.bndb_hlil_split/`
Parity estimate: **before 78% -> after 95%** for the scoped ten-command
chat/voice `ClientCommand` surface (`say`, `say_team`, `tell`, `botSay`,
`vsay`, `vsay_team`, `vtell`, `vosay`, `vosay_team`, and `votell`) plus the
adjacent `vtaunt` boundary and voice/tell transport helpers. The repo-wide
parity estimate remains **98%**.

Completed work:

1. Rechecked the qagame HLIL `ClientCommand` ladder at `sub_10045DEC`, the
   command strings at `data_10084EAC` through `data_10084EF0`, and the helper
   bodies around `sub_10041B60`, `sub_10041B90`, `sub_10041CC0`,
   `sub_10041E40`, `sub_10041E60`, and `sub_10041F50`.
2. Revalidated symbol-map ownership for `Cmd_Say_f`, `Cmd_Tell_f`,
   `Cmd_BotSay_f`, `Cmd_Voice_f`, `Cmd_VoiceTell_f`, `Cmd_VoiceTaunt_f`, and
   `ClientCommand`.
3. Reordered `ClientCommand` so the retail chat/voice cluster flows directly
   from `botSay` into `vsay`; the source-local `complaint` hook remains
   supported, but now sits after the adjacent `vtaunt` retail boundary.
4. Added a focused parity sentinel tying the ten command names to source
   dispatch order, handler calls, HLIL strings, voice transport commands,
   private tell echo behavior, bot chat payloads, and voice flood labels.
5. Added a dedicated reconstruction note and refreshed the qagame mapping
   ledger with this source-reconstruction pass.

Verification:

- `python -m pytest tests/test_game_helper_seam_parity.py -q --tb=short -k
  "chat_voice_client_command_tranche or game_say_reconstructs"` passed:
  `2 passed, 27 deselected`.
- `python -m pytest tests/test_game_helper_seam_parity.py -q --tb=short`
  passed: `29 passed`.

### Task A84: Reconstruct retail qagame server-command wiring tranche [COMPLETED]
Priority: High
Primary areas: `src/code/game/g_cmds.c`, `src/code/game/g_svcmds.c`,
`src/code/game/g_bot.c`, `src/code/game/g_mem.c`,
`tests/test_game_helper_seam_parity.py`,
`docs/reverse-engineering/qagame-server-command-wiring-reconstruction-2026-05-25.md`,
`docs/reverse-engineering/qagame-mapping.md`,
`references/hlil/quakelive/qagamex86.dll/qagamex86.dll.bndb_hlil_split/`
Parity estimate: **before 82% -> after 94%** for the scoped ten-command
qagame server-command surface (`addscore`, `addteamscore`, `setmatchtime`,
`entitylist`, `forceteam`, `game_memory`, `addbot`, `botlist`, `game_crash`,
and `reload_access`) plus the related direct-table, console-dispatch, bot
media-refresh, and helper wiring. The repo-wide parity estimate remains
**98%**.

Completed work:

1. Rechecked the owning `qagamex86.dll` corpus metadata/import/export/function
   evidence, the qagame symbol map, the `data_10080750` direct command table,
   `ConsoleCommand` at `sub_10066B90`, and `Svcmd_AddBot_f` at `sub_10037910`.
2. Revalidated the retail direct command table tail rows for `addscore`,
   `addteamscore`, and `setmatchtime` against the recovered command strings,
   handlers, privilege floors, and observable score/time messages.
3. Revalidated server-console dispatch for `entitylist`, `forceteam`,
   `game_memory`, `addbot`, `botlist`, `game_crash`, and `reload_access`
   against source helpers and HLIL command-token comparisons.
4. Corrected `Svcmd_AddBot_f` so its local-client media refresh sends
   `loaddeferred\n`, matching retail Quake Live and the existing
   `G_AddTrainerBot` path.
5. Added a focused parity sentinel tying the ten command names to source
   dispatch, helper bodies, symbol-map identities, HLIL strings, and the
   corrected addbot server-command spelling.
6. Added a dedicated reconstruction note and refreshed the qagame mapping
   ledger with this source-reconstruction pass.

Verification:

- `python -m pytest tests/test_game_helper_seam_parity.py -q --tb=short -k
  "server_command_wiring or console_tail or direct_score_time"` passed:
  `3 passed, 25 deselected`.
- `python -m pytest tests/test_game_helper_seam_parity.py -q --tb=short`
  passed: `28 passed`.

### Task A83: Reconstruct retail qagame direct command table tail [COMPLETED]
Priority: High
Primary areas: `src/code/game/g_cmds.c`,
`tests/test_game_helper_seam_parity.py`,
`docs/reverse-engineering/qagame-direct-command-table-tail-reconstruction-2026-05-25.md`,
`docs/reverse-engineering/qagame-mapping.md`,
`references/hlil/quakelive/qagamex86.dll/qagamex86.dll.bndb_hlil_split/`
Parity estimate: **before 18% -> after 91%** for the scoped remaining
direct-command table tail (`addscore`, `addteamscore`, `setmatchtime`, and the
help-visible null-handler `rcon` row). The repo-wide parity estimate remains
**98%**.

Completed work:

1. Rechecked the `data_10080750` tail rows at `0x100808F4`, `0x10080908`,
   `0x1008091C`, and `0x10080930`, plus the `sub_10061670`,
   `sub_10061730`, `sub_10062CE0`, and `sub_10070B40` HLIL bodies.
2. Added direct table rows for `addscore`, `addteamscore`, `setmatchtime`, and
   help-visible `rcon`.
3. Updated direct dispatch so matched rows with null handlers fall through
   instead of being invoked, matching the recovered `rcon` row.
4. Added score adjustment handlers for player and team score deltas with the
   recovered `Player score adjusted.`, `Team score adjusted.`, and
   increase/decrease print strings.
5. Added `setmatchtime` handling that rewrites `CS_LEVEL_START_TIME` from
   `level.time`, formats whole seconds as `%i:%i%i`, and broadcasts the
   recovered match-time confirmation.
6. Added a reconstruction note, qagame mapping rows, and parity sentinels for
   the remaining table offsets, strings, and source wiring.

Verification:

- `python -m pytest tests/test_game_helper_seam_parity.py -q --tb=short -k
  "direct_score_time or direct_admin_access or direct_command_table"` passed:
  `3 passed, 24 deselected`.

### Task A82: Reconstruct retail qagame direct admin command tranche [COMPLETED]
Priority: High
Primary areas: `src/code/game/g_cmds.c`, `src/code/game/g_main.c`,
`src/code/game/g_local.h`, `tests/test_game_helper_seam_parity.py`,
`docs/reverse-engineering/qagame-direct-admin-command-reconstruction-2026-05-25.md`,
`docs/reverse-engineering/qagame-mapping.md`,
`references/hlil/quakelive/qagamex86.dll/qagamex86.dll.bndb_hlil_split/`
Parity estimate: **before 34% -> after 87%** for the scoped ten-command
direct admin/access command surface (`mute`, `unmute`, `tempban`, `ban`,
`listaccess`, `unban`, `addadmin`, `addmod`, `demote`, and `abort`) plus the
related access-list page printer, access-entry mutation helpers, kick/drop
helper, and `opsay` privilege-floor correction. The repo-wide parity estimate
remains **98%**; later direct table rows such as `addscore`, `addteamscore`,
and `setmatchtime` are closed by Task A83.

Completed work:

1. Rechecked the qagame HLIL direct command table at `data_10080750`, the
   symbol map rows for `0x10061550`, `0x10062470` through `0x10062C60`, and the
   access-list page helper at `0x100327D0`.
2. Extended the direct command table with the ten selected retail rows and
   corrected `opsay` from admin to moderator privilege based on the adjacent
   table-entry byte layout.
3. Reworked `mute` and `unmute` around the shared PlayerID resolver and
   recovered broadcast strings, including the same-or-higher target guard for
   `mute`.
4. Added source-side access-list mutation helpers and `G_PrintAccessListPage`
   with the recovered 20-entry page size, separator, tier labels, and
   `TEMP`/`PERM` mode column.
5. Rebuilt `tempban` and `ban` through the retail-style shared helper: direct
   rows use PlayerID lookup, refuse privileged targets, write temporary or
   permanent ban entries, and drop clients with `was kicked`.
6. Added `addadmin`, `addmod`, `demote`, `unban`, `listaccess`, and `abort`
   handlers, including the recovered promotion/demotion broadcasts, `priv %i`
   refreshes, unban confirmation, timeout-active abort rejection, `PRE_GAME`
   reset, and `map_restart 3`.
7. Added a dedicated reconstruction note, expanded qagame mapping rows, and
   added helper seam parity tests covering the selected table offsets, exact
   HLIL strings, access-list format, and source wiring.

Verification:

- `python -m pytest tests/test_game_helper_seam_parity.py -q --tb=short -k
  "direct_admin_access or direct_mute or direct_command_table or timeout_race"`
  passed: `4 passed, 22 deselected`.
- `python -m pytest tests/test_game_helper_seam_parity.py -q --tb=short`
  passed: `26 passed`.

### Task A81: Restore retail parity for access, A&D bonus, flood, drop-health, knockback, and vampiric `g_*` CVar tranche [COMPLETED]
Priority: High
Primary areas: `src/code/game/g_main.c`, `src/game/g_config.c`,
`src/code/game/g_combat.c`, `src/code/game/g_items.c`,
`src/code/game/g_team.c`, `src/code/game/g_active.c`,
`src/code/game/g_cmds.c`, `src/code/game/g_svcmds.c`,
`tests/test_game_active_pmove_wiring_parity.py`,
`docs/gameplay/cvars.md`,
`docs/attack_defend_bonuses.md`,
`references/hlil/quakelive/qagamex86.dll/qagamex86.dll.bndb_hlil_split/`
Parity estimate: **before 69% -> after 100%** for the scoped ten-CVar
registration/default/flag/wiring surface. This batch explicitly skipped the
vote/complaint rows and the A78-A80 rows already closed in this local run,
while also avoiding rows called out as inspected by session
`019e6082-1189-74e3-8bdc-423ce9f7ef4d`.

Completed work:

1. Rechecked retail qagame HLIL rows, defaults, and registration flags for
   `g_accessFile`, `g_adTouchScoreBonus`, `g_adElimScoreBonus`,
   `g_adCaptureScoreBonus`, `g_floodprot_maxcount`,
   `g_floodprot_decay`, `g_dropDamagedHealth`, `g_max_knockback`,
   `g_returnFlagOnSuicide`, and `g_vampiricDamage`.
2. Corrected the Attack & Defend bonus rows from source-local archive flags
   to retail `CVAR_SERVERINFO | CVAR_GAMERULE` while preserving the recovered
   `1`, `2`, and `3` defaults and score/announcement wiring.
3. Corrected flood protection to retail runtime-only rows, including the
   `g_floodprot_maxcount=10` default shared by active-client decay, command
   flood gating, and `floodstatus`.
4. Corrected `g_dropDamagedHealth` to retail default `0` with
   `CVAR_TEMP | 0x00040000 | CVAR_GAMERULE`, and aligned the custom-settings
   digest so the `DROP DAMAGED HEALTH` bit only appears when the cvar is
   enabled.
5. Corrected `g_max_knockback` to retail default `120` and `CVAR_GAMERULE`
   across both the legacy game cvar table and the config helper table, then
   moved the invalid-value fallback used by knockback config/damage code to
   the same value.
6. Corrected `g_returnFlagOnSuicide` to retail default `0` and
   `CVAR_GAMERULE`, while preserving the cached flag config wiring.
7. Corrected `g_vampiricDamage` to retail
   `0x00040000 | CVAR_GAMERULE` and revalidated the combat reward,
   custom-settings, and Steam tag hooks.
8. Documented the tranche in gameplay CVar notes and refreshed the A&D bonus
   tuning note so it no longer describes the retail gamerule rows as archived.

Verification:

- `python -m pytest tests/test_game_active_pmove_wiring_parity.py -q
  --tb=short` passed after the tranche update.
- `python -m pytest tests/test_game_weapon_parity.py
  tests/test_bot_resource_loading.py tests/test_spawn_spec_cvars.py -q
  --tb=short` passed for adjacent knockback/access/spawn documentation
  sentinels.

### Task A80: Restore retail parity for Freeze reset, last-man, and Red Rover zombie `g_*` CVar tranche [COMPLETED]
Priority: High
Primary areas: `src/code/game/g_main.c`, `src/code/game/g_active.c`,
`src/code/game/g_freeze.c`, `src/code/game/g_team.c`,
`src/code/game/g_client.c`, `tests/test_game_active_pmove_wiring_parity.py`,
`tests/test_freeze_cvars.py`, `tests/test_game_helper_seam_parity.py`,
`docs/gameplay/cvars.md`,
`references/hlil/quakelive/qagamex86.dll/qagamex86.dll.bndb_hlil_split/`
Parity estimate: **before 57% -> after 100%** for the scoped ten-CVar
Freeze reset, last-man-standing, and Red Rover zombie spawn-trait
registration/default/wiring surface. This batch explicitly excluded the
`g_*` cvars already closed by session `019e6082-1189-74e3-8bdc-423ce9f7ef4d`
and the local A55-A79 ledger.

Completed work:

1. Rechecked retail qagame HLIL rows, defaults, and registration flags for
   `g_freezeThawWinningTeam`, `g_freezeThawThroughSurface`,
   `g_freezeResetWeaponsOnRound`, `g_freezeResetHealthOnRound`,
   `g_freezeResetArmorOnRound`, `g_freezeRemovePowerupsOnRound`,
   `g_lastManStandingWarning`, `g_lastManStandingMessage`,
   `g_rrInfectedZombieHealthBonus`, and `g_rrInfectedZombieSpeed`.
2. Corrected the six Freeze reset/thaw rows to retail `CVAR_GAMERULE`
   surfaces, including the retail `g_freezeThawWinningTeam=1` default.
3. Corrected the last-man rows to zero flags and corrected
   `g_lastManStandingMessage` and its empty-cvar fallback to the retail
   `You are the last standing` payload.
4. Corrected the Red Rover infected zombie health and speed rows to retail
   `CVAR_GAMERULE` surfaces while preserving the recovered `50` and `1.15`
   defaults.
5. Revalidated functionality through Freeze config caching, thaw-through-wall
   line-of-sight gates, winner thaw release, reset weapon/health/armor/powerup
   handling, CA/FZ/A&D/RR last-alive notification, Red Rover infected spawn
   health finalization, and infected speed scaling.
6. Added HLIL-backed parity sentinels and updated gameplay cvar notes for the
   audited controls.

Verification:

- `python -m pytest tests/test_game_active_pmove_wiring_parity.py -q
  --tb=short` passed: `24 passed`.
- `python -m pytest tests/test_freeze_cvars.py
  tests/test_game_helper_seam_parity.py::test_client_spawn_uses_recovered_loadout_and_rr_helpers
  tests/test_game_helper_seam_parity.py::test_red_rover_helpers_match_recovered_retail_boundaries
  tests/test_game_round_controller_helper_parity.py::test_red_rover_controller_readback_helpers_match_retail_mapping_surface
  -q --tb=short` passed: `7 passed`.
- `python -m pytest
  tests/test_cgame_event_transport_parity.py::test_last_alive_shared_helper_emits_retail_last_standing_sound
  -q --tb=short` passed: `1 passed`.

### Task A79: Reconstruct retail qagame direct client-command tranche [COMPLETED]
Priority: High
Primary areas: `src/code/game/g_cmds.c`, `src/code/game/g_local.h`,
`tests/test_game_helper_seam_parity.py`,
`docs/reverse-engineering/qagame-client-command-reconstruction-2026-05-25.md`,
`references/hlil/quakelive/qagamex86.dll/qagamex86.dll.bndb_hlil_split/`
Parity estimate: **before 42% -> after 89%** for the scoped ten-command
direct client-command surface (`players`, `timeout`, `timein`, `allready`,
`pause`, `unpause`, `lock`, `unlock`, `putteam`, and `opsay`) plus the related
`?` help-table wiring. The repo-wide parity estimate remains **98%** while
other command-table rows and compatibility-only surfaces remain separate
focused tasks.

Completed work:

1. Rechecked the `qagamex86.dll` metadata/import/export corpus, the symbol map,
   and the HLIL direct command table at `data_10080750`.
2. Replaced the single-entry direct `opsay` dispatcher with a shared retail-like
   direct command table, privilege floor checks, and help filtering.
3. Rebuilt `/players` around the retail `%2d %llu %c %s` row format, cached
   SteamID64 values, and the recovered `" MA*"` privilege marker map.
4. Added the shared direct-command state gate, PlayerID parser, and team-token
   parser with the exact recovered rejection strings.
5. Added the per-team lock latch used by `lock`, `unlock`, and
   `G_TeamJoinAllowed` while preserving `g_teamSpawnAsSpec` as a compatibility
   guard.
6. Reworked `allready`, `putteam`, `lock`, `unlock`, timeout, pause, timein,
   and opsay wiring so the selected tranche follows the recovered table and
   helper boundaries.
7. Added a dedicated reconstruction note and expanded the helper seam parity
   tests for the selected table rows, helper names, HLIL strings, and source
   wiring.

Verification:

- `python -m pytest
  tests/test_game_helper_seam_parity.py::test_game_direct_command_table_reconstructs_retail_client_command_tranche
  tests/test_game_helper_seam_parity.py::test_team_join_guard_and_connect_broadcast_match_retail_flow
  tests/test_game_helper_seam_parity.py::test_timeout_race_and_direct_command_helpers_match_recovered_boundaries
  -q --tb=short` passed: `3 passed`.

### Task A78: Restore retail parity for Red Rover infection `g_*` CVar tranche [COMPLETED]
Priority: High
Primary areas: `src/code/game/g_main.c`, `src/code/game/g_client.c`,
`src/code/game/g_active.c`, `src/code/game/g_cmds.c`,
`src/code/game/g_team.c`, `tests/test_game_active_pmove_wiring_parity.py`,
`tests/test_game_round_controller_helper_parity.py`,
`tests/test_game_helper_seam_parity.py`,
`tests/test_cgame_event_transport_parity.py`, `docs/gameplay/cvars.md`,
`references/hlil/quakelive/qagamex86.dll/qagamex86.dll.bndb_hlil_split/`
Parity estimate: **before 46% -> after 100%** for the scoped ten-CVar Red
Rover infection registration/default/wiring surface. Defaults were mostly
present but one literal default differed and all selected rows had legacy
archive/norestart flag surfaces instead of retail gamerule/latch surfaces. The
repo-wide parity estimate remains **98%** while remaining `g_*` rows continue
to be audited in focused batches.

Completed work:

1. Rechecked retail qagame HLIL rows, defaults, and registration flags for
   `g_rrAllowNegativeScores`, `g_rrDamageScoreBonus`, `g_rrInfected`,
   `g_rrInfectedSpreadTime`, `g_rrInfectedSpreadWarningTime`,
   `g_rrInfectedSurvivorMinSpeed`, `g_rrInfectedSurvivorPingRate`,
   `g_rrInfectedSurvivorScoreBonus`,
   `g_rrInfectedSurvivorScoreMethod`, and
   `g_rrInfectedSurvivorScoreRate`.
2. Corrected the nine infection scoring/spread/survivor rows to
   `CVAR_GAMERULE` and corrected `g_rrInfected` to the retail
   `CVAR_LATCH | GAME_CVAR_FLAG_RETAIL_40000 | CVAR_GAMERULE` surface.
3. Corrected `g_rrInfectedSurvivorMinSpeed` to the retail literal default
   `500.0f`.
4. Revalidated functional wiring through negative-score clamping,
   damage-based survivor scoring, survival bonus cadence, infection spread and
   warning timers, survivor slow-movement pings, ping-rate configstrings,
   custom-settings export, infected autojoin routing, infection seeding, round
   completion, death conversion, and last-alive notification paths.
5. Added HLIL-backed parity sentinels and updated gameplay cvar notes for the
   audited Red Rover infection controls.

Verification:

- `python -m pytest tests/test_game_active_pmove_wiring_parity.py -q
  --tb=short` passed: `22 passed`.
- `python -m pytest
  tests/test_game_round_controller_helper_parity.py::test_red_rover_controller_readback_helpers_match_retail_mapping_surface
  tests/test_game_round_controller_helper_parity.py::test_red_rover_autojoin_helper_routes_team_selection
  tests/test_game_helper_seam_parity.py::test_client_spawn_uses_recovered_loadout_and_rr_helpers
  tests/test_game_helper_seam_parity.py::test_client_begin_and_respawn_dispatch_freeze_and_rr_like_retail
  tests/test_game_helper_seam_parity.py::test_red_rover_helpers_match_recovered_retail_boundaries
  tests/test_cgame_event_transport_parity.py::test_qagame_infected_event_uses_retail_recipient_slot
  tests/test_cgame_event_transport_parity.py::test_red_rover_survival_bonus_emits_retail_global_team_sound
  -q --tb=short` passed: `7 passed`.

### Task A77: Restore retail parity for round and Freeze timing `g_*` CVar tranche [COMPLETED]
Priority: High
Primary areas: `src/code/game/g_main.c`, `src/code/game/g_active.c`,
`src/code/game/g_client.c`, `src/code/game/g_freeze.c`,
`src/code/game/g_combat.c`, `tests/test_game_active_pmove_wiring_parity.py`,
`tests/test_freeze_cvars.py`, `tests/test_game_round_controller_helper_parity.py`,
`docs/gameplay/cvars.md`,
`references/hlil/quakelive/qagamex86.dll/qagamex86.dll.bndb_hlil_split/`
Parity estimate: **before 58% -> after 100%** for the scoped ten-CVar
round draw, Freeze warmup, thaw, protection, environmental respawn, and
auto-thaw registration/default/wiring surface. The repo-wide parity estimate
remains **98%** while remaining `g_*` rows continue to be audited in focused
batches.

Completed work:

1. Rechecked retail qagame HLIL rows, defaults, and registration flags for
   `g_roundWarmupDelay`, `g_roundDrawLivingCount`,
   `g_roundDrawHealthCount`, `g_freezeThawTime`, `g_freezeThawTick`,
   `g_freezeThawRadius`, `g_freezeRoundDelay`,
   `g_freezeProtectedSpawnTime`, `g_freezeEnvironmentalRespawnDelay`, and
   `g_freezeAutoThawTime`.
2. Corrected registration flags: draw gates and most Freeze timing rows now
   carry `CVAR_GAMERULE`, while `g_roundWarmupDelay` and
   `g_freezeRoundDelay` now match the retail
   `CVAR_SERVERINFO | CVAR_GAMERULE` surface.
3. Corrected recovered retail defaults: `g_freezeThawTick` is now `1`,
   `g_freezeProtectedSpawnTime` is now `0`,
   `g_freezeEnvironmentalRespawnDelay` is now `5000`, and
   `g_freezeAutoThawTime` is now `120000`.
4. Revalidated functionality through CA/FZ draw resolution, end-round living
   and health prints, warmup-delay rescheduling, Freeze config caching, thaw
   radius and tick accumulation, post-round delay, post-thaw protection,
   environmental respawn release, and auto-thaw deadlines.
5. Added HLIL-backed parity sentinels and updated gameplay cvar notes for the
   audited round and Freeze timing controls.

Verification:

- `python -m pytest tests/test_game_active_pmove_wiring_parity.py -q
  --tb=short` passed: `20 passed`.
- `python -m pytest tests/test_game_active_pmove_wiring_parity.py
  tests/test_freeze_cvars.py tests/test_game_round_controller_helper_parity.py
  tests/test_game_runframe_parity.py -q --tb=short` passed: `34 passed`.
- A broader adjacent sweep that also included
  `tests/test_game_exit_rules_parity.py` still exposes the unrelated existing
  `ExitLevel` mapname sentinel mismatch outside this tranche; the touched
  round/Freeze timing surface is covered by the passing focused and adjacent
  suites above.

### Task A76: Restore retail parity for player-appearance, lag rewind, and instagib `g_*` CVar tranche [COMPLETED]
Priority: High
Primary areas: `src/code/game/g_main.c`, `src/code/game/g_active.c`,
`src/code/game/g_client.c`, `src/code/game/g_pmove.c`,
`src/code/game/g_weapon.c`, `tests/test_game_active_pmove_wiring_parity.py`,
`tests/test_cgame_displaycontext_parity.py`, `docs/gameplay/cvars.md`,
`references/hlil/quakelive/qagamex86.dll/qagamex86.dll.bndb_hlil_split/`
Parity estimate: **before 72% -> after 100%** for the scoped ten-CVar
player-appearance, lag rewind, and instagib registration/default/wiring
surface. The repo-wide parity estimate remains **98%** while remaining `g_*`
rows continue to be audited in focused batches.

Completed work:

1. Rechecked retail qagame HLIL rows, defaults, and registration flags for
   `g_allowCustomHeadmodels`, `g_playerCylinders`,
   `g_playerheadmodelOverride`, `g_playerheadScale`,
   `g_playerheadScaleOffset`, `g_playermodelOverride`,
   `g_playerModelScale`, `g_lagHaxHistory`, `g_lagHaxMs`, and
   `g_instaGib`.
2. Added the recovered `0x00010000` game cvar flag alias and corrected the
   seven player-appearance rows so they match retail: six
   `0x00010000 | CVAR_GAMERULE` rows and the dedicated
   `g_playerCylinders` `CVAR_GAMERULE` row.
3. Corrected `g_lagHaxHistory` and `g_lagHaxMs` to retail `CVAR_LATCH`
   rows while preserving the recovered `4` and `80` defaults.
4. Corrected `g_instaGib` to the retail
   `CVAR_SERVERINFO | 0x00040000 | CVAR_GAMERULE` registration surface.
5. Revalidated functional wiring through player-cylinder and
   player-appearance configstrings, forced model/head userinfo rewrites,
   admin config caching, lag rewind allocation/store/shift/restore, weapon
   hitscan rewind bracketing, pmove instagib no-player-clip caching, factory
   reset, custom-settings, and rank payload export.
6. Added HLIL-backed parity sentinels and updated gameplay cvar notes for the
   audited player-appearance, lag rewind, and instagib controls.

Verification:

- `python -m pytest tests/test_game_active_pmove_wiring_parity.py -q
  --tb=short` passed: `18 passed`.
- `python -m pytest
  tests/test_cgame_displaycontext_parity.py::test_game_cvar_transport_redundancy_stays_off_serverinfo_slabs
  tests/test_cgame_displaycontext_parity.py::test_cgame_player_cylinders_configstring_retains_direct_retail_parser_boundary
  tests/test_cgame_displaycontext_parity.py::test_cgame_player_appearance_configstring_reconstruction_uses_retail_parser_and_head_gate
  -q --tb=short` passed: `3 passed`.
- `python -m pytest tests/test_game_active_pmove_wiring_parity.py
  tests/test_cgame_displaycontext_parity.py::test_game_cvar_transport_redundancy_stays_off_serverinfo_slabs
  tests/test_cgame_displaycontext_parity.py::test_cgame_player_cylinders_configstring_retains_direct_retail_parser_boundary
  tests/test_cgame_displaycontext_parity.py::test_cgame_player_appearance_configstring_reconstruction_uses_retail_parser_and_head_gate
  tests/test_engine_netcode_parity.py tests/test_pmove_selected_cvar_parity.py
  tests/test_game_factory_regen_parity.py -q --tb=short` passed:
  `74 passed`.
- A broader `python -m pytest tests/test_engine_cvar_retail_parity.py -q
  --tb=short` sweep still exposes an unrelated existing Steamworks sentinel
  mismatch in `src/code/qcommon/common.c`; the touched `g_*` tranche is covered
  by the passing focused and adjacent suites above.

### Task A75: Restore retail parity for flag-physics and forced-override `g_*` CVar tranche [COMPLETED]
Priority: High
Primary areas: `src/code/game/g_main.c`, `src/code/game/g_local.h`,
`src/code/game/g_combat.c`, `src/code/game/g_team.c`,
`tests/test_game_active_pmove_wiring_parity.py`,
`docs/gameplay/cvars.md`,
`references/hlil/quakelive/qagamex86.dll/qagamex86.dll.bndb_hlil_split/`
Parity estimate: **before 54% -> after 100%** for the scoped ten-CVar
flag-physics, friendly-fire dampening, and forced-override registration/wiring
surface. The repo-wide parity estimate remains **98%** while remaining `g_*`
rows continue to be audited in focused batches.

Completed work:

1. Rechecked retail qagame HLIL rows, defaults, and registration flags for
   `g_flagBounce`, `g_flagPhysics`, `g_throwFlagVelocity`,
   `g_throwFlagForwardMult`, `g_tackleFlag`, `g_droppedFlagBonus`,
   `g_neutralFlagPingRate`, `g_friendlyFireDampen`,
   `g_forceDmgThroughSurface`, and `g_forceAtmosphericEffects`.
2. Corrected the flag cvar rows to retail defaults and flags, including
   `g_flagBounce` default `0.25`/`CVAR_GAMERULE`,
   `g_throwFlagForwardMult` default `2.5` with no flags,
   `g_droppedFlagBonus` default `1`/`CVAR_TEMP`, and the retail
   `g_neutralFlagPingRate` registration name/default/flag surface.
3. Added the missing `g_friendlyFireDampen` row and wired it into same-team
   damage when `g_friendlyFire` allows friendly hits.
4. Updated the flag config cache so the throw forward multiplier is stored as
   a float and both item drops and carried-flag tosses preserve classic
   behavior unless `g_flagPhysics` enables the retail physics path.
5. Revalidated forced override wiring for atmosphere and damage-through-surface
   configstring publication.

Verification:

- `python -m pytest tests/test_game_active_pmove_wiring_parity.py -q
  --tb=short` passed: `16 passed`.
- `python -m pytest tests/test_game_active_pmove_wiring_parity.py
  tests/test_game_callvote_option_parity.py tests/test_game_item_runframe_parity.py
  tests/test_game_target_parity.py tests/test_game_runframe_parity.py
  tests/test_game_native_export_helper_parity.py
  tests/test_game_visibility_queue_parity.py tests/test_engine_netcode_parity.py
  -q --tb=short` passed: `68 passed`.
- `git diff --check -- ...` reported no whitespace errors; Git only warned
  that touched text files will be normalized from LF to CRLF the next time Git
  writes them.

### Task A74: Restore retail parity for Domination and auto-shuffle `g_*` CVar tranche [COMPLETED]
Priority: High
Primary areas: `src/code/game/g_main.c`, `src/code/game/g_team.c`,
`tests/test_game_active_pmove_wiring_parity.py`,
`docs/gameplay/cvars.md`,
`references/hlil/quakelive/qagamex86.dll/qagamex86.dll.bndb_hlil_split/`
Parity estimate: **before 38% -> after 100%** for the scoped ten-CVar
Domination and auto-shuffle registration/wiring surface. The repo-wide parity
estimate remains **98%** while remaining `g_*` rows continue to be audited in
focused batches.

Completed work:

1. Rechecked retail qagame HLIL rows, defaults, and registration flags for
   `g_domCapTime`, `g_domTeammateCapScale`, `g_domDistressThreshold`,
   `g_domEnableContention`, `g_domNeutralFlag`, `g_domScoreRate`,
   `g_shuffle_timedelay`, `g_shuffle_minplayers`,
   `g_shuffle_automatic`, and `g_shuffle_automatic_minplayers`.
2. Corrected the six Domination rows from legacy archived controls to retail
   `CVAR_GAMERULE` rows while preserving the recovered defaults.
3. Corrected the four auto-shuffle rows to retail zero-flag rows, including
   `g_shuffle_timedelay` default `5000`, `g_shuffle_minplayers` default `3`,
   `g_shuffle_automatic` default `0`, and
   `g_shuffle_automatic_minplayers` default `6`.
4. Corrected `Team_UpdateAutoShuffleState` so `g_shuffle_timedelay` is treated
   as milliseconds and passed directly into `G_AutoShuffleCountdown_Arm`,
   while log/UI announcements round the millisecond value up to seconds.
5. Revalidated functional wiring through Domination capture/scoring cadence,
   teammate capture scaling, distress threshold, contention/neutralization
   rules, capture-time configstring publication, auto-shuffle threshold
   resolution, automatic shuffle gating, and countdown arming.
6. Added HLIL-backed parity sentinels and updated gameplay cvar notes for the
   audited Domination and auto-shuffle controls.

Verification:

- `python -m pytest tests/test_game_active_pmove_wiring_parity.py -q
  --tb=short` passed: `14 passed`.
- `python -m pytest tests/test_game_active_pmove_wiring_parity.py
  tests/test_auto_shuffle_countdown.py tests/test_clanarena_shuffle.py
  tests/test_match_state_configstring.py tests/test_game_runframe_parity.py
  tests/test_cgame_domination_count_parity.py
  tests/test_game_callvote_option_parity.py
  tests/test_game_module_retail_parity_gate.py -q --tb=short` passed:
  `37 passed, 6 skipped`.
- `python -m pytest
  tests/test_game_helper_seam_parity.py::test_team_balance_helper_is_split_out_for_setteam_and_readyup
  tests/test_game_helper_seam_parity.py::test_input_spawn_and_host_map_paths_keep_retail_factory_gates
  tests/test_game_helper_seam_parity.py::test_custom_settings_cvar_helper_matches_recovered_boundary
  -q --tb=short` passed: `3 passed`.
- A broader adjacent sweep that included all of
  `tests/test_game_helper_seam_parity.py` still exposes an unrelated existing
  `G_Say` token sentinel mismatch outside this tranche.

### Task A73: Restore retail parity for match-flow/warmup/timeout `g_*` CVar tranche [COMPLETED]
Priority: High
Primary areas: `src/code/game/g_main.c`, `src/code/game/g_client.c`,
`src/code/game/g_combat.c`, `src/code/game/g_gametype_lifecycle.inc`,
`src/code/game/g_mem.c`, `src/code/game/g_spawn.c`,
`src/code/game/g_team.c`, `src/game/g_match_config.c`,
`tests/test_game_active_pmove_wiring_parity.py`,
`docs/gameplay/cvars.md`,
`references/hlil/quakelive/qagamex86.dll/qagamex86.dll.bndb_hlil_split/`
Parity estimate: **before 55% -> after 100%** for the scoped ten-CVar
match-state, friendly-fire, debug-allocation, spawn-grant, warmup, ready-delay,
and timeout registration/wiring surface. The repo-wide parity estimate remains
**98%** while remaining `g_*` rows continue to be audited in focused batches.

Completed work:

1. Rechecked retail qagame HLIL rows, defaults, and registration flags for
   `g_gameState`, `g_friendlyFire`, `g_debugAlloc`,
   `g_grantItemOnSpawn`, `g_doWarmup`, `g_warmup`,
   `g_warmupReadyDelay`, `g_warmupReadyDelayAction`,
   `g_timeoutCount`, and `g_timeoutLen`.
2. Corrected `g_friendlyFire` and `g_grantItemOnSpawn` to retail
   `CVAR_GAMERULE` rows.
3. Corrected warmup/ready-delay rows: `g_warmup` now defaults to retail `10`,
   `g_doWarmup` now carries `CVAR_ARCHIVE`, and both ready-delay controls are
   zero-flag rows.
4. Corrected timeout rows: `g_timeoutLen` now carries `CVAR_GAMERULE`, and
   `g_timeoutCount` now defaults to `0` with
   `CVAR_SERVERINFO | CVAR_GAMERULE`.
5. Revalidated behavior/wiring through game-state publication, friendly-fire
   damage gates, debug allocation prints, spawn grant scripts, warmup
   countdowns, duel ready-delay actions, match-config timeout loading, timeout
   pool refills, and match-state configstring publication.
6. Added HLIL-backed parity sentinels and documented the audited match-flow,
   warmup, timeout, and spawn-grant controls for server operators.

Verification:

- `python -m pytest tests/test_game_active_pmove_wiring_parity.py -q
  --tb=short` passed: `12 passed`.
- `python -m pytest tests/test_game_active_pmove_wiring_parity.py
  tests/test_game_duel_ready_delay_parity.py tests/test_gametype_lifecycle.py
  tests/test_match_state_configstring.py tests/test_match_sim_harness.py
  tests/test_game_helper_seam_parity.py tests/test_game_callvote_option_parity.py
  tests/test_spawn_spec_cvars.py tests/test_game_module_retail_parity_gate.py
  -q --tb=short` passed: `81 passed, 8 skipped`.

### Task A72: Restore retail parity for server access/factory match `g_*` CVar tranche [COMPLETED]
Priority: High
Primary areas: `src/code/game/g_main.c`, `src/code/game/g_utils.c`,
`src/code/game/g_factory.c`, `src/code/game/g_svcmds.c`,
`src/code/game/g_client.c`, `src/game/g_match_config.c`,
`tests/test_game_active_pmove_wiring_parity.py`,
`docs/gameplay/cvars.md`,
`references/hlil/quakelive/qagamex86.dll/qagamex86.dll.bndb_hlil_split/`
Parity estimate: **before 64% -> after 100%** for the scoped ten-CVar
server access, ban/filter, factory selection, overtime/mercy, automatic
action, and malformed-userinfo registration and wiring surface. The repo-wide
parity estimate remains **98%** while remaining `g_*` rows continue to be
audited in focused batches.

Completed work:

1. Rechecked retail qagame HLIL rows, defaults, and registration flags for
   `g_password`, `g_needpass`, `g_banIPs`, `g_filterBan`, `g_factory`,
   `g_factoryTitle`, `g_overtime`, `g_mercytime`, `g_autoAction`, and
   `g_kickBadUserinfo`.
2. Corrected registration surfaces: `g_factory` is now the retail
   `CVAR_SERVERINFO | CVAR_ROM` row, `g_overtime` is
   `CVAR_SERVERINFO | CVAR_GAMERULE`, `g_mercytime` is
   `CVAR_NORESTART | CVAR_GAMERULE`, `g_autoAction` defaults to `0` with
   zero flags, and `g_kickBadUserinfo` now carries zero flags.
3. Preserved the already-matching retail rows for password/needpass,
   ban/filter, and factory title while tightening indentation around the
   audited rows.
4. Revalidated runtime wiring through password-to-needpass mirroring, IP ban
   and filter decisions, factory selection/title application, match overtime
   config loading, mercy-rule timing, malformed-userinfo kick/fallback
   handling, and `g_autoAction` parsing.
5. Added HLIL-backed parity sentinels and documented the audited server
   access/factory/match-flow controls for server operators.

Verification:

- `python -m pytest tests/test_game_active_pmove_wiring_parity.py -q
  --tb=short` passed: `10 passed`.
- `python -m pytest tests/test_game_active_pmove_wiring_parity.py
  tests/test_game_factory_regen_parity.py tests/test_game_helper_seam_parity.py
  tests/test_game_attack_defend_parity.py
  tests/test_game_round_controller_helper_parity.py
  tests/test_engine_netcode_parity.py
  tests/test_game_module_retail_parity_gate.py -q --tb=short` passed:
  `81 passed, 1 skipped`.
- `python -m pytest tests/test_match_state_configstring.py
  tests/test_match_sim_harness.py -q --tb=short` passed:
  `19 passed, 7 skipped`.
- A broader adjacent sweep that also included
  `tests/test_game_exit_rules_parity.py` still exposes an unrelated existing
  `ExitLevel` sentinel mismatch: the source reads `SERVERINFO_KEY_MAPNAME`
  while the test expects the literal `"mapname"` string.

### Task A71: Restore retail parity for Team Arena environment `g_*` CVar tranche [COMPLETED]
Priority: High
Primary areas: `src/code/game/g_main.c`, `src/code/cgame/cg_main.c`,
`src/code/game/g_arenas.c`, `src/code/game/g_team.c`,
`src/code/game/g_combat.c`, `src/code/game/g_spawn.c`,
`tests/test_game_active_pmove_wiring_parity.py`,
`docs/gameplay/cvars.md`,
`references/hlil/quakelive/qagamex86.dll/qagamex86.dll.bndb_hlil_split/`,
`references/hlil/quakelive/cgamex86.dll/cgamex86.dll_hlil_split/`
Parity estimate: **before 46% -> after 100%** for the scoped ten-CVar
Team Arena environment, podium, Obelisk/Cube, MOTD, and dust registration
surface. The repo-wide parity estimate remains **98%** while remaining
`g_*` rows continue to be audited in focused batches.

Completed work:

1. Rechecked retail qagame HLIL rows, defaults, and registration flags for
   `g_allTalk`, `g_motd`, `g_podiumDist`, `g_podiumDrop`,
   `g_obeliskHealth`, `g_obeliskRegenAmount`, `g_obeliskRegenPeriod`,
   `g_obeliskRespawnDelay`, `g_cubeTimeout`, and `g_enableDust`.
2. Corrected qagame registration flags: `g_allTalk`, `g_motd`, and
   `g_enableDust` are plain zero-flag rows; podium, Obelisk, and Cube timing
   rows now carry `CVAR_GAMERULE` instead of legacy zero/serverinfo/archive
   surfaces.
3. Corrected the cgame mirror for `g_obeliskRespawnDelay` to the retail
   zero-flag row while preserving cgame's retail `CVAR_SERVERINFO` mirror for
   `g_enableDust`.
4. Revalidated behavior/wiring through all-talk chat gating, MOTD publication,
   podium placement, Obelisk health/regen/respawn timing, Harvester cube
   timeout, worldspawn dust key handling, and cgame dust/effect consumers.
5. Added focused HLIL-backed parity sentinels and documented the audited Team
   Arena environment controls for server operators.

Verification:

- `python -m pytest tests/test_game_active_pmove_wiring_parity.py -q
  --tb=short` passed: `8 passed`.
- `python -m pytest tests/test_game_active_pmove_wiring_parity.py
  tests/test_game_factory_regen_parity.py tests/test_game_weapon_parity.py
  tests/test_game_battlesuit_parity.py tests/test_engine_netcode_parity.py
  tests/test_game_module_retail_parity_gate.py -q --tb=short` passed:
  `85 passed, 1 skipped`.
- `python -m pytest tests/test_cgame_hud_parity.py
  tests/test_engine_netcode_parity.py -q --tb=short` passed:
  `47 passed`.
- Broader dirty-tree sweeps that included unrelated cgame display/impact and
  Steam platform cvar tests still expose pre-existing failures outside this
  tranche; the touched CVar surfaces above are covered by the passing focused
  and adjacent suites.
- `git diff --check -- ...` reported no whitespace errors; Git only warned
  that touched text files will be normalized from LF to CRLF the next time Git
  writes them.

### Task A70: Restore retail parity for classic gameplay/admin `g_*` CVar tranche [COMPLETED]
Priority: High
Primary areas: `src/code/game/g_main.c`, `src/code/game/g_active.c`,
`src/code/game/g_local.h`, `tests/test_game_active_pmove_wiring_parity.py`,
`docs/gameplay/cvars.md`,
`references/hlil/quakelive/qagamex86.dll/qagamex86.dll.bndb_hlil_split/`
Parity estimate: **before 74% -> after 100%** for the scoped ten-CVar
classic gameplay/admin registration and inactivity-wiring surface. The
repo-wide parity estimate remains **98%** while remaining `g_*` rows continue
to be audited in focused batches.

Completed work:

1. Rechecked retail qagame HLIL rows, defaults, and registration flags for
   `g_speed`, `g_gravity`, `g_weaponRespawn`, `g_inactivity`,
   `g_inactivityWarning`, `g_dropInactive`, `g_debugMove`, `g_debugDamage`,
   `g_teamAutoJoin`, and `g_teamForceBalance`.
2. Corrected registration flags for `g_speed`, `g_gravity`,
   `g_weaponRespawn`, and `g_teamForceBalance` so the source rows match the
   retail serverinfo/archive/gamerule bits recovered from HLIL.
3. Restored the retail `g_inactivityWarning` row with default `10`, exported
   the cvar to game code, and replaced the hardcoded ten-second warning path
   with the retail cvar-driven threshold and pluralized centerprint text.
4. Wired `g_dropInactive` into `ClientInactivityTimer`: timed-out inactive
   clients are moved to spectator when the cvar is disabled, and are dropped
   only when it is enabled, matching the retail branch.
5. Added the retail-style inactivity warning reset latch for `g_inactivity`
   changes, and revalidated existing wiring for debug movement/damage,
   team autojoin/force-balance, speed, gravity, and weapon-respawn behavior.
6. Added focused HLIL-backed parity sentinels and documented the audited
   classic gameplay/admin controls for server operators.

Verification:

- `python -m pytest tests/test_game_active_pmove_wiring_parity.py -q
  --tb=short` passed: `6 passed`.
- `python -m pytest tests/test_game_active_pmove_wiring_parity.py
  tests/test_game_helper_seam_parity.py tests/test_game_factory_regen_parity.py
  tests/test_game_weapon_parity.py tests/test_cvar_alias_console.py
  tests/test_engine_netcode_parity.py tests/test_game_module_retail_parity_gate.py
  -q --tb=short` passed: `103 passed, 1 skipped`.
- `git diff --check -- ...` reported no whitespace errors; Git only warned
  that touched text files will be normalized from LF to CRLF the next time Git
  writes them.

### Task A69: Restore retail parity for second weapon-special `g_*` CVar tranche [COMPLETED]
Priority: High
Primary areas: `src/code/game/g_main.c`, `src/code/game/g_missile.c`,
`src/code/game/g_pmove.c`, `src/code/game/bg_pmove.c`,
`src/code/game/bg_public.h`, `src/code/game/g_local.h`,
`src/code/cgame/cg_servercmds.c`, `src/game/g_config.c`,
`tests/test_game_weapon_parity.py`, `tests/test_game_factory_regen_parity.py`,
`docs/gameplay/cvars.md`,
`references/hlil/quakelive/qagamex86.dll/qagamex86.dll.bndb_hlil_split/`
Parity estimate: **before 59% -> after 100%** for the scoped ten-CVar
weapon-special, Quad Hog, and prox-mine registration/wiring surface. The
repo-wide parity estimate remains **98%** while remaining `g_*` rows continue
to be audited in focused batches.

Completed work:

1. Rechecked retail qagame HLIL rows and string/default storage for
   `g_midAirMinHeight`, `g_nailspeed`, `g_nailspread`, `g_damagePlums`,
   `g_quadDamageFactor`, `g_quadHog`, `g_quadHogIdle`,
   `g_quadHogPingRate`, `g_quadHogTime`, and `g_proxMineTimeout`.
2. Corrected registration defaults and flags: midair height, damage plums,
   Quad Damage, Quad Hog timers, and prox mine timeout now match the retail
   table; Nailgun speed/spread and prox mine timeout now carry the recovered
   `0x00040000 | CVAR_GAMERULE` flag combination; Quad Hog now carries
   `CVAR_LATCH | 0x00040000 | CVAR_GAMERULE`.
3. Revalidated functional wiring through `G_InitWeaponConfig`,
   `G_IsMidAirEligibleTarget`, Nailgun projectile spread/speed sampling,
   Quad Damage scaling, server-settings publication, Quad Hog pickup/frame
   timers, pmove cache/compact payload mirroring, custom-settings masks, and
   proximity mine activation.
4. Corrected retail units: Quad Hog ping rate is milliseconds (`1500`) and is
   no longer multiplied by `1000`, while Quad Hog time/idle and prox mine
   timeout remain seconds-based and are converted at the timer boundary.
5. Added focused HLIL-backed parity sentinels and documented the audited
   controls for server operators.

Verification:

- `python -m pytest tests/test_game_weapon_parity.py -q --tb=short` passed:
  `33 passed`.
- `python -m pytest tests/test_game_weapon_parity.py
  tests/test_game_factory_regen_parity.py tests/test_game_ammopack_parity.py
  tests/test_cvar_console_write_parity.py
  tests/test_game_module_retail_parity_gate.py
  tests/test_pmove_selected_cvar_parity.py -q --tb=short` passed:
  `82 passed, 1 skipped`.
- `python -m pytest tests/test_pmove_helper_parity.py -q --tb=short` passed:
  `38 passed`.
- `git diff --check -- ...` reported no whitespace errors; Git only warned
  that touched text files will be normalized from LF to CRLF the next time Git
  writes them.

### Task A68: Restore retail parity for first weapon-special `g_*` CVar tranche [COMPLETED]
Priority: High
Primary areas: `src/code/game/g_main.c`, `src/code/game/g_missile.c`,
`src/code/game/g_weapon.c`, `src/code/game/g_pmove.c`,
`tests/test_game_weapon_parity.py`, `tests/test_game_factory_regen_parity.py`,
`docs/gameplay/cvars.md`,
`references/hlil/quakelive/qagamex86.dll/qagamex86.dll.bndb_hlil_split/`
Parity estimate: **before 64% -> after 100%** for the scoped ten-CVar
weapon-special registration and wiring surface. The repo-wide parity estimate
remains **98%** while remaining weapon-special and item/powerup cvar rows
continue to be audited in focused batches.

Completed work:

1. Rechecked retail qagame HLIL rows and string/default storage for
   `g_velocity_gh`, `g_guidedRocket`, `g_lightningDischarge`,
   `g_railJump`, `g_gauntletSpeedFactor`, `g_headShotDamage_rg`,
   `g_ironsights_mg`, `g_nailbounce`, `g_nailbouncepercentage`, and
   `g_nailcount`.
2. Corrected registration flags: grapple velocity, lightning discharge, rail
   jump, rail headshot damage, and the three audited Nailgun rows now use
   `0x00040000 | CVAR_GAMERULE`; guided rockets and gauntlet speed factor now
   use `CVAR_GAMERULE`; machinegun ironsights now use retail
   `CVAR_TEMP | 0x00040000 | CVAR_GAMERULE`.
3. Revalidated functional wiring through `G_InitWeaponConfig`,
   `G_SynchronizeGrappleConfig`, guided rocket think arming,
   `G_ApplyRailJump`, lightning discharge activation,
   `G_PmoveCacheSettings`, Nailgun count/bounce spawn paths, custom-settings
   mask participation, `G_UpdateCvars`, and factory config refreshes.
4. Added focused HLIL-backed parity sentinels and documented the audited
   weapon-special controls for server operators.

Verification:

- `python -m pytest tests/test_game_weapon_parity.py -q --tb=short` passed:
  `31 passed`.
- `python -m pytest tests/test_game_weapon_parity.py
  tests/test_game_factory_regen_parity.py tests/test_game_ammopack_parity.py
  tests/test_cvar_console_write_parity.py
  tests/test_game_module_retail_parity_gate.py
  tests/test_pmove_selected_cvar_parity.py -q --tb=short` passed:
  `80 passed, 1 skipped`.

### Task A67: Restore retail parity for velocity/acceleration `g_*` CVar tranche [COMPLETED]
Priority: High
Primary areas: `src/code/game/g_main.c`, `src/code/game/g_missile.c`,
`src/game/g_config.c`, `tests/test_game_weapon_parity.py`,
`docs/gameplay/cvars.md`,
`references/hlil/quakelive/qagamex86.dll/qagamex86.dll.bndb_hlil_split/`
Parity estimate: **before 66% -> after 100%** for the scoped ten-CVar
projectile velocity/acceleration registration and wiring surface. The
repo-wide parity estimate remains **98%** while remaining weapon-special
cvar rows continue to be audited in focused batches.

Completed work:

1. Rechecked retail qagame HLIL rows and string/default storage for
   `g_accelFactor_bfg`, `g_accelFactor_pg`, `g_accelFactor_rl`,
   `g_accelRate_bfg`, `g_accelRate_pg`, `g_accelRate_rl`,
   `g_velocity_bfg`, `g_velocity_gl`, `g_velocity_pg`, and
   `g_velocity_rl`.
2. Corrected retail defaults and flags: acceleration factors now use default
   `1` plus `0x00040000 | CVAR_GAMERULE`; acceleration rates now use default
   `16` plus `CVAR_GAMERULE`; audited velocity rows now use the retail
   `1800`, `700`, `2000`, and `1000` defaults plus
   `0x00040000 | CVAR_GAMERULE`.
3. Revalidated functional wiring through `G_InitWeaponConfig`,
   `G_SynchronizeRocketConfig`, the rocket/plasma/BFG acceleration think
   callbacks, `G_GetMissileAccelerationThinkTime`, grenade/plasma/rocket/BFG
   projectile constructors, custom-settings mask participation,
   `G_UpdateCvars`, and factory config refreshes.
4. Added focused HLIL-backed parity sentinels and documented the audited
   projectile velocity/acceleration controls for server operators.

Verification:

- `python -m pytest tests/test_game_weapon_parity.py -q --tb=short` passed:
  `29 passed`.
- `python -m pytest tests/test_game_weapon_parity.py
  tests/test_game_factory_regen_parity.py tests/test_game_ammopack_parity.py
  tests/test_cvar_console_write_parity.py
  tests/test_game_module_retail_parity_gate.py
  tests/test_pmove_selected_cvar_parity.py -q --tb=short` passed:
  `78 passed, 1 skipped`.

### Task A66: Restore retail parity for splash radius/falloff `g_*` CVar tranche [COMPLETED]
Priority: High
Primary areas: `src/code/game/g_main.c`, `src/code/game/g_weapon.c`,
`src/code/game/g_missile.c`, `src/game/g_config.c`,
`tests/test_game_weapon_parity.py`, `docs/gameplay/cvars.md`,
`references/hlil/quakelive/qagamex86.dll/qagamex86.dll.bndb_hlil_split/`
Parity estimate: **before 68% -> after 100%** for the scoped ten-CVar
splash/radius/falloff registration and wiring surface. The repo-wide parity
estimate remains **98%** while adjacent velocity, acceleration, and remaining
weapon-special cvar rows continue to be audited in focused batches.

Completed work:

1. Rechecked retail qagame HLIL rows and string/default storage for
   `g_splashdamage_bfg`, `g_splashdamage_pl`, `g_splashradius_bfg`,
   `g_splashradius_gl`, `g_splashradius_pg`, `g_splashradius_pl`,
   `g_splashradius_rl`, `g_range_lg_falloff`, `g_range_sg_falloff`, and
   `g_rocketsplashOffset`.
2. Corrected registration names and flags: BFG/prox splash damage and all
   audited splash radius rows now use retail lowercase names and
   `0x00040000 | CVAR_GAMERULE`; falloff ranges and rocket splash offset now
   use `CVAR_GAMERULE`.
3. Corrected retail defaults: BFG splash radius is `80`, both falloff ranges
   are `768`, and `g_rocketsplashOffset` is `-10.0`.
4. Revalidated functional wiring through `G_InitWeaponConfig`, shotgun and
   lightning falloff helpers, grenade/plasma/rocket/BFG/prox missile spawn
   paths, rocket splash-origin offset handling, custom-settings mask
   participation, `G_UpdateCvars`, and factory config refreshes.

Verification:

- `python -m pytest tests/test_game_weapon_parity.py -q --tb=short` passed:
  `27 passed`.
- `python -m pytest tests/test_game_weapon_parity.py
  tests/test_game_factory_regen_parity.py tests/test_game_ammopack_parity.py
  tests/test_cvar_console_write_parity.py
  tests/test_game_module_retail_parity_gate.py
  tests/test_pmove_selected_cvar_parity.py -q --tb=short` passed:
  `76 passed, 1 skipped`.

### Task A65: Restore retail parity for second weapon damage `g_*` CVar tranche [COMPLETED]
Priority: High
Primary areas: `src/code/game/g_main.c`, `src/code/game/g_weapon.c`,
`src/code/game/g_missile.c`, `src/code/game/g_combat.c`,
`src/game/g_config.c`, `tests/test_game_weapon_parity.py`,
`docs/gameplay/cvars.md`,
`references/hlil/quakelive/qagamex86.dll/qagamex86.dll.bndb_hlil_split/`
Parity estimate: **before 70% -> after 100%** for the scoped ten-CVar
weapon damage/splash registration and wiring surface. The repo-wide parity
estimate remains **98%** while the remaining splash radius, BFG splash, and
weapon range/velocity cvar rows continue to be walked in focused batches.

Completed work:

1. Rechecked retail qagame HLIL rows and string/default storage for
   `g_damage_pg`, `g_damage_pl`, `g_damage_rg`, `g_damage_rl`,
   `g_damage_sg`, `g_damage_sg_falloff`, `g_damage_sg_outer`,
   `g_splashdamage_gl`, `g_splashdamage_pg`, and `g_splashdamage_rl`.
2. Corrected the seven remaining direct/shotgun damage rows to use the
   recovered `0x00040000 | CVAR_GAMERULE` pair via
   `GAME_CVAR_FLAG_RETAIL_40000`.
3. Corrected the audited splash damage registrations to retail lowercase cvar
   names (`g_splashdamage_*`) and retail flags, and changed rocket splash
   damage from the legacy `100` default to Quake Live's `84` default across
   registration, cache fallback, and custom-settings comparisons.
4. Revalidated functional wiring through `G_InitWeaponConfig`,
   `G_ClampModDamage`, shotgun/rail weapon paths, grenade/plasma/rocket/prox
   missile spawn paths, custom-settings mask participation, `G_UpdateCvars`,
   and factory config refreshes.

Verification:

- `python -m pytest tests/test_game_weapon_parity.py -q --tb=short` passed:
  `25 passed`.
- `python -m pytest tests/test_game_weapon_parity.py
  tests/test_game_factory_regen_parity.py tests/test_game_ammopack_parity.py
  tests/test_cvar_console_write_parity.py
  tests/test_game_module_retail_parity_gate.py
  tests/test_pmove_selected_cvar_parity.py -q --tb=short` passed:
  `74 passed, 1 skipped`.

### Task A64: Restore retail parity for first ten weapon damage `g_*` CVars [COMPLETED]
Priority: High
Primary areas: `src/code/game/g_main.c`, `src/code/game/g_weapon.c`,
`src/code/game/g_missile.c`, `src/code/game/g_combat.c`,
`src/game/g_config.c`, `tests/test_game_weapon_parity.py`,
`docs/gameplay/cvars.md`,
`references/hlil/quakelive/qagamex86.dll/qagamex86.dll.bndb_hlil_split/`
Parity estimate: **before 72% -> after 100%** for the scoped ten-CVar
weapon damage registration and wiring surface. The repo-wide parity estimate
remains **98%** while the remaining weapon damage/splash/range cvar rows are
still being walked in focused batches.

Completed work:

1. Rechecked retail qagame HLIL rows and string/default storage for
   `g_damage_bfg`, `g_damage_cg`, `g_damage_g`, `g_damage_gh`,
   `g_damage_hmg`, `g_damage_gl`, `g_damage_lg`,
   `g_damage_lg_falloff`, `g_damage_mg`, and `g_damage_ng`.
2. Confirmed the retail default strings (`100`, `8`, `50`, `10`, `6`, `5`,
   `12`, and `0`) and corrected the ten registration flags to the recovered
   `0x00040000 | CVAR_GAMERULE` pair via `GAME_CVAR_FLAG_RETAIL_40000`.
3. Revalidated functional wiring through `G_InitWeaponConfig`,
   `G_ClampModDamage`, weapon and missile fire paths, custom-settings mask
   participation where retail exposes it, `G_UpdateCvars`, and factory config
   refreshes.
4. Added focused parity sentinels against the HLIL registration rows/default
   strings and documented the audited damage tranche for server operators.

Verification:

- `python -m pytest tests/test_game_weapon_parity.py -q --tb=short` passed:
  `23 passed`.
- `python -m pytest tests/test_game_weapon_parity.py
  tests/test_game_factory_regen_parity.py tests/test_game_ammopack_parity.py
  tests/test_cvar_console_write_parity.py
  tests/test_game_module_retail_parity_gate.py
  tests/test_pmove_selected_cvar_parity.py -q --tb=short` passed:
  `72 passed, 1 skipped`.

### Task A63: Restore retail parity for second knockback `g_*` CVar tranche [COMPLETED]
Priority: High
Primary areas: `src/code/game/g_main.c`, `src/game/g_config.c`,
`src/code/game/g_combat.c`, `tests/test_game_weapon_parity.py`,
`docs/gameplay/cvars.md`,
`references/hlil/quakelive/qagamex86.dll/qagamex86.dll.bndb_hlil_split/`
Parity estimate: **before 70% -> after 100%** for the scoped ten-CVar
knockback base/scalar surface. The repo-wide parity estimate remains **98%**
while adjacent weapon cvar families continue to be walked in focused batches.

Completed work:

1. Rechecked retail qagame HLIL rows and string/default storage for
   `g_knockback`, `g_knockback_bfg`, `g_knockback_gh`,
   `g_knockback_ng`, `g_knockback_pl`, `g_knockback_cg`,
   `g_knockback_hmg`, `g_knockback_z`, `g_knockback_z_self`, and
   `g_knockback_cripple`.
2. Corrected default spellings for the remaining weapon-specific scalars,
   vertical boosters, and cripple scalar to match retail byte strings:
   `1`, `-5`, `24`, and `0` instead of source-only float-suffixed forms.
3. Corrected flags: global `g_knockback`, `g_knockback_z`,
   `g_knockback_z_self`, and `g_knockback_cripple` now use
   `CVAR_GAMERULE`; BFG, grapple, nailgun, proximity launcher, chaingun, and
   heavy machinegun rows now use `CONFIG_CVAR_FLAG_RETAIL_40000 |
   CVAR_GAMERULE`.
4. Revalidated wiring through `G_InitKnockbackConfig`,
   `G_KnockbackScaleForMOD`, and the final `g_knockback.value` scaling in
   `G_Damage`; the later A90 pass removed the source-only vertical boost and
   cripple-velocity helpers after the retail `G_Damage` branch was remapped.

Verification:

- `python -m pytest tests/test_game_weapon_parity.py -q --tb=short` passed:
  `21 passed`.
- `python -m pytest tests/test_game_weapon_parity.py
  tests/test_game_factory_regen_parity.py tests/test_game_ammopack_parity.py
  tests/test_cvar_console_write_parity.py
  tests/test_game_module_retail_parity_gate.py
  tests/test_pmove_selected_cvar_parity.py -q --tb=short` passed:
  `70 passed, 1 skipped`.
- `git diff --check -- src/code/game/g_main.c src/game/g_config.c
  tests/test_game_weapon_parity.py docs/gameplay/cvars.md
  IMPLEMENTATION_PLAN.md` passed with only the repository's existing CRLF
  normalization warnings.

### Task A62: Restore retail parity for first ten weapon knockback `g_*` CVars [COMPLETED]
Priority: High
Primary areas: `src/game/g_config.c`, `src/code/game/g_combat.c`,
`tests/test_game_weapon_parity.py`, `tests/test_game_factory_regen_parity.py`,
`docs/gameplay/cvars.md`,
`references/hlil/quakelive/qagamex86.dll/qagamex86.dll.bndb_hlil_split/`
Parity estimate: **before 68% -> after 100%** for the scoped ten-CVar
weapon knockback registration and combat wiring surface. The repo-wide parity
estimate remains **98%** while adjacent weapon cvar families continue to be
walked in focused batches.

Completed work:

1. Rechecked retail qagame HLIL rows and string/default storage for
   `g_knockback_g`, `g_knockback_mg`, `g_knockback_sg`,
   `g_knockback_gl`, `g_knockback_rl`, `g_knockback_rl_self`,
   `g_knockback_lg`, `g_knockback_rg`, `g_knockback_pg`, and
   `g_knockback_pg_self`.
2. Corrected the registration default spellings to match retail byte strings:
   `1`, `1.10`, `0.90`, `1.75`, `0.85`, and `1.30` instead of
   source-only float-suffixed forms.
3. Corrected the ten registration flags from plain `0` to the recovered
   retail `0x00040000 | CVAR_GAMERULE` pair, and generalized the local helper
   to `CONFIG_CVAR_FLAG_RETAIL_40000` because the same bit also appears on
   non-spawn-item retail cvars.
4. Revalidated functional wiring through `G_InitKnockbackConfig`,
   `G_UpdateKnockbackConfig`, factory refreshes, `G_UpdateCvars`, and
   `G_KnockbackScaleForMOD` into `G_Damage`.

Verification:

- `python -m pytest tests/test_game_weapon_parity.py -q --tb=short` passed:
  `19 passed`.
- `python -m pytest tests/test_game_factory_regen_parity.py
  tests/test_game_ammopack_parity.py -q --tb=short` passed: `29 passed`.

### Task A61: Restore retail parity for factory item-spawn and respawn `g_*` CVars [COMPLETED]
Priority: High
Primary areas: `src/game/g_config.c`, `src/code/game/g_main.c`,
`src/code/game/g_items.c`, `src/code/game/g_vote.c`,
`tests/test_game_factory_regen_parity.py`,
`tests/test_game_ammopack_parity.py`, `docs/gameplay/cvars.md`,
`references/hlil/quakelive/qagamex86.dll/qagamex86.dll.bndb_hlil_split/`
Parity estimate: **before 72% -> after 100%** for the scoped ten-CVar
factory item-spawn/respawn surface. The repo-wide parity estimate remains
**98%** because this closes table-flag/default mismatches inside an already
mostly wired gameplay seam.

Completed work:

1. Rechecked retail qagame HLIL registration rows and string/default storage
   for `g_ammoPack`, `g_ammoPackHack`, `g_ammoRespawn`,
   `g_powerupRespawn`, `g_spawnItemPowerup`, `g_spawnItemHoldable`,
   `g_spawnItemWeapons`, `g_spawnItemHealth`, `g_spawnItemArmor`, and
   `g_spawnItemAmmo`.
2. Corrected the local registration flags: ammo-pack toggles now use
   `CVAR_LATCH | CVAR_GAMERULE`, ammo/powerup respawn timers use
   `CVAR_GAMERULE`, and the six `g_spawnItem*` cvars use the recovered
   `0x00040000 | CVAR_GAMERULE` retail bit pair via
   `CONFIG_CVAR_FLAG_RETAIL_40000`.
3. Revalidated functional wiring through the factory cvar cache, item spawn
   gating, global-versus-weapon ammo family switching, ammo/powerup respawn
   timing, and loadout ammo vote toggles.
4. Added focused parity sentinels against the HLIL table rows/default strings
   and updated the stale ammo-pack parity expectation that still pinned the
   pre-fix archive flags.

Verification:

- `python -m pytest tests/test_game_factory_regen_parity.py -q --tb=short`
  passed: `25 passed`.
- `python -m pytest tests/test_game_factory_regen_parity.py
  tests/test_game_ammopack_parity.py tests/test_bg_misc_validation_fixtures.py
  tests/test_bg_misc_helper_parity.py tests/test_bg_itemlist_indexes.py
  tests/test_bg_itemlist_retail_metadata.py tests/test_game_weapon_parity.py
  tests/test_cvar_console_write_parity.py
  tests/test_game_module_retail_parity_gate.py -q --tb=short` passed:
  `101 passed, 1 skipped`.
- `git diff --check -- src/code/game/g_main.c src/game/g_config.c
  tests/test_game_factory_regen_parity.py tests/test_game_ammopack_parity.py
  docs/gameplay/cvars.md IMPLEMENTATION_PLAN.md` passed with only the
  repository's existing CRLF normalization warnings.

### Task A60: Resolve remaining source-visible `cl_*` cvar surfaces [COMPLETED]
Priority: Medium
Primary areas: `src/code/client/cl_main.c`, `src/code/client/client.h`,
`src/code/client/cl_console.c`, `src/code/macosx/Q3Controller.m`,
`tests/test_engine_cvar_retail_parity.py`, `docs/client_cvars.md`,
`references/hlil/quakelive/quakelive_steam.exe/quakelive_steam.exe_hlil_split/quakelive_steam.exe_hlil_part04.txt`,
`references/hlil/quakelive/quakelive_steam.exe/quakelive_steam.exe_hlil_split/quakelive_steam.exe_hlil_part06.txt`,
`references/reverse-engineering/ghidra/quakelive_steam/decompile_top_functions.c`
Parity estimate: **before 99% -> after 100%** for the remaining
source-visible `cl_*` cvar/name inventory. Repo-wide remains **98%** pending
the active compatibility-only and runtime-evidence gaps.

Completed work:

1. Rechecked the remaining source-visible names against the recovered retail
   `CL_Init` cvar slab, string table, dynamic connect path, and companion
   Ghidra corpus.
2. Kept `cl_currentServerAddress` as the retail dynamic-only connect cvar:
   `CL_Connect_f` sets it from the requested server string, and neither retail
   nor source registers it in `CL_Init`.
3. Folded `cl_matchmakingProvider`, `cl_matchmakingPolicy`,
   `cl_statsProvider`, `cl_statsPolicy`, `cl_socialOverlayProvider`, and
   `cl_socialOverlayPolicy` into the guarded service-disclosure contract:
   `CVAR_ROM` defaults, refresh through `CL_RefreshPlatformServiceCvars`, and
   explicit absence from the retail client cvar slab.
4. Removed the non-retail Quake III/PunkBuster/platform carryovers
   `cl_allowDownload`, `cl_contimestamps`, `cl_conXOffset`, `cl_guid`,
   `cl_noprint`, `cl_punkbuster`, and `cl_showBanner` from the checked source
   surface; console notify drawing now uses the recovered base x-adjust, and
   the legacy pak-compare fallback no longer exposes a client disable cvar.
5. Added focused regression coverage and refreshed `docs/client_cvars.md` with
   the final inventory classification.
6. Verification:
   `python -m pytest tests/test_engine_cvar_retail_parity.py::test_engine_cvar_thirtyninth_client_service_disclosure_tranche_matches_guarded_retail_divergence_contracts tests/test_engine_cvar_retail_parity.py::test_engine_cvar_fortieth_client_remaining_cl_surface_matches_resolved_retail_contracts -q --tb=short`
   -> `2 passed`;
   focused client `cl_*` parity sweep through the thirty-fourth to fortieth
   tranches -> `7 passed`;
   `python -m pytest tests/test_client_full_parity_gate.py -q --tb=short`
   -> `2 passed, 1 skipped`;
   `python -m pytest tests/test_cgame_console_surface_parity.py::test_voice_menu_timer_uses_retail_separate_latch -q --tb=short`
   -> `1 passed`;
   source/tracking inventory reports `REMAINING=0`;
   `git diff --check` on touched files passed with CRLF warnings only.

### Task A59: Re-audit retail `con_*` cvar parity [COMPLETED]
Priority: High
Primary areas: `src/code/client/cl_console.c`,
`tests/test_engine_cvar_retail_parity.py`,
`tests/test_cl_console_cgame_parity.py`,
`tests/test_engine_command_parity.py`,
`references/hlil/quakelive/quakelive_steam.exe/quakelive_steam.exe_hlil_split/quakelive_steam.exe_hlil_part04.txt`,
`references/hlil/quakelive/quakelive_steam.exe/quakelive_steam.exe_hlil_split/quakelive_steam.exe_hlil_part06.txt`
Parity estimate: **before 100% -> after 100%** for the scoped retail
`con_*` console cvar surface. No production source patch was required because
the checked-in registrations and consumers already matched the recovered
retail evidence.

Completed work:

1. Rechecked the engine-owned retail evidence for console cvars against
   `metadata.txt`, `imports.txt`, `exports.txt`, `functions.csv`,
   `analysis_symbols.txt`, and the Binary Ninja HLIL rows around `004b4a30`.
2. Confirmed the exhaustive Quake Live retail `con_*` set contains eight cvars,
   not ten: `con_background`, `con_height`, `con_matchlimit`, `con_noprint`,
   `con_opacity`, `con_scale`, `con_speed`, and `con_timestamps`.
3. Rejected the tempting Quake III carryovers as non-retail for Quake Live:
   `con_notifytime` is absent from the Quake Live HLIL, and `scr_conspeed` is
   replaced by the retail `con_speed` bounded cvar.
4. Added a focused regression guard that now proves the exact retail names,
   defaults, flags, bounded ranges, HLIL registration rows, and source wiring
   for every retail `con_*` cvar, including background selection, console
   height, find-match limit, print suppression, opacity, scale, scroll speed,
   and timestamp/cgame physics-time routing.
5. Verification:
   `python -m pytest tests/test_engine_cvar_retail_parity.py::test_console_cvar_surface_matches_retail_hlil tests/test_engine_cvar_retail_parity.py::test_console_cvar_functional_wiring_matches_retail_hlil_surface tests/test_engine_cvar_retail_parity.py::test_engine_cvar_second_tranche_matches_retail_contracts tests/test_engine_cvar_retail_parity.py::test_engine_cvar_sixth_client_tranche_matches_retail_contracts -q --tb=short`
   -> `4 passed`;
   `python -m pytest tests/test_cl_console_cgame_parity.py tests/test_engine_command_parity.py::test_console_and_alias_command_families_match_retail_wiring -q --tb=short`
   -> `10 passed`. A broader full-file sweep of
   `tests/test_engine_cvar_retail_parity.py` currently reports `49 passed, 3
   failed` in unrelated renderer/Steam cvar tranches.

### Task A58: Re-audit client/server usercmd movement transport [COMPLETED]
Priority: High
Primary areas: `src/code/client/cl_input.c`,
`src/code/client/cl_cgame.c`, `src/code/cgame/cg_predict.c`,
`src/code/cgame/cg_syscalls.c`, `src/code/qcommon/msg.c`,
`src/code/server/sv_client.c`, `src/code/server/sv_game.c`,
`tests/test_usercmd_movement_transport_parity.py`,
`docs/reverse-engineering/quakelive_steam_mapping_round_17.md`,
`docs/reverse-engineering/quakelive_steam_mapping_round_57.md`,
`docs/reverse-engineering/quakelive_steam_mapping_round_62.md`,
`docs/reverse-engineering/quakelive_steam_mapping_round_126.md`,
`docs/reverse-engineering/quakelive_steam_mapping_round_277.md`,
`references/analysis/quakelive_symbol_aliases.json`
Parity estimate: **before 100% -> after 100%** for the scoped usercmd
movement transport seam: client command creation, packet packing, keyed
qcommon deltas, server replay into qagame, and cgame prediction access to the
host command ring. No production source patch was required.

Completed work:

1. Rechecked the retained retail mappings for `CL_CreateCmd`,
   `CL_CreateNewCommands`, `CL_ReadyToSendPacket`, `CL_WritePacket`,
   `CL_SendCmd`, `MSG_WriteDeltaUsercmdKey`, `MSG_ReadDeltaUsercmdKey`,
   `SV_ClientThink`, `SV_UserMove`, `SV_ExecuteClientMessage`,
   `QLCGImport_GetCurrentCmdNumber`, and `QLCGImport_GetUserCmd`.
2. Added a focused end-to-end sentinel for the client command path, including
   final `weapon` / `weaponPrimary` / `fov` storage, `serverTime` and view-angle
   capture, primed command generation, packet throttle checks, `cl_packetdup`
   resend window, `clc_move` versus `clc_moveNoDelta`, checksum-feed keying,
   ordered `MSG_WriteDeltaUsercmdKey`, and `outPackets` bookkeeping.
3. Pinned the qcommon keyed usercmd delta pair against Quake Live extensions:
   `weaponPrimary` and `fov` now stay covered alongside the signed
   `forwardmove`, `rightmove`, and `upmove` bytes in both changed-field and
   copied-baseline read paths.
4. Added server replay coverage for `SV_UserMove` and `SV_ClientThink`,
   including delta-message selection, command-count guards, keyed decode,
   message-ack ping timestamping, pure-client gates, first-command
   `SV_ClientEnterWorld`, stale-command suppression, `lastUsercmd`, qagame
   `G_GET_USERCMD`, bot `BOTLIB_USER_COMMAND`, and `GAME_CLIENT_THINK`.
5. Added cgame import coverage proving prediction pulls commands through
   `trap_GetCurrentCmdNumber` / `trap_GetUserCmd`, while host-side
   `CL_GetUserCmd` still rejects future and overwritten command numbers before
   copying from the command ring.
6. Verification:
   `python -m pytest tests/test_usercmd_movement_transport_parity.py -q --tb=short`
   -> `5 passed`;
   `python -m pytest tests/test_usercmd_movement_transport_parity.py tests/test_engine_client_command_parity.py::test_usercmd_cgame_bridge_matches_retail_weapon_primary_and_fov_bytes tests/test_engine_client_command_parity.py::test_client_input_mapping_round_277_promotes_console_input_and_usercmd_symbols -q --tb=short`
   -> `7 passed`;
   `python -m pytest tests/test_usercmd_movement_transport_parity.py tests/test_playerstate_replication.py tests/test_game_active_pmove_wiring_parity.py tests/test_cgame_snapshot_parity.py tests/test_cgame_playerstate_transition_parity.py tests/test_cgame_item_respawn_timer_parity.py tests/test_game_native_export_helper_parity.py tests/test_pmove_validation_fixtures.py tests/test_pmove_air_control_runtime_parity.py tests/test_pmove_jump_timing_parity.py tests/test_pmove_movement_fixtures.py tests/test_pmove_helper_parity.py tests/test_pmove_acceleration_scope_parity.py tests/test_pmove_crouch_time_parity.py tests/test_pmove_crouch_slide_friction_parity.py tests/test_pmove_reload_fallback_parity.py tests/test_pmove_water_scale_parity.py tests/test_bg_playerstate_bridge_parity.py tools/tests/test_pmove_settings_configstring.py tests/test_pmove_selected_cvar_parity.py -q --tb=short`
   -> `199 passed, 107 subtests passed`;
   `python -m pytest tests/test_game_module_retail_parity_gate.py tests/test_qcommon_full_parity_gate.py tests/test_client_full_parity_gate.py -q --tb=short`
   -> `6 passed, 3 skipped`.

### Task A57: Restore retail parity for spawn and sudden-death `g_*` CVars [COMPLETED]
Priority: High
Primary areas: `src/code/game/g_main.c`, `src/game/g_config.c`,
`src/code/game/g_client.c`, `src/code/game/g_combat.c`,
`src/code/game/g_items.c`, `src/game/g_match_config.c`,
`docs/gameplay/cvars.md`, `tests/test_game_factory_regen_parity.py`,
`references/hlil/quakelive/qagamex86.dll/qagamex86.dll.bndb_hlil_split/qagamex86.dll.bndb_hlil_part02.txt`,
`references/hlil/quakelive/qagamex86.dll/qagamex86.dll.bndb_hlil_split/qagamex86.dll.bndb_hlil_part03.txt`
Parity estimate: **before 74% -> after 100%** for the selected ten-cvar
surface: `g_startingWeapons`, `g_startingHealth`,
`g_startingHealthBonus`, `g_startingArmor`, `g_suddenDeathRespawn`,
`g_suddenDeathRespawnStart`, `g_suddenDeathRespawnTick`,
`g_suddenDeathRespawnMax`, `g_suddenDeathRespawnIncrement`, and
`g_suddenDeathRespawnPrint`. Repo-wide remains **98%** pending the active
compatibility-only and runtime-evidence gaps.

Completed work:

1. Rechecked the qagame HLIL registration rows and string/default data for the
   selected spawn and sudden-death cvars, including the retail
   `g_startingWeapons` default mask (`3`) and the shared `CVAR_GAMERULE` flag
   across the sudden-death controller.
2. Corrected `g_startingHealth` to the retail `CVAR_SERVERINFO |
   CVAR_GAMERULE` row, corrected `g_startingArmor` and
   `g_startingWeapons` to `CVAR_GAMERULE`, and changed
   `g_startingWeapons` from source-local `0` to retail `3`.
3. Corrected `g_startingHealthBonus` and `g_suddenDeathRespawn` in the config
   cvar registration layer so duplicate registration preserves the recovered
   `CVAR_GAMERULE` flags.
4. Corrected `g_suddenDeathRespawnStart`, `g_suddenDeathRespawnTick`,
   `g_suddenDeathRespawnMax`, `g_suddenDeathRespawnIncrement`, and
   `g_suddenDeathRespawnPrint` to their retail `CVAR_GAMERULE` rows.
5. Revalidated wiring for spawn loadout masks, starting health/armor fallback,
   factory config caching, sudden-death match config caching, respawn-delay
   calculation, centerprint announcements, item respawn suppression, and match
   state publication.
6. Verification:
   `python -m pytest tests/test_game_factory_regen_parity.py -q --tb=short`
   -> `23 passed`;
   `python -m pytest tests/test_game_factory_regen_parity.py tests/test_match_state_configstring.py tests/test_gametype_lifecycle.py tests/test_game_helper_seam_parity.py tests/test_cvar_console_write_parity.py tests/test_game_module_retail_parity_gate.py -q --tb=short`
   -> `61 passed, 6 skipped`.

### Task A56: Re-audit server/client snapshot playerState transport [COMPLETED]
Priority: High
Primary areas: `src/code/server/sv_snapshot.c`,
`src/code/client/cl_parse.c`, `src/code/client/cl_cgame.c`,
`src/code/cgame/cg_syscalls.c`, `tests/test_playerstate_replication.py`,
`docs/reverse-engineering/quakelive_steam_mapping_round_17.md`,
`docs/reverse-engineering/quakelive_steam_mapping_round_65.md`,
`docs/reverse-engineering/quakelive_steam_mapping_round_127.md`,
`references/analysis/quakelive_symbol_aliases.json`
Parity estimate: **before 100% -> after 100%** for the scoped snapshot
playerState transport seam: server snapshot playerState build/write, client
snapshot parse/ring storage, `CL_GetSnapshot` exposure, and cgame syscall
retrieval. No production source patch was required.

Completed work:

1. Rechecked the retained retail mappings for `SV_BuildClientSnapshot`,
   `SV_WriteSnapshotToClient`, `SV_SendClientSnapshot`, `CL_ParseSnapshot`,
   `QLCGImport_GetCurrentSnapshotNumber`, and `QLCGImport_GetSnapshot`
   against mapping rounds 17, 65, 127, and the committed alias ledger.
2. Expanded `tests/test_playerstate_replication.py` so the server-side
   snapshot path now pins `SV_GameClientNum` copying into `frame->ps`, own
   client suppression, view-origin selection, visible-entity gathering,
   `svc_snapshot` field order, area-mask write, playerState delta write, and
   packet-entity emission order.
3. Added client-side snapshot parse coverage for `serverCommandSequence`,
   server time, delta metadata, snap flags, areamask, `MSG_ReadDeltaPlayerstate`,
   packet-entity parsing, invalid-frame discard, ping calculation from
   `ps.commandTime`, backup-ring storage, and `cl.newSnapshots`.
4. Added cgame import coverage showing `trap_GetSnapshot` reaches
   `CL_GetSnapshot`, which validates the ring entry and copies areamask,
   playerState, and bounded packet entities into the cgame-visible snapshot.
5. Verification:
   `python -m pytest tests/test_playerstate_replication.py -q --tb=short`
   -> `14 passed`;
   `python -m pytest tests/test_playerstate_replication.py tests/test_game_active_pmove_wiring_parity.py tests/test_cgame_snapshot_parity.py tests/test_cgame_playerstate_transition_parity.py tests/test_cgame_item_respawn_timer_parity.py tests/test_game_native_export_helper_parity.py tests/test_pmove_validation_fixtures.py tests/test_pmove_air_control_runtime_parity.py tests/test_pmove_jump_timing_parity.py tests/test_pmove_movement_fixtures.py tests/test_pmove_helper_parity.py tests/test_pmove_acceleration_scope_parity.py tests/test_pmove_crouch_time_parity.py tests/test_pmove_crouch_slide_friction_parity.py tests/test_pmove_reload_fallback_parity.py tests/test_pmove_water_scale_parity.py tests/test_bg_playerstate_bridge_parity.py tools/tests/test_pmove_settings_configstring.py tests/test_pmove_selected_cvar_parity.py -q --tb=short`
   -> `194 passed, 107 subtests passed`;
   `python -m pytest tests/test_game_module_retail_parity_gate.py tests/test_qcommon_full_parity_gate.py tests/test_client_full_parity_gate.py -q --tb=short`
   -> `6 passed, 3 skipped`. The full server parity gate still reports the
   unrelated retained `SV-G01` Steam GameServer lifecycle/callback/auth
   artifact lane as failing.

### Task A55: Restore retail parity for cosmetic, item-timer, and loadout `g_*` CVars [COMPLETED]
Priority: High
Primary areas: `src/code/game/g_main.c`, `src/code/game/g_local.h`,
`src/game/g_config.c`, `docs/gameplay/cvars.md`,
`tests/test_game_callvote_option_parity.py`,
`references/hlil/quakelive/qagamex86.dll/qagamex86.dll.bndb_hlil_split/qagamex86.dll.bndb_hlil_part02.txt`,
`references/hlil/quakelive/qagamex86.dll/qagamex86.dll.bndb_hlil_split/qagamex86.dll.bndb_hlil_part03.txt`
Parity estimate: **before 82% -> after 100%** for the selected ten-cvar
surface: `g_customSettings`, `g_itemTimers`, `g_itemHeight`,
`g_forceSmallScoreboardMessage`, `g_forceSendConfigstring`,
`g_forceAtmosphericEffects`, `g_forceDmgThroughSurface`,
`g_specItemTimers`, `g_loadout`, and `g_infiniteAmmo`. Repo-wide remains
**98%** pending the active compatibility-only and runtime-evidence gaps.

Completed work:

1. Rechecked the qagame HLIL registration rows and string/default data for the
   selected ten `g_*` CVars, including the recovered `CVAR_GAMERULE` bit and
   the `g_itemHeight` retail default string at `10086c34` (`35`).
2. Aligned source registration defaults and flags: `g_customSettings` now
   registers as default `0` with `CVAR_SERVERINFO`; `g_itemTimers` and
   `g_itemHeight` use `CVAR_SERVERINFO | CVAR_GAMERULE`; the forced cosmetics
   cvars use their retail no-flag or `CVAR_GAMERULE` rows; `g_loadout` and
   `g_infiniteAmmo` use their retail game-rule surfaces.
3. Added the missing retail `g_specItemTimers` registration as a plain
   qagame cvar, matching the recovered table's default `1` and no-flag row.
4. Revalidated wiring for the selected cvars: custom-settings digest rebuilds,
   item timer broadcasts and late-join sync, forced-cosmetics configstring
   updates, loadout vote/cgame mirroring, and infinite-ammo factory/spawn/weapon
   paths.
5. Updated gameplay cvar notes so the documented defaults/flags distinguish the
   retail `g_itemHeight` default (`35`) from the local invalid-height fallback.
6. Verification:
   `python -m pytest tests/test_game_callvote_option_parity.py -q --tb=short`
   -> `9 passed`;
   `python -m pytest tests/test_cvar_console_write_parity.py tests/test_game_callvote_option_parity.py tests/test_game_factory_regen_parity.py tests/test_game_forfeit_parity.py tests/test_game_module_retail_parity_gate.py tests/test_game_helper_seam_parity.py tests/test_game_native_export_helper_parity.py tests/test_game_compact_scoreboard_parity.py -q --tb=short`
   -> `74 passed, 1 skipped`.

### Task A54: Re-audit qcommon playerState delta-codec wiring [COMPLETED]
Priority: High
Primary areas: `src/code/qcommon/msg.c`, `src/code/game/q_shared.h`,
`tests/test_playerstate_replication.py`,
`docs/reverse-engineering/quakelive_steam_mapping_round_57.md`,
`docs/reverse-engineering/qcommon-full-parity-audit-and-implementation-plan-2026-04-10.md`,
`references/analysis/quakelive_symbol_aliases.json`
Parity estimate: **before 100% -> after 100%** for the scoped qcommon
playerState snapshot replication bridge: the Quake Live-expanded scalar
netfield table, signed command-axis mirrors, stats/persistant/ammo/powerup
array-mask sections, and server-to-cgame delta round trips. No production
source patch was required.

Completed work:

1. Rechecked the retained retail mapping for `sub_4D5D50 ->
   MSG_WriteDeltaPlayerstate` and `sub_4D66C0 -> MSG_ReadDeltaPlayerstate`
   against the committed alias ledger and mapping round 57.
2. Expanded `tests/test_playerstate_replication.py` with executable coverage
   for all four playerState array-mask sections, proving changed
   `stats[]`, `persistant[]`, `ammo[]`, and `powerups[]` slots round-trip
   while unchanged baseline slots survive the delta copy.
3. Added structural coverage for the full Quake Live scalar `playerStateFields`
   order and bit widths, including the movement-critical command-time,
   origin/velocity/viewangle, jump/crouch, weapon-primary, location, fov, and
   signed `forwardmove` / `rightmove` / `upmove` tail fields.
4. Pinned the signed-byte codec helpers so command-axis mirrors are compared
   as signed bytes, serialized as unsigned byte payloads, and restored through
   `MSG_SetPlayerStateFieldValue` on both changed and copied-from-baseline
   scalar fields.
5. Verification:
   `python -m pytest tests/test_playerstate_replication.py -q --tb=short`
   -> `10 passed`;
   `python -m pytest tests/test_playerstate_replication.py tests/test_game_active_pmove_wiring_parity.py tests/test_cgame_snapshot_parity.py tests/test_cgame_playerstate_transition_parity.py tests/test_cgame_item_respawn_timer_parity.py tests/test_pmove_validation_fixtures.py tests/test_pmove_air_control_runtime_parity.py tests/test_pmove_jump_timing_parity.py tests/test_pmove_movement_fixtures.py tests/test_pmove_helper_parity.py tests/test_pmove_acceleration_scope_parity.py tests/test_pmove_crouch_time_parity.py tests/test_pmove_crouch_slide_friction_parity.py tests/test_pmove_reload_fallback_parity.py tests/test_pmove_water_scale_parity.py tests/test_bg_playerstate_bridge_parity.py tools/tests/test_pmove_settings_configstring.py tests/test_pmove_selected_cvar_parity.py -q --tb=short`
   -> `184 passed, 107 subtests passed`;
   `python -m pytest tests/test_game_module_retail_parity_gate.py tests/test_qcommon_full_parity_gate.py -q --tb=short`
   -> `4 passed, 2 skipped`.

### Task A53: Restore retail `ammo_pack` item sentinel wiring [COMPLETED]
Priority: High
Primary areas: `src/code/game/bg_misc.c`, `src/code/game/g_items.c`,
`src/game/g_config.c`, `tests/test_game_ammopack_parity.py`,
`references/hlil/quakelive/qagamex86.dll/qagamex86.dll.bndb_hlil.txt`,
`references/symbol-maps/qagame.json`
Parity estimate: **before 96% -> after 100%** for scoped `ammo_pack`
metadata, grab eligibility, factory-family gating, `Pickup_Ammo` forwarding,
and `Add_Ammo` sentinel fan-out. Repo-wide remains **98%** pending the active
compatibility-only and runtime-evidence gaps.

Completed work:

1. Rechecked the qagame item table and symbol-map evidence for `ammo_pack`,
   `Pickup_Ammo`, `Add_Ammo`, `g_ammoPack`, `g_ammoPackHack`, and
   `g_ammoRespawn`.
2. Kept the shared item metadata aligned with retail: `ammo_pack` remains an
   `IT_AMMO` item tagged with the `WP_NUM_WEAPONS` sentinel and the recovered
   pickup sound, model, icon, pickup name, and quantity.
3. Reshaped game-side ammo pickup wiring so `Pickup_Ammo` resolves the entity
   count/item quantity and forwards the item tag once, while `Add_Ammo` owns
   the retail `WP_NUM_WEAPONS` sentinel path that scans owned weapons and adds
   per-weapon ammo-pack quantities.
4. Confirmed the existing shared grab rule still scans owned weapons below
   their maximum ammo, and the factory gate still switches between global
   ammo-pack and weapon-specific ammo families via `g_ammoPack` /
   `g_ammoPackHack`.
5. Added focused regression coverage for the retail evidence, source metadata,
   grab rule, `Add_Ammo` sentinel fan-out, `Pickup_Ammo` forwarding, and
   factory-family gate.
6. Verification:
   `python -m pytest tests/test_game_ammopack_parity.py -q --tb=short`
   -> `4 passed`;
   `python -m pytest tests/test_bg_misc_validation_fixtures.py tests/test_bg_misc_helper_parity.py tests/test_bg_itemlist_indexes.py tests/test_bg_itemlist_retail_metadata.py -q --tb=short`
   -> `47 passed`;
   `python -m pytest tests/test_game_factory_regen_parity.py tests/test_game_weapon_parity.py -q --tb=short`
   -> `38 passed`;
   `python -m pytest tests/test_game_ammopack_parity.py tests/test_bg_misc_validation_fixtures.py tests/test_bg_misc_helper_parity.py tests/test_bg_itemlist_indexes.py tests/test_bg_itemlist_retail_metadata.py -q --tb=short`
   -> `51 passed`.

### Task A52: Re-audit cgame prediction pmove replay wiring [COMPLETED]
Priority: High
Primary areas: `src/code/cgame/cg_predict.c`,
`src/code/cgame/cg_playerstate.c`, `src/code/cgame/cg_snapshot.c`,
`tests/test_cgame_snapshot_parity.py`,
`docs/reverse-engineering/cgame-mapping.md`,
`docs/reverse-engineering/cgame-bg-parity-implementation-plan.md`,
`references/symbol-maps/cgame.json`
Parity estimate: **before 100% -> after 100%** for the scoped cgame
prediction/playerState replay seam: local `pmove_t` setup, usercmd replay,
trigger/item prediction, mover correction, step smoothing, predictable-event
handoff, and committed retail symbol evidence. No production source patch was
required.

Completed work:

1. Rechecked the retail cgame prediction map for `CG_PredictPlayerState`,
   `CG_TouchItem`, `CG_TouchTriggerPrediction`, `CG_UpdateStepChange`,
   `CG_UpdatePredictedRailFire`, and `CG_TransitionPlayerState` against the
   committed symbol map and existing source reconstruction.
2. Expanded the cgame snapshot parity sentinel so the full prediction replay
   pipeline is pinned: projectile-nudge reset, local `pmove_settings_t` copy,
   trace/pointcontents callbacks, tracemask/body handling, command overflow
   guard, latest-command rail replay, next-snapshot seed selection,
   `pmove_msec` clamp, fixed-move view-angle update, `Pmove`, step smoothing,
   local projectile nudge, trigger prediction, final mover adjustment, and
   transition handoff.
3. Added structural coverage for item and trigger prediction sidecars,
   including retail server-authored pickup skips, grab/event/NODRAW/ammo side
   effects, no-predict and double-touch guards, box-trace trigger collision,
   teleport hyperspace, jump-pad activation, and jump-pad cache clearing.
4. Added a committed-evidence sentinel tying the source wiring back to
   `references/symbol-maps/cgame.json` and the cgame mapping ledgers.
5. Verification:
   `python -m pytest tests/test_cgame_snapshot_parity.py -q --tb=short`
   -> `11 passed`;
   `python -m pytest tests/test_cgame_snapshot_parity.py tests/test_cgame_playerstate_transition_parity.py tests/test_cgame_item_respawn_timer_parity.py -q --tb=short`
   -> `23 passed`;
   `python -m pytest tests/test_game_active_pmove_wiring_parity.py tests/test_cgame_snapshot_parity.py tests/test_cgame_playerstate_transition_parity.py tests/test_cgame_item_respawn_timer_parity.py tests/test_pmove_validation_fixtures.py tests/test_pmove_air_control_runtime_parity.py tests/test_pmove_jump_timing_parity.py tests/test_pmove_movement_fixtures.py tests/test_pmove_helper_parity.py tests/test_pmove_acceleration_scope_parity.py tests/test_pmove_crouch_time_parity.py tests/test_pmove_crouch_slide_friction_parity.py tests/test_pmove_reload_fallback_parity.py tests/test_pmove_water_scale_parity.py tests/test_bg_playerstate_bridge_parity.py tests/test_playerstate_replication.py tools/tests/test_pmove_settings_configstring.py tests/test_pmove_selected_cvar_parity.py -q --tb=short`
   -> `180 passed, 107 subtests passed`;
   `python -m pytest tests/test_game_module_retail_parity_gate.py tests/test_qcommon_full_parity_gate.py -q --tb=short`
   -> `4 passed, 2 skipped`.

### Task A51: Reconstruct VM bounded cvar registration and integer cache wiring [COMPLETED]
Priority: High
Primary areas: `src/code/qcommon/cvar.c`, `src/code/qcommon/qcommon.h`,
`src/code/game/q_shared.h`, `src/code/client/cl_cgame.c`,
`tests/test_cvar_console_write_parity.py`, `tests/test_cgame_hud_parity.py`,
`docs/reverse-engineering/quakelive_steam_mapping_round_294.md`,
`references/hlil/quakelive/quakelive_steam.exe/quakelive_steam.exe_hlil_split/quakelive_steam.exe_hlil_part04.txt`,
`references/hlil/quakelive/quakelive_steam.exe/quakelive_steam.exe_hlil_split/quakelive_steam.exe_hlil_part06.txt`
Parity estimate: **before 97% -> after 98%** for scoped core cvar
handling/management, VM cvar shadows, and bounded range registration. Repo-wide
remains **98%** pending the active compatibility-only and runtime-evidence
gaps.

Completed work:

1. Rechecked the retail `sub_4CCCC0`, `sub_4CDD30`, `sub_4CE400`, and
   `sub_4CE460` evidence for hex integer parsing, bounded cvar metadata,
   VM cvar shadow flags, and ranged VM registration.
2. Added `Cvar_ParseInteger()` and routed cvar creation/mutation integer-cache
   updates through the retail `"0x"` / `"0x%08x"` fallback path.
3. Reconstructed bounded-cvar registration metadata by forcing
   `CVAR_VM_CREATED` in `Cvar_GetBounded()` and adding `Cvar_RegisterBounded()`
   for the native cgame range-register import.
4. Added the retail `vmCvar_t.flags` shadow field and copied cvar flags during
   VM registration.
5. Updated cgame range registration to call the recovered qcommon wrapper and
   refreshed focused cvar/HUD parity tests for that source-visible path.
6. Verification:
   `python -m pytest tests/test_cvar_console_write_parity.py -q --tb=short`
   -> `6 passed`;
   `python -m pytest tests/test_cvar_console_write_parity.py tests/test_cgame_displaycontext_parity.py::test_register_cvars_publishes_retail_version_and_vote_reset tests/test_cgame_hud_parity.py::test_crosshair_team_health_default_matches_retail_mode_cvar tests/test_qcommon_full_parity_gate.py -q --tb=short`
   -> `10 passed, 1 skipped`;
   `python -m pytest tests/test_cvar_alias_console.py -q --tb=short`
   -> `1 passed`.

### Task A50: Re-audit focused retail `g_*` vote and complaint cvar parity tranche [COMPLETED]
Priority: Medium
Primary areas: `src/code/game/g_main.c`, `src/game/g_config.c`,
`docs/gameplay/cvars.md`, `tests/test_game_callvote_option_parity.py`,
`references/hlil/quakelive/qagamex86.dll/qagamex86.dll.bndb_hlil_split/qagamex86.dll.bndb_hlil_part03.txt`,
`references/hlil/quakelive/qagamex86.dll/qagamex86.dll.bndb_hlil_split/qagamex86.dll.bndb_hlil_part02.txt`
Parity estimate: **before 80% -> after 100%** for the scoped ten-cvar
vote/complaint tranche: `g_allowSpecVote`, `g_allowVote`,
`g_allowVoteMidGame`, `g_allowForfeit`, `g_allowKill`,
`g_complaintLimit`, `g_complaintDamageThreshold`, `g_voteFlags`,
`g_voteDelay`, and `g_voteLimit`. Repo-wide remains **98%** pending the
active compatibility-only and runtime-evidence gaps.

Completed work:

1. Rechecked the selected qagame registration rows against the committed HLIL
   cvar slab and string/default evidence.
2. Corrected `g_allowForfeit` to the retail `1` default and recovered
   `CVAR_GAMERULE` flag, and corrected `g_allowKill` to the retail
   `CVAR_GAMERULE` flag.
3. Corrected the factory fallback constants for
   `g_complaintDamageThreshold` and `g_complaintLimit` to retail `400` and
   `5`, matching the main registration table.
4. Confirmed the existing callvote, spectator vote, mid-game vote,
   vote-delay, vote-limit, vote-flag, forfeit, self-kill, complaint, and
   endvote wiring remains attached to the selected cvars.
5. Refreshed gameplay cvar notes and added focused regression coverage for
   the selected defaults, flags, retail evidence, and behavioral wiring.
6. Verification:
   `python -m pytest tests/test_game_callvote_option_parity.py -q --tb=short`
   -> `7 passed`;
   `python -m pytest tests/test_game_callvote_option_parity.py tests/test_game_forfeit_parity.py tests/test_game_factory_regen_parity.py tests/test_game_module_retail_parity_gate.py -q --tb=short`
   -> `35 passed, 1 skipped`;
   `python -m pytest tests/test_cvar_console_write_parity.py tests/test_game_callvote_option_parity.py tests/test_game_forfeit_parity.py tests/test_game_factory_regen_parity.py tests/test_game_module_retail_parity_gate.py -q --tb=short`
   -> `39 passed, 1 skipped`.

### Task A49: Restore retail key item mover wiring [COMPLETED]
Priority: High
Primary areas: `src/code/game/bg_misc.c`, `src/code/game/g_items.c`,
`src/code/game/g_mover.c`, `src/code/game/g_target.c`,
`src/code/cgame/cg_newdraw.c`, `tests/test_game_key_item_parity.py`,
`references/hlil/quakelive/qagamex86.dll/qagamex86.dll.bndb_hlil.txt`,
`references/symbol-maps/qagame.json`, `references/symbol-maps/cgame.json`
Parity estimate: **before 96% -> after 100%** for scoped silver/gold/master
key item pickup, reset, keyed mover, remove-keys target, and HUD icon wiring;
repo-wide remains **98%** pending the active portability/runtime-evidence gaps.

Completed work:

1. Rechecked the retail qagame key item records, `G_ResetKeyItem`,
   `Touch_DoorTriggerKeyed`, `Touch_ButtonKeyed`, and
   `Use_Target_RemoveKeys` evidence against the committed HLIL and symbol maps.
2. Restored the missing keyed-button touch path: silver-key buttons now accept
   silver or master keys, gold-key buttons accept gold or master keys, and
   keyed buttons only fire from `MOVER_POS1`.
3. Kept the existing retail-aligned key pickup/reset surface: key pickup sets
   the carried mask/stat and does not auto-respawn, dropped copies are freed
   when keys are reset, and `target_remove_keys` clears carried keys through
   the reset helper.
4. Added structural coverage for key item metadata, pickup/reset/drop,
   keyed-door/keyed-button gates, and the `CG_PLAYER_HASKEY` ownerdraw path.

### Task A48: Reconstruct core cvar handling and management wiring [COMPLETED]
Priority: High
Primary areas: `src/code/qcommon/cvar.c`, `src/code/game/q_shared.h`,
`tests/test_cvar_console_write_parity.py`,
`docs/reverse-engineering/quakelive_steam_mapping_round_293.md`,
`references/analysis/quakelive_symbol_aliases.json`,
`references/hlil/quakelive/quakelive_steam.exe/quakelive_steam.exe_hlil_split/quakelive_steam.exe_hlil_part04.txt`,
`references/hlil/quakelive/quakelive_steam.exe/quakelive_steam.exe_hlil_split/quakelive_steam.exe_hlil_part06.txt`
Parity estimate: **before 92% -> after 97%** for scoped core cvar
handling/management and source-visible WebView cvar-change wiring. Repo-wide
remains **98%** pending the active compatibility-only and runtime-evidence
gaps.

Completed work:

1. Rechecked retail `Cvar_Set2`, `Cvar_Get`, `Cvar_GetBounded`, and
   `QLWebView_PublishCvarChange` ownership against the committed alias ledger
   and HLIL/string evidence.
2. Restored the retail `2048` static cvar slot cap, added the recovered
   `CVAR_GAMERULE` flag, and reconstructed the initialization-time GAMERULE
   console `set` refusal gate.
3. Added retail cvar flag conflict cleanup for `CVAR_CHEAT` combined with
   archive or replicated/protected flags, including the recovered warning
   strings.
4. Reconstructed the missing `Cvar_Set2` publish call sites for user-created
   cvars and latched values while preserving the retail console write guard
   surface of ROM, INIT, LATCH, and CHEAT only.
5. Added mapping round 293 and focused regression coverage for the cvar core
   wiring, while leaving the repo-owned `sets`, `setu`, and `setcloud`
   compatibility helpers intact.
6. Verification:
   `python -m pytest tests/test_cvar_console_write_parity.py tests/test_client_config_parity.py tests/test_engine_command_parity.py -q --tb=short`
   -> `24 passed`;
   `python -m pytest tests/test_qcommon_full_parity_gate.py -q --tb=short`
   -> `2 passed, 1 skipped`. A broader
   `tests/test_engine_cvar_retail_parity.py tests/test_qcommon_full_parity_gate.py`
   run reached this cvar work but still failed two unrelated existing
   platform/Steam-service string checks.

### Task A47: Active-client pmove and playerState wiring reconstruction [COMPLETED]
Priority: High
Primary areas: `src/code/game/g_main.c`, `src/code/game/g_active.c`,
`src/code/game/g_local.h`, `tests/test_game_active_pmove_wiring_parity.py`,
`docs/reverse-engineering/qagame-mapping.md`
Parity estimate: **before 99% -> after 100%** for the scoped qagame
frame-step-to-`ClientThink_real` movement wiring edge. The broader shared
pmove/playerState reconstruction remains **100%** after this source-level
call-site realignment and guard expansion.

Completed work:

1. Rechecked qagame mappings for `G_RunFrame`, `ClientThink_real`,
   `SpectatorThink`, `ClientImpacts`, `G_TouchTriggers`,
   `SendPendingPredictableEvents`, and related active-client movement wiring.
2. Reconstructed the frame entity-loop client slot so bot/synchronous client
   frames run scheduled thinks inline and dispatch directly to
   `ClientThink_real`, matching the recovered retail `G_RunFrame` shape instead
   of routing that call-site through the classic source `G_RunClient` wrapper.
3. Added `ClientThink_real` to the game-local prototype surface so the recovered
   direct frame-loop dispatch is explicit and compile-visible.
4. Added focused structural coverage for the full active-client pmove wiring:
   command-time clamping, spectator scoreboard `PMF_NO_MOVE`, pmove setup,
   tracemask selection, fixed-move transport, playerState-to-entityState
   projection, predictable-event flushing, trigger touch, client impacts,
   respawn checks, timer actions, and committed symbol-map evidence.
5. Verification:
   `python -m pytest tests/test_game_active_pmove_wiring_parity.py -q --tb=short`
   -> `4 passed`;
   `python -m pytest tests/test_game_active_pmove_wiring_parity.py tests/test_game_helper_seam_parity.py tests/test_game_spectator_connection_parity.py -q --tb=short`
   -> `30 passed`;
   `python -m pytest tests/test_game_active_pmove_wiring_parity.py tests/test_pmove_validation_fixtures.py tests/test_pmove_air_control_runtime_parity.py tests/test_pmove_jump_timing_parity.py tests/test_pmove_movement_fixtures.py tests/test_pmove_helper_parity.py tests/test_pmove_acceleration_scope_parity.py tests/test_pmove_crouch_time_parity.py tests/test_pmove_crouch_slide_friction_parity.py tests/test_pmove_reload_fallback_parity.py tests/test_pmove_water_scale_parity.py tests/test_bg_playerstate_bridge_parity.py tests/test_cgame_playerstate_transition_parity.py tests/test_playerstate_replication.py tools/tests/test_pmove_settings_configstring.py tests/test_pmove_selected_cvar_parity.py -q --tb=short`
   -> `162 passed, 107 subtests passed`;
   `python -m pytest tests/test_game_module_retail_parity_gate.py tests/test_qcommon_full_parity_gate.py -q --tb=short`
   -> `4 passed, 2 skipped`.

### Task A46: Re-audit sixth focused retail `cl_*` cvar parity tranche [COMPLETED]
Priority: Medium
Primary areas: `src/code/client/cl_main.c`,
`src/common/platform/platform_services.c`,
`tests/test_engine_cvar_retail_parity.py`, `docs/client_cvars.md`,
`references/hlil/quakelive/quakelive_steam.exe/quakelive_steam.exe_hlil_split/quakelive_steam.exe_hlil_part04.txt`,
`references/reverse-engineering/ghidra/quakelive_steam/decompile_top_functions.c`
Parity estimate: **before 100% -> after 100%** for the scoped ten-cvar
service-disclosure tranche: `cl_onlineServicesMode`,
`cl_onlineServicesPolicy`, `cl_onlineServicesParityScope`,
`cl_onlineServicesParityReason`, `cl_identityBootstrapMode`,
`cl_identityBootstrapPolicy`, `cl_voiceServiceMode`,
`cl_voiceServicePolicy`, `cl_workshopProvider`, and `cl_workshopPolicy`.
These are intentional non-retail ROM diagnostics for the documented
online-services divergence; no production source patch was required. Repo-wide
remains **98%** pending the active portability/runtime-evidence gaps.

Completed work:

1. Rechecked the selected `cl_*` service-disclosure cvars against the
   repository's online-services divergence policy: default disabled or
   unclassified values, `CVAR_ROM` flags, and refresh through
   `CL_RefreshPlatformServiceCvars`.
2. Confirmed the active labels are sourced from the platform-services
   descriptor helpers and workshop descriptor helpers rather than being
   hardcoded as live-service state.
3. Confirmed no selected disclosure cvar appears in the recovered retail
   `CL_Init` HLIL/Ghidra evidence, keeping this compatibility surface outside
   the strict retail cvar slab.
4. Added a focused regression test that pins the defaults, flags, refresh
   wiring, descriptor ownership, and retail-evidence absence for all ten cvars.
5. Refreshed `docs/client_cvars.md` with the sixth focused cvar-tranche note.
6. Verification:
   `python -m pytest tests/test_engine_cvar_retail_parity.py::test_engine_cvar_thirtyninth_client_service_disclosure_tranche_matches_guarded_retail_divergence_contracts -q`
   -> `1 passed`.

### Task A45: Re-audit fifth focused retail `cl_*` cvar parity tranche [COMPLETED]
Priority: Medium
Primary areas: `src/code/client/cl_main.c`, `src/code/client/cl_input.c`,
`src/code/client/cl_parse.c`, `src/code/ui/ui_main.c`,
`tests/test_engine_cvar_retail_parity.py`, `docs/client_cvars.md`,
`references/hlil/quakelive/quakelive_steam.exe/quakelive_steam.exe_hlil_split/quakelive_steam.exe_hlil_part04.txt`,
`references/hlil/quakelive/uix86.all/uix86.dll_hlil_split/uix86.dll_hlil_part01.txt`,
`references/reverse-engineering/ghidra/quakelive_steam/decompile_top_functions.c`,
`references/reverse-engineering/ghidra/uix86/decompile_top_functions.c`
Parity estimate: **before 100% -> after 100%** for the scoped ten-cvar
native-UI bridge tranche: `cl_maxpackets`, `cl_packetdup`,
`cl_serverStatusResendTime`, `cl_maxPing`, `cl_motdString`,
`cl_downloadItem`, `cl_downloadName`, `cl_downloadTime`,
`cl_downloadCount`, and `cl_downloadSize`. No production source patch was
required; this pass refreshed and pinned the retail/native UI evidence.
Repo-wide remains **98%** pending the active portability/runtime-evidence gaps.

Completed work:

1. Rechecked retail registration/default/flag evidence for the selected
   engine-owned cvars against the committed Quake Live HLIL/Ghidra corpus.
2. Confirmed native `uix86` bridge behavior for network preset writes,
   server-status resend publication, max-ping filtering reads, MOTD reads, and
   workshop progress reads.
3. Confirmed `cl_downloadCount` / `cl_downloadSize` remain UI-facing temp
   fallbacks for legacy download/QVM paths while the recovered native progress
   bridge stays keyed by `cl_downloadItem` plus `GetItemDownloadInfo` and
   `cl_downloadTime`.
4. Added a focused regression test that pins the retail evidence,
   source-visible registrations, flags, and wiring for all ten cvars.
5. Refreshed `docs/client_cvars.md` with the fifth focused cvar-tranche note.
6. Verification:
   `python -m pytest tests/test_engine_cvar_retail_parity.py::test_engine_cvar_sixth_client_tranche_matches_retail_contracts tests/test_engine_cvar_retail_parity.py::test_engine_cvar_thirtyfourth_client_cl_tranche_matches_retail_contracts tests/test_engine_cvar_retail_parity.py::test_engine_cvar_thirtyseventh_client_lifecycle_workshop_tranche_matches_retail_contracts tests/test_engine_cvar_retail_parity.py::test_engine_cvar_thirtyeighth_client_native_ui_bridge_tranche_matches_retail_contracts tests/test_ui_menu_files.py::test_ui_retail_download_info_reads_item_progress_through_native_slot -q`
   -> `5 passed`. Broader workshop/platform-service verification was not
   runnable in this worktree because `tests/test_client_workshop_bootstrap_parity.py`
   and `tests/test_platform_services.py` currently fail collection on unrelated
   indentation errors before the selected tests can execute.

### Task A44: Profile and utility pmove/playerState wiring sweep [COMPLETED]
Priority: High
Primary areas: `src/code/game/g_pmove.c`, `src/code/game/bg_pmove.c`,
`src/code/cgame/cg_servercmds.c`, `src/game/g_config.c`,
`src/code/game/g_main.c`, `tests/test_pmove_selected_cvar_parity.py`,
`docs/reverse-engineering/qagame-mapping.md`,
`docs/reverse-engineering/cgame-bg-parity-implementation-plan.md`
Parity estimate: **before 100% -> after 100%** for scoped shared pmove,
playerState profile flag ownership, utility cvar transport, and
custom-settings wiring. Production source was already aligned with the
committed retail evidence; this pass added regression coverage for the
remaining profile/utility movement slab.

Completed work:

1. Rechecked the remaining profile and utility `pmove_*` fields against the
   retail qagame cvar slab and shared cgame/qagame movement consumers:
   `pmove_AirStepFriction`, `pmove_AirSteps`, `pmove_BunnyHop`,
   `pmove_CrouchSlide`, `pmove_CrouchSlideFriction`,
   `pmove_CrouchSlideTime`, `pmove_CrouchStepJump`, `pmove_DoubleJump`,
   `pmove_noPlayerClip`, `pmove_StepHeight`, `pmove_StepJump`,
   `pmove_velocity_gh`, `pmove_WaterSwimScale`, `pmove_WaterWadeScale`,
   `pmove_WeaponDropTime`, and `pmove_WeaponRaiseTime`.
2. Expanded `tests/test_pmove_selected_cvar_parity.py` so this cvar group is
   pinned from retail registration defaults/flags through factory reset,
   refresh callback/no-callback ownership, `g_pmoveSettings` cache assignment,
   compact and JSON cgame parsing, default shared movement constants, and
   active movement consumers.
3. Added coverage for the linked playerState and wiring edges: spawn-time
   `PMF_CROUCH_SLIDE` / `PMF_DOUBLE_JUMP` / `PMF_AIR_CONTROL` seeding,
   crouch-slide friction/timer consumption, no-player-clip tracemask removal,
   step/crouch-step gates, water/step globals, grapple pull speed,
   weapon raise/drop timings, and custom-settings mask participation.
4. Refreshed the qagame and cgame/bg mapping notes with the new evidence lane.
5. Verification:
   `python -m pytest tests/test_pmove_selected_cvar_parity.py -q --tb=short`
   -> `12 passed`;
   `python -m pytest tests/test_pmove_validation_fixtures.py tests/test_pmove_air_control_runtime_parity.py tests/test_pmove_jump_timing_parity.py tests/test_pmove_movement_fixtures.py tests/test_pmove_helper_parity.py tests/test_pmove_acceleration_scope_parity.py tests/test_pmove_crouch_time_parity.py tests/test_pmove_crouch_slide_friction_parity.py tests/test_pmove_reload_fallback_parity.py tests/test_pmove_water_scale_parity.py tests/test_bg_playerstate_bridge_parity.py tests/test_cgame_playerstate_transition_parity.py tests/test_playerstate_replication.py tools/tests/test_pmove_settings_configstring.py tests/test_pmove_selected_cvar_parity.py -q --tb=short`
   -> `158 passed, 107 subtests passed`;
   `python -m pytest tests/test_game_module_retail_parity_gate.py tests/test_qcommon_full_parity_gate.py -q --tb=short`
   -> `4 passed, 2 skipped`.

### Task A43: Re-audit fourth focused retail `cl_*` cvar parity tranche [COMPLETED]
Priority: Medium
Primary areas: `src/code/client/cl_main.c`, `src/code/client/cl_input.c`,
`src/code/client/cl_parse.c`, `src/code/client/cl_cgame.c`,
`src/code/client/cl_scrn.c`, `src/code/client/cl_ui.c`,
`src/code/qcommon/common.c`, `src/code/qcommon/cmd.c`,
`src/code/ui/ui_main.c`, `tests/test_engine_cvar_retail_parity.py`,
`docs/client_cvars.md`,
`references/hlil/quakelive/quakelive_steam.exe/quakelive_steam.exe_hlil_split/quakelive_steam.exe_hlil_part04.txt`,
`references/hlil/quakelive/uix86.all/uix86.dll_hlil_split/uix86.dll_hlil_part01.txt`,
`references/reverse-engineering/ghidra/quakelive_steam/decompile_top_functions.c`,
`references/reverse-engineering/ghidra/uix86/decompile_top_functions.c`
Parity estimate: **before 100% -> after 100%** for the scoped ten-cvar
lifecycle/MOTD/workshop tranche: `cl_motd`, `cl_motdString`,
`cl_timeout`, `cl_nodelta`, `cl_debugMove`, `cl_paused`, `cl_running`,
`cl_downloadItem`, `cl_downloadName`, and `cl_downloadTime`. The selected
cvar registrations and source-visible owners were already aligned; the
expanded workshop verification found and fixed one adjacent callback diagnostic
string drift, bringing the scoped workshop handoff evidence from **99% -> 100%**.
Repo-wide remains **98%** pending the active portability/runtime-evidence gaps.

Completed work:

1. Rechecked retail registration/default/flag evidence for the selected
   `CL_Init`, `CL_InitInput`, and common runtime `cl_*` cvars against the
   committed HLIL/Ghidra corpus.
2. Confirmed source-visible owners already match retail: MOTD enable/ROM
   string publication, timeout disconnect checks, delta suppression, movement
   diagnostics, paused/running ROM state and command routing.
3. Confirmed the retained workshop request cvars stay aligned with the
   recovered retail/uix86 handoff: `cl_downloadItem`, `cl_downloadName`, and
   `cl_downloadTime` are seeded from the request owner and consumed by the
   native UI progress bridge.
4. Restored the retail `ItemInstalled_t` invalid-app diagnostic string, which
   reuses the recovered `OnDownloadItemResult skip, invalid app id %d` text.
5. Added a focused regression test that pins the retail evidence, source
   registrations, and source-visible wiring for all ten cvars.
6. Refreshed `docs/client_cvars.md` with the fourth focused cvar-tranche note.
7. Verification:
   `python -m pytest tests/test_engine_cvar_retail_parity.py::test_engine_cvar_sixth_client_tranche_matches_retail_contracts tests/test_engine_cvar_retail_parity.py::test_engine_cvar_seventh_client_tranche_matches_retail_contracts tests/test_engine_cvar_retail_parity.py::test_engine_cvar_twentieth_client_debug_tranche_matches_retail_contracts tests/test_engine_cvar_retail_parity.py::test_engine_cvar_thirtyseventh_client_lifecycle_workshop_tranche_matches_retail_contracts tests/test_client_workshop_bootstrap_parity.py -q`
   -> `8 passed`.

### Task A42: Deep pmove/playerState mapping sweep [COMPLETED]
Priority: High
Primary areas: `src/code/game/bg_pmove.c`, `src/code/game/g_pmove.c`,
`src/code/cgame/cg_servercmds.c`, `src/code/game/bg_public.h`,
`tests/pmove_validation_harness.c`,
`tests/test_pmove_validation_fixtures.py`,
`tests/test_pmove_selected_cvar_parity.py`,
`tests/test_pmove_helper_parity.py`, `tests/test_playerstate_replication.py`,
`references/symbol-maps/qagame.json`, `references/symbol-maps/cgame.json`,
`docs/reverse-engineering/qagame-mapping.md`,
`docs/reverse-engineering/cgame-bg-parity-implementation-plan.md`
Parity estimate: **before 100% -> after 100%** for scoped shared pmove,
playerState command-gate management, pmove cvar transport, and qagame/cgame
prediction wiring. No production source patch was required; this pass added
retail-backed fixture and mapping coverage for the fragile remaining edges.

Completed work:

1. Rechecked qagame/cgame `PmoveSingle` symbol evidence for the playerState
   command gate: command time advances before `PMF_NO_MOVE`, while view-angle
   updates, command mirrors, trace dispatch, and movement side effects remain
   behind the no-move return.
2. Added an executable `PMF_NO_MOVE` fixture in
   `tests/pmove_validation_harness.c` and
   `tests/test_pmove_validation_fixtures.py` to pin that runtime behavior.
3. Validated the selected pmove cvar mapping sentinel, covering representative
   `pmove_*` retail names across registration defaults/flags, factory reset,
   refresh callback ownership, cached settings, compact/JSON cgame parsing,
   default shared movement constants, active `bg_pmove.c` consumers, and
   committed symbol-map evidence.
4. Re-ran the broad movement/playerState suite:
   `python -m pytest tests/test_pmove_validation_fixtures.py tests/test_pmove_air_control_runtime_parity.py tests/test_pmove_jump_timing_parity.py tests/test_pmove_movement_fixtures.py tests/test_pmove_helper_parity.py tests/test_pmove_acceleration_scope_parity.py tests/test_pmove_crouch_time_parity.py tests/test_pmove_crouch_slide_friction_parity.py tests/test_pmove_reload_fallback_parity.py tests/test_pmove_water_scale_parity.py tests/test_bg_playerstate_bridge_parity.py tests/test_cgame_playerstate_transition_parity.py tests/test_playerstate_replication.py tools/tests/test_pmove_settings_configstring.py tests/test_pmove_selected_cvar_parity.py -q --tb=short`
   -> `154 passed, 107 subtests passed`.

### Task A41: Re-audit third focused retail `cl_*` cvar parity tranche [COMPLETED]
Priority: Medium
Primary areas: `src/code/client/cl_main.c`, `src/code/client/cl_input.c`,
`src/code/client/cl_parse.c`, `src/code/qcommon/msg.c`,
`tests/test_engine_cvar_retail_parity.py`, `docs/client_cvars.md`,
`references/hlil/quakelive/quakelive_steam.exe/quakelive_steam.exe_hlil_split/quakelive_steam.exe_hlil_part04.txt`,
`references/reverse-engineering/ghidra/quakelive_steam/decompile_top_functions.c`
Parity estimate: **before 100% -> after 100%** for the scoped ten-cvar
debug/identity/mouse tranche: `cl_shownet`, `cl_showSend`,
`cl_anonymous`, `cl_platform`, `cl_maxPing`, `cl_mouseAccel`,
`cl_mouseAccelDebug`, `cl_mouseAccelOffset`, `cl_mouseAccelPower`, and
`cl_mouseSensCap`. No source patch was required; this pass refreshed and
pinned the retail evidence. Repo-wide remains **98%** pending the active
portability/runtime-evidence gaps.

Completed work:

1. Rechecked retail `CL_Init` default values and flags against the committed
   HLIL/Ghidra evidence for the ten selected client cvars.
2. Confirmed the current source already matches the source-visible retail
   owners: network/message debug printing, packet-send diagnostics, anonymous
   auth userinfo, platform ROM marker publication, max-ping timeout filtering,
   mouse acceleration math, mouse acceleration debug logging, and sensitivity
   cap behavior.
3. Added a focused regression test that pins the retail evidence, source
   registrations, and source-visible wiring for all ten cvars.
4. Refreshed `docs/client_cvars.md` with the third focused cvar-tranche note.
5. Verification:
   `python -m pytest tests/test_engine_cvar_retail_parity.py::test_engine_cvar_thirtysixth_client_debug_identity_tranche_matches_retail_contracts -q`
   -> `1 passed`.

### Task A40: Re-audit second focused retail `cl_*` cvar parity tranche [COMPLETED]
Priority: Medium
Primary areas: `src/code/client/cl_main.c`, `src/code/client/cl_input.c`,
`tests/test_engine_cvar_retail_parity.py`, `docs/client_cvars.md`,
`references/hlil/quakelive/quakelive_steam.exe/quakelive_steam.exe_hlil_split/quakelive_steam.exe_hlil_part04.txt`,
`references/reverse-engineering/ghidra/quakelive_steam/decompile_top_functions.c`
Parity estimate: **before 100% -> after 100%** for the scoped ten-cvar
demo/input tranche: `cl_avidemo`, `cl_avidemo_latch`,
`cl_avidemo_mintime`, `cl_avidemo_maxtime`, `cl_forceavidemo`,
`cl_anglespeedkey`, `cl_yawspeed`, `cl_pitchspeed`, `cl_run`, and
`cl_freelook`. No source patch was required; this pass refreshed and pinned
the retail evidence. Repo-wide remains **98%** pending the active
portability/runtime-evidence gaps.

Completed work:

1. Rechecked retail `CL_Init` default values and flags against the committed
   HLIL/Ghidra evidence for the ten selected client demo/input cvars.
2. Confirmed the current source already matches the source-visible retail
   owners: avidemo latch/start/stop/screenshot/fixed-msec handling, keyboard
   and joystick angle-speed scaling, run/walk move-speed selection, and
   freelook center-view/mouse-pitch gating.
3. Added a focused regression test that pins the retail evidence, source
   registrations, and source-visible wiring for all ten cvars.
4. Refreshed `docs/client_cvars.md` with the second focused cvar-tranche note.
5. Verification:
   `python -m pytest tests/test_engine_cvar_retail_parity.py::test_engine_cvar_thirtyfifth_client_demo_input_tranche_matches_retail_contracts -q`
   -> `1 passed`.

### Task A39: Re-audit focused retail `s_*` sound cvar parity tranche [COMPLETED]
Priority: Medium
Primary areas: `src/code/client/snd_dma.c`,
`tests/test_engine_cvar_retail_parity.py`,
`tests/test_client_sound_voice_parity.py`,
`references/hlil/quakelive/quakelive_steam.exe/quakelive_steam.exe_hlil_split/quakelive_steam.exe_hlil_part04.txt`
Parity estimate: **before 98% -> after 100%** for the scoped ten-cvar tranche:
`s_announcerVolume`, `s_doppler`, `s_initsound`, `s_mixahead`,
`s_mixPreStep`, `s_musicvolume`, `s_pvs`, `s_voiceVolume`, `s_voiceStep`,
and `s_volume`. Repo-wide remains **98%** pending the active
portability/runtime-evidence gaps.

Completed work:

1. Rechecked retail `S_Init` default values, flags, and registration order
   against the committed HLIL evidence for the selected sound cvars.
2. Realigned the retail sound-registration cluster so `s_show`, `s_testsound`,
   and `s_volume` match the recovered order, while the legacy source-only
   `s_separation`/`s_khz` compatibility cvars now sit outside the retail
   early `s_initsound` gate.
3. Restored the retail `S_Update_` mix-ahead owner for `s_mixahead` by removing
   the older source-only `sane`/`op` cap; `s_mixPreStep` remains wired through
   `S_GetSoundtime` and the voice-buffer scheduler.
4. Expanded the focused regression guard so default value, flag set,
   registration order, and source-visible wiring are pinned for the selected
   cvars, including `s_pvs` spatial culling and `s_voiceStep` voice scheduling.
5. Verification:
   `python -m pytest tests/test_client_sound_voice_parity.py tests/test_engine_cvar_retail_parity.py::test_engine_cvar_eighteenth_sound_tranche_matches_retail_contracts -q --tb=short`
   -> `9 passed`.

### Task A38: Re-audit focused retail `cl_*` cvar parity tranche [COMPLETED]
Priority: Medium
Primary areas: `src/code/client/cl_keys.c`, `src/code/client/cl_main.c`,
`src/code/client/cl_input.c`, `src/code/client/cl_cgame.c`,
`src/code/client/cl_scrn.c`, `tests/test_engine_cvar_retail_parity.py`,
`docs/client_cvars.md`,
`references/hlil/quakelive/quakelive_steam.exe/quakelive_steam.exe_hlil_split/quakelive_steam.exe_hlil_part04.txt`,
`references/reverse-engineering/ghidra/quakelive_steam/decompile_top_functions.c`
Parity estimate: **before 96% -> after 100%** for the scoped ten-cvar tranche:
`cl_allowConsoleChat`, `cl_demoRecordMessage`, `cl_freezeDemo`,
`cl_maxpackets`, `cl_packetdup`, `cl_timeNudge`, `cl_autoTimeNudge`,
`cl_quitOnDemoCompleted`, `cl_serverStatusResendTime`, and
`cl_showTimeDelta`. Repo-wide remains **98%** pending the active
portability/runtime-evidence gaps.

Completed work:

1. Rechecked retail `CL_Init` default values and flags against the committed
   HLIL/Ghidra evidence for the ten selected client cvars.
2. Restored the retail `cl_allowConsoleChat` console-enter owner so bare
   console text is forced to command form unless that cvar explicitly enables
   console chat.
3. Added a focused regression test that pins the retail evidence, source
   registrations, and source-visible wiring for all ten cvars.
4. Refreshed `docs/client_cvars.md` with the scoped cvar-tranche evidence note.
5. Verification:
   `python -m pytest tests/test_engine_cvar_retail_parity.py::test_engine_cvar_second_tranche_matches_retail_contracts tests/test_engine_cvar_retail_parity.py::test_engine_cvar_sixth_client_tranche_matches_retail_contracts tests/test_engine_cvar_retail_parity.py::test_engine_cvar_seventh_client_tranche_matches_retail_contracts tests/test_engine_cvar_retail_parity.py::test_engine_cvar_eighth_client_input_tranche_matches_retail_contracts tests/test_engine_cvar_retail_parity.py::test_engine_cvar_ninth_client_misc_tranche_matches_retail_contracts tests/test_engine_cvar_retail_parity.py::test_engine_cvar_twentieth_client_debug_tranche_matches_retail_contracts tests/test_engine_cvar_retail_parity.py::test_engine_cvar_thirtyfourth_client_cl_tranche_matches_retail_contracts -q`
   -> `7 passed`.

### Task A37: Re-audit pmove factory wiring [COMPLETED]
Priority: High
Primary areas: `src/code/game/g_pmove.c`, `src/code/game/g_factory.c`,
`src/game/g_config.c`, `src/code/game/g_main.c`,
`src/code/cgame/cg_servercmds.c`,
`tools/tests/test_pmove_settings_configstring.py`,
`tests/test_game_factory_regen_parity.py`,
`tests/test_game_weapon_parity.py`, `tests/test_ui_menu_files.py`,
`tests/test_cgame_displaycontext_parity.py`,
`references/hlil/quakelive/qagamex86.dll/qagamex86.dll.bndb_hlil.txt`,
`references/symbol-maps/qagame.json`,
`docs/reverse-engineering/qagame-mapping.md`
Parity estimate: **before 100% -> after 100%** for scoped pmove factory
cvar registration, factory reset/apply ordering, cached movement-settings
refresh, custom-settings mask participation, and cgame/UI publication wiring.

Completed work:

1. Rechecked the 36-entry retail `pmove_*` cvar slab at
   `0x1008F7C4..0x1008FB20` against the current split `g_pmove.c` owner:
   default strings, flag groups, callback/no-callback slots, reset defaults,
   cache fields, and minimum-positive clamps still match the committed HLIL
   and symbol-map evidence.
2. Rechecked factory selection flow: `Factory_Apply` resets gameplay config
   and pmove-owned factory surfaces before overrides, refreshes all VM cvars,
   updates config mirrors, and only then rebuilds weapon/reload/knockback/ammo
   and match-factory mirrors. `G_UpdateWeaponReloadConfig` still pushes reload
   overrides into the pmove cache and forces a pmove settings refresh.
3. Rechecked custom-settings ownership: air-control, ramp-jump, physics,
   weapon-switching, no-player-clip, instagib, quad-hog, and grappling-hook
   bits still mirror the retail `G_UpdateCustomSettingsMaskForCvar` grouping
   while `pmove_velocity_gh` remains distinct from projectile `g_velocity_gh`.
4. Added a focused regression guard in
   `tests/test_game_factory_regen_parity.py` to pin the factory null/active
   reset sequence, post-override refresh order, and reload-to-pmove handoff.
5. Re-ran the focused wiring suite:
   `python -m pytest tools/tests/test_pmove_settings_configstring.py tests/test_game_factory_regen_parity.py tests/test_game_weapon_parity.py::test_grappling_hook_full_server_and_cgame_wiring_matches_retail tests/test_ui_menu_files.py::test_ui_retail_server_settings_ownerdraw_restored tests/test_ui_menu_files.py::test_game_retail_weapon_reload_configstring_restored tests/test_cgame_displaycontext_parity.py::test_cgame_weapon_reload_configstring_bridge_restored tests/test_cgame_displaycontext_parity.py::test_cgame_server_settings_panel_reconstruction_uses_retail_custom_setting_configstrings -q --tb=short`
   -> `32 passed, 107 subtests passed`.

### Task A36: Re-audit player movement, player states, and shared wiring [COMPLETED]
Priority: High
Primary areas: `src/code/game/bg_pmove.c`, `src/code/game/bg_slidemove.c`,
`src/code/game/q_shared.h`, `src/code/qcommon/msg.c`,
`src/code/game/g_pmove.c`, `src/code/cgame/cg_servercmds.c`,
`tests/test_pmove_*.py`, `tests/test_playerstate_replication.py`,
`references/symbol-maps/qagame.json`,
`references/symbol-maps/cgame.json`,
`docs/reverse-engineering/cgame-bg-parity-implementation-plan.md`
Parity estimate: **before 100% -> after 100%** for scoped player movement,
playerState layout/replication, pmove settings transport, and cgame/qagame
prediction wiring. No source patch was required; this pass refreshed the
evidence that the existing retail reconstruction remains intact.

Completed work:

1. Rechecked the current source against the committed pmove/playerState mapping
   notes and symbol-map evidence for the shared qagame/cgame movement island.
2. Confirmed the retail playerState prefix remains intact, including
   `clientNum` at `0x88`, `location` at `0x8c`, `weaponPrimary`, `fov`,
   `crouchSlideTime`, and the signed command-byte mirrors at `0x1dc..0x1de`.
3. Confirmed qcommon still delta-replicates the playerState command mirrors,
   holdable timer stats, movement flags, and jump/crouch timing fields used by
   retail prediction and demo/HUD consumers.
4. Confirmed qagame still publishes the compact retail pmove settings stream,
   cgame parses the 33-token retail core plus bounded reconstruction extension,
   and `PmoveSingle` consumes the server-seeded movement-profile flags rather
   than mutating them locally.
5. Re-ran the focused movement/playerState suites:
   `python -m pytest tests/test_pmove_validation_fixtures.py tests/test_pmove_air_control_runtime_parity.py tests/test_pmove_jump_timing_parity.py tests/test_pmove_movement_fixtures.py tests/test_pmove_helper_parity.py tests/test_pmove_acceleration_scope_parity.py tests/test_pmove_crouch_time_parity.py tests/test_pmove_crouch_slide_friction_parity.py tests/test_pmove_reload_fallback_parity.py tests/test_pmove_water_scale_parity.py tests/test_bg_playerstate_bridge_parity.py tests/test_cgame_playerstate_transition_parity.py tests/test_playerstate_replication.py tools/tests/test_pmove_settings_configstring.py -q --tb=short`
   -> `145 passed, 107 subtests passed`.
6. Re-ran the shared projection and strict gate sentinels:
   `python -m pytest tests/test_bg_misc_validation_fixtures.py tests/test_bg_misc_runtime_parity.py tests/test_bg_misc_helper_parity.py -q --tb=short`
   -> `39 passed`;
   `python -m pytest tests/test_game_module_retail_parity_gate.py tests/test_qcommon_full_parity_gate.py -q --tb=short`
   -> `4 passed, 2 skipped`.

### Task A33: Audit retail UI feeder parity and wiring [COMPLETED]
Priority: High
Primary areas: `src/code/ui/ui_main.c`, `src/code/cgame/cg_main.c`,
`src/ui/*.menu` (read-only evidence), `references/hlil/quakelive/uix86.all/`,
`references/symbol-maps/ui.json`, `tests/test_ui_menu_files.py`,
`tests/test_cgame_displaycontext_parity.py`
Parity estimate: **before 86% -> after 100%** for scoped feeder ownership and
callback wiring after the retail matrix, player-model feeder repair, and
cgame scoreboard-family verification. Repo-wide remains **98%** pending the
active portability/runtime-evidence gaps.

Feeder queue:

- [x] Establish ownership buckets for the 0x00-0x13 Quake Live feeder ids:
  UI-owned listboxes, cgame-owned scoreboard/team listboxes, and dormant
  `FEEDER_CLANS`.
- [x] Verify UI-owned callbacks for `FEEDER_HEADS`, `FEEDER_MAPS`,
  `FEEDER_SERVERS`, `FEEDER_ALLMAPS`, `FEEDER_PLAYER_LIST`,
  `FEEDER_TEAM_LIST`, `FEEDER_MODS`, `FEEDER_DEMOS`, `FEEDER_Q3HEADS`,
  `FEEDER_SERVERSTATUS`, `FEEDER_FINDPLAYER`, `FEEDER_CINEMATICS`, and
  `FEEDER_CVMAPS`.
- [x] Verify cgame-owned callbacks for `FEEDER_REDTEAM_LIST`,
  `FEEDER_BLUETEAM_LIST`, `FEEDER_SCOREBOARD`, `FEEDER_ENDSCOREBOARD`,
  `FEEDER_REDTEAM_STATS`, and `FEEDER_BLUETEAM_STATS`.
- [x] Keep `FEEDER_CLANS` as a defined-but-dormant retail id unless new
  committed evidence shows an active menu, host, or browser contract.
- [x] Run focused feeder parity tests and patch any concrete mismatch surfaced
  by the matrix.
- [x] Repair `FEEDER_HEADS` / `FEEDER_Q3HEADS` to use the validated retail
  player-model catalog, pass listbox item cvars through `feederSelection`, and
  drop the non-retail PunkBuster server-browser text column from the UI feeder.
- [x] Verification:
  `python -m pytest tests/test_ui_menu_files.py::test_ui_retail_feeder_matrix_matches_menu_consumers_and_callback_ownership tests/test_ui_menu_files.py::test_ui_retail_feeder_leaf_callbacks_match_remaining_ui_owned_ids tests/test_ui_menu_files.py::test_ui_retail_callvote_map_feeder_uses_active_map_slab tests/test_ui_menu_files.py::test_ui_retail_clan_feeder_scaffolding_is_removed tests/test_cgame_displaycontext_parity.py::test_cgame_scoreboard_feeder_matrix_owns_all_retail_scoreboard_feeders tests/test_cgame_displaycontext_parity.py::test_cgame_scoreboard_selection_callbacks_restore_cached_team_list_menu_seam`
- [x] Verification: Debug Win32 `ui.vcxproj` and `cgamex86.vcxproj` builds
  succeeded; `ui.vcxproj` still reports three pre-existing C4090 warnings in
  `UI_RunOrdersScript` / `UI_RunVoiceOrdersScript`.

## Recent closure

### Task A35: Re-audit match exit rules and round-mode wiring [COMPLETED]
Priority: High
Primary areas: `src/code/game/g_main.c`, `src/code/game/g_active.c`,
`src/code/game/g_team.c`, `src/code/game/g_local.h`,
`tests/test_game_exit_rules_parity.py`,
`tests/test_game_round_controller_helper_parity.py`,
`tests/test_game_attack_defend_parity.py`,
`references/hlil/quakelive/qagamex86.dll/`,
`references/symbol-maps/qagame.json`,
`docs/reverse-engineering/qagame-mapping.md`
Parity estimate: **before 96% -> after 100%** for scoped match-exit rule,
intermission, Red Rover tie, Freeze fallback, and A/D plus CA/Freeze mercy
window wiring; repo-wide remains **98%** pending the active
portability/runtime-evidence gaps.

Completed work:

1. Rechecked qagame `ScoreIsTied`, `CheckExitRules`, `G_ADCheckExitRules`,
   `G_CAFZCheckExitRules`, and `G_RRCheckExitRules` against the committed
   Binary Ninja HLIL and symbol-map entries.
2. Restored Red Rover to the retail non-team leader-score tie path instead of
   the red/blue team-score tie path.
3. Restored the generic Freeze exit-rule fallback gate to use
   `g_freezeRoundDelay`, matching the retail branch in `CheckExitRules`.
4. Shared the overtime-adjusted exit-limit helper with the A/D and CA/Freeze
   mercy checks, and removed the source-only CA/Freeze roundlimit leader guard
   so the red-first/blue-second threshold order matches retail.
5. Refreshed focused structural coverage for the match-exit, round-controller,
   and Attack and Defend helper seams.

### Task A34: Restore retail spectator player-name scorebox wiring [COMPLETED]
Priority: High
Primary areas: `src/code/cgame/cg_newdraw.c`,
`tests/test_cgame_displaycontext_parity.py`,
`references/symbol-maps/cgame.json`,
`docs/reverse-engineering/cgame-mapping.md`
Parity estimate: **before 88% -> after 100%** for scoped cgame spectator
player-name and scorebox score ownerdraw wiring, including follow-name anchor
alignment, first/second-place configstring label ownership, fixed retail
truncation thresholds, and missing/forfeit score fallbacks; repo-wide remains
**98%** pending the active portability/runtime-evidence gaps.

Completed work:

1. Rechecked the cgame ownerdraw corridor against the Binary Ninja HLIL for
   `0x10033BF0`, `0x10035BD0`, and `0x10035F30`, plus the committed Ghidra
   switch and symbol-map entries.
2. Restored retail anchor alignment for `CG_FOLLOW_PLAYER_NAME` and
   `CG_FOLLOW_PLAYER_NAME_EX` instead of centering inside the authored rect.
3. Routed `CG_1ST_PLYR` / `CG_2ND_PLYR` through cached
   `CS_FIRST_PLACE_NAME` / `CS_SECOND_PLACE_NAME` labels, including the
   tournament `-` fallback and the fixed 140/132-pixel ellipsis truncation
   thresholds observed in HLIL.
4. Routed `CG_1ST_PLYR_SCORE` / `CG_2ND_PLYR_SCORE` through cached
   `CS_SCORES1` / `CS_SCORES2` values with the retail unavailable marker for
   `SCORE_NOT_PRESENT` and forfeit scores.
5. Refreshed cgame display-context parity coverage and reran the focused
   spectator/scorebox suites.

### Task A32: Restore retail Flight refuel-rate registration boundary [COMPLETED]
Priority: High
Primary areas: `src/code/game/g_items.c`, `src/code/game/g_main.c`,
`src/code/game/g_local.h`, `references/symbol-maps/qagame.json`,
`tests/test_game_factory_regen_parity.py`
Parity estimate: **before 99% -> after 100%** for scoped Flight powerup
pickup/fuel timer parity; repo-wide remains **98%** pending the active
portability/runtime-evidence gaps.

Completed work:

1. Rechecked qagame `Pickup_Powerup` at `0x1004DFE0` against the committed
   Ghidra decompile and the qagame symbol-map evidence.
2. Confirmed retail keeps `g_flightThrust` and `g_flightRefuelRate`
   registered for cvar/factory parity, but exposes no Flight-specific pickup
   multiplier.
3. Restored the registered `g_flightRefuelRate` storage/default while keeping
   direct `quantity * 1000` timer addition for Flight fuel/refill.
4. Added structural coverage so Flight cannot gain a separate refuel-rate
   consumer while `PM_FlyMove` remains free of `g_flightThrust` movement input.

### Task A31: Restore retail spectator follow command and fallback state [COMPLETED]
Priority: High
Primary areas: `src/code/game/g_cmds.c`, `src/code/game/g_active.c`,
`src/code/game/g_local.h`, `tests/test_game_spectator_connection_parity.py`,
`docs/reverse-engineering/qagame-spectator-follow-reconstruction-2026-05-22.md`
Parity estimate: **before 88% -> after 96%** for scoped qagame spectator
follow/stop-follow command handling, HUD auto-follow command compatibility,
saved-team restoration, and missing-target fallback; repo-wide remains **98%**
pending broader runtime and remaining subsystem gaps.

Completed work:

1. Rechecked the qagame symbol map entries for `SpectatorThink`,
   `SpectatorClientEndFrame`, `StopFollowing`, `Cmd_Follow_f`, and
   `FollowCycle`, plus the cgame symbol-map evidence for the retail
   `follow %d%s` HUD auto-follow command shape.
2. Added a shared qagame spectator fallback helper that preserves the local
   `g_teamSpecFreeCam` policy while giving stop-follow and missing-target
   paths a single state transition.
3. Restored `StopFollowing` to preserve `sess.sessionTeam`, restore
   `ps.persistant[PERS_TEAM]` from it, reset `sess.spectatorClient` to the
   caller's own slot, clear `PMF_FOLLOW`, and set scoreboard flags from the
   fallback state.
4. Restored `Cmd_Follow_f` player-string parsing and optional cgame powerup
   suffix tolerance. A later 2026-05-26 HLIL pass corrected the boundary:
   `follow1` and `follow2` are `SetTeam` tokens, not `Cmd_Follow_f` tokens.
5. Routed unresolved active-player follow targets, removed POIs, and invalid
   explicit follow targets through `StopFollowing` from
   `SpectatorClientEndFrame`.
6. Added focused static parity coverage for the stop-follow, follow-command,
   and end-frame fallback seams.

### Task A30: Restore retail scoreboard feeder dispatch and team-row selection [COMPLETED]
Priority: High
Primary areas: `src/code/cgame/cg_main.c`,
`tests/test_cgame_displaycontext_parity.py`
Parity estimate: **before 94% -> after 100%** for scoped scoreboard feeder
dispatch, feeder-local row mapping, selection cursor synchronization, and
invalid-row guard behavior; repo-wide remains **98%** pending the active
portability/runtime-evidence gaps.

Completed work:

1. Rechecked cgame `CG_FeederCount`, `CG_SetScoreSelection`,
   `CG_InfoFromScoreIndex`, `CG_FeederItemText`, and `CG_FeederSelection`
   against the Binary Ninja HLIL feeder block and the committed cgame symbol
   map.
2. Restored retail text-dispatch ownership: red/blue team-list feeders enter
   the team-list leaves, red/blue stats feeders enter the rich stats leaves, and
   all other text feeder requests fall back to the race or normal scoreboard
   leaf instead of being misrouted through team-list fallbacks.
3. Restored explicit team-local row mapping for team scoreboard cursors while
   keeping `cg.selectedScore` as the absolute `cg.scores` row used by cgame.
4. Hardened score-row lookup so invalid feeder rows return no row context
   instead of indexing past `cg.scores`.
5. Updated cgame display-context parity tests and reran the focused scoreboard
   suite.

### Task A29: Restore retail `pmove_*` cvar registration and callback wiring [COMPLETED]
Priority: High
Primary areas: `src/code/game/g_pmove.c`, `src/code/game/g_main.c`,
`src/game/g_config.c`, `tools/tests/test_pmove_settings_configstring.py`,
`tests/test_game_factory_regen_parity.py`,
`references/symbol-maps/qagame.json`,
`docs/reverse-engineering/qagame-mapping.md`,
`docs/reverse-engineering/cgame-bg-parity-implementation-plan.md`
Parity estimate: **before 92% -> after 100%** for scoped `pmove_*` cvar
default, flag, callback, cache, and transport wiring; repo-wide remains
**98%** pending the active portability/runtime-evidence gaps.

Completed work:

1. Rechecked the qagame cvar-table slab at `0x1008F7C4..0x1008FB20`,
   confirming the 36 retail `pmove_*` names, default strings, and four observed
   registration flag groups.
2. Restored those high-bit retail flags in the split `g_pmove.c` registration
   owner instead of registering every pmove cvar with flag `0`.
3. Revalidated the surrounding cache, custom-setting, configstring, and cgame
   compact-parser wiring; no payload order change was needed.
4. Added structural coverage that pins each `pmove_*` registration's default
   and flag group against the recovered retail table.
5. Reconstructed the retail callback-backed update path for the pmove cvar
   slab: all callback-backed entries now update through named mirrors and the
   three callback-less profile toggles (`pmove_AirControl`, `pmove_CrouchSlide`,
   and `pmove_DoubleJump`) remain suppressed just like the retail table.
6. Restored the cached lower-bound behavior observed in `G_InitPublishedCvarState`
   and the pmove callbacks: `pmove_velocity_gh`,
   `pmove_JumpVelocityTimeThreshold`, and
   `pmove_JumpVelocityTimeThresholdOffset` now clamp to retail's `0.001`
   minimum before publication.
7. Rechecked the adjacent grapple-speed ownership: retail `PM_GrappleMove`
   reads the dedicated `pmove_velocity_gh` cache, while `g_velocity_gh`
   remains a separate projectile-speed cvar with the recovered `1800` default.
   Source now keeps those paths decoupled and updates the grappling-hook
   custom-settings comparison accordingly.
8. Re-ran the full-name `pmove_*` sweep and classified `pmove_fixed` /
   `pmove_msec` as legacy fixed-timestep controls outside the 36-entry QL
   factory-managed tuning slab. Coverage now pins their `0` / `8` defaults,
   server-side `CVAR_SYSTEMINFO` registration, cgame mirrors, `8..33` clamp,
   and shared `Pmove` chunking behavior.

### Task A28: Re-audit retail step/crouch-step/chain-jump takeoff wiring [COMPLETED]
Priority: High
Primary areas: `src/code/game/bg_pmove.c`,
`references/symbol-maps/qagame.json`,
`references/symbol-maps/cgame.json`,
`docs/reverse-engineering/qagame-mapping.md`,
`docs/reverse-engineering/cgame-mapping.md`,
`docs/reverse-engineering/cgame-bg-parity-implementation-plan.md`,
`tests/test_pmove_helper_parity.py`,
`tests/test_pmove_movement_fixtures.py`
Parity estimate: **before 91% -> after 100%** for scoped crouch-step,
step-jump, and chain-jump takeoff wiring; repo-wide remains **98%**
pending the active portability/runtime-evidence gaps.

Completed work:

1. Rechecked qagame `PM_StepSlideMove` at `0x1002EFE0`, cgame
   `PM_StepSlideMove` at `0x100034B0`, and the shared qagame/cgame
   `PM_ApplyJumpTakeoff` leaves at `0x1002E2C0` / `0x10002790`.
2. Restored the missing normal step-jump takeoff latch so the normal path
   selects `pmove_StepJumpVelocity` in the additive retail branches, while the
   crouch-step fallback continues to use `pmove_ChainJumpVelocity` and raises
   only the ramp-suppression latch.
3. Corrected chain-jump mode wiring so PMF_AIR_CONTROL overrides disabled
   `pmove_ChainJump` mode `0`, the post-offset air-control addend divides by
   the retail offset threshold, and max clamping applies after additive and
   ramp-accumulated takeoff velocity.
4. Added executable fixtures that pin mode `0` air-control override,
   late-window air-control edge values, normal step additive takeoff, crouch-step
   chain-additive takeoff, step-jump scale-mode takeoff, step-jump air-control edge
   profiles, and non-ramp max clamping.

### Task A27: Pin pmove command/vector math helper contracts [COMPLETED]
Priority: High
Primary areas: `tests/test_pmove_movement_fixtures.py`,
`tests/test_pmove_helper_parity.py`,
`references/symbol-maps/qagame.json`, `references/symbol-maps/cgame.json`,
`docs/reverse-engineering/qagame-mapping.md`,
`docs/reverse-engineering/cgame-mapping.md`,
`docs/reverse-engineering/cgame-bg-parity-implementation-plan.md`
Parity estimate: **before 95% -> after 100%** for scoped executable evidence
coverage of the retail `PM_ClipVelocity`, `PM_Accelerate`, `PM_CmdScale`, and
`PM_SetMovementDir` math helpers; repo-wide remains **98%** pending the active
portability/runtime-evidence gaps.

Completed work:

1. Rechecked qagame `PM_ClipVelocity`, `PM_Accelerate`, `PM_CmdScale`, and
   `PM_SetMovementDir` against the cgame twins and the shared source helpers
   reached by walk, air, water, ladder, fly, and noclip movement.
2. Added executable fixtures for overbounce clip branches, acceleration clamp
   and overspeed no-op behavior, zero/axial/2D-diagonal/3D-diagonal command
   scaling, and the full movementDir 0..7 ring plus idle side-strafe snaps.
3. Updated structural tests, symbol-map comments, and mapping notes so the
   command/vector layer beneath the movement leaves is source-validated.

### Task A26: Pin low-level pmove animation helper gates [COMPLETED]
Priority: High
Primary areas: `tests/test_pmove_movement_fixtures.py`,
`tests/test_pmove_helper_parity.py`,
`references/symbol-maps/qagame.json`, `references/symbol-maps/cgame.json`,
`docs/reverse-engineering/qagame-mapping.md`,
`docs/reverse-engineering/cgame-mapping.md`,
`docs/reverse-engineering/cgame-bg-parity-implementation-plan.md`
Parity estimate: **before 96% -> after 100%** for scoped executable evidence
coverage of the retail low-level pmove animation start/continue/force gates;
repo-wide remains **98%** pending the active portability/runtime-evidence gaps.

Completed work:

1. Rechecked qagame `PM_StartTorsoAnim`, `PM_ContinueLegsAnim`, and
   `PM_ForceLegsAnim` against the cgame twins plus the source-local
   `PM_StartLegsAnim` / `PM_ContinueTorsoAnim` call chain they expose.
2. Added executable fixtures for torso toggle-bit writes, `PM_DEAD`
   suppression, legs high-priority timer no-ops, current-animation no-ops,
   torso high-priority timer no-ops, and the `PM_ForceLegsAnim` timer-clear
   behavior before the live/dead start gate.
3. Updated structural tests, symbol-map comments, and mapping notes so the
   animation helpers beneath jump, footstep, weapon, and gesture paths are
   source-validated.

### Task A25: Pin PM_AddEvent and PM_AddTouchEnt queue wiring [COMPLETED]
Priority: High
Primary areas: `tests/test_pmove_movement_fixtures.py`,
`tests/test_pmove_helper_parity.py`,
`references/symbol-maps/qagame.json`, `references/symbol-maps/cgame.json`,
`docs/reverse-engineering/qagame-mapping.md`,
`docs/reverse-engineering/cgame-mapping.md`,
`docs/reverse-engineering/cgame-bg-parity-implementation-plan.md`
Parity estimate: **before 97% -> after 100%** for scoped executable evidence
coverage of the retail pmove predictable-event and touch-entity queue helpers;
repo-wide remains **98%** pending the active portability/runtime-evidence gaps.

Completed work:

1. Rechecked qagame `PM_AddEvent` / `PM_AddTouchEnt` at `0x1002DAF0` /
   `0x1002DB20`, cgame `PM_AddEvent` / `PM_AddTouchEnt` at `0x10001FC0` /
   `0x10001FF0`, and their downstream use from trace/event leaves.
2. Added executable pmove fixtures for the predictable-event two-slot wrap with
   zero event parms and for the touch accumulator's `ENTITYNUM_WORLD`,
   duplicate-suppression, and `MAXTOUCH` cap gates.
3. Updated structural tests, symbol-map comments, and mapping notes so the
   low-level queues behind ground contacts, weapon events, water events, and
   prediction are source-validated.

### Task A24: Pin PM_DropTimers misc and animation timer decay [COMPLETED]
Priority: High
Primary areas: `tests/test_pmove_movement_fixtures.py`,
`tests/test_pmove_helper_parity.py`,
`references/symbol-maps/qagame.json`, `references/symbol-maps/cgame.json`,
`docs/reverse-engineering/qagame-mapping.md`,
`docs/reverse-engineering/cgame-mapping.md`,
`docs/reverse-engineering/cgame-bg-parity-implementation-plan.md`
Parity estimate: **before 96% -> after 100%** for scoped executable evidence
coverage of the retail `PM_DropTimers` misc-time, animation-timer, and
crouch-slide decay behavior; repo-wide remains **98%** pending the active
portability/runtime-evidence gaps.

Completed work:

1. Rechecked qagame `PM_DropTimers` at `0x10031E30`, cgame `PM_DropTimers` at
   `0x10006300`, and the `PmoveSingle` spectator/noclip/tail call sites against
   the committed pmove evidence.
2. Added executable fixture coverage for partial `pm_time` decay, exact/overrun
   misc timer expiry, `PMF_ALL_TIMES` clearing while preserving unrelated flags,
   independent legs/torso animation timer clamps, and the existing crouch-slide
   ground-plane decay gate.
3. Updated structural tests, symbol-map comments, and mapping notes so the
   timer helper is covered as a first-class reconstructed source leaf.

### Task A23: Pin PM_TorsoAnimation ready-idle wiring [COMPLETED]
Priority: High
Primary areas: `tests/test_pmove_movement_fixtures.py`,
`tests/test_pmove_helper_parity.py`,
`references/symbol-maps/qagame.json`, `references/symbol-maps/cgame.json`,
`docs/reverse-engineering/qagame-mapping.md`,
`docs/reverse-engineering/cgame-mapping.md`,
`docs/reverse-engineering/cgame-bg-parity-implementation-plan.md`
Parity estimate: **before 97% -> after 100%** for scoped executable evidence
coverage of the retail `PM_TorsoAnimation` ready-state idle split and inherited
timer/dead-player suppression behavior; repo-wide remains **98%** pending the
active portability/runtime-evidence gaps.

Completed work:

1. Rechecked qagame `PM_TorsoAnimation` at `0x1002DB80`, cgame
   `PM_TorsoAnimation` at `0x10002050`, and the surrounding `PmoveSingle` tail
   calls against the committed Ghidra function lattice.
2. Added executable pmove fixture coverage for the ready gauntlet
   `TORSO_STAND2` branch, the default ready `TORSO_STAND` branch, the
   high-priority torso-timer no-op, the non-ready weaponstate no-op, and the
   inherited `PM_DEAD` animation-start suppression.
3. Updated structural tests, symbol-map comments, and pmove mapping notes so
   the post-weapon torso-idle helper is pinned by source behavior rather than
   only by normalized names.

### Task A22: Pin PM_Animate command-button source behavior [COMPLETED]
Priority: High
Primary areas: `tests/test_pmove_movement_fixtures.py`,
`references/symbol-maps/qagame.json`, `references/symbol-maps/cgame.json`,
`docs/reverse-engineering/qagame-mapping.md`,
`docs/reverse-engineering/cgame-mapping.md`,
`docs/reverse-engineering/cgame-bg-parity-implementation-plan.md`
Parity estimate: **before 96% -> after 100%** for scoped executable evidence
coverage of the retail `PM_Animate` command-button priority, torso-timer gate,
and predictable-event behavior; repo-wide remains **98%** pending the active
portability/runtime-evidence gaps.

Completed work:

1. Rechecked qagame `PM_Weapon`, `PM_Animate`, and `PmoveSingle` tail ordering
   against the committed qagame/cgame Ghidra evidence and found no
   production-source mismatch in the dispatcher tail.
2. Added an executable pmove fixture for the shared `PM_Animate` leaf covering
   gesture priority over voice commands, the long gesture timer plus `EV_TAUNT`
   event, the retail voice-command priority order, the 600 ms voice timer, and
   the existing-torso-timer suppression gate.
3. Updated the symbol maps and reverse-engineering notes so the mapped
   animation/timer helper records the tested source behavior instead of relying
   only on structural matching.

### Task A21: Pin 3D water and ladder pmove leaves with executable fixtures [COMPLETED]
Priority: High
Primary areas: `tests/test_pmove_movement_fixtures.py`,
`references/symbol-maps/qagame.json`, `references/symbol-maps/cgame.json`,
`docs/reverse-engineering/cgame-mapping.md`,
`docs/reverse-engineering/cgame-bg-parity-implementation-plan.md`
Parity estimate: **before 94% -> after 100%** for scoped executable evidence
coverage of the retail water-jump, water-idle, ladder-probe, and ladder-move
leaves; repo-wide remains **98%** pending the active portability/runtime-evidence
gaps.

Completed work:

1. Rechecked qagame `PM_CheckDuck`, `PM_Footsteps`, and `PM_Weapon` against the
   committed qagame/cgame Ghidra decompiles and found no production-source
   mismatch in that tail corridor.
2. Extended the pmove movement fixture harness with deterministic trace and
   pointcontents probes for the adjacent 3D movement leaves.
3. Added executable coverage for the retail `MASK_PLAYERSOLID` + `SURF_LADDER`
   ladder probe, the `0.66 * speed` ladder climb/descent clamp, the two-deep
   water-jump solid-lip/clearance sequence, and the idle `-60` water sink
   fallback through `PM_WaterMove`.

### Task A20: Rewire pmove_ChainJump as the retail jump velocity mode [COMPLETED]
Priority: High
Primary areas: `src/code/game/bg_public.h`,
`src/code/game/bg_pmove.c`, `src/code/game/g_pmove.c`,
`src/code/cgame/cg_servercmds.c`,
`references/symbol-maps/qagame.json`,
`references/symbol-maps/cgame.json`,
`docs/reverse-engineering/qagame-mapping.md`,
`docs/reverse-engineering/cgame-mapping.md`,
`tests/test_pmove_helper_parity.py`,
`tests/test_pmove_movement_fixtures.py`,
`tools/tests/test_pmove_settings_configstring.py`
Parity estimate: **before 97% -> after 100%** for scoped
`pmove_ChainJump` mode transport and takeoff-branch wiring; repo-wide remains
**98%** pending the active portability/runtime-evidence gaps.

Completed work:

1. Rechecked the qagame cvar refresh evidence where `pmove_ChainJump`'s
   integer slot is copied into the cached jump velocity selector, then matched
   it against the recovered `PM_ApplyJumpTakeoff` velocity-mode branches.
2. Promoted `pmove_settings_t.chainJump` from a boolean to an integer mode and
   carried that value through server cvar caching, compact configstring
   serialization, cgame compact parsing, and the legacy JSON fallback parser.
3. Updated the shared takeoff selector so mode `0` disables chain-jump timing,
   mode `1` uses the gradient scaler, mode `2` reaches the additive branch, and
   PMF_AIR_CONTROL still selects the retail air-control additive branch.
4. Added executable pmove fixtures that pin the vertical takeoff results for
   modes `0`, `1`, and `2`, plus the air-control override path.

### Task A19: Restore retail pmove jump-takeoff velocity modes [COMPLETED]
Priority: High
Primary areas: `src/code/game/bg_pmove.c`,
`src/code/game/bg_pmove_jump.h`, `references/symbol-maps/qagame.json`,
`references/symbol-maps/cgame.json`,
`docs/reverse-engineering/qagame-mapping.md`,
`docs/reverse-engineering/cgame-mapping.md`,
`docs/reverse-engineering/cgame-bg-parity-implementation-plan.md`,
`tests/test_jump_velocity_scaling.py`, `tests/test_pmove_helper_parity.py`,
`tests/test_pmove_jump_timing_parity.py`,
`tests/test_crouch_step_prediction.py`,
`tests/test_pmove_validation_fixtures.py`,
`tests/pmove_validation_harness.c`
Parity estimate: **before 96% -> after 100%** for scoped
`PM_ApplyJumpTakeoff` vertical velocity-mode reconstruction; repo-wide remains
**98%** pending the active portability/runtime-evidence gaps.

Completed work:

1. Rechecked qagame `PM_ApplyJumpTakeoff` at `0x1002E2C0`, cgame
   `PM_ApplyJumpTakeoff` at `0x10002790`, and `PM_LoadMoveTuningConstants`
   against the committed HLIL and Ghidra evidence.
2. Replaced the source-only wrapper-side `pmove_StepJumpVelocity` addition with
   the retail takeoff velocity-mode block: normal chain jumps use the gradient
   scaler, PMF_AIR_CONTROL switches to the additive chain/step branch, and
   ramp-jump accumulation applies to vertical velocity before the max clamp.
3. Updated structural, helper, and executable pmove fixtures to pin the
   gradient `cmd.serverTime - jumpTime` behavior and the crouch-step fallback
   velocity produced by the shared takeoff leaf.

### Task A18: Align pmove playerState byte mirrors and item timer stats [COMPLETED]
Priority: High
Primary areas: `src/code/game/q_shared.h`, `src/code/qcommon/msg.c`,
`src/code/game/bg_pmove.c`, `src/code/game/bg_public.h`,
`src/code/game/g_active.c`, `src/code/game/g_team.c`,
`src/code/cgame/cg_newdraw.c`, `references/symbol-maps/qagame.json`,
`references/symbol-maps/cgame.json`,
`docs/reverse-engineering/cgame-bg-parity-implementation-plan.md`,
`tests/test_playerstate_replication.py`,
`tests/test_invulnerability_move_parity.py`,
`tests/test_pmove_movement_fixtures.py`
Parity estimate: **before 92% -> after 100%** for scoped pmove
playerState sidecar layout, command-mirror transport, and progress-backed
holdable timer wiring; repo-wide remains **98%** pending the active
portability/runtime-evidence gaps.

Completed work:

1. Rechecked the retail engine playerState netfield table plus cgame/qagame
   `PmoveSingle` decompiles, confirming `clientNum` at `0x88`, `location` at
   `0x8c`, and signed command mirrors at byte offsets `0x1dc..0x1de`.
2. Rebuilt the shared `playerState_t` prefix to match those offsets, moved
   source-only local sidecars after the retail replicated prefix, and taught
   `MSG_WriteDeltaPlayerstate` / `MSG_ReadDeltaPlayerstate` to encode the
   command mirrors as one-byte fields without clobbering adjacent bytes.
3. Reconstructed the progress-backed holdable timer as retail stats slots
   `STAT_PLAYER_ITEM_TIME_MAX`, `STAT_PLAYER_ITEM_TIME`, and
   `STAT_PLAYER_ITEM_RECHARGE`, including the PmoveSingle recharge clamp and
   the invulnerability move stale/clear gates.
4. Added server location mirroring into `ps.location`, moved the
   `CG_PLAYER_ITEM` overlay to the stats-backed timer slots, and pinned the
   recovered offsets and round-trip behavior with executable replication tests.

### Task A17: Remove source-only replicated ground-trace cache [COMPLETED]
Priority: High
Primary areas: `src/code/game/q_shared.h`, `src/code/qcommon/msg.c`,
`src/code/game/bg_pmove.c`, `references/symbol-maps/qagame.json`,
`references/symbol-maps/cgame.json`,
`docs/reverse-engineering/qagame-mapping.md`,
`docs/reverse-engineering/cgame-mapping.md`,
`docs/reverse-engineering/cgame-bg-parity-implementation-plan.md`,
`tests/test_pmove_helper_parity.py`, `tests/test_pmove_jump_timing_parity.py`
Parity estimate: **before 99% -> after 100%** for scoped
playerState ground-trace layout and `PM_GroundTrace` storage parity; repo-wide
remains **98%** pending the active portability/runtime-evidence gaps.

Completed work:

1. Rechecked cgame `PM_GroundTrace` at `0x100053A0`, qagame `PM_GroundTrace`
   at `0x10030ED0`, and the adjacent `PM_CheckDuck` playerState offset evidence
   against the committed Ghidra decompile.
2. Removed the reconstruction-only `groundTraceHistory*` and
   `groundTraceLatest*` playerState fields plus their delta replication, leaving
   the retail `groundEntityNum` store as the only replicated ground-trace state.
3. Rewired ramp-jump reconstruction to consult the current frame-local
   `pml.groundTrace` normal instead of a non-retail playerState cache, and
   updated symbol-map/docs/tests to pin the layout boundary.

### Task A16: Restore autoHop-only held-jump release wiring [COMPLETED]
Priority: High
Primary areas: `src/code/game/bg_pmove.c`,
`src/code/game/bg_slidemove.c`, `references/symbol-maps/qagame.json`,
`references/symbol-maps/cgame.json`,
`docs/reverse-engineering/qagame-mapping.md`,
`docs/reverse-engineering/cgame-mapping.md`,
`docs/reverse-engineering/cgame-bg-parity-implementation-plan.md`,
`tests/test_pmove_helper_parity.py`, `tests/test_step_jump_gate_parity.py`,
`tests/test_pmove_movement_fixtures.py`
Parity estimate: **before 99% -> after 100%** for scoped
`PM_CheckJump` / `PM_CanStepJump` held-release parity; repo-wide remains
**98%** pending the active portability/runtime-evidence gaps.

Completed work:

1. Rechecked qagame `PM_CanStepJump` at `0x1002E510` and `PM_CheckJump` at
   `0x1002E590`, plus the cgame twins at `0x100029E0` and `0x10002A60`,
   against the committed HLIL and compact pmove-setting parse order.
2. Restored the retail release-bypass split: `autoHop` can bypass the held-jump
   release requirement unless `PMF_REQUIRE_JUMP_RELEASE` is set, while
   `bunnyHop` remains separate movement tuning and no longer bypasses release.
3. Added structural and executable fixture coverage so both normal jump and
   step-jump gates reject held input when only bunny-hop tuning is enabled.

### Task A15: Restore retail step-jump crouch fallback wiring [COMPLETED]
Priority: High
Primary areas: `src/code/game/bg_slidemove.c`,
`src/code/game/bg_pmove.c`, `references/symbol-maps/qagame.json`,
`references/symbol-maps/cgame.json`,
`docs/reverse-engineering/qagame-mapping.md`,
`docs/reverse-engineering/cgame-mapping.md`,
`docs/reverse-engineering/cgame-bg-parity-implementation-plan.md`,
`tests/test_step_jump_gate_parity.py`,
`tests/test_pmove_validation_fixtures.py`,
`tests/pmove_validation_harness.c`,
`tests/test_crouch_step_prediction.py`,
`tests/test_pmove_helper_parity.py`
Parity estimate: **before 98% -> after 100%** for scoped
`PM_StepSlideMove` step-jump gate and crouch-fallback parity; repo-wide
remains **98%** pending the active portability/runtime-evidence gaps.

Completed work:

1. Rechecked qagame `PM_StepSlideMove` at `0x1002EFE0`, cgame
   `PM_StepSlideMove` at `0x100034B0`, and the adjacent
   `PM_CanStepJump` / `PM_CanCrouchStepJump` leaves against the committed
   HLIL plus qagame Ghidra decompile.
2. Replaced the source-only recent-ground-history step-jump delay helper with
   the retail `cmd.serverTime - jumpTime >= jumpTimeDeltaMin` gate.
3. Restored the retail branch split where the general `PM_CanStepJump` recheck
   launches the normal step jump, while the failed-general path can still run
   the crouch-step fallback through `PM_CanCrouchStepJump` and the shrunken-box
   clearance trace.
4. Added direct and executable fixtures for the crouch-step fallback, including
   the no-upmove case that retail permits after the general gate rejects the
   command, and corrected the cgame `PM_StepSlideMove` symbol signature back to
   the one-argument retail boundary.

### Task A14: Restore exact invulnerability pmove timer gate [COMPLETED]
Priority: High
Primary areas: `src/code/game/bg_pmove.c`,
`references/symbol-maps/qagame.json`, `references/symbol-maps/cgame.json`,
`docs/reverse-engineering/cgame-bg-parity-implementation-plan.md`,
`tests/test_invulnerability_move_parity.py`,
`tests/test_pmove_movement_fixtures.py`
Parity estimate: **before 99% -> after 100%** for scoped
`PM_InvulnerabilityMove` timer-gate and holdable-clear parity; repo-wide
remains **98%** pending the active portability/runtime-evidence gaps.

Completed work:

1. Rechecked qagame `PM_InvulnerabilityMove` at `0x1002FA80` and cgame
   `PM_InvulnerabilityMove` at `0x10003F50` against the committed HLIL,
   focusing on the held-item dispatch predicate and timer-collapse block.
2. Restored the exact retail stale-timer gate
   `STAT_PLAYER_ITEM_RECHARGE != 0 && STAT_PLAYER_ITEM_TIME == 0`, allowing
   negative countdown remnants to enter the active decay path instead of being
   filtered by a broader signed range test.
3. Moved the pending holdable-slot clear under the timer clamp and tied it to
   `STAT_PLAYER_ITEM_RECHARGE == 0`, matching the retail collapse point.
4. Added structural and executable pmove coverage for exact zero with a max
   timer, negative decay with a max timer, and zero with no max timer.

### Task A13: Remove source-only flight-thrust pmove override [COMPLETED]
Priority: High
Primary areas: `src/code/game/bg_pmove.c`,
`src/code/game/bg_public.h`, `src/code/game/g_main.c`,
`src/code/game/g_pmove.c`, `src/code/cgame/cg_servercmds.c`,
`references/symbol-maps/qagame.json`, `references/symbol-maps/cgame.json`,
`docs/reverse-engineering/cgame-bg-parity-implementation-plan.md`,
`tests/test_pmove_helper_parity.py`,
`tests/test_game_factory_regen_parity.py`,
`tools/tests/test_pmove_settings_configstring.py`
Parity estimate: **before 99% -> after 100%** for scoped `PM_FlyMove`
and `g_flightThrust` wiring parity; repo-wide remains **98%** pending the
active portability/runtime-evidence gaps.

Completed work:

1. Rechecked qagame `PM_FlyMove` at `0x1002FA20` and cgame `PM_FlyMove` at
   `0x10003EF0` against the committed HLIL; both retail bodies run
   `PM_Friction`, `PM_BuildWishMove3D`, `PM_Accelerate(..., 8)`, and
   `PM_StepSlideMove(qfalse)` without a flight-thrust branch.
2. Confirmed `g_flightThrust` is still a retail qagame cvar table entry with
   default `1200`, but its vmCvar storage is not referenced by the shared pmove
   leaf or pmove settings transport.
3. Removed the source-only `flightThrust` field from `pmove_settings_t`, the
   compact/JSON pmove settings payload extension, and `PM_FlyMove`, while
   keeping the retail cvar registration.
4. Updated symbol-map/docs evidence and regression tests to pin the
   no-override movement leaf and cvar registration boundary.

### Task A12: Restore invulnerability-aware dead pmove collision gate [COMPLETED]
Priority: High
Primary areas: `src/code/game/bg_pmove.c`,
`references/symbol-maps/qagame.json`, `references/symbol-maps/cgame.json`,
`docs/reverse-engineering/qagame-mapping.md`,
`docs/reverse-engineering/cgame-mapping.md`,
`docs/reverse-engineering/cgame-bg-parity-implementation-plan.md`,
`tests/test_pmove_helper_parity.py`,
`tests/test_pmove_movement_fixtures.py`
Parity estimate: **before 99% -> after 100%** for scoped `PmoveSingle`
dead-player trace-mask parity; repo-wide remains **98%** pending the active
portability/runtime-evidence gaps.

Completed work:

1. Rechecked qagame `PmoveSingle` at `0x10031FA0` and cgame `PmoveSingle` at
   `0x10006470` against the committed Ghidra evidence, focusing on the top
   tracemask gate before command-time handling.
2. Restored the retail condition that clears `CONTENTS_BODY` from the pmove
   trace mask only when `STAT_HEALTH <= 0` and `PW_INVULNERABILITY` is not
   active, preserving body collision for invulnerable dead-player states.
3. Updated symbol-map and mapping documentation to record the paired
   health/powerup gate.
4. Added structural and executable pmove coverage for the dispatcher ordering
   and both dead-player tracemask outcomes.

### Task A11: Move pmove profile-bit ownership back to spawn wiring [COMPLETED]
Priority: High
Primary areas: `src/code/game/g_client.c`, `src/code/game/g_pmove.c`,
`src/code/game/bg_pmove.c`, `src/code/game/g_local.h`,
`references/symbol-maps/qagame.json`, `references/symbol-maps/cgame.json`,
`docs/reverse-engineering/qagame-mapping.md`,
`docs/reverse-engineering/cgame-bg-parity-implementation-plan.md`,
`tests/test_pmove_helper_parity.py`, `tests/test_pmove_crouch_time_parity.py`,
`tests/test_pmove_crouch_slide_friction_parity.py`,
`tests/pmove_validation_harness.c`
Parity estimate: **before 99% -> after 100%** for scoped pmove
profile-flag ownership and prediction wiring parity; repo-wide remains
**98%** pending the active portability/runtime-evidence gaps.

Completed work:

1. Rechecked qagame `ClientSpawn` at `0x1003BC30` and shared
   `PmoveSingle` at qagame `0x10031FA0` / cgame `0x10006470` against the
   committed Ghidra evidence.
2. Restored the retail ownership split where spawn seeds
   `PMF_CROUCH_SLIDE`, `PMF_DOUBLE_JUMP`, and `PMF_AIR_CONTROL` from the
   active movement profile, while `PmoveSingle` consumes those replicated
   bits instead of deriving them from settings every frame.
3. Rewired crouch-slide friction and air double-jump acceptance to respect
   the profile flags directly, preserving the existing tuning fields for
   friction strength, jump velocity, and prediction-side settings.
4. Updated symbol-map/docs evidence and regression fixtures to lock the spawn
   profile helper, shared pmove dispatcher order, crouch-slide friction gate,
   and double-jump latch behavior.

### Task A10: Reconstruct compact pmove settings configstring wiring [COMPLETED]
Priority: High
Primary areas: `src/code/game/g_pmove.c`,
`src/code/cgame/cg_servercmds.c`,
`references/symbol-maps/cgame.json`,
`docs/reverse-engineering/cgame-mapping.md`,
`docs/reverse-engineering/cgame-bg-parity-implementation-plan.md`,
`tests/test_pmove_helper_parity.py`,
`tools/tests/test_pmove_settings_configstring.py`
Parity estimate: **before 99% -> after 100%** for scoped pmove
settings transport/source wiring parity; repo-wide remains **98%** pending
the active portability/runtime-evidence gaps.

Completed work:

1. Rechecked `CG_ParsePmoveConfigString` at `0x10048F30` against the committed
   cgame Ghidra/HLIL evidence and mapped the retail 33-token compact numeric
   payload order, including the non-negative clamps on the recovered
   threshold and velocity fields.
2. Replaced the reconstruction-only JSON `CS_PMOVE_SETTINGS` server payload
   with the compact retail token stream from `G_PmoveSerializeSettings`, while
   retaining current source-only fields as a trailing extension after the
   retail core.
3. Rewired cgame parsing so compact payloads take the retail path, JSON remains
   only as a backward-compatible fallback for older local artifacts, and
   reload timing stays owned by the dedicated compact reload configstring.
4. Updated symbol-map/docs evidence and regression tests to pin the recovered
   token order, clamp behavior, extension boundary, and JSON fallback.

### Task A9: Contain inherited Quake III service endpoints behind the online-services policy [COMPLETED]
Priority: High
Primary areas: `src/code/qcommon/qcommon.h`, `src/code/client/cl_main.c`,
`src/code/server/`, `src/common/platform/platform_config.h`,
`docs/reverse-engineering/network-handshake.md`,
`docs/reverse-engineering/quakelive_steam_mapping_round_73.md`,
`docs/steam_platform_abstraction.md`, `tests/test_platform_services.py`
Parity estimate: **before 98% -> after 98%** repo-wide; scoped
network-service policy parity improves from **82% -> 94%**.

Completed work:

1. Confirmed from the retail Quake Live evidence that the retained game port
   remains `27960`, while the inherited Quake III update, master, and
   authorize hostnames are not retail QL Steam service evidence.
2. Added `QL_ENABLE_LEGACY_Q3_SERVICES`, defaulted it off, and forced it off
   whenever `QL_BUILD_ONLINE_SERVICES=0`, so default builds no longer resolve
   the retired `*.quake3arena.com` hosts.
3. Kept `PORT_SERVER` and the LAN server-port scan range unconditional, while
   quarantining `UPDATE_SERVER_NAME`, `MASTER_SERVER_NAME`,
   `AUTHORIZE_SERVER_NAME`, `PORT_MASTER`, `PORT_UPDATE`, and
   `PORT_AUTHORIZE` behind the legacy-service gate.
4. Restored the retail `sv_master` heartbeat gate as `sv_masterAdvertise` and
   left the older `sv_master1` through `sv_master5` array as an explicitly
   configured compatibility lane.
5. Replaced default build calls into the legacy Q3 MOTD, master query,
   authorize, getIpAuthorize, and remote-ban flows with policy-visible stubs
   or local challenge responses, and covered the boundary with focused tests.

### Task A8: Re-audit renderer source and host wiring, then remove the non-retail FontStash prebuild [COMPLETED]
Priority: High
Primary areas: `src/code/renderer/tr_font.c`,
`docs/reverse-engineering/renderer-wiring-reverse-engineering-round-2026-05-20.md`,
`docs/reverse-engineering/renderer-full-parity-audit-and-implementation-plan-2026-04-09.md`,
`docs/reverse-engineering/renderer-host-text-core-ownership-2026-04-10.md`,
`docs/platform/retail-font-stack.md`,
`tests/test_renderer_host_text_core_parity.py`
Parity estimate: **before 99% -> after 100%** for scoped renderer
source/wiring parity; repo-wide remains **98%** pending fresh runtime evidence.

Completed work:

1. Re-ran the renderer source/wiring evidence walk against the committed
   `quakelive_steam.exe` Ghidra/HLIL corpus, current symbol aliases, renderer
   parity gates, and the tracked renderer/module runtime artifacts.
2. Confirmed that scene, world/model, shader, post-process, memory-image,
   export ABI, Win32 host glue, and native UI/cgame host-text import ownership
   still do not need a new renderer file-level gap note.
3. Isolated one hidden retained-host-text mismatch: source eagerly prebuilt
   every byte glyph for every retained FontStash face during
   `R_InitFontStash`, while retail HLIL creates the atlas, installs
   `R_fonsErrorCallback`, loads the five faces, and leaves glyph population
   lazy through the draw/measure cache path.
4. Removed the eager `R_PrebuildFontStashAtlas` startup sweep from
   `tr_font.c`, added focused source/docs coverage so the lazy retained-atlas
   ownership stays pinned, and documented that the older
   `R_fonsErrorCallback` retail-module artifact is now stale `RW-G04`
   evidence until the module runtime probe is rerun.
5. Followed up on the same FontStash overflow lane by preserving old atlas
   pixels and cached glyph UVs during `R_ResizeFontStashAtlas` expansion,
   leaving full glyph-cache clearing reserved for the retail max-size flush
   path.
6. Matched the retail `*fontstash` texture callback by uploading the retained
   one-byte atlas through `GL_ALPHA` texture storage instead of expanding it
   into RGBA for every atlas refresh.
7. Restored the retail renderer export ABI shape around `GetRefAPI`: source now
   uses `REF_API_VERSION == 9`, keeps the legacy post-`ModelBounds` font slot
   as a no-op, preserves `SetColor` immediately after the loading-view bridge,
   and leaves `postprocess_restart` at the private tail offset recovered from
   the `0x9c` retail export table.

### Task A7: Run the source-file parity audit campaign and isolate the remaining file-level gaps [COMPLETED]
Priority: High
Primary areas: `docs/reverse-engineering/source-file-parity-ledger-2026-04-22.md`,
`docs/reverse-engineering/source-file-parity-audit-plan-2026-04-22.md`,
`docs/reverse-engineering/source-file-gap-notes/`,
`tools/reverse-engineering/generate_source_file_audit.py`, all tracked
`src/` source trees
Parity estimate: **before 96% -> after 96%**

Completed work:

1. Closed the full source-file parity audit campaign by walking all `567`
   tracked source entries across the primary runtime, compatibility-only,
   and secondary support trees in the generated plan order.
2. Kept inherited subsystem closure as the baseline while isolating concrete
   file-level ownership only where the current evidence supported it, which
   left the repo-wide source-file gap register concentrated in the seeded
   `RW-G01` and `RW-G02` note set instead of reopening already-bounded
   surfaces.
3. Extended the source-file audit generator and its regression coverage so
   completed tranche metadata, compatibility wording, function-count fixes,
   and Phase 4 secondary-source summaries all survive regeneration on the
   current worktree.
4. Regenerated the source-file ledger, source-file audit plan, gap-note
   index/readme, and historical audit index so the campaign snapshot is now
   self-consistent and no pending tranche remains in the generated plan.
5. Returned the top-level queue to the remaining repo-wide workstreams, with
   the online-service compatibility boundary now back at the head of the
   active task list.

### Task A7p: Audit `src/q3radiant` function-by-function and isolate file-level gap ownership [COMPLETED]
Priority: High
Primary areas: `docs/reverse-engineering/source-file-parity-ledger-2026-04-22.md`,
`docs/reverse-engineering/source-file-parity-audit-plan-2026-04-22.md`,
`src/q3radiant/`,
`tests/test_source_file_audit_generator.py`,
`tools/reverse-engineering/generate_source_file_audit.py`
Parity estimate: **before 96% -> after 96%**

Completed work:

1. Completed the final Phase 4 secondary-source tranche in the source-file
   campaign by walking all `97` tracked files under `src/q3radiant`
   against the current generated ledger and the repo-wide parity register.
2. Confirmed that this tranche does not open any new file-level gap notes:
   the retained Radiant editor shell, plugin bridge, OpenGL host glue, and
   bundled spline/editor helper sources remain bounded secondary support
   trees on current evidence rather than concrete repo-wide gap owners.
3. Extended the source-file audit generator and its regression coverage so
   completed metadata for `src/q3radiant` and the checked final Phase 4
   plan item now survive regeneration too.
4. Re-ran the refreshed generator suite (`20 passed`) and regenerated the
   source-file campaign docs so the final Phase 4 tranche is now recorded
   as complete in the generated outputs.
5. Closed the currently enumerated secondary-source file-walk queue in the
   generated source-file audit plan, leaving no remaining pending Phase 4
   tranche in that campaign snapshot.

### Task A7o: Audit `src/lcc` and `src/libs` function-by-function and isolate file-level gap ownership [COMPLETED]
Priority: High
Primary areas: `docs/reverse-engineering/source-file-parity-ledger-2026-04-22.md`,
`docs/reverse-engineering/source-file-parity-audit-plan-2026-04-22.md`,
`src/lcc/`,
`src/libs/`,
`tests/test_source_file_audit_generator.py`,
`tools/reverse-engineering/generate_source_file_audit.py`
Parity estimate: **before 96% -> after 96%**

Completed work:

1. Completed the third Phase 4 secondary-source tranche in the source-file
   campaign by walking all `99` tracked files across `src/lcc` and
   `src/libs` against the current generated ledger and the repo-wide parity
   register.
2. Confirmed that this tranche does not open any new file-level gap notes:
   the retained LCC compiler/preprocessor/code-generator and bundled test
   sources under `src/lcc`, plus the tracked command-line, JPEG, and pak
   helper sources under `src/libs`, remain bounded secondary support trees
   on current evidence rather than concrete repo-wide gap owners.
3. Extended the source-file audit generator and its regression coverage so
   completed metadata for `src/lcc`, `src/libs`, and the checked third
   Phase 4 plan item now survive regeneration too.
4. Re-ran the refreshed generator suite (`19 passed`) and regenerated the
   source-file campaign docs so the third Phase 4 tranche is now recorded
   as complete in the generated outputs.
5. Advanced the file-walk queue so the remaining Phase 4 target is now the
   secondary-source tranche covering `src/q3radiant/`.

### Task A7n: Audit `src/game`, `src/q3asm`, and `src/q3map` function-by-function and isolate file-level gap ownership [COMPLETED]
Priority: High
Primary areas: `docs/reverse-engineering/source-file-parity-ledger-2026-04-22.md`,
`docs/reverse-engineering/source-file-parity-audit-plan-2026-04-22.md`,
`src/game/`,
`src/q3asm/`,
`src/q3map/`,
`tests/test_source_file_audit_generator.py`,
`tools/reverse-engineering/generate_source_file_audit.py`
Parity estimate: **before 96% -> after 96%**

Completed work:

1. Completed the second Phase 4 secondary-source tranche in the source-file
   campaign by walking all `40` tracked files across `src/game`,
   `src/q3asm`, and `src/q3map` against the current generated ledger and the
   repo-wide parity register.
2. Confirmed that this tranche does not open any new file-level gap notes:
   the retained gameplay config helpers and standalone fixture/support
   sources under `src/game`, the `q3asm` bytecode assembler sources, and the
   `q3map` compile/light/vis toolchain all remain bounded secondary support
   trees on current evidence rather than concrete repo-wide gap owners.
3. Extended the source-file audit generator and its regression coverage so
   completed metadata for `src/game`, `src/q3asm`, `src/q3map`, and the
   checked second Phase 4 plan item now survive regeneration too.
4. Re-ran the refreshed generator suite plus focused `src/game` helper
   coverage (`41 passed` across the source-audit, factory-config,
   scoreboard-helper, and tournament-queue suites) so this tranche stays
   recorded as complete on the current worktree.
5. Regenerated the source-file campaign docs so the second Phase 4 tranche is
   now recorded as complete in the generated outputs, and the next file-walk
   target is now the secondary-source tranche covering `src/lcc/` and
   `src/libs/`.

### Task A7m: Audit `src/code/bspc`, `src/code/jpeg-6`, and `src/code/splines` function-by-function and isolate file-level gap ownership [COMPLETED]
Priority: High
Primary areas: `docs/reverse-engineering/source-file-parity-ledger-2026-04-22.md`,
`docs/reverse-engineering/source-file-parity-audit-plan-2026-04-22.md`,
`src/code/bspc/`,
`src/code/jpeg-6/`,
`src/code/splines/`,
`tests/test_source_file_audit_generator.py`,
`tools/reverse-engineering/generate_source_file_audit.py`
Parity estimate: **before 96% -> after 96%**

Completed work:

1. Completed the first Phase 4 secondary-source tranche in the source-file
   campaign by walking all `106` tracked files across `src/code/bspc`,
   `src/code/jpeg-6`, and `src/code/splines` against the current repo-wide
   ledger and the generated source-file register.
2. Corrected the audit generator’s function extractor so the tranche now
   counts libjpeg macro-style definitions and retained splines C++ method
   definitions instead of leaving most of `jpeg-6` and parts of the splines
   tree as misleading zero-function placeholders in the ledger.
3. Confirmed that this tranche does not open any new file-level gap notes:
   the retained BSPC compiler/AAS toolchain, bundled `jpeg-6` support
   sources, and legacy splines helper/editor sources remain bounded
   secondary trees on current evidence rather than concrete repo-wide gap
   owners.
4. Extended the source-file audit generator and its regression coverage so
   completed secondary-section metadata and the checked first Phase 4 plan
   item now survive regeneration too; the refreshed generator suite passes
   on the current worktree (`17 passed`).
5. Regenerated the source-file campaign docs so the first Phase 4 tranche is
   now recorded as complete in the generated outputs, and the next file-walk
   target is now the secondary-source tranche covering `src/game/`,
   `src/q3asm/`, and `src/q3map/`.

### Task A7l: Audit `src/code/null` function-by-function and isolate file-level gap ownership [COMPLETED]
Priority: High
Primary areas: `docs/reverse-engineering/source-file-parity-ledger-2026-04-22.md`,
`docs/reverse-engineering/source-file-parity-audit-plan-2026-04-22.md`,
`docs/reverse-engineering/source-file-gap-notes/`,
`src/code/null/`,
`docs/reverse-engineering/repo-wide-parity-audit-2026-04-21.md`,
`tests/test_non_windows_portability.py`,
`tools/reverse-engineering/generate_source_file_audit.py`
Parity estimate: **before 96% -> after 96%**

Completed work:

1. Completed the next compatibility tranche in the source-file campaign by
   walking all `7` tracked `src/code/null` entries against the current
   repo-wide parity ledger, the existing `RW-G02` portability notes, and the
   focused non-Windows portability regression lane.
2. Isolated `src/code/null/null_glimp.c` as an additional concrete `RW-G02`
   owner because the null renderer host still consists of no-op
   `GLimp_*` entry points plus a `QGL_Init()` path that returns success
   without loading a real GL backend, while `null_main.c`, `null_client.c`,
   `null_input.c`, and `null_snddma.c` remain the other null-runtime owners
   already tracked in dedicated notes.
3. Confirmed that no further null file needs a new file-level gap note in
   this tranche: `null_net.c` and `mac_net.c` remain bounded loopback helper
   surfaces on current evidence rather than newly isolated repo-wide
   blockers, so they are now explicitly recorded as current compatibility
   function-walk completions.
4. Extended the source-file audit generator and its regression coverage so a
   completed null compatibility tranche, the newly isolated `null_glimp.c`
   note, and the walked-complete helper rows all survive regeneration; the
   refreshed generator plus non-Windows portability suites now pass
   together (`20 passed`).
5. Regenerated the source-file campaign docs so Phase 3 is now fully closed
   in the generated outputs, and the next file-walk target is now the first
   Phase 4 secondary-source tranche covering `src/code/bspc/`,
   `src/code/jpeg-6/`, and `src/code/splines/`.

### Task A7k: Audit `src/code/unix` function-by-function and isolate file-level gap ownership [COMPLETED]
Priority: High
Primary areas: `docs/reverse-engineering/source-file-parity-ledger-2026-04-22.md`,
`docs/reverse-engineering/source-file-parity-audit-plan-2026-04-22.md`,
`src/code/unix/`,
`docs/reverse-engineering/repo-wide-parity-audit-2026-04-21.md`,
`tests/test_non_windows_portability.py`,
`tools/reverse-engineering/generate_source_file_audit.py`
Parity estimate: **before 96% -> after 96%**

Completed work:

1. Completed the next compatibility tranche in the source-file campaign by
   walking all `10` tracked `src/code/unix` entries against the current
   repo-wide parity ledger, the existing `RW-G02` portability notes, and the
   focused non-Windows portability regression lane.
2. Confirmed that no additional `src/code/unix` file needs a new file-level
   gap note: the existing `RW-G02` ownership remains concentrated in
   `unix_main.c`, `linux_glimp.c`, `linux_snd.c`, and `linux_joystick.c`,
   while `linux_common.c`, `linux_qgl.c`, `linux_signals.c`, `unix_net.c`,
   `unix_shared.c`, and `vm_x86.c` are now explicitly recorded as current
   function-walk completions on present evidence.
3. Extended the source-file audit generator and its regression coverage so a
   completed compatibility tranche now survives regeneration too, including
   the checked Phase 3 Unix plan item, the compatibility-specific ledger row
   wording, and the retained `RW-G02` note ownership inside the still-open
   portability lane.
4. Re-ran the generator and the focused portability coverage (`18 passed`
   across the generator and non-Windows suites) so the Unix tranche now stays
   recorded as complete in the generated docs, and the next file-walk target
   is now the compatibility-only `src/code/null` tranche at the head of the
   remaining queue.

### Task A7j: Audit `src/code/ui` function-by-function and isolate file-level gap ownership [COMPLETED]
Priority: High
Primary areas: `docs/reverse-engineering/source-file-parity-ledger-2026-04-22.md`,
`docs/reverse-engineering/source-file-parity-audit-plan-2026-04-22.md`,
`src/code/ui/`,
`docs/reverse-engineering/ui-full-parity-audit-and-implementation-plan-2026-04-05.md`,
`tools/reverse-engineering/generate_source_file_audit.py`
Parity estimate: **before 96% -> after 96%**

Completed work:

1. Completed the next source-file campaign tranche by walking all `9`
   tracked `src/code/ui` entries against the refreshed strict-retail UI
   audit, the focused UI parity lane, and the current repo-wide gap ledger.
2. Confirmed that no `src/code/ui` file needs a new file-level gap note:
   the current UI closure still holds on current evidence, the focused UI
   suite is green (`56 passed`, `2 skipped`), the clean read-only `src/ui`
   runtime-panel parity proof still bounds the menu/data payload, and the
   read-only tree therefore did not require or permit a source correction in
   this tranche.
3. Extended the source-file audit generator and its regression coverage so
   completed read-only tranche metadata now survives regeneration too,
   including the UI checklist state, the read-only ledger row wording, and
   the UI tranche summary in the generated audit docs.
4. Regenerated the source-file campaign docs from the hardened generator so
   the UI tranche is now recorded as complete beside the earlier runtime
   walks, and the next file-walk target is now the compatibility-only
   `src/code/unix` tranche at the head of the remaining queue.

### Task A7i: Audit `src/code/cgame` function-by-function and isolate file-level gap ownership [COMPLETED]
Priority: High
Primary areas: `docs/reverse-engineering/source-file-parity-ledger-2026-04-22.md`,
`docs/reverse-engineering/source-file-parity-audit-plan-2026-04-22.md`,
`src/code/cgame/`,
`docs/reverse-engineering/game-module-parity-audit-and-implementation-plan-2026-04-10.md`,
`tools/reverse-engineering/generate_source_file_audit.py`
Parity estimate: **before 96% -> after 96%**

Completed work:

1. Completed the next module/gameplay tranche in the source-file campaign by
   walking all `22` tracked `src/code/cgame` entries against the refreshed
   strict-retail module audit, the focused `cgame` parity lane, and the
   current repo-wide gap ledger.
2. Confirmed that no `src/code/cgame` file needs a new file-level gap note:
   the current module closure still holds on current evidence, the focused
   `cgame` suite is green (`199 passed`, `1 skipped`), and the shared native
   export-helper certification still bounds the tree without needing a source
   correction in this tranche.
3. Hardened the source-file audit generator so completed tranche checkmarks,
   section result notes, and current-walk ledger rows now survive regeneration
   instead of reverting already-audited runtime sections back to the default
   pending wording; `--help` is also now a safe no-write path.
4. Regenerated the source-file campaign docs from the hardened generator so
   the corrected `cgame` function counts and the previously completed runtime
   tranches live in one durable output again, and the next file-walk target
   is now the read-only `src/code/ui` tranche at the head of the remaining
   module/gameplay queue.

### Task A7h: Audit `src/code/game` function-by-function and isolate file-level gap ownership [COMPLETED]
Priority: High
Primary areas: `docs/reverse-engineering/source-file-parity-ledger-2026-04-22.md`,
`docs/reverse-engineering/source-file-parity-audit-plan-2026-04-22.md`,
`src/code/game/`,
`docs/reverse-engineering/game-module-parity-audit-and-implementation-plan-2026-04-10.md`,
`tools/reverse-engineering/generate_source_file_audit.py`
Parity estimate: **before 96% -> after 96%**

Completed work:

1. Hardened the source-file audit generator again so it now ignores
   control-flow keywords such as `if`, `for`, `while`, and `switch`, which
   keeps the source-file campaign counts aligned with real Quake-style C
   definitions in the `src/code/game` tranche instead of overcounting
   control blocks.
2. Completed the next module/gameplay tranche in the source-file campaign by
   walking all `45` tracked `src/code/game` entries against the refreshed
   strict-retail module audit, the qagame retail gate, and the current
   repo-wide gap ledger.
3. Closed the concrete issues surfaced during the walk without opening a new
   persistent gap note: `BG_CanGrabWeaponItem()` now matches the retained
   retail world-weapon regrab gate, the Attack & Defend lifecycle/frame hooks
   are explicit in the module-side source layout again, and the standalone
   auto-shuffle countdown harness now uses the shared compiler-discovery path
   on Windows instead of assuming `gcc`.
4. Confirmed that no `src/code/game` file needs a new file-level gap note:
   the current gameplay/module closure still holds on current evidence, and
   the newer auto-shuffle/countdown, Clan Arena shuffle, Race, ready-up, and
   shared `pmove` coverage all remain bounded inside the already-closed
   module register rather than opening a new repo-wide gap family.
5. Recorded the result directly in the source-file campaign docs so the game
   rows now distinguish current function-walk completion from the
   still-pending module trees, and the next file-walk target is now the
   `src/code/cgame` tranche at the head of the remaining module/gameplay
   queue.

### Task A7g: Audit `src/code/botlib` function-by-function and isolate file-level gap ownership [COMPLETED]
Priority: High
Primary areas: `docs/reverse-engineering/source-file-parity-ledger-2026-04-22.md`,
`docs/reverse-engineering/source-file-parity-audit-plan-2026-04-22.md`,
`src/code/botlib/`,
`docs/reverse-engineering/botlib-internal-parity-audit-and-implementation-plan-2026-04-10.md`,
`tools/reverse-engineering/generate_source_file_audit.py`
Parity estimate: **before 96% -> after 96%**

Completed work:

1. Fixed the source-file audit generator so it now counts Quake-style
   brace-on-next-line C function definitions, which restores accurate
   function-count coverage for the `src/code/botlib` tranche instead of
   leaving most files reported as zero-function placeholders.
2. Completed the next primary-runtime tranche in the source-file campaign by
   walking all `28` tracked `src/code/botlib` entries against the dedicated
   botlib internal audit, the retained mapping-round `61` bridge/import
   ownership, and the current repo-wide gap ledger.
3. Confirmed that no `src/code/botlib` file needs a new file-level gap note:
   the retained bridge/import closures and the deterministic
   AAS/reachability/goal-state proof lane still bound the tree on current
   evidence, while the remaining live-map or gameplay-tuning nuance stays
   explicitly outside the repo-wide/file-level gap register.
4. Recorded the result directly in the source-file campaign docs so the
   botlib rows now distinguish current function-walk completion from the
   still-pending module and compatibility trees, and the next file-walk
   target is now the `src/code/game` tranche at the head of the remaining
   module/gameplay queue.

### Task A7f: Audit `src/code/win32` function-by-function and isolate file-level gap ownership [COMPLETED]
Priority: High
Primary areas: `docs/reverse-engineering/source-file-parity-ledger-2026-04-22.md`,
`docs/reverse-engineering/source-file-parity-audit-plan-2026-04-22.md`,
`src/code/win32/`,
`docs/reverse-engineering/platform-specific-engine-parity-audit-and-implementation-plan-2026-04-16.md`
Parity estimate: **before 96% -> after 96%**

Completed work:

1. Completed the next primary-runtime tranche in the source-file campaign by
   walking all `11` tracked `src/code/win32` entries against the closed
   strict-retail Windows platform audit, renderer host-glue evidence, and the
   current repo-wide gap ledger.
2. Confirmed that no `src/code/win32` file needs a new file-level gap note:
   the retained clipboard, raw-input, loading-window, renderer-host glue, and
   `win_glimp.c` pixel-format closures still hold on current evidence, and no
   file in this tree currently owns a repo-wide gap family.
3. Recorded the result directly in the source-file campaign docs so the
   Win32 rows now distinguish current function-walk completion from the
   still-pending runtime trees, without reopening the closed strict-retail
   Windows platform register.
4. Narrowed `A7` procedurally again: the next file-walk target is now the
   `src/code/botlib` tranche at the head of the remaining strict-retail
   engine-core queue.

### Task A7e: Audit `src/code/renderer` function-by-function and isolate file-level gap ownership [COMPLETED]
Priority: High
Primary areas: `docs/reverse-engineering/source-file-parity-ledger-2026-04-22.md`,
`docs/reverse-engineering/source-file-parity-audit-plan-2026-04-22.md`,
`src/code/renderer/`,
`docs/reverse-engineering/renderer-full-parity-audit-and-implementation-plan-2026-04-09.md`
Parity estimate: **before 96% -> after 96%**

Completed work:

1. Completed the next primary-runtime tranche in the source-file campaign by
   walking all `23` tracked `src/code/renderer` entries against the closed
   strict-retail renderer audit, mapping notes, and the current repo-wide
   gap ledger.
2. Confirmed that no `src/code/renderer` file needs a new file-level gap note:
   the retained export, image, post-process, scene/runtime, font, and
   host-text closures still hold on current evidence, and the then-bounded
   `R_fonsErrorCallback` module-runtime blocker remained classified under
   `RW-G04` evidence freshness rather than as a new renderer source-gap owner.
   The later 2026-05-20 renderer wiring pass patched the source-side eager
   FontStash prebuild behind that stale artifact.
3. Recorded the result directly in the source-file campaign docs so the
   renderer rows now distinguish current function-walk completion from the
   still-pending runtime trees, without reopening the closed strict-retail
   renderer register.
4. Narrowed `A7` procedurally again: the next file-walk target is now the
   `src/code/win32` tranche at the head of the remaining strict-retail
   engine-core queue.

### Task A7d: Audit `src/code/server` function-by-function and isolate file-level gap ownership [COMPLETED]
Priority: High
Primary areas: `docs/reverse-engineering/source-file-parity-ledger-2026-04-22.md`,
`docs/reverse-engineering/source-file-parity-audit-plan-2026-04-22.md`,
`src/code/server/`,
`docs/reverse-engineering/server-full-parity-audit-and-implementation-plan-2026-04-10.md`
Parity estimate: **before 96% -> after 96%**

Completed work:

1. Completed the next primary-runtime tranche in the source-file campaign by
   walking all `11` tracked `src/code/server` entries against the closed
   strict-retail server audit, mapping notes, and the current repo-wide
   gap ledger.
2. Confirmed that no new `src/code/server` file-level owners need opening
   beyond the already-seeded `RW-G01` note for `sv_rankings.c`; the retained
   Steam GameServer/auth/stats and `idZMQ` publication/runtime owners remain
   closed on current evidence.
3. Recorded the result directly in the source-file campaign docs so the
   server rows now distinguish current function-walk completion from the
   still-pending runtime trees, while keeping the bounded rankings ownership
   explicit in the existing `sv_rankings.c` gap note instead of reopening the
   closed strict-retail server register.
4. Narrowed `A7` procedurally again: the next file-walk target is now the
   `src/code/renderer` tranche at the head of the remaining strict-retail
   engine-core queue.

### Task A7c: Audit `src/code/client` function-by-function and isolate file-level gap ownership [COMPLETED]
Priority: High
Primary areas: `docs/reverse-engineering/source-file-parity-ledger-2026-04-22.md`,
`docs/reverse-engineering/source-file-parity-audit-plan-2026-04-22.md`,
`src/code/client/`,
`docs/reverse-engineering/client-full-parity-audit-and-implementation-plan-2026-04-09.md`
Parity estimate: **before 96% -> after 96%**

Completed work:

1. Completed the next primary-runtime tranche in the source-file campaign by
   walking all `22` tracked `src/code/client` entries against the closed
   strict-retail client audit, mapping notes, and the current repo-wide
   gap ledger.
2. Confirmed that no new `src/code/client` file-level owners need opening
   beyond the already-seeded `RW-G01` notes for `ql_auth.c` and
   `cl_steam_resources.c`.
3. Recorded the result directly in the source-file campaign docs so the
   client rows now distinguish current function-walk completion from the
   still-pending runtime trees, while keeping the bounded online-services
   ownership explicit in the two existing client gap notes instead of
   reopening the closed strict-retail client register.
4. Narrowed `A7` procedurally again: the next file-walk target is now the
   `src/code/server` tranche at the head of the remaining strict-retail
   engine-core queue.

### Task A7b: Audit `src/code/qcommon` function-by-function and isolate file-level gap ownership [COMPLETED]
Priority: High
Primary areas: `docs/reverse-engineering/source-file-parity-ledger-2026-04-22.md`,
`docs/reverse-engineering/source-file-parity-audit-plan-2026-04-22.md`,
`src/code/qcommon/`,
`docs/reverse-engineering/qcommon-full-parity-audit-and-implementation-plan-2026-04-10.md`
Parity estimate: **before 96% -> after 96%**

Completed work:

1. Completed the next primary-runtime tranche in the source-file campaign by
   walking all `19` tracked `src/code/qcommon` entries against the closed
   strict-retail qcommon audit, mapping rounds, and the current repo-wide
   ledger.
2. Confirmed that no new `src/code/qcommon` file-level owners need opening:
   the current strict-retail qcommon register remains closed, and no
   additional repo-wide gap family is concretely owned by a qcommon source
   file on the current worktree.
3. Recorded the result directly in the source-file campaign docs so the
   qcommon rows now distinguish current function-walk completion from the
   still-pending runtime trees, while keeping `vm_x86.c` classified as the
   already-bounded compatibility carry beneath the closed `vm.c`
   host-selection seam.
4. Narrowed `A7` procedurally again: the next file-walk target is now the
   `src/code/client` tranche at the head of the remaining strict-retail
   engine-core queue.

### Task A7a: Audit `src/common` function-by-function and isolate file-level gap ownership [COMPLETED]
Priority: High
Primary areas: `docs/reverse-engineering/source-file-parity-ledger-2026-04-22.md`,
`docs/reverse-engineering/source-file-parity-audit-plan-2026-04-22.md`,
`src/common/`, `src/common/platform/`
Parity estimate: **before 96% -> after 96%**

Completed work:

1. Completed the first primary-runtime tranche in the new source-file campaign
   by walking all `18` tracked `src/common` entries against the current
   engine-wide closure and repo-wide gap ledgers.
2. Confirmed that no new `src/common` file-level owners need opening beyond
   the already-seeded `RW-G01` notes for `platform_config.h`,
   `platform_services.c`, and the bounded auth backend shims.
3. Recorded the result directly in the source-file campaign docs so the
   `src/common` rows now distinguish current function-walk completion from the
   still-pending primary-runtime trees, while keeping `platform_steamworks.c`
   classified as a retained Steamworks wrapper surface gated by policy rather
   than as a newly opened repo-wide gap owner.
4. Narrowed `A7` procedurally: the next file-walk target is now the
   `src/code/qcommon` tranche at the head of the remaining strict-retail
   engine-core queue.

### Task A4i: Replace the Unix `Sys_CheckCD()` unconditional pass with a bounded data-root probe [COMPLETED]
Priority: Medium
Primary areas: `src/code/unix/unix_main.c`,
`tests/test_non_windows_portability.py`,
`docs/platform/toolchain-matrix.md`, `docs/build/linux-glibc-32bit.md`
Parity estimate: **before 96% -> after 96%**

Completed work:

1. Replaced the Unix `Sys_CheckCD()` `return qtrue;` placeholder with a
   bounded Quake-data probe that now scans the configured `fs_basepath`,
   `fs_cdpath`, default install roots, and current working directory for
   `baseq3/default.cfg`, `pak00.pk3`, or `pak0.pk3` before reporting success.
2. Kept the reconstructed lane deliberately compatibility-scoped rather than
   over-claiming retail parity: the probe is a coarse host-side data-root
   guard for existing engine callers such as `SV_BotInitBotLib()`, not a full
   filesystem bootstrap replacement.
3. Expanded the focused non-Windows portability suite so the new root list,
   accepted asset markers, and `baseq3` path contract are source-pinned
   alongside the previously restored low-memory, symbol-compare, release-marker,
   profiling, and clipboard seams.
4. Narrowed `RW-G02` again: the remaining portability debt is now even more
   cleanly concentrated in the absent real Unix renderer/audio/input host
   modernization and broader non-Windows validation breadth, not in an
   unconditional Unix content-root success stub.

### Task A4h: Restore a bounded Unix clipboard compatibility path [COMPLETED]
Priority: Medium
Primary areas: `src/code/unix/unix_main.c`,
`tests/test_non_windows_portability.py`,
`docs/platform/toolchain-matrix.md`, `docs/build/linux-glibc-32bit.md`
Parity estimate: **before 96% -> after 96%**

Completed work:

1. Replaced the bare Unix `Sys_GetClipboardData()` `NULL` stub with a bounded
   compatibility path that now reads clipboard text through `wl-paste`,
   `xclip`, or `xsel` when the surrounding Wayland/X11 environment and helper
   binaries are available, while still returning `NULL` cleanly on unsupported
   hosts.
2. Bounded the new lane explicitly so it mirrors the existing host contract
   instead of over-claiming parity: clipboard text is trimmed at the first
   newline/control break, capped to a fixed maximum size, and copied into the
   engine allocator before it reaches the existing client, UI, and browser
   clipboard consumers.
3. Expanded the focused non-Windows portability suite so the Unix clipboard
   probe chain, PATH lookup, command gating, and Wayland/X11 fallback order
   are source-pinned alongside the earlier low-memory, symbol-compare,
   monkey-marker, profiling, and null-runtime compatibility seams.
4. Narrowed `RW-G02` again: the remaining portability debt is now even more
   clearly in the missing real Unix renderer/audio/input host modernization
   and broader non-Windows validation breadth, not in an unimplemented Unix
   clipboard host hook.

### Task A2c: Refresh the repo-wide parity audit evidence on the current worktree [COMPLETED]
Priority: Medium
Primary areas: `AUDIT.md`, `IMPLEMENTATION_PLAN.md`,
`docs/reverse-engineering/repo-wide-parity-audit-2026-04-21.md`
Parity estimate: **before 96% -> after 96%**

Completed work:

1. Re-ran a broad current-worktree parity sweep across the top-level
   strict-retail gates, gameplay validation fixtures, portability suite, and
   staged runtime-audit lane, producing `72 passed, 7 skipped`.
2. Rebased the top-level ledgers on that sweep so the current repo-wide gap
   register is explicitly backed by one aggregated evidence pass instead of
   only by the individual runtime-probe refresh notes.
3. Clarified that the remaining repo-wide gap families still collapse to
   `RW-G01`, `RW-G02`, and `RW-G04`, with the staged retail-runtime DLL guard
   now treated as closed and the remaining `RW-G04` debt narrowed to fresh
   artifact regeneration/publication.
4. Cleaned up stale date language in the historical top-level audit anchors so
   the repo-wide ledgers no longer point readers at the older `2026-04-17`
   top-level state while describing the current 2026-04-21 worktree.

### Task A6f: Add a strict staged retail-runtime DLL audit for native Windows validation [COMPLETED]
Priority: Medium
Primary areas: `tools/ci/audit-retail-dependencies.ps1`,
`tools/ci/validate-windows-native.ps1`, Windows/toolchain docs
Parity estimate: **before 96% -> after 96%**

Completed work:

1. Extended the retail dependency auditor so it can now audit either the local
   Steam install or an explicit runtime root, checking for missing expected
   retail DLLs, extra non-retail DLLs, and byte-hash mismatches instead of
   only diffing the Steam tree opportunistically.
2. Added a strict retail-runtime staging step to
   `tools/ci/validate-windows-native.ps1`: the retail validation lane now
   assembles `build\win32\<Config>\retail-runtime\` from the rebuilt host
   executables and gameplay/UI DLLs plus the exact retail launcher DLL payload
   from `assets\quakelive\`, then fails fast if the staged root contains extra
   DLLs or is missing any retail payload DLLs.
3. Rebased the Windows/toolchain documentation on that explicit staging
   boundary so the mixed developer build root `build\win32\<Config>\bin\` is
   no longer described as the strict retail payload surface.
4. Narrowed `RW-G04` again: the remaining freshness debt is now no longer the
   previously documented local/runtime DLL-guard follow-up, and is instead
   concentrated in refreshed native build outputs plus the broader glibc and
   self-hosted publication follow-ups.

### Task A6e: Re-promote the retail module runtime alias through an explicit renderer-text bounded blocker [COMPLETED]
Priority: Medium
Primary areas: `tools/modules/run_retail_module_runtime_probe.ps1`,
`tests/test_game_module_retail_parity_gate.py`, runtime-evidence ledgers
Parity estimate: **before 96% -> after 96%**

Completed work:

1. Expanded the retail-module probe's bounded-owner classification so the
   current 2026-04-21 rerun can distinguish two renderer-owned live-map
   blocker shapes outside module scope: the older fatal `R_LoadMD3` drop path
   and the current `R_fonsErrorCallback` font-atlas saturation lane that keeps
   retail `uix86.dll`, `cgamex86.dll`, and `qagamex86.dll` loaded but prevents
   `CS_ACTIVE`.
2. Rebased the module runtime probe on the current map-launch contract again by
   threading the same `com_maxfps 30` / no-warmup assumptions used by the
   other runtime probes into the retail-module lane, while keeping the stable
   alias guarded so only sufficient reruns are promoted.
3. Reran `tools/modules/run_retail_module_runtime_probe.ps1` on 2026-04-21 and
   refreshed
   `artifacts/module_validation/logs/retail_module_runtime_evidence_latest.json`
   to the current bounded `20260421` bundle instead of leaving it pinned to
   the older `2026-04-09` artifact.
4. Narrowed `RW-G04` again: the remaining freshness debt is now no longer a
   non-promotable retail-module alias question, and is instead concentrated in
   fresh native build outputs plus the broader glibc/self-hosted publication
   follow-ups.

### Task A4g: Restore a bounded Unix profiling control path [COMPLETED]
Priority: Medium
Primary areas: `src/code/unix/unix_main.c`,
`src/code/unix/Makefile`, `tests/test_non_windows_portability.py`,
portability ledgers
Parity estimate: **before 96% -> after 96%**

Completed work:

1. Replaced the empty Unix profiling hooks with a bounded `gprof`-compatible
   runtime path: `Sys_Init()` now pauses profiling early when `moncontrol` is
   available, `Sys_BeginProfiling()` re-enables it on first active play, and
   `Sys_Exit()` now flushes `_mcleanup()` through `Sys_EndProfiling()`.
2. Added an explicit Unix build toggle `QL_ENABLE_GPROF=1` so profiling is a
   reproducible opt-in lane rather than an undocumented linker accident. The
   Unix makefile now threads `-pg` through the relevant engine compile/link
   paths when that toggle is enabled.
3. Rebased the focused non-Windows portability checks and ledgers so they now
   record a bounded profiling lane instead of an empty Unix no-op while still
   keeping the broader Unix renderer/audio/input host gap open.
4. Narrowed `RW-G02` again: the remaining portability debt is now even more
   clearly in the modern Unix runtime boundary itself, not in stale host-side
   syscall placeholders.

### Task A6d: Refresh renderer runtime evidence and stabilize alias promotion for the renderer/module probes [COMPLETED]
Priority: Medium
Primary areas: `tools/renderer/run_renderer_runtime_probe.ps1`,
`tools/modules/run_retail_module_runtime_probe.ps1`,
`tests/test_renderer_full_parity_gate.py`,
`tests/test_renderer_text_runtime_validation_parity.py`,
`tests/test_game_module_retail_parity_gate.py`, runtime-evidence docs
Parity estimate: **before 96% -> after 96%**

Completed work:

1. Repaired the renderer runtime probe contract so the current `map <name>
   ffa` path, quoted launch arguments, and normalized path handling work
   reliably again, then reran the probe on 2026-04-21 to refresh the clean
   dated bundle
   `artifacts/renderer_validation/logs/renderer_runtime_evidence_20260421.json`.
2. Added guarded `*_latest.json` promotion to both the renderer and retail
   module probes so only sufficient reruns replace the stable tracked alias.
   The renderer alias now points at the clean 2026-04-21 bundle, and the
   retail-module lane gained the guarded promotion rules that later enabled
   `A6e` to refresh the stable alias to the current bounded `2026-04-21`
   module artifact instead of silently accepting degraded reruns.
3. Rebased the renderer/module parity gates, the font audit script, and the
   active runtime-evidence docs on those stable aliases plus the current
   `map <name> ffa` launch contract.
4. Narrowed `RW-G04` again: the remaining freshness debt is now concentrated
   in fresh native build outputs and the broader glibc/self-hosted publication
   follow-ups.

### Task A4f: Classify the Linux glibc preset as server-only portability evidence [COMPLETED]
Priority: Medium
Primary areas: `docs/build/linux-glibc-32bit.md`,
`docs/platform/toolchain-matrix.md`,
`tests/test_non_windows_portability.py`, portability ledgers
Parity estimate: **before 96% -> after 96%**

Completed work:

1. Updated `docs/build/linux-glibc-32bit.md` so the helper is explicitly
   framed as a `qagamei386.so` server-module reconstruction preset rather than
   as evidence of a retail-equivalent Linux client/runtime.
2. Mirrored that portability boundary in the native toolchain matrix so the
   top-level Linux lane description now points contributors at the correct
   server-only interpretation immediately.
3. Expanded the focused non-Windows portability regression coverage so the
   server-module-only classification and the still-open Unix profiling or
   renderer/audio/input host gaps are pinned in the docs.
4. Narrowed `RW-G02` procedurally: the remaining work is now more cleanly
   about whether to modernise the real Unix host boundary, not about what the
   existing Linux build helper is supposed to prove.

### Task A4e: Modernise the null input compatibility contract [COMPLETED]
Priority: Medium
Primary areas: `src/code/null/null_input.c`,
`tests/test_non_windows_portability.py`,
`tests/test_engine_host_support_full_parity_gate.py`, portability ledgers
Parity estimate: **before 95% -> after 96%**

Completed work:

1. Modernised `src/code/null/null_input.c` so the dedicated/null host now
   carries the current input bootstrap cvars (`in_mouse`, `in_nograb`,
   `in_joystick`, `in_debugjoystick`, and `joy_threshold`) plus an explicit
   compatibility-state refresh that keeps `ui_joyavail` pinned to `0`
   instead of leaving the file as a bare inert no-op.
2. Reconstructed the null input frame pump as an explicit no-device contract:
   `IN_Frame()` now maintains the compatibility cvar surface and consumes
   joystick modification latches, while `Sys_SendKeyEvents()` now refreshes
   the same no-device state without emitting real input events.
3. Expanded both the focused non-Windows portability suite and the
   engine-host/support compatibility gate so the current null input lane is
   pinned alongside the earlier null host/client/audio modernization work.
4. Narrowed `RW-G02` again: the remaining portability debt is now
   concentrated even more tightly in the Unix profiling placeholders and the
   absence of a real modern Unix client/renderer/audio/input host, rather
   than in stale null input bootstrap/event-pump seams.

### Task A4d: Modernise the null client/audio compatibility contracts [COMPLETED]
Priority: Medium
Primary areas: `src/code/null/null_client.c`,
`src/code/null/null_snddma.c`, `tests/test_non_windows_portability.py`,
portability ledgers
Parity estimate: **before 94% -> after 95%**

Completed work:

1. Modernised `src/code/null/null_client.c` so the null compatibility lane now
   exposes the current browser/advert/input-facing `client.h` contract instead
   of only the older partial web-host shim set: the null client now carries
   `CL_RefreshOnlineServicesBridgeState()`, the current browser cursor and app
   activation hooks, mouse/button/wheel webview input stubs, and the retained
   advertisement-bridge entry points while explicitly forcing the browser
   cvars back to the non-live state.
2. Promoted `src/code/null/null_snddma.c` from a narrow legacy dummy into an
   explicit current silent-audio compatibility seam by adding the current
   `SNDDMA_Activate()` and `S_AddVoiceSamples()` entry points alongside the
   existing null DMA and local-sound hooks.
3. Expanded the focused non-Windows portability regression coverage so it now
   asserts the current null client/audio contract surfaces directly instead of
   only pinning the older null host/network/glimp tranche.
4. Narrowed `RW-G02` again: the remaining non-Windows debt is now
   concentrated in the profiling hooks plus the absence of a real modern Unix
   client/renderer/audio/input host, rather than in stale or missing null
   browser/advert/audio contract entry points.

### Task A4c: Modernise the null host contracts and reconstruct the Unix monkey-marker hook [COMPLETED]
Priority: Medium
Primary areas: `src/code/unix/unix_main.c`, `src/code/null/null_main.c`,
`src/code/null/null_net.c`, `src/code/null/mac_net.c`,
`src/code/null/null_glimp.c`, `tests/test_non_windows_portability.py`,
portability ledgers
Parity estimate: **before 93% -> after 94%**

Completed work:

1. Reconstructed the Unix `Sys_MonkeyShouldBeSpanked()` compatibility hook as
   a retained `q3monkeyid` release-marker probe rooted in the historical
   `Construct` script plus the committed retail string corpus, instead of
   leaving it as an unconditional placeholder.
2. Modernised the stale null host shims so they now match the current
   `qcommon` contracts: `null_main.c` now carries current command-line,
   executable-name, timer, path, and homepath scaffolding; `null_net.c` and
   `mac_net.c` now expose `Sys_StringToAdr()` plus the current loopback packet
   stub signatures; and `null_glimp.c` no longer carries the stale `int
   GLimp_Init()` signature.
3. Added focused non-Windows portability coverage for the new Unix marker
   probe and the null-host contract cleanup.
4. Narrowed `RW-G02` again: the remaining open portability debt is now
   concentrated in the profiling hooks plus the broader Unix/client/audio/input
   and still-stubbed null runtime surfaces, rather than in stale host-contract
   mismatches or the old `q3monkeyid` placeholder.

### Task A6c: Refresh the qcommon, server, and WOW64 evidence contracts on the current machine [COMPLETED]
Priority: Medium
Primary areas: `tools/qcommon/run_qcommon_runtime_probe.ps1`,
`tools/server/run_server_runtime_probe.ps1`,
`tools/ci/wow64-smoketest.ps1`,
their tracked artifacts, and repo-wide validation ledgers
Parity estimate: **before 93% -> after 93%**

Completed work:

1. Repaired the stale qcommon and dedicated-server probe contracts so both
   runtime lanes now use the current `map <name> ffa` command shape, then
   re-ran them on 2026-04-21 to refresh
   `artifacts/qcommon_validation/logs/qcommon_runtime_evidence_20260410.json`
   and
   `artifacts/server_validation/logs/server_runtime_evidence_20260410.json`.
2. Rebased the qcommon and server gate/documentation expectations on the
   current runtime markers, including the qcommon `game.error` plus native
   `stopRefresh` fallback evidence and the current dedicated `getstatus`
   server-type field spelling.
3. Updated the retained WOW64 smoke harness so it now prefers retail DLLs from
   `assets/quakelive/baseq3/` when present but falls back to the current
   Win32 build outputs under `build/win32/Debug/bin/baseq3/`, then captured a
   successful 32-bit PowerShell run at
   `artifacts/wow64-smoketest/wow64-smoketest.log`.
4. Narrowed `RW-G04` again: the remaining freshness debt is now concentrated
   in fresh native build outputs, the still-archived runtime bundles outside
   the refreshed client/qcommon/server lanes, and the broader glibc or
   self-hosted validation publication follow-ups.

### Task A4b: Restore bounded Unix function compare/checksum coverage on the compatibility host lane [COMPLETED]
Priority: Medium
Primary areas: `src/code/unix/unix_main.c`,
`tests/test_non_windows_portability.py`, `docs/platform/toolchain-matrix.md`,
top-level portability ledgers
Parity estimate: **before 93% -> after 93%**

Completed work:

1. Restored Unix `Sys_FunctionCmp()` and `Sys_FunctionCheckSum()` with a
   Linux/glibc symbol-backed path that resolves function byte ranges through
   `dladdr1(..., RTLD_DL_SYMENT)` and hashes them with
   `Com_BlockChecksum()` when symbol sizes are available.
2. Added focused portability coverage that now checks the new source-side
   helper path directly instead of only tracking the old placeholder story in
   documentation.
3. Narrowed `RW-G02` again: the remaining open Unix helper debt is now
   concentrated in the historical profiling lane plus the broader
   non-Windows client/audio/input/toolchain boundary.

### Task A6b: Re-baseline the `src/ui` runtime-panel contract to the clean current state [COMPLETED]
Priority: Medium
Primary areas: `tests/test_ui_src_panel_parity.py`,
`tests/test_ui_full_parity_gate.py`, `docs/quakelive_asset_audit.md`,
`docs/ui/hud-audit.md`, `docs/ui/scripting-guide.md`, top-level ledgers
Parity estimate: **before 93% -> after 93%**

Completed work:

1. Tightened the repo/UI parity gates so the current worktree now expects the
   `src/ui` runtime-panel compare to be clean (`65 / 65`, `0` content diffs)
   instead of tolerating the older historical non-zero drift contract.
2. Re-based the UI documentation and the repo-wide ledgers so they now
   distinguish clean checked-in runtime-panel parity from the separate
   bundle-staged retail art path.
3. Documented that explicit runtime-root refreshes always write the runtime
   package manifest, but only emit `pak_ui_src_retail_overlay.pk3` when
   `drift_files` is non-empty.

### Task A6a: Refresh the tracked client runtime evidence bundle after UI package-proof hardening [COMPLETED]
Priority: Medium
Primary areas: `tools/client/run_client_runtime_probe.ps1`,
`tests/test_client_full_parity_gate.py`,
`artifacts/client_validation/logs/client_runtime_evidence_20260410.json`,
client/runtime audit docs
Parity estimate: **before 93% -> after 93%**

Completed work:

1. Tightened the client parity gate so the tracked runtime bundle must now
   prove the emitted UI runtime-package manifest plus the refreshed main
   package hashes instead of relying only on the older screenshot/log bundle.
2. Rebased the main-menu offline-browser proof on the current retained runtime
   behavior, using the observed `game.error` publication and UI-side
   `stopRefresh` fallback markers instead of the older stale probe
   expectations.
3. Re-ran `tools/client/run_client_runtime_probe.ps1` on 2026-04-21 and
   refreshed `artifacts/client_validation/logs/client_runtime_evidence_20260410.json`
   with fresh screenshots, logs, demo output, and UI package evidence.
4. Narrowed `RW-G04` by refreshing the client runtime bundle while leaving the
   remaining archived runtime/build artifacts as the still-open repo-wide
   freshness debt.

### Task A5: Harden the read-only `src/ui` parity path with runtime package proof [COMPLETED]
Priority: High
Primary areas: `tools/build_ui_bundle.py`, `tests/test_ui_src_panel_parity.py`,
`tools/client/run_client_runtime_probe.ps1`, `docs/quakelive_asset_audit.md`,
`docs/ui/hud-audit.md`, `docs/ui/scripting-guide.md`
Parity estimate: **before 92% -> after 93%**

Completed work:

1. Added an explicit runtime-package manifest to `tools/build_ui_bundle.py`
   for `--runtime-root` runs so emitted `pak_uiql.pk3` and
   `pak_ui_src_retail_overlay.pk3` outputs are now machine-described instead
   of assumed from console output alone.
2. Added focused UI bundle coverage that proves the explicit runtime-root path
   emits the expected PK3s, includes the required runtime entries and
   compatibility aliases, and keeps any emitted overlay package in lockstep
   with the source-vs-retail drift contract.
3. Tightened the client runtime probe so it now verifies the refreshed runtime
   package manifest and fails fast if the required UI runtime package was not
   emitted into the writable homepath.
4. Refreshed the UI packaging docs so they consistently describe the current
   contract: staging/overlay manifests by default, explicit package emission
   only for runtime-root refreshes or probe flows, with the overlay PK3
   remaining optional when the drift contract is empty.

### Task A4a: Restore Unix low-memory detection on the compatibility host lane [COMPLETED]
Priority: Medium
Primary areas: `src/code/unix/unix_main.c`, `docs/platform/toolchain-matrix.md`
Parity estimate: **before 92% -> after 92%**

Completed work:

1. Replaced the unconditional Unix `Sys_LowPhysicalMemory()` placeholder with
   a native `sysconf()`-backed physical page-count query so the renderer/cgame
   low-memory heuristic no longer hardcodes the non-low-memory path on Unix.
2. Refreshed the platform note so it now records the restored low-memory
   probe separately from the still-bounded checksum/comparison/profiling
   helpers.
3. Narrowed the active `RW-G02` description to the remaining portability debt
   instead of continuing to list `Sys_LowPhysicalMemory()` as an unresolved
   placeholder.

### Task A2: Repo-wide parity re-baseline and documentation convergence [COMPLETED]
Priority: Critical
Primary areas: `AUDIT.md`, `IMPLEMENTATION_PLAN.md`,
`docs/reverse-engineering/repo-wide-parity-audit-2026-04-21.md`,
`docs/parity-plan.md`, `docs/ui_deltas.md`, `docs/ui_followup_issues.md`,
`docs/quakelive_asset_audit.md`
Parity estimate: **before 92% -> after 92%**

Completed work:

1. Re-ran the repo's top-level parity-gate suites on 2026-04-21 and confirmed
   that the strict-retail Windows gate set remains green on the current
   worktree.
2. Re-based the top-level ledger so it now distinguishes the strict-retail
   Windows closure state from repo-wide parity across compatibility-only,
   portability, and packaging-dependent lanes.
3. Published a dedicated repo-wide gap register in
   `docs/reverse-engineering/repo-wide-parity-audit-2026-04-21.md`.
4. Demoted the most misleading broad-planning documents to explicit historical
   references so they no longer conflict with the current reverse-engineering
   ledgers.

### Task A1: Client parity-gate revalidation and workflow restoration [COMPLETED]
Priority: Critical
Primary areas: `.github/workflows/client-validation.yml`,
`tools/client/run_client_runtime_probe.ps1`,
`artifacts/client_validation/logs/*`, client ledger docs
Parity estimate: **before 99% -> after 100%**

Completed work:

1. Restored `.github/workflows/client-validation.yml` so the client validation
   lane again runs the focused platform, Steamworks, config, workshop, UI-menu,
   and unified parity-gate suites expected by the audited `CL-P6` closure.
2. Repaired `tools/client/run_client_runtime_probe.ps1` so it now:
   - runs against the default build-disabled client configuration
   - uses the valid `map bloodrun ffa` command shape for the local-map probe
   - avoids helper-stdout pollution in the structured probe return path
   - retries transient `pak_uiql.pk3` rewrite locks on Windows
   - caps the probe at `com_maxfps 30`, which lets the map pass reach
     `CS_ACTIVE` before the queued demo/screenshot/disconnect commands fire
3. Refreshed
   `artifacts/client_validation/logs/client_runtime_evidence_20260410.json`
   and
   `artifacts/client_validation/logs/client_full_parity_gate.json` with a
   clean runtime bundle.
4. Revalidated the lane with:
   - `pytest tests/test_client_full_parity_gate.py -q --tb=no`
   - `pytest tests/test_platform_services.py tests/test_steamworks_harness.py tests/test_client_config_parity.py tests/test_client_workshop_bootstrap_parity.py tests/test_ui_menu_files.py tests/test_client_full_parity_gate.py -q --tb=no`

### Task A3a: Expose explicit compatibility-only provider/policy labels through auth, workshop, and browser-overlay surfaces [COMPLETED]
Priority: Critical
Primary areas: `src/common/platform/`, `src/code/client/`,
`docs/platform/authentication.md`, `docs/steam_platform_abstraction.md`
Parity estimate: **before 96% -> after 96%**

Completed work:

1. Added `QL_DescribePlatformFeaturePolicy(...)` as the shared companion label
   for platform-service descriptors and threaded that label through the client
   auth dispatcher so build-disabled, runtime-disabled, and provider-unavailable
   lanes stay explicit in auth lifecycle logs.
2. Mirrored the browser/advert overlay descriptor through the ROM cvars
   `ui_browserAwesomiumProvider` and `ui_browserAwesomiumPolicy`, and routed the
   blocked browser commands through provider-aware compatibility logging instead
   of generic “provider unavailable” messages.
3. Bounded the retained workshop bootstrap to the Steam UGC owner lane,
   documented provider/policy-aware fallback logging for non-Steam/bootstrap
   paths, and refreshed the focused platform/workshop regression coverage to
   keep those compatibility-only labels visible.

### Task A3b: Expose explicit compatibility-only provider/policy labels through server auth and Steam GameServer surfaces [COMPLETED]
Priority: Critical
Primary areas: `src/code/server/`, `src/code/qcommon/`,
`docs/platform/authentication.md`, `docs/steam_platform_abstraction.md`
Parity estimate: **before 96% -> after 96%**

Completed work:

1. Mirrored the retained server auth and matchmaking descriptors through the
   ROM cvars `sv_platformAuthProvider`, `sv_platformAuthPolicy`,
   `sv_steamServerProvider`, and `sv_steamServerPolicy` so dedicated-server
   diagnostics expose the active provider/policy pair just as explicitly as the
   client-side browser, workshop, and auth surfaces.
2. Bounded the Steam GameServer bootstrap/publication lane with
   provider/policy-aware fallback and callback logging, including the
   compatibility-only dedicated-server publication fallback when the retained
   GameServer owner is unavailable.
3. Updated server-side auth telemetry so it now appends
   `provider=<...> policy=<...>` to the message payload while intentionally
   preserving the legacy `credential=steam` field, then refreshed the focused
   platform-service regression coverage to keep that compatibility labeling
   explicit.

### Task A3c: Expose explicit compatibility-only provider/policy labels through client live-resource bridge surfaces [COMPLETED]
Priority: Critical
Primary areas: `src/code/client/cl_steam_resources.c`,
`tests/test_platform_services.py`, `docs/steam_platform_abstraction.md`,
`docs/reverse-engineering/source-file-gap-notes/rw-g01-client-steam-resources.md`
Parity estimate: **before 96% -> after 96%**

Completed work:

1. Threaded the overlay service descriptor’s provider/policy labels into the
   retained live-resource bridge so the `steam://` avatar/resource path has the
   same explicit compatibility labeling as the browser overlay and workshop
   seams.
2. Replaced the generic Steam-resource and launcher-backend diagnostics with
   provider-aware logs that now spell out when the Steam resource bridge is
   disabled, when the retained SteamDataSource owner cannot satisfy a request,
   and when the launcher/web fallback owner is the remaining compatibility
   path.
3. Refreshed the focused platform-service regression coverage and the
   file-level `RW-G01` gap note so the live-resource bridge now documents the
   bounded compatibility/fallback story it still implements instead of the
   older generic “backend unavailable” wording.

### Task A3d: Expose explicit compatibility-only provider/policy labels through client matchmaking, stats, and social-overlay command surfaces [COMPLETED]
Priority: Critical
Primary areas: `src/code/client/cl_main.c`,
`tests/test_platform_services.py`, `docs/steam_platform_abstraction.md`
Parity estimate: **before 96% -> after 96%**

Completed work:

1. Mirrored the retained client matchmaking, stats, and social-overlay
   descriptors through the ROM cvars `cl_matchmakingProvider`,
   `cl_matchmakingPolicy`, `cl_statsProvider`, `cl_statsPolicy`,
   `cl_socialOverlayProvider`, and `cl_socialOverlayPolicy` so the active
   provider/policy pair remains visible at bootstrap and callback-init time.
2. Routed the retained `stats_clear`, `connect_lobby`, `clientviewprofile`,
   `clientfriendinvite`, callback-bundle fallback, and main-menu rich-presence
   failure paths through provider-aware compatibility diagnostics instead of
   generic Steam-only wording.
3. Refreshed the focused platform-service regression coverage and the platform
   abstraction notes so this client command surface now documents the bounded
   compatibility lane it still implements.

### Task A3e: Expose explicit compatibility-only provider/policy labels through the default-disabled server rankings surface [COMPLETED]
Priority: Critical
Primary areas: `src/code/server/sv_rankings.c`, `src/code/server/sv_init.c`,
`tests/test_platform_services.py`,
`docs/reverse-engineering/source-file-gap-notes/rw-g01-server-rankings.md`
Parity estimate: **before 96% -> after 96%**

Completed work:

1. Added explicit rankings provider/policy helpers and mirrored them through
   the ROM cvars `sv_rankingsProvider` and `sv_rankingsPolicy` so the
   default-disabled rankings lane no longer hides behind the generic
   `sv_rankingsActive` flag alone.
2. Threaded the provider/policy pair into the disabled rankings bootstrap
   diagnostics so the forced `sv_enableRankings 0` fallback and the retained
   compatibility-only rankings surface stay explicit at runtime.
3. Refreshed the focused server/platform-service parity checks and the
   `RW-G01` rankings gap note so this retained GPL-era rankings lane is now
   documented using the same compatibility-labeling story as the other active
   repo-wide online-service seams.

### Task A3f: Expose explicit heuristic compatibility labeling through auth backend responses and fallback traces [COMPLETED]
Priority: Critical
Primary areas: `src/common/platform/backends/`, `src/code/client/ql_auth.c`,
`tools/integration/auth_flow_trace.py`, `docs/platform/authentication.md`,
`docs/steam_platform_abstraction.md`
Parity estimate: **before 96% -> after 96%**

Completed work:

1. Updated the retained Steamworks and open-adapter auth backends so their
   response payloads explicitly identify themselves as heuristic compatibility
   backends instead of reading like retail live-service verdicts.
2. Threaded an explicit `hybrid-fallback` stage plus fallback-dispatch log
   through the hybrid auth path so the open-adapter handoff is visible in
   lifecycle traces whenever Steamworks returns a retry-eligible result.
3. Refreshed the scripted auth-flow trace, the focused platform-service
   regression coverage, and the auth/backend gap notes so the documented QA
   evidence now matches the bounded compatibility story carried by the current
   source.

### Task A3g: Expose explicit overall online-services mode/policy labels through the structural service-table surface [COMPLETED]
Priority: Critical
Primary areas: `src/common/platform/platform_services.c`,
`src/code/client/cl_main.c`, `src/code/server/sv_init.c`,
`tests/test_platform_services.py`, `docs/steam_platform_abstraction.md`
Parity estimate: **before 96% -> after 96%**

Completed work:

1. Added common helpers that collapse the cached service table into overall
   online-services mode/policy labels, keeping the build-disabled,
   externally-disabled, Steamworks-only, open-adapter-only, and hybrid
   compatibility lanes explicit at the structural layer itself.
2. Mirrored those summary labels through the new ROM cvars
   `cl_onlineServicesMode`, `cl_onlineServicesPolicy`,
   `sv_onlineServicesMode`, and `sv_onlineServicesPolicy` so client/server
   diagnostics no longer require reading each per-feature provider cvar to
   understand the current repo-wide online-service boundary.
3. Refreshed the focused platform-service probes plus the `RW-G01`
   platform-services/platform-config notes so the structural service-table and
   build-flag story now matches the bounded compatibility surface described by
   the current docs and tests.

### Task A3h: Expose explicit overall online-services mode/policy labeling through auth policy-block and ticket-request failure paths [COMPLETED]
Priority: Critical
Primary areas: `src/code/client/ql_auth.c`,
`tests/test_platform_services.py`, `docs/platform/authentication.md`,
`docs/steam_platform_abstraction.md`,
`docs/reverse-engineering/source-file-gap-notes/rw-g01-client-auth.md`
Parity estimate: **before 96% -> after 96%**

Completed work:

1. Routed the early Steam and standalone auth policy gates through a shared
   helper that now emits explicit `policy-blocked` lifecycle logs and response
   text naming the active overall online-services mode/policy lane instead of
   the older generic build/runtime wording.
2. Threaded that same structural mode/policy context through Steam
   ticket-request failure and backend-uninitialised responses so the bounded
   auth surface stays explicit even when no backend dispatch occurs.
3. Refreshed the focused auth/platform-service regression coverage plus the
   client-auth gap note and supporting docs so the documented `RW-G01`
   compatibility story now matches those early auth exit paths too.

### Task A3i: Expose explicit provider/policy labeling through the retained advert bridge surface [COMPLETED]
Priority: Critical
Primary areas: `src/code/client/cl_cgame.c`, `src/code/client/cl_main.c`,
`tests/test_platform_services.py`, `docs/steam_platform_abstraction.md`,
`docs/reverse-engineering/source-file-gap-notes/rw-g01-platform-services.md`
Parity estimate: **before 96% -> after 96%**

Completed work:

1. Mirrored the retained advert bridge through the new ROM cvars
   `ui_advertisementBridgeProvider` and `ui_advertisementBridgePolicy` so the
   active advert bridge lane is visible independently of the older browser
   overlay cvars.
2. Added bounded provider-aware advert lifecycle diagnostics for the UI/cgame
   bridge transitions (`init-ui`, `activate`, `set-active`, and
   `shutdown-cgame`) instead of leaving that seam implicit behind generic
   overlay state refreshes.
3. Refreshed the focused platform-service assertions plus the platform-service
   abstraction/gap-note docs so the retained advert flow now matches the same
   explicit compatibility-labeling story as the other active `RW-G01`
   surfaces.

### Task A3j: Expose explicit overall mode/policy labeling through the retained client voice fallback lane [COMPLETED]
Priority: Critical
Primary areas: `src/code/client/cl_main.c`,
`tests/test_platform_services.py`, `docs/steam_platform_abstraction.md`,
`docs/reverse-engineering/source-file-gap-notes/rw-g01-platform-services.md`
Parity estimate: **before 96% -> after 96%**

Completed work:

1. Mirrored the retained client voice compatibility lane through the new ROM
   cvars `cl_voiceServiceMode` and `cl_voiceServicePolicy` so the local
   speaking-state fallback no longer hides behind the broader online-services
   summary cvars alone.
2. Added explicit `voice fallback` diagnostics for `+voice` and `-voice`,
   naming the active overall online-services mode/policy lane whenever Steam
   voice is unavailable and the local speaking-state bridge is the remaining
   compatibility path.
3. Refreshed the focused platform-service assertions plus the
   platform-service abstraction/gap-note docs so the retained voice surface now
   matches the same explicit compatibility-labeling story as the other active
   `RW-G01` seams.

### Task A3k: Expose explicit overall mode/policy labeling through the retained client identity bootstrap and UI subscription lanes [COMPLETED]
Priority: Critical
Primary areas: `src/code/client/cl_main.c`, `src/code/client/cl_ui.c`,
`tests/test_platform_services.py`, `docs/steam_platform_abstraction.md`,
`docs/reverse-engineering/source-file-gap-notes/rw-g01-platform-services.md`
Parity estimate: **before 96% -> after 96%**

Completed work:

1. Mirrored the retained client identity/bootstrap and UI app-subscription
   lanes through the new ROM cvars `cl_identityBootstrapMode`,
   `cl_identityBootstrapPolicy`, `ui_subscriptionBridgeMode`, and
   `ui_subscriptionBridgePolicy` so these remaining Steam-owned shims no longer
   rely on the broader summary cvars alone for compatibility context.
2. Added explicit identity/subscription diagnostics for Steam persona-name
   seeding, Steam country seeding, and the UI `IsSubscribedApp` bridge,
   naming the active overall online-services mode/policy lane whenever the
   compatibility path falls back or the current provider is unavailable.
3. Refreshed the focused platform-service assertions plus the
   platform-service abstraction/gap-note docs so the retained client bootstrap
   and UI subscription surface now matches the same explicit
   compatibility-labeling story as the other active `RW-G01` seams.

### Task A3l: Expose explicit provider/policy labeling through the retained live-resource and avatar bridge lane [COMPLETED]
Priority: Critical
Primary areas: `src/code/client/cl_steam_resources.c`,
`src/code/client/cl_main.c`, `src/code/client/cl_cgame.c`,
`tests/test_platform_services.py`, `docs/steam_platform_abstraction.md`,
`docs/reverse-engineering/source-file-gap-notes/rw-g01-platform-services.md`
Parity estimate: **before 96% -> after 96%**

Completed work:

1. Mirrored the retained live-resource bridge through the new ROM cvars
   `ui_resourceBridgeProvider` and `ui_resourceBridgePolicy` so the
   `steam://`/launcher-backed image lane is visible independently of the older
   browser overlay and advert bridge cvars.
2. Routed the cgame avatar import through the existing provider-aware resource
   stub path instead of returning before the compatibility diagnostics fired,
   which keeps disabled `steam://avatar/...` lookups explicit at runtime.
3. Refreshed the focused platform-service assertions plus the
   platform-service abstraction/gap-note docs so the retained live-resource and
   avatar lane now matches the same explicit compatibility-labeling story as
   the other active `RW-G01` seams.

### Task A3m: Expose explicit provider/policy labeling through the retained client workshop lifecycle [COMPLETED]
Priority: Critical
Primary areas: `src/code/client/cl_main.c`,
`tests/test_platform_services.py`,
`tests/test_client_workshop_bootstrap_parity.py`,
`docs/steam_platform_abstraction.md`,
`docs/reverse-engineering/source-file-gap-notes/rw-g01-platform-services.md`
Parity estimate: **before 96% -> after 96%**

Completed work:

1. Mirrored the retained client workshop seam through the ROM cvars
   `cl_workshopProvider` and `cl_workshopPolicy` so the active workshop owner
   is visible alongside the other client online-service descriptors.
2. Routed the workshop bootstrap, download, callback-ignore, queue-complete,
   and filesystem-restart diagnostics through a shared provider-aware helper,
   which keeps the current compatibility-only workshop lane explicit instead of
   falling back to generic Steamworks-only wording.
3. Refreshed the focused workshop/platform-service regression coverage plus the
   platform-service abstraction and `RW-G01` gap note so the documented
   workshop lifecycle now matches the same explicit compatibility-labeling
   story as the other active online-service seams.

### Task A3n: Expose explicit provider/policy labeling through the retained dedicated-server P2P callback lane [COMPLETED]
Priority: Critical
Primary areas: `src/code/server/sv_client.c`,
`tests/test_platform_services.py`,
`docs/steam_platform_abstraction.md`,
`docs/reverse-engineering/source-file-gap-notes/rw-g01-platform-services.md`
Parity estimate: **before 96% -> after 96%**

Completed work:

1. Added a shared dedicated-server P2P callback logger that reports the active
   Steam GameServer provider/policy pair for the retained session-request
   surface instead of leaving those diagnostics as raw Steam-only wording.
2. Routed the server-side P2P request callback through that helper for missing
   client, unauthenticated client, and accept-failure paths so the bounded
   compatibility lane stays explicit during those callback exits too.
3. Refreshed the focused platform-service regression coverage plus the
   platform-service abstraction and `RW-G01` gap note so the dedicated-server
   P2P callback path now matches the same explicit compatibility-labeling story
   as the other active online-service seams.

### Task A3o: Expose explicit provider/policy labeling through the retained dedicated-server stats lane [COMPLETED]
Priority: Critical
Primary areas: `src/code/server/sv_init.c`, `src/code/server/sv_client.c`,
`tests/test_platform_services.py`,
`docs/steam_platform_abstraction.md`,
`docs/reverse-engineering/source-file-gap-notes/rw-g01-platform-services.md`
Parity estimate: **before 96% -> after 96%**

Completed work:

1. Mirrored the retained dedicated-server stats seam through the ROM cvars
   `sv_statsProvider` and `sv_statsPolicy` so the active GameServerStats owner
   is visible alongside the other server online-service descriptors.
2. Added a shared provider-aware server-stats logger and routed the
   request-current-values, session-bootstrap P2P hello failure, and stat-delta
   diagnostics through it so this compatibility-only lane no longer hides
   behind raw Steam-only wording.
3. Refreshed the focused platform-service regression coverage plus the
   platform-service abstraction and `RW-G01` gap note so the dedicated-server
   stats path now matches the same explicit compatibility-labeling story as the
   other active online-service seams.

### Task A3p: Expose explicit provider/policy labeling through the retained client rich-presence lifecycle [COMPLETED]
Priority: Critical
Primary areas: `src/code/client/cl_main.c`, `src/code/client/cl_cgame.c`,
`src/code/client/client.h`, `tests/test_platform_services.py`,
`docs/steam_platform_abstraction.md`,
`docs/reverse-engineering/source-file-gap-notes/rw-g01-platform-services.md`
Parity estimate: **before 96% -> after 96%**

Completed work:

1. Exported the shared matchmaking-lane logger through `client.h` so the
   retained first-snapshot rich-presence owner can report the active
   provider/policy pair instead of silently depending on a Steam-only path.
2. Routed the main-menu and first-snapshot rich-presence writes through
   explicit provider-aware fallback diagnostics for provider-unavailable and
   update-failed exits while preserving the existing retail status strings.
3. Refreshed the focused platform-service regression coverage plus the
   platform-service abstraction and `RW-G01` gap note so the retained client
   rich-presence lifecycle now matches the same explicit compatibility-labeling
   story as the other active online-service seams.

### Task A3q: Expose explicit provider/policy labeling through the retained dedicated-server auth rejection lane [COMPLETED]
Priority: Critical
Primary areas: `src/code/server/sv_client.c`,
`tests/test_platform_services.py`, `docs/platform/authentication.md`,
`docs/steam_platform_abstraction.md`,
`docs/reverse-engineering/source-file-gap-notes/rw-g01-platform-services.md`
Parity estimate: **before 96% -> after 96%**

Completed work:

1. Added a shared dedicated-server auth rejection logger so the retained
   auth-session bootstrap reports the active provider/policy pair when session
   startup fails instead of falling back to raw Steam-only debug wording.
2. Routed both auth-session bootstrap failure exits through that helper while
   preserving the legacy outward `Failed to authenticate with Steam: ...`
   message contract for stable client-facing and telemetry consumers.
3. Refreshed the focused platform-service regression coverage plus the auth and
   platform-service docs so the retained dedicated-server auth rejection path
   now matches the same explicit compatibility-labeling story as the other
   active online-service seams.

### Task A3r: Expose explicit provider/policy labeling through the retained client callback and stats-registration bootstrap gates [COMPLETED]
Priority: Critical
Primary areas: `src/code/client/cl_main.c`,
`tests/test_platform_services.py`,
`docs/steam_platform_abstraction.md`,
`docs/reverse-engineering/source-file-gap-notes/rw-g01-platform-services.md`
Parity estimate: **before 96% -> after 96%**

Completed work:

1. Routed the disabled-services early exit in `CL_Steam_InitCallbacks()` through
   the same provider-aware callback-bundle fallback diagnostic used by the
   registration-failure path, so the retained browser-event compatibility lane
   no longer stays silent when callbacks never become eligible.
2. Added explicit stats provider/policy-aware skip diagnostics to the
   `stats_clear` registration gate for provider-unavailable, initialisation-
   failed, and unsupported-app-id exits, which keeps that bootstrap boundary
   explicit even when the command is never registered.
3. Refreshed the focused platform-service regression coverage plus the
   platform-service abstraction and `RW-G01` gap note so the retained client
   callback/stats bootstrap path now matches the same explicit
   compatibility-labeling story as the other active online-service seams.

### Task A3s: Expose explicit provider/policy labeling through the retained dedicated-server callback bootstrap stub [COMPLETED]
Priority: Critical
Primary areas: `src/code/server/sv_client.c`,
`tests/test_platform_services.py`,
`docs/steam_platform_abstraction.md`,
`docs/reverse-engineering/source-file-gap-notes/rw-g01-platform-services.md`
Parity estimate: **before 96% -> after 96%**

Completed work:

1. Routed the build-disabled `SV_SteamServerInitCallbacks()` stub through the
   same provider-aware callback-registration fallback diagnostic used by the
   active registration failure path, so the dedicated-server callback lane no
   longer disappears silently during startup.
2. Extended the focused platform-service regression coverage to pin that
   build-disabled callback-bootstrap fallback against the existing provider and
   policy labels.
3. Refreshed the platform-service abstraction and `RW-G01` gap note so the
   retained dedicated-server callback bootstrap now matches the same explicit
   compatibility-labeling story as the other active online-service seams.

### Task A3t: Expose explicit mode/policy labeling through the retained client voice transport lifecycle [COMPLETED]
Priority: Critical
Primary areas: `src/code/client/cl_main.c`,
`tests/test_platform_services.py`,
`docs/steam_platform_abstraction.md`,
`docs/reverse-engineering/source-file-gap-notes/rw-g01-platform-services.md`
Parity estimate: **before 96% -> after 96%**

Completed work:

1. Added a shared voice-transport lifecycle logger so the retained Steam voice
   send/receive lane now reports the active overall mode/policy pair instead
   of falling back to raw generic trace wording when the transport fails.
2. Routed voice packet send failure, packet read failure, decompress failure,
   and zero-byte-decompress diagnostics through that helper so the retained
   voice transport now matches the same explicit compatibility story as the
   `+voice` / `-voice` command surface.
3. Refreshed the focused platform-service regression coverage plus the
   platform-service abstraction and `RW-G01` gap note so the retained client
   voice transport lifecycle now matches the same explicit
   compatibility-labeling story as the other active online-service seams.

### Task A3u: Expose explicit provider/policy labeling through the retained dedicated-server stats-owner stubs [COMPLETED]
Priority: Critical
Primary areas: `src/code/server/sv_client.c`,
`tests/test_platform_services.py`,
`docs/steam_platform_abstraction.md`,
`docs/reverse-engineering/source-file-gap-notes/rw-g01-platform-services.md`
Parity estimate: **before 96% -> after 96%**

Completed work:

1. Added a shared provider-aware stub logger for the build-disabled dedicated-
   server stats owner path so the retained `SV_SteamStats_*` surface no longer
   disappears silently when the current stats lane is unavailable.
2. Routed the build-disabled stat-delta, achievement-unlock, and achievement-
   query stubs through that helper with call-site detail strings, keeping the
   compatibility-only fallback explicit even when the owner functions still
   return without touching a live backend.
3. Refreshed the focused platform-service regression coverage plus the
   platform-service abstraction and `RW-G01` gap note so the retained
   dedicated-server stats-owner stubs now match the same explicit
   compatibility-labeling story as the other active online-service seams.

### Task A3v: Expose explicit provider/policy labeling through the retained dedicated-server networking maintenance lane [COMPLETED]
Priority: Critical
Primary areas: `src/code/server/sv_main.c`,
`tests/test_platform_services.py`,
`docs/steam_platform_abstraction.md`,
`docs/reverse-engineering/source-file-gap-notes/rw-g01-platform-services.md`
Parity estimate: **before 96% -> after 96%**

Completed work:

1. Added a shared provider-aware networking logger for the retained Steam
   GameServer maintenance owner so keepalive and packet-relay failures no
   longer collapse into silent compatibility-only behavior.
2. Routed keepalive send failure, inbound relay read failure, unknown relay
   sender, and relay-send failure exits through that helper, keeping the
   bounded Steam GameServer networking lane explicit whenever those paths fail.
3. Refreshed the focused platform-service regression coverage plus the
   platform-service abstraction and `RW-G01` gap note so the retained
   dedicated-server networking maintenance lane now matches the same explicit
   compatibility-labeling story as the other active online-service seams.

### Task A3w: Expose explicit provider/policy labeling through the retained dedicated-server published-state owner [COMPLETED]
Priority: Critical
Primary areas: `src/code/server/sv_main.c`,
`tests/test_platform_services.py`,
`docs/steam_platform_abstraction.md`,
`docs/reverse-engineering/source-file-gap-notes/rw-g01-platform-services.md`
Parity estimate: **before 96% -> after 96%**

Completed work:

1. Added a shared provider-aware published-state logger for the retained Steam
   GameServer metadata owner so publication writes no longer fail silently
   behind the bounded compatibility lane.
2. Routed max-player, password, hostname, map, game-description, game-tags,
   score key-value, player-data, and bot-count publication failures through
   that helper, keeping the retained GameServer metadata owner explicit when
   those writes cannot be applied.
3. Refreshed the focused platform-service regression coverage plus the
   platform-service abstraction and `RW-G01` gap note so the retained
   dedicated-server published-state owner now matches the same explicit
   compatibility-labeling story as the other active online-service seams.

### Task A3x: Expose explicit provider/policy labeling through the retained client P2P callback lane [COMPLETED]
Priority: Critical
Primary areas: `src/code/client/cl_main.c`,
`tests/test_platform_services.py`,
`docs/steam_platform_abstraction.md`,
`docs/reverse-engineering/source-file-gap-notes/rw-g01-platform-services.md`
Parity estimate: **before 96% -> after 96%**

Completed work:

1. Added a shared matchmaking callback logger for the retained client P2P
   session-request owner so this callback lane no longer falls back to a raw
   generic Steam trace.
2. Routed both the accept-failure and accepted-session callback exits through
   that helper with the requested remote SteamID detail, which keeps the
   bounded client matchmaking callback surface explicit whenever the callback
   fires.
3. Refreshed the focused platform-service regression coverage plus the
   platform-service abstraction and `RW-G01` gap note so the retained client
   P2P callback lane now matches the same explicit compatibility-labeling story
   as the other active online-service seams.

### Task A3y: Expose explicit provider/policy labeling through the retained client browser-event publish lane [COMPLETED]
Priority: Critical
Primary areas: `src/code/client/cl_main.c`,
`tests/test_platform_services.py`,
`docs/steam_platform_abstraction.md`,
`docs/reverse-engineering/source-file-gap-notes/rw-g01-platform-services.md`
Parity estimate: **before 96% -> after 96%**

Completed work:

1. Added a shared browser-event lifecycle logger for the retained client
   browser-event owner so this queue lane no longer falls back to generic
   `PublishEvent failed` or raw `steam_event` traces.
2. Routed the missing-view, missing-window-object, and queued-event exits
   through that helper with explicit queue metadata, keeping the retained
   overlay/browser seam honest about the current provider/policy pair whenever
   browser events are published.
3. Refreshed the focused platform-service regression coverage plus the
   platform-service abstraction and `RW-G01` gap note so the retained client
   browser-event publish lane now matches the same explicit compatibility
   labeling story as the other active online-service seams.

### Task A3z: Expose explicit provider/policy labeling through the retained client microtransaction callback lane [COMPLETED]
Priority: Critical
Primary areas: `src/code/client/cl_main.c`,
`tests/test_platform_services.py`,
`docs/steam_platform_abstraction.md`,
`docs/reverse-engineering/source-file-gap-notes/rw-g01-platform-services.md`
Parity estimate: **before 96% -> after 96%**

Completed work:

1. Added a shared microtransaction callback logger for the retained client
   purchase-authorization lane so this callback no longer falls back to a raw
   generic payload dump.
2. Routed the retained microtransaction authorization callback through that
   helper before it forwards the purchase update into the browser-event queue,
   keeping the overlay/browser compatibility owner explicit whenever this
   callback fires.
3. Refreshed the focused platform-service regression coverage plus the
   platform-service abstraction and `RW-G01` gap note so the retained client
   microtransaction callback lane now matches the same explicit
   compatibility-labeling story as the other active online-service seams.

### Task A3aa: Expose explicit provider/policy labeling through the retained dedicated-server workshop operator surface [COMPLETED]
Priority: Critical
Primary areas: `src/code/server/sv_init.c`, `src/code/server/sv_ccmds.c`,
`tests/test_platform_services.py`,
`docs/steam_platform_abstraction.md`,
`docs/reverse-engineering/source-file-gap-notes/rw-g01-platform-services.md`
Parity estimate: **before 96% -> after 96%**

Completed work:

1. Mirrored the retained dedicated-server workshop seam through the ROM cvars
   `sv_workshopProvider` and `sv_workshopPolicy` so the active workshop owner
   is visible alongside the other server online-service descriptors.
2. Added a shared provider-aware workshop operator logger plus a bounded
   Steam-UGC support gate for `steam_downloadugc`, `steam_subscribeugc`, and
   `steam_unsubscribeugc`, which keeps those Steam-specific operator commands
   explicit about the current compatibility lane instead of pretending that
   every workshop provider owns the same surface.
3. Refreshed the focused platform-service regression coverage plus the
   platform-service abstraction and `RW-G01` gap note so the retained server
   workshop operator surface now matches the same explicit
   compatibility-labeling story as the other active online-service seams.

### Task A3ab: Expose explicit provider/policy labeling through the retained client web-host social and UGC export lanes [COMPLETED]
Priority: Critical
Primary areas: `src/code/client/cl_cgame.c`, `tests/test_platform_services.py`,
`docs/steam_platform_abstraction.md`,
`docs/reverse-engineering/source-file-gap-notes/rw-g01-platform-services.md`
Parity estimate: **before 96% -> after 96%**

Completed work:

1. Added retained web-host helpers for the overall online-service mode/policy
   plus matchmaking and workshop provider/policy labels, keeping the browser
   social/UGC export seams aligned with the repo-wide compatibility boundary.
2. Updated `GetConfig`, friend-list export, UGC export, and `web.ugc.failed`
   publication so browser callers see explicit provider/policy metadata while
   disabled or unavailable Steam-backed exports log bounded fallback
   diagnostics without changing the legacy array payload shape.
3. Refreshed focused regression coverage plus the platform-service abstraction
   and `RW-G01` gap note so the retained client web-host export lane now
   matches the same explicit compatibility-labeling story as the other active
   online-service seams.

### Task A3ac: Expose explicit provider/policy labeling through the retained client lobby callback lane [COMPLETED]
Priority: Critical
Primary areas: `src/code/client/cl_main.c`, `tests/test_platform_services.py`,
`docs/steam_platform_abstraction.md`,
`docs/reverse-engineering/source-file-gap-notes/rw-g01-platform-services.md`
Parity estimate: **before 96% -> after 96%**

Completed work:

1. Extended the retained matchmaking callback diagnostics so the client lobby
   callback owner now reports provider/policy-aware lifecycle detail for lobby
   create, enter, membership, chat, metadata, game-created, kicked, and
   join-requested events instead of only making the bounded queue visible once
   the browser-event publication layer runs.
2. Kept the existing browser-event payload shapes intact while making the
   callback-origin seam explicit, which preserves the compatibility-only
   browser contract without letting those lobby callbacks read like silent
   Steam-owned behavior.
3. Refreshed the focused platform-service regression coverage plus the
   platform-service abstraction and `RW-G01` gap note so the retained client
   lobby callback lane now matches the same explicit compatibility-labeling
   story as the other active online-service seams.

### Task A3ad: Expose explicit provider/policy labeling through the retained client callback connect-handoff lane [COMPLETED]
Priority: Critical
Primary areas: `src/code/client/cl_main.c`, `tests/test_platform_services.py`,
`docs/steam_platform_abstraction.md`,
`docs/reverse-engineering/source-file-gap-notes/rw-g01-platform-services.md`
Parity estimate: **before 96% -> after 96%**

Completed work:

1. Routed the retained rich-presence join and server-change callback handoff
   through the shared matchmaking callback logger so the immediate
   join/connect command path now reports the active provider/policy pair
   instead of silently executing callback payloads.
2. Added bounded callback detail for missing join commands, missing server
   targets, and password-seeded server-connect handoff without changing the
   legacy immediate-command behavior or the outward connect payload shape.
3. Refreshed the focused platform-service regression coverage plus the
   platform-service abstraction and `RW-G01` gap note so the retained client
   callback connect-handoff lane now matches the same explicit
   compatibility-labeling story as the other active online-service seams.

### Task A3ae: Expose explicit provider/policy labeling through the retained client stats callback lane [COMPLETED]
Priority: Critical
Primary areas: `src/code/client/cl_main.c`, `tests/test_platform_services.py`,
`docs/steam_platform_abstraction.md`,
`docs/reverse-engineering/source-file-gap-notes/rw-g01-platform-services.md`
Parity estimate: **before 96% -> after 96%**

Completed work:

1. Added a shared stats callback logger so the retained user-stats callback
   owner now reports the active stats provider/policy pair instead of only
   becoming visible once the browser-event queue publishes the resulting
   payload.
2. Routed the `users.stats.*.received` callback path through that helper with
   bounded SteamID, game-ID, and result detail while preserving the legacy
   browser-event payload shape and queue semantics.
3. Refreshed the focused platform-service regression coverage plus the
   platform-service abstraction and `RW-G01` gap note so the retained client
   stats callback lane now matches the same explicit compatibility-labeling
   story as the other active online-service seams.

### Task A3af: Expose explicit provider/policy labeling through the retained client social-presence and UGC callback lanes [COMPLETED]
Priority: Critical
Primary areas: `src/code/client/cl_main.c`, `tests/test_platform_services.py`,
`docs/steam_platform_abstraction.md`,
`docs/reverse-engineering/source-file-gap-notes/rw-g01-platform-services.md`
Parity estimate: **before 96% -> after 96%**

Completed work:

1. Routed the retained client persona-state and friend-rich-presence callback
   owners through the shared matchmaking callback logger so those
   browser-facing presence updates now report the active provider/policy pair
   instead of only becoming visible when the shared queue publishes them.
2. Routed the retained client UGC query-complete callback through the
   workshop lifecycle logger with bounded call/query/result detail while
   preserving the legacy `web.ugc.results` / `web.ugc.failed` payload shapes
   and browser event names.
3. Refreshed the focused platform-service regression coverage plus the
   platform-service abstraction and `RW-G01` gap note so the retained client
   social-presence and UGC callback lanes now match the same explicit
   compatibility-labeling story as the other active online-service seams.

### Task A3ag: Expose explicit provider/policy labeling through the retained client workshop callback lane [COMPLETED]
Priority: Critical
Primary areas: `src/code/client/cl_main.c`, `tests/test_platform_services.py`,
`docs/steam_platform_abstraction.md`,
`docs/reverse-engineering/source-file-gap-notes/rw-g01-platform-services.md`
Parity estimate: **before 96% -> after 96%**

Completed work:

1. Routed the retained client workshop `ItemInstalled` and
   `DownloadItemResult` callback owners through provider/policy-aware
   lifecycle diagnostics so tracked completion, untracked-item ignore, and
   result-failure exits are explicit instead of only becoming visible through
   the downstream queue helpers.
2. Kept the existing workshop queue behavior intact: item completion still
   flows through `CL_Workshop_FinalizeInstalledItem()`, failures still flow
   through `CL_Workshop_FailActiveDownload()`, and the legacy queue-advance
   behavior remains unchanged.
3. Refreshed the focused platform-service regression coverage plus the
   platform-service abstraction and `RW-G01` gap note so the retained client
   workshop callback lane now matches the same explicit
   compatibility-labeling story as the other active online-service seams.

### Task A3ah: Expose explicit provider/policy labeling through the retained dedicated-server connection callback lane [COMPLETED]
Priority: Critical
Primary areas: `src/code/server/sv_client.c`,
`tests/test_platform_services.py`,
`docs/steam_platform_abstraction.md`,
`docs/reverse-engineering/source-file-gap-notes/rw-g01-platform-services.md`
Parity estimate: **before 96% -> after 96%**

Completed work:

1. Routed the retained Steam GameServer connected, connect-failure, and
   disconnected callbacks through a shared provider/policy-aware callback
   lifecycle logger so those server callback-owner state changes no longer
   appear as isolated one-off print lines.
2. Kept the existing server behavior intact: successful connects still publish
   identity and refreshed published state, failure/disconnect callbacks still
   clear the connected flag, and no auth/session routing changed.
3. Refreshed the focused platform-service regression coverage plus the
   platform-service abstraction and `RW-G01` gap note so the retained
   dedicated-server connection callback lane now matches the same explicit
   compatibility-labeling story as the other active online-service seams.

### Task A3ai: Expose explicit provider/policy labeling through the retained client workshop callback bootstrap gate [COMPLETED]
Priority: Critical
Primary areas: `src/code/client/cl_main.c`, `tests/test_platform_services.py`,
`docs/steam_platform_abstraction.md`,
`docs/reverse-engineering/source-file-gap-notes/rw-g01-platform-services.md`
Parity estimate: **before 96% -> after 96%**

Completed work:

1. Routed the retained client workshop callback registration-failure path
   through the shared workshop lifecycle logger so the polling-only fallback is
   explicit about the active provider/policy pair instead of appearing as a
   one-off raw debug line.
2. Kept the existing bootstrap behavior intact: the client still enables the
   main callback bundle, leaves workshop progress on the polling fallback when
   workshop callback registration fails, and does not change queue or browser
   event behavior.
3. Refreshed the focused platform-service regression coverage plus the
   platform-service abstraction and `RW-G01` gap note so the retained client
   workshop callback bootstrap gate now matches the same explicit
   compatibility-labeling story as the other active online-service seams.

### Task A3aj: Expose explicit provider/policy labeling through the retained dedicated-server identity publication lane [COMPLETED]
Priority: Critical
Primary areas: `src/code/server/sv_init.c`, `tests/test_platform_services.py`,
`docs/steam_platform_abstraction.md`,
`docs/reverse-engineering/source-file-gap-notes/rw-g01-platform-services.md`
Parity estimate: **before 96% -> after 96%**

Completed work:

1. Routed the retained Steam GameServer identity-publication owner through a
   shared provider/policy-aware lifecycle logger so both the unavailable and
   successful publish paths are explicit instead of only surfacing a raw
   identity-unavailable debug line.
2. Kept the existing identity behavior intact: the server still publishes the
   `0x2ca` SteamID configstring, mirrors `sv_referencedSteamworks`, and writes
   the `0x2cb` referenced-workshop configstring without changing the outward
   contract.
3. Refreshed the focused platform-service regression coverage plus the
   platform-service abstraction and `RW-G01` gap note so the retained
   dedicated-server identity publication lane now matches the same explicit
   compatibility-labeling story as the other active online-service seams.

### Task A3ak: Expose explicit provider/policy labeling through the retained dedicated-server callback bootstrap gate [COMPLETED]
Priority: Critical
Primary areas: `src/code/server/sv_client.c`, `tests/test_platform_services.py`,
`docs/steam_platform_abstraction.md`,
`docs/reverse-engineering/source-file-gap-notes/rw-g01-platform-services.md`
Parity estimate: **before 96% -> after 96%**

Completed work:

1. Routed the retained Steam GameServer callback-registration fallback through
   a provider/policy-aware bootstrap lifecycle logger in both the live
   registration-failure path and the build-disabled stub path instead of
   leaving those exits as raw one-off debug lines.
2. Kept the existing callback-registration behavior intact: successful
   registration still clears `sv_steamServerConnected`, while the unavailable
   paths still return immediately after surfacing the explicit compatibility
   diagnostic.
3. Refreshed the focused platform-service regression coverage plus the
   platform-service abstraction and `RW-G01` gap note so the retained
   dedicated-server callback bootstrap gate now matches the same explicit
   compatibility-labeling story as the other active server-owned seams.

### Task A3al: Expose explicit provider/policy labeling through the retained client callback bootstrap gate [COMPLETED]
Priority: Critical
Primary areas: `src/code/client/cl_main.c`, `tests/test_platform_services.py`,
`docs/steam_platform_abstraction.md`,
`docs/reverse-engineering/source-file-gap-notes/rw-g01-platform-services.md`
Parity estimate: **before 96% -> after 96%**

Completed work:

1. Routed the retained client callback-bundle fallback through a shared
   provider-aware bootstrap logger so the services-disabled and
   registration-failure exits now spell out the active matchmaking, stats, and
   social-overlay provider/policy pairs instead of staying as raw one-off
   debug lines.
2. Kept the existing callback bootstrap behavior intact: the client still
   clears the browser-event and lobby state before registration, still returns
   early when online services stay disabled, and still unregisters the partial
   client/lobby/micro callback bundle before falling back.
3. Refreshed the focused platform-service regression coverage plus the
   platform-service abstraction and `RW-G01` gap note so the retained client
   callback bootstrap gate now matches the same explicit compatibility-labeling
   story as the other active client-owned seams.

### Task A3am: Expose explicit provider/policy labeling through the retained client workshop required-items bootstrap gate [COMPLETED]
Priority: Critical
Primary areas: `src/code/client/cl_main.c`, `tests/test_platform_services.py`,
`docs/steam_platform_abstraction.md`,
`docs/reverse-engineering/source-file-gap-notes/rw-g01-platform-services.md`
Parity estimate: **before 96% -> after 96%**

Completed work:

1. Routed the retained client workshop required-items bootstrap fallback
   through the shared workshop lifecycle logger so the non-Steam/bootstrap-
   unavailable exit no longer stays as a raw one-off print line.
2. Kept the existing workshop bootstrap behavior intact: the client still logs
   the server-published required item list, still returns immediately when the
   current workshop lane cannot own Steam bootstrap, and still preserves the
   existing queue setup once a Steam UGC owner is available.
3. Refreshed the focused platform-service regression coverage plus the
   platform-service abstraction and `RW-G01` gap note so the retained client
   workshop required-items bootstrap gate now matches the same explicit
   compatibility-labeling story as the other active workshop seams.

### Task A3an: Expose explicit provider/policy labeling through the retained dedicated-server stats request/session lifecycle lane [COMPLETED]
Priority: Critical
Primary areas: `src/code/server/sv_client.c`,
`tests/test_platform_services.py`, `docs/steam_platform_abstraction.md`,
`docs/reverse-engineering/source-file-gap-notes/rw-g01-platform-services.md`
Parity estimate: **before 96% -> after 96%**

Completed work:

1. Routed successful stats request issue plus the active-session reuse, fresh
   session-bootstrap, and backend reconnect requery transitions through the
   shared stats lifecycle logger, so those retained GameServerStats success
   paths now surface the same provider/policy pair as the existing failure
   diagnostics.
2. Kept the retained stats owner behavior intact: existing request issuance,
   session reset/bootstrap, P2P hello delivery, and reconnect-driven requery
   semantics all remain unchanged apart from the new explicit compatibility
   labels.
3. Refreshed the focused platform-service regression coverage plus the
   platform-service abstraction and `RW-G01` gap note so the retained
   dedicated-server stats owner now documents the same explicit
   compatibility-labeling story on both its request and session lifecycle
   paths.

### Task A3ao: Expose explicit provider/policy labeling through the retained dedicated-server stats publish/store lane [COMPLETED]
Priority: Critical
Primary areas: `src/code/server/sv_client.c`,
`tests/test_platform_services.py`, `docs/steam_platform_abstraction.md`,
`docs/reverse-engineering/source-file-gap-notes/rw-g01-platform-services.md`
Parity estimate: **before 96% -> after 96%**

Completed work:

1. Routed the retained stats pending-value flush path through the shared stats
   lifecycle logger so stat publish failures, achievement publish failures,
   store-request failure, and successful store completion now all surface the
   same provider/policy pair instead of failing silently inside the
   GameServerStats owner.
2. Kept the retained stats owner behavior intact: dirty stat/achievement
   accumulation, backend store submission, and dirty-bit clearing still follow
   the same recovered control flow, with the new compatibility labels only
   documenting the existing publish/store decisions.
3. Refreshed the focused platform-service regression coverage plus the
   platform-service abstraction and `RW-G01` gap note so the retained
   dedicated-server stats owner now documents the same explicit
   compatibility-labeling story across its request, session, and publish/store
   lifecycle paths.

### Task A3ap: Expose explicit provider/policy labeling through the retained dedicated-server stats query/load lane [COMPLETED]
Priority: Critical
Primary areas: `src/code/server/sv_client.c`,
`tests/test_platform_services.py`, `docs/steam_platform_abstraction.md`,
`docs/reverse-engineering/source-file-gap-notes/rw-g01-platform-services.md`
Parity estimate: **before 96% -> after 96%**

Completed work:

1. Routed the retained `GetUserStatInt` and `GetUserAchievement` fetch paths
   through the shared stats lifecycle logger so stat/achievement query
   success and failure now surface the same provider/policy pair instead of
   silently returning through the dedicated-server `GameServerStats` owner.
2. Kept the retained stats owner behavior intact: request issuance, cached
   value reuse, pending-delta accumulation, and achievement unlock decisions
   still follow the same recovered control flow, with the new compatibility
   labels only documenting the existing query/load outcomes.
3. Refreshed the focused platform-service regression coverage plus the
   platform-service abstraction and `RW-G01` gap note so the retained
   dedicated-server stats owner now documents the same explicit
   compatibility-labeling story across its request, session, query, and
   publish/store lifecycle paths.

### Task A3aq: Expose explicit provider/policy labeling through the retained dedicated-server stats achievement owner/query lane [COMPLETED]
Priority: Critical
Primary areas: `src/code/server/sv_client.c`,
`tests/test_platform_services.py`, `docs/steam_platform_abstraction.md`,
`docs/reverse-engineering/source-file-gap-notes/rw-g01-platform-services.md`
Parity estimate: **before 96% -> after 96%**

Completed work:

1. Routed the retained achievement-owner entry points through the shared stats
   lifecycle logger so invalid-achievement, gameplay-gated, unavailable,
   session-unavailable, already-held, queued-unlock, and ownership-result
   outcomes now surface the same provider/policy pair instead of returning
   silently through the active `GameServerStats` owner.
2. Kept the retained stats owner behavior intact: achievement gate checks,
   session bootstrap, cached ownership reuse, and pending unlock/store flows
   still follow the same recovered control flow, with the new compatibility
   labels only documenting the existing owner/query decisions.
3. Refreshed the focused platform-service regression coverage plus the
   platform-service abstraction and `RW-G01` gap note so the retained
   dedicated-server stats owner now documents the same explicit
   compatibility-labeling story across its request, session, query,
   achievement-owner, and publish/store lifecycle paths.

### Task A3ar: Expose explicit provider/policy labeling through the retained dedicated-server stats field-owner lane [COMPLETED]
Priority: Critical
Primary areas: `src/code/server/sv_client.c`,
`tests/test_platform_services.py`, `docs/steam_platform_abstraction.md`,
`docs/reverse-engineering/source-file-gap-notes/rw-g01-platform-services.md`
Parity estimate: **before 96% -> after 96%**

Completed work:

1. Routed the retained stat-delta owner entry point through the shared stats
   lifecycle logger so invalid/no-op, unavailable, session-unavailable, and
   baseline-unavailable queue decisions now surface the same provider/policy
   pair instead of returning silently through the active `GameServerStats`
   owner.
2. Kept the retained stats owner behavior intact: stat lookup, session
   bootstrap, pending-delta accumulation, and dirty-bit publication still
   follow the same recovered control flow, with the new compatibility labels
   only documenting the existing field-owner decisions.
3. Refreshed the focused platform-service regression coverage plus the
   platform-service abstraction and `RW-G01` gap note so the retained
   dedicated-server stats owner now documents the same explicit
   compatibility-labeling story across its request, session, query,
   field-owner, achievement-owner, and publish/store lifecycle paths.

### Task A3as: Expose explicit provider/policy labeling through the retained dedicated-server stats session-teardown lane [COMPLETED]
Priority: Critical
Primary areas: `src/code/server/sv_client.c`,
`tests/test_platform_services.py`, `docs/steam_platform_abstraction.md`,
`docs/reverse-engineering/source-file-gap-notes/rw-g01-platform-services.md`
Parity estimate: **before 96% -> after 96%**

Completed work:

1. Routed the retained stats session-teardown helper through the shared stats
   lifecycle logger so inactive-session skips and completed session clears now
   surface the same provider/policy pair instead of returning silently during
   auth/session shutdown.
2. Kept the retained teardown behavior intact: pending stat/achievement flush,
   session reset, and caller-owned auth shutdown sequencing still follow the
   same recovered control flow, with the new compatibility labels only
   documenting the existing session-clear decisions.
3. Refreshed the focused platform-service regression coverage plus the
   platform-service abstraction and `RW-G01` gap note so the retained
   dedicated-server stats owner now documents the same explicit
   compatibility-labeling story across its request, session, query,
   field-owner, achievement-owner, session-teardown, and publish/store
   lifecycle paths.

### Task A3at: Expose explicit provider/policy labeling through the retained dedicated-server stats session-bootstrap gate [COMPLETED]
Priority: Critical
Primary areas: `src/code/server/sv_client.c`,
`tests/test_platform_services.py`, `docs/steam_platform_abstraction.md`,
`docs/reverse-engineering/source-file-gap-notes/rw-g01-platform-services.md`
Parity estimate: **before 96% -> after 96%**

Completed work:

1. Routed the retained stats session-bootstrap gate through the shared stats
   lifecycle logger so null, out-of-range, zombie, missing-gentity,
   missing-SteamID, bot-owned, and invalid-SteamID skips now surface the same
   provider/policy pair instead of returning silently before session creation.
2. Kept the retained bootstrap behavior intact: valid clients still reuse live
   sessions, still create/reset sessions the same way, still request current
   values, and still send the Steam P2P hello packet with the same recovered
   control flow.
3. Refreshed the focused platform-service regression coverage plus the
   platform-service abstraction and `RW-G01` gap note so the retained
   dedicated-server stats owner now documents the same explicit
   compatibility-labeling story across its request, session-bootstrap, query,
   field-owner, achievement-owner, session-teardown, and publish/store
   lifecycle paths.

### Task A3au: Expose explicit provider/policy labeling through the retained dedicated-server stats client-slot gate [COMPLETED]
Priority: Critical
Primary areas: `src/code/server/sv_client.c`,
`tests/test_platform_services.py`, `docs/steam_platform_abstraction.md`,
`docs/reverse-engineering/source-file-gap-notes/rw-g01-platform-services.md`
Parity estimate: **before 96% -> after 96%**

Completed work:

1. Routed the retained stats client-slot helper through the shared stats
   lifecycle logger so out-of-range, inactive, zombie, missing-gentity,
   missing-SteamID, bot-owned, and invalid-SteamID gating now surface the
   same provider/policy pair instead of returning silently before the field
   and achievement owners can explain why the request stopped.
2. Kept the retained owner behavior intact: valid stat/achievement callers
   still resolve the same live client slot, still bootstrap or reuse sessions
   the same way, and still apply the same field/achievement control flow once
   a valid slot is available.
3. Refreshed the focused platform-service regression coverage plus the
   platform-service abstraction and `RW-G01` gap note so the retained
   dedicated-server stats owner now documents the same explicit
   compatibility-labeling story across its request, session-bootstrap,
   client-slot, query, field-owner, achievement-owner, session-teardown, and
   publish/store lifecycle paths.

### Task A3av: Expose explicit provider/policy labeling through the retained dedicated-server stats request gate [COMPLETED]
Priority: Critical
Primary areas: `src/code/server/sv_client.c`,
`tests/test_platform_services.py`, `docs/steam_platform_abstraction.md`,
`docs/reverse-engineering/source-file-gap-notes/rw-g01-platform-services.md`
Parity estimate: **before 96% -> after 96%**

Completed work:

1. Routed the retained `SV_SteamStats_RequestCurrentValues` gate through the
   shared stats lifecycle logger so null-session, inactive-session, and
   missing-SteamID request skips now surface the same provider/policy pair
   instead of returning silently before the existing request issue/failure
   diagnostics run.
2. Kept the retained request behavior intact: valid sessions still issue the
   same `SteamGameServerStats` request, still mark `backendAvailable` and
   `requestIssued`, and still preserve the same success/failure control flow
   once the request gate is satisfied.
3. Refreshed the focused platform-service regression coverage plus the
   platform-service abstraction and `RW-G01` gap note so the retained
   dedicated-server stats owner now documents the same explicit
   compatibility-labeling story across its request gate, session-bootstrap,
   client-slot, query, field-owner, achievement-owner, session-teardown, and
   publish/store lifecycle paths.

### Task A3aw: Expose explicit provider/policy labeling through the retained dedicated-server stats value-query gate [COMPLETED]
Priority: Critical
Primary areas: `src/code/server/sv_client.c`,
`tests/test_platform_services.py`, `docs/steam_platform_abstraction.md`,
`docs/reverse-engineering/source-file-gap-notes/rw-g01-platform-services.md`
Parity estimate: **before 96% -> after 96%**

Completed work:

1. Routed the retained stat/achievement value-query gate through the shared
   stats lifecycle logger so null-session, inactive-session, invalid-id,
   unmapped-id, and already-cached paths now surface the same provider/policy
   pair instead of returning silently before the existing query result
   diagnostics run.
2. Kept the retained query behavior intact: valid uncached stat and
   achievement requests still issue the same backend reads, still apply the
   same pending-delta merge or cached ownership update, and still preserve the
   same success/failure control flow once the query gate is satisfied.
3. Refreshed the focused platform-service regression coverage plus the
   platform-service abstraction and `RW-G01` gap note so the retained
   dedicated-server stats owner now documents the same explicit
   compatibility-labeling story across its request gate, session-bootstrap,
   client-slot, value-query gate, field-owner, achievement-owner,
   session-teardown, and publish/store lifecycle paths.

### Task A3ax: Expose explicit provider/policy labeling through the retained dedicated-server stats value-flush gate [COMPLETED]
Priority: Critical
Primary areas: `src/code/server/sv_client.c`,
`tests/test_platform_services.py`, `docs/steam_platform_abstraction.md`,
`docs/reverse-engineering/source-file-gap-notes/rw-g01-platform-services.md`
Parity estimate: **before 96% -> after 96%**

Completed work:

1. Routed the retained `SV_SteamStats_FlushPendingValues` gate through the
   shared stats lifecycle logger so null-session, inactive-session,
   missing-SteamID, and no-pending-update skips now surface the same
   provider/policy pair instead of returning silently before the existing
   publish/store diagnostics run.
2. Kept the retained flush behavior intact: dirty stat/achievement scans,
   backend publish attempts, store submission, and dirty-bit clearing still
   follow the same recovered control flow once the flush gate is satisfied.
3. Refreshed the focused platform-service regression coverage plus the
   platform-service abstraction and `RW-G01` gap note so the retained
   dedicated-server stats owner now documents the same explicit
   compatibility-labeling story across its request gate, session-bootstrap,
   client-slot, value-query gate, value-flush gate, field-owner,
   achievement-owner, session-teardown, and publish/store lifecycle paths.

### Task A3ay: Expose explicit provider/policy labeling through the retained dedicated-server stats session-reset helper [COMPLETED]
Priority: Critical
Primary areas: `src/code/server/sv_client.c`,
`tests/test_platform_services.py`, `docs/steam_platform_abstraction.md`,
`docs/reverse-engineering/source-file-gap-notes/rw-g01-platform-services.md`
Parity estimate: **before 96% -> after 96%**

Completed work:

1. Routed the retained `SV_SteamStats_ResetSession` helper through the shared
   stats lifecycle logger so null-session skips and retained-session clears
   now surface the same provider/policy pair instead of clearing state
   silently inside the dedicated-server `GameServerStats` owner.
2. Kept the retained reset behavior intact: session memory still clears with
   the same recovered `Com_Memset` flow, while the new compatibility labels
   only document when the helper is skipping or clearing retained state.
3. Refreshed the focused platform-service regression coverage plus the
   platform-service abstraction and `RW-G01` gap note so the retained
   dedicated-server stats owner now documents the same explicit
   compatibility-labeling story across its request gate, session-bootstrap,
   client-slot, value-query gate, value-flush gate, session-reset helper,
   field-owner, achievement-owner, session-teardown, and publish/store
   lifecycle paths.

### Task A3az: Expose explicit provider/policy labeling through the retained dedicated-server stats descriptor lookup helpers [COMPLETED]
Priority: Critical
Primary areas: `src/code/server/sv_client.c`,
`tests/test_platform_services.py`, `docs/steam_platform_abstraction.md`,
`docs/reverse-engineering/source-file-gap-notes/rw-g01-platform-services.md`
Parity estimate: **before 96% -> after 96%**

Completed work:

1. Routed the retained `SV_SteamStats_GetFieldName` and
   `SV_SteamStats_GetAchievementName` helpers through the shared stats
   lifecycle logger so invalid and unmapped descriptor lookups now surface the
   same provider/policy pair instead of returning silently beneath the
   dedicated-server `GameServerStats` owner.
2. Kept the retained stats behavior intact: the same caller-specific query,
   flush, stat-delta, and achievement owner paths still short-circuit on
   missing descriptors, while the helper signatures now accept the active
   lifecycle stage so those compatibility labels stay contextual.
3. Refreshed the focused platform-service regression coverage plus the
   platform-service abstraction and `RW-G01` gap note so the retained
   dedicated-server stats owner now documents the same explicit
   compatibility-labeling story across its descriptor lookup helpers,
   request gate, session-bootstrap, client-slot, value-query gate,
   value-flush gate, session-reset helper, field-owner, achievement-owner,
   session-teardown, and publish/store lifecycle paths.

### Task A3ba: Expose explicit provider/policy labeling through the retained client rich-presence join callback null-payload guard [COMPLETED]
Priority: Critical
Primary areas: `src/code/client/cl_main.c`,
`tests/test_platform_services.py`, `docs/steam_platform_abstraction.md`,
`docs/reverse-engineering/source-file-gap-notes/rw-g01-platform-services.md`
Parity estimate: **before 96% -> after 96%**

Completed work:

1. Routed the retained `CL_Steam_Client_OnRichPresenceJoinRequested` null-event
   guard through the shared matchmaking callback logger so the compatibility
   lane now labels ignored null join payloads instead of silently returning.
2. Kept the retained callback handoff intact: non-null join payloads still
   flow through `CL_Steam_OnRichPresenceJoinRequested` without behavioral
   changes beyond the new compatibility labeling.
3. Refreshed the focused platform-service regression coverage plus the
   platform-service abstraction and `RW-G01` gap note so this client callback
   owner now documents the same explicit compatibility-labeling story.

### Task A3bb: Expose explicit provider/policy labeling through the retained client user-stats callback null-payload guard [COMPLETED]
Priority: Critical
Primary areas: `src/code/client/cl_main.c`,
`tests/test_platform_services.py`, `docs/steam_platform_abstraction.md`,
`docs/reverse-engineering/source-file-gap-notes/rw-g01-platform-services.md`
Parity estimate: **before 96% -> after 96%**

Completed work:

1. Routed the retained `CL_Steam_Client_OnUserStatsReceived` null-event guard
   through the shared stats callback logger so ignored null payloads now
   surface the active provider/policy pair instead of dropping silently.
2. Kept the retained stats browser-event behavior intact for non-null payloads:
   user-stat JSON publishing still follows the same recovered control flow.
3. Refreshed the focused platform-service regression coverage plus the
   platform-service abstraction and `RW-G01` gap note so this client callback
   owner now documents the same explicit compatibility-labeling story.

### Task A3bc: Expose explicit provider/policy labeling through the retained client persona callback null-payload guard [COMPLETED]
Priority: Critical
Primary areas: `src/code/client/cl_main.c`,
`tests/test_platform_services.py`, `docs/steam_platform_abstraction.md`,
`docs/reverse-engineering/source-file-gap-notes/rw-g01-platform-services.md`
Parity estimate: **before 96% -> after 96%**

Completed work:

1. Routed the retained `CL_Steam_Client_OnPersonaStateChange` null-event guard
   through the shared matchmaking callback logger so ignored null persona
   payloads no longer return silently.
2. Kept the retained persona browser-event behavior intact for non-null
   payloads: the same summary formatting and publish path still applies.
3. Refreshed the focused platform-service regression coverage plus the
   platform-service abstraction and `RW-G01` gap note so this client callback
   owner now documents the same explicit compatibility-labeling story.

### Task A3bd: Expose explicit provider/policy labeling through the retained client P2P-session callback null-payload guard [COMPLETED]
Priority: Critical
Primary areas: `src/code/client/cl_main.c`,
`tests/test_platform_services.py`, `docs/steam_platform_abstraction.md`,
`docs/reverse-engineering/source-file-gap-notes/rw-g01-platform-services.md`
Parity estimate: **before 96% -> after 96%**

Completed work:

1. Routed the retained `CL_Steam_Client_OnP2PSessionRequest` null-event guard
   through the shared matchmaking callback logger so ignored null session
   payloads no longer return silently.
2. Kept the retained accept/fail logging and `QL_Steamworks_AcceptP2PSession`
   behavior intact for non-null payloads.
3. Refreshed the focused platform-service regression coverage plus the
   platform-service abstraction and `RW-G01` gap note so this client callback
   owner now documents the same explicit compatibility-labeling story.

### Task A3be: Expose explicit provider/policy labeling through the retained client server-change callback null-payload guard [COMPLETED]
Priority: Critical
Primary areas: `src/code/client/cl_main.c`,
`tests/test_platform_services.py`, `docs/steam_platform_abstraction.md`,
`docs/reverse-engineering/source-file-gap-notes/rw-g01-platform-services.md`
Parity estimate: **before 96% -> after 96%**

Completed work:

1. Routed the retained `CL_Steam_Client_OnGameServerChangeRequested`
   null-event guard through the shared matchmaking callback logger so ignored
   null server-change payloads no longer return silently.
2. Kept the retained connect handoff intact: non-null payloads still flow
   through `CL_Steam_OnGameServerChangeRequested` without behavioral changes.
3. Refreshed the focused platform-service regression coverage plus the
   platform-service abstraction and `RW-G01` gap note so this client callback
   owner now documents the same explicit compatibility-labeling story.

### Task A3bf: Expose explicit provider/policy labeling through the retained client friend rich-presence callback null-payload guard [COMPLETED]
Priority: Critical
Primary areas: `src/code/client/cl_main.c`,
`tests/test_platform_services.py`, `docs/steam_platform_abstraction.md`,
`docs/reverse-engineering/source-file-gap-notes/rw-g01-platform-services.md`
Parity estimate: **before 96% -> after 96%**

Completed work:

1. Routed the retained `CL_Steam_Client_OnFriendRichPresenceUpdate`
   null-event guard through the shared matchmaking callback logger so ignored
   null rich-presence payloads no longer return silently.
2. Kept the retained friend-summary formatting and browser-event publishing
   intact for non-null payloads.
3. Refreshed the focused platform-service regression coverage plus the
   platform-service abstraction and `RW-G01` gap note so this client callback
   owner now documents the same explicit compatibility-labeling story.

### Task A3bg: Expose explicit provider/policy labeling through the retained client UGC-query callback null-payload guard [COMPLETED]
Priority: Critical
Primary areas: `src/code/client/cl_main.c`,
`tests/test_platform_services.py`, `docs/steam_platform_abstraction.md`,
`docs/reverse-engineering/source-file-gap-notes/rw-g01-platform-services.md`
Parity estimate: **before 96% -> after 96%**

Completed work:

1. Routed the retained `CL_Steam_Client_OnUGCQueryCompleted` null-event guard
   through the shared workshop lifecycle logger so ignored null query payloads
   no longer return silently.
2. Kept the retained UGC result/failure browser-event publishing intact for
   non-null payloads.
3. Refreshed the focused platform-service regression coverage plus the
   platform-service abstraction and `RW-G01` gap note so this client callback
   owner now documents the same explicit compatibility-labeling story.

### Task A3bh: Expose explicit provider/policy labeling through the retained client lobby-created callback null-payload guard [COMPLETED]
Priority: Critical
Primary areas: `src/code/client/cl_main.c`,
`tests/test_platform_services.py`, `docs/steam_platform_abstraction.md`,
`docs/reverse-engineering/source-file-gap-notes/rw-g01-platform-services.md`
Parity estimate: **before 96% -> after 96%**

Completed work:

1. Routed the retained `CL_Steam_Lobby_OnLobbyCreated` null-event guard
   through the shared matchmaking callback logger so ignored null lobby-create
   payloads no longer return silently.
2. Kept the retained success/error lobby browser-event publishing intact for
   non-null payloads.
3. Refreshed the focused platform-service regression coverage plus the
   platform-service abstraction and `RW-G01` gap note so this client callback
   owner now documents the same explicit compatibility-labeling story.

### Task A3bi: Expose explicit provider/policy labeling through the retained client lobby-enter callback null-payload guard [COMPLETED]
Priority: Critical
Primary areas: `src/code/client/cl_main.c`,
`tests/test_platform_services.py`, `docs/steam_platform_abstraction.md`,
`docs/reverse-engineering/source-file-gap-notes/rw-g01-platform-services.md`
Parity estimate: **before 96% -> after 96%**

Completed work:

1. Routed the retained `CL_Steam_Lobby_OnLobbyEnter` null-event guard through
   the shared matchmaking callback logger so ignored null lobby-enter payloads
   no longer return silently.
2. Kept the retained lobby-enter success/error publishing and current-lobby
   tracking intact for non-null payloads.
3. Refreshed the focused platform-service regression coverage plus the
   platform-service abstraction and `RW-G01` gap note so this client callback
   owner now documents the same explicit compatibility-labeling story.

### Task A3bj: Expose explicit provider/policy labeling through the retained client lobby-chat-update callback null-payload guard [COMPLETED]
Priority: Critical
Primary areas: `src/code/client/cl_main.c`,
`tests/test_platform_services.py`, `docs/steam_platform_abstraction.md`,
`docs/reverse-engineering/source-file-gap-notes/rw-g01-platform-services.md`
Parity estimate: **before 96% -> after 96%**

Completed work:

1. Routed the retained `CL_Steam_Lobby_OnLobbyChatUpdate` null-event guard
   through the shared matchmaking callback logger so ignored null lobby-chat
   payloads no longer return silently.
2. Kept the retained user-summary formatting and join/leave browser-event
   publishing intact for non-null payloads.
3. Refreshed the focused platform-service regression coverage plus the
   platform-service abstraction and `RW-G01` gap note so this client callback
   owner now documents the same explicit compatibility-labeling story.

### Task A3bk: Expose explicit provider/policy labeling through the retained client lobby-chat-message callback null-payload guard [COMPLETED]
Priority: Critical
Primary areas: `src/code/client/cl_main.c`,
`tests/test_platform_services.py`, `docs/steam_platform_abstraction.md`,
`docs/reverse-engineering/source-file-gap-notes/rw-g01-platform-services.md`
Parity estimate: **before 96% -> after 96%**

Completed work:

1. Routed the retained `CL_Steam_Lobby_OnLobbyChatMessage` null-event guard
   through the shared matchmaking callback logger so ignored null lobby-chat
   message payloads no longer return silently.
2. Kept the retained friend-summary lookup, JSON escaping, and browser-event
   publishing intact for non-null payloads.
3. Refreshed the focused platform-service regression coverage plus the
   platform-service abstraction and `RW-G01` gap note so this client callback
   owner now documents the same explicit compatibility-labeling story.

### Task A3bl: Expose explicit provider/policy labeling through the retained client lobby-data-update callback null-payload guard [COMPLETED]
Priority: Critical
Primary areas: `src/code/client/cl_main.c`,
`tests/test_platform_services.py`, `docs/steam_platform_abstraction.md`,
`docs/reverse-engineering/source-file-gap-notes/rw-g01-platform-services.md`
Parity estimate: **before 96% -> after 96%**

Completed work:

1. Routed the retained `CL_Steam_Lobby_OnLobbyDataUpdate` null-event guard
   through the shared matchmaking callback logger so ignored null lobby-data
   update payloads no longer return silently.
2. Kept the retained lobby/member detail formatting and browser-event
   publishing intact for non-null payloads.
3. Refreshed the focused platform-service regression coverage plus the
   platform-service abstraction and `RW-G01` gap note so this client callback
   owner now documents the same explicit compatibility-labeling story.

### Task A3bm: Expose explicit provider/policy labeling through the retained client lobby-game-created callback null-payload guard [COMPLETED]
Priority: Critical
Primary areas: `src/code/client/cl_main.c`,
`tests/test_platform_services.py`, `docs/steam_platform_abstraction.md`,
`docs/reverse-engineering/source-file-gap-notes/rw-g01-platform-services.md`
Parity estimate: **before 96% -> after 96%**

Completed work:

1. Routed the retained `CL_Steam_Lobby_OnLobbyGameCreated` null-event guard
   through the shared matchmaking callback logger so ignored null lobby-game
   created payloads no longer return silently.
2. Kept the retained game-server detail formatting and browser-event
   publishing intact for non-null payloads.
3. Refreshed the focused platform-service regression coverage plus the
   platform-service abstraction and `RW-G01` gap note so this client callback
   owner now documents the same explicit compatibility-labeling story.

### Task A3bn: Expose explicit provider/policy labeling through the retained client lobby-kicked callback null-payload guard [COMPLETED]
Priority: Critical
Primary areas: `src/code/client/cl_main.c`,
`tests/test_platform_services.py`, `docs/steam_platform_abstraction.md`,
`docs/reverse-engineering/source-file-gap-notes/rw-g01-platform-services.md`
Parity estimate: **before 96% -> after 96%**

Completed work:

1. Routed the retained `CL_Steam_Lobby_OnLobbyKicked` null-event guard through
   the shared matchmaking callback logger so ignored null lobby-kicked
   payloads no longer return silently.
2. Kept the retained current-lobby clearing, detail formatting, and
   browser-event publishing intact for non-null payloads.
3. Refreshed the focused platform-service regression coverage plus the
   platform-service abstraction and `RW-G01` gap note so this client callback
   owner now documents the same explicit compatibility-labeling story.

### Task A3bo: Expose explicit provider/policy labeling through the retained client lobby-join-requested callback null-payload guard [COMPLETED]
Priority: Critical
Primary areas: `src/code/client/cl_main.c`,
`tests/test_platform_services.py`, `docs/steam_platform_abstraction.md`,
`docs/reverse-engineering/source-file-gap-notes/rw-g01-platform-services.md`
Parity estimate: **before 96% -> after 96%**

Completed work:

1. Routed the retained `CL_Steam_Lobby_OnGameLobbyJoinRequested` null-event
   guard through the shared matchmaking callback logger so ignored null
   join-requested payloads no longer return silently.
2. Kept the retained lobby/friend detail formatting and browser-event
   publishing intact for non-null payloads.
3. Refreshed the focused platform-service regression coverage plus the
   platform-service abstraction and `RW-G01` gap note so this client callback
   owner now documents the same explicit compatibility-labeling story.

### Task A3bp: Expose explicit provider/policy labeling through the retained client microtransaction authorization callback null-payload guard [COMPLETED]
Priority: Critical
Primary areas: `src/code/client/cl_main.c`,
`tests/test_platform_services.py`, `docs/steam_platform_abstraction.md`,
`docs/reverse-engineering/source-file-gap-notes/rw-g01-platform-services.md`
Parity estimate: **before 96% -> after 96%**

Completed work:

1. Routed the retained `CL_Steam_Micro_OnAuthorizationResponse` null-event
   guard through the shared microtransaction callback logger so ignored null
   authorization payloads no longer return silently.
2. Kept the retained purchase payload formatting and browser-event publishing
   intact for non-null payloads while extending the logger to spell out the
   null-payload compatibility path.
3. Refreshed the focused platform-service regression coverage plus the
   platform-service abstraction and `RW-G01` gap note so this client callback
   owner now documents the same explicit compatibility-labeling story.

### Task A3bq: Expose explicit provider/policy labeling through the retained client workshop item-installed callback null-payload guard [COMPLETED]
Priority: Critical
Primary areas: `src/code/client/cl_main.c`,
`tests/test_platform_services.py`, `docs/steam_platform_abstraction.md`,
`docs/reverse-engineering/source-file-gap-notes/rw-g01-platform-services.md`
Parity estimate: **before 96% -> after 96%**

Completed work:

1. Routed the retained `CL_Steam_Workshop_OnItemInstalled` null-event guard
   through the shared workshop lifecycle logger so ignored null item-installed
   payloads no longer return silently.
2. Kept the retained app-id validation, item lookup, and install-finalization
   behavior intact for non-null payloads.
3. Refreshed the focused platform-service regression coverage plus the
   platform-service abstraction and `RW-G01` gap note so this client callback
   owner now documents the same explicit compatibility-labeling story.

### Task A3br: Expose explicit provider/policy labeling through the retained client workshop item-installed inactive-download-state guard [COMPLETED]
Priority: Critical
Primary areas: `src/code/client/cl_main.c`,
`tests/test_platform_services.py`, `docs/steam_platform_abstraction.md`,
`docs/reverse-engineering/source-file-gap-notes/rw-g01-platform-services.md`
Parity estimate: **before 96% -> after 96%**

Completed work:

1. Routed the retained `CL_Steam_Workshop_OnItemInstalled` inactive-download
   guard through the shared workshop lifecycle logger so compatibility-owned
   installed callbacks now explain why no active download state can consume
   them.
2. Kept the retained unexpected-app-id, untracked-item, and install-complete
   handling intact once a live download state exists.
3. Refreshed the focused platform-service regression coverage plus the
   platform-service abstraction and `RW-G01` gap note so this workshop
   callback guard now documents the same explicit compatibility-labeling story.

### Task A3bs: Expose explicit provider/policy labeling through the retained client workshop download-result callback null-payload guard [COMPLETED]
Priority: Critical
Primary areas: `src/code/client/cl_main.c`,
`tests/test_platform_services.py`, `docs/steam_platform_abstraction.md`,
`docs/reverse-engineering/source-file-gap-notes/rw-g01-platform-services.md`
Parity estimate: **before 96% -> after 96%**

Completed work:

1. Routed the retained `CL_Steam_Workshop_OnDownloadItemResult` null-event
   guard through the shared workshop lifecycle logger so ignored null
   download-result payloads no longer return silently.
2. Kept the retained app-id validation, active-item matching, and
   success/failure completion handling intact for non-null payloads.
3. Refreshed the focused platform-service regression coverage plus the
   platform-service abstraction and `RW-G01` gap note so this workshop
   callback owner now documents the same explicit compatibility-labeling
   story.

### Task A3bt: Expose explicit provider/policy labeling through the retained client workshop download-result inactive-lane guards [COMPLETED]
Priority: Critical
Primary areas: `src/code/client/cl_main.c`,
`tests/test_platform_services.py`, `docs/steam_platform_abstraction.md`,
`docs/reverse-engineering/source-file-gap-notes/rw-g01-platform-services.md`
Parity estimate: **before 96% -> after 96%**

Completed work:

1. Routed the retained `CL_Steam_Workshop_OnDownloadItemResult`
   inactive-download-state and active-item-index guards through the shared
   workshop lifecycle logger so compatibility-owned download callbacks now
   explain why no active lane can consume them.
2. Kept the retained unexpected-app-id, inactive-item, and
   success/failure-completion handling intact once a live download lane exists.
3. Refreshed the focused platform-service regression coverage plus the
   platform-service abstraction and `RW-G01` gap note so these workshop guard
   exits now document the same explicit compatibility-labeling story.

### Task A3bu: Expose explicit provider/policy labeling through the retained dedicated-server connect-failure callback null-payload guard [COMPLETED]
Priority: Critical
Primary areas: `src/code/server/sv_client.c`,
`tests/test_platform_services.py`, `docs/steam_platform_abstraction.md`,
`docs/reverse-engineering/source-file-gap-notes/rw-g01-platform-services.md`
Parity estimate: **before 96% -> after 96%**

Completed work:

1. Routed the retained `SV_SteamServerConnectFailureCallback` null-event guard
   through the shared server-callback lifecycle logger so ignored null
   connect-failure payloads no longer return silently.
2. Kept the retained connected-flag clear and failure-result formatting intact
   for non-null payloads.
3. Refreshed the focused platform-service regression coverage plus the
   platform-service abstraction and `RW-G01` gap note so this dedicated-server
   callback owner now documents the same explicit compatibility-labeling story.

### Task A3bv: Expose explicit provider/policy labeling through the retained dedicated-server disconnected callback null-payload guard [COMPLETED]
Priority: Critical
Primary areas: `src/code/server/sv_client.c`,
`tests/test_platform_services.py`, `docs/steam_platform_abstraction.md`,
`docs/reverse-engineering/source-file-gap-notes/rw-g01-platform-services.md`
Parity estimate: **before 96% -> after 96%**

Completed work:

1. Routed the retained `SV_SteamServerDisconnectedCallback` null-event guard
   through the shared server-callback lifecycle logger so ignored null
   disconnect payloads no longer return silently.
2. Kept the retained connected-flag clear and disconnect-result formatting
   intact for non-null payloads.
3. Refreshed the focused platform-service regression coverage plus the
   platform-service abstraction and `RW-G01` gap note so this dedicated-server
   callback owner now documents the same explicit compatibility-labeling story.

### Task A3bw: Expose explicit provider/policy labeling through the retained dedicated-server auth-ticket callback null-payload guard [COMPLETED]
Priority: Critical
Primary areas: `src/code/server/sv_client.c`,
`tests/test_platform_services.py`, `docs/steam_platform_abstraction.md`,
`docs/reverse-engineering/source-file-gap-notes/rw-g01-platform-services.md`
Parity estimate: **before 96% -> after 96%**

Completed work:

1. Routed the retained `SV_SteamServerValidateAuthTicketResponseCallback`
   null-event guard through the shared server-callback lifecycle logger so
   ignored null auth-ticket payloads no longer return silently.
2. Kept the retained fake-VAC override, auth-state publication, and
   accept/drop handling intact for non-null payloads.
3. Refreshed the focused platform-service regression coverage plus the
   platform-service abstraction and `RW-G01` gap note so this dedicated-server
   callback owner now documents the same explicit compatibility-labeling story.

### Task A3bx: Expose explicit provider/policy labeling through the retained dedicated-server auth-ticket missing-client guard [COMPLETED]
Priority: Critical
Primary areas: `src/code/server/sv_client.c`,
`tests/test_platform_services.py`, `docs/steam_platform_abstraction.md`,
`docs/reverse-engineering/source-file-gap-notes/rw-g01-platform-services.md`
Parity estimate: **before 96% -> after 96%**

Completed work:

1. Routed the retained `SV_SteamServerValidateAuthTicketResponseCallback`
   missing-client guard through the shared server-callback lifecycle logger so
   auth responses for no-longer-tracked clients no longer return silently.
2. Kept the retained client lookup and finalise/drop behavior intact once one
   live client session still owns the callback.
3. Refreshed the focused platform-service regression coverage plus the
   platform-service abstraction and `RW-G01` gap note so this dedicated-server
   callback owner now documents the same explicit compatibility-labeling story.

### Task A3by: Expose explicit provider/policy labeling through the retained dedicated-server P2P-session-request callback null-payload guard [COMPLETED]
Priority: Critical
Primary areas: `src/code/server/sv_client.c`,
`tests/test_platform_services.py`, `docs/steam_platform_abstraction.md`,
`docs/reverse-engineering/source-file-gap-notes/rw-g01-platform-services.md`
Parity estimate: **before 96% -> after 96%**

Completed work:

1. Routed the retained `SV_SteamServerP2PSessionRequestCallback` null-event
   guard through the shared P2P-session lifecycle logger so ignored null
   session-request payloads no longer return silently.
2. Kept the retained client lookup, auth gate, and accept-call failure
   handling intact for non-null payloads.
3. Refreshed the focused platform-service regression coverage plus the
   platform-service abstraction and `RW-G01` gap note so this dedicated-server
   callback owner now documents the same explicit compatibility-labeling story.

### Task A3bz: Expose explicit provider/policy labeling through the Steamworks servers-connected dispatch guard [COMPLETED]
Priority: Critical
Primary areas: `src/common/platform/platform_steamworks.c`,
`tests/test_platform_services.py`, `docs/steam_platform_abstraction.md`,
`docs/reverse-engineering/source-file-gap-notes/rw-g01-platform-services.md`
Parity estimate: **before 96% -> after 96%**

Completed work:

1. Added a shared `QL_Steamworks_LogServerCallbackDispatch` helper and routed
   the retained `QL_Steamworks_DispatchServersConnected` missing-state and
   missing-binding guards through it so that dispatcher no longer returns
   silently.
2. Kept the retained zeroed event bootstrap and callback invocation intact
   once one registered dispatch target exists.
3. Refreshed the focused platform-service regression coverage plus the
   platform-service abstraction and `RW-G01` gap note so this dispatcher guard
   now documents the same explicit compatibility-labeling story.

### Task A3ca: Expose explicit provider/policy labeling through the Steamworks connect-failure dispatch guards [COMPLETED]
Priority: Critical
Primary areas: `src/common/platform/platform_steamworks.c`,
`tests/test_platform_services.py`, `docs/steam_platform_abstraction.md`,
`docs/reverse-engineering/source-file-gap-notes/rw-g01-platform-services.md`
Parity estimate: **before 96% -> after 96%**

Completed work:

1. Routed the retained `QL_Steamworks_DispatchServerConnectFailure`
   missing-state, missing-binding, and missing-payload guards through the
   shared server-dispatch logger so that dispatcher no longer returns
   silently.
2. Kept the retained raw-event translation and callback invocation intact once
   one valid dispatch surface and payload exist.
3. Refreshed the focused platform-service regression coverage plus the
   platform-service abstraction and `RW-G01` gap note so these dispatcher
   guards now document the same explicit compatibility-labeling story.

### Task A3cb: Expose explicit provider/policy labeling through the Steamworks disconnected dispatch guards [COMPLETED]
Priority: Critical
Primary areas: `src/common/platform/platform_steamworks.c`,
`tests/test_platform_services.py`, `docs/steam_platform_abstraction.md`,
`docs/reverse-engineering/source-file-gap-notes/rw-g01-platform-services.md`
Parity estimate: **before 96% -> after 96%**

Completed work:

1. Routed the retained `QL_Steamworks_DispatchServersDisconnected`
   missing-state, missing-binding, and missing-payload guards through the
   shared server-dispatch logger so that dispatcher no longer returns
   silently.
2. Kept the retained raw-event translation and callback invocation intact once
   one valid dispatch surface and payload exist.
3. Refreshed the focused platform-service regression coverage plus the
   platform-service abstraction and `RW-G01` gap note so these dispatcher
   guards now document the same explicit compatibility-labeling story.

### Task A3cc: Expose explicit provider/policy labeling through the Steamworks auth-ticket dispatch guards [COMPLETED]
Priority: Critical
Primary areas: `src/common/platform/platform_steamworks.c`,
`tests/test_platform_services.py`, `docs/steam_platform_abstraction.md`,
`docs/reverse-engineering/source-file-gap-notes/rw-g01-platform-services.md`
Parity estimate: **before 96% -> after 96%**

Completed work:

1. Routed the retained `QL_Steamworks_DispatchValidateAuthTicketResponse`
   missing-state, missing-binding, and missing-payload guards through the
   shared server-dispatch logger so that dispatcher no longer returns
   silently.
2. Kept the retained raw auth-ticket response translation and callback
   invocation intact once one valid dispatch surface and payload exist.
3. Refreshed the focused platform-service regression coverage plus the
   platform-service abstraction and `RW-G01` gap note so these dispatcher
   guards now document the same explicit compatibility-labeling story.

### Task A3cd: Expose explicit provider/policy labeling through the Steamworks P2P-session-request dispatch guards [COMPLETED]
Priority: Critical
Primary areas: `src/common/platform/platform_steamworks.c`,
`tests/test_platform_services.py`, `docs/steam_platform_abstraction.md`,
`docs/reverse-engineering/source-file-gap-notes/rw-g01-platform-services.md`
Parity estimate: **before 96% -> after 96%**

Completed work:

1. Routed the retained `QL_Steamworks_DispatchServerP2PSessionRequest`
   missing-state, missing-binding, and missing-payload guards through the
   shared server-dispatch logger so that dispatcher no longer returns
   silently.
2. Kept the retained raw P2P-session translation and callback invocation
   intact once one valid dispatch surface and payload exist.
3. Refreshed the focused platform-service regression coverage plus the
   platform-service abstraction and `RW-G01` gap note so these dispatcher
   guards now document the same explicit compatibility-labeling story.

### Task A3ce: Restore the retail direct-request workshop detail string [COMPLETED]
Priority: Critical
Primary areas: `src/code/client/cl_main.c`, `tests/test_platform_services.py`,
`docs/steam_platform_abstraction.md`,
`docs/reverse-engineering/source-file-gap-notes/rw-g01-platform-services.md`
Parity estimate: **before 96% -> after 96%**

Completed work:

1. Updated the retained client workshop direct-request lane so it now reuses
   the retail-observed `Workshop item %llu: requesting download.` detail.
2. Kept the existing compatibility wrapper ownership and queue-state updates
   intact around that retail string restoration.
3. Refreshed the focused regression coverage and the matching abstraction/gap
   notes for the workshop request lane.

### Task A3cf: Restore the retail queued-request workshop detail string [COMPLETED]
Priority: Critical
Primary areas: `src/code/client/cl_main.c`, `tests/test_platform_services.py`,
`docs/steam_platform_abstraction.md`,
`docs/reverse-engineering/source-file-gap-notes/rw-g01-platform-services.md`
Parity estimate: **before 96% -> after 96%**

Completed work:

1. Updated the retained client workshop bootstrap queueing lane so it now
   reuses the retail-observed `Workshop item %llu: queueing download.` detail.
2. Kept the existing deferred-download state model intact around that retail
   string restoration.
3. Refreshed the focused regression coverage and the matching abstraction/gap
   notes for the queued-request lane.

### Task A3cg: Restore the retail workshop cache-hit detail string [COMPLETED]
Priority: Critical
Primary areas: `src/code/client/cl_main.c`, `tests/test_platform_services.py`,
`docs/steam_platform_abstraction.md`,
`docs/reverse-engineering/source-file-gap-notes/rw-g01-platform-services.md`
Parity estimate: **before 96% -> after 96%**

Completed work:

1. Updated the retained client workshop bootstrap cache-hit lane so it now
   reuses the retail-observed `Workshop item %llu: in cache.` detail.
2. Kept the existing cached-item completion handling intact around that retail
   string restoration.
3. Refreshed the focused regression coverage and the matching abstraction/gap
   notes for the cache-hit lane.

### Task A3ch: Restore the retail queued-handoff workshop detail string [COMPLETED]
Priority: Critical
Primary areas: `src/code/client/cl_main.c`, `tests/test_platform_services.py`,
`docs/steam_platform_abstraction.md`,
`docs/reverse-engineering/source-file-gap-notes/rw-g01-platform-services.md`
Parity estimate: **before 96% -> after 96%**

Completed work:

1. Updated the retained client workshop queue-advance lane so it now reuses
   the retail-observed `Workshop item %llu: was queued, requesting download.`
   detail.
2. Kept the existing queue-advance ownership and state updates intact around
   that retail string restoration.
3. Refreshed the focused regression coverage and the matching abstraction/gap
   notes for the queued handoff lane.

### Task A3ci: Restore the retail workshop completion detail string [COMPLETED]
Priority: Critical
Primary areas: `src/code/client/cl_main.c`, `tests/test_platform_services.py`,
`docs/steam_platform_abstraction.md`,
`docs/reverse-engineering/source-file-gap-notes/rw-g01-platform-services.md`
Parity estimate: **before 96% -> after 96%**

Completed work:

1. Updated the retained client workshop active-item completion lane so it now
   reuses the retail-observed `Steamworks download complete: %llu` detail.
2. Kept the existing active-download clear path intact around that retail
   string restoration.
3. Refreshed the focused regression coverage and the matching abstraction/gap
   notes for the workshop completion lane.

### Task A3cj: Restore the retail workshop queue-complete detail string [COMPLETED]
Priority: Critical
Primary areas: `src/code/client/cl_main.c`, `tests/test_platform_services.py`,
`docs/steam_platform_abstraction.md`,
`docs/reverse-engineering/source-file-gap-notes/rw-g01-platform-services.md`
Parity estimate: **before 96% -> after 96%**

Completed work:

1. Updated the retained client workshop queue-settled lane so it now reuses
   the retail-observed `Download completed for all steamworks items` detail.
2. Kept the existing queue-active reset behavior intact around that retail
   string restoration.
3. Refreshed the focused regression coverage and the matching abstraction/gap
   notes for the queue-complete lane.

### Task A3ck: Restore the retail workshop invalid-app skip detail in the item-installed callback [COMPLETED]
Priority: Critical
Primary areas: `src/code/client/cl_main.c`, `tests/test_platform_services.py`,
`docs/steam_platform_abstraction.md`,
`docs/reverse-engineering/source-file-gap-notes/rw-g01-platform-services.md`
Parity estimate: **before 96% -> after 96%**

Completed work:

1. Updated the retained client workshop item-installed invalid-app guard so it
   now reuses the retail-observed `OnDownloadItemResult skip, invalid app id
   %d` detail.
2. Kept the existing compatibility wrapper ownership intact around that
   observed retail string restoration.
3. Refreshed the focused regression coverage and the matching abstraction/gap
   notes for the item-installed invalid-app guard.

### Task A3cl: Restore the retail workshop invalid-app skip detail in the download-result callback [COMPLETED]
Priority: Critical
Primary areas: `src/code/client/cl_main.c`, `tests/test_platform_services.py`,
`docs/steam_platform_abstraction.md`,
`docs/reverse-engineering/source-file-gap-notes/rw-g01-platform-services.md`
Parity estimate: **before 96% -> after 96%**

Completed work:

1. Updated the retained client workshop download-result invalid-app guard so
   it now reuses the retail-observed `OnDownloadItemResult skip, invalid app
   id %d` detail.
2. Kept the existing callback wrapper ownership intact around that retail
   string restoration.
3. Refreshed the focused regression coverage and the matching abstraction/gap
   notes for the download-result invalid-app guard.

### Task A3cm: Restore the retail workshop active-download skip detail [COMPLETED]
Priority: Critical
Primary areas: `src/code/client/cl_main.c`, `tests/test_platform_services.py`,
`docs/steam_platform_abstraction.md`,
`docs/reverse-engineering/source-file-gap-notes/rw-g01-platform-services.md`
Parity estimate: **before 96% -> after 96%**

Completed work:

1. Updated the retained client workshop active-download mismatch guard so it
   now reuses the retail-observed `OnDownloadItemResult skip, not the active
   download %llu` detail.
2. Kept the existing active-item comparison and early-return behavior intact
   around that retail string restoration.
3. Refreshed the focused regression coverage and the matching abstraction/gap
   notes for the active-download skip lane.

### Task A3cn: Restore the retail workshop failure-result detail string [COMPLETED]
Priority: Critical
Primary areas: `src/code/client/cl_main.c`, `tests/test_platform_services.py`,
`docs/steam_platform_abstraction.md`,
`docs/reverse-engineering/source-file-gap-notes/rw-g01-platform-services.md`
Parity estimate: **before 96% -> after 96%**

Completed work:

1. Updated the retained client workshop download-result failure lane so it now
   reuses the retail-observed `Download item %llu failed with EResult code %i`
   detail.
2. Kept the existing failure-state and queue-advance behavior intact around
   that retail string restoration.
3. Refreshed the focused regression coverage and the matching abstraction/gap
   notes for the failure-result lane.

### Task A3co: Restore the retail workshop missing-`pak00.pk3` warning [COMPLETED]
Priority: Critical
Primary areas: `src/code/qcommon/files.c`, `tests/test_platform_services.py`,
`docs/steam_platform_abstraction.md`,
`docs/reverse-engineering/source-file-gap-notes/rw-g01-platform-services.md`
Parity estimate: **before 96% -> after 96%**

Completed work:

1. Updated the filesystem-side workshop startup lane so it now reuses the
   retail-observed `WARNING: Skipping workshop PK3s since pak00 doesn't
   exist.` detail.
2. Kept the retained workshop mount pass active after that warning, matching
   the retail mount-mode toggle instead of turning the warning into a hard
   return.
3. Refreshed the focused regression coverage and the matching abstraction/gap
   notes for the missing-`pak00.pk3` guard.

### Task A3cp: Restore the retail `fs_skipWorkshop` skip detail [COMPLETED]
Priority: Critical
Primary areas: `src/code/qcommon/files.c`, `tests/test_platform_services.py`,
`docs/steam_platform_abstraction.md`,
`docs/reverse-engineering/source-file-gap-notes/rw-g01-platform-services.md`
Parity estimate: **before 96% -> after 96%**

Completed work:

1. Updated the filesystem-side workshop startup lane so the
   `fs_skipWorkshop` gate now reuses the retail-observed `Skipping workshop
   since fs_skipWorkshop is set.` detail.
2. Kept the existing early-return ownership intact around that exact retail
   string restoration.
3. Refreshed the focused regression coverage and the matching abstraction/gap
   notes for the `fs_skipWorkshop` gate.

### Task A3cq: Restore the retail workshop build-mode skip detail [COMPLETED]
Priority: Critical
Primary areas: `src/code/qcommon/files.c`, `tests/test_platform_services.py`,
`docs/steam_platform_abstraction.md`,
`docs/reverse-engineering/source-file-gap-notes/rw-g01-platform-services.md`
Parity estimate: **before 96% -> after 96%**

Completed work:

1. Updated the filesystem-side workshop startup lane so the retained
   `com_build`/`com_buildScript` gate now reuses the retail-observed
   `Skipping workshop since running in build mode.` detail.
2. Kept the existing build-mode early return intact around that retail string
   restoration.
3. Refreshed the focused regression coverage and the matching abstraction/gap
   notes for the build-mode gate.

### Task A3cr: Restore the retail null-`ISteamUGC` skip detail [COMPLETED]
Priority: Critical
Primary areas: `src/code/qcommon/files.c`,
`src/common/platform/platform_steamworks.c`,
`src/common/platform/platform_steamworks.h`,
`tests/test_platform_services.py`,
`docs/steam_platform_abstraction.md`,
`docs/reverse-engineering/source-file-gap-notes/rw-g01-platform-services.md`
Parity estimate: **before 96% -> after 96%**

Completed work:

1. Updated the filesystem-side workshop startup lane so it now reuses the
   retail-observed `WARNING: Skipping workshop, ISteamUGC is NULL.` detail.
2. Kept the existing early-return behavior intact while splitting the null
   interface case away from the zero-subscribed-items case.
3. Refreshed the focused regression coverage and the matching abstraction/gap
   notes for the null-`ISteamUGC` guard.

### Task A3cs: Expose the exact workshop UGC-availability helper [COMPLETED]
Priority: Critical
Primary areas: `src/common/platform/platform_steamworks.c`,
`src/common/platform/platform_steamworks.h`,
`tests/test_platform_services.py`
Parity estimate: **before 96% -> after 96%**

Completed work:

1. Added `QL_Steamworks_HasUGCInterface()` so the retained workshop startup
   lane can distinguish a null `ISteamUGC` owner from an empty subscription
   list.
2. Kept the helper thin by routing it straight through the retained
   `QL_Steamworks_GetUGCInterface()` owner.
3. Refreshed the focused regression coverage for the new availability helper.

### Task A3ct: Restore the retail basepath-only `pak00.pk3` probe [COMPLETED]
Priority: Critical
Primary areas: `src/code/qcommon/files.c`, `tests/test_platform_services.py`
Parity estimate: **before 96% -> after 96%**

Completed work:

1. Updated `FS_HasBasePak0` so it now mirrors the retail
   `fs_basepath/baseq3/pak00.pk3` probe instead of scanning the broader local
   root set.
2. Kept the helper bounded to the workshop startup gate, matching the retail
   `SteamWorkshop_Init` ownership.
3. Refreshed the focused regression coverage for the basepath-only probe.

### Task A3cu: Restore the retail workshop raw-path mount toggle [COMPLETED]
Priority: Critical
Primary areas: `src/code/qcommon/files.c`, `tests/test_platform_services.py`
Parity estimate: **before 96% -> after 96%**

Completed work:

1. Updated the workshop mount pass so it now forwards the retained
   `mountRawPath` flag into `FS_AddGameDirectoryInternal` instead of always
   forcing the raw-path lane.
2. Mirrored the retail rule where the flag depends on whether `pak00.pk3` was
   present when workshop startup began.
3. Refreshed the focused regression coverage for the mount-mode toggle.

### Task A3cv: Restore the retail manual workshop direct-download detail [COMPLETED]
Priority: Critical
Primary areas: `src/code/server/sv_ccmds.c`,
`tests/test_platform_services.py`,
`tests/test_engine_operator_command_parity.py`,
`docs/steam_platform_abstraction.md`,
`docs/reverse-engineering/source-file-gap-notes/rw-g01-platform-services.md`
Parity estimate: **before 96% -> after 96%**

Completed work:

1. Updated the retained `steam_downloadugc` immediate-request lane so it now
   reuses the retail-observed `Workshop item %llu: download` detail.
2. Kept the existing provider/policy-aware operator logger intact around that
   exact retail string restoration.
3. Refreshed the focused regression coverage and the matching abstraction/gap
   notes for the direct-download lane.

### Task A3cw: Restore the retail manual workshop cache-hit detail [COMPLETED]
Priority: Critical
Primary areas: `src/code/server/sv_ccmds.c`,
`tests/test_platform_services.py`,
`tests/test_engine_operator_command_parity.py`,
`docs/steam_platform_abstraction.md`,
`docs/reverse-engineering/source-file-gap-notes/rw-g01-platform-services.md`
Parity estimate: **before 96% -> after 96%**

Completed work:

1. Updated the retained `steam_downloadugc` cache-hit lane so it now reuses
   the retail-observed `Workshop item %llu: in cache.` detail.
2. Kept the existing immediate-return ownership intact around that retail
   string restoration.
3. Refreshed the focused regression coverage and the matching abstraction/gap
   notes for the manual cache-hit lane.

### Task A3cx: Remove the non-retail manual download failure-only diagnostic [COMPLETED]
Priority: Critical
Primary areas: `src/code/server/sv_ccmds.c`,
`tests/test_platform_services.py`,
`tests/test_engine_operator_command_parity.py`,
`docs/steam_platform_abstraction.md`,
`docs/reverse-engineering/source-file-gap-notes/rw-g01-platform-services.md`
Parity estimate: **before 96% -> after 96%**

Completed work:

1. Updated the retained `steam_downloadugc` immediate-request lane so it no
   longer emits the extra compatibility-only `download request failed`
   diagnostic that retail never printed.
2. Kept the existing command registration and provider-gated command surface
   intact while mirroring the retail immediate-request call shape more closely.
3. Refreshed the focused regression coverage and the matching abstraction/gap
   notes for the removed non-retail failure-only diagnostic.

### Task A3cy: Remove the non-retail client workshop request-failure gate [COMPLETED]
Priority: Critical
Primary areas: `src/code/client/cl_main.c`, `tests/test_platform_services.py`,
`docs/steam_platform_abstraction.md`,
`docs/reverse-engineering/source-file-gap-notes/rw-g01-platform-services.md`
Parity estimate: **before 96% -> after 96%**

Completed work:

1. Updated `CL_Workshop_StartDownload` so it now ignores the raw
   `QL_Steamworks_DownloadItem` return value like the retail
   `SteamWorkshop_RequestDownload` owner.
2. Kept the existing queue-state and active-item updates intact around that
   control-flow restoration.
3. Refreshed the focused regression coverage and the matching abstraction/gap
   notes for the removed client request-failure gate.

### Task A3cz: Remove the non-retail client workshop request-failure detail [COMPLETED]
Priority: Critical
Primary areas: `src/code/client/cl_main.c`, `tests/test_platform_services.py`,
`docs/steam_platform_abstraction.md`,
`docs/reverse-engineering/source-file-gap-notes/rw-g01-platform-services.md`
Parity estimate: **before 96% -> after 96%**

Completed work:

1. Removed the extra `item %llu download request failed` detail from
   `CL_Workshop_StartDownload`, which retail never printed.
2. Kept the retained retail request strings unchanged around that removal.
3. Refreshed the focused regression coverage and the matching abstraction/gap
   notes for the removed request-failure detail.

### Task A3da: Remove the duplicate client workshop failure trace [COMPLETED]
Priority: Critical
Primary areas: `src/code/client/cl_main.c`, `tests/test_platform_services.py`,
`docs/steam_platform_abstraction.md`,
`docs/reverse-engineering/source-file-gap-notes/rw-g01-platform-services.md`
Parity estimate: **before 96% -> after 96%**

Completed work:

1. Updated `CL_Workshop_FailActiveDownload` so it no longer emits a second
   `item %llu failed with EResult code %i` trace after the callback owner has
   already logged the retail failure detail.
2. Kept the existing completed-state and active-download clear behavior intact.
3. Refreshed the focused regression coverage and the matching abstraction/gap
   notes for the removed duplicate failure trace.

### Task A3db: Restore the thin retail `steam_subscribeugc` command shape [COMPLETED]
Priority: Critical
Primary areas: `src/code/server/sv_ccmds.c`,
`tests/test_platform_services.py`,
`tests/test_engine_operator_command_parity.py`,
`docs/steam_platform_abstraction.md`,
`docs/reverse-engineering/source-file-gap-notes/rw-g01-platform-services.md`
Parity estimate: **before 96% -> after 96%**

Completed work:

1. Updated `SV_SteamCmd_SubscribeUGC_f` so it now mirrors the retail thin
   wrapper shape instead of stopping early behind the compatibility-only
   workshop-support gate.
2. Kept the existing one-argument item-ID parse surface intact.
3. Refreshed the focused regression coverage and the matching abstraction/gap
   notes for the subscribe command shape.

### Task A3dc: Remove the non-retail subscribe-request trace [COMPLETED]
Priority: Critical
Primary areas: `src/code/server/sv_ccmds.c`,
`tests/test_platform_services.py`,
`tests/test_engine_operator_command_parity.py`,
`docs/steam_platform_abstraction.md`,
`docs/reverse-engineering/source-file-gap-notes/rw-g01-platform-services.md`
Parity estimate: **before 96% -> after 96%**

Completed work:

1. Removed the extra `subscribe requested` diagnostic from
   `SV_SteamCmd_SubscribeUGC_f`, which retail never printed.
2. Kept the retained command registration and parse surface unchanged.
3. Refreshed the focused regression coverage and the matching abstraction/gap
   notes for the removed subscribe-request trace.

### Task A3dd: Remove the non-retail subscribe-failure trace [COMPLETED]
Priority: Critical
Primary areas: `src/code/server/sv_ccmds.c`,
`tests/test_platform_services.py`,
`tests/test_engine_operator_command_parity.py`,
`docs/steam_platform_abstraction.md`,
`docs/reverse-engineering/source-file-gap-notes/rw-g01-platform-services.md`
Parity estimate: **before 96% -> after 96%**

Completed work:

1. Removed the extra `subscribe request failed` diagnostic from
   `SV_SteamCmd_SubscribeUGC_f`, which retail never printed.
2. Kept the retained direct wrapper call intact around that removal.
3. Refreshed the focused regression coverage and the matching abstraction/gap
   notes for the removed subscribe-failure trace.

### Task A3de: Restore the retail post-subscribe item-state refresh [COMPLETED]
Priority: Critical
Primary areas: `src/code/server/sv_ccmds.c`,
`tests/test_platform_services.py`,
`tests/test_engine_operator_command_parity.py`
Parity estimate: **before 96% -> after 96%**

Completed work:

1. Updated `SV_SteamCmd_SubscribeUGC_f` so it now re-reads
   `QL_Steamworks_GetItemState` after the subscribe call, matching the retail
   `SteamWorkshop_SubscribeItem` wrapper behavior.
2. Kept the existing one-argument item-ID parse surface intact.
3. Refreshed the focused regression coverage for the post-subscribe state
   refresh.

### Task A3df: Restore the retail post-subscribe filesystem restart fast path [COMPLETED]
Priority: Critical
Primary areas: `src/code/server/sv_ccmds.c`,
`tests/test_platform_services.py`,
`tests/test_engine_operator_command_parity.py`,
`docs/steam_platform_abstraction.md`,
`docs/reverse-engineering/source-file-gap-notes/rw-g01-platform-services.md`
Parity estimate: **before 96% -> after 96%**

Completed work:

1. Updated `SV_SteamCmd_SubscribeUGC_f` so it now calls `FS_Restart` when the
   newly subscribed item is already installed, matching the retail installed-
   item fast path recovered from `SteamWorkshop_SubscribeItem`.
2. Kept the retained operator command surface intact around that restart hook.
3. Refreshed the focused regression coverage and the matching abstraction/gap
   notes for the post-subscribe restart path.

### Task A3dg: Restore the thin retail `steam_unsubscribeugc` command shape [COMPLETED]
Priority: Critical
Primary areas: `src/code/server/sv_ccmds.c`,
`tests/test_platform_services.py`,
`tests/test_engine_operator_command_parity.py`,
`docs/steam_platform_abstraction.md`,
`docs/reverse-engineering/source-file-gap-notes/rw-g01-platform-services.md`
Parity estimate: **before 96% -> after 96%**

Completed work:

1. Updated `SV_SteamCmd_UnsubscribeUGC_f` so it now mirrors the retail thin
   wrapper shape instead of stopping early behind the compatibility-only
   workshop-support gate.
2. Kept the existing one-argument item-ID parse surface intact.
3. Refreshed the focused regression coverage and the matching abstraction/gap
   notes for the unsubscribe command shape.

### Task A3dh: Remove the non-retail unsubscribe request/failure traces [COMPLETED]
Priority: Critical
Primary areas: `src/code/server/sv_ccmds.c`,
`tests/test_platform_services.py`,
`tests/test_engine_operator_command_parity.py`,
`docs/steam_platform_abstraction.md`,
`docs/reverse-engineering/source-file-gap-notes/rw-g01-platform-services.md`
Parity estimate: **before 96% -> after 96%**

Completed work:

1. Removed the extra `unsubscribe requested` and `unsubscribe request failed`
   diagnostics from `SV_SteamCmd_UnsubscribeUGC_f`, which retail never
   printed.
2. Kept the retained direct wrapper call intact around those removals.
3. Refreshed the focused regression coverage and the matching abstraction/gap
   notes for the removed unsubscribe traces.

### Task A3di: Restore the thin retail `steam_downloadugc` command helper ownership [COMPLETED]
Priority: Critical
Primary areas: `src/code/server/sv_ccmds.c`,
`tests/test_platform_services.py`,
`tests/test_engine_operator_command_parity.py`,
`docs/steam_platform_abstraction.md`,
`docs/reverse-engineering/source-file-gap-notes/rw-g01-platform-services.md`
Parity estimate: **before 96% -> after 96%**

Completed work:

1. Updated `SV_SteamCmd_DownloadUGC_f` so it now mirrors the retail thin
   wrapper shape by handing the parsed item ID off to
   `SV_SteamWorkshop_RequestDownload` instead of inlining the workshop
   control-flow directly in the operator command.
2. Kept the existing one-argument item-ID parse surface intact.
3. Refreshed the focused regression coverage and the matching abstraction/gap
   notes for the recovered command-helper ownership split.

### Task A3dj: Restore the local `SteamWorkshop_RequestDownload` helper ownership [COMPLETED]
Priority: Critical
Primary areas: `src/code/server/sv_ccmds.c`,
`tests/test_platform_services.py`,
`tests/test_engine_operator_command_parity.py`,
`docs/steam_platform_abstraction.md`,
`docs/reverse-engineering/source-file-gap-notes/rw-g01-platform-services.md`
Parity estimate: **before 96% -> after 96%**

Completed work:

1. Added `SV_SteamWorkshop_RequestDownload` so the compatibility-gated cache
   hit, restored retail detail strings, and `QL_Steamworks_DownloadItem`
   dispatch now sit under the same local helper boundary that the retail
   `steam_downloadugc` command calls into.
2. Kept the restored `Workshop item %llu: in cache.` and
   `Workshop item %llu: download` details intact around that helper recovery.
3. Refreshed the focused regression coverage and the matching abstraction/gap
   notes for the recovered request-download helper ownership.

### Task A3dk: Restore the thin retail `steam_subscribeugc` command helper ownership [COMPLETED]
Priority: Critical
Primary areas: `src/code/server/sv_ccmds.c`,
`tests/test_platform_services.py`,
`tests/test_engine_operator_command_parity.py`,
`docs/steam_platform_abstraction.md`,
`docs/reverse-engineering/source-file-gap-notes/rw-g01-platform-services.md`
Parity estimate: **before 96% -> after 96%**

Completed work:

1. Updated `SV_SteamCmd_SubscribeUGC_f` so it now mirrors the retail thin
   wrapper shape by handing the parsed item ID off to
   `SV_SteamWorkshop_SubscribeItem` instead of owning the workshop control
   flow directly.
2. Kept the existing one-argument item-ID parse surface intact.
3. Refreshed the focused regression coverage and the matching abstraction/gap
   notes for the recovered subscribe-helper ownership split.

### Task A3dl: Restore the thin retail `steam_unsubscribeugc` command helper ownership [COMPLETED]
Priority: Critical
Primary areas: `src/code/server/sv_ccmds.c`,
`tests/test_platform_services.py`,
`tests/test_engine_operator_command_parity.py`,
`docs/steam_platform_abstraction.md`,
`docs/reverse-engineering/source-file-gap-notes/rw-g01-platform-services.md`
Parity estimate: **before 96% -> after 96%**

Completed work:

1. Updated `SV_SteamCmd_UnsubscribeUGC_f` so it now mirrors the retail thin
   wrapper shape by handing the parsed item ID off to
   `SV_SteamWorkshop_UnsubscribeItem` instead of owning the unsubscribe call
   path directly.
2. Kept the existing one-argument item-ID parse surface intact.
3. Refreshed the focused regression coverage and the matching abstraction/gap
   notes for the recovered unsubscribe-helper ownership split.

### Task A3dm: Move the recovered post-subscribe item-state refresh under the local helper owner [COMPLETED]
Priority: Critical
Primary areas: `src/code/server/sv_ccmds.c`,
`tests/test_platform_services.py`,
`tests/test_engine_operator_command_parity.py`
Parity estimate: **before 96% -> after 96%**

Completed work:

1. Updated `SV_SteamWorkshop_SubscribeItem` so the recovered
   `QL_Steamworks_GetItemState` re-read now sits under the same local helper
   owner that the thin `steam_subscribeugc` command calls into.
2. Kept the direct `QL_Steamworks_SubscribeItem` wrapper call intact around
   that ownership correction.
3. Refreshed the focused regression coverage for the helper-owned
   post-subscribe state refresh.

### Task A3dn: Move the recovered post-subscribe filesystem restart under the local helper owner [COMPLETED]
Priority: Critical
Primary areas: `src/code/server/sv_ccmds.c`,
`tests/test_platform_services.py`,
`tests/test_engine_operator_command_parity.py`,
`docs/steam_platform_abstraction.md`,
`docs/reverse-engineering/source-file-gap-notes/rw-g01-platform-services.md`
Parity estimate: **before 96% -> after 96%**

Completed work:

1. Updated `SV_SteamWorkshop_SubscribeItem` so the recovered installed-item
   `FS_Restart` fast path now sits under the same local helper owner that the
   thin `steam_subscribeugc` command calls into.
2. Kept the retained operator command surface intact around that helper-owned
   restart path.
3. Refreshed the focused regression coverage and the matching abstraction/gap
   notes for the helper-owned post-subscribe restart path.

### Task A3do: Restore the retail platform subscribe-wrapper item-state refresh [COMPLETED]
Priority: Critical
Primary areas: `src/common/platform/platform_steamworks.c`,
`tests/test_platform_services.py`,
`docs/steam_platform_abstraction.md`,
`docs/reverse-engineering/source-file-gap-notes/rw-g01-platform-services.md`
Parity estimate: **before 96% -> after 96%**

Completed work:

1. Updated `QL_Steamworks_SubscribeItem` so it now re-reads
   `QL_Steamworks_GetItemState` after the raw subscribe vtable call, matching
   the retail `SteamWorkshop_SubscribeItem` helper shape.
2. Kept the recovered `0xc0 / 4` subscribe slot ownership intact around that
   state refresh.
3. Refreshed the focused regression coverage and the matching abstraction/gap
   notes for the platform subscribe-wrapper state refresh.

### Task A3dp: Remove the unconditional platform subscribe success return [COMPLETED]
Priority: Critical
Primary areas: `src/common/platform/platform_steamworks.c`,
`tests/test_platform_services.py`,
`tests/test_steamworks_harness.py`,
`docs/steam_platform_abstraction.md`,
`docs/reverse-engineering/source-file-gap-notes/rw-g01-platform-services.md`
Parity estimate: **before 96% -> after 96%**

Completed work:

1. Replaced the unconditional `return qtrue;` tail in
   `QL_Steamworks_SubscribeItem` with the recovered `itemState != 0u` result,
   matching the retail helper's post-subscribe return contract.
2. Kept the wrapper ABI and surrounding UGC interface ownership unchanged.
3. Refreshed the focused regression coverage and the matching abstraction/gap
   notes for the removed unconditional subscribe success return.

### Task A3dq: Add harness coverage for the zero-state subscribe result [COMPLETED]
Priority: Critical
Primary areas: `tests/test_steamworks_harness.py`,
`tests/steamworks_harness.c`
Parity estimate: **before 96% -> after 96%**

Completed work:

1. Extended the Steamworks harness so the enabled workshop helper test now
   asserts that `QLR_Steamworks_SubscribeItem` returns false when the post-
   subscribe item state remains zero.
2. Kept the existing disabled-lane and installed-item success expectations
   intact around that new regression.
3. Refreshed the harness support stubs so `platform_steamworks.c` continues to
   compile directly under the test fixture after the newer platform-services
   diagnostics were added.

### Task A3dr: Add harness coverage for dedicated-server installed-state subscribe success [COMPLETED]
Priority: Critical
Primary areas: `tests/test_steamworks_harness.py`
Parity estimate: **before 96% -> after 96%**

Completed work:

1. Updated the dedicated-server UGC ownership harness so it now primes the
   installed-item state before asserting subscribe success, matching the
   restored retail post-subscribe return contract.
2. Kept the existing dedicated-server UGC call-count and item-ID assertions
   intact.
3. Refreshed the focused harness coverage for the server-owned workshop lane.

### Task A3ds: Restore the client bootstrap helper name to the retail request owner [COMPLETED]
Priority: Critical
Primary areas: `src/code/client/cl_main.c`,
`tests/test_platform_services.py`
Parity estimate: **before 96% -> after 96%**

Completed work:

1. Renamed the retained client bootstrap helper to
   `CL_Workshop_RequestDownload` so the source-side owner now mirrors the
   retail `SteamWorkshop_RequestDownload` helper boundary again.
2. Dropped the synthetic queued-branch parameter from that helper.
3. Refreshed the focused regression coverage for the recovered helper owner.

### Task A3dt: Remove the non-retail queued-handoff branch from the request helper [COMPLETED]
Priority: Critical
Primary areas: `src/code/client/cl_main.c`,
`tests/test_platform_services.py`
Parity estimate: **before 96% -> after 96%**

Completed work:

1. Removed the queued-handoff branch from `CL_Workshop_RequestDownload` so it
   now owns only the initial `Workshop item %llu: requesting download.`
   detail recovered from retail `SteamWorkshop_RequestDownload`.
2. Kept the retained request-state updates intact around that narrower helper
   contract.
3. Refreshed the focused regression coverage for the removed queued branch.

### Task A3du: Restore the retail queued-handoff detail under `SteamWorkshop_AdvanceDownloadQueue` [COMPLETED]
Priority: Critical
Primary areas: `src/code/client/cl_main.c`,
`tests/test_platform_services.py`
Parity estimate: **before 96% -> after 96%**

Completed work:

1. Moved the retail `Workshop item %llu: was queued, requesting download.`
   detail under `CL_Workshop_AdvanceQueue`, matching the recovered
   `SteamWorkshop_AdvanceDownloadQueue` string owner.
2. Removed that detail from the initial-request helper owner.
3. Refreshed the focused regression coverage for the recovered queued-handoff
   detail owner.

### Task A3dv: Restore the queued download dispatch under the queue-pop helper [COMPLETED]
Priority: Critical
Primary areas: `src/code/client/cl_main.c`,
`tests/test_platform_services.py`
Parity estimate: **before 96% -> after 96%**

Completed work:

1. Moved the queued `QL_Steamworks_DownloadItem` dispatch under
   `CL_Workshop_AdvanceQueue`, matching the recovered retail queue-pop helper
   flow instead of reusing the initial-request helper.
2. Kept the retained queue-state bookkeeping intact around that owner shift.
3. Refreshed the focused regression coverage for the recovered dispatch owner.

### Task A3dw: Restore the queued active-item handoff under the queue-pop helper [COMPLETED]
Priority: Critical
Primary areas: `src/code/client/cl_main.c`,
`tests/test_platform_services.py`
Parity estimate: **before 96% -> after 96%**

Completed work:

1. Moved the queued `CL_Workshop_SetActiveItem` handoff under
   `CL_Workshop_AdvanceQueue`, matching the retail helper that promotes the
   next queued item before issuing its download request.
2. Kept the retained progress-cvar updates intact around that recovered owner
   split.
3. Refreshed the focused regression coverage for the queued active-item
   handoff owner.

### Task A3dx: Restore the queue-advance owner split under `SteamWorkshop_FinalizeItem` [COMPLETED]
Priority: Critical
Primary areas: `src/code/client/cl_main.c`,
`tests/test_platform_services.py`
Parity estimate: **before 96% -> after 96%**

Completed work:

1. Updated `CL_Workshop_FinalizeInstalledItem` so it now returns the
   `CL_Workshop_AdvanceQueue` result when the active item completes, matching
   the recovered retail `SteamWorkshop_FinalizeItem` helper flow.
2. Kept the retained completion log and active-download clear intact around
   that owner split.
3. Refreshed the focused regression coverage for the finalize-owned queue
   advance.

### Task A3dy: Remove the explicit queued-handoff from the item-installed callback owner [COMPLETED]
Priority: Critical
Primary areas: `src/code/client/cl_main.c`,
`tests/test_platform_services.py`
Parity estimate: **before 96% -> after 96%**

Completed work:

1. Removed the extra `CL_Workshop_AdvanceQueue` call from
   `CL_Steam_Workshop_OnItemInstalled` so the callback now leaves queued
   handoff ownership with `CL_Workshop_FinalizeInstalledItem`, matching
   retail.
2. Kept the retained null/app-id/tracked-item guard surface intact.
3. Refreshed the focused regression coverage for the callback-owner cleanup.

### Task A3dz: Remove the explicit queued-handoff from the download-result success owner [COMPLETED]
Priority: Critical
Primary areas: `src/code/client/cl_main.c`,
`tests/test_platform_services.py`
Parity estimate: **before 96% -> after 96%**

Completed work:

1. Removed the extra `CL_Workshop_AdvanceQueue` call from the successful
   `CL_Steam_Workshop_OnDownloadItemResult` lane so the completion path now
   mirrors the retail finalize-helper ownership split.
2. Kept the recovered invalid-app, active-download, and failure-result details
   intact.
3. Refreshed the focused regression coverage for the success-owner cleanup.

### Task A3ea: Route bootstrap cache hits through the finalize helper owner [COMPLETED]
Priority: Critical
Primary areas: `src/code/client/cl_main.c`,
`tests/test_platform_services.py`
Parity estimate: **before 96% -> after 96%**

Completed work:

1. Updated the bootstrap cache-hit path so it now calls
   `CL_Workshop_FinalizeInstalledItem` after the retail `Workshop item %llu:
   in cache.` detail instead of marking the item complete inline.
2. Kept the retained cache-hit logging intact around that recovered owner
   split.
3. Refreshed the focused regression coverage for the finalize-owned cache-hit
   path.

### Task A3eb: Update the bootstrap caller to use the recovered request helper split [COMPLETED]
Priority: Critical
Primary areas: `src/code/client/cl_main.c`,
`tests/test_platform_services.py`,
`docs/steam_platform_abstraction.md`,
`docs/reverse-engineering/source-file-gap-notes/rw-g01-platform-services.md`
Parity estimate: **before 96% -> after 96%**

Completed work:

1. Updated the client workshop bootstrap caller so the first request now goes
   through `CL_Workshop_RequestDownload`, while queued handoffs and completion
   handoffs stay with the recovered queue/finalize owners.
2. Refreshed the focused regression coverage plus the matching abstraction and
   gap-note documentation for the recovered helper ownership split.
3. Kept the bounded compatibility-only workshop provider/policy diagnostics
   intact around that tighter retail flow.

### Task A3ec: Add explicit retained state for queued workshop items [COMPLETED]
Priority: Critical
Primary areas: `src/code/client/cl_main.c`,
`tests/test_platform_services.py`
Parity estimate: **before 96% -> after 96%**

Completed work:

1. Added an explicit `queued` flag to the retained client workshop item state
   so the source can distinguish queued-for-later items from items that have
   already issued `DownloadItem`, matching the retail queue-container
   separation more closely.
2. Kept the retained `requestNumber`, `downloadRequested`, and `completed`
   fields intact around that narrower queue-state split.
3. Refreshed the focused regression coverage for the new queued-item state.

### Task A3ed: Restore bootstrap queueing ownership under `SteamWorkshop_RequestDownload` [COMPLETED]
Priority: Critical
Primary areas: `src/code/client/cl_main.c`,
`tests/test_platform_services.py`
Parity estimate: **before 96% -> after 96%**

Completed work:

1. Updated `CL_Workshop_RequestDownload` so it now owns the retail
   `Workshop item %llu: queueing download.` branch when a bootstrap download
   is already active, instead of leaving that detail under the caller.
2. Kept the recovered initial `requesting download` branch intact in the same
   helper.
3. Refreshed the focused regression coverage for the restored queueing-detail
   owner.

### Task A3ee: Route every uncached bootstrap item through the recovered request helper [COMPLETED]
Priority: Critical
Primary areas: `src/code/client/cl_main.c`,
`tests/test_platform_services.py`
Parity estimate: **before 96% -> after 96%**

Completed work:

1. Updated the bootstrap loop so every uncached item now flows through
   `CL_Workshop_RequestDownload`, matching the retail `CL_InitDownloads`
   caller shape instead of splitting the queueing branch out in the caller.
2. Kept the retained cache-hit finalize path intact around that caller
   tightening.
3. Refreshed the focused regression coverage for the unified request-helper
   routing.

### Task A3ef: Mark queued bootstrap items explicitly when the request helper defers them [COMPLETED]
Priority: Critical
Primary areas: `src/code/client/cl_main.c`,
`tests/test_platform_services.py`
Parity estimate: **before 96% -> after 96%**

Completed work:

1. Updated `CL_Workshop_RequestDownload` so it now marks later bootstrap items
   as explicitly queued when the active download already exists, matching the
   recovered retail helper's queue-container behavior more closely.
2. Kept the retained active-download issue path intact for the first item.
3. Refreshed the focused regression coverage for the explicit queued-item
   mark.

### Task A3eg: Make the queue-pop helper consume explicit queued items only [COMPLETED]
Priority: Critical
Primary areas: `src/code/client/cl_main.c`,
`tests/test_platform_services.py`
Parity estimate: **before 96% -> after 96%**

Completed work:

1. Updated `CL_Workshop_AdvanceQueue` so it now consumes only items marked as
   queued, instead of inferring queue membership from
   `!completed && !downloadRequested`.
2. Kept the recovered queued-handoff detail and `DownloadItem` dispatch intact
   around that narrower scan.
3. Refreshed the focused regression coverage for the explicit queued scan.

### Task A3eh: Clear the retained queued flag when a queued item becomes active [COMPLETED]
Priority: Critical
Primary areas: `src/code/client/cl_main.c`,
`tests/test_platform_services.py`
Parity estimate: **before 96% -> after 96%**

Completed work:

1. Updated `CL_Workshop_AdvanceQueue` so it now clears the retained queued
   flag before issuing the queued item's `DownloadItem` request, matching the
   queue-pop ownership more closely.
2. Kept the retained `downloadRequested` tracking intact around that state
   handoff.
3. Refreshed the focused regression coverage for the queued-flag clear path.

### Task A3ei: Restore bootstrap caller ownership of `cl_downloadItem` seeding [COMPLETED]
Priority: Critical
Primary areas: `src/code/client/cl_main.c`,
`tests/test_platform_services.py`
Parity estimate: **before 96% -> after 96%**

Completed work:

1. Added `CL_Workshop_SetDownloadRequestCvars` and moved the
   `cl_downloadItem` seed under the bootstrap caller after successful request-
   helper returns, matching the retail `CL_InitDownloads` ownership split.
2. Kept the retained decimal SteamID formatting intact around that move.
3. Refreshed the focused regression coverage for the caller-owned item cvar.

### Task A3ej: Restore bootstrap caller ownership of `cl_downloadName` seeding [COMPLETED]
Priority: Critical
Primary areas: `src/code/client/cl_main.c`,
`tests/test_platform_services.py`
Parity estimate: **before 96% -> after 96%**

Completed work:

1. Moved the `cl_downloadName` seed under
   `CL_Workshop_SetDownloadRequestCvars` so the bootstrap caller now owns the
   `Workshop item %i of %i` request-label cvar after successful helper
   returns, matching retail.
2. Kept the retained `requestNumber`/`totalItems` labeling intact around that
   ownership split.
3. Refreshed the focused regression coverage for the caller-owned name cvar.

### Task A3ek: Restore bootstrap caller ownership of `cl_downloadTime` seeding [COMPLETED]
Priority: Critical
Primary areas: `src/code/client/cl_main.c`,
`tests/test_platform_services.py`
Parity estimate: **before 96% -> after 96%**

Completed work:

1. Moved the `cl_downloadTime` seed under
   `CL_Workshop_SetDownloadRequestCvars` so the bootstrap caller now owns the
   request timestamp after successful helper returns, matching the retail
   `CL_InitDownloads` call site.
2. Kept the retained `cls.realtime` source intact around that move.
3. Refreshed the focused regression coverage for the caller-owned time cvar.

### Task A3el: Remove item/name/time cvar mutation from the active-item helper [COMPLETED]
Priority: Critical
Primary areas: `src/code/client/cl_main.c`,
`tests/test_platform_services.py`,
`docs/steam_platform_abstraction.md`,
`docs/reverse-engineering/source-file-gap-notes/rw-g01-platform-services.md`
Parity estimate: **before 96% -> after 96%**

Completed work:

1. Removed the `cl_downloadItem`, `cl_downloadName`, and `cl_downloadTime`
   mutations from `CL_Workshop_SetActiveItem`, leaving that helper focused on
   active-download state and progress-byte refresh rather than bootstrap-cvar
   ownership.
2. Kept the then-retained UI-facing `cl_downloadCount` / `cl_downloadSize`
   temp-cvar updates intact around that narrower helper contract.
3. Refreshed the focused regression coverage plus the matching abstraction and
   gap-note documentation for the recovered active-item helper split.

### Task A3em: Restore installed-item handling under the client request helper [COMPLETED]
Priority: Critical
Primary areas: `src/code/client/cl_main.c`,
`tests/test_platform_services.py`
Parity estimate: **before 96% -> after 96%**

Completed work:

1. Updated `CL_Workshop_RequestDownload` so it now owns the installed-item
   gate, matching the retail `SteamWorkshop_RequestDownload` helper shape
   instead of relying on a bootstrap-caller pre-check.
2. Kept the retained queued and active-download branches intact around that
   helper-owned cache-hit path.
3. Refreshed the focused regression coverage for the recovered installed-item
   owner split.

### Task A3en: Remove the bootstrap caller installed-state pre-check [COMPLETED]
Priority: Critical
Primary areas: `src/code/client/cl_main.c`,
`tests/test_platform_services.py`
Parity estimate: **before 96% -> after 96%**

Completed work:

1. Removed the installed-state short-circuit from
   `CL_Workshop_BeginBootstrap` so parsed workshop items now flow through the
   recovered request helper regardless of whether they are already installed.
2. Kept the retained parsed-item count, truncation guard, and SteamID parse
   surface intact.
3. Refreshed the focused regression coverage for the removed caller pre-check.

### Task A3eo: Restore the retail `in cache` detail under `SteamWorkshop_RequestDownload` [COMPLETED]
Priority: Critical
Primary areas: `src/code/client/cl_main.c`,
`tests/test_platform_services.py`
Parity estimate: **before 96% -> after 96%**

Completed work:

1. Moved the retail `Workshop item %llu: in cache.` detail under
   `CL_Workshop_RequestDownload`, matching the recovered helper that owns that
   string in retail.
2. Removed that detail from the bootstrap caller owner.
3. Refreshed the focused regression coverage for the recovered cache-hit
   string owner.

### Task A3ep: Restore finalize ownership for request-helper cache hits [COMPLETED]
Priority: Critical
Primary areas: `src/code/client/cl_main.c`,
`tests/test_platform_services.py`
Parity estimate: **before 96% -> after 96%**

Completed work:

1. Updated the request helper so installed-item cache hits now call
   `CL_Workshop_FinalizeInstalledItem`, matching the retail helper/finalize
   handoff.
2. Removed that finalize call from the bootstrap caller cache-hit branch.
3. Refreshed the focused regression coverage for the recovered finalize owner.

### Task A3eq: Restore queue-gate activation for helper-owned cache hits [COMPLETED]
Priority: Critical
Primary areas: `src/code/client/cl_main.c`,
`tests/test_platform_services.py`
Parity estimate: **before 96% -> after 96%**

Completed work:

1. Kept `CL_Workshop_RequestDownload` setting the retained queue gate active
   before the installed-item branch, matching the retail helper that marks the
   queue lane active even when a bootstrap item is already in cache.
2. Left the later queue-complete owner unchanged around that recovered gate
   activation.
3. Refreshed the focused regression coverage for the helper-owned queue gate.

### Task A3er: Keep bootstrap request numbering limited to helper-success returns [COMPLETED]
Priority: Critical
Primary areas: `src/code/client/cl_main.c`,
`tests/test_platform_services.py`
Parity estimate: **before 96% -> after 96%**

Completed work:

1. Kept `item->requestNumber` assignment under the bootstrap caller's
   successful `CL_Workshop_RequestDownload` return path, matching the retail
   `CL_InitDownloads` caller shape after the installed-item path moved under
   the helper.
2. Prevented cache-hit items from receiving bootstrap request ordinals.
3. Refreshed the focused regression coverage for the request-number owner.

### Task A3es: Route every parsed bootstrap item through the recovered request helper [COMPLETED]
Priority: Critical
Primary areas: `src/code/client/cl_main.c`,
`tests/test_platform_services.py`
Parity estimate: **before 96% -> after 96%**

Completed work:

1. Tightened `CL_Workshop_BeginBootstrap` so every parsed workshop item now
   flows through `CL_Workshop_RequestDownload`, matching the retail caller
   that invokes `SteamWorkshop_RequestDownload` for each token.
2. Kept the retained truncation and parse guards intact around that caller
   recovery.
3. Refreshed the focused regression coverage for the per-token request-helper
   routing.

### Task A3et: Restore queue-complete eligibility for all-cached bootstrap passes [COMPLETED]
Priority: Critical
Primary areas: `src/code/client/cl_main.c`,
`tests/test_platform_services.py`
Parity estimate: **before 96% -> after 96%**

Completed work:

1. By moving cache-hit handling under `CL_Workshop_RequestDownload`, the
   retained bootstrap lane now marks the queue gate active even when every
   required item is already installed, matching the retail path that still
   runs the later queue-complete helper.
2. Kept the retained no-download request-number and cvar behavior intact for
   those cache-hit items.
3. Refreshed the focused regression coverage for the all-cached queue-complete
   eligibility lane.

### Task A3eu: Update the focused workshop bootstrap regression for helper-owned cache hits [COMPLETED]
Priority: Critical
Primary areas: `tests/test_platform_services.py`
Parity estimate: **before 96% -> after 96%**

Completed work:

1. Updated the focused client workshop regression so it now asserts the
   installed-item `in cache` detail and finalize handoff under
   `CL_Workshop_RequestDownload` instead of under the bootstrap caller.
2. Added a direct assertion that the helper keeps the retained queue gate
   active around that installed-item branch.
3. Kept the existing queued and active-download assertions intact.

### Task A3ev: Refresh the abstraction notes for the helper-owned cache-hit split [COMPLETED]
Priority: Critical
Primary areas: `docs/steam_platform_abstraction.md`,
`docs/reverse-engineering/source-file-gap-notes/rw-g01-platform-services.md`,
`IMPLEMENTATION_PLAN.md`
Parity estimate: **before 96% -> after 96%**

Completed work:

1. Refreshed the abstraction notes so they now document the recovered
   `SteamWorkshop_RequestDownload` cache-hit ownership split and the retained
   all-cached queue-gate behavior.
2. Recorded the next ten micro-closures in the implementation ledger as
   `A3em` through `A3ev`.
3. Kept the compatibility-boundary framing explicit around those retail-backed
   helper corrections.

### Task A3ew: Restore the plain retail workshop bootstrap announcement string [COMPLETED]
Priority: Critical
Primary areas: `src/code/client/cl_main.c`,
`tests/test_platform_services.py`
Parity estimate: **before 96% -> after 96%**

Completed work:

1. Updated `CL_Workshop_BeginBootstrap` so it now prints the recovered retail
   `Server requires the following workshop items: %s` announcement instead of
   the newer provider/policy-flavored compatibility detail.
2. Kept the retained bootstrap-unavailable compatibility log intact around
   that exact-string recovery.
3. Refreshed the focused regression coverage for the restored announcement
   string.

### Task A3ex: Remove the non-retail bootstrap provider/policy announcement locals [COMPLETED]
Priority: Critical
Primary areas: `src/code/client/cl_main.c`,
`tests/test_platform_services.py`
Parity estimate: **before 96% -> after 96%**

Completed work:

1. Removed the bootstrap-only `workshopProvider` / `workshopPolicy` locals
   from `CL_Workshop_BeginBootstrap` after restoring the plain retail
   announcement string.
2. Kept the later provider/policy-aware fallback diagnostics intact elsewhere
   in the workshop lane.
3. Refreshed the focused regression coverage for the removed announcement
   locals.

### Task A3ey: Update the bootstrap regression for the restored retail announcement [COMPLETED]
Priority: Critical
Primary areas: `tests/test_platform_services.py`
Parity estimate: **before 96% -> after 96%**

Completed work:

1. Updated the focused client workshop bootstrap regression so it now asserts
   the plain retail announcement string and the absence of the removed
   provider/policy announcement locals.
2. Kept the existing request-helper and queue-owner assertions intact.
3. Reconfirmed the bootstrap regression against the current worktree.

### Task A3ez: Restore the retail frame restart-required string [COMPLETED]
Priority: Critical
Primary areas: `src/code/client/cl_main.c`,
`tests/test_platform_services.py`
Parity estimate: **before 96% -> after 96%**

Completed work:

1. Updated `CL_Workshop_Frame` so the restart-required path now prints the
   recovered retail `Steamworks downloads complete - FS restart is required`
   detail.
2. Kept the retained `FS_Restart( clc.checksumFeed )` behavior and
   `downloadsRequested` reset intact around that exact-string recovery.
3. Refreshed the focused regression coverage for the restored restart-required
   string.

### Task A3fa: Remove the compatibility-only frame restart lifecycle trace [COMPLETED]
Priority: Critical
Primary areas: `src/code/client/cl_main.c`,
`tests/test_platform_services.py`
Parity estimate: **before 96% -> after 96%**

Completed work:

1. Removed the compatibility-only `downloads complete; restarting filesystem`
   workshop lifecycle trace from the frame restart path, which retail never
   printed.
2. Replaced it with the recovered plain restart-required print under the same
   owner.
3. Refreshed the focused regression coverage for the removed compatibility
   trace.

### Task A3fb: Restore the retail frame completion string before pk3 validation [COMPLETED]
Priority: Critical
Primary areas: `src/code/client/cl_main.c`,
`tests/test_platform_services.py`
Parity estimate: **before 96% -> after 96%**

Completed work:

1. Added the recovered `Steamworks downloads complete` print to the no-restart
   branch of `CL_Workshop_Frame`, matching the retail completion helper before
   it performs the missing-pk3 compare.
2. Kept the retained state-clear and `CL_DownloadsComplete` handoff ordering
   unchanged around that exact-string recovery.
3. Refreshed the focused regression coverage for the restored completion
   string.

### Task A3fc: Restore the retail missing-pk3 warning header under the frame helper [COMPLETED]
Priority: Critical
Primary areas: `src/code/client/cl_main.c`,
`tests/test_platform_services.py`
Parity estimate: **before 96% -> after 96%**

Completed work:

1. Replaced the non-retail `WARNING: You are missing some files referenced by
   the server:` wording in `CL_Workshop_Frame` with the recovered retail
   `WARNING: Missing pk3s referenced by the server:` header.
2. Kept the retained `FS_ComparePaks( ..., qfalse )` gate intact around that
   warning path.
3. Refreshed the focused regression coverage for the restored warning header.

### Task A3fd: Restore the retail missing-pk3 consequence line [COMPLETED]
Priority: Critical
Primary areas: `src/code/client/cl_main.c`,
`tests/test_platform_services.py`
Parity estimate: **before 96% -> after 96%**

Completed work:

1. Replaced the newer `You might not be able to join the game` /
   `Go to the setting menu...` warning tail in `CL_Workshop_Frame` with the
   recovered retail `The server will most likely refuse the connection.` line.
2. Kept the retained missing-file payload insertion intact around that exact
   warning tail.
3. Refreshed the focused regression coverage for the restored consequence
   line.

### Task A3fe: Add focused regression coverage for the retail frame strings [COMPLETED]
Priority: Critical
Primary areas: `tests/test_platform_services.py`
Parity estimate: **before 96% -> after 96%**

Completed work:

1. Added a dedicated `CL_Workshop_Frame` regression so the restart-required,
   downloads-complete, and missing-pk3 warning strings now stay pinned to the
   recovered retail literals.
2. Included negative assertions for the removed compatibility-only restart and
   missing-file wording.
3. Kept the retained `FS_Restart`, state-clear, and `CL_DownloadsComplete`
   owner assertions intact.

### Task A3ff: Refresh the abstraction notes for the restored bootstrap/frame string surface [COMPLETED]
Priority: Critical
Primary areas: `docs/steam_platform_abstraction.md`,
`docs/reverse-engineering/source-file-gap-notes/rw-g01-platform-services.md`,
`IMPLEMENTATION_PLAN.md`
Parity estimate: **before 96% -> after 96%**

Completed work:

1. Refreshed the abstraction notes so they now document the restored plain
   workshop bootstrap announcement plus the recovered retail frame restart,
   completion, and missing-pk3 warning strings.
2. Recorded the next ten micro-closures in the implementation ledger as
   `A3ew` through `A3ff`.
3. Kept the compatibility-boundary framing explicit around those retail-backed
   exact-string corrections.

### Task A3fg: Restore the retained no-restart workshop completion lane to the retail active-gate teardown [COMPLETED]
Priority: Critical
Primary areas: `src/code/client/cl_main.c`, `tests/test_platform_services.py`
Parity estimate: **before 96% -> after 96%**

Completed work:

1. Rechecked the retail `CL_Workshop_Frame` HLIL helper and confirmed that the
   no-restart lane clears only the outer workshop-active gate before tailing
   into `CL_DownloadsComplete()`.
2. Updated the retained frame helper to drop only
   `cl_steamWorkshopDownloadState.active` on the no-restart completion path
   instead of zeroing the full bootstrap state.
3. Refreshed the focused frame regression so it now pins that exact handoff.

### Task A3fh: Remove the compatibility-only bootstrap-state reset from the retained workshop completion frame owner [COMPLETED]
Priority: Critical
Primary areas: `src/code/client/cl_main.c`, `tests/test_platform_services.py`
Parity estimate: **before 96% -> after 96%**

Completed work:

1. Removed the retained `CL_Workshop_ClearBootstrapState( qtrue )` call from
   the workshop no-restart completion lane because the retail helper does not
   clear the full bootstrap structure there.
2. Kept the recovered retail completion/warning strings and the
   `CL_DownloadsComplete()` handoff intact.
3. Added the matching negative assertion to the focused regression.

### Task A3fi: Refresh the workshop frame regression for the retail active-gate handoff [COMPLETED]
Priority: Critical
Primary areas: `tests/test_platform_services.py`, `IMPLEMENTATION_PLAN.md`
Parity estimate: **before 96% -> after 96%**

Completed work:

1. Updated the focused frame test to assert the retained active-gate clear
   instead of the older bootstrap-state reset.
2. Kept the surrounding retail restart-required, downloads-complete, and
   missing-pk3 string checks intact.
3. Recorded the handoff correction in the implementation ledger.

### Task A3fj: Bound retained workshop progress ownership to the recovered UI bridge [COMPLETED]
Priority: Critical
Primary areas: `src/code/client/cl_main.c`, `tests/test_platform_services.py`
Parity estimate: **before 96% -> after 96%**

Completed work:

1. Cross-checked the recovered `uix86` workshop-progress path and confirmed
   that it reads `cl_downloadItem`, calls the native `GetItemDownloadInfo`
   import, and reads `cl_downloadTime` rather than consuming
   `cl_downloadCount` / `cl_downloadSize`.
2. Used that evidence to trim the retained workshop helper ownership back to
   the native-item download-info bridge instead of generic download cvars.
3. Added focused evidence coverage for that UI bridge sequence.

### Task A3fk: Remove the compatibility-only generic progress-cvar write from the retained workshop active-item helper [COMPLETED]
Priority: Critical
Primary areas: `src/code/client/cl_main.c`, `tests/test_platform_services.py`
Parity estimate: **before 96% -> after 96%**

Completed work:

1. Removed the retained `CL_Workshop_UpdateProgressCvars()` call from
   `CL_Workshop_SetActiveItem`.
2. Kept the active-item byte reset and immediate native
   `CL_Workshop_RefreshProgress()` query intact.
3. Refreshed the focused helper regression to pin the trimmed cvar surface.

### Task A3fl: Remove the compatibility-only generic progress-cvar write from the retained workshop clear-active helper [COMPLETED]
Priority: Critical
Primary areas: `src/code/client/cl_main.c`, `tests/test_platform_services.py`
Parity estimate: **before 96% -> after 96%**

Completed work:

1. Removed the retained `CL_Workshop_UpdateProgressCvars()` call from
   `CL_Workshop_ClearActiveDownload`.
2. Kept the retained active-item and byte-count clear itself intact.
3. Added the matching negative regression assertion for the helper body.

### Task A3fm: Refresh the retained workshop helper regression for the trimmed progress-cvar surface [COMPLETED]
Priority: Critical
Primary areas: `tests/test_platform_services.py`, `IMPLEMENTATION_PLAN.md`
Parity estimate: **before 96% -> after 96%**

Completed work:

1. Extended the workshop helper test to extract
   `CL_Workshop_ClearActiveDownload`.
2. Added explicit negative assertions covering both the active-item helper and
   the clear-active helper so future edits do not reintroduce generic
   progress-cvar churn on workshop queue handoffs.
3. Recorded that focused regression tightening in the plan ledger.

### Task A3fn: Pin the recovered `uix86` workshop progress bridge evidence [COMPLETED]
Priority: Critical
Primary areas: `tests/test_platform_services.py`,
`references/reverse-engineering/ghidra/uix86/source-recreation/ui_reconstruction.c`
Parity estimate: **before 96% -> after 96%**

Completed work:

1. Added a focused evidence test covering the recovered workshop progress
   bridge in `ui_reconstruction.c`.
2. Pinned the `cl_downloadItem` read, native `GetItemDownloadInfo` import
   call, and `cl_downloadTime` read as the companion evidence backing the
   retained client-side ownership trim.
3. Included negative assertions showing that same recovered bridge does not
   use `cl_downloadCount` or `cl_downloadSize`.

### Task A3fo: Refresh the abstraction notes for the workshop completion and progress-bridge ownership correction [COMPLETED]
Priority: Critical
Primary areas: `docs/steam_platform_abstraction.md`
Parity estimate: **before 96% -> after 96%**

Completed work:

1. Updated the abstraction note so it now documents the retail no-restart
   frame handoff as an active-gate clear rather than a full bootstrap-state
   reset.
2. Recorded the recovered `uix86` workshop progress bridge evidence and the
   resulting removal of retained generic progress-cvar churn from the workshop
   active-item and clear-active helpers.
3. Kept the broader online-service compatibility-boundary framing explicit.

### Task A3fp: Refresh the source-gap notes and ledger for the workshop completion/progress ownership correction [COMPLETED]
Priority: Critical
Primary areas: `docs/reverse-engineering/source-file-gap-notes/rw-g01-platform-services.md`,
`IMPLEMENTATION_PLAN.md`
Parity estimate: **before 96% -> after 96%**

Completed work:

1. Updated the `RW-G01` source-gap note to match the restored workshop frame
   teardown and progress-bridge ownership story.
2. Recorded the next ten micro-closures in the implementation ledger as
   `A3fg` through `A3fp`.
3. Kept the evidence wording explicit so the batch is framed as retail-backed
   ownership correction rather than freehand compatibility instrumentation.

### Task A3fq: Restore the retained workshop queue-pop helper name to the recovered retail owner [COMPLETED]
Priority: Critical
Primary areas: `src/code/client/cl_main.c`, `tests/test_platform_services.py`
Parity estimate: **before 96% -> after 96%**

Completed work:

1. Rechecked the retail alias/evidence for `sub_469400` and renamed the
   retained queue-pop helper to `CL_Workshop_AdvanceDownloadQueue` so it
   matches the recovered `SteamWorkshop_AdvanceDownloadQueue` owner.
2. Updated the focused workshop regression to extract/assert that renamed
   helper directly.
3. Kept the broader workshop bootstrap ownership split intact around the
   recovered helper family.

### Task A3fr: Move the retained active-download clear under the shared queue-pop owner [COMPLETED]
Priority: Critical
Primary areas: `src/code/client/cl_main.c`, `tests/test_platform_services.py`
Parity estimate: **before 96% -> after 96%**

Completed work:

1. Rechecked the retail `SteamWorkshop_AdvanceDownloadQueue` HLIL and
   restored the retained active-download clear under the shared queue-pop
   helper before it scans for queued items.
2. Removed the need for completion/failure callers to open-code that clear.
3. Added focused regression coverage pinning the retained
   `CL_Workshop_ClearActiveDownload()` call inside the queue-pop owner.

### Task A3fs: Route the retained finalize helper through the shared queue-pop owner [COMPLETED]
Priority: Critical
Primary areas: `src/code/client/cl_main.c`, `tests/test_platform_services.py`
Parity estimate: **before 96% -> after 96%**

Completed work:

1. Updated `CL_Workshop_FinalizeInstalledItem` so the active-item completion
   lane now tails directly into `CL_Workshop_AdvanceDownloadQueue()`.
2. Removed the explicit active-download clear from the finalize helper body
   because that teardown now belongs to the shared queue-pop owner.
3. Refreshed the focused helper regression so it now asserts the shared
   completion handoff instead of the old inline clear.

### Task A3ft: Route the retained active-download failure helper through the shared queue-pop owner [COMPLETED]
Priority: Critical
Primary areas: `src/code/client/cl_main.c`, `tests/test_platform_services.py`
Parity estimate: **before 96% -> after 96%**

Completed work:

1. Updated `CL_Workshop_FailActiveDownload` so it now marks the active item
   completed and then tails into `CL_Workshop_AdvanceDownloadQueue()`.
2. Kept the helper bounded to retained state management only; the retail
   failure detail still stays in the callback owner.
3. Added the matching regression assertion for the shared failure handoff.

### Task A3fu: Remove the ignored retained `EResult` parameter from the workshop failure helper [COMPLETED]
Priority: Critical
Primary areas: `src/code/client/cl_main.c`, `tests/test_platform_services.py`
Parity estimate: **before 96% -> after 96%**

Completed work:

1. Dropped the unused `result` parameter from `CL_Workshop_FailActiveDownload`
   because the retained helper never consumed it and the retail shared
   queue-pop handoff does not take that result code.
2. Kept the actual failure-detail formatting anchored to the
   `DownloadItemResult` callback owner where the retail string lives.
3. Updated the focused callback/helper regression to match the trimmed helper
   signature.

### Task A3fv: Remove the callback-inline queue advance from the retained workshop download-result owner [COMPLETED]
Priority: Critical
Primary areas: `src/code/client/cl_main.c`, `tests/test_platform_services.py`
Parity estimate: **before 96% -> after 96%**

Completed work:

1. Removed the retained `CL_Workshop_AdvanceDownloadQueue()` call from the
   `CL_Steam_Workshop_OnDownloadItemResult` failure lane.
2. Kept the retail failure detail log intact and let the failure helper own
   the shared queue-pop handoff instead.
3. Added a focused negative assertion so that callback owner no longer grows
   a second inline queue-advance call.

### Task A3fw: Refresh the retained workshop callback regression for the shared failure handoff [COMPLETED]
Priority: Critical
Primary areas: `tests/test_platform_services.py`, `IMPLEMENTATION_PLAN.md`
Parity estimate: **before 96% -> after 96%**

Completed work:

1. Updated the workshop callback regression so the download-result owner now
   asserts `CL_Workshop_FailActiveDownload()` without the older ignored
   result argument.
2. Added the matching negative assertion covering the removed callback-inline
   queue-advance call.
3. Recorded that callback-owner tightening in the implementation ledger.

### Task A3fx: Refresh the retained workshop helper regression for the shared queue-pop teardown [COMPLETED]
Priority: Critical
Primary areas: `tests/test_platform_services.py`, `IMPLEMENTATION_PLAN.md`
Parity estimate: **before 96% -> after 96%**

Completed work:

1. Updated the focused helper regression to extract
   `CL_Workshop_AdvanceDownloadQueue`.
2. Added assertions covering the shared active-download clear in the queue-pop
   helper plus the new finalize/failure return handoffs.
3. Tightened the downloads-settled assertion so it now references the renamed
   shared owner as well.

### Task A3fy: Refresh the abstraction notes for the retained workshop failure/queue-pop owner split [COMPLETED]
Priority: Critical
Primary areas: `docs/steam_platform_abstraction.md`
Parity estimate: **before 96% -> after 96%**

Completed work:

1. Updated the abstraction note so it now documents the recovered
   `DownloadItemResult` failure handoff into the shared
   `SteamWorkshop_AdvanceDownloadQueue` owner.
2. Recorded that the retained queue-pop helper now owns the active-download
   clear before scanning queued items.
3. Kept the framing explicit that this batch is a bounded retail ownership
   correction inside the already-bounded online-services lane.

### Task A3fz: Refresh the source-gap notes and ledger for the retained workshop failure/queue-pop owner split [COMPLETED]
Priority: Critical
Primary areas: `docs/reverse-engineering/source-file-gap-notes/rw-g01-platform-services.md`,
`IMPLEMENTATION_PLAN.md`
Parity estimate: **before 96% -> after 96%**

Completed work:

1. Updated the `RW-G01` note to match the recovered shared queue-pop ownership
   for both workshop completion and failure lanes.
2. Recorded the next ten micro-closures in the implementation ledger as
   `A3fq` through `A3fz`.
3. Kept the evidence wording explicit so the batch stays framed as retail
   helper-owner correction rather than new compatibility instrumentation.

### Task A3ga: Rename the retained client UI workshop progress import parameters to the recovered low/high split [COMPLETED]
Priority: Critical
Primary areas: `src/code/client/cl_ui.c`, `tests/test_client_workshop_bootstrap_parity.py`
Parity estimate: **before 96% -> after 96%**

Completed work:

1. Rechecked the companion `uix86` workshop-progress reconstruction and
   confirmed that the native `GetItemDownloadInfo` import is reached from the
   parsed `cl_downloadItem` low/high words.
2. Renamed the retained `QL_UI_trap_GetItemDownloadInfo` parameters from
   generic `arg1` / `arg2` to `itemIdLow` / `itemIdHigh` to match that
   recovered split without changing runtime behavior.
3. Refreshed the focused client workshop import assertion to pin the renamed
   retained bridge.

### Task A3gb: Clarify the retained client workshop progress bridge comment against the recovered `uix86` owner [COMPLETED]
Priority: Critical
Primary areas: `src/code/client/cl_ui.c`
Parity estimate: **before 96% -> after 96%**

Completed work:

1. Updated the retained client bridge comment so it now records that the
   companion `uix86` reconstruction parses `cl_downloadItem`, calls the native
   import with the low/high words, and then reads `cl_downloadTime`.
2. Kept the retained bridge behavior unchanged: it still prefers retained
   client workshop state and falls back to the platform Steamworks helper.
3. Preserved the workshop progress import as a naming/evidence correction
   rather than a behavior change.

### Task A3gc: Rename the retained UI syscall wrapper parameters to the recovered low/high split [COMPLETED]
Priority: Critical
Primary areas: `src/code/ui/ui_syscalls.c`, `tests/test_ui_menu_files.py`
Parity estimate: **before 96% -> after 96%**

Completed work:

1. Renamed `trap_QL_GetItemDownloadInfo` to use `itemIdLow` / `itemIdHigh`
   parameter names instead of the older `itemHi` / `itemLo` wording.
2. Kept the retained native import call order unchanged while making that
   order explicit in the wrapper surface.
3. Refreshed the UI menu syscall regression to pin the renamed wrapper
   signature.

### Task A3gd: Rename the retained UI local declaration for the workshop progress import to the recovered low/high split [COMPLETED]
Priority: Critical
Primary areas: `src/code/ui/ui_local.h`
Parity estimate: **before 96% -> after 96%**

Completed work:

1. Updated the retained `ui_local.h` declaration for
   `trap_QL_GetItemDownloadInfo` to use `itemIdLow` / `itemIdHigh`.
2. Kept the declaration aligned with the wrapper implementation and retained
   import cast signature.
3. Preserved the rest of the native UI import surface unchanged.

### Task A3ge: Extend the recovered workshop progress evidence test to pin the parsed item-ID split before the import call [COMPLETED]
Priority: Critical
Primary areas: `tests/test_platform_services.py`
Parity estimate: **before 96% -> after 96%**

Completed work:

1. Extended the companion `uix86` evidence test so it now asserts the
   recovered `sscanf( "%llu", ... )` parse before the `GetItemDownloadInfo`
   import call.
2. Kept the existing assertions covering the native import and
   `cl_downloadTime` read intact.
3. Tightened the evidence trail for the retained low/high parameter naming.

### Task A3gf: Refresh the retained workshop progress import regression for the renamed client bridge parameters [COMPLETED]
Priority: Critical
Primary areas: `tests/test_client_workshop_bootstrap_parity.py`
Parity estimate: **before 96% -> after 96%**

Completed work:

1. Updated the focused workshop progress import regression so it now extracts
   the renamed `QL_UI_trap_GetItemDownloadInfo` signature.
2. Refreshed the retained bridge assertions to use `itemIdLow` /
   `itemIdHigh` in both the client-state and platform fallback calls.
3. Kept the negative assertions against generic download-count/size ownership
   intact.

### Task A3gg: Refresh the CL-G03 parity gate for the retained workshop progress import naming correction [COMPLETED]
Priority: Critical
Primary areas: `tests/test_client_full_parity_gate.py`
Parity estimate: **before 96% -> after 96%**

Completed work:

1. Updated the `CL-G03` parity gate so it now looks for the renamed
   `itemIdLow` / `itemIdHigh` signature on the retained client workshop
   progress bridge.
2. Kept the broader workshop publication/bootstrap/mount ownership gate
   unchanged.
3. Preserved the gate as a source-shape check rather than runtime behavior.

### Task A3gh: Refresh the UI menu import-surface regression for the retained workshop progress naming correction [COMPLETED]
Priority: Critical
Primary areas: `tests/test_ui_menu_files.py`
Parity estimate: **before 96% -> after 96%**

Completed work:

1. Updated the UI menu native-import regression so it now asserts the renamed
   `trap_QL_GetItemDownloadInfo( itemIdLow, itemIdHigh, ... )` wrapper.
2. Kept the rest of the recovered advert/cursor/subscription/measure-text
   import surface unchanged.
3. Recorded the import-surface naming correction in the focused regression.

### Task A3gi: Refresh the abstraction note for the recovered workshop progress import low/high split [COMPLETED]
Priority: Critical
Primary areas: `docs/steam_platform_abstraction.md`
Parity estimate: **before 96% -> after 96%**

Completed work:

1. Updated the abstraction note so it now explicitly records the recovered
   `GetItemDownloadInfo` low/high-word call shape from the parsed
   `cl_downloadItem`.
2. Kept the surrounding workshop progress-bridge ownership story intact.
3. Preserved the framing as companion-evidence-backed naming clarification.

### Task A3gj: Refresh the source-gap notes and ledger for the retained workshop progress import low/high split [COMPLETED]
Priority: Critical
Primary areas: `docs/reverse-engineering/source-file-gap-notes/rw-g01-platform-services.md`,
`IMPLEMENTATION_PLAN.md`
Parity estimate: **before 96% -> after 96%**

Completed work:

1. Updated the `RW-G01` note so it now explicitly describes the recovered
   low/high-word `GetItemDownloadInfo` bridge.
2. Recorded the next ten micro-closures in the implementation ledger as
   `A3ga` through `A3gj`.
3. Kept the batch framed as an evidence-backed interface-naming correction
   rather than a behavior change.

### Task A3gk: Refresh the legacy workshop bootstrap parity suite for the recovered request-helper owner [COMPLETED]
Priority: Critical
Primary areas: `tests/test_client_workshop_bootstrap_parity.py`
Parity estimate: **before 96% -> after 96%**

Completed work:

1. Updated the legacy workshop parity suite to extract
   `CL_Workshop_RequestDownload` instead of the removed pre-audit
   `CL_Workshop_StartDownload` helper.
2. Replaced the stale request-helper assertions with the current retail-backed
   `in cache`, `requesting download`, and `queueing download` owner split.
3. Kept the broader workshop bootstrap coverage anchored to current retained
   source instead of older compatibility wording.

### Task A3gl: Refresh the legacy workshop bootstrap parity suite for the recovered shared queue-pop owner [COMPLETED]
Priority: Critical
Primary areas: `tests/test_client_workshop_bootstrap_parity.py`
Parity estimate: **before 96% -> after 96%**

Completed work:

1. Updated the legacy workshop parity suite to extract
   `CL_Workshop_AdvanceDownloadQueue`.
2. Added the current shared-owner assertions for the active-download clear,
   queued-item clear, and retained queued download request.
3. Removed the older assumptions that queue progression stayed inline under
   callback or finalize owners.

### Task A3gm: Refresh the legacy workshop bootstrap parity suite for the recovered finalize/failure helper signatures [COMPLETED]
Priority: Critical
Primary areas: `tests/test_client_workshop_bootstrap_parity.py`
Parity estimate: **before 96% -> after 96%**

Completed work:

1. Updated the suite to match the current `qboolean`
   `CL_Workshop_FinalizeInstalledItem` / `CL_Workshop_FailActiveDownload`
   helper shapes.
2. Replaced the stale failure-helper expectation that still passed an ignored
   `EResult` parameter.
3. Added the shared queue-pop handoff assertions for both completion and
   failure helpers.

### Task A3gn: Refresh the legacy workshop bootstrap parity suite for the recovered bootstrap exact-string surface [COMPLETED]
Priority: Critical
Primary areas: `tests/test_client_workshop_bootstrap_parity.py`
Parity estimate: **before 96% -> after 96%**

Completed work:

1. Replaced the stale provider/policy-decorated bootstrap string expectations
   with the restored retail `Server requires the following workshop items: %s`
   announcement.
2. Updated the bootstrap-unavailable expectation to the current workshop
   lifecycle log detail instead of the older raw print wording.
3. Kept the request-number/download-cvar ownership assertions aligned with the
   current retained bootstrap caller.

### Task A3go: Refresh the legacy workshop bootstrap parity suite for the recovered callback bootstrap and failure-owner split [COMPLETED]
Priority: Critical
Primary areas: `tests/test_client_workshop_bootstrap_parity.py`
Parity estimate: **before 96% -> after 96%**

Completed work:

1. Updated the callback-bootstrap expectation to the current
   `CL_LogWorkshopLifecycle( "callback-bootstrap", detail )` fallback lane.
2. Refreshed the item-installed and download-result callback assertions to
   match the current null-payload, invalid-app, untracked-item, and
   active-download guards.
3. Added the current shared failure-handoff expectation so the callback owner
   no longer expects an inline queue advance.

### Task A3gp: Refresh the legacy workshop bootstrap parity suite for the recovered workshop frame string surface [COMPLETED]
Priority: Critical
Primary areas: `tests/test_client_workshop_bootstrap_parity.py`
Parity estimate: **before 96% -> after 96%**

Completed work:

1. Updated the workshop frame assertions to the restored retail
   restart-required and downloads-complete print strings.
2. Replaced the older compatibility-only restart log expectation with the
   current retail output plus missing-pk3 warning assertions.
3. Kept the frame-order and `CL_DownloadsComplete()` ownership checks intact.

### Task A3gq: Refresh the legacy workshop bootstrap parity suite for the current queue-complete/request-cvar ownership split [COMPLETED]
Priority: Critical
Primary areas: `tests/test_client_workshop_bootstrap_parity.py`
Parity estimate: **before 96% -> after 96%**

Completed work:

1. Updated the queue-complete assertion to the current
   `Download completed for all steamworks items` detail.
2. Kept the request-number / `cl_downloadItem` / `cl_downloadName` /
   `cl_downloadTime` ownership assertions aligned with the retained bootstrap
   caller and helper split.
3. Preserved the workshop progress owner assertions already tightened in the
   newer focused tests.

### Task A3gr: Restore the full legacy workshop bootstrap parity suite to passing status [COMPLETED]
Priority: Critical
Primary areas: `tests/test_client_workshop_bootstrap_parity.py`
Parity estimate: **before 96% -> after 96%**

Completed work:

1. Re-ran the full legacy workshop parity suite after the assertion refresh.
2. Confirmed the older coverage now passes again instead of failing on removed
   pre-audit helper names.
3. Kept the suite as supplemental validation beside the newer
   platform-services coverage.

### Task A3gs: Refresh the abstraction note for the restored legacy workshop validation alignment [COMPLETED]
Priority: Critical
Primary areas: `docs/steam_platform_abstraction.md`
Parity estimate: **before 96% -> after 96%**

Completed work:

1. Updated the abstraction note so it now records that focused validation
   keeps the recovered workshop owner split aligned across both the
   platform-services and legacy workshop parity suites.
2. Kept the note framed as validation coverage around the already-documented
   recovered owner split.
3. Avoided re-framing the batch as a runtime behavior change.

### Task A3gt: Refresh the source-gap notes and ledger for the restored legacy workshop validation alignment [COMPLETED]
Priority: Critical
Primary areas: `docs/reverse-engineering/source-file-gap-notes/rw-g01-platform-services.md`,
`IMPLEMENTATION_PLAN.md`
Parity estimate: **before 96% -> after 96%**

Completed work:

1. Updated the `RW-G01` note so it now records that the recovered workshop
   owner split is validated in both focused workshop suites.
2. Recorded the next ten micro-closures in the implementation ledger as
   `A3gk` through `A3gt`.
3. Kept the batch framed as validation-gap closure on top of already-restored
   retail-backed behavior.

### Task A3gu: Refresh the Round 05 workshop wrapper note for the retained client-state progress bridge [COMPLETED]
Priority: Critical
Primary areas: `docs/reverse-engineering/quakelive_steam_mapping_round_05.md`
Parity estimate: **before 96% -> after 96%**

Completed work:

1. Updated the Round 05 `SteamUGC_GetItemDownloadInfo` note so it no longer
   describes the older legacy-download-counter fallback.
2. Recorded that the retained UI import now consults retained client workshop
   state first and only then falls back to `QL_Steamworks_GetItemDownloadInfo`,
   the retained wrapper over the same low/high-word
   `SteamUGC_GetItemDownloadInfo` slot.
3. Kept the wrapper promotion itself unchanged.

### Task A3gv: Refresh the Round 14 workshop import-call note for the recovered parsed low/high split [COMPLETED]
Priority: Critical
Primary areas: `docs/reverse-engineering/quakelive_steam_mapping_round_14.md`
Parity estimate: **before 96% -> after 96%**

Completed work:

1. Updated the Round 14 local-fact note so it now records the parsed
   `cl_downloadItem` low/high-word handoff before the UI import call.
2. Removed the stale `(itemHi, itemLo, ...)` wording.
3. Kept the underlying wrapper identification unchanged.

### Task A3gw: Refresh the Round 14 workshop import-owner note for the retained wrapper name and fallback story [COMPLETED]
Priority: Critical
Primary areas: `docs/reverse-engineering/quakelive_steam_mapping_round_14.md`
Parity estimate: **before 96% -> after 96%**

Completed work:

1. Updated the Round 14 note so import `96` is described as
   `QL_UI_trap_GetItemDownloadInfo` instead of the older placeholder wrapper
   name.
2. Recorded the retained-client-state-first progress bridge plus the direct
   Steam item-info fallback.
3. Kept the wrapper role framed as a UI-owned import seam.

### Task A3gx: Refresh the Round 14 alias summary for the recovered workshop import-entry wording [COMPLETED]
Priority: Critical
Primary areas: `docs/reverse-engineering/quakelive_steam_mapping_round_14.md`
Parity estimate: **before 96% -> after 96%**

Completed work:

1. Updated the alias-summary row for `QLUIImport_GetItemDownloadInfo`.
2. Recorded that the wrapper is reached from the parsed `cl_downloadItem`
   low/high words.
3. Kept the alias candidate itself unchanged.

### Task A3gy: Refresh the CL-G03 audit note for the retained workshop request-surface cvars [COMPLETED]
Priority: Critical
Primary areas: `docs/reverse-engineering/client-full-parity-audit-and-implementation-plan-2026-04-09.md`
Parity estimate: **before 96% -> after 96%**

Completed work:

1. Updated the CL-G03 closure note so it now records the retained
   `cl_downloadItem` / `cl_downloadName` / `cl_downloadTime` request surface
   instead of the older byte-counter wording.
2. Kept the surrounding retained bootstrap-owner summary intact.
3. Avoided re-framing the lane as a new runtime change.

### Task A3gz: Refresh the CL-G03 audit note for the retained shared queue-pop callback-owner split [COMPLETED]
Priority: Critical
Primary areas: `docs/reverse-engineering/client-full-parity-audit-and-implementation-plan-2026-04-09.md`
Parity estimate: **before 96% -> after 96%**

Completed work:

1. Updated the CL-G03 closure note so it now records the shared queue-pop
   owner for installed-item completion and download-result failure.
2. Removed the older phrasing that implied direct callback-owned queue
   advancement.
3. Kept the polling-fallback note intact.

### Task A3ha: Refresh the CL-P3 closure note for the retained workshop request-surface cvars [COMPLETED]
Priority: Critical
Primary areas: `docs/reverse-engineering/client-full-parity-audit-and-implementation-plan-2026-04-09.md`
Parity estimate: **before 96% -> after 96%**

Completed work:

1. Updated the CL-P3 completed-work note so it now records
   `cl_downloadItem` / `cl_downloadName` / `cl_downloadTime` instead of the
   older byte-counter wording.
2. Kept the retained active/queued workshop bootstrap summary intact.
3. Preserved the closure note as historical documentation rather than a new
   behavior claim.

### Task A3hb: Refresh the CL-P3 closure note for the retained shared finalize/failure helper handoff [COMPLETED]
Priority: Critical
Primary areas: `docs/reverse-engineering/client-full-parity-audit-and-implementation-plan-2026-04-09.md`
Parity estimate: **before 96% -> after 96%**

Completed work:

1. Updated the CL-P3 callback-exactness closure note so it now records the
   shared finalize/failure helper handoff into
   `SteamWorkshop_AdvanceDownloadQueue`.
2. Removed the older immediate callback-owned queue-advancement wording.
3. Kept the listed validation suites intact.

### Task A3hc: Add focused validation for the stale reverse-engineering workshop note cleanup and tighten the CL-G03 parity gate [COMPLETED]
Priority: Critical
Primary areas: `tests/test_client_workshop_bootstrap_parity.py`,
`tests/test_client_full_parity_gate.py`
Parity estimate: **before 96% -> after 96%**

Completed work:

1. Added a focused regression covering the refreshed Round 05 / Round 14 /
   client-parity-plan workshop notes.
2. Tightened the `CL-G03` parity gate so it now requires the current request-
   surface and shared queue-pop wording in the client parity plan.
3. Kept the gate scoped to current workshop ownership/validation shape rather
   than runtime artifacts.

### Task A3hd: Refresh the abstraction notes, source-gap notes, and ledger for stale reverse-engineering workshop note cleanup [COMPLETED]
Priority: Critical
Primary areas: `docs/steam_platform_abstraction.md`,
`docs/reverse-engineering/source-file-gap-notes/rw-g01-platform-services.md`,
`IMPLEMENTATION_PLAN.md`
Parity estimate: **before 96% -> after 96%**

Completed work:

1. Updated the abstraction/source-gap notes so they now explicitly record that
   the older reverse-engineering workshop notes were brought back into line
   with the recovered low/high import wording and shared queue-pop owner
   story.
2. Recorded the next ten micro-closures in the implementation ledger as
   `A3gu` through `A3hd`.
3. Kept the batch framed as stale-note cleanup and validation tightening on
   top of already-restored retail-backed behavior.

### Task A3he: Refresh the client CVar note for the retained workshop request-surface cvars [COMPLETED]
Priority: Critical
Primary areas: `docs/client_cvars.md`
Parity estimate: **before 96% -> after 96%**

Completed work:

1. Updated the client CVar note so it now records `cl_downloadItem`,
   `cl_downloadName`, and `cl_downloadTime` as the retained workshop
   request-surface trio.
2. Anchored that wording to the recovered `CL_InitDownloads` ownership.
3. Kept the note scoped to documentation rather than new runtime behavior.

### Task A3hf: Refresh the client CVar note for the recovered UI progress bridge [COMPLETED]
Priority: Critical
Primary areas: `docs/client_cvars.md`
Parity estimate: **before 96% -> after 96%**

Completed work:

1. Updated the same note so it now records the parsed `cl_downloadItem`
   low/high-word handoff into the native `GetItemDownloadInfo` probe.
2. Kept `cl_downloadTime` in the documented retained progress surface.
3. Avoided reintroducing the older legacy-byte-counter wording.

### Task A3hg: Refresh the client CVar note for the non-authoritative counter cvars [COMPLETED]
Priority: Critical
Primary areas: `docs/client_cvars.md`
Parity estimate: **before 96% -> after 96%**

Completed work:

1. Updated the note so it now records `cl_downloadCount` and
   `cl_downloadSize` as UI-facing temp cvars rather than the authoritative
   workshop progress owner.
2. Kept the non-Steam fallback guidance explicit.
3. Left the underlying CVar registration untouched.

### Task A3hh: Refresh the CL-P3 closure note for the retained/direct workshop progress bridge [COMPLETED]
Priority: Critical
Primary areas: `docs/reverse-engineering/client-full-parity-audit-and-implementation-plan-2026-04-09.md`
Parity estimate: **before 96% -> after 96%**

Completed work:

1. Updated the historical `CL-P3` closure note so it now describes the
   retained-client-state-first workshop progress bridge plus the direct
   `GetItemDownloadInfo` fallback keyed by parsed `cl_downloadItem` words.
2. Removed the older generic "retained client owner" shorthand.
3. Kept the rest of the closure summary intact.

### Task A3hi: Add focused validation for the client workshop CVar-note alignment [COMPLETED]
Priority: Critical
Primary areas: `tests/test_client_workshop_bootstrap_parity.py`
Parity estimate: **before 96% -> after 96%**

Completed work:

1. Extended the focused workshop-note regression so it now reads
   `docs/client_cvars.md`.
2. Added assertions for the retained request-surface trio, direct
   `GetItemDownloadInfo` bridge wording, and the non-authoritative
   `cl_downloadCount` / `cl_downloadSize` note.
3. Kept the test scoped to evidence-note drift rather than runtime behavior.

### Task A3hj: Tighten the CL-G03 parity gate for current client workshop CVar wording [COMPLETED]
Priority: Critical
Primary areas: `tests/test_client_full_parity_gate.py`
Parity estimate: **before 96% -> after 96%**

Completed work:

1. Added `docs/client_cvars.md` as a tracked CL-G03 documentation input.
2. Tightened the gate so it now requires the current retained/direct workshop
   progress wording in both the client CVar note and the client parity plan.
3. Added a dedicated `client_cvar_notes_current` detail lane for that check.

### Task A3hk: Refresh the abstraction note for the aligned workshop CVar note [COMPLETED]
Priority: Critical
Primary areas: `docs/steam_platform_abstraction.md`
Parity estimate: **before 96% -> after 96%**

Completed work:

1. Updated the abstraction note so it now calls out the aligned
   `docs/client_cvars.md` wording.
2. Recorded that `cl_downloadItem`, `cl_downloadName`, and `cl_downloadTime`
   remain the retained workshop request/progress bridge.
3. Recorded that `cl_downloadCount` / `cl_downloadSize` stay UI-facing temp
   cvars instead of the authoritative owner.

### Task A3hl: Refresh the RW-G01 source-gap note for the aligned workshop CVar note [COMPLETED]
Priority: Critical
Primary areas: `docs/reverse-engineering/source-file-gap-notes/rw-g01-platform-services.md`
Parity estimate: **before 96% -> after 96%**

Completed work:

1. Updated the `RW-G01` note so it now calls out the aligned
   `docs/client_cvars.md` wording alongside the workshop progress bridge note.
2. Recorded the same retained trio versus UI-temp-counter split there.
3. Kept the note framed as documentation alignment over already-restored
   behavior.

### Task A3hm: Refresh the implementation ledger for the workshop CVar-note cleanup [COMPLETED]
Priority: Critical
Primary areas: `IMPLEMENTATION_PLAN.md`
Parity estimate: **before 96% -> after 96%**

Completed work:

1. Recorded the client workshop CVar-note cleanup as explicit micro-closures
   instead of leaving it implicit.
2. Kept the ledger framing evidence-backed and documentation-oriented.
3. Preserved the active `A3` scope summary unchanged.

### Task A3hn: Record the next ten micro-closures for the client workshop CVar-note cleanup batch [COMPLETED]
Priority: Critical
Primary areas: `IMPLEMENTATION_PLAN.md`
Parity estimate: **before 96% -> after 96%**

Completed work:

1. Recorded this batch in the implementation ledger as `A3he` through
   `A3hn`.
2. Kept the batch framed as stale-note cleanup and validation tightening on
   top of already-restored retail-backed behavior.
3. Avoided re-framing the batch as a runtime code change.

### Task A3ho: Refresh the Round 05 workshop wrapper note for the retained direct-helper name [COMPLETED]
Priority: Critical
Primary areas: `docs/reverse-engineering/quakelive_steam_mapping_round_05.md`
Parity estimate: **before 96% -> after 96%**

Completed work:

1. Updated the Round 05 `SteamUGC_GetItemDownloadInfo` note so it now names
   `QL_Steamworks_GetItemDownloadInfo` directly instead of the older generic
   "direct Steam item-info probe" wording.
2. Kept the retained-client-state-first UI import story intact.
3. Preserved the wrapper promotion itself unchanged.

### Task A3hp: Refresh the Round 14 workshop import-call note for the retained direct-helper name [COMPLETED]
Priority: Critical
Primary areas: `docs/reverse-engineering/quakelive_steam_mapping_round_14.md`
Parity estimate: **before 96% -> after 96%**

Completed work:

1. Updated the Round 14 local-fact note so it now names
   `QL_Steamworks_GetItemDownloadInfo` as the retained fallback helper.
2. Kept the parsed `cl_downloadItem` low/high-word handoff explicit.
3. Avoided changing the underlying wrapper identification.

### Task A3hq: Refresh the Round 14 alias summary for the retained direct-helper bridge wording [COMPLETED]
Priority: Critical
Primary areas: `docs/reverse-engineering/quakelive_steam_mapping_round_14.md`
Parity estimate: **before 96% -> after 96%**

Completed work:

1. Updated the alias-summary row for `QLUIImport_GetItemDownloadInfo`.
2. Recorded that the retained `cl_ui.c` bridge falls back to
   `QL_Steamworks_GetItemDownloadInfo`.
3. Kept the alias candidate itself unchanged.

### Task A3hr: Refresh the CL-G03 observed-source note for the retained direct-helper bridge [COMPLETED]
Priority: Critical
Primary areas: `docs/reverse-engineering/client-full-parity-audit-and-implementation-plan-2026-04-09.md`
Parity estimate: **before 96% -> after 96%**

Completed work:

1. Updated the historical `CL-G03` observed-source note so it now names
   `QL_Steamworks_GetItemDownloadInfo` instead of the older generic direct
   Steam-item probe wording.
2. Kept the retained-client-state-first bridge summary intact.
3. Left the surrounding workshop mount/bootstrap notes unchanged.

### Task A3hs: Refresh the CL-P3 closure note for the retained direct-helper bridge [COMPLETED]
Priority: Critical
Primary areas: `docs/reverse-engineering/client-full-parity-audit-and-implementation-plan-2026-04-09.md`
Parity estimate: **before 96% -> after 96%**

Completed work:

1. Updated the historical `CL-P3` closure note so it now names
   `QL_Steamworks_GetItemDownloadInfo` as the retained fallback helper.
2. Kept the retained workshop owner split and legacy-counter exclusion intact.
3. Preserved the closure note as historical documentation rather than a new
   runtime change.

### Task A3ht: Refresh the CL-P3 exit criteria for the recovered low/high workshop progress bridge [COMPLETED]
Priority: Critical
Primary areas: `docs/reverse-engineering/client-full-parity-audit-and-implementation-plan-2026-04-09.md`
Parity estimate: **before 96% -> after 96%**

Completed work:

1. Updated the workshop-progress exit criterion so it now names the recovered
   `GetItemDownloadInfo` low/high-word bridge explicitly.
2. Kept the negative contrast with the older generic legacy counters.
3. Avoided re-framing the lane as a behavior change.

### Task A3hu: Add focused validation for the refreshed workshop helper-note wording [COMPLETED]
Priority: Critical
Primary areas: `tests/test_client_workshop_bootstrap_parity.py`
Parity estimate: **before 96% -> after 96%**

Completed work:

1. Extended the focused workshop-note regression to require the refreshed
   Round 05 / Round 14 helper wording.
2. Added assertions for the current client-parity-plan wording around the
   retained/direct helper split and the low/high-word exit criterion.
3. Kept the test scoped to evidence-note drift rather than runtime behavior.

### Task A3hv: Tighten the CL-G03 parity gate for the refreshed workshop helper-note wording [COMPLETED]
Priority: Critical
Primary areas: `tests/test_client_full_parity_gate.py`
Parity estimate: **before 96% -> after 96%**

Completed work:

1. Tightened the `CL-G03` parity gate so it now requires the refreshed
   retained/direct helper wording in the client parity plan.
2. Kept the existing retained request-surface and shared queue-pop checks
   intact.
3. Preserved the gate as a documentation/validation guard, not a runtime
   behavior claim.

### Task A3hw: Refresh the abstraction and RW-G01 notes for the retained direct-helper wording alignment [COMPLETED]
Priority: Critical
Primary areas: `docs/steam_platform_abstraction.md`,
`docs/reverse-engineering/source-file-gap-notes/rw-g01-platform-services.md`
Parity estimate: **before 96% -> after 96%**

Completed work:

1. Updated the abstraction and `RW-G01` notes so they now record that the
   older client-parity notes were aligned to the explicit
   `QL_Steamworks_GetItemDownloadInfo` fallback naming.
2. Kept the retained-client-state progress bridge and shared queue-pop owner
   story intact.
3. Left the surrounding workshop/service-boundary notes unchanged.

### Task A3hx: Record the next ten micro-closures for the workshop helper-note wording cleanup batch [COMPLETED]
Priority: Critical
Primary areas: `IMPLEMENTATION_PLAN.md`
Parity estimate: **before 96% -> after 96%**

Completed work:

1. Recorded this batch in the implementation ledger as `A3ho` through
   `A3hx`.
2. Kept the batch framed as stale-note cleanup and validation tightening on
   top of already-restored retail-backed behavior.
3. Avoided re-framing the batch as a runtime code change.

### Task A3hy: Refresh the top-level CL-P3 summary for the retained direct-helper name [COMPLETED]
Priority: Critical
Primary areas: `docs/reverse-engineering/client-full-parity-audit-and-implementation-plan-2026-04-09.md`
Parity estimate: **before 96% -> after 96%**

Completed work:

1. Updated the top-level `CL-P3` summary so it now names
   `QL_Steamworks_GetItemDownloadInfo` instead of the older generic direct
   probe wording.
2. Kept the retained-client-state-first bridge summary intact.
3. Preserved the surrounding parity summary unchanged.

### Task A3hz: Refresh the top-level CL-P3 summary for the recovered low/high-word bridge wording [COMPLETED]
Priority: Critical
Primary areas: `docs/reverse-engineering/client-full-parity-audit-and-implementation-plan-2026-04-09.md`
Parity estimate: **before 96% -> after 96%**

Completed work:

1. Updated the same summary so it now records the retail
   `SteamUGC_GetItemDownloadInfo` low/high-word slot more explicitly.
2. Kept the parsed `cl_downloadItem` ownership visible in the wording.
3. Avoided reintroducing generic helper shorthand.

### Task A3ia: Refresh the historical A3gu implementation-plan note for the retained direct-helper name [COMPLETED]
Priority: Critical
Primary areas: `IMPLEMENTATION_PLAN.md`
Parity estimate: **before 96% -> after 96%**

Completed work:

1. Updated the older `A3gu` completed-work note so it now names
   `QL_Steamworks_GetItemDownloadInfo` directly.
2. Kept the retained-client-state-first import story intact.
3. Preserved the historical task framing.

### Task A3ib: Refresh the historical A3el implementation-plan note for UI-facing temp-cvar wording [COMPLETED]
Priority: Critical
Primary areas: `IMPLEMENTATION_PLAN.md`
Parity estimate: **before 96% -> after 96%**

Completed work:

1. Updated the older `A3el` note so it now describes the then-retained
   `cl_downloadCount` / `cl_downloadSize` updates as UI-facing temp cvars.
2. Kept the note historically accurate for that intermediate step.
3. Avoided implying those counters were ever the authoritative progress owner.

### Task A3ic: Add focused validation for the top-level CL-P3 workshop helper wording [COMPLETED]
Priority: Critical
Primary areas: `tests/test_client_workshop_bootstrap_parity.py`
Parity estimate: **before 96% -> after 96%**

Completed work:

1. Extended the focused workshop-note regression to require the refreshed
   top-level `CL-P3` summary wording.
2. Kept the existing Round 05 / Round 14 note checks intact.
3. Left the test scoped to evidence-note drift rather than runtime behavior.

### Task A3id: Add focused validation for the historical implementation-plan workshop wording [COMPLETED]
Priority: Critical
Primary areas: `tests/test_client_workshop_bootstrap_parity.py`
Parity estimate: **before 96% -> after 96%**

Completed work:

1. Extended the same regression so it now reads `IMPLEMENTATION_PLAN.md`.
2. Added assertions for the refreshed `A3gu` helper wording and `A3el`
   temp-cvar wording.
3. Kept the validation surface narrow and evidence-backed.

### Task A3ie: Tighten the CL-G03 parity gate for the refreshed implementation-plan workshop wording [COMPLETED]
Priority: Critical
Primary areas: `tests/test_client_full_parity_gate.py`
Parity estimate: **before 96% -> after 96%**

Completed work:

1. Tightened the `CL-G03` parity gate so it now requires the refreshed
   top-level client-plan wording plus the aligned implementation-plan notes.
2. Added a dedicated `implementation_plan_notes_current` detail lane for that
   check.
3. Preserved the gate as a documentation/validation guard, not a runtime
   behavior claim.

### Task A3if: Refresh the abstraction note for the aligned top-level summary and implementation-plan wording [COMPLETED]
Priority: Critical
Primary areas: `docs/steam_platform_abstraction.md`
Parity estimate: **before 96% -> after 96%**

Completed work:

1. Updated the abstraction note so it now calls out the aligned top-level
   `CL-P3` summary and older implementation-plan workshop note wording.
2. Recorded the explicit helper naming and UI-facing temp-cvar framing there.
3. Left the broader workshop boundary story unchanged.

### Task A3ig: Refresh the RW-G01 note for the aligned top-level summary and implementation-plan wording [COMPLETED]
Priority: Critical
Primary areas: `docs/reverse-engineering/source-file-gap-notes/rw-g01-platform-services.md`
Parity estimate: **before 96% -> after 96%**

Completed work:

1. Updated the `RW-G01` note so it now records the aligned top-level `CL-P3`
   summary and implementation-plan workshop wording.
2. Kept the explicit helper naming and UI-facing temp-cvar framing visible.
3. Preserved the surrounding compatibility-boundary note unchanged.

### Task A3ih: Record the next ten micro-closures for the workshop summary-and-ledger wording cleanup batch [COMPLETED]
Priority: Critical
Primary areas: `IMPLEMENTATION_PLAN.md`
Parity estimate: **before 96% -> after 96%**

Completed work:

1. Recorded this batch in the implementation ledger as `A3hy` through
   `A3ih`.
2. Kept the batch framed as stale-note cleanup and validation tightening on
   top of already-restored retail-backed behavior.
3. Avoided re-framing the batch as a runtime code change.

### Task A3ii: Close `RW-G01` as a documented bounded divergence across the repo-wide ledgers [COMPLETED]
Priority: Critical
Primary areas: `AUDIT.md`, `IMPLEMENTATION_PLAN.md`,
`docs/reverse-engineering/repo-wide-parity-audit-2026-04-21.md`,
`docs/reverse-engineering/source-file-parity-ledger-2026-04-22.md`,
`docs/reverse-engineering/source-file-parity-audit-plan-2026-04-22.md`,
`docs/reverse-engineering/source-file-gap-notes/`,
`tools/reverse-engineering/generate_source_file_audit.py`
Parity estimate: **before 96% -> after 98%**

Completed work:

1. Reclassified the `RW-G01` online-services lane as an intentional
   documented divergence instead of active repo-wide parity debt, while
   keeping the strict-retail Windows target unchanged at `100%`.
2. Updated the source-file audit generator and regenerated the plan, ledger,
   and per-file note set so the seven `RW-G01` owners now land under
   documented-divergence notes while `RW-G02` remains the only active
   file-level compatibility gap family.
3. Refreshed the top-level repo-wide ledgers so the checked-in whole-repo
   estimate now reads `98%`, with `RW-G02` and `RW-G04` left as the active
   remaining repo-wide gap families.

### Task A4j: Add a bounded silent Linux sound sink and close the OSS shutdown leak [COMPLETED]
Priority: Medium
Primary areas: `src/code/unix/linux_snd.c`,
`tests/test_non_windows_portability.py`,
`docs/reverse-engineering/source-file-gap-notes/rw-g02-linux-snd.md`,
`docs/platform/toolchain-matrix.md`, `docs/build/linux-glibc-32bit.md`
Parity estimate: **before 98% -> after 98%**

Completed work:

1. Added an explicit silent Linux DMA sink selected through `snddevice null`,
   `none`, or `silent`, giving headless/client smoke probes a non-OSS sound
   path without pulling in ALSA, PulseAudio, SDL, or other external library
   code.
2. Reconstructed the Linux sound lifecycle around the retained OSS backend so
   `audio_fd` starts at `-1`, failed init paths route through shared cleanup,
   and `SNDDMA_Shutdown()` now unmaps the mmap DMA buffer and closes the sound
   descriptor instead of leaving restart/error cleanup implicit.
3. Kept the result deliberately bounded: the default Linux sound backend is
   still the legacy `/dev/dsp` OSS path, the silent sink is not an audible
   backend, and `RW-G02` remains open until the broader Linux client renderer,
   audio, input, and validation boundary is settled.
4. Expanded the focused non-Windows portability suite and refreshed the
   platform/gap notes so the new silent sink, DMA-position simulation, and OSS
   shutdown cleanup stay source-pinned as compatibility work rather than
   strict-retail Windows parity.

### Task A4k: Bound the retained Linux joystick device and restart lifecycle [COMPLETED]
Priority: Medium
Primary areas: `src/code/unix/linux_joystick.c`,
`src/code/unix/linux_glimp.c`, `src/code/unix/linux_local.h`,
`tests/test_non_windows_portability.py`,
`docs/reverse-engineering/source-file-gap-notes/rw-g02-linux-joystick.md`,
`docs/reverse-engineering/source-file-gap-notes/rw-g02-linux-glimp.md`,
`docs/platform/toolchain-matrix.md`
Parity estimate: **before 98% -> after 98%**

Completed work:

1. Reworked the retained Linux joystick lane so startup now scans modern
   `/dev/input/js0` through `/dev/input/js3` before the historical
   `/dev/js0` through `/dev/js3` nodes, while still avoiding SDL or any other
   external input library.
2. Added explicit joystick shutdown/restart handling: `IN_ShutdownJoystick()`
   releases queued joystick key state, clears tracked axes/buttons, closes
   `joy_fd`, and resets `ui_joyavail`; `linux_glimp.c` now calls that path on
   input shutdown and when latched `in_joystick` changes trigger a restart.
3. Bounded event translation so Linux button events cannot exceed the
   `K_JOY1` through `K_JOY32` range and axis events cannot exceed the
   retained eight-axis / sixteen-direction-key table.
4. Kept `RW-G02` open because this is still retained Linux joystick
   compatibility, not a validated modern Linux client input stack, and pinned
   that distinction in the focused portability suite and gap notes.

### Task A4l: Bound the retained Linux mouse/input shutdown lifecycle [COMPLETED]
Priority: Medium
Primary areas: `src/code/unix/linux_glimp.c`,
`tests/test_non_windows_portability.py`,
`docs/reverse-engineering/source-file-gap-notes/rw-g02-linux-glimp.md`,
`docs/reverse-engineering/function-parity-gap-audit-2026-04-24.md`,
`docs/platform/toolchain-matrix.md`, `docs/build/linux-glibc-32bit.md`
Parity estimate: **before 98% -> after 98%**

Completed work:

1. Reconstructed the Linux input shutdown path around the retained X11 mouse
   grab lifecycle so `IN_Shutdown()` now calls `IN_DeactivateMouse()` before
   clearing `mouse_avail`, avoiding stale grab/activity state across
   `in_restart` and normal input teardown.
2. Kept joystick teardown in the same host-owned shutdown path and now clears
   `mouse_active` explicitly after the deactivate call, so a later `IN_Init()`
   can reactivate the mouse according to the current cvar state instead of
   inheriting a stale active flag.
3. Added focused source assertions and refreshed the RW-G02 notes so this
   remains bounded Linux-host compatibility work rather than a claim that the
   legacy X11/GLX/DGA client path is modern or retail-equivalent.

### Task A4m: Bound the retained Unix native-module loader roots and outputs [COMPLETED]
Priority: Medium
Primary areas: `src/code/unix/unix_main.c`,
`tests/test_non_windows_portability.py`,
`docs/reverse-engineering/source-file-gap-notes/rw-g02-unix-main.md`,
`docs/reverse-engineering/function-parity-gap-audit-2026-04-24.md`,
`docs/platform/toolchain-matrix.md`, `docs/build/linux-glibc-32bit.md`
Parity estimate: **before 98% -> after 98%**

Completed work:

1. Reworked the retained Unix `Sys_LoadDll()` root probe into an explicit
   bounded search over cwd, `fs_homepath`, `fs_basepath`, and `fs_cdpath`, so
   archived/native module roots can be reached through the same configured
   data-root lane used elsewhere in the Unix host.
2. Reset the legacy `entryPoint` output before probing, matching the safer
   failure contract used by the recovered Win32 loader shape and preventing a
   failed Unix load from leaving stale caller state behind.
3. Added focused source assertions and refreshed the RW-G02 notes so this
   remains Unix host compatibility work, not a claim that the non-Windows
   native-module runtime is retail-equivalent.

### Task A4n: Bound the Unix event-loop packet payload copy [COMPLETED]
Priority: Medium
Primary areas: `src/code/unix/unix_main.c`,
`tests/test_non_windows_portability.py`,
`docs/reverse-engineering/source-file-gap-notes/rw-g02-unix-main.md`,
`docs/reverse-engineering/function-parity-gap-audit-2026-04-24.md`,
`docs/platform/toolchain-matrix.md`, `docs/build/linux-glibc-32bit.md`
Parity estimate: **before 98% -> after 98%**

Completed work:

1. Reconstructed the retained Unix `Sys_GetEvent()` packet queue copy so
   `SE_PACKET` events preserve only unread bytes after `netmsg.readcount`,
   matching the recovered Win32 event-loop packet path and its SOCKS-aware
   comment.
2. Kept the change deliberately bounded: the current Unix UDP receiver still
   leaves `readcount` at zero, but the event loop now honors that field if a
   future Unix packet transport consumes header bytes before queuing.
3. Added focused source assertions and refreshed the RW-G02 notes so this is
   recorded as Unix host event-loop compatibility, not proof of full
   non-Windows runtime parity.

### Task A4o: Bound Unix native-module candidate validation [COMPLETED]
Priority: Medium
Primary areas: `src/code/unix/unix_main.c`,
`tests/test_non_windows_portability.py`,
`docs/reverse-engineering/source-file-gap-notes/rw-g02-unix-main.md`,
`docs/reverse-engineering/function-parity-gap-audit-2026-04-24.md`,
`docs/platform/toolchain-matrix.md`, `docs/build/linux-glibc-32bit.md`
Parity estimate: **before 98% -> after 98%**

Completed work:

1. Reworked the retained Unix `Sys_LoadDll()` probing loop so each opened
   native-module candidate is validated before returning a handle: it must
   expose `dllEntry` and then satisfy either the Quake Live export-table path,
   a `vmMain` export, or the legacy `dllEntry()`-returned entry point path.
2. Closed incompatible `dlopen()` handles, reset failed-load outputs, and
   continued to the next configured root instead of treating the first opened
   but incompatible shared object as the final loader outcome.
3. Added focused source assertions and refreshed the RW-G02 docs so this stays
   recorded as bounded Unix host compatibility work aligned with the recovered
   Win32 loader shape, not proof of full non-Windows runtime parity.

### Task A4p: Bound the null sound host with an explicit silent DMA sink [COMPLETED]
Priority: Medium
Primary areas: `src/code/null/null_snddma.c`,
`tests/test_non_windows_portability.py`,
`docs/reverse-engineering/source-file-gap-notes/rw-g02-null-snddma.md`,
`docs/reverse-engineering/function-parity-gap-audit-2026-04-24.md`,
`docs/platform/toolchain-matrix.md`
Parity estimate: **before 98% -> after 98%**

Completed work:

1. Replaced the null sound host's outright `SNDDMA_Init()` failure with a
   local silent DMA sink that seeds the shared `dma` shape, owns a deterministic
   22,050 Hz 16-bit stereo buffer, and advances its DMA cursor from
   `Sys_Milliseconds()`.
2. Added explicit buffer/state cleanup through `SNDDMA_Shutdown()`,
   `SNDDMA_BeginPainting()`, and `S_ClearSoundBuffer()` while preserving the
   compatibility-only no-op behavior for submit, activation, sound
   registration, local sound, and voice samples.
3. Added focused source assertions and refreshed the RW-G02 docs so this
   remains a bounded null-host compatibility sink, not an audible backend or
   a broader runtime parity claim.

### Task A4q: Make the null renderer host refuse fake GL initialization [COMPLETED]
Priority: Medium
Primary areas: `src/code/null/null_glimp.c`,
`tests/test_non_windows_portability.py`,
`docs/reverse-engineering/source-file-gap-notes/rw-g02-null-glimp.md`,
`docs/reverse-engineering/function-parity-gap-audit-2026-04-24.md`,
`docs/platform/toolchain-matrix.md`
Parity estimate: **before 98% -> after 98%**

Completed work:

1. Replaced the null `QGL_Init()` success stub with an explicit `qfalse`
   result, so the compatibility host no longer claims that a GL backend was
   loaded when no renderer library or function pointers exist.
2. Made `GLimp_Init()` fail with a clear fatal message for the null renderer
   host and routed `GLimp_Shutdown()` through `QGL_Shutdown()`, which now clears
   retained extension pointers and logging state.
3. Added focused source assertions and refreshed the RW-G02 docs so this stays
   recorded as a bounded renderer-host compatibility boundary, not a real
   graphics context or swap path.

### Task A4r: Route the null key-event pump through explicit no-device input state [COMPLETED]
Priority: Medium
Primary areas: `src/code/null/null_input.c`,
`tests/test_non_windows_portability.py`,
`docs/reverse-engineering/source-file-gap-notes/rw-g02-null-input.md`,
`docs/reverse-engineering/function-parity-gap-audit-2026-04-24.md`,
`docs/platform/toolchain-matrix.md`
Parity estimate: **before 98% -> after 98%**

Completed work:

1. Extended the null input compatibility state so it clears the retained
   `in_joystick->modified` latch while continuing to pin `ui_joyavail` to `0`.
2. Routed `Sys_SendKeyEvents()` through that no-device refresh once null input
   is initialized, making the key-event pump an explicit disabled-input
   maintenance path instead of an unstructured empty placeholder.
3. Added focused source assertions and refreshed the RW-G02 docs so this stays
   recorded as a null-host input boundary, not a real input backend or event
   source.

### Task A4s: Bound the Linux GLX shutdown and end-frame lifecycle [COMPLETED]
Priority: Medium
Primary areas: `src/code/unix/linux_glimp.c`,
`tests/test_non_windows_portability.py`,
`docs/reverse-engineering/source-file-gap-notes/rw-g02-linux-glimp.md`,
`docs/reverse-engineering/function-parity-gap-audit-2026-04-24.md`,
`docs/platform/toolchain-matrix.md`
Parity estimate: **before 98% -> after 98%**

Completed work:

1. Reworked `GLimp_Shutdown()` so partial Linux GLX init state is cleaned up
   instead of returning early when `ctx` is missing: the path now deactivates
   mouse state, detaches any current context, destroys retained context/window
   state only when present, restores VidMode/gamma state, closes the QGL log,
   clears the GLX globals, and releases QGL before clearing renderer state.
2. Guarded `GLimp_EndFrame()` against missing display/window/swap state so a
   failed partial init or post-shutdown call cannot fall through into stale
   GLX function-pointer state.
3. Added focused source assertions and refreshed the RW-G02 docs so this stays
   recorded as Linux renderer-host lifecycle containment, not a modern GLX or
   SDL-style Linux client parity claim.

## Active tasks

### Task A4: Modernise or explicitly contain the non-Windows portability lanes [COMPLETED 2026-06-05]
Priority: High
Primary areas: `src/code/unix/`, `src/code/null/`,
`docs/platform/toolchain-matrix.md`, `docs/build/linux-glibc-32bit.md`,
`docs/reverse-engineering/non-windows-portability-boundary-2026-06-05.md`
Parity estimate: **before 98% -> after 99%**

Scope:

1. Replace the remaining Unix `Sys_*` helper placeholders that still matter
   after the restored low-memory, Linux/glibc function compare/checksum,
   `q3monkeyid` marker-probe, bounded `gprof`-control paths, and bounded
   clipboard retrieval path, bounded data-root probe, and Linux silent sound
   sink / OSS shutdown cleanup plus bounded Linux joystick descriptor/restart
   handling plus Linux mouse-grab shutdown cleanup plus Linux GLX partial-init
   shutdown/end-frame containment and the bounded Unix native-module root probe
   plus candidate validation, Unix packet event copy,
   the null renderer GL-init refusal, the explicit null silent DMA sink, and
   the null no-device key pump, or keep them clearly classified as
   compatibility-only. The null host/client/audio shims now match the current
   contract surface closely enough that the remaining work is primarily about
   the real Unix host boundary rather than stale null host/client/audio/input
   entry points.
2. Decide whether Linux client/renderer/audio/input support is a real target or
   whether the current server-only path should remain the bounded endpoint.
3. Refresh the toolchain/runtime guidance and validation coverage once the
   intended portability boundary is settled.

Completed work:

1. Re-baselined the non-Windows portability lanes around the current target:
   hosted POSIX source builds and dedicated/server-module validation are the
   active support endpoints.
2. Chose explicit containment for the legacy Linux client/runtime stack: the
   retained X11/GLX/DGA renderer/input path, OSS-first audio host, silent
   sink, and null host/client/audio/input/renderer shims are compatibility-only
   carries, not active modern Linux client parity targets.
3. Added
   `docs/reverse-engineering/non-windows-portability-boundary-2026-06-05.md`
   and refreshed the RW-G02 gap notes, repo-wide audit, function-gap summary,
   toolchain matrix, Linux glibc preset note, and focused portability tests so
   this boundary is enforced as a documented closure.
4. Future Linux client/runtime work now needs a successor task that explicitly
   adopts a modern renderer/audio/input dependency stack and reproducible
   validation.

### Task A6: Refresh build/runtime evidence for the repo-wide ledger [COMPLETED 2026-06-05]
Priority: Medium
Primary areas: tracked runtime probe bundles, native build helpers, platform
docs
Parity estimate: **before 99% -> after 99%**

Scope:

1. Refresh the archived runtime evidence bundles on a current toolchain instead
   of relying solely on the April 2026 tracked artifacts, and promote the
   stable `latest` aliases only when reruns remain sufficient.
2. Re-run native build validation where the required Windows toolchain is
   available and fold the results back into the repo-wide audit.
3. Capture the remaining glibc and continuous/self-hosted publication
   follow-ups called out in `docs/platform/toolchain-matrix.md`, including the
   remaining retail-module runtime freshness tail.

Completed work:

1. Added
   `docs/reverse-engineering/runtime-build-evidence-refresh-2026-06-05.json`
   and `docs/reverse-engineering/runtime-build-evidence-refresh-2026-06-05.md`
   as the A6 evidence ledger.
2. Confirmed the retail-module `latest` alias now points at
   `artifacts/module_validation/logs/retail_module_runtime_evidence_20260602.json`,
   with no warnings, no missing markers, retail `ui`/`qagame`/`cgame` loads,
   `Server: bloodrun`, `Going from CS_PRIMED to CS_ACTIVE`, screenshots, and
   vm-trace create/free/call traffic.
3. Verified Visual Studio 2022 `v143` availability and ran the modern native
   validation lane with optional codecs disabled. MSBuild produced a clean
   `Release|x86` build with `0` warnings and `0` errors; the wrapper timed out
   after the successful build while continuing post-build checks, so
   `tools/ci/assert-dll-exports.ps1` was rerun directly.
4. Tightened `tools/ci/assert-dll-exports.ps1` so it prefers the newest
   Release artifact before inspecting exports. The direct export audit now
   validates the fresh `build/win32/Release/modules/qagamex86/qagamex86.dll`
   and `build/win32/Release/modules/cgamex86/cgamex86.dll` outputs rather
   than older `bin/baseq3` copies.
5. Recorded that strict retail VC10 staged-runtime evidence is still blocked
   on this checkout because `tools/ci/audit-retail-toolchain.ps1 -Strict`
   expects `PlatformToolset` `v100`, while the checked-in project files
   currently use `v141`. This is now a documented validation boundary, not an
   uninspected A6 freshness gap.

Earlier 2026-06-05 preflight, now superseded by the A6 refresh ledger:

1. `docs/reverse-engineering/windows-native-validation-preflight-2026-06-05.md`
   now records the local native Windows validation preflight. The wrapper-level
   repo-root inference issue was fixed in
   `tools/ci/audit-retail-toolchain.ps1` and
   `tools/ci/validate-windows-native.ps1`, so documented `-File` invocations
   now reach the project metadata checks.
2. `powershell -NoProfile -ExecutionPolicy Bypass -File
   .\tools\ci\audit-retail-toolchain.ps1 -Strict` stops before build because
   the strict retail audit expects `PlatformToolset=v100` while
   `src/code/quakelive_steam.vcxproj` currently reports `v141`.
3. `powershell -NoProfile -ExecutionPolicy Bypass -File
   .\tools\ci\validate-windows-native.ps1 -RuntimeProfile retail` verifies the
   current `v141` defaults for `qagamex86`, `cgamex86`, `uix86`,
   `quakelive_steam`, and `awesomium_process`, then hits the same strict
   `v100` audit blocker. The later A6 refresh above adds modern-host build
   evidence and current retail-module runtime evidence while keeping this
   strict VC10 blocker documented.

### Task 23: Ownerdraw/stat payload completion and validation [COMPLETED]
Priority: High
Primary areas: `src/code/game/`, `src/code/cgame/`, runtime validation harnesses
Parity estimate: **before 99% -> after 100%**

Completed work:

1. Revalidated the ownerdraw debug payload against the current runtime capture
   path and confirmed that the live `pickupAvg` slab is emitted as fixed-point
   seconds rather than the older integer-only fixture assumption.
2. Updated the ownerdraw runtime harness in
   `tests/test_ownerdraw_stats_logging.py` so the debug-ownerdraw assertion
   path now accepts and normalizes float `pickupAvg` CSV payloads while keeping
   the integer stat families strict.
3. Re-ran the focused ownerdraw/stat validation surface on the current
   worktree; no concrete unsupported ownerdraw or `PLAYER_STATS` payload field
   remains in the active repo-level gap register.

### Task 24: Gameplay validation sweep [COMPLETED]
Priority: High
Primary areas: physics, Race, gametype-specific rules
Parity estimate: **before 99% -> after 100%**

Completed work:

1. Expanded the gametype lifecycle harness so it now builds through the shared
   compiler helper on Windows as well as POSIX, and it directly validates duel
   warmup/configstring sequencing, Race lifecycle routing, and CA/RR
   round-warmup init dispatch.
2. Tightened the ready-up and match-state regression guards around the retail
   gametype truth tables, including the both-teams-present gate and the
   Attack & Defend inclusion in the round-controller team-count publisher set.
3. Reconfirmed the focused Race and shared `pmove` regression lanes on the
   current worktree; the gameplay validation sweep is now covered by dedicated
   fixtures rather than left as an open catch-all validation reminder.

### Task 25: UI import contract retail remap guard [COMPLETED]
Priority: High
Primary areas: `tests/test_ui_menu_files.py`, `src/code/ui/ui_public.h`,
`src/code/ui/ui_syscalls.c`
Parity estimate: **before 98% -> after 100%** for the focused `uiImport_t`
legacy-to-retail-native import contract.

Completed work:

1. Rechecked the committed `uix86.dll` native import evidence and preserved the
   current runtime split: `uiImport_t` remains the legacy source/QVM syscall
   ABI, while `uiQlImport_t` carries the recovered retail native slot numbers.
2. Added a parser-based parity guard that pins every `uiImport_t` value,
   verifies the complete `UI_MapNativeImport` handoff into recovered retail
   native slots, and keeps direct-only retail native slots out of the legacy
   syscall surface.
3. Re-ran the full UI static regression lane so future drift in either the
   enum or remap table fails before it can affect retail-module loading.

## Working priority order

1. Keep the online-service compatibility boundary explicitly documented if a
   future open replacement path is introduced.

## Reference audits for closed surfaces

- `docs/reverse-engineering/non-windows-portability-boundary-2026-06-05.md`
- `docs/reverse-engineering/runtime-build-evidence-refresh-2026-06-05.md`
- `docs/reverse-engineering/repo-wide-parity-audit-2026-04-21.md`
- `docs/reverse-engineering/source-file-parity-ledger-2026-04-22.md`
- `docs/reverse-engineering/source-file-parity-audit-plan-2026-04-22.md`
- `docs/reverse-engineering/historical-audit-index-2026-04-22.md`
- `docs/reverse-engineering/engine-full-parity-audit-and-implementation-plan-2026-04-10.md`
- `docs/reverse-engineering/game-module-parity-audit-and-implementation-plan-2026-04-10.md`
- `docs/reverse-engineering/ui-full-parity-audit-and-implementation-plan-2026-04-05.md`
- `docs/reverse-engineering/qcommon-full-parity-audit-and-implementation-plan-2026-04-10.md`
- `docs/reverse-engineering/qshared-retail-helper-parity-audit-2026-04-17.md`
- `docs/reverse-engineering/renderer-full-parity-audit-and-implementation-plan-2026-04-09.md`
- `docs/reverse-engineering/server-full-parity-audit-and-implementation-plan-2026-04-10.md`
- `docs/reverse-engineering/engine-host-support-full-parity-audit-and-implementation-plan-2026-04-10.md`
- `docs/reverse-engineering/platform-specific-engine-parity-audit-and-implementation-plan-2026-04-16.md`
- `docs/reverse-engineering/engine-netcode-parity-audit-2026-04-16.md`
- `docs/reverse-engineering/awesomium-browser-host-parity-audit-and-implementation-plan-2026-04-16.md`

## Historical closure anchors kept for parity-gate compatibility

The entries below are intentionally terse. They preserve the exact historical
task headings and parity-estimate lines that checked-in parity gates still read
from this file, without keeping pages of duplicated completed-task prose in the
active plan.

### Task 34: Cgame Attack and Defend round-scoreboard owner parity closure [COMPLETED]

### Task 31: Strict retail game-module parity closure [COMPLETED]

### Task 73: Renderer internal helper-family ownership closure tranche [COMPLETED]
Parity estimate: **before 93% -> after 96%** (`RG-P5` complete; `RG-G06` closed)

### Task 75: Renderer strict retail-font-stack re-audit and closure-plan refresh [COMPLETED]

### Task 87: Client CL-P6 parity gate and runtime-evidence closure [COMPLETED]
Parity estimate: **before 99% -> after 100%**

### Task 92: Qcommon QC-P2 parity gate and Windows-friendly harness closure [COMPLETED]

### Task 94: Qcommon QC-P3 retail homepath closure [COMPLETED]

### Task 97: Qcommon QC-P4 collision leaf ownership closure [COMPLETED]

### Task 100: Server SV-P7 parity gate and dedicated runtime-evidence closure [COMPLETED]
Parity estimate: **before 97% -> after 100%**

### Task 102: Qcommon QC-P5 fallback VM closure [COMPLETED]

### Task 103: Remaining engine host/support EH-P2 Win32 Unicode clipboard closure [COMPLETED]

### Task 104: Strict retail game-module final ledger and runtime-evidence reconciliation [COMPLETED]

### Task 104: Qcommon QC-P6 runtime-evidence and ledger closure [COMPLETED]
Parity estimate: **before 98% -> after 100%**

### Task 110: Qshared shared-helper exactness and validation-lane closure [COMPLETED]
Parity estimate: **before 99% -> after 100%**

### Task 105: Remaining engine host/support EH-P3 raw-input host closure [COMPLETED]

### Task 111: Client/input m_cpi and general mouse parity closure [COMPLETED]
Parity estimate: **before 96% -> after 100%** (`m_cpi` math was already retail-mapped; this closes the remaining Win32 mouse host/key-number gaps)

### Task 112: Win32 game-cursor mouse ownership closure [COMPLETED]
Parity estimate: **before 99% -> after 100%** (browser/UI/cgame absolute-coordinate lanes now preserve the retail cursor-owner split; UI/cgame game cursors suppress the OS cursor while browser cursor overrides remain browser-owned)

### Task 106: Remaining engine host/support EH-P6 parity gate and evidence closure [COMPLETED]
Parity estimate: **before 89% -> after 92%**

### Task 107: Remaining engine host/support EH-P4 botlib internal proof closure [COMPLETED]
Parity estimate: **before 92% -> after 95%**

### Task 109: Remaining engine host/support EH-P1 boundary formalisation closure [COMPLETED]
Parity estimate: **before 100% -> after 100%** (`EH-P1` complete; strict-retail scope classification formalised)

### Task 113: Clientinfo compact identity/color transport closure [COMPLETED]
Parity estimate: **before 94% -> after 98%** for the scoped `CS_PLAYERS` clientinfo color, SteamID, and country transport lane

### Task 114: Clientinfo identity-tail and native sidecar reconstruction [COMPLETED]
Parity estimate: **before 82% -> after 90%** for the scoped cgame clientinfo
identity/speaking/avatar tail. This pass confirmed the retail `0x738`
clientinfo stride, documented the `0x710..0x730` privilege, queue, speaking,
identity, and avatar tail, and reconstructed source wiring for `cn`, `xcn`,
`rp`, `p`, cached clean names, avatar handles, and in-record speaking state.
This pass left the binary-exact cgame animation/clientinfo layout split open:
retail uses `37` animation records of size `0x18`, which is closed by the
follow-up Task 115 animation-record pass below.

### Task 115: Clientinfo cgame animation record and retail stride closure [COMPLETED]
Parity estimate: **before 90% -> after 94%** for the scoped cgame clientinfo
layout/animation lane. This pass confirmed the retail animation cache at
clientinfo offset `0x318` with `37` records of size `0x18`, custom sounds at
`0x690`, and the retail outer clientinfo stride of `0x738`. Source cgame now
uses a local `cgAnimation_t` record without the shared GPL `flipflop` field,
cgame animation parsing/playback consumes that type, and `clientInfo_t` carries
an explicit temporary pad so the x86 source stride matches retail. The shared
game/UI `animation_t` remains untouched. The remaining gap is the internal
member-order repack to move the animation, sound, identity, avatar, and voice
fields to their retail byte offsets naturally, which is closed by Task 116.

### Task 116: Clientinfo internal anchor-offset repack [COMPLETED]
Parity estimate: **before 94% -> after 96%** for the scoped cgame clientinfo
byte-layout lane. This pass moved the recovered native sidecar fields behind
`sounds[MAX_CUSTOM_SOUNDS]` and aligned the strongest retail anchors in the x86
source layout: fixed animation metadata at `0x2E0`, model handles at `0x2FC`,
animations at `0x318`, custom sounds at `0x690`, privilege/spectator queue at
`0x710..0x718`, speaking state at `0x71C..0x720`, Steam identity at
`0x728..0x72C`, avatar cache at `0x730`, and final size `0x738`. The remaining
gap is the early `0x008..0x2DF` mixed retail/source-compatibility region,
including model/head-model scratch strings, color override cache, country flag
cache, and scoreboard/team-overlay mirrors.

### Task 117: Clientinfo early-slot retail offset map [COMPLETED]
Parity estimate: **before 96% -> after 97%** for the scoped cgame clientinfo
byte-layout lane. This pass promoted the early `0x000..0x2FC` retail map into
named `CG_CLIENTINFO_RETAIL_OFFSET_*` constants and documented the evidence
chain from `CG_NewClientInfo`, `CG_CopyClientIdentity`, placement/profile text,
country flag lookup, and head/model scale consumers. High-confidence early
anchors now include display name `0x008`, clean/native identity name `0x048`,
country `0x0C8`, team `0x108`, bot skill `0x10C..0x110`, colors
`0x114..0x128`, handicap `0x130`, wins/losses `0x134..0x138`, fixed animation
metadata `0x2E0..0x2F8`, and model handles `0x2FC..0x314`. The source struct is
not forcibly repacked around this early map yet because the current tree keeps
source-compatibility color override, country flag, and scoreboard/team-overlay
fields in that region; moving them should be a deliberate sidecar migration once
the remaining medium-confidence slots are closed.

### Task 118: Clientinfo model-string band and pre-animation scalar reconstruction [COMPLETED]
Parity estimate: **before 97% -> after 98%** for the scoped cgame clientinfo
byte-layout lane. This pass promoted the six 64-byte retail model string slots
from a medium-confidence band to named high-confidence offsets: body model/skin
at `0x154..0x1D3`, icon body model/skin at `0x1D4..0x253`, and head
model/skin at `0x254..0x2D3`. The adjacent pre-animation fields are now pinned
as deferred flag `0x2D4`, model bounding-box scale `0x2D8`, and new-animation
flag `0x2DC`. Source reconstruction now separates `clientInfo_t.modelScale`
from the animation.cfg `headOffset` vector, moves `newAnims` onto the retail
`0x2DC` lane, and keeps focused regression coverage over the Ghidra/HLIL
constructor, load, copy, sound, icon, and tag-flag evidence.

### Task 119: Clientinfo score, compact tinfo, and effect-timer lane closure [COMPLETED]
Parity estimate: **before 98% -> after 99%** for the scoped cgame clientinfo
byte-layout lane. This pass promoted the live score mirror at `0x12C`,
team-task scalar at `0x13C`, medkit timer at `0x144`, and invulnerability
start/stop timers at `0x148..0x14C` using HLIL/Ghidra producer and consumer
evidence. It also documents the remaining `0x150` breath-puff timer candidate
as medium confidence and reconstructs `CG_ParseTeamInfo` to accept the retail
compact `tinfo <count> <client...>` shape while preserving legacy six-field
source-server rows for teammate location, health, armor, weapon, and powerup
compatibility.

### Task 120: Clientinfo animation metadata and render-handle slot closure [COMPLETED]
Parity estimate: **before 99% -> after 99.3%** for the scoped cgame
clientinfo byte-layout lane. This pass split the broad `0x2E0..0x314`
animation metadata/model-handle bands into individually named retail offsets:
`fixedlegs`, `fixedtorso`, `headOffset[3]`, `footsteps`, `gender`, legs/torso/
head model and skin handles, and `modelIcon`. The evidence now ties animation
cfg parsing, model/skin/icon registration, player/model-preview rendering, and
the retail deferred-asset copier together. It also preserves the retail detail
that `CG_CopyClientInfoModel` copies from `0x2E8` onward and intentionally does
not propagate `fixedlegs` or `fixedtorso` during deferred asset reuse.
