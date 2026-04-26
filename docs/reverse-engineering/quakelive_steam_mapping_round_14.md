# Quake Live Steam Host Mapping Round 14

## Scope

This round revisits the native UI import slab rooted at `data_567338`.

Round 13 tightened the shared advertisement bridge, but the adjacent Quake Live UI import block still contained a cluster of unnamed wrappers around offsets `0x164..0x180`. A fresh pass across the host slab, `uix86.dll` HLIL callsites, and the local `cl_ui.c` reconstruction now pins that cluster as:

- the parser import seam used by menu/script loading
- the Quake Live-specific text draw/measure helpers
- the UI-owned Steam subscription and workshop download-info wrappers

The primary local evidence for this round is:

- `references/hlil/quakelive/quakelive_steam.exe/quakelive_steam.exe_hlil.txt`
- `references/hlil/quakelive/uix86.all/uix86.dll_hlil.txt`
- `src/code/client/cl_ui.c`

## UI Import Slab Ownership

The owning slab is now explicit enough to document directly.

Observed local facts:

1. The native UI VM is created through `sub_4E9FF0("ui", &data_146CC18, &data_567338, ...)`.
2. The host slab entries at offsets `0x164..0x180` resolve to:
   - `data_56749C = sub_4B0270`
   - `data_5674A0 = sub_4B0290`
   - `data_5674A4 = sub_4B02B0`
   - `data_5674A8 = sub_4B02D0`
   - `data_5674AC = sub_4BF2E0`
   - `data_5674B0 = sub_4B03E0`
   - `data_5674B4 = sub_4BF310`
   - `data_5674B8 = sub_4BF2F0`
3. The local reconstruction assigns the same import numbers in `cl_ui.c`:
   - imports `89..92` are `QL_UI_trap_PC_*`
   - imports `93..96` are `QL_UI_trap_Import93..96`

That is enough to treat this region as a coherent native UI host surface rather than a generic tailcall band.

## Parser Imports At `0x164..0x170`

The four parser wrappers are now high-confidence.

Observed local facts:

1. `sub_4B0270`, `sub_4B0290`, `sub_4B02B0`, and `sub_4B02D0` are grouped jump wrappers through `data_13E1844 + 0x204..0x210`.
2. `uix86.dll` uses the matching offsets exactly like the classic parser API:
   - `(*(data_106B40A8 + 0x164))("ui/menus.txt")` opens a source handle
   - `(*(data_106B40A8 + 0x168))(handle)` frees that handle
   - `(*(data_106B40A8 + 0x16C))(handle, &token)` repeatedly reads tokens during menu parsing
   - `(*(data_106B40A8 + 0x170))(handle, &filename, &line)` retrieves source file and line data
3. `cl_ui.c` reconstructs imports `89..92` as:
   - `QL_UI_trap_PC_LoadSource`
   - `QL_UI_trap_PC_FreeSource`
   - `QL_UI_trap_PC_ReadToken`
   - `QL_UI_trap_PC_SourceFileAndLine`

These are UI-owned parser import wrappers, not new parser implementations.

## UI Steam And Text Helpers At `0x174..0x180`

The four Quake Live-specific imports are also stable enough to promote now.

### `sub_4BF2E0`

Observed local facts:

1. `sub_4BF2E0` is a pure tailcall to `sub_460590`.
2. `sub_460590` is already promoted as `SteamApps_BIsSubscribedApp`.
3. `uix86.dll` calls `(*(data_106B40A8 + 0x174))(0x53DCC)` during init.
4. `cl_ui.c` reconstructs import `93` as `QL_UI_trap_Import93`, which returns `QL_Steamworks_IsSubscribedApp(...) ? 1 : 0`.

This is best named by its UI import ownership rather than by the lower Steam wrapper it forwards into.

### `sub_4B03E0`

Observed local facts:

