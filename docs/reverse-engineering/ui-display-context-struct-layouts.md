# UI Display Context Struct Layouts

This note maps the front `uiDC` slab embedded in `uiInfo_t`: the top-level
`displayContextDef_t` plus its directly embedded `cachedAssets_t`.

This is the strongest retail-backed nested UI record currently exposed in the
committed tree. The retail `uix86.dll` `_UI_Init` body (`FUN_1000fab0`) seeds
the callback table and tail state in one contiguous block, while the current
`src/code/ui` tree still preserves the shared consumer paths that explain what
each slot does.

## Method

- Layout facts come from a local x86 `sizeof` and `offsetof` probe compiled
  with `clang -m32 -target i686-pc-windows-msvc` against
  `src/code/ui/ui_shared.h`, using the Win32 preprocessor path expected by
  `q_shared.h`.
- The historical baseline comes from the Team Arena-era
  `assets/quake3/src/code/ui/ui_shared.h`.
- Current member roles were cross-checked against:
  - the already-mapped retail helpers `_UI_Init`, `AssetCache`, `Text_Width`,
    `Text_Height`, `Text_Paint`, `Text_PaintWithCursor`, `Text_Paint_Limit`,
    `UI_OwnerDraw`, `UI_OwnerDrawVisible`, `UI_OwnerDrawHandleKey`,
    `UI_FeederCount`, `UI_FeederItemText`, `UI_FeederItemImage`,
    `UI_FeederSelection`, `UI_Pause`, `UI_ReadableSize`, `UI_PrintTime`,
    `Display_MouseMove`, and `Menu_PaintAll`
  - the asset-global parser in `src/code/ui/ui_main.c`
  - `Init_Display`, `Display_GetContext`, the scripted menu runtime, and the
    item/menu paint paths in `src/code/ui/ui_shared.c`
- Retail parity is strongest for `_UI_Init` (`FUN_1000fab0`) plus the mapped
  callback owners it installs into this block. The committed `uix86` corpus now
  directly names most of the callback table and the main ownerdraw/feeder/text
  consumers, and the remaining uncertainty is narrower than before:
  `UI_GetValue` and `UI_GetTeamColor` are now revalidated as pure stub
  callbacks, while the unresolved asset side is concentrated in a small set of
  parser-visible-but-unconsumed or clearly dormant carry-over slots.

## Hard Layout Facts

- Target layout is 32-bit x86: pointers, callbacks, `qhandle_t`, `sfxHandle_t`,
  `qboolean`, and `int` slots are `4` bytes.
- `sizeof(fontInfo_t) = 0x5044`.
- `sizeof(glconfig_t) = 0x2C44`.
- `sizeof(cachedAssets_t) = 0xF190`.
- `sizeof(displayContextDef_t) = 0x11ECC`.
- Major `displayContextDef_t` bands are:
  - callback table: `0x0000-0x00C7`
  - per-frame/runtime scalars: `0x00C8-0x00E7`
  - cached UI assets: `0x00E8-0xF277`
  - copied renderer config: `0xF278-0x11EBB`
  - tail shader/metrics fields: `0x11EBC-0x11ECB`
- Relative to the Team Arena baseline, the only size delta is one extra
  callback:
  - legacy `sizeof(displayContextDef_t) = 0x11EC8`
  - current `sizeof(displayContextDef_t) = 0x11ECC`
  - inserted field: `playLauncherCinematic` at offset `0x0B8`

## `cachedAssets_t`

Current x86 size: `0xF190`

This is the heavyweight asset bank embedded inside `displayContextDef_t`. Most
of its size comes from the three in-place `fontInfo_t` records; the remainder
is a compact shader/sound/tuning tail.

