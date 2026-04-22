# Source-File Parity Ledger

Last updated: 2026-04-22

## Purpose

This is the clean main parity document for the new source-file campaign. It keeps one concise row per tracked source file while leaving the detailed reasoning in the existing subsystem audits and in the new per-file gap notes.

The ledger does not replace the current gate-facing ledgers. `AUDIT.md`, `IMPLEMENTATION_PLAN.md`, and `repo-wide-parity-audit-2026-04-21.md` remain the high-level summary sources.

## Scope

- Tracked compilation units under `src/` excluding generated/vendor mirror trees under `src/libs/_deps/` and `src/libs/_build/`: `566` files.
- Header exception tracked because it owns an active repo-wide gap policy surface: `1` file.
- Total tracked source entries in this ledger: `567`.
- Function counts are approximate source-definition counts from the checked-in tree and are meant for audit triage, not for ABI accounting.

## Status legend

- `walked-closed`: The 2026-04-22 campaign has rerun the full file walk for this file and did not isolate a new file-level gap.
- `baseline-closed`: Subsystem or strict-retail closure already exists; this 2026-04-22 campaign has not yet rerun the full file walk.
- `gap-note-open`: A concrete file-level parity gap is already evidenced and has a dedicated note.
- `compatibility-open`: The file sits inside an open repo-wide compatibility or portability lane; a file-specific gap note will be added once the function walk isolates it.
- `queued-secondary`: The file belongs to a secondary tool, editor, compiler, or legacy support tree; it is catalogued now and queued after the primary runtime surface.

## Current totals

- `walked-closed`: `192` files
- `baseline-closed`: `9` files
- `gap-note-open`: `15` files
- `compatibility-open`: `9` files
- `queued-secondary`: `342` files

## Active file-level gap notes

| File | Gap family | Note |
| --- | --- | --- |
| `src/common/platform/platform_config.h` | `RW-G01` | [note](source-file-gap-notes/rw-g01-platform-config.md) |
| `src/common/platform/platform_services.c` | `RW-G01` | [note](source-file-gap-notes/rw-g01-platform-services.md) |
| `src/common/platform/backends/platform_backend_open_steam.c` | `RW-G01` | [note](source-file-gap-notes/rw-g01-open-steam-backend.md) |
| `src/common/platform/backends/platform_backend_steamworks.c` | `RW-G01` | [note](source-file-gap-notes/rw-g01-steamworks-backend.md) |
| `src/code/client/ql_auth.c` | `RW-G01` | [note](source-file-gap-notes/rw-g01-client-auth.md) |
| `src/code/client/cl_steam_resources.c` | `RW-G01` | [note](source-file-gap-notes/rw-g01-client-steam-resources.md) |
| `src/code/server/sv_rankings.c` | `RW-G01` | [note](source-file-gap-notes/rw-g01-server-rankings.md) |
| `src/code/unix/unix_main.c` | `RW-G02` | [note](source-file-gap-notes/rw-g02-unix-main.md) |
| `src/code/unix/linux_glimp.c` | `RW-G02` | [note](source-file-gap-notes/rw-g02-linux-glimp.md) |
| `src/code/unix/linux_snd.c` | `RW-G02` | [note](source-file-gap-notes/rw-g02-linux-snd.md) |
| `src/code/unix/linux_joystick.c` | `RW-G02` | [note](source-file-gap-notes/rw-g02-linux-joystick.md) |
| `src/code/null/null_main.c` | `RW-G02` | [note](source-file-gap-notes/rw-g02-null-main.md) |
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
| `src/common/platform/backends/platform_backend_open_steam.c` | `1` | RW-G01 file-level note open | [repo-wide audit](repo-wide-parity-audit-2026-04-21.md) + [gap note](source-file-gap-notes/rw-g01-open-steam-backend.md) | [note](source-file-gap-notes/rw-g01-open-steam-backend.md) |
| `src/common/platform/backends/platform_backend_steamworks.c` | `1` | RW-G01 file-level note open | [repo-wide audit](repo-wide-parity-audit-2026-04-21.md) + [gap note](source-file-gap-notes/rw-g01-steamworks-backend.md) | [note](source-file-gap-notes/rw-g01-steamworks-backend.md) |
| `src/common/platform/platform_services.c` | `6` | RW-G01 file-level note open | [repo-wide audit](repo-wide-parity-audit-2026-04-21.md) + [gap note](source-file-gap-notes/rw-g01-platform-services.md) | [note](source-file-gap-notes/rw-g01-platform-services.md) |
| `src/common/platform/platform_steamworks.c` | `142` | Current function walk complete; no new file-level gap isolated | [engine-wide closure](engine-full-parity-audit-and-implementation-plan-2026-04-10.md) + current 2026-04-22 source walk | - |
| `src/common/polylib.c` | `17` | Current function walk complete; no new file-level gap isolated | [engine-wide closure](engine-full-parity-audit-and-implementation-plan-2026-04-10.md) + current 2026-04-22 source walk | - |
| `src/common/scriplib.c` | `14` | Current function walk complete; no new file-level gap isolated | [engine-wide closure](engine-full-parity-audit-and-implementation-plan-2026-04-10.md) + current 2026-04-22 source walk | - |
| `src/common/threads.c` | `19` | Current function walk complete; no new file-level gap isolated | [engine-wide closure](engine-full-parity-audit-and-implementation-plan-2026-04-10.md) + current 2026-04-22 source walk | - |
| `src/common/trilib.c` | `3` | Current function walk complete; no new file-level gap isolated | [engine-wide closure](engine-full-parity-audit-and-implementation-plan-2026-04-10.md) + current 2026-04-22 source walk | - |
| `src/common/platform/platform_config.h` | `n/a` | RW-G01 file-level note open | [repo-wide audit](repo-wide-parity-audit-2026-04-21.md) + [gap note](source-file-gap-notes/rw-g01-platform-config.md) | [note](source-file-gap-notes/rw-g01-platform-config.md) |
### `src/code/client` (22 files)

Current 2026-04-22 audit result: the `src/code/client` function walk did
not isolate any new file-level owners beyond the already-seeded `RW-G01`
compatibility-policy notes. The strict-retail client register remains
closed on current evidence, while `ql_auth.c` and
`cl_steam_resources.c` continue to own the repo-wide bounded
online-services story inside this tree.

| File | Functions | Current parity state | Primary evidence | Gap note |
| --- | ---: | --- | --- | --- |
| `src/code/client/cl_cgame.c` | `177` | Current function walk complete; no new file-level gap isolated | [client audit](client-full-parity-audit-and-implementation-plan-2026-04-09.md) + current 2026-04-22 source walk | - |
| `src/code/client/cl_cin.c` | `46` | Current function walk complete; no new file-level gap isolated | [client audit](client-full-parity-audit-and-implementation-plan-2026-04-09.md) + current 2026-04-22 source walk | - |
| `src/code/client/cl_console.c` | `45` | Current function walk complete; no new file-level gap isolated | [client audit](client-full-parity-audit-and-implementation-plan-2026-04-09.md) + current 2026-04-22 source walk | - |
| `src/code/client/cl_input.c` | `80` | Current function walk complete; no new file-level gap isolated | [client audit](client-full-parity-audit-and-implementation-plan-2026-04-09.md) + current 2026-04-22 source walk | - |
| `src/code/client/cl_input_translation.c` | `3` | Current function walk complete; no new file-level gap isolated | [client audit](client-full-parity-audit-and-implementation-plan-2026-04-09.md) + current 2026-04-22 source walk | - |
| `src/code/client/cl_keys.c` | `37` | Current function walk complete; no new file-level gap isolated | [client audit](client-full-parity-audit-and-implementation-plan-2026-04-09.md) + current 2026-04-22 source walk | - |
| `src/code/client/cl_main.c` | `163` | Current function walk complete; no new file-level gap isolated | [client audit](client-full-parity-audit-and-implementation-plan-2026-04-09.md) + current 2026-04-22 source walk | - |
| `src/code/client/cl_net_chan.c` | `5` | Current function walk complete; no new file-level gap isolated | [client audit](client-full-parity-audit-and-implementation-plan-2026-04-09.md) + current 2026-04-22 source walk | - |
| `src/code/client/cl_parse.c` | `9` | Current function walk complete; no new file-level gap isolated | [client audit](client-full-parity-audit-and-implementation-plan-2026-04-09.md) + current 2026-04-22 source walk | - |
| `src/code/client/cl_screenshot_io.c` | `3` | Current function walk complete; no new file-level gap isolated | [client audit](client-full-parity-audit-and-implementation-plan-2026-04-09.md) + current 2026-04-22 source walk | - |
| `src/code/client/cl_scrn.c` | `18` | Current function walk complete; no new file-level gap isolated | [client audit](client-full-parity-audit-and-implementation-plan-2026-04-09.md) + current 2026-04-22 source walk | - |
| `src/code/client/cl_steam_resources.c` | `20` | RW-G01 file-level note open | [repo-wide audit](repo-wide-parity-audit-2026-04-21.md) + [gap note](source-file-gap-notes/rw-g01-client-steam-resources.md) | [note](source-file-gap-notes/rw-g01-client-steam-resources.md) |
| `src/code/client/cl_ui.c` | `61` | Current function walk complete; no new file-level gap isolated | [client audit](client-full-parity-audit-and-implementation-plan-2026-04-09.md) + current 2026-04-22 source walk | - |
| `src/code/client/cl_webpak.c` | `28` | Current function walk complete; no new file-level gap isolated | [client audit](client-full-parity-audit-and-implementation-plan-2026-04-09.md) + current 2026-04-22 source walk | - |
| `src/code/client/ql_auth.c` | `16` | RW-G01 file-level note open | [repo-wide audit](repo-wide-parity-audit-2026-04-21.md) + [gap note](source-file-gap-notes/rw-g01-client-auth.md) | [note](source-file-gap-notes/rw-g01-client-auth.md) |
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
| `src/code/game/bg_misc.c` | `37` | Current function walk complete; no file-level parity gap isolated | [module audit](game-module-parity-audit-and-implementation-plan-2026-04-10.md) + current 2026-04-22 source walk | - |
| `src/code/game/bg_pmove.c` | `64` | Current function walk complete; no file-level parity gap isolated | [module audit](game-module-parity-audit-and-implementation-plan-2026-04-10.md) + current 2026-04-22 source walk | - |
| `src/code/game/bg_slidemove.c` | `9` | Current function walk complete; no file-level parity gap isolated | [module audit](game-module-parity-audit-and-implementation-plan-2026-04-10.md) + current 2026-04-22 source walk | - |
| `src/code/game/g_active.c` | `65` | Current function walk complete; no file-level parity gap isolated | [module audit](game-module-parity-audit-and-implementation-plan-2026-04-10.md) + current 2026-04-22 source walk | - |
| `src/code/game/g_arenas.c` | `8` | Current function walk complete; no file-level parity gap isolated | [module audit](game-module-parity-audit-and-implementation-plan-2026-04-10.md) + current 2026-04-22 source walk | - |
| `src/code/game/g_autoshuffle.c` | `7` | Current function walk complete; no file-level parity gap isolated | [module audit](game-module-parity-audit-and-implementation-plan-2026-04-10.md) + current 2026-04-22 source walk | - |
| `src/code/game/g_bot.c` | `27` | Current function walk complete; no file-level parity gap isolated | [module audit](game-module-parity-audit-and-implementation-plan-2026-04-10.md) + current 2026-04-22 source walk | - |
| `src/code/game/g_client.c` | `77` | Current function walk complete; no file-level parity gap isolated | [module audit](game-module-parity-audit-and-implementation-plan-2026-04-10.md) + current 2026-04-22 source walk | - |
| `src/code/game/g_cmds.c` | `159` | Current function walk complete; no file-level parity gap isolated | [module audit](game-module-parity-audit-and-implementation-plan-2026-04-10.md) + current 2026-04-22 source walk | - |
| `src/code/game/g_combat.c` | `41` | Current function walk complete; no file-level parity gap isolated | [module audit](game-module-parity-audit-and-implementation-plan-2026-04-10.md) + current 2026-04-22 source walk | - |
| `src/code/game/g_entity.c` | `0` | Current function walk complete; no file-level parity gap isolated | [module audit](game-module-parity-audit-and-implementation-plan-2026-04-10.md) + current 2026-04-22 source walk | - |
| `src/code/game/g_factory.c` | `26` | Current function walk complete; no file-level parity gap isolated | [module audit](game-module-parity-audit-and-implementation-plan-2026-04-10.md) + current 2026-04-22 source walk | - |
| `src/code/game/g_freeze.c` | `7` | Current function walk complete; no file-level parity gap isolated | [module audit](game-module-parity-audit-and-implementation-plan-2026-04-10.md) + current 2026-04-22 source walk | - |
| `src/code/game/g_items.c` | `74` | Current function walk complete; no file-level parity gap isolated | [module audit](game-module-parity-audit-and-implementation-plan-2026-04-10.md) + current 2026-04-22 source walk | - |
| `src/code/game/g_main.c` | `196` | Current function walk complete; no file-level parity gap isolated | [module audit](game-module-parity-audit-and-implementation-plan-2026-04-10.md) + current 2026-04-22 source walk | - |
| `src/code/game/g_match_state.c` | `9` | Current function walk complete; no file-level parity gap isolated | [module audit](game-module-parity-audit-and-implementation-plan-2026-04-10.md) + current 2026-04-22 source walk | - |
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
| `src/code/qcommon/common.c` | `103` | Current function walk complete; no file-level parity gap isolated | [qcommon audit](qcommon-full-parity-audit-and-implementation-plan-2026-04-10.md) + current 2026-04-22 source walk | - |
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

