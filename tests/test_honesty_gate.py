"""Offline honesty gate for what this repository actually runs.

The checks below are the contract for `make check`. They call the real
pre-review command, recompute baseline numbers from tmlr_baselines.yaml,
count rulebook entries, and fail if README.md drifts from those facts.
"""
import json
import subprocess
import sys
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
FIXTURES = ROOT / "fixtures" / "pre_review"

TRIGGER_RULES = ["C1", "C9", "C7", "C4", "W4", "W4", "W4", "W4", "W4", "ABSTRACT"]
UNIMPLEMENTED_TIER1 = {"L1", "C6", "M1", "M3"}


def _run(*args):
    return subprocess.run(
        [sys.executable, *args],
        cwd=ROOT,
        capture_output=True,
        text=True,
    )


def _readme():
    return (ROOT / "README.md").read_text(encoding="utf-8")


def _problem_lines(text):
    start = text.index("## Problem\n") + len("## Problem\n")
    rest = text[start:]
    nxt = rest.find("\n## ")
    section = rest if nxt < 0 else rest[:nxt]
    return [line for line in section.splitlines() if line.strip()]


def test_version_file_is_dev():
    assert (ROOT / "VERSION").read_text(encoding="utf-8").strip() == "0.1.0-dev"


def test_readme_problem_is_three_lines_and_matches_what_runs():
    text = _readme()
    assert text.startswith("# Loop Engineering 0.1.0-dev\n")
    assert "STATUS: WORK-IN-PROGRESS — not A yet" in text
    lines = _problem_lines(text)
    assert len(lines) <= 3, lines
    assert "does not load `rulebook.yaml`" in text
    assert "L1, C6, M1, or M3" in text
    assert "Tier 2, Tier 3, and `cross_ref.yaml` are specs" in text
    assert "38 rule entries" in text
    assert "numeric medians are 4.5 datasets and 3.5 models" in text
    assert "hand-coded" in text
    assert "not verified against the papers" in text
    assert "statistical_tests_reported_pct` of 20" in text
    without_about_quote = text.replace("跨论文智能审阅系统（v4.0）", "")
    assert "v4.0" not in without_about_quote
    for banned in (
        "v4.1",
        "共 47 条",
        "47 rules",
        "从真实审阅实践提取",
        "82 条",
        "Top 5%",
    ):
        assert banned not in text, banned


def test_readme_names_the_github_about_gap():
    text = _readme()
    assert "跨论文智能审阅系统（v4.0）" in text
    assert "0.1.0-dev: hard-coded regex pre-review of a local main.tex" in text


def test_failure_modes_cover_the_required_limits():
    text = (ROOT / "FAILURE_MODES.md").read_text(encoding="utf-8")
    assert "n=5" in text
    assert "hand-coded" in text
    assert "false positive" in text
    assert "false negative" in text
    assert "no ground-truth reviewer agreement" in text
    assert "Spot-check on 2026-11-16, not re-run by make check" in text
    assert "Top 5%" in text
    assert "TMLR-03" in text
    assert "not a confirmed acceptance" in text
    assert "Weili Shi" in text


def test_prereg_withdraws_the_old_claims():
    text = (ROOT / "PREREG.md").read_text(encoding="utf-8")
    assert "0.1.0-dev" in text
    assert "withdrawn" in text


def test_rule_counts_match_entries_not_the_inflated_47():
    data = yaml.safe_load((ROOT / "rulebook.yaml").read_text(encoding="utf-8"))
    sections = ("tier_1", "tier_2", "tier_3", "defense", "tier_2_plus")
    counts = {name: len(data[name]) for name in sections}
    assert counts == {
        "tier_1": 7,
        "tier_2": 10,
        "tier_3": 8,
        "defense": 4,
        "tier_2_plus": 9,
    }
    assert sum(counts.values()) == 38
    assert data["stats"]["total_patterns"] == 38
    inflated = sum(len(data[name]) for name in sections + ("stats",))
    assert inflated == 38 + len(data["stats"])
    header = (ROOT / "rulebook.yaml").read_text(encoding="utf-8").split("tier_1:", 1)[0]
    assert "82 patterns extracted" not in header


