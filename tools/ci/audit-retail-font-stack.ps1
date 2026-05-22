[CmdletBinding()]
param(
	[string]$RepoRoot = (Resolve-Path (Join-Path $PSScriptRoot '../..')).Path,
	[switch]$Strict
)

$ErrorActionPreference = 'Stop'

function Assert-FileContains {
	param(
		[string]$RelativePath,
		[string]$Pattern,
		[string]$Description
	)

	$path = Join-Path $RepoRoot $RelativePath
	if (-not (Test-Path $path)) {
		throw "Required file was not found: $RelativePath"
	}

	$match = Select-String -Path $path -Pattern $Pattern -Quiet
	if (-not $match) {
		throw "Missing $Description in $RelativePath"
	}

	Write-Host "Verified $Description in $RelativePath"
}

function Report-UnresolvedGap {
	param(
		[string]$Message
	)

	if ($Strict) {
		throw $Message
	}

	Write-Warning $Message
}

function Read-JsonFile {
	param(
		[string]$RelativePath
	)

	$path = Join-Path $RepoRoot $RelativePath
	if (-not (Test-Path $path)) {
		throw "Required file was not found: $RelativePath"
	}

	return Get-Content -Path $path -Raw | ConvertFrom-Json
}

function Get-RegexIndex {
	param(
		[string]$Text,
		[string]$Pattern
	)

	$match = [regex]::Match( $Text, $Pattern )
	if ( -not $match.Success ) {
		return -1
	}

	return $match.Index
}

Assert-FileContains -RelativePath 'src/code/renderer/tr_font.c' -Pattern 'R_BuildFontCacheName' -Description 'retail face-specific font cache helper'
Assert-FileContains -RelativePath 'src/code/renderer/tr_font.c' -Pattern 'R_BuildFontCacheStem' -Description 'retail cache-stem helper'
Assert-FileContains -RelativePath 'src/code/renderer/tr_font.c' -Pattern 'R_BuildFontPageName' -Description 'retail face-specific font page helper'
Assert-FileContains -RelativePath 'src/code/renderer/tr_font.c' -Pattern 'R_FindCachedFontDataName' -Description 'retail-first cached font probe helper'
Assert-FileContains -RelativePath 'src/code/renderer/tr_font.c' -Pattern 'R_RegisterCachedFontShaders' -Description 'inclusive cached-font shader rebind helper'
Assert-FileContains -RelativePath 'src/code/renderer/tr_font.c' -Pattern 'R_FlushFontAtlasPage' -Description 'classic font atlas flush helper'
Assert-FileContains -RelativePath 'src/code/renderer/tr_font.c' -Pattern 'R_ReadAbsoluteFontFile' -Description 'absolute font-file loader'
Assert-FileContains -RelativePath 'src/code/renderer/tr_font.c' -Pattern 'fonts/handelgothic\.ttf' -Description 'retail default font mapping'
Assert-FileContains -RelativePath 'src/code/renderer/tr_font.c' -Pattern 'fonts/notosans-regular\.ttf' -Description 'retail sans font mapping'
Assert-FileContains -RelativePath 'src/code/renderer/tr_font.c' -Pattern 'fonts/droidsansmono\.ttf' -Description 'retail mono font mapping'
Assert-FileContains -RelativePath 'src/code/renderer/tr_font.c' -Pattern 'fonts/droidsansfallbackfull\.ttf' -Description 'retail fallback font mapping'
Assert-FileContains -RelativePath 'src/code/renderer/tr_font.c' -Pattern '#include <ft2build\.h>' -Description 'repo-managed FreeType header root'
Assert-FileContains -RelativePath 'src/code/renderer/tr_font.c' -Pattern '#include FT_FREETYPE_H' -Description 'repo-managed FreeType face header macro'
Assert-FileContains -RelativePath 'docs/reverse-engineering/renderer-font-cache-and-atlas-ownership-2026-04-10.md' -Pattern 'RG-G05 is now considered closed' -Description 'RG-P7 ownership closure note'
Assert-FileContains -RelativePath 'src/code/renderer/tr_font.c' -Pattern '\*fontstash' -Description 'renderer-owned fontstash texture name'
Assert-FileContains -RelativePath 'src/code/renderer/tr_font.c' -Pattern 'R_fonsErrorCallback' -Description 'retail fontstash error callback'
Assert-FileContains -RelativePath 'src/code/renderer/tr_font.c' -Pattern 'Expand font atlas to %dx%d' -Description 'retail fontstash atlas expansion log'
Assert-FileContains -RelativePath 'src/code/renderer/tr_font.c' -Pattern 'Max font atlas size, flushing' -Description 'retail fontstash atlas flush log'
Assert-FileContains -RelativePath 'src/code/renderer/tr_font.c' -Pattern 'void R_InitFontStash\( void \)' -Description 'renderer fontstash init entry point'
Assert-FileContains -RelativePath 'src/code/renderer/tr_font.c' -Pattern 'void R_DoneFontStash\( void \)' -Description 'renderer fontstash shutdown entry point'
Assert-FileContains -RelativePath 'src/code/renderer/tr_font.c' -Pattern 'void RE_DrawScaledText\( int x, int y, const char \*text, int fontHandle, float scale, int maxX, float \*outMaxX, qboolean forceColor, const float \*baseColor \)' -Description 'shared renderer host text draw helper'
Assert-FileContains -RelativePath 'src/code/renderer/tr_font.c' -Pattern 'void RE_MeasureScaledText\( const char \*text, const char \*end, int fontHandle, float scale, int maxX, float \*outWidth, float \*outHeight, float \*outLeft \)' -Description 'shared renderer host text measure helper'
Assert-FileContains -RelativePath 'src/code/renderer/tr_font.c' -Pattern 'qboolean RE_GetScaledFontMetrics\( int fontHandle, float scale, float \*outAscent, float \*outDescent, float \*outLineHeight \)' -Description 'shared renderer host text metrics helper'
Assert-FileContains -RelativePath 'src/code/renderer/tr_font.c' -Pattern 'R_DecodeFontStashCodepoint' -Description 'retail UTF-8 host-text decode helper'
Assert-FileContains -RelativePath 'src/code/renderer/tr_font.c' -Pattern 'R_ParseHostTextColorEscape' -Description 'retail host color-escape helper'
Assert-FileContains -RelativePath 'src/code/renderer/tr_font.c' -Pattern 'R_BuildFontStashFaceChain' -Description 'retail retained fallback-face chain helper'
Assert-FileContains -RelativePath 'src/code/renderer/tr_font.c' -Pattern 'R_GetFontStashScaleTenths' -Description 'retail size-tenths host glyph key helper'
Assert-FileContains -RelativePath 'src/code/renderer/tr_font.c' -Pattern 'sans-windows-fallback' -Description 'renderer Windows fallback face slot'
Assert-FileContains -RelativePath 'src/code/renderer/tr_font.c' -Pattern 'Retail host DrawScaledText/MeasureText resolve glyphs from the retained' -Description 'retail retained-atlas glyph-priority note'
Assert-FileContains -RelativePath 'src/code/ui/ui_shared.h' -Pattern '#define QL_FONT_NAME_TEXT "fonts/font"' -Description 'UI retail text-font bucket name'
Assert-FileContains -RelativePath 'src/code/ui/ui_shared.h' -Pattern '#define QL_FONT_NAME_SMALL "fonts/smallfont"' -Description 'UI retail small-font bucket name'
Assert-FileContains -RelativePath 'src/code/ui/ui_shared.h' -Pattern '#define QL_FONT_NAME_BIG "fonts/bigfont"' -Description 'UI retail big-font bucket name'
Assert-FileContains -RelativePath 'src/code/ui/ui_shared.h' -Pattern '#define QL_FONT_NAME_MONO "fonts/monofont"' -Description 'UI retail mono-font bucket name'
Assert-FileContains -RelativePath 'src/code/ui/ui_shared.h' -Pattern '#define QL_FONT_TEXT_POINT_SIZE 24' -Description 'UI retail text-font point size'
Assert-FileContains -RelativePath 'src/code/ui/ui_shared.h' -Pattern '#define QL_FONT_SMALL_POINT_SIZE 16' -Description 'UI retail small-font point size'
Assert-FileContains -RelativePath 'src/code/ui/ui_shared.h' -Pattern '#define QL_FONT_BIG_POINT_SIZE 48' -Description 'UI retail big-font point size'
Assert-FileContains -RelativePath 'src/code/ui/ui_shared.h' -Pattern '#define QL_FONT_MONO_POINT_SIZE 16' -Description 'UI retail mono-font point size'
Assert-FileContains -RelativePath 'src/code/ui/ui_main.c' -Pattern '\{ &ui_smallFont, "ui_smallFont", "0\.25", CVAR_ARCHIVE\}' -Description 'UI small-font cvar default and flags'
Assert-FileContains -RelativePath 'src/code/ui/ui_main.c' -Pattern '\{ &ui_bigFont, "ui_bigFont", "0\.4", CVAR_ARCHIVE\}' -Description 'UI big-font cvar default and flags'
Assert-FileContains -RelativePath 'src/code/cgame/cg_main.c' -Pattern '\{ &cg_smallFont, "ui_smallFont", "0\.25", CVAR_ARCHIVE\}' -Description 'cgame small-font cvar default and flags'
Assert-FileContains -RelativePath 'src/code/cgame/cg_main.c' -Pattern '\{ &cg_bigFont, "ui_bigFont", "0\.4", CVAR_ARCHIVE\}' -Description 'cgame big-font cvar default and flags'
Assert-FileContains -RelativePath 'src/code/renderer/tr_init.c' -Pattern 'r_debugFontAtlas = ri\.Cvar_Get\( "r_debugFontAtlas", "0", CVAR_TEMP \);' -Description 'renderer debug font-atlas cvar default and flags'
Assert-FileContains -RelativePath 'src/code/renderer/tr_init.c' -Pattern 'r_saveFontData = ri\.Cvar_Get\( "r_saveFontData", "0", 0 \);' -Description 'renderer font-data save cvar default and flags'
Assert-FileContains -RelativePath 'src/code/ui/ui_shared.c' -Pattern 'void UI_NormalizeFontPath' -Description 'UI font normalization helper'
Assert-FileContains -RelativePath 'src/code/ui/ui_shared.c' -Pattern 'menu->font = String_Alloc\( fontPath \);' -Description 'UI resolved menu font token storage'
Assert-FileContains -RelativePath 'docs/reverse-engineering/ui-display-context-struct-layouts.md' -Pattern 'Seeded by the asset-global `font` directive or the retail `MenuParse_font` registration path' -Description 'UI display-context doc for parser-owned primary font registration'
Assert-FileContains -RelativePath 'docs/reverse-engineering/ui-display-context-struct-layouts.md' -Pattern 'Font registration hook used by the asset-global parser and the retail menu-font normalization/bootstrap path' -Description 'UI display-context doc for parser-owned font hook'
Assert-FileContains -RelativePath 'docs/reverse-engineering/ui-display-context-struct-layouts.md' -Pattern 'AssetCache` now owns the fixed Quake Live-compatible shared textures only' -Description 'UI display-context doc for art-only AssetCache ownership'
Assert-FileContains -RelativePath 'src/code/ui/ui_quakelive_bridge.c' -Pattern 'font \\"fonts/font\\" 16' -Description 'bridge main-menu text-font size override'
Assert-FileContains -RelativePath 'src/code/ui/ui_quakelive_bridge.c' -Pattern 'smallFont \\"fonts/smallfont\\" 12' -Description 'bridge main-menu small-font size override'
Assert-FileContains -RelativePath 'src/code/ui/ui_quakelive_bridge.c' -Pattern 'bigFont \\"fonts/bigfont\\" 20' -Description 'bridge main-menu big-font size override'
Assert-FileContains -RelativePath 'src/ui/main.menu' -Pattern 'font\s+"fonts/font"\s+16' -Description 'main menu text-font size override'
Assert-FileContains -RelativePath 'src/ui/main.menu' -Pattern 'smallFont\s+"fonts/smallfont"\s+12' -Description 'main menu small-font size override'
Assert-FileContains -RelativePath 'src/ui/main.menu' -Pattern 'bigFont\s+"fonts/bigfont"\s+20' -Description 'main menu big-font size override'
Assert-FileContains -RelativePath 'src/ui/hud.menu' -Pattern 'font\s+"fonts/font"\s+24' -Description 'HUD text-font size'
Assert-FileContains -RelativePath 'src/ui/hud.menu' -Pattern 'smallFont\s+"fonts/smallfont"\s+16' -Description 'HUD small-font size'
Assert-FileContains -RelativePath 'src/ui/hud.menu' -Pattern 'bigFont\s+"fonts/bigfont"\s+48' -Description 'HUD big-font size'
Assert-FileContains -RelativePath 'src/code/renderer/tr_init.c' -Pattern 'R_InitFontStash\(\)' -Description 'renderer startup fontstash wiring'
Assert-FileContains -RelativePath 'src/code/renderer/tr_init.c' -Pattern 'R_DoneFontStash\(\)' -Description 'renderer shutdown fontstash wiring'
Assert-FileContains -RelativePath 'src/code/renderer/tr_public.h' -Pattern '#define\s+REF_API_VERSION\s+9' -Description 'retail renderer API version'
Assert-FileContains -RelativePath 'src/code/renderer/tr_init.c' -Pattern 're\.RegisterFont = R_NoopRegisterFont;' -Description 'retail no-op legacy refexport font slot'
Assert-FileContains -RelativePath 'src/code/renderer/tr_init.c' -Pattern 're\.PostProcessRestart = R_PostProcessRestart;' -Description 'retail private postprocess_restart refexport slot'
Assert-FileContains -RelativePath 'src/code/renderer/tr_init.c' -Pattern 're\.TransformClipToWindow = R_TransformClipToWindowExport;' -Description 'retail private clip-to-window refexport wrapper'
Assert-FileContains -RelativePath 'docs/reverse-engineering/renderer-host-text-core-ownership-2026-04-10.md' -Pattern 'RG-P8 is now considered complete' -Description 'RG-P8 ownership closure note'
Assert-FileContains -RelativePath 'src/code/client/cl_ui.c' -Pattern 'RE_DrawScaledText\( x, y, text, fontHandle, scale, maxX, outMaxX' -Description 'UI native host text draw switchover'
Assert-FileContains -RelativePath 'src/code/client/cl_ui.c' -Pattern 'RE_DrawScaledText\( x, y, text, fontHandle, scale, maxX, outMaxX, forceColor != qfalse \? qtrue : qfalse, ql_ui_currentColor \);' -Description 'UI native host text current-color and force-color bridge'
Assert-FileContains -RelativePath 'src/code/client/cl_ui.c' -Pattern 'RE_MeasureScaledText\( text, end, fontHandle, scale, maxX, &width, &height, outLeft \)' -Description 'UI native host text measure switchover'
Assert-FileContains -RelativePath 'src/code/client/cl_ui.c' -Pattern 'return QL_UI_PackFloatBits64\( width, height \);' -Description 'UI native host text packed measurement return'
Assert-FileContains -RelativePath 'src/code/client/cl_cgame.c' -Pattern 'RE_DrawScaledText\( x, y, text, fontHandle, scale, maxX, outMaxX' -Description 'cgame native host text draw switchover'
Assert-FileContains -RelativePath 'src/code/client/cl_cgame.c' -Pattern 'RE_DrawScaledText\( x, y, text, fontHandle, scale, maxX, outMaxX, forceColor != qfalse \? qtrue : qfalse, ql_cgame_currentColor \);' -Description 'cgame native host text current-color and force-color bridge'
Assert-FileContains -RelativePath 'src/code/client/cl_cgame.c' -Pattern 'RE_MeasureScaledText\( text, end, fontHandle, scale, maxX, &width, &height, outLeft \)' -Description 'cgame native host text measure switchover'
Assert-FileContains -RelativePath 'src/code/client/cl_cgame.c' -Pattern 'return QL_CG_PackFloatBits64\( width, height \);' -Description 'cgame native host text packed measurement return'
Assert-FileContains -RelativePath 'src/code/client/client.h' -Pattern 'qboolean RE_GetScaledFontMetrics\( int fontHandle, float scale, float \*outAscent, float \*outDescent, float \*outLineHeight \);' -Description 'client host text metrics prototype'
Assert-FileContains -RelativePath 'src/code/ui/ui_public.h' -Pattern 'UI_QL_IMPORT_R_REGISTERFONT = 70,' -Description 'UI native font registration import slot'
Assert-FileContains -RelativePath 'src/code/ui/ui_public.h' -Pattern 'UI_QL_IMPORT_DRAW_SCALED_TEXT = 94,' -Description 'UI native host text draw import slot'
Assert-FileContains -RelativePath 'src/code/ui/ui_public.h' -Pattern 'UI_QL_IMPORT_MEASURE_TEXT = 95,' -Description 'UI native host text measure import slot'
Assert-FileContains -RelativePath 'src/code/cgame/cg_public.h' -Pattern 'CG_QL_IMPORT_R_REGISTERFONT = 93,' -Description 'cgame native font registration import slot'
Assert-FileContains -RelativePath 'src/code/cgame/cg_public.h' -Pattern 'CG_QL_IMPORT_DRAW_SCALED_TEXT = 123,' -Description 'cgame native host text draw import slot'
Assert-FileContains -RelativePath 'src/code/cgame/cg_public.h' -Pattern 'CG_QL_IMPORT_MEASURE_TEXT = 124,' -Description 'cgame native host text measure import slot'
Assert-FileContains -RelativePath 'src/code/client/cl_ui.c' -Pattern 'ql_ui_imports\[UI_QL_IMPORT_R_REGISTERFONT\] = \(ql_import_f\)QL_UI_trap_R_RegisterFont;' -Description 'UI native font registration import assignment'
Assert-FileContains -RelativePath 'src/code/client/cl_ui.c' -Pattern 'ql_ui_imports\[UI_QL_IMPORT_DRAW_SCALED_TEXT\] = \(ql_import_f\)QL_UI_trap_DrawScaledText;' -Description 'UI native host text draw import assignment'
Assert-FileContains -RelativePath 'src/code/client/cl_ui.c' -Pattern 'ql_ui_imports\[UI_QL_IMPORT_MEASURE_TEXT\] = \(ql_import_f\)QL_UI_trap_MeasureText;' -Description 'UI native host text measure import assignment'
Assert-FileContains -RelativePath 'src/code/client/cl_cgame.c' -Pattern 'ql_cgame_imports\[CG_QL_IMPORT_R_REGISTERFONT\] = \(ql_import_f\)QL_CG_trap_R_RegisterFont;' -Description 'cgame native font registration import assignment'
Assert-FileContains -RelativePath 'src/code/client/cl_cgame.c' -Pattern 'ql_cgame_imports\[CG_QL_IMPORT_DRAW_SCALED_TEXT\] = \(ql_import_f\)QL_CG_trap_DrawScaledText;' -Description 'cgame native host text draw import assignment'
Assert-FileContains -RelativePath 'src/code/client/cl_cgame.c' -Pattern 'ql_cgame_imports\[CG_QL_IMPORT_MEASURE_TEXT\] = \(ql_import_f\)QL_CG_trap_MeasureText;' -Description 'cgame native host text measure import assignment'
Assert-FileContains -RelativePath 'src/code/client/ql_ui_imports.inc' -Pattern 'UI_Import_Syscall\( UI_R_REGISTERFONT, fontName, pointSize, font \);' -Description 'UI VM font registration compatibility syscall wrapper'
Assert-FileContains -RelativePath 'src/code/client/ql_cgame_imports.inc' -Pattern 'CG_Import_Syscall\(CG_R_REGISTERFONT, fontName, pointSize, font \);' -Description 'cgame VM font registration compatibility syscall wrapper'
Assert-FileContains -RelativePath 'src/code/client/cl_console.c' -Pattern '#define\s+CONSOLE_HOST_FONT_MONO\s+2' -Description 'console mono host-text font handle'
Assert-FileContains -RelativePath 'src/code/client/cl_console.c' -Pattern '#define\s+CONSOLE_HOST_SCALE_MULTIPLIER\s+2\.1597f' -Description 'console host-text scale multiplier'
Assert-FileContains -RelativePath 'src/code/client/cl_console.c' -Pattern 'RE_DrawScaledText\( x, baselineY, text, CONSOLE_HOST_FONT_MONO,' -Description 'console host text draw switchover'
Assert-FileContains -RelativePath 'src/code/client/cl_console.c' -Pattern 'RE_MeasureScaledText\( drawText, drawText \+ prefixBytes, CONSOLE_HOST_FONT_MONO,' -Description 'console host field cursor measurement'
Assert-FileContains -RelativePath 'src/code/cgame/cg_local.h' -Pattern 'static ID_INLINE void trap_QL_DrawScaledText\( int x, int y, const char \*text, int fontHandle, float scale, int maxX, float \*outMaxX, qboolean forceColor \)' -Description 'cgame Q3_VM host text draw stub'
Assert-FileContains -RelativePath 'src/code/cgame/cg_local.h' -Pattern 'static ID_INLINE unsigned long long trap_QL_MeasureText\( const char \*text, const char \*end, int fontHandle, float scale, int maxX, float \*outLeft \)' -Description 'cgame Q3_VM host text measure stub'
Assert-FileContains -RelativePath 'src/code/client/cl_scrn.c' -Pattern '#define\s+SCREEN_OVERLAY_HOST_FONT_MONO\s+2' -Description 'screen-overlay mono host-text font handle'
Assert-FileContains -RelativePath 'src/code/client/cl_scrn.c' -Pattern 'RE_DrawScaledText\( screenX, screenY, string, SCREEN_OVERLAY_HOST_FONT_MONO,' -Description 'screen-overlay host text switchover'
Assert-FileContains -RelativePath 'src/code/renderer/tr_world.c' -Pattern '#define\s+R_DEBUG_ADVERTISEMENT_TEXT_SCALE\s+\(\s*16\.0f / 48\.0f\s*\)' -Description 'renderer advertisement debug host-text scale'
Assert-FileContains -RelativePath 'src/code/renderer/tr_world.c' -Pattern 'RE_DrawScaledText\( R_DEBUG_ADVERTISEMENT_TEXT_X, y, text,' -Description 'renderer advertisement debug host text draw'
Assert-FileContains -RelativePath 'src/code/renderer/tr_backend.c' -Pattern 'RB_ShowFontAtlas' -Description 'renderer debug font atlas draw path'
Assert-FileContains -RelativePath 'src/code/renderer/renderer.vcxproj' -Pattern 'QLEnableFreeType' -Description 'renderer repo-managed FreeType build toggle'
Assert-FileContains -RelativePath 'src/code/renderer/renderer.vcxproj' -Pattern 'QLEnableFreeType Condition=.*>1</QLEnableFreeType>' -Description 'renderer FreeType defaults enabled for parity builds'
Assert-FileContains -RelativePath 'src/code/renderer/renderer.vcxproj' -Pattern 'ValidateFreeType' -Description 'renderer repo-managed FreeType validation target'
Assert-FileContains -RelativePath 'src/code/quakelive_steam.vcxproj' -Pattern 'QLEnableFreeType' -Description 'engine repo-managed FreeType link toggle'
Assert-FileContains -RelativePath 'src/code/quakelive_steam.vcxproj' -Pattern 'QLEnableFreeType Condition=.*>1</QLEnableFreeType>' -Description 'engine FreeType defaults enabled for parity builds'
Assert-FileContains -RelativePath 'src/code/quakelive_steam.vcxproj' -Pattern 'ValidateFreeType' -Description 'engine repo-managed FreeType validation target'
Assert-FileContains -RelativePath 'src/code/quakelive_steam.vcxproj' -Pattern '\$\(FreeTypeDependencies\);\$\(VorbisDependencies\);\$\(PngDependencies\);winmm\.lib;(wsock32|ws2_32)\.lib;Dbghelp\.lib' -Description 'engine config link lines retain FreeType dependencies'
Assert-FileContains -RelativePath '.vscode/build.ps1' -Pattern 'QLEnableFreeType' -Description 'Windows build-script FreeType toggle'
Assert-FileContains -RelativePath '.vscode/build.ps1' -Pattern "Invoke-InternalDependencyBootstrap -DependencyName 'freetype'" -Description 'Windows build-script FreeType bootstrap hook'
Assert-FileContains -RelativePath '.vscode/build.ps1' -Pattern 'build_internal_deps\.ps1' -Description 'Windows internal codec bootstrap hook'
Assert-FileContains -RelativePath 'src/code/quakelive.internal-deps.targets' -Pattern 'QLBootstrapFreeType' -Description 'MSBuild FreeType bootstrap target'
Assert-FileContains -RelativePath 'tools/build_internal_deps.ps1' -Pattern 'Ensure-FreeType' -Description 'repo-managed FreeType bootstrap implementation'
Assert-FileContains -RelativePath 'src/code/unix/Makefile' -Pattern 'QL_ENABLE_FREETYPE \?= 0' -Description 'Unix FreeType toggle'
Assert-FileContains -RelativePath 'src/code/unix/Makefile' -Pattern 'pkg-config --cflags freetype2' -Description 'Unix FreeType pkg-config include detection'
Assert-FileContains -RelativePath 'src/code/unix/Makefile' -Pattern 'CLIENT_FREETYPE_CFLAGS := \$\(FREETYPE_CFLAGS\) -DBUILD_FREETYPE' -Description 'Unix FreeType compile define wiring'
Assert-FileContains -RelativePath 'docs/reverse-engineering/renderer-freetype-build-lane-recovery-2026-04-10.md' -Pattern 'RG-P10 is now considered complete' -Description 'RG-P10 build-lane closure note'
Assert-FileContains -RelativePath 'docs/reverse-engineering/renderer-text-strict-validation-and-runtime-evidence-2026-04-10.md' -Pattern 'RG-P11 is now considered complete' -Description 'RG-P11 runtime closure note'

