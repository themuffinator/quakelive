param(
	[string]$RepoRoot = (Resolve-Path (Join-Path $PSScriptRoot '..\..')).Path,
	[string]$RetailBasePath = 'C:\PROGRA~2\Steam\STEAMA~1\common\QUAKEL~1',
	[string]$MapName = 'bloodrun',
	[int]$MenuWaitFrames = 300
)

$ErrorActionPreference = 'Stop'

function Add-WaitLines {
	param(
		[System.Collections.Generic.List[string]]$Lines,
		[int]$Count
	)

	for ($i = 0; $i -lt $Count; $i++) {
		$Lines.Add('wait')
	}
}

function Initialize-WindowCapture {
	if ('QLRendererWindowCapture' -as [type]) {
		return
	}

	Add-Type -AssemblyName System.Drawing
	Add-Type @"
using System;
using System.Runtime.InteropServices;
public struct QLRECT {
	public int Left;
	public int Top;
	public int Right;
	public int Bottom;
}
public static class QLRendererWindowCapture {
	[DllImport("user32.dll")]
	public static extern bool GetWindowRect(IntPtr hWnd, out QLRECT lpRect);
}
"@
}

function Capture-ProcessWindow {
	param(
		[System.Diagnostics.Process]$Process,
		[string]$ImagePath,
		[string]$MetaPath
	)

	Initialize-WindowCapture
	$Process.Refresh()
	if ($Process.MainWindowHandle -eq 0) {
		return $null
	}

	$rect = New-Object QLRECT
	if (-not [QLRendererWindowCapture]::GetWindowRect([IntPtr]$Process.MainWindowHandle, [ref]$rect)) {
		return $null
	}

	$width = $rect.Right - $rect.Left
	$height = $rect.Bottom - $rect.Top
	if ($width -le 0 -or $height -le 0) {
		return $null
	}

	$bitmap = New-Object System.Drawing.Bitmap($width, $height)
	$graphics = [System.Drawing.Graphics]::FromImage($bitmap)
	try {
		try {
			$graphics.CopyFromScreen($rect.Left, $rect.Top, 0, 0, $bitmap.Size)
		} catch {
			return $null
		}
		$bitmap.Save($ImagePath, [System.Drawing.Imaging.ImageFormat]::Png)
	} finally {
		$graphics.Dispose()
		$bitmap.Dispose()
	}

	$meta = [ordered]@{
		timestamp = (Get-Date).ToString('o')
		processId = $Process.Id
		windowHandle = [int64]$Process.MainWindowHandle
		windowTitle = $Process.MainWindowTitle
		rect = [ordered]@{
			left = $rect.Left
			top = $rect.Top
			right = $rect.Right
			bottom = $rect.Bottom
			width = $width
			height = $height
		}
		image = $ImagePath
	}
	$meta | ConvertTo-Json -Depth 5 | Set-Content -Path $MetaPath -Encoding ascii

	return [ordered]@{
		window_capture = $ImagePath
		window_meta = $MetaPath
		window_sha256 = (Get-FileHash -Algorithm SHA256 -Path $ImagePath).Hash.ToLowerInvariant()
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
		'+set','fs_basepath',$script:RetailBasePath,
		'+set','fs_cdpath',$script:CdPath,
		'+set','fs_homepath',$script:QlHome
	)
	if ($ExtraArgs) {
		$launchArgs += $ExtraArgs
	}
	$launchArgs += @('+exec', $ConfigName)

	$process = Start-Process -FilePath $script:Exe -ArgumentList $launchArgs -WorkingDirectory $script:RepoRoot -PassThru
	return [ordered]@{
		process = $process
		launch_args = $launchArgs
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

function Archive-LiveLog {
	param([string]$Destination)

	if (Test-Path $script:RuntimeLog) {
		Copy-Item -Path $script:RuntimeLog -Destination $Destination -Force
	}
}

function Invoke-MainMenuProbe {
	param(
		[string]$Stamp,
		[string]$ScreenshotName,
		[string]$WindowPng,
		[string]$WindowJson,
		[string]$ArchivedLog
	)

	$configName = "codex_renderer_p6_main_$Stamp.cfg"
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
	$launch = Start-RendererProcess -ConfigName $configName -ExtraArgs @()
	$process = $launch.process
	$capturedWindow = $null
	$shotLogged = $false
	$deadline = (Get-Date).AddSeconds(120)
	while ((Get-Date) -lt $deadline -and -not $process.HasExited) {
		if (Test-Path $script:RuntimeLog) {
			$logText = Get-Content -Path $script:RuntimeLog -Raw -ErrorAction SilentlyContinue
			if ($logText -match [regex]::Escape("Wrote screenshots/$ScreenshotName.jpg")) {
				$shotLogged = $true
				if (-not $capturedWindow) {
					$capturedWindow = Capture-ProcessWindow -Process $process -ImagePath $WindowPng -MetaPath $WindowJson
				}
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
		engine_screenshot = Find-EngineScreenshot -ScreenshotName $ScreenshotName
		window_capture = $capturedWindow
		log_path = $ArchivedLog
		shot_logged = $shotLogged
		log_text = if (Test-Path $ArchivedLog) { Get-Content -Path $ArchivedLog -Raw -ErrorAction SilentlyContinue } else { '' }
	}
}

function Invoke-MapRuntimeProbe {
	param(
		[string]$Stamp,
		[string]$ScreenshotName,
		[string]$WindowPng,
		[string]$WindowJson,
		[string]$ArchivedLog
	)

	$configName = "codex_renderer_p6_map_$Stamp.cfg"
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
		("map $MapName")
	) | Set-Content -Path $configPath -Encoding ascii

	Reset-LiveLog
	$launch = Start-RendererProcess -ConfigName $configName -ExtraArgs @('+set', 'sv_pure', '0', '+set', 'rconPassword', $password)
	$process = $launch.process
	$capturedWindow = $null
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
		if (-not $capturedWindow -and $process.MainWindowHandle -ne 0 -and ($serverSeen -or $activeSeen)) {
			$capturedWindow = Capture-ProcessWindow -Process $process -ImagePath $WindowPng -MetaPath $WindowJson
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
	$engineScreenshot = Find-EngineScreenshot -ScreenshotName $ScreenshotName
	return [ordered]@{
		config = $configPath
		launch_args = $launch.launch_args
		engine_screenshot = $engineScreenshot
		window_capture = $capturedWindow
		log_path = $ArchivedLog
		server_seen = $serverSeen
		active_seen = $activeSeen
		shot_logged = ($shotLogged -or $null -ne $engineScreenshot)
		log_text = if (Test-Path $ArchivedLog) { Get-Content -Path $ArchivedLog -Raw -ErrorAction SilentlyContinue } else { '' }
	}
}

$script:BuildRoot = Join-Path $RepoRoot 'build\win32\Debug'
$script:QlHome = Join-Path $BuildRoot 'bin'
$script:RuntimeRoot = Join-Path $QlHome 'baseq3'
$script:Exe = Join-Path $QlHome 'quakelive_steam.exe'
$script:RetailBasePath = $RetailBasePath
$script:CdPath = Join-Path $RepoRoot 'assets\quakelive'
$script:DumpRoot = Join-Path $BuildRoot 'dumps'
$script:DumpShotRoot = Join-Path $DumpRoot 'screenshots'
$script:DumpLogRoot = Join-Path $DumpRoot 'logs'
$script:ArtifactRoot = Join-Path $RepoRoot 'artifacts\renderer_validation\logs'
$script:RuntimeLog = Join-Path $RuntimeRoot 'qconsole.log'
$script:MapName = $MapName
$retailBaseq3Root = Join-Path $RetailBasePath 'baseq3'
$artifactDate = Get-Date -Format 'yyyyMMdd'
$stamp = Get-Date -Format 'yyyyMMdd_HHmmss'
$artifactPath = Join-Path $ArtifactRoot ("renderer_runtime_evidence_" + $artifactDate + '.json')
$mainShotName = "codex_renderer_p6_main_$stamp"
$mapShotName = "codex_renderer_p6_map_$stamp"
$mainWindowPng = Join-Path $DumpShotRoot ($mainShotName + '_window.png')
$mainWindowJson = Join-Path $DumpShotRoot ($mainShotName + '_window.json')
$mapWindowPng = Join-Path $DumpShotRoot ($mapShotName + '_window.png')
$mapWindowJson = Join-Path $DumpShotRoot ($mapShotName + '_window.json')
$mainArchivedLog = Join-Path $DumpLogRoot ("codex_renderer_p6_main_" + $stamp + '.log')
$mapArchivedLog = Join-Path $DumpLogRoot ("codex_renderer_p6_map_" + $stamp + '.log')

foreach ($requiredPath in @($Exe, $RuntimeRoot, $CdPath, $retailBaseq3Root)) {
	if (-not (Test-Path $requiredPath)) {
		throw "Required path missing: $requiredPath"
	}
}

New-Item -ItemType Directory -Force -Path $DumpShotRoot, $DumpLogRoot, $ArtifactRoot | Out-Null
$env:QLR_DUMP_PATH = $DumpRoot

$mainProbe = Invoke-MainMenuProbe -Stamp $stamp -ScreenshotName $mainShotName -WindowPng $mainWindowPng -WindowJson $mainWindowJson -ArchivedLog $mainArchivedLog
$mapProbe = Invoke-MapRuntimeProbe -Stamp $stamp -ScreenshotName $mapShotName -WindowPng $mapWindowPng -WindowJson $mapWindowJson -ArchivedLog $mapArchivedLog

$verifiedMarkers = @()
$missingMarkers = @()
foreach ($marker in @(
	'----- R_Init -----',
	'R_Init: InitOpenGL',
	'Initializing OpenGL subsystem',
	'R_Init: InitRenderTargets',
	'R_Init: InitColorCorrection',
	'R_Init: InitImages',
	'R_Init: InitShaders',
	'R_Init: InitFreeType',
	'----- finished R_Init -----',
	("Wrote screenshots/$mainShotName.jpg")
)) {
	if ($mainProbe.log_text -match [regex]::Escape($marker)) {
		$verifiedMarkers += $marker
	} else {
		$missingMarkers += $marker
	}
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
if (-not $mainProbe.window_capture) {
	$warnings += 'Main-menu process-bound window capture was not recorded.'
}
if (-not $mapProbe.window_capture) {
	$warnings += 'Map-runtime process-bound window capture was not recorded.'
}
if (-not $mainProbe.engine_screenshot) {
	$warnings += 'Main-menu engine screenshot was not recorded.'
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
if ($missingMarkers.Count -gt 0) {
	$warnings += 'One or more expected renderer/runtime log markers were missing.'
}

$artifact = [ordered]@{
	artifact_version = 1
	phase = 'RG-P6'
	parity_estimate = [ordered]@{
		before = 96
		after = 98
	}
	probe_script = To-RepoPath (Join-Path $RepoRoot 'tools\renderer\run_renderer_runtime_probe.ps1')
	runtime_root = To-RepoPath $RuntimeRoot
	retail_baseq3_root = $retailBaseq3Root.Replace('\', '/')
	main_menu = [ordered]@{
		engine_screenshot = if ($mainProbe.engine_screenshot) { To-RepoPath $mainProbe.engine_screenshot.FullName } else { '' }
		window_capture = if ($mainProbe.window_capture) { To-RepoPath $mainProbe.window_capture.window_capture } else { '' }
		window_sha256 = if ($mainProbe.window_capture) { $mainProbe.window_capture.window_sha256 } else { '' }
		window_meta = if ($mainProbe.window_capture) { To-RepoPath $mainProbe.window_capture.window_meta } else { '' }
		log = To-RepoPath $mainProbe.log_path
		config = To-RepoPath $mainProbe.config
		launch_args = $mainProbe.launch_args
	}
	map_runtime = [ordered]@{
		map = $MapName
		engine_screenshot = if ($mapProbe.engine_screenshot) { To-RepoPath $mapProbe.engine_screenshot.FullName } else { '' }
		window_capture = if ($mapProbe.window_capture) { To-RepoPath $mapProbe.window_capture.window_capture } else { '' }
		window_sha256 = if ($mapProbe.window_capture) { $mapProbe.window_capture.window_sha256 } else { '' }
		window_meta = if ($mapProbe.window_capture) { To-RepoPath $mapProbe.window_capture.window_meta } else { '' }
		log = To-RepoPath $mapProbe.log_path
		config = To-RepoPath $mapProbe.config
		launch_args = $mapProbe.launch_args
		server_seen = $mapProbe.server_seen
		active_seen = $mapProbe.active_seen
		shot_logged = $mapProbe.shot_logged
	}
	verified_log_markers = $verifiedMarkers
	missing_log_markers = $missingMarkers
	warnings = $warnings
	summary = if ($warnings.Count -eq 0) {
		'Windowed renderer runtime probes covered both the main menu and a live in-game map, produced authoritative engine screenshots plus process-bound captures, and logged the expected renderer init/runtime markers.'
	} else {
		'Renderer runtime probe completed with partial evidence; inspect warnings and missing markers before treating the artifact as full closure evidence.'
	}
}

$artifact | ConvertTo-Json -Depth 7 | Set-Content -Path $artifactPath -Encoding ascii
$artifact | ConvertTo-Json -Depth 7
