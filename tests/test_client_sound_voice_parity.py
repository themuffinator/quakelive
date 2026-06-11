"""Guard the retail-backed client sound and Steam voice path against drift."""

from __future__ import annotations

import csv
import json
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parent.parent
ALIASES = REPO_ROOT / "references" / "analysis" / "quakelive_symbol_aliases.json"
FUNCTIONS_CSV = REPO_ROOT / "references" / "reverse-engineering" / "ghidra" / "quakelive_steam" / "functions.csv"
QL_STEAM_HLIL = REPO_ROOT / "references" / "hlil" / "quakelive" / "quakelive_steam.exe" / "quakelive_steam.exe_hlil.txt"
CL_CGAME = REPO_ROOT / "src" / "code" / "client" / "cl_cgame.c"
CL_MAIN = REPO_ROOT / "src" / "code" / "client" / "cl_main.c"
PLATFORM_STEAMWORKS = REPO_ROOT / "src" / "common" / "platform" / "platform_steamworks.c"
SND_DMA = REPO_ROOT / "src" / "code" / "client" / "snd_dma.c"
SND_LOCAL = REPO_ROOT / "src" / "code" / "client" / "snd_local.h"
SND_MEM = REPO_ROOT / "src" / "code" / "client" / "snd_mem.c"
SND_MIX = REPO_ROOT / "src" / "code" / "client" / "snd_mix.c"
SND_OGG_DECODE = REPO_ROOT / "src" / "code" / "client" / "snd_ogg_decode.c"
SND_OGG_STREAM = REPO_ROOT / "src" / "code" / "client" / "snd_ogg_stream.c"
SND_PUBLIC = REPO_ROOT / "src" / "code" / "client" / "snd_public.h"

# Retail console-command owner evidence for this sound slice comes from
# `references/analysis/quakelive_symbol_aliases.json` plus the paired HLIL in
# `references/hlil/quakelive/quakelive_steam.exe/`:
# `sub_4D9B60` -> `S_SoundInfo_f`
# `sub_4DAFD0` -> `S_SoundList_f`
# `sub_4DB710` -> `S_Play_f`
# `sub_4DB810` -> `S_Music_f`


SOUND_CONSOLE_ALIASES = {
	"sub_4D9B60": ("S_SoundInfo_f", "FUN_004d9b60", "237"),
	"sub_4DAFD0": ("S_SoundList_f", None, None),
	"sub_4DB710": ("S_Play_f", "FUN_004db710", "246"),
	"sub_4DB810": ("S_Music_f", None, None),
}

SOUND_CONSOLE_LOWERCASE_BN_ALIASES = {
	"sub_4d9b60": "S_SoundInfo_f",
	"sub_4dafd0": "S_SoundList_f",
	"sub_4db710": "S_Play_f",
	"sub_4db810": "S_Music_f",
}

SHARED_SOUND_HASH_ALIASES = {
	"sub_4D8990": ("generateHashValue", "FUN_004d8990", "75"),
}

SHARED_SOUND_HASH_LOWERCASE_BN_ALIASES = {
	"sub_4d8990": "generateHashValue",
}

SOUND_HELPER_ALIASES = {
	"sub_4D9B20": ("S_SoundFileTypeForPath", "FUN_004d9b20", "63"),
	"sub_4DAB00": ("S_AddVoiceSamples", "FUN_004dab00", "373"),
	"sub_4DB1C0": ("S_UpdateBackgroundTrack", "FUN_004db1c0", "347"),
	"sub_4DBB10": ("SND_free", "FUN_004dbb10", "31"),
	"sub_4DBB30": ("SND_setup", "FUN_004dbb30", "106"),
	"sub_4DBBA0": ("SND_shutdown", "FUN_004dbba0", "50"),
	"sub_4DBBE0": ("S_DisplayFreeMemory", "FUN_004dbbe0", "27"),
	"sub_4DBC00": ("ResampleSfx", "FUN_004dbc00", "245"),
	"sub_4DBD00": ("S_LoadSound", "FUN_004dbd00", "228"),
	"sub_4DC6A0": ("S_VorbisBufferRead", "FUN_004dc6a0", "62"),
	"sub_4DC6E0": ("S_VorbisBufferSeek", "FUN_004dc6e0", "61"),
	"sub_4DC720": ("S_VorbisBufferTell", "FUN_004dc720", "13"),
	"sub_4DC730": ("S_VorbisDecodeMemory", "FUN_004dc730", "490"),
	"sub_4DC920": ("S_LoadOggSound", "FUN_004dc920", "55"),
	"sub_4DC960": ("S_OggReadCallback", "FUN_004dc960", "31"),
	"sub_4DC980": ("S_OggCloseCallback", "FUN_004dc980", "21"),
	"sub_4DC9A0": ("S_OpenBackgroundOgg", "FUN_004dc9a0", "156"),
	"sub_4DCA40": ("S_CloseBackgroundOgg", "FUN_004dca40", "12"),
	"sub_4DCAD0": ("S_FindWavChunk", "FUN_004dcad0", "71"),
	"sub_4DCB20": ("GetWavinfo", "FUN_004dcb20", "326"),
	"sub_4DCC70": ("S_LoadWavSound", "FUN_004dcc70", "177"),
}

SOUND_HELPER_LOWERCASE_BN_ALIASES = {
	"sub_4d9b20": "S_SoundFileTypeForPath",
	"sub_4dab00": "S_AddVoiceSamples",
	"sub_4db1c0": "S_UpdateBackgroundTrack",
	"sub_4dbb10": "SND_free",
	"sub_4dbb30": "SND_setup",
	"sub_4dbba0": "SND_shutdown",
	"sub_4dbbe0": "S_DisplayFreeMemory",
	"sub_4dbc00": "ResampleSfx",
	"sub_4dbd00": "S_LoadSound",
	"sub_4dc6a0": "S_VorbisBufferRead",
	"sub_4dc6e0": "S_VorbisBufferSeek",
	"sub_4dc720": "S_VorbisBufferTell",
	"sub_4dc730": "S_VorbisDecodeMemory",
	"sub_4dc920": "S_LoadOggSound",
	"sub_4dc960": "S_OggReadCallback",
	"sub_4dc980": "S_OggCloseCallback",
	"sub_4dc9a0": "S_OpenBackgroundOgg",
	"sub_4dca40": "S_CloseBackgroundOgg",
	"sub_4dcad0": "S_FindWavChunk",
	"sub_4dcb20": "GetWavinfo",
	"sub_4dcc70": "S_LoadWavSound",
}

SOUND_REGISTRATION_ALIASES = {
	"sub_4D9D00": ("S_FindName", "FUN_004d9d00", "266"),
	"sub_4D9E10": ("S_memoryLoad", "FUN_004d9e10", "50"),
	"sub_4D9E50": ("S_RegisterSound", "FUN_004d9e50", "151"),
	"sub_4DB320": ("S_FreeOldestSound", "FUN_004db320", "126"),
	"sub_4DB3A0": ("S_BeginRegistration", "FUN_004db3a0", "78"),
}

SOUND_REGISTRATION_LOWERCASE_BN_ALIASES = {
	"sub_4d9d00": "S_FindName",
	"sub_4d9e10": "S_memoryLoad",
	"sub_4d9e50": "S_RegisterSound",
	"sub_4db320": "S_FreeOldestSound",
	"sub_4db3a0": "S_BeginRegistration",
}

SOUND_BACKGROUND_ALIASES = {
	"sub_4DB030": ("S_StopBackgroundTrack", "FUN_004db030", "35"),
	"sub_4DB060": ("S_StartBackgroundTrack", "FUN_004db060", "351"),
	"sub_4DB1C0": ("S_UpdateBackgroundTrack", "FUN_004db1c0", "347"),
	"sub_4DCA40": ("S_CloseBackgroundOgg", "FUN_004dca40", "12"),
	"sub_4DCA50": ("S_OggUpdateBackgroundTrack", "FUN_004dca50", "114"),
}

SOUND_BACKGROUND_LOWERCASE_BN_ALIASES = {
	"sub_4db030": "S_StopBackgroundTrack",
	"sub_4db060": "S_StartBackgroundTrack",
	"sub_4db1c0": "S_UpdateBackgroundTrack",
	"sub_4dc9a0": "S_OpenBackgroundOgg",
	"sub_4dca40": "S_CloseBackgroundOgg",
	"sub_4dca50": "S_OggUpdateBackgroundTrack",
}

SOUND_MIXER_ALIASES = {
	"sub_4DBDF0": ("S_TransferStereo16", "FUN_004dbdf0", "214"),
	"sub_4DBED0": ("S_TransferPaintBuffer", "FUN_004dbed0", "351"),
	"sub_4DC030": ("S_PaintChannelFrom16", "FUN_004dc030", "775"),
	"sub_4DC350": ("S_PaintChannels", "FUN_004dc350", "781"),
}

SOUND_MIXER_LOWERCASE_BN_ALIASES = {
	"sub_4dbdf0": "S_TransferStereo16",
	"sub_4dbed0": "S_TransferPaintBuffer",
	"sub_4dc030": "S_PaintChannelFrom16",
	"sub_4dc350": "S_PaintChannels",
}


