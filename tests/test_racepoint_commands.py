"""Tests for the racepoint admin command metadata pipeline."""
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

    include_args = [
        f"-I{REPO_ROOT}",
        "-Isrc",  # ensure q_shared and friends resolve like the engine build.
        "-Isrc/code",
        "-Isrc/code/game",
        "-Isrc/code/qcommon",
        "-Isrc/code/botlib",
    ]

    compile_cmd = [
        "gcc",
        "-std=c99",
        "-Wall",
        "-Werror",
        *include_args,
        str(c_path),
        "src/code/game/g_race.c",
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


def test_racepoint_command_emits_metadata(tmp_path: Path) -> None:
    source = textwrap.dedent(
        r"""
        #include <ctype.h>
        #include <stdarg.h>
        #include <stdio.h>
        #include <stdlib.h>
        #include <string.h>

        #include "src/code/game/g_local.h"

        level_locals_t level;
        gentity_t g_entities[MAX_GENTITIES];
        gclient_t g_clients[MAX_CLIENTS];
        vmCvar_t g_gametype;
        vmCvar_t g_cheats;

        static int g_cmd_argc = 0;
        static const char *g_cmd_argv[4];

        static void Test_SetArgs(int argc, const char **argv) {
            g_cmd_argc = argc;
            for (int i = 0; i < 4; ++i) {
                if (i < argc) {
                    g_cmd_argv[i] = argv[i];
                } else {
                    g_cmd_argv[i] = "";
                }
            }
        }

        int trap_Argc(void) {
            return g_cmd_argc;
        }

        void trap_Argv(int n, char *buffer, int bufferLength) {
            if (!buffer || bufferLength <= 0) {
                return;
            }
            if (n < 0 || n >= g_cmd_argc || !g_cmd_argv[n]) {
                buffer[0] = '\0';
                return;
            }
            Q_strncpyz(buffer, g_cmd_argv[n], bufferLength);
        }

        char *va(char *fmt, ...) {
            static char buffers[4][1024];
            static int index = 0;
            char *buffer = buffers[index];
            index = (index + 1) % 4;

            va_list args;
            va_start(args, fmt);
            vsnprintf(buffer, sizeof(buffers[0]), fmt, args);
            va_end(args);
            return buffer;
        }

        char *vtos(const vec3_t v) {
            return va("%.2f %.2f %.2f", v[0], v[1], v[2]);
        }

        void QDECL Com_sprintf(char *dest, int size, const char *fmt, ...) {
            va_list args;
            va_start(args, fmt);
            vsnprintf(dest, size, fmt, args);
            va_end(args);
        }

        void Q_strncpyz(char *dest, const char *src, int destsize) {
            int i;
            if (!dest || destsize <= 0) {
                return;
            }
            if (!src) {
                dest[0] = '\0';
                return;
            }
            for (i = 0; i < destsize - 1 && src[i]; ++i) {
                dest[i] = src[i];
            }
            dest[i] = '\0';
        }

        void Q_strcat(char *dest, int size, const char *src) {
            int len;
            int copy;

            if (!dest || !src) {
                return;
            }

            len = (int)strlen(dest);
            copy = size - len - 1;
            if (copy <= 0) {
                return;
            }
            if ((int)strlen(src) < copy) {
                copy = (int)strlen(src);
            }
            memcpy(dest + len, src, copy);
            dest[len + copy] = '\0';
        }

        int Q_stricmp(const char *s1, const char *s2) {
            unsigned char c1;
            unsigned char c2;
            if (s1 == s2) {
                return 0;
            }
            while (*s1 || *s2) {
                c1 = (unsigned char)tolower((unsigned char)*s1++);
                c2 = (unsigned char)tolower((unsigned char)*s2++);
                if (c1 != c2) {
                    return (int)c1 - (int)c2;
                }
            }
            return 0;
        }

        gentity_t *G_Find(gentity_t *from, int fieldofs, const char *match) {
            int start = 0;
            if (from) {
                start = (int)(from - g_entities) + 1;
            }
            for (int i = start; i < MAX_GENTITIES; ++i) {
                gentity_t *ent = &g_entities[i];
                const char **field = (const char **)((byte *)ent + fieldofs);
                if (!ent->inuse || !*field) {
                    continue;
                }
                if (!strcmp(*field, match)) {
                    return ent;
                }
            }
            return NULL;
        }

        gentity_t *G_Spawn(void) {
            for (int i = 0; i < MAX_GENTITIES; ++i) {
                if (!g_entities[i].inuse) {
                    memset(&g_entities[i], 0, sizeof(g_entities[i]));
                    g_entities[i].inuse = qtrue;
                    g_entities[i].s.number = i;
                    return &g_entities[i];
                }
            }
            return NULL;
        }

        void G_FreeEntity(gentity_t *ent) {
            if (!ent) {
                return;
            }
            memset(ent, 0, sizeof(*ent));
        }

        char *G_NewString(const char *string) {
            size_t len;
            char *copy;
            if (!string) {
                return NULL;
            }
            len = strlen(string) + 1;
            copy = malloc(len);
            if (!copy) {
                return NULL;
            }
            memcpy(copy, string, len);
            return copy;
        }

        void QDECL G_Printf(const char *fmt, ...) {
            va_list args;
            va_start(args, fmt);
            fputs("PRINTF:", stdout);
            vfprintf(stdout, fmt, args);
            va_end(args);
        }

        void G_SetOrigin(gentity_t *ent, vec3_t origin) {
            if (!ent) {
                return;
            }
            VectorCopy(origin, ent->s.origin);
            VectorCopy(origin, ent->r.currentOrigin);
        }

        void trap_LinkEntity(gentity_t *ent) {
            (void)ent;
        }

        void trap_Trace(trace_t *results, const vec3_t start, const vec3_t mins, const vec3_t maxs,
                const vec3_t end, int passEntityNum, int contentmask) {
            (void)mins;
            (void)maxs;
            (void)end;
            (void)passEntityNum;
            (void)contentmask;
            memset(results, 0, sizeof(*results));
            results->fraction = 1.0f;
            VectorCopy(start, results->endpos);
            results->endpos[2] = 32.0f;
            results->entityNum = ENTITYNUM_WORLD;
        }

        void trap_SendServerCommand(int clientNum, const char *text) {
            printf("CMD:%d:%s\n", clientNum, text);
        }

        void trap_SetConfigstring(int num, const char *string) {
            printf("CFG:%d:%s\n", num, string);
        }

        void trap_Print(const char *text) {
            printf("PRINT:%s\n", text);
        }

        char *ConcatArgs(int start);  /* unused but referenced by headers */

        void trap_SendConsoleCommand(int exec_when, const char *text);

        char *ConcatArgs(int start) {
            (void)start;
            return "";
        }

        void trap_SendConsoleCommand(int exec_when, const char *text) {
            (void)exec_when;
            (void)text;
        }

        char *Info_ValueForKey(const char *s, const char *key);
        char *Info_ValueForKey(const char *s, const char *key) {
            (void)s;
            (void)key;
            return "";
        }

        void trap_GetServerinfo(char *buffer, int bufferSize) {
            if (bufferSize > 0) {
                buffer[0] = '\0';
            }
        }

        void trap_GetConfigstring(int num, char *buffer, int bufferSize) {
            (void)num;
            if (bufferSize > 0) {
                buffer[0] = '\0';
            }
        }

        void trap_ArgvBuffer(int arg, char *buffer, int bufferSize) {
            (void)arg;
            if (bufferSize > 0) {
                buffer[0] = '\0';
            }
        }

        int main(void) {
            gentity_t *admin;
            const char *spawnArgs[] = { "racepoint" };
            const char *dumpArgs[] = { "racepoint", "dump" };
            const char *clearArgs[] = { "racepoint", "clear" };

            memset(&level, 0, sizeof(level));
            memset(g_entities, 0, sizeof(g_entities));
            memset(g_clients, 0, sizeof(g_clients));

            level.clients = g_clients;
            level.maxclients = 1;
            level.gentities = g_entities;
            level.gentitySize = sizeof(gentity_t);

            admin = &g_entities[0];
            admin->inuse = qtrue;
            admin->client = &g_clients[0];
            admin->classname = "player";
            admin->health = 100;
            admin->s.number = 0;
            VectorSet(admin->s.origin, 128.0f, -64.0f, 256.0f);
            VectorCopy(admin->s.origin, admin->r.currentOrigin);
            admin->racePointIndex = -1;
            g_clients[0].pers.connected = CON_CONNECTED;

            g_gametype.integer = GT_RACE;
            g_cheats.integer = 1;

            G_RaceInitLevel();

            Test_SetArgs(1, spawnArgs);
            G_RaceAdminCommand(admin);

            Test_SetArgs(2, dumpArgs);
            G_RaceAdminCommand(admin);

            G_RaceSendInfoCommand(-1);

            Test_SetArgs(2, clearArgs);
            G_RaceAdminCommand(admin);

            G_RaceSendInfoCommand(-1);

            printf("DONE\n");
            return 0;
        }
        """
    )

    output = _compile_and_run(source, tmp_path / "racepoint")
    lines = [line.strip() for line in output.splitlines() if line.strip()]

    cmd_lines = [line for line in lines if line.startswith("CMD:")]

    # Spawning a point should print a helpful message, emit metadata, and broadcast race_init.
    spawn_prints = [line for line in cmd_lines if 'print "spawning a race point' in line]
    assert spawn_prints, output

    admin_payloads = [line for line in cmd_lines if "admin_race_point_0" in line]
    assert len(admin_payloads) >= 2, output

    assert any(line == "CMD:-1:race_init 1" for line in cmd_lines), output
    assert any(line.startswith("CMD:-1:race_info 1") for line in cmd_lines), output

    dump_lines = [line for line in cmd_lines if "targetname=admin_race_point_0" in line]
    assert dump_lines and dump_lines[0].startswith("CMD:0:print \"0:"), output

    assert any(line.startswith("CMD:0:print \"clearing race points") for line in cmd_lines), output
    assert any(line == "CMD:-1:race_init 0" for line in cmd_lines), output
    assert any(line.startswith("CMD:-1:race_info 0") for line in cmd_lines), output

    assert lines[-1] == "DONE"
