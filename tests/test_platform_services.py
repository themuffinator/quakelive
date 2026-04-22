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

    assert "UI_SetBrowserActive( ui_activeMenuFlow == UI_MENU_FLOW_QUAKELIVE );" in main_case.group(1)
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
    load_avatar_block = _extract_function_block(
        steamworks,
        "qboolean QL_Steamworks_LoadAvatarRGBA( uint32_t idLow, uint32_t idHigh, ql_steam_avatar_size_t size, uint8_t **outPixels, uint32_t *outWidth, uint32_t *outHeight )",
    )

    assert "CL_SteamResources_ParseAvatarURL( url, &size, &idLow, &idHigh )" in avatar_block
    assert "QL_Steamworks_LoadAvatarRGBA( idLow, idHigh, size, &rgbaPixels, &width, &height )" in avatar_block
    assert "width == 0 || height == 0 || width > INT_MAX || height > INT_MAX" in avatar_block
    assert "*outPixels = rgbaPixels;" in avatar_block
    assert "*outWidth = (int)width;" in avatar_block
    assert "*outHeight = (int)height;" in avatar_block
    assert "CL_SteamResources_EncodeAvatarTGA" not in avatar_block

    assert "qhandle_t CL_RegisterShaderFromRGBA( const char *name, const byte *pic, int width, int height, qboolean mipRawImage );" in client_h
    assert "qhandle_t CL_RegisterShaderFromRGBA( const char *name, const byte *pic, int width, int height, qboolean mipRawImage ) {" in cl_main
    assert "image = R_CreateImage( name, pic, width, height, mipRawImage, mipRawImage, mipRawImage ? GL_REPEAT : GL_CLAMP );" in cl_main

    assert "if ( CL_SteamResources_IsAvatarURL( url ) ) {" in shader_block
    assert "CL_SteamResources_RequestAvatarRGBA( url, &rgbaPixels, &width, &height )" in shader_block
    assert "shader = CL_RegisterShaderFromRGBA( rendererName, rgbaPixels, width, height, qfalse );" in shader_block
    assert "QL_Steamworks_FreeBuffer( rgbaPixels );" in shader_block
    assert "CL_SteamResources_EncodeAvatarTGA" not in shader_block
    assert '".tga"' not in steam_resources
    assert 'Cvar_Set( "ui_resourceBridgeProvider", CL_GetSteamResourceServiceProviderLabel() );' in refresh_cvars_block
    assert 'Cvar_Set( "ui_resourceBridgePolicy", CL_GetSteamResourceServicePolicyLabel() );' in refresh_cvars_block
    assert "CL_RefreshSteamResourceBridgeCvars();" in resources_init_block

    assert "friendsVTable" in load_avatar_block
    assert "utilsVTable" in load_avatar_block
    assert "QL_Steamworks_GetAvatarMethodIndex( size )" in load_avatar_block
    assert "utilsVTable[0x14 / 4]" in load_avatar_block
    assert "utilsVTable[0x18 / 4]" in load_avatar_block


