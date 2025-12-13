from __future__ import annotations

import subprocess
import textwrap
from pathlib import Path
from typing import Dict, Tuple

REPO_ROOT = Path(__file__).resolve().parent.parent

_SERVICE_TABLE_PROBE = textwrap.dedent(
    """
    #include <stdio.h>

    #include "src/common/platform/platform_services.c"
    #include "src/common/platform/platform_steamworks.c"

    static void dump_descriptor(const char *label, const ql_platform_feature_descriptor *descriptor) {
        const char *provider = descriptor && descriptor->provider ? descriptor->provider : "<null>";
        printf("%s|%s|%d|%d\\n", label, provider,
            descriptor && descriptor->compiled ? 1 : 0,
            descriptor && descriptor->initialised ? 1 : 0);
    }

    int main(void) {
        const ql_platform_service_table *services = QL_GetPlatformServices();
        dump_descriptor("auth", &services->auth);
        dump_descriptor("matchmaking", &services->matchmaking);
        dump_descriptor("workshop", &services->workshop);
        dump_descriptor("overlay", &services->overlay);
        dump_descriptor("stats", &services->stats);
        return 0;
    }
    """
)

_HYBRID_FALLBACK_PROBE = textwrap.dedent(
    """
    #include <stdio.h>
    #include <stdarg.h>
    #include <string.h>
    #include <ctype.h>

    #include "client.h"

    #include "src/common/platform/platform_services.c"
    #include "src/common/platform/platform_steamworks.c"
    #include "src/common/platform/backends/platform_backend_steamworks.c"
    #include "src/common/platform/backends/platform_backend_open_steam.c"
    #include "src/code/client/ql_auth.c"

    static int qlower(int ch) {
        return tolower(ch & 0xff);
    }

    void Com_Printf( const char *fmt, ... ) {
        va_list args;
        va_start(args, fmt);
        vfprintf(stderr, fmt, args);
        va_end(args);
    }

    void Com_sprintf( char *dest, int size, const char *fmt, ... ) {
        if ( !dest || size <= 0 ) {
            return;
        }

        va_list args;
        va_start(args, fmt);
        int written = vsnprintf(dest, (size_t)size, fmt, args);
        (void)written;
        va_end(args);

        dest[size - 1] = 0;
    }

    void Q_strncpyz( char *dest, const char *src, int destsize ) {
        if ( !dest || destsize <= 0 ) {
            return;
        }

        if ( !src ) {
            dest[0] = 0;
            return;
        }

        size_t count = destsize > 1 ? (size_t)(destsize - 1) : (size_t)0;
        if ( count == 0 ) {
            dest[0] = 0;
            return;
        }

        strncpy(dest, src, count);
        dest[count] = 0;
    }

    int Q_stricmp( const char *s1, const char *s2 ) {
        if ( !s1 ) {
            s1 = "";
        }
        if ( !s2 ) {
            s2 = "";
        }

        while ( *s1 && *s2 ) {
            int diff = qlower(*s1++) - qlower(*s2++);
            if ( diff ) {
                return diff;
            }
        }

        return qlower(*s1) - qlower(*s2);
    }

    int Q_stricmpn( const char *s1, const char *s2, int n ) {
        if ( n <= 0 ) {
            return 0;
        }

        if ( !s1 ) {
            s1 = "";
        }
        if ( !s2 ) {
            s2 = "";
        }

        while ( n-- > 0 ) {
            unsigned char c1 = (unsigned char)*s1++;
            unsigned char c2 = (unsigned char)*s2++;
            int diff = qlower(c1) - qlower(c2);
            if ( diff || !c1 || !c2 ) {
                return diff;
            }
        }

        return 0;
    }

    const char *QL_GetCredentialLabel( const ql_auth_credential_t *credential ) {
        if ( !credential ) {
            return "unknown";
        }

        switch ( credential->kind ) {
            case QL_AUTH_CREDENTIAL_LEGACY_CDKEY:
                return "legacy_cdkey";
            case QL_AUTH_CREDENTIAL_STEAM:
                return "steam";
            case QL_AUTH_CREDENTIAL_STANDALONE_TOKEN:
                return "standalone";
            default:
                return "unknown";
        }
    }

    int main(void) {
        ql_auth_credential_t credential;
        memset(&credential, 0, sizeof(credential));
        credential.kind = QL_AUTH_CREDENTIAL_STEAM;
        Q_strncpyz(credential.value, "retry:TICKET-ABCDEFGHIJKLMNOP", sizeof(credential.value));
        credential.length = strlen(credential.value);

        ql_auth_response_t response;
        memset(&response, 0, sizeof(response));

        qboolean handled = QL_Auth_ExecuteRequest(&credential, &response);

        printf("handled=%d\\n", handled ? 1 : 0);
        printf("result=%d\\n", response.result);
        printf("outcome=%d\\n", response.outcome);
        printf("message=%s\\n", response.message);
        return 0;
    }
    """
)