Current 2026-04-22 audit result: the `src/code/renderer` function walk
did not isolate any new file-level owners inside the closed strict-retail
`renderer` register. The retained export, image, post-process,
scene/runtime, font, and host-text closures still hold on current
evidence, while the bounded `R_fonsErrorCallback` issue remains part of
`RW-G04` evidence freshness rather than a new renderer source-gap owner.

| File | Functions | Current parity state | Primary evidence | Gap note |
| --- | ---: | --- | --- | --- |
| `src/code/renderer/tr_animation.c` | `2` | Current function walk complete; no file-level parity gap isolated | [renderer audit](renderer-full-parity-audit-and-implementation-plan-2026-04-09.md) + current 2026-04-22 source walk | - |
| `src/code/renderer/tr_backend.c` | `74` | Current function walk complete; no file-level parity gap isolated | [renderer audit](renderer-full-parity-audit-and-implementation-plan-2026-04-09.md) + current 2026-04-22 source walk | - |
| `src/code/renderer/tr_bsp.c` | `31` | Current function walk complete; no file-level parity gap isolated | [renderer audit](renderer-full-parity-audit-and-implementation-plan-2026-04-09.md) + current 2026-04-22 source walk | - |
| `src/code/renderer/tr_cmds.c` | `12` | Current function walk complete; no file-level parity gap isolated | [renderer audit](renderer-full-parity-audit-and-implementation-plan-2026-04-09.md) + current 2026-04-22 source walk | - |
| `src/code/renderer/tr_curve.c` | `12` | Current function walk complete; no file-level parity gap isolated | [renderer audit](renderer-full-parity-audit-and-implementation-plan-2026-04-09.md) + current 2026-04-22 source walk | - |
| `src/code/renderer/tr_flares.c` | `6` | Current function walk complete; no file-level parity gap isolated | [renderer audit](renderer-full-parity-audit-and-implementation-plan-2026-04-09.md) + current 2026-04-22 source walk | - |
| `src/code/renderer/tr_font.c` | `65` | Current function walk complete; no file-level parity gap isolated | [renderer audit](renderer-full-parity-audit-and-implementation-plan-2026-04-09.md) + current 2026-04-22 source walk | - |
| `src/code/renderer/tr_image.c` | `56` | Current function walk complete; no file-level parity gap isolated | [renderer audit](renderer-full-parity-audit-and-implementation-plan-2026-04-09.md) + current 2026-04-22 source walk | - |
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
| `src/code/server/sv_ccmds.c` | `73` | Current function walk complete; no new file-level gap isolated | [server audit](server-full-parity-audit-and-implementation-plan-2026-04-10.md) + current 2026-04-22 source walk | - |
| `src/code/server/sv_client.c` | `62` | Current function walk complete; no new file-level gap isolated | [server audit](server-full-parity-audit-and-implementation-plan-2026-04-10.md) + current 2026-04-22 source walk | - |
| `src/code/server/sv_game.c` | `47` | Current function walk complete; no new file-level gap isolated | [server audit](server-full-parity-audit-and-implementation-plan-2026-04-10.md) + current 2026-04-22 source walk | - |
| `src/code/server/sv_init.c` | `17` | Current function walk complete; no new file-level gap isolated | [server audit](server-full-parity-audit-and-implementation-plan-2026-04-10.md) + current 2026-04-22 source walk | - |
| `src/code/server/sv_main.c` | `39` | Current function walk complete; no new file-level gap isolated | [server audit](server-full-parity-audit-and-implementation-plan-2026-04-10.md) + current 2026-04-22 source walk | - |
| `src/code/server/sv_net_chan.c` | `5` | Current function walk complete; no new file-level gap isolated | [server audit](server-full-parity-audit-and-implementation-plan-2026-04-10.md) + current 2026-04-22 source walk | - |
| `src/code/server/sv_rankings.c` | `39` | RW-G01 file-level note open | [repo-wide audit](repo-wide-parity-audit-2026-04-21.md) + [gap note](source-file-gap-notes/rw-g01-server-rankings.md) | [note](source-file-gap-notes/rw-g01-server-rankings.md) |
| `src/code/server/sv_snapshot.c` | `11` | Current function walk complete; no new file-level gap isolated | [server audit](server-full-parity-audit-and-implementation-plan-2026-04-10.md) + current 2026-04-22 source walk | - |
| `src/code/server/sv_world.c` | `12` | Current function walk complete; no new file-level gap isolated | [server audit](server-full-parity-audit-and-implementation-plan-2026-04-10.md) + current 2026-04-22 source walk | - |
| `src/code/server/sv_zmq.c` | `45` | Current function walk complete; no new file-level gap isolated | [server audit](server-full-parity-audit-and-implementation-plan-2026-04-10.md) + current 2026-04-22 source walk | - |
### `src/code/ui` (9 files)

| File | Functions | Current parity state | Primary evidence | Gap note |
| --- | ---: | --- | --- | --- |
| `src/code/ui/ui_atoms.c` | `40` | Subsystem closure stands; read-only file walk pending | [ui audit](ui-full-parity-audit-and-implementation-plan-2026-04-05.md) | - |
| `src/code/ui/ui_cdkey.c` | `8` | Subsystem closure stands; read-only file walk pending | [ui audit](ui-full-parity-audit-and-implementation-plan-2026-04-05.md) | - |
| `src/code/ui/ui_gameinfo.c` | `18` | Subsystem closure stands; read-only file walk pending | [ui audit](ui-full-parity-audit-and-implementation-plan-2026-04-05.md) | - |
| `src/code/ui/ui_main.c` | `260` | Subsystem closure stands; read-only file walk pending | [ui audit](ui-full-parity-audit-and-implementation-plan-2026-04-05.md) | - |
| `src/code/ui/ui_players.c` | `28` | Subsystem closure stands; read-only file walk pending | [ui audit](ui-full-parity-audit-and-implementation-plan-2026-04-05.md) | - |
| `src/code/ui/ui_quakelive_bridge.c` | `9` | Subsystem closure stands; read-only file walk pending | [ui audit](ui-full-parity-audit-and-implementation-plan-2026-04-05.md) | - |
| `src/code/ui/ui_shared.c` | `321` | Subsystem closure stands; read-only file walk pending | [ui audit](ui-full-parity-audit-and-implementation-plan-2026-04-05.md) | - |
| `src/code/ui/ui_syscalls.c` | `105` | Subsystem closure stands; read-only file walk pending | [ui audit](ui-full-parity-audit-and-implementation-plan-2026-04-05.md) | - |
| `src/code/ui/ui_util.c` | `0` | Subsystem closure stands; read-only file walk pending | [ui audit](ui-full-parity-audit-and-implementation-plan-2026-04-05.md) | - |
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

| File | Functions | Current parity state | Primary evidence | Gap note |
| --- | ---: | --- | --- | --- |
| `src/code/unix/linux_common.c` | `6` | RW-G02 tree still open; file-specific gap not yet isolated | [repo-wide audit](repo-wide-parity-audit-2026-04-21.md) | - |
| `src/code/unix/linux_glimp.c` | `40` | RW-G02 file-level note open | [repo-wide audit](repo-wide-parity-audit-2026-04-21.md) + [gap note](source-file-gap-notes/rw-g02-linux-glimp.md) | [note](source-file-gap-notes/rw-g02-linux-glimp.md) |
| `src/code/unix/linux_joystick.c` | `2` | RW-G02 file-level note open | [repo-wide audit](repo-wide-parity-audit-2026-04-21.md) + [gap note](source-file-gap-notes/rw-g02-linux-joystick.md) | [note](source-file-gap-notes/rw-g02-linux-joystick.md) |
| `src/code/unix/linux_qgl.c` | `341` | RW-G02 tree still open; file-specific gap not yet isolated | [repo-wide audit](repo-wide-parity-audit-2026-04-21.md) | - |
| `src/code/unix/linux_signals.c` | `2` | RW-G02 tree still open; file-specific gap not yet isolated | [repo-wide audit](repo-wide-parity-audit-2026-04-21.md) | - |
| `src/code/unix/linux_snd.c` | `6` | RW-G02 file-level note open | [repo-wide audit](repo-wide-parity-audit-2026-04-21.md) + [gap note](source-file-gap-notes/rw-g02-linux-snd.md) | [note](source-file-gap-notes/rw-g02-linux-snd.md) |
| `src/code/unix/unix_main.c` | `59` | RW-G02 file-level note open | [repo-wide audit](repo-wide-parity-audit-2026-04-21.md) + [gap note](source-file-gap-notes/rw-g02-unix-main.md) | [note](source-file-gap-notes/rw-g02-unix-main.md) |
| `src/code/unix/unix_net.c` | `17` | RW-G02 tree still open; file-specific gap not yet isolated | [repo-wide audit](repo-wide-parity-audit-2026-04-21.md) | - |
| `src/code/unix/unix_shared.c` | `21` | RW-G02 tree still open; file-specific gap not yet isolated | [repo-wide audit](repo-wide-parity-audit-2026-04-21.md) | - |
| `src/code/unix/vm_x86.c` | `2` | RW-G02 tree still open; file-specific gap not yet isolated | [repo-wide audit](repo-wide-parity-audit-2026-04-21.md) | - |
### `src/code/null` (7 files)

