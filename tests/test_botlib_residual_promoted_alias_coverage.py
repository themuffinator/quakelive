from __future__ import annotations

import csv
import json
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]

SYMBOL_ALIASES = REPO_ROOT / "references" / "analysis" / "quakelive_symbol_aliases.json"
FUNCTIONS_CSV = (
	REPO_ROOT
	/ "references"
	/ "reverse-engineering"
	/ "ghidra"
	/ "quakelive_steam"
	/ "functions.csv"
)
QL_STEAM_HLIL_PART03 = (
	REPO_ROOT
	/ "references"
	/ "hlil"
	/ "quakelive"
	/ "quakelive_steam.exe"
	/ "quakelive_steam.exe_hlil_split"
	/ "quakelive_steam.exe_hlil_part03.txt"
)
BOTLIB_AAS_CLUSTER = REPO_ROOT / "src" / "code" / "botlib" / "be_aas_cluster.c"
BOTLIB_AAS_DEBUG = REPO_ROOT / "src" / "code" / "botlib" / "be_aas_debug.c"
BOTLIB_AI_CHAT = REPO_ROOT / "src" / "code" / "botlib" / "be_ai_chat.c"

EXPECTED_RESIDUAL_PROMOTED_ALIASES = {
	"483B90": "AAS_CheckAreaForPossiblePortals",
	"484580": "AAS_ShowFacePolygon",
	"499170": "BotFreeMatchPieces",
	"499C60": "BotCheckInitialChatIntegrety",
	"499E70": "BotCheckReplyChatIntegrety",
}

EXPECTED_RESIDUAL_PROMOTED_SIZES = {
	"483B90": 1136,
	"484580": 841,
	"499170": 70,
	"499C60": 507,
	"499E70": 504,
}

PROMOTED_BOTLIB_CORE_START = 0x4829C0
PROMOTED_BOTLIB_CORE_END = 0x4A83C0


def _read(path: Path) -> str:
	return path.read_text(encoding="utf-8")


def _aliases() -> dict[str, str]:
	return json.loads(_read(SYMBOL_ALIASES))["quakelive_steam_srp"]


def _extract_function_block(source: str, signature: str) -> str:
	start = source.find(signature)
	assert start != -1, signature
	brace = source.find("{", start)
	assert brace != -1, signature

	depth = 0
	for offset in range(brace, len(source)):
		if source[offset] == "{":
			depth += 1
		elif source[offset] == "}":
			depth -= 1
			if depth == 0:
				return source[start : offset + 1]

	raise AssertionError(f"unterminated function block: {signature}")


def _function_row(address: str) -> str:
	with FUNCTIONS_CSV.open(newline="", encoding="utf-8") as functions:
		for row in csv.DictReader(functions):
			if row["entry"] == f"00{address.lower()}":
				return f'{row["name"]},{row["entry"]},{row["size"]},{row["thunk"]},{row["calling_convention"]}'
	raise AssertionError(f"missing function row: {address}")


def test_residual_promoted_botlib_aliases_rows_and_hlil_anchors_are_pinned() -> None:
	aliases = _aliases()
	hlil = _read(QL_STEAM_HLIL_PART03)

	for address, name in EXPECTED_RESIDUAL_PROMOTED_ALIASES.items():
		assert aliases[f"sub_{address}"] == name
		assert _function_row(address) == (
			f"FUN_00{address.lower()},00{address.lower()},"
			f"{EXPECTED_RESIDUAL_PROMOTED_SIZES[address]},0,unknown"
		)

	for hlil_anchor in (
		"00483b90    int32_t sub_483b90(int32_t arg1 @ esi, int32_t arg2)",
		"00484032          int32_t eax_1 = sub_483b90(i, i)",
		"00484580    uint32_t sub_484580(int32_t arg1, int32_t arg2, int32_t arg3)",
		"00484968              sub_484580(esi_3, arg2, edx_3)",
		"00499170    void sub_499170(void* arg1)",
		"004994f5                  sub_499170(result)",
		"00499c60    int32_t* sub_499c60(int32_t* arg1)",
		"00499e70    int32_t* sub_499e70(void* arg1)",
		"0049a8a0      sub_499e70(result)",
		"0049adfb      sub_499c60(result)",
	):
		assert hlil_anchor in hlil


