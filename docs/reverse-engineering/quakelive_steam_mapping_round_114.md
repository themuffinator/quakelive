# Quake Live Steam Host Mapping Round 114

## Scope

This round continues directly from
[Round 113](./quakelive_steam_mapping_round_113.md) and takes the refreshed
largest-unaliased `quakelive_steam.exe` queue beginning with `sub_4AA610`,
`sub_48E160`, and `sub_408340`. Each candidate was classified before opening
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
- matching owners under `src/code/botlib/`
- upstream libzmq `src/socket_base.cpp` naming for the statically linked
  ZeroMQ method

## Largest-Unaliased Classification

| Rank | Raw symbol | Size | Classification | Alias/action | Confidence | Source debt decision |
| ---: | --- | ---: | --- | --- | --- | --- |
| 1 | `sub_4AA610` | `2689` | `engine-owned` | `PC_EvaluateTokens` alias added | High | No debt opened; retained botlib preprocessor evaluator exists. |
| 2 | `sub_48E160` | `2655` | `engine-owned` | `AAS_Reachability_Elevator` alias added | High | No debt opened; retained botlib func_plat reachability owner exists. |
| 3 | `sub_408340` | `2632` | `platform-service-owned` | `zmq_socket_base_t_connect` alias added | High | No new debt opened; this is internal libzmq support under the existing ZMQ service lane. |

Bucket summary:

- `engine-owned`: 2 of 3
- `platform-service-owned`: 1 of 3
- `CRT/STL`: 0 of 3
- `Awesomium`: 0 of 3
- `Steam SDK support`: 0 of 3

## Evidence Notes

### `sub_4AA610 -> PC_EvaluateTokens`

`sub_4AA610` matches botlib `PC_EvaluateTokens`. The body parses the token list
used by `#if` and `#elif`, keeps fixed-size value and operator work arrays,
handles `defined(...)`, unary minus, parentheses, integer-only operators, the
ternary `? :` pair, and reports the same diagnostic strings including
`trailing operator in #if/#elif`, `defined without name in #if/#elif`, and
`mising values in #if/#elif`.

The source owner is `src/code/botlib/l_precomp.c:1685`. This is retained
engine-owned botlib preprocessing behavior with an existing source owner.

### `sub_48E160 -> AAS_Reachability_Elevator`

`sub_48E160` matches botlib `AAS_Reachability_Elevator`. The body iterates BSP
entities, filters `classname == "func_plat"`, reads `model`, optional
`origin`, `lip`, `height`, and `speed`, samples areas around the platform's
bottom and top positions, traces crouch presence between top candidates,
allocates reachability links, sets `TRAVEL_ELEVATOR`, applies team travel
flags, and computes travel time from `aassettings.rs_startelevator + height *
100 / speed`.

The source owner is `src/code/botlib/be_aas_reach.c:2947`. The reachability
builder calls it from `src/code/botlib/be_aas_reach.c:4469`, immediately
before the now-named `AAS_Reachability_FuncBobbing` pass. This is retained
engine-owned botlib behavior with an existing source owner.

### `sub_408340 -> zmq_socket_base_t_connect`

`sub_408340` matches upstream libzmq `zmq::socket_base_t::connect`. The
function is a `socket_base_t` method according to the retained
`zmq::socket_base_t` RTTI/vtable anchors in `analysis_symbols.txt`, and its
body carries `..\..\..\src\socket_base.cpp` assertion strings. The HLIL shows
the expected connect flow: parse and check the endpoint URI, special-case
`inproc`, find the peer endpoint, create paired pipes, write identity frames
when configured, send the bind command, otherwise choose an I/O thread and
create a session for `tcp`, `pgm`, or `epgm` style endpoints.

The alias uses an identifier-safe spelling of the upstream C++ method name:
`zmq_socket_base_t_connect`. This is platform-service support for the retained
ZeroMQ runtime, not Quake engine logic and not Steam SDK or Awesomium code.
The writable source already owns the higher-level `idZMQ` service lane and
runtime fallback policy, so this pass does not open new source debt.

## New High-Confidence Aliases Added This Round

- `sub_408340 -> zmq_socket_base_t_connect`
- `sub_48E160 -> AAS_Reachability_Elevator`
- `sub_4AA610 -> PC_EvaluateTokens`

## Verification

I validated the alias artifact directly:

- `references/analysis/quakelive_symbol_aliases.json` parses cleanly through
  `ConvertFrom-Json`
- recount after this pass: `1159` raw alias entries, `1158` address-backed
  alias entries
- top remaining unaliased function by size: `sub_4224E0` at `2491` bytes

## Completion Stats After Round 114

- Ghidra baseline: `5473` functions, `351` imports, `2` exports, `4377`
  analysis symbols
- Current mapping coverage: `1159` raw alias entries, `1158` address-backed
  aliases
- Address-backed coverage: `21.158%` of `5473` functions
- Alias delta this round: `3`
- Estimated writable-source parity for this mapping-only round: unchanged

This pass deliberately did not open source debt. It classifies the former top
three unaliased entries as two retained engine-owned botlib functions and one
platform-service ZeroMQ support method, leaving the next host queue headed by
`sub_4224E0`.
