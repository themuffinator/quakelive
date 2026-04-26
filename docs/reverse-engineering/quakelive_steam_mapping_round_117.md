# Quake Live Steam Host Mapping Round 117

## Scope

This round continues directly from
[Round 116](./quakelive_steam_mapping_round_116.md) and takes the refreshed
largest-unaliased `quakelive_steam.exe` queue beginning with `sub_470200`,
`sub_48D870`, and `sub_51DCA0`. Each candidate was classified before opening
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
- matching owners under `src/code/win32/`, `src/code/botlib/`, and
  `src/libs/_deps/libvorbis/`

## Largest-Unaliased Classification

| Rank | Raw symbol | Size | Classification | Alias/action | Confidence | Source debt decision |
| ---: | --- | ---: | --- | --- | --- | --- |
| 1 | `sub_470200` | `2317` | `engine-owned` | `QGL_Shutdown` alias added | High | No new debt opened; source owner already exists in `win_qgl.c`. |
| 2 | `sub_48D870` | `2278` | `engine-owned` | `AAS_Reachability_Teleport` alias added | High | No new debt opened; source owner already exists in `be_aas_reach.c`. |
| 3 | `sub_51DCA0` | `2119` | `CRT/STL` | `dradf4` alias added | High | No engine debt; bundled libvorbis small-FFT support. |

Bucket summary:

- `engine-owned`: 2 of 3
- `platform-service-owned`: 0 of 3
- `CRT/STL`: 1 of 3
- `Awesomium`: 0 of 3
- `Steam SDK support`: 0 of 3

## Evidence Notes

### `sub_470200 -> QGL_Shutdown`

`sub_470200` matches the Win32 OpenGL thunk shutdown path. The HLIL starts
with the preserved diagnostics `...shutting down QGL` and
`...unloading OpenGL DLL`, frees `glw_state.hinstOpenGL` with `FreeLibrary`
when present, clears the module handle, then zeroes the large QGL function
pointer table.

The local source owner is `src/code/win32/win_qgl.c:2808`, where
`QGL_Shutdown` performs the same unload and pointer-null sequence. The nearby
mapped neighbors also match the QGL lane: `sub_470B40 -> QGL_EnableLogging`
and `sub_4728D0 -> QGL_Init`. This is retained engine renderer/platform
behavior, not service or third-party runtime code.

### `sub_48D870 -> AAS_Reachability_Teleport`

`sub_48D870` matches botlib teleporter reachability generation. The function
enumerates BSP entities, accepts `trigger_multiple` and `trigger_teleport`,
uses the preserved model and missing-target diagnostics, resolves
`target_teleporter` and destination `targetname` chains, traces/predicts from
the destination when needed, links the trigger brush into AAS areas, and emits
`TRAVEL_TELEPORT` reachabilities with team filters and the configured
teleport travel time.

The local source owner is `src/code/botlib/be_aas_reach.c:2753`. The scheduler
calls this path after jump-pad reachability and before elevator and
func_bobbing reachability, matching the host caller chain around the mapped
botlib reachability cluster.

### `sub_51DCA0 -> dradf4`

`sub_51DCA0` matches libvorbis `dradf4`, the radix-4 forward real FFT kernel
in `smallft.c`. The body computes `t0 = l1 * ido`, handles the four-way
butterfly, then uses the three twiddle arrays and the preserved
`0.70710678118654752f` half-sqrt-two constant for the even-`ido` tail.

The local source owner is `src/libs/_deps/libvorbis/lib/smallft.c:168`. This
is statically linked bundled libvorbis support and is therefore classified as
`CRT/STL` for this mapping lane. It does not open engine source debt.

## New High-Confidence Aliases Added This Round

- `sub_470200 -> QGL_Shutdown`
- `sub_48D870 -> AAS_Reachability_Teleport`
- `sub_51DCA0 -> dradf4`

## Verification

I validated the alias artifact directly:

- `references/analysis/quakelive_symbol_aliases.json` parses cleanly through
  `ConvertFrom-Json`
- recount after this pass: `1168` raw alias entries, `1167` address-backed
  alias entries
- top remaining unaliased function by size: `sub_41D720` at `2096` bytes

## Completion Stats After Round 117

- Ghidra baseline: `5473` functions, `351` imports, `2` exports, `4377`
  analysis symbols
- Current mapping coverage: `1168` raw alias entries, `1167` address-backed
  aliases
- Address-backed coverage: `21.323%` of `5473` functions
- Alias delta this round: `3`
- Estimated writable-source parity for this mapping-only round: unchanged

This pass deliberately did not open source debt. It classifies the former top
three unaliased entries as two retained engine functions with existing source
owners and one bundled libvorbis FFT helper, leaving the next host queue headed
by `sub_41D720`.
