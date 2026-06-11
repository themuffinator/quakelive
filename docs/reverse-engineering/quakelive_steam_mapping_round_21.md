# Quake Live Steam Host Mapping Round 21

## Scope

This round continues the native `cgamex86.dll` display-context recovery from Round 20, but shifts focus from the renderer/sound tail to the control-command seam in the middle of the retail `cgDC` callback block.

The main goals were:

- close the host callbacks behind retail native cgame `setCVar`, `startLocalSound`, and `executeText`
- explain the retail offset drift that pushes those callbacks later than the current reconstructed `displayContextDef_t`
- avoid forcing the still-split key-binding initializer until its second write site is pinned cleanly

The primary local evidence for this round is:

- `references/hlil/quakelive/quakelive_steam.exe/quakelive_steam.exe_hlil.txt`
- `references/hlil/quakelive/cgamex86.dll/cgamex86.dll_hlil.txt`
- `references/reverse-engineering/ghidra/quakelive_steam/functions.csv`
- `src/code/client/cl_cgame.c`
- `src/code/client/ql_cgame_imports.inc`
- `src/code/cgame/cg_main.c`
- `src/code/ui/ui_shared.h`

## Retail Native Cgame Mid-Band Shift

Round 20 already established that `sub_10029210` builds the retail local `cgDC` block by selecting specific entries from the host import slab at `data_565958`. This pass closes the next three host-backed callbacks and clarifies the layout drift.

Observed local facts:

1. In native cgame `sub_10029210`, the relevant local assignments are:
   - `data_10A25680 = *(result + 0x1C)` at local offset `0x60`
   - `data_10A25694 = *(result + 0x9C)` at local offset `0x74`
   - `data_10A256B8 = *(result + 0x50)` at local offset `0x98`
2. The current reconstructed `displayContextDef_t` in `src/code/ui/ui_shared.h` would place:
   - `setCVar` at `0x60`
   - `drawTextWithCursor` at `0x64`
   - `startLocalSound` at `0x70`
   - `executeText` at `0x94`
3. Retail native cgame callsites instead prove a one-slot shift after `setCVar`:
   - `(*(data_1074CCF8 + 0x60))(name, value)` performs cvar updates
   - `(*(data_1074CCF8 + 0x74))(sfx, channel)` starts local sounds
   - `(*(data_1074CCF8 + 0x98))(text)` appends console text such as `"in_restart\n"`
4. The simplest evidence-backed read is that retail carries one extra callback-sized slot after `setCVar`, which shifts the later control helpers by `+4` bytes relative to the current header. I am documenting that drift here rather than forcing a speculative struct edit.

## Local Offset `0x60`: Native Cgame `setCVar`

The `setCVar` host callback is now high-confidence.

Observed local facts:

1. `sub_10029210` assigns local `cgDC` offset `0x60` from host import `result + 0x1C`, which resolves to `data_565974 = sub_4EA2A0`.
2. Native cgame menu/HUD paths call that slot exactly like a cvar setter:
   - `sub_10059E49`: `(*(data_1074CCF8 + 0x60))(eax, sub_10057830())`
   - `sub_10058B96`: `(*(data_1074CCF8 + 0x60))(*(eax_2 + 0x158), "Custom")`
3. The host wrapper is a pure tailcall:
   - `sub_4EA2A0 -> sub_4CD250(arg1, arg2)`
4. `sub_4CD250` forwards to `sub_4CCE90(..., force = 1)`, and that underlying helper logs `Cvar_Set2: %s (%s)\n`, validates the cvar name, and performs the exact engine-side cvar set/update path.
5. The reconstructed host syscall layer already matches this meaning:
   - `ql_cgame_imports.inc`: `QL_CG_trap_Cvar_Set`
   - `cl_cgame.c`: `case CG_CVAR_SET: Cvar_Set( VMA(1), VMA(2) );`

That closes `sub_4EA2A0` as the native cgame cvar-set import wrapper.

## Local Offset `0x74`: Native Cgame `startLocalSound`

The shifted local-sound callback is now exact.

Observed local facts:

