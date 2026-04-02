# UI Menu Struct Layouts

This note maps `menuDef_t`, the shared top-level menu record declared in
`src/code/ui/ui_shared.h`.

`menuDef_t` builds directly on the already-mapped `windowDef_t` front matter
and adds menu-local script hooks, focus/fade state, widescreen policy, and the
fixed-capacity child-item pointer bank. The x86 layout is stable across the
Team Arena baseline and the current Quake Live-compatible tree.

## Method

- Layout facts come from a local x86 `sizeof` and `offsetof` probe compiled
  with `clang -m32 -target i686-pc-windows-msvc` against
  `src/code/ui/ui_shared.h`.
- Legacy comparison comes from the Team Arena-era
  `assets/quake3/src/code/ui/ui_shared.h`.
- Current member roles were cross-checked against:
  - the already-mapped retail/shared helpers `Menu_SetupKeywordHash`,
    `Menu_Parse`, `Menu_UpdatePosition`, `Menu_ClearFocus`,
    `Menu_SetFeederSelection`, `Menus_ActivateByName`, `Menus_CloseByName`,
    `Menus_CloseAll`, `Menu_SetPrevCursorItem`, `Menu_SetNextCursorItem`,
    `Menu_HandleMouseMove`, `Menu_Paint`, `Menu_PaintAll`, and
    `Menu_OverActiveItem`
  - `Menu_Init`, `Menu_PostParse`, `Menu_GetFocusedItem`,
    `Menu_ScrollFeeder`, `Menus_AnyFullScreenVisible`, and `Menus_Activate` in
    `src/code/ui/ui_shared.c`
  - the menu parser helpers in `src/code/ui/ui_shared.c`
  - the child append path in `MenuParse_itemDef`
- Retail parity is now stronger than when this note was first written. The
  committed corpus already exposes the core parser, visibility, focus, and
  paint slab for shared menus. `Menu_PostParse` and a few init-side defaults
  still rely more heavily on the preserved source tree, but most member roles
  below are directly retail-backed.

## Hard Layout Facts

- Target layout is 32-bit x86: pointers, `qboolean`, `int`, and `float` slots
  are `4` bytes.
- `MAX_MENUITEMS = 96` in both the Team Arena baseline and the current tree.
- `sizeof(menuDef_t) = 0x288`.
- `menuDef_t` keeps the same x86 size and member ordering as the Team Arena
  baseline.
- The struct is divided into three bands:
  - embedded `Window window`: `0x000-0x0B3`
  - menu-local policy/script/color state: `0x0B4-0x107`
  - child item pointer bank: `0x108-0x287`
- `0x288 = 0x108 + MAX_MENUITEMS * 4`, so there is no trailing padding after
  the `items[]` array.

## `menuDef_t`

Current x86 size: `0x288`