def _extract_function_block(source: str, marker: str) -> str:
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


def _assert_order(text: str, *needles: str) -> None:
	cursor = -1
	for needle in needles:
		index = text.find(needle, cursor + 1)
		assert index != -1, f"missing ordered text: {needle}"
		cursor = index


def test_sound_helper_aliases_cover_retail_ogg_wav_voice_cluster() -> None:
	aliases = json.loads(ALIASES.read_text(encoding="utf-8"))["quakelive_steam_srp"]
	function_rows = {
		row["name"]: row
		for row in csv.DictReader(FUNCTIONS_CSV.read_text(encoding="utf-8").splitlines())
	}
	hlil = QL_STEAM_HLIL.read_text(encoding="utf-8")
	snd_dma = SND_DMA.read_text(encoding="utf-8")
	snd_mem = SND_MEM.read_text(encoding="utf-8")

	for alias, (name, ghidra_name, size) in SOUND_HELPER_ALIASES.items():
		assert aliases[alias] == name
		assert aliases[ghidra_name] == name
		assert function_rows[ghidra_name]["size"] == size

	for alias, name in SOUND_HELPER_LOWERCASE_BN_ALIASES.items():
		assert aliases[alias] == name

	for expected in (
		'004d9b20    int32_t sub_4d9b20(char* arg1)',
		'if (sub_4d9060(eax_1, ".ogg") == 0)',
		'004dab00    void sub_4dab00(int32_t arg1, int32_t arg2, int32_t arg3)',
		'void* ecx = &data_13e1860',
		'"client %d silenced: no voices le',
		'004db1c0    int32_t sub_4db1c0()',
		'sub_4dca50(&var_7538, esi_3)',
		'sub_4da840(divs.dp.d',
		'004dbba0    int32_t sub_4dbba0()',
		'data_12c5b8c = 0',
		'free(result)',
		'004dbd00    int32_t sub_4dbd00(int32_t* arg1)',
		'sub_4d9b20(&arg1[4])',
		'sub_4cf640(&arg1[4], &var_4c, 1)',
		'sub_4d9a60(&var_48, 0x40, ".ogg")',
		'result_1 = sub_4dc920(arg1, ecx_2, eax_4)',
		'result_1 = sub_4dcc70(arg1, ecx_2)',
		'sub_4cf320(ecx_2)',
		'004dc6a0    int32_t sub_4dc6a0(int32_t arg1, int32_t arg2, int32_t arg3, void* arg4)',
		'if (result u> eax - ecx - 1)',
		'memcpy(arg1, ecx, result)',
		'004dc6e0    int32_t sub_4dc6e0(int32_t* arg1, int32_t arg2, int32_t arg3)',
		'004dc720    int32_t sub_4dc720(int32_t* arg1)',
		'return arg1[1] - *arg1',
		'004dc730    int32_t __convention("regparm") sub_4dc730',
		'sub_4fda00(&var_2f4, &var_2d8, 0, 0, sub_4dc6a0, sub_4dc6e0, 0, sub_4dc720)',
		'004dc920    int32_t sub_4dc920(int32_t* arg1, int32_t arg2, int32_t arg3)',
		'result = sub_4dc730(sub_4d0010(eax, arg3, arg2), arg1, arg3, eax)',
		'004dc960    void* sub_4dc960(int32_t arg1, int32_t arg2, int32_t arg3, int32_t* arg4)',
		'return sub_4d0010(arg1, arg2 * arg3, *arg4)',
		'004dc980    int32_t sub_4dc980(int32_t* arg1)',
		'sub_4cf320(*arg1)',
		'004dc9a0    int32_t sub_4dc9a0(int32_t* arg1)',
		'sub_4fda00(&data_12c5b74, &data_12cdbb0, 0, 0, sub_4dc960, 0, sub_4dc980, 0)',
		'004dca40    int32_t sub_4dca40()',
		'sub_4fcde0(&data_12cdbb0)',
		'004dcad0    int32_t sub_4dcad0(int32_t arg1 @ esi, int32_t* arg2)',
		'004dcb20    int32_t __convention("regparm") sub_4dcb20(int32_t arg1, int32_t* arg2 @ edi)',
		'var_c == 0x46464952',
		'var_c == 0x45564157',
		'var_8 == 0x20746d66',
		'004dcc70    int32_t sub_4dcc70(int32_t* arg1, int32_t arg2)',
		'"%s is not a mono wav file"',
		'"WAV_Load: %s is not a 16-bit fil',
		'"WAV_Load: %s is not a 22kHz file',
	):
		assert expected in hlil

	for expected in (
		"SFT_UNKNOWN = 0",
		"SFT_WAV = 1",
		"SFT_OGG = 2",
		"static soundFileType_t S_SoundFileTypeForPath",
		'if ( !Q_stricmp( dot, ".ogg" ) ) {',
		'if ( !Q_stricmp( dot, ".wav" ) ) {',
		"static int S_FindWavChunk( fileHandle_t file, const char *chunk )",
		"return FS_Read( dest, count, file );",
		"if ( S_ReadWavBytes( file, name, sizeof( name ) ) != sizeof( name ) ) {",
		"return ( len + 1 ) & ~1;",
		"static qboolean S_LoadOggSound",
		"static qboolean S_LoadWavSound",
		"static qboolean S_LoadPCMSound",
	):
		assert expected in snd_mem

	assert "static void FindNextChunk" not in snd_mem
	assert "static void FindChunk" not in snd_mem
	assert "static int S_FindWavChunk" not in snd_dma
	assert "FGetLittleShort" not in snd_dma
	assert "FGetLittleLong" not in snd_dma
	for legacy_parser_message in (
		"Missing RIFF/WAVE chunks",
		"Missing fmt chunk",
		"Microsoft PCM format only",
		"Missing data chunk",
	):
		assert legacy_parser_message not in hlil
		assert legacy_parser_message not in snd_mem


def test_sound_registration_cache_helpers_match_retail_diagnostics_and_reset_path() -> None:
	aliases = json.loads(ALIASES.read_text(encoding="utf-8"))["quakelive_steam_srp"]
	function_rows = {
		row["name"]: row
		for row in csv.DictReader(FUNCTIONS_CSV.read_text(encoding="utf-8").splitlines())
	}
	hlil = QL_STEAM_HLIL.read_text(encoding="utf-8")
	snd_dma = SND_DMA.read_text(encoding="utf-8")

	hash_block = _extract_function_block(snd_dma, "static long S_HashSFXName")
	find_block = _extract_function_block(snd_dma, "static sfx_t *S_FindName")
	register_block = _extract_function_block(snd_dma, "sfxHandle_t\tS_RegisterSound")
	memory_load_block = _extract_function_block(snd_dma, "void S_memoryLoad")
	begin_block = _extract_function_block(snd_dma, "void S_BeginRegistration( void )")
	free_oldest_block = _extract_function_block(snd_dma, "void S_FreeOldestSound")

	for alias, (name, ghidra_name, size) in SHARED_SOUND_HASH_ALIASES.items():
		assert aliases[alias] == name
		assert aliases[ghidra_name] == name
		assert function_rows[ghidra_name]["size"] == size

	for alias, name in SHARED_SOUND_HASH_LOWERCASE_BN_ALIASES.items():
		assert aliases[alias] == name

	for alias, (name, ghidra_name, size) in SOUND_REGISTRATION_ALIASES.items():
		assert aliases[alias] == name
		assert aliases[ghidra_name] == name
		assert function_rows[ghidra_name]["size"] == size

	for alias, name in SOUND_REGISTRATION_LOWERCASE_BN_ALIASES.items():
		assert aliases[alias] == name

	for expected in (
		"004d8990    int32_t sub_4d8990(char* arg1, int32_t arg2)",
		"004d8998  int32_t ebx = 0",
		"004d89aa          int32_t eax_2 = tolower(sx.d(*esi))",
		"004d89b6          if (eax_2 == 0x2e)",
		"004d89bb          if (eax_2 == 0x5c)",
		"004d89bd              eax_2 = 0x2f",
		"004d89c5          int32_t ecx_2 = (edi_1 + esi) * eax_2",
		"004d89da  return (arg2 - 1) & ebx",
		"004d9d00    char* sub_4d9d00(char* arg1 @ edi)",
		'sub_4c9b60(arg1, "S_FindName: NULL")',
		'sub_4c9b60(0, "S_FindName: empty name")',
		'sub_4c9b60(0, "S_FindName: name too long: %s")',
		"004d9d56  int32_t eax_2 = sub_4d8990(arg1, 0x80)",
		"004d9e10    int32_t sub_4d9e10(int32_t* arg1 @ esi)",
		'char const data_543f98[0x24] = "^3WARNING: couldn\\\'t load sound: %s\\n", 0',
		"004d9e50    int32_t sub_4d9e50(char* arg1)",
		'char const data_543fbc[0x2e] = "^3WARNING: could not find %s - using default\\n", 0',
		"004db320    int32_t* sub_4db320()",
		'char const data_544350[0x25] = "S_FreeOldestSound: freeing sound %s\\n", 0',
		"004db3a0    int32_t sub_4db3a0()",
		'004db3ed  return sub_4d9e50("sound/feedback/hit.wav")',
	):
		assert expected in hlil

	assert "#define\t\tLOOP_HASH\t\t128" in snd_dma
	assert "static\tsfx_t\t\t*sfxHash[LOOP_HASH];" in snd_dma

	for expected in (
		"hash = 0;",
		"i = 0;",
		"while (name[i] != '\\0') {",
		"letter = tolower(name[i]);",
		"if (letter =='.') break;",
		"if (letter =='\\\\') letter = '/';",
		"hash+=(long)(letter)*(i+119);",
		"hash &= (LOOP_HASH-1);",
		"return hash;",
	):
		assert expected in hash_block

	for expected in (
		'Com_Error (ERR_FATAL, "S_FindName: NULL");',
		'Com_Error (ERR_FATAL, "S_FindName: empty name");',
		'Com_Error (ERR_FATAL, "S_FindName: name too long: %s", name);',
		"hash = S_HashSFXName(name);",
		"sfx = sfxHash[hash];",
		"sfx = sfx->next;",
		"if (s_numSfx == MAX_SFX) {",
		'Com_Error (ERR_FATAL, "S_FindName: out of sfx_t");',
		"sfx->next = sfxHash[hash];",
		"sfxHash[hash] = sfx;",
	):
		assert expected in find_block

	assert '"Sound name too long: %s"' not in find_block
	assert '"S_FindName: NULL\\n"' not in find_block
	assert '"S_FindName: empty name\\n"' not in find_block

	for expected in (
		"compressed = qfalse;",
		'Com_Printf( "Sound name exceeds MAX_QPATH\\n" );',
		"sfx = S_FindName( name );",
		"S_memoryLoad(sfx);",
		'Com_Printf( S_COLOR_YELLOW "WARNING: could not find %s - using default\\n", sfx->soundName );',
		"return sfx - s_knownSfx;",
	):
		assert expected in register_block

	assert 'Com_Printf( S_COLOR_YELLOW "WARNING: couldn\'t load sound: %s\\n", sfx->soundName );' in memory_load_block
	assert "sfx->defaultSound = qtrue;" in memory_load_block
	assert "sfx->inMemory = qtrue;" in memory_load_block
	assert "//\t\tCom_Printf( S_COLOR_YELLOW \"WARNING: couldn't load sound" not in memory_load_block

	for expected in (
		"SND_shutdown();",
		"SND_setup();",
		"s_numSfx = 0;",
		"Com_Memset( s_knownSfx, 0, sizeof( s_knownSfx ) );",
		"Com_Memset(sfxHash, 0, sizeof(sfx_t *)*LOOP_HASH);",
		'S_RegisterSound("sound/feedback/hit.wav", qfalse);',
	):
		assert expected in begin_block

	for expected in (
		"oldest = Com_Milliseconds();",
		"for (i=1 ; i < s_numSfx ; i++) {",
		'Com_DPrintf("S_FreeOldestSound: freeing sound %s\\n", sfx->soundName);',
		"SND_free(buffer);",
		"sfx->inMemory = qfalse;",
		"sfx->soundData = NULL;",
	):
		assert expected in free_oldest_block


