# Skill 参考

> 本文件列出全部 Skill 与选择指引。工作流的阶段划分见[设计思想](design.md)，GitLab 相关技能见 [GitLab 插件](gitlab.md)。

## 工作流 Skill

| 阶段 | 需要解决的问题 | 主要 Skill |
| --- | --- | --- |
| **DEFINE · 明确需求** | 要做什么，如何判断完成？ | [cstack-clarify](../plugins/cstack/skills/cstack-clarify/SKILL.md)：澄清未决选择；[cstack-specify](../plugins/cstack/skills/cstack-specify/SKILL.md)：整理需求与验收条件 |
| **PLAN · 规划方案** | 哪些技术决策需要确定，如何分步交付？ | [cstack-tech-design](../plugins/cstack/skills/cstack-tech-design/SKILL.md)：确定共享或难以回退的技术选择；[cstack-slice](../plugins/cstack/skills/cstack-slice/SKILL.md)：拆分可验证的纵向切片 |
| **BUILD · 实现与诊断** | 如何实现需求或定位故障？ | [cstack-implement](../plugins/cstack/skills/cstack-implement/SKILL.md)：在授权范围内实现；[cstack-orchestrate](../plugins/cstack/skills/cstack-orchestrate/SKILL.md)：用 `git worktree` 并行实现可独立推进的切片；[cstack-diagnose](../plugins/cstack/skills/cstack-diagnose/SKILL.md)：建立反馈回路并定位根因；[cstack-test-first](../plugins/cstack/skills/cstack-test-first/SKILL.md)：围绕行为走测试先行循环 |
| **VERIFY · 验收** | 实际行为是否满足已确认需求？ | [cstack-create-verification-skill](../plugins/cstack/skills/cstack-create-verification-skill/SKILL.md)：建立或更新可重复的验证方法；[cstack-verify](../plugins/cstack/skills/cstack-verify/SKILL.md)：按验收条件核验候选变更 |
| **REVIEW · 审查** | 变更或测试中有哪些可证实的问题？ | [cstack-review](../plugins/cstack/skills/cstack-review/SKILL.md)：审查变更及相关路径；[cstack-test-audit](../plugins/cstack/skills/cstack-test-audit/SKILL.md)：在有疑点时审计测试有效性 |
| **SHIP · 交付** | 当前交付候选是否就绪，授权范围允许做什么？ | [cstack-ship](../plugins/cstack/skills/cstack-ship/SKILL.md)：判断并在授权范围内执行交付 |

## 辅助 Skill

不绑定阶段，按需跨阶段使用。

### 理解问题与设计方案

| Skill | 用途 |
| --- | --- |
| [cstack-research](../plugins/cstack/skills/cstack-research/SKILL.md) | 调查技术事实、比较方案，为决策提供依据 |
| [cstack-impact](../plugins/cstack/skills/cstack-impact/SKILL.md) | 查一项变更的影响半径，并证明决定其是否安全的关键事实 |
| [cstack-architecture-review](../plugins/cstack/skills/cstack-architecture-review/SKILL.md) | 审查现有架构的结构问题及实际代价 |
| [cstack-codebase-design](../plugins/cstack/skills/cstack-codebase-design/SKILL.md) | 用深模块、接缝（Seam）、删除检验等方法设计单个模块 |
| [cstack-wayfinding](../plugins/cstack/skills/cstack-wayfinding/SKILL.md) | 为跨会话的大工程整理地图、未知区域和决策工单 |
| [cstack-challenge](../plugins/cstack/skills/cstack-challenge/SKILL.md) | 对已成形方案做有边界的对抗审查 |
| [cstack-domain-model](../plugins/cstack/skills/cstack-domain-model/SKILL.md) | 梳理业务概念、关系和规则 |
| [cstack-prototype](../plugins/cstack/skills/cstack-prototype/SKILL.md) | 用一次性原型拍板说不清的行为、状态、界面或可行性问题 |

### 改进与协作

