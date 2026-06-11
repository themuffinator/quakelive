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
CGAME_FUNCTIONS_CSV = (
	REPO_ROOT
	/ "references"
	/ "reverse-engineering"
	/ "ghidra"
	/ "cgamex86"
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
CGAME_HLIL = (
	REPO_ROOT
	/ "references"
	/ "hlil"
	/ "quakelive"
	/ "cgamex86.dll"
	/ "cgamex86.dll_hlil.txt"
)
CLIENT_CL_CGAME = REPO_ROOT / "src" / "code" / "client" / "cl_cgame.c"
CLIENT_QL_CGAME_IMPORTS = REPO_ROOT / "src" / "code" / "client" / "ql_cgame_imports.inc"
CGAME_PUBLIC = REPO_ROOT / "src" / "code" / "cgame" / "cg_public.h"
CGAME_SYSCALLS = REPO_ROOT / "src" / "code" / "cgame" / "cg_syscalls.c"
CGAME_LOCAL = REPO_ROOT / "src" / "code" / "cgame" / "cg_local.h"
CGAME_MAIN = REPO_ROOT / "src" / "code" / "cgame" / "cg_main.c"

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

EXPECTED_NATIVE_SOUND_GHIDRA_ALIASES = {
	"4AFE10": "QLCGImport_S_StartSound",
	"4AFE20": "QLCGImport_S_StartSoundVolume",
	"4AFE50": "QLCGImport_S_StartLocalSoundVolume",
	"4AFE90": "QLCGImport_S_AddLoopingSound",
	"4AFEA0": "QLCGImport_S_UpdateEntityPosition",
	"4AFEB0": "QLCGImport_S_Respatialize",
	"4AFEC0": "QLCGImport_S_RegisterSound",
	"4AFED0": "QLCGImport_S_StartBackgroundTrack",
}

EXPECTED_NATIVE_SOUND_LOWERCASE_BN_ALIASES = {
	"sub_4afe10": "QLCGImport_S_StartSound",
	"sub_4afe20": "QLCGImport_S_StartSoundVolume",
	"sub_4afe50": "QLCGImport_S_StartLocalSoundVolume",
	"j_sub_4da490": "QLCGImport_S_ClearLoopingSoundsFrame",
	"j_sub_4da3e0": "QLCGImport_S_ClearLoopingSoundsKillAll",
	"sub_4afe90": "QLCGImport_S_AddLoopingSound",
	"sub_4afea0": "QLCGImport_S_UpdateEntityPosition",
	"sub_4afeb0": "QLCGImport_S_Respatialize",
	"sub_4afec0": "QLCGImport_S_RegisterSound",
	"sub_4afed0": "QLCGImport_S_StartBackgroundTrack",
}

EXPECTED_PC_SOURCE_HANDLE_GHIDRA_ALIASES = {
	"4B0270": "QLUIImport_PC_LoadSource",
	"4B0290": "QLUIImport_PC_FreeSource",
	"4B02B0": "QLUIImport_PC_ReadToken",
	"4B02D0": "QLUIImport_PC_SourceFileAndLine",
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
	("CG_QL_IMPORT_S_STARTLOCALSOUND", "QL_CG_trap_S_StartLocalSound"),
	("CG_QL_IMPORT_S_STARTLOCALSOUND_VOLUME", "QL_CG_trap_S_StartLocalSoundVolume"),
	("CG_QL_IMPORT_S_CLEARLOOPINGSOUNDS_FRAME", "QL_CG_trap_S_ClearLoopingSoundsFrame"),
	("CG_QL_IMPORT_S_CLEARLOOPINGSOUNDS_KILLALL", "QL_CG_trap_S_ClearLoopingSoundsKillAll"),
	("CG_QL_IMPORT_S_ADDLOOPINGSOUND", "QL_CG_trap_S_AddLoopingSound"),
	("CG_QL_IMPORT_S_UPDATEENTITYPOSITION", "QL_CG_trap_S_UpdateEntityPosition"),
	("CG_QL_IMPORT_S_RESPATIALIZE", "QL_CG_trap_S_Respatialize"),
	("CG_QL_IMPORT_S_REGISTERSOUND", "QL_CG_trap_S_RegisterSound"),
	("CG_QL_IMPORT_S_STARTBACKGROUNDTRACK", "QL_CG_trap_S_StartBackgroundTrack"),
	("CG_QL_IMPORT_S_STOPBACKGROUNDTRACK", "QL_CG_trap_S_StopBackgroundTrack"),
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
	("CG_QL_IMPORT_COMPAT_S_ADDREALLOOPINGSOUND", "QL_CG_trap_S_AddRealLoopingSound"),
	("CG_QL_IMPORT_COMPAT_S_STOPLOOPINGSOUND", "QL_CG_trap_S_StopLoopingSound"),
)


def _read(path: Path) -> str:
	return path.read_text(encoding="utf-8")


def _aliases() -> dict[str, str]:
	return json.loads(_read(SYMBOL_ALIASES))["quakelive_steam_srp"]


def _function_rows(path: Path = FUNCTIONS_CSV) -> dict[str, str]:
	rows: dict[str, str] = {}
	with path.open(newline="", encoding="utf-8") as functions:
		for row in csv.DictReader(functions):
			entry = row["entry"].upper()
			value = f'{row["name"]},{row["entry"]},{row["size"]},{row["thunk"]},{row["calling_convention"]}'
			rows[entry] = value
			rows[entry[2:]] = value
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


def _assert_order(source: str, *needles: str) -> None:
	cursor = 0
	for needle in needles:
		index = source.find(needle, cursor)
		if index == -1:
			raise AssertionError(f"expected ordered snippet not found after {cursor}: {needle}")
		cursor = index + len(needle)


def test_native_cgame_import_slab_aliases_and_rows_are_pinned() -> None:
	aliases = _aliases()
	rows = _function_rows()

	for address, (name, size) in EXPECTED_NATIVE_SLAB_ALIASES.items():
		assert aliases[f"sub_{address}"] == name
		if size is not None:
			assert rows[address] == f"FUN_00{address.lower()},00{address.lower()},{size},0,unknown"

	for address, name in EXPECTED_NATIVE_SOUND_GHIDRA_ALIASES.items():
		assert aliases[f"FUN_00{address.lower()}"] == name
		expected_size = EXPECTED_NATIVE_SLAB_ALIASES[address][1]
		assert rows[address] == f"FUN_00{address.lower()},00{address.lower()},{expected_size},0,unknown"

	for alias, name in EXPECTED_NATIVE_SOUND_LOWERCASE_BN_ALIASES.items():
		assert aliases[alias] == name

	for address, name in EXPECTED_PC_SOURCE_HANDLE_GHIDRA_ALIASES.items():
		assert aliases[f"FUN_00{address.lower()}"] == name
		expected_size = EXPECTED_NATIVE_SLAB_ALIASES[address][1]
		assert rows[address] == f"FUN_00{address.lower()},00{address.lower()},{expected_size},0,unknown"

	assert "4B0050" not in rows
	assert "4B0170" not in rows
	assert "4B0210" not in rows
	assert "4B02F0" not in rows
	assert "sub_4B02F0" not in aliases
	assert "QLCGImport_S_StopBackgroundTrack" not in aliases.values()

	for alias, name in {
		"sub_4BEFB0": "QLCGImport_S_StartLocalSound",
		"j_sub_4DA490": "QLCGImport_S_ClearLoopingSoundsFrame",
		"j_sub_4DA3E0": "QLCGImport_S_ClearLoopingSoundsKillAll",
	}.items():
		assert aliases[alias] == name


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
		"004afe70    int32_t* j_sub_4da490()",
		"004afe70  return sub_4da490() __tailcall",
		"004afe80    void j_sub_4da3e0()",
		"004afe80  return sub_4da3e0() __tailcall",
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
		"004b0290    int32_t sub_4b0290()",
		"004b02a0  jump(*(data_13e1844 + 0x208))",
		"004b02b0    int32_t sub_4b02b0()",
		"004b02c0  jump(*(data_13e1844 + 0x20c))",
		"004b02d0    int32_t sub_4b02d0()",
		"004b02df  jump(*(data_13e1844 + 0x210))",
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
		"005659f4  void* data_5659f4 = sub_4befb0",
		"005659fc  void* data_5659fc = j_sub_4da490",
		"00565a00  void* data_565a00 = j_sub_4da3e0",
		"00565a18  void* data_565a18 = 0x4b02f0",
		"00565a70  void* data_565a70 = sub_4bef40",
		"00565a98  void* data_565a98 = sub_4b00c0",
		"00565abc  void* data_565abc = sub_4b0170",
		"00565b08  void* data_565b08 = sub_4b0270",
		"00565b0c  void* data_565b0c = sub_4b0290",
		"00565b10  void* data_565b10 = sub_4b02b0",
		"00565b14  void* data_565b14 = sub_4b02d0",
		"00565b2c  void* data_565b2c = sub_4b0370",
		"0056749c  void* data_56749c = sub_4b0270",
		"005674a0  void* data_5674a0 = sub_4b0290",
		"005674a4  void* data_5674a4 = sub_4b02b0",
		"005674a8  void* data_5674a8 = sub_4b02d0",
	):
		assert table_anchor in table_hlil


