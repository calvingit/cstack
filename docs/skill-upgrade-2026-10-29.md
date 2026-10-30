# CStack Skills 提升方案：把丢掉的“结构”找回来

> 性质：诊断与方案，不直接改 Skill 正文。
> 日期：2026-10-29。
> 对照对象：`docs/` 引用的 Matt Skills、Cursor pstack，以及本地 `calvingit/skills` 的 Engineering Skills。
> 目标：不是把参考仓库抄一遍，而是补回那些“删掉之后行为会退化”的核心概念，并让中间产物真正接起来。

## 0. 结论先行

1. **问题不是 SKILL 写得太少，而是三类东西被压平了**：方法的控制结构（决策树、前沿、循环、门槛）、中间表示（PROFILE / decisions / SPEC / SOLUTION / tickets / evidence）、交接契约（谁拥有哪个事实、谁授权、谁收尾）。
2. **CStack 的“后半程”很硬，“前半程”很软，链条从中间断开。** VERIFY / REVIEW / SHIP 保留了相当严谨的证据观，但它们要消费的 SPEC 的 R/AC、SOLUTION 的 D、tickets 的 delivery AC 在 CStack 里根本不存在。下游只能读散文、凭理解，也就无法做到它自己在提案 §5 里写的 `Contract → Candidate → Evidence → Decision`。
3. **提升的方向是分层的 CStack v2**：Kernel（不变量）+ Workflow Policy（风险选择）+ Artifact Chain（产物链）+ Method Skills（各有形态的方法），而不是继续给一批同构散文各加几句话。
4. **落地分批推进**：先补产物链和 DEFINE/PLAN，再补 BUILD 的机制，最后补知识层与可选能力。每一项都要能用真实任务观察证明“加了确实改变行为”，否则删掉。

## 1. 诊断：CStack 到底丢了什么

### 1.1 三个层次，缺一不可

一个工程 Skill 真正起作用，靠的不是原则清单，而是一个可重复的判断程序。这个程序由三层组成：

| 层次 | 作用 | 参考体系的做法 | CStack 现状 | 后果 |
| --- | --- | --- | --- | --- |
| 控制结构 | 保证判断**完整、可推进、能停** | grilling 的 design tree → frontier → rounds；debug 的 red-capable feedback loop；design 的 Design Review Gate；review 的轮次预算；to-tickets 的 tracer bullet | 大多压成“找出未决选择”“先复现”“比较少量方案”这类一句式建议 | 缺的是“怎么保证没漏、什么时候算完、卡住时怎么办” |
| 中间表示 | 让判断**能被下游继承** | `decisions.md` → `SPEC.md`（R/AC）→ `SOLUTION.md`（D）→ `tickets/*.md`（covers / blocked-by）→ evidence | 每个 Skill 都说“沿用已有文档，不要新建”，却没有任何 Skill 负责创建并命名产物 | 链条不存在，下游无法按 ID 引用，只能重新理解 |
| 交接契约 | 让职责**不越界、不丢事** | Task Contract、ownership matrix、closeout roles、amendment stop-write | 只有零散句子（“不授权实现”“交回调用方”），没有统一模型 | 角色边界靠自觉，审查/验收/实现容易互相替代 |

一句话：**CStack 保留了很多“判断的结论”，删掉了“产生结论的机制”。**

### 1.2 结构性证据

- 28 个 CStack Skill 里，有 18 个是 20–24 行、结构完全相同的“目标 / 方法 / 停止与交接”散文，另有 9 个是 11–14 行的条目式，只有 `visual-explain`（42 行）是另一种结构。参考体系里承担完整职责的 Skill 通常 46–120 行，而且**每个方法的形态都不一样**：有决策树、阶段清单、模板、schema、gate、预算。
- 长度差集中在“要产出结构”的环节，不在“要做判断”的环节：

