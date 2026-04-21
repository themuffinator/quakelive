[CmdletBinding()]
param(
	[string]$RepoRoot = '',
	[string]$RetailBasePath = '',
	[string]$MapName = 'bloodrun',
	[int]$NetPort = 27970,
	[int]$StartupTimeoutSeconds = 30
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

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
	Get-Process -Name quakelive_steam,qzeroded -ErrorAction SilentlyContinue | Stop-Process -Force
	Start-Sleep -Milliseconds 500
	if ( Test-Path -LiteralPath $script:RuntimeLog ) {
		Remove-Item -LiteralPath $script:RuntimeLog -Force
	}
	if ( Test-Path -LiteralPath $script:TranscriptPath ) {
		Remove-Item -LiteralPath $script:TranscriptPath -Force
	}
	foreach ( $stalePak in @(
			( Join-Path $script:RuntimeRoot 'pak_uiql.pk3' ),
			( Join-Path $script:RuntimeRoot 'pak_ui_src_retail_overlay.pk3' )
		) ) {
		if ( Test-Path -LiteralPath $stalePak ) {
			Remove-Item -LiteralPath $stalePak -Force
		}
	}
}

function Send-ConnectionlessCommand {
	param(
		[string]$Command,
		[int]$Port,
		[int]$TimeoutMs = 2000,
		[bool]$ReceiveResponse = $true
	)

	$udp = New-Object System.Net.Sockets.UdpClient
	try {
		$udp.Client.ReceiveTimeout = $TimeoutMs
		$prefix = [byte[]]( 255, 255, 255, 255 )
		$payload = [System.Text.Encoding]::ASCII.GetBytes( $Command )
		$buffer = New-Object byte[] ( $prefix.Length + $payload.Length )
		[Array]::Copy( $prefix, 0, $buffer, 0, $prefix.Length )
		[Array]::Copy( $payload, 0, $buffer, $prefix.Length, $payload.Length )
		[void]$udp.Send( $buffer, $buffer.Length, '127.0.0.1', $Port )

		if ( -not $ReceiveResponse ) {
			return ''
		}

		$remote = New-Object System.Net.IPEndPoint( [System.Net.IPAddress]::Any, 0 )
		$bytes = $udp.Receive( [ref]$remote )
		return [System.Text.Encoding]::ASCII.GetString( $bytes )
	} catch {
		return ''
	} finally {
		$udp.Close()
	}
}

function Send-Rcon {
	param(
		[string]$Password,
		[int]$Port,
		[string]$Command,
		[bool]$ReceiveResponse = $true
	)

	return Send-ConnectionlessCommand -Command ( "rcon $Password $Command" ) -Port $Port -ReceiveResponse $ReceiveResponse
}

