from __future__ import annotations

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
        printf(
            "%s|%s|%d|%d\\n",
            label,
            provider,
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
    result = subprocess.run([str(exe_path)], cwd=REPO_ROOT, check=True, capture_output=True, text=True)
    return result.stdout


def _parse_service_output(output: str) -> Dict[str, Tuple[str, bool, bool]]:
    services: Dict[str, Tuple[str, bool, bool]] = {}
    for line in output.strip().splitlines():
        label, provider, compiled, initialised = line.split("|", 3)
        services[label] = (provider, compiled == "1", initialised == "1")
    return services


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
        "auth": ("Build-disabled (QL_BUILD_ONLINE_SERVICES=0)", False, False),
        "matchmaking": ("Build-disabled (QL_BUILD_ONLINE_SERVICES=0)", False, False),
        "workshop": ("Build-disabled (QL_BUILD_ONLINE_SERVICES=0)", False, False),
        "overlay": ("Build-disabled (QL_BUILD_ONLINE_SERVICES=0)", False, False),
        "stats": ("Build-disabled (QL_BUILD_ONLINE_SERVICES=0)", False, False),
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
                "auth": ("Steamworks", True, True),
                "matchmaking": ("Steamworks", True, True),
                "workshop": ("Steam UGC", True, True),
                "overlay": ("Steam Overlay", True, True),
                "stats": ("Steam Stats", True, True),
            },
        ),
        (
            {"QL_BUILD_ONLINE_SERVICES": 1, "QL_BUILD_STEAMWORKS": 0, "QL_BUILD_OPEN_STEAM": 1},
            {
                "auth": ("Open Steam Adapter", True, True),
                "matchmaking": ("GameNetworkingSockets", True, True),
                "workshop": ("REST UGC Service", True, True),
                "overlay": ("In-Process UI Overlay", True, True),
                "stats": ("Metrics REST Adapter", True, True),
            },
        ),
        (
            {"QL_BUILD_ONLINE_SERVICES": 1, "QL_BUILD_STEAMWORKS": 1, "QL_BUILD_OPEN_STEAM": 1},
            {
                "auth": ("Hybrid", True, True),
                "matchmaking": ("Hybrid: Steamworks + GameNetworkingSockets", True, True),
                "workshop": ("Hybrid: Steam UGC + REST Mirror", True, True),
                "overlay": ("Hybrid: Steam Overlay + In-Process UI", True, True),
                "stats": ("Hybrid: Steam Stats + Metrics REST", True, True),
            },
        ),
        (
            {"QL_BUILD_ONLINE_SERVICES": 1, "QL_BUILD_STEAMWORKS": 1, "QL_BUILD_OPEN_STEAM": 0, "QL_STEAMWORKS_INIT_RESULT": 0},
            {
                "auth": ("Steamworks", True, False),
                "matchmaking": ("Steamworks", True, False),
                "workshop": ("Steam UGC", True, False),
                "overlay": ("Steam Overlay", True, False),
                "stats": ("Steam Stats", True, False),
            },
        ),
        (
            {"QL_BUILD_ONLINE_SERVICES": 1, "QL_BUILD_STEAMWORKS": 1, "QL_BUILD_OPEN_STEAM": 1, "QL_STEAMWORKS_INIT_RESULT": 0},
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
        {"QL_BUILD_ONLINE_SERVICES": 1, "QL_BUILD_STEAMWORKS": 1, "QL_BUILD_OPEN_STEAM": 1},
        include_client_stub=True,
    )

    details = dict(line.split("=", 1) for line in output.strip().splitlines())

    assert details["handled"] == "1"
    assert details["result"] == str(QL_AUTH_RESULT_ACCEPTED := 1)
    assert details["outcome"] == str(QL_AUTH_OUTCOME_SUCCESS := 0)
    assert "Hybrid fallback accepted credential via open adapter" in details["message"]