def _compile_and_run(
    workdir: Path,
    source: str,
    macros: Dict[str, int],
    *,
    include_client_stub: bool = False,
) -> str:
    workdir.mkdir(parents=True, exist_ok=True)
    c_path = workdir / "probe.c"
    c_path.write_text(source, encoding="utf-8")
    exe_path = workdir / "probe"

    include_args = [f"-I{REPO_ROOT}", "-Isrc/common", "-Isrc/code", "-Isrc/code/game", "-Isrc/code/qcommon"]
    if include_client_stub:
        include_args.insert(0, "-Itests/stubs")

    macro_args = [f"-D{key}={value}" for key, value in macros.items()]

    compile_cmd = [
        "gcc",
        "-std=c99",
        "-Wall",
        "-Werror",
        *include_args,
        *macro_args,
        str(c_path),
        "-ldl",
        "-o",
        str(exe_path),
    ]

    if include_client_stub:
        compile_cmd.insert(4, "-Wno-error")

    subprocess.run(compile_cmd, cwd=REPO_ROOT, check=True, capture_output=True)
    result = subprocess.run([str(exe_path)], cwd=REPO_ROOT, check=True, capture_output=True, text=True)
    return result.stdout


def _parse_service_output(output: str) -> Dict[str, Tuple[str, bool, bool]]:
    services: Dict[str, Tuple[str, bool, bool]] = {}
    for line in output.strip().splitlines():
        label, provider, compiled, initialised = line.split("|", 3)
        services[label] = (provider, compiled == "1", initialised == "1")
    return services


def test_platform_service_table_tracks_build_flags(tmp_path) -> None:
    scenarios = [
            (
                {"QL_BUILD_STEAMWORKS": 1, "QL_BUILD_OPEN_STEAM": 0},
                {
                    "auth": ("Steamworks", True, False),
                    "matchmaking": ("Steamworks", True, False),
                    "workshop": ("Steam UGC", True, False),
                    "overlay": ("Steam Overlay", True, False),
                    "stats": ("Steam Stats", True, False),
                },
            ),
            (
                {"QL_BUILD_STEAMWORKS": 0, "QL_BUILD_OPEN_STEAM": 1},
                {
                    "auth": ("Open Steam Adapter", True, True),
                    "matchmaking": ("GameNetworkingSockets", True, True),
                    "workshop": ("REST UGC Service", True, True),
                    "overlay": ("In-Process UI Overlay", True, True),
                    "stats": ("Metrics REST Adapter", True, True),
                },
            ),
            (
                {"QL_BUILD_STEAMWORKS": 1, "QL_BUILD_OPEN_STEAM": 1},
                {
                    "auth": ("Hybrid", True, True),
                    "matchmaking": ("Hybrid: Steamworks + GameNetworkingSockets", True, True),
                    "workshop": ("Hybrid: Steam UGC + REST Mirror", True, True),
                    "overlay": ("Hybrid: Steam Overlay + In-Process UI", True, True),
                    "stats": ("Hybrid: Steam Stats + Metrics REST", True, True),
                },
            ),
        ]

    for idx, (macros, expected) in enumerate(scenarios):
        workdir = tmp_path / f"service_probe_{idx}"
        output = _compile_and_run(workdir, _SERVICE_TABLE_PROBE, macros)
        services = _parse_service_output(output)
        assert services == expected


def test_hybrid_fallback_accepts_when_steam_pending(tmp_path) -> None:
    workdir = tmp_path / "hybrid_fallback"
    output = _compile_and_run(
        workdir,
        _HYBRID_FALLBACK_PROBE,
        {"QL_BUILD_STEAMWORKS": 1, "QL_BUILD_OPEN_STEAM": 1},
        include_client_stub=True,
    )

    details = dict(line.split("=", 1) for line in output.strip().splitlines())

    assert details["handled"] == "1"
    assert details["result"] == str(QL_AUTH_RESULT_ACCEPTED := 1)
    assert details["outcome"] == str(QL_AUTH_OUTCOME_SUCCESS := 0)
    assert "Hybrid fallback accepted credential via open adapter" in details["message"]
