# Botlib Native Import Compatibility Bridge Recheck - 2026-06-05

## Scope

This pass rechecked the qagame native import wiring that sits between the
retail Quake Live DLL import slab and the retained Quake III botlib syscall
IDs. It complements the already-closed server `SV_BotInitBotLib` import table
and the generated botlib wrappers from mapping rounds `61` and `64`.

The reconstruction result is a source correction in `G_MapNativeImport` and the
host import table: retained botlib IDs that already have recovered Quake Live
native slots now map directly to those slots instead of falling through to the
compatibility slab. This pass also corrects the AAS native slot quartet exposed
through qagame callers and promotes the high-confidence direct bot-AI
debug-visualization, characteristic, goal-state, fuzzy-logic, and movement-state
resource slots.

## Retail Evidence

- `references/hlil/quakelive/qagamex86.dll/qagamex86.dll.bndb_hlil.txt`
  repeatedly calls through `data_104b13ac + offset`, proving that native
  qagame uses a direct import pointer slab rather than the QVM syscall path.
- The qagame HLIL obstacle-prediction caller uses
  `(*(data_104b13ac + 0x13c))(..., 0x64, 0x3e8, 6, 0x400, 0x4000000, 0)`,
  which lines up with `BOTLIB_AAS_PREDICT_ROUTE` and the recovered native slot
  `G_QL_IMPORT_BOTLIB_AAS_PREDICT_ROUTE = 79`.
- The same qagame corpus pins the following direct AAS quartet:
  `+0x13c` / slot `79` for `AAS_PredictRoute`, `+0x140` / slot `80` for
  `AAS_AlternativeRouteGoals`, `+0x144` / slot `81` for `AAS_Swimming`, and
  `+0x148` / slot `82` for `AAS_PredictClientMovement`.
- `BotTestAAS` (`sub_10020f00`) then immediately calls two botlib debug
  visualization slots: `data_104b13ac + 0x14c` / slot `83` with
  `(origin, bot_showAreas.integer, bot_showAreaNumber.integer)`, and
  `data_104b13ac + 0x150` / slot `84` with the selected bot state's movement
  handle (`bs->ms`, observed as `eax_7[0x657]`).
- The same retail block reads `bot_showAvoidSpots` from the qagame cvar table
  and resets it through the native `Cvar_Set` slot when the selected bot state
  is absent. Split HLIL table entries also identify `bot_showAreaNumber`,
  `bot_showAreas`, and `bot_showAvoidSpots`.
- The Ghidra qagame companion corpus contains repeated `DAT_104b13ac + offset`
  calls around movement, chat, action, and goal helpers, confirming that the
  import slab is broad and not limited to the small server setup wrapper set.
- Ghidra qagame `BotAIStartFrame` uses `DAT_104b13ac + 0xd8` for
  `BotLibStartFrame` and `DAT_104b13ac + 0xe0` for `BotLibUpdateEntity`,
  matching native slots `54` and `56`.
- The qagame HLIL and Ghidra corpora also repeatedly call direct bot-AI import
  offsets: `+0x1b8/+0x1bc` for character load/free,
  `+0x1c4/+0x1cc/+0x1d0` for characteristic bounded-float/bounded-integer/string
  reads, `+0x1e0` for `BotRemoveConsoleMessage`, `+0x1f4` for
  `BotReplyChat`, `+0x1fc` for `BotEnterChat`, `+0x200` for
  `BotGetChatMessage`, `+0x228/+0x22c` for remove/reset avoid goals,
  `+0x238/+0x240` for goal-stack diagnostics, `+0x27c` for item-weight loads,
  `+0x284/+0x288/+0x28c` for fuzzy-logic interbreed/save/mutate,
  `+0x290/+0x294` for goal-state allocation/free, `+0x2b4` for
  `BotPredictVisiblePosition` in the `BotAimAtEnemy` aiming path, and
  local-table `+0x2b8/+0x2bc` for move-state allocation/free.
- The EA import band is pinned by qagame HLIL calls at offsets `+0x154`
  through `+0x1b4`. Representative calls identify `+0x158` as team chat
  (`"what do you say?"`, `"I'm the team leader\n"`), `+0x15c` as command
  (`"vtaunt"`, `"kill"`, tutorial `say` strings), `+0x160` as action flags,
  `+0x164` as the retail-only `EA_Walk`, `+0x198` as weapon select, `+0x1a8`
  as view angles, and `+0x1b0/+0x1b4` as input fetch/reset.