$sourceFiles = Get-ChildItem -Path (Join-Path $RepoRoot 'src/code') -Recurse -File -Include *.c,*.h
$fontstashMatches = $sourceFiles | Select-String -Pattern '\*fontstash|R_fonsErrorCallback|fons'
$debugAtlasPaths = $sourceFiles |
	Select-String -Pattern 'r_debugFontAtlas' |
	Select-Object -ExpandProperty Path -Unique
$expectedDebugAtlasPaths = @(
	(Join-Path $RepoRoot 'src/code/renderer/tr_init.c'),
	(Join-Path $RepoRoot 'src/code/renderer/tr_local.h')
)
$unexpectedDebugAtlasPaths = $debugAtlasPaths | Where-Object { $_ -notin $expectedDebugAtlasPaths }

if ($fontstashMatches.Count -gt 0) {
	Write-Host "Found fontstash-related source references: $($fontstashMatches.Count)"
}
else {
	Report-UnresolvedGap -Message 'Retail host fontstash source remains missing: no source file under src/code currently references "*fontstash", "R_fonsErrorCallback", or a similar fons implementation.'
}

$uiCompatShimPresent = Select-String -Path (Join-Path $RepoRoot 'src/code/client/cl_ui.c') -Pattern 'font = QL_UI_GetScaledFont\( fontHandle \);' -Quiet
$cgameCompatShimPresent = Select-String -Path (Join-Path $RepoRoot 'src/code/client/cl_cgame.c') -Pattern 'font = QL_CG_GetScaledFont\( fontHandle \);' -Quiet
$trFontSource = Get-Content -Path (Join-Path $RepoRoot 'src/code/renderer/tr_font.c') -Raw
$clConsoleSource = Get-Content -Path (Join-Path $RepoRoot 'src/code/client/cl_console.c') -Raw
$clScrnSource = Get-Content -Path (Join-Path $RepoRoot 'src/code/client/cl_scrn.c') -Raw
$uiMainSource = Get-Content -Path (Join-Path $RepoRoot 'src/code/ui/ui_main.c') -Raw
$uiSharedSource = Get-Content -Path (Join-Path $RepoRoot 'src/code/ui/ui_shared.c') -Raw
$cgDrawSource = Get-Content -Path (Join-Path $RepoRoot 'src/code/cgame/cg_draw.c') -Raw
$cgLocalSource = Get-Content -Path (Join-Path $RepoRoot 'src/code/cgame/cg_local.h') -Raw
$cgMainSource = Get-Content -Path (Join-Path $RepoRoot 'src/code/cgame/cg_main.c') -Raw
$cgNewdrawSource = Get-Content -Path (Join-Path $RepoRoot 'src/code/cgame/cg_newdraw.c') -Raw
$cgConsoleSource = Get-Content -Path (Join-Path $RepoRoot 'src/code/cgame/cg_consolecmds.c') -Raw
$uiSyscallsSource = Get-Content -Path (Join-Path $RepoRoot 'src/code/ui/ui_syscalls.c') -Raw
$cgSyscallsSource = Get-Content -Path (Join-Path $RepoRoot 'src/code/cgame/cg_syscalls.c') -Raw
$trPublicSource = Get-Content -Path (Join-Path $RepoRoot 'src/code/renderer/tr_public.h') -Raw
$trInitSource = Get-Content -Path (Join-Path $RepoRoot 'src/code/renderer/tr_init.c') -Raw
$trWorldSource = Get-Content -Path (Join-Path $RepoRoot 'src/code/renderer/tr_world.c') -Raw
$retainedAtlasPriority = $trFontSource.IndexOf('if ( r_fontStash.shader ) {')
$compatFontPriority = $trFontSource.IndexOf('codepoint <= GLYPH_END && R_EnsureFontStashCompatibilityFont( face )')
$rGetScaleTenthsStart = $trFontSource.IndexOf('static int R_GetFontStashScaleTenths( float scale ) {')
$rDecodeCodepointStart = $trFontSource.IndexOf('static const char *R_DecodeFontStashCodepoint( const char *text, const char *end, unsigned int *outCodepoint ) {')
$rParseColorEscapeStart = $trFontSource.IndexOf('static qboolean R_ParseHostTextColorEscape( const char *text, const char *end, int *outColorIndex, const char **outNext ) {')
$rAppendFaceChainStart = $trFontSource.IndexOf('static void R_AppendFontStashFaceChain( rFontStashFace_t **faces, int *faceCount, int maxFaces, rFontStashFace_t *face ) {')
$rGetFaceForHandleStart = $trFontSource.IndexOf('static rFontStashFace_t *R_GetFontStashFaceForHandle( int fontHandle ) {')
$rGetScaledFontMetricsStart = $trFontSource.IndexOf('qboolean RE_GetScaledFontMetrics( int fontHandle, float scale, float *outAscent, float *outDescent, float *outLineHeight ) {')
$reDrawScaledTextStart = $trFontSource.IndexOf('void RE_DrawScaledText( int x, int y, const char *text, int fontHandle, float scale, int maxX, float *outMaxX, qboolean forceColor, const float *baseColor ) {')
$reMeasureScaledTextStart = $trFontSource.IndexOf('void RE_MeasureScaledText( const char *text, const char *end, int fontHandle, float scale, int maxX, float *outWidth, float *outHeight, float *outLeft ) {')
$reRegisterFontFallbackStart = $trFontSource.IndexOf('static qboolean RE_RegisterFontFallback( const char *cacheName, float glyphScale, fontInfo_t *font ) {')
$uiAssetCacheStart = $uiMainSource.IndexOf('void AssetCache() {')
$uiAssetParseStart = $uiMainSource.IndexOf('qboolean Asset_Parse(int handle) {')
$uiAssetStopStart = $uiMainSource.IndexOf('void Font_Report() {')
$uiNormalizeFontStart = $uiSharedSource.IndexOf('void UI_NormalizeFontPath( const char **fontName, int *pointSize, const char *defaultFont, int defaultPointSize ) {')
$uiPcScriptParseStart = $uiSharedSource.IndexOf('qboolean PC_Script_Parse(int handle, const char **out) {')
$uiItemTextWidthStart = $uiSharedSource.IndexOf('static int Item_TextWidth(itemDef_t *item, const char *text, int limit) {')
$uiItemTextHeightStart = $uiSharedSource.IndexOf('static int Item_TextHeight(itemDef_t *item, const char *text, int limit) {')
$uiItemDrawTextStart = $uiSharedSource.IndexOf('static void Item_DrawText(itemDef_t *item, float x, float y, vec4_t color, const char *text, float adjust, int limit) {')
$uiItemDrawTextWithCursorStart = $uiSharedSource.IndexOf('static void Item_DrawTextWithCursor(itemDef_t *item, float x, float y, vec4_t color, const char *text, int cursorPos, char cursor, int limit) {')
$uiItemSetTextExtentsStart = $uiSharedSource.IndexOf('void Item_SetTextExtents(itemDef_t *item, int *width, int *height, const char *text) {')
$uiItemInitStart = $uiSharedSource.IndexOf('void Item_Init(itemDef_t *item) {')
$uiMenuHandleMouseMoveStart = $uiSharedSource.IndexOf('void Menu_HandleMouseMove(menuDef_t *menu, float x, float y) {')
$uiItemParseFontStart = $uiSharedSource.IndexOf('qboolean ItemParse_font( itemDef_t *item, int handle ) {')
$uiItemParseTextScaleStart = $uiSharedSource.IndexOf('qboolean ItemParse_textscale( itemDef_t *item, int handle ) {')
$uiMenuParseFontStart = $uiSharedSource.IndexOf('qboolean MenuParse_font( itemDef_t *item, int handle ) {')
$uiMenuParseNameStart = $uiSharedSource.IndexOf('qboolean MenuParse_name( itemDef_t *item, int handle ) {')
$uiMenuParseKeywordsStart = $uiSharedSource.IndexOf('keywordHash_t menuParseKeywords[] = {')
$uiMenuParseKeywordHashStart = $uiSharedSource.IndexOf('keywordHash_t *menuParseKeywordHash[KEYWORDHASH_SIZE];')
$cgRegisterFontsStart = $cgMainSource.IndexOf('static void CG_RegisterHudFonts( void ) {')
$cgLoadHudMenuStart = $cgMainSource.IndexOf('void CG_LoadHudMenu( void ) {')
$cgAssetCacheStart = $cgMainSource.IndexOf('void CG_AssetCache( void ) {')
$cgInitStart = $cgMainSource.IndexOf('void CG_Init( int serverMessageNum, int serverCommandSequence, int clientNum ) {')
$cgAssetParseStart = $cgMainSource.IndexOf('qboolean CG_Asset_Parse( int handle ) {')
$cgParseMenuStart = $cgMainSource.IndexOf('void CG_ParseMenu( const char *menuFile ) {')
$cgSetupBrowserMenuHashStart = $cgMainSource.IndexOf('void CG_SetupBrowserMenuKeywordHash( void ) {')
$cgParseBrowserMenuStart = $cgMainSource.IndexOf('qboolean CG_ParseBrowserMenu( int handle, void *menu ) {')
$cgInitBrowserRuntimeStart = $cgMainSource.IndexOf('void CG_InitBrowserRuntime( void ) {')
$cgResetBrowserOverlayStateStart = $cgMainSource.IndexOf('void CG_ResetBrowserOverlayState( void ) {')
$cgLoadHudCommandStart = $cgConsoleSource.IndexOf('static void CG_LoadHud_f( void ) {')
$cgLoadHudCommandStopStart = $cgConsoleSource.IndexOf('static void CG_scrollScoresDown_f( void) {')
$uiSelectFontStart = $uiMainSource.IndexOf('static fontInfo_t *UI_SelectTextFont(float scale, int fontIndex) {')
$uiSelectHandleStart = $uiMainSource.IndexOf('static int UI_SelectTextFontHandle( float scale, int fontIndex ) {')
$uiTextLimitStart = $uiMainSource.IndexOf('static const char *UI_GetTextLimitEnd')
$uiHostMetricsStart = $uiMainSource.IndexOf('static void UI_GetHostTextMetrics( const char *text, float scale, int limit, int fontIndex, int *outWidth, int *outHeight ) {')
$uiDrawHostTextSpanStart = $uiMainSource.IndexOf('static void UI_DrawHostTextSpan( float x, float y, float scale, const vec4_t color, const char *text, int fontIndex, int style, qboolean forceColor ) {')
$uiTextWidthExtStart = $uiMainSource.IndexOf('static int Text_WidthExt(const char *text, float scale, int limit, int fontIndex) {')
$uiTextPaintWithCursorExtStart = $uiMainSource.IndexOf('static void Text_PaintWithCursorExt(float x, float y, float scale, vec4_t color, const char *text, int cursorPos, char cursor, int limit, int style, int fontIndex) {')
$uiTextPaintWithCursorStart = $uiMainSource.IndexOf('void Text_PaintWithCursor(float x, float y, float scale, vec4_t color, const char *text, int cursorPos, char cursor, int limit, int style) {')
$uiPaintLimitStart = $uiMainSource.IndexOf('static void Text_Paint_Limit(float *maxX, float x, float y, float scale, vec4_t color, const char* text, float adjust, int limit) {')
$uiSyncMenuStateStart = $uiMainSource.IndexOf('static void UI_SyncMenuStateFromCvars( void ) {')
$cgSelectHandleStart = $cgDrawSource.IndexOf('int CG_SelectTextFontHandle( float scale, int fontIndex ) {')
$cgTextLimitStart = $cgDrawSource.IndexOf('static const char *CG_GetTextLimitEnd')
$cgHostMetricsStart = $cgDrawSource.IndexOf('static void CG_GetHostTextMetrics( const char *text, float scale, int limit, int fontIndex, int *outWidth, int *outHeight ) {')
$cgDrawHostTextSpanStart = $cgDrawSource.IndexOf('static void CG_DrawHostTextSpan( float x, float y, float scale, const vec4_t color, const char *text, int fontIndex, int style, qboolean forceColor ) {')
$cgTextWidthExtStart = $cgDrawSource.IndexOf('int CG_Text_WidthExt( const char *text, float scale, int limit, int fontIndex ) {')
$cgTextGetExtentsStart = $cgDrawSource.IndexOf('static void CG_Text_GetExtents( const char *text, float scale, int limit, int style, int *outWidth, int *outHeight ) {')
$cgTextPaintCharStart = $cgDrawSource.IndexOf('void CG_Text_PaintChar(float x, float y, float width, float height, float scale, float s, float t, float s2, float t2, qhandle_t hShader) {')
$cgDrawSnapshotStart = $cgDrawSource.IndexOf('static float CG_DrawSnapshot( float y ) {')
$cgDrawFPSStart = $cgDrawSource.IndexOf('static float CG_DrawFPS( float y ) {')
$cgDrawTimerStart = $cgDrawSource.IndexOf('static float CG_DrawTimer( float y ) {')
$cgTextPaintWithCursorExtStart = $cgMainSource.IndexOf('static void CG_Text_PaintWithCursorExt( float x, float y, float scale, vec4_t color, const char *text, int cursorPos, char cursor, int limit, int style, int fontIndex ) {')
$cgTextPaintWithCursorStart = $cgMainSource.IndexOf('void CG_Text_PaintWithCursor( float x, float y, float scale, vec4_t color, const char *text, int cursorPos, char cursor, int limit, int style ) {')
$cgOwnerDrawWidthStart = $cgMainSource.IndexOf('static int CG_OwnerDrawWidth( int ownerDraw, float scale ) {')
$cgPaintLimitStart = $cgNewdrawSource.IndexOf('static void CG_Text_Paint_Limit(float *maxX, float x, float y, float scale, vec4_t color, const char* text, float adjust, int limit) {')
$cgNewTeamInfoStart = $cgNewdrawSource.IndexOf('void CG_DrawNewTeamInfo(rectDef_t *rect, float text_x, float text_y, float scale, vec4_t color, qhandle_t shader) {')
$conDrawInputStart = $clConsoleSource.IndexOf('void Con_DrawInput (void) {')
$conDrawNotifyStart = $clConsoleSource.IndexOf('void Con_DrawNotify (void)')
$conDrawHostTextStart = $clConsoleSource.IndexOf('static void Con_DrawHostText( int x, int y, int charWidth, int charHeight, const char *text, const float *color, qboolean forceColor ) {')
$conDrawHostCharStart = $clConsoleSource.IndexOf('static void Con_DrawHostChar( int x, int y, int charWidth, int charHeight, int ch, const float *color, qboolean forceColor ) {')
$conDrawHostFieldHelperStart = $clConsoleSource.IndexOf('static void Con_DrawHostField_helper( field_t *edit, int x, int y, int charWidth, int charHeight, qboolean showCursor ) {')
$conDrawHostFieldStart = $clConsoleSource.IndexOf('static void Con_DrawHostField( field_t *edit, int x, int y, int charWidth, int charHeight, qboolean showCursor ) {')
$conDrawConsoleLineTextStart = $clConsoleSource.IndexOf('static void Con_DrawConsoleLineText( int x, int y, const short *text, int count ) {')
$conGetChatFieldWidthStart = $clConsoleSource.IndexOf('static int Con_GetChatFieldWidthInChars( qboolean teamChat ) {')
$conDrawSolidStart = $clConsoleSource.IndexOf('void Con_DrawSolidConsole( float frac ) {')
$scrDrawStringStart = $clScrnSource.IndexOf('void SCR_DrawStringExt( int x, int y, float size, const char *string, float *setColor, qboolean forceColor ) {')
$scrDrawBigStringStart = $clScrnSource.IndexOf('void SCR_DrawBigString( int x, int y, const char *s, float alpha ) {')
$uiSyscallDrawStart = $uiSyscallsSource.IndexOf('void trap_QL_DrawScaledText( int x, int y, const char *text, int fontHandle, float scale, int maxX, float *outMaxX, qboolean forceColor ) {')
$uiSyscallMeasureStart = $uiSyscallsSource.IndexOf('unsigned long long trap_QL_MeasureText( const char *text, const char *end, int fontHandle, float scale, int maxX, float *outLeft ) {')
$uiSyscallGetItemStart = $uiSyscallsSource.IndexOf('void trap_QL_GetItemDownloadInfo( unsigned int itemIdLow, unsigned int itemIdHigh, unsigned long long *outDownloaded, unsigned long long *outTotal ) {')
$cgSyscallDrawStart = $cgSyscallsSource.IndexOf('void trap_QL_DrawScaledText( int x, int y, const char *text, int fontHandle, float scale, int maxX, float *outMaxX, qboolean forceColor ) {')
$cgSyscallMeasureStart = $cgSyscallsSource.IndexOf('unsigned long long trap_QL_MeasureText( const char *text, const char *end, int fontHandle, float scale, int maxX, float *outLeft ) {')
$cgSyscallAvatarStart = $cgSyscallsSource.IndexOf('qhandle_t trap_QL_GetAvatarImageHandle( unsigned int identityLow, unsigned int identityHigh ) {')
$cgVmDrawStubStart = $cgLocalSource.IndexOf('static ID_INLINE void trap_QL_DrawScaledText( int x, int y, const char *text, int fontHandle, float scale, int maxX, float *outMaxX, qboolean forceColor ) {')
$cgVmMeasureStubStart = $cgLocalSource.IndexOf('static ID_INLINE unsigned long long trap_QL_MeasureText( const char *text, const char *end, int fontHandle, float scale, int maxX, float *outLeft ) {')
$cgVmMutedStubStart = $cgLocalSource.IndexOf('static ID_INLINE int trap_QL_IsClientMuted( unsigned int identityLow, unsigned int identityHigh ) {')
$rAdvertDebugTextStart = $trWorldSource.IndexOf('static void R_DrawAdvertisementDebugText( int y, const char *text, const vec4_t color ) {')
$rAdvertDebugQuadStart = $trWorldSource.IndexOf('static void R_DrawAdvertisementDebugQuad( const vec3_t points[4], const vec4_t color ) {')

