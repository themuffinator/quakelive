# Botlib Chat Tail Source Mapping - 2026-06-05

## Scope

This pass selects `src/code/botlib/be_ai_chat.c` as a non-overlapping botlib
section for continued work. It now covers the chat matching helpers, chat
resource loaders, message construction/selection, lifecycle setup/shutdown, and
the tail chat-state export family:

- `UnifyWhiteSpaces`, `StringContains`, and `StringContainsWord`
- `BotFindMatch` and `BotMatchVariable`
- `BotLoadSynonyms`, `BotLoadRandomStrings`, `RandomString`, and
  `BotLoadMatchTemplates`
- `BotLoadReplyChat`, `BotLoadInitialChat`, and `BotLoadChatFile`
- `BotConstructChatMessage`, `BotChooseInitialChatMessage`, and
  `BotNumInitialChats`
- `BotAllocChatState`, `BotFreeChatState`, `BotSetupChatAI`, and
  `BotShutdownChatAI`
- `BotInitialChat` and `BotReplyChat`
- `BotChatLength`, `BotEnterChat`, `BotGetChatMessage`,
  `BotSetChatGender`, and `BotSetChatName`
- related export and qagame/server import wiring

This deliberately avoids the active `l_struct.c` parser/resource-reader lane
from session `019e97e9-ddaa-7e53-81bb-6511a54422c2`, and avoids the dirty
botlib source files already present in this worktree
(`be_aas_entity.c`, `be_aas_main.c`, `be_ai_move.c`, `be_ai_weap.c`, and
`be_interface.c`). The pass is additive only: it creates a focused test file
and this note without editing the shared active-session
`tests/test_botlib_internal_parity.py`.

The second round also avoids making parser-core claims. It references parser
entrypoints such as `LoadSourceFile`, `PC_ExpectTokenString`, and
`BotLoadChatMessage` only as observed call boundaries inside the chat loader
bodies, leaving parser/resource reconstruction to the active session.

No runtime launch was needed. The committed HLIL and Ghidra references expose
the relevant body shapes, diagnostics, native-slot evidence, and compatibility
boundary directly.

## Owning Retail Binary

Owning binary:

- `assets/quakelive/quakelive_steam.exe`

Reference corpus used:

- `references/reverse-engineering/ghidra/quakelive_steam/metadata.txt`
- `references/reverse-engineering/ghidra/quakelive_steam/imports.txt`
- `references/reverse-engineering/ghidra/quakelive_steam/exports.txt`
- `references/reverse-engineering/ghidra/quakelive_steam/functions.csv`
- `references/reverse-engineering/ghidra/quakelive_steam/decompile_top_functions.c`
- `references/reverse-engineering/ghidra/qagamex86/decompile_top_functions.c`
- `references/hlil/quakelive/quakelive_steam.exe/quakelive_steam.exe_hlil_split/quakelive_steam.exe_hlil_part03.txt`
- `references/hlil/quakelive/qagamex86.dll/qagamex86.dll.bndb_hlil.txt`
- `references/analysis/quakelive_symbol_aliases.json`
- `src/code/botlib/be_ai_chat.c`
- `src/code/botlib/be_interface.c`
- `src/code/game/botlib.h`
- `src/code/game/g_public.h`
- `src/code/game/g_syscalls.c`
- `src/code/server/sv_game.c`

## Why This Section

This is a good next botlib section because it is important, bounded, and
comparatively collision-free:

- It gates bot command parsing, reply chat matching, initial chat construction,
  and outbound bot chat commands.
- The engine-owned HLIL has exact function starts and concrete source-shape
  anchors for chat-state message storage at `+0x28`, name storage at `+0x8`,
  client storage at `+0x4`, and the command strings `say %s`,
  `say_team %s`, and `tell %d %s`.
- The qagame corpus gives a clean split between direct native calls for
  `BotEnterChat` / `BotGetChatMessage` and compatibility-only access for
  `BotChatLength` / `StringContains`.
- Existing docs already call this strip less complete than the export table,
  movement, entity, and parser tranches, so this pass improves a real evidence
  seam rather than repeating a closed area.

## Retail Evidence

Observed facts:

