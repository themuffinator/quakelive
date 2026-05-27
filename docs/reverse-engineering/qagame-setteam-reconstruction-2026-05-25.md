# qagame SetTeam Reconstruction - 2026-05-25

## Evidence Checked

- Owning retail binary: `qagamex86.dll`.
- Ghidra corpus baseline: `references/reverse-engineering/ghidra/qagamex86/metadata.txt` reports 1027 functions, 65 imports, 2 exports, and 180 decompiled functions.
- Function starts from `functions.csv`: `FUN_10040440` size 637, `FUN_100406d0` size 1587, `FUN_10040d90` size 403, `FUN_100618b0` size 138, `FUN_100647c0` size 95, `FUN_100680c0` size 60, and `FUN_10068100` size 62.
- Symbol map anchors from `references/symbol-maps/qagame.json`: `0x10040440` is `G_ApplyTeamChange`, `0x100406D0` is `SetTeam`, `0x10040D90` is `Cmd_Team_f`, `0x100618B0` is `G_TeamJoinAllowed`, `0x100647C0` is `G_RRResolveAutoJoinTeam`, `0x100680C0` is `TeamCount`, and `0x10068100` is `Team_CountsBalanced`.
- Canonical HLIL note: the committed Binary Ninja qagame split currently covers `bg_pmove` and `g_items`, not a dedicated `g_cmds`/`SetTeam` split. This round therefore used the committed symbol map and Ghidra decompile as structured companion evidence, with source/tests as reconstruction guards.
- Cross-check evidence for the retail `gclient + 0x3E4` slab came from `references/hlil/quakelive/qagamex86.dll/qagamex86.dll.bndb_hlil_split/qagamex86.dll.bndb_hlil_part01.txt`, `part02.txt`, the Ghidra decompile, and the committed overlay in `src/game/ql_game_types.h`.

## Recovered Wiring

- `SetTeam` remains the outer parser at `0x100406D0`. It resolves scoreboard/follow/free spectator requests, team token requests, Red Rover autojoin fallback, team-balance rejection, tournament queue/spectate-only latches, and the `G_TeamJoinAllowed` lock gate.
- `G_ApplyTeamChange` is now restored as the inner executor corresponding to `0x10040440`. It owns the body-queue/death transition, rank stats teardown/reset, session field mutation, spectator item sync, leadership repair, userinfo republish, `ClientBegin`, and the rank switch-team event.
- `Cmd_Team_f` now follows the recovered retail command wrapper contract by using `ConcatArgs( 1 )` before forwarding to `SetTeam`, matching the symbol-map note for `0x10040D90`.
- `SetTeam` now performs the retail outer tail call pattern: `G_ApplyTeamChange( ent, (team_t)team, specState, specClient );` followed by `CalculateRanks();`.
- `follow1` and `follow2` now mirror the decompiled active-player fallback: `follow1` drops to free spectator when no active player exists, while `follow2` follows `FOLLOW_ACTIVE1` with one active player and drops to free spectator with none.
- Red Rover now takes the retail pre-balance route for non-spectator team requests, using `G_RRResolveAutoJoinTeam` instead of honoring explicit red/blue tokens through the generic team-mode force-balance branch.
- `G_ClearClientRevengeState` now mirrors the decompiled `level.sortedClients` loops that clear a changed or disconnected client's per-opponent revenge counter across connected clients before userinfo publication or slot teardown.

## Source Reconstruction Notes

- The spectator timestamp path now uses `(int)time( NULL )` when the queue position is clear, matching the existing session serializer/init convention and the decompiled inner helper.
- The recovered helper syncs spectator item states as soon as the session team becomes spectator, then republishes userinfo and re-enters `ClientBegin`.
- Follow-up 2026-05-27: the previously deferred `ps.eFlags |= 0x4000`
  spectator write is now modeled as `EF_SPECTATOR_RESPAWN`, an intentional alias
  of the GPL `EF_VOTED` bit value. `G_ApplyTeamChange` sets/clears it with the
  resolved team, and `ClientSpawn` repeats the same rule before the respawn
  teleport toggle so cgame can send `specresp` from `CG_Respawn`.
- Red Rover live team changes suppress the generic team-change broadcast and rank-stat teardown path unless the destination is spectator, reflecting the special-case branches visible around the retail inner helper.
- The rank switch-team event is emitted after `ClientBegin`, matching the observed retail executor ordering more closely than the previous monolithic source tail.
- `gclient_t` now carries the reconstructed `revengeKillStreaks[MAX_CLIENTS]` matrix. The death path increments `attacker[victim]`, awards the `REVENGE` player event/rank medal when the reverse counter reaches the retail threshold, and clears `victim[attacker]`; `ClientSpawn` preserves the matrix across respawn memset, while `ClientDisconnect` clears the departing slot from the connected clients.

## Open Questions

- The retail helper has a Red Rover direct `ClientSpawn`/loadout path when the round controller is already in a live state. Current source routes Red Rover through `ClientBegin` and `G_RRResetClientForRound`; this remains intentionally deferred until that controller state can be cross-checked in a focused Red Rover runtime/static pass.
- The outer `SetTeam` decompile exposes a team-size cap diagnostic distinct from `g_maxGameClients`. Current source still relies on the existing `g_maxGameClients` and balance gates until the cvar ownership for that cap is pinned down.

## Parity Estimate

- Before this round: `SetTeam` and immediate command wiring were about 78% reconstructed relative to the retail evidence, with the parser behavior mostly present but the inner executor boundary flattened into the GPL-shaped function.
- After the first source split: the same surface was about 88% reconstructed.
- After the follow/Red Rover parser pass: the same surface was about 91% reconstructed.
- After the revenge-matrix pass: the same surface is about 94% reconstructed. The major remaining gaps are the ambiguous spectator eflag write, the team-size cap diagnostic, and the Red Rover live-spawn shortcut.
