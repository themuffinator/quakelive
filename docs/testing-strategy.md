# Gameplay Testing Strategy

## Overview
To ensure gameplay logic matches Quake Live behaviour throughout the transition from QVM bytecode to native DLL modules, the project will validate every change against a shared suite of deterministic regression tests. The tests are organised so contributors can execute them locally, while CI runs the same batteries on both compilation targets to catch behavioural drift early.

## Test Suites

### 1. Deterministic Match Simulation
- **Purpose:** Replay scripted bot-vs-bot and bot-vs-player matches that cover common rulesets (duel, TDM, CTF) and verify event timelines (spawns, item pickups, weapon fire, scoring).
- **Harness:**
  - A headless dedicated-server harness derived from `code/game/` that loads `.arena` scripts and drives matches via console commands.
  - Record seedable bot behaviour (`s_randomSeed` + deterministic bot input) so both QVM and DLL paths produce identical game event logs.
  - Emit JSON logs with tick timestamps, entity states, and scoreboard deltas for diffing.
- **Implementation Hooks:**
  - Extend the existing botlib to accept scripted command queues.
  - Provide a `tests/match_scenarios/*.json` catalogue describing map, mode, bot loadouts, and expected outcomes.

### 2. Rules Engine Unit Tests
- **Purpose:** Verify isolated gameplay systems (weapon damage tables, item respawn timers, ability cooldowns, vote handling) without needing full match simulations.
- **Harness:**
  - Build a minimal runner that links against `qagame` exports and exposes C-based fixtures via Unity or Catch2 for native DLLs; recompile the same fixtures into QVM bytecode with `q3lcc`.
  - Drive tests with deterministic input data files stored under `tests/rules/`.
- **Implementation Hooks:**
  - Wrap shared logic into headers reusable by both builds so assertions can be compiled for either target.
  - Introduce a thin syscall mock layer that simulates engine callbacks (e.g., `trap_SendServerCommand`).

### 3. Client Prediction and UI Regression
- **Purpose:** Ensure `cgame` prediction, HUD updates, and scoreboard rendering remain stable when toggling between bytecode and DLL.
- **Harness:**
  - Replay captured network snapshots (`tests/netdumps/*.snap`) through a deterministic client harness.
  - Capture rendered HUD state hashes and key text outputs per snapshot.
  - Compare against blessed baselines stored in version control.
- **Implementation Hooks:**
  - Extend the existing demo playback code to operate in batch mode and export frame-by-frame state summaries.
  - Provide texture/font fallbacks so the harness runs headless on CI.

### 4. Syscall Contract Verification
- **Purpose:** Validate the interface between the engine and the game/cgame/ui modules, ensuring no regressions in syscall usage when moving to DLL exports.
- **Harness:**
  - Instrument the VM interpreter and native shim to log every syscall with arguments.
  - Provide a replay script that exercises menu navigation, server connection, and in-game interactions.
  - Diff logs between QVM and DLL runs to confirm ordering and payload parity.
- **Implementation Hooks:**
  - Introduce a shared `syscall_contract.expect` file enumerating required calls and argument schemas.
- Add a validator (`tools/tests/validate_syscall_contract.py`) that flags missing or unexpected syscalls and reports diffs.

### 5. Weapon Timing Baselines
- **Purpose:** Validate refire/reload durations and ammo pickup/max stack defaults against the HLIL reference tables.
- **Harness:**
  - Parse the HLIL timing tables and compare them against `bg_pmove.c`/`bg_misc.c` defaults.
  - Emit a deterministic baseline JSON payload alongside a concise mismatch log for CI review.

## Tooling Requirements
- Deterministic RNG seeding utilities shared across both build products.
- JSON/YAML parsing library approved for inclusion (e.g., cJSON for C harnesses).
- Cross-platform batch runners (`tests/run_headless_server.sh`, `tests/run_client_harness.py`) that accept `--target=qvm|dll`.
- Golden-result diffing tool (Python script) that surfaces concise failure diffs for CI logs.

## CI Integration
- Introduce a matrix job that builds both QVM (`make target=qvm`) and native DLLs (`msbuild /p:Configuration=Release /p:Platform=Win32`).
- For each artefact set, run the deterministic match, rules engine, client prediction, and syscall verification suites.
- Store harness outputs under `artifacts/tests/<suite>/<target>/latest/` and publish them as CI artifacts for manual review when failures occur.

## Contributor Workflow
1. Build the desired target (`make qvm-tests` or `cmake --build . --target dll-tests`).
2. Execute `python tests/run_all.py --target qvm` to validate QVM changes, then re-run with `--target dll` for native coverage.
3. Inspect diff logs when mismatches occur; update blessed baselines with `python tests/update_baseline.py` only after confirming behavioural intent.
4. Document any intentional behaviour delta in `docs/behaviour-deltas.md` (see documentation backlog).

Keeping the test definitions identical across both targets ensures new gameplay work cannot ship without demonstrating parity between the virtual machine and native implementations.
