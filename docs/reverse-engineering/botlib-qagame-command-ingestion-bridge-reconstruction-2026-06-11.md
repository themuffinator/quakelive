# Botlib Qagame Command Ingestion Bridge Reconstruction - 2026-06-11

## Scope

This pass rechecked the qagame bot command loop and outgoing bot usercmd bridge:

- inbound server-command drain through `trap_BotGetServerCommand`;
- `BotAI` command parsing for `cp`, `cs`, `print`, `chat`, `tchat`,
  `vchat`, `vtchat`, `vtell`, `scores`, and `clientLevelShot`;
- `RemoveColorEscapeSequences`;
- `BotUpdateInput -> BotInputToUserCommand`;
- `BotAIStartFrame -> trap_BotUserCommand`;
- native/legacy host wrappers for `BOTLIB_GET_CONSOLE_MESSAGE` and
  `BOTLIB_USER_COMMAND`.

This is a qagame-and-wiring reconstruction pass. It does not reopen the
botlib core residual-address pocket, which remains closed as mapping-only for
the documented libjpeg false leads and folded thunks.

## Retail Evidence

Observed qagame Binary Ninja HLIL anchors:

- `10021F90` is `RemoveColorEscapeSequences`. It skips Quake color escapes
  beginning with `^`, copies only bytes `<= 0x7e`, and terminates the compacted
  string.
- `10021FE0` is `BotAI`. It resets EA input through import offset `0x1b4`,
  loads the bot state, copies the current client snapshot into the bot state
  when available, then drains server commands through import offset `0xec`.
- `BotAI` splits each command at the first space, calls
  `RemoveColorEscapeSequences` on the argument tail, and then compares command
  tokens in retail order: `"cp "`, `"cs"`, `"print"`, `"chat"`, `"tchat"`,
  `"vchat"`, `"vtchat"`, and `"vtell"`.
- The `"cp "` comparison includes the trailing space even though the source
  token was already split at the first space. This is retained as retail
  behavior, not corrected as a style cleanup.
- The `"chat"` branch strips the surrounding quotes, then if the resulting
  message starts with two decimal digits followed by a space, advances the
  queued pointer by three bytes before queuing `CMS_CHAT`.
- The `"tchat"` branch strips quotes and queues `CMS_CHAT` without the
  two-digit sender-prefix skip.
- The voice command branches call `BotVoiceChatCommand` with modes `0`, `1`,
  and `2` for `vchat`, `vtchat`, and `vtell`.
- `10021E10` is `BotUpdateInput`. It calls the EA get-input import at offset
  `0x1b0`, applies the respawn-filtering path, then calls
  `BotInputToUserCommand`.
- `10023400` calls `BotAI` in the scheduled think loop, later calls
  `BotUpdateInput`, then sends `lastucmd` with the user-command import.

Observed host Binary Ninja HLIL anchors:

- `004E17F0` tail-calls `SV_BotGetConsoleMessage`.
- `004E1800` forwards bot usercmds to the `SV_ClientThink` owner through the
  client stride.
- `004E1E20` jumps through `data_13e1844 + 0xec`, matching the qagame
  `trap_BotGetServerCommand` import slot.

Observed Ghidra/function-row anchors:

- `FUN_10021e10,10021e10,372,0,unknown`
- `FUN_10021f90,10021f90,70,0,unknown`
- `FUN_10021fe0,10021fe0,1187,0,unknown`
- `FUN_1002c7d0,1002c7d0,379,0,unknown`
- `FUN_10023400,10023400,2038,0,unknown`
- `FUN_004e17f0,004e17f0,9,0,unknown`
- `FUN_004e1800,004e1800,33,0,unknown`

Symbol alias anchors:

- `FUN_10021e10` / `sub_10021e10 -> BotUpdateInput`
- `FUN_10021f90` / `sub_10021f90 -> RemoveColorEscapeSequences`
- `FUN_10021fe0` / `sub_10021fe0 -> BotAI`
- `FUN_1002c7d0` / `sub_1002c7d0 -> BotVoiceChatCommand`
- `sub_4E17F0 -> QL_G_trap_BotGetServerCommand`
- `sub_4E1800 -> QL_G_trap_BotUserCommand`

## Source Reconstruction

Changed `BotAI` in `src/code/game/ai_main.c` so the normal `chat` branch now
matches retail after quote stripping:

- if the queued chat text begins with two ASCII digits and a space, `args`
  advances by three bytes before `trap_BotQueueConsoleMessage(bs->cs,
  CMS_CHAT, args)`;
- `tchat` remains unchanged and does not strip this sender prefix;
- the existing `"cp "` comparison is intentionally preserved because the
  retail HLIL compares the split command token against the trailing-space
  literal.

The VM/native wiring already matched the retail shape:

- `BOTLIB_GET_CONSOLE_MESSAGE -> G_QL_IMPORT_BOTLIB_GET_CONSOLE_MESSAGE = 59`;
- `BOTLIB_USER_COMMAND -> G_QL_IMPORT_BOTLIB_USER_COMMAND = 60`;
- qagame syscall wrappers call `BOTLIB_GET_CONSOLE_MESSAGE` and
  `BOTLIB_USER_COMMAND`;
- legacy `sv_game.c` dispatch uses `SV_BotGetConsoleMessage` and
  `SV_ClientThink`;
- native `ql_game_imports` maps to `QL_G_trap_BotGetServerCommand` and
  `QL_G_trap_BotUserCommand`.

## Validation

Added `tests/test_botlib_qagame_command_ingestion_parity.py`, which pins:

- qagame and host aliases/function-row sizes;
- `BotAI` command-token order and the retained retail `"cp "` comparison;
- the reconstructed `chat` two-digit sender-prefix strip;
- `tchat` as a separate no-prefix-strip path;
- voice command modes;
- `BotUpdateInput`, `BotAIStartFrame`, and host usercmd dispatch wiring;
- qagame and host HLIL anchors for the behavior.

Initial focused run:

```powershell
python -m pytest tests/test_botlib_qagame_command_ingestion_parity.py -q --tb=short
```

Result: `3 passed in 0.18s`.

No game launch was needed. The change is covered by static source and committed
retail reference evidence.

## Open Boundaries

- This does not emulate live chat traffic. It reconstructs the retail parser
  behavior and pins the qagame/host wiring.
- The retail `cp ` comparison remains intentionally odd; changing it to
  `"cp"` would diverge from observed retail HLIL.
- The broader command-response logic in `ai_cmd.c` remains covered by the
  existing team/voice command parity tests and was not modified here.

## Parity Estimate

- Focused qagame `BotAI` command-ingestion confidence:
  **before 88% -> after 98%**.
- Focused bot usercmd output bridge confidence: **before 94% -> after 98%**.
- Overall botlib plus qagame/server wiring reconstruction parity:
  **83.35% -> 83.5%**.
