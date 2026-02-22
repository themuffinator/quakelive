[CmdletBinding()]
param(
    [string]$RepoRoot = (Resolve-Path (Join-Path $PSScriptRoot '../..')).Path,
    [string]$Solution = 'src/code/quakelive.sln',
    [string]$Configuration = 'Release',
    [string]$Platform = 'Win32',
    [string]$PlatformToolset = 'v100'
)

$ErrorActionPreference = 'Stop'

$solutionPath = Join-Path $RepoRoot $Solution
if (-not (Test-Path $solutionPath)) {
    throw "Solution file not found at '$solutionPath'."
}

$msbuild = Get-Command msbuild.exe -ErrorAction SilentlyContinue
if (-not $msbuild) {
    throw 'msbuild.exe was not found in PATH. Install Visual Studio Build Tools or ensure msbuild is available.'
}

Write-Host "Building '$Solution' ($Configuration|$Platform) with toolset $PlatformToolset."
$arguments = @(
    $solutionPath,
    '/m',
    "/p:Configuration=$Configuration",
    "/p:Platform=$Platform",
    "/p:PlatformToolset=$PlatformToolset",
    '/p:PreferredToolArchitecture=x86'
)

$process = Start-Process -FilePath $msbuild.Source -ArgumentList $arguments -Wait -PassThru
if ($process.ExitCode -ne 0) {
    throw "msbuild.exe failed with exit code $($process.ExitCode)."
}

Write-Host 'Gameplay DLL build completed successfully.'

$cl = Get-Command cl.exe -ErrorAction SilentlyContinue
if (-not $cl) {
    throw 'cl.exe was not found in PATH. Ensure the Visual Studio toolchain is initialised before invoking this script.'
}

$cleanRoot = Join-Path $RepoRoot 'src-re\prototypes'
$buildRoot = Join-Path $RepoRoot 'build\re\windows'
if (-not (Test-Path $buildRoot)) {
    New-Item -ItemType Directory -Path $buildRoot | Out-Null
}

function Invoke-RePrototypeBuild {
    param(
        [string]$Name,
        [string[]]$Sources,
        [string[]]$IncludeDirs,
        [string[]]$Exports
    )

    $outputPath = Join-Path $buildRoot ("$Name.dll")
    $arguments = @('/nologo', '/LD', '/O2', '/MD', '/W3', '/DWIN32', '/D_WINDOWS', '/D_CRT_SECURE_NO_WARNINGS')
    if ($env:QLR_RE_MSVC_FLAGS) {
        $arguments += $env:QLR_RE_MSVC_FLAGS.Split(' ', [System.StringSplitOptions]::RemoveEmptyEntries)
    }
    foreach ($include in $IncludeDirs) {
        $arguments += "/I`"$include`""
    }
    foreach ($source in $Sources) {
        $arguments += "`"$source`""
    }
    $arguments += '/link'
    $arguments += "/OUT:`"$outputPath`""
    $arguments += '/MACHINE:X86'
    foreach ($export in $Exports) {
        $arguments += "/EXPORT:$export"
    }

    Write-Host "[clean-room] Building $Name -> $outputPath"
    $process = Start-Process -FilePath $cl.Source -ArgumentList $arguments -Wait -PassThru -NoNewWindow
    if ($process.ExitCode -ne 0) {
        throw "cl.exe failed while building $Name (exit code $($process.ExitCode))."
    }
}

$shimExports = @(
    'qlr_native_shim_reset_log',
    'qlr_native_shim_close',
    'qlr_native_shim_flush',
    'qlr_native_shim_logf',
    'qlr_native_shim_log_syscall'
)

Invoke-RePrototypeBuild \
    -Name 'qlr_client_frame' \
    -Sources @(
        (Join-Path $cleanRoot 'c_client\cl_frame.c'),
        (Join-Path $cleanRoot 'common\native_shim.c')
    ) \
    -IncludeDirs @(
        (Join-Path $cleanRoot 'c_client'),
        (Join-Path $cleanRoot 'common')
    ) \
    -Exports (@('CL_Frame', 'QLR_ClientFrame_BindContext', 'QLR_ClientFrame_UnbindContext') + $shimExports)

Invoke-RePrototypeBuild \
    -Name 'qlr_game_frame' \
    -Sources @(
        (Join-Path $cleanRoot 'g_gameplay\g_frame.c'),
        (Join-Path $cleanRoot 'common\native_shim.c')
    ) \
    -IncludeDirs @(
        (Join-Path $cleanRoot 'g_gameplay'),
        (Join-Path $cleanRoot 'common')
    ) \
    -Exports (@('G_RunFrame', 'QLR_Game_BindFrameContext', 'QLR_Game_UnbindFrameContext') + $shimExports)

Write-Host "Clean-room DLLs stored under $buildRoot"