| File | Functions | Current parity state | Primary evidence | Gap note |
| --- | ---: | --- | --- | --- |
| `src/code/null/mac_net.c` | `5` | RW-G02 tree still open; file-specific gap not yet isolated | [repo-wide audit](repo-wide-parity-audit-2026-04-21.md) | - |
| `src/code/null/null_client.c` | `50` | RW-G02 file-level note open | [repo-wide audit](repo-wide-parity-audit-2026-04-21.md) + [gap note](source-file-gap-notes/rw-g02-null-client.md) | [note](source-file-gap-notes/rw-g02-null-client.md) |
| `src/code/null/null_glimp.c` | `7` | RW-G02 tree still open; file-specific gap not yet isolated | [repo-wide audit](repo-wide-parity-audit-2026-04-21.md) | - |
| `src/code/null/null_input.c` | `6` | RW-G02 file-level note open | [repo-wide audit](repo-wide-parity-audit-2026-04-21.md) + [gap note](source-file-gap-notes/rw-g02-null-input.md) | [note](source-file-gap-notes/rw-g02-null-input.md) |
| `src/code/null/null_main.c` | `28` | RW-G02 file-level note open | [repo-wide audit](repo-wide-parity-audit-2026-04-21.md) + [gap note](source-file-gap-notes/rw-g02-null-main.md) | [note](source-file-gap-notes/rw-g02-null-main.md) |
| `src/code/null/null_net.c` | `5` | RW-G02 tree still open; file-specific gap not yet isolated | [repo-wide audit](repo-wide-parity-audit-2026-04-21.md) | - |
| `src/code/null/null_snddma.c` | `10` | RW-G02 file-level note open | [repo-wide audit](repo-wide-parity-audit-2026-04-21.md) + [gap note](source-file-gap-notes/rw-g02-null-snddma.md) | [note](source-file-gap-notes/rw-g02-null-snddma.md) |

## Secondary Tool, Editor, Compiler, And Legacy Source Surface

### `src/code/bspc` (47 files)

| File | Functions | Current parity state | Primary evidence | Gap note |
| --- | ---: | --- | --- | --- |
| `src/code/bspc/_files.c` | `0` | Secondary source tree; queued after primary runtime surface | [source-file plan](source-file-parity-audit-plan-2026-04-22.md) | - |
| `src/code/bspc/aas_areamerging.c` | `6` | Secondary source tree; queued after primary runtime surface | [source-file plan](source-file-parity-audit-plan-2026-04-22.md) | - |
| `src/code/bspc/aas_cfg.c` | `4` | Secondary source tree; queued after primary runtime surface | [source-file plan](source-file-parity-audit-plan-2026-04-22.md) | - |
| `src/code/bspc/aas_create.c` | `30` | Secondary source tree; queued after primary runtime surface | [source-file plan](source-file-parity-audit-plan-2026-04-22.md) | - |
| `src/code/bspc/aas_edgemelting.c` | `3` | Secondary source tree; queued after primary runtime surface | [source-file plan](source-file-parity-audit-plan-2026-04-22.md) | - |
| `src/code/bspc/aas_facemerging.c` | `6` | Secondary source tree; queued after primary runtime surface | [source-file plan](source-file-parity-audit-plan-2026-04-22.md) | - |
| `src/code/bspc/aas_file.c` | `9` | Secondary source tree; queued after primary runtime surface | [source-file plan](source-file-parity-audit-plan-2026-04-22.md) | - |
| `src/code/bspc/aas_gsubdiv.c` | `12` | Secondary source tree; queued after primary runtime surface | [source-file plan](source-file-parity-audit-plan-2026-04-22.md) | - |
| `src/code/bspc/aas_map.c` | `16` | Secondary source tree; queued after primary runtime surface | [source-file plan](source-file-parity-audit-plan-2026-04-22.md) | - |
| `src/code/bspc/aas_prunenodes.c` | `2` | Secondary source tree; queued after primary runtime surface | [source-file plan](source-file-parity-audit-plan-2026-04-22.md) | - |
| `src/code/bspc/aas_store.c` | `23` | Secondary source tree; queued after primary runtime surface | [source-file plan](source-file-parity-audit-plan-2026-04-22.md) | - |
| `src/code/bspc/be_aas_bspc.c` | `16` | Secondary source tree; queued after primary runtime surface | [source-file plan](source-file-parity-audit-plan-2026-04-22.md) | - |
| `src/code/bspc/brushbsp.c` | `41` | Secondary source tree; queued after primary runtime surface | [source-file plan](source-file-parity-audit-plan-2026-04-22.md) | - |
| `src/code/bspc/bspc.c` | `9` | Secondary source tree; queued after primary runtime surface | [source-file plan](source-file-parity-audit-plan-2026-04-22.md) | - |
| `src/code/bspc/cfgq3.c` | `0` | Secondary source tree; queued after primary runtime surface | [source-file plan](source-file-parity-audit-plan-2026-04-22.md) | - |
| `src/code/bspc/csg.c` | `19` | Secondary source tree; queued after primary runtime surface | [source-file plan](source-file-parity-audit-plan-2026-04-22.md) | - |
| `src/code/bspc/faces.c` | `23` | Secondary source tree; queued after primary runtime surface | [source-file plan](source-file-parity-audit-plan-2026-04-22.md) | - |
| `src/code/bspc/gldraw.c` | `10` | Secondary source tree; queued after primary runtime surface | [source-file plan](source-file-parity-audit-plan-2026-04-22.md) | - |
| `src/code/bspc/glfile.c` | `5` | Secondary source tree; queued after primary runtime surface | [source-file plan](source-file-parity-audit-plan-2026-04-22.md) | - |
| `src/code/bspc/l_bsp_ent.c` | `8` | Secondary source tree; queued after primary runtime surface | [source-file plan](source-file-parity-audit-plan-2026-04-22.md) | - |
| `src/code/bspc/l_bsp_hl.c` | `19` | Secondary source tree; queued after primary runtime surface | [source-file plan](source-file-parity-audit-plan-2026-04-22.md) | - |
| `src/code/bspc/l_bsp_q1.c` | `10` | Secondary source tree; queued after primary runtime surface | [source-file plan](source-file-parity-audit-plan-2026-04-22.md) | - |
| `src/code/bspc/l_bsp_q2.c` | `19` | Secondary source tree; queued after primary runtime surface | [source-file plan](source-file-parity-audit-plan-2026-04-22.md) | - |
| `src/code/bspc/l_bsp_q3.c` | `18` | Secondary source tree; queued after primary runtime surface | [source-file plan](source-file-parity-audit-plan-2026-04-22.md) | - |
| `src/code/bspc/l_bsp_sin.c` | `20` | Secondary source tree; queued after primary runtime surface | [source-file plan](source-file-parity-audit-plan-2026-04-22.md) | - |
| `src/code/bspc/l_cmd.c` | `73` | Secondary source tree; queued after primary runtime surface | [source-file plan](source-file-parity-audit-plan-2026-04-22.md) | - |
| `src/code/bspc/l_log.c` | `9` | Secondary source tree; queued after primary runtime surface | [source-file plan](source-file-parity-audit-plan-2026-04-22.md) | - |
| `src/code/bspc/l_math.c` | `21` | Secondary source tree; queued after primary runtime surface | [source-file plan](source-file-parity-audit-plan-2026-04-22.md) | - |
| `src/code/bspc/l_mem.c` | `22` | Secondary source tree; queued after primary runtime surface | [source-file plan](source-file-parity-audit-plan-2026-04-22.md) | - |
| `src/code/bspc/l_poly.c` | `31` | Secondary source tree; queued after primary runtime surface | [source-file plan](source-file-parity-audit-plan-2026-04-22.md) | - |
| `src/code/bspc/l_qfiles.c` | `11` | Secondary source tree; queued after primary runtime surface | [source-file plan](source-file-parity-audit-plan-2026-04-22.md) | - |
| `src/code/bspc/l_threads.c` | `65` | Secondary source tree; queued after primary runtime surface | [source-file plan](source-file-parity-audit-plan-2026-04-22.md) | - |
| `src/code/bspc/l_utils.c` | `7` | Secondary source tree; queued after primary runtime surface | [source-file plan](source-file-parity-audit-plan-2026-04-22.md) | - |
| `src/code/bspc/leakfile.c` | `1` | Secondary source tree; queued after primary runtime surface | [source-file plan](source-file-parity-audit-plan-2026-04-22.md) | - |
| `src/code/bspc/map.c` | `22` | Secondary source tree; queued after primary runtime surface | [source-file plan](source-file-parity-audit-plan-2026-04-22.md) | - |
| `src/code/bspc/map_hl.c` | `14` | Secondary source tree; queued after primary runtime surface | [source-file plan](source-file-parity-audit-plan-2026-04-22.md) | - |
| `src/code/bspc/map_q1.c` | `17` | Secondary source tree; queued after primary runtime surface | [source-file plan](source-file-parity-audit-plan-2026-04-22.md) | - |
| `src/code/bspc/map_q2.c` | `20` | Secondary source tree; queued after primary runtime surface | [source-file plan](source-file-parity-audit-plan-2026-04-22.md) | - |
| `src/code/bspc/map_q3.c` | `8` | Secondary source tree; queued after primary runtime surface | [source-file plan](source-file-parity-audit-plan-2026-04-22.md) | - |
| `src/code/bspc/map_sin.c` | `16` | Secondary source tree; queued after primary runtime surface | [source-file plan](source-file-parity-audit-plan-2026-04-22.md) | - |
| `src/code/bspc/nodraw.c` | `4` | Secondary source tree; queued after primary runtime surface | [source-file plan](source-file-parity-audit-plan-2026-04-22.md) | - |
| `src/code/bspc/portals.c` | `33` | Secondary source tree; queued after primary runtime surface | [source-file plan](source-file-parity-audit-plan-2026-04-22.md) | - |
| `src/code/bspc/prtfile.c` | `9` | Secondary source tree; queued after primary runtime surface | [source-file plan](source-file-parity-audit-plan-2026-04-22.md) | - |
| `src/code/bspc/tetrahedron.c` | `45` | Secondary source tree; queued after primary runtime surface | [source-file plan](source-file-parity-audit-plan-2026-04-22.md) | - |
| `src/code/bspc/textures.c` | `3` | Secondary source tree; queued after primary runtime surface | [source-file plan](source-file-parity-audit-plan-2026-04-22.md) | - |
| `src/code/bspc/tree.c` | `8` | Secondary source tree; queued after primary runtime surface | [source-file plan](source-file-parity-audit-plan-2026-04-22.md) | - |
| `src/code/bspc/writebsp.c` | `13` | Secondary source tree; queued after primary runtime surface | [source-file plan](source-file-parity-audit-plan-2026-04-22.md) | - |
### `src/code/jpeg-6` (51 files)

