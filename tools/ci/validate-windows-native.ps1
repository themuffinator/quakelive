[CmdletBinding()]
param(
    [string]$RepoRoot = (Resolve-Path (Join-Path $PSScriptRoot '../..')).Path,
    [string]$PlatformToolset = 'v141',
    [string]$ProjectToolset = 'v141',
    [ValidateSet('retail', 'modern')]
    [string]$RuntimeProfile = 'modern',
    [string]$Configuration = 'Release',
    [string]$Platform = 'Win32',
    [string]$WindowsTargetPlatformVersion = ''
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
    $ns = New-Object System.Xml.XmlNamespaceManager($xml.NameTable)
    $ns.AddNamespace('msb', 'http://schemas.microsoft.com/developer/msbuild/2003')
    $toolsets = $xml.SelectNodes('//msb:PlatformToolset', $ns)
    if (-not $toolsets) {
        throw "No <PlatformToolset> nodes were found in $ProjectRelativePath"
    }

    foreach ($toolset in $toolsets) {
        if ($toolset.InnerText -ne $ExpectedToolset) {
            throw "PlatformToolset mismatch in ${ProjectRelativePath}: expected '$ExpectedToolset', found '$($toolset.InnerText)'"
        }
    }

    Write-Host "Verified $ProjectRelativePath uses PlatformToolset='$ExpectedToolset'"
}

function Get-RuntimeDlls {
    param(
        [string]$Profile
    )

    switch ($Profile) {
        'retail' { return @('MSVCR100.dll', 'MSVCP100.dll') }
        'modern' { return @('VCRUNTIME140.dll', 'MSVCP140.dll', 'ucrtbase.dll') }
    }

    throw "Unsupported RuntimeProfile '$Profile'."
}

function Get-LatestWindowsSdkVersion {
    $roots = @(
        'C:\Program Files (x86)\Windows Kits\10\Include',
        'C:\Program Files\Windows Kits\10\Include'
    )

    foreach ($root in $roots) {
        if (-not (Test-Path $root)) {
            continue
        }

        $versions = Get-ChildItem -Path $root -Directory -ErrorAction SilentlyContinue | Sort-Object Name -Descending
        foreach ($version in $versions) {
            $umPath = Join-Path $version.FullName 'um'
            if (Test-Path $umPath) {
                return $version.Name
            }
        }
    }

    return $null
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
        throw "Missing required ${Description}: $($missing -join ', ') (searched: $pathList)"
    }

    Write-Host "Validated required $Description are available: $($FileNames -join ', ')"
}

$projectChecks = @(
    'src/code/game/qagamex86.vcxproj',
    'src/code/cgame/cgamex86.vcxproj',
    'src/code/ui/ui.vcxproj',
    'src/code/quakelive_steam.vcxproj',
    'src/code/awesomium_process.vcxproj'
)
foreach ($project in $projectChecks) {
    Assert-PlatformToolset -ProjectRelativePath $project -ExpectedToolset $ProjectToolset
}

if ($RuntimeProfile -eq 'retail') {
    $toolchainAudit = Join-Path $PSScriptRoot 'audit-retail-toolchain.ps1'
    & $toolchainAudit -RepoRoot $RepoRoot -Strict:$true
}
elseif ($PlatformToolset -ne $ProjectToolset) {
    Write-Host "Checked-in native project defaults remain '$ProjectToolset'; building with toolset override '$PlatformToolset'."
}

if ($RuntimeProfile -eq 'modern' -and -not $WindowsTargetPlatformVersion) {
    $WindowsTargetPlatformVersion = Get-LatestWindowsSdkVersion
    if (-not $WindowsTargetPlatformVersion) {
        throw 'Unable to locate an installed Windows 10/11 SDK for the modern compatibility build.'
    }

    Write-Host "Using Windows SDK $WindowsTargetPlatformVersion for the modern compatibility build."
}

$metadataAudit = Join-Path $PSScriptRoot 'audit-retail-metadata.ps1'
& $metadataAudit -RepoRoot $RepoRoot

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

Assert-FilesAvailable -FileNames (Get-RuntimeDlls -Profile $RuntimeProfile) -SearchRoots $runtimeRoots -Description "$RuntimeProfile runtime DLLs"
if ($RuntimeProfile -eq 'retail') {
    Assert-FilesAvailable -FileNames $launcherPayload -SearchRoots @($launcherRoot) -Description 'launcher payload DLLs'
}
else {
    $missingLauncherPayload = @()
    foreach ($name in $launcherPayload) {
        if (-not (Find-FileInPaths -FileName $name -SearchRoots @($launcherRoot))) {
            $missingLauncherPayload += $name
        }
    }

    if ($missingLauncherPayload.Count -gt 0) {
        Write-Warning "Retail launcher payload is not fully staged under '$launcherRoot'; modern compatibility validation will continue without it."
    }
    else {
        Write-Host "Validated required launcher payload DLLs are available: $($launcherPayload -join ', ')"
    }
}

$builder = Join-Path $PSScriptRoot 'build-windows-dlls.ps1'
& $builder -RepoRoot $RepoRoot -Configuration $Configuration -Platform $Platform -PlatformToolset $PlatformToolset -WindowsTargetPlatformVersion $WindowsTargetPlatformVersion

$awesomiumProcessPath = Join-Path $RepoRoot "build\win32\$Configuration\bin\awesomium_process.exe"
if (-not (Test-Path $awesomiumProcessPath)) {
    throw "Expected awesomium_process.exe at '$awesomiumProcessPath' after the native Windows build."
}

$exportAudit = Join-Path $PSScriptRoot 'assert-dll-exports.ps1'
& $exportAudit -RepoRoot $RepoRoot

Write-Host "Validated awesomium_process build output: $awesomiumProcessPath"
