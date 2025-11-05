# Trace harness for deterministic regression testing

This harness captures short match simulations with syscall, random number generator
and entity state streams so that we can confirm deterministic execution during
reverse-engineering work. The utilities live under `tools/trace/` and are written
as pure Python helpers that can be executed on any workstation that has the Quake
Live binaries and instrumentation tooling available.

## Launching a capture

1. Ensure the instrumented client or VM emits trace lines to stdout or stderr
   using the format `TRACE:<CHANNEL>:<JSON_PAYLOAD>`. The harness recognises the
   following channels:

   | Channel | Purpose | Example payload |
   |---------|---------|-----------------|
   | `META`  | Key/value metadata stored verbatim in the manifest. | `{"map": "qztourney7"}` |
   | `SYS`   | Syscall stream captured from the VM. | `{"name": "trap_Print", "args": ["go"]}` |
   | `RNG`   | RNG seeds or reseeding events. | `{"seed": 123456, "reason": "warmup"}` |
   | `ENT`   | Entity state snapshots. | `{"time": 123, "entities": [{"id": 1, "health": 125}]}` |

2. Run the launcher with the instrumented binary. Example:

   ```bash
   python -m tools.trace.launcher --output ./out/trace -- \
       /path/to/instrumented-client +set fs_game baseq3
   ```

   When using the Python API directly:

   ```python
   from pathlib import Path
   from tools.trace import TraceLauncher, TraceLauncherConfig

   config = TraceLauncherConfig(
       command=["/path/to/instrumented-client", "+set", "fs_game", "baseq3"],
       output_dir=Path("./out/trace"),
       match_duration=45.0,  # seconds
   )
   result = TraceLauncher(config).launch()
   print("Trace stored in", result.output_dir)
   ```

   The launcher trims runs to short matches by default (`match_duration=60s`).
   Traces longer than this window trigger a graceful terminate and, if required,
   a hard kill after the termination timeout expires.

## Generated artefacts

A successful capture produces the following files inside the output directory:

- `manifest.json`: summary of the run including command line, exit code, event
  counts, metadata and per-channel digests.
- `stdout.log` / `stderr.log`: raw textual output from the instrumented process.
- `syscalls.jsonl`: canonical JSON lines stream of syscall invocations.
- `rng_seeds.jsonl`: JSON lines containing RNG seed mutations.
- `entities.jsonl`: JSON lines containing entity state snapshots.

All JSON artefacts are normalised with sorted keys and newline-terminated entries.
The digests stored in the manifest are SHA-256 hashes of those canonical strings
so that replays can detect even single byte differences.

## Replay and determinism checks

The replay helper feeds the captured artefacts back into a VM or DLL binding and
confirms that the resulting digests match the ones stored during capture.

```python
from pathlib import Path
from tools.trace import TraceReplayer, TraceVMDriver

class RecordingDriver(TraceVMDriver):
    def apply_syscall(self, event):
        # send syscall back into the VM implementation
        ...

    def apply_rng_seed(self, event):
        # reseed the VM RNG
        ...

    def apply_entity_state(self, event):
        # optionally assert entity state transitions
        ...

replayer = TraceReplayer(Path("./out/trace"), RecordingDriver())
result = replayer.replay()
print("Replayed", result.counts["syscalls"], "syscalls deterministically")
```

If any digest diverges, the replayer raises `TraceReplayMismatch` with details so
that the offending channel can be inspected. Unknown trace lines are preserved in
`manifest.json` under the `unknown_lines` key for quick debugging.
