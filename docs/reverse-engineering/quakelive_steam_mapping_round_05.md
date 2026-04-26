# Quake Live Steam Host Mapping Round 05

## Scope

This round resolves three wrapper-layer questions that were still open after Round 04:

1. the SteamApps subscription probe behind the Quake Live UI import surface
2. the SteamUGC download-progress probe used by workshop UI flows
3. the Steam game-server key/value publication helper that fans server info into the Steam backend

The evidence chain stayed the same as in earlier rounds:

- `references/reverse-engineering/ghidra/quakelive_steam/metadata.txt`
- `references/reverse-engineering/ghidra/quakelive_steam/functions.csv`
- `references/reverse-engineering/ghidra/quakelive_steam/analysis_symbols.txt`
- `references/hlil/quakelive/quakelive_steam.exe/`

For these wrappers, I also used the current reconstruction as a secondary cross-check once the retail HLIL already bounded the behavior:

- `src/common/platform/platform_steamworks.c`
- `src/code/client/cl_ui.c`

## SteamApps And SteamUGC Wrapper Resolution

Two small helpers that were previously left unnamed now have enough support to promote.

| Raw symbol | Alias candidate | Basis | Observed role |
| --- | --- | --- | --- |
| `sub_460590` (`0x00460590`) | `SteamApps_BIsSubscribedApp` | Observed | Returns `0` until the client Steam API is initialized, then calls `SteamApps()->vtable[0x1c]` with the supplied app ID. The same `0x1c` slot is reconstructed in `platform_steamworks.c` as `QL_Steamworks_IsSubscribedApp`, and `cl_ui.c` wires the equivalent behavior into UI import `93`. |
| `sub_460660` (`0x00460660`) | `SteamUGC_GetItemDownloadInfo` | Observed | Direct wrapper around `SteamUGC()->vtable[0xd8]` with `(idLow, idHigh, outDownloaded, outTotal)`. The same `0xd8` slot is reconstructed in `platform_steamworks.c` as `QL_Steamworks_GetItemDownloadInfo`, and `cl_ui.c` uses that path for UI import `96` by consulting retained client workshop state first and then falling back to `QL_Steamworks_GetItemDownloadInfo`, the retained wrapper over the same low/high-word `SteamUGC_GetItemDownloadInfo` slot. |

### Import-table anchors

The host also exposes thin tailcall stubs for these two helpers:

- `sub_4BF2E0` tailcalls `sub_460590` and appears in import tables at `data_565B40` and `data_5674AC`
- `sub_4BF2F0` tailcalls `sub_460660` and appears in the later import table at `data_5674B8`

I did not add separate aliases for those tailcall wrappers in this round. Their behavior is fully inherited from the underlying Steam API shims, while the owning import-table names are still better treated at the table level rather than by assigning a duplicate semantic name to each tailcall export.

## Steam Server Key/Value Publication

The previously bounded helper at `sub_465A60` is now strong enough to promote with a wrapper-level name.

| Raw symbol | Alias candidate | Basis | Observed role |
| --- | --- | --- | --- |
| `sub_465A60` (`0x00465A60`) | `SteamServer_SetKeyValuesFromInfoString` | Observed | Walks an info string, splits it into `key` / `value` pairs with `sub_4D9380`, and calls the Steam game-server slot at `+0x50` once per pair. Startup and dirty-serverinfo refresh paths both feed it the `data_1206288` buffer built by `sub_4CDBE0(4)`. |

### Supporting flow

The relevant surrounding helpers now line up cleanly:

1. `sub_4CDBE0(flagMask)` zeroes `data_1206288` and appends server cvars from `data_1437900` through `sub_4D9620` when their flag mask matches.
2. `sub_4D9380` parses one `\\key\\value` pair at a time from that info string into temporary key/value buffers.
3. `sub_465A60` loops until the info string is exhausted, forwarding each parsed pair into the Steam game-server interface.

That flow explains both confirmed call sites:

- `sub_466800` runs `sub_465B00(); sub_466260(1); sub_4CDBE0(4); sub_465A60(..., &data_1206288)` immediately after `Connected to Steam servers`
- the server dirty-bit path at `004E4B36` rebuilds `data_1206288`, reruns `sub_465A60`, and then publishes configstring `0` with the same refreshed info block

This is the right level to name as a wrapper: the function is not just one raw Steam call, it is the host-side adapter that translates Quake-style info strings into repeated Steam game-server key/value updates.

## New High-Confidence Aliases Added This Round

- `sub_460590`
- `sub_460660`
- `sub_465A60`

## Open Questions

1. `sub_4BF2E0` and `sub_4BF2F0` are now clearly import-table tailcall exports, but I am still leaving the table-owned surface unnamed and only promoting the underlying Steam wrappers.
2. `sub_4E2620` and `sub_4E2640` remain deliberately unnamed after re-checking `sub_4F4E10` and `sub_4F4E40`; the extra front-end work there is generic container maintenance around `data_5756FC`, not a clean stats-specific contract.
