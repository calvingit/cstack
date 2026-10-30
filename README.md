# CStack

面向 AI Coding Agent 的工程方法 Skills 包。六阶段 `DEFINE → PLAN → BUILD → VERIFY → REVIEW → SHIP` 用于理解工程工作，不是必须按顺序执行的流水线。

**状态：待用户评测的首版方法集。** 这些 Skill 的触发、跨 Runtime 兼容性及相对原生 Agent 的收益尚未验证。

## 方法选择

| 阶段 | Skill | 用途 |
| --- | --- | --- |
| DEFINE | [clarify](skills/clarify/SKILL.md) | 澄清会改变行为、范围或验收的未决选择，产出 DECISIONS |
| DEFINE | [specify](skills/specify/SKILL.md) | 将已确认需求整理为带 R/AC 的 SPEC 或验收依据 |
| PLAN | [design](skills/design/SKILL.md) | 处理需要共享或不可轻易撤回的技术决策，产出 TECH 的 D 记录 |
| PLAN | [slice](skills/slice/SKILL.md) | 拆成可验证的纵向切片和真实依赖，产出 SLICES |
| BUILD | [implement](skills/implement/SKILL.md) | 实现授权范围，跑相称的开发检查并接独立收尾 |
| BUILD | [diagnose](skills/diagnose/SKILL.md) | 先建立能变红的反馈回路，再定位根因，按授权修复 |
| BUILD | [test-first](skills/test-first/SKILL.md) | 按行为进行测试先行的失败与通过循环 |
| VERIFY | [verification-setup](skills/verification-setup/SKILL.md) | 发现或建立项目可重复的验证方法 |
| VERIFY | [verify](skills/verify/SKILL.md) | 按验收条件核验指定候选和实际受测对象 |
| REVIEW | [review](skills/review/SKILL.md) | 审查变更及相关路径中的可证实缺陷 |
| REVIEW | [test-audit](skills/test-audit/SKILL.md) | 在有具体疑点时审计测试有效性和维护价值 |
| SHIP | [ship](skills/ship/SKILL.md) | 判断并在明确授权范围内执行交付 |

## 按需辅助方法

这些 Skill 横跨阶段，只在存在对应的独立任务或判断时使用。

| Skill | 用途 | 与主流程的边界 |
| --- | --- | --- |
| [research](skills/research/SKILL.md) | 基于来源调查技术事实、比较方案 | 提供决策依据，不代替具体技术设计 |
| [impact](skills/impact/SKILL.md) | 追踪变更对调用方、数据和关键不变量的影响 | 可用于计划或审查，不代替验收与代码审查 |
| [architecture-review](skills/architecture-review/SKILL.md) | 审查现有架构的结构问题及实际代价 | 判断当前架构，不自行设计或实施重构 |
| [codebase-design](skills/codebase-design/SKILL.md) | 用深模块、Seam、删除测试等词汇设计单个模块 | 回答单点怎么成形，不判断整体架构 |
| [wayfinding](skills/wayfinding/SKILL.md) | 跨会话大工程的地图、战争迷雾与决策票据 | 规划，不直接实现；目的地清楚后交给 specify / design / slice |
| [challenge](skills/challenge/SKILL.md) | 对已成形方案做有边界的对抗审查 | 只报告问题，不重新设计或修改实现 |
| [project-setup](skills/project-setup/SKILL.md) | 记录稳定的项目工程档案（PROFILE） | 只放位置与策略，不存任务状态 |
| [core](skills/core/SKILL.md) | 共享判断底线与产物槽位词汇 | 只做索引，不执行任务；不自动触发，供其他 Skill 调用 |
| [simplify](skills/simplify/SKILL.md) | 识别或移除无当前职责的复杂性 | 限于用户请求的范围，不扩展成无关清理 |
| [ui-review](skills/ui-review/SKILL.md) | 根据实际界面与交互检查视觉和可用性 | 与逐项业务验收分开，无法观察时保留未知 |
| [handoff](skills/handoff/SKILL.md) | 整理可核查的工作状态和下一步 | 复用现有事实，不建立第二份任务状态 |
| [pr-feedback](skills/pr-feedback/SKILL.md) | 核实并处理 PR 评审意见 | 区分问题判断、代码修改和外部回复的授权 |
| [performance](skills/performance/SKILL.md) | 测量性能、定位瓶颈并按授权优化 | 与通用故障诊断配合，侧重可比测量 |
| [prototype](skills/prototype/SKILL.md) | 用最小原型检验具体设计或可行性问题 | 原型观察不能代替生产系统验收 |
| [retro](skills/retro/SKILL.md) | 复盘实际任务并提出有依据的改进 | 按需复盘，不默认增加规则或 Skill |
| [domain-model](skills/domain-model/SKILL.md) | 梳理业务概念、关系和规则 | 支持需求澄清与设计，不代替业务决策 |