def test_client_steam_callback_owner_reconstructs_retail_frame_pump_and_lifecycle() -> None:
    cl_main = (REPO_ROOT / "src/code/client/cl_main.c").read_text(encoding="utf-8")

    frame_block = _extract_function_block(cl_main, "void CL_Frame ( int msec ) {")
    init_block = _extract_function_block(cl_main, "void CL_Init( void ) {")
    shutdown_block = _extract_function_block(cl_main, "void CL_Shutdown( void ) {")
    callback_init_block = _extract_function_block(cl_main, "static void CL_Steam_InitCallbacks( void ) {")
    callback_shutdown_block = _extract_function_block(cl_main, "static void CL_Steam_ShutdownCallbacks( void ) {")
    stats_gate_block = _extract_function_block(cl_main, "static qboolean CL_Steam_ShouldRegisterStatsClear( void ) {")
    stats_clear_block = _extract_function_block(cl_main, "static void CL_Steam_ClearStats_f( void )")

    assert "CL_Steam_Frame();" in frame_block
    assert frame_block.index("CL_Steam_Frame();") < frame_block.index("CL_CheckForResend();")
    assert "CL_WebHost_Frame();" in frame_block
    assert frame_block.index("CL_WebHost_Frame();") < frame_block.index("CL_CheckForResend();")

    assert "static const ql_platform_feature_descriptor *CL_GetMatchmakingServiceDescriptor( void ) {" in cl_main
    assert "static const ql_platform_feature_descriptor *CL_GetStatsServiceDescriptor( void ) {" in cl_main
    assert "static void CL_LogMatchmakingServiceIgnored( const char *commandName, const char *reason ) {" in cl_main
    assert "static void CL_LogStatsServiceIgnored( const char *commandName, const char *reason ) {" in cl_main
    assert "static void CL_RefreshPlatformServiceCvars( void ) {" in cl_main
    assert "cl_statsClearRegistered = qfalse;" in init_block
    assert "if ( CL_Steam_ShouldRegisterStatsClear() ) {" in init_block
    assert 'Cmd_AddCommand ("stats_clear", CL_Steam_ClearStats_f );' in init_block
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
    assert 'Cvar_Get ("cl_matchmakingProvider", "Unavailable", CVAR_ROM );' in init_block
    assert 'Cvar_Get ("cl_matchmakingPolicy", "compatibility-unavailable", CVAR_ROM );' in init_block
    assert 'Cvar_Get ("cl_statsProvider", "Unavailable", CVAR_ROM );' in init_block
    assert 'Cvar_Get ("cl_statsPolicy", "compatibility-unavailable", CVAR_ROM );' in init_block
    assert 'Cvar_Get ("cl_socialOverlayProvider", "Unavailable", CVAR_ROM );' in init_block
    assert 'Cvar_Get ("cl_socialOverlayPolicy", "compatibility-unavailable", CVAR_ROM );' in init_block
    assert "CL_RefreshPlatformServiceCvars();" in init_block
    assert "CL_Steam_InitCallbacks();" in init_block
    assert "CL_WebHost_Init();" in init_block

    assert "CL_Steam_ShutdownCallbacks();" in shutdown_block
    assert "if ( cl_statsClearRegistered ) {" in shutdown_block
    assert 'Cmd_RemoveCommand ("stats_clear");' in shutdown_block
    assert "CL_WebHost_Shutdown();" in shutdown_block

    assert "QL_Steamworks_RegisterClientCallbacks( &clientBindings )" in callback_init_block
    assert "QL_Steamworks_RegisterLobbyCallbacks( &lobbyBindings )" in callback_init_block
    assert "QL_Steamworks_RegisterMicroCallbacks( &microBindings )" in callback_init_block
    assert "QL_Steamworks_RegisterWorkshopCallbacks( &workshopBindings )" in callback_init_block
    assert "CL_RefreshPlatformServiceCvars();" in callback_init_block
    assert 'Cvar_Set( "cl_onlineServicesMode", QL_GetOnlineServicesModeLabel() );' in cl_main
    assert 'Cvar_Set( "cl_onlineServicesPolicy", QL_GetOnlineServicesPolicyLabel() );' in cl_main
    assert 'Cvar_Set( "cl_identityBootstrapMode", CL_GetIdentityBootstrapModeLabel() );' in cl_main
    assert 'Cvar_Set( "cl_identityBootstrapPolicy", CL_GetIdentityBootstrapPolicyLabel() );' in cl_main
    assert 'Cvar_Set( "cl_voiceServiceMode", CL_GetVoiceServiceModeLabel() );' in cl_main
    assert 'Cvar_Set( "cl_voiceServicePolicy", CL_GetVoiceServicePolicyLabel() );' in cl_main
    assert 'Cvar_Set( "ui_subscriptionBridgeMode", QL_GetOnlineServicesModeLabel() );' in cl_main
    assert 'Cvar_Set( "ui_subscriptionBridgePolicy", QL_GetOnlineServicesPolicyLabel() );' in cl_main
    assert "matchmakingProvider = CL_GetMatchmakingServiceProviderLabel();" in callback_init_block
    assert "matchmakingPolicy = CL_GetMatchmakingServicePolicyLabel();" in callback_init_block
    assert "statsProvider = CL_GetStatsServiceProviderLabel();" in callback_init_block
    assert "statsPolicy = CL_GetStatsServicePolicyLabel();" in callback_init_block
    assert 'Com_DPrintf( "Client callback bundle unavailable for matchmaking=%s [%s], stats=%s [%s]; keeping compatibility-only browser event fallback\\n",' in callback_init_block
    assert "cl_steamCallbackState.callbackRegistrationActive = qtrue;" in callback_init_block

    assert "QL_Steamworks_UnregisterWorkshopCallbacks();" in callback_shutdown_block
    assert "QL_Steamworks_UnregisterMicroCallbacks();" in callback_shutdown_block
    assert "QL_Steamworks_UnregisterLobbyCallbacks();" in callback_shutdown_block
    assert "QL_Steamworks_UnregisterClientCallbacks();" in callback_shutdown_block

    assert "return QL_Steamworks_GetAppID() == 0x54100u ? qtrue : qfalse;" in stats_gate_block
    assert 'CL_LogStatsServiceIgnored( "stats_clear", "stats provider unavailable" );' in stats_clear_block
    assert 'if ( !QL_Steamworks_ClearStats( qtrue ) ) {' in stats_clear_block
    assert 'CL_LogStatsServiceIgnored( "stats_clear", "clear request failed" );' in stats_clear_block


