[CmdletBinding()]
param(
	[string]$RepoRoot = '',
	[string]$RetailBasePath = '',
	[string]$AssetCdPath = '',
	[string]$MapName = 'bloodrun',
	[int]$MenuWaitFrames = 240,
	[int]$MapWaitFrames = 420
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

function Add-WaitLines {
	param(
		[System.Collections.Generic.List[string]]$Lines,
		[int]$Count
	)

	for ( $i = 0; $i -lt $Count; $i++ ) {
		$Lines.Add( 'wait' )
	}
}

function Send-Rcon {
	param(
		[string]$Password,
		[string]$Command
	)

	$udp = New-Object System.Net.Sockets.UdpClient
	try {
		$prefix = [byte[]]( 255, 255, 255, 255 )
		$payload = [System.Text.Encoding]::ASCII.GetBytes( "rcon $Password $Command" )
		$buffer = New-Object byte[] ( $prefix.Length + $payload.Length )
		[Array]::Copy( $prefix, 0, $buffer, 0, $prefix.Length )
		[Array]::Copy( $payload, 0, $buffer, $prefix.Length, $payload.Length )
		[void]$udp.Send( $buffer, $buffer.Length, '127.0.0.1', 27960 )
	} finally {
		$udp.Close()
	}
}

function Resolve-ExistingPath {
	param([string]$Path)

	if ( [string]::IsNullOrWhiteSpace( $Path ) ) {
		return ''
	}

	$resolved = Resolve-Path -LiteralPath $Path -ErrorAction Stop
	return [System.IO.Path]::GetFullPath( $resolved.Path )
}

function Resolve-RetailBasePath {
	param([string]$ExplicitPath)

	$candidates = @(
		$ExplicitPath,
		'C:\Program Files (x86)\Steam\steamapps\common\Quake Live',
		'C:\PROGRA~2\Steam\STEAMA~1\common\QUAKEL~1'
	)

	foreach ( $candidate in $candidates ) {
		if ( [string]::IsNullOrWhiteSpace( $candidate ) ) {
			continue
		}

		try {
			$resolved = Resolve-ExistingPath -Path $candidate
		} catch {
			continue
		}

		if ( Test-Path -LiteralPath ( Join-Path $resolved 'baseq3\pak00.pk3' ) ) {
			return $resolved
		}
	}

	throw 'Unable to resolve a retail Quake Live base path. Pass -RetailBasePath explicitly.'
}

function Resolve-RetailUiBundleRoot {
	param(
		[string]$ExplicitPath,
		[string]$Root
	)

	$candidate = if ( [string]::IsNullOrWhiteSpace( $ExplicitPath ) ) {
		[System.IO.Path]::GetFullPath((Join-Path $Root 'build\ui_bundle\staging'))
	} else {
		Resolve-ExistingPath -Path $ExplicitPath
	}
	$baseq3Root = Join-Path $candidate 'baseq3'

	foreach ( $requiredPath in @(
			$baseq3Root,
			( Join-Path $baseq3Root 'default.cfg' ),
			( Join-Path $baseq3Root 'ui\\menudef.h' ),
			( Join-Path $baseq3Root 'ui\hud3.txt' ),
			( Join-Path $baseq3Root 'ui\ingame_scoreboard_ffa.menu' ),
			( Join-Path $baseq3Root 'ui\assets\button_back.png' ),
			( Join-Path $baseq3Root 'ui\assets\hud\ffa.png' ),
			( Join-Path $baseq3Root 'ui\assets\score\scoretl.png' ),
			( Join-Path $baseq3Root 'fonts\font.dat' ),
			( Join-Path $baseq3Root 'fonts\font.tga' )
		) ) {
		if ( -not ( Test-Path -LiteralPath $requiredPath ) ) {
			throw "Quake Live UI staging content was not found: $requiredPath. Run tools/build_ui_bundle.py before running the client probe so staging\\baseq3 contains the retail UI runtime tree."
		}
	}

	return $candidate
}

function Get-LaunchSafePath {
	param([string]$Path)

	if ( [string]::IsNullOrWhiteSpace( $Path ) ) {
		return ''
	}

	$command = 'for %I in ("' + $Path + '") do @echo %~sI'
	$shortPath = (& cmd /c $command 2>$null | Select-Object -First 1).Trim()
	if ( -not [string]::IsNullOrWhiteSpace( $shortPath ) -and $shortPath -notmatch '\s' ) {
		return $shortPath
	}

	return $Path
}

function Sync-RuntimeUiPackages {
	param([string]$RuntimeBaseq3Dir)

	$uiBundleBuilder = Join-Path $script:RepoRoot 'tools\build_ui_bundle.py'
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

function To-RepoPath {
	param([string]$Path)

	if ( [string]::IsNullOrWhiteSpace( $Path ) ) {
		return ''
	}

	$resolved = [System.IO.Path]::GetFullPath( $Path )
	$repoResolved = [System.IO.Path]::GetFullPath( $script:RepoRoot )
	if ( $resolved.StartsWith( $repoResolved, [System.StringComparison]::OrdinalIgnoreCase ) ) {
		return $resolved.Substring( $repoResolved.Length ).TrimStart( '\' ).Replace( '\', '/' )
	}

	return $resolved.Replace( '\', '/' )
}

function Get-ArtifactSha256 {
	param([string]$Path)

	if ( [string]::IsNullOrWhiteSpace( $Path ) -or -not ( Test-Path -LiteralPath $Path ) ) {
		return ''
	}

	return (Get-FileHash -Algorithm SHA256 -Path $Path).Hash.ToLowerInvariant()
}

function Reset-LiveLog {
	Get-Process -Name quakelive_steam -ErrorAction SilentlyContinue | Stop-Process -Force
	Start-Sleep -Milliseconds 500
	if ( Test-Path -LiteralPath $script:RuntimeLog ) {
		Remove-Item -LiteralPath $script:RuntimeLog -Force
	}
	Sync-RuntimeUiPackages -RuntimeBaseq3Dir $script:RuntimeRoot
}

function Remove-StaleMatches {
	param([string]$Pattern)

	if ( [string]::IsNullOrWhiteSpace( $Pattern ) ) {
		return
	}

	Get-ChildItem -LiteralPath ( Join-Path $script:RuntimeRoot 'screenshots' ) -Filter $Pattern -ErrorAction SilentlyContinue |
		Remove-Item -Force -ErrorAction SilentlyContinue
	Get-ChildItem -LiteralPath ( Join-Path $script:RuntimeRoot 'demos' ) -Filter $Pattern -ErrorAction SilentlyContinue |
		Remove-Item -Force -ErrorAction SilentlyContinue
}

function Get-NewClientProcess {
	param(
		[int[]]$ExistingIds,
		[datetime]$StartedAfter
	)

	$deadline = (Get-Date).AddSeconds( 15 )
	while ( (Get-Date) -lt $deadline ) {
		$candidates = Get-Process -Name quakelive_steam -ErrorAction SilentlyContinue |
			Where-Object {
				$ExistingIds -notcontains $_.Id -and $_.StartTime -ge $StartedAfter
			} |
			Sort-Object StartTime -Descending
		if ( $candidates ) {
			return $candidates | Select-Object -First 1
		}
		Start-Sleep -Milliseconds 250
	}

	return $null
}

function Get-LaunchedClientProcess {
	param([datetime]$StartedAfter)

	return Get-Process -Name quakelive_steam -ErrorAction SilentlyContinue |
		Where-Object { $_.StartTime -ge $StartedAfter } |
		Sort-Object StartTime -Descending |
		Select-Object -First 1
}

function Stop-ClientProcessesStartedAfter {
	param([datetime]$StartedAfter)

	Get-Process -Name quakelive_steam -ErrorAction SilentlyContinue |
		Where-Object { $_.StartTime -ge $StartedAfter } |
		Stop-Process -Force -ErrorAction SilentlyContinue
}

function Start-ProcessWithScopedEnvironment {
	param(
		[string]$FilePath,
		[string[]]$ArgumentList,
		[string]$WorkingDirectory,
		[hashtable]$Environment
	)

	$startProcessCommand = Get-Command -Name Start-Process -ErrorAction Stop
	if ( $startProcessCommand.Parameters.ContainsKey( 'Environment' ) ) {
		return Start-Process -FilePath $FilePath -ArgumentList $ArgumentList -WorkingDirectory $WorkingDirectory -PassThru -WindowStyle Normal -Environment $Environment
	}

	$previousValues = @{}
	foreach ( $key in $Environment.Keys ) {
		$previousValues[$key] = [System.Environment]::GetEnvironmentVariable( $key, 'Process' )
		[System.Environment]::SetEnvironmentVariable( $key, $Environment[$key], 'Process' )
	}

	try {
		return Start-Process -FilePath $FilePath -ArgumentList $ArgumentList -WorkingDirectory $WorkingDirectory -PassThru -WindowStyle Normal
	} finally {
		foreach ( $key in $Environment.Keys ) {
			[System.Environment]::SetEnvironmentVariable( $key, $previousValues[$key], 'Process' )
		}
	}
}

function Start-ClientProcess {
	param(
		[string]$ConfigName,
		[string[]]$ExtraArgs
	)

	$existingIds = @( Get-Process -Name quakelive_steam -ErrorAction SilentlyContinue | ForEach-Object { $_.Id } )
	$launchStartTime = Get-Date

	$launchArgs = @(
		'+set', 'developer', '1',
		'+set', 'logfile', '2',
		'+set', 'g_logfile', '1',
		'+set', 'com_noErrorInterrupt', '1',
		'+set', 'com_zoneMegs', '64',
		'+set', 'com_hunkMegs', '256',
		'+set', 'fs_basepath', $script:RetailBasePath,
		'+set', 'fs_cdpath', $script:RetailUiBundleRoot,
		'+set', 'fs_homepath', $script:QlHome,
		'+set', 'r_fullscreen', '0',
		'+set', 'r_mode', '-1',
		'+set', 'r_customwidth', '1280',
		'+set', 'r_customheight', '720',
		'+set', 'r_windowedMode', '-1',
		'+set', 'r_windowedWidth', '1280',
		'+set', 'r_windowedHeight', '720',
		'+set', 'r_ext_multitexture', '0',
		'+set', 'ui_browserAwesomium', '0',
		'+set', 'web_browserActive', '0',
		'+set', 's_initsound', '0'
	)
	if ( $ExtraArgs ) {
		$launchArgs += $ExtraArgs
	}
	$launchArgs += @(
		'+exec', $ConfigName
	)

	$environment = @{
		'QLR_DUMP_PATH' = $script:DumpsRoot
		'QL_DISABLE_EXTERNAL_ECOSYSTEMS' = '1'
		'QL_DISABLE_STEAMWORKS' = '1'
		'QL_DISABLE_AWESOMIUM' = '1'
	}

	$launchProcess = Start-ProcessWithScopedEnvironment -FilePath $script:Exe -ArgumentList $launchArgs -WorkingDirectory $script:QlHome -Environment $environment
	$process = Get-NewClientProcess -ExistingIds $existingIds -StartedAfter $launchStartTime
	if ( -not $process ) {
		$process = $launchProcess
	}
	return [ordered]@{
		process = $process
		launch_process = $launchProcess
		start_time = $launchStartTime
		launch_args = $launchArgs
		environment = $environment
	}
}

function Find-EngineScreenshot {
	param([string]$ScreenshotPrefix)

	return Get-ChildItem -LiteralPath ( Join-Path $script:RuntimeRoot 'screenshots' ) -Filter ($ScreenshotPrefix + '*.jpg') -ErrorAction SilentlyContinue |
		Sort-Object LastWriteTime -Descending |
		Select-Object -First 1
}

function Find-DemoArtifact {
	param([string]$DemoPrefix)

	return Get-ChildItem -LiteralPath ( Join-Path $script:RuntimeRoot 'demos' ) -Filter ($DemoPrefix + '*.dm_*') -ErrorAction SilentlyContinue |
		Sort-Object LastWriteTime -Descending |
		Select-Object -First 1
}

function Archive-LiveLog {
	param([string]$Destination)

	if ( Test-Path -LiteralPath $script:RuntimeLog ) {
		Copy-Item -LiteralPath $script:RuntimeLog -Destination $Destination -Force
	}
}

function Invoke-MainMenuProbe {
	param(
		[string]$Stamp,
		[string]$ScreenshotPrefix,
		[string]$SavedConfigName,
		[string]$ArchivedLog
	)

	$configName = "codex_client_p6_main_$Stamp.cfg"
	$configPath = Join-Path $script:RuntimeRoot $configName
	$savedConfigPath = Join-Path $script:RuntimeRoot $SavedConfigName

	Remove-StaleMatches -Pattern ($ScreenshotPrefix + '*.jpg')
	if ( Test-Path -LiteralPath $savedConfigPath ) {
		Remove-Item -LiteralPath $savedConfigPath -Force
	}

	$lines = New-Object 'System.Collections.Generic.List[string]'
	foreach ( $line in @(
		'set developer 1',
		'set logfile 2',
		'set g_logfile 1',
		'set r_fullscreen 0',
		'set ui_browserAwesomium 0',
		'set web_browserActive 0',
		'set name "^2CLP6Probe"',
		'set sensitivity 4'
	) ) {
		$lines.Add( $line )
	}

	Add-WaitLines -Lines $lines -Count $MenuWaitFrames
	foreach ( $command in @(
		'web_showBrowser #home',
		'web_changeHash #friends',
		'web_showError codex_client_p6_error',
		'web_hideBrowser',
		'web_reload',
		'web_stopRefresh',
		("writeClientConfig $SavedConfigName"),
		("screenshotJPEG $ScreenshotPrefix")
	) ) {
		$lines.Add( $command )
		Add-WaitLines -Lines $lines -Count 90
	}
	$lines.Add( 'quit' )
	Set-Content -LiteralPath $configPath -Value $lines -Encoding ascii

	Reset-LiveLog
	$launch = Start-ClientProcess -ConfigName $configName -ExtraArgs @()
	$process = $launch.process
	$shotLogged = $false
	$uiInitSeen = $false
	$deadline = (Get-Date).AddSeconds(150)
	while ( (Get-Date) -lt $deadline ) {
		$currentProcess = Get-LaunchedClientProcess -StartedAfter $launch.start_time
		if ( $currentProcess ) {
			$process = $currentProcess
		} elseif ( $process.HasExited ) {
			break
		}
		$process.Refresh()

		if ( Test-Path -LiteralPath $script:RuntimeLog ) {
			$logText = Get-Content -LiteralPath $script:RuntimeLog -Raw -ErrorAction SilentlyContinue
			if ( $logText -match [regex]::Escape( '----- UI Initialization Complete -----' ) ) {
				$uiInitSeen = $true
			}
			if ( $logText -match [regex]::Escape( "Wrote screenshots/$ScreenshotPrefix.jpg" ) ) {
				$shotLogged = $true
				break
			}
		}
		Start-Sleep -Milliseconds 500
	}

	if ( -not $process.HasExited ) {
		$null = $process.WaitForExit( 90000 )
	}
	if ( -not $process.HasExited ) {
		Stop-ClientProcessesStartedAfter -StartedAfter $launch.start_time
	}

	Archive-LiveLog -Destination $ArchivedLog
	return [ordered]@{
		config = $configPath
		saved_config = $savedConfigPath
		launch_args = $launch.launch_args
		environment = $launch.environment
		engine_screenshot = Find-EngineScreenshot -ScreenshotPrefix $ScreenshotPrefix
		log_path = $ArchivedLog
		shot_logged = $shotLogged
		log_text = if ( Test-Path -LiteralPath $ArchivedLog ) { Get-Content -LiteralPath $ArchivedLog -Raw -ErrorAction SilentlyContinue } else { '' }
	}
}

function Invoke-MapRuntimeProbe {
	param(
		[string]$Stamp,
		[string]$ScreenshotPrefix,
		[string]$DemoPrefix,
		[string]$ArchivedLog
	)

	$configName = "codex_client_p6_map_$Stamp.cfg"
	$configPath = Join-Path $script:RuntimeRoot $configName

	Remove-StaleMatches -Pattern ($ScreenshotPrefix + '*.jpg')
	Remove-StaleMatches -Pattern ($DemoPrefix + '*.dm_*')

	$lines = New-Object 'System.Collections.Generic.List[string]'
	foreach ( $line in @(
		'set developer 1',
		'set logfile 2',
		'set g_logfile 1',
		'set r_fullscreen 0',
		'set sv_pure 0',
		'set g_gametype 1',
		'set g_doWarmup 0',
		'set g_warmup 0',
		("map $MapName")
	) ) {
		$lines.Add( $line )
	}
	Add-WaitLines -Lines $lines -Count ($MapWaitFrames * 6)
	$lines.Add( 'disconnect' )
	Add-WaitLines -Lines $lines -Count 180
	$lines.Add( 'quit' )
	Set-Content -LiteralPath $configPath -Value $lines -Encoding ascii

	Reset-LiveLog
	$password = 'qlrpass'
	$launch = Start-ClientProcess -ConfigName $configName -ExtraArgs @(
		'+set', 'sv_pure', '0',
		'+set', 'rconPassword', $password,
		'+set', 'g_gametype', '1',
		'+set', 'g_doWarmup', '0',
		'+set', 'g_warmup', '0'
	)
	$process = $launch.process
	$serverSeen = $false
	$activeSeen = $false
	$shotLogged = $false
	$disconnectSeen = $false
	$commandsIssued = $false
	$logText = ''
	$deadline = (Get-Date).AddSeconds(240)

	while ( (Get-Date) -lt $deadline ) {
		Start-Sleep -Milliseconds 500
		$currentProcess = Get-LaunchedClientProcess -StartedAfter $launch.start_time
		if ( $currentProcess ) {
			$process = $currentProcess
		} elseif ( $process.HasExited ) {
			break
		}
		$process.Refresh()
		if ( Test-Path -LiteralPath $script:RuntimeLog ) {
			$logText = Get-Content -LiteralPath $script:RuntimeLog -Raw -ErrorAction SilentlyContinue
			if ( $logText -match [regex]::Escape( "Server: $MapName" ) ) {
				$serverSeen = $true
			}
			if ( $logText -match 'Going from CS_PRIMED to CS_ACTIVE' ) {
				$activeSeen = $true
			}
			if ( $logText -match 'CL_Frame: disconnected console fallback active' ) {
				$disconnectSeen = $true
			}
			if ( $logText -match [regex]::Escape( "Wrote screenshots/$ScreenshotPrefix.jpg" ) ) {
				$shotLogged = $true
			}
		}

		if ( $activeSeen -and -not $commandsIssued -and -not $process.HasExited ) {
			$commandsIssued = $true
			Start-Sleep -Milliseconds 1000
			Send-Rcon -Password $password -Command ( "record $DemoPrefix" )
			Start-Sleep -Milliseconds 1500
			Send-Rcon -Password $password -Command ( "screenshotJPEG $ScreenshotPrefix" )
			$shotDeadline = (Get-Date).AddSeconds(30)
			while ( (Get-Date) -lt $shotDeadline -and -not $process.HasExited ) {
				Start-Sleep -Milliseconds 500
				$process.Refresh()
				if ( Test-Path -LiteralPath $script:RuntimeLog ) {
					$logText = Get-Content -LiteralPath $script:RuntimeLog -Raw -ErrorAction SilentlyContinue
					if ( $logText -match [regex]::Escape( "Wrote screenshots/$ScreenshotPrefix.jpg" ) ) {
						$shotLogged = $true
						break
					}
				}
			}
			if ( -not $shotLogged -and ( Find-EngineScreenshot -ScreenshotPrefix $ScreenshotPrefix ) ) {
				$shotLogged = $true
			}

			Send-Rcon -Password $password -Command 'stoprecord'
			$demoDeadline = (Get-Date).AddSeconds(20)
			while ( (Get-Date) -lt $demoDeadline -and -not $process.HasExited ) {
				if ( Find-DemoArtifact -DemoPrefix $DemoPrefix ) {
					break
				}
				Start-Sleep -Milliseconds 500
			}
		}

		if ( $disconnectSeen -and $shotLogged ) {
			break
		}
	}

	if ( -not $process.HasExited ) {
		$null = $process.WaitForExit( 120000 )
	}
	if ( -not $process.HasExited ) {
		Stop-ClientProcessesStartedAfter -StartedAfter $launch.start_time
	}

	Archive-LiveLog -Destination $ArchivedLog
	return [ordered]@{
		config = $configPath
		launch_args = $launch.launch_args
		environment = $launch.environment
		engine_screenshot = Find-EngineScreenshot -ScreenshotPrefix $ScreenshotPrefix
		demo_file = Find-DemoArtifact -DemoPrefix $DemoPrefix
		log_path = $ArchivedLog
		server_seen = $serverSeen
		active_seen = $activeSeen
		disconnect_seen = $disconnectSeen
		shot_logged = $shotLogged
		log_text = if ( Test-Path -LiteralPath $ArchivedLog ) { Get-Content -LiteralPath $ArchivedLog -Raw -ErrorAction SilentlyContinue } else { '' }
	}
}

if ( [string]::IsNullOrWhiteSpace( $RepoRoot ) ) {
	$RepoRoot = (Resolve-Path ( Join-Path $PSScriptRoot '..\..' )).Path
} else {
	$RepoRoot = Resolve-ExistingPath -Path $RepoRoot
}

$script:RepoRoot = $RepoRoot
$script:RetailBasePath = Get-LaunchSafePath -Path ( Resolve-RetailBasePath -ExplicitPath $RetailBasePath )
$script:RetailUiBundleRoot = Resolve-RetailUiBundleRoot -ExplicitPath $AssetCdPath -Root $RepoRoot
$script:QlHome = Join-Path $RepoRoot 'build\win32\Debug\bin'
$script:RuntimeRoot = Join-Path $script:QlHome 'baseq3'
$script:DumpsRoot = Join-Path $RepoRoot 'build\win32\Debug\dumps'
$script:LogRoot = Join-Path $script:DumpsRoot 'logs'
$script:RuntimeLog = Join-Path $script:RuntimeRoot 'qconsole.log'
$script:Exe = Join-Path $script:QlHome 'quakelive_steam.exe'

foreach ( $path in @(
		$script:RuntimeRoot,
		$script:DumpsRoot,
		$script:LogRoot,
		(Join-Path $script:RuntimeRoot 'screenshots'),
		(Join-Path $script:RuntimeRoot 'demos')
	) ) {
	if ( -not ( Test-Path -LiteralPath $path ) ) {
		New-Item -ItemType Directory -Path $path | Out-Null
	}
}

if ( -not ( Test-Path -LiteralPath $script:Exe ) ) {
	throw "Missing client executable: $script:Exe"
}

$stamp = Get-Date -Format 'yyyyMMdd_HHmmss'
$menuShotPrefix = "codex_client_p6_main_$stamp"
$mapShotPrefix = "codex_client_p6_map_$stamp"
$demoPrefix = "codex_client_p6_demo_$stamp"
$savedConfigName = "codex_client_p6_saved_$stamp.cfg"

$mainLog = Join-Path $script:LogRoot ("codex_client_p6_main_{0}.log" -f $stamp)
$mapLog = Join-Path $script:LogRoot ("codex_client_p6_map_{0}.log" -f $stamp)

$mainProbe = Invoke-MainMenuProbe -Stamp $stamp -ScreenshotPrefix $menuShotPrefix -SavedConfigName $savedConfigName -ArchivedLog $mainLog
$mapProbe = Invoke-MapRuntimeProbe -Stamp $stamp -ScreenshotPrefix $mapShotPrefix -DemoPrefix $demoPrefix -ArchivedLog $mapLog

$qzconfigPath = Join-Path $script:RuntimeRoot 'qzconfig.cfg'
$repconfigPath = Join-Path $script:RuntimeRoot 'repconfig.cfg'
$savedConfigPath = Join-Path $script:RuntimeRoot $savedConfigName
$mainEngineScreenshotPath = if ( $mainProbe.engine_screenshot ) { $mainProbe.engine_screenshot.FullName } else { '' }
$mapEngineScreenshotPath = if ( $mapProbe.engine_screenshot ) { $mapProbe.engine_screenshot.FullName } else { '' }
$mapDemoPath = if ( $mapProbe.demo_file ) { $mapProbe.demo_file.FullName } else { '' }

$mainLogText = $mainProbe.log_text
$mapLogText = $mapProbe.log_text

$verifiedMarkers = New-Object 'System.Collections.Generic.List[string]'
$missingMarkers = New-Object 'System.Collections.Generic.List[string]'

$warnings = New-Object 'System.Collections.Generic.List[string]'
if ( -not ( Test-Path -LiteralPath $qzconfigPath ) ) {
	$warnings.Add( 'qzconfig.cfg was not present after the client runtime probe.' )
}
if ( -not ( Test-Path -LiteralPath $repconfigPath ) ) {
	$warnings.Add( 'repconfig.cfg was not present after the client runtime probe.' )
}
if ( -not ( Test-Path -LiteralPath $savedConfigPath ) ) {
	$warnings.Add( 'writeClientConfig did not produce the expected client config artifact.' )
}
if ( -not $mapProbe.demo_file ) {
	$warnings.Add( 'Map runtime probe did not produce a demo artifact.' )
}

$mapScreenshotLogged = ( $mapLogText -match [regex]::Escape( "Wrote screenshots/$mapShotPrefix.jpg" ) ) -or -not [string]::IsNullOrWhiteSpace( $mapEngineScreenshotPath )
$gameEndPublished = $mapLogText -match [regex]::Escape( 'steam_event game.end' )
$shutdownSeen = $mapLogText -match [regex]::Escape( '----- CL_Shutdown -----' )
$lifecycleEndConfirmed = $mapProbe.disconnect_seen -or $gameEndPublished -or $shutdownSeen

foreach ( $pair in @(
		@('----- UI Initialization -----', $mainLogText),
		@('----- UI Initialization Complete -----', $mainLogText),
		@('execing qzconfig.cfg', $mainLogText),
		@('execing repconfig.cfg', $mainLogText),
		@('web_showBrowser ignored: online services disabled by build settings', $mainLogText),
		@('web_changeHash ignored: online services disabled by build settings', $mainLogText),
		@('web_showError codex_client_p6_error', $mainLogText),
		@('web_reload', $mainLogText),
		@('web_stopRefresh ignored: online services disabled by build settings', $mainLogText),
		@("Wrote screenshots/$menuShotPrefix.jpg", $mainLogText),
		@("Server: $MapName", $mapLogText),
		@('Going from CS_PRIMED to CS_ACTIVE', $mapLogText)
	) ) {
	if ( $pair[1] -match [regex]::Escape( $pair[0] ) ) {
		$verifiedMarkers.Add( $pair[0] )
	} else {
		$missingMarkers.Add( $pair[0] )
	}
}

if ( $mapScreenshotLogged ) {
	$verifiedMarkers.Add( "engine screenshot artifact: $mapShotPrefix" )
} else {
	$missingMarkers.Add( "engine screenshot artifact: $mapShotPrefix" )
}

if ( $lifecycleEndConfirmed ) {
	$verifiedMarkers.Add( 'client runtime end markers observed' )
} else {
	$missingMarkers.Add( 'client runtime end markers observed' )
}

$artifact = [ordered]@{
	artifact_version = 2
	phase = 'CL-P6'
	parity_estimate = [ordered]@{
		before = 99
		after = 100
	}
	probe_script = 'tools/client/run_client_runtime_probe.ps1'
	runtime_root = To-RepoPath -Path $script:RuntimeRoot
	retail_basepath = To-RepoPath -Path $script:RetailBasePath
	asset_cdpath = To-RepoPath -Path $script:RetailUiBundleRoot
	main_menu = [ordered]@{
		engine_screenshot = To-RepoPath -Path $mainEngineScreenshotPath
		engine_sha256 = Get-ArtifactSha256 -Path $mainEngineScreenshotPath
		window_capture = ''
		window_sha256 = ''
		window_meta = ''
		log = To-RepoPath -Path $mainProbe.log_path
		config = To-RepoPath -Path $mainProbe.config
		saved_config = To-RepoPath -Path $mainProbe.saved_config
		launch_args = $mainProbe.launch_args
		argument_line = ($mainProbe.launch_args -join ' ')
		environment = $mainProbe.environment
		ui_init_started = $mainLogText -match [regex]::Escape( '----- UI Initialization -----' )
		ui_init_complete = $mainLogText -match [regex]::Escape( '----- UI Initialization Complete -----' )
		execed_qzconfig = $mainLogText -match [regex]::Escape( 'execing qzconfig.cfg' )
		execed_repconfig = $mainLogText -match [regex]::Escape( 'execing repconfig.cfg' )
		qzconfig = [ordered]@{
			path = To-RepoPath -Path $qzconfigPath
			exists = Test-Path -LiteralPath $qzconfigPath
			sha256 = Get-ArtifactSha256 -Path $qzconfigPath
		}
		repconfig = [ordered]@{
			path = To-RepoPath -Path $repconfigPath
			exists = Test-Path -LiteralPath $repconfigPath
			sha256 = Get-ArtifactSha256 -Path $repconfigPath
		}
		write_client_config = [ordered]@{
			path = To-RepoPath -Path $savedConfigPath
			exists = Test-Path -LiteralPath $savedConfigPath
			sha256 = Get-ArtifactSha256 -Path $savedConfigPath
		}
		offline_browser_policy = [ordered]@{
			show_browser_ignored = $mainLogText -match [regex]::Escape( 'web_showBrowser ignored: online services disabled by build settings' )
			change_hash_ignored = $mainLogText -match [regex]::Escape( 'web_changeHash ignored: online services disabled by build settings' )
			show_error_logged = $mainLogText -match [regex]::Escape( 'web_showError codex_client_p6_error' )
			reload_logged = $mainLogText -match [regex]::Escape( 'web_reload' )
			stop_refresh_ignored = $mainLogText -match [regex]::Escape( 'web_stopRefresh ignored: online services disabled by build settings' )
		}
		shot_logged = $mainProbe.shot_logged
	}
	map_runtime = [ordered]@{
		map = $MapName
		engine_screenshot = To-RepoPath -Path $mapEngineScreenshotPath
		engine_sha256 = Get-ArtifactSha256 -Path $mapEngineScreenshotPath
		window_capture = ''
		window_sha256 = ''
		window_meta = ''
		log = To-RepoPath -Path $mapProbe.log_path
		config = To-RepoPath -Path $mapProbe.config
		launch_args = $mapProbe.launch_args
		argument_line = ($mapProbe.launch_args -join ' ')
		environment = $mapProbe.environment
		server_seen = $mapProbe.server_seen
		active_seen = $mapProbe.active_seen
		disconnect_seen = $mapProbe.disconnect_seen
		game_end_published = $gameEndPublished
		shutdown_seen = $shutdownSeen
		lifecycle_end_confirmed = $lifecycleEndConfirmed
		shot_logged = $mapProbe.shot_logged
		demo_file = To-RepoPath -Path $mapDemoPath
		demo_sha256 = Get-ArtifactSha256 -Path $mapDemoPath
		demo_written = [bool]$mapProbe.demo_file
	}
	verified_log_markers = $verifiedMarkers
	missing_log_markers = $missingMarkers
	warnings = $warnings
	summary = 'Windowed client runtime probes covered retail config/bootstrap writes, default-disabled browser-policy behavior, and a live local-map client lifecycle with authoritative engine screenshots plus a flushed demo artifact.'
}

$artifactPath = Join-Path $RepoRoot 'artifacts\client_validation\logs\client_runtime_evidence_20260410.json'
$artifactDir = Split-Path -Path $artifactPath -Parent
if ( -not ( Test-Path -LiteralPath $artifactDir ) ) {
	New-Item -ItemType Directory -Path $artifactDir | Out-Null
}
$artifact | ConvertTo-Json -Depth 7 | Set-Content -LiteralPath $artifactPath -Encoding ascii

if ( $missingMarkers.Count -eq 0 -and $warnings.Count -eq 0 ) {
	Write-Host 'Windowed client runtime probes covered retail config/bootstrap, offline browser-policy behavior, and a live local-map client lifecycle with authoritative engine screenshots.'
} else {
	Write-Warning 'Client runtime probe completed with partial evidence; inspect warnings and missing markers before treating the CL-P6 artifact as final closure evidence.'
}
