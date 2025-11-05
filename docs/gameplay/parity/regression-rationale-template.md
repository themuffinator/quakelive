# Regression Rationale Template

Use this template when documenting gameplay regressions or intentional deviations from Quake Live behaviour. Providing a consistent rationale trail ensures code owners can assess risk, schedule reviews, and flag areas that require additional testing before releases.

## 1. Summary
- **Feature / Behaviour:** <!-- e.g. Weapon respawn timer adjustment -->
- **Affected Modules:** <!-- e.g. src/code/game/g_items.c -->
- **Reference Materials:** <!-- HLIL dump, QA session recording, config diff -->

## 2. Expected vs. Observed
- **Expected Behaviour:** <!-- Describe Quake Live behaviour, include reference links -->
- **Observed Behaviour:** <!-- Detail the current implementation in the repo -->
- **Impact Assessment:** <!-- Player-facing impact, competitive implications, telemetry risk -->

## 3. Root Cause Analysis
- **Origin Commit / Change:** <!-- Link to commit hash or PR -->
- **Trigger Conditions:** <!-- Game modes, cvars, player state, map scripts -->
- **Reproduction Steps:**
  1. <!-- Step-by-step instructions -->
  2. <!-- Capture screenshots or demo files if relevant -->

## 4. Mitigation Plan
- **Owner:** <!-- Primary engineer accountable for the fix -->
- **Planned Fix Version:** <!-- Target milestone or build -->
- **Mitigation Tasks:**
  - [ ] <!-- Example: Update `bg_pmove.c` to restore Quake Live air control clamp. Owner: @physics-guild -->
  - [ ] <!-- Example: Add regression unit test to `src/code/game/tests/pmove_parity_test.cpp`. Owner: @qa-automation -->

## 5. Validation & Sign-off
- **Test Coverage:** <!-- Manual, automated, map-specific smoke tests -->
- **Approvals:**
  - [ ] Gameplay Systems (@gamedev-lead)
  - [ ] QA Lead (@qa-automation)
  - [ ] Release Manager (@release-captain)

---
> Store completed rationales alongside the feature documentation that introduced the regression. Update the Gameplay Parity Ledger once the mitigation ships.