if ( $uiAssetCacheStart -ge 0 -and $uiAssetParseStart -gt $uiAssetCacheStart ) {
	$uiAssetCacheBlock = $uiMainSource.Substring( $uiAssetCacheStart, $uiAssetParseStart - $uiAssetCacheStart )
	if ( $uiAssetCacheBlock -match 'trap_R_RegisterFont' ) {
		Report-UnresolvedGap -Message 'UI AssetCache still eagerly registers fonts instead of leaving font ownership to the retail parser path.'
	}
	else {
		Write-Host 'Verified UI AssetCache stays art-only and does not eagerly register fonts.'
	}
}
else {
	Report-UnresolvedGap -Message 'Unable to locate UI AssetCache or Asset_Parse while auditing font-cache ownership.'
}

if ( $uiAssetParseStart -ge 0 -and $uiAssetStopStart -gt $uiAssetParseStart ) {
	$uiAssetParseBlock = $uiMainSource.Substring( $uiAssetParseStart, $uiAssetStopStart - $uiAssetParseStart )
	if ( $uiAssetParseBlock -match 'if \(Q_stricmp\(token\.string, "font"\) == 0\) \{' -and
		$uiAssetParseBlock -match 'UI_NormalizeFontPath\( &fontPath, &pointSize, QL_FONT_NAME_TEXT, QL_FONT_TEXT_POINT_SIZE \);' -and
		$uiAssetParseBlock -match 'trap_R_RegisterFont\(fontPath, pointSize, &uiInfo\.uiDC\.Assets\.textFont\);' -and
		$uiAssetParseBlock -match 'uiInfo\.uiDC\.Assets\.fontRegistered = qtrue;' -and
		$uiAssetParseBlock -match 'if \(Q_stricmp\(token\.string, "smallFont"\) == 0\) \{' -and
		$uiAssetParseBlock -match 'UI_NormalizeFontPath\( &fontPath, &pointSize, QL_FONT_NAME_SMALL, QL_FONT_SMALL_POINT_SIZE \);' -and
		$uiAssetParseBlock -match 'trap_R_RegisterFont\(fontPath, pointSize, &uiInfo\.uiDC\.Assets\.smallFont\);' -and
		$uiAssetParseBlock -match 'if \(Q_stricmp\(token\.string, "bigFont"\) == 0\) \{' -and
		$uiAssetParseBlock -match 'UI_NormalizeFontPath\( &fontPath, &pointSize, QL_FONT_NAME_BIG, QL_FONT_BIG_POINT_SIZE \);' -and
		$uiAssetParseBlock -match 'trap_R_RegisterFont\(fontPath, pointSize, &uiInfo\.uiDC\.Assets\.bigFont\);' ) {
		Write-Host 'Verified UI assetGlobalDef registers text/small/big fonts through normalized retail buckets.'
	}
	else {
		Report-UnresolvedGap -Message 'UI assetGlobalDef font registration no longer normalizes and registers the retail text/small/big buckets.'
	}
}
else {
	Report-UnresolvedGap -Message 'Unable to locate UI Asset_Parse while auditing font bucket registration.'
}

