# `src/code/null/null_snddma.c` Gap Note

Last updated: 2026-04-22

Gap family: `RW-G02`
- Owning retail binary: `assets/quakelive/quakelive_steam.exe` for engine-owned surfaces, or the corresponding committed module corpus when this file sits in a module tree.
- Current classification: Open repo-wide gap; the file is an explicitly silent sound/device compatibility shim.

## Why this file is still open

This file honestly exposes the current sound entry points, but it still resolves every one of them to silent or no-op behavior, which keeps the null runtime outside any repo-wide parity closure claim.

## Observed facts

- `SNDDMA_Init()` returns `qfalse`.
- DMA position, shutdown, begin-painting, submit, activation, local-sound, and voice-sample entry points are all compatibility-safe no-ops.
- The repo-wide audit explicitly classifies these sound/device activation and voice surfaces as shims, not as portability closure.

## Function-by-function status

| Function | Status | Notes |
| --- | --- | --- |
| `SNDDMA_Init` | `open portability owner` | Silent sound or voice compatibility stub. |
| `SNDDMA_GetDMAPos` | `open portability owner` | Silent sound or voice compatibility stub. |
| `SNDDMA_Shutdown` | `open portability owner` | Silent sound or voice compatibility stub. |
| `SNDDMA_BeginPainting` | `open portability owner` | Silent sound or voice compatibility stub. |
| `SNDDMA_Submit` | `open portability owner` | Silent sound or voice compatibility stub. |
| `SNDDMA_Activate` | `open portability owner` | Silent sound or voice compatibility stub. |
| `S_RegisterSound` | `open portability owner` | Silent sound or voice compatibility stub. |
| `S_StartLocalSound` | `open portability owner` | Silent sound or voice compatibility stub. |
| `S_ClearSoundBuffer` | `open portability owner` | Silent sound or voice compatibility stub. |
| `S_AddVoiceSamples` | `open portability owner` | Silent sound or voice compatibility stub. |

## Closure target

- Keep the file explicitly classified as a silent compatibility shim unless the null runtime grows a richer audio target.
