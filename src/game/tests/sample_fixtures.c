#include "fixture_runner.h"

#if defined(__has_include)
#if __has_include("bg_public.h")
#include "bg_public.h"
#elif __has_include("../code/game/bg_public.h")
#include "../code/game/bg_public.h"
#elif __has_include("../../code/game/bg_public.h")
#include "../../code/game/bg_public.h"
#else
#error "Unable to locate bg_public.h for sample fixtures"
#endif
#else
#include "../../code/game/bg_public.h"
#endif

#include <string.h>

static qboolean GT_SampleTrajectoryLinear(void) {
    trajectory_t trajectory;
    vec3_t point;

    memset(&trajectory, 0, sizeof(trajectory));
    trajectory.trType = TR_LINEAR;
    trajectory.trTime = 1000;
    VectorSet(trajectory.trBase, 0.0f, 0.0f, 0.0f);
    VectorSet(trajectory.trDelta, 100.0f, 0.0f, 0.0f);

    BG_EvaluateTrajectory(&trajectory, 1500, point);

    if (Q_fabs(point[0] - 50.0f) > 0.1f) {
        return GT_Failf("expected x to advance 50 units, received %.2f", point[0]);
    }

    if (Q_fabs(point[1]) > 0.01f || Q_fabs(point[2]) > 0.01f) {
        return GT_Failf("expected trajectory to stay on x-axis, received (%.2f, %.2f)", point[1], point[2]);
    }

    return qtrue;
}

static const game_fixture_t gt_sample_rules_fixtures[] = {
    {
        "trajectory_linear_progression",
        NULL,
        GT_SampleTrajectoryLinear,
        NULL,
        "Validates BG_EvaluateTrajectory for linear motion"
    }
};

game_fixture_result_t GT_RunSampleRulesFixtures(void) {
    game_fixture_reporter_t reporter;
    GT_InitDefaultReporter(&reporter);
    return GT_RunFixtureSuite(
        "sample_rules",
        gt_sample_rules_fixtures,
        GAME_TESTS_ARRAY_LEN(gt_sample_rules_fixtures),
        &reporter);
}
