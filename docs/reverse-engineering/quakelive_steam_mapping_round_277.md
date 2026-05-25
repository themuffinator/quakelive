# Quake Live Steam Host Mapping Round 277

## Scope

- Continued the client-host mapping pass around `src/code/client/cl_input.c`
  and adjacent console/input registration wiring in `quakelive_steam.exe`.
- Focused on console initialization, low-level key button state helpers,
  movement command thunks, joystick/mouse filter helpers, usercmd creation,
  packet-send readiness, and the `CL_SendCmd` orchestration path.

## Evidence

- `references/reverse-engineering/ghidra/quakelive_steam/metadata.txt`
  reports `5473` functions, `351` imports, `2` exports, and `4377` analysis
  symbols for the retail client host.
- `references/reverse-engineering/ghidra/quakelive_steam/functions.csv`
  confirms address-backed rows for the main promoted owners:
  - `FUN_004b4a30`, `FUN_004b4be0`, `FUN_004b4c60`,
    `FUN_004b4cf0`
  - `FUN_004b5290`, `FUN_004b5360`, `FUN_004b5570`,
    `FUN_004b55b0`, `FUN_004b5640`, `FUN_004b5710`
  - `FUN_004b5bd0`, `FUN_004b5c70`, `FUN_004b5de0`,
    `FUN_004b5e60`, `FUN_004b62a0`, `FUN_004b6330`
- `references/hlil/quakelive/quakelive_steam.exe/quakelive_steam.exe_hlil.txt`
  provides the host-side control flow:
  - `0x004B4A30` registers the console cvars and commands including
    `toggleconsole`, `messagemode`, `messagemode2`, `clear`, `condump`,
    and `find`, matching `Con_Init`.
  - `0x004B4BE0` and `0x004B4C60` implement retail key down/up tracking
    around duplicate keys, manual console release, accumulated msec, active
    state, and `wasPressed`.
  - `0x004B4CF0` computes the normalized frame fraction for a `kbutton_t`,
    clamps the result, and clears the consumed msec/pressed edge.
  - `0x004B4D80` through `0x004B4F60` are tiny command thunks that call the
    key helpers for movement, look, speed, attack, button, and centerview
    commands. Some of these wrappers are visible in HLIL but not emitted as
    standalone rows in Ghidra `functions.csv`.
  - `0x004B5290` applies keyboard look/turn angles through `cl_anglespeedkey`,
    `cl_yawspeed`, `cl_pitchspeed`, and `CL_KeyState`.
  - `0x004B5360` assembles keyboard movement, walking speed, and clamped
    forward/right/up usercmd bytes.
  - `0x004B5570` stores joystick axis values and errors on invalid axes with
    `CL_JoystickEvent: bad axis %i`.
  - `0x004B55B0`, `0x004B5640`, and `0x004B5710` cover joystick movement and
    the retail mouse filter begin/end helpers.
  - `0x004B5BD0` builds usercmd button bits from `in_buttons`, including talk
    and any-key state.
  - `0x004B5C70` creates the command, calling angle, button, keyboard, mouse,
    and joystick helpers before storing the final usercmd fields.
  - `0x004B5DE0` creates new commands when the client is primed or active and
    caps `frame_msec` at `200`.
  - `0x004B5E60` checks demo/cinematic/download/active state, loopback/LAN
    status, `cl_maxpackets` bounds, and packet timing before permitting a send.
  - `0x004B62A0` runs command creation, readiness testing, packet writing, and
    optional `cl_showSend` output.
  - `0x004B6330` registers the input command surface and cvars.

## Promoted Aliases

Updated `references/analysis/quakelive_symbol_aliases.json`:

