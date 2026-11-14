# --- acceptance_backfill (EVAL_ACCEPTANCE_STANDARD.md P4) ---
# 原证据来源: audit.py —— 判定为「入口写错」：audit.py 是 argparse CLI，paper_id 是位置
#   必填参数，裸跑只打 help 并 exit 1（rc=2 via make）；`--all` 虽能 exit 0，但 6 篇论文
#   全部打印「❌ Error」而 rc 仍为 0 —— 既不是断言也不是门，用它当 eval 是假的绿。
# 新入口: 仓内真测试套件 tests/test_repo_integrity.py（5 条对真实文件的断言：全部 *.py 字节
#   编译、rulebook.yaml 的 7/10/8 分档、tmlr_baselines.yaml 的 5 条基线、registry.yaml 的
#   6 篇论文、cross_ref.yaml 的跨文规则）。实测 `5 passed`，0.3s。
# 说明: 本仓 CI（.github/workflows/ci.yml）另外跑「全部相对 Markdown 链接可解析」，实测
#   0 条坏链；那一步未并入 eval，需要时手工跑 ci.yml 里的 PY 段。
.PHONY: eval

eval:
	python3 -m pytest tests/ -q
