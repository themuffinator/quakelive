"""Guard retail-backed engine sound playback entrypoint behavior."""

from __future__ import annotations

import csv
import json
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parent.parent
ALIASES = REPO_ROOT / "references" / "analysis" / "quakelive_symbol_aliases.json"
FUNCTIONS_CSV = (
	REPO_ROOT
	/ "references"
	/ "reverse-engineering"
	/ "ghidra"
	/ "quakelive_steam"
	/ "functions.csv"
)
QL_STEAM_HLIL = REPO_ROOT / "references" / "hlil" / "quakelive" / "quakelive_steam.exe" / "quakelive_steam.exe_hlil.txt"
CL_CGAME = REPO_ROOT / "src" / "code" / "client" / "cl_cgame.c"
QL_CGAME_IMPORTS = REPO_ROOT / "src" / "code" / "client" / "ql_cgame_imports.inc"
CG_PUBLIC = REPO_ROOT / "src" / "code" / "cgame" / "cg_public.h"
CG_SYSCALLS = REPO_ROOT / "src" / "code" / "cgame" / "cg_syscalls.c"
SND_DMA = REPO_ROOT / "src" / "code" / "client" / "snd_dma.c"
SND_LOCAL = REPO_ROOT / "src" / "code" / "client" / "snd_local.h"
WIN_SND = REPO_ROOT / "src" / "code" / "win32" / "win_snd.c"


CORE_SOUND_ALIASES = {
	"sub_4D9C50": ("S_ChannelSetup", "FUN_004d9c50", "74"),
	"sub_4D9CA0": ("S_Shutdown", "FUN_004d9ca0", "83"),
	"sub_4D9EF0": ("S_SpatializeOrigin", "FUN_004d9ef0", "352"),
	"sub_4DA050": ("S_StartSoundVolume", "FUN_004da050", "760"),
	"sub_4DA350": ("S_StartSound", "FUN_004da350", "35"),
	"sub_4DA380": ("S_StartLocalSoundVolume", "FUN_004da380", "83"),
	"sub_4DA3E0": ("S_ClearSoundBuffer", "FUN_004da3e0", "163"),
	"sub_4DA4C0": ("S_AddLoopingSound", "FUN_004da4c0", "558"),
	"sub_4DA6F0": ("S_AddLoopSounds", "FUN_004da6f0", "328"),
	"sub_4DA840": ("S_RawSamples", "FUN_004da840", "688"),
	"sub_4DAC80": ("S_UpdateEntityPosition", "FUN_004dac80", "72"),
	"sub_4DACD0": ("S_Respatialize", "FUN_004dacd0", "351"),
	"sub_4DAE30": ("S_ScanChannelStarts", "FUN_004dae30", "413"),
	"sub_4DB490": ("S_GetSoundtime", "FUN_004db490", "209"),
	"sub_4DB3F0": ("S_StartLocalSound", "FUN_004db3f0", "82"),
	"sub_4DB450": ("S_StopAllSounds", "FUN_004db450", "49"),
	"sub_4DB570": ("S_Update_", "FUN_004db570", "262"),
	"sub_4DB680": ("S_Update", "FUN_004db680", "129"),
	"sub_4DB870": ("S_Init", "FUN_004db870", "593"),
	"sub_4DBAD0": ("S_DisableSounds", "FUN_004dbad0", "59"),
}

CORE_SOUND_LOWERCASE_BN_ALIASES = {
	"sub_4d9c50": "S_ChannelSetup",
	"sub_4d9ca0": "S_Shutdown",
	"sub_4d9ef0": "S_SpatializeOrigin",
	"sub_4da050": "S_StartSoundVolume",
	"sub_4da350": "S_StartSound",
	"sub_4da380": "S_StartLocalSoundVolume",
	"sub_4da3e0": "S_ClearSoundBuffer",
	"sub_4da490": "S_ClearLoopingSoundsFrame",
	"sub_4da4c0": "S_AddLoopingSound",
	"sub_4da6f0": "S_AddLoopSounds",
	"sub_4da840": "S_RawSamples",
	"sub_4dac80": "S_UpdateEntityPosition",
	"sub_4dacd0": "S_Respatialize",
	"sub_4dae30": "S_ScanChannelStarts",
	"sub_4db3f0": "S_StartLocalSound",
	"sub_4db450": "S_StopAllSounds",
	"sub_4db490": "S_GetSoundtime",
	"sub_4db570": "S_Update_",
	"sub_4db680": "S_Update",
	"sub_4db870": "S_Init",
	"sub_4dbad0": "S_DisableSounds",
	"j_sub_4da490": "QLCGImport_S_ClearLoopingSoundsFrame",
	"j_sub_4da3e0": "QLCGImport_S_ClearLoopingSoundsKillAll",
}


def _read(path: Path) -> str:
	return path.read_text(encoding="utf-8")


def _function_block(source: str, marker: str) -> str:
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


def _assert_order(block: str, *needles: str) -> None:
	cursor = 0
	for needle in needles:
		index = block.find(needle, cursor)
		if index == -1:
			raise AssertionError(f"expected ordered snippet not found after {cursor}: {needle}")
		cursor = index + len(needle)


def _function_rows() -> dict[str, dict[str, str]]:
	return {
		row["name"]: row
		for row in csv.DictReader(FUNCTIONS_CSV.read_text(encoding="utf-8").splitlines())
	}


def test_sound_playback_aliases_cover_retail_core_entrypoints() -> None:
	aliases = json.loads(_read(ALIASES))["quakelive_steam_srp"]
	rows = _function_rows()

	for alias, (name, ghidra_name, size) in CORE_SOUND_ALIASES.items():
		assert aliases[alias] == name
		assert aliases[ghidra_name] == name
		assert rows[ghidra_name]["size"] == size

	for alias, name in CORE_SOUND_LOWERCASE_BN_ALIASES.items():
		assert aliases[alias] == name

	assert aliases["sub_4DA490"] == "S_ClearLoopingSoundsFrame"
	assert "FUN_004da490" not in aliases
	assert aliases["j_sub_4DA490"] == "QLCGImport_S_ClearLoopingSoundsFrame"
	assert aliases["j_sub_4DA3E0"] == "QLCGImport_S_ClearLoopingSoundsKillAll"


