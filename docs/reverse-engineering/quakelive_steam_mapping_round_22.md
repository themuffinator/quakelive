# Quake Live Steam Host Mapping Round 22

## Scope

This round returns to the raw native `cgamex86.dll` sound-import band rooted at `data_565958` in `quakelive_steam.exe` and consumed directly through `data_1074CCCC` in native cgame. Round 21 already closed the shifted local `cgDC` control callbacks copied into `data_1074CCF8`; this pass treats the raw sound table as a separate seam and maps the retail looping / listener helpers that were still unnamed there.

The main goals were:

- close the raw sound-start, looping-sound, entity-position, and listener-spatialization wrappers
- separate the raw import table from the later local `cgDC` copy built by `sub_10029210`
- recover enough of the retail looping-sound record at `data_12B8950` to explain the helper split cleanly

The primary local evidence for this round is:

- `references/hlil/quakelive/quakelive_steam.exe/quakelive_steam.exe_hlil.txt`
- `references/hlil/quakelive/cgamex86.dll/cgamex86.dll_hlil.txt`
- `references/reverse-engineering/ghidra/quakelive_steam/functions.csv`
- `src/code/client/cl_cgame.c`
- `src/code/client/ql_cgame_imports.inc`
- `src/code/client/snd_dma.c`
- `src/code/client/snd_local.h`
- `src/code/client/snd_public.h`

## Raw Native Cgame Sound Band

Observed local facts:

1. Native cgame keeps two callback views alive at once:
   - `data_1074CCCC` is the raw import table passed in from the host
   - `sub_10029210` later copies selected entries into a local callback slab and publishes that slab through `data_1074CCF8`
2. In `quakelive_steam.exe`, the contiguous raw sound band at `data_5659EC..data_565A0C` resolves to:
   - `data_5659EC = sub_4AFE10`
   - `data_5659F0 = sub_4AFE20`
   - `data_5659F4 = sub_4BEFB0`
   - `data_5659F8 = sub_4AFE50`
   - `data_5659FC = j_sub_4DA490`
   - `data_565A00 = j_sub_4DA3E0`
   - `data_565A04 = sub_4AFE90`
   - `data_565A08 = sub_4AFEA0`
   - `data_565A0C = sub_4AFEB0`
3. Native cgame calls those raw entries directly through `data_1074CCCC + offset`; for example:
   - `(*(data_1074CCCC + 0x94))(origin, entityNum, channel, sfx)`
   - `(*(data_1074CCCC + 0xA0))(sfx, channel, volume)`
   - `(*(data_1074CCCC + 0xAC))(entityNum, origin, velocity, sfx)`
   - `(*(data_1074CCCC + 0xB0))(entityNum, origin)`
   - `(*(data_1074CCCC + 0xB4))(listenerNum, head, axis, inwater)`

That is a separate sound seam from the already-mapped local `cgDC` `startLocalSound` / `sendConsoleCommand` callbacks in Round 21.

## Raw Offset `0x94`: `S_StartSound`

The raw `+0x94` wrapper is now exact.

Observed local facts:

1. `data_5659EC = sub_4AFE10`.
2. `sub_4AFE10` is a pure tailcall into `sub_4DA350`.
3. `sub_4DA350(arg1, arg2, arg3, arg4)` tailcalls `sub_4DA050(arg1, arg2, arg3, arg4, 1.0f)`.
4. `sub_4DA050` is the retail sound-start core and emits the exact engine strings:
   - `S_StartSound: bad entitynum %i`
   - `^3S_StartSound: handle %i out of range`
5. Native cgame raw callers use `data_1074CCCC + 0x94` with the same `(origin, entityNum, entchannel, sfx)` shape seen in `trap_S_StartSound`.

That closes `sub_4AFE10` as the raw native cgame import wrapper for `S_StartSound`, with `sub_4DA350` as the default-volume engine helper and `sub_4DA050` as the retail volume-extended core.

## Raw Offsets `0x98` And `0xA0`: Retail Volume Helpers

The retail raw table carries two adjacent volume-enabled helpers not surfaced in the GPL-era import enum.

Observed local facts:

