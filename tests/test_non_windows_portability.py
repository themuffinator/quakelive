from __future__ import annotations

from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parent.parent
UNIX_MAIN_PATH = REPO_ROOT / "src" / "code" / "unix" / "unix_main.c"
UNIX_NET_PATH = REPO_ROOT / "src" / "code" / "unix" / "unix_net.c"
LINUX_COMMON_PATH = REPO_ROOT / "src" / "code" / "unix" / "linux_common.c"
LINUX_GLIMP_PATH = REPO_ROOT / "src" / "code" / "unix" / "linux_glimp.c"
LINUX_JOYSTICK_PATH = REPO_ROOT / "src" / "code" / "unix" / "linux_joystick.c"
NULL_MAIN_PATH = REPO_ROOT / "src" / "code" / "null" / "null_main.c"
NULL_NET_PATH = REPO_ROOT / "src" / "code" / "null" / "null_net.c"
MAC_NET_PATH = REPO_ROOT / "src" / "code" / "null" / "mac_net.c"
NULL_GLIMP_PATH = REPO_ROOT / "src" / "code" / "null" / "null_glimp.c"
NULL_CLIENT_PATH = REPO_ROOT / "src" / "code" / "null" / "null_client.c"
NULL_SNDDMA_PATH = REPO_ROOT / "src" / "code" / "null" / "null_snddma.c"
NULL_INPUT_PATH = REPO_ROOT / "src" / "code" / "null" / "null_input.c"
UNIX_MAKEFILE_PATH = REPO_ROOT / "src" / "code" / "unix" / "Makefile"
LINUX_SND_PATH = REPO_ROOT / "src" / "code" / "unix" / "linux_snd.c"
BUILD_CLEANROOM_SCRIPT_PATH = REPO_ROOT / "tools" / "ci" / "build-cleanroom.sh"
BUILD_POSIX_NATIVE_SCRIPT_PATH = REPO_ROOT / "tools" / "ci" / "build-posix-native.sh"
RUN_HARNESSES_PATH = REPO_ROOT / "tests" / "run_harnesses.py"
RE_TRACE_HARNESS_PATH = REPO_ROOT / "tools" / "tests" / "re_trace_harness.py"
PUSH_WORKFLOW_PATH = REPO_ROOT / ".github" / "workflows" / "push-verification.yml"
NIGHTLY_WORKFLOW_PATH = REPO_ROOT / ".github" / "workflows" / "nightly-build.yml"
LINUX_GLIBC_32BIT_DOC_PATH = REPO_ROOT / "docs" / "build" / "linux-glibc-32bit.md"
TOOLCHAIN_MATRIX_PATH = REPO_ROOT / "docs" / "platform" / "toolchain-matrix.md"
REVERSE_BUILDS_DOC_PATH = REPO_ROOT / "docs" / "devops" / "reverse-builds.md"
TOOLCHAIN_CI_PATH = REPO_ROOT / "docs" / "toolchain-ci.md"
REPO_WIDE_AUDIT_PATH = (
	REPO_ROOT / "docs" / "reverse-engineering" / "repo-wide-parity-audit-2026-04-21.md"
)
UNIX_MAIN_GAP_NOTE_PATH = (
	REPO_ROOT / "docs" / "reverse-engineering" / "source-file-gap-notes" / "rw-g02-unix-main.md"
)
LINUX_SND_GAP_NOTE_PATH = (
	REPO_ROOT / "docs" / "reverse-engineering" / "source-file-gap-notes" / "rw-g02-linux-snd.md"
)
LINUX_JOYSTICK_GAP_NOTE_PATH = (
	REPO_ROOT / "docs" / "reverse-engineering" / "source-file-gap-notes" / "rw-g02-linux-joystick.md"
)
LINUX_GLIMP_GAP_NOTE_PATH = (
	REPO_ROOT / "docs" / "reverse-engineering" / "source-file-gap-notes" / "rw-g02-linux-glimp.md"
)
NULL_GLIMP_GAP_NOTE_PATH = (
	REPO_ROOT / "docs" / "reverse-engineering" / "source-file-gap-notes" / "rw-g02-null-glimp.md"
)
NULL_INPUT_GAP_NOTE_PATH = (
	REPO_ROOT / "docs" / "reverse-engineering" / "source-file-gap-notes" / "rw-g02-null-input.md"
)
NULL_SNDDMA_GAP_NOTE_PATH = (
	REPO_ROOT / "docs" / "reverse-engineering" / "source-file-gap-notes" / "rw-g02-null-snddma.md"
)


def _read_text(path: Path) -> str:
	return path.read_text(encoding="utf-8", errors="ignore")


def _function_block(text: str, signature: str) -> str:
	start = text.index(signature)
	next_comment = text.find("/*", start + len(signature))
	if next_comment == -1:
		return text[start:]
	return text[start:next_comment]


def test_unix_low_physical_memory_uses_sysconf_backed_probe() -> None:
	unix_main = _read_text(UNIX_MAIN_PATH)

	assert "static qboolean Sys_QueryPhysicalMemoryBytes( unsigned long long *totalBytes ) {" in unix_main
	assert "_SC_PHYS_PAGES" in unix_main
	assert "_SC_PAGESIZE" in unix_main or "_SC_PAGE_SIZE" in unix_main

	low_memory_block = _function_block(unix_main, "qboolean Sys_LowPhysicalMemory() {")
	assert "Sys_QueryPhysicalMemoryBytes( &totalBytes )" in low_memory_block
	assert "return ( totalBytes <= MEM_THRESHOLD ) ? qtrue : qfalse;" in low_memory_block
	assert "return qfalse; // bk001207 - FIXME" not in low_memory_block


def test_unix_function_compare_and_checksum_use_symbol_backed_linux_metadata() -> None:
	unix_main = _read_text(UNIX_MAIN_PATH)

	assert "static qboolean Sys_QueryFunctionBytes( void *functionPointer, const byte **functionBytes, size_t *functionSize ) {" in unix_main

	query_block = _function_block(
		unix_main,
		"static qboolean Sys_QueryFunctionBytes( void *functionPointer, const byte **functionBytes, size_t *functionSize ) {",
	)
	assert "dladdr1( functionPointer, &info, (void **)&symbol, RTLD_DL_SYMENT )" in query_block
	assert "symbol->st_size == 0" in query_block

	function_cmp_block = _function_block(unix_main, "int Sys_FunctionCmp( void *f1, void *f2 ) {")
	assert "if ( f1 == f2 ) {" in function_cmp_block
	assert "Sys_QueryFunctionBytes( f1, &functionBytes1, &functionSize1 )" in function_cmp_block
	assert "Sys_QueryFunctionBytes( f2, &functionBytes2, &functionSize2 )" in function_cmp_block
	assert "memcmp( functionBytes1, functionBytes2, functionSize1 ) == 0" in function_cmp_block

	function_checksum_block = _function_block(unix_main, "int Sys_FunctionCheckSum( void *f1 ) {")
	assert "Sys_QueryFunctionBytes( f1, &functionBytes, &functionSize )" in function_checksum_block
	assert "Com_BlockChecksum( functionBytes, (int)functionSize )" in function_checksum_block