| Address | Alias | Confidence | Evidence |
| --- | --- | --- | --- |
| `sub_4B4A30` | `Con_Init` | High | Console cvar and command registration owner. |
| `sub_4B4BD0` | `IN_MLookDown` | High | `+mlook` registration target sets the mlook latch. |
| `sub_4B4BE0` | `IN_KeyDown` | High | Key down helper with duplicate-key guard and retail warning string. |
| `sub_4B4C60` | `IN_KeyUp` | High | Key up helper with manual-console and frame-msec release paths. |
| `sub_4B4CF0` | `CL_KeyState` | High | Normalized key-state frame fraction helper. |
| `sub_4B4D80` | `IN_UpDown` | High | `+moveup` thunk to `IN_KeyDown`. |
| `sub_4B4D90` | `IN_UpUp` | High | `-moveup` thunk to `IN_KeyUp`. |
| `sub_4B4DA0` | `IN_DownDown` | High | `+movedown` thunk to `IN_KeyDown`. |
| `sub_4B4DB0` | `IN_DownUp` | High | `-movedown` thunk to `IN_KeyUp`. |
| `sub_4B4DC0` | `IN_LeftDown` | High | `+left` thunk to `IN_KeyDown`. |
| `sub_4B4DD0` | `IN_LeftUp` | High | `-left` thunk to `IN_KeyUp`. |
| `sub_4B4DE0` | `IN_RightDown` | High | `+right` thunk to `IN_KeyDown`. |
| `sub_4B4DF0` | `IN_RightUp` | High | `-right` thunk to `IN_KeyUp`. |
| `sub_4B4E00` | `IN_ForwardDown` | High | `+forward` thunk to `IN_KeyDown`. |
| `sub_4B4E10` | `IN_ForwardUp` | High | `-forward` thunk to `IN_KeyUp`. |
| `sub_4B4E20` | `IN_BackDown` | High | `+back` thunk to `IN_KeyDown`. |
| `sub_4B4E30` | `IN_BackUp` | High | `-back` thunk to `IN_KeyUp`. |
| `sub_4B4E40` | `IN_LookupDown` | High | `+lookup` thunk to `IN_KeyDown`. |
| `sub_4B4E50` | `IN_LookupUp` | High | `-lookup` thunk to `IN_KeyUp`. |
| `sub_4B4E60` | `IN_LookdownDown` | High | `+lookdown` thunk to `IN_KeyDown`. |
| `sub_4B4E70` | `IN_LookdownUp` | High | `-lookdown` thunk to `IN_KeyUp`. |
| `sub_4B4E80` | `IN_MoveleftDown` | High | `+moveleft` thunk to `IN_KeyDown`. |
| `sub_4B4E90` | `IN_MoveleftUp` | High | `-moveleft` thunk to `IN_KeyUp`. |
| `sub_4B4EA0` | `IN_MoverightDown` | High | `+moveright` thunk to `IN_KeyDown`. |
| `sub_4B4EB0` | `IN_MoverightUp` | High | `-moveright` thunk to `IN_KeyUp`. |
| `sub_4B4EC0` | `IN_SpeedDown` | High | `+speed` thunk to `IN_KeyDown`. |
| `sub_4B4ED0` | `IN_SpeedUp` | High | `-speed` thunk to `IN_KeyUp`. |
| `sub_4B4EE0` | `IN_StrafeDown` | High | `+strafe` thunk to `IN_KeyDown`. |
| `sub_4B4EF0` | `IN_StrafeUp` | High | `-strafe` thunk to `IN_KeyUp`. |
| `sub_4B4F00` | `IN_Button0Down` | High | `+attack` thunk to button slot 0. |
| `sub_4B4F10` | `IN_Button0Up` | High | `-attack` thunk to button slot 0. |
| `sub_4B4F20` | `IN_Button2Down` | High | `+button2` thunk to button slot 2. |
| `sub_4B4F30` | `IN_Button2Up` | High | `-button2` thunk to button slot 2. |
| `sub_4B4F40` | `IN_Button3Down` | High | `+button3` thunk to button slot 3. |
| `sub_4B4F50` | `IN_Button3Up` | High | `-button3` thunk to button slot 3. |
| `sub_4B4F60` | `IN_CenterView` | High | `centerview` command target resets pitch from snapshot delta. |
| `sub_4B5290` | `CL_AdjustAngles` | High | Keyboard look/turn angle adjustment helper. |
| `sub_4B5360` | `CL_KeyMove` | High | Keyboard movement assembly helper. |
| `sub_4B5570` | `CL_JoystickEvent` | High | Joystick axis event storage and retail bad-axis error string. |
| `sub_4B55B0` | `CL_JoystickMove` | High | Joystick movement and view-axis application helper. |
| `sub_4B5640` | `CL_BeginMouseFilter` | High | Retail mouse filter setup and modified-cvar reset owner. |
| `sub_4B5710` | `CL_EndMouseFilter` | High | Retail mouse history update and averaging owner. |
| `sub_4B5BD0` | `CL_CmdButtons` | High | Usercmd button-bit assembly helper. |
| `sub_4B5C70` | `CL_CreateCmd` | High | Usercmd construction owner. |
| `sub_4B5DE0` | `CL_CreateNewCommands` | High | Primed/active command creation owner. |
| `sub_4B5E60` | `CL_ReadyToSendPacket` | High | Send throttling and `cl_maxpackets` owner. |
| `sub_4B62A0` | `CL_SendCmd` | High | Top-level usercmd send orchestration owner. |
| `sub_4B6300` | `IN_MLookUp` | High | `-mlook` registration target clears latch and recenters when needed. |
| `sub_4B6330` | `CL_InitInput` | High | Input command and cvar registration owner. |

