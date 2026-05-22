import pathlib
import unittest

REPO_ROOT = pathlib.Path(__file__).resolve().parents[2]


def _read_source(relative_path: str) -> str:
    return (REPO_ROOT / relative_path).read_text(encoding="utf-8")


def _extract_function_body(source: str, signature: str) -> str:
    start = source.index(signature)
    brace = source.index("{", start)
    depth = 1
    i = brace + 1
    while depth > 0:
        char = source[i]
        if char == "{":
            depth += 1
        elif char == "}":
            depth -= 1
        i += 1
    return source[brace + 1 : i - 1]


class PmoveSettingsConfigstringTests(unittest.TestCase):
    def test_registration_preserves_retail_defaults_and_flag_groups(self) -> None:
        source = _read_source("src/code/game/g_pmove.c")
        body = _extract_function_body(source, "void G_RegisterPmoveCvars( void )")

        self.assertIn("#define PMOVE_CVAR_FLAG_FACTORY_MANAGED\t0x00100000", source)
        self.assertIn("#define PMOVE_CVAR_FLAG_CHANGE_LATCH\t0x00004000", source)
        self.assertIn("#define PMOVE_CVAR_FLAG_CUSTOM_SETTING\t0x00040000", source)
        self.assertNotIn("#define PMOVE_CVAR_FLAGS 0", source)

        expected_registrations = [
            'G_PmoveRegisterCvar( &g_pmove_airAccel_cvar, "pmove_AirAccel", "1.0f", PMOVE_CVAR_FLAGS_CUSTOM_LATCH );',
            'G_PmoveRegisterCvar( &g_pmove_airControl_cvar, "pmove_AirControl", "0", PMOVE_CVAR_FLAGS_CUSTOM );',
            'G_PmoveRegisterCvar( &g_pmove_airStepFriction_cvar, "pmove_AirStepFriction", "0.03f", PMOVE_CVAR_FLAGS_FACTORY );',
            'G_PmoveRegisterCvar( &g_pmove_airSteps_cvar, "pmove_AirSteps", "1", PMOVE_CVAR_FLAGS_CUSTOM_LATCH );',
            'G_PmoveRegisterCvar( &g_pmove_airStopAccel_cvar, "pmove_AirStopAccel", "1.0f", PMOVE_CVAR_FLAGS_FACTORY );',
            'G_PmoveRegisterCvar( &g_pmove_autoHop_cvar, "pmove_AutoHop", "1", PMOVE_CVAR_FLAGS_FACTORY );',
            'G_PmoveRegisterCvar( &g_pmove_bunnyHop_cvar, "pmove_BunnyHop", "1", PMOVE_CVAR_FLAGS_FACTORY );',
            'G_PmoveRegisterCvar( &g_pmove_chainJump_cvar, "pmove_ChainJump", "1", PMOVE_CVAR_FLAGS_FACTORY );',
            'G_PmoveRegisterCvar( &g_pmove_chainJumpVelocity_cvar, "pmove_ChainJumpVelocity", "110.0f", PMOVE_CVAR_FLAGS_FACTORY );',
            'G_PmoveRegisterCvar( &g_pmove_circleStrafeFriction_cvar, "pmove_CircleStrafeFriction", "6.0f", PMOVE_CVAR_FLAGS_FACTORY );',
            'G_PmoveRegisterCvar( &g_pmove_crouchSlide_cvar, "pmove_CrouchSlide", "0", PMOVE_CVAR_FLAGS_FACTORY_ONLY );',
            'G_PmoveRegisterCvar( &g_pmove_crouchSlideFriction_cvar, "pmove_CrouchSlideFriction", "0.5f", PMOVE_CVAR_FLAGS_FACTORY );',
            'G_PmoveRegisterCvar( &g_pmove_crouchSlideTime_cvar, "pmove_CrouchSlideTime", "2000", PMOVE_CVAR_FLAGS_FACTORY );',
            'G_PmoveRegisterCvar( &g_pmove_crouchStepJump_cvar, "pmove_CrouchStepJump", "1", PMOVE_CVAR_FLAGS_FACTORY );',
            'G_PmoveRegisterCvar( &g_pmove_doubleJump_cvar, "pmove_DoubleJump", "0", PMOVE_CVAR_FLAGS_FACTORY_ONLY );',
            'G_PmoveRegisterCvar( &g_pmove_jumpTimeDeltaMin_cvar, "pmove_JumpTimeDeltaMin", "100.0f", PMOVE_CVAR_FLAGS_FACTORY );',
            'G_PmoveRegisterCvar( &g_pmove_jumpVelocity_cvar, "pmove_JumpVelocity", "275.0f", PMOVE_CVAR_FLAGS_FACTORY );',
            'G_PmoveRegisterCvar( &g_pmove_jumpVelocityMax_cvar, "pmove_JumpVelocityMax", "700.0f", PMOVE_CVAR_FLAGS_FACTORY );',
            'G_PmoveRegisterCvar( &g_pmove_jumpVelocityScaleAdd_cvar, "pmove_JumpVelocityScaleAdd", "0.4f", PMOVE_CVAR_FLAGS_FACTORY );',
            'G_PmoveRegisterCvar( &g_pmove_jumpVelocityTimeThreshold_cvar, "pmove_JumpVelocityTimeThreshold", "500.0f", PMOVE_CVAR_FLAGS_FACTORY );',
            'G_PmoveRegisterCvar( &g_pmove_jumpVelocityTimeThresholdOffset_cvar, "pmove_JumpVelocityTimeThresholdOffset", "0.6f", PMOVE_CVAR_FLAGS_FACTORY );',
            'G_PmoveRegisterCvar( &g_pmove_noPlayerClip_cvar, "pmove_noPlayerClip", "0", PMOVE_CVAR_FLAGS_CUSTOM_LATCH );',
            'G_PmoveRegisterCvar( &g_pmove_rampJump_cvar, "pmove_RampJump", "0", PMOVE_CVAR_FLAGS_CUSTOM_LATCH );',
            'G_PmoveRegisterCvar( &g_pmove_rampJumpScale_cvar, "pmove_RampJumpScale", "1.0f", PMOVE_CVAR_FLAGS_FACTORY );',
            'G_PmoveRegisterCvar( &g_pmove_stepHeight_cvar, "pmove_StepHeight", "22.0f", PMOVE_CVAR_FLAGS_CUSTOM_LATCH );',
            'G_PmoveRegisterCvar( &g_pmove_stepJump_cvar, "pmove_StepJump", "1", PMOVE_CVAR_FLAGS_CUSTOM_LATCH );',
            'G_PmoveRegisterCvar( &g_pmove_stepJumpVelocity_cvar, "pmove_StepJumpVelocity", "48.0f", PMOVE_CVAR_FLAGS_FACTORY );',
            'G_PmoveRegisterCvar( &g_pmove_strafeAccel_cvar, "pmove_StrafeAccel", "1.0f", PMOVE_CVAR_FLAGS_FACTORY );',
            'G_PmoveRegisterCvar( &g_pmove_velocityGh_cvar, "pmove_velocity_gh", "800", PMOVE_CVAR_FLAGS_CUSTOM_LATCH );',
            'G_PmoveRegisterCvar( &g_pmove_walkAccel_cvar, "pmove_WalkAccel", "10.0f", PMOVE_CVAR_FLAGS_CUSTOM_LATCH );',
            'G_PmoveRegisterCvar( &g_pmove_walkFriction_cvar, "pmove_WalkFriction", "6.0f", PMOVE_CVAR_FLAGS_FACTORY );',
            'G_PmoveRegisterCvar( &g_pmove_waterSwimScale_cvar, "pmove_WaterSwimScale", "0.6f", PMOVE_CVAR_FLAGS_FACTORY );',
            'G_PmoveRegisterCvar( &g_pmove_waterWadeScale_cvar, "pmove_WaterWadeScale", "0.8f", PMOVE_CVAR_FLAGS_FACTORY );',
            'G_PmoveRegisterCvar( &g_pmove_weaponDropTime_cvar, "pmove_WeaponDropTime", "200", PMOVE_CVAR_FLAGS_CUSTOM_LATCH );',
            'G_PmoveRegisterCvar( &g_pmove_weaponRaiseTime_cvar, "pmove_WeaponRaiseTime", "200", PMOVE_CVAR_FLAGS_CUSTOM_LATCH );',
            'G_PmoveRegisterCvar( &g_pmove_wishSpeed_cvar, "pmove_WishSpeed", "400.0f", PMOVE_CVAR_FLAGS_FACTORY );',
        ]
        position = -1

        for registration in expected_registrations:
            with self.subTest(registration=registration):
                next_position = body.index(registration, position + 1)
                self.assertGreater(next_position, position)
                position = next_position

    def test_legacy_fixed_timestep_pmove_cvars_stay_outside_ql_tuning_slab(self) -> None:
        pmove_source = _read_source("src/code/game/g_pmove.c")
        register_body = _extract_function_body(pmove_source, "void G_RegisterPmoveCvars( void )")
        game_main = _read_source("src/code/game/g_main.c")
        cgame_main = _read_source("src/code/cgame/cg_main.c")
        game_active = _read_source("src/code/game/g_active.c")
        cgame_predict = _read_source("src/code/cgame/cg_predict.c")
        bg_pmove = _read_source("src/code/game/bg_pmove.c")

        self.assertNotIn('"pmove_fixed"', register_body)
        self.assertNotIn('"pmove_msec"', register_body)

        self.assertIn('{ &pmove_fixed, "pmove_fixed", "0", CVAR_SYSTEMINFO, 0, qfalse}', game_main)
        self.assertIn('{ &pmove_msec, "pmove_msec", "8", CVAR_SYSTEMINFO, 0, qfalse}', game_main)
        self.assertIn('{ &pmove_fixed, "pmove_fixed", "0", 0}', cgame_main)
        self.assertIn('{ &pmove_msec, "pmove_msec", "8", 0}', cgame_main)

        for source in (game_active, cgame_predict):
            with self.subTest(source=source[:32]):
                self.assertIn("if ( pmove_msec.integer < 8 )", source)
                self.assertIn('trap_Cvar_Set("pmove_msec", "8");', source)
                self.assertIn("else if (pmove_msec.integer > 33)", source)
                self.assertIn('trap_Cvar_Set("pmove_msec", "33");', source)

        self.assertIn("pm.pmove_fixed = pmove_fixed.integer | client->pers.pmoveFixed;", game_active)
        self.assertIn("pm.pmove_msec = pmove_msec.integer;", game_active)
        self.assertIn("cg_pmove.pmove_fixed = pmove_fixed.integer;// | cg_pmove_fixed.integer;", cgame_predict)
        self.assertIn("cg_pmove.pmove_msec = pmove_msec.integer;", cgame_predict)
        self.assertIn("if ( pmove->pmove_fixed ) {", bg_pmove)
        self.assertIn("if ( msec > pmove->pmove_msec ) {", bg_pmove)
        self.assertIn("if ( msec > 66 ) {", bg_pmove)

    def test_retail_pmove_cvars_are_reset_refreshed_and_cached(self) -> None:
        source = _read_source("src/code/game/g_pmove.c")
        reset_body = _extract_function_body(source, "void G_PmoveResetFactoryManagedCvars( void )")
        refresh_body = _extract_function_body(source, "void G_RefreshPmoveSettings( void )")
        cache_body = _extract_function_body(source, "static void G_PmoveCacheSettings( void )")
        callback_suppressed_cvars = {"pmove_AirControl", "pmove_CrouchSlide", "pmove_DoubleJump"}
        expected_wiring = [
            ("g_pmove_airAccel_cvar", "pmove_AirAccel", "1.0f", "g_pmoveSettings.airAccel = g_pmove_airAccel_cvar.value;"),
            ("g_pmove_airControl_cvar", "pmove_AirControl", "0", "g_pmoveSettings.airControl = g_pmove_airControl_cvar.value;"),
            ("g_pmove_airStepFriction_cvar", "pmove_AirStepFriction", "0.03f", "g_pmoveSettings.airStepFriction = g_pmove_airStepFriction_cvar.value;"),
            ("g_pmove_airSteps_cvar", "pmove_AirSteps", "1", "g_pmoveSettings.airSteps = g_pmove_airSteps_cvar.integer;"),
            ("g_pmove_airStopAccel_cvar", "pmove_AirStopAccel", "1.0f", "g_pmoveSettings.airStopAccel = g_pmove_airStopAccel_cvar.value;"),
            ("g_pmove_autoHop_cvar", "pmove_AutoHop", "1", "g_pmoveSettings.autoHop = ( g_pmove_autoHop_cvar.integer != 0 );"),
            ("g_pmove_bunnyHop_cvar", "pmove_BunnyHop", "1", "g_pmoveSettings.bunnyHop = ( g_pmove_bunnyHop_cvar.integer != 0 );"),
            ("g_pmove_chainJump_cvar", "pmove_ChainJump", "1", "g_pmoveSettings.chainJump = g_pmove_chainJump_cvar.integer;"),
            ("g_pmove_chainJumpVelocity_cvar", "pmove_ChainJumpVelocity", "110.0f", "g_pmoveSettings.chainJumpVelocity = g_pmove_chainJumpVelocity_cvar.value;"),
            ("g_pmove_circleStrafeFriction_cvar", "pmove_CircleStrafeFriction", "6.0f", "g_pmoveSettings.circleStrafeFriction = g_pmove_circleStrafeFriction_cvar.value;"),
            ("g_pmove_crouchSlide_cvar", "pmove_CrouchSlide", "0", "g_pmoveSettings.crouchSlide = ( g_pmove_crouchSlide_cvar.integer != 0 );"),
            ("g_pmove_crouchSlideFriction_cvar", "pmove_CrouchSlideFriction", "0.5f", "g_pmoveSettings.crouchSlideFriction = g_pmove_crouchSlideFriction_cvar.value;"),
            ("g_pmove_crouchSlideTime_cvar", "pmove_CrouchSlideTime", "2000", "g_pmoveSettings.crouchSlideTime = g_pmove_crouchSlideTime_cvar.integer;"),
            ("g_pmove_crouchStepJump_cvar", "pmove_CrouchStepJump", "1", "g_pmoveSettings.crouchStepJump = ( g_pmove_crouchStepJump_cvar.integer != 0 );"),
            ("g_pmove_doubleJump_cvar", "pmove_DoubleJump", "0", "g_pmoveSettings.doubleJump = ( g_pmove_doubleJump_cvar.integer != 0 );"),
            ("g_pmove_jumpTimeDeltaMin_cvar", "pmove_JumpTimeDeltaMin", "100.0f", "g_pmoveSettings.jumpTimeDeltaMin = g_pmove_jumpTimeDeltaMin_cvar.value;"),
            ("g_pmove_jumpVelocity_cvar", "pmove_JumpVelocity", "275.0f", "g_pmoveSettings.jumpVelocity = g_pmove_jumpVelocity_cvar.value;"),
            ("g_pmove_jumpVelocityMax_cvar", "pmove_JumpVelocityMax", "700.0f", "g_pmoveSettings.jumpVelocityMax = g_pmove_jumpVelocityMax_cvar.value;"),
            ("g_pmove_jumpVelocityScaleAdd_cvar", "pmove_JumpVelocityScaleAdd", "0.4f", "g_pmoveSettings.jumpVelocityScaleAdd = g_pmove_jumpVelocityScaleAdd_cvar.value;"),
            ("g_pmove_jumpVelocityTimeThreshold_cvar", "pmove_JumpVelocityTimeThreshold", "500.0f", "g_pmoveSettings.jumpVelocityTimeThreshold = G_PmoveClampRetailMinPositive( g_pmove_jumpVelocityTimeThreshold_cvar.value );"),
            ("g_pmove_jumpVelocityTimeThresholdOffset_cvar", "pmove_JumpVelocityTimeThresholdOffset", "0.6f", "g_pmoveSettings.jumpVelocityTimeThresholdOffset = G_PmoveClampRetailMinPositive( g_pmove_jumpVelocityTimeThresholdOffset_cvar.value );"),
            ("g_pmove_noPlayerClip_cvar", "pmove_noPlayerClip", "0", "noPlayerClip = ( g_pmove_noPlayerClip_cvar.integer != 0 );"),
            ("g_pmove_rampJump_cvar", "pmove_RampJump", "0", "g_pmoveSettings.rampJump = ( g_pmove_rampJump_cvar.integer != 0 );"),
            ("g_pmove_rampJumpScale_cvar", "pmove_RampJumpScale", "1.0f", "g_pmoveSettings.rampJumpScale = g_pmove_rampJumpScale_cvar.value;"),
            ("g_pmove_stepHeight_cvar", "pmove_StepHeight", "22.0f", "g_pmoveSettings.stepHeight = g_pmove_stepHeight_cvar.value;"),
            ("g_pmove_stepJump_cvar", "pmove_StepJump", "1", "g_pmoveSettings.stepJump = ( g_pmove_stepJump_cvar.integer != 0 );"),
            ("g_pmove_stepJumpVelocity_cvar", "pmove_StepJumpVelocity", "48.0f", "g_pmoveSettings.stepJumpVelocity = g_pmove_stepJumpVelocity_cvar.value;"),
            ("g_pmove_strafeAccel_cvar", "pmove_StrafeAccel", "1.0f", "g_pmoveSettings.strafeAccel = g_pmove_strafeAccel_cvar.value;"),
            ("g_pmove_velocityGh_cvar", "pmove_velocity_gh", "800", "g_pmoveSettings.velocityGh = G_PmoveClampRetailMinPositive( g_pmove_velocityGh_cvar.value );"),
            ("g_pmove_walkAccel_cvar", "pmove_WalkAccel", "10.0f", "g_pmoveSettings.walkAccel = g_pmove_walkAccel_cvar.value;"),
            ("g_pmove_walkFriction_cvar", "pmove_WalkFriction", "6.0f", "g_pmoveSettings.walkFriction = g_pmove_walkFriction_cvar.value;"),
            ("g_pmove_waterSwimScale_cvar", "pmove_WaterSwimScale", "0.6f", "g_pmoveSettings.waterSwimScale = g_pmove_waterSwimScale_cvar.value;"),
            ("g_pmove_waterWadeScale_cvar", "pmove_WaterWadeScale", "0.8f", "g_pmoveSettings.waterWadeScale = g_pmove_waterWadeScale_cvar.value;"),
            ("g_pmove_weaponDropTime_cvar", "pmove_WeaponDropTime", "200", "g_pmoveSettings.weaponDropTime = g_pmove_weaponDropTime_cvar.integer;"),
            ("g_pmove_weaponRaiseTime_cvar", "pmove_WeaponRaiseTime", "200", "g_pmoveSettings.weaponRaiseTime = g_pmove_weaponRaiseTime_cvar.integer;"),
            ("g_pmove_wishSpeed_cvar", "pmove_WishSpeed", "400.0f", "g_pmoveSettings.wishSpeed = g_pmove_wishSpeed_cvar.value;"),
        ]

        for variable, name, default, cache_snippet in expected_wiring:
            with self.subTest(cvar=name):
                callback_flag = "qfalse" if name in callback_suppressed_cvars else "qtrue"
                self.assertIn(f'trap_Cvar_Set( "{name}", "{default}" );', reset_body)
                self.assertIn(f'G_PmoveUpdateCvar( &{variable}, "{name}", {callback_flag} );', refresh_body)
                self.assertIn(cache_snippet, cache_body)

        self.assertIn('G_PmoveUpdateCvar( &g_instaGib, "g_instaGib", qfalse );', refresh_body)

    def test_retail_pmove_update_callbacks_and_positive_clamps_are_reconstructed(self) -> None:
        source = _read_source("src/code/game/g_pmove.c")
        update_body = _extract_function_body(
            source,
            "static void G_PmoveUpdateCvar( vmCvar_t *vmCvar, const char *name, qboolean trackChange )",
        )
        clamp_body = _extract_function_body(source, "static float G_PmoveClampRetailMinPositive( float value )")

        self.assertIn("#define PMOVE_RETAIL_MIN_POSITIVE\t0.001f", source)
        self.assertIn("value >= PMOVE_RETAIL_MIN_POSITIVE", clamp_body)
        self.assertIn("modificationCount = vmCvar->modificationCount;", update_body)
        self.assertIn("trap_Cvar_Update( vmCvar );", update_body)
        self.assertIn("vmCvar->modificationCount == modificationCount", update_body)
        self.assertIn("if ( g_cheats.integer != 0 )", update_body)
        self.assertIn('trap_SendServerCommand( -1, va( "print \\"Server: %s changed to %s\\n\\"", name, vmCvar->string ) );', update_body)

    def test_serialization_uses_retail_compact_core_order(self) -> None:
        source = _read_source("src/code/game/g_pmove.c")
        body = _extract_function_body(
            source,
            "static qboolean G_PmoveSerializeSettings( const pmove_settings_t *settings, char *buffer, size_t bufferSize )",
        )
        expected_fields = [
            "settings->airAccel",
            "settings->airStepFriction",
            "settings->airSteps",
            "settings->airStopAccel",
            "settings->autoHop ? 1 : 0",
            "settings->bunnyHop ? 1 : 0",
            "settings->chainJump",
            "(int)settings->chainJumpVelocity",
            "settings->circleStrafeFriction",
            "settings->crouchSlideFriction",
            "settings->crouchSlideTime",
            "settings->crouchStepJump ? 1 : 0",
            "settings->jumpTimeDeltaMin",
            "settings->jumpVelocity",
            "settings->jumpVelocityMax",
            "settings->jumpVelocityScaleAdd",
            "settings->jumpVelocityTimeThreshold",
            "settings->jumpVelocityTimeThresholdOffset",
            "settings->noPlayerClip ? 1 : 0",
            "settings->rampJump ? 1 : 0",
            "settings->rampJumpScale",
            "settings->stepHeight",
            "settings->stepJump ? 1 : 0",
            "settings->stepJumpVelocity",
            "settings->strafeAccel",
            "settings->velocityGh",
            "settings->walkAccel",
            "settings->walkFriction",
            "settings->waterSwimScale",
            "settings->waterWadeScale",
            "settings->weaponDropTime",
            "settings->weaponRaiseTime",
            "settings->wishSpeed",
        ]
        position = -1

        for field in expected_fields:
            with self.subTest(field=field):
                next_position = body.index(field, position + 1)
                self.assertGreater(next_position, position)
                position = next_position

    def test_serialization_keeps_source_extension_after_retail_core(self) -> None:
        source = _read_source("src/code/game/g_pmove.c")
        body = _extract_function_body(
            source,
            "static qboolean G_PmoveSerializeSettings( const pmove_settings_t *settings, char *buffer, size_t bufferSize )",
        )
        self.assertIn("Retail cgame consumes only the first 33 tokens.", body)
        self.assertLess(body.index("settings->wishSpeed"), body.index("settings->airControl"))
        self.assertIn("settings->crouchSlide ? 1 : 0", body)
        self.assertIn("settings->doubleJump ? 1 : 0", body)
        self.assertNotIn("flightThrust", body)
        self.assertNotIn("\\\"weaponReloadTimes\\\"", body)


if __name__ == "__main__":
    unittest.main()
