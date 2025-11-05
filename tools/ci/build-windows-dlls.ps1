[CmdletBinding()]
param(
    [string]$RepoRoot = (Resolve-Path (Join-Path $PSScriptRoot '../..')).Path,
    [string]$Solution = 'src/code/quake3.sln',
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