- Ghidra qagame cross-checks the same EA tranche in tutorial and bot-action
  blocks, including `DAT_104b13ac + 0x164` for walk, `+0x198` for weapon
  select, `+0x1a8` for view, and `+0x1b4` for input reset.
- The bot-AI movement export table in retail `quakelive_steam.exe` assigns
  `arg1[0x39] = sub_4a4a50`, `arg1[0x3a] = sub_4a17f0`,
  `arg1[0x3d] = sub_49fed0`, `arg1[0x3e] = sub_4a0cd0`, and
  `arg1[0x3f] = sub_4a0f70`, matching `BotMoveToGoal`,
  `BotMoveInDirection`, `BotReachabilityArea`, `BotMovementViewTarget`, and
  `BotPredictVisiblePosition`.
- The same retail export table now has alias coverage for the broader AI band:
  character accessors (`sub_497590`, `sub_496a80`, `sub_497780`...
  `sub_4979e0`), chat/console helpers (`sub_497cb0`, `sub_497bd0`,
  `sub_497de0`, `sub_497e60`, `sub_49bae0`), goal and item-weight helpers
  (`sub_49f680` through `sub_49f840`), and weapon-state helpers
  (`sub_4a6190`, `sub_4a6100`, `sub_4a6060`, `sub_4a62a0`, `sub_4a62d0`,
  `sub_4a6260`).
- Retail chat-console helper bodies are now pinned directly: queueing uses a
  `0x114`-byte console-message node, wraps handles above `0x2000`, copies the
  payload with `strncpy(..., 0x100)`, appends at the chat state's tail, and
  increments the `+0x134` count. `BotNextConsoleMessage` copies the full
  `0x114` node and then clears the copied link fields at `arg2[0x43]` and
  `arg2[0x44]`.
- AAS internal mapping advanced across the clustering and debug corridor:
  `AAS_UpdatePortal`, `AAS_FloodClusterAreas_r`, `AAS_FindClusters`,
  `AAS_CreatePortals`, the view/forced portal helpers, `AAS_Error`,
  `AAS_Loaded`, `AAS_ProjectPointOntoVector`, and the shown polygon/debug-line
  helpers now have alias coverage. This tranche intentionally does not invent
  a standalone `AAS_SetInitialized`; retail `AAS_ContinueInit` writes the
  initialized flag directly.
- Parser and script-reader mapping advanced across `l_precomp.c`,
  `l_script.c`, and `l_struct.c`: source warning/error helpers, source-token
  stack helpers, define hash/copy/free/expand helpers, directive readers,
  script string/name/primitive/token readers, quote strippers, script load/free
  helpers, and `FindField` now have alias coverage against BN HLIL starts and
  Ghidra `functions.csv` rows.
- Movement avoid-spot handling is also pinned in the engine HLIL:
  `sub_4a0770` is `BotAvoidSpots`, using the travel-type switch to decide
  between endpoint and segment checks and returning immediately on
  `AVOID_ALWAYS`; `sub_4a0990` is `BotAddAvoidSpot`, clearing count at
  `+0x300` for `AVOID_CLEAR`, capping at `0x20`, storing origin/radius/type
  at the `0x80 + index * 0x14` avoid-spot array, then incrementing the count.
- A follow-up internal mapping tranche promoted the AAS lifecycle and
  setup/shutdown helpers around `Export_BotLibSetup`,
  `Export_BotLibShutdown`, and `Export_BotLibLoadMap`: `AAS_Setup`,
  `EA_Setup`, `BotSetupGoalAI`, `BotSetupMoveAI`, `BotShutdownMoveAI`,
  `BotShutdownGoalAI`, `BotShutdownWeights`, `BotShutdownCharacters`,
  `AAS_LoadMap`, `BotInitLevelItems`, and `BotSetBrushModelTypes` now have
  alias and HLIL-order coverage.
- The related qagame native import tail is now split by ABI parity and
  configstring ownership. Slot `202` / offset `+0x328` calls a GUID generator
  before retail qagame sets configstring `0x2c8` as `MATCH_GUID`; source now
  promotes it as `G_QL_IMPORT_GENERATE_MATCH_GUID` / `SV_GenerateMatchGuid`
  and uses it to seed `level.rankMatchGuid` before publishing `CS_MATCH_GUID`
  on retail configstring `0x2c8`. The source-side warmup-ready snapshot moved
  to extension slot `0x2d1`, keeping the earlier readiness plumbing without
  colliding with the retail match GUID lane. Slot `206` / offset `+0x338` is promoted: qagame calls it
  with the callvote factory token before the exact `"Factory does not exist.\n"`
  rejection, and the host table binds `data_56d2b8` to `sub_4e2a20`, a boolean
  wrapper over `Factory_FindById`.
