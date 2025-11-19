"""Verifies legacy CVar aliases mirror the canonical handles."""

from __future__ import annotations

import subprocess
import textwrap
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent

_CVAR_ALIAS_PROBE = textwrap.dedent(
    """
    #include <ctype.h>
    #include <stdio.h>
    #include <stdlib.h>
    #include <string.h>

    #define MAX_TEST_CVARS 16
    #define MAX_TEST_VM_HANDLES 4

    #include "q_shared.h"

    void trap_Cvar_Register( vmCvar_t *vmCvar, const char *varName, const char *defaultValue, int flags );
    void trap_Cvar_Set( const char *varName, const char *value );
    void trap_Cvar_Update( vmCvar_t *vmCvar );

    #include "g_legacy_cvars.h"

    typedef struct {
        char name[64];
        char value[MAX_CVAR_VALUE_STRING];
        vmCvar_t *vmHandles[MAX_TEST_VM_HANDLES];
        int vmHandleCount;
        int modificationCount;
    } testCvarEntry_t;

    static void Test_WriteVmCvar( vmCvar_t *vm, const char *value, int modificationCount );

    static testCvarEntry_t s_entries[MAX_TEST_CVARS];
    static int s_entryCount = 0;

    static testCvarEntry_t *Test_FindEntry( const char *name ) {
        for ( int i = 0; i < s_entryCount; ++i ) {
            if ( Q_stricmp( s_entries[i].name, name ) == 0 ) {
                return &s_entries[i];
            }
        }
        return NULL;
    }

    static void Test_LinkVmHandle( testCvarEntry_t *entry, vmCvar_t *vm ) {
        if ( !entry || !vm ) {
            return;
        }
        for ( int i = 0; i < entry->vmHandleCount; ++i ) {
            if ( entry->vmHandles[i] == vm ) {
                Test_WriteVmCvar( vm, entry->value, entry->modificationCount );
                return;
            }
        }
        if ( entry->vmHandleCount >= MAX_TEST_VM_HANDLES ) {
            return;
        }
        entry->vmHandles[entry->vmHandleCount++] = vm;
        Test_WriteVmCvar( vm, entry->value, entry->modificationCount );
    }

    static testCvarEntry_t *Test_AddEntry( const char *name, const char *value ) {
        if ( s_entryCount >= MAX_TEST_CVARS ) {
            return NULL;
        }
        testCvarEntry_t *entry = &s_entries[s_entryCount++];
        Q_strncpyz( entry->name, name, sizeof( entry->name ) );
        Q_strncpyz( entry->value, value ? value : "", sizeof( entry->value ) );
        entry->vmHandleCount = 0;
        for ( int i = 0; i < MAX_TEST_VM_HANDLES; ++i ) {
            entry->vmHandles[i] = NULL;
        }
        entry->modificationCount = 1;
        return entry;
    }

    static void Test_WriteVmCvar( vmCvar_t *vm, const char *value, int modificationCount ) {
        if ( !vm ) {
            return;
        }
        Q_strncpyz( vm->string, value ? value : "", sizeof( vm->string ) );
        vm->integer = atoi( vm->string );
        vm->value = (float)atof( vm->string );
        vm->modificationCount = modificationCount;
    }

    void trap_Cvar_Register( vmCvar_t *vmCvar, const char *varName, const char *defaultValue, int flags ) {
        testCvarEntry_t *entry = Test_FindEntry( varName );
        if ( !entry ) {
            entry = Test_AddEntry( varName, defaultValue ? defaultValue : "" );
        }
        Test_LinkVmHandle( entry, vmCvar );
    }

    void trap_Cvar_Set( const char *varName, const char *value ) {
        testCvarEntry_t *entry = Test_FindEntry( varName );
        if ( !entry ) {
            entry = Test_AddEntry( varName, value );
        } else {
            Q_strncpyz( entry->value, value ? value : "", sizeof( entry->value ) );
        }
        entry->modificationCount++;
        for ( int i = 0; i < entry->vmHandleCount; ++i ) {
            Test_WriteVmCvar( entry->vmHandles[i], entry->value, entry->modificationCount );
        }
    }

    void trap_Cvar_Update( vmCvar_t *vmCvar ) {
        if ( !vmCvar ) {
            return;
        }
        for ( int i = 0; i < s_entryCount; ++i ) {
            for ( int handle = 0; handle < s_entries[i].vmHandleCount; ++handle ) {
                if ( s_entries[i].vmHandles[handle] == vmCvar ) {
                    Test_WriteVmCvar( vmCvar, s_entries[i].value, s_entries[i].modificationCount );
                    return;
                }
            }
        }
    }

    int Q_stricmp( const char *s1, const char *s2 ) {
        if ( !s1 ) {
            return s2 ? -1 : 0;
        }
        if ( !s2 ) {
            return 1;
        }
        while ( *s1 && *s2 ) {
            const char c1 = (char)tolower( (unsigned char)*s1 );
            const char c2 = (char)tolower( (unsigned char)*s2 );
            if ( c1 != c2 ) {
                return c1 - c2;
            }
            ++s1;
            ++s2;
        }
        return (unsigned char)*s1 - (unsigned char)*s2;
    }

    void Q_strncpyz( char *dest, const char *src, int destsize ) {
        if ( !dest || destsize <= 0 ) {
            return;
        }
        if ( !src ) {
            src = "";
        }
        strncpy( dest, src, destsize - 1 );
        dest[destsize - 1] = 0;
    }

    static void Test_SeedCvar( const char *name, const char *value ) {
        testCvarEntry_t *entry = Test_AddEntry( name, value );
        if ( entry ) {
            entry->modificationCount = 2;
        }
    }

    int main(void) {
        vmCvar_t weaponRespawn;
        vmCvar_t damageGauntlet;
        vmCvar_t weaponRespawnAlias;
        vmCvar_t damageGauntletAlias;
        legacyCvarAlias_t bindings[] = {
            { &weaponRespawn, "g_weaponRespawn", &weaponRespawnAlias, "g_weaponrespawn", "5", 0, -1, -1 },
            { &damageGauntlet, "g_damage_g", &damageGauntletAlias, "g_damage_gauntlet", "50", 0, -1, -1 }
        };

        trap_Cvar_Register( &weaponRespawn, "g_weaponRespawn", "5", 0 );
        trap_Cvar_Register( &damageGauntlet, "g_damage_g", "50", 0 );

        Test_SeedCvar( "g_damage_gauntlet", "80" );
        LegacyCvar_RegisterAliases( bindings, sizeof( bindings ) / sizeof( bindings[0] ) );

        if ( strcmp( damageGauntlet.string, "80" ) != 0 ) {
            puts("register_alias_failed");
            return 1;
        }

        trap_Cvar_Set( "g_damage_gauntlet", "90" );
        LegacyCvar_UpdateAliases( bindings, sizeof( bindings ) / sizeof( bindings[0] ) );
        if ( strcmp( damageGauntlet.string, "90" ) != 0 ) {
            puts("alias_to_primary_failed");
            return 1;
        }

        trap_Cvar_Set( "g_damage_g", "120" );
        LegacyCvar_UpdateAliases( bindings, sizeof( bindings ) / sizeof( bindings[0] ) );
        if ( strcmp( damageGauntletAlias.string, "120" ) != 0 ) {
            puts("primary_to_alias_failed");
            return 1;
        }

        trap_Cvar_Set( "g_weaponrespawn", "7" );
        LegacyCvar_UpdateAliases( bindings, sizeof( bindings ) / sizeof( bindings[0] ) );
        if ( strcmp( weaponRespawn.string, "7" ) != 0 ) {
            puts("weaponrespawn_legacy_failed");
            return 1;
        }

        puts("ok");
        return 0;
    }
    """
)


def test_legacy_cvar_aliases(tmp_path: Path) -> None:
    workdir = tmp_path / "legacy_cvars"
    workdir.mkdir(parents=True, exist_ok=True)

    src_path = workdir / "legacy_cvars_test.c"
    src_path.write_text(_CVAR_ALIAS_PROBE, encoding="utf-8")
    exe_path = workdir / "legacy_cvars_test"

    compile_cmd = [
        "gcc",
        "-std=c99",
        "-Wall",
        "-Werror",
        str(src_path),
        "-I",
        str(REPO_ROOT / "src" / "code" / "game"),
        "-o",
        str(exe_path),
    ]
    subprocess.run(compile_cmd, check=True, cwd=REPO_ROOT)

    result = subprocess.run([str(exe_path)], check=True, capture_output=True, text=True, cwd=REPO_ROOT)
    assert "ok" in result.stdout.splitlines()
