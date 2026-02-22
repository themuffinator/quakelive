[CmdletBinding()]
param(
	[string]$Solution,
	[string]$Configuration = 'Debug',
	[string]$Platform = 'x86'
)

$scriptRoot = $PSScriptRoot
if (-not $scriptRoot) {
	$scriptRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
}

if (-not $Solution) {
	$Solution = Join-Path $scriptRoot '..\src\code\quakelive.sln'
}

$ErrorActionPreference = 'Stop'

$platformNormalized = $Platform
if ($platformNormalized -ieq 'Win32') {
	$platformNormalized = 'x86'
}

$msbuildPath = $null
$msbuildCmd = Get-Command msbuild.exe -ErrorAction SilentlyContinue
if ($msbuildCmd) {
	$msbuildPath = $msbuildCmd.Source
}

if (-not $msbuildPath) {
	$vswhere = $null
	$pf86 = [Environment]::GetFolderPath('ProgramFilesX86')
	if ($pf86) {
		$candidate = Join-Path $pf86 'Microsoft Visual Studio/Installer/vswhere.exe'
		if (Test-Path $candidate) {
			$vswhere = $candidate
		}
	}
	if (-not $vswhere) {
		$pf = [Environment]::GetFolderPath('ProgramFiles')
		if ($pf) {
			$candidate = Join-Path $pf 'Microsoft Visual Studio/Installer/vswhere.exe'
			if (Test-Path $candidate) {
				$vswhere = $candidate
			}
		}
	}
	if ($vswhere) {
		$msbuildPath = & $vswhere -latest -products * -find 'MSBuild\**\Bin\MSBuild.exe' 2>$null | Select-Object -First 1
	}
}

if (-not $msbuildPath) {
	$pf = [Environment]::GetFolderPath('ProgramFiles')
	if ($pf) {
		$vs18Root = Join-Path $pf 'Microsoft Visual Studio\18'
		if (Test-Path $vs18Root) {
			$msbuildPath = Get-ChildItem -Path $vs18Root -Filter MSBuild.exe -Recurse -ErrorAction SilentlyContinue |
				Where-Object { $_.FullName -match '\\MSBuild\\Current\\Bin(\\amd64)?\\MSBuild\.exe$' } |
				Select-Object -First 1 -ExpandProperty FullName
		}
	}
}

if (-not $msbuildPath) {
	throw 'msbuild.exe was not found. Install Visual Studio Build Tools or ensure MSBuild is available.'
}

$msbuildDir = Split-Path -Parent $msbuildPath
$msbuildBase = $null
$cursor = $msbuildDir
while ($cursor -and (Split-Path -Leaf $cursor) -ne 'MSBuild') {
	$cursor = Split-Path -Parent $cursor
}
if ($cursor) {
	$msbuildBase = $cursor
} else {
	$msbuildBase = Split-Path -Parent (Split-Path -Parent $msbuildPath)
}
$defaultToolset = $null

# Read the installed toolset names from MSBuild so we can override v100 projects on modern setups.
$vcPropsRoot = Join-Path $msbuildBase 'Microsoft\VC'
if (Test-Path $vcPropsRoot) {
	$vcVersionDir = Get-ChildItem -Path $vcPropsRoot -Directory | Sort-Object Name -Descending | Select-Object -First 1
	if ($vcVersionDir) {
		$toolsetRoot = Join-Path $vcVersionDir.FullName 'Platforms\Win32\PlatformToolsets'
		if (Test-Path $toolsetRoot) {
			$defaultToolset = Get-ChildItem -Path $toolsetRoot -Directory | Sort-Object Name -Descending | Select-Object -First 1 -ExpandProperty Name
		}
	}
}

$toolset = $env:QLR_PLATFORM_TOOLSET
if (-not $toolset) {
	$toolset = $defaultToolset
}

$solutionPath = Resolve-Path $Solution
$solutionDir = Split-Path -Parent $solutionPath

$vorbisSdkDir = $env:VorbisSdkDir
if (-not $vorbisSdkDir) {
	$vorbisSdkDir = Join-Path $solutionDir '..\libs\vorbis'
}

$pngSdkDir = $env:PngSdkDir
if (-not $pngSdkDir) {
	$pngSdkDir = Join-Path $solutionDir '..\libs\libpng'
}

$enableOgg = $env:QLEnableOgg
$vorbisInclude = Join-Path $vorbisSdkDir 'include\vorbis\vorbisfile.h'
$vorbisLibDir = Join-Path $vorbisSdkDir 'lib\Win32'
$oggAvailable = (Test-Path $vorbisInclude) -and
	(Test-Path (Join-Path $vorbisLibDir 'vorbisfile.lib')) -and
	(Test-Path (Join-Path $vorbisLibDir 'vorbis.lib')) -and
	(Test-Path (Join-Path $vorbisLibDir 'ogg.lib'))
if (-not $enableOgg) {
	$enableOgg = if ($oggAvailable) { 1 } else { 0 }
} else {
	$enableOgg = [int]$enableOgg
}

$enablePng = $env:QLEnablePng
$pngInclude = Join-Path $pngSdkDir 'include\png.h'
$pngLibDir = Join-Path $pngSdkDir 'lib\Win32'
$pngAvailable = (Test-Path $pngInclude) -and
	(Test-Path (Join-Path $pngLibDir 'libpng16.lib')) -and
	(Test-Path (Join-Path $pngLibDir 'zlib.lib'))
if (-not $enablePng) {
	$enablePng = if ($pngAvailable) { 1 } else { 0 }
} else {
	$enablePng = [int]$enablePng
}
if ($enablePng -eq 0 -and $pngAvailable) {
	Write-Warning "QLEnablePng was forced to 0 but libpng is available. Enabling PNG to avoid blank UI assets."
	$enablePng = 1
}

$msbuildArgs = @(
	$solutionPath,
	'/m',
	"/p:Configuration=$Configuration",
	"/p:Platform=$platformNormalized"
)
if ($toolset) {
	$msbuildArgs += "/p:PlatformToolset=$toolset"
}
if ($enableOgg -ne $null) {
	$msbuildArgs += "/p:QLEnableOgg=$enableOgg"
}
if ($enablePng -ne $null) {
	$msbuildArgs += "/p:QLEnablePng=$enablePng"
}
if ($env:VorbisSdkDir) {
	$msbuildArgs += "/p:VorbisSdkDir=$vorbisSdkDir"
}
if ($env:PngSdkDir) {
	$msbuildArgs += "/p:PngSdkDir=$pngSdkDir"
}

Write-Host "Using MSBuild: $msbuildPath"
if ($toolset) {
	Write-Host "Using PlatformToolset: $toolset"
}
Write-Host "QLEnableOgg: $enableOgg (available: $oggAvailable)"
Write-Host "QLEnablePng: $enablePng (available: $pngAvailable)"

& $msbuildPath @msbuildArgs
