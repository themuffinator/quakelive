# quakelive_steam.exe Mapping Round 254

Date: 2026-05-18

Scope: a focused reread of the engine-owned client timing owner
`sub_4B07C0` / `CL_SetCGameTime`, plus the adjacent client cvar-registration
wiring in `CL_Init`.

## Summary

This round did not add new aliases. It tightened one already-mapped client
owner where the source still carried a placeholder `cl_autoTimeNudge` branch
even though the committed retail HLIL exposes the retained Quake Live behavior.

Classification mix:

- `0` new engine/client aliases
- `0` engine/client alias renames
- `2` engine/client source reconstruction contract fixes
- `0` platform-service-owned functions
- `0` CRT/STL/support-library functions
- `0` Awesomium functions
- `0` Steam SDK support functions

The source-parity wins are:

- [`cl_cgame.c`](../../src/code/client/cl_cgame.c) now selects client time
  nudge through the recovered spectator, LAN, manual, auto half-ping,
  previous-value, and clamp contract instead of the old zero placeholder.
- [`cl_main.c`](../../src/code/client/cl_main.c) now registers the engine-side
  ROM `cg_spectating` cvar visible in the retained `CL_Init` cvar table.

## Evidence Notes

Observed facts from the committed retail corpus:

- Round 129 already mapped `sub_4B07C0` to `CL_SetCGameTime` with high
  confidence.
- The HLIL for `sub_4B07C0` reads the retained `cg_spectating` cvar first; a
  nonzero spectator state forces the selected nudge to `0`.
- Non-spectator play calls `sub_4EE570(data_1617c04, data_1617c08)` before
  considering user nudge. Round 219 already identifies `sub_4EE570` as
  `Sys_IsLANAddress`, so LAN/local server play also forces nudge `0`.
- When `cl_autoTimeNudge` is disabled, the owner reads `cl_timeNudge`.
- When `cl_autoTimeNudge` is enabled, the owner derives the nudge from
  `cl.snap.ping * -0.5`, preserves the previous nonzero auto-nudge value when
  it differs, clamps the result to `[-20, 0]`, stores it, then subtracts that
  nudge from `cls.realtime + cl.serverTimeDelta`.
- The snapshot parser initializes the same ping slot to `999` and then
  replaces it from the outgoing-packet realtime delta, matching source
  `cl.snap.ping`.
- The retained `CL_Init` cvar table registers `cl_autoTimeNudge`,
  `cg_spectating`, `timedemo`, and `cl_timeNudge`; the checked-in source had
  the first and last entries but was missing the engine-side
  `cg_spectating` registration.

Source-side inference used this round:

- The committed `Sys_IsLANAddress` helper is the appropriate source owner for
  the retained address-family/private-LAN check, because its HLIL mapping and
  implementation shape already match the `sub_4EE570` body.

## Source Reconstruction

- [`cl_cgame.c`](../../src/code/client/cl_cgame.c) adds
  `CL_SelectClientTimeNudge()` and `CL_ClampTimeNudge()`.
- [`cl_cgame.c`](../../src/code/client/cl_cgame.c) adds the retained
  previous-nudge storage as `cl_autoTimeNudgePrevious`.
- [`cl_cgame.c`](../../src/code/client/cl_cgame.c) routes `CL_SetCGameTime`
  through the selector and removes the placeholder comments and forced zero
  auto-nudge behavior.
- [`cl_main.c`](../../src/code/client/cl_main.c) registers
  `cg_spectating` as a ROM cvar in client init.
- [`tests/test_engine_cvar_retail_parity.py`](../../tests/test_engine_cvar_retail_parity.py)
  now pins the recovered selector shape and `cg_spectating` registration.
- [`docs/client_cvars.md`](../client_cvars.md) and the client parity audit now
  document the timing/cvar contract.

## Verification

Static/source validation:

- `python -m pytest tests/test_engine_cvar_retail_parity.py tests/test_client_full_parity_gate.py -q --tb=no`
  passed with `38 passed, 1 skipped`
- `python -m pytest tests/test_client_config_parity.py tests/test_engine_netcode_parity.py tests/test_platform_services.py -q --tb=no`
  passed with `86 passed`
- `pwsh -NoProfile -ExecutionPolicy Bypass -File .vscode/build.ps1 -Solution src/code/quakelive_steam.vcxproj -Configuration Debug -Platform x86`
  compiled the touched client files, then failed in the unrelated existing
  `win_net.c` `WSAEVENT` / `ip_socket_event` declarations before link
- `git diff --check` reported only the repository's existing LF -> CRLF
  normalization warnings

No runtime launch was performed. The source change is bounded to a statically
recoverable timing branch, and the committed HLIL/Ghidra evidence was
sufficient.

Alias accounting after this pass:

- current `quakelive_steam` aliases: `2238` raw entries, `2231`
  strict address-backed aliases
- strict Ghidra address-backed coverage: `40.764%` of `5473` committed
  functions

Parity estimate after this pass:

- strict `client` parity: `100%` before, `100%` after
- repo-wide checked-in tree parity: `98%` before, `98%` after

The score stays flat because the client gate was already closed, but the
classic timing lane now has stronger source-level fidelity and less latent
placeholder risk.

## Next Queue Head

The next useful client-owned pass is to continue reading already-mapped large
owners whose source carries old uncertainty comments, especially input timing
and command-generation code, and only open source work where the HLIL exposes
a concrete divergence.
