# Source-File Parity Ledger

Last updated: 2026-05-20

## Purpose

This is the clean main parity document for the new source-file campaign. It keeps one concise row per tracked source file while leaving the detailed reasoning in the existing subsystem audits and in the new per-file gap notes.

The ledger does not replace the current gate-facing ledgers. `AUDIT.md`, `IMPLEMENTATION_PLAN.md`, and `repo-wide-parity-audit-2026-04-21.md` remain the high-level summary sources.

## Scope

- Tracked compilation units under `src/` excluding generated/vendor mirror trees under `src/libs/_deps/` and `src/libs/_build/`: `566` files.
- Header exception tracked because it owns a documented repo-wide divergence policy surface: `1` file.
- Total tracked source entries in this ledger: `567`.
- Function counts are approximate source-definition counts from the checked-in tree and are meant for audit triage, not for ABI accounting.

## Status legend

- `walked-closed`: The 2026-04-22 campaign has rerun the full file walk for this file and did not isolate a new file-level gap.
- `baseline-closed`: Subsystem or strict-retail closure already exists; this 2026-04-22 campaign has not yet rerun the full file walk.
- `documented-divergence`: The file has a dedicated note because it remains an intentional bounded compatibility divergence, not active parity debt.
- `gap-note-open`: A concrete file-level parity gap is already evidenced and has a dedicated note.
- `compatibility-open`: The file sits inside an open repo-wide compatibility or portability lane; a file-specific gap note will be added once the function walk isolates it.
- `queued-secondary`: The file belongs to a secondary tool, editor, compiler, or legacy support tree; it is catalogued now and queued after the primary runtime surface.

## Current totals

- `walked-closed`: `551` files
- `baseline-closed`: `0` files
- `documented-divergence`: `7` files
- `gap-note-open`: `9` files
- `compatibility-open`: `0` files
- `queued-secondary`: `0` files

## Documented divergence notes

| File | Gap family | Note |
| --- | --- | --- |
| `src/common/platform/platform_config.h` | `RW-G01` | [note](source-file-gap-notes/rw-g01-platform-config.md) |
| `src/common/platform/platform_services.c` | `RW-G01` | [note](source-file-gap-notes/rw-g01-platform-services.md) |
| `src/common/platform/backends/platform_backend_open_steam.c` | `RW-G01` | [note](source-file-gap-notes/rw-g01-open-steam-backend.md) |
| `src/common/platform/backends/platform_backend_steamworks.c` | `RW-G01` | [note](source-file-gap-notes/rw-g01-steamworks-backend.md) |
| `src/code/client/ql_auth.c` | `RW-G01` | [note](source-file-gap-notes/rw-g01-client-auth.md) |
| `src/code/client/cl_steam_resources.c` | `RW-G01` | [note](source-file-gap-notes/rw-g01-client-steam-resources.md) |
| `src/code/server/sv_rankings.c` | `RW-G01` | [note](source-file-gap-notes/rw-g01-server-rankings.md) |

## Active file-level gap notes

| File | Gap family | Note |
| --- | --- | --- |
| `src/code/unix/unix_main.c` | `RW-G02` | [note](source-file-gap-notes/rw-g02-unix-main.md) |
| `src/code/unix/linux_glimp.c` | `RW-G02` | [note](source-file-gap-notes/rw-g02-linux-glimp.md) |
| `src/code/unix/linux_snd.c` | `RW-G02` | [note](source-file-gap-notes/rw-g02-linux-snd.md) |
| `src/code/unix/linux_joystick.c` | `RW-G02` | [note](source-file-gap-notes/rw-g02-linux-joystick.md) |
| `src/code/null/null_main.c` | `RW-G02` | [note](source-file-gap-notes/rw-g02-null-main.md) |
| `src/code/null/null_glimp.c` | `RW-G02` | [note](source-file-gap-notes/rw-g02-null-glimp.md) |
| `src/code/null/null_client.c` | `RW-G02` | [note](source-file-gap-notes/rw-g02-null-client.md) |
| `src/code/null/null_input.c` | `RW-G02` | [note](source-file-gap-notes/rw-g02-null-input.md) |
| `src/code/null/null_snddma.c` | `RW-G02` | [note](source-file-gap-notes/rw-g02-null-snddma.md) |

## Primary Runtime And Reconstruction Surface

### `src/common` (18 files)

Current 2026-04-22 audit result: the `src/common` function walk did not
isolate any new file-level owners beyond the already-seeded `RW-G01`
policy/configuration surfaces. The retained `platform_steamworks.c`
wrapper family remains baseline-closed on current evidence; the
deliberate compatibility-only boundary still lives in
`platform_config.h`, `platform_services.c`, and the existing
auth/backend call sites.

| File | Functions | Current parity state | Primary evidence | Gap note |
| --- | ---: | --- | --- | --- |
| `src/common/aselib.c` | `25` | Current function walk complete; no new file-level gap isolated | [engine-wide closure](engine-full-parity-audit-and-implementation-plan-2026-04-10.md) + current 2026-04-22 source walk | - |
| `src/common/auth_credentials.c` | `11` | Current function walk complete; no new file-level gap isolated | [engine-wide closure](engine-full-parity-audit-and-implementation-plan-2026-04-10.md) + current 2026-04-22 source walk | - |
| `src/common/bspfile.c` | `17` | Current function walk complete; no new file-level gap isolated | [engine-wide closure](engine-full-parity-audit-and-implementation-plan-2026-04-10.md) + current 2026-04-22 source walk | - |
| `src/common/cmdlib.c` | `58` | Current function walk complete; no new file-level gap isolated | [engine-wide closure](engine-full-parity-audit-and-implementation-plan-2026-04-10.md) + current 2026-04-22 source walk | - |
| `src/common/imagelib.c` | `15` | Current function walk complete; no new file-level gap isolated | [engine-wide closure](engine-full-parity-audit-and-implementation-plan-2026-04-10.md) + current 2026-04-22 source walk | - |
| `src/common/l3dslib.c` | `5` | Current function walk complete; no new file-level gap isolated | [engine-wide closure](engine-full-parity-audit-and-implementation-plan-2026-04-10.md) + current 2026-04-22 source walk | - |
| `src/common/mathlib.c` | `25` | Current function walk complete; no new file-level gap isolated | [engine-wide closure](engine-full-parity-audit-and-implementation-plan-2026-04-10.md) + current 2026-04-22 source walk | - |
| `src/common/md4.c` | `7` | Current function walk complete; no new file-level gap isolated | [engine-wide closure](engine-full-parity-audit-and-implementation-plan-2026-04-10.md) + current 2026-04-22 source walk | - |
| `src/common/mutex.c` | `12` | Current function walk complete; no new file-level gap isolated | [engine-wide closure](engine-full-parity-audit-and-implementation-plan-2026-04-10.md) + current 2026-04-22 source walk | - |
| `src/common/platform/backends/platform_backend_open_steam.c` | `1` | RW-G01 documented divergence note | [repo-wide audit](repo-wide-parity-audit-2026-04-21.md) + [note](source-file-gap-notes/rw-g01-open-steam-backend.md) | [note](source-file-gap-notes/rw-g01-open-steam-backend.md) |
| `src/common/platform/backends/platform_backend_steamworks.c` | `1` | RW-G01 documented divergence note | [repo-wide audit](repo-wide-parity-audit-2026-04-21.md) + [note](source-file-gap-notes/rw-g01-steamworks-backend.md) | [note](source-file-gap-notes/rw-g01-steamworks-backend.md) |
| `src/common/platform/platform_services.c` | `9` | RW-G01 documented divergence note | [repo-wide audit](repo-wide-parity-audit-2026-04-21.md) + [note](source-file-gap-notes/rw-g01-platform-services.md) | [note](source-file-gap-notes/rw-g01-platform-services.md) |
| `src/common/platform/platform_steamworks.c` | `144` | Current function walk complete; no new file-level gap isolated | [engine-wide closure](engine-full-parity-audit-and-implementation-plan-2026-04-10.md) + current 2026-04-22 source walk | - |
| `src/common/polylib.c` | `17` | Current function walk complete; no new file-level gap isolated | [engine-wide closure](engine-full-parity-audit-and-implementation-plan-2026-04-10.md) + current 2026-04-22 source walk | - |
| `src/common/scriplib.c` | `14` | Current function walk complete; no new file-level gap isolated | [engine-wide closure](engine-full-parity-audit-and-implementation-plan-2026-04-10.md) + current 2026-04-22 source walk | - |
| `src/common/threads.c` | `19` | Current function walk complete; no new file-level gap isolated | [engine-wide closure](engine-full-parity-audit-and-implementation-plan-2026-04-10.md) + current 2026-04-22 source walk | - |
| `src/common/trilib.c` | `3` | Current function walk complete; no new file-level gap isolated | [engine-wide closure](engine-full-parity-audit-and-implementation-plan-2026-04-10.md) + current 2026-04-22 source walk | - |
| `src/common/platform/platform_config.h` | `n/a` | RW-G01 documented divergence note | [repo-wide audit](repo-wide-parity-audit-2026-04-21.md) + [note](source-file-gap-notes/rw-g01-platform-config.md) | [note](source-file-gap-notes/rw-g01-platform-config.md) |
### `src/code/client` (22 files)

Current 2026-04-22 audit result: the `src/code/client` function walk did
not isolate any new file-level owners beyond the already-seeded `RW-G01`
compatibility-policy notes. The strict-retail client register remains
closed on current evidence, while `ql_auth.c` and
`cl_steam_resources.c` continue to own the repo-wide bounded
online-services story inside this tree.

| File | Functions | Current parity state | Primary evidence | Gap note |
| --- | ---: | --- | --- | --- |
| `src/code/client/cl_cgame.c` | `194` | Current function walk complete; no new file-level gap isolated | [client audit](client-full-parity-audit-and-implementation-plan-2026-04-09.md) + current 2026-04-22 source walk | - |
| `src/code/client/cl_cin.c` | `46` | Current function walk complete; no new file-level gap isolated | [client audit](client-full-parity-audit-and-implementation-plan-2026-04-09.md) + current 2026-04-22 source walk | - |
| `src/code/client/cl_console.c` | `45` | Current function walk complete; no new file-level gap isolated | [client audit](client-full-parity-audit-and-implementation-plan-2026-04-09.md) + current 2026-04-22 source walk | - |
| `src/code/client/cl_input.c` | `80` | Current function walk complete; no new file-level gap isolated | [client audit](client-full-parity-audit-and-implementation-plan-2026-04-09.md) + current 2026-04-22 source walk | - |
| `src/code/client/cl_input_translation.c` | `3` | Current function walk complete; no new file-level gap isolated | [client audit](client-full-parity-audit-and-implementation-plan-2026-04-09.md) + current 2026-04-22 source walk | - |
| `src/code/client/cl_keys.c` | `37` | Current function walk complete; no new file-level gap isolated | [client audit](client-full-parity-audit-and-implementation-plan-2026-04-09.md) + current 2026-04-22 source walk | - |
| `src/code/client/cl_main.c` | `195` | Current function walk complete; no new file-level gap isolated | [client audit](client-full-parity-audit-and-implementation-plan-2026-04-09.md) + current 2026-04-22 source walk | - |
| `src/code/client/cl_net_chan.c` | `5` | Current function walk complete; no new file-level gap isolated | [client audit](client-full-parity-audit-and-implementation-plan-2026-04-09.md) + current 2026-04-22 source walk | - |
| `src/code/client/cl_parse.c` | `9` | Current function walk complete; no new file-level gap isolated | [client audit](client-full-parity-audit-and-implementation-plan-2026-04-09.md) + current 2026-04-22 source walk | - |
| `src/code/client/cl_screenshot_io.c` | `3` | Current function walk complete; no new file-level gap isolated | [client audit](client-full-parity-audit-and-implementation-plan-2026-04-09.md) + current 2026-04-22 source walk | - |
| `src/code/client/cl_scrn.c` | `18` | Current function walk complete; no new file-level gap isolated | [client audit](client-full-parity-audit-and-implementation-plan-2026-04-09.md) + current 2026-04-22 source walk | - |
| `src/code/client/cl_steam_resources.c` | `27` | RW-G01 documented divergence note | [repo-wide audit](repo-wide-parity-audit-2026-04-21.md) + [note](source-file-gap-notes/rw-g01-client-steam-resources.md) | [note](source-file-gap-notes/rw-g01-client-steam-resources.md) |
| `src/code/client/cl_ui.c` | `64` | Current function walk complete; no new file-level gap isolated | [client audit](client-full-parity-audit-and-implementation-plan-2026-04-09.md) + current 2026-04-22 source walk | - |
| `src/code/client/cl_webpak.c` | `28` | Current function walk complete; no new file-level gap isolated | [client audit](client-full-parity-audit-and-implementation-plan-2026-04-09.md) + current 2026-04-22 source walk | - |
| `src/code/client/ql_auth.c` | `18` | RW-G01 documented divergence note | [repo-wide audit](repo-wide-parity-audit-2026-04-21.md) + [note](source-file-gap-notes/rw-g01-client-auth.md) | [note](source-file-gap-notes/rw-g01-client-auth.md) |
| `src/code/client/snd_adpcm.c` | `4` | Current function walk complete; no new file-level gap isolated | [client audit](client-full-parity-audit-and-implementation-plan-2026-04-09.md) + current 2026-04-22 source walk | - |
| `src/code/client/snd_dma.c` | `57` | Current function walk complete; no new file-level gap isolated | [client audit](client-full-parity-audit-and-implementation-plan-2026-04-09.md) + current 2026-04-22 source walk | - |
| `src/code/client/snd_mem.c` | `17` | Current function walk complete; no new file-level gap isolated | [client audit](client-full-parity-audit-and-implementation-plan-2026-04-09.md) + current 2026-04-22 source walk | - |
| `src/code/client/snd_mix.c` | `8` | Current function walk complete; no new file-level gap isolated | [client audit](client-full-parity-audit-and-implementation-plan-2026-04-09.md) + current 2026-04-22 source walk | - |
| `src/code/client/snd_ogg_decode.c` | `5` | Current function walk complete; no new file-level gap isolated | [client audit](client-full-parity-audit-and-implementation-plan-2026-04-09.md) + current 2026-04-22 source walk | - |
| `src/code/client/snd_ogg_stream.c` | `20` | Current function walk complete; no new file-level gap isolated | [client audit](client-full-parity-audit-and-implementation-plan-2026-04-09.md) + current 2026-04-22 source walk | - |
| `src/code/client/snd_wavelet.c` | `9` | Current function walk complete; no new file-level gap isolated | [client audit](client-full-parity-audit-and-implementation-plan-2026-04-09.md) + current 2026-04-22 source walk | - |
### `src/code/cgame` (22 files)

Current 2026-04-22 audit result: the `src/code/cgame` function walk did
not isolate any new file-level owners inside the closed strict-retail
module register. The refreshed module audit, the focused cgame parity
lane (`199 passed`, `1 skipped`), and the shared native export helper
certification still bound this tree on current evidence, so no new
repo-wide gap note is opened here.

| File | Functions | Current parity state | Primary evidence | Gap note |
| --- | ---: | --- | --- | --- |
| `src/code/cgame/cg_consolecmds.c` | `69` | Current function walk complete; no file-level parity gap isolated | [module audit](game-module-parity-audit-and-implementation-plan-2026-04-10.md) + current 2026-04-22 source walk | - |
| `src/code/cgame/cg_draw.c` | `140` | Current function walk complete; no file-level parity gap isolated | [module audit](game-module-parity-audit-and-implementation-plan-2026-04-10.md) + current 2026-04-22 source walk | - |
| `src/code/cgame/cg_drawtools.c` | `28` | Current function walk complete; no file-level parity gap isolated | [module audit](game-module-parity-audit-and-implementation-plan-2026-04-10.md) + current 2026-04-22 source walk | - |
| `src/code/cgame/cg_effects.c` | `26` | Current function walk complete; no file-level parity gap isolated | [module audit](game-module-parity-audit-and-implementation-plan-2026-04-10.md) + current 2026-04-22 source walk | - |
| `src/code/cgame/cg_ents.c` | `38` | Current function walk complete; no file-level parity gap isolated | [module audit](game-module-parity-audit-and-implementation-plan-2026-04-10.md) + current 2026-04-22 source walk | - |
| `src/code/cgame/cg_event.c` | `51` | Current function walk complete; no file-level parity gap isolated | [module audit](game-module-parity-audit-and-implementation-plan-2026-04-10.md) + current 2026-04-22 source walk | - |
| `src/code/cgame/cg_info.c` | `11` | Current function walk complete; no file-level parity gap isolated | [module audit](game-module-parity-audit-and-implementation-plan-2026-04-10.md) + current 2026-04-22 source walk | - |
| `src/code/cgame/cg_localents.c` | `31` | Current function walk complete; no file-level parity gap isolated | [module audit](game-module-parity-audit-and-implementation-plan-2026-04-10.md) + current 2026-04-22 source walk | - |
| `src/code/cgame/cg_main.c` | `157` | Current function walk complete; no file-level parity gap isolated | [module audit](game-module-parity-audit-and-implementation-plan-2026-04-10.md) + current 2026-04-22 source walk | - |
| `src/code/cgame/cg_marks.c` | `6` | Current function walk complete; no file-level parity gap isolated | [module audit](game-module-parity-audit-and-implementation-plan-2026-04-10.md) + current 2026-04-22 source walk | - |
| `src/code/cgame/cg_newdraw.c` | `438` | Current function walk complete; no file-level parity gap isolated | [module audit](game-module-parity-audit-and-implementation-plan-2026-04-10.md) + current 2026-04-22 source walk | - |
| `src/code/cgame/cg_particles.c` | `24` | Current function walk complete; no file-level parity gap isolated | [module audit](game-module-parity-audit-and-implementation-plan-2026-04-10.md) + current 2026-04-22 source walk | - |
| `src/code/cgame/cg_players.c` | `66` | Current function walk complete; no file-level parity gap isolated | [module audit](game-module-parity-audit-and-implementation-plan-2026-04-10.md) + current 2026-04-22 source walk | - |
| `src/code/cgame/cg_playerstate.c` | `11` | Current function walk complete; no file-level parity gap isolated | [module audit](game-module-parity-audit-and-implementation-plan-2026-04-10.md) + current 2026-04-22 source walk | - |
| `src/code/cgame/cg_predict.c` | `15` | Current function walk complete; no file-level parity gap isolated | [module audit](game-module-parity-audit-and-implementation-plan-2026-04-10.md) + current 2026-04-22 source walk | - |
| `src/code/cgame/cg_scoreboard.c` | `27` | Current function walk complete; no file-level parity gap isolated | [module audit](game-module-parity-audit-and-implementation-plan-2026-04-10.md) + current 2026-04-22 source walk | - |
| `src/code/cgame/cg_screen.c` | `12` | Current function walk complete; no file-level parity gap isolated | [module audit](game-module-parity-audit-and-implementation-plan-2026-04-10.md) + current 2026-04-22 source walk | - |
| `src/code/cgame/cg_servercmds.c` | `129` | Current function walk complete; no file-level parity gap isolated | [module audit](game-module-parity-audit-and-implementation-plan-2026-04-10.md) + current 2026-04-22 source walk | - |
| `src/code/cgame/cg_snapshot.c` | `9` | Current function walk complete; no file-level parity gap isolated | [module audit](game-module-parity-audit-and-implementation-plan-2026-04-10.md) + current 2026-04-22 source walk | - |
| `src/code/cgame/cg_syscalls.c` | `132` | Current function walk complete; no file-level parity gap isolated | [module audit](game-module-parity-audit-and-implementation-plan-2026-04-10.md) + current 2026-04-22 source walk | - |
| `src/code/cgame/cg_view.c` | `35` | Current function walk complete; no file-level parity gap isolated | [module audit](game-module-parity-audit-and-implementation-plan-2026-04-10.md) + current 2026-04-22 source walk | - |
| `src/code/cgame/cg_weapons.c` | `74` | Current function walk complete; no file-level parity gap isolated | [module audit](game-module-parity-audit-and-implementation-plan-2026-04-10.md) + current 2026-04-22 source walk | - |
### `src/code/game` (45 files)

