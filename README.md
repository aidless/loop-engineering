# Loop Engineering v4.0

[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)

> 从单论文循环到跨论文智能审阅系统

## 设计理念

**问题**: 每篇论文从零开始审阅，发现的模式无法跨论文复用。

**方案**: 本仓库即全局中枢——存放可复用规则、TMLR 基线、跨论文关联；每个论文实例的工作目录由 `registry.yaml` 登记。工具脚本全部位于仓库**根目录**（更早的版本把它们放在 `.loop/` 下，该目录已不存在）。

## 快速开始

```bash
# 查看全部论文状态
python status.py --all

# 初始化新论文
python init_paper.py my_paper "My Paper Title" --venue TMLR

# 对新论文运行自动预审阅
python pre_review.py my_paper

# 推进论文阶段（带前置条件校验）
python advance_phase.py my_paper

# 交互式回复审稿意见
python respond.py PAPER-A
```
> 注意：当前 `pre_review.py` 仅实现 Tier 1（内置硬编码检查）；`--tier 2/3` 与 `--json` 为预留接口，`rulebook.yaml` 暂未接入脚本。

## 目录结构

```
loop-engineering/
├── *.py                            ← 全部工具在仓库根目录（不在 .loop/ 下）
│   ├── status.py                   ← 全局仪表盘 + TMLR 基线对比
│   ├── pre_review.py               ← 自动预审阅扫描器（Tier 1）
│   ├── init_paper.py               ← 论文骨架初始化器
│   ├── advance_phase.py            ← 阶段推进
│   ├── respond.py                  ← 审稿回复工具
│   ├── agent_review.py / cross_review.py / review_engine.py
│   ├── audit.py / submission_audit.py / paper_quality.py
│   ├── citation_checker.py / scholar_verify.py / latex_check.py
│   └── portfolio_health.py / quality_checks.py / dual_submit.py
├── registry.yaml                   ← 论文注册表
├── rulebook.yaml                   ← 可自动化审阅规则
├── tmlr_baselines.yaml             ← TMLR 已发表论文基线
├── cross_ref.yaml                  ← 跨论文模式关联
├── templates/phase_template.yaml
├── snapshots/                      ← 历史健康快照（append-only）
└── reviews/ reports/ docs/         ← 产出与说明
│
└── PAPER_B/ ...
```

## 五个核心工具

| 工具 | 命令 | 功能 |
|------|------|------|
| `status.py` | `python status.py --all` | 全局仪表盘 + TMLR 基线对比 |
| `init_paper.py` | `python init_paper.py ID "Title"` | 一键生成论文骨架 |
| `pre_review.py` | `python pre_review.py ID` | 自动扫描 Tier 1 规则（7类阻断问题） |
| `respond.py` | `python respond.py ID` | 交互式审稿回复，逐条标记 resolved |
| `advance_phase.py` | `python advance_phase.py ID` | 校验前置条件后推进阶段 |

## 六阶段流水线

```
Phase 0 (基线评估) → Phase 1 (格式转换) → Phase 2 (内容审阅★)
  → Phase 3 (润色) → Phase 4 (匿名化) → Phase 5 (提交就绪)
```

每个 Phase 有前置条件、退出标准、最大轮次限制。

## 审阅规则库

从 3 篇论文的 11 轮审阅中提取，分三个 Tier：

- **Tier 1 (阻断)**: 7 条 — C1首次声称、L1遗漏文献、C6内部矛盾、M1混淆变量...
- **Tier 2 (高优)**: 10 条 — L2孤儿引用、S3效应量缺失、S4多重比较...
- **Tier 3 (润色)**: 8 条 — 术语一致性、图表完整性、写作质量...

完整规则以 `rulebook.yaml` 为准；82 条的完整清单条目（`rulebook_full.yaml`）尚未入库——已知缺口，不作声明。

## TMLR 基线对标

5 篇已发表 TMLR 论文的关键特征已收录。自动对比你的论文在统计 rigor、数据集规模、CI/效应量报告等方面与 TMLR 中位数的差距。

## 添加新论文

```bash
# 1. 初始化
python init_paper.py my_paper "Title" --venue TMLR

# 2. 写论文 (编辑 main.tex)

# 3. 运行预审阅
python pre_review.py my_paper

# 4. 修复问题后推进阶段
python advance_phase.py my_paper
```

## 添加新规则

编辑 `rulebook.yaml`，在对应 Tier 下添加新条目：

```yaml
  NEW_rule_id:
    id: NEW
    category: claim_evidence
    description: "What to check"
    auto_check: "grep for 'pattern'"
    severity: critical
```

## 版本历史

| 版本 | 日期 | 变更 |
|------|------|------|
| v4.0 | 2026-07-02 | 全局中枢 + 自动预审阅 + TMLR对标 + 审稿回复追踪 |
| v3.1 | 2026-07-01 | 第三方审阅 + 回归测试 + Git自动提交 |
| v2.0 | 2026-06-28 | 多轮递进式审阅 (快速→深度→对抗→冷重启→终审) |
| v1.0 | 2026-06-27 | 单论文6阶段循环 |