def test_platform_steamworks_reconstructs_retail_callback_bundle_registration_surface() -> None:
    steamworks = (REPO_ROOT / "src/common/platform/platform_steamworks.c").read_text(encoding="utf-8")

    register_client_block = _extract_function_block(
        steamworks, "qboolean QL_Steamworks_RegisterClientCallbacks( const ql_steam_client_callback_bindings_t *bindings ) {"
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
    clear_resource_block = _extract_function_block(
        steam_resources,
        "void CL_ClearSteamResourceCache( qboolean clearPersisted ) {",
    )
    clear_slot_block = _extract_function_block(
        steam_resources,
        "static void CL_SteamResources_ClearSlot( clSteamResource_t *slot, qboolean clearPersisted )",
    )

    assert 'Cvar_Get ("web_zoom", "100", CVAR_ARCHIVE );' in cl_main
    assert 'Cvar_Get ("web_console", "0", CVAR_ARCHIVE );' in cl_main
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

    assert '{ "GetFriendList", CL_WEB_METHOD_GET_FRIEND_LIST, qtrue }' in cl_cgame
    assert '{ "GetConfig", CL_WEB_METHOD_GET_CONFIG, qtrue }' in cl_cgame
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

    assert "case CL_WEB_METHOD_GET_ALL_UGC:" in method_block
    assert "CL_WebHost_BuildUGCResultsJson( ugcJson, sizeof( ugcJson ) );" in method_block
    assert 'CL_WebView_PublishEvent( "web.ugc.results", ugcJson );' in method_block
    assert "case CL_WEB_METHOD_GET_NEXT_KEY_DOWN:" in method_block
    assert "cl_webHost.keyCaptureArmed = qtrue;" in method_block
    assert "case CL_WEB_METHOD_SET_FAVORITE_SERVER:" in method_block
    assert "CL_WebHost_SetFavoriteServer(" in method_block

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


def test_client_browser_event_publication_hooks_reconstruct_runtime_owner() -> None:
    cl_main = (REPO_ROOT / "src/code/client/cl_main.c").read_text(encoding="utf-8")
    cl_cgame = (REPO_ROOT / "src/code/client/cl_cgame.c").read_text(encoding="utf-8")

    disconnect_block = _extract_function_block(cl_main, "void CL_Disconnect( qboolean showMainMenu ) {")
    stop_record_block = _extract_function_block(cl_main, "void CL_StopRecord_f( void ) {")
    first_snapshot_block = _extract_function_block(cl_cgame, "void CL_FirstSnapshot( void )")

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
    assert 'Cmd_RemoveCommand ("clientviewprofile");' in shutdown_block
    assert 'Cmd_RemoveCommand ("clientfriendinvite");' in shutdown_block
    assert "vtable[0x74 / 4]" in platform_block
    assert "QL_Steamworks_CombineIdentityWords( idLow, idHigh )" in platform_block


def test_client_voice_commands_reconstruct_retail_binding_surface() -> None:
    cl_main = (REPO_ROOT / "src/code/client/cl_main.c").read_text(encoding="utf-8")

    voice_log_block = _extract_function_block(
        cl_main, "static void CL_LogVoiceServiceFallback( const char *commandName, const char *reason ) {"
    )
    state_block = _extract_function_block(cl_main, "static void CL_SetLocalSpeakingState( qboolean speaking )")
    start_block = _extract_function_block(cl_main, "static void CL_VoiceStartRecording_f( void )")
    stop_block = _extract_function_block(cl_main, "static void CL_VoiceStopRecording_f( void )")
    disconnect_block = _extract_function_block(cl_main, "void CL_Disconnect( qboolean showMainMenu )")
    init_block = _extract_function_block(cl_main, "void CL_Init( void )")
    shutdown_block = _extract_function_block(cl_main, "void CL_Shutdown( void )")

    assert "static const char *CL_GetVoiceServiceModeLabel( void ) {" in cl_main
    assert "static const char *CL_GetVoiceServicePolicyLabel( void ) {" in cl_main
    assert 'Com_DPrintf( "%s voice fallback: %s (%s [%s])\\n",' in voice_log_block
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
    assert 'Cmd_AddCommand ("+voice", CL_VoiceStartRecording_f );' in init_block
    assert 'Cmd_AddCommand ("-voice", CL_VoiceStopRecording_f );' in init_block
    assert 'Cmd_RemoveCommand ("+voice");' in shutdown_block
    assert 'Cmd_RemoveCommand ("-voice");' in shutdown_block


def test_client_lobby_bootstrap_reconstructs_retail_connect_surface() -> None:
    cl_main = (REPO_ROOT / "src/code/client/cl_main.c").read_text(encoding="utf-8")

    connect_block = _extract_function_block(cl_main, "static void CL_Steam_ConnectLobby_f( void )")
    init_block = _extract_function_block(cl_main, "void CL_Init( void )")
    shutdown_block = _extract_function_block(cl_main, "void CL_Shutdown( void )")

    assert "static const char *CL_GetMatchmakingServiceProviderLabel( void ) {" in cl_main
    assert "static const char *CL_GetMatchmakingServicePolicyLabel( void ) {" in cl_main
    assert 'Cvar_Set( "lobby_autoconnect", Cmd_Argv( 1 ) );' in connect_block
    assert 'CL_LogMatchmakingServiceIgnored( "connect_lobby", "missing lobby id" );' in connect_block
    assert 'CL_LogMatchmakingServiceIgnored( "connect_lobby", "matchmaking provider unavailable" );' in connect_block
    assert 'Cvar_Get( "lobby_autoconnect", "", CVAR_TEMP );' in init_block
    assert 'Cvar_Get( "steam_maxLobbyClients", "16", CVAR_ARCHIVE );' in init_block
    assert 'Cmd_AddCommand ("connect_lobby", CL_Steam_ConnectLobby_f );' in init_block
    assert 'Cmd_RemoveCommand ("connect_lobby");' in shutdown_block


def test_client_rich_presence_join_and_server_change_reconstruct_retail_connect_handoff() -> None:
    cl_main = (REPO_ROOT / "src/code/client/cl_main.c").read_text(encoding="utf-8")

    execute_block = _extract_function_block(cl_main, "static void CL_Steam_ExecuteImmediateCommand( const char *command )")
    join_block = _extract_function_block(cl_main, "void CL_Steam_OnRichPresenceJoinRequested( const char *command )")
    server_change_block = _extract_function_block(
        cl_main,
        "void CL_Steam_OnGameServerChangeRequested( const char *server, const char *password )",
    )

    assert "Cbuf_ExecuteText( EXEC_NOW, command );" in execute_block
    assert "CL_Steam_ExecuteImmediateCommand( command );" in join_block
    assert "if ( password && password[0] ) {" in server_change_block
    assert 'Cvar_Set( "password", password );' in server_change_block
    assert 'CL_Steam_ExecuteImmediateCommand( va( "connect %s\\n", server ) );' in server_change_block


def test_client_main_menu_presence_seed_reconstructs_retail_bootstrap_status() -> None:
    cl_main = (REPO_ROOT / "src/code/client/cl_main.c").read_text(encoding="utf-8")
    steamworks = (REPO_ROOT / "src/common/platform/platform_steamworks.c").read_text(encoding="utf-8")

    presence_block = _extract_function_block(cl_main, "static void CL_Steam_SetMainMenuRichPresence( void )")
    init_block = _extract_function_block(cl_main, "void CL_Init( void )")
    platform_block = _extract_function_block(
        steamworks,
        "qboolean QL_Steamworks_SetRichPresence( const char *key, const char *value )",
    )

    assert 'if ( !QL_Steamworks_SetRichPresence( "status", "At the main menu" ) ) {' in presence_block
    assert 'CL_LogMatchmakingServiceIgnored( "steam_presence_main_menu", "rich presence update failed" );' in presence_block
    assert "CL_Steam_SetMainMenuRichPresence();" in init_block
    assert "vtable[0xac / 4]" in platform_block
    assert "return fn( friends, NULL, key, value ) ? qtrue : qfalse;" in platform_block


def test_client_identity_bootstrap_and_ui_subscription_lanes_stay_explicit() -> None:
    cl_main = (REPO_ROOT / "src/code/client/cl_main.c").read_text(encoding="utf-8")
    cl_ui = (REPO_ROOT / "src/code/client/cl_ui.c").read_text(encoding="utf-8")

    identity_log_block = _extract_function_block(
        cl_main, "static void CL_LogIdentityBootstrapFallback( const char *stage, const char *reason ) {"
    )
    persona_block = _extract_function_block(cl_main, "static void CL_Steam_SyncPersonaNameCvar( void )")
    country_block = _extract_function_block(cl_main, "static void CL_Steam_SeedCountryCvar( void )")
    subscribed_block = _extract_function_block(cl_ui, "static int QDECL QL_UI_trap_IsSubscribedApp( int arg1 )")
    subscription_log_block = _extract_function_block(
        cl_ui, "static void QL_UI_LogSubscriptionBridgeIgnored( int appId, const char *reason ) {"
    )

    assert "static const char *CL_GetIdentityBootstrapModeLabel( void ) {" in cl_main
    assert "static const char *CL_GetIdentityBootstrapPolicyLabel( void ) {" in cl_main
    assert 'Com_DPrintf( "%s identity bootstrap: %s (%s [%s])\\n",' in identity_log_block
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


def test_first_snapshot_reconstructs_retail_match_start_presence_status() -> None:
    cl_cgame = (REPO_ROOT / "src/code/client/cl_cgame.c").read_text(encoding="utf-8")

    presence_block = _extract_function_block(cl_cgame, "static void CL_Steam_SetMatchRichPresence( void )")
    first_snapshot_block = _extract_function_block(cl_cgame, "void CL_FirstSnapshot( void )")

    assert "CL_SteamServicesEnabled()" in presence_block
    assert "clc.demoplaying" in presence_block
    assert 'QL_Steamworks_SetRichPresence( "status", "Playing a match" );' in presence_block
    assert "CL_Steam_SetMatchRichPresence();" in first_snapshot_block
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

    helper_block = _extract_function_block(sv_main, "static void SV_SteamServerNetworkingFrame( void )")
    frame_block = _extract_function_block(sv_main, "void SV_Frame( int msec )")

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
    assert "QL_Steamworks_ServerSetMaxPlayerCount( sv_maxclients ? sv_maxclients->integer : 0 );" in publish_block
    assert 'needPass = Cvar_VariableIntegerValue( "g_needpass" );' in publish_block
    assert "QL_Steamworks_ServerSetPasswordProtected( needPass ? qtrue : qfalse );" in publish_block
    assert "QL_Steamworks_ServerSetServerName( sv_hostname->string );" in publish_block
    assert "QL_Steamworks_ServerSetMapName( sv_mapname->string );" in publish_block
    assert "QL_Steamworks_ServerSetGameDescription( SV_SteamServerGameDescription( sv_gametype->integer ) );" in publish_block
    assert "SV_SteamServerBuildGameTags( gameTags, sizeof( gameTags ) );" in publish_block
    assert "QL_Steamworks_ServerSetGameTags( gameTags );" in publish_block
    assert 'Cvar_VariableStringBuffer( "g_redScore", redScore, sizeof( redScore ) );' in publish_block
    assert 'QL_Steamworks_ServerSetKeyValue( "g_redScore", redScore );' in publish_block
    assert 'Cvar_VariableStringBuffer( "g_blueScore", blueScore, sizeof( blueScore ) );' in publish_block
    assert 'QL_Steamworks_ServerSetKeyValue( "g_blueScore", blueScore );' in publish_block
    assert 'rawName = Info_ValueForKey( cl->userinfo, "name" );' in publish_block
    assert 'Com_sprintf( playerName, sizeof( playerName ), "(Bot) %s", rawName );' in publish_block
    assert "playerState = SV_GameClientNum( i );" in publish_block
    assert "QL_Steamworks_ServerUpdateUserData( &steamId, playerName, (uint32_t)playerState->persistant[PERS_SCORE] );" in publish_block
    assert "QL_Steamworks_ServerSetBotPlayerCount( botCount );" in publish_block
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
	assert 'Cvar_Get ("sv_onlineServicesMode", "Unavailable", CVAR_ROM );' in sv_init_block
	assert 'Cvar_Get ("sv_onlineServicesPolicy", "compatibility-unavailable", CVAR_ROM );' in sv_init_block
	assert 'Cvar_Set( "sv_onlineServicesMode", QL_GetOnlineServicesModeLabel() );' in sv_init
	assert 'Cvar_Set( "sv_onlineServicesPolicy", QL_GetOnlineServicesPolicyLabel() );' in sv_init
	assert "SV_RefreshPlatformServiceCvars();" in sv_init_block
	assert "SV_RefreshPlatformServiceCvars();" in spawn_block
	assert 'Com_DPrintf( "Steam server identity unavailable for %s [%s]\\n",' in publish_block
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

    compatibility_block = _extract_function_block(
        sv_client, "static void SV_BuildPlatformAuthCompatibilityDetail( const char *detail, char *buffer, int bufferSize )"
    )
    log_auth_block = _extract_function_block(
        sv_client, "static void SV_LogPlatformAuth( const netadr_t *adr, const client_t *cl, const char *status, const char *detail )"
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
    assert "SV_BuildPlatformAuthCompatibilityDetail( detailMessage[0] ? detailMessage : NULL, message, sizeof( message ) );" in log_auth_block
    assert "NET_LogAuthTelemetry( NS_SERVER, adr, steamId, label, status, result, outcome, message[0] ? message : NULL );" in log_auth_block
    assert 'Com_Printf( "Connected to Steam servers via %s [%s]\\n",' in connected_block
    assert "SV_SteamServerPublishIdentity();" in connected_block
    assert "SV_SteamServerUpdatePublishedState( qtrue );" in connected_block
    assert 'Com_Printf( "Steam server connect failure (%d) via %s [%s]\\n", event->result,' in failure_block
    assert 'Com_Printf( "Disconnected from Steam servers (%d) via %s [%s]\\n", event->result,' in disconnected_block
    assert "QL_Steamworks_RegisterServerCallbacks( &bindings )" in init_callbacks_block
    assert "bindings.onValidateAuthTicketResponse = SV_SteamServerValidateAuthTicketResponseCallback;" in init_callbacks_block
    assert 'Com_DPrintf( "Steam server callbacks unavailable for %s [%s]\\n",' in init_callbacks_block
    assert "response = k_EAuthSessionResponseVACBanned;" in auth_callback_block
    assert "SV_DropClient( cl, message );" in auth_callback_block
    assert "QL_Steamworks_ServerAcceptP2PSession( &event->remoteId )" in p2p_block
    assert "denied = SV_BeginPlatformAuthSession( newcl, &from );" in direct_connect_block
    assert 'SV_FinalisePlatformAuthState( newcl, qtrue, "accepted" );' not in direct_connect_block
    assert "net_fakevacban" not in direct_connect_block
    assert "SV_EndPlatformAuthSession( drop );" in drop_block


def test_server_steam_stats_owner_reconstructs_retail_gameserverstats_bridge() -> None:
    server_h = (REPO_ROOT / "src/code/server/server.h").read_text(encoding="utf-8")
    sv_client = (REPO_ROOT / "src/code/server/sv_client.c").read_text(encoding="utf-8")
    sv_game = (REPO_ROOT / "src/code/server/sv_game.c").read_text(encoding="utf-8")
    steamworks_h = (REPO_ROOT / "src/common/platform/platform_steamworks.h").read_text(encoding="utf-8")
    steamworks = (REPO_ROOT / "src/common/platform/platform_steamworks.c").read_text(encoding="utf-8")

    create_session_block = _extract_function_block(sv_client, "static void SV_SteamStats_CreatePlayerSession( client_t *cl )")
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
    assert "qboolean QL_Steamworks_ServerRequestUserStats( const CSteamID *steamId );" in steamworks_h
    assert "qboolean QL_Steamworks_ServerGetUserStatInt( const CSteamID *steamId, const char *name, int *outValue );" in steamworks_h
    assert "qboolean QL_Steamworks_ServerGetUserAchievement( const CSteamID *steamId, const char *name, qboolean *outAchieved );" in steamworks_h
    assert "qboolean QL_Steamworks_ServerSetUserStatInt( const CSteamID *steamId, const char *name, int value );" in steamworks_h
    assert "qboolean QL_Steamworks_ServerSetUserAchievement( const CSteamID *steamId, const char *name );" in steamworks_h
    assert "qboolean QL_Steamworks_ServerStoreUserStats( const CSteamID *steamId );" in steamworks_h
    assert "SteamGameServerStats" in steamworks
    assert "QL_Steamworks_GetGameServerStatsInterface( void )" in steamworks
    assert "vtable[0x00 / 4]" in request_block
    assert "vtable[0x08 / 4]" in get_stat_block
    assert "vtable[0x0c / 4]" in get_achievement_block
    assert "vtable[0x14 / 4]" in set_stat_block
    assert "vtable[0x1c / 4]" in set_achievement_block
    assert "vtable[0x24 / 4]" in store_block
    assert '"wins"' in sv_client
    assert '"AW_MIDAIR"' in sv_client
    assert 'QL_Steamworks_ServerSendP2PPacket( &session->steamId, SV_STEAM_STATS_P2P_HELLO, 5, SV_STEAM_STATS_P2P_SEND_RELIABLE, SV_STEAM_STATS_P2P_CHANNEL )' in create_session_block
    assert "SV_SteamStats_RequestCurrentValues( session );" in create_session_block
    assert "SV_SteamStats_FlushPendingValues( session );" in remove_session_block
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
    assert "SV_SteamStats_ShouldUnlockAchievement()" in unlock_block
    assert "session->achievementDirty[achievementId] = qtrue;" in unlock_block
    assert "SV_SteamStats_FlushPendingValues( session );" in unlock_block
    assert "return session->achievementUnlocked[achievementId] ? qtrue : qfalse;" in has_block
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

    masters_block = _extract_function_block(sv_init, "static qboolean SV_SteamServerHasConfiguredMasters( void )")
    publish_block = _extract_function_block(sv_init, "void SV_SteamServerPublishIdentity( void )")
    spawn_block = _extract_function_block(sv_init, "void SV_SpawnServer( char *server, qboolean killBots )")
    init_block = _extract_function_block(sv_init, "void SV_Init (void)")
    shutdown_block = _extract_function_block(sv_init, "void SV_Shutdown( char *finalmsg )")

    assert 'Cvar_Get ("sv_referencedSteamworks", "", CVAR_ROM );' in init_block
    assert "SV_SteamServerInitCallbacks();" in init_block
    assert "if ( sv_master[i] && sv_master[i]->string[0] ) {" in masters_block
    assert "QL_Steamworks_ServerGetSteamID( &steamIdLow, &steamIdHigh )" in publish_block
    assert 'Com_DPrintf( "Steam server identity unavailable for %s [%s]\\n",' in publish_block
    assert "referencedSteamworks = FS_ReferencedSteamworks();" in publish_block
    assert "SV_SetConfigstring( 0x2ca, steamIdString );" in publish_block
    assert 'Cvar_Set( "sv_referencedSteamworks", referencedSteamworks );' in publish_block
    assert "SV_SetConfigstring( 0x2cb, referencedSteamworks );" in publish_block
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
    workshop_init_block = _extract_function_block(files, "static void FS_SteamWorkshopInit( const char *gameName ) {")
    startup_block = _extract_function_block(files, "static void FS_Startup( const char *gameName ) {")
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
    assert "subscribedCount = QL_Steamworks_GetNumSubscribedItems();" in workshop_init_block
    assert "mountedCount = QL_Steamworks_GetSubscribedItems( itemIds, subscribedCount );" in workshop_init_block
    assert "QL_Steamworks_GetItemInstallInfo( idLow, idHigh, &sizeOnDisk, installFolder, sizeof( installFolder ), &timestamp )" in workshop_init_block
    assert 'FS_AddGameDirectoryInternal( installFolder, "", qtrue, idLow, idHigh );' in workshop_init_block
    assert "const char *path, const char *dir, qboolean rawPath, unsigned int steamItemIdLow, unsigned int steamItemIdHigh" in files
    assert "uint32_t QL_Steamworks_GetNumSubscribedItems( void );" in steamworks_h
    assert "uint32_t QL_Steamworks_GetSubscribedItems( uint64_t *outItemIds, uint32_t maxItems );" in steamworks_h
    assert "qboolean QL_Steamworks_GetItemInstallInfo( uint32_t idLow, uint32_t idHigh, uint64_t *outSizeOnDisk, char *folder, size_t folderSize, uint32_t *outTimestamp );" in steamworks_h
    assert "vtable[0xc8 / 4]" in count_block
    assert "vtable[0xcc / 4]" in list_block
    assert "vtable[0xd4 / 4]" in install_block


def test_lobby_social_wrappers_reconstruct_mapped_matchmaking_slots() -> None:
    steamworks = (REPO_ROOT / "src/common/platform/platform_steamworks.c").read_text(encoding="utf-8")

    create_block = _extract_function_block(steamworks, "qboolean QL_Steamworks_CreateLobby( int maxMembers )")
    leave_block = _extract_function_block(steamworks, "qboolean QL_Steamworks_LeaveLobby( uint32_t idLow, uint32_t idHigh )")
    join_block = _extract_function_block(steamworks, "qboolean QL_Steamworks_JoinLobby( uint32_t idLow, uint32_t idHigh )")
    set_server_block = _extract_function_block(
        steamworks,
        "qboolean QL_Steamworks_SetLobbyServer( uint32_t idLow, uint32_t idHigh, uint32_t serverIp, uint16_t serverPort )",
    )
    invite_block = _extract_function_block(steamworks, "qboolean QL_Steamworks_ShowInviteOverlay( uint32_t idLow, uint32_t idHigh )")
    say_block = _extract_function_block(steamworks, "qboolean QL_Steamworks_SayLobby( uint32_t idLow, uint32_t idHigh, const char *message )")
    stats_block = _extract_function_block(steamworks, "qboolean QL_Steamworks_RequestUserStats( uint32_t idLow, uint32_t idHigh )")

    assert "vtable[0x34 / 4]" in create_block
    assert "return fn( matchmaking, NULL, 2, maxMembers ) != 0 ? qtrue : qfalse;" in create_block
    assert "vtable[0x3c / 4]" in leave_block
    assert "fn( matchmaking, NULL, idLow, idHigh );" in leave_block
    assert "vtable[0x38 / 4]" in join_block
    assert "return fn( matchmaking, NULL, idLow, idHigh ) != 0 ? qtrue : qfalse;" in join_block
    assert "userVTable[0x08 / 4]" in set_server_block
    assert "matchmakingVTable[0x8c / 4]" in set_server_block
    assert "matchmakingVTable[0x74 / 4]" in set_server_block
    assert "if ( lobbyOwnerId.value != localSteamId.value ) {" in set_server_block
    assert "setLobbyServerFn( matchmaking, NULL, idLow, idHigh, serverIp, serverPort, idLow, idHigh );" in set_server_block
    assert "vtable[0x84 / 4]" in invite_block
    assert "fn( friends, NULL, idLow, idHigh );" in invite_block
    assert "vtable[0x68 / 4]" in say_block
    assert "messageLength = (int)strlen( message ) + 1;" in say_block
    assert "vtable[0x40 / 4]" in stats_block
    assert "return fn( userStats, NULL, idLow, idHigh ) != 0 ? qtrue : qfalse;" in stats_block


def test_operator_workshop_commands_reconstruct_retail_ugc_surface() -> None:
    sv_ccmds = (REPO_ROOT / "src/code/server/sv_ccmds.c").read_text(encoding="utf-8")
    steamworks = (REPO_ROOT / "src/common/platform/platform_steamworks.c").read_text(encoding="utf-8")

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

    assert 'Com_Printf( "Usage: steam_downloadugc <itemid>\\n" );' in download_block
    assert 'sscanf( Cmd_Argv( 1 ), "%llu", &itemId );' in download_block
    assert "QL_Steamworks_GetItemState( itemIdLow, itemIdHigh ) & 4u" in download_block
    assert "QL_Steamworks_DownloadItem( itemIdLow, itemIdHigh, qtrue )" in download_block
    assert 'Com_Printf( "Usage: steam_subscribeugc <itemid>\\n" );' in subscribe_block
    assert "QL_Steamworks_SubscribeItem( itemIdLow, itemIdHigh )" in subscribe_block
    assert 'Com_Printf( "Usage: steam_unsubscribeugc <itemid>\\n" );' in unsubscribe_block
    assert "QL_Steamworks_UnsubscribeItem( itemIdLow, itemIdHigh )" in unsubscribe_block
    assert 'Cmd_AddCommand ("steam_downloadugc", SV_SteamCmd_DownloadUGC_f);' in add_block
    assert 'Cmd_AddCommand ("steam_subscribeugc", SV_SteamCmd_SubscribeUGC_f);' in add_block
    assert 'Cmd_AddCommand ("steam_unsubscribeugc", SV_SteamCmd_UnsubscribeUGC_f);' in add_block
    assert "vtable[0xd0 / 4]" in item_state_block
    assert "vtable[0xc0 / 4]" in subscribe_platform_block
    assert "vtable[0xc4 / 4]" in unsubscribe_platform_block
    assert "vtable[0xdc / 4]" in download_platform_block