def test_sound_init_cvar_surface_drops_legacy_rate_and_separation_controls() -> None:
	hlil = _read(QL_STEAM_HLIL)
	snd_dma = _read(SND_DMA)
	snd_local = _read(SND_LOCAL)
	win_snd = _read(WIN_SND)
	init_block = _function_block(snd_dma, "void S_Init( void )")

	for expected in (
		'"s_announcerVolume"',
		'"s_doppler"',
		'"s_initsound"',
		'"s_mixahead"',
		'"s_mixPreStep"',
		'"s_musicvolume"',
		'"s_pvs"',
		'"s_voiceVolume"',
		'"s_voiceStep"',
		'"s_show"',
		'"s_testsound"',
		'"s_volume"',
		"004db870    int32_t sub_4db870()",
	):
		assert expected in hlil

	assert '"s_khz"' not in hlil
	assert '"s_separation"' not in hlil
	assert 's_khz = Cvar_Get ("s_khz", "22", CVAR_ARCHIVE);' not in init_block
	assert 's_separation = Cvar_Get ("s_separation", "0.5", CVAR_ARCHIVE);' not in init_block
	assert "cvar_t\t\t*s_khz;" not in snd_dma
	assert "cvar_t\t\t*s_separation;" not in snd_dma
	assert "extern cvar_t\t*s_khz;" not in snd_local
	assert "extern cvar_t\t*s_separation;" not in snd_local
	assert "s_khz->integer" not in win_snd
	assert "\tdma.speed = 22050;" in win_snd


def test_sound_lifecycle_setup_shutdown_and_disable_match_retail_state_edges() -> None:
	hlil = _read(QL_STEAM_HLIL)
	source = _read(SND_DMA)
	channel_setup_block = _function_block(source, "void S_ChannelSetup()")
	shutdown_block = _function_block(source, "void S_Shutdown( void )")
	init_block = _function_block(source, "void S_Init( void )")
	disable_block = _function_block(source, "void S_DisableSounds( void )")

	for expected in (
		"004d9c50    void* sub_4d9c50()",
		"004d9c5c  sub_4c95e0(&data_14298c0, 0, 0x1500)",
		"004d9c7c  for (i = &data_142ad88; i u> &data_14298c0; i -= 0x38)",
		"004d9c89  data_12c5b78 = &data_142ad88",
		'004d9c99  return sub_4c9ab0("Channel memory manager started\\n")',
		"004d9ca0    void sub_4d9ca0()",
		"004d9ca9      sub_4dbba0()",
		"004d9cae      sub_4efa30()",
		"004d9cb8      data_126094c = 0",
		'004d9cc2      sub_4c8270("play")',
		'004d9ccc      sub_4c8270("music")',
		'004d9cd6      sub_4c8270("s_list")',
		'004d9ce0      sub_4c8270("s_info")',
		'004d9cea      sub_4c8270("s_stop")',
		"004dba70  data_126094c = 1",
		"004dba75  data_1260934 = 1",
		"004dba7a  data_1260928 = 0",
		"004dba80  sub_4c95e0(&data_12c5950, 0, 0x200)",
		"004dbab5      sub_4da3e0()",
		"004dbad0    void sub_4dbad0()",
		"004dbafb      sub_4da3e0()",
		"004dbb00  data_1260934 = 1",
	):
		assert expected in hlil

	for expected in (
		"Com_Memset( s_channels, 0, sizeof( s_channels ) );",
		"while (--q > p) {",
		"*(channel_t **)q = q-1;",
		"*(channel_t **)q = NULL;",
		"freelist = p + MAX_CHANNELS - 1;",
		'Com_DPrintf("Channel memory manager started\\n");',
	):
		assert expected in channel_setup_block

	assert "s_channelInitPrinted" not in channel_setup_block
	assert 'if ( !s_channelInitPrinted ) {' not in channel_setup_block

	for expected in (
		"SND_shutdown();",
		"SNDDMA_Shutdown();",
		"s_soundStarted = 0;",
		'Cmd_RemoveCommand("play");',
		'Cmd_RemoveCommand("music");',
		'Cmd_RemoveCommand("s_list");',
		'Cmd_RemoveCommand("s_info");',
		'Cmd_RemoveCommand("s_stop");',
	):
		assert expected in shutdown_block

	for expected in (
		"s_soundStarted = 1;",
		"s_soundMuted = 1;",
		"s_numSfx = 0;",
		"Com_Memset(sfxHash, 0, sizeof(sfx_t *)*LOOP_HASH);",
		"s_soundtime = 0;",
		"s_paintedtime = 0;",
		"S_StopAllSounds ();",
		"S_SoundInfo_f();",
	):
		assert expected in init_block

	assert "//\t\ts_numSfx = 0;" not in init_block
	assert "S_StopAllSounds();" in disable_block
	assert "s_soundMuted = qtrue;" in disable_block


def test_channel_freelist_helpers_match_retail_alloc_and_free_paths() -> None:
	hlil = _read(QL_STEAM_HLIL)
	source = _read(SND_DMA)
	snd_local = _read(SND_LOCAL)
	free_block = _function_block(source, "void S_ChannelFree")
	malloc_block = _function_block(source, "channel_t*\tS_ChannelMalloc")
	setup_block = _function_block(source, "void S_ChannelSetup()")
	start_block = _function_block(source, "static void S_StartSoundInternal")
	scan_block = _function_block(source, "qboolean S_ScanChannelStarts")

	for expected in (
		"004d9c50    void* sub_4d9c50()",
		"004d9c5c  sub_4c95e0(&data_14298c0, 0, 0x1500)",
		"004d9c7c  for (i = &data_142ad88; i u> &data_14298c0; i -= 0x38)",
		"004d9c83  *i = 0",
		"004d9c89  data_12c5b78 = &data_142ad88",
		"004da11b      int32_t* edi_1 = data_12c5b78",
		"004da123      if (edi_1 == 0)",
		"004da127          data_12c5b78 = *edi_1",
		"004da131          *edi_1 = sub_4caf40()",
		"004da2ce              edi_1 = ecx_3",
		"004da2d0              *ecx_3 = eax_5",
		"004da31d          edi_1[1] = 0x7fffffff",
		"004dae35  void* ebx = data_12c5b78",
		"004dae75              *(ecx_1 - 0x28) = ebx",
		"004dae78              *ecx_1 = 0",
		"004dae7e              ebx = ecx_1 - 0x28",
		"004dafc2  data_12c5b78 = ebx",
	):
		assert expected in hlil

	for expected in (
		"int\t\t\tallocTime;",
		"int\t\t\tstartSample;",
		"sfx_t\t\t*thesfx;",
	):
		assert expected in snd_local

	for expected in (
		"v->thesfx = NULL;",
		"*(channel_t **)v = freelist;",
		"freelist = (channel_t*)v;",
	):
		assert expected in free_block
	assert "Com_Memset( v, 0, sizeof( *v ) );" not in free_block

	for expected in (
		"if (freelist == NULL) {",
		"return NULL;",
		"v = freelist;",
		"freelist = *(channel_t **)freelist;",
		"v->allocTime = Com_Milliseconds();",
		"return v;",
	):
		assert expected in malloc_block

	for expected in (
		"Com_Memset( s_channels, 0, sizeof( s_channels ) );",
		"*(channel_t **)q = q-1;",
		"*(channel_t **)q = NULL;",
		"freelist = p + MAX_CHANNELS - 1;",
	):
		assert expected in setup_block

	assert "ch = S_ChannelMalloc();" in start_block
	assert "if (!ch) {" in start_block
	assert "ch->allocTime = sfx->lastTimeUsed;" in start_block
	assert "S_ChannelFree(ch);" in scan_block


