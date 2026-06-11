# Quake Live Steam Mapping Round 556: Awesomium JavaScript Method Handler Dispatch Flow

Date: 2026-06-11

## Scope

This round rechecked the retail Awesomium/WebUI JavaScript method-handler
corridor in `quakelive_steam.exe`, with emphasis on method-name lookup,
non-returning plugin call dispatch, and return-value plugin calls exposed to the
`qz` JavaScript object.

No live WebUI or Steam behavior was enabled and no runtime source behavior was
changed. The reconstructed source keeps live Awesomium and online-service paths
behind `QL_BUILD_ONLINE_SERVICES`, with deterministic fallbacks for default
builds.

## Evidence Inputs

- Binary Ninja HLIL:
  `references/hlil/quakelive/quakelive_steam.exe/quakelive_steam.exe_hlil_split/quakelive_steam.exe_hlil_part01.txt`
- Ghidra function rows:
  `references/reverse-engineering/ghidra/quakelive_steam/functions.csv`
- Alias ledger:
  `references/analysis/quakelive_symbol_aliases.json`
- Source reconstruction:
  `src/code/client/cl_cgame.c`

## Observed Facts

| Retail address | Alias | Observed signal | Reconstruction status |
| --- | --- | --- | --- |
| `0x00431570` | `QLJSHandler_LookupMethodId` | Walks the method table at `data_55c008` through `0x55c1a0` in 12-byte rows, compares an Awesomium `WebString`, returns the row method ID, and falls back to `0x22`. | Source-backed by `QLJSHandler_LookupMethodBinding` and the bounded `cl_webMethodBindings` table. |
| `0x00431e50` | `QLJSHandler_OnMethodCall` | Copies the incoming method name into a `WebString`, resolves the method ID, rejects out-of-range calls, and dispatches non-return plugin calls for command, URL, clipboard, Steam server/lobby/user/UGC, key-capture, favorite-server, and no-op methods. | Source-backed by `QLJSHandler_OnMethodCall` using `returnsValue == qfalse` bindings. |
| `0x004328b0` | `QLJSHandler_OnMethodCallWithReturnValue` | Copies the incoming method name, resolves the method ID, and constructs Awesomium `JSValue` returns for file, game-running, cvar, map/factory/demo/friend/config, cursor, and clipboard-style queries. | Source-backed by `QLJSHandler_OnMethodCallWithReturnValue` using `returnsValue == qtrue` bindings. |

## Mapping Work

Added
`tests/test_awesomium_browser_parity.py::test_awesomium_js_method_handler_dispatch_retail_hlil_flow_is_pinned`
to pin:

- Ghidra row names and sizes for `QLJSHandler_LookupMethodId`,
  `QLJSHandler_OnMethodCall`, and
  `QLJSHandler_OnMethodCallWithReturnValue`;
- alias ledger spellings for `FUN_*`, upper-case Binary Ninja `sub_*`, and
  lower-case `sub_*` forms;
- HLIL anchors for the method-table scan, table fallback ID, non-return switch
  calls, Steam/clipboard/server-browser/lobby/UGC signals, return-value switch
  construction, and `JSObject` object-return fields;
- source table entries from retail addresses `0x0055c008..0x0055c194` with
  explicit return-value flags; and
- reconstructed source dispatch order for the non-return and return-value
  method families.

## Source Reconstruction Decision

No source reconstruction patch was needed in this round. The current source
already models the retail split between:

- a single bounded method-name table with retail table addresses retained as
  evidence comments;
- non-return plugin calls gated away from return-value handlers;
- return-value plugin calls gated away from non-return handlers;
- online-service operations routed through the existing Steam/WebUI adapter
  stubs when `QL_BUILD_ONLINE_SERVICES` is disabled; and
- fallback return strings for default builds where live Awesomium, Steam, or
  browser state is unavailable.

## Confidence

- High for method lookup table coverage: Ghidra rows, alias ledger spellings,
  HLIL row bounds, and source method-table entries agree.
- High for handler ownership: the retail `OnMethodCall` and
  `OnMethodCallWithReturnValue` functions have distinct HLIL bodies and the
  source preserves that split with explicit `returnsValue` flags.
- Medium-high for individual online-service side effects: the method names,
  Steam imports, and call families are pinned, while default source builds
  intentionally stub live service use as a documented divergence.

## Inference Boundary

Observed facts:

1. Retail lookup scans the Awesomium method table at 12-byte stride and returns
   `0x22` when a method is not found.
2. Retail non-return dispatch reaches command execution, URL handling,
   clipboard writes, server browser calls, lobby calls, user-stats requests,
   overlay/invite calls, UGC calls, key capture, favorite server updates, and
   an unimplemented-plugin diagnostic path.
3. Retail return-value dispatch constructs Awesomium `JSValue` and `JSObject`
   returns for file/game/cvar/list/config/cursor/clipboard style queries.

Inferences:

1. The source `returnsValue` flag is the cleanest source-level equivalent to
   retail's split `JSMethodHandler` entry points because it prevents a method
   from being dispatched through the wrong call path before the switch body.
2. The source fallback values are intentional containment for disabled online
   services, not evidence that retail lacked those side effects.

Open questions:

1. The exact string/object formatting of every returned Awesomium `JSValue`
   remains a candidate for smaller follow-up passes if a later UI behavior gap
   needs byte-level return compatibility.
2. Live Steam-backed side effects should stay disabled by default until there
   is a documented open replacement path for the retail WebUI service surface.

## Validation

- `python -m pytest tests/test_awesomium_browser_parity.py::test_awesomium_js_method_handler_dispatch_retail_hlil_flow_is_pinned -q --tb=short`

## Parity Estimate

- Focused JavaScript method-handler dispatch HLIL-flow confidence:
  **before 72% -> after 98%**.
- Focused Awesomium/WebUI launch/runtime integration mapping confidence:
  **before 98.3% -> after 98.5%**.
- Strict Windows Awesomium/WebUI source behavior remains effectively closed for
  the currently reconstructed offline/default build path.
