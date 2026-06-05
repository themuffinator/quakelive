[CmdletBinding()]
param(
	[string]$Configuration = 'Debug',
	[string]$BasePath = '',
	[switch]$EnableAwesomium,
	[string[]]$ExtraArgs = @()
)

$scriptRoot = $PSScriptRoot
if (-not $scriptRoot) {
	$scriptRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
}

$repoRoot = [System.IO.Path]::GetFullPath((Join-Path $scriptRoot '..'))
$runtimeBinDir = Join-Path $repoRoot "build\win32\$Configuration\bin"
$program = Join-Path $runtimeBinDir 'quakelive_steam.exe'

if (-not (Test-Path $program)) {
	throw "Launch target was not found: $program. Run the Build Debug task first."
}

function Get-LaunchSafeArgument {
	param([string]$Path)

	if ([string]::IsNullOrWhiteSpace($Path)) {
		return ''
	}

	$command = 'for %I in ("' + $Path + '") do @echo %~sI'
	$shortPath = (& cmd /c $command 2>$null | Select-Object -First 1).Trim()
	if (-not [string]::IsNullOrWhiteSpace($shortPath) -and $shortPath -notmatch '\s') {
		return $shortPath
	}

	return $Path
}

function Format-LaunchArgument {
	param([string]$Argument)

	if ($null -eq $Argument) {
		return '""'
	}

	if ($Argument -notmatch '[\s"]') {
		return $Argument
	}

	$escaped = $Argument -replace '(\\*)"', '$1$1\"'
	$escaped = $escaped -replace '(\\+)$', '$1$1'
	return '"' + $escaped + '"'
}

$steamBasePath = $BasePath
if (-not $steamBasePath) {
	$steamBasePath = $env:QLR_STEAM_BASEPATH
}
if (-not $steamBasePath) {
	$steamBasePath = 'C:\Program Files (x86)\Steam\steamapps\common\Quake Live'
}
$steamBasePath = [System.IO.Path]::GetFullPath($steamBasePath)
$retailPakPath = Join-Path $steamBasePath 'baseq3\pak00.pk3'

if (-not (Test-Path $steamBasePath -PathType Container)) {
	throw "Quake Live base path was not found: $steamBasePath. Update .vscode\\launch.json or set QLR_STEAM_BASEPATH."
}

if (-not (Test-Path $retailPakPath -PathType Leaf)) {
	throw "Quake Live base path is missing retail data: $retailPakPath. Point the launcher at the Steam install root that contains baseq3\\pak00.pk3."
}

$workingDirectory = $runtimeBinDir
$steamBasePathArg = Get-LaunchSafeArgument -Path $steamBasePath
$runtimeBaseq3 = Join-Path $runtimeBinDir 'baseq3'
$runtimeModulesDir = Join-Path $repoRoot "build\win32\$Configuration\modules"
$retailUiBundleRoot = $steamBasePath

$retailUiBundleRootArg = Get-LaunchSafeArgument -Path $retailUiBundleRoot
$runtimeBinDirArg = Get-LaunchSafeArgument -Path $runtimeBinDir

function Sync-LaunchModuleArtifact {
	param(
		[string]$ModuleName
	)

	$moduleDir = Join-Path $runtimeModulesDir $ModuleName
	if (-not (Test-Path -LiteralPath $moduleDir)) {
		return
	}

	foreach ($artifact in @('dll', 'pdb', 'map', 'bsc')) {
		$sourcePath = Join-Path $moduleDir "$ModuleName.$artifact"
		if (-not (Test-Path -LiteralPath $sourcePath)) {
			continue
		}

		$destinationPath = Join-Path $runtimeBaseq3 "$ModuleName.$artifact"
		$shouldCopy = $true
		if (Test-Path -LiteralPath $destinationPath) {
			$sourceInfo = Get-Item -LiteralPath $sourcePath
			$destinationInfo = Get-Item -LiteralPath $destinationPath
			$shouldCopy = $sourceInfo.LastWriteTimeUtc -gt $destinationInfo.LastWriteTimeUtc -or
				$sourceInfo.Length -ne $destinationInfo.Length
		}

		if ($shouldCopy) {
			Copy-Item -LiteralPath $sourcePath -Destination $destinationPath -Force
		}
	}
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
}

function Read-BuildSettings {
	param([string]$Path)

	$settings = @{}
	if (-not (Test-Path -LiteralPath $Path -PathType Leaf)) {
		return $settings
	}

	foreach ($line in Get-Content -LiteralPath $Path) {
		$separator = $line.IndexOf('=')
		if ($separator -le 0) {
			continue
		}

		$key = $line.Substring(0, $separator)
		$value = $line.Substring($separator + 1)
		$settings[$key] = $value
	}

	return $settings
}

