# Changelog

All notable changes to this repository are documented here. The format follows
[Keep a Changelog](https://keepachangelog.com/en/1.1.0/), and this project adheres to
[Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

- Governance baseline: LICENSE, security policy, code of conduct, contributor and
  support guides, issue and pull-request templates, CODEOWNERS, dependabot, and
  `.editorconfig` added. No research content changed.

## [0.1.0-dev] - 2026-11-16

The labels v4.0 (README, dashboard) and v4.1 (several CLI docstrings) are withdrawn.
They described a six-phase cross-paper review system, a 47-rule book drawn from
real reviews, and TMLR medians. What runs is a six-pattern regular-expression
scan plus hand-written YAML. 0.1.0-dev is the version of that smaller program.
It is not a 1.0 release.

- `make check` runs the scan on committed fixtures, recomputes baseline figures
  from `tmlr_baselines.yaml`, checks rule-entry counts, and fails if `README.md`
  drifts. `.github/workflows/ci.yml` runs it.
- `rulebook.yaml` `stats.total_patterns` was 91. The countable entries are 38
  (7 + 10 + 8 + 4 + 9). The figure 47 added the nine `stats` keys and is not a
  rule count. `total_patterns` is now 38.
- Stored aggregate dataset/model medians (4 and 3) are labeled hand-coded.
  Numeric fields alone median to 4.5 and 3.5. CI 0% and effect-size 0% are the
  stored booleans, not a paper audit. The stored 20% statistical-test rate does
  not match the five rows.
- `pre_review.py --tier 2` and `--tier 3` exit 2. `--tex` and `--json` print the
  checks that exist. The old "minutes saved" line was removed; it was not a
  measurement.
- No acceptance, review decision, or adoption count was added. TMLR-03 is not
  treated as a confirmed acceptance. The TMLR-05 row is still the stale
  anonymous record; see `FAILURE_MODES.md`.
