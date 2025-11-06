#!/usr/bin/env python3
"""Validate syscall contract logs against the expected baseline."""

from __future__ import annotations

import argparse
import difflib
from collections import defaultdict
from itertools import zip_longest
from pathlib import Path
import sys

DEFAULT_EXPECT = Path("tests/expectations/syscall_contract.expect")
DEFAULT_LOG = Path("logs/syscall_contract.log")


class ContractFilters:
    """Runtime filters that tailor validation runs."""

    def __init__(self, modules: set[str] | None = None):
        self.modules = modules or set()

    def applies(self) -> bool:
        return bool(self.modules)

    def include_line(self, tokens: list[str]) -> bool:
        if not self.modules:
            return True
        if len(tokens) < 2:
            return False
        return tokens[1] in self.modules


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


def _filter_contract(lines: list[str], filters: ContractFilters) -> list[str]:
    if not filters.applies():
        return lines
    filtered: list[str] = []
    for line in lines:
        tokens = _tokens(line)
        if filters.include_line(tokens):
            filtered.append(line)
    return filtered


def _parse_wildcard_overrides(values: list[str] | None) -> dict[str, set[int]]:
    overrides: dict[str, set[int]] = defaultdict(set)

    if not values:
        return overrides

    for value in values:
        if ":" not in value:
            raise ValueError(
                f"Invalid wildcard override '{value}'. Expected MODULE:IDX[,IDX...] format."
            )
        module, positions = value.split(":", 1)
        module = module.strip()
        if not module:
            raise ValueError(f"Invalid wildcard override '{value}': module is empty.")
        for raw_index in positions.split(","):
            raw_index = raw_index.strip()
            if not raw_index:
                continue
            try:
                index = int(raw_index)
            except ValueError as exc:  # pragma: no cover - defensive guard
                raise ValueError(
                    f"Invalid token index '{raw_index}' in wildcard override '{value}'."
                ) from exc
            if index < 1:
                raise ValueError(
                    f"Token indices must be 1-based; got {index} in wildcard override '{value}'."
                )
            overrides[module].add(index)
    return overrides


def _compare(
    expected: list[str],
    actual: list[str],
    wildcard_overrides: dict[str, set[int]] | None = None,
) -> list[str]:
    errors: list[str] = []

    wildcard_overrides = wildcard_overrides or {}

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

        module = exp_tokens[1] if len(exp_tokens) > 1 else ""
        overrides_for_module = wildcard_overrides.get(module, set())

        for pos, (exp_token, act_token) in enumerate(zip(exp_tokens, act_tokens), 1):
            if pos in overrides_for_module:
                continue
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
    parser.add_argument(
        "-m",
        "--module",
        action="append",
        dest="modules",
        help=(
            "Restrict validation to one or more module names. Repeat the flag to compare multiple modules."
        ),
    )
    parser.add_argument(
        "--wildcard",
        action="append",
        dest="wildcards",
        metavar="MODULE:IDX[,IDX...]",
        help=(
            "Temporarily treat the 1-based token indices for a module as wildcards without editing the expectation file."
        ),
    )

    args = parser.parse_args(argv)

    expected = _read_contract(args.expect)
    actual = _read_contract(args.log)

    filters = ContractFilters(set(args.modules) if args.modules else None)

    try:
        wildcard_overrides = _parse_wildcard_overrides(args.wildcards)
    except ValueError as exc:
        print(str(exc), file=sys.stderr)
        return 2

    if filters.applies():
        expected = _filter_contract(expected, filters)
        actual = _filter_contract(actual, filters)

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

    errors = _compare(expected, actual, wildcard_overrides)
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
