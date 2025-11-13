from __future__ import annotations

import subprocess
import textwrap
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent


def _compile_and_run(source: str, workdir: Path) -> str:
    workdir.mkdir(parents=True, exist_ok=True)
    c_path = workdir / "probe.c"
    exe_path = workdir / "probe"
    c_path.write_text(source, encoding="utf-8")

    include_args = [
        f"-I{REPO_ROOT}",
        "-Isrc/common",
        "-Isrc/code",
        "-Isrc/code/game",
        "-Isrc/code/qcommon",
    ]

    compile_cmd = [
        "gcc",
        "-std=c99",
        "-Wall",
        "-Werror",
        *include_args,
        str(c_path),
        "src/code/game/g_autoshuffle.c",
        "-o",
        str(exe_path),
    ]
    subprocess.run(compile_cmd, check=True, cwd=REPO_ROOT)

    result = subprocess.run([str(exe_path)], check=True, cwd=REPO_ROOT, capture_output=True, text=True)
    return result.stdout


def test_auto_shuffle_countdown_announces_each_second(tmp_path: Path) -> None:
    source = textwrap.dedent(
        """
        #include <stdarg.h>
        #include <stdio.h>
        #include <string.h>

        #include "src/code/game/g_local.h"

        level_locals_t level;

        static int g_event_count = 0;
        static qboolean g_guard_locked = qfalse;

        static qboolean AutoShuffleGuard(void) {
            return g_guard_locked;
        }

        static void Step(int delta) {
            level.previousTime = level.time;
            level.time += delta;
            G_AutoShuffleCountdown_Frame();
        }

        char *va(char *fmt, ...) {
            static char buffer[256];
            va_list args;
            va_start(args, fmt);
            vsnprintf(buffer, sizeof(buffer), fmt, args);
            va_end(args);
            return buffer;
        }

        void trap_SendServerCommand( int clientNum, const char *text ) {
            (void)clientNum;
            fputs("EVENT:", stdout);
            for (const char *ch = text; *ch; ++ch) {
                if (*ch == '\\n') {
                    fputs("\\n", stdout);
                } else {
                    putchar(*ch);
                }
            }
            fputc(10, stdout);
            g_event_count++;
        }

        int main(void) {
            G_AutoShuffleCountdown_SetGuard(AutoShuffleGuard);

            level.time = 1000;
            G_AutoShuffleCountdown_Arm(5000);
            printf("REMAIN:start:%d\\n", G_AutoShuffleCountdown_GetSecondsRemaining());
            G_AutoShuffleCountdown_Frame();

            Step(500);
            Step(500);
            Step(1000);
            Step(1000);
            Step(1000);
            Step(1000);
            printf("STATE:after-first:%d\\n", G_AutoShuffleCountdown_IsActive() ? 1 : 0);

            G_AutoShuffleCountdown_Arm(4000);
            g_guard_locked = qtrue;
            G_AutoShuffleCountdown_Frame();
            Step(1000);
            Step(1000);
            g_guard_locked = qfalse;
            G_AutoShuffleCountdown_Frame();
            Step(500);
            Step(600);
            Step(1000);
            printf("STATE:after-guard:%d\\n", G_AutoShuffleCountdown_IsActive() ? 1 : 0);

            G_AutoShuffleCountdown_Arm(3000);
            G_AutoShuffleCountdown_Frame();
            G_AutoShuffleCountdown_Cancel();
            printf("STATE:after-cancel:%d\\n", G_AutoShuffleCountdown_IsActive() ? 1 : 0);
            Step(500);
            G_AutoShuffleCountdown_Frame();

            printf("EVENTS:%d\\n", g_event_count);
            return 0;
        }
        """
    )

    output = _compile_and_run(source, tmp_path / "autoshuffle")
    lines = [line.strip() for line in output.splitlines() if line.strip()]

    events = [line.split(":", 1)[1] for line in lines if line.startswith("EVENT:")]
    assert events[:5] == [
        'cp "Auto-Shuffling Teams in 5 seconds.\\n"',
        'cp "Auto-Shuffling Teams in 4 seconds.\\n"',
        'cp "Auto-Shuffling Teams in 3 seconds.\\n"',
        'cp "Auto-Shuffling Teams in 2 seconds.\\n"',
        'cp "Auto-Shuffling Teams in 1 seconds.\\n"',
    ]

    # Guarded countdown should only announce once the lock clears.
    guard_events = [evt for evt in events if "Teams in 2" in evt or "Teams in 1" in evt][2:]
    assert guard_events == [
        'cp "Auto-Shuffling Teams in 2 seconds.\\n"',
        'cp "Auto-Shuffling Teams in 1 seconds.\\n"',
    ]

    assert any(line == "STATE:after-first:0" for line in lines)
    assert any(line == "STATE:after-guard:0" for line in lines)
    assert any(line == "STATE:after-cancel:0" for line in lines)

    final_event_count = next((int(line.split(":", 1)[1]) for line in lines if line.startswith("EVENTS:")), None)
    assert final_event_count == len(events)

    # Ensure cancellation prevented any further announcements.
    assert events.count('cp "Auto-Shuffling Teams in 1 seconds.\\n"') == 2
