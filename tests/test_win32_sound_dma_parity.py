"""Guard the retail-backed Win32 DirectSound DMA host mapping against drift."""

from __future__ import annotations

import csv
import json
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parent.parent
ALIASES = REPO_ROOT / "references" / "analysis" / "quakelive_symbol_aliases.json"
FUNCTIONS_CSV = REPO_ROOT / "references" / "reverse-engineering" / "ghidra" / "quakelive_steam" / "functions.csv"
QL_STEAM_HLIL = REPO_ROOT / "references" / "hlil" / "quakelive" / "quakelive_steam.exe" / "quakelive_steam.exe_hlil.txt"
WIN_SND = REPO_ROOT / "src" / "code" / "win32" / "win_snd.c"


WIN32_SOUND_DMA_ALIASES = {
	"sub_4EF9F0": ("DSoundError", "FUN_004ef9f0", "60"),
	"sub_4EFA30": ("SNDDMA_Shutdown", "FUN_004efa30", "330"),
	"sub_4EFB80": ("SNDDMA_GetDMAPos", "FUN_004efb80", "103"),
	"sub_4EFBF0": ("SNDDMA_BeginPainting", "FUN_004efbf0", "258"),
	"sub_4EFD00": ("SNDDMA_Submit", "FUN_004efd00", "36"),
	"sub_4EFD30": ("SNDDMA_Activate", "FUN_004efd30", "49"),
	"sub_4EFD70": ("SNDDMA_InitDS", "FUN_004efd70", "795"),
	"sub_4F0090": ("SNDDMA_Init", "FUN_004f0090", "93"),
}