if ( $uiNormalizeFontStart -ge 0 -and $uiPcScriptParseStart -gt $uiNormalizeFontStart ) {
	$uiNormalizeFontPrelude = $uiSharedSource.Substring( 0, $uiNormalizeFontStart )
	$uiNormalizeFontBlock = $uiSharedSource.Substring( $uiNormalizeFontStart, $uiPcScriptParseStart - $uiNormalizeFontStart )
	if ( $uiNormalizeFontPrelude -match '\{ "FONT_DEFAULT", QL_FONT_NAME_TEXT, QL_FONT_TEXT_POINT_SIZE \}' -and
		$uiNormalizeFontPrelude -match '\{ "FONT_SANS", QL_FONT_NAME_SMALL, QL_FONT_SMALL_POINT_SIZE \}' -and
		$uiNormalizeFontPrelude -match '\{ "FONT_MONO", QL_FONT_NAME_MONO, QL_FONT_MONO_POINT_SIZE \}' -and
		$uiNormalizeFontPrelude -match '\{ "font2", QL_FONT_NAME_BIG, QL_FONT_BIG_POINT_SIZE \}' -and
		$uiNormalizeFontPrelude -match '\{ "fonts/arial\.ttf", QL_FONT_NAME_TEXT, QL_FONT_TEXT_POINT_SIZE \}' -and
		$uiNormalizeFontPrelude -match '\{ "fonts/verdana\.ttf", QL_FONT_NAME_SMALL, QL_FONT_SMALL_POINT_SIZE \}' -and
		$uiNormalizeFontBlock -match '\*fontName = uiLegacyFontMap\[i\]\.fontName;' -and
		$uiNormalizeFontBlock -match '\*pointSize = uiLegacyFontMap\[i\]\.pointSize;' -and
		$uiNormalizeFontBlock -match 'if \( \(\*fontName\)\[0\] == ''\\0'' && defaultFont != NULL \) \{' -and
		$uiNormalizeFontBlock -match '\*fontName = defaultFont;' -and
		$uiNormalizeFontBlock -match 'if \( \*pointSize <= 0 \) \{' -and
		$uiNormalizeFontBlock -match '\*pointSize = defaultPointSize;' ) {
		Write-Host 'Verified UI font alias normalization maps legacy tokens onto Quake Live buckets and default sizes.'
	}
	else {
		Report-UnresolvedGap -Message 'UI font alias normalization no longer maps legacy tokens/default sizes onto Quake Live buckets.'
	}
}
else {
	Report-UnresolvedGap -Message 'Unable to locate UI_NormalizeFontPath while auditing font alias mapping.'
}

if ( $uiItemTextWidthStart -ge 0 -and $uiItemTextHeightStart -gt $uiItemTextWidthStart -and $uiItemDrawTextStart -gt $uiItemTextHeightStart -and $uiItemDrawTextWithCursorStart -gt $uiItemDrawTextStart -and $uiItemSetTextExtentsStart -gt $uiItemDrawTextWithCursorStart ) {
	$uiItemTextWidthBlock = $uiSharedSource.Substring( $uiItemTextWidthStart, $uiItemTextHeightStart - $uiItemTextWidthStart )
	$uiItemTextHeightBlock = $uiSharedSource.Substring( $uiItemTextHeightStart, $uiItemDrawTextStart - $uiItemTextHeightStart )
	$uiItemDrawTextBlock = $uiSharedSource.Substring( $uiItemDrawTextStart, $uiItemDrawTextWithCursorStart - $uiItemDrawTextStart )
	$uiItemDrawTextWithCursorBlock = $uiSharedSource.Substring( $uiItemDrawTextWithCursorStart, $uiItemSetTextExtentsStart - $uiItemDrawTextWithCursorStart )
	if ( $uiItemTextWidthBlock -match 'DC->textWidthExt\(text, item->textscale, limit, item->fontIndex\)' -and
		$uiItemTextHeightBlock -match 'DC->textHeightExt\(text, item->textscale, limit, item->fontIndex\)' -and
		$uiItemDrawTextBlock -match 'DC->drawTextExt\(x, y, item->textscale, color, text, adjust, limit, item->textStyle, item->fontIndex\);' -and
		$uiItemDrawTextWithCursorBlock -match 'DC->drawTextWithCursorExt\(x, y, item->textscale, color, text, cursorPos, cursor, limit, item->textStyle, item->fontIndex\);' ) {
		Write-Host 'Verified UI item text width/height/paint wrappers forward item font buckets into host text ext callbacks.'
	}
	else {
		Report-UnresolvedGap -Message 'UI item text wrappers no longer forward item font buckets through the host text ext callbacks.'
	}
}
else {
	Report-UnresolvedGap -Message 'Unable to locate UI item text wrappers while auditing item font bucket plumbing.'
}

if ( $uiItemInitStart -ge 0 -and $uiMenuHandleMouseMoveStart -gt $uiItemInitStart -and $uiItemParseFontStart -ge 0 -and $uiItemParseTextScaleStart -gt $uiItemParseFontStart ) {
	$uiItemInitBlock = $uiSharedSource.Substring( $uiItemInitStart, $uiMenuHandleMouseMoveStart - $uiItemInitStart )
	$uiItemParseFontBlock = $uiSharedSource.Substring( $uiItemParseFontStart, $uiItemParseTextScaleStart - $uiItemParseFontStart )
	if ( $uiItemInitBlock -match 'item->fontIndex = ITEM_FONT_INHERIT;' -and
		$uiItemParseFontBlock -match 'PC_Int_Parse\(handle, &item->fontIndex\)' -and
		$uiItemParseFontBlock -notmatch 'PC_String_Parse' -and
		$uiItemParseFontBlock -notmatch 'String_Alloc' ) {
		Write-Host 'Verified UI item font parser stores the retail integer font bucket instead of a string asset.'
	}
	else {
		Report-UnresolvedGap -Message 'UI item font parser no longer preserves the retail integer font-bucket contract.'
	}
}
else {
	Report-UnresolvedGap -Message 'Unable to locate UI item init/font parser while auditing item font bucket ownership.'
}

if ( $uiMenuParseFontStart -ge 0 -and $uiMenuParseNameStart -gt $uiMenuParseFontStart ) {
	$uiMenuParseFontBlock = $uiSharedSource.Substring( $uiMenuParseFontStart, $uiMenuParseNameStart - $uiMenuParseFontStart )
	if ( $uiMenuParseFontBlock -match 'UI_NormalizeFontPath\( &fontPath, &pointSize, QL_FONT_NAME_TEXT, QL_FONT_TEXT_POINT_SIZE \);' -and
		$uiMenuParseFontBlock -match 'menu->font = String_Alloc\( fontPath \);' -and
		$uiMenuParseFontBlock -match 'if \(!DC->Assets\.fontRegistered\) \{' -and
		$uiMenuParseFontBlock -match 'DC->registerFont\( fontPath, pointSize, &DC->Assets\.textFont \);' -and
		$uiMenuParseFontBlock -match 'DC->registerFont\( QL_FONT_NAME_SMALL, QL_FONT_SMALL_POINT_SIZE, &DC->Assets\.smallFont \);' -and
		$uiMenuParseFontBlock -match 'DC->registerFont\( QL_FONT_NAME_BIG, QL_FONT_BIG_POINT_SIZE, &DC->Assets\.bigFont \);' -and
		$uiMenuParseFontBlock -match 'DC->Assets\.fontRegistered = qtrue;' ) {
		Write-Host 'Verified UI menu font parser normalizes and bootstraps the retained font trio once.'
	}
	else {
		Report-UnresolvedGap -Message 'UI menu font parser no longer normalizes and bootstraps the retained font trio.'
	}
}
else {
	Report-UnresolvedGap -Message 'Unable to locate MenuParse_font while auditing menu font bootstrap.'
}

if ( $uiMenuParseKeywordsStart -ge 0 -and $uiMenuParseKeywordHashStart -gt $uiMenuParseKeywordsStart -and
	$cgSetupBrowserMenuHashStart -ge 0 -and $cgParseBrowserMenuStart -gt $cgSetupBrowserMenuHashStart -and
	$cgInitBrowserRuntimeStart -ge 0 -and $cgResetBrowserOverlayStateStart -gt $cgInitBrowserRuntimeStart ) {
	$uiMenuParseKeywordsBlock = $uiSharedSource.Substring( $uiMenuParseKeywordsStart, $uiMenuParseKeywordHashStart - $uiMenuParseKeywordsStart )
	$cgBrowserMenuHashBlock = $cgMainSource.Substring( $cgSetupBrowserMenuHashStart, $cgParseBrowserMenuStart - $cgSetupBrowserMenuHashStart )
	$cgBrowserMenuParseBlock = $cgMainSource.Substring( $cgParseBrowserMenuStart, $cgInitBrowserRuntimeStart - $cgParseBrowserMenuStart )
	$cgInitBrowserRuntimeBlock = $cgMainSource.Substring( $cgInitBrowserRuntimeStart, $cgResetBrowserOverlayStateStart - $cgInitBrowserRuntimeStart )
	if ( $uiMenuParseKeywordsBlock -match '\{"font", MenuParse_font, NULL\}' -and
		$cgBrowserMenuHashBlock -match 'Menu_SetupKeywordHash\(\);' -and
		$cgBrowserMenuParseBlock -match 'return Menu_Parse\( handle, \(menuDef_t \*\)menu \);' -and
		$cgInitBrowserRuntimeBlock -match 'String_Init\(\);' -and
		$cgInitBrowserRuntimeBlock -match 'CG_SetupBrowserMenuKeywordHash\(\);' ) {
		Write-Host 'Verified cgame browser menu parsing reaches the shared retail font parser through the menu keyword hash.'
	}
	else {
		Report-UnresolvedGap -Message 'cgame browser menu parsing no longer routes font declarations through the shared retail MenuParse_font path.'
	}
}
else {
	Report-UnresolvedGap -Message 'Unable to locate cgame browser menu parser seam while auditing font parser routing.'
}

if ( $cgRegisterFontsStart -ge 0 -and $cgLoadHudMenuStart -gt $cgRegisterFontsStart ) {
	$cgRegisterFontsBlock = $cgMainSource.Substring( $cgRegisterFontsStart, $cgLoadHudMenuStart - $cgRegisterFontsStart )
	if ( $cgRegisterFontsBlock -match 'if \( cgDC\.Assets\.fontRegistered \) \{' -and
		$cgRegisterFontsBlock -match 'trap_R_RegisterFont\( QL_FONT_NAME_TEXT, QL_FONT_TEXT_POINT_SIZE, &cgDC\.Assets\.textFont \);' -and
		$cgRegisterFontsBlock -match 'trap_R_RegisterFont\( QL_FONT_NAME_SMALL, QL_FONT_SMALL_POINT_SIZE, &cgDC\.Assets\.smallFont \);' -and
		$cgRegisterFontsBlock -match 'trap_R_RegisterFont\( QL_FONT_NAME_BIG, QL_FONT_BIG_POINT_SIZE, &cgDC\.Assets\.bigFont \);' -and
		$cgRegisterFontsBlock -match 'cgDC\.Assets\.fontRegistered = qtrue;' ) {
		Write-Host 'Verified cgame HUD font bootstrap registers the retail text/small/big font trio once.'
	}
	else {
		Report-UnresolvedGap -Message 'cgame HUD font bootstrap no longer registers the retail text/small/big font buckets once.'
	}
}
else {
	Report-UnresolvedGap -Message 'Unable to locate CG_RegisterHudFonts while auditing cgame font ownership.'
}

