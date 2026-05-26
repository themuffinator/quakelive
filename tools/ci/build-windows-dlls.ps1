[CmdletBinding()]
param(
    [string]$RepoRoot = (Resolve-Path (Join-Path $PSScriptRoot '../..')).Path,
    [string]$Solution = 'src/code/quakelive.sln',
    [string]$Configuration = 'Release',
    [string]$Platform = 'Win32',
    [string]$PlatformToolset = 'v143',
    [string]$WindowsTargetPlatformVersion = ''
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

function Get-MSBuildPath {
    $command = Get-Command msbuild.exe -ErrorAction SilentlyContinue
    if ($command) {
        return $command.Source
    }

    $vsWhere = Get-VsWherePath
    if ($vsWhere) {
        $json = & $vsWhere -products * -requires Microsoft.Component.MSBuild -format json 2>$null
        if ($LASTEXITCODE -eq 0 -and $json) {
            $data = $json | ConvertFrom-Json
            foreach ($install in $data) {
                $candidates = @(
                    (Join-Path $install.installationPath 'MSBuild\Current\Bin\MSBuild.exe'),
                    (Join-Path $install.installationPath 'MSBuild\15.0\Bin\MSBuild.exe')
                )

                foreach ($candidate in $candidates) {
                    if (Test-Path $candidate) {
                        return $candidate
                    }
                }
            }
        }
    }

    return $null
}

function Get-CLPath {
    $command = Get-Command cl.exe -ErrorAction SilentlyContinue
    if ($command) {
        return $command.Source
    }

    $vsWhere = Get-VsWherePath
    if ($vsWhere) {
        $json = & $vsWhere -products * -requires Microsoft.VisualStudio.Component.VC.Tools.x86.x64 -format json 2>$null
        if ($LASTEXITCODE -eq 0 -and $json) {
            $data = $json | ConvertFrom-Json
            foreach ($install in $data) {
                $search = Join-Path $install.installationPath 'VC/Tools/MSVC'
                if (-not (Test-Path $search)) {
                    continue
                }

                $versions = Get-ChildItem -Path $search -Directory | Sort-Object Name -Descending
                foreach ($version in $versions) {
                    $candidates = @(
                        (Join-Path $version.FullName 'bin/Hostx64/x86/cl.exe'),
                        (Join-Path $version.FullName 'bin/Hostx86/x86/cl.exe')
                    )

                    foreach ($candidate in $candidates) {
                        if (Test-Path $candidate) {
                            return $candidate
                        }
                    }
                }
            }
        }
    }

    $legacyPath = 'C:\Program Files (x86)\Microsoft Visual Studio 10.0\VC\bin\cl.exe'
    if (Test-Path $legacyPath) {
        return $legacyPath
    }

    return $null
}

function Get-DeveloperCommand {
    param(
        [string]$RequestedToolset
    )

    if ($RequestedToolset -eq 'v100') {
        $legacyCandidates = @(
            @{ Path = 'C:\Program Files (x86)\Microsoft Visual Studio 10.0\VC\vcvarsall.bat'; Arguments = 'x86' },
            @{ Path = 'C:\Program Files (x86)\Microsoft Visual Studio 10.0\VC\bin\vcvars32.bat'; Arguments = '' }
        )

        foreach ($candidate in $legacyCandidates) {
            if (Test-Path $candidate.Path) {
                return [pscustomobject]$candidate
            }
        }
    }

    $vsWhere = Get-VsWherePath
    if (-not $vsWhere) {
        return $null
    }

    $requiredComponent = switch ($RequestedToolset) {
        'v141' { 'Microsoft.VisualStudio.Component.VC.v141.x86.x64' }
        'v143' { 'Microsoft.VisualStudio.Component.VC.Tools.x86.x64' }
        default { 'Microsoft.VisualStudio.Component.VC.Tools.x86.x64' }
    }

    $json = & $vsWhere -products * -requires $requiredComponent -format json 2>$null
    if ($LASTEXITCODE -ne 0 -or -not $json) {
        return $null
    }

    $data = $json | ConvertFrom-Json
    foreach ($install in $data) {
        $candidate = Join-Path $install.installationPath 'Common7\Tools\VsDevCmd.bat'
        if (Test-Path $candidate) {
            return [pscustomobject]@{
                Path = $candidate
                Arguments = '-arch=x86 -host_arch=x86'
            }
        }
    }

    return $null
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
            if (Test-Path (Join-Path $version.FullName 'um')) {
                return $version.Name
            }
        }
    }

    return $null
}