| File | Functions | Current parity state | Primary evidence | Gap note |
| --- | ---: | --- | --- | --- |
| `src/code/jpeg-6/jcapimin.c` | `0` | Secondary source tree; queued after primary runtime surface | [source-file plan](source-file-parity-audit-plan-2026-04-22.md) | - |
| `src/code/jpeg-6/jcapistd.c` | `0` | Secondary source tree; queued after primary runtime surface | [source-file plan](source-file-parity-audit-plan-2026-04-22.md) | - |
| `src/code/jpeg-6/jccoefct.c` | `0` | Secondary source tree; queued after primary runtime surface | [source-file plan](source-file-parity-audit-plan-2026-04-22.md) | - |
| `src/code/jpeg-6/jccolor.c` | `0` | Secondary source tree; queued after primary runtime surface | [source-file plan](source-file-parity-audit-plan-2026-04-22.md) | - |
| `src/code/jpeg-6/jcdctmgr.c` | `0` | Secondary source tree; queued after primary runtime surface | [source-file plan](source-file-parity-audit-plan-2026-04-22.md) | - |
| `src/code/jpeg-6/jchuff.c` | `0` | Secondary source tree; queued after primary runtime surface | [source-file plan](source-file-parity-audit-plan-2026-04-22.md) | - |
| `src/code/jpeg-6/jcinit.c` | `0` | Secondary source tree; queued after primary runtime surface | [source-file plan](source-file-parity-audit-plan-2026-04-22.md) | - |
| `src/code/jpeg-6/jcmainct.c` | `0` | Secondary source tree; queued after primary runtime surface | [source-file plan](source-file-parity-audit-plan-2026-04-22.md) | - |
| `src/code/jpeg-6/jcmarker.c` | `0` | Secondary source tree; queued after primary runtime surface | [source-file plan](source-file-parity-audit-plan-2026-04-22.md) | - |
| `src/code/jpeg-6/jcmaster.c` | `0` | Secondary source tree; queued after primary runtime surface | [source-file plan](source-file-parity-audit-plan-2026-04-22.md) | - |
| `src/code/jpeg-6/jcomapi.c` | `0` | Secondary source tree; queued after primary runtime surface | [source-file plan](source-file-parity-audit-plan-2026-04-22.md) | - |
| `src/code/jpeg-6/jcparam.c` | `0` | Secondary source tree; queued after primary runtime surface | [source-file plan](source-file-parity-audit-plan-2026-04-22.md) | - |
| `src/code/jpeg-6/jcphuff.c` | `0` | Secondary source tree; queued after primary runtime surface | [source-file plan](source-file-parity-audit-plan-2026-04-22.md) | - |
| `src/code/jpeg-6/jcprepct.c` | `0` | Secondary source tree; queued after primary runtime surface | [source-file plan](source-file-parity-audit-plan-2026-04-22.md) | - |
| `src/code/jpeg-6/jcsample.c` | `0` | Secondary source tree; queued after primary runtime surface | [source-file plan](source-file-parity-audit-plan-2026-04-22.md) | - |
| `src/code/jpeg-6/jctrans.c` | `0` | Secondary source tree; queued after primary runtime surface | [source-file plan](source-file-parity-audit-plan-2026-04-22.md) | - |
| `src/code/jpeg-6/jdapimin.c` | `0` | Secondary source tree; queued after primary runtime surface | [source-file plan](source-file-parity-audit-plan-2026-04-22.md) | - |
| `src/code/jpeg-6/jdapistd.c` | `0` | Secondary source tree; queued after primary runtime surface | [source-file plan](source-file-parity-audit-plan-2026-04-22.md) | - |
| `src/code/jpeg-6/jdatadst.c` | `0` | Secondary source tree; queued after primary runtime surface | [source-file plan](source-file-parity-audit-plan-2026-04-22.md) | - |
| `src/code/jpeg-6/jdatasrc.c` | `0` | Secondary source tree; queued after primary runtime surface | [source-file plan](source-file-parity-audit-plan-2026-04-22.md) | - |
| `src/code/jpeg-6/jdcoefct.c` | `0` | Secondary source tree; queued after primary runtime surface | [source-file plan](source-file-parity-audit-plan-2026-04-22.md) | - |
| `src/code/jpeg-6/jdcolor.c` | `0` | Secondary source tree; queued after primary runtime surface | [source-file plan](source-file-parity-audit-plan-2026-04-22.md) | - |
| `src/code/jpeg-6/jddctmgr.c` | `0` | Secondary source tree; queued after primary runtime surface | [source-file plan](source-file-parity-audit-plan-2026-04-22.md) | - |
| `src/code/jpeg-6/jdhuff.c` | `0` | Secondary source tree; queued after primary runtime surface | [source-file plan](source-file-parity-audit-plan-2026-04-22.md) | - |
| `src/code/jpeg-6/jdinput.c` | `0` | Secondary source tree; queued after primary runtime surface | [source-file plan](source-file-parity-audit-plan-2026-04-22.md) | - |
| `src/code/jpeg-6/jdmainct.c` | `0` | Secondary source tree; queued after primary runtime surface | [source-file plan](source-file-parity-audit-plan-2026-04-22.md) | - |
| `src/code/jpeg-6/jdmarker.c` | `0` | Secondary source tree; queued after primary runtime surface | [source-file plan](source-file-parity-audit-plan-2026-04-22.md) | - |
| `src/code/jpeg-6/jdmaster.c` | `0` | Secondary source tree; queued after primary runtime surface | [source-file plan](source-file-parity-audit-plan-2026-04-22.md) | - |
| `src/code/jpeg-6/jdmerge.c` | `0` | Secondary source tree; queued after primary runtime surface | [source-file plan](source-file-parity-audit-plan-2026-04-22.md) | - |
| `src/code/jpeg-6/jdphuff.c` | `0` | Secondary source tree; queued after primary runtime surface | [source-file plan](source-file-parity-audit-plan-2026-04-22.md) | - |
| `src/code/jpeg-6/jdpostct.c` | `0` | Secondary source tree; queued after primary runtime surface | [source-file plan](source-file-parity-audit-plan-2026-04-22.md) | - |
| `src/code/jpeg-6/jdsample.c` | `0` | Secondary source tree; queued after primary runtime surface | [source-file plan](source-file-parity-audit-plan-2026-04-22.md) | - |
| `src/code/jpeg-6/jdtrans.c` | `0` | Secondary source tree; queued after primary runtime surface | [source-file plan](source-file-parity-audit-plan-2026-04-22.md) | - |
| `src/code/jpeg-6/jerror.c` | `0` | Secondary source tree; queued after primary runtime surface | [source-file plan](source-file-parity-audit-plan-2026-04-22.md) | - |
| `src/code/jpeg-6/jfdctflt.c` | `0` | Secondary source tree; queued after primary runtime surface | [source-file plan](source-file-parity-audit-plan-2026-04-22.md) | - |
| `src/code/jpeg-6/jfdctfst.c` | `0` | Secondary source tree; queued after primary runtime surface | [source-file plan](source-file-parity-audit-plan-2026-04-22.md) | - |
| `src/code/jpeg-6/jfdctint.c` | `0` | Secondary source tree; queued after primary runtime surface | [source-file plan](source-file-parity-audit-plan-2026-04-22.md) | - |
| `src/code/jpeg-6/jidctflt.c` | `0` | Secondary source tree; queued after primary runtime surface | [source-file plan](source-file-parity-audit-plan-2026-04-22.md) | - |
| `src/code/jpeg-6/jidctfst.c` | `0` | Secondary source tree; queued after primary runtime surface | [source-file plan](source-file-parity-audit-plan-2026-04-22.md) | - |
| `src/code/jpeg-6/jidctint.c` | `0` | Secondary source tree; queued after primary runtime surface | [source-file plan](source-file-parity-audit-plan-2026-04-22.md) | - |
| `src/code/jpeg-6/jidctred.c` | `0` | Secondary source tree; queued after primary runtime surface | [source-file plan](source-file-parity-audit-plan-2026-04-22.md) | - |
| `src/code/jpeg-6/jload.c` | `1` | Secondary source tree; queued after primary runtime surface | [source-file plan](source-file-parity-audit-plan-2026-04-22.md) | - |
| `src/code/jpeg-6/jmemansi.c` | `0` | Secondary source tree; queued after primary runtime surface | [source-file plan](source-file-parity-audit-plan-2026-04-22.md) | - |
| `src/code/jpeg-6/jmemdos.c` | `0` | Secondary source tree; queued after primary runtime surface | [source-file plan](source-file-parity-audit-plan-2026-04-22.md) | - |
| `src/code/jpeg-6/jmemmgr.c` | `0` | Secondary source tree; queued after primary runtime surface | [source-file plan](source-file-parity-audit-plan-2026-04-22.md) | - |
| `src/code/jpeg-6/jmemname.c` | `0` | Secondary source tree; queued after primary runtime surface | [source-file plan](source-file-parity-audit-plan-2026-04-22.md) | - |
| `src/code/jpeg-6/jmemnobs.c` | `0` | Secondary source tree; queued after primary runtime surface | [source-file plan](source-file-parity-audit-plan-2026-04-22.md) | - |
| `src/code/jpeg-6/jpegtran.c` | `0` | Secondary source tree; queued after primary runtime surface | [source-file plan](source-file-parity-audit-plan-2026-04-22.md) | - |
| `src/code/jpeg-6/jquant1.c` | `0` | Secondary source tree; queued after primary runtime surface | [source-file plan](source-file-parity-audit-plan-2026-04-22.md) | - |
| `src/code/jpeg-6/jquant2.c` | `0` | Secondary source tree; queued after primary runtime surface | [source-file plan](source-file-parity-audit-plan-2026-04-22.md) | - |
| `src/code/jpeg-6/jutils.c` | `0` | Secondary source tree; queued after primary runtime surface | [source-file plan](source-file-parity-audit-plan-2026-04-22.md) | - |
### `src/code/splines` (8 files)

| File | Functions | Current parity state | Primary evidence | Gap note |
| --- | ---: | --- | --- | --- |
| `src/code/splines/math_angles.cpp` | `3` | Secondary source tree; queued after primary runtime surface | [source-file plan](source-file-parity-audit-plan-2026-04-22.md) | - |
| `src/code/splines/math_matrix.cpp` | `3` | Secondary source tree; queued after primary runtime surface | [source-file plan](source-file-parity-audit-plan-2026-04-22.md) | - |
| `src/code/splines/math_quaternion.cpp` | `3` | Secondary source tree; queued after primary runtime surface | [source-file plan](source-file-parity-audit-plan-2026-04-22.md) | - |
| `src/code/splines/math_vector.cpp` | `1` | Secondary source tree; queued after primary runtime surface | [source-file plan](source-file-parity-audit-plan-2026-04-22.md) | - |
| `src/code/splines/q_parse.cpp` | `19` | Secondary source tree; queued after primary runtime surface | [source-file plan](source-file-parity-audit-plan-2026-04-22.md) | - |
| `src/code/splines/q_shared.cpp` | `47` | Secondary source tree; queued after primary runtime surface | [source-file plan](source-file-parity-audit-plan-2026-04-22.md) | - |
| `src/code/splines/splines.cpp` | `9` | Secondary source tree; queued after primary runtime surface | [source-file plan](source-file-parity-audit-plan-2026-04-22.md) | - |
| `src/code/splines/util_str.cpp` | `0` | Secondary source tree; queued after primary runtime surface | [source-file plan](source-file-parity-audit-plan-2026-04-22.md) | - |
### `src/game` (10 files)

