"""治理第三层 · 自我审查循环（主动证伪）。

Agent 系统最贵的 bug 不是"报错"，是"静默失效"：
退出码 0、日志打着 ✓，但产出其实是废的。所以有效性不能靠退出码，
要靠三条判据（本模块即其实装）：

  ① 新鲜度 freshness   —— 产出的数据日期不得落后今日超过 N 天
  ② 可达性 reachability —— 关键判定式的取值域必须结构可达（否则永远不触发）
  ③ 键匹配 key-match    —— 消费键必须对得上数据键（否则查了个寂寞）

复核后再执行"剔除（sunset）"：对确认失效的项，标记退役而非任其腐烂。
"""
from __future__ import annotations

import time
from dataclasses import dataclass, field


@dataclass
class OutputRecord:
    """一个 Agent 产出的自描述记录。"""
    name: str
    produced_at: float = field(default_factory=time.time)
    data_date: float | None = None          # 数据本身的最新日期
    keys_available: set[str] = field(default_factory=set)
    keys_consumed: set[str] = field(default_factory=set)
    domain: set[str] | None = None          # 判定式实际可取值域（None = 未声明）
    expected_values: set[str] | None = None # 判定式期望出现过的取值
    meta: dict = field(default_factory=dict)


class ReviewCycle:
    def __init__(self, *, freshness_days: int = 2, now: float | None = None):
        self.freshness_days = freshness_days
        self.now = now or time.time()

    # ---- 三判据 ----
    def check_freshness(self, o: OutputRecord) -> dict | None:
        if o.data_date is None:
            return None
        lag_days = (self.now - o.data_date) / 86400
        if lag_days > self.freshness_days:
            return {"check": "freshness", "agent": o.name,
                    "detail": f"数据落后 {lag_days:.1f} 天 > 阈值 {self.freshness_days}",
                    "severity": "error"}
        return None

    def check_reachability(self, o: OutputRecord) -> dict | None:
        # 判定式的取值域若与"期望出现过的取值"完全不相交，则该判定式结构不可达
        if not o.domain or not o.expected_values:
            return None
        if o.domain.isdisjoint(o.expected_values):
            return {"check": "reachability", "agent": o.name,
                    "detail": f"取值域 {sorted(o.domain)} 与期望 {sorted(o.expected_values)} 不相交 ⇒ 判定式永不可达",
                    "severity": "error"}
        return None

    def check_key_match(self, o: OutputRecord) -> dict | None:
        missing = o.keys_consumed - o.keys_available
        if missing:
            return {"check": "key_match", "agent": o.name,
                    "detail": f"消费键 {sorted(missing)} 在数据键中不存在 ⇒ 静默查空",
                    "severity": "error"}
        return None

    def review(self, records: list[OutputRecord]) -> dict:
        findings = []
        for o in records:
            for f in (self.check_freshness(o), self.check_reachability(o), self.check_key_match(o)):
                if f:
                    findings.append(f)
        return {
            "reviewed": len(records),
            "findings": findings,
            "healthy": not findings,
            "ts": time.strftime("%Y-%m-%dT%H:%M:%S%z"),
        }
