# Quake Live Steam Host Mapping Round 267

## Scope

This pass tightened the `cg_main.c` command/configstring/music bridge that sits
between server command parsing, cached game-state strings, and the sound import
table.

The directly checked helpers were:

- `0x10020DB0 -> CG_Argv`
- `0x100252F0 -> CG_ConfigString`
- `0x10025320 -> CG_StartMusic`

## Evidence

- `references/hlil/quakelive/cgamex86.dll/cgamex86.dll_hlil.txt` shows
  `0x10020DB0` calling the argv import through `data_1074cccc + 0x30` into a
  static `0x400` byte buffer and returning that buffer.
- The same HLIL file shows `0x100252F0` bounds-checking the requested
  configstring index against `0x400`, erroring with
  `CG_ConfigString: bad index: %i`, then returning the cached string-data base
  plus the indexed offset.
- `0x10025320` reads the music configstring slot, parses two tokens, and calls
  the background-track import through `data_1074cccc + 0xBC`.
- `references/analysis/quakelive_symbol_aliases.json` and
  `references/symbol-maps/cgame.json` both carry the same recovered names for
  these three helpers.

## Source Updates

- Added richer required function headers above `CG_Argv`, `CG_ConfigString`,
  and `CG_StartMusic`.
- Preserved behavior:
  - `CG_Argv` still routes through `trap_Argv` into the static
    `MAX_STRING_CHARS` buffer.
  - `CG_ConfigString` still returns the cached `cgs.gameState` string pointer.
  - `CG_StartMusic` still parses `CS_MUSIC` into the intro and loop track
    names before calling `trap_S_StartBackgroundTrack`.

## Tests

- `tests/test_cgame_displaycontext_parity.py` now checks the source-side
  wrappers against the committed HLIL blocks and verifies the symbol-map/alias
  evidence for the three recovered names.

## Parity Estimate

- Before: command/configstring/music bridge source-compliance and evidence
  parity was about 98%.
- After: about 98.5%.

This round was intentionally behavior-neutral.
