[CmdletBinding()]
param(
    [switch]$RequireV100
)

$ErrorActionPreference = 'Stop'

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

function Test-V100Component {
    param(
        [string]$VsWhere
    )

    if (-not $VsWhere) {
        return $false
    }

    $json = & $VsWhere -products * -requires Microsoft.VisualStudio.Component.VC.v100.x86.x64 -format json 2>$null
    if ($LASTEXITCODE -eq 0 -and $json) {
        $data = $json | ConvertFrom-Json
        if ($data -and $data.Count -gt 0) {
            return $true
        }
    }

    $legacyRoot = 'C:\Program Files (x86)\Microsoft Visual Studio 10.0\VC\bin\cl.exe'
    return (Test-Path $legacyRoot)
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

$vsWherePath = Get-VsWherePath
$v100Available = Test-V100Component -VsWhere $vsWherePath
if (-not $v100Available -and $RequireV100) {
    Write-Error 'Visual Studio 2010 (v100) toolset not found. Install VS2010 SP1 or add the "Visual Studio 2010 Tools" component to a newer Visual Studio instance.'
}
elseif (-not $v100Available) {
    Write-Warning 'Visual Studio 2010 (v100) toolset not found; builds targeting Quake Live DLLs cannot be reproduced yet.'
}
else {
    Write-Host 'Detected Visual Studio installation with v100 toolset support.'
}

$dumpbinPath = Get-DumpbinPath -VsWhere $vsWherePath
if (-not $dumpbinPath) {
    Write-Error 'Unable to locate dumpbin.exe in any Visual Studio installation.'
}
else {
    Write-Host "dumpbin.exe located at: $dumpbinPath"
}
