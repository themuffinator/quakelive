#ifndef GAME_TESTS_FIXTURE_RUNNER_H
#define GAME_TESTS_FIXTURE_RUNNER_H

#if defined(__has_include)
#if __has_include("q_shared.h")
#include "q_shared.h"
#elif __has_include("../code/game/q_shared.h")
#include "../code/game/q_shared.h"
#elif __has_include("../../code/game/q_shared.h")
#include "../../code/game/q_shared.h"
#else
#error "Unable to locate q_shared.h for fixture runner"
#endif
#else
#include "../../code/game/q_shared.h"
#endif

#include "../ql_game_types.h"

// Basic macro utilities reused in fixtures
#ifndef GAME_TESTS_ARRAY_LEN
#define GAME_TESTS_ARRAY_LEN(arr) (int)(sizeof(arr) / sizeof((arr)[0]))
#endif

// Forward declaration to avoid including stdarg consumers in headers.
typedef qboolean (*game_fixture_step_t)(void);

typedef struct game_fixture_s {
    const char *name;
    game_fixture_step_t setup;
    game_fixture_step_t run;
    game_fixture_step_t teardown;
    const char *description;
} game_fixture_t;

typedef struct game_fixture_reporter_s {
    void (*on_fixture_start)(const char *name, void *user);
    void (*on_fixture_success)(const char *name, void *user);
    void (*on_fixture_failure)(const char *name, const char *message, void *user);
    void *user;
} game_fixture_reporter_t;

typedef struct game_fixture_result_s {
    int executed;
    int failed;
} game_fixture_result_t;

// Executes a suite and returns the aggregated result counters.
game_fixture_result_t GT_RunFixtureSuite(
    const char *suite_name,
    const game_fixture_t *fixtures,
    int fixture_count,
    const game_fixture_reporter_t *reporter);

// Populates a reporter that prints over trap_Printf/trap_Error. Safe for both DLL and QVM builds.
void GT_InitDefaultReporter(game_fixture_reporter_t *reporter);

// Resets the failure latch captured by GT_Failf.
void GT_ResetFailure(void);

// Records a formatted failure message and returns qfalse for convenient "return" chaining.
qboolean GT_Failf(const char *fmt, ...);

// Returns the last formatted failure message. Empty string if no failure was recorded.
const char *GT_LastFailure(void);

#endif // GAME_TESTS_FIXTURE_RUNNER_H