| Offset | Member | Type | Role |
| --- | --- | --- | --- |
| `0x0000` | `fontStr` | `const char *` | Retained legacy font-path slot. The current asset-global parser and the committed retail token set both go straight through `font`, `smallFont`, and `bigFont` registration paths instead of storing through this field, and no active consumer was found. |
| `0x0004` | `cursorStr` | `const char *` | Parsed cursor-shader path. The asset-global parser fills it before registering `Assets.cursor`. |
| `0x0008` | `gradientStr` | `const char *` | Retained legacy gradient-path slot. The live parser path and committed retail token set use `gradientbar` and register `Assets.gradientBar` directly instead of storing through this field, and no active consumer was found. |
| `0x000C` | `textFont` | `fontInfo_t` | Primary UI font. Populated by `AssetCache` or the asset-global `font` directive and used by the text paint helpers. |
| `0x5050` | `smallFont` | `fontInfo_t` | Small-font variant used by the text paint helpers when `scale <= ui_smallFont`. |
| `0xA094` | `bigFont` | `fontInfo_t` | Large-font variant used by the text paint helpers when `scale >= ui_bigFont`. |
| `0xF0D8` | `cursor` | `qhandle_t` | Active cursor shader used by `UI_Refresh` when drawing the visible menu cursor. |
| `0xF0DC` | `gradientBar` | `qhandle_t` | Gradient-bar shader used by `GradientBar_Paint`. |
| `0xF0E0` | `scrollBarArrowUp` | `qhandle_t` | Up-arrow shader for vertical listbox scrollbars. |
| `0xF0E4` | `scrollBarArrowDown` | `qhandle_t` | Down-arrow shader for vertical listbox scrollbars. |
| `0xF0E8` | `scrollBarArrowLeft` | `qhandle_t` | Left-arrow shader for horizontal listbox scrollbars. |
| `0xF0EC` | `scrollBarArrowRight` | `qhandle_t` | Right-arrow shader for horizontal listbox scrollbars. |
| `0xF0F0` | `scrollBar` | `qhandle_t` | Scrollbar track shader used by listbox paint paths. |
| `0xF0F4` | `scrollBarThumb` | `qhandle_t` | Scrollbar thumb shader used by listbox paint paths. |
| `0xF0F8` | `buttonMiddle` | `qhandle_t` | Legacy button-frame shader slot. Structurally present, but no active current-tree producer or consumer was found. |
| `0xF0FC` | `buttonInside` | `qhandle_t` | Legacy button-fill shader slot. Structurally present, but no active current-tree producer or consumer was found. |
| `0xF100` | `solidBox` | `qhandle_t` | Legacy filled-box shader slot. Structurally present, but no active current-tree producer or consumer was found. |
| `0xF104` | `sliderBar` | `qhandle_t` | Slider track shader used by `Item_Slider_Paint`. |
| `0xF108` | `sliderThumb` | `qhandle_t` | Slider thumb shader used by `Item_Slider_Paint`. |
| `0xF10C` | `menuEnterSound` | `sfxHandle_t` | Parser-visible menu-enter sound handle. Both the current asset-global parser and the committed retail token set still recognize it, but no stable active runtime consumer was found. |
| `0xF110` | `menuExitSound` | `sfxHandle_t` | Parser-visible menu-exit sound handle. Both the current asset-global parser and the committed retail token set still recognize it, but no stable active runtime consumer was found. |
| `0xF114` | `menuBuzzSound` | `sfxHandle_t` | Parser-visible menu-buzz sound handle. Both the current asset-global parser and the committed retail token set still recognize it, but no stable active runtime consumer was found. |
| `0xF118` | `itemFocusSound` | `sfxHandle_t` | Default focus sound used by `Item_SetFocus` when an item does not supply its own `focusSound`. |
| `0xF11C` | `fadeClamp` | `float` | Shared menu fade alpha clamp copied into menus during post-parse setup and used by fade helpers. |
| `0xF120` | `fadeCycle` | `int` | Shared fade timing period copied into menus during post-parse setup. |
| `0xF124` | `fadeAmount` | `float` | Shared fade delta copied into menus during post-parse setup. |
| `0xF128` | `shadowX` | `float` | X offset for shadowed text paint. |
| `0xF12C` | `shadowY` | `float` | Y offset for shadowed text paint. |
| `0xF130` | `shadowColor` | `vec4_t` | Shared shadow color used by text paint and fade logic. |
| `0xF140` | `shadowFadeClamp` | `float` | Cached alpha component of `shadowColor`, set when parsing `shadowColor`. |
| `0xF144` | `fontRegistered` | `qboolean` | Guard that prevents re-registering the three core fonts once the cache is seeded. |
| `0xF148` | `fxBasePic` | `qhandle_t` | Effects-color strip base shader used by the cosmetics/effects selector. |
| `0xF14C` | `fxPic[7]` | `qhandle_t[7]` | Effects-color indicator shaders for the seven supported color choices. |
| `0xF168` | `crosshairShader[NUM_CROSSHAIRS]` | `qhandle_t[10]` | Crosshair preview bank used by the crosshair ownerdraw. |

