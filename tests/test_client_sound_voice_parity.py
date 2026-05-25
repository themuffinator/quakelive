"""Guard the retail-backed client sound and Steam voice path against drift."""

from __future__ import annotations

from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parent.parent
CL_CGAME = REPO_ROOT / "src" / "code" / "client" / "cl_cgame.c"
CL_MAIN = REPO_ROOT / "src" / "code" / "client" / "cl_main.c"
PLATFORM_STEAMWORKS = REPO_ROOT / "src" / "common" / "platform" / "platform_steamworks.c"
SND_DMA = REPO_ROOT / "src" / "code" / "client" / "snd_dma.c"
SND_LOCAL = REPO_ROOT / "src" / "code" / "client" / "snd_local.h"
SND_MEM = REPO_ROOT / "src" / "code" / "client" / "snd_mem.c"
SND_MIX = REPO_ROOT / "src" / "code" / "client" / "snd_mix.c"
SND_OGG_DECODE = REPO_ROOT / "src" / "code" / "client" / "snd_ogg_decode.c"
SND_PUBLIC = REPO_ROOT / "src" / "code" / "client" / "snd_public.h"

# Retail console-command owner evidence for this sound slice comes from
# `references/analysis/quakelive_symbol_aliases.json` plus the paired HLIL in
# `references/hlil/quakelive/quakelive_steam.exe/`:
# `sub_4D9B60` -> `S_SoundInfo_f`
# `sub_4DAFD0` -> `S_SoundList_f`
# `sub_4DB710` -> `S_Play_f`
# `sub_4DB810` -> `S_Music_f`


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


def test_sound_console_commands_match_retail_registration_and_output_contracts() -> None:
	snd_dma = SND_DMA.read_text(encoding="utf-8")

	init_block = _extract_function_block(snd_dma, "void S_Init( void ) {")
	shutdown_block = _extract_function_block(snd_dma, "void S_Shutdown( void )")
	info_block = _extract_function_block(snd_dma, "void S_SoundInfo_f(void) {")
	play_block = _extract_function_block(snd_dma, "void S_Play_f( void ) {")
	music_block = _extract_function_block(snd_dma, "void S_Music_f( void ) {")
	list_block = _extract_function_block(snd_dma, "void S_SoundList_f( void ) {")

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
	snd_local = SND_LOCAL.read_text(encoding="utf-8")
	snd_dma = SND_DMA.read_text(encoding="utf-8")
	snd_mix = SND_MIX.read_text(encoding="utf-8")
	add_voice_block = _extract_function_block(
		snd_dma,
		"void S_AddVoiceSamples( int clientNum, int samples, const short *data )",
	)

	assert "#define MAX_VOICE_CHANNELS\t5" in snd_local
	assert "#define VOICE_BUFFER_SAMPLES\t0x4000" in snd_local
	assert "typedef struct {" in snd_local
	assert "short\tsamples[VOICE_BUFFER_SAMPLES];" in snd_local
	assert "voiceChannel_t\ts_voiceChannels[MAX_VOICE_CHANNELS];" in snd_dma
	assert 's_pvs = Cvar_GetBounded( "s_pvs", "0", "0", "1", CVAR_ARCHIVE | CVAR_PROTECTED | CVAR_VM_CREATED | CVAR_CLOUD );' in snd_dma
	assert 's_voiceStep = Cvar_Get( "s_voiceStep", "0.02", CVAR_ARCHIVE | CVAR_PROTECTED );' in snd_dma
	assert "Com_Memset( s_voiceChannels, 0, sizeof( s_voiceChannels ) );" in snd_dma
	assert "if ( voice->endSample <= voice->startSample ) {" in add_voice_block
	assert "startSample = s_paintedtime + (int)( s_mixPreStep->value * dma.speed );" in add_voice_block
	assert "startSample += (int)( s_voiceStep->value * dma.speed );" in add_voice_block
	assert "voice->samples[( voice->endSample + i ) & ( VOICE_BUFFER_SAMPLES - 1 )] = data[i];" in add_voice_block
	assert "voiceScale = (int)( Com_Clamp( 0.0f, 2.0f, s_voiceVolume->value ) * 256.0f );" in snd_mix
	assert "voice->samples[sampleTime & ( VOICE_BUFFER_SAMPLES - 1 )] * voiceScale" in snd_mix
	assert "if ( s_pvs && s_pvs->integer && !S_OriginInPVS( listener_origin, origin ) ) {" in snd_dma


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
	assert "if ( !CL_SteamServicesEnabled() || !QL_Steamworks_Init() ) {" in frame_block
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

	assert 'QL_Steamworks_LoadOptionalSymbol( (void **)&state.SteamNetworking, "SteamAPI_SteamNetworking" );' in load_block
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
	snd_dma = SND_DMA.read_text(encoding="utf-8")
	snd_mem = SND_MEM.read_text(encoding="utf-8")

	shutdown_block = _extract_function_block(snd_dma, "void S_Shutdown( void )")
	begin_block = _extract_function_block(snd_dma, "void S_BeginRegistration( void )")
	load_block = _extract_function_block(snd_mem, "qboolean S_LoadSound( sfx_t *sfx )")

	assert '#define DEF_COMSOUNDMEGS "16"' in snd_mem
	assert "void SND_shutdown( void ) {" in snd_mem
	assert 'Com_Printf("%d bytes sound buffer memory in use, %d free\\n", totalInUse, inUse);' in snd_mem
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
	assert 'COM_DefaultExtension( resolvedName, resolvedNameSize, ".ogg" );' in snd_mem
	assert 'if ( !S_LoadSoundFile( sfx->soundName, loadName, sizeof( loadName ), &data, &size ) ) {' in load_block
	assert 'isOgg = S_IsOggSound( loadName, data, size );' in load_block


