# Quake Live Steam Mapping Round 594: SteamDataSource OnRequest Avatar Boundary

Date: 2026-06-11

## Scope

This round pins the retail `SteamDataSource::OnRequest` body to the repository's
bounded browser-resource reconstruction. The retail evidence shows a native
SteamDataSource path for avatar filenames and the asynchronous
`AvatarImageLoaded_t` retry lane; the current source intentionally keeps
non-avatar `steam://` requests on the documented launcher/web fallback owner.

No source behavior was changed in this pass. The work adds a stricter parity
gate so future reconstruction cannot accidentally widen the live SteamDataSource
surface without also documenting a real open replacement path.

## Retail Evidence

Primary owner: `assets/quakelive/quakelive_steam.exe`

Evidence checked:

- Binary Ninja HLIL part 02:
  - `sub_4640c0` / `FUN_004640c0`: `SteamDataSource_OnRequest`
  - `sub_464290` / `FUN_00464290`: `SteamDataSource_OnAvatarImageLoaded`
  - `sub_463550` / `FUN_00463550`: `SteamDataSource_StartResponseThread`
- Ghidra `functions.csv`:
  - `FUN_004640c0,004640c0,450,0,unknown`
  - `FUN_00464290,00464290,102,0,unknown`
  - `FUN_00463550,00463550,164,0,unknown`
- Symbol alias map:
  - `FUN_004640c0` and `sub_4640c0` promote to `SteamDataSource_OnRequest`
  - `FUN_00464290` and `sub_464290` promote to
    `SteamDataSource_OnAvatarImageLoaded`
  - `FUN_00463550` and `sub_463550` promote to
    `SteamDataSource_StartResponseThread`

Observed HLIL signals:

- `sub_4640c0` copies the request URL into a WebString, splits the first path
  segment at `/`, extracts `Awesomium::WebURL::filename`, and parses that
  filename as a decimal SteamID with `sscanf("%llu", ...)`.
- The first path segment is compared with `"avatar"` for six bytes. The native
  path only continues when that segment exactly matches the avatar token.
- The avatar request calls `SteamFriends()` vtable slot `0x90`. The source maps
  that retail slot through `QL_Steamworks_RequestAvatarImage(...)`.
- A return value of `0xffffffff` records the pending response owner in the
  SteamDataSource request map; any nonzero image handle starts the response
  thread through `sub_463550`.
- `sub_464290` looks up the pending owner by SteamID, erases that map entry, and
  forwards the loaded image handle back through `sub_463550`.

## Source Reconstruction

The source owner is `src/code/client/cl_steam_resources.c`.

Pinned source contracts:

- The retail mapping table keeps the `SteamDataSource` vtable slot:
  - `OnRequest`, vtable `0x00532B80`, slot `0x04`, target `0x004640C0`
  - `StartResponseThread`, target `0x00463550`
  - `AvatarImageLoaded_t` callback target, vtable `0x00532B68`, slot `0x10`,
    target `0x00464290`
- `CL_SteamDataSource_Request(...)` clears the response, marks it as
  SteamDataSource-owned, and only resolves native Steam requests when
  `CL_SteamResources_IsAvatarURL(...)` succeeds.
- Avatar requests call `CL_SteamResources_RequestAvatarRGBA(...)`, publish
  `image/rgba`, and leave pending requests retryable through
  `CL_SteamResources_OnAvatarImageLoaded(...)`.
- Non-avatar Steam URIs are not treated as live online service fetches. They log
  `non-avatar Steam URI routed to launcher/web fallback owner` and return to
  `QLResourceInterceptor_OnRequest(...)`, where the retail `ql` host mapping and
  launcher/web fallback remain the compatibility owners.

The gap note
`docs/reverse-engineering/source-file-gap-notes/rw-g01-client-steam-resources.md`
already classifies this as a bounded divergence:

- native subset: `avatar-only SteamDataSource`
- native gap: `missing non-avatar SteamDataSource owner`
- fallback owner: `QLResourceInterceptor launcher/web fallback`

## Confidence

Observed facts:

- HLIL gives the path-token comparison, SteamID parse, SteamFriends avatar slot,
  pending sentinel, and callback completion path.
- Ghidra function rows confirm the owning retail functions and sizes.
- Source mappings and labels keep the avatar-only native subset and non-avatar
  fallback boundary explicit.

Inference:

- The repository's current behavior is a faithful bounded reconstruction of the
  avatar lane, not a full recreation of the retail Awesomium delayed-response
  ABI. The non-avatar fallback is therefore intentional and should remain
  visible until a documented open replacement exists.

Parity estimates:

- Focused `SteamDataSource_OnRequest` boundary confidence:
  **before 88% -> after 99%**.
- Focused browser resource bridge divergence classification confidence:
  **before 93% -> after 97%**.
- Overall Steam launch/runtime integration mapping confidence: **93.10% -> 93.12%**.