def test_unix_monkey_marker_detection_reconstructs_q3monkeyid_release_hook() -> None:
	unix_main = _read_text(UNIX_MAIN_PATH)

	assert "static qboolean Sys_PathHasReleaseMarker( const char *directory, const char *markerName ) {" in unix_main

	path_helper_block = _function_block(
		unix_main,
		"static qboolean Sys_PathHasReleaseMarker( const char *directory, const char *markerName ) {",
	)
	assert 'Com_sprintf( path, sizeof( path ), "%s/%s", directory, markerName );' in path_helper_block
	assert "stat( path, &fileInfo ) != 0" in path_helper_block

	assert 'Sys_PathHasReleaseMarker( Sys_Cwd(), "q3monkeyid" )' in unix_main
	assert 'Sys_PathHasReleaseMarker( Sys_DefaultInstallPath(), "q3monkeyid" )' in unix_main
	assert "return qfalse;" in unix_main


def test_unix_profiling_hooks_use_gmon_compatible_runtime_controls() -> None:
	unix_main = _read_text(UNIX_MAIN_PATH)
	unix_makefile = _read_text(UNIX_MAKEFILE_PATH)

	assert "typedef void (*sys_moncontrol_t)( int mode );" in unix_main
	assert "typedef void (*sys_mcleanup_t)( void );" in unix_main
	assert "static qboolean Sys_ResolveProfilingHooks( void ) {" in unix_main

	resolve_block = _function_block(unix_main, "static qboolean Sys_ResolveProfilingHooks( void ) {")
	assert 'dlsym( RTLD_DEFAULT, "moncontrol" )' in resolve_block
	assert 'dlsym( RTLD_DEFAULT, "_mcleanup" )' in resolve_block

	profiling_enable_block = _function_block(unix_main, "static void Sys_SetProfilingEnabled( qboolean enabled ) {")
	assert "sys_moncontrol( enabled ? 1 : 0 );" in profiling_enable_block

	begin_block = _function_block(unix_main, "void Sys_BeginProfiling( void ) {")
	assert "if ( sys_profilingActive ) {" in begin_block
	assert "sys_profilingSessionStarted = qtrue;" in begin_block
	assert "Sys_SetProfilingEnabled( qtrue );" in begin_block

	end_block = _function_block(unix_main, "void Sys_EndProfiling( void ) {")
	assert "if ( !sys_profilingSessionStarted ) {" in end_block
	assert "sys_moncontrol( 0 );" in end_block
	assert "sys_mcleanup();" in end_block

	exit_block = _function_block(unix_main, "void Sys_Exit( int ex ) {")
	assert "Sys_EndProfiling();" in exit_block

	init_block = _function_block(unix_main, "void Sys_Init(void)")
	assert "Sys_SetProfilingEnabled( qfalse );" in init_block

	assert "QL_ENABLE_GPROF ?= 0" in unix_makefile
	assert "PROFILE_CFLAGS := -pg" in unix_makefile
	assert "PROFILE_LDFLAGS := -pg" in unix_makefile
	assert "DO_CC=$(CC) $(CFLAGS) $(PROFILE_CFLAGS)" in unix_makefile
	assert "DO_DED_CC=$(CC) -DDEDICATED -DC_ONLY $(CFLAGS) $(PROFILE_CFLAGS)" in unix_makefile
	assert "$(STEAMWORKS_LDFLAGS) $(PROFILE_LDFLAGS)" in unix_makefile
	assert "$(LDFLAGS) $(PROFILE_LDFLAGS)" in unix_makefile


def test_unix_clipboard_path_uses_bounded_wayland_and_x11_command_probes() -> None:
	unix_main = _read_text(UNIX_MAIN_PATH)

	assert "#define SYS_CLIPBOARD_MAX_BYTES ( 1024 * 1024 )" in unix_main
	assert "static void Sys_TrimClipboardText( char *text ) {" in unix_main
	assert "static qboolean Sys_IsExecutableOnPath( const char *name ) {" in unix_main
	assert "static char *Sys_ReadClipboardCommand( const char *command ) {" in unix_main

	path_block = _function_block(unix_main, "static qboolean Sys_IsExecutableOnPath( const char *name ) {")
	assert 'getenv( "PATH" )' in path_block
	assert "strchr( name, '/' )" in path_block
	assert "access( candidate, X_OK ) == 0" in path_block

	read_block = _function_block(unix_main, "static char *Sys_ReadClipboardCommand( const char *command ) {")
	assert 'pipe = popen( command, "r" );' in read_block
	assert "used >= SYS_CLIPBOARD_MAX_BYTES" in read_block
	assert "newBuffer = realloc( buffer, newCapacity );" in read_block
	assert "Sys_TrimClipboardText( buffer );" in read_block
	assert "data = Z_Malloc( dataBytes );" in read_block

	clipboard_block = _function_block(unix_main, "char *Sys_GetClipboardData( void ) {")
	assert 'display = getenv( "DISPLAY" );' in clipboard_block
	assert 'waylandDisplay = getenv( "WAYLAND_DISPLAY" );' in clipboard_block
	assert 'Sys_IsExecutableOnPath( "wl-paste" )' in clipboard_block
	assert 'Sys_ReadClipboardCommand( "wl-paste --no-newline 2>/dev/null" )' in clipboard_block
	assert 'Sys_ReadClipboardCommand( "wl-paste 2>/dev/null" )' in clipboard_block
	assert 'Sys_IsExecutableOnPath( "xclip" )' in clipboard_block
	assert 'Sys_ReadClipboardCommand( "xclip -selection clipboard -out 2>/dev/null" )' in clipboard_block
	assert 'Sys_IsExecutableOnPath( "xsel" )' in clipboard_block
	assert 'Sys_ReadClipboardCommand( "xsel --clipboard --output 2>/dev/null" )' in clipboard_block