def test_cgame_pc_source_handle_bridge_matches_botlib_precompiler_contract() -> None:
	aliases = _aliases()
	rows = _function_rows()
	cgame_rows = _function_rows(CGAME_FUNCTIONS_CSV)
	cl_cgame = _read(CLIENT_CL_CGAME)
	ql_cgame_imports = _read(CLIENT_QL_CGAME_IMPORTS)
	cgame_public = _read(CGAME_PUBLIC)
	cg_local = _read(CGAME_LOCAL)
	cg_syscalls = _read(CGAME_SYSCALLS)
	cg_main = _read(CGAME_MAIN)
	hlil = _read(QL_STEAM_HLIL_PART04)
	table_hlil = _read(QL_STEAM_HLIL_PART07)
	cgame_hlil = _read(CGAME_HLIL)

	import_block = _extract_function_block(cl_cgame, "static void CL_InitCGameImports")
	syscall_block = _extract_function_block(cl_cgame, "static int CL_CgameSystemCallsImpl")
	map_block = _extract_function_block(cg_syscalls, "static int CG_MapNativeImport")
	host_load = _extract_function_block(ql_cgame_imports, "static int QDECL QL_CG_trap_PC_LoadSource")
	host_free = _extract_function_block(ql_cgame_imports, "static int QDECL QL_CG_trap_PC_FreeSource")
	host_read = _extract_function_block(ql_cgame_imports, "static int QDECL QL_CG_trap_PC_ReadToken")
	host_line = _extract_function_block(
		ql_cgame_imports,
		"static int QDECL QL_CG_trap_PC_SourceFileAndLine",
	)
	cg_load = _extract_function_block(cg_syscalls, "int trap_PC_LoadSource")
	cg_free = _extract_function_block(cg_syscalls, "int trap_PC_FreeSource")
	cg_read = _extract_function_block(cg_syscalls, "int trap_PC_ReadToken")
	cg_line = _extract_function_block(cg_syscalls, "int trap_PC_SourceFileAndLine")
	menu_start = cg_main.find("void CG_ParseMenu")
	menu_end = cg_main.find("qboolean CG_Load_Menu", menu_start)
	assert menu_start != -1
	assert menu_end != -1
	menu_block = cg_main[menu_start:menu_end]

	for address, name in EXPECTED_PC_SOURCE_HANDLE_GHIDRA_ALIASES.items():
		assert aliases[f"sub_{address}"] == name
		assert aliases[f"FUN_00{address.lower()}"] == name
		assert rows[address] == (
			f"FUN_00{address.lower()},00{address.lower()},"
			f"{EXPECTED_NATIVE_SLAB_ALIASES[address][1]},0,unknown"
		)

	for expected in (
		"004b0270    int32_t sub_4b0270()",
		"004b0280  jump(*(data_13e1844 + 0x204))",
		"004b0290    int32_t sub_4b0290()",
		"004b02a0  jump(*(data_13e1844 + 0x208))",
		"004b02b0    int32_t sub_4b02b0()",
		"004b02c0  jump(*(data_13e1844 + 0x20c))",
		"004b02d0    int32_t sub_4b02d0()",
		"004b02df  jump(*(data_13e1844 + 0x210))",
	):
		assert expected in hlil

	_assert_order(
		table_hlil,
		"00565b08  void* data_565b08 = sub_4b0270",
		"00565b0c  void* data_565b0c = sub_4b0290",
		"00565b10  void* data_565b10 = sub_4b02b0",
		"00565b14  void* data_565b14 = sub_4b02d0",
	)
	_assert_order(
		table_hlil,
		"0056749c  void* data_56749c = sub_4b0270",
		"005674a0  void* data_5674a0 = sub_4b0290",
		"005674a4  void* data_5674a4 = sub_4b02b0",
		"005674a8  void* data_5674a8 = sub_4b02d0",
	)
	assert cgame_rows["10025AC0"] == "FUN_10025ac0,10025ac0,383,0,unknown"
	for expected in (
		"10025ac0    void sub_10025ac0(int32_t arg1)",
		"10025aec  int32_t edi = (*(data_1074cccc + 0x1b0))(arg1)",
		"10025b2e      if ((*(data_1074cccc + 0x1b8))(edi, &var_418) != 0)",
		"10025b54              if (sub_10057330(\"assetGlobalDef\", 0x1869f, &i) != 0)",
		"10025b81                  if (sub_10057330(\"menudef\", 0x1869f, &i) == 0)",
		"10025c22      (*(data_1074cccc + 0x1b4))(edi)",
		"10025b08      edi = (*(data_1074cccc + 0x1b0))(\"ui/testhud.menu\")",
	):
		assert expected in cgame_hlil
	_assert_order(
		cgame_public,
		"CG_QL_IMPORT_PC_ADD_GLOBAL_DEFINE = 107,",
		"CG_QL_IMPORT_PC_LOAD_SOURCE = 108,",
		"CG_QL_IMPORT_PC_FREE_SOURCE = 109,",
		"CG_QL_IMPORT_PC_READ_TOKEN = 110,",
		"CG_QL_IMPORT_PC_SOURCE_FILE_AND_LINE = 111,",
		"CG_QL_IMPORT_RETAIL_RESERVED_112 = 112,",
	)
	_assert_order(
		import_block,
		"ql_cgame_imports[CG_QL_IMPORT_PC_ADD_GLOBAL_DEFINE] = (ql_import_f)QL_CG_trap_PC_AddGlobalDefine;",
		"ql_cgame_imports[CG_QL_IMPORT_PC_LOAD_SOURCE] = (ql_import_f)QL_CG_trap_PC_LoadSource;",
		"ql_cgame_imports[CG_QL_IMPORT_PC_FREE_SOURCE] = (ql_import_f)QL_CG_trap_PC_FreeSource;",
		"ql_cgame_imports[CG_QL_IMPORT_PC_READ_TOKEN] = (ql_import_f)QL_CG_trap_PC_ReadToken;",
		"ql_cgame_imports[CG_QL_IMPORT_PC_SOURCE_FILE_AND_LINE] = (ql_import_f)QL_CG_trap_PC_SourceFileAndLine;",
		"ql_cgame_imports[CG_QL_IMPORT_RETAIL_RESERVED_112] = (ql_import_f)QL_CG_trap_RetailReservedImport;",
	)

	for expected in (
		"case CG_PC_LOAD_SOURCE: return CG_QL_IMPORT_PC_LOAD_SOURCE;",
		"case CG_PC_FREE_SOURCE: return CG_QL_IMPORT_PC_FREE_SOURCE;",
		"case CG_PC_READ_TOKEN: return CG_QL_IMPORT_PC_READ_TOKEN;",
		"case CG_PC_SOURCE_FILE_AND_LINE: return CG_QL_IMPORT_PC_SOURCE_FILE_AND_LINE;",
	):
		assert expected in map_block

	for expected in (
		"return botlib_export->PC_LoadSourceHandle( VMA(1) );",
		"return botlib_export->PC_FreeSourceHandle( args[1] );",
		"return botlib_export->PC_ReadTokenHandle( args[1], VMA(2) );",
		"return botlib_export->PC_SourceFileAndLine( args[1], VMA(2), VMA(3) );",
	):
		assert expected in syscall_block

	assert "return CG_Import_Syscall( CG_PC_LOAD_SOURCE, filename );" in host_load
	assert "return CG_Import_Syscall( CG_PC_FREE_SOURCE, handle );" in host_free
	assert "return CG_Import_Syscall( CG_PC_READ_TOKEN, handle, pc_token );" in host_read
	assert "return CG_Import_Syscall( CG_PC_SOURCE_FILE_AND_LINE, handle, filename, line );" in host_line

	assert "return syscall( CG_PC_LOAD_SOURCE, filename );" in cg_load
	assert "return syscall( CG_PC_FREE_SOURCE, handle );" in cg_free
	assert "return syscall( CG_PC_READ_TOKEN, handle, pc_token );" in cg_read
	assert "return syscall( CG_PC_SOURCE_FILE_AND_LINE, handle, filename, line );" in cg_line

	for expected in (
		"int\t\t\ttrap_PC_LoadSource( const char *filename );",
		"int\t\t\ttrap_PC_FreeSource( int handle );",
		"int\t\t\ttrap_PC_ReadToken( int handle, pc_token_t *pc_token );",
		"int\t\t\ttrap_PC_SourceFileAndLine( int handle, char *filename, int *line );",
	):
		assert expected in cg_local

	_assert_order(
		menu_block,
		"handle = trap_PC_LoadSource( menuFile );",
		"handle = trap_PC_LoadSource( \"ui/testhud.menu\" );",
		"if ( !trap_PC_ReadToken( handle, &token ) )",
		"if ( Q_stricmp( token.string, \"assetGlobalDef\" ) == 0 )",
		"if ( Q_stricmp( token.string, \"menudef\" ) == 0 )",
		"trap_PC_FreeSource( handle );",
	)