if ( $cgAssetParseStart -ge 0 -and $cgParseMenuStart -gt $cgAssetParseStart ) {
	$cgAssetParseBlock = $cgMainSource.Substring( $cgAssetParseStart, $cgParseMenuStart - $cgAssetParseStart )
	if ( $cgAssetParseBlock -match 'if \(Q_stricmp\(token\.string, "font"\) == 0\) \{' -and
		$cgAssetParseBlock -match 'cgDC\.registerFont\(tempStr, pointSize, &cgDC\.Assets\.textFont\);' -and
		$cgAssetParseBlock -match 'if \(Q_stricmp\(token\.string, "smallFont"\) == 0\) \{' -and
		$cgAssetParseBlock -match 'cgDC\.registerFont\(tempStr, pointSize, &cgDC\.Assets\.smallFont\);' -and
		$cgAssetParseBlock -match 'if \(Q_stricmp\(token\.string, "bigfont"\) == 0\) \{' -and
		$cgAssetParseBlock -match 'cgDC\.registerFont\(tempStr, pointSize, &cgDC\.Assets\.bigFont\);' -and
		$cgAssetParseBlock -cnotmatch 'Q_stricmp\(token\.string, "bigFont"\)' ) {
		Write-Host 'Verified cgame assetGlobalDef registers retail font/smallFont/lowercase-bigfont buckets.'
	}
	else {
		Report-UnresolvedGap -Message 'cgame assetGlobalDef font registration no longer matches retail font/smallFont/lowercase-bigfont tokens.'
	}
}
else {
	Report-UnresolvedGap -Message 'Unable to locate CG_Asset_Parse while auditing cgame asset font buckets.'
}

if ( $cgAssetCacheStart -ge 0 -and $cgInitStart -gt $cgAssetCacheStart ) {
	$cgAssetCacheBlock = $cgMainSource.Substring( $cgAssetCacheStart, $cgInitStart - $cgAssetCacheStart )
	if ( $cgAssetCacheBlock -match 'CG_RegisterHudFonts\(\);' ) {
		Report-UnresolvedGap -Message 'CG_AssetCache still eagerly registers HUD fonts instead of remaining an art-only retail cache.'
	}
	else {
		Write-Host 'Verified CG_AssetCache stays art-only and no longer re-registers HUD fonts.'
	}
}
else {
	Report-UnresolvedGap -Message 'Unable to locate CG_AssetCache or CG_Init while auditing cgame font-cache ownership.'
}

if ( $cgInitStart -ge 0 ) {
	$cgInitBlock = $cgMainSource.Substring( $cgInitStart )
	$cgInitDisplayIndex = $cgInitBlock.IndexOf('CG_InitDisplayContext();')
	$cgRegisterFontsIndex = $cgInitBlock.IndexOf('CG_RegisterHudFonts();')
	$cgInitBrowserRuntimeIndex = $cgInitBlock.IndexOf('CG_InitBrowserRuntime();')
	$cgAssetCacheIndex = $cgInitBlock.IndexOf('CG_AssetCache();')
	$cgLoadHudMenuIndex = $cgInitBlock.IndexOf('CG_LoadHudMenu();')
	if ( $cgInitDisplayIndex -ge 0 -and
		$cgRegisterFontsIndex -gt $cgInitDisplayIndex -and
		$cgInitBrowserRuntimeIndex -gt $cgRegisterFontsIndex -and
		$cgAssetCacheIndex -gt $cgInitBrowserRuntimeIndex -and
		$cgLoadHudMenuIndex -gt $cgAssetCacheIndex ) {
		Write-Host 'Verified cgame init seeds cgDC fonts before browser menu runtime and HUD menu parsing.'
	}
	else {
		Report-UnresolvedGap -Message 'cgame init no longer seeds display-context fonts before browser HUD menu parsing.'
	}
}
else {
	Report-UnresolvedGap -Message 'Unable to locate CG_Init while auditing cgame browser font bootstrap ordering.'
}

if ( $cgLoadHudCommandStart -ge 0 -and $cgLoadHudCommandStopStart -gt $cgLoadHudCommandStart ) {
	$cgLoadHudCommandBlock = $cgConsoleSource.Substring( $cgLoadHudCommandStart, $cgLoadHudCommandStopStart - $cgLoadHudCommandStart )
	if ( $cgLoadHudCommandBlock -match 'CG_InitBrowserRuntime\(\);' -and
		$cgLoadHudCommandBlock -match 'CG_LoadHudMenu\(\);' -and
		$cgLoadHudCommandBlock.IndexOf('CG_InitBrowserRuntime();') -lt $cgLoadHudCommandBlock.IndexOf('CG_LoadHudMenu();') -and
		$cgLoadHudCommandBlock -notmatch 'Menu_Reset\(\);' -and
		$cgLoadHudCommandBlock -notmatch 'Menu_Parse\(' ) {
		Write-Host 'Verified cgame loadhud refresh rebuilds browser parser state before replaying HUD menu font parsing.'
	}
	else {
		Report-UnresolvedGap -Message 'cgame loadhud refresh no longer rebuilds browser parser state before HUD font parsing.'
	}
}
else {
	Report-UnresolvedGap -Message 'Unable to locate CG_LoadHud_f while auditing HUD font reload wiring.'
}

if ( $uiSelectFontStart -ge 0 -and $uiSelectHandleStart -gt $uiSelectFontStart ) {
	$uiSelectFontBlock = $uiMainSource.Substring( $uiSelectFontStart, $uiSelectHandleStart - $uiSelectFontStart )
	$smallThresholdIndex = Get-RegexIndex -Text $uiSelectFontBlock -Pattern 'if\s*\(\s*scale\s*<=\s*ui_smallFont\.value\s*\)\s*\{'
	$bigThresholdIndex = Get-RegexIndex -Text $uiSelectFontBlock -Pattern 'if\s*\(\s*scale\s*>=\s*ui_bigFont\.value\s*\)\s*\{'
	$textReturnIndex = Get-RegexIndex -Text $uiSelectFontBlock -Pattern 'return\s+&uiInfo\.uiDC\.Assets\.textFont\s*;\s*\}'
	$smallScaleBlock = ''
	$bigScaleBlock = ''

	if ( $smallThresholdIndex -ge 0 -and $bigThresholdIndex -gt $smallThresholdIndex ) {
		$smallScaleBlock = $uiSelectFontBlock.Substring( $smallThresholdIndex, $bigThresholdIndex - $smallThresholdIndex )
	}
	if ( $bigThresholdIndex -ge 0 -and $textReturnIndex -gt $bigThresholdIndex ) {
		$bigScaleBlock = $uiSelectFontBlock.Substring( $bigThresholdIndex, $textReturnIndex - $bigThresholdIndex )
	}

	if ( $smallScaleBlock -match 'return\s+&uiInfo\.uiDC\.Assets\.smallFont\s*;' -and
		$bigScaleBlock -match 'return\s+&uiInfo\.uiDC\.Assets\.bigFont\s*;' -and
		$textReturnIndex -gt $bigThresholdIndex ) {
		Write-Host 'Verified UI scale thresholds select small, big, and text font buckets in retail order.'
	}
	else {
		Report-UnresolvedGap -Message 'UI scale-driven font selection no longer honors ui_smallFont/ui_bigFont bucket thresholds.'
	}
}
else {
	Report-UnresolvedGap -Message 'Unable to locate UI_SelectTextFont while auditing scale-driven UI font buckets.'
}

if ( $uiSelectHandleStart -ge 0 -and $uiTextLimitStart -gt $uiSelectHandleStart ) {
	$uiSelectHandleBlock = $uiMainSource.Substring( $uiSelectHandleStart, $uiTextLimitStart - $uiSelectHandleStart )
	if ( $uiSelectHandleBlock -match 'case FONT_SANS:' -and
		$uiSelectHandleBlock -match 'case FONT_MONO:' -and
		$uiSelectHandleBlock -match 'case FONT_DEFAULT:' -and
		$uiSelectHandleBlock -match 'font = UI_SelectTextFont\( scale, ITEM_FONT_INHERIT \);' -and
		$uiSelectHandleBlock -match 'if \( font == &uiInfo\.uiDC\.Assets\.smallFont \) \{' -and
		$uiSelectHandleBlock -match 'return FONT_SANS;' -and
		$uiSelectHandleBlock -match 'return FONT_DEFAULT;' -and
		$uiSelectHandleBlock -notmatch 'font == &uiInfo\.uiDC\.Assets\.bigFont.*return FONT_SANS' -and
		$uiSelectHandleBlock -notmatch 'font == &uiInfo\.uiDC\.Assets\.bigFont.*return FONT_MONO' ) {
		Write-Host 'Verified UI host-text face selection maps explicit font buckets, inherited small, and inherited big/default scale correctly.'
	}
	else {
		Report-UnresolvedGap -Message 'UI host-text face selection no longer maps explicit or inherited font buckets to the retained face table.'
	}
}
else {
	Report-UnresolvedGap -Message 'Unable to locate UI_SelectTextFontHandle while auditing host-text face selection.'
}

if ( $uiHostMetricsStart -ge 0 -and $uiDrawHostTextSpanStart -gt $uiHostMetricsStart -and $uiTextWidthExtStart -gt $uiDrawHostTextSpanStart ) {
	$uiHostMetricsBlock = $uiMainSource.Substring( $uiHostMetricsStart, $uiDrawHostTextSpanStart - $uiHostMetricsStart )
	$uiDrawHostTextSpanBlock = $uiMainSource.Substring( $uiDrawHostTextSpanStart, $uiTextWidthExtStart - $uiDrawHostTextSpanStart )
	if ( $uiHostMetricsBlock -match 'UI_RefreshDisplayContextScale\(\);' -and
		$uiHostMetricsBlock -match 'limitEnd = UI_GetTextLimitEnd\( text, limit \);' -and
		$uiHostMetricsBlock -match 'packed = trap_QL_MeasureText\(' -and
		$uiHostMetricsBlock -match 'UI_SelectTextFontHandle\( scale, fontIndex \),' -and
		$uiHostMetricsBlock -match 'scale \* QL_FONT_HOST_POINT_SIZE \* uiInfo\.uiDC\.yscale,' -and
		$uiHostMetricsBlock -match 'UI_UnpackFloatBits64\( packed, &width, &height \);' -and
		$uiHostMetricsBlock -match '\*outWidth = \(int\)\( width / uiInfo\.uiDC\.xscale \);' -and
		$uiHostMetricsBlock -match '\*outHeight = \(int\)\( height / uiInfo\.uiDC\.yscale \);' -and
		$uiDrawHostTextSpanBlock -match 'UI_AdjustFrom640\( &screenX, &screenY, NULL, NULL \);' -and
		$uiDrawHostTextSpanBlock -match 'hostScale = scale \* QL_FONT_HOST_POINT_SIZE \* uiInfo\.uiDC\.yscale;' -and
		$uiDrawHostTextSpanBlock -match 'fontHandle = UI_SelectTextFontHandle\( scale, fontIndex \);' -and
		$uiDrawHostTextSpanBlock -match 'ofs = \( style == ITEM_TEXTSTYLE_SHADOWED \) \? 1 : 2;' -and
		$uiDrawHostTextSpanBlock -match 'trap_QL_DrawScaledText\( \(int\)screenX \+ ofs, \(int\)screenY \+ ofs, text, fontHandle, hostScale, 0, NULL, qtrue \);' -and
		$uiDrawHostTextSpanBlock -match 'trap_QL_DrawScaledText\( \(int\)screenX, \(int\)screenY, text, fontHandle, hostScale, 0, NULL, forceColor \);' -and
		$uiDrawHostTextSpanBlock -notmatch 'Text_PaintChar' -and
		$uiDrawHostTextSpanBlock -notmatch 'trap_R_DrawStretchPic' ) {
		Write-Host 'Verified UI host text metrics and span painting project through the native retained text traps.'
	}
	else {
		Report-UnresolvedGap -Message 'UI host text metrics or span painting no longer project through the retained native text traps.'
	}
}
else {
	Report-UnresolvedGap -Message 'Unable to locate UI host text metrics/span helpers while auditing retained text wiring.'
}

if ( $uiTextPaintWithCursorExtStart -ge 0 -and $uiTextPaintWithCursorStart -gt $uiTextPaintWithCursorExtStart ) {
	$uiTextPaintWithCursorExtBlock = $uiMainSource.Substring( $uiTextPaintWithCursorExtStart, $uiTextPaintWithCursorStart - $uiTextPaintWithCursorExtStart )
	if ( $uiTextPaintWithCursorExtBlock -match 'UI_DrawHostTextSpan\( x, y, scale, color, drawText, fontIndex, style, qfalse \);' -and
		$uiTextPaintWithCursorExtBlock -match 'cursorEnd = UI_GetCursorTextEnd\( text, limitEnd, cursorPos, color, cursorColor \);' -and
		$uiTextPaintWithCursorExtBlock -match 'UI_AdjustFrom640\( &screenX, &screenY, NULL, NULL \);' -and
		$uiTextPaintWithCursorExtBlock -match 'hostScale = scale \* QL_FONT_HOST_POINT_SIZE \* uiInfo\.uiDC\.yscale;' -and
		$uiTextPaintWithCursorExtBlock -match 'fontHandle = UI_SelectTextFontHandle\( scale, fontIndex \);' -and
		$uiTextPaintWithCursorExtBlock -match 'trap_QL_MeasureText\( text, cursorEnd, fontHandle, hostScale, 0, NULL \)' -and
		$uiTextPaintWithCursorExtBlock -match 'trap_QL_DrawScaledText\( \(int\)\( screenX \+ prefixWidth \) \+ ofs, \(int\)screenY \+ ofs, cursorString, fontHandle, hostScale, 0, NULL, qtrue \);' -and
		$uiTextPaintWithCursorExtBlock -match 'trap_QL_DrawScaledText\( \(int\)\( screenX \+ prefixWidth \), \(int\)screenY, cursorString, fontHandle, hostScale, 0, NULL, qtrue \);' -and
		$uiTextPaintWithCursorExtBlock -notmatch 'Text_PaintChar' -and
		$uiTextPaintWithCursorExtBlock -notmatch 'trap_R_DrawStretchPic' ) {
		Write-Host 'Verified UI cursor text uses retained host-text prefix measurement and cursor drawing.'
	}
	else {
		Report-UnresolvedGap -Message 'UI cursor text no longer uses retained host-text prefix measurement and cursor drawing.'
	}
}
else {
	Report-UnresolvedGap -Message 'Unable to locate Text_PaintWithCursorExt while auditing UI cursor text wiring.'
}

if ( $uiPaintLimitStart -ge 0 -and $uiSyncMenuStateStart -gt $uiPaintLimitStart ) {
	$uiPaintLimitBlock = $uiMainSource.Substring( $uiPaintLimitStart, $uiSyncMenuStateStart - $uiPaintLimitStart )
	if ( $uiPaintLimitBlock -match 'limitEnd = UI_GetTextLimitEnd\( text, limit \);' -and
		$uiPaintLimitBlock -match 'UI_CopyTextSpan\( text, limitEnd, limitedText, sizeof\( limitedText \) \);' -and
		$uiPaintLimitBlock -match 'UI_AdjustFrom640\( &screenX, &screenY, NULL, NULL \);' -and
		$uiPaintLimitBlock -match 'UI_AdjustFrom640\( &screenMaxX, NULL, NULL, NULL \);' -and
		$uiPaintLimitBlock -match 'fontHandle = UI_SelectTextFontHandle\( scale, ITEM_FONT_INHERIT \);' -and
		$uiPaintLimitBlock -match 'scale \* QL_FONT_HOST_POINT_SIZE \* uiInfo\.uiDC\.yscale,' -and
		$uiPaintLimitBlock -match '\(int\)screenMaxX,' -and
		$uiPaintLimitBlock -match '&outMaxX,' -and
		$uiPaintLimitBlock -match '\*maxX = \( outMaxX - uiInfo\.uiDC\.bias \) / uiInfo\.uiDC\.xscale;' -and
		$uiPaintLimitBlock -notmatch 'Text_PaintChar' ) {
		Write-Host 'Verified UI limited text paint projects maxX through the retail host-text draw path.'
	}
	else {
		Report-UnresolvedGap -Message 'UI limited text paint no longer matches the retail host-text maxX projection path.'
	}
}
else {
	Report-UnresolvedGap -Message 'Unable to locate Text_Paint_Limit while auditing UI host-text clipping.'
}

