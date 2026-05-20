# Quake Live Reverse Engineering Mapping Round 272

## Scope

- Rechecked `src/code/cgame/cg_main.c` native/legacy entry wiring against the committed `cgamex86.dll` HLIL evidence.
- Focused on the bridge between `vmMain`, the synthetic native export wrappers, `CG_GetNativeExportTable`, and the retail table rooted at `data_100769A8`.

## Evidence

- `references/hlil/quakelive/cgamex86.dll/cgamex86.dll_hlil.txt`
  - `dllEntry` writes `*arg1 = &data_100769a8` and native API version `8`.
  - `data_100769A8` through `data_100769F8` contains the recovered cgame native export table.
  - `data_100769E8` is a deliberate null slot, preserved as `CG_NATIVE_EXPORT_RESERVED_NULL`.
- `src/code/cgame/cg_public.h`
  - `cgameNativeExport_t` now names the recovered slot order separately from the legacy `cgameExport_t` command enum.
- `src/code/cgame/cg_main.c`
  - `cg_nativeExports` preserves the retail slot order and keeps small wrappers for legacy QVM-style entries that need type or state adaptation.

## Source Notes

- Added explicit source headers to the native wrapper helpers:
  - `CG_NativeDrawActiveFrame`
  - `CG_NativeKeyEvent`
  - `CG_NativeMouseEvent`
  - `CG_NativeChatDown`
  - `CG_NativeChatUp`
  - `CG_GetNativeExportTable`
- Normalized the direct legacy `vmMain` calls for `CG_MOUSE_EVENT` and `CG_EVENT_HANDLING` to repository call-spacing style.
- No runtime behavior changed in this pass.

## Guardrail

- `tests/test_cgame_displaycontext_parity.py::test_cgame_native_export_table_and_vmmain_wrappers_match_retail_order` now checks:
  - native wrapper behavior for draw, key, mouse, chat-down, and chat-up paths;
  - legacy `vmMain` dispatch behavior for those same command paths;
  - source native export order through `CG_NATIVE_EXPORT_SET_CLIENT_SPEAKING_STATE`;
  - `dllEntry` publication of `data_100769A8` and API version `8`;
  - the full committed HLIL native table tail, including the null slot at `data_100769E8`.

## Parity Estimate

- Before: native export / legacy `vmMain` bridge parity was high but partially guarded, about 98%.
- After: the same bridge is now directly guarded across the complete recovered export table, about 98.5%.