def test_sound_console_commands_match_retail_registration_and_output_contracts() -> None:
	aliases = json.loads(ALIASES.read_text(encoding="utf-8"))["quakelive_steam_srp"]
	function_rows = {
		row["name"]: row
		for row in csv.DictReader(FUNCTIONS_CSV.read_text(encoding="utf-8").splitlines())
	}
	hlil = QL_STEAM_HLIL.read_text(encoding="utf-8")
	snd_dma = SND_DMA.read_text(encoding="utf-8")

	init_block = _extract_function_block(snd_dma, "void S_Init( void ) {")
	shutdown_block = _extract_function_block(snd_dma, "void S_Shutdown( void )")
	info_block = _extract_function_block(snd_dma, "void S_SoundInfo_f(void) {")
	play_block = _extract_function_block(snd_dma, "void S_Play_f( void ) {")
	music_block = _extract_function_block(snd_dma, "void S_Music_f( void ) {")
	list_block = _extract_function_block(snd_dma, "void S_SoundList_f( void ) {")

	for alias, (name, ghidra_name, size) in SOUND_CONSOLE_ALIASES.items():
		assert aliases[alias] == name
		if ghidra_name is not None:
			assert aliases[ghidra_name] == name
			assert function_rows[ghidra_name]["size"] == size

	for alias, name in SOUND_CONSOLE_LOWERCASE_BN_ALIASES.items():
		assert aliases[alias] == name

	for expected in (
		"004d9b60    int32_t sub_4d9b60()",
		'sub_4c9860(esi, "----- Sound Info -----\\n")',
		'sub_4c9860(esi, "sound system not started\\n")',
		'sub_4c9860(esi, "sound system is muted\\n")',
		'sub_4c9860(esi, "%5d stereo\\n")',
		'sub_4c9860(esi, "Background file: %s\\n")',
		'sub_4c9860(esi, "No background file.\\n")',
		'sub_4c9860(esi, "----------------------\\n")',
		"004dafd0    int32_t sub_4dafd0()",
		"void* const eax = &data_5442c4",
		"if (*(esi_1 - 8) == 0)",
		"eax = &data_5442c0",
		'sub_4c9860(esi_1, "%6i [%s] : %s\\n")',
		'char const data_54429c[0x12] = "%i sounds loaded\\n", 0',
		'char const data_5442b0[0xf] = "%6i [%s] : %s\\n", 0',
		"005442c0  50 47 44 00",
		"PGD.",
		"005442c4              4d 45 4d 00",
		"MEM.",
		"004db022  return sub_4dbbe0() __tailcall",
		"004db710    int32_t sub_4db710()",
		"result = sub_4c7ed0()",
		"if (sub_4d8f10(sub_4c7ee0(esi), 0x2e) != 0)",
		"int32_t var_114_3 = sub_4c7ee0(1)",
		'sub_4d9160(&var_108, 0x100, "%s.wav")',
		"eax_6, ecx_1 = sub_4d9e50(&var_108)",
		"sub_4da050(nullptr, data_1260948, 6, eax_6, fconvert.s(float.t(1)))",
		"004db810    int32_t sub_4db810()",
		"if (eax_6 == 2)",
		"int32_t result = sub_4db060(sub_4c7ee0(1), eax)",
		"data_12608d0 = 0",
		'return sub_4c9860(esi, "music <musicfile> [loopfile]\\n")',
		"return sub_4db060(sub_4c7ee0(1), eax_2)",
		'004dba07  sub_4c81d0("play", sub_4db710)',
		'004dba16  sub_4c81d0("music", sub_4db810)',
		'004dba25  sub_4c81d0("s_list", sub_4dafd0)',
		'004dba34  sub_4c81d0("s_info", sub_4d9b60)',
		'004dba43  sub_4c81d0("s_stop", sub_4db450)',
	):
		assert expected in hlil

	assert 'Cmd_AddCommand("play", S_Play_f);' in init_block
	assert 'Cmd_AddCommand("music", S_Music_f);' in init_block
	assert 'Cmd_AddCommand("s_list", S_SoundList_f);' in init_block
	assert 'Cmd_AddCommand("s_info", S_SoundInfo_f);' in init_block
	assert 'Cmd_AddCommand("s_stop", S_StopAllSounds);' in init_block

	assert 'Cmd_RemoveCommand("play");' in shutdown_block
	assert 'Cmd_RemoveCommand("music");' in shutdown_block
	assert 'Cmd_RemoveCommand("s_list");' in shutdown_block
	assert 'Cmd_RemoveCommand("s_info");' in shutdown_block
	assert 'Cmd_RemoveCommand("s_stop");' in shutdown_block

	assert 'Com_Printf("----- Sound Info -----\\n" );' in info_block
	assert 'Com_Printf ("sound system not started\\n");' in info_block
	assert 'Com_Printf ("sound system is muted\\n");' in info_block
	assert 'Com_Printf("%5d stereo\\n", dma.channels - 1);' in info_block
	assert 'Com_Printf("%5d samples\\n", dma.samples);' in info_block
	assert 'Com_Printf("%5d samplebits\\n", dma.samplebits);' in info_block
	assert 'Com_Printf("%5d submission_chunk\\n", dma.submission_chunk);' in info_block
	assert 'Com_Printf("%5d speed\\n", dma.speed);' in info_block
	assert 'Com_Printf("0x%x dma buffer\\n", dma.buffer);' in info_block
	assert "if ( s_backgroundFile || S_OggStreamActive( &s_backgroundOgg ) ) {" in info_block
	assert 'Com_Printf("Background file: %s\\n", s_backgroundLoop );' in info_block
	assert 'Com_Printf("No background file.\\n" );' in info_block
	assert 'Com_Printf("----------------------\\n" );' in info_block

	assert "while ( i<Cmd_Argc() ) {" in play_block
	assert "if ( !Q_strrchr(Cmd_Argv(i), '.') ) {" in play_block
	assert 'Com_sprintf( name, sizeof(name), "%s.wav", Cmd_Argv(1) );' in play_block
	assert "h = S_RegisterSound( name, qfalse );" in play_block
	assert "S_StartLocalSound( h, CHAN_LOCAL_SOUND );" in play_block

	assert "if ( c == 2 ) {" in music_block
	assert "S_StartBackgroundTrack( Cmd_Argv(1), Cmd_Argv(1) );" in music_block
	assert "s_backgroundLoop[0] = 0;" in music_block
	assert 'Com_Printf ("music <musicfile> [loopfile]\\n");' in music_block

	assert 'location = sfx->inMemory ? "MEM" : "PGD";' in list_block
	assert 'Com_Printf( "%6i [%s] : %s\\n", size, location, sfx->soundName );' in list_block
	assert 'Com_Printf( "%i sounds loaded\\n", s_numSfx );' in list_block
	assert "S_DisplayFreeMemory();" in list_block
	assert 'Total resident: %i\\n' not in list_block
	assert '%6i[%s] : %s[%s]\\n' not in list_block


