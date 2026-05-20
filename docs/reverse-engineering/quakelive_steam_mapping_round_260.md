# Quake Live Steam Host Mapping Round 260

## Scope

This round focuses on `src/code/cgame/cg_main.c` and the directly related
cgame wiring that hangs off the recovered native cgame entry table.

Primary evidence:

- `references/reverse-engineering/ghidra/cgamex86/metadata.txt`
- `references/reverse-engineering/ghidra/cgamex86/functions.csv`
- `references/reverse-engineering/ghidra/cgamex86/exports.txt`
- `references/reverse-engineering/ghidra/cgamex86/analysis_symbols.txt`
- `references/hlil/quakelive/cgamex86.dll/cgamex86.dll_hlil_split/cgamex86.dll_hlil_part01.txt`
- `references/hlil/quakelive/cgamex86.dll/cgamex86.dll_hlil_split/cgamex86.dll_hlil_part02.txt`
- `references/symbol-maps/cgame.json`
- `references/analysis/quakelive_symbol_aliases.json`
- `src/code/cgame/cg_main.c`
- `src/code/cgame/cg_public.h`
- `src/code/cgame/cg_newdraw.c`
- `src/code/qcommon/vm.c`

## Native Cgame Entry Spine

Observed corpus facts:

1. `cgamex86.dll` has 751 recovered Ghidra functions, 55 imports, and two PE
   exports: `dllEntry` and `entry`.
2. HLIL `dllEntry` at `0x10020A70` writes the export table pointer rooted at
   `data_100769A8`, caches the host import/syscall table, writes API version
   `8`, and returns the caller-provided export holder.
3. The table at `data_100769A8` contains the established cgame native export
   sequence: init, register-cvars, shutdown, console-command, draw-frame,
   crosshair, attacker, key/mouse/event handling, tracked-player notifiers,
   chat down/up, physics-time, client-identity copy, one literal null slot,
   chat-field helpers, and speaking-state.
4. Current `cg_public.h`, `cg_main.c`, and `vm.c` already preserve that native
   table shape, including the deliberate null slot and the explicit integer
   wrappers for the chat-field and speaking-state tail.
5. HLIL for `CG_InitDisplayContext` at `0x10029210` still agrees with the
   current callback table wiring: ownerdraw, value, visibility, menu-script,
   cvar-string, binding, feeder, text, cinematic, widescreen-adjustment, and
   print/error callbacks are assigned before publishing `cgDC` through
   `Init_Display`.

The source change in `cg_main.c` is therefore deliberately small: the
crosshair-player and last-attacker native export helpers now carry the standard
function header comments and the crosshair helper indentation is normalized.
No behavior changed in the entry/export ABI.

## Related Score Wiring Guard

The focused cgame tests exposed a stale assertion in
`tests/test_cgame_spectator_parity.py`: it expected the red/blue team-score
calls to live inside `CG_DrawScoreValue`. That conflicts with the stronger
retail evidence already encoded in `references/symbol-maps/cgame.json` and
`tests/test_cgame_displaycontext_parity.py`.

Observed retail split:

- `CG_DrawScoreValue` / `0x100323D0` owns `CG_PLAYER_SCORE`, `CG_1STPLACE`,
  and `CG_2NDPLACE`.
- `CG_DrawTeamScore` / `0x1002FF50` owns `CG_RED_SCORE` and `CG_BLUE_SCORE`.
- The current ownerdraw dispatcher in `cg_newdraw.c` preserves that split by
  routing player and placement score ownerdraws through `CG_DrawScoreValue`,
  while red/blue team scores route to `CG_DrawTeamScore`.

The spectator parity guard now checks that dispatcher wiring directly instead
of trying to force team-score cases into the score-value helper.

## Validation

Command run:

```text
python -m pytest tests/test_cgame_displaycontext_parity.py tests/test_cl_console_cgame_parity.py tests/test_cgame_spectator_parity.py tests/test_cgame_scoreboard_social_parity.py tests/test_cgame_buffered_chat_parity.py -q
```

Result:

- `118 passed in 0.74s`

No runtime launch was performed. The committed cgame HLIL/Ghidra corpus and the
focused parity tests were sufficient for this static source/wiring pass.

## Parity Estimate

Estimated `cg_main.c` and directly related cgame wiring parity improves
**98% -> 98%**. This round mostly confirms that the recovered native entry spine
is already aligned and tightens the test evidence around an adjacent HUD score
split, rather than adding a new behavioral reconstruction.
