# UI Window Struct Layouts

This note maps the shared UI window primitives declared in
`src/code/ui/ui_shared.h`: `rectDef_t` and `windowDef_t`.

These records sit below the menu/item layer and are reused almost everywhere in
the shared UI runtime. Their x86 layout is stable across the Team Arena
baseline and the current Quake Live-compatible tree. The strongest evidence
here now comes from both the current shared UI runtime and the committed retail
`uix86.dll` map: the core shared-window/runtime slab is already promoted around
`Fade`, `Window_Paint`, `Item_SetScreenCoords`, `Menu_UpdatePosition`,
`Rect_ContainsPoint`, `Menu_FindItemByName`, `Menu_ShowItemByName`,
`Script_FadeIn`, `Script_FadeOut`, `Item_Paint`, and `Menu_Paint`.

## Method

- Layout facts come from a local x86 `sizeof` and `offsetof` probe compiled
  with `clang -m32 -target i686-pc-windows-msvc` against
  `src/code/ui/ui_shared.h`.
- Legacy comparison comes from the Team Arena-era
  `assets/quake3/src/code/ui/ui_shared.h`.
- Current member roles were cross-checked against:
  - the already-mapped retail/shared helpers `Fade`, `Window_Paint`,
    `Item_SetScreenCoords`, `Menu_UpdatePosition`, `Rect_ContainsPoint`,
    `Menu_FindItemByName`, `Menu_ShowItemByName`, `Script_FadeIn`,
    `Script_FadeOut`, `Menu_TransitionItemByName`, `Script_Transition`,
    `Menu_OrbitItemByName`, `Script_Orbit`, `Item_Paint`, and `Menu_Paint`
  - `Window_Init`, `Item_UpdatePosition`, and `Window_CacheContents` in
    `src/code/ui/ui_shared.c`
  - the item/menu parser helpers in `src/code/ui/ui_shared.c`
  - `UI_LauncherPlayCinematic` handoff consumers in the shared script path
- Retail parity is now materially stronger than when this note was first
  written. The committed corpus already names the central paint, hit-test,
  focus/visibility, fade, and transition/orbit helpers for this struct. The
  effect-field ownership is now mostly direct-retail-backed as well:
  `Menu_TransitionItemByName` seeds the transition target and per-step deltas,
  `Menu_OrbitItemByName` seeds the orbit center and cadence, and `Item_Paint`
  consumes those fields through the `nextTime` gate. The remaining uncertainty
  is now narrower and mostly about secondary carry-over details such as the
  retained outline-related color path.

## Hard Layout Facts

- Target layout is 32-bit x86: `float`, `int`, `qboolean`, pointers, and
  `qhandle_t` slots are `4` bytes.
- `sizeof(rectDef_t) = 0x10`.
- `sizeof(windowDef_t) = 0xB4`.
- Both structs keep the same x86 size and member ordering as the Team Arena
  baseline.
- The current runtime shows that the old header comments on `windowDef_t` are
  stale:
  - `rectClient` is the authored/local rectangle parsed from menu files and
    mutated by effect paths
  - `rect` is the resolved screen-space rectangle used for hit testing and
    painting after parent offsets and widescreen correction

## `rectDef_t`

Current x86 size: `0x10`

This is the shared float rectangle type used for authored menu coordinates,
resolved screen rectangles, border/fill regions, animation targets, and hit
tests.

| Offset | Member | Type | Role |
| --- | --- | --- | --- |
| `0x00` | `x` | `float` | Left edge / X position. Used by every shared hit-test, paint, and layout path. |
| `0x04` | `y` | `float` | Top edge / Y position. |
| `0x08` | `w` | `float` | Width. |
| `0x0C` | `h` | `float` | Height. |

`Rect_ContainsPoint` treats the rectangle as an open interior test
`x > rect->x && x < rect->x + rect->w` and the same for Y, so the current UI
runtime does not consider points exactly on the outer edge as contained.

## `windowDef_t`

Current x86 size: `0xB4`

This is the common per-window state block embedded by both `itemDef_t` and
`menuDef_t`. It combines authored geometry, resolved geometry, background and
border paint state, ownerdraw metadata, runtime animation/fade state, and the
optional cinematic handle.