def test_volume_aware_sound_imports_route_to_engine_helpers() -> None:
	cl_cgame = CL_CGAME.read_text(encoding="utf-8")
	snd_public = SND_PUBLIC.read_text(encoding="utf-8")

	start_block = _extract_function_block(
		cl_cgame,
		"static void QDECL QL_CG_trap_S_StartSoundVolume( vec3_t origin, int entityNum, int entchannel, sfxHandle_t sfx, float volume )",
	)
	local_block = _extract_function_block(
		cl_cgame,
		"static void QDECL QL_CG_trap_S_StartLocalSoundVolume( sfxHandle_t sfx, int channelNum, float volume )",
	)

	assert "void S_StartSoundVolume( vec3_t origin, int entnum, int entchannel, sfxHandle_t sfx, float volume );" in snd_public
	assert "void S_StartLocalSoundVolume( sfxHandle_t sfx, int channelNum, float volume );" in snd_public
	assert "S_StartSoundVolume( origin, entityNum, entchannel, sfx, volume );" in start_block
	assert "S_StartLocalSoundVolume( sfx, channelNum, volume );" in local_block
	assert "(void)volume;" not in start_block
	assert "(void)volume;" not in local_block


def test_voice_mixer_reconstructs_retail_lane_shape_and_cvars() -> None:
	hlil = QL_STEAM_HLIL.read_text(encoding="utf-8")
	snd_local = SND_LOCAL.read_text(encoding="utf-8")
	snd_dma = SND_DMA.read_text(encoding="utf-8")
	snd_mix = SND_MIX.read_text(encoding="utf-8")
	add_voice_block = _extract_function_block(
		snd_dma,
		"void S_AddVoiceSamples( int clientNum, int samples, const short *data )",
	)

	for expected in (
		"004dab00    void sub_4dab00(int32_t arg1, int32_t arg2, int32_t arg3)",
		"004dab4c      long double x87_r7_2 = float.t(data_142c324) * fconvert.t(0.5)",
		'004dab84              sub_4c9ab0("client %d: using voice %d\\n")',
		'004dab97      sub_4c9ab0("client %d silenced: no voices le…")',
		'004dabed      sub_4c9ab0("voice channel %d: start samples …")',
		'004dac0a      sub_4c9ab0("voice channel %d: %d samples alr…")',
		'004dac2b      sub_4c9ab0("voice channel %d: overflow %d vo…")',
		'004dac41  sub_4c9ab0("voice channel %d: add %d samples…")',
		"004dc3b3              if (esi_1 != 0)",
		"004dc3bc                  long double temp2_1 = fconvert.t(*(data_13e1854 + 0x2c))",
		'004dc3cb                      sub_4c9ab0("background sound underrun\\n")',
		"004dc3e9              sub_4c95e0(&data_12c5ba0, 0, (ebx - edi) * 8)",
		'char const data_5445c8[0x1b] = "background sound underrun\\n", 0',
		'char const data_544158[0x32] = "voice channel %d: add %d samples to voice buffer\\n", 0',
		'char const data_544190[0x43] = "voice channel %d: overflow %d voice samples with room for only %d\\n", 0',
		'char const data_5441d4[0x30] = "voice channel %d: %d samples already in buffer\\n", 0',
		'char const data_544204[0x2c] = "voice channel %d: start samples at time %d\\n", 0',
		'char const data_544230[0x24] = "client %d silenced: no voices left\\n", 0',
		'char const data_544254[0x1b] = "client %d: using voice %d\\n", 0',
		'004dc562                          sub_4c9ab0("voice channel %d: no data in the…")',
		'004dc507                              sub_4c9ab0("voice channel %d: consumed all b…")',
		'char const data_544560[0x2f] = "voice channel %d: no data in the paint window\\n", 0',
		'char const data_544590[0x37] = "voice channel %d: consumed all buffered voice samples\\n", 0',
	):
		assert expected in hlil

	assert "#define MAX_VOICE_CHANNELS\t5" in snd_local
	assert "#define VOICE_BUFFER_SAMPLES\t0x4000" in snd_local
	assert "typedef struct {" in snd_local
	assert "short\tsamples[VOICE_BUFFER_SAMPLES];" in snd_local
	assert "voiceChannel_t\ts_voiceChannels[MAX_VOICE_CHANNELS];" in snd_dma
	assert "extern cvar_t\t*s_musicVolume;" in snd_local
	assert 's_pvs = Cvar_GetBounded( "s_pvs", "0", "0", "1", CVAR_ARCHIVE | CVAR_PROTECTED | CVAR_VM_CREATED | CVAR_CLOUD );' in snd_dma
	assert 's_voiceStep = Cvar_Get( "s_voiceStep", "0.02", CVAR_ARCHIVE | CVAR_PROTECTED );' in snd_dma
	assert "Com_Memset( s_voiceChannels, 0, sizeof( s_voiceChannels ) );" in snd_dma
	_assert_order(
		add_voice_block,
		"channelIndex = -1;",
		"for ( i = 0; i < MAX_VOICE_CHANNELS; ++i ) {",
		"if ( s_voiceChannels[i].clientNum == clientNum ) {",
	)
	assert "if ( !s_soundStarted || s_soundMuted || !data || samples <= 0 )" not in add_voice_block
	assert "s_paintedtime - s_voiceChannels[i].endSample > (int)( dma.samples * 0.5f )" in add_voice_block
	assert 'Com_DPrintf( "client %d: using voice %d\\n", clientNum, channelIndex );' in add_voice_block
	assert 'Com_DPrintf( "client %d silenced: no voices left\\n", clientNum );' in add_voice_block
	assert "if ( voice->endSample <= voice->startSample ) {" in add_voice_block
	assert "startSample = s_paintedtime + (int)( s_mixPreStep->value * dma.speed );" in add_voice_block
	assert "startSample += (int)( s_voiceStep->value * dma.speed );" in add_voice_block
	assert 'Com_DPrintf( "voice channel %d: start samples at time %d\\n", channelIndex, startSample );' in add_voice_block
	assert 'Com_DPrintf( "voice channel %d: %d samples already in buffer\\n", channelIndex, queuedSamples );' in add_voice_block
	assert 'Com_DPrintf( "voice channel %d: overflow %d voice samples with room for only %d\\n", channelIndex, samples, room );' in add_voice_block
	assert 'Com_DPrintf( "voice channel %d: add %d samples to voice buffer\\n", channelIndex, count );' in add_voice_block
	assert "voice->samples[( voice->endSample + i ) & ( VOICE_BUFFER_SAMPLES - 1 )] = data[i];" in add_voice_block
	assert "s_voiceChannels[i].endSample <= s_paintedtime" not in add_voice_block
	assert "s_voiceChannels[i].endSample - s_paintedtime < (int)( dma.speed * 0.5f )" not in add_voice_block
	assert "voiceScale = (int)( Com_Clamp( 0.0f, 2.0f, s_voiceVolume->value ) * 256.0f );" in snd_mix
	assert "voice->samples[sampleTime & ( VOICE_BUFFER_SAMPLES - 1 )] * voiceScale" in snd_mix
	assert "if ( s_musicVolume && s_musicVolume->value > 0.0f ) {" in snd_mix
	assert 'Com_DPrintf( "background sound underrun\\n" );' in snd_mix
	assert 'Com_DPrintf( "voice channel %d: no data in the paint window\\n", voiceIndex );' in snd_mix
	assert 'Com_DPrintf( "voice channel %d: consumed all buffered voice samples\\n", voiceIndex );' in snd_mix
	assert "if ( s_pvs && s_pvs->integer && !S_OriginInPVS( listener_origin, origin ) ) {" in snd_dma