| 阶段 | CStack Skill（行数） | 参考 Skill（行数） | 被压掉的核心概念 |
| --- | ---: | ---: | --- |
| DEFINE | clarify（22） | grilling（75） | design tree、frontier、rounds、问题格式、决策分类、事实由 Agent 查、frontier 清空才算完 |
| DEFINE | specify（22） | to-spec（116） | SPEC 的 R/AC、Acceptance Seam、R→AC 追溯、Create/Amendment、交接判断 |
| PLAN | design（22） | solution-design（111）+ codebase-design（67） | 设计依据先后、何时必须做方案、Design Review Gate、D-ID 追溯、Verification Seam、深模块词汇 |
| PLAN | slice（22） | to-tickets（80） | tracer bullet、blocking edges、covers 字段、ticket 本地 AC 命名空间、宽重构 expand–contract |
| BUILD | diagnose（22） | debug（72，Matt diagnosing-bugs 更长） | 先建 red-capable feedback loop、最小化复现、3–5 条可证伪假设、单变量探测 |
| BUILD | implement（23） | ticket-implement（18）+ quick-implement（61）+ closeout（37） | 契约继承、实现前证据计划、独立收尾角色、implementation receipt |
| VERIFY | verify（24） | verify（38） | 与参考最接近；缺 acceptance seam 与 verification seam 的区分 |
| VERIFY | verification-setup（22） | verification-setup（42）+ 项目 harness 契约 | Launch / Doctor / Drive / Observe / Isolate / Cleanup、Feature Map、“端口通不等于起来了” |
| REVIEW | review（23） | code-review（44，Matt 另加两轴） | P0–P3 严重度、Standards/Spec 两轴、报告契约、“发现必须有可达场景” |
| 知识层 | domain-model（11） | domain-modeling（87） | 术语格式、ADR 三条件门、权威位置发现、何时更新 |

结论很清楚：**CStack 的长处正好是参考体系也强调“判断证据”的 VERIFY / REVIEW / SHIP；短板集中在需要“把判断固化成中间产物”的 DEFINE / PLAN 和知识层。** 这不是偶然，因为首版提案把注意力放在“减少错误完成声明”，前端被当成可以一句话带过的准备。

### 1.3 “中间产物没衔接”的机制解释

CStack 每个 Skill 都强调“不要为了流程建文件”“沿用已有位置”。初衷是对的，但它产生了一个副作用：**没有任何 Skill 拥有产物的写入权**。

- clarify 说“只有用户要求或确有交接需要时才更新文档”，于是没有 `decisions.md`。
- specify 说“需要维护的规格，沿用项目已有的文件和格式”，于是没有 `SPEC.md` 的 R/AC 编号。
- design 说“只在确有共享和维护需要时才写文档”，于是没有 `SOLUTION.md` 的 D-ID。
- slice 说“沿用用户指定的 issue、任务文件或会话形式”，于是 tickets 没有 `covers`、`blocked-by` 这些可被下游消费的字段。
- verify 要求“逐条 AC 判断”，但上游没有稳定的 AC 可引用，只能临场从散文里提炼。

结果就是用户说的那句：**中间产物没有衔接上。** 这不是“少建了几个文件”，而是“没有权威来源”。CStack 的 verify、ship 之所以看起来成立，是因为它们把“读需求、读设计”当成理所当然；一旦没有 SPEC / SOLUTION，它们的严谨就落空了。

## 2. 原则：怎么补，才不是复制

1. **恢复结构，不恢复字数。** 该短的地方继续短；一个 Skill 的长度由它需要多少不可压缩的决策结构决定，而不是统一模板。
2. **产物是契约，不是流程。** 按需创建；一旦创建，它就是该项事实的唯一权威，下游用 ID 引用，不复制内容。简单任务可以只留在会话里。
3. **每个概念都要能回答三件事**：什么时候触发、产出什么、怎么判断完成。答不出来，就是装饰，删掉。
4. **判断与执行分离，但不等于多 Agent 编排。** 同一上下文的角色分离也可以（例如先独立定预期，再看实现），不能把“独立性”误解为必须多派 Agent。
5. **保留 CStack 的差异化**：candidate-bound evidence、evidence invalidation、按风险选择、跨 Runtime、中文自然表达。这些不要为了对齐参考而丢掉。
6. **不引入 Runtime、脚本编排、持久状态机。** 参考体系里的 ticket 图、`.loop/` 状态、subagent 派发属于宿主能力，不进入通用方法层。

## 3. 目标架构：四层

### 3.1 Layer 1：Kernel（稳定不变量）

参考工程体系用一份 `engineering-kernel.md` 固定 17 条不变量，分组是 Scope / Knowledge / Decision / Action / Evidence。CStack 现在把这些散落在 README 的“关键边界”里，每个 Skill 各说一遍。

建议 CStack 建一份**很小**的 kernel（6 组、约 15 条），只写“任何 Skill 都不得违反”的底线，不写方法细节：

