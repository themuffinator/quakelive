from __future__ import annotations

import subprocess
import textwrap
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent


def _compile_and_run(source: str, workdir: Path) -> str:
    workdir.mkdir(parents=True, exist_ok=True)
    c_path = workdir / "probe.c"
    exe_path = workdir / "probe"
    c_path.write_text(source, encoding="utf-8")

    compile_cmd = [
        "gcc",
        "-std=c99",
        "-Wall",
        f"-I{REPO_ROOT}",
        "-Isrc",
        "-Isrc/code",
        "-Isrc/code/game",
        "-Isrc/code/qcommon",
        str(c_path),
        "-o",
        str(exe_path),
    ]

    subprocess.run(compile_cmd, check=True, cwd=REPO_ROOT)

    result = subprocess.run(
        [str(exe_path)],
        check=True,
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
    )
    return result.stdout


def test_fake_vacban_constants_match_hlil(tmp_path: Path) -> None:
    source = textwrap.dedent(
        r"""
	#include <stdio.h>

	#include "src/code/server/server.h"

	int main(void) {
	printf("message:%s\n", SV_FAKEVACBAN_AUTH_MESSAGE);
	printf("result:%s\n", SV_FAKEVACBAN_RESULT_CODE);
	printf("outcome:%s\n", SV_FAKEVACBAN_OUTCOME);
	printf("status:%s\n", SV_FAKEVACBAN_STATUS);
	printf("label:%s\n", SV_FAKEVACBAN_LABEL);
	return 0;
	}
        """
    )

    output = _compile_and_run(source, tmp_path / "fakevac_constants")
    lines = [line.strip() for line in output.splitlines() if line.strip()]
    assert lines == [
        "message:Failed to authenticate with Steam: VAC ban on record",
        "result:3",
        "outcome:VAC ban on record",
        "status:failed",
        "label:steam",
    ]


def test_fake_vacban_telemetry_payload(tmp_path: Path) -> None:
    source = textwrap.dedent(
        r"""
	#include <stdio.h>
	#include <stdarg.h>
	#include <string.h>

	#include "src/code/game/q_shared.h"
	#include "src/code/qcommon/qcommon.h"
	#include "src/code/server/server.h"
	#include "src/code/qcommon/net_chan.c"

	short ShortSwap( short l ) { return l; }

	void Com_Printf( const char *fmt, ... ) {
	va_list args;
	va_start( args, fmt );
	vprintf( fmt, args );
	va_end( args );
	}

	void Com_DPrintf( const char *fmt, ... ) { (void)fmt; }
	void Com_Error( int code, const char *fmt, ... ) { (void)code; (void)fmt; }
	void Sys_SnapVector( float *v ) { (void)v; }
	int Sys_Milliseconds( void ) { return 0; }
	void FS_FreeFile( void *buffer ) { (void)buffer; }
	int FS_ReadFile( const char *qpath, void **buffer ) { (void)qpath; (void)buffer; return -1; }
	void Info_SetValueForKey( char *s, const char *key, const char *value ) { (void)s; (void)key; (void)value; }
	char *Info_ValueForKey( const char *s, const char *key ) { (void)s; (void)key; return ""; }
	void Cmd_TokenizeString( const char *text_in ) { (void)text_in; }
	int Cmd_Argc( void ) { return 0; }
	char *Cmd_Argv( int arg ) { (void)arg; return ""; }
	void Cvar_Set( const char *var_name, const char *value ) { (void)var_name; (void)value; }
	cvar_t *Cvar_Get( const char *var_name, const char *value, int flags ) { (void)var_name; (void)value; (void)flags; return NULL; }
	int Cvar_VariableIntegerValue( const char *var_name ) { (void)var_name; return 0; }
	qboolean Sys_StringToAdr( const char *s, netadr_t *a ) { (void)s; (void)a; return qfalse; }
	const char *NET_ErrorString( void ) { return ""; }
	void Sys_SendPacket( int length, const void *data, netadr_t to ) { (void)length; (void)data; (void)to; }
	qboolean Sys_GetPacket( netadr_t *net_from, msg_t *net_message ) { (void)net_from; (void)net_message; return qfalse; }
	qboolean Sys_IsLANAddress( netadr_t adr ) { (void)adr; return qfalse; }
	void Sys_ShowIP(void) {}
	void Sys_Config( void ) {}

	void Com_Memset( void *dest, const int val, const size_t count ) { memset( dest, val, count ); }
	void Com_Memcpy( void *dest, const void *src, const size_t count ) { memcpy( dest, src, count ); }

	void MSG_InitOOB( msg_t *buf, byte *data, int length ) { (void)buf; (void)data; (void)length; }
	void MSG_WriteLong( msg_t *sb, int c ) { (void)sb; (void)c; }
	void MSG_WriteShort( msg_t *sb, int c ) { (void)sb; (void)c; }
	void MSG_WriteData( msg_t *buf, const void *data, int length ) { (void)buf; (void)data; (void)length; }
	void MSG_BeginReadingOOB( msg_t *msg ) { (void)msg; }
	int MSG_ReadLong( msg_t *msg ) { (void)msg; return 0; }
	int MSG_ReadShort( msg_t *msg ) { (void)msg; return 0; }

	void Huff_Compress( msg_t *buf, int offset ) { (void)buf; (void)offset; }

	char *va( char *format, ... ) {
	static char buffer[1024];
	va_list args;
	va_start( args, format );
	vsnprintf( buffer, sizeof( buffer ), format, args );
	va_end( args );
	return buffer;
	}

	void Com_sprintf( char *dest, int size, const char *fmt, ... ) {
	va_list args;
	va_start( args, fmt );
	vsnprintf( dest, (size_t)size, fmt, args );
	va_end( args );
	}

	void Q_strncpyz( char *dest, const char *src, int destsize ) {
	if ( destsize <= 0 ) {
	return;
	}
	if ( !src ) {
	dest[0] = '\0';
	return;
	}
	strncpy( dest, src, (size_t)(destsize - 1) );
	dest[destsize - 1] = '\0';
	}

	int main(void) {
	netadr_t adr = { NA_IP, {127,0,0,1}, {0}, BigShort(27960) };
	NET_LogAuthTelemetry( NS_SERVER, &adr, "12345", SV_FAKEVACBAN_LABEL, SV_FAKEVACBAN_STATUS, SV_FAKEVACBAN_RESULT_CODE, SV_FAKEVACBAN_OUTCOME, SV_FAKEVACBAN_AUTH_MESSAGE );
	return 0;
	}
        """
    )

    output = _compile_and_run(source, tmp_path / "fakevac_telemetry")
    lines = [line.strip() for line in output.splitlines() if line.strip()]
    assert lines == [
        "NET: server auth 127.0.0.1:27960 credential=steam steamid=12345 status=failed result=3 outcome=VAC ban on record message=\"Failed to authenticate with Steam: VAC ban on record\"",
    ]
