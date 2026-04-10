[CmdletBinding()]
param(
	[string]$Solution,
	[string]$Configuration = 'Debug',
	[string]$Platform = 'x86'
)

$scriptRoot = $PSScriptRoot
if (-not $scriptRoot) {
	$scriptRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
}

if (-not $Solution) {
	$Solution = Join-Path $scriptRoot '..\src\code\quakelive.sln'
}

$ErrorActionPreference = 'Stop'

$platformNormalized = $Platform
if ($platformNormalized -ieq 'Win32') {
	$platformNormalized = 'x86'
}

$msbuildPath = $null
$msbuildCmd = Get-Command msbuild.exe -ErrorAction SilentlyContinue
if ($msbuildCmd) {
	$msbuildPath = $msbuildCmd.Source
}

if (-not $msbuildPath) {
	$vswhere = $null
	$pf86 = [Environment]::GetFolderPath('ProgramFilesX86')
	if ($pf86) {
		$candidate = Join-Path $pf86 'Microsoft Visual Studio/Installer/vswhere.exe'
		if (Test-Path $candidate) {
			$vswhere = $candidate
		}
	}
	if (-not $vswhere) {
		$pf = [Environment]::GetFolderPath('ProgramFiles')
		if ($pf) {
			$candidate = Join-Path $pf 'Microsoft Visual Studio/Installer/vswhere.exe'
			if (Test-Path $candidate) {
				$vswhere = $candidate
			}
		}
	}
	if ($vswhere) {
		$msbuildPath = & $vswhere -latest -products * -find 'MSBuild\**\Bin\MSBuild.exe' 2>$null | Select-Object -First 1
	}
}

if (-not $msbuildPath) {
	$pf = [Environment]::GetFolderPath('ProgramFiles')
	if ($pf) {
		$vs18Root = Join-Path $pf 'Microsoft Visual Studio\18'
		if (Test-Path $vs18Root) {
			$msbuildPath = Get-ChildItem -Path $vs18Root -Filter MSBuild.exe -Recurse -ErrorAction SilentlyContinue |
				Where-Object { $_.FullName -match '\\MSBuild\\Current\\Bin(\\amd64)?\\MSBuild\.exe$' } |
				Select-Object -First 1 -ExpandProperty FullName
		}
	}
}

if (-not $msbuildPath) {
	throw 'msbuild.exe was not found. Install Visual Studio Build Tools or ensure MSBuild is available.'
}

function Get-LatestWindowsSdkVersion {
	$roots = @(
		'C:\Program Files (x86)\Windows Kits\10\Include',
		'C:\Program Files\Windows Kits\10\Include'
	)

	foreach ($root in $roots) {
		if (-not (Test-Path $root)) {
			continue
		}

		$versions = Get-ChildItem -Path $root -Directory -ErrorAction SilentlyContinue | Sort-Object Name -Descending
		foreach ($version in $versions) {
			if (Test-Path (Join-Path $version.FullName 'um')) {
				return $version.Name
			}
		}
	}

	return $null
}

$msbuildDir = Split-Path -Parent $msbuildPath
$msbuildBase = $null
$cursor = $msbuildDir
while ($cursor -and (Split-Path -Leaf $cursor) -ne 'MSBuild') {
	$cursor = Split-Path -Parent $cursor
}
if ($cursor) {
	$msbuildBase = $cursor
} else {
	$msbuildBase = Split-Path -Parent (Split-Path -Parent $msbuildPath)
}
$defaultToolset = $null

# Prefer the checked-in v141 default when it is installed; otherwise let the project files decide.
$vcPropsRoot = Join-Path $msbuildBase 'Microsoft\VC'
if (Test-Path $vcPropsRoot) {
	$toolsetRoots = Get-ChildItem -Path $vcPropsRoot -Directory -ErrorAction SilentlyContinue |
		ForEach-Object { Join-Path $_.FullName 'Platforms\Win32\PlatformToolsets' } |
		Where-Object { Test-Path $_ }
	if ($toolsetRoots) {
		$installedToolsets = @(
			$toolsetRoots |
			ForEach-Object { Get-ChildItem -Path $_ -Directory -ErrorAction SilentlyContinue | Select-Object -ExpandProperty Name } |
			Sort-Object -Unique
		)
		if ($installedToolsets -contains 'v141') {
			$defaultToolset = 'v141'
		}
	}
}

$toolset = $env:QLR_PLATFORM_TOOLSET
if (-not $toolset) {
	$toolset = $defaultToolset
}
$windowsTargetPlatformVersion = $env:QLR_WINDOWS_TARGET_PLATFORM_VERSION
if (-not $windowsTargetPlatformVersion -and $toolset -eq 'v141') {
	$windowsTargetPlatformVersion = Get-LatestWindowsSdkVersion
}

$solutionPath = Resolve-Path $Solution
$solutionDir = Split-Path -Parent $solutionPath