- Scope：不越出已确认目标；不吞并他人改动。
- Knowledge：区分观察、推断、未知；不编造来源或结果。
- Decision：超出授权且改变契约的选择交回所有者；变更只改负责方，再同步受影响产物。
- Authority：任务/工具/交接本身不增加授权；下游只能收窄，不能扩大。
- Evidence：预期来自确认需求，不由待验证实现反推；证据绑定候选、环境、执行者、覆盖范围。
- Recovery：外部写入结果未知时不盲目重试；先确认写入方停止再接管。

关键点：kernel 是**判据**，不是流程；它不规定顺序、文档或工具。

### 3.2 Layer 2：Workflow Policy（按风险选择）

CStack 提案 §4 有四维（Uncertainty / Blast Radius / Verification Difficulty / Reversibility），但落到 Skill 里就变成各写一句“按风险决定”。建议抽出独立策略，回答“当前事实 → 需要哪些方法和独立检查”：

| 当前事实 | 选择的动作 |
| --- | --- |
| 行为、范围、验收已确认，影响局部，现有检查足够 | 直接实现 + 相称验证 |
| 行为/范围/验收有未决选择 | clarify；需要共享或版本化时再 specify |
| 存在跨模块的共享类型、接口、状态、迁移 | design（与 ticket 数量无关） |
| 有多个可分别交付、存在真实依赖的单元 | slice → tickets |
| 缺可重复的观察方法 | verification-setup |
| 高影响或难以观察 | 加强证据与独立审查，但不自动等于拆票 |

四维要分开看，不能合成一个分数；可逆性（Reversibility）要单独提示：数据与外部副作用不能靠回滚代码撤销。

### 3.3 Layer 3：Artifact Chain（最关键的补丁）

> 2026-10-29 决策落定：采用 6 个逻辑槽位（PROFILE / DECISIONS / SPEC / TECH / SLICES / EVIDENCE），形态自由、不照抄模板，详见[产物链与独立性设计](artifact-spine-2026-10-29.md)。

这是“衔接中间产物”的正面回答。产物链不是必经流程，而是一组**可按需启用的权威槽位**。

| 产物 | 内容 | 唯一写入者 | 消费方 | 何时必须有 |
| --- | --- | --- | --- | --- |
| `PROFILE` | 稳定项目事实：任务目录、需求权威、术语表、ADR 根、验证入口 | project-setup | 全流程 | 项目有稳定约定、需要跨任务复用时 |
| `DECISIONS` | 已确认的需求选择、理由、可观察验收、未决项 | clarify | specify | 访谈有结论、需要交接时 |
| `SPEC` | 问题、目标、范围、R（需求）、AC（验收条件）、Acceptance Seam | specify | design / slice / verify / review | 需求需要共享、版本化或交接时 |
| `SOLUTION` → `TECH` | 共享技术决策 D、备选、权衡、Verification Seam | design | slice / verify / review | 多实现需共享契约时（单实现也可能需要） |
| `TICKETS` → `SLICES` | tracer-bullet 切片：covers R/AC/D、blocked-by、delivery AC、constraints | slice | implement / verify | 有多个可分别交付的单元时 |
| `EVIDENCE` | 逐 AC 的 PASS / FAIL / NOT VERIFIED + 候选、环境、执行者、覆盖限制 | verify | review / ship | 有完成声明时 |

命名取 CStack 自己的槽位名，文件层可与现有 Engineering Skills 映射，避免造第二套语义：

- `PROFILE` ≈ 现有 `.agents/engineering-profile.md`；
- `TECH` ≈ 现有 `SOLUTION.md`；
- `SLICES` ≈ 现有 `tickets/*.md` 的 tracer-bullet 切片。

共享的是语义与 ID，不是文件名；CStack 不强制这些文件存在。

产物链的形状（`?` 表示按需）：

```text
PROFILE ──► DECISIONS ──► SPEC(R/AC) ──► TECH(D)? ──► SLICES(covers/blocked-by)? ──► EVIDENCE

回流：需求变化回 SPEC；设计变化回 TECH；拆分变化回 SLICES；候选或环境变化回 VERIFY。
```

规则三条：
1. 产物只由负责方写；下游只引用，不复制。
2. 相关条件变化后，只重判受影响的产物和证据，不全量重跑。
3. 没有产物也能工作；但一旦某产物存在，它就覆盖会话里的口头版本。

