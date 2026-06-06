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
QL_STEAM_HLIL_PART04 = (
	REPO_ROOT
	/ "references"
	/ "hlil"
	/ "quakelive"
	/ "quakelive_steam.exe"
	/ "quakelive_steam.exe_hlil_split"
	/ "quakelive_steam.exe_hlil_part04.txt"
)
QL_STEAM_HLIL_PART07 = (
	REPO_ROOT
	/ "references"
	/ "hlil"
	/ "quakelive"
	/ "quakelive_steam.exe"
	/ "quakelive_steam.exe_hlil_split"
	/ "quakelive_steam.exe_hlil_part07.txt"
)
CLIENT_CL_CGAME = REPO_ROOT / "src" / "code" / "client" / "cl_cgame.c"
CGAME_PUBLIC = REPO_ROOT / "src" / "code" / "cgame" / "cg_public.h"

CGAME_NATIVE_SLAB_START = 0x4AF820
CGAME_NATIVE_SLAB_END = 0x4B0500

EXPECTED_NATIVE_SLAB_ALIASES = {
	"4AF820": ("CL_GetServerCommand", 958),
	"4AFBF0": ("CL_ShutdownCGame", 72),
	"4AFC40": ("QLCGImport_AddCommand", 19),
	"4AFC60": ("QLCGImport_RemoveCommand", 9),
	"4AFC70": ("QLCGImport_SendClientCommand", 9),
	"4AFC80": ("QLCGImport_CM_LoadMap", 26),
	"4AFCB0": ("QLCGImport_CM_InlineModel", 9),
	"4AFCC0": ("QLCGImport_CM_TempBoxModel", 23),
	"4AFCE0": ("QLCGImport_CM_TempCapsuleModel", 23),
	"4AFD00": ("QLCGImport_CM_PointContents", 9),
	"4AFD10": ("QLCGImport_CM_TransformedPointContents", 9),
	"4AFD20": ("QLCGImport_CM_BoxTrace", 43),
	"4AFD50": ("QLCGImport_CM_CapsuleTrace", 43),
	"4AFD80": ("QLCGImport_CM_TransformedBoxTrace", 51),
	"4AFDC0": ("QLCGImport_CM_TransformedCapsuleTrace", 51),
	"4AFE00": ("QLCGImport_CM_MarkFragments", 10),
	"4AFE10": ("QLCGImport_S_StartSound", 9),
	"4AFE20": ("QLCGImport_S_StartSoundVolume", 36),
	"4AFE50": ("QLCGImport_S_StartLocalSoundVolume", 28),
	"4AFE90": ("QLCGImport_S_AddLoopingSound", 9),
	"4AFEA0": ("QLCGImport_S_UpdateEntityPosition", 9),
	"4AFEB0": ("QLCGImport_S_Respatialize", 9),
	"4AFEC0": ("QLCGImport_S_RegisterSound", 9),
	"4AFED0": ("QLCGImport_S_StartBackgroundTrack", 9),
	"4AFEE0": ("QLCGImport_R_LoadWorldMap", 10),
	"4AFEF0": ("QLCGImport_R_RegisterShader", 10),
	"4AFF00": ("QLCGImport_R_RegisterShaderNoMip", 10),
	"4AFF20": ("QLCGImport_SetupAdvertCellShader", 9),
	"4AFF30": ("QLCGImport_RefreshAdvertCellShader", 9),
	"4AFF40": ("QLCGImport_SetActiveAdvert", 9),
	"4AFF50": ("QLCGImport_AdvertisementBridge_SetMapPath", 9),
	"4AFF80": ("QLCGImport_AdvertisementBridge_UpdateViewParameters", 60),
	"4AFFD0": ("QLCGImport_AdvertisementBridge_SetFrameTime", 9),
	"4AFFE0": ("QLCGImport_AdvertisementBridge_ClearDelay", 9),
	"4AFFF0": ("QLImport_R_RegisterFont", 10),
	"4B0000": ("QLCGImport_R_AddRefEntityToScene", 10),
	"4B0010": ("QLCGImport_R_AddPolyToScene", 28),
	"4B0030": ("QLCGImport_R_AddPolysToScene", 10),
	"4B0040": ("QLCGImport_R_LightForPoint", 10),
	"4B0050": ("QLCGImport_AdvertisementBridge_UpdateLoadingViewParameters", None),
	"4B0060": ("QLCGImport_R_SetColor", 10),
	"4B0070": ("QLCGImport_R_DrawStretchPic", 76),
	"4B00D0": ("QLCGImport_R_LerpTag", 41),
	"4B0100": ("QLCGImport_R_RemapShader", 10),
	"4B0110": ("QLCGImport_GetGameState", 27),
	"4B0130": ("QLCGImport_GetCurrentSnapshotNumber", 26),
	"4B0150": ("QLCGImport_GetSnapshot", 9),
	"4B0160": ("QLCGImport_GetServerCommand", 9),
	"4B0170": ("QLCGImport_GetCurrentCmdNumber", None),
	"4B0180": ("QLCGImport_GetUserCmd", 89),
	"4B01E0": ("QLCGImport_SetUserCmdValue", 40),
	"4B0210": ("QLCGImport_MemoryRemaining", None),
	"4B0230": ("QLCGImport_Key_SetCatcher", 9),
	"4B0240": ("QLCGImport_Key_GetKey", 9),
	"4B0250": ("QLCGImport_Key_KeynumToStringBuf", 9),
	"4B0260": ("QLCGImport_Key_GetBindingBuf", 9),
	"4B0270": ("QLUIImport_PC_LoadSource", 18),
	"4B0290": ("QLUIImport_PC_FreeSource", 18),
	"4B02B0": ("QLUIImport_PC_ReadToken", 18),
	"4B02D0": ("QLUIImport_PC_SourceFileAndLine", 17),
	"4B0300": ("QLCGImport_CIN_PlayCinematic", 9),
	"4B0310": ("QLCGImport_CIN_StopCinematic", 9),
	"4B0320": ("QLCGImport_CIN_DrawCinematic", 9),
	"4B0330": ("QLCGImport_GetEntityToken", 10),
	"4B0340": ("QLUIImport_SetCursorPos", 9),
	"4B03B0": ("QLCGImport_PublishTaggedInfoString", 9),
	"4B03C0": ("QLCGImport_R_MirrorPoint", 10),
	"4B03D0": ("QLCGImport_R_MirrorVector", 10),
	"4B03E0": ("QLImport_DrawScaledText", 49),
	"4B0420": ("QLCGImport_ToggleClientMute", 21),
	"4B0440": ("QLCGImport_GetAvatarImageHandle", 21),
	"4B0460": ("CL_LoadCGameForCvarRegistration", 87),
	"4B04C0": ("CL_InitCGame", 321),
}