def test_online_service_bridge_only_hard_stubs_when_build_disabled() -> None:
    cl_cgame = (REPO_ROOT / "src/code/client/cl_cgame.c").read_text(encoding="utf-8")
    cl_ui = (REPO_ROOT / "src/code/client/cl_ui.c").read_text(encoding="utf-8")
    ui_main = (REPO_ROOT / "src/code/ui/ui_main.c").read_text(encoding="utf-8")

    refresh_block = _extract_function_block(cl_cgame, "void CL_RefreshOnlineServicesBridgeState( void )")
    assert "#if !QL_PLATFORM_HAS_ONLINE_SERVICES" in refresh_block
    assert 'Cvar_Set( "ui_browserAwesomium", "0" );' in refresh_block
    assert "CL_GetOverlayServiceDescriptor()" in refresh_block
    assert 'Cvar_Set( "ui_browserAwesomium", overlayAvailable ? "1" : "0" );' in refresh_block

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

    assert "CL_SteamServicesEnabled()" in block
    assert "QL_CG_CombineIdentityWords( identityLow, identityHigh )" in block
    assert 'Com_sprintf( url, sizeof( url ), "steam://avatar/large/%llu"' in block
    assert "CL_Steam_RegisterShader( url )" in block


def test_steam_resource_bridge_reconstructs_avatar_url_fetches() -> None:
    steam_resources = (REPO_ROOT / "src/code/client/cl_steam_resources.c").read_text(encoding="utf-8")
    steamworks = (REPO_ROOT / "src/common/platform/platform_steamworks.c").read_text(encoding="utf-8")

    request_block = _extract_function_block(
        steam_resources,
        "qboolean Sys_Steam_RequestURL( const char *url, byte **outBuffer, int *outSize ) {",
    )
    avatar_block = _extract_function_block(
        steam_resources,
        "static qboolean CL_SteamResources_RequestAvatar( const char *url, byte **outBuffer, int *outSize )",
    )
    load_avatar_block = _extract_function_block(
        steamworks,
        "qboolean QL_Steamworks_LoadAvatarRGBA( uint32_t idLow, uint32_t idHigh, ql_steam_avatar_size_t size, uint8_t **outPixels, uint32_t *outWidth, uint32_t *outHeight )",
    )

    assert "CL_SteamResources_IsAvatarURL( url )" in request_block
    assert "CL_SteamResources_RequestAvatar( url, outBuffer, outSize )" in request_block
    assert 'Com_Printf( "Steam avatar backend unavailable for %s\\n"' in request_block

    assert "CL_SteamResources_ParseAvatarURL( url, &size, &idLow, &idHigh )" in avatar_block
    assert "QL_Steamworks_LoadAvatarRGBA( idLow, idHigh, size, &rgbaPixels, &width, &height )" in avatar_block
    assert "CL_SteamResources_EncodeAvatarTGA( rgbaPixels, width, height, outBuffer, outSize )" in avatar_block
    assert "QL_Steamworks_FreeBuffer( rgbaPixels );" in avatar_block
    assert '".tga"' in steam_resources

    assert "friendsVTable" in load_avatar_block
    assert "utilsVTable" in load_avatar_block
    assert "QL_Steamworks_GetAvatarMethodIndex( size )" in load_avatar_block
    assert "utilsVTable[0x14 / 4]" in load_avatar_block
    assert "utilsVTable[0x18 / 4]" in load_avatar_block


