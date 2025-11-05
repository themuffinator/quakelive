# escape=`
# Visual C++ 2010 SP1 build tools on top of Windows Server Core.
# Captures the linker signature observed in quakelive_steam.exe (LINK 10.00).

FROM mcr.microsoft.com/windows/servercore:ltsc2019

SHELL ["powershell", "-Command", "$ErrorActionPreference = 'Stop'; $ProgressPreference = 'SilentlyContinue';"]

# Install Chocolatey for package management.
RUN Set-ExecutionPolicy Bypass -Scope Process -Force; \
    [System.Net.ServicePointManager]::SecurityProtocol = [System.Net.SecurityProtocolType]::Tls12; \
    iex ((New-Object System.Net.WebClient).DownloadString('https://community.chocolatey.org/install.ps1'))

# Visual Studio 2010 requires the Windows 7.1 SDK for 32-bit libs.
RUN choco install windows-sdk-7.1 -y --checksum64 7e6be6961f0e59101cf15f183e2a661843a95e6f389bb39ead7e454e5d604378

# Install Visual Studio 2010 Professional silently (installs VC10 compiler + linker).
RUN choco install visualstudio2010professional -y --package-parameters "'--NoWeb --Quiet --NoRestart'"

# Set up convenience script that drops the user into an x86 developer prompt.
RUN New-Item -ItemType Directory -Path C:\toolchain | Out-Null; \
    Set-Content -Path C:\toolchain\vcvars32.cmd -Value "@echo off`r`ncall \"C:\Program Files (x86)\Microsoft Visual Studio 10.0\VC\vcvarsall.bat\" x86`r`ncmd.exe"; \
    setx PATH "$env:PATH;C:\Program Files (x86)\Microsoft Visual Studio 10.0\VC\bin;C:\Program Files\Microsoft SDKs\Windows\v7.1\Bin"

WORKDIR C:\workspace

ENTRYPOINT ["cmd.exe", "/k", "C:\\toolchain\\vcvars32.cmd"]
