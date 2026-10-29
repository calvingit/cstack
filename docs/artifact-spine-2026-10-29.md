# CStack 产物链与独立性设计（决策落定）

> 依据：2026-10-29 的两条结论——**需要有产物链，但不照抄参考体系；尽量保持每个 Skill 独立，可以共享 kernel / principles。**
> 性质：设计定稿，不直接改 Skill 正文。
> 关联：[CStack Skills 提升方案](skill-upgrade-2026-10-29.md)。

## 0. 两个决策落到什么约束

| 决策 | 约束 |
| --- | --- |
| 要有产物链，不照抄 | 定义 CStack 自己的**逻辑槽位**，只约定“字段、所有权、交接规则”，不约定文件名与模板；产物形态自由（会话 / 文件 / issue）。 |
| 尽量独立，可共享 kernel / principles | 唯一共享层是一份很小的 `principles`（不变量 + 产物词汇）；每个 Skill 内嵌自己需要的“底线 + 产物”要点，缺共享文件也能单独工作。 |

一句话：**共享“词汇与不变量”，不共享“文件与流程”；槽位是逻辑的，形态是自由的。**

## 1. 产物链：6 个槽位，4 层

不是 6 个必须创建的文档，而是 6 个**可按需启用的权威槽位**。同一个槽位可以是一段会话记录、一个 Markdown 文件、一个 issue，或 PR 描述里的一节。

| 层 | 槽位 | 回答的问题 | 最小字段 | 唯一写入者 | 消费方 |
| --- | --- | --- | --- | --- | --- |
| 项目基座 | `PROFILE` | 这个项目长期怎么运作？ | 术语/领域模型位置、验证入口、需求权威来源、既有决策（ADR）位置、任务存放约定 | setup | 所有 Skill |
| 需求契约 | `DECISIONS` | 哪些需求选择已经由用户确认？ | 决定（问题 + 选择）、理由、可观察结果、确认来源、未决项 | clarify | specify |
| 需求契约 | `SPEC` | 要做什么，怎么算完成？ | Goal、Scope/Out、`R#`、`AC#`（来源 R、可观察、可判定、失败情形）、Acceptance Seam、约束 | specify | design / slice / implement / verify / review |
| 交付计划 | `TECH` | 哪些共享或难逆转的技术选择已定？ | `D#`（决定）、依据（R/AC 或代码事实）、备选、权衡、恢复/迁移、Verification Seam | design | slice / implement / verify / review |
| 交付计划 | `SLICES` | 怎么分步交付，谁阻塞谁？ | `S#`、交付什么（端到端可验证）、covers（R/AC/D）、blocked-by、本地 AC、约束 | slice | implement / verify |
| 结果 | `EVIDENCE` | 实际做到什么程度？ | 逐 `AC#` 的 PASS / FAIL / NOT VERIFIED、候选（HEAD + 工作树状态）、方法、环境、执行者、覆盖限制、证据位置 | verify | review / ship |

### 1.1 标识约定

- `R1` / `AC1` / `C1`（需求确认）/ `D1`（技术决定）/ `S1`（切片）为稳定 ID；`S1-AC1` 表示切片自己的本地验收条件，**与 SPEC 的 `AC#` 分属不同命名空间**。
- 下游一律引用 ID，不复制内容。复制只允许作为可追溯的摘要，并标明来源与版本。
- 没有 ID 就无法被下游消费；所以“要不要编号”的判据是“这项事实是否会被下游引用”，不是“够不够正式”。

### 1.2 链条与流转

```text
[项目基座] PROFILE
              │
[需求契约]    ├─► DECISIONS ─► SPEC(R/AC)
              │                    │
[交付计划]    │                    ├─► TECH(D)? ─► SLICES(S)? 
              │                    │
[结果]        └────────────────────┴─► EVIDENCE ─► 就绪判断
```

三条不变量：

