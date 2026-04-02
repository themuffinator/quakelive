# UI Mapping Round 2026-04-01

This round does not add new `uix86.dll` function aliases. The committed `ui`
map already covers the full current committed function corpus at `444 / 444`
anchors, so the useful work here was to tighten the downstream `ui`
reverse-engineering notes to match that reality instead of leaving them stuck
at an older "mostly source-backed" classification.

## Sources Used

- `references/symbol-maps/ui.json`
- `references/analysis/quakelive_symbol_aliases.json`
- `references/reverse-engineering/ghidra/uix86/ui_ghidra_reference.h`
- `references/reverse-engineering/ghidra/uix86/functions.csv`
- `references/hlil/quakelive/uix86.all/uix86.dll_hlil.txt`
- `src/code/ui/ui_main.c`
- `src/code/ui/ui_shared.c`
- `src/code/ui/ui_local.h`

## Reclassified Areas

### Shared Window Runtime

The older `ui-window-struct-layouts.md` note still treated most of
`windowDef_t` ownership as source-backed because it predated the promoted
shared-window/runtime tranche. The current committed map already names the core
helpers around:

- `Fade`
- `Window_Paint`
- `Item_SetScreenCoords`
- `Menu_UpdatePosition`
- `Rect_ContainsPoint`
- `Menu_FindItemByName`
- `Menu_ShowItemByName`
- `Script_FadeIn`
- `Script_FadeOut`
- `Item_Paint`
- `Menu_Paint`

That is enough to treat the main paint, hit-test, focus/visibility, and fade
slab as directly retail-backed. The remaining uncertainty is now narrower:
exact helper boundaries inside the transition/orbit effect band
(`rectEffects`, `rectEffects2`, `offsetTime`, `nextTime`).

### Window Effect Field Ownership

The transition/orbit effect band also tightened in this pass with already
promoted retail helpers.

- `Menu_TransitionItemByName @ 0x100165E0` seeds `WINDOW_INTRANSITION`,
  `WINDOW_VISIBLE`, `offsetTime`, the source rect in `rectClient`, the
  destination rect in `rectEffects`, and the per-step X/Y/W/H deltas in
  `rectEffects2`.
- `Menu_OrbitItemByName @ 0x100168A0` seeds `WINDOW_ORBITING`,
  `WINDOW_VISIBLE`, `offsetTime`, the orbit center in `rectEffects.x/y`, and
  the starting position in `rectClient.x/y`.
- `Item_Paint @ 0x1001CED0` is the committed retail consumer that checks
  `nextTime`, rewrites it to `realTime + offsetTime`, advances orbit or
  transition motion from the seeded effect fields, and then refreshes screen
  coordinates before the normal paint dispatch.

That means the core ownership of `rectEffects`, `rectEffects2`, `offsetTime`,
and the transition/orbit use of `nextTime` no longer needs to sit in an
open-ended source-backed bucket; the remaining weak area in `windowDef_t` is
smaller and mostly limited to secondary carry-over paths like the retained
outline-related color band.

### Shared Menu Runtime

The menu-layout note had the same stale problem. The committed map already
promotes the core shared-menu slab around:

- `Menu_SetupKeywordHash`
- `Menu_Parse`
- `Menu_UpdatePosition`
- `Menu_ClearFocus`
- `Menu_SetFeederSelection`
- `Menus_ActivateByName`
- `Menus_CloseByName`
- `Menus_CloseAll`
- `Menu_SetPrevCursorItem`
- `Menu_SetNextCursorItem`
- `Menu_HandleMouseMove`
- `Menu_Paint`
- `Menu_PaintAll`
- `Menu_OverActiveItem`

That means `menuDef_t` is no longer accurately described as only
"source-backed". What still leans on the preserved source tree is the init-side
ownership around `Menu_PostParse` and a few default-value details such as the
retained `fontIndex` slot.

### Display Context Callback Slab

The display-context note also lagged behind the current map. The callback slab
installed by `_UI_Init` is now directly reinforced by promoted retail owners
including:

- `AssetCache`
- `Text_Width`
- `Text_Height`
- `Text_Paint`
- `Text_PaintWithCursor`
- `Text_Paint_Limit`
- `UI_OwnerDraw`
- `UI_OwnerDrawVisible`
- `UI_OwnerDrawHandleKey`
- `UI_FeederCount`
- `UI_FeederItemText`
- `UI_FeederItemImage`
- `UI_FeederSelection`
- `UI_Pause`
- `UI_ReadableSize`
- `UI_PrintTime`
- `Display_MouseMove`
- `Menu_PaintAll`

The real open question here is no longer "are the shared menu/runtime helpers
mapped?" They are. The remaining weak fields are the legacy asset carry-over
slots such as `fontStr`, `gradientStr`, `buttonMiddle`, `buttonInside`,
`solidBox`, `gradientImage`, and the tail `cursor`.

### Display-Context Carry-Over Split

The carry-over asset band also tightened in this pass with direct committed
retail callback evidence.

- `UI_GetValue @ 0x1000A980` is a pure hardcoded `0.0` callback in the
  committed HLIL, not a still-missing value-dispatch helper.
- `UI_GetTeamColor @ 0x1000D2F0` is a pure no-op callback in the committed
  HLIL, even though shared team-color paint and script paths still call the
  slot.
- `gradientbar`, `cursor`, and `itemFocusSound` remain parser-visible and
  live: the parser writes them directly into `Assets.gradientBar`,
  `Assets.cursor`, and `Assets.itemFocusSound`, and the shared runtime still
  consumes those fields.