function Assert-AwesomiumEnabledBuild {
	param([string]$RuntimeBinDir)

	$buildSettingsPath = Join-Path $RuntimeBinDir 'ql_build_settings.txt'
	$settings = Read-BuildSettings -Path $buildSettingsPath
	if (-not $settings.ContainsKey('QLBuildOnlineServices')) {
		throw "Awesomium launch requested, but build settings were not found at $buildSettingsPath. Run the Launch Debug Awesomium task so the client is rebuilt with QLBuildOnlineServices=1."
	}

	if ($settings['QLBuildOnlineServices'] -ne '1') {
		throw "Awesomium launch requested, but the last build for $RuntimeBinDir used QLBuildOnlineServices=$($settings['QLBuildOnlineServices']). Run the Launch Debug Awesomium task or rebuild with -OnlineServices 1 before launching."
	}
}

if (-not (Test-Path -LiteralPath $runtimeBaseq3)) {
	New-Item -ItemType Directory -Path $runtimeBaseq3 | Out-Null
}

foreach ($staleUiPackage in @(
		(Join-Path $runtimeBaseq3 'pak_uiql.pk3'),
		(Join-Path $runtimeBaseq3 'pak_ui_src_retail_overlay.pk3')
	)) {
	if (Test-Path -LiteralPath $staleUiPackage) {
		Remove-Item -LiteralPath $staleUiPackage -Force
	}
}

Sync-LaunchModuleArtifact -ModuleName 'cgamex86'
Sync-LaunchModuleArtifact -ModuleName 'qagamex86'

if ($EnableAwesomium) {
	Assert-AwesomiumEnabledBuild -RuntimeBinDir $runtimeBinDir
	Sync-AwesomiumRuntime -SourceRoot $steamBasePath -DestinationRoot $runtimeBinDir
}

$arguments = @(
	'+set', 'developer', '1',
	'+set', 'logfile', '2',
	'+set', 'g_logfile', '1',
	'+set', 'com_noErrorInterrupt', '1',
	'+set', 'fs_basepath', $steamBasePathArg,
	'+set', 'fs_cdpath', $retailUiBundleRootArg,
	'+set', 'fs_homepath', $runtimeBinDirArg,
	'+set', 'r_fullscreen', '0',
	'+set', 'r_ext_multitexture', '0'
)

if ($EnableAwesomium) {
	$arguments += @(
		'+set', 'ui_browserAwesomium', '1',
		'+set', 'qlr_requireAwesomium', '1'
	)
} else {
	$arguments += @(
		'+set', 'ui_browserAwesomium', '0',
		'+set', 'web_browserActive', '0'
	)
}

if ($ExtraArgs.Count -gt 0) {
	$arguments += $ExtraArgs
}

$env:QLR_DUMP_PATH = Join-Path $repoRoot "build\win32\$Configuration\dumps"
$env:QLR_FULL_DUMP = '1'
if ($EnableAwesomium) {
	Remove-Item Env:QL_DISABLE_EXTERNAL_ECOSYSTEMS -ErrorAction SilentlyContinue
	Remove-Item Env:QL_DISABLE_AWESOMIUM -ErrorAction SilentlyContinue
	Remove-Item Env:QL_DISABLE_STEAMWORKS -ErrorAction SilentlyContinue
} else {
	$env:QL_DISABLE_STEAMWORKS = '1'
	$env:QL_DISABLE_EXTERNAL_ECOSYSTEMS = '1'
	$env:QL_DISABLE_AWESOMIUM = '1'
}

Write-Host "Launching: $program"
Write-Host "Working directory: $workingDirectory"
Write-Host "Retail base path: $steamBasePath"
Write-Host "UI content root: $retailUiBundleRoot"
Write-Host "Awesomium enabled: $EnableAwesomium"
$commandLine = ($arguments | ForEach-Object { Format-LaunchArgument $_ }) -join ' '
Write-Host "Arguments: $commandLine"

Push-Location $workingDirectory
try {
	$process = Start-Process -FilePath $program -WorkingDirectory $workingDirectory -ArgumentList $commandLine -PassThru
	Write-Host "quakelive_steam.exe PID: $($process.Id)"
	Wait-Process -Id $process.Id
	$process.Refresh()
	exit $process.ExitCode
} finally {
	Pop-Location
}