- Four remaining goal-table holes are now promoted by export-table order and
  neighboring proven slots: `BotGetMapLocationGoal` at slot `153`,
  `BotAvoidGoalTime` at slot `155`, `BotInitLevelItems` at slot `157`, and
  `BotFreeItemWeights` at slot `160`. This pass did not find direct qagame
  calls for those four offsets.
- The native chat strip keeps the true gaps visible: `BotChatLength` remains at
  the unpromoted slot `126` and `StringContains` at `129`, while direct qagame
  use proves `BotEnterChat` at `127` and `BotGetChatMessage` at `128`.
  Negative qagame checks also found no direct
  `DAT_104b13ac + 0x1f8` / `+0x204` import calls.
- Host mapping round `64` already promoted the generated named wrappers for
  `BOTLIB_SETUP`, `BOTLIB_SHUTDOWN`, libvars, start frame, load map, update
  entity, botlib test, snapshot entity, console message, and user command.

## Source Confirmation

- `src/code/game/g_public.h` keeps the recovered native botlib slot numbers for
  the named retail slab: `G_QL_IMPORT_BOTLIB_SETUP = 49`, `..._LIBVAR_GET = 52`,
  `..._AAS_TIME = 66`, `..._AAS_PREDICT_ROUTE = 79`,
  `..._AAS_PREDICT_CLIENT_MOVEMENT = 82`,
  `..._AI_DRAW_DEBUG_AREAS = 83`, `..._AI_DRAW_AVOID_SPOTS = 84`, the EA band
  from `..._EA_SAY = 85` through `..._EA_RESET_INPUT = 109`, and the recovered
  bot-AI slots through
  `..._GENETIC_PARENTS_AND_CHILD_SELECTION = 184`.
- `src/code/game/g_syscalls.c::G_MapNativeImport` explicitly maps the named
  retail botlib slots and falls back to
  `G_QL_IMPORT_COMPAT_BASE + arg` for valid legacy IDs.
- The direct mapper now includes `BOTLIB_LIBVAR_GET`,
  `BOTLIB_START_FRAME`, `BOTLIB_UPDATENTITY`, `BOTLIB_TEST`, and the direct AAS
  quartet from `BOTLIB_AAS_PREDICT_ROUTE` through
  `BOTLIB_AAS_PREDICT_CLIENT_MOVEMENT`, aligning the source-built native
  qagame path with the named slots already published by the host.
- The mapper now also includes the retail-visible bot-AI direct slot band for
  debug visualization, character load/free, characteristic
  float/bfloat/integer/binteger/string, console-message removal, reply chat,
  enter chat, get chat message, remove/reset avoid goals, empty/dump
  goal-stack helpers, item weights, goal
  fuzzy-logic interbreed/save/mutate, goal-state allocation/free, reset move
  state, visible-position prediction, and move-state allocation/free.
- The mapper now promotes the legacy EA IDs that have a retail native slot:
  `BOTLIB_EA_SAY` through `BOTLIB_EA_RESET_INPUT`. `EA_Walk` is wired only as a
  native host import because there is no retained legacy qagame syscall ID for
  that Quake Live-only action.
- `BotReachabilityArea` is filled at native slot `171`, between
  `BotResetLastAvoidReach` and `BotMovementViewTarget`, based on the engine
  export table and `botlib.h`/`be_interface.c` export order. No direct qagame
  call to `data_104b13ac + 0x2ac` was observed in this pass.
- `src/code/game/ai_main.c::BotTestAAS` now mirrors the retail debug pass before
  its old solid/cluster checks: update the AAS debug cvars, draw nearby debug
  areas through slot `83`, draw selected-bot avoid spots through slot `84`, and
  clear `bot_showAvoidSpots` when the selected bot state is invalid.
- `src/code/server/sv_game.c::SV_InitGameImports` fills both sides:
  named `G_QL_IMPORT_BOTLIB_*` slots first, then copies
  `ql_game_compat_imports` into the compatibility slab.
- `src/code/server/ql_game_imports.inc` preserves legacy compatibility wrappers
  while also providing the direct-only `QL_G_trap_EA_Walk` native wrapper.
  A later 2026-06-06 slab pass recovered `BOTLIB_AI_CHAT_LENGTH` and
  `BOTLIB_AI_STRING_CONTAINS` as direct native slots 126 and 129; the remaining
  compatibility-only botlib IDs are parser helpers like
  `BOTLIB_PC_LOAD_SOURCE`, `BOTLIB_PC_FREE_SOURCE`,
  `BOTLIB_PC_READ_TOKEN`, and `BOTLIB_PC_SOURCE_FILE_AND_LINE`.