- `menuEnterSound`, `menuExitSound`, and `menuBuzzSound` are also still
  parser-visible in both the current tree and committed retail token set, but
  no stable active consumer surfaced in the current evidence.
- `fontStr`, `gradientStr`, `buttonMiddle`, `buttonInside`, `solidBox`,
  `gradientImage`, and the tail `cursor` now read more cleanly as retained
  compatibility/carry-over slots than as active unresolved runtime owners.

### Catalog Struct Producers

The catalog note previously grouped most parser ownership into a weaker
source-backed bucket. That was too pessimistic for the character/gametype/map
side. The current committed map already promotes:

- `Character_Parse`
- `UI_ParseTeamInfo`
- `GameType_Parse`
- `MapList_Parse`
- `UI_ParseGameInfo`
- `UI_LoadArenasFromFile`
- `UI_LoadArenas`
- `UI_LoadBotsFromFile`
- `UI_LoadBots`
- `UI_DrawSelectedPlayer`

The genuinely weaker band is now narrower: team/alias loading outside the
character parser path plus the old single-player `tierInfo` producer side.

### Folded Parser/String Init Logic

The parser/string-allocation band also tightened in this pass, but mostly as a
negative-result classification rather than as a new alias promotion.

- `String_Alloc`, `String_Report`, and `PC_SourceError` are still bounded
  retail helpers.
- `String_Init` is not currently exposed as a separate committed retail
  function.
- Instead, the committed Ghidra decompile shows the exact `String_Init`
  behavior inlined inside `_UI_Init @ 0x1000FAB0` and again inside
  `UI_Load @ 0x10004FC0`: clear the string-hash table, reset the pool/menu
  state, call `UI_InitMemory`, call `Item_SetupKeywordHash`,
  `Menu_SetupKeywordHash`, and conditionally call `Controls_GetConfig`.
- `PC_SourceWarning` likewise does not currently appear as a bounded retail
  helper in the committed corpus. The parser-side diagnostic surface that *is*
  directly exposed is `PC_SourceError`, while warning-class messages found in
  the corpus currently route through generic `Com_Printf`-style paths instead
  of a preserved file/line `PC_SourceWarning` wrapper.

The practical result is that these two source functions should currently be
treated as source-side compatibility helpers, not as missing named retail
functions waiting to be promoted.

### Legacy CD-Key Script Band

The committed retail corpus still preserves a legacy CD-key behavior surface,
but it does not currently resolve into the old qmenu popup owners.

- `UI_HasUniqueCDKey @ 0x10003910` still exists as the native export-table
  replacement for the old `UI_HASUNIQUECDKEY` path.
- The retained `uiMenuCommand_t` enum still carries `UIMENU_NEED_CD` and
  `UIMENU_BAD_CD_KEY`.
- `UI_RunMenuScript @ 0x1000B0E0` contains direct `getCDKey` and `verifyCDKey`
  branches that read and write the `cdkey1..4`, `cdkey`, `cdkeychecksum`, and
  `ui_cdkeyvalid` cvars.
- The committed `UI_RunMenuScript` branch chain then advances directly to the
  `loadArenas` token; the current source-side `openCredentials` ->
  `UI_CDKeyMenu` path does not presently appear as a separately bounded retail
  branch in the committed corpus.
- `_UI_SetActiveMenu @ 0x100100D0` still preserves the outer native UIMENU
  dispatcher, but the committed HLIL jump table only reaches menu activation
  paths for `main`, `error_popmenu`, `ingame`, `ingame_about`, and
  `joingame_menu`.
- In that same jump table, case `5` (`UIMENU_TEAM`) lands on `joingame_menu`
  rather than the older source-side `"team"` activation path.
- The retained `UIMENU_NEED_CD` and `UIMENU_BAD_CD_KEY` enum values therefore
  survive more as interface carry-over than as evidence for a still-bounded
  popup owner, and the source-side `UIMENU_POSTGAME` path likewise does not
  currently surface as a separate committed retail branch.
- Broad committed-corpus searches still do not surface bounded retail
  `UI_CDKeyMenu`, `UI_PushMenu`, `UI_PopMenu`, `Menu_AddItem`, or `Menu_Draw`
  helpers.

That means the best current retail reading is not "the old CD-key popup is
still there but unnamed." It is narrower: the bounded corpus still exposes the
CD-key validation/state path, but not a recoverable standalone qmenu popup
stack for it.

## What Still Is Not Mapped

This round intentionally did not fabricate names for the old GPL qmenu widget
core. The committed retail `uix86.dll` corpus still does not expose stable
one-to-one helpers like:

- `Menu_AddItem`
- `Menu_Draw`
- `Menu_DefaultKey`
- `MField_Draw`
- `ScrollList_Key`

The outer stack owners are better now: `_UI_KeyEvent`, `_UI_MouseEvent`, and
`_UI_SetActiveMenu` are already promoted, and `UI_RunMenuScript` now gives a
bounded retail CD-key script/cvar band. What remains missing is the inner
legacy qmenu widget-core family, so the qmenu struct note still stays
conservative.

## Result

This round raises the effective quality of the `ui` mapping notes without
inventing new aliases. The direct-retail-backed portion of the documented
`ui_shared` runtime is now reflected accurately in the struct-layout notes, and
the remaining open questions are narrowed to the genuinely weak areas:

- transition/orbit helper boundaries inside `windowDef_t`
- `Menu_PostParse` and related init-only menu details
- dormant-versus-live legacy asset carry-over fields in `displayContextDef_t`
- the folded-versus-standalone status of source-only helpers such as
  `String_Init` and `PC_SourceWarning`
- the inner qmenu widget-core helper family
