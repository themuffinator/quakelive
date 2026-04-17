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
$stagedUiBundleRoot = [System.IO.Path]::GetFullPath((Join-Path $repoRoot 'build\ui_bundle\staging'))
$stagedUiBundleBaseq3 = Join-Path $stagedUiBundleRoot 'baseq3'
$runtimeUiPackage = Join-Path $runtimeBaseq3 'pak_uiql.pk3'

function Test-LaunchUiStagingRoot {
	param(
		[string]$Baseq3Root
	)

	foreach ($requiredRetailUiPath in @(
		$Baseq3Root,
		(Join-Path $Baseq3Root 'default.cfg'),
		(Join-Path $Baseq3Root 'ui\menudef.h'),
		(Join-Path $Baseq3Root 'ui\hud3.txt'),
		(Join-Path $Baseq3Root 'ui\ingame_scoreboard_ffa.menu'),
		(Join-Path $Baseq3Root 'ui\assets\button_back.png'),
		(Join-Path $Baseq3Root 'ui\assets\hud\ffa.png'),
		(Join-Path $Baseq3Root 'ui\assets\score\scoretl.png'),
		(Join-Path $Baseq3Root 'fonts\font.dat'),
		(Join-Path $Baseq3Root 'fonts\font.tga')
	)) {
		if (-not (Test-Path -LiteralPath $requiredRetailUiPath)) {
			return $false
		}
	}

	return $true
}

if (Test-LaunchUiStagingRoot -Baseq3Root $stagedUiBundleBaseq3) {
	$retailUiBundleRoot = $stagedUiBundleRoot
} elseif (Test-Path -LiteralPath $runtimeUiPackage) {
	$retailUiBundleRoot = $runtimeBinDir
} else {
	throw "Quake Live UI content was not found in either $stagedUiBundleBaseq3 or $runtimeUiPackage. Run the Build Debug task or tools/build_ui_bundle.py before launching."
}

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

function Sync-RuntimeUiPackages {
	param(
		[string]$RuntimeBaseq3Dir
	)

	$uiBundleBuilder = Join-Path $repoRoot 'tools\build_ui_bundle.py'
	$pythonCmd = Get-Command python -ErrorAction SilentlyContinue
	if (-not $pythonCmd) {
		$pythonCmd = Get-Command py -ErrorAction SilentlyContinue
	}

	if (-not $pythonCmd) {
		Write-Warning "Python was not found; skipping runtime UI PK3 refresh. Existing pak_uiql.pk3 artifacts will be reused if present."
		return
	}

	$pythonArgs = @(
		$uiBundleBuilder,
		'--runtime-root',
		$RuntimeBaseq3Dir
	)
	if ($pythonCmd.Name -ieq 'py.exe' -or $pythonCmd.Name -ieq 'py') {
		$pythonArgs = @('-3') + $pythonArgs
	}

	& $pythonCmd.Source @pythonArgs
	if ($LASTEXITCODE -ne 0) {
		throw "tools/build_ui_bundle.py failed while refreshing runtime UI packages."
	}
}

if (-not (Test-Path -LiteralPath $runtimeBaseq3)) {
	New-Item -ItemType Directory -Path $runtimeBaseq3 | Out-Null
}

Sync-RuntimeUiPackages -RuntimeBaseq3Dir $runtimeBaseq3

Sync-LaunchModuleArtifact -ModuleName 'cgamex86'
Sync-LaunchModuleArtifact -ModuleName 'qagamex86'

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
		'+set', 'ui_browserAwesomium', '1'
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
$env:QL_DISABLE_STEAMWORKS = '1'
if ($EnableAwesomium) {
	Remove-Item Env:QL_DISABLE_EXTERNAL_ECOSYSTEMS -ErrorAction SilentlyContinue
	Remove-Item Env:QL_DISABLE_AWESOMIUM -ErrorAction SilentlyContinue
} else {
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