| Offset | Member | Type | Role |
| --- | --- | --- | --- |
| `0x000` | `window` | `Window` | Embedded shared window record controlling the menu background, border, authored/resolved rectangle, visibility flags, ownerdraw gating, and optional cinematic/background shader. |
| `0x0B4` | `font` | `const char *` | Parsed menu-level font declaration. The current tree uses it only during `MenuParse_font` to normalize/register fonts into `DC->Assets`; no per-menu runtime consumer was found afterward. |
| `0x0B8` | `fullScreen` | `qboolean` | Fullscreen menu latch. `Menu_PostParse` expands the menu rectangle to `SCREEN_WIDTH x SCREEN_HEIGHT`, `Menus_AnyFullScreenVisible` uses it for fullscreen-state queries, and `Menu_Paint` uses it to draw the full-screen background path. |
| `0x0BC` | `widescreen` | `int` | Menu-level widescreen policy. `Menu_UpdatePosition` applies it to the menu window rectangle, and `UI_ResolveWidescreenMode` uses it as the default policy for child items that did not set their own mode. |
| `0x0C0` | `itemCount` | `int` | Number of valid child pointers in `items[]`. Used as the loop bound throughout menu parse, focus, interaction, feeder, cache, and paint paths. |
| `0x0C4` | `fontIndex` | `int` | Retained structural slot from the legacy menu layer. No active parser or runtime consumer was found in the current tree or the Team Arena baseline. |
| `0x0C8` | `cursorItem` | `int` | Current focused child-item index for keyboard navigation. `Menu_Init` seeds it to `-1`, focus/navigation helpers update it, and mouse-followed keyboard navigation reuses it when moving focus. |
| `0x0CC` | `fadeCycle` | `int` | Menu-local fade timing period. Seeded from `DC->Assets.fadeCycle` in `Menu_Init`, optionally overridden by `fadeCycle` in menu files, and passed through to `Window_Paint` / item fade paths. |
| `0x0D0` | `fadeClamp` | `float` | Menu-local fade alpha clamp. Seeded from `DC->Assets.fadeClamp`, optionally overridden by `fadeClamp` in menu files, and used by window/item fade logic. |
| `0x0D4` | `fadeAmount` | `float` | Menu-local fade delta. Seeded from `DC->Assets.fadeAmount`, optionally overridden by `fadeAmount` in menu files, and used by window/item fade logic. |
| `0x0D8` | `onOpen` | `const char *` | Menu-open script parsed from `onOpen`. `Menus_Activate` runs it when the menu becomes visible/focused. |
| `0x0DC` | `onClose` | `const char *` | Menu-close script parsed from `onClose`. `Menus_CloseByName` runs it before clearing visibility. |
| `0x0E0` | `onESC` | `const char *` | Escape-key script parsed from `onESC`. `Menu_HandleKey` runs it on the escape path when the menu is active and the UI is not waiting for a bind key. |
| `0x0E4` | `soundName` | `const char *` | Background loop sound token parsed from `soundLoop`. `Menus_Activate` starts it, and `Menu_CacheContents` precaches it through `DC->registerSound`. |
| `0x0E8` | `focusColor` | `vec4_t` | Shared highlight color for focused items in this menu. Item paint paths derive pulsing lowlight/highlight blends from it. |
| `0x0F8` | `disableColor` | `vec4_t` | Shared tint for disabled items in this menu. Item paint paths copy this color when an item is disabled by cvar gating. |
| `0x108` | `items` | `itemDef_t *[MAX_MENUITEMS]` | Fixed-capacity child item pointer bank. `MenuParse_itemDef` allocates and appends children here, and nearly all menu interaction/paint paths walk this array up to `itemCount`. |

## Current Ownership Split

- `Menu_Init` owns the structural defaults:
  - zero the whole record
  - `cursorItem = -1`
  - `fadeAmount = DC->Assets.fadeAmount`
  - `fadeClamp = DC->Assets.fadeClamp`
  - `fadeCycle = DC->Assets.fadeCycle`
  - `widescreen = WIDESCREEN_STRETCH`
  - initialize the embedded `window`
- The menu parser helpers own the authored/static menu fields:
  - `font`
  - `fullScreen`
  - `widescreen`
  - `window` subfields such as `name`, `rectClient`, colors, and background
  - `onOpen`
  - `onClose`
  - `onESC`
  - `soundName`
  - `focusColor`
  - `disableColor`
  - optional overrides for `fadeClamp`, `fadeAmount`, and `fadeCycle`
- `MenuParse_itemDef` owns child construction:
  - allocate a new `itemDef_t`
  - initialize it
  - parse it
  - set `parent = menu`
  - append it at `items[itemCount++]`
- `Menu_PostParse` owns the initial resolved geometry:
  - force fullscreen menu bounds when `fullScreen`
  - call `Menu_UpdatePosition`
- the already-mapped retail/shared helpers `Menus_ActivateByName`,
  `Menus_CloseByName`, `Menus_CloseAll`, `Menu_HandleMouseMove`,
  `Menu_SetFeederSelection`, `Menu_SetPrevCursorItem`,
  `Menu_SetNextCursorItem`, `Menu_OverActiveItem`, `Menu_Paint`, and
  `Menu_PaintAll` own the live focus/selection/render state centered on
  `cursorItem` and `items[]`.

## Open Questions

1. Revisit the remaining init-only ownership around `Menu_PostParse` and any
   adjacent defaults if future retail evidence exposes cleaner boundaries. The
   core parser, visibility, focus, and paint slab for this struct is already
   directly retail-backed.
2. Revisit `fontIndex` if later retail evidence surfaces a removed or dormant
   font-selection path; the slot is structurally stable, but no active consumer
   was found in the committed trees.
