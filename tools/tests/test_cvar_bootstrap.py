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


class CVarBootstrapTests(unittest.TestCase):
    def test_header_declares_weapon_reload_config(self) -> None:
        header = _read_source("src/code/game/g_local.h")
        self.assertIn("typedef struct weaponReloadConfig_s", header)
        self.assertIn("extern weaponReloadConfig_t g_weaponReloadConfig;", header)

    def test_header_declares_knockback_config(self) -> None:
        header = _read_source("src/code/game/g_local.h")
        self.assertIn("typedef struct knockbackConfig_s", header)
        self.assertIn("extern knockbackConfig_t g_knockbackConfig;", header)

    def test_header_exposes_weapon_cvar_handles(self) -> None:
        header = _read_source("src/code/game/g_local.h")
        expected_symbols = [
            "extern\tvmCvar_t\tg_damage_g;",
            "extern\tvmCvar_t\tg_damage_mg;",
            "extern\tvmCvar_t\tg_damage_mg_team;",
            "extern\tvmCvar_t\tg_damage_sg;",
            "extern\tvmCvar_t\tg_damage_gl;",
            "extern\tvmCvar_t\tg_splashDamage_gl;",
            "extern\tvmCvar_t\tg_splashRadius_gl;",
            "extern\tvmCvar_t\tg_damage_rl;",
            "extern\tvmCvar_t\tg_splashDamage_rl;",
            "extern\tvmCvar_t\tg_splashRadius_rl;",
            "extern\tvmCvar_t\tg_damage_pg;",
            "extern\tvmCvar_t\tg_splashDamage_pg;",
            "extern\tvmCvar_t\tg_splashRadius_pg;",
            "extern\tvmCvar_t\tg_damage_lg;",
            "extern\tvmCvar_t\tg_damage_rg;",
            "extern\tvmCvar_t\tg_damage_bfg;",
            "extern\tvmCvar_t\tg_splashDamage_bfg;",
            "extern\tvmCvar_t\tg_splashRadius_bfg;",
        ]

        for symbol in expected_symbols:
            with self.subTest(symbol=symbol):
                self.assertIn(symbol, header)

    def test_register_cvars_initialises_configs(self) -> None:
        source = _read_source("src/code/game/g_main.c")
        body = _extract_function_body(source, "void G_RegisterCvars( void )")
        weapon_call = body.index("G_InitWeaponConfig();")
        reload_call = body.index("G_InitWeaponReloadConfig();")
        knockback_call = body.index("G_InitKnockbackConfig();")
        ammo_call = body.index("G_InitStartingAmmoConfig();")
        self.assertLess(weapon_call, reload_call, "weapon config must initialise before reload config")
        self.assertLess(reload_call, knockback_call, "reload config must initialise before knockback config")
        self.assertLess(knockback_call, ammo_call, "knockback config must initialise before starting ammo")

    def test_weapon_reload_config_populates_pmove_cache(self) -> None:
        source = _read_source("src/game/g_config.c")
        body = _extract_function_body(source, "void G_InitWeaponReloadConfig( void )")
        self.assertIn("G_PmoveStoreWeaponReloads( &g_weaponReloadConfig );", body)

    def test_update_cvars_refreshes_configs(self) -> None:
        source = _read_source("src/code/game/g_main.c")
        body = _extract_function_body(source, "void G_UpdateCvars( void )")
        weapon_call = body.index("G_UpdateWeaponConfig();")
        reload_call = body.index("G_UpdateWeaponReloadConfig();")
        knockback_call = body.index("G_UpdateKnockbackConfig();")
        ammo_call = body.index("G_UpdateStartingAmmoConfig();")
        self.assertLess(weapon_call, reload_call, "weapon config refresh must precede reload refresh")
        self.assertLess(reload_call, knockback_call, "reload refresh must precede knockback refresh")
        self.assertLess(knockback_call, ammo_call, "knockback refresh must precede starting ammo refresh")

    def test_clientspawn_uses_starting_ammo_config(self) -> None:
        source = _read_source("src/code/game/g_client.c")
        body = _extract_function_body(source, "void ClientSpawn(gentity_t *ent)")
        self.assertIn("g_startingAmmoConfig.machinegun", body)
        self.assertIn("g_startingAmmoConfig.gauntlet", body)
        self.assertIn("g_startingAmmoConfig.grapplingHook", body)

    def test_cvar_bootstrap_invokes_startup_variable(self) -> None:
        source = _read_source("src/code/qcommon/cvar.c")
        body = _extract_function_body(source, "void Cvar_BootstrapExpandedDefaults( void )")
        self.assertIn("Com_StartupVariable", body)

    def test_com_init_bootstraps_expanded_defaults_before_startup_variables(self) -> None:
        source = _read_source("src/code/qcommon/common.c")
        body = _extract_function_body(source, "void Com_Init( char *commandLine )")
        parse_call = body.index("Com_ParseCommandLine( commandLine );")
        cmd_init_call = body.index("Cmd_Init ();")
        bootstrap_call = body.index("Cvar_BootstrapExpandedDefaults();")
        first_startup = body.index("Com_StartupVariable( NULL );")

        self.assertLess(parse_call, bootstrap_call, "command line must be parsed before bootstrapping expanded CVars")
        self.assertLess(cmd_init_call, bootstrap_call, "command system must be initialised before bootstrapping expanded CVars")
        self.assertLess(bootstrap_call, first_startup, "expanded CVars must bootstrap before general startup variable processing")


if __name__ == "__main__":
    unittest.main()
