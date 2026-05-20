# Native pipeline VM call inventory

This document captures every `VM_Create` and `VM_Call` usage across the client, server, and shared subsystems so we can plan the removal of the QVM seam. Each entry records the current lifecycle responsibility and the proposed native entry point or shim that will replace the VM trampoline. Signature notes highlight where the vararg `VM_Call` interface must be tightened when moving to native exports.

## Status update (2026-03-26)

The source-built native DLL ABI slice is now largely in place:

- platform loaders prefer the structured Quake Live-style `dllEntry(exports, imports, apiVersion)` interface before the legacy `vmMain` fallback
- `cgame`, `qagame`, and `ui` now publish recovered native export-slot tables distinct from the legacy `vmMain` enums
- `VM_Call` native dispatch maps engine call numbers onto the recovered retail native export order
- engine-side native import dispatch is split from legacy syscall-contract logging, so native DLL traffic no longer appears as old VM syscall traffic during validation

That closes the core import/export replication work for the reconstructed source-built gameplay DLLs. The remaining work in this area is strict compatibility validation against the retail DLLs themselves, plus the host/platform/bootstrap surfaces those binaries expect from the retail engine.

That retail-binary validation lane now has a dedicated tracked probe:
`tools/modules/run_retail_module_runtime_probe.ps1`, with the current evidence
captured in
`artifacts/module_validation/logs/retail_module_runtime_evidence_latest.json`.
That stable alias is only promoted when a rerun remains sufficient, and it now
points at the current bounded `2026-04-21` artifact. The authoritative tracked
pass still loads retail `uix86.dll`, `qagamex86.dll`, and `cgamex86.dll` from
the Steam profile root under the reconstructed host. The remaining live-map
shortfall is no longer an ambiguous module-host failure; it is the
renderer-owned `R_fonsErrorCallback` font-atlas saturation blocker that
prevents `CS_ACTIVE` after retail module load, which belongs to the renderer
text audit rather than to the native module ABI slice. The 2026-05-20 renderer
wiring pass removed the non-retail eager FontStash prebuild behind that
source-side blocker, restored the retained atlas upload to retail `GL_ALPHA`
storage, and realigned the renderer `GetRefAPI` table to the retail version
`9` / `0x9c` export-tail ABI. This alias is now stale evidence until the
module runtime probe is rerun.

The final strict-retail module closure state is tracked separately by
`tests/test_game_module_retail_parity_gate.py`, which writes
`artifacts/module_validation/logs/retail_module_parity_gate.json` as the
current `GMR-P8` artifact across the combined module gap register first unified
in `GMR-P5`. That gate consumes the stable runtime alias above together with
the launcher/resource fallback closure, the current `2026-04-10` module audit,
and the synced parity ledgers/pipeline notes, so the module layer can close
without claiming ownership of the remaining renderer blocker. The alias
promotion rule keeps degraded reruns from silently replacing the authoritative
bounded artifact until the host/runtime seam is revalidated cleanly again.

