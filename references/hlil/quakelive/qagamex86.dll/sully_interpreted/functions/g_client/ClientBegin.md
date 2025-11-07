# `ClientBegin` (`sub_1003B030`)

**Signature:** `void ClientBegin(int clientNum)`  
**Address:** `0x1003B030`

The Quake Live implementation of `ClientBegin` starts at `0x1003B030`.  The HLIL
tracks the same spawn preparation steps as the Quake III GPL source while adding
Live’s extra session wiring.

* **Client slot reset** – The routine rebuilds the `gclient_t` template by wiping
  the leading `0x250` bytes, restoring the saved `svFlags`, and initialising
  timers (`client->pers.enterTime`, vote cooldowns) to `level.time`.  Session
  team data at `0x348` is inspected to decide whether the player should respawn
  as a spectator or rejoin their previous team.【F:references/hlil/quakelive/qagamex86.dll/qagamex86.dll.bndb_hlil.txt†L41211-L41224】
* **Class loadouts** – Quake Live replaces the Quake III weapon loadout switch
  with a gametype-driven dispatch (`switch(data_105a898c)`) that calls helpers
  such as `sub_100634f0` (Duel) or `sub_1004bde0` (Clan Arena).  The HLIL shows
  the same table-driven design as the GPL code’s `ClientBegin` with different
  branches for Live-specific modes.【F:references/hlil/quakelive/qagamex86.dll/qagamex86.dll.bndb_hlil.txt†L41227-L41239】
* **Stat mirroring** – After pulling in the loadout, the function pushes the
  persistent max health into `ps.stats[STAT_HEALTH]` and resets award trackers at
  `0x2D8`/`0x2DC`, matching Quake III’s logic but targeting the larger
  `gclient_t` layout.【F:references/hlil/quakelive/qagamex86.dll/qagamex86.dll.bndb_hlil.txt†L41219-L41224】
* **Session logging** – The familiar `"ClientBegin: %i"` print occurs immediately
  before returning, confirming the same call-site Quake III used for server logs
  and demos.【F:references/hlil/quakelive/qagamex86.dll/qagamex86.dll.bndb_hlil.txt†L41248-L41252】

Once `ClientBegin` returns the next frame invokes `ClientThink_real` through the
standard frame pipeline described in the `G_RunFrame` Sully notes.
