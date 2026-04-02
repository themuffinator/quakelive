# UI qmenu Struct Layouts

This note maps the legacy qmenu widget structs still declared in
`src/code/ui/ui_local.h` onto their retail-compatible x86 layouts. The focus is
the small qmenu framework family:

- `menuframework_s`
- `menucommon_s`
- `mfield_t`
- `menufield_s`
- `menuslider_s`
- `menulist_s`
- `menuaction_s`
- `menuradiobutton_s`
- `menubitmap_s`
- `menutext_s`

The goal is to pin exact x86 offsets first, then attach the strongest source
semantics that still explain how these members are used. The committed retail
`uix86.dll` symbol map still does not expose one-to-one qmenu core helpers such
as `Menu_AddItem`, `Menu_Draw`, `Menu_DefaultKey`, `MField_Draw`, or
`ScrollList_Key`. The outer UI ownership around `_UI_KeyEvent`,
`_UI_MouseEvent`, and `_UI_SetActiveMenu` is now retail-mapped, but the inner
legacy qmenu widget core remains source-backed, so this note treats layout as
hard fact and keeps the per-member roles conservative.

The current negative-result evidence is also meaningful here. Broad committed
corpus searches still do not surface bounded retail `UI_PushMenu`,
`UI_PopMenu`, `Menu_AddItem`, `Menu_Draw`, `Menu_DefaultKey`, `MField_Draw`,
`ScrollList_Key`, or `UI_CDKeyMenu` helpers. What the retail corpus *does*
still show is the outer dispatcher layer plus a legacy CD-key script/cvar band:
`_UI_SetActiveMenu`, `UI_HasUniqueCDKey`, the retained `UIMENU_NEED_CD` /
`UIMENU_BAD_CD_KEY` enum values, and `UI_RunMenuScript` branches that service
`getCDKey` / `verifyCDKey` by reading or writing the `cdkey*`, `cdkey`,
`cdkeychecksum`, and `ui_cdkeyvalid` cvars. The committed `_UI_SetActiveMenu`
jump table also matters here: it routes case `5` (`UIMENU_TEAM`) to
`joingame_menu`, does not activate standalone branches for `UIMENU_NEED_CD` or
`UIMENU_BAD_CD_KEY`, and does not expose a separate committed
`UIMENU_POSTGAME` branch. The best current reading is therefore not simply
"qmenu is unmapped yet"; it is that the inner qmenu widget core is not
presently bounded as a standalone retail helper family in the committed
corpus, and several source-side menu routes remain compatibility carry-overs
rather than currently revalidated retail owners.

## Method

- Layout facts come from `src/code/ui/ui_local.h`, cross-checked with a local
  x86 `offsetof` and `sizeof` probe compiled with
  `clang -m32 -target i686-pc-windows-msvc`.
- Historical owner functions and member roles come from the original GPL qmenu
  sources under `assets/quake3/src/code/q3_ui/ui_qmenu.c`,
  `assets/quake3/src/code/q3_ui/ui_mfield.c`, and
  `assets/quake3/src/code/q3_ui/ui_atoms.c`.
- Legacy comparison comes from `assets/quake3/src/code/q3_ui/ui_local.h`.
- Retail revalidation status was checked against the committed `uix86` HLIL and
  Ghidra corpus. The outer stack owners `_UI_KeyEvent`, `_UI_MouseEvent`, and
  `_UI_SetActiveMenu` are promoted there, but no stable raw qmenu widget-core
  helper names have been recovered yet, so this pass lands the type map first
  rather than forcing weak function-name guesses.
- Additional negative-result validation checked the committed corpus for
  `UI_PushMenu`, `UI_PopMenu`, `Menu_AddItem`, `Menu_Draw`, `Menu_DefaultKey`,
  `MField_Draw`, `ScrollList_Key`, and `UI_CDKeyMenu`, and only the outer
  dispatcher / CD-key cvar-script band surfaced cleanly.