def test_sound_spatializer_uses_retail_max_distance_falloff() -> None:
	hlil = _read(QL_STEAM_HLIL)
	source = _read(SND_DMA)
	spatialize_block = _function_block(source, "void S_SpatializeOrigin")

	for expected in (
		"004d9ef0    int32_t sub_4d9ef0(int32_t* arg1 @ esi, int32_t* arg2 @ edi, float* arg3, int32_t arg4)",
		"004d9f35  long double x87_r7_7 = fconvert.t(1250f)",
		"004d9f3b  long double x87_r6 = fconvert.t(fconvert.s(sub_4d8190(&var_14)))",
		"004d9f47  if ((eax_3:1.b & 1) == 0)",
		"004d9f49      *arg1 = 0",
		"004d9f51      *arg2 = 0",
		"004d9f72  float var_28_1 = fconvert.s(x87_r7_7 * fconvert.t(0.00079999997979030013))",
		"004d9f75  if (data_142c320 == 1)",
		"004d9fa5  sub_4d7cb0(&var_14, &data_12c5b50, &var_20)",
		"004da013      sub_526000(fconvert.t(fconvert.s(fconvert.t(var_2c) * x87_r7_17)) * x87_r5_2)",
	):
		assert expected in hlil

	for expected in (
		"#define\t\tSOUND_MAXDISTANCE\t1250.0f",
		"#define\t\tSOUND_ATTENUATE\t\t0.0008f",
	):
		assert expected in source

	for expected in (
		"dist = VectorNormalize(source_vec);",
		"if ( dist >= SOUND_MAXDISTANCE ) {",
		"*left_vol = 0;",
		"*right_vol = 0;",
		"return;",
		"dist *= dist_mult;",
		"if (dma.channels == 1)",
		"rscale = 0.5 * (1.0 + dot);",
		"lscale = 0.5 * (1.0 - dot);",
		"scale = (1.0 - dist) * rscale;",
		"scale = (1.0 - dist) * lscale;",
	):
		assert expected in spatialize_block

	assert "SOUND_FULLVOLUME" not in source
	assert "dist -= SOUND_FULLVOLUME;" not in spatialize_block
	assert "#define\t\tSOUND_FULLVOLUME\t80" not in source


def test_start_sound_volume_reconstructs_retail_duplicate_and_steal_policy() -> None:
	hlil = _read(QL_STEAM_HLIL)
	source = _read(SND_DMA)
	start_block = _function_block(source, "static void S_StartSoundInternal")
	start_wrapper_block = _function_block(source, "void S_StartSound( vec3_t origin, int entityNum, int entchannel, sfxHandle_t sfxHandle )")
	start_volume_block = _function_block(source, "void S_StartSoundVolume")

	for expected in (
		"004da050    void sub_4da050(float* arg1, int32_t arg2, int32_t arg3, int32_t arg4, float arg5)",
		'char const data_54401c[0x28] = "^3S_StartSound: handle %i out of range\\n", 0',
		'char const data_544050[0x1b] = "double sound start: %d %s\\n", 0',
		'char const data_544078[0x1f] = "S_StartSound: bad entitynum %i", 0',
		"004da0fa      if (arg2 != 0x3fe)",
		'004da142                  sub_4c9ab0("double sound start: %d %s\\n")',
		"004da172              if (*(edx_2 - 4) == arg2 && *edx_2 != 7",
		"004da243              if (*(edx_3 - 0x30) == 0x3fe",
		"004da309          int32_t eax_10 =",
		"004da309              sub_526000(fconvert.t(fconvert.s(fconvert.t(arg5) * fconvert.t(127.0))))",
		"004da30e          edi_1[4] = eax_10",
		"004da311          edi_1[5] = eax_10",
		"004da350    int32_t sub_4da350(float* arg1, int32_t arg2, int32_t arg3, int32_t arg4)",
		"004da372  return sub_4da050(arg1, arg2, arg3, arg4, fconvert.s(float.t(1)))",
		"004da380    void sub_4da380(int32_t arg1, int32_t arg2, float arg3)",
		"004da3b9          sub_4da050(nullptr, data_1260948, arg2, arg1, fconvert.s(fconvert.t(arg3)))",
		"004db3f0    void sub_4db3f0(int32_t arg1, int32_t arg2)",
		"004db428          sub_4da050(nullptr, data_1260948, arg2, arg1, fconvert.s(float.t(1)))",
	):
		assert expected in hlil

	for expected in (
		'Com_Error( ERR_DROP, "S_StartSound: bad entitynum %i", entityNum );',
		'Com_Printf( S_COLOR_YELLOW "S_StartSound: handle %i out of range\\n", sfxHandle );',
		"if ( entityNum != ENTITYNUM_WORLD ) {",
		"if ( ch->entnum == entityNum && ch->thesfx == sfx ) {",
		"if ( time - ch->allocTime < 50 ) {",
		'Com_DPrintf( "double sound start: %d %s\\n", entityNum, sfx->soundName );',
		"if (ch->entnum == entityNum && ch->allocTime<oldest && ch->entchannel != CHAN_ANNOUNCER) {",
		"if (ch->entnum == ENTITYNUM_WORLD && ch->allocTime<oldest) {",
		"ch->master_vol = (int)( volume * 127.0f );",
		"ch->startSample = START_SAMPLE_IMMEDIATE;",
		"ch->leftvol = ch->master_vol;",
		"ch->rightvol = ch->master_vol;",
		"ch->doppler = qfalse;",
	):
		assert expected in start_block

	assert "S_StartSoundInternal( origin, entityNum, entchannel, sfxHandle, 1.0f );" in start_wrapper_block
	assert "S_StartSoundInternal( origin, entityNum, entchannel, sfxHandle, volume );" in start_volume_block
	for removed_helper in (
		"S_ChannelVolumeScale",
		"S_ChannelMasterVolume",
		"S_ChannelMasterVolumeScaled",
	):
		assert removed_helper not in source

	for legacy in (
		"int\t\t\tinplay;",
		"int\t\t\tallowed;",
		"allowed = 4;",
		"if (inplay>allowed) {",
		'Com_Printf("dropping sound\\n");',
		'Com_Printf( S_COLOR_YELLOW, "S_StartSound: handle %i out of range\\n", sfxHandle );',
		"S_ChannelVolumeScale",
		"S_ChannelMasterVolume",
		"Com_Clamp( 0.0f, 255.0f, 127.0f",
		"s_announcerVolume->value",
		"s_voiceVolume->value",
	):
		assert legacy not in start_block


