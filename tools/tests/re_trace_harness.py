"""Trace harness driving the clean-room native prototypes."""
from __future__ import annotations

import ctypes
import difflib
import os
import re
from dataclasses import dataclass
from pathlib import Path
from typing import List

REPO_ROOT = Path(__file__).resolve().parents[2]
LOG_PATH = REPO_ROOT / "logs" / "re" / "native-shim.log"


@dataclass
class TraceHarnessResult:
    """Summary of a trace harness invocation."""

    log_path: Path
    diff_path: Path
    matches_expectation: bool


class _CallbackRegistry:
    """Keep :mod:`ctypes` callbacks and structures alive."""

    def __init__(self) -> None:
        self._callbacks: List[ctypes._CFuncPtr] = []  # type: ignore[attr-defined]
        self._structures: List[object] = []

    def register(self, callback: ctypes._CFuncPtr) -> ctypes._CFuncPtr:  # type: ignore[attr-defined]
        self._callbacks.append(callback)
        return callback

    def keep(self, obj: object) -> object:
        self._structures.append(obj)
        return obj


# ---------------------------------------------------------------------------
# C structure translations (client)
# ---------------------------------------------------------------------------


class _QlrCvarShadow(ctypes.Structure):
    _fields_ = [
        ("integer", ctypes.c_int),
        ("value", ctypes.c_float),
        ("string", ctypes.c_char_p),
    ]


class _QlrClientStaticShadow(ctypes.Structure):
    _fields_ = [
        ("rendererStarted", ctypes.c_bool),
        ("soundStarted", ctypes.c_bool),
        ("soundRegistered", ctypes.c_bool),
        ("uiStarted", ctypes.c_bool),
        ("cddialog", ctypes.c_bool),
        ("state", ctypes.c_int),
        ("keyCatchers", ctypes.c_int),
        ("realtime", ctypes.c_int),
        ("frametime", ctypes.c_int),
        ("realFrametime", ctypes.c_int),
    ]


class _QlrClSnapshot(ctypes.Structure):
    _fields_ = [
        ("valid", ctypes.c_int32),
        ("snapFlags", ctypes.c_int32),
        ("serverTime", ctypes.c_int32),
        ("messageNum", ctypes.c_int32),
        ("deltaNum", ctypes.c_int32),
        ("ping", ctypes.c_int32),
        ("areamask", ctypes.c_uint8 * 32),
        ("cmdNum", ctypes.c_int32),
        ("playerState", ctypes.c_uint8 * 0x16C),
        ("numEntities", ctypes.c_int32),
        ("parseEntitiesNum", ctypes.c_int32),
        ("serverCommandNum", ctypes.c_int32),
    ]


class _QlrClientTimingWindow(ctypes.Structure):
    _fields_ = [
        ("latest", _QlrClSnapshot),
        ("serverTime", ctypes.c_int32),
        ("oldServerTime", ctypes.c_int32),
        ("oldFrameServerTime", ctypes.c_int32),
        ("serverTimeDelta", ctypes.c_int32),
        ("extrapolatedSnapshot", ctypes.c_int32),
        ("newSnapshots", ctypes.c_int32),
    ]


class _QlrClientActiveShadow(ctypes.Structure):
    _fields_ = [
        ("timeoutcount", ctypes.c_int),
        ("timing", _QlrClientTimingWindow),
    ]


class _QlrClientConnectionShadow(ctypes.Structure):
    _fields_ = [
        ("demorecording", ctypes.c_bool),
        ("demowaiting", ctypes.c_bool),
        ("demoplaying", ctypes.c_bool),
        ("firstDemoFrameSkipped", ctypes.c_bool),
        ("serverMessageSequence", ctypes.c_int),
        ("lastPacketTime", ctypes.c_int),
        ("timeDemoBaseTime", ctypes.c_int),
        ("timeDemoFrames", ctypes.c_int),
        ("timeDemoStart", ctypes.c_int),
        ("netchanSequence", ctypes.c_int),
    ]


_ClientVoidHook = ctypes.CFUNCTYPE(None)
_ClientMenuHook = ctypes.CFUNCTYPE(None, ctypes.c_int)
_ClientTimeoutHook = ctypes.CFUNCTYPE(
    None,
    ctypes.POINTER(_QlrClientConnectionShadow),
    ctypes.POINTER(_QlrClientStaticShadow),
    ctypes.POINTER(_QlrClientActiveShadow),
)


