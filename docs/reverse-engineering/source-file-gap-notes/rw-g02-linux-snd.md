# `src/code/unix/linux_snd.c` Gap Note

Last updated: 2026-05-17

Gap family: `RW-G02`
- Owning retail binary: `assets/quakelive/quakelive_steam.exe` for engine-owned surfaces, or the corresponding committed module corpus when this file sits in a module tree.
- Current classification: Open repo-wide gap; this OSS audio host path remains part of the unresolved non-Windows client/runtime lane.

## Why this file is still open

The file still implements a classic `/dev/dsp` OSS path, which the repo-wide audit does not treat as closed portability proof for a Linux client/runtime replacement target. The current source now also carries a bounded silent DMA sink for `snddevice null`, `none`, or `silent`, but that is a headless compatibility bridge rather than ALSA/PulseAudio/SDL modernization.

## Observed facts

- Audio initialisation still opens `snddevice`, which defaults to `/dev/dsp`, unless the operator explicitly selects the silent DMA sink through `snddevice null`, `none`, or `silent`.
- The file owns the OSS capability probing, format selection, and mmap-backed DMA path.
- `SNDDMA_Shutdown()` now unmaps the OSS DMA buffer and closes `audio_fd`, so sound restart/error paths no longer leave the Unix host descriptor and mapping behind.
- The repo-wide audit still classifies Linux client/runtime support as compatibility-only rather than closed parity.

## Function-by-function status

| Function | Status | Notes |
| --- | --- | --- |
| `Snd_Memset` | `bounded compatibility` | Still supports the retained OSS mmap fallback, not a broader modern audio backend. |
| `SNDDMA_InitCvars` | `bounded compatibility` | Centralises the retained `sndbits`, `sndspeed`, `sndchannels`, and `snddevice` cvar setup. |
| `SNDDMA_IsNullDevice` | `bounded compatibility` | Classifies the explicit silent sink aliases. |
| `SNDDMA_InitNull` | `bounded compatibility` | Provides the headless silent DMA sink without external audio libraries. |
| `SNDDMA_Init` | `open portability owner` | Still defaults to the unresolved OSS `/dev/dsp` sound host path, with an explicit silent-sink escape hatch. |
| `SNDDMA_GetDMAPos` | `bounded compatibility` | Advances the silent sink from `Sys_Milliseconds()` and otherwise defers to OSS `SNDCTL_DSP_GETOPTR`. |
| `SNDDMA_Shutdown` | `bounded compatibility` | Now tears down the silent sink or unmaps/closes the OSS backend. |
| `SNDDMA_Submit` | `open portability owner` | Still no real non-OSS modern backend submit path. |
| `SNDDMA_BeginPainting` | `bounded compatibility` | Clears the silent DMA buffer before mixing. |

## Closure target

- Either modernise the Linux sound host and validate it as an actual portability target or keep this file explicitly compatibility-only. The silent sink and OSS cleanup reduce runtime friction, but they do not close the broader Linux audio parity lane.
