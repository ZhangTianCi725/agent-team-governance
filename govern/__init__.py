"""agent-team-governance —— 多智能体协作的治理层。

三层：
  ① decision_log  决策可追溯（不可逆决策永久记录 + 证据收据）
  ② rules         行为约束（每条规则都是"会红"的判据，且必须自证可红）
  ③ review        自我审查（反静默失效三判据：新鲜度 / 可达性 / 键匹配）

设计信条：无治理的 Agent 会乱写。治理不是给 Agent 加限制，
而是让它的产出**可追溯、可约束、可证伪**。
"""

from .decision_log import DecisionLog
from .rules import Rule, RuleSet
from .review import ReviewCycle, OutputRecord

__all__ = ["DecisionLog", "Rule", "RuleSet", "ReviewCycle", "OutputRecord"]
__version__ = "0.1.0"