1. `sub_10029210` assigns local `cgDC` offset `0x74` from host import `result + 0x9C`, which resolves to `data_5659F4 = sub_4BEFB0`.
2. Native cgame uses that slot with the exact `sfxHandle_t, channelNum` shape:
   - `sub_10059ECC..10059EEB`: it first resolves a sound through `(*(data_1074CCF8 + 0xAC))(eax, 6)` and then passes the resulting handle into `(*(data_1074CCF8 + 0x74))(handle, 6)`
   - `sub_1005A2FD`: `(*(data_1074CCF8 + 0x74))(*ebp_1, 6)`
3. The host wrapper is a pure tailcall:
   - `sub_4BEFB0 -> sub_4DB3F0(arg1, arg2)`
4. `sub_4DB3F0` first returns silently unless the sound system is started and unmuted, then validates the handle range and logs `^3S_StartLocalSound: handle %i out of range\n` on failure, which pins the exact engine helper.
5. The reconstructed host syscall layer matches that role:
   - `ql_cgame_imports.inc`: `QL_CG_trap_S_StartLocalSound`
   - `cl_cgame.c`: `case CG_S_STARTLOCALSOUND: S_StartLocalSound( args[1], args[2] );`

That closes `sub_4BEFB0` as the native cgame local-sound import wrapper.

## Local Offset `0x98`: Retail `executeText` Lands On `Cbuf_AddText`

The retail command-text slot is now closed, and it is more specific than the old GPL-era `executeText` comment suggests.

Observed local facts:

1. `sub_10029210` assigns local `cgDC` offset `0x98` from host import `result + 0x50`, which resolves to `data_5659A8 = sub_4EA380`.
2. Native cgame calls that slot with a single `const char *` text argument:
   - `sub_10059E99`: `(*(data_1074CCF8 + 0x98))(sub_100575E0("%s ; "))`
   - `sub_1005E442`: `(*(data_1074CCF8 + 0x98))("in_restart\n")`
3. The host wrapper is a pure tailcall:
   - `sub_4EA380 -> sub_4C7CF0(arg1)`
4. `sub_4C7CF0` is the engine command-buffer append helper: it checks buffer space and emits the exact overflow string `Cbuf_AddText: overflow\n`.
5. The reconstructed syscall table matches that behavior directly:
   - `cl_cgame.c`: `case CG_SENDCONSOLECOMMAND: Cbuf_AddText( VMA(1) );`
   - `ql_cgame_imports.inc`: `QL_CG_trap_SendConsoleCommand`

So the retail `cgDC` text-command slot is not a two-argument `trap_Cmd_ExecuteText` wrapper. It lands on the one-argument send-console-command / `Cbuf_AddText` path instead.

## Promoted Aliases

| Raw symbol | Alias candidate | Basis | Observed role |
| --- | --- | --- | --- |
| `sub_4EA2A0` (`0x004EA2A0`) | `QLCGImport_Cvar_Set` | Observed | Native cgame import wrapper for `Cvar_Set`, used as the retail `cgDC.setCVar` callback. |
| `sub_4EA380` (`0x004EA380`) | `QLCGImport_SendConsoleCommand` | Observed | Native cgame import wrapper behind the shifted retail `cgDC` text-command slot; tailcalls `Cbuf_AddText`. |
| `sub_4BEFB0` (`0x004BEFB0`) | `QLCGImport_S_StartLocalSound` | Observed | Native cgame import wrapper for `S_StartLocalSound`. |

## Open Questions

1. The retail local `cgDC` still has an unresolved callback-sized gap after `setCVar`. The current evidence proves the shift, but I have not yet found the second initializer or a stable callsite for that missing slot.
2. The key-binding trio at local offsets `0x8C..0x94` is still split across additional initialization paths outside `sub_10029210`. I am leaving those host wrappers unpromoted until the second write site is pinned cleanly.
3. This round intentionally does not rename the raw host entries at `data_5659E8..data_5659F0`; the direct `data_1074CCCC` callers around `0x10013525` belong to a different native cgame syscall seam and deserve a separate pass.
