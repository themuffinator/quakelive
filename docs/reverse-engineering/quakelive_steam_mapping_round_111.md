# Quake Live Steam Host Mapping Round 111

## Scope

This round continues directly from
[Round 110](./quakelive_steam_mapping_round_110.md) and takes the refreshed
largest-unaliased `quakelive_steam.exe` queue beginning with `sub_51E4F0`,
`sub_5181F0`, and `sub_50A1A0`. Each candidate was classified before opening
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
- matching owners under `src/libs/_deps/`

## Largest-Unaliased Classification

| Rank | Raw symbol | Size | Classification | Alias/action | Confidence | Source debt decision |
| ---: | --- | ---: | --- | --- | --- | --- |
| 1 | `sub_51E4F0` | `5099` | `CRT/STL` | `dradfg` alias added | High | No engine debt; bundled libvorbis FFT support. |
| 2 | `sub_5181F0` | `3610` | `CRT/STL` | `setup_tone_curves` alias added | High | No engine debt; bundled libvorbis psychoacoustic setup. |
| 3 | `sub_50A1A0` | `3327` | `CRT/STL` | `png_init_read_transformations` alias added | High | No engine debt; bundled libpng read-transform setup. |

Bucket summary:

- `engine-owned`: 0 of 3
- `platform-service-owned`: 0 of 3
- `CRT/STL`: 3 of 3
- `Awesomium`: 0 of 3
- `Steam SDK support`: 0 of 3

## Evidence Notes

### `sub_51E4F0 -> dradfg`

`sub_51E4F0` matches libvorbis `dradfg`. The HLIL body is the large
non-specialized radix helper in the small FFT pipeline: it initializes
twiddle-factor values through `_CIcos` and `_CIsin`, derives `ipph`, `ipp2`,
`idp2`, `nbd`, `t0`, and `t10`, and is reached from the factorized transform
dispatcher after the radix-4 and radix-2 fast paths.

The source owner is `src/libs/_deps/libvorbis/lib/smallft.c:270`. The local
dispatcher calls `dradfg` from `src/libs/_deps/libvorbis/lib/smallft.c:616`
and `src/libs/_deps/libvorbis/lib/smallft.c:621`, matching the binary call
shape. This is bundled support-library code and does not open engine source
debt.

### `sub_5181F0 -> setup_tone_curves`

`sub_5181F0` matches libvorbis `setup_tone_curves`. The decompiled body has
the expected psychoacoustic setup shape: `P_BANDS`, `P_LEVELS`, `EHMER_MAX`,
the large stack work buffers for tone curves and ATH curves, center boost and
center decay handling, `_ogg_malloc` table construction, and sentinel values
such as `-999`, `999`, `100`, `30`, and `10`.

The source owner is `src/libs/_deps/libvorbis/lib/psy.c:85`. The retained
caller is `_vp_psy_init`, which assigns `p->tonecurves` from
`setup_tone_curves` at `src/libs/_deps/libvorbis/lib/psy.c:326`. This is
bundled support-library code and does not open engine source debt.

### `sub_50A1A0 -> png_init_read_transformations`

`sub_50A1A0` matches libpng `png_init_read_transformations`. The binary body
is entered from the PNG read-start-row path and initializes the retained read
transform pipeline: palette and RGB transform setup, background composition,
transparency handling, gamma-table setup, palette gamma/background updates,
and significant-bit shifting through the `PNG_SHIFT` path.

The source owner is `src/libs/_deps/libpng/pngrtran.c:1415`. The caller
evidence comes from `png_read_start_row`, which invokes
`png_init_read_transformations` at `src/libs/_deps/libpng/pngrutil.c:4428`.
This is bundled support-library code and does not open engine source debt.

## New High-Confidence Aliases Added This Round

- `sub_50A1A0 -> png_init_read_transformations`
- `sub_5181F0 -> setup_tone_curves`
- `sub_51E4F0 -> dradfg`

## Verification

I validated the alias artifact directly:

- `references/analysis/quakelive_symbol_aliases.json` parses cleanly through
  `ConvertFrom-Json`
- recount after this pass: `1150` raw alias entries, `1149` address-backed
  alias entries
- top remaining unaliased function by size: `sub_4B1100` at `3172` bytes

## Completion Stats After Round 111

- Ghidra baseline: `5473` functions, `351` imports, `2` exports, `4377`
  analysis symbols
- Current mapping coverage: `1150` raw alias entries, `1149` address-backed
  aliases
- Address-backed coverage: `20.994%` of `5473` functions
- Alias delta this round: `3`
- Estimated writable-source parity for this mapping-only round: unchanged

This pass deliberately did not open source debt. It converts the former top
three unaliased entries into high-confidence bundled libvorbis/libpng support
aliases and leaves the next host queue headed by `sub_4B1100`.
