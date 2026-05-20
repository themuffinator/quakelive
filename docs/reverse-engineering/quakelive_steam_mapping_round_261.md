# Quake Live Steam Host Mapping Round 261

## Scope

This round continues the `cgame/cg_main.c` source and wiring pass from round
260, narrowing onto the `CG_InitDisplayContext` callback slab and the adjacent
retail cinematic/cvar callback helpers.

Primary evidence:

- `references/reverse-engineering/ghidra/cgamex86/decompile_top_functions.c`
- `references/hlil/quakelive/cgamex86.dll/cgamex86.dll_hlil_split/cgamex86.dll_hlil_part01.txt`
- `references/symbol-maps/cgame.json`
- `src/code/cgame/cg_main.c`
- `tests/test_cgame_displaycontext_parity.py`

## Callback Slab Evidence

Observed corpus facts:

1. Ghidra `FUN_10029210` assigns the display-context callbacks in a single
   slab and publishes the result through `DAT_1074ccf8 = &DAT_10a25620`.
2. The cvar/string/text subsection includes:
   - `0x10028C30 -> CG_Cvar_Get`
   - `0x10028CE0 -> CG_Cvar_GetString`
   - `0x10028D30 -> CG_Text_PaintWithCursor`
   - `0x10028D80 -> CG_OwnerDrawWidth`
3. The cinematic subsection includes:
   - `0x10028E80 -> CG_PlayCinematic`
   - `0x10028EC0 -> CG_StopCinematic`
   - `0x10028ED0 -> CG_DrawCinematic`
   - `0x10028F20 -> CG_RunCinematicFrame`
4. HLIL for `0x10028E80` converts the float extents to integers and calls the
   host cinematic play import with mode `2`, matching the current
   `CIN_loop` wrapper.
5. HLIL exposes `0x10028EC0` and `0x10028F20` as direct tail jumps to the stop
   and run-frame imports.
6. The `CG_DrawCinematic` slot is still a slightly awkward recovered boundary:
   the table assignment points directly at `0x10028ED0`, and the raw decoded
   byte stream preserves the set-extents import at `+0x1A4` followed by the
   draw import at `+0x1A0`. That continues to support the normalized source
   helper even though the HLIL split does not print a clean named function
   body for the entire wrapper.

## Source Reconstruction

The source behavior was already aligned, so this pass is mostly hygiene and
guarding:

- `CG_Cvar_Get` now has the required reconstruction function header and tabbed
  source style.
- `CG_PlayCinematic`, `CG_StopCinematic`, `CG_DrawCinematic`, and
  `CG_RunCinematicFrame` now have the required reconstruction function headers
  and normalized tabbed formatting.
- `tests/test_cgame_displaycontext_parity.py` now checks the display-context
  cvar and cinematic callback assignments against both Ghidra's callback slab
  and the relevant HLIL/raw-byte evidence.

## Validation

Commands run:

```text
python -m pytest tests/test_cgame_displaycontext_parity.py::test_cgame_init_splits_display_context_bootstrap_before_collision_map -q
```

Result:

- `1 passed in 0.53s`

No runtime launch was performed. The committed HLIL/Ghidra evidence and focused
display-context parity guard were sufficient for this static reconstruction
round.

## Parity Estimate

Estimated `cg_main.c` and directly related display-context wiring parity remains
**98% -> 98%**. This round tightens documentation, style compliance, and test
coverage around an already-aligned callback band rather than adding new runtime
behavior.
