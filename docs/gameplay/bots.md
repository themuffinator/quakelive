# Bot Admission and Regression Notes

This page captures the current expectations for server-side bot handling in the Quake Live reverse engineering project.

## Slot reclamation for local players

* When `sv_maxclients` slots are exhausted by bots, a new connection from the local host (`ip` of `localhost`) should evict the last bot rather than failing with "server is full". The server enumerates active clients and counts only entries whose `client_t.state` is not `CS_FREE` **and** whose `netchan.remoteAddress.type` is `NA_BOT`.
* `SV_DirectConnect` now funnels that detection through `SV_ClientIsBot`, guaranteeing that only live, masked bot slots contribute to the "all bots" verdict. The helper also records the highest indexed bot so the eviction targets the freshest mask-bearing slot, mirroring the behaviour captured in the regression traces.
* Regression scenario: start a listen server with the maximum number of bots, then issue a local `connect localhost`. The expected result is that the newest bot is dropped ("only bots on server") and the human client reuses that slot. Previously, stale bot records prevented the eviction because the NA_BOT mask persisted after a bot disconnected.

## Expected clean-up

* `SV_BotFreeClient` now clears the remote address type back to `NA_BAD` when the slot is released. This keeps bookkeeping consistent for any feature that scans `svs.clients` for bot occupants.
* Game-side code (e.g. `ClientConnect` in `g_client.c`) still receives the `isBot` hint by checking the `NA_BOT` transport type for clients whose state is at least `CS_CONNECTED`.

## Bot flag masking

* The server marks a bot slot by setting `SVF_BOT` only after the `client_t` reaches `CS_CONNECTED`, ensuring entity flags stay in sync with live clients and mirroring the HLIL flow noted in the ClientConnect analysis.
* `SV_ClientIsBot` centralises the masking checks so reconnects, listen-server slot reclamation, and map restarts all rely on the same predicate. `SV_DropClient` captures the predicate once (`wasBot`) to clear masks on eviction without disturbing human challenge bookkeeping, while `SV_MapRestart_f` and `SV_SpawnServer` reuse it to refresh bots as they re-enter the world.
* Regression scenario: add a bot, issue `clientkick <botnum>`, then immediately connect as a human. Inspect `g_entities[botnum].r.svFlags` (via `entitylist` or debugging) to confirm the `SVF_BOT` bit clears once the slot returns to `CS_FREE`, preventing stale bot markers from leaking into recycled slots. The `tests/test_server_bot_masking.py::test_drop_client_clears_bot_mask_when_reclaimed` guard ensures this flow continues to mirror Quake Live.
* Regression scenario: populate a server with bots, run `map_restart`, and verify that each returning bot entity is re-flagged once it hits `CS_ACTIVE` while any human reconnecting during the restart keeps `SVF_BOT` cleared. This confirms the refresh call in `SV_ClientEnterWorld` mirrors the HLIL masking behaviour across state transitions. The `test_map_restart_refreshes_entity_masks_via_helper` regression test snapshots this lifecycle so future changes are caught immediately.
* Regression scenario: allow a human to reclaim a freshly freed bot slot (for example by connecting from localhost after a bot eviction) and watch the entity through the `CS_CONNECTED` handshake; the mask should clear as soon as the connection is accepted, matching the Quake Live HLIL expectations for admission checks. `test_listen_server_slot_reclaim_uses_bot_mask_helper` covers this handshake by asserting the helper-guided eviction path stays intact.

## Known limitations

* Remote players cannot automatically reclaim slots from bots; they must wait for manual kicks or administrative commands.
* The Steam ID handshakes mentioned in the HLIL dumps remain unimplemented and will continue to deny authentication if a backend requires them.

Keep these behaviours in mind when changing server/client admission paths or adjusting how bots are counted inside matchmaking heuristics.