| File | Functions | Current parity state | Primary evidence | Gap note |
| --- | ---: | --- | --- | --- |
| `src/game/g_config.c` | `30` | Secondary source tree; queued after primary runtime surface | [source-file plan](source-file-parity-audit-plan-2026-04-22.md) | - |
| `src/game/g_match_config.c` | `12` | Secondary source tree; queued after primary runtime surface | [source-file plan](source-file-parity-audit-plan-2026-04-22.md) | - |
| `src/game/tests/cosmetics_fixtures.c` | `13` | Secondary source tree; queued after primary runtime surface | [source-file plan](source-file-parity-audit-plan-2026-04-22.md) | - |
| `src/game/tests/fixture_runner.c` | `8` | Secondary source tree; queued after primary runtime surface | [source-file plan](source-file-parity-audit-plan-2026-04-22.md) | - |
| `src/game/tests/item_fixtures.c` | `7` | Secondary source tree; queued after primary runtime surface | [source-file plan](source-file-parity-audit-plan-2026-04-22.md) | - |
| `src/game/tests/rules_entry.c` | `1` | Secondary source tree; queued after primary runtime surface | [source-file plan](source-file-parity-audit-plan-2026-04-22.md) | - |
| `src/game/tests/sample_fixtures.c` | `2` | Secondary source tree; queued after primary runtime surface | [source-file plan](source-file-parity-audit-plan-2026-04-22.md) | - |
| `src/game/tests/syscall_mocks.c` | `4` | Secondary source tree; queued after primary runtime surface | [source-file plan](source-file-parity-audit-plan-2026-04-22.md) | - |
| `src/game/tests/vote_control_fixtures.c` | `12` | Secondary source tree; queued after primary runtime surface | [source-file plan](source-file-parity-audit-plan-2026-04-22.md) | - |
| `src/game/tests/weapon_cvar_fixtures.c` | `9` | Secondary source tree; queued after primary runtime surface | [source-file plan](source-file-parity-audit-plan-2026-04-22.md) | - |
### `src/lcc` (74 files)

| File | Functions | Current parity state | Primary evidence | Gap note |
| --- | ---: | --- | --- | --- |
| `src/lcc/cpp/cpp.c` | `0` | Secondary source tree; queued after primary runtime surface | [source-file plan](source-file-parity-audit-plan-2026-04-22.md) | - |
| `src/lcc/cpp/eval.c` | `0` | Secondary source tree; queued after primary runtime surface | [source-file plan](source-file-parity-audit-plan-2026-04-22.md) | - |
| `src/lcc/cpp/getopt.c` | `0` | Secondary source tree; queued after primary runtime surface | [source-file plan](source-file-parity-audit-plan-2026-04-22.md) | - |
| `src/lcc/cpp/hideset.c` | `0` | Secondary source tree; queued after primary runtime surface | [source-file plan](source-file-parity-audit-plan-2026-04-22.md) | - |
| `src/lcc/cpp/include.c` | `0` | Secondary source tree; queued after primary runtime surface | [source-file plan](source-file-parity-audit-plan-2026-04-22.md) | - |
| `src/lcc/cpp/lex.c` | `0` | Secondary source tree; queued after primary runtime surface | [source-file plan](source-file-parity-audit-plan-2026-04-22.md) | - |
| `src/lcc/cpp/macro.c` | `0` | Secondary source tree; queued after primary runtime surface | [source-file plan](source-file-parity-audit-plan-2026-04-22.md) | - |
| `src/lcc/cpp/nlist.c` | `0` | Secondary source tree; queued after primary runtime surface | [source-file plan](source-file-parity-audit-plan-2026-04-22.md) | - |
| `src/lcc/cpp/tokens.c` | `0` | Secondary source tree; queued after primary runtime surface | [source-file plan](source-file-parity-audit-plan-2026-04-22.md) | - |
| `src/lcc/cpp/unix.c` | `1` | Secondary source tree; queued after primary runtime surface | [source-file plan](source-file-parity-audit-plan-2026-04-22.md) | - |
| `src/lcc/etc/bprint.c` | `18` | Secondary source tree; queued after primary runtime surface | [source-file plan](source-file-parity-audit-plan-2026-04-22.md) | - |
| `src/lcc/etc/gcc-solaris.c` | `1` | Secondary source tree; queued after primary runtime surface | [source-file plan](source-file-parity-audit-plan-2026-04-22.md) | - |
| `src/lcc/etc/irix.c` | `1` | Secondary source tree; queued after primary runtime surface | [source-file plan](source-file-parity-audit-plan-2026-04-22.md) | - |
| `src/lcc/etc/lcc.c` | `24` | Secondary source tree; queued after primary runtime surface | [source-file plan](source-file-parity-audit-plan-2026-04-22.md) | - |
| `src/lcc/etc/linux.c` | `1` | Secondary source tree; queued after primary runtime surface | [source-file plan](source-file-parity-audit-plan-2026-04-22.md) | - |
| `src/lcc/etc/ops.c` | `2` | Secondary source tree; queued after primary runtime surface | [source-file plan](source-file-parity-audit-plan-2026-04-22.md) | - |
| `src/lcc/etc/osf.c` | `1` | Secondary source tree; queued after primary runtime surface | [source-file plan](source-file-parity-audit-plan-2026-04-22.md) | - |
| `src/lcc/etc/solaris.c` | `1` | Secondary source tree; queued after primary runtime surface | [source-file plan](source-file-parity-audit-plan-2026-04-22.md) | - |
| `src/lcc/etc/win32.c` | `1` | Secondary source tree; queued after primary runtime surface | [source-file plan](source-file-parity-audit-plan-2026-04-22.md) | - |
| `src/lcc/lburg/gram.c` | `4` | Secondary source tree; queued after primary runtime surface | [source-file plan](source-file-parity-audit-plan-2026-04-22.md) | - |
| `src/lcc/lburg/lburg.c` | `29` | Secondary source tree; queued after primary runtime surface | [source-file plan](source-file-parity-audit-plan-2026-04-22.md) | - |
| `src/lcc/lib/assert.c` | `1` | Secondary source tree; queued after primary runtime surface | [source-file plan](source-file-parity-audit-plan-2026-04-22.md) | - |
| `src/lcc/lib/bbexit.c` | `5` | Secondary source tree; queued after primary runtime surface | [source-file plan](source-file-parity-audit-plan-2026-04-22.md) | - |
| `src/lcc/lib/yynull.c` | `1` | Secondary source tree; queued after primary runtime surface | [source-file plan](source-file-parity-audit-plan-2026-04-22.md) | - |
| `src/lcc/src/2html.c` | `32` | Secondary source tree; queued after primary runtime surface | [source-file plan](source-file-parity-audit-plan-2026-04-22.md) | - |
| `src/lcc/src/alloc.c` | `6` | Secondary source tree; queued after primary runtime surface | [source-file plan](source-file-parity-audit-plan-2026-04-22.md) | - |
| `src/lcc/src/asdl.c` | `30` | Secondary source tree; queued after primary runtime surface | [source-file plan](source-file-parity-audit-plan-2026-04-22.md) | - |
| `src/lcc/src/bind.c` | `0` | Secondary source tree; queued after primary runtime surface | [source-file plan](source-file-parity-audit-plan-2026-04-22.md) | - |
| `src/lcc/src/bytecode.c` | `23` | Secondary source tree; queued after primary runtime surface | [source-file plan](source-file-parity-audit-plan-2026-04-22.md) | - |
| `src/lcc/src/dag.c` | `25` | Secondary source tree; queued after primary runtime surface | [source-file plan](source-file-parity-audit-plan-2026-04-22.md) | - |
| `src/lcc/src/decl.c` | `26` | Secondary source tree; queued after primary runtime surface | [source-file plan](source-file-parity-audit-plan-2026-04-22.md) | - |
| `src/lcc/src/enode.c` | `22` | Secondary source tree; queued after primary runtime surface | [source-file plan](source-file-parity-audit-plan-2026-04-22.md) | - |
| `src/lcc/src/error.c` | `7` | Secondary source tree; queued after primary runtime surface | [source-file plan](source-file-parity-audit-plan-2026-04-22.md) | - |
| `src/lcc/src/event.c` | `2` | Secondary source tree; queued after primary runtime surface | [source-file plan](source-file-parity-audit-plan-2026-04-22.md) | - |
| `src/lcc/src/expr.c` | `25` | Secondary source tree; queued after primary runtime surface | [source-file plan](source-file-parity-audit-plan-2026-04-22.md) | - |
| `src/lcc/src/gen.c` | `47` | Secondary source tree; queued after primary runtime surface | [source-file plan](source-file-parity-audit-plan-2026-04-22.md) | - |
| `src/lcc/src/init.c` | `10` | Secondary source tree; queued after primary runtime surface | [source-file plan](source-file-parity-audit-plan-2026-04-22.md) | - |
| `src/lcc/src/inits.c` | `1` | Secondary source tree; queued after primary runtime surface | [source-file plan](source-file-parity-audit-plan-2026-04-22.md) | - |
| `src/lcc/src/input.c` | `5` | Secondary source tree; queued after primary runtime surface | [source-file plan](source-file-parity-audit-plan-2026-04-22.md) | - |
| `src/lcc/src/lex.c` | `9` | Secondary source tree; queued after primary runtime surface | [source-file plan](source-file-parity-audit-plan-2026-04-22.md) | - |
| `src/lcc/src/list.c` | `3` | Secondary source tree; queued after primary runtime surface | [source-file plan](source-file-parity-audit-plan-2026-04-22.md) | - |
| `src/lcc/src/main.c` | `5` | Secondary source tree; queued after primary runtime surface | [source-file plan](source-file-parity-audit-plan-2026-04-22.md) | - |
| `src/lcc/src/null.c` | `25` | Secondary source tree; queued after primary runtime surface | [source-file plan](source-file-parity-audit-plan-2026-04-22.md) | - |
| `src/lcc/src/output.c` | `7` | Secondary source tree; queued after primary runtime surface | [source-file plan](source-file-parity-audit-plan-2026-04-22.md) | - |
| `src/lcc/src/pass2.c` | `23` | Secondary source tree; queued after primary runtime surface | [source-file plan](source-file-parity-audit-plan-2026-04-22.md) | - |
| `src/lcc/src/prof.c` | `8` | Secondary source tree; queued after primary runtime surface | [source-file plan](source-file-parity-audit-plan-2026-04-22.md) | - |
| `src/lcc/src/profio.c` | `11` | Secondary source tree; queued after primary runtime surface | [source-file plan](source-file-parity-audit-plan-2026-04-22.md) | - |
| `src/lcc/src/simp.c` | `14` | Secondary source tree; queued after primary runtime surface | [source-file plan](source-file-parity-audit-plan-2026-04-22.md) | - |
| `src/lcc/src/stab.c` | `11` | Secondary source tree; queued after primary runtime surface | [source-file plan](source-file-parity-audit-plan-2026-04-22.md) | - |
| `src/lcc/src/stmt.c` | `24` | Secondary source tree; queued after primary runtime surface | [source-file plan](source-file-parity-audit-plan-2026-04-22.md) | - |
| `src/lcc/src/string.c` | `3` | Secondary source tree; queued after primary runtime surface | [source-file plan](source-file-parity-audit-plan-2026-04-22.md) | - |
| `src/lcc/src/sym.c` | `21` | Secondary source tree; queued after primary runtime surface | [source-file plan](source-file-parity-audit-plan-2026-04-22.md) | - |
| `src/lcc/src/symbolic.c` | `32` | Secondary source tree; queued after primary runtime surface | [source-file plan](source-file-parity-audit-plan-2026-04-22.md) | - |
| `src/lcc/src/trace.c` | `6` | Secondary source tree; queued after primary runtime surface | [source-file plan](source-file-parity-audit-plan-2026-04-22.md) | - |
| `src/lcc/src/tree.c` | `9` | Secondary source tree; queued after primary runtime surface | [source-file plan](source-file-parity-audit-plan-2026-04-22.md) | - |
| `src/lcc/src/types.c` | `31` | Secondary source tree; queued after primary runtime surface | [source-file plan](source-file-parity-audit-plan-2026-04-22.md) | - |
| `src/lcc/tst/8q.c` | `0` | Secondary source tree; queued after primary runtime surface | [source-file plan](source-file-parity-audit-plan-2026-04-22.md) | - |
| `src/lcc/tst/array.c` | `0` | Secondary source tree; queued after primary runtime surface | [source-file plan](source-file-parity-audit-plan-2026-04-22.md) | - |
| `src/lcc/tst/cf.c` | `0` | Secondary source tree; queued after primary runtime surface | [source-file plan](source-file-parity-audit-plan-2026-04-22.md) | - |
| `src/lcc/tst/cq.c` | `2` | Secondary source tree; queued after primary runtime surface | [source-file plan](source-file-parity-audit-plan-2026-04-22.md) | - |
| `src/lcc/tst/cvt.c` | `1` | Secondary source tree; queued after primary runtime surface | [source-file plan](source-file-parity-audit-plan-2026-04-22.md) | - |
| `src/lcc/tst/fields.c` | `0` | Secondary source tree; queued after primary runtime surface | [source-file plan](source-file-parity-audit-plan-2026-04-22.md) | - |
| `src/lcc/tst/front.c` | `4` | Secondary source tree; queued after primary runtime surface | [source-file plan](source-file-parity-audit-plan-2026-04-22.md) | - |
| `src/lcc/tst/incr.c` | `0` | Secondary source tree; queued after primary runtime surface | [source-file plan](source-file-parity-audit-plan-2026-04-22.md) | - |
| `src/lcc/tst/init.c` | `0` | Secondary source tree; queued after primary runtime surface | [source-file plan](source-file-parity-audit-plan-2026-04-22.md) | - |
| `src/lcc/tst/limits.c` | `0` | Secondary source tree; queued after primary runtime surface | [source-file plan](source-file-parity-audit-plan-2026-04-22.md) | - |
| `src/lcc/tst/paranoia.c` | `1` | Secondary source tree; queued after primary runtime surface | [source-file plan](source-file-parity-audit-plan-2026-04-22.md) | - |
| `src/lcc/tst/sort.c` | `0` | Secondary source tree; queued after primary runtime surface | [source-file plan](source-file-parity-audit-plan-2026-04-22.md) | - |
| `src/lcc/tst/spill.c` | `0` | Secondary source tree; queued after primary runtime surface | [source-file plan](source-file-parity-audit-plan-2026-04-22.md) | - |
| `src/lcc/tst/stdarg.c` | `0` | Secondary source tree; queued after primary runtime surface | [source-file plan](source-file-parity-audit-plan-2026-04-22.md) | - |
| `src/lcc/tst/struct.c` | `5` | Secondary source tree; queued after primary runtime surface | [source-file plan](source-file-parity-audit-plan-2026-04-22.md) | - |
| `src/lcc/tst/switch.c` | `0` | Secondary source tree; queued after primary runtime surface | [source-file plan](source-file-parity-audit-plan-2026-04-22.md) | - |
| `src/lcc/tst/wf1.c` | `1` | Secondary source tree; queued after primary runtime surface | [source-file plan](source-file-parity-audit-plan-2026-04-22.md) | - |
| `src/lcc/tst/yacc.c` | `1` | Secondary source tree; queued after primary runtime surface | [source-file plan](source-file-parity-audit-plan-2026-04-22.md) | - |
### `src/libs` (25 files)

