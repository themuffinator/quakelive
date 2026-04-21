from __future__ import annotations

from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parent.parent
UNIX_MAIN_PATH = REPO_ROOT / "src" / "code" / "unix" / "unix_main.c"
NULL_MAIN_PATH = REPO_ROOT / "src" / "code" / "null" / "null_main.c"
NULL_NET_PATH = REPO_ROOT / "src" / "code" / "null" / "null_net.c"
MAC_NET_PATH = REPO_ROOT / "src" / "code" / "null" / "mac_net.c"
NULL_GLIMP_PATH = REPO_ROOT / "src" / "code" / "null" / "null_glimp.c"
NULL_CLIENT_PATH = REPO_ROOT / "src" / "code" / "null" / "null_client.c"
NULL_SNDDMA_PATH = REPO_ROOT / "src" / "code" / "null" / "null_snddma.c"
NULL_INPUT_PATH = REPO_ROOT / "src" / "code" / "null" / "null_input.c"
UNIX_MAKEFILE_PATH = REPO_ROOT / "src" / "code" / "unix" / "Makefile"
LINUX_GLIBC_32BIT_DOC_PATH = REPO_ROOT / "docs" / "build" / "linux-glibc-32bit.md"
TOOLCHAIN_MATRIX_PATH = REPO_ROOT / "docs" / "platform" / "toolchain-matrix.md"
REPO_WIDE_AUDIT_PATH = (
	REPO_ROOT / "docs" / "reverse-engineering" / "repo-wide-parity-audit-2026-04-21.md"
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
	assert "(void)enable;" in null_glimp
	assert "(void)dllname;" in null_glimp

	assert "void CL_RefreshOnlineServicesBridgeState( void ) {" in null_client
	assert 'Cvar_Set( "ui_browserAwesomium", "0" );' in null_client
	assert 'Cvar_Set( "web_browserActive", "0" );' in null_client
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


def test_portability_docs_track_restored_low_memory_probe_and_remaining_stubs() -> None:
	linux_glibc_doc = _read_text(LINUX_GLIBC_32BIT_DOC_PATH)
	toolchain_matrix = _read_text(TOOLCHAIN_MATRIX_PATH)
	repo_wide_audit = _read_text(REPO_WIDE_AUDIT_PATH)

	assert "intentionally limited to the 32-bit `qagamei386.so` server-module lane" in linux_glibc_doc
	assert "not evidence of a retail-equivalent Linux client/runtime" in linux_glibc_doc
	assert "`QL_ENABLE_GPROF=1` for a bounded `gprof`-compatible build lane" in linux_glibc_doc
	assert "remaining Unix renderer/audio/input host gaps" in linux_glibc_doc

	assert "`Sys_LowPhysicalMemory()` now queries physical page counts through `sysconf()`" in toolchain_matrix
	assert "`Sys_FunctionCmp()` / `Sys_FunctionCheckSum()` now use Linux/glibc symbol metadata" in toolchain_matrix
	assert "`Sys_MonkeyShouldBeSpanked()` now reconstructs the retained `q3monkeyid` release-marker probe" in toolchain_matrix
	assert "`Sys_BeginProfiling()` / `Sys_EndProfiling()` now pause or resume `moncontrol()`" in toolchain_matrix
	assert "`_mcleanup()` when the Unix engine is built with `QL_ENABLE_GPROF=1`" in toolchain_matrix
	assert "server-module-only evidence rather than Linux client/runtime parity proof" in toolchain_matrix
	assert "null host/runtime now carries current executable-name, path, timer, and loopback-network scaffolding" in toolchain_matrix
	assert "browser/advert/input shim entry points" in toolchain_matrix
	assert "input bootstrap cvars and a no-op key-event pump" in toolchain_matrix
	assert "silent sound/device activation/voice stubs" in toolchain_matrix

	assert "`Sys_LowPhysicalMemory()` through a" in repo_wide_audit
	assert "`sysconf()`-backed physical page-count query" in repo_wide_audit
	assert "symbol-backed" in repo_wide_audit
	assert "`Sys_FunctionCmp()` / `Sys_FunctionCheckSum()` coverage on Linux/glibc" in repo_wide_audit
	assert "reconstructs `Sys_MonkeyShouldBeSpanked()` as a retained `q3monkeyid`" in repo_wide_audit
	assert "marker probe" in repo_wide_audit
	assert "bounded `gprof`-compatible profiling control path" in repo_wide_audit
	assert "`moncontrol` / `_mcleanup`" in repo_wide_audit
	assert "`QL_ENABLE_GPROF=1`" in repo_wide_audit
	assert "server-module-only evidence rather than Linux client/runtime parity" in repo_wide_audit
	assert "current executable-name," in repo_wide_audit
	assert "timer/path, loopback-network" in repo_wide_audit
	assert "browser/advert/input, and silent" in repo_wide_audit
	assert "input bootstrap-cvar" in repo_wide_audit
	assert "sound/device activation/voice shims" in repo_wide_audit
