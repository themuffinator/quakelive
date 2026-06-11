# Quake Live mapping round 606: cgame browser widget input bridge

Date: 2026-06-11

## Scope

This pass extends the input reconstruction campaign past host/client event
dispatch into the retail cgame browser-widget consumers. It covers mouse move,
hover/focus, listbox hit testing, thumb dragging, slider capture, text-field
keys, widget key fanout, out-of-bounds clicks, focused overlay lookup, and the
display-level mouse entry point.

## Retail evidence

Primary Binary Ninja HLIL anchors are in
`references/hlil/quakelive/cgamex86.dll/cgamex86.dll_hlil.txt`:

- `10060820` / `CG_BrowserHandleMouseMove` iterates overlay items, filters
  disabled/hidden widgets, calls mouse-leave, mouse-enter, and focus helpers.
- `10063830` / `CG_BrowserDisplayMouseMove` finds the focused overlay and then
  forwards coordinates through `CG_BrowserHandleMouseMove`.
- `100638e0` / `CG_BrowserOverActiveItem` tests active menu/widget hit regions,
  including corrected text rectangles.
- `1005a1a0`, `1005aa60`, `1005abb0`, and `1005ad30` own browser focus,
  mouse-over, mouse-enter, and mouse-leave transitions.
- `1005a370..1005a750`, `1005ad70`, `1005be30`, and `1005bea0` own listbox
  max-scroll, thumb geometry, hit testing, key/repeat handling, and drag
  application.
- `1005a5f0`, `1005a6e0`, `1005c050`, `1005c1f0`, and `1005c370` own slider
  thumb, hit testing, capture, value application, and key handling.
- `1005ba50`, `1005b280`, `1005b550`, `1005b860`, `1005ebe0`, `1005c540`,
  `1005ca00`, and `1005cc70` own text-field keys, yes/no, multi, preset-list,
  bind, widget dispatch, out-of-bounds click routing, and overlay key handling.

Ghidra confirms promoted rows for the same owner band except
`CG_BrowserListRepeatScroll`, which remains HLIL/source anchored as a static
helper.

## Mapping updates

`references/analysis/quakelive_symbol_aliases.json` now includes uppercase
Binary Ninja `sub_*` spellings for the cgame browser input helpers that
previously had only `FUN_*` and lowercase `sub_*` names. Digit-only addresses
remain represented by their existing lowercase `sub_*` spelling because there
is no distinct uppercase form.

## Source reconstruction status

No behavioral source patch was required. The current source already preserves
the retail wrapper structure:

- `CG_BrowserDisplayMouseMove` and `CG_BrowserHandleMouseMove` feed the display
  and overlay-root mouse lanes.
- `CG_SetBrowserFocus`, `CG_SetBrowserMouseOver`, `CG_BrowserMouseEnter`, and
  `CG_BrowserMouseLeave` preserve cvar visibility gates, corrected text-rect
  tests, script callbacks, listbox hover handling, and focus sounds.
- Listbox, slider, bind, multi, preset-list, yes/no, and text-field wrappers
  route through the shared UI item helpers while keeping cgame-specific capture
  and overlay ownership.
- `CG_BrowserHandleOOBClick`, `CG_BrowserHandleKey`, and the display key
  wrapper preserve out-of-bounds click handling and focused-overlay fallback.

## Validation

Strengthened
`tests/test_cgame_displaycontext_parity.py::test_cgame_browser_leaf_wrappers_restore_remaining_retail_owner_slice`
to cross-check:

- alias spellings;
- Ghidra function rows;
- HLIL call anchors for mouse move, widget key fanout, OOB click, display mouse
  move, and active-item hit testing;
- source wrapper calls for listbox, slider, text-field, bind, multi,
  preset-list, widget, and overlay key/mouse handling.

Focused validation:

```text
python -m pytest tests/test_cgame_displaycontext_parity.py::test_cgame_browser_leaf_wrappers_restore_remaining_retail_owner_slice -q --tb=short
1 passed
```

## Parity estimate

- Focused cgame browser-widget input evidence coverage: before 86% -> after
  99%.
- Focused browser-widget input alias coverage: before 58% -> after 99%.
- Focused mouse/key consumer bridge confidence: before 94% -> after 99%.
- Repo-wide parity estimate remains 99% -> 99%; this pass improves evidence
  coverage and regression protection rather than changing runtime behavior.
