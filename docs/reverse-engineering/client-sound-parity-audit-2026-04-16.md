# Client Sound Parity Audit - 2026-04-16

## Scope

This audit rechecked the writable client sound path against the committed retail
Quake Live corpus, focusing on the host-side client audio and Steam voice
transport seams that still sat outside the already-mapped retained Quake III
`snd_dma.c` / `snd_mix.c` / `snd_mem.c` closures.

Primary evidence:

- `references/hlil/quakelive/quakelive_steam.exe/quakelive_steam.exe_hlil.txt`
- `docs/reverse-engineering/quakelive_steam_mapping_round_06.md`
- `docs/reverse-engineering/quakelive_steam_mapping_round_19.md`
- `docs/reverse-engineering/quakelive_steam_mapping_round_22.md`
- `docs/reverse-engineering/quakelive_steam_mapping_round_59.md`
- `docs/reverse-engineering/quakelive_steam_mapping_round_60.md`
- `src/code/client/snd_dma.c`
- `src/code/client/snd_mix.c`
- `src/code/client/cl_main.c`
- `src/code/client/snd_ogg_decode.c`
- `src/common/platform/platform_steamworks.c`

## Confirmed Gaps Before This Pass

1. Retail exposes `S_StartSoundVolume` and `S_StartLocalSoundVolume`, and the
   native cgame import table already carried those slots, but the writable
   source still discarded the incoming `volume` scalar and always called the
   fixed-volume helpers.
2. Retail `S_ClearSoundBuffer` clears a separate five-lane voice ring rooted at
   `data_13e1860`, and retail `S_PaintChannels` mixes that voice bank before
   normal channels. The writable source had no equivalent voice-channel state
   or mixer path.
3. Retail `S_Init` registers `s_voiceStep` and `s_pvs`, and those values are
   used by the voice-buffer scheduling and sound-PVS gating paths
   respectively. The writable source had neither cvar.
4. Retail `SteamClient_Frame` runs three sound-adjacent duties that the source
   still lacked:
   - outgoing voice capture/send on Steam P2P channel `1`
   - incoming voice packet drain/decompress on channel `1`
   - client-side P2P session acceptance
5. Retail incoming voice checks the local mute set before publishing speaking
   state and feeding PCM into the mixer. The source had the mute set in
   `cl_cgame.c`, but no host-side query surface for `cl_main.c`.

## Closures Implemented In This Pass

1. Restored the retail volume-aware sound starts in the engine sound surface
   and rewired the native cgame wrappers to call them instead of dropping the
   scalar.
2. Added the retail-shaped five-lane circular voice buffer, `s_voiceStep`
   scheduling, `s_pvs` spatial culling gate, and top-level voice accumulation
   in `S_PaintChannels`.
3. Reconstructed the client-side Steam networking and voice wrappers needed by
   the retail host:
   - `SteamAPI_SteamNetworking`
   - client P2P send / available / read / accept helpers
   - Steam user voice start / stop / get / decompress / optimal-rate helpers
4. Extended `cl_main.c` so the client Steam frame now:
   - runs callbacks
   - sends captured voice to the published server SteamID
   - accepts incoming P2P sessions
   - reads relayed voice packets
   - applies the local mute set
   - updates the speaking-state sidecar
   - feeds decompressed PCM into the sound voice mixer
5. Added focused structural tests covering the reconstructed sound and Steam
   voice lane.
6. Restored the retail sound-cache allocator lifecycle in `snd_mem.c` and
   `snd_dma.c`:
   - `com_soundMegs` now defaults to the retail `16`
   - `S_BeginRegistration` now tears down and rebuilds the sound slab every
     pass
   - `S_Shutdown` now frees the sound slab and removes the exact retail
     command names
   - the sound-memory summary string now matches the retail wording
7. Added the retail `S_LoadSound` filesystem retry branch that reattempts
   sound loads with a default `.ogg` extension when the original path is
   missing before giving up.
8. Restored the retail OGG background-track update failure path:
   - decoder reads now log the retail `OGG_UpdateBackgroundTrack` status line
   - decoder failures close the OGG state immediately
   - short reads and failures both flow through the same loop-restart / stop
     path as the retail host
9. Aligned the in-memory Vorbis decode helper with the retail mono-only
   contract:
   - non-mono OGG assets now fail with the retail-style `is not a mono file`
     diagnostic instead of being source-only downmixed
   - Vorbis read failures now log the retail `OGG_Decode` status line
   - the callback table now mirrors the retail read/seek/tell-only setup

## Residual Notes

1. The five-lane voice-buffer replacement policy was reconstructed from HLIL
   threshold behavior and the committed mapping notes, but still deserves a
   runtime revalidation pass if we later collect a dedicated retail/client
   voice evidence bundle.
2. No further writable client-audio parity gaps are currently confirmed from
   the audited retail helper cluster. Any remaining work in this area is now
   lower-confidence revalidation rather than a source-visible mismatch.