| Skill | 用途 |
| --- | --- |
| [cstack-create-project-profile](../plugins/cstack/skills/cstack-create-project-profile/SKILL.md) | 建立或更新稳定的项目工程档案（PROFILE） |
| [cstack-create-design-md](../plugins/cstack/skills/cstack-create-design-md/SKILL.md) | 建立或更新项目的界面设计系统文档（DESIGN.md） |
| [cstack-simplify](../plugins/cstack/skills/cstack-simplify/SKILL.md) | 在请求范围内识别或移除当前已无职责的复杂度 |
| [cstack-second-pass](../plugins/cstack/skills/cstack-second-pass/SKILL.md) | 第一遍已能运行时，用已学到的知识从变更前基线重写更简洁的版本 |
| [cstack-ui-review](../plugins/cstack/skills/cstack-ui-review/SKILL.md) | 根据实际界面与交互检查视觉和可用性 |
| [cstack-performance](../plugins/cstack/skills/cstack-performance/SKILL.md) | 测量性能、定位瓶颈并按授权优化 |
| [cstack-pr-feedback](../plugins/cstack/skills/cstack-pr-feedback/SKILL.md) | 核实并处理 PR 评审意见，区分判断、修改和回复的授权 |
| [cstack-handoff](../plugins/cstack/skills/cstack-handoff/SKILL.md) | 整理可核查的工作状态和下一步 |
| [cstack-retro](../plugins/cstack/skills/cstack-retro/SKILL.md) | 复盘实际任务，提出有依据的改进 |
| [cstack-visual-explain](../plugins/cstack/skills/cstack-visual-explain/SKILL.md) | 用图形解释工程概念、代码流程、方案或 PR 变更 |
| [cstack-chinese-writing-style](../plugins/cstack/skills/cstack-chinese-writing-style/SKILL.md) | 改写或审校中文技术写作，消除英文式翻译腔 |

### 沟通与理解

以下 Skill 按显式调用设计，不承担工程流程调度。

| Skill | 用途 |
| --- | --- |
| [cstack-bro](../plugins/cstack/skills/cstack-bro/SKILL.md) | 用户没听懂时换一种说法重讲那件事，补回缺失的前提，不改结论 |
| [cstack-restate-goal](../plugins/cstack/skills/cstack-restate-goal/SKILL.md) | 重述当前目标和边界，不启动访谈 |
| [cstack-how](../plugins/cstack/skills/cstack-how/SKILL.md) | 追踪并解释当前代码怎样运行 |
| [cstack-why](../plugins/cstack/skills/cstack-why/SKILL.md) | 根据项目证据调查设计、约束或改动的原因 |

## 容易选错的场景

| 用户的问题 | 用哪个 | 不用哪个 |
| --- | --- | --- |
| 这个模块的接口设计得合不合理 | [cstack-codebase-design](../plugins/cstack/skills/cstack-codebase-design/SKILL.md) | [cstack-architecture-review](../plugins/cstack/skills/cstack-architecture-review/SKILL.md)（除非跨模块） |
| 这套结构整体有没有问题 | [cstack-architecture-review](../plugins/cstack/skills/cstack-architecture-review/SKILL.md) | [cstack-codebase-design](../plugins/cstack/skills/cstack-codebase-design/SKILL.md) |
| 这个改动会不会在别处打破东西 | [cstack-impact](../plugins/cstack/skills/cstack-impact/SKILL.md)；审查时用 [cstack-review](../plugins/cstack/skills/cstack-review/SKILL.md) 的同一套证明层级 | [cstack-verify](../plugins/cstack/skills/cstack-verify/SKILL.md)（判 AC，不判风险） |
| 应用好慢 | [cstack-performance](../plugins/cstack/skills/cstack-performance/SKILL.md) | [cstack-diagnose](../plugins/cstack/skills/cstack-diagnose/SKILL.md)（除非是明确故障） |
| 没听懂，或者这段说得太绕 | [cstack-bro](../plugins/cstack/skills/cstack-bro/SKILL.md) | [cstack-restate-goal](../plugins/cstack/skills/cstack-restate-goal/SKILL.md)（不重述目标）；[cstack-visual-explain](../plugins/cstack/skills/cstack-visual-explain/SKILL.md)（要的是图） |
| 中文读起来像机翻，句子生硬拗口 | [cstack-chinese-writing-style](../plugins/cstack/skills/cstack-chinese-writing-style/SKILL.md) | [cstack-bro](../plugins/cstack/skills/cstack-bro/SKILL.md)（不解决文风） |
| 这个方案有没有问题 | [cstack-challenge](../plugins/cstack/skills/cstack-challenge/SKILL.md) | [cstack-review](../plugins/cstack/skills/cstack-review/SKILL.md)（审的是变更） |
| 这些测试是不是假的 | [cstack-test-audit](../plugins/cstack/skills/cstack-test-audit/SKILL.md) | [cstack-verify](../plugins/cstack/skills/cstack-verify/SKILL.md)（判 AC） |
| 第一遍已经能运行，要从变更前基线重写得更简洁 | [cstack-second-pass](../plugins/cstack/skills/cstack-second-pass/SKILL.md) | [cstack-simplify](../plugins/cstack/skills/cstack-simplify/SKILL.md)（在现有代码上减复杂度） |
| 行为、状态、界面或可行性还说不清，要对照实物拍板 | [cstack-prototype](../plugins/cstack/skills/cstack-prototype/SKILL.md) | [cstack-implement](../plugins/cstack/skills/cstack-implement/SKILL.md)（答案已经清楚就直接做）；[cstack-second-pass](../plugins/cstack/skills/cstack-second-pass/SKILL.md)（已能运行之后从基线重写）；[cstack-simplify](../plugins/cstack/skills/cstack-simplify/SKILL.md)（局部减复杂度） |
| 要定界面的颜色、字体和组件规范 | [cstack-create-design-md](../plugins/cstack/skills/cstack-create-design-md/SKILL.md) | [cstack-tech-design](../plugins/cstack/skills/cstack-tech-design/SKILL.md)（那是技术方案） |
| 当前页面好不好看、交互有没有问题 | [cstack-ui-review](../plugins/cstack/skills/cstack-ui-review/SKILL.md) | [cstack-create-design-md](../plugins/cstack/skills/cstack-create-design-md/SKILL.md)（写的是规范，不审页面） |
| 共享接口、数据模型或迁移怎么定 | [cstack-tech-design](../plugins/cstack/skills/cstack-tech-design/SKILL.md) | [cstack-create-design-md](../plugins/cstack/skills/cstack-create-design-md/SKILL.md)（不写视觉规范） |

