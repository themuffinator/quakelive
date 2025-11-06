# Reconstruction Process – Slide Deck

> **Usage:** Present live or capture as a narrated video. Adapt bullet points into
> voice-over scripts to keep recordings under five minutes.

## Slide 1 – Goals of reconstruction
- Rebuild Quake Live gameplay on top of the GPL Quake III codebase.
- Preserve deterministic behaviour while modernising the toolchain.
- Document binary-to-source mappings for long-term maintainability.

## Slide 2 – Inputs & references
- HLIL exports in `references/hlil/` act as the ground truth for legacy binaries.
- Asset snapshots in `references/assets/` provide DLLs, PK3s, and configs.
- Documentation indices (e.g., `docs/reference-index.md`) track coverage.

## Slide 3 – Workflow overview
- Identify target subsystem and locate corresponding HLIL dump.
- Compare against reconstructed source under `src/` or `src-re/` branches.
- Capture deltas, update mapping docs, and propose code changes.

## Slide 4 – Tooling support
- Use Ghidra for cross-referencing symbol flow and control graphs.
- Employ Binary Ninja for HLIL-to-source diff annotations.
- Lean on the deterministic harness to validate behaviour during refactors.

## Slide 5 – Review & documentation
- Summarise findings in `docs/reverse-engineering/` notebooks.
- Update `docs/documentation-backlog.md` with remaining questions.
- Sync with the mentorship rotation for sign-off before merging changes.
