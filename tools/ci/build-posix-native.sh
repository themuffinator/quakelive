#!/usr/bin/env bash
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
UNIX_MAKE_DIR="${REPO_ROOT}/src/code/unix"

HOST_SYSTEM="${QL_POSIX_PLATFORM:-$(uname -s | tr '[:upper:]' '[:lower:]')}"
case "${HOST_SYSTEM}" in
	linux*)
		PLATFORM_NAME="linux"
		MAKE_PLATFORM="linux"
		SHLIB_EXT="so"
		SHLIB_LDFLAGS_DEFAULT="-shared"
		HOST_LDFLAGS_DEFAULT="-ldl -lm"
		HOST_CFLAGS_DEFAULT=""
		;;
	darwin*|macos*)
		PLATFORM_NAME="macos"
		MAKE_PLATFORM="darwin"
		SHLIB_EXT="dylib"
		SHLIB_LDFLAGS_DEFAULT="-dynamiclib -Wl,-undefined,dynamic_lookup"
		HOST_LDFLAGS_DEFAULT="-lm"
		HOST_CFLAGS_DEFAULT="-DMACOS_X"
		;;
	*)
		echo "Unsupported native POSIX build host: ${HOST_SYSTEM}" >&2
		exit 1
		;;
esac

BUILD_ROOT="${QL_POSIX_BUILD_ROOT:-${BUILD_ROOT:-${REPO_ROOT}/build/posix/${PLATFORM_NAME}}}"
[[ "${BUILD_ROOT}" = /* ]] || BUILD_ROOT="${REPO_ROOT}/${BUILD_ROOT}"

HOST_ARCH_RAW="${QL_POSIX_ARCH:-$(uname -m | tr '-' '_')}"
case "${HOST_ARCH_RAW}" in
	aarch64)
		HOST_ARCH="arm64"
		;;
	amd64)
		HOST_ARCH="x86_64"
		;;
	*)
		HOST_ARCH="${HOST_ARCH_RAW}"
		;;
esac
CC="${QL_POSIX_CC:-${CC:-cc}}"
CXX="${QL_POSIX_CXX:-${CXX:-c++}}"
MAKE_JOBS="${QL_POSIX_MAKE_JOBS:-2}"
EXTRA_CFLAGS="${QL_POSIX_EXTRA_CFLAGS:-}"
CFLAGS_DEFAULT="-std=gnu99 -O2 -DNDEBUG -fPIC -fcommon -fsigned-char -include stdint.h -I${REPO_ROOT}/src/code -I${REPO_ROOT}/src/game -I${REPO_ROOT}/src ${HOST_CFLAGS_DEFAULT}"
CFLAGS="${QL_POSIX_CFLAGS:-${CFLAGS:-${CFLAGS_DEFAULT} ${EXTRA_CFLAGS}}}"
SHLIB_LDFLAGS="${QL_POSIX_SHLIB_LDFLAGS:-${SHLIB_LDFLAGS_DEFAULT}}"
HOST_LDFLAGS="${QL_POSIX_LDFLAGS:-${LDFLAGS:-${HOST_LDFLAGS_DEFAULT}}}"

if ! command -v "${CC%% *}" >/dev/null 2>&1; then
	echo "Compiler '${CC}' not found in PATH" >&2
	exit 1
fi

if ! command -v make >/dev/null 2>&1; then
	echo "GNU make is required for the native POSIX build" >&2
	exit 1
fi

mkdir -p "${BUILD_ROOT}"

COMMON_MODULE_SOURCES=(
	"${REPO_ROOT}/src/code/game/bg_lib.c"
	"${REPO_ROOT}/src/code/game/bg_misc.c"
	"${REPO_ROOT}/src/code/game/bg_pmove.c"
	"${REPO_ROOT}/src/code/game/bg_slidemove.c"
	"${REPO_ROOT}/src/code/game/q_math.c"
	"${REPO_ROOT}/src/code/game/q_shared.c"
)

CGAME_SOURCES=(
	"${COMMON_MODULE_SOURCES[@]}"
	"${REPO_ROOT}/src/code/ui/ui_shared.c"
	"${REPO_ROOT}/src/code/cgame/cg_consolecmds.c"
	"${REPO_ROOT}/src/code/cgame/cg_draw.c"
	"${REPO_ROOT}/src/code/cgame/cg_drawtools.c"
	"${REPO_ROOT}/src/code/cgame/cg_effects.c"
	"${REPO_ROOT}/src/code/cgame/cg_ents.c"
	"${REPO_ROOT}/src/code/cgame/cg_event.c"
	"${REPO_ROOT}/src/code/cgame/cg_info.c"
	"${REPO_ROOT}/src/code/cgame/cg_localents.c"
	"${REPO_ROOT}/src/code/cgame/cg_main.c"
	"${REPO_ROOT}/src/code/cgame/cg_newdraw.c"
	"${REPO_ROOT}/src/code/cgame/cg_marks.c"
	"${REPO_ROOT}/src/code/cgame/cg_particles.c"
	"${REPO_ROOT}/src/code/cgame/cg_players.c"
	"${REPO_ROOT}/src/code/cgame/cg_playerstate.c"
	"${REPO_ROOT}/src/code/cgame/cg_predict.c"
	"${REPO_ROOT}/src/code/cgame/cg_screen.c"
	"${REPO_ROOT}/src/code/cgame/cg_scoreboard.c"
	"${REPO_ROOT}/src/code/cgame/cg_servercmds.c"
	"${REPO_ROOT}/src/code/cgame/cg_snapshot.c"
	"${REPO_ROOT}/src/code/cgame/cg_syscalls.c"
	"${REPO_ROOT}/src/code/cgame/cg_view.c"
	"${REPO_ROOT}/src/code/cgame/cg_weapons.c"
)

QAGAME_SOURCES=(
	"${REPO_ROOT}/src/code/game/ai_chat.c"
	"${REPO_ROOT}/src/code/game/ai_cmd.c"
	"${REPO_ROOT}/src/code/game/ai_dmnet.c"
	"${REPO_ROOT}/src/code/game/ai_dmq3.c"
	"${REPO_ROOT}/src/code/game/ai_main.c"
	"${REPO_ROOT}/src/code/game/ai_team.c"
	"${REPO_ROOT}/src/code/game/ai_vcmd.c"
	"${COMMON_MODULE_SOURCES[@]}"
	"${REPO_ROOT}/src/code/game/g_autoshuffle.c"
	"${REPO_ROOT}/src/code/game/g_active.c"
	"${REPO_ROOT}/src/code/game/g_arenas.c"
	"${REPO_ROOT}/src/code/game/g_bot.c"
	"${REPO_ROOT}/src/code/game/g_client.c"
	"${REPO_ROOT}/src/code/game/g_cmds.c"
	"${REPO_ROOT}/src/code/game/g_combat.c"
	"${REPO_ROOT}/src/code/game/g_items.c"
	"${REPO_ROOT}/src/code/game/g_main.c"
	"${REPO_ROOT}/src/code/game/g_match_state.c"
	"${REPO_ROOT}/src/code/game/g_mem.c"
	"${REPO_ROOT}/src/code/game/g_entity.c"
	"${REPO_ROOT}/src/code/game/g_misc.c"
	"${REPO_ROOT}/src/code/game/g_missile.c"
	"${REPO_ROOT}/src/code/game/g_mover.c"
	"${REPO_ROOT}/src/code/game/g_session.c"
	"${REPO_ROOT}/src/code/game/g_spawn.c"
	"${REPO_ROOT}/src/code/game/g_svcmds.c"
	"${REPO_ROOT}/src/code/game/g_syscalls.c"
	"${REPO_ROOT}/src/code/game/g_target.c"
	"${REPO_ROOT}/src/code/game/g_team.c"
	"${REPO_ROOT}/src/code/game/g_trigger.c"
	"${REPO_ROOT}/src/code/game/g_utils.c"
	"${REPO_ROOT}/src/code/game/g_factory.c"
	"${REPO_ROOT}/src/code/game/g_freeze.c"
	"${REPO_ROOT}/src/code/game/g_race.c"
	"${REPO_ROOT}/src/code/game/g_pmove.c"
	"${REPO_ROOT}/src/code/game/g_vote.c"
	"${REPO_ROOT}/src/common/platform/backends/platform_backend_open_steam.c"
	"${REPO_ROOT}/src/common/auth_credentials.c"
	"${REPO_ROOT}/src/game/g_config.c"
	"${REPO_ROOT}/src/game/g_match_config.c"
	"${REPO_ROOT}/src/code/game/g_weapon.c"
)

UI_SOURCES=(
	"${REPO_ROOT}/src/code/game/bg_lib.c"
	"${REPO_ROOT}/src/code/game/bg_misc.c"
	"${REPO_ROOT}/src/code/game/q_math.c"
	"${REPO_ROOT}/src/code/game/q_shared.c"
	"${REPO_ROOT}/src/code/ui/ui_atoms.c"
	"${REPO_ROOT}/src/code/ui/ui_cdkey.c"
	"${REPO_ROOT}/src/code/ui/ui_gameinfo.c"
	"${REPO_ROOT}/src/code/ui/ui_main.c"
	"${REPO_ROOT}/src/code/ui/ui_players.c"
	"${REPO_ROOT}/src/code/ui/ui_shared.c"
	"${REPO_ROOT}/src/code/ui/ui_syscalls.c"
	"${REPO_ROOT}/src/code/ui/ui_util.c"
)

MODULE_TARGETS=(
	"${BUILD_ROOT}/baseq3/cgame${HOST_ARCH}.${SHLIB_EXT}"
	"${BUILD_ROOT}/baseq3/qagame${HOST_ARCH}.${SHLIB_EXT}"
	"${BUILD_ROOT}/baseq3/ui${HOST_ARCH}.${SHLIB_EXT}"
)

HOST_TARGETS=(
	"${BUILD_ROOT}/${MAKE_PLATFORM}q3ded"
)

compile_module() {
	local module_name="$1"
	local output_path="$2"
	local module_defines="$3"
	shift 3
	local sources=("$@")
	local objects=()
	local source_path
	local rel_path
	local object_path

	echo "[native-posix] Building ${module_name} -> ${output_path}"
	for source_path in "${sources[@]}"; do
		if [[ ! -f "${source_path}" ]]; then
			echo "Missing ${module_name} source: ${source_path}" >&2
			exit 1
		fi

		rel_path="${source_path#${REPO_ROOT}/}"
		object_path="${BUILD_ROOT}/obj/${module_name}/${rel_path}.o"
		mkdir -p "$(dirname "${object_path}")"
		"${CC}" ${CFLAGS} ${module_defines} -o "${object_path}" -c "${source_path}"
		objects+=("${object_path}")
	done

	mkdir -p "$(dirname "${output_path}")"
	"${CC}" ${SHLIB_LDFLAGS} -o "${output_path}" "${objects[@]}"
}

COMMON_DEFINES="-DQL_BUILD_ONLINE_SERVICES=0 -DQL_BUILD_STEAMWORKS=0 -DQL_BUILD_OPEN_STEAM=0 -DQL_ENABLE_OGG=0 -DQL_ENABLE_RANKINGS=0"
compile_module "cgame" "${MODULE_TARGETS[0]}" "${COMMON_DEFINES} -DCGAME" "${CGAME_SOURCES[@]}"
compile_module "qagame" "${MODULE_TARGETS[1]}" "${COMMON_DEFINES} -DGLOBALRANK" "${QAGAME_SOURCES[@]}"
compile_module "ui" "${MODULE_TARGETS[2]}" "${COMMON_DEFINES} -DUI_EXPORTS" "${UI_SOURCES[@]}"

BUILD_TARGETS=("${MODULE_TARGETS[@]}" "${HOST_TARGETS[@]}")
if [[ "${PLATFORM_NAME}" == "linux" && "${QL_POSIX_BUILD_CLIENT:-0}" == "1" ]]; then
	BUILD_TARGETS+=("${BUILD_ROOT}/linuxquake3")
	BUILD_TARGETS+=("${BUILD_ROOT}/linuxquake3-smp")
fi

echo "[native-posix] Building ${PLATFORM_NAME}/${HOST_ARCH} dedicated host under ${BUILD_ROOT}"
make -j "${MAKE_JOBS}" \
	-C "${UNIX_MAKE_DIR}" \
	"B=${BUILD_ROOT}" \
	"ARCH=${HOST_ARCH}" \
	"PLATFORM=${MAKE_PLATFORM}" \
	"CC=${CC}" \
	"CXX=${CXX}" \
	"CFLAGS=${CFLAGS}" \
	"DEBUG_CFLAGS=${CFLAGS}" \
	"RELEASE_CFLAGS=${CFLAGS}" \
	"SHLIBEXT=${SHLIB_EXT}" \
	"SHLIBCFLAGS=-fPIC" \
	"SHLIBLDFLAGS=${SHLIB_LDFLAGS}" \
	"LDFLAGS=${HOST_LDFLAGS}" \
	"PNG_CFLAGS=" \
	"PNG_LDFLAGS=-lpng" \
	"QL_BUILD_ONLINE_SERVICES=0" \
	"QL_BUILD_STEAMWORKS=0" \
	"QL_BUILD_OPEN_STEAM=0" \
	"QL_ENABLE_OGG=0" \
	"QL_ENABLE_RANKINGS=0" \
	"QL_ENABLE_FREETYPE=0" \
	makedirs "${HOST_TARGETS[@]}"

DIST_ROOT="${BUILD_ROOT}/dist"
PACKAGE_ROOT="${BUILD_ROOT}/package-root"
for path in "${DIST_ROOT}" "${PACKAGE_ROOT}"; do
	case "${path}" in
		"${BUILD_ROOT}"/*)
			rm -rf "${path}"
			mkdir -p "${path}"
			;;
		*)
			echo "Refusing to reset path outside build root: ${path}" >&2
			exit 1
			;;
	esac
done

hash_file() {
	if command -v sha256sum >/dev/null 2>&1; then
		sha256sum "$1" | awk '{print $1}'
	else
		shasum -a 256 "$1" | awk '{print $1}'
	fi
}

manifest_path="${DIST_ROOT}/native-build-manifest.txt"
package_version="${QL_POSIX_PACKAGE_VERSION:-}"
{
	if [[ -n "${package_version}" ]]; then
		echo "artifact_version=${package_version}"
	fi
	echo "platform=${PLATFORM_NAME}"
	echo "make_platform=${MAKE_PLATFORM}"
	echo "arch=${HOST_ARCH}"
	echo "source_sha=${GITHUB_SHA:-unknown}"
	echo "outputs:"
} > "${manifest_path}"

copy_output() {
	local absolute_path="$1"
	local rel_path="${absolute_path#${BUILD_ROOT}/}"
	if [[ ! -f "${absolute_path}" ]]; then
		echo "Expected native build output was not produced: ${absolute_path}" >&2
		exit 1
	fi

	mkdir -p "${PACKAGE_ROOT}/$(dirname "${rel_path}")"
	cp "${absolute_path}" "${PACKAGE_ROOT}/${rel_path}"
	printf "  %s  %s\n" "$(hash_file "${absolute_path}")" "${rel_path}" >> "${manifest_path}"
}

for output in "${BUILD_TARGETS[@]}"; do
	copy_output "${output}"
done

cp "${manifest_path}" "${PACKAGE_ROOT}/native-build-manifest.txt"

if [[ -n "${package_version}" ]]; then
	package_name="QuakeLive-reverse-${package_version}-${PLATFORM_NAME}-${HOST_ARCH}-native.tar.gz"
else
	package_name="quakelive-${PLATFORM_NAME}-${HOST_ARCH}-native.tar.gz"
fi
tar -czf "${DIST_ROOT}/${package_name}" -C "${PACKAGE_ROOT}" .
printf "package_sha256=%s  %s\n" "$(hash_file "${DIST_ROOT}/${package_name}")" "${package_name}" >> "${manifest_path}"

echo "[native-posix] Published ${DIST_ROOT}/${package_name}"
echo "[native-posix] Manifest ${manifest_path}"