## Client UI VM (`uivm`)
| Lifecycle | Location(s) | Current invocation | Proposed native entry (signature) | Notes / blockers |
| --- | --- | --- | --- | --- |
| Load | `CL_InitUI` – `src/code/client/cl_ui.c` | `uivm = VM_Create("ui", CL_UISystemCalls, interpret);` | `bool UI_Load(vmInterpret_t interpret, const uiImports_t *imports);` returning success and caching imports. | Requires native replacement for `CL_UISystemCalls` dispatch table; DLL must expose initializer that accepts structured imports. 【F:src/code/client/cl_ui.c†L1157-L1176】 |
| Version gate | `CL_InitUI` | `VM_Call(uivm, UI_GETAPIVERSION);` | `int UI_GetApiVersion(void);` | Move version constant definitions to shared native header. 【F:src/code/client/cl_ui.c†L1163-L1176】 |
| Init | `CL_InitUI` | `VM_Call(uivm, UI_INIT, (cls.state >= …));` (invoked for both legacy and current API path). | `void UI_Init(qboolean inGame);` | Requires passing `qboolean`/`bool` instead of implicit int; initialization currently depends on `cls` globals via system calls. 【F:src/code/client/cl_ui.c†L1167-L1176】 |
| Shutdown | `CL_ShutdownUI` – `src/code/client/cl_ui.c` | `VM_Call(uivm, UI_SHUTDOWN);` | `void UI_Shutdown(void);` | Must ensure UI module releases resources without relying on VM stack unwinding. 【F:src/code/client/cl_ui.c†L1133-L1144】 |
| Console command | `UI_GameCommand` – `src/code/client/cl_ui.c` | `VM_Call(uivm, UI_CONSOLE_COMMAND, cls.realtime);` | `qboolean UI_ConsoleCommand(int realtime);` | Depends on `cls` global; evaluate moving required values into explicit parameters. 【F:src/code/client/cl_ui.c†L1193-L1202】 |
| Unique CD key check | `UI_usesUniqueCDKey` – `src/code/client/cl_ui.c` | `VM_Call(uivm, UI_HASUNIQUECDKEY);` | `qboolean UI_HasUniqueCDKey(void);` | Return type should be strict boolean; remove manual comparison with `qtrue`. 【F:src/code/client/cl_ui.c†L1179-L1186】 |
| Menu activation | `CL_Disconnect`, `CL_Frame`, cinematic start, and key/menu handlers – `cl_main.c`, `cl_cin.c`, `cl_keys.c`, `cl_scrn.c` | `VM_Call(uivm, UI_SET_ACTIVE_MENU, UIMENU_*);` | `void UI_SetActiveMenu(menuCommand_t id);` | Centralize menu enums in shared header; ensure callers pass typed enum instead of raw ints. 【F:src/code/client/cl_main.c†L738-L772】【F:src/code/client/cl_main.c†L1988-L2004】【F:src/code/client/cl_cin.c†L1528-L1542】【F:src/code/client/cl_keys.c†L1094-L1124】【F:src/code/client/cl_scrn.c†L450-L486】 |
| Key input | `CL_KeyEvent`, `CL_CharEvent` – `src/code/client/cl_keys.c` | `VM_Call(uivm, UI_KEY_EVENT, key, down);` and `VM_Call(uivm, UI_KEY_EVENT, key | K_CHAR_FLAG, qtrue);` | `void UI_KeyEvent(int key, qboolean down);` | UI key dispatch now sits behind the recovered console/browser catcher priority and the demo-playback shortcut guard; preserve UTF-8/key flag policy when native entrypoints replace VM calls. 【F:src/code/client/cl_keys.c†L1361-L1525】 |
| Mouse input | `CL_MouseEvent` – `src/code/client/cl_input.c` | `VM_Call(uivm, UI_MOUSE_EVENT, dx, dy);` | `void UI_MouseEvent(int dx, int dy);` | Preserve the recovered raw event payload after the `cg_ignoreMouseInput` and browser-keycatcher gates. 【F:src/code/client/cl_input.c†L368-L394】 |
| Fullscreen query | `SCR_DrawScreenField` – `src/code/client/cl_scrn.c` | `VM_Call(uivm, UI_IS_FULLSCREEN);` | `qboolean UI_IsFullscreen(void);` | Used to gate background rendering; ensure deterministic return semantics. 【F:src/code/client/cl_scrn.c†L458-L472】 |
| Connection draw | `SCR_DrawScreenField` – `src/code/client/cl_scrn.c` | `VM_Call(uivm, UI_REFRESH, cls.realtime);` / `VM_Call(uivm, UI_DRAW_CONNECT_SCREEN, qfalse/qtrue);` | `void UI_Refresh(int realtime);` / `void UI_DrawConnectScreen(qboolean overlay);` | Both functions rely on `cls.realtime`; consider packaging timing data into shared context struct. 【F:src/code/client/cl_scrn.c†L469-L506】 |

