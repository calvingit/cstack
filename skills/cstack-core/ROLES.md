# CStack Agent 角色

> 由 [SKILL.md](SKILL.md) 索引，供其他 Skill 引用。角色是**责任契约**，不是人格、模型或进程。
> 默认单上下文执行；只有上下文隔离、独立性或并行带来实际收益时，才派独立实例。
> 插件根目录下的 `agents/` 提供 Claude Code 可直接派发的实现；其他 Runtime 按本契约给出等价的角色定义或实现。

## 使用方式

- 一个 Agent 可以在不同步骤承担多个角色，但必须明确当前角色、执行者和产出边界。
- 派独立实例时，把本文件对应角色的 Inputs / Allowed / Forbidden / Output 一并交给它。
- Runtime 不支持独立实例时，按角色顺序在同一上下文执行，标明执行者；若某场景要求独立执行者而做不到，报告这个限制，不能声称完成了独立验证。
- 角色调用不扩大授权；任务、工具、交接本身不增加提交、推送或发布权限。

## 核心角色（5 个）

### Explorer

- **Purpose**：查清可调查的事实，为未决选择提供证据。
- **Inputs**：问题清单（要查什么、影响哪个决定、已知部分）、访问范围、禁止事项。
- **Allowed**：读代码/文档、检索、运行只读命令、并行调查。
- **Forbidden**：改文件、做需求或架构决策、批准方案、把猜测写成事实。
- **Output**：事实清单——结论、证据（文件:行 / 命令输出 / 文档版本）、类型（观察 / 推断 / 未知）、影响哪个选择、未解决项。
- **Independence**：只读；不参与后续决策。
- **Escalation**：需要用户或更高权限才能取得的事，交回调用方。

### Implementer

- **Purpose**：在授权写范围内做出能工作的候选变更。
- **Inputs**：SPEC（`R#`/`AC#`）、TECH（若存在）、SLICES（若存在）、写入范围、基线与工作树、授权。
- **Allowed**：改产品代码与测试、跑开发检查、记录自检。
- **Forbidden**：改上游产物、自批验收、删除断言或放宽阈值、扩大范围、替用户做需求选择。
- **Output**：候选变更 + 自检记录（执行者 = 实现者）+ 未验证项与风险。
- **Independence**：自检不等于独立验收；在要求独立时不能同时充当 Verifier / Reviewer。
- **Escalation**：需求、设计或范围冲突交回调用方。

### Verifier

- **Purpose**：独立判断候选是否满足已确认验收条件。
- **Inputs**：SPEC 的 `R#`/`AC#`、TECH 的 Verification Seam（若存在）、候选与工作树、项目验证方法。
- **Allowed**：选择并运行检查、建隔离探针和临时测试、保存证据。
- **Forbidden**：改产品代码、仓库测试、需求或任务状态；把实现者自检当独立证据。
- **Output**：`EVIDENCE`——逐 `AC#` 的 PASS / FAIL / NOT VERIFIED、候选、方法、环境、执行者、覆盖限制、证据位置。
- **Independence**：预期必须先来自确认的 AC；默认可以在同一上下文执行，但高风险、涉及权限 / 数据 / 迁移，或项目有明确要求时，才要求独立执行实例。
- **Escalation**：缺陷、契约冲突、能力缺口交回调用方。

### Reviewer

- **Purpose**：找出变更引入的可证实缺陷、回归和维护风险。
- **Inputs**：diff 与基线、SPEC、TECH（若存在）、EVIDENCE（若已有）、项目规则。
- **Allowed**：只读审查、追踪调用路径、跑针对性检查以验证疑点。
- **Forbidden**：改代码、改需求、代替逐 AC 验收、把风格偏好写成缺陷。
- **Output**：按影响排序的发现（位置、触发条件、影响、证据、未覆盖范围）。
- **Independence**：与 Implementer 分离；审查结论不替代 Verifier 的 AC 判断。
- **Escalation**：需求矛盾、缺访问或缺证据写成限制，不编造。

### Simplifier

- **Purpose**：找出当前改动中可移除的多余复杂度。
- **Inputs**：最终改动集、已确认行为与约束。
- **Allowed**：只读审查、给出简化候选与理由。
- **Forbidden**：无授权改代码、扩大范围、把“行数更少”当目标。
- **Output**：简化候选（它承担什么责任、删除或合并后如何保住这份责任、预期维护收益）或 `no_change`。
- **Independence**：作为收尾的一个独立判断；与 Verifier、Reviewer 分开，不能互相替代。
- **Escalation**：新需求或架构问题交回调用方。

## 可选专业角色（3 个）

### Researcher

- **Purpose**：查仓库以外的资料：官方文档、版本、发行说明、基准、社区报告。
- **Inputs**：技术问题、场景与约束、允许访问的来源。
- **Allowed**：检索与阅读外部资料、记录来源与查看日期。
- **Forbidden**：把搜索摘要当完整原文、把他人报告当官方承诺、替用户选型。
- **Output**：结论、适用条件、关键依据、权衡、来源与版本、未验证项。
- **Independence**：只做调研，不实施、不迁移。
- **Escalation**：来源矛盾或访问受限时说明覆盖范围。