def test_unix_checkcd_uses_configured_baseq3_content_roots_instead_of_an_unconditional_success() -> None:
	unix_main = _read_text(UNIX_MAIN_PATH)

	assert "static qboolean Sys_PathHasBaseq3Asset( const char *rootPath, const char *assetName ) {" in unix_main

	path_block = _function_block(unix_main, "static qboolean Sys_PathHasBaseq3Asset( const char *rootPath, const char *assetName ) {")
	assert 'Com_sprintf( path, sizeof( path ), "%s/baseq3/%s", rootPath, assetName );' in path_block
	assert "stat( path, &fileInfo ) != 0" in path_block
	assert "S_ISREG( fileInfo.st_mode )" in path_block

	checkcd_block = _function_block(unix_main, "qboolean Sys_CheckCD( void ) {")
	assert 'Cvar_VariableString( "fs_basepath" )' in checkcd_block
	assert 'Cvar_VariableString( "fs_cdpath" )' in checkcd_block
	assert "Sys_DefaultInstallPath()" in checkcd_block
	assert "Sys_DefaultCDPath()" in checkcd_block
	assert "Sys_Cwd()" in checkcd_block
	assert '"default.cfg"' in checkcd_block
	assert '"pak00.pk3"' in checkcd_block
	assert '"pak0.pk3"' in checkcd_block
	assert "Sys_PathHasBaseq3Asset( roots[i], assets[j] )" in checkcd_block
	assert "return qfalse;" in checkcd_block
	assert "return qtrue;" in checkcd_block
	assert "return qtrue;" not in checkcd_block.split("for ( i = 0;", 1)[0]


def test_unix_load_dll_uses_bounded_module_roots_and_resets_outputs() -> None:
	unix_main = _read_text(UNIX_MAIN_PATH)

	load_block = _function_block(unix_main, "void *Sys_LoadDll( const char *name, char *fqpath,")
	assert "*fqpath = 0;" in load_block
	assert "*entryPoint = NULL;" in load_block
	assert 'Cvar_VariableString( "fs_basepath" )' in load_block
	assert 'Cvar_VariableString( "fs_homepath" )' in load_block
	assert 'Cvar_VariableString( "fs_cdpath" )' in load_block
	assert "char  *searchRoots[4];" in load_block
	assert "searchRoots[searchCount++] = pwdpath;" in load_block
	assert "searchRoots[searchCount++] = homepath;" in load_block
	assert "searchRoots[searchCount++] = basepath;" in load_block
	assert "searchRoots[searchCount++] = cdpath;" in load_block
	assert "for ( i = 0; i < searchCount; i++ )" in load_block
	assert "FS_BuildOSPath( searchRoots[i], gamedir, fname )" in load_block
	assert "libHandle = dlopen( fn, Q_RTLD );" in load_block


def test_unix_load_dll_rejects_incompatible_module_candidates() -> None:
	unix_main = _read_text(UNIX_MAIN_PATH)

	load_block = _function_block(unix_main, "void *Sys_LoadDll( const char *name, char *fqpath,")
	assert 'dlsym( libHandle, "dllEntry" )' in load_block
	assert 'dlsym( libHandle, "vmMain" )' in load_block
	assert "Rejected DLL '%s': missing dllEntry export" in load_block
	assert "dllEntryQL( dllExports, imports, apiVersion );" in load_block
	assert "*entryPoint = dllEntryRet( systemcalls );" in load_block
	assert "Rejected DLL '%s': missing compatible VM exports" in load_block
	assert "dlclose( libHandle );" in load_block
	assert "libHandle = NULL;" in load_block


def test_unix_packet_events_preserve_unread_message_payload() -> None:
	unix_main = _read_text(UNIX_MAIN_PATH)

	get_event_block = _function_block(unix_main, "sysEvent_t Sys_GetEvent( void ) {")
	assert "Sys_GetPacket ( &adr, &netmsg )" in get_event_block
	assert "len = sizeof( netadr_t ) + netmsg.cursize - netmsg.readcount;" in get_event_block
	assert "memcpy( buf+1, &netmsg.data[netmsg.readcount], netmsg.cursize - netmsg.readcount );" in get_event_block
	assert "Sys_QueEvent( 0, SE_PACKET, 0, 0, len, buf );" in get_event_block
	assert "len = sizeof( netadr_t ) + netmsg.cursize;" not in get_event_block


def test_linux_sound_host_has_bounded_null_sink_and_oss_shutdown_path() -> None:
	linux_snd = _read_text(LINUX_SND_PATH)

	assert 'int audio_fd = -1;' in linux_snd
	assert '#define SND_NULL_DEVICE_NAME "null"' in linux_snd
	assert '#define SND_NONE_DEVICE_NAME "none"' in linux_snd
	assert '#define SND_SILENT_DEVICE_NAME "silent"' in linux_snd
	assert "static byte snd_nullBuffer[SND_NULL_BUFFER_SAMPLES * ( SND_NULL_SAMPLEBITS / 8 )];" in linux_snd

	null_device_block = _function_block(
		linux_snd,
		"static qboolean SNDDMA_IsNullDevice( const char *deviceName ) {",
	)
	assert "!Q_stricmp( deviceName, SND_NULL_DEVICE_NAME )" in null_device_block
	assert "!Q_stricmp( deviceName, SND_NONE_DEVICE_NAME )" in null_device_block
	assert "!Q_stricmp( deviceName, SND_SILENT_DEVICE_NAME )" in null_device_block

	null_init_block = _function_block(linux_snd, "static qboolean SNDDMA_InitNull( void ) {")
	assert "dma.channels = SND_NULL_CHANNELS;" in null_init_block
	assert "dma.samplebits = SND_NULL_SAMPLEBITS;" in null_init_block
	assert "dma.speed = SND_NULL_SPEED;" in null_init_block
	assert "dma.samples = SND_NULL_BUFFER_SAMPLES;" in null_init_block
	assert "dma.buffer = snd_nullBuffer;" in null_init_block
	assert "snd_nullLastMilliseconds = Sys_Milliseconds();" in null_init_block

	init_block = _function_block(linux_snd, "qboolean SNDDMA_Init( void ) {")
	assert "SNDDMA_IsNullDevice( snddevice->string )" in init_block
	assert "return SNDDMA_InitNull();" in init_block
	assert "if ( audio_fd < 0 ) {" in init_block
	assert "SNDDMA_Shutdown();" in init_block

	position_block = _function_block(linux_snd, "int SNDDMA_GetDMAPos( void ) {")
	assert "if ( snd_nullInited ) {" in position_block
	assert "currentMilliseconds = Sys_Milliseconds();" in position_block
	assert "sampleDelta = ( elapsedMilliseconds * dma.speed * dma.channels ) / 1000;" in position_block
	assert "snd_nullDmaPosition = ( snd_nullDmaPosition + sampleDelta ) % dma.samples;" in position_block

	shutdown_block = _function_block(linux_snd, "void SNDDMA_Shutdown( void ) {")
	assert "munmap( dma.buffer, snd_mmapSize );" in shutdown_block
	assert "close( audio_fd );" in shutdown_block
	assert "audio_fd = -1;" in shutdown_block
	assert "Com_Memset( &dma, 0, sizeof( dma ) );" in shutdown_block

	begin_block = _function_block(linux_snd, "void SNDDMA_BeginPainting( void ) {")
	assert "Snd_Memset( snd_nullBuffer, 0, sizeof( snd_nullBuffer ) );" in begin_block


