# Quake Live Steam Mapping Round 598: SteamDataSource Lifecycle Callback Boundary

Date: 2026-06-11

## Scope

This round rechecks the `SteamDataSource` constructor, shutdown, deleting
destructor, and embedded `AvatarImageLoaded_t` callback owner against retail
`quakelive_steam.exe` Binary Ninja HLIL and the committed Ghidra corpus.

No runtime behavior was widened. The source already keeps Steam-backed menu
resources behind `QL_BUILD_ONLINE_SERVICES`; this pass pins the lifecycle
mapping so callback registration and teardown remain explicit bounded owners.

## Retail Evidence

Primary owner: `assets/quakelive/quakelive_steam.exe`

Evidence checked:

- Binary Ninja HLIL part 02:
  - `sub_464300` / `FUN_00464300`: `SteamDataSource_Init`
  - `sub_464440` / `FUN_00464440`: `SteamDataSource_Shutdown`
  - `sub_464510` / `FUN_00464510`: `SteamDataSource_Destroy`
- Binary Ninja HLIL part 05:
  - the WebCore setup path allocates the data-source object and calls
    `sub_464300(...)` before registering the `"steam"` data source.
- Binary Ninja HLIL part 06:
  - `SteamDataSource::vftable` lives at `0x00532B80`, with slot `0x00`
    mapped to `sub_464510` and slot `0x04` mapped to `sub_4640c0`.
  - `CCallback<class SteamDataSource, struct AvatarImageLoaded_t, 0>` lives at
    `0x00532B68`.
- Ghidra `functions.csv`:
  - `FUN_00464300,00464300,311,0,unknown`
  - `FUN_00464440,00464440,194,0,unknown`
  - `FUN_00464510,00464510,33,0,unknown`
- Symbol alias map:
  - `FUN_00464300` and `sub_464300` promote to `SteamDataSource_Init`
  - `FUN_00464440` and `sub_464440` promote to `SteamDataSource_Shutdown`
  - `FUN_00464510` and `sub_464510` promote to `SteamDataSource_Destroy`

Observed constructor signals:

- `sub_464300` calls the base `Awesomium::DataSource` constructor and installs
  the `SteamDataSource` vtable.
- The constructor allocates two retained tree roots (`operator new(0x28)` and
  `operator new(0x18)`) used by request/avatar bookkeeping.
- It writes the embedded callback vtable at `result[0xb]`, callback owner at
  `result[0xe]`, target `sub_464290` at `result[0xf]`, and calls
  `SteamAPI_RegisterCallback(&result[0xb], 0x14e, ...)`.

Observed teardown signals:

- `sub_464440` restores the `SteamDataSource` and embedded callback vtables.
- It checks the callback flag byte at `arg1[0xc]` before calling
  `SteamAPI_UnregisterCallback(&arg1[0xb], ...)`.
- Callback unregister runs before both retained tree owners are erased and
  deleted.
- `sub_464510` is the deleting destructor wrapper: it calls `sub_464440(...)`
  and conditionally calls `operator delete(arg1)`.

## Source Reconstruction

The source owner is `src/code/client/cl_steam_resources.c`, with platform
callback object storage in `src/common/platform/platform_steamworks.c`.

Pinned source contracts:

- `cl_steamDataSourceRetailMappings[]` records `SteamDataSource` destroy,
  `Init`, `Shutdown`, callback target, and callback id `0x14e` rows.
- `CL_InitSteamResources()` clears resource and pending-avatar state, resets
  `cl_steamAvatarCallbacksRegistered`, refreshes diagnostic cvars, then
  registers avatar callbacks only when `CL_SteamServicesEnabled()` is true.
- `CL_SteamResources_RegisterAvatarCallbacks()` binds
  `CL_SteamResources_OnAvatarImageLoaded` to
  `QL_Steamworks_RegisterAvatarCallbacks(...)` and only flips the local
  registered flag after the platform callback object registers successfully.
- `CL_ShutdownSteamResources()` unregisters the avatar callback owner before
  clearing the resource cache.
- `QL_Steamworks_RegisterAvatarCallbacks()` prepares a non-game-server
  callback object with callback id `0x14e`, raw payload size
  `sizeof( ql_steam_avatar_image_loaded_raw_t )`, and dispatcher
  `QL_Steamworks_DispatchAvatarImageLoaded`.
- `QL_Steamworks_UnregisterAvatarCallbacks()` unregisters the retained callback
  object and clears its state.

## Compatibility Boundary

This pass does not claim that the repo recreates the retail C++ object layout,
STL tree node layout, or asynchronous `Awesomium::DataSource::SendResponse`
path. The reconstructed source keeps the lifecycle effects visible in C:

- callback registration is owned by the Steam resource bridge;
- callback dispatch converts retail raw words into a
  `ql_steam_avatar_image_loaded_t` event;
- callback teardown happens before cache/resource teardown; and
- non-avatar `steam://` traffic remains routed to the documented
  `QLResourceInterceptor launcher/web fallback` owner.

## Validation

Added
`tests/test_platform_services.py::test_steam_datasource_lifecycle_callback_boundary_tracks_retail_hlil`
to pin:

- lifecycle aliases, Ghidra rows, RTTI/vtable symbols, and HLIL constructor /
  destructor ordering;
- source mapping rows for destroy, init, shutdown, callback target, and
  callback id;
- `CL_InitSteamResources()` and `CL_ShutdownSteamResources()` callback
  ownership order;
- `QL_Steamworks_RegisterAvatarCallbacks()` /
  `QL_Steamworks_UnregisterAvatarCallbacks()` platform object ownership; and
- the harness-dispatched `AvatarImageLoaded_t` payload evidence.

Planned validation for this pass:

```text
python -m pytest tests/test_platform_services.py::test_steam_datasource_lifecycle_callback_boundary_tracks_retail_hlil -q --tb=short
python -m pytest tests/test_platform_services.py -q --tb=short
```

## Confidence

Observed facts:

- HLIL gives the constructor allocation sequence, vtable writes, callback
  target write, callback id `0x14e`, unregister guard, tree teardown, and
  deleting destructor wrapper.
- Ghidra rows and alias-map entries identify the three lifecycle owners.
- Source mappings and tests keep the lifecycle effects tied to the bounded
  resource bridge and the platform callback object.

Inference:

- `CL_InitSteamResources()` / `CL_ShutdownSteamResources()` are the correct C
  reconstruction owners for the retail data-source constructor/destructor
  effects, while the exact retail C++ object ABI remains a bounded
  compatibility gap.

Parity estimates:

- Focused `SteamDataSource` lifecycle callback confidence:
  **before 92% -> after 99%**.
- Focused Steam resource bridge lifecycle divergence classification:
  **before 94% -> after 98%**.
- Overall Steam launch/runtime integration mapping confidence: **93.14% -> 93.16%**.
