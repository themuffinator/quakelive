# Implementation Plan

Last updated: 2026-05-17

This file now tracks only active repo-level work. Detailed closure narratives
live in the dedicated subsystem audits under `docs/reverse-engineering/`.
Historical task headings that existing parity gates still check are preserved in
the appendix as compact archival anchors instead of repeated full narratives.

## Strategic goal

The long-term parity target remains the same: the reconstructed engine should,
in theory, be able to replace the retail Quake Live engine, load retail
`cgamex86.dll`, `qagamex86.dll`, and `uix86.dll`, present the retail main menu,
and interoperate with the retail Windows host/runtime contracts. Quake
Live-only online services remain behind `QL_BUILD_ONLINE_SERVICES`, default
disabled, until a documented open replacement path exists.

## Current planning baseline

- Treat `AUDIT.md` and
  `docs/reverse-engineering/repo-wide-parity-audit-2026-04-21.md` as the
  current cross-subsystem truth.
- Treat the 2026-04-10 engine-wide **100%** report as the strict-retail
  Windows closure milestone, not as a whole-repo all-green claim.
- The strict-retail Windows replacement target remains **100%** on the current
  worktree, but the current repo-wide parity estimate is **98%** once the
  compatibility-only and packaging-dependent surfaces are counted.
- The new file-by-file audit campaign now lives in
  `docs/reverse-engineering/source-file-parity-ledger-2026-04-22.md` and
  `docs/reverse-engineering/source-file-parity-audit-plan-2026-04-22.md`.
  It tracks `567` source entries, seeds concrete per-file notes for the
  documented `RW-G01` divergence owners plus the active `RW-G02` gap owners,
  and keeps the older
  subsystem ledgers as inherited baselines until each file is walked again.
- Top-level planning is reopened in this file because the 2026-04-21 repo-wide
  audit identified active gaps outside the strict-retail score.
- The older broad planning notes under `docs/parity-plan.md`,
  `docs/ui_deltas.md`, and `docs/ui_followup_issues.md` are historical
  snapshots, not current gap ledgers.

## Recent closure

### Task A7: Run the source-file parity audit campaign and isolate the remaining file-level gaps [COMPLETED]
Priority: High
Primary areas: `docs/reverse-engineering/source-file-parity-ledger-2026-04-22.md`,
`docs/reverse-engineering/source-file-parity-audit-plan-2026-04-22.md`,
`docs/reverse-engineering/source-file-gap-notes/`,
`tools/reverse-engineering/generate_source_file_audit.py`, all tracked
`src/` source trees
Parity estimate: **before 96% -> after 96%**

Completed work:

1. Closed the full source-file parity audit campaign by walking all `567`
   tracked source entries across the primary runtime, compatibility-only,
   and secondary support trees in the generated plan order.
2. Kept inherited subsystem closure as the baseline while isolating concrete
   file-level ownership only where the current evidence supported it, which
   left the repo-wide source-file gap register concentrated in the seeded
   `RW-G01` and `RW-G02` note set instead of reopening already-bounded
   surfaces.
3. Extended the source-file audit generator and its regression coverage so
   completed tranche metadata, compatibility wording, function-count fixes,
   and Phase 4 secondary-source summaries all survive regeneration on the
   current worktree.
4. Regenerated the source-file ledger, source-file audit plan, gap-note
   index/readme, and historical audit index so the campaign snapshot is now
   self-consistent and no pending tranche remains in the generated plan.
5. Returned the top-level queue to the remaining repo-wide workstreams, with
   the online-service compatibility boundary now back at the head of the
   active task list.

### Task A7p: Audit `src/q3radiant` function-by-function and isolate file-level gap ownership [COMPLETED]
Priority: High
Primary areas: `docs/reverse-engineering/source-file-parity-ledger-2026-04-22.md`,
`docs/reverse-engineering/source-file-parity-audit-plan-2026-04-22.md`,
`src/q3radiant/`,
`tests/test_source_file_audit_generator.py`,
`tools/reverse-engineering/generate_source_file_audit.py`
Parity estimate: **before 96% -> after 96%**

Completed work:

1. Completed the final Phase 4 secondary-source tranche in the source-file
   campaign by walking all `97` tracked files under `src/q3radiant`
   against the current generated ledger and the repo-wide parity register.
2. Confirmed that this tranche does not open any new file-level gap notes:
   the retained Radiant editor shell, plugin bridge, OpenGL host glue, and
   bundled spline/editor helper sources remain bounded secondary support
   trees on current evidence rather than concrete repo-wide gap owners.
3. Extended the source-file audit generator and its regression coverage so
   completed metadata for `src/q3radiant` and the checked final Phase 4
   plan item now survive regeneration too.
4. Re-ran the refreshed generator suite (`20 passed`) and regenerated the
   source-file campaign docs so the final Phase 4 tranche is now recorded
   as complete in the generated outputs.
5. Closed the currently enumerated secondary-source file-walk queue in the
   generated source-file audit plan, leaving no remaining pending Phase 4
   tranche in that campaign snapshot.

### Task A7o: Audit `src/lcc` and `src/libs` function-by-function and isolate file-level gap ownership [COMPLETED]
Priority: High
Primary areas: `docs/reverse-engineering/source-file-parity-ledger-2026-04-22.md`,
`docs/reverse-engineering/source-file-parity-audit-plan-2026-04-22.md`,
`src/lcc/`,
`src/libs/`,
`tests/test_source_file_audit_generator.py`,
`tools/reverse-engineering/generate_source_file_audit.py`
Parity estimate: **before 96% -> after 96%**

Completed work:

1. Completed the third Phase 4 secondary-source tranche in the source-file
   campaign by walking all `99` tracked files across `src/lcc` and
   `src/libs` against the current generated ledger and the repo-wide parity
   register.
2. Confirmed that this tranche does not open any new file-level gap notes:
   the retained LCC compiler/preprocessor/code-generator and bundled test
   sources under `src/lcc`, plus the tracked command-line, JPEG, and pak
   helper sources under `src/libs`, remain bounded secondary support trees
   on current evidence rather than concrete repo-wide gap owners.
3. Extended the source-file audit generator and its regression coverage so
   completed metadata for `src/lcc`, `src/libs`, and the checked third
   Phase 4 plan item now survive regeneration too.
4. Re-ran the refreshed generator suite (`19 passed`) and regenerated the
   source-file campaign docs so the third Phase 4 tranche is now recorded
   as complete in the generated outputs.
5. Advanced the file-walk queue so the remaining Phase 4 target is now the
   secondary-source tranche covering `src/q3radiant/`.

### Task A7n: Audit `src/game`, `src/q3asm`, and `src/q3map` function-by-function and isolate file-level gap ownership [COMPLETED]
Priority: High
Primary areas: `docs/reverse-engineering/source-file-parity-ledger-2026-04-22.md`,
`docs/reverse-engineering/source-file-parity-audit-plan-2026-04-22.md`,
`src/game/`,
`src/q3asm/`,
`src/q3map/`,
`tests/test_source_file_audit_generator.py`,
`tools/reverse-engineering/generate_source_file_audit.py`
Parity estimate: **before 96% -> after 96%**

Completed work:

1. Completed the second Phase 4 secondary-source tranche in the source-file
   campaign by walking all `40` tracked files across `src/game`,
   `src/q3asm`, and `src/q3map` against the current generated ledger and the
   repo-wide parity register.
2. Confirmed that this tranche does not open any new file-level gap notes:
   the retained gameplay config helpers and standalone fixture/support
   sources under `src/game`, the `q3asm` bytecode assembler sources, and the
   `q3map` compile/light/vis toolchain all remain bounded secondary support
   trees on current evidence rather than concrete repo-wide gap owners.
3. Extended the source-file audit generator and its regression coverage so
   completed metadata for `src/game`, `src/q3asm`, `src/q3map`, and the
   checked second Phase 4 plan item now survive regeneration too.
4. Re-ran the refreshed generator suite plus focused `src/game` helper
   coverage (`41 passed` across the source-audit, factory-config,
   scoreboard-helper, and tournament-queue suites) so this tranche stays
   recorded as complete on the current worktree.
5. Regenerated the source-file campaign docs so the second Phase 4 tranche is
   now recorded as complete in the generated outputs, and the next file-walk
   target is now the secondary-source tranche covering `src/lcc/` and
   `src/libs/`.

### Task A7m: Audit `src/code/bspc`, `src/code/jpeg-6`, and `src/code/splines` function-by-function and isolate file-level gap ownership [COMPLETED]
Priority: High
Primary areas: `docs/reverse-engineering/source-file-parity-ledger-2026-04-22.md`,
`docs/reverse-engineering/source-file-parity-audit-plan-2026-04-22.md`,
`src/code/bspc/`,
`src/code/jpeg-6/`,
`src/code/splines/`,
`tests/test_source_file_audit_generator.py`,
`tools/reverse-engineering/generate_source_file_audit.py`
Parity estimate: **before 96% -> after 96%**

Completed work:

1. Completed the first Phase 4 secondary-source tranche in the source-file
   campaign by walking all `106` tracked files across `src/code/bspc`,
   `src/code/jpeg-6`, and `src/code/splines` against the current repo-wide
   ledger and the generated source-file register.
2. Corrected the audit generator’s function extractor so the tranche now
   counts libjpeg macro-style definitions and retained splines C++ method
   definitions instead of leaving most of `jpeg-6` and parts of the splines
   tree as misleading zero-function placeholders in the ledger.
3. Confirmed that this tranche does not open any new file-level gap notes:
   the retained BSPC compiler/AAS toolchain, bundled `jpeg-6` support
   sources, and legacy splines helper/editor sources remain bounded
   secondary trees on current evidence rather than concrete repo-wide gap
   owners.
4. Extended the source-file audit generator and its regression coverage so
   completed secondary-section metadata and the checked first Phase 4 plan
   item now survive regeneration too; the refreshed generator suite passes
   on the current worktree (`17 passed`).
5. Regenerated the source-file campaign docs so the first Phase 4 tranche is
   now recorded as complete in the generated outputs, and the next file-walk
   target is now the secondary-source tranche covering `src/game/`,
   `src/q3asm/`, and `src/q3map/`.

### Task A7l: Audit `src/code/null` function-by-function and isolate file-level gap ownership [COMPLETED]
Priority: High
Primary areas: `docs/reverse-engineering/source-file-parity-ledger-2026-04-22.md`,
`docs/reverse-engineering/source-file-parity-audit-plan-2026-04-22.md`,
`docs/reverse-engineering/source-file-gap-notes/`,
`src/code/null/`,
`docs/reverse-engineering/repo-wide-parity-audit-2026-04-21.md`,
`tests/test_non_windows_portability.py`,
`tools/reverse-engineering/generate_source_file_audit.py`
Parity estimate: **before 96% -> after 96%**

Completed work:

1. Completed the next compatibility tranche in the source-file campaign by
   walking all `7` tracked `src/code/null` entries against the current
   repo-wide parity ledger, the existing `RW-G02` portability notes, and the
   focused non-Windows portability regression lane.
2. Isolated `src/code/null/null_glimp.c` as an additional concrete `RW-G02`
   owner because the null renderer host still consists of no-op
   `GLimp_*` entry points plus a `QGL_Init()` path that returns success
   without loading a real GL backend, while `null_main.c`, `null_client.c`,
   `null_input.c`, and `null_snddma.c` remain the other null-runtime owners
   already tracked in dedicated notes.
3. Confirmed that no further null file needs a new file-level gap note in
   this tranche: `null_net.c` and `mac_net.c` remain bounded loopback helper
   surfaces on current evidence rather than newly isolated repo-wide
   blockers, so they are now explicitly recorded as current compatibility
   function-walk completions.
4. Extended the source-file audit generator and its regression coverage so a
   completed null compatibility tranche, the newly isolated `null_glimp.c`
   note, and the walked-complete helper rows all survive regeneration; the
   refreshed generator plus non-Windows portability suites now pass
   together (`20 passed`).
5. Regenerated the source-file campaign docs so Phase 3 is now fully closed
   in the generated outputs, and the next file-walk target is now the first
   Phase 4 secondary-source tranche covering `src/code/bspc/`,
   `src/code/jpeg-6/`, and `src/code/splines/`.

### Task A7k: Audit `src/code/unix` function-by-function and isolate file-level gap ownership [COMPLETED]
Priority: High
Primary areas: `docs/reverse-engineering/source-file-parity-ledger-2026-04-22.md`,
`docs/reverse-engineering/source-file-parity-audit-plan-2026-04-22.md`,
`src/code/unix/`,
`docs/reverse-engineering/repo-wide-parity-audit-2026-04-21.md`,
`tests/test_non_windows_portability.py`,
`tools/reverse-engineering/generate_source_file_audit.py`
Parity estimate: **before 96% -> after 96%**

Completed work:

1. Completed the next compatibility tranche in the source-file campaign by
   walking all `10` tracked `src/code/unix` entries against the current
   repo-wide parity ledger, the existing `RW-G02` portability notes, and the
   focused non-Windows portability regression lane.
2. Confirmed that no additional `src/code/unix` file needs a new file-level
   gap note: the existing `RW-G02` ownership remains concentrated in
   `unix_main.c`, `linux_glimp.c`, `linux_snd.c`, and `linux_joystick.c`,
   while `linux_common.c`, `linux_qgl.c`, `linux_signals.c`, `unix_net.c`,
   `unix_shared.c`, and `vm_x86.c` are now explicitly recorded as current
   function-walk completions on present evidence.
3. Extended the source-file audit generator and its regression coverage so a
   completed compatibility tranche now survives regeneration too, including
   the checked Phase 3 Unix plan item, the compatibility-specific ledger row
   wording, and the retained `RW-G02` note ownership inside the still-open
   portability lane.
4. Re-ran the generator and the focused portability coverage (`18 passed`
   across the generator and non-Windows suites) so the Unix tranche now stays
   recorded as complete in the generated docs, and the next file-walk target
   is now the compatibility-only `src/code/null` tranche at the head of the
   remaining queue.

### Task A7j: Audit `src/code/ui` function-by-function and isolate file-level gap ownership [COMPLETED]
Priority: High
Primary areas: `docs/reverse-engineering/source-file-parity-ledger-2026-04-22.md`,
`docs/reverse-engineering/source-file-parity-audit-plan-2026-04-22.md`,
`src/code/ui/`,
`docs/reverse-engineering/ui-full-parity-audit-and-implementation-plan-2026-04-05.md`,
`tools/reverse-engineering/generate_source_file_audit.py`
Parity estimate: **before 96% -> after 96%**

Completed work:

1. Completed the next source-file campaign tranche by walking all `9`
   tracked `src/code/ui` entries against the refreshed strict-retail UI
   audit, the focused UI parity lane, and the current repo-wide gap ledger.
2. Confirmed that no `src/code/ui` file needs a new file-level gap note:
   the current UI closure still holds on current evidence, the focused UI
   suite is green (`56 passed`, `2 skipped`), the clean read-only `src/ui`
   runtime-panel parity proof still bounds the menu/data payload, and the
   read-only tree therefore did not require or permit a source correction in
   this tranche.
3. Extended the source-file audit generator and its regression coverage so
   completed read-only tranche metadata now survives regeneration too,
   including the UI checklist state, the read-only ledger row wording, and
   the UI tranche summary in the generated audit docs.
4. Regenerated the source-file campaign docs from the hardened generator so
   the UI tranche is now recorded as complete beside the earlier runtime
   walks, and the next file-walk target is now the compatibility-only
   `src/code/unix` tranche at the head of the remaining queue.

### Task A7i: Audit `src/code/cgame` function-by-function and isolate file-level gap ownership [COMPLETED]
Priority: High
Primary areas: `docs/reverse-engineering/source-file-parity-ledger-2026-04-22.md`,
`docs/reverse-engineering/source-file-parity-audit-plan-2026-04-22.md`,
`src/code/cgame/`,
`docs/reverse-engineering/game-module-parity-audit-and-implementation-plan-2026-04-10.md`,
`tools/reverse-engineering/generate_source_file_audit.py`
Parity estimate: **before 96% -> after 96%**

Completed work:

1. Completed the next module/gameplay tranche in the source-file campaign by
   walking all `22` tracked `src/code/cgame` entries against the refreshed
   strict-retail module audit, the focused `cgame` parity lane, and the
   current repo-wide gap ledger.
2. Confirmed that no `src/code/cgame` file needs a new file-level gap note:
   the current module closure still holds on current evidence, the focused
   `cgame` suite is green (`199 passed`, `1 skipped`), and the shared native
   export-helper certification still bounds the tree without needing a source
   correction in this tranche.
3. Hardened the source-file audit generator so completed tranche checkmarks,
   section result notes, and current-walk ledger rows now survive regeneration
   instead of reverting already-audited runtime sections back to the default
   pending wording; `--help` is also now a safe no-write path.
4. Regenerated the source-file campaign docs from the hardened generator so
   the corrected `cgame` function counts and the previously completed runtime
   tranches live in one durable output again, and the next file-walk target
   is now the read-only `src/code/ui` tranche at the head of the remaining
   module/gameplay queue.

### Task A7h: Audit `src/code/game` function-by-function and isolate file-level gap ownership [COMPLETED]
Priority: High
Primary areas: `docs/reverse-engineering/source-file-parity-ledger-2026-04-22.md`,
`docs/reverse-engineering/source-file-parity-audit-plan-2026-04-22.md`,
`src/code/game/`,
`docs/reverse-engineering/game-module-parity-audit-and-implementation-plan-2026-04-10.md`,
`tools/reverse-engineering/generate_source_file_audit.py`
Parity estimate: **before 96% -> after 96%**

Completed work:

1. Hardened the source-file audit generator again so it now ignores
   control-flow keywords such as `if`, `for`, `while`, and `switch`, which
   keeps the source-file campaign counts aligned with real Quake-style C
   definitions in the `src/code/game` tranche instead of overcounting
   control blocks.
2. Completed the next module/gameplay tranche in the source-file campaign by
   walking all `45` tracked `src/code/game` entries against the refreshed
   strict-retail module audit, the qagame retail gate, and the current
   repo-wide gap ledger.
3. Closed the concrete issues surfaced during the walk without opening a new
   persistent gap note: `BG_CanGrabWeaponItem()` now matches the retained
   retail world-weapon regrab gate, the Attack & Defend lifecycle/frame hooks
   are explicit in the module-side source layout again, and the standalone
   auto-shuffle countdown harness now uses the shared compiler-discovery path
   on Windows instead of assuming `gcc`.
4. Confirmed that no `src/code/game` file needs a new file-level gap note:
   the current gameplay/module closure still holds on current evidence, and
   the newer auto-shuffle/countdown, Clan Arena shuffle, Race, ready-up, and
   shared `pmove` coverage all remain bounded inside the already-closed
   module register rather than opening a new repo-wide gap family.
5. Recorded the result directly in the source-file campaign docs so the game
   rows now distinguish current function-walk completion from the
   still-pending module trees, and the next file-walk target is now the
   `src/code/cgame` tranche at the head of the remaining module/gameplay
   queue.

### Task A7g: Audit `src/code/botlib` function-by-function and isolate file-level gap ownership [COMPLETED]
Priority: High
Primary areas: `docs/reverse-engineering/source-file-parity-ledger-2026-04-22.md`,
`docs/reverse-engineering/source-file-parity-audit-plan-2026-04-22.md`,
`src/code/botlib/`,
`docs/reverse-engineering/botlib-internal-parity-audit-and-implementation-plan-2026-04-10.md`,
`tools/reverse-engineering/generate_source_file_audit.py`
Parity estimate: **before 96% -> after 96%**

Completed work:

1. Fixed the source-file audit generator so it now counts Quake-style
   brace-on-next-line C function definitions, which restores accurate
   function-count coverage for the `src/code/botlib` tranche instead of
   leaving most files reported as zero-function placeholders.
2. Completed the next primary-runtime tranche in the source-file campaign by
   walking all `28` tracked `src/code/botlib` entries against the dedicated
   botlib internal audit, the retained mapping-round `61` bridge/import
   ownership, and the current repo-wide gap ledger.
3. Confirmed that no `src/code/botlib` file needs a new file-level gap note:
   the retained bridge/import closures and the deterministic
   AAS/reachability/goal-state proof lane still bound the tree on current
   evidence, while the remaining live-map or gameplay-tuning nuance stays
   explicitly outside the repo-wide/file-level gap register.
4. Recorded the result directly in the source-file campaign docs so the
   botlib rows now distinguish current function-walk completion from the
   still-pending module and compatibility trees, and the next file-walk
   target is now the `src/code/game` tranche at the head of the remaining
   module/gameplay queue.

### Task A7f: Audit `src/code/win32` function-by-function and isolate file-level gap ownership [COMPLETED]
Priority: High
Primary areas: `docs/reverse-engineering/source-file-parity-ledger-2026-04-22.md`,
`docs/reverse-engineering/source-file-parity-audit-plan-2026-04-22.md`,
`src/code/win32/`,
`docs/reverse-engineering/platform-specific-engine-parity-audit-and-implementation-plan-2026-04-16.md`
Parity estimate: **before 96% -> after 96%**

Completed work:

1. Completed the next primary-runtime tranche in the source-file campaign by
   walking all `11` tracked `src/code/win32` entries against the closed
   strict-retail Windows platform audit, renderer host-glue evidence, and the
   current repo-wide gap ledger.
2. Confirmed that no `src/code/win32` file needs a new file-level gap note:
   the retained clipboard, raw-input, loading-window, renderer-host glue, and
   `win_glimp.c` pixel-format closures still hold on current evidence, and no
   file in this tree currently owns a repo-wide gap family.
3. Recorded the result directly in the source-file campaign docs so the
   Win32 rows now distinguish current function-walk completion from the
   still-pending runtime trees, without reopening the closed strict-retail
   Windows platform register.
4. Narrowed `A7` procedurally again: the next file-walk target is now the
   `src/code/botlib` tranche at the head of the remaining strict-retail
   engine-core queue.

### Task A7e: Audit `src/code/renderer` function-by-function and isolate file-level gap ownership [COMPLETED]
Priority: High
Primary areas: `docs/reverse-engineering/source-file-parity-ledger-2026-04-22.md`,
`docs/reverse-engineering/source-file-parity-audit-plan-2026-04-22.md`,
`src/code/renderer/`,
`docs/reverse-engineering/renderer-full-parity-audit-and-implementation-plan-2026-04-09.md`
Parity estimate: **before 96% -> after 96%**

Completed work:

1. Completed the next primary-runtime tranche in the source-file campaign by
   walking all `23` tracked `src/code/renderer` entries against the closed
   strict-retail renderer audit, mapping notes, and the current repo-wide
   gap ledger.
2. Confirmed that no `src/code/renderer` file needs a new file-level gap note:
   the retained export, image, post-process, scene/runtime, font, and
   host-text closures still hold on current evidence, and the bounded
   `R_fonsErrorCallback` module-runtime blocker remains classified under
   `RW-G04` evidence freshness rather than as a new renderer source-gap
   owner.
3. Recorded the result directly in the source-file campaign docs so the
   renderer rows now distinguish current function-walk completion from the
   still-pending runtime trees, without reopening the closed strict-retail
   renderer register.
4. Narrowed `A7` procedurally again: the next file-walk target is now the
   `src/code/win32` tranche at the head of the remaining strict-retail
   engine-core queue.

### Task A7d: Audit `src/code/server` function-by-function and isolate file-level gap ownership [COMPLETED]
Priority: High
Primary areas: `docs/reverse-engineering/source-file-parity-ledger-2026-04-22.md`,
`docs/reverse-engineering/source-file-parity-audit-plan-2026-04-22.md`,
`src/code/server/`,
`docs/reverse-engineering/server-full-parity-audit-and-implementation-plan-2026-04-10.md`
Parity estimate: **before 96% -> after 96%**

Completed work:

1. Completed the next primary-runtime tranche in the source-file campaign by
   walking all `11` tracked `src/code/server` entries against the closed
   strict-retail server audit, mapping notes, and the current repo-wide
   gap ledger.
2. Confirmed that no new `src/code/server` file-level owners need opening
   beyond the already-seeded `RW-G01` note for `sv_rankings.c`; the retained
   Steam GameServer/auth/stats and `idZMQ` publication/runtime owners remain
   closed on current evidence.
3. Recorded the result directly in the source-file campaign docs so the
   server rows now distinguish current function-walk completion from the
   still-pending runtime trees, while keeping the bounded rankings ownership
   explicit in the existing `sv_rankings.c` gap note instead of reopening the
   closed strict-retail server register.
4. Narrowed `A7` procedurally again: the next file-walk target is now the
   `src/code/renderer` tranche at the head of the remaining strict-retail
   engine-core queue.

### Task A7c: Audit `src/code/client` function-by-function and isolate file-level gap ownership [COMPLETED]
Priority: High
Primary areas: `docs/reverse-engineering/source-file-parity-ledger-2026-04-22.md`,
`docs/reverse-engineering/source-file-parity-audit-plan-2026-04-22.md`,
`src/code/client/`,
`docs/reverse-engineering/client-full-parity-audit-and-implementation-plan-2026-04-09.md`
Parity estimate: **before 96% -> after 96%**

Completed work:

1. Completed the next primary-runtime tranche in the source-file campaign by
   walking all `22` tracked `src/code/client` entries against the closed
   strict-retail client audit, mapping notes, and the current repo-wide
   gap ledger.
2. Confirmed that no new `src/code/client` file-level owners need opening
   beyond the already-seeded `RW-G01` notes for `ql_auth.c` and
   `cl_steam_resources.c`.
3. Recorded the result directly in the source-file campaign docs so the
   client rows now distinguish current function-walk completion from the
   still-pending runtime trees, while keeping the bounded online-services
   ownership explicit in the two existing client gap notes instead of
   reopening the closed strict-retail client register.
4. Narrowed `A7` procedurally again: the next file-walk target is now the
   `src/code/server` tranche at the head of the remaining strict-retail
   engine-core queue.

### Task A7b: Audit `src/code/qcommon` function-by-function and isolate file-level gap ownership [COMPLETED]
Priority: High
Primary areas: `docs/reverse-engineering/source-file-parity-ledger-2026-04-22.md`,
`docs/reverse-engineering/source-file-parity-audit-plan-2026-04-22.md`,
`src/code/qcommon/`,
`docs/reverse-engineering/qcommon-full-parity-audit-and-implementation-plan-2026-04-10.md`
Parity estimate: **before 96% -> after 96%**

Completed work:

1. Completed the next primary-runtime tranche in the source-file campaign by
   walking all `19` tracked `src/code/qcommon` entries against the closed
   strict-retail qcommon audit, mapping rounds, and the current repo-wide
   ledger.
2. Confirmed that no new `src/code/qcommon` file-level owners need opening:
   the current strict-retail qcommon register remains closed, and no
   additional repo-wide gap family is concretely owned by a qcommon source
   file on the current worktree.
3. Recorded the result directly in the source-file campaign docs so the
   qcommon rows now distinguish current function-walk completion from the
   still-pending runtime trees, while keeping `vm_x86.c` classified as the
   already-bounded compatibility carry beneath the closed `vm.c`
   host-selection seam.
4. Narrowed `A7` procedurally again: the next file-walk target is now the
   `src/code/client` tranche at the head of the remaining strict-retail
   engine-core queue.

### Task A7a: Audit `src/common` function-by-function and isolate file-level gap ownership [COMPLETED]
Priority: High
Primary areas: `docs/reverse-engineering/source-file-parity-ledger-2026-04-22.md`,
`docs/reverse-engineering/source-file-parity-audit-plan-2026-04-22.md`,
`src/common/`, `src/common/platform/`
Parity estimate: **before 96% -> after 96%**

Completed work:

1. Completed the first primary-runtime tranche in the new source-file campaign
   by walking all `18` tracked `src/common` entries against the current
   engine-wide closure and repo-wide gap ledgers.
2. Confirmed that no new `src/common` file-level owners need opening beyond
   the already-seeded `RW-G01` notes for `platform_config.h`,
   `platform_services.c`, and the bounded auth backend shims.
3. Recorded the result directly in the source-file campaign docs so the
   `src/common` rows now distinguish current function-walk completion from the
   still-pending primary-runtime trees, while keeping `platform_steamworks.c`
   classified as a retained Steamworks wrapper surface gated by policy rather
   than as a newly opened repo-wide gap owner.
4. Narrowed `A7` procedurally: the next file-walk target is now the
   `src/code/qcommon` tranche at the head of the remaining strict-retail
   engine-core queue.

### Task A4i: Replace the Unix `Sys_CheckCD()` unconditional pass with a bounded data-root probe [COMPLETED]
Priority: Medium
Primary areas: `src/code/unix/unix_main.c`,
`tests/test_non_windows_portability.py`,
`docs/platform/toolchain-matrix.md`, `docs/build/linux-glibc-32bit.md`
Parity estimate: **before 96% -> after 96%**

Completed work:

1. Replaced the Unix `Sys_CheckCD()` `return qtrue;` placeholder with a
   bounded Quake-data probe that now scans the configured `fs_basepath`,
   `fs_cdpath`, default install roots, and current working directory for
   `baseq3/default.cfg`, `pak00.pk3`, or `pak0.pk3` before reporting success.
2. Kept the reconstructed lane deliberately compatibility-scoped rather than
   over-claiming retail parity: the probe is a coarse host-side data-root
   guard for existing engine callers such as `SV_BotInitBotLib()`, not a full
   filesystem bootstrap replacement.
3. Expanded the focused non-Windows portability suite so the new root list,
   accepted asset markers, and `baseq3` path contract are source-pinned
   alongside the previously restored low-memory, symbol-compare, release-marker,
   profiling, and clipboard seams.
4. Narrowed `RW-G02` again: the remaining portability debt is now even more
   cleanly concentrated in the absent real Unix renderer/audio/input host
   modernization and broader non-Windows validation breadth, not in an
   unconditional Unix content-root success stub.

### Task A4h: Restore a bounded Unix clipboard compatibility path [COMPLETED]
Priority: Medium
Primary areas: `src/code/unix/unix_main.c`,
`tests/test_non_windows_portability.py`,
`docs/platform/toolchain-matrix.md`, `docs/build/linux-glibc-32bit.md`
Parity estimate: **before 96% -> after 96%**

Completed work:

1. Replaced the bare Unix `Sys_GetClipboardData()` `NULL` stub with a bounded
   compatibility path that now reads clipboard text through `wl-paste`,
   `xclip`, or `xsel` when the surrounding Wayland/X11 environment and helper
   binaries are available, while still returning `NULL` cleanly on unsupported
   hosts.
2. Bounded the new lane explicitly so it mirrors the existing host contract
   instead of over-claiming parity: clipboard text is trimmed at the first
   newline/control break, capped to a fixed maximum size, and copied into the
   engine allocator before it reaches the existing client, UI, and browser
   clipboard consumers.
3. Expanded the focused non-Windows portability suite so the Unix clipboard
   probe chain, PATH lookup, command gating, and Wayland/X11 fallback order
   are source-pinned alongside the earlier low-memory, symbol-compare,
   monkey-marker, profiling, and null-runtime compatibility seams.
4. Narrowed `RW-G02` again: the remaining portability debt is now even more
   clearly in the missing real Unix renderer/audio/input host modernization
   and broader non-Windows validation breadth, not in an unimplemented Unix
   clipboard host hook.

### Task A2c: Refresh the repo-wide parity audit evidence on the current worktree [COMPLETED]
Priority: Medium
Primary areas: `AUDIT.md`, `IMPLEMENTATION_PLAN.md`,
`docs/reverse-engineering/repo-wide-parity-audit-2026-04-21.md`
Parity estimate: **before 96% -> after 96%**

Completed work:

1. Re-ran a broad current-worktree parity sweep across the top-level
   strict-retail gates, gameplay validation fixtures, portability suite, and
   staged runtime-audit lane, producing `72 passed, 7 skipped`.
2. Rebased the top-level ledgers on that sweep so the current repo-wide gap
   register is explicitly backed by one aggregated evidence pass instead of
   only by the individual runtime-probe refresh notes.
3. Clarified that the remaining repo-wide gap families still collapse to
   `RW-G01`, `RW-G02`, and `RW-G04`, with the staged retail-runtime DLL guard
   now treated as closed and the remaining `RW-G04` debt narrowed to fresh
   artifact regeneration/publication.
4. Cleaned up stale date language in the historical top-level audit anchors so
   the repo-wide ledgers no longer point readers at the older `2026-04-17`
   top-level state while describing the current 2026-04-21 worktree.

