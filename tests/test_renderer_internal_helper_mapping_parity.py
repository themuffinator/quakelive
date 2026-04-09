from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]


def _read(rel_path: str) -> str:
	return (REPO_ROOT / rel_path).read_text(encoding="utf-8")


def _normalize_whitespace(text: str) -> str:
	return " ".join(text.split())


def test_mapping_round_100_records_rg_p5_closure_without_invented_aliases() -> None:
	mapping_round = _read("docs/reverse-engineering/quakelive_steam_mapping_round_100.md")
	normalized = _normalize_whitespace(mapping_round)

	assert "# Quake Live Steam Host Mapping Round 100" in mapping_round
	assert "## Phase 5 Closure Update (2026-04-09)" in mapping_round
	assert "no new aliases were promoted in this pass" in mapping_round
	assert "source-backed compatibility decompositions or compiler-shaped micro-splits" in normalized
	assert "No unresolved high-impact ownership gap remains in an active runtime path." in mapping_round


def test_renderer_internal_helper_ownership_note_bounds_all_rg_g06_file_bands() -> None:
	ownership_note = _read("docs/reverse-engineering/renderer-internal-helper-ownership-2026-04-09.md")
	normalized = _normalize_whitespace(ownership_note)

	assert "## Phase 5 Ownership Closure" in ownership_note
	assert "| `tr_backend.c` |" in ownership_note
	assert "| `tr_bsp.c` |" in ownership_note
	assert "| `tr_curve.c` |" in ownership_note
	assert "| `tr_flares.c` |" in ownership_note
	assert "| `win_glimp.c` |" in ownership_note
	assert "source-backed compatibility decompositions" in normalized
	assert "compiler-shaped splits" in normalized
	assert "No unresolved high-impact ownership gap remains in an active runtime path." in ownership_note


def test_renderer_audit_and_repo_summaries_mark_rg_p5_complete() -> None:
	renderer_audit = _read("docs/reverse-engineering/renderer-full-parity-audit-and-implementation-plan-2026-04-09.md")
	audit_summary = _read("AUDIT.md")
	implementation_plan = _read("IMPLEMENTATION_PLAN.md")

	assert "`RG-G06` stays closed" in renderer_audit
	assert "The earlier `RG-P1`..`RG-P6` work remains valid" in renderer_audit
	assert "## What Still Holds From `RG-P1`..`RG-P6`" in renderer_audit
	assert "The open renderer gap register is now wider than the old single-tranche `RG-G05` story." in audit_summary
	assert "`RG-P5` is now complete." in audit_summary
	assert "Task 75: Renderer strict retail-font-stack re-audit and closure-plan refresh [COMPLETED]" in implementation_plan
	assert "Task 73: Renderer internal helper-family ownership closure tranche [COMPLETED]" in implementation_plan
	assert "Parity estimate: **before 93% -> after 96%** (`RG-P5` complete; `RG-G06` closed)" in implementation_plan


def test_representative_rg_g06_helper_seams_remain_present_in_source() -> None:
	tr_backend = _read("src/code/renderer/tr_backend.c")
	tr_bsp = _read("src/code/renderer/tr_bsp.c")
	tr_curve = _read("src/code/renderer/tr_curve.c")
	tr_flares = _read("src/code/renderer/tr_flares.c")
	win_glimp = _read("src/code/win32/win_glimp.c")

	assert "void RB_ExecuteRenderCommands( const void *data ) {" in tr_backend
	assert "static void RBPP_RebuildState( void ) {" in tr_backend
	assert "void GL_Bind( image_t *image ) {" in tr_backend
	assert "static\tvoid R_LoadSurfaces( lump_t *surfs, lump_t *verts, lump_t *indexLump ) {" in tr_bsp
	assert "int R_StitchPatches( int grid1num, int grid2num ) {" in tr_bsp
	assert "static void LerpDrawVert( drawVert_t *a, drawVert_t *b, drawVert_t *out ) {" in tr_curve
	assert "void R_FreeSurfaceGridMesh( srfGridMesh_t *grid ) {" in tr_curve
	assert "void RB_RenderFlares (void) {" in tr_flares
	assert "void RB_TestFlare( flare_t *f ) {" in tr_flares
	assert "static void GLW_StartOpenGL( void )" in win_glimp
	assert "void GLimp_Init( void )" in win_glimp
