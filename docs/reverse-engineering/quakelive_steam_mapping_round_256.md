# quakelive_steam.exe Mapping Round 256

Date: 2026-05-18

Scope: a deeper implementation reread of the engine-owned client gameplay
mouse movement owner `sub_4B5800` / `CL_MouseMove`, following the round 255
debug-file and cvar-table cleanup.

## Summary

This round did not add new aliases. It moved the source implementation of
`CL_MouseMove` closer to the retail body by reconstructing the gameplay mouse
math and view-angle filter that were still approximated by older Quake III
source behavior.

Classification mix:

- `0` new engine/client aliases
- `0` engine/client alias renames
- `4` engine/client source reconstruction contract fixes
- `0` platform-service-owned functions
- `0` CRT/STL/support-library functions
- `0` Awesomium functions
- `0` Steam SDK support functions

The source-parity wins are:

- [`cl_input.c`](../../src/code/client/cl_input.c) now applies the retail
  gameplay CPI conversion: `mx` / `my` are divided by `m_cpi / 2.5399999618530273`
  rather than multiplied by the previous source-side `1000 / m_cpi` shortcut.
- [`cl_input.c`](../../src/code/client/cl_input.c) now applies the retail
  CPI-enabled view-axis multiplier (`45.45454545454546`) to `m_yaw` and
  `m_pitch`, and the mouse path no longer uses `cl_viewAccel`.
- [`cl_input.c`](../../src/code/client/cl_input.c) now reconstructs the signed
  acceleration formula: `cl_mouseAccel` gates the acceleration branch, the
  rate is multiplied by `1000` when CPI is enabled, power is `cl_mouseAccelPower - 1`
  clamped to zero, positive acceleration adds sensitivity, and negative
  acceleration subtracts sensitivity.
- [`cl_input.c`](../../src/code/client/cl_input.c) now treats `m_filter` as
  the retail view-angle history filter with a `[0, 31]` cvar clamp instead of
  averaging the previous two raw mouse-delta buckets.

## Evidence Notes

Observed facts from the committed retail corpus:

- Round 123 already mapped `sub_4B5800` to `CL_MouseMove`; round 255
  refreshed the same owner and recovered the debug-file path.
- The Ghidra decompile for `FUN_004b5800` shows the gameplay deltas loaded
  from retained raw mouse accumulators, then zeroed before any movement math.
- When `m_cpi` is nonzero, the retail body divides `mx` and `my` by
  `m_cpi / 2.5399999618530273`.
- The acceleration branch is gated by `cl_mouseAccel != 0.0`. Inside it,
  rate is `sqrt(mx*mx + my*my) / frame_msec`, multiplied by `1000` when
  `m_cpi` is nonzero, then reduced by `cl_mouseAccelOffset`.
- Positive post-offset rate is multiplied by `abs(cl_mouseAccel)`, and the
  applied power uses `cl_mouseAccelPower - 1.0` clamped to zero.
- The sign of `cl_mouseAccel` controls whether the powered value is added to
  or subtracted from base `sensitivity`.
- The sensitivity cap check is inside the acceleration branch.
- The yaw and pitch application reads `m_yaw` and `m_pitch`; the same retail
  block only applies the `45.45454545454546` multiplier while `m_cpi` is
  nonzero. No `cl_viewAccel` read appears in the recovered `CL_MouseMove`
  body.
- The adjacent `sub_4B5640` / `sub_4B5710` helpers clamp `m_filter`, reset
  retained history when the cvar is modified, restore the unfiltered yaw/pitch
  base before applying movement, then store and average up to `m_filter`
  retained yaw/pitch samples.

Source-side inference used this round:

- The retained `sub_4B5640` / `sub_4B5710` helpers are source-owned by
  `CL_MouseMove` because they are only called from the recovered mouse
  movement owner and operate directly on the same yaw/pitch state that the
  source exposes through `cl.viewangles`.
- The UI/cgame mouse-event cursor translation helper remains intentionally
  unchanged in this round. The committed `CL_MouseEvent` HLIL suggests a
  raw-delta dispatch path, but that wiring intersects with prior overlay and
  cursor reconstruction and should be resolved as a separate pass.

## Source Reconstruction

- [`cl_input.c`](../../src/code/client/cl_input.c) adds named constants for
  the retail CPI and view-axis scale values.
- [`cl_input.c`](../../src/code/client/cl_input.c) adds small helpers for
  reading retained mouse deltas, applying CPI movement scale, selecting the
  CPI view-axis scale, calculating signed acceleration sensitivity, and
  beginning/ending the retained `m_filter` view-angle history pass.
- [`cl_input.c`](../../src/code/client/cl_input.c) routes `CL_MouseMove`
  through the new helpers and removes the old two-frame raw-delta smoothing
  and `cl_viewAccel` mouse-axis multiplier.
- [`tests/test_engine_cvar_retail_parity.py`](../../tests/test_engine_cvar_retail_parity.py)
  and [`tests/test_engine_client_command_parity.py`](../../tests/test_engine_client_command_parity.py)
  now pin the recovered CPI, signed acceleration, mouse-axis, and filter
  contracts.
- [`docs/client_cvars.md`](../client_cvars.md), the input architecture note,
  and the client parity audit now document the recovered gameplay mouse math.

## Verification

Static/source validation:

- `python -m pytest tests/test_engine_cvar_retail_parity.py tests/test_engine_client_command_parity.py -q --tb=short`
  passed with `51 passed`
- `python -m pytest tests/test_engine_cvar_retail_parity.py tests/test_engine_client_command_parity.py tests/test_input_translation.py -q --tb=short`
  passed with `62 passed`
- `python -m pytest tests/test_client_full_parity_gate.py tests/test_client_config_parity.py tests/test_engine_netcode_parity.py tests/test_platform_services.py -q --tb=short`
  passed with `88 passed, 1 skipped`
- `git diff --check` reported only the repository's existing LF -> CRLF
  normalization warnings
- `pwsh -NoProfile -ExecutionPolicy Bypass -File .vscode/build.ps1 -Solution src/code/quakelive_steam.vcxproj -Configuration Debug -Platform x86`
  compiled the touched client source batch including `cl_input.c`, then failed
  in the unrelated existing `win_net.c` `WSAEVENT` / `ip_socket_event`
  declarations before link

No runtime launch was performed. The source change is bounded to statically
recoverable input math and cvar wiring.

Alias accounting after this pass:

- current `quakelive_steam` aliases: `2238` raw entries, `2231`
  strict address-backed aliases
- strict Ghidra address-backed coverage: `40.764%` of `5473` committed
  functions

Parity estimate after this pass:

- strict `client` parity: `100%` before, `100%` after
- repo-wide checked-in tree parity: `98%` before, `98%` after

The score stays flat because the client parity gate was already closed, but
this pass removes a meaningful source-level approximation in the classic
gameplay input lane.

## Next Queue Head

The next useful client-owned pass is to isolate `CL_MouseEvent`
(`sub_4B54E0`) from the current overlay/cursor reconstruction and decide
whether UI/cgame mouse dispatch should keep the compatibility cursor helper or
return to the raw retail delta dispatch visible in the committed HLIL.