def test_local_and_loop_warning_paths_preserve_retail_yellow_diagnostics() -> None:
	hlil = _read(QL_STEAM_HLIL)
	source = _read(SND_DMA)
	local_block = _function_block(source, "void S_StartLocalSound( sfxHandle_t sfxHandle, int channelNum )")
	local_volume_block = _function_block(source, "void S_StartLocalSoundVolume")
	loop_block = _function_block(source, "void S_AddLoopingSound")
	real_loop_block = _function_block(source, "void S_AddRealLoopingSound")

	for expected in (
		'char const data_544098[0x2d] = "^3S_StartLocalSound: handle %i out of range\\n", 0',
		'char const data_5440c8[0x2d] = "^3S_AddLoopingSound: handle %i out of range\\n", 0',
		"004da393  if (data_126094c != 0 && data_1260934 == 0)",
		"004da3a2      if (arg1 s>= 0 && arg1 s< data_1260928)",
		"004da3b9          sub_4da050(nullptr, data_1260948, arg2, arg1, fconvert.s(fconvert.t(arg3)))",
		"004da522    void sub_4da522(int32_t* arg1 @ ebp, int32_t arg2 @ esi, int32_t arg3)",
		"004da575  *(ecx_1 + 0x12b8978) = 0",
		"004da57f  long double x87_r7_6 = float.t(1)",
		"004da587  *(ecx_1 + 0x12b8980) = fconvert.s(x87_r7_6)",
		"004da58d  *(ecx_1 + &data_12b897c) = fconvert.s(x87_r7_6)",
		"004da6e1      sub_4c9860(arg4, \"^3S_AddLoopingSound: handle %i o…\")",
		"004db403  if (data_126094c != 0 && data_1260934 == 0)",
		"004db412      if (arg1 s>= 0 && arg1 s< data_1260928)",
		"004db428          sub_4da050(nullptr, data_1260948, arg2, arg1, fconvert.s(float.t(1)))",
		"004db438      sub_4c9860(esi, \"^3S_StartLocalSound: handle %i o…\")",
	):
		assert expected in hlil

	for block in (local_block, local_volume_block):
		assert 'Com_Printf( S_COLOR_YELLOW "S_StartLocalSound: handle %i out of range\\n", sfxHandle );' in block
		assert 'Com_Printf( S_COLOR_YELLOW, "S_StartLocalSound: handle %i out of range\\n", sfxHandle );' not in block

	_assert_order(
		local_block,
		"if ( !s_soundStarted || s_soundMuted ) {",
		"return;",
		"if ( sfxHandle < 0 || sfxHandle >= s_numSfx ) {",
		'Com_Printf( S_COLOR_YELLOW "S_StartLocalSound: handle %i out of range\\n", sfxHandle );',
		"S_StartSound( NULL, listener_number, channelNum, sfxHandle );",
	)
	_assert_order(
		local_volume_block,
		"if ( !s_soundStarted || s_soundMuted ) {",
		"return;",
		"if ( sfxHandle < 0 || sfxHandle >= s_numSfx ) {",
		'Com_Printf( S_COLOR_YELLOW "S_StartLocalSound: handle %i out of range\\n", sfxHandle );',
		"S_StartSoundVolume( NULL, listener_number, channelNum, sfxHandle, volume );",
	)

	assert 'Com_Printf( S_COLOR_YELLOW "S_AddLoopingSound: handle %i out of range\\n", sfxHandle );' in loop_block
	assert 'Com_Printf( S_COLOR_YELLOW, "S_AddLoopingSound: handle %i out of range\\n", sfxHandle );' not in loop_block
	assert 'Com_Printf( S_COLOR_YELLOW "S_AddRealLoopingSound: handle %i out of range\\n", sfxHandle );' in real_loop_block
	assert 'Com_Printf( S_COLOR_YELLOW, "S_AddRealLoopingSound: handle %i out of range\\n", sfxHandle );' not in real_loop_block
	assert "loopSounds[entityNum].active = qtrue;" in real_loop_block
	assert "loopSounds[entityNum].kill = qfalse;" in real_loop_block
	assert "loopSounds[entityNum].doppler = qfalse;" in real_loop_block
	assert "loopSounds[entityNum].oldDopplerScale = 1.0;" in real_loop_block
	assert "loopSounds[entityNum].dopplerScale = 1.0;" in real_loop_block
	assert "loopSounds[entityNum].framenum = cls.framecount;" in real_loop_block


