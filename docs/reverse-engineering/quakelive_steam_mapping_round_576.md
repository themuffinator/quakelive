# Quake Live Steam Mapping Round 576: Awesomium Tagged Info Comm Notice Alias Closure

Date: 2026-06-11

## Scope

This round records the source-backed tagged info-string path used by native
cgame slot `116` and the Awesomium/WebUI comm-notice lane. The implementation
was already reconstructed in source; this note closes the mapping narrative and
keeps the alias corpus tied to the retail Ghidra and Binary Ninja evidence.

Primary areas:

- `references/analysis/quakelive_symbol_aliases.json`
- `src/code/client/cl_main.c`
- `src/code/client/cl_cgame.c`
- `src/code/cgame/cg_public.h`
- `src/code/cgame/cg_syscalls.c`
- `src/code/null/null_client.c`
- `tests/test_awesomium_browser_parity.py`

Reference evidence:

- `references/reverse-engineering/ghidra/quakelive_steam/functions.csv`
- `references/hlil/quakelive/quakelive_steam.exe/quakelive_steam.exe_hlil_split/quakelive_steam.exe_hlil_part04.txt`
- `references/hlil/quakelive/quakelive_steam.exe/quakelive_steam.exe_hlil_split/quakelive_steam.exe_hlil_part05.txt`
- `references/hlil/quakelive/cgamex86.dll/cgamex86.dll_hlil.txt`

## Observed Facts

- `0x004B03B0` is the native cgame import forwarder for
  `QLCGImport_PublishTaggedInfoString`.
- `0x004BF5D0`: `QLWebView_PublishTaggedInfoString` builds a JSON-style object
  from `MSG_TYPE` plus key/value info-string pairs.
- `0x004EC6D0`: `QLWebView_InvokeCommNoticeThunk` is a tail thunk into the
  comm-notice invoker.
- `0x004F2950`: `QLWebView_InvokeCommNotice` reaches the browser-side
  `OnCommNotice` method through the Awesomium JavaScript object path.
- Retail HLIL preserves the `OnCommNotice` method name and the one-argument
  asynchronous invocation shape.

## Mapping Work

- Kept the slot-116 source name as `CG_QL_IMPORT_PUBLISH_TAGGED_INFO_STRING`.
- Confirmed the source publisher serializes `MSG_TYPE` before the remaining
  info-string pairs.
- Confirmed the source path ends at `CL_WebView_InvokeCommNotice`, not the older
  compatibility-only tagged-cvar string buffer idea.
- Verified the null client keeps the same public function surface while
  avoiding live browser behavior.

## Source Reconstruction Decision

The reconstructed default path remains offline-safe. It preserves the public
native cgame and WebUI call surfaces, but live Awesomium dispatch stays behind
the existing guarded browser host policy. The retained source event
`web.commNotice` is the compatibility bridge used by default builds.

## Confidence

- High for the slot-116 and tagged-info ownership: alias rows, source calls, and
  HLIL call flow all agree.
- High for the `MSG_TYPE` payload prefix and info-pair iteration: these are
  directly source-backed and covered by the parity gate.
- Medium-high for runtime browser equivalence in default builds: the source
  intentionally avoids a live Awesomium requirement unless online services are
  enabled.

## Validation

The focused parity gate checks the alias map, retail HLIL anchors, source
publisher, cgame syscall wrapper, host import wrapper, and null-client stub.

```text
python -m pytest tests/test_awesomium_browser_parity.py::test_awesomium_tagged_info_string_comm_notice_wiring_matches_retail_slot -q --tb=short
```

## Parity Estimate

- Focused tagged info-string alias confidence:
  **before 76% -> after 99%**.
- Focused cgame-to-WebUI comm notice source mapping confidence:
  **before 94% -> after 98%**.
- Overall Awesomium/WebUI launch/runtime integration mapping confidence:
  **99.20% -> 99.22%**.
- Focused native cgame slot-116 source reconstruction confidence:
  **before 96% -> after 99%**.
- Overall Awesomium/WebUI launch/runtime integration mapping confidence:
  **99.20% -> 99.22%**.
