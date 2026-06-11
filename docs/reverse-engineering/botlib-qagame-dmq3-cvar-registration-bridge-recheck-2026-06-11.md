# Botlib qagame DMQ3 cvar registration bridge recheck - 2026-06-11

## Scope

This pass rechecked the `BotSetupDeathmatchAI` setup lane in qagame against
the retail Quake Live Binary Ninja HLIL and the committed Ghidra companion
corpus. The target was the DMQ3 bot cvar registration sequence that wires
deathmatch bot movement, chat, challenge, obstacle-prediction, and single-player
skill controls before gametype-specific flag and obelisk goal setup.

## Retail evidence

Observed Binary Ninja HLIL evidence in
`references/hlil/quakelive/qagamex86.dll/qagamex86.dll.bndb_hlil_split/qagamex86.dll.bndb_hlil_part01.txt`:

- `sub_1001f580` reads `g_gametype` and `sv_maxclients` through the qagame
  cvar integer-value import before registering bot setup cvars.
- The retail registration order is `bot_rocketjump`, `bot_grapple`,
  `bot_fastchat`, `bot_nochat`, `bot_testrchat`, `bot_challenge`,
  `bot_predictobstacles`, then `g_spSkill`.
- `bot_rocketjump`, `bot_grapple`, and `bot_predictobstacles` use default `1`
  with flags `0`.
- `bot_fastchat` and `bot_testrchat` use default `0` with flags `0`.
- `bot_nochat` and `bot_challenge` use default `0` with flags `0x80000`,
  matching this tree's `CVAR_CLOUD`.
- `g_spSkill` uses default `2` with flags `0`.

Observed Ghidra companion evidence in
`references/reverse-engineering/ghidra/qagamex86/decompile_top_functions.c`:

- `FUN_1001f580` repeats the same eight `Cvar_Register` calls, defaults, flags,
  and order.
- The same setup block transitions immediately into CTF and Harvester goal
  discovery, supporting the source ownership boundary for this sequence.

## Source reconstruction status

`src/code/game/ai_dmq3.c` already reconstructs this retail lane in
`BotSetupDeathmatchAI`:

- The source reads `g_gametype` and `sv_maxclients` first.
- The eight DMQ3 bot cvars are registered in the retail order with matching
  defaults and flags.
- The next visible ownership boundary is the gametype-specific goal setup.

No source-code change was required for this slice. The reconstruction change is
a stronger parity gate in
`tests/test_botlib_qagame_ai_dmq3_deathmatch_setup_parity.py` that now checks
the full source, Binary Ninja HLIL, and Ghidra sequence.

## Confidence

- Focused DMQ3 setup cvar registration bridge: **91% -> 99%**.
- Focused qagame bot setup coverage: **96% -> 99%**.
- Overall botlib plus qagame/server wiring reconstruction parity:
  **83.78% -> 83.82%**.

Remaining uncertainty is not about this registration sequence; it is in later
bot decision and state-machine lanes that still need fresh evidence passes.
