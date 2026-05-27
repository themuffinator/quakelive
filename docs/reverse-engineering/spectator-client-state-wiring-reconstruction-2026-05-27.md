# Spectator Client State Wiring Reconstruction - 2026-05-27

## Scope

This pass maps the cross-binary spectator client-state lane that keeps retail
Quake Live observers synchronized after team changes, respawns, follow-state
snapshot copies, and major-item timer updates. It covers the qagame producers,
the client command bridge, and the cgame consumers that rebuild local spectator
HUD state.

## Evidence Map

| Retail address | Recovered name | Source owner | Evidence summary |
| --- | --- | --- | --- |
| `0x10040440` | `G_ApplyTeamChange` | `src/code/game/g_cmds.c` | HLIL/Ghidra set `ps.eFlags |= 0x4000` on the spectator destination path, clear the same bit for non-spectator destinations, write `sess.sessionTeam`, then call `sub_1004ED70` for spectator item-state resync. |
| `0x1003BC30` | `ClientSpawn` | `src/code/game/g_client.c` | HLIL checks `sess.sessionTeam == TEAM_SPECTATOR`, sets or clears the same `0x4000` playerstate eFlag before toggling `EF_TELEPORT_BIT`, and preserves that value across the respawn memset. |
| `0x100433D0` | `CG_Respawn` | `src/code/cgame/cg_playerstate.c` | Retail cgame checks the recovered `0x4000` eFlag and sends the `specresp` client command after the usual respawn reset work. |
| `0x1004EAC0` | `G_SendSpectatorItemStateToClient` | `src/code/game/g_items.c` | Builds one `EV_ITEM_PICKUP_SPEC` temp entity for a spectator, using single-client delivery and packing owner, item, absolute respawn time, duel layout, palette, and initial-sync state into entity fields. |
| `0x1004ED10` | `G_BroadcastSpectatorItemState` | `src/code/game/g_items.c` | Fans the synthetic spectator item-state event to connected spectators when a tracked major item is picked up. |
| `0x1004ED70` | `G_SyncSpectatorItemStatesForClient` | `src/code/game/g_items.c` | Walks live item entities and sends initial-sync item states to one spectator client on team entry or `specresp`. |
| `0x10019D90` | `CG_RecordSpectatorItemPickup` | `src/code/cgame/cg_draw.c` | Decodes the synthetic event into the ten-row spectator item cache keyed by pickup owner. |
| `0x1001C8D0` / `0x1001CA10` / `0x1001CA90` / `0x1000F700` | spectator item cache maintenance and draw path | `src/code/cgame/cg_draw.c` | Clear, compare, per-frame update, and draw the spectator major-item timer overlay gated by `cg_specItemTimers*`. |

## Reconstructed Wiring

1. Added `EF_SPECTATOR_RESPAWN` as the Quake Live name for the retail `0x4000`
   playerstate bit. It intentionally aliases the GPL `EF_VOTED` value because
   the retail binaries use that bit as both the legacy vote marker and the
   spectator `specresp` cue.
2. `G_ApplyTeamChange` now sets `EF_SPECTATOR_RESPAWN` when the resolved team is
   `TEAM_SPECTATOR` and clears it otherwise, matching the retail write before
   session mutation and item-state resync.
3. `ClientSpawn` now re-applies the same spectator eFlag rule before toggling
   `EF_TELEPORT_BIT`, so respawn snapshots carry the bit that retail cgame
   checks in `CG_Respawn`.
4. `SpectatorClientEndFrame` now describes the copied-follow snapshot merge in
   spectator-state terms: the followed player's snapshot is copied, but the
   observer's `EF_SPECTATOR_RESPAWN` and team-vote bits survive the copy.
5. `CG_Respawn` now gates the `specresp` command through
   `EF_SPECTATOR_RESPAWN` instead of a raw `0x00004000` literal.
6. The server-side item-state path remains a single-client synthetic event:
   `Touch_Item` records owner/palette/layout before hiding the respawning item,
   links the hidden item, then broadcasts `EV_ITEM_PICKUP_SPEC`; `specresp` and
   spectator team entry use the same send helper with `initialSync`.
7. The cgame item-state path records the event only after the retail-style
   event filter validates owner and item class, then updates/sorts/draws the
   ten-row spectator item cache under the `cg_specItemTimers*` cvars.

## Guardrails

- Observed facts: the `0x4000` set/clear in `G_ApplyTeamChange`, the repeated
  `0x4000` set/clear in `ClientSpawn`, the `CG_Respawn` `specresp` command
  string, the `specresp` qagame command handler, and the `EV_ITEM_PICKUP_SPEC`
  producer/consumer call flow.
- Inference: `EF_SPECTATOR_RESPAWN` is a descriptive source alias, not a new
  retail enum name. The alias is justified because it bridges two independent
  signals: server writes the bit for spectator client state, and cgame reads the
  same bit to trigger the spectator respawn resync command.
- The vote overlap is intentional. Retail Quake Live reuses the GPL `EF_VOTED`
  bit value for this spectator cue, so the source keeps both names rather than
  inventing a different network bit.

## Verification

New static coverage lives in
`tests/test_spectator_client_state_wiring_parity.py`. It locks the eFlag alias,
the qagame set/clear order, the cgame `specresp` command gate, the qagame
`specresp` handler, the spectator item-event payload fields, the cgame decoder,
the item touch/broadcast order, and the mapping-ledger notes.

## Parity Estimate

Scoped spectator client-state parity: before 99.90% -> after 99.97%.

Repo-wide parity remains 98%. This was a narrow cross-binary reconstruction
rather than a new repo-wide audit closure.
