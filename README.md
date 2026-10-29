# CStack

面向 AI Coding Agent 的工程 Skills 实验包。目标是小而稳定、跨 Runtime、依据真实证据和风险选择工作方式。

**状态：基础原型。六个 Skill 已创建；工程收益和跨 Runtime 兼容性尚未证实。**

## 基础 Skills

| Skill | 职责 | 停止点 |
| --- | --- | --- |
| [cstack-define](skills/cstack-define/SKILL.md) | 澄清目标、范围与可观察 AC；合并 clarify/specify | 有足够可靠的需求依据 |
| [cstack-plan](skills/cstack-plan/SKILL.md) | 必要设计与可验证工作单元；合并 design/decompose | 共享技术决策明确 |
| [cstack-build](skills/cstack-build/SKILL.md) | 实现、按需诊断、开发检查 | 当前候选及检查结果可交接 |
| [cstack-verify](skills/cstack-verify/SKILL.md) | 按 AC 核验实际候选与受测对象 | 逐项 PASS / FAIL / NOT VERIFIED |
| [cstack-review](skills/cstack-review/SKILL.md) | 审查 diff 与调用路径，核实缺陷和风险 | 有依据的发现与限制 |
| [cstack-ship](skills/cstack-ship/SKILL.md) | 分别判断合并/发布就绪、授权和执行状态 | GO / HOLD 与交接；不执行交付 |

六阶段是工程地图，可以跳过或返回。明确的局部改动可直接 BUILD；仅验收、审查或交付判断可直接使用对应 Skill。无需依次调用全部六个。

每个目录中的 `SKILL.md` 是完整入口，包含触发说明、方法、权限边界、输出与停止条件；不依赖仓库外或根目录共享文件。`agents/openai.yaml` 仅提供可选 UI 元数据，方法正文不依赖它。暂不拆独立方法 Skill、建立 Runtime Adapter 或维护状态数据库。

## 使用

在支持目录式 Skills 的宿主中，按其安装机制导入所需的 `skills/cstack-*` 完整目录。本次只提交仓库源码，没有安装到个人技能目录；各宿主自动发现与触发仍需实测。

不依赖自动发现的显式使用示例：

> 读取并使用 `skills/cstack-verify/SKILL.md`，依据当前任务的 AC 核验候选；报告实际观察对象与证据缺口。

有原生 Skill 注册的宿主可使用其命名调用机制。不要把正文放进系统权限层；Skill 不能扩大用户授权或绕过项目规则。

## 验证与研究材料

- [基础版本说明](docs/base-skills-2026-10-29.md)：本轮选择与验证边界。
- [原始研究提案](docs/cstack-proposal-2026-10-28.md)：按原文保存，仍是研究提案。
- [架构审查](docs/architecture-review-2026-10-28.md)：职责、证据、权限和三个开放决策。
- [规则预实验 example-v0](evals/example-v0/README.md)：24 次 sol/luna 提示词对照，没有加载 Skill 文件，不属于 Skill 效果验证。
- [预实验报告](evals/example-v0/results/cstack-example-eval-2026-10-28.md)：原始结果及日志缺口。未证明候选规则优于基线。

检查旧实验归档：`python3 evals/example-v0/verify_archive.py`。此命令只核对保存材料，不调用模型。

2026-10-29 用户授权按现有方案创建基础 Skill。此前提案中的“不创建 Skill/仓库”描述历史阶段边界；本次授权不代表完整架构定稿、真实合并部署授权或效果已获证明。