def test_looping_sound_state_paths_preserve_retail_clear_merge_and_compat_frame_contract() -> None:
	aliases = json.loads(_read(ALIASES))["quakelive_steam_srp"]
	rows = _function_rows()
	hlil = _read(QL_STEAM_HLIL)
	source = _read(SND_DMA)
	cl_cgame = _read(CL_CGAME)
	ql_imports = _read(QL_CGAME_IMPORTS)
	cg_public = _read(CG_PUBLIC)
	cg_syscalls = _read(CG_SYSCALLS)

	stop_loop_block = _function_block(source, "void S_StopLoopingSound")
	clear_buffer_block = _function_block(source, "void S_ClearSoundBuffer( void )")
	frame_clear_block = _function_block(source, "void S_ClearLoopingSoundsFrame( void )")
	clear_loops_block = _function_block(source, "void S_ClearLoopingSounds")
	add_loop_block = _function_block(source, "void S_AddLoopingSound")
	real_loop_block = _function_block(source, "void S_AddRealLoopingSound")
	add_loop_sounds_block = _function_block(source, "void S_AddLoopSounds")
	legacy_cgame_import_block = _function_block(cl_cgame, "static int CL_CgameSystemCallsImpl")
	native_frame_clear_block = _function_block(cl_cgame, "static void QDECL QL_CG_trap_S_ClearLoopingSoundsFrame")
	native_killall_block = _function_block(cl_cgame, "static void QDECL QL_CG_trap_S_ClearLoopingSoundsKillAll")
	legacy_real_loop_import_block = _function_block(ql_imports, "static void QDECL QL_CG_trap_S_AddRealLoopingSound")

	assert aliases["sub_4DA3E0"] == "S_ClearSoundBuffer"
	assert rows["FUN_004da3e0"]["size"] == "163"
	assert aliases["sub_4DA490"] == "S_ClearLoopingSoundsFrame"
	assert aliases["j_sub_4DA490"] == "QLCGImport_S_ClearLoopingSoundsFrame"
	assert aliases["j_sub_4DA3E0"] == "QLCGImport_S_ClearLoopingSoundsKillAll"
	assert aliases["sub_4DA4C0"] == "S_AddLoopingSound"
	assert rows["FUN_004da4c0"]["size"] == "558"
	assert aliases["sub_4DA6F0"] == "S_AddLoopSounds"
	assert rows["FUN_004da6f0"]["size"] == "328"
	assert "FUN_004da522" not in rows

	_assert_order(
		hlil,
		"004da3e0    void sub_4da3e0()",
		"004da490    void* sub_4da490()",
		"004da4c0    void sub_4da4c0(int32_t arg1, float* arg2, float* arg3, int32_t arg4)",
		"004da522    void sub_4da522(int32_t* arg1 @ ebp, int32_t arg2 @ esi, int32_t arg3)",
		"004da6f0    void* sub_4da6f0()",
	)

	for expected in (
		"004da3fa  sub_4c95e0(&data_12b8950, 0, 0xd000)",
		"004da40b  sub_4c95e0(&data_142ade0, 0, 0x1500)",
		"004da410  data_142c2f0 = 0",
		"004da41a  sub_4d9c50()",
		"004da42b  data_13e1850 = 0",
		"004da435  sub_4c95e0(&data_13e1860, 0, 0x2803c)",
		"004da4ae  for (i = &data_12b8964; i s< 0x12c5964; i += 0x34)",
		"004da4a0      *i = 0",
		"004da4b0  data_142c2f0 = 0",
		"004da536          *(ecx_1 + &data_12b8950) = fconvert.s(fconvert.t(*arg2))",
		"004da565          *(ecx_1 + &data_12b8964) = 1",
		"004da575          *(ecx_1 + 0x12b8978) = 0",
		"004da587          *(ecx_1 + 0x12b8980) = fconvert.s(x87_r7_6)",
		"004da58d          *(ecx_1 + &data_12b897c) = fconvert.s(x87_r7_6)",
		"004da6d0  *(ecx_1 + 0x12b8968) = data_1528cc0.d",
		"004da6fb  data_142c2f0 = 0",
		"004da706  data_1260938 += 1",
		"004da717  void* i_1 = &data_12b897c",
		"004da724      if (*(i - 0x18) != 0)",
		"004da732          if (*(i - 0x1c) != result)",
		"004da744              sub_4d9ef0(&var_8, &var_c, i - 0x2c, 0x7f)",
		"004da777                      if (*(j - 0x14) != 0 && *j == 0 && *(j - 0x1c) == *(i_1 - 0x20))",
		"004da78a                          *(j - 0x18) = data_1260938",
		"004da7e1                  if (edx_5 s> 0xff)",
		"004da7eb                  if (var_8 s> 0xff)",
		"004da808                  *(result + 0x28) = edx_7",
		"004da80e                  *(result + 0x2c) = *(i - 4)",
		"004da811                  data_142c2f0 = ecx_5 + 1",
		"004da81a                  if (ecx_5 == 0x5f)",
	):
		assert expected in hlil

	_assert_order(
		clear_buffer_block,
		"Com_Memset(loopSounds, 0, MAX_GENTITIES*sizeof(loopSound_t));",
		"Com_Memset(loop_channels, 0, MAX_CHANNELS*sizeof(channel_t));",
		"numLoopChannels = 0;",
		"S_ChannelSetup();",
		"s_rawend = 0;",
		"Com_Memset( s_voiceChannels, 0, sizeof( s_voiceChannels ) );",
	)
	_assert_order(
		stop_loop_block,
		"loopSounds[entityNum].active = qfalse;",
		"loopSounds[entityNum].kill = qfalse;",
	)
	_assert_order(
		frame_clear_block,
		"for ( i = 0 ; i < MAX_GENTITIES ; i++) {",
		"loopSounds[i].active = qfalse;",
		"numLoopChannels = 0;",
	)
	assert "loopSounds[i].kill = qfalse;" not in frame_clear_block
	assert "S_StopLoopingSound(i);" not in frame_clear_block
	_assert_order(
		clear_loops_block,
		"if (killall || loopSounds[i].kill == qtrue || (loopSounds[i].sfx && loopSounds[i].sfx->soundLength == 0)) {",
		"loopSounds[i].kill = qfalse;",
		"S_StopLoopingSound(i);",
		"numLoopChannels = 0;",
	)

	_assert_order(
		add_loop_block,
		"if ( !s_soundStarted || s_soundMuted ) {",
		'Com_Printf( S_COLOR_YELLOW "S_AddLoopingSound: handle %i out of range\\n", sfxHandle );',
		"if (sfx->inMemory == qfalse) {",
		'Com_Error( ERR_DROP, "%s has length 0", sfx->soundName );',
		"VectorCopy( origin, loopSounds[entityNum].origin );",
		"VectorCopy( velocity, loopSounds[entityNum].velocity );",
		"loopSounds[entityNum].active = qtrue;",
		"loopSounds[entityNum].kill = qtrue;",
		"loopSounds[entityNum].doppler = qfalse;",
		"loopSounds[entityNum].oldDopplerScale = 1.0;",
		"loopSounds[entityNum].dopplerScale = 1.0;",
		"loopSounds[entityNum].sfx = sfx;",
		"if (s_doppler->integer && VectorLengthSquared(velocity)>0.0) {",
		"loopSounds[entityNum].doppler = qtrue;",
		"if ((loopSounds[entityNum].framenum+1) != cls.framecount) {",
		"loopSounds[entityNum].dopplerScale = lenb/(lena*100);",
		"loopSounds[entityNum].framenum = cls.framecount;",
	)
	_assert_order(
		real_loop_block,
		"if ( !s_soundStarted || s_soundMuted ) {",
		'Com_Printf( S_COLOR_YELLOW "S_AddRealLoopingSound: handle %i out of range\\n", sfxHandle );',
		"if (sfx->inMemory == qfalse) {",
		'Com_Error( ERR_DROP, "%s has length 0", sfx->soundName );',
		"VectorCopy( origin, loopSounds[entityNum].origin );",
		"VectorCopy( velocity, loopSounds[entityNum].velocity );",
		"loopSounds[entityNum].sfx = sfx;",
		"loopSounds[entityNum].active = qtrue;",
		"loopSounds[entityNum].kill = qfalse;",
		"loopSounds[entityNum].doppler = qfalse;",
		"loopSounds[entityNum].oldDopplerScale = 1.0;",
		"loopSounds[entityNum].dopplerScale = 1.0;",
		"loopSounds[entityNum].framenum = cls.framecount;",
	)

	_assert_order(
		add_loop_sounds_block,
		"numLoopChannels = 0;",
		"time = Com_Milliseconds();",
		"loopFrame++;",
		"for ( i = 0 ; i < MAX_GENTITIES ; i++) {",
		"loop = &loopSounds[i];",
		"if ( !loop->active || loop->mergeFrame == loopFrame ) {",
		"S_SpatializeOrigin( loop->origin, 127, &left_total, &right_total);",
		"loop->sfx->lastTimeUsed = time;",
		"for (j=(i+1); j< MAX_GENTITIES ; j++) {",
		"if ( !loop2->active || loop2->doppler || loop2->sfx != loop->sfx) {",
		"loop2->mergeFrame = loopFrame;",
		"S_SpatializeOrigin( loop2->origin, 127, &left, &right);",
		"left_total += left;",
		"right_total += right;",
		"if (left_total == 0 && right_total == 0) {",
		"ch = &loop_channels[numLoopChannels];",
		"if (left_total > 255) {",
		"if (right_total > 255) {",
		"ch->master_vol = 127;",
		"ch->leftvol = left_total;",
		"ch->rightvol = right_total;",
		"ch->thesfx = loop->sfx;",
		"ch->doppler = loop->doppler;",
		"ch->dopplerScale = loop->dopplerScale;",
		"ch->oldDopplerScale = loop->oldDopplerScale;",
		"numLoopChannels++;",
		"if (numLoopChannels == MAX_CHANNELS) {",
	)
	assert "S_SpatializeOrigin( loop->origin, 90" not in add_loop_sounds_block
	assert "loop2->doppler || loop2->sfx != loop->sfx" in add_loop_sounds_block

	assert "case CG_S_CLEARLOOPINGSOUNDS:" in legacy_cgame_import_block
	assert "S_ClearLoopingSounds( args[1] ? qtrue : qfalse );" in legacy_cgame_import_block
	assert "case CG_S_ADDREALLOOPINGSOUND:" in legacy_cgame_import_block
	assert "S_AddRealLoopingSound( args[1], VMA(2), VMA(3), args[4] );" in legacy_cgame_import_block
	assert "S_ClearLoopingSoundsFrame();" in native_frame_clear_block
	assert "S_ClearSoundBuffer();" in native_killall_block
	assert "CG_Import_Syscall( CG_S_ADDREALLOOPINGSOUND, entityNum, origin, velocity, sfx );" in legacy_real_loop_import_block
	assert "CG_S_ADDREALLOOPINGSOUND" in cg_public
	assert "syscall( CG_S_ADDREALLOOPINGSOUND, entityNum, origin, velocity, sfx );" in cg_syscalls


