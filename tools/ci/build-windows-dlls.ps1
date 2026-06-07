[CmdletBinding()]
param(
    [string]$RepoRoot = (Resolve-Path (Join-Path $PSScriptRoot '../..')).Path,
    [string]$Solution = 'src/code/quakelive.sln',
    [string]$Configuration = 'Release',
    [string]$Platform = 'x86',
    [string]$PlatformToolset = '',
    [string]$WindowsTargetPlatformVersion = '',
    [string]$BuildLogRoot = '',
    [switch]$DisableOptionalCodecs
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

$solutionPath = if ([System.IO.Path]::IsPathRooted($Solution)) {
    $Solution
}
else {
    Join-Path $RepoRoot $Solution
}
if (-not (Test-Path $solutionPath)) {
    throw "Solution file not found at '$solutionPath'."
}
$solutionPath = (Resolve-Path $solutionPath).Path

if (-not $WindowsTargetPlatformVersion -and $PlatformToolset -in @('v141', 'v143')) {
    $WindowsTargetPlatformVersion = Get-LatestWindowsSdkVersion
    if (-not $WindowsTargetPlatformVersion) {
        throw "Unable to locate an installed Windows 10/11 SDK for the $PlatformToolset build."
    }
}

if ($DisableOptionalCodecs) {
    Write-Warning '-DisableOptionalCodecs is retained for compatibility but no longer disables OGG/PNG; the release build links repo-managed static codec libraries.'
}

if (-not $BuildLogRoot) {
    $BuildLogRoot = Join-Path $RepoRoot 'artifacts\build-logs'
}

$buildScript = Join-Path $RepoRoot '.vscode\build.ps1'
if (-not (Test-Path $buildScript)) {
    throw "VS Code build helper was not found: $buildScript"
}

$buildPlatform = $Platform
if ($buildPlatform -ieq 'Win32') {
    $buildPlatform = 'x86'
}

$buildArguments = @(
    '-NoProfile',
    '-ExecutionPolicy', 'Bypass',
    '-File', $buildScript,
    '-Solution', $solutionPath,
    '-Configuration', $Configuration,
    '-Platform', $buildPlatform,
    '-OnlineServices', '0',
    '-Steamworks', '0',
    '-OpenSteam', '0',
    '-RequireAwesomiumSdk', '0',
    '-BuildLogRoot', $BuildLogRoot
)

if ($PlatformToolset) {
    $buildArguments += @('-PlatformToolset', $PlatformToolset)
}
if ($WindowsTargetPlatformVersion) {
    $buildArguments += @('-WindowsTargetPlatformVersion', $WindowsTargetPlatformVersion)
}

$powershellHost = Get-Command pwsh.exe -ErrorAction SilentlyContinue
if (-not $powershellHost) {
    $powershellHost = Get-Command powershell.exe -ErrorAction SilentlyContinue
}
if (-not $powershellHost) {
    throw 'Neither pwsh.exe nor powershell.exe could be found to run the shared Windows build helper.'
}

$toolsetLabel = if ($PlatformToolset) { $PlatformToolset } else { 'helper default' }
Write-Host "Building '$Solution' ($Configuration|$buildPlatform) through .vscode/build.ps1 with toolset $toolsetLabel."
$process = Start-Process -FilePath $powershellHost.Source -ArgumentList $buildArguments -Wait -PassThru -NoNewWindow
if ($process.ExitCode -ne 0) {
    $logCandidates = Get-ChildItem -Path $BuildLogRoot -Filter 'msbuild-*.log' -File -ErrorAction SilentlyContinue |
        Sort-Object LastWriteTimeUtc -Descending
    $latestLog = $logCandidates | Select-Object -First 1
    if ($latestLog) {
        Write-Error "Shared Windows build helper failed with exit code $($process.ExitCode). Last 160 log lines from '$($latestLog.FullName)':"
        Get-Content -Path $latestLog.FullName -Tail 160 | ForEach-Object { Write-Error $_ }
    }

    throw "Shared Windows build helper failed with exit code $($process.ExitCode)."
}

Write-Host "Native Windows solution build completed successfully via .vscode/build.ps1."

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
