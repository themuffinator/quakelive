# Quake Live Steam Host Mapping Round 119

## Scope

This round continues directly from
[Round 118](./quakelive_steam_mapping_round_118.md) and maps a broad pass over
the refreshed largest-unaliased `quakelive_steam.exe` queue. The pass began
with `sub_5099C0`, `sub_5076D0`, and `sub_491050`, then continued through the
next largest high-confidence candidates before opening any source debt.

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
- `references/reverse-engineering/ghidra/quakelive_steam/decompile_top_functions.c`
- `references/hlil/quakelive/quakelive_steam.exe/quakelive_steam.exe_hlil_split/`
- `references/reverse-engineering/ghidra/quakelive_steam/analysis_symbols.txt`
- matching owners under `src/code/botlib/`, `src/code/qcommon/`,
  `src/code/jpeg-6/`, `src/libs/_deps/libpng/`,
  `src/libs/_deps/libvorbis/`, `src/libs/_deps/zlib/`, and
  `src/libs/pak/`

## Largest-Unaliased Classification

| Rank | Raw symbol | Size | Classification | Alias/action | Confidence | Source debt decision |
| ---: | --- | ---: | --- | --- | --- | --- |
| 1 | `sub_5099C0` | `1780` | `CRT/STL` | `png_build_gamma_table` alias added | High | No engine debt; bundled libpng transform support. |
| 2 | `sub_5076D0` | `1777` | `CRT/STL` | `png_do_rgb_to_gray` alias added | High | No engine debt; bundled libpng transform support. |
| 3 | `sub_491050` | `1772` | `engine-owned` | `AAS_Reachability_WalkOffLedge` alias added | High | No new debt; source owner already exists in `be_aas_reach.c`. |
| 4 | `sub_475ED0` | `1764` | `CRT/STL` | `forward_DCT_float` alias added | High | No engine debt; bundled IJG JPEG encoder support. |
| 5 | `sub_427940` | `1760` | `platform-service-owned` | `zmq_plain_mechanism_t_send_zap_request` alias added | Medium-high | No engine debt; ZeroMQ PLAIN authentication support. |
| 6 | `sub_49BAE0` | `1732` | `engine-owned` | `BotReplyChat` alias added | High | No new debt; source owner already exists in `be_ai_chat.c`. |
| 7 | `sub_519020` | `1727` | `CRT/STL` | `_vp_psy_init` alias added | High | No engine debt; bundled libvorbis psychoacoustic setup. |
| 8 | `sub_4C1AA0` | `1716` | `engine-owned` | `CM_AddFacetBevels` alias added | High | No new debt; source owner already exists in `cm_patch.c`. |
| 9 | `sub_4814A0` | `1702` | `CRT/STL` | `jpeg_idct_float` alias added | High | No engine debt; bundled IJG JPEG decoder support. |
| 10 | `sub_41F3C0` | `1701` | `platform-service-owned` | `zmq_mtrie_t_rm_helper` alias added | High | No engine debt; ZeroMQ subscription trie support. |
| 11 | `sub_500CC8` | `1642` | `CRT/STL` | `inflate_fast` alias added | High | No engine debt; bundled zlib inflate fast path. |
| 12 | `sub_4E8390` | `1575` | `CRT/STL` | `inflate_codes` alias added | High | No engine debt; legacy minizip/zlib inflate support. |

Bucket summary:

- `engine-owned`: 3 of 12
- `platform-service-owned`: 2 of 12
- `CRT/STL`: 7 of 12
- `Awesomium`: 0 of 12
- `Steam SDK support`: 0 of 12

## Evidence Notes

### `sub_5099C0 -> png_build_gamma_table`

`sub_5099C0` builds libpng gamma lookup tables. The function uses `pow`, allocates
gamma-table storage, fills 8-bit and 16-bit table variants, and writes the same
png struct fields used by `png_build_gamma_table` in
`src/libs/_deps/libpng/png.c:3613`.

### `sub_5076D0 -> png_do_rgb_to_gray`

`sub_5076D0` performs the libpng RGB/RGBA to gray/gray-alpha transform. It uses
the red and green coefficients from the png struct, handles 8-bit and 16-bit
rows, applies gamma tables when present, and matches the row-info updates from
`src/libs/_deps/libpng/pngrtran.c:3119`.

### `sub_491050 -> AAS_Reachability_WalkOffLedge`

`sub_491050` walks AAS faces, tests face flags and client bounding-box traces,
rejects existing reachabilities, lava/slime, non-grounded destinations, and
cluster-portal paths, then emits `TRAVEL_WALKOFFLEDGE` reachabilities using
`rs_startwalkoffledge`. The source owner is
`src/code/botlib/be_aas_reach.c:4131`.

### `sub_475ED0 -> forward_DCT_float`

`sub_475ED0` is the IJG JPEG floating-point forward DCT wrapper. It loads eight
8-byte sample rows, subtracts `CENTERJSAMPLE`, calls the configured float DCT
method, then stores rounded 64-coefficient blocks using the `+16384.5 - 16384`
rounding idiom from `src/code/jpeg-6/jcdctmgr.c`.

### `sub_427940 -> zmq_plain_mechanism_t_send_zap_request`