1. `data_5659F0 = sub_4AFE20`, and `sub_4AFE20` tailcalls `sub_4DA050(origin, entityNum, entchannel, sfx, volume)`.
2. That makes `sub_4AFE20` the direct raw wrapper for the same sound-start core, but with an explicit volume scalar instead of the fixed `1.0f` used by `sub_4DA350`.
3. `data_5659F8 = sub_4AFE50`, and `sub_4AFE50` tailcalls `sub_4DA380(sfx, channel, volume)`.
4. `sub_4DA380` forwards into `sub_4DA050(nullptr, data_1260948, channel, sfx, volume)` and reuses the `^3S_StartLocalSound: handle %i out of range` failure path.
5. Native cgame calls `data_1074CCCC + 0xA0` exactly like a local-sound helper with an extra scalar:
   - `(*(data_1074CCCC + 0xA0))(sfx, 6, data_10A629A8)`
   - `(*(data_1074CCCC + 0xA0))(sfx, 7, data_10A6B528)`

I did not find a clean direct raw cgame callsite for `data_1074CCCC + 0x98` in this pass, but the wrapper body itself is exact and sits contiguously in the same retail sound band.

## Retail Looping-Sound Record At `data_12B8950`

`sub_4DA4C0` is enough to recover most of the retail looping-sound layout.

Observed field writes:

- `+0x00..0x08`: origin vector
- `+0x0C`: `sfx` pointer (`arg4 * 0x58 + &data_1260950`)
- `+0x14`: active flag, set to `1`
- `+0x18`: frame marker, written from `data_1528CC0.d`
- `+0x1C..0x24`: velocity vector
- `+0x28`: doppler-enabled flag
- `+0x2C`: doppler scale
- `+0x30`: previous / default doppler scale

Observed structural facts:

1. The record stride is `0x34`.
2. The covered bank size is `0xD000`, which is `1024 * 0x34`.
3. `sub_4DA490` iterates from `0x12B8964` to `0x12C5964` in `0x34`-byte steps, clears one dword per record, and resets `data_142C2F0 = 0`.

Inference:

- The untouched `+0x10` slot is most plausibly the retail `mergeFrame` field. That matches the GPL-era ownership, and `S_AddLoopSounds` needs one record-local merge marker even though `S_AddLoopingSound` never writes it.

This record shape is a better fit for the retail sound implementation than the current GPL `loopSound_t`: it still has `framenum` and doppler-state fields, but it no longer carries the later `kill` boolean that the GPL `S_ClearLoopingSounds` uses.

## Raw Offset `0xAC`: `S_AddLoopingSound`

The raw looping-sound add path is now exact.

Observed local facts:

1. `data_565A04 = sub_4AFE90`.
2. `sub_4AFE90` tailcalls `sub_4DA4C0`.
3. `sub_4DA4C0` validates the sound handle, emits the exact failure string `^3S_AddLoopingSound: handle %i out of range`, writes the looping-sound record described above, and applies the retail doppler path.
4. Native cgame calls `data_1074CCCC + 0xAC` with the exact `entityNum, origin, velocity, sfx` shape expected by `trap_S_AddLoopingSound`.

That closes `sub_4AFE90` as the raw import wrapper for `S_AddLoopingSound` and `sub_4DA4C0` as the engine helper itself.

## Raw Offsets `0xB0` And `0xB4`: Entity Position And Listener Spatialization

The last two raw sound slots are also exact.

Observed local facts:

1. `data_565A08 = sub_4AFEA0`, and `sub_4AFEA0` tailcalls `sub_4DAC80(arg1, arg2)`.
2. `sub_4DAC80` checks `arg1` against the entity limit and emits the exact failure string `S_UpdateEntityPosition: bad entitynum %i`, then writes the origin vector into the looping-sound bank.
3. Native cgame uses `data_1074CCCC + 0xB0` with the exact `(entityNum, origin)` shape:
   - `(*(data_1074CCCC + 0xB0))(*arg1, &arg1[0xAE])`
4. `data_565A0C = sub_4AFEB0`, and `sub_4AFEB0` tailcalls `sub_4DACD0(arg1, arg2, arg3, arg4)`.
5. `sub_4DACD0` stores the listener origin, listener entity number, and a full `3x3` axis matrix, then walks the active channel bank and performs the retail spatialization update.
6. Native cgame calls `data_1074CCCC + 0xB4` with the exact listener-shape tuple:
   - `listenerNum`
   - `&data_10A9C838` for the head / origin vector
   - `&data_10A9C844` for the view-axis matrix
   - `0` or another in-water flag in the last slot

That closes `sub_4AFEA0` / `sub_4DAC80` as `S_UpdateEntityPosition` and `sub_4AFEB0` / `sub_4DACD0` as `S_Respatialize`.

