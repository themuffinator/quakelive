[CmdletBinding()]
param(
    [string]$RepoRoot = (Resolve-Path (Join-Path $PSScriptRoot '../..')).Path,
    [string]$ManifestPath = (Join-Path $PSScriptRoot 'manifests/native-dll-exports.json')
)

$ErrorActionPreference = 'Stop'

if (-not (Test-Path $ManifestPath)) {
    throw "Export manifest not found at '$ManifestPath'."
}

$manifestJson = Get-Content -Path $ManifestPath -Raw
if (-not $manifestJson) {
    throw 'Export manifest is empty.'
}

$manifest = $manifestJson | ConvertFrom-Json
if (-not $manifest -or -not $manifest.modules) {
    throw 'Export manifest does not define any modules.'
}

function Get-ExportTool {
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

    $dumpbin = Get-Command dumpbin.exe -ErrorAction SilentlyContinue
    if ($dumpbin) {
        return [pscustomobject]@{ Name = 'dumpbin'; Path = $dumpbin.Source; Mode = 'Dumpbin' }
    }

    $vsWhere = Get-VsWherePath
    if ($vsWhere) {
        $json = & $vsWhere -products * -requires Microsoft.VisualStudio.Component.VC.Tools.x86.x64 -format json 2>$null
        if ($LASTEXITCODE -eq 0 -and $json) {
            $data = $json | ConvertFrom-Json
            foreach ($install in $data) {
                $searchRoot = Join-Path $install.installationPath 'VC/Tools/MSVC'
                if (-not (Test-Path $searchRoot)) {
                    continue
                }

                $versions = Get-ChildItem -Path $searchRoot -Directory | Sort-Object Name -Descending
                foreach ($version in $versions) {
                    $candidates = @(
                        (Join-Path $version.FullName 'bin/HostX86/x86/dumpbin.exe'),
                        (Join-Path $version.FullName 'bin/HostX64/x86/dumpbin.exe'),
                        (Join-Path $version.FullName 'bin/HostX64/x64/dumpbin.exe')
                    )

                    foreach ($candidate in $candidates) {
                        if (Test-Path $candidate) {
                            return [pscustomobject]@{ Name = 'dumpbin'; Path = $candidate; Mode = 'Dumpbin' }
                        }
                    }
                }
            }
        }
    }

    $legacyDumpbin = 'C:\Program Files (x86)\Microsoft Visual Studio 10.0\VC\bin\dumpbin.exe'
    if (Test-Path $legacyDumpbin) {
        return [pscustomobject]@{ Name = 'dumpbin'; Path = $legacyDumpbin; Mode = 'Dumpbin' }
    }

    $objdump = Get-Command objdump.exe -ErrorAction SilentlyContinue
    if ($objdump) {
        return [pscustomobject]@{ Name = 'objdump'; Path = $objdump.Source; Mode = 'Objdump' }
    }

    throw 'Neither dumpbin.exe nor objdump.exe could be located. Install Visual Studio or binutils to inspect exports.'
}

function Read-DumpbinExports {
    param(
        [string]$ToolPath,
        [string]$BinaryPath
    )

    $output = & $ToolPath /nologo /exports $BinaryPath 2>&1
    if ($LASTEXITCODE -ne 0) {
        throw "dumpbin.exe failed while inspecting '$BinaryPath'."
    }

    $exports = @()
    foreach ($line in $output) {
        if ($line -match '^[ \t]*[0-9]+[ \t]+[0-9A-Fa-f]+[ \t]+[0-9A-Fa-f]+[ \t]+(?<Name>\S+?)(?:[ \t]*=[ \t]*\S+)?$') {
            $exports += $Matches['Name']
        }
    }

    return $exports
}

