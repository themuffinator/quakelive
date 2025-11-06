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
3. Inspect `logs/syscall_contract.log` after the run completes. The checked-in
   placeholder carries notes about noisy modules and example invocations for the
   validator. The actual capture produced by the engine will overwrite those
   comments on each run.

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

### Targeted comparisons

Use `--module` to focus on a specific subsystem without editing the expectation
file. This is useful when UI churn or match setup noise would otherwise drown
out the section you are investigating:

```bash
python tools/tests/validate_syscall_contract.py --module shim-ui
```

Repeat the flag to include multiple modules in a single validation run.

### Temporary wildcard overrides

Occasionally a contract change is limited to one or two arguments (for example a
pointer that now lands at a different address). Rather than committing a
permanent wildcard, pass `--wildcard` to treat specific token positions as
ignored for the duration of the run:

```bash
python tools/tests/validate_syscall_contract.py --wildcard shim-ui:5,6
```

Token indices are 1-based, so `1` refers to the origin, `2` to the module name,
and so on for the argument list.

If the validator reports a mismatch it prints both the offending tokens and a
unified diff. Lines prefixed with `-` indicate the expected value, while lines
prefixed with `+` are what the latest log produced. The script exits with a
non-zero status when mismatches are found so CI can fail fast. Update the
expectation file once you have confirmed the new contract is intentional.

### Troubleshooting tips

- Use `--wildcard` for transient pointer churn rather than editing the baseline
  expectation file until the change is confirmed.
- Combine `--module` filters with targeted repro steps (e.g. navigating to the
  scoreboard) to isolate the smallest possible diff before updating
  expectations.
- If the validator exits with status 2, inspect the error message for malformed
  wildcard syntax (the parser requires `MODULE:IDX[,IDX...]`).