## `displayContextDef_t`

Current x86 size: `0x11ECC`

This is the shared UI backend context. `UI_Init` populates the callback table,
scaling state, copied `glconfig`, and a few tail shaders; `Init_Display`
publishes the address through the global `DC` pointer consumed by the shared
menu runtime.

### Render And Model Hooks

| Offset | Member | Type | Role |
| --- | --- | --- | --- |
| `0x0000` | `registerShaderNoMip` | `qhandle_t (*)(const char *)` | Shader registration hook used by menu/item asset loaders. |
| `0x0004` | `setColor` | `void (*)(const vec4_t)` | Color-state hook used by the shared paint helpers. |
| `0x0008` | `drawHandlePic` | `void (*)(float,float,float,float,qhandle_t)` | Primary textured-quad draw hook used throughout the menu painter. |
| `0x000C` | `drawStretchPic` | `void (*)(float,float,float,float,float,float,float,float,qhandle_t)` | Raw stretch-pic hook used by low-level draw helpers. |
| `0x0010` | `drawText` | `void (*)(float,float,float,vec4_t,const char *,float,int,int)` | Text paint hook used by the shared text/item/menu code. |
| `0x0014` | `textWidth` | `int (*)(const char *,float,int)` | Text-width query used by layout and ownerdraw sizing. |
| `0x0018` | `textHeight` | `int (*)(const char *,float,int)` | Text-height query used by layout and ownerdraw sizing. |
| `0x001C` | `registerModel` | `qhandle_t (*)(const char *)` | Model registration hook used by scripted model items. |
| `0x0020` | `modelBounds` | `void (*)(qhandle_t, vec3_t, vec3_t)` | Model-bounds query used by model-item framing. |
| `0x0024` | `fillRect` | `void (*)(float,float,float,float,const vec4_t)` | Filled-rect helper used by menu/item backgrounds and selections. |
| `0x0028` | `drawRect` | `void (*)(float,float,float,float,float,const vec4_t)` | Generic border-rect helper used by windows and debug outlines. |
| `0x002C` | `drawSides` | `void (*)(float,float,float,float,float)` | Border-side helper used by framed windows. |
| `0x0030` | `drawTopBottom` | `void (*)(float,float,float,float,float)` | Border top/bottom helper used by framed windows. |
| `0x0034` | `clearScene` | `void (*)(void)` | Scene reset hook for model/cinematic-backed item painting. |
| `0x0038` | `addRefEntityToScene` | `void (*)(const refEntity_t *)` | Model-item scene submission hook. |
| `0x003C` | `renderScene` | `void (*)(const refdef_t *)` | Model-item scene render hook. |
| `0x0040` | `registerFont` | `void (*)(const char *, int, fontInfo_t *)` | Font registration hook used by the asset cache and asset-global parser. |
| `0x0044` | `ownerDrawItem` | `void (*)(float,float,float,float,float,float,int,int,int,float,float,vec4_t,qhandle_t,int)` | Owning UI-side ownerdraw dispatcher used by item paint paths. |

### Script, Cvar, Feeder, And Bind Hooks