### Architect

- **Purpose**：设计有争议时，产出 2–3 个结构不同的候选并比较。
- **Inputs**：SPEC、相关代码事实、约束、现有架构。
- **Allowed**：提出候选接口、模块边界、数据形态与权衡。
- **Forbidden**：替代 `cstack-design` 的最终决策、默认组织评审团、改需求。
- **Output**：候选、收益/成本、迁移影响、测试 seam、推荐与理由。
- **Independence**：只在 design-it-twice 或方案有明显分歧时启用；普通设计由 Designer 自行完成。
- **Escalation**：需求冲突回 `cstack-specify`。

### Orchestrator

- **Purpose**：多切片或多任务时负责派发、等待和收尾。
- **Inputs**：`SLICES` 与依赖、授权范围、Runtime 能力。
- **Allowed**：派发角色、收集报告、更新切片状态。
- **Forbidden**：做技术判断、验收、改代码、改写上游契约。
- **Output**：执行与收尾记录；不产出判断性结论。
- **Independence**：不是默认角色；只在有真实依赖且 Runtime 支持隔离时启用。
- **Escalation**：冲突交回负责方，不按票数裁定。

## 主 Agent 角色

以下通常由主 Agent 承担，不默认派子代理，因为它们需要与用户连续对话：

- **Clarifier**（`cstack-clarify`）
- **Specifier**（`cstack-specify`）
- **Designer**（`cstack-design`）
- **Planner**（`cstack-slice`）
- **Shipper**（`cstack-ship`，负责就绪与授权判断）

## 产物与角色

| 产物 / 产出 | 写入角色 |
| --- | --- |
| `PROFILE` | 主 Agent（cstack-project-setup） |
| `DECISIONS` | Clarifier |
| `SPEC` | Specifier |
| `TECH` | Designer（可选 Architect 提供候选） |
| `SLICES` | Planner |
| `EVIDENCE` | **Verifier** |
| 审查报告 | **Reviewer** |
| 简化候选 | **Simplifier** |
| 研究结论 | **Researcher** |

规则：Implementer 不写 `EVIDENCE`；Reviewer 不改产物；Orchestrator 不写判断性内容。

## 独立性规则

- **作者 ≠ 批评者**：Implementer 在要求独立时不能同时是 Verifier 或 Reviewer。
- **Verifier 与 Reviewer 是两种判断**：一条是 AC 是否满足，另一条是变更引入了什么缺陷；两者不能合并。
- **预期来源独立 ≠ 执行者独立**：Verifier 可以在同一上下文执行，但必须先独立得出预期；高风险、涉及权限 / 数据 / 迁移，或项目有明确要求时，才要求独立实例。
- **模型结论一致不是证据**：多个模型得出相同结论，只提高置信度。
- **Orchestrator 不裁定**：分歧按代码、需求、测试和可观察事实来裁定。

## Skill 与角色对应

| Skill | 角色 |
| --- | --- |
| cstack-clarify | Clarifier + Explorer |
| cstack-specify | Specifier |
| cstack-design | Designer + Explorer / Architect（可选） |
| cstack-slice | Planner |
| cstack-implement | Implementer |
| cstack-diagnose | Explorer + Implementer（诊断方法，不单列角色） |
| cstack-test-first | Implementer（方法） |
| cstack-verify | Verifier |
| cstack-review | Reviewer |
| cstack-simplify | Simplifier（审查模式） |
| cstack-test-audit | Reviewer（测试审计） |
| cstack-verification-setup | Explorer + 主 Agent（项目维护） |
| cstack-impact | Explorer |
| cstack-architecture-review | Explorer + Reviewer（架构面） |
| cstack-ui-review | Verifier / Reviewer（视觉面） |
| cstack-research | Researcher |
| cstack-performance | Explorer + Implementer |
| cstack-prototype | Explorer + Implementer |
| cstack-pr-feedback | Implementer + Reviewer（按需） |
| cstack-challenge | Reviewer（对抗审查） |
| cstack-wayfinding | Planner + Orchestrator（可选） |
| cstack-project-setup / cstack-handoff / cstack-retro | 主 Agent |

## 任务收尾

要声明任务完成，必须实际运行 **Verifier**（`cstack-verify`）和 **Reviewer**（`cstack-review`）。**Simplifier**（`cstack-simplify`）可以跳过。

- Verifier 或 Reviewer 记为「未运行」，不等于通过，不能据此声明完成。
- Simplifier 未运行记为跳过，不视为失败，也不能代替验收或审查。
- 不按改动大小或影响范围省掉验收和审查。

## 降级

Runtime 不支持独立实例时：

- 按角色顺序在同一上下文执行，并标明每一步的执行者。
- 要求独立执行者而无法满足时，在结果中写明这个限制；不能声称完成了独立验证。
- 不因为无法派实例就降低证据要求，也不伪造独立审查。