EXPECTED_IMPORT_ASSIGNMENTS = (
	("CG_QL_IMPORT_ADDCOMMAND", "QL_CG_trap_AddCommand"),
	("CG_QL_IMPORT_REMOVECOMMAND", "QL_CG_trap_RemoveCommand"),
	("CG_QL_IMPORT_SENDCLIENTCOMMAND", "QL_CG_trap_SendClientCommand"),
	("CG_QL_IMPORT_CM_LOADMAP", "QL_CG_trap_CM_LoadMap"),
	("CG_QL_IMPORT_CM_INLINEMODEL", "QL_CG_trap_CM_InlineModel"),
	("CG_QL_IMPORT_CM_TEMPBOXMODEL", "QL_CG_trap_CM_TempBoxModel"),
	("CG_QL_IMPORT_CM_TEMPCAPSULEMODEL", "QL_CG_trap_CM_TempCapsuleModel"),
	("CG_QL_IMPORT_CM_POINTCONTENTS", "QL_CG_trap_CM_PointContents"),
	("CG_QL_IMPORT_CM_TRANSFORMEDPOINTCONTENTS", "QL_CG_trap_CM_TransformedPointContents"),
	("CG_QL_IMPORT_CM_BOXTRACE", "QL_CG_trap_CM_BoxTrace"),
	("CG_QL_IMPORT_CM_CAPSULETRACE", "QL_CG_trap_CM_CapsuleTrace"),
	("CG_QL_IMPORT_CM_TRANSFORMEDBOXTRACE", "QL_CG_trap_CM_TransformedBoxTrace"),
	("CG_QL_IMPORT_CM_TRANSFORMEDCAPSULETRACE", "QL_CG_trap_CM_TransformedCapsuleTrace"),
	("CG_QL_IMPORT_CM_MARKFRAGMENTS", "QL_CG_trap_CM_MarkFragments"),
	("CG_QL_IMPORT_S_STARTSOUND", "QL_CG_trap_S_StartSound"),
	("CG_QL_IMPORT_S_STARTSOUND_VOLUME", "QL_CG_trap_S_StartSoundVolume"),
	("CG_QL_IMPORT_S_STARTLOCALSOUND_VOLUME", "QL_CG_trap_S_StartLocalSoundVolume"),
	("CG_QL_IMPORT_S_ADDLOOPINGSOUND", "QL_CG_trap_S_AddLoopingSound"),
	("CG_QL_IMPORT_S_UPDATEENTITYPOSITION", "QL_CG_trap_S_UpdateEntityPosition"),
	("CG_QL_IMPORT_S_RESPATIALIZE", "QL_CG_trap_S_Respatialize"),
	("CG_QL_IMPORT_S_REGISTERSOUND", "QL_CG_trap_S_RegisterSound"),
	("CG_QL_IMPORT_S_STARTBACKGROUNDTRACK", "QL_CG_trap_S_StartBackgroundTrack"),
	("CG_QL_IMPORT_R_LOADWORLDMAP", "QL_CG_trap_R_LoadWorldMap"),
	("CG_QL_IMPORT_R_REGISTERSHADER", "QL_CG_trap_R_RegisterShader"),
	("CG_QL_IMPORT_R_REGISTERSHADERNOMIP", "QL_CG_trap_R_RegisterShaderNoMip"),
	("CG_QL_IMPORT_SETUP_ADVERT_CELL_SHADER", "QL_CG_trap_SetupAdvertCellShader"),
	("CG_QL_IMPORT_REFRESH_ADVERT_CELL_SHADER", "QL_CG_trap_RefreshAdvertCellShader"),
	("CG_QL_IMPORT_SET_ACTIVE_ADVERT", "QL_CG_trap_SetActiveAdvert"),
	("CG_QL_IMPORT_ADVERTISEMENTBRIDGE_SET_MAP_PATH", "QL_CG_trap_AdvertisementBridge_SetMapPath"),
	("CG_QL_IMPORT_ADVERTISEMENTBRIDGE_UPDATE_VIEW_PARAMETERS", "QL_CG_trap_AdvertisementBridge_UpdateViewParameters"),
	("CG_QL_IMPORT_ADVERTISEMENTBRIDGE_SETFRAMETIME", "QL_CG_trap_AdvertisementBridge_SetFrameTime"),
	("CG_QL_IMPORT_ADVERTISEMENTBRIDGE_CLEAR_DELAY", "QL_CG_trap_AdvertisementBridge_ClearDelay"),
	("CG_QL_IMPORT_R_REGISTERFONT", "QL_CG_trap_R_RegisterFont"),
	("CG_QL_IMPORT_R_ADDREFENTITYTOSCENE", "QL_CG_trap_R_AddRefEntityToScene"),
	("CG_QL_IMPORT_R_ADDPOLYTOSCENE", "QL_CG_trap_R_AddPolyToScene"),
	("CG_QL_IMPORT_R_ADDPOLYSTOSCENE", "QL_CG_trap_R_AddPolysToScene"),
	("CG_QL_IMPORT_R_LIGHTFORPOINT", "QL_CG_trap_R_LightForPoint"),
	("CG_QL_IMPORT_ADVERTISEMENTBRIDGE_UPDATE_LOADING_VIEW_PARAMETERS", "QL_CG_trap_AdvertisementBridge_UpdateLoadingViewParameters"),
	("CG_QL_IMPORT_R_SETCOLOR", "QL_CG_trap_R_SetColor_QL"),
	("CG_QL_IMPORT_R_DRAWSTRETCHPIC", "QL_CG_trap_R_DrawStretchPic"),
	("CG_QL_IMPORT_R_LERPTAG", "QL_CG_trap_R_LerpTag"),
	("CG_QL_IMPORT_R_REMAP_SHADER", "QL_CG_trap_R_RemapShader"),
	("CG_QL_IMPORT_GETGAMESTATE", "QL_CG_trap_GetGameState"),
	("CG_QL_IMPORT_GETCURRENTSNAPSHOTNUMBER", "QL_CG_trap_GetCurrentSnapshotNumber"),
	("CG_QL_IMPORT_GETSNAPSHOT", "QL_CG_trap_GetSnapshot"),
	("CG_QL_IMPORT_GETSERVERCOMMAND", "QL_CG_trap_GetServerCommand"),
	("CG_QL_IMPORT_GETCURRENTCMDNUMBER", "QL_CG_trap_GetCurrentCmdNumber"),
	("CG_QL_IMPORT_GETUSERCMD", "QL_CG_trap_GetUserCmd"),
	("CG_QL_IMPORT_SETUSERCMDVALUE", "QL_CG_trap_SetUserCmdValue"),
	("CG_QL_IMPORT_MEMORY_REMAINING", "QL_CG_trap_MemoryRemaining"),
	("CG_QL_IMPORT_KEY_SETCATCHER", "QL_CG_trap_Key_SetCatcher"),
	("CG_QL_IMPORT_KEY_GETKEY", "QL_CG_trap_Key_GetKey"),
	("CG_QL_IMPORT_KEY_KEYNUMTOSTRINGBUF", "QL_CG_trap_Key_KeynumToStringBuf"),
	("CG_QL_IMPORT_KEY_GETBINDINGBUF", "QL_CG_trap_Key_GetBindingBuf"),
	("CG_QL_IMPORT_PC_LOAD_SOURCE", "QL_CG_trap_PC_LoadSource"),
	("CG_QL_IMPORT_PC_FREE_SOURCE", "QL_CG_trap_PC_FreeSource"),
	("CG_QL_IMPORT_PC_READ_TOKEN", "QL_CG_trap_PC_ReadToken"),
	("CG_QL_IMPORT_PC_SOURCE_FILE_AND_LINE", "QL_CG_trap_PC_SourceFileAndLine"),
	("CG_QL_IMPORT_CIN_PLAYCINEMATIC", "QL_CG_trap_CIN_PlayCinematic"),
	("CG_QL_IMPORT_CIN_STOPCINEMATIC", "QL_CG_trap_CIN_StopCinematic"),
	("CG_QL_IMPORT_CIN_DRAWCINEMATIC", "QL_CG_trap_CIN_DrawCinematic"),
	("CG_QL_IMPORT_GET_ENTITY_TOKEN", "QL_CG_trap_GetEntityToken"),
	("CG_QL_IMPORT_PUBLISH_TAGGED_INFO_STRING", "QL_CG_trap_PublishTaggedInfoString"),
	("CG_QL_IMPORT_R_MIRROR_POINT", "QL_CG_trap_R_MirrorPoint"),
	("CG_QL_IMPORT_R_MIRROR_VECTOR", "QL_CG_trap_R_MirrorVector"),
	("CG_QL_IMPORT_DRAW_SCALED_TEXT", "QL_CG_trap_DrawScaledText"),
	("CG_QL_IMPORT_TOGGLE_CLIENT_MUTE", "QL_CG_trap_ToggleClientMute"),
	("CG_QL_IMPORT_GET_AVATAR_IMAGE_HANDLE", "QL_CG_trap_GetAvatarImageHandle"),
)


