# Failure modes

`make check` locks the behavior of the hard-coded scan and the arithmetic of `tmlr_baselines.yaml`. It does not make that scan a review, and it does not audit the papers. Spot-check on 2026-11-16, not re-run by make check.

## n=5 baseline

`tmlr_baselines.yaml` has n=5 hand-coded rows. Dataset and model medians that use only numeric cells are 4.5 and 3.5, because three dataset values and three model values are prose. The stored aggregate (datasets 4, models 3, CI 0%, effect size 0%, score 7.0, statistical tests 20%) is hand-coded. The 20% test rate is not in the rows: every `statistical_tests` value is "none reported" or "not specified".

`our_papers_vs_baseline` says one comparison is "Top 5% of TMLR papers for statistical rigor". A ranking against TMLR cannot be computed from n=5 hand-coded rows. That sentence is unsupported.

The five `score_estimated` values are guesses. Their median is 7.0. No rubric or decision letter is in the repository. They are not TMLR scores.

### What a spot-check could and could not confirm

This pass opened public pages. It did not extract CI or effect-size tables, and it did not change the YAML.

- TMLR-01. The NSF Public Access Repository record 10663435, as returned in this pass, lists "Pitfalls in Evaluating Inference-time Methods for Improving LLM Reliability" by Michael M. Jerge and David Evans in Transactions on Machine Learning Research, with a published date of 2025-06-12. The OpenReview PDF fetched here was still an anonymous review draft, so camera-ready counts were not audited. The public repository `mmjerge/LLM-Evaluation-Framework` summarizes that paper's experiment as 6 methods, 5 models, and 10 benchmarks, which is not the same pair of numbers as `datasets: 6` and `models: 4`. The conflict is unresolved. This check did not re-count the camera-ready PDF.
- TMLR-02. OpenReview forum `VVneIp69GR` shows "Adapting Language Models to Produce Good Class Probabilities for Classification Tasks" by Lautaro Estienne and coauthors, accepted by TMLR, published 2026-02-01. The YAML's `datasets: 3` and `models: "multiple LLMs (3+)"` were not checked against the paper.
- TMLR-03. The YAML title is "An Effective-Rank Audit of Alignment-Induced Activation Shifts" by Nakamura, year 2026. An arXiv preprint (2605.24583, Yuki Nakamura) and a Zenodo record that describes a TMLR submission use related titles. This pass did not find an acceptance page. TMLR-03 is not a confirmed acceptance. Do not cite it as a published TMLR paper on the strength of this file.
- TMLR-04. OpenReview forum `80b2zaeTUe` shows the Platt-scaling paper by Nathan Phelps, Daniel J. Lizotte, and Douglas G. Woolford, accepted by TMLR, published 2025-08-31. The abstract describes a simulation study and a case study, which is the level of the prose field "simulation + real". Counts, confidence intervals, and effect sizes were not extracted.
- TMLR-05. The YAML says "(Anonymous at review time)" and year 2025. PMC13668306 / PMID 42877900 is a 2026 TMLR paper, "Optimized Graph Structures for Calibrating Graph Neural Networks with Out-of-Distribution Nodes", by Weili Shi, Xueying Yang, Xujiang Zhao, Haifeng Chen, Zhiqiang Tao, and Sheng Li. The YAML row is stale. The page reports means and standard deviations over 10 seeds and uses "confidence intervals" for ECE bins. That is not a completed audit of statistical confidence intervals or effect sizes, so the booleans were left as stored.

CI 0% and effect-size 0% remain labels on hand-coded booleans.

## Hand-coded features

Rule text, baseline rows, `cross_ref.yaml`, and `registry.yaml` phase numbers are hand-written. `registry.yaml` points at `../Research/`, which is not in this repository. A phase of "提交就绪" or a self-score in that file is not a review that happened here.

`cross_ref.yaml` is spec data. `cross_review.py` would read it only when those external trees exist. `propagation_log` is not executed.

`rulebook.yaml` comments that mention 3 papers, 11 rounds, or paperreview.ai are unverified annotations. There is no ground-truth reviewer agreement study in this repository.

## Rule false positives and false negatives

The scanner's positive hits on `fixtures/pre_review/`:

- `false_positive_first.tex` contains "First, we describe the setup." C1 reports that ordinal as a novelty claim. That is a false positive.
- `trigger.tex` fires C1, C9, C4, C7, five W4 patterns, and ABSTRACT. C7's message says to verify an enumerated count, but the code only captures the number word (`three`). It does not count items. W4 fires on "prove" with no check that the sentence is a mathematical proof.
- `tier1_gaps.tex` states a missing citation, a headline contradicted later in the file, a confounded comparison, and a mismatched embedding model. The scan returns no hits. L1, C6, M1, and M3 are false negatives: those Tier-1 ids are not implemented.

`--tier 2` and `--tier 3` exit 2. They are not silent no-ops.

## No reviewer agreement

There is no ground-truth reviewer agreement. Nothing in this repository compares scanner output, or the 38 rule entries, to a human reviewer on a shared set of papers. A hit is a regular expression. It is not evidence that a reviewer would raise the same point, or that fixing it would change a decision.