def test_linux_joystick_host_bounds_device_scan_and_shutdown_state() -> None:
	linux_joystick = _read_text(LINUX_JOYSTICK_PATH)
	linux_glimp = _read_text(LINUX_GLIMP_PATH)
	linux_local = _read_text(REPO_ROOT / "src" / "code" / "unix" / "linux_local.h")

	assert "#define LINUX_JOYSTICK_MAX_DEVICES 4" in linux_joystick
	assert "#define LINUX_JOYSTICK_MAX_BUTTONS 32" in linux_joystick
	assert "#define LINUX_JOYSTICK_MAX_AXES 8" in linux_joystick
	assert '"/dev/input/js%d"' in linux_joystick
	assert '"/dev/js%d"' in linux_joystick
	assert "static unsigned int joy_button_state;" in linux_joystick

	try_open_block = _function_block(linux_joystick, "static qboolean IN_TryOpenJoystick( const char *filename ) {")
	assert "open( filename, O_RDONLY | O_NONBLOCK )" in try_open_block
	assert "JSIOCGAXES" in linux_joystick
	assert "JSIOCGBUTTONS" in linux_joystick
	assert "JSIOCGNAME( sizeof( name ) )" in linux_joystick
	assert 'Cvar_Set( "ui_joyavail", "1" );' in linux_joystick

	startup_block = _function_block(linux_joystick, "void IN_StartupJoystick( void ) {")
	assert "IN_ShutdownJoystick();" in startup_block
	assert 'Cvar_Set( "ui_joyavail", "0" );' in startup_block
	assert "ARRAY_LEN( deviceFormats )" in startup_block
	assert "LINUX_JOYSTICK_MAX_DEVICES" in startup_block
	assert "IN_TryOpenJoystick( filename )" in startup_block

	shutdown_block = _function_block(linux_joystick, "void IN_ShutdownJoystick( void ) {")
	assert "IN_ReleaseJoystickKeys();" in shutdown_block
	assert "IN_ClearJoystickState();" in shutdown_block
	assert "close( joy_fd );" in shutdown_block
	assert 'Cvar_Set( "ui_joyavail", "0" );' in shutdown_block

	move_block = _function_block(linux_joystick, "void IN_JoyMove( void ) {")
	assert "if ( joy_fd == -1 )" in move_block
	assert "eventType = event.type & ~JS_EVENT_INIT;" in linux_joystick
	assert "event.number >= LINUX_JOYSTICK_MAX_BUTTONS" in linux_joystick
	assert "event.number >= LINUX_JOYSTICK_MAX_AXES" in linux_joystick
	assert "buttonMask = 1u << event.number;" in linux_joystick
	assert "joy_button_state |= buttonMask;" in linux_joystick
	assert "joy_button_state &= ~buttonMask;" in linux_joystick
	assert "for ( i = 0; i < LINUX_JOYSTICK_MAX_AXES; i++ )" in linux_joystick
	assert "for ( i = 0; i < LINUX_JOYSTICK_AXIS_KEY_BITS; i++ )" in linux_joystick

	assert "void IN_ShutdownJoystick( void );" in linux_local

	input_init_block = _function_block(linux_glimp, "void IN_Init(void) {")
	assert "IN_StartupJoystick( );" in input_init_block
	assert "in_joystick->modified = qfalse;" in input_init_block

	input_shutdown_block = _function_block(linux_glimp, "void IN_Shutdown(void)")
	assert "IN_DeactivateMouse();" in input_shutdown_block
	assert "IN_ShutdownJoystick();" in input_shutdown_block
	assert input_shutdown_block.index("IN_DeactivateMouse();") < input_shutdown_block.index("IN_ShutdownJoystick();")
	assert "mouse_avail = qfalse;" in input_shutdown_block
	assert "mouse_active = qfalse;" in input_shutdown_block

	input_frame_block = _function_block(linux_glimp, "void IN_Frame (void) {")
	assert "if ( in_joystick && in_joystick->modified )" in input_frame_block
	assert "IN_StartupJoystick();" in input_frame_block
	assert "in_joystick->modified = qfalse;" in input_frame_block


def test_linux_glx_shutdown_bounds_partial_context_lifecycle() -> None:
	linux_glimp = _read_text(LINUX_GLIMP_PATH)

	shutdown_block = _function_block(linux_glimp, "void GLimp_Shutdown( void )")
	assert "if (!ctx || !dpy)" not in shutdown_block
	assert 'ri.Printf( PRINT_ALL, "Shutting down OpenGL subsystem\\n" );' in shutdown_block
	assert "IN_DeactivateMouse();" in shutdown_block
	assert "mouse_active = qfalse;" in shutdown_block
	assert "if ( qglXMakeCurrent )" in shutdown_block
	assert "qglXMakeCurrent( dpy, None, NULL );" in shutdown_block
	assert "if ( ctx && qglXDestroyContext )" in shutdown_block
	assert "qglXDestroyContext( dpy, ctx );" in shutdown_block
	assert "XDestroyWindow( dpy, win );" in shutdown_block
	assert "if ( vidmode_active && vidmodes )" in shutdown_block
	assert "XF86VidModeSwitchToMode( dpy, scrnum, vidmodes[0] );" in shutdown_block
	assert "XF86VidModeSetGamma( dpy, scrnum, &vidmode_InitialGamma );" in shutdown_block
	assert "XCloseDisplay( dpy );" in shutdown_block
	assert "fclose( glw_state.log_fp );" in shutdown_block
	assert "glw_state.log_fp = NULL;" in shutdown_block
	assert "QGL_Shutdown();" in shutdown_block
	assert shutdown_block.index("QGL_Shutdown();") < shutdown_block.index("memset( &glConfig")
	assert "dpy = NULL;" in shutdown_block
	assert "win = 0;" in shutdown_block
	assert "ctx = NULL;" in shutdown_block
	assert "vidmode_active = qfalse;" in shutdown_block

	end_frame_block = _function_block(linux_glimp, "void GLimp_EndFrame (void)")
	assert "if ( !dpy || !win || !qglXSwapBuffers )" in end_frame_block
	assert "return;" in end_frame_block
	assert "qglXSwapBuffers(dpy, win);" in end_frame_block


