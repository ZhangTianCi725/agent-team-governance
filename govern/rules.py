"""治理第二层 · 行为约束（规则引擎）。

核心信条 —— 一条好的规则必须**会红**：
  - 写不出"什么情况下它会触发（=失败）"的规则，是装饰，不是治理。
  - 每条规则都必须在正对照（必违例样本）下真的红一次，才算"可红"。

RuleSet.self_test() 就是把这个信条变成可执行的动作：
用正反对照样本验证规则集 —— 该红的红、不该红的不红。
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable


@dataclass
class Rule:
    id: str
    description: str
    check: Callable[[dict], bool]      # 返回 True = 通过；False = 违例
    severity: str = "error"            # error | warn

    def violated(self, ctx: dict) -> bool:
        return not self.check(ctx)


class RuleSet:
    def __init__(self):
        self._rules: dict[str, Rule] = {}

    def register(self, rule: Rule) -> Rule:
        self._rules[rule.id] = rule
        return rule

    def rule(self, id: str, description: str, severity: str = "error"):
        """装饰器写法：@rs.rule("R-001", "输出必须落盘")"""
        def deco(fn: Callable[[dict], bool]):
            self.register(Rule(id, description, fn, severity))
            return fn
        return deco

    def evaluate(self, ctx: dict) -> list[dict]:
        """返回违例清单（空 = 合规）。"""
        return [
            {"id": r.id, "description": r.description, "severity": r.severity}
            for r in self._rules.values()
            if r.violated(ctx)
        ]

    def satisfies(self, ctx: dict) -> bool:
        return not self.evaluate(ctx)

    def self_test(self, cases: list[tuple[str, dict, set[str]]]) -> dict:
        """探针自证（正反对照）。

        cases: [(标签, 上下文, 期望触发的规则 id 集合)]
        返回: {"ok": bool, "detail": [...]}
        —— 校验规则集"该红的红、不该红的不红"。
        """
        detail, ok = [], True
        for label, ctx, expected in cases:
            got = {v["id"] for v in self.evaluate(ctx)}
            passed = got == set(expected)
            ok = ok and passed
            detail.append({"case": label, "expected": sorted(expected),
                           "got": sorted(got), "pass": passed})
        return {"ok": ok, "detail": detail}
