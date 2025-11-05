#!/usr/bin/env python3
"""Validate syscall contract logs against the expected baseline."""

from __future__ import annotations

import argparse
import difflib
from itertools import zip_longest
from pathlib import Path
import sys

DEFAULT_EXPECT = Path("tests/expectations/syscall_contract.expect")
DEFAULT_LOG = Path("logs/syscall_contract.log")


def _read_contract(path: Path) -> list[str]:
    if not path.exists():
        return []
    lines: list[str] = []
    for raw in path.read_text(encoding="utf-8").splitlines():
        stripped = raw.strip()
        if not stripped or stripped.startswith("#"):
            continue
        lines.append(stripped)
    return lines


def _tokens(line: str) -> list[str]:
    return line.split()


def _compare(expected: list[str], actual: list[str]) -> list[str]:
    errors: list[str] = []

    for index, (exp_line, act_line) in enumerate(zip_longest(expected, actual), 1):
        if exp_line is None:
            errors.append(f"Unexpected extra log line {index}: {act_line}")
            continue
        if act_line is None:
            errors.append(f"Missing log line {index}: expected '{exp_line}'")
            continue

        exp_tokens = _tokens(exp_line)
        act_tokens = _tokens(act_line)

        if len(exp_tokens) != len(act_tokens):
            errors.append(
                f"Token length mismatch on line {index}: expected {len(exp_tokens)}, got {len(act_tokens)}"
            )
            continue

        for pos, (exp_token, act_token) in enumerate(zip(exp_tokens, act_tokens), 1):
            if exp_token in {"_", "*"}:
                continue
            if exp_token != act_token:
                errors.append(
                    f"Mismatch on line {index}, token {pos}: expected '{exp_token}', got '{act_token}'"
                )
                break

    if errors:
        diff = difflib.unified_diff(
            expected,
            actual,
            fromfile="expectation",
            tofile="log",
            lineterm="",
        )
        errors.append("\n".join(diff))
    return errors


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--expect",
        type=Path,
        default=DEFAULT_EXPECT,
        help=f"Path to expectation file (default: {DEFAULT_EXPECT})",
    )
    parser.add_argument(
        "--log",
        type=Path,
        default=DEFAULT_LOG,
        help=f"Path to syscall contract log (default: {DEFAULT_LOG})",
    )

    args = parser.parse_args(argv)

    expected = _read_contract(args.expect)
    actual = _read_contract(args.log)

    if not expected:
        print(f"No expectations found in {args.expect}.", file=sys.stderr)
        if actual:
            print(
                "Log contains entries but expectation is empty; update the expectation file to match.",
                file=sys.stderr,
            )
            return 1
        print("Both expectation and log are empty. Nothing to validate.")
        return 0

    if not actual:
        print(f"Log file {args.log} is missing or empty.", file=sys.stderr)
        return 1

    errors = _compare(expected, actual)
    if errors:
        print("Syscall contract validation failed:", file=sys.stderr)
        for error in errors:
            if error:
                print(error, file=sys.stderr)
        return 1

    print("Syscall contract log matches expectations.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
