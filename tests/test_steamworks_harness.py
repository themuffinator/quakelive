"""Steamworks harness coverage for auth ticket flows."""
from __future__ import annotations

import ctypes
import subprocess
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent

QL_AUTH_RESULT_PENDING = 0
QL_AUTH_RESULT_ACCEPTED = 1
QL_AUTH_RESULT_DENIED = 2
QL_AUTH_RESULT_ERROR = 3

QL_AUTH_OUTCOME_SUCCESS = 0
QL_AUTH_OUTCOME_RETRY = 1
QL_AUTH_OUTCOME_FAILURE = 2

BEGIN_AUTH_OK = 0
BEGIN_AUTH_INVALID_TICKET = 1

TICKET_BUFFER = 256


class AuthResponse(ctypes.Structure):
    _fields_ = [
        ("result", ctypes.c_int),
        ("outcome", ctypes.c_int),
        ("message", ctypes.c_char * 128),
    ]


@pytest.fixture(scope="session", params=[False, True], ids=["steamworks_disabled", "steamworks_enabled"])
def steamworks_harness(request: pytest.FixtureRequest, tmp_path_factory: pytest.TempPathFactory) -> tuple[ctypes.CDLL, bool]:
    enabled = bool(request.param)
    build_dir = tmp_path_factory.mktemp(f"steamworks_harness_{'on' if enabled else 'off'}")
    lib_path = build_dir / "libsteamworks_harness.so"

    compile_cmd = [
        "gcc",
        "-shared",
        "-fPIC",
        "-Isrc/common",
        "-Isrc/code",
        "-Isrc/code/game",
        "-Isrc/code/qcommon",
        "-DQL_BUILD_STEAMWORKS=%d" % (1 if enabled else 0),
        str(REPO_ROOT / "tests" / "steamworks_harness.c"),
        "-o",
        str(lib_path),
    ]
    subprocess.check_call(compile_cmd, cwd=REPO_ROOT)

    lib = ctypes.CDLL(str(lib_path))

    lib.QLR_Steamworks_Request.argtypes = [
        ctypes.c_char_p,
        ctypes.c_size_t,
        ctypes.POINTER(ctypes.c_int),
        ctypes.POINTER(ctypes.c_uint32),
    ]
    lib.QLR_Steamworks_Request.restype = ctypes.c_int

    lib.QLR_Steamworks_Validate.argtypes = [ctypes.c_char_p, ctypes.POINTER(AuthResponse)]
    lib.QLR_Steamworks_Validate.restype = ctypes.c_int

    lib.QLR_Steamworks_Shutdown.argtypes = []
    lib.QLR_Steamworks_Shutdown.restype = None

    if enabled:
        lib.QLR_SteamworksMock_Reset.argtypes = []
        lib.QLR_SteamworksMock_Reset.restype = None

        lib.QLR_SteamworksMock_PrimeState.argtypes = []
        lib.QLR_SteamworksMock_PrimeState.restype = None

        lib.QLR_SteamworksMock_SetLibraryAvailable.argtypes = [ctypes.c_int]
        lib.QLR_SteamworksMock_SetLibraryAvailable.restype = None

        lib.QLR_SteamworksMock_SetInitResult.argtypes = [ctypes.c_int]
        lib.QLR_SteamworksMock_SetInitResult.restype = None

        lib.QLR_SteamworksMock_SetUserAvailable.argtypes = [ctypes.c_int]
        lib.QLR_SteamworksMock_SetUserAvailable.restype = None

        lib.QLR_SteamworksMock_SetTicket.argtypes = [ctypes.c_char_p, ctypes.c_uint32, ctypes.c_uint32]
        lib.QLR_SteamworksMock_SetTicket.restype = None

        lib.QLR_SteamworksMock_SetAuthResult.argtypes = [ctypes.c_int]
        lib.QLR_SteamworksMock_SetAuthResult.restype = None

        lib.QLR_SteamworksMock_SetSteamId.argtypes = [ctypes.c_uint64]
        lib.QLR_SteamworksMock_SetSteamId.restype = None

    return lib, enabled