| File | Functions | Current parity state | Primary evidence | Gap note |
| --- | ---: | --- | --- | --- |
| `src/libs/cmdlib/cmdlib.cpp` | `41` | Secondary source tree; queued after primary runtime surface | [source-file plan](source-file-parity-audit-plan-2026-04-22.md) | - |
| `src/libs/jpeg6/jcomapi.cpp` | `0` | Secondary source tree; queued after primary runtime surface | [source-file plan](source-file-parity-audit-plan-2026-04-22.md) | - |
| `src/libs/jpeg6/jdapimin.cpp` | `0` | Secondary source tree; queued after primary runtime surface | [source-file plan](source-file-parity-audit-plan-2026-04-22.md) | - |
| `src/libs/jpeg6/jdapistd.cpp` | `0` | Secondary source tree; queued after primary runtime surface | [source-file plan](source-file-parity-audit-plan-2026-04-22.md) | - |
| `src/libs/jpeg6/jdatasrc.cpp` | `0` | Secondary source tree; queued after primary runtime surface | [source-file plan](source-file-parity-audit-plan-2026-04-22.md) | - |
| `src/libs/jpeg6/jdcoefct.cpp` | `0` | Secondary source tree; queued after primary runtime surface | [source-file plan](source-file-parity-audit-plan-2026-04-22.md) | - |
| `src/libs/jpeg6/jdcolor.cpp` | `0` | Secondary source tree; queued after primary runtime surface | [source-file plan](source-file-parity-audit-plan-2026-04-22.md) | - |
| `src/libs/jpeg6/jddctmgr.cpp` | `0` | Secondary source tree; queued after primary runtime surface | [source-file plan](source-file-parity-audit-plan-2026-04-22.md) | - |
| `src/libs/jpeg6/jdhuff.cpp` | `0` | Secondary source tree; queued after primary runtime surface | [source-file plan](source-file-parity-audit-plan-2026-04-22.md) | - |
| `src/libs/jpeg6/jdinput.cpp` | `0` | Secondary source tree; queued after primary runtime surface | [source-file plan](source-file-parity-audit-plan-2026-04-22.md) | - |
| `src/libs/jpeg6/jdmainct.cpp` | `0` | Secondary source tree; queued after primary runtime surface | [source-file plan](source-file-parity-audit-plan-2026-04-22.md) | - |
| `src/libs/jpeg6/jdmarker.cpp` | `0` | Secondary source tree; queued after primary runtime surface | [source-file plan](source-file-parity-audit-plan-2026-04-22.md) | - |
| `src/libs/jpeg6/jdmaster.cpp` | `0` | Secondary source tree; queued after primary runtime surface | [source-file plan](source-file-parity-audit-plan-2026-04-22.md) | - |
| `src/libs/jpeg6/jdpostct.cpp` | `0` | Secondary source tree; queued after primary runtime surface | [source-file plan](source-file-parity-audit-plan-2026-04-22.md) | - |
| `src/libs/jpeg6/jdsample.cpp` | `0` | Secondary source tree; queued after primary runtime surface | [source-file plan](source-file-parity-audit-plan-2026-04-22.md) | - |
| `src/libs/jpeg6/jdtrans.cpp` | `0` | Secondary source tree; queued after primary runtime surface | [source-file plan](source-file-parity-audit-plan-2026-04-22.md) | - |
| `src/libs/jpeg6/jerror.cpp` | `0` | Secondary source tree; queued after primary runtime surface | [source-file plan](source-file-parity-audit-plan-2026-04-22.md) | - |
| `src/libs/jpeg6/jfdctflt.cpp` | `0` | Secondary source tree; queued after primary runtime surface | [source-file plan](source-file-parity-audit-plan-2026-04-22.md) | - |
| `src/libs/jpeg6/jidctflt.cpp` | `0` | Secondary source tree; queued after primary runtime surface | [source-file plan](source-file-parity-audit-plan-2026-04-22.md) | - |
| `src/libs/jpeg6/jmemmgr.cpp` | `0` | Secondary source tree; queued after primary runtime surface | [source-file plan](source-file-parity-audit-plan-2026-04-22.md) | - |
| `src/libs/jpeg6/jmemnobs.cpp` | `0` | Secondary source tree; queued after primary runtime surface | [source-file plan](source-file-parity-audit-plan-2026-04-22.md) | - |
| `src/libs/jpeg6/jpgload.cpp` | `1` | Secondary source tree; queued after primary runtime surface | [source-file plan](source-file-parity-audit-plan-2026-04-22.md) | - |
| `src/libs/jpeg6/jutils.cpp` | `0` | Secondary source tree; queued after primary runtime surface | [source-file plan](source-file-parity-audit-plan-2026-04-22.md) | - |
| `src/libs/pak/pakstuff.cpp` | `46` | Secondary source tree; queued after primary runtime surface | [source-file plan](source-file-parity-audit-plan-2026-04-22.md) | - |
| `src/libs/pak/unzip.cpp` | `61` | Secondary source tree; queued after primary runtime surface | [source-file plan](source-file-parity-audit-plan-2026-04-22.md) | - |
### `src/q3asm` (2 files)

| File | Functions | Current parity state | Primary evidence | Gap note |
| --- | ---: | --- | --- | --- |
| `src/q3asm/cmdlib.c` | `58` | Secondary source tree; queued after primary runtime surface | [source-file plan](source-file-parity-audit-plan-2026-04-22.md) | - |
| `src/q3asm/q3asm.c` | `18` | Secondary source tree; queued after primary runtime surface | [source-file plan](source-file-parity-audit-plan-2026-04-22.md) | - |
### `src/q3map` (28 files)