def _read(path: Path) -> str:
	return path.read_text(encoding="utf-8")


def _aliases() -> dict[str, str]:
	return json.loads(_read(SYMBOL_ALIASES))["quakelive_steam_srp"]


def _function_rows() -> dict[str, str]:
	rows: dict[str, str] = {}
	with FUNCTIONS_CSV.open(newline="", encoding="utf-8") as functions:
		for row in csv.DictReader(functions):
			rows[row["entry"].upper()[2:]] = (
				f'{row["name"]},{row["entry"]},{row["size"]},{row["thunk"]},{row["calling_convention"]}'
			)
	return rows


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


def test_native_cgame_import_slab_aliases_and_rows_are_pinned() -> None:
	aliases = _aliases()
	rows = _function_rows()

	for address, (name, size) in EXPECTED_NATIVE_SLAB_ALIASES.items():
		assert aliases[f"sub_{address}"] == name
		if size is not None:
			assert rows[address] == f"FUN_00{address.lower()},00{address.lower()},{size},0,unknown"

	assert "4B0050" not in rows
	assert "4B0170" not in rows
	assert "4B0210" not in rows


def test_native_cgame_import_slab_hlil_wrapper_shapes_are_pinned() -> None:
	hlil = _read(QL_STEAM_HLIL_PART04)
	table_hlil = _read(QL_STEAM_HLIL_PART07)

	for hlil_anchor in (
		"004afc40    int32_t sub_4afc40(char* arg1)",
		"004afc52  return sub_4c81d0(arg1, 0)",
		"004afc64  return sub_4c8270() __tailcall",
		"004afc74  return sub_4b8200() __tailcall",
		"004afc80    char* __convention(\"regparm\") sub_4afc80",
		"004afc99  return sub_4c0580(arg4, 1, &var_8)",
		"004afcd6  return sub_4c0400(arg1, arg2, 0)",
		"004afcf6  return sub_4c0400(arg1, arg2, 1)",
		"004afd4a  return sub_4c78c0(arg1, arg2, arg3, arg4, arg5, arg6, arg7, 0)",
		"004afd7a  return sub_4c78c0(arg1, arg2, arg3, arg4, arg5, arg6, arg7, 1)",
		"004afdb2  return sub_4c7900(arg1, arg2, arg3, arg4, arg5, arg6, arg7, arg8, arg9, 0)",
		"004afdf2  return sub_4c7900(arg1, arg2, arg3, arg4, arg5, arg6, arg7, arg8, arg9, 1)",
		"004afe2c  int32_t var_8 = ecx",
		"004afe43  return sub_4da050(arg1, arg2, arg3, arg4, fconvert.s(fconvert.t(arg5)))",
		"004aff20    int32_t sub_4aff20()",
		"004aff24  return sub_4f21e0() __tailcall",
		"004aff80    int32_t sub_4aff80(int32_t arg1, int32_t arg2, int32_t arg3, int32_t arg4, float arg5, float arg6, float arg7, int32_t arg8, int32_t arg9)",
		"004affbb  return sub_4f1f70(arg1, arg2, arg3, arg4, fconvert.s(fconvert.t(arg5)),",
		"004b0010    int32_t sub_4b0010(int32_t arg1, int32_t arg2, int32_t arg3)",
		"004b002b  return data_146cc8c(arg1, arg2, arg3, 1)",
		"004b0110    int32_t sub_4b0110(int32_t arg1)",
		"004b012a  return memcpy(arg1, &data_146cfd4, 0x4e84)",
		"004b0130    int32_t sub_4b0130(int32_t* arg1, int32_t* arg2)",
		"004b013f  *arg1 = data_146cd30",
		"004b0146  *arg2 = result",
		"004b0154  return sub_4af570() __tailcall",
		"004b0164  return sub_4af820() __tailcall",
		"004b0170    int32_t sub_4b0170()",
		"004b0175  return data_14725d0",
		"004b0180    int32_t sub_4b0180(int32_t arg1, int32_t arg2)",
		"004b0199      sub_4c9b60(1, \"CL_GetUserCmd: %i >= %i\")",
		"004b01ce  __builtin_memcpy(dest: arg2, src: (arg1 & 0x3f) * 0x1c + &data_1471ed0, n: 0x1c)",
		"004b01e0    int32_t sub_4b01e0(int32_t arg1, int32_t arg2, float arg3, int32_t arg4)",
		"004b0210    int32_t j_sub_4c92a0()",
		"004b0210  return sub_4c92a0() __tailcall",
		"004b0270    int32_t sub_4b0270()",
		"004b0280  jump(*(data_13e1844 + 0x204))",
		"004b02b0    int32_t sub_4b02b0()",
		"004b02c0  jump(*(data_13e1844 + 0x20c))",
		"004b03b4  return sub_4bf5d0() __tailcall",
		"004b03e0    int32_t sub_4b03e0(int32_t arg1, int32_t arg2, int32_t arg3, int32_t arg4, float arg5, int32_t arg6, int32_t arg7, int32_t arg8)",
		"004b0410  return data_146ccf0(arg1, arg2, arg3, arg4, fconvert.s(fconvert.t(arg5)), arg6, arg7,",
		"004b0434  return sub_461c00(arg1, arg2)",
		"004b0454  return sub_460f30(arg1, arg2)",
		"004b0460    void* __fastcall sub_4b0460(int32_t arg1)",
		"004b04c0    int32_t sub_4b04c0()",
	):
		assert hlil_anchor in hlil

	for table_anchor in (
		"00565a6c  void* data_565a6c = sub_4affc0",
		"00565a70  void* data_565a70 = sub_4bef40",
		"00565a98  void* data_565a98 = sub_4b00c0",
		"00565abc  void* data_565abc = sub_4b0170",
		"00565b2c  void* data_565b2c = sub_4b0370",
	):
		assert table_anchor in table_hlil


