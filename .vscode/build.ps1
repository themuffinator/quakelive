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
	[string]$OpenSteam = '',
	[ValidateSet('0', '1')]
	[string]$RequireAwesomiumSdk = '',
	[string]$Targets = '',
	[string]$PlatformToolset = '',
	[string]$WindowsTargetPlatformVersion = '',
	[string]$BuildLogRoot = ''
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
$projectPlatformNormalized = $Platform
if ($projectPlatformNormalized -ieq 'x86') {
	$projectPlatformNormalized = 'Win32'
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

$toolset = $PlatformToolset
if (-not $toolset) {
	$toolset = $env:QLR_PLATFORM_TOOLSET
}
if (-not $toolset) {
	$toolset = $defaultToolset
}
$windowsTargetPlatformVersion = $WindowsTargetPlatformVersion
if (-not $windowsTargetPlatformVersion) {
	$windowsTargetPlatformVersion = $env:QLR_WINDOWS_TARGET_PLATFORM_VERSION
}
if (-not $windowsTargetPlatformVersion -and $toolset -eq 'v141') {
	$windowsTargetPlatformVersion = Get-LatestWindowsSdkVersion
}

$solutionPath = Resolve-Path $Solution
$solutionDir = Split-Path -Parent $solutionPath
$repoRoot = [System.IO.Path]::GetFullPath((Join-Path $scriptRoot '..'))
$repoLibsDir = Join-Path $repoRoot 'src\libs'
$internalDepsScript = Join-Path $scriptRoot '..\tools\build_internal_deps.ps1'
$explicitProjectTargetMap = @{
	'splines' = 'splines\Splines.vcxproj'
	'botlib' = 'botlib\botlib.vcxproj'
	'cgame' = 'cgame\cgame.vcxproj'
	'game' = 'game\game.vcxproj'
	'quakelive_steam' = 'quakelive_steam.vcxproj'
	'awesomium_process' = 'awesomium_process.vcxproj'
	'renderer' = 'renderer\renderer.vcxproj'
	'ui' = 'ui\ui.vcxproj'
	'qagamex86' = 'game\qagamex86.vcxproj'
	'cgamex86' = 'cgame\cgamex86.vcxproj'
}

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
		'-RepoRoot', $repoRoot,
		'-Dependency', $DependencyName,
		'-Configuration', $Configuration
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
$pngDebugPostfix = if ($Configuration -match '^Debug') { 'd' } else { '' }
$pngStaticLibrary = "libpng16_static$pngDebugPostfix.lib"
$zlibStaticLibrary = "zlibstatic$pngDebugPostfix.lib"

$FreeTypeSdkDir = Join-Path $repoLibsDir 'freetype'
$FreeTypeIncludeDir = ''
$FreeTypeLibDir = ''
$FreeTypeLibrary = $null
$FreeTypeSource = ''
$FreeTypeLibraryCandidates = @('freetype.lib', 'libfreetype.lib')

$enableOgg = $env:QLEnableOgg
$bootstrapOgg = (-not $enableOgg) -or ([int]$enableOgg -ne 0)
if ($bootstrapOgg) {
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
$bootstrapPng = (-not $enablePng) -or ([int]$enablePng -ne 0)
if ($bootstrapPng) {
	Invoke-InternalDependencyBootstrap -DependencyName 'png'
}

$pngAvailable = (Test-Path $pngHeader) -and
	(Test-Path (Join-Path $pngLibDir $pngStaticLibrary)) -and
	(Test-Path (Join-Path $pngLibDir $zlibStaticLibrary))
if (-not $enablePng) {
	$enablePng = if ($pngAvailable) { 1 } else { 0 }
} else {
	$enablePng = [int]$enablePng
}
if ($enablePng -eq 0 -and $pngAvailable) {
	Write-Warning "QLEnablePng was forced to 0 but repo-managed libpng is available. Enabling PNG to avoid blank UI assets."
	$enablePng = 1
}

$enableFreeType = $env:QLEnableFreeType
$bootstrapFreeType = (-not $enableFreeType) -or ([int]$enableFreeType -ne 0)
if ($bootstrapFreeType) {
	Invoke-InternalDependencyBootstrap -DependencyName 'freetype'
}

foreach ($candidateIncludeDir in @(
	(Join-Path $FreeTypeSdkDir 'include\freetype2'),
	(Join-Path $FreeTypeSdkDir 'include')
)) {
	if (Test-Path (Join-Path $candidateIncludeDir 'ft2build.h')) {
		$FreeTypeIncludeDir = $candidateIncludeDir
		break
	}
}

foreach ($candidateLibDir in @(
	(Join-Path $FreeTypeSdkDir 'lib\Win32'),
	(Join-Path $FreeTypeSdkDir 'lib')
)) {
	$library = $FreeTypeLibraryCandidates |
		Where-Object { Test-Path (Join-Path $candidateLibDir $_) } |
		Select-Object -First 1
	if ($library -and $FreeTypeIncludeDir -and (Test-Path (Join-Path $FreeTypeIncludeDir 'ft2build.h'))) {
		$FreeTypeLibDir = $candidateLibDir
		$FreeTypeLibrary = $library
		$FreeTypeSource = 'repo-managed FreeType tree'
		break
	}
}

$freeTypeHeader = Join-Path $FreeTypeIncludeDir 'ft2build.h'
$freeTypeAvailable = (Test-Path $freeTypeHeader) -and ($null -ne $FreeTypeLibrary)
if (-not $enableFreeType) {
	$enableFreeType = if ($freeTypeAvailable) { 1 } else { 0 }
} else {
	$enableFreeType = [int]$enableFreeType
}
if ($enableFreeType -eq 0 -and $freeTypeAvailable) {
	Write-Warning "QLEnableFreeType was forced to 0 but repo-managed FreeType is available. Enabling FreeType to keep retail font rendering enabled."
	$enableFreeType = 1
}

$requestedBuildTargets = @()
$explicitProjectTargets = @()
$unmappedBuildTargets = @()
if ($Targets) {
	$requestedBuildTargets = @(
		$Targets -split ';' |
			ForEach-Object { $_.Trim() } |
			Where-Object { $_ }
	)

	foreach ($targetName in $requestedBuildTargets) {
		$targetKey = $targetName.ToLowerInvariant()
		if ($explicitProjectTargetMap.ContainsKey($targetKey)) {
			$explicitProjectTargets += [PSCustomObject]@{
				Name = $targetName
				Path = Join-Path $solutionDir $explicitProjectTargetMap[$targetKey]
			}
		} else {
			$unmappedBuildTargets += $targetName
		}
	}
}
$buildExplicitProjectTargets = $requestedBuildTargets.Count -gt 0 -and $unmappedBuildTargets.Count -eq 0

$msbuildArgs = @(
	$solutionPath,
	'/m',
	'/nr:false',
	"/p:Configuration=$Configuration",
	"/p:Platform=$platformNormalized"
)
$projectMsbuildArgs = @(
	'/m',
	'/nr:false',
	"/p:Configuration=$Configuration",
	"/p:Platform=$projectPlatformNormalized"
)
if ($Targets -and -not $buildExplicitProjectTargets) {
	$msbuildArgs += "/t:$Targets"
}
if ($toolset) {
	$msbuildArgs += "/p:PlatformToolset=$toolset"
	$projectMsbuildArgs += "/p:PlatformToolset=$toolset"
}
if ($windowsTargetPlatformVersion) {
	$msbuildArgs += "/p:WindowsTargetPlatformVersion=$windowsTargetPlatformVersion"
	$projectMsbuildArgs += "/p:WindowsTargetPlatformVersion=$windowsTargetPlatformVersion"
}
if ($OnlineServices -ne '') {
	$msbuildArgs += "/p:QLBuildOnlineServices=$OnlineServices"
	$projectMsbuildArgs += "/p:QLBuildOnlineServices=$OnlineServices"
}
if ($Steamworks -ne '') {
	$msbuildArgs += "/p:QLBuildSteamworks=$Steamworks"
	$projectMsbuildArgs += "/p:QLBuildSteamworks=$Steamworks"
}
if ($OpenSteam -ne '') {
	$msbuildArgs += "/p:QLBuildOpenSteam=$OpenSteam"
	$projectMsbuildArgs += "/p:QLBuildOpenSteam=$OpenSteam"
}
if ($RequireAwesomiumSdk -ne '') {
	$msbuildArgs += "/p:QLRequireAwesomiumSdk=$RequireAwesomiumSdk"
	$projectMsbuildArgs += "/p:QLRequireAwesomiumSdk=$RequireAwesomiumSdk"
}
if ($enableOgg -ne $null) {
	$msbuildArgs += "/p:QLEnableOgg=$enableOgg"
	$projectMsbuildArgs += "/p:QLEnableOgg=$enableOgg"
}
if ($enablePng -ne $null) {
	$msbuildArgs += "/p:QLEnablePng=$enablePng"
	$projectMsbuildArgs += "/p:QLEnablePng=$enablePng"
}
if ($enableFreeType -ne $null) {
	$msbuildArgs += "/p:QLEnableFreeType=$enableFreeType"
	$projectMsbuildArgs += "/p:QLEnableFreeType=$enableFreeType"
}

if ($BuildLogRoot) {
	New-Item -ItemType Directory -Force -Path $BuildLogRoot | Out-Null
	$safeConfiguration = $Configuration -replace '[^A-Za-z0-9_.-]', '-'
	$safePlatform = $platformNormalized -replace '[^A-Za-z0-9_.-]', '-'
	$safeToolset = if ($toolset) { $toolset -replace '[^A-Za-z0-9_.-]', '-' } else { 'default' }
	$msbuildLog = Join-Path $BuildLogRoot "msbuild-${safeConfiguration}-${safePlatform}-${safeToolset}.log"
	$msbuildArgs += @(
		'/clp:Summary;Verbosity=minimal',
		"/flp:logfile=$msbuildLog;verbosity=normal;encoding=UTF-8"
	)
	$projectMsbuildArgs += @(
		'/clp:Summary;Verbosity=minimal',
		"/flp:logfile=$msbuildLog;verbosity=normal;encoding=UTF-8"
	)
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
if ($RequireAwesomiumSdk -ne '') {
	Write-Host "QLRequireAwesomiumSdk: $RequireAwesomiumSdk"
}
if ($Targets) {
	Write-Host "MSBuild targets: $Targets"
	if ($buildExplicitProjectTargets) {
		Write-Host "Resolved MSBuild project targets: $($explicitProjectTargets.Name -join ';')"
	} elseif ($unmappedBuildTargets.Count -gt 0) {
		Write-Host "Using solution target fallback for unmapped targets: $($unmappedBuildTargets -join ';')"
	}
}
Write-Host "QLEnableOgg: $enableOgg (available: $oggAvailable)"
Write-Host "Vorbis include: $vorbisIncludeDir"
Write-Host "Vorbis library dir: $vorbisLibDir"
Write-Host "QLEnablePng: $enablePng (available: $pngAvailable)"
if ($pngSource) {
	Write-Host "PNG source: $pngSource"
	Write-Host "PNG include: $pngInclude"
	Write-Host "PNG library dir: $pngLibDir"
	Write-Host "PNG static libraries: $pngStaticLibrary, $zlibStaticLibrary"
}
Write-Host "QLEnableFreeType: $enableFreeType (available: $freeTypeAvailable)"
if ($freeTypeAvailable) {
	Write-Host "FreeType source: $FreeTypeSource"
	Write-Host "FreeType include: $FreeTypeIncludeDir"
	Write-Host "FreeType library: $(Join-Path $FreeTypeLibDir $FreeTypeLibrary)"
}

if ($buildExplicitProjectTargets) {
	foreach ($target in $explicitProjectTargets) {
		Write-Host "Building project target $($target.Name): $($target.Path)"
		& $msbuildPath $target.Path @projectMsbuildArgs
		$buildExitCode = $LASTEXITCODE
		if ($buildExitCode -ne 0) {
			exit $buildExitCode
		}
	}
	$buildExitCode = 0
} else {
	& $msbuildPath @msbuildArgs
	$buildExitCode = $LASTEXITCODE
}

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
		$runtimeBinDir = Join-Path $repoRoot "build\win32\$Configuration\bin"
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

$runtimeBinDir = Join-Path $repoRoot "build\win32\$Configuration\bin"
$runtimeBaseq3Dir = Join-Path $runtimeBinDir 'baseq3'
$runtimeModulesDir = Join-Path $repoRoot "build\win32\$Configuration\modules"

if (-not (Test-Path $runtimeBinDir)) {
	New-Item -ItemType Directory -Path $runtimeBinDir | Out-Null
}

foreach ($staleCodecDll in @(
		'ogg.dll',
		'vorbis.dll',
		'vorbisenc.dll',
		'vorbisfile.dll',
		'libpng16.dll',
		'zlib1.dll'
	)) {
	$staleCodecPath = Join-Path $runtimeBinDir $staleCodecDll
	if (Test-Path -LiteralPath $staleCodecPath) {
		Remove-Item -LiteralPath $staleCodecPath -Force
	}
}

$buildSettingsPath = Join-Path $runtimeBinDir 'ql_build_settings.txt'
$onlineServicesSetting = if ($OnlineServices -ne '') { $OnlineServices } else { '0' }
$steamworksSetting = if ($Steamworks -ne '') { $Steamworks } else { '0' }
$openSteamSetting = if ($OpenSteam -ne '') { $OpenSteam } else { '0' }
$requireAwesomiumSdkSetting = if ($RequireAwesomiumSdk -ne '') { $RequireAwesomiumSdk } else { '1' }
@(
	"Configuration=$Configuration",
	"Platform=$platformNormalized",
	"QLBuildOnlineServices=$onlineServicesSetting",
	"QLBuildSteamworks=$steamworksSetting",
	"QLBuildOpenSteam=$openSteamSetting",
	"QLRequireAwesomiumSdk=$requireAwesomiumSdkSetting",
	"QLEnableOgg=$enableOgg",
	"QLEnablePng=$enablePng",
	"QLEnableFreeType=$enableFreeType"
) | Set-Content -Path $buildSettingsPath -Encoding ASCII

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

function Resolve-RetailBasePath {
	$steamBasePath = $env:QLR_STEAM_BASEPATH
	if (-not $steamBasePath) {
		$steamBasePath = 'C:\Program Files (x86)\Steam\steamapps\common\Quake Live'
	}

	return [System.IO.Path]::GetFullPath($steamBasePath)
}

function Sync-AwesomiumRuntime {
	param(
		[string]$SourceRoot,
		[string]$DestinationRoot
	)

	$requiredFiles = @(
		'awesomium.dll',
		'awesomium_process.exe',
		'web.pak',
		'icudt.dll',
		'libEGL.dll',
		'libGLESv2.dll',
		'avcodec-53.dll',
		'avformat-53.dll',
		'avutil-51.dll',
		'xinput9_1_0.dll'
	)

	$retailPakPath = Join-Path $SourceRoot 'baseq3\pak00.pk3'
	if (-not (Test-Path -LiteralPath $SourceRoot -PathType Container)) {
		throw "Awesomium online build requested, but Quake Live base path was not found: $SourceRoot. Set QLR_STEAM_BASEPATH to the Steam install root."
	}

	if (-not (Test-Path -LiteralPath $retailPakPath -PathType Leaf)) {
		throw "Awesomium online build requested, but the Quake Live base path is missing retail data: $retailPakPath."
	}

	if (-not (Test-Path -LiteralPath $DestinationRoot -PathType Container)) {
		New-Item -ItemType Directory -Path $DestinationRoot | Out-Null
	}

	foreach ($fileName in $requiredFiles) {
		$sourcePath = Join-Path $SourceRoot $fileName
		$destinationPath = Join-Path $DestinationRoot $fileName

		if (-not (Test-Path -LiteralPath $sourcePath -PathType Leaf)) {
			throw "Awesomium runtime dependency was not found: $sourcePath"
		}

		$shouldCopy = $true
		if (Test-Path -LiteralPath $destinationPath -PathType Leaf) {
			$sourceInfo = Get-Item -LiteralPath $sourcePath
			$destinationInfo = Get-Item -LiteralPath $destinationPath
			$shouldCopy = $sourceInfo.Length -ne $destinationInfo.Length -or
				$sourceInfo.LastWriteTimeUtc -gt $destinationInfo.LastWriteTimeUtc
		}

		if ($shouldCopy) {
			Copy-Item -LiteralPath $sourcePath -Destination $destinationPath -Force
		}
	}

	Write-Host "Synced Awesomium runtime dependencies from $SourceRoot"
}

if (-not (Test-Path $runtimeBaseq3Dir)) {
	New-Item -ItemType Directory -Path $runtimeBaseq3Dir | Out-Null
}

foreach ($staleUiPackage in @(
		(Join-Path $runtimeBaseq3Dir 'pak_uiql.pk3'),
		(Join-Path $runtimeBaseq3Dir 'pak_ui_src_retail_overlay.pk3')
	)) {
	if (Test-Path -LiteralPath $staleUiPackage) {
		Remove-Item -LiteralPath $staleUiPackage -Force
	}
}
Write-Host "Retail UI assets are loaded from the Quake Live installation; no local UI PK3 is generated."

Sync-ModuleRuntimeArtifacts -ModuleName 'cgamex86' -RuntimeBaseq3Dir $runtimeBaseq3Dir -ModulesDir $runtimeModulesDir
Sync-ModuleRuntimeArtifacts -ModuleName 'qagamex86' -RuntimeBaseq3Dir $runtimeBaseq3Dir -ModulesDir $runtimeModulesDir

if ($onlineServicesSetting -eq '1') {
	$steamBasePath = Resolve-RetailBasePath
	Sync-AwesomiumRuntime -SourceRoot $steamBasePath -DestinationRoot $runtimeBinDir
}

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
