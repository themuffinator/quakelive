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
    def test_serialization_lists_all_pmove_fields(self) -> None:
        source = _read_source("src/code/game/g_pmove.c")
        body = _extract_function_body(
            source,
            "static qboolean G_PmoveSerializeSettings( const pmove_settings_t *settings, char *buffer, size_t bufferSize )",
        )
        expected_fields = {
            "airAccel": "PMOVE_FLOAT_FIELD",
            "airControl": "PMOVE_FLOAT_FIELD",
            "airStepFriction": "PMOVE_FLOAT_FIELD",
            "airSteps": "PMOVE_INT_FIELD",
            "airStopAccel": "PMOVE_FLOAT_FIELD",
            "autoHop": "PMOVE_BOOL_FIELD",
            "bunnyHop": "PMOVE_BOOL_FIELD",
            "chainJump": "PMOVE_BOOL_FIELD",
            "chainJumpVelocity": "PMOVE_FLOAT_FIELD",
            "circleStrafeFriction": "PMOVE_FLOAT_FIELD",
            "crouchSlide": "PMOVE_BOOL_FIELD",
            "crouchSlideFriction": "PMOVE_FLOAT_FIELD",
            "crouchSlideTime": "PMOVE_INT_FIELD",
            "crouchStepJump": "PMOVE_BOOL_FIELD",
            "doubleJump": "PMOVE_BOOL_FIELD",
            "jumpTimeDeltaMin": "PMOVE_FLOAT_FIELD",
            "jumpVelocity": "PMOVE_FLOAT_FIELD",
            "jumpVelocityMax": "PMOVE_FLOAT_FIELD",
            "jumpVelocityScaleAdd": "PMOVE_FLOAT_FIELD",
            "jumpVelocityTimeThreshold": "PMOVE_FLOAT_FIELD",
            "jumpVelocityTimeThresholdOffset": "PMOVE_FLOAT_FIELD",
            "noPlayerClip": "PMOVE_BOOL_FIELD",
            "rampJump": "PMOVE_BOOL_FIELD",
            "rampJumpScale": "PMOVE_FLOAT_FIELD",
            "stepHeight": "PMOVE_FLOAT_FIELD",
            "stepJump": "PMOVE_BOOL_FIELD",
            "stepJumpVelocity": "PMOVE_FLOAT_FIELD",
            "strafeAccel": "PMOVE_FLOAT_FIELD",
            "velocityGh": "PMOVE_FLOAT_FIELD",
            "walkAccel": "PMOVE_FLOAT_FIELD",
            "walkFriction": "PMOVE_FLOAT_FIELD",
            "waterSwimScale": "PMOVE_FLOAT_FIELD",
            "waterWadeScale": "PMOVE_FLOAT_FIELD",
            "weaponDropTime": "PMOVE_INT_FIELD",
            "weaponRaiseTime": "PMOVE_INT_FIELD",
            "wishSpeed": "PMOVE_FLOAT_FIELD",
        }

        for field, macro in expected_fields.items():
            with self.subTest(field=field):
                token = f"{macro}( {field} );"
                self.assertIn(token, body)

    def test_serialization_includes_weapon_reload_array(self) -> None:
        source = _read_source("src/code/game/g_pmove.c")
        body = _extract_function_body(
            source,
            "static qboolean G_PmoveSerializeSettings( const pmove_settings_t *settings, char *buffer, size_t bufferSize )",
        )
        self.assertIn("\\\"weaponReloadTimes\\\"", body)


if __name__ == "__main__":
    unittest.main()