def test_sound_mixer_paint_channels_preserves_retail_stage_order_and_transfer_helpers() -> None:
	aliases = json.loads(ALIASES.read_text(encoding="utf-8"))["quakelive_steam_srp"]
	function_rows = {
		row["name"]: row
		for row in csv.DictReader(FUNCTIONS_CSV.read_text(encoding="utf-8").splitlines())
	}
	hlil = QL_STEAM_HLIL.read_text(encoding="utf-8")
	snd_mix = SND_MIX.read_text(encoding="utf-8")

	stereo_block = _extract_function_block(snd_mix, "void S_TransferStereo16")
	transfer_block = _extract_function_block(snd_mix, "void S_TransferPaintBuffer")
	paint16_block = _extract_function_block(snd_mix, "static void S_PaintChannelFrom16")
	paint_block = _extract_function_block(snd_mix, "void S_PaintChannels( int endtime )")
	dynamic_block = paint_block[
		paint_block.index("// paint in the channels."):paint_block.index("// paint in the looped channels.")
	]
	loop_block = paint_block[
		paint_block.index("// paint in the looped channels."):paint_block.index("// transfer out according to DMA format")
	]

	for alias, (name, ghidra_name, size) in SOUND_MIXER_ALIASES.items():
		assert aliases[alias] == name
		assert aliases[ghidra_name] == name
		assert function_rows[ghidra_name]["size"] == size

	for alias, name in SOUND_MIXER_LOWERCASE_BN_ALIASES.items():
		assert aliases[alias] == name

	_assert_order(
		hlil,
		"004dbdf0    void sub_4dbdf0(int32_t arg1, int32_t arg2)",
		"004dbed0    char* __convention(\"regparm\") sub_4dbed0(int32_t arg1)",
		"004dc030    void sub_4dc030(void* arg1, int32_t* arg2, int32_t arg3, int32_t arg4, int32_t arg5)",
		"004dc350    int32_t sub_4dc350(void* arg1)",
	)

	for expected in (
		"004dc366  int32_t result = sub_526000(fconvert.t(*(data_13e185c + 0x2c)) * fconvert.t(255.0))",
		"004dc39a          if (ebx - edi s> 0x1000)",
		"004dc412                      void* eax_3 = ecx_3 & 0x3fff",
		"004dc425                      *edx_4 = *((eax_3 << 3) + &data_14098a0)",
		'004dc3cb                      sub_4c9ab0("background sound underrun\\n")',
		"004dc3e9              sub_4c95e0(&data_12c5ba0, 0, (ebx - edi) * 8)",
		"004dc46a          long double temp3_1 = fconvert.t(*(data_14298a0 + 0x2c))",
		"004dc47d              void* ebx_6 = &data_13e1864",
		"004dc4e2                                  sx.d(*(ebx_6 + ((esi_2 & 0x3fff) << 1) + 8)) * eax_7",
		"004dc4e6                              *(ecx_6 - 4) += edx_13",
		"004dc4e9                              *ecx_6 += edx_13",
		"004dc522              while (i_1 s< 5)",
		"004dc528          void* esi_3 = &data_14298e8",
		"004dc52d          int32_t i_8 = 0x60",
		"004dc5a0                          st0, eax_6 = sub_4dc030(esi_3 - 0x28, ebx_7, eax_6, ecx_8, 0)",
		"004dc5c8          if (data_142c2f0 s> 0)",
		"004dc5ce              void* eax_9 = &data_142ae08",
		"004dc5f9                              int32_t temp1_1 = mods.dp.d(sx.q(edi), ecx_10)",
		"004dc622                                  st0 = sub_4dc030(var_c_1 - 0x28, ebx_8, esi_5, temp1_1,",
		"004dc654          result = sub_4dbed0(var_8_1)",
		"004dc659          data_142c2ec = var_8_1",
		'char const data_544560[0x2f] = "voice channel %d: no data in the paint window\\n", 0',
		'char const data_544590[0x37] = "voice channel %d: consumed all buffered voice samples\\n", 0',
		'char const data_5445c8[0x1b] = "background sound underrun\\n", 0',
	):
		assert expected in hlil

	_assert_order(
		hlil,
		"004dc350    int32_t sub_4dc350(void* arg1)",
		"004dc3af          if (esi_1 s>= edi)",
		"004dc46a          long double temp3_1 = fconvert.t(*(data_14298a0 + 0x2c))",
		"004dc528          void* esi_3 = &data_14298e8",
		"004dc5c8          if (data_142c2f0 s> 0)",
		"004dc654          result = sub_4dbed0(var_8_1)",
		"004dc659          data_142c2ec = var_8_1",
	)

	for expected in (
		"lpos = ls_paintedtime & ((dma.samples>>1)-1);",
		"snd_out = (short *) pbuf + (lpos<<1);",
		"snd_linear_count = (dma.samples>>1) - lpos;",
		"if (ls_paintedtime + snd_linear_count > endtime)",
		"snd_linear_count = endtime - ls_paintedtime;",
		"S_WriteLinearBlastStereo16 ();",
	):
		assert expected in stereo_block

	for expected in (
		"if ( s_testsound->integer ) {",
		"count = (endtime - s_paintedtime);",
		"if (dma.samplebits == 16 && dma.channels == 2)",
		"S_TransferStereo16 (pbuf, endtime);",
		"count = (endtime - s_paintedtime) * dma.channels;",
		"out_mask = dma.samples - 1;",
		"out_idx = s_paintedtime * dma.channels & out_mask;",
		"step = 3 - dma.channels;",
		"if (dma.samplebits == 16)",
		"else if (dma.samplebits == 8)",
	):
		assert expected in transfer_block

	for expected in (
		"if (ch->doppler) {",
		"sampleOffset = sampleOffset*ch->oldDopplerScale;",
		"while (sampleOffset>=SND_CHUNK_SIZE) {",
		"if (!chunk) {",
		"chunk = sc->soundData;",
		"leftvol = ch->leftvol*snd_vol;",
		"rightvol = ch->rightvol*snd_vol;",
		"samp[i].left += (data * leftvol)>>8;",
		"samp[i].right += (data * rightvol)>>8;",
	):
		assert expected in paint16_block

	_assert_order(
		paint_block,
		"snd_vol = s_volume->value*255;",
		"while ( s_paintedtime < endtime ) {",
		"if ( endtime - s_paintedtime > PAINTBUFFER_SIZE ) {",
		"if ( s_rawend < s_paintedtime ) {",
		"if ( s_voiceVolume && s_voiceVolume->value > 0.0f ) {",
		"// paint in the channels.",
		"// paint in the looped channels.",
		"S_TransferPaintBuffer( end );",
		"s_paintedtime = end;",
	)

	for expected in (
		"if ( s_musicVolume && s_musicVolume->value > 0.0f ) {",
		'Com_DPrintf( "background sound underrun\\n" );',
		"Com_Memset(paintbuffer, 0, (end - s_paintedtime) * sizeof(portable_samplepair_t));",
		"stop = (end < s_rawend) ? end : s_rawend;",
		"s = i&(MAX_RAW_SAMPLES-1);",
		"paintbuffer[i-s_paintedtime] = s_rawsamples[s];",
		"paintbuffer[i-s_paintedtime].left =",
		"paintbuffer[i-s_paintedtime].right = 0;",
		"voiceScale = (int)( Com_Clamp( 0.0f, 2.0f, s_voiceVolume->value ) * 256.0f );",
		"for ( voiceIndex = 0; voiceIndex < MAX_VOICE_CHANNELS; ++voiceIndex ) {",
		"voice = &s_voiceChannels[voiceIndex];",
		"if ( voiceStart < s_paintedtime ) {",
		"if ( voiceEnd > end ) {",
		'Com_DPrintf( "voice channel %d: no data in the paint window\\n", voiceIndex );',
		"voice->samples[sampleTime & ( VOICE_BUFFER_SAMPLES - 1 )] * voiceScale;",
		"samp->left += data;",
		"samp->right += data;",
		"voice->startSample = end;",
		'Com_DPrintf( "voice channel %d: consumed all buffered voice samples\\n", voiceIndex );',
	):
		assert expected in paint_block

	for expected in (
		"ch = s_channels;",
		"for ( i = 0; i < MAX_CHANNELS ; i++, ch++ ) {",
		"if ( !ch->thesfx || (ch->leftvol<0.25 && ch->rightvol<0.25 )) {",
		"sampleOffset = ltime - ch->startSample;",
		"if ( sampleOffset + count > sc->soundLength ) {",
		"if( sc->soundCompressionMethod == 1) {",
		"S_PaintChannelFromADPCM",
		"} else if( sc->soundCompressionMethod == 2) {",
		"S_PaintChannelFromWavelet",
		"} else if( sc->soundCompressionMethod == 3) {",
		"S_PaintChannelFromMuLaw",
		"} else {",
		"S_PaintChannelFrom16",
	):
		assert expected in dynamic_block

	for expected in (
		"ch = loop_channels;",
		"for ( i = 0; i < numLoopChannels ; i++, ch++ ) {",
		"if ( !ch->thesfx || (!ch->leftvol && !ch->rightvol )) {",
		"if (sc->soundData==NULL || sc->soundLength==0) {",
		"do {",
		"sampleOffset = (ltime % sc->soundLength);",
		"if ( sampleOffset + count > sc->soundLength ) {",
		"if( sc->soundCompressionMethod == 1) {",
		"S_PaintChannelFromADPCM",
		"} else if( sc->soundCompressionMethod == 2) {",
		"S_PaintChannelFromWavelet",
		"} else if( sc->soundCompressionMethod == 3) {",
		"S_PaintChannelFromMuLaw",
		"} else {",
		"S_PaintChannelFrom16",
		"ltime += count;",
		"} while ( ltime < end);",
	):
		assert expected in loop_block