def test_sound_buffer_loop_raw_and_update_helpers_match_retail_wiring() -> None:
	hlil = _read(QL_STEAM_HLIL)
	source = _read(SND_DMA)
	clear_buffer_block = _function_block(source, "void S_ClearSoundBuffer( void )")
	frame_clear_block = _function_block(source, "void S_ClearLoopingSoundsFrame( void )")
	clear_loops_block = _function_block(source, "void S_ClearLoopingSounds")
	add_loop_block = _function_block(source, "void S_AddLoopingSound")
	add_loop_sounds_block = _function_block(source, "void S_AddLoopSounds")
	raw_block = _function_block(source, "void S_RawSamples")
	position_block = _function_block(source, "void S_UpdateEntityPosition")
	pvs_block = _function_block(source, "static qboolean S_OriginInPVS")
	respatialize_block = _function_block(source, "void S_Respatialize")
	scan_block = _function_block(source, "qboolean S_ScanChannelStarts")
	update_block = _function_block(source, "void S_Update( void )")
	soundtime_block = _function_block(source, "int S_GetSoundtime(void)")
	update_paint_block = _function_block(source, "void S_Update_(void)")

	for expected in (
		"004da3e0    void sub_4da3e0()",
		"004da490    void* sub_4da490()",
		"004da4a0      *i = 0",
		"004da4b0  data_142c2f0 = 0",
		"004da4c0    void sub_4da4c0(int32_t arg1, float* arg2, float* arg3, int32_t arg4)",
		"004da6f0    void* sub_4da6f0()",
		"sub_4d9ef0(&var_8, &var_c, i - 0x2c, 0x7f)",
		"sub_4d9ef0(&var_20, &var_1c, j - 0x28, 0x7f)",
		"004da840    void sub_4da840(int32_t arg1, int32_t arg2, int32_t arg3, int32_t arg4, int32_t arg5, float arg6)",
		"004da876      int32_t eax_2 = sub_526000(fconvert.t(*(data_13e185c + 0x2c)) * fconvert.t(arg6)",
		"* fconvert.t(256.0))",
		'char const data_544108[0x22] = "S_RawSamples: overflowed %i > %i\\n", 0',
		'char const data_54412c[0x2a] = "S_RawSamples: resetting minimum: %i < %i\\n", 0',
		"004db9d9  data_13e185c =",
		'004db9d9      sub_4cdd30(x87_r2, x87_r3, x87_r4, "s_volume", "0.8", "0.0", "2.0", 0x81801)',
		"004dac80    void* sub_4dac80(int32_t arg1, float* arg2)",
		'char const data_544270[0x29] = "S_UpdateEntityPosition: bad entitynum %i", 0',
		"004dacd0    float* sub_4dacd0(int32_t arg1, float* arg2, float* arg3, int32_t arg4)",
		"004dadd7                  if (*(data_13e1858 + 0x30) != 0)",
		"004dade2                      eax_5 = data_146ccd4(&data_126093c, &var_14)",
		"004daded                  if (*(data_13e1858 + 0x30) == 0 || eax_5 != 0)",
		"004dae03                      sub_4d9ef0(ebx_1 - 0x10, ebx_1 - 0x14, &var_14, 0x7f)",
		"004dadef                      *(ebx_1 - 0x14) = 0",
		"004dadf2                      *(ebx_1 - 0x10) = 0",
		"004dae19      result = sub_4da6f0()",
		"004dae30    int32_t sub_4dae30()",
		"004dae35  void* ebx = data_12c5b78",
		"004dae3c  int32_t esi = data_142c2ec",
		"004dae43  int32_t result = 0",
		"004dae45  void* ecx_1 = &data_14298e8",
		"004dae4a  int32_t i_1 = 0x10",
		"004dae60          if (edx_1 == 0x7fffffff)",
		"004dae62              *(ecx_1 - 0x24) = esi",
		"004dae65              result = 1",
		"004dae60          else if (*(edi_1 + 0xc) + edx_1 s<= esi)",
		"004dae75              *(ecx_1 - 0x28) = ebx",
		"004dae78              *ecx_1 = 0",
		"004dae7e              ebx = ecx_1 - 0x28",
		"004dafb1      ecx_1 += 0x150",
		"004dafc2  data_12c5b78 = ebx",
		"004dafcc  return result",
		"004db490    int32_t sub_4db490()",
		"004db557          return eax_8",
		"004db560  return eax_6",
		"004db570    void sub_4db570()",
		'004db95b  data_13e1858 = sub_4cdd30(x87_r6, x87_r7, x87_r0, "s_pvs", U"0", U"0", U"1", 0x81801)',
		"004db5a6      if (data_142c334 != 0)",
		"004db5b2          if (data_142c2ec s> 0x40000000)",
		"004db5c8          data_142c2e0 = data_142c2ec",
		"004db5d2          esi_1 = sub_4efb80()",
		"004db5d6      sub_4db490()",
		"004db655          sub_4efbf0()",
		"004db680    void sub_4db680()",
		"004db690  if (data_126094c == 0 || data_1260934 != 0)",
		"004db69b  if (*(data_142c2fc + 0x30) == 2)",
		'004db6cf                  sub_4c9860(esi_1, "%3i %3i %s\\n")',
		'char const data_5443ac[0xc] = "%3i %3i %s\\n", 0',
		'char const data_544390[0x1a] = "----(%i)---- painted: %i\\n", 0',
		'00544460  char const data_544460[0x6] = "s_pvs", 0',
		'004db6f6  sub_4db1c0()',
		"004db6fb  return sub_4db570() __tailcall",
	):
		assert expected in hlil

	for expected in (
		"Com_Memset(loopSounds, 0, MAX_GENTITIES*sizeof(loopSound_t));",
		"Com_Memset(loop_channels, 0, MAX_CHANNELS*sizeof(channel_t));",
		"S_ChannelSetup();",
		"s_rawend = 0;",
		"Com_Memset( s_voiceChannels, 0, sizeof( s_voiceChannels ) );",
		"SNDDMA_BeginPainting ();",
		"Snd_Memset(dma.buffer, clear, dma.samples * dma.samplebits/8);",
		"SNDDMA_Submit ();",
	):
		assert expected in clear_buffer_block

	for expected in (
		"loopSounds[i].active = qfalse;",
		"numLoopChannels = 0;",
	):
		assert expected in frame_clear_block
	assert "loopSounds[i].kill = qfalse;" not in frame_clear_block
	assert "S_StopLoopingSound(i);" not in frame_clear_block

	for expected in (
		"if (killall || loopSounds[i].kill == qtrue || (loopSounds[i].sfx && loopSounds[i].sfx->soundLength == 0)) {",
		"S_StopLoopingSound(i);",
		"numLoopChannels = 0;",
	):
		assert expected in clear_loops_block

	for expected in (
		"VectorCopy( origin, loopSounds[entityNum].origin );",
		"VectorCopy( velocity, loopSounds[entityNum].velocity );",
		"loopSounds[entityNum].active = qtrue;",
		"loopSounds[entityNum].kill = qtrue;",
		"loopSounds[entityNum].oldDopplerScale = 1.0;",
		"if (s_doppler->integer && VectorLengthSquared(velocity)>0.0) {",
		"loopSounds[entityNum].framenum = cls.framecount;",
	):
		assert expected in add_loop_block

	for expected in (
		"S_SpatializeOrigin( loop->origin, 127, &left_total, &right_total);",
		"S_SpatializeOrigin( loop2->origin, 127, &left, &right);",
	):
		assert expected in add_loop_sounds_block
	assert "S_SpatializeOrigin( loop->origin, 90" not in add_loop_sounds_block
	assert "S_SpatializeOrigin( loop2->origin, 90" not in add_loop_sounds_block

	for expected in (
		'Com_DPrintf( "S_RawSamples: resetting minimum: %i < %i\\n", s_rawend, s_soundtime );',
		"scale = (float)rate / dma.speed;",
		"intVolume = 256 * volume * s_volume->value;",
		"intVolume *= 256;",
		'Com_DPrintf( "S_RawSamples: overflowed %i > %i\\n", s_rawend, s_soundtime );',
	):
		assert expected in raw_block
	assert "intVolume = 256 * volume;" not in raw_block

	assert 'Com_Error( ERR_DROP, "S_UpdateEntityPosition: bad entitynum %i", entityNum );' in position_block
	assert "VectorCopy( origin, loopSounds[entityNum].origin );" in position_block

	for expected in (
		"listenerLeaf = CM_PointLeafnum( listener );",
		"originLeaf = CM_PointLeafnum( origin );",
		"listenerCluster = CM_LeafCluster( listenerLeaf );",
		"originCluster = CM_LeafCluster( originLeaf );",
		"if ( listenerCluster < 0 || originCluster < 0 ) {",
		"return qfalse;",
		"mask = CM_ClusterPVS( listenerCluster );",
		"if ( !mask ) {",
		"return ( mask[originCluster >> 3] & ( 1 << ( originCluster & 7 ) ) ) ? qtrue : qfalse;",
	):
		assert expected in pvs_block

	for expected in (
		"listener_number = entityNum;",
		"VectorCopy(head, listener_origin);",
		"if ( s_pvs && s_pvs->integer && !S_OriginInPVS( listener_origin, origin ) ) {",
		"ch->leftvol = 0;",
		"ch->rightvol = 0;",
		"continue;",
		"S_SpatializeOrigin (origin, ch->master_vol, &ch->leftvol, &ch->rightvol);",
		"S_AddLoopSounds ();",
	):
		assert expected in respatialize_block
	assert "S_OriginInPVS( origin, listener_origin )" not in respatialize_block

	for expected in (
		"newSamples = qfalse;",
		"ch = s_channels;",
		"for (i=0; i<MAX_CHANNELS ; i++, ch++) {",
		"if ( !ch->thesfx ) {",
		"if ( ch->startSample == START_SAMPLE_IMMEDIATE ) {",
		"ch->startSample = s_paintedtime;",
		"newSamples = qtrue;",
		"continue;",
		"if ( ch->startSample + (ch->thesfx->soundLength) <= s_paintedtime ) {",
		"S_ChannelFree(ch);",
		"return newSamples;",
	):
		assert expected in scan_block
	assert "ch->startSample = s_soundtime;" not in scan_block
	assert "S_ChannelFree(ch);" in scan_block
	assert "S_ChannelFree(ch + i);" not in scan_block

	for expected in (
		"if ( s_show->integer == 2 ) {",
		'Com_Printf ("%3i %3i %s\\n", ch->leftvol, ch->rightvol, ch->thesfx->soundName);',
		'Com_Printf ("----(%i)---- painted: %i\\n", total, s_paintedtime);',
		"S_UpdateBackgroundTrack();",
		"S_Update_();",
	):
		assert expected in update_block
	assert 'Com_DPrintf ("not started or muted\\n");' not in update_block
	assert 'Com_Printf ("%f %f %s\\n", ch->leftvol, ch->rightvol, ch->thesfx->soundName);' not in update_block

	for expected in (
		"S_GetSoundtime();",
		"S_ScanChannelStarts();",
		"ma = s_mixahead->value * dma.speed;",
		"endtime = (endtime + dma.submission_chunk-1)",
		"SNDDMA_BeginPainting ();",
		"S_PaintChannels (endtime);",
		"SNDDMA_Submit ();",
	):
		assert expected in update_paint_block

	for expected in (
		"int S_GetSoundtime(void)",
		"s_soundtime = buffers*fullsamples + samplepos/dma.channels;",
		"if ( dma.submission_chunk < 256 ) {",
		"s_paintedtime = s_soundtime + s_mixPreStep->value * dma.speed;",
		"return s_paintedtime;",
		"s_paintedtime = s_soundtime + dma.submission_chunk;",
		"return s_soundtime;",
	):
		assert expected in soundtime_block


