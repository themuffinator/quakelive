# QVM Toolchain Snapshot

The classic Quake III virtual machine (QVM) builders are still wired into the `src/code/Construct` meta-build and expect a staging directory called `code/qvmtools/`. The Cons script populates that folder on demand by compiling the required utilities and copying the resulting binaries back into the game tree for later reuse.【F:src/code/Construct†L287-L308】 This snapshot captures the binaries that are staged there today and the host requirements needed to rebuild them if the cache is missing.

## Bundled binaries and their sources

| Deliverable | Origin | How it is produced |
| --- | --- | --- |
| `q3lcc` | `src/lcc/` | Built through the platform-specific LCC makefiles (`makefile` on POSIX, `makefile.nt` via `nmake` on Windows) and copied into `code/qvmtools/` by the Cons helper.【F:src/lcc/makefile†L1-L60】【F:src/lcc/makefile.nt†L1-L61】【F:src/code/Construct†L287-L308】 |
| `q3rcc` | `src/lcc/` | Compiled alongside `q3lcc` by the same makefiles and deposited into `code/qvmtools/` once `build_tools('q3lcc')` completes.【F:src/lcc/makefile†L17-L36】【F:src/lcc/makefile.nt†L17-L36】【F:src/code/Construct†L287-L308】 |
| `q3cpp` | `src/lcc/` | Produced by the LCC driver build and staged together with `q3lcc`/`q3rcc` for reuse by the VM wrapper scripts.【F:src/lcc/makefile†L23-L30】【F:src/lcc/makefile.nt†L23-L30】【F:src/code/Construct†L287-L308】 |
| `q3asm` | `src/q3asm/` | Built with the standalone GNU makefile that wraps a direct `gcc` compile and then copied into `code/qvmtools/` by the Cons helper.【F:src/q3asm/Makefile†L1-L12】【F:src/code/Construct†L287-L308】 |

The VM wrappers that drive this toolchain (`src/code/game/game.sh`, `src/code/cgame/cgame.sh`, `src/code/q3_ui/q3_ui.sh`) assume those binaries live on the `PATH` and assemble the `.qvm` artefacts in a `vm/` subdirectory before invoking `q3asm` with the corresponding `.q3asm` linker script.【F:src/code/game/game.sh†L1-L46】【F:src/code/cgame/cgame.sh†L1-L34】【F:src/code/q3_ui/q3_ui.sh†L1-L53】【F:src/code/game/game.q3asm†L1-L15】 Windows batch equivalents (`game.bat`, `cgame.bat`, `q3_ui.bat`) provide the same orchestration for contributors who stay on the legacy toolchain.【F:src/code/game/game.bat†L1-L53】 These scripts populate `code/game/vm/`, `code/cgame/vm/`, and `code/q3_ui/vm/` with the bytecode payloads consumed by the engine and installation helpers such as `installvms.bat`.【F:src/code/installvms.bat†L1-L6】

## Host prerequisites

Recreating the staged binaries requires the original build prerequisites for each tool:

- **POSIX (Linux/macOS)** – The `src/lcc/makefile` assumes a Unix toolchain with `make`, a hosted C compiler (`cc`/`gcc`), `ar`, and `ranlib` for the archive steps.【F:src/lcc/makefile†L1-L37】 The assembler lives in `src/q3asm/` and builds with a single `gcc` invocation driven by its minimalist makefile.【F:src/q3asm/Makefile†L1-L12】
- **Windows** – The helper script `src/lcc/buildnt.sh` shells out to `nmake -f makefile.nt all`, which in turn hard-codes the Microsoft Visual C++ compiler (`cl`) and linker to emit the LCC family of executables in debug (`/MDd`) mode before they are copied into `code/qvmtools/`.【F:src/lcc/buildnt.sh†L1-L5】【F:src/lcc/makefile.nt†L1-L61】 The VM batch files expect those binaries to be reachable directly as `lcc`, `q3asm`, etc., mirroring the legacy Quake III development environment.【F:src/code/game/game.bat†L1-L53】

With these prerequisites in place, invoking the wrapper scripts will recreate the `.qvm` payloads exactly as the Quake III pipeline originally did, keeping bytecode builds available for regression testing while the native DLL workflow evolves.
