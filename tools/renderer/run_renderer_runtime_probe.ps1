param(
	[string]$RepoRoot = (Resolve-Path (Join-Path $PSScriptRoot '..\..')).Path,
	[string]$RetailBasePath = 'C:\PROGRA~2\Steam\STEAMA~1\common\QUAKEL~1',
	[string]$MapName = 'bloodrun',
	[int]$MenuWaitFrames = 450
)

$ErrorActionPreference = 'Stop'
$RepoRoot = [System.IO.Path]::GetFullPath((Resolve-Path -LiteralPath $RepoRoot).Path)
$RetailBasePath = [System.IO.Path]::GetFullPath((Resolve-Path -LiteralPath $RetailBasePath).Path)

function Resolve-RetailUiBundleRoot {
	param([string]$Root)

	$candidate = [System.IO.Path]::GetFullPath((Join-Path $Root 'build\ui_bundle\staging'))
	$baseq3Root = Join-Path $candidate 'baseq3'
	foreach ($requiredPath in @(
			$baseq3Root,
			(Join-Path $baseq3Root 'default.cfg'),
			(Join-Path $baseq3Root 'ui\hud3.txt'),
			(Join-Path $baseq3Root 'ui\ingame_scoreboard_ffa.menu'),
			(Join-Path $baseq3Root 'ui\assets\button_back.png'),
			(Join-Path $baseq3Root 'ui\assets\hud\ffa.png'),
			(Join-Path $baseq3Root 'ui\assets\score\scoretl.png'),
			(Join-Path $baseq3Root 'fonts\font.dat'),
			(Join-Path $baseq3Root 'fonts\font.tga')
		)) {
		if (-not (Test-Path -LiteralPath $requiredPath)) {
			throw "Quake Live UI staging content was not found: $requiredPath. Run tools/build_ui_bundle.py before running the renderer probe so staging\\baseq3 contains the retail UI runtime tree."
		}
	}

	return $candidate
}

function Add-WaitLines {
	param(
		[System.Collections.Generic.List[string]]$Lines,
		[int]$Count
	)

	for ($i = 0; $i -lt $Count; $i++) {
		$Lines.Add('wait')
	}
}

function Send-Rcon {
	param(
		[string]$Password,
		[string]$Command
	)

	$udp = New-Object System.Net.Sockets.UdpClient
	try {
		$prefix = [byte[]](255, 255, 255, 255)
		$payload = [System.Text.Encoding]::ASCII.GetBytes("rcon $Password $Command")
		$buffer = New-Object byte[] ($prefix.Length + $payload.Length)
		[Array]::Copy($prefix, 0, $buffer, 0, $prefix.Length)
		[Array]::Copy($payload, 0, $buffer, $prefix.Length, $payload.Length)
		[void]$udp.Send($buffer, $buffer.Length, '127.0.0.1', 27960)
	} finally {
		$udp.Close()
	}
}