`sub_427940` is ZeroMQ PLAIN authentication support. The surrounding HLIL shows
it is called after a PLAIN `HELLO` has yielded username and password strings,
and the body emits the ZAP request frames: version `1.0`, request id `1`, domain,
address, identity, mechanism `PLAIN`, username, and password. The preserved
assertion path is `..\..\..\src\plain_mechanism.cpp`.

### `sub_49BAE0 -> BotReplyChat`

`sub_49BAE0` matches the bot reply-chat selector. It validates the chat state,
copies the input message into a `bot_match_t`, scans reply-chat keys, evaluates
name, gender, variable, and string-word tests, chooses a highest-priority ready
message, appends up to eight variables, honors `bot_testrchat`, and constructs
the selected chat message. The source owner is `src/code/botlib/be_ai_chat.c:2614`.

### `sub_519020 -> _vp_psy_init`

`sub_519020` is libvorbis psychoacoustic look initialization. It clears the
`vorbis_look_psy`, computes eighth-octave shifts and first/total octave lines,
allocates ATH, octave, bark, tone-curve, and noise-offset arrays, applies the
AoTuV rate weighting branch, and matches `_vp_psy_init` in
`src/libs/_deps/libvorbis/lib/psy.c:266`.

### `sub_4C1AA0 -> CM_AddFacetBevels`

`sub_4C1AA0` is collision patch facet bevel generation. The decompile builds
base windings, tests axial and edge bevel planes, emits the preserved
`ERROR: too many bevels`, `WARNING: bevel plane already used`, and
`WARNING: CM_AddFacetBevels... invalid bevel` diagnostics, then appends valid
bevels to the facet. The source owner is `src/code/qcommon/cm_patch.c:807`.

### `sub_4814A0 -> jpeg_idct_float`

`sub_4814A0` is the IJG JPEG floating-point inverse DCT. The function reads the
range-limit table, dequantizes coefficients with the component DCT table,
short-circuits all-zero AC columns, performs the two-pass float IDCT, and writes
the eight output rows through `range_limit`, matching `src/code/jpeg-6/jidctflt.c`.

### `sub_41F3C0 -> zmq_mtrie_t_rm_helper`

`sub_41F3C0` is the recursive ZeroMQ multi-trie removal helper. The function
removes a pipe from node pipe sets, invokes the removal callback with the
current subscription buffer when a subscription disappears, recurses through
single-child and ranged child tables, frees empty child nodes, compacts the
child span, and carries assertion strings from `..\..\..\src\mtrie.cpp`.

### `sub_500CC8 -> inflate_fast`

`sub_500CC8` is the modern zlib `inflate_fast` path. It copies stream and
inflate-state locals, decodes literal/length and distance codes through the
lcode/dcode tables, handles window wrap copies, writes `invalid distance too
far back`, `invalid distance code`, and `invalid literal/length code`, then
updates `next_in`, `next_out`, `avail_in`, `avail_out`, `hold`, and `bits`.
The source owner is `src/libs/_deps/zlib/inffast.c:50`.

### `sub_4E8390 -> inflate_codes`

`sub_4E8390` belongs to the older zlib/minizip inflate implementation retained
for pak/zip support. It is the `inflate_codes` state machine with `START`,
`LEN`, `LENEXT`, `DIST`, `DISTEXT`, `COPY`, `LIT`, `WASH`, `END`, and
`BADCODE` states, calling the older `inflate_fast` helper when enough input and
window space are available. Matching source owners are `src/libs/pak/unzip.cpp`
and `src/code/qcommon/unzip.c`.

## New High-Confidence Aliases Added This Round

- `sub_5099C0 -> png_build_gamma_table`
- `sub_5076D0 -> png_do_rgb_to_gray`
- `sub_491050 -> AAS_Reachability_WalkOffLedge`
- `sub_475ED0 -> forward_DCT_float`
- `sub_427940 -> zmq_plain_mechanism_t_send_zap_request`
- `sub_49BAE0 -> BotReplyChat`
- `sub_519020 -> _vp_psy_init`
- `sub_4C1AA0 -> CM_AddFacetBevels`
- `sub_4814A0 -> jpeg_idct_float`
- `sub_41F3C0 -> zmq_mtrie_t_rm_helper`
- `sub_500CC8 -> inflate_fast`
- `sub_4E8390 -> inflate_codes`

## Verification

I validated the alias artifact directly:

- `references/analysis/quakelive_symbol_aliases.json` parses cleanly through
  `ConvertFrom-Json`
- recount after this pass: `1190` raw alias entries, `1184` address-keyed
  aliases; six support aliases are non-`sub_...` jump/helper names
  alias entries
- top remaining unaliased function by size: `sub_49EDA0` at `1562` bytes

## Completion Stats After Round 119

- Ghidra baseline: `5473` functions, `351` imports, `2` exports, `4377`
  analysis symbols
- Current mapping coverage: `1190` raw alias entries, `1184` address-keyed
  aliases
- Address-keyed coverage: `21.633%` of `5473` functions
- Alias delta this round: `12`
- Estimated writable-source parity for this mapping-only round: unchanged

This pass deliberately did not open source debt. It classifies the top queue as
three retained engine/source-owned functions, two ZeroMQ platform-service
helpers, and seven bundled support-library functions, leaving the next host
queue headed by `sub_49EDA0`, `sub_4C72A0`, and `sub_4DE050`.
