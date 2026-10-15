# agent-team-governance

[简体中文](README.md) | **English**

[![CI](https://github.com/ZhangTianCi725/agent-team-governance/actions/workflows/ci.yml/badge.svg)](https://github.com/ZhangTianCi725/agent-team-governance/actions/workflows/ci.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Python 3.10+](https://img.shields.io/badge/python-3.10%2B-blue.svg)](https://www.python.org/)
[![dependencies: 0](https://img.shields.io/badge/dependencies-0-brightgreen.svg)](requirements.txt)

📐 [Architecture](ARCHITECTURE.md) · 🧪 [Case Study (3 real incidents)](docs/case-study.md) · ▶️ [Minimal runnable example](examples/minimal_team.py) · ⚖️ [Design creeds](#design-creeds)

> **A governance layer for multi-agent systems — make an agent team's output *traceable, constrained, falsifiable*.**

When multiple LLM agents work together, the real danger is not that they
*can't* do the job — it's that they **do it wrong**: hallucinations, overwriting
each other's results, and *silent failures* (exit code 0, logs showing ✓, but the
output is garbage).

This library distills three battle-tested governance patterns into a
**zero-dependency, runnable minimal skeleton**:

```text
              ┌─────────────────────────────────────────────┐
              │        Agent team (N roles)                 │
              │  researcher │ writer │ reviewer │ ...       │
              └───────────────────┬─────────────────────────┘
                                  │  output (with contract)
      ┌───────────────────────────┼───────────────────────────┐
      │  ① decision_log           │  ② rules                  │  ③ review
      │  traceable decisions      │  behavior constraints     │  self-audit
      │  ─────────────            │  ─────────────            │  ─────────────
      │  irreversible ⇒ logged    │  every rule must "go red" │  freshness
      │  who decides, writes it   │  positive + negative test │  reachability
      │  decisions need evidence  │  violations reported      │  key_match
      └───────────────────────────┴───────────────────────────┴──────────────┘
```

## Why you need it

A single agent is easy: write a clear prompt and you're done.
An **agent team** develops diseases that only multi-agent systems have:

| Disease | Symptom | This library's answer |
|:--|:--|:--|
| **Untraceable** | Something broke — nobody knows who changed what, or why | Decision log: irreversible decisions are permanently recorded, with evidence receipts |
| **Unconstrained** | Agents overstep, overwrite each other's output, write junk | Rule engine: every rule can go red and is self-tested |
| **Silent failure** | Exit code 0, but the output is stale/invalid | Self-audit: three anti-silent-failure criteria |
| **Green-washing** | A check always passes because it can never fail | `RuleSet.self_test()` with positive + negative controls |

## Quick start

No third-party dependencies (standard library only):

```bash
python examples/minimal_team.py
```

You'll see all three layers in action: the rule set proves it *can* go red,
decisions get logged, and silent failures are caught on the spot.

```python
from govern import DecisionLog, RuleSet, ReviewCycle, OutputRecord

# ② behavior constraints
rs = RuleSet()

@rs.rule("R-001", "output must be persisted")
def _landed(ctx): return bool(ctx.get("output_path"))

# ① traceable decisions
dlog = DecisionLog("data/decisions.jsonl")
dlog.record(decided_by="orchestrator", decision="publish the draft",
            rationale="passed all three reviews", reversible=False,
            evidence=["review:healthy=true"])

# ③ self-audit (anti-silent-failure)
report = ReviewCycle(freshness_days=2).review([
    OutputRecord(name="writer", keys_available={"company_name"},
                 keys_consumed={"code", "company_name"}),   # `code` doesn't exist ⇒ query returns empty
])
print(report["findings"])   # catches the key_match failure
```

## Layout

```text
agent-team-governance/
├── govern/
│   ├── store.py          # append-only JSONL store + write-back self-proof
│   ├── decision_log.py   # ① traceable decisions
│   ├── rules.py          # ② behavior constraints (with positive/negative self-test)
│   └── review.py         # ③ self-audit (three anti-silent-failure criteria)
├── roles/                # role definition templates (charter + state + contract)
├── examples/minimal_team.py
├── ARCHITECTURE.md       # design rationale + how the three layers cooperate
└── docs/case-study.md    # real incident post-mortems (root cause → fix → prevention)
```

## Design creeds

1. **A rule must be able to go red** — a check for which you cannot write down
   "the condition under which it fails" is decoration, not governance.
   `self_test()` enforces this with positive and negative controls.
2. **Append only, never overwrite** — when agents run in parallel, whole-file
   rewrites clobber each other. `JsonlStore` only appends, and reads back to
   prove the write landed.
3. **Decisions carry a rationale and evidence** — a decision without a
   `rationale` is rejected outright; key claims must carry a reproducible receipt.
4. **Effectiveness ≠ exit code** — whether an output is valid is decided by the
   freshness / reachability / key-match criteria, not by whether it raised an error.
5. **Falsify proactively** — the point of self-audit is not to prove "I'm right",
   but to find out "I'm wrong" as early as possible.

## Background

These patterns are abstracted from a **single-operator, 5-agent production system**
(data audit / strategy research / sentiment monitoring / execution / team lead)
that has been running unattended for months. The pitfalls it hit — silent
failures, live files getting whole-file rewritten, green-washing checks — the three
post-mortems below are exactly those.

## Case Study — the three layers were reverse-engineered from real incidents

This was not designed first and then given a use case. It was **bitten first**, and the
three layers grew out of the wounds. Each case is written up as
**symptom → root cause → fix → prevention**:

| Case | Symptom | Why it's dangerous | Governing layer |
|:--|:--|:--|:--|
| **① Silent failure** | The system "ran fine" for **13 days** — the output was garbage | Exit code `0`, logs full of ✓ — **nothing raised an alarm**, so nobody looked | ③ `review.py` three criteria (freshness / reachability / key-match) |
| **② Live file overwritten** | A shared log went **327 lines → 191**, silently losing 9 sections | With agents running in parallel, each thinks it is *creating* the file | ① `store.py` append-only + **read-back self-proof** |
| **③ Green-washing check** | A check **always passes** — because it can never fail | Worse than no check at all: it manufactures **false confidence** | ② `rules.py` `self_test()` positive + negative controls |

> What all three share: **none of them cries out on its own.** The job of a governance
> layer is therefore not to make agents smarter, but to **make their failures loud**.

👉 Full post-mortems (timeline, root-cause code, fix commits): [**`docs/case-study.md`**](docs/case-study.md)

## Roadmap

- [x] Three-layer minimal skeleton + runnable demo
- [ ] CLI: `govern init` to scaffold a role
- [ ] Adapters for mainstream agent frameworks (LangGraph / CrewAI)
- [ ] A controlled experiment: governed vs. ungoverned (completion rate / error rate / cost)

## Support

If this project is useful to you, a ⭐ star is appreciated.

## License

[MIT](LICENSE)
