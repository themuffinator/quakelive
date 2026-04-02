# Quake Live Steam Host Mapping Round 101

## Scope

This round moves off the Win32 host seam from
[Round 100](./quakelive_steam_mapping_round_100.md) and closes the adjacent
`cl_keys.c` ownership block in the engine binary.

The evidence order for this pass was:

- `references/reverse-engineering/ghidra/quakelive_steam/functions.csv`
- `references/hlil/quakelive/quakelive_steam.exe/quakelive_steam.exe_hlil.txt`
- writable terminology in
  [cl_keys.c](../../src/code/client/cl_keys.c)
  and the event-loop anchor in
  [common.c](../../src/code/qcommon/common.c)

Two earlier aliases were already useful anchors inside this seam:

- `sub_4B6570 -> Key_KeynumToString`
- `sub_4B6C90 -> Key_GetBinding`
- `sub_4B6CB0 -> Key_GetKey`
- `sub_4B8200 -> CL_AddReliableCommand`

Everything promoted this round hangs off those anchors plus the retail event
loop at `0x004CBCD1`, where event case `1` calls `sub_4B7B00` and event case
`2` calls `sub_4B71C0`.

## Field Editing Owners

The field-edit cluster now reads cleanly as the retained `Field_*` source
owners.

Observed local facts:

1. `sub_4B6890` implements the character-edit path for a `field_t`-shaped
   buffer: `Ctrl+V` paste, `Ctrl+C` clear, backspace/delete, home/end, insert
   mode, cursor/scroll maintenance, and printable-character insertion.
2. `sub_4B72A0` calls the retained retail Unicode clipboard helper at
   `sub_4ECDF0`, converts each UTF-16 code unit to UTF-8 bytes with
   `WideCharToMultiByte`, then feeds those bytes back through the same field
   editing rules as if the user had typed them.
3. `sub_4B74E0` handles the non-printable key side of the same fields:
   shift-insert paste, delete, left/right/home/end navigation, and overstrike
   toggling.

That resolves the owner names as:

| Raw symbol | Alias candidate | Basis | Observed role |
| --- | --- | --- | --- |
| `sub_4B6890` (`0x004B6890`) | `Field_CharEvent` | Observed + source-owner match | Character-input edit path for console/chat fields, with retained UTF-8-aware insertion and deletion. |
| `sub_4B72A0` (`0x004B72A0`) | `Field_Paste` | Observed + source-owner match | Clipboard paste helper that replays clipboard text through `Field_CharEvent` semantics. |
| `sub_4B74E0` (`0x004B74E0`) | `Field_KeyDownEvent` | Observed + source-owner match | Non-printable key handler for editable text fields. |

## Key Binding And Registration Helpers

The next block is a direct run through the early `cl_keys.c` binding helpers.

Observed local facts:

1. `sub_4B6AF0` returns the global overstrike toggle and `sub_4B6B00` writes
   it, matching `Key_GetOverstrikeMode` / `Key_SetOverstrikeMode`.
2. `sub_4B6B30` matches the full `Key_StringToKeynum` contract: empty-string
   rejection, single-character return, `0x11` hex parsing, and keyname-table
   lookup.
3. `sub_4B6C10` frees and replaces the binding string for a key slot, sets the
   archive-dirty flag, and notifies the browser-facing binding surface when the
   value changes, which is the Quake Live-retained `Key_SetBinding` owner.
4. `sub_4B6D00`, `sub_4B6D60`, and `sub_4B6DF0` are exact command handlers for
   `unbind`, `unbindall`, and `bind`.
5. `sub_4B6F80`, `sub_4B6FE0`, and `sub_4B7030` match `Key_WriteBindings`,
   `Key_Bindlist_f`, and `CL_InitKeyCommands` through their literal command
   strings and registration flow.

| Raw symbol | Alias candidate | Basis | Observed role |
| --- | --- | --- | --- |
| `sub_4B6AF0` (`0x004B6AF0`) | `Key_GetOverstrikeMode` | Observed + exact source match | Returns the retained overstrike toggle. |
| `sub_4B6B00` (`0x004B6B00`) | `Key_SetOverstrikeMode` | Observed + exact source match | Writes the retained overstrike toggle. |
| `sub_4B6B30` (`0x004B6B30`) | `Key_StringToKeynum` | Observed + exact source match | Resolves ASCII, `0xNN`, and named key tokens into key numbers. |
| `sub_4B6C10` (`0x004B6C10`) | `Key_SetBinding` | Observed + source-owner match | Replaces a key binding string, marks archive state dirty, and republishes browser-facing binding changes. |
| `sub_4B6D00` (`0x004B6D00`) | `Key_Unbind_f` | Observed + exact source match | Console command owner for `unbind`. |
| `sub_4B6D60` (`0x004B6D60`) | `Key_Unbindall_f` | Observed + exact source match | Console command owner for `unbindall`. |
| `sub_4B6DF0` (`0x004B6DF0`) | `Key_Bind_f` | Observed + exact source match | Console command owner for `bind`. |
| `sub_4B6F80` (`0x004B6F80`) | `Key_WriteBindings` | Observed + exact source match | Writes `unbindall` plus the current `bind` lines to a file handle. |
| `sub_4B6FE0` (`0x004B6FE0`) | `Key_Bindlist_f` | Observed + exact source match | Console command owner for `bindlist`. |
| `sub_4B7030` (`0x004B7030`) | `CL_InitKeyCommands` | Observed + exact source match | Clears key globals and registers the bind-family console commands. |

