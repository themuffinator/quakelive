"""Guard recovered cgame drawtools helpers against retail boundary drift."""

from __future__ import annotations

from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parent.parent
CG_DRAWTOOLS = REPO_ROOT / "src" / "code" / "cgame" / "cg_drawtools.c"
CG_LOCAL = REPO_ROOT / "src" / "code" / "cgame" / "cg_local.h"
CG_BG_PLAN = REPO_ROOT / "docs" / "reverse-engineering" / "cgame-bg-parity-implementation-plan.md"


def _block_from_marker(source: str, marker: str) -> str:
	start = source.rindex(marker)
	brace_start = source.index("{", start)
	depth = 0

	for index in range(brace_start, len(source)):
		char = source[index]
		if char == "{":
			depth += 1
		elif char == "}":
			depth -= 1
			if depth == 0:
				return source[start:index + 1]

	raise AssertionError(f"Unbalanced block for marker: {marker}")


def test_drawtools_restore_the_retail_uv_preserving_picture_helper() -> None:
	source = CG_DRAWTOOLS.read_text(encoding="utf-8")
	header = CG_LOCAL.read_text(encoding="utf-8")
	draw_pic_st = _block_from_marker(source, "void CG_DrawPicST")
	draw_pic = _block_from_marker(source, "void CG_DrawPic")
	tile_clear_box = _block_from_marker(source, "static void CG_TileClearBox")

	assert "void CG_DrawPicST( float x, float y, float width, float height, float s1, float t1, float s2, float t2, qhandle_t hShader );" in header
	assert "CG_AdjustFrom640( &x, &y, &width, &height );" in draw_pic_st
	assert "trap_R_DrawStretchPic( x, y, width, height, s1, t1, s2, t2, hShader );" in draw_pic_st
	assert "CG_DrawPicST( x, y, width, height, 0.0f, 0.0f, 1.0f, 1.0f, hShader );" in draw_pic
	assert "CG_DrawPicST( x, y, w, h, s1, t1, s2, t2, hShader );" in tile_clear_box


def test_cgame_bg_plan_no_longer_lists_drawpicst_as_an_open_direct_owner_gap() -> None:
	plan = CG_BG_PLAN.read_text(encoding="utf-8")
	cg_d_row = plan.split("| `CG-D` |", 1)[1].splitlines()[0]

	assert "`CG_DrawPicST`" not in cg_d_row