- The alias ledger promotes:
  - `sub_497F00 -> UnifyWhiteSpaces`
  - `sub_498020 -> StringContains`
  - `sub_498100 -> StringContainsWord`
  - `sub_4999C0 -> BotFindMatch`
  - `sub_499BF0 -> BotMatchVariable`
  - `sub_498210 -> BotLoadSynonyms`
  - `sub_498DD0 -> BotLoadRandomStrings`
  - `sub_4990D0 -> RandomString`
  - `sub_499580 -> BotLoadMatchTemplates`
  - `sub_49A3A0 -> BotLoadReplyChat`
  - `sub_49A960 -> BotLoadInitialChat`
  - `sub_49AFB0 -> BotLoadChatFile`
  - `sub_49B170 -> BotConstructChatMessage`
  - `sub_49B4D0 -> BotChooseInitialChatMessage`
  - `sub_49B610 -> BotNumInitialChats`
  - `sub_49B6C0 -> BotInitialChat`
  - `sub_49BAE0 -> BotReplyChat`
  - `sub_49C1B0 -> BotChatLength`
  - `sub_49C210 -> BotEnterChat`
  - `sub_49C300 -> BotGetChatMessage`
  - `sub_49C370 -> BotSetChatGender`
  - `sub_49C3D0 -> BotSetChatName`
  - `sub_49C440 -> BotAllocChatState`
  - `sub_49C480 -> BotFreeChatState`
  - `sub_49C560 -> BotSetupChatAI`
  - `sub_49C5F0 -> BotShutdownChatAI`
- The 2026-06-11 Ghidra bridge recheck also promotes matching `FUN_*`
  aliases for the chat corridor entries that have committed Ghidra rows, from
  `FUN_00497b00 -> InitConsoleMessageHeap` through
  `FUN_0049c5f0 -> BotShutdownChatAI`.
- Ghidra `functions.csv` includes raw rows for the two standalone string
  search bodies: `FUN_00498020,00498020,222,0,unknown` and
  `FUN_00498100,00498100,272,0,unknown`.
- Ghidra `functions.csv` also gives stable size rows for the newly mapped
  loader/lifecycle bodies, including:
  `FUN_00498210,00498210,1272,0,unknown`,
  `FUN_00498dd0,00498dd0,742,0,unknown`,
  `FUN_004990d0,004990d0,153,0,unknown`,
  `FUN_00499580,00499580,753,0,unknown`,
  `FUN_0049a3a0,0049a3a0,1438,0,unknown`,
  `FUN_0049a960,0049a960,1487,0,unknown`,
  `FUN_0049afb0,0049afb0,437,0,unknown`,
  `FUN_0049b170,0049b170,858,0,unknown`,
  `FUN_0049b4d0,0049b4d0,307,0,unknown`,
  `FUN_0049b610,0049b610,176,0,unknown`,
  `FUN_0049c480,0049c480,213,0,unknown`,
  `FUN_0049c560,0049c560,144,0,unknown`, and
  `FUN_0049c5f0,0049c5f0,196,0,unknown`.
- `BotAllocChatState` remains a Binary Ninja-only owner in this committed
  evidence set: HLIL shows `0049c440    int32_t sub_49c440()`, but
  `functions.csv` has no `0049c440` row.
- Binary Ninja HLIL for `0x00498020` returns `0xffffffff` for null inputs,
  walks candidate start indices, and uses case-sensitive or `toupper` compare
  behavior matching source `StringContains`.
- Binary Ninja HLIL for `0x00498100` scans word starts and accepts spaces,
  period, comma, and exclamation as word boundaries, matching
  `StringContainsWord`.
- Binary Ninja HLIL for `0x00499BF0` preserves the exact fatal diagnostic
  `BotMatchVariable: variable out of range`.
- Binary Ninja HLIL for `0x0049C1B0` validates the chat-state handle and then
  measures the chat message buffer at state offset `+0x28`.
- Binary Ninja HLIL for `0x0049C210` strips tildes through `sub_497EB0`,
  checks `bot_testichat`, sends `say_team %s`, `tell %d %s`, or `say %s`, and
  clears the message buffer afterward.
- Binary Ninja HLIL for `0x0049C300` strips tildes, copies at most `size - 1`
  bytes from the same `+0x28` message buffer, writes the terminator, then
  clears the source buffer.
- Binary Ninja HLIL for `0x0049C370` maps gender input `1` and `2` to stored
  values and defaults to genderless.
- Binary Ninja HLIL for `0x0049C3D0` stores the bot client at `+0x4`, clears
  the `0x20`-byte name buffer at `+0x8`, copies at most `0x20` bytes, and
  forces the final byte at `+0x27` to zero.
- Binary Ninja HLIL for `0x00498210` (`BotLoadSynonyms`) performs two-pass
  hunk allocation, sets the `botfiles` base folder, reports the retail typo
  `counldn't load %s`, tracks a 32-level context stack, and preserves the
  diagnostics `more than 32 context levels`, `empty string`,
  `synonym must have at least two entries`, `too many }`, and `missing }`.
