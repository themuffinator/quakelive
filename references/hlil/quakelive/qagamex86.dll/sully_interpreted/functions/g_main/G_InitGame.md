# `G_InitGame` (`sub_10055110`)

**Signature:** `void G_InitGame(int levelTime, int randomSeed, int restart)`  
**Address:** `0x10055110`

`sub_10055110` mirrors the Quake III Arena `G_InitGame` routine with Quake Live’s
Steam-aware logging and session handling bolted on.

* The function prints the usual banner (`"------- Game Initialization -------"`) and
  seeds the random number generator, exactly like the GPL code, before clearing
  the `level` globals (`memset(&data_105dce40, 0, 0x4B9C)`).【F:references/hlil/quakelive/qagamex86.dll/qagamex86.dll.bndb_hlil.txt†L61286-L61303】
* `level.time` and `level.previousTime` are set to the incoming `levelTime`,
  while `_time64` is cached to publish the `g_levelStartTime` cvar—identical to
  the stock engine initialisation.【F:references/hlil/quakelive/qagamex86.dll/qagamex86.dll.bndb_hlil.txt†L61304-L61315】
* Logfile setup honours the Quake Live dual-mode switch: if `g_logSync`
  (`data_105aa36c`) is disabled the engine helper is called with `mode=2`,
  otherwise mode `3` is used so the host can enforce synchronous writes.  Both
  cases invoke the same callbacks Quake III used but with the Live globals
  (`data_105dce54`, `data_105a5c94`).【F:references/hlil/quakelive/qagamex86.dll/qagamex86.dll.bndb_hlil.txt†L61321-L61348】
* The routine latches the stored `session` value and toggles
  `data_105dce7c` when the persistent gametype does not match `g_gametype`,
  forcing Quake Live’s `newSession` flow before calling into
  `G_WriteSessionData` (`sub_1003a270`).【F:references/hlil/quakelive/qagamex86.dll/qagamex86.dll.bndb_hlil.txt†L61350-L61362】
* Entity/client arrays are cleared and fanned out just as in Quake III:
  `g_entities` at `data_104b3fa0`, `g_clients` at `0x105AD180`, with the helper at
  `data_104b13ac + 0x58` publishing the sizes to the engine so configstrings can
  serialise the structures.【F:references/hlil/quakelive/qagamex86.dll/qagamex86.dll.bndb_hlil.txt†L61363-L61421】
* Finally the function executes the usual spawn pipeline—`SpawnEntities`,
  `InitBodyQue`, `G_FindTeams`, bot initialisation, and the ruleset switch table—
  but swaps in Quake Live helpers (`sub_10066440`, `sub_10038160`, etc.) for the
  enhanced modes.【F:references/hlil/quakelive/qagamex86.dll/qagamex86.dll.bndb_hlil.txt†L320-L421】

Taken together these steps confirm that the Quake Live DLL still honours the
original VM lifecycle while layering in persistent session state and Steam-aware
logging.
