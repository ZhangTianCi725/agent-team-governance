#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""最小演示：3 个 Agent 协作 + 三层治理。

运行：
    python examples/minimal_team.py

演示内容：
  1) 治理第二层：注册 3 条"会红"的规则，并用正反对照自证规则集有效
  2) 治理第一层：把一次不可逆决策记入决策日志（带证据收据）
  3) 治理第三层：跑一次自我审查，故意喂 1 条"静默失效"的产出并当场逮住它
"""
import os
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from govern import DecisionLog, RuleSet, ReviewCycle, OutputRecord  # noqa: E402

DIVIDER = "─" * 60


def main() -> None:
    print(DIVIDER)
    print("agent-team-governance · 最小演示")
    print(DIVIDER)

    # ── 治理第二层：规则引擎 ───────────────────────────────
    rs = RuleSet()

    @rs.rule("R-001", "产出必须落盘（产出 = 事实流中的一条记录）")
    def _landed(ctx):
        return bool(ctx.get("output_path"))

    @rs.rule("R-002", "任何数值读数必须带时点（无时点的读数不可比）")
    def _has_timestamp(ctx):
        return bool(ctx.get("reading_ts"))

    @rs.rule("R-003", "不可逆动作必须先记入决策日志", severity="error")
    def _logged_if_irreversible(ctx):
        if ctx.get("is_irreversible"):
            return bool(ctx.get("in_decision_log"))
        return True

    # 正反对照：该红的红、不该红的不红
    report = rs.self_test([
        ("合规样本", {"output_path": "out.md", "reading_ts": "2026-01-01", "is_irreversible": False}, set()),
        ("违约: 没落盘", {"output_path": "", "reading_ts": "2026-01-01", "is_irreversible": False}, {"R-001"}),
        ("违约: 无时点读数", {"output_path": "out.md", "reading_ts": "", "is_irreversible": False}, {"R-002"}),
        ("违约: 不可逆未记日志", {"output_path": "out.md", "reading_ts": "t", "is_irreversible": True, "in_decision_log": False}, {"R-003"}),
    ])
    print(f"\n[治理② 规则自证] 规则集可红性校验：{'✅ 通过' if report['ok'] else '❌ 失败'}")
    for d in report["detail"]:
        flag = "✅" if d["pass"] else "❌"
        print(f"   {flag} {d['case']:12s} 期望={d['expected']} 实得={d['got']}")

    # ── 治理第一层：决策日志 ───────────────────────────────
    dlog = DecisionLog("data/demo_decisions.jsonl")
    dlog.record(
        decided_by="orchestrator",
        decision="将 writer 产出的稿子直接发布",
        rationale="三审通过且无未闭环项",
        reversible=False,
        evidence=["review:healthy=true", "rules:self_test.ok=true"],
    )
    print(f"\n[治理① 决策日志] 已记录 {len(dlog.all())} 条 · "
          f"其中不可逆 {len(dlog.irreversible())} 条（带证据收据）")

    # ── 治理第三层：自我审查（反静默失效） ─────────────────
    now = time.time()
    records = [
        # 健康的产出
        OutputRecord(
            name="researcher",
            data_date=now - 1 * 86400,
            keys_available={"code", "date", "value"},
            keys_consumed={"code", "value"},
        ),
        # 故意埋雷：静默失效（键错配 —— 消费了不存在的键）
        OutputRecord(
            name="writer",
            data_date=now - 1 * 86400,
            keys_available={"company_name"},
            keys_consumed={"code", "company_name"},   # code 不存在 ⇒ 查空
        ),
    ]
    review = ReviewCycle(freshness_days=2, now=now).review(records)
    print(f"\n[治理③ 自我审查] 复核 {review['reviewed']} 条产出 "
          f"⇒ {'✅ 全部健康' if review['healthy'] else '🚩 逮到静默失效'}")
    for f in review["findings"]:
        print(f"   🚩 [{f['check']}] {f['agent']}: {f['detail']}")

    print("\n" + DIVIDER)
    print("结论：三条治理各自可执行 —— 规则能红、决策留痕、失效被逮。")
    print(DIVIDER)


if __name__ == "__main__":
    main()