### 3.4 Layer 4：Method Skills（各有形态）

不同方法的 SKILL 应该有不同结构，而不是统一“目标/方法/停止”。例如：clarify 是“树 + 轮次”；diagnose 是“循环 + 阶段门槛”；slice 是“规则 + 校验”；review 是“范围 + 分级 + 报告契约”。**同构模板本身就是失真的一部分。**

## 4. 六个阶段的对齐与改法

下面每个阶段只写“要恢复什么、改成什么样”，不写成正文；具体措辞在实施时再定。

### 4.1 DEFINE

**clarify ← grilling。** 要恢复的不是“多问几个问题”，而是保证访谈完整、可推进、能停的结构：

- **design tree**：每个决定会分叉出依赖它的决定；先画树，再问。
- **frontier（前沿）**：所有“前置条件已定、现在就能问、不用猜答案”的未决选择。一轮问完整个前沿，等回答。
- **rounds（轮次）**：用户每答一轮，树被重塑，前沿向外推；依赖未答问题的问题放到下一轮。
- **事实由 Agent 查**：能看代码、文档、工具查到的，不问用户；查事实阻塞的是它下游的问题，不阻塞其余前沿。
- **决策分类**：用户可见行为/范围/验收/兼容/权限由用户定；跨模块架构与公共契约记为 SOLUTION 输入；私有实现细节 Agent 自己定。
- **完成判据**：前沿清空、没有静默假设，才算收敛；不是“问到自己觉得够了”。
- **产出**：`DECISIONS`（确认项、理由、可观察验收、未决项），供 specify 继承。

一个最小骨架（约 25 行，保留结构而不抄原文）：

```text
1. 建立/更新决策树，明确目标与范围。
2. 计算前沿：前置已定、现在可问的未决选择。
3. 整轮提问：编号、背景、选项、推荐及理由；一次问完前沿。
4. 用户回答后重算前沿；依赖未答项的问题留到下一轮。
5. 事实先自己查（代码/文档/工具）；只把真正的决定交给用户。
6. 把确认项写入 DECISIONS；前沿为空且用户确认理解一致后停止。
```

这不是复制 Matt 的格式，而是保留“树—前沿—轮次—完成判据”这套控制结构。

**specify ← to-spec。** 要恢复：

- **SPEC 是工程需求快照**：问题、目标、范围、R（需求）、AC（验收条件）、业务/外部/兼容约束。
- **R 与 AC 带稳定 ID**，AC 必须能独立判定；每个 in-scope R 都有 AC 覆盖。
- **Acceptance Seam**：需求在哪一层可被观察到（用户交互、外部契约响应、导出文件）；优先用现有公开面。
- **R→AC 追溯**：例子只能解释已确认规则，不能新增业务规则。
- **Create / Amendment 两种模式**：需求变了走修订，不是重开访谈，也不是新建 `SPEC-v2`。
- **交接判断**：确认 SPEC 后要独立判断两件事——是否需要 `SOLUTION`（共享设计），以及推荐 `直接实现 / 拆票`（与 ticket 数量无关）。
- 保持“不写实现细节、不写测试脚本”。

**新增 project-setup（可选）。** 参考体系用 `PROFILE` 记录“稳定的项目事实”（任务目录、需求权威、术语表、ADR 根、验证入口），不记录当前任务状态。CStack 没有这一层，导致每个 Skill 都要重新发现、产物也没有固定落点。建议作为“按需辅助”新增，不进入主流程。

### 4.2 PLAN

**design ← solution-design。** 要恢复：

- **何时必须做方案**：多模块/多调用方共享类型或契约；新增或修改跨模块接口/归属/依赖方向；多个实现要遵守同一状态机/生命周期/并发；需要 expand–contract 或迁移；用户或项目明确要求共享技术约束。**ticket 数量不是判据**，单个执行单元也可能需要。
- **设计依据的先后**：用户请求与 SPEC → AGENTS/架构/ADR → 同域稳定实现 → 当前生产主路径 → 更新的相似实现 → 通用原则；现存代码是证据，不是绝对权威。
- **Design Review Gate**：涉及新公共抽象、新领域模型、API/事件契约、数据模型、权限模型、长期架构方向、多个合理长期方案时，才停下来问用户；私有方法、文件布局不问。
- **D-ID 追溯**：每个 D 至少引用一条 R/AC 或一个可观察的代码事实（路径/符号），记录决策、理由、权衡。没有依据的 D 不成立。
- **Verification Seam**：技术正确性在哪一层可被检查（如集成测试、契约测试），与 SPEC 的 Acceptance Seam（公开观察）分开。
- **Amendment**：SPEC 含义不变时只改受影响 D，保留不相关 D。