def test_request_produces_expected_ticket(steamworks_harness: tuple[ctypes.CDLL, bool]) -> None:
    lib, enabled = steamworks_harness

    ticket_buffer = ctypes.create_string_buffer(TICKET_BUFFER)
    ticket_length = ctypes.c_int()
    ticket_handle = ctypes.c_uint32()

    if enabled:
        lib.QLR_SteamworksMock_Reset()
        lib.QLR_SteamworksMock_PrimeState()

    result = lib.QLR_Steamworks_Request(
        ticket_buffer,
        ctypes.sizeof(ticket_buffer),
        ctypes.byref(ticket_length),
        ctypes.byref(ticket_handle),
    )

    if not enabled:
        assert result == 0
        return

    assert result != 0
    assert ticket_buffer.value.decode() == "12345678"
    assert ticket_length.value == 8
    assert ticket_handle.value == 1


def test_validate_maps_auth_results(steamworks_harness: tuple[ctypes.CDLL, bool]) -> None:
    lib, enabled = steamworks_harness

    if not enabled:
        response = AuthResponse()
        assert lib.QLR_Steamworks_Validate(b"deadbeef", ctypes.byref(response)) == 0
        return

    lib.QLR_SteamworksMock_Reset()
    lib.QLR_SteamworksMock_PrimeState()

    raw_ticket = ctypes.create_string_buffer(b"\xAA\xBB\xCC")
    lib.QLR_SteamworksMock_SetTicket(raw_ticket, 3, 99)

    ticket_buffer = ctypes.create_string_buffer(TICKET_BUFFER)
    ticket_length = ctypes.c_int()
    ticket_handle = ctypes.c_uint32()

    assert lib.QLR_Steamworks_Request(
        ticket_buffer,
        ctypes.sizeof(ticket_buffer),
        ctypes.byref(ticket_length),
        ctypes.byref(ticket_handle),
    )

    ticket_hex = ticket_buffer.value
    assert ticket_hex == b"aabbcc"
    assert ticket_length.value == 6
    assert ticket_handle.value == 99

    lib.QLR_SteamworksMock_SetAuthResult(BEGIN_AUTH_OK)
    success = AuthResponse()
    assert lib.QLR_Steamworks_Validate(ticket_hex, ctypes.byref(success))
    assert success.result == QL_AUTH_RESULT_ACCEPTED
    assert success.outcome == QL_AUTH_OUTCOME_SUCCESS
    assert success.message.decode() == "Steam ticket accepted"

    lib.QLR_SteamworksMock_Reset()
    lib.QLR_SteamworksMock_PrimeState()
    lib.QLR_SteamworksMock_SetTicket(raw_ticket, 3, 77)
    lib.QLR_SteamworksMock_SetAuthResult(BEGIN_AUTH_INVALID_TICKET)

    denied = AuthResponse()
    assert lib.QLR_Steamworks_Validate(ticket_hex, ctypes.byref(denied))
    assert denied.result == QL_AUTH_RESULT_DENIED
    assert denied.outcome == QL_AUTH_OUTCOME_FAILURE
    assert "invalid" in denied.message.decode().lower()

    lib.QLR_SteamworksMock_SetLibraryAvailable(0)
    lib.QLR_SteamworksMock_SetInitResult(0)
    lib.QLR_SteamworksMock_PrimeState()

    runtime_missing = AuthResponse()
    assert lib.QLR_Steamworks_Validate(ticket_hex, ctypes.byref(runtime_missing))
    assert runtime_missing.result == QL_AUTH_RESULT_ERROR
    assert runtime_missing.outcome == QL_AUTH_OUTCOME_FAILURE
    assert "runtime" in runtime_missing.message.decode().lower()