1. **一个事实只有一个权威槽位**；下游只引用，不复制。
2. **槽位可以缺席**；缺席表示“当前任务没有把它单独固化”，不等于“没有要求”，也不等于可以凭空假设。
3. **变化只改负责槽位**，再重判受影响的下游：需求变 → DECISIONS/SPEC；设计变 → TECH；拆分变 → SLICES；候选或环境变 → EVIDENCE。

### 1.3 何时启用哪个槽位

| 任务事实 | 启用的槽位 |
| --- | --- |
| 项目有稳定约定、要跨任务复用 | PROFILE |
| 访谈产生了会改变行为/范围/验收的确认选择 | DECISIONS → SPEC |
| 需求需要被共享、版本化或交接给下游 | SPEC（必须：否则 verify 无稳定 AC 可依） |
| 多个实现要共享类型、接口、状态、迁移 | TECH |
| 有多个可分别交付、存在真实依赖的单元 | SLICES |
| 有完成声明 | EVIDENCE（必须：否则就是自证） |

简单任务可以只有会话里的 `DECISIONS + EVIDENCE`，不落任何文件。

## 2. 为什么这不是照抄

| 维度 | 参考体系（Matt / Engineering Skills / pstack） | CStack 设计 |
| --- | --- | --- |
| 形态 | 固定文件名与模板：`SPEC.md`、`SOLUTION.md`、`tickets/NN-.md` | **逻辑槽位 + 字段**；文件、会话、issue 都可以，不强制模板 |
| 技术产物 | `SOLUTION.md` | `TECH` 槽位，仅共享/难逆时启用；字段以“依据 → 备选 → 权衡 → 恢复”为主，不照搬章节 |
| 证据 | 是 Skill 的输出报告 | **`EVIDENCE` 是第一等槽位**，候选绑定、逐 AC、执行者与覆盖限制是核心字段 |
| 决定记录 | `decisions.md` 常被当附件 | `DECISIONS` 是独立槽位，拥有明确上游/下游 |
| 执行图 | ticket 图、`.loop/` 状态、脚本 | 不进入方法层；`SLICES` 只记交付契约与真实依赖，无运行状态 |
| 收尾 | 默认多 Agent 派发 | 角色分离，但允许单上下文；派发属于 Runtime |
| 知识回写 | 有独立 protocol | 只保留“往哪写”的规则，不建新流程 |

结论：**保留“事实单向流动、按 ID 引用、变化只改负责方”的机制，去掉固定的文件形态、模板和运行状态。**

## 3. 独立性：principles + 内嵌底线

### 3.1 唯一共享层：`cstack-core` Skill

`cstack-core` 是一个**不自动触发**的 Skill，由其他 Skill 通过 Skill tool 调用或用户显式调用；它的 `SKILL.md` 只做索引，正文放在两份文档里：

**A. 判断底线（约 10 条不变量）**

- Scope：不越出已确认目标；不覆盖或吞并他人改动。
- Knowledge：区分观察、推断、未知；不编造来源、能力或执行结果。
- Decision：会改变需求或契约的未决选择交回有权决定的人；变更只改负责方，再同步受影响产物。
- Authority：任务、工具、交接本身不增加授权；下游只能收窄，不能扩大。
- Evidence：预期来自确认需求，不由待验证实现反推；证据绑定候选、环境、执行者、覆盖范围。
- Recovery：外部写入结果未知时不盲目重试；接管前确认写入方已停止。

**B. 产物词汇（6 个槽位的字段与 ID 约定）**

第 1 节的表就是正文；共享层只保证所有 Skill 对“槽位叫什么、字段有哪些、ID 怎么编”理解一致。

### 3.2 每个 Skill 的内嵌模式

每个 `SKILL.md` 增加两个很短的小节，放在方法之前：

```markdown
## 底线（独立安装时自足）
- <本 Skill 必须守住的 3–5 条，措辞自足，不依赖其他 Skill>

## 产物
- 读：<需要哪些槽位及字段>
- 写：<自己拥有的槽位与必填字段>
- 需要与其他 Skill 对齐槽位和字段时，调用 `cstack-core` Skill；未安装时以本节为最小自足版。
```

