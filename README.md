# Loop Engineering v5.3

> Automated paper quality audit system for TMLR submissions. 91 rules, 15 checks, 15 modules.

## What It Does

Catches problems in your paper before reviewers do. Checks formatting, citations, statistics, methodology, LaTeX compilation, and semantic claims — all automated.

## Quick Start

```bash
# Full pre-submission audit
python submission_audit.py /path/to/paper/main.tex

# Quality checks only
python quality_checks.py /path/to/paper/

# Tier 1 pre-review scan
python pre_review.py /path/to/paper/

# Check citation accuracy via Semantic Scholar
python scholar_verify.py /path/to/paper/

# LaTeX compilation check
python latex_check.py /path/to/paper/

# Global status dashboard
python status.py --all
```

## What It Checks (91 Rules)

| Category | Count | Examples |
|----------|:---:|------|
| **Format** | 12 | TMLR compliance, anonymization, figure quality, dual-version consistency |
| **Citations** | 15 | Ghost refs, accuracy, Semantic Scholar verification, self-cite rate |
| **Statistics** | 18 | CI coverage, effect sizes, multiple comparison correction, power analysis |
| **Consistency** | 14 | Numerical cross-validation, symbol definitions, bibentry format |
| **Methodology** | 11 | Small sample N, selective reporting, cherry-picking detection |
| **LaTeX** | 12 | bibitem format, cite/bib matching, ref/label, aux/log analysis |
| **Semantics** | 9 | "First" claim verification, novelty search |

## Architecture

```
Configuration
  ├── registry.yaml          Paper registry (ID, path, status, dependencies)
  ├── rulebook.yaml          91 review rules (4 tiers)
  ├── cross_ref.yaml         Cross-paper issue correlation (8 patterns)
  └── tmlr_baselines.yaml    TMLR published paper baselines (5 papers)

Audit Engine
  ├── submission_audit.py    15 pre-submission checks
  ├── quality_checks.py      9 quality checks (Q1-Q9)
  ├── review_engine.py       3-tier batch scanning
  └── pre_review.py          Tier 1 pre-review scan

v5.3 New
  ├── scholar_verify.py      Semantic Scholar API citation verification
  └── latex_check.py         LaTeX compilation checks

Analysis Tools
  ├── cross_review.py        Cross-paper pattern scanning
  ├── paper_quality.py       4-dimension quality assessment
  ├── score_calibrator.py    TMLR calibrated scoring
  ├── citation_checker.py    Citation accuracy verification
  └── portfolio_health.py    Portfolio health dashboard

Utilities
  ├── dual_submit.py         arXiv + TMLR dual-version generation
  ├── advance_phase.py       6-phase advancement with gate checks
  ├── init_paper.py          Paper skeleton generator
  ├── respond.py             Reviewer response tracker
  └── status.py              Global status dashboard
```

## Rule Tiers

- **Tier 1 (Blocking)**: Must fix before submission. Ghost refs, missing controls, contradictions.
- **Tier 2 (Quality)**: Important for paper quality. Small N, missing CIs, cherry-picking.
- **Tier 3 (Polish)**: Minor refinements. Terminology, figure labels, writing clarity.
- **Defense**: Adversarial patterns. Prepare for hostile reviewer attacks.

## Cross-Paper Tracking

Finds issues in one paper that may exist in others:

```yaml
cross_references:
  - pattern_id: "abstract_too_dense"
    found_in: ["paper_a", "paper_b"]
    propagate_to: ["paper_c"]
```

## TMLR Baseline Comparison

Compares your paper against 5 published TMLR papers:

| Metric | TMLR Median | Loop Engine Result |
|--------|:---:|:---:|
| Datasets | 4 | 8 |
| Models | 3 | 5 |
| Seeds specified | 0% | 100% |
| CI reported | 0% | 100% |
| Effect sizes | 0% | 100% |

## Version History

| Version | Date | Changes |
|---------|------|---------|
| v5.3 | 2026-07-05 | +scholar_verify, +latex_check, 91 rules |
| v5.0 | 2026-07-03 | +submission_audit, +quality_checks (Q1-Q9) |
| v4.0 | 2026-07-02 | Global hub + auto pre-review + TMLR baseline |
| v3.1 | 2026-07-01 | Third-party review + regression testing |
| v2.0 | 2026-06-28 | Multi-round progressive review |
| v1.0 | 2026-06-27 | Single-paper 6-phase pipeline |

## License

MIT
