# Artifact-chain v0

一个最小检查：验证 `DECISIONS → SPEC → TECH → SLICES → EVIDENCE` 的引用是否闭合。它检查语义关系，不规定产物格式——真实产物可以是会话、Markdown、issue 或 PR 描述；`sample.json` 只是为了能自动校验，不是模板。

## 运行

```bash
python3 evals/artifact-chain-v0/check_chain.py
```

会检查：

- 决定 ID 唯一；`R#` 的来源是已确认的 `C#`；`AC#` 的来源是存在的 `R#`。
- 每条 `R#` 至少有一个 `AC#`；每条 `AC#` 有且只有一条 `EVIDENCE` 结论。
- 每个 `D#` 有依据（`R#` / `AC#` 或 `code:` 代码事实）；切片 covers 的引用存在。
- 切片 `blocked_by` 引用存在、无自阻塞、无环；切片本地 AC 不重复。
- `PASS` 必须带方法、环境、执行者；未决 `C#` 必须在 SPEC 的未决项中保留。
- `EVIDENCE` 记录候选 HEAD 与工作树状态。

## 限制

这是产物链的引用检查，不是模型行为评测，也不证明 Skill 触发率或跨 Runtime 兼容性。后续应加入真实任务与失败注入（见 [提升方案 §7](../../docs/skill-upgrade-2026-10-29.md)）。
