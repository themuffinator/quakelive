[CmdletBinding()]
param(
    [string]$RepoRoot = ''
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

if ([string]::IsNullOrWhiteSpace($RepoRoot)) {
    $scriptRoot = $PSScriptRoot
    if ([string]::IsNullOrWhiteSpace($scriptRoot) -and $MyInvocation.MyCommand.Path) {
        $scriptRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
    }
    if ([string]::IsNullOrWhiteSpace($scriptRoot)) {
        $scriptRoot = (Get-Location).Path
    }

    $RepoRoot = (Resolve-Path (Join-Path $scriptRoot '../..')).Path
} else {
    $RepoRoot = (Resolve-Path $RepoRoot).Path
}

$stagingRoot = Join-Path $RepoRoot 'artifacts/wow64-smoketest'
$logPath = Join-Path $stagingRoot 'wow64-smoketest.log'
$redistUrl = 'https://download.microsoft.com/download/1/6/B/16B06A42-FE73-4E4A-9E7E-27ED41E0F0A3/vcredist_x86.exe'
$redistPath = Join-Path $stagingRoot 'vcredist_x86.exe'

New-Item -ItemType Directory -Force -Path $stagingRoot | Out-Null

function Write-Log {
    param(
        [string]$Message
    )

    $timestamp = Get-Date -Format 's'
    $line = "[$timestamp] $Message"
    Write-Host $line
    Add-Content -Path $logPath -Value $line
}

function Assert-32BitHost {
    if ([Environment]::Is64BitProcess) {
        throw 'Launch the WOW64 smoke test from 32-bit PowerShell (SysWOW64) so x86 DLLs can be loaded.'
    }
}

function Ensure-Redist {
    $msvcr100 = Join-Path $env:WINDIR 'SysWOW64/msvcr100.dll'
    if (Test-Path $msvcr100) {
        Write-Log "Visual C++ 2010 runtime already present at $msvcr100"
        return
    }

    if (-not (Test-Path $redistPath)) {
        Write-Log 'Downloading Visual C++ 2010 SP1 x86 redistributable...'
        Invoke-WebRequest -Uri $redistUrl -OutFile $redistPath
    }

    Write-Log 'Installing Visual C++ 2010 SP1 x86 redistributable...'
    $process = Start-Process -FilePath $redistPath -ArgumentList '/quiet /norestart' -Wait -PassThru
    if ($process.ExitCode -ne 0) {
        throw "Redistributable installer exited with code $($process.ExitCode)."
    }

    Write-Log 'Redistributable installation completed.'
}

function Resolve-ModuleSource {
    param(
        [string]$PreferredPath,
        [string]$FallbackPath
    )

    if (Test-Path $PreferredPath) {
        return $PreferredPath
    }

    if (Test-Path $FallbackPath) {
        return $FallbackPath
    }

    throw "Missing source module. Checked: $PreferredPath and $FallbackPath"
}

function Stage-Modules {
    $sources = @(
        @{
            Name = 'qagamex86.dll'
            Source = Join-Path $RepoRoot 'assets/quakelive/baseq3/qagamex86.dll'
            FallbackSource = Join-Path $RepoRoot 'build/win32/Debug/bin/baseq3/qagamex86.dll'
            Exports = @('dllEntry', 'vmMain')
        },
        @{
            Name = 'cgamex86.dll'
            Source = Join-Path $RepoRoot 'assets/quakelive/baseq3/cgamex86.dll'
            FallbackSource = Join-Path $RepoRoot 'build/win32/Debug/bin/baseq3/cgamex86.dll'
            Exports = @('dllEntry', 'vmMain')
        },
        @{
            Name = 'uix86.dll'
            Source = Join-Path $RepoRoot 'assets/quakelive/baseq3/uix86.dll'
            FallbackSource = Join-Path $RepoRoot 'build/win32/Debug/bin/baseq3/uix86.dll'
            Exports = @('dllEntry', 'vmMain')
        }
    )

    foreach ($item in $sources) {
        $sourcePath = Resolve-ModuleSource -PreferredPath $item.Source -FallbackPath $item.FallbackSource
        $destination = Join-Path $stagingRoot $item.Name
        Copy-Item -LiteralPath $sourcePath -Destination $destination -Force
        Write-Log "Staged $($item.Name) from $sourcePath to $destination"
    }

    return $sources
}

function Add-NativeHelpers {
$code = @"
using System;
using System.Runtime.InteropServices;

public static class Wow64Native
{
[DllImport("kernel32.dll", SetLastError = true, CharSet = CharSet.Ansi)]
public static extern IntPtr LoadLibrary(string lpFileName);

[DllImport("kernel32.dll", SetLastError = true, CharSet = CharSet.Ansi)]
public static extern IntPtr GetProcAddress(IntPtr hModule, string procName);

[DllImport("kernel32.dll", SetLastError = true)]
public static extern bool FreeLibrary(IntPtr hModule);
}
"@

    Add-Type -TypeDefinition $code -Language CSharp -ErrorAction Stop | Out-Null
}

function Test-NativeModule {
    param(
        [string]$Path,
        [string[]]$Exports
    )

    Write-Log "Loading $Path"
    $handle = [Wow64Native]::LoadLibrary($Path)
    if ($handle -eq [IntPtr]::Zero) {
        $errorCode = [Runtime.InteropServices.Marshal]::GetLastWin32Error()
        throw "Failed to load $Path (Win32 error $errorCode)."
    }

    foreach ($export in $Exports) {
        $proc = [Wow64Native]::GetProcAddress($handle, $export)
        if ($proc -eq [IntPtr]::Zero) {
            throw "$Path is missing export '$export'."
        }

        Write-Log "$Path exports '$export' at address $proc"
    }

    [Wow64Native]::FreeLibrary($handle) | Out-Null
    Write-Log "Unloaded $Path successfully"
}

Assert-32BitHost
Ensure-Redist
$modules = Stage-Modules
Add-NativeHelpers

foreach ($module in $modules) {
    $path = Join-Path $stagingRoot $module.Name
    Test-NativeModule -Path $path -Exports $module.Exports
}

Write-Log 'WOW64 compatibility check completed successfully.'
