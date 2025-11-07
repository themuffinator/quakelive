# `ClientConnect` (`sub_1003AC10`)

**Signature:** `const char *ClientConnect(int clientNum, qboolean firstTime, qboolean isBot)`  
**Address:** `0x1003AC10`

The HLIL around `0x1003AC10` maps cleanly onto Quake III Arena’s `ClientConnect`
implementation with Quake Live’s backend hooks layered in.

1. **Ban & password checks** – If this is the first handshake (`firstTime`), the
   routine queries the backend ban list via `sub_10032460()` and blocks the
   connect with the familiar ban string when the lookup returns `-1`—a direct
   lift from the GPL code.  It also validates the `password` userinfo key against
   the server latch before allowing non-localhost clients to continue.【F:references/hlil/quakelive/qagamex86.dll/qagamex86.dll.bndb_hlil.txt†L41023-L41084】
2. **Client block setup** – The entity pointer (`g_entities[clientNum]`) is
   linked to the freshly cleared client slot (`memset(client, 0, 0xBD8)`) and the
   engine callback at `data_104b13ac + 0x320` provides the 64-bit Steam ID stored
   at offsets `0x2C0/0x2C4`.  This replaces Quake III’s CD-key hash bookkeeping
   while keeping the same overall structure.【F:references/hlil/quakelive/qagamex86.dll/qagamex86.dll.bndb_hlil.txt†L41112-L41123】
3. **Persistent data migration** – On restarts or reconnects (`firstTime == qtrue`
   or `level.newSession`), Quake Live resets the persistent stats block
   (`memset(client + 0x568, 0, 0x32C)` and randomises the command time seed) so
   returning clients do not inherit stale timers.【F:references/hlil/quakelive/qagamex86.dll/qagamex86.dll.bndb_hlil.txt†L41124-L41133】
4. **Steam authentication** – When `firstTime` is `qfalse`, the function calls the
   engine helper at `data_104b13ac + 0x334`; a zero return triggers the
   "Failed to verify Steam auth token" rejection that Quake Live introduced.
   Bots bypass this path by forcing the entity flag at `gentity + 0x1E0`.【F:references/hlil/quakelive/qagamex86.dll/qagamex86.dll.bndb_hlil.txt†L41136-L41149】
5. **Privilege & logging** – The routine mirrors Quake III’s logging strings
   (`"ClientConnect: %i"`) while adding Quake Live’s privilege broadcast
   (`"priv %i"`) when the backend marks the account as premium.  Steam ID prints
   leverage the same `Com_Printf` callback chain as the GPL code.【F:references/hlil/quakelive/qagamex86.dll/qagamex86.dll.bndb_hlil.txt†L41152-L41189】

A successful connect ends by clearing the `SVF_BOT` bit unless the slot truly is
bot-driven and returns `NULL`, matching the Quake III convention that a `NULL`
string signals acceptance.