def test_launcher_resource_bridge_reconstructs_retail_web_fallback_owner() -> None:
    cl_webpak = (REPO_ROOT / "src/code/client/cl_webpak.c").read_text(encoding="utf-8")
    steam_resources = (REPO_ROOT / "src/code/client/cl_steam_resources.c").read_text(encoding="utf-8")

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
    url_block = _extract_function_block(
        steam_resources,
        "qboolean Sys_Steam_RequestURL( const char *url, byte **outBuffer, int *outSize ) {",
    )

    assert 'strstr( virtualPath, ".." ) || strstr( virtualPath, "::" ) || strchr( virtualPath, \':\' )' in cl_webpak
    assert "FS_FOpenWebFileRead( request, &file, resolvedPath, sizeof( resolvedPath ) )" in mapped_block
    assert "length = FS_filelength( file );" in mapped_block
    assert "buffer = Z_Malloc( length + 1 );" in mapped_block
    assert "if ( length > 0 && FS_Read( buffer, length, file ) != length ) {" in mapped_block
    assert "normalizedValid = CL_WebPak_NormalizePath( virtualPath, normalized, sizeof( normalized ) );" in request_block
    assert "if ( normalizedValid && CL_WebPak_ReadInternal( normalized, outBuffer, outLength ) ) {" in request_block
    assert "if ( CL_WebRequestReadMappedFile( virtualPath, outBuffer, outLength ) ) {" in request_block
    assert "if ( !normalizedValid ) {" in request_block
    assert "length = FS_ReadFile( normalized, &fsBuffer );" in request_block

    assert "static qboolean CL_SteamResources_IsURIResource( const char *url ) {" in steam_resources
    assert 'return ( strstr( url, "://" ) != NULL ) ? qtrue : qfalse;' in steam_resources
    assert "if ( !CL_SteamResources_IsURIResource( url ) ) {" in shader_block
    assert "if ( CL_LauncherRequestData( url, (void **)outBuffer, outSize ) ) {" in url_block
    assert 'Com_Printf( "Launcher resource backend unavailable for %s\\n"' in url_block


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
    assert "CL_Web_ClearSessionState();" in clear_cache_block
    assert "CL_Web_ClearSessionState();" in reload_block
    assert "for ( i = 0; i < MAX_STEAM_RESOURCES; i++ ) {" in clear_resource_block
    assert "CL_SteamResources_ClearSlot( &cl_steamResources[i], clearPersisted );" in clear_resource_block
    assert "if ( slot->cachePath[0] && ( clearPersisted || !slot->persisted ) ) {" in clear_slot_block
    assert "CL_SteamResources_RemoveCacheFile( slot->cachePath );" in clear_slot_block


def test_advert_bridge_callbacks_track_retail_ui_and_cgame_state_paths() -> None:
    cl_cgame = (REPO_ROOT / "src/code/client/cl_cgame.c").read_text(encoding="utf-8")
    cl_ui = (REPO_ROOT / "src/code/client/cl_ui.c").read_text(encoding="utf-8")

    init_ui_block = _extract_function_block(cl_cgame, "void CL_AdvertisementBridge_InitUI( void )")
    activate_block = _extract_function_block(cl_cgame, "void CL_AdvertisementBridge_ActivateAdvert( int cellId )")
    set_active_block = _extract_function_block(cl_cgame, "void CL_AdvertisementBridge_SetActiveAdvert( int cellId )")
    shutdown_block = _extract_function_block(cl_cgame, "static void CL_AdvertisementBridge_ShutdownCGame( void )")
    ui_import82_block = _extract_function_block(cl_ui, "static void QDECL QL_UI_trap_InitAdvertisementBridge( void )")
    ui_import84_block = _extract_function_block(cl_ui, "static void QDECL QL_UI_trap_ActivateAdvert( int cellId )")
    cg_import_block = _extract_function_block(cl_cgame, "static void QDECL QL_CG_trap_SetActiveAdvert( int cellId )")

    assert "cl_advertisementBridge.activatedAdvertCellId = cellId;" in activate_block
    assert "cl_advertisementBridge.activeAdvertCellId = cellId;" in set_active_block
    assert "if ( cellId == 0 ) {" in set_active_block
    assert "cl_advertisementBridge.activatedAdvertCellId = 0;" in set_active_block
    assert "cl_advertisementBridge.activeAdvertCellId = 0;" in shutdown_block
    assert "cl_advertisementBridge.activatedAdvertCellId = 0;" in shutdown_block
    assert "CL_RefreshOnlineServicesBridgeState();" in init_ui_block
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

    assert 'Info_ValueForKey( info, "steamid" )' in parse_block
    assert "cl.gameState.stringOffsets[CS_PLAYERS + clientNum]" in parse_block
    assert 'dialog = "steamid";' in overlay_block
    assert 'dialog = "friendadd";' in overlay_block
    assert "CL_GetClientSteamId( clientNum, &steamIdLow, &steamIdHigh )" in overlay_block
    assert "QL_Steamworks_ActivateOverlayToUser( dialog, steamIdLow, steamIdHigh );" in overlay_block
    assert 'Cmd_AddCommand ("clientviewprofile", CL_Steam_OverlayCommand_f );' in init_block
    assert 'Cmd_AddCommand ("clientfriendinvite", CL_Steam_OverlayCommand_f );' in init_block
    assert 'Cmd_RemoveCommand ("clientviewprofile");' in shutdown_block
    assert 'Cmd_RemoveCommand ("clientfriendinvite");' in shutdown_block
    assert "vtable[0x74 / 4]" in platform_block
    assert "QL_Steamworks_CombineIdentityWords( idLow, idHigh )" in platform_block


