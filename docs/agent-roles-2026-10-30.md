# CStack Agent 角色设计（提案）

> 日期：2026-10-30
> 状态：已确认采用 5 核心 + 3 可选，角色定义落在 [`skills/core/ROLES.md`](../skills/core/ROLES.md)；Claude Code 可直接派发的实现见插件根 [`agents/`](../agents/README.md)。
> 关联：[CStack Skills 提升方案](skill-upgrade-2026-10-29.md)、[产物链与独立性设计](artifact-spine-2026-10-29.md)。

## 0. 结论

1. **需要角色，但不需要默认的多 Agent 编排。** 角色是“谁以什么边界执行哪个判断”的责任契约，不是人格、模型或进程。
2. 采用 **5 个核心角色**：Explorer、Implementer、Verifier、Reviewer、Simplifier。
3. 保留 **3 个可选专业角色**：Researcher、Architect、Orchestrator。
4. 角色定义放在 `core/ROLES.md`，由 `SKILL.md` 索引；各 Skill 只引用自己需要的角色。默认单上下文执行；只有收益明确或独立性要求时才派独立实例。

## 1. 先分清四件事

| 概念 | 例子 | 说明 |
| --- | --- | --- |
| **Skill（方法）** | `verify` | 一套判断程序：输入、步骤、停止条件、输出槽位 |
| **Role（责任）** | Verifier | 谁负责这项判断，允许做什么、禁止做什么、产出什么 |
| **Agent instance（执行实例）** | 一个 subagent / 独立上下文 | 角色的一次具体执行；可以同上下文，也可以独立 |
| **Invocation policy（调用策略）** | `allow_implicit_invocation: false` | 谁能启动：用户、调用方、模型自动发现 |

CStack 现有 Skill 已经定义了“方法”，缺的是方法的**执行身份与独立性边界**。角色就是补这一层，不是再加一套流程。

## 2. 为什么需要角色

- **上下文隔离**：Explorer 读大量文件、日志和调用链，把结果压缩成事实清单，避免主上下文被淹没。
- **独立性**：Implementer 不验收自己的活；Verifier 与 Reviewer 是不同判断，不能互相替代。
- **并行**：多个互不相交的调查、研究或切片可以并行，但不需要默认打开。
- **成本约束**：角色不是越多越好。默认单 Agent；只有“隔离、独立性、并行”三者之一带来实际收益时才派独立实例。

这也是与 pstack 的区别：**吸收角色的职责边界，不吸收它的模型路由、并行编排和固定 playbook 顺序。**

## 3. 核心角色（5 个）

| 角色 | 对应 Skill | 输入 | 允许 | 禁止 | 输出 | 何时独立实例化 |
| --- | --- | --- | --- | --- | --- | --- |
| **Explorer** | clarify / design / impact / diagnose 的调查部分 | 问题清单、访问范围、禁止事项 | 读代码/文档、跑只读命令、检索 | 改文件、做需求决策、批准方案 | 事实清单：结论、证据、观察/推断/未知、未解决项 | 事实面广或会淹没主上下文时；单文件小查询不必 |
| **Implementer** | implement（含 ticket 级实现） | SPEC / TECH / SLICES、写入范围、授权 | 在写范围内改代码与测试、跑开发检查 | 改上游槽位、自批验收、扩权 | 候选变更 + 自检记录（执行者=实现者） | 作为写作用域的默认执行者；与 Verifier/Reviewer 分离 |
| **Verifier** | verify | SPEC 的 `R#`/`AC#`、候选、验证方法 | 独立选择并运行检查、建隔离探针 | 改产品/仓库测试/需求、调度、改状态 | `EVIDENCE`：逐 AC 的 PASS/FAIL/NOT VERIFIED + 候选/环境/执行者/限制 | 有完成声明时必须有；高风险或要求执行者独立时用独立实例 |
| **Reviewer** | review | diff、SPEC、TECH、EVIDENCE | 只读审查、追踪调用路径、跑针对性检查 | 改代码、改需求、代替逐 AC 验收 | 按影响排序的缺陷报告 + 证据 + 未覆盖范围 | 非平凡变更时；与 Implementer 分离 |
| **Simplifier** | simplify（审查模式） | 最终改动集、约束 | 只读审查复杂度、给候选 | 无授权就改代码、扩大范围 | 简化候选与理由；无候选也有效 | 收尾 full tier 默认；与 Verifier/Reviewer 分开 |

## 4. 可选专业角色（3 个）

| 角色 | 用途 | 何时启用 | 不做什么 |
| --- | --- | --- | --- |
| **Researcher** | 查仓库以外的资料：官方文档、版本、发行说明、基准、社区报告 | 技术选型、版本/兼容性判断、外部 API 行为 | 不做代码事实调查（交给 Explorer），不替用户选型 |
| **Architect** | 设计有争议时，产出 2–3 个结构不同的候选并比较 | 需要 design-it-twice、接口方案有明显分歧 | 不替代 `design` 的最终决策；不默认组评审团 |
| **Orchestrator** | 多切片/多任务时负责派发、等待与收尾编排 | 存在 `SLICES` 且有真实依赖，Runtime 支持隔离 | 不做技术判断、不验收、不改代码；不是默认角色 |