**新增 codebase-design（独立 Skill）。** 这是 CStack 现在缺失、但影响设计质量最深的一块词汇：深模块、Interface（不只是签名）、Implementation、Depth、Seam、Adapter、Leverage、Locality、删除检验、design-it-twice。它回答“一个已知设计点该怎么成形”，不替代 design（是否要做方案）和 architecture-review（整体架构是否成立）。没有这套语言，design 和 review 只能用“接口设计得好不好”这种空话。

**slice ← to-tickets。** 要恢复：

- **tracer bullet（纵向切片）**：每个切片穿过交付需要的所有层（数据、接口、UI、测试、必要文档），完成即可演示或验收；不是一个“先建所有接口”的横向层。
- **blocking edges（真实依赖）**：只有“缺了前一项，后一项会开始错”才算阻塞；没有阻塞的即可启动（frontier）。不为了叙事顺序造线性链，不成环。
- **ticket 是稳定交付契约**：`covers.requirements` / `covers.spec_acceptance` / 引用 D / `constraints` / ticket 本地 AC（与 SPEC AC 不同命名空间）。执行状态与证据属于运行时，不写回 ticket。
- **共享契约落在第一个真正使用它的切片上**；只有真实阻塞（schema 生成、expand–contract、兼容层）才设准备型 ticket。
- **宽重构例外**：一次机械改动横扫全仓、无法独立变绿时，用 expand → migrate（按包/目录分批）→ contract，而不是硬塞纵向切片。
- **校验拆分**：标题、blocked by、交付什么、设计依据；普通拆分不需要用户逐项确认，暴露了产品/范围/优先级/兼容/共享设计选择才回上游。
- 对于大而模糊、跨会话的工程，再考虑可选的 **wayfinding**（地图 + 战争迷雾 + 决策工单），不要用 slice 硬扛。

### 4.3 BUILD

**implement ← quick-implement / ticket-implement + closeout。** 要恢复：

- **契约继承**：读调用方给的 SPEC / SOLUTION / ticket 写范围；下游只能收窄，不能扩权；冲突交回。
- **实现前的证据计划**：先把每条 AC 对到一个足够的方法、前置条件和覆盖限制，再动手；缺方法就报缺口，不把“跑通命令”当验收。
- **独立收尾角色**：`simplify`（审查模式）→ `verify` → `review`，默认分开执行并各自消费真实报告；省略的角色记为“未运行”，不能记为“通过”。收尾分级按影响的 blast radius，`verify` 永不省略。
- **implementation receipt**：列出适用的 SPEC / SOLUTION、基线、既有改动、实际改动、验收证据、验证、简化、审查、未验证项。
- **硬停**：已有 ticket 图或活跃写入方、目标/范围/结果不清、缺共享设计，都先停受影响部分。

**diagnose ← debug / diagnosing-bugs。这一项要最大幅度重写。** 参考体系里，诊断的核心不是“尝试复现”，而是**先造一个能变红的反馈回路**；没有这个回路就不进入假设阶段。要恢复：

- **Phase 1 反馈回路**：优先真实路径上的失败测试 → curl/CLI/浏览器自动化 → 重放抓包/日志 → 一次性脚本。回路要**red-capable**（能抓住用户描述的那个症状）、确定性、够快、可无人运行。
- **Phase 2 复现 + 最小化**：先确认红；再把输入、配置、步骤逐个删到“每个剩余元素都是必要的”。
- **Phase 3 假设**：先列 3–5 条**可证伪**假设，每条带预测（“若 X 是原因，改 Y 会使 bug 消失，改 Z 会加重”）；不要单假设锚定。
- **Phase 4 探测**：每个探测对应一条预测，一次只改一个变量；调试器/REPL 优先，定向日志带唯一前缀，禁止“全量打日志再 grep”。
- **Phase 5 修复 + 回归**：有正确 seam 才写回归测试；没有正确 seam 本身就是发现（架构阻止了锁定 bug）。
- **Phase 6 清理**：删探针、复跑原始场景、记录根因。
- 明确红线：**没有 red-capable 回路，不得进入假设。** 这正是 CStack 现在缺的那句话。