| Offset | Member | Type | Role |
| --- | --- | --- | --- |
| `0x0048` | `getValue` | `float (*)(int)` | Numeric ownerdraw query hook installed by `_UI_Init`. The committed retail callback body is a pure hardcoded `0.0` return, so ownerdraw color-range selection in `Item_Paint` only ever evaluates against zero unless another layer replaces the slot. |
| `0x004C` | `ownerDrawVisible` | `qboolean (*)(int)` | Visibility predicate for ownerdraw-backed widgets. |
| `0x0050` | `runScript` | `void (*)(char **)` | Menu script dispatcher used by item/menu events. |
| `0x0054` | `getTeamColor` | `void (*)(vec4_t *)` | Team-color callback installed by `_UI_Init`. Shared `WINDOW_STYLE_TEAMCOLOR` paint and `Script_SetTeamColor` still call through it, but the committed retail body is a pure no-op that does not populate the color buffer. |
| `0x0058` | `getCVarString` | `void (*)(const char *, char *, int)` | Cvar-string query hook used by parser/runtime bindings. |
| `0x005C` | `getCVarValue` | `float (*)(const char *)` | Numeric cvar query hook used by ownerdraws and edit/list widgets. |
| `0x0060` | `setCVar` | `void (*)(const char *, const char *)` | Cvar write hook used by menu scripts and widget commit paths. |
| `0x0064` | `drawTextWithCursor` | `void (*)(float,float,float,vec4_t,const char *,int,char,int,int)` | Text-entry draw hook used by edit fields. |
| `0x0068` | `setOverstrikeMode` | `void (*)(qboolean)` | Overstrike-state setter used by text-entry controls. |
| `0x006C` | `getOverstrikeMode` | `qboolean (*)(void)` | Overstrike-state query used by text-entry controls. |
| `0x0070` | `startLocalSound` | `void (*)(sfxHandle_t, int)` | Local UI sound playback hook used by focus and script sounds. |
| `0x0074` | `ownerDrawHandleKey` | `qboolean (*)(int,int,float *,int)` | Key-handler hook for ownerdraw-backed widgets. |
| `0x0078` | `feederCount` | `int (*)(float)` | List-feeder count query used by listboxes and scripted menus. |
| `0x007C` | `feederItemText` | `const char *(*)(float,int,int,qhandle_t *)` | List-feeder text query used by listbox row paint. |
| `0x0080` | `feederItemImage` | `qhandle_t (*)(float,int)` | List-feeder image query used by listbox row paint. |
| `0x0084` | `feederSelection` | `void (*)(float,int)` | List-feeder selection callback used by listbox interaction and menu activation. |
| `0x0088` | `keynumToStringBuf` | `void (*)(int, char *, int)` | Key-name formatter used by controls/binding menus. |
| `0x008C` | `getBindingBuf` | `void (*)(int, char *, int)` | Binding lookup hook used by controls menus. |
| `0x0090` | `setBinding` | `void (*)(int, const char *)` | Binding write hook used by controls menus. |
| `0x0094` | `executeText` | `void (*)(int, const char *)` | Console-command execution hook used by scripts and control paths. |
| `0x0098` | `Error` | `void (*)(int, const char *, ...)` | Fatal/error reporting hook used by parser/runtime error paths. |
| `0x009C` | `Print` | `void (*)(const char *, ...)` | Console/log print hook used by parser/runtime debug output. |
| `0x00A0` | `Pause` | `void (*)(qboolean)` | Pause-state hook used when menus manipulate the frontend pause latch. |
| `0x00A4` | `ownerDrawWidth` | `int (*)(int,float)` | Width query hook for ownerdraw-backed text/layout decisions. |

### Audio And Cinematic Hooks

| Offset | Member | Type | Role |
| --- | --- | --- | --- |
| `0x00A8` | `registerSound` | `sfxHandle_t (*)(const char *, qboolean)` | Sound registration hook used by parser/runtime sound setup. |
| `0x00AC` | `startBackgroundTrack` | `void (*)(const char *, const char *)` | Background music start hook used by menu open/activation paths. |
| `0x00B0` | `stopBackgroundTrack` | `void (*)(void)` | Background music stop hook used by menu scripts. |
| `0x00B4` | `playCinematic` | `int (*)(const char *, float, float, float, float)` | Classic cinematic-start hook used by window-backed cinematics. |
| `0x00B8` | `playLauncherCinematic` | `qhandle_t (*)(const char *, qboolean, int, int)` | Quake Live-era launcher-video hook. `Script_PlayLauncher` uses it to turn a browser/launcher video into a shader-backed item background. |
| `0x00BC` | `stopCinematic` | `void (*)(int)` | Cinematic stop hook used by menu/window cleanup. |
| `0x00C0` | `drawCinematic` | `void (*)(int, float, float, float, float)` | Cinematic draw hook used by window-backed cinematics. |
| `0x00C4` | `runCinematicFrame` | `void (*)(int)` | Per-frame cinematic advance hook used by cinematic windows. |

### Runtime State And Embedded Payloads

