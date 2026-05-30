# Arena File Support Reconstruction - 2026-05-29

## Evidence

- `quakelive_steam.exe` host loader `sub_45ea60` uses a `0x4000` arena text
  buffer, copies `map`, `longname`, and `type` into the host cache, falls back
  from empty `longname` to `map`, and derives gametype support from retail short
  tokens.
- Host loader `sub_45ec80` reads `scripts/arenas.txt`, enumerates
  `scripts/*.arena` with a `0x400` list buffer, and prints `%i arenas parsed`.
  `sub_45ed90` clears the host arena cache before reloading.
- Retail UI loader `sub_10003070` matches the `0x4000` file-size limit, and
  `sub_10003190` builds a 256-row map cache, emits the corrected
  `not enough memory` warning, and seeds `imageName` with
  `levelshots/preview/%s`.
- UI type-bit reconstruction is anchored by the recovered short-token table:
  `ffa`, `duel`/`tourney`, `race`, `tdm`, `ca`, `ctf`, `oneflag`, `overload`,
  `hh`/`har`, `ft`, `dom`, `ad`, and `rr`.

## Source Closure

- `MAX_ARENAS_TEXT` now mirrors the retail `0x4000` single-file arena buffer.
- `uiInfo.mapList` and the client web-host map catalog now keep 256 map rows,
  matching the retail UI cap instead of truncating at 128.
- UI and client web-host arena parsing now use the retail short-token substring
  table and preserve the retail empty-type FFA fallback without inventing FFA
  for unknown nonempty `type` strings.
- Host factory parsing and map-pool validation now use `overload` for Obelisk,
  `hh`/`har` for Harvester, and the same short-token support checks used by the
  arena catalog.
- UI arena previews now point at `levelshots/preview/%s`, aligning the catalog
  loader with the already reconstructed cgame vote-preview path.

## Confidence And Open Questions

Confidence is high for the host, UI, client-web, and map-pool wiring because the
same constants, strings, and token table are visible in the committed HLIL and
Ghidra corpus. Qagame retains its older arena loader behavior in this pass
because the committed qagame references expose the shared parser but do not give
equally strong evidence for retail `.arena` file enumeration ownership there.
