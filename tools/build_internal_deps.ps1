[CmdletBinding()]
param(
	[string]$RepoRoot = (Resolve-Path (Join-Path $PSScriptRoot '..')).Path,
	[ValidateSet('png', 'vorbis')]
	[string[]]$Dependency,
	[string]$PlatformToolset = '',
	[switch]$Force
)

$ErrorActionPreference = 'Stop'

if (-not $Dependency -or $Dependency.Count -eq 0) {
	throw 'At least one dependency name must be supplied via -Dependency.'
}

$RepoRoot = (Resolve-Path $RepoRoot).Path
$libsRoot = Join-Path $RepoRoot 'src/libs'
$depsRoot = Join-Path $libsRoot '_deps'
$buildRoot = Join-Path $libsRoot '_build'

function Get-CMakePath {
	foreach ($name in @('cmake.exe', 'cmake')) {
		$command = Get-Command $name -ErrorAction SilentlyContinue | Select-Object -First 1
		if ($command) {
			return $command.Source
		}
	}

	throw 'cmake was not found on PATH. Install CMake to build the repo-managed third-party codec dependencies.'
}

function Get-VswherePath {
	$roots = @(
		[Environment]::GetFolderPath('ProgramFilesX86'),
		[Environment]::GetFolderPath('ProgramFiles')
	) | Where-Object { $_ }

	foreach ($root in $roots) {
		$candidate = Join-Path $root 'Microsoft Visual Studio\Installer\vswhere.exe'
		if (Test-Path $candidate) {
			return $candidate
		}
	}

	return $null
}

function Get-VisualStudioGeneratorInfo {
	$majorVersion = $null
	$vswhere = Get-VswherePath

	if ($vswhere) {
		$vsInstall = & $vswhere -latest -products * -format json | ConvertFrom-Json
		if ($vsInstall) {
			$installationVersion = if ($vsInstall -is [System.Array]) {
				$vsInstall[0].installationVersion
			} else {
				$vsInstall.installationVersion
			}

			if ($installationVersion) {
				$majorVersion = [int]($installationVersion.Split('.')[0])
			}
		}
	}

	if (-not $majorVersion -and $env:VisualStudioVersion) {
		$majorVersion = [int]($env:VisualStudioVersion.Split('.')[0])
	}

	switch ($majorVersion) {
		17 { return [pscustomobject]@{ Generator = 'Visual Studio 17 2022'; NeedsArchitecture = $true } }
		16 { return [pscustomobject]@{ Generator = 'Visual Studio 16 2019'; NeedsArchitecture = $true } }
		15 { return [pscustomobject]@{ Generator = 'Visual Studio 15 2017'; NeedsArchitecture = $true } }
		14 { return [pscustomobject]@{ Generator = 'Visual Studio 14 2015'; NeedsArchitecture = $false } }
		12 { return [pscustomobject]@{ Generator = 'Visual Studio 12 2013'; NeedsArchitecture = $false } }
		11 { return [pscustomobject]@{ Generator = 'Visual Studio 11 2012'; NeedsArchitecture = $false } }
		10 { return [pscustomobject]@{ Generator = 'Visual Studio 10 2010'; NeedsArchitecture = $false } }
		default {
			throw 'Unable to determine a supported Visual Studio generator for CMake. Set up a Visual Studio build environment before bootstrapping internal dependencies.'
		}
	}
}

function Enter-DependencyLock {
	param(
		[string]$LockPath
	)

	$lockDir = Split-Path -Parent $LockPath
	if ($lockDir) {
		New-Item -ItemType Directory -Force -Path $lockDir | Out-Null
	}

	for ($attempt = 0; $attempt -lt 120; $attempt++) {
		try {
			return [System.IO.File]::Open($LockPath, [System.IO.FileMode]::OpenOrCreate, [System.IO.FileAccess]::ReadWrite, [System.IO.FileShare]::None)
		} catch [System.IO.IOException] {
			Start-Sleep -Milliseconds 500
		}
	}

	throw "Timed out waiting for dependency lock '$LockPath'."
}

function Test-RequiredPaths {
	param(
		[string[]]$Paths
	)

	foreach ($path in $Paths) {
		if (-not (Test-Path $path)) {
			return $false
		}
	}

	return $true
}