**Diagnostician 不单列。** 诊断是 `diagnose` 这套方法；执行时通常由 Implementer 承担，调查部分可派 Explorer。只有疑难、非确定性 bug 需要独立专注时，才临时按“Explorer + Implementer”组合，而不是新增常驻角色。

## 5. 角色与产物槽位的所有权

| 产物槽位 | 写入者 |
| --- | --- |
| `PROFILE` | setup（项目档案） |
| `DECISIONS` | clarifier（主 Agent，clarify 方法） |
| `SPEC` | specifier（主 Agent，specify 方法） |
| `TECH` | designer（主 Agent，design 方法；可选 Architect 提供候选） |
| `SLICES` | planner（主 Agent，slice 方法） |
| `EVIDENCE` | **Verifier（必须是独立于 Implementer 的判断）** |
| 审查报告 | **Reviewer** |
| 简化候选 | **Simplifier** |

关键规则：

- **Implementer 永远不写 `EVIDENCE`。** 自检只是候选记录。
- **Reviewer 不改任何槽位**，只报问题；修复后由 Verifier 重判受影响的 `EVIDENCE`。
- **Orchestrator 不写任何判断性内容**，只推进状态与派发。
- **Clarifier / Specifier / Designer / Planner 通常是主 Agent 角色**，因为它们需要与用户连续对话；不默认派子代理。

## 6. 独立性规则

- **作者 ≠ 批评者**：同一实现者在“要求独立验收”的场景下，不能同时充当 Verifier 或 Reviewer。
- **预期来源独立 ≠ 执行者独立**：Verifier 可以从同一个 Agent 上下文开始，但必须先从确认的 `R#`/`AC#` 得出预期，再看实现；高风险或项目要求时，才要求独立执行实例。
- **Verifier 与 Reviewer 是两种判断**：一个判断“AC 是否满足”，一个判断“变更引入了什么缺陷”，不能合并成一份结论。
- **模型数量不是证据**：多个模型一致只提高置信度，不替代可观察证据。
- **Orchestrator 不裁定**：分歧交回负责方或按证据解决，不按票数。

## 7. 调用与降级

- Runtime 支持 subagent / 独立上下文：按角色契约派发，把输入、范围、禁止事项和输出要求一并给到。
- Runtime 不支持：同一上下文按角色顺序执行，但必须**标明执行者**并保留输出边界。若某风险要求“独立执行者”而 Runtime 做不到，报告这个限制，不能声称完成了独立验证。
- 不指定模型供应商、不写模型路由、不要求固定并发数；这些属于 Runtime / 用户选择。
- 角色调用不扩大授权：任务、工具、交接本身不增加提交、推送或发布权限。

## 8. 什么时候不派角色（避免过度编排）

| 场景 | 默认做法 |
| --- | --- |
| 单文件小改动、行为清楚 | 主 Agent 直接实现 + 一次验证；不派 Explorer |
| 需求清楚、局部改动 | 不派 Architect，不建 SLICES |
| 简单查询一个符号 | 不派 Explorer，直接查 |
| 同一上下文能可靠完成的验证 | Verifier 角色可在同上下文执行，但预期必须先独立得出 |
| 没有真实依赖的多个改动 | 不派 Orchestrator，不用并行 |
| 纯解释/沟通（how/why/bro） | 单 Agent，不派角色 |

## 9. 角色接口模板

每个角色在 `ROLES.md` 中按同一组字段定义：

```text
Role: <名称>
Purpose: <负责哪项判断或工作>
Inputs: <契约、候选、范围、权限、现有证据>
Allowed: <允许的操作>
Forbidden: <禁止的操作；特别是不扩权、不改上游、不自批>
Output: <结构化产出与必填字段>
Independence: <何时必须与谁分离；不满足时怎么报告>
Escalation: <什么情况交回调用方或用户>
```

## 10. 落地方式

1. 新增 `skills/core/ROLES.md`，并在 `core/SKILL.md` 的索引表加入它。
2. `clarify/references/fact-finder.md` 保留派发细节，角色定义改为引用 `ROLES.md` 的 Explorer。
3. `implement` 的收尾段引用 Verifier / Reviewer / Simplifier；`verify` / `review` / `simplify` 在开头标明自己就是对应角色。
4. `design` 在需要 design-it-twice 时可选 Architect；`research` 对应 Researcher。
5. `Orchestrator` 只在未来引入任务图或并行时定义，不进入默认主链。
6. 不在每个 Skill 目录里复制角色定义，也不为角色固定模型。

## 11. 需要拍板的三件事

1. 是否采用 **5 核心 + 3 可选** 这套角色集？还是先只做 5 个核心，Researcher / Architect / Orchestrator 等真实需求出现再加？
2. Verifier 在什么风险级别下必须用**独立执行实例**？当前建议：默认同上下文但预期先行；高风险、权限/数据/迁移、或项目明确要求时用独立实例。
3. Orchestrator 是否进入 `core`？当前建议：**不进入**，等有真实的多切片执行需求再说。