1. `sub_4B03E0` forwards eight parameters into `data_146CCF0`, preserving `(x, y, text, fontHandle, scale, maxX, outMaxX, forceColor)` shape.
2. `uix86.dll` uses offset `0x178` throughout its text paint helpers, including paths that:
   - convert virtual UI coordinates to screen coordinates
   - pass a text pointer and scale
   - supply `maxX`, `outMaxX`, and a color-force flag
3. `cl_ui.c` reconstructs import `94` as a scaled text renderer with the exact same parameter contract.

The stable role here is a host text-draw helper exposed through the Quake Live UI import seam.

### `sub_4BF310`

Observed local facts:

1. `sub_4BF310` forwards into `data_146CCF4`.
2. `uix86.dll` uses offset `0x17C` in text layout helpers and subtracts the packed float results to compute width/height and alignment.
3. `cl_ui.c` reconstructs import `95` as a text measurement helper returning packed float bits.

This is the paired host text-measure helper for the same UI seam.

### `sub_4BF2F0`

Observed local facts:

1. `sub_4BF2F0` is a pure tailcall to `sub_460660`.
2. `sub_460660` is already promoted as `SteamUGC_GetItemDownloadInfo`.
3. `uix86.dll` parses `cl_downloadItem` and calls offset `0x180` with the resulting `(itemIdLow, itemIdHigh, &downloaded, &total)` words.
4. `cl_ui.c` reconstructs import `96` as `QL_UI_trap_GetItemDownloadInfo`, returning workshop download statistics from retained client workshop state before falling back to `QL_Steamworks_GetItemDownloadInfo`, the retained platform wrapper over `SteamUGC_GetItemDownloadInfo` reached from the parsed low/high words.

This is the UI-owned workshop download-info import wrapper.

## Promoted Aliases

| Raw symbol | Alias candidate | Basis | Observed role |
| --- | --- | --- | --- |
| `sub_4B0270` (`0x004B0270`) | `QLUIImport_PC_LoadSource` | Observed | UI import wrapper for opening parser source handles. |
| `sub_4B0290` (`0x004B0290`) | `QLUIImport_PC_FreeSource` | Observed | UI import wrapper for releasing parser source handles. |
| `sub_4B02B0` (`0x004B02B0`) | `QLUIImport_PC_ReadToken` | Observed | UI import wrapper for reading parser tokens. |
| `sub_4B02D0` (`0x004B02D0`) | `QLUIImport_PC_SourceFileAndLine` | Observed | UI import wrapper for retrieving parser source file/line metadata. |
| `sub_4B03E0` (`0x004B03E0`) | `QLUIImport_DrawScaledText` | Observed plus bounded inference | Host text renderer exposed through UI import `94`, supporting scale, max width, and forced-color handling. |
| `sub_4BF2E0` (`0x004BF2E0`) | `QLUIImport_IsSubscribedApp` | Observed | UI import wrapper over `SteamApps_BIsSubscribedApp`. |
| `sub_4BF310` (`0x004BF310`) | `QLUIImport_MeasureText` | Observed plus bounded inference | Host text measurement helper exposed through UI import `95`, returning packed width/height floats. |
| `sub_4BF2F0` (`0x004BF2F0`) | `QLUIImport_GetItemDownloadInfo` | Observed | UI import wrapper over `SteamUGC_GetItemDownloadInfo`, reached from the parsed `cl_downloadItem` low/high words and mirrored in retained `cl_ui.c` as a retained-state-first bridge that falls back to `QL_Steamworks_GetItemDownloadInfo`. |

## Open Questions

1. UI imports `82` and `83` remain bounded but not worth promotion yet: `cl_ui.c` still treats them as an optional overlay hook and a retail stub.
2. `sub_4B0340`, `sub_4BEF20`, `sub_4E1740`, and `sub_4B0420` sit in the same broader slab neighborhood, but their exact UI-facing semantics are still not pinned tightly enough to name.
3. The lower targets behind `data_146CCF0` and `data_146CCF4` are now functionally constrained as text draw/measure backends, but this round only promotes the stable UI wrapper names.
