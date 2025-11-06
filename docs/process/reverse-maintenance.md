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
| **Automation** | Auto-archive items 14 days after moving to **Done**; auto-move cards to **Ready for Pickup** when labels change from `needs-repro`/`needs-diff` to `awaits-review`; Slack reminder to `#reverse-maintenance` when a card enters **Verification** |

### Label Taxonomy

All cards should carry labels from each of the following categories to keep
filters useful for release planning:

- **Verification Status** – `needs-repro`, `needs-diff`, `awaits-review`,
  `ready-for-release`
- **Subsystem** – `engine`, `gameplay`, `ui`, `tooling`, `build-farm`, `documentation`
- **Complexity** – `xs`, `s`, `m`, `l`, `xl`
- **Priority** – `p0` (critical), `p1` (high), `p2` (normal), `p3` (deferred)

### Seeded Backlog

| Title | Summary | Tags | Priority |
| --- | --- | --- | --- |
| CRT manifest skew review | Validate VC80 redistributable availability in MSVC container builds and document mitigation steps. | `awaits-review`, `build-farm`, `m` | `p1` – Ready |
| Recover FFmpeg build flags | Reverse-engineer FFmpeg 0.8.x configure options from shipped DLLs and publish the recipe. | `awaits-review`, `tooling`, `l` | `p0` – Blocker |
| Behaviour diff automation health check | Schedule rerun of `tools/analysis/behaviour_diff.py` harness for latest builds and capture new artefacts. | `needs-repro`, `engine`, `m` | `p0` – Blocker |
| Gameplay ledger refresh cadence | Ensure gameplay parity ledger checklists are reflected after each feature delta. | `awaits-review`, `gameplay`, `s` | `p1` – Operational |
| Archive PDB regeneration workflow | Define how to capture and store regenerated symbol files during recapture. | `needs-diff`, `build-farm`, `s` | `p2` – Planned |
| Document FFmpeg TODO resolution | Update `docs/reverse-engineering/build-recapture.md` once configure commands are recovered. | `needs-diff`, `documentation`, `xs` | `p2` – Planned |

Sources for these backlog items were taken from the build recapture guidance,
the behaviour diff ledger, and standing documentation TODOs.

## Triage Cadence

- **Weekly triage** every Tuesday 15:00 UTC with reverse-maintenance DRI and
  rotating subsystem owners. Review new cards, confirm label coverage, and
  reprioritise based on release blockers. Owners must groom high-priority
  (`p0`/`p1`) cards asynchronously by Monday EOD to keep the session focused on
  decision-making.
- **Monthly audit** on the first Thursday to reconcile ledger/documentation
  updates and ensure closed tasks have corresponding pull requests linked.
  Capture automation health (auto-move and Slack reminders) as part of this
  review and adjust as needed.

## Escalation Paths

1. **Subsystem owner escalation** – If a card remains in **Verification** for
   more than two weeks, ping the listed subsystem owner for decision or
   resourcing.
2. **Release management escalation** – For blockers affecting tagged release
   milestones or any card marked `p0`, notify the release manager
   (@release-captain) via the `#release-maintenance` Slack channel and attach
   the project card link within 12 hours of discovery.
3. **Executive escalation** – Critical production regressions escalate to the
   technical director (@technical-director) after 48 hours without mitigation
   plan, or immediately if external player impact is confirmed.

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

## Meeting Notes Log

```
### Week of 2024-06-10
- Attendance: Reverse-maintenance DRI, subsystem owners for engine, gameplay,
  and tooling, release manager
- High-priority cards: Recover FFmpeg build flags (`p0`), Behaviour diff
  automation health check (`p0`)
- Decisions: Commit to daily status updates on `p0` cards; rerun behaviour diff
  harness before end of week
- Follow-up owners: Tooling owner to publish FFmpeg configure findings; Engine
  owner to attach latest diff artefacts
```

```
### Week of 2024-06-17
- Attendance: Reverse-maintenance DRI, subsystem owners for build-farm and
  documentation
- High-priority cards: CRT manifest skew review (`p1`), Archive PDB regeneration
  workflow (`p2`)
- Decisions: Align CRT checks with new MSVC image; defer PDB workflow doc until
  FFmpeg recovery lands
- Follow-up owners: Build-farm owner to add CI validation step; Documentation
  owner to prep outline for deferred workflow doc
```
