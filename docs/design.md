# CStack 设计思想

> 本文说明这套 Skills 的工作流与设计取舍。方法清单与安装方式见 [README](../README.md)；共享词汇与不变量见 [cstack-core](../skills/cstack-core/SKILL.md)。

## 1. 定位

CStack 是面向 AI Coding Agent 的工程方法 Skills 包，Markdown-first，跨 Runtime 使用。差异化目标可以概括为一句话：**让验证证据、审查结论和交付决策都绑定到明确的代码候选、环境与授权范围；相关条件变化后，重新判定证据是否失效。**

明确不做的事：

- 不开发 Runtime、任务调度服务、Git 客户端或 CI 平台。
- 不建固定流水线：不要求每次修改都跑完六阶段，不强制生成 SPEC、设计文档或任务清单。
- 不引入脚本状态机、工单执行图、模型路由或"多模型投票即通过"。
- 不用代码行数、固定测试比例或模型数量当通用质量标准。
- 不因用户一句话自动提升权限；不默认提交、推送、合并、部署。

## 2. 六阶段：地图，不是流水线

`DEFINE → PLAN → BUILD → VERIFY → REVIEW → SHIP` 用于理解工程工作。上游阶段和中间产物可以按当前问题跳过或返回。任务要声明完成时，验收和审查不能跳过。

| 阶段 | 回答的问题 | 最小输出 |
| --- | --- | --- |
| DEFINE | 要实现什么，范围与验收是什么？ | 已确认目标、边界、AC |
| PLAN | 技术选择与交付顺序是否成立？ | 必要技术决策、可验证工作单元 |
| BUILD | 当前范围是否正确实现？ | 候选变更及开发检查 |
| VERIFY | 实际行为是否满足已确认 AC？ | 逐个 AC 的 PASS / FAIL / NOT VERIFIED 与证据 |
| REVIEW | 变更引入了哪些可证明的缺陷或风险？ | 按影响排序的发现及限制 |
| SHIP | 是否可以合并或发布？ | 就绪结论、阻塞、已接受风险 |

简单任务（目标清楚、影响局部、现有检查足够）可以直接实现，不经过上游中间产物。深度由风险决定，不由流程决定。即使改动很小，收尾仍须实际运行 `cstack-verify` 和 `cstack-review`；`cstack-simplify` 可以跳过。验收或审查记为未运行的，不等于通过。

## 3. 证据：候选绑定与失效

这是 CStack 的核心机制。每条验证结论必须能回答五个问题：观察对象、环境、执行者、覆盖内容、未覆盖内容。

- **候选绑定**：记录 HEAD、提交范围或工作树状态；工作树有未提交内容时，不能用 HEAD SHA 代表候选状态。
- **结论词汇**：逐个 AC 给 PASS / FAIL / NOT VERIFIED。证据不足写 NOT VERIFIED，不写 PASS；环境失败不是产品失败；实现者的自检记录不算证据，独立判断只能由 Verifier 给出。
- **失效重判**：功能代码、测试、验证配置、验收条件、依赖、基线或环境变化后，重新判断受影响的证据是否仍然适用——只重判受影响部分，不全量重跑；判断不了影响就补验或保留 NOT VERIFIED。
- **风险接受留痕**：FAIL 或 NOT VERIFIED 不得改写成 PASS；接受风险要记录依据和接受者。
- **证明层级**：判断风险或安全事实是否成立时按 [CRITERIA.md](../skills/cstack-core/CRITERIA.md) 的层级；只列调用方或搜索没结果都到不了证明。

## 4. 产物链：6 类权威产物

产物链不是必经流程，而是 6 类**可按需启用的权威产物**。同一类产物可以是会话记录、文件或 issue，形态自由；约定的是字段、所有权和交接规则，不是文件名与模板。

| 层 | 产物 | 回答的问题 | 唯一写入者 | 消费方 |
| --- | --- | --- | --- | --- |
| 项目基座 | `PROFILE` | 这个项目长期怎么运作？ | cstack-create-project-profile | 所有 Skill |
| 需求契约 | `DECISIONS` | 哪些需求选择已由用户确认？ | cstack-clarify | cstack-specify |
| 需求契约 | `SPEC` | 要做什么，怎么算完成？ | cstack-specify | cstack-tech-design / cstack-slice / cstack-implement / cstack-verify / cstack-review |
| 交付计划 | `TECH` | 哪些共享或难以撤回的技术选择已定？ | cstack-tech-design | cstack-slice / cstack-implement / cstack-verify / cstack-review |
| 交付计划 | `SLICES` | 怎么分步交付，谁阻塞谁？ | cstack-slice | cstack-implement / cstack-verify |
| 结果 | `EVIDENCE` | 实际做到什么程度？ | cstack-verify | cstack-review / cstack-ship |

三条不变量：

