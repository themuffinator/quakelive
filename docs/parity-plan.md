# Parity Audit and Delivery Plan

> Historical planning snapshot. Many items below predate the current
> reverse-engineering closure work and should not be read as the current gap
> register. For the current repo-wide status, use `AUDIT.md`,
> `IMPLEMENTATION_PLAN.md`, and
> `docs/reverse-engineering/repo-wide-parity-audit-2026-04-21.md`.

## Purpose and approach
- Establish a living action plan that drives the Quake Live reverse port toward feature, UI, and platform parity while staying aligned with the existing gameplay ledger and UI delta reports.
- Track progress directly in this document with dated status updates so future "Work on the plan" requests continue from the next unchecked item.

## Guiding principles
- Keep tasks scoped to reviewable increments (feature toggle, harness, asset drop) to avoid risky mega-PRs; split any large gap into testable vertical slices.
- Each task must name its evidence (ledger entry, capture, harness log) and success criteria to tighten validation.
- Prefer updating the relevant parity ledger or delta document in the same change so parity evidence is discoverable.

## Current parity snapshot (audit)
- **Gameplay systems:** Weapon balance tuning is still in progress, loadout unlock rules and matchmaking skill scaling hooks have not started, while physics adjustments and Domination entity plumbing are already complete. Competitive ruleset handling and item timer HUD overrides remain mid-port, and race/CTF timers are still missing.【F:docs/gameplay/parity/parity-ledger.md†L15-L30】
- **HUD and UI:** The active build still renders legacy Quake III HUD/menu flows; new Quake Live owner-draw IDs, widescreen scoreboxes, and spectator overlays are absent, and the menu stack does not mirror the streamlined Quake Live set or its browser/Awesomium hooks.【F:docs/ui_deltas.md†L7-L55】
- **Testing and harnesses:** Deterministic match, rules engine, client prediction, and syscall contract suites are defined to validate parity across QVM and DLL targets, but the plan depends on extending these runners and publishing artifacts in CI for every target matrix.【F:docs/testing-strategy.md†L8-L64】
- **Builds, assets, and packaging:** The repository already preserves HLIL dumps, extracted Quake Live assets, and deterministic CI legs across QVM/DLL/reverse builds; packaging must continue staging `default.cfg` and related assets to keep bootstrap parity intact.【F:docs/repo-overview.md†L6-L66】

## Parity plan backlog
- [x] **Baseline audit recorded (2024-11-04):** Summarised current gameplay, UI, testing, and packaging gaps using the gameplay parity ledger, HUD delta report, testing strategy, and repository overview.
- [ ] **Gameplay parity closure:**
  - [ ] Weapon balance deltas: port remaining weapon constants and damage tables; update `docs/gameplay/parity/parity-ledger.md` with before/after values and attach deterministic demo captures.
  - [ ] Loadout unlock rules: implement unlock gating and progression thresholds; mirror matchmaking skill scaling hooks; validate against HLIL traces.
  - [ ] Race/CTF timers: add timer HUD wiring in cgame and scoreboard; verify timing drift against reference demos.
  - [ ] Competitive ruleset handling: finish competitive rules toggles and item timer HUD overrides; capture comparison demos for ledger sign-off.
  - [ ] Sign-off cadence: after each bullet above lands, refresh the gameplay parity ledger and record maintainer approvals.
- [ ] **HUD and spectator parity:**
  - [ ] Owner-draw coverage: extend owner-draw IDs and cgame draw paths for Quake Live HUD elements; include widescreen-aware layouts.
  - [ ] Scoreboard/spectator overlays: port competitive HUD/spectator menus and assets; replace legacy scoreboards with menu-driven overlays and overtime/timeout states.
  - [ ] Validation harness: run headless HUD capture harnesses per layout (4:3, 16:9, 21:9) and bless captured baselines in git.
- [ ] **Lobby/menu and launcher alignment:**
  - [ ] Menu stack swap: replace legacy menu definitions with Quake Live (`menus.txt`, `main.menu`, `ingame.txt`); keep rollback switch for debugging.
  - [ ] Browser/Awesomium hooks: wire script bridges for authentication, news, and store flows; verify string parity against captures.
  - [ ] Launcher/WebView bridge: audit Awesomium/FFmpeg/Steam integration for download/update/auth paths; log deviations and fix or document them.
- [ ] **Testing and CI gating:**
  - [ ] Harness expansion: extend deterministic runners for HUD/menu behaviour, matchmaking flows, and physics deltas; produce machine-readable baselines.
  - [ ] CI artifacts: ensure every target (QVM/DLL/reverse) publishes harness outputs, captures, and parity diffs as downloadable artifacts.
  - [ ] Release gates: add CI gates that block merges on parity regression or missing baselines; require ledger/document updates in the same change.
- [ ] **Assets, packaging, and data parity:**
  - [ ] Asset staging: keep `default.cfg` and Quake Live UI assets staged in packaging recipes; verify shader/material registrations for new HUD/menu assets.
  - [ ] Asset diffs: track changes against extracted references and update packaging scripts when adding new dependencies; include checksum notes.
  - [ ] Data validation: add smoke tests that load the packaged assets in headless mode to confirm registrations and prevent missing-data regressions.
- [ ] **Documentation and ownership cadence:**
  - [ ] Plan upkeep: update this plan and the gameplay parity ledger as items close; add dates, evidence links, and owner acknowledgements.
  - [ ] Release notes: log major parity completions in release notes; include pointers to captures/harness logs for reviewers.
  - [ ] Reviewer guidance: align documentation backlog entries with the plan so reviewers can find parity evidence quickly.

## Near-term execution order
- Next "Work on the plan" step: begin **Gameplay parity closure → Weapon balance deltas**.
- Prepare supporting materials before coding: extract current constants from HLIL dumps, generate baseline demo captures, and line-item the ledger entry for quick updates.

### Weapon balance deltas kickoff (2024-11-08)
- [ ] **Reference diffing and ownership:** Re-diff Quake Live HLIL weapon constants against the current `bg_pmove.c`/`bg_misc.c` defaults to confirm the 2024-09-22 ledger snapshot is still accurate; tag Gameplay Systems (@gamedev-lead) and QA Lead (@qa-automation) as approvers.
- [ ] **Deterministic captures:** Regenerate rocket/rail/lightning scrim captures with the current reverse build and stash them under `artifacts/tests/weapon-balance-deltas.md`, noting command lines and seeds so QA can replay parity evidence.
- [ ] **Ledger refresh:** If the diff or captures deviate, update `docs/gameplay/parity/parity-ledger.md` with before/after values and a new owner approval note; otherwise, record a "revalidated" timestamp tied to the refreshed captures.
- [ ] **Harness/CI follow-up:** Add a deterministic weapon timing runner (reload/refire/ammo pickup) to the existing test harness matrix and wire it into CI artifacts so future deltas block on parity regressions.

## Update protocol
- Leave the date and a short note when ticking an item; include links to the relevant MR/commit and any updated parity evidence (logs, captures).
- When asked to "Work on the plan", pick the next unchecked top-level item above and break it into actionable PR-ready tasks before implementation.