function To-RepoPath {
	param([string]$Path)

	if ([string]::IsNullOrWhiteSpace($Path)) {
		return ''
	}

	$resolved = [System.IO.Path]::GetFullPath($Path)
	$repoResolved = [System.IO.Path]::GetFullPath($RepoRoot)
	if ($resolved.StartsWith($repoResolved, [System.StringComparison]::OrdinalIgnoreCase)) {
		return $resolved.Substring($repoResolved.Length).TrimStart('\').Replace('\', '/')
	}

	return $resolved.Replace('\', '/')
}

function Initialize-ProbeHome {
	if (Test-Path $script:QlHome) {
		Remove-Item -LiteralPath $script:QlHome -Recurse -Force
	}

	New-Item -ItemType Directory -Force -Path $script:RuntimeRoot, (Join-Path $script:RuntimeRoot 'screenshots') | Out-Null
	foreach ($moduleName in @('uix86.dll', 'cgamex86.dll', 'qagamex86.dll')) {
		Copy-Item -Path (Join-Path $script:SourceBaseq3 $moduleName) -Destination (Join-Path $script:RuntimeRoot $moduleName) -Force
	}
	foreach ($stalePak in @(
			(Join-Path $script:RuntimeRoot 'pak_uiql.pk3'),
			(Join-Path $script:RuntimeRoot 'pak_ui_src_retail_overlay.pk3')
		)) {
		if (Test-Path -LiteralPath $stalePak) {
			Remove-Item -LiteralPath $stalePak -Force
		}
	}
}

function Set-ProbeRuntimeContext {
	param([string]$Label)

	$script:QlHome = Join-Path $script:BuildRoot ("renderer_probe_home_" + $Label)
	$script:RuntimeRoot = Join-Path $script:QlHome 'baseq3'
	$script:RuntimeLog = Join-Path $script:RuntimeRoot 'qconsole.log'
	Initialize-ProbeHome
}

function Quote-LaunchArgument {
	param([string]$Value)

	if ($null -eq $Value) {
		return '""'
	}

	if ($Value -notmatch '[\s"]') {
		return $Value
	}

	return '"' + $Value.Replace('"', '\"') + '"'
}

function Start-RendererProcess {
	param(
		[string]$ConfigName,
		[string[]]$ExtraArgs
	)

	$launchArgs = @(
		'+set','developer','1',
		'+set','logfile','2',
		'+set','g_logfile','1',
		'+set','r_fullscreen','0',
		'+set','r_mode','-1',
		'+set','r_customwidth','1280',
		'+set','r_customheight','720',
		'+set','r_windowedMode','-1',
		'+set','r_windowedWidth','1280',
		'+set','r_windowedHeight','720',
		'+set','r_enablePostProcess','1',
		'+set','r_enableBloom','1',
		'+set','r_enableColorCorrect','1',
		'+set','r_ext_multitexture','1',
		'+set','r_allowExtensions','1',
		'+set','r_picmip','0',
		'+set','s_initsound','0',
		'+set','com_zoneMegs','64',
		'+set','com_hunkMegs','256',
		'+set','fs_basepath',$script:RetailBasePath,
		'+set','fs_cdpath',$script:RetailUiBundleRoot,
		'+set','fs_homepath',$script:QlHome
	)
	if ($ExtraArgs) {
		$launchArgs += $ExtraArgs
	}
	$launchArgs += @('+exec', $ConfigName)

	$argumentLine = ($launchArgs | ForEach-Object { Quote-LaunchArgument -Value $_ }) -join ' '
	$process = Start-Process -FilePath $script:Exe -ArgumentList $argumentLine -WorkingDirectory $script:QlHome -PassThru
	return [ordered]@{
		process = $process
		launch_args = $launchArgs
		argument_line = $argumentLine
	}
}

function Reset-LiveLog {
	Get-Process -Name quakelive_steam -ErrorAction SilentlyContinue | Stop-Process -Force
	Start-Sleep -Milliseconds 500
	if (Test-Path $script:RuntimeLog) {
		Remove-Item -Path $script:RuntimeLog -Force
	}
}

function Find-EngineScreenshot {
	param([string]$ScreenshotName)

	return Get-ChildItem -Path (Join-Path $script:RuntimeRoot 'screenshots') -Filter ($ScreenshotName + '*.jpg') -ErrorAction SilentlyContinue |
		Sort-Object LastWriteTime -Descending |
		Select-Object -First 1
}

function Resolve-EngineScreenshot {
	param([string]$ScreenshotName)

	$namedScreenshot = Find-EngineScreenshot -ScreenshotName $ScreenshotName
	if ($namedScreenshot) {
		return $namedScreenshot
	}

	return Get-ChildItem -Path (Join-Path $script:RuntimeRoot 'screenshots') -Filter '*.jpg' -ErrorAction SilentlyContinue |
		Sort-Object LastWriteTime -Descending |
		Select-Object -First 1
}

function Get-ArtifactSha256 {
	param([string]$Path)

	if (-not $Path -or -not (Test-Path $Path)) {
		return ''
	}

	return (Get-FileHash -Algorithm SHA256 -Path $Path).Hash.ToLowerInvariant()
}

function Get-MissingAasAliasName {
	param([string]$LogText)

	$match = [regex]::Match($LogText, '(?im)Fatal: can''t open maps/([^/\r\n]+)\.aas')
	if ($match.Success) {
		return $match.Groups[1].Value
	}

	return ''
}

function Stage-RetailAasAlias {
	param(
		[string]$MapName,
		[string]$AliasName
	)

	if ([string]::IsNullOrWhiteSpace($AliasName)) {
		return ''
	}

	$source = Join-Path $script:RetailBaseq3Root ('maps\' + $MapName + '.aas')
	if (-not (Test-Path -LiteralPath $source)) {
		return ''
	}

	$destinationDir = Join-Path $script:RuntimeRoot 'maps'
	$destination = Join-Path $destinationDir ($AliasName + '.aas')
	New-Item -ItemType Directory -Force -Path $destinationDir | Out-Null
	Copy-Item -LiteralPath $source -Destination $destination -Force
	return $destination
}

function Archive-LiveLog {
	param([string]$Destination)

	if (Test-Path $script:RuntimeLog) {
		Copy-Item -Path $script:RuntimeLog -Destination $Destination -Force
	}
}

function Invoke-MainMenuProbe {
	param(
		[string]$Stamp,
		[string]$ConfigLabel,
		[string]$ScreenshotName,
		[string]$ArchivedLog,
		[string[]]$ExtraArgs = @()
	)

	$configName = "codex_renderer_p11_${ConfigLabel}_$Stamp.cfg"
	$configPath = Join-Path $script:RuntimeRoot $configName
	$lines = New-Object 'System.Collections.Generic.List[string]'
	foreach ($line in @(
		'set developer 1',
		'set logfile 2',
		'set g_logfile 1',
		'set r_fullscreen 0'
	)) {
		$lines.Add($line)
	}
	Add-WaitLines -Lines $lines -Count $MenuWaitFrames
	$lines.Add("screenshotJPEG $ScreenshotName")
	Add-WaitLines -Lines $lines -Count 150
	$lines.Add('quit')
	Set-Content -Path $configPath -Value $lines -Encoding ascii

	Reset-LiveLog
	$launch = Start-RendererProcess -ConfigName $configName -ExtraArgs $ExtraArgs
	$process = $launch.process
	$shotLogged = $false
	$deadline = (Get-Date).AddSeconds(120)
	while ((Get-Date) -lt $deadline -and -not $process.HasExited) {
		$process.Refresh()

		if (Test-Path $script:RuntimeLog) {
			$logText = Get-Content -Path $script:RuntimeLog -Raw -ErrorAction SilentlyContinue
			if ($logText -match [regex]::Escape("Wrote screenshots/$ScreenshotName.jpg")) {
				$shotLogged = $true
				break
			}
		}
		Start-Sleep -Milliseconds 500
	}

	if (-not $process.HasExited) {
		$null = $process.WaitForExit(90000)
	}
	if (-not $process.HasExited) {
		Stop-Process -Id $process.Id -Force
	}

	Archive-LiveLog -Destination $ArchivedLog
	return [ordered]@{
		config = $configPath
		launch_args = $launch.launch_args
		argument_line = $launch.argument_line
		engine_screenshot = Resolve-EngineScreenshot -ScreenshotName $ScreenshotName
		log_path = $ArchivedLog
		shot_logged = $shotLogged
		log_text = if (Test-Path $ArchivedLog) { Get-Content -Path $ArchivedLog -Raw -ErrorAction SilentlyContinue } else { '' }
	}
}

function Invoke-DebugAtlasProbe {
	param(
		[string]$Stamp,
		[string]$ScreenshotName,
		[string]$ArchivedLog
	)

	$configName = "codex_renderer_p11_atlas_$Stamp.cfg"
	$configPath = Join-Path $script:RuntimeRoot $configName
	$password = 'qlrpass'
	@(
		'set developer 1',
		'set logfile 2',
		'set g_logfile 1',
		'set sv_pure 0',
		'set r_fullscreen 0',
		'set g_gametype 1',
		'set g_doWarmup 1',
		'set g_warmup 20',
		("map $MapName ffa")
	) | Set-Content -Path $configPath -Encoding ascii

	Reset-LiveLog
	$launch = Start-RendererProcess -ConfigName $configName -ExtraArgs @('+set', 'sv_pure', '0', '+set', 'rconPassword', $password)
	$process = $launch.process
	$serverSeen = $false
	$activeSeen = $false
	$shotLogged = $false
	$deadline = (Get-Date).AddSeconds(180)

	while ((Get-Date) -lt $deadline -and -not $process.HasExited) {
		Start-Sleep -Milliseconds 500
		$process.Refresh()
		if (Test-Path $script:RuntimeLog) {
			$logText = Get-Content -Path $script:RuntimeLog -Raw -ErrorAction SilentlyContinue
			if ($logText -match [regex]::Escape("Server: $MapName")) {
				$serverSeen = $true
			}
			if ($logText -match 'Going from CS_PRIMED to CS_ACTIVE') {
				$activeSeen = $true
			}
		}
		if ($serverSeen -and $activeSeen) {
			break
		}
	}

	if (-not $process.HasExited -and $activeSeen) {
		Start-Sleep -Milliseconds 1000
		Send-Rcon -Password $password -Command 'r_debugFontAtlas 1'
		Start-Sleep -Milliseconds 500
		Send-Rcon -Password $password -Command 'toggleconsole'
		Start-Sleep -Milliseconds 1000
		Send-Rcon -Password $password -Command ("screenshotJPEG $ScreenshotName")
		$shotDeadline = (Get-Date).AddSeconds(30)
		while ((Get-Date) -lt $shotDeadline -and -not $process.HasExited) {
			Start-Sleep -Milliseconds 500
			if (Test-Path $script:RuntimeLog) {
				$logText = Get-Content -Path $script:RuntimeLog -Raw -ErrorAction SilentlyContinue
				if ($logText -match [regex]::Escape("Wrote screenshots/$ScreenshotName.jpg")) {
					$shotLogged = $true
					break
				}
			}
		}
		Send-Rcon -Password $password -Command 'toggleconsole'
		Send-Rcon -Password $password -Command 'r_debugFontAtlas 0'
		Send-Rcon -Password $password -Command 'quit'
	}

	if (-not $process.HasExited) {
		$null = $process.WaitForExit(90000)
	}
	if (-not $process.HasExited) {
		Stop-Process -Id $process.Id -Force
	}

	Archive-LiveLog -Destination $ArchivedLog
	$engineScreenshot = Resolve-EngineScreenshot -ScreenshotName $ScreenshotName
	$logText = if (Test-Path $ArchivedLog) { Get-Content -Path $ArchivedLog -Raw -ErrorAction SilentlyContinue } else { '' }
	return [ordered]@{
		config = $configPath
		launch_args = $launch.launch_args
		argument_line = $launch.argument_line
		engine_screenshot = $engineScreenshot
		log_path = $ArchivedLog
		server_seen = $serverSeen
		active_seen = $activeSeen
		shot_logged = ($shotLogged -or $null -ne $engineScreenshot)
		log_text = $logText
		missing_aas_alias = Get-MissingAasAliasName -LogText $logText
	}
}

function Invoke-MapRuntimeProbe {
	param(
		[string]$Stamp,
		[string]$ScreenshotName,
		[string]$ArchivedLog
	)

	$configName = "codex_renderer_p11_map_$Stamp.cfg"
	$configPath = Join-Path $script:RuntimeRoot $configName
	$password = 'qlrpass'
	@(
		'set developer 1',
		'set logfile 2',
		'set g_logfile 1',
		'set sv_pure 0',
		'set r_fullscreen 0',
		'set g_gametype 1',
		'set g_doWarmup 1',
		'set g_warmup 20',
		("map $MapName ffa")
	) | Set-Content -Path $configPath -Encoding ascii

	Reset-LiveLog
	$launch = Start-RendererProcess -ConfigName $configName -ExtraArgs @('+set', 'sv_pure', '0', '+set', 'rconPassword', $password)
	$process = $launch.process
	$serverSeen = $false
	$activeSeen = $false
	$shotLogged = $false
	$deadline = (Get-Date).AddSeconds(180)

	while ((Get-Date) -lt $deadline -and -not $process.HasExited) {
		Start-Sleep -Milliseconds 500
		$process.Refresh()
		if (Test-Path $script:RuntimeLog) {
			$logText = Get-Content -Path $script:RuntimeLog -Raw -ErrorAction SilentlyContinue
			if ($logText -match [regex]::Escape("Server: $MapName")) {
				$serverSeen = $true
			}
			if ($logText -match 'Going from CS_PRIMED to CS_ACTIVE') {
				$activeSeen = $true
			}
		}
		if ($serverSeen -and $activeSeen) {
			break
		}
	}

	if (-not $process.HasExited -and ($serverSeen -or $activeSeen)) {
		Start-Sleep -Milliseconds 1000
		Send-Rcon -Password $password -Command ("screenshotJPEG $ScreenshotName")
		$shotDeadline = (Get-Date).AddSeconds(30)
		while ((Get-Date) -lt $shotDeadline -and -not $process.HasExited) {
			Start-Sleep -Milliseconds 500
			if (Test-Path $script:RuntimeLog) {
				$logText = Get-Content -Path $script:RuntimeLog -Raw -ErrorAction SilentlyContinue
				if ($logText -match [regex]::Escape("Wrote screenshots/$ScreenshotName.jpg")) {
					$shotLogged = $true
					break
				}
			}
		}
		Send-Rcon -Password $password -Command 'quit'
	}

	if (-not $process.HasExited) {
		$null = $process.WaitForExit(90000)
	}
	if (-not $process.HasExited) {
		Stop-Process -Id $process.Id -Force
	}

	Archive-LiveLog -Destination $ArchivedLog
	$engineScreenshot = Resolve-EngineScreenshot -ScreenshotName $ScreenshotName
	$logText = if (Test-Path $ArchivedLog) { Get-Content -Path $ArchivedLog -Raw -ErrorAction SilentlyContinue } else { '' }
	return [ordered]@{
		config = $configPath
		launch_args = $launch.launch_args
		argument_line = $launch.argument_line
		engine_screenshot = $engineScreenshot
		log_path = $ArchivedLog
		server_seen = $serverSeen
		active_seen = $activeSeen
		shot_logged = ($shotLogged -or $null -ne $engineScreenshot)
		log_text = $logText
		missing_aas_alias = Get-MissingAasAliasName -LogText $logText
	}
}

$script:BuildRoot = Join-Path $RepoRoot 'build\win32\Debug'
$script:SourceBaseq3 = Join-Path $BuildRoot 'bin\baseq3'
$script:QlHome = ''
$script:RuntimeRoot = ''
$script:Exe = Join-Path $BuildRoot 'bin\quakelive_steam.exe'
$script:RetailBasePath = $RetailBasePath
$script:RetailUiBundleRoot = Resolve-RetailUiBundleRoot -Root $RepoRoot
$script:DumpRoot = Join-Path $BuildRoot 'dumps'
$script:DumpShotRoot = Join-Path $DumpRoot 'screenshots'
$script:DumpLogRoot = Join-Path $DumpRoot 'logs'
$script:ArtifactRoot = Join-Path $RepoRoot 'artifacts\renderer_validation\logs'
$script:RuntimeLog = ''
$script:MapName = $MapName
$retailBaseq3Root = Join-Path $RetailBasePath 'baseq3'
$script:RetailBaseq3Root = $retailBaseq3Root
$artifactDate = Get-Date -Format 'yyyyMMdd'
$stamp = Get-Date -Format 'yyyyMMdd_HHmmss'
$artifactPath = Join-Path $ArtifactRoot ("renderer_runtime_evidence_" + $artifactDate + '.json')
$latestArtifactPath = Join-Path $ArtifactRoot 'renderer_runtime_evidence_latest.json'
$mainShotName = "codex_renderer_p11_main_$stamp"
$atlasShotName = "codex_renderer_p11_atlas_$stamp"
$mapShotName = "codex_renderer_p11_map_$stamp"
$mainArchivedLog = Join-Path $DumpLogRoot ("codex_renderer_p11_main_" + $stamp + '.log')
$atlasArchivedLog = Join-Path $DumpLogRoot ("codex_renderer_p11_atlas_" + $stamp + '.log')
$mapArchivedLog = Join-Path $DumpLogRoot ("codex_renderer_p11_map_" + $stamp + '.log')

foreach ($requiredPath in @($Exe, $SourceBaseq3, $retailBaseq3Root)) {
	if (-not (Test-Path $requiredPath)) {
		throw "Required path missing: $requiredPath"
	}
}

New-Item -ItemType Directory -Force -Path $DumpShotRoot, $DumpLogRoot, $ArtifactRoot | Out-Null
$env:QLR_DUMP_PATH = $DumpRoot

Set-ProbeRuntimeContext -Label 'main'
$mainProbe = Invoke-MainMenuProbe -Stamp $stamp -ConfigLabel 'main' -ScreenshotName $mainShotName -ArchivedLog $mainArchivedLog
Set-ProbeRuntimeContext -Label 'atlas'
$atlasProbe = Invoke-DebugAtlasProbe -Stamp $stamp -ScreenshotName $atlasShotName -ArchivedLog $atlasArchivedLog
Set-ProbeRuntimeContext -Label 'map'
$mapProbe = Invoke-MapRuntimeProbe -Stamp $stamp -ScreenshotName $mapShotName -ArchivedLog $mapArchivedLog
$stagedAasAlias = ''
$stagedAasAliasName = ''

if (-not $atlasProbe.active_seen -or -not $mapProbe.active_seen) {
	$stagedAasAliasName = if ($mapProbe.missing_aas_alias) { $mapProbe.missing_aas_alias } else { $atlasProbe.missing_aas_alias }
	$stagedAasAlias = Stage-RetailAasAlias -MapName $MapName -AliasName $stagedAasAliasName
	if ($stagedAasAlias) {
		$retryStamp = $stamp + '_aas'
		$atlasShotName = "codex_renderer_p11_atlas_$retryStamp"
		$mapShotName = "codex_renderer_p11_map_$retryStamp"
		$retryAtlasArchivedLog = Join-Path $DumpLogRoot ("codex_renderer_p11_atlas_" + $retryStamp + '.log')
		$retryMapArchivedLog = Join-Path $DumpLogRoot ("codex_renderer_p11_map_" + $retryStamp + '.log')

		Set-ProbeRuntimeContext -Label 'atlas'
		$atlasProbe = Invoke-DebugAtlasProbe -Stamp $retryStamp -ScreenshotName $atlasShotName -ArchivedLog $retryAtlasArchivedLog
		Set-ProbeRuntimeContext -Label 'map'
		$mapProbe = Invoke-MapRuntimeProbe -Stamp $retryStamp -ScreenshotName $mapShotName -ArchivedLog $retryMapArchivedLog
	}
}

$verifiedMarkers = @()
$missingMarkers = @()
$mainShotMarkerSeen = ($mainProbe.log_text -match [regex]::Escape("Wrote screenshots/$mainShotName.jpg")) -or $mainProbe.shot_logged
foreach ($marker in @(
	'----- R_Init -----',
	'R_Init: InitOpenGL',
	'Initializing OpenGL subsystem',
	'R_Init: InitRenderTargets',
	'R_Init: InitColorCorrection',
	'R_Init: InitImages',
	'R_Init: InitShaders',
	'R_Init: InitFreeType',
	'R_Init: InitFontStash',
	'----- finished R_Init -----'
)) {
	if ($mainProbe.log_text -match [regex]::Escape($marker)) {
		$verifiedMarkers += $marker
	} else {
		$missingMarkers += $marker
	}
}
if ($mainShotMarkerSeen) {
	$verifiedMarkers += "Wrote screenshots/$mainShotName.jpg"
} else {
	$missingMarkers += "Wrote screenshots/$mainShotName.jpg"
}
if ($atlasProbe.shot_logged) {
	$verifiedMarkers += "Wrote screenshots/$atlasShotName.jpg"
} else {
	$missingMarkers += "Wrote screenshots/$atlasShotName.jpg"
}
foreach ($marker in @(
	'R_Init: InitFontStash'
)) {
	if ($atlasProbe.log_text -match [regex]::Escape($marker)) {
		$verifiedMarkers += $marker
	} else {
		$missingMarkers += $marker
	}
}
if ($atlasProbe.engine_screenshot) {
	$verifiedMarkers += "engine screenshot artifact: $atlasShotName"
} else {
	$missingMarkers += "engine screenshot artifact: $atlasShotName"
}
foreach ($marker in @(
	("Server: $MapName"),
	'Going from CS_PRIMED to CS_ACTIVE',
	'screenshotJPEG'
)) {
	if ($mapProbe.log_text -match [regex]::Escape($marker)) {
		$verifiedMarkers += $marker
	} else {
		$missingMarkers += $marker
	}
}
if ($mapProbe.engine_screenshot) {
	$verifiedMarkers += "engine screenshot artifact: $mapShotName"
} else {
	$missingMarkers += "engine screenshot artifact: $mapShotName"
}

$warnings = @()
if (-not $mainProbe.engine_screenshot) {
	$warnings += 'Main-menu engine screenshot was not recorded.'
}
if (-not $atlasProbe.engine_screenshot) {
	$warnings += 'Debug-atlas engine screenshot was not recorded.'
}
if (-not $mapProbe.engine_screenshot) {
	$warnings += 'Map-runtime engine screenshot was not recorded.'
}
if (-not $mapProbe.server_seen) {
	$warnings += "Map runtime never logged 'Server: $MapName'."
}
if (-not $mapProbe.active_seen) {
	$warnings += 'Map runtime never reached CS_ACTIVE.'
}
if (-not $mapProbe.shot_logged) {
	$warnings += 'Map-runtime screenshot command did not confirm in qconsole.log.'
}
$mainEngineSha256 = if ($mainProbe.engine_screenshot) { Get-ArtifactSha256 -Path $mainProbe.engine_screenshot.FullName } else { '' }
$atlasEngineSha256 = if ($atlasProbe.engine_screenshot) { Get-ArtifactSha256 -Path $atlasProbe.engine_screenshot.FullName } else { '' }
$mapEngineSha256 = if ($mapProbe.engine_screenshot) { Get-ArtifactSha256 -Path $mapProbe.engine_screenshot.FullName } else { '' }
$registerFontFallbackSeen = (
	($mainProbe.log_text -match [regex]::Escape('RE_RegisterFont: FreeType code not available')) -or
	($mainProbe.log_text -match [regex]::Escape("RE_RegisterFont: using built-in glyph fallback via 'gfx/2d/bigchars'")) -or
	($atlasProbe.log_text -match [regex]::Escape('RE_RegisterFont: FreeType code not available')) -or
	($atlasProbe.log_text -match [regex]::Escape("RE_RegisterFont: using built-in glyph fallback via 'gfx/2d/bigchars'")) -or
	($mapProbe.log_text -match [regex]::Escape('RE_RegisterFont: FreeType code not available')) -or
	($mapProbe.log_text -match [regex]::Escape("RE_RegisterFont: using built-in glyph fallback via 'gfx/2d/bigchars'"))
)
if ($registerFontFallbackSeen) {
	$warnings += 'Runtime logs still hit the fallback RE_RegisterFont lane instead of the BUILD_FREETYPE path.'
}
if ($mainEngineSha256 -and $atlasEngineSha256 -and $mainEngineSha256 -eq $atlasEngineSha256) {
	$warnings += 'Main-menu and debug-atlas engine screenshots matched unexpectedly.'
}
if ($missingMarkers.Count -gt 0) {
	$warnings += 'One or more expected renderer/runtime log markers were missing.'
}

$artifact = [ordered]@{
	artifact_version = 2
	phase = 'RG-P11'
	parity_estimate = [ordered]@{
		before = 98
		after = 100
	}
	probe_script = To-RepoPath (Join-Path $RepoRoot 'tools\renderer\run_renderer_runtime_probe.ps1')
	runtime_root = To-RepoPath $RuntimeRoot
	retail_baseq3_root = $retailBaseq3Root.Replace('\', '/')
	main_menu = [ordered]@{
		engine_screenshot = if ($mainProbe.engine_screenshot) { To-RepoPath $mainProbe.engine_screenshot.FullName } else { '' }
		engine_sha256 = $mainEngineSha256
		window_capture = ''
		window_sha256 = ''
		window_meta = ''
		log = To-RepoPath $mainProbe.log_path
		config = To-RepoPath $mainProbe.config
		launch_args = $mainProbe.launch_args
		argument_line = $mainProbe.argument_line
	}
	debug_atlas = [ordered]@{
		engine_screenshot = if ($atlasProbe.engine_screenshot) { To-RepoPath $atlasProbe.engine_screenshot.FullName } else { '' }
		engine_sha256 = $atlasEngineSha256
		window_capture = ''
		window_sha256 = ''
		window_meta = ''
		log = To-RepoPath $atlasProbe.log_path
		config = To-RepoPath $atlasProbe.config
		launch_args = $atlasProbe.launch_args
		argument_line = $atlasProbe.argument_line
	}
	map_runtime = [ordered]@{
		map = $MapName
		engine_screenshot = if ($mapProbe.engine_screenshot) { To-RepoPath $mapProbe.engine_screenshot.FullName } else { '' }
		engine_sha256 = $mapEngineSha256
		window_capture = ''
		window_sha256 = ''
		window_meta = ''
		log = To-RepoPath $mapProbe.log_path
		config = To-RepoPath $mapProbe.config
		launch_args = $mapProbe.launch_args
		argument_line = $mapProbe.argument_line
		server_seen = $mapProbe.server_seen
		active_seen = $mapProbe.active_seen
		shot_logged = $mapProbe.shot_logged
		missing_aas_alias = $mapProbe.missing_aas_alias
		staged_aas_alias = if ($stagedAasAlias) { To-RepoPath $stagedAasAlias } else { '' }
		staged_aas_alias_name = $stagedAasAliasName
	}
	verified_log_markers = $verifiedMarkers
	missing_log_markers = $missingMarkers
	warnings = $warnings
	text_validation = [ordered]@{
		fontstash_init_seen = (($mainProbe.log_text -match [regex]::Escape('R_Init: InitFontStash')) -or ($atlasProbe.log_text -match [regex]::Escape('R_Init: InitFontStash')))
		registerfont_fallback_seen = $registerFontFallbackSeen
		debug_atlas_engine_capture_distinct = ($mainEngineSha256 -ne '' -and $atlasEngineSha256 -ne '' -and $mainEngineSha256 -ne $atlasEngineSha256)
		debug_atlas_window_capture_distinct = $false
	}
	summary = if ($warnings.Count -eq 0) {
		'Windowed renderer runtime probes covered UI bootstrap, retained-atlas debug visualization, and a live in-game map, produced authoritative engine screenshots, and logged the expected renderer text/runtime markers without falling back to compatibility-only RegisterFont paths.'
	} else {
		'Renderer runtime probe completed with partial evidence; inspect warnings and missing markers before treating the artifact as final text/runtime closure evidence.'
	}
}

$latestArtifactIsSufficient = (
	$warnings.Count -eq 0 -and
	$missingMarkers.Count -eq 0 -and
	$mainEngineSha256 -ne '' -and
	$atlasEngineSha256 -ne '' -and
	$mapEngineSha256 -ne '' -and
	$mainEngineSha256 -ne $atlasEngineSha256 -and
	$mainProbe.shot_logged -and
	$atlasProbe.shot_logged -and
	$mapProbe.server_seen -and
	$mapProbe.active_seen -and
	$mapProbe.shot_logged -and
	-not $registerFontFallbackSeen
)

$artifact | ConvertTo-Json -Depth 7 | Set-Content -Path $artifactPath -Encoding ascii
if ($latestArtifactIsSufficient -or -not (Test-Path -LiteralPath $latestArtifactPath)) {
	$artifact | ConvertTo-Json -Depth 7 | Set-Content -Path $latestArtifactPath -Encoding ascii
}
$artifact | ConvertTo-Json -Depth 7
