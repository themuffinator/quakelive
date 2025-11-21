[CmdletBinding()]
param(
    [string]$RepoRoot = (Resolve-Path (Join-Path $PSScriptRoot '../..')).Path,
    [string]$PlatformToolset = 'v100',
    [string]$Configuration = 'Release',
    [string]$Platform = 'Win32'
)

$ErrorActionPreference = 'Stop'

function Assert-PlatformToolset {
    param(
        [string]$ProjectRelativePath,
        [string]$ExpectedToolset
    )

    $projectPath = Join-Path $RepoRoot $ProjectRelativePath
    if (-not (Test-Path $projectPath)) {
        throw "Project file not found: $ProjectRelativePath"
    }

    [xml]$xml = Get-Content -Path $projectPath
    $toolsets = $xml.Project.PropertyGroup.PlatformToolset
    if (-not $toolsets) {
        throw "No <PlatformToolset> nodes were found in $ProjectRelativePath"
    }

    foreach ($toolset in $toolsets) {
        if ($toolset -ne $ExpectedToolset) {
            throw "PlatformToolset mismatch in $ProjectRelativePath: expected '$ExpectedToolset', found '$toolset'"
        }
    }

    Write-Host "Verified $ProjectRelativePath uses PlatformToolset='$ExpectedToolset'"
}

function Find-FileInPaths {
    param(
        [string]$FileName,
        [string[]]$SearchRoots
    )

    foreach ($root in $SearchRoots) {
        if (-not $root) { continue }
        if (-not (Test-Path $root)) { continue }

        $candidate = Join-Path $root $FileName
        if (Test-Path $candidate) {
            return (Resolve-Path $candidate).Path
        }
    }

    return $null
}

function Assert-FilesAvailable {
    param(
        [string[]]$FileNames,
        [string[]]$SearchRoots,
        [string]$Description
    )

    $missing = @()
    foreach ($name in $FileNames) {
        $match = Find-FileInPaths -FileName $name -SearchRoots $SearchRoots
        if (-not $match) {
            $missing += $name
        }
    }

    if ($missing.Count -gt 0) {
        $paths = $SearchRoots | Where-Object { $_ }
        $pathList = $paths -join ', '
        throw "Missing required $Description: $($missing -join ', ') (searched: $pathList)"
    }

    Write-Host "Validated required $Description are available: $($FileNames -join ', ')"
}

$projectChecks = @(
    'src/code/game/game.vcxproj',
    'src/code/cgame/cgame.vcxproj'
)
foreach ($project in $projectChecks) {
    Assert-PlatformToolset -ProjectRelativePath $project -ExpectedToolset $PlatformToolset
}

$launcherRoot = Join-Path $RepoRoot 'assets/quakelive'
$launcherPayload = @(
    'awesomium.dll',
    'libEGL.dll',
    'libGLESv2.dll',
    'avcodec-53.dll',
    'avformat-53.dll',
    'avutil-51.dll',
    'steam_api.dll',
    'icudt.dll',
    'xinput9_1_0.dll'
)
$runtimeRoots = @(
    $launcherRoot,
    (Join-Path $env:WINDIR 'System32'),
    (Join-Path $env:WINDIR 'SysWOW64')
)

Assert-FilesAvailable -FileNames @('MSVCR100.dll', 'MSVCP100.dll') -SearchRoots $runtimeRoots -Description 'Visual C++ 2010 CRT DLLs'
Assert-FilesAvailable -FileNames $launcherPayload -SearchRoots @($launcherRoot) -Description 'launcher payload DLLs'

$builder = Join-Path $PSScriptRoot 'build-windows-dlls.ps1'
& $builder -RepoRoot $RepoRoot -Configuration $Configuration -Platform $Platform -PlatformToolset $PlatformToolset
