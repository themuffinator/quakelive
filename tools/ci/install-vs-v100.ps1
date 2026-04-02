[CmdletBinding()]
param()

$ErrorActionPreference = 'Stop'

& (Join-Path $PSScriptRoot 'install-vs-toolset.ps1') -PlatformToolset v100
