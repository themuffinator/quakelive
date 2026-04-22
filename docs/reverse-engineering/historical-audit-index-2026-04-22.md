# Historical Audit Index

Last updated: 2026-04-22

## Why this exists

The repo already has workflows and parity tests that reference specific audit documents by name. This index archives and reorganises the current audit landscape without renaming or moving those files.

## Current summary ledgers

- `AUDIT.md` - current top-level parity summary and active repo-wide gap register.
- `IMPLEMENTATION_PLAN.md` - current repo-level work queue and active task list.
- `docs/reverse-engineering/repo-wide-parity-audit-2026-04-21.md` - current repo-wide gap rationale and evidence register.
- `docs/reverse-engineering/source-file-parity-ledger-2026-04-22.md` - new file-by-file campaign ledger.
- `docs/reverse-engineering/source-file-parity-audit-plan-2026-04-22.md` - new chunked execution plan for the file walk.

## Current strict-retail closure ledgers

- `docs/reverse-engineering/engine-full-parity-audit-and-implementation-plan-2026-04-10.md`
- `docs/reverse-engineering/game-module-parity-audit-and-implementation-plan-2026-04-10.md`
- `docs/reverse-engineering/ui-full-parity-audit-and-implementation-plan-2026-04-05.md`
- `docs/reverse-engineering/client-full-parity-audit-and-implementation-plan-2026-04-09.md`
- `docs/reverse-engineering/qcommon-full-parity-audit-and-implementation-plan-2026-04-10.md`
- `docs/reverse-engineering/qshared-retail-helper-parity-audit-2026-04-17.md`
- `docs/reverse-engineering/renderer-full-parity-audit-and-implementation-plan-2026-04-09.md`
- `docs/reverse-engineering/server-full-parity-audit-and-implementation-plan-2026-04-10.md`
- `docs/reverse-engineering/engine-host-support-full-parity-audit-and-implementation-plan-2026-04-10.md`
- `docs/reverse-engineering/platform-specific-engine-parity-audit-and-implementation-plan-2026-04-16.md`
- `docs/reverse-engineering/engine-netcode-parity-audit-2026-04-16.md`
- `docs/reverse-engineering/awesomium-browser-host-parity-audit-and-implementation-plan-2026-04-16.md`

## Focused ownership, runtime, and mapping references

- `docs/reverse-engineering/quakelive_steam_mapping_round_*.md` - mapping-round history and promoted ownership evidence.
- `docs/reverse-engineering/*validation-and-runtime-evidence*.md` - retained runtime bundles and validation notes.
- `docs/reverse-engineering/*ownership*.md` and `docs/reverse-engineering/*struct-layouts*.md` - focused ownership and recovered layout notes.
- `docs/reverse-engineering/cgame-*.md`, `qagame-*.md`, and related subsystem notebooks - narrower reconstruction notes that predate the repo-wide consolidation.

## Historical broad-planning snapshots

- `docs/parity-plan.md`
- `docs/ui_deltas.md`
- `docs/ui_followup_issues.md`

These files remain useful as historical context, but they should not be treated as the current parity source of truth.

## File-level gap notes

- `docs/reverse-engineering/source-file-gap-notes/` now holds the current per-file gap drill-downs opened by the source-file campaign.
- Only files with concrete, currently evidenced parity gaps should receive a note; tree-level suspicion belongs in the main ledger until the function walk isolates the file.