## Source Notes

- No runtime source behavior was changed in this round.
- Retail `0x004B5C70` appears to inline the final move storage that the source
  keeps as `CL_FinishMove`. This is a structural difference in recovery shape,
  not a behavior concern for the current source.
- Retail `CL_InitInput` evidence in this slice directly shows the classic
  movement surface, `+attack`, `+button2`, `+button3`, `+mlook`, `-mlook`,
  `ListInputDevices`, `cl_nodelta`, and `cl_debugMove`. The current source
  retains additional higher button registrations for compatibility; this pass
  records the recovered retail surface without removing those extensions.
- The 2026-05-25 usercmd movement-transport re-audit follows this lane into
  the network packet writer: client-side source now pins that command stream
  through `CL_WritePacket`, including the `cl_packetdup` resend window,
  `clc_move` / `clc_moveNoDelta` selection, checksum-feed plus server-command
  hash key, ordered `MSG_WriteDeltaUsercmdKey` loop, and `outPackets`
  bookkeeping used later for ping calculation.

## Still Open

- Higher `+button4` through `+button14` source registrations remain a
  compatibility note for later review because the observed retail host slice
  did not show matching command registrations in `0x004B6330`.
- This pass did not change mouse-math behavior. The previously reconstructed
  `CL_MouseMove` owner at `0x004B5800` remains the behavior authority for that
  lane.

## Guardrail

- Added
  `tests/test_engine_client_command_parity.py::test_client_input_mapping_round_277_promotes_console_input_and_usercmd_symbols`.
- The guard checks:
  - promoted aliases in `quakelive_symbol_aliases.json`;
  - matching Ghidra function rows for the main input/usercmd owners;
  - host HLIL snippets for console init, key state, movement thunks, joystick,
    mouse filter, command creation, packet readiness, send orchestration, and
    input registration;
  - source-side `CL_FinishMove`/`CL_CreateCmd` structure and the documented
    retail inline-storage note.

## Parity Estimate

- Before: focused console/input/usercmd symbol confidence was strong from
  source parity and scattered address evidence, but many stable retail owners
  remained outside the alias ledger, about `87%` for this focused lane.
- After: the console init, key state, movement thunk, joystick, mouse filter,
  usercmd creation, command send, and input registration owners are explicitly
  mapped and guarded, about `95%` for this focused lane.
- Overall strict Windows replacement parity remains `100%`; repo-wide parity
  remains `98%`. This pass improves evidence freshness and symbol precision
  rather than closing a new runtime gap.
