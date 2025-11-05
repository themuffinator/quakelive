#include "fixture_runner.h"
#include "syscall_mocks.h"

#include <stdarg.h>

static char gt_failure_message[256];
static qboolean gt_failure_active = qfalse;

static void GT_DefaultFixtureStart(const char *name, void *user);
static void GT_DefaultFixtureSuccess(const char *name, void *user);
static void GT_DefaultFixtureFailure(const char *name, const char *message, void *user);

void GT_ResetFailure(void) {
    gt_failure_message[0] = '\0';
    gt_failure_active = qfalse;
}

qboolean GT_Failf(const char *fmt, ...) {
    va_list args;
    va_start(args, fmt);
    Q_vsnprintf(gt_failure_message, sizeof(gt_failure_message), fmt, args);
    va_end(args);
    gt_failure_active = qtrue;
    return qfalse;
}

const char *GT_LastFailure(void) {
    return gt_failure_active ? gt_failure_message : "";
}

void GT_InitDefaultReporter(game_fixture_reporter_t *reporter) {
    if (!reporter) {
        return;
    }

    reporter->on_fixture_start = GT_DefaultFixtureStart;
    reporter->on_fixture_success = GT_DefaultFixtureSuccess;
    reporter->on_fixture_failure = GT_DefaultFixtureFailure;
    reporter->user = NULL;
}

static void GT_DefaultFixtureStart(const char *name, void *user) {
    (void)user;
    trap_Printf("[rules] %s\n", name);
}

static void GT_DefaultFixtureSuccess(const char *name, void *user) {
    (void)user;
    trap_Printf("  PASS %s\n", name);
}

static void GT_DefaultFixtureFailure(const char *name, const char *message, void *user) {
    (void)user;
    trap_Printf("  FAIL %s\n", name);
    if (message && message[0]) {
        trap_Printf("    %s\n", message);
    }
}

game_fixture_result_t GT_RunFixtureSuite(
    const char *suite_name,
    const game_fixture_t *fixtures,
    int fixture_count,
    const game_fixture_reporter_t *reporter) {
    game_fixture_reporter_t local_reporter;
    game_fixture_result_t result = {0, 0};

    if (!fixtures || fixture_count <= 0) {
        return result;
    }

    if (!reporter) {
        GT_InitDefaultReporter(&local_reporter);
        reporter = &local_reporter;
    }

    // Ensure the syscall surface is bound before any fixture calls trap_*.
    GT_ResetSyscallMocks();

    if (suite_name) {
        trap_Printf("[rules-suite] %s\n", suite_name);
    }

    for (int i = 0; i < fixture_count; ++i) {
        const game_fixture_t *fixture = &fixtures[i];
        qboolean passed = qtrue;

        result.executed++;
        GT_ResetFailure();

        if (fixture->name && reporter->on_fixture_start) {
            reporter->on_fixture_start(fixture->name, reporter->user);
        }

        if (fixture->setup) {
            passed = fixture->setup();
        }

        if (passed && fixture->run) {
            passed = fixture->run();
        }

        if (fixture->teardown) {
            qboolean teardown_ok = fixture->teardown();
            passed = passed && teardown_ok;
        }

        if (!passed) {
            const char *message = GT_LastFailure();
            result.failed++;
            if (reporter->on_fixture_failure) {
                if (!message || !message[0]) {
                    message = "Fixture returned failure";
                }
                reporter->on_fixture_failure(fixture->name ? fixture->name : "<unnamed>", message, reporter->user);
            }
        } else if (reporter->on_fixture_success) {
            reporter->on_fixture_success(fixture->name ? fixture->name : "<unnamed>", reporter->user);
        }
    }

    return result;
}