## Client game VM (`cgvm`)
| Lifecycle | Location(s) | Current invocation | Proposed native entry (signature) | Notes / blockers |
| --- | --- | --- | --- | --- |
| Load | `CL_InitCGame` – `src/code/client/cl_cgame.c` | `cgvm = VM_Create("cgame", CL_CgameSystemCalls, interpret);` | `bool CG_Load(vmInterpret_t interpret, const cgameImports_t *imports);` | Requires native import surface mirroring `CL_CgameSystemCalls`. 【F:src/code/client/cl_cgame.c†L758-L772】 |
| Init | `CL_InitCGame` | `VM_Call(cgvm, CG_INIT, clc.serverMessageSequence, clc.lastExecutedServerCommand, clc.clientNum);` | `void CG_Init(int serverMessageSeq, int lastServerCommand, int clientNum);` | Replace implicit globals with explicit parameters (may expand to struct). 【F:src/code/client/cl_cgame.c†L764-L779】 |
| Shutdown | `CL_ShutdownCGame` – `src/code/client/cl_cgame.c` | `VM_Call(cgvm, CG_SHUTDOWN);` | `void CG_Shutdown(void);` | Ensure renderer callbacks are released safely when called from native DLL. 【F:src/code/client/cl_cgame.c†L404-L422】 |
| Rendering | `CL_CGameRendering` – `src/code/client/cl_cgame.c` | `VM_Call(cgvm, CG_DRAW_ACTIVE_FRAME, cl.serverTime, stereo, clc.demoplaying);` | `void CG_DrawActiveFrame(int serverTime, stereoFrame_t stereoView, qboolean demoPlaying);` | Stereo enum and demo state should become typed parameters. 【F:src/code/client/cl_cgame.c†L804-L816】 |
| Console command | `CL_GameCommand` – `src/code/client/cl_cgame.c` | `VM_Call(cgvm, CG_CONSOLE_COMMAND);` | `qboolean CG_ConsoleCommand(void);` | Still relies on command buffer globals; may require exported parser helper. 【F:src/code/client/cl_cgame.c†L792-L804】 |
| Event handling | `CL_KeyEvent` – `src/code/client/cl_keys.c` | `VM_Call(cgvm, CG_EVENT_HANDLING, CGAME_EVENT_NONE);` | `void CG_EventHandling(cgameEvent_t state);` | Called when closing CG UI overlays; share enums with native layer. 【F:src/code/client/cl_keys.c†L1108-L1118】 |
| Key input | `CL_KeyEvent` – `src/code/client/cl_keys.c` | `VM_Call(cgvm, CG_KEY_EVENT, key, down);` | `void CG_KeyEvent(int key, qboolean down);` | Preserve the recovered demo shortcut and console/browser/UI/message priority before cgame receives key events. 【F:src/code/client/cl_keys.c†L1361-L1525】 |
| Mouse input | `CL_MouseEvent` – `src/code/client/cl_input.c` | `VM_Call(cgvm, CG_MOUSE_EVENT, dx, dy);` | `void CG_MouseEvent(int dx, int dy);` | Preserve the recovered raw event payload after the `cg_ignoreMouseInput` and browser-keycatcher gates. 【F:src/code/client/cl_input.c†L368-L394】 |
| Target queries | `Con_MessageMode3_f`, `Con_MessageMode4_f` – `src/code/client/cl_console.c` | `VM_Call(cgvm, CG_CROSSHAIR_PLAYER);` / `VM_Call(cgvm, CG_LAST_ATTACKER);` | `int CG_CrosshairPlayer(void);` / `int CG_LastAttacker(void);` | Return sentinel `-1` is engine contract; preserve semantics. 【F:src/code/client/cl_console.c†L120-L142】 |

