# Linux glibc (32-bit) build preset

This preset rebuilds the Quake Live `qagamei386.so` against the historical glibc baseline (`libc6`) and X11/OpenGL headers called out in the original Linux README. It pairs a multiarch GCC toolchain with the archive copy of the server module so you can confirm symbol parity after the build.

Scope note: this preset is intentionally limited to the 32-bit `qagamei386.so` server-module lane. It is useful for export and symbol parity against the archived Linux shared object, but it is not evidence of a retail-equivalent Linux client/runtime, and it does not close the remaining Unix renderer/audio/input host gaps tracked in the portability ledgers. If you need engine-host profiling on Linux, the Unix makefile now exposes `QL_ENABLE_GPROF=1` for a bounded `gprof`-compatible build lane, the Unix host also carries a bounded clipboard retrieval path via `wl-paste`, `xclip`, or `xsel` when those helpers are available, `Sys_CheckCD()` now performs a bounded data-root probe across `fs_basepath`, `fs_cdpath`, and the default install roots for `baseq3/default.cfg`, `pak00.pk3`, or `pak0.pk3`, Unix `Sys_LoadDll()` now probes cwd plus `fs_homepath`, `fs_basepath`, and `fs_cdpath` and rejects incompatible native-module candidates before continuing, Unix `Sys_GetEvent()` now preserves only unread packet bytes after `netmsg.readcount`, the Linux input shutdown path now releases retained X mouse grabs before clearing mouse availability, and a bounded silent Linux sound sink is available through `snddevice null` for headless/client smoke work, but all of those remain separate from this server-module-only preset.

## Prerequisites

The legacy README expects a glibc-based userland (`libc6`) plus the X11 DGA/VidMode and OpenGL headers used by the original port.【F:src/code/unix/README.Linux†L68-L155】 On Debian/Ubuntu hosts, enable the `i386` architecture and install the 32-bit development stack before building:

```bash
sudo dpkg --add-architecture i386
sudo apt-get update
sudo apt-get install -y build-essential gcc-multilib g++-multilib libc6-dev-i386 \
  libx11-dev:i386 libxext-dev:i386 libxxf86dga-dev:i386 libxxf86vm-dev:i386 \
  libgl1-mesa-dev:i386 libglu1-mesa-dev:i386
```

The preset relies on pkg-config to locate the 32-bit headers; if your distribution stores `.pc` files somewhere other than `/usr/lib/i386-linux-gnu/pkgconfig`, set `PKG_CONFIG_LIBDIR` accordingly.

## Build and validation steps

Use the helper script to emit a Release-flavored `qagamei386.so` and diff its exports against the archived reference at `assets/quakelive/baseq3/qagamei386.so`:

```bash
BUILD_DIR=build/linux-i386-glibc tools/build/linux32_qagame.sh
```

The script pins the 32-bit toolchain flags (`-m32` with `-std=gnu89`), disables Vorbis for the server-only build, and writes both the rebuilt module and the export comparison artifacts under `$BUILD_DIR`.

After the run, review the parity report:

- `build/linux-i386-glibc/baseq3/qagamei386.so` – freshly built 32-bit server module
- `build/linux-i386-glibc/qagame.exports` – sorted export list from the new build
- `build/linux-i386-glibc/qagame-reference.exports` – sorted exports from the archived binary
- `build/linux-i386-glibc/qagame.exports.diff` – unified diff showing any symbol drift (empty if the lists match)

Re-run the script after code changes to keep the Linux native module aligned with the shipped Quake Live artifact.