- Binary Ninja HLIL for `0x00498DD0` (`BotLoadRandomStrings`) follows the same
  two-pass hunk allocation pattern, requires named random groups, reports
  `unknown random %s`, and delegates individual chat-message parsing through
  the chat message loader boundary.
- Binary Ninja HLIL for `0x004990D0` (`RandomString`) walks the global random
  list, string-compares the requested name, computes a random list index through
  `rand() & 0x7fff` scaled by `32767.0`, and returns the selected string or
  null.
- Binary Ninja HLIL for `0x00499580` (`BotLoadMatchTemplates`) sets the
  `botfiles` base folder, requires integer context tokens, calls the match-piece
  loader, then reads `(type, subtype);` for each template.
- Binary Ninja HLIL for `0x0049A3A0` (`BotLoadReplyChat`) requires `[` key
  sets, supports `&`, `!`, `name`, `female`, `male`, `it`, match-piece keys,
  and bot-name lists, stores priorities, loads reply messages, checks developer
  integrity, and prints `no rchats` when the file has none.
- Binary Ninja HLIL for `0x0049A960` (`BotLoadInitialChat`) performs two-pass
  memory sizing/allocation, requires top-level `chat` blocks and nested `type`
  blocks, skips nonmatching chat definitions by brace depth, reports unknown
  definitions, and prints `couldn't find chat %s in %s` when the requested chat
  name is absent.
- Binary Ninja HLIL for `0x0049AFB0` (`BotLoadChatFile`) validates the state
  handle, frees the previous chat file, respects `bot_reloadcharacters`, scans
  the `ichatdata` cache for matching `(chatfile, chatname)`, reports
  `ichatdata table full; couldn't load chat %s from %s`, and caches newly
  loaded initial-chat data when reloading is disabled.
- Binary Ninja HLIL for `0x0049B170` (`BotConstructChatMessage` plus inlined
  expansion loop) writes into the chat-state message buffer at `+0x28`, expands
  `v` variables and `r` random strings, calls the random-string selector,
  reports unknown random strings, applies weighted synonym replacement, and
  warns after ten recursive random expansions.
- Binary Ninja HLIL for `0x0049B4D0` (`BotChooseInitialChatMessage`) walks
  initial-chat types from `chatstate->chat`, filters recently used messages by
  `AAS_Time`, randomly picks an eligible message, and stamps it with
  `AAS_Time() + 20.0`.
- Binary Ninja HLIL for `0x0049B610` (`BotNumInitialChats`) validates the chat
  state handle, walks type records from `chatstate->chat`, checks
  `bot_testichat`, prints the type count and separator in debug mode, and
  returns the type's message count.
- Binary Ninja HLIL for `0x0049C440` allocates chat-state handles from `1`
  through `0x40` and clears `0x13c` bytes for each state.
- Binary Ninja HLIL for `0x0049C480` validates/free a chat state, conditionally
  frees the initial-chat file when `bot_reloadcharacters` is active, drains
  console messages through the console-message heap helpers, frees the state,
  and zeroes the state slot.
- Binary Ninja HLIL for `0x0049C560` loads `synfile`/`rndfile`/`matchfile`,
  gates reply-chat loading behind `nochat`, loads `rchatfile` only when chat is
  enabled, then initializes the console-message heap.
- Binary Ninja HLIL for `0x0049C5F0` frees remaining live chat states, cached
  `ichatdata` entries, the console-message heap, match templates, random
  strings, synonyms, and reply chats, nulling each global after release.
- The qagame HLIL and Ghidra companion corpus repeatedly call direct import
  offset `+0x1fc` for `BotEnterChat` and `+0x200` for `BotGetChatMessage`.
- The same qagame corpora do not show direct import calls through
  `data_104b13ac + 0x1f8` or `+0x204`, supporting the current compatibility
  boundary for `BotChatLength` and `StringContains`.

## Source Confirmation

The checked-in source matches the recovered retail shape:

- `UnifyWhiteSpaces` compresses whitespace runs to one space only when not at
  the start or end, and removes other whitespace bytes through `memmove`.
- `StringContains` returns `-1` for null input, computes
  `strlen(str1) - strlen(str2)`, and compares each candidate position with
  `toupper` when not case-sensitive.
- `StringContainsWord` scans to word starts and treats space, `.`, `,`, and
  `!` as delimiters in the same high-level shape visible in HLIL.
- `BotFindMatch` copies into `match->string`, removes trailing newlines,
  checks context masks, resets every match-variable offset to `-1`, and writes
  matched type/subtype.
- `BotMatchVariable` emits the retail fatal diagnostic for invalid variable
  indices, bounds the copied variable slice by `size`, and writes an empty
  string for absent variables.