原则：

- **只内嵌本 Skill 需要的部分**，不复制整份 principles。
- 内嵌部分写“字段与判据”，不写别的 Skill 的流程。
- 调用了 `cstack-core` 就按它的词汇对齐；没装时内嵌足以独立运行。**没有硬依赖。**

### 3.3 打包方式

- 推荐：发行 `cstack-core`（`SKILL.md` 索引 + `PRINCIPLES.md` + `ARTIFACTS.md`）与各 Skill 同目录安装，作为唯一权威词汇表；其他 Skill 需要时调用它。
- 单 Skill 安装：靠内嵌“底线 + 产物”块工作；跨 Skill 交接时，对方 Skill 也内嵌同名同义字段，因此仍能对上。
- 约束：**不能既宣称“单目录独立”，又要求读取根目录共享文件且无内嵌兜底。** 这条现在满足。

### 3.4 长度预算

- 主 `SKILL.md`：判断结构 + 完成判据 + 底线/产物，通常 40–95 行；结构越复杂允许越长，但超出就把细节移到 `references/`。
- 超过这个量级的细节（模板、示例、检查清单）放同目录 `references/`，按需读取。
- 一个 Skill 的篇幅由它需要多少不可压缩的结构决定，不再强行压到 22 行。

## 4. Skill 接口契约

这张表就是“链”的接线图：每个 Skill 读什么、写什么、何时停、交给谁。

| Skill | 读 | 写 / 产出 | 停止条件 | 交给 |
| --- | --- | --- | --- | --- |
| setup | 项目现状 | PROFILE | 稳定事实已记录，无重复权威 | 任意 |
| clarify | 请求、PROFILE | DECISIONS | 前沿清空、无静默假设、用户确认理解 | specify |
| specify | DECISIONS、PROFILE、代码事实 | SPEC（R/AC、Acceptance Seam） | 每条 R 有可判定 AC，来源清楚 | design / slice / 直接实现 |
| design | SPEC、代码事实 | TECH（D#、依据、权衡、Verification Seam） | 共享/难逆决策已定或判定不需要 | slice / verify |
| slice | SPEC、TECH? | SLICES（covers、blocked-by、本地 AC） | 每个切片可独立验证、依赖真实且无环 | implement |
| implement | SPEC、TECH?、SLICES? | 候选变更 + 自检记录（执行者 = 实现者） | 开发检查与自检完成 | verify / review |
| verify | SPEC、TECH?、参考方法 | EVIDENCE（逐 AC 判定、候选绑定） | 每条 AC 有 PASS/FAIL/NOT VERIFIED | review / ship |
| review | diff、SPEC、TECH?、EVIDENCE | 审查报告（不改槽位） | 有证据的发现已按影响排序 | 修复 / ship |
| ship | EVIDENCE、项目门禁、授权 | 就绪/授权/执行结果（短记录） | 就绪判断或具体阻塞已表达 | 用户 / 执行 |

关键点：
- `design`、`slice` 可以**判定为不需要**，但必须给出依据；不能因为省事跳过。
- `implement` 的自检记录不算 `EVIDENCE`；独立判断只能由 `verify` 写。
- `review` 不改任何槽位，只指出问题；修复后由 `verify` 重判受影响的 `EVIDENCE`。

## 5. 产物缺失时怎么降级

| 缺失 | 允许的做法 | 不允许 |
| --- | --- | --- |
| 无 PROFILE | 当场发现项目约定 | 编造项目事实 |
| 无 DECISIONS / SPEC | 用户请求足够清楚时，按会话契约执行；`EVIDENCE` 标注“来源：会话确认” | 从实现或测试反推需求 |
| 无 TECH | 单实现且无共享契约时直接做 | 跨模块共享设计时硬做 |
| 无 SLICES | 单一交付范围直接实现 | 多单元互相阻塞时假装没有依赖 |
| 无 EVIDENCE | 只能报告“未验证”，不能声明完成 | 用自检、绿色单测或截图替代逐 AC 证据 |