Current 2026-04-22 audit result: the `src/code/game` function walk did
not isolate any new file-level owners inside the closed strict-retail
module register. The refreshed module audit, the qagame retail gate, the
focused gameplay sweep, and the current auto-shuffle/countdown plus Clan
Arena shuffle regression lanes still bound this tree on current
evidence.

| File | Functions | Current parity state | Primary evidence | Gap note |
| --- | ---: | --- | --- | --- |
| `src/code/game/ai_chat.c` | `24` | Current function walk complete; no file-level parity gap isolated | [module audit](game-module-parity-audit-and-implementation-plan-2026-04-10.md) + current 2026-04-22 source walk | - |
| `src/code/game/ai_cmd.c` | `41` | Current function walk complete; no file-level parity gap isolated | [module audit](game-module-parity-audit-and-implementation-plan-2026-04-10.md) + current 2026-04-22 source walk | - |
| `src/code/game/ai_dmnet.c` | `35` | Current function walk complete; no file-level parity gap isolated | [module audit](game-module-parity-audit-and-implementation-plan-2026-04-10.md) + current 2026-04-22 source walk | - |
| `src/code/game/ai_dmq3.c` | `116` | Current function walk complete; no file-level parity gap isolated | [module audit](game-module-parity-audit-and-implementation-plan-2026-04-10.md) + current 2026-04-22 source walk | - |
| `src/code/game/ai_main.c` | `39` | Current function walk complete; no file-level parity gap isolated | [module audit](game-module-parity-audit-and-implementation-plan-2026-04-10.md) + current 2026-04-22 source walk | - |
| `src/code/game/ai_team.c` | `28` | Current function walk complete; no file-level parity gap isolated | [module audit](game-module-parity-audit-and-implementation-plan-2026-04-10.md) + current 2026-04-22 source walk | - |
| `src/code/game/ai_vcmd.c` | `16` | Current function walk complete; no file-level parity gap isolated | [module audit](game-module-parity-audit-and-implementation-plan-2026-04-10.md) + current 2026-04-22 source walk | - |
| `src/code/game/bg_lib.c` | `33` | Current function walk complete; no file-level parity gap isolated | [module audit](game-module-parity-audit-and-implementation-plan-2026-04-10.md) + current 2026-04-22 source walk | - |
| `src/code/game/bg_misc.c` | `37` | 2026-05-19 re-audit closed the armor pickup branch mismatch, corrected the qagame `0x1002CE00` helper label to `BG_CanGrabArmorItem`, refreshed the `BG_PlayerTouchesItem` touch-bounds evidence, restored the retail `TR_QL_ACCEL` trajectory branch, normalized the cgame `0x10001170` lookup label to `BG_FindItemByTypeAndTag`, corrected the cgame pickup-gate switch evidence, and added executable coverage for armor pickup, tier rebuild, regen targets, type-6 trajectory evaluation, weapon/holdable tag bridge numbering, the full weapon stat table, pickup/classname/type-tag lookup helpers, persistent-powerup guards, health/armor upper bounds, armor-tier clearing, predictable events, jump pads, playerstate event projection, and playerstate-to-entitystate visibility/replication fields | [module audit](game-module-parity-audit-and-implementation-plan-2026-04-10.md) + [BG-B armor note](cgame-bg-parity-implementation-plan.md#2026-05-19-bg-misc-armor-pickup-re-audit) | - |
| `src/code/game/bg_pmove.c` | `64` | Current function walk complete; no file-level parity gap isolated | [module audit](game-module-parity-audit-and-implementation-plan-2026-04-10.md) + current 2026-04-22 source walk | - |
| `src/code/game/bg_slidemove.c` | `9` | Current function walk complete; no file-level parity gap isolated | [module audit](game-module-parity-audit-and-implementation-plan-2026-04-10.md) + current 2026-04-22 source walk | - |
| `src/code/game/g_active.c` | `65` | Current function walk complete; no file-level parity gap isolated | [module audit](game-module-parity-audit-and-implementation-plan-2026-04-10.md) + current 2026-04-22 source walk | - |
| `src/code/game/g_arenas.c` | `8` | Current function walk complete; no file-level parity gap isolated | [module audit](game-module-parity-audit-and-implementation-plan-2026-04-10.md) + current 2026-04-22 source walk | - |
| `src/code/game/g_autoshuffle.c` | `7` | Current function walk complete; no file-level parity gap isolated | [module audit](game-module-parity-audit-and-implementation-plan-2026-04-10.md) + current 2026-04-22 source walk | - |
| `src/code/game/g_bot.c` | `27` | Current function walk complete; no file-level parity gap isolated | [module audit](game-module-parity-audit-and-implementation-plan-2026-04-10.md) + current 2026-04-22 source walk | - |
| `src/code/game/g_client.c` | `77` | Current function walk complete; no file-level parity gap isolated | [module audit](game-module-parity-audit-and-implementation-plan-2026-04-10.md) + current 2026-04-22 source walk | - |
| `src/code/game/g_cmds.c` | `159` | 2026-05-19 re-audit tightened the `Cmd_Forfeit_f` / `G_CanForfeit` split so the command wrapper only handles pause/countdown rejection while the shared forfeit gate owns the retail duel surrender `-999` score marker before `g_main.c::G_ApplyForfeit` runs | [module audit](game-module-parity-audit-and-implementation-plan-2026-04-10.md) + current 2026-05-19 source walk | - |
| `src/code/game/g_combat.c` | `41` | Current function walk complete; no file-level parity gap isolated | [module audit](game-module-parity-audit-and-implementation-plan-2026-04-10.md) + current 2026-04-22 source walk | - |
| `src/code/game/g_entity.c` | `0` | Current function walk complete; no file-level parity gap isolated | [module audit](game-module-parity-audit-and-implementation-plan-2026-04-10.md) + current 2026-04-22 source walk | - |
| `src/code/game/g_factory.c` | `26` | Current function walk complete; no file-level parity gap isolated | [module audit](game-module-parity-audit-and-implementation-plan-2026-04-10.md) + current 2026-04-22 source walk | - |
| `src/code/game/g_freeze.c` | `7` | Current function walk complete; no file-level parity gap isolated | [module audit](game-module-parity-audit-and-implementation-plan-2026-04-10.md) + current 2026-04-22 source walk | - |
| `src/code/game/g_items.c` | `74` | Current function walk complete; no file-level parity gap isolated | [module audit](game-module-parity-audit-and-implementation-plan-2026-04-10.md) + current 2026-04-22 source walk | - |
| `src/code/game/g_main.c` | `198` | 2026-05-19 re-audit preserved the recovered `G_CountAndSortConnectedClients` helper boundary at `0x10055FA0`, confirmed `G_FindNextTournamentPlayer` is now a real `AddTournamentPlayer` dependency, named the retail `G_RunThink` `ent + 0x2FC` callback as `runFrame` in the source overlay, restored the `G_UpdateCustomSettingsMaskForCvar` cvar-table helper boundary used by registration/update, revalidated `CheckVote`/intermission wiring through the real `g_vote.c` helper trio, tightened the init/frame calls into the retail `G_UpdateTeamCountConfigstrings` publisher, rechecked the `G_CanForfeit` to `G_ApplyForfeit` shared exit path, guarded the `G_CheckAutoRecord` frame hook's sentinel/start/stop/delayed-screenshot split, promoted the `G_UpdateAwardConfigstrings` tail to a preserved source helper, guarded the overtime/sudden-death exit-rule helper chain, pinned the `G_SelectNextMapVoteSlot` empty-slot/tie-break rules consumed by `ExitLevel`, locked the `G_CheckTimeoutExpired` pause-delta/reset/match-state republish handoff, tightened the `G_InitGame` timeout/overtime/match-state bootstrap corridor, and guarded the `LogExit` one-shot `PLAYER_STATS`/match-report handoff while retaining the existing init/run-frame/intermission wiring | [module audit](game-module-parity-audit-and-implementation-plan-2026-04-10.md) + current 2026-05-19 source walk | - |
| `src/code/game/g_match_state.c` | `9` | 2026-05-19 re-audit matched `G_UpdateTeamCountConfigstrings` to the HLIL last-publish `> 250 ms` cadence and preserved the `0x297`/`0x298` raw-roster versus active-player count policy used by `g_main.c` init/frame wiring | [module audit](game-module-parity-audit-and-implementation-plan-2026-04-10.md) + current 2026-05-19 source walk | - |
| `src/code/game/g_mem.c` | `3` | Current function walk complete; no file-level parity gap isolated | [module audit](game-module-parity-audit-and-implementation-plan-2026-04-10.md) + current 2026-04-22 source walk | - |
| `src/code/game/g_misc.c` | `24` | Current function walk complete; no file-level parity gap isolated | [module audit](game-module-parity-audit-and-implementation-plan-2026-04-10.md) + current 2026-04-22 source walk | - |
| `src/code/game/g_missile.c` | `27` | Current function walk complete; no file-level parity gap isolated | [module audit](game-module-parity-audit-and-implementation-plan-2026-04-10.md) + current 2026-04-22 source walk | - |
| `src/code/game/g_mover.c` | `39` | Current function walk complete; no file-level parity gap isolated | [module audit](game-module-parity-audit-and-implementation-plan-2026-04-10.md) + current 2026-04-22 source walk | - |
| `src/code/game/g_pmove.c` | `18` | Current function walk complete; no file-level parity gap isolated | [module audit](game-module-parity-audit-and-implementation-plan-2026-04-10.md) + current 2026-04-22 source walk | - |
| `src/code/game/g_race.c` | `46` | Current function walk complete; no file-level parity gap isolated | [module audit](game-module-parity-audit-and-implementation-plan-2026-04-10.md) + current 2026-04-22 source walk | - |
| `src/code/game/g_rankings.c` | `17` | Current function walk complete; no file-level parity gap isolated | [module audit](game-module-parity-audit-and-implementation-plan-2026-04-10.md) + current 2026-04-22 source walk | - |
| `src/code/game/g_rr.c` | `6` | Current function walk complete; no file-level parity gap isolated | [module audit](game-module-parity-audit-and-implementation-plan-2026-04-10.md) + current 2026-04-22 source walk | - |
| `src/code/game/g_session.c` | `4` | Current function walk complete; no file-level parity gap isolated | [module audit](game-module-parity-audit-and-implementation-plan-2026-04-10.md) + current 2026-04-22 source walk | - |
| `src/code/game/g_spawn.c` | `39` | Current function walk complete; no file-level parity gap isolated | [module audit](game-module-parity-audit-and-implementation-plan-2026-04-10.md) + current 2026-04-22 source walk | - |
| `src/code/game/g_svcmds.c` | `20` | Current function walk complete; no file-level parity gap isolated | [module audit](game-module-parity-audit-and-implementation-plan-2026-04-10.md) + current 2026-04-22 source walk | - |
| `src/code/game/g_svcmds_new.c` | `3` | Current function walk complete; no file-level parity gap isolated | [module audit](game-module-parity-audit-and-implementation-plan-2026-04-10.md) + current 2026-04-22 source walk | - |
| `src/code/game/g_syscalls.c` | `205` | Current function walk complete; no file-level parity gap isolated | [module audit](game-module-parity-audit-and-implementation-plan-2026-04-10.md) + current 2026-04-22 source walk | - |
| `src/code/game/g_target.c` | `34` | Current function walk complete; no file-level parity gap isolated | [module audit](game-module-parity-audit-and-implementation-plan-2026-04-10.md) + current 2026-04-22 source walk | - |
| `src/code/game/g_team.c` | `143` | Current function walk complete; no file-level parity gap isolated | [module audit](game-module-parity-audit-and-implementation-plan-2026-04-10.md) + current 2026-04-22 source walk | - |
| `src/code/game/g_trigger.c` | `24` | Current function walk complete; no file-level parity gap isolated | [module audit](game-module-parity-audit-and-implementation-plan-2026-04-10.md) + current 2026-04-22 source walk | - |
| `src/code/game/g_utils.c` | `33` | Current function walk complete; no file-level parity gap isolated | [module audit](game-module-parity-audit-and-implementation-plan-2026-04-10.md) + current 2026-04-22 source walk | - |
| `src/code/game/g_vote.c` | `9` | Current function walk complete; no file-level parity gap isolated | [module audit](game-module-parity-audit-and-implementation-plan-2026-04-10.md) + current 2026-04-22 source walk | - |
| `src/code/game/g_weapon.c` | `40` | Current function walk complete; no file-level parity gap isolated | [module audit](game-module-parity-audit-and-implementation-plan-2026-04-10.md) + current 2026-04-22 source walk | - |
| `src/code/game/q_math.c` | `58` | Current function walk complete; no file-level parity gap isolated | [module audit](game-module-parity-audit-and-implementation-plan-2026-04-10.md) + current 2026-04-22 source walk | - |
| `src/code/game/q_shared.c` | `61` | Current function walk complete; no file-level parity gap isolated | [module audit](game-module-parity-audit-and-implementation-plan-2026-04-10.md) + current 2026-04-22 source walk | - |
### `src/code/qcommon` (19 files)

Current 2026-04-22 audit result: the `src/code/qcommon` function walk did
not isolate any new file-level owners inside the closed strict-retail
`qcommon` register. The refreshed qcommon audit and the current runtime
proof lane still bound the tree on current evidence, while `vm_x86.c`
remains the already-documented compatibility carry beneath the closed
`vm.c` host-selection seam rather than a new repo-wide or subsystem gap
owner.

| File | Functions | Current parity state | Primary evidence | Gap note |
| --- | ---: | --- | --- | --- |
| `src/code/qcommon/cm_load.c` | `28` | Current function walk complete; no file-level parity gap isolated | [qcommon audit](qcommon-full-parity-audit-and-implementation-plan-2026-04-10.md) + current 2026-04-22 source walk | - |
| `src/code/qcommon/cm_patch.c` | `27` | Current function walk complete; no file-level parity gap isolated | [qcommon audit](qcommon-full-parity-audit-and-implementation-plan-2026-04-10.md) + current 2026-04-22 source walk | - |
| `src/code/qcommon/cm_polylib.c` | `17` | Current function walk complete; no file-level parity gap isolated | [qcommon audit](qcommon-full-parity-audit-and-implementation-plan-2026-04-10.md) + current 2026-04-22 source walk | - |
| `src/code/qcommon/cm_test.c` | `15` | Current function walk complete; no file-level parity gap isolated | [qcommon audit](qcommon-full-parity-audit-and-implementation-plan-2026-04-10.md) + current 2026-04-22 source walk | - |
| `src/code/qcommon/cm_trace.c` | `23` | Current function walk complete; no file-level parity gap isolated | [qcommon audit](qcommon-full-parity-audit-and-implementation-plan-2026-04-10.md) + current 2026-04-22 source walk | - |
| `src/code/qcommon/cmd.c` | `30` | Current function walk complete; no file-level parity gap isolated | [qcommon audit](qcommon-full-parity-audit-and-implementation-plan-2026-04-10.md) + current 2026-04-22 source walk | - |
| `src/code/qcommon/common.c` | `106` | Current function walk complete; no file-level parity gap isolated | [qcommon audit](qcommon-full-parity-audit-and-implementation-plan-2026-04-10.md) + current 2026-04-22 source walk | - |
| `src/code/qcommon/cvar.c` | `45` | Current function walk complete; no file-level parity gap isolated | [qcommon audit](qcommon-full-parity-audit-and-implementation-plan-2026-04-10.md) + current 2026-04-22 source walk | - |
| `src/code/qcommon/files.c` | `105` | Current function walk complete; no file-level parity gap isolated | [qcommon audit](qcommon-full-parity-audit-and-implementation-plan-2026-04-10.md) + current 2026-04-22 source walk | - |
| `src/code/qcommon/huffman.c` | `18` | Current function walk complete; no file-level parity gap isolated | [qcommon audit](qcommon-full-parity-audit-and-implementation-plan-2026-04-10.md) + current 2026-04-22 source walk | - |
| `src/code/qcommon/md4.c` | `8` | Current function walk complete; no file-level parity gap isolated | [qcommon audit](qcommon-full-parity-audit-and-implementation-plan-2026-04-10.md) + current 2026-04-22 source walk | - |
| `src/code/qcommon/msg.c` | `48` | Current function walk complete; no file-level parity gap isolated | [qcommon audit](qcommon-full-parity-audit-and-implementation-plan-2026-04-10.md) + current 2026-04-22 source walk | - |
| `src/code/qcommon/net_chan.c` | `19` | Current function walk complete; no file-level parity gap isolated | [qcommon audit](qcommon-full-parity-audit-and-implementation-plan-2026-04-10.md) + current 2026-04-22 source walk | - |
| `src/code/qcommon/unzip.c` | `48` | Current function walk complete; no file-level parity gap isolated | [qcommon audit](qcommon-full-parity-audit-and-implementation-plan-2026-04-10.md) + current 2026-04-22 source walk | - |
| `src/code/qcommon/vm.c` | `33` | Current function walk complete; no file-level parity gap isolated | [qcommon audit](qcommon-full-parity-audit-and-implementation-plan-2026-04-10.md) + current 2026-04-22 source walk | - |
| `src/code/qcommon/vm_interpreted.c` | `5` | Current function walk complete; no file-level parity gap isolated | [qcommon audit](qcommon-full-parity-audit-and-implementation-plan-2026-04-10.md) + current 2026-04-22 source walk | - |
| `src/code/qcommon/vm_ppc.c` | `15` | Current function walk complete; no file-level parity gap isolated | [qcommon audit](qcommon-full-parity-audit-and-implementation-plan-2026-04-10.md) + current 2026-04-22 source walk | - |
| `src/code/qcommon/vm_ppc_new.c` | `19` | Current function walk complete; no file-level parity gap isolated | [qcommon audit](qcommon-full-parity-audit-and-implementation-plan-2026-04-10.md) + current 2026-04-22 source walk | - |
| `src/code/qcommon/vm_x86.c` | `15` | Current function walk complete; no file-level parity gap isolated | [qcommon audit](qcommon-full-parity-audit-and-implementation-plan-2026-04-10.md) + current 2026-04-22 source walk | - |
### `src/code/renderer` (23 files)

Current 2026-04-22 audit result plus 2026-05-20 renderer wiring refresh:
the `src/code/renderer` function walk did not isolate any new file-level
owners inside the closed strict-retail `renderer` register. The retained
export, image, post-process, scene/runtime, font, and host-text closures
still hold on current evidence. The 2026-05-20 renderer refresh also restored
direct `GL_ALPHA` retained-atlas uploads and the retail `REF_API_VERSION == 9`
/ `0x9c` `GetRefAPI` tail, while the stale `R_fonsErrorCallback`
module-runtime artifact remains part of `RW-G04` evidence freshness rather
than a new renderer source-gap owner.

| File | Functions | Current parity state | Primary evidence | Gap note |
| --- | ---: | --- | --- | --- |
| `src/code/renderer/tr_animation.c` | `2` | Current function walk complete; no file-level parity gap isolated | [renderer audit](renderer-full-parity-audit-and-implementation-plan-2026-04-09.md) + current 2026-04-22 source walk | - |
| `src/code/renderer/tr_backend.c` | `74` | Current function walk complete; no file-level parity gap isolated | [renderer audit](renderer-full-parity-audit-and-implementation-plan-2026-04-09.md) + current 2026-04-22 source walk | - |
| `src/code/renderer/tr_bsp.c` | `31` | Current function walk complete; no file-level parity gap isolated | [renderer audit](renderer-full-parity-audit-and-implementation-plan-2026-04-09.md) + current 2026-04-22 source walk | - |
| `src/code/renderer/tr_cmds.c` | `12` | Current function walk complete; no file-level parity gap isolated | [renderer audit](renderer-full-parity-audit-and-implementation-plan-2026-04-09.md) + current 2026-04-22 source walk | - |
| `src/code/renderer/tr_curve.c` | `12` | Current function walk complete; no file-level parity gap isolated | [renderer audit](renderer-full-parity-audit-and-implementation-plan-2026-04-09.md) + current 2026-04-22 source walk | - |
| `src/code/renderer/tr_flares.c` | `6` | Current function walk complete; no file-level parity gap isolated | [renderer audit](renderer-full-parity-audit-and-implementation-plan-2026-04-09.md) + current 2026-04-22 source walk | - |
| `src/code/renderer/tr_font.c` | `65` | Current function walk complete; no file-level parity gap isolated | [renderer audit](renderer-full-parity-audit-and-implementation-plan-2026-04-09.md) + current 2026-04-22 source walk | - |
| `src/code/renderer/tr_image.c` | `58` | Current function walk complete; no file-level parity gap isolated | [renderer audit](renderer-full-parity-audit-and-implementation-plan-2026-04-09.md) + current 2026-04-22 source walk | - |
| `src/code/renderer/tr_init.c` | `31` | Current function walk complete; no file-level parity gap isolated | [renderer audit](renderer-full-parity-audit-and-implementation-plan-2026-04-09.md) + current 2026-04-22 source walk | - |
| `src/code/renderer/tr_light.c` | `6` | Current function walk complete; no file-level parity gap isolated | [renderer audit](renderer-full-parity-audit-and-implementation-plan-2026-04-09.md) + current 2026-04-22 source walk | - |
| `src/code/renderer/tr_main.c` | `32` | Current function walk complete; no file-level parity gap isolated | [renderer audit](renderer-full-parity-audit-and-implementation-plan-2026-04-09.md) + current 2026-04-22 source walk | - |
| `src/code/renderer/tr_marks.c` | `4` | Current function walk complete; no file-level parity gap isolated | [renderer audit](renderer-full-parity-audit-and-implementation-plan-2026-04-09.md) + current 2026-04-22 source walk | - |
| `src/code/renderer/tr_mesh.c` | `5` | Current function walk complete; no file-level parity gap isolated | [renderer audit](renderer-full-parity-audit-and-implementation-plan-2026-04-09.md) + current 2026-04-22 source walk | - |
| `src/code/renderer/tr_model.c` | `11` | Current function walk complete; no file-level parity gap isolated | [renderer audit](renderer-full-parity-audit-and-implementation-plan-2026-04-09.md) + current 2026-04-22 source walk | - |
| `src/code/renderer/tr_noise.c` | `3` | Current function walk complete; no file-level parity gap isolated | [renderer audit](renderer-full-parity-audit-and-implementation-plan-2026-04-09.md) + current 2026-04-22 source walk | - |
| `src/code/renderer/tr_scene.c` | `10` | Current function walk complete; no file-level parity gap isolated | [renderer audit](renderer-full-parity-audit-and-implementation-plan-2026-04-09.md) + current 2026-04-22 source walk | - |
| `src/code/renderer/tr_shade.c` | `18` | Current function walk complete; no file-level parity gap isolated | [renderer audit](renderer-full-parity-audit-and-implementation-plan-2026-04-09.md) + current 2026-04-22 source walk | - |
| `src/code/renderer/tr_shade_calc.c` | `32` | Current function walk complete; no file-level parity gap isolated | [renderer audit](renderer-full-parity-audit-and-implementation-plan-2026-04-09.md) + current 2026-04-22 source walk | - |
| `src/code/renderer/tr_shader.c` | `35` | Current function walk complete; no file-level parity gap isolated | [renderer audit](renderer-full-parity-audit-and-implementation-plan-2026-04-09.md) + current 2026-04-22 source walk | - |
| `src/code/renderer/tr_shadows.c` | `6` | Current function walk complete; no file-level parity gap isolated | [renderer audit](renderer-full-parity-audit-and-implementation-plan-2026-04-09.md) + current 2026-04-22 source walk | - |
| `src/code/renderer/tr_sky.c` | `13` | Current function walk complete; no file-level parity gap isolated | [renderer audit](renderer-full-parity-audit-and-implementation-plan-2026-04-09.md) + current 2026-04-22 source walk | - |
| `src/code/renderer/tr_surface.c` | `25` | Current function walk complete; no file-level parity gap isolated | [renderer audit](renderer-full-parity-audit-and-implementation-plan-2026-04-09.md) + current 2026-04-22 source walk | - |
| `src/code/renderer/tr_world.c` | `18` | Current function walk complete; no file-level parity gap isolated | [renderer audit](renderer-full-parity-audit-and-implementation-plan-2026-04-09.md) + current 2026-04-22 source walk | - |
### `src/code/server` (11 files)

Current 2026-04-22 audit result: the `src/code/server` function walk did
not isolate any new file-level owners beyond the already-seeded `RW-G01`
ownership note for `sv_rankings.c`. The strict-retail server register
remains closed on current evidence, while the retained rankings policy
surface stays bounded in its existing per-file note instead of reopening
the subsystem.

| File | Functions | Current parity state | Primary evidence | Gap note |
| --- | ---: | --- | --- | --- |
| `src/code/server/sv_bot.c` | `30` | Current function walk complete; no new file-level gap isolated | [server audit](server-full-parity-audit-and-implementation-plan-2026-04-10.md) + current 2026-04-22 source walk | - |
| `src/code/server/sv_ccmds.c` | `78` | Current function walk complete; no new file-level gap isolated | [server audit](server-full-parity-audit-and-implementation-plan-2026-04-10.md) + current 2026-04-22 source walk | - |
| `src/code/server/sv_client.c` | `70` | Current function walk complete; no new file-level gap isolated | [server audit](server-full-parity-audit-and-implementation-plan-2026-04-10.md) + current 2026-04-22 source walk | - |
| `src/code/server/sv_game.c` | `47` | Current function walk complete; no new file-level gap isolated | [server audit](server-full-parity-audit-and-implementation-plan-2026-04-10.md) + current 2026-04-22 source walk | - |
| `src/code/server/sv_init.c` | `28` | Current function walk complete; no new file-level gap isolated | [server audit](server-full-parity-audit-and-implementation-plan-2026-04-10.md) + current 2026-04-22 source walk | - |
| `src/code/server/sv_main.c` | `41` | Current function walk complete; no new file-level gap isolated | [server audit](server-full-parity-audit-and-implementation-plan-2026-04-10.md) + current 2026-04-22 source walk | - |
| `src/code/server/sv_net_chan.c` | `5` | Current function walk complete; no new file-level gap isolated | [server audit](server-full-parity-audit-and-implementation-plan-2026-04-10.md) + current 2026-04-22 source walk | - |
| `src/code/server/sv_rankings.c` | `42` | RW-G01 documented divergence note | [repo-wide audit](repo-wide-parity-audit-2026-04-21.md) + [note](source-file-gap-notes/rw-g01-server-rankings.md) | [note](source-file-gap-notes/rw-g01-server-rankings.md) |
| `src/code/server/sv_snapshot.c` | `11` | Current function walk complete; no new file-level gap isolated | [server audit](server-full-parity-audit-and-implementation-plan-2026-04-10.md) + current 2026-04-22 source walk | - |
| `src/code/server/sv_world.c` | `12` | Current function walk complete; no new file-level gap isolated | [server audit](server-full-parity-audit-and-implementation-plan-2026-04-10.md) + current 2026-04-22 source walk | - |
| `src/code/server/sv_zmq.c` | `45` | Current function walk complete; no new file-level gap isolated | [server audit](server-full-parity-audit-and-implementation-plan-2026-04-10.md) + current 2026-04-22 source walk | - |
### `src/code/ui` (9 files)

Current 2026-04-22 audit result: the read-only `src/code/ui` function
walk did not isolate any new file-level owners inside the closed
strict-retail UI register. The refreshed UI audit, the focused UI
parity lane (`56 passed`, `2 skipped`), the clean read-only `src/ui`
runtime-panel parity proof, and the bundle/runtime evidence still bound
this tree on current evidence, so no new repo-wide gap note is opened
here.

| File | Functions | Current parity state | Primary evidence | Gap note |
| --- | ---: | --- | --- | --- |
| `src/code/ui/ui_atoms.c` | `40` | Current read-only function walk complete; no file-level parity gap isolated | [ui audit](ui-full-parity-audit-and-implementation-plan-2026-04-05.md) + current 2026-04-22 source walk | - |
| `src/code/ui/ui_cdkey.c` | `8` | Current read-only function walk complete; no file-level parity gap isolated | [ui audit](ui-full-parity-audit-and-implementation-plan-2026-04-05.md) + current 2026-04-22 source walk | - |
| `src/code/ui/ui_gameinfo.c` | `18` | Current read-only function walk complete; no file-level parity gap isolated | [ui audit](ui-full-parity-audit-and-implementation-plan-2026-04-05.md) + current 2026-04-22 source walk | - |
| `src/code/ui/ui_main.c` | `260` | Current read-only function walk complete; no file-level parity gap isolated | [ui audit](ui-full-parity-audit-and-implementation-plan-2026-04-05.md) + current 2026-04-22 source walk | - |
| `src/code/ui/ui_players.c` | `28` | Current read-only function walk complete; no file-level parity gap isolated | [ui audit](ui-full-parity-audit-and-implementation-plan-2026-04-05.md) + current 2026-04-22 source walk | - |
| `src/code/ui/ui_quakelive_bridge.c` | `9` | Current read-only function walk complete; no file-level parity gap isolated | [ui audit](ui-full-parity-audit-and-implementation-plan-2026-04-05.md) + current 2026-04-22 source walk | - |
| `src/code/ui/ui_shared.c` | `321` | Current read-only function walk complete; no file-level parity gap isolated | [ui audit](ui-full-parity-audit-and-implementation-plan-2026-04-05.md) + current 2026-04-22 source walk | - |
| `src/code/ui/ui_syscalls.c` | `105` | Current read-only function walk complete; no file-level parity gap isolated | [ui audit](ui-full-parity-audit-and-implementation-plan-2026-04-05.md) + current 2026-04-22 source walk | - |
| `src/code/ui/ui_util.c` | `0` | Current read-only function walk complete; no file-level parity gap isolated | [ui audit](ui-full-parity-audit-and-implementation-plan-2026-04-05.md) + current 2026-04-22 source walk | - |
### `src/code/win32` (11 files)

Current 2026-04-22 audit result: the `src/code/win32` function walk did
not isolate any new file-level owners inside the closed strict-retail
Windows platform register. The retained clipboard, raw-input,
loading-window, renderer-host glue, and `win_glimp.c` pixel-format
closures still hold on current evidence.

| File | Functions | Current parity state | Primary evidence | Gap note |
| --- | ---: | --- | --- | --- |
| `src/code/win32/awesomium_process.cpp` | `2` | Current function walk complete; no file-level parity gap isolated | [platform-specific audit](platform-specific-engine-parity-audit-and-implementation-plan-2026-04-16.md) + current 2026-04-22 source walk | - |
| `src/code/win32/win_gamma.c` | `4` | Current function walk complete; no file-level parity gap isolated | [platform-specific audit](platform-specific-engine-parity-audit-and-implementation-plan-2026-04-16.md) + current 2026-04-22 source walk | - |
| `src/code/win32/win_glimp.c` | `26` | Current function walk complete; no file-level parity gap isolated | [platform-specific audit](platform-specific-engine-parity-audit-and-implementation-plan-2026-04-16.md) + current 2026-04-22 source walk | - |
| `src/code/win32/win_input.c` | `45` | Current function walk complete; no file-level parity gap isolated | [platform-specific audit](platform-specific-engine-parity-audit-and-implementation-plan-2026-04-16.md) + current 2026-04-22 source walk | - |
| `src/code/win32/win_main.c` | `48` | Current function walk complete; no file-level parity gap isolated | [platform-specific audit](platform-specific-engine-parity-audit-and-implementation-plan-2026-04-16.md) + current 2026-04-22 source walk | - |
| `src/code/win32/win_net.c` | `21` | Current function walk complete; no file-level parity gap isolated | [platform-specific audit](platform-specific-engine-parity-audit-and-implementation-plan-2026-04-16.md) + current 2026-04-22 source walk | - |
| `src/code/win32/win_qgl.c` | `346` | Current function walk complete; no file-level parity gap isolated | [platform-specific audit](platform-specific-engine-parity-audit-and-implementation-plan-2026-04-16.md) + current 2026-04-22 source walk | - |
| `src/code/win32/win_shared.c` | `13` | Current function walk complete; no file-level parity gap isolated | [platform-specific audit](platform-specific-engine-parity-audit-and-implementation-plan-2026-04-16.md) + current 2026-04-22 source walk | - |
| `src/code/win32/win_snd.c` | `8` | Current function walk complete; no file-level parity gap isolated | [platform-specific audit](platform-specific-engine-parity-audit-and-implementation-plan-2026-04-16.md) + current 2026-04-22 source walk | - |
| `src/code/win32/win_syscon.c` | `13` | Current function walk complete; no file-level parity gap isolated | [platform-specific audit](platform-specific-engine-parity-audit-and-implementation-plan-2026-04-16.md) + current 2026-04-22 source walk | - |
| `src/code/win32/win_wndproc.c` | `9` | Current function walk complete; no file-level parity gap isolated | [platform-specific audit](platform-specific-engine-parity-audit-and-implementation-plan-2026-04-16.md) + current 2026-04-22 source walk | - |
### `src/code/botlib` (28 files)

Current 2026-04-22 audit result: the `src/code/botlib` function walk did
not isolate any new file-level owners inside the closed botlib internal
register. The retained mapping-round `61` bridge/import ownership and the
deterministic AAS/reachability/goal-state proof lane still bound the tree
on current evidence, while the remaining live-map or gameplay-tuning
nuance stays outside the repo-wide/file-level gap register.

| File | Functions | Current parity state | Primary evidence | Gap note |
| --- | ---: | --- | --- | --- |
| `src/code/botlib/be_aas_bspq3.c` | `21` | Current function walk complete; no file-level parity gap isolated | [botlib audit](botlib-internal-parity-audit-and-implementation-plan-2026-04-10.md) + current 2026-04-22 source walk | - |
| `src/code/botlib/be_aas_cluster.c` | `33` | Current function walk complete; no file-level parity gap isolated | [botlib audit](botlib-internal-parity-audit-and-implementation-plan-2026-04-10.md) + current 2026-04-22 source walk | - |
| `src/code/botlib/be_aas_debug.c` | `19` | Current function walk complete; no file-level parity gap isolated | [botlib audit](botlib-internal-parity-audit-and-implementation-plan-2026-04-10.md) + current 2026-04-22 source walk | - |
| `src/code/botlib/be_aas_entity.c` | `15` | Current function walk complete; no file-level parity gap isolated | [botlib audit](botlib-internal-parity-audit-and-implementation-plan-2026-04-10.md) + current 2026-04-22 source walk | - |
| `src/code/botlib/be_aas_file.c` | `8` | Current function walk complete; no file-level parity gap isolated | [botlib audit](botlib-internal-parity-audit-and-implementation-plan-2026-04-10.md) + current 2026-04-22 source walk | - |
| `src/code/botlib/be_aas_main.c` | `17` | Current function walk complete; no file-level parity gap isolated | [botlib audit](botlib-internal-parity-audit-and-implementation-plan-2026-04-10.md) + current 2026-04-22 source walk | - |
| `src/code/botlib/be_aas_move.c` | `19` | Current function walk complete; no file-level parity gap isolated | [botlib audit](botlib-internal-parity-audit-and-implementation-plan-2026-04-10.md) + current 2026-04-22 source walk | - |
| `src/code/botlib/be_aas_optimize.c` | `8` | Current function walk complete; no file-level parity gap isolated | [botlib audit](botlib-internal-parity-audit-and-implementation-plan-2026-04-10.md) + current 2026-04-22 source walk | - |
| `src/code/botlib/be_aas_reach.c` | `54` | Current function walk complete; no file-level parity gap isolated | [botlib audit](botlib-internal-parity-audit-and-implementation-plan-2026-04-10.md) + current 2026-04-22 source walk | - |
| `src/code/botlib/be_aas_route.c` | `52` | Current function walk complete; no file-level parity gap isolated | [botlib audit](botlib-internal-parity-audit-and-implementation-plan-2026-04-10.md) + current 2026-04-22 source walk | - |
| `src/code/botlib/be_aas_routealt.c` | `4` | Current function walk complete; no file-level parity gap isolated | [botlib audit](botlib-internal-parity-audit-and-implementation-plan-2026-04-10.md) + current 2026-04-22 source walk | - |
| `src/code/botlib/be_aas_sample.c` | `28` | Current function walk complete; no file-level parity gap isolated | [botlib audit](botlib-internal-parity-audit-and-implementation-plan-2026-04-10.md) + current 2026-04-22 source walk | - |
| `src/code/botlib/be_ai_char.c` | `19` | Current function walk complete; no file-level parity gap isolated | [botlib audit](botlib-internal-parity-audit-and-implementation-plan-2026-04-10.md) + current 2026-04-22 source walk | - |
| `src/code/botlib/be_ai_chat.c` | `60` | Current function walk complete; no file-level parity gap isolated | [botlib audit](botlib-internal-parity-audit-and-implementation-plan-2026-04-10.md) + current 2026-04-22 source walk | - |
| `src/code/botlib/be_ai_gen.c` | `2` | Current function walk complete; no file-level parity gap isolated | [botlib audit](botlib-internal-parity-audit-and-implementation-plan-2026-04-10.md) + current 2026-04-22 source walk | - |
| `src/code/botlib/be_ai_goal.c` | `43` | Current function walk complete; no file-level parity gap isolated | [botlib audit](botlib-internal-parity-audit-and-implementation-plan-2026-04-10.md) + current 2026-04-22 source walk | - |
| `src/code/botlib/be_ai_move.c` | `70` | Current function walk complete; no file-level parity gap isolated | [botlib audit](botlib-internal-parity-audit-and-implementation-plan-2026-04-10.md) + current 2026-04-22 source walk | - |
| `src/code/botlib/be_ai_weap.c` | `14` | Current function walk complete; no file-level parity gap isolated | [botlib audit](botlib-internal-parity-audit-and-implementation-plan-2026-04-10.md) + current 2026-04-22 source walk | - |
| `src/code/botlib/be_ai_weight.c` | `24` | Current function walk complete; no file-level parity gap isolated | [botlib audit](botlib-internal-parity-audit-and-implementation-plan-2026-04-10.md) + current 2026-04-22 source walk | - |
| `src/code/botlib/be_ea.c` | `32` | Current function walk complete; no file-level parity gap isolated | [botlib audit](botlib-internal-parity-audit-and-implementation-plan-2026-04-10.md) + current 2026-04-22 source walk | - |
| `src/code/botlib/be_interface.c` | `16` | Current function walk complete; no file-level parity gap isolated | [botlib audit](botlib-internal-parity-audit-and-implementation-plan-2026-04-10.md) + current 2026-04-22 source walk | - |
| `src/code/botlib/l_crc.c` | `5` | Current function walk complete; no file-level parity gap isolated | [botlib audit](botlib-internal-parity-audit-and-implementation-plan-2026-04-10.md) + current 2026-04-22 source walk | - |
| `src/code/botlib/l_libvar.c` | `13` | Current function walk complete; no file-level parity gap isolated | [botlib audit](botlib-internal-parity-audit-and-implementation-plan-2026-04-10.md) + current 2026-04-22 source walk | - |
| `src/code/botlib/l_log.c` | `7` | Current function walk complete; no file-level parity gap isolated | [botlib audit](botlib-internal-parity-audit-and-implementation-plan-2026-04-10.md) + current 2026-04-22 source walk | - |
| `src/code/botlib/l_memory.c` | `13` | Current function walk complete; no file-level parity gap isolated | [botlib audit](botlib-internal-parity-audit-and-implementation-plan-2026-04-10.md) + current 2026-04-22 source walk | - |
| `src/code/botlib/l_precomp.c` | `82` | Current function walk complete; no file-level parity gap isolated | [botlib audit](botlib-internal-parity-audit-and-implementation-plan-2026-04-10.md) + current 2026-04-22 source walk | - |
| `src/code/botlib/l_script.c` | `39` | Current function walk complete; no file-level parity gap isolated | [botlib audit](botlib-internal-parity-audit-and-implementation-plan-2026-04-10.md) + current 2026-04-22 source walk | - |
| `src/code/botlib/l_struct.c` | `9` | Current function walk complete; no file-level parity gap isolated | [botlib audit](botlib-internal-parity-audit-and-implementation-plan-2026-04-10.md) + current 2026-04-22 source walk | - |

## Compatibility-Only Unix And Null Host Surface

### `src/code/unix` (10 files)

Current 2026-04-22 audit result: the `src/code/unix` function walk did
not isolate any new file-level owners beyond the existing `RW-G02`
notes for `unix_main.c`, `linux_glimp.c`, `linux_snd.c`, and
`linux_joystick.c`. The focused non-Windows portability lane
(`18 passed`) and the current repo-wide audit still bound
`linux_common.c`, `linux_qgl.c`, `linux_signals.c`, `unix_net.c`,
`unix_shared.c`, and `vm_x86.c` on current evidence.

| File | Functions | Current parity state | Primary evidence | Gap note |
| --- | ---: | --- | --- | --- |
| `src/code/unix/linux_common.c` | `6` | Current compatibility function walk complete; no new file-level portability gap isolated | [repo-wide audit](repo-wide-parity-audit-2026-04-21.md) + current 2026-04-22 source walk | - |
| `src/code/unix/linux_glimp.c` | `41` | RW-G02 file-level note open | [repo-wide audit](repo-wide-parity-audit-2026-04-21.md) + [note](source-file-gap-notes/rw-g02-linux-glimp.md) | [note](source-file-gap-notes/rw-g02-linux-glimp.md) |
| `src/code/unix/linux_joystick.c` | `6` | RW-G02 file-level note open | [repo-wide audit](repo-wide-parity-audit-2026-04-21.md) + [note](source-file-gap-notes/rw-g02-linux-joystick.md) | [note](source-file-gap-notes/rw-g02-linux-joystick.md) |
| `src/code/unix/linux_qgl.c` | `341` | Current compatibility function walk complete; no new file-level portability gap isolated | [repo-wide audit](repo-wide-parity-audit-2026-04-21.md) + current 2026-04-22 source walk | - |
| `src/code/unix/linux_signals.c` | `2` | Current compatibility function walk complete; no new file-level portability gap isolated | [repo-wide audit](repo-wide-parity-audit-2026-04-21.md) + current 2026-04-22 source walk | - |
| `src/code/unix/linux_snd.c` | `9` | RW-G02 file-level note open | [repo-wide audit](repo-wide-parity-audit-2026-04-21.md) + [note](source-file-gap-notes/rw-g02-linux-snd.md) | [note](source-file-gap-notes/rw-g02-linux-snd.md) |
| `src/code/unix/unix_main.c` | `59` | RW-G02 file-level note open | [repo-wide audit](repo-wide-parity-audit-2026-04-21.md) + [note](source-file-gap-notes/rw-g02-unix-main.md) | [note](source-file-gap-notes/rw-g02-unix-main.md) |
| `src/code/unix/unix_net.c` | `17` | Current compatibility function walk complete; no new file-level portability gap isolated | [repo-wide audit](repo-wide-parity-audit-2026-04-21.md) + current 2026-04-22 source walk | - |
| `src/code/unix/unix_shared.c` | `21` | Current compatibility function walk complete; no new file-level portability gap isolated | [repo-wide audit](repo-wide-parity-audit-2026-04-21.md) + current 2026-04-22 source walk | - |
| `src/code/unix/vm_x86.c` | `2` | Current compatibility function walk complete; no new file-level portability gap isolated | [repo-wide audit](repo-wide-parity-audit-2026-04-21.md) + current 2026-04-22 source walk | - |
### `src/code/null` (7 files)

Current 2026-04-22 audit result: the `src/code/null` function walk
isolated `null_glimp.c` as an additional `RW-G02` owner beside the
existing notes for `null_main.c`, `null_client.c`, `null_input.c`,
and `null_snddma.c`. The focused non-Windows portability lane
(`18 passed`) and the current repo-wide audit still bound
`null_net.c` and `mac_net.c` on current evidence, so no further
file-level owner is opened inside the null tree this round.

| File | Functions | Current parity state | Primary evidence | Gap note |
| --- | ---: | --- | --- | --- |
| `src/code/null/mac_net.c` | `5` | Current compatibility function walk complete; no new file-level portability gap isolated | [repo-wide audit](repo-wide-parity-audit-2026-04-21.md) + current 2026-04-22 source walk | - |
| `src/code/null/null_client.c` | `50` | RW-G02 file-level note open | [repo-wide audit](repo-wide-parity-audit-2026-04-21.md) + [note](source-file-gap-notes/rw-g02-null-client.md) | [note](source-file-gap-notes/rw-g02-null-client.md) |
| `src/code/null/null_glimp.c` | `7` | RW-G02 file-level note open | [repo-wide audit](repo-wide-parity-audit-2026-04-21.md) + [note](source-file-gap-notes/rw-g02-null-glimp.md) | [note](source-file-gap-notes/rw-g02-null-glimp.md) |
| `src/code/null/null_input.c` | `6` | RW-G02 file-level note open | [repo-wide audit](repo-wide-parity-audit-2026-04-21.md) + [note](source-file-gap-notes/rw-g02-null-input.md) | [note](source-file-gap-notes/rw-g02-null-input.md) |
| `src/code/null/null_main.c` | `28` | RW-G02 file-level note open | [repo-wide audit](repo-wide-parity-audit-2026-04-21.md) + [note](source-file-gap-notes/rw-g02-null-main.md) | [note](source-file-gap-notes/rw-g02-null-main.md) |
| `src/code/null/null_net.c` | `5` | Current compatibility function walk complete; no new file-level portability gap isolated | [repo-wide audit](repo-wide-parity-audit-2026-04-21.md) + current 2026-04-22 source walk | - |
| `src/code/null/null_snddma.c` | `11` | RW-G02 file-level note open | [repo-wide audit](repo-wide-parity-audit-2026-04-21.md) + [note](source-file-gap-notes/rw-g02-null-snddma.md) | [note](source-file-gap-notes/rw-g02-null-snddma.md) |

## Secondary Tool, Editor, Compiler, And Legacy Source Surface

### `src/code/bspc` (47 files)

Current 2026-04-22 audit result: the `src/code/bspc` function walk did
not isolate any new file-level owners. This retained BSP/AAS compiler
toolchain remains a secondary support surface outside the primary
runtime replacement target on current evidence.

| File | Functions | Current parity state | Primary evidence | Gap note |
| --- | ---: | --- | --- | --- |
| `src/code/bspc/_files.c` | `0` | Current secondary function walk complete; no new file-level gap isolated | [source-file plan](source-file-parity-audit-plan-2026-04-22.md) + current 2026-04-22 source walk | - |
| `src/code/bspc/aas_areamerging.c` | `6` | Current secondary function walk complete; no new file-level gap isolated | [source-file plan](source-file-parity-audit-plan-2026-04-22.md) + current 2026-04-22 source walk | - |
| `src/code/bspc/aas_cfg.c` | `4` | Current secondary function walk complete; no new file-level gap isolated | [source-file plan](source-file-parity-audit-plan-2026-04-22.md) + current 2026-04-22 source walk | - |
| `src/code/bspc/aas_create.c` | `30` | Current secondary function walk complete; no new file-level gap isolated | [source-file plan](source-file-parity-audit-plan-2026-04-22.md) + current 2026-04-22 source walk | - |
| `src/code/bspc/aas_edgemelting.c` | `3` | Current secondary function walk complete; no new file-level gap isolated | [source-file plan](source-file-parity-audit-plan-2026-04-22.md) + current 2026-04-22 source walk | - |
| `src/code/bspc/aas_facemerging.c` | `6` | Current secondary function walk complete; no new file-level gap isolated | [source-file plan](source-file-parity-audit-plan-2026-04-22.md) + current 2026-04-22 source walk | - |
| `src/code/bspc/aas_file.c` | `9` | Current secondary function walk complete; no new file-level gap isolated | [source-file plan](source-file-parity-audit-plan-2026-04-22.md) + current 2026-04-22 source walk | - |
| `src/code/bspc/aas_gsubdiv.c` | `12` | Current secondary function walk complete; no new file-level gap isolated | [source-file plan](source-file-parity-audit-plan-2026-04-22.md) + current 2026-04-22 source walk | - |
| `src/code/bspc/aas_map.c` | `16` | Current secondary function walk complete; no new file-level gap isolated | [source-file plan](source-file-parity-audit-plan-2026-04-22.md) + current 2026-04-22 source walk | - |
| `src/code/bspc/aas_prunenodes.c` | `2` | Current secondary function walk complete; no new file-level gap isolated | [source-file plan](source-file-parity-audit-plan-2026-04-22.md) + current 2026-04-22 source walk | - |
| `src/code/bspc/aas_store.c` | `23` | Current secondary function walk complete; no new file-level gap isolated | [source-file plan](source-file-parity-audit-plan-2026-04-22.md) + current 2026-04-22 source walk | - |
| `src/code/bspc/be_aas_bspc.c` | `16` | Current secondary function walk complete; no new file-level gap isolated | [source-file plan](source-file-parity-audit-plan-2026-04-22.md) + current 2026-04-22 source walk | - |
| `src/code/bspc/brushbsp.c` | `41` | Current secondary function walk complete; no new file-level gap isolated | [source-file plan](source-file-parity-audit-plan-2026-04-22.md) + current 2026-04-22 source walk | - |
| `src/code/bspc/bspc.c` | `9` | Current secondary function walk complete; no new file-level gap isolated | [source-file plan](source-file-parity-audit-plan-2026-04-22.md) + current 2026-04-22 source walk | - |
| `src/code/bspc/cfgq3.c` | `0` | Current secondary function walk complete; no new file-level gap isolated | [source-file plan](source-file-parity-audit-plan-2026-04-22.md) + current 2026-04-22 source walk | - |
| `src/code/bspc/csg.c` | `19` | Current secondary function walk complete; no new file-level gap isolated | [source-file plan](source-file-parity-audit-plan-2026-04-22.md) + current 2026-04-22 source walk | - |
| `src/code/bspc/faces.c` | `23` | Current secondary function walk complete; no new file-level gap isolated | [source-file plan](source-file-parity-audit-plan-2026-04-22.md) + current 2026-04-22 source walk | - |
| `src/code/bspc/gldraw.c` | `10` | Current secondary function walk complete; no new file-level gap isolated | [source-file plan](source-file-parity-audit-plan-2026-04-22.md) + current 2026-04-22 source walk | - |
| `src/code/bspc/glfile.c` | `5` | Current secondary function walk complete; no new file-level gap isolated | [source-file plan](source-file-parity-audit-plan-2026-04-22.md) + current 2026-04-22 source walk | - |
| `src/code/bspc/l_bsp_ent.c` | `8` | Current secondary function walk complete; no new file-level gap isolated | [source-file plan](source-file-parity-audit-plan-2026-04-22.md) + current 2026-04-22 source walk | - |
| `src/code/bspc/l_bsp_hl.c` | `19` | Current secondary function walk complete; no new file-level gap isolated | [source-file plan](source-file-parity-audit-plan-2026-04-22.md) + current 2026-04-22 source walk | - |
| `src/code/bspc/l_bsp_q1.c` | `10` | Current secondary function walk complete; no new file-level gap isolated | [source-file plan](source-file-parity-audit-plan-2026-04-22.md) + current 2026-04-22 source walk | - |
| `src/code/bspc/l_bsp_q2.c` | `19` | Current secondary function walk complete; no new file-level gap isolated | [source-file plan](source-file-parity-audit-plan-2026-04-22.md) + current 2026-04-22 source walk | - |
| `src/code/bspc/l_bsp_q3.c` | `18` | Current secondary function walk complete; no new file-level gap isolated | [source-file plan](source-file-parity-audit-plan-2026-04-22.md) + current 2026-04-22 source walk | - |
| `src/code/bspc/l_bsp_sin.c` | `20` | Current secondary function walk complete; no new file-level gap isolated | [source-file plan](source-file-parity-audit-plan-2026-04-22.md) + current 2026-04-22 source walk | - |
| `src/code/bspc/l_cmd.c` | `73` | Current secondary function walk complete; no new file-level gap isolated | [source-file plan](source-file-parity-audit-plan-2026-04-22.md) + current 2026-04-22 source walk | - |
| `src/code/bspc/l_log.c` | `9` | Current secondary function walk complete; no new file-level gap isolated | [source-file plan](source-file-parity-audit-plan-2026-04-22.md) + current 2026-04-22 source walk | - |
| `src/code/bspc/l_math.c` | `21` | Current secondary function walk complete; no new file-level gap isolated | [source-file plan](source-file-parity-audit-plan-2026-04-22.md) + current 2026-04-22 source walk | - |
| `src/code/bspc/l_mem.c` | `22` | Current secondary function walk complete; no new file-level gap isolated | [source-file plan](source-file-parity-audit-plan-2026-04-22.md) + current 2026-04-22 source walk | - |
| `src/code/bspc/l_poly.c` | `31` | Current secondary function walk complete; no new file-level gap isolated | [source-file plan](source-file-parity-audit-plan-2026-04-22.md) + current 2026-04-22 source walk | - |
| `src/code/bspc/l_qfiles.c` | `11` | Current secondary function walk complete; no new file-level gap isolated | [source-file plan](source-file-parity-audit-plan-2026-04-22.md) + current 2026-04-22 source walk | - |
| `src/code/bspc/l_threads.c` | `65` | Current secondary function walk complete; no new file-level gap isolated | [source-file plan](source-file-parity-audit-plan-2026-04-22.md) + current 2026-04-22 source walk | - |
| `src/code/bspc/l_utils.c` | `7` | Current secondary function walk complete; no new file-level gap isolated | [source-file plan](source-file-parity-audit-plan-2026-04-22.md) + current 2026-04-22 source walk | - |
| `src/code/bspc/leakfile.c` | `1` | Current secondary function walk complete; no new file-level gap isolated | [source-file plan](source-file-parity-audit-plan-2026-04-22.md) + current 2026-04-22 source walk | - |
| `src/code/bspc/map.c` | `22` | Current secondary function walk complete; no new file-level gap isolated | [source-file plan](source-file-parity-audit-plan-2026-04-22.md) + current 2026-04-22 source walk | - |
| `src/code/bspc/map_hl.c` | `14` | Current secondary function walk complete; no new file-level gap isolated | [source-file plan](source-file-parity-audit-plan-2026-04-22.md) + current 2026-04-22 source walk | - |
| `src/code/bspc/map_q1.c` | `17` | Current secondary function walk complete; no new file-level gap isolated | [source-file plan](source-file-parity-audit-plan-2026-04-22.md) + current 2026-04-22 source walk | - |
| `src/code/bspc/map_q2.c` | `20` | Current secondary function walk complete; no new file-level gap isolated | [source-file plan](source-file-parity-audit-plan-2026-04-22.md) + current 2026-04-22 source walk | - |
| `src/code/bspc/map_q3.c` | `8` | Current secondary function walk complete; no new file-level gap isolated | [source-file plan](source-file-parity-audit-plan-2026-04-22.md) + current 2026-04-22 source walk | - |
| `src/code/bspc/map_sin.c` | `16` | Current secondary function walk complete; no new file-level gap isolated | [source-file plan](source-file-parity-audit-plan-2026-04-22.md) + current 2026-04-22 source walk | - |
| `src/code/bspc/nodraw.c` | `4` | Current secondary function walk complete; no new file-level gap isolated | [source-file plan](source-file-parity-audit-plan-2026-04-22.md) + current 2026-04-22 source walk | - |
| `src/code/bspc/portals.c` | `33` | Current secondary function walk complete; no new file-level gap isolated | [source-file plan](source-file-parity-audit-plan-2026-04-22.md) + current 2026-04-22 source walk | - |
| `src/code/bspc/prtfile.c` | `9` | Current secondary function walk complete; no new file-level gap isolated | [source-file plan](source-file-parity-audit-plan-2026-04-22.md) + current 2026-04-22 source walk | - |
| `src/code/bspc/tetrahedron.c` | `45` | Current secondary function walk complete; no new file-level gap isolated | [source-file plan](source-file-parity-audit-plan-2026-04-22.md) + current 2026-04-22 source walk | - |
| `src/code/bspc/textures.c` | `3` | Current secondary function walk complete; no new file-level gap isolated | [source-file plan](source-file-parity-audit-plan-2026-04-22.md) + current 2026-04-22 source walk | - |
| `src/code/bspc/tree.c` | `8` | Current secondary function walk complete; no new file-level gap isolated | [source-file plan](source-file-parity-audit-plan-2026-04-22.md) + current 2026-04-22 source walk | - |
| `src/code/bspc/writebsp.c` | `13` | Current secondary function walk complete; no new file-level gap isolated | [source-file plan](source-file-parity-audit-plan-2026-04-22.md) + current 2026-04-22 source walk | - |
### `src/code/jpeg-6` (51 files)

Current 2026-04-22 audit result: the `src/code/jpeg-6` function walk
did not isolate any new file-level owners. The refreshed extractor now
lands on the macro-style IJG definitions instead of the earlier zero-row
placeholders, while this bundled JPEG support tree remains a secondary
support surface on current evidence.

| File | Functions | Current parity state | Primary evidence | Gap note |
| --- | ---: | --- | --- | --- |
| `src/code/jpeg-6/jcapimin.c` | `7` | Current secondary function walk complete; no new file-level gap isolated | [source-file plan](source-file-parity-audit-plan-2026-04-22.md) + current 2026-04-22 source walk | - |
| `src/code/jpeg-6/jcapistd.c` | `3` | Current secondary function walk complete; no new file-level gap isolated | [source-file plan](source-file-parity-audit-plan-2026-04-22.md) + current 2026-04-22 source walk | - |
| `src/code/jpeg-6/jccoefct.c` | `5` | Current secondary function walk complete; no new file-level gap isolated | [source-file plan](source-file-parity-audit-plan-2026-04-22.md) + current 2026-04-22 source walk | - |
| `src/code/jpeg-6/jccolor.c` | `8` | Current secondary function walk complete; no new file-level gap isolated | [source-file plan](source-file-parity-audit-plan-2026-04-22.md) + current 2026-04-22 source walk | - |
| `src/code/jpeg-6/jcdctmgr.c` | `2` | Current secondary function walk complete; no new file-level gap isolated | [source-file plan](source-file-parity-audit-plan-2026-04-22.md) + current 2026-04-22 source walk | - |
| `src/code/jpeg-6/jchuff.c` | `12` | Current secondary function walk complete; no new file-level gap isolated | [source-file plan](source-file-parity-audit-plan-2026-04-22.md) + current 2026-04-22 source walk | - |
| `src/code/jpeg-6/jcinit.c` | `1` | Current secondary function walk complete; no new file-level gap isolated | [source-file plan](source-file-parity-audit-plan-2026-04-22.md) + current 2026-04-22 source walk | - |
| `src/code/jpeg-6/jcmainct.c` | `4` | Current secondary function walk complete; no new file-level gap isolated | [source-file plan](source-file-parity-audit-plan-2026-04-22.md) + current 2026-04-22 source walk | - |
| `src/code/jpeg-6/jcmarker.c` | `6` | Current secondary function walk complete; no new file-level gap isolated | [source-file plan](source-file-parity-audit-plan-2026-04-22.md) + current 2026-04-22 source walk | - |
| `src/code/jpeg-6/jcmaster.c` | `4` | Current secondary function walk complete; no new file-level gap isolated | [source-file plan](source-file-parity-audit-plan-2026-04-22.md) + current 2026-04-22 source walk | - |
| `src/code/jpeg-6/jcomapi.c` | `2` | Current secondary function walk complete; no new file-level gap isolated | [source-file plan](source-file-parity-audit-plan-2026-04-22.md) + current 2026-04-22 source walk | - |
| `src/code/jpeg-6/jcparam.c` | `4` | Current secondary function walk complete; no new file-level gap isolated | [source-file plan](source-file-parity-audit-plan-2026-04-22.md) + current 2026-04-22 source walk | - |
| `src/code/jpeg-6/jcphuff.c` | `13` | Current secondary function walk complete; no new file-level gap isolated | [source-file plan](source-file-parity-audit-plan-2026-04-22.md) + current 2026-04-22 source walk | - |
| `src/code/jpeg-6/jcprepct.c` | `6` | Current secondary function walk complete; no new file-level gap isolated | [source-file plan](source-file-parity-audit-plan-2026-04-22.md) + current 2026-04-22 source walk | - |
| `src/code/jpeg-6/jcsample.c` | `10` | Current secondary function walk complete; no new file-level gap isolated | [source-file plan](source-file-parity-audit-plan-2026-04-22.md) + current 2026-04-22 source walk | - |
| `src/code/jpeg-6/jctrans.c` | `6` | Current secondary function walk complete; no new file-level gap isolated | [source-file plan](source-file-parity-audit-plan-2026-04-22.md) + current 2026-04-22 source walk | - |
| `src/code/jpeg-6/jdapimin.c` | `10` | Current secondary function walk complete; no new file-level gap isolated | [source-file plan](source-file-parity-audit-plan-2026-04-22.md) + current 2026-04-22 source walk | - |
| `src/code/jpeg-6/jdapistd.c` | `6` | Current secondary function walk complete; no new file-level gap isolated | [source-file plan](source-file-parity-audit-plan-2026-04-22.md) + current 2026-04-22 source walk | - |
| `src/code/jpeg-6/jdatadst.c` | `4` | Current secondary function walk complete; no new file-level gap isolated | [source-file plan](source-file-parity-audit-plan-2026-04-22.md) + current 2026-04-22 source walk | - |
| `src/code/jpeg-6/jdatasrc.c` | `5` | Current secondary function walk complete; no new file-level gap isolated | [source-file plan](source-file-parity-audit-plan-2026-04-22.md) + current 2026-04-22 source walk | - |
| `src/code/jpeg-6/jdcoefct.c` | `9` | Current secondary function walk complete; no new file-level gap isolated | [source-file plan](source-file-parity-audit-plan-2026-04-22.md) + current 2026-04-22 source walk | - |
| `src/code/jpeg-6/jdcolor.c` | `7` | Current secondary function walk complete; no new file-level gap isolated | [source-file plan](source-file-parity-audit-plan-2026-04-22.md) + current 2026-04-22 source walk | - |
| `src/code/jpeg-6/jddctmgr.c` | `2` | Current secondary function walk complete; no new file-level gap isolated | [source-file plan](source-file-parity-audit-plan-2026-04-22.md) + current 2026-04-22 source walk | - |
| `src/code/jpeg-6/jdhuff.c` | `6` | Current secondary function walk complete; no new file-level gap isolated | [source-file plan](source-file-parity-audit-plan-2026-04-22.md) + current 2026-04-22 source walk | - |
| `src/code/jpeg-6/jdinput.c` | `6` | Current secondary function walk complete; no new file-level gap isolated | [source-file plan](source-file-parity-audit-plan-2026-04-22.md) + current 2026-04-22 source walk | - |
| `src/code/jpeg-6/jdmainct.c` | `5` | Current secondary function walk complete; no new file-level gap isolated | [source-file plan](source-file-parity-audit-plan-2026-04-22.md) + current 2026-04-22 source walk | - |
| `src/code/jpeg-6/jdmarker.c` | `6` | Current secondary function walk complete; no new file-level gap isolated | [source-file plan](source-file-parity-audit-plan-2026-04-22.md) + current 2026-04-22 source walk | - |
| `src/code/jpeg-6/jdmaster.c` | `6` | Current secondary function walk complete; no new file-level gap isolated | [source-file plan](source-file-parity-audit-plan-2026-04-22.md) + current 2026-04-22 source walk | - |
| `src/code/jpeg-6/jdmerge.c` | `5` | Current secondary function walk complete; no new file-level gap isolated | [source-file plan](source-file-parity-audit-plan-2026-04-22.md) + current 2026-04-22 source walk | - |
| `src/code/jpeg-6/jdphuff.c` | `7` | Current secondary function walk complete; no new file-level gap isolated | [source-file plan](source-file-parity-audit-plan-2026-04-22.md) + current 2026-04-22 source walk | - |
| `src/code/jpeg-6/jdpostct.c` | `5` | Current secondary function walk complete; no new file-level gap isolated | [source-file plan](source-file-parity-audit-plan-2026-04-22.md) + current 2026-04-22 source walk | - |
| `src/code/jpeg-6/jdsample.c` | `10` | Current secondary function walk complete; no new file-level gap isolated | [source-file plan](source-file-parity-audit-plan-2026-04-22.md) + current 2026-04-22 source walk | - |
| `src/code/jpeg-6/jdtrans.c` | `1` | Current secondary function walk complete; no new file-level gap isolated | [source-file plan](source-file-parity-audit-plan-2026-04-22.md) + current 2026-04-22 source walk | - |
| `src/code/jpeg-6/jerror.c` | `5` | Current secondary function walk complete; no new file-level gap isolated | [source-file plan](source-file-parity-audit-plan-2026-04-22.md) + current 2026-04-22 source walk | - |
| `src/code/jpeg-6/jfdctflt.c` | `1` | Current secondary function walk complete; no new file-level gap isolated | [source-file plan](source-file-parity-audit-plan-2026-04-22.md) + current 2026-04-22 source walk | - |
| `src/code/jpeg-6/jfdctfst.c` | `1` | Current secondary function walk complete; no new file-level gap isolated | [source-file plan](source-file-parity-audit-plan-2026-04-22.md) + current 2026-04-22 source walk | - |
| `src/code/jpeg-6/jfdctint.c` | `1` | Current secondary function walk complete; no new file-level gap isolated | [source-file plan](source-file-parity-audit-plan-2026-04-22.md) + current 2026-04-22 source walk | - |
| `src/code/jpeg-6/jidctflt.c` | `1` | Current secondary function walk complete; no new file-level gap isolated | [source-file plan](source-file-parity-audit-plan-2026-04-22.md) + current 2026-04-22 source walk | - |
| `src/code/jpeg-6/jidctfst.c` | `1` | Current secondary function walk complete; no new file-level gap isolated | [source-file plan](source-file-parity-audit-plan-2026-04-22.md) + current 2026-04-22 source walk | - |
| `src/code/jpeg-6/jidctint.c` | `1` | Current secondary function walk complete; no new file-level gap isolated | [source-file plan](source-file-parity-audit-plan-2026-04-22.md) + current 2026-04-22 source walk | - |
| `src/code/jpeg-6/jidctred.c` | `3` | Current secondary function walk complete; no new file-level gap isolated | [source-file plan](source-file-parity-audit-plan-2026-04-22.md) + current 2026-04-22 source walk | - |
| `src/code/jpeg-6/jload.c` | `1` | Current secondary function walk complete; no new file-level gap isolated | [source-file plan](source-file-parity-audit-plan-2026-04-22.md) + current 2026-04-22 source walk | - |
| `src/code/jpeg-6/jmemansi.c` | `9` | Current secondary function walk complete; no new file-level gap isolated | [source-file plan](source-file-parity-audit-plan-2026-04-22.md) + current 2026-04-22 source walk | - |
| `src/code/jpeg-6/jmemdos.c` | `19` | Current secondary function walk complete; no new file-level gap isolated | [source-file plan](source-file-parity-audit-plan-2026-04-22.md) + current 2026-04-22 source walk | - |
| `src/code/jpeg-6/jmemmgr.c` | `4` | Current secondary function walk complete; no new file-level gap isolated | [source-file plan](source-file-parity-audit-plan-2026-04-22.md) + current 2026-04-22 source walk | - |
| `src/code/jpeg-6/jmemname.c` | `11` | Current secondary function walk complete; no new file-level gap isolated | [source-file plan](source-file-parity-audit-plan-2026-04-22.md) + current 2026-04-22 source walk | - |
| `src/code/jpeg-6/jmemnobs.c` | `6` | Current secondary function walk complete; no new file-level gap isolated | [source-file plan](source-file-parity-audit-plan-2026-04-22.md) + current 2026-04-22 source walk | - |
| `src/code/jpeg-6/jpegtran.c` | `1` | Current secondary function walk complete; no new file-level gap isolated | [source-file plan](source-file-parity-audit-plan-2026-04-22.md) + current 2026-04-22 source walk | - |
| `src/code/jpeg-6/jquant1.c` | `9` | Current secondary function walk complete; no new file-level gap isolated | [source-file plan](source-file-parity-audit-plan-2026-04-22.md) + current 2026-04-22 source walk | - |
| `src/code/jpeg-6/jquant2.c` | `6` | Current secondary function walk complete; no new file-level gap isolated | [source-file plan](source-file-parity-audit-plan-2026-04-22.md) + current 2026-04-22 source walk | - |
| `src/code/jpeg-6/jutils.c` | `0` | Current secondary function walk complete; no new file-level gap isolated | [source-file plan](source-file-parity-audit-plan-2026-04-22.md) + current 2026-04-22 source walk | - |
### `src/code/splines` (8 files)

Current 2026-04-22 audit result: the `src/code/splines` function walk
did not isolate any new file-level owners. The refreshed extractor now
lands on the retained C++ method definitions, while this legacy spline
editor/helper tree remains a bounded secondary support surface on
current evidence.

| File | Functions | Current parity state | Primary evidence | Gap note |
| --- | ---: | --- | --- | --- |
| `src/code/splines/math_angles.cpp` | `7` | Current secondary function walk complete; no new file-level gap isolated | [source-file plan](source-file-parity-audit-plan-2026-04-22.md) + current 2026-04-22 source walk | - |
| `src/code/splines/math_matrix.cpp` | `6` | Current secondary function walk complete; no new file-level gap isolated | [source-file plan](source-file-parity-audit-plan-2026-04-22.md) + current 2026-04-22 source walk | - |
| `src/code/splines/math_quaternion.cpp` | `3` | Current secondary function walk complete; no new file-level gap isolated | [source-file plan](source-file-parity-audit-plan-2026-04-22.md) + current 2026-04-22 source walk | - |
| `src/code/splines/math_vector.cpp` | `5` | Current secondary function walk complete; no new file-level gap isolated | [source-file plan](source-file-parity-audit-plan-2026-04-22.md) + current 2026-04-22 source walk | - |
| `src/code/splines/q_parse.cpp` | `19` | Current secondary function walk complete; no new file-level gap isolated | [source-file plan](source-file-parity-audit-plan-2026-04-22.md) + current 2026-04-22 source walk | - |
| `src/code/splines/q_shared.cpp` | `47` | Current secondary function walk complete; no new file-level gap isolated | [source-file plan](source-file-parity-audit-plan-2026-04-22.md) + current 2026-04-22 source walk | - |
| `src/code/splines/splines.cpp` | `45` | Current secondary function walk complete; no new file-level gap isolated | [source-file plan](source-file-parity-audit-plan-2026-04-22.md) + current 2026-04-22 source walk | - |
| `src/code/splines/util_str.cpp` | `19` | Current secondary function walk complete; no new file-level gap isolated | [source-file plan](source-file-parity-audit-plan-2026-04-22.md) + current 2026-04-22 source walk | - |
### `src/game` (10 files)

Current 2026-04-22 audit result: the `src/game` function walk did not
isolate any new file-level owners. The retained gameplay config helpers
and standalone fixture/support sources remain a bounded secondary
support surface on current evidence.

| File | Functions | Current parity state | Primary evidence | Gap note |
| --- | ---: | --- | --- | --- |
| `src/game/g_config.c` | `30` | Current secondary function walk complete; no new file-level gap isolated | [source-file plan](source-file-parity-audit-plan-2026-04-22.md) + current 2026-04-22 source walk | - |
| `src/game/g_match_config.c` | `12` | Current secondary function walk complete; no new file-level gap isolated | [source-file plan](source-file-parity-audit-plan-2026-04-22.md) + current 2026-04-22 source walk | - |
| `src/game/tests/cosmetics_fixtures.c` | `13` | Current secondary function walk complete; no new file-level gap isolated | [source-file plan](source-file-parity-audit-plan-2026-04-22.md) + current 2026-04-22 source walk | - |
| `src/game/tests/fixture_runner.c` | `8` | Current secondary function walk complete; no new file-level gap isolated | [source-file plan](source-file-parity-audit-plan-2026-04-22.md) + current 2026-04-22 source walk | - |
| `src/game/tests/item_fixtures.c` | `7` | Current secondary function walk complete; no new file-level gap isolated | [source-file plan](source-file-parity-audit-plan-2026-04-22.md) + current 2026-04-22 source walk | - |
| `src/game/tests/rules_entry.c` | `1` | Current secondary function walk complete; no new file-level gap isolated | [source-file plan](source-file-parity-audit-plan-2026-04-22.md) + current 2026-04-22 source walk | - |
| `src/game/tests/sample_fixtures.c` | `2` | Current secondary function walk complete; no new file-level gap isolated | [source-file plan](source-file-parity-audit-plan-2026-04-22.md) + current 2026-04-22 source walk | - |
| `src/game/tests/syscall_mocks.c` | `4` | Current secondary function walk complete; no new file-level gap isolated | [source-file plan](source-file-parity-audit-plan-2026-04-22.md) + current 2026-04-22 source walk | - |
| `src/game/tests/vote_control_fixtures.c` | `12` | Current secondary function walk complete; no new file-level gap isolated | [source-file plan](source-file-parity-audit-plan-2026-04-22.md) + current 2026-04-22 source walk | - |
| `src/game/tests/weapon_cvar_fixtures.c` | `9` | Current secondary function walk complete; no new file-level gap isolated | [source-file plan](source-file-parity-audit-plan-2026-04-22.md) + current 2026-04-22 source walk | - |
### `src/lcc` (74 files)

Current 2026-04-22 audit result: the `src/lcc` function walk did not
isolate any new file-level owners. The retained LCC compiler,
preprocessor, code-generator, and bundled test sources remain a
bounded secondary support surface on current evidence.

| File | Functions | Current parity state | Primary evidence | Gap note |
| --- | ---: | --- | --- | --- |
| `src/lcc/cpp/cpp.c` | `5` | Current secondary function walk complete; no new file-level gap isolated | [source-file plan](source-file-parity-audit-plan-2026-04-22.md) + current 2026-04-22 source walk | - |
| `src/lcc/cpp/eval.c` | `4` | Current secondary function walk complete; no new file-level gap isolated | [source-file plan](source-file-parity-audit-plan-2026-04-22.md) + current 2026-04-22 source walk | - |
| `src/lcc/cpp/getopt.c` | `1` | Current secondary function walk complete; no new file-level gap isolated | [source-file plan](source-file-parity-audit-plan-2026-04-22.md) + current 2026-04-22 source walk | - |
| `src/lcc/cpp/hideset.c` | `6` | Current secondary function walk complete; no new file-level gap isolated | [source-file plan](source-file-parity-audit-plan-2026-04-22.md) + current 2026-04-22 source walk | - |
| `src/lcc/cpp/include.c` | `3` | Current secondary function walk complete; no new file-level gap isolated | [source-file plan](source-file-parity-audit-plan-2026-04-22.md) + current 2026-04-22 source walk | - |
| `src/lcc/cpp/lex.c` | `7` | Current secondary function walk complete; no new file-level gap isolated | [source-file plan](source-file-parity-audit-plan-2026-04-22.md) + current 2026-04-22 source walk | - |
| `src/lcc/cpp/macro.c` | `9` | Current secondary function walk complete; no new file-level gap isolated | [source-file plan](source-file-parity-audit-plan-2026-04-22.md) + current 2026-04-22 source walk | - |
| `src/lcc/cpp/nlist.c` | `1` | Current secondary function walk complete; no new file-level gap isolated | [source-file plan](source-file-parity-audit-plan-2026-04-22.md) + current 2026-04-22 source walk | - |
| `src/lcc/cpp/tokens.c` | `10` | Current secondary function walk complete; no new file-level gap isolated | [source-file plan](source-file-parity-audit-plan-2026-04-22.md) + current 2026-04-22 source walk | - |
| `src/lcc/cpp/unix.c` | `2` | Current secondary function walk complete; no new file-level gap isolated | [source-file plan](source-file-parity-audit-plan-2026-04-22.md) + current 2026-04-22 source walk | - |
| `src/lcc/etc/bprint.c` | `18` | Current secondary function walk complete; no new file-level gap isolated | [source-file plan](source-file-parity-audit-plan-2026-04-22.md) + current 2026-04-22 source walk | - |
| `src/lcc/etc/gcc-solaris.c` | `1` | Current secondary function walk complete; no new file-level gap isolated | [source-file plan](source-file-parity-audit-plan-2026-04-22.md) + current 2026-04-22 source walk | - |
| `src/lcc/etc/irix.c` | `1` | Current secondary function walk complete; no new file-level gap isolated | [source-file plan](source-file-parity-audit-plan-2026-04-22.md) + current 2026-04-22 source walk | - |
| `src/lcc/etc/lcc.c` | `24` | Current secondary function walk complete; no new file-level gap isolated | [source-file plan](source-file-parity-audit-plan-2026-04-22.md) + current 2026-04-22 source walk | - |
| `src/lcc/etc/linux.c` | `1` | Current secondary function walk complete; no new file-level gap isolated | [source-file plan](source-file-parity-audit-plan-2026-04-22.md) + current 2026-04-22 source walk | - |
| `src/lcc/etc/ops.c` | `2` | Current secondary function walk complete; no new file-level gap isolated | [source-file plan](source-file-parity-audit-plan-2026-04-22.md) + current 2026-04-22 source walk | - |
| `src/lcc/etc/osf.c` | `1` | Current secondary function walk complete; no new file-level gap isolated | [source-file plan](source-file-parity-audit-plan-2026-04-22.md) + current 2026-04-22 source walk | - |
| `src/lcc/etc/solaris.c` | `1` | Current secondary function walk complete; no new file-level gap isolated | [source-file plan](source-file-parity-audit-plan-2026-04-22.md) + current 2026-04-22 source walk | - |
| `src/lcc/etc/win32.c` | `1` | Current secondary function walk complete; no new file-level gap isolated | [source-file plan](source-file-parity-audit-plan-2026-04-22.md) + current 2026-04-22 source walk | - |
| `src/lcc/lburg/gram.c` | `7` | Current secondary function walk complete; no new file-level gap isolated | [source-file plan](source-file-parity-audit-plan-2026-04-22.md) + current 2026-04-22 source walk | - |
| `src/lcc/lburg/lburg.c` | `29` | Current secondary function walk complete; no new file-level gap isolated | [source-file plan](source-file-parity-audit-plan-2026-04-22.md) + current 2026-04-22 source walk | - |
| `src/lcc/lib/assert.c` | `1` | Current secondary function walk complete; no new file-level gap isolated | [source-file plan](source-file-parity-audit-plan-2026-04-22.md) + current 2026-04-22 source walk | - |
| `src/lcc/lib/bbexit.c` | `5` | Current secondary function walk complete; no new file-level gap isolated | [source-file plan](source-file-parity-audit-plan-2026-04-22.md) + current 2026-04-22 source walk | - |
| `src/lcc/lib/yynull.c` | `1` | Current secondary function walk complete; no new file-level gap isolated | [source-file plan](source-file-parity-audit-plan-2026-04-22.md) + current 2026-04-22 source walk | - |
| `src/lcc/src/2html.c` | `32` | Current secondary function walk complete; no new file-level gap isolated | [source-file plan](source-file-parity-audit-plan-2026-04-22.md) + current 2026-04-22 source walk | - |
| `src/lcc/src/alloc.c` | `6` | Current secondary function walk complete; no new file-level gap isolated | [source-file plan](source-file-parity-audit-plan-2026-04-22.md) + current 2026-04-22 source walk | - |
| `src/lcc/src/asdl.c` | `30` | Current secondary function walk complete; no new file-level gap isolated | [source-file plan](source-file-parity-audit-plan-2026-04-22.md) + current 2026-04-22 source walk | - |
| `src/lcc/src/bind.c` | `0` | Current secondary function walk complete; no new file-level gap isolated | [source-file plan](source-file-parity-audit-plan-2026-04-22.md) + current 2026-04-22 source walk | - |
| `src/lcc/src/bytecode.c` | `23` | Current secondary function walk complete; no new file-level gap isolated | [source-file plan](source-file-parity-audit-plan-2026-04-22.md) + current 2026-04-22 source walk | - |
| `src/lcc/src/dag.c` | `25` | Current secondary function walk complete; no new file-level gap isolated | [source-file plan](source-file-parity-audit-plan-2026-04-22.md) + current 2026-04-22 source walk | - |
| `src/lcc/src/decl.c` | `26` | Current secondary function walk complete; no new file-level gap isolated | [source-file plan](source-file-parity-audit-plan-2026-04-22.md) + current 2026-04-22 source walk | - |
| `src/lcc/src/enode.c` | `22` | Current secondary function walk complete; no new file-level gap isolated | [source-file plan](source-file-parity-audit-plan-2026-04-22.md) + current 2026-04-22 source walk | - |
| `src/lcc/src/error.c` | `7` | Current secondary function walk complete; no new file-level gap isolated | [source-file plan](source-file-parity-audit-plan-2026-04-22.md) + current 2026-04-22 source walk | - |
| `src/lcc/src/event.c` | `2` | Current secondary function walk complete; no new file-level gap isolated | [source-file plan](source-file-parity-audit-plan-2026-04-22.md) + current 2026-04-22 source walk | - |
| `src/lcc/src/expr.c` | `25` | Current secondary function walk complete; no new file-level gap isolated | [source-file plan](source-file-parity-audit-plan-2026-04-22.md) + current 2026-04-22 source walk | - |
| `src/lcc/src/gen.c` | `47` | Current secondary function walk complete; no new file-level gap isolated | [source-file plan](source-file-parity-audit-plan-2026-04-22.md) + current 2026-04-22 source walk | - |
| `src/lcc/src/init.c` | `10` | Current secondary function walk complete; no new file-level gap isolated | [source-file plan](source-file-parity-audit-plan-2026-04-22.md) + current 2026-04-22 source walk | - |
| `src/lcc/src/inits.c` | `1` | Current secondary function walk complete; no new file-level gap isolated | [source-file plan](source-file-parity-audit-plan-2026-04-22.md) + current 2026-04-22 source walk | - |
| `src/lcc/src/input.c` | `5` | Current secondary function walk complete; no new file-level gap isolated | [source-file plan](source-file-parity-audit-plan-2026-04-22.md) + current 2026-04-22 source walk | - |
| `src/lcc/src/lex.c` | `9` | Current secondary function walk complete; no new file-level gap isolated | [source-file plan](source-file-parity-audit-plan-2026-04-22.md) + current 2026-04-22 source walk | - |
| `src/lcc/src/list.c` | `3` | Current secondary function walk complete; no new file-level gap isolated | [source-file plan](source-file-parity-audit-plan-2026-04-22.md) + current 2026-04-22 source walk | - |
| `src/lcc/src/main.c` | `5` | Current secondary function walk complete; no new file-level gap isolated | [source-file plan](source-file-parity-audit-plan-2026-04-22.md) + current 2026-04-22 source walk | - |
| `src/lcc/src/null.c` | `25` | Current secondary function walk complete; no new file-level gap isolated | [source-file plan](source-file-parity-audit-plan-2026-04-22.md) + current 2026-04-22 source walk | - |
| `src/lcc/src/output.c` | `7` | Current secondary function walk complete; no new file-level gap isolated | [source-file plan](source-file-parity-audit-plan-2026-04-22.md) + current 2026-04-22 source walk | - |
| `src/lcc/src/pass2.c` | `23` | Current secondary function walk complete; no new file-level gap isolated | [source-file plan](source-file-parity-audit-plan-2026-04-22.md) + current 2026-04-22 source walk | - |
| `src/lcc/src/prof.c` | `8` | Current secondary function walk complete; no new file-level gap isolated | [source-file plan](source-file-parity-audit-plan-2026-04-22.md) + current 2026-04-22 source walk | - |
| `src/lcc/src/profio.c` | `11` | Current secondary function walk complete; no new file-level gap isolated | [source-file plan](source-file-parity-audit-plan-2026-04-22.md) + current 2026-04-22 source walk | - |
| `src/lcc/src/simp.c` | `14` | Current secondary function walk complete; no new file-level gap isolated | [source-file plan](source-file-parity-audit-plan-2026-04-22.md) + current 2026-04-22 source walk | - |
| `src/lcc/src/stab.c` | `11` | Current secondary function walk complete; no new file-level gap isolated | [source-file plan](source-file-parity-audit-plan-2026-04-22.md) + current 2026-04-22 source walk | - |
| `src/lcc/src/stmt.c` | `24` | Current secondary function walk complete; no new file-level gap isolated | [source-file plan](source-file-parity-audit-plan-2026-04-22.md) + current 2026-04-22 source walk | - |
| `src/lcc/src/string.c` | `3` | Current secondary function walk complete; no new file-level gap isolated | [source-file plan](source-file-parity-audit-plan-2026-04-22.md) + current 2026-04-22 source walk | - |
| `src/lcc/src/sym.c` | `21` | Current secondary function walk complete; no new file-level gap isolated | [source-file plan](source-file-parity-audit-plan-2026-04-22.md) + current 2026-04-22 source walk | - |
| `src/lcc/src/symbolic.c` | `32` | Current secondary function walk complete; no new file-level gap isolated | [source-file plan](source-file-parity-audit-plan-2026-04-22.md) + current 2026-04-22 source walk | - |
| `src/lcc/src/trace.c` | `6` | Current secondary function walk complete; no new file-level gap isolated | [source-file plan](source-file-parity-audit-plan-2026-04-22.md) + current 2026-04-22 source walk | - |
| `src/lcc/src/tree.c` | `9` | Current secondary function walk complete; no new file-level gap isolated | [source-file plan](source-file-parity-audit-plan-2026-04-22.md) + current 2026-04-22 source walk | - |
| `src/lcc/src/types.c` | `31` | Current secondary function walk complete; no new file-level gap isolated | [source-file plan](source-file-parity-audit-plan-2026-04-22.md) + current 2026-04-22 source walk | - |
| `src/lcc/tst/8q.c` | `0` | Current secondary function walk complete; no new file-level gap isolated | [source-file plan](source-file-parity-audit-plan-2026-04-22.md) + current 2026-04-22 source walk | - |
| `src/lcc/tst/array.c` | `0` | Current secondary function walk complete; no new file-level gap isolated | [source-file plan](source-file-parity-audit-plan-2026-04-22.md) + current 2026-04-22 source walk | - |
| `src/lcc/tst/cf.c` | `0` | Current secondary function walk complete; no new file-level gap isolated | [source-file plan](source-file-parity-audit-plan-2026-04-22.md) + current 2026-04-22 source walk | - |
| `src/lcc/tst/cq.c` | `2` | Current secondary function walk complete; no new file-level gap isolated | [source-file plan](source-file-parity-audit-plan-2026-04-22.md) + current 2026-04-22 source walk | - |
| `src/lcc/tst/cvt.c` | `1` | Current secondary function walk complete; no new file-level gap isolated | [source-file plan](source-file-parity-audit-plan-2026-04-22.md) + current 2026-04-22 source walk | - |
| `src/lcc/tst/fields.c` | `0` | Current secondary function walk complete; no new file-level gap isolated | [source-file plan](source-file-parity-audit-plan-2026-04-22.md) + current 2026-04-22 source walk | - |
| `src/lcc/tst/front.c` | `4` | Current secondary function walk complete; no new file-level gap isolated | [source-file plan](source-file-parity-audit-plan-2026-04-22.md) + current 2026-04-22 source walk | - |
| `src/lcc/tst/incr.c` | `0` | Current secondary function walk complete; no new file-level gap isolated | [source-file plan](source-file-parity-audit-plan-2026-04-22.md) + current 2026-04-22 source walk | - |
| `src/lcc/tst/init.c` | `0` | Current secondary function walk complete; no new file-level gap isolated | [source-file plan](source-file-parity-audit-plan-2026-04-22.md) + current 2026-04-22 source walk | - |
| `src/lcc/tst/limits.c` | `0` | Current secondary function walk complete; no new file-level gap isolated | [source-file plan](source-file-parity-audit-plan-2026-04-22.md) + current 2026-04-22 source walk | - |
| `src/lcc/tst/paranoia.c` | `2` | Current secondary function walk complete; no new file-level gap isolated | [source-file plan](source-file-parity-audit-plan-2026-04-22.md) + current 2026-04-22 source walk | - |
| `src/lcc/tst/sort.c` | `0` | Current secondary function walk complete; no new file-level gap isolated | [source-file plan](source-file-parity-audit-plan-2026-04-22.md) + current 2026-04-22 source walk | - |
| `src/lcc/tst/spill.c` | `0` | Current secondary function walk complete; no new file-level gap isolated | [source-file plan](source-file-parity-audit-plan-2026-04-22.md) + current 2026-04-22 source walk | - |
| `src/lcc/tst/stdarg.c` | `0` | Current secondary function walk complete; no new file-level gap isolated | [source-file plan](source-file-parity-audit-plan-2026-04-22.md) + current 2026-04-22 source walk | - |
| `src/lcc/tst/struct.c` | `5` | Current secondary function walk complete; no new file-level gap isolated | [source-file plan](source-file-parity-audit-plan-2026-04-22.md) + current 2026-04-22 source walk | - |
| `src/lcc/tst/switch.c` | `0` | Current secondary function walk complete; no new file-level gap isolated | [source-file plan](source-file-parity-audit-plan-2026-04-22.md) + current 2026-04-22 source walk | - |
| `src/lcc/tst/wf1.c` | `1` | Current secondary function walk complete; no new file-level gap isolated | [source-file plan](source-file-parity-audit-plan-2026-04-22.md) + current 2026-04-22 source walk | - |
| `src/lcc/tst/yacc.c` | `1` | Current secondary function walk complete; no new file-level gap isolated | [source-file plan](source-file-parity-audit-plan-2026-04-22.md) + current 2026-04-22 source walk | - |
### `src/libs` (25 files)

Current 2026-04-22 audit result: the tracked `src/libs` function walk
did not isolate any new file-level owners. The retained command-line,
JPEG, and pak-support helper sources remain a bounded secondary
support surface on current evidence.

| File | Functions | Current parity state | Primary evidence | Gap note |
| --- | ---: | --- | --- | --- |
| `src/libs/cmdlib/cmdlib.cpp` | `41` | Current secondary function walk complete; no new file-level gap isolated | [source-file plan](source-file-parity-audit-plan-2026-04-22.md) + current 2026-04-22 source walk | - |
| `src/libs/jpeg6/jcomapi.cpp` | `2` | Current secondary function walk complete; no new file-level gap isolated | [source-file plan](source-file-parity-audit-plan-2026-04-22.md) + current 2026-04-22 source walk | - |
| `src/libs/jpeg6/jdapimin.cpp` | `10` | Current secondary function walk complete; no new file-level gap isolated | [source-file plan](source-file-parity-audit-plan-2026-04-22.md) + current 2026-04-22 source walk | - |
| `src/libs/jpeg6/jdapistd.cpp` | `6` | Current secondary function walk complete; no new file-level gap isolated | [source-file plan](source-file-parity-audit-plan-2026-04-22.md) + current 2026-04-22 source walk | - |
| `src/libs/jpeg6/jdatasrc.cpp` | `5` | Current secondary function walk complete; no new file-level gap isolated | [source-file plan](source-file-parity-audit-plan-2026-04-22.md) + current 2026-04-22 source walk | - |
| `src/libs/jpeg6/jdcoefct.cpp` | `9` | Current secondary function walk complete; no new file-level gap isolated | [source-file plan](source-file-parity-audit-plan-2026-04-22.md) + current 2026-04-22 source walk | - |
| `src/libs/jpeg6/jdcolor.cpp` | `7` | Current secondary function walk complete; no new file-level gap isolated | [source-file plan](source-file-parity-audit-plan-2026-04-22.md) + current 2026-04-22 source walk | - |
| `src/libs/jpeg6/jddctmgr.cpp` | `2` | Current secondary function walk complete; no new file-level gap isolated | [source-file plan](source-file-parity-audit-plan-2026-04-22.md) + current 2026-04-22 source walk | - |
| `src/libs/jpeg6/jdhuff.cpp` | `6` | Current secondary function walk complete; no new file-level gap isolated | [source-file plan](source-file-parity-audit-plan-2026-04-22.md) + current 2026-04-22 source walk | - |
| `src/libs/jpeg6/jdinput.cpp` | `6` | Current secondary function walk complete; no new file-level gap isolated | [source-file plan](source-file-parity-audit-plan-2026-04-22.md) + current 2026-04-22 source walk | - |
| `src/libs/jpeg6/jdmainct.cpp` | `5` | Current secondary function walk complete; no new file-level gap isolated | [source-file plan](source-file-parity-audit-plan-2026-04-22.md) + current 2026-04-22 source walk | - |
| `src/libs/jpeg6/jdmarker.cpp` | `6` | Current secondary function walk complete; no new file-level gap isolated | [source-file plan](source-file-parity-audit-plan-2026-04-22.md) + current 2026-04-22 source walk | - |
| `src/libs/jpeg6/jdmaster.cpp` | `6` | Current secondary function walk complete; no new file-level gap isolated | [source-file plan](source-file-parity-audit-plan-2026-04-22.md) + current 2026-04-22 source walk | - |
| `src/libs/jpeg6/jdpostct.cpp` | `5` | Current secondary function walk complete; no new file-level gap isolated | [source-file plan](source-file-parity-audit-plan-2026-04-22.md) + current 2026-04-22 source walk | - |
| `src/libs/jpeg6/jdsample.cpp` | `10` | Current secondary function walk complete; no new file-level gap isolated | [source-file plan](source-file-parity-audit-plan-2026-04-22.md) + current 2026-04-22 source walk | - |
| `src/libs/jpeg6/jdtrans.cpp` | `1` | Current secondary function walk complete; no new file-level gap isolated | [source-file plan](source-file-parity-audit-plan-2026-04-22.md) + current 2026-04-22 source walk | - |
| `src/libs/jpeg6/jerror.cpp` | `5` | Current secondary function walk complete; no new file-level gap isolated | [source-file plan](source-file-parity-audit-plan-2026-04-22.md) + current 2026-04-22 source walk | - |
| `src/libs/jpeg6/jfdctflt.cpp` | `1` | Current secondary function walk complete; no new file-level gap isolated | [source-file plan](source-file-parity-audit-plan-2026-04-22.md) + current 2026-04-22 source walk | - |
| `src/libs/jpeg6/jidctflt.cpp` | `1` | Current secondary function walk complete; no new file-level gap isolated | [source-file plan](source-file-parity-audit-plan-2026-04-22.md) + current 2026-04-22 source walk | - |
| `src/libs/jpeg6/jmemmgr.cpp` | `4` | Current secondary function walk complete; no new file-level gap isolated | [source-file plan](source-file-parity-audit-plan-2026-04-22.md) + current 2026-04-22 source walk | - |
| `src/libs/jpeg6/jmemnobs.cpp` | `6` | Current secondary function walk complete; no new file-level gap isolated | [source-file plan](source-file-parity-audit-plan-2026-04-22.md) + current 2026-04-22 source walk | - |
| `src/libs/jpeg6/jpgload.cpp` | `1` | Current secondary function walk complete; no new file-level gap isolated | [source-file plan](source-file-parity-audit-plan-2026-04-22.md) + current 2026-04-22 source walk | - |
| `src/libs/jpeg6/jutils.cpp` | `0` | Current secondary function walk complete; no new file-level gap isolated | [source-file plan](source-file-parity-audit-plan-2026-04-22.md) + current 2026-04-22 source walk | - |
| `src/libs/pak/pakstuff.cpp` | `48` | Current secondary function walk complete; no new file-level gap isolated | [source-file plan](source-file-parity-audit-plan-2026-04-22.md) + current 2026-04-22 source walk | - |
| `src/libs/pak/unzip.cpp` | `61` | Current secondary function walk complete; no new file-level gap isolated | [source-file plan](source-file-parity-audit-plan-2026-04-22.md) + current 2026-04-22 source walk | - |
### `src/q3asm` (2 files)

Current 2026-04-22 audit result: the `src/q3asm` function walk did not
isolate any new file-level owners. This retained bytecode assembler
toolchain remains a bounded secondary support surface on current
evidence.

| File | Functions | Current parity state | Primary evidence | Gap note |
| --- | ---: | --- | --- | --- |
| `src/q3asm/cmdlib.c` | `58` | Current secondary function walk complete; no new file-level gap isolated | [source-file plan](source-file-parity-audit-plan-2026-04-22.md) + current 2026-04-22 source walk | - |
| `src/q3asm/q3asm.c` | `18` | Current secondary function walk complete; no new file-level gap isolated | [source-file plan](source-file-parity-audit-plan-2026-04-22.md) + current 2026-04-22 source walk | - |
### `src/q3map` (28 files)

Current 2026-04-22 audit result: the `src/q3map` function walk did not
isolate any new file-level owners. The retained map compile, light,
and vis toolchain remains a bounded secondary support surface on
current evidence.

| File | Functions | Current parity state | Primary evidence | Gap note |
| --- | ---: | --- | --- | --- |
| `src/q3map/brush.c` | `22` | Current secondary function walk complete; no new file-level gap isolated | [source-file plan](source-file-parity-audit-plan-2026-04-22.md) + current 2026-04-22 source walk | - |
| `src/q3map/brush_primit.c` | `1` | Current secondary function walk complete; no new file-level gap isolated | [source-file plan](source-file-parity-audit-plan-2026-04-22.md) + current 2026-04-22 source walk | - |
| `src/q3map/bsp.c` | `7` | Current secondary function walk complete; no new file-level gap isolated | [source-file plan](source-file-parity-audit-plan-2026-04-22.md) + current 2026-04-22 source walk | - |
| `src/q3map/facebsp.c` | `9` | Current secondary function walk complete; no new file-level gap isolated | [source-file plan](source-file-parity-audit-plan-2026-04-22.md) + current 2026-04-22 source walk | - |
| `src/q3map/fog.c` | `6` | Current secondary function walk complete; no new file-level gap isolated | [source-file plan](source-file-parity-audit-plan-2026-04-22.md) + current 2026-04-22 source walk | - |
| `src/q3map/gldraw.c` | `10` | Current secondary function walk complete; no new file-level gap isolated | [source-file plan](source-file-parity-audit-plan-2026-04-22.md) + current 2026-04-22 source walk | - |
| `src/q3map/glfile.c` | `5` | Current secondary function walk complete; no new file-level gap isolated | [source-file plan](source-file-parity-audit-plan-2026-04-22.md) + current 2026-04-22 source walk | - |
| `src/q3map/leakfile.c` | `1` | Current secondary function walk complete; no new file-level gap isolated | [source-file plan](source-file-parity-audit-plan-2026-04-22.md) + current 2026-04-22 source walk | - |
| `src/q3map/light.c` | `27` | Current secondary function walk complete; no new file-level gap isolated | [source-file plan](source-file-parity-audit-plan-2026-04-22.md) + current 2026-04-22 source walk | - |
| `src/q3map/light_trace.c` | `19` | Current secondary function walk complete; no new file-level gap isolated | [source-file plan](source-file-parity-audit-plan-2026-04-22.md) + current 2026-04-22 source walk | - |
| `src/q3map/lightmaps.c` | `5` | Current secondary function walk complete; no new file-level gap isolated | [source-file plan](source-file-parity-audit-plan-2026-04-22.md) + current 2026-04-22 source walk | - |
| `src/q3map/lightv.c` | `76` | Current secondary function walk complete; no new file-level gap isolated | [source-file plan](source-file-parity-audit-plan-2026-04-22.md) + current 2026-04-22 source walk | - |
| `src/q3map/map.c` | `22` | Current secondary function walk complete; no new file-level gap isolated | [source-file plan](source-file-parity-audit-plan-2026-04-22.md) + current 2026-04-22 source walk | - |
| `src/q3map/mesh.c` | `13` | Current secondary function walk complete; no new file-level gap isolated | [source-file plan](source-file-parity-audit-plan-2026-04-22.md) + current 2026-04-22 source walk | - |
| `src/q3map/misc_model.c` | `5` | Current secondary function walk complete; no new file-level gap isolated | [source-file plan](source-file-parity-audit-plan-2026-04-22.md) + current 2026-04-22 source walk | - |
| `src/q3map/nodraw.c` | `4` | Current secondary function walk complete; no new file-level gap isolated | [source-file plan](source-file-parity-audit-plan-2026-04-22.md) + current 2026-04-22 source walk | - |
| `src/q3map/patch.c` | `5` | Current secondary function walk complete; no new file-level gap isolated | [source-file plan](source-file-parity-audit-plan-2026-04-22.md) + current 2026-04-22 source walk | - |
| `src/q3map/portals.c` | `22` | Current secondary function walk complete; no new file-level gap isolated | [source-file plan](source-file-parity-audit-plan-2026-04-22.md) + current 2026-04-22 source walk | - |
| `src/q3map/prtfile.c` | `6` | Current secondary function walk complete; no new file-level gap isolated | [source-file plan](source-file-parity-audit-plan-2026-04-22.md) + current 2026-04-22 source walk | - |
| `src/q3map/shaders.c` | `6` | Current secondary function walk complete; no new file-level gap isolated | [source-file plan](source-file-parity-audit-plan-2026-04-22.md) + current 2026-04-22 source walk | - |
| `src/q3map/soundv.c` | `76` | Current secondary function walk complete; no new file-level gap isolated | [source-file plan](source-file-parity-audit-plan-2026-04-22.md) + current 2026-04-22 source walk | - |
| `src/q3map/surface.c` | `24` | Current secondary function walk complete; no new file-level gap isolated | [source-file plan](source-file-parity-audit-plan-2026-04-22.md) + current 2026-04-22 source walk | - |
| `src/q3map/terrain.c` | `21` | Current secondary function walk complete; no new file-level gap isolated | [source-file plan](source-file-parity-audit-plan-2026-04-22.md) + current 2026-04-22 source walk | - |
| `src/q3map/tjunction.c` | `8` | Current secondary function walk complete; no new file-level gap isolated | [source-file plan](source-file-parity-audit-plan-2026-04-22.md) + current 2026-04-22 source walk | - |
| `src/q3map/tree.c` | `5` | Current secondary function walk complete; no new file-level gap isolated | [source-file plan](source-file-parity-audit-plan-2026-04-22.md) + current 2026-04-22 source walk | - |
| `src/q3map/vis.c` | `24` | Current secondary function walk complete; no new file-level gap isolated | [source-file plan](source-file-parity-audit-plan-2026-04-22.md) + current 2026-04-22 source walk | - |
| `src/q3map/visflow.c` | `20` | Current secondary function walk complete; no new file-level gap isolated | [source-file plan](source-file-parity-audit-plan-2026-04-22.md) + current 2026-04-22 source walk | - |
| `src/q3map/writebsp.c` | `11` | Current secondary function walk complete; no new file-level gap isolated | [source-file plan](source-file-parity-audit-plan-2026-04-22.md) + current 2026-04-22 source walk | - |
### `src/q3radiant` (97 files)

Current 2026-04-22 audit result: the `src/q3radiant` function walk did
not isolate any new file-level owners. The retained Radiant editor
shell, plugin bridge, OpenGL host glue, and bundled spline/editor
helper sources remain a bounded secondary support surface on current
evidence.

| File | Functions | Current parity state | Primary evidence | Gap note |
| --- | ---: | --- | --- | --- |
| `src/q3radiant/BSInput.cpp` | `2` | Current secondary function walk complete; no new file-level gap isolated | [source-file plan](source-file-parity-audit-plan-2026-04-22.md) + current 2026-04-22 source walk | - |
| `src/q3radiant/Bmp.cpp` | `11` | Current secondary function walk complete; no new file-level gap isolated | [source-file plan](source-file-parity-audit-plan-2026-04-22.md) + current 2026-04-22 source walk | - |
| `src/q3radiant/Brush.cpp` | `77` | Current secondary function walk complete; no new file-level gap isolated | [source-file plan](source-file-parity-audit-plan-2026-04-22.md) + current 2026-04-22 source walk | - |
| `src/q3radiant/BrushScript.cpp` | `28` | Current secondary function walk complete; no new file-level gap isolated | [source-file plan](source-file-parity-audit-plan-2026-04-22.md) + current 2026-04-22 source walk | - |
| `src/q3radiant/CSG.CPP` | `8` | Current secondary function walk complete; no new file-level gap isolated | [source-file plan](source-file-parity-audit-plan-2026-04-22.md) + current 2026-04-22 source walk | - |
| `src/q3radiant/CamWnd.cpp` | `34` | Current secondary function walk complete; no new file-level gap isolated | [source-file plan](source-file-parity-audit-plan-2026-04-22.md) + current 2026-04-22 source walk | - |
| `src/q3radiant/CapDialog.cpp` | `1` | Current secondary function walk complete; no new file-level gap isolated | [source-file plan](source-file-parity-audit-plan-2026-04-22.md) + current 2026-04-22 source walk | - |
| `src/q3radiant/ChildFrm.cpp` | `1` | Current secondary function walk complete; no new file-level gap isolated | [source-file plan](source-file-parity-audit-plan-2026-04-22.md) + current 2026-04-22 source walk | - |
| `src/q3radiant/CommandsDlg.cpp` | `2` | Current secondary function walk complete; no new file-level gap isolated | [source-file plan](source-file-parity-audit-plan-2026-04-22.md) + current 2026-04-22 source walk | - |
| `src/q3radiant/DRAG.CPP` | `7` | Current secondary function walk complete; no new file-level gap isolated | [source-file plan](source-file-parity-audit-plan-2026-04-22.md) + current 2026-04-22 source walk | - |
| `src/q3radiant/DialogInfo.cpp` | `4` | Current secondary function walk complete; no new file-level gap isolated | [source-file plan](source-file-parity-audit-plan-2026-04-22.md) + current 2026-04-22 source walk | - |
| `src/q3radiant/DialogTextures.cpp` | `4` | Current secondary function walk complete; no new file-level gap isolated | [source-file plan](source-file-parity-audit-plan-2026-04-22.md) + current 2026-04-22 source walk | - |
| `src/q3radiant/DialogThick.cpp` | `1` | Current secondary function walk complete; no new file-level gap isolated | [source-file plan](source-file-parity-audit-plan-2026-04-22.md) + current 2026-04-22 source walk | - |
| `src/q3radiant/DlgEvent.cpp` | `1` | Current secondary function walk complete; no new file-level gap isolated | [source-file plan](source-file-parity-audit-plan-2026-04-22.md) + current 2026-04-22 source walk | - |
| `src/q3radiant/ECLASS.CPP` | `13` | Current secondary function walk complete; no new file-level gap isolated | [source-file plan](source-file-parity-audit-plan-2026-04-22.md) + current 2026-04-22 source walk | - |
| `src/q3radiant/ENTITY.CPP` | `29` | Current secondary function walk complete; no new file-level gap isolated | [source-file plan](source-file-parity-audit-plan-2026-04-22.md) + current 2026-04-22 source walk | - |
| `src/q3radiant/EditWnd.cpp` | `1` | Current secondary function walk complete; no new file-level gap isolated | [source-file plan](source-file-parity-audit-plan-2026-04-22.md) + current 2026-04-22 source walk | - |
| `src/q3radiant/EntityListDlg.cpp` | `6` | Current secondary function walk complete; no new file-level gap isolated | [source-file plan](source-file-parity-audit-plan-2026-04-22.md) + current 2026-04-22 source walk | - |
| `src/q3radiant/FNMATCH.CPP` | `1` | Current secondary function walk complete; no new file-level gap isolated | [source-file plan](source-file-parity-audit-plan-2026-04-22.md) + current 2026-04-22 source walk | - |
| `src/q3radiant/FindTextureDlg.cpp` | `12` | Current secondary function walk complete; no new file-level gap isolated | [source-file plan](source-file-parity-audit-plan-2026-04-22.md) + current 2026-04-22 source walk | - |
| `src/q3radiant/GLInterface.cpp` | `4` | Current secondary function walk complete; no new file-level gap isolated | [source-file plan](source-file-parity-audit-plan-2026-04-22.md) + current 2026-04-22 source walk | - |
| `src/q3radiant/GroupBar.cpp` | `4` | Current secondary function walk complete; no new file-level gap isolated | [source-file plan](source-file-parity-audit-plan-2026-04-22.md) + current 2026-04-22 source walk | - |
| `src/q3radiant/GroupDlg.cpp` | `33` | Current secondary function walk complete; no new file-level gap isolated | [source-file plan](source-file-parity-audit-plan-2026-04-22.md) + current 2026-04-22 source walk | - |
| `src/q3radiant/IEpairs.cpp` | `6` | Current secondary function walk complete; no new file-level gap isolated | [source-file plan](source-file-parity-audit-plan-2026-04-22.md) + current 2026-04-22 source walk | - |
| `src/q3radiant/IShaders.cpp` | `1` | Current secondary function walk complete; no new file-level gap isolated | [source-file plan](source-file-parity-audit-plan-2026-04-22.md) + current 2026-04-22 source walk | - |
| `src/q3radiant/LBMLIB.CPP` | `18` | Current secondary function walk complete; no new file-level gap isolated | [source-file plan](source-file-parity-audit-plan-2026-04-22.md) + current 2026-04-22 source walk | - |
| `src/q3radiant/LstToolBar.cpp` | `1` | Current secondary function walk complete; no new file-level gap isolated | [source-file plan](source-file-parity-audit-plan-2026-04-22.md) + current 2026-04-22 source walk | - |
| `src/q3radiant/MAP.CPP` | `26` | Current secondary function walk complete; no new file-level gap isolated | [source-file plan](source-file-parity-audit-plan-2026-04-22.md) + current 2026-04-22 source walk | - |
| `src/q3radiant/MATHLIB.CPP` | `23` | Current secondary function walk complete; no new file-level gap isolated | [source-file plan](source-file-parity-audit-plan-2026-04-22.md) + current 2026-04-22 source walk | - |
| `src/q3radiant/MRU.CPP` | `15` | Current secondary function walk complete; no new file-level gap isolated | [source-file plan](source-file-parity-audit-plan-2026-04-22.md) + current 2026-04-22 source walk | - |
| `src/q3radiant/MainFrm.cpp` | `348` | Current secondary function walk complete; no new file-level gap isolated | [source-file plan](source-file-parity-audit-plan-2026-04-22.md) + current 2026-04-22 source walk | - |
| `src/q3radiant/MapInfo.cpp` | `2` | Current secondary function walk complete; no new file-level gap isolated | [source-file plan](source-file-parity-audit-plan-2026-04-22.md) + current 2026-04-22 source walk | - |
| `src/q3radiant/Messaging.cpp` | `10` | Current secondary function walk complete; no new file-level gap isolated | [source-file plan](source-file-parity-audit-plan-2026-04-22.md) + current 2026-04-22 source walk | - |
| `src/q3radiant/NameDlg.cpp` | `3` | Current secondary function walk complete; no new file-level gap isolated | [source-file plan](source-file-parity-audit-plan-2026-04-22.md) + current 2026-04-22 source walk | - |
| `src/q3radiant/NewProjDlg.cpp` | `1` | Current secondary function walk complete; no new file-level gap isolated | [source-file plan](source-file-parity-audit-plan-2026-04-22.md) + current 2026-04-22 source walk | - |
| `src/q3radiant/PARSE.CPP` | `4` | Current secondary function walk complete; no new file-level gap isolated | [source-file plan](source-file-parity-audit-plan-2026-04-22.md) + current 2026-04-22 source walk | - |
| `src/q3radiant/PMESH.CPP` | `125` | Current secondary function walk complete; no new file-level gap isolated | [source-file plan](source-file-parity-audit-plan-2026-04-22.md) + current 2026-04-22 source walk | - |
| `src/q3radiant/POINTS.CPP` | `6` | Current secondary function walk complete; no new file-level gap isolated | [source-file plan](source-file-parity-audit-plan-2026-04-22.md) + current 2026-04-22 source walk | - |
| `src/q3radiant/PatchDensityDlg.cpp` | `3` | Current secondary function walk complete; no new file-level gap isolated | [source-file plan](source-file-parity-audit-plan-2026-04-22.md) + current 2026-04-22 source walk | - |
| `src/q3radiant/PatchDialog.cpp` | `20` | Current secondary function walk complete; no new file-level gap isolated | [source-file plan](source-file-parity-audit-plan-2026-04-22.md) + current 2026-04-22 source walk | - |
| `src/q3radiant/PlugIn.cpp` | `17` | Current secondary function walk complete; no new file-level gap isolated | [source-file plan](source-file-parity-audit-plan-2026-04-22.md) + current 2026-04-22 source walk | - |
| `src/q3radiant/PlugInManager.cpp` | `93` | Current secondary function walk complete; no new file-level gap isolated | [source-file plan](source-file-parity-audit-plan-2026-04-22.md) + current 2026-04-22 source walk | - |
| `src/q3radiant/PluginEntities.cpp` | `1` | Current secondary function walk complete; no new file-level gap isolated | [source-file plan](source-file-parity-audit-plan-2026-04-22.md) + current 2026-04-22 source walk | - |
| `src/q3radiant/PrefsDlg.cpp` | `11` | Current secondary function walk complete; no new file-level gap isolated | [source-file plan](source-file-parity-audit-plan-2026-04-22.md) + current 2026-04-22 source walk | - |
| `src/q3radiant/QE3.CPP` | `20` | Current secondary function walk complete; no new file-level gap isolated | [source-file plan](source-file-parity-audit-plan-2026-04-22.md) + current 2026-04-22 source walk | - |
| `src/q3radiant/QGL_WIN.C` | `2` | Current secondary function walk complete; no new file-level gap isolated | [source-file plan](source-file-parity-audit-plan-2026-04-22.md) + current 2026-04-22 source walk | - |
| `src/q3radiant/QGL_WIN.CPP` | `2` | Current secondary function walk complete; no new file-level gap isolated | [source-file plan](source-file-parity-audit-plan-2026-04-22.md) + current 2026-04-22 source walk | - |
| `src/q3radiant/RADBSP.CPP` | `1` | Current secondary function walk complete; no new file-level gap isolated | [source-file plan](source-file-parity-audit-plan-2026-04-22.md) + current 2026-04-22 source walk | - |
| `src/q3radiant/RADEditView.cpp` | `2` | Current secondary function walk complete; no new file-level gap isolated | [source-file plan](source-file-parity-audit-plan-2026-04-22.md) + current 2026-04-22 source walk | - |
| `src/q3radiant/RADEditWnd.cpp` | `2` | Current secondary function walk complete; no new file-level gap isolated | [source-file plan](source-file-parity-audit-plan-2026-04-22.md) + current 2026-04-22 source walk | - |
| `src/q3radiant/Radiant.cpp` | `4` | Current secondary function walk complete; no new file-level gap isolated | [source-file plan](source-file-parity-audit-plan-2026-04-22.md) + current 2026-04-22 source walk | - |
| `src/q3radiant/RadiantDoc.cpp` | `2` | Current secondary function walk complete; no new file-level gap isolated | [source-file plan](source-file-parity-audit-plan-2026-04-22.md) + current 2026-04-22 source walk | - |
| `src/q3radiant/RadiantView.cpp` | `5` | Current secondary function walk complete; no new file-level gap isolated | [source-file plan](source-file-parity-audit-plan-2026-04-22.md) + current 2026-04-22 source walk | - |
| `src/q3radiant/RotateDlg.cpp` | `8` | Current secondary function walk complete; no new file-level gap isolated | [source-file plan](source-file-parity-audit-plan-2026-04-22.md) + current 2026-04-22 source walk | - |
| `src/q3radiant/SELECT.CPP` | `43` | Current secondary function walk complete; no new file-level gap isolated | [source-file plan](source-file-parity-audit-plan-2026-04-22.md) + current 2026-04-22 source walk | - |
| `src/q3radiant/ScaleDialog.cpp` | `1` | Current secondary function walk complete; no new file-level gap isolated | [source-file plan](source-file-parity-audit-plan-2026-04-22.md) + current 2026-04-22 source walk | - |
| `src/q3radiant/ScriptDlg.cpp` | `4` | Current secondary function walk complete; no new file-level gap isolated | [source-file plan](source-file-parity-audit-plan-2026-04-22.md) + current 2026-04-22 source walk | - |
| `src/q3radiant/SelectedFace.cpp` | `4` | Current secondary function walk complete; no new file-level gap isolated | [source-file plan](source-file-parity-audit-plan-2026-04-22.md) + current 2026-04-22 source walk | - |
| `src/q3radiant/ShaderEdit.cpp` | `1` | Current secondary function walk complete; no new file-level gap isolated | [source-file plan](source-file-parity-audit-plan-2026-04-22.md) + current 2026-04-22 source walk | - |
| `src/q3radiant/ShaderInfo.cpp` | `2` | Current secondary function walk complete; no new file-level gap isolated | [source-file plan](source-file-parity-audit-plan-2026-04-22.md) + current 2026-04-22 source walk | - |
| `src/q3radiant/StdAfx.cpp` | `0` | Current secondary function walk complete; no new file-level gap isolated | [source-file plan](source-file-parity-audit-plan-2026-04-22.md) + current 2026-04-22 source walk | - |
| `src/q3radiant/SurfaceDlg.cpp` | `31` | Current secondary function walk complete; no new file-level gap isolated | [source-file plan](source-file-parity-audit-plan-2026-04-22.md) + current 2026-04-22 source walk | - |
| `src/q3radiant/SurfacePlugin.cpp` | `1` | Current secondary function walk complete; no new file-level gap isolated | [source-file plan](source-file-parity-audit-plan-2026-04-22.md) + current 2026-04-22 source walk | - |
| `src/q3radiant/TexEdit.cpp` | `3` | Current secondary function walk complete; no new file-level gap isolated | [source-file plan](source-file-parity-audit-plan-2026-04-22.md) + current 2026-04-22 source walk | - |
| `src/q3radiant/TexWnd.cpp` | `68` | Current secondary function walk complete; no new file-level gap isolated | [source-file plan](source-file-parity-audit-plan-2026-04-22.md) + current 2026-04-22 source walk | - |
| `src/q3radiant/TextureBar.cpp` | `11` | Current secondary function walk complete; no new file-level gap isolated | [source-file plan](source-file-parity-audit-plan-2026-04-22.md) + current 2026-04-22 source walk | - |
| `src/q3radiant/TextureLayout.cpp` | `3` | Current secondary function walk complete; no new file-level gap isolated | [source-file plan](source-file-parity-audit-plan-2026-04-22.md) + current 2026-04-22 source walk | - |
| `src/q3radiant/TextureLoad.cpp` | `3` | Current secondary function walk complete; no new file-level gap isolated | [source-file plan](source-file-parity-audit-plan-2026-04-22.md) + current 2026-04-22 source walk | - |
| `src/q3radiant/ToolWnd.cpp` | `0` | Current secondary function walk complete; no new file-level gap isolated | [source-file plan](source-file-parity-audit-plan-2026-04-22.md) + current 2026-04-22 source walk | - |
| `src/q3radiant/Undo.cpp` | `23` | Current secondary function walk complete; no new file-level gap isolated | [source-file plan](source-file-parity-audit-plan-2026-04-22.md) + current 2026-04-22 source walk | - |
| `src/q3radiant/VERTSEL.CPP` | `7` | Current secondary function walk complete; no new file-level gap isolated | [source-file plan](source-file-parity-audit-plan-2026-04-22.md) + current 2026-04-22 source walk | - |
| `src/q3radiant/WIN_CAM.CPP` | `2` | Current secondary function walk complete; no new file-level gap isolated | [source-file plan](source-file-parity-audit-plan-2026-04-22.md) + current 2026-04-22 source walk | - |
| `src/q3radiant/WIN_DLG.CPP` | `17` | Current secondary function walk complete; no new file-level gap isolated | [source-file plan](source-file-parity-audit-plan-2026-04-22.md) + current 2026-04-22 source walk | - |
| `src/q3radiant/WIN_QE3.CPP` | `34` | Current secondary function walk complete; no new file-level gap isolated | [source-file plan](source-file-parity-audit-plan-2026-04-22.md) + current 2026-04-22 source walk | - |
| `src/q3radiant/WIN_XY.CPP` | `4` | Current secondary function walk complete; no new file-level gap isolated | [source-file plan](source-file-parity-audit-plan-2026-04-22.md) + current 2026-04-22 source walk | - |
| `src/q3radiant/WIN_Z.CPP` | `2` | Current secondary function walk complete; no new file-level gap isolated | [source-file plan](source-file-parity-audit-plan-2026-04-22.md) + current 2026-04-22 source walk | - |
| `src/q3radiant/WaveOpen.cpp` | `3` | Current secondary function walk complete; no new file-level gap isolated | [source-file plan](source-file-parity-audit-plan-2026-04-22.md) + current 2026-04-22 source walk | - |
| `src/q3radiant/Win_ent.cpp` | `21` | Current secondary function walk complete; no new file-level gap isolated | [source-file plan](source-file-parity-audit-plan-2026-04-22.md) + current 2026-04-22 source walk | - |
| `src/q3radiant/Win_main.cpp` | `24` | Current secondary function walk complete; no new file-level gap isolated | [source-file plan](source-file-parity-audit-plan-2026-04-22.md) + current 2026-04-22 source walk | - |
| `src/q3radiant/Winding.cpp` | `21` | Current secondary function walk complete; no new file-level gap isolated | [source-file plan](source-file-parity-audit-plan-2026-04-22.md) + current 2026-04-22 source walk | - |
| `src/q3radiant/XYWnd.cpp` | `97` | Current secondary function walk complete; no new file-level gap isolated | [source-file plan](source-file-parity-audit-plan-2026-04-22.md) + current 2026-04-22 source walk | - |
| `src/q3radiant/Z.CPP` | `7` | Current secondary function walk complete; no new file-level gap isolated | [source-file plan](source-file-parity-audit-plan-2026-04-22.md) + current 2026-04-22 source walk | - |
| `src/q3radiant/ZView.cpp` | `11` | Current secondary function walk complete; no new file-level gap isolated | [source-file plan](source-file-parity-audit-plan-2026-04-22.md) + current 2026-04-22 source walk | - |
| `src/q3radiant/ZWnd.cpp` | `19` | Current secondary function walk complete; no new file-level gap isolated | [source-file plan](source-file-parity-audit-plan-2026-04-22.md) + current 2026-04-22 source walk | - |
| `src/q3radiant/brush_primit.cpp` | `12` | Current secondary function walk complete; no new file-level gap isolated | [source-file plan](source-file-parity-audit-plan-2026-04-22.md) + current 2026-04-22 source walk | - |
| `src/q3radiant/cameratargetdlg.cpp` | `2` | Current secondary function walk complete; no new file-level gap isolated | [source-file plan](source-file-parity-audit-plan-2026-04-22.md) + current 2026-04-22 source walk | - |
| `src/q3radiant/cbrushstub.cpp` | `21` | Current secondary function walk complete; no new file-level gap isolated | [source-file plan](source-file-parity-audit-plan-2026-04-22.md) + current 2026-04-22 source walk | - |
| `src/q3radiant/dlgcamera.cpp` | `25` | Current secondary function walk complete; no new file-level gap isolated | [source-file plan](source-file-parity-audit-plan-2026-04-22.md) + current 2026-04-22 source walk | - |
| `src/q3radiant/splines/math_angles.cpp` | `7` | Current secondary function walk complete; no new file-level gap isolated | [source-file plan](source-file-parity-audit-plan-2026-04-22.md) + current 2026-04-22 source walk | - |
| `src/q3radiant/splines/math_matrix.cpp` | `6` | Current secondary function walk complete; no new file-level gap isolated | [source-file plan](source-file-parity-audit-plan-2026-04-22.md) + current 2026-04-22 source walk | - |
| `src/q3radiant/splines/math_quaternion.cpp` | `3` | Current secondary function walk complete; no new file-level gap isolated | [source-file plan](source-file-parity-audit-plan-2026-04-22.md) + current 2026-04-22 source walk | - |
| `src/q3radiant/splines/math_vector.cpp` | `5` | Current secondary function walk complete; no new file-level gap isolated | [source-file plan](source-file-parity-audit-plan-2026-04-22.md) + current 2026-04-22 source walk | - |
| `src/q3radiant/splines/q_parse.cpp` | `19` | Current secondary function walk complete; no new file-level gap isolated | [source-file plan](source-file-parity-audit-plan-2026-04-22.md) + current 2026-04-22 source walk | - |
| `src/q3radiant/splines/q_shared.cpp` | `47` | Current secondary function walk complete; no new file-level gap isolated | [source-file plan](source-file-parity-audit-plan-2026-04-22.md) + current 2026-04-22 source walk | - |
| `src/q3radiant/splines/splines.cpp` | `45` | Current secondary function walk complete; no new file-level gap isolated | [source-file plan](source-file-parity-audit-plan-2026-04-22.md) + current 2026-04-22 source walk | - |
| `src/q3radiant/splines/util_str.cpp` | `19` | Current secondary function walk complete; no new file-level gap isolated | [source-file plan](source-file-parity-audit-plan-2026-04-22.md) + current 2026-04-22 source walk | - |
| `src/q3radiant/terrain.cpp` | `56` | Current secondary function walk complete; no new file-level gap isolated | [source-file plan](source-file-parity-audit-plan-2026-04-22.md) + current 2026-04-22 source walk | - |
