[CmdletBinding()]
param(
    [ValidateSet('v100', 'v141', 'v143')]
    [string]$PlatformToolset = 'v143',
    [switch]$RequireToolset,
    [switch]$RequireV100
)

$ErrorActionPreference = 'Stop'

if ($RequireV100) {
    $PlatformToolset = 'v100'
    $RequireToolset = $true
}

function Get-VsWherePath {
    $candidates = @(
        (Join-Path ${env:ProgramFiles(x86)} 'Microsoft Visual Studio/Installer/vswhere.exe'),
        (Join-Path ${env:ProgramFiles} 'Microsoft Visual Studio/Installer/vswhere.exe')
    )
    foreach ($path in $candidates) {
        if (Test-Path $path) {
            return $path
        }
    }
    return $null
}

function Get-ToolsetSpec {
    param(
        [string]$RequestedToolset
    )

    switch ($RequestedToolset) {
        'v100' {
            return @{
                ComponentId = 'Microsoft.VisualStudio.Component.VC.v100.x86.x64'
                DisplayName = 'Visual Studio 2010 (v100)'
                LegacyRoots = @('C:\Program Files (x86)\Microsoft Visual Studio 10.0\VC\bin\cl.exe')
            }
        }
        'v141' {
            return @{
                ComponentId = 'Microsoft.VisualStudio.Component.VC.v141.x86.x64'
                DisplayName = 'Visual Studio 2017 (v141)'
                LegacyRoots = @()
            }
        }
        'v143' {
            return @{
                ComponentId = 'Microsoft.VisualStudio.Component.VC.Tools.x86.x64'
                DisplayName = 'Visual Studio 2022 (v143)'
                LegacyRoots = @()
            }
        }
    }

    throw "Unsupported PlatformToolset '$RequestedToolset'."
}

function Test-ToolsetComponent {
    param(
        [string]$VsWhere,
        [hashtable]$ToolsetSpec
    )

    if (-not $ToolsetSpec) {
        return $false
    }

    if ($VsWhere) {
        $json = & $VsWhere -products * -requires $ToolsetSpec.ComponentId -format json 2>$null
        if ($LASTEXITCODE -eq 0 -and $json) {
            $data = $json | ConvertFrom-Json
            if ($data -and $data.Count -gt 0) {
                return $true
            }
        }
    }

    foreach ($legacyRoot in $ToolsetSpec.LegacyRoots) {
        if (Test-Path $legacyRoot) {
            return $true
        }
    }

    return $false
}

function Get-DumpbinPath {
    param(
        [string]$VsWhere
    )

    $command = Get-Command dumpbin.exe -ErrorAction SilentlyContinue
    if ($command) {
        return $command.Source
    }

    if ($VsWhere) {
        $json = & $VsWhere -products * -requires Microsoft.VisualStudio.Component.VC.Tools.x86.x64 -format json 2>$null
        if ($LASTEXITCODE -eq 0 -and $json) {
            $data = $json | ConvertFrom-Json
            foreach ($install in $data) {
                $root = $install.installationPath
                $search = Join-Path $root 'VC/Tools/MSVC'
                if (Test-Path $search) {
                    $candidate = Get-ChildItem -Path $search -Directory | Sort-Object Name -Descending | ForEach-Object {
                        Join-Path $_.FullName 'bin/Hostx64/x86/dumpbin.exe'
                    } | Where-Object { Test-Path $_ } | Select-Object -First 1
                    if ($candidate) {
                        return $candidate
                    }
                }
            }
        }
    }

    return $null
}

$toolsetSpec = Get-ToolsetSpec -RequestedToolset $PlatformToolset
$vsWherePath = Get-VsWherePath
$toolsetAvailable = Test-ToolsetComponent -VsWhere $vsWherePath -ToolsetSpec $toolsetSpec
if (-not $toolsetAvailable -and $RequireToolset) {
    Write-Error "$($toolsetSpec.DisplayName) toolset not found. Install the '$PlatformToolset' build tools or add component '$($toolsetSpec.ComponentId)' to a newer Visual Studio instance."
}
elseif (-not $toolsetAvailable) {
    Write-Warning "$($toolsetSpec.DisplayName) toolset not found."
}
else {
    Write-Host "Detected Visual Studio installation with $($toolsetSpec.DisplayName) support."
}

$dumpbinPath = Get-DumpbinPath -VsWhere $vsWherePath
if (-not $dumpbinPath) {
    Write-Error 'Unable to locate dumpbin.exe in any Visual Studio installation.'
}
else {
    Write-Host "dumpbin.exe located at: $dumpbinPath"
}