class _QlrClientFrameCvars(ctypes.Structure):
    _fields_ = [
        ("com_cl_running", ctypes.POINTER(_QlrCvarShadow)),
        ("cl_avidemo", ctypes.POINTER(_QlrCvarShadow)),
        ("cl_forceavidemo", ctypes.POINTER(_QlrCvarShadow)),
        ("com_timescale", ctypes.POINTER(_QlrCvarShadow)),
        ("cl_timeNudge", ctypes.POINTER(_QlrCvarShadow)),
        ("cl_paused", ctypes.POINTER(_QlrCvarShadow)),
        ("sv_paused", ctypes.POINTER(_QlrCvarShadow)),
        ("com_sv_running", ctypes.POINTER(_QlrCvarShadow)),
        ("cl_timedemo", ctypes.POINTER(_QlrCvarShadow)),
        ("cl_showTimeDelta", ctypes.POINTER(_QlrCvarShadow)),
        ("cl_freezeDemo", ctypes.POINTER(_QlrCvarShadow)),
        ("cl_activeAction", ctypes.POINTER(_QlrCvarShadow)),
    ]


class _QlrClientFrameHooks(ctypes.Structure):
    _fields_ = [
        ("stopAllSounds", _ClientVoidHook),
        ("setActiveMenu", _ClientMenuHook),
        ("writeDemoMessage", _ClientVoidHook),
        ("checkTimeout", _ClientTimeoutHook),
        ("checkUserinfo", _ClientVoidHook),
        ("readPackets", _ClientVoidHook),
        ("sendCmd", _ClientVoidHook),
        ("predictMovement", _ClientVoidHook),
        ("runConsole", _ClientVoidHook),
        ("updateScreen", _ClientVoidHook),
        ("soundUpdate", _ClientVoidHook),
        ("setCGameTime", _ClientVoidHook),
        ("firstSnapshot", _ClientVoidHook),
        ("beginProfiling", _ClientVoidHook),
    ]


class _QlrClientFrameContext(ctypes.Structure):
    _fields_ = [
        ("cls", ctypes.POINTER(_QlrClientStaticShadow)),
        ("cl", ctypes.POINTER(_QlrClientActiveShadow)),
        ("clc", ctypes.POINTER(_QlrClientConnectionShadow)),
        ("cvars", _QlrClientFrameCvars),
        ("hooks", _QlrClientFrameHooks),
    ]


# ---------------------------------------------------------------------------
# C structure translations (game)
# ---------------------------------------------------------------------------


class _QlrGEntity(ctypes.Structure):
    pass


_EntityHook = ctypes.CFUNCTYPE(None, ctypes.POINTER(_QlrGEntity))
_ThinkHook = ctypes.CFUNCTYPE(None, ctypes.POINTER(_QlrGEntity))
_RunThinksHook = ctypes.CFUNCTYPE(None, ctypes.c_int)
_GameVoidHook = ctypes.CFUNCTYPE(None)


class _QlrGEntity(ctypes.Structure):
    _fields_ = [
        ("inuse", ctypes.c_bool),
        ("next", ctypes.POINTER(_QlrGEntity)),
        ("client", ctypes.c_void_p),
        ("think", _ThinkHook),
        ("nextthink", ctypes.c_int),
        ("eventTime", ctypes.c_int),
    ]


class _QlrLevelLocals(ctypes.Structure):
    _fields_ = [
        ("time", ctypes.c_int),
        ("previousTime", ctypes.c_int),
        ("framenum", ctypes.c_int),
        ("startTime", ctypes.c_int),
        ("msec", ctypes.c_int),
        ("num_entities", ctypes.c_int),
        ("maxclients", ctypes.c_int),
        ("warmupTime", ctypes.c_int),
        ("intermissionQueued", ctypes.c_int),
        ("firstEntity", ctypes.POINTER(_QlrGEntity)),
    ]


class _QlrGameFrameHooks(ctypes.Structure):
    _fields_ = [
        ("run_scheduled_thinks", _RunThinksHook),
        ("physics_step", _EntityHook),
        ("client_think", _EntityHook),
        ("fire_event", _EntityHook),
        ("client_end_frame", _EntityHook),
        ("begin_match", _GameVoidHook),
        ("begin_intermission", _GameVoidHook),
    ]


class _QlrGameFrameContext(ctypes.Structure):
    _fields_ = [
        ("level", ctypes.POINTER(_QlrLevelLocals)),
        ("entities", ctypes.POINTER(_QlrGEntity)),
        ("entity_count", ctypes.c_size_t),
        ("hooks", _QlrGameFrameHooks),
    ]


# ---------------------------------------------------------------------------
# Harness implementation
# ---------------------------------------------------------------------------