def test_client_voice_commands_reconstruct_retail_binding_surface() -> None:
    cl_main = (REPO_ROOT / "src/code/client/cl_main.c").read_text(encoding="utf-8")

    state_block = _extract_function_block(cl_main, "static void CL_SetLocalSpeakingState( qboolean speaking )")
    start_block = _extract_function_block(cl_main, "static void CL_VoiceStartRecording_f( void )")
    stop_block = _extract_function_block(cl_main, "static void CL_VoiceStopRecording_f( void )")
    disconnect_block = _extract_function_block(cl_main, "void CL_Disconnect( qboolean showMainMenu )")
    init_block = _extract_function_block(cl_main, "void CL_Init( void )")
    shutdown_block = _extract_function_block(cl_main, "void CL_Shutdown( void )")

    assert "if ( !cgvm || cls.state != CA_ACTIVE || !cl.snap.valid ) {" in state_block
    assert "VM_Call( cgvm, CG_SET_CLIENT_SPEAKING_STATE, cl.snap.ps.clientNum, speaking ? 1 : 0 );" in state_block
    assert "if ( cl_voiceRecordingActive ) {" in start_block
    assert "cl_voiceRecordingActive = qtrue;" in start_block
    assert "CL_SetLocalSpeakingState( qtrue );" in start_block
    assert "if ( !cl_voiceRecordingActive ) {" in stop_block
    assert "cl_voiceRecordingActive = qfalse;" in stop_block
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

    assert 'Cvar_Set( "lobby_autoconnect", Cmd_Argv( 1 ) );' in connect_block
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

    assert 'QL_Steamworks_SetRichPresence( "status", "At the main menu" );' in presence_block
    assert "CL_Steam_SetMainMenuRichPresence();" in init_block
    assert "vtable[0xac / 4]" in platform_block
    assert "return fn( friends, NULL, key, value ) ? qtrue : qfalse;" in platform_block


def test_first_snapshot_reconstructs_retail_match_start_presence_status() -> None:
    cl_cgame = (REPO_ROOT / "src/code/client/cl_cgame.c").read_text(encoding="utf-8")

    presence_block = _extract_function_block(cl_cgame, "static void CL_Steam_SetMatchRichPresence( void )")
    first_snapshot_block = _extract_function_block(cl_cgame, "void CL_FirstSnapshot( void )")

    assert "CL_SteamServicesEnabled()" in presence_block
    assert "clc.demoplaying" in presence_block
    assert 'QL_Steamworks_SetRichPresence( "status", "Playing a match" );' in presence_block
    assert "CL_Steam_SetMatchRichPresence();" in first_snapshot_block