| Offset | Member | Type | Role |
| --- | --- | --- | --- |
| `0x00C8` | `yscale` | `float` | Virtual-480 to physical-screen Y scale computed in `UI_Init`. |
| `0x00CC` | `xscale` | `float` | Virtual-640 to physical-screen X scale computed in `UI_Init`. |
| `0x00D0` | `bias` | `float` | Widescreen horizontal bias computed in `UI_Init` and used by widescreen rect correction. |
| `0x00D4` | `realTime` | `int` | Current UI real time. Updated each refresh/console-command pass and used by fades, blink logic, and timers. |
| `0x00D8` | `frameTime` | `int` | Delta from the previous `realTime`, used by refresh logic and FPS tracking. |
| `0x00DC` | `cursorx` | `int` | Current virtual-screen cursor X position used by menu hit-testing and cursor draw. |
| `0x00E0` | `cursory` | `int` | Current virtual-screen cursor Y position used by menu hit-testing and cursor draw. |
| `0x00E4` | `debug` | `qboolean` | Legacy debug latch. Structurally present, but the current tree exposes only a weak `#ifndef NDEBUG` check and no stable writer. |
| `0x00E8` | `Assets` | `cachedAssets_t` | Embedded asset bank holding fonts, shared shaders, sound handles, fade tuning, and Quake Live-specific cosmetics/crosshair assets. |
| `0xF278` | `glconfig` | `glconfig_t` | Cached renderer configuration copied in `UI_Init` and used by widescreen scaling and the GL-info ownerdraw. |
| `0x11EBC` | `whiteShader` | `qhandle_t` | Shared white shader used by primitive border/fill helpers. |
| `0x11EC0` | `gradientImage` | `qhandle_t` | Legacy gradient shader slot. The live gradient style path paints through `Assets.gradientBar`, and no active producer or consumer was found for this tail slot in the current tree or the committed retail token set. |
| `0x11EC4` | `cursor` | `qhandle_t` | Legacy top-level cursor shader slot assigned during `_UI_Init` from `"menu/art/3_cursor2"`. The live visible cursor draw path uses `Assets.cursor`, and no separate committed retail draw consumer for this tail slot has been revalidated yet. |
| `0x11EC8` | `FPS` | `float` | Rolling UI FPS estimate updated by `UI_Refresh`; shown by the shared debug overlay when `debugMode` is enabled. |

## Current Ownership Split

- `_UI_Init` / `UI_Init` owns the callback table, scaling fields, copied
  `glconfig`, `whiteShader`, the legacy tail `cursor`, and the initial
  registration path for the shared frontend assets.
- `Init_Display` and `Display_GetContext` publish the active
  `displayContextDef_t *` through the shared `DC` global consumed by the menu
  runtime.
- The asset-global parser in `ui_main.c` owns the configurable
  `cachedAssets_t` fields such as fonts, cursor shader, sounds, fade values,
  and shadow parameters.
- The same parser-visible asset band now splits more cleanly:
  - live fields: `Assets.cursor`, `Assets.gradientBar`, and `Assets.itemFocusSound`
  - parser-visible but currently unconsumed fields: `menuEnterSound`,
    `menuExitSound`, `menuBuzzSound`
  - retained carry-over slots with no active producer/consumer in current
    evidence: `fontStr`, `gradientStr`, `buttonMiddle`, `buttonInside`,
    `solidBox`, `gradientImage`, and the tail `cursor` as a live draw input
- `AssetCache` owns the fixed Quake Live-compatible shared textures and fonts:
  gradient bar, scrollbar assets, slider assets, effects-color strip assets,
  and the crosshair preview bank.

## Open Questions

1. The remaining weak asset band is smaller now:
   `buttonMiddle`, `buttonInside`, and `solidBox` still have no active
   producer/consumer in the current tree or committed retail evidence, while
   `gradientImage` and the tail `cursor` are currently only init/layout-visible
   rather than revalidated as live draw inputs.
2. `menuEnterSound`, `menuExitSound`, and `menuBuzzSound` are now clearly
   parser-visible in both the current tree and committed retail token set, but
   they still lack a stable active consumer. Revisit them if future retail
   runtime evidence surfaces a menu-open, menu-close, or buzz path that still
   uses the cached handles.