- `BotLoadSynonyms` matches the retail two-pass parser/allocation pattern and
  context stack diagnostics without making new parser-core assumptions.
- `BotLoadRandomStrings`, `RandomString`, and `BotLoadMatchTemplates` preserve
  the retail `botfiles` base-folder usage, diagnostics, random-index behavior,
  and match-template `(type, subtype);` layout.
- `BotLoadReplyChat`, `BotLoadInitialChat`, and `BotLoadChatFile` match the
  retail key-set parser, initial-chat two-pass loader, and `ichatdata` cache
  boundary guarded by `bot_reloadcharacters`.
- `BotConstructChatMessage` matches the retail `+0x28` output buffer target,
  variable/random expansion cases, weighted-synonym pass, and ten-expansion
  warning behavior.
- `BotChooseInitialChatMessage` and `BotNumInitialChats` match retail recent-use
  filtering, `bot_testichat` diagnostics, and message-count behavior.
- `BotAllocChatState`, `BotFreeChatState`, `BotSetupChatAI`, and
  `BotShutdownChatAI` match retail handle range, `0x13c` state allocation,
  console-message heap interaction, cvar/file defaults, and global release
  order.
- `BotChatLength`, `BotEnterChat`, `BotGetChatMessage`, `BotSetChatGender`,
  and `BotSetChatName` match the retail tail-body behavior described above.
- `be_interface.c::Init_AI_Export` exposes the full chat family on the AI
  export table in the source order expected by `botlib.h`.
- `g_syscalls.c::G_MapNativeImport` intentionally maps the directly observed
  qagame native calls (`BotEnterChat`, `BotGetChatMessage`, `BotFindMatch`,
  `BotMatchVariable`, `UnifyWhiteSpaces`, `BotSetChatGender`, and
  `BotSetChatName`) while leaving `BotChatLength` and `StringContains` to the
  compatibility slab.
- `sv_game.c` still fills compatibility slots for all retained legacy chat
  syscalls, including `BotChatLength` and `StringContains`.

## Changes

- Added `tests/test_botlib_chat_parity.py`, a standalone guard that pins:
  - chat tail aliases and HLIL body anchors,
  - string/match helper source shape and diagnostics,
  - chat resource loader aliases, Ghidra size rows, and HLIL parser-boundary
    anchors,
  - message construction, initial-chat selection/counting, and chat AI
    lifecycle setup/shutdown anchors,
  - export-table source wiring,
  - direct native import slots for the qagame-proven chat bridge, and
  - compatibility-only treatment for `BotChatLength` and `StringContains`.
- The 2026-06-11 bridge recheck added a central alias-row gate for the full
  chat corridor, proving each promoted Ghidra `FUN_*` alias matches the
  Binary Ninja `sub_*` owner and preserving the no-row boundary for
  `BotAllocChatState`.
- Added this mapping note as the selected non-overlapping forward botlib
  section.
- No C source body change was needed.

## Follow-On Work

Good next slices inside this same section:

- Keep `BotAllocChatState` as a no-Ghidra-row exception unless a refreshed
  committed Ghidra export produces a stable `0049c440` function row.
- Add a tiny native harness for `StringContains`, `StringContainsWord`, and
  `UnifyWhiteSpaces`, if future source changes touch bot command matching.
- Deepen `BotReplyChat` scoring and key-evaluation coverage by naming the main
  qagame callers that populate reply message/context arguments.
- A qagame-side pass that names the main `DAT_104b13ac + 0x1fc` and
  `+0x200` callers around `BotChat_EnterGame`, command replies, and timed chat
  flows.

## Validation

Targeted validation for this pass:

- `python -m pytest tests/test_botlib_chat_parity.py -q`
- `python -m pytest tests/test_botlib_chat_parity.py tests/test_bot_resource_loading.py -q`

No game launch was performed. Static source, HLIL, Ghidra, and pytest coverage
fully answer this mapping question.

## Parity Estimate

- Focused `be_ai_chat.c` chat tail and matching-helper mapping:
  `70% -> 93%`. Before this round, aliases existed and the console-message
  sub-slice was pinned, but the tail-body shapes, loader/cache bodies,
  construction/selection/lifecycle bodies, and native-vs-compat import boundary
  were not covered by a dedicated guard.
- Focused qagame bot-AI chat bridge evidence: `96% -> 97%`; this pass confirms
  the compatibility-only gap is intentional for `BotChatLength` and
  `StringContains`, rather than an uninspected source omission.
- Overall botlib plus related wiring: approximately `74% -> 76%`.
- Strict-retail Windows replacement target: unchanged at `100%`; this pass
  reduces future botlib-chat uncertainty rather than changing an active gate.