def test_client_steam_voice_frame_reconstructs_retail_transport_path() -> None:
	cl_main = CL_MAIN.read_text(encoding="utf-8")

	start_block = _extract_function_block(cl_main, "static void CL_VoiceStartRecording_f( void )")
	stop_block = _extract_function_block(cl_main, "static void CL_VoiceStopRecording_f( void )")
	send_block = _extract_function_block(cl_main, "static void CL_Steam_SendVoicePacket( void )")
	stats_report_block = _extract_function_block(cl_main, "static void CL_Steam_ProcessStatsReportPackets( void )")
	process_block = _extract_function_block(cl_main, "static void CL_Steam_ProcessVoicePackets( void )")
	session_block = _extract_function_block(
		cl_main,
		"static void CL_Steam_Client_OnP2PSessionRequest( void *context, const ql_steam_p2p_session_request_t *event )",
	)
	frame_block = _extract_function_block(cl_main, "void SteamClient_Frame( void )")

	assert "#define CL_STEAM_STATS_REPORT_CHANNEL 0" in cl_main
	assert "QL_Steamworks_StartVoiceRecording();" in start_block
	assert "(int)QL_Steamworks_GetVoiceOptimalSampleRate()" in start_block
	assert "QL_Steamworks_StopVoiceRecording();" in stop_block
	assert "CL_GetServerSteamId( &serverIdLow, &serverIdHigh )" in send_block
	assert "QL_Steamworks_GetCompressedVoice( compressedVoice, sizeof( compressedVoice ), &compressedBytes )" in send_block
	assert "QL_Steamworks_SendP2PPacket( &serverId, compressedVoice, compressedBytes, 1, CL_STEAM_VOICE_CHANNEL )" in send_block
	assert "while ( QL_Steamworks_IsP2PPacketAvailable( &packetSize, CL_STEAM_STATS_REPORT_CHANNEL ) ) {" in stats_report_block
	assert "QL_Steamworks_ReadP2PPacket( packetData, packetSize, &bytesRead, &remoteId, CL_STEAM_STATS_REPORT_CHANNEL )" in stats_report_block
	assert 'CL_Steam_PublishBrowserEvent( "game.stats.report", reportPayload );' in stats_report_block
	assert "QL_Steamworks_ReadP2PPacket( packetBuffer, packetSize, &bytesRead, &remoteId, CL_STEAM_VOICE_CHANNEL )" in process_block
	assert "QL_Steamworks_DecompressVoice( packetBuffer + 1, bytesRead - 1, decompressedVoice, sizeof( decompressedVoice ), &voiceBytes, CL_STEAM_VOICE_SAMPLE_RATE )" in process_block
	assert "CL_IsVoiceSenderMuted( clientNum )" in process_block
	assert "CL_SetClientSpeakingState( clientNum, qtrue );" in process_block
	assert "S_AddVoiceSamples( clientNum, (int)( voiceBytes >> 1 ), decompressedVoice );" in process_block
	assert "QL_Steamworks_GetP2PTransportLabel()" in cl_main
	assert "CL_GetServerSteamId( &serverIdLow, &serverIdHigh ) || !( serverIdLow | serverIdHigh )" in session_block
	assert "trackedSteamId = ( (uint64_t)serverIdHigh << 32 ) | serverIdLow;" in session_block
	assert "if ( event->remoteId.value != trackedSteamId ) {" in session_block
	assert "QL_Steamworks_AcceptP2PSession( &event->remoteId )" in session_block
	assert "qboolean SteamClient_IsInitialized( void ) {" in cl_main
	assert "static qboolean SteamClient_IsInitialized( void ) {" not in cl_main
	assert "services = QL_RefreshPlatformServices();" not in frame_block
	assert "SteamClient_SetInitializedState( services );" not in frame_block
	assert "if ( !SteamClient_IsInitialized() ) {" in frame_block
	assert "QL_Steamworks_RunCallbacks();" in frame_block
	assert "CL_Steam_SendVoicePacket();" in frame_block
	assert "CL_Steam_ProcessStatsReportPackets();" in frame_block
	assert "CL_Steam_ProcessVoicePackets();" in frame_block
	assert frame_block.index("CL_Steam_SendVoicePacket();") < frame_block.index("CL_Steam_ProcessStatsReportPackets();")
	assert frame_block.index("CL_Steam_ProcessStatsReportPackets();") < frame_block.index("CL_Steam_ProcessVoicePackets();")


def test_platform_steam_voice_wrappers_use_retail_slots() -> None:
	steamworks = PLATFORM_STEAMWORKS.read_text(encoding="utf-8")

	load_block = _extract_function_block(steamworks, "qboolean QL_Steamworks_LoadLibrary( void )")
	send_block = _extract_function_block(
		steamworks,
		"qboolean QL_Steamworks_SendP2PPacket( const CSteamID *steamId, const void *data, uint32_t length, int sendType, int channel )",
	)
	available_block = _extract_function_block(
		steamworks,
		"qboolean QL_Steamworks_IsP2PPacketAvailable( uint32_t *outSize, int channel )",
	)
	read_block = _extract_function_block(
		steamworks,
		"qboolean QL_Steamworks_ReadP2PPacket( void *data, uint32_t dataSize, uint32_t *outSize, CSteamID *outSteamId, int channel )",
	)
	accept_block = _extract_function_block(
		steamworks,
		"qboolean QL_Steamworks_AcceptP2PSession( const CSteamID *steamId )",
	)
	transport_label_block = _extract_function_block(steamworks, "const char *QL_Steamworks_GetP2PTransportLabel( void )")
	start_block = _extract_function_block(steamworks, "qboolean QL_Steamworks_StartVoiceRecording( void )")
	stop_block = _extract_function_block(steamworks, "qboolean QL_Steamworks_StopVoiceRecording( void )")
	get_block = _extract_function_block(
		steamworks,
		"qboolean QL_Steamworks_GetCompressedVoice( void *data, uint32_t dataSize, uint32_t *outSize )",
	)
	decompress_block = _extract_function_block(
		steamworks,
		"qboolean QL_Steamworks_DecompressVoice( const void *compressedData, uint32_t compressedSize, void *data, uint32_t dataSize, uint32_t *outSize, uint32_t sampleRate )",
	)
	rate_block = _extract_function_block(steamworks, "uint32_t QL_Steamworks_GetVoiceOptimalSampleRate( void )")

	assert 'QL_Steamworks_LoadOptionalSymbolAlias( (void **)&state.SteamNetworking, "SteamNetworking", "SteamAPI_SteamNetworking" );' in load_block
	assert "vtable[0]" in send_block
	assert "vtable[1]" in available_block
	assert "vtable[2]" in read_block
	assert "vtable[0x0c / 4]" in accept_block
	assert 'return "legacy ISteamNetworking";' in transport_label_block
	assert "vtable[0x1c / 4]" in start_block
	assert "vtable[0x20 / 4]" in stop_block
	assert "vtable[0x28 / 4]" in get_block
	assert "vtable[0x2c / 4]" in decompress_block
	assert "vtable[0x30 / 4]" in rate_block


