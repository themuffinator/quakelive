[CmdletBinding()]
param(
	[string]$RepoRoot = '',
	[string]$RetailInstallRoot = '',
	[string]$RetailProfileRoot = '',
	[string]$MapName = 'catalyst',
	[int]$MenuWaitFrames = 240
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

function Initialize-WindowCapture {
	if ( 'QLModuleWindowCapture' -as [type] ) {
		return
	}

	Add-Type -AssemblyName System.Drawing
	Add-Type @"
using System;
using System.Runtime.InteropServices;
public struct QLMODULERECT {
	public int Left;
	public int Top;
	public int Right;
	public int Bottom;
}
public static class QLModuleWindowCapture {
	[DllImport("user32.dll")]
	public static extern bool GetWindowRect(IntPtr hWnd, out QLMODULERECT lpRect);
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
	if ( $Process.MainWindowHandle -eq 0 ) {
		return $null
	}

	$rect = New-Object QLMODULERECT
	if ( -not [QLModuleWindowCapture]::GetWindowRect( [IntPtr]$Process.MainWindowHandle, [ref]$rect ) ) {
		return $null
	}

	$width = $rect.Right - $rect.Left
	$height = $rect.Bottom - $rect.Top
	if ( $width -le 0 -or $height -le 0 ) {
		return $null
	}

	$bitmap = New-Object System.Drawing.Bitmap( $width, $height )
	$graphics = [System.Drawing.Graphics]::FromImage( $bitmap )
	try {
		try {
			$graphics.CopyFromScreen( $rect.Left, $rect.Top, 0, 0, $bitmap.Size )
		} catch {
			return $null
		}
		$bitmap.Save( $ImagePath, [System.Drawing.Imaging.ImageFormat]::Png )
	} finally {
		$graphics.Dispose()
		$bitmap.Dispose()
	}

	$meta = [ordered]@{
		timestamp = (Get-Date).ToString( 'o' )
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

function To-RepoPath {
	param([string]$Path)

	if ( [string]::IsNullOrWhiteSpace( $Path ) ) {
		return ''
	}

	$resolved = [System.IO.Path]::GetFullPath( $Path )
	$repoResolved = [System.IO.Path]::GetFullPath( $RepoRoot )
	if ( $resolved.StartsWith( $repoResolved, [System.StringComparison]::OrdinalIgnoreCase ) ) {
		return $resolved.Substring( $repoResolved.Length ).TrimStart( '\' ).Replace( '\', '/' )
	}

	return $resolved.Replace( '\', '/' )
}

function Resolve-ExistingPath {
	param([string]$Path)

	if ( [string]::IsNullOrWhiteSpace( $Path ) ) {
		return ''
	}

	$resolved = Resolve-Path -LiteralPath $Path -ErrorAction Stop
	return [System.IO.Path]::GetFullPath( $resolved.Path )
}

function Test-RetailProfileRoot {
	param([string]$Root)

	if ( [string]::IsNullOrWhiteSpace( $Root ) -or -not ( Test-Path -LiteralPath $Root ) ) {
		return $false
	}

	$baseq3 = Join-Path $Root 'baseq3'
	foreach ( $requiredFile in @(
		'cgamex86.dll',
		'qagamex86.dll',
		'uix86.dll'
	) ) {
		if ( -not ( Test-Path -LiteralPath ( Join-Path $baseq3 $requiredFile ) ) ) {
			return $false
		}
	}

	return $true
}

function Test-RetailContentRoot {
	param([string]$Root)

	if ( [string]::IsNullOrWhiteSpace( $Root ) -or -not ( Test-Path -LiteralPath $Root ) ) {
		return $false
	}

	return Test-Path -LiteralPath ( Join-Path $Root 'baseq3\pak00.pk3' )
}

function Get-RetailInstallCandidates {
	$candidates = New-Object 'System.Collections.Generic.List[string]'

	foreach ( $candidate in @(
		$RetailInstallRoot,
		'C:\Program Files (x86)\Steam\steamapps\common\Quake Live',
		'C:\PROGRA~2\Steam\STEAMA~1\common\QUAKEL~1'
	) ) {
		if ( [string]::IsNullOrWhiteSpace( $candidate ) ) {
			continue
		}

		try {
			$resolved = Resolve-ExistingPath -Path $candidate
		} catch {
			continue
		}

		if ( -not $candidates.Contains( $resolved ) ) {
			$candidates.Add( $resolved )
		}

		$parent = Split-Path -Path $resolved -Parent
		if ( $parent ) {
			try {
				$resolvedParent = Resolve-ExistingPath -Path $parent
				if ( -not $candidates.Contains( $resolvedParent ) ) {
					$candidates.Add( $resolvedParent )
				}
			} catch {
			}
		}
	}

	if ( $candidates.Count -eq 0 ) {
		throw 'Unable to resolve a retail Quake Live install root. Pass -RetailInstallRoot explicitly.'
	}

	return $candidates
}

function Resolve-RetailContentRoot {
	param([string[]]$InstallCandidates)

	foreach ( $candidate in $InstallCandidates ) {
		if ( Test-RetailContentRoot -Root $candidate ) {
			return $candidate
		}
	}

	throw 'Unable to find retail base content (baseq3\\pak00.pk3). Pass -RetailInstallRoot explicitly.'
}

function Resolve-RetailProfileRoot {
	param(
		[string[]]$InstallCandidates,
		[string]$ExplicitProfileRoot
	)

	if ( -not [string]::IsNullOrWhiteSpace( $ExplicitProfileRoot ) ) {
		$resolvedExplicit = Resolve-ExistingPath -Path $ExplicitProfileRoot
		if ( Test-RetailProfileRoot -Root $resolvedExplicit ) {
			return $resolvedExplicit
		}

		throw "Retail profile root does not contain the expected DLL set: $resolvedExplicit"
	}

	$candidates = New-Object 'System.Collections.Generic.List[object]'
	foreach ( $installCandidate in $InstallCandidates ) {
		if ( Test-RetailProfileRoot -Root $installCandidate ) {
			$candidates.Add( [ordered]@{
				root = $installCandidate
				stamp = (Get-Item -LiteralPath $installCandidate).LastWriteTimeUtc.Ticks
			} )
		}

		foreach ( $child in Get-ChildItem -LiteralPath $installCandidate -Directory -ErrorAction SilentlyContinue ) {
			if ( Test-RetailProfileRoot -Root $child.FullName ) {
				$candidates.Add( [ordered]@{
					root = [System.IO.Path]::GetFullPath( $child.FullName )
					stamp = $child.LastWriteTimeUtc.Ticks
				} )
			}
		}
	}

	if ( $candidates.Count -eq 0 ) {
		throw 'Unable to locate a retail Quake Live profile directory containing cgamex86.dll, qagamex86.dll, and uix86.dll.'
	}

	return ($candidates | Sort-Object -Property @{ Expression = 'stamp'; Descending = $true }, @{ Expression = 'root'; Descending = $false } | Select-Object -First 1).root
}

function Quote-LaunchArgument {
	param([string]$Value)

	if ( $null -eq $Value ) {
		return '""'
	}

	if ( $Value -notmatch '[\s"]' ) {
		return $Value
	}

	return '"' + $Value.Replace( '"', '\"' ) + '"'
}

function Start-ModuleProcess {
	param(
		[string]$ConfigName,
		[string[]]$ExtraArgs
	)

	$launchArgs = @(
		'+set', 'developer', '1',
		'+set', 'logfile', '2',
		'+set', 'g_logfile', '1',
		'+set', 'vm_trace', '1',
		'+set', 'vm_ui', '0',
		'+set', 'vm_cgame', '0',
		'+set', 'vm_game', '0',
		'+set', 'r_fullscreen', '0',
		'+set', 'r_mode', '-1',
		'+set', 'r_customwidth', '1280',
		'+set', 'r_customheight', '720',
		'+set', 'r_windowedMode', '-1',
		'+set', 'r_windowedWidth', '1280',
		'+set', 'r_windowedHeight', '720',
		'+set', 's_initsound', '0',
		'+set', 'cl_allowDownload', '0',
		'+set', 'fs_basepath', $script:RetailProfileRoot,
		'+set', 'fs_cdpath', $script:RetailContentRoot,
		'+set', 'fs_homepath', $script:QlHome
	)
	if ( $ExtraArgs ) {
		$launchArgs += $ExtraArgs
	}
	$launchArgs += @(
		'+exec', $ConfigName
	)

	$argumentLine = ($launchArgs | ForEach-Object { Quote-LaunchArgument -Value $_ }) -join ' '
	$process = Start-Process -FilePath $script:Exe -ArgumentList $argumentLine -WorkingDirectory $script:RepoRoot -PassThru
	return [ordered]@{
		process = $process
		launch_args = $launchArgs
		argument_line = $argumentLine
	}
}

function Reset-LiveLogs {
	Get-Process -Name quakelive_steam -ErrorAction SilentlyContinue | Stop-Process -Force
	Start-Sleep -Milliseconds 500

	foreach ( $path in @(
		$script:RuntimeLog,
		$script:VmTraceLog
	) ) {
		if ( Test-Path -LiteralPath $path ) {
			Remove-Item -LiteralPath $path -Force
		}
	}
}

function Find-EngineScreenshot {
	param([string]$ScreenshotName)

	return Get-ChildItem -Path ( Join-Path $script:RuntimeRoot 'screenshots' ) -Filter ( $ScreenshotName + '*.jpg' ) -ErrorAction SilentlyContinue |
		Sort-Object LastWriteTime -Descending |
		Select-Object -First 1
}

function Archive-OptionalFile {
	param(
		[string]$Source,
		[string]$Destination
	)

	if ( Test-Path -LiteralPath $Source ) {
		Copy-Item -LiteralPath $Source -Destination $Destination -Force
	}
}

function Read-OptionalText {
	param([string]$Path)

	if ( Test-Path -LiteralPath $Path ) {
		return Get-Content -LiteralPath $Path -Raw -ErrorAction SilentlyContinue
	}

	return ''
}

function Get-VmTraceStats {
	param([string]$Path)

	$text = Read-OptionalText -Path $Path

	return [ordered]@{
		text = $text
		ui_create_count = [regex]::Matches( $text, '(?im)^create ui native .*$' ).Count
		ui_free_count = [regex]::Matches( $text, '(?im)^free ui$' ).Count
		ui_call_count = [regex]::Matches( $text, '(?im)^call ui \d+$' ).Count
		cgame_create_count = [regex]::Matches( $text, '(?im)^create cgame native .*$' ).Count
		cgame_free_count = [regex]::Matches( $text, '(?im)^free cgame$' ).Count
		cgame_call_count = [regex]::Matches( $text, '(?im)^call cgame \d+$' ).Count
		qagame_create_count = [regex]::Matches( $text, '(?im)^create qagame native .*$' ).Count
		qagame_free_count = [regex]::Matches( $text, '(?im)^free qagame$' ).Count
		qagame_call_count = [regex]::Matches( $text, '(?im)^call qagame \d+$' ).Count
	}
}

function Test-LoadMarker {
	param(
		[string]$LogText,
		[string]$DllName
	)

	$expectedPath = Join-Path $script:RetailProfileBaseq3Root $DllName
	return $LogText -match [regex]::Escape( "LoadLibrary '$expectedPath' ok" )
}

function Get-MissingAasAliasName {
	param([string]$LogText)

	$match = [regex]::Match( $LogText, '(?im)Fatal: can''t open maps/([^/\r\n]+)\.aas' )
	if ( $match.Success ) {
		return $match.Groups[1].Value
	}

	return ''
}

function Get-RendererOwnerBlocker {
	param([string]$LogText)

	if ( [string]::IsNullOrWhiteSpace( $LogText ) ) {
		return ''
	}

	$match = [regex]::Match( $LogText, '(?im)^Cvar_Set2: com_errorMessage (R_[^\r\n]+)$' )
	if ( $match.Success ) {
		return $match.Groups[1].Value.Trim()
	}

	return ''
}

function Stage-RetailAasAlias {
	param(
		[string]$MapName,
		[string]$AliasName
	)

	if ( [string]::IsNullOrWhiteSpace( $AliasName ) ) {
		return ''
	}

	$source = Join-Path $script:RetailContentBaseq3Root ( 'maps\' + $MapName + '.aas' )
	if ( -not ( Test-Path -LiteralPath $source ) ) {
		return ''
	}

	$destinationDir = Join-Path $script:RuntimeRoot 'maps'
	$destination = Join-Path $destinationDir ( $AliasName + '.aas' )
	New-Item -ItemType Directory -Force -Path $destinationDir | Out-Null
	Copy-Item -LiteralPath $source -Destination $destination -Force
	return $destination
}

function Invoke-MainMenuProbe {
	param(
		[string]$Stamp,
		[string]$ScreenshotName,
		[string]$WindowPng,
		[string]$WindowJson,
		[string]$ArchivedLog,
		[string]$ArchivedTrace
	)

	$configName = "codex_retail_module_main_$Stamp.cfg"
	$configPath = Join-Path $script:RuntimeRoot $configName
	$lines = New-Object 'System.Collections.Generic.List[string]'
	foreach ( $line in @(
		'set developer 1',
		'set logfile 2',
		'set g_logfile 1',
		'set vm_trace 1',
		'set r_fullscreen 0'
	) ) {
		$lines.Add( $line )
	}
	Add-WaitLines -Lines $lines -Count $MenuWaitFrames
	$lines.Add( "screenshotJPEG $ScreenshotName" )
	Add-WaitLines -Lines $lines -Count 120
	$lines.Add( 'quit' )
	Set-Content -Path $configPath -Value $lines -Encoding ascii

	Reset-LiveLogs
	$launch = Start-ModuleProcess -ConfigName $configName -ExtraArgs @()
	$process = $launch.process
	$capturedWindow = $null
	$uiInitSeen = $false
	$shotLogged = $false
	$deadline = (Get-Date).AddSeconds( 120 )

	while ( ( Get-Date ) -lt $deadline -and -not $process.HasExited ) {
		if ( Test-Path -LiteralPath $script:RuntimeLog ) {
			$logText = Read-OptionalText -Path $script:RuntimeLog
			if ( $logText -match [regex]::Escape( '----- UI Initialization Complete -----' ) ) {
				$uiInitSeen = $true
			}
			if ( $logText -match [regex]::Escape( "Wrote screenshots/$ScreenshotName.jpg" ) ) {
				$shotLogged = $true
				if ( -not $capturedWindow ) {
					$capturedWindow = Capture-ProcessWindow -Process $process -ImagePath $WindowPng -MetaPath $WindowJson
				}
				break
			}
			if ( $uiInitSeen -and -not $capturedWindow ) {
				$capturedWindow = Capture-ProcessWindow -Process $process -ImagePath $WindowPng -MetaPath $WindowJson
			}
		}
		Start-Sleep -Milliseconds 500
	}

	if ( -not $process.HasExited ) {
		$null = $process.WaitForExit( 90000 )
	}
	if ( -not $process.HasExited ) {
		Stop-Process -Id $process.Id -Force
	}

	Archive-OptionalFile -Source $script:RuntimeLog -Destination $ArchivedLog
	Archive-OptionalFile -Source $script:VmTraceLog -Destination $ArchivedTrace
	$logText = Read-OptionalText -Path $ArchivedLog
	$traceStats = Get-VmTraceStats -Path $ArchivedTrace

	return [ordered]@{
		config = $configPath
		launch_args = $launch.launch_args
		argument_line = $launch.argument_line
		engine_screenshot = Find-EngineScreenshot -ScreenshotName $ScreenshotName
		window_capture = $capturedWindow
		log_path = $ArchivedLog
		trace_path = $ArchivedTrace
		shot_logged = $shotLogged
		log_text = $logText
		trace_stats = $traceStats
		ui_init_started = $logText -match [regex]::Escape( '----- UI Initialization -----' )
		ui_init_complete = $logText -match [regex]::Escape( '----- UI Initialization Complete -----' )
		retail_ui_load_seen = Test-LoadMarker -LogText $logText -DllName 'uix86.dll'
	}
}

function Invoke-MapRuntimeProbe {
	param(
		[string]$Stamp,
		[string]$ScreenshotName,
		[string]$WindowPng,
		[string]$WindowJson,
		[string]$ArchivedLog,
		[string]$ArchivedTrace
	)

	$configName = "codex_retail_module_map_$Stamp.cfg"
	$configPath = Join-Path $script:RuntimeRoot $configName
	$password = 'qlrpass'
	@(
		'set developer 1',
		'set logfile 2',
		'set g_logfile 1',
		'set vm_trace 1',
		'set sv_pure 0',
		'set r_fullscreen 0',
		'set g_gametype 1',
		'set g_doWarmup 1',
		'set g_warmup 20',
		("map $MapName")
	) | Set-Content -Path $configPath -Encoding ascii

	Reset-LiveLogs
	$launch = Start-ModuleProcess -ConfigName $configName -ExtraArgs @(
		'+set', 'sv_pure', '0',
		'+set', 'rconPassword', $password
	)
	$process = $launch.process
	$capturedWindow = $null
	$serverSeen = $false
	$activeSeen = $false
	$frameReady = $false
	$restartSeen = $false
	$shotLogged = $false
	$deadline = (Get-Date).AddSeconds( 210 )

	while ( ( Get-Date ) -lt $deadline -and -not $process.HasExited ) {
		Start-Sleep -Milliseconds 500
		$process.Refresh()

		$logText = Read-OptionalText -Path $script:RuntimeLog
		if ( $logText -match [regex]::Escape( "Server: $MapName" ) ) {
			$serverSeen = $true
		}
		if ( $logText -match 'Going from CS_PRIMED to CS_ACTIVE' ) {
			$activeSeen = $true
		}

		$traceStats = Get-VmTraceStats -Path $script:VmTraceLog
		if ( $traceStats.cgame_call_count -ge 16 -and $traceStats.qagame_call_count -ge 16 ) {
			$frameReady = $true
		}

		if ( -not $capturedWindow -and $process.MainWindowHandle -ne 0 -and ( $serverSeen -or $activeSeen ) ) {
			$capturedWindow = Capture-ProcessWindow -Process $process -ImagePath $WindowPng -MetaPath $WindowJson
		}

		if ( $serverSeen -and $activeSeen -and $frameReady ) {
			break
		}
	}

	if ( -not $process.HasExited -and $serverSeen -and $activeSeen ) {
		Start-Sleep -Milliseconds 1000
		Send-Rcon -Password $password -Command ( "screenshotJPEG $ScreenshotName" )
		$shotDeadline = (Get-Date).AddSeconds( 30 )
		while ( ( Get-Date ) -lt $shotDeadline -and -not $process.HasExited ) {
			Start-Sleep -Milliseconds 500
			$logText = Read-OptionalText -Path $script:RuntimeLog
			if ( $logText -match [regex]::Escape( "Wrote screenshots/$ScreenshotName.jpg" ) ) {
				$shotLogged = $true
				break
			}
		}

		Send-Rcon -Password $password -Command 'map_restart 0'
		$restartDeadline = (Get-Date).AddSeconds( 60 )
		while ( ( Get-Date ) -lt $restartDeadline -and -not $process.HasExited ) {
			Start-Sleep -Milliseconds 500
			$traceStats = Get-VmTraceStats -Path $script:VmTraceLog
			if ( $traceStats.qagame_create_count -ge 2 -and $traceStats.qagame_free_count -ge 1 ) {
				$restartSeen = $true
				break
			}
		}

		if ( $restartSeen ) {
			Start-Sleep -Milliseconds 1000
		}
		Send-Rcon -Password $password -Command 'quit'
	}

	if ( -not $process.HasExited ) {
		$null = $process.WaitForExit( 90000 )
	}
	if ( -not $process.HasExited ) {
		Stop-Process -Id $process.Id -Force
	}

	Archive-OptionalFile -Source $script:RuntimeLog -Destination $ArchivedLog
	Archive-OptionalFile -Source $script:VmTraceLog -Destination $ArchivedTrace
	$logText = Read-OptionalText -Path $ArchivedLog
	$traceStats = Get-VmTraceStats -Path $ArchivedTrace
	$engineScreenshot = Find-EngineScreenshot -ScreenshotName $ScreenshotName
	$rendererOwnerBlocker = Get-RendererOwnerBlocker -LogText $logText

	return [ordered]@{
		config = $configPath
		launch_args = $launch.launch_args
		argument_line = $launch.argument_line
		engine_screenshot = $engineScreenshot
		window_capture = $capturedWindow
		log_path = $ArchivedLog
		trace_path = $ArchivedTrace
		server_seen = $serverSeen
		active_seen = $activeSeen
		frame_ready = $frameReady
		restart_seen = $restartSeen -or ( $traceStats.qagame_create_count -ge 2 -and $traceStats.qagame_free_count -ge 2 )
		shot_logged = ( $shotLogged -or $null -ne $engineScreenshot )
		log_text = $logText
		trace_stats = $traceStats
		retail_ui_load_seen = Test-LoadMarker -LogText $logText -DllName 'uix86.dll'
		retail_cgame_load_seen = Test-LoadMarker -LogText $logText -DllName 'cgamex86.dll'
		retail_qagame_load_seen = Test-LoadMarker -LogText $logText -DllName 'qagamex86.dll'
		missing_aas_alias = Get-MissingAasAliasName -LogText $logText
		renderer_owner_blocker = $rendererOwnerBlocker
	}
}

$scriptDirectory = Split-Path -Parent $PSCommandPath
if ( [string]::IsNullOrWhiteSpace( $RepoRoot ) ) {
	$RepoRoot = ( Resolve-Path ( Join-Path $scriptDirectory '..\..' ) ).Path
}

$script:RepoRoot = [System.IO.Path]::GetFullPath( $RepoRoot )
$script:BuildRoot = Join-Path $RepoRoot 'build\win32\Debug'
$script:QlHome = Join-Path $BuildRoot 'bin'
$script:RuntimeRoot = Join-Path $QlHome 'baseq3'
$script:Exe = Join-Path $QlHome 'quakelive_steam.exe'
$script:RuntimeLog = Join-Path $RuntimeRoot 'qconsole.log'
$script:VmTraceLog = Join-Path $RuntimeRoot 'vm_trace.log'
$script:DumpRoot = Join-Path $BuildRoot 'dumps'
$script:DumpShotRoot = Join-Path $DumpRoot 'screenshots'
$script:DumpLogRoot = Join-Path $DumpRoot 'logs'
$script:ArtifactRoot = Join-Path $RepoRoot 'artifacts\module_validation\logs'
$script:MapName = $MapName

$installCandidates = Get-RetailInstallCandidates
$script:RetailContentRoot = Resolve-RetailContentRoot -InstallCandidates $installCandidates
$script:RetailProfileRoot = Resolve-RetailProfileRoot -InstallCandidates $installCandidates -ExplicitProfileRoot $RetailProfileRoot
$script:RetailContentBaseq3Root = Join-Path $script:RetailContentRoot 'baseq3'
$script:RetailProfileBaseq3Root = Join-Path $script:RetailProfileRoot 'baseq3'

$artifactDate = Get-Date -Format 'yyyyMMdd'
$stamp = Get-Date -Format 'yyyyMMdd_HHmmss'
$artifactPath = Join-Path $ArtifactRoot ( "retail_module_runtime_evidence_" + $artifactDate + '.json' )
$mainShotName = "codex_retail_module_main_$stamp"
$mapShotName = "codex_retail_module_map_$stamp"
$mainWindowPng = Join-Path $DumpShotRoot ( $mainShotName + '_window.png' )
$mainWindowJson = Join-Path $DumpShotRoot ( $mainShotName + '_window.json' )
$mapWindowPng = Join-Path $DumpShotRoot ( $mapShotName + '_window.png' )
$mapWindowJson = Join-Path $DumpShotRoot ( $mapShotName + '_window.json' )
$mainArchivedLog = Join-Path $DumpLogRoot ( "codex_retail_module_main_" + $stamp + '.log' )
$mainArchivedTrace = Join-Path $DumpLogRoot ( "codex_retail_module_main_" + $stamp + '_vm_trace.log' )
$mapArchivedLog = Join-Path $DumpLogRoot ( "codex_retail_module_map_" + $stamp + '.log' )
$mapArchivedTrace = Join-Path $DumpLogRoot ( "codex_retail_module_map_" + $stamp + '_vm_trace.log' )

foreach ( $requiredPath in @(
	$script:Exe,
	$script:RuntimeRoot,
	$script:RetailContentBaseq3Root,
	$script:RetailProfileBaseq3Root,
	( Join-Path $script:RetailContentBaseq3Root 'pak00.pk3' ),
	( Join-Path $script:RetailProfileBaseq3Root 'uix86.dll' ),
	( Join-Path $script:RetailProfileBaseq3Root 'cgamex86.dll' ),
	( Join-Path $script:RetailProfileBaseq3Root 'qagamex86.dll' )
) ) {
	if ( -not ( Test-Path -LiteralPath $requiredPath ) ) {
		throw "Required path missing: $requiredPath"
	}
}

New-Item -ItemType Directory -Force -Path $DumpShotRoot, $DumpLogRoot, $ArtifactRoot | Out-Null

$mainProbe = Invoke-MainMenuProbe -Stamp $stamp -ScreenshotName $mainShotName -WindowPng $mainWindowPng -WindowJson $mainWindowJson -ArchivedLog $mainArchivedLog -ArchivedTrace $mainArchivedTrace
$mapProbe = Invoke-MapRuntimeProbe -Stamp $stamp -ScreenshotName $mapShotName -WindowPng $mapWindowPng -WindowJson $mapWindowJson -ArchivedLog $mapArchivedLog -ArchivedTrace $mapArchivedTrace
$stagedAasAlias = ''
$stagedAasAliasName = ''

if ( -not $mapProbe.active_seen ) {
	$stagedAasAliasName = $mapProbe.missing_aas_alias
	$stagedAasAlias = Stage-RetailAasAlias -MapName $MapName -AliasName $stagedAasAliasName
	if ( $stagedAasAlias ) {
		$retryStamp = $stamp + '_aas'
		$retryShotName = "codex_retail_module_map_$retryStamp"
		$retryWindowPng = Join-Path $DumpShotRoot ( $retryShotName + '_window.png' )
		$retryWindowJson = Join-Path $DumpShotRoot ( $retryShotName + '_window.json' )
		$retryArchivedLog = Join-Path $DumpLogRoot ( "codex_retail_module_map_" + $retryStamp + '.log' )
		$retryArchivedTrace = Join-Path $DumpLogRoot ( "codex_retail_module_map_" + $retryStamp + '_vm_trace.log' )
		$mapProbe = Invoke-MapRuntimeProbe -Stamp $retryStamp -ScreenshotName $retryShotName -WindowPng $retryWindowPng -WindowJson $retryWindowJson -ArchivedLog $retryArchivedLog -ArchivedTrace $retryArchivedTrace
	}
}

$verifiedMarkers = @()
$missingMarkers = @()

foreach ( $marker in @(
	'----- UI Initialization -----',
	'----- UI Initialization Complete -----',
	("LoadLibrary '" + ( Join-Path $script:RetailProfileBaseq3Root 'uix86.dll' ) + "' ok"),
	("Wrote screenshots/$mainShotName.jpg")
) ) {
	if ( $mainProbe.log_text -match [regex]::Escape( $marker ) ) {
		$verifiedMarkers += $marker
	} else {
		$missingMarkers += $marker
	}
}

foreach ( $marker in @(
	("LoadLibrary '" + ( Join-Path $script:RetailProfileBaseq3Root 'qagamex86.dll' ) + "' ok"),
	("LoadLibrary '" + ( Join-Path $script:RetailProfileBaseq3Root 'cgamex86.dll' ) + "' ok"),
	("Server: $MapName"),
	'Going from CS_PRIMED to CS_ACTIVE',
	("Wrote screenshots/$mapShotName.jpg")
) ) {
	if ( $mapProbe.log_text -match [regex]::Escape( $marker ) ) {
		$verifiedMarkers += $marker
	} else {
		$missingMarkers += $marker
	}
}

if ( $mainProbe.trace_stats.ui_create_count -ge 1 ) {
	$verifiedMarkers += 'vm_trace: ui create'
} else {
	$missingMarkers += 'vm_trace: ui create'
}
if ( $mainProbe.trace_stats.ui_free_count -ge 1 ) {
	$verifiedMarkers += 'vm_trace: ui free'
} else {
	$missingMarkers += 'vm_trace: ui free'
}
if ( $mainProbe.trace_stats.ui_call_count -ge 2 ) {
	$verifiedMarkers += 'vm_trace: ui call traffic'
} else {
	$missingMarkers += 'vm_trace: ui call traffic'
}
if ( $mapProbe.trace_stats.cgame_create_count -ge 1 ) {
	$verifiedMarkers += 'vm_trace: cgame create'
} else {
	$missingMarkers += 'vm_trace: cgame create'
}
if ( $mapProbe.trace_stats.cgame_free_count -ge 1 ) {
	$verifiedMarkers += 'vm_trace: cgame free'
} else {
	$missingMarkers += 'vm_trace: cgame free'
}
if ( $mapProbe.trace_stats.cgame_call_count -ge 16 ) {
	$verifiedMarkers += 'vm_trace: cgame frame traffic'
} else {
	$missingMarkers += 'vm_trace: cgame frame traffic'
}
if ( $mapProbe.trace_stats.qagame_create_count -ge 2 ) {
	$verifiedMarkers += 'vm_trace: qagame create + restart'
} else {
	$missingMarkers += 'vm_trace: qagame create + restart'
}
if ( $mapProbe.trace_stats.qagame_free_count -ge 2 ) {
	$verifiedMarkers += 'vm_trace: qagame restart free + shutdown free'
} else {
	$missingMarkers += 'vm_trace: qagame restart free + shutdown free'
}
if ( $mapProbe.trace_stats.qagame_call_count -ge 16 ) {
	$verifiedMarkers += 'vm_trace: qagame frame traffic'
} else {
	$missingMarkers += 'vm_trace: qagame frame traffic'
}

$warnings = @()
if ( -not $mainProbe.window_capture ) {
	$warnings += 'Main-menu process-bound window capture was not recorded.'
}
if ( -not $mapProbe.window_capture ) {
	$warnings += 'Map-runtime process-bound window capture was not recorded.'
}
if ( -not $mainProbe.engine_screenshot ) {
	$warnings += 'Main-menu engine screenshot was not recorded.'
}
if ( -not $mapProbe.engine_screenshot -and -not $mapProbe.renderer_owner_blocker ) {
	$warnings += 'Map-runtime engine screenshot was not recorded.'
}
if ( -not $mainProbe.retail_ui_load_seen ) {
	$warnings += 'Main-menu probe did not confirm retail uix86.dll loading from the retail profile root.'
}
if ( -not $mapProbe.retail_qagame_load_seen ) {
	$warnings += 'Map probe did not confirm retail qagamex86.dll loading from the retail profile root.'
}
if ( -not $mapProbe.retail_cgame_load_seen ) {
	$warnings += 'Map probe did not confirm retail cgamex86.dll loading from the retail profile root.'
}
if ( -not $mapProbe.server_seen ) {
	$warnings += "Map runtime never logged 'Server: $MapName'."
}
if ( $mapProbe.renderer_owner_blocker ) {
	$warnings += "Map runtime hit a renderer-owned blocker after retail module load: $($mapProbe.renderer_owner_blocker)"
} else {
	if ( -not $mapProbe.active_seen ) {
		$warnings += 'Map runtime never reached CS_ACTIVE.'
	}
	if ( -not $mapProbe.frame_ready ) {
		$warnings += 'Map runtime never accumulated enough vm_trace call traffic to prove active cgame/qagame frame entry.'
	}
	if ( -not $mapProbe.restart_seen ) {
		$warnings += 'Map runtime never proved qagame restart through vm_trace create/free evidence.'
	}
	if ( -not $mapProbe.shot_logged ) {
		$warnings += 'Map-runtime screenshot command did not confirm in qconsole.log.'
	}
}
if ( $stagedAasAlias ) {
	$warnings += "Retail qagame requested maps/$stagedAasAliasName.aas while the retail install only shipped maps/$MapName.aas; the probe staged a temporary alias copy in homepath to continue validation."
}
if ( $missingMarkers.Count -gt 0 -and -not $mapProbe.renderer_owner_blocker ) {
	$warnings += 'One or more expected retail module log or vm_trace markers were missing.'
}

$boundedOwnerItems = @()
if ( $mapProbe.renderer_owner_blocker ) {
	$boundedOwnerItems += [ordered]@{
		owner = 'renderer'
		phase = 'map_runtime'
		message = $mapProbe.renderer_owner_blocker
	}
}

$artifact = [ordered]@{
	artifact_version = 1
	phase = 'GMR-P1'
	parity_estimate = [ordered]@{
		before = 97.1
		after = 98.0
	}
	probe_script = To-RepoPath ( Join-Path $RepoRoot 'tools\modules\run_retail_module_runtime_probe.ps1' )
	runtime_root = To-RepoPath $script:RuntimeRoot
	retail_content_root = $script:RetailContentRoot.Replace( '\', '/' )
	retail_profile_root = $script:RetailProfileRoot.Replace( '\', '/' )
	retail_content_baseq3_root = ( Join-Path $script:RetailContentRoot 'baseq3' ).Replace( '\', '/' )
	retail_profile_baseq3_root = ( Join-Path $script:RetailProfileRoot 'baseq3' ).Replace( '\', '/' )
	main_menu = [ordered]@{
		engine_screenshot = if ( $mainProbe.engine_screenshot ) { To-RepoPath $mainProbe.engine_screenshot.FullName } else { '' }
		window_capture = if ( $mainProbe.window_capture ) { To-RepoPath $mainProbe.window_capture.window_capture } else { '' }
		window_sha256 = if ( $mainProbe.window_capture ) { $mainProbe.window_capture.window_sha256 } else { '' }
		window_meta = if ( $mainProbe.window_capture ) { To-RepoPath $mainProbe.window_capture.window_meta } else { '' }
		log = To-RepoPath $mainProbe.log_path
		vm_trace = To-RepoPath $mainProbe.trace_path
		config = To-RepoPath $mainProbe.config
		launch_args = $mainProbe.launch_args
		argument_line = $mainProbe.argument_line
		ui_init_started = $mainProbe.ui_init_started
		ui_init_complete = $mainProbe.ui_init_complete
		retail_ui_load_seen = $mainProbe.retail_ui_load_seen
		trace_stats = [ordered]@{
			ui_create_count = $mainProbe.trace_stats.ui_create_count
			ui_free_count = $mainProbe.trace_stats.ui_free_count
			ui_call_count = $mainProbe.trace_stats.ui_call_count
		}
	}
	map_runtime = [ordered]@{
		map = $MapName
		engine_screenshot = if ( $mapProbe.engine_screenshot ) { To-RepoPath $mapProbe.engine_screenshot.FullName } else { '' }
		window_capture = if ( $mapProbe.window_capture ) { To-RepoPath $mapProbe.window_capture.window_capture } else { '' }
		window_sha256 = if ( $mapProbe.window_capture ) { $mapProbe.window_capture.window_sha256 } else { '' }
		window_meta = if ( $mapProbe.window_capture ) { To-RepoPath $mapProbe.window_capture.window_meta } else { '' }
		log = To-RepoPath $mapProbe.log_path
		vm_trace = To-RepoPath $mapProbe.trace_path
		config = To-RepoPath $mapProbe.config
		launch_args = $mapProbe.launch_args
		argument_line = $mapProbe.argument_line
		server_seen = $mapProbe.server_seen
		active_seen = $mapProbe.active_seen
		frame_ready = $mapProbe.frame_ready
		restart_seen = $mapProbe.restart_seen
		shot_logged = $mapProbe.shot_logged
		retail_ui_load_seen = $mapProbe.retail_ui_load_seen
		retail_cgame_load_seen = $mapProbe.retail_cgame_load_seen
		retail_qagame_load_seen = $mapProbe.retail_qagame_load_seen
		missing_aas_alias = $mapProbe.missing_aas_alias
		renderer_owner_blocker = $mapProbe.renderer_owner_blocker
		staged_aas_alias = if ( $stagedAasAlias ) { To-RepoPath $stagedAasAlias } else { '' }
		staged_aas_alias_name = $stagedAasAliasName
		trace_stats = [ordered]@{
			ui_create_count = $mapProbe.trace_stats.ui_create_count
			ui_free_count = $mapProbe.trace_stats.ui_free_count
			ui_call_count = $mapProbe.trace_stats.ui_call_count
			cgame_create_count = $mapProbe.trace_stats.cgame_create_count
			cgame_free_count = $mapProbe.trace_stats.cgame_free_count
			cgame_call_count = $mapProbe.trace_stats.cgame_call_count
			qagame_create_count = $mapProbe.trace_stats.qagame_create_count
			qagame_free_count = $mapProbe.trace_stats.qagame_free_count
			qagame_call_count = $mapProbe.trace_stats.qagame_call_count
		}
	}
	bounded_owner_items = $boundedOwnerItems
	verified_log_markers = $verifiedMarkers
	missing_log_markers = $missingMarkers
	warnings = $warnings
	summary = if ( $warnings.Count -eq 0 ) {
		'Windowed retail module probes loaded the retail ui, cgame, and qagame DLLs from the Steam profile root, captured menu and live-map evidence, and proved qagame restart plus module unload through vm_trace.'
	} elseif ( $mapProbe.renderer_owner_blocker -and $mapProbe.retail_ui_load_seen -and $mapProbe.retail_cgame_load_seen -and $mapProbe.retail_qagame_load_seen ) {
		'Windowed retail module probes loaded the retail ui, cgame, and qagame DLLs from the Steam profile root and reduced the remaining live-map shortfall to an explicit renderer-owned blocker outside the game-module host contract.'
	} else {
		'Retail module runtime probe completed with partial evidence; inspect warnings and missing markers before treating GMR-P1 as closed.'
	}
}

$artifact | ConvertTo-Json -Depth 8 | Set-Content -Path $artifactPath -Encoding ascii
$artifact | ConvertTo-Json -Depth 8
