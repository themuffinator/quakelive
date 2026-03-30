param(
	[string]$GhidraHome = "C:\Users\djdac\Tools\ghidra_12.0.4_PUBLIC",
	[string]$QuakeLiveRoot = ".\assets\quakelive",
	[string]$OutputRoot = ".\references\reverse-engineering\ghidra\uix86\source-recreation",
	[string]$ReferencePath = ".\references\reverse-engineering\ghidra\uix86\ui_ghidra_reference.h"
)

$ErrorActionPreference = "Stop"

$repoRoot = (Resolve-Path (Join-Path $PSScriptRoot "..\..")).Path
$pyghidraDist = Join-Path $GhidraHome "Ghidra\Features\PyGhidra\pypkg\dist"
if (-not (Test-Path $pyghidraDist)) {
	throw "Ghidra PyGhidra distribution directory not found: $pyghidraDist"
}

if ([System.IO.Path]::IsPathRooted($QuakeLiveRoot)) {
	$quakeliveRootAbs = $QuakeLiveRoot
}
else {
	$quakeliveRootAbs = Join-Path $repoRoot $QuakeLiveRoot
}

$uiBinary = Join-Path $quakeliveRootAbs "baseq3\uix86.dll"
if (-not (Test-Path $uiBinary)) {
	throw "Required binary not found: $uiBinary"
}

if ([System.IO.Path]::IsPathRooted($OutputRoot)) {
	$outputAbs = $OutputRoot
}
else {
	$outputAbs = Join-Path $repoRoot $OutputRoot
}

if ([System.IO.Path]::IsPathRooted($ReferencePath)) {
	$referenceAbs = $ReferencePath
}
else {
	$referenceAbs = Join-Path $repoRoot $ReferencePath
}

$buildRoot = Join-Path $repoRoot "build\re"
$projectRoot = Join-Path $buildRoot "ghidra-ui-source-recreation-project"
$scriptPath = Join-Path $repoRoot "ghidra_scripts"
$symbolMap = Join-Path $repoRoot "references\symbol-maps\ui.json"
$buildReference = Join-Path $repoRoot "scripts\ghidra\build_ui_ghidra_reference.py"
$pyghidraVenv = Join-Path $buildRoot "pyghidra-venv"
$venvPython = Join-Path $pyghidraVenv "Scripts\python.exe"

New-Item -ItemType Directory -Force -Path $buildRoot | Out-Null
New-Item -ItemType Directory -Force -Path $outputAbs | Out-Null
New-Item -ItemType Directory -Force -Path $projectRoot | Out-Null

if (-not (Test-Path $venvPython)) {
	py -3.11 -m venv $pyghidraVenv
	if ($LASTEXITCODE -ne 0) {
		throw "Failed to create PyGhidra virtual environment"
	}

	& $venvPython -m pip install --no-index -f $pyghidraDist pyghidra
	if ($LASTEXITCODE -ne 0) {
		throw "Failed to install PyGhidra into $pyghidraVenv"
	}
}

python $buildReference --repo-root $repoRoot
if ($LASTEXITCODE -ne 0) {
	throw "Failed to build UI Ghidra reference header"
}

& $venvPython -m pyghidra.ghidra_launch --install-dir $GhidraHome ghidra.app.util.headless.AnalyzeHeadless `
	$projectRoot `
	"QuakeLiveUIRecreation" `
	-import $uiBinary `
	-overwrite `
	-scriptPath $scriptPath `
	-postScript "ApplyUISymbolMap.py" $symbolMap

if ($LASTEXITCODE -ne 0) {
	throw "ApplyUISymbolMap.py failed"
}

& $venvPython -m pyghidra.ghidra_launch --install-dir $GhidraHome ghidra.app.util.headless.AnalyzeHeadless `
	$projectRoot `
	"QuakeLiveUIRecreation" `
	-process "uix86.dll" `
	-scriptPath $scriptPath `
	-postScript "ExportUISourceRecreation.py" $outputAbs $referenceAbs `
	-deleteProject

if ($LASTEXITCODE -ne 0) {
	throw "ExportUISourceRecreation.py failed"
}