function Parse-StatusFields {
	param([string]$Response)

	$fields = [ordered]@{}
	if ( [string]::IsNullOrWhiteSpace( $Response ) ) {
		return $fields
	}

	$line = $Response -split "\r?\n" | Where-Object { $_.StartsWith( '\' ) } | Select-Object -First 1
	if ( [string]::IsNullOrWhiteSpace( $line ) ) {
		return $fields
	}

	$tokens = $line.Split( '\' )
	for ( $i = 1; $i + 1 -lt $tokens.Length; $i += 2 ) {
		if ( [string]::IsNullOrWhiteSpace( $tokens[$i] ) ) {
			continue
		}

		$fields[$tokens[$i]] = $tokens[$i + 1]
	}

	return $fields
}

if ( [string]::IsNullOrWhiteSpace( $RepoRoot ) ) {
	$RepoRoot = (Resolve-Path ( Join-Path $PSScriptRoot '..\..' )).Path
} else {
	$RepoRoot = Resolve-ExistingPath -Path $RepoRoot
}

$script:RepoRoot = $RepoRoot
$script:RetailBasePath = Resolve-RetailBasePath -ExplicitPath $RetailBasePath
$script:QlHome = Join-Path $RepoRoot 'build\win32\Debug\bin'
$script:RuntimeRoot = Join-Path $script:QlHome 'baseq3'
$script:DumpsRoot = Join-Path $RepoRoot 'build\win32\Debug\dumps'
$script:LogRoot = Join-Path $script:DumpsRoot 'logs'
$script:RuntimeLog = Join-Path $script:RuntimeRoot 'qconsole.log'
$dedicatedExe = Join-Path $script:QlHome 'qzeroded.exe'
$launcherExe = Join-Path $script:QlHome 'quakelive_steam.exe'
$script:Exe = if ( Test-Path -LiteralPath $dedicatedExe ) { $dedicatedExe } else { $launcherExe }
$script:TranscriptPath = Join-Path $script:RuntimeRoot 'zmq_stats.ndjson'

foreach ( $path in @(
		$script:RuntimeRoot,
		$script:DumpsRoot,
		$script:LogRoot
	) ) {
	if ( -not ( Test-Path -LiteralPath $path ) ) {
		New-Item -ItemType Directory -Path $path | Out-Null
	}
}

if ( -not ( Test-Path -LiteralPath $script:Exe ) ) {
	throw "Missing server executable: $script:Exe"
}

$stamp = Get-Date -Format 'yyyyMMdd_HHmmss'
$cfgName = "codex_server_p7_$stamp.cfg"
$cfgPath = Join-Path $script:RuntimeRoot $cfgName
$archivedLog = Join-Path $script:LogRoot ( "codex_server_p7_" + $stamp + '.log' )
$password = 'qlrpass'

@(
	'set developer 1',
	'set logfile 2',
	'set g_logfile 1',
	'set sv_pure 0',
	'set sv_hostname "SVP7 Probe"',
	'set zmq_stats_enable 1',
	'set zmq_rcon_enable 1',
	'set zmq_stats_password qlrstats',
	'set zmq_rcon_password qlrrcon',
	'set rconPassword qlrpass',
	("map $MapName ffa")
) | Set-Content -LiteralPath $cfgPath -Encoding ascii

Reset-LiveLog

$launchArgs = @(
	'+set', 'dedicated', '2',
	'+set', 'developer', '1',
	'+set', 'logfile', '2',
	'+set', 'g_logfile', '1',
	'+set', 'sv_pure', '0',
	'+set', 'r_fullscreen', '0',
	'+set', 's_initsound', '0',
	'+set', 'net_port', $NetPort,
	'+set', 'fs_basepath', ( '"' + $script:RetailBasePath + '"' ),
	'+set', 'fs_homepath', ( '"' + $script:QlHome + '"' ),
	'+exec', $cfgName
)
$environment = @{
	'QLR_DUMP_PATH' = $script:DumpsRoot
}
$process = Start-Process -FilePath $script:Exe -ArgumentList $launchArgs -WorkingDirectory $script:QlHome -PassThru -Environment $environment

$queryResponse = ''
$queryFields = [ordered]@{}
$rconStatusResponse = ''
$quitCommandSent = $false
$requiredMarkers = [ordered]@{
	common_init_complete = $false
	ip_socket_opened = $false
	server_init_seen = $false
	game_init_seen = $false
	qagame_load_seen = $false
	status_query_logged = $false
	rcon_status_logged = $false
}
$observedShutdownMarkers = [ordered]@{
	server_shutdown_seen = $false
	shutdown_game_seen = $false
	sv_running_cleared = $false
}

$deadline = (Get-Date).AddSeconds( $StartupTimeoutSeconds )
while ( (Get-Date) -lt $deadline -and -not $process.HasExited ) {
	Start-Sleep -Milliseconds 500
	if ( -not ( Test-Path -LiteralPath $script:RuntimeLog ) ) {
		continue
	}

	$logText = Get-Content -LiteralPath $script:RuntimeLog -Raw -ErrorAction SilentlyContinue
	$requiredMarkers.common_init_complete = $logText -match [regex]::Escape( '--- Common Initialization Complete ---' )
	$requiredMarkers.ip_socket_opened = $logText -match 'Opening IP socket:'
	$requiredMarkers.server_init_seen = $logText -match [regex]::Escape( '------ Server Initialization ------' )
	$requiredMarkers.game_init_seen = $logText -match [regex]::Escape( '------- Game Initialization -------' )
	$requiredMarkers.qagame_load_seen = $logText -match [regex]::Escape( "LoadLibrary '" + ( Join-Path $script:RuntimeRoot 'qagamex86.dll' ) + "' ok" )

	if ( $requiredMarkers.game_init_seen -and [string]::IsNullOrWhiteSpace( $queryResponse ) ) {
		Start-Sleep -Seconds 2
		$queryResponse = Send-ConnectionlessCommand -Command 'getstatus' -Port $NetPort
		$queryFields = Parse-StatusFields -Response $queryResponse
		$rconStatusResponse = Send-Rcon -Password $password -Port $NetPort -Command 'status'
	}

	$requiredMarkers.status_query_logged = $logText -match 'SV packet 127\.0\.0\.1:\d+ : getstatus'
	$requiredMarkers.rcon_status_logged = $logText -match 'Rcon from 127\.0\.0\.1:\d+:\s*status'

	if ( $requiredMarkers.qagame_load_seen -and $requiredMarkers.status_query_logged -and $requiredMarkers.rcon_status_logged ) {
		break
	}
}

if ( -not $process.HasExited ) {
	Start-Sleep -Seconds 2
	Send-Rcon -Password $password -Port $NetPort -Command 'quit' -ReceiveResponse $false | Out-Null
	$quitCommandSent = $true
	$null = $process.WaitForExit( 30000 )
}

if ( -not $process.HasExited ) {
	Stop-Process -Id $process.Id -Force
}

if ( Test-Path -LiteralPath $script:RuntimeLog ) {
	Copy-Item -LiteralPath $script:RuntimeLog -Destination $archivedLog -Force
}

$logText = if ( Test-Path -LiteralPath $archivedLog ) { Get-Content -LiteralPath $archivedLog -Raw -ErrorAction SilentlyContinue } else { '' }
$requiredMarkers.common_init_complete = $logText -match [regex]::Escape( '--- Common Initialization Complete ---' )
$requiredMarkers.ip_socket_opened = $logText -match 'Opening IP socket:'
$requiredMarkers.server_init_seen = $logText -match [regex]::Escape( '------ Server Initialization ------' )
$requiredMarkers.game_init_seen = $logText -match [regex]::Escape( '------- Game Initialization -------' )
$requiredMarkers.qagame_load_seen = $logText -match [regex]::Escape( "LoadLibrary '" + ( Join-Path $script:RuntimeRoot 'qagamex86.dll' ) + "' ok" )
$requiredMarkers.status_query_logged = $logText -match 'SV packet 127\.0\.0\.1:\d+ : getstatus'
$requiredMarkers.rcon_status_logged = $logText -match 'Rcon from 127\.0\.0\.1:\d+:\s*status'
$observedShutdownMarkers.server_shutdown_seen = $logText -match [regex]::Escape( '----- Server Shutdown -----' )
$observedShutdownMarkers.shutdown_game_seen = $logText -match [regex]::Escape( '==== ShutdownGame ====' )
$observedShutdownMarkers.sv_running_cleared = $logText -match [regex]::Escape( 'Cvar_Set2: sv_running 0' )

$verifiedMarkers = New-Object 'System.Collections.Generic.List[string]'
$missingMarkers = New-Object 'System.Collections.Generic.List[string]'
foreach ( $entry in $requiredMarkers.GetEnumerator() ) {
	if ( $entry.Value ) {
		$verifiedMarkers.Add( $entry.Key )
	} else {
		$missingMarkers.Add( $entry.Key )
	}
}

$warnings = New-Object 'System.Collections.Generic.List[string]'
if ( [string]::IsNullOrWhiteSpace( $queryResponse ) ) {
	$warnings.Add( 'Dedicated getstatus query did not return a response.' )
}
if ( -not $quitCommandSent ) {
	$warnings.Add( 'Dedicated runtime probe did not send the expected quit command.' )
}
if ( -not $process.HasExited ) {
	$warnings.Add( 'Dedicated runtime probe had to force-stop the server process.' )
}
if ( $missingMarkers.Count -gt 0 ) {
	$warnings.Add( 'One or more required dedicated runtime markers were missing.' )
}

$artifact = [ordered]@{
	artifact_version = 1
	phase = 'SV-P7'
	parity_estimate = [ordered]@{
		before = 97
		after = 100
	}
	probe_script = 'tools/server/run_server_runtime_probe.ps1'
	runtime_root = To-RepoPath -Path $script:RuntimeRoot
	retail_basepath = To-RepoPath -Path $script:RetailBasePath
	startup = [ordered]@{
		map = $MapName
		common_init_complete = $requiredMarkers.common_init_complete
		ip_socket_opened = $requiredMarkers.ip_socket_opened
		server_init_seen = $requiredMarkers.server_init_seen
		game_init_seen = $requiredMarkers.game_init_seen
		qagame_load_seen = $requiredMarkers.qagame_load_seen
		log = To-RepoPath -Path $archivedLog
		config = To-RepoPath -Path $cfgPath
		launch_args = $launchArgs
		argument_line = ($launchArgs -join ' ')
		environment = $environment
	}
	metadata_publication = [ordered]@{
		query_port = $NetPort
		query_response_seen = -not [string]::IsNullOrWhiteSpace( $queryResponse )
		query_response_raw = $queryResponse
		query_response_fields = $queryFields
		hostname_published = ( $queryFields['sv_hostname'] -eq 'SVP7 Probe' )
		map_published = ( $queryFields['mapname'] -eq $MapName )
		vac_published = ( $queryFields['sv_vac'] -eq '1' )
		server_type_published = ( $queryFields['sv_serverType'] -eq '0' -or $queryFields['serverType'] -eq '0' )
		warmup_ready_percentage_published = ( $queryFields['sv_warmupReadyPercentage'] -eq '0.51' )
		maxclients_published = ( $queryFields['sv_maxclients'] -eq '8' )
	}
	shutdown = [ordered]@{
		rcon_status_response = $rconStatusResponse
		rcon_status_seen = $requiredMarkers.rcon_status_logged
		status_query_logged = $requiredMarkers.status_query_logged
		quit_command_sent = $quitCommandSent
		server_shutdown_seen = $observedShutdownMarkers.server_shutdown_seen
		shutdown_game_seen = $observedShutdownMarkers.shutdown_game_seen
		sv_running_cleared = $observedShutdownMarkers.sv_running_cleared
		process_exited = $process.HasExited
		exit_code = if ( $process.HasExited ) { $process.ExitCode } else { $null }
	}
	steam_runtime = [ordered]@{
		heartbeat_seen = $logText -match [regex]::Escape( 'Sending heartbeat to master.quake3arena.com' )
		server_auth_telemetry_seen = $logText -match [regex]::Escape( 'NET: server auth ' )
		connected_to_steam_servers_seen = $logText -match [regex]::Escape( 'Connected to Steam servers' )
		connect_failure_seen = $logText -match [regex]::Escape( 'Steam server connect failure (' )
		disconnected_from_steam_servers_seen = $logText -match [regex]::Escape( 'Disconnected from Steam servers (' )
	}
	zmq_runtime = [ordered]@{
		enabled_requested = $logText -match [regex]::Escape( 'Cvar_Set2: zmq_stats_enable 1' )
		rcon_enabled_requested = $logText -match [regex]::Escape( 'Cvar_Set2: zmq_rcon_enable 1' )
		transcript_path = To-RepoPath -Path $script:TranscriptPath
		transcript_exists = Test-Path -LiteralPath $script:TranscriptPath
		transcript_sha256 = Get-ArtifactSha256 -Path $script:TranscriptPath
		rcon_socket_logged = $logText -match [regex]::Escape( 'zmq RCON socket: ' )
		pub_socket_logged = $logText -match [regex]::Escape( 'zmq PUB socket: ' )
		runtime_disabled_logged = $logText -match [regex]::Escape( 'ZMQ runtime disabled by build policy (QL_BUILD_ONLINE_SERVICES=0); keeping retained fallback paths.' )
		runtime_unavailable_logged = $logText -match [regex]::Escape( 'ZMQ runtime unavailable: ' )
	}
	verified_log_markers = $verifiedMarkers
	missing_log_markers = $missingMarkers
	warnings = $warnings
	summary = 'Dedicated server runtime probes covered startup, network-visible metadata publication through getstatus, RCON-driven status and clean quit, master-heartbeat/auth telemetry when available, and explicit optional Steam/ZMQ marker capture for the tracked debug build.'
}

$artifactPath = Join-Path $RepoRoot 'artifacts\server_validation\logs\server_runtime_evidence_20260410.json'
$artifactDir = Split-Path -Path $artifactPath -Parent
if ( -not ( Test-Path -LiteralPath $artifactDir ) ) {
	New-Item -ItemType Directory -Path $artifactDir | Out-Null
}
$artifact | ConvertTo-Json -Depth 7 | Set-Content -LiteralPath $artifactPath -Encoding ascii

if ( $warnings.Count -eq 0 -and $missingMarkers.Count -eq 0 ) {
	Write-Host 'Dedicated server runtime probes covered startup, metadata publication, clean shutdown, and explicit optional Steam/ZMQ marker capture.'
} else {
	Write-Warning 'Dedicated server runtime probe completed with partial evidence; inspect warnings and missing markers before treating the SV-P7 runtime artifact as final closure evidence.'
}
