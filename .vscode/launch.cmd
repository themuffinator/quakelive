@echo off
setlocal
for %%I in ("%~f0") do set "SCRIPT_DIR=%%~dpI"

set "CONFIG=%~1"
if "%CONFIG%"=="" set "CONFIG=Debug"
if not "%~1"=="" shift

set "BASEPATH="
set "ENABLE_AWESOMIUM="

:parse_opts
if /I "%~1"=="-BasePath" (
	if "%~2"=="" (
		echo launch.cmd: -BasePath requires a value.
		exit /b 1
	)
	set "BASEPATH=%~2"
	shift
	shift
	goto parse_opts
)
if /I "%~1"=="-Awesomium" (
	set "ENABLE_AWESOMIUM=1"
	shift
	goto parse_opts
)

if not "%~1"=="" (
	echo launch.cmd: additional game arguments are not supported through the batch wrapper.
	echo launch.cmd: run ".vscode\launch.ps1" directly if you need custom launch args.
	exit /b 1
)

set "AWESOMIUM_ARG="
if defined ENABLE_AWESOMIUM set "AWESOMIUM_ARG=-EnableAwesomium"

where pwsh.exe >nul 2>nul
if %ERRORLEVEL% EQU 0 (
	pwsh.exe -NoProfile -ExecutionPolicy Bypass -File "%SCRIPT_DIR%launch.ps1" -Configuration "%CONFIG%" -BasePath "%BASEPATH%" %AWESOMIUM_ARG%
	exit /b %ERRORLEVEL%
)

powershell.exe -NoProfile -ExecutionPolicy Bypass -File "%SCRIPT_DIR%launch.ps1" -Configuration "%CONFIG%" -BasePath "%BASEPATH%" %AWESOMIUM_ARG%
exit /b %ERRORLEVEL%