## Input Dispatch Owners

The remaining block closes the runtime dispatch path from queued input events
into the field, chat, UI, cgame, and command-binding handlers.

Observed local facts:

1. `sub_4B70E0` tokenizes a binding on `;`, emits `-%s key time\n` for button
   releases, and forwards any down-only trailing commands, which is the exact
   `CL_AddKeyUpCommands` contract.
2. The retail event loop in `sub_4CBCD1` dispatches event type `1` to
   `sub_4B7B00` and event type `2` to `sub_4B71C0`, matching the
   `CL_KeyEvent` / `CL_CharEvent` split in writable `common.c`.
3. `sub_4B71C0` special-cases the console key, converts one incoming UTF-16
   code unit to UTF-8, then routes the resulting bytes to console, UI, chat,
   or disconnected-console handling. That is the `CL_CharEvent` owner with a
   Steam-specific Unicode implementation delta.
4. `sub_4B7660` matches `Console_Key` across enter submission, history recall,
   scrollback keys, and tab completion.
5. `sub_4B79B0` matches `Message_Key` across escape cancel, enter submission,
   reply/tell/team chat formatting, and fallback field editing.
6. `sub_4B7B00` updates `keys[key].down`, repeat counts, and `anykeydown`,
   hardcodes the console key, special-cases escape routing, processes key-up
   button bindings, and fans key-down events into console, UI, cgame, chat, or
   the bound-command executor. Quake Live adds demo/browser-specific behavior
   inside the same owner, but the ownership match is stable.
7. `sub_4B80E0` walks every key slot, synthesizes the needed key-up side
   effects for any key still down, resets repeat/down state, and zeroes the
   aggregate count, matching `Key_ClearStates`.

| Raw symbol | Alias candidate | Basis | Observed role |
| --- | --- | --- | --- |
| `sub_4B70E0` (`0x004B70E0`) | `CL_AddKeyUpCommands` | Observed + exact source match | Expands button-release bindings into `-cmd key time` text and forwards queued down-only fragments. |
| `sub_4B71C0` (`0x004B71C0`) | `CL_CharEvent` | Observed + source-owner match | Character-event dispatcher; retail Steam converts UTF-16 input to UTF-8 before routing it. |
| `sub_4B7660` (`0x004B7660`) | `Console_Key` | Observed + source-owner match | Console-line handler for enter, completion, history, and scrollback. |
| `sub_4B79B0` (`0x004B79B0`) | `Message_Key` | Observed + source-owner match | In-game chat input handler for escape, enter, reply/tell/team chat, and fallback field editing. |
| `sub_4B7B00` (`0x004B7B00`) | `CL_KeyEvent` | Observed + source-owner match | Main key event dispatcher for console, UI, cgame, message, and bound-command handling. |
| `sub_4B80E0` (`0x004B80E0`) | `Key_ClearStates` | Observed + source-owner match | Releases any still-down keys through the normal key-up side effects, then zeroes the retained state. |

## New High-Confidence Aliases Added This Round

- field editing:
  - `sub_4B6890`
  - `sub_4B72A0`
  - `sub_4B74E0`
- key binding helpers:
  - `sub_4B6AF0`
  - `sub_4B6B00`
  - `sub_4B6B30`
  - `sub_4B6C10`
  - `sub_4B6D00`
  - `sub_4B6D60`
  - `sub_4B6DF0`
  - `sub_4B6F80`
  - `sub_4B6FE0`
  - `sub_4B7030`
- input dispatch:
  - `sub_4B70E0`
  - `sub_4B71C0`
  - `sub_4B7660`
  - `sub_4B79B0`
  - `sub_4B7B00`
  - `sub_4B80E0`

## Open Questions

1. `sub_4ECDF0` remains the retail-only Unicode clipboard fetch helper under
   `Field_Paste`. The behavior is now tightly bounded, but I still do not have
   a strong enough retail owner name to promote it directly.
2. `sub_4B81F0` sits immediately after `Key_ClearStates` and still needs one
   more ownership pass before I would name it.
3. `sub_4F1290`, `sub_4F2900`, and `sub_4F4640` remain the highest-value
   unmapped leftovers from the recent host/browser/ZMQ passes.

## Verification

I validated the alias artifact directly:

- `references/analysis/quakelive_symbol_aliases.json` parses cleanly through
  `ConvertFrom-Json`
- recount after this pass: `1026` raw alias entries, `1025` address-backed
  alias entries

## Completion Stats After Round 101

- Ghidra baseline: `5473` functions, `351` imports, `2` exports, `4377`
  analysis symbols
- Current mapping coverage: `1026` raw alias entries, `1025` address-backed
  aliases
- Address-backed coverage: `18.728%` of `5473` functions
- Alias delta this round: `19`
- Estimated parity for this round: `94% -> 94%`

This was a mapping-only pass. It closes the core retained input/key handling
owners, but it does not change the writable-source parity estimate by itself.