if ( $cgSelectHandleStart -ge 0 -and $cgTextLimitStart -gt $cgSelectHandleStart ) {
	$cgSelectHandleBlock = $cgDrawSource.Substring( $cgSelectHandleStart, $cgTextLimitStart - $cgSelectHandleStart )
	if ( $cgSelectHandleBlock -match 'case FONT_SANS:' -and
		$cgSelectHandleBlock -match 'case FONT_MONO:' -and
		$cgSelectHandleBlock -match 'case FONT_DEFAULT:' -and
		$cgSelectHandleBlock -match 'if \( scale <= cg_smallFont\.value \) \{' -and
		$cgSelectHandleBlock -match 'return FONT_SANS;' -and
		$cgSelectHandleBlock -match 'return FONT_DEFAULT;' -and
		$cgSelectHandleBlock -notmatch 'cg_bigFont' ) {
		Write-Host 'Verified cgame host-text face selection maps explicit buckets, inherited small, and inherited default/big scale correctly.'
	}
	else {
		Report-UnresolvedGap -Message 'cgame host-text face selection no longer maps explicit or inherited font buckets to the retained face table.'
	}
}
else {
	Report-UnresolvedGap -Message 'Unable to locate CG_SelectTextFontHandle while auditing host-text face selection.'
}

if ( $cgHostMetricsStart -ge 0 -and $cgDrawHostTextSpanStart -gt $cgHostMetricsStart -and $cgTextWidthExtStart -gt $cgDrawHostTextSpanStart -and $cgTextGetExtentsStart -gt $cgTextWidthExtStart -and $cgTextPaintCharStart -gt $cgTextGetExtentsStart ) {
	$cgHostMetricsBlock = $cgDrawSource.Substring( $cgHostMetricsStart, $cgDrawHostTextSpanStart - $cgHostMetricsStart )
	$cgDrawHostTextSpanBlock = $cgDrawSource.Substring( $cgDrawHostTextSpanStart, $cgTextWidthExtStart - $cgDrawHostTextSpanStart )
	$cgTextWidthHeightBlock = $cgDrawSource.Substring( $cgTextWidthExtStart, $cgTextGetExtentsStart - $cgTextWidthExtStart )
	$cgTextGetExtentsBlock = $cgDrawSource.Substring( $cgTextGetExtentsStart, $cgTextPaintCharStart - $cgTextGetExtentsStart )
	if ( $cgHostMetricsBlock -match 'CG_AdjustFrom640\( NULL, NULL, &xScale, &yScale \);' -and
		$cgHostMetricsBlock -match 'limitEnd = CG_GetTextLimitEnd\( text, limit \);' -and
		$cgHostMetricsBlock -match 'packed = trap_QL_MeasureText\(' -and
		$cgHostMetricsBlock -match 'CG_SelectTextFontHandle\( scale, fontIndex \),' -and
		$cgHostMetricsBlock -match 'scale \* QL_FONT_HOST_POINT_SIZE \* yScale,' -and
		$cgHostMetricsBlock -match 'CG_UnpackFloatBits64\( packed, &width, &height \);' -and
		$cgHostMetricsBlock -match '\*outWidth = \(int\)\( width / xScale \);' -and
		$cgHostMetricsBlock -match '\*outHeight = \(int\)\( height / yScale \);' -and
		$cgDrawHostTextSpanBlock -match 'CG_AdjustFrom640\( &screenX, &screenY, NULL, &yScale \);' -and
		$cgDrawHostTextSpanBlock -match 'hostScale = scale \* QL_FONT_HOST_POINT_SIZE \* yScale;' -and
		$cgDrawHostTextSpanBlock -match 'fontHandle = CG_SelectTextFontHandle\( scale, fontIndex \);' -and
		$cgDrawHostTextSpanBlock -match 'shadowOffset = \( style == ITEM_TEXTSTYLE_SHADOWED \) \? 1\.0f : 2\.0f;' -and
		$cgDrawHostTextSpanBlock -match 'trap_QL_DrawScaledText\( \(int\)shadowX, \(int\)shadowY, text, fontHandle, hostScale, 0, NULL, qtrue \);' -and
		$cgDrawHostTextSpanBlock -match 'trap_QL_DrawScaledText\( \(int\)screenX, \(int\)screenY, text, fontHandle, hostScale, 0, NULL, forceColor \);' -and
		$cgTextWidthHeightBlock -match 'CG_GetHostTextMetrics\( text, scale, limit, fontIndex, &width, NULL \);' -and
		$cgTextWidthHeightBlock -match 'CG_GetHostTextMetrics\( text, scale, limit, fontIndex, NULL, &height \);' -and
		$cgTextGetExtentsBlock -match 'CG_GetHostTextMetrics\( text, scale, limit, ITEM_FONT_INHERIT, outWidth, outHeight \);' -and
		$cgDrawHostTextSpanBlock -notmatch 'CG_Text_PaintChar' -and
		$cgDrawHostTextSpanBlock -notmatch 'trap_R_DrawStretchPic' ) {
		Write-Host 'Verified cgame host text metrics, extents, and span painting project through the native retained text traps.'
	}
	else {
		Report-UnresolvedGap -Message 'cgame host text metrics, extents, or span painting no longer project through the retained native text traps.'
	}
}
else {
	Report-UnresolvedGap -Message 'Unable to locate cgame host text metrics/span helpers while auditing retained text wiring.'
}

if ( $cgTextPaintWithCursorExtStart -ge 0 -and $cgTextPaintWithCursorStart -gt $cgTextPaintWithCursorExtStart -and $cgOwnerDrawWidthStart -gt $cgTextPaintWithCursorStart ) {
	$cgTextPaintWithCursorExtBlock = $cgMainSource.Substring( $cgTextPaintWithCursorExtStart, $cgTextPaintWithCursorStart - $cgTextPaintWithCursorExtStart )
	$cgTextPaintWithCursorBlock = $cgMainSource.Substring( $cgTextPaintWithCursorStart, $cgOwnerDrawWidthStart - $cgTextPaintWithCursorStart )
	if ( $cgTextPaintWithCursorExtBlock -match '\(void\)cursorPos;' -and
		$cgTextPaintWithCursorExtBlock -match '\(void\)cursor;' -and
		$cgTextPaintWithCursorExtBlock -match 'CG_Text_PaintExt\( x, y, scale, color, text, 0\.0f, limit, style, fontIndex \);' -and
		$cgTextPaintWithCursorBlock -match 'CG_Text_PaintWithCursorExt\( x, y, scale, color, text, cursorPos, cursor, limit, style, ITEM_FONT_INHERIT \);' ) {
		Write-Host 'Verified cgame cursor-signature text wrappers preserve the retail shared painter path.'
	}
	else {
		Report-UnresolvedGap -Message 'cgame cursor-signature text wrappers no longer preserve the retail shared painter path.'
	}
}
else {
	Report-UnresolvedGap -Message 'Unable to locate cgame cursor-signature text wrappers while auditing retained text wiring.'
}

if ( $cgDrawSnapshotStart -ge 0 -and $cgDrawFPSStart -gt $cgDrawSnapshotStart ) {
	$cgDrawSnapshotBlock = $cgDrawSource.Substring( $cgDrawSnapshotStart, $cgDrawFPSStart - $cgDrawSnapshotStart )
	if ( $cgDrawSnapshotBlock -match 's = va\( "time:%i snap:%i cmd:%i", cg\.snap->serverTime,' -and
		$cgDrawSnapshotBlock -match 'w = CG_Text_WidthExt\( s, 0\.25f, 0, FONT_DEFAULT \);' -and
		$cgDrawSnapshotBlock -match 'drawY = \(float\)\(int\)\( y \+ 2\.0f \) \+ 16\.0f;' -and
		$cgDrawSnapshotBlock -match 'CG_Text_PaintExt\( 635\.0f - w, drawY, 0\.25f, colorWhite, s, 0\.0f, 0, ITEM_TEXTSTYLE_NORMAL, FONT_DEFAULT \);' -and
		$cgDrawSnapshotBlock -match 'return y \+ 16\.0f \+ 4\.0f;' -and
		$cgDrawSnapshotBlock -notmatch 'CG_DrawBigString' ) {
		Write-Host 'Verified cgame snapshot debug text uses the retail default host-text bucket at scale 0.25.'
	}
	else {
		Report-UnresolvedGap -Message 'cgame snapshot debug text no longer uses the retail default host-text bucket and scale.'
	}
}
else {
	Report-UnresolvedGap -Message 'Unable to locate CG_DrawSnapshot while auditing cgame host-text consumers.'
}

if ( $cgDrawFPSStart -ge 0 -and $cgDrawTimerStart -gt $cgDrawFPSStart ) {
	$cgDrawFPSBlock = $cgDrawSource.Substring( $cgDrawFPSStart, $cgDrawTimerStart - $cgDrawFPSStart )
	if ( $cgDrawFPSBlock -match 'w = CG_Text_WidthExt\( s, 0\.25f, 0, FONT_MONO \);' -and
		$cgDrawFPSBlock -match 'h = CG_Text_HeightExt\( s, 0\.25f, 0, FONT_MONO \);' -and
		$cgDrawFPSBlock -match 'CG_Text_PaintExt\( 635\.0f - w, y \+ h, 0\.25f, colorWhite, s, 0\.0f, 0, ITEM_TEXTSTYLE_NORMAL, FONT_MONO \);' ) {
		Write-Host 'Verified cgame FPS text uses the retail mono host-text bucket at scale 0.25.'
	}
	else {
		Report-UnresolvedGap -Message 'cgame FPS text no longer uses the retail mono host-text bucket and scale.'
	}
}
else {
	Report-UnresolvedGap -Message 'Unable to locate CG_DrawFPS while auditing cgame mono host-text consumers.'
}

if ( $cgPaintLimitStart -ge 0 -and $cgNewTeamInfoStart -gt $cgPaintLimitStart ) {
	$cgPaintLimitBlock = $cgNewdrawSource.Substring( $cgPaintLimitStart, $cgNewTeamInfoStart - $cgPaintLimitStart )
	if ( $cgPaintLimitBlock -match 'CG_AdjustFrom640\( &screenX, &screenY, NULL, NULL \);' -and
		$cgPaintLimitBlock -match 'CG_AdjustFrom640\( &screenMaxX, NULL, NULL, NULL \);' -and
		$cgPaintLimitBlock -match 'CG_AdjustFrom640\( &xBias, NULL, &xScale, &yScale \);' -and
		$cgPaintLimitBlock -match 'fontHandle = CG_SelectTextFontHandle\( scale, ITEM_FONT_INHERIT \);' -and
		$cgPaintLimitBlock -match 'scale \* QL_FONT_HOST_POINT_SIZE \* yScale,' -and
		$cgPaintLimitBlock -match '\(int\)screenMaxX,' -and
		$cgPaintLimitBlock -match '&outMaxX,' -and
		$cgPaintLimitBlock -match '\*maxX = \( outMaxX - xBias \) / xScale;' -and
		$cgPaintLimitBlock -notmatch 'trap_R_DrawStretchPic' ) {
		Write-Host 'Verified cgame limited text paint projects maxX through the retail host-text draw path.'
	}
	else {
		Report-UnresolvedGap -Message 'cgame limited text paint no longer matches the retail host-text maxX projection path.'
	}
}
else {
	Report-UnresolvedGap -Message 'Unable to locate CG_Text_Paint_Limit while auditing cgame host-text clipping.'
}

if ( $conDrawHostTextStart -ge 0 -and $conDrawHostCharStart -gt $conDrawHostTextStart ) {
	$conDrawHostTextBlock = $clConsoleSource.Substring( $conDrawHostTextStart, $conDrawHostCharStart - $conDrawHostTextStart )
	if ( $conDrawHostTextBlock -match 'scale = Con_GetHostTextScale\( charWidth \);' -and
		$conDrawHostTextBlock -match 'Con_GetHostFontMetrics\( charWidth, charHeight, &ascent, NULL \);' -and
		$conDrawHostTextBlock -match 'baselineY = y \+ \(int\)\( ascent \+ 0\.5f \);' -and
		$conDrawHostTextBlock -match 'RE_DrawScaledText\( x, baselineY, text, CONSOLE_HOST_FONT_MONO, scale, 0, NULL, forceColor, drawColor \);' -and
		$conDrawHostTextBlock -notmatch 'DrawStretchPic' -and
		$conDrawHostTextBlock -notmatch 'charSetShader' ) {
		Write-Host 'Verified console host text draws through the retail mono host-text lane.'
	}
	else {
		Report-UnresolvedGap -Message 'Console host text no longer matches the retail mono host-text draw lane.'
	}
}
else {
	Report-UnresolvedGap -Message 'Unable to locate Con_DrawHostText while auditing console host-text wiring.'
}

