---
name: gitlab-pipeline
description: 当要新建或修改 GitLab 的 CI 配置、诊断失败的流水线或优化已有流水线时使用。不用于创建和评审 MR、不用于写提交信息、不用于分支变基，也不用于判断能否合并。
---

# gitlab-pipeline · 流水线的编写、诊断与优化

## 目标

用 `glab` 完成三件事：给还没有流水线的项目写出能运行的配置，把失败流水线定位到具体原因，把已经能运行的流水线提速。默认只读，改配置和推送都要单独授权。

本 Skill 面向自部署实例，记录的行为在 GitLab CE 16.11 + glab 1.124 上实测。换实例、升版本或换订阅级别后先按 [SERVER-MATRIX.md](../gitlab-core/references/SERVER-MATRIX.md) 探测，不要直接套用旧结论。

## 强制约束

- **先探测能力，再下结论。** 关键字、组件、`--dry-run` 的可用性随实例版本和订阅级别变化。没有经过 `glab ci lint` 确认的写法，不描述成可用。
- **校验结论只有三种状态。** 通过 / 未能验证（写明原因）/ 未验证。`glab ci lint` 通过只说明这份配置能被解析，不等于流水线可用。
- **不猜部署目标。** 没有明确目标时，deploy 只写成占位 job，不臆造集群、镜像仓库、凭据或云账号。
- **密钥不进配置。** 凭据不写进 YAML，也不从本地配置文件中读出再使用。
- **改配置不等于已提交。** 写文件、`git add`、提交、推送、建 MR、合并是不同动作，逐个授权。
- **不编造执行结果。** 没运行过的作业、没读到的日志、无法访问的实例，一律标为未验证并写明原因。

## 判断顺序

### 1. 确认实例与项目上下文

`glab ci lint`、`glab ci config compile` 和 CI Lint API 都要求能对上 GitLab 项目。remote 指向 GitHub 一类非 GitLab 仓库时，前两条都会报同一个错并退出 1，拿不到任何配置结论：

```bash
glab auth status                 # 确认当前 host 与登录态
git remote -v                    # 确认 remote 指向该实例
glab api "version" | jq '{version, enterprise}'
glab api "projects/<id>" | jq '{default_branch, shared_runners_enabled}'
```

`enterprise` 为 `false` 是社区版，组件目录、外部密钥管理、Epics 一类能力不适用。

**上下文缺失不等于配置有错。** 换到对应实例的仓库再校验，或改用 CI Lint API 显式指定项目 ID；两样都做不到，就在报告里写明静态校验未运行、结论仅有代码阅读依据，不要用未运行的校验冒充通过。典型误判：在 GitHub remote 的仓库里看到 `none of the git remotes ... correspond to the GITLAB_HOST`，转而去改 YAML。

### 2. 确认要做什么

三种意图的处理方式完全不同，先分清属于哪一种：

| 意图 | 入口 | 主要依据 |
| --- | --- | --- |
| 新建配置 | [recipes.md](references/recipes.md) 选栈模板 | 项目清单与锁文件 |
| 诊断失败 | [debugging.md](references/debugging.md) | 作业日志与失败签名 |
| 优化已有 | [optimize.md](references/optimize.md) | 当前流水线结构与耗时 |

改动涉及 `cache`、`artifacts`、`needs` 或 `parallel` 时，同时读 [caching.md](references/caching.md)。

### 3. 读现有配置与项目约定

已有配置时，先读 `.gitlab-ci.yml`，再顺着每个 `include:` 往下读：

- `include: local:` 读工作区里的对应文件。
- `include: component:` / `template:` / `project:` / `remote:` 只记录用了什么，不改它指向的内容。

然后对齐项目已有写法，新增的 job 要像项目里的 job：

- **隐藏 job 与 `extends:`**：有 `.base`、`.test-base` 一类基 job 时优先继承，不要从零写。
- **stage 落位**：读 `stages:` 数组，放进已有 stage；确需新增 stage 时单独说明，那是一次独立改动。
- **条件写法**：项目用 `rules:` 就跟着用 `rules:`；用 `only:`/`except:` 的老项目跟随现状，可提一句弃用，不当阻塞。
- **`default:` 继承**：`image:`、`before_script:`、`cache:`、`tags:` 已由 `default:` 覆盖的，不要重复声明。
- **依赖与产物流向**：别的 job 声明了 `needs:` 就照同样写法声明；需要上游产物时按项目已有写法接 `needs: [{ job: ..., artifacts: true }]`。
- **命名**：跟随现有风格，避开 `image`、`services`、`stages`、`variables` 等保留字。
- **`workflow:`**：项目已有就用，不要顺手加一个。

### 4. 新建还是增量

已有配置一律增量改，不动无关部分。没有配置时先给出结构化提案，确认后再写文件：

