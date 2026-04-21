[CmdletBinding()]
param(
	[string]$RepoRoot = (Resolve-Path (Join-Path $PSScriptRoot '../..')).Path,
	[string]$SteamInstallRoot = 'C:\Program Files (x86)\Steam\steamapps\common\Quake Live',
	[string]$RuntimeRoot = '',
	[switch]$SkipSteamInstall,
	[switch]$Strict
)

$ErrorActionPreference = 'Stop'

function Get-NormalizedDllRecord {
	param(
		[string]$Root,
		[System.IO.FileInfo]$File
	)

	$relativePath = $File.FullName.Substring($Root.Length).TrimStart('\', '/')
	$normalized = if ($relativePath -match '^[0-9]{17}[\\/]+baseq3[\\/]') {
		Join-Path 'baseq3' $File.Name
	}
	else {
		$relativePath -replace '/', '\'
	}

	[pscustomobject]@{
		NormalizedPath = $normalized
		FullPath = $File.FullName
		Sha256 = (Get-FileHash $File.FullName -Algorithm SHA256).Hash
	}
}

function Get-RetailReferenceRecord {
	param(
		[string]$Root,
		[string]$RelativePath
	)

	$dlls = Get-ChildItem -Path $Root -Recurse -File -Filter *.dll
	$match = $dlls |
		ForEach-Object { Get-NormalizedDllRecord -Root $Root -File $_ } |
		Where-Object { $_.NormalizedPath -eq $RelativePath } |
		Select-Object -First 1

	if (-not $match) {
		throw "Retail dependency was not found under '$Root': $RelativePath"
	}

	$item = Get-Item $match.FullPath
	[pscustomobject]@{
		RelativePath = $RelativePath
		FullPath = $item.FullName
		Length = $item.Length
		FileVersion = $item.VersionInfo.FileVersion
		ProductVersion = $item.VersionInfo.ProductVersion
		ProductName = $item.VersionInfo.ProductName
		CompanyName = $item.VersionInfo.CompanyName
		Sha256 = (Get-FileHash $item.FullName -Algorithm SHA256).Hash
	}
}

function Invoke-DllPayloadAudit {
	param(
		[string]$Root,
		[string]$Label,
		[object[]]$ExpectedRecords,
		[string[]]$AllowedHashMismatchPaths = @()
	)

	if (-not (Test-Path $Root)) {
		$message = "$Label was not found: $Root"
		if ($Strict) {
			throw $message
		}

		Write-Warning $message
		return
	}

	$rootPath = (Resolve-Path $Root).Path
	$dlls = Get-ChildItem -Path $rootPath -Recurse -File -Filter *.dll
	$actualRecords = $dlls | ForEach-Object {
		Get-NormalizedDllRecord -Root $rootPath -File $_
	}

	$expectedByPath = @{}
	foreach ($record in $ExpectedRecords) {
		$expectedByPath[$record.RelativePath] = $record
	}

	$hashOptionalLookup = @{}
	foreach ($relativePath in $AllowedHashMismatchPaths) {
		$hashOptionalLookup[$relativePath] = $true
	}

	$actualByPath = @{}
	foreach ($record in $actualRecords) {
		if (-not $actualByPath.ContainsKey($record.NormalizedPath)) {
			$actualByPath[$record.NormalizedPath] = @()
		}

		$actualByPath[$record.NormalizedPath] += $record
	}

	$missingExpected = foreach ($relativePath in ($expectedByPath.Keys | Sort-Object)) {
		if (-not $actualByPath.ContainsKey($relativePath)) {
			[pscustomobject]@{
				NormalizedPath = $relativePath
			}
		}
	}

	$mismatches = foreach ($relativePath in ($expectedByPath.Keys | Sort-Object)) {
		if (-not $actualByPath.ContainsKey($relativePath)) {
			continue
		}

		if ($hashOptionalLookup.ContainsKey($relativePath)) {
			continue
		}

		$expectedRecord = $expectedByPath[$relativePath]
		$matchingActual = $actualByPath[$relativePath] | Where-Object { $_.Sha256 -eq $expectedRecord.Sha256 } | Select-Object -First 1
		if ($matchingActual) {
			continue
		}

		foreach ($actualRecord in $actualByPath[$relativePath]) {
			[pscustomobject]@{
				NormalizedPath = $relativePath
				ObservedPath = $actualRecord.FullPath
				ExpectedSha256 = $expectedRecord.Sha256
				ObservedSha256 = $actualRecord.Sha256
			}
		}
	}

	$extra = foreach ($relativePath in ($actualByPath.Keys | Sort-Object)) {
		if ($expectedByPath.ContainsKey($relativePath)) {
			continue
		}

		foreach ($actualRecord in $actualByPath[$relativePath]) {
			[pscustomobject]@{
				NormalizedPath = $relativePath
				ObservedPath = $actualRecord.FullPath
			}
		}
	}

	$matchedCount = @($expectedByPath.Keys | Where-Object {
		$relativePath = $_
		$actualByPath.ContainsKey($relativePath) -and
		($actualByPath[$relativePath] | Where-Object { $_.Sha256 -eq $expectedByPath[$relativePath].Sha256 } | Select-Object -First 1)
	}).Count

	Write-Host ''
	Write-Host "$Label DLL summary: $($dlls.Count) files ($($actualByPath.Keys.Count) normalized paths)"
	Write-Host "Matched retail DLL payload: $matchedCount / $($expectedByPath.Keys.Count)"
	if ($AllowedHashMismatchPaths.Count -gt 0) {
		Write-Host "Retail-hash-optional DLL slots: $($AllowedHashMismatchPaths -join ', ')"
	}

	if ($missingExpected.Count -gt 0) {
		Write-Host ''
		Write-Host "Expected retail DLLs missing from ${Label}:"
		$missingExpected | Select-Object NormalizedPath | Format-Table -AutoSize
	}

	if ($extra.Count -gt 0) {
		Write-Host ''
		Write-Host "Extra DLLs present in ${Label} but absent from the reference retail payload:"
		$extra | Select-Object NormalizedPath, ObservedPath | Format-Table -AutoSize
	}

	if ($mismatches.Count -gt 0) {
		Write-Host ''
		Write-Host "DLLs in ${Label} whose hashes differ from the reference retail payload:"
		$mismatches | Select-Object NormalizedPath, ObservedPath | Format-Table -AutoSize
	}

	if ($Strict -and ($missingExpected.Count -gt 0 -or $extra.Count -gt 0 -or $mismatches.Count -gt 0)) {
		throw "$Label dependency audit failed."
	}

	if ($missingExpected.Count -eq 0 -and $extra.Count -eq 0 -and $mismatches.Count -eq 0) {
		Write-Host "$Label matches the reference retail dependency payload."
	}
}

$assetRoot = Join-Path $RepoRoot 'assets/quakelive'
$retailDllPaths = @(
	'awesomium.dll',
	'steam_api.dll',
	'avcodec-53.dll',
	'avformat-53.dll',
	'avutil-51.dll',
	'libEGL.dll',
	'libGLESv2.dll',
	'icudt.dll',
	'xinput9_1_0.dll',
	'baseq3\cgamex86.dll',
	'baseq3\qagamex86.dll',
	'baseq3\uix86.dll'
)

$referenceRoot = $null
$referenceLabel = $null

if (Test-Path $assetRoot) {
	try {
		$assetRecords = $retailDllPaths | ForEach-Object {
			Get-RetailReferenceRecord -Root $assetRoot -RelativePath $_
		}
		$referenceRoot = $assetRoot
		$referenceLabel = 'committed assets/quakelive payload'
	}
	catch {
		$assetRecords = $null
	}
}

if (-not $assetRecords) {
	if (-not (Test-Path $SteamInstallRoot)) {
		throw "Neither the committed retail DLL payload nor the local Steam install was available for the retail dependency audit."
	}

	$assetRecords = $retailDllPaths | ForEach-Object {
		Get-RetailReferenceRecord -Root $SteamInstallRoot -RelativePath $_
	}
	$referenceRoot = $SteamInstallRoot
	$referenceLabel = 'local Steam install payload'
}
$retailDllRecords = $assetRecords

Write-Host "Retail reference manifest ($referenceLabel):"
$assetRecords |
	Select-Object RelativePath, Length, FileVersion, ProductVersion, ProductName, CompanyName |
	Format-Table -AutoSize

if ($SkipSteamInstall -and -not $RuntimeRoot) {
	throw 'No audit target was supplied. Provide -RuntimeRoot when using -SkipSteamInstall.'
}

if (-not $SkipSteamInstall) {
	Invoke-DllPayloadAudit -Root $SteamInstallRoot -Label 'Steam install root' -ExpectedRecords $retailDllRecords
}

if ($RuntimeRoot) {
	Invoke-DllPayloadAudit `
		-Root $RuntimeRoot `
		-Label 'Runtime root' `
		-ExpectedRecords $retailDllRecords `
		-AllowedHashMismatchPaths @(
			'baseq3\cgamex86.dll',
			'baseq3\qagamex86.dll',
			'baseq3\uix86.dll'
		)
}
