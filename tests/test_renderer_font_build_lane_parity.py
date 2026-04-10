from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]


def _read(rel_path: str) -> str:
	return (REPO_ROOT / rel_path).read_text(encoding="utf-8")


def test_renderer_build_lane_uses_external_freetype_sdk() -> None:
	tr_font = _read("src/code/renderer/tr_font.c")
	renderer_vcxproj = _read("src/code/renderer/renderer.vcxproj")
	engine_vcxproj = _read("src/code/quakelive_steam.vcxproj")
	build_script = _read(".vscode/build.ps1")
	unix_makefile = _read("src/code/unix/Makefile")

	assert "#include <ft2build.h>" in tr_font
	assert "#include FT_ERRORS_H" in tr_font
	assert "#include FT_SYSTEM_H" in tr_font
	assert "#include FT_IMAGE_H" in tr_font
	assert "#include FT_FREETYPE_H" in tr_font
	assert "#include FT_OUTLINE_H" in tr_font

	assert "QLEnableFreeType" in renderer_vcxproj
	assert "ValidateFreeType" in renderer_vcxproj
	assert "BUILD_FREETYPE" in renderer_vcxproj

	assert "QLEnableFreeType" in engine_vcxproj
	assert "ValidateFreeType" in engine_vcxproj
	assert "FreeTypeDependencies" in engine_vcxproj

	assert "QLEnableFreeType" in build_script
	assert "FreeTypeSdkDir" in build_script
	assert "FreeTypeIncludeDir" in build_script
	assert "FreeTypeLibDir" in build_script

	assert "QL_ENABLE_FREETYPE ?= 0" in unix_makefile
	assert "pkg-config --cflags freetype2" in unix_makefile
	assert "pkg-config --libs freetype2" in unix_makefile
	assert "CLIENT_FREETYPE_CFLAGS := $(FREETYPE_CFLAGS) -DBUILD_FREETYPE" in unix_makefile
	assert "CLIENT_FREETYPE_LDFLAGS := $(FREETYPE_LDFLAGS)" in unix_makefile


def test_renderer_project_metadata_no_longer_points_at_missing_ft2_vendor_tree() -> None:
	renderer_vcxproj = _read("src/code/renderer/renderer.vcxproj")
	renderer_vcxproj_filters = _read("src/code/renderer/renderer.vcxproj.filters")
	renderer_vcproj = _read("src/code/renderer/renderer.vcproj")
	retail_font_stack = _read("docs/platform/retail-font-stack.md")
	rg_p10_note = _read("docs/reverse-engineering/renderer-freetype-build-lane-recovery-2026-04-10.md")

	assert "..\\ft2\\" not in renderer_vcxproj
	assert "..\\ft2\\" not in renderer_vcxproj_filters
	assert "..\\ft2\\" not in renderer_vcproj
	assert "explicit external FreeType SDK replacement lane" in retail_font_stack
	assert "RG-P10 is now considered complete." in rg_p10_note