def test_recomputed_baseline_medians_are_not_the_stored_aggregate():
    import status

    assert hasattr(status, "recompute_baselines")
    data = yaml.safe_load((ROOT / "tmlr_baselines.yaml").read_text(encoding="utf-8"))
    rec = status.recompute_baselines(data)
    assert rec == {
        "n_papers": 5,
        "n_numeric_datasets": 2,
        "n_numeric_models": 2,
        "median_datasets_numeric": 4.5,
        "median_models_numeric": 3.5,
        "ci_flag_pct": 0,
        "effect_size_flag_pct": 0,
        "median_score": 7.0,
        "statistical_tests_reported_pct": 0,
    }
    agg = data["aggregate"]
    assert agg["median_datasets"] == 4
    assert agg["median_models"] == 3
    assert agg["ci_reported_pct"] == 0
    assert agg["effect_size_reported_pct"] == 0
    assert agg["median_estimated_score"] == 7.0
    assert agg["statistical_tests_reported_pct"] == 20
    assert agg["median_datasets"] != rec["median_datasets_numeric"]
    assert agg["statistical_tests_reported_pct"] != rec["statistical_tests_reported_pct"]
    raw = (ROOT / "tmlr_baselines.yaml").read_text(encoding="utf-8")
    assert "HAND-CODED" in raw.split("baselines:", 1)[0]


def test_trigger_fixture_matches_golden():
    proc = _run("pre_review.py", "--tex", str(FIXTURES / "trigger.tex"), "--json")
    assert proc.returncode == 0, proc.stderr
    actual = json.loads(proc.stdout)
    expected = json.loads((FIXTURES / "trigger.golden.json").read_text(encoding="utf-8"))
    assert [item["rule"] for item in actual] == TRIGGER_RULES
    assert actual == expected


def test_clean_fixture_has_no_hits():
    proc = _run("pre_review.py", "--tex", str(FIXTURES / "clean.tex"), "--json")
    assert proc.returncode == 0, proc.stderr
    assert json.loads(proc.stdout) == []


def test_gap_fixture_misses_unimplemented_tier1_rules():
    proc = _run("pre_review.py", "--tex", str(FIXTURES / "tier1_gaps.tex"), "--json")
    assert proc.returncode == 0, proc.stderr
    rules = {item["rule"] for item in json.loads(proc.stdout)}
    assert rules.isdisjoint(UNIMPLEMENTED_TIER1)
    assert rules == set()


def test_ordinal_first_is_a_false_positive():
    proc = _run("pre_review.py", "--tex", str(FIXTURES / "false_positive_first.tex"), "--json")
    assert proc.returncode == 0, proc.stderr
    actual = json.loads(proc.stdout)
    expected = json.loads(
        (FIXTURES / "false_positive_first.golden.json").read_text(encoding="utf-8")
    )
    assert actual == expected
    assert actual[0]["rule"] == "C1"
    assert "First, we describe the setup" in actual[0]["description"]


def test_tier2_flag_fails_closed():
    proc = _run("pre_review.py", "--tex", str(FIXTURES / "clean.tex"), "--tier", "2")
    assert proc.returncode == 2
    assert "not implemented" in proc.stderr


def test_scanner_does_not_load_the_rulebook():
    import inspect
    import pre_review

    assert "rulebook" not in inspect.getsource(pre_review.run_tier1_checks)


def test_dashboard_prints_dev_version_and_recomputed_medians():
    proc = _run("status.py", "--all")
    assert proc.returncode == 0, proc.stderr
    assert "Loop Engineering 0.1.0-dev" in proc.stdout
    assert "Loop Engineering v4.0" not in proc.stdout
    assert "Loop Engineering v4.1" not in proc.stdout
    assert "stored strings, not this package version" in proc.stdout
    assert "4.5" in proc.stdout
    assert "3.5" in proc.stdout
    assert "hand-coded" in proc.stdout


def test_python_sources_do_not_advertise_v4():
    bad = []
    for path in ROOT.glob("*.py"):
        text = path.read_text(encoding="utf-8")
        if "v4.0" in text or "v4.1" in text:
            bad.append(path.name)
    assert bad == []


def test_ci_runs_make_check():
    ci = (ROOT / ".github" / "workflows" / "ci.yml").read_text(encoding="utf-8")
    makefile = (ROOT / "Makefile").read_text(encoding="utf-8")
    assert "\ncheck:" in makefile or makefile.startswith("check:")
    assert "tests/test_honesty_gate.py" in makefile
    assert "make check" in ci
    assert "make check || true" not in ci


def test_eval_cases_do_not_require_the_inflated_rule_count():
    raw = (ROOT / "eval" / "cases.jsonl").read_text(encoding="utf-8")
    assert "7|10|8|47" not in raw
    assert "共 47 条" not in raw
