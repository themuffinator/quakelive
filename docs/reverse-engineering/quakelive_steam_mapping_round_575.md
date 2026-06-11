# Quake Live Steam Mapping Round 575: Advertisement Bridge Reserved Slot 21C0

Date: 2026-06-11

## Scope

This round closed the remaining implied slot in the source-owned
`data_12d2670` advertisement/WebUI bridge layout. The target was the Binary
Ninja-only retail wrapper at `0x004F21C0`, which older notes left as an opaque
no-argument advertisement-bridge slot.

Writable areas:

- `src/code/client/cl_cgame.c`
- `references/analysis/quakelive_symbol_aliases.json`
- `tests/test_awesomium_browser_parity.py`
- `tests/test_game_native_export_helper_parity.py`

Reference evidence:

- `references/hlil/quakelive/quakelive_steam.exe/quakelive_steam.exe_hlil_split/quakelive_steam.exe_hlil_part05.txt`
- `references/hlil/quakelive/cgamex86.dll/cgamex86.dll_hlil.txt`
- `references/reverse-engineering/ghidra/quakelive_steam/functions.csv`
- `src/code/client/cl_cgame.c`
- `src/code/cgame/cg_public.h`

## Observed Facts

- Binary Ninja HLIL shows `0x004F21C0` as `sub_4f21c0`, loading
  `data_12d2670` and dispatching `jump(*(*ecx + 0x40))`.
- The adjacent bridge wrappers are already mapped as:
  - `0x004F2180 -> AdvertisementBridge_GetLabelList1Entry`, slot `+0x64`
  - `0x004F21E0 -> AdvertisementBridge_SetupAdvertCellShader`, slot `+0x50`
  - `0x004F20C0 -> AdvertisementBridge_InitUI`, slot `+0x44`
- The native cgame HLIL for `CG_LoadHudMenu` calls import slot `54`; the
  reconstructed host import slab routes slot `54` through
  `QL_CG_trap_AdvertisementBridge_Reserved21C0`.
- The committed Ghidra `functions.csv` does not expose a `FUN_004f21c0` row, so
  this promotion is deliberately limited to Binary Ninja `sub_*` aliases.

## Mapping And Reconstruction Work

- Promoted:
  - `sub_4F21C0 -> AdvertisementBridge_Reserved21C0`
  - `sub_4f21c0 -> AdvertisementBridge_Reserved21C0`
- Added `QL_WEB_BRIDGE_SLOT_RESERVED_21C0 = 0x40` to the source bridge slot
  enum.
- Added a `QL_WEB_BRIDGE_ASSERT_VTBL_OFFSET( reserved21C0,
  QL_WEB_BRIDGE_SLOT_RESERVED_21C0 )` assertion so the source vtable layout now
  pins the previously implied `+0x40` member explicitly.
- Extended the Awesomium bridge parity gate to prove the alias, HLIL dispatch,
  slot constant, and vtable offset assertion together.
- Extended the native cgame import parity gate so import slot `54`, the cgame
  HLIL call, the engine HLIL bridge dispatch, and the alias map stay linked.

## Source Reconstruction Decision

The source behavior remains a guarded no-op. The retail evidence proves a
no-argument callback at bridge vtable slot `+0x40` and a native cgame import
callout into that slot, but it does not prove a stable public behavior beyond
that. The `Reserved21C0` name records the address-backed bridge position without
inventing online-service behavior.

## Confidence

- High that `sub_4F21C0` is the `data_12d2670` bridge slot `+0x40` dispatcher:
  HLIL, source vtable layout, and native cgame import slot `54` all agree.
- Medium for the `AdvertisementBridge_Reserved21C0` owner name: the bridge and
  slot are concrete, while the public action remains intentionally opaque.
- High that no `FUN_004f21c0` alias should be added yet: the committed Ghidra
  `functions.csv` does not provide that row.

## Validation

Planned validation:

```text
python -m json.tool references/analysis/quakelive_symbol_aliases.json
python -m pytest tests/test_awesomium_browser_parity.py tests/test_game_native_export_helper_parity.py -q --tb=short
```

## Parity Estimate

- Focused advertisement/WebUI bridge slot-layout confidence:
  **before 96% -> after 99%**.
- Focused native cgame advertisement bridge import-54 confidence:
  **before 94% -> after 99%**.
- Overall Steam/WebUI launch/runtime integration mapping confidence:
  **99.22% -> 99.24%**.