其中一些方法参考了 [tstack 的 PR 跟进](https://github.com/t3dotgg/tstack/blob/1085050f3baed1ac724caa4a8166145fb2ac88af/skills/babysit-pr/SKILL.md)、[Warp 的 PR 反馈处理](https://github.com/warpdotdev/common-skills/blob/8792394ff1b655e0af451b8fabb68ef0cfcbd208/.agents/skills/respond-to-pr-comments-in-blocklist/SKILL.md)、[Addy 的性能分析](https://github.com/addyosmani/agent-skills/blob/aeac41d4d005999432bb7312f7ff06383a91d59d/skills/performance-optimization/SKILL.md)，以及 Matt 的[原型](https://github.com/mattpocock/skills/blob/59db609eb1e18aaf59b63284d0e52255aff0c63c/skills/engineering/prototype/SKILL.md)、[复盘](https://github.com/mattpocock/skills/blob/59db609eb1e18aaf59b63284d0e52255aff0c63c/skills/engineering/retro/SKILL.md)和[领域建模](https://github.com/mattpocock/skills/blob/59db609eb1e18aaf59b63284d0e52255aff0c63c/skills/engineering/domain-modeling/SKILL.md)思路，按 CStack 的职责边界编写。

## 汇报风格

[report-style](skills/report-style/SKILL.md) 将工作状态、验证结果和证据分开，帮助 Agent 给出简洁、可核查的任务汇报。它借鉴 [ste-zh](https://github.com/dualface/ste-zh/tree/27d57e4d6609ce88e14dd15cbae355223a83b246) 的规则，保留上游 MIT 许可；不强制固定模板或修改项目文件。

## 图形化解释

[visual-explain](skills/visual-explain/SKILL.md) 用图形解释工程概念、代码流程、方案或 PR 变更。对话内展示时，优先使用当前 Runtime 实际提供且适用的 `visualize` Skill；其他情况按环境选择 Mermaid、可复制的 PR 内容或独立 HTML。原生能力是否可发现、调用和渲染，仍需在目标 Harness 中验证。

## 沟通与理解

这些小工具按显式调用设计，不承担工程流程调度。其用途参考 [pstack 的沟通类 Skill](https://github.com/cursor/plugins/tree/1ba91fc25c0977741dd0e267849e6234b037ed0a/pstack/skills)，指令按 CStack 的边界编写。

| Skill | 用途 |
| --- | --- |
| [bro](skills/bro/SKILL.md) | 用更通俗的话重述上一条答复或指定片段，保留原有条件和不确定性 |
| [restate-goal](skills/restate-goal/SKILL.md) | 重述对用户当前目标和边界的理解，不启动访谈 |
| [how](skills/how/SKILL.md) | 追踪并解释当前代码怎样运行 |
| [why](skills/why/SKILL.md) | 根据历史和项目证据调查某项设计或约束为什么存在 |

四个 Skill 的 OpenAI 元数据声明 `allow_implicit_invocation: false`；其他 Runtime 可能不识别该设置，实际调用行为仍需在对应 Harness 中验证。

Skill 按任务需要组合；同一方法可以跨阶段使用。例如验证时发现故障，可以进入诊断；审查发现测试可能虚假通过，可以按需审计测试。已有目标和验收依据的局部改动不需要先生成规格、设计或任务清单。

## 关键边界

- **验收**依据已确认的需求判断实际行为；**审查**寻找变更引入的缺陷；**交付**综合有效证据、项目门禁和授权。三者可以复用适用的观察，但不互相代替。
- 项目验证方法负责如何操作和观察系统；方法能够运行，并不代表某个候选已经通过验收。
- 实现、验证和审查需要识别当前候选及相关工作树变更。证据需说明实际受测对象、环境、观察和限制；条件变化后重新判断适用性。
- 合并就绪、发布就绪、执行授权和实际结果分别表达。合并会触发自动部署时，副作用必须在授权范围内；入队不等于已合并。
- **产物链**：需求确认（DECISIONS）、规格（SPEC）、技术决定（TECH）、切片（SLICES）与证据（EVIDENCE）按逻辑槽位衔接。槽位可以缺席，形态自由，但下游按 ID 引用、不复制内容；缺失不授权编造。共享词汇见 [core](skills/core/SKILL.md)。
- 不要求固定文档、独立执行者、全量检查、任务图或新的 Runtime。具体深度由任务风险、现有项目约束和用户要求决定。

## Agent 角色

[core/ROLES.md](skills/core/ROLES.md) 定义 5 个核心角色（Explorer、Implementer、Verifier、Reviewer、Simplifier）与 3 个可选角色（Researcher、Architect、Orchestrator）。默认单 Agent；只有上下文隔离、独立性或并行有实际收益时才派独立实例。

插件根 [agents/](agents/README.md) 提供 Claude Code **可直接派发**的 agent 定义：`explorer`、`implementer`、`verifier`、`reviewer`、`simplifier`、`researcher`、`architect`。Orchestrator 因为 Claude Code 的 subagent 不支持嵌套派发，只保留契约，由主 Agent 配合 `slice` / `wayfinding` 承担。

关键规则：Implementer 不写 `EVIDENCE`；Verifier 与 Reviewer 是两种判断；预期来源独立不等于执行者独立；Orchestrator 不做判断，也不进入默认主链。

## 作为插件安装

仓库根提供 Claude Code / Codex 插件清单（`.claude-plugin/plugin.json` 与 `.claude-plugin/marketplace.json`）：

```text
/plugin marketplace add calvingit/cstack
/plugin install cstack@cstack
```

命令行等价写法：`claude plugin marketplace add calvingit/cstack`、`claude plugin install cstack@cstack`。更新用 `claude plugin marketplace update cstack` 与 `claude plugin update cstack@cstack`。Claude Code 按 `version` 判断有没有新版本，只有改了版本号才会更新。手写挂载方式见下一节。

## 在测试项目中使用

`skills/core/` 是一个**不自动触发**的共享 Skill：`SKILL.md` 只索引 `PRINCIPLES.md` 与 `ARTIFACTS.md`，由其他 Skill 通过 Skill tool 调用，或由用户显式调用。其余每个目录都是一个完整 Skill。导入时建议连同 `core` 一起复制，供各 Skill 对齐槽位名与字段。每个 `SKILL.md` 内嵌自己需要的「底线 / 产物」要点，缺少 `core` 时仍可单独运行；装了时在需要对齐词汇处调用它。`agents/openai.yaml` 是可选的 OpenAI 元数据，部分 Skill 在其中声明调用策略。其他 Runtime 的发现和调用行为需要各自验证。

例如，在**准备好的临时 Codex 测试项目根目录**中，将下面的路径改成你的 CStack 本地克隆路径后运行：

```bash
CSTACK_ROOT="/absolute/path/to/cstack"
mkdir -p .agents/skills
cp -R "$CSTACK_ROOT"/skills/* .agents/skills/
```

建议使用没有旧版同名 Skill 的隔离项目，避免覆盖已有配置。通过目标 Harness 检查 Skill 是否被发现，并分别测试显式调用与不点名的自然语言请求；自动触发不由文件存在保证。

显式任务示例：

> 使用 `$verify` 验收当前候选的已确认需求，提供实际检查对象和证据限制。

> 使用 `$review` 审查当前变更，报告具体缺陷、触发条件和证据。

> 使用 `$ship` 判断当前 PR 能否交付，按我已授权的范围处理。

## 历史资料

- [研究提案](docs/proposal-2026-10-28.md)和[首轮架构审查](docs/architecture-review-2026-10-28.md)记录设计依据与开放问题。
- [六个阶段 Skill 的旧原型](docs/base-skills-2026-10-29.md)是历史快照，已由本方法集替代。
- [规则预实验](evals/example-v0/README.md)及 [v0 冒烟记录](evals/base-v0/smoke.json)属于历史资料，不能证明当前 Skill 的 Harness 兼容性或效果。