def test_native_cgame_sound_import_wiring_reconstructs_retail_clear_slots() -> None:
	cl_cgame = _read(CLIENT_CL_CGAME)
	cg_syscalls = _read(CGAME_SYSCALLS)

	frame_block = _extract_function_block(
		cl_cgame,
		"static void QDECL QL_CG_trap_S_ClearLoopingSoundsFrame( void )",
	)
	killall_block = _extract_function_block(
		cl_cgame,
		"static void QDECL QL_CG_trap_S_ClearLoopingSoundsKillAll( void )",
	)
	map_block = _extract_function_block(cg_syscalls, "static int CG_MapNativeImport")

	assert "S_ClearLoopingSoundsFrame();" in frame_block
	assert "S_ClearLoopingSounds( qfalse );" not in frame_block
	assert "S_ClearSoundBuffer();" in killall_block
	assert "S_ClearLoopingSounds( qtrue );" not in killall_block
	assert "case CG_S_STARTLOCALSOUND: return CG_QL_IMPORT_S_STARTLOCALSOUND;" in map_block
	assert "case CG_S_CLEARLOOPINGSOUNDS:" in map_block
	assert "return ( stack && stack[1] ) ? CG_QL_IMPORT_S_CLEARLOOPINGSOUNDS_KILLALL : CG_QL_IMPORT_S_CLEARLOOPINGSOUNDS_FRAME;" in map_block
	assert "case CG_S_STOPBACKGROUNDTRACK: return CG_QL_IMPORT_S_STOPBACKGROUNDTRACK;" in map_block
	assert "case CG_S_ADDREALLOOPINGSOUND: return CG_QL_IMPORT_COMPAT_S_ADDREALLOOPINGSOUND;" in map_block
	assert "case CG_S_STOPLOOPINGSOUND: return CG_QL_IMPORT_COMPAT_S_STOPLOOPINGSOUND;" in map_block


