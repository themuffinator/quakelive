"""Filesystem search path regression tests for FS_FOpenFileRead."""
from __future__ import annotations

import ctypes
import zipfile
from pathlib import Path
from typing import Iterator, Tuple

import pytest

from tests.compiler_support import compile_c_binary, find_c_compiler, shared_library_name

REPO_ROOT = Path(__file__).resolve().parent.parent


@pytest.fixture(scope="session")
def fs_harness(tmp_path_factory: pytest.TempPathFactory) -> ctypes.CDLL:
	build_dir = tmp_path_factory.mktemp("fs_harness_build")
	lib_path = build_dir / shared_library_name("fs_harness")
	compiler = find_c_compiler()

	if compiler is None:
		pytest.skip("no supported C compiler is available for the filesystem search-path harness")

	compile_c_binary(
		compiler,
		[
			REPO_ROOT / "tests" / "fs_searchpath_harness.c",
			REPO_ROOT / "src" / "code" / "qcommon" / "unzip.c",
		],
		lib_path,
		include_dirs=[
			REPO_ROOT / "src" / "code",
			REPO_ROOT / "src" / "code" / "qcommon",
			REPO_ROOT / "src" / "code" / "game",
			REPO_ROOT / "src" / "code" / "client",
			REPO_ROOT / "src" / "code" / "server",
			REPO_ROOT / "src" / "code" / "botlib",
		],
		defines=[
			"QL_BUILD_ONLINE_SERVICES=1",
			"QL_BUILD_STEAMWORKS=1",
		],
		shared=True,
		workdir=REPO_ROOT,
	)

	lib = ctypes.CDLL(str(lib_path))
	lib.QLR_FS_TestInitCvars.argtypes = [ctypes.c_char_p, ctypes.c_char_p]
	lib.QLR_FS_TestShutdown.argtypes = []
	lib.QLR_FS_TestSetSteamUserId.argtypes = [ctypes.c_int, ctypes.c_uint32, ctypes.c_uint32]
	lib.QLR_FS_TestResolveHomePath.argtypes = [ctypes.c_char_p]
	lib.QLR_FS_TestResolveHomePath.restype = ctypes.c_char_p
	lib.QLR_FS_TestSetWebPath.argtypes = [ctypes.c_char_p]
	lib.QLR_FS_TestSetFallbackMappings.argtypes = [ctypes.c_char_p]
	lib.QLR_FS_TestRewriteWebPath.argtypes = [ctypes.c_char_p, ctypes.c_char_p, ctypes.c_size_t]
	lib.QLR_FS_TestRewriteWebPath.restype = ctypes.c_int
	lib.QLR_FS_TestOpenWebFileRead.argtypes = [
		ctypes.c_char_p,
		ctypes.c_char_p,
		ctypes.c_size_t,
		ctypes.c_char_p,
		ctypes.c_size_t,
	]
	lib.QLR_FS_TestOpenWebFileRead.restype = ctypes.c_int
	lib.QLR_FS_TestAddGameDirectory.argtypes = [ctypes.c_char_p, ctypes.c_char_p]
	lib.QLR_FS_TestSetRestrict.argtypes = [ctypes.c_int]
	lib.QLR_FS_TestSetDebug.argtypes = [ctypes.c_int]
	lib.QLR_FS_TestLoadedPakNames.argtypes = []
	lib.QLR_FS_TestLoadedPakNames.restype = ctypes.c_char_p
	lib.QLR_FS_TestClearCapturedLog.argtypes = []
	lib.QLR_FS_TestCapturedLog.argtypes = []
	lib.QLR_FS_TestCapturedLog.restype = ctypes.c_char_p
	lib.QLR_FS_TestReadFile.argtypes = [
		ctypes.c_char_p,
		ctypes.c_int,
		ctypes.c_char_p,
		ctypes.c_size_t,
		ctypes.POINTER(ctypes.c_size_t),
	]
	lib.QLR_FS_TestReadFile.restype = ctypes.c_int
	return lib


@pytest.fixture()
def fs_environment(tmp_path: Path, fs_harness: ctypes.CDLL) -> Iterator[Tuple[ctypes.CDLL, Path, Path]]:
    basepath = tmp_path / "base"
    homepath = tmp_path / "home"
    (basepath / "baseq3").mkdir(parents=True)
    (homepath / "baseq3").mkdir(parents=True)

    fs_harness.QLR_FS_TestInitCvars(
        str(basepath).encode(), str(homepath).encode()
    )
    fs_harness.QLR_FS_TestSetRestrict(0)
    yield fs_harness, basepath, homepath
    fs_harness.QLR_FS_TestShutdown()


