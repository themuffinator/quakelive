# Source-File Parity Audit Plan

Last updated: 2026-05-20

## Purpose

This campaign breaks the broad parity story back down into manageable, checklisted file walks. It supplements `AUDIT.md`, `IMPLEMENTATION_PLAN.md`, and the existing subsystem ledgers instead of replacing them.

Per tracked file, the campaign should eventually produce:

- one concise row in the main source-file parity ledger;
- a dedicated per-file note whenever a concrete parity gap or documented bounded divergence is confirmed; and
- a function-by-function status table inside that per-file note.

## Scope

- Primary runtime and reconstruction surface tracked now: `208` files.
- Compatibility-only Unix/null surface tracked now: `17` files.
- Secondary tool, editor, compiler, and legacy source surface tracked now: `342` files.
- Header exception tracked alongside compilation units: `1` file (`src/common/platform/platform_config.h`).
- Total tracked source entries in the campaign ledger: `567`.
- Generated/vendor mirror trees under `src/libs/_deps/` and `src/libs/_build/` stay out of this campaign so the audit remains focused on repo-owned reconstruction and support sources.

## Deliverables

- Main ledger: `docs/reverse-engineering/source-file-parity-ledger-2026-04-22.md`
- Historical index: `docs/reverse-engineering/historical-audit-index-2026-04-22.md`
- File-level gap notes: `docs/reverse-engineering/source-file-gap-notes/`
- Repo-wide summary ledgers remain `AUDIT.md` and `docs/reverse-engineering/repo-wide-parity-audit-2026-04-21.md`.

## Checklist

### Phase 0 - Documentation Baseline

- [x] Keep `AUDIT.md` and `IMPLEMENTATION_PLAN.md` in place as gate-facing ledgers.
- [x] Create `source-file-parity-ledger-2026-04-22.md` as the clean main file-by-file ledger.
- [x] Create `historical-audit-index-2026-04-22.md` instead of renaming or moving older audit docs that workflows and tests already reference.
- [x] Seed `16` concrete per-file notes for the currently evidenced `RW-G01` documented divergences and `RW-G02` gap owners.

### Phase 1 - Strict-Retail Engine Core

- [x] Audit `src/common` function-by-function (`18` tracked files).
  2026-04-22 result: no new file-level gap owners were isolated beyond the
  existing `RW-G01` policy/configuration notes; `platform_steamworks.c`
  remains a retained Steamworks wrapper surface gated by
  `platform_config.h`, not a newly opened repo-wide gap owner.
- [x] Audit `src/code/qcommon` function-by-function (`19` tracked files).
  2026-04-22 result: no new file-level gap owners were isolated inside the
  closed strict-retail `qcommon` register; `vm_x86.c` remains the documented
  compatibility carry beneath the closed `vm.c` host-selection seam rather
  than a newly opened repo-wide or subsystem gap owner.
- [x] Audit `src/code/client` function-by-function (`22` tracked files).
  2026-04-22 result: no new file-level gap owners were isolated beyond the
  existing `RW-G01` notes for `ql_auth.c` and `cl_steam_resources.c`; the
  rest of the strict-retail client register remains closed on current
  evidence.
- [x] Audit `src/code/server` function-by-function (`11` tracked files).
  2026-04-22 result: no new file-level gap owners were isolated beyond the
  existing `RW-G01` note for `sv_rankings.c`; the rest of the strict-retail
  server register remains closed on current evidence.
- [x] Audit `src/code/renderer` function-by-function (`23` tracked files).
  2026-04-22 result plus 2026-05-20 renderer wiring refresh: no new
  file-level gap owners were isolated inside the closed strict-retail
  `renderer` register. The stale `R_fonsErrorCallback` module-runtime
  artifact remains part of `RW-G04` evidence freshness rather than a new
  source-file gap owner after the non-retail eager FontStash prebuild was
  removed from `tr_font.c`, the retained atlas upload path was restored to
  `GL_ALPHA`, and the `GetRefAPI` export table was realigned to the retail
  API version `9` / `0x9c` ABI tail.
- [x] Audit `src/code/win32` function-by-function (`11` tracked files).
  2026-04-22 result: no new file-level gap owners were isolated inside the
  closed strict-retail Windows platform register; the earlier `PS-G01`
  `win_glimp.c` pixel-format drift remains closed on current evidence.
- [x] Audit `src/code/botlib` function-by-function (`28` tracked files).
  2026-04-22 result: no new file-level gap owners were isolated inside the
  closed botlib internal register; the retained mapping-round `61`
  bridge/import ownership and deterministic AAS/reachability/goal-state
  proof lane still bound the tree on current evidence.

### Phase 2 - Module And Gameplay Surface

- [x] Audit `src/code/game` function-by-function (`45` tracked files).
  2026-04-22 result: no new file-level gap owners were isolated inside the
  closed strict-retail module register; the refreshed module audit, the
  qagame retail gate, the focused gameplay sweep, and the current
  auto-shuffle/countdown plus Clan Arena shuffle regression lanes still
  bound the tree on current evidence.
- [x] Audit `src/code/cgame` function-by-function (`22` tracked files).
  2026-04-22 result: no new file-level gap owners were isolated inside the
  closed strict-retail module register; the refreshed module audit, the
  focused cgame parity lane (`199 passed`, `1 skipped`), and the shared
  native export helper certification still bound the tree on current
  evidence.
- [x] Audit `src/code/ui` function-by-function (`9` tracked files) (read-only source tree).
  2026-04-22 result: no new file-level gap owners were isolated inside the
  closed strict-retail UI register; the refreshed UI audit, the focused UI
  parity lane (`56 passed`, `2 skipped`), and the clean read-only
  `src/ui` runtime-panel parity proof still bound the tree on current
  evidence.

