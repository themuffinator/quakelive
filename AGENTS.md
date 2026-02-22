# Agent Instructions

This repository exists to faithfully reconstruct the Quake Live engine and game source using the Binary Ninja HLIL references as an accurate guide to the retail code base; every change should focus on rebuilding the Quake Live codebase piece by piece on top of the retail Quake III Arena GPL source.

This repository currently has the following rules for agents:

- Obey system, developer, and user instructions, and ensure AGENTS.md scope rules are followed.
- Use the latest GPT model available and announce the model at the start of the first response each session.
- In C/C++ code, indent with tabs, and include the required commented header format above every function definition.
- Avoid creating binary files (including standard images, models, and similar assets).
- Avoid creating new source files for trivially small code additions unless they are expected to grow.
- When tasks are large, break them into smaller tasks automatically.
- Do not make significant decisions based on assumptions; ask questions if needed.
- Prefer `rg` instead of `ls -R` or `grep -R` for repository searches.
- After committing changes, generate a pull request message using the `make_pr` tool.
- For each task completion, estimate before and after parity percentages versus the retail Quake Live source base outlined in the Binary Ninja HLIL references.
- **Read-only access to the `assets/` and `src/ui/` directory trees.**

## Automatic Debugging Process (Windows)

Use this process after code changes that can affect startup/runtime stability:

1. Build `Debug|x86` and ensure the binary is up to date.
2. Run a normal launch pass with logging enabled:
   - Use `+set developer 1 +set logfile 2 +set g_logfile 1`.
   - Set `+set fs_basepath C:\\Program Files (x86)\\Steam\\steamapps\\common\\Quake Live` (or equivalent retail install containing `baseq3\\pak00.pk3`).
   - Set `+set fs_cdpath ${workspaceFolder}\\assets\\quakelive` and `+set fs_homepath ${workspaceFolder}\\build\\win32\\Debug\\bin`.
   - Use `cwd=${workspaceFolder}` to keep path resolution deterministic.
   - Capture at least one runtime screenshot for this pass and store it under `build\\win32\\Debug\\dumps\\screenshots\\`.
   - Capture in two ways for reliability:
     1. Process-bound window capture (window handle/title/rect from `quakelive_steam.exe`).
     2. Engine-generated screenshot (`screenshotJPEG` preferred for tooling compatibility).
   - If process-bound capture and engine screenshot disagree, treat the engine-generated screenshot as authoritative for rendered output.
   - Avoid full-desktop captures; screenshots must prove they came from the game process.
3. Read the newest `build\\win32\\Debug\\bin\\baseq3\\qconsole.log` and classify result:
   - Success path: confirm non-zero pk3 mounts, preflight checks, UI init completion, and clean shutdown sequence.
   - Crash/fatal path: capture exact failing subsystem and message from log.
4. Validate dump generation on crash paths:
   - Set `QLR_DUMP_PATH=${workspaceFolder}\\build\\win32\\Debug\\dumps`.
   - Trigger/observe crash and verify a fresh `quakelive_steam_*.dmp` file appears.
   - Capture a screenshot near the crash moment (or immediately after relaunch if the process exits too fast).
   - Record window handle/title/rect metadata with the screenshot path to prove capture came from the game process.
   - Also collect an engine screenshot immediately before/after crash probe when possible; this helps distinguish renderer failure from OS capture artifacts.
5. Iterate fix -> rebuild -> relaunch:
   - If crash occurred, inspect dump/log evidence, patch root cause, then rerun steps 2-4.
   - If normal launch succeeded, run one forced-crash pass (`+crash`) to confirm dump pipeline remains functional.
6. Report outcomes with artifact evidence:
   - Log snippets (startup and failure/success markers).
   - Dump filename/timestamp/size when crashes are tested.
   - Screenshot filenames/timestamps for each pass.
   - Whether post-fix relaunch is stable.

# Work Queue

Agents should refer to `IMPLEMENTATION_PLAN.md` for the current prioritized list of reconstruction tasks. The primary goal is to close the parity gaps identified in `AUDIT.md`.

*   **Priority 1**: Implement PQL/CPMA Air Control logic in `bg_pmove.c` (Physics).
*   **Priority 2**: Verify UI bridge and fallback mechanisms.
*   **Priority 3**: Validate Race and Gametype logic.

Tick off items in `IMPLEMENTATION_PLAN.md` as they are completed.
