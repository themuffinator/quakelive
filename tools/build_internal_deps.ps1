[CmdletBinding()]
param(
	[string]$RepoRoot = (Resolve-Path (Join-Path $PSScriptRoot '..')).Path,
	[ValidateSet('png', 'vorbis', 'freetype')]
	[string[]]$Dependency,
	[string]$Configuration = 'Release',
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
$dependencyConfiguration = if ($Configuration -match '^Debug') { 'Debug' } else { 'Release' }

function Get-CMakePath {
	foreach ($name in @('cmake.exe', 'cmake')) {
		$command = Get-Command $name -ErrorAction SilentlyContinue | Select-Object -First 1
		if ($command) {
			return $command.Source
		}
	}

	throw 'cmake was not found on PATH. Install CMake to build the repo-managed third-party codec dependencies.'
}

function Get-GitPath {
	foreach ($name in @('git.exe', 'git')) {
		$command = Get-Command $name -ErrorAction SilentlyContinue | Select-Object -First 1
		if ($command) {
			return $command.Source
		}
	}

	throw 'git was not found on PATH. Install Git to bootstrap the repo-managed dependency source cache.'
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

function Get-SafeBuildName {
	param(
		[string]$Name
	)

	return $Name -replace '[^A-Za-z0-9_.-]', '-'
}

function Get-StaticDependencyStampPath {
	param(
		[string]$InstallRoot
	)

	return Join-Path $InstallRoot ('.static-codec-build-' + (Get-SafeBuildName -Name $dependencyConfiguration))
}

function Assert-PathUnderRoot {
	param(
		[string]$Path,
		[string]$Root,
		[string]$Description
	)

	$resolvedPath = [System.IO.Path]::GetFullPath($Path)
	$resolvedRoot = [System.IO.Path]::GetFullPath($Root)
	if (-not $resolvedRoot.EndsWith([System.IO.Path]::DirectorySeparatorChar)) {
		$resolvedRoot += [System.IO.Path]::DirectorySeparatorChar
	}

	if (-not $resolvedPath.StartsWith($resolvedRoot, [System.StringComparison]::OrdinalIgnoreCase)) {
		throw "$Description path '$resolvedPath' escapes the allowed root '$resolvedRoot'."
	}

	return $resolvedPath
}

function Reset-DependencyInstallRoot {
	param(
		[string]$InstallRoot,
		[string]$Name
	)

	$validatedInstallRoot = Assert-PathUnderRoot -Path $InstallRoot -Root $libsRoot -Description "$Name install root"
	if (Test-Path $validatedInstallRoot) {
		Remove-Item -LiteralPath $validatedInstallRoot -Recurse -Force
	}
}

function Remove-InstalledRuntimeDlls {
	param(
		[string]$InstallRoot,
		[string]$Name
	)

	$validatedInstallRoot = Assert-PathUnderRoot -Path $InstallRoot -Root $libsRoot -Description "$Name install root"
	if (-not (Test-Path $validatedInstallRoot)) {
		return
	}

	Get-ChildItem -LiteralPath $validatedInstallRoot -Recurse -File -Filter *.dll -ErrorAction SilentlyContinue |
		ForEach-Object { Remove-Item -LiteralPath $_.FullName -Force }
}

function Write-StaticDependencyStamp {
	param(
		[string]$InstallRoot,
		[string]$Name
	)

	$stampPath = Get-StaticDependencyStampPath -InstallRoot $InstallRoot
	@(
		"Dependency=$Name",
		"RequestedConfiguration=$Configuration",
		"Configuration=$dependencyConfiguration",
		"Linkage=static"
	) | Set-Content -Path $stampPath -Encoding ASCII
}

function Reset-StaleCMakeBuildDir {
	param(
		[string]$BuildDir,
		[string]$SourceDir,
		[string]$Name
	)

	$cachePath = Join-Path $BuildDir 'CMakeCache.txt'
	if (-not (Test-Path $cachePath)) {
		return
	}

	$cachedSourceLine = Get-Content -Path $cachePath -ErrorAction SilentlyContinue |
		Where-Object { $_ -like 'CMAKE_HOME_DIRECTORY:INTERNAL=*' } |
		Select-Object -First 1
	if (-not $cachedSourceLine) {
		return
	}

	$cachedSource = $cachedSourceLine.Substring('CMAKE_HOME_DIRECTORY:INTERNAL='.Length)
	$resolvedCachedSource = [System.IO.Path]::GetFullPath($cachedSource)
	$resolvedSource = [System.IO.Path]::GetFullPath($SourceDir)
	if ($resolvedCachedSource -eq $resolvedSource) {
		return
	}

	$validatedBuildDir = Assert-PathUnderRoot -Path $BuildDir -Root $buildRoot -Description "$Name CMake build"
	Write-Host "Removing stale $Name CMake build cache from $validatedBuildDir"
	Remove-Item -LiteralPath $validatedBuildDir -Recurse -Force
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

	Reset-StaleCMakeBuildDir -BuildDir $BuildDir -SourceDir $SourceDir -Name $Name
	New-Item -ItemType Directory -Force -Path $BuildDir | Out-Null
	New-Item -ItemType Directory -Force -Path $InstallDir | Out-Null

	$configureArgs = @(
		'-S', $SourceDir,
		'-B', $BuildDir,
		'-G', $generatorInfo.Generator,
		'-DCMAKE_POLICY_VERSION_MINIMUM=3.5',
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
	& $cmakePath --build $BuildDir --config $dependencyConfiguration --target INSTALL
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

function Ensure-GitDependencySource {
	param(
		[string]$Name,
		[string]$SourceDir,
		[string]$RepositoryUrl,
		[string]$Tag,
		[string[]]$RequiredPaths
	)

	if (Test-RequiredPaths -Paths $RequiredPaths) {
		return
	}

	$gitPath = Get-GitPath
	$sourceRoot = Assert-PathUnderRoot -Path $SourceDir -Root $depsRoot -Description "$Name source"

	New-Item -ItemType Directory -Force -Path $depsRoot | Out-Null

	if (Test-Path $sourceRoot) {
		$gitMetadataDir = Join-Path $sourceRoot '.git'
		if (Test-Path $gitMetadataDir) {
			Write-Host "Refreshing $Name sources from $RepositoryUrl ($Tag)"
			& $gitPath -C $sourceRoot fetch --depth 1 origin tag $Tag
			if ($LASTEXITCODE -ne 0) {
				throw "git fetch failed while refreshing $Name sources."
			}

			& $gitPath -C $sourceRoot checkout --force $Tag
			if ($LASTEXITCODE -ne 0) {
				throw "git checkout failed while refreshing $Name sources."
			}
		} else {
			$existingEntries = Get-ChildItem -LiteralPath $sourceRoot -Force -ErrorAction SilentlyContinue | Select-Object -First 1
			if ($existingEntries) {
				throw "Repo-managed source cache for $Name is incomplete under '$sourceRoot'. Remove that directory and rerun the bootstrap."
			}

			$validatedSourceRoot = Assert-PathUnderRoot -Path $sourceRoot -Root $depsRoot -Description "$Name source cache"
			Remove-Item -LiteralPath $validatedSourceRoot -Recurse -Force
		}
	}

	if (-not (Test-Path $sourceRoot)) {
		Write-Host "Cloning $Name sources from $RepositoryUrl ($Tag)"
		& $gitPath clone --depth 1 --branch $Tag $RepositoryUrl $sourceRoot
		if ($LASTEXITCODE -ne 0) {
			throw "git clone failed while retrieving $Name sources."
		}
	}

	if (-not (Test-RequiredPaths -Paths $RequiredPaths)) {
		throw "Repo-managed source cache for $Name is still incomplete after refresh: $($RequiredPaths -join ', ')"
	}
}

function Ensure-Vorbis {
	$installRoot = Join-Path $libsRoot 'vorbis'
	$staticStamp = Get-StaticDependencyStampPath -InstallRoot $installRoot
	$requiredOutputs = @(
		(Join-Path $installRoot 'include\ogg\ogg.h'),
		(Join-Path $installRoot 'include\vorbis\vorbisfile.h'),
		(Join-Path $installRoot 'lib\Win32\ogg.lib'),
		(Join-Path $installRoot 'lib\Win32\vorbis.lib'),
		(Join-Path $installRoot 'lib\Win32\vorbisfile.lib'),
		$staticStamp
	)

	if (-not $Force -and (Test-RequiredPaths -Paths $requiredOutputs)) {
		return
	}

	$lock = Enter-DependencyLock -LockPath (Join-Path $buildRoot 'vorbis.lock')
	try {
		if (-not $Force -and (Test-RequiredPaths -Paths $requiredOutputs)) {
			return
		}

		Reset-DependencyInstallRoot -InstallRoot $installRoot -Name 'Vorbis'

		$oggSourceDir = Join-Path $depsRoot 'libogg'
		$vorbisSourceDir = Join-Path $depsRoot 'libvorbis'
		Ensure-GitDependencySource -Name 'libogg' `
			-SourceDir $oggSourceDir `
			-RepositoryUrl 'https://github.com/xiph/ogg.git' `
			-Tag 'v1.3.5' `
			-RequiredPaths @(
			(Join-Path $oggSourceDir 'CMakeLists.txt'),
			(Join-Path $oggSourceDir 'include\ogg\ogg.h')
		)
		Ensure-GitDependencySource -Name 'libvorbis' `
			-SourceDir $vorbisSourceDir `
			-RepositoryUrl 'https://github.com/xiph/vorbis.git' `
			-Tag 'v1.3.7' `
			-RequiredPaths @(
			(Join-Path $vorbisSourceDir 'CMakeLists.txt'),
			(Join-Path $vorbisSourceDir 'lib\CMakeLists.txt')
		)

		Invoke-CMakeConfigureAndInstall -Name 'libogg' `
			-SourceDir $oggSourceDir `
			-BuildDir (Join-Path $buildRoot 'libogg') `
			-InstallDir $installRoot `
			-ExtraConfigureArgs @(
				'-DBUILD_SHARED_LIBS=OFF',
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
				'-DBUILD_SHARED_LIBS=OFF',
				'-DBUILD_TESTING=OFF',
				"-DOGG_ROOT=$installRoot",
				"-DOGG_LIBRARY=$(Join-Path $installRoot 'lib\Win32\ogg.lib')",
				"-DOGG_INCLUDE_DIR=$(Join-Path $installRoot 'include')",
				"-DCMAKE_PREFIX_PATH=$installRoot",
				'-DCMAKE_INSTALL_BINDIR=bin',
				'-DCMAKE_INSTALL_LIBDIR=lib/Win32',
				'-DCMAKE_INSTALL_INCLUDEDIR=include'
			)

		Remove-InstalledRuntimeDlls -InstallRoot $installRoot -Name 'Vorbis'
		Write-StaticDependencyStamp -InstallRoot $installRoot -Name 'Vorbis'
	} finally {
		if ($lock) {
			$lock.Dispose()
		}
	}
}

function Ensure-Png {
	$installRoot = Join-Path $libsRoot 'libpng'
	$staticStamp = Get-StaticDependencyStampPath -InstallRoot $installRoot
	$pngDebugPostfix = if ($dependencyConfiguration -eq 'Debug') { 'd' } else { '' }
	$pngStaticLibrary = "libpng16_static$pngDebugPostfix.lib"
	$zlibStaticLibrary = "zlibstatic$pngDebugPostfix.lib"
	$requiredOutputs = @(
		(Join-Path $installRoot 'include\png.h'),
		(Join-Path $installRoot 'include\zlib.h'),
		(Join-Path $installRoot "lib\Win32\$pngStaticLibrary"),
		(Join-Path $installRoot "lib\Win32\$zlibStaticLibrary"),
		$staticStamp
	)

	if (-not $Force -and (Test-RequiredPaths -Paths $requiredOutputs)) {
		return
	}

	$lock = Enter-DependencyLock -LockPath (Join-Path $buildRoot 'png.lock')
	try {
		if (-not $Force -and (Test-RequiredPaths -Paths $requiredOutputs)) {
			return
		}

		Reset-DependencyInstallRoot -InstallRoot $installRoot -Name 'PNG'

		$zlibSourceDir = Join-Path $depsRoot 'zlib'
		$pngSourceDir = Join-Path $depsRoot 'libpng'
		Ensure-GitDependencySource -Name 'zlib' `
			-SourceDir $zlibSourceDir `
			-RepositoryUrl 'https://github.com/madler/zlib.git' `
			-Tag 'v1.3.1' `
			-RequiredPaths @(
			(Join-Path $zlibSourceDir 'CMakeLists.txt'),
			(Join-Path $zlibSourceDir 'zlib.h')
		)
		Ensure-GitDependencySource -Name 'libpng' `
			-SourceDir $pngSourceDir `
			-RepositoryUrl 'https://github.com/glennrp/libpng.git' `
			-Tag 'v1.6.43' `
			-RequiredPaths @(
			(Join-Path $pngSourceDir 'CMakeLists.txt'),
			(Join-Path $pngSourceDir 'png.h')
		)

		Invoke-CMakeConfigureAndInstall -Name 'zlib' `
			-SourceDir $zlibSourceDir `
			-BuildDir (Join-Path $buildRoot 'zlib') `
			-InstallDir $installRoot `
			-ExtraConfigureArgs @(
				'-DBUILD_SHARED_LIBS=OFF',
				'-DZLIB_BUILD_EXAMPLES=OFF',
				"-DINSTALL_BIN_DIR=$(Join-Path $installRoot 'bin')",
				"-DINSTALL_LIB_DIR=$(Join-Path $installRoot 'lib\Win32')",
				"-DINSTALL_INC_DIR=$(Join-Path $installRoot 'include')",
				"-DINSTALL_MAN_DIR=$(Join-Path $installRoot 'share\man')",
				"-DINSTALL_PKGCONFIG_DIR=$(Join-Path $installRoot 'share\pkgconfig')"
			)

		Invoke-CMakeConfigureAndInstall -Name 'libpng' `
			-SourceDir $pngSourceDir `
			-BuildDir (Join-Path $buildRoot 'libpng') `
			-InstallDir $installRoot `
			-ExtraConfigureArgs @(
				'-DPNG_SHARED=OFF',
				'-DPNG_STATIC=ON',
				'-DPNG_TESTS=OFF',
				'-DPNG_TOOLS=OFF',
				"-DZLIB_ROOT=$installRoot",
				"-DZLIB_INCLUDE_DIR=$(Join-Path $installRoot 'include')",
				"-DZLIB_LIBRARY=$(Join-Path $installRoot "lib\Win32\$zlibStaticLibrary")",
				"-DCMAKE_PREFIX_PATH=$installRoot",
				'-DCMAKE_INSTALL_BINDIR=bin',
				'-DCMAKE_INSTALL_LIBDIR=lib/Win32',
				'-DCMAKE_INSTALL_INCLUDEDIR=include'
			)

		Remove-InstalledRuntimeDlls -InstallRoot $installRoot -Name 'PNG'
		Write-StaticDependencyStamp -InstallRoot $installRoot -Name 'PNG'
	} finally {
		if ($lock) {
			$lock.Dispose()
		}
	}
}

function Ensure-FreeType {
	$installRoot = Join-Path $libsRoot 'freetype'
	$requiredHeaders = @(
		(Join-Path $installRoot 'include\freetype2\ft2build.h'),
		(Join-Path $installRoot 'include\freetype2\freetype\config\ftheader.h')
	)
	$requiredLibraries = @(
		(Join-Path $installRoot 'lib\Win32\freetype.lib'),
		(Join-Path $installRoot 'lib\Win32\libfreetype.lib')
	)
	$existingLibrary = $requiredLibraries | Where-Object { Test-Path $_ } | Select-Object -First 1

	if (-not $Force -and (Test-RequiredPaths -Paths $requiredHeaders) -and $existingLibrary) {
		return
	}

	$lock = Enter-DependencyLock -LockPath (Join-Path $buildRoot 'freetype.lock')
	try {
		$existingLibrary = $requiredLibraries | Where-Object { Test-Path $_ } | Select-Object -First 1
		if (-not $Force -and (Test-RequiredPaths -Paths $requiredHeaders) -and $existingLibrary) {
			return
		}

		$freeTypeSourceDir = Join-Path $depsRoot 'freetype'
		Ensure-GitDependencySource -Name 'FreeType' `
			-SourceDir $freeTypeSourceDir `
			-RepositoryUrl 'https://gitlab.freedesktop.org/freetype/freetype.git' `
			-Tag 'VER-2-14-3' `
			-RequiredPaths @(
				(Join-Path $freeTypeSourceDir 'CMakeLists.txt'),
				(Join-Path $freeTypeSourceDir 'include\ft2build.h'),
				(Join-Path $freeTypeSourceDir 'include\freetype\config\ftheader.h')
			)

		Invoke-CMakeConfigureAndInstall -Name 'FreeType' `
			-SourceDir $freeTypeSourceDir `
			-BuildDir (Join-Path $buildRoot 'freetype') `
			-InstallDir $installRoot `
			-ExtraConfigureArgs @(
				'-DBUILD_SHARED_LIBS=OFF',
				'-DFT_DISABLE_ZLIB=TRUE',
				'-DFT_DISABLE_BZIP2=TRUE',
				'-DFT_DISABLE_PNG=TRUE',
				'-DFT_DISABLE_HARFBUZZ=TRUE',
				'-DFT_DISABLE_BROTLI=TRUE',
				'-DCMAKE_INSTALL_BINDIR=bin',
				'-DCMAKE_INSTALL_LIBDIR=lib/Win32',
				'-DCMAKE_INSTALL_INCLUDEDIR=include'
			)

		$existingLibrary = $requiredLibraries | Where-Object { Test-Path $_ } | Select-Object -First 1
		if (-not (Test-RequiredPaths -Paths $requiredHeaders) -or -not $existingLibrary) {
			throw 'FreeType bootstrap completed without producing the expected repo-managed headers and import library.'
		}
	} finally {
		if ($lock) {
			$lock.Dispose()
		}
	}
}

foreach ($name in $Dependency | Select-Object -Unique) {
	switch ($name) {
		'freetype' {
			Ensure-FreeType
		}
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