def test_server_game_server_wrappers_reconstruct_mapped_server_slots() -> None:
    steamworks = (REPO_ROOT / "src/common/platform/platform_steamworks.c").read_text(encoding="utf-8")

    init_block = _extract_function_block(steamworks, "qboolean QL_Steamworks_ServerInit( uint32_t ip, uint16_t gamePort, qboolean secure, qboolean dedicated )")
    shutdown_block = _extract_function_block(steamworks, "void QL_Steamworks_ServerShutdown( void )")
    is_initialised_block = _extract_function_block(steamworks, "qboolean QL_Steamworks_ServerIsInitialised( void )")
    run_callbacks_block = _extract_function_block(steamworks, "void QL_Steamworks_RunServerCallbacks( void )")
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
    sv_init = (REPO_ROOT / "src/code/server/sv_init.c").read_text(encoding="utf-8")

    hostname_block = _extract_function_block(sv_init, "static void SV_SteamServerInitDefaultHostname( void )")
    pack_ip_block = _extract_function_block(common, "static uint32_t Com_SteamPackGameServerIP( const char *addressString )")
    bootstrap_block = _extract_function_block(common, "void Com_InitSteamGameServer( void )")
    common_init_block = _extract_function_block(common, "void Com_Init( char *commandLine )")
    common_shutdown_block = _extract_function_block(common, "void Com_Shutdown (void)")
    sv_init_block = _extract_function_block(sv_init, "void SV_Init (void)")

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
    assert "QL_Steamworks_ServerSetDedicated( dedicated );" in bootstrap_block
    assert 'Cvar_VariableStringBuffer( "sv_setSteamAccount", steamAccount, sizeof( steamAccount ) );' in bootstrap_block
    assert "QL_Steamworks_ServerLogOn( steamAccount );" in bootstrap_block
    assert "QL_Steamworks_ServerEnableHeartbeats( qfalse );" in bootstrap_block
    assert 'QL_Steamworks_ServerSetProduct( "Quake Live" );' in bootstrap_block
    assert 'QL_Steamworks_ServerSetGameDir( "baseq3" );' in bootstrap_block
    assert "void\t\tCom_InitSteamGameServer( void );" in qcommon
    assert "Com_InitSteamGameServer();" in common_init_block
    assert "QL_Steamworks_Shutdown();" in common_shutdown_block
    assert "SV_SteamServerInitDefaultHostname();" in sv_init_block
    assert 'sv_tags = Cvar_Get ("sv_tags", "", CVAR_ARCHIVE );' in sv_init_block
    assert 'Cvar_Get ("sv_setSteamAccount", "", CVAR_ARCHIVE | CVAR_PROTECTED );' in sv_init_block
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
    publish_block = _extract_function_block(sv_init, "static void SV_SteamServerPublishIdentity( void )")
    spawn_block = _extract_function_block(sv_init, "void SV_SpawnServer( char *server, qboolean killBots )")
    init_block = _extract_function_block(sv_init, "void SV_Init (void)")
    shutdown_block = _extract_function_block(sv_init, "void SV_Shutdown( char *finalmsg )")

    assert 'Cvar_Get ("sv_referencedSteamworks", "", CVAR_ROM );' in init_block
    assert "if ( sv_master[i] && sv_master[i]->string[0] ) {" in masters_block
    assert "QL_Steamworks_ServerGetSteamID( &steamIdLow, &steamIdHigh )" in publish_block
    assert "SV_SetConfigstring( 0x2ca, steamIdString );" in publish_block
    assert 'Cvar_Set( "sv_referencedSteamworks", steamIdString );' in publish_block
    assert "SV_SetConfigstring( 0x2cb, steamIdString );" in publish_block
    assert "SV_SteamServerPublishIdentity();" in spawn_block
    assert "QL_Steamworks_ServerEnableHeartbeats( SV_SteamServerHasConfiguredMasters() );" in spawn_block
    assert "QL_Steamworks_ServerSetKeyValuesFromInfoString( serverInfo );" in spawn_block
    assert "QL_Steamworks_ServerEnableHeartbeats( qfalse );" in shutdown_block


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
