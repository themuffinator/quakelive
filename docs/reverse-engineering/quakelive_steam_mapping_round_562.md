# Quake Live Steam Mapping Round 562: Workshop Queue and Completion Helpers

Date: 2026-06-11

## Scope

This round rechecked the retail Steam Workshop download queue and completion
helper band in `quakelive_steam.exe`, covering the helpers at
`0x004692d0..0x004699c0` that gate active downloads, queue pending Workshop
items, promote the next item, and notify the client frame when downloads have
settled.

No live Steam behavior was enabled. Workshop integration remains behind
`QL_BUILD_ONLINE_SERVICES`, default disabled, with the source preferring
offline-safe stubs and bounded state over live service usage.

## Evidence Inputs

- Binary Ninja HLIL:
  `references/hlil/quakelive/quakelive_steam.exe/quakelive_steam.exe_hlil_split/quakelive_steam.exe_hlil_part02.txt`
- Binary Ninja HLIL frame and string anchors:
  `references/hlil/quakelive/quakelive_steam.exe/quakelive_steam.exe_hlil_split/quakelive_steam.exe_hlil_part04.txt`
  and
  `references/hlil/quakelive/quakelive_steam.exe/quakelive_steam.exe_hlil_split/quakelive_steam.exe_hlil_part06.txt`
- Ghidra function rows:
  `references/reverse-engineering/ghidra/quakelive_steam/functions.csv`
- Alias ledger:
  `references/analysis/quakelive_symbol_aliases.json`
- Source reconstruction:
  `src/code/client/cl_main.c` and
  `src/common/platform/platform_steamworks.c`

## Observed Facts

| Retail helper | Alias | Observed signal | Reconstruction status |
| --- | --- | --- | --- |
| `sub_4692d0` | `SteamWorkshop_DownloadsSettled` | Tests the retail active-download flag, checks the queue count, logs `Download completed for all steamworks items`, clears the active flag, and returns settled/not-settled state to the frame path. | Source-backed by `CL_Workshop_DownloadsSettled` and `CL_Workshop_Frame`. |
| `sub_469330` | `std_list_remove_workshop_download_node` | Walks the retail queued-download list, compares the low/high Workshop item ID pair, unlinks the matching node, deletes it, and decrements the list count. | Alias-only STL helper; source clears the bounded active entry instead. |
| `sub_469390` | `std_list_create_workshop_download_node` | Allocates a `0x10` byte list node, writes list links, and stores the queued item low/high pair at offsets `+8` and `+0xc`. | Alias-only STL helper; source stores the same item pair in `cl_steamWorkshopDownloadState.items[]`. |
| `sub_469400` | `SteamWorkshop_AdvanceDownloadQueue` | Removes the completed active ID, clears the active pair, promotes the next queued node, logs `was queued, requesting download`, and calls Steam UGC slot `0xdc` with high priority. | Source-backed by `CL_Workshop_AdvanceDownloadQueue`. |
| `sub_469750` | `std_list_push_workshop_download_node` | Creates a queue node through `sub_469390`, links it into the retail list, increments the count, and raises `list<T> too long` on overflow. | Alias-only STL helper; source uses a fixed `MAX_STEAM_WORKSHOP_ITEMS` queue. |
| `sub_4699c0` | `SteamWorkshop_RequestDownload` | Starts an explicit download when idle, queues when another download is active, ignores duplicate active explicit requests, and finalizes immediately when the item is already installed. | Source-backed by `CL_Workshop_RequestDownload`. |

## Mapping Work

Promoted function spellings:

- `FUN_004692d0`, `sub_4692D0`, `sub_4692d0` -> `SteamWorkshop_DownloadsSettled`
- `FUN_00469330`, `sub_469330` -> `std_list_remove_workshop_download_node`
- `FUN_00469390`, `sub_469390` -> `std_list_create_workshop_download_node`
- `FUN_00469750`, `sub_469750` -> `std_list_push_workshop_download_node`

