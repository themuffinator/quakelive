import json
from pathlib import Path

import pytest

import tests.run_harnesses as run_harnesses


@pytest.fixture()
def ruleset_only(monkeypatch):
    monkeypatch.setattr(
        run_harnesses,
        "SCENARIOS",
        {"ruleset_pql": run_harnesses.SCENARIOS["ruleset_pql"]},
    )


def test_ruleset_metadata_propagates(tmp_path: Path, ruleset_only):
    summaries = run_harnesses._run_match_harness("qvm", tmp_path, seed=1337)
    assert len(summaries) == 1

    summary = summaries[0]
    assert summary["slug"] == "ruleset_pql"
    assert summary["ruleset"] == "pql"
    assert summary["metadata"].get("ruleset") == "pql"

    timeline_path = tmp_path / "match_sim" / "qvm" / "ruleset_pql" / "timeline.json"
    timeline = json.loads(timeline_path.read_text(encoding="utf-8"))
    assert timeline["config"]["metadata"]["ruleset"] == "pql"