$solutionPath = Join-Path $RepoRoot $Solution
if (-not (Test-Path $solutionPath)) {
    throw "Solution file not found at '$solutionPath'."
}

$msbuildPlatform = $Platform
if ([System.IO.Path]::GetExtension($solutionPath) -ieq '.sln' -and $Platform -eq 'Win32') {
    $msbuildPlatform = 'x86'
}

$msbuild = Get-MSBuildPath
if (-not $msbuild) {
    throw 'msbuild.exe was not found. Install Visual Studio Build Tools or ensure MSBuild is available.'
}

if (-not $WindowsTargetPlatformVersion -and $PlatformToolset -in @('v141', 'v143')) {
    $WindowsTargetPlatformVersion = Get-LatestWindowsSdkVersion
    if (-not $WindowsTargetPlatformVersion) {
        throw "Unable to locate an installed Windows 10/11 SDK for the $PlatformToolset build."
    }
}

Write-Host "Building '$Solution' ($Configuration|$msbuildPlatform) with toolset $PlatformToolset."
$arguments = @(
    $solutionPath,
    '/m',
    "/p:Configuration=$Configuration",
    "/p:Platform=$msbuildPlatform",
    "/p:PlatformToolset=$PlatformToolset",
    '/p:PreferredToolArchitecture=x86'
)

if ($WindowsTargetPlatformVersion) {
    $arguments += "/p:WindowsTargetPlatformVersion=$WindowsTargetPlatformVersion"
}

$process = Start-Process -FilePath $msbuild -ArgumentList $arguments -Wait -PassThru
if ($process.ExitCode -ne 0) {
    throw "msbuild.exe failed with exit code $($process.ExitCode)."
}

Write-Host 'Native Windows solution build completed successfully.'

$cl = Get-CLPath
if (-not $cl) {
    throw 'cl.exe was not found. Install Visual Studio C++ build tools or initialise a developer toolchain.'
}

$developerCommand = Get-DeveloperCommand -RequestedToolset $PlatformToolset
if (-not $developerCommand -and [string]::IsNullOrWhiteSpace($env:INCLUDE)) {
    throw "Unable to initialise the MSVC developer environment for toolset '$PlatformToolset'. Open a Visual Studio Developer Prompt or install a matching toolset."
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
    if ($developerCommand) {
        $commandLine = "call `"$($developerCommand.Path)`""
        if ($developerCommand.Arguments) {
            $commandLine += " $($developerCommand.Arguments)"
        }
        $commandLine += " >nul && `"$cl`" $($arguments -join ' ')"
        $process = Start-Process -FilePath 'cmd.exe' -ArgumentList @('/d', '/c', $commandLine) -Wait -PassThru -NoNewWindow
    }
    else {
        $process = Start-Process -FilePath $cl -ArgumentList $arguments -Wait -PassThru -NoNewWindow
    }

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

Invoke-RePrototypeBuild `
    -Name 'qlr_client_frame' `
    -Sources @(
        (Join-Path $cleanRoot 'c_client\cl_frame.c'),
        (Join-Path $cleanRoot 'common\native_shim.c')
    ) `
    -IncludeDirs @(
        (Join-Path $cleanRoot 'c_client'),
        (Join-Path $cleanRoot 'common')
    ) `
    -Exports (@('CL_Frame', 'QLR_ClientFrame_BindContext', 'QLR_ClientFrame_UnbindContext') + $shimExports)

Invoke-RePrototypeBuild `
    -Name 'qlr_game_frame' `
    -Sources @(
        (Join-Path $cleanRoot 'g_gameplay\g_frame.c'),
        (Join-Path $cleanRoot 'common\native_shim.c')
    ) `
    -IncludeDirs @(
        (Join-Path $cleanRoot 'g_gameplay'),
        (Join-Path $cleanRoot 'common')
    ) `
    -Exports (@('G_RunFrame', 'QLR_Game_BindFrameContext', 'QLR_Game_UnbindFrameContext') + $shimExports)

Write-Host "Clean-room DLLs stored under $buildRoot"