if ( $conDrawHostFieldHelperStart -ge 0 -and $conDrawHostFieldStart -gt $conDrawHostFieldHelperStart ) {
	$conDrawHostFieldHelperBlock = $clConsoleSource.Substring( $conDrawHostFieldHelperStart, $conDrawHostFieldStart - $conDrawHostFieldHelperStart )
	if ( $clConsoleSource -match 'static qboolean Con_IsUtf8ContinuationByte\( unsigned char ch \) \{' -and
		$clConsoleSource -match 'static int Con_ClampUtf8Boundary\( const char \*text, int index \) \{' -and
		$clConsoleSource -match 'static int Con_PrevUtf8CharStart\( const char \*text, int index \) \{' -and
		$conDrawHostFieldHelperBlock -match 'cursor = Con_ClampUtf8Boundary\( edit->buffer, edit->cursor \);' -and
		$conDrawHostFieldHelperBlock -match 'while \( visibleChars < edit->widthInChars && start > 0 \) \{' -and
		$conDrawHostFieldHelperBlock -match 'start = Con_PrevUtf8CharStart\( edit->buffer, start \);' -and
		$conDrawHostFieldHelperBlock -match 'end = Con_PrevUtf8CharStart\( edit->buffer, end \);' -and
		$conDrawHostFieldHelperBlock -match 'Con_DrawHostText\( x, y, charWidth, charHeight, drawText, g_color_table\[ColorIndex\( COLOR_WHITE \)\], qfalse \);' -and
		$conDrawHostFieldHelperBlock -match 'RE_MeasureScaledText\( drawText, drawText \+ prefixBytes, CONSOLE_HOST_FONT_MONO, Con_GetHostTextScale\( charWidth \), 0, &prefixWidth, NULL, NULL \);' -and
		$conDrawHostFieldHelperBlock -match 'Con_DrawHostText\( cursorX, y, charWidth, charHeight, Key_GetOverstrikeMode\(\) \? "_" : "\|", g_color_table\[ColorIndex\( COLOR_WHITE \)\], qtrue \);' -and
		$conDrawHostFieldHelperBlock -notmatch 'prestep = edit->scroll;' -and
		$conDrawHostFieldHelperBlock -notmatch 'drawLen = edit->widthInChars;' ) {
		Write-Host 'Verified console host field uses UTF-8-aware windowing and host-text cursor measurement.'
	}
	else {
		Report-UnresolvedGap -Message 'Console host field no longer matches the retail UTF-8 host-text cursor/windowing lane.'
	}
}
else {
	Report-UnresolvedGap -Message 'Unable to locate Con_DrawHostField_helper while auditing console field host-text wiring.'
}

if ( $conDrawConsoleLineTextStart -ge 0 -and $conGetChatFieldWidthStart -gt $conDrawConsoleLineTextStart ) {
	$conDrawConsoleLineTextBlock = $clConsoleSource.Substring( $conDrawConsoleLineTextStart, $conGetChatFieldWidthStart - $conDrawConsoleLineTextStart )
	if ( $conDrawConsoleLineTextBlock -match 'buffer\[bufferIndex\+\+\] = ''\^'';' -and
		$conDrawConsoleLineTextBlock -match 'buffer\[bufferIndex\+\+\] = \(char\)\( ''0'' \+ colorIndex \);' -and
		$conDrawConsoleLineTextBlock -match 'Con_DrawHostText\( x, y, charWidth, charHeight, buffer, g_color_table\[ColorIndex\( COLOR_WHITE \)\], qfalse \);' ) {
		Write-Host 'Verified console scrollback text converts packed color cells into host-text color escapes.'
	}
	else {
		Report-UnresolvedGap -Message 'Console scrollback text no longer routes packed color cells through host text.'
	}
}
else {
	Report-UnresolvedGap -Message 'Unable to locate Con_DrawConsoleLineText while auditing console scrollback text wiring.'
}

if ( $conDrawInputStart -ge 0 -and $conDrawNotifyStart -gt $conDrawInputStart -and $conDrawSolidStart -gt $conDrawNotifyStart ) {
	$conDrawInputBlock = $clConsoleSource.Substring( $conDrawInputStart, $conDrawNotifyStart - $conDrawInputStart )
	$conDrawNotifyBlock = $clConsoleSource.Substring( $conDrawNotifyStart, $conDrawSolidStart - $conDrawNotifyStart )
	if ( $conDrawInputBlock -match 'Con_DrawHostChar\( con\.xadjust \+ charWidth, y, charWidth, charHeight, ''\]'', con\.color, qtrue \);' -and
		$conDrawInputBlock -match 'Con_DrawHostField\( &g_consoleField, con\.xadjust \+ 2 \* charWidth, y, charWidth, charHeight, qtrue \);' -and
		$conDrawNotifyBlock -match 'Con_DrawHostText\( promptX, promptY, charWidth, charHeight, prompt, g_color_table\[ColorIndex\( COLOR_WHITE \)\], qtrue \);' -and
		$conDrawNotifyBlock -match 'Con_DrawHostField\( &chatField, fieldX, promptY, charWidth, charHeight, qtrue \);' ) {
		Write-Host 'Verified console and chat input prompts consume the retained host-text field helpers.'
	}
	else {
		Report-UnresolvedGap -Message 'Console or chat input prompts no longer use the retained host-text field helpers.'
	}
}
else {
	Report-UnresolvedGap -Message 'Unable to locate console input or notify draw blocks while auditing host-text prompts.'
}

if ( $scrDrawStringStart -ge 0 -and $scrDrawBigStringStart -gt $scrDrawStringStart ) {
	$scrDrawStringBlock = $clScrnSource.Substring( $scrDrawStringStart, $scrDrawBigStringStart - $scrDrawStringStart )
	if ( $scrDrawStringBlock -match 'xscale = cls\.glconfig\.vidWidth / 640\.0f;' -and
		$scrDrawStringBlock -match 'yscale = cls\.glconfig\.vidHeight / 480\.0f;' -and
		$scrDrawStringBlock -match 'screenX = \(int\)\( x \* xscale \);' -and
		$scrDrawStringBlock -match 'screenY = \(int\)\( y \* yscale \);' -and
		$scrDrawStringBlock -match 'RE_DrawScaledText\( screenX, screenY, string, SCREEN_OVERLAY_HOST_FONT_MONO,' -and
		$scrDrawStringBlock -match 'size \* yscale, -1, NULL, forceColor, setColor \);' -and
		$scrDrawStringBlock -notmatch 'SCR_DrawChar\(' -and
		$clScrnSource -notmatch 'static void SCR_DrawChar' -and
		$scrDrawStringBlock -notmatch 'while \( \*s \)' ) {
		Write-Host 'Verified client screen-overlay text uses the retail mono host-text lane.'
	}
	else {
		Report-UnresolvedGap -Message 'Client screen-overlay text no longer matches the retail scaled mono host-text lane.'
	}
}
else {
	Report-UnresolvedGap -Message 'Unable to locate SCR_DrawStringExt while auditing client screen-overlay text wiring.'
}

if ( $rAdvertDebugTextStart -ge 0 -and $rAdvertDebugQuadStart -gt $rAdvertDebugTextStart ) {
	$rAdvertDebugTextBlock = $trWorldSource.Substring( $rAdvertDebugTextStart, $rAdvertDebugQuadStart - $rAdvertDebugTextStart )
	if ( $trWorldSource -match '#define R_DEBUG_ADVERTISEMENT_TEXT_X\s+25' -and
		$trWorldSource -match '#define R_DEBUG_ADVERTISEMENT_TEXT_Y\s+256' -and
		$trWorldSource -match '#define R_DEBUG_ADVERTISEMENT_TEXT_STEP\s+16' -and
		$trWorldSource -match '#define R_DEBUG_ADVERTISEMENT_TEXT_SCALE\s+\(\s*16\.0f / 48\.0f\s*\)' -and
		$rAdvertDebugTextBlock -match 'RE_DrawScaledText\( R_DEBUG_ADVERTISEMENT_TEXT_X, y, text,' -and
		$rAdvertDebugTextBlock -match '0, R_DEBUG_ADVERTISEMENT_TEXT_SCALE, 0, NULL, qtrue, color \);' -and
		$rAdvertDebugTextBlock -notmatch 'DrawStretchPic' -and
		$rAdvertDebugTextBlock -notmatch 'charSetShader' ) {
		Write-Host 'Verified renderer advertisement debug labels use retained host text.'
	}
	else {
		Report-UnresolvedGap -Message 'Renderer advertisement debug labels no longer use the retained host-text draw path.'
	}
}
else {
	Report-UnresolvedGap -Message 'Unable to locate R_DrawAdvertisementDebugText while auditing renderer host-text consumers.'
}

if ( $uiSyscallDrawStart -ge 0 -and $uiSyscallMeasureStart -gt $uiSyscallDrawStart -and $uiSyscallGetItemStart -gt $uiSyscallMeasureStart ) {
	$uiSyscallDrawBlock = $uiSyscallsSource.Substring( $uiSyscallDrawStart, $uiSyscallMeasureStart - $uiSyscallDrawStart )
	$uiSyscallMeasureBlock = $uiSyscallsSource.Substring( $uiSyscallMeasureStart, $uiSyscallGetItemStart - $uiSyscallMeasureStart )
	if ( $uiSyscallDrawBlock -match 'UI_GetNativeImportFunction\( UI_QL_IMPORT_DRAW_SCALED_TEXT \)' -and
		$uiSyscallDrawBlock -match 'if \( !import \) \{\s+return;\s+\}' -and
		$uiSyscallDrawBlock -match '\(\(void \(QDECL \*\)\( int, int, const char \*, int, float, int, float \*, int \)\)import\)\( x, y, text, fontHandle, scale, maxX, outMaxX, forceColor \? qtrue : qfalse \);' -and
		$uiSyscallDrawBlock -notmatch 'syscall\(' -and
		$uiSyscallMeasureBlock -match 'UI_GetNativeImportFunction\( UI_QL_IMPORT_MEASURE_TEXT \)' -and
		$uiSyscallMeasureBlock -match 'if \( !import \) \{\s+return 0;\s+\}' -and
		$uiSyscallMeasureBlock -match '\(\(unsigned long long \(QDECL \*\)\( const char \*, const char \*, int, float, int, float \* \)\)import\)\( text, end, fontHandle, scale, maxX, outLeft \);' -and
		$uiSyscallMeasureBlock -notmatch 'syscall\(' ) {
		Write-Host 'Verified UI module host text traps resolve native imports and fail closed without compatibility syscall fallback.'
	}
	else {
		Report-UnresolvedGap -Message 'UI module host text traps no longer match the retail native import bridge contract.'
	}
}
else {
	Report-UnresolvedGap -Message 'Unable to locate UI host text trap wrappers while auditing native import bridge wiring.'
}

if ( $cgSyscallDrawStart -ge 0 -and $cgSyscallMeasureStart -gt $cgSyscallDrawStart -and $cgSyscallAvatarStart -gt $cgSyscallMeasureStart ) {
	$cgSyscallDrawBlock = $cgSyscallsSource.Substring( $cgSyscallDrawStart, $cgSyscallMeasureStart - $cgSyscallDrawStart )
	$cgSyscallMeasureBlock = $cgSyscallsSource.Substring( $cgSyscallMeasureStart, $cgSyscallAvatarStart - $cgSyscallMeasureStart )
	if ( $cgSyscallDrawBlock -match 'CG_GetNativeImportFunction\( CG_QL_IMPORT_DRAW_SCALED_TEXT \)' -and
		$cgSyscallDrawBlock -match 'if \( !import \) \{\s+return;\s+\}' -and
		$cgSyscallDrawBlock -match '\(\(void \(QDECL \*\)\( int, int, const char \*, int, float, int, float \*, int \)\)import\)\( x, y, text, fontHandle, scale, maxX, outMaxX, forceColor \? qtrue : qfalse \);' -and
		$cgSyscallDrawBlock -notmatch 'syscall\(' -and
		$cgSyscallMeasureBlock -match 'CG_GetNativeImportFunction\( CG_QL_IMPORT_MEASURE_TEXT \)' -and
		$cgSyscallMeasureBlock -match 'if \( !import \) \{\s+return 0;\s+\}' -and
		$cgSyscallMeasureBlock -match '\(\(unsigned long long \(QDECL \*\)\( const char \*, const char \*, int, float, int, float \* \)\)import\)\( text, end, fontHandle, scale, maxX, outLeft \);' -and
		$cgSyscallMeasureBlock -notmatch 'syscall\(' ) {
		Write-Host 'Verified cgame module host text traps resolve native imports and fail closed without compatibility syscall fallback.'
	}
	else {
		Report-UnresolvedGap -Message 'cgame module host text traps no longer match the retail native import bridge contract.'
	}
}
else {
	Report-UnresolvedGap -Message 'Unable to locate cgame host text trap wrappers while auditing native import bridge wiring.'
}

if ( $cgVmDrawStubStart -ge 0 -and $cgVmMeasureStubStart -gt $cgVmDrawStubStart -and $cgVmMutedStubStart -gt $cgVmMeasureStubStart ) {
	$cgVmDrawStubBlock = $cgLocalSource.Substring( $cgVmDrawStubStart, $cgVmMeasureStubStart - $cgVmDrawStubStart )
	$cgVmMeasureStubBlock = $cgLocalSource.Substring( $cgVmMeasureStubStart, $cgVmMutedStubStart - $cgVmMeasureStubStart )
	if ( $cgVmDrawStubBlock -match '\(void\)x;' -and
		$cgVmDrawStubBlock -match '\(void\)text;' -and
		$cgVmDrawStubBlock -match 'if \( outMaxX \) \{\s+\*outMaxX = 0\.0f;\s+\}' -and
		$cgVmDrawStubBlock -notmatch 'syscall\(' -and
		$cgVmMeasureStubBlock -match '\(void\)text;' -and
		$cgVmMeasureStubBlock -match 'if \( outLeft \) \{\s+\*outLeft = 0\.0f;\s+\}' -and
		$cgVmMeasureStubBlock -match 'return 0;' -and
		$cgVmMeasureStubBlock -notmatch 'syscall\(' ) {
		Write-Host 'Verified cgame Q3_VM host text stubs fail closed without compatibility syscall fallback.'
	}
	else {
		Report-UnresolvedGap -Message 'cgame Q3_VM host text stubs no longer fail closed cleanly.'
	}
}
else {
	Report-UnresolvedGap -Message 'Unable to locate cgame Q3_VM host text stubs while auditing fallback wiring.'
}

if ($uiCompatShimPresent -or $cgameCompatShimPresent) {
	Report-UnresolvedGap -Message 'Retail host text import switchover remains incomplete: native ui/cgame DrawScaledText and MeasureText still use compatibility glyph loops instead of the retained host text core.'
}
else {
	Write-Host 'Verified host text imports no longer route through compatibility glyph loops.'
}

if ($retainedAtlasPriority -lt 0 -or $compatFontPriority -lt 0 -or $retainedAtlasPriority -gt $compatFontPriority) {
	Report-UnresolvedGap -Message 'Renderer host text glyph selection still prefers the classic compatibility font lane ahead of the retained *fontstash atlas.'
}
else {
	Write-Host 'Verified renderer host text glyph selection prefers the retained *fontstash atlas.'
}

if ( $trPublicSource.IndexOf('(*AdvertisementBridge_UpdateLoadingViewParameters)') -lt $trPublicSource.IndexOf('(*SetColor)') -and
	$trPublicSource.IndexOf('(*ModelBounds)') -lt $trPublicSource.IndexOf('(*RegisterFont)') -and
	$trPublicSource.IndexOf('(*RegisterFont)') -lt $trPublicSource.IndexOf('(*RemapShader)') -and
	$trPublicSource.IndexOf('(*inPVS)') -lt $trPublicSource.IndexOf('(*PostProcessRestart)') -and
	$trPublicSource.IndexOf('(*PostProcessRestart)') -lt $trPublicSource.IndexOf('(*DrawScaledText)') -and
	$trInitSource.IndexOf('re.SetColor = RE_SetColor;') -lt $trInitSource.IndexOf('re.PostProcessRestart = R_PostProcessRestart;') ) {
	Write-Host 'Verified renderer refexport ABI tail keeps the retail loading bridge, no-op font slot, and postprocess_restart order.'
}
else {
	Report-UnresolvedGap -Message 'Renderer refexport ABI tail no longer matches the retail loading bridge, no-op font slot, or postprocess_restart order.'
}