**test-first ← tdd。** 现有版本方向对，补三点：TDD 是**纵向行为循环**（一测一实现，tracer bullet），不是“先写完全部测试”；测试价值看“行为破坏时变红、只改内部时仍绿”；不要为测试加生产接口。

### 4.4 VERIFY

**verify。** CStack 已经是强项，保留。补两点：Acceptance Seam（公开观察）与 Verification Seam（技术检查）分开；实现前的证据计划是导航、不是判决，仍要独立核对适用性。PASS / FAIL / NOT VERIFIED 与“环境失败不是产品失败”保留。

**verification-setup ← verification-setup + 项目 harness 契约。** 要恢复可操作的 harness 结构：

- **Launch**：确切启动命令、怎么判断就绪、怎么关。
- **Doctor**：只读检查“这个实例值不值得驱动”（进程、版本、端口归属、认证）。
- **Drive**：真实选择器/命令，优先稳定句柄，不用坐标和 tab 顺序。
- **Observe**：抓什么证据、放哪、证据标准；走真实用户路径，不用内部 setter。
- **Isolate / Cleanup**：能否并行两个实例；只关自己启动的，不按进程名杀；清理不删证据。
- **Feature Map**：功能与验证方法的映射。
- 关键判据：**“起来了”指应用可用，不是端口有响应**（迁移和种子数据跑完、真实读请求通过）。

### 4.5 REVIEW

**review。** 补：

- **严重度 P0–P3**，且“严重度”与“是否阻塞本次变更”是两个决定。
- **两轴可选**：Standards（是否符合本仓有据可查的规范）与 Spec（是否忠实实现需求）分开报告，避免一轴掩盖另一轴。
- **报告契约**：结论、范围、按影响排序的发现、后续项、需求缺口、未验证范围、证据。
- **发现门槛**：可达场景 + 具体位置 + 实质后果；先查能推翻它的保护条件；“看起来安全”不算证明。
- **基线选择**：分支比较用 merge base，单提交看该提交的 patch，工作树含暂存/未暂存/相关未跟踪。
- 保留“审查轮次预算”：预算用尽而问题未解，是 HOLD 或请求决策，不能自动改判通过。

### 4.6 SHIP

**ship。** CStack 这块和各参考体系相比不弱（tstack 的 full-send/sol-loop 反而更激进）。补的是**词汇与产物绑定**：

- 状态词汇统一：Merge Readiness / Release Readiness；GO / HOLD / NO-GO；已准备 / 已推送 / PR 已创建 / 已入队 / 已合并 / 已部署分别表达。
- 明确消费 `EVIDENCE` 与 `SOLUTION`；证据失效规则（候选、基线、依赖、环境变化）写清。
- 权限分组：Inspect / Prepare / Merge / Deploy，口令不自动升权。
- 合并即触发部署时，两者一起评估但结论分开。

## 5. 横切能力：现在缺、但决定“思想完整性”

这些不一定是 Skill，但必须有明确位置，否则每个 Skill 都会重新长一遍：

| 能力 | 形态 | 作用 |
| --- | --- | --- |
| Kernel | `core` Skill（不自动触发，`SKILL.md` 只索引 `PRINCIPLES.md` / `ARTIFACTS.md`） | 稳定不变量与产物词汇，防越界与证据造假 |
| Task Contract | 独立文档 | 目标/范围/验收/决策边界/证据/恢复的六类边界，跨 Skill 交接的依据 |
| Ownership & Invocation | 独立文档 | 事实与产物归属、调用模型、三种写法（方法引用/角色派发/Skill 调用） |
| Workflow Policy | 独立文档 | 风险选择，避免每个 Skill 各自解释 |
| Closeout Roles | 独立文档 | simplify / verify / review 的分工、分级、独立性与证据消费 |
| Knowledge Protocol | 独立文档 | 长期发现回写给谁（测试、注释、runbook、ADR、领域文档） |

新增可选 Skill（不在主线，但补思想完整性）：