def test_null_sound_host_has_bounded_silent_dma_sink() -> None:
	null_snddma = _read_text(NULL_SNDDMA_PATH)

	assert '#include "../client/snd_local.h"' in null_snddma
	assert "#define SND_NULL_SAMPLEBITS 16" in null_snddma
	assert "#define SND_NULL_SPEED 22050" in null_snddma
	assert "#define SND_NULL_CHANNELS 2" in null_snddma
	assert "#define SND_NULL_BUFFER_SAMPLES 0x8000" in null_snddma
	assert "static byte\tsnd_nullBuffer[SND_NULL_BUFFER_SAMPLES * ( SND_NULL_SAMPLEBITS / 8 )];" in null_snddma

	clear_block = _function_block(null_snddma, "static void SNDDMA_ClearNullState( void ) {")
	assert "snd_nullInited = qfalse;" in clear_block
	assert "snd_nullDmaPosition = 0;" in clear_block
	assert "Com_Memset( snd_nullBuffer, 0, sizeof( snd_nullBuffer ) );" in clear_block
	assert "Com_Memset( &dma, 0, sizeof( dma ) );" in clear_block

	init_block = _function_block(null_snddma, "qboolean SNDDMA_Init( void ) {")
	assert "dma.channels = SND_NULL_CHANNELS;" in init_block
	assert "dma.samplebits = SND_NULL_SAMPLEBITS;" in init_block
	assert "dma.speed = SND_NULL_SPEED;" in init_block
	assert "dma.samples = SND_NULL_BUFFER_SAMPLES;" in init_block
	assert "dma.submission_chunk = 1;" in init_block
	assert "dma.buffer = snd_nullBuffer;" in init_block
	assert "snd_nullLastMilliseconds = Sys_Milliseconds();" in init_block
	assert "snd_nullInited = qtrue;" in init_block
	assert "return qtrue;" in init_block
	assert "return qfalse;" not in init_block

	position_block = _function_block(null_snddma, "int\tSNDDMA_GetDMAPos( void ) {")
	assert "if ( !snd_nullInited )" in position_block
	assert "currentMilliseconds = Sys_Milliseconds();" in position_block
	assert "sampleDelta = ( elapsedMilliseconds * dma.speed * dma.channels ) / 1000;" in position_block
	assert "snd_nullDmaPosition = ( snd_nullDmaPosition + sampleDelta ) % dma.samples;" in position_block
	assert "return snd_nullDmaPosition;" in position_block

	shutdown_block = _function_block(null_snddma, "void SNDDMA_Shutdown( void ) {")
	assert "SNDDMA_ClearNullState();" in shutdown_block

	begin_block = _function_block(null_snddma, "void SNDDMA_BeginPainting( void ) {")
	assert "if ( snd_nullInited )" in begin_block
	assert "Com_Memset( snd_nullBuffer, 0, sizeof( snd_nullBuffer ) );" in begin_block

	clear_sound_block = _function_block(null_snddma, "void S_ClearSoundBuffer( void ) {")
	assert "snd_nullDmaPosition = 0;" in clear_sound_block
	assert "snd_nullLastMilliseconds = Sys_Milliseconds();" in clear_sound_block
	assert "Com_Memset( snd_nullBuffer, 0, sizeof( snd_nullBuffer ) );" in clear_sound_block


def test_null_renderer_host_refuses_fake_gl_initialization() -> None:
	null_glimp = _read_text(NULL_GLIMP_PATH)

	assert "static qboolean\tglimp_nullLogging;" in null_glimp

	glimp_init_block = _function_block(null_glimp, "void GLimp_Init( void ) {")
	assert 'ri.Error( ERR_FATAL, "GLimp_Init() - null renderer host has no OpenGL subsystem\\n" );' in glimp_init_block

	qgl_init_block = _function_block(null_glimp, "qboolean QGL_Init( const char *dllname ) {")
	assert "(void)dllname;" in qgl_init_block
	assert "return qfalse;" in qgl_init_block
	assert "return qtrue;" not in qgl_init_block

	logging_block = _function_block(null_glimp, "void\t\tGLimp_EnableLogging( qboolean enable ) {")
	assert "glimp_nullLogging = enable;" in logging_block

	log_comment_block = _function_block(null_glimp, "void GLimp_LogComment( char *comment ) {")
	assert "if ( !glimp_nullLogging )" in log_comment_block
	assert "(void)comment;" in log_comment_block

	shutdown_block = _function_block(null_glimp, "void QGL_Shutdown( void ) {")
	assert "qwglSwapIntervalEXT = NULL;" in shutdown_block
	assert "qglMultiTexCoord2fARB = NULL;" in shutdown_block
	assert "qglActiveTextureARB = NULL;" in shutdown_block
	assert "qglClientActiveTextureARB = NULL;" in shutdown_block
	assert "qglLockArraysEXT = NULL;" in shutdown_block
	assert "qglUnlockArraysEXT = NULL;" in shutdown_block
	assert "glimp_nullLogging = qfalse;" in shutdown_block

	glimp_shutdown_block = _function_block(null_glimp, "void GLimp_Shutdown( void ) {")
	assert "QGL_Shutdown();" in glimp_shutdown_block


def test_null_input_key_pump_maintains_no_device_state() -> None:
	null_input = _read_text(NULL_INPUT_PATH)

	assert "static qboolean\tin_nullInputInitialized;" in null_input

	touch_block = _function_block(null_input, "static void IN_NullTouchCompatibilityCvars( void ) {")
	assert "(void)in_mouse;" in touch_block
	assert "(void)in_nograb;" in touch_block
	assert "(void)in_joystick;" in touch_block
	assert "(void)in_debugJoystick;" in touch_block
	assert "(void)joy_threshold;" in touch_block

	refresh_block = _function_block(null_input, "static void IN_NullRefreshCompatibilityState( void ) {")
	assert "if ( in_joystick )" in refresh_block
	assert "in_joystick->modified = qfalse;" in refresh_block
	assert 'Cvar_Set( "ui_joyavail", "0" );' in refresh_block
	assert "IN_NullTouchCompatibilityCvars();" in refresh_block

	init_block = _function_block(null_input, "void IN_Init( void ) {")
	assert "in_nullInputInitialized = qtrue;" in init_block
	assert "IN_NullRefreshCompatibilityState();" in init_block

	frame_block = _function_block(null_input, "void IN_Frame( void ) {")
	assert "IN_NullRefreshCompatibilityState();" in frame_block

	shutdown_block = _function_block(null_input, "void IN_Shutdown( void ) {")
	assert "IN_NullRefreshCompatibilityState();" in shutdown_block
	assert "in_nullInputInitialized = qfalse;" in shutdown_block

	key_events_block = _function_block(null_input, "void Sys_SendKeyEvents( void ) {")
	assert "if ( in_nullInputInitialized )" in key_events_block
	assert "IN_NullRefreshCompatibilityState();" in key_events_block