- The same check also confirmed a narrower retail script/dispatcher surface
  than the current source tree:
  - `_UI_SetActiveMenu` reaches `main`, `error_popmenu`, `ingame`,
    `ingame_about`, and `joingame_menu`, with case `5` (`UIMENU_TEAM`) landing
    on `joingame_menu`
  - no committed retail `_UI_SetActiveMenu` branch surfaced for
    `UIMENU_POSTGAME`
  - `UI_RunMenuScript` exposes `getCDKey`, `verifyCDKey`, and then
    `loadArenas`, but no separate committed `openCredentials` token or
    bounded `UI_CDKeyMenu` owner

## Hard Layout Facts

- Target layout is 32-bit x86: pointers, handles, and callback slots are
  `4` bytes.
- `qboolean` is a `4` byte enum slot on this target, not a packed bitfield.
- Current retail-compatible sizes are:
  - `sizeof(menuframework_s) = 0x1A0`
  - `sizeof(menucommon_s) = 0x3C`
  - `sizeof(mfield_t) = 0x110`
  - `sizeof(menufield_s) = 0x14C`
  - `sizeof(menuslider_s) = 0x4C`
  - `sizeof(menulist_s) = 0x60`
  - `sizeof(menuaction_s) = 0x3C`
  - `sizeof(menuradiobutton_s) = 0x40`
  - `sizeof(menubitmap_s) = 0x58`
  - `sizeof(menutext_s) = 0x48`
- The only size-changing delta versus the original GPL `q3_ui` header is
  `menuframework_s`:
  - legacy `MAX_MENUITEMS = 64`
  - current `MAX_MENUITEMS = 96`
  - legacy `sizeof(menuframework_s) = 0x120`
  - current `sizeof(menuframework_s) = 0x1A0`
- `menucommon_s`, `mfield_t`, `menufield_s`, `menuslider_s`, and
  `menulist_s` keep the same x86 size as the original GPL qmenu layer.
- `menuaction_s`, `menuradiobutton_s`, `menubitmap_s`, and `menutext_s` also
  keep their original GPL x86 sizes and member ordering unchanged.

## `menuframework_s`

Current x86 size: `0x1A0`

| Offset | Member | Type | Role |
| --- | --- | --- | --- |
| `0x00` | `cursor` | `int` | Current focused item index. `UI_PushMenu`, `Menu_SetCursor`, `Menu_AdjustCursor`, `Menu_DefaultKey`, and `UI_MouseEvent` all route focus through this slot. |
| `0x04` | `cursor_prev` | `int` | Previous focused item index. Used by `Menu_CursorMoved`, wrap fallback in `Menu_AdjustCursor`, and mouse-focus cleanup in `UI_MouseEvent`. |
| `0x08` | `nitems` | `int` | Active item count. Guarded in `Menu_AddItem`, loop bound in `Menu_Draw` and `UI_MouseEvent`, and range check in `Menu_ItemAtCursor`. |
| `0x0C` | `items` | `void *[96]` | Pointer table for child widgets. `Menu_AddItem` stores here, qmenu draw/key paths fetch `menucommon_s *` entries from it. |
| `0x18C` | `draw` | `void (*)(void)` | Optional whole-menu custom draw hook. `UI_Refresh` / `UI_Draw` in the old qmenu path calls this first and falls back to `Menu_Draw` when it is null. |
| `0x190` | `key` | `sfxHandle_t (*)(int key)` | Optional whole-menu key router. `UI_KeyEvent` calls this when present and otherwise falls back to `Menu_DefaultKey`. |
| `0x194` | `wrapAround` | `qboolean` | Enables cursor wrap from end-to-start and start-to-end in `Menu_AdjustCursor`. |
| `0x198` | `fullscreen` | `qboolean` | Marks the menu as fullscreen for `UI_IsFullscreen` and background fill handling in the qmenu refresh path. |
| `0x19C` | `showlogo` | `qboolean` | Selects the logo background shader instead of the no-logo background when `fullscreen` is active. |

## `menucommon_s`

Current x86 size: `0x3C`

