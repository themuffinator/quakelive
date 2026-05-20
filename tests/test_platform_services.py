from __future__ import annotations

import json
import re
import subprocess
import shutil
import textwrap
import os
from pathlib import Path
from typing import Dict, Tuple

import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent

_SERVICE_TABLE_PROBE = textwrap.dedent(
    """
    #include <stdio.h>

    #include "src/common/platform/platform_services.c"

#ifndef QL_STEAMWORKS_INIT_RESULT
#define QL_STEAMWORKS_INIT_RESULT 1
#endif

#if QL_BUILD_STEAMWORKS
/*
=============
QL_Steamworks_Init
=============
*/
qboolean QL_Steamworks_Init( void ) {
    return QL_STEAMWORKS_INIT_RESULT;
}
#endif

    static int qlower(int ch) {
        return tolower(ch & 0xff);
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

    static void dump_descriptor(const char *label, const ql_platform_feature_descriptor *descriptor) {
        const char *provider = descriptor && descriptor->provider ? descriptor->provider : "<null>";
        const char *policy = QL_DescribePlatformFeaturePolicy(descriptor);
        printf(
            "%s|%s|%s|%d|%d\\n",
            label,
            provider,
            policy,
            descriptor && descriptor->compiled ? 1 : 0,
            descriptor && descriptor->initialised ? 1 : 0
        );
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

_SERVICE_MODE_PROBE = textwrap.dedent(
    """
    #include <stdio.h>

    #include "src/common/platform/platform_services.c"

#ifndef QL_STEAMWORKS_INIT_RESULT
#define QL_STEAMWORKS_INIT_RESULT 1
#endif

#if QL_BUILD_STEAMWORKS
/*
=============
QL_Steamworks_Init
=============
*/
qboolean QL_Steamworks_Init( void ) {
    return QL_STEAMWORKS_INIT_RESULT;
}
#endif

    static int qlower(int ch) {
        return tolower(ch & 0xff);
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

    int main(void) {
        printf("mode=%s\\n", QL_GetOnlineServicesModeLabel());
        printf("policy=%s\\n", QL_GetOnlineServicesPolicyLabel());
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
    #include "src/common/platform/backends/platform_backend_steamworks.c"
    #include "src/common/platform/backends/platform_backend_open_steam.c"
    #include "src/common/auth_credentials.c"
    #include "src/code/client/ql_auth.c"

#ifndef QL_STEAMWORKS_INIT_RESULT
#define QL_STEAMWORKS_INIT_RESULT 1
#endif

/*
=============
QL_Steamworks_Init
=============
*/
qboolean QL_Steamworks_Init( void ) {
    return QL_STEAMWORKS_INIT_RESULT;
}

/*
=============
QL_Steamworks_RunCallbacks
=============
*/
void QL_Steamworks_RunCallbacks( void ) {}

/*
=============
QL_Steamworks_RequestAuthTicket
=============
*/
qboolean QL_Steamworks_RequestAuthTicket( char *ticketBuffer, size_t ticketBufferSize, int *ticketLength, uint32_t *ticketHandle ) {
const char *stubTicket = "retry:TICKET-HYBRID-FALLBACK";

if ( ticketBuffer && ticketBufferSize > 0 ) {
Q_strncpyz( ticketBuffer, stubTicket, (int)ticketBufferSize );
}

if ( ticketLength && ticketBuffer ) {
*ticketLength = (int)strlen( ticketBuffer );
}

(void)ticketHandle;
return qtrue;
}

/*
=============
QL_Steamworks_CancelAuthTicket
=============
*/
qboolean QL_Steamworks_CancelAuthTicket( uint32_t ticketHandle ) {
(void)ticketHandle;
return qtrue;
}

/*
=============
QL_Steamworks_ValidateTicket
=============
*/
qboolean QL_Steamworks_ValidateTicket( const char *ticketHex, ql_auth_response_t *response ) {
(void)ticketHex;
(void)response;
return qfalse;
}

    static int qlower(int ch) {
        return tolower(ch & 0xff);
    }

    void QDECL Com_Printf( const char *fmt, ... ) {
        va_list args;
        va_start(args, fmt);
        vfprintf(stderr, fmt, args);
        va_end(args);
    }

    int QDECL Com_sprintf( char *dest, int size, const char *fmt, ... ) {
        if ( !dest || size <= 0 ) {
            return 0;
        }

        va_list args;
        va_start(args, fmt);
        int written = vsnprintf(dest, (size_t)size, fmt, args);
        va_end(args);

        dest[size - 1] = '\\0';
        return written;
    }

    void Q_strncpyz( char *dest, const char *src, int destsize ) {
        if ( !dest || destsize <= 0 ) {
            return;
        }

        if ( !src ) {
            dest[0] = '\\0';
            return;
        }

        size_t count = destsize > 1 ? (size_t)(destsize - 1) : (size_t)0;
        if ( count == 0 ) {
            dest[0] = '\\0';
            return;
        }

        strncpy(dest, src, count);
        dest[count] = '\\0';
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

/*
=============
CL_OnlineServicesEnabled
=============
*/
qboolean CL_OnlineServicesEnabled( void ) {
#if QL_BUILD_ONLINE_SERVICES
        return qtrue;
#else
        return qfalse;
#endif
}

/*
=============
CL_SteamServicesEnabled
=============
*/
qboolean CL_SteamServicesEnabled( void ) {
#if QL_PLATFORM_HAS_STEAM_SERVICES
        return CL_OnlineServicesEnabled();
#else
        return qfalse;
#endif
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

_POLICY_BLOCKED_AUTH_PROBE = textwrap.dedent(
    """
    #include <stdio.h>
    #include <stdarg.h>
    #include <string.h>
    #include <ctype.h>

    #include "client.h"
    #include "src/common/platform/platform_services.c"
    #include "src/common/auth_credentials.c"
    #include "src/code/client/ql_auth.c"

    static int qlower(int ch) {
        return tolower(ch & 0xff);
    }

    void QDECL Com_Printf( const char *fmt, ... ) {
        va_list args;
        va_start(args, fmt);
        vfprintf(stderr, fmt, args);
        va_end(args);
    }

    int QDECL Com_sprintf( char *dest, int size, const char *fmt, ... ) {
        if ( !dest || size <= 0 ) {
            return 0;
        }

        va_list args;
        va_start(args, fmt);
        int written = vsnprintf(dest, (size_t)size, fmt, args);
        va_end(args);

        dest[size - 1] = '\\0';
        return written;
    }

    void Q_strncpyz( char *dest, const char *src, int destsize ) {
        if ( !dest || destsize <= 0 ) {
            return;
        }

        if ( !src ) {
            dest[0] = '\\0';
            return;
        }

        size_t count = destsize > 1 ? (size_t)(destsize - 1) : (size_t)0;
        if ( count == 0 ) {
            dest[0] = '\\0';
            return;
        }

        strncpy(dest, src, count);
        dest[count] = '\\0';
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

/*
=============
CL_OnlineServicesEnabled
=============
*/
qboolean CL_OnlineServicesEnabled( void ) {
#if QL_BUILD_ONLINE_SERVICES
        return qtrue;
#else
        return qfalse;
#endif
}

/*
=============
CL_SteamServicesEnabled
=============
*/
qboolean CL_SteamServicesEnabled( void ) {
#if QL_PLATFORM_HAS_STEAM_SERVICES
        return CL_OnlineServicesEnabled();
#else
        return qfalse;
#endif
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
    extra_env: Dict[str, str] | None = None,
) -> str:
    workdir.mkdir(parents=True, exist_ok=True)
    c_path = workdir / "probe.c"
    c_path.write_text(source, encoding="utf-8")
    exe_path = workdir / "probe"
    compiler = shutil.which("gcc") or shutil.which("clang") or shutil.which("cc")

    if not compiler:
        pytest.skip("No C compiler found for platform service probe")

    include_args = [f"-I{REPO_ROOT}", "-Isrc/common", "-Isrc/code", "-Isrc/code/game", "-Isrc/code/qcommon"]
    if include_client_stub:
        include_args.insert(0, "-Itests/stubs")

    macro_args = [f"-D{key}={value}" for key, value in macros.items()]
    platform_args = []

    if os.name == "nt":
        platform_args.extend(["-DWIN32", "-D_CRT_SECURE_NO_WARNINGS", "-Wno-return-type"])

    if include_client_stub:
        macro_args.append("-DQL_AUTH_HAS_CLIENT_BACKEND=1")

    compile_cmd = [
        compiler,
        "-std=c99",
        "-Wall",
        "-Werror",
        *platform_args,
        *include_args,
        *macro_args,
        str(c_path),
        "-o",
        str(exe_path),
    ]

    subprocess.run(compile_cmd, cwd=REPO_ROOT, check=True, capture_output=True)
    run_env = os.environ.copy()
    if extra_env:
        run_env.update(extra_env)

    result = subprocess.run(
        [str(exe_path)],
        cwd=REPO_ROOT,
        check=True,
        capture_output=True,
        text=True,
        env=run_env,
    )
    return result.stdout


def _parse_service_output(output: str) -> Dict[str, Tuple[str, str, bool, bool]]:
    services: Dict[str, Tuple[str, str, bool, bool]] = {}
    for line in output.strip().splitlines():
        label, provider, policy, compiled, initialised = line.split("|", 4)
        services[label] = (provider, policy, compiled == "1", initialised == "1")
    return services


def _parse_mode_output(output: str) -> Dict[str, str]:
    return dict(line.split("=", 1) for line in output.strip().splitlines())


def _extract_function_block(text: str, signature: str) -> str:
    start = text.find(signature)
    if start == -1:
        raise AssertionError(f"function signature not found: {signature}")

    brace_start = text.find("{", start)
    if brace_start == -1:
        raise AssertionError(f"opening brace not found for: {signature}")

    depth = 0
    for index in range(brace_start, len(text)):
        char = text[index]
        if char == "{":
            depth += 1
        elif char == "}":
            depth -= 1
            if depth == 0:
                return text[start : index + 1]

    raise AssertionError(f"unterminated function block for: {signature}")


def test_platform_service_table_tracks_build_flags(tmp_path) -> None:
    build_disabled = {
        "auth": ("Build-disabled (QL_BUILD_ONLINE_SERVICES=0)", "compatibility-disabled (QL_BUILD_ONLINE_SERVICES=0)", False, False),
        "matchmaking": ("Build-disabled (QL_BUILD_ONLINE_SERVICES=0)", "compatibility-disabled (QL_BUILD_ONLINE_SERVICES=0)", False, False),
        "workshop": ("Build-disabled (QL_BUILD_ONLINE_SERVICES=0)", "compatibility-disabled (QL_BUILD_ONLINE_SERVICES=0)", False, False),
        "overlay": ("Build-disabled (QL_BUILD_ONLINE_SERVICES=0)", "compatibility-disabled (QL_BUILD_ONLINE_SERVICES=0)", False, False),
        "stats": ("Build-disabled (QL_BUILD_ONLINE_SERVICES=0)", "compatibility-disabled (QL_BUILD_ONLINE_SERVICES=0)", False, False),
    }

    scenarios = [
        (
            {},
            build_disabled,
        ),
        (
            {"QL_BUILD_ONLINE_SERVICES": 0, "QL_BUILD_STEAMWORKS": 1, "QL_BUILD_OPEN_STEAM": 1},
            build_disabled,
        ),
        (
            {"QL_BUILD_ONLINE_SERVICES": 1, "QL_BUILD_STEAMWORKS": 1, "QL_BUILD_OPEN_STEAM": 0},
            {
                "auth": ("Steamworks", "compatibility-only", True, True),
                "matchmaking": ("Steamworks", "compatibility-only", True, True),
                "workshop": ("Steam UGC", "compatibility-only", True, True),
                "overlay": ("Steam Overlay", "compatibility-only", True, True),
                "stats": ("Steam Stats", "compatibility-only", True, True),
            },
        ),
        (
            {"QL_BUILD_ONLINE_SERVICES": 1, "QL_BUILD_STEAMWORKS": 0, "QL_BUILD_OPEN_STEAM": 1},
            {
                "auth": ("Open Steam Adapter", "compatibility-only", True, True),
                "matchmaking": ("GameNetworkingSockets", "compatibility-only", True, True),
                "workshop": ("REST UGC Service", "compatibility-only", True, True),
                "overlay": ("In-Process UI Overlay", "compatibility-only", True, True),
                "stats": ("Metrics REST Adapter", "compatibility-only", True, True),
            },
        ),
        (
            {"QL_BUILD_ONLINE_SERVICES": 1, "QL_BUILD_STEAMWORKS": 1, "QL_BUILD_OPEN_STEAM": 1},
            {
                "auth": ("Hybrid", "compatibility-only", True, True),
                "matchmaking": ("Hybrid: Steamworks + GameNetworkingSockets", "compatibility-only", True, True),
                "workshop": ("Hybrid: Steam UGC + REST Mirror", "compatibility-only", True, True),
                "overlay": ("Hybrid: Steam Overlay + In-Process UI", "compatibility-only", True, True),
                "stats": ("Hybrid: Steam Stats + Metrics REST", "compatibility-only", True, True),
            },
        ),
        (
            {"QL_BUILD_ONLINE_SERVICES": 1, "QL_BUILD_STEAMWORKS": 1, "QL_BUILD_OPEN_STEAM": 0, "QL_STEAMWORKS_INIT_RESULT": 0},
            {
                "auth": ("Steamworks", "compatibility-only provider unavailable", True, False),
                "matchmaking": ("Steamworks", "compatibility-only provider unavailable", True, False),
                "workshop": ("Steam UGC", "compatibility-only provider unavailable", True, False),
                "overlay": ("Steam Overlay", "compatibility-only provider unavailable", True, False),
                "stats": ("Steam Stats", "compatibility-only provider unavailable", True, False),
            },
        ),
        (
            {"QL_BUILD_ONLINE_SERVICES": 1, "QL_BUILD_STEAMWORKS": 1, "QL_BUILD_OPEN_STEAM": 1, "QL_STEAMWORKS_INIT_RESULT": 0},
            {
                "auth": ("Hybrid", "compatibility-only", True, True),
                "matchmaking": ("Hybrid: Steamworks + GameNetworkingSockets", "compatibility-only", True, True),
                "workshop": ("Hybrid: Steam UGC + REST Mirror", "compatibility-only", True, True),
                "overlay": ("Hybrid: Steam Overlay + In-Process UI", "compatibility-only", True, True),
                "stats": ("Hybrid: Steam Stats + Metrics REST", "compatibility-only", True, True),
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
        {"QL_BUILD_ONLINE_SERVICES": 1, "QL_BUILD_STEAMWORKS": 1, "QL_BUILD_OPEN_STEAM": 1},
        include_client_stub=True,
    )

    details = dict(line.split("=", 1) for line in output.strip().splitlines())

    assert details["handled"] == "1"
    assert details["result"] == str(QL_AUTH_RESULT_ACCEPTED := 1)
    assert details["outcome"] == str(QL_AUTH_OUTCOME_SUCCESS := 0)
    assert "Hybrid fallback accepted credential via heuristic open adapter" in details["message"]


def test_platform_service_table_respects_runtime_external_disable_env(tmp_path) -> None:
    workdir = tmp_path / "service_probe_external_disable"
    output = _compile_and_run(
        workdir,
        _SERVICE_TABLE_PROBE,
        {"QL_BUILD_ONLINE_SERVICES": 1, "QL_BUILD_STEAMWORKS": 1, "QL_BUILD_OPEN_STEAM": 1},
        extra_env={"QL_DISABLE_EXTERNAL_ECOSYSTEMS": "1"},
    )

    services = _parse_service_output(output)
    expected = {
        "auth": ("Disabled by QL_DISABLE_EXTERNAL_ECOSYSTEMS", "compatibility-disabled (QL_DISABLE_EXTERNAL_ECOSYSTEMS)", True, False),
        "matchmaking": ("Disabled by QL_DISABLE_EXTERNAL_ECOSYSTEMS", "compatibility-disabled (QL_DISABLE_EXTERNAL_ECOSYSTEMS)", True, False),
        "workshop": ("Disabled by QL_DISABLE_EXTERNAL_ECOSYSTEMS", "compatibility-disabled (QL_DISABLE_EXTERNAL_ECOSYSTEMS)", True, False),
        "overlay": ("Disabled by QL_DISABLE_EXTERNAL_ECOSYSTEMS", "compatibility-disabled (QL_DISABLE_EXTERNAL_ECOSYSTEMS)", True, False),
        "stats": ("Disabled by QL_DISABLE_EXTERNAL_ECOSYSTEMS", "compatibility-disabled (QL_DISABLE_EXTERNAL_ECOSYSTEMS)", True, False),
    }

    assert services == expected


def test_online_services_mode_labels_track_build_flags_and_runtime_policy(tmp_path) -> None:
    scenarios = [
        (
            {},
            {
                "mode": "Build-disabled default (QL_BUILD_ONLINE_SERVICES=0)",
                "policy": "compatibility-disabled (QL_BUILD_ONLINE_SERVICES=0)",
            },
            None,
        ),
        (
            {"QL_BUILD_ONLINE_SERVICES": 0, "QL_BUILD_STEAMWORKS": 1, "QL_BUILD_OPEN_STEAM": 1},
            {
                "mode": "Build-disabled default (QL_BUILD_ONLINE_SERVICES=0)",
                "policy": "compatibility-disabled (QL_BUILD_ONLINE_SERVICES=0)",
            },
            None,
        ),
        (
            {"QL_BUILD_ONLINE_SERVICES": 1, "QL_BUILD_STEAMWORKS": 1, "QL_BUILD_OPEN_STEAM": 0},
            {
                "mode": "Steamworks compatibility lane",
                "policy": "compatibility-opt-in heuristic steamworks",
            },
            None,
        ),
        (
            {"QL_BUILD_ONLINE_SERVICES": 1, "QL_BUILD_STEAMWORKS": 1, "QL_BUILD_OPEN_STEAM": 0, "QL_STEAMWORKS_INIT_RESULT": 0},
            {
                "mode": "Steamworks compatibility lane",
                "policy": "compatibility-opt-in heuristic steamworks (provider unavailable)",
            },
            None,
        ),
        (
            {"QL_BUILD_ONLINE_SERVICES": 1, "QL_BUILD_STEAMWORKS": 0, "QL_BUILD_OPEN_STEAM": 1},
            {
                "mode": "Open-adapter compatibility lane",
                "policy": "compatibility-opt-in heuristic open-adapter",
            },
            None,
        ),
        (
            {"QL_BUILD_ONLINE_SERVICES": 1, "QL_BUILD_STEAMWORKS": 1, "QL_BUILD_OPEN_STEAM": 1},
            {
                "mode": "Hybrid compatibility lane",
                "policy": "compatibility-opt-in heuristic hybrid",
            },
            None,
        ),
        (
            {"QL_BUILD_ONLINE_SERVICES": 1, "QL_BUILD_STEAMWORKS": 1, "QL_BUILD_OPEN_STEAM": 1},
            {
                "mode": "Externally-disabled compatibility lane",
                "policy": "compatibility-disabled (QL_DISABLE_EXTERNAL_ECOSYSTEMS)",
            },
            {"QL_DISABLE_EXTERNAL_ECOSYSTEMS": "1"},
        ),
    ]

    for idx, (macros, expected, extra_env) in enumerate(scenarios):
        workdir = tmp_path / f"service_mode_probe_{idx}"
        output = _compile_and_run(
            workdir,
            _SERVICE_MODE_PROBE,
            macros,
            extra_env=extra_env,
        )
        details = _parse_mode_output(output)
        assert details == expected


def test_online_service_bridge_only_hard_stubs_when_build_disabled() -> None:
    cl_cgame = (REPO_ROOT / "src/code/client/cl_cgame.c").read_text(encoding="utf-8")
    cl_main = (REPO_ROOT / "src/code/client/cl_main.c").read_text(encoding="utf-8")
    cl_ui = (REPO_ROOT / "src/code/client/cl_ui.c").read_text(encoding="utf-8")
    ui_main = (REPO_ROOT / "src/code/ui/ui_main.c").read_text(encoding="utf-8")

    refresh_block = _extract_function_block(cl_cgame, "void CL_RefreshOnlineServicesBridgeState( void )")
    assert "#if !QL_PLATFORM_HAS_ONLINE_SERVICES" in refresh_block
    assert 'Cvar_Set( "ui_browserAwesomium", "0" );' in refresh_block
    assert 'Cvar_Set( "ui_browserAwesomiumProvider", overlayProvider );' in refresh_block
    assert 'Cvar_Set( "ui_browserAwesomiumPolicy", overlayPolicy );' in refresh_block
    assert 'Cvar_Set( "ui_advertisementBridgeProvider", advertProvider );' in refresh_block
    assert 'Cvar_Set( "ui_advertisementBridgePolicy", advertPolicy );' in refresh_block
    assert "CL_GetOverlayServiceDescriptor()" in refresh_block
    assert 'Cvar_Set( "ui_browserAwesomium", overlayAvailable ? "1" : "0" );' in refresh_block
    assert "CL_GetOverlayServiceProviderLabel()" in refresh_block
    assert "CL_GetOverlayServicePolicyLabel()" in refresh_block
    assert 'Cvar_Get ("ui_browserAwesomiumProvider", "Unavailable", CVAR_ROM );' in cl_main
    assert 'Cvar_Get ("ui_browserAwesomiumPolicy", "compatibility-unavailable", CVAR_ROM );' in cl_main
    assert 'Cvar_Get ("ui_advertisementBridgeProvider", "Unavailable", CVAR_ROM );' in cl_main
    assert 'Cvar_Get ("ui_advertisementBridgePolicy", "compatibility-unavailable", CVAR_ROM );' in cl_main

    assert '#include "../../common/platform/platform_config.h"' in ui_main
    assert "#define UI_BROWSER_AWESOMIUM_DEFAULT \"0\"" in ui_main
    assert '"ui_browserAwesomium", UI_BROWSER_AWESOMIUM_DEFAULT, CVAR_TEMP' in ui_main

    show_browser_block = _extract_function_block(cl_cgame, "void CL_Web_ShowBrowser_f( void )")
    assert "#if !QL_PLATFORM_HAS_ONLINE_SERVICES" in show_browser_block
    assert "CL_RefreshOnlineServicesBridgeState();" in show_browser_block
    assert "CL_OnlineServicesEnabled()" not in show_browser_block

    advert_init_block = _extract_function_block(cl_cgame, "static void CL_AdvertisementBridge_InitCGame( void )")
    assert "cl_advertisementBridge.initialised = qtrue;" in advert_init_block
    assert "CL_RefreshOnlineServicesBridgeState();" in advert_init_block

    import82_block = _extract_function_block(cl_ui, "static void QDECL QL_UI_trap_InitAdvertisementBridge( void )")
    assert "CL_AdvertisementBridge_InitUI();" in import82_block

    init_ui_block = _extract_function_block(cl_ui, "void CL_InitUI( void )")
    assert "CL_RefreshOnlineServicesBridgeState();" in init_ui_block


def test_service_disabled_menu_verb_matrix_stays_explicit() -> None:
    cl_cgame = (REPO_ROOT / "src/code/client/cl_cgame.c").read_text(encoding="utf-8")
    ui_main = (REPO_ROOT / "src/code/ui/ui_main.c").read_text(encoding="utf-8")

    overlay_log_block = _extract_function_block(
        cl_cgame, "static void CL_LogOverlayServiceIgnored( const char *commandName, const char *reason ) {"
    )
    show_browser_block = _extract_function_block(cl_cgame, "void CL_Web_ShowBrowser_f( void )")
    change_hash_block = _extract_function_block(cl_cgame, "void CL_Web_ChangeHash_f( void )")
    browser_active_block = _extract_function_block(cl_cgame, "void CL_Web_BrowserActive_f( void )")
    stop_refresh_block = _extract_function_block(cl_cgame, "void CL_Web_StopRefresh_f( void )")
    deferred_exec_block = _extract_function_block(
        ui_main, "qboolean UI_HandleDeferredScriptExec( const itemDef_t *item, const char *commandText ) {"
    )

    assert 'Com_DPrintf( "%s ignored: %s (%s [%s])\\n",' in overlay_log_block
    assert "CL_GetOverlayServiceProviderLabel()" in overlay_log_block
    assert "CL_GetOverlayServicePolicyLabel()" in overlay_log_block
    assert 'CL_LogOverlayServiceIgnored( "web_showBrowser", "online services disabled by build settings" );' in show_browser_block
    assert 'CL_LogOverlayServiceIgnored( "web_showBrowser", "browser overlay provider unavailable" );' in show_browser_block
    assert 'CL_LogOverlayServiceIgnored( "web_changeHash", "online services disabled by build settings" );' in change_hash_block
    assert 'CL_LogOverlayServiceIgnored( "web_changeHash", "browser overlay provider unavailable" );' in change_hash_block
    assert 'CL_LogOverlayServiceIgnored( "web_browserActive", "online services disabled by build settings" );' in browser_active_block
    assert 'CL_LogOverlayServiceIgnored( "web_browserActive", "browser overlay provider unavailable" );' in browser_active_block
    assert 'CL_LogOverlayServiceIgnored( "web_stopRefresh", "online services disabled by build settings" );' in stop_refresh_block
    assert 'CL_LogOverlayServiceIgnored( "web_stopRefresh", "browser overlay provider unavailable" );' in stop_refresh_block

    assert 'Com_Printf( "UI: browser overlay unavailable; opening bridge server browser.\\n" );' in deferred_exec_block
    assert 'Com_Printf( "UI: browser overlay unavailable; keeping native menu fallback for %s.\\n", commandText );' in deferred_exec_block


def test_awesomium_menu_flow_clears_browser_overlay_for_gameplay() -> None:
    ui_main = (REPO_ROOT / "src/code/ui/ui_main.c").read_text(encoding="utf-8")

    init_block = _extract_function_block(ui_main, "void _UI_Init( qboolean inGameLoad ) {")
    set_active_menu_block = _extract_function_block(ui_main, "void _UI_SetActiveMenu( uiMenuCommand_t menu ) {")

    assert "Menus_CloseAll();" in init_block
    assert "UI_SetBrowserActive( qfalse );" in init_block
    assert "UI_BrowserBridge_SetActive( qfalse );" in init_block

    main_case = re.search(r"case UIMENU_MAIN:(.*?)return;", set_active_menu_block, re.DOTALL)
    none_case = re.search(r"case UIMENU_NONE:(.*?)return;", set_active_menu_block, re.DOTALL)
    ingame_case = re.search(r"case UIMENU_INGAME:(.*?)return;", set_active_menu_block, re.DOTALL)

    assert main_case is not None
    assert none_case is not None
    assert ingame_case is not None

    assert "static qboolean UI_MenuFlowUsesBrowserOverlay(uiMenuFlow_t flow) {" in ui_main
    assert "flow == UI_MENU_FLOW_QUAKELIVE && UI_BrowserOverlayAvailable()" in ui_main
    assert "UI_SetBrowserActive( UI_MenuFlowUsesBrowserOverlay( ui_activeMenuFlow ) );" in main_case.group(1)
    assert "UI_BrowserBridge_SetActive( ui_activeMenuFlow == UI_MENU_FLOW_BRIDGED );" in main_case.group(1)
    assert "UI_SetBrowserActive( qfalse );" in none_case.group(1)
    assert "UI_BrowserBridge_SetActive( qfalse );" in none_case.group(1)
    assert "UI_SetBrowserActive( qfalse );" in ingame_case.group(1)
    assert "UI_BrowserBridge_SetActive( qfalse );" in ingame_case.group(1)


def test_disabled_online_services_no_longer_force_console_fallback() -> None:
    cl_main = (REPO_ROOT / "src/code/client/cl_main.c").read_text(encoding="utf-8")
    cl_scrn = (REPO_ROOT / "src/code/client/cl_scrn.c").read_text(encoding="utf-8")
    client_h = (REPO_ROOT / "src/code/client/client.h").read_text(encoding="utf-8")

    assert "CL_UseDisconnectedConsoleFallback" not in client_h
    assert "CL_UseDisconnectedConsoleFallback" not in cl_main
    assert "CL_UseDisconnectedConsoleFallback" not in cl_scrn
    assert "disconnected console fallback active" not in cl_main
    assert "fallback draw path active" not in cl_scrn

    frame_block = _extract_function_block(cl_main, "void CL_Frame ( int msec ) {")
    assert 'VM_Call( uivm, UI_SET_ACTIVE_MENU, UIMENU_MAIN );' in frame_block
    assert "cls.keyCatchers = KEYCATCH_CONSOLE;" not in frame_block
    assert "S_StopBackgroundTrack();" not in frame_block

    draw_block = _extract_function_block(cl_scrn, "void SCR_DrawScreenField( stereoFrame_t stereoFrame ) {")
    assert "uiFullscreen = VM_Call( uivm, UI_IS_FULLSCREEN ) ? qtrue : qfalse;" in draw_block
    assert 'VM_Call( uivm, UI_SET_ACTIVE_MENU, UIMENU_MAIN );' in draw_block
    assert "consoleFallback" not in draw_block


def test_native_cgame_avatar_import_routes_through_steam_shader_cache() -> None:
    cl_cgame = (REPO_ROOT / "src/code/client/cl_cgame.c").read_text(encoding="utf-8")
    block = _extract_function_block(
        cl_cgame,
        "static qhandle_t QDECL QL_CG_trap_GetAvatarImageHandle( unsigned int identityLow, unsigned int identityHigh )",
    )

    assert "CL_SteamServicesEnabled()" not in block
    assert "QL_CG_CombineIdentityWords( identityLow, identityHigh )" in block
    assert 'Com_sprintf( url, sizeof( url ), "steam://avatar/large/%llu"' in block
    assert "CL_Steam_RegisterShader( url )" in block


def test_steam_resource_bridge_reconstructs_avatar_url_fetches() -> None:
    steam_resources = (REPO_ROOT / "src/code/client/cl_steam_resources.c").read_text(encoding="utf-8")
    steamworks = (REPO_ROOT / "src/common/platform/platform_steamworks.c").read_text(encoding="utf-8")
    cl_main = (REPO_ROOT / "src/code/client/cl_main.c").read_text(encoding="utf-8")
    client_h = (REPO_ROOT / "src/code/client/client.h").read_text(encoding="utf-8")

    avatar_block = _extract_function_block(
        steam_resources,
        "static qboolean CL_SteamResources_RequestAvatarRGBA( const char *url, byte **outPixels, int *outWidth, int *outHeight )",
    )
    shader_block = _extract_function_block(
        steam_resources,
        "qhandle_t CL_Steam_RegisterShader( const char *url ) {",
    )
    refresh_cvars_block = _extract_function_block(
        steam_resources,
        "static void CL_RefreshSteamResourceBridgeCvars( void ) {",
    )
    resources_init_block = _extract_function_block(steam_resources, "void CL_InitSteamResources( void ) {")
    resources_shutdown_block = _extract_function_block(steam_resources, "void CL_ShutdownSteamResources( void ) {")
    request_avatar_image_block = _extract_function_block(
        steamworks,
        "ql_steam_avatar_image_state_t QL_Steamworks_RequestAvatarImage( uint32_t idLow, uint32_t idHigh, ql_steam_avatar_size_t size, int *outImage )",
    )
    load_avatar_block = _extract_function_block(
        steamworks,
        "qboolean QL_Steamworks_LoadAvatarRGBA( uint32_t idLow, uint32_t idHigh, ql_steam_avatar_size_t size, uint8_t **outPixels, uint32_t *outWidth, uint32_t *outHeight )",
    )

    assert "CL_SteamResources_ParseAvatarURL( url, &size, &idLow, &idHigh )" in avatar_block
    assert "QL_Steamworks_RequestAvatarImage( idLow, idHigh, size, NULL )" in avatar_block
    assert "avatarState == QL_STEAM_AVATAR_IMAGE_PENDING" in avatar_block
    assert "CL_SteamResources_MarkPendingAvatar( idLow, idHigh );" in avatar_block
    assert "CL_SteamResources_ClearPendingAvatar( idLow, idHigh );" in avatar_block
    assert "QL_Steamworks_LoadAvatarRGBA( idLow, idHigh, size, &rgbaPixels, &width, &height )" in avatar_block
    assert "width == 0 || height == 0 || width > INT_MAX || height > INT_MAX" in avatar_block
    assert "*outPixels = rgbaPixels;" in avatar_block
    assert "*outWidth = (int)width;" in avatar_block
    assert "*outHeight = (int)height;" in avatar_block
    assert "CL_SteamResources_EncodeAvatarTGA" not in avatar_block

    assert "qhandle_t CL_RegisterShaderFromRGBA( const char *name, const byte *pic, int width, int height, qboolean mipRawImage );" in client_h
    assert "qhandle_t CL_RegisterShaderFromRGBA( const char *name, const byte *pic, int width, int height, qboolean mipRawImage ) {" in cl_main
    assert "image = R_CreateImage( name, pic, width, height, mipRawImage, mipRawImage, mipRawImage ? GL_REPEAT : GL_CLAMP );" in cl_main
    assert "if ( image == -1 ) {" in request_avatar_image_block
    assert "return QL_STEAM_AVATAR_IMAGE_PENDING;" in request_avatar_image_block
    assert "QL_Steamworks_RequestAvatarImage( idLow, idHigh, size, &image ) != QL_STEAM_AVATAR_IMAGE_READY" in load_avatar_block
    assert "CL_SteamResources_RegisterAvatarCallbacks();" in resources_init_block
    assert "CL_SteamResources_UnregisterAvatarCallbacks();" in resources_shutdown_block
    assert "CL_SteamResources_ClearPendingAvatars();" in resources_init_block
    assert "CL_SteamResources_ClearPendingAvatars();" in resources_shutdown_block or "CL_SteamResources_ClearPendingAvatars();" in steam_resources

    assert "if ( CL_SteamResources_IsAvatarURL( url ) ) {" in shader_block
    assert "CL_SteamResources_RequestAvatarRGBA( url, &rgbaPixels, &width, &height )" in shader_block
    assert "shader = CL_RegisterShaderFromRGBA( rendererName, rgbaPixels, width, height, qfalse );" in shader_block
    assert "QL_Steamworks_FreeBuffer( rgbaPixels );" in shader_block
    assert "CL_SteamResources_EncodeAvatarTGA" not in shader_block
    assert '".tga"' not in steam_resources
    assert 'Cvar_Set( "ui_resourceBridgeProvider", CL_GetSteamResourceServiceProviderLabel() );' in refresh_cvars_block
    assert 'Cvar_Set( "ui_resourceBridgePolicy", CL_GetSteamResourceServicePolicyLabel() );' in refresh_cvars_block
    assert "CL_RefreshSteamResourceBridgeCvars();" in resources_init_block

    assert "friendsVTable" in request_avatar_image_block
    assert "utilsVTable" in load_avatar_block
    assert "QL_Steamworks_GetAvatarMethodIndex( size )" in request_avatar_image_block
    assert "utilsVTable[0x14 / 4]" in load_avatar_block
    assert "utilsVTable[0x18 / 4]" in load_avatar_block


def test_client_steam_callback_owner_reconstructs_retail_frame_pump_and_lifecycle() -> None:
    cl_main = (REPO_ROOT / "src/code/client/cl_main.c").read_text(encoding="utf-8")

    frame_block = _extract_function_block(cl_main, "void CL_Frame ( int msec ) {")
    steam_frame_block = _extract_function_block(cl_main, "static void SteamClient_Frame( void )")
    init_block = _extract_function_block(cl_main, "void CL_Init( void ) {")
    shutdown_block = _extract_function_block(cl_main, "void CL_Shutdown( void ) {")
    steam_callbacks_init_block = _extract_function_block(cl_main, "static qboolean SteamCallbacks_Init( void ) {")
    steam_micro_callbacks_init_block = _extract_function_block(cl_main, "static qboolean SteamMicroCallbacks_Init( void ) {")
    steam_lobby_callbacks_init_block = _extract_function_block(cl_main, "static qboolean SteamLobbyCallbacks_Init( void ) {")
    steam_lobby_init_block = _extract_function_block(cl_main, "static qboolean SteamLobby_Init( void ) {")
    workshop_callback_init_block = _extract_function_block(
        cl_main, "static qboolean CL_Steam_RegisterWorkshopCallbacks( const char *workshopProvider, const char *workshopPolicy ) {"
    )
    callback_shutdown_block = _extract_function_block(cl_main, "static void CL_Steam_ShutdownCallbacks( void ) {")
    callback_bootstrap_log_block = _extract_function_block(
        cl_main, "static void CL_LogClientCallbackBootstrapFallback( const char *reason ) {"
    )
    stats_gate_block = _extract_function_block(cl_main, "static qboolean CL_Steam_ShouldRegisterStatsClear( void ) {")
    stats_clear_block = _extract_function_block(cl_main, "static void CL_Steam_ClearStats_f( void )")

    assert "SteamClient_Frame();" in frame_block
    assert frame_block.index("SteamClient_Frame();") < frame_block.index("CL_CheckForResend();")
    assert "CL_WebHost_Frame();" in frame_block
    assert frame_block.index("CL_WebHost_Frame();") < frame_block.index("CL_CheckForResend();")
    assert "CL_Steam_ProcessStatsReportPackets();" in steam_frame_block

    assert "static const ql_platform_feature_descriptor *CL_GetMatchmakingServiceDescriptor( void ) {" in cl_main
    assert "static const ql_platform_feature_descriptor *CL_GetStatsServiceDescriptor( void ) {" in cl_main
    assert "void CL_LogMatchmakingServiceIgnored( const char *commandName, const char *reason ) {" in cl_main
    assert "static void CL_LogStatsServiceIgnored( const char *commandName, const char *reason ) {" in cl_main
    assert "static void CL_LogStatsServiceRegistrationSkipped( const char *reason ) {" in cl_main
    assert "static void CL_RefreshPlatformServiceCvars( void ) {" in cl_main
    steam_client_init_block = _extract_function_block(cl_main, "void SteamClient_Init( void ) {")
    assert "cl_statsClearRegistered = qfalse;" not in init_block
    assert "if ( CL_Steam_ShouldRegisterStatsClear() ) {" not in init_block
    assert 'Cmd_AddCommand ("stats_clear", CL_Steam_ClearStats_f );' not in init_block
    assert "cl_statsClearRegistered = qfalse;" in steam_client_init_block
    assert "if ( CL_Steam_ShouldRegisterStatsClear() ) {" in steam_client_init_block
    assert 'Cmd_AddCommand ("stats_clear", CL_Steam_ClearStats_f );' in steam_client_init_block
    assert 'Cvar_Get ("ui_resourceBridgeProvider", "Unavailable", CVAR_ROM );' in init_block
    assert 'Cvar_Get ("ui_resourceBridgePolicy", "compatibility-unavailable", CVAR_ROM );' in init_block
    assert 'Cvar_Get ("ui_subscriptionBridgeMode", "Unavailable", CVAR_ROM );' in init_block
    assert 'Cvar_Get ("ui_subscriptionBridgePolicy", "compatibility-unavailable", CVAR_ROM );' in init_block
    assert 'Cvar_Get ("cl_onlineServicesMode", "Unavailable", CVAR_ROM );' in init_block
    assert 'Cvar_Get ("cl_onlineServicesPolicy", "compatibility-unavailable", CVAR_ROM );' in init_block
    assert 'Cvar_Get ("cl_identityBootstrapMode", "Unavailable", CVAR_ROM );' in init_block
    assert 'Cvar_Get ("cl_identityBootstrapPolicy", "compatibility-unavailable", CVAR_ROM );' in init_block
    assert 'Cvar_Get ("cl_voiceServiceMode", "Unavailable", CVAR_ROM );' in init_block
    assert 'Cvar_Get ("cl_voiceServicePolicy", "compatibility-unavailable", CVAR_ROM );' in init_block
    assert 'Cvar_Get ("cl_workshopProvider", "Unavailable", CVAR_ROM );' in init_block
    assert 'Cvar_Get ("cl_workshopPolicy", "compatibility-unavailable", CVAR_ROM );' in init_block
    assert 'Cvar_Get ("cl_matchmakingProvider", "Unavailable", CVAR_ROM );' in init_block
    assert 'Cvar_Get ("cl_matchmakingPolicy", "compatibility-unavailable", CVAR_ROM );' in init_block
    assert 'Cvar_Get ("cl_statsProvider", "Unavailable", CVAR_ROM );' in init_block
    assert 'Cvar_Get ("cl_statsPolicy", "compatibility-unavailable", CVAR_ROM );' in init_block
    assert 'Cvar_Get ("cl_socialOverlayProvider", "Unavailable", CVAR_ROM );' in init_block
    assert 'Cvar_Get ("cl_socialOverlayPolicy", "compatibility-unavailable", CVAR_ROM );' in init_block
    steam_client_init_block = _extract_function_block(cl_main, "void SteamClient_Init( void ) {")
    assert "CL_RefreshPlatformServiceCvars();" in init_block
    assert "CL_Steam_InitCallbacks();" not in init_block
    assert "CL_Steam_InitCallbacks();" not in steam_client_init_block
    assert "SteamCallbacks_Init();" in steam_client_init_block
    assert "SteamMicroCallbacks_Init();" in steam_client_init_block
    assert "SteamLobby_Init();" in steam_client_init_block
    assert "CL_WebHost_Init();" in init_block

    assert "CL_Steam_ShutdownCallbacks();" in shutdown_block
    assert "if ( cl_statsClearRegistered ) {" not in shutdown_block
    assert 'Cmd_RemoveCommand ("stats_clear");' not in shutdown_block
    assert "CL_WebHost_Shutdown();" in shutdown_block

    assert "QL_Steamworks_RegisterClientCallbacks( &clientBindings )" in steam_callbacks_init_block
    assert "QL_Steamworks_RegisterLobbyCallbacks( &lobbyBindings )" in steam_lobby_callbacks_init_block
    assert "QL_Steamworks_RegisterMicroCallbacks( &microBindings )" in steam_micro_callbacks_init_block
    assert "QL_Steamworks_RegisterWorkshopCallbacks( &workshopBindings )" in workshop_callback_init_block
    assert "CL_RefreshPlatformServiceCvars();" in steam_client_init_block
    assert 'Cvar_Set( "cl_onlineServicesMode", QL_GetOnlineServicesModeLabel() );' in cl_main
    assert 'Cvar_Set( "cl_onlineServicesPolicy", QL_GetOnlineServicesPolicyLabel() );' in cl_main
    assert 'Cvar_Set( "cl_identityBootstrapMode", CL_GetIdentityBootstrapModeLabel() );' in cl_main
    assert 'Cvar_Set( "cl_identityBootstrapPolicy", CL_GetIdentityBootstrapPolicyLabel() );' in cl_main
    assert 'Cvar_Set( "cl_voiceServiceMode", CL_GetVoiceServiceModeLabel() );' in cl_main
    assert 'Cvar_Set( "cl_voiceServicePolicy", CL_GetVoiceServicePolicyLabel() );' in cl_main
    assert 'Cvar_Set( "cl_workshopProvider", CL_GetWorkshopServiceProviderLabel() );' in cl_main
    assert 'Cvar_Set( "cl_workshopPolicy", CL_GetWorkshopServicePolicyLabel() );' in cl_main
    assert 'Cvar_Set( "ui_subscriptionBridgeMode", QL_GetOnlineServicesModeLabel() );' in cl_main
    assert 'Cvar_Set( "ui_subscriptionBridgePolicy", QL_GetOnlineServicesPolicyLabel() );' in cl_main
    assert 'Com_DPrintf( "client callback bootstrap: %s (matchmaking=%s [%s], stats=%s [%s], overlay=%s [%s])\\n",' in callback_bootstrap_log_block
    assert "CL_GetMatchmakingServiceProviderLabel()" in callback_bootstrap_log_block
    assert "CL_GetMatchmakingServicePolicyLabel()" in callback_bootstrap_log_block
    assert "CL_GetStatsServiceProviderLabel()" in callback_bootstrap_log_block
    assert "CL_GetStatsServicePolicyLabel()" in callback_bootstrap_log_block
    assert "CL_GetSocialOverlayServiceProviderLabel()" in callback_bootstrap_log_block
    assert "CL_GetSocialOverlayServicePolicyLabel()" in callback_bootstrap_log_block
    assert "workshopProvider = CL_GetWorkshopServiceProviderLabel();" in steam_client_init_block
    assert "workshopPolicy = CL_GetWorkshopServicePolicyLabel();" in steam_client_init_block
    assert steam_client_init_block.index("CL_RefreshPlatformServiceCvars();") < steam_client_init_block.index("if ( !CL_SteamServicesEnabled() ) {")
    assert 'CL_LogClientCallbackBootstrapFallback( "online services disabled; keeping compatibility-only browser event fallback" );' in steam_client_init_block
    assert 'CL_LogClientCallbackBootstrapFallback( "callback registration failed; keeping compatibility-only browser event fallback" );' in steam_client_init_block
    assert 'Com_sprintf( detail, sizeof( detail ), "callbacks unavailable; keeping polling fallback (%s [%s])",' in workshop_callback_init_block
    assert 'CL_LogWorkshopLifecycle( "callback-bootstrap", detail );' in workshop_callback_init_block
    assert "cl_steamCallbackState.callbackRegistrationActive = qtrue;" in steam_client_init_block
    assert "callbacksRegistered = SteamLobbyCallbacks_Init();" in steam_lobby_init_block

    assert "QL_Steamworks_UnregisterWorkshopCallbacks();" in callback_shutdown_block
    assert "QL_Steamworks_UnregisterMicroCallbacks();" in callback_shutdown_block
    assert "QL_Steamworks_UnregisterLobbyCallbacks();" in callback_shutdown_block
    assert "QL_Steamworks_UnregisterClientCallbacks();" in callback_shutdown_block

    assert 'CL_LogStatsServiceRegistrationSkipped( "stats provider unavailable" );' in stats_gate_block
    assert 'CL_LogStatsServiceRegistrationSkipped( "stats provider initialisation failed" );' in stats_gate_block
    assert 'CL_LogStatsServiceRegistrationSkipped( "stats_clear unsupported for current app id" );' in stats_gate_block
    assert "if ( QL_Steamworks_GetAppID() != 0x54100u ) {" in stats_gate_block
    assert "return qtrue;" in stats_gate_block
    assert 'CL_LogStatsServiceIgnored( "stats_clear", "stats provider unavailable" );' in stats_clear_block
    assert 'if ( !QL_Steamworks_ClearStats( qtrue ) ) {' in stats_clear_block
    assert 'CL_LogStatsServiceIgnored( "stats_clear", "clear request failed" );' in stats_clear_block


def test_platform_steamworks_reconstructs_retail_callback_bundle_registration_surface() -> None:
    steamworks = (REPO_ROOT / "src/common/platform/platform_steamworks.c").read_text(encoding="utf-8")

    register_client_block = _extract_function_block(
        steamworks, "qboolean QL_Steamworks_RegisterClientCallbacks( const ql_steam_client_callback_bindings_t *bindings ) {"
    )
    register_avatar_block = _extract_function_block(
        steamworks, "qboolean QL_Steamworks_RegisterAvatarCallbacks( const ql_steam_avatar_callback_bindings_t *bindings ) {"
    )
    register_lobby_block = _extract_function_block(
        steamworks, "qboolean QL_Steamworks_RegisterLobbyCallbacks( const ql_steam_lobby_callback_bindings_t *bindings ) {"
    )
    register_micro_block = _extract_function_block(
        steamworks, "qboolean QL_Steamworks_RegisterMicroCallbacks( const ql_steam_micro_callback_bindings_t *bindings ) {"
    )
    register_workshop_block = _extract_function_block(
        steamworks, "qboolean QL_Steamworks_RegisterWorkshopCallbacks( const ql_steam_workshop_callback_bindings_t *bindings ) {"
    )
    bind_ugc_block = _extract_function_block(steamworks, "qboolean QL_Steamworks_BindUGCQueryCallResult( SteamAPICall_t callHandle ) {")
    shutdown_block = _extract_function_block(steamworks, "void QL_Steamworks_Shutdown( void ) {")

    assert '#define QL_STEAM_CALLBACK_RICH_PRESENCE_JOIN_REQUESTED 0x151' in steamworks
    assert '#define QL_STEAM_CALLBACK_USER_STATS_RECEIVED 0x44d' in steamworks
    assert '#define QL_STEAM_CALLBACK_FRIEND_RICH_PRESENCE_UPDATE 0x150' in steamworks
    assert '#define QL_STEAM_CALLBACK_AVATAR_IMAGE_LOADED 0x14e' in steamworks
    assert '#define QL_STEAM_CALLBACK_ITEM_INSTALLED 0xd4d' in steamworks
    assert '#define QL_STEAM_CALLBACK_DOWNLOAD_ITEM_RESULT 0xd4e' in steamworks
    assert '#define QL_STEAM_CALLBACK_LOBBY_CREATED 0x201' in steamworks
    assert '#define QL_STEAM_CALLBACK_LOBBY_CHAT_MESSAGE 0x1fb' in steamworks
    assert '#define QL_STEAM_CALLBACK_MICROTXN_AUTHORIZATION_RESPONSE 0x98' in steamworks
    assert 'QL_Steamworks_LoadOptionalSymbol( (void **)&state.SteamAPI_RegisterCallback, "SteamAPI_RegisterCallback" );' in steamworks
    assert 'QL_Steamworks_LoadOptionalSymbol( (void **)&state.SteamAPI_RegisterCallResult, "SteamAPI_RegisterCallResult" );' in steamworks

    assert "QL_Steamworks_PrepareCallbackObject( &callbackState->richPresenceJoinRequested" in register_client_block
    assert "QL_Steamworks_PrepareCallbackObject( &callbackState->ugcQueryCompleted" in register_client_block
    assert "QL_Steamworks_RegisterCallbackObject( &callbackState->richPresenceJoinRequested )" in register_client_block
    assert "QL_Steamworks_RegisterCallbackObject( &callbackState->friendRichPresenceUpdate )" in register_client_block

    assert "QL_Steamworks_PrepareCallbackObject( &callbackState->avatarImageLoaded" in register_avatar_block
    assert "QL_Steamworks_RegisterCallbackObject( &callbackState->avatarImageLoaded )" in register_avatar_block

    assert "QL_Steamworks_PrepareCallbackObject( &callbackState->lobbyChatMessage" in register_lobby_block
    assert "QL_Steamworks_PrepareCallbackObject( &callbackState->gameLobbyJoinRequested" in register_lobby_block

    assert "QL_Steamworks_PrepareCallbackObject( &callbackState->authorizationResponse" in register_micro_block
    assert "QL_Steamworks_RegisterCallbackObject( &callbackState->authorizationResponse )" in register_micro_block

    assert "QL_Steamworks_PrepareCallbackObject( &callbackState->itemInstalled" in register_workshop_block
    assert "QL_Steamworks_PrepareCallbackObject( &callbackState->downloadItemResult" in register_workshop_block
    assert "QL_Steamworks_RegisterCallbackObject( &callbackState->itemInstalled )" in register_workshop_block
    assert "QL_Steamworks_RegisterCallbackObject( &callbackState->downloadItemResult )" in register_workshop_block

    assert "state.SteamAPI_RegisterCallResult( &callbackState->ugcQueryCompleted, callHandle );" in bind_ugc_block
    assert "callbackState->ugcCallBound = qtrue;" in bind_ugc_block

    assert "QL_Steamworks_UnregisterWorkshopCallbacks();" in shutdown_block
    assert "QL_Steamworks_UnregisterMicroCallbacks();" in shutdown_block
    assert "QL_Steamworks_UnregisterLobbyCallbacks();" in shutdown_block
    assert "QL_Steamworks_UnregisterAvatarCallbacks();" in shutdown_block
    assert "QL_Steamworks_UnregisterClientCallbacks();" in shutdown_block


def test_launcher_resource_bridge_reconstructs_retail_web_fallback_owner() -> None:
    cl_webpak = (REPO_ROOT / "src/code/client/cl_webpak.c").read_text(encoding="utf-8")
    steam_resources = (REPO_ROOT / "src/code/client/cl_steam_resources.c").read_text(encoding="utf-8")
    cl_main = (REPO_ROOT / "src/code/client/cl_main.c").read_text(encoding="utf-8")
    client_h = (REPO_ROOT / "src/code/client/client.h").read_text(encoding="utf-8")

    normalize_block = _extract_function_block(
        cl_webpak,
        "static qboolean CL_WebPak_NormalizePath( const char *virtualPath, char *normalized, size_t normalizedSize ) {",
    )
    datapack_table_block = _extract_function_block(
        cl_webpak,
        "static qboolean CL_WebDataPak_BuildPathTable( clWebDataPak_t *dataPak ) {",
    )
    datapack_load_block = _extract_function_block(
        cl_webpak,
        "static qboolean CL_WebDataPak_LoadFile( const char *pakPath, clWebDataPak_t *outDataPak ) {",
    )
    datapack_index_block = _extract_function_block(
        cl_webpak,
        "static int CL_WebDataPak_FindEntryIndex( const clWebDataPak_t *dataPak, uint16_t resourceId ) {",
    )
    datapack_view_block = _extract_function_block(
        cl_webpak,
        "static qboolean CL_WebDataPak_GetResourceView( const clWebDataPak_t *dataPak, uint16_t resourceId, const byte **outData, int *outLength ) {",
    )
    standalone_path_block = _extract_function_block(
        cl_webpak,
        "static void CL_WebPak_BuildStandalonePath( const char *rootPath, const char *filename, char *outPath, size_t outPathSize ) {",
    )
    init_block = _extract_function_block(cl_webpak, "void CL_WebPak_Init( void ) {")
    request_block = _extract_function_block(
        cl_webpak,
        "qboolean CL_WebRequestResolve( const char *virtualPath, void **outBuffer, int *outLength ) {",
    )
    mapped_block = _extract_function_block(
        cl_webpak,
        "static qboolean CL_WebRequestReadMappedFile( const char *request, void **outBuffer, int *outLength )",
    )
    shader_block = _extract_function_block(
        steam_resources,
        "qhandle_t CL_Steam_RegisterShader( const char *url ) {",
    )
    data_source_block = _extract_function_block(
        steam_resources,
        "static qboolean CL_SteamDataSource_Request( const char *url, clSteamDataSourceResponse_t *response ) {",
    )
    interceptor_block = _extract_function_block(
        steam_resources,
        "static qboolean QLResourceInterceptor_OnRequest( const char *url, clSteamDataSourceResponse_t *response ) {",
    )
    steam_resources_init_block = _extract_function_block(steam_resources, "void CL_InitSteamResources( void ) {")
    url_block = _extract_function_block(
        steam_resources,
        "qboolean Sys_Steam_RequestURL( const char *url, byte **outBuffer, int *outSize ) {",
    )

    assert "static const char *CL_WebPak_StripProtocol( const char *virtualPath ) {" in cl_webpak
    assert "typedef struct {" in cl_webpak
    assert "static clWebDataPak_t cl_webDataPak;" in cl_webpak
    assert "Retail web.pak sits beside the executable." in cl_webpak
    assert 'Com_sprintf( outPath, outPathSize, "%s%c%s", rootPath, PATH_SEP, filename );' in standalone_path_block
    assert 'separator = strstr( virtualPath, "://" );' in cl_webpak
    assert "normalizedSource = CL_WebPak_StripProtocol( virtualPath );" in normalize_block
    assert "normalized[index] = ( ch == '\\\\' ) ? '/' : ch;" in normalize_block
    assert "strchr( normalized, ':' )" in normalize_block
    assert "trailerResourceId = CL_WebDataPak_ReadUInt32( manifestData + manifestLength - 4 );" in datapack_table_block
    assert "if ( havePending ) {" in datapack_table_block
    assert "dataPak->paths[dataPak->pathCount].resourceId = (uint16_t)nextResourceId;" in datapack_table_block
    assert "dataPak->paths[dataPak->pathCount].resourceId = (uint16_t)trailerResourceId;" in datapack_table_block
    assert "if ( !dataPak || !dataPak->buffer || dataPak->resourceCount == 0 ) {" in datapack_index_block
    assert "!dataPak->loaded" not in datapack_index_block
    assert "if ( !dataPak || !dataPak->buffer || dataPak->resourceCount == 0 ) {" in datapack_view_block
    assert "!dataPak->loaded" not in datapack_view_block
    assert "if ( fileLength <= 0 || fileLength > INT_MAX ) {" in datapack_load_block
    assert "dataPak.buffer = malloc( (size_t)fileLength );" in datapack_load_block
    assert "if ( version == 4u ) {" in datapack_load_block
    assert "dataPak.headerLength = 9;" in datapack_load_block
    assert "if ( version == 5u ) {" in datapack_load_block
    assert "if ( !CL_WebDataPak_BuildPathTable( &dataPak ) ) {" in datapack_load_block
    assert "FS_FOpenWebFileRead( request, &file, resolvedPath, sizeof( resolvedPath ) )" in mapped_block
    assert "length = FS_filelength( file );" in mapped_block
    assert "buffer = Z_Malloc( length + 1 );" in mapped_block
    assert "if ( length > 0 && FS_Read( buffer, length, file ) != length ) {" in mapped_block
    assert "normalizedValid = CL_WebPak_NormalizePath( virtualPath, normalized, sizeof( normalized ) );" in request_block
    assert "if ( normalizedValid && CL_WebPak_ReadInternal( normalized, outBuffer, outLength ) ) {" in request_block
    assert "if ( CL_WebRequestReadMappedFile( virtualPath, outBuffer, outLength ) ) {" in request_block
    assert "if ( !normalizedValid ) {" in request_block
    assert "length = FS_ReadFile( normalized, &fsBuffer );" in request_block
    assert 'CL_WebPak_BuildStandalonePath( homePath, "web.pak", pakPath, sizeof( pakPath ) );' in init_block
    assert 'CL_WebPak_BuildStandalonePath( basePath, "web.pak", pakPath, sizeof( pakPath ) );' in init_block
    assert "if ( CL_WebDataPak_Load( pakPath ) ) {" in init_block
    assert 'Com_Printf( "web.pak datapack mounted from %s\\n", pakPath );' in init_block

    assert "static qboolean CL_SteamResources_IsURIResource( const char *url ) {" in steam_resources
    assert 'return ( strstr( url, "://" ) != NULL ) ? qtrue : qfalse;' in steam_resources
    assert "static const ql_platform_feature_descriptor *CL_GetSteamResourceServiceDescriptor( void ) {" in steam_resources
    assert "static const char *CL_GetSteamResourceServiceProviderLabel( void ) {" in steam_resources
    assert "static const char *CL_GetSteamResourceServicePolicyLabel( void ) {" in steam_resources
    assert "static void CL_LogSteamResourceBridgeUnavailable( const char *url, const char *reason ) {" in steam_resources
    assert "static void CL_LogLauncherResourceFallbackUnavailable( const char *url, const char *reason ) {" in steam_resources
    assert "static void CL_LogSteamResourceRequestStubbed( const char *url ) {" in steam_resources
    assert "return &services->overlay;" in steam_resources
    assert "static void CL_SteamResources_BuildRendererName( const char *url, const clSteamResource_t *slot, char *rendererName, size_t rendererNameSize ) {" in steam_resources
    assert "if ( !CL_SteamResources_IsURIResource( url ) ) {" in shader_block
    assert "CL_LogSteamResourceRequestStubbed( url );" in shader_block
    assert "CL_SteamResources_BuildRendererName( url, slot, rendererName, sizeof( rendererName ) );" in shader_block
    assert "shader = CL_RegisterShaderFromMemory( rendererName, buffer, bufferLength, qfalse );" in shader_block
    assert 'CL_LogSteamResourceBridgeUnavailable( url, "keeping launcher/web fallback resource bridge" );' in data_source_block
    assert 'CL_LogSteamResourceBridgeUnavailable( url, "avatar request deferred pending AvatarImageLoaded callback" );' in data_source_block
    assert 'CL_LogSteamResourceBridgeUnavailable( url, "avatar request could not be satisfied" );' in data_source_block
    assert 'CL_LogSteamResourceBridgeUnavailable( url, "no live SteamDataSource owner is available" );' in data_source_block
    assert "CL_SteamResources_SanitizeCacheName" not in steam_resources
    assert "CL_SteamResources_RegisterCachedShader" not in steam_resources
    assert "CL_SteamResources_WriteCacheFile" not in steam_resources
    assert "CL_SteamResources_RemoveCacheFile" not in steam_resources
    assert "cachePath" not in steam_resources
    assert "persisted" not in steam_resources
    assert "qhandle_t CL_RegisterShaderFromMemory( const char *name, const byte *buffer, int bufferLength, qboolean mipRawImage );" in client_h
    assert "qhandle_t CL_RegisterShaderFromMemory( const char *name, const byte *buffer, int bufferLength, qboolean mipRawImage ) {" in cl_main
    assert "image = R_LoadImageFromMemory( name, buffer, bufferLength, mipRawImage, mipRawImage, mipRawImage ? GL_REPEAT : GL_CLAMP );" in cl_main
    assert "if ( CL_SteamDataSource_Request( url, response ) ) {" in interceptor_block
    assert "if ( CL_LauncherRequestData( url, (void **)&response->buffer, &response->bufferLength ) ) {" in interceptor_block
    assert 'CL_LogLauncherResourceFallbackUnavailable( url, "no launcher/web resource owner is available" );' in interceptor_block
    assert 'Com_Printf( "Steam resource bridge disabled for %s [%s]; keeping launcher/web fallback resource bridge.\\n",' in steam_resources_init_block
    assert "CL_SteamResources_RegisterAvatarCallbacks();" in steam_resources_init_block
    assert "QLResourceInterceptor_OnRequest( url, &response )" in url_block
    assert 'CL_LogLauncherResourceFallbackUnavailable( url, "request could not be resolved" );' in url_block
    assert 'CL_LogLauncherResourceFallbackUnavailable( url, "no binary buffer was produced" );' in url_block


def test_launcher_resource_fallbacks_survive_service_disabled_policy() -> None:
    files_c = (REPO_ROOT / "src/code/qcommon/files.c").read_text(encoding="utf-8")
    cl_webpak = (REPO_ROOT / "src/code/client/cl_webpak.c").read_text(encoding="utf-8")
    steam_resources = (REPO_ROOT / "src/code/client/cl_steam_resources.c").read_text(encoding="utf-8")

    rewrite_block = _extract_function_block(
        files_c,
        "qboolean FS_RewriteWebPath( const char *uri, char *outPath, int outSize ) {",
    )
    open_block = _extract_function_block(
        files_c,
        "qboolean FS_FOpenWebFileRead( const char *request, fileHandle_t *file, char *resolvedPath, size_t resolvedSize ) {",
    )
    init_block = _extract_function_block(cl_webpak, "void CL_WebPak_Init( void ) {")
    available_block = _extract_function_block(cl_webpak, "qboolean CL_WebPak_Available( void ) {")
    fetch_block = _extract_function_block(
        cl_webpak,
        "qboolean CL_WebPak_Fetch( const char *virtualPath, void **outBuffer, int *outLength ) {",
    )
    request_block = _extract_function_block(
        cl_webpak,
        "qboolean CL_WebRequestResolve( const char *virtualPath, void **outBuffer, int *outLength ) {",
    )
    launcher_block = _extract_function_block(
        cl_webpak,
        "qboolean CL_LauncherRequestData( const char *virtualPath, void **outBuffer, int *outLength ) {",
    )
    shader_block = _extract_function_block(
        steam_resources,
        "qhandle_t CL_Steam_RegisterShader( const char *url ) {",
    )
    data_source_block = _extract_function_block(
        steam_resources,
        "static qboolean CL_SteamDataSource_Request( const char *url, clSteamDataSourceResponse_t *response ) {",
    )
    resources_init_block = _extract_function_block(steam_resources, "void CL_InitSteamResources( void ) {")
    refresh_cvars_block = _extract_function_block(
        steam_resources,
        "static void CL_RefreshSteamResourceBridgeCvars( void ) {",
    )
    interceptor_block = _extract_function_block(
        steam_resources,
        "static qboolean QLResourceInterceptor_OnRequest( const char *url, clSteamDataSourceResponse_t *response ) {",
    )
    url_block = _extract_function_block(
        steam_resources,
        "qboolean Sys_Steam_RequestURL( const char *url, byte **outBuffer, int *outSize ) {",
    )

    assert "FS_OnlineServicesEnabled" not in files_c
    assert 'Com_sprintf( outPath, outSize, "%s/%s", fs_webpath->string, localPath );' in rewrite_block
    assert "if ( !FS_RewriteWebPath( request, qpath, sizeof( qpath ) ) ) {" not in open_block
    assert "if ( !FS_OnlineServicesEnabled() ) {" not in open_block

    assert "web.pak mount skipped: online services disabled by build/runtime policy" not in init_block
    assert "CL_OnlineServicesEnabled()" not in init_block
    assert "return ( cl_webPak != NULL || cl_webDataPak.loaded );" in available_block
    assert "CL_OnlineServicesEnabled()" not in fetch_block
    assert "CL_OnlineServicesEnabled()" not in request_block
    assert "CL_OnlineServicesEnabled()" not in launcher_block

    assert "if ( CL_SteamResources_IsSteamURL( url ) ) {" in shader_block
    assert "if ( !CL_SteamServicesEnabled() ) {" in shader_block
    assert "UI: launcher resource request stubbed" not in shader_block
    assert 'CL_LogSteamResourceRequestStubbed( url );' in shader_block
    assert "CL_OnlineServicesEnabled()" not in shader_block
    assert "Steam backend disabled by build/runtime policy" not in steam_resources
    assert "Steam backend unavailable for %s" not in steam_resources
    assert "Steam resource bridge disabled by build/runtime policy" not in steam_resources
    assert 'Com_Printf( "Steam resource bridge unavailable for %s via %s [%s]; %s\\n"' in steam_resources
    assert 'Com_Printf( "Launcher/web fallback unavailable for %s via %s [%s]; %s\\n"' in steam_resources
    assert 'Cvar_Set( "ui_resourceBridgeProvider", CL_GetSteamResourceServiceProviderLabel() );' in refresh_cvars_block
    assert 'Cvar_Set( "ui_resourceBridgePolicy", CL_GetSteamResourceServicePolicyLabel() );' in refresh_cvars_block
    assert 'Com_Printf( "Steam resource bridge disabled for %s [%s]; keeping launcher/web fallback resource bridge.\\n",' in resources_init_block
    assert 'CL_LogSteamResourceBridgeUnavailable( url, "keeping launcher/web fallback resource bridge" );' in data_source_block
    assert "return;" in resources_init_block
    assert "if ( CL_LauncherRequestData( url, (void **)&response->buffer, &response->bufferLength ) ) {" in interceptor_block
    assert "QLResourceInterceptor_OnRequest( url, &response )" in url_block
    assert "Launcher backend disabled by build/runtime policy" not in url_block
    assert "Launcher resource backend unavailable for %s" not in steam_resources
    assert 'CL_LogLauncherResourceFallbackUnavailable( url, "request could not be resolved" );' in url_block


def test_awesomium_launch_task_builds_with_in_process_overlay_provider() -> None:
    tasks = json.loads((REPO_ROOT / ".vscode" / "tasks.json").read_text(encoding="utf-8"))
    awesomium_task = next(task for task in tasks["tasks"] if task["label"] == "Build Debug Awesomium")
    args = awesomium_task["args"]

    assert args[args.index("-OnlineServices") + 1] == "1"
    assert args[args.index("-Steamworks") + 1] == "0"
    assert args[args.index("-OpenSteam") + 1] == "1"


def test_client_auth_ticket_lifetime_reconstructs_retail_disconnect_owner() -> None:
    steamworks = (REPO_ROOT / "src/common/platform/platform_steamworks.c").read_text(encoding="utf-8")
    steamworks_header = (REPO_ROOT / "src/common/platform/platform_steamworks.h").read_text(encoding="utf-8")
    ql_auth = (REPO_ROOT / "src/code/client/ql_auth.c").read_text(encoding="utf-8")
    cl_main = (REPO_ROOT / "src/code/client/cl_main.c").read_text(encoding="utf-8")

    cancel_platform_block = _extract_function_block(
        steamworks,
        "qboolean QL_Steamworks_CancelAuthTicket( uint32_t ticketHandle ) {",
    )
    request_ticket_block = _extract_function_block(
        ql_auth,
        "static qboolean QL_ClientAuth_RequestSteamTicket( ql_auth_credential_t *credential, char *logBuffer, size_t logBufferSize ) {",
    )
    set_ticket_block = _extract_function_block(
        ql_auth,
        "static void QL_ClientAuth_SetSteamTicketHandle( uint32_t ticketHandle ) {",
    )
    cancel_client_block = _extract_function_block(
        ql_auth,
        "void QL_ClientAuth_CancelSteamTicket( void ) {",
    )
    disconnect_block = _extract_function_block(
        cl_main,
        "void CL_Disconnect( qboolean showMainMenu ) {",
    )

    assert "qboolean QL_Steamworks_CancelAuthTicket( uint32_t ticketHandle );" in steamworks_header
    assert "if ( ticketHandle == 0 || !state.initialised || !state.SteamUser || !state.CancelAuthTicket ) {" in cancel_platform_block
    assert "state.CancelAuthTicket( user, (HAuthTicket)ticketHandle );" in cancel_platform_block
    assert "static uint32_t cl_clientAuthSteamTicketHandle = 0;" in ql_auth
    assert "uint32_t ticketHandle = 0;" in request_ticket_block
    assert "QL_Steamworks_RequestAuthTicket( credential->value, sizeof( credential->value ), &ticketLength, &ticketHandle )" in request_ticket_block
    assert "QL_ClientAuth_SetSteamTicketHandle( ticketHandle );" in request_ticket_block
    assert "QL_Steamworks_CancelAuthTicket( cl_clientAuthSteamTicketHandle );" in set_ticket_block
    assert "QL_Steamworks_CancelAuthTicket( cl_clientAuthSteamTicketHandle );" in cancel_client_block
    assert "cl_clientAuthSteamTicketHandle = 0;" in cancel_client_block
    assert "QL_ClientAuth_CancelSteamTicket();" in disconnect_block


def test_client_auth_logs_include_provider_and_policy_labels() -> None:
    ql_auth = (REPO_ROOT / "src/code/client/ql_auth.c").read_text(encoding="utf-8")

    log_stage_block = _extract_function_block(
        ql_auth,
        "static void QL_ClientAuth_LogStage( const ql_client_auth_transport_t *transport, const char *stage, const char *detail ) {",
    )
    log_response_block = _extract_function_block(
        ql_auth,
        "static void QL_ClientAuth_LogResponse( const ql_client_auth_transport_t *transport, const ql_auth_response_t *response ) {",
    )
    policy_block_block = _extract_function_block(
        ql_auth,
        "static qboolean QL_ClientAuth_ReportPolicyBlock( const ql_client_auth_transport_t *transport, ql_auth_response_t *response, const char *requestLabel ) {",
    )
    execute_block = _extract_function_block(
        ql_auth,
        "qboolean QL_Auth_ExecuteRequest( const ql_auth_credential_t *credential, ql_auth_response_t *response ) {",
    )

    assert "const char *policyLabel;" in ql_auth
    assert 'static const char *QL_ClientAuth_GetEndpoint( qlAuthCredentialKind kind ) {' in ql_auth
    assert 'Com_Printf( "[auth] %s [%s] %s (%s): %s\\n",' in log_stage_block
    assert 'Com_Printf( "[auth] %s [%s] result -> outcome=%s, message=\\"%s\\"\\n",' in log_response_block
    assert 'const char *modeLabel = QL_GetOnlineServicesModeLabel();' in policy_block_block
    assert 'const char *policyLabel = QL_GetOnlineServicesPolicyLabel();' in policy_block_block
    assert 'QL_ClientAuth_LogStage( transport, "policy-blocked", detail );' in policy_block_block
    assert 'responseLabel = "Steam";' in policy_block_block
    assert 'responseLabel = "Standalone";' in policy_block_block
    assert '"%s blocked: %s [%s]"' in policy_block_block
    assert 'policyLabel = services ? QL_DescribePlatformFeaturePolicy( &services->auth ) : "compatibility-unavailable";' in execute_block
    assert 'endpoint = QL_ClientAuth_GetEndpoint( credential->kind );' in execute_block
    assert 'return QL_ClientAuth_ReportPolicyBlock( &transport, response, "Steam authentication" );' in execute_block
    assert 'return QL_ClientAuth_ReportPolicyBlock( &transport, response, "Standalone launcher authentication" );' in execute_block
    assert 'QL_ClientAuth_LogStage( &transport, "ticket-request-failed", "Steam auth ticket request failed before dispatch" );' in execute_block
    assert '"Steam ticket failed: %s [%s]"' in execute_block
    assert '"Auth init failed: %s [%s]"' in execute_block
    assert '"No auth backend: %s [%s]"' in execute_block
    assert 'transport.logPrefix = "dispatcher";' not in execute_block
    assert '[auth] %s [%s] payload summary: ticket=%s (len=%zu)\\n' in execute_block


def test_policy_blocked_auth_requests_surface_online_services_mode_and_policy(tmp_path) -> None:
    steam_workdir = tmp_path / "steam_policy_block"
    steam_output = _compile_and_run(
        steam_workdir,
        _POLICY_BLOCKED_AUTH_PROBE,
        {"QL_BUILD_ONLINE_SERVICES": 0, "QL_BUILD_STEAMWORKS": 0, "QL_BUILD_OPEN_STEAM": 0},
        include_client_stub=True,
    )
    steam_details = dict(line.split("=", 1) for line in steam_output.strip().splitlines())

    standalone_probe = _POLICY_BLOCKED_AUTH_PROBE.replace(
        "credential.kind = QL_AUTH_CREDENTIAL_STEAM;",
        "credential.kind = QL_AUTH_CREDENTIAL_STANDALONE_TOKEN;",
    ).replace(
        'Q_strncpyz(credential.value, "retry:TICKET-ABCDEFGHIJKLMNOP", sizeof(credential.value));',
        'Q_strncpyz(credential.value, "JWT-VALID-ABCDEFGHIJKLMNOP", sizeof(credential.value));',
    )
    standalone_workdir = tmp_path / "standalone_policy_block"
    standalone_output = _compile_and_run(
        standalone_workdir,
        standalone_probe,
        {"QL_BUILD_ONLINE_SERVICES": 0, "QL_BUILD_STEAMWORKS": 0, "QL_BUILD_OPEN_STEAM": 0},
        include_client_stub=True,
    )
    standalone_details = dict(line.split("=", 1) for line in standalone_output.strip().splitlines())

    expected_suffix = "Build-disabled default (QL_BUILD_ONLINE_SERVICES=0) [compatibility-disabled (QL_BUILD_ONLINE_SERVICES=0)]"
    assert steam_details["handled"] == "0"
    assert f"Steam blocked: {expected_suffix}" == steam_details["message"]
    assert standalone_details["handled"] == "0"
    assert f"Standalone blocked: {expected_suffix}" == standalone_details["message"]


def test_auth_backend_responses_and_trace_keep_heuristic_compatibility_lanes_explicit() -> None:
    steamworks_backend = (REPO_ROOT / "src/common/platform/backends/platform_backend_steamworks.c").read_text(encoding="utf-8")
    open_backend = (REPO_ROOT / "src/common/platform/backends/platform_backend_open_steam.c").read_text(encoding="utf-8")
    ql_auth = (REPO_ROOT / "src/code/client/ql_auth.c").read_text(encoding="utf-8")
    trace_script = REPO_ROOT / "tools/integration/auth_flow_trace.py"

    hybrid_block = _extract_function_block(
        ql_auth,
        "static qboolean QL_ClientAuth_HandleHybridSteam( const ql_client_auth_transport_t *transport, const ql_auth_credential_t *credential, ql_auth_response_t *response ) {",
    )

    assert "Steamworks heuristic compatibility backend" in steamworks_backend
    assert "Open adapter heuristic compatibility backend" in open_backend
    assert '"Hybrid fallback accepted credential via heuristic open adapter (token=%s)"' in ql_auth
    assert 'QL_ClientAuth_LogStage( transport,' in hybrid_block
    assert '"hybrid-fallback"' in hybrid_block
    assert '"Steamworks heuristic compatibility backend returned retry; dispatching open adapter fallback"' in hybrid_block
    assert 'fallbackTransport.logPrefix = "Open Steam Adapter";' in hybrid_block
    assert 'QL_ClientAuth_LogStage( &fallbackTransport, "dispatch", "submitting fallback credential" );' in hybrid_block

    trace_output = subprocess.run(
        [os.sys.executable, str(trace_script)],
        cwd=REPO_ROOT,
        check=True,
        capture_output=True,
        text=True,
    ).stdout

    assert "[auth] Steamworks [compatibility-only] dispatch (/steam/session/validate): submitting credential" in trace_output
    assert 'message="Steamworks heuristic compatibility backend rejected ticket: payload too short"' in trace_output
    assert 'message="Steamworks heuristic compatibility backend denied the ticket"' in trace_output
    assert "[auth] Hybrid [compatibility-only] hybrid-fallback (/steam/session/validate): Steamworks heuristic compatibility backend returned retry; dispatching open adapter fallback" in trace_output
    assert "[auth] Open Steam Adapter [compatibility-only] dispatch (/launcher/auth/verify): submitting fallback credential" in trace_output
    assert 'message="Hybrid fallback accepted credential via heuristic open adapter' in trace_output
    assert 'message="Open adapter heuristic compatibility backend requested launcher token refresh"' in trace_output
    assert 'message="Open adapter heuristic compatibility backend treated token as revoked"' in trace_output
    assert 'message="Open adapter heuristic compatibility backend accepted standalone token' in trace_output


def test_browser_cache_reload_owner_restores_retail_command_and_cvar_surface() -> None:
    cl_main = (REPO_ROOT / "src/code/client/cl_main.c").read_text(encoding="utf-8")
    cl_cgame = (REPO_ROOT / "src/code/client/cl_cgame.c").read_text(encoding="utf-8")
    steam_resources = (REPO_ROOT / "src/code/client/cl_steam_resources.c").read_text(encoding="utf-8")

    clear_session_block = _extract_function_block(
        cl_cgame,
        "static void CL_Web_ClearSessionState( void ) {",
    )
    clear_cache_block = _extract_function_block(
        cl_cgame,
        "void CL_Web_ClearCache_f( void ) {",
    )
    reload_view_block = _extract_function_block(
        cl_cgame,
        "static void QLWebHost_ReloadView( qboolean ignoreCache ) {",
    )
    reload_block = _extract_function_block(
        cl_cgame,
        "void CL_Web_Reload_f( void ) {",
    )
    register_block = _extract_function_block(
        cl_cgame,
        "void QLWebHost_RegisterCommands( void ) {",
    )
    clear_resource_block = _extract_function_block(
        steam_resources,
        "void CL_ClearSteamResourceCache( qboolean clearPersisted ) {",
    )
    clear_slot_block = _extract_function_block(
        steam_resources,
        "static void CL_SteamResources_ClearSlot( clSteamResource_t *slot, qboolean clearPersisted )",
    )

    assert 'Cvar_Get ("web_zoom", "100", CVAR_ARCHIVE );' not in cl_main
    assert 'Cvar_Get ("web_console", "0", CVAR_ARCHIVE );' not in cl_main
    assert 'Cvar_Get ("web_zoom", "100", CVAR_ARCHIVE );' in register_block
    assert 'Cvar_Get ("web_console", "0", CVAR_ARCHIVE );' in register_block
    assert "CL_ClearSteamResourceCache( qtrue );" in clear_session_block
    assert "if ( !cl_webHost.sessionInitialised ) {" in clear_cache_block
    assert "CL_Web_ClearSessionState();" in clear_cache_block
    assert "(void)ignoreCache;" in reload_view_block
    assert "CL_WebHost_PrimeLauncherDocument( cl_webHost.currentUrl )" in reload_view_block
    assert "QLLoadHandler_OnFailLoadingFrame( cl_webHost.currentUrl );" in reload_view_block
    assert "if ( !cl_webHost.viewInitialised ) {" in reload_block
    assert "CL_Web_ClearSessionState();" in reload_block
    assert "QLWebHost_ReloadView( qtrue );" in reload_block
    assert "for ( i = 0; i < MAX_STEAM_RESOURCES; i++ ) {" in clear_resource_block
    assert "CL_SteamResources_ClearSlot( &cl_steamResources[i], clearPersisted );" in clear_resource_block
    assert "cl_steamResourceGeneration++;" in clear_resource_block
    assert "(void)clearPersisted;" in clear_slot_block
    assert "Com_Memset( slot, 0, sizeof( *slot ) );" in clear_slot_block


def test_client_browser_host_core_reconstructs_retained_runtime_owner() -> None:
    cl_cgame = (REPO_ROOT / "src/code/client/cl_cgame.c").read_text(encoding="utf-8")
    cl_webpak = (REPO_ROOT / "src/code/client/cl_webpak.c").read_text(encoding="utf-8")
    qcommon_h = (REPO_ROOT / "src/code/qcommon/qcommon.h").read_text(encoding="utf-8")
    files_c = (REPO_ROOT / "src/code/qcommon/files.c").read_text(encoding="utf-8")

    load_scripts_block = _extract_function_block(cl_cgame, "static void QLLoadHandler_LoadDocumentScripts( void ) {")
    resolve_session_block = _extract_function_block(cl_cgame, "static void CL_WebHost_ResolveSessionPath( char *buffer, size_t bufferSize ) {")
    register_sources_block = _extract_function_block(cl_cgame, "static void QLWebHost_RegisterRuntimeSources( void ) {")
    wait_bootstrap_block = _extract_function_block(cl_cgame, "static qboolean QLWebHost_WaitForBootstrapReady( void ) {")
    install_listeners_block = _extract_function_block(cl_cgame, "static void QLWebHost_InstallRuntimeListeners( void ) {")
    upload_surface_block = _extract_function_block(cl_cgame, "static qboolean QLWebView_UploadSurfaceImage( void ) {")
    runtime_block = _extract_function_block(cl_cgame, "static qboolean QLWebHost_EnsureRuntime( void ) {")
    open_block = _extract_function_block(cl_cgame, "static qboolean QLWebHost_OpenURL( const char *url ) {")
    document_ready_block = _extract_function_block(cl_cgame, "static void QLLoadHandler_OnDocumentReady( void ) {")
    webpak_list_block = _extract_function_block(cl_webpak, "int CL_WebPak_GetFileList( const char *path, const char *extension, char *listbuf, int bufsize ) {")
    pak_list_block = _extract_function_block(files_c, "int FS_GetPakFileList( const pack_t *pack, const char *path, const char *extension, char *listbuf, int bufsize ) {")
    bridge_block = _extract_function_block(cl_cgame, "void CL_RefreshOnlineServicesBridgeState( void ) {")
    frame_block = _extract_function_block(cl_cgame, "void CL_WebHost_Frame( void ) {")
    shutdown_block = _extract_function_block(cl_cgame, "void CL_WebHost_Shutdown( void ) {")

    assert '#define CL_WEB_DEFAULT_URL "asset://ql/index.html"' in cl_cgame
    assert '#define CL_WEB_SURFACE_SHADER "browser"' in cl_cgame
    assert "#define CL_WEB_BOOTSTRAP_MAX_ATTEMPTS 10" in cl_cgame
    assert "#define CL_WEB_BOOTSTRAP_SLEEP_MSEC 100" in cl_cgame
    assert "int\t\tFS_GetPakFileList( const pack_t *pack, const char *path, const char *extension, char *listbuf, int bufsize );" in qcommon_h
    assert 'Cvar_VariableStringBuffer( "fs_homepath", buffer, bufferSize );' in resolve_session_block
    assert "cl_webHost.dataPakSourceInstalled = qtrue;" in register_sources_block
    assert "cl_webHost.steamDataSourceInstalled = qtrue;" in register_sources_block
    assert "cl_webHost.resourceInterceptorInstalled = qtrue;" in register_sources_block
    assert "for ( attempt = 0; attempt < CL_WEB_BOOTSTRAP_MAX_ATTEMPTS; attempt++ ) {" in wait_bootstrap_block
    assert "NET_Sleep( CL_WEB_BOOTSTRAP_SLEEP_MSEC );" in wait_bootstrap_block
    assert "cl_webHost.bootstrapReady = qtrue;" in wait_bootstrap_block
    assert "cl_webHost.dialogHandlerInstalled = qtrue;" in install_listeners_block
    assert "cl_webHost.viewHandlerInstalled = qtrue;" in install_listeners_block
    assert "cl_webHost.loadHandlerInstalled = qtrue;" in install_listeners_block
    assert 'Q_strncpyz( cl_webHost.surfaceShaderName, CL_WEB_SURFACE_SHADER, sizeof( cl_webHost.surfaceShaderName ) );' in upload_surface_block
    assert "cl_webHost.surfaceShader = CL_RegisterShaderFromRGBA(" in upload_surface_block
    assert "cl_webHost.coreInitialised = qtrue;" in runtime_block
    assert "cl_webHost.sessionInitialised = qtrue;" in runtime_block
    assert "cl_webHost.viewInitialised = qtrue;" in runtime_block
    assert "QLWebHost_RegisterRuntimeSources();" in runtime_block
    assert "cl_webHost.jsMethodHandlerInstalled = qtrue;" in runtime_block
    assert "if ( !QLWebHost_WaitForBootstrapReady() ) {" in runtime_block
    assert "QLWebHost_InstallRuntimeListeners();" in runtime_block
    assert "QLWebView_Resize( cls.glconfig.vidWidth, cls.glconfig.vidHeight );" in runtime_block
    assert "QLWebView_RebuildSurfaceImage();" in runtime_block

    assert "Q_strncpyz( cl_webHost.currentUrl, url ? url : CL_WEB_DEFAULT_URL, sizeof( cl_webHost.currentUrl ) );" in open_block
    assert "QLLoadHandler_OnBeginLoadingFrame();" in open_block
    assert "CL_WebHost_PrimeLauncherDocument( cl_webHost.currentUrl )" in open_block
    assert "QLLoadHandler_OnDocumentReady();" in open_block
    assert "QLLoadHandler_OnFailLoadingFrame( cl_webHost.currentUrl );" in open_block
    assert 'count = CL_WebPak_GetFileList( "js", ".js", fileList, sizeof( fileList ) );' in load_scripts_block
    assert "CL_LauncherRequestData( scriptPath, &scriptBuffer, &scriptLength )" in load_scripts_block
    assert "QLLoadHandler_LoadDocumentScripts();" in document_ready_block
    assert "QLJSHandler_BindQzInstance();" in document_ready_block
    assert 'CL_WebView_PublishEvent( "web.object.ready", NULL );' in document_ready_block
    assert "sourceCount = FS_GetPakFileList( cl_webPak, path, extension, sourceList, sizeof( sourceList ) );" in webpak_list_block
    assert "sourceCount = CL_WebDataPak_GetFileList( path, extension, sourceList, sizeof( sourceList ) );" in webpak_list_block
    assert "sourceCount = FS_GetFileList( path, extension, sourceList, sizeof( sourceList ) );" in webpak_list_block
    assert "nFiles = FS_AddFileToList( name + temp, list, nFiles );" in pak_list_block

    assert 'Cvar_Set( "ui_browserAwesomium", overlayAvailable ? "1" : "0" );' in bridge_block
    assert 'Cvar_Set( "ui_browserAwesomiumProvider", overlayProvider );' in bridge_block
    assert 'Cvar_Set( "ui_browserAwesomiumPolicy", overlayPolicy );' in bridge_block
    assert "CL_WebHost_ResetRuntime( qtrue );" in bridge_block

    assert "CL_RefreshOnlineServicesBridgeState();" in frame_block
    assert "QLWebHost_OpenURL( CL_WEB_DEFAULT_URL );" in frame_block
    assert "Q_stricmp( cl_webHost.currentUrl, expectedUrl )" in frame_block
    assert "QLWebCore_Update();" in frame_block
    assert "QLWebHost_PumpFrame();" in frame_block

    assert "QLWebHost_HideBrowser();" in shutdown_block
    assert "CL_Web_ClearSessionState();" in shutdown_block
    assert "CL_WebHost_ResetRuntime( qtrue );" in shutdown_block
    assert "CL_ResetBrowserOverlayState();" in shutdown_block


def test_client_browser_commands_drive_retained_host_owner_surface() -> None:
    cl_cgame = (REPO_ROOT / "src/code/client/cl_cgame.c").read_text(encoding="utf-8")

    show_browser_block = _extract_function_block(cl_cgame, "void CL_Web_ShowBrowser_f( void )")
    change_hash_block = _extract_function_block(cl_cgame, "void CL_Web_ChangeHash_f( void )")
    browser_active_block = _extract_function_block(cl_cgame, "void CL_Web_BrowserActive_f( void )")
    hide_browser_block = _extract_function_block(cl_cgame, "void CL_Web_HideBrowser_f( void )")
    show_error_block = _extract_function_block(cl_cgame, "void CL_Web_ShowError_f( void )")
    reload_view_block = _extract_function_block(cl_cgame, "static void QLWebHost_ReloadView( qboolean ignoreCache ) {")
    reload_block = _extract_function_block(cl_cgame, "void CL_Web_Reload_f( void )")
    stop_refresh_block = _extract_function_block(cl_cgame, "void CL_Web_StopRefresh_f( void )")

    assert "QLWebHost_NavigateOrOpen( cl_webBrowserHash );" in show_browser_block
    assert "QLWebHost_NavigateOrOpen( cl_webBrowserHash );" in change_hash_block
    assert "QLWebHost_HideBrowser();" in browser_active_block
    assert "QLWebHost_HideBrowser();" in hide_browser_block
    assert "CL_WebView_PublishGameError( message );" in show_error_block
    assert "cl_webHost.currentUrl[0]" in reload_view_block
    assert "CL_WebHost_PrimeLauncherDocument( cl_webHost.currentUrl )" in reload_view_block
    assert "QLWebHost_ReloadView( qtrue );" in reload_block
    assert "cl_webHost.refreshStopped = qtrue;" in stop_refresh_block


def test_client_browser_js_bridge_reconstructs_qz_instance_contract() -> None:
    cl_cgame = (REPO_ROOT / "src/code/client/cl_cgame.c").read_text(encoding="utf-8")

    bind_block = _extract_function_block(cl_cgame, "static void QLJSHandler_BindQzInstance( void ) {")
    load_scripts_block = _extract_function_block(cl_cgame, "static void QLLoadHandler_LoadDocumentScripts( void ) {")
    document_ready_block = _extract_function_block(cl_cgame, "static void QLLoadHandler_OnDocumentReady( void ) {")
    next_power_block = _extract_function_block(cl_cgame, "static int QLWebView_NextPowerOfTwo( int value ) {")
    map_cursor_block = _extract_function_block(cl_cgame, "static int QLWebView_MapCursorCoordinate( int coordinate, int viewDimension, int surfaceDimension ) {")
    mapped_mouse_block = _extract_function_block(cl_cgame, "static void QLWebView_InjectMappedMouseMove( int x, int y ) {")
    rebuild_surface_block = _extract_function_block(cl_cgame, "static void QLWebView_RebuildSurfaceImage( void ) {")
    coerce_integer_block = _extract_function_block(
        cl_cgame, "static int QLJSHandler_CoerceIntegerArgument( const char *argument ) {"
    )
    coerce_unsigned_integer_block = _extract_function_block(
        cl_cgame, "static uint32_t QLJSHandler_CoerceUnsignedIntegerArgument( const char *argument ) {"
    )
    method_block = _extract_function_block(
        cl_cgame,
        "static qboolean QLJSHandler_OnMethodCall( const char *methodName, const char **arguments, int argumentCount ) {",
    )
    return_block = _extract_function_block(
        cl_cgame,
        "static qboolean QLJSHandler_OnMethodCallWithReturnValue( const char *methodName, const char **arguments, int argumentCount, char *outValue, size_t outValueSize ) {",
    )
    mouse_block = _extract_function_block(cl_cgame, "static void QLWebView_InjectMouseMove( int x, int y ) {")
    mouse_down_block = _extract_function_block(cl_cgame, "static void QLWebView_InjectMouseDown( int key ) {")
    mouse_up_block = _extract_function_block(cl_cgame, "static void QLWebView_InjectMouseUp( int key ) {")
    wheel_block = _extract_function_block(cl_cgame, "static void QLWebView_InjectMouseWheel( int direction ) {")
    key_block = _extract_function_block(cl_cgame, "static void QLWebView_InjectKeyboardEvent( int key, qboolean down ) {")
    activation_block = _extract_function_block(cl_cgame, "static void QLWebView_InjectActivationKeyboardEvent( void ) {")
    app_activate_block = _extract_function_block(cl_cgame, "void CL_WebHost_NotifyAppActivation( qboolean active ) {")
    public_mouse_block = _extract_function_block(cl_cgame, "void CL_WebView_OnMouseMove( int x, int y ) {")
    public_mouse_button_block = _extract_function_block(cl_cgame, "void CL_WebView_OnMouseButtonEvent( int key, qboolean down ) {")
    public_wheel_event_block = _extract_function_block(cl_cgame, "void CL_WebView_OnMouseWheelEvent( int direction ) {")
    public_key_block = _extract_function_block(cl_cgame, "void CL_WebView_OnKeyEvent( int key, qboolean down ) {")

    assert "CL_WEB_METHOD_OPEN_STEAM_OVERLAY_URL = 11," in cl_cgame
    assert "CL_WEB_METHOD_SET_CLIPBOARD_TEXT = 13," in cl_cgame
    assert "CL_WEB_METHOD_REQUEST_SERVERS = 14," in cl_cgame
    assert "CL_WEB_METHOD_REQUEST_SERVER_DETAILS = 15," in cl_cgame
    assert "CL_WEB_METHOD_REFRESH_LIST = 16," in cl_cgame
    assert "CL_WEB_METHOD_CREATE_LOBBY = 17," in cl_cgame
    assert "CL_WEB_METHOD_ACTIVATE_GAME_OVERLAY_TO_USER = 25," in cl_cgame
    assert "CL_WEB_METHOD_NO_OP = 30," in cl_cgame
    assert "CL_WEB_METHOD_SET_FAVORITE_SERVER = 33" in cl_cgame
    assert '{ "GetClipboardText", CL_WEB_METHOD_GET_CLIPBOARD_TEXT, qtrue }' in cl_cgame
    assert '{ "OpenSteamOverlayURL", CL_WEB_METHOD_OPEN_STEAM_OVERLAY_URL, qfalse }' in cl_cgame
    assert '{ "SetClipboardText", CL_WEB_METHOD_SET_CLIPBOARD_TEXT, qfalse }' in cl_cgame
    assert '{ "RequestServers", CL_WEB_METHOD_REQUEST_SERVERS, qfalse }' in cl_cgame
    assert '{ "RequestServerDetails", CL_WEB_METHOD_REQUEST_SERVER_DETAILS, qfalse }' in cl_cgame
    assert '{ "RefreshList", CL_WEB_METHOD_REFRESH_LIST, qfalse }' in cl_cgame
    assert '{ "CreateLobby", CL_WEB_METHOD_CREATE_LOBBY, qfalse }' in cl_cgame
    assert '{ "LeaveLobby", CL_WEB_METHOD_LEAVE_LOBBY, qfalse }' in cl_cgame
    assert '{ "JoinLobby", CL_WEB_METHOD_JOIN_LOBBY, qfalse }' in cl_cgame
    assert '{ "SetLobbyServer", CL_WEB_METHOD_SET_LOBBY_SERVER, qfalse }' in cl_cgame
    assert '{ "ShowInviteOverlay", CL_WEB_METHOD_SHOW_INVITE_OVERLAY, qfalse }' in cl_cgame
    assert '{ "SayLobby", CL_WEB_METHOD_SAY_LOBBY, qfalse }' in cl_cgame
    assert '{ "RequestUserStats", CL_WEB_METHOD_REQUEST_USER_STATS, qfalse }' in cl_cgame
    assert '{ "GetFriendList", CL_WEB_METHOD_GET_FRIEND_LIST, qtrue }' in cl_cgame
    assert '{ "ActivateGameOverlayToUser", CL_WEB_METHOD_ACTIVATE_GAME_OVERLAY_TO_USER, qfalse }' in cl_cgame
    assert '{ "Invite", CL_WEB_METHOD_INVITE, qfalse }' in cl_cgame
    assert '{ "FileExists", CL_WEB_METHOD_FILE_EXISTS, qtrue }' in cl_cgame
    assert '{ "GetConfig", CL_WEB_METHOD_GET_CONFIG, qtrue }' in cl_cgame
    assert '{ "GetCursorPosition", CL_WEB_METHOD_GET_CURSOR_POSITION, qtrue }' in cl_cgame
    assert '{ "NoOp", CL_WEB_METHOD_NO_OP, qfalse }' in cl_cgame
    assert '{ "GetAllUGC", CL_WEB_METHOD_GET_ALL_UGC, qfalse }' in cl_cgame
    assert '{ "GetNextKeyDown", CL_WEB_METHOD_GET_NEXT_KEY_DOWN, qfalse }' in cl_cgame

    assert "cl_webHost.qzInstanceBound = qtrue;" in bind_block
    assert "cl_webHost.windowObjectBound = qtrue;" in bind_block
    assert 'count = CL_WebPak_GetFileList( "js", ".js", fileList, sizeof( fileList ) );' in load_scripts_block
    assert "CL_LauncherRequestData( scriptPath, &scriptBuffer, &scriptLength )" in load_scripts_block
    assert "QLLoadHandler_LoadDocumentScripts();" in document_ready_block
    assert "for ( result = 1; result < value; result <<= 1 ) {" in next_power_block
    assert "targetDimension = surfaceDimension > 0 ? surfaceDimension : viewDimension;" in map_cursor_block
    assert "cl_webHost.cursorX = cursorX;" in mapped_mouse_block
    assert "cl_webHost.surfaceWidth = QLWebView_NextPowerOfTwo( cl_webHost.viewWidth );" in rebuild_surface_block
    assert "cl_webHost.surfaceHeight = QLWebView_NextPowerOfTwo( cl_webHost.viewHeight );" in rebuild_surface_block
    assert "QLJSHandler_BindQzInstance();" in document_ready_block
    assert 'CL_WebView_PublishEvent( "web.object.ready", NULL );' in document_ready_block
    assert "value = strtol( argument, &end, 10 );" in coerce_integer_block
    assert "if ( end == argument ) {" in coerce_integer_block
    assert "while ( *end && isspace( (unsigned char)*end ) ) {" in coerce_integer_block
    assert "if ( *end ) {" in coerce_integer_block
    assert "return (int)value;" in coerce_integer_block
    assert "value = strtoul( argument, &end, 10 );" in coerce_unsigned_integer_block
    assert "if ( end == argument ) {" in coerce_unsigned_integer_block
    assert "while ( *end && isspace( (unsigned char)*end ) ) {" in coerce_unsigned_integer_block
    assert "if ( *end ) {" in coerce_unsigned_integer_block
    assert "return (uint32_t)value;" in coerce_unsigned_integer_block

    assert "case CL_WEB_METHOD_OPEN_STEAM_OVERLAY_URL:" in method_block
    assert "if ( argumentCount < 1 || !arguments[0] || !arguments[0][0] ) {\n\t\t\t\treturn qfalse;\n\t\t\t}\n\t\t\treturn CL_Steam_OpenOverlayUrl( arguments[0] );" not in method_block
    assert "return CL_Steam_OpenOverlayUrl( arguments[0] );" in method_block
    assert "case CL_WEB_METHOD_SET_CLIPBOARD_TEXT:" in method_block
    assert 'Sys_SetClipboardData( arguments[0] ? arguments[0] : "" );' in method_block
    assert "case CL_WEB_METHOD_REQUEST_SERVERS:" in method_block
    assert "return CL_Steam_RequestServers( QLJSHandler_CoerceIntegerArgument( arguments[0] ) );" in method_block
    assert "case CL_WEB_METHOD_REQUEST_SERVER_DETAILS:" in method_block
    assert "return CL_Steam_RequestServerDetails(" in method_block
    assert "QLJSHandler_CoerceUnsignedIntegerArgument( arguments[0] )" in method_block
    assert "(unsigned short)QLJSHandler_CoerceIntegerArgument( arguments[1] )" in method_block
    assert "case CL_WEB_METHOD_REFRESH_LIST:" in method_block
    assert "return CL_Steam_RefreshServerList();" in method_block
    assert "case CL_WEB_METHOD_CREATE_LOBBY:" in method_block
    assert "return CL_Steam_CreateLobby();" in method_block
    assert "case CL_WEB_METHOD_LEAVE_LOBBY:" in method_block
    assert "return CL_Steam_LeaveLobby();" in method_block
    assert "case CL_WEB_METHOD_JOIN_LOBBY:" in method_block
    assert "return CL_Steam_JoinLobby( arguments[0] );" in method_block
    assert "case CL_WEB_METHOD_SET_LOBBY_SERVER:" in method_block
    assert "return CL_Steam_SetLobbyServer(" in method_block
    assert "case CL_WEB_METHOD_SHOW_INVITE_OVERLAY:" in method_block
    assert "return CL_Steam_ShowInviteOverlay();" in method_block
    assert "case CL_WEB_METHOD_SAY_LOBBY:" in method_block
    assert 'return CL_Steam_SayLobby( arguments[0] ? arguments[0] : "" );' in method_block
    assert "case CL_WEB_METHOD_REQUEST_USER_STATS:" in method_block
    assert "return CL_Steam_RequestUserStats( arguments[0] );" in method_block
    assert "case CL_WEB_METHOD_ACTIVATE_GAME_OVERLAY_TO_USER:" in method_block
    assert "return CL_Steam_ActivateOverlayToUser( arguments[0], arguments[1] );" in method_block
    assert "case CL_WEB_METHOD_INVITE:" in method_block
    assert "return CL_Steam_Invite( arguments[0] );" in method_block
    assert "case CL_WEB_METHOD_GET_ALL_UGC:" in method_block
    assert "if ( argumentCount < 1 ) {" in method_block
    assert "return CL_Steam_RequestAllUGC( QLJSHandler_CoerceIntegerArgument( arguments[0] ) );" in method_block
    assert "case CL_WEB_METHOD_GET_NEXT_KEY_DOWN:" in method_block
    assert "if ( argumentCount <= 0 ) {" in method_block
    assert "cl_webHost.keyCaptureArmed = qtrue;" in method_block
    assert "cl_webHost.keyCaptureArmed = QLJSHandler_CoerceIntegerArgument( arguments[0] ) != 0 ? qtrue : qfalse;" in method_block
    assert "case CL_WEB_METHOD_NO_OP:" in method_block
    assert "return qtrue;" in method_block
    assert "case CL_WEB_METHOD_SET_FAVORITE_SERVER:" in method_block
    assert "CL_WebHost_SetFavoriteServer(" in method_block
    assert "(uint16_t)QLJSHandler_CoerceIntegerArgument( arguments[1] )" in method_block
    assert "QLJSHandler_CoerceIntegerArgument( arguments[2] ) != 0 ? qtrue : qfalse" in method_block

    assert "case CL_WEB_METHOD_GET_FRIEND_LIST:" in return_block
    assert "CL_WebHost_BuildFriendListJson( outValue, outValueSize );" in return_block
    assert "case CL_WEB_METHOD_GET_CONFIG:" in return_block
    assert "CL_WebHost_BuildConfigJson( outValue, outValueSize );" in return_block
    assert "case CL_WEB_METHOD_GET_CURSOR_POSITION:" in return_block
    assert "CL_WebHost_RequestCursorPosition( &x, &y );" in return_block
    assert "case CL_WEB_METHOD_GET_CLIPBOARD_TEXT:" in return_block
    assert "Sys_GetClipboardData();" in return_block

    assert "QLWebView_InjectMappedMouseMove(" in mouse_block
    assert "QLWebView_MapCursorCoordinate( x, cl_webHost.viewWidth, cl_webHost.surfaceWidth )" in mouse_block
    assert "QLWebView_MapCursorCoordinate( y, cl_webHost.viewHeight, cl_webHost.surfaceHeight )" in mouse_block
    assert "button = CL_WebHost_MapMouseButton( key );" in mouse_down_block
    assert "button = CL_WebHost_MapMouseButton( key );" in mouse_up_block
    assert "QLWebView_InjectMappedMouseMove( cl_webHost.cursorX, cl_webHost.cursorY );" in mouse_down_block
    assert "if ( direction == 0 ) {" in wheel_block
    assert "QLWebView_PublishGameKey( key );" in key_block
    assert "cl_webHost.keyCaptureArmed = qfalse;" in key_block
    assert "QLWebView_InjectKeyboardEvent( 0x11, qtrue );" in activation_block
    assert "QLWebView_InjectActivationKeyboardEvent();" in app_activate_block
    assert "QLWebView_InjectMouseMove( x, y );" in public_mouse_block
    assert "QLWebView_InjectMouseDown( key );" in public_mouse_button_block
    assert "QLWebView_InjectMouseUp( key );" in public_mouse_button_block
    assert "QLWebView_InjectMouseWheel( direction );" in public_wheel_event_block
    assert "QLWebView_InjectKeyboardEvent( key, down );" in public_key_block
    assert 'CL_WebView_PublishEvent( "game.key", payload );' in cl_cgame


def test_client_browser_lobby_social_shims_reconstruct_retail_qz_instance_dispatch_surface() -> None:
    client_h = (REPO_ROOT / "src/code/client/client.h").read_text(encoding="utf-8")
    cl_main = (REPO_ROOT / "src/code/client/cl_main.c").read_text(encoding="utf-8")
    qcommon_h = (REPO_ROOT / "src/code/qcommon/qcommon.h").read_text(encoding="utf-8")
    win_main = (REPO_ROOT / "src/code/win32/win_main.c").read_text(encoding="utf-8")
    unix_main = (REPO_ROOT / "src/code/unix/unix_main.c").read_text(encoding="utf-8")
    null_main = (REPO_ROOT / "src/code/null/null_main.c").read_text(encoding="utf-8")
    platform_steamworks_h = (REPO_ROOT / "src/common/platform/platform_steamworks.h").read_text(encoding="utf-8")
    platform_steamworks_c = (REPO_ROOT / "src/common/platform/platform_steamworks.c").read_text(encoding="utf-8")

    current_lobby_block = _extract_function_block(
        cl_main, "static qboolean CL_Steam_GetCurrentLobbyIdentityWords( uint32_t *outIdLow, uint32_t *outIdHigh )"
    )
    open_overlay_url_block = _extract_function_block(cl_main, "qboolean CL_Steam_OpenOverlayUrl( const char *url )")
    create_block = _extract_function_block(cl_main, "qboolean CL_Steam_CreateLobby( void )")
    leave_block = _extract_function_block(cl_main, "qboolean CL_Steam_LeaveLobby( void )")
    join_block = _extract_function_block(cl_main, "qboolean CL_Steam_JoinLobby( const char *lobbyId )")
    set_server_block = _extract_function_block(
        cl_main, "qboolean CL_Steam_SetLobbyServer( unsigned int serverIp, unsigned short serverPort )"
    )
    show_invite_block = _extract_function_block(cl_main, "qboolean CL_Steam_ShowInviteOverlay( void )")
    invite_connect_block = _extract_function_block(
        cl_main, "static qboolean CL_Steam_BuildInviteConnectString( char *buffer, size_t bufferSize )"
    )
    invite_block = _extract_function_block(cl_main, "qboolean CL_Steam_Invite( const char *steamId )")
    say_block = _extract_function_block(cl_main, "qboolean CL_Steam_SayLobby( const char *message )")
    request_ugc_block = _extract_function_block(cl_main, "qboolean CL_Steam_RequestAllUGC( int filter )")
    request_stats_block = _extract_function_block(cl_main, "qboolean CL_Steam_RequestUserStats( const char *steamId )")
    activate_overlay_block = _extract_function_block(
        cl_main, "qboolean CL_Steam_ActivateOverlayToUser( const char *dialog, const char *steamId )"
    )
    request_all_ugc_query_block = _extract_function_block(
        platform_steamworks_c, "qboolean QL_Steamworks_RequestAllUGCQuery( uint32_t filter )"
    )
    query_ugc_result_block = _extract_function_block(
        platform_steamworks_c,
        "qboolean QL_Steamworks_GetQueryUGCResult( uint64_t queryHandle, uint32_t index, uint64_t *outPublishedFileId, char *title, size_t titleSize, char *description, size_t descriptionSize )",
    )
    query_ugc_preview_block = _extract_function_block(
        platform_steamworks_c, "qboolean QL_Steamworks_GetQueryUGCPreviewURL( uint64_t queryHandle, uint32_t index, char *buffer, size_t bufferSize )"
    )
    release_ugc_query_block = _extract_function_block(
        platform_steamworks_c, "void QL_Steamworks_ReleaseQueryUGCRequest( uint64_t queryHandle )"
    )
    activate_overlay_web_page_block = _extract_function_block(
        platform_steamworks_c, "qboolean QL_Steamworks_ActivateOverlayToWebPage( const char *url )"
    )
    platform_block = _extract_function_block(
        platform_steamworks_c,
        "qboolean QL_Steamworks_ActivateOverlayToUser( const char *dialog, uint32_t idLow, uint32_t idHigh )",
    )
    invite_user_to_lobby_block = _extract_function_block(
        platform_steamworks_c,
        "qboolean QL_Steamworks_InviteUserToLobby( uint32_t lobbyIdLow, uint32_t lobbyIdHigh, uint32_t userIdLow, uint32_t userIdHigh )",
    )
    invite_user_to_game_block = _extract_function_block(
        platform_steamworks_c,
        "qboolean QL_Steamworks_InviteUserToGame( uint32_t idLow, uint32_t idHigh, const char *connectString )",
    )
    win_set_clipboard_block = _extract_function_block(win_main, "void Sys_SetClipboardData( const char *text )")
    unix_write_clipboard_block = _extract_function_block(
        unix_main, "static qboolean Sys_WriteClipboardCommand( const char *command, const char *text ) {"
    )
    unix_set_clipboard_block = _extract_function_block(unix_main, "void Sys_SetClipboardData( const char *text ) {")
    null_set_clipboard_block = _extract_function_block(null_main, "void Sys_SetClipboardData( const char *text ) {")

    assert "qboolean CL_Steam_OpenOverlayUrl( const char *url );" in client_h
    assert "qboolean CL_Steam_CreateLobby( void );" in client_h
    assert "qboolean CL_Steam_LeaveLobby( void );" in client_h
    assert "qboolean CL_Steam_JoinLobby( const char *lobbyId );" in client_h
    assert "qboolean CL_Steam_SetLobbyServer( unsigned int serverIp, unsigned short serverPort );" in client_h
    assert "qboolean CL_Steam_ShowInviteOverlay( void );" in client_h
    assert "qboolean CL_Steam_Invite( const char *steamId );" in client_h
    assert "qboolean CL_Steam_SayLobby( const char *message );" in client_h
    assert "qboolean CL_Steam_RequestAllUGC( int filter );" in client_h
    assert "qboolean CL_Steam_RequestUserStats( const char *steamId );" in client_h
    assert "qboolean CL_Steam_ActivateOverlayToUser( const char *dialog, const char *steamId );" in client_h
    assert "void\tSys_SetClipboardData( const char *text );" in qcommon_h
    assert "qboolean QL_Steamworks_ActivateOverlayToWebPage( const char *url );" in platform_steamworks_h
    assert "qboolean QL_Steamworks_InviteUserToLobby( uint32_t lobbyIdLow, uint32_t lobbyIdHigh, uint32_t userIdLow, uint32_t userIdHigh );" in platform_steamworks_h
    assert "qboolean QL_Steamworks_InviteUserToGame( uint32_t idLow, uint32_t idHigh, const char *connectString );" in platform_steamworks_h
    assert "qboolean QL_Steamworks_RequestAllUGCQuery( uint32_t filter );" in platform_steamworks_h
    assert "qboolean QL_Steamworks_GetQueryUGCResult( uint64_t queryHandle, uint32_t index, uint64_t *outPublishedFileId, char *title, size_t titleSize, char *description, size_t descriptionSize );" in platform_steamworks_h
    assert "qboolean QL_Steamworks_GetQueryUGCPreviewURL( uint64_t queryHandle, uint32_t index, char *buffer, size_t bufferSize );" in platform_steamworks_h
    assert "void QL_Steamworks_ReleaseQueryUGCRequest( uint64_t queryHandle );" in platform_steamworks_h

    assert "currentLobbyValid" not in cl_main
    assert "static qboolean CL_Steam_ParseIdentityArgument" not in cl_main
    assert "cl_steamCallbackState.currentLobbyValid" not in current_lobby_block
    assert "idLow = (uint32_t)( cl_steamCallbackState.currentLobbyId & 0xffffffffu );" in current_lobby_block
    assert "idHigh = (uint32_t)( cl_steamCallbackState.currentLobbyId >> 32 );" in current_lobby_block
    assert "accountType = ( idHigh >> 20 ) & 0xfu;" in current_lobby_block
    assert "accountInstance = idHigh & 0xfffffu;" in current_lobby_block
    assert "universe = ( idHigh >> 24 ) & 0xffu;" in current_lobby_block
    assert "if ( accountType == 0u || accountType >= 0xbu ) {" in current_lobby_block
    assert "if ( universe == 0u || universe >= 5u ) {" in current_lobby_block
    assert "if ( accountType == 1u ) {" in current_lobby_block
    assert "accountInstance > 4u" in current_lobby_block
    assert "accountInstance != 0u" in current_lobby_block
    assert "accountType == 3u && idLow == 0u" in current_lobby_block
    assert 'if ( !url ) {' in open_overlay_url_block
    assert 'CL_LogSocialOverlayIgnored( "OpenSteamOverlayURL", "missing overlay url" );' in open_overlay_url_block
    assert 'CL_LogSocialOverlayIgnored( "OpenSteamOverlayURL", "social overlay provider unavailable" );' in open_overlay_url_block
    assert "QL_Steamworks_ActivateOverlayToWebPage( url )" in open_overlay_url_block
    assert 'CL_LogSocialOverlayIgnored( "OpenSteamOverlayURL", "overlay page activation failed" );' in open_overlay_url_block
    assert "maxMembers = cl_steamMaxLobbyClients ? cl_steamMaxLobbyClients->integer : 16;" in create_block
    assert "if ( maxMembers <= 0 ) {" not in create_block
    assert "return QL_Steamworks_CreateLobby( maxMembers );" in create_block
    assert 'CL_LogMatchmakingServiceIgnored( "LeaveLobby", "no active lobby" );' not in leave_block
    assert "CL_Steam_LeaveCurrentLobby();" in leave_block
    assert "parsedLobbyId = 0ull;" in join_block
    assert 'sscanf( lobbyId, "%llu", &parsedLobbyId );' in join_block
    assert 'CL_LogMatchmakingServiceIgnored( "JoinLobby", "invalid lobby id" );' not in join_block
    assert "CL_Steam_ParseIdentityArgument( lobbyId, &lobbyIdLow, &lobbyIdHigh )" not in join_block
    assert "return QL_Steamworks_JoinLobby(" in join_block
    assert "(uint32_t)( parsedLobbyId & 0xffffffffu )" in join_block
    assert "(uint32_t)( parsedLobbyId >> 32 )" in join_block
    assert "CL_Steam_GetCurrentLobbyIdentityWords( &lobbyIdLow, &lobbyIdHigh )" in set_server_block
    assert "return QL_Steamworks_SetLobbyServer( lobbyIdLow, lobbyIdHigh, (uint32_t)serverIp, (uint16_t)serverPort );" in set_server_block
    assert "CL_Steam_GetCurrentLobbyIdentityWords( &lobbyIdLow, &lobbyIdHigh )" in show_invite_block
    assert "return QL_Steamworks_ShowInviteOverlay( lobbyIdLow, lobbyIdHigh );" in show_invite_block
    assert "!com_sv_running->integer" in invite_connect_block
    assert "NET_AdrToString( serverAddress )" in invite_connect_block
    assert 'Cvar_Get( "net_port", va( "%i", PORT_SERVER ), CVAR_LATCH )' in invite_connect_block
    assert 'Cvar_VariableIntegerValue( "sv_serverType" ) == 1' in invite_connect_block
    assert "NET_GetLocalAddressIP( &localAddress )" in invite_connect_block
    assert "QL_Steamworks_ServerGetPublicIP()" in invite_connect_block
    assert '"+connect %lu:%s"' in invite_connect_block
    assert "parsedSteamId = 0ull;" in invite_block
    assert 'sscanf( steamId, "%llu", &parsedSteamId );' in invite_block
    assert 'CL_LogMatchmakingServiceIgnored( "Invite", "invalid target user id" );' not in invite_block
    assert "CL_Steam_ParseIdentityArgument( steamId, &steamIdLow, &steamIdHigh )" not in invite_block
    assert "cls.state != CA_ACTIVE" in invite_block
    assert "CL_Steam_GetCurrentLobbyIdentityWords( &lobbyIdLow, &lobbyIdHigh )" in invite_block
    assert "QL_Steamworks_InviteUserToLobby(" in invite_block
    assert "(uint32_t)( parsedSteamId & 0xffffffffu )" in invite_block
    assert "(uint32_t)( parsedSteamId >> 32 )" in invite_block
    assert "CL_Steam_BuildInviteConnectString( connectString, sizeof( connectString ) )" in invite_block
    assert "return QL_Steamworks_InviteUserToGame(" in invite_block
    assert "CL_Steam_GetCurrentLobbyIdentityWords( &lobbyIdLow, &lobbyIdHigh )" in say_block
    assert 'CL_LogMatchmakingServiceIgnored( "SayLobby", "missing lobby message" );' not in say_block
    assert 'lobbyMessage = message ? message : "";' in say_block
    assert "return QL_Steamworks_SayLobby( lobbyIdLow, lobbyIdHigh, lobbyMessage );" in say_block
    assert 'CL_LogWorkshopLifecycle( "request-ugc-query", "workshop provider unavailable" );' in request_ugc_block
    assert 'CL_LogWorkshopLifecycle( "request-ugc-query", "invalid query page" );' not in request_ugc_block
    assert "return QL_Steamworks_RequestAllUGCQuery( (uint32_t)filter );" in request_ugc_block
    assert "parsedSteamId = 0ull;" in request_stats_block
    assert 'sscanf( steamId, "%llu", &parsedSteamId );' in request_stats_block
    assert 'CL_LogStatsServiceIgnored( "RequestUserStats", "invalid user id" );' not in request_stats_block
    assert "CL_Steam_ParseIdentityArgument( steamId, &steamIdLow, &steamIdHigh )" not in request_stats_block
    assert "return QL_Steamworks_RequestUserStats(" in request_stats_block
    assert "(uint32_t)( parsedSteamId & 0xffffffffu )" in request_stats_block
    assert "(uint32_t)( parsedSteamId >> 32 )" in request_stats_block
    assert 'if ( !dialog ) {' in activate_overlay_block
    assert "parsedSteamId = 0ull;" in activate_overlay_block
    assert 'sscanf( steamId, "%llu", &parsedSteamId );' in activate_overlay_block
    assert 'CL_LogSocialOverlayIgnored( "ActivateGameOverlayToUser", "invalid target user id" );' not in activate_overlay_block
    assert "CL_Steam_ParseIdentityArgument( steamId, &steamIdLow, &steamIdHigh )" not in activate_overlay_block
    assert "return QL_Steamworks_ActivateOverlayToUser(" in activate_overlay_block
    assert "(uint32_t)( parsedSteamId & 0xffffffffu )" in activate_overlay_block
    assert "(uint32_t)( parsedSteamId >> 32 )" in activate_overlay_block
    assert "queryHandle = createQueryFn( ugc, NULL, 1, 0, appId, appId, filter );" in request_all_ugc_query_block
    assert "if ( filter < 1u ) {" not in request_all_ugc_query_block
    assert "callHandle = sendQueryFn( ugc, NULL, queryHandleLow, queryHandleHigh );" in request_all_ugc_query_block
    assert "!QL_Steamworks_BindUGCQueryCallResult( (SteamAPICall_t)callHandle )" in request_all_ugc_query_block
    assert "QL_Steamworks_ReleaseQueryUGCRequest( queryHandle );" in request_all_ugc_query_block
    assert "vtable[0x04 / 4]" in request_all_ugc_query_block
    assert "vtable[0x0c / 4]" in request_all_ugc_query_block
    assert "memcpy( outPublishedFileId, details, sizeof( *outPublishedFileId ) );" in query_ugc_result_block
    assert "QL_Steamworks_CopySteamString( title, titleSize, (const char *)( details + QL_STEAM_UGC_DETAILS_TITLE_OFFSET ) );" in query_ugc_result_block
    assert "QL_Steamworks_CopySteamString( description, descriptionSize, (const char *)( details + QL_STEAM_UGC_DETAILS_DESCRIPTION_OFFSET ) );" in query_ugc_result_block
    assert "vtable[0x10 / 4]" in query_ugc_result_block
    assert "vtable[0x14 / 4]" in query_ugc_preview_block
    assert "vtable[0x34 / 4]" in release_ugc_query_block
    assert "typedef void (__fastcall *QL_SteamFriends_ActivateGameOverlayToWebPageFn)( void *self, void *unused, const char *url );" in activate_overlay_web_page_block
    assert 'if ( !url ) {' in activate_overlay_web_page_block
    assert "fn = (QL_SteamFriends_ActivateGameOverlayToWebPageFn)vtable[0x78 / 4];" in activate_overlay_web_page_block
    assert "fn( friends, NULL, url );" in activate_overlay_web_page_block
    assert 'if ( !dialog ) {' in platform_block
    assert "vtable[0x40 / 4]" in invite_user_to_lobby_block
    assert "return fn( matchmaking, NULL, lobbyIdLow, lobbyIdHigh, userIdLow, userIdHigh ) ? qtrue : qfalse;" in invite_user_to_lobby_block
    assert "vtable[0xc4 / 4]" in invite_user_to_game_block
    assert "return fn( friends, NULL, idLow, idHigh, connectString ) ? qtrue : qfalse;" in invite_user_to_game_block
    assert "OpenClipboard( NULL ) == 0" in win_set_clipboard_block
    assert "EmptyClipboard();" in win_set_clipboard_block
    assert "GlobalAlloc( GMEM_MOVEABLE, textBytes );" in win_set_clipboard_block
    assert "memcpy( clipboardText, text, textBytes );" in win_set_clipboard_block
    assert "SetClipboardData( CF_TEXT, clipboardData );" in win_set_clipboard_block
    assert 'pipe = popen( command, "w" );' in unix_write_clipboard_block
    assert "bytesWritten = fwrite( text, 1, textBytes, pipe );" in unix_write_clipboard_block
    assert "pclose( pipe )" in unix_write_clipboard_block
    assert 'Sys_WriteClipboardCommand( "wl-copy --trim-newline 2>/dev/null", text )' in unix_set_clipboard_block
    assert 'Sys_WriteClipboardCommand( "wl-copy 2>/dev/null", text )' in unix_set_clipboard_block
    assert 'Sys_WriteClipboardCommand( "xclip -selection clipboard 2>/dev/null", text )' in unix_set_clipboard_block
    assert 'Sys_WriteClipboardCommand( "xsel --clipboard --input 2>/dev/null", text )' in unix_set_clipboard_block
    assert "(void)text;" in null_set_clipboard_block


def test_client_browser_favorite_server_lane_reconstructs_retail_steam_matchmaking_owner() -> None:
    cl_cgame = (REPO_ROOT / "src/code/client/cl_cgame.c").read_text(encoding="utf-8")
    platform_steamworks_h = (REPO_ROOT / "src/common/platform/platform_steamworks.h").read_text(encoding="utf-8")
    platform_steamworks_c = (REPO_ROOT / "src/common/platform/platform_steamworks.c").read_text(encoding="utf-8")

    favorite_block = _extract_function_block(
        cl_cgame, "static qboolean CL_WebHost_SetFavoriteServer( uint32_t ip, uint16_t port, qboolean add )"
    )
    mirror_block = _extract_function_block(
        cl_cgame, "static qboolean CL_WebHost_MirrorFavoriteServer( uint32_t ip, uint16_t port, qboolean add )"
    )
    steamworks_block = _extract_function_block(
        platform_steamworks_c, "qboolean QL_Steamworks_SetFavoriteServer( uint32_t serverIp, uint16_t serverPort, qboolean add )"
    )

    assert '#include "../../common/platform/platform_steamworks.h"' in cl_cgame
    assert "qboolean QL_Steamworks_SetFavoriteServer( uint32_t serverIp, uint16_t serverPort, qboolean add );" in platform_steamworks_h
    assert "if ( CL_SteamServicesEnabled() && !QL_Steamworks_SetFavoriteServer( ip, port, add ) ) {" in favorite_block
    assert "return CL_WebHost_MirrorFavoriteServer( ip, port, add );" in favorite_block
    assert "CL_WebHost_BuildFavoriteAddress( ip, port, addressString, sizeof( addressString ) );" in mirror_block
    assert "LAN_SaveServersToCache();" in mirror_block
    assert "QL_Steamworks_GetAppID();" in steamworks_block
    assert "typedef int (__fastcall *QL_SteamMatchmaking_AddFavoriteGameFn)" in steamworks_block
    assert "typedef qboolean (__fastcall *QL_SteamMatchmaking_RemoveFavoriteGameFn)" in steamworks_block
    assert "addFavoriteGameFn = (QL_SteamMatchmaking_AddFavoriteGameFn)vtable[0x08 / 4];" in steamworks_block
    assert "removeFavoriteGameFn = (QL_SteamMatchmaking_RemoveFavoriteGameFn)vtable[0x0c / 4];" in steamworks_block
    assert "lastPlayedTime = time( NULL );" in steamworks_block
    assert "serverPort," in steamworks_block
    assert "QL_STEAM_FAVORITE_FLAG_FAVORITE" in steamworks_block


def test_client_browser_server_shims_reconstruct_retail_server_browser_surface() -> None:
    client_h = (REPO_ROOT / "src/code/client/client.h").read_text(encoding="utf-8")
    cl_main = (REPO_ROOT / "src/code/client/cl_main.c").read_text(encoding="utf-8")

    request_mode_block = _extract_function_block(
        cl_main, "static int CL_SteamBrowser_RequestModeToSource( int requestMode )"
    )
    build_address_block = _extract_function_block(
        cl_main, "static void CL_SteamBrowser_BuildAddressString( uint32_t serverIp, uint16_t serverPort, char *buffer, size_t bufferSize )"
    )
    format_detail_id_block = _extract_function_block(
        cl_main, "static void CL_SteamBrowser_FormatDetailId( uint32_t serverIp, uint16_t serverPort, char *buffer, size_t bufferSize )"
    )
    request_servers_block = _extract_function_block(cl_main, "qboolean CL_Steam_RequestServers( int requestMode )")
    request_details_block = _extract_function_block(
        cl_main, "qboolean CL_Steam_RequestServerDetails( unsigned int serverIp, unsigned short serverPort )"
    )
    refresh_list_block = _extract_function_block(cl_main, "qboolean CL_Steam_RefreshServerList( void )")
    browser_frame_block = _extract_function_block(cl_main, "static void CL_SteamBrowser_Frame( void )")
    publish_server_failed_block = _extract_function_block(
        cl_main, "static void CL_SteamBrowser_PublishServerFailed( int serverIndex )"
    )
    publish_rules_failed_block = _extract_function_block(
        cl_main,
        "static void CL_SteamBrowser_PublishRulesFailed( const char *detailId, uint32_t serverIp, uint16_t serverPort )",
    )
    publish_players_failed_block = _extract_function_block(
        cl_main,
        "static void CL_SteamBrowser_PublishPlayersFailed( const char *detailId, uint32_t serverIp, uint16_t serverPort )",
    )
    fail_detail_request_block = _extract_function_block(
        cl_main, "static void CL_SteamBrowser_FailDetailRequest( void )"
    )
    publish_refresh_end_block = _extract_function_block(cl_main, "static void CL_SteamBrowser_PublishRefreshEnd( void )")
    publish_server_block = _extract_function_block(
        cl_main,
        "static void CL_SteamBrowser_PublishServerResponse( const netadr_t *address, uint32_t serverIp, uint16_t serverPort, const char *infoString, int ping )",
    )
    server_info_packet_block = _extract_function_block(cl_main, "void CL_ServerInfoPacket( netadr_t from, msg_t *msg ) {")
    server_status_response_block = _extract_function_block(
        cl_main, "void CL_ServerStatusResponse( netadr_t from, msg_t *msg ) {"
    )

    assert "qboolean CL_Steam_RequestServers( int requestMode );" in client_h
    assert "qboolean CL_Steam_RequestServerDetails( unsigned int serverIp, unsigned short serverPort );" in client_h
    assert "qboolean CL_Steam_RefreshServerList( void );" in client_h

    assert "case 0:" in request_mode_block
    assert "return AS_GLOBAL;" in request_mode_block
    assert "case 1:" in request_mode_block
    assert "return AS_LOCAL;" in request_mode_block
    assert "case 3:" in request_mode_block
    assert "return AS_FAVORITES;" in request_mode_block
    assert '"%u.%u.%u.%u:%i"' in build_address_block
    assert "(int)(short)serverPort" in build_address_block
    assert '"%u_%i"' in format_detail_id_block
    assert "(int)(short)serverPort" in format_detail_id_block

    assert "CL_SteamBrowser_RequestModeToSource( requestMode )" in request_servers_block
    assert "cl_steamBrowserState.requestInitialised = qtrue;" in request_servers_block
    assert "CL_SteamBrowser_MarkServerVisible( source, -1, qtrue );" in request_servers_block
    assert "CL_SteamBrowser_ResetPings( source );" in request_servers_block
    assert 'CL_Steam_PublishBrowserEvent( "servers.refresh.start", NULL );' in request_servers_block
    assert "CL_RequestLocalServers();" in request_servers_block
    assert 'CL_RequestGlobalServers( masterNum, debugProtocol, "full empty" );' in request_servers_block
    assert 'CL_RequestGlobalServers( masterNum, va( "%d", protocol ), "full empty" );' in request_servers_block
    assert 'Cbuf_ExecuteText( EXEC_NOW, "localservers\\n" );' not in request_servers_block
    assert 'Cbuf_ExecuteText( EXEC_NOW, va( "globalservers %d %s full empty\\n", masterNum, debugProtocol ) );' not in request_servers_block
    assert 'Cbuf_ExecuteText( EXEC_NOW, va( "globalservers %d %d full empty\\n", masterNum, protocol ) );' not in request_servers_block

    assert "CL_SteamBrowser_BuildAddressString( (uint32_t)serverIp, (uint16_t)serverPort, addressString, sizeof( addressString ) );" in request_details_block
    assert "CL_SteamBrowser_BeginDetailRequest( (uint32_t)serverIp, (uint16_t)serverPort, &address );" in request_details_block
    assert "CL_ServerStatus( addressString, NULL, 0 );" in request_details_block
    assert "CL_ServerStatus( addressString, serverStatus, sizeof( serverStatus ) );" in request_details_block

    assert "if ( !cl_steamBrowserState.requestInitialised ) {" in refresh_list_block
    assert "return CL_Steam_RequestServers( cl_steamBrowserState.requestMode );" in refresh_list_block

    assert 'Com_sprintf( eventName, sizeof( eventName ), "servers.details.%i.failed", serverIndex );' in publish_server_failed_block
    assert '\\"id\\":%i' in publish_server_failed_block
    assert 'Com_sprintf( eventName, sizeof( eventName ), "servers.rules.%s.failed", detailId ? detailId : "" );' in publish_rules_failed_block
    assert '\\"id\\":\\"%s\\",\\"ip\\":%u,\\"port\\":%u' in publish_rules_failed_block
    assert 'Com_sprintf( eventName, sizeof( eventName ), "servers.players.%s.failed", detailId ? detailId : "" );' in publish_players_failed_block
    assert '\\"id\\":\\"%s\\",\\"ip\\":%u,\\"port\\":%u' in publish_players_failed_block
    assert "CL_SteamBrowser_PublishRulesFailed(" in fail_detail_request_block
    assert "CL_SteamBrowser_PublishPlayersFailed(" in fail_detail_request_block
    assert "CL_SteamBrowser_ClearDetailRequest();" in fail_detail_request_block
    assert "switch ( cl_steamBrowserState.requestSource ) {" in publish_refresh_end_block
    assert "if ( !servers[i].visible || !servers[i].adr.port || servers[i].ping != 0 ) {" in publish_refresh_end_block
    assert "CL_SteamBrowser_PublishServerFailed( i );" in publish_refresh_end_block
    assert "CL_SteamBrowser_FailDetailRequest();" in browser_frame_block
    assert "CL_UpdateVisiblePings_f( cl_steamBrowserState.requestSource )" in browser_frame_block
    assert "CL_SteamBrowser_PublishRefreshEnd();" in browser_frame_block

    assert 'Com_sprintf( responseId, sizeof( responseId ), "%u_%u", (unsigned int)serverIp, (unsigned int)serverPort );' in publish_server_block
    assert 'Com_sprintf( eventName, sizeof( eventName ), "servers.details.%s.response", responseId );' in publish_server_block
    assert '\\"id\\":\\"%s\\"' in publish_server_block
    assert 'Info_ValueForKey( infoString, "sv_keywords" )' in publish_server_block
    assert 'Info_ValueForKey( infoString, "g_needpass" )' in publish_server_block
    assert 'Info_ValueForKey( infoString, "steamid" )' in publish_server_block
    assert '\\"lastPlayed\\":0' in publish_server_block

    assert "CL_SteamBrowser_PublishServerResponse(" in server_info_packet_block
    assert "CL_SteamBrowser_PackAddressIP( &from )" in server_info_packet_block

    assert "publishBrowserDetails = CL_SteamBrowser_DetailMatchesAddress( &from );" in server_status_response_block
    assert "CL_SteamBrowser_PublishRulesFromInfoString(" in server_status_response_block
    assert "CL_SteamBrowser_PublishPlayerResponse(" in server_status_response_block
    assert "CL_SteamBrowser_PublishPlayersEnd( cl_steamBrowserState.detailId );" in server_status_response_block


def test_client_web_host_exports_label_online_service_social_and_ugc_boundaries() -> None:
    cl_cgame = (REPO_ROOT / "src/code/client/cl_cgame.c").read_text(encoding="utf-8")

    web_mode_block = _extract_function_block(cl_cgame, "static const char *CL_GetWebHostModeLabel( void )")
    web_policy_block = _extract_function_block(cl_cgame, "static const char *CL_GetWebHostPolicyLabel( void )")
    matchmaking_descriptor_block = _extract_function_block(
        cl_cgame, "static const ql_platform_feature_descriptor *CL_GetWebHostMatchmakingServiceDescriptor( void )"
    )
    matchmaking_provider_block = _extract_function_block(
        cl_cgame, "static const char *CL_GetWebHostMatchmakingProviderLabel( void )"
    )
    matchmaking_policy_block = _extract_function_block(
        cl_cgame, "static const char *CL_GetWebHostMatchmakingPolicyLabel( void )"
    )
    workshop_descriptor_block = _extract_function_block(
        cl_cgame, "static const ql_platform_feature_descriptor *CL_GetWebHostWorkshopServiceDescriptor( void )"
    )
    workshop_provider_block = _extract_function_block(
        cl_cgame, "static const char *CL_GetWebHostWorkshopProviderLabel( void )"
    )
    workshop_policy_block = _extract_function_block(
        cl_cgame, "static const char *CL_GetWebHostWorkshopPolicyLabel( void )"
    )
    matchmaking_log_block = _extract_function_block(
        cl_cgame, "static void CL_LogWebHostMatchmakingExportLifecycle( const char *stage, const char *reason )"
    )
    workshop_log_block = _extract_function_block(
        cl_cgame, "static void CL_LogWebHostWorkshopExportLifecycle( const char *stage, const char *reason )"
    )
    steam_identity_block = _extract_function_block(cl_cgame, "static qboolean CL_WebHost_HasSteamIdentity( void )")
    friend_block = _extract_function_block(
        cl_cgame, "static void CL_WebHost_BuildFriendListJson( char *buffer, size_t bufferSize )"
    )
    config_block = _extract_function_block(
        cl_cgame, "static void CL_WebHost_BuildConfigJson( char *buffer, size_t bufferSize )"
    )
    method_block = _extract_function_block(
        cl_cgame,
        "static qboolean QLJSHandler_OnMethodCall( const char *methodName, const char **arguments, int argumentCount ) {",
    )

    assert "return QL_GetOnlineServicesModeLabel();" in web_mode_block
    assert "return QL_GetOnlineServicesPolicyLabel();" in web_policy_block
    assert "return &services->matchmaking;" in matchmaking_descriptor_block
    assert "return &services->workshop;" in workshop_descriptor_block
    assert 'return "Unavailable";' in matchmaking_provider_block
    assert 'return "Unavailable";' in workshop_provider_block
    assert "return QL_DescribePlatformFeaturePolicy( CL_GetWebHostMatchmakingServiceDescriptor() );" in matchmaking_policy_block
    assert "return QL_DescribePlatformFeaturePolicy( CL_GetWebHostWorkshopServiceDescriptor() );" in workshop_policy_block
    assert 'Com_DPrintf( "Web host matchmaking %s: %s (%s [%s])\\n",' in matchmaking_log_block
    assert "CL_GetWebHostMatchmakingProviderLabel()" in matchmaking_log_block
    assert "CL_GetWebHostMatchmakingPolicyLabel()" in matchmaking_log_block
    assert 'Com_DPrintf( "Web host workshop %s: %s (%s [%s])\\n",' in workshop_log_block
    assert "CL_GetWebHostWorkshopProviderLabel()" in workshop_log_block
    assert "CL_GetWebHostWorkshopPolicyLabel()" in workshop_log_block

    assert "if ( !CL_SteamServicesEnabled() ) {" in steam_identity_block
    assert "return QL_Steamworks_GetUserSteamID( &steamIdLow, &steamIdHigh );" in steam_identity_block
    assert friend_block.index("if ( !CL_WebHost_HasSteamIdentity() ) {") < friend_block.index(
        "friendCount = QL_Steamworks_GetFriendCount( CL_WEB_FRIEND_FLAGS );"
    )
    assert 'CL_LogWebHostMatchmakingExportLifecycle( "friend-list", "Steam social export unavailable for current compatibility lane" );' in friend_block
    assert "CL_Steam_FormatFriendSummaryJson( &summary, friendJson, sizeof( friendJson ) );" in friend_block
    assert 'Q_strcat( buffer, bufferSize, friendJson );' in friend_block
    assert '"queryPort"' not in friend_block
    assert '"gameServer"' not in friend_block

    for field in (
        "onlineServicesMode",
        "onlineServicesPolicy",
        "matchmakingProvider",
        "matchmakingPolicy",
        "workshopProvider",
        "workshopPolicy",
    ):
        assert f'\\"{field}\\":\\"' in config_block

    assert "onlineServicesMode = CL_GetWebHostModeLabel();" in config_block
    assert "onlineServicesPolicy = CL_GetWebHostPolicyLabel();" in config_block
    assert "matchmakingProvider = CL_GetWebHostMatchmakingProviderLabel();" in config_block
    assert "matchmakingPolicy = CL_GetWebHostMatchmakingPolicyLabel();" in config_block
    assert "workshopProvider = CL_GetWebHostWorkshopProviderLabel();" in config_block
    assert "workshopPolicy = CL_GetWebHostWorkshopPolicyLabel();" in config_block
    assert "CL_WebHost_AppendJsonEscaped( buffer, bufferSize, onlineServicesMode );" in config_block
    assert "CL_WebHost_AppendJsonEscaped( buffer, bufferSize, workshopPolicy );" in config_block

    assert "char ugcFailure[512];" not in method_block
    assert 'CL_WebView_PublishEvent( "web.ugc.failed", ugcFailure );' not in method_block
    assert 'CL_WebView_PublishEvent( "web.ugc.failed", "{\\"result\\":0}" );' not in method_block


def test_client_browser_event_publication_hooks_reconstruct_runtime_owner() -> None:
    cl_main = (REPO_ROOT / "src/code/client/cl_main.c").read_text(encoding="utf-8")
    cl_cgame = (REPO_ROOT / "src/code/client/cl_cgame.c").read_text(encoding="utf-8")

    micro_callback_log_block = _extract_function_block(
        cl_main,
        "static void CL_LogMicroTransactionCallbackLifecycle( const ql_steam_microtxn_authorization_response_t *event ) {",
    )
    browser_event_log_block = _extract_function_block(
        cl_main,
        "static void CL_LogBrowserEventLifecycle( const char *eventName, const char *reason ) {",
    )
    publish_event_block = _extract_function_block(cl_main, "void CL_WebView_PublishEvent( const char *name, const char *payload ) {")
    micro_callback_block = _extract_function_block(
        cl_main,
        "static void CL_Steam_Micro_OnAuthorizationResponse( void *context, const ql_steam_microtxn_authorization_response_t *event ) {",
    )
    disconnect_block = _extract_function_block(cl_main, "void CL_Disconnect( qboolean showMainMenu ) {")
    stop_record_block = _extract_function_block(cl_main, "void CL_StopRecord_f( void ) {")
    first_snapshot_block = _extract_function_block(cl_cgame, "void CL_FirstSnapshot( void )")

    assert 'Com_DPrintf( "microtxn.authorization callback: appid=%u order=%llu authorized=%d (%s [%s])\\n",' in micro_callback_log_block
    assert 'Com_DPrintf( "microtxn.authorization callback: ignored null callback payload (%s [%s])\\n",' in micro_callback_log_block
    assert "CL_GetSocialOverlayServiceProviderLabel()," in micro_callback_log_block
    assert "CL_GetSocialOverlayServicePolicyLabel()" in micro_callback_log_block
    assert 'Com_DPrintf( "%s browser event: %s (%s [%s])\\n",' in browser_event_log_block
    assert "CL_GetSocialOverlayServiceProviderLabel()," in browser_event_log_block
    assert "CL_GetSocialOverlayServicePolicyLabel()" in browser_event_log_block
    assert 'CL_LogBrowserEventLifecycle( name, "queued without live view" );' in publish_event_block
    assert 'CL_LogBrowserEventLifecycle( name, "queued without window object" );' in publish_event_block
    assert "payloadLength = (int)strlen( event->payload );" in publish_event_block
    assert 'Com_sprintf( detail, sizeof( detail ), "queued payload bytes=%d sequence=%d", payloadLength, event->sequence );' in publish_event_block
    assert "CL_LogBrowserEventLifecycle( event->name, detail );" in publish_event_block
    assert "CL_LogMicroTransactionCallbackLifecycle( NULL );" in micro_callback_block
    assert "CL_LogMicroTransactionCallbackLifecycle( event );" in micro_callback_block
    assert 'CL_Steam_PublishBrowserEvent( "microtxn.authorization", payload );' in micro_callback_block
    assert 'Com_DPrintf( "GOT MICRO RESPONSE: %s\\n", payload );' not in micro_callback_block
    assert "publishGameEnd = ( cls.state >= CA_CONNECTED || clc.demoplaying || clc.demorecording ) ? qtrue : qfalse;" in disconnect_block
    assert "QL_ClientAuth_CancelSteamTicket();" in disconnect_block
    assert "CL_WebView_PublishGameEnd();" in disconnect_block
    assert "CL_WebView_PublishGameDemo( clc.demoName, clc.demoName );" in stop_record_block
    assert "CL_WebView_PublishGameStart();" in first_snapshot_block


def test_advert_bridge_callbacks_track_retail_ui_and_cgame_state_paths() -> None:
    cl_cgame = (REPO_ROOT / "src/code/client/cl_cgame.c").read_text(encoding="utf-8")
    cl_ui = (REPO_ROOT / "src/code/client/cl_ui.c").read_text(encoding="utf-8")

    advert_log_block = _extract_function_block(
        cl_cgame, "static void CL_LogAdvertisementBridgeLifecycle( const char *stage, int cellId ) {"
    )
    init_ui_block = _extract_function_block(cl_cgame, "void CL_AdvertisementBridge_InitUI( void )")
    activate_block = _extract_function_block(cl_cgame, "void CL_AdvertisementBridge_ActivateAdvert( int cellId )")
    set_active_block = _extract_function_block(cl_cgame, "void CL_AdvertisementBridge_SetActiveAdvert( int cellId )")
    shutdown_block = _extract_function_block(cl_cgame, "static void CL_AdvertisementBridge_ShutdownCGame( void )")
    ui_import82_block = _extract_function_block(cl_ui, "static void QDECL QL_UI_trap_InitAdvertisementBridge( void )")
    ui_import84_block = _extract_function_block(cl_ui, "static void QDECL QL_UI_trap_ActivateAdvert( int cellId )")
    cg_import_block = _extract_function_block(cl_cgame, "static void QDECL QL_CG_trap_SetActiveAdvert( int cellId )")

    assert "static const char *CL_GetAdvertisementBridgeProviderLabel( void ) {" in cl_cgame
    assert "static const char *CL_GetAdvertisementBridgePolicyLabel( void ) {" in cl_cgame
    assert 'Com_DPrintf( "Advert bridge %s: cell=%d active=%d activated=%d via %s [%s]\\n",' in advert_log_block
    assert "cl_advertisementBridge.activatedAdvertCellId = cellId;" in activate_block
    assert "cl_advertisementBridge.activeAdvertCellId = cellId;" in set_active_block
    assert "if ( cellId == 0 ) {" in set_active_block
    assert "cl_advertisementBridge.activatedAdvertCellId = 0;" in set_active_block
    assert "cl_advertisementBridge.activeAdvertCellId = 0;" in shutdown_block
    assert "cl_advertisementBridge.activatedAdvertCellId = 0;" in shutdown_block
    assert "CL_RefreshOnlineServicesBridgeState();" in init_ui_block
    assert 'CL_LogAdvertisementBridgeLifecycle( "init-ui", 0 );' in init_ui_block
    assert 'CL_LogAdvertisementBridgeLifecycle( "activate", cellId );' in activate_block
    assert 'CL_LogAdvertisementBridgeLifecycle( "set-active", cellId );' in set_active_block
    assert 'CL_LogAdvertisementBridgeLifecycle( "shutdown-cgame", 0 );' in shutdown_block
    assert "CL_AdvertisementBridge_InitUI();" in ui_import82_block
    assert "CL_AdvertisementBridge_ActivateAdvert( cellId );" in ui_import84_block
    assert "CL_AdvertisementBridge_SetActiveAdvert( cellId );" in cg_import_block


def test_advert_default_shader_fallback_uses_steam_resource_cache() -> None:
    cl_cgame = (REPO_ROOT / "src/code/client/cl_cgame.c").read_text(encoding="utf-8")
    cl_ui = (REPO_ROOT / "src/code/client/cl_ui.c").read_text(encoding="utf-8")

    ui_block = _extract_function_block(cl_ui, "static qhandle_t QL_UI_RegisterDefaultAdvertCellShader( const char *defaultContent )")
    cg_block = _extract_function_block(cl_cgame, "static qhandle_t QL_CG_RegisterDefaultAdvertCellShader( const char *defaultContent )")

    assert "return CL_Steam_RegisterShader( defaultContent );" in ui_block
    assert "return CL_Steam_RegisterShader( defaultContent );" in cg_block


def test_client_overlay_commands_reconstruct_retail_steam_surface() -> None:
    cl_main = (REPO_ROOT / "src/code/client/cl_main.c").read_text(encoding="utf-8")
    steamworks = (REPO_ROOT / "src/common/platform/platform_steamworks.c").read_text(encoding="utf-8")

    parse_block = _extract_function_block(
        cl_main,
        "static qboolean CL_GetClientSteamId( int clientNum, uint32_t *steamIdLow, uint32_t *steamIdHigh )",
    )
    overlay_block = _extract_function_block(cl_main, "static void CL_Steam_OverlayCommand_f( void )")
    init_block = _extract_function_block(cl_main, "void CL_Init( void )")
    shutdown_block = _extract_function_block(cl_main, "void CL_Shutdown( void )")
    platform_block = _extract_function_block(
        steamworks,
        "qboolean QL_Steamworks_ActivateOverlayToUser( const char *dialog, uint32_t idLow, uint32_t idHigh )",
    )

    assert "static const ql_platform_feature_descriptor *CL_GetSocialOverlayServiceDescriptor( void ) {" in cl_main
    assert "static void CL_LogSocialOverlayIgnored( const char *commandName, const char *reason ) {" in cl_main
    assert 'Info_ValueForKey( info, "steamid" )' in parse_block
    assert "cl.gameState.stringOffsets[CS_PLAYERS + clientNum]" in parse_block
    assert "commandName = Cmd_Argv( 0 );" in overlay_block
    assert 'CL_LogSocialOverlayIgnored( commandName, "missing target client" );' in overlay_block
    assert 'CL_LogSocialOverlayIgnored( commandName, "social overlay provider unavailable" );' in overlay_block
    assert 'dialog = "steamid";' in overlay_block
    assert 'dialog = "friendadd";' in overlay_block
    assert 'CL_LogSocialOverlayIgnored( commandName, "unsupported social overlay verb" );' in overlay_block
    assert "CL_GetClientSteamId( clientNum, &steamIdLow, &steamIdHigh )" in overlay_block
    assert 'CL_LogSocialOverlayIgnored( commandName, "target client has no Steam identity" );' in overlay_block
    assert 'if ( !QL_Steamworks_ActivateOverlayToUser( dialog, steamIdLow, steamIdHigh ) ) {' in overlay_block
    assert 'CL_LogSocialOverlayIgnored( commandName, "overlay activation failed" );' in overlay_block
    assert 'Cmd_AddCommand ("clientviewprofile", CL_Steam_OverlayCommand_f );' in init_block
    assert 'Cmd_AddCommand ("clientfriendinvite", CL_Steam_OverlayCommand_f );' in init_block
    assert 'Cmd_RemoveCommand ("clientviewprofile");' not in shutdown_block
    assert 'Cmd_RemoveCommand ("clientfriendinvite");' not in shutdown_block
    assert "vtable[0x74 / 4]" in platform_block
    assert "QL_Steamworks_CombineIdentityWords( idLow, idHigh )" in platform_block


def test_client_voice_commands_reconstruct_retail_binding_surface() -> None:
    cl_main = (REPO_ROOT / "src/code/client/cl_main.c").read_text(encoding="utf-8")

    voice_log_block = _extract_function_block(
        cl_main, "static void CL_LogVoiceServiceFallback( const char *commandName, const char *reason ) {"
    )
    voice_transport_log_block = _extract_function_block(
        cl_main, "static void CL_LogVoiceTransportLifecycle( const char *stage, const char *reason ) {"
    )
    state_block = _extract_function_block(cl_main, "static void CL_SetLocalSpeakingState( qboolean speaking )")
    start_block = _extract_function_block(cl_main, "static void CL_VoiceStartRecording_f( void )")
    stop_block = _extract_function_block(cl_main, "static void CL_VoiceStopRecording_f( void )")
    send_block = _extract_function_block(cl_main, "static void CL_Steam_SendVoicePacket( void )")
    process_block = _extract_function_block(cl_main, "static void CL_Steam_ProcessVoicePackets( void )")
    disconnect_block = _extract_function_block(cl_main, "void CL_Disconnect( qboolean showMainMenu )")
    init_block = _extract_function_block(cl_main, "void CL_Init( void )")
    shutdown_block = _extract_function_block(cl_main, "void CL_Shutdown( void )")

    assert "static const char *CL_GetVoiceServiceModeLabel( void ) {" in cl_main
    assert "static const char *CL_GetVoiceServicePolicyLabel( void ) {" in cl_main
    assert 'Com_DPrintf( "%s voice fallback: %s (%s [%s])\\n",' in voice_log_block
    assert 'Com_DPrintf( "%s voice transport: %s (%s [%s])\\n",' in voice_transport_log_block
    assert "if ( !cgvm || cls.state != CA_ACTIVE || !cl.snap.valid ) {" in state_block
    assert "VM_Call( cgvm, CG_SET_CLIENT_SPEAKING_STATE, cl.snap.ps.clientNum, speaking ? 1 : 0 );" in state_block
    assert "if ( cl_voiceRecordingActive ) {" in start_block
    assert "cl_voiceRecordingActive = qtrue;" in start_block
    assert 'CL_LogVoiceServiceFallback( "+voice", "local speaking-state fallback active" );' in start_block
    assert "CL_SetLocalSpeakingState( qtrue );" in start_block
    assert "if ( !cl_voiceRecordingActive ) {" in stop_block
    assert "cl_voiceRecordingActive = qfalse;" in stop_block
    assert 'CL_LogVoiceServiceFallback( "-voice", "local speaking-state fallback active" );' in stop_block
    assert "CL_SetLocalSpeakingState( qfalse );" in stop_block
    assert "cl_voiceRecordingActive = qfalse;" in disconnect_block
    assert 'if ( !QL_Steamworks_SendP2PPacket( &serverId, compressedVoice, compressedBytes, 1, CL_STEAM_VOICE_CHANNEL ) ) {' in send_block
    assert 'CL_LogVoiceTransportLifecycle( "voice_send", "voice packet send failed" );' in send_block
    assert 'CL_LogVoiceTransportLifecycle( "voice_receive", "voice packet read failed" );' in process_block
    assert 'CL_LogVoiceTransportLifecycle( "voice_receive", "voice decompress failed" );' in process_block
    assert 'CL_LogVoiceTransportLifecycle( "voice_receive", detail );' in process_block
    steam_client_init_block = _extract_function_block(cl_main, "void SteamClient_Init( void ) {")
    assert 'Cmd_AddCommand ("+voice", CL_VoiceStartRecording_f );' not in init_block
    assert 'Cmd_AddCommand ("-voice", CL_VoiceStopRecording_f );' not in init_block
    assert 'Cmd_AddCommand ("+voice", CL_VoiceStartRecording_f );' in steam_client_init_block
    assert 'Cmd_AddCommand ("-voice", CL_VoiceStopRecording_f );' in steam_client_init_block
    assert 'Cmd_RemoveCommand ("+voice");' not in shutdown_block
    assert 'Cmd_RemoveCommand ("-voice");' not in shutdown_block


def test_client_lobby_bootstrap_reconstructs_retail_connect_surface() -> None:
    cl_main = (REPO_ROOT / "src/code/client/cl_main.c").read_text(encoding="utf-8")

    callback_log_block = _extract_function_block(
        cl_main, "static void CL_LogMatchmakingCallbackLifecycle( const char *stage, const char *reason ) {"
    )
    rich_presence_callback_block = _extract_function_block(
        cl_main, "static void CL_Steam_Client_OnRichPresenceJoinRequested( void *context, const ql_steam_rich_presence_join_requested_t *event )"
    )
    connect_block = _extract_function_block(cl_main, "static void CL_Steam_ConnectLobby_f( void )")
    p2p_callback_block = _extract_function_block(
        cl_main, "static void CL_Steam_Client_OnP2PSessionRequest( void *context, const ql_steam_p2p_session_request_t *event )"
    )
    server_change_callback_block = _extract_function_block(
        cl_main, "static void CL_Steam_Client_OnGameServerChangeRequested( void *context, const ql_steam_game_server_change_requested_t *event )"
    )
    lobby_created_block = _extract_function_block(
        cl_main, "static void CL_Steam_Lobby_OnLobbyCreated( void *context, const ql_steam_lobby_created_t *event )"
    )
    lobby_enter_response_message_block = _extract_function_block(
        cl_main, "static const char *CL_Steam_GetLobbyEnterResponseMessage( int response )"
    )
    lobby_data_json_block = _extract_function_block(
        cl_main, "static void CL_Steam_AppendLobbyDataJson( char *buffer, size_t bufferSize, uint32_t lobbyIdLow, uint32_t lobbyIdHigh )"
    )
    set_lobby_block = _extract_function_block(
        cl_main, "static void CL_Steam_SetCurrentLobby( uint64_t lobbyId )"
    )
    clear_lobby_block = _extract_function_block(
        cl_main, "static void CL_Steam_ClearCurrentLobby( void )"
    )
    leave_lobby_block = _extract_function_block(
        cl_main, "static void CL_Steam_LeaveCurrentLobby( void )"
    )
    lobby_enter_block = _extract_function_block(
        cl_main, "static void CL_Steam_Lobby_OnLobbyEnter( void *context, const ql_steam_lobby_enter_t *event )"
    )
    lobby_chat_update_block = _extract_function_block(
        cl_main, "static void CL_Steam_Lobby_OnLobbyChatUpdate( void *context, const ql_steam_lobby_chat_update_t *event )"
    )
    lobby_chat_message_block = _extract_function_block(
        cl_main, "static void CL_Steam_Lobby_OnLobbyChatMessage( void *context, const ql_steam_lobby_chat_message_t *event )"
    )
    lobby_data_update_block = _extract_function_block(
        cl_main, "static void CL_Steam_Lobby_OnLobbyDataUpdate( void *context, const ql_steam_lobby_data_update_t *event )"
    )
    lobby_game_created_block = _extract_function_block(
        cl_main, "static void CL_Steam_Lobby_OnLobbyGameCreated( void *context, const ql_steam_lobby_game_created_t *event )"
    )
    lobby_kicked_block = _extract_function_block(
        cl_main, "static void CL_Steam_Lobby_OnLobbyKicked( void *context, const ql_steam_lobby_kicked_t *event )"
    )
    lobby_join_requested_block = _extract_function_block(
        cl_main, "static void CL_Steam_Lobby_OnGameLobbyJoinRequested( void *context, const ql_steam_game_lobby_join_requested_t *event )"
    )
    init_block = _extract_function_block(cl_main, "void CL_Init( void )")
    shutdown_block = _extract_function_block(cl_main, "void CL_Shutdown( void )")

    assert "static const char *CL_GetMatchmakingServiceProviderLabel( void ) {" in cl_main
    assert "static const char *CL_GetMatchmakingServicePolicyLabel( void ) {" in cl_main
    assert 'Com_DPrintf( "%s callback: %s (%s [%s])\\n",' in callback_log_block
    assert 'CL_LogMatchmakingCallbackLifecycle( "rich_presence_join_requested", "ignored null callback payload" );' in rich_presence_callback_block
    assert "CL_Steam_OnRichPresenceJoinRequested( event->command );" in rich_presence_callback_block
    assert 'Cvar_Set( "lobby_autoconnect", Cmd_Argv( 1 ) );' in connect_block
    assert 'CL_LogMatchmakingServiceIgnored( "connect_lobby", "missing lobby id" );' in connect_block
    assert 'CL_LogMatchmakingServiceIgnored( "connect_lobby", "matchmaking provider unavailable" );' in connect_block
    assert 'CL_LogMatchmakingCallbackLifecycle( "p2p_session_request", "ignored null callback payload" );' in p2p_callback_block
    assert "CL_Steam_FormatSteamId( event->remoteId.value, remoteId, sizeof( remoteId ) );" in p2p_callback_block
    assert 'if ( !QL_Steamworks_AcceptP2PSession( &event->remoteId ) ) {' in p2p_callback_block
    assert 'CL_LogMatchmakingCallbackLifecycle( "p2p_session_request", detail );' in p2p_callback_block
    assert '"accept failed for %s"' in p2p_callback_block
    assert '"accepted %s"' in p2p_callback_block
    assert 'CL_LogMatchmakingCallbackLifecycle( "server_change_requested", "ignored null callback payload" );' in server_change_callback_block
    assert "CL_Steam_OnGameServerChangeRequested( event->server, event->password );" in server_change_callback_block
    assert 'CL_LogMatchmakingCallbackLifecycle( "lobby_created", "ignored null callback payload" );' in lobby_created_block
    assert 'CL_LogMatchmakingCallbackLifecycle( "lobby_created", detail );' in lobby_created_block
    assert '"error result=%d id=%s"' in lobby_created_block
    assert '"created id=%s result=%d"' in lobby_created_block
    assert 'Com_sprintf( payload, sizeof( payload ), "{\\"code\\":%d,\\"message\\":\\"Unable to create lobby\\"}", event->result );' in lobby_created_block
    assert 'QL_Steamworks_SetLobbyData( lobbyIdLow, lobbyIdHigh, "hello", "world" );' in lobby_created_block
    assert 'Com_sprintf( payload, sizeof( payload ), "{\\"id\\":\\"%s\\",\\"status\\":%d}", lobbyId, event->result );' in lobby_created_block
    assert '"Lobby does not exist"' in lobby_enter_response_message_block
    assert '"Access denied"' in lobby_enter_response_message_block
    assert '"Lobby is full"' in lobby_enter_response_message_block
    assert '"Unexpected error"' in lobby_enter_response_message_block
    assert '"You are banned from this lobby"' in lobby_enter_response_message_block
    assert '"Cannot join as a limited user"' in lobby_enter_response_message_block
    assert '"Locked to a clan you are not in"' in lobby_enter_response_message_block
    assert '"You are banned from Steam Community"' in lobby_enter_response_message_block
    assert '"You have been blocked from joining by a member"' in lobby_enter_response_message_block
    assert '"Cannot join lobby with blocked member"' in lobby_enter_response_message_block
    assert "lobbyDataCount = QL_Steamworks_GetLobbyDataCount( lobbyIdLow, lobbyIdHigh );" not in lobby_enter_block
    assert "CL_Steam_AppendLobbyDataJson( payload, sizeof( payload ), lobbyIdLow, lobbyIdHigh );" in lobby_enter_block
    assert "QL_Steamworks_GetLobbyDataCount( lobbyIdLow, lobbyIdHigh )" in lobby_data_json_block
    assert "QL_Steamworks_GetLobbyDataByIndex( lobbyIdLow, lobbyIdHigh, i, key, sizeof( key ), value, sizeof( value ) )" in lobby_data_json_block
    assert 'CL_Steam_AppendJsonFragment( buffer, bufferSize, "\\"%s\\":\\"%s\\"", escapedKey, escapedValue );' in lobby_data_json_block
    assert "currentLobbyValid" not in set_lobby_block
    assert "currentLobbyValid" not in clear_lobby_block
    assert "QL_Steamworks_LeaveLobby( lobbyIdLow, lobbyIdHigh );" in leave_lobby_block
    assert "if ( !cl_steamCallbackState.currentLobbyValid ) {" not in leave_lobby_block
    assert 'Com_sprintf( eventName, sizeof( eventName ), "lobby.%s.left", lobbyId );' in leave_lobby_block
    assert 'Com_sprintf( payload, sizeof( payload ), "{\\"id\\":\\"%s\\"}", lobbyId );' in leave_lobby_block
    assert 'CL_LogMatchmakingCallbackLifecycle( "lobby_enter", "ignored null callback payload" );' in lobby_enter_block
    assert 'CL_LogMatchmakingCallbackLifecycle( "lobby_enter", detail );' in lobby_enter_block
    assert '"enter failed response=%d permissions=%u id=%s"' in lobby_enter_block
    assert '"entered id=%s permissions=%u locked=%d"' in lobby_enter_block
    assert "responseMessage = CL_Steam_GetLobbyEnterResponseMessage( event->response );" in lobby_enter_block
    assert 'Com_sprintf( payload, sizeof( payload ), "{\\"code\\":%d,\\"id\\":\\"%s\\",\\"message\\":\\"%s\\"}", event->response, lobbyId, escapedMessage );' in lobby_enter_block
    assert "cl_steamCallbackState.currentLobbyValid" not in lobby_enter_block
    assert "if ( CL_Steam_GetCurrentLobbyIdentityWords( NULL, NULL ) ) {" in lobby_enter_block
    assert "CL_Steam_LeaveCurrentLobby();" in lobby_enter_block
    assert "QL_Steamworks_GetLobbyOwner( lobbyIdLow, lobbyIdHigh, &ownerIdLow, &ownerIdHigh )" in lobby_enter_block
    assert "QL_Steamworks_GetNumLobbyMembers( lobbyIdLow, lobbyIdHigh )" in lobby_enter_block
    assert "QL_Steamworks_GetLobbyMemberLimit( lobbyIdLow, lobbyIdHigh )" in lobby_enter_block
    assert "QL_Steamworks_GetLobbyMemberByIndex( lobbyIdLow, lobbyIdHigh, i, &memberIdLow, &memberIdHigh )" in lobby_enter_block
    assert "QL_Steamworks_GetFriendPersonaName( memberIdLow, memberIdHigh, memberName, sizeof( memberName ) )" in lobby_enter_block
    assert '"{\\"id\\":\\"%s\\",\\"is_owner\\":%s,\\"owner\\":\\"%s\\",\\"lobbydata\\":{"' in lobby_enter_block
    assert '"},\\"num_players\\":%d,\\"max_players\\":%d,\\"players\\":{"' in lobby_enter_block
    assert '"\\"%s\\":{\\"id\\":\\"%s\\",\\"name\\":\\"%s\\"}"' in lobby_enter_block
    assert 'CL_LogMatchmakingCallbackLifecycle( "lobby_chat_update", "ignored null callback payload" );' in lobby_chat_update_block
    assert 'CL_LogMatchmakingCallbackLifecycle( "lobby_chat_update", detail );' in lobby_chat_update_block
    assert '"user %s %s in lobby %s (state=%u)"' in lobby_chat_update_block
    assert "numPlayers = QL_Steamworks_GetNumLobbyMembers( lobbyIdLow, lobbyIdHigh );" in lobby_chat_update_block
    assert "maxPlayers = QL_Steamworks_GetLobbyMemberLimit( lobbyIdLow, lobbyIdHigh );" in lobby_chat_update_block
    assert 'Com_sprintf( eventName, sizeof( eventName ), "lobby.%s.user.joined", lobbyId );' in lobby_chat_update_block
    assert 'Com_sprintf( eventName, sizeof( eventName ), "lobby.%s.user.left", lobbyId );' in lobby_chat_update_block
    assert 'Com_sprintf( payload, sizeof( payload ), "{\\"id\\":\\"%s\\",\\"name\\":\\"%s\\",\\"num_players\\":%d,\\"max_players\\":%d}",' in lobby_chat_update_block
    assert 'CL_LogMatchmakingCallbackLifecycle( "lobby_chat_message", "ignored null callback payload" );' in lobby_chat_message_block
    assert 'CL_LogMatchmakingCallbackLifecycle( "lobby_chat_message", detail );' in lobby_chat_message_block
    assert '"chat from %s in lobby %s type=%d bytes=%d"' in lobby_chat_message_block
    assert 'Com_sprintf( payload, sizeof( payload ), "{\\"id\\":\\"%s\\",\\"name\\":\\"%s\\",\\"msg\\":\\"%s\\"}", userId, name, message );' in lobby_chat_message_block
    assert 'CL_LogMatchmakingCallbackLifecycle( "lobby_data_update", "ignored null callback payload" );' in lobby_data_update_block
    assert 'CL_LogMatchmakingCallbackLifecycle( "lobby_data_update", detail );' in lobby_data_update_block
    assert '"update lobby=%llu member=%llu success=%d"' in lobby_data_update_block
    assert 'CL_Steam_FormatSteamId( event->lobbyId.value, lobbyId, sizeof( lobbyId ) );' in lobby_data_update_block
    assert 'Com_sprintf( payload, sizeof( payload ), "{\\"id\\":\\"%s\\"}", lobbyId );' in lobby_data_update_block
    assert "if ( event->memberId.value == event->lobbyId.value ) {" not in lobby_data_update_block
    assert "CL_Steam_AppendLobbyDataJson( payload, sizeof( payload ), lobbyIdLow, lobbyIdHigh );" not in lobby_data_update_block
    assert 'CL_LogMatchmakingCallbackLifecycle( "lobby_game_created", "ignored null callback payload" );' in lobby_game_created_block
    assert 'CL_LogMatchmakingCallbackLifecycle( "lobby_game_created", detail );' in lobby_game_created_block
    assert '"game created lobby=%llu server=%llu ip=%u port=%u"' in lobby_game_created_block
    assert 'Com_sprintf( payload, sizeof( payload ), "{\\"ip\\":%u,\\"port\\":%u,\\"id\\":\\"%llu\\"}",' in lobby_game_created_block
    assert 'CL_LogMatchmakingCallbackLifecycle( "lobby_kicked", "ignored null callback payload" );' in lobby_kicked_block
    assert 'CL_LogMatchmakingCallbackLifecycle( "lobby_kicked", detail );' in lobby_kicked_block
    assert '"kicked lobby=%llu admin=%llu disconnected=%d"' in lobby_kicked_block
    assert 'Com_sprintf( payload, sizeof( payload ), "{\\"id\\":\\"%llu\\"}", (unsigned long long)event->lobbyId.value );' in lobby_kicked_block
    assert "CL_Steam_ClearCurrentLobby();" in lobby_kicked_block
    assert "if ( cl_steamCallbackState.currentLobbyValid && cl_steamCallbackState.currentLobbyId == event->lobbyId.value ) {" not in lobby_kicked_block
    assert lobby_kicked_block.index( "CL_Steam_PublishBrowserEvent( eventName, payload );" ) < lobby_kicked_block.index( "CL_Steam_ClearCurrentLobby();" )
    assert 'CL_LogMatchmakingCallbackLifecycle( "lobby_join_requested", "ignored null callback payload" );' in lobby_join_requested_block
    assert 'CL_LogMatchmakingCallbackLifecycle( "lobby_join_requested", detail );' in lobby_join_requested_block
    assert '"join requested lobby=%llu friend=%llu"' in lobby_join_requested_block
    assert 'Com_sprintf( payload, sizeof( payload ), "{\\"id\\":\\"%llu\\"}", (unsigned long long)event->lobbyId.value );' in lobby_join_requested_block
    lobby_init_block = _extract_function_block(cl_main, "static qboolean SteamLobby_Init( void ) {")

    assert 'Cvar_Get( "lobby_autoconnect", "", CVAR_TEMP );' not in init_block
    assert 'Cvar_Get( "steam_maxLobbyClients", "16", CVAR_ARCHIVE );' not in init_block
    assert 'Cmd_AddCommand ("connect_lobby", CL_Steam_ConnectLobby_f );' not in init_block
    assert 'Cvar_Get( "lobby_autoconnect", "", CVAR_TEMP );' in lobby_init_block
    assert 'Cvar_Get( "steam_maxLobbyClients", "16", CVAR_ARCHIVE );' in lobby_init_block
    assert 'Cmd_AddCommand ("connect_lobby", CL_Steam_ConnectLobby_f );' in lobby_init_block
    assert 'Cmd_RemoveCommand ("connect_lobby");' not in shutdown_block


def test_client_rich_presence_join_and_server_change_reconstruct_retail_connect_handoff() -> None:
    cl_main = (REPO_ROOT / "src/code/client/cl_main.c").read_text(encoding="utf-8")

    callback_log_block = _extract_function_block(
        cl_main, "static void CL_LogMatchmakingCallbackLifecycle( const char *stage, const char *reason ) {"
    )
    execute_block = _extract_function_block(cl_main, "static void CL_Steam_ExecuteImmediateCommand( const char *command )")
    join_block = _extract_function_block(cl_main, "void CL_Steam_OnRichPresenceJoinRequested( const char *command )")
    server_change_block = _extract_function_block(
        cl_main,
        "void CL_Steam_OnGameServerChangeRequested( const char *server, const char *password )",
    )

    assert 'Com_DPrintf( "%s callback: %s (%s [%s])\\n",' in callback_log_block
    assert "Cbuf_ExecuteText( EXEC_NOW, command );" in execute_block
    assert 'CL_LogMatchmakingCallbackLifecycle( "rich_presence_join_requested", "missing join command" );' in join_block
    assert 'CL_LogMatchmakingCallbackLifecycle( "rich_presence_join_requested", "executing immediate join command" );' in join_block
    assert "CL_Steam_ExecuteImmediateCommand( command );" in join_block
    assert 'CL_LogMatchmakingCallbackLifecycle( "server_change_requested", "missing server target" );' in server_change_block
    assert 'Com_sprintf( detail, sizeof( detail ), "connecting to requested server (password=%d)",' in server_change_block
    assert 'CL_LogMatchmakingCallbackLifecycle( "server_change_requested", detail );' in server_change_block
    assert "if ( password && password[0] ) {" in server_change_block
    assert 'Cvar_Set( "password", password );' in server_change_block
    assert 'CL_Steam_ExecuteImmediateCommand( va( "connect %s\\n", server ) );' in server_change_block


def test_client_stats_callback_lane_stays_explicit() -> None:
    cl_main = (REPO_ROOT / "src/code/client/cl_main.c").read_text(encoding="utf-8")

    callback_log_block = _extract_function_block(
        cl_main, "static void CL_LogStatsCallbackLifecycle( const char *stage, const char *reason ) {"
    )
    stats_json_block = _extract_function_block(
        cl_main, "static void CL_Steam_AppendUserStatsJson( uint32_t idLow, uint32_t idHigh, int result, char *buffer, size_t bufferSize )"
    )
    achievement_json_block = _extract_function_block(
        cl_main, "static void CL_Steam_AppendUserAchievementsJson( uint32_t idLow, uint32_t idHigh, int result, char *buffer, size_t bufferSize )"
    )
    callback_block = _extract_function_block(
        cl_main, "static void CL_Steam_Client_OnUserStatsReceived( void *context, const ql_steam_user_stats_received_t *event )"
    )

    assert 'Com_DPrintf( "%s callback: %s (%s [%s])\\n",' in callback_log_block
    assert "CL_GetStatsServiceProviderLabel()," in callback_log_block
    assert "CL_GetStatsServicePolicyLabel()" in callback_log_block
    assert "#define CL_STEAM_BROWSER_EVENT_PAYLOAD_LENGTH 65536" in cl_main
    assert "#define CL_STEAM_STATS_FIELD_COUNT 88" in cl_main
    assert "#define CL_STEAM_ACHIEVEMENT_COUNT 59" in cl_main
    assert 'static const char *s_clSteamStatNames[CL_STEAM_STATS_FIELD_COUNT] = {' in cl_main
    assert 'static const char *s_clSteamAchievementNames[CL_STEAM_ACHIEVEMENT_COUNT] = {' in cl_main
    assert 'CL_Steam_AppendJsonFragment( buffer, bufferSize, "\\"STATS\\":{" );' in stats_json_block
    assert 'QL_Steamworks_GetUserStatInt( idLow, idHigh, name, &value );' in stats_json_block
    assert '"%s\\"%s\\":%d"' in stats_json_block
    assert 'CL_Steam_AppendJsonFragment( buffer, bufferSize, "\\"ACHIEVEMENTS\\":{" );' in achievement_json_block
    assert 'QL_Steamworks_GetAchievementDisplayAttribute( name, "name" );' in achievement_json_block
    assert 'QL_Steamworks_GetAchievementDisplayAttribute( name, "desc" );' in achievement_json_block
    assert 'QL_Steamworks_GetUserAchievement( idLow, idHigh, name, &unlocked, &unlockTime );' in achievement_json_block
    assert 'CL_Steam_AppendJsonFragment( buffer, bufferSize, "\\"ID\\":\\"%s\\","' in achievement_json_block
    assert 'CL_Steam_AppendJsonFragment( buffer, bufferSize, "\\"NAME\\":\\"%s\\","' in achievement_json_block
    assert 'CL_Steam_AppendJsonFragment( buffer, bufferSize, "\\"DESC\\":\\"%s\\","' in achievement_json_block
    assert 'CL_Steam_AppendJsonFragment( buffer, bufferSize, "\\"TIME_UNLOCKED\\":%d}", unlockTime );' in achievement_json_block
    assert 'CL_LogStatsCallbackLifecycle( "user_stats_received", "ignored null callback payload" );' in callback_block
    assert 'Com_sprintf( detail, sizeof( detail ), "user stats received for %s game=%u result=%d",' in callback_block
    assert 'CL_LogStatsCallbackLifecycle( "user_stats_received", detail );' in callback_block
    assert 'Com_sprintf( eventName, sizeof( eventName ), "users.stats.%s.received", steamId );' in callback_block
    assert 'if ( !QL_Steamworks_GetFriendPersonaName( steamIdLow, steamIdHigh, rawName, sizeof( rawName ) ) ) {' in callback_block
    assert 'Q_strncpyz( rawName, event->name, sizeof( rawName ) );' in callback_block
    assert 'CL_Steam_AppendJsonFragment( payload, sizeof( payload ), "{\\"ID\\":\\"%s\\",\\"NAME\\":\\"%s\\","' in callback_block
    assert "CL_Steam_AppendUserStatsJson( steamIdLow, steamIdHigh, event->result, payload, sizeof( payload ) );" in callback_block
    assert "CL_Steam_AppendUserAchievementsJson( steamIdLow, steamIdHigh, event->result, payload, sizeof( payload ) );" in callback_block
    assert '"{\\"id\\":\\"%s\\"' not in callback_block
    assert 'CL_Steam_PublishBrowserEvent( eventName, payload );' in callback_block


def test_client_social_presence_and_ugc_callback_lanes_stay_explicit() -> None:
    cl_main = (REPO_ROOT / "src/code/client/cl_main.c").read_text(encoding="utf-8")
    steamworks = (REPO_ROOT / "src/common/platform/platform_steamworks.c").read_text(encoding="utf-8")

    format_game_block = _extract_function_block(
        cl_main, "static void CL_Steam_FormatFriendGameJson( const ql_steam_friend_summary_t *summary, char *buffer, size_t bufferSize )"
    )
    format_presence_block = _extract_function_block(
        cl_main, "static void CL_Steam_FormatFriendPresenceJson( const ql_steam_friend_summary_t *summary, char *buffer, size_t bufferSize )"
    )
    format_persona_block = _extract_function_block(
        cl_main, "static void CL_Steam_FormatPersonaChangeJson( const ql_steam_persona_state_change_t *event, char *buffer, size_t bufferSize )"
    )
    format_summary_block = _extract_function_block(
        cl_main, "void CL_Steam_FormatFriendSummaryJson( const ql_steam_friend_summary_t *summary, char *buffer, size_t bufferSize ) {"
    )
    ugc_results_block = _extract_function_block(
        cl_main, "static void CL_Steam_BuildUGCQueryResultsJson( uint64_t queryHandle, uint32_t numResultsReturned, char *buffer, size_t bufferSize )"
    )
    persona_block = _extract_function_block(
        cl_main, "static void CL_Steam_Client_OnPersonaStateChange( void *context, const ql_steam_persona_state_change_t *event )"
    )
    presence_block = _extract_function_block(
        cl_main, "static void CL_Steam_Client_OnFriendRichPresenceUpdate( void *context, const ql_steam_friend_rich_presence_update_t *event )"
    )
    ugc_block = _extract_function_block(
        cl_main, "static void CL_Steam_Client_OnUGCQueryCompleted( void *context, const ql_steam_ugc_query_completed_t *event )"
    )
    friend_summary_block = _extract_function_block(
        steamworks, "qboolean QL_Steamworks_GetFriendSummary( uint32_t idLow, uint32_t idHigh, ql_steam_friend_summary_t *outSummary )"
    )

    assert 'Q_strncpyz( buffer, "null", bufferSize );' in format_game_block
    assert '"{\\"lobby\\":\\"%s\\",\\"appid\\":%u,\\"ip\\":%u,\\"port\\":%u,\\"queryport\\":%u}"' in format_game_block
    assert "summary->appId," in format_game_block
    assert '"{\\"id\\":\\"%s\\",\\"status\\":\\"%s\\",\\"lanIp\\":\\"%s\\"}"' in format_presence_block
    assert "CL_Steam_FormatFriendSummaryJson( &event->summary, friendSummary, sizeof( friendSummary ) );" in format_persona_block
    assert '"{\\"id\\":\\"%s\\",\\"state\\":%u,\\"friend\\":%s}"' in format_persona_block
    assert '"{\\"id\\":\\"%s\\",\\"name\\":\\"%s\\",\\"state\\":%d,\\"relationship\\":%d,\\"nickname\\":\\"%s\\",\\"status\\":\\"%s\\",\\"lanIp\\":\\"%s\\",\\"playingQuake\\":%d,\\"game\\":%s}"' in format_summary_block
    assert "CL_Steam_FormatFriendGameJson( summary, game, sizeof( game ) );" in format_summary_block
    assert '"server"' not in format_summary_block
    assert "QL_Steamworks_GetQueryUGCResult( queryHandle, i, &publishedFileId, title, sizeof( title ), description, sizeof( description ) )" in ugc_results_block
    assert "QL_Steamworks_GetQueryUGCPreviewURL( queryHandle, i, image, sizeof( image ) )" in ugc_results_block
    assert 'CL_Steam_AppendJsonFragment(' in ugc_results_block
    assert '"%s{\\"title\\":\\"%s\\",\\"description\\":\\"%s\\",\\"id\\":\\"%s\\",\\"image\\":\\"%s\\"}"' in ugc_results_block
    assert 'outSummary->appId = (uint32_t)( gameInfo.gameId & 0x00ffffffull );' in friend_summary_block
    assert "if ( currentAppId != 0u && outSummary->appId == currentAppId ) {" in friend_summary_block
    assert 'CL_LogMatchmakingCallbackLifecycle( "persona_state_change", "ignored null callback payload" );' in persona_block
    assert 'CL_LogMatchmakingCallbackLifecycle( "persona_state_change", detail );' in persona_block
    assert '"persona changed for %s flags=%u"' in persona_block
    assert 'if ( ( event->changeFlags & 1u ) != 0 &&' in persona_block
    assert "QL_Steamworks_GetUserSteamID( &localIdLow, &localIdHigh )" in persona_block
    assert "SteamClient_SyncPersonaNameCvar();" in persona_block
    assert 'Com_sprintf( eventName, sizeof( eventName ), "users.persona.%s.change", steamId );' in persona_block
    assert "CL_Steam_FormatPersonaChangeJson( event, payload, sizeof( payload ) );" in persona_block
    assert '"changeFlags"' not in persona_block
    assert 'CL_LogMatchmakingCallbackLifecycle( "friend_rich_presence_update", "ignored null callback payload" );' in presence_block
    assert 'CL_LogMatchmakingCallbackLifecycle( "friend_rich_presence_update", detail );' in presence_block
    assert '"rich presence updated for %s app=%u"' in presence_block
    assert 'Com_sprintf( eventName, sizeof( eventName ), "users.presence.%s.change", steamId );' in presence_block
    assert 'CL_Steam_FormatFriendPresenceJson( &event->summary, summary, sizeof( summary ) );' in presence_block
    assert 'Com_sprintf( payload, sizeof( payload ), "%s", summary );' in presence_block
    assert '"appId"' not in presence_block
    assert '"friend"' not in presence_block
    assert 'CL_LogWorkshopLifecycle( "callback-ugc-query", "ignored null callback payload" );' in ugc_block
    assert 'CL_LogWorkshopLifecycle( "callback-ugc-query", detail );' in ugc_block
    assert '"query completed call=%llu query=%llu result=%d count=%u total=%u cached=%d"' in ugc_block
    assert "CL_Steam_BuildUGCQueryResultsJson( event->queryHandle, event->numResultsReturned, payload, sizeof( payload ) );" in ugc_block
    assert 'CL_Steam_PublishBrowserEvent( "web.ugc.results", payload );' in ugc_block
    assert 'CL_Steam_PublishBrowserEvent( "web.ugc.failed", NULL );' in ugc_block
    assert "QL_Steamworks_ReleaseQueryUGCRequest( event->queryHandle );" in ugc_block


def test_client_workshop_callback_lanes_stay_explicit() -> None:
    cl_main = (REPO_ROOT / "src/code/client/cl_main.c").read_text(encoding="utf-8")

    item_installed_block = _extract_function_block(
        cl_main, "static void CL_Steam_Workshop_OnItemInstalled( void *context, const ql_steam_item_installed_t *event )"
    )
    download_result_block = _extract_function_block(
        cl_main, "static void CL_Steam_Workshop_OnDownloadItemResult( void *context, const ql_steam_download_item_result_t *event )"
    )

    assert 'CL_LogWorkshopLifecycle( "callback-item-installed", detail );' in item_installed_block
    assert 'CL_LogWorkshopLifecycle( "callback-item-installed", "ignored null callback payload" );' in item_installed_block
    assert 'CL_LogWorkshopLifecycle( "callback-item-installed", "ignored installed callback without active download state" );' in item_installed_block
    assert '"OnDownloadItemResult skip, invalid app id %d"' in item_installed_block
    assert '"ignored installed callback for untracked item %llu"' in item_installed_block
    assert '"installed item %llu request=%d"' in item_installed_block
    assert "CL_Workshop_FinalizeInstalledItem( itemIndex );" in item_installed_block
    assert 'CL_LogWorkshopLifecycle( "callback-download-result", detail );' in download_result_block
    assert 'CL_LogWorkshopLifecycle( "callback-download-result", "ignored null callback payload" );' in download_result_block
    assert 'CL_LogWorkshopLifecycle( "callback-download-result", "ignored download callback without active download state" );' in download_result_block
    assert 'CL_LogWorkshopLifecycle( "callback-download-result", "ignored download callback without active item index" );' in download_result_block
    assert '"OnDownloadItemResult skip, invalid app id %d"' in download_result_block
    assert '"OnDownloadItemResult skip, not the active download %llu"' in download_result_block
    assert '"Download item %llu failed with EResult code %i"' in download_result_block
    assert 'CL_Workshop_FinalizeInstalledItem( cl_steamWorkshopDownloadState.activeItemIndex );' in download_result_block
    assert "CL_Workshop_FailActiveDownload();" in download_result_block
    assert "CL_Workshop_AdvanceDownloadQueue();" not in download_result_block


def test_client_workshop_required_items_bootstrap_lane_stays_explicit() -> None:
    cl_main = (REPO_ROOT / "src/code/client/cl_main.c").read_text(encoding="utf-8")

    bootstrap_block = _extract_function_block(cl_main, "static qboolean CL_Workshop_BeginBootstrap( void )")
    set_request_cvars_block = _extract_function_block(cl_main, "static void CL_Workshop_SetDownloadRequestCvars( int itemIndex )")
    set_active_item_block = _extract_function_block(cl_main, "static void CL_Workshop_SetActiveItem( int itemIndex )")
    clear_active_download_block = _extract_function_block(cl_main, "static void CL_Workshop_ClearActiveDownload( void )")
    request_download_block = _extract_function_block(cl_main, "static qboolean CL_Workshop_RequestDownload( int itemIndex )")
    advance_queue_block = _extract_function_block(cl_main, "static qboolean CL_Workshop_AdvanceDownloadQueue( void )")
    finalize_item_block = _extract_function_block(cl_main, "static qboolean CL_Workshop_FinalizeInstalledItem( int itemIndex )")
    fail_block = _extract_function_block(cl_main, "static qboolean CL_Workshop_FailActiveDownload( void )")
    downloads_settled_block = _extract_function_block(cl_main, "static qboolean CL_Workshop_DownloadsSettled( void )")

    assert "qboolean\tqueued;" in cl_main
    assert 'Com_Printf( "Server requires the following workshop items: %s\\n", workshopItems );' in bootstrap_block
    assert "workshopProvider = CL_GetWorkshopServiceProviderLabel();" not in bootstrap_block
    assert "workshopPolicy = CL_GetWorkshopServicePolicyLabel();" not in bootstrap_block
    assert 'CL_LogWorkshopLifecycle( "bootstrap-unavailable", "required items unavailable; keeping compatibility-only fallback" );' in bootstrap_block
    assert 'Com_sprintf( detail, sizeof( detail ), "server requires %i workshop item(s)", totalItems );' in bootstrap_block
    assert 'CL_LogWorkshopLifecycle( "bootstrap-begin", detail );' in bootstrap_block
    assert '"Workshop item %llu: queueing download."' not in bootstrap_block
    assert 'if ( CL_Workshop_RequestDownload( itemIndex ) ) {' in bootstrap_block
    assert "item->requestNumber = ++requestNumber;" in bootstrap_block
    assert 'cl_steamWorkshopDownloadState.downloadsRequested = qtrue;' in bootstrap_block
    assert "CL_Workshop_SetDownloadRequestCvars( itemIndex );" in bootstrap_block
    assert 'Cvar_Set( "cl_downloadItem", itemString );' in set_request_cvars_block
    assert 'Cvar_Set( "cl_downloadName", downloadName );' in set_request_cvars_block
    assert 'Cvar_SetValue( "cl_downloadTime", cls.realtime );' in set_request_cvars_block
    assert 'Cvar_Set( "cl_downloadItem", itemString );' not in set_active_item_block
    assert 'Cvar_Set( "cl_downloadName", downloadName );' not in set_active_item_block
    assert 'Cvar_SetValue( "cl_downloadTime", cls.realtime );' not in set_active_item_block
    assert "CL_Workshop_UpdateProgressCvars();" not in set_active_item_block
    assert "CL_Workshop_UpdateProgressCvars();" not in clear_active_download_block
    assert '"Workshop item %llu: in cache."' in request_download_block
    assert "CL_Workshop_FinalizeInstalledItem( itemIndex );" in request_download_block
    assert '"Workshop item %llu: requesting download."' in request_download_block
    assert '"Workshop item %llu: queueing download."' in request_download_block
    assert '"Workshop item %llu: was queued, requesting download."' not in request_download_block
    assert '"download request failed"' not in request_download_block
    assert "cl_steamWorkshopDownloadState.queueActive = qtrue;" in request_download_block
    assert "item->queued = qtrue;" in request_download_block
    assert '"Workshop item %llu: was queued, requesting download."' in advance_queue_block
    assert "CL_Workshop_ClearActiveDownload();" in advance_queue_block
    assert "if ( item->completed || !item->queued ) {" in advance_queue_block
    assert "item->queued = qfalse;" in advance_queue_block
    assert "CL_Workshop_SetActiveItem( i );" in advance_queue_block
    assert "QL_Steamworks_DownloadItem( item->itemIdLow, item->itemIdHigh, qtrue );" in advance_queue_block
    assert '"Steamworks download complete: %llu"' in finalize_item_block
    assert "CL_Workshop_ClearActiveDownload();" not in finalize_item_block
    assert "return CL_Workshop_AdvanceDownloadQueue();" in finalize_item_block
    assert 'CL_LogWorkshopLifecycle( "item-failed", detail );' not in fail_block
    assert "return CL_Workshop_AdvanceDownloadQueue();" in fail_block
    assert 'if ( CL_Workshop_FinalizeInstalledItem( cl_steamWorkshopDownloadState.activeItemIndex ) ) {' in downloads_settled_block
    assert 'if ( CL_Workshop_AdvanceDownloadQueue() ) {' in downloads_settled_block
    assert 'CL_LogWorkshopLifecycle( "queue-complete", "Download completed for all steamworks items" );' in downloads_settled_block


def test_client_workshop_frame_reuses_retail_completion_strings() -> None:
    cl_main = (REPO_ROOT / "src/code/client/cl_main.c").read_text(encoding="utf-8")

    frame_block = _extract_function_block(cl_main, "static void CL_Workshop_Frame( void )")

    assert 'Com_Printf( "Steamworks downloads complete - FS restart is required\\n" );' in frame_block
    assert 'CL_LogWorkshopLifecycle( "filesystem-restart", "downloads complete; restarting filesystem" );' not in frame_block
    assert 'Com_Printf( "Steamworks downloads complete\\n" );' in frame_block
    assert 'Com_Printf( "WARNING: Missing pk3s referenced by the server:\\n%s\\n"' in frame_block
    assert '"The server will most likely refuse the connection.\\n", missingfiles );' in frame_block
    assert '"WARNING: You are missing some files referenced by the server:\\n%s"' not in frame_block
    assert '"You might not be able to join the game\\n"' not in frame_block
    assert "FS_Restart( clc.checksumFeed );" in frame_block
    assert "cl_steamWorkshopDownloadState.active = qfalse;" in frame_block
    assert "CL_Workshop_ClearBootstrapState( qtrue );" not in frame_block
    assert "CL_DownloadsComplete();" in frame_block


def test_recovered_ui_workshop_progress_bridge_uses_item_id_and_native_download_info() -> None:
    ui_reconstruction = (
        REPO_ROOT
        / "references"
        / "reverse-engineering"
        / "ghidra"
        / "uix86"
        / "source-recreation"
        / "ui_reconstruction.c"
    ).read_text(encoding="cp1252")

    bridge_start = ui_reconstruction.index('(**(code **)(DAT_106b40a8 + 0x24))("cl_downloadItem",local_d0,0x40);')
    bridge_block = ui_reconstruction[bridge_start:bridge_start + 320]

    assert 'sscanf(local_d0,"%llu",&uStack_158);' in bridge_block
    assert '(**(code **)(DAT_106b40a8 + 0x180))(uStack_158,uStack_154,&uStack_168,&uStack_170);' in bridge_block
    assert '(**(code **)(DAT_106b40a8 + 0x28))("cl_downloadTime");' in bridge_block
    assert "cl_downloadCount" not in bridge_block
    assert "cl_downloadSize" not in bridge_block


def test_client_main_menu_presence_seed_reconstructs_retail_bootstrap_status() -> None:
    client_h = (REPO_ROOT / "src/code/client/client.h").read_text(encoding="utf-8")
    cl_main = (REPO_ROOT / "src/code/client/cl_main.c").read_text(encoding="utf-8")
    steamworks = (REPO_ROOT / "src/common/platform/platform_steamworks.c").read_text(encoding="utf-8")

    presence_block = _extract_function_block(cl_main, "static void CL_Steam_SetMainMenuRichPresence( void )")
    init_block = _extract_function_block(cl_main, "void CL_Init( void )")
    platform_block = _extract_function_block(
        steamworks,
        "qboolean QL_Steamworks_SetRichPresence( const char *key, const char *value )",
    )

    assert "void CL_LogMatchmakingServiceIgnored( const char *commandName, const char *reason );" in client_h
    assert 'CL_LogMatchmakingServiceIgnored( "steam_presence_main_menu", "matchmaking provider unavailable" );' in presence_block
    assert 'if ( !QL_Steamworks_SetRichPresence( "status", "At the main menu" ) ) {' in presence_block
    assert 'CL_LogMatchmakingServiceIgnored( "steam_presence_main_menu", "rich presence update failed" );' in presence_block
    steam_client_init_block = _extract_function_block(cl_main, "void SteamClient_Init( void ) {")
    assert "CL_Steam_SetMainMenuRichPresence();" not in init_block
    assert "CL_Steam_SetMainMenuRichPresence();" in steam_client_init_block
    assert "vtable[0xac / 4]" in platform_block
    assert "return fn( friends, NULL, key, value ) ? qtrue : qfalse;" in platform_block


def test_client_identity_bootstrap_and_ui_subscription_lanes_stay_explicit() -> None:
    cl_main = (REPO_ROOT / "src/code/client/cl_main.c").read_text(encoding="utf-8")
    cl_ui = (REPO_ROOT / "src/code/client/cl_ui.c").read_text(encoding="utf-8")

    identity_log_block = _extract_function_block(
        cl_main, "static void CL_LogIdentityBootstrapFallback( const char *stage, const char *reason ) {"
    )
    init_block = _extract_function_block(cl_main, "void CL_Init( void )")
    persona_block = _extract_function_block(cl_main, "static void SteamClient_SyncPersonaNameCvar( void ) {")
    country_block = _extract_function_block(cl_main, "static void CL_Steam_SeedCountryCvar( void )")
    subscribed_block = _extract_function_block(cl_ui, "static int QDECL QL_UI_trap_IsSubscribedApp( int arg1 )")
    subscription_log_block = _extract_function_block(
        cl_ui, "static void QL_UI_LogSubscriptionBridgeIgnored( int appId, const char *reason ) {"
    )

    assert "static const char *CL_GetIdentityBootstrapModeLabel( void ) {" in cl_main
    assert "static const char *CL_GetIdentityBootstrapPolicyLabel( void ) {" in cl_main
    assert 'Com_DPrintf( "%s identity bootstrap: %s (%s [%s])\\n",' in identity_log_block
    assert "SteamClient_SyncPersonaNameCvar();" in init_block
    assert "QLWebHost_RegisterCommands();" in init_block
    assert init_block.index('Cmd_AddCommand ("clientviewprofile", CL_Steam_OverlayCommand_f );') < init_block.index("QLWebHost_RegisterCommands();")
    assert init_block.index("QLWebHost_RegisterCommands();") < init_block.index("SteamClient_SyncPersonaNameCvar();")
    assert 'CL_LogIdentityBootstrapFallback( "steam_persona_name", "identity bootstrap provider unavailable" );' in persona_block
    assert 'CL_LogIdentityBootstrapFallback( "steam_persona_name", "identity bootstrap initialisation failed" );' in persona_block
    assert 'CL_LogIdentityBootstrapFallback( "steam_persona_name", "persona unavailable; falling back to anon" );' in persona_block
    assert 'CL_LogIdentityBootstrapFallback( "steam_country_seed", "identity bootstrap provider unavailable" );' in country_block
    assert 'CL_LogIdentityBootstrapFallback( "steam_country_seed", "identity bootstrap initialisation failed" );' in country_block
    assert 'CL_LogIdentityBootstrapFallback( "steam_country_seed", "country seed unavailable" );' in country_block
    assert 'if ( QL_Steamworks_GetIPCountry( country, sizeof( country ) ) && country[0] ) {' in country_block
    assert 'Cvar_Set( "country", country );' in country_block

    assert '#include "../../common/platform/platform_services.h"' in cl_ui
    assert "static const char *QL_UI_GetSubscriptionBridgeModeLabel( void ) {" in cl_ui
    assert "static const char *QL_UI_GetSubscriptionBridgePolicyLabel( void ) {" in cl_ui
    assert 'Com_DPrintf( "UI subscription bridge ignored for app %d: %s (%s [%s])\\n",' in subscription_log_block
    assert 'QL_UI_LogSubscriptionBridgeIgnored( arg1, "subscription bridge provider unavailable" );' in subscribed_block
    assert "return QL_Steamworks_IsSubscribedApp( (uint32_t)arg1 ) ? 1 : 0;" in subscribed_block


def test_game_start_publisher_reconstructs_retail_match_presence_and_connect_handoff() -> None:
    client_h = (REPO_ROOT / "src/code/client/client.h").read_text(encoding="utf-8")
    qcommon_h = (REPO_ROOT / "src/code/qcommon/qcommon.h").read_text(encoding="utf-8")
    cl_main = (REPO_ROOT / "src/code/client/cl_main.c").read_text(encoding="utf-8")
    cl_cgame = (REPO_ROOT / "src/code/client/cl_cgame.c").read_text(encoding="utf-8")

    presence_block = _extract_function_block(cl_main, "static void CL_Steam_SetMatchRichPresence( void )")
    packed_publish_block = _extract_function_block(
        cl_main, "static void CL_WebView_PublishPackedGameStart( uint32_t packedIp, unsigned int port, qboolean publishLanIp )"
    )
    publish_for_address_block = _extract_function_block(
        cl_main, "static void CL_WebView_PublishGameStartForAddress( const netadr_t *serverAddress )"
    )
    publish_start_block = _extract_function_block(cl_main, "void CL_WebView_PublishGameStart( void )")
    connect_block = _extract_function_block(cl_main, "void CL_Connect_f( void )")
    first_snapshot_block = _extract_function_block(cl_cgame, "void CL_FirstSnapshot( void )")

    assert "void CL_LogMatchmakingServiceIgnored( const char *commandName, const char *reason );" in client_h
    assert "qboolean\tNET_GetLocalAddressIP( netadr_t *address );" in qcommon_h
    assert "CL_SteamServicesEnabled()" in presence_block
    assert "clc.demoplaying" in presence_block
    assert 'CL_LogMatchmakingServiceIgnored( "steam_presence_match", "matchmaking provider unavailable" );' in presence_block
    assert 'if ( !QL_Steamworks_SetRichPresence( "status", "Playing a match" ) ) {' in presence_block
    assert 'CL_LogMatchmakingServiceIgnored( "steam_presence_match", "rich presence update failed" );' in presence_block
    assert 'Com_sprintf( lanAddress, sizeof( lanAddress ), "%lu:%u", (unsigned long)packedIp, port );' in packed_publish_block
    assert 'QL_Steamworks_SetRichPresence( "lanIp", lanAddress );' in packed_publish_block
    assert "CL_Steam_SetMatchRichPresence();" in packed_publish_block
    assert 'Com_sprintf( payload, sizeof( payload ), "{\\"ip\\":%u,\\"port\\":%u}", packedIp, port );' in packed_publish_block
    assert "NET_GetLocalAddressIP( &localAddress )" in publish_start_block
    assert "packedIp = QL_Steamworks_ServerGetPublicIP();" in publish_start_block
    assert "CL_WebView_PublishGameStartForAddress( &serverAddress );" in publish_start_block
    assert "CL_WebView_PublishPackedGameStart( CL_WebView_PackAddressIP( serverAddress ), port, qfalse );" in publish_for_address_block
    assert 'Cvar_Set( "cl_currentServerAddress", server );' in connect_block
    assert "CL_WebView_PublishGameStartForAddress( &clc.serverAddress );" in connect_block
    assert "CL_WebView_PublishGameStart();" in first_snapshot_block


def test_server_game_server_wrappers_reconstruct_mapped_server_slots() -> None:
    steamworks = (REPO_ROOT / "src/common/platform/platform_steamworks.c").read_text(encoding="utf-8")

    platform_shutdown_block = _extract_function_block(steamworks, "void QL_Steamworks_Shutdown( void )")
    init_block = _extract_function_block(steamworks, "qboolean QL_Steamworks_ServerInit( uint32_t ip, uint16_t gamePort, qboolean secure, qboolean dedicated )")
    shutdown_block = _extract_function_block(steamworks, "void QL_Steamworks_ServerShutdown( void )")
    is_initialised_block = _extract_function_block(steamworks, "qboolean QL_Steamworks_ServerIsInitialised( void )")
    run_callbacks_block = _extract_function_block(steamworks, "void QL_Steamworks_RunServerCallbacks( void )")
    register_callbacks_block = _extract_function_block(
        steamworks, "qboolean QL_Steamworks_RegisterServerCallbacks( const ql_steam_server_callback_bindings_t *bindings )"
    )
    unregister_callbacks_block = _extract_function_block(steamworks, "void QL_Steamworks_UnregisterServerCallbacks( void )")
    dispatch_log_block = _extract_function_block(
        steamworks, "static void QL_Steamworks_LogServerCallbackDispatch( const char *stage, const char *detail ) {"
    )
    dispatch_connected_block = _extract_function_block(
        steamworks, "static void QL_Steamworks_DispatchServersConnected( void *context, const void *payload )"
    )
    dispatch_failure_block = _extract_function_block(
        steamworks, "static void QL_Steamworks_DispatchServerConnectFailure( void *context, const void *payload )"
    )
    dispatch_disconnected_block = _extract_function_block(
        steamworks, "static void QL_Steamworks_DispatchServersDisconnected( void *context, const void *payload )"
    )
    dispatch_validate_auth_block = _extract_function_block(
        steamworks, "static void QL_Steamworks_DispatchValidateAuthTicketResponse( void *context, const void *payload )"
    )
    dispatch_p2p_block = _extract_function_block(
        steamworks, "static void QL_Steamworks_DispatchServerP2PSessionRequest( void *context, const void *payload )"
    )
    ugc_block = _extract_function_block(steamworks, "static void *QL_Steamworks_GetUGCInterface( void )")
    dedicated_block = _extract_function_block(steamworks, "qboolean QL_Steamworks_ServerSetDedicated( qboolean dedicated )")
    logon_block = _extract_function_block(steamworks, "qboolean QL_Steamworks_ServerLogOn( const char *account )")
    product_block = _extract_function_block(steamworks, "qboolean QL_Steamworks_ServerSetProduct( const char *product )")
    game_dir_block = _extract_function_block(steamworks, "qboolean QL_Steamworks_ServerSetGameDir( const char *gameDir )")
    description_block = _extract_function_block(steamworks, "qboolean QL_Steamworks_ServerSetGameDescription( const char *description )")
    max_players_block = _extract_function_block(steamworks, "qboolean QL_Steamworks_ServerSetMaxPlayerCount( int maxPlayers )")
    bot_players_block = _extract_function_block(steamworks, "qboolean QL_Steamworks_ServerSetBotPlayerCount( int botPlayers )")
    server_name_block = _extract_function_block(steamworks, "qboolean QL_Steamworks_ServerSetServerName( const char *name )")
    map_name_block = _extract_function_block(steamworks, "qboolean QL_Steamworks_ServerSetMapName( const char *mapName )")
    password_block = _extract_function_block(steamworks, "qboolean QL_Steamworks_ServerSetPasswordProtected( qboolean passwordProtected )")
    heartbeat_block = _extract_function_block(steamworks, "qboolean QL_Steamworks_ServerEnableHeartbeats( qboolean enable )")
    steam_id_block = _extract_function_block(steamworks, "qboolean QL_Steamworks_ServerGetSteamID( uint32_t *outIdLow, uint32_t *outIdHigh )")
    game_tags_block = _extract_function_block(steamworks, "qboolean QL_Steamworks_ServerSetGameTags( const char *tags )")
    key_value_block = _extract_function_block(steamworks, "qboolean QL_Steamworks_ServerSetKeyValue( const char *key, const char *value )")
    key_values_block = _extract_function_block(steamworks, "qboolean QL_Steamworks_ServerSetKeyValuesFromInfoString( const char *infoString )")
    user_data_block = _extract_function_block(steamworks, "qboolean QL_Steamworks_ServerUpdateUserData( const CSteamID *steamId, const char *playerName, uint32_t score )")
    public_ip_block = _extract_function_block(steamworks, "uint32_t QL_Steamworks_ServerGetPublicIP( void )")
    accept_p2p_block = _extract_function_block(steamworks, "qboolean QL_Steamworks_ServerAcceptP2PSession( const CSteamID *steamId )")
    begin_auth_block = _extract_function_block(
        steamworks, "qboolean QL_Steamworks_ServerBeginAuthSession( const CSteamID *steamId, const char *ticketHex, ql_auth_response_t *response )"
    )
    end_auth_block = _extract_function_block(steamworks, "void QL_Steamworks_ServerEndAuthSession( const CSteamID *steamId )")

    assert "#define QL_STEAM_CALLBACK_STEAM_SERVERS_CONNECTED 0x65" in steamworks
    assert "#define QL_STEAM_CALLBACK_STEAM_SERVER_CONNECT_FAILURE 0x66" in steamworks
    assert "#define QL_STEAM_CALLBACK_STEAM_SERVERS_DISCONNECTED 0x67" in steamworks
    assert "#define QL_STEAM_CALLBACK_VALIDATE_AUTH_TICKET_RESPONSE 0x8f" in steamworks
    assert "#define QL_STEAM_CALLBACK_P2P_SESSION_REQUEST 0x4b2" in steamworks
    assert "QL_Steamworks_UnregisterServerCallbacks();" in platform_shutdown_block
    assert "QL_Steamworks_ServerShutdown();" in platform_shutdown_block
    assert platform_shutdown_block.index("QL_Steamworks_UnregisterServerCallbacks();") < platform_shutdown_block.index(
        "QL_Steamworks_ServerShutdown();"
    )
    assert "if ( state.gameServerInitialised ) {" in init_block
    assert "if ( !QL_Steamworks_Init() || !state.SteamGameServer_Init ) {" in init_block
    assert "serverMode = secure ? QL_STEAM_GAMESERVER_MODE_AUTH_SECURE : QL_STEAM_GAMESERVER_MODE_NO_AUTH;" in init_block
    assert "state.SteamGameServer_Init( ip, 0, gamePort, 0xffffu, serverMode, QL_STEAM_GAMESERVER_VERSION )" in init_block
    assert "state.gameServerInitialised = qtrue;" in init_block
    assert "state.useGameServerUGC = dedicated ? qtrue : qfalse;" in init_block
    assert "if ( state.gameServerInitialised && state.SteamGameServer_Shutdown ) {" in shutdown_block
    assert "state.gameServerInitialised = qfalse;" in shutdown_block
    assert "state.useGameServerUGC = qfalse;" in shutdown_block
    assert "return state.gameServerInitialised;" in is_initialised_block
    assert "!state.gameServerInitialised" in run_callbacks_block
    assert 'Com_DPrintf( "Steam server callback dispatch %s via %s [%s]: %s\\n",' in dispatch_log_block
    assert "services = QL_GetPlatformServices();" in dispatch_log_block
    assert 'provider = services->matchmaking.provider ? services->matchmaking.provider : "Unavailable";' in dispatch_log_block
    assert 'policy = QL_DescribePlatformFeaturePolicy( &services->matchmaking );' in dispatch_log_block
    assert 'QL_Steamworks_LogServerCallbackDispatch( "servers_connected", "ignored dispatch without callback state" );' in dispatch_connected_block
    assert 'QL_Steamworks_LogServerCallbackDispatch( "servers_connected", "ignored dispatch without registered callback" );' in dispatch_connected_block
    assert 'QL_Steamworks_LogServerCallbackDispatch( "connect_failure", "ignored dispatch without callback state" );' in dispatch_failure_block
    assert 'QL_Steamworks_LogServerCallbackDispatch( "connect_failure", "ignored dispatch without registered callback" );' in dispatch_failure_block
    assert 'QL_Steamworks_LogServerCallbackDispatch( "connect_failure", "ignored dispatch without payload" );' in dispatch_failure_block
    assert 'QL_Steamworks_LogServerCallbackDispatch( "disconnected", "ignored dispatch without callback state" );' in dispatch_disconnected_block
    assert 'QL_Steamworks_LogServerCallbackDispatch( "disconnected", "ignored dispatch without registered callback" );' in dispatch_disconnected_block
    assert 'QL_Steamworks_LogServerCallbackDispatch( "disconnected", "ignored dispatch without payload" );' in dispatch_disconnected_block
    assert 'QL_Steamworks_LogServerCallbackDispatch( "validate_auth_ticket_response", "ignored dispatch without callback state" );' in dispatch_validate_auth_block
    assert 'QL_Steamworks_LogServerCallbackDispatch( "validate_auth_ticket_response", "ignored dispatch without registered callback" );' in dispatch_validate_auth_block
    assert 'QL_Steamworks_LogServerCallbackDispatch( "validate_auth_ticket_response", "ignored dispatch without payload" );' in dispatch_validate_auth_block
    assert 'QL_Steamworks_LogServerCallbackDispatch( "p2p_session_request", "ignored dispatch without callback state" );' in dispatch_p2p_block
    assert 'QL_Steamworks_LogServerCallbackDispatch( "p2p_session_request", "ignored dispatch without registered callback" );' in dispatch_p2p_block
    assert 'QL_Steamworks_LogServerCallbackDispatch( "p2p_session_request", "ignored dispatch without payload" );' in dispatch_p2p_block
    assert "if ( callbackState->registered ) {" in register_callbacks_block
    assert "QL_Steamworks_UnregisterServerCallbacks();" in register_callbacks_block
    assert (
        "QL_Steamworks_PrepareCallbackObject( &callbackState->serversConnected, QL_STEAM_CALLBACK_STEAM_SERVERS_CONNECTED"
        in register_callbacks_block
    )
    assert (
        "QL_Steamworks_PrepareCallbackObject( &callbackState->validateAuthTicketResponse, QL_STEAM_CALLBACK_VALIDATE_AUTH_TICKET_RESPONSE"
        in register_callbacks_block
    )
    assert (
        "QL_Steamworks_PrepareCallbackObject( &callbackState->p2pSessionRequest, QL_STEAM_CALLBACK_P2P_SESSION_REQUEST"
        in register_callbacks_block
    )
    assert "!QL_Steamworks_RegisterCallbackObject( &callbackState->serversConnected )" in register_callbacks_block
    assert "!QL_Steamworks_RegisterCallbackObject( &callbackState->validateAuthTicketResponse )" in register_callbacks_block
    assert "!QL_Steamworks_RegisterCallbackObject( &callbackState->p2pSessionRequest )" in register_callbacks_block
    assert "callbackState->registered = qtrue;" in register_callbacks_block
    assert "QL_Steamworks_UnregisterCallbackObject( &callbackState->p2pSessionRequest );" in unregister_callbacks_block
    assert "QL_Steamworks_UnregisterCallbackObject( &callbackState->validateAuthTicketResponse );" in unregister_callbacks_block
    assert "QL_Steamworks_UnregisterCallbackObject( &callbackState->serversConnected );" in unregister_callbacks_block
    assert "memset( callbackState, 0, sizeof( *callbackState ) );" in unregister_callbacks_block
    assert "if ( state.useGameServerUGC && state.gameServerInitialised && state.SteamGameServerUGC ) {" in ugc_block
    assert "return state.SteamGameServerUGC();" in ugc_block
    assert "return state.SteamUGC();" in ugc_block
    assert "vtable[0x10 / 4]" in dedicated_block
    assert "fn( gameServer, dedicated ? 1 : 0 );" in dedicated_block
    assert "vtable[0x14 / 4]" in logon_block
    assert "vtable[0x18 / 4]" in logon_block
    assert "if ( account && account[0] ) {" in logon_block
    assert "logOnFn( gameServer, account );" in logon_block
    assert "anonymousFn( gameServer );" in logon_block
    assert "vtable[0x04 / 4]" in product_block
    assert "fn( gameServer, product );" in product_block
    assert "vtable[0x0c / 4]" in game_dir_block
    assert "fn( gameServer, gameDir );" in game_dir_block
    assert "vtable[0x08 / 4]" in description_block
    assert "fn( gameServer, description );" in description_block
    assert "vtable[0x30 / 4]" in max_players_block
    assert "fn( gameServer, maxPlayers );" in max_players_block
    assert "vtable[0x34 / 4]" in bot_players_block
    assert "fn( gameServer, botPlayers );" in bot_players_block
    assert "vtable[0x38 / 4]" in server_name_block
    assert "fn( gameServer, name );" in server_name_block
    assert "vtable[0x3c / 4]" in map_name_block
    assert "fn( gameServer, mapName );" in map_name_block
    assert "vtable[0x40 / 4]" in password_block
    assert "fn( gameServer, passwordProtected ? 1 : 0 );" in password_block
    assert "vtable[0x9c / 4]" in heartbeat_block
    assert "fn( gameServer, enable ? 1 : 0 );" in heartbeat_block
    assert "return qtrue;" in heartbeat_block
    assert "vtable[0x28 / 4]" in steam_id_block
    assert "if ( !fn( gameServer, NULL, &steamId ) ) {" in steam_id_block
    assert "*outIdLow = (uint32_t)( steamId.value & 0xffffffffu );" in steam_id_block
    assert "*outIdHigh = (uint32_t)( ( steamId.value >> 32 ) & 0xffffffffu );" in steam_id_block
    assert "vtable[0x54 / 4]" in game_tags_block
    assert "fn( gameServer, tags );" in game_tags_block
    assert "vtable[0x50 / 4]" in key_value_block
    assert "fn( gameServer, key, value );" in key_value_block
    assert "Info_NextPair( &head, key, value );" in key_values_block
    assert "QL_Steamworks_ServerSetKeyValue( key, value )" in key_values_block
    assert "vtable[0x6c / 4]" in user_data_block
    assert "idLow = (uint32_t)( steamId->value & 0xffffffffu );" in user_data_block
    assert "idHigh = (uint32_t)( ( steamId->value >> 32 ) & 0xffffffffu );" in user_data_block
    assert "return fn( gameServer, idLow, idHigh, playerName, score ) != 0 ? qtrue : qfalse;" in user_data_block
    assert "vtable[0x90 / 4]" in public_ip_block
    assert "return fn( gameServer );" in public_ip_block
    assert "vtable[0x0c / 4]" in accept_p2p_block
    assert "return acceptSession( networking, *steamId ) ? qtrue : qfalse;" in accept_p2p_block
    assert "QL_Steamworks_HexDecode( ticketHex, ticketData, sizeof( ticketData ), &ticketLength )" in begin_auth_block
    assert "result = state.BeginAuthSession( gameServer, ticketData, (int)ticketLength, *steamId );" in begin_auth_block
    assert "QL_Steamworks_MapAuthResult( result, response );" in begin_auth_block
    assert "state.EndAuthSession( gameServer, *steamId );" in end_auth_block


def test_server_frame_reconstructs_retail_steam_server_owner() -> None:
    sv_main = (REPO_ROOT / "src/code/server/sv_main.c").read_text(encoding="utf-8")

    networking_log_block = _extract_function_block(
        sv_main, "static void SV_LogSteamServerNetworkingLifecycle( const CSteamID *steamId, const char *stage, const char *detail ) {"
    )
    keepalive_block = _extract_function_block(sv_main, "static void SV_SteamServerSendKeepAlive( void )")
    relay_block = _extract_function_block(sv_main, "static void SV_SteamServerRelayP2PPackets( void )")
    helper_block = _extract_function_block(sv_main, "static void SV_SteamServerNetworkingFrame( void )")
    frame_block = _extract_function_block(sv_main, "void SV_Frame( int msec )")

    assert 'Com_DPrintf( "Steam server networking %s for %llu via %s [%s]: %s\\n",' in networking_log_block
    assert "SV_GetSteamServerProviderLabel()" in networking_log_block
    assert "SV_GetSteamServerPolicyLabel()" in networking_log_block
    assert 'if ( !QL_Steamworks_ServerSendP2PPacket( &steamId, keepAlive, (uint32_t)sizeof( keepAlive ), 2, 16 ) ) {' in keepalive_block
    assert 'SV_LogSteamServerNetworkingLifecycle( &steamId, "keepalive", "send failed" );' in keepalive_block
    assert 'SV_LogSteamServerNetworkingLifecycle( NULL, "p2p-read", "read failed" );' in relay_block
    assert 'SV_LogSteamServerNetworkingLifecycle( &remoteId, "p2p-relay", "sender not found" );' in relay_block
    assert 'SV_LogSteamServerNetworkingLifecycle( &clientId, "p2p-relay", "relay send failed" );' in relay_block
    assert "QL_Steamworks_RunServerCallbacks();" in helper_block
    assert "SV_SteamServerSendKeepAlive();" in helper_block
    assert "SV_SteamServerRelayP2PPackets();" in helper_block
    assert "SV_SteamServerDrainOutgoingPackets();" in helper_block
    assert "SV_SteamServerNetworkingFrame();" in frame_block
    assert "QL_Steamworks_RunCallbacks();" not in frame_block


def test_server_info_changes_reconstruct_retail_steam_rule_publication() -> None:
    sv_init = (REPO_ROOT / "src/code/server/sv_init.c").read_text(encoding="utf-8")
    sv_main = (REPO_ROOT / "src/code/server/sv_main.c").read_text(encoding="utf-8")

    spawn_block = _extract_function_block(sv_init, "void SV_SpawnServer( char *server, qboolean killBots )")
    frame_block = _extract_function_block(sv_main, "void SV_Frame( int msec )")

    assert "serverInfo = Cvar_InfoString( CVAR_SERVERINFO );" in spawn_block
    assert "SV_SetConfigstring( CS_SERVERINFO, serverInfo );" in spawn_block
    assert "QL_Steamworks_ServerSetKeyValuesFromInfoString( serverInfo );" in spawn_block
    assert "serverInfo = Cvar_InfoString( CVAR_SERVERINFO );" in frame_block
    assert "QL_Steamworks_ServerSetKeyValuesFromInfoString( serverInfo );" in frame_block
    assert "SV_SetConfigstring( CS_SERVERINFO, serverInfo );" in frame_block


def test_server_published_state_reconstructs_retail_steam_server_owner() -> None:
    sv_init = (REPO_ROOT / "src/code/server/sv_init.c").read_text(encoding="utf-8")
    sv_main = (REPO_ROOT / "src/code/server/sv_main.c").read_text(encoding="utf-8")

    description_block = _extract_function_block(sv_main, "static const char *SV_SteamServerGameDescription( int gametype )")
    tag_name_block = _extract_function_block(sv_main, "static const char *SV_SteamServerGameTagName( int gametype )")
    tag_build_block = _extract_function_block(sv_main, "static void SV_SteamServerBuildGameTags( char *tags, int size )")
    publish_log_block = _extract_function_block(
        sv_main, "static void SV_LogSteamServerPublishedState( const CSteamID *steamId, const char *stage, const char *detail ) {"
    )
    publish_block = _extract_function_block(sv_main, "void SV_SteamServerUpdatePublishedState( qboolean fullUpdate )")
    spawn_block = _extract_function_block(sv_init, "void SV_SpawnServer( char *server, qboolean killBots )")
    frame_block = _extract_function_block(sv_main, "void SV_Frame( int msec )")

    assert '"Attack & Defend"' in description_block
    assert '"Unknown Gametype"' in description_block
    assert '"clanarena"' in tag_name_block
    assert '"freezetag"' in tag_name_block
    assert '"domination"' in tag_name_block
    assert '"a&d"' in tag_name_block
    assert '"redrover"' in tag_name_block
    assert 'SV_SteamServerAppendGameTag( tags, size, SV_SteamServerGameTagName( gametype ) );' in tag_build_block
    assert 'if ( Cvar_VariableIntegerValue( "sv_cheats" ) ) {' in tag_build_block
    assert 'SV_SteamServerAppendGameTag( tags, size, "cheats" );' in tag_build_block
    assert 'if ( Cvar_VariableIntegerValue( "g_instagib" ) ) {' in tag_build_block
    assert 'SV_SteamServerAppendGameTag( tags, size, "instagib" );' in tag_build_block
    assert 'SV_SteamServerAppendGameTag( tags, size, "lowgrav" );' in tag_build_block
    assert 'SV_SteamServerAppendGameTag( tags, size, "highgrav" );' in tag_build_block
    assert 'SV_SteamServerAppendGameTag( tags, size, "vampiric" );' in tag_build_block
    assert 'SV_SteamServerAppendGameTag( tags, size, "infected" );' in tag_build_block
    assert 'SV_SteamServerAppendGameTag( tags, size, "quadhog" );' in tag_build_block
    assert 'Q_strcat( tags, size, sv_tags->string );' in tag_build_block
    assert "SV_SteamServerTrimGameTags( tags );" in tag_build_block
    assert 'Com_DPrintf( "Steam server published state %s for %llu via %s [%s]: %s\\n",' in publish_log_block
    assert "SV_GetSteamServerProviderLabel()" in publish_log_block
    assert "SV_GetSteamServerPolicyLabel()" in publish_log_block
    assert 'if ( !QL_Steamworks_ServerSetMaxPlayerCount( sv_maxclients ? sv_maxclients->integer : 0 ) ) {' in publish_block
    assert 'SV_LogSteamServerPublishedState( NULL, "max-players", "publish failed" );' in publish_block
    assert 'needPass = Cvar_VariableIntegerValue( "g_needpass" );' in publish_block
    assert 'if ( !QL_Steamworks_ServerSetPasswordProtected( needPass ? qtrue : qfalse ) ) {' in publish_block
    assert 'SV_LogSteamServerPublishedState( NULL, "password-protected", "publish failed" );' in publish_block
    assert 'if ( !QL_Steamworks_ServerSetServerName( sv_hostname->string ) ) {' in publish_block
    assert 'SV_LogSteamServerPublishedState( NULL, "server-name", "publish failed" );' in publish_block
    assert 'if ( !QL_Steamworks_ServerSetMapName( sv_mapname->string ) ) {' in publish_block
    assert 'SV_LogSteamServerPublishedState( NULL, "map-name", "publish failed" );' in publish_block
    assert 'if ( !QL_Steamworks_ServerSetGameDescription( SV_SteamServerGameDescription( sv_gametype->integer ) ) ) {' in publish_block
    assert 'SV_LogSteamServerPublishedState( NULL, "game-description", "publish failed" );' in publish_block
    assert "SV_SteamServerBuildGameTags( gameTags, sizeof( gameTags ) );" in publish_block
    assert 'if ( !QL_Steamworks_ServerSetGameTags( gameTags ) ) {' in publish_block
    assert 'SV_LogSteamServerPublishedState( NULL, "game-tags", "publish failed" );' in publish_block
    assert 'Cvar_VariableStringBuffer( "g_redScore", redScore, sizeof( redScore ) );' in publish_block
    assert 'if ( !QL_Steamworks_ServerSetKeyValue( "g_redScore", redScore ) ) {' in publish_block
    assert 'SV_LogSteamServerPublishedState( NULL, "key-value", "publish failed for g_redScore" );' in publish_block
    assert 'Cvar_VariableStringBuffer( "g_blueScore", blueScore, sizeof( blueScore ) );' in publish_block
    assert 'if ( !QL_Steamworks_ServerSetKeyValue( "g_blueScore", blueScore ) ) {' in publish_block
    assert 'SV_LogSteamServerPublishedState( NULL, "key-value", "publish failed for g_blueScore" );' in publish_block
    assert 'rawName = Info_ValueForKey( cl->userinfo, "name" );' in publish_block
    assert 'Com_sprintf( playerName, sizeof( playerName ), "(Bot) %s", rawName );' in publish_block
    assert "playerState = SV_GameClientNum( i );" in publish_block
    assert 'if ( !QL_Steamworks_ServerUpdateUserData( &steamId, playerName, (uint32_t)playerState->persistant[PERS_SCORE] ) ) {' in publish_block
    assert 'Com_sprintf( detail, sizeof( detail ), "publish failed for client %d (%s)", i, playerName );' in publish_block
    assert 'SV_LogSteamServerPublishedState( &steamId, "user-data", detail );' in publish_block
    assert 'if ( !QL_Steamworks_ServerSetBotPlayerCount( botCount ) ) {' in publish_block
    assert 'SV_LogSteamServerPublishedState( NULL, "bot-player-count", "publish failed" );' in publish_block
    assert "SV_SteamServerUpdatePublishedState( qtrue );" in spawn_block
    assert "SV_SteamServerUpdatePublishedState( qfalse );" in frame_block


def test_server_init_reconstructs_retail_hostname_and_bootstrap_metadata() -> None:
	common = (REPO_ROOT / "src/code/qcommon/common.c").read_text(encoding="utf-8")
	qcommon = (REPO_ROOT / "src/code/qcommon/qcommon.h").read_text(encoding="utf-8")
	server_h = (REPO_ROOT / "src/code/server/server.h").read_text(encoding="utf-8")
	sv_init = (REPO_ROOT / "src/code/server/sv_init.c").read_text(encoding="utf-8")

	hostname_block = _extract_function_block(sv_init, "static void SV_SteamServerInitDefaultHostname( void )")
	pack_ip_block = _extract_function_block(common, "static uint32_t Com_SteamPackGameServerIP( const char *addressString )")
	bootstrap_block = _extract_function_block(common, "void Com_InitSteamGameServer( void )")
	common_init_block = _extract_function_block(common, "void Com_Init( char *commandLine )")
	common_shutdown_block = _extract_function_block(common, "void Com_Shutdown (void)")
	sv_init_block = _extract_function_block(sv_init, "void SV_Init (void)")
	spawn_block = _extract_function_block(sv_init, "void SV_SpawnServer( char *server, qboolean killBots )")
	publish_block = _extract_function_block(sv_init, "void SV_SteamServerPublishIdentity( void )")

	assert "if ( com_buildScript && com_buildScript->integer ) {" in hostname_block
	assert 'sv_hostname = Cvar_Get ("sv_hostname", "noname", CVAR_SERVERINFO | CVAR_ARCHIVE );' in hostname_block
	assert "if ( !QL_Steamworks_Init() || !QL_Steamworks_GetPersonaName( personaName, sizeof( personaName ) ) ) {" in hostname_block
	assert 'Q_strncpyz( personaName, "anon", sizeof( personaName ) );' in hostname_block
	assert 'Com_sprintf( defaultHostname, sizeof( defaultHostname ), "%s\'s Match", personaName );' in hostname_block
	assert 'sv_hostname = Cvar_Get ("sv_hostname", defaultHostname, CVAR_SERVERINFO | CVAR_ARCHIVE );' in hostname_block
	assert 'if ( !addressString || !addressString[0] || !Q_stricmp( addressString, "localhost" ) ) {' in pack_ip_block
	assert "if ( !NET_StringToAdr( addressString, &address ) || address.type != NA_IP ) {" in pack_ip_block
	assert "dedicated = ( com_dedicated && com_dedicated->integer > 0 ) ? qtrue : qfalse;" in bootstrap_block
	assert 'Cvar_Get( "sv_setSteamAccount", "", CVAR_ARCHIVE | CVAR_PROTECTED );' in bootstrap_block
	assert 'steamVac = Cvar_Get( "sv_vac", "1", CVAR_SERVERINFO | CVAR_ARCHIVE );' in bootstrap_block
	assert 'netPort = Cvar_Get( "net_port", va( "%i", PORT_SERVER ), CVAR_LATCH );' in bootstrap_block
	assert "if ( !QL_Steamworks_ServerInit( steamIp, (uint16_t)netPort->integer, steamVac && steamVac->integer ? qtrue : qfalse, dedicated ) ) {" in bootstrap_block
	assert 'Com_Printf( "Steam GameServer bootstrap unavailable for %s [%s]; keeping compatibility-only dedicated-server publication fallback.\\n",' in bootstrap_block
	assert "QL_Steamworks_ServerSetDedicated( dedicated );" in bootstrap_block
	assert 'Cvar_VariableStringBuffer( "sv_setSteamAccount", steamAccount, sizeof( steamAccount ) );' in bootstrap_block
	assert "QL_Steamworks_ServerLogOn( steamAccount );" in bootstrap_block
	assert "QL_Steamworks_ServerEnableHeartbeats( qfalse );" in bootstrap_block
	assert 'QL_Steamworks_ServerSetProduct( "Quake Live" );' in bootstrap_block
	assert 'QL_Steamworks_ServerSetGameDir( "baseq3" );' in bootstrap_block
	assert "void\t\tCom_InitSteamGameServer( void );" in qcommon
	assert "const char *SV_GetPlatformAuthProviderLabel( void );" in server_h
	assert "const char *SV_GetPlatformAuthPolicyLabel( void );" in server_h
	assert "const char *SV_GetSteamServerProviderLabel( void );" in server_h
	assert "const char *SV_GetSteamServerPolicyLabel( void );" in server_h
	assert "const char *SV_GetWorkshopProviderLabel( void );" in server_h
	assert "const char *SV_GetWorkshopPolicyLabel( void );" in server_h
	assert "const char *SV_GetServerStatsProviderLabel( void );" in server_h
	assert "const char *SV_GetServerStatsPolicyLabel( void );" in server_h
	assert "void SV_RefreshPlatformServiceCvars( void );" in server_h
	assert "static const ql_platform_feature_descriptor *Com_GetSteamGameServerServiceDescriptor( void ) {" in common
	assert "static const char *Com_GetSteamGameServerProviderLabel( void ) {" in common
	assert "static const char *Com_GetSteamGameServerPolicyLabel( void ) {" in common
	assert "Com_InitSteamGameServer();" in common_init_block
	assert "QL_Steamworks_Shutdown();" in common_shutdown_block
	assert "SV_SteamServerInitDefaultHostname();" in sv_init_block
	assert 'sv_tags = Cvar_Get ("sv_tags", "", CVAR_ARCHIVE );' in sv_init_block
	assert 'Cvar_Get ("sv_setSteamAccount", "", CVAR_ARCHIVE | CVAR_PROTECTED );' in sv_init_block
	assert 'Cvar_Get ("sv_platformAuthProvider", "Unavailable", CVAR_ROM );' in sv_init_block
	assert 'Cvar_Get ("sv_platformAuthPolicy", "compatibility-unavailable", CVAR_ROM );' in sv_init_block
	assert 'Cvar_Get ("sv_steamServerProvider", "Unavailable", CVAR_ROM );' in sv_init_block
	assert 'Cvar_Get ("sv_steamServerPolicy", "compatibility-unavailable", CVAR_ROM );' in sv_init_block
	assert 'Cvar_Get ("sv_workshopProvider", "Unavailable", CVAR_ROM );' in sv_init_block
	assert 'Cvar_Get ("sv_workshopPolicy", "compatibility-unavailable", CVAR_ROM );' in sv_init_block
	assert 'Cvar_Get ("sv_statsProvider", "Unavailable", CVAR_ROM );' in sv_init_block
	assert 'Cvar_Get ("sv_statsPolicy", "compatibility-unavailable", CVAR_ROM );' in sv_init_block
	assert 'Cvar_Get ("sv_onlineServicesMode", "Unavailable", CVAR_ROM );' in sv_init_block
	assert 'Cvar_Get ("sv_onlineServicesPolicy", "compatibility-unavailable", CVAR_ROM );' in sv_init_block
	assert 'Cvar_Set( "sv_onlineServicesMode", QL_GetOnlineServicesModeLabel() );' in sv_init
	assert 'Cvar_Set( "sv_onlineServicesPolicy", QL_GetOnlineServicesPolicyLabel() );' in sv_init
	assert 'Cvar_Set( "sv_workshopProvider", SV_GetWorkshopProviderLabel() );' in sv_init
	assert 'Cvar_Set( "sv_workshopPolicy", SV_GetWorkshopPolicyLabel() );' in sv_init
	assert 'Cvar_Set( "sv_statsProvider", SV_GetServerStatsProviderLabel() );' in sv_init
	assert 'Cvar_Set( "sv_statsPolicy", SV_GetServerStatsPolicyLabel() );' in sv_init
	assert "SV_RefreshPlatformServiceCvars();" in sv_init_block
	assert "SV_RefreshPlatformServiceCvars();" in spawn_block
	assert 'SV_LogSteamServerIdentityLifecycle( "unavailable", "server steam ID unavailable" );' in publish_block
	assert 'Com_sprintf( detail, sizeof( detail ), "published id=%s referenced=%d",' in publish_block
	assert 'SV_LogSteamServerIdentityLifecycle( "published", detail );' in publish_block
	assert "SV_SteamServerConfigureBootstrap" not in sv_init


def test_net_restart_reconstructs_retail_network_and_steam_server_restart_order() -> None:
    win_net = (REPO_ROOT / "src/code/win32/win_net.c").read_text(encoding="utf-8")

    restart_block = _extract_function_block(win_net, "void NET_Restart( void )")

    assert "QL_Steamworks_ServerShutdown();" in restart_block
    assert "NET_Config( networkingEnabled );" in restart_block
    assert "Com_InitSteamGameServer();" in restart_block
    assert restart_block.index("QL_Steamworks_ServerShutdown();") < restart_block.index("NET_Config( networkingEnabled );")
    assert restart_block.index("NET_Config( networkingEnabled );") < restart_block.index("Com_InitSteamGameServer();")


def test_native_client_connect_denials_reconstruct_engine_owned_return_contract() -> None:
    sv_game = (REPO_ROOT / "src/code/server/sv_game.c").read_text(encoding="utf-8")
    server_h = (REPO_ROOT / "src/code/server/server.h").read_text(encoding="utf-8")
    sv_client = (REPO_ROOT / "src/code/server/sv_client.c").read_text(encoding="utf-8")
    sv_ccmds = (REPO_ROOT / "src/code/server/sv_ccmds.c").read_text(encoding="utf-8")
    sv_init = (REPO_ROOT / "src/code/server/sv_init.c").read_text(encoding="utf-8")

    connect_block = _extract_function_block(
        sv_game,
        "const char *SV_GameClientConnect( int clientNum, qboolean firstTime, qboolean isBot )",
    )
    direct_connect_block = _extract_function_block(sv_client, "void SV_DirectConnect( netadr_t from )")
    map_restart_block = _extract_function_block(sv_ccmds, "static void SV_MapRestart_f( void )")
    spawn_block = _extract_function_block(sv_init, "void SV_SpawnServer( char *server, qboolean killBots )")

    assert "static char\tsv_gameClientConnectDenied[MAX_STRING_CHARS];" in sv_game
    assert "int\t\t\tdeniedOffset;" in connect_block
    assert "const char\t*denied;" in connect_block
    assert "sv_gameClientConnectDenied[0] = '\\0';" in connect_block
    assert "deniedOffset = VM_Call( gvm, GAME_CLIENT_CONNECT, clientNum, firstTime, isBot );" in connect_block
    assert "denied = VM_ExplicitArgPtr( gvm, deniedOffset );" in connect_block
    assert "Q_strncpyz( sv_gameClientConnectDenied, denied, sizeof( sv_gameClientConnectDenied ) );" in connect_block
    assert "return sv_gameClientConnectDenied;" in connect_block
    assert "const char\t*SV_GameClientConnect( int clientNum, qboolean firstTime, qboolean isBot );" in server_h
    assert "denied = SV_GameClientConnect( clientNum, qtrue, qfalse );" in direct_connect_block
    assert "denied = SV_GameClientConnect( i, qfalse, isBot );" in map_restart_block
    assert "denied = SV_GameClientConnect( i, qfalse, isBot );" in spawn_block
    assert "VM_ExplicitArgPtr( gvm, VM_Call( gvm, GAME_CLIENT_CONNECT" not in sv_ccmds
    assert "VM_ExplicitArgPtr( gvm, VM_Call( gvm, GAME_CLIENT_CONNECT" not in sv_init


def test_ui_unique_cd_key_normalizes_nonzero_native_returns_to_qboolean() -> None:
    cl_ui = (REPO_ROOT / "src/code/client/cl_ui.c").read_text(encoding="utf-8")

    block = _extract_function_block(cl_ui, "qboolean UI_usesUniqueCDKey()")

    assert "return VM_Call( uivm, UI_HASUNIQUECDKEY ) ? qtrue : qfalse;" in block
    assert "== qtrue" not in block


def test_native_command_queries_and_fullscreen_gate_normalize_nonzero_returns_to_qboolean() -> None:
    cl_ui = (REPO_ROOT / "src/code/client/cl_ui.c").read_text(encoding="utf-8")
    cl_cgame = (REPO_ROOT / "src/code/client/cl_cgame.c").read_text(encoding="utf-8")
    cl_scrn = (REPO_ROOT / "src/code/client/cl_scrn.c").read_text(encoding="utf-8")
    sv_game = (REPO_ROOT / "src/code/server/sv_game.c").read_text(encoding="utf-8")

    ui_command_block = _extract_function_block(cl_ui, "qboolean UI_GameCommand( void )")
    cg_command_block = _extract_function_block(cl_cgame, "qboolean CL_GameCommand( void )")
    sv_command_block = _extract_function_block(sv_game, "qboolean SV_GameCommand( void )")
    draw_block = _extract_function_block(cl_scrn, "void SCR_DrawScreenField( stereoFrame_t stereoFrame ) {")

    assert "return VM_Call( uivm, UI_CONSOLE_COMMAND, cls.realtime ) ? qtrue : qfalse;" in ui_command_block
    assert "return VM_Call( cgvm, CG_CONSOLE_COMMAND ) ? qtrue : qfalse;" in cg_command_block
    assert "return VM_Call( gvm, GAME_CONSOLE_COMMAND ) ? qtrue : qfalse;" in sv_command_block
    assert "uiFullscreen = VM_Call( uivm, UI_IS_FULLSCREEN ) ? qtrue : qfalse;" in draw_block
    assert "return VM_Call( uivm, UI_CONSOLE_COMMAND, cls.realtime );" not in ui_command_block
    assert "return VM_Call( cgvm, CG_CONSOLE_COMMAND );" not in cg_command_block
    assert "return VM_Call( gvm, GAME_CONSOLE_COMMAND );" not in sv_command_block


def test_scr_adjust_from_640_matches_retail_engine_full_width_scaling() -> None:
    cl_scrn = (REPO_ROOT / "src/code/client/cl_scrn.c").read_text(encoding="utf-8")
    adjust_block = _extract_function_block(cl_scrn, "void SCR_AdjustFrom640( float *x, float *y, float *w, float *h ) {")

    for expected in (
        "float\txscale;",
        "float\tyscale;",
        "xscale = cls.glconfig.vidWidth / 640.0;",
        "yscale = cls.glconfig.vidHeight / 480.0;",
        "*x *= xscale;",
        "*w *= xscale;",
        "*y *= yscale;",
        "*h *= yscale;",
    ):
        assert expected in adjust_block

    assert "xbias" not in adjust_block


def test_native_qboolean_argument_owners_normalize_explicit_values() -> None:
    cl_ui = (REPO_ROOT / "src/code/client/cl_ui.c").read_text(encoding="utf-8")
    cl_cgame = (REPO_ROOT / "src/code/client/cl_cgame.c").read_text(encoding="utf-8")
    cl_keys = (REPO_ROOT / "src/code/client/cl_keys.c").read_text(encoding="utf-8")

    init_block = _extract_function_block(cl_ui, "void CL_InitUI( void )")
    rendering_block = _extract_function_block(cl_cgame, "void CL_CGameRendering( stereoFrame_t stereo )")
    key_block = _extract_function_block(cl_keys, "void CL_KeyEvent (int key, qboolean down, unsigned time)")

    assert "qboolean\tinGame;" in init_block
    assert "inGame = ( cls.state >= CA_AUTHORIZING && cls.state < CA_ACTIVE ) ? qtrue : qfalse;" in init_block
    assert "VM_Call( uivm, UI_INIT, inGame );" in init_block
    assert "(cls.state >= CA_AUTHORIZING && cls.state < CA_ACTIVE)" not in init_block.split("VM_Call( uivm, UI_INIT", 1)[1]
    assert "qboolean\tdemoPlaying;" in rendering_block
    assert "demoPlaying = clc.demoplaying ? qtrue : qfalse;" in rendering_block
    assert "VM_Call( cgvm, CG_DRAW_ACTIVE_FRAME, cl.serverTime, stereo, demoPlaying );" in rendering_block
    assert "qboolean\tdispatchDown;" in key_block
    assert "dispatchDown = down ? qtrue : qfalse;" in key_block
    assert "keys[key].down = dispatchDown;" in key_block
    assert "VM_Call( uivm, UI_KEY_EVENT, dispatchKey, dispatchDown, time );" in key_block
    assert "VM_Call( cgvm, CG_KEY_EVENT, dispatchKey, dispatchDown );" in key_block


def test_vm_native_export_dispatch_normalizes_qboolean_contracts() -> None:
    vm = (REPO_ROOT / "src/code/qcommon/vm.c").read_text(encoding="utf-8")

    arg_block = _extract_function_block(vm, "static qboolean VM_NormalizeQbooleanArg( int value )")
    result_block = _extract_function_block(vm, "static int VM_NormalizeQbooleanResult( qboolean value )")

    assert "return value ? qtrue : qfalse;" in arg_block
    assert "return value ? qtrue : qfalse;" in result_block
    assert "((void (QDECL *)( qboolean ))exportFunc)( VM_NormalizeQbooleanArg( args[0] ) );" in vm
    assert "return VM_NormalizeQbooleanResult( ((qboolean (QDECL *)( void ))exportFunc)() );" in vm
    assert "return VM_NormalizeQbooleanResult( ((qboolean (QDECL *)( int ))exportFunc)( args[0] ) );" in vm
    assert "((void (QDECL *)( int, stereoFrame_t, qboolean ))exportFunc)( args[0], args[1], VM_NormalizeQbooleanArg( args[2] ) );" in vm
    assert "((void (QDECL *)( int, qboolean ))exportFunc)( args[0], VM_NormalizeQbooleanArg( args[1] ) );" in vm
    assert "((void (QDECL *)( int, int, qboolean ))exportFunc)( args[0], args[1], VM_NormalizeQbooleanArg( args[2] ) );" in vm
    assert "((void (QDECL *)( qboolean ))exportFunc)( VM_NormalizeQbooleanArg( args[0] ) );" in vm
    assert "return (int)(intptr_t)((const char *(QDECL *)( int, qboolean, qboolean ))exportFunc)( args[0], VM_NormalizeQbooleanArg( args[1] ), VM_NormalizeQbooleanArg( args[2] ) );" in vm
    assert "return VM_NormalizeQbooleanResult( ((qboolean (QDECL *)( int, void * ))exportFunc)( args[0], (void *)(intptr_t)args[1] ) );" in vm
    assert "return VM_NormalizeQbooleanResult( ((qboolean (QDECL *)( int, int ))exportFunc)( args[0], args[1] ) );" in vm
    assert "return VM_NormalizeQbooleanResult( ((qboolean (QDECL *)( int ))exportFunc)( args[0] ) );" in vm


def test_vm_native_loader_rejects_incomplete_structured_export_tables() -> None:
    vm = (REPO_ROOT / "src/code/qcommon/vm.c").read_text(encoding="utf-8")

    export_count_block = _extract_function_block(vm, "static int VM_GetExpectedNativeExportCount( const char *module )")
    required_slot_block = _extract_function_block(vm, "static qboolean VM_NativeExportSlotIsRequired( const char *module, int slot )")
    validation_block = _extract_function_block(vm, "static qboolean VM_ValidateNativeDllInterface( vm_t *vm )")

    assert "return UI_NATIVE_EXPORT_COUNT;" in export_count_block
    assert "return CG_NATIVE_EXPORT_COUNT;" in export_count_block
    assert "return GAME_NATIVE_EXPORT_COUNT;" in export_count_block
    assert 'if ( !Q_stricmp( module, "cgame" ) && slot == CG_NATIVE_EXPORT_RESERVED_NULL ) {' in required_slot_block
    assert "return qfalse;" in required_slot_block
    assert "expectedExportCount = VM_GetExpectedNativeExportCount( vm->name );" in validation_block
    assert "dllExports = (void **)vm->dllExports;" in validation_block
    assert "for ( i = 0 ; i < expectedExportCount ; i++ ) {" in validation_block
    assert "if ( !VM_NativeExportSlotIsRequired( vm->name, i ) ) {" in validation_block
    assert "if ( !dllExports[i] ) {" in validation_block
    assert '''Com_Printf( "Rejected DLL '%s': missing native export slot %d for %s\\n",''' in validation_block
    assert 'VM_LogTraceEvent( "reject %s missing export %d", vm->name, i );' in validation_block


def test_native_import_dispatch_normalizes_qboolean_contracts() -> None:
    cl_ui = (REPO_ROOT / "src/code/client/cl_ui.c").read_text(encoding="utf-8")
    cl_cgame = (REPO_ROOT / "src/code/client/cl_cgame.c").read_text(encoding="utf-8")
    sv_game = (REPO_ROOT / "src/code/server/sv_game.c").read_text(encoding="utf-8")

    ui_block = _extract_function_block(cl_ui, "static int CL_UISystemCallsImpl( int *args, qboolean logContract )")
    cgame_block = _extract_function_block(cl_cgame, "static int CL_CgameSystemCallsImpl( int *args, qboolean logContract )")
    game_block = _extract_function_block(sv_game, "static int SV_GameSystemCallsImpl( int *args, qboolean logContract )")

    assert "return S_RegisterSound( VMA(1), args[2] ? qtrue : qfalse );" in ui_block
    assert "return Key_IsDown( args[1] ) ? qtrue : qfalse;" in ui_block
    assert "return Key_GetOverstrikeMode() ? qtrue : qfalse;" in ui_block
    assert "Key_SetOverstrikeMode( args[1] ? qtrue : qfalse );" in ui_block
    assert "LAN_MarkServerVisible( args[1], args[2], args[3] ? qtrue : qfalse );" in ui_block
    assert "return LAN_ServerIsVisible( args[1], args[2] ) ? qtrue : qfalse;" in ui_block
    assert "return LAN_UpdateVisiblePings( args[1] ) ? qtrue : qfalse;" in ui_block
    assert "return CL_CDKeyValidate(VMA(1), VMA(2)) ? qtrue : qfalse;" in ui_block

    assert "S_ClearLoopingSounds( args[1] ? qtrue : qfalse );" in cgame_block
    assert "return S_RegisterSound( VMA(1), args[2] ? qtrue : qfalse );" in cgame_block
    assert "return CL_GetSnapshot( args[1], VMA(2) ) ? qtrue : qfalse;" in cgame_block
    assert "return CL_GetServerCommand( args[1] ) ? qtrue : qfalse;" in cgame_block
    assert "return CL_GetUserCmd( args[1], VMA(2) ) ? qtrue : qfalse;" in cgame_block
    assert "return Key_IsDown( args[1] ) ? qtrue : qfalse;" in cgame_block
    assert "return Key_GetOverstrikeMode() ? qtrue : qfalse;" in cgame_block
    assert "Key_SetOverstrikeMode( args[1] ? qtrue : qfalse );" in cgame_block
    assert "return re.GetEntityToken( VMA(1), args[2] ) ? qtrue : qfalse;" in cgame_block
    assert "return re.inPVS( VMA(1), VMA(2) ) ? qtrue : qfalse;" in cgame_block

    assert "return SV_EntityContact( VMA(1), VMA(2), VMA(3), /*int capsule*/ qfalse ) ? qtrue : qfalse;" in game_block
    assert "return SV_EntityContact( VMA(1), VMA(2), VMA(3), /*int capsule*/ qtrue ) ? qtrue : qfalse;" in game_block
    assert "return SV_inPVS( VMA(1), VMA(2) ) ? qtrue : qfalse;" in game_block
    assert "return SV_inPVSIgnorePortals( VMA(1), VMA(2) ) ? qtrue : qfalse;" in game_block
    assert "return SV_GetClientSteamId( args[1], (uint32_t *)VMA(2), (uint32_t *)VMA(3) ) ? qtrue : qfalse;" in game_block
    assert "return SV_VerifyClientSteamAuth( args[1] ) ? qtrue : qfalse;" in game_block
    assert "SV_AdjustAreaPortalState( VMA(1), args[2] ? qtrue : qfalse );" in game_block


def test_loopback_steam_auth_verify_falls_back_for_local_clients() -> None:
    sv_game = (REPO_ROOT / "src/code/server/sv_game.c").read_text(encoding="utf-8")
    verify_block = _extract_function_block(sv_game, "static qboolean SV_VerifyClientSteamAuth( int clientNum )")
    platform_auth_section = verify_block.split("#else", 1)[1]

    assert "#if !SV_HAS_PLATFORM_AUTH" in verify_block
    assert "cl = &svs.clients[clientNum];" in verify_block
    assert "if ( NET_IsLocalAddress( cl->netchan.remoteAddress ) ) {" in verify_block
    assert "return qtrue;" in verify_block

    assert "if ( !cl->platformAuthToken[0] ) {" in verify_block
    assert "if ( NET_IsLocalAddress( cl->netchan.remoteAddress ) ) {" in verify_block
    assert "cl->platformAuthSucceeded = qtrue;" in verify_block
    assert "return qtrue;" in verify_block
    assert "if ( cl->platformAuthPending ) {" in verify_block
    assert "if ( cl->state < CS_CONNECTED ) {" in verify_block
    assert platform_auth_section.index("if ( cl->state < CS_CONNECTED ) {") < platform_auth_section.rindex("return qfalse;")
    assert "return qfalse;" in verify_block
    assert "return cl->platformAuthSucceeded;" in verify_block
    assert "QL_RequestExternalAuth" not in verify_block


def test_server_callback_auth_owner_reconstructs_retail_steam_gameserver_bundle() -> None:
    sv_client = (REPO_ROOT / "src/code/server/sv_client.c").read_text(encoding="utf-8")
    stub_section = sv_client.split("#else", 1)[1]

    compatibility_block = _extract_function_block(
        sv_client, "static void SV_BuildPlatformAuthCompatibilityDetail( const char *detail, char *buffer, int bufferSize )"
    )
    log_auth_block = _extract_function_block(
        sv_client, "static void SV_LogPlatformAuth( const netadr_t *adr, const client_t *cl, const char *status, const char *detail )"
    )
    connect_rejected_block = _extract_function_block(
        sv_client, "static void SV_LogPlatformAuthConnectRejected( const char *detail ) {"
    )
    callback_log_block = _extract_function_block(
        sv_client, "static void SV_LogSteamServerCallbackLifecycle( const char *stage, const char *detail ) {"
    )
    bootstrap_log_block = _extract_function_block(
        sv_client, "static void SV_LogSteamServerCallbackBootstrapLifecycle( const char *stage, const char *detail ) {"
    )
    connected_block = _extract_function_block(
        sv_client, "static void SV_SteamServerConnectedCallback( void *context, const ql_steam_server_connected_t *event )"
    )
    failure_block = _extract_function_block(
        sv_client, "static void SV_SteamServerConnectFailureCallback( void *context, const ql_steam_server_connect_failure_t *event )"
    )
    disconnected_block = _extract_function_block(
        sv_client, "static void SV_SteamServerDisconnectedCallback( void *context, const ql_steam_server_disconnected_t *event )"
    )
    auth_callback_block = _extract_function_block(
        sv_client,
        "static void SV_SteamServerValidateAuthTicketResponseCallback( void *context, const ql_steam_validate_auth_ticket_response_t *event )",
    )
    p2p_log_block = _extract_function_block(
        sv_client, "static void SV_LogSteamServerP2PSessionRequest( const CSteamID *steamId, const char *state, const char *reason ) {"
    )
    p2p_block = _extract_function_block(
        sv_client, "static void SV_SteamServerP2PSessionRequestCallback( void *context, const ql_steam_p2p_session_request_t *event )"
    )
    init_callbacks_block = _extract_function_block(sv_client, "void SV_SteamServerInitCallbacks( void )")
    direct_connect_block = _extract_function_block(sv_client, "void SV_DirectConnect( netadr_t from )")
    drop_block = _extract_function_block(sv_client, "void SV_DropClient( client_t *drop, const char *reason )")

    assert "provider = SV_GetPlatformAuthProviderLabel();" in compatibility_block
    assert "policy = SV_GetPlatformAuthPolicyLabel();" in compatibility_block
    assert 'Q_strcat( buffer, bufferSize, "provider=" );' in compatibility_block
    assert 'Q_strcat( buffer, bufferSize, " policy=" );' in compatibility_block
    assert 'Com_DPrintf( "Server auth rejected connection via %s [%s]: %s\\n",' in connect_rejected_block
    assert "SV_GetPlatformAuthProviderLabel()" in connect_rejected_block
    assert "SV_GetPlatformAuthPolicyLabel()" in connect_rejected_block
    assert 'Com_Printf( "Steam server callback %s via %s [%s]: %s\\n",' in callback_log_block
    assert "SV_GetSteamServerProviderLabel()" in callback_log_block
    assert "SV_GetSteamServerPolicyLabel()" in callback_log_block
    assert 'Com_DPrintf( "Steam server callback bootstrap %s via %s [%s]: %s\\n",' in bootstrap_log_block
    assert "SV_GetSteamServerProviderLabel()" in bootstrap_log_block
    assert "SV_GetSteamServerPolicyLabel()" in bootstrap_log_block
    assert "SV_BuildPlatformAuthCompatibilityDetail( detailMessage[0] ? detailMessage : NULL, message, sizeof( message ) );" in log_auth_block
    assert "NET_LogAuthTelemetry( NS_SERVER, adr, steamId, label, status, result, outcome, message[0] ? message : NULL );" in log_auth_block
    assert 'SV_LogSteamServerCallbackLifecycle( "connected", "published identity and state refresh" );' in connected_block
    assert "SV_SteamServerPublishIdentity();" in connected_block
    assert "SV_SteamServerUpdatePublishedState( qtrue );" in connected_block
    assert 'SV_LogSteamServerCallbackLifecycle( "connect_failure", "ignored null callback payload" );' in failure_block
    assert 'Com_sprintf( detail, sizeof( detail ), "connect failure result=%d", event->result );' in failure_block
    assert 'SV_LogSteamServerCallbackLifecycle( "connect_failure", detail );' in failure_block
    assert 'SV_LogSteamServerCallbackLifecycle( "disconnected", "ignored null callback payload" );' in disconnected_block
    assert 'Com_sprintf( detail, sizeof( detail ), "disconnected result=%d", event->result );' in disconnected_block
    assert 'SV_LogSteamServerCallbackLifecycle( "disconnected", detail );' in disconnected_block
    assert 'SV_LogSteamServerCallbackLifecycle( "validate_auth_ticket_response", "ignored null callback payload" );' in auth_callback_block
    assert 'Com_sprintf( detail, sizeof( detail ), "ignored auth response for missing client %llu",' in auth_callback_block
    assert 'SV_LogSteamServerCallbackLifecycle( "validate_auth_ticket_response", detail );' in auth_callback_block
    assert 'Com_Printf( "Steam P2P session request %s for %llu via %s [%s]: %s\\n",' in p2p_log_block
    assert "SV_GetSteamServerProviderLabel()" in p2p_log_block
    assert "SV_GetSteamServerPolicyLabel()" in p2p_log_block
    assert "QL_Steamworks_RegisterServerCallbacks( &bindings )" in init_callbacks_block
    assert "bindings.onValidateAuthTicketResponse = SV_SteamServerValidateAuthTicketResponseCallback;" in init_callbacks_block
    assert 'SV_LogSteamServerCallbackBootstrapLifecycle( "unavailable", "register callbacks failed" );' in init_callbacks_block
    assert "static void SV_LogSteamServerCallbackBootstrapLifecycle( const char *stage, const char *detail ) {" in stub_section
    assert 'Com_DPrintf( "Steam server callback bootstrap %s via %s [%s]: %s\\n",' in stub_section
    assert 'SV_LogSteamServerCallbackBootstrapLifecycle( "unavailable", "build-disabled stub" );' in stub_section
    assert "SV_GetSteamServerProviderLabel()" in stub_section
    assert "SV_GetSteamServerPolicyLabel()" in stub_section
    assert "response = k_EAuthSessionResponseVACBanned;" in auth_callback_block
    assert "SV_DropClient( cl, message );" in auth_callback_block
    assert "QL_Steamworks_ServerAcceptP2PSession( &event->remoteId )" in p2p_block
    assert 'SV_LogSteamServerP2PSessionRequest( NULL, "ignored", "null callback payload" );' in p2p_block
    assert 'SV_LogSteamServerP2PSessionRequest( &event->remoteId, "ignored", "client not found" );' in p2p_block
    assert 'SV_LogSteamServerP2PSessionRequest( &event->remoteId, "ignored", "client not authenticated" );' in p2p_block
    assert 'SV_LogSteamServerP2PSessionRequest( &event->remoteId, "failed", "accept call failed" );' in p2p_block
    assert "denied = SV_BeginPlatformAuthSession( newcl, &from );" in direct_connect_block
    assert "SV_LogPlatformAuthConnectRejected( message );" in sv_client
    assert 'Com_DPrintf( "Steam rejected a connection: %s.\\n", denied );' not in direct_connect_block
    assert 'SV_FinalisePlatformAuthState( newcl, qtrue, "accepted" );' not in direct_connect_block
    assert "net_fakevacban" not in direct_connect_block
    assert "SV_EndPlatformAuthSession( drop );" in drop_block


def test_server_steam_stats_owner_reconstructs_retail_gameserverstats_bridge() -> None:
    server_h = (REPO_ROOT / "src/code/server/server.h").read_text(encoding="utf-8")
    sv_client = (REPO_ROOT / "src/code/server/sv_client.c").read_text(encoding="utf-8")
    sv_init = (REPO_ROOT / "src/code/server/sv_init.c").read_text(encoding="utf-8")
    sv_game = (REPO_ROOT / "src/code/server/sv_game.c").read_text(encoding="utf-8")
    steamworks_h = (REPO_ROOT / "src/common/platform/platform_steamworks.h").read_text(encoding="utf-8")
    steamworks = (REPO_ROOT / "src/common/platform/platform_steamworks.c").read_text(encoding="utf-8")
    stub_section = sv_client.split("#else", 1)[1]

    stats_log_block = _extract_function_block(
        sv_client, "static void SV_LogSteamStatsLifecycle( const CSteamID *steamId, const char *stage, const char *detail ) {"
    )
    reset_block = _extract_function_block(sv_client, "static void SV_SteamStats_ResetSession( sv_steam_stats_session_t *session )")
    field_name_block = _extract_function_block(
        sv_client, "static const char *SV_SteamStats_GetFieldName( int statIndex, const char *stage ) {"
    )
    achievement_name_block = _extract_function_block(
        sv_client, "static const char *SV_SteamStats_GetAchievementName( int achievementId, const char *stage ) {"
    )
    client_slot_block = _extract_function_block(
        sv_client, "static client_t *SV_SteamStats_GetClientSlot( int clientNum, const char *stage, const char *subject ) {"
    )
    create_session_block = _extract_function_block(sv_client, "static void SV_SteamStats_CreatePlayerSession( client_t *cl )")
    request_values_block = _extract_function_block(sv_client, "static qboolean SV_SteamStats_RequestCurrentValues( sv_steam_stats_session_t *session )")
    load_stat_block = _extract_function_block(sv_client, "static qboolean SV_SteamStats_LoadFieldValue( sv_steam_stats_session_t *session, int statIndex )")
    load_achievement_block = _extract_function_block(sv_client, "static qboolean SV_SteamStats_LoadAchievement( sv_steam_stats_session_t *session, int achievementId )")
    flush_block = _extract_function_block(sv_client, "static void SV_SteamStats_FlushPendingValues( sv_steam_stats_session_t *session )")
    remove_session_block = _extract_function_block(sv_client, "static void SV_SteamStats_RemovePlayerSession( client_t *cl )")
    requery_block = _extract_function_block(sv_client, "static void SV_SteamStats_RequerySessions( void )")
    add_stat_block = _extract_function_block(sv_client, "void SV_SteamStats_AddFieldValue( int clientNum, int statIndex, int delta )")
    unlock_block = _extract_function_block(sv_client, "void SV_SteamStats_UnlockAchievement( int clientNum, int achievementId )")
    has_block = _extract_function_block(sv_client, "qboolean SV_SteamStats_HasAchievement( int clientNum, int achievementId )")
    should_unlock_block = _extract_function_block(sv_client, "static qboolean SV_SteamStats_ShouldUnlockAchievement( void )")
    begin_auth_block = _extract_function_block(sv_client, "static const char *SV_BeginPlatformAuthSession( client_t *cl, const netadr_t *adr )")
    end_auth_block = _extract_function_block(sv_client, "static void SV_EndPlatformAuthSession( client_t *cl )")
    connected_block = _extract_function_block(
        sv_client, "static void SV_SteamServerConnectedCallback( void *context, const ql_steam_server_connected_t *event )"
    )
    stats_provider_block = _extract_function_block(sv_init, "const char *SV_GetServerStatsProviderLabel( void ) {")
    stats_policy_block = _extract_function_block(sv_init, "const char *SV_GetServerStatsPolicyLabel( void ) {")
    request_block = _extract_function_block(steamworks, "qboolean QL_Steamworks_ServerRequestUserStats( const CSteamID *steamId )")
    get_stat_block = _extract_function_block(
        steamworks, "qboolean QL_Steamworks_ServerGetUserStatInt( const CSteamID *steamId, const char *name, int *outValue )"
    )
    get_achievement_block = _extract_function_block(
        steamworks, "qboolean QL_Steamworks_ServerGetUserAchievement( const CSteamID *steamId, const char *name, qboolean *outAchieved )"
    )
    set_stat_block = _extract_function_block(
        steamworks, "qboolean QL_Steamworks_ServerSetUserStatInt( const CSteamID *steamId, const char *name, int value )"
    )
    set_achievement_block = _extract_function_block(
        steamworks, "qboolean QL_Steamworks_ServerSetUserAchievement( const CSteamID *steamId, const char *name )"
    )
    store_block = _extract_function_block(steamworks, "qboolean QL_Steamworks_ServerStoreUserStats( const CSteamID *steamId )")
    add_bridge_block = _extract_function_block(sv_game, "static void SV_ClientAddSteamStat( int clientNum, int statIndex, int delta )")
    unlock_bridge_block = _extract_function_block(sv_game, "static void SV_ClientUnlockSteamAchievement( int clientNum, int achievementId )")
    has_bridge_block = _extract_function_block(sv_game, "static qboolean SV_ClientHasSteamAchievement( int clientNum, int achievementId )")

    assert "void SV_SteamStats_AddFieldValue( int clientNum, int statIndex, int delta );" in server_h
    assert "void SV_SteamStats_UnlockAchievement( int clientNum, int achievementId );" in server_h
    assert "qboolean SV_SteamStats_HasAchievement( int clientNum, int achievementId );" in server_h
    assert "const char *SV_GetServerStatsProviderLabel( void );" in server_h
    assert "const char *SV_GetServerStatsPolicyLabel( void );" in server_h
    assert "qboolean QL_Steamworks_ServerRequestUserStats( const CSteamID *steamId );" in steamworks_h
    assert "qboolean QL_Steamworks_ServerGetUserStatInt( const CSteamID *steamId, const char *name, int *outValue );" in steamworks_h
    assert "qboolean QL_Steamworks_ServerGetUserAchievement( const CSteamID *steamId, const char *name, qboolean *outAchieved );" in steamworks_h
    assert "qboolean QL_Steamworks_ServerSetUserStatInt( const CSteamID *steamId, const char *name, int value );" in steamworks_h
    assert "qboolean QL_Steamworks_ServerSetUserAchievement( const CSteamID *steamId, const char *name );" in steamworks_h
    assert "qboolean QL_Steamworks_ServerStoreUserStats( const CSteamID *steamId );" in steamworks_h
    assert "SteamGameServerStats" in steamworks
    assert "QL_Steamworks_GetGameServerStatsInterface( void )" in steamworks
    assert "return SV_GetPlatformFeatureProviderLabel( &services->stats );" in stats_provider_block
    assert 'return QL_DescribePlatformFeaturePolicy( &services->stats );' in stats_policy_block
    assert 'Com_DPrintf( "Server stats %s for %llu via %s [%s]: %s\\n",' in stats_log_block
    assert "SV_GetServerStatsProviderLabel()" in stats_log_block
    assert "SV_GetServerStatsPolicyLabel()" in stats_log_block
    assert "vtable[0x00 / 4]" in request_block
    assert "vtable[0x08 / 4]" in get_stat_block
    assert "vtable[0x0c / 4]" in get_achievement_block
    assert "vtable[0x14 / 4]" in set_stat_block
    assert "vtable[0x1c / 4]" in set_achievement_block
    assert "vtable[0x24 / 4]" in store_block
    assert '"wins"' in sv_client
    assert '"AW_MIDAIR"' in sv_client
    assert "static void SV_LogSteamStatsStubLifecycle( const char *stage, const char *detail ) {" in stub_section
    assert 'Com_DPrintf( "Server stats %s via %s [%s]: %s\\n",' in stub_section
    assert "SV_GetServerStatsProviderLabel()" in stub_section
    assert "SV_GetServerStatsPolicyLabel()" in stub_section
    assert 'SV_LogSteamStatsLifecycle( NULL, "session-reset", "ignored reset for null session" );' in reset_block
    assert '"session-reset", "cleared retained session state"' in reset_block
    assert 'lookupStage = stage ? stage : "descriptor-lookup";' in field_name_block
    assert '"ignored stat descriptor lookup for invalid index %d"' in field_name_block
    assert '"ignored stat descriptor lookup for unmapped index %d"' in field_name_block
    assert "SV_LogSteamStatsLifecycle( NULL, lookupStage, detail );" in field_name_block
    assert 'lookupStage = stage ? stage : "descriptor-lookup";' in achievement_name_block
    assert '"ignored achievement descriptor lookup for invalid id %d"' in achievement_name_block
    assert '"ignored achievement descriptor lookup for unmapped id %d"' in achievement_name_block
    assert "SV_LogSteamStatsLifecycle( NULL, lookupStage, detail );" in achievement_name_block
    assert '"%s unavailable for out-of-range client %d"' in client_slot_block
    assert '"%s unavailable for inactive client %d"' in client_slot_block
    assert '"%s unavailable for zombie client %d"' in client_slot_block
    assert '"%s unavailable for client %d without gentity"' in client_slot_block
    assert '"%s unavailable for client %d without steam id"' in client_slot_block
    assert '"%s unavailable for bot-owned client %d"' in client_slot_block
    assert '"%s unavailable for client %d with invalid steam id"' in client_slot_block
    assert "SV_LogSteamStatsLifecycle( NULL, stage, detail );" in client_slot_block
    assert 'QL_Steamworks_ServerSendP2PPacket( &session->steamId, SV_STEAM_STATS_P2P_HELLO, 5, SV_STEAM_STATS_P2P_SEND_RELIABLE, SV_STEAM_STATS_P2P_CHANNEL )' in create_session_block
    assert 'SV_LogSteamStatsLifecycle( NULL, "session-bootstrap", "ignored bootstrap for null client" );' in create_session_block
    assert '"ignored bootstrap for out-of-range client %d"' in create_session_block
    assert '"ignored bootstrap for zombie client %d"' in create_session_block
    assert '"ignored bootstrap for client %d without gentity"' in create_session_block
    assert '"ignored bootstrap for client %d without steam id"' in create_session_block
    assert '"ignored bootstrap for bot-owned client %d"' in create_session_block
    assert '"ignored bootstrap for client %d with invalid steam id"' in create_session_block
    assert 'SV_LogSteamStatsLifecycle( NULL, "session-bootstrap", detail );' in create_session_block
    assert 'SV_LogSteamStatsLifecycle( &session->steamId, "session-bootstrap", "reusing active session" );' in create_session_block
    assert 'SV_LogSteamStatsLifecycle( &session->steamId, "session-bootstrap", "created session" );' in create_session_block
    assert 'SV_LogSteamStatsLifecycle( &session->steamId, "session-bootstrap", "p2p hello send failed" );' in create_session_block
    assert 'SV_LogSteamStatsLifecycle( &session->steamId, "session-bootstrap", "p2p hello sent" );' in create_session_block
    assert 'SV_LogSteamStatsLifecycle( NULL, "request-current-values", "ignored request for null session" );' in request_values_block
    assert 'SV_LogSteamStatsLifecycle( &session->steamId, "request-current-values", "ignored request for inactive session" );' in request_values_block
    assert 'SV_LogSteamStatsLifecycle( NULL, "request-current-values", "ignored request for session without steam id" );' in request_values_block
    assert 'SV_LogSteamStatsLifecycle( &session->steamId, "request-current-values", "request failed" );' in request_values_block
    assert 'SV_LogSteamStatsLifecycle( &session->steamId, "request-current-values", "request issued" );' in request_values_block
    assert '"ignored stat query for null session at index %d"' in load_stat_block
    assert '"ignored stat query for inactive session at index %d"' in load_stat_block
    assert '"ignored stat query for invalid index %d"' in load_stat_block
    assert '"ignored stat query for unmapped index %d"' in load_stat_block
    assert '"stat %s already cached as %d"' in load_stat_block
    assert '"stat %s query failed"' in load_stat_block
    assert '"stat %s loaded as %d"' in load_stat_block
    assert 'SV_SteamStats_GetFieldName( statIndex, "value-query" );' in load_stat_block
    assert 'SV_LogSteamStatsLifecycle( &session->steamId, "value-query", detail );' in load_stat_block
    assert "session->statValue[statIndex] = value + session->pendingStatDelta[statIndex];" in load_stat_block
    assert '"ignored achievement query for null session at id %d"' in load_achievement_block
    assert '"ignored achievement query for inactive session at id %d"' in load_achievement_block
    assert '"ignored achievement query for invalid id %d"' in load_achievement_block
    assert '"ignored achievement query for unmapped id %d"' in load_achievement_block
    assert '"achievement %s already cached as %s"' in load_achievement_block
    assert '"achievement %s query failed"' in load_achievement_block
    assert '"achievement %s loaded as %s"' in load_achievement_block
    assert 'SV_SteamStats_GetAchievementName( achievementId, "value-query" );' in load_achievement_block
    assert 'SV_LogSteamStatsLifecycle( &session->steamId, "value-query", detail );' in load_achievement_block
    assert 'name, session->achievementUnlocked[achievementId] ? "unlocked" : "locked" );' in load_achievement_block
    assert "SV_SteamStats_RequestCurrentValues( session );" in create_session_block
    assert 'SV_LogSteamStatsLifecycle( NULL, "value-flush", "ignored flush for null session" );' in flush_block
    assert 'SV_LogSteamStatsLifecycle( &session->steamId, "value-flush", "ignored flush for inactive session" );' in flush_block
    assert 'SV_LogSteamStatsLifecycle( NULL, "value-flush", "ignored flush for session without steam id" );' in flush_block
    assert 'SV_LogSteamStatsLifecycle( &session->steamId, "value-flush", "no pending stat or achievement updates" );' in flush_block
    assert '"stat %s unavailable during flush"' in flush_block
    assert '"stat %s publish failed"' in flush_block
    assert '"achievement %s publish failed"' in flush_block
    assert 'SV_SteamStats_GetFieldName( i, "value-flush" );' in flush_block
    assert 'SV_SteamStats_GetAchievementName( i, "value-flush" );' in flush_block
    assert '"retained %d stat field(s) and %d achievement(s) after publish failure"' in flush_block
    assert 'SV_LogSteamStatsLifecycle( &session->steamId, "value-flush", "store request failed" );' in flush_block
    assert '"stored %d stat field(s) and %d achievement(s)"' in flush_block
    assert 'SV_LogSteamStatsLifecycle( &session->steamId, "value-flush", detail );' in flush_block
    assert "QL_Steamworks_ServerStoreUserStats( &session->steamId )" in flush_block
    assert '"session teardown skipped for inactive client %d"' in remove_session_block
    assert '"cleared session for client %d"' in remove_session_block
    assert 'SV_LogSteamStatsLifecycle( NULL, "session-teardown", detail );' in remove_session_block
    assert 'SV_LogSteamStatsLifecycle( &steamId, "session-teardown", detail );' in remove_session_block
    assert "SV_SteamStats_FlushPendingValues( session );" in remove_session_block
    assert 'SV_LogSteamStatsLifecycle( &session->steamId, "session-requery", "backend reconnected; request reset" );' in requery_block
    assert "SV_SteamStats_RequestCurrentValues( session );" in requery_block
    assert 'Cvar_VariableStringBuffer( "g_gameState", gameState, sizeof( gameState ) );' in should_unlock_block
    assert '!Q_stricmp( gameState, "IN_PROGRESS" )' in should_unlock_block
    assert 'Cvar_VariableIntegerValue( "g_training" ) != 0' in should_unlock_block
    assert 'Cvar_VariableIntegerValue( "practiceflags" ) != 0' in should_unlock_block
    assert "SV_SteamStats_CreatePlayerSession( cl );" in begin_auth_block
    assert "SV_SteamStats_RemovePlayerSession( cl );" in end_auth_block
    assert "SV_SteamStats_RequerySessions();" in connected_block
    assert "session->pendingStatDelta[statIndex] += delta;" in add_stat_block
    assert "session->statDirty[statIndex] = qtrue;" in add_stat_block
    assert '"ignored stat index %d delta %d for client %d"' in add_stat_block
    assert '"stat %s session unavailable for client %d"' in add_stat_block
    assert '"stat %s baseline unavailable; queuing delta %d for client %d"' in add_stat_block
    assert 'SV_SteamStats_GetFieldName( statIndex, "field-delta" );' in add_stat_block
    assert 'SV_SteamStats_GetClientSlot( clientNum, "field-delta", subject );' in add_stat_block
    assert 'SV_LogSteamStatsLifecycle( &session->steamId, "field-delta", detail );' in add_stat_block
    assert 'SV_LogSteamStatsStubLifecycle( "field-delta", detail );' in stub_section
    assert '"ignored stat index %d delta %d for client %d"' in stub_section
    assert "SV_SteamStats_ShouldUnlockAchievement()" in unlock_block
    assert '"ignored achievement %d for client %d"' in unlock_block
    assert '"achievement %s blocked by gameplay gate for client %d"' in unlock_block
    assert '"achievement %s session unavailable for client %d"' in unlock_block
    assert '"achievement %s already unlocked for client %d"' in unlock_block
    assert '"queued achievement %s unlock for client %d"' in unlock_block
    assert 'SV_SteamStats_GetAchievementName( achievementId, "achievement-unlock" );' in unlock_block
    assert 'SV_LogSteamStatsLifecycle( NULL, "achievement-unlock", detail );' in unlock_block
    assert 'SV_LogSteamStatsLifecycle( &session->steamId, "achievement-unlock", detail );' in unlock_block
    assert "session->achievementDirty[achievementId] = qtrue;" in unlock_block
    assert "SV_SteamStats_FlushPendingValues( session );" in unlock_block
    assert '"query unavailable for achievement %d on client %d"' in has_block
    assert '"achievement %s ownership is %s for client %d"' in has_block
    assert 'SV_SteamStats_GetAchievementName( achievementId, "achievement-query" );' in has_block
    assert 'SV_LogSteamStatsLifecycle( &session->steamId, "achievement-query", detail );' in has_block
    assert 'SV_SteamStats_GetClientSlot( clientNum, "achievement-query", subject );' in has_block
    assert "return session->achievementUnlocked[achievementId] ? qtrue : qfalse;" in has_block
    assert 'SV_LogSteamStatsStubLifecycle( "achievement-unlock", detail );' in stub_section
    assert 'SV_LogSteamStatsStubLifecycle( "achievement-query", detail );' in stub_section
    assert '"ignored achievement %d for client %d"' in stub_section
    assert '"query unavailable for achievement %d on client %d"' in stub_section
    assert "SV_SteamStats_AddFieldValue( clientNum, statIndex, delta );" in add_bridge_block
    assert "SV_SteamStats_UnlockAchievement( clientNum, achievementId );" in unlock_bridge_block
    assert "return SV_SteamStats_HasAchievement( clientNum, achievementId );" in has_bridge_block


def test_qagame_connect_auth_bridge_reconstructs_engine_owned_pending_contract() -> None:
    g_client = (REPO_ROOT / "src/code/game/g_client.c").read_text(encoding="utf-8")
    connect_block = _extract_function_block(g_client, "char *ClientConnect( int clientNum, qboolean firstTime, qboolean isBot )")
    auth_bridge_block = _extract_function_block(
        g_client, "static char *G_RunPlatformAuthChecks( int clientNum, char *userinfo, qboolean firstTime, qboolean isBot, gclient_t *client )"
    )

    assert "if ( firstTime && !isBot ) {" in connect_block
    assert "if ( !firstTime && !isBot ) {" not in connect_block
    assert "G_BuildSteamAuthToken( userinfo, token, sizeof( token ) );" in auth_bridge_block
    assert "QL_InitAuthCredential( &credential );" in auth_bridge_block
    assert "QL_ParsePlatformToken( token, QL_AUTH_CREDENTIAL_STEAM, &credential )" in auth_bridge_block
    assert "G_WritePlatformAuthUserinfo( clientNum, userinfo, G_GetAuthResultString( QL_AUTH_RESULT_PENDING )," in auth_bridge_block
    assert "G_GetAuthOutcomeString( QL_AUTH_OUTCOME_RETRY )" in auth_bridge_block
    assert "QL_RequestExternalAuth" not in auth_bridge_block


def test_ui_and_cgame_native_import_slabs_leave_unrecovered_retail_gaps_null() -> None:
    cl_ui = (REPO_ROOT / "src/code/client/cl_ui.c").read_text(encoding="utf-8")
    cl_cgame = (REPO_ROOT / "src/code/client/cl_cgame.c").read_text(encoding="utf-8")

    ui_init_block = _extract_function_block(cl_ui, "static void CL_InitUIImports( void )")
    cgame_init_block = _extract_function_block(cl_cgame, "static void CL_InitCGameImports( void )")

    assert "Com_Memset( ql_ui_imports, 0, sizeof( ql_ui_imports ) );" in ui_init_block
    assert "ql_ui_imports[UI_QL_IMPORT_UNUSED_83] = (ql_import_f)QL_UI_trap_UpdateAdvert;" in ui_init_block
    assert "ql_ui_imports[UI_QL_IMPORT_UNUSED_85] = (ql_import_f)QL_UI_trap_Unused85;" in ui_init_block
    assert "ql_ui_imports[UI_QL_IMPORT_LAUNCHER_READSCREENSHOT] = (ql_import_f)QL_UI_trap_Launcher_ReadScreenshot;" in ui_init_block

    assert "Com_Memset( ql_cgame_imports, 0, sizeof( ql_cgame_imports ) );" in cgame_init_block
    assert "ql_cgame_imports[CG_QL_IMPORT_GET_AVATAR_IMAGE_HANDLE] = (ql_import_f)QL_CG_trap_GetAvatarImageHandle;" in cgame_init_block
    assert "ql_cgame_imports[CG_QL_IMPORT_COMPAT_ACOS] = (ql_import_f)QL_CG_trap_ACos;" in cgame_init_block


def test_module_side_syscall_wrappers_normalize_qboolean_contracts() -> None:
    ui_syscalls = (REPO_ROOT / "src/code/ui/ui_syscalls.c").read_text(encoding="utf-8")
    cg_syscalls = (REPO_ROOT / "src/code/cgame/cg_syscalls.c").read_text(encoding="utf-8")
    g_syscalls = (REPO_ROOT / "src/code/game/g_syscalls.c").read_text(encoding="utf-8")

    assert "return syscall( UI_S_REGISTERSOUND, sample, compressed ? qtrue : qfalse );" in ui_syscalls
    assert "return syscall( UI_KEY_ISDOWN, keynum ) ? qtrue : qfalse;" in ui_syscalls
    assert "return syscall( UI_KEY_GETOVERSTRIKEMODE ) ? qtrue : qfalse;" in ui_syscalls
    assert "syscall( UI_KEY_SETOVERSTRIKEMODE, state ? qtrue : qfalse );" in ui_syscalls
    assert "syscall( UI_LAN_MARKSERVERVISIBLE, source, n, visible ? qtrue : qfalse );" in ui_syscalls
    assert "return syscall( UI_LAN_UPDATEVISIBLEPINGS, source ) ? qtrue : qfalse;" in ui_syscalls
    assert "return syscall( UI_VERIFY_CDKEY, key, chksum ) ? qtrue : qfalse;" in ui_syscalls
    assert "return ((int (QDECL *)( int, int ))import)( x, y ) ? qtrue : qfalse;" in ui_syscalls
    assert "return ((int (QDECL *)( int *, int * ))import)( x, y ) ? qtrue : qfalse;" in ui_syscalls
    assert "return ((int (QDECL *)( int ))import)( appId ) ? qtrue : qfalse;" in ui_syscalls
    assert "forceColor ? qtrue : qfalse" in ui_syscalls

    assert "syscall( CG_S_CLEARLOOPINGSOUNDS, killall ? qtrue : qfalse );" in cg_syscalls
    assert "return syscall( CG_S_REGISTERSOUND, sample, compressed ? qtrue : qfalse );" in cg_syscalls
    assert "return syscall( CG_GETSNAPSHOT, snapshotNumber, snapshot ) ? qtrue : qfalse;" in cg_syscalls
    assert "return syscall( CG_GETSERVERCOMMAND, serverCommandNumber ) ? qtrue : qfalse;" in cg_syscalls
    assert "return syscall( CG_GETUSERCMD, cmdNumber, ucmd ) ? qtrue : qfalse;" in cg_syscalls
    assert "return syscall( CG_KEY_ISDOWN, keynum ) ? qtrue : qfalse;" in cg_syscalls
    assert "return syscall( CG_KEY_GETOVERSTRIKEMODE ) ? qtrue : qfalse;" in cg_syscalls
    assert "syscall( CG_KEY_SETOVERSTRIKEMODE, state ? qtrue : qfalse );" in cg_syscalls
    assert "return syscall( CG_GET_ENTITY_TOKEN, buffer, bufferSize ) ? qtrue : qfalse;" in cg_syscalls
    assert "return syscall( CG_R_INPVS, p1, p2 ) ? qtrue : qfalse;" in cg_syscalls

    assert "return syscall( G_STEAMID_QUERY, clientNum, steamIdLow, steamIdHigh ) ? qtrue : qfalse;" in g_syscalls
    assert "return syscall( G_STEAM_AUTH_VALIDATE, clientNum ) ? qtrue : qfalse;" in g_syscalls
    assert "return ((qboolean (QDECL *)( int, int ))import)( clientNum, achievementId ) ? qtrue : qfalse;" in g_syscalls
    assert "return syscall( G_RANK_CHECK_INIT ) ? qtrue : qfalse;" in g_syscalls
    assert "return syscall( G_RANK_ACTIVE ) ? qtrue : qfalse;" in g_syscalls
    assert "syscall( G_RANK_REPORT_INT, index1, index2, key, value, accum ? qtrue : qfalse );" in g_syscalls
    assert "return syscall( G_IN_PVS, p1, p2 ) ? qtrue : qfalse;" in g_syscalls
    assert "return syscall( G_IN_PVS_IGNORE_PORTALS, p1, p2 ) ? qtrue : qfalse;" in g_syscalls
    assert "syscall( G_ADJUST_AREA_PORTAL_STATE, ent, open ? qtrue : qfalse );" in g_syscalls
    assert "return syscall( G_AREAS_CONNECTED, area1, area2 ) ? qtrue : qfalse;" in g_syscalls
    assert "return syscall( G_ENTITY_CONTACT, mins, maxs, ent ) ? qtrue : qfalse;" in g_syscalls
    assert "return syscall( G_ENTITY_CONTACTCAPSULE, mins, maxs, ent ) ? qtrue : qfalse;" in g_syscalls
    assert "return syscall( G_GET_ENTITY_TOKEN, buffer, bufferSize ) ? qtrue : qfalse;" in g_syscalls


def test_cgame_native_tail_exports_use_explicit_integer_contract_wrappers() -> None:
    cg_main = (REPO_ROOT / "src/code/cgame/cg_main.c").read_text(encoding="utf-8")
    vm = (REPO_ROOT / "src/code/qcommon/vm.c").read_text(encoding="utf-8")

    assert "return CG_NativeGetChatFieldY();" in cg_main
    assert "return CG_NativeGetChatFieldPixelWidth();" in cg_main
    assert "return CG_NativeSetClientSpeakingState( arg0, arg1 );" in cg_main
    assert "static int CG_NativeGetChatFieldY( void ) {\n\treturn (int)CG_GetChatFieldY();\n}" in cg_main
    assert "static int CG_NativeGetChatFieldPixelWidth( void ) {\n\treturn (int)CG_GetChatFieldPixelWidth();\n}" in cg_main
    assert "static int CG_NativeSetClientSpeakingState( int clientNum, int speaking ) {\n\treturn (int)(intptr_t)CG_SetClientSpeakingState( clientNum, speaking );\n}" in cg_main
    assert "[CG_NATIVE_EXPORT_GET_CHAT_FIELD_Y] = CG_NativeGetChatFieldY," in cg_main
    assert "[CG_NATIVE_EXPORT_GET_CHAT_FIELD_PIXEL_WIDTH] = CG_NativeGetChatFieldPixelWidth," in cg_main
    assert "[CG_NATIVE_EXPORT_SET_CLIENT_SPEAKING_STATE] = CG_NativeSetClientSpeakingState" in cg_main
    assert "return ((int (QDECL *)( void ))exportFunc)();" in vm
    assert "return ((int (QDECL *)( int, int ))exportFunc)( args[0], args[1] );" in vm


def test_ui_native_key_event_export_uses_explicit_slot_wrapper() -> None:
    ui_main = (REPO_ROOT / "src/code/ui/ui_main.c").read_text(encoding="utf-8")
    vm = (REPO_ROOT / "src/code/qcommon/vm.c").read_text(encoding="utf-8")

    assert "static void UI_NativeKeyEvent( int key, qboolean down, int time ) {\n\t(void)time;\n\t_UI_KeyEvent( key, down );\n}" in ui_main
    assert "UI_NativeKeyEvent( arg0, arg1 ? qtrue : qfalse, arg2 );" in ui_main
    assert "[UI_NATIVE_EXPORT_KEY_EVENT] = UI_NativeKeyEvent," in ui_main
    assert "((void (QDECL *)( int, qboolean, int ))exportFunc)( args[0], VM_NormalizeQbooleanArg( args[1] ), args[2] );" in vm


def test_module_native_export_qboolean_slots_use_explicit_wrappers() -> None:
    ui_main = (REPO_ROOT / "src/code/ui/ui_main.c").read_text(encoding="utf-8")
    cg_main = (REPO_ROOT / "src/code/cgame/cg_main.c").read_text(encoding="utf-8")
    g_main = (REPO_ROOT / "src/code/game/g_main.c").read_text(encoding="utf-8")

    assert "static void UI_NativeInit( qboolean inGameLoad ) {\n\t_UI_Init( inGameLoad );\n}" in ui_main
    assert "static void UI_NativeDrawConnectScreen( qboolean overlay ) {\n\tUI_DrawConnectScreen( overlay );\n}" in ui_main
    assert "UI_NativeInit( arg0 ? qtrue : qfalse );" in ui_main
    assert "UI_NativeDrawConnectScreen( arg0 ? qtrue : qfalse );" in ui_main
    assert "[UI_NATIVE_EXPORT_INIT] = UI_NativeInit," in ui_main
    assert "[UI_NATIVE_EXPORT_DRAW_CONNECT_SCREEN] = UI_NativeDrawConnectScreen," in ui_main

    assert "static void CG_NativeDrawActiveFrame( int serverTime, stereoFrame_t stereoView, qboolean demoPlayback ) {\n\tCG_DrawActiveFrame( serverTime, stereoView, demoPlayback );\n}" in cg_main
    assert "static void CG_NativeKeyEvent( int key, qboolean down ) {\n\tCG_KeyEvent( key, down );\n}" in cg_main
    assert "CG_NativeDrawActiveFrame( arg0, arg1, arg2 ? qtrue : qfalse );" in cg_main
    assert "CG_NativeKeyEvent( arg0, arg1 ? qtrue : qfalse );" in cg_main
    assert "[CG_NATIVE_EXPORT_DRAW_ACTIVE_FRAME] = CG_NativeDrawActiveFrame," in cg_main
    assert "[CG_NATIVE_EXPORT_KEY_EVENT] = CG_NativeKeyEvent," in cg_main

    assert "static void G_NativeInit( int levelTime, int randomSeed, qboolean restart ) {\n\tG_InitGame( levelTime, randomSeed, restart );\n}" in g_main
    assert "static void G_NativeShutdown( qboolean restart ) {\n\tG_ShutdownGame( restart );\n}" in g_main
    assert "static const char *G_NativeClientConnect( int clientNum, qboolean firstTime, qboolean isBot ) {\n\treturn ClientConnect( clientNum, firstTime, isBot );\n}" in g_main
    assert "G_NativeInit( arg0, arg1, arg2 ? qtrue : qfalse );" in g_main
    assert "G_NativeShutdown( arg0 ? qtrue : qfalse );" in g_main
    assert "return (int)(intptr_t)G_NativeClientConnect( arg0, arg1 ? qtrue : qfalse, arg2 ? qtrue : qfalse );" in g_main
    assert "[GAME_NATIVE_EXPORT_INIT] = G_NativeInit," in g_main
    assert "[GAME_NATIVE_EXPORT_SHUTDOWN] = G_NativeShutdown," in g_main
    assert "[GAME_NATIVE_EXPORT_CLIENT_CONNECT] = G_NativeClientConnect," in g_main


def test_server_spawn_and_shutdown_reconstruct_retail_steam_identity_and_heartbeat_control() -> None:
    sv_init = (REPO_ROOT / "src/code/server/sv_init.c").read_text(encoding="utf-8")

    identity_log_block = _extract_function_block(
        sv_init, "static void SV_LogSteamServerIdentityLifecycle( const char *stage, const char *detail ) {"
    )
    masters_block = _extract_function_block(sv_init, "static qboolean SV_SteamServerHasConfiguredMasters( void )")
    publish_block = _extract_function_block(sv_init, "void SV_SteamServerPublishIdentity( void )")
    spawn_block = _extract_function_block(sv_init, "void SV_SpawnServer( char *server, qboolean killBots )")
    init_block = _extract_function_block(sv_init, "void SV_Init (void)")
    shutdown_block = _extract_function_block(sv_init, "void SV_Shutdown( char *finalmsg )")

    assert 'Cvar_Get ("sv_referencedSteamworks", "", CVAR_ROM );' in init_block
    assert "SV_SteamServerInitCallbacks();" in init_block
    assert 'Com_DPrintf( "Steam server identity %s via %s [%s]: %s\\n",' in identity_log_block
    assert "SV_GetSteamServerProviderLabel()" in identity_log_block
    assert "SV_GetSteamServerPolicyLabel()" in identity_log_block
    assert "if ( sv_master[i] && sv_master[i]->string[0] ) {" in masters_block
    assert "QL_Steamworks_ServerGetSteamID( &steamIdLow, &steamIdHigh )" in publish_block
    assert 'SV_LogSteamServerIdentityLifecycle( "unavailable", "server steam ID unavailable" );' in publish_block
    assert "referencedSteamworks = FS_ReferencedSteamworks();" in publish_block
    assert "SV_SetConfigstring( 0x2ca, steamIdString );" in publish_block
    assert 'Cvar_Set( "sv_referencedSteamworks", referencedSteamworks );' in publish_block
    assert "SV_SetConfigstring( 0x2cb, referencedSteamworks );" in publish_block
    assert 'Com_sprintf( detail, sizeof( detail ), "published id=%s referenced=%d",' in publish_block
    assert 'SV_LogSteamServerIdentityLifecycle( "published", detail );' in publish_block
    assert "SV_RefreshPlatformServiceCvars();" in spawn_block
    assert "SV_SteamServerPublishIdentity();" in spawn_block
    assert "QL_Steamworks_ServerEnableHeartbeats( SV_SteamServerHasConfiguredMasters() );" in spawn_block
    assert "QL_Steamworks_ServerSetKeyValuesFromInfoString( serverInfo );" in spawn_block
    assert "QL_Steamworks_ServerEnableHeartbeats( qfalse );" in shutdown_block
    assert "QL_Steamworks_ServerShutdown();" in shutdown_block
    assert shutdown_block.index("QL_Steamworks_ServerEnableHeartbeats( qfalse );") < shutdown_block.index("QL_Steamworks_ServerShutdown();")


def test_server_zmq_runtime_reconstructs_retail_publication_and_rcon_owners() -> None:
    server_h = (REPO_ROOT / "src/code/server/server.h").read_text(encoding="utf-8")
    sv_init = (REPO_ROOT / "src/code/server/sv_init.c").read_text(encoding="utf-8")
    sv_main = (REPO_ROOT / "src/code/server/sv_main.c").read_text(encoding="utf-8")
    sv_game = (REPO_ROOT / "src/code/server/sv_game.c").read_text(encoding="utf-8")
    sv_zmq = (REPO_ROOT / "src/code/server/sv_zmq.c").read_text(encoding="utf-8")
    common = (REPO_ROOT / "src/code/qcommon/common.c").read_text(encoding="utf-8")

    init_block = _extract_function_block(sv_init, "void SV_Init (void)")
    spawn_block = _extract_function_block(sv_init, "void SV_SpawnServer( char *server, qboolean killBots )")
    shutdown_block = _extract_function_block(sv_init, "void SV_Shutdown( char *finalmsg )")
    frame_block = _extract_function_block(sv_main, "void SV_Frame( int msec )")
    submit_block = _extract_function_block(sv_game, "static void SV_SubmitMatchReport( void *report )")
    event_block = _extract_function_block(
        sv_game, "static void SV_ReportPlayerEvent( uint32_t steamIdLow, uint32_t steamIdHigh, const void *clientStats, const char *eventName, void *payload )"
    )
    register_block = _extract_function_block(sv_zmq, "void Zmq_RegisterCvarsAndInitRcon( void )")
    apply_passwords_block = _extract_function_block(sv_zmq, "static void idZMQ_ApplyPasswords( qboolean rconModeChanged, qboolean statsModeChanged )")
    update_passwords_block = _extract_function_block(sv_zmq, "void Zmq_UpdatePasswords( void )")
    init_publisher_block = _extract_function_block(sv_zmq, "void Zmq_InitStatsPublisher( void )")
    shutdown_runtime_block = _extract_function_block(sv_zmq, "void Zmq_ShutdownRuntime( void )")
    broadcast_block = _extract_function_block(sv_zmq, "void Zmq_BroadcastRconOutput( const char *message )")
    pump_block = _extract_function_block(sv_zmq, "void Zmq_PumpRcon( void )")
    printf_block = _extract_function_block(common, "void QDECL Com_Printf( const char *fmt, ... )")
    com_shutdown_block = _extract_function_block(common, "void Com_Shutdown (void)")

    assert "void Zmq_RegisterCvarsAndInitRcon( void );" in server_h
    assert "void Zmq_UpdatePasswords( void );" in server_h
    assert "void Zmq_InitStatsPublisher( void );" in server_h
    assert "void Zmq_ShutdownStatsPublisher( void );" in server_h
    assert "void Zmq_ShutdownRuntime( void );" in server_h
    assert "void Zmq_PumpRcon( void );" in server_h
    assert "void Zmq_BroadcastRconOutput( const char *message );" in server_h
    assert "void Zmq_SubmitMatchReport( const void *report );" in server_h
    assert "void Zmq_ReportPlayerEvent( uint32_t steamIdLow, uint32_t steamIdHigh, const void *clientStats, const char *eventName, const void *payload );" in server_h

    assert 'Cvar_Get( "zmq_rcon_enable", "0", CVAR_ARCHIVE );' in register_block
    assert 'Cvar_Get( "zmq_stats_enable", "0", CVAR_ARCHIVE );' in register_block
    assert 'Cvar_Get( "zmq_rcon_ip", "0.0.0.0", CVAR_ARCHIVE );' in register_block
    assert 'Cvar_Get( "zmq_rcon_port", "28960", CVAR_ARCHIVE );' in register_block
    assert 'Cvar_Get( "zmq_rcon_password", "", CVAR_ARCHIVE | CVAR_PROTECTED );' in register_block
    assert 'Cvar_Get( "zmq_stats_password", "", CVAR_ARCHIVE | CVAR_PROTECTED );' in register_block
    assert "idZMQ_EnsureRconSocket();" in register_block
    assert 'FS_FOpenFileWrite( QL_ZMQ_PASSFILE );' in sv_zmq
    assert 'Com_sprintf( line, sizeof( line ), "stats_stats=%s\\n", s_zmq.statsPassword );' in sv_zmq
    assert 'Com_sprintf( line, sizeof( line ), "rcon_rcon=%s\\n", s_zmq.rconPassword );' in sv_zmq
    assert 'Com_Printf( "Failed to open %s\\n", QL_ZMQ_PASSFILE );' in sv_zmq
    assert "idZMQ_ApplyPasswords( qfalse, qfalse );" in update_passwords_block
    assert "idZMQ_ApplyPasswords( rconModeChanged, statsModeChanged );" in update_passwords_block
    assert "idZMQ_CloseSocket( &s_zmq.rconSocket );" in apply_passwords_block
    assert "idZMQ_CloseSocket( &s_zmq.pubSocket );" in apply_passwords_block
    assert "idZMQ_CloseAuthSocket();" in apply_passwords_block
    assert 'Com_Printf( "zmq stats and rcon passwords updated\\n" );' in update_passwords_block
    assert "idZMQ_EnsureStatsPublisher();" in init_publisher_block
    assert 'idZMQ_Publish( "MATCH_REPORT", (const char *)report );' in sv_zmq
    assert 'idZMQ_Publish( eventName && eventName[0] ? eventName : "UNKNOWN_EVENT", (const char *)payload );' in sv_zmq
    assert 'idZMQ_TrySetSocketString( socket, QL_ZMQ_ZAP_DOMAIN, "rcon" );' in sv_zmq
    assert 'idZMQ_TrySetSocketString( socket, QL_ZMQ_ZAP_DOMAIN, "stats" );' in sv_zmq
    assert 'idZMQ_TrySetSocketInt( socket, QL_ZMQ_PLAIN_SERVER, s_zmq.rconPassword[0] ? 1 : 0 );' in sv_zmq
    assert 'idZMQ_TrySetSocketInt( socket, QL_ZMQ_PLAIN_SERVER, s_zmq.statsPassword[0] ? 1 : 0 );' in sv_zmq
    assert 'Com_Printf( "zmq RCON socket: %s\\n", s_zmq.rconEndpoint );' in sv_zmq
    assert 'Com_Printf( "zmq PUB socket: %s\\n", s_zmq.statsEndpoint );' in sv_zmq
    assert 'Com_Printf( "zmq RCON socket error, bind failed: %s\\n", idZMQ_LastErrorString() );' in sv_zmq
    assert 'Com_Printf( "zmq PUB socket error, bind failed: %s\\n", idZMQ_LastErrorString() );' in sv_zmq
    assert "idZMQ_PumpAuthSocket();" in pump_block
    assert "if ( s_zmq.zmq_poll( &item, 1, 0 ) <= 0 || !( item.revents & QL_ZMQ_POLLIN ) ) {" in pump_block
    assert "while ( s_zmq.zmq_poll( &item, 1, 0 ) > 0 && ( item.revents & QL_ZMQ_POLLIN ) ) {" not in pump_block
    assert 'Com_Printf( "zmq RCON client connected: %s\\n", peer->label );' in pump_block
    assert 'Com_Printf( "zmq RCON command from %s: %s\\n", peer->label, command );' in pump_block
    assert 'Com_Printf( "zmq RCON client disconnected: %s\\n", peer->label );' in broadcast_block
    assert 'Com_sprintf( buffer, bufferSize, "{\\"TYPE\\":\\"%s\\",\\"DATA\\":%s}\\n", type, payload );' in sv_zmq
    assert 'Com_sprintf( buffer, bufferSize, "{\\"TYPE\\":\\"%s\\",\\"DATA\\":null}\\n", type );' in sv_zmq
    assert 's_zmq.statsTranscript = FS_FOpenFileWrite( QL_ZMQ_STATS_TRANSCRIPT );' in sv_zmq
    assert "idZMQ_CloseAuthSocket();" in shutdown_runtime_block
    assert "QL_ZMQ_IMMEDIATE" not in sv_zmq
    assert "QL_ZMQ_ROUTER_HANDOVER" not in sv_zmq
    assert "Zmq_RegisterCvarsAndInitRcon();" in init_block
    assert "Zmq_InitStatsPublisher();" in spawn_block
    assert spawn_block.index("QL_Steamworks_ServerSetKeyValuesFromInfoString( serverInfo );") < spawn_block.index("Zmq_InitStatsPublisher();")
    assert "Zmq_ShutdownStatsPublisher();" in shutdown_block
    assert shutdown_block.index("SV_ShutdownGameProgs();") < shutdown_block.index("Zmq_ShutdownStatsPublisher();")
    assert "Zmq_UpdatePasswords();" in frame_block
    assert "Zmq_PumpRcon();" in frame_block
    assert frame_block.index("SV_SteamServerNetworkingFrame();") < frame_block.index("Zmq_UpdatePasswords();")
    assert frame_block.index("Zmq_UpdatePasswords();") < frame_block.index("Zmq_PumpRcon();")
    assert "Zmq_SubmitMatchReport( report );" in submit_block
    assert "Zmq_ReportPlayerEvent( steamIdLow, steamIdHigh, clientStats, eventName, payload );" in event_block
    assert "Zmq_BroadcastRconOutput( msg );" in printf_block
    assert "Zmq_ShutdownRuntime();" in com_shutdown_block
    assert "idZMQ_ClearRconPeers();" in shutdown_runtime_block
    assert "idZMQ_UnloadLibrary();" in shutdown_runtime_block


def test_server_rankings_policy_lane_stays_explicit_and_per_server() -> None:
    server_h = (REPO_ROOT / "src/code/server/server.h").read_text(encoding="utf-8")
    sv_init = (REPO_ROOT / "src/code/server/sv_init.c").read_text(encoding="utf-8")
    sv_main = (REPO_ROOT / "src/code/server/sv_main.c").read_text(encoding="utf-8")
    sv_rankings = (REPO_ROOT / "src/code/server/sv_rankings.c").read_text(encoding="utf-8")

    init_block = _extract_function_block(sv_init, "void SV_Init (void)")
    begin_block = _extract_function_block(sv_rankings, "void SV_RankBegin( char *gamekey )")
    check_init_block = _extract_function_block(sv_rankings, "qboolean SV_RankCheckInit( void )")
    publish_disabled_block = _extract_function_block(sv_rankings, "static void SV_RankPublishDisabledState( void )")
    log_disabled_block = _extract_function_block(sv_rankings, "static void SV_RankLogDisabledState( void )")

    assert "extern\tcvar_t\t*sv_enableRankings;" in server_h
    assert "extern\tcvar_t\t*sv_rankingsActive;" in server_h
    assert "extern\tcvar_t\t*sv_leagueName;" in server_h
    assert "const char *SV_GetRankingsProviderLabel( void );" in server_h
    assert "const char *SV_GetRankingsPolicyLabel( void );" in server_h
    assert "void SV_RefreshRankingsPolicyCvars( void );" in server_h
    assert "cvar_t\t*sv_enableRankings;" in sv_main
    assert "cvar_t\t*sv_rankingsActive;" in sv_main
    assert "cvar_t\t*sv_leagueName;" in sv_main
    assert 'sv_enableRankings = Cvar_Get ("sv_enableRankings", "0", CVAR_SERVERINFO | CVAR_ARCHIVE );' in init_block
    assert 'sv_rankingsActive = Cvar_Get ("sv_rankingsActive", "0", CVAR_SERVERINFO );' in init_block
    assert 'sv_leagueName = Cvar_Get ("sv_leagueName", "", CVAR_ARCHIVE );' in init_block
    assert 'Cvar_Get ("sv_rankingsProvider", "Unavailable", CVAR_ROM );' in init_block
    assert 'Cvar_Get ("sv_rankingsPolicy", "compatibility-unavailable", CVAR_ROM );' in init_block
    assert "SV_RefreshRankingsPolicyCvars();" in sv_init

    assert "static qboolean\ts_rankings_stub_announced = qfalse;" in sv_rankings
    assert "static int\t\ts_rankings_stub_server_id = -1;" in sv_rankings
    assert 'const char *SV_GetRankingsProviderLabel( void ) {' in sv_rankings
    assert 'return "Build-disabled (QL_ENABLE_RANKINGS=0)";' in sv_rankings
    assert 'const char *SV_GetRankingsPolicyLabel( void ) {' in sv_rankings
    assert 'return "compatibility-disabled (QL_ENABLE_RANKINGS=0)";' in sv_rankings
    assert 'void SV_RefreshRankingsPolicyCvars( void ) {' in sv_rankings
    assert 'Cvar_Set( "sv_rankingsProvider", SV_GetRankingsProviderLabel() );' in sv_rankings
    assert 'Cvar_Set( "sv_rankingsPolicy", SV_GetRankingsPolicyLabel() );' in sv_rankings
    assert "SV_RefreshRankingsPolicyCvars();" in publish_disabled_block
    assert 'Com_Printf( "Rankings disabled by build policy (QL_ENABLE_RANKINGS=0); exposing retained compatibility surface only (%s [%s]).\\n",' in log_disabled_block
    assert 'Cvar_Set( "sv_rankingsActive", "0" );' in publish_disabled_block
    assert "SV_RankLogDisabledState();" in begin_block
    assert "if ( sv_enableRankings && sv_enableRankings->integer != 0 ) {" in begin_block
    assert 'Com_Printf( "Rankings requested but build disabled (QL_ENABLE_RANKINGS=0); forcing sv_enableRankings back to 0 (%s [%s]).\\n",' in begin_block
    assert 'Cvar_Set( "sv_enableRankings", "0" );' in begin_block
    assert "SV_RankPublishDisabledState();" in begin_block
    assert "s_rankings_stub_server_id = sv.serverId;" in begin_block
    assert "return s_rankings_stub_server_id == sv.serverId ? qtrue : qfalse;" in check_init_block


def test_server_control_plane_cvars_restore_retail_runtime_owners() -> None:
	server_h = (REPO_ROOT / "src/code/server/server.h").read_text(encoding="utf-8")
	qcommon = (REPO_ROOT / "src/code/qcommon/qcommon.h").read_text(encoding="utf-8")
	sv_init = (REPO_ROOT / "src/code/server/sv_init.c").read_text(encoding="utf-8")
	sv_main = (REPO_ROOT / "src/code/server/sv_main.c").read_text(encoding="utf-8")
	common = (REPO_ROOT / "src/code/qcommon/common.c").read_text(encoding="utf-8")
	sv_game = (REPO_ROOT / "src/code/server/sv_game.c").read_text(encoding="utf-8")
	cm_trace = (REPO_ROOT / "src/code/qcommon/cm_trace.c").read_text(encoding="utf-8")
	ui_gameinfo = (REPO_ROOT / "src/code/ui/ui_gameinfo.c").read_text(encoding="utf-8")

	init_block = _extract_function_block(sv_init, "void SV_Init (void)")
	clear_idle_block = _extract_function_block(sv_main, "void SV_ClearIdleServerExit( void )")
	should_error_block = _extract_function_block(sv_main, "qboolean SV_ShouldErrorExit( errorParm_t code )")
	check_idle_block = _extract_function_block(sv_main, "qboolean SV_CheckIdleServerExit( int currentTime )")
	check_timeouts_block = _extract_function_block(sv_main, "void SV_CheckTimeouts( void )")
	sv_frame_block = _extract_function_block(sv_main, "void SV_Frame( int msec )")
	shutdown_game_block = _extract_function_block(sv_game, "void SV_ShutdownGameProgs( void )")
	entity_string_block = _extract_function_block(sv_game, "static char *SV_GetGameEntityString( void )")
	init_game_vm_block = _extract_function_block(sv_game, "static void SV_InitGameVM( qboolean restart )")
	error_block = _extract_function_block(common, "void QDECL Com_Error( int code, const char *fmt, ... )")
	frame_block = _extract_function_block(common, "void Com_Frame( void )")
	cylinder_block = _extract_function_block(
		cm_trace, "void CM_TraceThroughVerticalCylinder( traceWork_t *tw, vec3_t origin, float radius, float halfheight, vec3_t start, vec3_t end)"
	)

	assert "extern\tcvar_t\t*sv_mapPoolFile;" in server_h
	assert "extern\tcvar_t\t*sv_includeCurrentMapInVote;" in server_h
	assert "extern\tcvar_t\t*sv_gtid;" in server_h
	assert "extern\tcvar_t\t*sv_idleRestart;" in server_h
	assert "extern\tcvar_t\t*sv_idleExit;" in server_h
	assert "extern\tcvar_t\t*sv_errorExit;" in server_h
	assert "extern\tcvar_t\t*sv_quitOnEmpty;" in server_h
	assert "extern\tcvar_t\t*sv_quitOnExitLevel;" in server_h
	assert "extern\tcvar_t\t*sv_altEntDir;" in server_h
	assert "extern\tcvar_t\t*sv_dumpEntities;" in server_h
	assert "extern\tcvar_t\t*sv_cylinderScale;" in server_h
	assert "qboolean SV_ShouldErrorExit( errorParm_t code );" in server_h
	assert "qboolean SV_CheckIdleServerExit( int currentTime );" in server_h
	assert "qboolean SV_ShouldErrorExit( errorParm_t code );" in qcommon
	assert "qboolean SV_CheckIdleServerExit( int currentTime );" in qcommon

	assert 'sv_mapPoolFile = Cvar_Get ("sv_mapPoolFile", "mappool.txt", CVAR_ARCHIVE );' in init_block
	assert 'sv_includeCurrentMapInVote = Cvar_Get ("sv_includeCurrentMapInVote", "0", CVAR_TEMP );' in init_block
	assert 'sv_gtid = Cvar_Get ("sv_gtid", "", CVAR_SERVERINFO | CVAR_ROM );' in init_block
	assert 'sv_idleRestart = Cvar_Get ("sv_idleRestart", "1", 0 );' in init_block
	assert 'sv_idleExit = Cvar_Get ("sv_idleExit", "120", 0 );' in init_block
	assert 'sv_errorExit = Cvar_Get ("sv_errorExit", "1", 0 );' in init_block
	assert 'sv_quitOnEmpty = Cvar_Get ("sv_quitOnEmpty", "0", 0 );' in init_block
	assert 'sv_quitOnExitLevel = Cvar_Get ("sv_quitOnExitLevel", "0", 0 );' in init_block
	assert 'sv_altEntDir = Cvar_Get ("sv_altEntDir", "", 0 );' in init_block
	assert 'sv_dumpEntities = Cvar_Get ("sv_dumpEntities", "0", 0 );' in init_block
	assert 'sv_cylinderScale = Cvar_Get ("sv_cylinderScale", "1.1f", 0 );' in init_block
	assert 'static const char *fileCvars[] = { "ui_mapPoolFile", "sv_mapPoolFile", NULL };' in ui_gameinfo

	assert "s_svIdleExitDeadline = 0;" in clear_idle_block
	assert "if ( code != ERR_DROP && code != ERR_DISCONNECT ) {" in should_error_block
	assert "if ( !sv_errorExit ) {" in should_error_block
	assert 'Com_Printf( "sv_errorExit: configured to shut down on ERR_DROP or ERR_DISCONNECT\\n" );' in should_error_block
	assert "sv_errorExit->integer == 2" in should_error_block
	assert "( sv_errorExit->integer == 1 && com_sv_running && com_sv_running->integer )" in should_error_block
	assert "s_svIdleExitDeadline = currentTime + sv_idleExit->integer * 1000;" in check_idle_block
	assert "SV_ClearIdleServerExit();" in check_idle_block
	assert 'Com_Error( ERR_FATAL, "shutting down idle dedicated server after sv_idleExit (%d) seconds", sv_idleExit->integer );' in check_idle_block
	assert "if ( SV_CountActiveHumanClients() > 0 ) {" in check_timeouts_block
	assert "if ( s_svEmptyServerTime == -1 ) {" in check_timeouts_block
	assert "if ( sv_quitOnEmpty && sv_quitOnEmpty->integer > 0 ) {" in check_timeouts_block
	assert 'Com_Printf( "server has been empty for %d seconds, quit\\n", sv_quitOnEmpty->integer );' in check_timeouts_block

	assert "if ( SV_ShouldErrorExit( code ) ) {" in error_block
	assert "code = ERR_FATAL;" in error_block
	assert "if ( !com_sv_running->integer || ( sv_killserver && sv_killserver->integer ) ) {" in frame_block
	assert "minMsec = 50;" in frame_block
	assert "SV_CheckIdleServerExit( Sys_Milliseconds() );" in frame_block
	assert "SV_ClearIdleServerExit();" in frame_block
	assert 'if ( sv_idleRestart && sv_idleRestart->integer && svs.time > 0x5265c00 && SV_CountActiveHumanClients() == 0 ) {' in sv_frame_block
	assert 'SV_Shutdown( "Restarting idle server" );' in sv_frame_block
	assert 'Cbuf_AddText( "vstr nextmap\\n" );' in sv_frame_block

	assert "FS_FreeFile( s_svEntityStringOverride );" in shutdown_game_block
	assert 'Com_sprintf( altEntPath, sizeof( altEntPath ), "%s/%s.ent", sv_altEntDir->string, mapName );' in entity_string_block
	assert "FS_ReadFile( altEntPath, (void **)&s_svEntityStringOverride )" in entity_string_block
	assert 'Com_sprintf( dumpPath, sizeof( dumpPath ), "ents/%s.ent", mapName );' in entity_string_block
	assert 'FS_WriteFile( dumpPath, entityString, (int)strlen( entityString ) );' in entity_string_block
	assert "sv.entityParsePoint = SV_GetGameEntityString();" in init_game_vm_block

	assert 'radius *= Cvar_Get( "sv_cylinderScale", "1.1f", 0 )->value;' in cylinder_block


def test_server_dedicated_build_lane_emits_qzeroded_and_defaults_dedicated_runtime() -> None:
	qcommon = (REPO_ROOT / "src/code/qcommon/qcommon.h").read_text(encoding="utf-8")
	common = (REPO_ROOT / "src/code/qcommon/common.c").read_text(encoding="utf-8")
	win_shared = (REPO_ROOT / "src/code/win32/win_shared.c").read_text(encoding="utf-8")
	unix_shared = (REPO_ROOT / "src/code/unix/unix_shared.c").read_text(encoding="utf-8")
	null_main = (REPO_ROOT / "src/code/null/null_main.c").read_text(encoding="utf-8")
	build_script = (REPO_ROOT / ".vscode/build.ps1").read_text(encoding="utf-8")
	runtime_probe = (REPO_ROOT / "tools/server/run_server_runtime_probe.ps1").read_text(encoding="utf-8")
	build_windows = (REPO_ROOT / "docs/build/windows.md").read_text(encoding="utf-8")
	windows_pipeline = (REPO_ROOT / "docs/windows-native-pipeline.md").read_text(encoding="utf-8")

	name_gate_block = _extract_function_block(common, "static qboolean Com_ShouldDefaultDedicatedFromExecutable( void )")
	init_block = _extract_function_block(common, "void Com_Init( char *commandLine )")

	assert "Sys_ExecutableBaseName( void );" in qcommon
	assert "char *Sys_ExecutableBaseName( void )" in win_shared
	assert "char *Sys_ExecutableBaseName( void )" in unix_shared
	assert "char *Sys_ExecutableBaseName( void )" in null_main

	assert '!Q_stricmp( executableName, "qzeroded" )' in name_gate_block
	assert '!Q_stricmp( executableName, "qzeroded.exe" )' in name_gate_block
	assert '!Q_stricmp( executableName, "qzeroded.x86" )' in name_gate_block
	assert 'Cvar_Get( "dedicated", "2", 0 );' in init_block
	assert init_block.index("Com_ShouldDefaultDedicatedFromExecutable()") < init_block.index("Com_StartupVariable( NULL );")

	assert "$dedicatedExe = Join-Path $runtimeBinDir 'qzeroded.exe'" in build_script
	assert "Copy-Item -Path $clientExe -Destination $dedicatedExe -Force" in build_script
	assert "@{ Source = 'quakelive_steam.pdb'; Destination = 'qzeroded.pdb' }" in build_script
	assert "@{ Source = 'quakelive_steam.map'; Destination = 'qzeroded.map' }" in build_script
	assert 'Write-Host "Emitted dedicated server alias: $dedicatedExe"' in build_script

	assert "Get-Process -Name quakelive_steam,qzeroded -ErrorAction SilentlyContinue | Stop-Process -Force" in runtime_probe
	assert "$dedicatedExe = Join-Path $script:QlHome 'qzeroded.exe'" in runtime_probe
	assert "$script:Exe = if ( Test-Path -LiteralPath $dedicatedExe ) { $dedicatedExe } else { $launcherExe }" in runtime_probe

	assert "`qzeroded`" in build_windows
	assert "`qzeroded.x86`" in build_windows
	assert "`qzeroded.exe`" in build_windows
	assert "`qzeroded.exe`" in windows_pipeline


def test_windows_build_and_launch_pipeline_refresh_runtime_ui_bundle_and_vm_modules() -> None:
	build_script = (REPO_ROOT / ".vscode/build.ps1").read_text(encoding="utf-8")
	launch_script = (REPO_ROOT / ".vscode/launch.ps1").read_text(encoding="utf-8")
	launch_json = json.loads((REPO_ROOT / ".vscode/launch.json").read_text(encoding="utf-8"))

	assert '$uiBundleBuilder = Join-Path $repoRoot \'tools\\build_ui_bundle.py\'' in build_script
	assert 'Write-Host "Refreshing staged retail UI bundle..."' in build_script
	assert "Sync-ModuleRuntimeArtifacts -ModuleName 'cgamex86'" in build_script
	assert "Sync-ModuleRuntimeArtifacts -ModuleName 'qagamex86'" in build_script
	assert "Copy-Item -Path $sourcePath -Destination $destinationPath -Force" in build_script

	assert "(Join-Path $Baseq3Root 'ui\\menudef.h')" in launch_script
	assert "$runtimeModulesDir = Join-Path $repoRoot \"build\\win32\\$Configuration\\modules\"" in launch_script
	assert "function Sync-LaunchModuleArtifact" in launch_script
	assert "Sync-LaunchModuleArtifact -ModuleName 'cgamex86'" in launch_script
	assert "Sync-LaunchModuleArtifact -ModuleName 'qagamex86'" in launch_script

	for configuration in launch_json["configurations"]:
		assert configuration["cwd"] == "${workspaceFolder}\\build\\win32\\Debug\\bin"
		basepath_index = configuration["args"].index("fs_basepath") + 1
		assert configuration["args"][basepath_index] == "C:\\PROGRA~2\\Steam\\STEAMA~1\\common\\QUAKEL~1"


def test_filesystem_referenced_steamworks_helper_reconstructs_retail_publication_list() -> None:
    files = (REPO_ROOT / "src/code/qcommon/files.c").read_text(encoding="utf-8")
    qcommon = (REPO_ROOT / "src/code/qcommon/qcommon.h").read_text(encoding="utf-8")

    referenced_steamworks_block = _extract_function_block(files, "const char *FS_ReferencedSteamworks( void ) {")

    assert "unsigned int\tsteamItemIdLow;" in files
    assert "unsigned int\tsteamItemIdHigh;" in files
    assert "const char *FS_ReferencedSteamworks( void );" in qcommon
    assert "!search->pack || !search->pack->referenced" in referenced_steamworks_block
    assert "( search->pack->steamItemIdLow | search->pack->steamItemIdHigh ) == 0" in referenced_steamworks_block
    assert 'Com_sprintf( itemString, sizeof( itemString ), "%llu", itemId );' in referenced_steamworks_block
    assert 'Q_strcat( info, sizeof( info ), va( "%llu ", itemId ) );' in referenced_steamworks_block


def test_workshop_mount_startup_reconstructs_retail_subscribed_item_import_path() -> None:
    files = (REPO_ROOT / "src/code/qcommon/files.c").read_text(encoding="utf-8")
    steamworks = (REPO_ROOT / "src/common/platform/platform_steamworks.c").read_text(encoding="utf-8")
    steamworks_h = (REPO_ROOT / "src/common/platform/platform_steamworks.h").read_text(encoding="utf-8")

    add_dir_block = _extract_function_block(
        files,
        "static void FS_AddGameDirectoryInternal( const char *path, const char *dir, qboolean rawPath, unsigned int steamItemIdLow, unsigned int steamItemIdHigh ) {",
    )
    base_pak_block = _extract_function_block(files, "static qboolean FS_HasBasePak0( void ) {")
    workshop_init_block = _extract_function_block(files, "static void FS_SteamWorkshopInit( const char *gameName ) {")
    startup_block = _extract_function_block(files, "static void FS_Startup( const char *gameName ) {")
    has_ugc_block = _extract_function_block(steamworks, "qboolean QL_Steamworks_HasUGCInterface( void ) {")
    count_block = _extract_function_block(steamworks, "uint32_t QL_Steamworks_GetNumSubscribedItems( void ) {")
    list_block = _extract_function_block(steamworks, "uint32_t QL_Steamworks_GetSubscribedItems( uint64_t *outItemIds, uint32_t maxItems ) {")
    install_block = _extract_function_block(
        steamworks,
        "qboolean QL_Steamworks_GetItemInstallInfo( uint32_t idLow, uint32_t idHigh, uint64_t *outSizeOnDisk, char *folder, size_t folderSize, uint32_t *outTimestamp ) {",
    )

    assert "qboolean\trawPath;" in files
    assert 'fs_skipWorkshop = Cvar_Get( "fs_skipWorkshop", "0", CVAR_INIT );' in startup_block
    assert "FS_SteamWorkshopInit( gameName );" in startup_block
    assert "search->dir->rawPath = rawPath;" in add_dir_block
    assert "pak->steamItemIdLow = steamItemIdLow;" in add_dir_block
    assert "pak->steamItemIdHigh = steamItemIdHigh;" in add_dir_block
    assert "!fs_basepath || !fs_basepath->string[0]" in base_pak_block
    assert 'FS_FileExistsOnDisk( FS_BuildOSPath( fs_basepath->string, BASEGAME, "pak00.pk3" ) )' in base_pak_block
    assert "mountRawPath = qfalse;" in workshop_init_block
    assert 'Com_Printf( "WARNING: Skipping workshop PK3s since pak00 doesn\'t exist.\\n" );' in workshop_init_block
    assert "mountRawPath = qtrue;" in workshop_init_block
    assert 'Com_Printf( "Skipping workshop since fs_skipWorkshop is set.\\n" );' in workshop_init_block
    assert 'Com_Printf( "Skipping workshop since running in build mode.\\n" );' in workshop_init_block
    assert "QL_Steamworks_HasUGCInterface()" in workshop_init_block
    assert 'Com_Printf( "WARNING: Skipping workshop, ISteamUGC is NULL.\\n" );' in workshop_init_block
    assert "subscribedCount = QL_Steamworks_GetNumSubscribedItems();" in workshop_init_block
    assert "mountedCount = QL_Steamworks_GetSubscribedItems( itemIds, subscribedCount );" in workshop_init_block
    assert "QL_Steamworks_GetItemInstallInfo( idLow, idHigh, &sizeOnDisk, installFolder, sizeof( installFolder ), &timestamp )" in workshop_init_block
    assert 'FS_AddGameDirectoryInternal( installFolder, "", mountRawPath, idLow, idHigh );' in workshop_init_block
    assert "const char *path, const char *dir, qboolean rawPath, unsigned int steamItemIdLow, unsigned int steamItemIdHigh" in files
    assert "qboolean QL_Steamworks_HasUGCInterface( void );" in steamworks_h
    assert "uint32_t QL_Steamworks_GetNumSubscribedItems( void );" in steamworks_h
    assert "uint32_t QL_Steamworks_GetSubscribedItems( uint64_t *outItemIds, uint32_t maxItems );" in steamworks_h
    assert "qboolean QL_Steamworks_GetItemInstallInfo( uint32_t idLow, uint32_t idHigh, uint64_t *outSizeOnDisk, char *folder, size_t folderSize, uint32_t *outTimestamp );" in steamworks_h
    assert "return QL_Steamworks_GetUGCInterface() != NULL ? qtrue : qfalse;" in has_ugc_block
    assert "vtable[0xc8 / 4]" in count_block
    assert "vtable[0xcc / 4]" in list_block
    assert "vtable[0xd4 / 4]" in install_block


def test_lobby_social_wrappers_reconstruct_mapped_matchmaking_slots() -> None:
    steamworks_h = (REPO_ROOT / "src/common/platform/platform_steamworks.h").read_text(encoding="utf-8")
    steamworks = (REPO_ROOT / "src/common/platform/platform_steamworks.c").read_text(encoding="utf-8")

    friend_name_block = _extract_function_block(
        steamworks,
        "qboolean QL_Steamworks_GetFriendPersonaName( uint32_t idLow, uint32_t idHigh, char *buffer, size_t bufferSize )",
    )
    create_block = _extract_function_block(steamworks, "qboolean QL_Steamworks_CreateLobby( int maxMembers )")
    leave_block = _extract_function_block(steamworks, "qboolean QL_Steamworks_LeaveLobby( uint32_t idLow, uint32_t idHigh )")
    join_block = _extract_function_block(steamworks, "qboolean QL_Steamworks_JoinLobby( uint32_t idLow, uint32_t idHigh )")
    owner_block = _extract_function_block(
        steamworks,
        "qboolean QL_Steamworks_GetLobbyOwner( uint32_t idLow, uint32_t idHigh, uint32_t *outIdLow, uint32_t *outIdHigh )",
    )
    data_count_block = _extract_function_block(
        steamworks,
        "int QL_Steamworks_GetLobbyDataCount( uint32_t idLow, uint32_t idHigh )",
    )
    set_lobby_data_block = _extract_function_block(
        steamworks,
        "qboolean QL_Steamworks_SetLobbyData( uint32_t idLow, uint32_t idHigh, const char *key, const char *value )",
    )
    data_index_block = _extract_function_block(
        steamworks,
        "qboolean QL_Steamworks_GetLobbyDataByIndex( uint32_t idLow, uint32_t idHigh, int index, char *key, size_t keySize, char *value, size_t valueSize )",
    )
    member_count_block = _extract_function_block(
        steamworks,
        "int QL_Steamworks_GetNumLobbyMembers( uint32_t idLow, uint32_t idHigh )",
    )
    member_limit_block = _extract_function_block(
        steamworks,
        "int QL_Steamworks_GetLobbyMemberLimit( uint32_t idLow, uint32_t idHigh )",
    )
    member_index_block = _extract_function_block(
        steamworks,
        "qboolean QL_Steamworks_GetLobbyMemberByIndex( uint32_t idLow, uint32_t idHigh, int index, uint32_t *outIdLow, uint32_t *outIdHigh )",
    )
    set_server_block = _extract_function_block(
        steamworks,
        "qboolean QL_Steamworks_SetLobbyServer( uint32_t idLow, uint32_t idHigh, uint32_t serverIp, uint16_t serverPort )",
    )
    invite_block = _extract_function_block(steamworks, "qboolean QL_Steamworks_ShowInviteOverlay( uint32_t idLow, uint32_t idHigh )")
    invite_lobby_block = _extract_function_block(
        steamworks,
        "qboolean QL_Steamworks_InviteUserToLobby( uint32_t lobbyIdLow, uint32_t lobbyIdHigh, uint32_t userIdLow, uint32_t userIdHigh )",
    )
    invite_game_block = _extract_function_block(
        steamworks,
        "qboolean QL_Steamworks_InviteUserToGame( uint32_t idLow, uint32_t idHigh, const char *connectString )",
    )
    say_block = _extract_function_block(steamworks, "qboolean QL_Steamworks_SayLobby( uint32_t idLow, uint32_t idHigh, const char *message )")
    stats_block = _extract_function_block(steamworks, "qboolean QL_Steamworks_RequestUserStats( uint32_t idLow, uint32_t idHigh )")
    user_stat_block = _extract_function_block(
        steamworks,
        "qboolean QL_Steamworks_GetUserStatInt( uint32_t idLow, uint32_t idHigh, const char *name, int *outValue )",
    )
    user_achievement_block = _extract_function_block(
        steamworks,
        "qboolean QL_Steamworks_GetUserAchievement( uint32_t idLow, uint32_t idHigh, const char *name, qboolean *outAchieved, int *outUnlockTime )",
    )
    achievement_attr_block = _extract_function_block(
        steamworks, 'const char *QL_Steamworks_GetAchievementDisplayAttribute( const char *name, const char *key )'
    )

    assert "qboolean QL_Steamworks_GetFriendPersonaName( uint32_t idLow, uint32_t idHigh, char *buffer, size_t bufferSize );" in steamworks_h
    assert "qboolean QL_Steamworks_GetLobbyOwner( uint32_t idLow, uint32_t idHigh, uint32_t *outIdLow, uint32_t *outIdHigh );" in steamworks_h
    assert "int QL_Steamworks_GetLobbyDataCount( uint32_t idLow, uint32_t idHigh );" in steamworks_h
    assert "qboolean QL_Steamworks_SetLobbyData( uint32_t idLow, uint32_t idHigh, const char *key, const char *value );" in steamworks_h
    assert "qboolean QL_Steamworks_GetLobbyDataByIndex( uint32_t idLow, uint32_t idHigh, int index, char *key, size_t keySize, char *value, size_t valueSize );" in steamworks_h
    assert "int QL_Steamworks_GetNumLobbyMembers( uint32_t idLow, uint32_t idHigh );" in steamworks_h
    assert "int QL_Steamworks_GetLobbyMemberLimit( uint32_t idLow, uint32_t idHigh );" in steamworks_h
    assert "qboolean QL_Steamworks_GetLobbyMemberByIndex( uint32_t idLow, uint32_t idHigh, int index, uint32_t *outIdLow, uint32_t *outIdHigh );" in steamworks_h
    assert "qboolean QL_Steamworks_GetUserStatInt( uint32_t idLow, uint32_t idHigh, const char *name, int *outValue );" in steamworks_h
    assert "qboolean QL_Steamworks_GetUserAchievement( uint32_t idLow, uint32_t idHigh, const char *name, qboolean *outAchieved, int *outUnlockTime );" in steamworks_h
    assert 'const char *QL_Steamworks_GetAchievementDisplayAttribute( const char *name, const char *key );' in steamworks_h
    assert "vtable[0x1c / 4]" in friend_name_block
    assert "QL_Steamworks_CopySteamString( buffer, bufferSize, fn( friends, NULL, QL_Steamworks_CombineIdentityWords( idLow, idHigh ) ) );" in friend_name_block
    assert "vtable[0x34 / 4]" in create_block
    assert "return fn( matchmaking, NULL, 2, maxMembers ) != 0 ? qtrue : qfalse;" in create_block
    assert "vtable[0x3c / 4]" in leave_block
    assert "fn( matchmaking, NULL, idLow, idHigh );" in leave_block
    assert "vtable[0x38 / 4]" in join_block
    assert "return fn( matchmaking, NULL, idLow, idHigh ) != 0 ? qtrue : qfalse;" in join_block
    assert "vtable[0x8c / 4]" in owner_block
    assert "fn( matchmaking, NULL, &lobbyOwnerId, idLow, idHigh );" in owner_block
    assert "vtable[0x54 / 4]" in data_count_block
    assert "return fn( matchmaking, NULL, idLow, idHigh );" in data_count_block
    assert "vtable[0x50 / 4]" in set_lobby_data_block
    assert "return fn( matchmaking, NULL, idLow, idHigh, key, value ) ? qtrue : qfalse;" in set_lobby_data_block
    assert "vtable[0x58 / 4]" in data_index_block
    assert "fn( matchmaking, NULL, idLow, idHigh, index, key, (int)keySize, value, (int)valueSize );" in data_index_block
    assert "vtable[0x44 / 4]" in member_count_block
    assert "return fn( matchmaking, NULL, idLow, idHigh );" in member_count_block
    assert "vtable[0x80 / 4]" in member_limit_block
    assert "return fn( matchmaking, NULL, idLow, idHigh );" in member_limit_block
    assert "vtable[0x48 / 4]" in member_index_block
    assert "fn( matchmaking, NULL, &memberId, idLow, idHigh, index );" in member_index_block
    assert "userVTable[0x08 / 4]" in set_server_block
    assert "matchmakingVTable[0x8c / 4]" in set_server_block
    assert "matchmakingVTable[0x74 / 4]" in set_server_block
    assert "if ( lobbyOwnerId.value != localSteamId.value ) {" in set_server_block
    assert "setLobbyServerFn( matchmaking, NULL, idLow, idHigh, serverIp, serverPort, idLow, idHigh );" in set_server_block
    assert "vtable[0x84 / 4]" in invite_block
    assert "fn( friends, NULL, idLow, idHigh );" in invite_block
    assert "vtable[0x40 / 4]" in invite_lobby_block
    assert "return fn( matchmaking, NULL, lobbyIdLow, lobbyIdHigh, userIdLow, userIdHigh ) ? qtrue : qfalse;" in invite_lobby_block
    assert "vtable[0xc4 / 4]" in invite_game_block
    assert "return fn( friends, NULL, idLow, idHigh, connectString ) ? qtrue : qfalse;" in invite_game_block
    assert "vtable[0x68 / 4]" in say_block
    assert "messageLength = (int)strlen( message ) + 1;" in say_block
    assert "vtable[0x40 / 4]" in stats_block
    assert "return fn( userStats, NULL, idLow, idHigh ) != 0 ? qtrue : qfalse;" in stats_block
    assert "vtable[0x48 / 4]" in user_stat_block
    assert "return fn( userStats, NULL, idLow, idHigh, name, outValue ) ? qtrue : qfalse;" in user_stat_block
    assert "vtable[0x50 / 4]" in user_achievement_block
    assert "if ( outUnlockTime ) {" in user_achievement_block
    assert "*outUnlockTime = unlockTime;" in user_achievement_block
    assert "*outAchieved = achieved ? qtrue : qfalse;" in user_achievement_block
    assert "vtable[0x30 / 4]" in achievement_attr_block
    assert 'value = fn( userStats, NULL, name, key );' in achievement_attr_block
    assert 'return value ? value : "";' in achievement_attr_block


def test_operator_workshop_commands_reconstruct_retail_ugc_surface() -> None:
    server_h = (REPO_ROOT / "src/code/server/server.h").read_text(encoding="utf-8")
    sv_init = (REPO_ROOT / "src/code/server/sv_init.c").read_text(encoding="utf-8")
    sv_ccmds = (REPO_ROOT / "src/code/server/sv_ccmds.c").read_text(encoding="utf-8")
    steamworks = (REPO_ROOT / "src/common/platform/platform_steamworks.c").read_text(encoding="utf-8")

    workshop_provider_block = _extract_function_block(sv_init, "const char *SV_GetWorkshopProviderLabel( void )")
    workshop_policy_block = _extract_function_block(sv_init, "const char *SV_GetWorkshopPolicyLabel( void )")
    workshop_log_block = _extract_function_block(
        sv_ccmds, "static void SV_LogWorkshopOperatorLifecycle( const char *commandName, unsigned long long itemId, const char *detail )"
    )
    workshop_support_block = _extract_function_block(sv_ccmds, "static qboolean SV_WorkshopServiceSupportsSteamCommands( void )")
    request_helper_block = _extract_function_block(sv_ccmds, "static void SV_SteamWorkshop_RequestDownload( uint32_t itemIdLow, uint32_t itemIdHigh )")
    subscribe_helper_block = _extract_function_block(sv_ccmds, "static void SV_SteamWorkshop_SubscribeItem( uint32_t itemIdLow, uint32_t itemIdHigh )")
    unsubscribe_helper_block = _extract_function_block(sv_ccmds, "static void SV_SteamWorkshop_UnsubscribeItem( uint32_t itemIdLow, uint32_t itemIdHigh )")
    download_block = _extract_function_block(sv_ccmds, "static void SV_SteamCmd_DownloadUGC_f( void )")
    subscribe_block = _extract_function_block(sv_ccmds, "static void SV_SteamCmd_SubscribeUGC_f( void )")
    unsubscribe_block = _extract_function_block(sv_ccmds, "static void SV_SteamCmd_UnsubscribeUGC_f( void )")
    add_block = _extract_function_block(sv_ccmds, "void SV_AddOperatorCommands( void )")
    item_state_block = _extract_function_block(
        steamworks,
        "uint32_t QL_Steamworks_GetItemState( uint32_t idLow, uint32_t idHigh )",
    )
    subscribe_platform_block = _extract_function_block(
        steamworks,
        "qboolean QL_Steamworks_SubscribeItem( uint32_t idLow, uint32_t idHigh )",
    )
    unsubscribe_platform_block = _extract_function_block(
        steamworks,
        "qboolean QL_Steamworks_UnsubscribeItem( uint32_t idLow, uint32_t idHigh )",
    )
    download_platform_block = _extract_function_block(
        steamworks,
        "qboolean QL_Steamworks_DownloadItem( uint32_t idLow, uint32_t idHigh, qboolean highPriority )",
    )

    assert "const char *SV_GetWorkshopProviderLabel( void );" in server_h
    assert "const char *SV_GetWorkshopPolicyLabel( void );" in server_h
    assert "return SV_GetPlatformFeatureProviderLabel( &services->workshop );" in workshop_provider_block
    assert 'return QL_DescribePlatformFeaturePolicy( &services->workshop );' in workshop_policy_block
    assert 'Com_Printf( "Workshop operator %s for %llu via %s [%s]: %s\\n",' in workshop_log_block
    assert "SV_GetWorkshopProviderLabel()" in workshop_log_block
    assert "SV_GetWorkshopPolicyLabel()" in workshop_log_block
    assert 'return ( strstr( provider, "Steam UGC" ) != NULL );' in workshop_support_block
    assert "SV_WorkshopServiceSupportsSteamCommands()" in request_helper_block
    assert "QL_Steamworks_GetItemState( itemIdLow, itemIdHigh ) & 4u" in request_helper_block
    assert 'Com_sprintf( detail, sizeof( detail ), "Workshop item %llu: in cache.", itemId );' in request_helper_block
    assert 'Com_sprintf( detail, sizeof( detail ), "Workshop item %llu: download", itemId );' in request_helper_block
    assert "(void)QL_Steamworks_SubscribeItem( itemIdLow, itemIdHigh );" in subscribe_helper_block
    assert "QL_Steamworks_GetItemState( itemIdLow, itemIdHigh ) & 4u" in subscribe_helper_block
    assert "FS_Restart( sv.checksumFeed );" in subscribe_helper_block
    assert "(void)QL_Steamworks_UnsubscribeItem( itemIdLow, itemIdHigh );" in unsubscribe_helper_block
    assert 'Com_Printf( "Usage: steam_downloadugc <itemid>\\n" );' in download_block
    assert 'sscanf( Cmd_Argv( 1 ), "%llu", &itemId );' in download_block
    assert "SV_SteamWorkshop_RequestDownload( itemIdLow, itemIdHigh );" in download_block
    assert 'Com_Printf( "Usage: steam_subscribeugc <itemid>\\n" );' in subscribe_block
    assert "SV_SteamWorkshop_SubscribeItem( itemIdLow, itemIdHigh );" in subscribe_block
    assert 'Com_Printf( "Usage: steam_unsubscribeugc <itemid>\\n" );' in unsubscribe_block
    assert "SV_SteamWorkshop_UnsubscribeItem( itemIdLow, itemIdHigh );" in unsubscribe_block
    assert 'Cmd_AddCommand ("steam_downloadugc", SV_SteamCmd_DownloadUGC_f);' in add_block
    assert 'Cmd_AddCommand ("steam_subscribeugc", SV_SteamCmd_SubscribeUGC_f);' in add_block
    assert 'Cmd_AddCommand ("steam_unsubscribeugc", SV_SteamCmd_UnsubscribeUGC_f);' in add_block
    assert "vtable[0xd0 / 4]" in item_state_block
    assert "vtable[0xc0 / 4]" in subscribe_platform_block
    assert "itemState = QL_Steamworks_GetItemState( idLow, idHigh );" in subscribe_platform_block
    assert "return itemState != 0u ? qtrue : qfalse;" in subscribe_platform_block
    assert "vtable[0xc4 / 4]" in unsubscribe_platform_block
    assert "vtable[0xdc / 4]" in download_platform_block
