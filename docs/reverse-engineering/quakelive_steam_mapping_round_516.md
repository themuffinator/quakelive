# Quake Live Steam Mapping Round 516: Raw Stop-Background Import Row

## Scope

This round tightens the sound-system wiring map around the native cgame/UI
`stopBackgroundTrack` bridge. The source reconstruction already routes the
legacy VM syscall and native import surfaces to `S_StopBackgroundTrack()`;
the remaining risk was evidence drift around the retail table entry at raw
address `0x4B02F0`.

## Evidence

Observed retail facts:

- Binary Ninja HLIL part 04 promotes the adjacent start-background wrapper:
  `sub_4afed0()` tail-calls `sub_4db060()`, and the alias corpus maps
  `sub_4AFED0` to `QLCGImport_S_StartBackgroundTrack`.
- The engine stop implementation is independently named: `sub_4db030()` is
  mapped as `S_StopBackgroundTrack` and is reached from existing retail stop
  call sites.
- Binary Ninja HLIL part 07 shows the cgame native table row:
  `data_565a14 = sub_4afed0`, `data_565a18 = 0x4b02f0`,
  `data_565a1c = sub_4afee0`.
- The same HLIL table file shows the UI native row:
  `data_567450 = sub_4afff0`, `data_567454 = 0x4b02f0`,
  `data_567458 = sub_4afed0`, `data_56745c = sub_4bf290`.
- Ghidra `functions.csv` for `quakelive_steam` has stable rows for the named
  neighbors and `S_StopBackgroundTrack`, but no function row at `004b02f0`.

Inferred meaning:

- `0x4B02F0` is the raw native import thunk used for stop-background-track in
  both the cgame and UI tables. Its table position, source-side import slots,
  and command callback wiring tie it to `S_StopBackgroundTrack()`.
- Because the committed Ghidra corpus does not expose a stable function row
  at `004b02f0`, this round keeps the address mapped-only rather than adding
  `sub_4B02F0` or a fake `QL*Import_S_StopBackgroundTrack` alias.

## Reconstruction

- Hardened `tests/test_botlib_cgame_native_import_slab_parity.py` so the cgame
  sound slab checks the start/stop/R-load table sequence and explicitly
  rejects a promoted `4B02F0` Ghidra row or alias.
- Hardened `tests/test_ui_menu_files.py` so the UI bridge pins the retail
  neighbor rows around `data_567454` and applies the same no-alias guard for
  `0x4B02F0`.
- Left source code unchanged: the reconstructed cgame and UI import surfaces
  already call the shared engine stop routine through
  `trap_S_StopBackgroundTrack()` / `S_StopBackgroundTrack()`.

## Remaining Boundary

The raw thunk body remains mapped by table position instead of named as a
standalone source-owned helper. If a future Ghidra refresh produces a stable
function row at `004b02f0`, the alias can be promoted in a separate round with
the new row, HLIL body, and table-slot evidence together.

## Validation

Static checks run:

- `python -m pytest tests\test_botlib_cgame_native_import_slab_parity.py::test_native_cgame_import_slab_aliases_and_rows_are_pinned -q --tb=short`
- `python -m pytest tests\test_botlib_cgame_native_import_slab_parity.py::test_native_cgame_sound_slab_keeps_volume_slots_direct_and_legacy_slots_fixed_volume -q --tb=short`
- `python -m pytest tests\test_ui_menu_files.py::test_ui_native_import_table_matches_recovered_retail_slots tests\test_ui_menu_files.py::test_ui_sound_import_wiring_matches_retail_native_and_vm_paths -q --tb=short`
- `python -m pytest tests\test_botlib_cgame_native_import_slab_parity.py -q --tb=short`
- `python -m pytest tests\test_cgame_sound_wiring_parity.py -q --tb=short`
- `python -m pytest tests\test_ui_menu_files.py -q --tb=short`

Results: all selected checks passed (`1`, `1`, `2`, `6`, `7`, and
`83 passed, 1 skipped`, respectively).

No runtime launch is required for this mapping-only pass.

## Parity Estimate

Focused raw stop-background native import row confidence:
**before 92% -> after 98%**.

Focused cgame/UI sound bridge evidence confidence:
**before 96% -> after 98%**.

Overall sound-system wiring reconstruction parity:
**92.7% -> 92.8%**.