if ( $trFontSource -match 'for \( s = text; \*s; s\+\+ \)' -or $trFontSource -match 'for \( s = text; \*s && \( !end \|\| s < end \); s\+\+ \)' ) {
	Report-UnresolvedGap -Message 'Renderer host text draw/measure still iterate raw bytes instead of decoding UTF-8 codepoints first.'
}
elseif ( $trFontSource -match 'R_DecodeFontStashCodepoint\( s, end, &codepoint \)' ) {
	Write-Host 'Verified renderer host text walks UTF-8 codepoints instead of raw bytes.'
}
else {
	Report-UnresolvedGap -Message 'Renderer host text UTF-8 decode helper is not wired into the draw/measure loops.'
}

if ( $trFontSource -match 'Q_IsColorString\( s \)' ) {
	Report-UnresolvedGap -Message 'Renderer host text still uses the legacy broad Q_IsColorString parser instead of the retail digit-only caret escape rules.'
}
elseif ( $trFontSource -match 'R_ParseHostTextColorEscape\( s, end, &colorIndex, &colorNext \)' ) {
	Write-Host 'Verified renderer host text uses the retail digit-only color-escape helper.'
}
else {
	Report-UnresolvedGap -Message 'Renderer host text color-escape handling is missing the retail digit-only parser.'
}

if ( $rGetScaleTenthsStart -ge 0 -and $rDecodeCodepointStart -gt $rGetScaleTenthsStart -and $rParseColorEscapeStart -gt $rDecodeCodepointStart -and $rAppendFaceChainStart -gt $rParseColorEscapeStart ) {
	$rGetScaleTenthsBlock = $trFontSource.Substring( $rGetScaleTenthsStart, $rDecodeCodepointStart - $rGetScaleTenthsStart )
	$rParseColorEscapeBlock = $trFontSource.Substring( $rParseColorEscapeStart, $rAppendFaceChainStart - $rParseColorEscapeStart )
	if ( $rGetScaleTenthsBlock -match 'if \( scale <= 0\.0f \) \{\s+scale = R_FONTSTASH_POINT_SIZE;' -and
		$rGetScaleTenthsBlock -match 'scaleTenths = \(int\)\( scale \* 10\.0f \+ 0\.5f \);' -and
		$rGetScaleTenthsBlock -match 'scaleTenths = 2;' -and
		$rGetScaleTenthsBlock -match 'scaleTenths = 0x7fff;' -and
		$rParseColorEscapeBlock -match 'if \( !text \|\| \*text != Q_COLOR_ESCAPE \) \{' -and
		$rParseColorEscapeBlock -match 'next = R_DecodeFontStashCodepoint\( text \+ 1, end, &codepoint \);' -and
		$rParseColorEscapeBlock -match 'codepoint < ''0'' \|\| codepoint > ''7''' -and
		$rParseColorEscapeBlock -match '\*outColorIndex = \(int\)\( codepoint - ''0'' \);' -and
		$rParseColorEscapeBlock -notmatch 'Q_IsColorString' ) {
		Write-Host 'Verified renderer host text scale rounding/clamping and digit-only color escape parsing.'
	}
	else {
		Report-UnresolvedGap -Message 'Renderer host text scale rounding/clamping or digit-only color parsing no longer matches retail.'
	}
}
else {
	Report-UnresolvedGap -Message 'Unable to locate renderer scale/color helper blocks while auditing host text core.'
}

if ( $rGetFaceForHandleStart -ge 0 -and $rGetScaledFontMetricsStart -gt $rGetFaceForHandleStart ) {
	$rGetFaceForHandleBlock = $trFontSource.Substring( $rGetFaceForHandleStart, $rGetScaledFontMetricsStart - $rGetFaceForHandleStart )
	if ( $rGetFaceForHandleBlock -match 'case R_FONTSTASH_FACE_SANS:' -and
		$rGetFaceForHandleBlock -match 'face = r_fontStash\.primarySansFace;' -and
		$rGetFaceForHandleBlock -match 'case R_FONTSTASH_FACE_MONO:' -and
		$rGetFaceForHandleBlock -match 'face = R_GetFontStashFace\( R_FONTSTASH_FACE_MONO \);' -and
		$rGetFaceForHandleBlock -match 'case R_FONTSTASH_FACE_NORMAL:' -and
		$rGetFaceForHandleBlock -match 'face = R_GetFontStashFace\( R_FONTSTASH_FACE_NORMAL \);' -and
		$rGetFaceForHandleBlock -match 'if \( !face \|\| !face->loaded \) \{\s+face = R_GetFontStashFace\( R_FONTSTASH_FACE_NORMAL \);' -and
		$rGetFaceForHandleBlock -match 'if \( \( !face \|\| !face->loaded \) && r_fontStash\.primarySansFace && r_fontStash\.primarySansFace->loaded \) \{' ) {
		Write-Host 'Verified renderer host text face handles fall back through normal and primary sans faces.'
	}
	else {
		Report-UnresolvedGap -Message 'Renderer host text face-handle fallback no longer mirrors the retained face table order.'
	}
}
else {
	Report-UnresolvedGap -Message 'Unable to locate R_GetFontStashFaceForHandle while auditing host text face fallback.'
}

if ( $trFontSource -match 'R_BuildFontStashFaceChain\( face, faceChain, ARRAY_LEN\( faceChain \) \)' -and
	$trFontSource -match 'R_GetFontStashGlyph\( face, codepoint, scaleTenths, &resolvedGlyph \)' ) {
	Write-Host 'Verified retained host glyph lookup uses fallback-face probing and codepoint-plus-size cache keys.'
}
else {
	Report-UnresolvedGap -Message 'Renderer host text glyph lookup still lacks retail fallback-face probing or codepoint-plus-size glyph cache selection.'
}

if ( $reDrawScaledTextStart -ge 0 -and $reMeasureScaledTextStart -gt $reDrawScaledTextStart -and $reRegisterFontFallbackStart -gt $reMeasureScaledTextStart ) {
	$reDrawScaledTextBlock = $trFontSource.Substring( $reDrawScaledTextStart, $reMeasureScaledTextStart - $reDrawScaledTextStart )
	$reMeasureScaledTextBlock = $trFontSource.Substring( $reMeasureScaledTextStart, $reRegisterFontFallbackStart - $reMeasureScaledTextStart )
	if ( $reDrawScaledTextBlock -match '\*outMaxX = \(float\)x;' -and
		$reDrawScaledTextBlock -match 'face = R_GetFontStashFaceForHandle\( fontHandle \);' -and
		$reDrawScaledTextBlock -match 'hasMaxX = \( maxX > 0 \);' -and
		$reDrawScaledTextBlock -match 'if \( R_ParseHostTextColorEscape\( s, end, &colorIndex, &colorNext \) \) \{' -and
		$reDrawScaledTextBlock -match 'if \( !forceColor \) \{' -and
		$reDrawScaledTextBlock -match 'newColor\[3\] = currentColor\[3\];' -and
		$reDrawScaledTextBlock -match 's = colorNext;' -and
		$reDrawScaledTextBlock -match 'next = R_DecodeFontStashCodepoint\( s, end, &codepoint \);' -and
		$reDrawScaledTextBlock -match 'glyphMaxX = penX \+ advance;' -and
		$reDrawScaledTextBlock -match 'if \( penX \+ drawRight > glyphMaxX \) \{' -and
		$reDrawScaledTextBlock -match 'if \( hasMaxX && glyphMaxX > maxXf \) \{' -and
		$reDrawScaledTextBlock -match '\*outMaxX = 0\.0f;' -and
		$reDrawScaledTextBlock.IndexOf('if ( hasMaxX && glyphMaxX > maxXf ) {') -lt $reDrawScaledTextBlock.IndexOf('RE_StretchPic(') -and
		$reDrawScaledTextBlock -match 'penX \+ drawLeft,' -and
		$reDrawScaledTextBlock -match '\(float\)y - drawTop,' -and
		$reDrawScaledTextBlock -match '\*outMaxX = glyphMaxX;' -and
		$reDrawScaledTextBlock -match 'RE_SetColor\( currentColor \);' -and
		$reMeasureScaledTextBlock -match '\*outWidth = 0\.0f;' -and
		$reMeasureScaledTextBlock -match '\*outHeight = 0\.0f;' -and
		$reMeasureScaledTextBlock -match '\*outLeft = 0\.0f;' -and
		$reMeasureScaledTextBlock -match 'for \( s = text; \*s && \( !end \|\| s < end \); \)' -and
		$reMeasureScaledTextBlock -match 'if \( R_ParseHostTextColorEscape\( s, end, &colorIndex, &colorNext \) \) \{' -and
		$reMeasureScaledTextBlock -match 'next = R_DecodeFontStashCodepoint\( s, end, &codepoint \);' -and
		$reMeasureScaledTextBlock -match 'glyphRight = penX \+ drawRight;' -and
		$reMeasureScaledTextBlock -match 'glyphMaxX = penX \+ advance;' -and
		$reMeasureScaledTextBlock.IndexOf('if ( hasMaxX && glyphMaxX > maxXf ) {') -lt $reMeasureScaledTextBlock.IndexOf('hasBounds = qtrue;') -and
		$reMeasureScaledTextBlock -match 'width = maxRight - minLeft;' -and
		$reMeasureScaledTextBlock -match 'height = metricsAscent;' -and
		$reMeasureScaledTextBlock -match '\*outLeft = hasBounds \? minLeft : 0\.0f;' ) {
		Write-Host 'Verified renderer DrawScaledText/MeasureScaledText maxX, color, bounds, and outMaxX/outLeft semantics.'
	}
	else {
		Report-UnresolvedGap -Message 'Renderer DrawScaledText/MeasureScaledText no longer preserve retail maxX/color/bounds semantics.'
	}
}
else {
	Report-UnresolvedGap -Message 'Unable to locate renderer DrawScaledText/MeasureScaledText while auditing host text core.'
}

if ( $trFontSource -match 'R_PrebuildFontStashAtlas' -or $trFontSource -match 'R_FONTSTASH_PREBUILD_ATTEMPTS' ) {
	Report-UnresolvedGap -Message 'Renderer host text still eagerly prebuilds the retained FontStash atlas during startup instead of populating it lazily.'
}
elseif ( $trFontSource -match 'R_RescaleFontStashGlyphUVs\( oldWidth, oldHeight, width, height \)' -and
	$trFontSource -match 'Com_Memcpy\( newBuffer \+ row \* width, oldBuffer \+ row \* oldWidth, copyWidth \);' ) {
	Write-Host 'Verified retained FontStash atlas growth preserves cached glyph pixels and UVs.'
}
else {
	Report-UnresolvedGap -Message 'Renderer host text atlas expansion does not preserve cached glyph pixels and UVs.'
}

if ( $trFontSource -match 'r_fontStash\.image->internalFormat = GL_ALPHA;' -and
	$trFontSource -match 'qglTexImage2D\( GL_TEXTURE_2D, 0, GL_ALPHA, r_fontStash\.width, r_fontStash\.height, 0, GL_ALPHA, GL_UNSIGNED_BYTE, r_fontStash\.buffer \);' ) {
	Write-Host 'Verified retained FontStash atlas uploads use the retail GL_ALPHA texture storage path.'
}
else {
	Report-UnresolvedGap -Message 'Renderer host text atlas uploads still do not mirror the retail GL_ALPHA texture storage path.'
}

if ($unexpectedDebugAtlasPaths.Count -gt 0) {
	Write-Host "Verified r_debugFontAtlas implementation references outside the legacy declaration sites: $($unexpectedDebugAtlasPaths.Count)"
}
else {
	Report-UnresolvedGap -Message 'Retail debug font-atlas path remains incomplete: r_debugFontAtlas only appears in declaration/registration wiring, not in an atlas draw implementation.'
}

foreach ($projectPath in @(
	'src/code/renderer/renderer.vcxproj',
	'src/code/renderer/renderer.vcxproj.filters',
	'src/code/renderer/renderer.vcproj',
	'src/code/unix/Makefile'
)) {
	$fullPath = Join-Path $RepoRoot $projectPath
	if (Select-String -Path $fullPath -Pattern '\.\.\\ft2\\|src/code/ft2|FTDIR' -Quiet) {
		Report-UnresolvedGap -Message "Legacy FreeType vendor references remain in $projectPath."
	}
}

foreach ($projectPath in @(
	'src/code/renderer/renderer.vcxproj',
	'src/code/quakelive_steam.vcxproj',
	'.vscode/build.ps1'
)) {
	$fullPath = Join-Path $RepoRoot $projectPath
	if (Select-String -Path $fullPath -Pattern 'VCPKG_ROOT|C:\\vcpkg' -Quiet) {
		Report-UnresolvedGap -Message "Non-retail external dependency probing remains in $projectPath."
	}
}

$runtimeEvidence = Read-JsonFile -RelativePath 'artifacts/renderer_validation/logs/renderer_runtime_evidence_latest.json'
if ($runtimeEvidence.phase -ne 'RG-P11') {
	Report-UnresolvedGap -Message 'Renderer runtime artifact is not the RG-P11 closure artifact.'
}
if ($runtimeEvidence.parity_estimate.before -ne 98 -or $runtimeEvidence.parity_estimate.after -ne 100) {
	Report-UnresolvedGap -Message 'Renderer runtime artifact parity estimate does not match the RG-P11 closure values.'
}
if ($runtimeEvidence.warnings.Count -ne 0 -or $runtimeEvidence.missing_log_markers.Count -ne 0) {
	Report-UnresolvedGap -Message 'Renderer runtime artifact still records warnings or missing log markers.'
}
if (-not $runtimeEvidence.debug_atlas.engine_sha256) {
	Report-UnresolvedGap -Message 'Renderer runtime artifact is missing retained-atlas screenshot hashes.'
}
if ($runtimeEvidence.main_menu.engine_sha256 -eq $runtimeEvidence.debug_atlas.engine_sha256) {
	Report-UnresolvedGap -Message 'Renderer runtime artifact does not distinguish main-menu and debug-atlas engine captures.'
}
if (-not $runtimeEvidence.text_validation.fontstash_init_seen -or
	$runtimeEvidence.text_validation.registerfont_fallback_seen -or
	-not $runtimeEvidence.text_validation.debug_atlas_engine_capture_distinct) {
	Report-UnresolvedGap -Message 'Renderer runtime artifact does not prove final text-specific validation.'
}

Write-Host 'Retail font-stack audit completed.'
