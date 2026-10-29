# CStack 插件 Agent

本目录是 Claude Code 插件可直接派发的 subagent 定义。Claude Code 会按每个文件的 `description` 自动委派，也可以在 Task 工具里按 `name` 指定。

| Agent | 主要用途 | 工具边界 |
| --- | --- | --- |
| `cstack-explorer` | 只读事实调查，回传结论 + 证据 + 未知 | 只读 + 只读 Bash |
| `cstack-implementer` | 在授权写范围内实现候选并自检 | 读 + 写 + Bash |
| `cstack-verifier` | 按 `R#`/`AC#` 独立判断，写 `EVIDENCE` | 只读 + Bash |
| `cstack-reviewer` | 审查 diff，报告缺陷与影响 | 只读 + Bash |
| `cstack-simplifier` | 收尾时找多余复杂度 | 只读 + Bash |
| `cstack-researcher` | 查仓库外的官方资料与版本信息 | 读 + Web + Bash |
| `cstack-architect` | design-it-twice，给出 2–3 个结构候选 | 只读 + Bash |

角色契约的权威定义在 [`../skills/cstack-core/ROLES.md`](../skills/cstack-core/ROLES.md)；本目录是它在 Claude Code 上的可执行实现。

## 为什么没有 Orchestrator

Claude Code 的 subagent 不支持再派 subagent，所以 `cstack-orchestrator` 不提供可执行文件，只保留在 `ROLES.md` 的契约里。多切片编排由主 Agent 配合 `cstack-slice` / `cstack-wayfinding` 完成；其他支持嵌套派发的 Runtime 可以按契约自行实现。

## 其他 Runtime

Codex、ZCode 等如果不读取 Claude Code 的 `agents/*.md`，以 `ROLES.md` 契约为准，用该 Runtime 的等价机制实现同样的输入、禁止项和输出结构。没有独立实例能力时按契约降级，不能伪造独立验证。

## 独立性

- `cstack-implementer` 与 `cstack-verifier` / `cstack-reviewer` 必须是不同的执行身份。
- `cstack-verifier` 必须先独立得出预期，再看实现。
- `cstack-reviewer` 不替代逐 AC 验收。
- 只读 Agent 不得修改产品代码、仓库测试或需求。
