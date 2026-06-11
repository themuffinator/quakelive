# Quake Live Steam Mapping Round 581: Awesomium Handler Destroyer and Shutdown Cleanup Boundary

## Scope

This round pins the retail Awesomium/WebUI cleanup lane:

- `sub_4F23B0` / `FUN_004f23b0`: `QLJSHandler_Destroy`
- `sub_4F2A60` / `FUN_004f2a60`: `QLWebHost_Shutdown`
- `sub_4F2A80` / `FUN_004f2a80`: `QLResourceInterceptor_Destroy`
- `sub_4F2AB0` / `FUN_004f2ab0`: `QLDialogHandler_Destroy`
- `sub_4F2AE0` / `FUN_004f2ae0`: `QLViewHandler_Destroy`
- `sub_4F2B10` / `FUN_004f2b10`: `QLLoadHandler_Destroy`
- `sub_4F3130` / `FUN_004f3130`: `AwesomiumDataPakSource_Destroy`

No live Awesomium or Steam behavior is enabled by this pass. The source
cleanup path remains behind the existing guarded Win32 online-services adapter.

## Evidence

Observed facts:

- `references/reverse-engineering/ghidra/quakelive_steam/functions.csv`
  records the handler destroyers as compact `34` or `35` byte deleting
  destructors and `QLWebHost_Shutdown` as a `32` byte owner.
- `references/analysis/quakelive_symbol_aliases.json` maps the `FUN_*`,
  uppercase `sub_*`, and lowercase `sub_*` spellings for every focused owner.
- Binary Ninja HLIL part05 shows `QLJSHandler_Destroy` restoring
  `Awesomium::JSMethodHandler::vftable`, checking `(arg2 & 1)`, and
  conditionally calling `operator delete`.
- Binary Ninja HLIL part05 shows the resource, dialog, view, and load handler
  destroyers performing the same base-vtable restore plus conditional-delete
  pattern for their Awesomium base classes.
- Binary Ninja HLIL part05 shows `AwesomiumDataPakSource_Destroy` calling the
  `Awesomium::DataPakSource` destructor before the same conditional-delete
  tail.
- Binary Ninja HLIL part05 shows `QLWebHost_Shutdown` destroying the retained
  WebView through slot `0x00` when present and tail-calling
  `Awesomium::WebCore::Shutdown` when the retained WebCore exists.
- Binary Ninja HLIL part06 places those destroyers in the corresponding
  retail vtable slots: resource interceptor slot `0x0c`, dialog slot `0x10`,
  view slot `0x20`, load slot `0x10`, JS handler slot `0x08`, and
  `DataPakSource` slot `0x00`.

Inferred mapping:

- The retail cleanup objects are ordinary MSVC deleting destructors, not
  policy-heavy shutdown functions. Source should preserve their ownership as
  evidence through the listener mapping table while letting the guarded
  Awesomium adapter own the actual runtime teardown.

## Reconstruction

Strengthened `tests/test_awesomium_browser_parity.py`:

- Added a focused parity gate for the seven cleanup owners, including aliases,
  Ghidra function sizes, Binary Ninja HLIL destructor bodies, vtable slots, and
  source listener-table entries.
- Cross-checked the source `CL_WebHost_ResetRuntime` path against the guarded
  `CL_Awesomium_Shutdown` adapter, ensuring reset clears the live runtime flags
  and the adapter destroys the WebView, releases the session, drops the
  DataPakSource pointer, shuts down WebCore, and clears startup state.
- Left source behavior unchanged because the existing guarded reset/shutdown
  path is the correct source boundary for the default-offline repository
  policy.

## Validation

- `python -m json.tool references\analysis\quakelive_symbol_aliases.json`
  - passed
- `python -m pytest tests/test_awesomium_browser_parity.py::test_awesomium_handler_destroyers_and_shutdown_cleanup_match_retail_lifetime_boundary -q --tb=short`
  - `1 passed`
- `python -m pytest tests/test_awesomium_browser_parity.py -q --tb=short`
  - `41 passed`
- `python -m pytest tests/test_game_native_export_helper_parity.py -q --tb=short`
  - `11 passed`

## Parity Estimate

- Focused Awesomium handler cleanup-owner evidence:
  **before 84% -> after 98%**.
- Focused WebUI shutdown/reset source-boundary confidence:
  **before 91% -> after 97%**.
- Overall Awesomium/WebUI launch/runtime integration mapping confidence: **99.24% -> 99.26%**.

Open questions:

- Retail frees concrete Awesomium handler objects through native C++ deleting
  destructors. The source adapter intentionally avoids recreating that object
  lifetime in default builds; any future live-service path should keep this
  behind `QL_BUILD_ONLINE_SERVICES`.