1. **一类事实只有一个权威产物**；下游按 ID 引用（`R#`、`AC#`、`D#`、`S#`），不复制内容。
2. **产物可以省略**；省略表示没有单独形成文档，但这不等于没有要求，更不等于可以凭空假设。缺少可引用的依据时，只能保留 NOT VERIFIED，不得补一个假设。
3. **变化只改负责的产物**，再重判受影响的下游产物：需求变改 DECISIONS/SPEC，设计变改 TECH，拆分变改 SLICES，候选或环境变改 EVIDENCE。

`ADR` 不是第 7 类产物，而是 `TECH` 中 `D#` 的长期形态：跨任务仍成立时提升为 ADR，`TECH` 保留 ID 与摘要。`EVIDENCE` 的粒度是一份交付候选一份，切片记录汇总进去，不单独成篇。

字段定义与 ID 约定见 [cstack-core/ARTIFACTS.md](../skills/cstack-core/ARTIFACTS.md)。

## 5. 风险自适应与权限

是否增加设计、验证和审查，由四个事实决定，不做加权打分：

1. **不确定性**（Uncertainty）：需求、不变量与技术路径是否确定？
2. **影响半径**（Blast Radius）：涉及多少调用方、共享契约、用户、数据与外部系统？
3. **验证难度**（Verification Difficulty）：有没有可用、可信且获准的真实执行环境？
4. **可逆性**（Reversibility）：能否安全恢复？数据和外部副作用无法随代码回滚一并撤销。

权限按操作分组：**Inspect**（只读）→ **Prepare**（在授权范围内实现、验证、审查，停在待合并状态）→ **Merge / Deploy**（各自需要明确授权）。就绪、授权与实际执行结果需分别说明；合并会触发自动部署时，副作用必须在授权范围内。

## 6. 强制约束与独立性

工作流与辅助 Skill 的 SKILL.md 开头有「强制约束」小节：3–5 条本 Skill 任何情况下不可违反的规则，表述完整，不依赖外部索引。全 Skill 共享的不变量（范围、认知、决策、授权、证据、恢复六组）收在 [cstack-core/PRINCIPLES.md](../skills/cstack-core/PRINCIPLES.md)。

独立性设计：

- `cstack-core` 是**唯一共享层**，不自动触发，只提供共享词汇、不变量、产物字段与共享判据；其他 Skill 通过读取它的文件对齐命名、字段和判据，不需要调用 Skill。
- 每个 Skill 内嵌自己需要的「强制约束 / 产物 / 判据」要点，**没有硬依赖**：只装单个 Skill 也能独立运行。
- 不能既宣称"单目录独立"，又要求读取根目录共享文件而无内嵌兜底。

## 7. 角色模型

四个概念分开：**Skill**（方法：输入、步骤、停止条件、输出产物）、**Role**（责任契约：谁负责这项判断）、**Agent instance**（一次具体执行，可在同一上下文，也可用独立实例）、**Invocation policy**（谁能启动它）。

采用 5 个核心角色（Explorer、Implementer、Verifier、Reviewer、Simplifier）与 3 个可选专业角色（Researcher、Architect、Orchestrator）。关键规则：

- **Implementer 永远不写 `EVIDENCE`**；自检只是候选记录。
- **Verifier 与 Reviewer 是两种判断**（验收条件是否满足 vs 变更引入了什么缺陷），不能合并成一份结论。任务收尾两者都必须实际运行；记为未运行的，不等于通过。Simplifier 可以跳过。
- **预期来源独立 ≠ 执行者独立**：默认同上下文执行，但预期先行；高风险时才要求独立实例。
- **角色不是越多越好**：默认单 Agent，只有隔离、独立性或并行有实际收益时才派独立实例。
- **辅助判断不产出 AC 结论**：界面、性能、影响半径、测试审计和对抗审查只提供观察与发现，`PASS` / `FAIL` 只由 Verifier 下。

角色契约见 [cstack-core/ROLES.md](../skills/cstack-core/ROLES.md)；Claude Code 可直接派发的定义见 [agents/](../agents/)，使用说明见 [Agent 角色](../README.md#agent-角色)。

## 8. 方法形态

每个 Skill 的结构由它的判断决定，不用统一模板：`cstack-clarify` 是"决策树 + 前沿 + 轮次"，`cstack-diagnose` 是"先建能变红的反馈回路，再假设"，`cstack-slice` 是"纵向切片 + 真实依赖 + 校验"，`cstack-review` 是"范围 + 严重度 + 报告契约"。硬把不同的判断套进同一副结构，反而会掩盖它们之间的差别。

长度由不可压缩的结构决定：主 SKILL.md 放判断结构与完成判据，细节放同目录 `references/` 按需读取。每个概念都要能回答三件事——什么时候触发、产出什么、怎么判断完成；答不出来就是装饰，删掉。

共同前提：软件工程的基本方法仍然有效，Skills 的价值在于让 Agent 稳定选择并执行这些方法；工具与自动化提供可重复的检查，证据判断不能靠参与模型的数量推断。