### Phase 3 - Compatibility-Only Host Surface

- [x] Audit `src/code/unix` and convert tree-level `RW-G02` status into file-specific notes where warranted (`10` tracked files).
  2026-04-22 result: no new file-level gap owners were isolated beyond the
  existing `RW-G02` notes for `unix_main.c`, `linux_glimp.c`,
  `linux_snd.c`, and `linux_joystick.c`; the focused non-Windows
  portability lane (`8 passed`) and the current repo-wide audit still
  bound the remaining Unix files on current evidence.
- [x] Audit `src/code/null` and convert tree-level `RW-G02` status into file-specific notes where warranted (`7` tracked files).
  2026-04-22 result: the null compatibility walk isolated
  `null_glimp.c` as an additional `RW-G02` owner beside the existing
  notes for `null_main.c`, `null_client.c`, `null_input.c`, and
  `null_snddma.c`; the focused non-Windows portability lane
  (`8 passed`) and the current repo-wide audit still bound `null_net.c`
  and `mac_net.c` on current evidence.

### Phase 4 - Secondary Tool, Editor, Compiler, And Legacy Source Trees

- [x] Audit `src/code/bspc/`, `src/code/jpeg-6/`, and `src/code/splines/` after the primary runtime surface is complete (`106` tracked files).
  2026-04-22 result: no new file-level gap owners were isolated across the
  first secondary-source tranche; the refreshed function-count pass now
  lands on libjpeg macro definitions and splines C++ methods, while the
  retained BSPC toolchain, bundled `jpeg-6` sources, and legacy splines
  helpers remain bounded secondary support trees on current evidence.
- [x] Audit `src/game/`, `src/q3asm/`, and `src/q3map/` after the primary runtime surface is complete (`40` tracked files).
  2026-04-22 result: no new file-level gap owners were isolated across the
  second secondary-source tranche; the retained gameplay fixture helpers,
  `q3asm` bytecode assembler sources, and `q3map` compile/light/vis
  toolchain remain bounded secondary support trees on current evidence.
- [x] Audit `src/lcc/` and `src/libs/` after the primary runtime surface is complete (`99` tracked files).
  2026-04-22 result: no new file-level gap owners were isolated across the
  third secondary-source tranche; the retained LCC compiler/preprocessor,
  test fixtures, and tracked support-library sources under `src/libs`
  remain bounded secondary support trees on current evidence.
- [x] Audit `src/q3radiant/` after the primary runtime surface is complete (`97` tracked files).
  2026-04-22 result: no new file-level gap owners were isolated across the
  final secondary-source tranche; the retained Gtk/MFC-era Radiant editor,
  plugin bridge, OpenGL host glue, and bundled spline/editor helpers
  remain bounded secondary support trees on current evidence.

## Current seeded documented-divergence note set

- `RW-G01`: `src/common/platform/platform_config.h` -> `docs/reverse-engineering/source-file-gap-notes/rw-g01-platform-config.md`
- `RW-G01`: `src/common/platform/platform_services.c` -> `docs/reverse-engineering/source-file-gap-notes/rw-g01-platform-services.md`
- `RW-G01`: `src/common/platform/backends/platform_backend_open_steam.c` -> `docs/reverse-engineering/source-file-gap-notes/rw-g01-open-steam-backend.md`
- `RW-G01`: `src/common/platform/backends/platform_backend_steamworks.c` -> `docs/reverse-engineering/source-file-gap-notes/rw-g01-steamworks-backend.md`
- `RW-G01`: `src/code/client/ql_auth.c` -> `docs/reverse-engineering/source-file-gap-notes/rw-g01-client-auth.md`
- `RW-G01`: `src/code/client/cl_steam_resources.c` -> `docs/reverse-engineering/source-file-gap-notes/rw-g01-client-steam-resources.md`
- `RW-G01`: `src/code/server/sv_rankings.c` -> `docs/reverse-engineering/source-file-gap-notes/rw-g01-server-rankings.md`

## Current seeded active file-level gap set

- `RW-G02`: `src/code/unix/unix_main.c` -> `docs/reverse-engineering/source-file-gap-notes/rw-g02-unix-main.md`
- `RW-G02`: `src/code/unix/linux_glimp.c` -> `docs/reverse-engineering/source-file-gap-notes/rw-g02-linux-glimp.md`
- `RW-G02`: `src/code/unix/linux_snd.c` -> `docs/reverse-engineering/source-file-gap-notes/rw-g02-linux-snd.md`
- `RW-G02`: `src/code/unix/linux_joystick.c` -> `docs/reverse-engineering/source-file-gap-notes/rw-g02-linux-joystick.md`
- `RW-G02`: `src/code/null/null_main.c` -> `docs/reverse-engineering/source-file-gap-notes/rw-g02-null-main.md`
- `RW-G02`: `src/code/null/null_glimp.c` -> `docs/reverse-engineering/source-file-gap-notes/rw-g02-null-glimp.md`
- `RW-G02`: `src/code/null/null_client.c` -> `docs/reverse-engineering/source-file-gap-notes/rw-g02-null-client.md`
- `RW-G02`: `src/code/null/null_input.c` -> `docs/reverse-engineering/source-file-gap-notes/rw-g02-null-input.md`
- `RW-G02`: `src/code/null/null_snddma.c` -> `docs/reverse-engineering/source-file-gap-notes/rw-g02-null-snddma.md`

## Completion criteria

- Every tracked file in the ledger has been explicitly walked in the current campaign, not just inherited from an older subsystem closure note.
- Every file with a confirmed parity gap or documented divergence has its own dedicated note with a function-by-function status table and explicit closure conditions.
- `AUDIT.md` and the repo-wide audit remain concise summary ledgers instead of turning into file dumps.
