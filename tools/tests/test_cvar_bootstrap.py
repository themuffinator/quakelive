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
    def test_register_cvars_initialises_configs(self) -> None:
        source = _read_source("src/code/game/g_main.c")
        body = _extract_function_body(source, "void G_RegisterCvars( void )")
        weapon_call = body.index("G_InitWeaponConfig();")
        ammo_call = body.index("G_InitStartingAmmoConfig();")
        self.assertLess(weapon_call, ammo_call, "weapon config must initialise before starting ammo")

    def test_update_cvars_refreshes_configs(self) -> None:
        source = _read_source("src/code/game/g_main.c")
        body = _extract_function_body(source, "void G_UpdateCvars( void )")
        weapon_call = body.index("G_UpdateWeaponConfig();")
        ammo_call = body.index("G_UpdateStartingAmmoConfig();")
        self.assertLess(weapon_call, ammo_call, "weapon config refresh must precede starting ammo refresh")

    def test_clientspawn_uses_starting_ammo_config(self) -> None:
        source = _read_source("src/code/game/g_client.c")
        body = _extract_function_body(source, "void ClientSpawn(gentity_t *ent)")
        self.assertIn("g_startingAmmoConfig.machinegun", body)
        self.assertIn("g_startingAmmoConfig.gauntlet", body)
        self.assertIn("g_startingAmmoConfig.grapplingHook", body)


if __name__ == "__main__":
    unittest.main()
