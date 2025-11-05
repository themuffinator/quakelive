[CmdletBinding()]
param(
    [string]$RepoRoot = (Resolve-Path (Join-Path $PSScriptRoot '../..')).Path
)

$ErrorActionPreference = 'Stop'

function Get-DumpbinPath {
    $command = Get-Command dumpbin.exe -ErrorAction SilentlyContinue
    if ($command) {
        return $command.Source
    }

    $vsWhereCandidates = @(
        (Join-Path ${env:ProgramFiles(x86)} 'Microsoft Visual Studio/Installer/vswhere.exe'),
        (Join-Path ${env:ProgramFiles} 'Microsoft Visual Studio/Installer/vswhere.exe')
    )

    foreach ($candidate in $vsWhereCandidates) {
        if (-not (Test-Path $candidate)) {
            continue
        }

        $json = & $candidate -products * -requires Microsoft.VisualStudio.Component.VC.Tools.x86.x64 -format json 2>$null
        if ($LASTEXITCODE -ne 0 -or -not $json) {
            continue
        }

        $data = $json | ConvertFrom-Json
        foreach ($install in $data) {
            $search = Join-Path $install.installationPath 'VC/Tools/MSVC'
            if (-not (Test-Path $search)) {
                continue
            }

            $match = Get-ChildItem -Path $search -Directory | Sort-Object Name -Descending | ForEach-Object {
                Join-Path $_.FullName 'bin/Hostx64/x86/dumpbin.exe'
            } | Where-Object { Test-Path $_ } | Select-Object -First 1

            if ($match) {
                return $match
            }
        }
    }

    return $null
}

$dumpbin = Get-DumpbinPath
if (-not $dumpbin) {
    throw 'dumpbin.exe is required to validate the Quake Live reference DLLs.'
}

$referenceDir = Join-Path $RepoRoot 'references/original-assets/quakelive/baseq3'
$targets = @(
    @{ Name = 'qagamex86.dll'; Imports = @('MSVCR100.dll', 'MSVCP100.dll') },
    @{ Name = 'cgamex86.dll'; Imports = @('MSVCR100.dll') },
    @{ Name = 'uix86.dll'; Imports = @('MSVCR100.dll') }
)

$expectedExports = @('dllEntry', 'vmMain')
$failures = @()

foreach ($target in $targets) {
    $path = Join-Path $referenceDir $target.Name
    if (-not (Test-Path $path)) {
        $failures += "Missing reference module: $($target.Name)"
        continue
    }

    Write-Host "Inspecting $($target.Name)"

    $exports = & $dumpbin /exports $path 2>&1
    if ($LASTEXITCODE -ne 0) {
        $failures += "dumpbin /exports failed for $($target.Name)"
        continue
    }

    foreach ($symbol in $expectedExports) {
        if ($exports -notmatch [regex]::Escape($symbol)) {
            $failures += "$($target.Name) is missing export '$symbol'"
        }
    }

    $imports = & $dumpbin /imports $path 2>&1
    if ($LASTEXITCODE -ne 0) {
        $failures += "dumpbin /imports failed for $($target.Name)"
        continue
    }

    foreach ($library in $target.Imports) {
        if ($imports -notmatch [regex]::Escape($library)) {
            $failures += "$($target.Name) is missing import '$library'"
        }
    }
}

if ($failures.Count -gt 0) {
    $failures | ForEach-Object { Write-Error $_ }
    exit 1
}

Write-Host 'All reference DLLs expose the expected imports and exports.'
