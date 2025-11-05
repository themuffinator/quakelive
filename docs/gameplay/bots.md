# Bot Admission and Regression Notes

This page captures the current expectations for server-side bot handling in the Quake Live reverse engineering project.

## Slot reclamation for local players

* When `sv_maxclients` slots are exhausted by bots, a new connection from the local host (`ip` of `localhost`) should evict the last bot rather than failing with "server is full". The server enumerates active clients and counts only entries whose `client_t.state` is not `CS_FREE` **and** whose `netchan.remoteAddress.type` is `NA_BOT`.
* Regression scenario: start a listen server with the maximum number of bots, then issue a local `connect localhost`. The expected result is that the newest bot is dropped ("only bots on server") and the human client reuses that slot. Previously, stale bot records prevented the eviction because the NA_BOT mask persisted after a bot disconnected.

## Expected clean-up

* `SV_BotFreeClient` now clears the remote address type back to `NA_BAD` when the slot is released. This keeps bookkeeping consistent for any feature that scans `svs.clients` for bot occupants.
* Game-side code (e.g. `ClientConnect` in `g_client.c`) still receives the `isBot` hint by checking the `NA_BOT` transport type for clients whose state is at least `CS_CONNECTED`.

## Known limitations

* Remote players cannot automatically reclaim slots from bots; they must wait for manual kicks or administrative commands.
* The Steam ID handshakes mentioned in the HLIL dumps remain unimplemented and will continue to deny authentication if a backend requires them.

Keep these behaviours in mind when changing server/client admission paths or adjusting how bots are counted inside matchmaking heuristics.
