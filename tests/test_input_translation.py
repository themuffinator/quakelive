from __future__ import annotations

import ctypes
from pathlib import Path

import pytest

from tests.compiler_support import compile_c_binary, find_c_compiler, shared_library_name


REPO_ROOT = Path(__file__).resolve().parent.parent


class TranslatedKey(ctypes.Structure):
    _fields_ = [
        ("key", ctypes.c_int),
        ("dispatchKey", ctypes.c_int),
        ("charCode", ctypes.c_int),
        ("hasChar", ctypes.c_int),
    ]


@pytest.fixture(scope="session")
def input_translation_lib(tmp_path_factory: pytest.TempPathFactory) -> ctypes.CDLL:
    build_dir = tmp_path_factory.mktemp("input_translation_build")
    lib_path = build_dir / shared_library_name("input_translation")
    compiler = find_c_compiler()

    if compiler is None:
        pytest.skip("no supported C compiler is available for the input translation harness")

    compile_c_binary(
        compiler,
        [
            REPO_ROOT / "tests" / "input_translation_harness.c",
            REPO_ROOT / "src" / "code" / "client" / "cl_input_translation.c",
        ],
        lib_path,
        include_dirs=[
            REPO_ROOT / "src" / "code",
            REPO_ROOT / "src" / "code" / "client",
            REPO_ROOT / "src" / "code" / "qcommon",
            REPO_ROOT / "src" / "code" / "game",
        ],
        shared=True,
        workdir=REPO_ROOT,
    )

    lib = ctypes.CDLL(str(lib_path))
    lib.QLR_TranslateKey.restype = TranslatedKey
    lib.QLR_TranslateKey.argtypes = [ctypes.c_int]
    lib.QLR_TranslateMouse.restype = ctypes.c_int
    lib.QLR_TranslateMouse.argtypes = [ctypes.c_int, ctypes.c_float]
    return lib


def test_uppercase_key_translates_to_lowercase_dispatch(input_translation_lib: ctypes.CDLL) -> None:
    translated = input_translation_lib.QLR_TranslateKey(ord("A"))

    assert translated.dispatchKey == ord("a")
    assert translated.charCode == ord("A")
    assert translated.hasChar == 1


def test_unicode_key_preserves_codepoint_for_char_payload(input_translation_lib: ctypes.CDLL) -> None:
    euro_sign = 0x20AC
    translated = input_translation_lib.QLR_TranslateKey(euro_sign)

    assert translated.dispatchKey == euro_sign
    assert translated.charCode == euro_sign
    assert translated.hasChar == 1


def test_control_character_key_preserves_backspace_payload(input_translation_lib: ctypes.CDLL) -> None:
    translated = input_translation_lib.QLR_TranslateKey(8)

    assert translated.dispatchKey == 8
    assert translated.charCode == 8
    assert translated.hasChar == 1


def test_negative_key_drops_character_payload(input_translation_lib: ctypes.CDLL) -> None:
    translated = input_translation_lib.QLR_TranslateKey(-5)

    assert translated.dispatchKey == 0
    assert translated.charCode == 0
    assert translated.hasChar == 0


def test_mouse_delta_scales_with_cpi(input_translation_lib: ctypes.CDLL) -> None:
    scaled = input_translation_lib.QLR_TranslateMouse(1, ctypes.c_float(500.0))
    unchanged = input_translation_lib.QLR_TranslateMouse(4, ctypes.c_float(0.0))

    assert scaled == 2
    assert unchanged == 4
