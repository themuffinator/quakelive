# Quake Live Steam Mapping Round 338: QLLoadHandler Document-Ready Scripts

Date: 2026-05-29

Scope: Awesomium `QLLoadHandler` document-ready behavior, launcher script
execution, and live WebUI readiness publication.

## Evidence Checked

- `references/reverse-engineering/ghidra/quakelive_steam/metadata.txt` keeps
  `quakelive_steam.exe` as the owning retail binary for the browser host.
- `references/reverse-engineering/ghidra/quakelive_steam/analysis_symbols.txt`
  identifies the browser listener vtables:
  `QLDialogHandler::vftable` at `0x00547fa8`,
  `QLViewHandler::vftable` at `0x00547fc0`, and
  `QLLoadHandler::vftable` at `0x00547fe8`.
- `references/hlil/quakelive/quakelive_steam.exe/quakelive_steam.exe_hlil_split/quakelive_steam.exe_hlil_part06.txt:35617`
  shows the `QLLoadHandler` vtable entries, including
  `OnDocumentReady` at slot `0x0c` pointing to `sub_4317f0`.
- `references/hlil/quakelive/quakelive_steam.exe/quakelive_steam.exe_hlil_split/quakelive_steam.exe_hlil_part01.txt:44449-44538`
  maps `sub_4317f0`: it enumerates `js/*.js`, builds `js/<name>`, reads each
  script, executes it through WebView slot `0x124`, refreshes the retained
  `window` object, and publishes `web.object.ready`.
- The bootstrap in
  `references/hlil/quakelive/quakelive_steam.exe/quakelive_steam.exe_hlil_split/quakelive_steam.exe_hlil_part05.txt:16045-16053`
  installs a four-byte `QLLoadHandler` object on WebView slot `0x28` after the
  dialog and view listeners.

## Source Reconstruction

- `src/code/client/cl_cgame.c` now keeps document-script diagnostics on the
  retained browser host: loaded, executed, and failed script counts.
- `QLLoadHandler_LoadDocumentScripts()` still resolves scripts through the
  reconstructed launcher path, `CL_LauncherRequestData`, so `web.pak`,
  `fs_webpath`, and filesystem fallbacks stay in retail order.
- For live Awesomium, each recovered script is now executed through
  `CL_Awesomium_ExecuteJavascript`, which is the SDK C-export-backed
  reconstruction of retail WebView slot `0x124`.
- `QLLoadHandler_PollLiveDocumentReady()` bridges the missing native listener
  object by polling `CL_Awesomium_IsLoading()` after each `CL_Awesomium_Update`.
  When loading clears, it calls `QLLoadHandler_OnFinishLoadingFrame()` and then
  `QLLoadHandler_OnDocumentReady()`.
- `QLWebHost_OpenURL()` and the live reload path now mark the document as
  loading and wait for that frame-pump projection instead of immediately
  publishing readiness after `LoadURL` or reload dispatch.

## Guardrails

- This round does not reconstruct the `Awesomium::WebViewListener::Load` C++
  object layout or install a local vtable. That remains an SDK/native-object
  gap.
- The source change reconstructs the observable engine-owned behavior around
  script resolution, script execution, and `web.object.ready` ordering.
- Script data stays external to source: no WebUI bundle or Awesomium SDK code is
  vendored or copied into the repository.

## Parity Movement

Before this round, the focused `QLLoadHandler_OnDocumentReady` lane was about
`78%` source-reconstructed: the vtable row, script enumeration, qz bind, and
ready event existed, but the recovered scripts were only read and freed, and
live readiness was declared synchronously after `LoadURL`.

After this round, the lane is about `92%` source-reconstructed and `98%` mapped.
The remaining gap is native listener-object installation and exact Awesomium
`JSObject` window refresh semantics, which stay behind the broader native
handler/JS marshalling gap.