$vorbisSdkDir = $env:VorbisSdkDir
if (-not $vorbisSdkDir) {
	$vorbisSdkDir = Join-Path $solutionDir '..\libs\vorbis'
}

$pngSdkDir = $env:PngSdkDir
if (-not $pngSdkDir) {
	$pngSdkDir = Join-Path $solutionDir '..\libs\libpng'
}

$enableOgg = $env:QLEnableOgg
$vorbisInclude = Join-Path $vorbisSdkDir 'include\vorbis\vorbisfile.h'
$vorbisLibDir = Join-Path $vorbisSdkDir 'lib\Win32'
$oggAvailable = (Test-Path $vorbisInclude) -and
	(Test-Path (Join-Path $vorbisLibDir 'vorbisfile.lib')) -and
	(Test-Path (Join-Path $vorbisLibDir 'vorbis.lib')) -and
	(Test-Path (Join-Path $vorbisLibDir 'ogg.lib'))
if (-not $enableOgg) {
	$enableOgg = if ($oggAvailable) { 1 } else { 0 }
} else {
	$enableOgg = [int]$enableOgg
}

$enablePng = $env:QLEnablePng
$pngInclude = Join-Path $pngSdkDir 'include\png.h'
$pngLibDir = Join-Path $pngSdkDir 'lib\Win32'
$pngAvailable = (Test-Path $pngInclude) -and
	(Test-Path (Join-Path $pngLibDir 'libpng16.lib')) -and
	(Test-Path (Join-Path $pngLibDir 'zlib.lib'))
if (-not $enablePng) {
	$enablePng = if ($pngAvailable) { 1 } else { 0 }
} else {
	$enablePng = [int]$enablePng
}
if ($enablePng -eq 0 -and $pngAvailable) {
	Write-Warning "QLEnablePng was forced to 0 but libpng is available. Enabling PNG to avoid blank UI assets."
	$enablePng = 1
}

$freeTypeSdkDir = $env:FreeTypeSdkDir
$freeTypeIncludeDir = $env:FreeTypeIncludeDir
$freeTypeLibDir = $env:FreeTypeLibDir
$enableFreeType = $env:QLEnableFreeType
$freeTypeLibraryCandidates = @('freetype.lib', 'libfreetype.lib')
$freeTypeCandidates = New-Object 'System.Collections.Generic.List[object]'

if ($freeTypeIncludeDir -or $freeTypeLibDir) {
	$freeTypeCandidates.Add([pscustomobject]@{
		sdk = $freeTypeSdkDir
		include = if ($freeTypeIncludeDir) { $freeTypeIncludeDir } elseif ($freeTypeSdkDir) { Join-Path $freeTypeSdkDir 'include' } else { '' }
		lib = if ($freeTypeLibDir) { $freeTypeLibDir } elseif ($freeTypeSdkDir) { Join-Path $freeTypeSdkDir 'lib\Win32' } else { '' }
		source = 'explicit FreeType include/lib override'
	})
}

$defaultFreeTypeSdkDir = if ($freeTypeSdkDir) { $freeTypeSdkDir } else { Join-Path $solutionDir '..\libs\freetype' }
foreach ($candidate in @(
	[pscustomobject]@{
		sdk = $defaultFreeTypeSdkDir
		include = Join-Path $defaultFreeTypeSdkDir 'include'
		lib = Join-Path $defaultFreeTypeSdkDir 'lib\Win32'
		source = 'repo-style FreeType SDK root'
	},
	[pscustomobject]@{
		sdk = $defaultFreeTypeSdkDir
		include = Join-Path $defaultFreeTypeSdkDir 'include'
		lib = Join-Path $defaultFreeTypeSdkDir 'lib'
		source = 'flat FreeType SDK root'
	}
)) {
	$freeTypeCandidates.Add($candidate)
}

$vcpkgRoot = $env:VCPKG_ROOT
if (-not $vcpkgRoot -and (Test-Path 'C:\vcpkg')) {
	$vcpkgRoot = 'C:\vcpkg'
}
if ($vcpkgRoot) {
	$vcpkgTripletDir = Join-Path $vcpkgRoot 'installed\x86-windows'
	$freeTypeCandidates.Add([pscustomobject]@{
		sdk = $vcpkgTripletDir
		include = Join-Path $vcpkgTripletDir 'include'
		lib = Join-Path $vcpkgTripletDir 'lib'
		source = 'vcpkg x86-windows installed tree'
	})
}

$freeTypeLibrary = $null
$freeTypeSource = ''
foreach ($candidate in $freeTypeCandidates) {
	if (-not $candidate.include -or -not $candidate.lib) {
		continue
	}

	$header = Join-Path $candidate.include 'ft2build.h'
	$library = $freeTypeLibraryCandidates |
		Where-Object { Test-Path (Join-Path $candidate.lib $_) } |
		Select-Object -First 1
	if ((Test-Path $header) -and $null -ne $library) {
		$freeTypeSdkDir = $candidate.sdk
		$freeTypeIncludeDir = $candidate.include
		$freeTypeLibDir = $candidate.lib
		$freeTypeLibrary = $library
		$freeTypeSource = $candidate.source
		break
	}
}

