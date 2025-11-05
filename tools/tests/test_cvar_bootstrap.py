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

    def test_register_cvars_initialises_configs(self) -> None:
        source = _read_source("src/code/game/g_main.c")
        body = _extract_function_body(source, "void G_RegisterCvars( void )")
        weapon_call = body.index("G_InitWeaponConfig();")
        reload_call = body.index("G_InitWeaponReloadConfig();")
        ammo_call = body.index("G_InitStartingAmmoConfig();")
        self.assertLess(weapon_call, reload_call, "weapon config must initialise before reload config")
        self.assertLess(reload_call, ammo_call, "reload config must initialise before starting ammo")

    def test_update_cvars_refreshes_configs(self) -> None:
        source = _read_source("src/code/game/g_main.c")
        body = _extract_function_body(source, "void G_UpdateCvars( void )")
        weapon_call = body.index("G_UpdateWeaponConfig();")
        reload_call = body.index("G_UpdateWeaponReloadConfig();")
        ammo_call = body.index("G_UpdateStartingAmmoConfig();")
        self.assertLess(weapon_call, reload_call, "weapon config refresh must precede reload refresh")
        self.assertLess(reload_call, ammo_call, "reload refresh must precede starting ammo refresh")

    def test_clientspawn_uses_starting_ammo_config(self) -> None:
        source = _read_source("src/code/game/g_client.c")
        body = _extract_function_body(source, "void ClientSpawn(gentity_t *ent)")
        self.assertIn("g_startingAmmoConfig.machinegun", body)
        self.assertIn("g_startingAmmoConfig.gauntlet", body)
        self.assertIn("g_startingAmmoConfig.grapplingHook", body)

    def test_cvar_init_bootstraps_expanded_defaults(self) -> None:
        source = _read_source("src/code/qcommon/cvar.c")
        body = _extract_function_body(source, "void Cvar_Init (void)")
        bootstrap_call = body.index("Cvar_InitExpandedDefaults();")
        toggle_call = body.index("Cmd_AddCommand (\"toggle\", Cvar_Toggle_f);")
        self.assertLess(
            bootstrap_call,
            toggle_call,
            "expanded CVar defaults must be bootstrapped before binding commands",
        )


if __name__ == "__main__":
    unittest.main()