def test_sound_cache_and_shutdown_match_retail_allocator_contracts() -> None:
	hlil = QL_STEAM_HLIL.read_text(encoding="utf-8")
	snd_dma = SND_DMA.read_text(encoding="utf-8")
	snd_mem = SND_MEM.read_text(encoding="utf-8")

	shutdown_block = _extract_function_block(snd_dma, "void S_Shutdown( void )")
	begin_block = _extract_function_block(snd_dma, "void S_BeginRegistration( void )")
	free_block = _extract_function_block(snd_mem, "void\tSND_free")
	malloc_block = _extract_function_block(snd_mem, "sndBuffer*\tSND_malloc")
	snd_setup_block = _extract_function_block(snd_mem, "void SND_setup()")
	snd_shutdown_block = _extract_function_block(snd_mem, "void SND_shutdown( void )")
	display_block = _extract_function_block(snd_mem, "void S_DisplayFreeMemory()")
	resample_block = _extract_function_block(snd_mem, "static void ResampleSfx")
	file_block = _extract_function_block(snd_mem, "static qboolean S_OpenSoundFile")
	pcm_block = _extract_function_block(snd_mem, "static qboolean S_LoadPCMSound")
	ogg_block = _extract_function_block(snd_mem, "static qboolean S_LoadOggSound")
	wav_block = _extract_function_block(snd_mem, "static qboolean S_LoadWavSound")
	load_block = _extract_function_block(snd_mem, "qboolean S_LoadSound( sfx_t *sfx )")

	for expected in (
		"004dbb10    int32_t* sub_4dbb10(int32_t* arg1)",
		"004dbb1c  data_12c5b8c += 0x808",
		"004dbb28  data_12c5b88 = arg1",
		"004dbb30    int32_t sub_4dbb30()",
		'004dbb48  int32_t esi_2 = sub_4ce0d0(x87_r0, "com_soundMegs", "16", 0x21)[0xc] * 0x202000',
		"004dbb51  data_12c5b8c = esi_2",
		"004dbb68  data_12c5b84 = eax_2",
		"004dbb8a  data_12c5b88 = esi_2 + eax_2 - 0x808",
		'004dbb99  return sub_4c9860(esi_2 + eax_2 - 0x808, "Sound memory manager started\\n")',
		"004dbba0    int32_t sub_4dbba0()",
		"004dbba5  data_12c5b8c = 0",
		"004dbbaf  data_12c5b90 = 0",
		"004dbbc7      data_12c5b84 = 0",
		"004dbbe0    int32_t sub_4dbbe0()",
		"004dbbeb  int32_t var_4 = data_12c5b8c",
		"004dbbec  int32_t var_8 = data_12c5b90",
		'char const data_544528[0x2f] = "%d bytes sound buffer memory in use, %d free \\n", 0',
		"004dbc00    int32_t sub_4dbc00(int32_t* arg1, int32_t arg2, int32_t arg3, int32_t arg4)",
		"004dbc1b  long double x87_r6 = fconvert.t(fconvert.s(float.t(arg2) / float.t(data_142c330)))",
		"004dbc34  edi[3] = eax",
		"004dbc6d          if (arg3 != 2)",
		"004dbc7c              esi_2 = ((zx.d(*(result + arg4)) - 0x80) << 8).w",
		"004dbc6f              esi_2 = *(arg4 + (result << 1))",
		"004dbc81          int32_t ebx_3 = edx & 0x3ff",
		"004dbca2              data_12c5b8c -= 0x808",
		"004dbcac              data_12c5b90 += 0x808",
		"004dbcc0              *(result + 0x800) = 0",
		"004dc8ad  sub_4dbc00(arg2, *(eax_4 + 8), 2, eax_7)",
		"004dcd07  sub_4dbc00(arg1, var_18, var_14, eax_4)",
	):
		assert expected in hlil

	assert '#define DEF_COMSOUNDMEGS "16"' in snd_mem
	assert "void SND_shutdown( void ) {" in snd_mem
	for expected in (
		"*(sndBuffer **)v = freelist;",
		"freelist = (sndBuffer*)v;",
		"inUse += sizeof(sndBuffer);",
	):
		assert expected in free_block
	assert "totalInUse -= sizeof(sndBuffer);" not in free_block

	for expected in (
		"if (freelist == NULL) {",
		"S_FreeOldestSound();",
		"goto redo;",
		"inUse -= sizeof(sndBuffer);",
		"totalInUse += sizeof(sndBuffer);",
		"v = freelist;",
		"freelist = *(sndBuffer **)freelist;",
		"v->next = NULL;",
	):
		assert expected in malloc_block

	for expected in (
		'cv = Cvar_Get( "com_soundMegs", DEF_COMSOUNDMEGS, CVAR_LATCH | CVAR_ARCHIVE );',
		"scs = (cv->integer*1024);",
		"buffer = malloc(scs*sizeof(sndBuffer) );",
		"inUse = scs*sizeof(sndBuffer);",
		"totalInUse = 0;",
		"freelist = p + scs - 1;",
		'Com_Printf("Sound memory manager started\\n");',
	):
		assert expected in snd_setup_block

	for expected in (
		"free( buffer );",
		"buffer = NULL;",
		"freelist = NULL;",
		"inUse = 0;",
		"totalInUse = 0;",
	):
		assert expected in snd_shutdown_block

	assert 'Com_Printf("%d bytes sound buffer memory in use, %d free \\n", totalInUse, inUse);' in display_block
	assert 'Com_Printf("%d bytes sound buffer memory in use, %d free\\n", totalInUse, inUse);' not in display_block
	for expected in (
		"static void ResampleSfx( sfx_t *sfx, int inrate, int inwidth, byte *data )",
		"stepscale = (float)inrate / dma.speed;",
		"outcount = sfx->soundLength / stepscale;",
		"sfx->soundLength = outcount;",
		"samplefrac = 0;",
		"fracstep = stepscale * 256;",
		"chunk = sfx->soundData;",
		"srcsample = samplefrac >> 8;",
		"samplefrac += fracstep;",
		"if( inwidth == 2 ) {",
		"sample = LittleShort ( ((short *)data)[srcsample] );",
		"sample = (int)( (unsigned char)(data[srcsample]) - 128) << 8;",
		"part  = (i&(SND_CHUNK_SIZE-1));",
		"newchunk = SND_malloc();",
		"sfx->soundData = newchunk;",
		"chunk->next = newchunk;",
		"chunk->sndChunk[part] = sample;",
	):
		assert expected in resample_block
	assert "qboolean compressed" not in resample_block
	assert "SND_shutdown();" in shutdown_block
	assert 'Cmd_RemoveCommand("play");' in shutdown_block
	assert 'Cmd_RemoveCommand("music");' in shutdown_block
	assert 'Cmd_RemoveCommand("s_list");' in shutdown_block
	assert 'Cmd_RemoveCommand("s_info");' in shutdown_block
	assert 'Cmd_RemoveCommand("s_stop");' in shutdown_block
	assert 'Cmd_RemoveCommand("stopsound");' not in shutdown_block
	assert 'Cmd_RemoveCommand("soundlist");' not in shutdown_block
	assert 'Cmd_RemoveCommand("soundinfo");' not in shutdown_block
	assert "SND_shutdown();" in begin_block
	assert "SND_setup();" in begin_block
	assert 'if (s_numSfx == 0)' not in begin_block
	assert 'COM_DefaultExtension( resolvedName, resolvedNameSize, ".ogg" );' in file_block
	assert "*fileType = S_SoundFileTypeForPath( name );" in file_block
	assert "*outSize = FS_FOpenFileRead( resolvedName, file, qtrue );" in file_block
	assert "*fileType = SFT_OGG;" in file_block
	assert "FS_ReadFile" not in file_block
	assert 'if ( !S_OpenSoundFile( sfx->soundName, loadName, sizeof( loadName ), &file, &size, &fileType ) ) {' in load_block
	assert "switch ( fileType ) {" in load_block
	assert "case SFT_WAV:" in load_block
	assert "result = S_LoadWavSound( sfx, loadName, file );" in load_block
	assert "case SFT_OGG:" in load_block
	assert "result = S_LoadOggSound( sfx, loadName, file, size );" in load_block
	assert "FS_FCloseFile( file );" in load_block
	assert "sfx->lastTimeUsed = Com_Milliseconds();" in load_block
	assert "FS_FreeFile( data );" not in load_block
	assert "sfx->lastTimeUsed = Com_Milliseconds()+1;" not in snd_mem
	assert "data = Hunk_AllocateTempMemory( size );" in ogg_block
	assert "if ( FS_Read( data, size, file ) != size ) {" in ogg_block
	assert "S_VorbisDecodeMemory( loadName, data, size, &info, &oggPcm )" in ogg_block
	assert "result = S_LoadPCMSound( sfx, loadName, &info, (byte *)oggPcm );" in ogg_block
	assert "Hunk_FreeTempMemory( oggPcm );" in ogg_block
	assert "Hunk_FreeTempMemory( data );" in ogg_block
	assert "dataLength = GetWavinfo( file, &info );" in wav_block
	assert 'Com_Error( ERR_DROP, "%s is not a mono wav file", loadName );' in wav_block
	assert "data = Hunk_AllocateTempMemory( dataLength );" in wav_block
	assert "if ( FS_Read( data, dataLength, file ) != dataLength ) {" in wav_block
	assert "result = S_LoadPCMSound( sfx, loadName, &info, data );" in wav_block
	assert "Hunk_FreeTempMemory( data );" in wav_block
	assert 'Com_DPrintf( "WAV_Load: %s is not a 16-bit file\\n", loadName );' in pcm_block
	assert 'Com_DPrintf( "WAV_Load: %s is not a 22kHz file\\n", loadName );' in pcm_block
	assert "ResampleSfx( sfx, info->rate, info->width, source );" in pcm_block
	assert "ResampleSfx( sfx, info->rate, info->width, source, qfalse );" not in pcm_block
	assert "lastTimeUsed" not in pcm_block
	assert 'Com_Printf ("%s is a stereo wav file\\n", loadName);' not in wav_block
	assert 'WARNING: %s is a 8 bit wav file' not in pcm_block
	assert 'WARNING: %s is not a 22kHz wav file' not in pcm_block


