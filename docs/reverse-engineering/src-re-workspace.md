# `src-re/` Workspace Primer

This note explains why `src-re/` exists as a separate tree and when code should
stay there versus being promoted into `src/`.

## Why `src-re/` is separate

`src-re/` is the clean-room reverse-engineering workspace. It is intentionally
kept separate from the main `src/` tree so the repository can distinguish
between:

- production engine and VM sources that ship or are built as the reconstructed
  Quake Live codebase
- annotated reverse-engineering notes and reduced-structure translations used to
  study retail control flow
- replayable prototype modules used by the deterministic reverse-build harnesses
- signed-off clean reconstructions that are ready for review but not yet
  necessarily merged into the production engine tree

Keeping those roles separate avoids mixing evidence, prototypes, and promoted
runtime code into one directory.

Machine-generated Ghidra exports belong with the reference corpus under
`references/reverse-engineering/ghidra/`, not in `src-re/`.

## What each subdirectory does

### `src-re/include/`

This is the only part of `src-re/` that is currently consumed directly by the
production `src/code/` tree.

- `ql_types.h` provides reverse-engineered type mirrors that are already used by
  reconstructed runtime code such as `src/code/game/g_main.c`.
- `fs_imports.h` defines the filesystem import table shared by the native VM
  bridge code in `src/code/client/`, `src/code/server/`, and
  `src/code/qcommon/`.

These headers remain here because they are part of the reverse-engineered ABI
surface, not the original Quake III source layout.

### `src-re/prototypes/`

This tree contains the replayable reverse-build modules used by the deterministic
clean-room harnesses.

- `tools/ci/build-cleanroom.sh` builds the Linux `.so` outputs from
  `src-re/prototypes/`.
- `tools/ci/build-windows-dlls.ps1` builds the Windows clean-room DLL outputs
  from `src-re/prototypes/`.

These files are active, but they are harness artefacts rather than production
engine/game sources.

### `src-re/annotated/`

This tree holds annotated walkthroughs and analysis-oriented translations. Its
purpose is explanation and comparison, not shipping runtime code.

### `src-re/clean/`

This tree holds signed-off clean reconstructions and shared clean-room headers.
It is the documentation and review record for recovered subsystems, not the
current production build input.

## Should `src-re/` be merged into `src/`?

Not yet.

The current evidence says `src-re/` still has a real job:

- production code includes `src-re/include/`
- CI and local reverse builds compile `src-re/prototypes/`
- review/sign-off documentation references `src-re/clean/`
- onboarding and reverse-engineering workflow docs treat `src-re/` as a
  separate stage in the reconstruction pipeline

Merging it into `src/` right now would blur the boundary between production
code, reverse-engineering evidence, and harness-only prototype code.

## Promotion rule of thumb

Promote code out of `src-re/` only when all of the following are true:

1. the subsystem behavior is stable against the retail references
2. the implementation belongs in the production runtime rather than only in a
   harness
3. the destination inside `src/` is unambiguous
4. the reverse-build and documentation workflows no longer need the separate
   staging copy

Until then, `src-re/` should remain a separate workspace.
