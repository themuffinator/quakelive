from __future__ import annotations

from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parent.parent
AUDIT_SCRIPT_PATH = REPO_ROOT / "tools" / "ci" / "audit-retail-dependencies.ps1"
VALIDATE_SCRIPT_PATH = REPO_ROOT / "tools" / "ci" / "validate-windows-native.ps1"
RETAIL_DEPENDENCY_DOC_PATH = REPO_ROOT / "docs" / "platform" / "retail-dependencies.md"
TOOLCHAIN_MATRIX_PATH = REPO_ROOT / "docs" / "platform" / "toolchain-matrix.md"
WINDOWS_BUILD_DOC_PATH = REPO_ROOT / "docs" / "build" / "windows.md"
WINDOWS_NATIVE_PIPELINE_PATH = REPO_ROOT / "docs" / "windows-native-pipeline.md"
WINDOWS_RUNTIME_GUIDE_PATH = REPO_ROOT / "docs" / "platform" / "windows-32bit-runtime.md"
TOOLCHAIN_CI_PATH = REPO_ROOT / "docs" / "toolchain-ci.md"
NIGHTLY_WORKFLOW_PATH = REPO_ROOT / ".github" / "workflows" / "nightly-build.yml"
INSTALL_TOOLSET_SCRIPT_PATH = REPO_ROOT / "tools" / "ci" / "install-vs-toolset.ps1"
VERIFY_TOOLSET_SCRIPT_PATH = REPO_ROOT / "tools" / "ci" / "verify-vs-toolchain.ps1"
BUILD_WINDOWS_DLLS_SCRIPT_PATH = REPO_ROOT / "tools" / "ci" / "build-windows-dlls.ps1"
NIGHTLY_BUILD_SCRIPT_PATH = REPO_ROOT / "tools" / "ci" / "nightly_build.py"
IMPLEMENTATION_PLAN_PATH = REPO_ROOT / "IMPLEMENTATION_PLAN.md"
AUDIT_PATH = REPO_ROOT / "AUDIT.md"
REPO_WIDE_AUDIT_PATH = (
	REPO_ROOT / "docs" / "reverse-engineering" / "repo-wide-parity-audit-2026-04-21.md"
)


def _read_text(path: Path) -> str:
	return path.read_text(encoding="utf-8")


def test_retail_dependency_runtime_stage_is_wired_and_documented() -> None:
	audit_script = _read_text(AUDIT_SCRIPT_PATH)
	validate_script = _read_text(VALIDATE_SCRIPT_PATH)
	retail_dependency_doc = _read_text(RETAIL_DEPENDENCY_DOC_PATH)
	toolchain_matrix = _read_text(TOOLCHAIN_MATRIX_PATH)
	windows_build_doc = _read_text(WINDOWS_BUILD_DOC_PATH)
	windows_native_pipeline = _read_text(WINDOWS_NATIVE_PIPELINE_PATH)
	windows_runtime_guide = _read_text(WINDOWS_RUNTIME_GUIDE_PATH)
	toolchain_ci = _read_text(TOOLCHAIN_CI_PATH)
	implementation_plan = _read_text(IMPLEMENTATION_PLAN_PATH)
	audit = _read_text(AUDIT_PATH)
	repo_wide_audit = _read_text(REPO_WIDE_AUDIT_PATH)

	assert "[string]$RuntimeRoot = ''" in audit_script
	assert "[switch]$SkipSteamInstall" in audit_script
	assert "Expected retail DLLs missing from ${Label}:" in audit_script
	assert "Extra DLLs present in ${Label} but absent from the reference retail payload:" in audit_script
	assert "Retail-hash-optional DLL slots:" in audit_script
	assert "'baseq3\\cgamex86.dll'" in audit_script
	assert "'baseq3\\qagamex86.dll'" in audit_script
	assert "'baseq3\\uix86.dll'" in audit_script
	assert 'throw \'No audit target was supplied. Provide -RuntimeRoot when using -SkipSteamInstall.\'' in audit_script

	assert "function Initialize-RetailRuntimeStage" in validate_script
	assert 'build\\win32\\$ConfigurationName\\retail-runtime' in validate_script
	assert "& $dependencyAudit -RepoRoot $RepoRoot -RuntimeRoot $retailRuntimeRoot -SkipSteamInstall -Strict:$true" in validate_script
	assert 'Write-Host "Validated staged retail runtime root: $retailRuntimeRoot"' in validate_script

	assert "build\\win32\\<Config>\\retail-runtime\\" in retail_dependency_doc
	assert "build\\win32\\<Config>\\bin\\" in retail_dependency_doc
	assert "strict retail payload boundary" in retail_dependency_doc
	assert "pwsh tools\\ci\\audit-retail-dependencies.ps1 -RuntimeRoot build\\win32\\Release\\retail-runtime -SkipSteamInstall -Strict" in retail_dependency_doc

	assert "retail-runtime" in toolchain_matrix
	assert "audit-retail-dependencies.ps1 -RuntimeRoot build\\win32\\Release\\retail-runtime -SkipSteamInstall -Strict" in toolchain_matrix
	assert "Expand local/runtime guards so parity builds fail fast when extra non-retail runtime DLLs are introduced alongside the launcher payload." not in toolchain_matrix

	assert "validate-windows-native.ps1 -PlatformToolset v100 -RuntimeProfile retail" in windows_build_doc
	assert "retail-runtime" in windows_build_doc

	assert "validate-windows-native.ps1 -PlatformToolset v100 -RuntimeProfile retail" in windows_native_pipeline
	assert "build\\win32\\<Config>\\retail-runtime\\" in windows_native_pipeline

	assert "build\\win32\\Release\\retail-runtime" in windows_runtime_guide

	assert "validate-windows-native.ps1 -PlatformToolset v100 -RuntimeProfile retail" in toolchain_ci
	assert "retail-runtime" in toolchain_ci

	assert "### Task A6f: Add a strict staged retail-runtime DLL audit for native Windows validation [COMPLETED]" in implementation_plan
	assert "The retail native validation lane now also stages" in audit
	assert "The retail native validation lane now also stages" in repo_wide_audit


