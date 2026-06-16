# ZMQ Dependency Ownership Decision

Date: 2026-06-06

## Question

Recent ZMQ mapping rounds name a large embedded `zmq::` surface in the retail
`quakelive_steam.exe` reference.  That raised an ownership question: should the
project vendor libzmq under `src/libs/` and remove library implementation code
from `src/code/`?

## Observed Facts

- The retail binary includes a substantial libzmq-like implementation: public
  `zmq_*` wrappers, `ctx_t`, `socket_base_t`, `own_t`, `pipe_t`,
  poller/select, session, stream engine, mechanisms, tries, queues, and related
  STL support helpers.  The mapping rounds name that evidence so retail control
  flow can be understood.
- Writable source does not currently contain a libzmq implementation.  The only
  ZMQ-named source file under `src/code/` is `src/code/server/sv_zmq.c`.
- `sv_zmq.c` is the Quake Live server-owned `idZMQ` integration layer: it
  registers the mapped `zmq_*` cvars, owns RCON/stats endpoints, formats
  publication frames, tracks RCON peers, provides fallback transcript behavior,
  and dynamically resolves external libzmq symbols.
- Default builds still do not use live ZMQ transport.  `idZMQ_LoadLibrary`
  returns disabled fallback behavior when `QL_BUILD_ONLINE_SERVICES=0` through
  the `QL_PLATFORM_HAS_ONLINE_SERVICES` policy guard.
- The current build files compile `server/sv_zmq.c` but do not compile or link
  a vendored libzmq tree from `src/code/` or `src/libs/`.

## Conclusion

Do not install or vendor libzmq implementation source under `src/libs/`, and
do not move or remove `src/code/server/sv_zmq.c`. A README-only
`src/libs/libzmq/` runtime-drop directory is acceptable so local opted-in builds
have a clear place for an ignored external `libzmq.dll`.

The reverse-engineering corpus is reconstructing the retail embedded libzmq
surface for naming and behavioral evidence.  The writable source is not
hand-rolling that library under `src/code`; it is reconstructing Quake Live's
server-owned `idZMQ` wiring and using external libzmq dynamically for opted-in
online-service builds.

The current install convention is runtime-only:

- Prefer `ZMQ_RUNTIME_DIR` or the MSBuild property `ZmqRuntimeDir` when a local
  libzmq runtime lives outside the repository.
- For a repo-local developer drop, use
  `src/libs/libzmq/bin/Win32/libzmq.dll`; `.gitignore` keeps that payload
  untracked.
- The Windows project copies `libzmq.dll` to the output directory when online
  services are enabled and a runtime path exists, but it does not include
  `zmq.h` or link `libzmq.lib`.

## Boundary For Future Work

If a future task deliberately chooses to replace dynamic loading with a vendored
libzmq dependency, the dependency should be introduced under `src/libs/` with
an explicit build target and documentation.  That change would be a separate
architecture decision because it would alter the current opt-in runtime contract
and the default-disabled online-service boundary.

Until then:

- Keep `sv_zmq.c` in `src/code/server/` as Quake Live server integration code.
- Do not add libzmq implementation files under `src/code/`.
- Do not add libzmq or CZMQ source files under `src/libs/libzmq/`; that path is
  for ignored runtime drops only.
- Keep live transport behind `QL_BUILD_ONLINE_SERVICES`.
- Treat the large `zmq::` alias map as retail dependency evidence, not as a
  directive to reconstruct third-party library internals in engine source.