## Server game VM (`gvm`)
| Lifecycle | Location(s) | Current invocation | Proposed native entry (signature) | Notes / blockers |
| --- | --- | --- | --- | --- |
| Load | `SV_InitGameProgs` – `src/code/server/sv_game.c` | `gvm = VM_Create("qagame", SV_GameSystemCalls, Cvar_VariableValue("vm_game"));` | `bool G_Load(vmInterpret_t interpret, const gameImports_t *imports);` | Needs structured system call surface; must support restart semantics currently provided by `VM_Restart`. 【F:src/code/server/sv_game.c†L934-L964】 |
| Init | `SV_InitGameVM` – `src/code/server/sv_game.c` | `VM_Call(gvm, GAME_INIT, svs.time, Com_Milliseconds(), restart);` | `void G_InitGame(int levelTime, int randomSeed, qboolean restart);` | Must move `svs` time tracking into explicit arguments; ensure deterministic seeding. 【F:src/code/server/sv_game.c†L916-L942】 |
| Shutdown | `SV_ShutdownGameProgs` – `src/code/server/sv_game.c` | `VM_Call(gvm, GAME_SHUTDOWN, qfalse/qtrue);` | `void G_ShutdownGame(qboolean restart);` | Called for full shutdown and restart; confirm cleanup without VM_Free semantics. 【F:src/code/server/sv_game.c†L884-L938】 |
| Console command | `SV_GameCommand` – `src/code/server/sv_game.c` | `VM_Call(gvm, GAME_CONSOLE_COMMAND);` | `qboolean G_ConsoleCommand(void);` | Shares parser contract with engine; may need explicit command buffer pointer. 【F:src/code/server/sv_game.c†L972-L981】 |
| Frame loop | `SV_Frame`, `SV_MapRestart_f`, `SV_SpawnServer`, `SV_RestartGameProgs` – `sv_main.c`, `sv_ccmds.c`, `sv_init.c` | Repeated `VM_Call(gvm, GAME_RUN_FRAME, svs.time);` | `void G_RunFrame(int levelTime);` | Called multiple times per engine frame; ensure levelTime progression controlled by server, not inside game DLL. 【F:src/code/server/sv_main.c†L830-L848】【F:src/code/server/sv_ccmds.c†L268-L307】【F:src/code/server/sv_init.c†L440-L501】 |
| Client connect | `SV_DirectConnect`, restart flows – `sv_client.c`, `sv_ccmds.c`, `sv_init.c` | `VM_Call(gvm, GAME_CLIENT_CONNECT, clientNum, firstTime, isBot);` often wrapped with `VM_ExplicitArgPtr`. | `char *G_ClientConnect(int clientNum, qboolean firstTime, qboolean isBot);` returning pointer to static string or `NULL`. | Native path must expose ownership of denial string; currently relies on VM pointer marshalling (`VM_ExplicitArgPtr`). 【F:src/code/server/sv_client.c†L421-L441】【F:src/code/server/sv_ccmds.c†L298-L307】【F:src/code/server/sv_init.c†L465-L489】 |
| Client begin | `SV_ClientEnterWorld`, bot reconnect path – `sv_client.c`, `sv_init.c` | `VM_Call(gvm, GAME_CLIENT_BEGIN, clientNum);` | `void G_ClientBegin(int clientNum);` | Called after baselines; ensures entity setup. 【F:src/code/server/sv_client.c†L624-L640】【F:src/code/server/sv_init.c†L488-L499】 |
| Client disconnect | `SV_DropClient` – `sv_client.c` | `VM_Call(gvm, GAME_CLIENT_DISCONNECT, clientNum);` | `void G_ClientDisconnect(int clientNum);` | Must release entity references; occurs even for errored drops. 【F:src/code/server/sv_client.c†L495-L522】 |
| Client userinfo | `SV_UpdateUserinfo_f` – `sv_client.c` | `VM_Call(gvm, GAME_CLIENT_USERINFO_CHANGED, clientNum);` | `void G_ClientUserinfoChanged(int clientNum);` | After moving to native, consider passing parsed configstrings rather than relying on `Info_ValueForKey` inside game. 【F:src/code/server/sv_client.c†L1188-L1202】 |
| Client command | `SV_ExecuteClientCommand` – `sv_client.c` | `VM_Call(gvm, GAME_CLIENT_COMMAND, clientNum);` | `void G_ClientCommand(int clientNum);` | Shares command buffer; evaluate re-entrant safety when moving to native. 【F:src/code/server/sv_client.c†L1218-L1242】 |
| Client think | `SV_ClientThink` – `sv_client.c` | `VM_Call(gvm, GAME_CLIENT_THINK, clientNum);` | `void G_ClientThink(int clientNum);` | Called for each usercmd; consider passing `usercmd_t` pointer directly instead of implicit global access. 【F:src/code/server/sv_client.c†L1309-L1324】 |
| Bot frame | `SV_BotFrame` – `sv_bot.c` | `VM_Call(gvm, BOTAI_START_FRAME, time);` | `void BotAI_StartFrame(int msec);` | Requires exporting botlib hooks or integrating bot AI directly. 【F:src/code/server/sv_bot.c†L436-L452】 |

## Shared VM runtime (`qcommon`)
| Component | Location | Current responsibility | Native pipeline impact |
| --- | --- | --- | --- |
| VM creation | `VM_Create` – `src/code/qcommon/vm.c` | Loads QVM bytecode or DLL, tracks `vm_t` table, populates `vm->entryPoint`. | Native pipeline will bypass bytecode loader; keep registry but ensure DLL loader enforces signed/native binaries. 【F:src/code/qcommon/vm.c†L426-L520】 |
| VM restart | `VM_Restart` – `src/code/qcommon/vm.c` | Reconstructs a VM in-place for QVMs or re-calls `VM_Create` for DLL builds during map restarts. | Native DLLs must provide hot-reload semantics or support deterministic tear-down/reload so server restarts remain fast. 【F:src/code/qcommon/vm.c†L360-L385】 |
| VM dispatch | `VM_Call` – `src/code/qcommon/vm.c` | Marshals up to 16 int args through varargs and invokes `vm->entryPoint` or interpreter. | Replace with direct typed function pointers per module; remove vararg marshalling and `currentVM` global once legacy QVM path is gone. 【F:src/code/qcommon/vm.c†L668-L712】 |