1. **识别到的技术栈**，一行，附把握程度（高 / 中 / 低）。
2. **建议的 stage 划分**，默认 `build`、`test`、`deploy`，deploy 可以是占位。
3. **建议的 job 表**：每个 job 一行，写清名称、stage、用途。
4. **`workflow:rules:` 默认不加**，并说明原因：开了 MR 之后每次推送会同时产生分支流水线和 MR 流水线。问用户要不要加，加了再写。

多个技术栈并存时（多种清单文件），说出主栈并请用户确认，不要自行决定。

### 5. 写出候选改动

新建按 [recipes.md](references/recipes.md) 的对应模板。无论新建还是增量，都遵循这套惯用写法：

- `default:` 收口共享字段。
- 隐藏 job 加 `extends:` 复用，不用 YAML 锚点。
- 有锁文件时用锁文件做 cache key，没有时退回清单文件。
- 不依赖上游产物的 job 加 `needs: []`，让它们一开始就能运行。
- 每个 job 一行注释说明用途。
- 镜像与运行时版本从项目文件里读（`engines.node`、`requires-python`、`go.mod`、`.ruby-version`、`rust-toolchain`），不要凭记忆写。

增量改动以 diff 形式给出来，只标出新增行，不要整份重贴：

```diff
  stages:
    - build
    - test
+   - security

+ secret-detection:
+   stage: security
```

### 6. 分级校验

按 [verification.md](references/verification.md) 的阶梯选择最便宜的一级。默认顺序：

```bash
glab ci lint <file>                              # 语法、include 引用、job 名冲突
glab ci config compile <file>                    # 合并 include 与 extends 后的完整配置
glab api --method POST "projects/<id>/ci/lint" \
  -f "content=$(cat <file>)" \
  -f "include_merged_yaml=true" -f "include_jobs=true"   # 展开后的 job 清单
```

三条命令都要在项目上下文里执行。第 1、2 级退出码 `0` 表示配置有效、`1` 表示配置有错；第 3 级看返回体的 `valid` 字段。**工作区里的 `include:` 目标文件对三级校验都不可见**：`include: local:` 由服务端按项目仓库内容解析，改过 include 文件但没推送到项目时（无论本地是否已提交），lint 与 config compile 仍报文件不存在。

推进到真实执行才是唯一能确认运行时行为的办法，但它要求推送，属于单独授权。无法进入真实执行时，按这三种状态报告缺口，不要用静态校验的结论冒充。

### 7. 按三种状态报告

报告按三种状态分别写：

- **通过**：哪一级校验实际运行过、捕获到什么，以及这一级覆盖的范围。写明 `glab ci lint` 通过只覆盖语法与引用，`config compile` 覆盖 include 合并与字段继承。
- **未能验证**：哪一级没运行、具体原因是什么。缺项目上下文、remote 不是 GitLab、没有推送授权、实例不可达，各自是一种具体原因。
- **未验证**：哪些事情只有真实流水线才能确认。`tags:` 匹配、保护分支规则、服务端变量、子流水线、`retry:` 与 `timeout:` 的实际行为，都要点名说尚未验证。

## 产物

- **读**：项目清单与锁文件、现有 CI 配置及其 include 链、`git remote -v`、实例版本与订阅级别、`glab` 命令的实际输出、作业日志。
- **写**：配置改动（diff 形式）、验证记录（三级各自是否运行、结论、缺口）。
- **不写**：平台状态、没发生过的流水线结果、未经确认的部署目标。

与 `gitlab-core` 统一安全边界时，读取它的 `SAFETY.md`；判断实例能力时，读取它的 `SERVER-MATRIX.md`。未安装 `gitlab-core` 时，以本 Skill 的强制约束作为最小可用版本。

## 报告与停止

- 报告固定包含：改了什么、哪一级校验通过、哪一级没运行及原因、剩余风险。
- 同一个错误两次修不掉就停下，把报错原文交回用户，给出一到两条可选路径，不再继续试。
- `401` 或权限错误不换凭据重试，不借用别的项目上下文，说明缺什么再停。
- 拿不到项目上下文时不猜项目，请用户指明或换到对应仓库再执行。
- 用户只要判断时停在判断；要求落地且已授权时，做到拿到结果或遇到具体阻塞为止。

## 参考

| 文件 | 何时读 | 内容 |
| --- | --- | --- |
| [recipes.md](references/recipes.md) | 新建配置、挑选镜像、确定部署写法 | 栈识别、六套起始模板、镜像与版本探测、部署走向 |
| [caching.md](references/caching.md) | 配置 `cache:`、`artifacts:`，或排查缓存不命中 | cache 与 artifact 的边界、key 设计、按栈路径、policy |
| [optimize.md](references/optimize.md) | 流水线能运行但慢、要并行、要省钱 | 八条优化手法与四条反模式，前后对比与度量 |
| [debugging.md](references/debugging.md) | 有失败流水线或作业日志要定位 | 日志分段、失败签名目录、误判清单、归因分类 |
| [verification.md](references/verification.md) | 选择校验层级、解释校验结果、说明缺口 | 三级阶梯、按改动类型选级、静态校验无法捕获什么 |