function Invoke-CMakeConfigureAndInstall {
	param(
		[string]$Name,
		[string]$SourceDir,
		[string]$BuildDir,
		[string]$InstallDir,
		[string[]]$ExtraConfigureArgs
	)

	$cmakePath = Get-CMakePath
	$generatorInfo = Get-VisualStudioGeneratorInfo

	New-Item -ItemType Directory -Force -Path $BuildDir | Out-Null
	New-Item -ItemType Directory -Force -Path $InstallDir | Out-Null

	$configureArgs = @(
		'-S', $SourceDir,
		'-B', $BuildDir,
		'-G', $generatorInfo.Generator,
		"-DCMAKE_INSTALL_PREFIX=$InstallDir"
	)

	if ($generatorInfo.NeedsArchitecture) {
		$configureArgs += @('-A', 'Win32')
	}

	if ($PlatformToolset -and -not ($generatorInfo.Generator -eq 'Visual Studio 10 2010' -and $PlatformToolset -eq 'v100')) {
		$configureArgs += @('-T', $PlatformToolset)
	}

	if ($ExtraConfigureArgs) {
		$configureArgs += $ExtraConfigureArgs
	}

	Write-Host "Configuring $Name with CMake generator '$($generatorInfo.Generator)'"
	& $cmakePath @configureArgs
	if ($LASTEXITCODE -ne 0) {
		throw "CMake configure failed for $Name."
	}

	Write-Host "Building and installing $Name"
	& $cmakePath --build $BuildDir --config Release --target INSTALL
	if ($LASTEXITCODE -ne 0) {
		throw "CMake build/install failed for $Name."
	}
}

function Ensure-DependencySources {
	param(
		[string]$Name,
		[string[]]$RequiredPaths
	)

	foreach ($path in $RequiredPaths) {
		if (-not (Test-Path $path)) {
			throw "Repo-managed source for $Name is missing: $path. Populate src/libs/_deps before building."
		}
	}
}

function Ensure-Vorbis {
	$installRoot = Join-Path $libsRoot 'vorbis'
	$requiredOutputs = @(
		(Join-Path $installRoot 'include\ogg\ogg.h'),
		(Join-Path $installRoot 'include\vorbis\vorbisfile.h'),
		(Join-Path $installRoot 'lib\Win32\ogg.lib'),
		(Join-Path $installRoot 'lib\Win32\vorbis.lib'),
		(Join-Path $installRoot 'lib\Win32\vorbisfile.lib')
	)

	if (-not $Force -and (Test-RequiredPaths -Paths $requiredOutputs)) {
		return
	}

	$lock = Enter-DependencyLock -LockPath (Join-Path $buildRoot 'vorbis.lock')
	try {
		if (-not $Force -and (Test-RequiredPaths -Paths $requiredOutputs)) {
			return
		}

		$oggSourceDir = Join-Path $depsRoot 'libogg'
		$vorbisSourceDir = Join-Path $depsRoot 'libvorbis'
		Ensure-DependencySources -Name 'libogg' -RequiredPaths @(
			(Join-Path $oggSourceDir 'CMakeLists.txt'),
			(Join-Path $oggSourceDir 'include\ogg\ogg.h')
		)
		Ensure-DependencySources -Name 'libvorbis' -RequiredPaths @(
			(Join-Path $vorbisSourceDir 'CMakeLists.txt'),
			(Join-Path $vorbisSourceDir 'lib\CMakeLists.txt')
		)

		Invoke-CMakeConfigureAndInstall -Name 'libogg' `
			-SourceDir $oggSourceDir `
			-BuildDir (Join-Path $buildRoot 'libogg') `
			-InstallDir $installRoot `
			-ExtraConfigureArgs @(
				'-DBUILD_SHARED_LIBS=ON',
				'-DINSTALL_DOCS=OFF',
				'-DINSTALL_PKG_CONFIG_MODULE=ON',
				'-DINSTALL_CMAKE_PACKAGE_MODULE=ON',
				'-DCMAKE_INSTALL_BINDIR=bin',
				'-DCMAKE_INSTALL_LIBDIR=lib/Win32',
				'-DCMAKE_INSTALL_INCLUDEDIR=include'
			)

		Invoke-CMakeConfigureAndInstall -Name 'libvorbis' `
			-SourceDir $vorbisSourceDir `
			-BuildDir (Join-Path $buildRoot 'libvorbis') `
			-InstallDir $installRoot `
			-ExtraConfigureArgs @(
				'-DBUILD_SHARED_LIBS=ON',
				'-DBUILD_TESTING=OFF',
				'-DOgg_ROOT=' + $installRoot,
				'-DCMAKE_PREFIX_PATH=' + $installRoot,
				'-DCMAKE_INSTALL_BINDIR=bin',
				'-DCMAKE_INSTALL_LIBDIR=lib/Win32',
				'-DCMAKE_INSTALL_INCLUDEDIR=include'
			)
	} finally {
		if ($lock) {
			$lock.Dispose()
		}
	}
}

