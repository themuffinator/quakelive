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
Assert-FileContains -RelativePath 'docs/reverse-engineering/renderer-host-text-core-ownership-2026-04-10.md' -Pattern 'RG-P8 is now considered complete' -Description 'RG-P8 ownership closure note'
Assert-FileContains -RelativePath 'src/code/client/cl_ui.c' -Pattern 'RE_DrawScaledText\( x, y, text, fontHandle, scale, maxX, outMaxX' -Description 'UI native host text draw switchover'
Assert-FileContains -RelativePath 'src/code/client/cl_ui.c' -Pattern 'RE_MeasureScaledText\( text, end, fontHandle, scale, maxX, &width, &height, outLeft \)' -Description 'UI native host text measure switchover'
Assert-FileContains -RelativePath 'src/code/client/cl_cgame.c' -Pattern 'RE_DrawScaledText\( x, y, text, fontHandle, scale, maxX, outMaxX' -Description 'cgame native host text draw switchover'
Assert-FileContains -RelativePath 'src/code/client/cl_cgame.c' -Pattern 'RE_MeasureScaledText\( text, end, fontHandle, scale, maxX, &width, &height, outLeft \)' -Description 'cgame native host text measure switchover'
Assert-FileContains -RelativePath 'src/code/renderer/tr_backend.c' -Pattern 'RB_ShowFontAtlas' -Description 'renderer debug font atlas draw path'
Assert-FileContains -RelativePath 'src/code/renderer/renderer.vcxproj' -Pattern 'QLEnableFreeType' -Description 'renderer repo-managed FreeType build toggle'
Assert-FileContains -RelativePath 'src/code/renderer/renderer.vcxproj' -Pattern 'ValidateFreeType' -Description 'renderer repo-managed FreeType validation target'
Assert-FileContains -RelativePath 'src/code/quakelive_steam.vcxproj' -Pattern 'QLEnableFreeType' -Description 'engine repo-managed FreeType link toggle'
Assert-FileContains -RelativePath 'src/code/quakelive_steam.vcxproj' -Pattern 'ValidateFreeType' -Description 'engine repo-managed FreeType validation target'
Assert-FileContains -RelativePath '.vscode/build.ps1' -Pattern 'QLEnableFreeType' -Description 'Windows build-script FreeType toggle'
Assert-FileContains -RelativePath '.vscode/build.ps1' -Pattern 'build_internal_deps\.ps1' -Description 'Windows internal codec bootstrap hook'
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
$uiMainSource = Get-Content -Path (Join-Path $RepoRoot 'src/code/ui/ui_main.c') -Raw
$cgMainSource = Get-Content -Path (Join-Path $RepoRoot 'src/code/cgame/cg_main.c') -Raw
$retainedAtlasPriority = $trFontSource.IndexOf('if ( face->ftFace && r_fontStash.shader ) {')
$compatFontPriority = $trFontSource.IndexOf('if ( R_EnsureFontStashCompatibilityFont( face ) ) {')
$uiAssetCacheStart = $uiMainSource.IndexOf('void AssetCache() {')
$uiAssetParseStart = $uiMainSource.IndexOf('qboolean Asset_Parse(int handle) {')
$cgRegisterFontsStart = $cgMainSource.IndexOf('static void CG_RegisterHudFonts( void ) {')
$cgLoadHudMenuStart = $cgMainSource.IndexOf('void CG_LoadHudMenu() {')
$cgAssetCacheStart = $cgMainSource.IndexOf('void CG_AssetCache() {')
$cgInitStart = $cgMainSource.IndexOf('void CG_Init( int serverMessageNum, int serverCommandSequence, int clientNum ) {')

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

if ( $cgRegisterFontsStart -ge 0 -and $cgLoadHudMenuStart -gt $cgRegisterFontsStart ) {
	$cgRegisterFontsBlock = $cgMainSource.Substring( $cgRegisterFontsStart, $cgLoadHudMenuStart - $cgRegisterFontsStart )
	foreach ( $pattern in @(
		'trap_R_RegisterFont\( QL_FONT_NAME_TEXT, QL_FONT_TEXT_POINT_SIZE, &cgDC\.Assets\.textFont \);',
		'trap_R_RegisterFont\( QL_FONT_NAME_SMALL, QL_FONT_SMALL_POINT_SIZE, &cgDC\.Assets\.smallFont \);',
		'trap_R_RegisterFont\( QL_FONT_NAME_BIG, QL_FONT_BIG_POINT_SIZE, &cgDC\.Assets\.bigFont \);'
	) ) {
		if ( $cgRegisterFontsBlock -notmatch $pattern ) {
			Report-UnresolvedGap -Message 'cgame HUD font bootstrap no longer registers the retail text/small/big font buckets.'
			break
		}
	}
}
else {
	Report-UnresolvedGap -Message 'Unable to locate CG_RegisterHudFonts while auditing cgame font ownership.'
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

$runtimeEvidence = Read-JsonFile -RelativePath 'artifacts/renderer_validation/logs/renderer_runtime_evidence_20260410.json'
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
