# Reverse Engineering Maintenance Process

This document outlines how the reverse-engineering team organises follow-up work
and keeps parity tasks actionable via the shared "Reverse Maintenance" project
board.

## Project Board Configuration

| Setting | Value |
| --- | --- |
| **Platform** | GitHub Projects (beta) board named `Reverse Maintenance` |
| **Views** | Kanban grouped by Status; Table view for batch triage |
| **Default Swimlanes** | Backlog, Ready for Pickup, In Progress, Verification, Done |
| **Automation** | Auto-archive items 14 days after moving to **Done** |

### Label Taxonomy

All cards should carry labels from each of the following categories to keep
filters useful for release planning:

- **Verification Status** – `needs-repro`, `needs-diff`, `awaits-review`,
  `ready-for-release`
- **Subsystem** – `engine`, `gameplay`, `ui`, `tooling`, `build-farm`, `documentation`
- **Complexity** – `xs`, `s`, `m`, `l`

### Seeded Backlog

| Title | Summary | Tags |
| --- | --- | --- |
| CRT manifest skew review | Validate VC80 redistributable availability in MSVC container builds and document mitigation steps. | `needs-diff`, `build-farm`, `m` |
| Recover FFmpeg build flags | Reverse-engineer FFmpeg 0.8.x configure options from shipped DLLs and publish the recipe. | `awaits-review`, `tooling`, `l` |
| Archive PDB regeneration workflow | Define how to capture and store regenerated symbol files during recapture. | `needs-diff`, `build-farm`, `s` |
| Gameplay ledger refresh cadence | Ensure gameplay parity ledger checklists are reflected after each feature delta. | `awaits-review`, `gameplay`, `s` |
| Behaviour diff automation health check | Schedule rerun of `tools/analysis/behaviour_diff.py` harness for latest builds and capture new artefacts. | `needs-repro`, `engine`, `m` |
| Document FFmpeg TODO resolution | Update `docs/reverse-engineering/build-recapture.md` once configure commands are recovered. | `needs-diff`, `documentation`, `xs` |

Sources for these backlog items were taken from the build recapture guidance,
the behaviour diff ledger, and standing documentation TODOs.

## Triage Cadence

- **Weekly triage** every Tuesday 15:00 UTC with reverse-maintenance DRI and
  rotating subsystem owners. Review new cards, confirm label coverage, and
  reprioritise based on release blockers.
- **Monthly audit** on the first Thursday to reconcile ledger/documentation
  updates and ensure closed tasks have corresponding pull requests linked.

## Escalation Paths

1. **Subsystem owner escalation** – If a card remains in **Verification** for
   more than two weeks, ping the listed subsystem owner for decision or
   resourcing.
2. **Release management escalation** – For blockers affecting tagged release
   milestones, notify the release manager (@release-captain) via the
   `#release-maintenance` Slack channel and attach the project card link.
3. **Executive escalation** – Critical production regressions escalate to the
   technical director (@technical-director) after 48 hours without mitigation
   plan.

## Meeting Notes Template

```
### Week of <YYYY-MM-DD>
- Attendance:
- High-priority cards:
- Decisions:
- Follow-up owners:
```

Use the template within the board's `Meeting Notes` custom field for quick
historical reference.
