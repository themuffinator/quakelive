from __future__ import annotations

import shutil
import subprocess
import textwrap
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent

_VOTE_THROTTLE_PROBE = textwrap.dedent(
    """
    #include <ctype.h>
    #include <stdarg.h>
    #include <stdio.h>
    #include <string.h>

    #define QAGAME 1
    #include "g_vote.c"

    level_locals_t level;
    gclient_t localClients[MAX_CLIENTS];
    vmCvar_t g_itemHeight;

    void trap_SendServerCommand( int clientNum, const char *text ) {
        if ( text ) {
            printf("%d:%s\\n", clientNum, text);
        }
    }

    /*
    =============
    qlr_tolower
    =============
    */
    static int qlr_tolower( int ch ) {
        return tolower( ch & 0xff );
    }

    /*
    =============
    va
    =============
    */
    char * QDECL va( const char *format, ... ) {
        static char buffer[4096];
        va_list args;

        va_start( args, format );
        vsnprintf( buffer, sizeof( buffer ), format, args );
        va_end( args );

        buffer[sizeof( buffer ) - 1] = '\\0';
        return buffer;
    }

    /*
    =============
    Q_strncpyz
    =============
    */
    void Q_strncpyz( char *dest, const char *src, int destsize ) {
        size_t count;

        if ( !dest || destsize <= 0 ) {
            return;
        }

        if ( !src ) {
            dest[0] = '\\0';
            return;
        }

        count = destsize > 1 ? (size_t)( destsize - 1 ) : 0;
        if ( count > 0 ) {
            strncpy( dest, src, count );
        }
        dest[count] = '\\0';
    }

    /*
    =============
    Q_stricmp
    =============
    */
    int Q_stricmp( const char *s1, const char *s2 ) {
        if ( !s1 ) {
            s1 = "";
        }
        if ( !s2 ) {
            s2 = "";
        }

        while ( *s1 && *s2 ) {
            int diff = qlr_tolower( *s1++ ) - qlr_tolower( *s2++ );
            if ( diff ) {
                return diff;
            }
        }

        return qlr_tolower( *s1 ) - qlr_tolower( *s2 );
    }

    /*
    =============
    trap_SetConfigstring
    =============
    */
    void trap_SetConfigstring( int num, const char *string ) {
        (void)num;
        (void)string;
    }

    /*
    =============
    trap_Cvar_Set
    =============
    */
    void trap_Cvar_Set( const char *var_name, const char *value ) {
        (void)var_name;
        (void)value;
    }

    /*
    =============
    trap_SendConsoleCommand
    =============
    */
    void trap_SendConsoleCommand( int exec_when, const char *text ) {
        (void)exec_when;
        (void)text;
    }

    /*
    =============
    Cmd_ShuffleTeams_f
    =============
    */
    void Cmd_ShuffleTeams_f( void ) {}

    /*
    =============
    TeamCount
    =============
    */
    team_t TeamCount( int ignoreClientNum, int team ) {
        (void)ignoreClientNum;
        (void)team;
        return TEAM_FREE;
    }

    /*
    =============
    G_BroadcastItemTimerState
    =============
    */
    void G_BroadcastItemTimerState( int enabled, int height ) {
        (void)enabled;
        (void)height;
    }

    int main(void) {
        memset(&level, 0, sizeof(level));
        memset(localClients, 0, sizeof(localClients));

        level.maxclients = 1;
        level.clients = localClients;

        G_InitClientVoteThrottle(&level.clients[0]);
        level.clients[0].pers.connected = CON_CONNECTED;

        level.time = 1000;
        level.framenum = 0;

        G_RegisterVoteCall(&level.clients[0], 0, 7);

        level.time = level.clients[0].pers.voteDelayTime + VOTE_THROTTLE_MSEC - 1;
        level.framenum = 1;
        G_UpdateVoteThrottle();

        level.time = level.clients[0].pers.voteDelayTime + VOTE_THROTTLE_MSEC;
        level.framenum = 2;
        G_UpdateVoteThrottle();

        level.time += 100;
        level.framenum = 3;
        G_UpdateVoteThrottle();

        G_RegisterVoteCall(&level.clients[0], 0, 9);

        level.time = level.clients[0].pers.voteDelayTime + VOTE_THROTTLE_MSEC - 1;
        level.framenum = 4;
        G_UpdateVoteThrottle();

        level.time = level.clients[0].pers.voteDelayTime + VOTE_THROTTLE_MSEC;
        level.framenum = 5;
        G_UpdateVoteThrottle();

        level.framenum = 6;
        G_UpdateVoteThrottle();

        return 0;
    }
    """
)


def test_vote_ui_throttle_transitions(tmp_path: Path) -> None:
    """The vote UI disables immediately and re-enables only after the throttle."""

    workdir = tmp_path / "vote_throttle"
    workdir.mkdir(parents=True, exist_ok=True)

    c_path = workdir / "probe.c"
    c_path.write_text(_VOTE_THROTTLE_PROBE, encoding="utf-8")
    exe_path = workdir / "probe"

    include_args = [
        f"-I{REPO_ROOT / 'src' / 'code' / 'game'}",
        f"-I{REPO_ROOT / 'src' / 'code'}",
        f"-I{REPO_ROOT / 'src'}",
    ]
    compiler = shutil.which("gcc")
    if compiler is None:
        pytest.skip("gcc is not available for the standalone vote-throttle probe")

    compile_cmd = [
        compiler,
        "-std=c99",
        "-Wall",
        "-Werror",
        *include_args,
        str(c_path),
        "-o",
        str(exe_path),
    ]
    subprocess.run(compile_cmd, check=True, cwd=REPO_ROOT)

    result = subprocess.run([str(exe_path)], check=True, capture_output=True, text=True, cwd=REPO_ROOT)

    lines = [line for line in result.stdout.splitlines() if line.strip()]
    assert lines == [
        "0:disable_vote_ui",
        "0:enable_vote_ui",
        "0:disable_vote_ui",
        "0:enable_vote_ui",
    ]