- **codebase-design**（深模块词汇，见 4.2）；
- **project-setup / profile**（稳定项目事实，见 4.1）；
- **wayfinding**（跨会话大工程的地图 + 战争迷雾 + 决策工单，见 4.2）；
- **challenge**（对已成形的方案做有边界的对抗审查）；
- **triage**（issue/PR 的 intake 状态机，可选，视是否使用 issue tracker）。

升级现有辅助 Skill：

- **domain-model**（从 11 行扩到能落地的版本）：术语格式（是什么，不是代码做了什么；择一规范词、记别名）、ADR 三条件门（难逆转 + 无上下文会意外 + 真实权衡）、权威位置发现（不假定固定路径）、何时更新术语与领域模型。
- **retro**：补“把教训编码进结构”的阶梯——架构消除 > 类型/lint/CI 拦截 > 测试 > 文档/规则；**同一类错误出现两次才立规则**；新检查要能拦住一个真实发生过的旧错误；避免把一次性失误变成通用规则。
- **research / impact / simplify / prototype / how / why**：现有质量尚可，补结构即可（impact 补“关键不变量要用运行证据”，prototype 补“保真度阶梯”，how/why 补明确的产出结构）。优先级低。

## 6. 落地路线

| 批次 | 内容 | 完成判据 | 风险/依赖 |
| --- | --- | --- | --- |
| **第 1 批 · 补链条** | kernel + task-contract + workflow-policy；clarify / specify / design / slice 重写；artifact 命名对齐 | 一个真实任务能从 clarify → specify → design? → slice 产出互相按 ID 引用的文件 | 需要先定“独立安装 vs 共享引用”策略（见 §8） |
| **第 2 批 · 补机制** | diagnose 重写（feedback loop）；verification-setup 补 harness；implement 补契约 + 收尾；verify/review 小修 | 注入“错误业务断言但单测绿”“伪验证（跳测试）”“候选变化后旧证据”三类样例能被拦住 | 依赖第 1 批的 SPEC AC 与 EVIDENCE |
| **第 3 批 · 补知识层** | project-setup/profile、codebase-design、domain-model、retro/knowledge-protocol；ship 词汇 | 设计与审查能用深模块语言；术语/ADR 有落点；复盘能产出被执行的规则 | 依赖第 2 批的稳定性 |
| **第 4 批 · 可选能力** | wayfinding、challenge、triage | 真实任务中正反路由、产物链引用闭合、失败注入可被发现 | 需要真实任务样例 |

不建议一次性全改。先把 `clarify` 按新结构重写成**样板**，评审通过后再批量，否则很容易把“补结构”做成“加长版散文”。

## 7. 如何判断改对了

用真实任务人工核验，至少覆盖：

1. **路由**：该触发 clarify 时触发、简单任务不触发；该做 design 时不跳过、局部改动不硬造设计。
2. **产物链**：从 DECISIONS 到 SPEC 的 R/AC，到 tickets 的 covers，到 EVIDENCE 的逐 AC，能否按 ID 对上；断链要能被发现。
3. **失败注入**：跳过的测试、放宽的断言、被屏蔽的门禁、mock 冒充真实服务，REVIEW/SHIP 是否阻断。
4. **候选失效**：验证后提交新代码、rebase、依赖变化，旧证据是否被重判。
5. **诊断纪律**：没有 red-capable 回路时，是否拒绝进入假设阶段。
6. **跨 Runtime**：加载、显式/隐式调用、Skill tool 行为是否一致。

每项都要能说明任务样本、模型、环境、工具和失败限制；单次演练只证明该场景。

## 8. 取舍与风险