一句话：**缺产物不等于缺要求；缺的是“可引用的依据”，此时只能保留 NOT VERIFIED，而不是补一个假设。**

## 6. 样板：clarify 的输出到 specify 的输入

用最小实例说明“链条真的接上”，而不是又一套模板。

`DECISIONS`（clarify 写，可以是一段会话记录）：

```text
C1 账号删除后如何保留数据？→ 软删除，保留 30 天（用户确认 2026-10-29）
   可观察结果：删除后 30 天内可由管理员恢复；30 天后物理清除
C2 未定：30 天到期后是否需要通知用户？
```

`SPEC` 片段（specify 写，引用 C 与代码事实）：

```text
Goal: 账号删除支持可恢复窗口
R1  用户删除账号后进入可恢复状态                        来源：C1
AC1 删除后 30 天内，管理员可恢复该账号                  来源：R1；观察：管理端接口返回 200 且账号状态 active
AC2 第 31 天起，账号数据不可恢复                        来源：R1；观察：恢复接口返回 410
Acceptance Seam: 管理端恢复接口 + 账号状态查询（现有公开面）
未决：到期通知（C2）→ 阻塞 AC3，回到 clarify
```

`EVIDENCE`（verify 写）：

```text
候选：HEAD abc123 + 未提交 2 个文件（已记录）
AC1 PASS  方法：管理端恢复接口；环境：本地 staging；执行者：verify；覆盖：单账号
AC2 NOT VERIFIED  原因：无法等待 31 天；建议：时区/时钟注入或数据构造，需单独授权
```

这条链上，每个箭头都有明确产出与接收方；`AC2` 没有被“看起来通过”掩盖，`C2` 也没有被悄悄假设。

## 7. 对实施顺序的影响

在原方案的第 1 批里，先做这四件事即可验证方向：

1. 写 `cstack-core`：`SKILL.md` 索引 + `PRINCIPLES.md` + `ARTIFACTS.md`（第 1、3.1 节）。
2. 重写 `clarify`：补 design tree / frontier / rounds，输出 `DECISIONS`，内嵌“底线 + 产物”。
3. 重写 `specify`：消费 `DECISIONS`，输出 `SPEC` 的 R/AC 与 Acceptance Seam。
4. 用上面的 §6 实例走一遍：检查 `C1 → R1 → AC1 → EVIDENCE` 能否按 ID 对上、未决项是否保留。

通过后再做 `design / slice`，最后 `diagnose / verify / review` 等。

## 8. 主要风险与对策

| 风险 | 对策 |
| --- | --- |
| 内嵌要点与共享 principles 漂移 | 内嵌块只写“字段名 + 判据”；evals 检查各 Skill 的槽位名/字段是否一致 |
| 槽位过多又变成流程负担 | 严格按 §1.3 启用；简单任务只留会话级 DECISIONS + EVIDENCE |
| 与现有 Engineering Skills 命名冲突 | 明确映射：`TECH ≈ SOLUTION`、`SLICES ≈ tickets/*.md`、`DECISIONS ≈ decisions.md`；CStack 用槽位名，文件层可兼容 |
| 为了“独立”重复太多 | 内嵌只覆盖本 Skill 的输入/输出，不复制他人的方法与模板 |
| 仍然写成加长版散文 | 先做 clarify 样板；若主文件超过约 95 行，把细节移入 `references/`，而不是继续堆正文 |

## 9. 结论

- 产物链采用 **6 个逻辑槽位 / 4 层**，字段与所有权固定，形态自由；不引入参考体系里的文件名、模板、ticket 脚本或运行状态。
- 独立性采用 **principles 共享词汇 + 每 Skill 内嵌底线/产物**；共享文件存在时对齐，缺失时自足，没有硬依赖。
- 下一步的最小验证单位是 **clarify → specify 的 `DECISIONS → SPEC` 一段**，而不是一次性重写全部 Skill。
