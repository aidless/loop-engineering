# Loop Engineering 0.1.0-dev

[![CI](https://github.com/aidless/loop-engineering/actions/workflows/ci.yml/badge.svg)](https://github.com/aidless/loop-engineering/actions/workflows/ci.yml)

[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)

STATUS: WORK-IN-PROGRESS — not A yet

## Problem

`pre_review.py` runs six hard-coded regular expressions on a local `main.tex` (C1, C4, C9, C7, W4, and abstract number density). It does not load `rulebook.yaml`, and it does not implement Tier-1 rules L1, C6, M1, or M3.
Tier 2, Tier 3, and `cross_ref.yaml` are specs: no committed paper is reviewed by them.
`make check` re-runs that scan on committed fixtures, recomputes what `tmlr_baselines.yaml` can support, and fails if this file drifts.

## 同一主张

`pre_review.py` 只对本地 `main.tex` 跑六条硬编码正则，不读取规则文件。Tier 2、Tier 3 与 `cross_ref.yaml` 是规格，不是已在本仓库执行过的审阅。

## What the numbers are

`rulebook.yaml` has 38 rule entries (tier 1 = 7, tier 2 = 10, tier 3 = 8, defense = 4, tier 2 plus = 9). Adding the `stats` keys to that count was the old figure of 47, and it is not a rule count. `stats.total_patterns` is 38. Annotations that name review rounds or paperreview.ai have no transcripts in this repository.

`tmlr_baselines.yaml` has five hand-coded rows. The numeric medians are 4.5 datasets and 3.5 models, using the two numeric dataset fields and the two numeric model fields. Strings such as "multiple graph benchmarks" are not parsed into numbers. The stored aggregate still says 4 and 3. CI 0% and effect-size 0% are the share of hand-coded `reports_ci: false` and `reports_effect_size: false` flags. They were not verified against the papers. The stored `statistical_tests_reported_pct` of 20 does not match the rows: zero of five name a test. The median of the stored `score_estimated` values is 7.0. Those scores are hand-coded guesses, not venue decisions.

`status.py --all` prints the registry and both figures. It does not open a PDF.

## Gaps that keep this below A

GitHub About still says: 跨论文智能审阅系统（v4.0）：全局中枢＋单论文实例双层架构，六阶段流水线、共享规则库、TMLR 基线对标与 Tier-1 自动预审。

Replace it with: 0.1.0-dev: hard-coded regex pre-review of a local main.tex (six patterns; not the Tier-1 rulebook). Tier 2/3 and cross_ref.yaml are specs. TMLR baseline numbers are hand-coded.

This pull request cannot edit GitHub About. Until that text is replaced, the public description and this file disagree. Known limits of the scan and the baseline file are in [FAILURE_MODES.md](FAILURE_MODES.md), not extra claims.

`init_paper.py` still writes a skeleton whose commands point at `../.loop/status.py`. That directory is not in this repository. `make check` does not cover that command.

## Check

From a fresh clone, after one install (the install needs network; the check does not):

```bash
python3 -m pip install -r requirements.txt
make check
```

`make check` runs `tests/test_honesty_gate.py` and the existing integrity tests, then `eval/run_cases.py`. It needs PyYAML and pytest. It does not download papers.

## Commands that exist

```bash
python3 pre_review.py --tex fixtures/pre_review/trigger.tex --json
python3 status.py --all
```

`pre_review.py --tier 2` and `--tier 3` exit 2. They do not run extra checks.