$freeTypeHeader = if ($freeTypeIncludeDir) { Join-Path $freeTypeIncludeDir 'ft2build.h' } else { '' }
$freeTypeAvailable = ($freeTypeHeader -and (Test-Path $freeTypeHeader) -and ($null -ne $freeTypeLibrary))
if (-not $enableFreeType) {
	$enableFreeType = if ($freeTypeAvailable) { 1 } else { 0 }
} else {
	$enableFreeType = [int]$enableFreeType
}

$msbuildArgs = @(
	$solutionPath,
	'/m',
	"/p:Configuration=$Configuration",
	"/p:Platform=$platformNormalized"
)
if ($toolset) {
	$msbuildArgs += "/p:PlatformToolset=$toolset"
}
if ($windowsTargetPlatformVersion) {
	$msbuildArgs += "/p:WindowsTargetPlatformVersion=$windowsTargetPlatformVersion"
}
if ($enableOgg -ne $null) {
	$msbuildArgs += "/p:QLEnableOgg=$enableOgg"
}
if ($enablePng -ne $null) {
	$msbuildArgs += "/p:QLEnablePng=$enablePng"
}
if ($enableFreeType -ne $null) {
	$msbuildArgs += "/p:QLEnableFreeType=$enableFreeType"
}
if ($env:VorbisSdkDir) {
	$msbuildArgs += "/p:VorbisSdkDir=$vorbisSdkDir"
}
if ($env:PngSdkDir) {
	$msbuildArgs += "/p:PngSdkDir=$pngSdkDir"
}
if ($freeTypeSdkDir) {
	$msbuildArgs += "/p:FreeTypeSdkDir=$freeTypeSdkDir"
}
if ($freeTypeIncludeDir) {
	$msbuildArgs += "/p:FreeTypeIncludeDir=$freeTypeIncludeDir"
}
if ($freeTypeLibDir) {
	$msbuildArgs += "/p:FreeTypeLibDir=$freeTypeLibDir"
}

Write-Host "Using MSBuild: $msbuildPath"
if ($toolset) {
	Write-Host "Using PlatformToolset: $toolset"
}
if ($windowsTargetPlatformVersion) {
	Write-Host "Using Windows SDK: $windowsTargetPlatformVersion"
}
Write-Host "QLEnableOgg: $enableOgg (available: $oggAvailable)"
Write-Host "QLEnablePng: $enablePng (available: $pngAvailable)"
Write-Host "QLEnableFreeType: $enableFreeType (available: $freeTypeAvailable)"
if ($freeTypeAvailable) {
	Write-Host "FreeType SDK source: $freeTypeSource"
	Write-Host "FreeType include: $freeTypeIncludeDir"
	Write-Host "FreeType library: $(Join-Path $freeTypeLibDir $freeTypeLibrary)"
}

& $msbuildPath @msbuildArgs
$buildExitCode = $LASTEXITCODE
if ($buildExitCode -ne 0) {
	exit $buildExitCode
}

if ($enableFreeType -ne 0 -and $freeTypeAvailable) {
	$freeTypeBinDirCandidates = @()
	if ($freeTypeSdkDir) {
		$freeTypeBinDirCandidates += (Join-Path $freeTypeSdkDir 'bin')
		$freeTypeBinDirCandidates += (Join-Path $freeTypeSdkDir 'bin\Win32')
	}
	if ($freeTypeLibDir) {
		$freeTypeLibParent = Split-Path -Parent $freeTypeLibDir
		if ($freeTypeLibParent) {
			$freeTypeBinDirCandidates += (Join-Path $freeTypeLibParent 'bin')
			$freeTypeLibGrandParent = Split-Path -Parent $freeTypeLibParent
			if ($freeTypeLibGrandParent) {
				$freeTypeBinDirCandidates += (Join-Path $freeTypeLibGrandParent 'bin')
			}
		}
	}

	$freeTypeBinDir = $freeTypeBinDirCandidates |
		Where-Object { $_ -and (Test-Path $_) } |
		Select-Object -First 1
	if ($freeTypeBinDir) {
		$runtimeBinDir = Join-Path $solutionDir "..\..\build\win32\$Configuration\bin"
		$freeTypeRuntimeDependencies = @(
			'freetype.dll',
			'brotlidec.dll',
			'brotlicommon.dll',
			'bz2.dll'
		)
		foreach ($dll in $freeTypeRuntimeDependencies) {
			$sourceDll = Join-Path $freeTypeBinDir $dll
			if (Test-Path $sourceDll) {
				Copy-Item -Path $sourceDll -Destination (Join-Path $runtimeBinDir $dll) -Force
			}
		}
	}
}