function Read-ObjdumpExports {
    param(
        [string]$ToolPath,
        [string]$BinaryPath
    )

    $output = & $ToolPath -p $BinaryPath 2>&1
    if ($LASTEXITCODE -ne 0) {
        throw "objdump.exe failed while inspecting '$BinaryPath'."
    }

    $exports = @()
    $capture = $false
    foreach ($line in $output) {
        if ($line -match '^Export Table:') {
            $capture = $true
            continue
        }

        if (-not $capture) {
            continue
        }

        if ($line -match '^[ \t]*$') {
            continue
        }

        if ($line -match '^[ \t]*\[?[0-9]+\]?[^A-Za-z0-9_@?\"]*(?<Name>[A-Za-z0-9_@?$]+)') {
            $exports += $Matches['Name']
        }
    }

    return $exports
}

function Get-BuiltBinaryPath {
    param(
        [string]$ModuleName,
        [string[]]$SearchRoots
    )

    $searchNames = @($ModuleName)
    $extension = [System.IO.Path]::GetExtension($ModuleName)
    $baseName = [System.IO.Path]::GetFileNameWithoutExtension($ModuleName)
    if ($baseName -and $extension) {
        $searchNames += "${baseName}_new${extension}"
    }

    foreach ($root in $SearchRoots) {
        if (-not (Test-Path $root)) {
            continue
        }

        $candidates = @()
        foreach ($searchName in ($searchNames | Select-Object -Unique)) {
            $candidates += Get-ChildItem -Path $root -Filter $searchName -File -Recurse -ErrorAction SilentlyContinue
        }
        if (-not $candidates) {
            continue
        }

        $releaseCandidates = $candidates | Where-Object { $_.FullName -match '[\\/](Release|Release TA|Release TA DEMO|Release Alpha)[\\/]' }
        if ($releaseCandidates) {
            return $releaseCandidates[0].FullName
        }

        return $candidates[0].FullName
    }

    return $null
}

function Get-RelativePathSafe {
    param(
        [string]$BasePath,
        [string]$TargetPath
    )

    try {
        return [System.IO.Path]::GetRelativePath($BasePath, $TargetPath)
    }
    catch {
        return $TargetPath
    }
}

$tool = Get-ExportTool
$searchRoots = @(
    (Join-Path $RepoRoot 'build'),
    (Join-Path $RepoRoot 'src/code')
)

$failures = @()
foreach ($module in $manifest.modules) {
    $moduleName = $module.name
    if (-not $moduleName) {
        $failures += 'Manifest entry is missing a module name.'
        continue
    }

    $expectedExports = @($module.exports)
    if ($expectedExports.Count -eq 0) {
        $failures += "Manifest entry for '$moduleName' does not declare any exports."
        continue
    }

    $binaryPath = Get-BuiltBinaryPath -ModuleName $moduleName -SearchRoots $searchRoots
    if (-not $binaryPath) {
        $failures += "Unable to locate a built artifact for '$moduleName'."
        continue
    }

    try {
        switch ($tool.Mode) {
            'Dumpbin' { $exports = Read-DumpbinExports -ToolPath $tool.Path -BinaryPath $binaryPath }
            'Objdump' { $exports = Read-ObjdumpExports -ToolPath $tool.Path -BinaryPath $binaryPath }
        }
    }
    catch {
        $failures += $_.Exception.Message
        continue
    }

    $missing = $expectedExports | Where-Object { $_ -notin $exports }
    $unexpected = $exports | Where-Object { $_ -notin $expectedExports }

    if ($missing.Count -gt 0 -or $unexpected.Count -gt 0) {
        $failureMessage = "Export mismatch for '$moduleName'"
        if ($missing.Count -gt 0) {
            $failureMessage += ": missing exports: $($missing -join ', ')"
        }
        if ($unexpected.Count -gt 0) {
            if ($missing.Count -gt 0) { $failureMessage += '; ' }
            $failureMessage += "unexpected exports: $($unexpected -join ', ')"
        }
        $failures += $failureMessage
    }
    else {
        $relativePath = Get-RelativePathSafe -BasePath $RepoRoot -TargetPath $binaryPath
        Write-Host "Validated exports for $moduleName at $relativePath"
    }
}

if ($failures.Count -gt 0) {
    $failures | ForEach-Object { Write-Error $_ }
    exit 1
}

Write-Host 'All gameplay DLL exports match the manifest.'