## Supporting Engine Helpers

This pass also closes the exact retail engine-side helpers surrounding the raw import band:

- `sub_4DB3F0` is the exact `S_StartLocalSound` helper. It first returns silently unless the sound system is started and unmuted, then range-checks the handle, emits `^3S_StartLocalSound: handle %i out of range`, and starts the sound at the current listener with a fixed volume.
- `sub_4DA3E0` is the exact `S_ClearSoundBuffer` helper. It clears the looping-sound bank, clears loop channels, resets counters, clears the raw sample buffer, zeroes the DMA buffer, and tailcalls the device submit / reset path.
- `sub_4DB450` is the exact `S_StopAllSounds` helper. It bails if sound is not started, conditionally shuts down the background-track state, then tailcalls `sub_4DA3E0`.

I am naming the concrete helpers above rather than the tiny raw tailcall rows at `004AFE70` / `004AFE80`, because the committed `functions.csv` currently does not expose those tailcall wrappers as stable standalone function rows.

## Promoted Aliases

| Raw symbol | Alias candidate | Basis | Observed role |
| --- | --- | --- | --- |
| `sub_4AFE10` (`0x004AFE10`) | `QLCGImport_S_StartSound` | Observed | Raw native cgame import wrapper for `S_StartSound`. |
| `sub_4AFE20` (`0x004AFE20`) | `QLCGImport_S_StartSoundVolume` | Observed | Raw retail import wrapper for the volume-enabled `S_StartSound` core. |
| `sub_4AFE50` (`0x004AFE50`) | `QLCGImport_S_StartLocalSoundVolume` | Observed | Raw native cgame import wrapper for the retail local-sound helper with an explicit volume scalar. |
| `sub_4AFE90` (`0x004AFE90`) | `QLCGImport_S_AddLoopingSound` | Observed | Raw native cgame import wrapper for `S_AddLoopingSound`. |
| `sub_4AFEA0` (`0x004AFEA0`) | `QLCGImport_S_UpdateEntityPosition` | Observed | Raw native cgame import wrapper for `S_UpdateEntityPosition`. |
| `sub_4AFEB0` (`0x004AFEB0`) | `QLCGImport_S_Respatialize` | Observed | Raw native cgame import wrapper for `S_Respatialize`. |
| `sub_4DA050` (`0x004DA050`) | `S_StartSoundVolume` | Observed | Retail sound-start core with an explicit volume scalar. |
| `sub_4DA350` (`0x004DA350`) | `S_StartSound` | Observed | Default-volume wrapper over `S_StartSoundVolume`. |
| `sub_4DA380` (`0x004DA380`) | `S_StartLocalSoundVolume` | Observed | Retail helper that starts a listener-local sound with an explicit volume scalar. |
| `sub_4DA3E0` (`0x004DA3E0`) | `S_ClearSoundBuffer` | Observed | Retail full sound-buffer clear / DMA-reset helper. |
| `sub_4DA4C0` (`0x004DA4C0`) | `S_AddLoopingSound` | Observed | Retail looping-sound record writer with doppler handling. |
| `sub_4DAC80` (`0x004DAC80`) | `S_UpdateEntityPosition` | Observed | Retail entity-position update helper for the looping-sound bank. |
| `sub_4DACD0` (`0x004DACD0`) | `S_Respatialize` | Observed | Retail listener spatialization helper. |
| `sub_4DB3F0` (`0x004DB3F0`) | `S_StartLocalSound` | Observed | Retail fixed-volume local sound helper. |
| `sub_4DB450` (`0x004DB450`) | `S_StopAllSounds` | Observed | Retail top-level sound shutdown helper. |

## Open Questions

1. `data_5659E8 = sub_4AFE00` is still unresolved. It sits immediately ahead of the raw sound band and likely belongs to the same subsystem, but the dynamic jump target `data_146CCBC` is still too weak to promote.
2. I am intentionally not renaming the direct raw `+0x9C` users in this pass. Round 21 already closed the copied local `cgDC` `startLocalSound` callback precisely; the remaining direct `data_1074CCCC + 0x9C` callers deserve a separate pass so I do not conflate the raw and copied seams.
3. `sub_4DA490` is semantically bounded as the lightweight retail looping-sound clear helper, but the committed Ghidra export does not currently surface a stable `004DA490` row, so I am keeping it documented but unaliased for now.
