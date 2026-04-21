# Windows 7 WOW64 compatibility test plan

This plan exercises the 32-bit Quake Live gameplay and client modules on Windows 7 x64 (WOW64) to confirm they load cleanly with the legacy Visual C++ 2010 runtime.

## Objectives
- Validate `qagamex86.dll` and `cgamex86.dll` load under WOW64 with the Visual C++ 2010 CRT present.
- Verify the launcher-side DLLs (UI/gameplay pair) stage correctly alongside the modules.
- Capture whether required exports (`dllEntry`, `vmMain`) resolve successfully.

## Environment
- Windows 7 x64 with WOW64 enabled.
- 32-bit PowerShell host (`%SystemRoot%\SysWOW64\WindowsPowerShell\v1.0\powershell.exe`).
- Outbound network access to download the Visual C++ 2010 SP1 (x86) redistributable if it is not pre-staged.

## Assets and locations
- Preferred source binaries: `assets\quakelive\baseq3\qagamex86.dll`, `assets\quakelive\baseq3\cgamex86.dll`, and `assets\quakelive\baseq3\uix86.dll` (launcher UI companion).
- Local fallback binaries when the retail DLLs are not staged in `assets/`: `build\win32\Debug\bin\baseq3\qagamex86.dll`, `build\win32\Debug\bin\baseq3\cgamex86.dll`, and `build\win32\Debug\bin\baseq3\uix86.dll`.
- Test staging area (created automatically): `artifacts\wow64-smoketest` within the repo root.
- Automation script: `tools\ci\wow64-smoketest.ps1`.

## Manual checklist
1. Launch 32-bit PowerShell from `C:\Windows\SysWOW64\WindowsPowerShell\v1.0\powershell.exe`.
2. Install the Visual C++ 2010 SP1 x86 redistributable (`vcredist_x86.exe /quiet /norestart`).
3. Copy `qagamex86.dll`, `cgamex86.dll`, and `uix86.dll` into a writable working directory.
4. Use `dumpbin /exports` or Dependency Walker (x86) to verify `dllEntry` and `vmMain` exports are present on both gameplay modules.
5. Use a lightweight loader (or the provided PowerShell harness) to load each module; confirm WOW64 does not block the load and that the expected exports resolve to valid addresses.
6. Record the working directory, redistributable version, and results of export checks for traceability.

## Automation
Run the PowerShell harness to automate staging and export verification:

```powershell
# 32-bit PowerShell prompt is required to load x86 DLLs
cd C:\path\to\quakelive-reverse
powershell -ExecutionPolicy Bypass -File tools\ci\wow64-smoketest.ps1
```

The harness:
- Downloads the Visual C++ 2010 SP1 x86 redistributable if missing and installs it quietly.
- Copies `qagamex86.dll`, `cgamex86.dll`, and `uix86.dll` into `artifacts\wow64-smoketest`, preferring the retail `assets\quakelive\baseq3\` payload when present and otherwise falling back to the current Win32 build outputs under `build\win32\Debug\bin\baseq3\`.
- Loads `qagamex86.dll`, `cgamex86.dll`, and `uix86.dll`, probing for `dllEntry` and `vmMain`, and logs outcomes to `artifacts\wow64-smoketest\wow64-smoketest.log`.

## Latest local run

- On 2026-04-21, the harness was rerun from 32-bit PowerShell on the current Windows host and completed successfully.
- The current local run used the fallback Win32 build outputs under `build\win32\Debug\bin\baseq3\` because the retail DLLs were not staged in `assets\quakelive\baseq3\`.
- The resulting log at `artifacts\wow64-smoketest\wow64-smoketest.log` records successful `LoadLibrary` plus `dllEntry` / `vmMain` export resolution for `qagamex86.dll`, `cgamex86.dll`, and `uix86.dll`.

## Integration
- **Scripted/manual sign-off:** run the harness locally from a 32-bit PowerShell host and attach `wow64-smoketest.log` to the test report for WOW64 coverage.
- **Future automation option:** if hosted validation returns later, prefer a Windows self-hosted runner capable of launching 32-bit PowerShell and publishing the resulting log as an artifact.