def test_hosted_nightly_uses_preinstalled_vs2022_toolset() -> None:
	nightly_workflow = _read_text(NIGHTLY_WORKFLOW_PATH)
	install_toolset = _read_text(INSTALL_TOOLSET_SCRIPT_PATH)
	verify_toolset = _read_text(VERIFY_TOOLSET_SCRIPT_PATH)
	validate_script = _read_text(VALIDATE_SCRIPT_PATH)
	build_windows_dlls = _read_text(BUILD_WINDOWS_DLLS_SCRIPT_PATH)
	nightly_build = _read_text(NIGHTLY_BUILD_SCRIPT_PATH)
	toolchain_ci = _read_text(TOOLCHAIN_CI_PATH)

	assert "NIGHTLY_PLATFORM_TOOLSET: v143" in nightly_workflow
	assert "Prepare nightly metadata" in nightly_workflow
	assert "QL_POSIX_PACKAGE_VERSION" in nightly_workflow
	assert "-DisableOptionalCodecs" in nightly_workflow
	assert "Publish Windows build logs" in nightly_workflow
	assert "Publish nightly GitHub release" in nightly_workflow
	assert "contents: write" in nightly_workflow
	assert "release_tag: ${{ steps.version.outputs.release_tag }}" in nightly_workflow
	assert "release_title: ${{ steps.version.outputs.release_title }}" in nightly_workflow
	assert "--asset-output-root artifacts/nightly/release-assets" in nightly_workflow
	assert "gh release create" in nightly_workflow
	assert "gh release upload" in nightly_workflow
	assert "--latest" in nightly_workflow
	assert "--latest=false" not in nightly_workflow
	assert "--prerelease" not in nightly_workflow
	assert "prerelease=false" in nightly_workflow
	assert "nightly-release-manifest.json" in nightly_workflow
	assert "SHA256SUMS.txt" in nightly_workflow
	assert "release-notes.md" in nightly_workflow
	assert "Microsoft.VisualStudio.Component.VC.Tools.x86.x64" in install_toolset
	assert "[ValidateSet('v100', 'v141', 'v143')]" in install_toolset
	assert "'v143' { return 'Microsoft.VisualStudio.Component.VC.Tools.x86.x64' }" in install_toolset

	assert "[ValidateSet('v100', 'v141', 'v143')]" in verify_toolset
	assert "DisplayName = 'Visual Studio 2022 (v143)'" in verify_toolset
	assert "'v143' {" in verify_toolset
	assert "ComponentId = 'Microsoft.VisualStudio.Component.VC.Tools.x86.x64'" in verify_toolset

	assert "[string]$PlatformToolset = 'v143'" in validate_script
	assert "[string]$ProjectToolset = 'v141'" in validate_script
	assert "[switch]$DisableOptionalCodecs" in validate_script
	assert "-DisableOptionalCodecs:$DisableOptionalCodecs" in validate_script
	assert "'v143' { 'Microsoft.VisualStudio.Component.VC.Tools.x86.x64' }" in build_windows_dlls
	assert "$PlatformToolset -in @('v141', 'v143')" in build_windows_dlls
	assert "[string]$BuildLogRoot = ''" in build_windows_dlls
	assert "'/p:QLEnableOgg=0'" in build_windows_dlls
	assert "'/p:QLEnablePng=0'" in build_windows_dlls
	assert "'/p:QLEnableFreeType=0'" in build_windows_dlls
	assert "msbuild-${safeConfiguration}-${safePlatform}-${safeToolset}.log" in build_windows_dlls
	assert 'package.add_argument("--toolset", default="v143")' in nightly_build
	assert 'subparsers.add_parser("release-manifest"' in nightly_build
	assert 'subparsers.add_parser("release-notes"' in nightly_build
	assert "RELEASE_PACKAGE_SUFFIXES" in nightly_build
	assert "def is_release_package" in nightly_build
	assert "def stage_release_asset" in nightly_build
	assert "build/re/windows" not in nightly_build
	assert "clean-room" not in nightly_build
	assert '"nightly-release-manifest.json"' in nightly_build
	assert '"SHA256SUMS.txt"' in nightly_build
	assert "hosted-compatible `v143` toolset" in toolchain_ci