def _write_pk3(root: Path, relative: str, content: str) -> None:
    pak_path = root / "baseq3" / "pak_test.pk3"
    with zipfile.ZipFile(pak_path, "w") as archive:
        archive.writestr(relative, content)


def _write_named_pk3(root: Path, pak_name: str, relative: str, content: str) -> None:
    pak_path = root / "baseq3" / pak_name
    with zipfile.ZipFile(pak_path, "w") as archive:
        archive.writestr(relative, content)


def _write_dir(root: Path, relative: str, content: str) -> Path:
    dest = root / "baseq3" / relative
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_text(content, encoding="utf-8")
    return dest


def _read_file(
    lib: ctypes.CDLL, filename: str, unique: bool = False
) -> Tuple[int, str, int]:
    buffer = ctypes.create_string_buffer(256)
    handle = ctypes.c_size_t()
    length = lib.QLR_FS_TestReadFile(
        filename.encode(), int(unique), buffer, ctypes.sizeof(buffer), ctypes.byref(handle)
    )
    return length, buffer.value.decode(), handle.value


def _split_u64(value: int) -> Tuple[int, int]:
    return value & 0xFFFFFFFF, (value >> 32) & 0xFFFFFFFF


def test_homepath_resolution_defaults_to_basepath_without_steam_user(
    fs_environment: Tuple[ctypes.CDLL, Path, Path],
) -> None:
    lib, basepath, _ = fs_environment

    lib.QLR_FS_TestSetSteamUserId(0, 0, 0)

    resolved = lib.QLR_FS_TestResolveHomePath(str(basepath).encode()).decode()

    assert resolved == str(basepath)


def test_homepath_resolution_appends_retail_steamid_suffix_when_available(
    fs_environment: Tuple[ctypes.CDLL, Path, Path],
) -> None:
    lib, basepath, _ = fs_environment
    steam_id = 76561198012345678
    steam_id_low, steam_id_high = _split_u64(steam_id)

    lib.QLR_FS_TestSetSteamUserId(1, steam_id_low, steam_id_high)

    resolved = lib.QLR_FS_TestResolveHomePath(str(basepath).encode()).decode()

    assert resolved == f"{basepath}/{steam_id}"


def test_rewrite_web_path_prefixes_fs_webpath_and_preserves_screenshot_relative_path(
    fs_environment: Tuple[ctypes.CDLL, Path, Path],
) -> None:
    lib, basepath, _ = fs_environment
    webroot = basepath.parent / "webroot"
    rewritten = ctypes.create_string_buffer(512)

    lib.QLR_FS_TestSetWebPath(str(webroot).encode())

    assert lib.QLR_FS_TestRewriteWebPath(
        b"https://cdn.quakelive.com/assets/menu.txt", rewritten, ctypes.sizeof(rewritten)
    )
    assert rewritten.value.decode() == f"{webroot}/assets/menu.txt"

    assert lib.QLR_FS_TestRewriteWebPath(
        b"https://cdn.quakelive.com/screenshots/finals/match.jpg", rewritten, ctypes.sizeof(rewritten)
    )
    assert rewritten.value.decode() == "screenshots/finals/match.jpg"


def test_web_fallback_reads_mapped_fs_webpath_content_and_reports_resolution(
    fs_environment: Tuple[ctypes.CDLL, Path, Path],
) -> None:
    lib, basepath, _ = fs_environment
    webroot = basepath.parent / "webroot"
    resolved = ctypes.create_string_buffer(512)
    buffer = ctypes.create_string_buffer(256)

    _write_dir(webroot, "web/news/today.json", "web-fallback")

    lib.QLR_FS_TestSetWebPath(str(webroot).encode())
    lib.QLR_FS_TestSetFallbackMappings(b"https://cdn.quakelive.com/=web")
    lib.QLR_FS_TestAddGameDirectory(str(basepath).encode(), b"baseq3")
    lib.QLR_FS_TestClearCapturedLog()

    length = lib.QLR_FS_TestOpenWebFileRead(
        b"https://cdn.quakelive.com/news/today.json",
        resolved,
        ctypes.sizeof(resolved),
        buffer,
        ctypes.sizeof(buffer),
    )
    captured = lib.QLR_FS_TestCapturedLog().decode()

    assert length == len("web-fallback")
    assert buffer.value.decode() == "web-fallback"
    assert resolved.value.decode() == "web/news/today.json"
    assert "web-fallback: https://cdn.quakelive.com/news/today.json -> web/news/today.json (fs_webpath)" in captured