def test_native_cgame_sound_slab_keeps_volume_slots_direct_and_legacy_slots_fixed_volume() -> None:
	cl_cgame = _read(CLIENT_CL_CGAME)
	ql_cgame_imports = _read(CLIENT_QL_CGAME_IMPORTS)
	cgame_public = _read(CGAME_PUBLIC)
	cg_local = _read(CGAME_LOCAL)
	cg_syscalls = _read(CGAME_SYSCALLS)
	hlil = _read(QL_STEAM_HLIL_PART04)
	table_hlil = _read(QL_STEAM_HLIL_PART07)

	import_block = _extract_function_block(cl_cgame, "static void CL_InitCGameImports")
	syscall_block = _extract_function_block(cl_cgame, "static int CL_CgameSystemCallsImpl")
	map_block = _extract_function_block(cg_syscalls, "static int CG_MapNativeImport")
	native_start_volume_block = _extract_function_block(cg_syscalls, "void trap_QL_S_StartSoundVolume")
	native_local_volume_block = _extract_function_block(cg_syscalls, "void trap_QL_S_StartLocalSoundVolume")
	qvm_start_volume_block = _extract_function_block(cg_local, "static ID_INLINE void trap_QL_S_StartSoundVolume")
	qvm_local_volume_block = _extract_function_block(cg_local, "static ID_INLINE void trap_QL_S_StartLocalSoundVolume")
	host_start_volume_block = _extract_function_block(
		cl_cgame,
		"static void QDECL QL_CG_trap_S_StartSoundVolume",
	)
	host_local_volume_block = _extract_function_block(
		cl_cgame,
		"static void QDECL QL_CG_trap_S_StartLocalSoundVolume",
	)
	legacy_start_block = _extract_function_block(
		ql_cgame_imports,
		"static void QDECL QL_CG_trap_S_StartSound",
	)
	legacy_local_block = _extract_function_block(
		ql_cgame_imports,
		"static void QDECL QL_CG_trap_S_StartLocalSound",
	)

	_assert_order(
		table_hlil,
		"005659ec  void* data_5659ec = sub_4afe10",
		"005659f0  void* data_5659f0 = sub_4afe20",
		"005659f4  void* data_5659f4 = sub_4befb0",
		"005659f8  void* data_5659f8 = sub_4afe50",
		"005659fc  void* data_5659fc = j_sub_4da490",
		"00565a00  void* data_565a00 = j_sub_4da3e0",
		"00565a04  void* data_565a04 = sub_4afe90",
		"00565a08  void* data_565a08 = sub_4afea0",
		"00565a0c  void* data_565a0c = sub_4afeb0",
		"00565a10  void* data_565a10 = sub_4afec0",
		"00565a14  void* data_565a14 = sub_4afed0",
		"00565a18  void* data_565a18 = 0x4b02f0",
		"00565a1c  void* data_565a1c = sub_4afee0",
	)
	_assert_order(
		cgame_public,
		"CG_QL_IMPORT_S_STARTSOUND = 37,",
		"CG_QL_IMPORT_S_STARTSOUND_VOLUME = 38,",
		"CG_QL_IMPORT_S_STARTLOCALSOUND = 39,",
		"CG_QL_IMPORT_S_STARTLOCALSOUND_VOLUME = 40,",
		"CG_QL_IMPORT_S_CLEARLOOPINGSOUNDS_FRAME = 41,",
		"CG_QL_IMPORT_S_CLEARLOOPINGSOUNDS_KILLALL = 42,",
		"CG_QL_IMPORT_S_ADDLOOPINGSOUND = 43,",
		"CG_QL_IMPORT_S_UPDATEENTITYPOSITION = 44,",
		"CG_QL_IMPORT_S_RESPATIALIZE = 45,",
		"CG_QL_IMPORT_S_REGISTERSOUND = 46,",
		"CG_QL_IMPORT_S_STARTBACKGROUNDTRACK = 47,",
		"CG_QL_IMPORT_S_STOPBACKGROUNDTRACK = 48,",
	)
	_assert_order(
		cgame_public,
		"CG_S_STARTSOUND,",
		"CG_S_STARTLOCALSOUND,",
		"CG_S_CLEARLOOPINGSOUNDS,",
		"CG_S_ADDLOOPINGSOUND,",
		"CG_S_UPDATEENTITYPOSITION,",
		"CG_S_RESPATIALIZE,",
		"CG_S_REGISTERSOUND,",
		"CG_S_STARTBACKGROUNDTRACK,",
	)

	for expected in (
		"004afe10    int32_t sub_4afe10()",
		"004afe14  return sub_4da350() __tailcall",
		"004afe20    int32_t sub_4afe20(float* arg1, int32_t arg2, int32_t arg3, int32_t arg4, float arg5)",
		"004afe43  return sub_4da050(arg1, arg2, arg3, arg4, fconvert.s(fconvert.t(arg5)))",
		"004afe50    int32_t sub_4afe50(int32_t arg1, int32_t arg2, float arg3)",
		"004afe6b  return sub_4da380(arg1, arg2, fconvert.s(fconvert.t(arg3)))",
		"004afe70  return sub_4da490() __tailcall",
		"004afe80  return sub_4da3e0() __tailcall",
		"004afe94  return sub_4da4c0() __tailcall",
		"004afea4  return sub_4dac80() __tailcall",
		"004afeb4  return sub_4dacd0() __tailcall",
		"004afec4  return sub_4d9e50() __tailcall",
		"004afed4  return sub_4db060() __tailcall",
	):
		assert expected in hlil

	for expected in (
		"case CG_S_STARTSOUND: return CG_QL_IMPORT_S_STARTSOUND;",
		"case CG_S_STARTLOCALSOUND: return CG_QL_IMPORT_S_STARTLOCALSOUND;",
		"case CG_S_CLEARLOOPINGSOUNDS:",
		"return ( stack && stack[1] ) ? CG_QL_IMPORT_S_CLEARLOOPINGSOUNDS_KILLALL : CG_QL_IMPORT_S_CLEARLOOPINGSOUNDS_FRAME;",
		"case CG_S_ADDLOOPINGSOUND: return CG_QL_IMPORT_S_ADDLOOPINGSOUND;",
		"case CG_S_UPDATEENTITYPOSITION: return CG_QL_IMPORT_S_UPDATEENTITYPOSITION;",
		"case CG_S_RESPATIALIZE: return CG_QL_IMPORT_S_RESPATIALIZE;",
		"case CG_S_STARTBACKGROUNDTRACK: return CG_QL_IMPORT_S_STARTBACKGROUNDTRACK;",
		"case CG_S_STOPBACKGROUNDTRACK: return CG_QL_IMPORT_S_STOPBACKGROUNDTRACK;",
	):
		assert expected in map_block
	assert "CG_QL_IMPORT_S_STARTSOUND_VOLUME" not in map_block
	assert "CG_QL_IMPORT_S_STARTLOCALSOUND_VOLUME" not in map_block
	assert "CG_S_STARTSOUND_VOLUME" not in cgame_public
	assert "CG_S_STARTLOCALSOUND_VOLUME" not in cgame_public

	for expected in (
		"ql_cgame_imports[CG_QL_IMPORT_S_STARTSOUND] = (ql_import_f)QL_CG_trap_S_StartSound;",
		"ql_cgame_imports[CG_QL_IMPORT_S_STARTSOUND_VOLUME] = (ql_import_f)QL_CG_trap_S_StartSoundVolume;",
		"ql_cgame_imports[CG_QL_IMPORT_S_STARTLOCALSOUND] = (ql_import_f)QL_CG_trap_S_StartLocalSound;",
		"ql_cgame_imports[CG_QL_IMPORT_S_STARTLOCALSOUND_VOLUME] = (ql_import_f)QL_CG_trap_S_StartLocalSoundVolume;",
		"ql_cgame_imports[CG_QL_IMPORT_S_CLEARLOOPINGSOUNDS_FRAME] = (ql_import_f)QL_CG_trap_S_ClearLoopingSoundsFrame;",
		"ql_cgame_imports[CG_QL_IMPORT_S_CLEARLOOPINGSOUNDS_KILLALL] = (ql_import_f)QL_CG_trap_S_ClearLoopingSoundsKillAll;",
		"ql_cgame_imports[CG_QL_IMPORT_S_ADDLOOPINGSOUND] = (ql_import_f)QL_CG_trap_S_AddLoopingSound;",
		"ql_cgame_imports[CG_QL_IMPORT_S_UPDATEENTITYPOSITION] = (ql_import_f)QL_CG_trap_S_UpdateEntityPosition;",
		"ql_cgame_imports[CG_QL_IMPORT_S_RESPATIALIZE] = (ql_import_f)QL_CG_trap_S_Respatialize;",
		"ql_cgame_imports[CG_QL_IMPORT_S_REGISTERSOUND] = (ql_import_f)QL_CG_trap_S_RegisterSound;",
		"ql_cgame_imports[CG_QL_IMPORT_S_STARTBACKGROUNDTRACK] = (ql_import_f)QL_CG_trap_S_StartBackgroundTrack;",
		"ql_cgame_imports[CG_QL_IMPORT_S_STOPBACKGROUNDTRACK] = (ql_import_f)QL_CG_trap_S_StopBackgroundTrack;",
	):
		assert expected in import_block

	for expected in (
		"S_StartSound( VMA(1), args[2], args[3], args[4] );",
		"S_StartLocalSound( args[1], args[2] );",
		"S_ClearLoopingSounds( args[1] ? qtrue : qfalse );",
		"S_AddLoopingSound( args[1], VMA(2), VMA(3), args[4] );",
		"S_UpdateEntityPosition( args[1], VMA(2) );",
		"S_Respatialize( args[1], VMA(2), VMA(3), args[4] );",
		"S_StartBackgroundTrack( VMA(1), VMA(2) );",
		"S_StopBackgroundTrack();",
	):
		assert expected in syscall_block

	assert "S_StartSoundVolume( origin, entityNum, entchannel, sfx, volume );" in host_start_volume_block
	assert "S_StartLocalSoundVolume( sfx, channelNum, volume );" in host_local_volume_block
	assert "CG_Import_Syscall" not in host_start_volume_block
	assert "CG_Import_Syscall" not in host_local_volume_block

	assert "CG_GetNativeImportFunction( CG_QL_IMPORT_S_STARTSOUND_VOLUME );" in native_start_volume_block
	assert "((void (QDECL *)( vec3_t, int, int, sfxHandle_t, float ))import)( origin, entityNum, entchannel, sfx, volume );" in native_start_volume_block
	assert "CG_GetNativeImportFunction( CG_QL_IMPORT_S_STARTLOCALSOUND_VOLUME );" in native_local_volume_block
	assert "((void (QDECL *)( sfxHandle_t, int, float ))import)( sfx, channelNum, volume );" in native_local_volume_block
	assert "syscall(" not in native_start_volume_block
	assert "syscall(" not in native_local_volume_block
	assert "(void)volume;" not in native_start_volume_block
	assert "(void)volume;" not in native_local_volume_block

	assert "(void)volume;" in qvm_start_volume_block
	assert "trap_S_StartSound( origin, entityNum, entchannel, sfx );" in qvm_start_volume_block
	assert "(void)volume;" in qvm_local_volume_block
	assert "trap_S_StartLocalSound( sfx, channelNum );" in qvm_local_volume_block

	assert "CG_Import_Syscall( CG_S_STARTSOUND, origin, entityNum, entchannel, sfx );" in legacy_start_block
	assert "CG_Import_Syscall( CG_S_STARTLOCALSOUND, sfx, channelNum );" in legacy_local_block
	assert "S_StartSoundVolume" not in legacy_start_block
	assert "S_StartLocalSoundVolume" not in legacy_local_block


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
