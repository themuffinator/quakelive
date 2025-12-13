"""
Launcher validation harness for comparing in-engine implementations against the
legacy Awesomium launcher flows documented in docs/launcher_awesomium_audit.md.

The harness does not depend on Awesomium. Instead, it inspects repository
artifacts (menus, bridge shims, resource handlers) and reports which elements
align with the expected bootstrap, data source, JS bridge, and frame-pump
contracts.
"""

from __future__ import annotations

import argparse
import dataclasses
import json
import sys
from pathlib import Path
from typing import Dict, Iterable, List, Optional

AUDIT_DOC = Path("docs/launcher_awesomium_audit.md")


@dataclasses.dataclass
class ValidationResult:
    """Container for a single validation outcome."""

    name: str
    passed: bool
    details: str

    def to_dict(self) -> Dict[str, object]:
        return {
            "name": self.name,
            "passed": self.passed,
            "details": self.details,
        }


@dataclasses.dataclass
class ValidationPlan:
    """Description of expected launcher artifacts and behaviours."""

    required_files: List[Path] = dataclasses.field(default_factory=list)
    optional_files: List[Path] = dataclasses.field(default_factory=list)
    notes: List[str] = dataclasses.field(default_factory=list)

    @classmethod
    def default(cls) -> "ValidationPlan":
        return cls(
            required_files=[
                Path("src/code/ui/ui_launcher.c"),
                Path("src/code/ui/ui_launcher.h"),
                Path("src/ui/launcher.menu"),
                Path("assets/launcher/web.pak"),
            ],
            optional_files=[
                Path("src/code/ui/ui_launcher_bridge.c"),
                Path("src/code/ui/ui_launcher_bridge.h"),
                Path("src/code/ui/ui_launcher_surface.c"),
            ],
            notes=[
                "Session bootstrap should mirror Awesomium WebCore/WebSession setup.",
                "Data sources must include a web.pak loader and Steam-backed image path.",
                "Bridge table should expose focus/input/auth/view toggles like data_12d2670.",
                "Frame pump needs to replace bitmap surface uploads with renderer primitives.",
                "Validation should compare layout, input, and event propagation against HLIL audit.",
            ],
        )


class LauncherValidationHarness:
    """Validate launcher embedding artifacts relative to the audit checklist."""

    def __init__(self, root: Path, plan: ValidationPlan):
        self.root = root
        self.plan = plan

    def _check_file(self, path: Path, required: bool) -> ValidationResult:
        full_path = self.root / path
        exists = full_path.exists()
        if exists:
            detail = f"Found {path}"
        elif required:
            detail = (
                f"Missing required artifact: {path}. Expected per Awesomium audit sections "
                "covering session bootstrap, data sources, and JS bridge shims."
            )
        else:
            detail = f"Optional artifact absent: {path}"
        return ValidationResult(
            name=f"artifact::{path}",
            passed=exists or not required,
            details=detail,
        )

    def _check_audit_doc(self) -> ValidationResult:
        if (self.root / AUDIT_DOC).exists():
            return ValidationResult(
                name="documentation::audit_present",
                passed=True,
                details="Audit document available for reference.",
            )
        return ValidationResult(
            name="documentation::audit_present",
            passed=False,
            details=(
                "Audit document missing; expected docs/launcher_awesomium_audit.md to guide"
                " migration tests."
            ),
        )

    def run(self) -> List[ValidationResult]:
        results: List[ValidationResult] = []
        results.append(self._check_audit_doc())
        for path in self.plan.required_files:
            results.append(self._check_file(path, required=True))
        for path in self.plan.optional_files:
            results.append(self._check_file(path, required=False))
        return results

    @staticmethod
    def summarise(results: Iterable[ValidationResult]) -> Dict[str, object]:
        results_list = list(results)
        return {
            "passed": all(r.passed for r in results_list),
            "results": [r.to_dict() for r in results_list],
        }


def parse_args(argv: Optional[List[str]] = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Validate launcher embedding artifacts.")
    parser.add_argument(
        "--root",
        type=Path,
        default=Path(__file__).resolve().parent.parent,
        help="Repository root to scan.",
    )
    parser.add_argument(
        "--plan",
        type=Path,
        help="Path to a JSON file overriding the default validation plan.",
    )
    parser.add_argument("--json", action="store_true", help="Emit JSON instead of text.")
    return parser.parse_args(argv)


def load_plan(path: Optional[Path]) -> ValidationPlan:
    if path is None:
        return ValidationPlan.default()
    data = json.loads(path.read_text())
    return ValidationPlan(
        required_files=[Path(p) for p in data.get("required_files", [])],
        optional_files=[Path(p) for p in data.get("optional_files", [])],
        notes=data.get("notes", []),
    )


def main(argv: Optional[List[str]] = None) -> int:
    args = parse_args(argv)
    plan = load_plan(args.plan)
    harness = LauncherValidationHarness(args.root, plan)
    results = harness.run()
    summary = LauncherValidationHarness.summarise(results)

    if args.json:
        print(json.dumps(summary, indent=2))
    else:
        print("Launcher validation summary:")
        for note in plan.notes:
            print(f"- {note}")
        for result in results:
            status = "OK" if result.passed else "MISSING"
            print(f"[{status}] {result.name}: {result.details}")
        print(f"Overall status: {'PASS' if summary['passed'] else 'INCOMPLETE'}")
    return 0 if summary["passed"] else 1


if __name__ == "__main__":
    sys.exit(main())
