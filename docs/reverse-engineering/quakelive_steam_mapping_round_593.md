# Quake Live Steam Mapping Round 593: Win32 DirectSound DMA Alias Closure

Date: 2026-06-11

## Scope

This round closes the shared symbol bridge for the retail Win32 DirectSound DMA
backend. The source behavior was already reconstructed in `win_snd.c`; this
pass promotes the missing Ghidra `FUN_*` aliases and lowercase Binary Ninja
aliases for the eight-function DirectSound helper cluster, then pins the bridge
with parity tests.

Focused retail owners:

- `sub_4ef9f0` / `FUN_004ef9f0` -> `DSoundError`
- `sub_4efa30` / `FUN_004efa30` -> `SNDDMA_Shutdown`
- `sub_4efb80` / `FUN_004efb80` -> `SNDDMA_GetDMAPos`
- `sub_4efbf0` / `FUN_004efbf0` -> `SNDDMA_BeginPainting`
- `sub_4efd00` / `FUN_004efd00` -> `SNDDMA_Submit`
- `sub_4efd30` / `FUN_004efd30` -> `SNDDMA_Activate`
- `sub_4efd70` / `FUN_004efd70` -> `SNDDMA_InitDS`
- `sub_4f0090` / `FUN_004f0090` -> `SNDDMA_Init`

## Evidence

Observed facts:

1. Binary Ninja HLIL exposes the backend as a contiguous retail sound/DMA lane
   from `004ef9f0` through `004f0090`, including DirectSound error text,
   shutdown, DMA cursor sampling, buffer lock/recovery, submit, activation,
   DirectSound initialization, and the public `SNDDMA_Init` wrapper.
2. Ghidra `functions.csv` contains matching rows and sizes for all eight
   `FUN_*` names in the same lane.
3. `src/code/win32/win_snd.c` already carries the retail-backed source behavior
   for `s_muteBackground`, DirectSound 8 fallback, 22,050 Hz stereo 16-bit DMA,
   begin-paint lock recovery, submit/unlock, activation failure shutdown, and
   COM cleanup.

Inferred meaning:

- The missing aliases were a documentation/evidence gap, not a runtime source
  gap. The retail behavior was already represented in source and tests.
- Because `S_Update_` calls through `SNDDMA_GetDMAPos`,
  `SNDDMA_BeginPainting`, `S_PaintChannels`, and `SNDDMA_Submit`, this backend
  closure also tightens the end-to-end sound frame wiring story.

## Reconstruction

Updated `references/analysis/quakelive_symbol_aliases.json` so every Win32
DirectSound DMA helper in the cluster has:

- the Ghidra `FUN_*` alias,
- the existing uppercase Binary Ninja `sub_*` alias,
- the lowercase Binary Ninja `sub_*` alias from the HLIL text.

Expanded `tests/test_win32_sound_dma_parity.py` to assert the Ghidra aliases in
the shared symbol corpus and the newly promoted lowercase Binary Ninja aliases,
while retaining the existing function-size and HLIL/source-behavior checks.

## Validation

- `python -m json.tool references\analysis\quakelive_symbol_aliases.json | Out-Null`
- `python -m pytest tests/test_win32_sound_dma_parity.py tests/test_client_sound_playback_parity.py::test_sound_update_timing_and_dma_submit_slice_matches_retail -q --tb=short`
  - Result: `3 passed in 0.54s`
- `python -m pytest tests/test_win32_sound_dma_parity.py tests/test_client_sound_playback_parity.py tests/test_client_sound_voice_parity.py tests/test_cgame_sound_wiring_parity.py -q --tb=short`
  - Result: `38 passed in 4.63s`

No C source files changed, so no Debug|x86 rebuild or runtime launch was
required.

## Parity Estimate

- Focused Win32 DirectSound DMA Ghidra/Binary Ninja alias coverage:
  **before 54% -> after 99%**.
- Focused DirectSound backend source/evidence bridge confidence:
  **before 95% -> after 98%**.
- Overall sound-system wiring reconstruction parity:
  **93.52% -> 93.54%**.
