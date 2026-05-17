# `src/code/null/null_snddma.c` Gap Note

Last updated: 2026-05-17

Gap family: `RW-G02`
- Owning retail binary: `assets/quakelive/quakelive_steam.exe` for engine-owned surfaces, or the corresponding committed module corpus when this file sits in a module tree.
- Current classification: Open repo-wide gap; the file is an explicitly silent sound/device compatibility shim.

## Why this file is still open

This file honestly exposes the current sound entry points, but it still resolves them through a silent compatibility sink or no-op behavior, which keeps the null runtime outside any repo-wide parity closure claim.

## Observed facts

- `SNDDMA_Init()` now returns `qtrue` for a local silent DMA sink and seeds the shared `dma` shape with a 22,050 Hz, 16-bit stereo buffer.
- `SNDDMA_GetDMAPos()` advances that sink from `Sys_Milliseconds()`, while `SNDDMA_Shutdown()`, `SNDDMA_BeginPainting()`, and `S_ClearSoundBuffer()` clear the retained silent buffer/state.
- Submit, activation, local-sound, registration, and voice-sample entry points remain compatibility-safe no-ops.
- The repo-wide audit explicitly classifies these sound/device activation and voice surfaces as shims, not as portability closure.

## Function-by-function status

| Function | Status | Notes |
| --- | --- | --- |
| `SNDDMA_ClearNullState` | `bounded compatibility` | Clears the local silent DMA sink state. |
| `SNDDMA_Init` | `bounded compatibility` | Seeds a local silent DMA sink rather than failing initialization outright. |
| `SNDDMA_GetDMAPos` | `bounded compatibility` | Advances the silent DMA cursor from host milliseconds. |
| `SNDDMA_Shutdown` | `bounded compatibility` | Clears the silent DMA sink state. |
| `SNDDMA_BeginPainting` | `bounded compatibility` | Clears the silent DMA buffer before mixing. |
| `SNDDMA_Submit` | `bounded compatibility` | Silent compatibility no-op. |
| `SNDDMA_Activate` | `open portability owner` | Silent sound or voice compatibility stub. |
| `S_RegisterSound` | `open portability owner` | Silent sound or voice compatibility stub. |
| `S_StartLocalSound` | `open portability owner` | Silent sound or voice compatibility stub. |
| `S_ClearSoundBuffer` | `bounded compatibility` | Clears the silent DMA buffer and resets the local cursor. |
| `S_AddVoiceSamples` | `open portability owner` | Silent sound or voice compatibility stub. |

## Closure target

- Keep the file explicitly classified as a silent compatibility shim unless the null runtime grows a richer audio target.
