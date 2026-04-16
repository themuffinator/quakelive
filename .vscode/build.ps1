[CmdletBinding()]
param(
	[string]$Solution,
	[string]$Configuration = 'Debug',
	[string]$Platform = 'x86',
	[ValidateSet('0', '1')]
	[string]$OnlineServices = '',
	[ValidateSet('0', '1')]
	[string]$Steamworks = '',
	[ValidateSet('0', '1')]
	[string]$OpenSteam = ''
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
$repoLibsDir = [System.IO.Path]::GetFullPath((Join-Path $scriptRoot '..\src\libs'))
$internalDepsScript = Join-Path $scriptRoot '..\tools\build_internal_deps.ps1'

function Invoke-InternalDependencyBootstrap {
	param(
		[string]$DependencyName
	)

	if (-not (Test-Path $internalDepsScript)) {
		throw "Internal dependency bootstrap script was not found: $internalDepsScript"
	}

	$bootstrapArgs = @(
		'-NoProfile',
		'-ExecutionPolicy', 'Bypass',
		'-File', $internalDepsScript,
		'-RepoRoot', (Join-Path $scriptRoot '..'),
		'-Dependency', $DependencyName
	)

	if ($toolset) {
		$bootstrapArgs += @('-PlatformToolset', $toolset)
	}

	& powershell @bootstrapArgs
	if ($LASTEXITCODE -ne 0) {
		throw "Failed to bootstrap repo-managed dependency '$DependencyName'."
	}
}

$vorbisSdkDir = Join-Path $repoLibsDir 'vorbis'
$vorbisIncludeDir = Join-Path $vorbisSdkDir 'include'
$vorbisLibDir = Join-Path $vorbisSdkDir 'lib\Win32'
$vorbisHeader = Join-Path $vorbisIncludeDir 'vorbis\vorbisfile.h'

$pngSdkDir = Join-Path $repoLibsDir 'libpng'
$pngInclude = Join-Path $pngSdkDir 'include'
$pngLibDir = Join-Path $pngSdkDir 'lib\Win32'
$pngHeader = Join-Path $pngInclude 'png.h'
$pngSource = 'repo-managed libpng install root'

$FreeTypeSdkDir = Join-Path $repoLibsDir 'freetype'
$FreeTypeIncludeDir = Join-Path $FreeTypeSdkDir 'include'
$FreeTypeLibDir = ''
$FreeTypeLibrary = $null
$FreeTypeSource = ''
$FreeTypeLibraryCandidates = @('freetype.lib', 'libfreetype.lib')

$enableOgg = $env:QLEnableOgg
if (-not $enableOgg) {
	Invoke-InternalDependencyBootstrap -DependencyName 'vorbis'
}

$oggAvailable = (Test-Path $vorbisHeader) -and
	(Test-Path (Join-Path $vorbisLibDir 'vorbisfile.lib')) -and
	(Test-Path (Join-Path $vorbisLibDir 'vorbis.lib')) -and
	(Test-Path (Join-Path $vorbisLibDir 'ogg.lib'))
if (-not $enableOgg) {
	$enableOgg = if ($oggAvailable) { 1 } else { 0 }
} else {
	$enableOgg = [int]$enableOgg
}

$enablePng = $env:QLEnablePng
if (-not $enablePng) {
	Invoke-InternalDependencyBootstrap -DependencyName 'png'
}

$pngAvailable = (Test-Path $pngHeader) -and
	(Test-Path (Join-Path $pngLibDir 'libpng16.lib')) -and
	(Test-Path (Join-Path $pngLibDir 'zlib.lib'))
if (-not $enablePng) {
	$enablePng = if ($pngAvailable) { 1 } else { 0 }
} else {
	$enablePng = [int]$enablePng
}
if ($enablePng -eq 0 -and $pngAvailable) {
	Write-Warning "QLEnablePng was forced to 0 but repo-managed libpng is available. Enabling PNG to avoid blank UI assets."
	$enablePng = 1
}

foreach ($candidateLibDir in @(
	(Join-Path $FreeTypeSdkDir 'lib\Win32'),
	(Join-Path $FreeTypeSdkDir 'lib')
)) {
	$library = $FreeTypeLibraryCandidates |
		Where-Object { Test-Path (Join-Path $candidateLibDir $_) } |
		Select-Object -First 1
	if ($library -and (Test-Path (Join-Path $FreeTypeIncludeDir 'ft2build.h'))) {
		$FreeTypeLibDir = $candidateLibDir
		$FreeTypeLibrary = $library
		$FreeTypeSource = 'repo-managed FreeType tree'
		break
	}
}

$enableFreeType = $env:QLEnableFreeType
$freeTypeHeader = Join-Path $FreeTypeIncludeDir 'ft2build.h'
$freeTypeAvailable = (Test-Path $freeTypeHeader) -and ($null -ne $FreeTypeLibrary)
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
if ($OnlineServices -ne '') {
	$msbuildArgs += "/p:QLBuildOnlineServices=$OnlineServices"
}
if ($Steamworks -ne '') {
	$msbuildArgs += "/p:QLBuildSteamworks=$Steamworks"
}
if ($OpenSteam -ne '') {
	$msbuildArgs += "/p:QLBuildOpenSteam=$OpenSteam"
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

Write-Host "Using MSBuild: $msbuildPath"
if ($toolset) {
	Write-Host "Using PlatformToolset: $toolset"
}
if ($windowsTargetPlatformVersion) {
	Write-Host "Using Windows SDK: $windowsTargetPlatformVersion"
}
if ($OnlineServices -ne '') {
	Write-Host "QLBuildOnlineServices: $OnlineServices"
}
if ($Steamworks -ne '') {
	Write-Host "QLBuildSteamworks: $Steamworks"
}
if ($OpenSteam -ne '') {
	Write-Host "QLBuildOpenSteam: $OpenSteam"
}
Write-Host "QLEnableOgg: $enableOgg (available: $oggAvailable)"
Write-Host "Vorbis include: $vorbisIncludeDir"
Write-Host "Vorbis library dir: $vorbisLibDir"
Write-Host "QLEnablePng: $enablePng (available: $pngAvailable)"
if ($pngSource) {
	Write-Host "PNG source: $pngSource"
	Write-Host "PNG include: $pngInclude"
	Write-Host "PNG library dir: $pngLibDir"
}
Write-Host "QLEnableFreeType: $enableFreeType (available: $freeTypeAvailable)"
if ($freeTypeAvailable) {
	Write-Host "FreeType source: $FreeTypeSource"
	Write-Host "FreeType include: $FreeTypeIncludeDir"
	Write-Host "FreeType library: $(Join-Path $FreeTypeLibDir $FreeTypeLibrary)"
}

& $msbuildPath @msbuildArgs
$buildExitCode = $LASTEXITCODE

if ($buildExitCode -ne 0) {
	exit $buildExitCode
}

if ($enableFreeType -ne 0 -and $freeTypeAvailable) {
	$freeTypeBinDirCandidates = @()
	if ($FreeTypeSdkDir) {
		$freeTypeBinDirCandidates += (Join-Path $FreeTypeSdkDir 'bin')
		$freeTypeBinDirCandidates += (Join-Path $FreeTypeSdkDir 'bin\Win32')
	}
	if ($FreeTypeLibDir) {
		$freeTypeLibParent = Split-Path -Parent $FreeTypeLibDir
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

$runtimeBinDir = Join-Path $solutionDir "..\..\build\win32\$Configuration\bin"
$runtimeBaseq3Dir = Join-Path $runtimeBinDir 'baseq3'
$runtimeModulesDir = Join-Path $solutionDir "..\..\build\win32\$Configuration\modules"
$uiBundleBuilder = Join-Path $solutionDir '..\..\tools\build_ui_bundle.py'
$pythonCmd = Get-Command python -ErrorAction SilentlyContinue
if (-not $pythonCmd) {
	$pythonCmd = Get-Command py -ErrorAction SilentlyContinue
}

function Sync-ModuleRuntimeArtifacts {
	param(
		[string]$ModuleName,
		[string]$RuntimeBaseq3Dir,
		[string]$ModulesDir
	)

	$moduleDir = Join-Path $ModulesDir $ModuleName
	if (-not (Test-Path $moduleDir)) {
		return
	}

	foreach ($artifact in @('dll', 'pdb', 'map', 'bsc')) {
		$sourcePath = Join-Path $moduleDir "$ModuleName.$artifact"
		if (-not (Test-Path $sourcePath)) {
			continue
		}

		$destinationPath = Join-Path $RuntimeBaseq3Dir "$ModuleName.$artifact"
		Copy-Item -Path $sourcePath -Destination $destinationPath -Force
	}
}

if (-not (Test-Path $runtimeBaseq3Dir)) {
	New-Item -ItemType Directory -Path $runtimeBaseq3Dir | Out-Null
}

if ($pythonCmd) {
	Write-Host "Refreshing staged retail UI bundle..."
	$pythonArgs = @(
		$uiBundleBuilder,
		'--runtime-root',
		$runtimeBaseq3Dir
	)
	if ($pythonCmd.Name -ieq 'py.exe' -or $pythonCmd.Name -ieq 'py') {
		$pythonArgs = @('-3') + $pythonArgs
	}
	& $pythonCmd.Source @pythonArgs
	$uiBundleExitCode = $LASTEXITCODE
	if ($uiBundleExitCode -ne 0) {
		exit $uiBundleExitCode
	}
} else {
	Write-Warning "Python was not found; skipping tools/build_ui_bundle.py refresh. Launches may use stale staged UI content."
}

Sync-ModuleRuntimeArtifacts -ModuleName 'cgamex86' -RuntimeBaseq3Dir $runtimeBaseq3Dir -ModulesDir $runtimeModulesDir
Sync-ModuleRuntimeArtifacts -ModuleName 'qagamex86' -RuntimeBaseq3Dir $runtimeBaseq3Dir -ModulesDir $runtimeModulesDir

$clientExe = Join-Path $runtimeBinDir 'quakelive_steam.exe'
$dedicatedExe = Join-Path $runtimeBinDir 'qzeroded.exe'
if (Test-Path $clientExe) {
	Copy-Item -Path $clientExe -Destination $dedicatedExe -Force

	$symbolAliases = @(
		@{ Source = 'quakelive_steam.pdb'; Destination = 'qzeroded.pdb' },
		@{ Source = 'quakelive_steam.map'; Destination = 'qzeroded.map' }
	)
	foreach ($alias in $symbolAliases) {
		$sourcePath = Join-Path $runtimeBinDir $alias.Source
		if (Test-Path $sourcePath) {
			Copy-Item -Path $sourcePath -Destination (Join-Path $runtimeBinDir $alias.Destination) -Force
		}
	}

	Write-Host "Emitted dedicated server alias: $dedicatedExe"
}