def test_null_runtime_shims_track_current_qcommon_contracts() -> None:
	null_main = _read_text(NULL_MAIN_PATH)
	null_net = _read_text(NULL_NET_PATH)
	mac_net = _read_text(MAC_NET_PATH)
	null_glimp = _read_text(NULL_GLIMP_PATH)
	null_client = _read_text(NULL_CLIENT_PATH)
	null_snddma = _read_text(NULL_SNDDMA_PATH)
	null_input = _read_text(NULL_INPUT_PATH)
	compacted_null_glimp = null_glimp.replace(" ", "").replace("\t", "")

	assert "void Sys_BeginStreamedFile( fileHandle_t f, int readAhead ) {" in null_main
	assert "int Sys_StreamedRead( void *buffer, int size, int count, fileHandle_t f ) {" in null_main
	assert "void QDECL Sys_Error( const char *error, ... ) {" in null_main
	assert "char *Sys_ExecutableBaseName( void ) {" in null_main
	assert "char *Sys_DefaultInstallPath( void ) {" in null_main
	assert "char *Sys_DefaultHomePath( void ) {" in null_main
	assert "char *Sys_GetCurrentUser( void ) {" in null_main
	assert "Q_strncpyz( sys_executablePath, argv[0], sizeof( sys_executablePath ) );" in null_main
	assert "Com_Init( cmdline );" in null_main
	assert "NET_Init();" in null_main

	assert "qboolean Sys_StringToAdr( const char *s, netadr_t *a )" in null_net
	assert "void Sys_SendPacket( int length, const void *data, netadr_t to )" in null_net
	assert "qboolean Sys_IsLANAddress( netadr_t adr ) {" in null_net

	assert "qboolean Sys_StringToAdr( const char *s, netadr_t *a )" in mac_net
	assert "void Sys_SendPacket( int length, const void *data, netadr_t to )" in mac_net
	assert "qboolean Sys_IsLANAddress( netadr_t adr ) {" in mac_net

	assert "voidGLimp_Init(void)" in compacted_null_glimp
	assert "intGLimp_Init(void)" not in compacted_null_glimp
	assert "glimp_nullLogging = enable;" in null_glimp
	assert "(void)dllname;" in null_glimp

	assert "void CL_RefreshOnlineServicesBridgeState( void ) {" in null_client
	assert '#define CL_NULL_BROWSER_PARITY_SCOPE_LABEL "strict-retail-excluded"' in null_client
	assert 'Cvar_Set( "ui_browserAwesomium", "0" );' in null_client
	assert 'Cvar_Set( "ui_browserAwesomiumParityScope", CL_NULL_BROWSER_PARITY_SCOPE_LABEL );' in null_client
	assert 'Cvar_Set( "web_browserActive", "0" );' in null_client
	assert 'Cvar_Set( "ui_advertisementBridgeParityScope", CL_NULL_BROWSER_PARITY_SCOPE_LABEL );' in null_client
	assert "void *CL_WebHost_GetCursorHandle( void ) {" in null_client
	assert "void CL_WebHost_NotifyAppActivation( qboolean active ) {" in null_client
	assert "void CL_WebView_OnMouseMove( int x, int y ) {" in null_client
	assert "void CL_WebView_OnMouseButtonEvent( int key, qboolean down ) {" in null_client
	assert "void CL_WebView_OnMouseWheelEvent( int direction ) {" in null_client
	assert "void CL_AdvertisementBridge_InitUI( void ) {" in null_client
	assert "void CL_AdvertisementBridge_ActivateAdvert( int cellId ) {" in null_client
	assert "void CL_AdvertisementBridge_SetActiveAdvert( int cellId ) {" in null_client

	assert "void SNDDMA_Activate( void ) {" in null_snddma
	assert "void S_AddVoiceSamples( int clientNum, int samples, const short *data ) {" in null_snddma

	assert 'in_mouse = Cvar_Get( "in_mouse", "0", CVAR_ARCHIVE );' in null_input
	assert 'in_nograb = Cvar_Get( "in_nograb", "0", CVAR_TEMP );' in null_input
	assert 'in_joystick = Cvar_Get( "in_joystick", "0", CVAR_ARCHIVE|CVAR_LATCH );' in null_input
	assert 'in_debugJoystick = Cvar_Get( "in_debugjoystick", "0", CVAR_TEMP );' in null_input
	assert 'joy_threshold = Cvar_Get( "joy_threshold", "0.15", CVAR_ARCHIVE );' in null_input
	assert 'Cvar_Set( "ui_joyavail", "0" );' in null_input
	assert "void Sys_SendKeyEvents( void ) {" in null_input


def test_posix_native_builds_cover_linux_and_macos_ci() -> None:
	native_build_script = _read_text(BUILD_POSIX_NATIVE_SCRIPT_PATH)
	cleanroom_build_script = _read_text(BUILD_CLEANROOM_SCRIPT_PATH)
	unix_makefile = _read_text(UNIX_MAKEFILE_PATH)
	unix_main = _read_text(UNIX_MAIN_PATH)
	unix_net = _read_text(UNIX_NET_PATH)
	linux_common = _read_text(LINUX_COMMON_PATH)
	unix_shared = _read_text(REPO_ROOT / "src" / "code" / "unix" / "unix_shared.c")
	null_client = _read_text(NULL_CLIENT_PATH)
	run_harnesses = _read_text(RUN_HARNESSES_PATH)
	re_trace_harness = _read_text(RE_TRACE_HARNESS_PATH)
	push_workflow = _read_text(PUSH_WORKFLOW_PATH)
	nightly_workflow = _read_text(NIGHTLY_WORKFLOW_PATH)
	reverse_builds_doc = _read_text(REVERSE_BUILDS_DOC_PATH)
	toolchain_ci = _read_text(TOOLCHAIN_CI_PATH)

	assert "UNIX_MAKE_DIR=\"${REPO_ROOT}/src/code/unix\"" in native_build_script
	assert "PLATFORM_NAME=\"linux\"" in native_build_script
	assert "PLATFORM_NAME=\"macos\"" in native_build_script
	assert "MAKE_PLATFORM=\"darwin\"" in native_build_script
	assert "SHLIB_EXT=\"so\"" in native_build_script
	assert "SHLIB_EXT=\"dylib\"" in native_build_script
	assert "HOST_ARCH_RAW=" in native_build_script
	assert "HOST_ARCH=\"arm64\"" in native_build_script
	assert "SHLIB_LDFLAGS_DEFAULT=\"-shared\"" in native_build_script
	assert "SHLIB_LDFLAGS_DEFAULT=\"-dynamiclib -Wl,-undefined,dynamic_lookup\"" in native_build_script
	assert "build/posix/${PLATFORM_NAME}" in native_build_script
	assert "QL_POSIX_BUILD_ROOT" in native_build_script
	assert "baseq3/cgame${HOST_ARCH}.${SHLIB_EXT}" in native_build_script
	assert "baseq3/qagame${HOST_ARCH}.${SHLIB_EXT}" in native_build_script
	assert "baseq3/ui${HOST_ARCH}.${SHLIB_EXT}" in native_build_script
	assert "src/code/cgame/cg_newdraw.c" in native_build_script
	assert "src/code/game/g_match_state.c" in native_build_script
	assert "src/game/g_match_config.c" in native_build_script
	assert "src/code/ui/ui_quakelive_bridge.c" not in native_build_script
	assert "${BUILD_ROOT}/${MAKE_PLATFORM}q3ded" in native_build_script
	assert "quakelive-${PLATFORM_NAME}-${HOST_ARCH}-native.tar.gz" in native_build_script
	assert "package_sha256=" in native_build_script
	assert "QL_BUILD_ONLINE_SERVICES=0" in native_build_script
	assert "QL_ENABLE_OGG=0" in native_build_script
	assert "QL_ENABLE_RANKINGS=0" in native_build_script

	assert "COMMONDIR=$(MOUNT_DIR)/../common" in unix_makefile
	assert "QL_ENABLE_RANKINGS ?= 0" in unix_makefile
	assert "$(B)/ded/sv_rankings.o" in unix_makefile
	assert "$(B)/ded/platform_services.o" in unix_makefile
	assert "$(B)/ded/linux_signals.o" in unix_makefile
	assert "$(B)/ded/unix_vm_x86.o" in unix_makefile
	assert "$(COMMONDIR)/platform/platform_services.c" in unix_makefile
	assert "$(UDIR)/vm_x86.c" in unix_makefile

	assert 'const char *dllExtension = "dylib";' in unix_main
	assert 'const char *dllExtension = "so";' in unix_main
	assert '"%sx86_64.%s"' in unix_main
	assert '"%sarm64.%s"' in unix_main
	assert "#define OSIOCGIFADDR SIOCGIFADDR" in unix_net
	assert "socklen_t\tfromlen;" in unix_net
	assert "#if defined(__linux__) || defined(__FreeBSD__)" in linux_common
	assert linux_common.rstrip().endswith("#endif")
	assert "defined __x86_64__ || defined __aarch64__" in unix_shared
	assert "void SteamClient_Init( void ) {" in null_client

	q_shared = _read_text(REPO_ROOT / "src" / "code" / "game" / "q_shared.h")
	bg_lib = _read_text(REPO_ROOT / "src" / "code" / "game" / "bg_lib.c")
	assert "#if idppc" in q_shared
	assert '#define CPUSTRING\t"MacOSX-arm64"' in q_shared
	assert 'defined( __APPLE__ )' in bg_lib

	assert "PLATFORM_NAME=\"linux\"" in cleanroom_build_script
	assert "PLATFORM_NAME=\"macos\"" in cleanroom_build_script

	assert "sys.platform == \"darwin\"" in run_harnesses
	assert "extension = \".dylib\"" in run_harnesses
	assert "'.dylib' if sys.platform == 'darwin' else '.so'" in re_trace_harness

	assert "posix-builds:" in push_workflow
	assert "Linux Native Build" in push_workflow
	assert "macOS Native Build" in push_workflow
	assert "bash tools/ci/build-posix-native.sh" in push_workflow
	assert "build/posix/${{ matrix.platform }}/dist/**" in push_workflow
	assert "Publish ${{ matrix.name }} package" in push_workflow

	assert "posix-native:" in nightly_workflow
	assert "Linux native build" in nightly_workflow
	assert "macOS native build" in nightly_workflow
	assert "bash tools/ci/build-posix-native.sh" in nightly_workflow
	assert "nightly-${{ matrix.artifact_name }}" in nightly_workflow
	assert "Publish ${{ matrix.name }} package" in nightly_workflow

	assert "build/posix/linux/dist/" in reverse_builds_doc
	assert "build/posix/macos/dist/" in reverse_builds_doc
	assert "native POSIX package" in toolchain_ci