def test_web_fallback_routes_screenshot_requests_through_homepath(
    fs_environment: Tuple[ctypes.CDLL, Path, Path],
) -> None:
    lib, basepath, homepath = fs_environment
    webroot = basepath.parent / "webroot"
    resolved = ctypes.create_string_buffer(512)
    buffer = ctypes.create_string_buffer(256)

    _write_dir(homepath, "screenshots/finals/match.jpg", "home-shot")

    lib.QLR_FS_TestSetWebPath(str(webroot).encode())
    lib.QLR_FS_TestSetFallbackMappings(
        b"https://cdn.quakelive.com/=web;quakelive://screenshots/=home:screenshots"
    )
    lib.QLR_FS_TestAddGameDirectory(str(basepath).encode(), b"baseq3")
    lib.QLR_FS_TestClearCapturedLog()

    length = lib.QLR_FS_TestOpenWebFileRead(
        b"quakelive://screenshots/finals/match.jpg",
        resolved,
        ctypes.sizeof(resolved),
        buffer,
        ctypes.sizeof(buffer),
    )
    captured = lib.QLR_FS_TestCapturedLog().decode()

    assert length == len("home-shot")
    assert buffer.value.decode() == "home-shot"
    assert resolved.value.decode() == "screenshots/finals/match.jpg"
    assert "web-fallback: quakelive://screenshots/finals/match.jpg -> screenshots/finals/match.jpg (fs_homepath)" in captured


def test_pk3_precedence_over_directory(fs_environment: Tuple[ctypes.CDLL, Path, Path]) -> None:
    lib, basepath, _ = fs_environment

    _write_dir(basepath, "ui/test.menu", "directory-version")
    _write_pk3(basepath, "ui/test.menu", "pak-version")

    lib.QLR_FS_TestAddGameDirectory(str(basepath).encode(), b"baseq3")

    length, content, _ = _read_file(lib, "ui/test.menu")

    assert length == len("pak-version")
    assert content == "pak-version"


def test_restrict_mode_prefers_pak_and_skips_directory(
    fs_environment: Tuple[ctypes.CDLL, Path, Path]
) -> None:
    lib, basepath, _ = fs_environment

    _write_dir(basepath, "ui/restrict.menu", "from-directory")
    _write_pk3(basepath, "ui/restrict.menu", "from-pak")

    lib.QLR_FS_TestSetRestrict(1)
    lib.QLR_FS_TestAddGameDirectory(str(basepath).encode(), b"baseq3")

    length, content, _ = _read_file(lib, "ui/restrict.menu")

    assert length == len("from-pak")
    assert content == "from-pak"


def test_unique_file_reopens_zip_handle(fs_environment: Tuple[ctypes.CDLL, Path, Path]) -> None:
    lib, basepath, _ = fs_environment

    _write_pk3(basepath, "ui/unique.menu", "unique")
    lib.QLR_FS_TestAddGameDirectory(str(basepath).encode(), b"baseq3")

    first_len, first_content, shared_handle = _read_file(lib, "ui/unique.menu", unique=False)
    second_len, second_content, unique_handle = _read_file(lib, "ui/unique.menu", unique=True)

    assert first_len == len("unique")
    assert second_len == len("unique")
    assert first_content == "unique"
    assert second_content == "unique"
    assert shared_handle != 0
    assert unique_handle != 0
    assert shared_handle != unique_handle


def test_homepath_overlay_pk3_precedes_lower_priority_base_pk3_and_logs_source(
    fs_environment: Tuple[ctypes.CDLL, Path, Path],
) -> None:
    lib, basepath, homepath = fs_environment

    _write_named_pk3(basepath, "pak00.pk3", "ui/hud.txt", "base-bundle")
    _write_named_pk3(homepath, "overlay.pk3", "ui/hud.txt", "overlay-bundle")

    lib.QLR_FS_TestSetDebug(1)
    lib.QLR_FS_TestAddGameDirectory(str(basepath).encode(), b"baseq3")
    lib.QLR_FS_TestAddGameDirectory(str(homepath).encode(), b"baseq3")

    loaded_paks = lib.QLR_FS_TestLoadedPakNames().decode()
    assert loaded_paks.split()[:2] == ["overlay", "pak00"]

    lib.QLR_FS_TestClearCapturedLog()
    length, content, _ = _read_file(lib, "ui/hud.txt")
    captured = lib.QLR_FS_TestCapturedLog().decode()

    assert length == len("overlay-bundle")
    assert content == "overlay-bundle"
    assert "FS_FOpenFileRead: ui/hud.txt" in captured
    assert str(homepath / "baseq3" / "overlay.pk3") in captured