function Ensure-Png {
	$installRoot = Join-Path $libsRoot 'libpng'
	$requiredOutputs = @(
		(Join-Path $installRoot 'include\png.h'),
		(Join-Path $installRoot 'include\zlib.h'),
		(Join-Path $installRoot 'lib\Win32\libpng16.lib'),
		(Join-Path $installRoot 'lib\Win32\zlib.lib')
	)

	if (-not $Force -and (Test-RequiredPaths -Paths $requiredOutputs)) {
		return
	}

	$lock = Enter-DependencyLock -LockPath (Join-Path $buildRoot 'png.lock')
	try {
		if (-not $Force -and (Test-RequiredPaths -Paths $requiredOutputs)) {
			return
		}

		$zlibSourceDir = Join-Path $depsRoot 'zlib'
		$pngSourceDir = Join-Path $depsRoot 'libpng'
		Ensure-DependencySources -Name 'zlib' -RequiredPaths @(
			(Join-Path $zlibSourceDir 'CMakeLists.txt'),
			(Join-Path $zlibSourceDir 'zlib.h')
		)
		Ensure-DependencySources -Name 'libpng' -RequiredPaths @(
			(Join-Path $pngSourceDir 'CMakeLists.txt'),
			(Join-Path $pngSourceDir 'png.h')
		)

		Invoke-CMakeConfigureAndInstall -Name 'zlib' `
			-SourceDir $zlibSourceDir `
			-BuildDir (Join-Path $buildRoot 'zlib') `
			-InstallDir $installRoot `
			-ExtraConfigureArgs @(
				'-DZLIB_BUILD_EXAMPLES=OFF',
				'-DINSTALL_BIN_DIR=' + (Join-Path $installRoot 'bin'),
				'-DINSTALL_LIB_DIR=' + (Join-Path $installRoot 'lib\Win32'),
				'-DINSTALL_INC_DIR=' + (Join-Path $installRoot 'include'),
				'-DINSTALL_MAN_DIR=' + (Join-Path $installRoot 'share\man'),
				'-DINSTALL_PKGCONFIG_DIR=' + (Join-Path $installRoot 'share\pkgconfig')
			)

		Invoke-CMakeConfigureAndInstall -Name 'libpng' `
			-SourceDir $pngSourceDir `
			-BuildDir (Join-Path $buildRoot 'libpng') `
			-InstallDir $installRoot `
			-ExtraConfigureArgs @(
				'-DPNG_SHARED=ON',
				'-DPNG_STATIC=OFF',
				'-DPNG_TESTS=OFF',
				'-DPNG_TOOLS=OFF',
				'-DZLIB_ROOT=' + $installRoot,
				'-DZLIB_INCLUDE_DIR=' + (Join-Path $installRoot 'include'),
				'-DZLIB_LIBRARY=' + (Join-Path $installRoot 'lib\Win32\zlib.lib'),
				'-DCMAKE_PREFIX_PATH=' + $installRoot,
				'-DCMAKE_INSTALL_BINDIR=bin',
				'-DCMAKE_INSTALL_LIBDIR=lib/Win32',
				'-DCMAKE_INSTALL_INCLUDEDIR=include'
			)
	} finally {
		if ($lock) {
			$lock.Dispose()
		}
	}
}

foreach ($name in $Dependency | Select-Object -Unique) {
	switch ($name) {
		'png' {
			Ensure-Png
		}
		'vorbis' {
			Ensure-Vorbis
		}
		default {
			throw "Unsupported dependency '$name'."
		}
	}
}