## Implicit global dependencies and pointer bridges
| Call site | Evidence of implicit dependency | Required shim in native pipeline |
| --- | --- | --- |
| `CL_InitUI` → `VM_Call(uivm, UI_INIT, …)` | Call gate evaluates `cls.state` to decide in-game flag. 【F:src/code/client/cl_ui.c†L1169-L1182】 | Pass an explicit `uiContext_t` snapshot (connection state, in-game flag) instead of reading `cls` through imports. |
| `UI_GameCommand`/`UI_REFRESH`/`UI_DRAW_CONNECT_SCREEN` | Engine forwards `cls.realtime` to the UI for command filtering and draw timing. 【F:src/code/client/cl_ui.c†L1193-L1205】【F:src/code/client/cl_scrn.c†L476-L499】 | Add a `UiTimeImports` struct that carries frame time and menu ownership rather than sampling globals per call. |
| `CL_CGameRendering` → `VM_Call(cgvm, CG_DRAW_ACTIVE_FRAME, …)` | Render entry depends on `cl.serverTime`, stereo mode, and `clc.demoplaying`. 【F:src/code/client/cl_cgame.c†L804-L816】 | Replace varargs call with `CG_DrawActiveFrame(const cgFrameContext_t *ctx)` holding timing and demo flags. |
| `SV_InitGameVM`/`SV_Frame` | Game init and per-frame calls both push `svs.time` (mutated outside the VM). 【F:src/code/server/sv_game.c†L894-L910】【F:src/code/server/sv_main.c†L832-L838】 | Provide a server tick context struct so the DLL cannot desync its notion of time. |
| `SV_MapRestart_f`/`SV_SpawnServer` settle loops | Restart flow advances `svs.time` while replaying `GAME_RUN_FRAME`. 【F:src/code/server/sv_ccmds.c†L272-L317】【F:src/code/server/sv_init.c†L440-L500】 | Introduce restart helpers that batch time steps inside the engine and notify the DLL via explicit callbacks. |
| `SV_DirectConnect` | Connection rejection strings are recovered through `VM_ExplicitArgPtr`. 【F:src/code/server/sv_client.c†L546-L558】 | Define `G_ClientConnectResult` with owned buffers so the DLL returns structured outcomes without pointer reinterpretation. |
| `SV_MapRestart_f` client reconnect | Map restart reuses `VM_ExplicitArgPtr` on reconnect denial. 【F:src/code/server/sv_ccmds.c†L298-L307】 | Share the same `G_ClientConnectResult` struct and treat denial text as engine-owned storage. |
| `SV_SpawnServer` bot reconnect | Post-spawn loop unwraps denial pointers via `VM_ExplicitArgPtr`. 【F:src/code/server/sv_init.c†L440-L499】 | Extend reconnect helper to accept structured responses and skip pointer aliasing. |

## Blockers and shared utilities to migrate
* **System call tables**: Completed for the current source-built native DLL path. `CL_UISystemCalls`, `CL_CgameSystemCalls`, and `SV_GameSystemCalls` are now exposed through structured native import tables passed via the Quake Live-style `dllEntry` handshake instead of only through legacy VM trampolines. Further work here is validation against retail DLL expectations, not first-time plumbing.
* **Pointer-return ownership**: Retail-binary hosting still needs stricter validation around places that historically relied on VM pointer reinterpretation, especially denial strings from `G_ClientConnect`. The reconstructed source-built DLLs share the current engine conventions, but retail DLLs may still expose tighter ownership or lifetime assumptions. 【F:src/code/server/sv_client.c†L546-L558】【F:src/code/server/sv_ccmds.c†L298-L307】【F:src/code/server/sv_init.c†L440-L499】
* **Restart semantics**: `SV_RestartGameProgs` and `VM_Restart` work for the rebuilt source path, but retail-binary hosting still needs explicit validation that unload, reload, and map-restart behavior match the retail engine's expectations. 【F:src/code/server/sv_game.c†L922-L935】【F:src/code/qcommon/vm.c†L360-L385】
* **Module unload hooks**: `CL_ShutdownUI` and `SV_ShutdownGameProgs` already drive native DLL unload through the current VM wrapper layer, but stale-pointer/lifetime behavior should still be rechecked against retail binaries whenever host ownership rules are recovered more precisely. 【F:src/code/client/cl_ui.c†L1133-L1141】【F:src/code/server/sv_game.c†L882-L935】【F:src/code/qcommon/vm.c†L580-L604】
* **Global state access**: The current import surface intentionally preserves ambient engine-query behavior for compatibility. Removing the QVM seam entirely is still a separate cleanup task from retail native ABI parity.
* **Command buffer bridging**: Console command handlers still rely on the engine `Cmd_*` API through the import table, which is compatible with the current native ABI. Tightening that into explicit typed command descriptors is optional cleanup unless retail evidence shows a concrete mismatch. 【F:src/code/client/cl_ui.c†L1193-L1205】【F:src/code/client/cl_cgame.c†L792-L805】【F:src/code/server/sv_client.c†L1322-L1374】

