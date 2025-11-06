# Syscall Contract Validation

The engine now records every syscall that crosses the VM/native boundary to
`logs/syscall_contract.log`. The log captures both sides of the interface:

- **VM layer** entries (`vm-interpreted` and `vm-dll`) show the raw command IDs
  delivered by the virtual machine runtime.
- **Shim layer** entries (`shim-cgame`, `shim-ui`, `shim-game`, and
  `shim-native`) reflect the arguments observed by the native glue code and
  clean-room prototypes before they are dispatched into the engine.

Each line is space-delimited and encodes the origin, module name, and a fixed
number of hexadecimal arguments. These lines provide a stable baseline that can
be diffed between the QVM and native builds.

## Generating the log

1. Ensure the engine has write access to the repository root (the log is written
   relative to `fs_homepath`).
2. Run the scenario you want to inspect (e.g. launch the client harness or play
   through the reproduction steps under test).
3. Inspect `logs/syscall_contract.log` after the run completes.

The log is truncated on engine start, so each run begins with a clean file.

## Validating against expectations

The blessed baseline lives at `tests/expectations/syscall_contract.expect`.
Execute the validator to compare the latest log against the baseline:

```bash
python tools/tests/validate_syscall_contract.py
```

By default the validator reads the standard log and expectation locations. Use
`--log` or `--expect` to override them if you are working with alternates.

Expectation files support `_` (or `*`) as a wildcard token that matches any
value. This makes it easy to ignore trailing stack noise or pointer values while
pinning down the arguments that matter.

If the validator reports a mismatch it prints both the offending tokens and a
unified diff. Lines prefixed with `-` indicate the expected value, while lines
prefixed with `+` are what the latest log produced. The script exits with a
non-zero status when mismatches are found so CI can fail fast. Update the
expectation file once you have confirmed the new contract is intentional.