### Task A6f: Add a strict staged retail-runtime DLL audit for native Windows validation [COMPLETED]
Priority: Medium
Primary areas: `tools/ci/audit-retail-dependencies.ps1`,
`tools/ci/validate-windows-native.ps1`, Windows/toolchain docs
Parity estimate: **before 96% -> after 96%**

Completed work:

1. Extended the retail dependency auditor so it can now audit either the local
   Steam install or an explicit runtime root, checking for missing expected
   retail DLLs, extra non-retail DLLs, and byte-hash mismatches instead of
   only diffing the Steam tree opportunistically.
2. Added a strict retail-runtime staging step to
   `tools/ci/validate-windows-native.ps1`: the retail validation lane now
   assembles `build\win32\<Config>\retail-runtime\` from the rebuilt host
   executables and gameplay/UI DLLs plus the exact retail launcher DLL payload
   from `assets\quakelive\`, then fails fast if the staged root contains extra
   DLLs or is missing any retail payload DLLs.
3. Rebased the Windows/toolchain documentation on that explicit staging
   boundary so the mixed developer build root `build\win32\<Config>\bin\` is
   no longer described as the strict retail payload surface.
4. Narrowed `RW-G04` again: the remaining freshness debt is now no longer the
   previously documented local/runtime DLL-guard follow-up, and is instead
   concentrated in refreshed native build outputs plus the broader glibc and
   self-hosted publication follow-ups.

### Task A6e: Re-promote the retail module runtime alias through an explicit renderer-text bounded blocker [COMPLETED]
Priority: Medium
Primary areas: `tools/modules/run_retail_module_runtime_probe.ps1`,
`tests/test_game_module_retail_parity_gate.py`, runtime-evidence ledgers
Parity estimate: **before 96% -> after 96%**

Completed work:

1. Expanded the retail-module probe's bounded-owner classification so the
   current 2026-04-21 rerun can distinguish two renderer-owned live-map
   blocker shapes outside module scope: the older fatal `R_LoadMD3` drop path
   and the current `R_fonsErrorCallback` font-atlas saturation lane that keeps
   retail `uix86.dll`, `cgamex86.dll`, and `qagamex86.dll` loaded but prevents
   `CS_ACTIVE`.
2. Rebased the module runtime probe on the current map-launch contract again by
   threading the same `com_maxfps 30` / no-warmup assumptions used by the
   other runtime probes into the retail-module lane, while keeping the stable
   alias guarded so only sufficient reruns are promoted.
3. Reran `tools/modules/run_retail_module_runtime_probe.ps1` on 2026-04-21 and
   refreshed
   `artifacts/module_validation/logs/retail_module_runtime_evidence_latest.json`
   to the current bounded `20260421` bundle instead of leaving it pinned to
   the older `2026-04-09` artifact.
4. Narrowed `RW-G04` again: the remaining freshness debt is now no longer a
   non-promotable retail-module alias question, and is instead concentrated in
   fresh native build outputs plus the broader glibc/self-hosted publication
   follow-ups.

### Task A4g: Restore a bounded Unix profiling control path [COMPLETED]
Priority: Medium
Primary areas: `src/code/unix/unix_main.c`,
`src/code/unix/Makefile`, `tests/test_non_windows_portability.py`,
portability ledgers
Parity estimate: **before 96% -> after 96%**

Completed work:

1. Replaced the empty Unix profiling hooks with a bounded `gprof`-compatible
   runtime path: `Sys_Init()` now pauses profiling early when `moncontrol` is
   available, `Sys_BeginProfiling()` re-enables it on first active play, and
   `Sys_Exit()` now flushes `_mcleanup()` through `Sys_EndProfiling()`.
2. Added an explicit Unix build toggle `QL_ENABLE_GPROF=1` so profiling is a
   reproducible opt-in lane rather than an undocumented linker accident. The
   Unix makefile now threads `-pg` through the relevant engine compile/link
   paths when that toggle is enabled.
3. Rebased the focused non-Windows portability checks and ledgers so they now
   record a bounded profiling lane instead of an empty Unix no-op while still
   keeping the broader Unix renderer/audio/input host gap open.
4. Narrowed `RW-G02` again: the remaining portability debt is now even more
   clearly in the modern Unix runtime boundary itself, not in stale host-side
   syscall placeholders.

### Task A6d: Refresh renderer runtime evidence and stabilize alias promotion for the renderer/module probes [COMPLETED]
Priority: Medium
Primary areas: `tools/renderer/run_renderer_runtime_probe.ps1`,
`tools/modules/run_retail_module_runtime_probe.ps1`,
`tests/test_renderer_full_parity_gate.py`,
`tests/test_renderer_text_runtime_validation_parity.py`,
`tests/test_game_module_retail_parity_gate.py`, runtime-evidence docs
Parity estimate: **before 96% -> after 96%**

Completed work:

1. Repaired the renderer runtime probe contract so the current `map <name>
   ffa` path, quoted launch arguments, and normalized path handling work
   reliably again, then reran the probe on 2026-04-21 to refresh the clean
   dated bundle
   `artifacts/renderer_validation/logs/renderer_runtime_evidence_20260421.json`.
2. Added guarded `*_latest.json` promotion to both the renderer and retail
   module probes so only sufficient reruns replace the stable tracked alias.
   The renderer alias now points at the clean 2026-04-21 bundle, and the
   retail-module lane gained the guarded promotion rules that later enabled
   `A6e` to refresh the stable alias to the current bounded `2026-04-21`
   module artifact instead of silently accepting degraded reruns.
3. Rebased the renderer/module parity gates, the font audit script, and the
   active runtime-evidence docs on those stable aliases plus the current
   `map <name> ffa` launch contract.
4. Narrowed `RW-G04` again: the remaining freshness debt is now concentrated
   in fresh native build outputs and the broader glibc/self-hosted publication
   follow-ups.

### Task A4f: Classify the Linux glibc preset as server-only portability evidence [COMPLETED]
Priority: Medium
Primary areas: `docs/build/linux-glibc-32bit.md`,
`docs/platform/toolchain-matrix.md`,
`tests/test_non_windows_portability.py`, portability ledgers
Parity estimate: **before 96% -> after 96%**

Completed work:

1. Updated `docs/build/linux-glibc-32bit.md` so the helper is explicitly
   framed as a `qagamei386.so` server-module reconstruction preset rather than
   as evidence of a retail-equivalent Linux client/runtime.
2. Mirrored that portability boundary in the native toolchain matrix so the
   top-level Linux lane description now points contributors at the correct
   server-only interpretation immediately.
3. Expanded the focused non-Windows portability regression coverage so the
   server-module-only classification and the still-open Unix profiling or
   renderer/audio/input host gaps are pinned in the docs.
4. Narrowed `RW-G02` procedurally: the remaining work is now more cleanly
   about whether to modernise the real Unix host boundary, not about what the
   existing Linux build helper is supposed to prove.

### Task A4e: Modernise the null input compatibility contract [COMPLETED]
Priority: Medium
Primary areas: `src/code/null/null_input.c`,
`tests/test_non_windows_portability.py`,
`tests/test_engine_host_support_full_parity_gate.py`, portability ledgers
Parity estimate: **before 95% -> after 96%**

Completed work:

1. Modernised `src/code/null/null_input.c` so the dedicated/null host now
   carries the current input bootstrap cvars (`in_mouse`, `in_nograb`,
   `in_joystick`, `in_debugjoystick`, and `joy_threshold`) plus an explicit
   compatibility-state refresh that keeps `ui_joyavail` pinned to `0`
   instead of leaving the file as a bare inert no-op.
2. Reconstructed the null input frame pump as an explicit no-device contract:
   `IN_Frame()` now maintains the compatibility cvar surface and consumes
   joystick modification latches, while `Sys_SendKeyEvents()` now refreshes
   the same no-device state without emitting real input events.
3. Expanded both the focused non-Windows portability suite and the
   engine-host/support compatibility gate so the current null input lane is
   pinned alongside the earlier null host/client/audio modernization work.
4. Narrowed `RW-G02` again: the remaining portability debt is now
   concentrated even more tightly in the Unix profiling placeholders and the
   absence of a real modern Unix client/renderer/audio/input host, rather
   than in stale null input bootstrap/event-pump seams.

### Task A4d: Modernise the null client/audio compatibility contracts [COMPLETED]
Priority: Medium
Primary areas: `src/code/null/null_client.c`,
`src/code/null/null_snddma.c`, `tests/test_non_windows_portability.py`,
portability ledgers
Parity estimate: **before 94% -> after 95%**

Completed work:

1. Modernised `src/code/null/null_client.c` so the null compatibility lane now
   exposes the current browser/advert/input-facing `client.h` contract instead
   of only the older partial web-host shim set: the null client now carries
   `CL_RefreshOnlineServicesBridgeState()`, the current browser cursor and app
   activation hooks, mouse/button/wheel webview input stubs, and the retained
   advertisement-bridge entry points while explicitly forcing the browser
   cvars back to the non-live state.
2. Promoted `src/code/null/null_snddma.c` from a narrow legacy dummy into an
   explicit current silent-audio compatibility seam by adding the current
   `SNDDMA_Activate()` and `S_AddVoiceSamples()` entry points alongside the
   existing null DMA and local-sound hooks.
3. Expanded the focused non-Windows portability regression coverage so it now
   asserts the current null client/audio contract surfaces directly instead of
   only pinning the older null host/network/glimp tranche.
4. Narrowed `RW-G02` again: the remaining non-Windows debt is now
   concentrated in the profiling hooks plus the absence of a real modern Unix
   client/renderer/audio/input host, rather than in stale or missing null
   browser/advert/audio contract entry points.

### Task A4c: Modernise the null host contracts and reconstruct the Unix monkey-marker hook [COMPLETED]
Priority: Medium
Primary areas: `src/code/unix/unix_main.c`, `src/code/null/null_main.c`,
`src/code/null/null_net.c`, `src/code/null/mac_net.c`,
`src/code/null/null_glimp.c`, `tests/test_non_windows_portability.py`,
portability ledgers
Parity estimate: **before 93% -> after 94%**

Completed work:

1. Reconstructed the Unix `Sys_MonkeyShouldBeSpanked()` compatibility hook as
   a retained `q3monkeyid` release-marker probe rooted in the historical
   `Construct` script plus the committed retail string corpus, instead of
   leaving it as an unconditional placeholder.
2. Modernised the stale null host shims so they now match the current
   `qcommon` contracts: `null_main.c` now carries current command-line,
   executable-name, timer, path, and homepath scaffolding; `null_net.c` and
   `mac_net.c` now expose `Sys_StringToAdr()` plus the current loopback packet
   stub signatures; and `null_glimp.c` no longer carries the stale `int
   GLimp_Init()` signature.
3. Added focused non-Windows portability coverage for the new Unix marker
   probe and the null-host contract cleanup.
4. Narrowed `RW-G02` again: the remaining open portability debt is now
   concentrated in the profiling hooks plus the broader Unix/client/audio/input
   and still-stubbed null runtime surfaces, rather than in stale host-contract
   mismatches or the old `q3monkeyid` placeholder.

### Task A6c: Refresh the qcommon, server, and WOW64 evidence contracts on the current machine [COMPLETED]
Priority: Medium
Primary areas: `tools/qcommon/run_qcommon_runtime_probe.ps1`,
`tools/server/run_server_runtime_probe.ps1`,
`tools/ci/wow64-smoketest.ps1`,
their tracked artifacts, and repo-wide validation ledgers
Parity estimate: **before 93% -> after 93%**

Completed work:

1. Repaired the stale qcommon and dedicated-server probe contracts so both
   runtime lanes now use the current `map <name> ffa` command shape, then
   re-ran them on 2026-04-21 to refresh
   `artifacts/qcommon_validation/logs/qcommon_runtime_evidence_20260410.json`
   and
   `artifacts/server_validation/logs/server_runtime_evidence_20260410.json`.
2. Rebased the qcommon and server gate/documentation expectations on the
   current runtime markers, including the qcommon `game.error` plus native
   `stopRefresh` fallback evidence and the current dedicated `getstatus`
   server-type field spelling.
3. Updated the retained WOW64 smoke harness so it now prefers retail DLLs from
   `assets/quakelive/baseq3/` when present but falls back to the current
   Win32 build outputs under `build/win32/Debug/bin/baseq3/`, then captured a
   successful 32-bit PowerShell run at
   `artifacts/wow64-smoketest/wow64-smoketest.log`.
4. Narrowed `RW-G04` again: the remaining freshness debt is now concentrated
   in fresh native build outputs, the still-archived runtime bundles outside
   the refreshed client/qcommon/server lanes, and the broader glibc or
   self-hosted validation publication follow-ups.

### Task A4b: Restore bounded Unix function compare/checksum coverage on the compatibility host lane [COMPLETED]
Priority: Medium
Primary areas: `src/code/unix/unix_main.c`,
`tests/test_non_windows_portability.py`, `docs/platform/toolchain-matrix.md`,
top-level portability ledgers
Parity estimate: **before 93% -> after 93%**

Completed work:

1. Restored Unix `Sys_FunctionCmp()` and `Sys_FunctionCheckSum()` with a
   Linux/glibc symbol-backed path that resolves function byte ranges through
   `dladdr1(..., RTLD_DL_SYMENT)` and hashes them with
   `Com_BlockChecksum()` when symbol sizes are available.
2. Added focused portability coverage that now checks the new source-side
   helper path directly instead of only tracking the old placeholder story in
   documentation.
3. Narrowed `RW-G02` again: the remaining open Unix helper debt is now
   concentrated in the historical profiling lane plus the broader
   non-Windows client/audio/input/toolchain boundary.

### Task A6b: Re-baseline the `src/ui` runtime-panel contract to the clean current state [COMPLETED]
Priority: Medium
Primary areas: `tests/test_ui_src_panel_parity.py`,
`tests/test_ui_full_parity_gate.py`, `docs/quakelive_asset_audit.md`,
`docs/ui/hud-audit.md`, `docs/ui/scripting-guide.md`, top-level ledgers
Parity estimate: **before 93% -> after 93%**

Completed work:

1. Tightened the repo/UI parity gates so the current worktree now expects the
   `src/ui` runtime-panel compare to be clean (`65 / 65`, `0` content diffs)
   instead of tolerating the older historical non-zero drift contract.
2. Re-based the UI documentation and the repo-wide ledgers so they now
   distinguish clean checked-in runtime-panel parity from the separate
   bundle-staged retail art path.
3. Documented that explicit runtime-root refreshes always write the runtime
   package manifest, but only emit `pak_ui_src_retail_overlay.pk3` when
   `drift_files` is non-empty.

### Task A6a: Refresh the tracked client runtime evidence bundle after UI package-proof hardening [COMPLETED]
Priority: Medium
Primary areas: `tools/client/run_client_runtime_probe.ps1`,
`tests/test_client_full_parity_gate.py`,
`artifacts/client_validation/logs/client_runtime_evidence_20260410.json`,
client/runtime audit docs
Parity estimate: **before 93% -> after 93%**

Completed work:

1. Tightened the client parity gate so the tracked runtime bundle must now
   prove the emitted UI runtime-package manifest plus the refreshed main
   package hashes instead of relying only on the older screenshot/log bundle.
2. Rebased the main-menu offline-browser proof on the current retained runtime
   behavior, using the observed `game.error` publication and UI-side
   `stopRefresh` fallback markers instead of the older stale probe
   expectations.
3. Re-ran `tools/client/run_client_runtime_probe.ps1` on 2026-04-21 and
   refreshed `artifacts/client_validation/logs/client_runtime_evidence_20260410.json`
   with fresh screenshots, logs, demo output, and UI package evidence.
4. Narrowed `RW-G04` by refreshing the client runtime bundle while leaving the
   remaining archived runtime/build artifacts as the still-open repo-wide
   freshness debt.

### Task A5: Harden the read-only `src/ui` parity path with runtime package proof [COMPLETED]
Priority: High
Primary areas: `tools/build_ui_bundle.py`, `tests/test_ui_src_panel_parity.py`,
`tools/client/run_client_runtime_probe.ps1`, `docs/quakelive_asset_audit.md`,
`docs/ui/hud-audit.md`, `docs/ui/scripting-guide.md`
Parity estimate: **before 92% -> after 93%**

Completed work:

1. Added an explicit runtime-package manifest to `tools/build_ui_bundle.py`
   for `--runtime-root` runs so emitted `pak_uiql.pk3` and
   `pak_ui_src_retail_overlay.pk3` outputs are now machine-described instead
   of assumed from console output alone.
2. Added focused UI bundle coverage that proves the explicit runtime-root path
   emits the expected PK3s, includes the required runtime entries and
   compatibility aliases, and keeps any emitted overlay package in lockstep
   with the source-vs-retail drift contract.
3. Tightened the client runtime probe so it now verifies the refreshed runtime
   package manifest and fails fast if the required UI runtime package was not
   emitted into the writable homepath.
4. Refreshed the UI packaging docs so they consistently describe the current
   contract: staging/overlay manifests by default, explicit package emission
   only for runtime-root refreshes or probe flows, with the overlay PK3
   remaining optional when the drift contract is empty.

### Task A4a: Restore Unix low-memory detection on the compatibility host lane [COMPLETED]
Priority: Medium
Primary areas: `src/code/unix/unix_main.c`, `docs/platform/toolchain-matrix.md`
Parity estimate: **before 92% -> after 92%**

Completed work:

1. Replaced the unconditional Unix `Sys_LowPhysicalMemory()` placeholder with
   a native `sysconf()`-backed physical page-count query so the renderer/cgame
   low-memory heuristic no longer hardcodes the non-low-memory path on Unix.
2. Refreshed the platform note so it now records the restored low-memory
   probe separately from the still-bounded checksum/comparison/profiling
   helpers.
3. Narrowed the active `RW-G02` description to the remaining portability debt
   instead of continuing to list `Sys_LowPhysicalMemory()` as an unresolved
   placeholder.

### Task A2: Repo-wide parity re-baseline and documentation convergence [COMPLETED]
Priority: Critical
Primary areas: `AUDIT.md`, `IMPLEMENTATION_PLAN.md`,
`docs/reverse-engineering/repo-wide-parity-audit-2026-04-21.md`,
`docs/parity-plan.md`, `docs/ui_deltas.md`, `docs/ui_followup_issues.md`,
`docs/quakelive_asset_audit.md`
Parity estimate: **before 92% -> after 92%**

Completed work:

1. Re-ran the repo's top-level parity-gate suites on 2026-04-21 and confirmed
   that the strict-retail Windows gate set remains green on the current
   worktree.
2. Re-based the top-level ledger so it now distinguishes the strict-retail
   Windows closure state from repo-wide parity across compatibility-only,
   portability, and packaging-dependent lanes.
3. Published a dedicated repo-wide gap register in
   `docs/reverse-engineering/repo-wide-parity-audit-2026-04-21.md`.
4. Demoted the most misleading broad-planning documents to explicit historical
   references so they no longer conflict with the current reverse-engineering
   ledgers.

### Task A1: Client parity-gate revalidation and workflow restoration [COMPLETED]
Priority: Critical
Primary areas: `.github/workflows/client-validation.yml`,
`tools/client/run_client_runtime_probe.ps1`,
`artifacts/client_validation/logs/*`, client ledger docs
Parity estimate: **before 99% -> after 100%**

Completed work:

1. Restored `.github/workflows/client-validation.yml` so the client validation
   lane again runs the focused platform, Steamworks, config, workshop, UI-menu,
   and unified parity-gate suites expected by the audited `CL-P6` closure.
2. Repaired `tools/client/run_client_runtime_probe.ps1` so it now:
   - runs against the default build-disabled client configuration
   - uses the valid `map bloodrun ffa` command shape for the local-map probe
   - avoids helper-stdout pollution in the structured probe return path
   - retries transient `pak_uiql.pk3` rewrite locks on Windows
   - caps the probe at `com_maxfps 30`, which lets the map pass reach
     `CS_ACTIVE` before the queued demo/screenshot/disconnect commands fire
3. Refreshed
   `artifacts/client_validation/logs/client_runtime_evidence_20260410.json`
   and
   `artifacts/client_validation/logs/client_full_parity_gate.json` with a
   clean runtime bundle.
4. Revalidated the lane with:
   - `pytest tests/test_client_full_parity_gate.py -q --tb=no`
   - `pytest tests/test_platform_services.py tests/test_steamworks_harness.py tests/test_client_config_parity.py tests/test_client_workshop_bootstrap_parity.py tests/test_ui_menu_files.py tests/test_client_full_parity_gate.py -q --tb=no`

### Task A3a: Expose explicit compatibility-only provider/policy labels through auth, workshop, and browser-overlay surfaces [COMPLETED]
Priority: Critical
Primary areas: `src/common/platform/`, `src/code/client/`,
`docs/platform/authentication.md`, `docs/steam_platform_abstraction.md`
Parity estimate: **before 96% -> after 96%**

Completed work:

1. Added `QL_DescribePlatformFeaturePolicy(...)` as the shared companion label
   for platform-service descriptors and threaded that label through the client
   auth dispatcher so build-disabled, runtime-disabled, and provider-unavailable
   lanes stay explicit in auth lifecycle logs.
2. Mirrored the browser/advert overlay descriptor through the ROM cvars
   `ui_browserAwesomiumProvider` and `ui_browserAwesomiumPolicy`, and routed the
   blocked browser commands through provider-aware compatibility logging instead
   of generic “provider unavailable” messages.
3. Bounded the retained workshop bootstrap to the Steam UGC owner lane,
   documented provider/policy-aware fallback logging for non-Steam/bootstrap
   paths, and refreshed the focused platform/workshop regression coverage to
   keep those compatibility-only labels visible.

### Task A3b: Expose explicit compatibility-only provider/policy labels through server auth and Steam GameServer surfaces [COMPLETED]
Priority: Critical
Primary areas: `src/code/server/`, `src/code/qcommon/`,
`docs/platform/authentication.md`, `docs/steam_platform_abstraction.md`
Parity estimate: **before 96% -> after 96%**

Completed work:

1. Mirrored the retained server auth and matchmaking descriptors through the
   ROM cvars `sv_platformAuthProvider`, `sv_platformAuthPolicy`,
   `sv_steamServerProvider`, and `sv_steamServerPolicy` so dedicated-server
   diagnostics expose the active provider/policy pair just as explicitly as the
   client-side browser, workshop, and auth surfaces.
2. Bounded the Steam GameServer bootstrap/publication lane with
   provider/policy-aware fallback and callback logging, including the
   compatibility-only dedicated-server publication fallback when the retained
   GameServer owner is unavailable.
3. Updated server-side auth telemetry so it now appends
   `provider=<...> policy=<...>` to the message payload while intentionally
   preserving the legacy `credential=steam` field, then refreshed the focused
   platform-service regression coverage to keep that compatibility labeling
   explicit.

### Task A3c: Expose explicit compatibility-only provider/policy labels through client live-resource bridge surfaces [COMPLETED]
Priority: Critical
Primary areas: `src/code/client/cl_steam_resources.c`,
`tests/test_platform_services.py`, `docs/steam_platform_abstraction.md`,
`docs/reverse-engineering/source-file-gap-notes/rw-g01-client-steam-resources.md`
Parity estimate: **before 96% -> after 96%**

Completed work:

1. Threaded the overlay service descriptor’s provider/policy labels into the
   retained live-resource bridge so the `steam://` avatar/resource path has the
   same explicit compatibility labeling as the browser overlay and workshop
   seams.
2. Replaced the generic Steam-resource and launcher-backend diagnostics with
   provider-aware logs that now spell out when the Steam resource bridge is
   disabled, when the retained SteamDataSource owner cannot satisfy a request,
   and when the launcher/web fallback owner is the remaining compatibility
   path.
3. Refreshed the focused platform-service regression coverage and the
   file-level `RW-G01` gap note so the live-resource bridge now documents the
   bounded compatibility/fallback story it still implements instead of the
   older generic “backend unavailable” wording.

### Task A3d: Expose explicit compatibility-only provider/policy labels through client matchmaking, stats, and social-overlay command surfaces [COMPLETED]
Priority: Critical
Primary areas: `src/code/client/cl_main.c`,
`tests/test_platform_services.py`, `docs/steam_platform_abstraction.md`
Parity estimate: **before 96% -> after 96%**

Completed work:

1. Mirrored the retained client matchmaking, stats, and social-overlay
   descriptors through the ROM cvars `cl_matchmakingProvider`,
   `cl_matchmakingPolicy`, `cl_statsProvider`, `cl_statsPolicy`,
   `cl_socialOverlayProvider`, and `cl_socialOverlayPolicy` so the active
   provider/policy pair remains visible at bootstrap and callback-init time.
2. Routed the retained `stats_clear`, `connect_lobby`, `clientviewprofile`,
   `clientfriendinvite`, callback-bundle fallback, and main-menu rich-presence
   failure paths through provider-aware compatibility diagnostics instead of
   generic Steam-only wording.
3. Refreshed the focused platform-service regression coverage and the platform
   abstraction notes so this client command surface now documents the bounded
   compatibility lane it still implements.

### Task A3e: Expose explicit compatibility-only provider/policy labels through the default-disabled server rankings surface [COMPLETED]
Priority: Critical
Primary areas: `src/code/server/sv_rankings.c`, `src/code/server/sv_init.c`,
`tests/test_platform_services.py`,
`docs/reverse-engineering/source-file-gap-notes/rw-g01-server-rankings.md`
Parity estimate: **before 96% -> after 96%**

Completed work:

1. Added explicit rankings provider/policy helpers and mirrored them through
   the ROM cvars `sv_rankingsProvider` and `sv_rankingsPolicy` so the
   default-disabled rankings lane no longer hides behind the generic
   `sv_rankingsActive` flag alone.
2. Threaded the provider/policy pair into the disabled rankings bootstrap
   diagnostics so the forced `sv_enableRankings 0` fallback and the retained
   compatibility-only rankings surface stay explicit at runtime.
3. Refreshed the focused server/platform-service parity checks and the
   `RW-G01` rankings gap note so this retained GPL-era rankings lane is now
   documented using the same compatibility-labeling story as the other active
   repo-wide online-service seams.

### Task A3f: Expose explicit heuristic compatibility labeling through auth backend responses and fallback traces [COMPLETED]
Priority: Critical
Primary areas: `src/common/platform/backends/`, `src/code/client/ql_auth.c`,
`tools/integration/auth_flow_trace.py`, `docs/platform/authentication.md`,
`docs/steam_platform_abstraction.md`
Parity estimate: **before 96% -> after 96%**

Completed work:

1. Updated the retained Steamworks and open-adapter auth backends so their
   response payloads explicitly identify themselves as heuristic compatibility
   backends instead of reading like retail live-service verdicts.
2. Threaded an explicit `hybrid-fallback` stage plus fallback-dispatch log
   through the hybrid auth path so the open-adapter handoff is visible in
   lifecycle traces whenever Steamworks returns a retry-eligible result.
3. Refreshed the scripted auth-flow trace, the focused platform-service
   regression coverage, and the auth/backend gap notes so the documented QA
   evidence now matches the bounded compatibility story carried by the current
   source.

### Task A3g: Expose explicit overall online-services mode/policy labels through the structural service-table surface [COMPLETED]
Priority: Critical
Primary areas: `src/common/platform/platform_services.c`,
`src/code/client/cl_main.c`, `src/code/server/sv_init.c`,
`tests/test_platform_services.py`, `docs/steam_platform_abstraction.md`
Parity estimate: **before 96% -> after 96%**

Completed work:

1. Added common helpers that collapse the cached service table into overall
   online-services mode/policy labels, keeping the build-disabled,
   externally-disabled, Steamworks-only, open-adapter-only, and hybrid
   compatibility lanes explicit at the structural layer itself.
2. Mirrored those summary labels through the new ROM cvars
   `cl_onlineServicesMode`, `cl_onlineServicesPolicy`,
   `sv_onlineServicesMode`, and `sv_onlineServicesPolicy` so client/server
   diagnostics no longer require reading each per-feature provider cvar to
   understand the current repo-wide online-service boundary.
3. Refreshed the focused platform-service probes plus the `RW-G01`
   platform-services/platform-config notes so the structural service-table and
   build-flag story now matches the bounded compatibility surface described by
   the current docs and tests.

### Task A3h: Expose explicit overall online-services mode/policy labeling through auth policy-block and ticket-request failure paths [COMPLETED]
Priority: Critical
Primary areas: `src/code/client/ql_auth.c`,
`tests/test_platform_services.py`, `docs/platform/authentication.md`,
`docs/steam_platform_abstraction.md`,
`docs/reverse-engineering/source-file-gap-notes/rw-g01-client-auth.md`
Parity estimate: **before 96% -> after 96%**

Completed work:

1. Routed the early Steam and standalone auth policy gates through a shared
   helper that now emits explicit `policy-blocked` lifecycle logs and response
   text naming the active overall online-services mode/policy lane instead of
   the older generic build/runtime wording.
2. Threaded that same structural mode/policy context through Steam
   ticket-request failure and backend-uninitialised responses so the bounded
   auth surface stays explicit even when no backend dispatch occurs.
3. Refreshed the focused auth/platform-service regression coverage plus the
   client-auth gap note and supporting docs so the documented `RW-G01`
   compatibility story now matches those early auth exit paths too.

### Task A3i: Expose explicit provider/policy labeling through the retained advert bridge surface [COMPLETED]
Priority: Critical
Primary areas: `src/code/client/cl_cgame.c`, `src/code/client/cl_main.c`,
`tests/test_platform_services.py`, `docs/steam_platform_abstraction.md`,
`docs/reverse-engineering/source-file-gap-notes/rw-g01-platform-services.md`
Parity estimate: **before 96% -> after 96%**

Completed work:

1. Mirrored the retained advert bridge through the new ROM cvars
   `ui_advertisementBridgeProvider` and `ui_advertisementBridgePolicy` so the
   active advert bridge lane is visible independently of the older browser
   overlay cvars.
2. Added bounded provider-aware advert lifecycle diagnostics for the UI/cgame
   bridge transitions (`init-ui`, `activate`, `set-active`, and
   `shutdown-cgame`) instead of leaving that seam implicit behind generic
   overlay state refreshes.
3. Refreshed the focused platform-service assertions plus the platform-service
   abstraction/gap-note docs so the retained advert flow now matches the same
   explicit compatibility-labeling story as the other active `RW-G01`
   surfaces.

### Task A3j: Expose explicit overall mode/policy labeling through the retained client voice fallback lane [COMPLETED]
Priority: Critical
Primary areas: `src/code/client/cl_main.c`,
`tests/test_platform_services.py`, `docs/steam_platform_abstraction.md`,
`docs/reverse-engineering/source-file-gap-notes/rw-g01-platform-services.md`
Parity estimate: **before 96% -> after 96%**

Completed work:

1. Mirrored the retained client voice compatibility lane through the new ROM
   cvars `cl_voiceServiceMode` and `cl_voiceServicePolicy` so the local
   speaking-state fallback no longer hides behind the broader online-services
   summary cvars alone.
2. Added explicit `voice fallback` diagnostics for `+voice` and `-voice`,
   naming the active overall online-services mode/policy lane whenever Steam
   voice is unavailable and the local speaking-state bridge is the remaining
   compatibility path.
3. Refreshed the focused platform-service assertions plus the
   platform-service abstraction/gap-note docs so the retained voice surface now
   matches the same explicit compatibility-labeling story as the other active
   `RW-G01` seams.

### Task A3k: Expose explicit overall mode/policy labeling through the retained client identity bootstrap and UI subscription lanes [COMPLETED]
Priority: Critical
Primary areas: `src/code/client/cl_main.c`, `src/code/client/cl_ui.c`,
`tests/test_platform_services.py`, `docs/steam_platform_abstraction.md`,
`docs/reverse-engineering/source-file-gap-notes/rw-g01-platform-services.md`
Parity estimate: **before 96% -> after 96%**

Completed work:

1. Mirrored the retained client identity/bootstrap and UI app-subscription
   lanes through the new ROM cvars `cl_identityBootstrapMode`,
   `cl_identityBootstrapPolicy`, `ui_subscriptionBridgeMode`, and
   `ui_subscriptionBridgePolicy` so these remaining Steam-owned shims no longer
   rely on the broader summary cvars alone for compatibility context.
2. Added explicit identity/subscription diagnostics for Steam persona-name
   seeding, Steam country seeding, and the UI `IsSubscribedApp` bridge,
   naming the active overall online-services mode/policy lane whenever the
   compatibility path falls back or the current provider is unavailable.
3. Refreshed the focused platform-service assertions plus the
   platform-service abstraction/gap-note docs so the retained client bootstrap
   and UI subscription surface now matches the same explicit
   compatibility-labeling story as the other active `RW-G01` seams.

### Task A3l: Expose explicit provider/policy labeling through the retained live-resource and avatar bridge lane [COMPLETED]
Priority: Critical
Primary areas: `src/code/client/cl_steam_resources.c`,
`src/code/client/cl_main.c`, `src/code/client/cl_cgame.c`,
`tests/test_platform_services.py`, `docs/steam_platform_abstraction.md`,
`docs/reverse-engineering/source-file-gap-notes/rw-g01-platform-services.md`
Parity estimate: **before 96% -> after 96%**

Completed work:

1. Mirrored the retained live-resource bridge through the new ROM cvars
   `ui_resourceBridgeProvider` and `ui_resourceBridgePolicy` so the
   `steam://`/launcher-backed image lane is visible independently of the older
   browser overlay and advert bridge cvars.
2. Routed the cgame avatar import through the existing provider-aware resource
   stub path instead of returning before the compatibility diagnostics fired,
   which keeps disabled `steam://avatar/...` lookups explicit at runtime.
3. Refreshed the focused platform-service assertions plus the
   platform-service abstraction/gap-note docs so the retained live-resource and
   avatar lane now matches the same explicit compatibility-labeling story as
   the other active `RW-G01` seams.

### Task A3m: Expose explicit provider/policy labeling through the retained client workshop lifecycle [COMPLETED]
Priority: Critical
Primary areas: `src/code/client/cl_main.c`,
`tests/test_platform_services.py`,
`tests/test_client_workshop_bootstrap_parity.py`,
`docs/steam_platform_abstraction.md`,
`docs/reverse-engineering/source-file-gap-notes/rw-g01-platform-services.md`
Parity estimate: **before 96% -> after 96%**

Completed work:

1. Mirrored the retained client workshop seam through the ROM cvars
   `cl_workshopProvider` and `cl_workshopPolicy` so the active workshop owner
   is visible alongside the other client online-service descriptors.
2. Routed the workshop bootstrap, download, callback-ignore, queue-complete,
   and filesystem-restart diagnostics through a shared provider-aware helper,
   which keeps the current compatibility-only workshop lane explicit instead of
   falling back to generic Steamworks-only wording.
3. Refreshed the focused workshop/platform-service regression coverage plus the
   platform-service abstraction and `RW-G01` gap note so the documented
   workshop lifecycle now matches the same explicit compatibility-labeling
   story as the other active online-service seams.

### Task A3n: Expose explicit provider/policy labeling through the retained dedicated-server P2P callback lane [COMPLETED]
Priority: Critical
Primary areas: `src/code/server/sv_client.c`,
`tests/test_platform_services.py`,
`docs/steam_platform_abstraction.md`,
`docs/reverse-engineering/source-file-gap-notes/rw-g01-platform-services.md`
Parity estimate: **before 96% -> after 96%**

Completed work:

1. Added a shared dedicated-server P2P callback logger that reports the active
   Steam GameServer provider/policy pair for the retained session-request
   surface instead of leaving those diagnostics as raw Steam-only wording.
2. Routed the server-side P2P request callback through that helper for missing
   client, unauthenticated client, and accept-failure paths so the bounded
   compatibility lane stays explicit during those callback exits too.
3. Refreshed the focused platform-service regression coverage plus the
   platform-service abstraction and `RW-G01` gap note so the dedicated-server
   P2P callback path now matches the same explicit compatibility-labeling story
   as the other active online-service seams.

### Task A3o: Expose explicit provider/policy labeling through the retained dedicated-server stats lane [COMPLETED]
Priority: Critical
Primary areas: `src/code/server/sv_init.c`, `src/code/server/sv_client.c`,
`tests/test_platform_services.py`,
`docs/steam_platform_abstraction.md`,
`docs/reverse-engineering/source-file-gap-notes/rw-g01-platform-services.md`
Parity estimate: **before 96% -> after 96%**

Completed work:

1. Mirrored the retained dedicated-server stats seam through the ROM cvars
   `sv_statsProvider` and `sv_statsPolicy` so the active GameServerStats owner
   is visible alongside the other server online-service descriptors.
2. Added a shared provider-aware server-stats logger and routed the
   request-current-values, session-bootstrap P2P hello failure, and stat-delta
   diagnostics through it so this compatibility-only lane no longer hides
   behind raw Steam-only wording.
3. Refreshed the focused platform-service regression coverage plus the
   platform-service abstraction and `RW-G01` gap note so the dedicated-server
   stats path now matches the same explicit compatibility-labeling story as the
   other active online-service seams.

### Task A3p: Expose explicit provider/policy labeling through the retained client rich-presence lifecycle [COMPLETED]
Priority: Critical
Primary areas: `src/code/client/cl_main.c`, `src/code/client/cl_cgame.c`,
`src/code/client/client.h`, `tests/test_platform_services.py`,
`docs/steam_platform_abstraction.md`,
`docs/reverse-engineering/source-file-gap-notes/rw-g01-platform-services.md`
Parity estimate: **before 96% -> after 96%**

Completed work:

1. Exported the shared matchmaking-lane logger through `client.h` so the
   retained first-snapshot rich-presence owner can report the active
   provider/policy pair instead of silently depending on a Steam-only path.
2. Routed the main-menu and first-snapshot rich-presence writes through
   explicit provider-aware fallback diagnostics for provider-unavailable and
   update-failed exits while preserving the existing retail status strings.
3. Refreshed the focused platform-service regression coverage plus the
   platform-service abstraction and `RW-G01` gap note so the retained client
   rich-presence lifecycle now matches the same explicit compatibility-labeling
   story as the other active online-service seams.

### Task A3q: Expose explicit provider/policy labeling through the retained dedicated-server auth rejection lane [COMPLETED]
Priority: Critical
Primary areas: `src/code/server/sv_client.c`,
`tests/test_platform_services.py`, `docs/platform/authentication.md`,
`docs/steam_platform_abstraction.md`,
`docs/reverse-engineering/source-file-gap-notes/rw-g01-platform-services.md`
Parity estimate: **before 96% -> after 96%**

Completed work:

1. Added a shared dedicated-server auth rejection logger so the retained
   auth-session bootstrap reports the active provider/policy pair when session
   startup fails instead of falling back to raw Steam-only debug wording.
2. Routed both auth-session bootstrap failure exits through that helper while
   preserving the legacy outward `Failed to authenticate with Steam: ...`
   message contract for stable client-facing and telemetry consumers.
3. Refreshed the focused platform-service regression coverage plus the auth and
   platform-service docs so the retained dedicated-server auth rejection path
   now matches the same explicit compatibility-labeling story as the other
   active online-service seams.

### Task A3r: Expose explicit provider/policy labeling through the retained client callback and stats-registration bootstrap gates [COMPLETED]
Priority: Critical
Primary areas: `src/code/client/cl_main.c`,
`tests/test_platform_services.py`,
`docs/steam_platform_abstraction.md`,
`docs/reverse-engineering/source-file-gap-notes/rw-g01-platform-services.md`
Parity estimate: **before 96% -> after 96%**

Completed work:

1. Routed the disabled-services early exit in `CL_Steam_InitCallbacks()` through
   the same provider-aware callback-bundle fallback diagnostic used by the
   registration-failure path, so the retained browser-event compatibility lane
   no longer stays silent when callbacks never become eligible.
2. Added explicit stats provider/policy-aware skip diagnostics to the
   `stats_clear` registration gate for provider-unavailable, initialisation-
   failed, and unsupported-app-id exits, which keeps that bootstrap boundary
   explicit even when the command is never registered.
3. Refreshed the focused platform-service regression coverage plus the
   platform-service abstraction and `RW-G01` gap note so the retained client
   callback/stats bootstrap path now matches the same explicit
   compatibility-labeling story as the other active online-service seams.

### Task A3s: Expose explicit provider/policy labeling through the retained dedicated-server callback bootstrap stub [COMPLETED]
Priority: Critical
Primary areas: `src/code/server/sv_client.c`,
`tests/test_platform_services.py`,
`docs/steam_platform_abstraction.md`,
`docs/reverse-engineering/source-file-gap-notes/rw-g01-platform-services.md`
Parity estimate: **before 96% -> after 96%**

Completed work:

1. Routed the build-disabled `SV_SteamServerInitCallbacks()` stub through the
   same provider-aware callback-registration fallback diagnostic used by the
   active registration failure path, so the dedicated-server callback lane no
   longer disappears silently during startup.
2. Extended the focused platform-service regression coverage to pin that
   build-disabled callback-bootstrap fallback against the existing provider and
   policy labels.
3. Refreshed the platform-service abstraction and `RW-G01` gap note so the
   retained dedicated-server callback bootstrap now matches the same explicit
   compatibility-labeling story as the other active online-service seams.

### Task A3t: Expose explicit mode/policy labeling through the retained client voice transport lifecycle [COMPLETED]
Priority: Critical
Primary areas: `src/code/client/cl_main.c`,
`tests/test_platform_services.py`,
`docs/steam_platform_abstraction.md`,
`docs/reverse-engineering/source-file-gap-notes/rw-g01-platform-services.md`
Parity estimate: **before 96% -> after 96%**

Completed work:

1. Added a shared voice-transport lifecycle logger so the retained Steam voice
   send/receive lane now reports the active overall mode/policy pair instead
   of falling back to raw generic trace wording when the transport fails.
2. Routed voice packet send failure, packet read failure, decompress failure,
   and zero-byte-decompress diagnostics through that helper so the retained
   voice transport now matches the same explicit compatibility story as the
   `+voice` / `-voice` command surface.
3. Refreshed the focused platform-service regression coverage plus the
   platform-service abstraction and `RW-G01` gap note so the retained client
   voice transport lifecycle now matches the same explicit
   compatibility-labeling story as the other active online-service seams.

### Task A3u: Expose explicit provider/policy labeling through the retained dedicated-server stats-owner stubs [COMPLETED]
Priority: Critical
Primary areas: `src/code/server/sv_client.c`,
`tests/test_platform_services.py`,
`docs/steam_platform_abstraction.md`,
`docs/reverse-engineering/source-file-gap-notes/rw-g01-platform-services.md`
Parity estimate: **before 96% -> after 96%**

Completed work:

1. Added a shared provider-aware stub logger for the build-disabled dedicated-
   server stats owner path so the retained `SV_SteamStats_*` surface no longer
   disappears silently when the current stats lane is unavailable.
2. Routed the build-disabled stat-delta, achievement-unlock, and achievement-
   query stubs through that helper with call-site detail strings, keeping the
   compatibility-only fallback explicit even when the owner functions still
   return without touching a live backend.
3. Refreshed the focused platform-service regression coverage plus the
   platform-service abstraction and `RW-G01` gap note so the retained
   dedicated-server stats-owner stubs now match the same explicit
   compatibility-labeling story as the other active online-service seams.

### Task A3v: Expose explicit provider/policy labeling through the retained dedicated-server networking maintenance lane [COMPLETED]
Priority: Critical
Primary areas: `src/code/server/sv_main.c`,
`tests/test_platform_services.py`,
`docs/steam_platform_abstraction.md`,
`docs/reverse-engineering/source-file-gap-notes/rw-g01-platform-services.md`
Parity estimate: **before 96% -> after 96%**

Completed work:

1. Added a shared provider-aware networking logger for the retained Steam
   GameServer maintenance owner so keepalive and packet-relay failures no
   longer collapse into silent compatibility-only behavior.
2. Routed keepalive send failure, inbound relay read failure, unknown relay
   sender, and relay-send failure exits through that helper, keeping the
   bounded Steam GameServer networking lane explicit whenever those paths fail.
3. Refreshed the focused platform-service regression coverage plus the
   platform-service abstraction and `RW-G01` gap note so the retained
   dedicated-server networking maintenance lane now matches the same explicit
   compatibility-labeling story as the other active online-service seams.

### Task A3w: Expose explicit provider/policy labeling through the retained dedicated-server published-state owner [COMPLETED]
Priority: Critical
Primary areas: `src/code/server/sv_main.c`,
`tests/test_platform_services.py`,
`docs/steam_platform_abstraction.md`,
`docs/reverse-engineering/source-file-gap-notes/rw-g01-platform-services.md`
Parity estimate: **before 96% -> after 96%**

Completed work:

1. Added a shared provider-aware published-state logger for the retained Steam
   GameServer metadata owner so publication writes no longer fail silently
   behind the bounded compatibility lane.
2. Routed max-player, password, hostname, map, game-description, game-tags,
   score key-value, player-data, and bot-count publication failures through
   that helper, keeping the retained GameServer metadata owner explicit when
   those writes cannot be applied.
3. Refreshed the focused platform-service regression coverage plus the
   platform-service abstraction and `RW-G01` gap note so the retained
   dedicated-server published-state owner now matches the same explicit
   compatibility-labeling story as the other active online-service seams.

### Task A3x: Expose explicit provider/policy labeling through the retained client P2P callback lane [COMPLETED]
Priority: Critical
Primary areas: `src/code/client/cl_main.c`,
`tests/test_platform_services.py`,
`docs/steam_platform_abstraction.md`,
`docs/reverse-engineering/source-file-gap-notes/rw-g01-platform-services.md`
Parity estimate: **before 96% -> after 96%**

Completed work:

1. Added a shared matchmaking callback logger for the retained client P2P
   session-request owner so this callback lane no longer falls back to a raw
   generic Steam trace.
2. Routed both the accept-failure and accepted-session callback exits through
   that helper with the requested remote SteamID detail, which keeps the
   bounded client matchmaking callback surface explicit whenever the callback
   fires.
3. Refreshed the focused platform-service regression coverage plus the
   platform-service abstraction and `RW-G01` gap note so the retained client
   P2P callback lane now matches the same explicit compatibility-labeling story
   as the other active online-service seams.

### Task A3y: Expose explicit provider/policy labeling through the retained client browser-event publish lane [COMPLETED]
Priority: Critical
Primary areas: `src/code/client/cl_main.c`,
`tests/test_platform_services.py`,
`docs/steam_platform_abstraction.md`,
`docs/reverse-engineering/source-file-gap-notes/rw-g01-platform-services.md`
Parity estimate: **before 96% -> after 96%**

Completed work:

1. Added a shared browser-event lifecycle logger for the retained client
   browser-event owner so this queue lane no longer falls back to generic
   `PublishEvent failed` or raw `steam_event` traces.
2. Routed the missing-view, missing-window-object, and queued-event exits
   through that helper with explicit queue metadata, keeping the retained
   overlay/browser seam honest about the current provider/policy pair whenever
   browser events are published.
3. Refreshed the focused platform-service regression coverage plus the
   platform-service abstraction and `RW-G01` gap note so the retained client
   browser-event publish lane now matches the same explicit compatibility
   labeling story as the other active online-service seams.

### Task A3z: Expose explicit provider/policy labeling through the retained client microtransaction callback lane [COMPLETED]
Priority: Critical
Primary areas: `src/code/client/cl_main.c`,
`tests/test_platform_services.py`,
`docs/steam_platform_abstraction.md`,
`docs/reverse-engineering/source-file-gap-notes/rw-g01-platform-services.md`
Parity estimate: **before 96% -> after 96%**

Completed work:

1. Added a shared microtransaction callback logger for the retained client
   purchase-authorization lane so this callback no longer falls back to a raw
   generic payload dump.
2. Routed the retained microtransaction authorization callback through that
   helper before it forwards the purchase update into the browser-event queue,
   keeping the overlay/browser compatibility owner explicit whenever this
   callback fires.
3. Refreshed the focused platform-service regression coverage plus the
   platform-service abstraction and `RW-G01` gap note so the retained client
   microtransaction callback lane now matches the same explicit
   compatibility-labeling story as the other active online-service seams.

### Task A3aa: Expose explicit provider/policy labeling through the retained dedicated-server workshop operator surface [COMPLETED]
Priority: Critical
Primary areas: `src/code/server/sv_init.c`, `src/code/server/sv_ccmds.c`,
`tests/test_platform_services.py`,
`docs/steam_platform_abstraction.md`,
`docs/reverse-engineering/source-file-gap-notes/rw-g01-platform-services.md`
Parity estimate: **before 96% -> after 96%**

Completed work:

1. Mirrored the retained dedicated-server workshop seam through the ROM cvars
   `sv_workshopProvider` and `sv_workshopPolicy` so the active workshop owner
   is visible alongside the other server online-service descriptors.
2. Added a shared provider-aware workshop operator logger plus a bounded
   Steam-UGC support gate for `steam_downloadugc`, `steam_subscribeugc`, and
   `steam_unsubscribeugc`, which keeps those Steam-specific operator commands
   explicit about the current compatibility lane instead of pretending that
   every workshop provider owns the same surface.
3. Refreshed the focused platform-service regression coverage plus the
   platform-service abstraction and `RW-G01` gap note so the retained server
   workshop operator surface now matches the same explicit
   compatibility-labeling story as the other active online-service seams.

### Task A3ab: Expose explicit provider/policy labeling through the retained client web-host social and UGC export lanes [COMPLETED]
Priority: Critical
Primary areas: `src/code/client/cl_cgame.c`, `tests/test_platform_services.py`,
`docs/steam_platform_abstraction.md`,
`docs/reverse-engineering/source-file-gap-notes/rw-g01-platform-services.md`
Parity estimate: **before 96% -> after 96%**

Completed work:

1. Added retained web-host helpers for the overall online-service mode/policy
   plus matchmaking and workshop provider/policy labels, keeping the browser
   social/UGC export seams aligned with the repo-wide compatibility boundary.
2. Updated `GetConfig`, friend-list export, UGC export, and `web.ugc.failed`
   publication so browser callers see explicit provider/policy metadata while
   disabled or unavailable Steam-backed exports log bounded fallback
   diagnostics without changing the legacy array payload shape.
3. Refreshed focused regression coverage plus the platform-service abstraction
   and `RW-G01` gap note so the retained client web-host export lane now
   matches the same explicit compatibility-labeling story as the other active
   online-service seams.

### Task A3ac: Expose explicit provider/policy labeling through the retained client lobby callback lane [COMPLETED]
Priority: Critical
Primary areas: `src/code/client/cl_main.c`, `tests/test_platform_services.py`,
`docs/steam_platform_abstraction.md`,
`docs/reverse-engineering/source-file-gap-notes/rw-g01-platform-services.md`
Parity estimate: **before 96% -> after 96%**

Completed work:

1. Extended the retained matchmaking callback diagnostics so the client lobby
   callback owner now reports provider/policy-aware lifecycle detail for lobby
   create, enter, membership, chat, metadata, game-created, kicked, and
   join-requested events instead of only making the bounded queue visible once
   the browser-event publication layer runs.
2. Kept the existing browser-event payload shapes intact while making the
   callback-origin seam explicit, which preserves the compatibility-only
   browser contract without letting those lobby callbacks read like silent
   Steam-owned behavior.
3. Refreshed the focused platform-service regression coverage plus the
   platform-service abstraction and `RW-G01` gap note so the retained client
   lobby callback lane now matches the same explicit compatibility-labeling
   story as the other active online-service seams.

### Task A3ad: Expose explicit provider/policy labeling through the retained client callback connect-handoff lane [COMPLETED]
Priority: Critical
Primary areas: `src/code/client/cl_main.c`, `tests/test_platform_services.py`,
`docs/steam_platform_abstraction.md`,
`docs/reverse-engineering/source-file-gap-notes/rw-g01-platform-services.md`
Parity estimate: **before 96% -> after 96%**

Completed work:

1. Routed the retained rich-presence join and server-change callback handoff
   through the shared matchmaking callback logger so the immediate
   join/connect command path now reports the active provider/policy pair
   instead of silently executing callback payloads.
2. Added bounded callback detail for missing join commands, missing server
   targets, and password-seeded server-connect handoff without changing the
   legacy immediate-command behavior or the outward connect payload shape.
3. Refreshed the focused platform-service regression coverage plus the
   platform-service abstraction and `RW-G01` gap note so the retained client
   callback connect-handoff lane now matches the same explicit
   compatibility-labeling story as the other active online-service seams.

### Task A3ae: Expose explicit provider/policy labeling through the retained client stats callback lane [COMPLETED]
Priority: Critical
Primary areas: `src/code/client/cl_main.c`, `tests/test_platform_services.py`,
`docs/steam_platform_abstraction.md`,
`docs/reverse-engineering/source-file-gap-notes/rw-g01-platform-services.md`
Parity estimate: **before 96% -> after 96%**

Completed work:

1. Added a shared stats callback logger so the retained user-stats callback
   owner now reports the active stats provider/policy pair instead of only
   becoming visible once the browser-event queue publishes the resulting
   payload.
2. Routed the `users.stats.*.received` callback path through that helper with
   bounded SteamID, game-ID, and result detail while preserving the legacy
   browser-event payload shape and queue semantics.
3. Refreshed the focused platform-service regression coverage plus the
   platform-service abstraction and `RW-G01` gap note so the retained client
   stats callback lane now matches the same explicit compatibility-labeling
   story as the other active online-service seams.

### Task A3af: Expose explicit provider/policy labeling through the retained client social-presence and UGC callback lanes [COMPLETED]
Priority: Critical
Primary areas: `src/code/client/cl_main.c`, `tests/test_platform_services.py`,
`docs/steam_platform_abstraction.md`,
`docs/reverse-engineering/source-file-gap-notes/rw-g01-platform-services.md`
Parity estimate: **before 96% -> after 96%**

Completed work:

1. Routed the retained client persona-state and friend-rich-presence callback
   owners through the shared matchmaking callback logger so those
   browser-facing presence updates now report the active provider/policy pair
   instead of only becoming visible when the shared queue publishes them.
2. Routed the retained client UGC query-complete callback through the
   workshop lifecycle logger with bounded call/query/result detail while
   preserving the legacy `web.ugc.results` / `web.ugc.failed` payload shapes
   and browser event names.
3. Refreshed the focused platform-service regression coverage plus the
   platform-service abstraction and `RW-G01` gap note so the retained client
   social-presence and UGC callback lanes now match the same explicit
   compatibility-labeling story as the other active online-service seams.

### Task A3ag: Expose explicit provider/policy labeling through the retained client workshop callback lane [COMPLETED]
Priority: Critical
Primary areas: `src/code/client/cl_main.c`, `tests/test_platform_services.py`,
`docs/steam_platform_abstraction.md`,
`docs/reverse-engineering/source-file-gap-notes/rw-g01-platform-services.md`
Parity estimate: **before 96% -> after 96%**

Completed work:

1. Routed the retained client workshop `ItemInstalled` and
   `DownloadItemResult` callback owners through provider/policy-aware
   lifecycle diagnostics so tracked completion, untracked-item ignore, and
   result-failure exits are explicit instead of only becoming visible through
   the downstream queue helpers.
2. Kept the existing workshop queue behavior intact: item completion still
   flows through `CL_Workshop_FinalizeInstalledItem()`, failures still flow
   through `CL_Workshop_FailActiveDownload()`, and the legacy queue-advance
   behavior remains unchanged.
3. Refreshed the focused platform-service regression coverage plus the
   platform-service abstraction and `RW-G01` gap note so the retained client
   workshop callback lane now matches the same explicit
   compatibility-labeling story as the other active online-service seams.

### Task A3ah: Expose explicit provider/policy labeling through the retained dedicated-server connection callback lane [COMPLETED]
Priority: Critical
Primary areas: `src/code/server/sv_client.c`,
`tests/test_platform_services.py`,
`docs/steam_platform_abstraction.md`,
`docs/reverse-engineering/source-file-gap-notes/rw-g01-platform-services.md`
Parity estimate: **before 96% -> after 96%**

Completed work:

1. Routed the retained Steam GameServer connected, connect-failure, and
   disconnected callbacks through a shared provider/policy-aware callback
   lifecycle logger so those server callback-owner state changes no longer
   appear as isolated one-off print lines.
2. Kept the existing server behavior intact: successful connects still publish
   identity and refreshed published state, failure/disconnect callbacks still
   clear the connected flag, and no auth/session routing changed.
3. Refreshed the focused platform-service regression coverage plus the
   platform-service abstraction and `RW-G01` gap note so the retained
   dedicated-server connection callback lane now matches the same explicit
   compatibility-labeling story as the other active online-service seams.

### Task A3ai: Expose explicit provider/policy labeling through the retained client workshop callback bootstrap gate [COMPLETED]
Priority: Critical
Primary areas: `src/code/client/cl_main.c`, `tests/test_platform_services.py`,
`docs/steam_platform_abstraction.md`,
`docs/reverse-engineering/source-file-gap-notes/rw-g01-platform-services.md`
Parity estimate: **before 96% -> after 96%**

Completed work:

1. Routed the retained client workshop callback registration-failure path
   through the shared workshop lifecycle logger so the polling-only fallback is
   explicit about the active provider/policy pair instead of appearing as a
   one-off raw debug line.
2. Kept the existing bootstrap behavior intact: the client still enables the
   main callback bundle, leaves workshop progress on the polling fallback when
   workshop callback registration fails, and does not change queue or browser
   event behavior.
3. Refreshed the focused platform-service regression coverage plus the
   platform-service abstraction and `RW-G01` gap note so the retained client
   workshop callback bootstrap gate now matches the same explicit
   compatibility-labeling story as the other active online-service seams.

### Task A3aj: Expose explicit provider/policy labeling through the retained dedicated-server identity publication lane [COMPLETED]
Priority: Critical
Primary areas: `src/code/server/sv_init.c`, `tests/test_platform_services.py`,
`docs/steam_platform_abstraction.md`,
`docs/reverse-engineering/source-file-gap-notes/rw-g01-platform-services.md`
Parity estimate: **before 96% -> after 96%**

Completed work:

1. Routed the retained Steam GameServer identity-publication owner through a
   shared provider/policy-aware lifecycle logger so both the unavailable and
   successful publish paths are explicit instead of only surfacing a raw
   identity-unavailable debug line.
2. Kept the existing identity behavior intact: the server still publishes the
   `0x2ca` SteamID configstring, mirrors `sv_referencedSteamworks`, and writes
   the `0x2cb` referenced-workshop configstring without changing the outward
   contract.
3. Refreshed the focused platform-service regression coverage plus the
   platform-service abstraction and `RW-G01` gap note so the retained
   dedicated-server identity publication lane now matches the same explicit
   compatibility-labeling story as the other active online-service seams.

### Task A3ak: Expose explicit provider/policy labeling through the retained dedicated-server callback bootstrap gate [COMPLETED]
Priority: Critical
Primary areas: `src/code/server/sv_client.c`, `tests/test_platform_services.py`,
`docs/steam_platform_abstraction.md`,
`docs/reverse-engineering/source-file-gap-notes/rw-g01-platform-services.md`
Parity estimate: **before 96% -> after 96%**

Completed work:

1. Routed the retained Steam GameServer callback-registration fallback through
   a provider/policy-aware bootstrap lifecycle logger in both the live
   registration-failure path and the build-disabled stub path instead of
   leaving those exits as raw one-off debug lines.
2. Kept the existing callback-registration behavior intact: successful
   registration still clears `sv_steamServerConnected`, while the unavailable
   paths still return immediately after surfacing the explicit compatibility
   diagnostic.
3. Refreshed the focused platform-service regression coverage plus the
   platform-service abstraction and `RW-G01` gap note so the retained
   dedicated-server callback bootstrap gate now matches the same explicit
   compatibility-labeling story as the other active server-owned seams.

### Task A3al: Expose explicit provider/policy labeling through the retained client callback bootstrap gate [COMPLETED]
Priority: Critical
Primary areas: `src/code/client/cl_main.c`, `tests/test_platform_services.py`,
`docs/steam_platform_abstraction.md`,
`docs/reverse-engineering/source-file-gap-notes/rw-g01-platform-services.md`
Parity estimate: **before 96% -> after 96%**

Completed work:

1. Routed the retained client callback-bundle fallback through a shared
   provider-aware bootstrap logger so the services-disabled and
   registration-failure exits now spell out the active matchmaking, stats, and
   social-overlay provider/policy pairs instead of staying as raw one-off
   debug lines.
2. Kept the existing callback bootstrap behavior intact: the client still
   clears the browser-event and lobby state before registration, still returns
   early when online services stay disabled, and still unregisters the partial
   client/lobby/micro callback bundle before falling back.
3. Refreshed the focused platform-service regression coverage plus the
   platform-service abstraction and `RW-G01` gap note so the retained client
   callback bootstrap gate now matches the same explicit compatibility-labeling
   story as the other active client-owned seams.

### Task A3am: Expose explicit provider/policy labeling through the retained client workshop required-items bootstrap gate [COMPLETED]
Priority: Critical
Primary areas: `src/code/client/cl_main.c`, `tests/test_platform_services.py`,
`docs/steam_platform_abstraction.md`,
`docs/reverse-engineering/source-file-gap-notes/rw-g01-platform-services.md`
Parity estimate: **before 96% -> after 96%**

Completed work:

1. Routed the retained client workshop required-items bootstrap fallback
   through the shared workshop lifecycle logger so the non-Steam/bootstrap-
   unavailable exit no longer stays as a raw one-off print line.
2. Kept the existing workshop bootstrap behavior intact: the client still logs
   the server-published required item list, still returns immediately when the
   current workshop lane cannot own Steam bootstrap, and still preserves the
   existing queue setup once a Steam UGC owner is available.
3. Refreshed the focused platform-service regression coverage plus the
   platform-service abstraction and `RW-G01` gap note so the retained client
   workshop required-items bootstrap gate now matches the same explicit
   compatibility-labeling story as the other active workshop seams.

### Task A3an: Expose explicit provider/policy labeling through the retained dedicated-server stats request/session lifecycle lane [COMPLETED]
Priority: Critical
Primary areas: `src/code/server/sv_client.c`,
`tests/test_platform_services.py`, `docs/steam_platform_abstraction.md`,
`docs/reverse-engineering/source-file-gap-notes/rw-g01-platform-services.md`
Parity estimate: **before 96% -> after 96%**

Completed work:

1. Routed successful stats request issue plus the active-session reuse, fresh
   session-bootstrap, and backend reconnect requery transitions through the
   shared stats lifecycle logger, so those retained GameServerStats success
   paths now surface the same provider/policy pair as the existing failure
   diagnostics.
2. Kept the retained stats owner behavior intact: existing request issuance,
   session reset/bootstrap, P2P hello delivery, and reconnect-driven requery
   semantics all remain unchanged apart from the new explicit compatibility
   labels.
3. Refreshed the focused platform-service regression coverage plus the
   platform-service abstraction and `RW-G01` gap note so the retained
   dedicated-server stats owner now documents the same explicit
   compatibility-labeling story on both its request and session lifecycle
   paths.

### Task A3ao: Expose explicit provider/policy labeling through the retained dedicated-server stats publish/store lane [COMPLETED]
Priority: Critical
Primary areas: `src/code/server/sv_client.c`,
`tests/test_platform_services.py`, `docs/steam_platform_abstraction.md`,
`docs/reverse-engineering/source-file-gap-notes/rw-g01-platform-services.md`
Parity estimate: **before 96% -> after 96%**

Completed work:

1. Routed the retained stats pending-value flush path through the shared stats
   lifecycle logger so stat publish failures, achievement publish failures,
   store-request failure, and successful store completion now all surface the
   same provider/policy pair instead of failing silently inside the
   GameServerStats owner.
2. Kept the retained stats owner behavior intact: dirty stat/achievement
   accumulation, backend store submission, and dirty-bit clearing still follow
   the same recovered control flow, with the new compatibility labels only
   documenting the existing publish/store decisions.
3. Refreshed the focused platform-service regression coverage plus the
   platform-service abstraction and `RW-G01` gap note so the retained
   dedicated-server stats owner now documents the same explicit
   compatibility-labeling story across its request, session, and publish/store
   lifecycle paths.

### Task A3ap: Expose explicit provider/policy labeling through the retained dedicated-server stats query/load lane [COMPLETED]
Priority: Critical
Primary areas: `src/code/server/sv_client.c`,
`tests/test_platform_services.py`, `docs/steam_platform_abstraction.md`,
`docs/reverse-engineering/source-file-gap-notes/rw-g01-platform-services.md`
Parity estimate: **before 96% -> after 96%**

Completed work:

1. Routed the retained `GetUserStatInt` and `GetUserAchievement` fetch paths
   through the shared stats lifecycle logger so stat/achievement query
   success and failure now surface the same provider/policy pair instead of
   silently returning through the dedicated-server `GameServerStats` owner.
2. Kept the retained stats owner behavior intact: request issuance, cached
   value reuse, pending-delta accumulation, and achievement unlock decisions
   still follow the same recovered control flow, with the new compatibility
   labels only documenting the existing query/load outcomes.
3. Refreshed the focused platform-service regression coverage plus the
   platform-service abstraction and `RW-G01` gap note so the retained
   dedicated-server stats owner now documents the same explicit
   compatibility-labeling story across its request, session, query, and
   publish/store lifecycle paths.

### Task A3aq: Expose explicit provider/policy labeling through the retained dedicated-server stats achievement owner/query lane [COMPLETED]
Priority: Critical
Primary areas: `src/code/server/sv_client.c`,
`tests/test_platform_services.py`, `docs/steam_platform_abstraction.md`,
`docs/reverse-engineering/source-file-gap-notes/rw-g01-platform-services.md`
Parity estimate: **before 96% -> after 96%**

Completed work:

1. Routed the retained achievement-owner entry points through the shared stats
   lifecycle logger so invalid-achievement, gameplay-gated, unavailable,
   session-unavailable, already-held, queued-unlock, and ownership-result
   outcomes now surface the same provider/policy pair instead of returning
   silently through the active `GameServerStats` owner.
2. Kept the retained stats owner behavior intact: achievement gate checks,
   session bootstrap, cached ownership reuse, and pending unlock/store flows
   still follow the same recovered control flow, with the new compatibility
   labels only documenting the existing owner/query decisions.
3. Refreshed the focused platform-service regression coverage plus the
   platform-service abstraction and `RW-G01` gap note so the retained
   dedicated-server stats owner now documents the same explicit
   compatibility-labeling story across its request, session, query,
   achievement-owner, and publish/store lifecycle paths.

### Task A3ar: Expose explicit provider/policy labeling through the retained dedicated-server stats field-owner lane [COMPLETED]
Priority: Critical
Primary areas: `src/code/server/sv_client.c`,
`tests/test_platform_services.py`, `docs/steam_platform_abstraction.md`,
`docs/reverse-engineering/source-file-gap-notes/rw-g01-platform-services.md`
Parity estimate: **before 96% -> after 96%**

Completed work:

1. Routed the retained stat-delta owner entry point through the shared stats
   lifecycle logger so invalid/no-op, unavailable, session-unavailable, and
   baseline-unavailable queue decisions now surface the same provider/policy
   pair instead of returning silently through the active `GameServerStats`
   owner.
2. Kept the retained stats owner behavior intact: stat lookup, session
   bootstrap, pending-delta accumulation, and dirty-bit publication still
   follow the same recovered control flow, with the new compatibility labels
   only documenting the existing field-owner decisions.
3. Refreshed the focused platform-service regression coverage plus the
   platform-service abstraction and `RW-G01` gap note so the retained
   dedicated-server stats owner now documents the same explicit
   compatibility-labeling story across its request, session, query,
   field-owner, achievement-owner, and publish/store lifecycle paths.

### Task A3as: Expose explicit provider/policy labeling through the retained dedicated-server stats session-teardown lane [COMPLETED]
Priority: Critical
Primary areas: `src/code/server/sv_client.c`,
`tests/test_platform_services.py`, `docs/steam_platform_abstraction.md`,
`docs/reverse-engineering/source-file-gap-notes/rw-g01-platform-services.md`
Parity estimate: **before 96% -> after 96%**

Completed work:

1. Routed the retained stats session-teardown helper through the shared stats
   lifecycle logger so inactive-session skips and completed session clears now
   surface the same provider/policy pair instead of returning silently during
   auth/session shutdown.
2. Kept the retained teardown behavior intact: pending stat/achievement flush,
   session reset, and caller-owned auth shutdown sequencing still follow the
   same recovered control flow, with the new compatibility labels only
   documenting the existing session-clear decisions.
3. Refreshed the focused platform-service regression coverage plus the
   platform-service abstraction and `RW-G01` gap note so the retained
   dedicated-server stats owner now documents the same explicit
   compatibility-labeling story across its request, session, query,
   field-owner, achievement-owner, session-teardown, and publish/store
   lifecycle paths.

### Task A3at: Expose explicit provider/policy labeling through the retained dedicated-server stats session-bootstrap gate [COMPLETED]
Priority: Critical
Primary areas: `src/code/server/sv_client.c`,
`tests/test_platform_services.py`, `docs/steam_platform_abstraction.md`,
`docs/reverse-engineering/source-file-gap-notes/rw-g01-platform-services.md`
Parity estimate: **before 96% -> after 96%**

Completed work:

1. Routed the retained stats session-bootstrap gate through the shared stats
   lifecycle logger so null, out-of-range, zombie, missing-gentity,
   missing-SteamID, bot-owned, and invalid-SteamID skips now surface the same
   provider/policy pair instead of returning silently before session creation.
2. Kept the retained bootstrap behavior intact: valid clients still reuse live
   sessions, still create/reset sessions the same way, still request current
   values, and still send the Steam P2P hello packet with the same recovered
   control flow.
3. Refreshed the focused platform-service regression coverage plus the
   platform-service abstraction and `RW-G01` gap note so the retained
   dedicated-server stats owner now documents the same explicit
   compatibility-labeling story across its request, session-bootstrap, query,
   field-owner, achievement-owner, session-teardown, and publish/store
   lifecycle paths.

### Task A3au: Expose explicit provider/policy labeling through the retained dedicated-server stats client-slot gate [COMPLETED]
Priority: Critical
Primary areas: `src/code/server/sv_client.c`,
`tests/test_platform_services.py`, `docs/steam_platform_abstraction.md`,
`docs/reverse-engineering/source-file-gap-notes/rw-g01-platform-services.md`
Parity estimate: **before 96% -> after 96%**

Completed work:

1. Routed the retained stats client-slot helper through the shared stats
   lifecycle logger so out-of-range, inactive, zombie, missing-gentity,
   missing-SteamID, bot-owned, and invalid-SteamID gating now surface the
   same provider/policy pair instead of returning silently before the field
   and achievement owners can explain why the request stopped.
2. Kept the retained owner behavior intact: valid stat/achievement callers
   still resolve the same live client slot, still bootstrap or reuse sessions
   the same way, and still apply the same field/achievement control flow once
   a valid slot is available.
3. Refreshed the focused platform-service regression coverage plus the
   platform-service abstraction and `RW-G01` gap note so the retained
   dedicated-server stats owner now documents the same explicit
   compatibility-labeling story across its request, session-bootstrap,
   client-slot, query, field-owner, achievement-owner, session-teardown, and
   publish/store lifecycle paths.

### Task A3av: Expose explicit provider/policy labeling through the retained dedicated-server stats request gate [COMPLETED]
Priority: Critical
Primary areas: `src/code/server/sv_client.c`,
`tests/test_platform_services.py`, `docs/steam_platform_abstraction.md`,
`docs/reverse-engineering/source-file-gap-notes/rw-g01-platform-services.md`
Parity estimate: **before 96% -> after 96%**

Completed work:

1. Routed the retained `SV_SteamStats_RequestCurrentValues` gate through the
   shared stats lifecycle logger so null-session, inactive-session, and
   missing-SteamID request skips now surface the same provider/policy pair
   instead of returning silently before the existing request issue/failure
   diagnostics run.
2. Kept the retained request behavior intact: valid sessions still issue the
   same `SteamGameServerStats` request, still mark `backendAvailable` and
   `requestIssued`, and still preserve the same success/failure control flow
   once the request gate is satisfied.
3. Refreshed the focused platform-service regression coverage plus the
   platform-service abstraction and `RW-G01` gap note so the retained
   dedicated-server stats owner now documents the same explicit
   compatibility-labeling story across its request gate, session-bootstrap,
   client-slot, query, field-owner, achievement-owner, session-teardown, and
   publish/store lifecycle paths.

### Task A3aw: Expose explicit provider/policy labeling through the retained dedicated-server stats value-query gate [COMPLETED]
Priority: Critical
Primary areas: `src/code/server/sv_client.c`,
`tests/test_platform_services.py`, `docs/steam_platform_abstraction.md`,
`docs/reverse-engineering/source-file-gap-notes/rw-g01-platform-services.md`
Parity estimate: **before 96% -> after 96%**

Completed work:

1. Routed the retained stat/achievement value-query gate through the shared
   stats lifecycle logger so null-session, inactive-session, invalid-id,
   unmapped-id, and already-cached paths now surface the same provider/policy
   pair instead of returning silently before the existing query result
   diagnostics run.
2. Kept the retained query behavior intact: valid uncached stat and
   achievement requests still issue the same backend reads, still apply the
   same pending-delta merge or cached ownership update, and still preserve the
   same success/failure control flow once the query gate is satisfied.
3. Refreshed the focused platform-service regression coverage plus the
   platform-service abstraction and `RW-G01` gap note so the retained
   dedicated-server stats owner now documents the same explicit
   compatibility-labeling story across its request gate, session-bootstrap,
   client-slot, value-query gate, field-owner, achievement-owner,
   session-teardown, and publish/store lifecycle paths.

### Task A3ax: Expose explicit provider/policy labeling through the retained dedicated-server stats value-flush gate [COMPLETED]
Priority: Critical
Primary areas: `src/code/server/sv_client.c`,
`tests/test_platform_services.py`, `docs/steam_platform_abstraction.md`,
`docs/reverse-engineering/source-file-gap-notes/rw-g01-platform-services.md`
Parity estimate: **before 96% -> after 96%**

Completed work:

1. Routed the retained `SV_SteamStats_FlushPendingValues` gate through the
   shared stats lifecycle logger so null-session, inactive-session,
   missing-SteamID, and no-pending-update skips now surface the same
   provider/policy pair instead of returning silently before the existing
   publish/store diagnostics run.
2. Kept the retained flush behavior intact: dirty stat/achievement scans,
   backend publish attempts, store submission, and dirty-bit clearing still
   follow the same recovered control flow once the flush gate is satisfied.
3. Refreshed the focused platform-service regression coverage plus the
   platform-service abstraction and `RW-G01` gap note so the retained
   dedicated-server stats owner now documents the same explicit
   compatibility-labeling story across its request gate, session-bootstrap,
   client-slot, value-query gate, value-flush gate, field-owner,
   achievement-owner, session-teardown, and publish/store lifecycle paths.

### Task A3ay: Expose explicit provider/policy labeling through the retained dedicated-server stats session-reset helper [COMPLETED]
Priority: Critical
Primary areas: `src/code/server/sv_client.c`,
`tests/test_platform_services.py`, `docs/steam_platform_abstraction.md`,
`docs/reverse-engineering/source-file-gap-notes/rw-g01-platform-services.md`
Parity estimate: **before 96% -> after 96%**

Completed work:

1. Routed the retained `SV_SteamStats_ResetSession` helper through the shared
   stats lifecycle logger so null-session skips and retained-session clears
   now surface the same provider/policy pair instead of clearing state
   silently inside the dedicated-server `GameServerStats` owner.
2. Kept the retained reset behavior intact: session memory still clears with
   the same recovered `Com_Memset` flow, while the new compatibility labels
   only document when the helper is skipping or clearing retained state.
3. Refreshed the focused platform-service regression coverage plus the
   platform-service abstraction and `RW-G01` gap note so the retained
   dedicated-server stats owner now documents the same explicit
   compatibility-labeling story across its request gate, session-bootstrap,
   client-slot, value-query gate, value-flush gate, session-reset helper,
   field-owner, achievement-owner, session-teardown, and publish/store
   lifecycle paths.

### Task A3az: Expose explicit provider/policy labeling through the retained dedicated-server stats descriptor lookup helpers [COMPLETED]
Priority: Critical
Primary areas: `src/code/server/sv_client.c`,
`tests/test_platform_services.py`, `docs/steam_platform_abstraction.md`,
`docs/reverse-engineering/source-file-gap-notes/rw-g01-platform-services.md`
Parity estimate: **before 96% -> after 96%**

Completed work:

1. Routed the retained `SV_SteamStats_GetFieldName` and
   `SV_SteamStats_GetAchievementName` helpers through the shared stats
   lifecycle logger so invalid and unmapped descriptor lookups now surface the
   same provider/policy pair instead of returning silently beneath the
   dedicated-server `GameServerStats` owner.
2. Kept the retained stats behavior intact: the same caller-specific query,
   flush, stat-delta, and achievement owner paths still short-circuit on
   missing descriptors, while the helper signatures now accept the active
   lifecycle stage so those compatibility labels stay contextual.
3. Refreshed the focused platform-service regression coverage plus the
   platform-service abstraction and `RW-G01` gap note so the retained
   dedicated-server stats owner now documents the same explicit
   compatibility-labeling story across its descriptor lookup helpers,
   request gate, session-bootstrap, client-slot, value-query gate,
   value-flush gate, session-reset helper, field-owner, achievement-owner,
   session-teardown, and publish/store lifecycle paths.

### Task A3ba: Expose explicit provider/policy labeling through the retained client rich-presence join callback null-payload guard [COMPLETED]
Priority: Critical
Primary areas: `src/code/client/cl_main.c`,
`tests/test_platform_services.py`, `docs/steam_platform_abstraction.md`,
`docs/reverse-engineering/source-file-gap-notes/rw-g01-platform-services.md`
Parity estimate: **before 96% -> after 96%**

Completed work:

1. Routed the retained `CL_Steam_Client_OnRichPresenceJoinRequested` null-event
   guard through the shared matchmaking callback logger so the compatibility
   lane now labels ignored null join payloads instead of silently returning.
2. Kept the retained callback handoff intact: non-null join payloads still
   flow through `CL_Steam_OnRichPresenceJoinRequested` without behavioral
   changes beyond the new compatibility labeling.
3. Refreshed the focused platform-service regression coverage plus the
   platform-service abstraction and `RW-G01` gap note so this client callback
   owner now documents the same explicit compatibility-labeling story.

### Task A3bb: Expose explicit provider/policy labeling through the retained client user-stats callback null-payload guard [COMPLETED]
Priority: Critical
Primary areas: `src/code/client/cl_main.c`,
`tests/test_platform_services.py`, `docs/steam_platform_abstraction.md`,
`docs/reverse-engineering/source-file-gap-notes/rw-g01-platform-services.md`
Parity estimate: **before 96% -> after 96%**

Completed work:

1. Routed the retained `CL_Steam_Client_OnUserStatsReceived` null-event guard
   through the shared stats callback logger so ignored null payloads now
   surface the active provider/policy pair instead of dropping silently.
2. Kept the retained stats browser-event behavior intact for non-null payloads:
   user-stat JSON publishing still follows the same recovered control flow.
3. Refreshed the focused platform-service regression coverage plus the
   platform-service abstraction and `RW-G01` gap note so this client callback
   owner now documents the same explicit compatibility-labeling story.

### Task A3bc: Expose explicit provider/policy labeling through the retained client persona callback null-payload guard [COMPLETED]
Priority: Critical
Primary areas: `src/code/client/cl_main.c`,
`tests/test_platform_services.py`, `docs/steam_platform_abstraction.md`,
`docs/reverse-engineering/source-file-gap-notes/rw-g01-platform-services.md`
Parity estimate: **before 96% -> after 96%**

Completed work:

1. Routed the retained `CL_Steam_Client_OnPersonaStateChange` null-event guard
   through the shared matchmaking callback logger so ignored null persona
   payloads no longer return silently.
2. Kept the retained persona browser-event behavior intact for non-null
   payloads: the same summary formatting and publish path still applies.
3. Refreshed the focused platform-service regression coverage plus the
   platform-service abstraction and `RW-G01` gap note so this client callback
   owner now documents the same explicit compatibility-labeling story.

### Task A3bd: Expose explicit provider/policy labeling through the retained client P2P-session callback null-payload guard [COMPLETED]
Priority: Critical
Primary areas: `src/code/client/cl_main.c`,
`tests/test_platform_services.py`, `docs/steam_platform_abstraction.md`,
`docs/reverse-engineering/source-file-gap-notes/rw-g01-platform-services.md`
Parity estimate: **before 96% -> after 96%**

Completed work:

1. Routed the retained `CL_Steam_Client_OnP2PSessionRequest` null-event guard
   through the shared matchmaking callback logger so ignored null session
   payloads no longer return silently.
2. Kept the retained accept/fail logging and `QL_Steamworks_AcceptP2PSession`
   behavior intact for non-null payloads.
3. Refreshed the focused platform-service regression coverage plus the
   platform-service abstraction and `RW-G01` gap note so this client callback
   owner now documents the same explicit compatibility-labeling story.

### Task A3be: Expose explicit provider/policy labeling through the retained client server-change callback null-payload guard [COMPLETED]
Priority: Critical
Primary areas: `src/code/client/cl_main.c`,
`tests/test_platform_services.py`, `docs/steam_platform_abstraction.md`,
`docs/reverse-engineering/source-file-gap-notes/rw-g01-platform-services.md`
Parity estimate: **before 96% -> after 96%**

Completed work:

1. Routed the retained `CL_Steam_Client_OnGameServerChangeRequested`
   null-event guard through the shared matchmaking callback logger so ignored
   null server-change payloads no longer return silently.
2. Kept the retained connect handoff intact: non-null payloads still flow
   through `CL_Steam_OnGameServerChangeRequested` without behavioral changes.
3. Refreshed the focused platform-service regression coverage plus the
   platform-service abstraction and `RW-G01` gap note so this client callback
   owner now documents the same explicit compatibility-labeling story.

### Task A3bf: Expose explicit provider/policy labeling through the retained client friend rich-presence callback null-payload guard [COMPLETED]
Priority: Critical
Primary areas: `src/code/client/cl_main.c`,
`tests/test_platform_services.py`, `docs/steam_platform_abstraction.md`,
`docs/reverse-engineering/source-file-gap-notes/rw-g01-platform-services.md`
Parity estimate: **before 96% -> after 96%**

Completed work:

1. Routed the retained `CL_Steam_Client_OnFriendRichPresenceUpdate`
   null-event guard through the shared matchmaking callback logger so ignored
   null rich-presence payloads no longer return silently.
2. Kept the retained friend-summary formatting and browser-event publishing
   intact for non-null payloads.
3. Refreshed the focused platform-service regression coverage plus the
   platform-service abstraction and `RW-G01` gap note so this client callback
   owner now documents the same explicit compatibility-labeling story.

### Task A3bg: Expose explicit provider/policy labeling through the retained client UGC-query callback null-payload guard [COMPLETED]
Priority: Critical
Primary areas: `src/code/client/cl_main.c`,
`tests/test_platform_services.py`, `docs/steam_platform_abstraction.md`,
`docs/reverse-engineering/source-file-gap-notes/rw-g01-platform-services.md`
Parity estimate: **before 96% -> after 96%**

Completed work:

1. Routed the retained `CL_Steam_Client_OnUGCQueryCompleted` null-event guard
   through the shared workshop lifecycle logger so ignored null query payloads
   no longer return silently.
2. Kept the retained UGC result/failure browser-event publishing intact for
   non-null payloads.
3. Refreshed the focused platform-service regression coverage plus the
   platform-service abstraction and `RW-G01` gap note so this client callback
   owner now documents the same explicit compatibility-labeling story.

### Task A3bh: Expose explicit provider/policy labeling through the retained client lobby-created callback null-payload guard [COMPLETED]
Priority: Critical
Primary areas: `src/code/client/cl_main.c`,
`tests/test_platform_services.py`, `docs/steam_platform_abstraction.md`,
`docs/reverse-engineering/source-file-gap-notes/rw-g01-platform-services.md`
Parity estimate: **before 96% -> after 96%**

Completed work:

1. Routed the retained `CL_Steam_Lobby_OnLobbyCreated` null-event guard
   through the shared matchmaking callback logger so ignored null lobby-create
   payloads no longer return silently.
2. Kept the retained success/error lobby browser-event publishing intact for
   non-null payloads.
3. Refreshed the focused platform-service regression coverage plus the
   platform-service abstraction and `RW-G01` gap note so this client callback
   owner now documents the same explicit compatibility-labeling story.

### Task A3bi: Expose explicit provider/policy labeling through the retained client lobby-enter callback null-payload guard [COMPLETED]
Priority: Critical
Primary areas: `src/code/client/cl_main.c`,
`tests/test_platform_services.py`, `docs/steam_platform_abstraction.md`,
`docs/reverse-engineering/source-file-gap-notes/rw-g01-platform-services.md`
Parity estimate: **before 96% -> after 96%**

Completed work:

1. Routed the retained `CL_Steam_Lobby_OnLobbyEnter` null-event guard through
   the shared matchmaking callback logger so ignored null lobby-enter payloads
   no longer return silently.
2. Kept the retained lobby-enter success/error publishing and current-lobby
   tracking intact for non-null payloads.
3. Refreshed the focused platform-service regression coverage plus the
   platform-service abstraction and `RW-G01` gap note so this client callback
   owner now documents the same explicit compatibility-labeling story.

### Task A3bj: Expose explicit provider/policy labeling through the retained client lobby-chat-update callback null-payload guard [COMPLETED]
Priority: Critical
Primary areas: `src/code/client/cl_main.c`,
`tests/test_platform_services.py`, `docs/steam_platform_abstraction.md`,
`docs/reverse-engineering/source-file-gap-notes/rw-g01-platform-services.md`
Parity estimate: **before 96% -> after 96%**

Completed work:

1. Routed the retained `CL_Steam_Lobby_OnLobbyChatUpdate` null-event guard
   through the shared matchmaking callback logger so ignored null lobby-chat
   payloads no longer return silently.
2. Kept the retained user-summary formatting and join/leave browser-event
   publishing intact for non-null payloads.
3. Refreshed the focused platform-service regression coverage plus the
   platform-service abstraction and `RW-G01` gap note so this client callback
   owner now documents the same explicit compatibility-labeling story.

### Task A3bk: Expose explicit provider/policy labeling through the retained client lobby-chat-message callback null-payload guard [COMPLETED]
Priority: Critical
Primary areas: `src/code/client/cl_main.c`,
`tests/test_platform_services.py`, `docs/steam_platform_abstraction.md`,
`docs/reverse-engineering/source-file-gap-notes/rw-g01-platform-services.md`
Parity estimate: **before 96% -> after 96%**

Completed work:

1. Routed the retained `CL_Steam_Lobby_OnLobbyChatMessage` null-event guard
   through the shared matchmaking callback logger so ignored null lobby-chat
   message payloads no longer return silently.
2. Kept the retained friend-summary lookup, JSON escaping, and browser-event
   publishing intact for non-null payloads.
3. Refreshed the focused platform-service regression coverage plus the
   platform-service abstraction and `RW-G01` gap note so this client callback
   owner now documents the same explicit compatibility-labeling story.

### Task A3bl: Expose explicit provider/policy labeling through the retained client lobby-data-update callback null-payload guard [COMPLETED]
Priority: Critical
Primary areas: `src/code/client/cl_main.c`,
`tests/test_platform_services.py`, `docs/steam_platform_abstraction.md`,
`docs/reverse-engineering/source-file-gap-notes/rw-g01-platform-services.md`
Parity estimate: **before 96% -> after 96%**

Completed work:

1. Routed the retained `CL_Steam_Lobby_OnLobbyDataUpdate` null-event guard
   through the shared matchmaking callback logger so ignored null lobby-data
   update payloads no longer return silently.
2. Kept the retained lobby/member detail formatting and browser-event
   publishing intact for non-null payloads.
3. Refreshed the focused platform-service regression coverage plus the
   platform-service abstraction and `RW-G01` gap note so this client callback
   owner now documents the same explicit compatibility-labeling story.

### Task A3bm: Expose explicit provider/policy labeling through the retained client lobby-game-created callback null-payload guard [COMPLETED]
Priority: Critical
Primary areas: `src/code/client/cl_main.c`,
`tests/test_platform_services.py`, `docs/steam_platform_abstraction.md`,
`docs/reverse-engineering/source-file-gap-notes/rw-g01-platform-services.md`
Parity estimate: **before 96% -> after 96%**

Completed work:

1. Routed the retained `CL_Steam_Lobby_OnLobbyGameCreated` null-event guard
   through the shared matchmaking callback logger so ignored null lobby-game
   created payloads no longer return silently.
2. Kept the retained game-server detail formatting and browser-event
   publishing intact for non-null payloads.
3. Refreshed the focused platform-service regression coverage plus the
   platform-service abstraction and `RW-G01` gap note so this client callback
   owner now documents the same explicit compatibility-labeling story.

### Task A3bn: Expose explicit provider/policy labeling through the retained client lobby-kicked callback null-payload guard [COMPLETED]
Priority: Critical
Primary areas: `src/code/client/cl_main.c`,
`tests/test_platform_services.py`, `docs/steam_platform_abstraction.md`,
`docs/reverse-engineering/source-file-gap-notes/rw-g01-platform-services.md`
Parity estimate: **before 96% -> after 96%**

Completed work:

1. Routed the retained `CL_Steam_Lobby_OnLobbyKicked` null-event guard through
   the shared matchmaking callback logger so ignored null lobby-kicked
   payloads no longer return silently.
2. Kept the retained current-lobby clearing, detail formatting, and
   browser-event publishing intact for non-null payloads.
3. Refreshed the focused platform-service regression coverage plus the
   platform-service abstraction and `RW-G01` gap note so this client callback
   owner now documents the same explicit compatibility-labeling story.

### Task A3bo: Expose explicit provider/policy labeling through the retained client lobby-join-requested callback null-payload guard [COMPLETED]
Priority: Critical
Primary areas: `src/code/client/cl_main.c`,
`tests/test_platform_services.py`, `docs/steam_platform_abstraction.md`,
`docs/reverse-engineering/source-file-gap-notes/rw-g01-platform-services.md`
Parity estimate: **before 96% -> after 96%**

Completed work:

1. Routed the retained `CL_Steam_Lobby_OnGameLobbyJoinRequested` null-event
   guard through the shared matchmaking callback logger so ignored null
   join-requested payloads no longer return silently.
2. Kept the retained lobby/friend detail formatting and browser-event
   publishing intact for non-null payloads.
3. Refreshed the focused platform-service regression coverage plus the
   platform-service abstraction and `RW-G01` gap note so this client callback
   owner now documents the same explicit compatibility-labeling story.

### Task A3bp: Expose explicit provider/policy labeling through the retained client microtransaction authorization callback null-payload guard [COMPLETED]
Priority: Critical
Primary areas: `src/code/client/cl_main.c`,
`tests/test_platform_services.py`, `docs/steam_platform_abstraction.md`,
`docs/reverse-engineering/source-file-gap-notes/rw-g01-platform-services.md`
Parity estimate: **before 96% -> after 96%**

Completed work:

1. Routed the retained `CL_Steam_Micro_OnAuthorizationResponse` null-event
   guard through the shared microtransaction callback logger so ignored null
   authorization payloads no longer return silently.
2. Kept the retained purchase payload formatting and browser-event publishing
   intact for non-null payloads while extending the logger to spell out the
   null-payload compatibility path.
3. Refreshed the focused platform-service regression coverage plus the
   platform-service abstraction and `RW-G01` gap note so this client callback
   owner now documents the same explicit compatibility-labeling story.

### Task A3bq: Expose explicit provider/policy labeling through the retained client workshop item-installed callback null-payload guard [COMPLETED]
Priority: Critical
Primary areas: `src/code/client/cl_main.c`,
`tests/test_platform_services.py`, `docs/steam_platform_abstraction.md`,
`docs/reverse-engineering/source-file-gap-notes/rw-g01-platform-services.md`
Parity estimate: **before 96% -> after 96%**

Completed work:

1. Routed the retained `CL_Steam_Workshop_OnItemInstalled` null-event guard
   through the shared workshop lifecycle logger so ignored null item-installed
   payloads no longer return silently.
2. Kept the retained app-id validation, item lookup, and install-finalization
   behavior intact for non-null payloads.
3. Refreshed the focused platform-service regression coverage plus the
   platform-service abstraction and `RW-G01` gap note so this client callback
   owner now documents the same explicit compatibility-labeling story.

### Task A3br: Expose explicit provider/policy labeling through the retained client workshop item-installed inactive-download-state guard [COMPLETED]
Priority: Critical
Primary areas: `src/code/client/cl_main.c`,
`tests/test_platform_services.py`, `docs/steam_platform_abstraction.md`,
`docs/reverse-engineering/source-file-gap-notes/rw-g01-platform-services.md`
Parity estimate: **before 96% -> after 96%**

Completed work:

1. Routed the retained `CL_Steam_Workshop_OnItemInstalled` inactive-download
   guard through the shared workshop lifecycle logger so compatibility-owned
   installed callbacks now explain why no active download state can consume
   them.
2. Kept the retained unexpected-app-id, untracked-item, and install-complete
   handling intact once a live download state exists.
3. Refreshed the focused platform-service regression coverage plus the
   platform-service abstraction and `RW-G01` gap note so this workshop
   callback guard now documents the same explicit compatibility-labeling story.

### Task A3bs: Expose explicit provider/policy labeling through the retained client workshop download-result callback null-payload guard [COMPLETED]
Priority: Critical
Primary areas: `src/code/client/cl_main.c`,
`tests/test_platform_services.py`, `docs/steam_platform_abstraction.md`,
`docs/reverse-engineering/source-file-gap-notes/rw-g01-platform-services.md`
Parity estimate: **before 96% -> after 96%**

Completed work:

1. Routed the retained `CL_Steam_Workshop_OnDownloadItemResult` null-event
   guard through the shared workshop lifecycle logger so ignored null
   download-result payloads no longer return silently.
2. Kept the retained app-id validation, active-item matching, and
   success/failure completion handling intact for non-null payloads.
3. Refreshed the focused platform-service regression coverage plus the
   platform-service abstraction and `RW-G01` gap note so this workshop
   callback owner now documents the same explicit compatibility-labeling
   story.

### Task A3bt: Expose explicit provider/policy labeling through the retained client workshop download-result inactive-lane guards [COMPLETED]
Priority: Critical
Primary areas: `src/code/client/cl_main.c`,
`tests/test_platform_services.py`, `docs/steam_platform_abstraction.md`,
`docs/reverse-engineering/source-file-gap-notes/rw-g01-platform-services.md`
Parity estimate: **before 96% -> after 96%**

Completed work:

1. Routed the retained `CL_Steam_Workshop_OnDownloadItemResult`
   inactive-download-state and active-item-index guards through the shared
   workshop lifecycle logger so compatibility-owned download callbacks now
   explain why no active lane can consume them.
2. Kept the retained unexpected-app-id, inactive-item, and
   success/failure-completion handling intact once a live download lane exists.
3. Refreshed the focused platform-service regression coverage plus the
   platform-service abstraction and `RW-G01` gap note so these workshop guard
   exits now document the same explicit compatibility-labeling story.

### Task A3bu: Expose explicit provider/policy labeling through the retained dedicated-server connect-failure callback null-payload guard [COMPLETED]
Priority: Critical
Primary areas: `src/code/server/sv_client.c`,
`tests/test_platform_services.py`, `docs/steam_platform_abstraction.md`,
`docs/reverse-engineering/source-file-gap-notes/rw-g01-platform-services.md`
Parity estimate: **before 96% -> after 96%**

Completed work:

1. Routed the retained `SV_SteamServerConnectFailureCallback` null-event guard
   through the shared server-callback lifecycle logger so ignored null
   connect-failure payloads no longer return silently.
2. Kept the retained connected-flag clear and failure-result formatting intact
   for non-null payloads.
3. Refreshed the focused platform-service regression coverage plus the
   platform-service abstraction and `RW-G01` gap note so this dedicated-server
   callback owner now documents the same explicit compatibility-labeling story.

### Task A3bv: Expose explicit provider/policy labeling through the retained dedicated-server disconnected callback null-payload guard [COMPLETED]
Priority: Critical
Primary areas: `src/code/server/sv_client.c`,
`tests/test_platform_services.py`, `docs/steam_platform_abstraction.md`,
`docs/reverse-engineering/source-file-gap-notes/rw-g01-platform-services.md`
Parity estimate: **before 96% -> after 96%**

Completed work:

1. Routed the retained `SV_SteamServerDisconnectedCallback` null-event guard
   through the shared server-callback lifecycle logger so ignored null
   disconnect payloads no longer return silently.
2. Kept the retained connected-flag clear and disconnect-result formatting
   intact for non-null payloads.
3. Refreshed the focused platform-service regression coverage plus the
   platform-service abstraction and `RW-G01` gap note so this dedicated-server
   callback owner now documents the same explicit compatibility-labeling story.

### Task A3bw: Expose explicit provider/policy labeling through the retained dedicated-server auth-ticket callback null-payload guard [COMPLETED]
Priority: Critical
Primary areas: `src/code/server/sv_client.c`,
`tests/test_platform_services.py`, `docs/steam_platform_abstraction.md`,
`docs/reverse-engineering/source-file-gap-notes/rw-g01-platform-services.md`
Parity estimate: **before 96% -> after 96%**

Completed work:

1. Routed the retained `SV_SteamServerValidateAuthTicketResponseCallback`
   null-event guard through the shared server-callback lifecycle logger so
   ignored null auth-ticket payloads no longer return silently.
2. Kept the retained fake-VAC override, auth-state publication, and
   accept/drop handling intact for non-null payloads.
3. Refreshed the focused platform-service regression coverage plus the
   platform-service abstraction and `RW-G01` gap note so this dedicated-server
   callback owner now documents the same explicit compatibility-labeling story.

### Task A3bx: Expose explicit provider/policy labeling through the retained dedicated-server auth-ticket missing-client guard [COMPLETED]
Priority: Critical
Primary areas: `src/code/server/sv_client.c`,
`tests/test_platform_services.py`, `docs/steam_platform_abstraction.md`,
`docs/reverse-engineering/source-file-gap-notes/rw-g01-platform-services.md`
Parity estimate: **before 96% -> after 96%**

Completed work:

1. Routed the retained `SV_SteamServerValidateAuthTicketResponseCallback`
   missing-client guard through the shared server-callback lifecycle logger so
   auth responses for no-longer-tracked clients no longer return silently.
2. Kept the retained client lookup and finalise/drop behavior intact once one
   live client session still owns the callback.
3. Refreshed the focused platform-service regression coverage plus the
   platform-service abstraction and `RW-G01` gap note so this dedicated-server
   callback owner now documents the same explicit compatibility-labeling story.

### Task A3by: Expose explicit provider/policy labeling through the retained dedicated-server P2P-session-request callback null-payload guard [COMPLETED]
Priority: Critical
Primary areas: `src/code/server/sv_client.c`,
`tests/test_platform_services.py`, `docs/steam_platform_abstraction.md`,
`docs/reverse-engineering/source-file-gap-notes/rw-g01-platform-services.md`
Parity estimate: **before 96% -> after 96%**

Completed work:

1. Routed the retained `SV_SteamServerP2PSessionRequestCallback` null-event
   guard through the shared P2P-session lifecycle logger so ignored null
   session-request payloads no longer return silently.
2. Kept the retained client lookup, auth gate, and accept-call failure
   handling intact for non-null payloads.
3. Refreshed the focused platform-service regression coverage plus the
   platform-service abstraction and `RW-G01` gap note so this dedicated-server
   callback owner now documents the same explicit compatibility-labeling story.

### Task A3bz: Expose explicit provider/policy labeling through the Steamworks servers-connected dispatch guard [COMPLETED]
Priority: Critical
Primary areas: `src/common/platform/platform_steamworks.c`,
`tests/test_platform_services.py`, `docs/steam_platform_abstraction.md`,
`docs/reverse-engineering/source-file-gap-notes/rw-g01-platform-services.md`
Parity estimate: **before 96% -> after 96%**

Completed work:

1. Added a shared `QL_Steamworks_LogServerCallbackDispatch` helper and routed
   the retained `QL_Steamworks_DispatchServersConnected` missing-state and
   missing-binding guards through it so that dispatcher no longer returns
   silently.
2. Kept the retained zeroed event bootstrap and callback invocation intact
   once one registered dispatch target exists.
3. Refreshed the focused platform-service regression coverage plus the
   platform-service abstraction and `RW-G01` gap note so this dispatcher guard
   now documents the same explicit compatibility-labeling story.

### Task A3ca: Expose explicit provider/policy labeling through the Steamworks connect-failure dispatch guards [COMPLETED]
Priority: Critical
Primary areas: `src/common/platform/platform_steamworks.c`,
`tests/test_platform_services.py`, `docs/steam_platform_abstraction.md`,
`docs/reverse-engineering/source-file-gap-notes/rw-g01-platform-services.md`
Parity estimate: **before 96% -> after 96%**

Completed work:

1. Routed the retained `QL_Steamworks_DispatchServerConnectFailure`
   missing-state, missing-binding, and missing-payload guards through the
   shared server-dispatch logger so that dispatcher no longer returns
   silently.
2. Kept the retained raw-event translation and callback invocation intact once
   one valid dispatch surface and payload exist.
3. Refreshed the focused platform-service regression coverage plus the
   platform-service abstraction and `RW-G01` gap note so these dispatcher
   guards now document the same explicit compatibility-labeling story.

### Task A3cb: Expose explicit provider/policy labeling through the Steamworks disconnected dispatch guards [COMPLETED]
Priority: Critical
Primary areas: `src/common/platform/platform_steamworks.c`,
`tests/test_platform_services.py`, `docs/steam_platform_abstraction.md`,
`docs/reverse-engineering/source-file-gap-notes/rw-g01-platform-services.md`
Parity estimate: **before 96% -> after 96%**

Completed work:

1. Routed the retained `QL_Steamworks_DispatchServersDisconnected`
   missing-state, missing-binding, and missing-payload guards through the
   shared server-dispatch logger so that dispatcher no longer returns
   silently.
2. Kept the retained raw-event translation and callback invocation intact once
   one valid dispatch surface and payload exist.
3. Refreshed the focused platform-service regression coverage plus the
   platform-service abstraction and `RW-G01` gap note so these dispatcher
   guards now document the same explicit compatibility-labeling story.

### Task A3cc: Expose explicit provider/policy labeling through the Steamworks auth-ticket dispatch guards [COMPLETED]
Priority: Critical
Primary areas: `src/common/platform/platform_steamworks.c`,
`tests/test_platform_services.py`, `docs/steam_platform_abstraction.md`,
`docs/reverse-engineering/source-file-gap-notes/rw-g01-platform-services.md`
Parity estimate: **before 96% -> after 96%**

Completed work:

1. Routed the retained `QL_Steamworks_DispatchValidateAuthTicketResponse`
   missing-state, missing-binding, and missing-payload guards through the
   shared server-dispatch logger so that dispatcher no longer returns
   silently.
2. Kept the retained raw auth-ticket response translation and callback
   invocation intact once one valid dispatch surface and payload exist.
3. Refreshed the focused platform-service regression coverage plus the
   platform-service abstraction and `RW-G01` gap note so these dispatcher
   guards now document the same explicit compatibility-labeling story.

### Task A3cd: Expose explicit provider/policy labeling through the Steamworks P2P-session-request dispatch guards [COMPLETED]
Priority: Critical
Primary areas: `src/common/platform/platform_steamworks.c`,
`tests/test_platform_services.py`, `docs/steam_platform_abstraction.md`,
`docs/reverse-engineering/source-file-gap-notes/rw-g01-platform-services.md`
Parity estimate: **before 96% -> after 96%**

Completed work:

1. Routed the retained `QL_Steamworks_DispatchServerP2PSessionRequest`
   missing-state, missing-binding, and missing-payload guards through the
   shared server-dispatch logger so that dispatcher no longer returns
   silently.
2. Kept the retained raw P2P-session translation and callback invocation
   intact once one valid dispatch surface and payload exist.
3. Refreshed the focused platform-service regression coverage plus the
   platform-service abstraction and `RW-G01` gap note so these dispatcher
   guards now document the same explicit compatibility-labeling story.

### Task A3ce: Restore the retail direct-request workshop detail string [COMPLETED]
Priority: Critical
Primary areas: `src/code/client/cl_main.c`, `tests/test_platform_services.py`,
`docs/steam_platform_abstraction.md`,
`docs/reverse-engineering/source-file-gap-notes/rw-g01-platform-services.md`
Parity estimate: **before 96% -> after 96%**

Completed work:

1. Updated the retained client workshop direct-request lane so it now reuses
   the retail-observed `Workshop item %llu: requesting download.` detail.
2. Kept the existing compatibility wrapper ownership and queue-state updates
   intact around that retail string restoration.
3. Refreshed the focused regression coverage and the matching abstraction/gap
   notes for the workshop request lane.

### Task A3cf: Restore the retail queued-request workshop detail string [COMPLETED]
Priority: Critical
Primary areas: `src/code/client/cl_main.c`, `tests/test_platform_services.py`,
`docs/steam_platform_abstraction.md`,
`docs/reverse-engineering/source-file-gap-notes/rw-g01-platform-services.md`
Parity estimate: **before 96% -> after 96%**

Completed work:

1. Updated the retained client workshop bootstrap queueing lane so it now
   reuses the retail-observed `Workshop item %llu: queueing download.` detail.
2. Kept the existing deferred-download state model intact around that retail
   string restoration.
3. Refreshed the focused regression coverage and the matching abstraction/gap
   notes for the queued-request lane.

### Task A3cg: Restore the retail workshop cache-hit detail string [COMPLETED]
Priority: Critical
Primary areas: `src/code/client/cl_main.c`, `tests/test_platform_services.py`,
`docs/steam_platform_abstraction.md`,
`docs/reverse-engineering/source-file-gap-notes/rw-g01-platform-services.md`
Parity estimate: **before 96% -> after 96%**

Completed work:

1. Updated the retained client workshop bootstrap cache-hit lane so it now
   reuses the retail-observed `Workshop item %llu: in cache.` detail.
2. Kept the existing cached-item completion handling intact around that retail
   string restoration.
3. Refreshed the focused regression coverage and the matching abstraction/gap
   notes for the cache-hit lane.

### Task A3ch: Restore the retail queued-handoff workshop detail string [COMPLETED]
Priority: Critical
Primary areas: `src/code/client/cl_main.c`, `tests/test_platform_services.py`,
`docs/steam_platform_abstraction.md`,
`docs/reverse-engineering/source-file-gap-notes/rw-g01-platform-services.md`
Parity estimate: **before 96% -> after 96%**

Completed work:

1. Updated the retained client workshop queue-advance lane so it now reuses
   the retail-observed `Workshop item %llu: was queued, requesting download.`
   detail.
2. Kept the existing queue-advance ownership and state updates intact around
   that retail string restoration.
3. Refreshed the focused regression coverage and the matching abstraction/gap
   notes for the queued handoff lane.

### Task A3ci: Restore the retail workshop completion detail string [COMPLETED]
Priority: Critical
Primary areas: `src/code/client/cl_main.c`, `tests/test_platform_services.py`,
`docs/steam_platform_abstraction.md`,
`docs/reverse-engineering/source-file-gap-notes/rw-g01-platform-services.md`
Parity estimate: **before 96% -> after 96%**

Completed work:

1. Updated the retained client workshop active-item completion lane so it now
   reuses the retail-observed `Steamworks download complete: %llu` detail.
2. Kept the existing active-download clear path intact around that retail
   string restoration.
3. Refreshed the focused regression coverage and the matching abstraction/gap
   notes for the workshop completion lane.

### Task A3cj: Restore the retail workshop queue-complete detail string [COMPLETED]
Priority: Critical
Primary areas: `src/code/client/cl_main.c`, `tests/test_platform_services.py`,
`docs/steam_platform_abstraction.md`,
`docs/reverse-engineering/source-file-gap-notes/rw-g01-platform-services.md`
Parity estimate: **before 96% -> after 96%**

Completed work:

1. Updated the retained client workshop queue-settled lane so it now reuses
   the retail-observed `Download completed for all steamworks items` detail.
2. Kept the existing queue-active reset behavior intact around that retail
   string restoration.
3. Refreshed the focused regression coverage and the matching abstraction/gap
   notes for the queue-complete lane.

### Task A3ck: Restore the retail workshop invalid-app skip detail in the item-installed callback [COMPLETED]
Priority: Critical
Primary areas: `src/code/client/cl_main.c`, `tests/test_platform_services.py`,
`docs/steam_platform_abstraction.md`,
`docs/reverse-engineering/source-file-gap-notes/rw-g01-platform-services.md`
Parity estimate: **before 96% -> after 96%**

Completed work:

1. Updated the retained client workshop item-installed invalid-app guard so it
   now reuses the retail-observed `OnDownloadItemResult skip, invalid app id
   %d` detail.
2. Kept the existing compatibility wrapper ownership intact around that
   observed retail string restoration.
3. Refreshed the focused regression coverage and the matching abstraction/gap
   notes for the item-installed invalid-app guard.

### Task A3cl: Restore the retail workshop invalid-app skip detail in the download-result callback [COMPLETED]
Priority: Critical
Primary areas: `src/code/client/cl_main.c`, `tests/test_platform_services.py`,
`docs/steam_platform_abstraction.md`,
`docs/reverse-engineering/source-file-gap-notes/rw-g01-platform-services.md`
Parity estimate: **before 96% -> after 96%**

Completed work:

1. Updated the retained client workshop download-result invalid-app guard so
   it now reuses the retail-observed `OnDownloadItemResult skip, invalid app
   id %d` detail.
2. Kept the existing callback wrapper ownership intact around that retail
   string restoration.
3. Refreshed the focused regression coverage and the matching abstraction/gap
   notes for the download-result invalid-app guard.

### Task A3cm: Restore the retail workshop active-download skip detail [COMPLETED]
Priority: Critical
Primary areas: `src/code/client/cl_main.c`, `tests/test_platform_services.py`,
`docs/steam_platform_abstraction.md`,
`docs/reverse-engineering/source-file-gap-notes/rw-g01-platform-services.md`
Parity estimate: **before 96% -> after 96%**

Completed work:

1. Updated the retained client workshop active-download mismatch guard so it
   now reuses the retail-observed `OnDownloadItemResult skip, not the active
   download %llu` detail.
2. Kept the existing active-item comparison and early-return behavior intact
   around that retail string restoration.
3. Refreshed the focused regression coverage and the matching abstraction/gap
   notes for the active-download skip lane.

### Task A3cn: Restore the retail workshop failure-result detail string [COMPLETED]
Priority: Critical
Primary areas: `src/code/client/cl_main.c`, `tests/test_platform_services.py`,
`docs/steam_platform_abstraction.md`,
`docs/reverse-engineering/source-file-gap-notes/rw-g01-platform-services.md`
Parity estimate: **before 96% -> after 96%**

Completed work:

1. Updated the retained client workshop download-result failure lane so it now
   reuses the retail-observed `Download item %llu failed with EResult code %i`
   detail.
2. Kept the existing failure-state and queue-advance behavior intact around
   that retail string restoration.
3. Refreshed the focused regression coverage and the matching abstraction/gap
   notes for the failure-result lane.

### Task A3co: Restore the retail workshop missing-`pak00.pk3` warning [COMPLETED]
Priority: Critical
Primary areas: `src/code/qcommon/files.c`, `tests/test_platform_services.py`,
`docs/steam_platform_abstraction.md`,
`docs/reverse-engineering/source-file-gap-notes/rw-g01-platform-services.md`
Parity estimate: **before 96% -> after 96%**

Completed work:

1. Updated the filesystem-side workshop startup lane so it now reuses the
   retail-observed `WARNING: Skipping workshop PK3s since pak00 doesn't
   exist.` detail.
2. Kept the retained workshop mount pass active after that warning, matching
   the retail mount-mode toggle instead of turning the warning into a hard
   return.
3. Refreshed the focused regression coverage and the matching abstraction/gap
   notes for the missing-`pak00.pk3` guard.

### Task A3cp: Restore the retail `fs_skipWorkshop` skip detail [COMPLETED]
Priority: Critical
Primary areas: `src/code/qcommon/files.c`, `tests/test_platform_services.py`,
`docs/steam_platform_abstraction.md`,
`docs/reverse-engineering/source-file-gap-notes/rw-g01-platform-services.md`
Parity estimate: **before 96% -> after 96%**

Completed work:

1. Updated the filesystem-side workshop startup lane so the
   `fs_skipWorkshop` gate now reuses the retail-observed `Skipping workshop
   since fs_skipWorkshop is set.` detail.
2. Kept the existing early-return ownership intact around that exact retail
   string restoration.
3. Refreshed the focused regression coverage and the matching abstraction/gap
   notes for the `fs_skipWorkshop` gate.

### Task A3cq: Restore the retail workshop build-mode skip detail [COMPLETED]
Priority: Critical
Primary areas: `src/code/qcommon/files.c`, `tests/test_platform_services.py`,
`docs/steam_platform_abstraction.md`,
`docs/reverse-engineering/source-file-gap-notes/rw-g01-platform-services.md`
Parity estimate: **before 96% -> after 96%**

Completed work:

1. Updated the filesystem-side workshop startup lane so the retained
   `com_build`/`com_buildScript` gate now reuses the retail-observed
   `Skipping workshop since running in build mode.` detail.
2. Kept the existing build-mode early return intact around that retail string
   restoration.
3. Refreshed the focused regression coverage and the matching abstraction/gap
   notes for the build-mode gate.

### Task A3cr: Restore the retail null-`ISteamUGC` skip detail [COMPLETED]
Priority: Critical
Primary areas: `src/code/qcommon/files.c`,
`src/common/platform/platform_steamworks.c`,
`src/common/platform/platform_steamworks.h`,
`tests/test_platform_services.py`,
`docs/steam_platform_abstraction.md`,
`docs/reverse-engineering/source-file-gap-notes/rw-g01-platform-services.md`
Parity estimate: **before 96% -> after 96%**

Completed work:

1. Updated the filesystem-side workshop startup lane so it now reuses the
   retail-observed `WARNING: Skipping workshop, ISteamUGC is NULL.` detail.
2. Kept the existing early-return behavior intact while splitting the null
   interface case away from the zero-subscribed-items case.
3. Refreshed the focused regression coverage and the matching abstraction/gap
   notes for the null-`ISteamUGC` guard.

### Task A3cs: Expose the exact workshop UGC-availability helper [COMPLETED]
Priority: Critical
Primary areas: `src/common/platform/platform_steamworks.c`,
`src/common/platform/platform_steamworks.h`,
`tests/test_platform_services.py`
Parity estimate: **before 96% -> after 96%**

Completed work:

1. Added `QL_Steamworks_HasUGCInterface()` so the retained workshop startup
   lane can distinguish a null `ISteamUGC` owner from an empty subscription
   list.
2. Kept the helper thin by routing it straight through the retained
   `QL_Steamworks_GetUGCInterface()` owner.
3. Refreshed the focused regression coverage for the new availability helper.

### Task A3ct: Restore the retail basepath-only `pak00.pk3` probe [COMPLETED]
Priority: Critical
Primary areas: `src/code/qcommon/files.c`, `tests/test_platform_services.py`
Parity estimate: **before 96% -> after 96%**

Completed work:

1. Updated `FS_HasBasePak0` so it now mirrors the retail
   `fs_basepath/baseq3/pak00.pk3` probe instead of scanning the broader local
   root set.
2. Kept the helper bounded to the workshop startup gate, matching the retail
   `SteamWorkshop_Init` ownership.
3. Refreshed the focused regression coverage for the basepath-only probe.

### Task A3cu: Restore the retail workshop raw-path mount toggle [COMPLETED]
Priority: Critical
Primary areas: `src/code/qcommon/files.c`, `tests/test_platform_services.py`
Parity estimate: **before 96% -> after 96%**

Completed work:

1. Updated the workshop mount pass so it now forwards the retained
   `mountRawPath` flag into `FS_AddGameDirectoryInternal` instead of always
   forcing the raw-path lane.
2. Mirrored the retail rule where the flag depends on whether `pak00.pk3` was
   present when workshop startup began.
3. Refreshed the focused regression coverage for the mount-mode toggle.

### Task A3cv: Restore the retail manual workshop direct-download detail [COMPLETED]
Priority: Critical
Primary areas: `src/code/server/sv_ccmds.c`,
`tests/test_platform_services.py`,
`tests/test_engine_operator_command_parity.py`,
`docs/steam_platform_abstraction.md`,
`docs/reverse-engineering/source-file-gap-notes/rw-g01-platform-services.md`
Parity estimate: **before 96% -> after 96%**

Completed work:

1. Updated the retained `steam_downloadugc` immediate-request lane so it now
   reuses the retail-observed `Workshop item %llu: download` detail.
2. Kept the existing provider/policy-aware operator logger intact around that
   exact retail string restoration.
3. Refreshed the focused regression coverage and the matching abstraction/gap
   notes for the direct-download lane.

### Task A3cw: Restore the retail manual workshop cache-hit detail [COMPLETED]
Priority: Critical
Primary areas: `src/code/server/sv_ccmds.c`,
`tests/test_platform_services.py`,
`tests/test_engine_operator_command_parity.py`,
`docs/steam_platform_abstraction.md`,
`docs/reverse-engineering/source-file-gap-notes/rw-g01-platform-services.md`
Parity estimate: **before 96% -> after 96%**

Completed work:

1. Updated the retained `steam_downloadugc` cache-hit lane so it now reuses
   the retail-observed `Workshop item %llu: in cache.` detail.
2. Kept the existing immediate-return ownership intact around that retail
   string restoration.
3. Refreshed the focused regression coverage and the matching abstraction/gap
   notes for the manual cache-hit lane.

### Task A3cx: Remove the non-retail manual download failure-only diagnostic [COMPLETED]
Priority: Critical
Primary areas: `src/code/server/sv_ccmds.c`,
`tests/test_platform_services.py`,
`tests/test_engine_operator_command_parity.py`,
`docs/steam_platform_abstraction.md`,
`docs/reverse-engineering/source-file-gap-notes/rw-g01-platform-services.md`
Parity estimate: **before 96% -> after 96%**

Completed work:

1. Updated the retained `steam_downloadugc` immediate-request lane so it no
   longer emits the extra compatibility-only `download request failed`
   diagnostic that retail never printed.
2. Kept the existing command registration and provider-gated command surface
   intact while mirroring the retail immediate-request call shape more closely.
3. Refreshed the focused regression coverage and the matching abstraction/gap
   notes for the removed non-retail failure-only diagnostic.

### Task A3cy: Remove the non-retail client workshop request-failure gate [COMPLETED]
Priority: Critical
Primary areas: `src/code/client/cl_main.c`, `tests/test_platform_services.py`,
`docs/steam_platform_abstraction.md`,
`docs/reverse-engineering/source-file-gap-notes/rw-g01-platform-services.md`
Parity estimate: **before 96% -> after 96%**

Completed work:

1. Updated `CL_Workshop_StartDownload` so it now ignores the raw
   `QL_Steamworks_DownloadItem` return value like the retail
   `SteamWorkshop_RequestDownload` owner.
2. Kept the existing queue-state and active-item updates intact around that
   control-flow restoration.
3. Refreshed the focused regression coverage and the matching abstraction/gap
   notes for the removed client request-failure gate.

### Task A3cz: Remove the non-retail client workshop request-failure detail [COMPLETED]
Priority: Critical
Primary areas: `src/code/client/cl_main.c`, `tests/test_platform_services.py`,
`docs/steam_platform_abstraction.md`,
`docs/reverse-engineering/source-file-gap-notes/rw-g01-platform-services.md`
Parity estimate: **before 96% -> after 96%**

Completed work:

1. Removed the extra `item %llu download request failed` detail from
   `CL_Workshop_StartDownload`, which retail never printed.
2. Kept the retained retail request strings unchanged around that removal.
3. Refreshed the focused regression coverage and the matching abstraction/gap
   notes for the removed request-failure detail.

### Task A3da: Remove the duplicate client workshop failure trace [COMPLETED]
Priority: Critical
Primary areas: `src/code/client/cl_main.c`, `tests/test_platform_services.py`,
`docs/steam_platform_abstraction.md`,
`docs/reverse-engineering/source-file-gap-notes/rw-g01-platform-services.md`
Parity estimate: **before 96% -> after 96%**

Completed work:

1. Updated `CL_Workshop_FailActiveDownload` so it no longer emits a second
   `item %llu failed with EResult code %i` trace after the callback owner has
   already logged the retail failure detail.
2. Kept the existing completed-state and active-download clear behavior intact.
3. Refreshed the focused regression coverage and the matching abstraction/gap
   notes for the removed duplicate failure trace.

### Task A3db: Restore the thin retail `steam_subscribeugc` command shape [COMPLETED]
Priority: Critical
Primary areas: `src/code/server/sv_ccmds.c`,
`tests/test_platform_services.py`,
`tests/test_engine_operator_command_parity.py`,
`docs/steam_platform_abstraction.md`,
`docs/reverse-engineering/source-file-gap-notes/rw-g01-platform-services.md`
Parity estimate: **before 96% -> after 96%**

Completed work:

1. Updated `SV_SteamCmd_SubscribeUGC_f` so it now mirrors the retail thin
   wrapper shape instead of stopping early behind the compatibility-only
   workshop-support gate.
2. Kept the existing one-argument item-ID parse surface intact.
3. Refreshed the focused regression coverage and the matching abstraction/gap
   notes for the subscribe command shape.

### Task A3dc: Remove the non-retail subscribe-request trace [COMPLETED]
Priority: Critical
Primary areas: `src/code/server/sv_ccmds.c`,
`tests/test_platform_services.py`,
`tests/test_engine_operator_command_parity.py`,
`docs/steam_platform_abstraction.md`,
`docs/reverse-engineering/source-file-gap-notes/rw-g01-platform-services.md`
Parity estimate: **before 96% -> after 96%**

Completed work:

1. Removed the extra `subscribe requested` diagnostic from
   `SV_SteamCmd_SubscribeUGC_f`, which retail never printed.
2. Kept the retained command registration and parse surface unchanged.
3. Refreshed the focused regression coverage and the matching abstraction/gap
   notes for the removed subscribe-request trace.

### Task A3dd: Remove the non-retail subscribe-failure trace [COMPLETED]
Priority: Critical
Primary areas: `src/code/server/sv_ccmds.c`,
`tests/test_platform_services.py`,
`tests/test_engine_operator_command_parity.py`,
`docs/steam_platform_abstraction.md`,
`docs/reverse-engineering/source-file-gap-notes/rw-g01-platform-services.md`
Parity estimate: **before 96% -> after 96%**

Completed work:

1. Removed the extra `subscribe request failed` diagnostic from
   `SV_SteamCmd_SubscribeUGC_f`, which retail never printed.
2. Kept the retained direct wrapper call intact around that removal.
3. Refreshed the focused regression coverage and the matching abstraction/gap
   notes for the removed subscribe-failure trace.

### Task A3de: Restore the retail post-subscribe item-state refresh [COMPLETED]
Priority: Critical
Primary areas: `src/code/server/sv_ccmds.c`,
`tests/test_platform_services.py`,
`tests/test_engine_operator_command_parity.py`
Parity estimate: **before 96% -> after 96%**

Completed work:

1. Updated `SV_SteamCmd_SubscribeUGC_f` so it now re-reads
   `QL_Steamworks_GetItemState` after the subscribe call, matching the retail
   `SteamWorkshop_SubscribeItem` wrapper behavior.
2. Kept the existing one-argument item-ID parse surface intact.
3. Refreshed the focused regression coverage for the post-subscribe state
   refresh.

### Task A3df: Restore the retail post-subscribe filesystem restart fast path [COMPLETED]
Priority: Critical
Primary areas: `src/code/server/sv_ccmds.c`,
`tests/test_platform_services.py`,
`tests/test_engine_operator_command_parity.py`,
`docs/steam_platform_abstraction.md`,
`docs/reverse-engineering/source-file-gap-notes/rw-g01-platform-services.md`
Parity estimate: **before 96% -> after 96%**

Completed work:

1. Updated `SV_SteamCmd_SubscribeUGC_f` so it now calls `FS_Restart` when the
   newly subscribed item is already installed, matching the retail installed-
   item fast path recovered from `SteamWorkshop_SubscribeItem`.
2. Kept the retained operator command surface intact around that restart hook.
3. Refreshed the focused regression coverage and the matching abstraction/gap
   notes for the post-subscribe restart path.

### Task A3dg: Restore the thin retail `steam_unsubscribeugc` command shape [COMPLETED]
Priority: Critical
Primary areas: `src/code/server/sv_ccmds.c`,
`tests/test_platform_services.py`,
`tests/test_engine_operator_command_parity.py`,
`docs/steam_platform_abstraction.md`,
`docs/reverse-engineering/source-file-gap-notes/rw-g01-platform-services.md`
Parity estimate: **before 96% -> after 96%**

Completed work:

1. Updated `SV_SteamCmd_UnsubscribeUGC_f` so it now mirrors the retail thin
   wrapper shape instead of stopping early behind the compatibility-only
   workshop-support gate.
2. Kept the existing one-argument item-ID parse surface intact.
3. Refreshed the focused regression coverage and the matching abstraction/gap
   notes for the unsubscribe command shape.

### Task A3dh: Remove the non-retail unsubscribe request/failure traces [COMPLETED]
Priority: Critical
Primary areas: `src/code/server/sv_ccmds.c`,
`tests/test_platform_services.py`,
`tests/test_engine_operator_command_parity.py`,
`docs/steam_platform_abstraction.md`,
`docs/reverse-engineering/source-file-gap-notes/rw-g01-platform-services.md`
Parity estimate: **before 96% -> after 96%**

Completed work:

1. Removed the extra `unsubscribe requested` and `unsubscribe request failed`
   diagnostics from `SV_SteamCmd_UnsubscribeUGC_f`, which retail never
   printed.
2. Kept the retained direct wrapper call intact around those removals.
3. Refreshed the focused regression coverage and the matching abstraction/gap
   notes for the removed unsubscribe traces.

### Task A3di: Restore the thin retail `steam_downloadugc` command helper ownership [COMPLETED]
Priority: Critical
Primary areas: `src/code/server/sv_ccmds.c`,
`tests/test_platform_services.py`,
`tests/test_engine_operator_command_parity.py`,
`docs/steam_platform_abstraction.md`,
`docs/reverse-engineering/source-file-gap-notes/rw-g01-platform-services.md`
Parity estimate: **before 96% -> after 96%**

Completed work:

1. Updated `SV_SteamCmd_DownloadUGC_f` so it now mirrors the retail thin
   wrapper shape by handing the parsed item ID off to
   `SV_SteamWorkshop_RequestDownload` instead of inlining the workshop
   control-flow directly in the operator command.
2. Kept the existing one-argument item-ID parse surface intact.
3. Refreshed the focused regression coverage and the matching abstraction/gap
   notes for the recovered command-helper ownership split.

### Task A3dj: Restore the local `SteamWorkshop_RequestDownload` helper ownership [COMPLETED]
Priority: Critical
Primary areas: `src/code/server/sv_ccmds.c`,
`tests/test_platform_services.py`,
`tests/test_engine_operator_command_parity.py`,
`docs/steam_platform_abstraction.md`,
`docs/reverse-engineering/source-file-gap-notes/rw-g01-platform-services.md`
Parity estimate: **before 96% -> after 96%**

Completed work:

1. Added `SV_SteamWorkshop_RequestDownload` so the compatibility-gated cache
   hit, restored retail detail strings, and `QL_Steamworks_DownloadItem`
   dispatch now sit under the same local helper boundary that the retail
   `steam_downloadugc` command calls into.
2. Kept the restored `Workshop item %llu: in cache.` and
   `Workshop item %llu: download` details intact around that helper recovery.
3. Refreshed the focused regression coverage and the matching abstraction/gap
   notes for the recovered request-download helper ownership.

### Task A3dk: Restore the thin retail `steam_subscribeugc` command helper ownership [COMPLETED]
Priority: Critical
Primary areas: `src/code/server/sv_ccmds.c`,
`tests/test_platform_services.py`,
`tests/test_engine_operator_command_parity.py`,
`docs/steam_platform_abstraction.md`,
`docs/reverse-engineering/source-file-gap-notes/rw-g01-platform-services.md`
Parity estimate: **before 96% -> after 96%**

Completed work:

1. Updated `SV_SteamCmd_SubscribeUGC_f` so it now mirrors the retail thin
   wrapper shape by handing the parsed item ID off to
   `SV_SteamWorkshop_SubscribeItem` instead of owning the workshop control
   flow directly.
2. Kept the existing one-argument item-ID parse surface intact.
3. Refreshed the focused regression coverage and the matching abstraction/gap
   notes for the recovered subscribe-helper ownership split.

### Task A3dl: Restore the thin retail `steam_unsubscribeugc` command helper ownership [COMPLETED]
Priority: Critical
Primary areas: `src/code/server/sv_ccmds.c`,
`tests/test_platform_services.py`,
`tests/test_engine_operator_command_parity.py`,
`docs/steam_platform_abstraction.md`,
`docs/reverse-engineering/source-file-gap-notes/rw-g01-platform-services.md`
Parity estimate: **before 96% -> after 96%**

Completed work:

1. Updated `SV_SteamCmd_UnsubscribeUGC_f` so it now mirrors the retail thin
   wrapper shape by handing the parsed item ID off to
   `SV_SteamWorkshop_UnsubscribeItem` instead of owning the unsubscribe call
   path directly.
2. Kept the existing one-argument item-ID parse surface intact.
3. Refreshed the focused regression coverage and the matching abstraction/gap
   notes for the recovered unsubscribe-helper ownership split.

### Task A3dm: Move the recovered post-subscribe item-state refresh under the local helper owner [COMPLETED]
Priority: Critical
Primary areas: `src/code/server/sv_ccmds.c`,
`tests/test_platform_services.py`,
`tests/test_engine_operator_command_parity.py`
Parity estimate: **before 96% -> after 96%**

Completed work:

1. Updated `SV_SteamWorkshop_SubscribeItem` so the recovered
   `QL_Steamworks_GetItemState` re-read now sits under the same local helper
   owner that the thin `steam_subscribeugc` command calls into.
2. Kept the direct `QL_Steamworks_SubscribeItem` wrapper call intact around
   that ownership correction.
3. Refreshed the focused regression coverage for the helper-owned
   post-subscribe state refresh.

### Task A3dn: Move the recovered post-subscribe filesystem restart under the local helper owner [COMPLETED]
Priority: Critical
Primary areas: `src/code/server/sv_ccmds.c`,
`tests/test_platform_services.py`,
`tests/test_engine_operator_command_parity.py`,
`docs/steam_platform_abstraction.md`,
`docs/reverse-engineering/source-file-gap-notes/rw-g01-platform-services.md`
Parity estimate: **before 96% -> after 96%**

Completed work:

1. Updated `SV_SteamWorkshop_SubscribeItem` so the recovered installed-item
   `FS_Restart` fast path now sits under the same local helper owner that the
   thin `steam_subscribeugc` command calls into.
2. Kept the retained operator command surface intact around that helper-owned
   restart path.
3. Refreshed the focused regression coverage and the matching abstraction/gap
   notes for the helper-owned post-subscribe restart path.

### Task A3do: Restore the retail platform subscribe-wrapper item-state refresh [COMPLETED]
Priority: Critical
Primary areas: `src/common/platform/platform_steamworks.c`,
`tests/test_platform_services.py`,
`docs/steam_platform_abstraction.md`,
`docs/reverse-engineering/source-file-gap-notes/rw-g01-platform-services.md`
Parity estimate: **before 96% -> after 96%**

Completed work:

1. Updated `QL_Steamworks_SubscribeItem` so it now re-reads
   `QL_Steamworks_GetItemState` after the raw subscribe vtable call, matching
   the retail `SteamWorkshop_SubscribeItem` helper shape.
2. Kept the recovered `0xc0 / 4` subscribe slot ownership intact around that
   state refresh.
3. Refreshed the focused regression coverage and the matching abstraction/gap
   notes for the platform subscribe-wrapper state refresh.

### Task A3dp: Remove the unconditional platform subscribe success return [COMPLETED]
Priority: Critical
Primary areas: `src/common/platform/platform_steamworks.c`,
`tests/test_platform_services.py`,
`tests/test_steamworks_harness.py`,
`docs/steam_platform_abstraction.md`,
`docs/reverse-engineering/source-file-gap-notes/rw-g01-platform-services.md`
Parity estimate: **before 96% -> after 96%**

Completed work:

1. Replaced the unconditional `return qtrue;` tail in
   `QL_Steamworks_SubscribeItem` with the recovered `itemState != 0u` result,
   matching the retail helper's post-subscribe return contract.
2. Kept the wrapper ABI and surrounding UGC interface ownership unchanged.
3. Refreshed the focused regression coverage and the matching abstraction/gap
   notes for the removed unconditional subscribe success return.

### Task A3dq: Add harness coverage for the zero-state subscribe result [COMPLETED]
Priority: Critical
Primary areas: `tests/test_steamworks_harness.py`,
`tests/steamworks_harness.c`
Parity estimate: **before 96% -> after 96%**

Completed work:

1. Extended the Steamworks harness so the enabled workshop helper test now
   asserts that `QLR_Steamworks_SubscribeItem` returns false when the post-
   subscribe item state remains zero.
2. Kept the existing disabled-lane and installed-item success expectations
   intact around that new regression.
3. Refreshed the harness support stubs so `platform_steamworks.c` continues to
   compile directly under the test fixture after the newer platform-services
   diagnostics were added.

### Task A3dr: Add harness coverage for dedicated-server installed-state subscribe success [COMPLETED]
Priority: Critical
Primary areas: `tests/test_steamworks_harness.py`
Parity estimate: **before 96% -> after 96%**

Completed work:

1. Updated the dedicated-server UGC ownership harness so it now primes the
   installed-item state before asserting subscribe success, matching the
   restored retail post-subscribe return contract.
2. Kept the existing dedicated-server UGC call-count and item-ID assertions
   intact.
3. Refreshed the focused harness coverage for the server-owned workshop lane.

### Task A3ds: Restore the client bootstrap helper name to the retail request owner [COMPLETED]
Priority: Critical
Primary areas: `src/code/client/cl_main.c`,
`tests/test_platform_services.py`
Parity estimate: **before 96% -> after 96%**

Completed work:

1. Renamed the retained client bootstrap helper to
   `CL_Workshop_RequestDownload` so the source-side owner now mirrors the
   retail `SteamWorkshop_RequestDownload` helper boundary again.
2. Dropped the synthetic queued-branch parameter from that helper.
3. Refreshed the focused regression coverage for the recovered helper owner.

### Task A3dt: Remove the non-retail queued-handoff branch from the request helper [COMPLETED]
Priority: Critical
Primary areas: `src/code/client/cl_main.c`,
`tests/test_platform_services.py`
Parity estimate: **before 96% -> after 96%**

Completed work:

1. Removed the queued-handoff branch from `CL_Workshop_RequestDownload` so it
   now owns only the initial `Workshop item %llu: requesting download.`
   detail recovered from retail `SteamWorkshop_RequestDownload`.
2. Kept the retained request-state updates intact around that narrower helper
   contract.
3. Refreshed the focused regression coverage for the removed queued branch.

### Task A3du: Restore the retail queued-handoff detail under `SteamWorkshop_AdvanceDownloadQueue` [COMPLETED]
Priority: Critical
Primary areas: `src/code/client/cl_main.c`,
`tests/test_platform_services.py`
Parity estimate: **before 96% -> after 96%**

Completed work:

1. Moved the retail `Workshop item %llu: was queued, requesting download.`
   detail under `CL_Workshop_AdvanceQueue`, matching the recovered
   `SteamWorkshop_AdvanceDownloadQueue` string owner.
2. Removed that detail from the initial-request helper owner.
3. Refreshed the focused regression coverage for the recovered queued-handoff
   detail owner.

### Task A3dv: Restore the queued download dispatch under the queue-pop helper [COMPLETED]
Priority: Critical
Primary areas: `src/code/client/cl_main.c`,
`tests/test_platform_services.py`
Parity estimate: **before 96% -> after 96%**

Completed work:

1. Moved the queued `QL_Steamworks_DownloadItem` dispatch under
   `CL_Workshop_AdvanceQueue`, matching the recovered retail queue-pop helper
   flow instead of reusing the initial-request helper.
2. Kept the retained queue-state bookkeeping intact around that owner shift.
3. Refreshed the focused regression coverage for the recovered dispatch owner.

### Task A3dw: Restore the queued active-item handoff under the queue-pop helper [COMPLETED]
Priority: Critical
Primary areas: `src/code/client/cl_main.c`,
`tests/test_platform_services.py`
Parity estimate: **before 96% -> after 96%**

Completed work:

1. Moved the queued `CL_Workshop_SetActiveItem` handoff under
   `CL_Workshop_AdvanceQueue`, matching the retail helper that promotes the
   next queued item before issuing its download request.
2. Kept the retained progress-cvar updates intact around that recovered owner
   split.
3. Refreshed the focused regression coverage for the queued active-item
   handoff owner.

### Task A3dx: Restore the queue-advance owner split under `SteamWorkshop_FinalizeItem` [COMPLETED]
Priority: Critical
Primary areas: `src/code/client/cl_main.c`,
`tests/test_platform_services.py`
Parity estimate: **before 96% -> after 96%**

Completed work:

1. Updated `CL_Workshop_FinalizeInstalledItem` so it now returns the
   `CL_Workshop_AdvanceQueue` result when the active item completes, matching
   the recovered retail `SteamWorkshop_FinalizeItem` helper flow.
2. Kept the retained completion log and active-download clear intact around
   that owner split.
3. Refreshed the focused regression coverage for the finalize-owned queue
   advance.

### Task A3dy: Remove the explicit queued-handoff from the item-installed callback owner [COMPLETED]
Priority: Critical
Primary areas: `src/code/client/cl_main.c`,
`tests/test_platform_services.py`
Parity estimate: **before 96% -> after 96%**

Completed work:

1. Removed the extra `CL_Workshop_AdvanceQueue` call from
   `CL_Steam_Workshop_OnItemInstalled` so the callback now leaves queued
   handoff ownership with `CL_Workshop_FinalizeInstalledItem`, matching
   retail.
2. Kept the retained null/app-id/tracked-item guard surface intact.
3. Refreshed the focused regression coverage for the callback-owner cleanup.

### Task A3dz: Remove the explicit queued-handoff from the download-result success owner [COMPLETED]
Priority: Critical
Primary areas: `src/code/client/cl_main.c`,
`tests/test_platform_services.py`
Parity estimate: **before 96% -> after 96%**

Completed work:

1. Removed the extra `CL_Workshop_AdvanceQueue` call from the successful
   `CL_Steam_Workshop_OnDownloadItemResult` lane so the completion path now
   mirrors the retail finalize-helper ownership split.
2. Kept the recovered invalid-app, active-download, and failure-result details
   intact.
3. Refreshed the focused regression coverage for the success-owner cleanup.

### Task A3ea: Route bootstrap cache hits through the finalize helper owner [COMPLETED]
Priority: Critical
Primary areas: `src/code/client/cl_main.c`,
`tests/test_platform_services.py`
Parity estimate: **before 96% -> after 96%**

Completed work:

1. Updated the bootstrap cache-hit path so it now calls
   `CL_Workshop_FinalizeInstalledItem` after the retail `Workshop item %llu:
   in cache.` detail instead of marking the item complete inline.
2. Kept the retained cache-hit logging intact around that recovered owner
   split.
3. Refreshed the focused regression coverage for the finalize-owned cache-hit
   path.

### Task A3eb: Update the bootstrap caller to use the recovered request helper split [COMPLETED]
Priority: Critical
Primary areas: `src/code/client/cl_main.c`,
`tests/test_platform_services.py`,
`docs/steam_platform_abstraction.md`,
`docs/reverse-engineering/source-file-gap-notes/rw-g01-platform-services.md`
Parity estimate: **before 96% -> after 96%**

Completed work:

1. Updated the client workshop bootstrap caller so the first request now goes
   through `CL_Workshop_RequestDownload`, while queued handoffs and completion
   handoffs stay with the recovered queue/finalize owners.
2. Refreshed the focused regression coverage plus the matching abstraction and
   gap-note documentation for the recovered helper ownership split.
3. Kept the bounded compatibility-only workshop provider/policy diagnostics
   intact around that tighter retail flow.

### Task A3ec: Add explicit retained state for queued workshop items [COMPLETED]
Priority: Critical
Primary areas: `src/code/client/cl_main.c`,
`tests/test_platform_services.py`
Parity estimate: **before 96% -> after 96%**

Completed work:

1. Added an explicit `queued` flag to the retained client workshop item state
   so the source can distinguish queued-for-later items from items that have
   already issued `DownloadItem`, matching the retail queue-container
   separation more closely.
2. Kept the retained `requestNumber`, `downloadRequested`, and `completed`
   fields intact around that narrower queue-state split.
3. Refreshed the focused regression coverage for the new queued-item state.

### Task A3ed: Restore bootstrap queueing ownership under `SteamWorkshop_RequestDownload` [COMPLETED]
Priority: Critical
Primary areas: `src/code/client/cl_main.c`,
`tests/test_platform_services.py`
Parity estimate: **before 96% -> after 96%**

Completed work:

1. Updated `CL_Workshop_RequestDownload` so it now owns the retail
   `Workshop item %llu: queueing download.` branch when a bootstrap download
   is already active, instead of leaving that detail under the caller.
2. Kept the recovered initial `requesting download` branch intact in the same
   helper.
3. Refreshed the focused regression coverage for the restored queueing-detail
   owner.

### Task A3ee: Route every uncached bootstrap item through the recovered request helper [COMPLETED]
Priority: Critical
Primary areas: `src/code/client/cl_main.c`,
`tests/test_platform_services.py`
Parity estimate: **before 96% -> after 96%**

Completed work:

1. Updated the bootstrap loop so every uncached item now flows through
   `CL_Workshop_RequestDownload`, matching the retail `CL_InitDownloads`
   caller shape instead of splitting the queueing branch out in the caller.
2. Kept the retained cache-hit finalize path intact around that caller
   tightening.
3. Refreshed the focused regression coverage for the unified request-helper
   routing.

### Task A3ef: Mark queued bootstrap items explicitly when the request helper defers them [COMPLETED]
Priority: Critical
Primary areas: `src/code/client/cl_main.c`,
`tests/test_platform_services.py`
Parity estimate: **before 96% -> after 96%**

Completed work:

1. Updated `CL_Workshop_RequestDownload` so it now marks later bootstrap items
   as explicitly queued when the active download already exists, matching the
   recovered retail helper's queue-container behavior more closely.
2. Kept the retained active-download issue path intact for the first item.
3. Refreshed the focused regression coverage for the explicit queued-item
   mark.

### Task A3eg: Make the queue-pop helper consume explicit queued items only [COMPLETED]
Priority: Critical
Primary areas: `src/code/client/cl_main.c`,
`tests/test_platform_services.py`
Parity estimate: **before 96% -> after 96%**

Completed work:

1. Updated `CL_Workshop_AdvanceQueue` so it now consumes only items marked as
   queued, instead of inferring queue membership from
   `!completed && !downloadRequested`.
2. Kept the recovered queued-handoff detail and `DownloadItem` dispatch intact
   around that narrower scan.
3. Refreshed the focused regression coverage for the explicit queued scan.

### Task A3eh: Clear the retained queued flag when a queued item becomes active [COMPLETED]
Priority: Critical
Primary areas: `src/code/client/cl_main.c`,
`tests/test_platform_services.py`
Parity estimate: **before 96% -> after 96%**

Completed work:

1. Updated `CL_Workshop_AdvanceQueue` so it now clears the retained queued
   flag before issuing the queued item's `DownloadItem` request, matching the
   queue-pop ownership more closely.
2. Kept the retained `downloadRequested` tracking intact around that state
   handoff.
3. Refreshed the focused regression coverage for the queued-flag clear path.

### Task A3ei: Restore bootstrap caller ownership of `cl_downloadItem` seeding [COMPLETED]
Priority: Critical
Primary areas: `src/code/client/cl_main.c`,
`tests/test_platform_services.py`
Parity estimate: **before 96% -> after 96%**

Completed work:

1. Added `CL_Workshop_SetDownloadRequestCvars` and moved the
   `cl_downloadItem` seed under the bootstrap caller after successful request-
   helper returns, matching the retail `CL_InitDownloads` ownership split.
2. Kept the retained decimal SteamID formatting intact around that move.
3. Refreshed the focused regression coverage for the caller-owned item cvar.

### Task A3ej: Restore bootstrap caller ownership of `cl_downloadName` seeding [COMPLETED]
Priority: Critical
Primary areas: `src/code/client/cl_main.c`,
`tests/test_platform_services.py`
Parity estimate: **before 96% -> after 96%**

Completed work:

1. Moved the `cl_downloadName` seed under
   `CL_Workshop_SetDownloadRequestCvars` so the bootstrap caller now owns the
   `Workshop item %i of %i` request-label cvar after successful helper
   returns, matching retail.
2. Kept the retained `requestNumber`/`totalItems` labeling intact around that
   ownership split.
3. Refreshed the focused regression coverage for the caller-owned name cvar.

### Task A3ek: Restore bootstrap caller ownership of `cl_downloadTime` seeding [COMPLETED]
Priority: Critical
Primary areas: `src/code/client/cl_main.c`,
`tests/test_platform_services.py`
Parity estimate: **before 96% -> after 96%**

Completed work:

1. Moved the `cl_downloadTime` seed under
   `CL_Workshop_SetDownloadRequestCvars` so the bootstrap caller now owns the
   request timestamp after successful helper returns, matching the retail
   `CL_InitDownloads` call site.
2. Kept the retained `cls.realtime` source intact around that move.
3. Refreshed the focused regression coverage for the caller-owned time cvar.

### Task A3el: Remove item/name/time cvar mutation from the active-item helper [COMPLETED]
Priority: Critical
Primary areas: `src/code/client/cl_main.c`,
`tests/test_platform_services.py`,
`docs/steam_platform_abstraction.md`,
`docs/reverse-engineering/source-file-gap-notes/rw-g01-platform-services.md`
Parity estimate: **before 96% -> after 96%**

Completed work:

1. Removed the `cl_downloadItem`, `cl_downloadName`, and `cl_downloadTime`
   mutations from `CL_Workshop_SetActiveItem`, leaving that helper focused on
   active-download state and progress-byte refresh rather than bootstrap-cvar
   ownership.
2. Kept the then-retained UI-facing `cl_downloadCount` / `cl_downloadSize`
   temp-cvar updates intact around that narrower helper contract.
3. Refreshed the focused regression coverage plus the matching abstraction and
   gap-note documentation for the recovered active-item helper split.

### Task A3em: Restore installed-item handling under the client request helper [COMPLETED]
Priority: Critical
Primary areas: `src/code/client/cl_main.c`,
`tests/test_platform_services.py`
Parity estimate: **before 96% -> after 96%**

Completed work:

1. Updated `CL_Workshop_RequestDownload` so it now owns the installed-item
   gate, matching the retail `SteamWorkshop_RequestDownload` helper shape
   instead of relying on a bootstrap-caller pre-check.
2. Kept the retained queued and active-download branches intact around that
   helper-owned cache-hit path.
3. Refreshed the focused regression coverage for the recovered installed-item
   owner split.

### Task A3en: Remove the bootstrap caller installed-state pre-check [COMPLETED]
Priority: Critical
Primary areas: `src/code/client/cl_main.c`,
`tests/test_platform_services.py`
Parity estimate: **before 96% -> after 96%**

Completed work:

1. Removed the installed-state short-circuit from
   `CL_Workshop_BeginBootstrap` so parsed workshop items now flow through the
   recovered request helper regardless of whether they are already installed.
2. Kept the retained parsed-item count, truncation guard, and SteamID parse
   surface intact.
3. Refreshed the focused regression coverage for the removed caller pre-check.

### Task A3eo: Restore the retail `in cache` detail under `SteamWorkshop_RequestDownload` [COMPLETED]
Priority: Critical
Primary areas: `src/code/client/cl_main.c`,
`tests/test_platform_services.py`
Parity estimate: **before 96% -> after 96%**

Completed work:

1. Moved the retail `Workshop item %llu: in cache.` detail under
   `CL_Workshop_RequestDownload`, matching the recovered helper that owns that
   string in retail.
2. Removed that detail from the bootstrap caller owner.
3. Refreshed the focused regression coverage for the recovered cache-hit
   string owner.

### Task A3ep: Restore finalize ownership for request-helper cache hits [COMPLETED]
Priority: Critical
Primary areas: `src/code/client/cl_main.c`,
`tests/test_platform_services.py`
Parity estimate: **before 96% -> after 96%**

Completed work:

1. Updated the request helper so installed-item cache hits now call
   `CL_Workshop_FinalizeInstalledItem`, matching the retail helper/finalize
   handoff.
2. Removed that finalize call from the bootstrap caller cache-hit branch.
3. Refreshed the focused regression coverage for the recovered finalize owner.

### Task A3eq: Restore queue-gate activation for helper-owned cache hits [COMPLETED]
Priority: Critical
Primary areas: `src/code/client/cl_main.c`,
`tests/test_platform_services.py`
Parity estimate: **before 96% -> after 96%**

Completed work:

1. Kept `CL_Workshop_RequestDownload` setting the retained queue gate active
   before the installed-item branch, matching the retail helper that marks the
   queue lane active even when a bootstrap item is already in cache.
2. Left the later queue-complete owner unchanged around that recovered gate
   activation.
3. Refreshed the focused regression coverage for the helper-owned queue gate.

### Task A3er: Keep bootstrap request numbering limited to helper-success returns [COMPLETED]
Priority: Critical
Primary areas: `src/code/client/cl_main.c`,
`tests/test_platform_services.py`
Parity estimate: **before 96% -> after 96%**

Completed work:

1. Kept `item->requestNumber` assignment under the bootstrap caller's
   successful `CL_Workshop_RequestDownload` return path, matching the retail
   `CL_InitDownloads` caller shape after the installed-item path moved under
   the helper.
2. Prevented cache-hit items from receiving bootstrap request ordinals.
3. Refreshed the focused regression coverage for the request-number owner.

### Task A3es: Route every parsed bootstrap item through the recovered request helper [COMPLETED]
Priority: Critical
Primary areas: `src/code/client/cl_main.c`,
`tests/test_platform_services.py`
Parity estimate: **before 96% -> after 96%**

Completed work:

1. Tightened `CL_Workshop_BeginBootstrap` so every parsed workshop item now
   flows through `CL_Workshop_RequestDownload`, matching the retail caller
   that invokes `SteamWorkshop_RequestDownload` for each token.
2. Kept the retained truncation and parse guards intact around that caller
   recovery.
3. Refreshed the focused regression coverage for the per-token request-helper
   routing.

### Task A3et: Restore queue-complete eligibility for all-cached bootstrap passes [COMPLETED]
Priority: Critical
Primary areas: `src/code/client/cl_main.c`,
`tests/test_platform_services.py`
Parity estimate: **before 96% -> after 96%**

Completed work:

1. By moving cache-hit handling under `CL_Workshop_RequestDownload`, the
   retained bootstrap lane now marks the queue gate active even when every
   required item is already installed, matching the retail path that still
   runs the later queue-complete helper.
2. Kept the retained no-download request-number and cvar behavior intact for
   those cache-hit items.
3. Refreshed the focused regression coverage for the all-cached queue-complete
   eligibility lane.

### Task A3eu: Update the focused workshop bootstrap regression for helper-owned cache hits [COMPLETED]
Priority: Critical
Primary areas: `tests/test_platform_services.py`
Parity estimate: **before 96% -> after 96%**

Completed work:

1. Updated the focused client workshop regression so it now asserts the
   installed-item `in cache` detail and finalize handoff under
   `CL_Workshop_RequestDownload` instead of under the bootstrap caller.
2. Added a direct assertion that the helper keeps the retained queue gate
   active around that installed-item branch.
3. Kept the existing queued and active-download assertions intact.

### Task A3ev: Refresh the abstraction notes for the helper-owned cache-hit split [COMPLETED]
Priority: Critical
Primary areas: `docs/steam_platform_abstraction.md`,
`docs/reverse-engineering/source-file-gap-notes/rw-g01-platform-services.md`,
`IMPLEMENTATION_PLAN.md`
Parity estimate: **before 96% -> after 96%**

Completed work:

1. Refreshed the abstraction notes so they now document the recovered
   `SteamWorkshop_RequestDownload` cache-hit ownership split and the retained
   all-cached queue-gate behavior.
2. Recorded the next ten micro-closures in the implementation ledger as
   `A3em` through `A3ev`.
3. Kept the compatibility-boundary framing explicit around those retail-backed
   helper corrections.

### Task A3ew: Restore the plain retail workshop bootstrap announcement string [COMPLETED]
Priority: Critical
Primary areas: `src/code/client/cl_main.c`,
`tests/test_platform_services.py`
Parity estimate: **before 96% -> after 96%**

Completed work:

1. Updated `CL_Workshop_BeginBootstrap` so it now prints the recovered retail
   `Server requires the following workshop items: %s` announcement instead of
   the newer provider/policy-flavored compatibility detail.
2. Kept the retained bootstrap-unavailable compatibility log intact around
   that exact-string recovery.
3. Refreshed the focused regression coverage for the restored announcement
   string.

### Task A3ex: Remove the non-retail bootstrap provider/policy announcement locals [COMPLETED]
Priority: Critical
Primary areas: `src/code/client/cl_main.c`,
`tests/test_platform_services.py`
Parity estimate: **before 96% -> after 96%**

Completed work:

1. Removed the bootstrap-only `workshopProvider` / `workshopPolicy` locals
   from `CL_Workshop_BeginBootstrap` after restoring the plain retail
   announcement string.
2. Kept the later provider/policy-aware fallback diagnostics intact elsewhere
   in the workshop lane.
3. Refreshed the focused regression coverage for the removed announcement
   locals.

### Task A3ey: Update the bootstrap regression for the restored retail announcement [COMPLETED]
Priority: Critical
Primary areas: `tests/test_platform_services.py`
Parity estimate: **before 96% -> after 96%**

Completed work:

1. Updated the focused client workshop bootstrap regression so it now asserts
   the plain retail announcement string and the absence of the removed
   provider/policy announcement locals.
2. Kept the existing request-helper and queue-owner assertions intact.
3. Reconfirmed the bootstrap regression against the current worktree.

### Task A3ez: Restore the retail frame restart-required string [COMPLETED]
Priority: Critical
Primary areas: `src/code/client/cl_main.c`,
`tests/test_platform_services.py`
Parity estimate: **before 96% -> after 96%**

Completed work:

1. Updated `CL_Workshop_Frame` so the restart-required path now prints the
   recovered retail `Steamworks downloads complete - FS restart is required`
   detail.
2. Kept the retained `FS_Restart( clc.checksumFeed )` behavior and
   `downloadsRequested` reset intact around that exact-string recovery.
3. Refreshed the focused regression coverage for the restored restart-required
   string.

### Task A3fa: Remove the compatibility-only frame restart lifecycle trace [COMPLETED]
Priority: Critical
Primary areas: `src/code/client/cl_main.c`,
`tests/test_platform_services.py`
Parity estimate: **before 96% -> after 96%**

Completed work:

1. Removed the compatibility-only `downloads complete; restarting filesystem`
   workshop lifecycle trace from the frame restart path, which retail never
   printed.
2. Replaced it with the recovered plain restart-required print under the same
   owner.
3. Refreshed the focused regression coverage for the removed compatibility
   trace.

### Task A3fb: Restore the retail frame completion string before pk3 validation [COMPLETED]
Priority: Critical
Primary areas: `src/code/client/cl_main.c`,
`tests/test_platform_services.py`
Parity estimate: **before 96% -> after 96%**

Completed work:

1. Added the recovered `Steamworks downloads complete` print to the no-restart
   branch of `CL_Workshop_Frame`, matching the retail completion helper before
   it performs the missing-pk3 compare.
2. Kept the retained state-clear and `CL_DownloadsComplete` handoff ordering
   unchanged around that exact-string recovery.
3. Refreshed the focused regression coverage for the restored completion
   string.

### Task A3fc: Restore the retail missing-pk3 warning header under the frame helper [COMPLETED]
Priority: Critical
Primary areas: `src/code/client/cl_main.c`,
`tests/test_platform_services.py`
Parity estimate: **before 96% -> after 96%**

Completed work:

1. Replaced the non-retail `WARNING: You are missing some files referenced by
   the server:` wording in `CL_Workshop_Frame` with the recovered retail
   `WARNING: Missing pk3s referenced by the server:` header.
2. Kept the retained `FS_ComparePaks( ..., qfalse )` gate intact around that
   warning path.
3. Refreshed the focused regression coverage for the restored warning header.

### Task A3fd: Restore the retail missing-pk3 consequence line [COMPLETED]
Priority: Critical
Primary areas: `src/code/client/cl_main.c`,
`tests/test_platform_services.py`
Parity estimate: **before 96% -> after 96%**

Completed work:

1. Replaced the newer `You might not be able to join the game` /
   `Go to the setting menu...` warning tail in `CL_Workshop_Frame` with the
   recovered retail `The server will most likely refuse the connection.` line.
2. Kept the retained missing-file payload insertion intact around that exact
   warning tail.
3. Refreshed the focused regression coverage for the restored consequence
   line.

### Task A3fe: Add focused regression coverage for the retail frame strings [COMPLETED]
Priority: Critical
Primary areas: `tests/test_platform_services.py`
Parity estimate: **before 96% -> after 96%**

Completed work:

1. Added a dedicated `CL_Workshop_Frame` regression so the restart-required,
   downloads-complete, and missing-pk3 warning strings now stay pinned to the
   recovered retail literals.
2. Included negative assertions for the removed compatibility-only restart and
   missing-file wording.
3. Kept the retained `FS_Restart`, state-clear, and `CL_DownloadsComplete`
   owner assertions intact.

### Task A3ff: Refresh the abstraction notes for the restored bootstrap/frame string surface [COMPLETED]
Priority: Critical
Primary areas: `docs/steam_platform_abstraction.md`,
`docs/reverse-engineering/source-file-gap-notes/rw-g01-platform-services.md`,
`IMPLEMENTATION_PLAN.md`
Parity estimate: **before 96% -> after 96%**

Completed work:

1. Refreshed the abstraction notes so they now document the restored plain
   workshop bootstrap announcement plus the recovered retail frame restart,
   completion, and missing-pk3 warning strings.
2. Recorded the next ten micro-closures in the implementation ledger as
   `A3ew` through `A3ff`.
3. Kept the compatibility-boundary framing explicit around those retail-backed
   exact-string corrections.

### Task A3fg: Restore the retained no-restart workshop completion lane to the retail active-gate teardown [COMPLETED]
Priority: Critical
Primary areas: `src/code/client/cl_main.c`, `tests/test_platform_services.py`
Parity estimate: **before 96% -> after 96%**

Completed work:

1. Rechecked the retail `CL_Workshop_Frame` HLIL helper and confirmed that the
   no-restart lane clears only the outer workshop-active gate before tailing
   into `CL_DownloadsComplete()`.
2. Updated the retained frame helper to drop only
   `cl_steamWorkshopDownloadState.active` on the no-restart completion path
   instead of zeroing the full bootstrap state.
3. Refreshed the focused frame regression so it now pins that exact handoff.

### Task A3fh: Remove the compatibility-only bootstrap-state reset from the retained workshop completion frame owner [COMPLETED]
Priority: Critical
Primary areas: `src/code/client/cl_main.c`, `tests/test_platform_services.py`
Parity estimate: **before 96% -> after 96%**

Completed work:

1. Removed the retained `CL_Workshop_ClearBootstrapState( qtrue )` call from
   the workshop no-restart completion lane because the retail helper does not
   clear the full bootstrap structure there.
2. Kept the recovered retail completion/warning strings and the
   `CL_DownloadsComplete()` handoff intact.
3. Added the matching negative assertion to the focused regression.

### Task A3fi: Refresh the workshop frame regression for the retail active-gate handoff [COMPLETED]
Priority: Critical
Primary areas: `tests/test_platform_services.py`, `IMPLEMENTATION_PLAN.md`
Parity estimate: **before 96% -> after 96%**

Completed work:

1. Updated the focused frame test to assert the retained active-gate clear
   instead of the older bootstrap-state reset.
2. Kept the surrounding retail restart-required, downloads-complete, and
   missing-pk3 string checks intact.
3. Recorded the handoff correction in the implementation ledger.

### Task A3fj: Bound retained workshop progress ownership to the recovered UI bridge [COMPLETED]
Priority: Critical
Primary areas: `src/code/client/cl_main.c`, `tests/test_platform_services.py`
Parity estimate: **before 96% -> after 96%**

Completed work:

1. Cross-checked the recovered `uix86` workshop-progress path and confirmed
   that it reads `cl_downloadItem`, calls the native `GetItemDownloadInfo`
   import, and reads `cl_downloadTime` rather than consuming
   `cl_downloadCount` / `cl_downloadSize`.
2. Used that evidence to trim the retained workshop helper ownership back to
   the native-item download-info bridge instead of generic download cvars.
3. Added focused evidence coverage for that UI bridge sequence.

### Task A3fk: Remove the compatibility-only generic progress-cvar write from the retained workshop active-item helper [COMPLETED]
Priority: Critical
Primary areas: `src/code/client/cl_main.c`, `tests/test_platform_services.py`
Parity estimate: **before 96% -> after 96%**

Completed work:

1. Removed the retained `CL_Workshop_UpdateProgressCvars()` call from
   `CL_Workshop_SetActiveItem`.
2. Kept the active-item byte reset and immediate native
   `CL_Workshop_RefreshProgress()` query intact.
3. Refreshed the focused helper regression to pin the trimmed cvar surface.

### Task A3fl: Remove the compatibility-only generic progress-cvar write from the retained workshop clear-active helper [COMPLETED]
Priority: Critical
Primary areas: `src/code/client/cl_main.c`, `tests/test_platform_services.py`
Parity estimate: **before 96% -> after 96%**

Completed work:

1. Removed the retained `CL_Workshop_UpdateProgressCvars()` call from
   `CL_Workshop_ClearActiveDownload`.
2. Kept the retained active-item and byte-count clear itself intact.
3. Added the matching negative regression assertion for the helper body.

### Task A3fm: Refresh the retained workshop helper regression for the trimmed progress-cvar surface [COMPLETED]
Priority: Critical
Primary areas: `tests/test_platform_services.py`, `IMPLEMENTATION_PLAN.md`
Parity estimate: **before 96% -> after 96%**

Completed work:

1. Extended the workshop helper test to extract
   `CL_Workshop_ClearActiveDownload`.
2. Added explicit negative assertions covering both the active-item helper and
   the clear-active helper so future edits do not reintroduce generic
   progress-cvar churn on workshop queue handoffs.
3. Recorded that focused regression tightening in the plan ledger.

### Task A3fn: Pin the recovered `uix86` workshop progress bridge evidence [COMPLETED]
Priority: Critical
Primary areas: `tests/test_platform_services.py`,
`references/reverse-engineering/ghidra/uix86/source-recreation/ui_reconstruction.c`
Parity estimate: **before 96% -> after 96%**

Completed work:

1. Added a focused evidence test covering the recovered workshop progress
   bridge in `ui_reconstruction.c`.
2. Pinned the `cl_downloadItem` read, native `GetItemDownloadInfo` import
   call, and `cl_downloadTime` read as the companion evidence backing the
   retained client-side ownership trim.
3. Included negative assertions showing that same recovered bridge does not
   use `cl_downloadCount` or `cl_downloadSize`.

### Task A3fo: Refresh the abstraction notes for the workshop completion and progress-bridge ownership correction [COMPLETED]
Priority: Critical
Primary areas: `docs/steam_platform_abstraction.md`
Parity estimate: **before 96% -> after 96%**

Completed work:

1. Updated the abstraction note so it now documents the retail no-restart
   frame handoff as an active-gate clear rather than a full bootstrap-state
   reset.
2. Recorded the recovered `uix86` workshop progress bridge evidence and the
   resulting removal of retained generic progress-cvar churn from the workshop
   active-item and clear-active helpers.
3. Kept the broader online-service compatibility-boundary framing explicit.

### Task A3fp: Refresh the source-gap notes and ledger for the workshop completion/progress ownership correction [COMPLETED]
Priority: Critical
Primary areas: `docs/reverse-engineering/source-file-gap-notes/rw-g01-platform-services.md`,
`IMPLEMENTATION_PLAN.md`
Parity estimate: **before 96% -> after 96%**

Completed work:

1. Updated the `RW-G01` source-gap note to match the restored workshop frame
   teardown and progress-bridge ownership story.
2. Recorded the next ten micro-closures in the implementation ledger as
   `A3fg` through `A3fp`.
3. Kept the evidence wording explicit so the batch is framed as retail-backed
   ownership correction rather than freehand compatibility instrumentation.

### Task A3fq: Restore the retained workshop queue-pop helper name to the recovered retail owner [COMPLETED]
Priority: Critical
Primary areas: `src/code/client/cl_main.c`, `tests/test_platform_services.py`
Parity estimate: **before 96% -> after 96%**

Completed work:

1. Rechecked the retail alias/evidence for `sub_469400` and renamed the
   retained queue-pop helper to `CL_Workshop_AdvanceDownloadQueue` so it
   matches the recovered `SteamWorkshop_AdvanceDownloadQueue` owner.
2. Updated the focused workshop regression to extract/assert that renamed
   helper directly.
3. Kept the broader workshop bootstrap ownership split intact around the
   recovered helper family.

### Task A3fr: Move the retained active-download clear under the shared queue-pop owner [COMPLETED]
Priority: Critical
Primary areas: `src/code/client/cl_main.c`, `tests/test_platform_services.py`
Parity estimate: **before 96% -> after 96%**

Completed work:

1. Rechecked the retail `SteamWorkshop_AdvanceDownloadQueue` HLIL and
   restored the retained active-download clear under the shared queue-pop
   helper before it scans for queued items.
2. Removed the need for completion/failure callers to open-code that clear.
3. Added focused regression coverage pinning the retained
   `CL_Workshop_ClearActiveDownload()` call inside the queue-pop owner.

### Task A3fs: Route the retained finalize helper through the shared queue-pop owner [COMPLETED]
Priority: Critical
Primary areas: `src/code/client/cl_main.c`, `tests/test_platform_services.py`
Parity estimate: **before 96% -> after 96%**

Completed work:

1. Updated `CL_Workshop_FinalizeInstalledItem` so the active-item completion
   lane now tails directly into `CL_Workshop_AdvanceDownloadQueue()`.
2. Removed the explicit active-download clear from the finalize helper body
   because that teardown now belongs to the shared queue-pop owner.
3. Refreshed the focused helper regression so it now asserts the shared
   completion handoff instead of the old inline clear.

### Task A3ft: Route the retained active-download failure helper through the shared queue-pop owner [COMPLETED]
Priority: Critical
Primary areas: `src/code/client/cl_main.c`, `tests/test_platform_services.py`
Parity estimate: **before 96% -> after 96%**

Completed work:

1. Updated `CL_Workshop_FailActiveDownload` so it now marks the active item
   completed and then tails into `CL_Workshop_AdvanceDownloadQueue()`.
2. Kept the helper bounded to retained state management only; the retail
   failure detail still stays in the callback owner.
3. Added the matching regression assertion for the shared failure handoff.

### Task A3fu: Remove the ignored retained `EResult` parameter from the workshop failure helper [COMPLETED]
Priority: Critical
Primary areas: `src/code/client/cl_main.c`, `tests/test_platform_services.py`
Parity estimate: **before 96% -> after 96%**

Completed work:

1. Dropped the unused `result` parameter from `CL_Workshop_FailActiveDownload`
   because the retained helper never consumed it and the retail shared
   queue-pop handoff does not take that result code.
2. Kept the actual failure-detail formatting anchored to the
   `DownloadItemResult` callback owner where the retail string lives.
3. Updated the focused callback/helper regression to match the trimmed helper
   signature.

### Task A3fv: Remove the callback-inline queue advance from the retained workshop download-result owner [COMPLETED]
Priority: Critical
Primary areas: `src/code/client/cl_main.c`, `tests/test_platform_services.py`
Parity estimate: **before 96% -> after 96%**

Completed work:

1. Removed the retained `CL_Workshop_AdvanceDownloadQueue()` call from the
   `CL_Steam_Workshop_OnDownloadItemResult` failure lane.
2. Kept the retail failure detail log intact and let the failure helper own
   the shared queue-pop handoff instead.
3. Added a focused negative assertion so that callback owner no longer grows
   a second inline queue-advance call.

### Task A3fw: Refresh the retained workshop callback regression for the shared failure handoff [COMPLETED]
Priority: Critical
Primary areas: `tests/test_platform_services.py`, `IMPLEMENTATION_PLAN.md`
Parity estimate: **before 96% -> after 96%**

Completed work:

1. Updated the workshop callback regression so the download-result owner now
   asserts `CL_Workshop_FailActiveDownload()` without the older ignored
   result argument.
2. Added the matching negative assertion covering the removed callback-inline
   queue-advance call.
3. Recorded that callback-owner tightening in the implementation ledger.

### Task A3fx: Refresh the retained workshop helper regression for the shared queue-pop teardown [COMPLETED]
Priority: Critical
Primary areas: `tests/test_platform_services.py`, `IMPLEMENTATION_PLAN.md`
Parity estimate: **before 96% -> after 96%**

Completed work:

1. Updated the focused helper regression to extract
   `CL_Workshop_AdvanceDownloadQueue`.
2. Added assertions covering the shared active-download clear in the queue-pop
   helper plus the new finalize/failure return handoffs.
3. Tightened the downloads-settled assertion so it now references the renamed
   shared owner as well.

### Task A3fy: Refresh the abstraction notes for the retained workshop failure/queue-pop owner split [COMPLETED]
Priority: Critical
Primary areas: `docs/steam_platform_abstraction.md`
Parity estimate: **before 96% -> after 96%**

Completed work:

1. Updated the abstraction note so it now documents the recovered
   `DownloadItemResult` failure handoff into the shared
   `SteamWorkshop_AdvanceDownloadQueue` owner.
2. Recorded that the retained queue-pop helper now owns the active-download
   clear before scanning queued items.
3. Kept the framing explicit that this batch is a bounded retail ownership
   correction inside the already-bounded online-services lane.

### Task A3fz: Refresh the source-gap notes and ledger for the retained workshop failure/queue-pop owner split [COMPLETED]
Priority: Critical
Primary areas: `docs/reverse-engineering/source-file-gap-notes/rw-g01-platform-services.md`,
`IMPLEMENTATION_PLAN.md`
Parity estimate: **before 96% -> after 96%**

Completed work:

1. Updated the `RW-G01` note to match the recovered shared queue-pop ownership
   for both workshop completion and failure lanes.
2. Recorded the next ten micro-closures in the implementation ledger as
   `A3fq` through `A3fz`.
3. Kept the evidence wording explicit so the batch stays framed as retail
   helper-owner correction rather than new compatibility instrumentation.

### Task A3ga: Rename the retained client UI workshop progress import parameters to the recovered low/high split [COMPLETED]
Priority: Critical
Primary areas: `src/code/client/cl_ui.c`, `tests/test_client_workshop_bootstrap_parity.py`
Parity estimate: **before 96% -> after 96%**

Completed work:

1. Rechecked the companion `uix86` workshop-progress reconstruction and
   confirmed that the native `GetItemDownloadInfo` import is reached from the
   parsed `cl_downloadItem` low/high words.
2. Renamed the retained `QL_UI_trap_GetItemDownloadInfo` parameters from
   generic `arg1` / `arg2` to `itemIdLow` / `itemIdHigh` to match that
   recovered split without changing runtime behavior.
3. Refreshed the focused client workshop import assertion to pin the renamed
   retained bridge.

### Task A3gb: Clarify the retained client workshop progress bridge comment against the recovered `uix86` owner [COMPLETED]
Priority: Critical
Primary areas: `src/code/client/cl_ui.c`
Parity estimate: **before 96% -> after 96%**

Completed work:

1. Updated the retained client bridge comment so it now records that the
   companion `uix86` reconstruction parses `cl_downloadItem`, calls the native
   import with the low/high words, and then reads `cl_downloadTime`.
2. Kept the retained bridge behavior unchanged: it still prefers retained
   client workshop state and falls back to the platform Steamworks helper.
3. Preserved the workshop progress import as a naming/evidence correction
   rather than a behavior change.

### Task A3gc: Rename the retained UI syscall wrapper parameters to the recovered low/high split [COMPLETED]
Priority: Critical
Primary areas: `src/code/ui/ui_syscalls.c`, `tests/test_ui_menu_files.py`
Parity estimate: **before 96% -> after 96%**

Completed work:

1. Renamed `trap_QL_GetItemDownloadInfo` to use `itemIdLow` / `itemIdHigh`
   parameter names instead of the older `itemHi` / `itemLo` wording.
2. Kept the retained native import call order unchanged while making that
   order explicit in the wrapper surface.
3. Refreshed the UI menu syscall regression to pin the renamed wrapper
   signature.

### Task A3gd: Rename the retained UI local declaration for the workshop progress import to the recovered low/high split [COMPLETED]
Priority: Critical
Primary areas: `src/code/ui/ui_local.h`
Parity estimate: **before 96% -> after 96%**

Completed work:

1. Updated the retained `ui_local.h` declaration for
   `trap_QL_GetItemDownloadInfo` to use `itemIdLow` / `itemIdHigh`.
2. Kept the declaration aligned with the wrapper implementation and retained
   import cast signature.
3. Preserved the rest of the native UI import surface unchanged.

### Task A3ge: Extend the recovered workshop progress evidence test to pin the parsed item-ID split before the import call [COMPLETED]
Priority: Critical
Primary areas: `tests/test_platform_services.py`
Parity estimate: **before 96% -> after 96%**

Completed work:

1. Extended the companion `uix86` evidence test so it now asserts the
   recovered `sscanf( "%llu", ... )` parse before the `GetItemDownloadInfo`
   import call.
2. Kept the existing assertions covering the native import and
   `cl_downloadTime` read intact.
3. Tightened the evidence trail for the retained low/high parameter naming.

### Task A3gf: Refresh the retained workshop progress import regression for the renamed client bridge parameters [COMPLETED]
Priority: Critical
Primary areas: `tests/test_client_workshop_bootstrap_parity.py`
Parity estimate: **before 96% -> after 96%**

Completed work:

1. Updated the focused workshop progress import regression so it now extracts
   the renamed `QL_UI_trap_GetItemDownloadInfo` signature.
2. Refreshed the retained bridge assertions to use `itemIdLow` /
   `itemIdHigh` in both the client-state and platform fallback calls.
3. Kept the negative assertions against generic download-count/size ownership
   intact.

### Task A3gg: Refresh the CL-G03 parity gate for the retained workshop progress import naming correction [COMPLETED]
Priority: Critical
Primary areas: `tests/test_client_full_parity_gate.py`
Parity estimate: **before 96% -> after 96%**

Completed work:

1. Updated the `CL-G03` parity gate so it now looks for the renamed
   `itemIdLow` / `itemIdHigh` signature on the retained client workshop
   progress bridge.
2. Kept the broader workshop publication/bootstrap/mount ownership gate
   unchanged.
3. Preserved the gate as a source-shape check rather than runtime behavior.

### Task A3gh: Refresh the UI menu import-surface regression for the retained workshop progress naming correction [COMPLETED]
Priority: Critical
Primary areas: `tests/test_ui_menu_files.py`
Parity estimate: **before 96% -> after 96%**

Completed work:

1. Updated the UI menu native-import regression so it now asserts the renamed
   `trap_QL_GetItemDownloadInfo( itemIdLow, itemIdHigh, ... )` wrapper.
2. Kept the rest of the recovered advert/cursor/subscription/measure-text
   import surface unchanged.
3. Recorded the import-surface naming correction in the focused regression.

### Task A3gi: Refresh the abstraction note for the recovered workshop progress import low/high split [COMPLETED]
Priority: Critical
Primary areas: `docs/steam_platform_abstraction.md`
Parity estimate: **before 96% -> after 96%**

Completed work:

1. Updated the abstraction note so it now explicitly records the recovered
   `GetItemDownloadInfo` low/high-word call shape from the parsed
   `cl_downloadItem`.
2. Kept the surrounding workshop progress-bridge ownership story intact.
3. Preserved the framing as companion-evidence-backed naming clarification.

### Task A3gj: Refresh the source-gap notes and ledger for the retained workshop progress import low/high split [COMPLETED]
Priority: Critical
Primary areas: `docs/reverse-engineering/source-file-gap-notes/rw-g01-platform-services.md`,
`IMPLEMENTATION_PLAN.md`
Parity estimate: **before 96% -> after 96%**

Completed work:

1. Updated the `RW-G01` note so it now explicitly describes the recovered
   low/high-word `GetItemDownloadInfo` bridge.
2. Recorded the next ten micro-closures in the implementation ledger as
   `A3ga` through `A3gj`.
3. Kept the batch framed as an evidence-backed interface-naming correction
   rather than a behavior change.

### Task A3gk: Refresh the legacy workshop bootstrap parity suite for the recovered request-helper owner [COMPLETED]
Priority: Critical
Primary areas: `tests/test_client_workshop_bootstrap_parity.py`
Parity estimate: **before 96% -> after 96%**

Completed work:

1. Updated the legacy workshop parity suite to extract
   `CL_Workshop_RequestDownload` instead of the removed pre-audit
   `CL_Workshop_StartDownload` helper.
2. Replaced the stale request-helper assertions with the current retail-backed
   `in cache`, `requesting download`, and `queueing download` owner split.
3. Kept the broader workshop bootstrap coverage anchored to current retained
   source instead of older compatibility wording.

### Task A3gl: Refresh the legacy workshop bootstrap parity suite for the recovered shared queue-pop owner [COMPLETED]
Priority: Critical
Primary areas: `tests/test_client_workshop_bootstrap_parity.py`
Parity estimate: **before 96% -> after 96%**

Completed work:

1. Updated the legacy workshop parity suite to extract
   `CL_Workshop_AdvanceDownloadQueue`.
2. Added the current shared-owner assertions for the active-download clear,
   queued-item clear, and retained queued download request.
3. Removed the older assumptions that queue progression stayed inline under
   callback or finalize owners.

### Task A3gm: Refresh the legacy workshop bootstrap parity suite for the recovered finalize/failure helper signatures [COMPLETED]
Priority: Critical
Primary areas: `tests/test_client_workshop_bootstrap_parity.py`
Parity estimate: **before 96% -> after 96%**

Completed work:

1. Updated the suite to match the current `qboolean`
   `CL_Workshop_FinalizeInstalledItem` / `CL_Workshop_FailActiveDownload`
   helper shapes.
2. Replaced the stale failure-helper expectation that still passed an ignored
   `EResult` parameter.
3. Added the shared queue-pop handoff assertions for both completion and
   failure helpers.

### Task A3gn: Refresh the legacy workshop bootstrap parity suite for the recovered bootstrap exact-string surface [COMPLETED]
Priority: Critical
Primary areas: `tests/test_client_workshop_bootstrap_parity.py`
Parity estimate: **before 96% -> after 96%**

Completed work:

1. Replaced the stale provider/policy-decorated bootstrap string expectations
   with the restored retail `Server requires the following workshop items: %s`
   announcement.
2. Updated the bootstrap-unavailable expectation to the current workshop
   lifecycle log detail instead of the older raw print wording.
3. Kept the request-number/download-cvar ownership assertions aligned with the
   current retained bootstrap caller.

### Task A3go: Refresh the legacy workshop bootstrap parity suite for the recovered callback bootstrap and failure-owner split [COMPLETED]
Priority: Critical
Primary areas: `tests/test_client_workshop_bootstrap_parity.py`
Parity estimate: **before 96% -> after 96%**

Completed work:

1. Updated the callback-bootstrap expectation to the current
   `CL_LogWorkshopLifecycle( "callback-bootstrap", detail )` fallback lane.
2. Refreshed the item-installed and download-result callback assertions to
   match the current null-payload, invalid-app, untracked-item, and
   active-download guards.
3. Added the current shared failure-handoff expectation so the callback owner
   no longer expects an inline queue advance.

### Task A3gp: Refresh the legacy workshop bootstrap parity suite for the recovered workshop frame string surface [COMPLETED]
Priority: Critical
Primary areas: `tests/test_client_workshop_bootstrap_parity.py`
Parity estimate: **before 96% -> after 96%**

Completed work:

1. Updated the workshop frame assertions to the restored retail
   restart-required and downloads-complete print strings.
2. Replaced the older compatibility-only restart log expectation with the
   current retail output plus missing-pk3 warning assertions.
3. Kept the frame-order and `CL_DownloadsComplete()` ownership checks intact.

### Task A3gq: Refresh the legacy workshop bootstrap parity suite for the current queue-complete/request-cvar ownership split [COMPLETED]
Priority: Critical
Primary areas: `tests/test_client_workshop_bootstrap_parity.py`
Parity estimate: **before 96% -> after 96%**

Completed work:

1. Updated the queue-complete assertion to the current
   `Download completed for all steamworks items` detail.
2. Kept the request-number / `cl_downloadItem` / `cl_downloadName` /
   `cl_downloadTime` ownership assertions aligned with the retained bootstrap
   caller and helper split.
3. Preserved the workshop progress owner assertions already tightened in the
   newer focused tests.

### Task A3gr: Restore the full legacy workshop bootstrap parity suite to passing status [COMPLETED]
Priority: Critical
Primary areas: `tests/test_client_workshop_bootstrap_parity.py`
Parity estimate: **before 96% -> after 96%**

Completed work:

1. Re-ran the full legacy workshop parity suite after the assertion refresh.
2. Confirmed the older coverage now passes again instead of failing on removed
   pre-audit helper names.
3. Kept the suite as supplemental validation beside the newer
   platform-services coverage.

### Task A3gs: Refresh the abstraction note for the restored legacy workshop validation alignment [COMPLETED]
Priority: Critical
Primary areas: `docs/steam_platform_abstraction.md`
Parity estimate: **before 96% -> after 96%**

Completed work:

1. Updated the abstraction note so it now records that focused validation
   keeps the recovered workshop owner split aligned across both the
   platform-services and legacy workshop parity suites.
2. Kept the note framed as validation coverage around the already-documented
   recovered owner split.
3. Avoided re-framing the batch as a runtime behavior change.

### Task A3gt: Refresh the source-gap notes and ledger for the restored legacy workshop validation alignment [COMPLETED]
Priority: Critical
Primary areas: `docs/reverse-engineering/source-file-gap-notes/rw-g01-platform-services.md`,
`IMPLEMENTATION_PLAN.md`
Parity estimate: **before 96% -> after 96%**

Completed work:

1. Updated the `RW-G01` note so it now records that the recovered workshop
   owner split is validated in both focused workshop suites.
2. Recorded the next ten micro-closures in the implementation ledger as
   `A3gk` through `A3gt`.
3. Kept the batch framed as validation-gap closure on top of already-restored
   retail-backed behavior.

### Task A3gu: Refresh the Round 05 workshop wrapper note for the retained client-state progress bridge [COMPLETED]
Priority: Critical
Primary areas: `docs/reverse-engineering/quakelive_steam_mapping_round_05.md`
Parity estimate: **before 96% -> after 96%**

Completed work:

1. Updated the Round 05 `SteamUGC_GetItemDownloadInfo` note so it no longer
   describes the older legacy-download-counter fallback.
2. Recorded that the retained UI import now consults retained client workshop
   state first and only then falls back to `QL_Steamworks_GetItemDownloadInfo`,
   the retained wrapper over the same low/high-word
   `SteamUGC_GetItemDownloadInfo` slot.
3. Kept the wrapper promotion itself unchanged.

### Task A3gv: Refresh the Round 14 workshop import-call note for the recovered parsed low/high split [COMPLETED]
Priority: Critical
Primary areas: `docs/reverse-engineering/quakelive_steam_mapping_round_14.md`
Parity estimate: **before 96% -> after 96%**

Completed work:

1. Updated the Round 14 local-fact note so it now records the parsed
   `cl_downloadItem` low/high-word handoff before the UI import call.
2. Removed the stale `(itemHi, itemLo, ...)` wording.
3. Kept the underlying wrapper identification unchanged.

### Task A3gw: Refresh the Round 14 workshop import-owner note for the retained wrapper name and fallback story [COMPLETED]
Priority: Critical
Primary areas: `docs/reverse-engineering/quakelive_steam_mapping_round_14.md`
Parity estimate: **before 96% -> after 96%**

Completed work:

1. Updated the Round 14 note so import `96` is described as
   `QL_UI_trap_GetItemDownloadInfo` instead of the older placeholder wrapper
   name.
2. Recorded the retained-client-state-first progress bridge plus the direct
   Steam item-info fallback.
3. Kept the wrapper role framed as a UI-owned import seam.

### Task A3gx: Refresh the Round 14 alias summary for the recovered workshop import-entry wording [COMPLETED]
Priority: Critical
Primary areas: `docs/reverse-engineering/quakelive_steam_mapping_round_14.md`
Parity estimate: **before 96% -> after 96%**

Completed work:

1. Updated the alias-summary row for `QLUIImport_GetItemDownloadInfo`.
2. Recorded that the wrapper is reached from the parsed `cl_downloadItem`
   low/high words.
3. Kept the alias candidate itself unchanged.

### Task A3gy: Refresh the CL-G03 audit note for the retained workshop request-surface cvars [COMPLETED]
Priority: Critical
Primary areas: `docs/reverse-engineering/client-full-parity-audit-and-implementation-plan-2026-04-09.md`
Parity estimate: **before 96% -> after 96%**

Completed work:

1. Updated the CL-G03 closure note so it now records the retained
   `cl_downloadItem` / `cl_downloadName` / `cl_downloadTime` request surface
   instead of the older byte-counter wording.
2. Kept the surrounding retained bootstrap-owner summary intact.
3. Avoided re-framing the lane as a new runtime change.

### Task A3gz: Refresh the CL-G03 audit note for the retained shared queue-pop callback-owner split [COMPLETED]
Priority: Critical
Primary areas: `docs/reverse-engineering/client-full-parity-audit-and-implementation-plan-2026-04-09.md`
Parity estimate: **before 96% -> after 96%**

Completed work:

1. Updated the CL-G03 closure note so it now records the shared queue-pop
   owner for installed-item completion and download-result failure.
2. Removed the older phrasing that implied direct callback-owned queue
   advancement.
3. Kept the polling-fallback note intact.

### Task A3ha: Refresh the CL-P3 closure note for the retained workshop request-surface cvars [COMPLETED]
Priority: Critical
Primary areas: `docs/reverse-engineering/client-full-parity-audit-and-implementation-plan-2026-04-09.md`
Parity estimate: **before 96% -> after 96%**

Completed work:

1. Updated the CL-P3 completed-work note so it now records
   `cl_downloadItem` / `cl_downloadName` / `cl_downloadTime` instead of the
   older byte-counter wording.
2. Kept the retained active/queued workshop bootstrap summary intact.
3. Preserved the closure note as historical documentation rather than a new
   behavior claim.

### Task A3hb: Refresh the CL-P3 closure note for the retained shared finalize/failure helper handoff [COMPLETED]
Priority: Critical
Primary areas: `docs/reverse-engineering/client-full-parity-audit-and-implementation-plan-2026-04-09.md`
Parity estimate: **before 96% -> after 96%**

Completed work:

1. Updated the CL-P3 callback-exactness closure note so it now records the
   shared finalize/failure helper handoff into
   `SteamWorkshop_AdvanceDownloadQueue`.
2. Removed the older immediate callback-owned queue-advancement wording.
3. Kept the listed validation suites intact.

### Task A3hc: Add focused validation for the stale reverse-engineering workshop note cleanup and tighten the CL-G03 parity gate [COMPLETED]
Priority: Critical
Primary areas: `tests/test_client_workshop_bootstrap_parity.py`,
`tests/test_client_full_parity_gate.py`
Parity estimate: **before 96% -> after 96%**

Completed work:

1. Added a focused regression covering the refreshed Round 05 / Round 14 /
   client-parity-plan workshop notes.
2. Tightened the `CL-G03` parity gate so it now requires the current request-
   surface and shared queue-pop wording in the client parity plan.
3. Kept the gate scoped to current workshop ownership/validation shape rather
   than runtime artifacts.

### Task A3hd: Refresh the abstraction notes, source-gap notes, and ledger for stale reverse-engineering workshop note cleanup [COMPLETED]
Priority: Critical
Primary areas: `docs/steam_platform_abstraction.md`,
`docs/reverse-engineering/source-file-gap-notes/rw-g01-platform-services.md`,
`IMPLEMENTATION_PLAN.md`
Parity estimate: **before 96% -> after 96%**

Completed work:

1. Updated the abstraction/source-gap notes so they now explicitly record that
   the older reverse-engineering workshop notes were brought back into line
   with the recovered low/high import wording and shared queue-pop owner
   story.
2. Recorded the next ten micro-closures in the implementation ledger as
   `A3gu` through `A3hd`.
3. Kept the batch framed as stale-note cleanup and validation tightening on
   top of already-restored retail-backed behavior.

### Task A3he: Refresh the client CVar note for the retained workshop request-surface cvars [COMPLETED]
Priority: Critical
Primary areas: `docs/client_cvars.md`
Parity estimate: **before 96% -> after 96%**

Completed work:

1. Updated the client CVar note so it now records `cl_downloadItem`,
   `cl_downloadName`, and `cl_downloadTime` as the retained workshop
   request-surface trio.
2. Anchored that wording to the recovered `CL_InitDownloads` ownership.
3. Kept the note scoped to documentation rather than new runtime behavior.

### Task A3hf: Refresh the client CVar note for the recovered UI progress bridge [COMPLETED]
Priority: Critical
Primary areas: `docs/client_cvars.md`
Parity estimate: **before 96% -> after 96%**

Completed work:

1. Updated the same note so it now records the parsed `cl_downloadItem`
   low/high-word handoff into the native `GetItemDownloadInfo` probe.
2. Kept `cl_downloadTime` in the documented retained progress surface.
3. Avoided reintroducing the older legacy-byte-counter wording.

### Task A3hg: Refresh the client CVar note for the non-authoritative counter cvars [COMPLETED]
Priority: Critical
Primary areas: `docs/client_cvars.md`
Parity estimate: **before 96% -> after 96%**

Completed work:

1. Updated the note so it now records `cl_downloadCount` and
   `cl_downloadSize` as UI-facing temp cvars rather than the authoritative
   workshop progress owner.
2. Kept the non-Steam fallback guidance explicit.
3. Left the underlying CVar registration untouched.

### Task A3hh: Refresh the CL-P3 closure note for the retained/direct workshop progress bridge [COMPLETED]
Priority: Critical
Primary areas: `docs/reverse-engineering/client-full-parity-audit-and-implementation-plan-2026-04-09.md`
Parity estimate: **before 96% -> after 96%**

Completed work:

1. Updated the historical `CL-P3` closure note so it now describes the
   retained-client-state-first workshop progress bridge plus the direct
   `GetItemDownloadInfo` fallback keyed by parsed `cl_downloadItem` words.
2. Removed the older generic "retained client owner" shorthand.
3. Kept the rest of the closure summary intact.

### Task A3hi: Add focused validation for the client workshop CVar-note alignment [COMPLETED]
Priority: Critical
Primary areas: `tests/test_client_workshop_bootstrap_parity.py`
Parity estimate: **before 96% -> after 96%**

Completed work:

1. Extended the focused workshop-note regression so it now reads
   `docs/client_cvars.md`.
2. Added assertions for the retained request-surface trio, direct
   `GetItemDownloadInfo` bridge wording, and the non-authoritative
   `cl_downloadCount` / `cl_downloadSize` note.
3. Kept the test scoped to evidence-note drift rather than runtime behavior.

### Task A3hj: Tighten the CL-G03 parity gate for current client workshop CVar wording [COMPLETED]
Priority: Critical
Primary areas: `tests/test_client_full_parity_gate.py`
Parity estimate: **before 96% -> after 96%**

Completed work:

1. Added `docs/client_cvars.md` as a tracked CL-G03 documentation input.
2. Tightened the gate so it now requires the current retained/direct workshop
   progress wording in both the client CVar note and the client parity plan.
3. Added a dedicated `client_cvar_notes_current` detail lane for that check.

### Task A3hk: Refresh the abstraction note for the aligned workshop CVar note [COMPLETED]
Priority: Critical
Primary areas: `docs/steam_platform_abstraction.md`
Parity estimate: **before 96% -> after 96%**

Completed work:

1. Updated the abstraction note so it now calls out the aligned
   `docs/client_cvars.md` wording.
2. Recorded that `cl_downloadItem`, `cl_downloadName`, and `cl_downloadTime`
   remain the retained workshop request/progress bridge.
3. Recorded that `cl_downloadCount` / `cl_downloadSize` stay UI-facing temp
   cvars instead of the authoritative owner.

### Task A3hl: Refresh the RW-G01 source-gap note for the aligned workshop CVar note [COMPLETED]
Priority: Critical
Primary areas: `docs/reverse-engineering/source-file-gap-notes/rw-g01-platform-services.md`
Parity estimate: **before 96% -> after 96%**

Completed work:

1. Updated the `RW-G01` note so it now calls out the aligned
   `docs/client_cvars.md` wording alongside the workshop progress bridge note.
2. Recorded the same retained trio versus UI-temp-counter split there.
3. Kept the note framed as documentation alignment over already-restored
   behavior.

### Task A3hm: Refresh the implementation ledger for the workshop CVar-note cleanup [COMPLETED]
Priority: Critical
Primary areas: `IMPLEMENTATION_PLAN.md`
Parity estimate: **before 96% -> after 96%**

Completed work:

1. Recorded the client workshop CVar-note cleanup as explicit micro-closures
   instead of leaving it implicit.
2. Kept the ledger framing evidence-backed and documentation-oriented.
3. Preserved the active `A3` scope summary unchanged.

### Task A3hn: Record the next ten micro-closures for the client workshop CVar-note cleanup batch [COMPLETED]
Priority: Critical
Primary areas: `IMPLEMENTATION_PLAN.md`
Parity estimate: **before 96% -> after 96%**

Completed work:

1. Recorded this batch in the implementation ledger as `A3he` through
   `A3hn`.
2. Kept the batch framed as stale-note cleanup and validation tightening on
   top of already-restored retail-backed behavior.
3. Avoided re-framing the batch as a runtime code change.

### Task A3ho: Refresh the Round 05 workshop wrapper note for the retained direct-helper name [COMPLETED]
Priority: Critical
Primary areas: `docs/reverse-engineering/quakelive_steam_mapping_round_05.md`
Parity estimate: **before 96% -> after 96%**

Completed work:

1. Updated the Round 05 `SteamUGC_GetItemDownloadInfo` note so it now names
   `QL_Steamworks_GetItemDownloadInfo` directly instead of the older generic
   "direct Steam item-info probe" wording.
2. Kept the retained-client-state-first UI import story intact.
3. Preserved the wrapper promotion itself unchanged.

### Task A3hp: Refresh the Round 14 workshop import-call note for the retained direct-helper name [COMPLETED]
Priority: Critical
Primary areas: `docs/reverse-engineering/quakelive_steam_mapping_round_14.md`
Parity estimate: **before 96% -> after 96%**

Completed work:

1. Updated the Round 14 local-fact note so it now names
   `QL_Steamworks_GetItemDownloadInfo` as the retained fallback helper.
2. Kept the parsed `cl_downloadItem` low/high-word handoff explicit.
3. Avoided changing the underlying wrapper identification.

### Task A3hq: Refresh the Round 14 alias summary for the retained direct-helper bridge wording [COMPLETED]
Priority: Critical
Primary areas: `docs/reverse-engineering/quakelive_steam_mapping_round_14.md`
Parity estimate: **before 96% -> after 96%**

Completed work:

1. Updated the alias-summary row for `QLUIImport_GetItemDownloadInfo`.
2. Recorded that the retained `cl_ui.c` bridge falls back to
   `QL_Steamworks_GetItemDownloadInfo`.
3. Kept the alias candidate itself unchanged.

### Task A3hr: Refresh the CL-G03 observed-source note for the retained direct-helper bridge [COMPLETED]
Priority: Critical
Primary areas: `docs/reverse-engineering/client-full-parity-audit-and-implementation-plan-2026-04-09.md`
Parity estimate: **before 96% -> after 96%**

Completed work:

1. Updated the historical `CL-G03` observed-source note so it now names
   `QL_Steamworks_GetItemDownloadInfo` instead of the older generic direct
   Steam-item probe wording.
2. Kept the retained-client-state-first bridge summary intact.
3. Left the surrounding workshop mount/bootstrap notes unchanged.

### Task A3hs: Refresh the CL-P3 closure note for the retained direct-helper bridge [COMPLETED]
Priority: Critical
Primary areas: `docs/reverse-engineering/client-full-parity-audit-and-implementation-plan-2026-04-09.md`
Parity estimate: **before 96% -> after 96%**

Completed work:

1. Updated the historical `CL-P3` closure note so it now names
   `QL_Steamworks_GetItemDownloadInfo` as the retained fallback helper.
2. Kept the retained workshop owner split and legacy-counter exclusion intact.
3. Preserved the closure note as historical documentation rather than a new
   runtime change.

### Task A3ht: Refresh the CL-P3 exit criteria for the recovered low/high workshop progress bridge [COMPLETED]
Priority: Critical
Primary areas: `docs/reverse-engineering/client-full-parity-audit-and-implementation-plan-2026-04-09.md`
Parity estimate: **before 96% -> after 96%**

Completed work:

1. Updated the workshop-progress exit criterion so it now names the recovered
   `GetItemDownloadInfo` low/high-word bridge explicitly.
2. Kept the negative contrast with the older generic legacy counters.
3. Avoided re-framing the lane as a behavior change.

### Task A3hu: Add focused validation for the refreshed workshop helper-note wording [COMPLETED]
Priority: Critical
Primary areas: `tests/test_client_workshop_bootstrap_parity.py`
Parity estimate: **before 96% -> after 96%**

Completed work:

1. Extended the focused workshop-note regression to require the refreshed
   Round 05 / Round 14 helper wording.
2. Added assertions for the current client-parity-plan wording around the
   retained/direct helper split and the low/high-word exit criterion.
3. Kept the test scoped to evidence-note drift rather than runtime behavior.

### Task A3hv: Tighten the CL-G03 parity gate for the refreshed workshop helper-note wording [COMPLETED]
Priority: Critical
Primary areas: `tests/test_client_full_parity_gate.py`
Parity estimate: **before 96% -> after 96%**

Completed work:

1. Tightened the `CL-G03` parity gate so it now requires the refreshed
   retained/direct helper wording in the client parity plan.
2. Kept the existing retained request-surface and shared queue-pop checks
   intact.
3. Preserved the gate as a documentation/validation guard, not a runtime
   behavior claim.

### Task A3hw: Refresh the abstraction and RW-G01 notes for the retained direct-helper wording alignment [COMPLETED]
Priority: Critical
Primary areas: `docs/steam_platform_abstraction.md`,
`docs/reverse-engineering/source-file-gap-notes/rw-g01-platform-services.md`
Parity estimate: **before 96% -> after 96%**

Completed work:

1. Updated the abstraction and `RW-G01` notes so they now record that the
   older client-parity notes were aligned to the explicit
   `QL_Steamworks_GetItemDownloadInfo` fallback naming.
2. Kept the retained-client-state progress bridge and shared queue-pop owner
   story intact.
3. Left the surrounding workshop/service-boundary notes unchanged.

### Task A3hx: Record the next ten micro-closures for the workshop helper-note wording cleanup batch [COMPLETED]
Priority: Critical
Primary areas: `IMPLEMENTATION_PLAN.md`
Parity estimate: **before 96% -> after 96%**

Completed work:

1. Recorded this batch in the implementation ledger as `A3ho` through
   `A3hx`.
2. Kept the batch framed as stale-note cleanup and validation tightening on
   top of already-restored retail-backed behavior.
3. Avoided re-framing the batch as a runtime code change.

### Task A3hy: Refresh the top-level CL-P3 summary for the retained direct-helper name [COMPLETED]
Priority: Critical
Primary areas: `docs/reverse-engineering/client-full-parity-audit-and-implementation-plan-2026-04-09.md`
Parity estimate: **before 96% -> after 96%**

Completed work:

1. Updated the top-level `CL-P3` summary so it now names
   `QL_Steamworks_GetItemDownloadInfo` instead of the older generic direct
   probe wording.
2. Kept the retained-client-state-first bridge summary intact.
3. Preserved the surrounding parity summary unchanged.

### Task A3hz: Refresh the top-level CL-P3 summary for the recovered low/high-word bridge wording [COMPLETED]
Priority: Critical
Primary areas: `docs/reverse-engineering/client-full-parity-audit-and-implementation-plan-2026-04-09.md`
Parity estimate: **before 96% -> after 96%**

Completed work:

1. Updated the same summary so it now records the retail
   `SteamUGC_GetItemDownloadInfo` low/high-word slot more explicitly.
2. Kept the parsed `cl_downloadItem` ownership visible in the wording.
3. Avoided reintroducing generic helper shorthand.

### Task A3ia: Refresh the historical A3gu implementation-plan note for the retained direct-helper name [COMPLETED]
Priority: Critical
Primary areas: `IMPLEMENTATION_PLAN.md`
Parity estimate: **before 96% -> after 96%**

Completed work:

1. Updated the older `A3gu` completed-work note so it now names
   `QL_Steamworks_GetItemDownloadInfo` directly.
2. Kept the retained-client-state-first import story intact.
3. Preserved the historical task framing.

### Task A3ib: Refresh the historical A3el implementation-plan note for UI-facing temp-cvar wording [COMPLETED]
Priority: Critical
Primary areas: `IMPLEMENTATION_PLAN.md`
Parity estimate: **before 96% -> after 96%**

Completed work:

1. Updated the older `A3el` note so it now describes the then-retained
   `cl_downloadCount` / `cl_downloadSize` updates as UI-facing temp cvars.
2. Kept the note historically accurate for that intermediate step.
3. Avoided implying those counters were ever the authoritative progress owner.

### Task A3ic: Add focused validation for the top-level CL-P3 workshop helper wording [COMPLETED]
Priority: Critical
Primary areas: `tests/test_client_workshop_bootstrap_parity.py`
Parity estimate: **before 96% -> after 96%**

Completed work:

1. Extended the focused workshop-note regression to require the refreshed
   top-level `CL-P3` summary wording.
2. Kept the existing Round 05 / Round 14 note checks intact.
3. Left the test scoped to evidence-note drift rather than runtime behavior.

### Task A3id: Add focused validation for the historical implementation-plan workshop wording [COMPLETED]
Priority: Critical
Primary areas: `tests/test_client_workshop_bootstrap_parity.py`
Parity estimate: **before 96% -> after 96%**

Completed work:

1. Extended the same regression so it now reads `IMPLEMENTATION_PLAN.md`.
2. Added assertions for the refreshed `A3gu` helper wording and `A3el`
   temp-cvar wording.
3. Kept the validation surface narrow and evidence-backed.

### Task A3ie: Tighten the CL-G03 parity gate for the refreshed implementation-plan workshop wording [COMPLETED]
Priority: Critical
Primary areas: `tests/test_client_full_parity_gate.py`
Parity estimate: **before 96% -> after 96%**

Completed work:

1. Tightened the `CL-G03` parity gate so it now requires the refreshed
   top-level client-plan wording plus the aligned implementation-plan notes.
2. Added a dedicated `implementation_plan_notes_current` detail lane for that
   check.
3. Preserved the gate as a documentation/validation guard, not a runtime
   behavior claim.

### Task A3if: Refresh the abstraction note for the aligned top-level summary and implementation-plan wording [COMPLETED]
Priority: Critical
Primary areas: `docs/steam_platform_abstraction.md`
Parity estimate: **before 96% -> after 96%**

Completed work:

1. Updated the abstraction note so it now calls out the aligned top-level
   `CL-P3` summary and older implementation-plan workshop note wording.
2. Recorded the explicit helper naming and UI-facing temp-cvar framing there.
3. Left the broader workshop boundary story unchanged.

### Task A3ig: Refresh the RW-G01 note for the aligned top-level summary and implementation-plan wording [COMPLETED]
Priority: Critical
Primary areas: `docs/reverse-engineering/source-file-gap-notes/rw-g01-platform-services.md`
Parity estimate: **before 96% -> after 96%**

Completed work:

1. Updated the `RW-G01` note so it now records the aligned top-level `CL-P3`
   summary and implementation-plan workshop wording.
2. Kept the explicit helper naming and UI-facing temp-cvar framing visible.
3. Preserved the surrounding compatibility-boundary note unchanged.

### Task A3ih: Record the next ten micro-closures for the workshop summary-and-ledger wording cleanup batch [COMPLETED]
Priority: Critical
Primary areas: `IMPLEMENTATION_PLAN.md`
Parity estimate: **before 96% -> after 96%**

Completed work:

1. Recorded this batch in the implementation ledger as `A3hy` through
   `A3ih`.
2. Kept the batch framed as stale-note cleanup and validation tightening on
   top of already-restored retail-backed behavior.
3. Avoided re-framing the batch as a runtime code change.

### Task A3ii: Close `RW-G01` as a documented bounded divergence across the repo-wide ledgers [COMPLETED]
Priority: Critical
Primary areas: `AUDIT.md`, `IMPLEMENTATION_PLAN.md`,
`docs/reverse-engineering/repo-wide-parity-audit-2026-04-21.md`,
`docs/reverse-engineering/source-file-parity-ledger-2026-04-22.md`,
`docs/reverse-engineering/source-file-parity-audit-plan-2026-04-22.md`,
`docs/reverse-engineering/source-file-gap-notes/`,
`tools/reverse-engineering/generate_source_file_audit.py`
Parity estimate: **before 96% -> after 98%**

Completed work:

1. Reclassified the `RW-G01` online-services lane as an intentional
   documented divergence instead of active repo-wide parity debt, while
   keeping the strict-retail Windows target unchanged at `100%`.
2. Updated the source-file audit generator and regenerated the plan, ledger,
   and per-file note set so the seven `RW-G01` owners now land under
   documented-divergence notes while `RW-G02` remains the only active
   file-level compatibility gap family.
3. Refreshed the top-level repo-wide ledgers so the checked-in whole-repo
   estimate now reads `98%`, with `RW-G02` and `RW-G04` left as the active
   remaining repo-wide gap families.

### Task A4j: Add a bounded silent Linux sound sink and close the OSS shutdown leak [COMPLETED]
Priority: Medium
Primary areas: `src/code/unix/linux_snd.c`,
`tests/test_non_windows_portability.py`,
`docs/reverse-engineering/source-file-gap-notes/rw-g02-linux-snd.md`,
`docs/platform/toolchain-matrix.md`, `docs/build/linux-glibc-32bit.md`
Parity estimate: **before 98% -> after 98%**

Completed work:

1. Added an explicit silent Linux DMA sink selected through `snddevice null`,
   `none`, or `silent`, giving headless/client smoke probes a non-OSS sound
   path without pulling in ALSA, PulseAudio, SDL, or other external library
   code.
2. Reconstructed the Linux sound lifecycle around the retained OSS backend so
   `audio_fd` starts at `-1`, failed init paths route through shared cleanup,
   and `SNDDMA_Shutdown()` now unmaps the mmap DMA buffer and closes the sound
   descriptor instead of leaving restart/error cleanup implicit.
3. Kept the result deliberately bounded: the default Linux sound backend is
   still the legacy `/dev/dsp` OSS path, the silent sink is not an audible
   backend, and `RW-G02` remains open until the broader Linux client renderer,
   audio, input, and validation boundary is settled.
4. Expanded the focused non-Windows portability suite and refreshed the
   platform/gap notes so the new silent sink, DMA-position simulation, and OSS
   shutdown cleanup stay source-pinned as compatibility work rather than
   strict-retail Windows parity.

### Task A4k: Bound the retained Linux joystick device and restart lifecycle [COMPLETED]
Priority: Medium
Primary areas: `src/code/unix/linux_joystick.c`,
`src/code/unix/linux_glimp.c`, `src/code/unix/linux_local.h`,
`tests/test_non_windows_portability.py`,
`docs/reverse-engineering/source-file-gap-notes/rw-g02-linux-joystick.md`,
`docs/reverse-engineering/source-file-gap-notes/rw-g02-linux-glimp.md`,
`docs/platform/toolchain-matrix.md`
Parity estimate: **before 98% -> after 98%**

Completed work:

1. Reworked the retained Linux joystick lane so startup now scans modern
   `/dev/input/js0` through `/dev/input/js3` before the historical
   `/dev/js0` through `/dev/js3` nodes, while still avoiding SDL or any other
   external input library.
2. Added explicit joystick shutdown/restart handling: `IN_ShutdownJoystick()`
   releases queued joystick key state, clears tracked axes/buttons, closes
   `joy_fd`, and resets `ui_joyavail`; `linux_glimp.c` now calls that path on
   input shutdown and when latched `in_joystick` changes trigger a restart.
3. Bounded event translation so Linux button events cannot exceed the
   `K_JOY1` through `K_JOY32` range and axis events cannot exceed the
   retained eight-axis / sixteen-direction-key table.
4. Kept `RW-G02` open because this is still retained Linux joystick
   compatibility, not a validated modern Linux client input stack, and pinned
   that distinction in the focused portability suite and gap notes.

### Task A4l: Bound the retained Linux mouse/input shutdown lifecycle [COMPLETED]
Priority: Medium
Primary areas: `src/code/unix/linux_glimp.c`,
`tests/test_non_windows_portability.py`,
`docs/reverse-engineering/source-file-gap-notes/rw-g02-linux-glimp.md`,
`docs/reverse-engineering/function-parity-gap-audit-2026-04-24.md`,
`docs/platform/toolchain-matrix.md`, `docs/build/linux-glibc-32bit.md`
Parity estimate: **before 98% -> after 98%**

Completed work:

1. Reconstructed the Linux input shutdown path around the retained X11 mouse
   grab lifecycle so `IN_Shutdown()` now calls `IN_DeactivateMouse()` before
   clearing `mouse_avail`, avoiding stale grab/activity state across
   `in_restart` and normal input teardown.
2. Kept joystick teardown in the same host-owned shutdown path and now clears
   `mouse_active` explicitly after the deactivate call, so a later `IN_Init()`
   can reactivate the mouse according to the current cvar state instead of
   inheriting a stale active flag.
3. Added focused source assertions and refreshed the RW-G02 notes so this
   remains bounded Linux-host compatibility work rather than a claim that the
   legacy X11/GLX/DGA client path is modern or retail-equivalent.

### Task A4m: Bound the retained Unix native-module loader roots and outputs [COMPLETED]
Priority: Medium
Primary areas: `src/code/unix/unix_main.c`,
`tests/test_non_windows_portability.py`,
`docs/reverse-engineering/source-file-gap-notes/rw-g02-unix-main.md`,
`docs/reverse-engineering/function-parity-gap-audit-2026-04-24.md`,
`docs/platform/toolchain-matrix.md`, `docs/build/linux-glibc-32bit.md`
Parity estimate: **before 98% -> after 98%**

Completed work:

1. Reworked the retained Unix `Sys_LoadDll()` root probe into an explicit
   bounded search over cwd, `fs_homepath`, `fs_basepath`, and `fs_cdpath`, so
   archived/native module roots can be reached through the same configured
   data-root lane used elsewhere in the Unix host.
2. Reset the legacy `entryPoint` output before probing, matching the safer
   failure contract used by the recovered Win32 loader shape and preventing a
   failed Unix load from leaving stale caller state behind.
3. Added focused source assertions and refreshed the RW-G02 notes so this
   remains Unix host compatibility work, not a claim that the non-Windows
   native-module runtime is retail-equivalent.

### Task A4n: Bound the Unix event-loop packet payload copy [COMPLETED]
Priority: Medium
Primary areas: `src/code/unix/unix_main.c`,
`tests/test_non_windows_portability.py`,
`docs/reverse-engineering/source-file-gap-notes/rw-g02-unix-main.md`,
`docs/reverse-engineering/function-parity-gap-audit-2026-04-24.md`,
`docs/platform/toolchain-matrix.md`, `docs/build/linux-glibc-32bit.md`
Parity estimate: **before 98% -> after 98%**

Completed work:

1. Reconstructed the retained Unix `Sys_GetEvent()` packet queue copy so
   `SE_PACKET` events preserve only unread bytes after `netmsg.readcount`,
   matching the recovered Win32 event-loop packet path and its SOCKS-aware
   comment.
2. Kept the change deliberately bounded: the current Unix UDP receiver still
   leaves `readcount` at zero, but the event loop now honors that field if a
   future Unix packet transport consumes header bytes before queuing.
3. Added focused source assertions and refreshed the RW-G02 notes so this is
   recorded as Unix host event-loop compatibility, not proof of full
   non-Windows runtime parity.

### Task A4o: Bound Unix native-module candidate validation [COMPLETED]
Priority: Medium
Primary areas: `src/code/unix/unix_main.c`,
`tests/test_non_windows_portability.py`,
`docs/reverse-engineering/source-file-gap-notes/rw-g02-unix-main.md`,
`docs/reverse-engineering/function-parity-gap-audit-2026-04-24.md`,
`docs/platform/toolchain-matrix.md`, `docs/build/linux-glibc-32bit.md`
Parity estimate: **before 98% -> after 98%**

Completed work:

1. Reworked the retained Unix `Sys_LoadDll()` probing loop so each opened
   native-module candidate is validated before returning a handle: it must
   expose `dllEntry` and then satisfy either the Quake Live export-table path,
   a `vmMain` export, or the legacy `dllEntry()`-returned entry point path.
2. Closed incompatible `dlopen()` handles, reset failed-load outputs, and
   continued to the next configured root instead of treating the first opened
   but incompatible shared object as the final loader outcome.
3. Added focused source assertions and refreshed the RW-G02 docs so this stays
   recorded as bounded Unix host compatibility work aligned with the recovered
   Win32 loader shape, not proof of full non-Windows runtime parity.

### Task A4p: Bound the null sound host with an explicit silent DMA sink [COMPLETED]
Priority: Medium
Primary areas: `src/code/null/null_snddma.c`,
`tests/test_non_windows_portability.py`,
`docs/reverse-engineering/source-file-gap-notes/rw-g02-null-snddma.md`,
`docs/reverse-engineering/function-parity-gap-audit-2026-04-24.md`,
`docs/platform/toolchain-matrix.md`
Parity estimate: **before 98% -> after 98%**

Completed work:

1. Replaced the null sound host's outright `SNDDMA_Init()` failure with a
   local silent DMA sink that seeds the shared `dma` shape, owns a deterministic
   22,050 Hz 16-bit stereo buffer, and advances its DMA cursor from
   `Sys_Milliseconds()`.
2. Added explicit buffer/state cleanup through `SNDDMA_Shutdown()`,
   `SNDDMA_BeginPainting()`, and `S_ClearSoundBuffer()` while preserving the
   compatibility-only no-op behavior for submit, activation, sound
   registration, local sound, and voice samples.
3. Added focused source assertions and refreshed the RW-G02 docs so this
   remains a bounded null-host compatibility sink, not an audible backend or
   a broader runtime parity claim.

### Task A4q: Make the null renderer host refuse fake GL initialization [COMPLETED]
Priority: Medium
Primary areas: `src/code/null/null_glimp.c`,
`tests/test_non_windows_portability.py`,
`docs/reverse-engineering/source-file-gap-notes/rw-g02-null-glimp.md`,
`docs/reverse-engineering/function-parity-gap-audit-2026-04-24.md`,
`docs/platform/toolchain-matrix.md`
Parity estimate: **before 98% -> after 98%**

Completed work:

1. Replaced the null `QGL_Init()` success stub with an explicit `qfalse`
   result, so the compatibility host no longer claims that a GL backend was
   loaded when no renderer library or function pointers exist.
2. Made `GLimp_Init()` fail with a clear fatal message for the null renderer
   host and routed `GLimp_Shutdown()` through `QGL_Shutdown()`, which now clears
   retained extension pointers and logging state.
3. Added focused source assertions and refreshed the RW-G02 docs so this stays
   recorded as a bounded renderer-host compatibility boundary, not a real
   graphics context or swap path.

### Task A4r: Route the null key-event pump through explicit no-device input state [COMPLETED]
Priority: Medium
Primary areas: `src/code/null/null_input.c`,
`tests/test_non_windows_portability.py`,
`docs/reverse-engineering/source-file-gap-notes/rw-g02-null-input.md`,
`docs/reverse-engineering/function-parity-gap-audit-2026-04-24.md`,
`docs/platform/toolchain-matrix.md`
Parity estimate: **before 98% -> after 98%**

Completed work:

1. Extended the null input compatibility state so it clears the retained
   `in_joystick->modified` latch while continuing to pin `ui_joyavail` to `0`.
2. Routed `Sys_SendKeyEvents()` through that no-device refresh once null input
   is initialized, making the key-event pump an explicit disabled-input
   maintenance path instead of an unstructured empty placeholder.
3. Added focused source assertions and refreshed the RW-G02 docs so this stays
   recorded as a null-host input boundary, not a real input backend or event
   source.

### Task A4s: Bound the Linux GLX shutdown and end-frame lifecycle [COMPLETED]
Priority: Medium
Primary areas: `src/code/unix/linux_glimp.c`,
`tests/test_non_windows_portability.py`,
`docs/reverse-engineering/source-file-gap-notes/rw-g02-linux-glimp.md`,
`docs/reverse-engineering/function-parity-gap-audit-2026-04-24.md`,
`docs/platform/toolchain-matrix.md`
Parity estimate: **before 98% -> after 98%**

Completed work:

1. Reworked `GLimp_Shutdown()` so partial Linux GLX init state is cleaned up
   instead of returning early when `ctx` is missing: the path now deactivates
   mouse state, detaches any current context, destroys retained context/window
   state only when present, restores VidMode/gamma state, closes the QGL log,
   clears the GLX globals, and releases QGL before clearing renderer state.
2. Guarded `GLimp_EndFrame()` against missing display/window/swap state so a
   failed partial init or post-shutdown call cannot fall through into stale
   GLX function-pointer state.
3. Added focused source assertions and refreshed the RW-G02 docs so this stays
   recorded as Linux renderer-host lifecycle containment, not a modern GLX or
   SDL-style Linux client parity claim.

## Active tasks

### Task A4: Modernise or explicitly contain the non-Windows portability lanes [OPEN]
Priority: High
Primary areas: `src/code/unix/`, `src/code/null/`,
`docs/platform/toolchain-matrix.md`, `docs/build/linux-glibc-32bit.md`
Estimated repo-wide lift if closed: **98% -> 99%**

Scope:

1. Replace the remaining Unix `Sys_*` helper placeholders that still matter
   after the restored low-memory, Linux/glibc function compare/checksum,
   `q3monkeyid` marker-probe, bounded `gprof`-control paths, and bounded
   clipboard retrieval path, bounded data-root probe, and Linux silent sound
   sink / OSS shutdown cleanup plus bounded Linux joystick descriptor/restart
   handling plus Linux mouse-grab shutdown cleanup plus Linux GLX partial-init
   shutdown/end-frame containment and the bounded Unix native-module root probe
   plus candidate validation, Unix packet event copy,
   the null renderer GL-init refusal, the explicit null silent DMA sink, and
   the null no-device key pump, or keep them clearly classified as
   compatibility-only. The null host/client/audio shims now match the current
   contract surface closely enough that the remaining work is primarily about
   the real Unix host boundary rather than stale null host/client/audio/input
   entry points.
2. Decide whether Linux client/renderer/audio/input support is a real target or
   whether the current server-only path should remain the bounded endpoint.
3. Refresh the toolchain/runtime guidance and validation coverage once the
   intended portability boundary is settled.

### Task A6: Refresh build/runtime evidence for the repo-wide ledger [OPEN]
Priority: Medium
Primary areas: tracked runtime probe bundles, native build helpers, platform
docs
Estimated repo-wide lift if closed: **98% -> 99%**

Scope:

1. Refresh the archived runtime evidence bundles on a current toolchain instead
   of relying solely on the April 2026 tracked artifacts, and promote the
   stable `latest` aliases only when reruns remain sufficient.
2. Re-run native build validation where the required Windows toolchain is
   available and fold the results back into the repo-wide audit.
3. Capture the remaining glibc and continuous/self-hosted publication
   follow-ups called out in `docs/platform/toolchain-matrix.md`, including the
   remaining retail-module runtime freshness tail.

### Task 23: Ownerdraw/stat payload completion and validation [COMPLETED]
Priority: High
Primary areas: `src/code/game/`, `src/code/cgame/`, runtime validation harnesses
Parity estimate: **before 99% -> after 100%**

Completed work:

1. Revalidated the ownerdraw debug payload against the current runtime capture
   path and confirmed that the live `pickupAvg` slab is emitted as fixed-point
   seconds rather than the older integer-only fixture assumption.
2. Updated the ownerdraw runtime harness in
   `tests/test_ownerdraw_stats_logging.py` so the debug-ownerdraw assertion
   path now accepts and normalizes float `pickupAvg` CSV payloads while keeping
   the integer stat families strict.
3. Re-ran the focused ownerdraw/stat validation surface on the current
   worktree; no concrete unsupported ownerdraw or `PLAYER_STATS` payload field
   remains in the active repo-level gap register.

### Task 24: Gameplay validation sweep [COMPLETED]
Priority: High
Primary areas: physics, Race, gametype-specific rules
Parity estimate: **before 99% -> after 100%**

Completed work:

1. Expanded the gametype lifecycle harness so it now builds through the shared
   compiler helper on Windows as well as POSIX, and it directly validates duel
   warmup/configstring sequencing, Race lifecycle routing, and CA/RR
   round-warmup init dispatch.
2. Tightened the ready-up and match-state regression guards around the retail
   gametype truth tables, including the both-teams-present gate and the
   Attack & Defend inclusion in the round-controller team-count publisher set.
3. Reconfirmed the focused Race and shared `pmove` regression lanes on the
   current worktree; the gameplay validation sweep is now covered by dedicated
   fixtures rather than left as an open catch-all validation reminder.

## Working priority order

1. Resolve the online-service compatibility boundary and evidence story.
2. Re-baseline the non-Windows portability lanes.
3. Refresh archived build/runtime evidence on current toolchains.

## Reference audits for closed surfaces

- `docs/reverse-engineering/repo-wide-parity-audit-2026-04-21.md`
- `docs/reverse-engineering/source-file-parity-ledger-2026-04-22.md`
- `docs/reverse-engineering/source-file-parity-audit-plan-2026-04-22.md`
- `docs/reverse-engineering/historical-audit-index-2026-04-22.md`
- `docs/reverse-engineering/engine-full-parity-audit-and-implementation-plan-2026-04-10.md`
- `docs/reverse-engineering/game-module-parity-audit-and-implementation-plan-2026-04-10.md`
- `docs/reverse-engineering/ui-full-parity-audit-and-implementation-plan-2026-04-05.md`
- `docs/reverse-engineering/qcommon-full-parity-audit-and-implementation-plan-2026-04-10.md`
- `docs/reverse-engineering/qshared-retail-helper-parity-audit-2026-04-17.md`
- `docs/reverse-engineering/renderer-full-parity-audit-and-implementation-plan-2026-04-09.md`
- `docs/reverse-engineering/server-full-parity-audit-and-implementation-plan-2026-04-10.md`
- `docs/reverse-engineering/engine-host-support-full-parity-audit-and-implementation-plan-2026-04-10.md`
- `docs/reverse-engineering/platform-specific-engine-parity-audit-and-implementation-plan-2026-04-16.md`
- `docs/reverse-engineering/engine-netcode-parity-audit-2026-04-16.md`
- `docs/reverse-engineering/awesomium-browser-host-parity-audit-and-implementation-plan-2026-04-16.md`

## Historical closure anchors kept for parity-gate compatibility

The entries below are intentionally terse. They preserve the exact historical
task headings and parity-estimate lines that checked-in parity gates still read
from this file, without keeping pages of duplicated completed-task prose in the
active plan.

### Task 34: Cgame Attack and Defend round-scoreboard owner parity closure [COMPLETED]

### Task 31: Strict retail game-module parity closure [COMPLETED]

### Task 73: Renderer internal helper-family ownership closure tranche [COMPLETED]
Parity estimate: **before 93% -> after 96%** (`RG-P5` complete; `RG-G06` closed)

### Task 75: Renderer strict retail-font-stack re-audit and closure-plan refresh [COMPLETED]

### Task 87: Client CL-P6 parity gate and runtime-evidence closure [COMPLETED]
Parity estimate: **before 99% -> after 100%**

### Task 92: Qcommon QC-P2 parity gate and Windows-friendly harness closure [COMPLETED]

### Task 94: Qcommon QC-P3 retail homepath closure [COMPLETED]

### Task 97: Qcommon QC-P4 collision leaf ownership closure [COMPLETED]

### Task 100: Server SV-P7 parity gate and dedicated runtime-evidence closure [COMPLETED]
Parity estimate: **before 97% -> after 100%**

### Task 102: Qcommon QC-P5 fallback VM closure [COMPLETED]

### Task 103: Remaining engine host/support EH-P2 Win32 Unicode clipboard closure [COMPLETED]

### Task 104: Strict retail game-module final ledger and runtime-evidence reconciliation [COMPLETED]

### Task 104: Qcommon QC-P6 runtime-evidence and ledger closure [COMPLETED]
Parity estimate: **before 98% -> after 100%**

### Task 110: Qshared shared-helper exactness and validation-lane closure [COMPLETED]
Parity estimate: **before 99% -> after 100%**

### Task 105: Remaining engine host/support EH-P3 raw-input host closure [COMPLETED]

### Task 106: Remaining engine host/support EH-P6 parity gate and evidence closure [COMPLETED]
Parity estimate: **before 89% -> after 92%**

### Task 107: Remaining engine host/support EH-P4 botlib internal proof closure [COMPLETED]
Parity estimate: **before 92% -> after 95%**

### Task 109: Remaining engine host/support EH-P1 boundary formalisation closure [COMPLETED]
Parity estimate: **before 100% -> after 100%** (`EH-P1` complete; strict-retail scope classification formalised)
