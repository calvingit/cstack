# CStack

面向 AI Coding Agent 的工程方法 Skills 包。六阶段 `DEFINE → PLAN → BUILD → VERIFY → REVIEW → SHIP` 用于理解工程工作，不是必须按顺序执行的流水线。

**状态：待用户评测的首版方法集。** 这些 Skill 的触发、跨 Runtime 兼容性及相对原生 Agent 的收益尚未验证。

## 方法选择

| 阶段 | Skill | 用途 |
| --- | --- | --- |
| DEFINE | [cstack-clarify](skills/cstack-clarify/SKILL.md) | 澄清会改变行为、范围或验收的未决选择 |
| DEFINE | [cstack-specify](skills/cstack-specify/SKILL.md) | 将已确认需求整理为可验证的规格或交接依据 |
| PLAN | [cstack-design](skills/cstack-design/SKILL.md) | 处理需要共享或不可轻易撤回的技术决策 |
| PLAN | [cstack-slice](skills/cstack-slice/SKILL.md) | 拆分可验证的交付单元和真实依赖 |
| BUILD | [cstack-implement](skills/cstack-implement/SKILL.md) | 实现授权范围并运行相称的开发检查 |
| BUILD | [cstack-diagnose](skills/cstack-diagnose/SKILL.md) | 复现和定位故障，按授权修复 |
| BUILD | [cstack-test-first](skills/cstack-test-first/SKILL.md) | 按行为进行测试先行的失败与通过循环 |
| VERIFY | [cstack-verification-setup](skills/cstack-verification-setup/SKILL.md) | 发现或建立项目可重复的验证方法 |
| VERIFY | [cstack-verify](skills/cstack-verify/SKILL.md) | 按验收条件核验指定候选和实际受测对象 |
| REVIEW | [cstack-review](skills/cstack-review/SKILL.md) | 审查变更及相关路径中的可证实缺陷 |
| REVIEW | [cstack-test-audit](skills/cstack-test-audit/SKILL.md) | 在有具体疑点时审计测试有效性和维护价值 |
| SHIP | [cstack-ship](skills/cstack-ship/SKILL.md) | 判断并在明确授权范围内执行交付 |

Skill 按任务需要组合；同一方法可以跨阶段使用。例如验证时发现故障，可以进入诊断；审查发现测试可能虚假通过，可以按需审计测试。已有目标和验收依据的局部改动不需要先生成规格、设计或任务清单。

## 关键边界

- **验收**依据已确认的需求判断实际行为；**审查**寻找变更引入的缺陷；**交付**综合有效证据、项目门禁和授权。三者可以复用适用的观察，但不互相代替。
- 项目验证方法负责如何操作和观察系统；方法能够运行，并不代表某个候选已经通过验收。
- 实现、验证和审查需要识别当前候选及相关工作树变更。证据需说明实际受测对象、环境、观察和限制；条件变化后重新判断适用性。
- 合并就绪、发布就绪、执行授权和实际结果分别表达。合并会触发自动部署时，副作用必须在授权范围内；入队不等于已合并。
- 不要求固定文档、独立执行者、全量检查、任务图或新的 Runtime。具体深度由任务风险、现有项目约束和用户要求决定。

## 在测试项目中使用

每个 `skills/cstack-*` 目录都是一个完整的 Skill。按目标 Harness 的机制导入完整目录；`SKILL.md` 不依赖仓库根目录或其他 CStack Skill，`agents/openai.yaml` 是可选的 OpenAI 界面元数据。其他 Runtime 的发现和调用行为需要各自验证。

例如，在**准备好的临时 Codex 测试项目根目录**中，将下面的路径改成你的 CStack 本地克隆路径后运行：

```bash
CSTACK_ROOT="/absolute/path/to/cstack"
mkdir -p .agents/skills
cp -R "$CSTACK_ROOT"/skills/cstack-* .agents/skills/
```

建议使用没有旧版同名 Skill 的隔离项目，避免覆盖已有配置。通过目标 Harness 检查 Skill 是否被发现，并分别测试显式调用与不点名的自然语言请求；自动触发不由文件存在保证。

显式任务示例：

> 使用 `$cstack-verify` 验收当前候选的已确认需求，提供实际检查对象和证据限制。

> 使用 `$cstack-review` 审查当前变更，报告具体缺陷、触发条件和证据。

> 使用 `$cstack-ship` 判断当前 PR 能否交付，按我已授权的范围处理。

## 历史资料

- [研究提案](docs/cstack-proposal-2026-10-28.md)和[首轮架构审查](docs/architecture-review-2026-10-28.md)记录设计依据与开放问题。
- [六个阶段 Skill 的旧原型](docs/base-skills-2026-10-29.md)是历史快照，已由本方法集替代。
- [规则预实验](evals/example-v0/README.md)及 [v0 冒烟记录](evals/base-v0/smoke.json)属于历史资料，不能证明当前 Skill 的 Harness 兼容性或效果。