| Offset | Member | Type | Role |
| --- | --- | --- | --- |
| `0x00` | `type` | `int` | Widget type tag. Core qmenu dispatch uses it in `Menu_AddItem`, `Menu_Draw`, and `Menu_DefaultKey`. |
| `0x04` | `name` | `const char *` | Widget label or asset name, depending on subtype. Draw helpers use it for labels, and bitmap widgets use it as the shader path. |
| `0x08` | `id` | `int` | Menu-local identifier carried by the widget. qmenu core stores it but leaves meaning to menu-specific callbacks. |
| `0x0C` | `x` | `int` | Primary horizontal anchor used by widget init and draw code. |
| `0x10` | `y` | `int` | Primary vertical anchor used by widget init and draw code. |
| `0x14` | `left` | `int` | Computed left edge of the interaction rectangle. Used by `UI_MouseEvent` and qmenu debug bounds drawing. |
| `0x18` | `top` | `int` | Computed top edge of the interaction rectangle. Used by `UI_MouseEvent` and qmenu debug bounds drawing. |
| `0x1C` | `right` | `int` | Computed right edge of the interaction rectangle. Used by `UI_MouseEvent` and qmenu debug bounds drawing. |
| `0x20` | `bottom` | `int` | Computed bottom edge of the interaction rectangle. Used by `UI_MouseEvent` and qmenu debug bounds drawing. |
| `0x24` | `parent` | `menuframework_s *` | Owning menu pointer. `Menu_AddItem` writes it and most widget draw helpers use `parent->cursor` to decide focus state. |
| `0x28` | `menuPosition` | `int` | Stable slot index inside `parent->items[]`. Focus-aware draw helpers compare `parent->cursor` against this member. |
| `0x2C` | `flags` | `unsigned` | `QMF_*` state and behavior bits such as `GRAYED`, `INACTIVE`, `MOUSEONLY`, `HASMOUSEFOCUS`, `PULSEIFFOCUS`, and `NODEFAULTINIT`. |
| `0x30` | `callback` | `void (*)(void *self, int event)` | Notification hook for `QM_GOTFOCUS`, `QM_LOSTFOCUS`, and `QM_ACTIVATED`. |
| `0x34` | `statusbar` | `void (*)(void *self)` | Per-item status-bar hook. `Menu_Draw` calls it for the item at the cursor when present. |
| `0x38` | `ownerdraw` | `void (*)(void *self)` | Per-item custom draw override. `Menu_Draw` calls this instead of the type-based widget draw switch when set. |

## `mfield_t`

Current x86 size: `0x110`

| Offset | Member | Type | Role |
| --- | --- | --- | --- |
| `0x00` | `cursor` | `int` | Current text insertion point inside `buffer`. Updated by `MField_KeyDownEvent` and `MField_CharEvent`. |
| `0x04` | `scroll` | `int` | Horizontal scroll offset in characters. `MField_Draw` uses it to keep the cursor visible and trim the visible window into `buffer`. |
| `0x08` | `widthInChars` | `int` | Visible field width in characters. Used by `MField_Draw`, arrow-key scrolling, and `MenuField_Init` bounds calculation. |
| `0x0C` | `buffer` | `char[MAX_EDIT_LINE]` | Inline text buffer. `MField_Clear`, `MField_Draw`, `MField_KeyDownEvent`, and `MField_CharEvent` all operate on it directly. |
| `0x10C` | `maxchars` | `int` | Optional caller-imposed text cap. `0` means no extra cap beyond `MAX_EDIT_LINE - 1`. |

## `menufield_s`

Current x86 size: `0x14C`

| Offset | Member | Type | Role |
| --- | --- | --- | --- |
| `0x00` | `generic` | `menucommon_s` | Standard qmenu widget header used for focus, bounds, flags, and callbacks. |
| `0x3C` | `field` | `mfield_t` | Embedded editable text payload. `MenuField_Init`, `MenuField_Draw`, and `MenuField_Key` are thin wrappers over this block. |

## `menuslider_s`

Current x86 size: `0x4C`

