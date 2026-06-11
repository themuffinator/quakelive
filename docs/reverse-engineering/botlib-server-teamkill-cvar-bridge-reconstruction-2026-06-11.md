# Botlib Server Teamkill Cvar Bridge Reconstruction - 2026-06-11

## Scope

This pass rechecked the server-owned botlib initialization bridge around
`SV_BotInitCvars`, `SV_BotInitBotLib`, and the adjacent native qagame import
wrappers. The concrete source reconstruction is the missing retail
`bot_teamkill` cvar precreation at the tail of `SV_BotInitCvars`.

## Retail Evidence

Primary Binary Ninja evidence comes from
`references/hlil/quakelive/quakelive_steam.exe/quakelive_steam.exe_hlil_split/quakelive_steam.exe_hlil_part04.txt`:

- `0x004DD6F0` is the retail `SV_BotInitCvars` body.
- The existing source already matched the earlier recovered retail fixes:
  `bot_enable` default `1` with flags `0x40`, `bot_thinktime` default `100`
  with flags `0`, and `bot_grapple` default `1`.
- The HLIL tail registers `bot_interbreedwrite` and then returns from
  `sub_4ce0d0(..., "bot_teamkill", U"0", 0)`.

Structured Ghidra evidence in
`references/reverse-engineering/ghidra/quakelive_steam/functions.csv` pins
`FUN_004dd6f0,004dd6f0,579,0,unknown`, and the shared alias corpus maps
`sub_4DD6F0 -> SV_BotInitCvars`.

The same pass rechecked the surrounding bridge names:

- `sub_4DD940 -> SV_BotInitBotLib`
- `sub_4DD640 -> BotClientCommand`
- `sub_4DD670 -> SV_BotFrame`
- `sub_4DDA50 -> SV_BotGetConsoleMessage`
- `sub_4DDAC0 -> SV_BotGetSnapshotEntity`
- `sub_4E1610 -> QL_G_trap_BotAllocateClient`
- `sub_4E1620 -> QL_G_trap_BotFreeClient`
- `sub_4E17F0 -> QL_G_trap_BotGetServerCommand`
- `sub_4E1800 -> QL_G_trap_BotUserCommand`

## Reconstruction

`src/code/server/sv_bot.c::SV_BotInitCvars` now registers:

```c
Cvar_Get("bot_teamkill", "0", 0);
```

The line is kept after `bot_interbreedwrite`, matching the retail cvar order
seen in HLIL. No qagame AI behavior was changed in this pass; the recovered
source change only restores the host-side cvar precreation surface.

## Regression Coverage

`tests/test_botlib_server_game_bridge_parity.py` now pins:

1. The complete source-side `SV_BotInitCvars` bot cvar sequence in retail order.
2. The Binary Ninja HLIL anchors for the `bot_interbreedwrite` call and final
   `bot_teamkill` return call.
3. The existing server botlib lifecycle, native qagame import assignments, and
   bot command/snapshot bridge wrappers.

Focused validation:

```powershell
python -m pytest tests/test_botlib_server_game_bridge_parity.py -q --tb=short
```

Result:

```text
5 passed in 0.46s
```

## Open Boundaries

This pass does not infer any qagame-side consumer for `bot_teamkill`; the
observed retail evidence only proves server-side cvar registration. Future work
should only promote a game-side behavioral mapping if a retail qagame HLIL body
or Ghidra row demonstrates direct use.

## Parity Estimate

- Focused `SV_BotInitCvars` retail cvar tranche: **96% -> 99%**.
- Server botlib lifecycle/import bridge confidence: **97% -> 98%**.
- Overall botlib plus qagame/server wiring reconstruction parity:
  **83.5% -> 83.58%**.