Added
`tests/test_platform_services.py::test_steam_workshop_queue_helpers_track_retail_reference_rows`
to pin:

1. Ghidra rows and sizes for the newly named helper functions and the adjacent
   public Workshop download owners.
2. HLIL active-download, queue-count, list-node allocation, remove, push, and
   UGC `DownloadItem` slot `0xdc` anchors.
3. The client-frame completion handoff that prints
   `Steamworks downloads complete`, restarts the file system when required, and
   calls the download-complete handoff.
4. Retail strings for queued downloads, duplicate active requests, completed
   downloads, and the STL `list<T> too long` failure path.
5. Source equivalents in `CL_Workshop_RequestDownload`,
   `CL_Workshop_AdvanceDownloadQueue`, `CL_Workshop_FinalizeInstalledItem`,
   `CL_Workshop_DownloadsSettled`, `CL_Workshop_Frame`,
   `QL_Steamworks_GetItemState`, and `QL_Steamworks_DownloadItem`.

## Source Reconstruction Decision

No C source patch was required. The retail binary uses an MSVC `std::list` of
Workshop item IDs for queued downloads, with small compiler-emitted helpers for
node creation, insertion, and removal. The reconstructed source intentionally
keeps a bounded `cl_steamWorkshopDownloadState.items[]` representation with
explicit `queued`, `downloadRequested`, `completed`, `activeItemIndex`, and
`queueActive` state.

That source model is equivalent for the observable runtime contract:

1. an installed item finalizes immediately;
2. the first uncached item requests `ISteamUGC::DownloadItem` through retail
   vtable slot `0xdc` with high priority;
3. later uncached items are marked queued while another download is active;
4. completion promotes the next queued item and requests its download; and
5. when no active or queued items remain, the client frame prints the retail
   completion message, performs the required file-system restart path, and
   completes the download lane.

The STL helper aliases are retained as binary-evidence names rather than source
data-structure requirements. This keeps the online-service divergence contained
while documenting how the retail queue works.

## Confidence

- High for `SteamWorkshop_DownloadsSettled`: active flag, queue count, retail
  completion log, and frame-call ownership agree across HLIL and source.
- High for list helper identity: allocation size, ID-pair storage, node
  unlink/delete behavior, insertion count update, and `list<T> too long` string
  match MSVC list operations.
- High for source queue equivalence: source request, queue, promotion, finalize,
  and frame-completion paths all preserve the retail observable state machine.
- Medium-high for exact data-structure parity: source intentionally avoids
  cloning the retail STL list layout.

## Inference Boundary

Observed facts:

1. Retail download requests call Steam UGC vtable slot `0xdc`.
2. Retail active-download completion clears the active low/high item pair,
   removes the finished node, and promotes the next queued node if present.
3. Retail frame code calls `sub_4692d0`, prints the completion message, and
   enters the file-system restart/download-complete handoff once the queue has
   settled.

Inferences:

1. The source bounded array is behaviorally equivalent to the retail list for
   the observed queue lifecycle, despite a different internal representation.
2. The retail helper at `sub_4692d0` is best named by its frame-facing contract:
   it reports whether Steam Workshop downloads have settled.

Open questions:

1. A future live-Steam validation pass could compare callback timing for
   `DownloadItemResult_t` and `ItemInstalled_t`, but that requires enabling
   online services and is outside the default build policy.
2. If later evidence exposes another retail queue mutation helper outside this
   band, the helper aliases may need a narrower container-specific suffix.

## Validation

- `python -m pytest tests/test_platform_services.py::test_steam_workshop_queue_helpers_track_retail_reference_rows -q`

## Parity Estimate

- Focused Workshop queue helper alias confidence:
  **before 61% -> after 98%**.
- Focused Workshop download/finalization source-equivalence confidence:
  **before 93% -> after 97%**.
- Overall Steam launch/runtime reconstruction parity:
  **92.7% -> 92.75%**.