def test_cluster_possible_portal_and_debug_face_polygon_source_shape() -> None:
	cluster_source = _read(BOTLIB_AAS_CLUSTER)
	debug_source = _read(BOTLIB_AAS_DEBUG)

	check_portals = _extract_function_block(
		cluster_source,
		"int AAS_CheckAreaForPossiblePortals(int areanum)",
	)
	show_face = _extract_function_block(
		debug_source,
		"void AAS_ShowFacePolygon(int facenum, int color, int flip)",
	)
	show_area_polygons = _extract_function_block(
		debug_source,
		"void AAS_ShowAreaPolygons(int areanum, int color, int groundfacesonly)",
	)

	assert "if (aasworld.areasettings[areanum].contents & AREACONTENTS_CLUSTERPORTAL) return 0;" in check_portals
	assert "if (!(aasworld.areasettings[areanum].areaflags & AREA_GROUNDED)) return 0;" in check_portals
	assert "Com_Memset(numareafrontfaces, 0, sizeof(numareafrontfaces));" in check_portals
	assert "Com_Memset(numareabackfaces, 0, sizeof(numareabackfaces));" in check_portals
	assert "numareas = AAS_GetAdjacentAreasWithLessPresenceTypes_r(areanums, 0, areanum);" in check_portals
	assert "if (face->faceflags & FACE_SOLID) continue;" in check_portals
	assert "if (aasworld.areasettings[otherareanum].contents & AREACONTENTS_CLUSTERPORTAL) return 0;" in check_portals
	assert "if (!numareafrontfaces[i] || !numareabackfaces[i]) return 0;" in check_portals
	assert "if (!AAS_ConnectedAreas(frontareanums, numfrontareas)) return 0;" in check_portals
	assert "if (!AAS_ConnectedAreas(backareanums, numbackareas)) return 0;" in check_portals
	assert "if (frontedgenum == backedgenum) break;" in check_portals
	assert "aasworld.areasettings[areanums[i]].contents |= AREACONTENTS_CLUSTERPORTAL;" in check_portals
	assert "aasworld.areasettings[areanums[i]].contents |= AREACONTENTS_ROUTEPORTAL;" in check_portals
	assert 'Log_Write("possible portal: %d\\r\\n", areanums[i]);' in check_portals
	assert "return numareas;" in check_portals

	assert "vec3_t points[128];" in show_face
	assert 'botimport.Print(PRT_ERROR, "facenum %d out of range\\n", facenum);' in show_face
	assert "for (i = face->numedges-1; i >= 0; i--)" in show_face
	assert "for (i = 0; i < face->numedges; i++)" in show_face
	assert "edgenum = aasworld.edgeindex[face->firstedge + i];" in show_face
	assert "edge = &aasworld.edges[abs(edgenum)];" in show_face
	assert "VectorCopy(aasworld.vertexes[edge->v[edgenum < 0]], points[numpoints]);" in show_face
	assert "AAS_ShowPolygon(color, numpoints, points);" in show_face
	assert "AAS_ShowFacePolygon(facenum, color, face->frontarea != areanum);" in show_area_polygons


def test_chat_match_piece_and_integrity_tail_source_shape() -> None:
	chat_source = _read(BOTLIB_AI_CHAT)

	free_match_pieces = _extract_function_block(
		chat_source,
		"void BotFreeMatchPieces(bot_matchpiece_t *matchpieces)",
	)
	load_match_pieces = _extract_function_block(
		chat_source,
		"bot_matchpiece_t *BotLoadMatchPieces(source_t *source, char *endtoken)",
	)
	free_templates = _extract_function_block(
		chat_source,
		"void BotFreeMatchTemplates(bot_matchtemplate_t *mt)",
	)
	initial_integrity = _extract_function_block(
		chat_source,
		"void BotCheckInitialChatIntegrety(bot_chat_t *chat)",
	)
	reply_integrity = _extract_function_block(
		chat_source,
		"void BotCheckReplyChatIntegrety(bot_replychat_t *replychat)",
	)
	load_reply = _extract_function_block(
		chat_source,
		"bot_replychat_t *BotLoadReplyChat(char *filename)",
	)
	load_initial = _extract_function_block(
		chat_source,
		"bot_chat_t *BotLoadInitialChat(char *chatfile, char *chatname)",
	)

	assert "for (mp = matchpieces; mp; mp = nextmp)" in free_match_pieces
	assert "nextmp = mp->next;" in free_match_pieces
	assert "if (mp->type == MT_STRING)" in free_match_pieces
	assert "for (ms = mp->firststring; ms; ms = nextms)" in free_match_pieces
	assert "nextms = ms->next;" in free_match_pieces
	assert "FreeMemory(ms);" in free_match_pieces
	assert "FreeMemory(mp);" in free_match_pieces

	assert load_match_pieces.count("BotFreeMatchPieces(firstpiece);") == 5
	assert "BotFreeMatchPieces(mt->first);" in free_templates

	assert "stringlist = NULL;" in initial_integrity
	assert "for (t = chat->types; t; t = t->next)" in initial_integrity
	assert "for (cm = t->firstchatmessage; cm; cm = cm->next)" in initial_integrity
	assert "stringlist = BotCheckChatMessageIntegrety(cm->chatmessage, stringlist);" in initial_integrity
	assert "for (s = stringlist; s; s = nexts)" in initial_integrity
	assert "nexts = s->next;" in initial_integrity
	assert "FreeMemory(s);" in initial_integrity

	assert "stringlist = NULL;" in reply_integrity
	assert "for (rp = replychat; rp; rp = rp->next)" in reply_integrity
	assert "for (cm = rp->firstchatmessage; cm; cm = cm->next)" in reply_integrity
	assert "stringlist = BotCheckChatMessageIntegrety(cm->chatmessage, stringlist);" in reply_integrity
	assert "for (s = stringlist; s; s = nexts)" in reply_integrity
	assert "nexts = s->next;" in reply_integrity
	assert "FreeMemory(s);" in reply_integrity

	assert "BotCheckReplyChatIntegrety(replychatlist);" in load_reply
	assert "BotCheckInitialChatIntegrety(chat);" in load_initial


def test_promoted_botlib_core_alias_scan_has_direct_test_mentions() -> None:
	aliases = _aliases()
	botlib_test_text = "\n".join(
		path.read_text(encoding="utf-8")
		for path in sorted((REPO_ROOT / "tests").glob("test_botlib_*.py"))
	)
	missing: list[str] = []

	for key, name in aliases.items():
		if not key.startswith("sub_"):
			continue
		try:
			address = int(key[4:], 16)
		except ValueError:
			continue
		if not PROMOTED_BOTLIB_CORE_START <= address <= PROMOTED_BOTLIB_CORE_END:
			continue

		address_text = key[4:]
		if not any(
			form in botlib_test_text
			for form in (key, address_text, address_text.lower(), address_text.upper(), name)
		):
			missing.append(f"0x{address:08X} {key} {name}")

	assert missing == []