def test_background_track_ogg_update_matches_retail_restart_path() -> None:
	aliases = json.loads(ALIASES.read_text(encoding="utf-8"))["quakelive_steam_srp"]
	function_rows = {
		row["name"]: row
		for row in csv.DictReader(FUNCTIONS_CSV.read_text(encoding="utf-8").splitlines())
	}
	hlil = QL_STEAM_HLIL.read_text(encoding="utf-8")
	snd_dma = SND_DMA.read_text(encoding="utf-8")

	has_ogg_block = _extract_function_block(
		snd_dma,
		"static qboolean S_BackgroundTrackHasOggExtension",
	)
	set_path_block = _extract_function_block(
		snd_dma,
		"static void S_SetOggTrackPath",
	)
	close_block = _extract_function_block(snd_dma, "static void S_CloseBackgroundOgg")
	open_block = _extract_function_block(snd_dma, "static qboolean S_OpenBackgroundOgg")
	stop_block = _extract_function_block(snd_dma, "void S_StopBackgroundTrack( void )")
	start_block = _extract_function_block(snd_dma, "void S_StartBackgroundTrack")
	update_helper = _extract_function_block(
		snd_dma,
		"static int S_OggUpdateBackgroundTrack( byte *buffer, int bytesToRead )",
	)
	update_block = _extract_function_block(snd_dma, "void S_UpdateBackgroundTrack( void )")

	for alias, (name, ghidra_name, size) in SOUND_BACKGROUND_ALIASES.items():
		assert aliases[alias] == name
		assert aliases[ghidra_name] == name
		assert function_rows[ghidra_name]["size"] == size

	for alias, name in SOUND_BACKGROUND_LOWERCASE_BN_ALIASES.items():
		assert aliases[alias] == name

	for expected in (
		"004db030    void sub_4db030()",
		"004db037  if (data_12c5b74 != 0)",
		"004db039      sub_4dca40()",
		"004db03e      data_12c5b74 = 0",
		"004db048      data_13e1850 = 0",
		"004db060    int32_t sub_4db060(char* arg1, char* arg2)",
		'004db0a0      sub_4c9ab0("S_StartBackgroundTrack( %s, %s )…")',
		'char const data_5442f0[0x39] = "S_StartBackgroundTrack: %s should have an OGG extension\\n", 0',
		"004db0dd          sub_4d8a40(__saved_ebx_3, &data_12608d0, 0x40)",
		'004db0ee          sub_4d9a60(&data_12608d0, 0x40, ".ogg")',
		"004db1c0    int32_t sub_4db1c0()",
		"sub_4dca50(&var_7538, esi_3)",
		"004db2c1                      result = sub_4dca40()",
		"004db2e3                      result = sub_4db060(var_18_3, var_14_3)",
		"004dca40    int32_t sub_4dca40()",
		"sub_4fcde0(&data_12cdbb0)",
	):
		assert expected in hlil

	assert "extension = Q_strrchr( path, '.' );" in has_ogg_block
	assert 'return ( extension && !Q_stricmp( extension, ".ogg" ) );' in has_ogg_block

	for expected in (
		"if ( S_BackgroundTrackHasOggExtension( source ) ) {",
		"Q_strncpyz( dest, source, destSize );",
		"COM_StripExtension( source, stripped );",
		'COM_DefaultExtension( dest, destSize, ".ogg" );',
	):
		assert expected in set_path_block

	assert "S_OggStreamClose( &s_backgroundOgg );" in close_block

	for expected in (
		"if ( !S_OggStreamOpen( &s_backgroundOgg, name ) ) {",
		"s_backgroundIsOgg = qtrue;",
		"s_backgroundFile = 0;",
		"s_backgroundInfo.format = WAV_FORMAT_PCM;",
		"s_backgroundInfo.channels = S_OggStreamChannels( &s_backgroundOgg );",
		"s_backgroundInfo.rate = S_OggStreamRate( &s_backgroundOgg );",
		"s_backgroundInfo.width = S_OggStreamWidth( &s_backgroundOgg );",
		"S_CloseBackgroundOgg();",
		"s_backgroundIsOgg = qfalse;",
	):
		assert expected in open_block

	for expected in (
		"if ( s_backgroundFile ) {",
		"S_CloseBackgroundOgg();",
		"s_backgroundIsOgg = qfalse;",
		"s_rawend = 0;",
	):
		assert expected in stop_block
	_assert_order(
		stop_block,
		"stopped = qfalse;",
		"if ( s_backgroundFile ) {",
		"stopped = qtrue;",
		"if ( S_OggStreamActive( &s_backgroundOgg ) ) {",
		"S_CloseBackgroundOgg();",
		"stopped = qtrue;",
		"s_backgroundIsOgg = qfalse;",
		"if ( stopped ) {",
		"s_rawend = 0;",
	)

	for expected in (
		"if ( !intro || !intro[0] ) {",
		"if ( !loop || !loop[0] ) {",
		'Com_DPrintf( "S_StartBackgroundTrack( %s, %s )\\n", intro, loop );',
		"if ( !S_BackgroundTrackHasOggExtension( intro ) ) {",
		'Com_DPrintf( "S_StartBackgroundTrack: %s should have an OGG extension\\n", intro );',
		"S_SetOggTrackPath( loop, s_backgroundLoop, sizeof( s_backgroundLoop ) );",
		"S_SetOggTrackPath( intro, introPath, sizeof( introPath ) );",
		"if ( S_OggStreamActive( &s_backgroundOgg ) ) {",
		"S_CloseBackgroundOgg();",
		"if ( !S_OpenBackgroundOgg( introPath ) ) {",
		'Com_Printf( S_COLOR_YELLOW "WARNING: couldn\'t open music file %s\\n", introPath );',
	):
		assert expected in start_block
	_assert_order(
		start_block,
		"S_SetOggTrackPath( loop, s_backgroundLoop, sizeof( s_backgroundLoop ) );",
		"S_SetOggTrackPath( intro, introPath, sizeof( introPath ) );",
		"if ( s_backgroundFile ) {",
		"if ( S_OggStreamActive( &s_backgroundOgg ) ) {",
		"S_CloseBackgroundOgg();",
		"s_backgroundIsOgg = qfalse;",
		"if ( !S_OpenBackgroundOgg( introPath ) ) {",
	)
	assert "s_rawend = 0;" not in start_block

	assert 'result = S_OggStreamRead( &s_backgroundOgg, buffer, bytesToRead );' in update_helper
	assert 'Com_Printf( S_COLOR_YELLOW "OGG_UpdateBackgroundTrack: %i\\n", result );' in update_helper
	assert "S_CloseBackgroundOgg();" in update_helper
	assert "return 0;" in update_helper
	assert "if ( !S_OggStreamActive( &s_backgroundOgg ) ) {" in update_block
	assert "r = S_OggUpdateBackgroundTrack( raw, fileBytes );" in update_block
	assert "S_RawSamples( fileSamples, s_backgroundInfo.rate," in update_block
	assert "if ( r < fileBytes || fileBytes == 0 ) {" in update_block
	assert "s_backgroundIsOgg = qfalse;" in update_block
	assert "if ( !S_BackgroundTrackLoop() ) {" in update_block
	assert "S_StopBackgroundTrack();" in update_block
	assert "S_OpenBackgroundWav" not in snd_dma
	assert "S_ResolveMusicFile" not in snd_dma
	assert "S_FileExists" not in snd_dma
	assert "S_SetTrackExtension" not in snd_dma
	assert "S_FindWavChunk" not in snd_dma
	assert "FGetLittleShort" not in snd_dma
	assert "FGetLittleLong" not in snd_dma
	assert "falling back to WAV" not in snd_dma
	assert "StreamedRead failure on music track" not in snd_dma
	assert "S_ByteSwapRawSamples" not in snd_dma
	assert "s_backgroundSamples" not in snd_dma
	assert 'COM_DefaultExtension( candidate, sizeof( candidate ), ".wav" );' not in snd_dma


def test_vorbis_memory_decode_matches_retail_mono_contract() -> None:
	snd_ogg_decode = SND_OGG_DECODE.read_text(encoding="utf-8")
	snd_ogg_stream = SND_OGG_STREAM.read_text(encoding="utf-8")
	enabled_block = snd_ogg_decode.rsplit("#else", 1)[0]
	read_block = _extract_function_block(
		enabled_block,
		"static size_t S_VorbisBufferRead",
	)
	seek_block = _extract_function_block(
		enabled_block,
		"static int S_VorbisBufferSeek",
	)
	tell_block = _extract_function_block(
		enabled_block,
		"static long S_VorbisBufferTell",
	)
	decode_block = _extract_function_block(
		enabled_block,
		"qboolean S_VorbisDecodeMemory( const char *name, const byte *data, int length, wavinfo_t *info, short **outPcm )",
	)
	stream_read_block = _extract_function_block(
		snd_ogg_stream,
		"static size_t S_OggReadCallback",
	)

	assert "static int S_VorbisBufferClose" not in snd_ogg_decode
	assert "callbacks.close_func = S_VorbisBufferClose;" not in snd_ogg_decode
	assert "requested = size * nmemb;" in read_block
	assert "available = buffer->length - buffer->position;" in read_block
	assert "Com_Memcpy( ptr, buffer->data + buffer->position, count );" in read_block
	assert "buffer->position += (int)count;" in read_block
	assert "return count;" in read_block
	assert "return count / size;" not in read_block
	assert "target = (int)offset;" in seek_block
	assert "target = buffer->position + (int)offset;" in seek_block
	assert "target = buffer->length + (int)offset;" in seek_block
	assert "return buffer->position;" in tell_block
	assert "return (size_t)bytesRead;" in stream_read_block
	assert "bytesRead / (int)size" not in stream_read_block
	assert "if ( channels != 1 ) {" in decode_block
	assert 'Com_Error( ERR_DROP, "%s is not a mono file", name ? name : "<unnamed>" );' in decode_block
	assert 'Com_Printf( S_COLOR_YELLOW "OGG_Decode: %s: %i\\n", name ? name : "<unnamed>", bytesRead );' in decode_block
	assert 'Com_Printf( "%s is not a mono file\\n", name ? name : "<unnamed>" );' not in decode_block
	assert "channels > 2" not in decode_block
	assert "stereo Vorbis file and was downmixed to mono" not in snd_ogg_decode
	assert "chunkSamples" not in decode_block
	assert "samplePairs" not in decode_block
	assert "Com_Memcpy( writePtr, decodeChunk, sampleCount * sizeof( short ) );" in decode_block
