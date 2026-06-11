from __future__ import annotations

import ctypes
from pathlib import Path

import pytest

from tests.compiler_support import compile_c_binary, find_c_compiler, shared_library_name


REPO_ROOT = Path(__file__).resolve().parent.parent
CL_INPUT = REPO_ROOT / "src" / "code" / "client" / "cl_input.c"
CLIENT_H = REPO_ROOT / "src" / "code" / "client" / "client.h"
CL_KEYS = REPO_ROOT / "src" / "code" / "client" / "cl_keys.c"


class TranslatedKey(ctypes.Structure):
    _fields_ = [
        ("key", ctypes.c_int),
        ("dispatchKey", ctypes.c_int),
        ("charCode", ctypes.c_int),
        ("hasChar", ctypes.c_int),
    ]


def _block_from_marker(source: str, marker: str) -> str:
    start = source.rindex(marker)
    brace_start = source.index("{", start)
    depth = 0

    for index in range(brace_start, len(source)):
        char = source[index]
        if char == "{":
            depth += 1
        elif char == "}":
            depth -= 1
            if depth == 0:
                return source[start:index + 1]

    raise AssertionError(f"Unbalanced block for marker: {marker}")


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
    lib.QLR_EncodeUtf8Codepoint.restype = ctypes.c_int
    lib.QLR_EncodeUtf8Codepoint.argtypes = [ctypes.c_int, ctypes.POINTER(ctypes.c_char), ctypes.c_int]
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


def test_codepoint_encoder_matches_retail_utf8_bytes(input_translation_lib: ctypes.CDLL) -> None:
    buffer = ctypes.create_string_buffer(4)
    written = input_translation_lib.QLR_EncodeUtf8Codepoint(0x20AC, buffer, len(buffer))

    assert written == 3
    assert buffer.raw[:written] == b"\xe2\x82\xac"


def test_codepoint_encoder_rejects_utf16_surrogates(input_translation_lib: ctypes.CDLL) -> None:
    buffer = ctypes.create_string_buffer(4)
    written = input_translation_lib.QLR_EncodeUtf8Codepoint(0xD800, buffer, len(buffer))

    assert written == 0


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


def test_char_event_dispatch_encodes_utf8_before_routing() -> None:
    source = CL_KEYS.read_text(encoding="utf-8")
    block = _block_from_marker(source, "void CL_CharEvent( int key )")

    for expected in (
        "byteCount = CL_EncodeUtf8Codepoint( translated.charCode, utf8, sizeof( utf8 ) );",
        "for ( i = 0 ; i < byteCount ; i++ ) {",
        "utf8Byte = (unsigned char)utf8[i];",
        "Field_CharEvent( &g_consoleField, utf8Byte );",
        "CL_WebView_OnKeyEvent( utf8Byte | K_CHAR_FLAG, qtrue );",
        "VM_Call( uivm, UI_KEY_EVENT, utf8Byte | K_CHAR_FLAG, qtrue, cls.realtime );",
        "Field_CharEvent( &chatField, utf8Byte );",
    ):
        assert expected in block

    assert "key = translated.charCode;" not in block


def test_key_string_to_keynum_lowercases_single_character_tokens() -> None:
    source = CL_KEYS.read_text(encoding="utf-8")
    block = _block_from_marker(source, "int Key_StringToKeynum( char *str )")

    assert "return tolower( str[0] );" in block
    assert "return str[0];" not in block


def test_key_command_init_resets_retail_field_and_binding_state() -> None:
    source = CL_KEYS.read_text(encoding="utf-8")
    block = _block_from_marker(source, "void CL_InitKeyCommands( void )")

    for expected in (
        "Com_Memset( historyEditLines, 0, sizeof( historyEditLines ) );",
        "nextHistoryLine = 0;",
        "historyLine = 0;",
        "Com_Memset( &g_consoleField, 0, sizeof( g_consoleField ) );",
        "Com_Memset( &chatField, 0, sizeof( chatField ) );",
        "chat_reply = qfalse;",
        "chat_team = qfalse;",
        "chat_playerNum = 0;",
        "key_overstrikeMode = qfalse;",
        "anykeydown = qfalse;",
        "Com_Memset( keys, 0, sizeof( keys ) );",
    ):
        assert expected in block


def test_mouse_delta_scales_with_cpi(input_translation_lib: ctypes.CDLL) -> None:
    scaled = input_translation_lib.QLR_TranslateMouse(1, ctypes.c_float(500.0))
    unchanged = input_translation_lib.QLR_TranslateMouse(4, ctypes.c_float(0.0))

    assert scaled == 2
    assert unchanged == 4


def test_mouse_event_dispatch_matches_retail_keycatcher_order() -> None:
    source = CL_INPUT.read_text(encoding="utf-8")
    client_h = CLIENT_H.read_text(encoding="utf-8")

    for expected in (
        "#define KEYCATCH_RETAIL_MOUSEPASS\t0x0010",
        "#define KEYCATCH_BROWSER\t\t\t0x0020",
    ):
        assert expected in client_h

    for expected in (
        "(void)time;",
        'if ( Cvar_VariableIntegerValue( "cg_ignoreMouseInput" ) ) {',
        "if ( cls.keyCatchers & KEYCATCH_BROWSER ) {",
        "CL_WebView_OnMouseMove( dx, dy );",
        "VM_Call( uivm, UI_MOUSE_EVENT, dx, dy );",
        "VM_Call( cgvm, CG_MOUSE_EVENT, dx, dy );",
        "if ( ( cls.keyCatchers & ~KEYCATCH_RETAIL_MOUSEPASS ) == 0 ) {",
        "cl.mouseDx[0] += dx;",
        "cl.mouseDy[0] += dy;",
    ):
        assert expected in source

    for unexpected in (
        "static int\t\tcl_mouseCursorX;",
        "static int\t\tcl_mouseCursorY;",
        "CL_UpdateMouseCursorPosition(",
        "translatedDx = CL_TranslateRetailMouseDelta",
        "VM_Call( uivm, UI_MOUSE_EVENT, translatedDx, translatedDy );",
        "VM_Call (cgvm, CG_MOUSE_EVENT, translatedDx, translatedDy);",
        "CL_WebView_OnMouseMove( cursorX, cursorY );",
    ):
        assert unexpected not in source