def _load_library(build_root: Path, name: str) -> ctypes.CDLL:
    ext = '.dll' if os.name == 'nt' else '.so'
    path = build_root / f"{name}{ext}"
    if not path.exists():
        raise FileNotFoundError(f"Clean-room library missing: {path}")
    return ctypes.CDLL(str(path))


def _initialise_client_context(registry: _CallbackRegistry) -> _QlrClientFrameContext:
    cls = _QlrClientStaticShadow(
        rendererStarted=True,
        soundStarted=True,
        soundRegistered=True,
        uiStarted=True,
        cddialog=True,
        state=5,
        keyCatchers=0,
        realtime=1234,
        frametime=0,
        realFrametime=0,
    )
    cl = _QlrClientActiveShadow()
    cl.timing.serverTime = 100
    cl.timing.oldServerTime = 90
    cl.timeoutcount = 2

    clc = _QlrClientConnectionShadow()
    clc.lastPacketTime = 77

    def _cvar(integer: int, value: float) -> _QlrCvarShadow:
        return registry.keep(_QlrCvarShadow(integer=integer, value=value, string=None))  # type: ignore[arg-type]

    com_cl_running = _cvar(1, 1.0)
    cl_avidemo = _cvar(30, 30.0)
    cl_forceavidemo = _cvar(0, 0.0)
    com_timescale = _cvar(1, 1.0)
    cl_paused = _cvar(1, 1.0)
    sv_paused = _cvar(1, 1.0)
    com_sv_running = _cvar(1, 1.0)
    cl_timedemo = _cvar(1, 1.0)
    cl_showTimeDelta = _cvar(0, 0.0)
    cl_freezeDemo = _cvar(0, 0.0)
    cl_activeAction = _cvar(0, 0.0)
    cl_timeNudge = _cvar(-30, -30.0)

    hooks_called: List[str] = []

    @registry.register
    @_ClientVoidHook
    def _void_hook() -> None:
        hooks_called.append('void')

    @registry.register
    @_ClientMenuHook
    def _menu_hook(menu_id: int) -> None:
        hooks_called.append(f"menu:{menu_id}")

    @registry.register
    @_ClientTimeoutHook
    def _timeout_hook(clc_ptr, cls_ptr, cl_ptr) -> None:
        hooks_called.append('timeout')
        if cl_ptr:
            cl_ptr.contents.timeoutcount += 1

    @registry.register
    @_ClientVoidHook
    def _sound_hook() -> None:
        hooks_called.append('sound')

    hooks = _QlrClientFrameHooks(
        stopAllSounds=_void_hook,
        setActiveMenu=_menu_hook,
        writeDemoMessage=_void_hook,
        checkTimeout=_timeout_hook,
        checkUserinfo=_void_hook,
        readPackets=_void_hook,
        sendCmd=_void_hook,
        predictMovement=_void_hook,
        runConsole=_void_hook,
        updateScreen=_void_hook,
        soundUpdate=_sound_hook,
        setCGameTime=_void_hook,
        firstSnapshot=_void_hook,
        beginProfiling=_void_hook,
    )

    context = _QlrClientFrameContext()
    context.cls = ctypes.pointer(registry.keep(cls))  # type: ignore[arg-type]
    context.cl = ctypes.pointer(registry.keep(cl))  # type: ignore[arg-type]
    context.clc = ctypes.pointer(registry.keep(clc))  # type: ignore[arg-type]
    context.cvars = _QlrClientFrameCvars(
        com_cl_running=ctypes.pointer(com_cl_running),
        cl_avidemo=ctypes.pointer(cl_avidemo),
        cl_forceavidemo=ctypes.pointer(cl_forceavidemo),
        com_timescale=ctypes.pointer(com_timescale),
        cl_timeNudge=ctypes.pointer(cl_timeNudge),
        cl_paused=ctypes.pointer(cl_paused),
        sv_paused=ctypes.pointer(sv_paused),
        com_sv_running=ctypes.pointer(com_sv_running),
        cl_timedemo=ctypes.pointer(cl_timedemo),
        cl_showTimeDelta=ctypes.pointer(cl_showTimeDelta),
        cl_freezeDemo=ctypes.pointer(cl_freezeDemo),
        cl_activeAction=ctypes.pointer(cl_activeAction),
    )
    context.hooks = hooks
    registry.keep(context)
    return context