WIN32_SOUND_DMA_LOWERCASE_BN_ALIASES = {
	"sub_4ef9f0": "DSoundError",
	"sub_4efa30": "SNDDMA_Shutdown",
	"sub_4efb80": "SNDDMA_GetDMAPos",
	"sub_4efbf0": "SNDDMA_BeginPainting",
	"sub_4efd00": "SNDDMA_Submit",
	"sub_4efd30": "SNDDMA_Activate",
	"sub_4efd70": "SNDDMA_InitDS",
	"sub_4f0090": "SNDDMA_Init",
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


def test_win32_sound_dma_aliases_cover_retail_directsound_cluster() -> None:
	aliases = json.loads(ALIASES.read_text(encoding="utf-8"))["quakelive_steam_srp"]
	function_rows = {
		row["name"]: row
		for row in csv.DictReader(FUNCTIONS_CSV.read_text(encoding="utf-8").splitlines())
	}
	hlil = QL_STEAM_HLIL.read_text(encoding="utf-8")

	for alias, (name, ghidra_name, size) in WIN32_SOUND_DMA_ALIASES.items():
		assert aliases[alias] == name
		assert aliases[ghidra_name] == name
		assert function_rows[ghidra_name]["size"] == size

	for alias, name in WIN32_SOUND_DMA_LOWERCASE_BN_ALIASES.items():
		assert aliases[alias] == name

	for expected in (
		'004ef9f0    int32_t __convention("regparm") sub_4ef9f0(int32_t arg1) __pure',
		'return "DSERR_PRIOLEVELNEEDED"',
		'return "DSERR_INVALIDPARAM"',
		'return "DSERR_INVALIDCALLS"',
		'return "DSERR_BUFFERLOST"',
		'004efa30    int32_t sub_4efa30()',
		'"Shutting down sound system\\n"',
		'"Destroying DS buffers\\n"',
		'"...freeing DSOUND.DLL\\n"',
		'CoUninitialize() __tailcall',
		'004efb80    int32_t sub_4efb80()',
		'data_12d16bc == 0',
		'data_12d16b4).b & (data_142c324 - 1)',
		'004efbf0    int32_t* sub_4efbf0()',
		'"Couldn\'t get sound buffer status',
		'"SNDDMA_BeginPainting: Lock faile',
		'sub_4d9ca0()',
		'004efd00    int32_t* sub_4efd00()',
		'(*(*result + 0x4c))(result, data_142c33c, data_12d16c4, 0, 0)',
		'004efd30    int32_t* sub_4efd30()',
		'"sound SetCooperativeLevel failed',
		'return sub_4efa30() __tailcall',
		'004efd70    int32_t sub_4efd70()',
		'"Initializing DirectSound\\n"',
		'"s_muteBackground"',
		'0x21',
		'if (eax_2[0xc] == 0)',
		'var_40_2 | 0x8000',
		'var_40_4 | 0x8000',
		'"locked hardware.  ok\\n"',
		'"forced to software.  ok\\n"',
		'004f0090    int32_t sub_4f0090()',
		'data_12d16bc = 1',
		'"Completed successfully\\n"',
	):
		assert expected in hlil


def test_win32_sound_dma_source_reconstructs_retail_host_controls() -> None:
	win_snd = WIN_SND.read_text(encoding="utf-8")

	init_block = _extract_function_block(win_snd, "qboolean SNDDMA_Init(void) {")
	init_ds_block = _extract_function_block(win_snd, "int SNDDMA_InitDS ()")
	shutdown_block = _extract_function_block(win_snd, "void SNDDMA_Shutdown( void ) {")
	position_block = _extract_function_block(win_snd, "int SNDDMA_GetDMAPos( void ) {")
	begin_block = _extract_function_block(win_snd, "void SNDDMA_BeginPainting( void ) {")
	submit_block = _extract_function_block(win_snd, "void SNDDMA_Submit( void ) {")
	activate_block = _extract_function_block(win_snd, "void SNDDMA_Activate( void ) {")

	assert 'Com_DPrintf("Completed successfully\\n" );' in init_block
	assert "CoInitialize(NULL);" in init_block
	assert "SNDDMA_InitDS ()" in init_block
	assert 'Com_Printf( "Initializing DirectSound\\n");' in init_ds_block
	assert 'muteBackground = Cvar_Get( "s_muteBackground", "1", CVAR_ARCHIVE | CVAR_LATCH );' in init_ds_block
	assert "dsbuf.dwFlags = DSBCAPS_LOCHARDWARE;" in init_ds_block
	assert "dsbuf.dwFlags = DSBCAPS_LOCSOFTWARE;" in init_ds_block
	assert init_ds_block.count("dsbuf.dwFlags |= DSBCAPS_GLOBALFOCUS;") == 2
	assert init_ds_block.count("if ( !muteBackground->integer ) {") == 2
	assert "DSBCAPS_GETCURRENTPOSITION2" in init_ds_block
	assert "dma.speed = 22050;" in init_ds_block
	assert 'Com_Printf( "locked hardware.  ok\\n" );' in init_ds_block
	assert 'Com_DPrintf( "forced to software.  ok\\n" );' in init_ds_block
	assert "SNDDMA_BeginPainting ();" in init_ds_block
	assert "SNDDMA_Submit ();" in init_ds_block

	assert 'Com_DPrintf( "Shutting down sound system\\n" );' in shutdown_block
	assert 'Com_DPrintf( "Destroying DS buffers\\n" );' in shutdown_block
	assert 'Com_DPrintf( "...freeing DSOUND.DLL\\n" );' in shutdown_block
	assert "CoUninitialize( );" in shutdown_block

	assert "if ( !dsound_init ) {" in position_block
	assert "GetCurrentPosition" in position_block
	assert "s &= (dma.samples-1);" in position_block

	assert "GetStatus" in begin_block
	assert 'Com_Printf ("Couldn\'t get sound buffer status\\n");' in begin_block
	assert "DSBSTATUS_BUFFERLOST" in begin_block
	assert "DSBSTATUS_PLAYING" in begin_block
	assert "DSERR_BUFFERLOST" in begin_block
	assert 'Com_Printf( "SNDDMA_BeginPainting: Lock failed with error' in begin_block
	assert "S_Shutdown ();" in begin_block

	assert "Unlock(pDSBuf, dma.buffer, locksize, NULL, 0)" in submit_block
	assert 'Com_Printf ("sound SetCooperativeLevel failed\\n");' in activate_block
	assert "SNDDMA_Shutdown ();" in activate_block
