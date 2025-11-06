#include "rules_fixtures.h"

#if defined(__has_include)
#if __has_include("bg_public.h")
#include "bg_public.h"
#elif __has_include("../code/game/bg_public.h")
#include "../code/game/bg_public.h"
#elif __has_include("../../code/game/bg_public.h")
#include "../../code/game/bg_public.h"
#else
#error "Unable to locate bg_public.h for item fixtures"
#endif
#else
#include "../../code/game/bg_public.h"
#endif

#include <string.h>

static qboolean GT_ItemFindsRocketLauncher(void) {
    const gitem_t *rocket = BG_FindItemForWeapon(WP_ROCKET_LAUNCHER);

    if (!rocket) {
        return GT_Failf("BG_FindItemForWeapon(WP_ROCKET_LAUNCHER) returned NULL");
    }

    if (rocket->giType != IT_WEAPON) {
        return GT_Failf("expected giType IT_WEAPON, received %d", rocket->giType);
    }

    if (rocket->quantity != 10) {
        return GT_Failf("expected rocket launcher quantity 10, received %d", rocket->quantity);
    }

    if (Q_stricmp(rocket->pickup_name, "Rocket Launcher") != 0) {
        return GT_Failf("unexpected pickup name '%s'", rocket->pickup_name);
    }

    return qtrue;
}

static qboolean GT_PlayerTouchWithinPickupBounds(void) {
    playerState_t ps;
    entityState_t item;

    memset(&ps, 0, sizeof(ps));
    memset(&item, 0, sizeof(item));

    VectorSet(ps.origin, 128.0f, 64.0f, 24.0f);

    item.pos.trType = TR_STATIONARY;
    item.pos.trTime = 0;
    VectorCopy(ps.origin, item.pos.trBase);

    if (!BG_PlayerTouchesItem(&ps, &item, 0)) {
        return GT_Failf("expected player to touch item when aligned within bounds");
    }

    return qtrue;
}

static qboolean GT_PlayerTouchRejectsWideOffset(void) {
    playerState_t ps;
    entityState_t item;

    memset(&ps, 0, sizeof(ps));
    memset(&item, 0, sizeof(item));

    VectorSet(ps.origin, 0.0f, 0.0f, 0.0f);

    item.pos.trType = TR_STATIONARY;
    item.pos.trTime = 0;
    VectorSet(item.pos.trBase, 60.0f, 0.0f, 0.0f);

    if (BG_PlayerTouchesItem(&ps, &item, 0)) {
        return GT_Failf("expected player outside x-bounds to miss pickup");
    }

    return qtrue;
}

static const game_fixture_t gt_item_rules_fixtures[] = {
    {
        "find_rocket_launcher",
        NULL,
        GT_ItemFindsRocketLauncher,
        NULL,
        "Ensures BG_FindItemForWeapon exposes the rocket launcher metadata"
    },
    {
        "touch_within_bounds",
        NULL,
        GT_PlayerTouchWithinPickupBounds,
        NULL,
        "Validates BG_PlayerTouchesItem accepts aligned pickups"
    },
    {
        "touch_rejects_wide_offset",
        NULL,
        GT_PlayerTouchRejectsWideOffset,
        NULL,
        "Validates BG_PlayerTouchesItem rejects pickups beyond the x tolerance"
    }
};

game_fixture_result_t GT_RunItemRulesFixtures(void) {
    game_fixture_reporter_t reporter;
    GT_InitDefaultReporter(&reporter);
    return GT_RunFixtureSuite(
        "item_rules",
        gt_item_rules_fixtures,
        GAME_TESTS_ARRAY_LEN(gt_item_rules_fixtures),
        &reporter);
}