| Offset | Member | Type | Role |
| --- | --- | --- | --- |
| `0x00` | `generic` | `menucommon_s` | Standard qmenu widget header. |
| `0x3C` | `minvalue` | `float` | Lower numeric bound enforced by `Slider_Key` and used by `Slider_Draw` when normalizing `range`. |
| `0x40` | `maxvalue` | `float` | Upper numeric bound enforced by `Slider_Key` and used by `Slider_Draw` when normalizing `range`. |
| `0x44` | `curvalue` | `float` | Current slider value. Keyboard and mouse input write it, callbacks observe it, and draw code converts it into thumb position. |
| `0x48` | `range` | `float` | Cached normalized `0..1` thumb fraction recomputed by `Slider_Draw` from `curvalue`, `minvalue`, and `maxvalue`. |

## `menulist_s`

Current x86 size: `0x60`

This struct backs both the small spin-control widget and the larger scroll-list
widget. The first six payload members are shared; the tail members are only
meaningful for scroll-list presentation.

| Offset | Member | Type | Role |
| --- | --- | --- | --- |
| `0x00` | `generic` | `menucommon_s` | Standard qmenu widget header. |
| `0x3C` | `oldvalue` | `int` | Previous selection index. Used to detect selection changes before firing callbacks in scroll-list navigation. |
| `0x40` | `curvalue` | `int` | Current selected row or item index. Shared by `SpinControl_*` and `ScrollList_*`. |
| `0x44` | `numitems` | `int` | Logical item count. `SpinControl_Init` derives it from the null-terminated `itemnames` table; scroll lists treat it as caller-owned state. |
| `0x48` | `top` | `int` | Index of the first visible item in the current page or column band. Scroll-list paging and arrow-key movement maintain it. |
| `0x4C` | `itemnames` | `const char **` | Pointer to the item string table. Spin controls draw `itemnames[curvalue]`; scroll lists draw ranges from this table. |
| `0x50` | `width` | `int` | Per-column text width in characters for scroll-list layout. |
| `0x54` | `height` | `int` | Number of visible rows per column in the scroll list. |
| `0x58` | `columns` | `int` | Number of parallel columns in the scroll-list presentation. |
| `0x5C` | `seperation` | `int` | Inter-column gap in character units. The original id spelling is preserved. |

## `menuaction_s`

Current x86 size: `0x3C`

This is the smallest concrete qmenu widget: it is just a `menucommon_s`
header, with no subtype-specific payload. `Action_Init` derives the clickable
bounds from `generic.name`, and `Action_Draw` uses only inherited header state
to pick colors, pulse/blink style, and the cursor glyph.

| Offset | Member | Type | Role |
| --- | --- | --- | --- |
| `0x00` | `generic` | `menucommon_s` | Entire action widget state. `generic.name` supplies the label text, `x/y` anchor the draw, `left/right/top/bottom` become the clickable bounds, and `parent/menuPosition/flags` drive focus highlighting and cursor rendering. |

## `menuradiobutton_s`

Current x86 size: `0x40`

| Offset | Member | Type | Role |
| --- | --- | --- | --- |
| `0x00` | `generic` | `menucommon_s` | Standard qmenu widget header. `RadioButton_Init` computes bounds from `generic.name`, and `RadioButton_Draw` uses the inherited focus and flag state for highlighting. |
| `0x3C` | `curvalue` | `int` | Current on/off state. `RadioButton_Key` toggles this field on activation and fires `generic.callback`; `RadioButton_Draw` selects `uis.rb_on` or `uis.rb_off` and prints `"on"` or `"off"` from it. |

## `menubitmap_s`

Current x86 size: `0x58`

