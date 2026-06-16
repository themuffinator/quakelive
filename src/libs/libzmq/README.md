# libzmq Runtime Drop

This directory is a local runtime-install location for opted-in ZMQ transport
builds. It is not a source reconstruction area.

Retail Quake Live appears to have linked a libzmq/CZMQ-derived implementation
into `quakelive_steam.exe`, and the reverse-engineering corpus maps that
embedded dependency so call sites and constants can be understood. SRP should
not recreate that third-party library in writable engine source.

## Local Windows Runtime

For a local online-service build that should copy `libzmq.dll` beside
`quakelive_steam.exe`, either:

1. Set `ZMQ_RUNTIME_DIR` or the MSBuild property `ZmqRuntimeDir` to a directory
   containing `libzmq.dll`.
2. Or place a local untracked runtime at:

   `src/libs/libzmq/bin/Win32/libzmq.dll`

The project copies that DLL to the build output when `QLBuildOnlineServices`
is enabled and a runtime path exists.

## Rules

- Do not commit `libzmq.dll`, `.lib`, `.pdb`, or other binary payloads.
- Do not commit libzmq/CZMQ source files under this directory.
- Do not add `#include <zmq.h>` or a static `libzmq.lib` link dependency to
  the engine project for the current dynamic-runtime design.
- Keep Quake Live-owned code in `src/code/server/sv_zmq.c`; it dynamically
  resolves the small public `zmq_*` export set it needs.
