# Gameplay Parity Documentation Hub

The **gameplay parity** documentation set keeps the reverse-engineering effort aligned with Quake Live behaviour. Use these resources together when assessing new gameplay contributions, running parity reviews, or preparing release sign-off.

| Document | Purpose | Primary Code Owners |
| --- | --- | --- |
| [`parity-ledger.md`](./parity-ledger.md) | Snapshot of gameplay features, their parity status, and the HLIL or asset references used to validate them. | Gameplay Systems (@gamedev-lead), Movement (@physics-guild), Modes (@mutator-crew), Backend Integrations (@services-team), Rulesets (@ui-systems), HUD (@hud-taskforce) |
| [`regression-rationale-template.md`](./regression-rationale-template.md) | Template for documenting intentional or accidental deviations from Quake Live behaviour, including required approvals. | Gameplay Systems (@gamedev-lead), QA Lead (@qa-automation), Release Manager (@release-captain) |
| [`hlil-mapping-updates.md`](./hlil-mapping-updates.md) | Running log of HLIL export changes that affect gameplay validation and reference lookups. | Documentation Steward (@analysis-ops), HLIL Export Maintainer (@reverse-core) |

## Review Workflow
1. Start with the **Gameplay Parity Ledger** to confirm the current implementation and the relevant code owners.
2. If you discover a deviation, record it with the **Regression Rationale Template** and notify the listed owners for sign-off.
3. When HLIL exports move or change, append the details to **HLIL Mapping Updates** so future audits resolve the correct references.

## Verification Checklist
- [ ] Ping the owners listed above in `#gameplay-parity` after updating any of the documents so they can cross-check the content.
- [ ] Reflect owner feedback directly in the relevant markdown files to keep parity documentation authoritative.
- [ ] Add a note to `docs/release-notes.md` (or the contributor newsletter) when major parity documentation changes land.