| Offset | Member | Type | Role |
| --- | --- | --- | --- |
| `0x00` | `generic` | `menucommon_s` | Standard qmenu widget header. `generic.name` is the primary shader path, `x/y` anchor the image, justification flags shift the draw origin, and `parent/flags` control focus overlays. |
| `0x3C` | `focuspic` | `char *` | Optional focus-overlay shader path. `Bitmap_Draw` lazily registers it into `focusshader` the first time the widget draws. |
| `0x40` | `errorpic` | `char *` | Fallback shader path. If `trap_R_RegisterShaderNoMip(generic.name)` fails, `Bitmap_Draw` retries with this string. |
| `0x44` | `shader` | `qhandle_t` | Cached handle for the primary image shader. `Bitmap_Init` zeroes it; `Bitmap_Draw` fills it on first use. |
| `0x48` | `focusshader` | `qhandle_t` | Cached handle for the focus/highlight overlay shader. `Bitmap_Init` zeroes it and `Bitmap_Draw` resolves it from `focuspic` on demand. |
| `0x4C` | `width` | `int` | Requested draw width. `Bitmap_Init` and `Bitmap_Draw` use it when computing bounds and final draw extents. |
| `0x50` | `height` | `int` | Requested draw height. Used with `width` for bounds and final draw extents. |
| `0x54` | `focuscolor` | `float *` | Optional override color for the pulsing or highlighted focus overlay. When null, `Bitmap_Draw` falls back to the shared `pulse_color`. |

## `menutext_s`

Current x86 size: `0x48`

This widget struct is shared by the plain text, proportional text, and banner
text helpers. `Text_Init` and `BText_Init` mark the widget inactive, while
`PText_Init` additionally computes the proportional hit box from the rendered
string width.

| Offset | Member | Type | Role |
| --- | --- | --- | --- |
| `0x00` | `generic` | `menucommon_s` | Standard qmenu widget header. The `generic.name` prefix is optionally prepended by `Text_Draw`, and `generic.flags` select inactive, gray, and pulse-if-focus behaviors across the three text draw paths. |
| `0x3C` | `string` | `char *` | Primary text payload. `Text_Draw` appends it after the optional `generic.name` prefix, while `PText_Draw` and `BText_Draw` render it directly. |
| `0x40` | `style` | `int` | UI string-style flags. Passed to `UI_DrawString`, `UI_DrawProportionalString`, `UI_DrawBannerString`, and to `UI_ProportionalSizeScale` during proportional bounds setup. |
| `0x44` | `color` | `float *` | Default text color pointer. The text draw helpers use this unless the widget is grayed, in which case they force `text_color_disabled`. |

## Practical Reading Notes

- `menuframework_s` is the top-level owner. If a question is about focus,
  fullscreen ownership, or menu-global key routing, start there.
- `menucommon_s` is the shared prefix for almost every qmenu widget. Any widget
  pointer can be treated as `menucommon_s *` for type dispatch, bounds tests,
  focus checks, callbacks, and parent lookup.
- `mfield_t` is a standalone text-edit payload. `menufield_s` is just
  `menucommon_s + mfield_t`.
- `menuslider_s` adds a small numeric payload on top of `menucommon_s`.
- `menulist_s` is overloaded: spin controls use only the selection and string
  table members, while scroll lists additionally rely on `top`, `width`,
  `height`, `columns`, and `seperation`.
- `menuaction_s` is effectively "pure `menucommon_s`": all of its behavior is
  inherited through the shared header.
- `menuradiobutton_s` adds a single boolean-style state slot to the shared
  header.
- `menubitmap_s` adds a small asset-cache tail over `menucommon_s`: two source
  strings, two cached shader handles, geometry, and an optional focus color.
- `menutext_s` is the shared payload for plain, proportional, and banner text
  widgets; the active variant is determined by the qmenu `type` tag, not by a
  different layout.

## Open Questions

1. Determine whether a bounded retail qmenu widget-core slab actually still
   exists in the committed corpus or whether the current retail evidence really
   stops at the outer dispatcher plus the CD-key cvar/script band.
2. Revalidate directly against any future retail evidence for a concrete
   `Menu_AddItem`-style boundary before treating the widened
   `MAX_MENUITEMS = 96` contract as retail-backed rather than source-compatible.
3. Recover any remaining qmenu-side stack owners beneath the already-mapped
   `_UI_KeyEvent`, `_UI_MouseEvent`, `_UI_SetActiveMenu`, and
   `UI_RunMenuScript` surface so the old framework and the newer `ui_shared`
   system are documented side-by-side rather than piecemeal.
