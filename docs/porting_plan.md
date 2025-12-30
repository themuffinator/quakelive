# Quake Live Porting Checklist and Backlog

This planning document consolidates the Quake Live vs. Quake III Arena HLIL comparison data into actionable migration work. Use it to track architectural alignment, reference the implementation touch points under `src/`, and seed backlog items for gameplay feature gaps.

## Architectural differences overview

| Difference | Quake III Arena behaviour | Quake Live behaviour | Impacted `src/` modules |
| --- | --- | --- | --- |
| VM dispatch vs. native DLL | Engine spawns the game VM via `VM_Create`, driven by `vm_game`/`vm_cgame` toggles and syscall trampolines. | Gameplay executes inside `qagamex86.dll`; no VM boundary, syscalls resolved locally. | `code/qcommon/vm.c`, `code/qcommon/cm_load.c`, `code/qcommon/q_shared.h` |
| Module bootstrap & config registration | DLL bytecode loaded at runtime; CVars registered inside VM entry points (`g_main.c` init). | Native DLL registers CVars directly in host process during load (e.g., `sub_10053400` configuring weapon CVars). | `code/game/g_main.c`, `code/game/g_syscalls.c`, `code/game/g_local.h` |
| Logging & authentication | CD key enforcement and limited client auth logging; CD checks in engine prior to VM hand-off. | Steam token validation, expanded connection logging, bot flag handling inside `ClientConnect`. | `code/server/sv_client.c`, `code/game/g_client.c`, `code/qcommon/net_chan.c` |

## Porting checklists

### 1. Native execution path (VM dispatch removal)
- [ ] Audit `code/qcommon/vm.c` for all call sites of `VM_Create`/`VM_Call`; document where direct DLL hooks are needed.
- [ ] Update loader seams in `code/server/sv_game.c` and `code/client/cl_cgame.c` to bypass bytecode expectations when a native module is present.
- [ ] Ensure `code/qcommon/cm_load.c` and related memory fences honour native pointer lifetimes (no bytecode relocation logic).
- [ ] Plan syscall surface parity by reviewing `code/game/g_syscalls.c` exports vs. direct native calls required by Quake Live.

### 2. Module bootstrap & configuration registration
- [ ] Catalogue CVar registration in `code/game/g_main.c` (`G_InitGame`, `G_RegisterCvars`) against Quake Live's `sub_10053400` expectations; flag missing `g_startingAmmo_*` entries.
- [ ] Extend `code/game/g_local.h` definitions to cover new configuration structs before wiring CVars.
- [ ] Map any engine-level fallbacks in `code/qcommon/cvar.c` needed to support the larger CVar set.
- [ ] Verify module load order via `code/server/sv_init.c` so config parsing occurs before client spawns.

### 3. Logging and authentication flow updates
- [ ] Introduce Steam/OpenID token hooks in `code/game/g_client.c::ClientConnect` mirroring HLIL logging strings.
- [ ] Add server-side verification shims within `code/server/sv_client.c` to surface auth failures before player instantiation.
- [ ] Review `code/qcommon/net_chan.c` (and `code/server/sv_main.c` messaging) for broadcast formatting needed for Steam IDs / analytics prints.
- [x] Confirm bot flag masking aligns with Quake Live by setting/clearing `SVF_BOT` in `code/game/g_client.c::ClientConnect` and syncing `client_t` handling in `code/server/sv_bot.c` and related structs.

## Gameplay feature backlog

| Item | Description | Owner | Prerequisites |
| --- | --- | --- | --- |
| CVar expansion sweep | Implement the `g_startingAmmo_*`, `weapon_reload_*`, `g_damage_g`, and `g_knockback_g` CVars with defaults matching Quake Live. | Gameplay Systems (A. Rivera) | Complete checklist 2 (CVar registration coverage) |
| Weapon tuning hooks | Port script-driven weapon tuning paths into `code/game/g_weapon.c` and `code/game/bg_pmove.c`, ensuring runtime CVar reads drive damage/spread. | Combat Mechanics (L. Chen) | "CVar expansion sweep" backlog item |
| Enhanced connection logging | Mirror Quake Live Steam logging (priv/broadcast messages) in `code/game/g_client.c` and `code/server/sv_main.c`. | Online Services (M. Patel) | Checklist 3 completion (logging/auth flow updates) |
| Bot connection parity | Align bot rejection/masking behaviour with HLIL (`ClientConnect` bot flag handling). Update `code/server/sv_bot.c` and shared client structs. | AI/Co-op (S. Nakamura) | Checklist 3 item "Confirm bot flag masking" |

Keep this document updated as HLIL annotations grow or as new discrepancies are discovered.
