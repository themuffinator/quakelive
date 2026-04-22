# `src/code/unix/linux_snd.c` Gap Note

Last updated: 2026-04-22

Gap family: `RW-G02`
- Owning retail binary: `assets/quakelive/quakelive_steam.exe` for engine-owned surfaces, or the corresponding committed module corpus when this file sits in a module tree.
- Current classification: Open repo-wide gap; this OSS audio host path remains part of the unresolved non-Windows client/runtime lane.

## Why this file is still open

The file still implements a classic `/dev/dsp` OSS path, which the repo-wide audit does not treat as closed portability proof for a Linux client/runtime replacement target.

## Observed facts

- Audio initialisation still opens `snddevice`, which defaults to `/dev/dsp`.
- The file owns the OSS capability probing, format selection, and mmap-backed DMA path.
- The repo-wide audit still classifies Linux client/runtime support as compatibility-only rather than closed parity.

## Function-by-function status

| Function | Status | Notes |
| --- | --- | --- |
| `Snd_Memset` | `open portability owner` | This function is part of the still-open OSS/Linux sound host path. |
| `SNDDMA_Init` | `open portability owner` | This function is part of the still-open OSS/Linux sound host path. |
| `SNDDMA_GetDMAPos` | `open portability owner` | This function is part of the still-open OSS/Linux sound host path. |
| `SNDDMA_Shutdown` | `open portability owner` | This function is part of the still-open OSS/Linux sound host path. |
| `SNDDMA_Submit` | `open portability owner` | This function is part of the still-open OSS/Linux sound host path. |
| `SNDDMA_BeginPainting` | `open portability owner` | This function is part of the still-open OSS/Linux sound host path. |

## Closure target

- Either modernise the Linux sound host and validate it as an actual portability target or keep this file explicitly compatibility-only.