def test_background_track_ogg_update_matches_retail_restart_path() -> None:
	snd_dma = SND_DMA.read_text(encoding="utf-8")

	update_helper = _extract_function_block(
		snd_dma,
		"static int S_OggUpdateBackgroundTrack( byte *buffer, int bytesToRead )",
	)
	update_block = _extract_function_block(snd_dma, "void S_UpdateBackgroundTrack( void )")

	assert 'result = S_OggStreamRead( &s_backgroundOgg, buffer, bytesToRead );' in update_helper
	assert 'Com_Printf( S_COLOR_YELLOW "OGG_UpdateBackgroundTrack: %i\\n", result );' in update_helper
	assert "S_OggStreamClose( &s_backgroundOgg );" in update_helper
	assert "return 0;" in update_helper
	assert "r = S_OggUpdateBackgroundTrack( raw, fileBytes );" in update_block
	assert "if ( r < fileBytes ) {" in update_block
	assert "s_backgroundIsOgg = qfalse;" in update_block
	assert "if ( !S_BackgroundTrackLoop() ) {" in update_block
	assert "S_StopBackgroundTrack();" in update_block


def test_vorbis_memory_decode_matches_retail_mono_contract() -> None:
	snd_ogg_decode = SND_OGG_DECODE.read_text(encoding="utf-8")
	enabled_block = snd_ogg_decode.rsplit("#else", 1)[0]
	decode_block = _extract_function_block(
		enabled_block,
		"qboolean S_VorbisDecodeMemory( const char *name, const byte *data, int length, wavinfo_t *info, short **outPcm )",
	)

	assert "static int S_VorbisBufferClose" not in snd_ogg_decode
	assert "callbacks.close_func = S_VorbisBufferClose;" not in snd_ogg_decode
	assert "if ( channels != 1 ) {" in decode_block
	assert 'Com_Printf( "%s is not a mono file\\n", name ? name : "<unnamed>" );' in decode_block
	assert 'Com_Printf( S_COLOR_YELLOW "OGG_Decode: %s: %i\\n", name ? name : "<unnamed>", bytesRead );' in decode_block
	assert "channels > 2" not in decode_block
	assert "stereo Vorbis file and was downmixed to mono" not in snd_ogg_decode
	assert "chunkSamples" not in decode_block
	assert "samplePairs" not in decode_block
	assert "Com_Memcpy( writePtr, decodeChunk, sampleCount * sizeof( short ) );" in decode_block