def test_portability_docs_track_restored_low_memory_probe_and_remaining_stubs() -> None:
	linux_glibc_doc = _read_text(LINUX_GLIBC_32BIT_DOC_PATH)
	toolchain_matrix = _read_text(TOOLCHAIN_MATRIX_PATH)
	repo_wide_audit = _read_text(REPO_WIDE_AUDIT_PATH)
	unix_main_gap_note = _read_text(UNIX_MAIN_GAP_NOTE_PATH)
	linux_snd_gap_note = _read_text(LINUX_SND_GAP_NOTE_PATH)
	linux_joystick_gap_note = _read_text(LINUX_JOYSTICK_GAP_NOTE_PATH)
	linux_glimp_gap_note = _read_text(LINUX_GLIMP_GAP_NOTE_PATH)
	null_glimp_gap_note = _read_text(NULL_GLIMP_GAP_NOTE_PATH)
	null_input_gap_note = _read_text(NULL_INPUT_GAP_NOTE_PATH)
	null_snddma_gap_note = _read_text(NULL_SNDDMA_GAP_NOTE_PATH)

	assert "intentionally limited to the 32-bit `qagamei386.so` server-module lane" in linux_glibc_doc
	assert "not evidence of a retail-equivalent Linux client/runtime" in linux_glibc_doc
	assert "`QL_ENABLE_GPROF=1` for a bounded `gprof`-compatible build lane" in linux_glibc_doc
	assert "bounded clipboard retrieval path via `wl-paste`, `xclip`, or `xsel`" in linux_glibc_doc
	assert "`Sys_CheckCD()` now performs a bounded data-root probe across `fs_basepath`" in linux_glibc_doc
	assert "Unix `Sys_LoadDll()` now probes cwd plus `fs_homepath`, `fs_basepath`, and `fs_cdpath` and rejects incompatible native-module candidates before continuing" in linux_glibc_doc
	assert "Unix `Sys_GetEvent()` now preserves only unread packet bytes after `netmsg.readcount`" in linux_glibc_doc
	assert "Linux input shutdown path now releases retained X mouse grabs before clearing mouse availability" in linux_glibc_doc
	assert "a bounded silent Linux sound sink is available through `snddevice null`" in linux_glibc_doc
	assert "remaining Unix renderer/audio/input host gaps" in linux_glibc_doc

	assert "`Sys_LowPhysicalMemory()` now queries physical page counts through `sysconf()`" in toolchain_matrix
	assert "`Sys_FunctionCmp()` / `Sys_FunctionCheckSum()` now use Linux/glibc symbol metadata" in toolchain_matrix
	assert "`Sys_MonkeyShouldBeSpanked()` now reconstructs the retained `q3monkeyid` release-marker probe" in toolchain_matrix
	assert "`Sys_BeginProfiling()` / `Sys_EndProfiling()` now pause or resume `moncontrol()`" in toolchain_matrix
	assert "`_mcleanup()` when the Unix engine is built with `QL_ENABLE_GPROF=1`" in toolchain_matrix
	assert "bounded clipboard retrieval path through `wl-paste`, `xclip`, or `xsel`" in toolchain_matrix
	assert "`Sys_CheckCD()` now probes configured `baseq3` roots" in toolchain_matrix
	assert "`default.cfg`, `pak00.pk3`, or `pak0.pk3`" in toolchain_matrix
	assert "Unix `Sys_LoadDll()` now clears failed-load outputs, validates module exports, and closes incompatible candidates while probing cwd" in toolchain_matrix
	assert "`fs_homepath`, `fs_basepath`, and `fs_cdpath` for native modules" in toolchain_matrix
	assert "Unix `Sys_GetEvent()` now queues only unread packet bytes after `netmsg.readcount`" in toolchain_matrix
	assert "The Linux OSS sound backend can now opt into a silent DMA sink with `snddevice null`" in toolchain_matrix
	assert "the OSS path now closes its file descriptor and unmaps the mmap DMA buffer on shutdown" in toolchain_matrix
	assert "Linux GLX shutdown now detaches any current context" in toolchain_matrix
	assert "guards the end-frame swap after shutdown or partial init failure" in toolchain_matrix
	assert "Linux joystick probing now prefers `/dev/input/js*` before the historical `/dev/js*` nodes" in toolchain_matrix
	assert "closes the joystick descriptor on shutdown or cvar restart" in toolchain_matrix
	assert "Linux input shutdown now also releases the retained X mouse grab before clearing mouse availability" in toolchain_matrix
	assert "server-module-only evidence rather than Linux client/runtime parity proof" in toolchain_matrix
	assert "null host/runtime now carries current executable-name, path, timer, and loopback-network scaffolding" in toolchain_matrix
	assert "browser/advert/input shim entry points" in toolchain_matrix
	assert "input bootstrap cvars and a no-device key-event pump" in toolchain_matrix
	assert "a renderer GL init refusal" in toolchain_matrix
	assert "explicit null silent DMA sink plus sound/device activation/voice stubs" in toolchain_matrix

	assert "`Sys_LowPhysicalMemory()` through a" in repo_wide_audit
	assert "`sysconf()`-backed physical page-count query" in repo_wide_audit
	assert "symbol-backed" in repo_wide_audit
	assert "`Sys_FunctionCmp()` / `Sys_FunctionCheckSum()` coverage on Linux/glibc" in repo_wide_audit
	assert "reconstructs `Sys_MonkeyShouldBeSpanked()` as a retained `q3monkeyid`" in repo_wide_audit
	assert "marker probe" in repo_wide_audit
	assert "bounded `gprof`-compatible profiling control path" in repo_wide_audit
	assert "`moncontrol` / `_mcleanup`" in repo_wide_audit
	assert "`QL_ENABLE_GPROF=1`" in repo_wide_audit
	assert "bounded clipboard retrieval path" in repo_wide_audit
	assert "`wl-paste`, `xclip`, or `xsel`" in repo_wide_audit
	assert "`Sys_CheckCD()` now also acts as a bounded" in repo_wide_audit
	assert "accepting `default.cfg`, `pak00.pk3`, or" in repo_wide_audit
	assert "`pak0.pk3` as sufficient evidence of usable game data" in repo_wide_audit
	assert "`Sys_LoadDll()` now" in repo_wide_audit
	assert "resets failed-load outputs, validates candidate exports, closes incompatible" in repo_wide_audit
	assert "handles, and searches cwd" in repo_wide_audit
	assert "`fs_homepath`, `fs_basepath`," in repo_wide_audit
	assert "`Sys_GetEvent()` now also queues only unread packet bytes after" in repo_wide_audit
	assert "matching the recovered Win32 event-loop packet copy" in repo_wide_audit
	assert "Linux sound host now has a bounded silent DMA sink via `snddevice null`" in repo_wide_audit
	assert "OSS `/dev/dsp` path now has explicit shutdown cleanup" in repo_wide_audit
	assert "Linux GLX teardown now handles partial-init state" in repo_wide_audit
	assert "guards the end-frame swap path when display/window/swap state is absent" in repo_wide_audit
	assert "Linux joystick input now bounds the retained device scan to `/dev/input/js0-3`" in repo_wide_audit
	assert "and `/dev/js0-3`" in repo_wide_audit
	assert "resets `ui_joyavail` and closes `joy_fd` across" in repo_wide_audit
	assert "shutdown or `in_joystick` restarts" in repo_wide_audit
	assert "releases the retained X mouse grab before clearing mouse availability" in repo_wide_audit
	assert "server-module-only evidence rather than Linux client/runtime parity" in repo_wide_audit
	assert "current executable-name," in repo_wide_audit
	assert "timer/path, loopback-network" in repo_wide_audit
	assert "browser/advert/input," in repo_wide_audit
	assert "renderer GL init refusal" in repo_wide_audit
	assert "input bootstrap-cvar and" in repo_wide_audit
	assert "no-device key-pump surface" in repo_wide_audit
	assert "explicit null silent DMA sink" in repo_wide_audit
	assert "sound/device activation/voice shims" in repo_wide_audit

	assert "bounded silent DMA sink for `snddevice null`, `none`, or `silent`" in linux_snd_gap_note
	assert "`SNDDMA_Shutdown()` now unmaps the OSS DMA buffer and closes `audio_fd`" in linux_snd_gap_note
	assert "`Sys_LoadDll()` now clears the legacy `entryPoint` output before probing" in unix_main_gap_note
	assert "searches cwd, `fs_homepath`, `fs_basepath`, and `fs_cdpath`" in unix_main_gap_note
	assert "rejects incompatible native-module candidates before continuing the root search" in unix_main_gap_note
	assert "`Sys_GetEvent()` now queues only unread packet payload bytes after `netmsg.readcount`" in unix_main_gap_note
	assert "prefers `/dev/input/js0` through `/dev/input/js3` before the historical `/dev/js0` through `/dev/js3`" in linux_joystick_gap_note
	assert "`IN_ShutdownJoystick()` releases queued joystick keys, closes `joy_fd`, clears the tracked axis/button state, and resets `ui_joyavail`" in linux_joystick_gap_note
	assert "`GLimp_Shutdown()` now no longer returns early solely because `ctx` is missing" in linux_glimp_gap_note
	assert "`GLimp_EndFrame()` now refuses to swap when the display, window, or GLX swap pointer is absent" in linux_glimp_gap_note
	assert "deactivates retained X mouse grabs before clearing mouse availability" in linux_glimp_gap_note
	assert "clears mouse availability/activity state" in linux_glimp_gap_note
	assert "`SNDDMA_Init()` now returns `qtrue` for a local silent DMA sink" in null_snddma_gap_note
	assert "`SNDDMA_GetDMAPos()` advances that sink from `Sys_Milliseconds()`" in null_snddma_gap_note
	assert "`QGL_Init()` now returns `qfalse`" in null_glimp_gap_note
	assert "`GLimp_Init()` now raises a fatal error" in null_glimp_gap_note
	assert "`Sys_SendKeyEvents()` now refreshes the no-device compatibility state" in null_input_gap_note
	assert "`IN_NullRefreshCompatibilityState()` clears `in_joystick->modified`" in null_input_gap_note


def test_repo_wide_audit_closes_rw_g01_as_documented_divergence() -> None:
	repo_wide_audit = _read_text(REPO_WIDE_AUDIT_PATH)

	assert "Repo-wide parity across the checked-in tree: **98%**" in repo_wide_audit
	assert "two bounded gap" in repo_wide_audit
	assert "### RW-G01 - Online services and external ecosystems are now a documented bounded divergence" in repo_wide_audit
	assert "Current status: **Closed as an active repo-wide gap; bounded divergence remains documented**" in repo_wide_audit
