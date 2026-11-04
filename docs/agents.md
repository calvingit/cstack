# Agent 角色

> 角色契约的完整定义见 [ROLES.md](../plugins/cstack/skills/cstack-core/ROLES.md)，角色模型的设计取舍见[设计思想 · 角色模型](design.md#7-角色模型)。

## 四个概念

**Skill**（方法：输入、步骤、停止条件、输出产物）、**Role**（责任契约：谁负责这项判断）、**Agent instance**（一次具体执行，可在同一上下文，也可用独立实例）、**Invocation policy**（谁能启动它）。四者需要分开看待，不能混为一谈。

## 核心与可选角色

[ROLES.md](../plugins/cstack/skills/cstack-core/ROLES.md) 定义 5 个核心角色（Explorer、Implementer、Verifier、Reviewer、Simplifier）和 3 个可选角色（Researcher、Architect、Orchestrator）。

默认单 Agent；上下文隔离、独立性或并行有实际收益时，才派独立实例。

## 可派发的子代理

插件根目录的 [agents/](../plugins/cstack/agents/) 提供 Claude Code 可直接派发的 subagent 定义。Claude Code 可根据 `description` 自动委派，也可在 Task 工具中按 `name` 指定。GitLab 插件另有 [gitlab-reviewer](../plugins/gitlab/agents/gitlab-reviewer.md)。

| Agent | 主要用途 | 工具边界 |
| --- | --- | --- |
| `cstack-explorer` | 只读事实调查，回传结论、证据和未知项 | 只读工具 + 只读 Bash |
| `cstack-implementer` | 在授权写范围内实现候选并自检 | 读 + 写 + Bash |
| `cstack-verifier` | 按 `R#` / `AC#` 独立判断，写 `EVIDENCE` | 只读 + Bash |
| `cstack-reviewer` | 审查 diff，报告缺陷与影响 | 只读 + Bash |
| `cstack-simplifier` | 可选：收尾时查找多余复杂度 | 只读 + Bash |
| `cstack-researcher` | 查阅仓库外的官方资料与版本信息 | 读 + Web + Bash |
| `cstack-architect` | 对设计提出 2–3 个结构候选 | 只读 + Bash |
| `gitlab-reviewer` | 只读评审 GitLab MR，取 diff、查证据、给分级发现 | 只读 + Bash |

## 独立性规则

- **Implementer 不写 `EVIDENCE`**，自检只是候选记录。
- **Verifier 与 Reviewer 是两种判断**：验收条件是否满足 vs 变更引入了什么缺陷，不能合并成一份结论。任务收尾两者都必须实际运行；未运行不等于通过。Simplifier 可以不派。
- **预期来源独立 ≠ 执行者独立**：Verifier 必须先依据已确认的验收条件独立得出预期，再看实现。默认允许在同一上下文完成验证；涉及高风险、权限、数据或迁移，或项目明确提出要求时，须使用独立实例。
- **Reviewer 与 Implementer 分离**：要求独立执行者时，Implementer 不能同时担任 Verifier 或 Reviewer。
- **只读 Agent 不得修改**产品代码、仓库测试或需求。
- **角色不是越多越好**：只有隔离、独立性或并行有实际收益时才派独立实例。

## 并行与 Orchestrator

Claude Code 的 subagent 不支持嵌套派发，因此 Orchestrator 由主会话承担，不提供可执行 Agent 定义。多切片并行实现由 [cstack-orchestrate](../plugins/cstack/skills/cstack-orchestrate/SKILL.md) 规定主会话如何派发 Implementer、Verifier、Reviewer 和 Simplifier 并按依赖合并收口。

其他 Runtime 可按角色契约使用等价机制；没有独立实例能力时按契约降级，不能伪造独立验证。

并行只发生在实现阶段，且只在切片互不阻塞、写入可隔离（`git worktree`）时成立。验收和审查仍是独立实例的判断，在合并后的单一候选上执行，不能按切片拼接，也不能按通过的切片数推断结论。