| File | Functions | Current parity state | Primary evidence | Gap note |
| --- | ---: | --- | --- | --- |
| `src/q3map/brush.c` | `22` | Secondary source tree; queued after primary runtime surface | [source-file plan](source-file-parity-audit-plan-2026-04-22.md) | - |
| `src/q3map/brush_primit.c` | `1` | Secondary source tree; queued after primary runtime surface | [source-file plan](source-file-parity-audit-plan-2026-04-22.md) | - |
| `src/q3map/bsp.c` | `7` | Secondary source tree; queued after primary runtime surface | [source-file plan](source-file-parity-audit-plan-2026-04-22.md) | - |
| `src/q3map/facebsp.c` | `9` | Secondary source tree; queued after primary runtime surface | [source-file plan](source-file-parity-audit-plan-2026-04-22.md) | - |
| `src/q3map/fog.c` | `6` | Secondary source tree; queued after primary runtime surface | [source-file plan](source-file-parity-audit-plan-2026-04-22.md) | - |
| `src/q3map/gldraw.c` | `10` | Secondary source tree; queued after primary runtime surface | [source-file plan](source-file-parity-audit-plan-2026-04-22.md) | - |
| `src/q3map/glfile.c` | `5` | Secondary source tree; queued after primary runtime surface | [source-file plan](source-file-parity-audit-plan-2026-04-22.md) | - |
| `src/q3map/leakfile.c` | `1` | Secondary source tree; queued after primary runtime surface | [source-file plan](source-file-parity-audit-plan-2026-04-22.md) | - |
| `src/q3map/light.c` | `27` | Secondary source tree; queued after primary runtime surface | [source-file plan](source-file-parity-audit-plan-2026-04-22.md) | - |
| `src/q3map/light_trace.c` | `19` | Secondary source tree; queued after primary runtime surface | [source-file plan](source-file-parity-audit-plan-2026-04-22.md) | - |
| `src/q3map/lightmaps.c` | `5` | Secondary source tree; queued after primary runtime surface | [source-file plan](source-file-parity-audit-plan-2026-04-22.md) | - |
| `src/q3map/lightv.c` | `76` | Secondary source tree; queued after primary runtime surface | [source-file plan](source-file-parity-audit-plan-2026-04-22.md) | - |
| `src/q3map/map.c` | `22` | Secondary source tree; queued after primary runtime surface | [source-file plan](source-file-parity-audit-plan-2026-04-22.md) | - |
| `src/q3map/mesh.c` | `13` | Secondary source tree; queued after primary runtime surface | [source-file plan](source-file-parity-audit-plan-2026-04-22.md) | - |
| `src/q3map/misc_model.c` | `5` | Secondary source tree; queued after primary runtime surface | [source-file plan](source-file-parity-audit-plan-2026-04-22.md) | - |
| `src/q3map/nodraw.c` | `4` | Secondary source tree; queued after primary runtime surface | [source-file plan](source-file-parity-audit-plan-2026-04-22.md) | - |
| `src/q3map/patch.c` | `5` | Secondary source tree; queued after primary runtime surface | [source-file plan](source-file-parity-audit-plan-2026-04-22.md) | - |
| `src/q3map/portals.c` | `22` | Secondary source tree; queued after primary runtime surface | [source-file plan](source-file-parity-audit-plan-2026-04-22.md) | - |
| `src/q3map/prtfile.c` | `6` | Secondary source tree; queued after primary runtime surface | [source-file plan](source-file-parity-audit-plan-2026-04-22.md) | - |
| `src/q3map/shaders.c` | `6` | Secondary source tree; queued after primary runtime surface | [source-file plan](source-file-parity-audit-plan-2026-04-22.md) | - |
| `src/q3map/soundv.c` | `76` | Secondary source tree; queued after primary runtime surface | [source-file plan](source-file-parity-audit-plan-2026-04-22.md) | - |
| `src/q3map/surface.c` | `24` | Secondary source tree; queued after primary runtime surface | [source-file plan](source-file-parity-audit-plan-2026-04-22.md) | - |
| `src/q3map/terrain.c` | `21` | Secondary source tree; queued after primary runtime surface | [source-file plan](source-file-parity-audit-plan-2026-04-22.md) | - |
| `src/q3map/tjunction.c` | `8` | Secondary source tree; queued after primary runtime surface | [source-file plan](source-file-parity-audit-plan-2026-04-22.md) | - |
| `src/q3map/tree.c` | `5` | Secondary source tree; queued after primary runtime surface | [source-file plan](source-file-parity-audit-plan-2026-04-22.md) | - |
| `src/q3map/vis.c` | `24` | Secondary source tree; queued after primary runtime surface | [source-file plan](source-file-parity-audit-plan-2026-04-22.md) | - |
| `src/q3map/visflow.c` | `20` | Secondary source tree; queued after primary runtime surface | [source-file plan](source-file-parity-audit-plan-2026-04-22.md) | - |
| `src/q3map/writebsp.c` | `11` | Secondary source tree; queued after primary runtime surface | [source-file plan](source-file-parity-audit-plan-2026-04-22.md) | - |
### `src/q3radiant` (97 files)

