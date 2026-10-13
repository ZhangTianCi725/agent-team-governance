"""治理第一层 · 决策可追溯。

原则：
  1. 不可逆决策永久记录，谁决策谁写一行。
  2. 每条决策必须带 rationale（理由）—— 没有理由的决策不予记录。
  3. 关键决策可附 evidence（证据收据：命令 / 日期窗 / 可复现步骤）。
     拿不出收据的断言，不算证据。
"""
from __future__ import annotations

import time
from pathlib import Path

from .store import JsonlStore


class DecisionLog:
    def __init__(self, path: str | Path = "data/decisions.jsonl"):
        self.store = JsonlStore(path)
        self._seq = self._max_seq()

    def _max_seq(self) -> int:
        return max((r.get("id", 0) for r in self.store.read_all()), default=0)

    def record(
        self,
        *,
        decided_by: str,
        decision: str,
        rationale: str,
        reversible: bool = True,
        evidence: list[str] | None = None,
    ) -> dict:
        if not rationale or not rationale.strip():
            raise ValueError("rationale 必填 —— 没有理由的决策不予记录")
        self._seq += 1
        rec = {
            "id": self._seq,
            "ts": time.strftime("%Y-%m-%dT%H:%M:%S%z"),
            "decided_by": decided_by,
            "decision": decision,
            "rationale": rationale,
            "reversible": bool(reversible),
            "evidence": evidence or [],
        }
        return self.store.append(rec)

    def all(self) -> list[dict]:
        return self.store.read_all()

    def irreversible(self) -> list[dict]:
        """不可逆决策 —— 最需要审计与人工复核的一类。"""
        return [r for r in self.all() if not r.get("reversible", True)]

    def export_markdown(self, path: str | Path) -> Path:
        path = Path(path)
        lines = ["# 决策日志", "", "| # | 时间 | 决策人 | 决策 | 可逆 |", "|--:|:--|:--|:--|:--:|"]
        for r in self.all():
            lines.append(
                f"| {r['id']} | {r['ts']} | {r['decided_by']} | "
                f"{r['decision']} | {'是' if r['reversible'] else '**否**'} |"
            )
        path.write_text("\n".join(lines) + "\n", encoding="utf-8")
        return path
