[CmdletBinding()]
param(
    [string]$ComponentId = 'Microsoft.VisualStudio.Component.VC.v100.x86.x64'
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

$vsWhere = Get-VsWherePath
if (-not $vsWhere) {
    throw 'Unable to locate vswhere.exe. Visual Studio installation state cannot be queried.'
}

# Bail out early if the requested component is already present.
$componentProbe = & $vsWhere -products * -requires $ComponentId -format json 2>$null
if ($LASTEXITCODE -eq 0 -and $componentProbe) {
    $installs = $componentProbe | ConvertFrom-Json
    if ($installs -and $installs.Count -gt 0) {
        Write-Host "Visual Studio component '$ComponentId' already installed."
        return
    }
}

$installInfoJson = & $vsWhere -latest -format json 2>$null
if ($LASTEXITCODE -ne 0 -or -not $installInfoJson) {
    throw 'vswhere.exe could not enumerate Visual Studio installations.'
}

$installInfo = $installInfoJson | ConvertFrom-Json
if (-not $installInfo -or $installInfo.Count -eq 0) {
    throw 'No Visual Studio installations were detected on the runner.'
}

$installationPath = $installInfo[0].installationPath
if (-not $installationPath) {
    throw 'Visual Studio installation path was not reported by vswhere.exe.'
}

$installerRoot = Split-Path $vsWhere -Parent
$vsInstaller = Join-Path $installerRoot 'vs_installer.exe'
if (-not (Test-Path $vsInstaller)) {
    throw 'vs_installer.exe was not found next to vswhere.exe. Cannot install Visual Studio components.'
}

Write-Host "Installing Visual Studio component '$ComponentId' into '$installationPath'."
$arguments = @(
    'modify',
    '--quiet',
    '--norestart',
    '--nocache',
    '--installPath', $installationPath,
    '--add', $ComponentId
)

$process = Start-Process -FilePath $vsInstaller -ArgumentList $arguments -Wait -PassThru
if ($process.ExitCode -ne 0) {
    throw "vs_installer.exe failed with exit code $($process.ExitCode) while adding component '$ComponentId'."
}

Write-Host 'Visual Studio component installation completed successfully.'