- **长度 vs 加载成本**：不用“砍概念”解决，用“分层加载”解决——主 `SKILL.md` 只放判断结构与完成判据，细节放 `references/`，按需读取。参考体系正是这么做的。CStack 现在没有 references，是把所有东西都塞进 22 行，结果两头都受损。
- **独立安装 vs 共享 kernel/契约**：已定：唯一共享层是 `core` Skill（不自动触发，`SKILL.md` 只索引 `PRINCIPLES.md` / `ARTIFACTS.md`）；每个 Skill 内嵌本 Skill 需要的“底线 + 产物”要点，未装 `core` 时也能独立运行；详见[产物链与独立性设计](artifact-spine-2026-10-29.md#3-独立性principles--内嵌底线)。不能既宣称“单目录独立”，又依赖根目录共享文件而无内嵌兜底。
- **过度流程化**：门槛是“是否改变行为/风险”，不是“每次全跑六阶段”。简单任务继续直接做；产物按需创建。
- **照抄风险**：参考体系里绑定 issue tracker、Runtime、多 Agent 派发、脚本状态机的部分不要进 CStack；只吸收可迁移的判断结构。

## 9. 建议的下一步

1. 拍板 §8 的安装策略（打包 or 内嵌）。
2. 先写 `core`（`SKILL.md` 索引 + `PRINCIPLES.md` + `ARTIFACTS.md`）。
3. 用新结构重写 `clarify` 作为样板（保留 design tree / frontier / rounds / 完成判据），评审后再重写 specify / design / slice。
4. 重写 `diagnose`（feedback loop 优先）作为 BUILD 的第二个样板。
5. 再动其余 Skill，每批用真实任务人工核验。

## 附录 A：Skill 处置一览

| Skill | 处置 | 优先级 | 说明 |
| --- | --- | --- | --- |
| clarify | 重写 | P0 | 补 design tree / frontier / rounds / 决策分类 / DECISIONS |
| specify | 重写 | P0 | 补 R/AC、Acceptance Seam、Create/Amendment、交接 |
| design | 重写 | P0 | 补何时必须、依据顺序、Design Gate、D-ID、Verification Seam |
| slice | 重写 | P0 | 补 tracer bullet、blocking edges、covers、宽重构例外 |
| diagnose | 重写 | P1 | feedback loop 优先、最小化、可证伪假设 |
| verification-setup | 升级 | P1 | Launch/Doctor/Drive/Observe/Isolate/Cleanup、Feature Map |
| implement | 升级 | P1 | 契约继承、证据计划、收尾角色、receipt |
| verify | 小修 | P2 | Acceptance/Verification Seam 区分 |
| review | 升级 | P2 | P0–P3、两轴、报告契约 |
| ship | 小修 | P2 | 就绪词汇、EVIDENCE 绑定、权限分组 |
| test-first | 升级 | P2 | 纵向循环、测试价值判据 |
| test-audit | 小修 | P3 | 与 review 的测试发现边界对齐 |
| domain-model | 大升级 | P2 | 术语格式、ADR 门、权威发现 |
| retro | 升级 | P2 | 知识编码阶梯、两次才立规则 |
| project-setup | 新增 | P2 | PROFILE，稳定项目事实 |
| codebase-design | 新增 | P1 | 深模块 / Seam / 删除检验 / design-it-twice |
| wayfinding | 新增（可选） | P3 | 地图 + 迷雾 + 决策工单 |
| challenge | 新增（可选） | P3 | 对抗审查 |
| research / impact / simplify / prototype | 小修 | P3 | 补结构，不改方向 |
| architecture-review / ui-review / handoff / pr-feedback / performance | 保留/小修 | P3 | 方向成立 |
| bro / restate-goal / how / why / visual-explain | 保留/小修 | P4 | 沟通与解释类，按需 |
| report-style | 保留 | — | 汇报风格，不动 |

## 附录 B：概念来源对照（只列可迁移的）

| 概念 | 参考来源 | 用途 |
| --- | --- | --- |
| design tree / frontier / rounds | Matt grilling | clarify 的完整性与完成判据 |
| acceptance seam / R→AC | 我们的 to-spec、Matt to-spec | SPEC 可判定、可追溯 |
| Design Review Gate / D-ID / verification seam | 我们的 solution-design | design 的决策与追溯 |
| tracer bullet / blocking edges / expand–contract | Matt to-tickets、我们的 to-tickets | slice 的拆分规则 |
| red-capable feedback loop / 3–5 falsifiable hypotheses | Matt diagnosing-bugs、我们的 debug | diagnose 的纪律 |
| Launch / Doctor / Drive / Observe / Isolate / Cleanup、Feature Map | pstack create-verification-skill | verification-setup 的 harness |
| Prove It Works / Test Behavior / Build the Lever | pstack 原则 | 证据观与工具化 |
| 教训编码阶梯（架构 > lint/type > test > doc） | pstack /correct | retro 与 knowledge-protocol |
| deep module / seam / deletion test / design-it-twice | 我们的 codebase-design、pstack architect | 设计质量词汇 |
| P0–P3 / 两轴审查 | Matt code-review、我们的 code-review | review 的分级与分离 |
| Task Contract / ownership / closeout roles | 我们的 shared/*.md | 交接与职责边界 |
