# Quake Live Steam Host Mapping Round 115

## Scope

This round continues directly from
[Round 114](./quakelive_steam_mapping_round_114.md) and takes the refreshed
largest-unaliased `quakelive_steam.exe` queue beginning with `sub_4224E0`,
`sub_4E8C80`, and `sub_517620`. Each candidate was classified before opening
source debt.

Classification buckets for this round:

- `engine-owned`: retained Quake III or Quake Live engine behavior with a
  matching source owner.
- `platform-service-owned`: Quake Live service glue outside normal engine
  ownership.
- `CRT/STL`: CRT, STL, or bundled third-party support-library code statically
  linked into the host binary.
- `Awesomium`: browser runtime or Awesomium support code.
- `Steam SDK support`: Steamworks SDK callback, helper, or support code.

The evidence order for this pass was:

- `references/reverse-engineering/ghidra/quakelive_steam/functions.csv`
- `references/hlil/quakelive/quakelive_steam.exe/quakelive_steam.exe_hlil_split/`
- `references/reverse-engineering/ghidra/quakelive_steam/decompile_top_functions.c`
- `references/reverse-engineering/ghidra/quakelive_steam/analysis_symbols.txt`
- matching owners under `src/code/qcommon/` and `src/libs/_deps/libvorbis/`
- upstream libzmq `src/stream_engine.cpp` naming for the statically linked
  ZeroMQ method

## Largest-Unaliased Classification

| Rank | Raw symbol | Size | Classification | Alias/action | Confidence | Source debt decision |
| ---: | --- | ---: | --- | --- | --- | --- |
| 1 | `sub_4224E0` | `2491` | `platform-service-owned` | `zmq_stream_engine_t_handshake` alias added | High | No new debt opened; this is internal libzmq support under the existing ZMQ service lane. |
| 2 | `sub_4E8C80` | `2484` | `CRT/STL` | `inflate_blocks` alias added | High | No engine debt; bundled zlib inflate-block support. |
| 3 | `sub_517620` | `2392` | `CRT/STL` | `vorbis_synthesis_blockin` alias added | High | No engine debt; bundled libvorbis synthesis support. |

Bucket summary:

- `engine-owned`: 0 of 3
- `platform-service-owned`: 1 of 3
- `CRT/STL`: 2 of 3
- `Awesomium`: 0 of 3
- `Steam SDK support`: 0 of 3

## Evidence Notes

### `sub_4224E0 -> zmq_stream_engine_t_handshake`

`sub_4224E0` matches upstream libzmq `zmq::stream_engine_t::handshake`. The
HLIL function is typed as a `zmq::stream_engine_t` method lane by the nearby
RTTI/vtable anchors in `analysis_symbols.txt`, and the body carries the
`..\..\..\src\stream_engine.cpp` assertions for `handshaking` and
`greeting_bytes_read < greeting_size`.

The function receives the ZeroMQ greeting, distinguishes unversioned peers from
versioned ZMTP peers, emits the major/minor version and mechanism bytes,
asserts `options.mechanism == ZMQ_NULL || options.mechanism == ZMQ_PLAIN ||
options.mechanism == ZMQ_CURVE`, and then allocates the expected v1/v2
encoder/decoder plus `NULL`, `PLAIN`, or `CURVE` mechanism handlers. This is
platform-service support for the retained ZeroMQ runtime, not engine logic,
Steam SDK code, or Awesomium code.

The alias uses an identifier-safe spelling of the upstream C++ method name:
`zmq_stream_engine_t_handshake`.

### `sub_4E8C80 -> inflate_blocks`

`sub_4E8C80` matches bundled zlib `inflate_blocks`. The decompiled body is the
classic inflate block state machine with `TYPE`, `LENS`, `STORED`, `TABLE`,
`BTREE`, `DTREE`, `CODES`, `DRY`, `DONE`, and `BAD` states. The preserved
diagnostic strings match the source owner exactly: `invalid block type`,
`invalid stored block lengths`, `too many length or distance symbols`, and
`invalid bit length repeat`.

The source owner is `src/code/qcommon/unzip.c:2578`, with a duplicate bundled
copy under `src/libs/pak/unzip.cpp:2828`. This is bundled support-library
code and does not open engine source debt.

### `sub_517620 -> vorbis_synthesis_blockin`

`sub_517620` matches libvorbis `vorbis_synthesis_blockin`. The caller at
`sub_4FCAB0` feeds a decoded `vorbis_block` into the retained DSP state, then
queries `vorbis_synthesis_pcmout`, matching the normal libvorbis decode loop.
The function itself checks `OV_EINVAL`, shifts `lW`, `W`, and `nW`, resets
sequence/granule tracking on discontinuity, accumulates `glue_bits`,
`time_bits`, `floor_bits`, and `res_bits`, performs the four overlap-add
cases using `_vorbis_window_get`, copies the next half-block, and clamps
`pcm_current` / `pcm_returned` from `granulepos` and `eofflag`.

The source owner is `src/libs/_deps/libvorbis/lib/block.c:721`. This is
bundled support-library code and does not open engine source debt.

## New High-Confidence Aliases Added This Round

- `sub_4224E0 -> zmq_stream_engine_t_handshake`
- `sub_4E8C80 -> inflate_blocks`
- `sub_517620 -> vorbis_synthesis_blockin`

## Verification

I validated the alias artifact directly:

- `references/analysis/quakelive_symbol_aliases.json` parses cleanly through
  `ConvertFrom-Json`
- recount after this pass: `1162` raw alias entries, `1161` address-backed
  alias entries
- top remaining unaliased function by size: `sub_4C2170` at `2388` bytes

## Completion Stats After Round 115

- Ghidra baseline: `5473` functions, `351` imports, `2` exports, `4377`
  analysis symbols
- Current mapping coverage: `1162` raw alias entries, `1161` address-backed
  aliases
- Address-backed coverage: `21.213%` of `5473` functions
- Alias delta this round: `3`
- Estimated writable-source parity for this mapping-only round: unchanged

This pass deliberately did not open source debt. It classifies the former top
three unaliased entries as one platform-service ZeroMQ support method and two
bundled support-library functions, leaving the next host queue headed by
`sub_4C2170`.