def test_native_cgame_import_table_source_matches_reconstructed_slot_surface() -> None:
	cl_cgame = _read(CLIENT_CL_CGAME)
	cgame_public = _read(CGAME_PUBLIC)
	import_block = _extract_function_block(cl_cgame, "static void CL_InitCGameImports")

	assert "CG_QL_IMPORT_COUNT = 128," in cgame_public
	assert "Com_Memset( ql_cgame_imports, 0, sizeof( ql_cgame_imports ) );" in import_block
	assert "ql_cgame_currentColor[0] = 1.0f;" in import_block

	for slot_name, trap_name in EXPECTED_IMPORT_ASSIGNMENTS:
		assert f"{slot_name}" in cgame_public
		assert f"ql_cgame_imports[{slot_name}] = (ql_import_f){trap_name};" in import_block

	for reserved_slot in (
		"CG_QL_IMPORT_ADVERTISEMENTBRIDGE_RESERVED_59",
		"CG_QL_IMPORT_ADVERTISEMENTBRIDGE_RESERVED_63",
		"CG_QL_IMPORT_ADVERTISEMENTBRIDGE_RESERVED_65",
		"CG_QL_IMPORT_RETAIL_RESERVED_66",
		"CG_QL_IMPORT_RETAIL_RESERVED_67",
		"CG_QL_IMPORT_RETAIL_RESERVED_68",
		"CG_QL_IMPORT_ADVERTISEMENTBRIDGE_RESERVED_69",
		"CG_QL_IMPORT_RETAIL_RESERVED_80",
		"CG_QL_IMPORT_RETAIL_RESERVED_112",
		"CG_QL_IMPORT_RETAIL_RESERVED_113",
		"CG_QL_IMPORT_RETAIL_RESERVED_117",
	):
		assert f"{reserved_slot}" in cgame_public
		assert f"ql_cgame_imports[{reserved_slot}] = (ql_import_f)QL_CG_trap_RetailReservedImport;" in import_block


def test_native_cgame_import_slab_alias_scan_has_direct_botlib_test_mentions() -> None:
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
		if not CGAME_NATIVE_SLAB_START <= address <= CGAME_NATIVE_SLAB_END:
			continue

		address_text = key[4:]
		if not any(
			form in botlib_test_text
			for form in (key, address_text, address_text.lower(), address_text.upper(), name)
		):
			missing.append(f"0x{address:08X} {key} {name}")

	assert missing == []