| File | Functions | Current parity state | Primary evidence | Gap note |
| --- | ---: | --- | --- | --- |
| `src/q3radiant/BSInput.cpp` | `0` | Secondary source tree; queued after primary runtime surface | [source-file plan](source-file-parity-audit-plan-2026-04-22.md) | - |
| `src/q3radiant/Bmp.cpp` | `11` | Secondary source tree; queued after primary runtime surface | [source-file plan](source-file-parity-audit-plan-2026-04-22.md) | - |
| `src/q3radiant/Brush.cpp` | `77` | Secondary source tree; queued after primary runtime surface | [source-file plan](source-file-parity-audit-plan-2026-04-22.md) | - |
| `src/q3radiant/BrushScript.cpp` | `28` | Secondary source tree; queued after primary runtime surface | [source-file plan](source-file-parity-audit-plan-2026-04-22.md) | - |
| `src/q3radiant/CSG.CPP` | `8` | Secondary source tree; queued after primary runtime surface | [source-file plan](source-file-parity-audit-plan-2026-04-22.md) | - |
| `src/q3radiant/CamWnd.cpp` | `1` | Secondary source tree; queued after primary runtime surface | [source-file plan](source-file-parity-audit-plan-2026-04-22.md) | - |
| `src/q3radiant/CapDialog.cpp` | `0` | Secondary source tree; queued after primary runtime surface | [source-file plan](source-file-parity-audit-plan-2026-04-22.md) | - |
| `src/q3radiant/ChildFrm.cpp` | `0` | Secondary source tree; queued after primary runtime surface | [source-file plan](source-file-parity-audit-plan-2026-04-22.md) | - |
| `src/q3radiant/CommandsDlg.cpp` | `0` | Secondary source tree; queued after primary runtime surface | [source-file plan](source-file-parity-audit-plan-2026-04-22.md) | - |
| `src/q3radiant/DRAG.CPP` | `7` | Secondary source tree; queued after primary runtime surface | [source-file plan](source-file-parity-audit-plan-2026-04-22.md) | - |
| `src/q3radiant/DialogInfo.cpp` | `2` | Secondary source tree; queued after primary runtime surface | [source-file plan](source-file-parity-audit-plan-2026-04-22.md) | - |
| `src/q3radiant/DialogTextures.cpp` | `0` | Secondary source tree; queued after primary runtime surface | [source-file plan](source-file-parity-audit-plan-2026-04-22.md) | - |
| `src/q3radiant/DialogThick.cpp` | `0` | Secondary source tree; queued after primary runtime surface | [source-file plan](source-file-parity-audit-plan-2026-04-22.md) | - |
| `src/q3radiant/DlgEvent.cpp` | `0` | Secondary source tree; queued after primary runtime surface | [source-file plan](source-file-parity-audit-plan-2026-04-22.md) | - |
| `src/q3radiant/ECLASS.CPP` | `13` | Secondary source tree; queued after primary runtime surface | [source-file plan](source-file-parity-audit-plan-2026-04-22.md) | - |
| `src/q3radiant/ENTITY.CPP` | `29` | Secondary source tree; queued after primary runtime surface | [source-file plan](source-file-parity-audit-plan-2026-04-22.md) | - |
| `src/q3radiant/EditWnd.cpp` | `0` | Secondary source tree; queued after primary runtime surface | [source-file plan](source-file-parity-audit-plan-2026-04-22.md) | - |
| `src/q3radiant/EntityListDlg.cpp` | `0` | Secondary source tree; queued after primary runtime surface | [source-file plan](source-file-parity-audit-plan-2026-04-22.md) | - |
| `src/q3radiant/FNMATCH.CPP` | `1` | Secondary source tree; queued after primary runtime surface | [source-file plan](source-file-parity-audit-plan-2026-04-22.md) | - |
| `src/q3radiant/FindTextureDlg.cpp` | `0` | Secondary source tree; queued after primary runtime surface | [source-file plan](source-file-parity-audit-plan-2026-04-22.md) | - |
| `src/q3radiant/GLInterface.cpp` | `4` | Secondary source tree; queued after primary runtime surface | [source-file plan](source-file-parity-audit-plan-2026-04-22.md) | - |
| `src/q3radiant/GroupBar.cpp` | `0` | Secondary source tree; queued after primary runtime surface | [source-file plan](source-file-parity-audit-plan-2026-04-22.md) | - |
| `src/q3radiant/GroupDlg.cpp` | `17` | Secondary source tree; queued after primary runtime surface | [source-file plan](source-file-parity-audit-plan-2026-04-22.md) | - |
| `src/q3radiant/IEpairs.cpp` | `0` | Secondary source tree; queued after primary runtime surface | [source-file plan](source-file-parity-audit-plan-2026-04-22.md) | - |
| `src/q3radiant/IShaders.cpp` | `1` | Secondary source tree; queued after primary runtime surface | [source-file plan](source-file-parity-audit-plan-2026-04-22.md) | - |
| `src/q3radiant/LBMLIB.CPP` | `18` | Secondary source tree; queued after primary runtime surface | [source-file plan](source-file-parity-audit-plan-2026-04-22.md) | - |
| `src/q3radiant/LstToolBar.cpp` | `0` | Secondary source tree; queued after primary runtime surface | [source-file plan](source-file-parity-audit-plan-2026-04-22.md) | - |
| `src/q3radiant/MAP.CPP` | `26` | Secondary source tree; queued after primary runtime surface | [source-file plan](source-file-parity-audit-plan-2026-04-22.md) | - |
| `src/q3radiant/MATHLIB.CPP` | `23` | Secondary source tree; queued after primary runtime surface | [source-file plan](source-file-parity-audit-plan-2026-04-22.md) | - |
| `src/q3radiant/MRU.CPP` | `15` | Secondary source tree; queued after primary runtime surface | [source-file plan](source-file-parity-audit-plan-2026-04-22.md) | - |
| `src/q3radiant/MainFrm.cpp` | `6` | Secondary source tree; queued after primary runtime surface | [source-file plan](source-file-parity-audit-plan-2026-04-22.md) | - |
| `src/q3radiant/MapInfo.cpp` | `0` | Secondary source tree; queued after primary runtime surface | [source-file plan](source-file-parity-audit-plan-2026-04-22.md) | - |
| `src/q3radiant/Messaging.cpp` | `9` | Secondary source tree; queued after primary runtime surface | [source-file plan](source-file-parity-audit-plan-2026-04-22.md) | - |
| `src/q3radiant/NameDlg.cpp` | `0` | Secondary source tree; queued after primary runtime surface | [source-file plan](source-file-parity-audit-plan-2026-04-22.md) | - |
| `src/q3radiant/NewProjDlg.cpp` | `0` | Secondary source tree; queued after primary runtime surface | [source-file plan](source-file-parity-audit-plan-2026-04-22.md) | - |
| `src/q3radiant/PARSE.CPP` | `4` | Secondary source tree; queued after primary runtime surface | [source-file plan](source-file-parity-audit-plan-2026-04-22.md) | - |
| `src/q3radiant/PMESH.CPP` | `125` | Secondary source tree; queued after primary runtime surface | [source-file plan](source-file-parity-audit-plan-2026-04-22.md) | - |
| `src/q3radiant/POINTS.CPP` | `6` | Secondary source tree; queued after primary runtime surface | [source-file plan](source-file-parity-audit-plan-2026-04-22.md) | - |
| `src/q3radiant/PatchDensityDlg.cpp` | `0` | Secondary source tree; queued after primary runtime surface | [source-file plan](source-file-parity-audit-plan-2026-04-22.md) | - |
| `src/q3radiant/PatchDialog.cpp` | `2` | Secondary source tree; queued after primary runtime surface | [source-file plan](source-file-parity-audit-plan-2026-04-22.md) | - |
| `src/q3radiant/PlugIn.cpp` | `0` | Secondary source tree; queued after primary runtime surface | [source-file plan](source-file-parity-audit-plan-2026-04-22.md) | - |
| `src/q3radiant/PlugInManager.cpp` | `73` | Secondary source tree; queued after primary runtime surface | [source-file plan](source-file-parity-audit-plan-2026-04-22.md) | - |
| `src/q3radiant/PluginEntities.cpp` | `1` | Secondary source tree; queued after primary runtime surface | [source-file plan](source-file-parity-audit-plan-2026-04-22.md) | - |
| `src/q3radiant/PrefsDlg.cpp` | `0` | Secondary source tree; queued after primary runtime surface | [source-file plan](source-file-parity-audit-plan-2026-04-22.md) | - |
| `src/q3radiant/QE3.CPP` | `20` | Secondary source tree; queued after primary runtime surface | [source-file plan](source-file-parity-audit-plan-2026-04-22.md) | - |
| `src/q3radiant/QGL_WIN.C` | `2` | Secondary source tree; queued after primary runtime surface | [source-file plan](source-file-parity-audit-plan-2026-04-22.md) | - |
| `src/q3radiant/QGL_WIN.CPP` | `2` | Secondary source tree; queued after primary runtime surface | [source-file plan](source-file-parity-audit-plan-2026-04-22.md) | - |
| `src/q3radiant/RADBSP.CPP` | `1` | Secondary source tree; queued after primary runtime surface | [source-file plan](source-file-parity-audit-plan-2026-04-22.md) | - |
| `src/q3radiant/RADEditView.cpp` | `0` | Secondary source tree; queued after primary runtime surface | [source-file plan](source-file-parity-audit-plan-2026-04-22.md) | - |
| `src/q3radiant/RADEditWnd.cpp` | `0` | Secondary source tree; queued after primary runtime surface | [source-file plan](source-file-parity-audit-plan-2026-04-22.md) | - |
| `src/q3radiant/Radiant.cpp` | `0` | Secondary source tree; queued after primary runtime surface | [source-file plan](source-file-parity-audit-plan-2026-04-22.md) | - |
| `src/q3radiant/RadiantDoc.cpp` | `0` | Secondary source tree; queued after primary runtime surface | [source-file plan](source-file-parity-audit-plan-2026-04-22.md) | - |
| `src/q3radiant/RadiantView.cpp` | `0` | Secondary source tree; queued after primary runtime surface | [source-file plan](source-file-parity-audit-plan-2026-04-22.md) | - |
| `src/q3radiant/RotateDlg.cpp` | `0` | Secondary source tree; queued after primary runtime surface | [source-file plan](source-file-parity-audit-plan-2026-04-22.md) | - |
| `src/q3radiant/SELECT.CPP` | `43` | Secondary source tree; queued after primary runtime surface | [source-file plan](source-file-parity-audit-plan-2026-04-22.md) | - |
| `src/q3radiant/ScaleDialog.cpp` | `0` | Secondary source tree; queued after primary runtime surface | [source-file plan](source-file-parity-audit-plan-2026-04-22.md) | - |
| `src/q3radiant/ScriptDlg.cpp` | `0` | Secondary source tree; queued after primary runtime surface | [source-file plan](source-file-parity-audit-plan-2026-04-22.md) | - |
| `src/q3radiant/SelectedFace.cpp` | `4` | Secondary source tree; queued after primary runtime surface | [source-file plan](source-file-parity-audit-plan-2026-04-22.md) | - |
| `src/q3radiant/ShaderEdit.cpp` | `0` | Secondary source tree; queued after primary runtime surface | [source-file plan](source-file-parity-audit-plan-2026-04-22.md) | - |
| `src/q3radiant/ShaderInfo.cpp` | `0` | Secondary source tree; queued after primary runtime surface | [source-file plan](source-file-parity-audit-plan-2026-04-22.md) | - |
| `src/q3radiant/StdAfx.cpp` | `0` | Secondary source tree; queued after primary runtime surface | [source-file plan](source-file-parity-audit-plan-2026-04-22.md) | - |
| `src/q3radiant/SurfaceDlg.cpp` | `3` | Secondary source tree; queued after primary runtime surface | [source-file plan](source-file-parity-audit-plan-2026-04-22.md) | - |
| `src/q3radiant/SurfacePlugin.cpp` | `1` | Secondary source tree; queued after primary runtime surface | [source-file plan](source-file-parity-audit-plan-2026-04-22.md) | - |
| `src/q3radiant/TexEdit.cpp` | `0` | Secondary source tree; queued after primary runtime surface | [source-file plan](source-file-parity-audit-plan-2026-04-22.md) | - |
| `src/q3radiant/TexWnd.cpp` | `54` | Secondary source tree; queued after primary runtime surface | [source-file plan](source-file-parity-audit-plan-2026-04-22.md) | - |
| `src/q3radiant/TextureBar.cpp` | `0` | Secondary source tree; queued after primary runtime surface | [source-file plan](source-file-parity-audit-plan-2026-04-22.md) | - |
| `src/q3radiant/TextureLayout.cpp` | `0` | Secondary source tree; queued after primary runtime surface | [source-file plan](source-file-parity-audit-plan-2026-04-22.md) | - |
| `src/q3radiant/TextureLoad.cpp` | `0` | Secondary source tree; queued after primary runtime surface | [source-file plan](source-file-parity-audit-plan-2026-04-22.md) | - |
| `src/q3radiant/ToolWnd.cpp` | `0` | Secondary source tree; queued after primary runtime surface | [source-file plan](source-file-parity-audit-plan-2026-04-22.md) | - |
| `src/q3radiant/Undo.cpp` | `23` | Secondary source tree; queued after primary runtime surface | [source-file plan](source-file-parity-audit-plan-2026-04-22.md) | - |
| `src/q3radiant/VERTSEL.CPP` | `7` | Secondary source tree; queued after primary runtime surface | [source-file plan](source-file-parity-audit-plan-2026-04-22.md) | - |
| `src/q3radiant/WIN_CAM.CPP` | `2` | Secondary source tree; queued after primary runtime surface | [source-file plan](source-file-parity-audit-plan-2026-04-22.md) | - |
| `src/q3radiant/WIN_DLG.CPP` | `17` | Secondary source tree; queued after primary runtime surface | [source-file plan](source-file-parity-audit-plan-2026-04-22.md) | - |
| `src/q3radiant/WIN_QE3.CPP` | `34` | Secondary source tree; queued after primary runtime surface | [source-file plan](source-file-parity-audit-plan-2026-04-22.md) | - |
| `src/q3radiant/WIN_XY.CPP` | `4` | Secondary source tree; queued after primary runtime surface | [source-file plan](source-file-parity-audit-plan-2026-04-22.md) | - |
| `src/q3radiant/WIN_Z.CPP` | `2` | Secondary source tree; queued after primary runtime surface | [source-file plan](source-file-parity-audit-plan-2026-04-22.md) | - |
| `src/q3radiant/WaveOpen.cpp` | `0` | Secondary source tree; queued after primary runtime surface | [source-file plan](source-file-parity-audit-plan-2026-04-22.md) | - |
| `src/q3radiant/Win_ent.cpp` | `21` | Secondary source tree; queued after primary runtime surface | [source-file plan](source-file-parity-audit-plan-2026-04-22.md) | - |
| `src/q3radiant/Win_main.cpp` | `20` | Secondary source tree; queued after primary runtime surface | [source-file plan](source-file-parity-audit-plan-2026-04-22.md) | - |
| `src/q3radiant/Winding.cpp` | `21` | Secondary source tree; queued after primary runtime surface | [source-file plan](source-file-parity-audit-plan-2026-04-22.md) | - |
| `src/q3radiant/XYWnd.cpp` | `21` | Secondary source tree; queued after primary runtime surface | [source-file plan](source-file-parity-audit-plan-2026-04-22.md) | - |
| `src/q3radiant/Z.CPP` | `7` | Secondary source tree; queued after primary runtime surface | [source-file plan](source-file-parity-audit-plan-2026-04-22.md) | - |
| `src/q3radiant/ZView.cpp` | `0` | Secondary source tree; queued after primary runtime surface | [source-file plan](source-file-parity-audit-plan-2026-04-22.md) | - |
| `src/q3radiant/ZWnd.cpp` | `0` | Secondary source tree; queued after primary runtime surface | [source-file plan](source-file-parity-audit-plan-2026-04-22.md) | - |
| `src/q3radiant/brush_primit.cpp` | `12` | Secondary source tree; queued after primary runtime surface | [source-file plan](source-file-parity-audit-plan-2026-04-22.md) | - |
| `src/q3radiant/cameratargetdlg.cpp` | `0` | Secondary source tree; queued after primary runtime surface | [source-file plan](source-file-parity-audit-plan-2026-04-22.md) | - |
| `src/q3radiant/cbrushstub.cpp` | `21` | Secondary source tree; queued after primary runtime surface | [source-file plan](source-file-parity-audit-plan-2026-04-22.md) | - |
| `src/q3radiant/dlgcamera.cpp` | `2` | Secondary source tree; queued after primary runtime surface | [source-file plan](source-file-parity-audit-plan-2026-04-22.md) | - |
| `src/q3radiant/splines/math_angles.cpp` | `3` | Secondary source tree; queued after primary runtime surface | [source-file plan](source-file-parity-audit-plan-2026-04-22.md) | - |
| `src/q3radiant/splines/math_matrix.cpp` | `3` | Secondary source tree; queued after primary runtime surface | [source-file plan](source-file-parity-audit-plan-2026-04-22.md) | - |
| `src/q3radiant/splines/math_quaternion.cpp` | `3` | Secondary source tree; queued after primary runtime surface | [source-file plan](source-file-parity-audit-plan-2026-04-22.md) | - |
| `src/q3radiant/splines/math_vector.cpp` | `1` | Secondary source tree; queued after primary runtime surface | [source-file plan](source-file-parity-audit-plan-2026-04-22.md) | - |
| `src/q3radiant/splines/q_parse.cpp` | `19` | Secondary source tree; queued after primary runtime surface | [source-file plan](source-file-parity-audit-plan-2026-04-22.md) | - |
| `src/q3radiant/splines/q_shared.cpp` | `47` | Secondary source tree; queued after primary runtime surface | [source-file plan](source-file-parity-audit-plan-2026-04-22.md) | - |
| `src/q3radiant/splines/splines.cpp` | `9` | Secondary source tree; queued after primary runtime surface | [source-file plan](source-file-parity-audit-plan-2026-04-22.md) | - |
| `src/q3radiant/splines/util_str.cpp` | `0` | Secondary source tree; queued after primary runtime surface | [source-file plan](source-file-parity-audit-plan-2026-04-22.md) | - |
| `src/q3radiant/terrain.cpp` | `56` | Secondary source tree; queued after primary runtime surface | [source-file plan](source-file-parity-audit-plan-2026-04-22.md) | - |
