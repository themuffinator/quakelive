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

Assert-FileContains -RelativePath 'src/code/renderer/tr_font.c' -Pattern 'R_BuildFontCacheName' -Description 'retail face-specific font cache helper'
Assert-FileContains -RelativePath 'src/code/renderer/tr_font.c' -Pattern 'R_ReadAbsoluteFontFile' -Description 'absolute font-file loader'
Assert-FileContains -RelativePath 'src/code/renderer/tr_font.c' -Pattern 'fonts/handelgothic\.ttf' -Description 'retail default font mapping'
Assert-FileContains -RelativePath 'src/code/renderer/tr_font.c' -Pattern 'fonts/notosans-regular\.ttf' -Description 'retail sans font mapping'
Assert-FileContains -RelativePath 'src/code/renderer/tr_font.c' -Pattern 'fonts/droidsansmono\.ttf' -Description 'retail mono font mapping'
Assert-FileContains -RelativePath 'src/code/renderer/tr_font.c' -Pattern 'fonts/droidsansfallbackfull\.ttf' -Description 'retail fallback font mapping'

Assert-FileContains -RelativePath 'src/code/client/cl_ui.c' -Pattern 'QL_UI_SCALED_FONT_SANS_WINDOWS_FALLBACK' -Description 'UI native Windows fallback handle'
Assert-FileContains -RelativePath 'src/code/client/cl_ui.c' -Pattern 'FindFirstFileA' -Description 'UI native Windows font fallback probing'
Assert-FileContains -RelativePath 'src/code/client/cl_ui.c' -Pattern 'QL_UI_GetScaledFont\( fontHandle \)' -Description 'UI native face-handle dispatch'

Assert-FileContains -RelativePath 'src/code/client/cl_cgame.c' -Pattern 'QL_CG_SCALED_FONT_SANS_WINDOWS_FALLBACK' -Description 'cgame native Windows fallback handle'
Assert-FileContains -RelativePath 'src/code/client/cl_cgame.c' -Pattern 'FindFirstFileA' -Description 'cgame native Windows font fallback probing'
Assert-FileContains -RelativePath 'src/code/client/cl_cgame.c' -Pattern 'QL_CG_GetScaledFont\( fontHandle \)' -Description 'cgame native face-handle dispatch'

$ft2Root = Join-Path $RepoRoot 'src/code/ft2'
if (Test-Path $ft2Root) {
	Write-Host "Found in-tree FreeType source directory: $ft2Root"
}
else {
	Report-UnresolvedGap -Message "Retail renderer project references still point at missing in-tree FreeType sources under '$ft2Root'."
}

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

if ($unexpectedDebugAtlasPaths.Count -gt 0) {
	Write-Host "Found r_debugFontAtlas implementation references outside the legacy declaration sites: $($unexpectedDebugAtlasPaths.Count)"
}
else {
	Report-UnresolvedGap -Message 'Retail debug font-atlas path remains incomplete: r_debugFontAtlas only appears in declaration/registration wiring, not in an atlas draw implementation.'
}

Write-Host 'Retail font-stack audit completed.'