## Changes

- Extended `tests/test_game_native_export_helper_parity.py` so the native import
  table guard now checks:
  - public header count and compatibility-base math,
  - explicit named retail botlib imports,
  - direct AAS and bot-AI slot promotion,
  - direct chat bridge promotion for `BotRemoveConsoleMessage` at slot `120`
    and `BotReplyChat` at slot `125`,
  - direct EA band promotion from slots `85` through `109`,
  - direct-only `EA_Walk` host wiring,
  - `BotTestAAS` debug-area and avoid-spot wiring at native slots `83` and
    `84`,
  - compatibility-only botlib/AI/parser IDs,
  - `G_MapNativeImport` direct-vs-fallback behavior,
  - server compatibility-slab population,
  - Ghidra/HLIL qagame direct import offsets for botlib frame, AAS,
    characteristic, avoid-goal, character, goal-state, fuzzy-logic,
    visible-position, and movement-state calls,
  - representative generated wrapper float packing/unpacking.
- Reconstructed the missing direct mappings in
  `src/code/game/g_syscalls.c::G_MapNativeImport`, corrected the direct AAS
  quartet slot order, added the recovered bot-AI native slot constants in
  `src/code/game/g_public.h`, and filled the matching host functions in
  `src/code/server/sv_game.c`.
- Promoted `BOTLIB_AI_PREDICT_VISIBLE_POSITION` to the recovered native slot
  `G_QL_IMPORT_BOTLIB_AI_PREDICT_VISIBLE_POSITION = 173`, matching the retail
  `DAT_104b13ac + 0x2b4` / `data_104b13ac + 0x2b4` evidence.
- Promoted the qagame EA native band to slots `85..109` and filled
  `BotReachabilityArea` at slot `171`.
- Promoted `BOTLIB_AI_REMOVE_CONSOLE_MESSAGE` to native slot `120` and
  `BOTLIB_AI_REPLY_CHAT` to native slot `125`, based on direct qagame import
  calls at `DAT_104b13ac + 0x1e0` and `DAT_104b13ac + 500` / `0x1f4`.
- Pinned the already-wired direct chat continuation:
  `BOTLIB_AI_ENTER_CHAT` at native slot `127` and
  `BOTLIB_AI_GET_CHAT_MESSAGE` at native slot `128`, with Ghidra qagame calls
  at `DAT_104b13ac + 0x1fc` and `DAT_104b13ac + 0x200`.
- Rechecked the remaining compatibility-served chat/parser IDs and added
  negative parity guards: no qagame direct import calls were found for
  `BotChatLength` / native hole `126` (`+0x1f8`), `StringContains` / native
  hole `129` (`+0x204`), or the parser helper wrappers.
- Promoted flanked goal-table holes for `BotGetMapLocationGoal`, `BotAvoidGoalTime`,
  `BotInitLevelItems`, and `BotFreeItemWeights` to slots `153`, `155`, `157`,
  and `160`.
- Reconstructed the small retail weapon-state source shape in
  `src/code/botlib/be_ai_weap.c`: `BotValidWeaponNumber` now prints
  `weapon number (%d) out of range\n`, `BotGetWeaponInfo` follows the retail
  validation-then-copy path without the dead post-handle `weaponconfig` guard,
  and `BotResetWeaponState` is validation-only like `sub_4a6260`.
- Added source-shape parity guards for `BotRemoveConsoleMessage`,
  `BotQueueConsoleMessage`, `BotNextConsoleMessage`, `BotNumConsoleMessages`,
  `BotAvoidSpots`, and `BotAddAvoidSpot`, tying the current C source to the
  retail HLIL node sizes, link clearing, handle wrapping, travel-type switch,
  and avoid-spot storage offsets.
- Expanded the `quakelive_steam` alias ledger beyond the AI export table:
  AAS export helpers, the EA export band, `Init_AAS_Export`,
  `Init_EA_Export`, `GetBotLibAPI`, top-level `Export_BotLib*` helpers, and
  parser-handle helpers now have explicit aliases. Shared no-op helpers
  `sub_4d7980` and `sub_4d7970` remain assignment-only and intentionally
  unaliased.
- Expanded that alias ledger again for internal AAS lifecycle, EA setup,
  bot-AI setup/shutdown, movement brush-model setup, weight/character
  shutdown, precompiler source loading/freeing, and precompiler global-define
  cleanup helpers. Tests now assert the retail setup/shutdown/load-map
  sequencing and the previously underasserted parser export slots
  `data_16dda6c = sub_4acb10` and `data_16dda70 = sub_4ac390`.