def test_sound_update_timing_and_dma_submit_slice_matches_retail() -> None:
	hlil = _read(QL_STEAM_HLIL)
	source = _read(SND_DMA)
	update_block = _function_block(source, "void S_Update( void )")
	update_paint_block = _function_block(source, "void S_Update_(void)")
	soundtime_block = _function_block(source, "int S_GetSoundtime(void)")

	for expected in (
		"004db490    int32_t sub_4db490()",
		"004db496  int32_t temp0 = divs.dp.d(sx.q(data_142c324), data_142c320)",
		"004db4a0  int32_t eax_2 = sub_4efb80()",
		"004db4ad  if (eax_2 s< data_1260930)",
		"004db4af      data_126092c += 1",
		"004db4bf      if (data_142c2ec s> 0x40000000)",
		"004db4c8          data_126092c = 0",
		"004db4d2          data_142c2ec = temp0",
		"004db4fc              sub_4da3e0()",
		"004db510  int32_t ecx_1 = data_126092c * temp0",
		"004db514  data_1260930 = eax_2",
		"004db524  data_142c2e0 = eax_6",
		"004db537      if (ecx_2 s< 0x100)",
		"004db54d              fconvert.t(*(data_142c300 + 0x2c)) * float.t(data_142c330)",
		"004db552          data_142c2ec = eax_8",
		"004db557          return eax_8",
		"004db55a      data_142c2ec = ecx_2 + eax_6",
		"004db560  return eax_6",
		"004db570    void sub_4db570()",
		"004db58a  if (data_126094c != 0 && data_1260934 == 0)",
		"004db591      eax_1, x87control_1 = sub_4caf40()",
		"004db5a6      if (data_142c334 != 0)",
		"004db5b2          if (data_142c2ec s> 0x40000000)",
		"004db5b4              data_142c2ec = 0",
		"004db5be              sub_4db450()",
		"004db5c8          data_142c2e0 = data_142c2ec",
		"004db5d2          esi_1 = sub_4efb80()",
		"004db5d6      sub_4db490()",
		"004db5f0          fconvert.t(fconvert.s(fconvert.t(*(data_142c2e4 + 0x2c)) * float.t(data_142c330)))",
		"004db61c      if (eax != data_568f04)",
		"004db61e          data_568f04 = eax",
		"004db623          sub_4dae30()",
		"004db63a          void* esi_3 = (eax_6 + esi_1 - 1) & not.d(eax_6 - 1)",
		"004db642          int32_t eax_10 = data_142c324 s>> ((data_142c320).b - 1)",
		"004db650          if (esi_3 - ecx_4 u> eax_10)",
		"004db655          sub_4efbf0()",
		"004db65b          sub_4dc350(esi_3)",
		"004db663          sub_4efd00()",
		"004db66b          data_12c5b7c = fconvert.s(fconvert.t(fconvert.s(float.t(eax_1))))",
		"004db680    void sub_4db680()",
		"004db690  if (data_126094c == 0 || data_1260934 != 0)",
		"004db700      return",
		"004db69b  if (*(data_142c2fc + 0x30) == 2)",
		"004db6a2      void* esi_1 = &data_14298d4",
		"004db6aa      int32_t i_1 = 0x60",
		"004db6c0              if (eax_1 != 0 || *esi_1 != eax_1)",
		"004db6cf                  sub_4c9860(esi_1, \"%3i %3i %s\\n\")",
		"004db6e4      int32_t var_10_2 = data_142c2ec",
		"004db6f6  sub_4db1c0()",
		"004db6fb  return sub_4db570() __tailcall",
	):
		assert expected in hlil

	for expected in (
		"static\tint\t\tbuffers;",
		"static\tint\t\toldsamplepos;",
		"fullsamples = dma.samples / dma.channels;",
		"samplepos = SNDDMA_GetDMAPos();",
		"if (samplepos < oldsamplepos)",
		"buffers++;",
		"if (s_paintedtime > 0x40000000)",
		"buffers = 0;",
		"s_paintedtime = fullsamples;",
		"S_StopAllSounds ();",
		"oldsamplepos = samplepos;",
		"s_soundtime = buffers*fullsamples + samplepos/dma.channels;",
		"if ( dma.submission_chunk < 256 ) {",
		"s_paintedtime = s_soundtime + s_mixPreStep->value * dma.speed;",
		"return s_paintedtime;",
		"s_paintedtime = s_soundtime + dma.submission_chunk;",
		"return s_soundtime;",
	):
		assert expected in soundtime_block

	for expected in (
		"static\t\t\tint ot = -1;",
		"if ( !s_soundStarted || s_soundMuted ) {",
		"S_GetSoundtime();",
		"if (s_soundtime == ot) {",
		"return;",
		"ot = s_soundtime;",
		"S_ScanChannelStarts();",
		"ma = s_mixahead->value * dma.speed;",
		"endtime = s_soundtime + ma;",
		"endtime = (endtime + dma.submission_chunk-1)",
		"& ~(dma.submission_chunk-1);",
		"samps = dma.samples >> (dma.channels-1);",
		"if (endtime - s_soundtime > samps)",
		"endtime = s_soundtime + samps;",
		"SNDDMA_BeginPainting ();",
		"S_PaintChannels (endtime);",
		"SNDDMA_Submit ();",
	):
		assert expected in update_paint_block
	assert update_paint_block.index("S_GetSoundtime();") < update_paint_block.index("S_ScanChannelStarts();")
	assert update_paint_block.index("SNDDMA_BeginPainting ();") < update_paint_block.index("S_PaintChannels (endtime);")
	assert update_paint_block.index("S_PaintChannels (endtime);") < update_paint_block.index("SNDDMA_Submit ();")

	for expected in (
		"if ( !s_soundStarted || s_soundMuted ) {",
		"if ( s_show->integer == 2 ) {",
		'Com_Printf ("%3i %3i %s\\n", ch->leftvol, ch->rightvol, ch->thesfx->soundName);',
		'Com_Printf ("----(%i)---- painted: %i\\n", total, s_paintedtime);',
		"S_UpdateBackgroundTrack();",
		"S_Update_();",
	):
		assert expected in update_block
	assert update_block.index("S_UpdateBackgroundTrack();") < update_block.index("S_Update_();")
	assert "S_PaintChannels (s_soundtime" not in update_paint_block
	assert "endtime = s_soundtime + dma.submission_chunk;" not in update_paint_block
