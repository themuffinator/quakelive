from __future__ import annotations

import ast
import dataclasses
import re
from pathlib import Path
from typing import Dict, List, Sequence, Tuple

ROOT = Path(__file__).resolve().parents[1]
LEDGER_PATH = ROOT / "docs/reverse-engineering/configstrings-ledger.md"
SRC_ROOT = ROOT / "src/code"

LEDGER_ROW_RE = re.compile(r"\|\s*`(?P<index>0x[0-9a-fA-F]+|\d+)`\s*\|\s*`(?P<macro>CS_[A-Z0-9_]+)`")
DEFINE_RE = re.compile(r"^\s*#define\s+(CS_[A-Za-z0-9_]+)\s+(.+)$")


@dataclasses.dataclass
class MacroDefinition:
    name: str
    value: int
    path: Path
    line: int
    expr: str


class ExpressionEvaluator(ast.NodeVisitor):
    ALLOWED_BIN_OPS = {
        ast.Add: lambda a, b: a + b,
        ast.Sub: lambda a, b: a - b,
        ast.Mult: lambda a, b: a * b,
        ast.FloorDiv: lambda a, b: a // b,
        ast.Div: lambda a, b: a // b,
        ast.Mod: lambda a, b: a % b,
        ast.BitOr: lambda a, b: a | b,
        ast.BitAnd: lambda a, b: a & b,
        ast.BitXor: lambda a, b: a ^ b,
        ast.LShift: lambda a, b: a << b,
        ast.RShift: lambda a, b: a >> b,
    }

    ALLOWED_UNARY_OPS = {
        ast.UAdd: lambda v: +v,
        ast.USub: lambda v: -v,
    }

    def __init__(self, symbol_table: Dict[str, int]):
        self.symbol_table = symbol_table

    def visit(self, node):  # type: ignore[override]
        if isinstance(node, ast.Expression):
            return self.visit(node.body)
        if isinstance(node, ast.Constant):
            if not isinstance(node.value, (int, float)):
                raise ValueError(f"Unsupported constant: {node.value!r}")
            return int(node.value)
        if isinstance(node, ast.Name):
            if node.id not in self.symbol_table:
                raise KeyError(node.id)
            return self.symbol_table[node.id]
        if isinstance(node, ast.UnaryOp):
            operator = type(node.op)
            if operator not in self.ALLOWED_UNARY_OPS:
                raise ValueError(f"Unsupported unary operator: {operator}")
            return self.ALLOWED_UNARY_OPS[operator](self.visit(node.operand))
        if isinstance(node, ast.BinOp):
            operator = type(node.op)
            if operator not in self.ALLOWED_BIN_OPS:
                raise ValueError(f"Unsupported binary operator: {operator}")
            return self.ALLOWED_BIN_OPS[operator](self.visit(node.left), self.visit(node.right))
        raise ValueError(f"Unsupported AST node: {type(node)}")


def _strip_comments(expr: str) -> str:
    expr = expr.split("//", 1)[0]
    expr = re.sub(r"/\*.*?\*/", "", expr)
    return expr.strip()


def parse_ledger(path: Path) -> Dict[str, int]:
    ledger: Dict[str, int] = {}
    for line in path.read_text().splitlines():
        match = LEDGER_ROW_RE.match(line)
        if not match:
            continue
        ledger[match.group("macro")] = int(match.group("index"), 0)
    return ledger


def parse_definitions(src_root: Path) -> Tuple[Dict[str, List[MacroDefinition]], List[Tuple[str, str, Path, int]]]:
    definitions: List[Tuple[str, str, Path, int]] = []
    for path in src_root.rglob("*.h"):
        for line_no, line in enumerate(path.read_text().splitlines(), 1):
            match = DEFINE_RE.match(line)
            if not match:
                continue
            name, expr = match.groups()
            expr = _strip_comments(expr)
            if not expr:
                continue
            definitions.append((name, expr, path, line_no))

    resolved: Dict[str, List[MacroDefinition]] = {}
    unresolved = definitions
    progress = True
    while unresolved and progress:
        progress = False
        next_unresolved: List[Tuple[str, str, Path, int]] = []
        symbol_table = {name: defs[-1].value for name, defs in resolved.items()}
        for name, expr, path, line_no in unresolved:
            evaluator = ExpressionEvaluator(symbol_table)
            try:
                value = evaluator.visit(ast.parse(expr, mode="eval"))
            except (SyntaxError, KeyError, ValueError):
                next_unresolved.append((name, expr, path, line_no))
                continue
            resolved.setdefault(name, []).append(
                MacroDefinition(name=name, value=value, path=path, line=line_no, expr=expr)
            )
            progress = True
        unresolved = next_unresolved
    return resolved, unresolved


def _format_definitions(defs: Sequence[MacroDefinition]) -> str:
    parts = []
    for entry in defs:
        relative = entry.path.relative_to(ROOT)
        parts.append(f"{relative}:{entry.line} -> {hex(entry.value)} (expr: {entry.expr})")
    return "; ".join(parts)


def test_configstring_indices_match_ledger():
    ledger = parse_ledger(LEDGER_PATH)
    resolved, unresolved = parse_definitions(SRC_ROOT)

    missing = []
    mismatched = []
    for macro, expected in ledger.items():
        definitions = resolved.get(macro)
        if not definitions:
            missing.append(macro)
            continue
        wrong = [definition for definition in definitions if definition.value != expected]
        if wrong:
            mismatched.append((macro, expected, wrong))

    still_unresolved = [entry for entry in unresolved if entry[0] in ledger]

    messages: List[str] = []
    if missing:
        messages.append("Missing configstring definitions: " + ", ".join(sorted(missing)))
    if mismatched:
        for macro, expected, defs in mismatched:
            messages.append(
                f"{macro} expected {hex(expected)} but found: {_format_definitions(defs)}"
            )
    if still_unresolved:
        unresolved_details = "; ".join(
            f"{path.relative_to(ROOT)}:{line} -> {expr}" for name, expr, path, line in still_unresolved
        )
        messages.append("Unresolved expressions: " + unresolved_details)

    assert not messages, "\n".join(["Configstring ledger drift detected:", *messages])