- Added server import-table guards for retail `SV_BotInitBotLib`: the BSP
  entity data assignment uses the `CM_EntityString` tailcall thunk
  `j_sub_4c0250`, and both debug line deletion and debug polygon deletion use
  `sub_4dd430` in the retail import table.
- Corrected the symbol aliases for the movement-tail helpers:
  `sub_49FC30` is `BotFuzzyPointReachabilityArea`, `sub_49FED0` is
  `BotReachabilityArea`, `sub_4A17F0` is `BotMoveInDirection`, and
  `sub_4A0F70` is `BotPredictVisiblePosition`.
- Added high-confidence AI export-table aliases for character, chat/console,
  goal, item-weight, weapon-state, and remaining movement/debug helpers.
- Added direct qagame wrappers for the retail-only debug visualization imports,
  host wrappers that call `botlib_export->ai.BotDrawDebugAreas` and
  `BotDrawAvoidSpots`, and qagame-side cvar registration for
  `bot_showAreaNumber`, `bot_showAreas`, and `bot_showAvoidSpots`.

## Open Questions

- The remaining compatibility-only IDs should not be promoted to named
  `G_QL_IMPORT_BOTLIB_*` slots unless a future retail reference proves a
  standalone native slot. The current source intentionally keeps them reachable
  through the compatibility slab.
- `BotReachabilityArea` is high-confidence by retail engine export order, but
  it remains an open qagame-use question because this pass did not find a direct
  `+0x2ac` qagame import call.
- `BotChatLength`, `StringContains`, and parser helpers remain
  compatibility-served until direct qagame native import evidence is found.
- The related slot `202` GUID generator is now wired through
  `G_QL_IMPORT_GENERATE_MATCH_GUID` with a 0x40 qagame buffer. The related
  configstring lane is now wired too: retail `0x2c8` is `CS_MATCH_GUID`, while
  `CS_WARMUP_READY` remains available on source-extension slot `0x2d1`.
- Related slot `206` / `SV_FactoryExists` now has the narrow source boundary
  requested by the evidence: `SV_FactoryExists` wraps the server-owned factory
  registry, `QL_G_trap_FactoryExists` fills `G_QL_IMPORT_FACTORY_EXISTS`, and
  native qagame callvote validation checks `trap_FactoryExists` before the
  existing local `Factory_FindById` lookup used for `baseGametype`.
- This pass did not attempt a full per-call qagame import-offset atlas. It pins
  the boundary that prevents old botlib syscall IDs from drifting while future
  qagame AI mapping rounds continue to name individual callers.

## Parity Estimate

- Focused qagame botlib native import compatibility bridge:
  `68% -> 99%`. The main source gaps were the named botlib wrappers that were
  still taking the compatibility fallback path, the direct AAS quartet order
  that still had `AAS_PredictClientMovement` and `AAS_PredictRoute` swapped,
  the qagame EA native band, and a band of retail-visible bot-AI resource slots
  still routed through the compatibility slab.
- Focused qagame EA native import wiring: `40% -> 95%`.
- Focused qagame bot-AI native slot wiring: `60% -> 94%`.
- Focused qagame bot-AI chat native bridge: `82% -> 90%`.
- Focused qagame bot-AI chat native bridge evidence after this recheck:
  `90% -> 96%`.
- Focused qagame bot-AI goal native bridge: `92% -> 97%`.
- Focused botlib AI export-table alias coverage: `72% -> 88%`.
- Focused botlib AAS/EA/top-level export alias coverage: `61% -> 96%`.
- Focused botlib weapon-state source-shape lane: `88% -> 91%`.
- Focused botlib chat console-message source-shape lane: `80% -> 93%`.
- Focused botlib avoid-spot source-shape lane: `80% -> 93%`.
- Focused botlib internal lifecycle/parser alias coverage: `96% -> 98%`.
- Focused AAS internal clustering/debug mapping confidence: `88% -> 92%`.
- Focused parser/precompiler internal mapping confidence: `55% -> 85%`.
- Related qagame native import-table evidence outside the botlib band:
  `99% -> 100%`, with factory-existence, GUID source wiring, and the related
  retail `0x2c8` `CS_MATCH_GUID` configstring ownership now promoted.
- Focused qagame `BotPredictVisiblePosition` native-slot wiring:
  `55% -> 96%`.
- Focused qagame botlib debug visualization wiring: `35% -> 92%`.
- Overall botlib plus related wiring: approximately `73% -> 74%`.
