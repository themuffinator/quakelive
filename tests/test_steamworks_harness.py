"""Steamworks harness coverage for auth ticket flows."""
from __future__ import annotations

import ctypes
import os
import shutil
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
AVATAR_SIZE_SMALL = 0
AVATAR_SIZE_MEDIUM = 1
AVATAR_SIZE_LARGE = 2

TICKET_BUFFER = 256
AVATAR_BUFFER = 256 * 256 * 4


def _find_c_compiler() -> str:
    compiler = shutil.which("gcc") or shutil.which("clang") or shutil.which("cc")
    if not compiler:
        pytest.skip("No C compiler found for Steamworks harness")

    return compiler


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
    lib_path = build_dir / ("steamworks_harness.dll" if os.name == "nt" else "libsteamworks_harness.so")
    compile_args = [
        _find_c_compiler(),
        "-shared",
    ]

    if os.name != "nt":
        compile_args.append("-fPIC")
    else:
        compile_args.extend(["-DWIN32", "-D_CRT_SECURE_NO_WARNINGS", "-Wno-return-type"])

    compile_cmd = [
        *compile_args,
        "-Isrc/common",
        "-Isrc/code",
        "-Isrc/code/game",
        "-Isrc/code/qcommon",
        "-DQL_BUILD_ONLINE_SERVICES=%d" % (1 if enabled else 0),
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
    lib.QLR_Steamworks_CancelTicket.argtypes = [ctypes.c_uint32]
    lib.QLR_Steamworks_CancelTicket.restype = ctypes.c_int

    lib.QLR_Steamworks_Validate.argtypes = [ctypes.c_char_p, ctypes.POINTER(AuthResponse)]
    lib.QLR_Steamworks_Validate.restype = ctypes.c_int

    lib.QLR_Steamworks_LoadAvatar.argtypes = [
        ctypes.c_uint32,
        ctypes.c_uint32,
        ctypes.c_int,
        ctypes.POINTER(ctypes.c_uint8),
        ctypes.c_uint32,
        ctypes.POINTER(ctypes.c_uint32),
        ctypes.POINTER(ctypes.c_uint32),
        ctypes.POINTER(ctypes.c_uint32),
    ]
    lib.QLR_Steamworks_LoadAvatar.restype = ctypes.c_int

    lib.QLR_Steamworks_ActivateOverlay.argtypes = [
        ctypes.c_char_p,
        ctypes.c_uint32,
        ctypes.c_uint32,
    ]
    lib.QLR_Steamworks_ActivateOverlay.restype = ctypes.c_int

    lib.QLR_Steamworks_SetRichPresence.argtypes = [ctypes.c_char_p, ctypes.c_char_p]
    lib.QLR_Steamworks_SetRichPresence.restype = ctypes.c_int

    lib.QLR_Steamworks_CreateLobby.argtypes = [ctypes.c_int]
    lib.QLR_Steamworks_CreateLobby.restype = ctypes.c_int

    lib.QLR_Steamworks_LeaveLobby.argtypes = [ctypes.c_uint32, ctypes.c_uint32]
    lib.QLR_Steamworks_LeaveLobby.restype = ctypes.c_int

    lib.QLR_Steamworks_JoinLobby.argtypes = [ctypes.c_uint32, ctypes.c_uint32]
    lib.QLR_Steamworks_JoinLobby.restype = ctypes.c_int

    lib.QLR_Steamworks_SetLobbyServer.argtypes = [ctypes.c_uint32, ctypes.c_uint32, ctypes.c_uint32, ctypes.c_uint16]
    lib.QLR_Steamworks_SetLobbyServer.restype = ctypes.c_int

    lib.QLR_Steamworks_ShowInviteOverlay.argtypes = [ctypes.c_uint32, ctypes.c_uint32]
    lib.QLR_Steamworks_ShowInviteOverlay.restype = ctypes.c_int

    lib.QLR_Steamworks_SayLobby.argtypes = [ctypes.c_uint32, ctypes.c_uint32, ctypes.c_char_p]
    lib.QLR_Steamworks_SayLobby.restype = ctypes.c_int

    lib.QLR_Steamworks_RequestUserStats.argtypes = [ctypes.c_uint32, ctypes.c_uint32]
    lib.QLR_Steamworks_RequestUserStats.restype = ctypes.c_int

    lib.QLR_Steamworks_GetNumSubscribedItems.argtypes = []
    lib.QLR_Steamworks_GetNumSubscribedItems.restype = ctypes.c_uint32

    lib.QLR_Steamworks_GetSubscribedItems.argtypes = [ctypes.POINTER(ctypes.c_uint64), ctypes.c_uint32]
    lib.QLR_Steamworks_GetSubscribedItems.restype = ctypes.c_uint32

    lib.QLR_Steamworks_GetItemInstallInfo.argtypes = [
        ctypes.c_uint32,
        ctypes.c_uint32,
        ctypes.POINTER(ctypes.c_uint64),
        ctypes.POINTER(ctypes.c_char),
        ctypes.c_uint32,
        ctypes.POINTER(ctypes.c_uint32),
    ]
    lib.QLR_Steamworks_GetItemInstallInfo.restype = ctypes.c_int

    lib.QLR_Steamworks_SubscribeItem.argtypes = [ctypes.c_uint32, ctypes.c_uint32]
    lib.QLR_Steamworks_SubscribeItem.restype = ctypes.c_int

    lib.QLR_Steamworks_UnsubscribeItem.argtypes = [ctypes.c_uint32, ctypes.c_uint32]
    lib.QLR_Steamworks_UnsubscribeItem.restype = ctypes.c_int

    lib.QLR_Steamworks_DownloadItem.argtypes = [ctypes.c_uint32, ctypes.c_uint32, ctypes.c_int]
    lib.QLR_Steamworks_DownloadItem.restype = ctypes.c_int

    lib.QLR_Steamworks_Init.argtypes = []
    lib.QLR_Steamworks_Init.restype = ctypes.c_int

    lib.QLR_Steamworks_ServerInit.argtypes = [ctypes.c_uint32, ctypes.c_uint16, ctypes.c_int, ctypes.c_int]
    lib.QLR_Steamworks_ServerInit.restype = ctypes.c_int

    lib.QLR_Steamworks_ServerShutdown.argtypes = []
    lib.QLR_Steamworks_ServerShutdown.restype = None

    lib.QLR_Steamworks_ServerIsInitialised.argtypes = []
    lib.QLR_Steamworks_ServerIsInitialised.restype = ctypes.c_int

    lib.QLR_Steamworks_ServerEnableHeartbeats.argtypes = [ctypes.c_int]
    lib.QLR_Steamworks_ServerEnableHeartbeats.restype = ctypes.c_int

    lib.QLR_Steamworks_ServerSetDedicated.argtypes = [ctypes.c_int]
    lib.QLR_Steamworks_ServerSetDedicated.restype = ctypes.c_int

    lib.QLR_Steamworks_ServerLogOn.argtypes = [ctypes.c_char_p]
    lib.QLR_Steamworks_ServerLogOn.restype = ctypes.c_int

    lib.QLR_Steamworks_ServerSetProduct.argtypes = [ctypes.c_char_p]
    lib.QLR_Steamworks_ServerSetProduct.restype = ctypes.c_int

    lib.QLR_Steamworks_ServerSetGameDir.argtypes = [ctypes.c_char_p]
    lib.QLR_Steamworks_ServerSetGameDir.restype = ctypes.c_int

    lib.QLR_Steamworks_ServerSetGameDescription.argtypes = [ctypes.c_char_p]
    lib.QLR_Steamworks_ServerSetGameDescription.restype = ctypes.c_int

    lib.QLR_Steamworks_ServerSetMaxPlayerCount.argtypes = [ctypes.c_int]
    lib.QLR_Steamworks_ServerSetMaxPlayerCount.restype = ctypes.c_int

    lib.QLR_Steamworks_ServerSetBotPlayerCount.argtypes = [ctypes.c_int]
    lib.QLR_Steamworks_ServerSetBotPlayerCount.restype = ctypes.c_int

    lib.QLR_Steamworks_ServerSetServerName.argtypes = [ctypes.c_char_p]
    lib.QLR_Steamworks_ServerSetServerName.restype = ctypes.c_int

    lib.QLR_Steamworks_ServerSetMapName.argtypes = [ctypes.c_char_p]
    lib.QLR_Steamworks_ServerSetMapName.restype = ctypes.c_int

    lib.QLR_Steamworks_ServerSetPasswordProtected.argtypes = [ctypes.c_int]
    lib.QLR_Steamworks_ServerSetPasswordProtected.restype = ctypes.c_int

    lib.QLR_Steamworks_ServerGetSteamID.argtypes = [ctypes.POINTER(ctypes.c_uint32), ctypes.POINTER(ctypes.c_uint32)]
    lib.QLR_Steamworks_ServerGetSteamID.restype = ctypes.c_int

    lib.QLR_Steamworks_ServerSetGameTags.argtypes = [ctypes.c_char_p]
    lib.QLR_Steamworks_ServerSetGameTags.restype = ctypes.c_int

    lib.QLR_Steamworks_ServerSetKeyValue.argtypes = [ctypes.c_char_p, ctypes.c_char_p]
    lib.QLR_Steamworks_ServerSetKeyValue.restype = ctypes.c_int

    lib.QLR_Steamworks_ServerSetKeyValuesFromInfoString.argtypes = [ctypes.c_char_p]
    lib.QLR_Steamworks_ServerSetKeyValuesFromInfoString.restype = ctypes.c_int

    lib.QLR_Steamworks_ServerUpdateUserData.argtypes = [
        ctypes.c_uint32,
        ctypes.c_uint32,
        ctypes.c_char_p,
        ctypes.c_uint32,
    ]
    lib.QLR_Steamworks_ServerUpdateUserData.restype = ctypes.c_int

    lib.QLR_Steamworks_ServerGetPublicIP.argtypes = []
    lib.QLR_Steamworks_ServerGetPublicIP.restype = ctypes.c_uint32

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

        lib.QLR_SteamworksMock_SetSteamGameServerInitResult.argtypes = [ctypes.c_int]
        lib.QLR_SteamworksMock_SetSteamGameServerInitResult.restype = None

        lib.QLR_SteamworksMock_SetUserAvailable.argtypes = [ctypes.c_int]
        lib.QLR_SteamworksMock_SetUserAvailable.restype = None

        lib.QLR_SteamworksMock_SetTicket.argtypes = [ctypes.c_char_p, ctypes.c_uint32, ctypes.c_uint32]
        lib.QLR_SteamworksMock_SetTicket.restype = None
        lib.QLR_SteamworksMock_GetCancelledTicketHandle.argtypes = []
        lib.QLR_SteamworksMock_GetCancelledTicketHandle.restype = ctypes.c_uint32
        lib.QLR_SteamworksMock_GetCancelAuthTicketCalls.argtypes = []
        lib.QLR_SteamworksMock_GetCancelAuthTicketCalls.restype = ctypes.c_int

        lib.QLR_SteamworksMock_SetAuthResult.argtypes = [ctypes.c_int]
        lib.QLR_SteamworksMock_SetAuthResult.restype = None

        lib.QLR_SteamworksMock_SetSteamId.argtypes = [ctypes.c_uint64]
        lib.QLR_SteamworksMock_SetSteamId.restype = None

        lib.QLR_SteamworksMock_SetLobbyOwnerId.argtypes = [ctypes.c_uint64]
        lib.QLR_SteamworksMock_SetLobbyOwnerId.restype = None

        lib.QLR_SteamworksMock_SetSteamGameServerPublicIP.argtypes = [ctypes.c_uint32]
        lib.QLR_SteamworksMock_SetSteamGameServerPublicIP.restype = None

        lib.QLR_SteamworksMock_SetSteamGameServerId.argtypes = [ctypes.c_uint64]
        lib.QLR_SteamworksMock_SetSteamGameServerId.restype = None

        lib.QLR_SteamworksMock_SetAvatarHandles.argtypes = [ctypes.c_int, ctypes.c_int, ctypes.c_int]
        lib.QLR_SteamworksMock_SetAvatarHandles.restype = None

        lib.QLR_SteamworksMock_SetAvatarPixels.argtypes = [
            ctypes.c_uint32,
            ctypes.c_uint32,
            ctypes.POINTER(ctypes.c_uint8),
            ctypes.c_uint32,
        ]
        lib.QLR_SteamworksMock_SetAvatarPixels.restype = None

        lib.QLR_SteamworksMock_SetUGCItemState.argtypes = [ctypes.c_uint32]
        lib.QLR_SteamworksMock_SetUGCItemState.restype = None

        lib.QLR_SteamworksMock_SetUGCDownloadInfo.argtypes = [ctypes.c_uint64, ctypes.c_uint64]
        lib.QLR_SteamworksMock_SetUGCDownloadInfo.restype = None

        lib.QLR_SteamworksMock_SetSubscribedItems.argtypes = [ctypes.POINTER(ctypes.c_uint64), ctypes.c_uint32]
        lib.QLR_SteamworksMock_SetSubscribedItems.restype = None

        lib.QLR_SteamworksMock_SetUGCInstallInfo.argtypes = [ctypes.c_uint64, ctypes.c_uint64, ctypes.c_char_p, ctypes.c_uint32]
        lib.QLR_SteamworksMock_SetUGCInstallInfo.restype = None

        lib.QLR_SteamworksMock_GetOverlayCallCount.argtypes = []
        lib.QLR_SteamworksMock_GetOverlayCallCount.restype = ctypes.c_int

        lib.QLR_SteamworksMock_GetOverlayDialog.argtypes = []
        lib.QLR_SteamworksMock_GetOverlayDialog.restype = ctypes.c_char_p

        lib.QLR_SteamworksMock_GetOverlaySteamId.argtypes = []
        lib.QLR_SteamworksMock_GetOverlaySteamId.restype = ctypes.c_uint64

        lib.QLR_SteamworksMock_GetRichPresenceCallCount.argtypes = []
        lib.QLR_SteamworksMock_GetRichPresenceCallCount.restype = ctypes.c_int

        lib.QLR_SteamworksMock_GetRichPresenceKey.argtypes = []
        lib.QLR_SteamworksMock_GetRichPresenceKey.restype = ctypes.c_char_p

        lib.QLR_SteamworksMock_GetRichPresenceValue.argtypes = []
        lib.QLR_SteamworksMock_GetRichPresenceValue.restype = ctypes.c_char_p

        lib.QLR_SteamworksMock_GetSteamGameServerInitCalls.argtypes = []
        lib.QLR_SteamworksMock_GetSteamGameServerInitCalls.restype = ctypes.c_int

        lib.QLR_SteamworksMock_GetSteamGameServerShutdownCalls.argtypes = []
        lib.QLR_SteamworksMock_GetSteamGameServerShutdownCalls.restype = ctypes.c_int

        lib.QLR_SteamworksMock_GetSteamGameServerLastInitIP.argtypes = []
        lib.QLR_SteamworksMock_GetSteamGameServerLastInitIP.restype = ctypes.c_uint32

        lib.QLR_SteamworksMock_GetSteamGameServerLastInitGamePort.argtypes = []
        lib.QLR_SteamworksMock_GetSteamGameServerLastInitGamePort.restype = ctypes.c_uint16

        lib.QLR_SteamworksMock_GetSteamGameServerLastInitServerMode.argtypes = []
        lib.QLR_SteamworksMock_GetSteamGameServerLastInitServerMode.restype = ctypes.c_int

        lib.QLR_SteamworksMock_GetSteamGameServerLastInitVersion.argtypes = []
        lib.QLR_SteamworksMock_GetSteamGameServerLastInitVersion.restype = ctypes.c_char_p

        lib.QLR_SteamworksMock_GetSteamGameServerCallbackCalls.argtypes = []
        lib.QLR_SteamworksMock_GetSteamGameServerCallbackCalls.restype = ctypes.c_int

        lib.QLR_SteamworksMock_GetSteamGameServerHeartbeatCalls.argtypes = []
        lib.QLR_SteamworksMock_GetSteamGameServerHeartbeatCalls.restype = ctypes.c_int

        lib.QLR_SteamworksMock_GetSteamGameServerLastHeartbeatEnabled.argtypes = []
        lib.QLR_SteamworksMock_GetSteamGameServerLastHeartbeatEnabled.restype = ctypes.c_int

        lib.QLR_SteamworksMock_GetSteamGameServerDedicatedCalls.argtypes = []
        lib.QLR_SteamworksMock_GetSteamGameServerDedicatedCalls.restype = ctypes.c_int

        lib.QLR_SteamworksMock_GetSteamGameServerLastDedicated.argtypes = []
        lib.QLR_SteamworksMock_GetSteamGameServerLastDedicated.restype = ctypes.c_int

        lib.QLR_SteamworksMock_GetSteamGameServerLogOnCalls.argtypes = []
        lib.QLR_SteamworksMock_GetSteamGameServerLogOnCalls.restype = ctypes.c_int

        lib.QLR_SteamworksMock_GetSteamGameServerLogOnAnonymousCalls.argtypes = []
        lib.QLR_SteamworksMock_GetSteamGameServerLogOnAnonymousCalls.restype = ctypes.c_int

        lib.QLR_SteamworksMock_GetSteamGameServerProductCalls.argtypes = []
        lib.QLR_SteamworksMock_GetSteamGameServerProductCalls.restype = ctypes.c_int

        lib.QLR_SteamworksMock_GetSteamGameServerGameDirCalls.argtypes = []
        lib.QLR_SteamworksMock_GetSteamGameServerGameDirCalls.restype = ctypes.c_int

        lib.QLR_SteamworksMock_GetSteamGameServerGameDescriptionCalls.argtypes = []
        lib.QLR_SteamworksMock_GetSteamGameServerGameDescriptionCalls.restype = ctypes.c_int

        lib.QLR_SteamworksMock_GetSteamGameServerMaxPlayerCountCalls.argtypes = []
        lib.QLR_SteamworksMock_GetSteamGameServerMaxPlayerCountCalls.restype = ctypes.c_int

        lib.QLR_SteamworksMock_GetSteamGameServerBotPlayerCountCalls.argtypes = []
        lib.QLR_SteamworksMock_GetSteamGameServerBotPlayerCountCalls.restype = ctypes.c_int

        lib.QLR_SteamworksMock_GetSteamGameServerServerNameCalls.argtypes = []
        lib.QLR_SteamworksMock_GetSteamGameServerServerNameCalls.restype = ctypes.c_int

        lib.QLR_SteamworksMock_GetSteamGameServerMapNameCalls.argtypes = []
        lib.QLR_SteamworksMock_GetSteamGameServerMapNameCalls.restype = ctypes.c_int

        lib.QLR_SteamworksMock_GetSteamGameServerPasswordCalls.argtypes = []
        lib.QLR_SteamworksMock_GetSteamGameServerPasswordCalls.restype = ctypes.c_int

        lib.QLR_SteamworksMock_GetSteamGameServerGameTagsCalls.argtypes = []
        lib.QLR_SteamworksMock_GetSteamGameServerGameTagsCalls.restype = ctypes.c_int

        lib.QLR_SteamworksMock_GetSteamGameServerUserDataCalls.argtypes = []
        lib.QLR_SteamworksMock_GetSteamGameServerUserDataCalls.restype = ctypes.c_int

        lib.QLR_SteamworksMock_GetSteamGameServerKeyValueCalls.argtypes = []
        lib.QLR_SteamworksMock_GetSteamGameServerKeyValueCalls.restype = ctypes.c_int

        lib.QLR_SteamworksMock_GetSteamGameServerLastAccount.argtypes = []
        lib.QLR_SteamworksMock_GetSteamGameServerLastAccount.restype = ctypes.c_char_p

        lib.QLR_SteamworksMock_GetSteamGameServerLastKey.argtypes = []
        lib.QLR_SteamworksMock_GetSteamGameServerLastKey.restype = ctypes.c_char_p

        lib.QLR_SteamworksMock_GetSteamGameServerLastProduct.argtypes = []
        lib.QLR_SteamworksMock_GetSteamGameServerLastProduct.restype = ctypes.c_char_p

        lib.QLR_SteamworksMock_GetSteamGameServerLastGameDir.argtypes = []
        lib.QLR_SteamworksMock_GetSteamGameServerLastGameDir.restype = ctypes.c_char_p

        lib.QLR_SteamworksMock_GetSteamGameServerLastGameDescription.argtypes = []
        lib.QLR_SteamworksMock_GetSteamGameServerLastGameDescription.restype = ctypes.c_char_p

        lib.QLR_SteamworksMock_GetSteamGameServerLastServerName.argtypes = []
        lib.QLR_SteamworksMock_GetSteamGameServerLastServerName.restype = ctypes.c_char_p

        lib.QLR_SteamworksMock_GetSteamGameServerLastMapName.argtypes = []
        lib.QLR_SteamworksMock_GetSteamGameServerLastMapName.restype = ctypes.c_char_p

        lib.QLR_SteamworksMock_GetSteamGameServerLastGameTags.argtypes = []
        lib.QLR_SteamworksMock_GetSteamGameServerLastGameTags.restype = ctypes.c_char_p

        lib.QLR_SteamworksMock_GetSteamGameServerLastUserDataName.argtypes = []
        lib.QLR_SteamworksMock_GetSteamGameServerLastUserDataName.restype = ctypes.c_char_p

        lib.QLR_SteamworksMock_GetSteamGameServerLastUserDataId.argtypes = []
        lib.QLR_SteamworksMock_GetSteamGameServerLastUserDataId.restype = ctypes.c_uint64

        lib.QLR_SteamworksMock_GetSteamGameServerLastUserDataScore.argtypes = []
        lib.QLR_SteamworksMock_GetSteamGameServerLastUserDataScore.restype = ctypes.c_uint32

        lib.QLR_SteamworksMock_GetSteamGameServerLastMaxPlayerCount.argtypes = []
        lib.QLR_SteamworksMock_GetSteamGameServerLastMaxPlayerCount.restype = ctypes.c_int

        lib.QLR_SteamworksMock_GetSteamGameServerLastBotPlayerCount.argtypes = []
        lib.QLR_SteamworksMock_GetSteamGameServerLastBotPlayerCount.restype = ctypes.c_int

        lib.QLR_SteamworksMock_GetSteamGameServerLastPasswordProtected.argtypes = []
        lib.QLR_SteamworksMock_GetSteamGameServerLastPasswordProtected.restype = ctypes.c_int

        lib.QLR_SteamworksMock_GetSteamGameServerLastValue.argtypes = []
        lib.QLR_SteamworksMock_GetSteamGameServerLastValue.restype = ctypes.c_char_p

        lib.QLR_SteamworksMock_GetLobbyCreateCalls.argtypes = []
        lib.QLR_SteamworksMock_GetLobbyCreateCalls.restype = ctypes.c_int

        lib.QLR_SteamworksMock_GetLobbyLeaveCalls.argtypes = []
        lib.QLR_SteamworksMock_GetLobbyLeaveCalls.restype = ctypes.c_int

        lib.QLR_SteamworksMock_GetLobbySetServerCalls.argtypes = []
        lib.QLR_SteamworksMock_GetLobbySetServerCalls.restype = ctypes.c_int

        lib.QLR_SteamworksMock_GetLobbyJoinCalls.argtypes = []
        lib.QLR_SteamworksMock_GetLobbyJoinCalls.restype = ctypes.c_int

        lib.QLR_SteamworksMock_GetLobbyInviteCalls.argtypes = []
        lib.QLR_SteamworksMock_GetLobbyInviteCalls.restype = ctypes.c_int

        lib.QLR_SteamworksMock_GetLobbySayCalls.argtypes = []
        lib.QLR_SteamworksMock_GetLobbySayCalls.restype = ctypes.c_int

        lib.QLR_SteamworksMock_GetUserStatsRequestCalls.argtypes = []
        lib.QLR_SteamworksMock_GetUserStatsRequestCalls.restype = ctypes.c_int

        lib.QLR_SteamworksMock_GetLobbyCreateType.argtypes = []
        lib.QLR_SteamworksMock_GetLobbyCreateType.restype = ctypes.c_int

        lib.QLR_SteamworksMock_GetLobbyCreateMaxMembers.argtypes = []
        lib.QLR_SteamworksMock_GetLobbyCreateMaxMembers.restype = ctypes.c_int

        lib.QLR_SteamworksMock_GetLobbyLeaveId.argtypes = []
        lib.QLR_SteamworksMock_GetLobbyLeaveId.restype = ctypes.c_uint64

        lib.QLR_SteamworksMock_GetLobbyJoinId.argtypes = []
        lib.QLR_SteamworksMock_GetLobbyJoinId.restype = ctypes.c_uint64

        lib.QLR_SteamworksMock_GetLobbySetServerId.argtypes = []
        lib.QLR_SteamworksMock_GetLobbySetServerId.restype = ctypes.c_uint64

        lib.QLR_SteamworksMock_GetLobbyInviteId.argtypes = []
        lib.QLR_SteamworksMock_GetLobbyInviteId.restype = ctypes.c_uint64

        lib.QLR_SteamworksMock_GetLobbySetServerIp.argtypes = []
        lib.QLR_SteamworksMock_GetLobbySetServerIp.restype = ctypes.c_uint32

        lib.QLR_SteamworksMock_GetLobbySetServerPort.argtypes = []
        lib.QLR_SteamworksMock_GetLobbySetServerPort.restype = ctypes.c_uint16

        lib.QLR_SteamworksMock_GetLobbySetServerGameServerId.argtypes = []
        lib.QLR_SteamworksMock_GetLobbySetServerGameServerId.restype = ctypes.c_uint64

        lib.QLR_SteamworksMock_GetLobbySayId.argtypes = []
        lib.QLR_SteamworksMock_GetLobbySayId.restype = ctypes.c_uint64

        lib.QLR_SteamworksMock_GetLobbySayMessage.argtypes = []
        lib.QLR_SteamworksMock_GetLobbySayMessage.restype = ctypes.c_char_p

        lib.QLR_SteamworksMock_GetUserStatsRequestId.argtypes = []
        lib.QLR_SteamworksMock_GetUserStatsRequestId.restype = ctypes.c_uint64

        lib.QLR_SteamworksMock_GetUGCSubscribeCalls.argtypes = []
        lib.QLR_SteamworksMock_GetUGCSubscribeCalls.restype = ctypes.c_int

        lib.QLR_SteamworksMock_GetUGCUnsubscribeCalls.argtypes = []
        lib.QLR_SteamworksMock_GetUGCUnsubscribeCalls.restype = ctypes.c_int

        lib.QLR_SteamworksMock_GetUGCDownloadCalls.argtypes = []
        lib.QLR_SteamworksMock_GetUGCDownloadCalls.restype = ctypes.c_int

        lib.QLR_SteamworksMock_GetSteamGameServerUGCSubscribeCalls.argtypes = []
        lib.QLR_SteamworksMock_GetSteamGameServerUGCSubscribeCalls.restype = ctypes.c_int

        lib.QLR_SteamworksMock_GetSteamGameServerUGCUnsubscribeCalls.argtypes = []
        lib.QLR_SteamworksMock_GetSteamGameServerUGCUnsubscribeCalls.restype = ctypes.c_int

        lib.QLR_SteamworksMock_GetSteamGameServerUGCDownloadCalls.argtypes = []
        lib.QLR_SteamworksMock_GetSteamGameServerUGCDownloadCalls.restype = ctypes.c_int

        lib.QLR_SteamworksMock_GetSteamGameServerUGCLastItemId.argtypes = []
        lib.QLR_SteamworksMock_GetSteamGameServerUGCLastItemId.restype = ctypes.c_uint64

        lib.QLR_SteamworksMock_GetSteamGameServerUGCLastHighPriority.argtypes = []
        lib.QLR_SteamworksMock_GetSteamGameServerUGCLastHighPriority.restype = ctypes.c_int

        lib.QLR_SteamworksMock_GetUGCLastItemId.argtypes = []
        lib.QLR_SteamworksMock_GetUGCLastItemId.restype = ctypes.c_uint64

        lib.QLR_SteamworksMock_GetUGCLastHighPriority.argtypes = []
        lib.QLR_SteamworksMock_GetUGCLastHighPriority.restype = ctypes.c_int

        lib.QLR_SteamworksMock_SetAppId.argtypes = [ctypes.c_uint32]
        lib.QLR_SteamworksMock_SetAppId.restype = None

        lib.QLR_SteamworksMock_SetLobbyChatEntryMessage.argtypes = [ctypes.c_char_p]
        lib.QLR_SteamworksMock_SetLobbyChatEntryMessage.restype = None

        lib.QLR_Steamworks_RegisterHarnessCallbacks.argtypes = []
        lib.QLR_Steamworks_RegisterHarnessCallbacks.restype = ctypes.c_int

        lib.QLR_Steamworks_UnregisterHarnessCallbacks.argtypes = []
        lib.QLR_Steamworks_UnregisterHarnessCallbacks.restype = None

        lib.QLR_Steamworks_BindUGCQueryCallResult.argtypes = [ctypes.c_uint64]
        lib.QLR_Steamworks_BindUGCQueryCallResult.restype = ctypes.c_int

        lib.QLR_Steamworks_RunCallbackPump.argtypes = []
        lib.QLR_Steamworks_RunCallbackPump.restype = None

        lib.QLR_SteamworksMock_QueueRichPresenceJoinRequested.argtypes = [ctypes.c_uint64, ctypes.c_char_p]
        lib.QLR_SteamworksMock_QueueRichPresenceJoinRequested.restype = ctypes.c_int

        lib.QLR_SteamworksMock_QueueLobbyEnter.argtypes = [ctypes.c_uint64, ctypes.c_uint32, ctypes.c_int, ctypes.c_uint32]
        lib.QLR_SteamworksMock_QueueLobbyEnter.restype = ctypes.c_int

        lib.QLR_SteamworksMock_QueueMicroAuthorizationResponse.argtypes = [ctypes.c_uint32, ctypes.c_uint64, ctypes.c_int]
        lib.QLR_SteamworksMock_QueueMicroAuthorizationResponse.restype = ctypes.c_int

        lib.QLR_SteamworksMock_QueueItemInstalled.argtypes = [ctypes.c_uint32, ctypes.c_uint32, ctypes.c_uint32]
        lib.QLR_SteamworksMock_QueueItemInstalled.restype = ctypes.c_int

        lib.QLR_SteamworksMock_QueueDownloadItemResult.argtypes = [
            ctypes.c_uint32,
            ctypes.c_uint32,
            ctypes.c_uint32,
            ctypes.c_int,
        ]
        lib.QLR_SteamworksMock_QueueDownloadItemResult.restype = ctypes.c_int

        lib.QLR_SteamworksMock_QueueUGCQueryCompleted.argtypes = [
            ctypes.c_uint64,
            ctypes.c_uint64,
            ctypes.c_int,
            ctypes.c_uint32,
            ctypes.c_uint32,
            ctypes.c_int,
        ]
        lib.QLR_SteamworksMock_QueueUGCQueryCompleted.restype = ctypes.c_int

        lib.QLR_SteamworksMock_GetRegisterCallbackCalls.argtypes = []
        lib.QLR_SteamworksMock_GetRegisterCallbackCalls.restype = ctypes.c_int

        lib.QLR_SteamworksMock_GetUnregisterCallbackCalls.argtypes = []
        lib.QLR_SteamworksMock_GetUnregisterCallbackCalls.restype = ctypes.c_int

        lib.QLR_SteamworksMock_GetRegisterCallResultCalls.argtypes = []
        lib.QLR_SteamworksMock_GetRegisterCallResultCalls.restype = ctypes.c_int

        lib.QLR_SteamworksMock_GetUnregisterCallResultCalls.argtypes = []
        lib.QLR_SteamworksMock_GetUnregisterCallResultCalls.restype = ctypes.c_int

        lib.QLR_SteamworksMock_GetClientCallbackCaptureCount.argtypes = []
        lib.QLR_SteamworksMock_GetClientCallbackCaptureCount.restype = ctypes.c_int

        lib.QLR_SteamworksMock_GetLastCallbackKind.argtypes = []
        lib.QLR_SteamworksMock_GetLastCallbackKind.restype = ctypes.c_char_p

        lib.QLR_SteamworksMock_GetLastCallbackText.argtypes = []
        lib.QLR_SteamworksMock_GetLastCallbackText.restype = ctypes.c_char_p

        lib.QLR_SteamworksMock_GetLastCallbackId.argtypes = []
        lib.QLR_SteamworksMock_GetLastCallbackId.restype = ctypes.c_uint64

        lib.QLR_SteamworksMock_GetLastCallbackAuxId.argtypes = []
        lib.QLR_SteamworksMock_GetLastCallbackAuxId.restype = ctypes.c_uint64

        lib.QLR_SteamworksMock_GetLastCallbackAppId.argtypes = []
        lib.QLR_SteamworksMock_GetLastCallbackAppId.restype = ctypes.c_uint32

        lib.QLR_SteamworksMock_GetLastCallbackResult.argtypes = []
        lib.QLR_SteamworksMock_GetLastCallbackResult.restype = ctypes.c_int

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


def test_cancel_ticket_routes_to_steam_user_cancel_path(steamworks_harness: tuple[ctypes.CDLL, bool]) -> None:
    lib, enabled = steamworks_harness

    if not enabled:
        assert lib.QLR_Steamworks_CancelTicket(99) == 0
        return

    lib.QLR_SteamworksMock_Reset()
    lib.QLR_SteamworksMock_PrimeState()
    assert lib.QLR_Steamworks_Init() != 0

    assert lib.QLR_Steamworks_CancelTicket(99) != 0
    assert lib.QLR_SteamworksMock_GetCancelAuthTicketCalls() == 1
    assert lib.QLR_SteamworksMock_GetCancelledTicketHandle() == 99


def test_load_avatar_returns_expected_rgba_payload(steamworks_harness: tuple[ctypes.CDLL, bool]) -> None:
    lib, enabled = steamworks_harness

    out_width = ctypes.c_uint32()
    out_height = ctypes.c_uint32()
    out_length = ctypes.c_uint32()
    buffer = (ctypes.c_uint8 * AVATAR_BUFFER)()

    if not enabled:
        assert not lib.QLR_Steamworks_LoadAvatar(
            0x89ABCDEF,
            0x01234567,
            AVATAR_SIZE_LARGE,
            buffer,
            len(buffer),
            ctypes.byref(out_width),
            ctypes.byref(out_height),
            ctypes.byref(out_length),
        )
        return

    lib.QLR_SteamworksMock_Reset()
    lib.QLR_SteamworksMock_PrimeState()

    pixels = (ctypes.c_uint8 * 16)(
        0x10, 0x20, 0x30, 0x40,
        0x50, 0x60, 0x70, 0x80,
        0x90, 0xA0, 0xB0, 0xC0,
        0xD0, 0xE0, 0xF0, 0xFF,
    )
    lib.QLR_SteamworksMock_SetAvatarHandles(0, 0, 77)
    lib.QLR_SteamworksMock_SetAvatarPixels(2, 2, pixels, len(pixels))

    assert lib.QLR_Steamworks_LoadAvatar(
        0x89ABCDEF,
        0x01234567,
        AVATAR_SIZE_LARGE,
        buffer,
        len(buffer),
        ctypes.byref(out_width),
        ctypes.byref(out_height),
        ctypes.byref(out_length),
    )
    assert out_width.value == 2
    assert out_height.value == 2
    assert out_length.value == 16
    assert bytes(buffer[: out_length.value]) == bytes(pixels)


def test_load_avatar_uses_requested_size_slot(steamworks_harness: tuple[ctypes.CDLL, bool]) -> None:
    lib, enabled = steamworks_harness

    if not enabled:
        return

    lib.QLR_SteamworksMock_Reset()
    lib.QLR_SteamworksMock_PrimeState()
    lib.QLR_SteamworksMock_SetAvatarHandles(0, 55, 0)

    pixels = (ctypes.c_uint8 * 16)(
        0x01, 0x02, 0x03, 0x04,
        0x05, 0x06, 0x07, 0x08,
        0x09, 0x0A, 0x0B, 0x0C,
        0x0D, 0x0E, 0x0F, 0x10,
    )
    lib.QLR_SteamworksMock_SetAvatarPixels(2, 2, pixels, len(pixels))

    buffer = (ctypes.c_uint8 * AVATAR_BUFFER)()
    out_width = ctypes.c_uint32()
    out_height = ctypes.c_uint32()
    out_length = ctypes.c_uint32()

    assert lib.QLR_Steamworks_LoadAvatar(
        0x11111111,
        0x22222222,
        AVATAR_SIZE_MEDIUM,
        buffer,
        len(buffer),
        ctypes.byref(out_width),
        ctypes.byref(out_height),
        ctypes.byref(out_length),
    )

    assert not lib.QLR_Steamworks_LoadAvatar(
        0x11111111,
        0x22222222,
        AVATAR_SIZE_LARGE,
        buffer,
        len(buffer),
        ctypes.byref(out_width),
        ctypes.byref(out_height),
        ctypes.byref(out_length),
    )


def test_activate_overlay_routes_dialog_and_identity(steamworks_harness: tuple[ctypes.CDLL, bool]) -> None:
    lib, enabled = steamworks_harness

    if not enabled:
        assert not lib.QLR_Steamworks_ActivateOverlay(b"steamid", 0x89ABCDEF, 0x01234567)
        return

    lib.QLR_SteamworksMock_Reset()
    lib.QLR_SteamworksMock_PrimeState()

    assert lib.QLR_Steamworks_ActivateOverlay(b"friendadd", 0x89ABCDEF, 0x01234567)
    assert lib.QLR_SteamworksMock_GetOverlayCallCount() == 1
    assert lib.QLR_SteamworksMock_GetOverlayDialog() == b"friendadd"
    assert lib.QLR_SteamworksMock_GetOverlaySteamId() == 0x0123456789ABCDEF


def test_set_rich_presence_uses_mapped_friends_slot(steamworks_harness: tuple[ctypes.CDLL, bool]) -> None:
    lib, enabled = steamworks_harness

    if not enabled:
        assert not lib.QLR_Steamworks_SetRichPresence(b"status", b"At the main menu")
        return

    lib.QLR_SteamworksMock_Reset()
    lib.QLR_SteamworksMock_PrimeState()

    assert lib.QLR_Steamworks_SetRichPresence(b"status", b"At the main menu")
    assert lib.QLR_SteamworksMock_GetRichPresenceCallCount() == 1
    assert lib.QLR_SteamworksMock_GetRichPresenceKey() == b"status"
    assert lib.QLR_SteamworksMock_GetRichPresenceValue() == b"At the main menu"


def test_game_server_helpers_use_mapped_server_slots(steamworks_harness: tuple[ctypes.CDLL, bool]) -> None:
    lib, enabled = steamworks_harness
    steam_id_low = ctypes.c_uint32()
    steam_id_high = ctypes.c_uint32()

    if not enabled:
        assert not lib.QLR_Steamworks_Init()
        assert not lib.QLR_Steamworks_ServerInit(0x01020304, 27960, 1, 1)
        assert not lib.QLR_Steamworks_ServerIsInitialised()
        assert not lib.QLR_Steamworks_ServerEnableHeartbeats(1)
        assert not lib.QLR_Steamworks_ServerSetDedicated(1)
        assert not lib.QLR_Steamworks_ServerLogOn(b"token")
        assert not lib.QLR_Steamworks_ServerSetProduct(b"Quake Live")
        assert not lib.QLR_Steamworks_ServerSetGameDir(b"baseq3")
        assert not lib.QLR_Steamworks_ServerSetGameDescription(b"Clan Arena")
        assert not lib.QLR_Steamworks_ServerSetMaxPlayerCount(16)
        assert not lib.QLR_Steamworks_ServerSetBotPlayerCount(3)
        assert not lib.QLR_Steamworks_ServerSetServerName(b"QLR Test Server")
        assert not lib.QLR_Steamworks_ServerSetMapName(b"campgrounds")
        assert not lib.QLR_Steamworks_ServerSetPasswordProtected(1)
        assert not lib.QLR_Steamworks_ServerGetSteamID(ctypes.byref(steam_id_low), ctypes.byref(steam_id_high))
        assert not lib.QLR_Steamworks_ServerSetGameTags(b"duel,instagib")
        assert not lib.QLR_Steamworks_ServerSetKeyValue(b"g_redScore", b"5")
        assert not lib.QLR_Steamworks_ServerSetKeyValuesFromInfoString(b"\\mapname\\campgrounds")
        assert not lib.QLR_Steamworks_ServerUpdateUserData(0x89ABCDEF, 0x01234567, b"QLR Player", 42)
        assert steam_id_low.value == 0
        assert steam_id_high.value == 0
        assert lib.QLR_Steamworks_ServerGetPublicIP() == 0
        return

    lib.QLR_SteamworksMock_Reset()
    lib.QLR_SteamworksMock_PrimeState()
    lib.QLR_SteamworksMock_SetSteamGameServerId(0x0FEDCBA987654321)
    lib.QLR_SteamworksMock_SetSteamGameServerPublicIP(0x11223344)

    assert lib.QLR_Steamworks_Init()
    assert not lib.QLR_Steamworks_ServerIsInitialised()
    assert lib.QLR_Steamworks_ServerInit(0x01020304, 27960, 1, 1)
    assert lib.QLR_Steamworks_ServerIsInitialised()
    assert lib.QLR_Steamworks_ServerEnableHeartbeats(1)
    assert lib.QLR_Steamworks_ServerSetDedicated(1)
    assert lib.QLR_Steamworks_ServerLogOn(b"token-123")
    assert lib.QLR_Steamworks_ServerSetProduct(b"Quake Live")
    assert lib.QLR_Steamworks_ServerSetGameDir(b"baseq3")
    assert lib.QLR_Steamworks_ServerSetGameDescription(b"Clan Arena")
    assert lib.QLR_Steamworks_ServerSetMaxPlayerCount(16)
    assert lib.QLR_Steamworks_ServerSetBotPlayerCount(3)
    assert lib.QLR_Steamworks_ServerSetServerName(b"QLR Test Server")
    assert lib.QLR_Steamworks_ServerSetMapName(b"campgrounds")
    assert lib.QLR_Steamworks_ServerSetPasswordProtected(1)
    assert lib.QLR_Steamworks_ServerGetSteamID(ctypes.byref(steam_id_low), ctypes.byref(steam_id_high))
    assert steam_id_low.value == 0x87654321
    assert steam_id_high.value == 0x0FEDCBA9
    assert lib.QLR_Steamworks_ServerSetGameTags(b"duel,instagib")
    assert lib.QLR_Steamworks_ServerSetKeyValue(b"g_redScore", b"5")
    assert lib.QLR_Steamworks_ServerSetKeyValuesFromInfoString(b"\\gametype\\ca\\mapname\\campgrounds")
    assert lib.QLR_Steamworks_ServerUpdateUserData(0x89ABCDEF, 0x01234567, b"QLR Player", 42)
    assert lib.QLR_Steamworks_ServerGetPublicIP() == 0x11223344
    assert lib.QLR_Steamworks_ServerLogOn(b"")
    assert lib.QLR_Steamworks_ServerEnableHeartbeats(0)

    assert lib.QLR_SteamworksMock_GetSteamGameServerHeartbeatCalls() == 2
    assert lib.QLR_SteamworksMock_GetSteamGameServerLastHeartbeatEnabled() == 0
    assert lib.QLR_SteamworksMock_GetSteamGameServerDedicatedCalls() == 1
    assert lib.QLR_SteamworksMock_GetSteamGameServerLastDedicated() == 1
    assert lib.QLR_SteamworksMock_GetSteamGameServerLogOnCalls() == 1
    assert lib.QLR_SteamworksMock_GetSteamGameServerLogOnAnonymousCalls() == 1
    assert lib.QLR_SteamworksMock_GetSteamGameServerLastAccount() == b"token-123"
    assert lib.QLR_SteamworksMock_GetSteamGameServerProductCalls() == 1
    assert lib.QLR_SteamworksMock_GetSteamGameServerLastProduct() == b"Quake Live"
    assert lib.QLR_SteamworksMock_GetSteamGameServerGameDirCalls() == 1
    assert lib.QLR_SteamworksMock_GetSteamGameServerLastGameDir() == b"baseq3"
    assert lib.QLR_SteamworksMock_GetSteamGameServerGameDescriptionCalls() == 1
    assert lib.QLR_SteamworksMock_GetSteamGameServerLastGameDescription() == b"Clan Arena"
    assert lib.QLR_SteamworksMock_GetSteamGameServerMaxPlayerCountCalls() == 1
    assert lib.QLR_SteamworksMock_GetSteamGameServerLastMaxPlayerCount() == 16
    assert lib.QLR_SteamworksMock_GetSteamGameServerBotPlayerCountCalls() == 1
    assert lib.QLR_SteamworksMock_GetSteamGameServerLastBotPlayerCount() == 3
    assert lib.QLR_SteamworksMock_GetSteamGameServerServerNameCalls() == 1
    assert lib.QLR_SteamworksMock_GetSteamGameServerLastServerName() == b"QLR Test Server"
    assert lib.QLR_SteamworksMock_GetSteamGameServerMapNameCalls() == 1
    assert lib.QLR_SteamworksMock_GetSteamGameServerLastMapName() == b"campgrounds"
    assert lib.QLR_SteamworksMock_GetSteamGameServerPasswordCalls() == 1
    assert lib.QLR_SteamworksMock_GetSteamGameServerLastPasswordProtected() == 1
    assert lib.QLR_SteamworksMock_GetSteamGameServerGameTagsCalls() == 1
    assert lib.QLR_SteamworksMock_GetSteamGameServerLastGameTags() == b"duel,instagib"
    assert lib.QLR_SteamworksMock_GetSteamGameServerUserDataCalls() == 1
    assert lib.QLR_SteamworksMock_GetSteamGameServerLastUserDataId() == 0x0123456789ABCDEF
    assert lib.QLR_SteamworksMock_GetSteamGameServerLastUserDataName() == b"QLR Player"
    assert lib.QLR_SteamworksMock_GetSteamGameServerLastUserDataScore() == 42
    assert lib.QLR_SteamworksMock_GetSteamGameServerKeyValueCalls() == 3
    assert lib.QLR_SteamworksMock_GetSteamGameServerLastKey() == b"mapname"
    assert lib.QLR_SteamworksMock_GetSteamGameServerLastValue() == b"campgrounds"


def test_game_server_init_uses_retail_init_signature_and_dedicated_ugc_owner(steamworks_harness: tuple[ctypes.CDLL, bool]) -> None:
    lib, enabled = steamworks_harness

    if not enabled:
        assert not lib.QLR_Steamworks_ServerInit(0x01020304, 27960, 1, 1)
        return

    lib.QLR_SteamworksMock_Reset()
    lib.QLR_SteamworksMock_PrimeState()

    assert lib.QLR_Steamworks_ServerInit(0x01020304, 27960, 1, 1)
    assert lib.QLR_SteamworksMock_GetSteamGameServerInitCalls() == 1
    assert lib.QLR_SteamworksMock_GetSteamGameServerLastInitIP() == 0x01020304
    assert lib.QLR_SteamworksMock_GetSteamGameServerLastInitGamePort() == 27960
    assert lib.QLR_SteamworksMock_GetSteamGameServerLastInitServerMode() == 3
    assert lib.QLR_SteamworksMock_GetSteamGameServerLastInitVersion() == b"1069"
    assert lib.QLR_Steamworks_ServerIsInitialised()

    lib.QLR_SteamworksMock_SetUGCItemState(4)
    assert lib.QLR_Steamworks_SubscribeItem(0x89ABCDEF, 0x01234567)
    assert lib.QLR_Steamworks_DownloadItem(0x89ABCDEF, 0x01234567, 1)
    assert lib.QLR_SteamworksMock_GetUGCSubscribeCalls() == 0
    assert lib.QLR_SteamworksMock_GetUGCDownloadCalls() == 0
    assert lib.QLR_SteamworksMock_GetSteamGameServerUGCSubscribeCalls() == 1
    assert lib.QLR_SteamworksMock_GetSteamGameServerUGCDownloadCalls() == 1
    assert lib.QLR_SteamworksMock_GetSteamGameServerUGCLastItemId() == 0x0123456789ABCDEF
    assert lib.QLR_SteamworksMock_GetSteamGameServerUGCLastHighPriority() == 1

    lib.QLR_Steamworks_ServerShutdown()
    assert not lib.QLR_Steamworks_ServerIsInitialised()
    assert lib.QLR_SteamworksMock_GetSteamGameServerShutdownCalls() == 1


def test_shutdown_cascades_game_server_shutdown(steamworks_harness: tuple[ctypes.CDLL, bool]) -> None:
    lib, enabled = steamworks_harness

    if not enabled:
        lib.QLR_Steamworks_Shutdown()
        return

    lib.QLR_SteamworksMock_Reset()
    lib.QLR_SteamworksMock_PrimeState()

    assert lib.QLR_Steamworks_Init()
    assert lib.QLR_Steamworks_ServerInit(0x01020304, 27960, 1, 1)

    lib.QLR_Steamworks_Shutdown()

    assert lib.QLR_SteamworksMock_GetSteamGameServerShutdownCalls() == 1
    assert not lib.QLR_Steamworks_ServerIsInitialised()


def test_lobby_helpers_use_mapped_matchmaking_slots(steamworks_harness: tuple[ctypes.CDLL, bool]) -> None:
    lib, enabled = steamworks_harness

    if not enabled:
        assert not lib.QLR_Steamworks_CreateLobby(24)
        assert not lib.QLR_Steamworks_LeaveLobby(0x01234567, 0x89ABCDEF)
        assert not lib.QLR_Steamworks_JoinLobby(0xAAAAAAAA, 0xBBBBBBBB)
        assert not lib.QLR_Steamworks_SetLobbyServer(0x33333333, 0x44444444, 0x01020304, 27960)
        assert not lib.QLR_Steamworks_ShowInviteOverlay(0xCCCCCCCC, 0xDDDDDDDD)
        assert not lib.QLR_Steamworks_SayLobby(0x11111111, 0x22222222, b"hello lobby")
        assert not lib.QLR_Steamworks_RequestUserStats(0x12345678, 0x9ABCDEF0)
        return

    lib.QLR_SteamworksMock_Reset()
    lib.QLR_SteamworksMock_PrimeState()

    assert lib.QLR_Steamworks_CreateLobby(24)
    assert lib.QLR_Steamworks_LeaveLobby(0x01234567, 0x89ABCDEF)
    assert lib.QLR_Steamworks_JoinLobby(0xAAAAAAAA, 0xBBBBBBBB)
    assert lib.QLR_Steamworks_SetLobbyServer(0x33333333, 0x44444444, 0x01020304, 27960)
    assert lib.QLR_Steamworks_ShowInviteOverlay(0xCCCCCCCC, 0xDDDDDDDD)
    assert lib.QLR_Steamworks_SayLobby(0x11111111, 0x22222222, b"hello lobby")
    assert lib.QLR_Steamworks_RequestUserStats(0x12345678, 0x9ABCDEF0)

    assert lib.QLR_SteamworksMock_GetLobbyCreateCalls() == 1
    assert lib.QLR_SteamworksMock_GetLobbyLeaveCalls() == 1
    assert lib.QLR_SteamworksMock_GetLobbyJoinCalls() == 1
    assert lib.QLR_SteamworksMock_GetLobbySetServerCalls() == 1
    assert lib.QLR_SteamworksMock_GetLobbyInviteCalls() == 1
    assert lib.QLR_SteamworksMock_GetLobbySayCalls() == 1
    assert lib.QLR_SteamworksMock_GetUserStatsRequestCalls() == 1
    assert lib.QLR_SteamworksMock_GetLobbyCreateType() == 2
    assert lib.QLR_SteamworksMock_GetLobbyCreateMaxMembers() == 24
    assert lib.QLR_SteamworksMock_GetLobbyLeaveId() == 0x89ABCDEF01234567
    assert lib.QLR_SteamworksMock_GetLobbyJoinId() == 0xBBBBBBBBAAAAAAAA
    assert lib.QLR_SteamworksMock_GetLobbySetServerId() == 0x4444444433333333
    assert lib.QLR_SteamworksMock_GetLobbySetServerIp() == 0x01020304
    assert lib.QLR_SteamworksMock_GetLobbySetServerPort() == 27960
    assert lib.QLR_SteamworksMock_GetLobbySetServerGameServerId() == 0x4444444433333333
    assert lib.QLR_SteamworksMock_GetLobbyInviteId() == 0xDDDDDDDDCCCCCCCC
    assert lib.QLR_SteamworksMock_GetLobbySayId() == 0x2222222211111111
    assert lib.QLR_SteamworksMock_GetLobbySayMessage() == b"hello lobby"
    assert lib.QLR_SteamworksMock_GetUserStatsRequestId() == 0x9ABCDEF012345678


def test_set_lobby_server_requires_local_lobby_ownership(steamworks_harness: tuple[ctypes.CDLL, bool]) -> None:
    lib, enabled = steamworks_harness

    if not enabled:
        return

    lib.QLR_SteamworksMock_Reset()
    lib.QLR_SteamworksMock_PrimeState()
    lib.QLR_SteamworksMock_SetSteamId(0x0123456789ABCDEF)
    lib.QLR_SteamworksMock_SetLobbyOwnerId(0x0FEDCBA987654321)

    assert not lib.QLR_Steamworks_SetLobbyServer(0xAAAAAAAA, 0xBBBBBBBB, 0x7F000001, 27960)
    assert lib.QLR_SteamworksMock_GetLobbySetServerCalls() == 0


def test_workshop_helpers_use_mapped_ugc_slots(steamworks_harness: tuple[ctypes.CDLL, bool]) -> None:
    lib, enabled = steamworks_harness

    if not enabled:
        assert not lib.QLR_Steamworks_SubscribeItem(0xAAAAAAAA, 0xBBBBBBBB)
        assert not lib.QLR_Steamworks_UnsubscribeItem(0xAAAAAAAA, 0xBBBBBBBB)
        assert not lib.QLR_Steamworks_DownloadItem(0xAAAAAAAA, 0xBBBBBBBB, 1)
        return

    lib.QLR_SteamworksMock_Reset()
    lib.QLR_SteamworksMock_PrimeState()
    lib.QLR_SteamworksMock_SetUGCItemState(0)

    assert not lib.QLR_Steamworks_SubscribeItem(0xAAAAAAAA, 0xBBBBBBBB)
    assert lib.QLR_SteamworksMock_GetUGCSubscribeCalls() == 1

    lib.QLR_SteamworksMock_Reset()
    lib.QLR_SteamworksMock_PrimeState()
    lib.QLR_SteamworksMock_SetUGCItemState(4)
    lib.QLR_SteamworksMock_SetUGCDownloadInfo(123, 456)

    assert lib.QLR_Steamworks_SubscribeItem(0xAAAAAAAA, 0xBBBBBBBB)
    assert lib.QLR_Steamworks_UnsubscribeItem(0xAAAAAAAA, 0xBBBBBBBB)
    assert lib.QLR_Steamworks_DownloadItem(0xAAAAAAAA, 0xBBBBBBBB, 1)

    assert lib.QLR_SteamworksMock_GetUGCSubscribeCalls() == 1
    assert lib.QLR_SteamworksMock_GetUGCUnsubscribeCalls() == 1
    assert lib.QLR_SteamworksMock_GetUGCDownloadCalls() == 1
    assert lib.QLR_SteamworksMock_GetUGCLastItemId() == 0xBBBBBBBBAAAAAAAA
    assert lib.QLR_SteamworksMock_GetUGCLastHighPriority() == 1


def test_workshop_subscription_enumeration_uses_retail_ugc_mount_slots(
    steamworks_harness: tuple[ctypes.CDLL, bool],
) -> None:
    lib, enabled = steamworks_harness
    subscribed_items = (ctypes.c_uint64 * 3)(
        0x0123456789ABCDEF,
        0x1111111122222222,
        0x3333333344444444,
    )
    copied_items = (ctypes.c_uint64 * 2)()
    size_on_disk = ctypes.c_uint64()
    timestamp = ctypes.c_uint32()
    install_folder = ctypes.create_string_buffer(260)

    if not enabled:
        assert lib.QLR_Steamworks_GetNumSubscribedItems() == 0
        assert lib.QLR_Steamworks_GetSubscribedItems(copied_items, len(copied_items)) == 0
        assert not lib.QLR_Steamworks_GetItemInstallInfo(
            0x89ABCDEF,
            0x01234567,
            ctypes.byref(size_on_disk),
            install_folder,
            len(install_folder),
            ctypes.byref(timestamp),
        )
        return

    lib.QLR_SteamworksMock_Reset()
    lib.QLR_SteamworksMock_PrimeState()
    lib.QLR_SteamworksMock_SetSubscribedItems(subscribed_items, len(subscribed_items))
    lib.QLR_SteamworksMock_SetUGCInstallInfo(
        subscribed_items[1],
        987654321,
        b"C:\\Workshop\\1111111122222222",
        77,
    )

    assert lib.QLR_Steamworks_GetNumSubscribedItems() == 3
    assert lib.QLR_Steamworks_GetSubscribedItems(copied_items, len(copied_items)) == 2
    assert list(copied_items) == [
        0x0123456789ABCDEF,
        0x1111111122222222,
    ]

    assert lib.QLR_Steamworks_GetItemInstallInfo(
        0x22222222,
        0x11111111,
        ctypes.byref(size_on_disk),
        install_folder,
        len(install_folder),
        ctypes.byref(timestamp),
    )
    assert size_on_disk.value == 987654321
    assert timestamp.value == 77
    assert install_folder.value == b"C:\\Workshop\\1111111122222222"


def test_callback_bundle_registration_and_dispatch_reconstructs_retail_client_owner(
    steamworks_harness: tuple[ctypes.CDLL, bool],
) -> None:
    lib, enabled = steamworks_harness

    if not enabled:
        return

    lib.QLR_SteamworksMock_Reset()
    lib.QLR_SteamworksMock_PrimeState()
    lib.QLR_SteamworksMock_SetAppId(0x54100)
    lib.QLR_SteamworksMock_SetLobbyChatEntryMessage(b"queued lobby chat")

    assert lib.QLR_Steamworks_RegisterHarnessCallbacks()
    assert lib.QLR_SteamworksMock_GetRegisterCallbackCalls() == 17

    assert lib.QLR_SteamworksMock_QueueRichPresenceJoinRequested(0x0123456789ABCDEF, b"connect 127.0.0.1")
    lib.QLR_Steamworks_RunCallbackPump()

    assert lib.QLR_SteamworksMock_GetClientCallbackCaptureCount() == 1
    assert lib.QLR_SteamworksMock_GetLastCallbackKind() == b"rich_presence"
    assert lib.QLR_SteamworksMock_GetLastCallbackText() == b"connect 127.0.0.1"
    assert lib.QLR_SteamworksMock_GetLastCallbackId() == 0x0123456789ABCDEF

    assert lib.QLR_SteamworksMock_QueueLobbyEnter(0x0FEDCBA987654321, 7, 0, 1)
    lib.QLR_Steamworks_RunCallbackPump()

    assert lib.QLR_SteamworksMock_GetClientCallbackCaptureCount() == 2
    assert lib.QLR_SteamworksMock_GetLastCallbackKind() == b"lobby_enter"
    assert lib.QLR_SteamworksMock_GetLastCallbackId() == 0x0FEDCBA987654321
    assert lib.QLR_SteamworksMock_GetLastCallbackAppId() == 7
    assert lib.QLR_SteamworksMock_GetLastCallbackResult() == 1

    assert lib.QLR_SteamworksMock_QueueMicroAuthorizationResponse(0x54100, 99, 1)
    lib.QLR_Steamworks_RunCallbackPump()

    assert lib.QLR_SteamworksMock_GetClientCallbackCaptureCount() == 3
    assert lib.QLR_SteamworksMock_GetLastCallbackKind() == b"microtxn"
    assert lib.QLR_SteamworksMock_GetLastCallbackId() == 99
    assert lib.QLR_SteamworksMock_GetLastCallbackAppId() == 0x54100
    assert lib.QLR_SteamworksMock_GetLastCallbackResult() == 1

    assert lib.QLR_SteamworksMock_QueueItemInstalled(0x54100, 0x89ABCDEF, 0x01234567)
    lib.QLR_Steamworks_RunCallbackPump()

    assert lib.QLR_SteamworksMock_GetClientCallbackCaptureCount() == 4
    assert lib.QLR_SteamworksMock_GetLastCallbackKind() == b"workshop_installed"
    assert lib.QLR_SteamworksMock_GetLastCallbackId() == 0x0123456789ABCDEF
    assert lib.QLR_SteamworksMock_GetLastCallbackAppId() == 0x54100
    assert lib.QLR_SteamworksMock_GetLastCallbackResult() == 0

    assert lib.QLR_SteamworksMock_QueueDownloadItemResult(0x54100, 0x89ABCDEF, 0x01234567, 1)
    lib.QLR_Steamworks_RunCallbackPump()

    assert lib.QLR_SteamworksMock_GetClientCallbackCaptureCount() == 5
    assert lib.QLR_SteamworksMock_GetLastCallbackKind() == b"workshop_download_result"
    assert lib.QLR_SteamworksMock_GetLastCallbackId() == 0x0123456789ABCDEF
    assert lib.QLR_SteamworksMock_GetLastCallbackAppId() == 0x54100
    assert lib.QLR_SteamworksMock_GetLastCallbackResult() == 1

    lib.QLR_Steamworks_UnregisterHarnessCallbacks()
    assert lib.QLR_SteamworksMock_GetUnregisterCallbackCalls() == 17


def test_ugc_call_result_binding_routes_through_registered_client_bundle(
    steamworks_harness: tuple[ctypes.CDLL, bool],
) -> None:
    lib, enabled = steamworks_harness

    if not enabled:
        return

    lib.QLR_SteamworksMock_Reset()
    lib.QLR_SteamworksMock_PrimeState()

    assert lib.QLR_Steamworks_RegisterHarnessCallbacks()
    assert lib.QLR_Steamworks_BindUGCQueryCallResult(0xAABBCCDD)
    assert lib.QLR_SteamworksMock_GetRegisterCallResultCalls() == 1

    assert lib.QLR_SteamworksMock_QueueUGCQueryCompleted(0xAABBCCDD, 0x1122334455667788, 1, 3, 5, 1)
    lib.QLR_Steamworks_RunCallbackPump()

    assert lib.QLR_SteamworksMock_GetClientCallbackCaptureCount() == 1
    assert lib.QLR_SteamworksMock_GetLastCallbackKind() == b"ugc"
    assert lib.QLR_SteamworksMock_GetLastCallbackId() == 0xAABBCCDD
    assert lib.QLR_SteamworksMock_GetLastCallbackAuxId() == 0x1122334455667788
    assert lib.QLR_SteamworksMock_GetLastCallbackAppId() == 3
    assert lib.QLR_SteamworksMock_GetLastCallbackResult() == 1

    lib.QLR_Steamworks_UnregisterHarnessCallbacks()
    assert lib.QLR_SteamworksMock_GetUnregisterCallResultCalls() == 1
