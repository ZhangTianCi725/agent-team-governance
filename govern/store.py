"""Append-only JSONL store —— 审计与回溯的地基。

为什么不用普通文件写：
  - 多 Agent 并行时，整份回写会互相覆盖（活文件事故的根因）。
  - 只追加 + 写完回读自证，才能保证"记录 = 事实"。
"""
from __future__ import annotations

import json
import os
import time
from pathlib import Path
from typing import Any


class JsonlStore:
    """只追加（append-only）的 JSONL 存储，带写入自证与崩溃安全重试。"""

    def __init__(self, path: str | os.PathLike):
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)

    # ---------- 写 ----------
    def append(self, record: dict[str, Any]) -> dict[str, Any]:
        line = json.dumps(record, ensure_ascii=False) + "\n"
        with open(self.path, "a", encoding="utf-8") as f:
            f.write(line)
        # 写入自证：回读最后一行，确认"是我的这条"（并发下 >> 也可能丢失）
        self._verify_landed(record)
        return record

    def _verify_landed(self, record: dict[str, Any], retries: int = 3) -> None:
        for _ in range(retries):
            tail = self.tail(1)
            if tail and tail[0] == record:
                return
            time.sleep(0.05)
        raise IOError(
            f"append 未落地：回读末行与写入记录不一致（{self.path}）"
        )

    # ---------- 读 ----------
    def read_all(self) -> list[dict[str, Any]]:
        if not self.path.exists():
            return []
        out: list[dict[str, Any]] = []
        for raw in self.path.read_text(encoding="utf-8").splitlines():
            raw = raw.strip()
            if not raw:
                continue
            try:
                out.append(json.loads(raw))
            except json.JSONDecodeError:
                # 半写帧：跳过坏行而不是整份崩掉
                continue
        return out

    def tail(self, n: int = 1) -> list[dict[str, Any]]:
        return self.read_all()[-n:]

    def __len__(self) -> int:
        return len(self.read_all())