def _initialise_game_context(registry: _CallbackRegistry) -> _QlrGameFrameContext:
    level = _QlrLevelLocals(
        time=64,
        previousTime=32,
        framenum=10,
        startTime=0,
        msec=0,
        num_entities=2,
        maxclients=2,
        warmupTime=96,
        intermissionQueued=128,
    )

    entities = registry.keep((_QlrGEntity * 2)())  # type: ignore[arg-type]

    @registry.register
    @_ThinkHook
    def _think(entity_ptr) -> None:
        entity_ptr.contents.nextthink = 0

    @registry.register
    @_EntityHook
    def _entity_hook(entity_ptr) -> None:
        entity_ptr.contents.eventTime = level.time

    @registry.register
    @_RunThinksHook
    def _run_thinks(msec: int) -> None:
        level.msec = msec

    @registry.register
    @_GameVoidHook
    def _void_game_hook() -> None:
        return

    entities[0].inuse = True
    entities[0].think = _think
    entities[0].nextthink = 64
    entities[0].eventTime = 64

    entities[1].inuse = True
    entities[1].eventTime = 96

    level.firstEntity = ctypes.pointer(entities[0])

    hooks = _QlrGameFrameHooks(
        run_scheduled_thinks=_run_thinks,
        physics_step=_entity_hook,
        client_think=_entity_hook,
        fire_event=_entity_hook,
        client_end_frame=_entity_hook,
        begin_match=_void_game_hook,
        begin_intermission=_void_game_hook,
    )

    context = _QlrGameFrameContext()
    context.level = ctypes.pointer(registry.keep(level))  # type: ignore[arg-type]
    context.entities = ctypes.cast(entities, ctypes.POINTER(_QlrGEntity))
    context.entity_count = len(entities)
    context.hooks = hooks
    return context


def _write_diff(expectation: Path, observed: Path, destination: Path) -> bool:
    expected_text = expectation.read_text(encoding='utf-8').splitlines()
    observed_text = observed.read_text(encoding='utf-8').splitlines()
    diff_lines = list(
        difflib.unified_diff(expected_text, observed_text, fromfile='expected', tofile='observed', lineterm='')
    )
    destination.parent.mkdir(parents=True, exist_ok=True)
    if diff_lines:
        destination.write_text("\n".join(diff_lines) + "\n", encoding='utf-8')
        return False
    destination.write_text("No differences detected.\n", encoding='utf-8')
    return True


_PTR_RE = re.compile(r"0x[0-9A-Fa-f]+")


def _normalise_log(text: str) -> str:
    return _PTR_RE.sub("0xPTR", text)


def run_trace_harness(build_root: Path, expectation: Path, artifact_dir: Path) -> TraceHarnessResult:
    """Execute the trace harness using the clean-room binaries."""

    build_root = build_root.resolve()
    artifact_dir = artifact_dir.resolve()
    expectation = expectation.resolve()

    client_lib = _load_library(build_root, 'qlr_client_frame')
    game_lib = _load_library(build_root, 'qlr_game_frame')

    registry = _CallbackRegistry()
    client_ctx = _initialise_client_context(registry)
    game_ctx = _initialise_game_context(registry)

    log_path = LOG_PATH.resolve()
    log_path.parent.mkdir(parents=True, exist_ok=True)
    if log_path.exists():
        log_path.unlink()

    client_lib.qlr_native_shim_reset_log()
    game_lib.qlr_native_shim_reset_log()
    client_lib.QLR_ClientFrame_BindContext(ctypes.byref(client_ctx))
    client_lib.CL_Frame(16)
    client_lib.QLR_ClientFrame_UnbindContext()

    game_lib.QLR_Game_BindFrameContext(ctypes.byref(game_ctx))
    game_lib.G_RunFrame(160)
    game_lib.QLR_Game_UnbindFrameContext()

    client_lib.qlr_native_shim_flush()
    game_lib.qlr_native_shim_flush()
    client_lib.qlr_native_shim_close()
    game_lib.qlr_native_shim_close()

    if not log_path.exists():
        raise FileNotFoundError(f"Trace log was not generated: {log_path}")

    artifact_dir.mkdir(parents=True, exist_ok=True)
    raw_log = log_path.read_text(encoding='utf-8')
    (artifact_dir / 'native-shim.raw.log').write_text(raw_log, encoding='utf-8')
    normalised_log = _normalise_log(raw_log)
    log_artifact = artifact_dir / 'native-shim.log'
    log_artifact.write_text(normalised_log, encoding='utf-8')

    diff_artifact = artifact_dir / 'native-shim.diff'
    matches = _write_diff(expectation, log_artifact, diff_artifact)

    return TraceHarnessResult(log_path=log_artifact, diff_path=diff_artifact, matches_expectation=matches)