## 触发方式

同一个 Skill 在 Claude Code 与 Codex 上的触发方式一致。手动触发的 Skill 需要两端同时关闭隐式调用：Claude Code 在 frontmatter 中写 `disable-model-invocation: true`，Codex 在 `agents/openai.yaml` 中写 `policy.allow_implicit_invocation: false`。可自动触发的 Skill 两端都允许按描述选用。

描述要与配置保持一致：手动触发的 Skill 在 description 里写明需要用户显式调用，其余 Skill 的 description 要写出可被自动匹配的使用场景。

| 触发方式 | Skill |
| --- | --- |
| 手动触发 | [cstack-core](../plugins/cstack/skills/cstack-core/SKILL.md)、[cstack-bro](../plugins/cstack/skills/cstack-bro/SKILL.md)、[cstack-create-project-profile](../plugins/cstack/skills/cstack-create-project-profile/SKILL.md)、[cstack-create-design-md](../plugins/cstack/skills/cstack-create-design-md/SKILL.md)、[cstack-how](../plugins/cstack/skills/cstack-how/SKILL.md)、[cstack-impact](../plugins/cstack/skills/cstack-impact/SKILL.md)、[cstack-orchestrate](../plugins/cstack/skills/cstack-orchestrate/SKILL.md)、[cstack-restate-goal](../plugins/cstack/skills/cstack-restate-goal/SKILL.md)、[cstack-second-pass](../plugins/cstack/skills/cstack-second-pass/SKILL.md)、[cstack-wayfinding](../plugins/cstack/skills/cstack-wayfinding/SKILL.md)、[cstack-why](../plugins/cstack/skills/cstack-why/SKILL.md)、[gitlab-core](gitlab.md) |
| 可自动触发 | 上表「工作流 Skill」与「辅助 Skill」中的其余全部 Skill，以及 GitLab 插件的七个自动触发技能（见 [GitLab 插件](gitlab.md)） |

## 共享层

[cstack-core](../plugins/cstack/skills/cstack-core/SKILL.md) 是仅手动触发的共享 Skill，供其他 Skill 按需读取文件；读取不会扩大授权。它索引共享判断约束 [PRINCIPLES.md](../plugins/cstack/skills/cstack-core/PRINCIPLES.md)，约定产物字段与 ID 的写法（[ARTIFACTS.md](../plugins/cstack/skills/cstack-core/ARTIFACTS.md)）、共享判据（[CRITERIA.md](../plugins/cstack/skills/cstack-core/CRITERIA.md)）和角色契约（[ROLES.md](../plugins/cstack/skills/cstack-core/ROLES.md)）。安装单个 Skill 时可以不安装 `cstack-core`；各 Skill 内嵌了独立运行所需的约束、产物和判据要点。

## 判断边界

每个 Skill 的「强制约束」小节列出该 Skill 任何情况下不可违反的规则；全 Skill 共享的不变量见上面的共享层。

验收与审查的分工、证据的候选绑定与失效重判、并行与冻结的边界、就绪与授权的区别，见[设计思想](design.md)第 2、3、5、7 节。
