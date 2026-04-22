# Implementation Plan

Last updated: 2026-04-22

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
  worktree, but the current repo-wide parity estimate is **96%** once the
  compatibility-only and packaging-dependent surfaces are counted.
- The new file-by-file audit campaign now lives in
  `docs/reverse-engineering/source-file-parity-ledger-2026-04-22.md` and
  `docs/reverse-engineering/source-file-parity-audit-plan-2026-04-22.md`.
  It tracks `567` source entries, seeds concrete file-level notes for the
  currently evidenced `RW-G01` and `RW-G02` owners, and keeps the older
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
   staged runtime-audit lane, producing `60 passed, 7 skipped`.
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
   joystick modification latches, while `Sys_SendKeyEvents()` remains the
   documented null-host no-op event source rather than an unstructured empty
   placeholder.
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

## Active tasks

### Task A3: Replace or further bound the compatibility-only online-service lanes [OPEN]
Priority: Critical
Primary areas: `src/common/platform/`, `src/code/client/`, `src/code/server/`,
`docs/platform/authentication.md`, `docs/steam_platform_abstraction.md`
Estimated repo-wide lift if closed: **96% -> 98%**

Scope:

1. Decide whether the repo will keep online services permanently bounded as a
   documented divergence or pursue real open replacements.
2. If the lane remains bounded, keep the default-disabled policy and
   compatibility labeling explicit everywhere the service table, auth flow,
   workshop flow, advert flow, or browser overlay surfaces are exposed.
3. If an open replacement path is pursued, replace the current heuristic
   backends with transport-backed implementations and refresh the runtime
   evidence for opted-in builds.

### Task A4: Modernise or explicitly contain the non-Windows portability lanes [OPEN]
Priority: High
Primary areas: `src/code/unix/`, `src/code/null/`,
`docs/platform/toolchain-matrix.md`, `docs/build/linux-glibc-32bit.md`
Estimated repo-wide lift if closed: **96% -> 97%**

Scope:

1. Replace the remaining Unix `Sys_*` helper placeholders that still matter
   after the restored low-memory, Linux/glibc function compare/checksum,
   `q3monkeyid` marker-probe, bounded `gprof`-control paths, and bounded
   clipboard retrieval path, or keep them clearly classified as
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
Estimated repo-wide lift if closed: **96% -> 97%**

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
