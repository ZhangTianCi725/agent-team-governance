# agent-team-governance

**简体中文** | [English](README.en.md)

> **多智能体协作的治理层 —— 让一个 Agent 团队的产出「可追溯、可约束、可证伪」。**
>
> A governance layer for multi-agent systems: *traceable, constrained, falsifiable.*

让多个 LLM Agent 协作，最危险的不是"它们不会做"，而是**它们乱做** ——
幻觉、互相覆盖、静默失效（退出码 0、日志打着 ✓，产出却是废的）。

这个库把三个被验证过有效的治理模式，做成了**开箱即用的最小骨架**：

```text
              ┌─────────────────────────────────────────────┐
              │            Agent 团队（N 个角色）             │
              │   researcher │ writer │ reviewer │ ...      │
              └───────────────────┬─────────────────────────┘
                                  │  产出（带契约）
        ┌─────────────────────────┼─────────────────────────┐
        │   ① decision_log        │   ② rules               │   ③ review
        │   决策可追溯            │   行为约束              │   自我审查
        │   ─────────────         │   ─────────────         │   ─────────────
        │   不可逆决策永久记录    │   每条规则必须"会红"    │   新鲜度 freshness
        │   谁决策谁写一行        │   正反对照自证有效      │   可达性 reachability
        │   决策必带证据收据      │   违例当场落报告        │   键匹配 key_match
        └─────────────────────────┴─────────────────────────┴─────────────────────────┘
```

## 为什么需要它

单个 Agent 的问题是好解决的：prompt 写清楚就行。
但**一个 Agent 团队**会出现只有多体系统才有的病：

| 病 | 症状 | 本库的解法 |
|:--|:--|:--|
| **不可追溯** | 出了问题不知道谁改的、为什么改 | 决策日志：不可逆决策永久记录 + 证据收据 |
| **行为失控** | Agent 越界、覆盖别人的产物、乱写 | 规则引擎：每条规则可红、可自证 |
| **静默失效** | 退出码 0，产出却是废的 | 自我审查：反静默失效三判据 |
| **假绿判据** | 检查永远通过，因为判据根本不会红 | `RuleSet.self_test()` 正反对照 |

## 快速开始

无需任何第三方依赖（纯标准库）：

```bash
python examples/minimal_team.py
```

你会看到三个治理层各自生效：规则集自证可红、决策留痕、静默失效被当场逮住。

```python
from govern import DecisionLog, RuleSet, ReviewCycle, OutputRecord

# ② 行为约束
rs = RuleSet()

@rs.rule("R-001", "产出必须落盘")
def _landed(ctx): return bool(ctx.get("output_path"))

# ① 决策可追溯
dlog = DecisionLog("data/decisions.jsonl")
dlog.record(decided_by="orchestrator", decision="发布稿子",
            rationale="三审通过", reversible=False, evidence=["review:healthy=true"])

# ③ 自我审查（反静默失效）
report = ReviewCycle(freshness_days=2).review([
    OutputRecord(name="writer", keys_available={"company_name"},
                 keys_consumed={"code", "company_name"}),   # code 不存在 ⇒ 查空
])
print(report["findings"])   # 逮到 key_match 失败
```

## 目录结构

```text
agent-team-governance/
├── govern/
│   ├── store.py          # append-only JSONL 存储 + 写入自证
│   ├── decision_log.py   # ① 决策可追溯
│   ├── rules.py          # ② 行为约束（含正反对照自证）
│   └── review.py         # ③ 自我审查（反静默失效三判据）
├── roles/                # 角色定义模板（说明书 + 状态 + 契约）
├── examples/minimal_team.py
└── docs/case-study.md    # 真实故障复盘（根因 → 修法 → 防复发）
```

## 设计信条

1. **规则必须会红** —— 写不出"什么情况下它会失败"的检查，是装饰不是治理。`self_test()` 用正反对照强制这一点。
2. **只追加，不覆盖** —— 多个 Agent 并行时，整份回写会互相覆盖。`JsonlStore` 只追加，且写完**回读自证**。
3. **决策必带理由与证据** —— 没有 rationale 的决策不予记录；关键断言必须带可复现的收据。
4. **有效性 ≠ 退出码** —— 产出是否有效，要用新鲜度 / 可达性 / 键匹配三条判据去查，而不是看它有没有报错。
5. **主动证伪** —— 自我审查的目的不是"证明我对"，是"尽早发现我错"。

## 背景

这套治理模式抽象自一个**单人运维的 5-Agent 生产系统**（数据审计 / 策略研究 /
舆情监控 / 执行 / 主管），已连续无人值守运行数月。踩过的坑（静默失效、活文件被整份
回写、假绿判据）都写进了 [`docs/case-study.md`](docs/case-study.md)。

## Roadmap

- [x] 三层治理最小骨架 + 可运行 demo
- [ ] CLI：`govern init` 生成角色骨架
- [ ] 与主流 Agent 框架（LangGraph / CrewAI）的适配示例
- [ ] 治理 vs 无治理的对照实验（任务完成率 / 错误率 / 成本）

## License

[MIT](LICENSE)
