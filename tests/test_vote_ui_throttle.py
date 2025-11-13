from __future__ import annotations

import subprocess
import textwrap
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent

_VOTE_THROTTLE_PROBE = textwrap.dedent(
    """
    #include <stdio.h>
    #include <string.h>

    #define QAGAME 1
    #include "g_vote.c"

    vmCvar_t g_voteDelay;
    vmCvar_t g_voteLimit;
    vmCvar_t g_voteFlags;

    level_locals_t level;
    gclient_t localClients[MAX_CLIENTS];

    void trap_SendServerCommand( int clientNum, const char *text ) {
        if ( text ) {
            printf("%d:%s\\n", clientNum, text);
        }
    }

    int main(void) {
        memset(&level, 0, sizeof(level));
        memset(localClients, 0, sizeof(localClients));

        g_voteDelay.value = 2.0f;
        g_voteDelay.integer = 2;
        g_voteLimit.integer = 3;
        g_voteLimit.value = 3.0f;
        g_voteFlags.integer = 0;
        g_voteFlags.value = 0.0f;

        level.maxclients = 1;
        level.clients = localClients;

        G_InitClientVoteThrottle(&level.clients[0]);
        level.clients[0].pers.connected = CON_CONNECTED;

        level.time = 1000;
        level.framenum = 0;

        G_RegisterVoteCall(&level.clients[0], 0, 7);

        int throttle = level.voteDelayMsec;

        level.time = level.clients[0].pers.voteDelayTime + throttle - 1;
        level.framenum = 1;
        G_UpdateVoteThrottle();

        level.time = level.clients[0].pers.voteDelayTime + throttle;
        level.framenum = 2;
        G_UpdateVoteThrottle();

        level.time += 100;
        level.framenum = 3;
        G_UpdateVoteThrottle();

        G_RegisterVoteCall(&level.clients[0], 0, 9);

        throttle = level.voteDelayMsec;

        level.time = level.clients[0].pers.voteDelayTime + throttle - 1;
        level.framenum = 4;
        G_UpdateVoteThrottle();

        level.time = level.clients[0].pers.voteDelayTime + throttle;
        level.framenum = 5;
        G_UpdateVoteThrottle();

        level.framenum = 6;
        G_UpdateVoteThrottle();

        return 0;
    }
    """
)

_VOTE_LIMIT_PROBE = textwrap.dedent(
    """
    #include <stdio.h>
    #include <string.h>

    #define QAGAME 1
    #include "g_vote.c"

    vmCvar_t g_voteDelay;
    vmCvar_t g_voteLimit;
    vmCvar_t g_voteFlags;

    level_locals_t level;
    gclient_t localClients[MAX_CLIENTS];

    void trap_SendServerCommand( int clientNum, const char *text ) {
        if ( text ) {
            printf("%d:%s\\n", clientNum, text);
        }
    }

    int main(void) {
        memset(&level, 0, sizeof(level));
        memset(localClients, 0, sizeof(localClients));

        g_voteDelay.value = 1.0f;
        g_voteDelay.integer = 1;
        g_voteLimit.integer = 1;
        g_voteLimit.value = 1.0f;
        g_voteFlags.integer = 0;
        g_voteFlags.value = 0.0f;

        level.maxclients = 1;
        level.clients = localClients;

        G_InitClientVoteThrottle(&level.clients[0]);
        level.clients[0].pers.connected = CON_CONNECTED;

        level.time = 500;
        level.framenum = 0;

        G_RegisterVoteCall(&level.clients[0], 0, 3);

        int throttle = level.voteDelayMsec;

        level.time = level.clients[0].pers.voteDelayTime + throttle;
        level.framenum = 1;
        G_UpdateVoteThrottle();

        g_voteLimit.integer = 2;
        g_voteLimit.value = 2.0f;

        level.framenum = 2;
        G_UpdateVoteThrottle();

        level.framenum = 3;
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

    compile_cmd = [
        "gcc",
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


def test_vote_ui_limit_unlocks(tmp_path: Path) -> None:
    """Raising g_voteLimit mid-match re-enables the UI when the throttle has elapsed."""

    workdir = tmp_path / "vote_limit"
    workdir.mkdir(parents=True, exist_ok=True)

    c_path = workdir / "probe.c"
    c_path.write_text(_VOTE_LIMIT_PROBE, encoding="utf-8")
    exe_path = workdir / "probe"

    include_args = [
        f"-I{REPO_ROOT / 'src' / 'code' / 'game'}",
        f"-I{REPO_ROOT / 'src' / 'code'}",
        f"-I{REPO_ROOT / 'src'}",
    ]

    compile_cmd = [
        "gcc",
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
    ]
