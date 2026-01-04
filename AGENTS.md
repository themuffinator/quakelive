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

# Work Queue

Agents should refer to `IMPLEMENTATION_PLAN.md` for the current prioritized list of reconstruction tasks. The primary goal is to close the parity gaps identified in `AUDIT.md`.

*   **Priority 1**: Implement PQL/CPMA Air Control logic in `bg_pmove.c` (Physics).
*   **Priority 2**: Verify UI bridge and fallback mechanisms.
*   **Priority 3**: Validate Race and Gametype logic.

Tick off items in `IMPLEMENTATION_PLAN.md` as they are completed.