| Offset | Member | Type | Role |
| --- | --- | --- | --- |
| `0x00` | `rect` | `Rectangle` | Resolved screen-space rectangle used by `Window_Paint`, `Rect_ContainsPoint`, and runtime hit-testing after `Menu_UpdatePosition` / `Item_SetScreenCoords` apply parent offsets and widescreen correction. |
| `0x10` | `rectClient` | `Rectangle` | Authored/local rectangle parsed from menu files. `Menu_UpdatePosition` and `Item_SetScreenCoords` project this into `rect`, and the transition/orbit effect paths mutate this source rectangle over time. |
| `0x20` | `name` | `const char *` | Window/item identifier parsed from `name`. Used by menu lookup and group/member matching helpers. |
| `0x24` | `group` | `const char *` | Optional grouping tag parsed from `group`. Used by the shared menu helpers that address multiple items by group name. |
| `0x28` | `cinematicName` | `const char *` | Optional cinematic path parsed from `cinematic`. Used by `Window_Paint` and `Window_CacheContents` to start/precache cinematics. |
| `0x2C` | `cinematic` | `int` | Runtime cinematic handle. `Window_Init` seeds it to `-1`, `Window_Paint` uses `-1` as “not started yet”, `-2` as a failed-start sentinel, and non-negative values as active handles. |
| `0x30` | `style` | `int` | Background/window paint style selector. `Window_Paint` switches on this field for filled, gradient, shader, team-color, and cinematic windows. |
| `0x34` | `border` | `int` | Border style selector. `Window_Paint` switches on this field for full, horizontal, vertical, and KC-gradient borders. |
| `0x38` | `ownerDraw` | `int` | Owning ownerdraw ID passed through to `DC->ownerDrawItem`, `DC->ownerDrawHandleKey`, and `DC->ownerDrawWidth`. |
| `0x3C` | `ownerDrawFlags` | `int` | Owning visibility/filter flags passed to the ownerdraw visibility and key handlers. |
| `0x40` | `borderSize` | `float` | Border thickness. `Window_Init` defaults it to `1`, `Window_Paint` uses it to inset the fill region, and parent border presence also shifts child layout in the menu/item position helpers. |
| `0x44` | `flags` | `int` | Window runtime flag word: visibility, focus, decoration, fading, wrapping, popup, etc. `Fade`, visibility checks, and many interaction paths read and modify this field. |
| `0x48` | `rectEffects` | `Rectangle` | Retail effect target/anchor rectangle. `Menu_TransitionItemByName` copies the destination rect here for timed transitions, while `Menu_OrbitItemByName` stores the orbit center in `x/y` and `Item_Paint` consumes the same field as the live orbit anchor. |
| `0x58` | `rectEffects2` | `Rectangle` | Retail per-step transition deltas. `Menu_TransitionItemByName` derives the absolute X/Y/W/H increments from the source and destination rects, and `Item_Paint` consumes them to walk `rectClient` toward `rectEffects`. |
| `0x68` | `offsetTime` | `int` | Effect/fade cadence in milliseconds. `Menu_TransitionItemByName` and `Menu_OrbitItemByName` seed it for scripted motion, and shared fade/orbit/transition paths reuse it as the update interval. |
| `0x6C` | `nextTime` | `int` | Next scheduled tick time for fades, transitions, orbit motion, and model rotation updates. `Item_Paint` advances transition/orbit work only when `DC->realTime > nextTime`, then rewrites the gate to `realTime + offsetTime`. |
| `0x70` | `foreColor` | `vec4_t` | Foreground tint. `Window_Paint` uses it for shader-style windows when `WINDOW_FORECOLORSET` is present; item text fades also drive its alpha component. |
| `0x80` | `backColor` | `vec4_t` | Background/fill tint. Used by filled windows and gradient bars; `Fade` drives `backColor[3]` for fading filled windows with shaders. |
| `0x90` | `borderColor` | `vec4_t` | Border tint used by all explicit border paint paths. |
| `0xA0` | `outlineColor` | `vec4_t` | Outline/highlight color used by some listbox selection fills and retained outline-related text paths. |
| `0xB0` | `background` | `qhandle_t` | Background shader handle. Parsed from `background`, reused by shader-style and filled windows, and also receives the shader returned by the Quake Live launcher-video bridge path. |

## Current Ownership Split

- `Window_Init` owns the structural defaults:
  - zero the whole record
  - `borderSize = 1`
  - `foreColor = {1,1,1,1}`
  - `cinematic = -1`
- The parser helpers own the authored/static fields:
  - `rectClient`, `name`, `group`, `cinematicName`, `style`, `border`,
    `borderSize`, colors, `background`, `ownerDraw`, and `ownerDrawFlags`
- `Menu_UpdatePosition` and `Item_SetScreenCoords` own the projection from
  `rectClient` into the live `rect` field.
- the already-mapped retail/runtime helpers `Fade`, `Window_Paint`,
  `Menu_TransitionItemByName`, `Script_Transition`, `Menu_OrbitItemByName`,
  `Script_Orbit`, `Script_FadeIn`, `Script_FadeOut`, and `Item_Paint` own the
  runtime fields with a narrower split than before:
  - `flags`
  - `cinematic`
  - `Menu_TransitionItemByName` seeds `WINDOW_INTRANSITION`, `WINDOW_VISIBLE`,
    `offsetTime`, `rectClient`, `rectEffects`, and `rectEffects2`
  - `Menu_OrbitItemByName` seeds `WINDOW_ORBITING`, `WINDOW_VISIBLE`,
    `offsetTime`, `rectEffects.x/y`, and the starting `rectClient.x/y`
  - `Item_Paint` consumes `nextTime`, `offsetTime`, `rectEffects`, and
    `rectEffects2` to advance orbit or transition motion and then refreshes the
    resolved screen coordinates

## Open Questions

1. Revisit whether the retained `outlineColor` text-outline path is truly live
   in retail or just a preserved carry-over surface; the current tree has a
   live listbox-selection use, but the text-outline draw path remains commented
   out.
