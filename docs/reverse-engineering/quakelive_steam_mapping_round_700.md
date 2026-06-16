# Quake Live Steam Mapping Round 700: Steam Avatar Image Slot Constants

Date: 2026-06-16

## Scope

This pass rechecked the retained Steam avatar image wrapper surface used by
`SteamClient_GetAvatarImageHandle`, the SteamDataSource avatar request path,
and the reconstructed `QL_Steamworks_RequestAvatarImage` /
`QL_Steamworks_LoadAvatarRGBA` helpers. The reconstruction goal was to replace
the remaining raw production vtable indices with named ABI slot constants while
preserving the mock vtable layout as the ABI control sample.

Focused parity estimate: **before 90% -> after 99%** for focused Steam avatar
image ABI source-shape confidence. Overall Steam launch/runtime integration mapping confidence moves from **93.82% -> 93.84%**. Repo-wide parity remains
**99%** because this pass names retained Steamworks wrapper boundaries without
changing the strict-retail Windows replacement score and does not enable live Steam behavior by default.

## Evidence

| Retail symbol | Current alias | Confidence | Notes |
| --- | --- | --- | --- |
| `FUN_00460f30` / `sub_460f30` | `SteamClient_GetAvatarImageHandle` | High | Public avatar helper; builds the `steam_%llu` cache key, requests the large friend avatar through `SteamFriends + 0x90`, then decodes the image through `SteamUtils + 0x14` and `SteamUtils + 0x18`. |
| `FUN_004640c0` / `sub_4640c0` | `SteamDataSource_OnRequest` | High | SteamDataSource avatar URL owner; requests the large avatar through `SteamFriends + 0x90`, treats `0xffffffff` as pending, and starts the response thread once the handle is ready. |
| `FUN_00463550` / `sub_463550` | `SteamDataSource_StartResponseThread` | Medium | Response-thread boundary reached with the ready avatar image handle. |

Observed Binary Ninja HLIL anchors:

- `00460f8a` calls `SteamFriends + 0x90` in
  `SteamClient_GetAvatarImageHandle`.
- `00460fa8` calls `SteamUtils + 0x14` for avatar image width and height.
- `00460fd4` calls `SteamUtils + 0x18` for avatar RGBA payload copy.
- `00463472` and `004634b4` repeat the `SteamUtils + 0x14` / `+0x18`
  decode sequence in the response-thread image emission path.
- `004641de` and `004641eb` call `SteamFriends + 0x90` from the
  SteamDataSource avatar URL owner.

Observed Ghidra companion facts:

- `imports.txt` imports `SteamFriends` and `SteamUtils`.
- `functions.csv` contains `FUN_00460f30,00460f30,278,0,unknown`.
- `references/analysis/quakelive_symbol_aliases.json` maps `FUN_00460f30`
  and `sub_460f30` to `SteamClient_GetAvatarImageHandle`.
- `analysis_symbols.txt` contains the SteamDataSource and
  `CCallback<class_SteamDataSource,struct_AvatarImageLoaded_t,0>` vtables.
- `tests/steamworks_harness.c` mirrors the mock `SteamFriends` avatar and
  `SteamUtils` image vtable assignments; Round 708 later promoted that mirror
  from raw offsets to named harness-local constants.

Inference: the retail avatar image path is anchored to the large-avatar slot
for both the public helper and SteamDataSource. The reconstructed wrapper also
keeps the adjacent small and medium ABI slots because the harness and existing
size-selection tests exercise them, but the retail observed large-avatar path
remains the confidence anchor.

## Source Reconstruction

The production wrapper layer now names these slots:

- `QL_STEAM_FRIENDS_GET_SMALL_FRIEND_AVATAR_SLOT`
- `QL_STEAM_FRIENDS_GET_MEDIUM_FRIEND_AVATAR_SLOT`
- `QL_STEAM_FRIENDS_GET_LARGE_FRIEND_AVATAR_SLOT`
- `QL_STEAM_UTILS_GET_IMAGE_SIZE_SLOT`
- `QL_STEAM_UTILS_GET_IMAGE_RGBA_SLOT`

The mapped wrapper surface is:

- `QL_Steamworks_GetAvatarMethodIndex`
- `QL_Steamworks_RequestAvatarImage`
- `QL_Steamworks_LoadAvatarRGBA`

The harness intentionally keeps a named mirror of the mock `SteamFriends` and
`SteamUtils` vtables, which keeps the test fixture as the ABI layout control
sample. SteamDataSource callback registration, pending-avatar retry behavior,
and non-avatar Steam URI fallback ownership are unchanged from Round 621.

## Validation

Completed for this pass:

- `python -m pytest -q tests/test_platform_services.py -k "steam_avatar_image_slot_constants_round_700 or steam_resource_bridge_reconstructs_avatar_url_fetches or steam_datasource_avatar_response_lifecycle_tracks_round_621" --tb=short` - 3 passed, 236 deselected.
- `python -m pytest -q tests/test_steamworks_harness.py --tb=short` - 132 passed.
- `python -m pytest -q tests/test_platform_services.py --tb=short` - 238 passed, 1 failed because the pre-existing ZMQ Round 698 gate references missing `docs/reverse-engineering/quakelive_steam_mapping_round_698.md`.
- `git diff --check` - passed with existing LF-to-CRLF working-copy warnings only.
