# 分级校验：选级、读结果、写缺口

改动 `.gitlab-ci.yml` 之后，能做的校验只有静态的这几级，越往后越贵。选最便宜且能捕获这次改动的那一级，运行后按三种状态写结论。

本文件记录的命令在 GitLab CE 16.11.10 + glab 1.124 上实测，`enterprise: false`。换实例、升版本或换订阅级别后，先按 [SERVER-MATRIX.md](../../gitlab-core/references/SERVER-MATRIX.md) 重新探测，不要直接套用这里的结论。

## 三级阶梯

| 级 | 命令 | 能捕获什么 | 前提 |
| --- | --- | --- | --- |
| 1 语法 | `glab ci lint <file>` | YAML 语法（带行列号）、`include: local:` 文件不存在、job 名冲突、stage 名不存在、`needs:` 引用不存在的 job | 必须在能对上 GitLab 项目的仓库里运行 |
| 2 合并 | `glab ci config compile [file]` | 合并 `include`、`extends`、`!reference`、`default:` 之后的完整配置；配置有错时退出 1 | 同样要求 GitLab 项目上下文 |
| 3 展开 | `glab api --method POST "projects/<id>/ci/lint" -f "content=$(cat <file>)" -f "include_merged_yaml=true" -f "include_jobs=true"` | 服务端解析后的 `merged_yaml` 与 `jobs` 数组，含 name / stage / script / needs / when / allow_failure | 项目上下文与网络可达；`content` 走表单提交 |

第 1 级在配置有效时退出 0 并输出 `✓ CI/CD YAML is valid!`，无效时退出 1 并给出具体错误。**第 1、2 级都要求 GitLab 项目上下文**，这一点与直觉相反：`ci config compile` 编译的虽然是本地这份配置，但它同样要绑定到 `glab` 的当前项目，`include: local:` 也按项目仓库内容解析。remote 指向 GitHub 时，两条命令报同一个错 `You must be in a GitLab project repository for this action: none of the git remotes ... correspond to the GITLAB_HOST`，退出码 1。这不是配置有错，而是校验手段受限：换到对应实例的仓库再运行，或改用第 3 级并显式指定项目 ID。

**不要默认用 `glab ci lint --dry-run --include-jobs`。** 在本实例上，保护分支报 `You do not have sufficient permission to run a pipeline on 'main'`，指定非默认 ref 报 `Reference not found`。两种失败都与配置无关，展开 job 请走第 3 级。

**工作区里的 `include:` 目标文件对三级校验都不可见。** `include: local:` 由服务端按项目仓库内容解析，改过 include 文件但没推送到项目时（无论本地是否已提交），第 1、2 级都会报文件不存在；第 3 级提交的是主配置内容，include 仍按仓库解析。这不是配置错误，是校验边界。

第 3 级返回 JSON，三个字段各有各的用途：

| 字段 | 用途 |
| --- | --- |
| `valid` / `errors` | 与第 1 级同源的结论，`false` 时把 `errors` 原文贴出来 |
| `merged_yaml` | 看合并后的字段实际长什么样，`extends` 与 `default:` 是否按预期覆盖 |
| `jobs` | 看作业清单：改了 `rules:` 之后还剩几个、各自的 `stage` 与 `when` 是什么 |

`jobs` 里没有某个作业，比日志里报错更早说明问题：要么 `rules:` 没匹配上，要么 `workflow:rules:` 把流水线整个关掉了。这两种情况在第 1、2 级里都看不出来。

## 按改动类型选级

| 改动 | 最便宜的一级 | 说明 |
| --- | --- | --- |
| 改缩进、加引号、调块标量 | 1 | 语法错误带行列号，直接定位 |
| 加一个 job | 1 | 顺带能查 `stage:` 与 `needs:` 是否指向已存在的名字 |
| 改 `stage:` 或增删 `stages:` 数组项 | 1 | stage 名不存在会直接报错 |
| 改 `needs:` 的目标 | 1 | 引用不存在的 job 会报错 |
| 改 `include: local:` 路径 | 1 | 前提是文件已经提交 |
| 改 `include: template:` / `project:` / `remote:` | 2 | 要合并进来才能看出实际生效的字段 |
| 改 `extends:`、隐藏 job 或 `!reference` | 2 | 继承与引用只有合并后才能核对 |
| 改 `default:` | 2 | 影响面是合并后的全部 job |
| 改 `rules:` 或 `workflow:rules:` | 3 | 要看 `jobs` 数组里到底剩几个 job、各是什么 `when` |
| 改 `cache:` | 真实流水线 | 三级都只确认语法，不判断 key 是否稳定命中 |
| 改 `artifacts:` | 3，再加真实流水线 | 第 3 级只能看到路径声明，文件是否真的产出要等执行 |
| 改 `parallel:` | 3 | 矩阵展开结果在 `jobs` 数组里 |
| 加 `include: component:` | 视实例而定 | 本实例报 `the component path is not supported`，跨实例组件不支持 |

`cache:` 最能说明问题：`glab ci lint` 通过只说明这一块语法合法，三级静态校验都不判断 key 是否稳定命中。`key` 会不会每次推送都变、`paths` 与实际写入目录是否对得上，三级静态校验都给不出答案。

## 退出码语义

| 退出码 | 含义 | 该做什么 |
| --- | --- | --- |
| 0 | 这一级通过（配置能被解析） | 记录为「这一级通过」，不要升级成「流水线可用」 |
| 1 | 配置有错 | 把报错原文贴出来，按错误定位到行或字段 |

把退出码显式打出来，避免被 shell 或管道吞掉：

```bash
glab ci lint .gitlab-ci.yml;           echo "lint exit=$?"
glab ci config compile .gitlab-ci.yml; echo "compile exit=$?"
```

`0` 只说明解析通过，不等于流水线能运行。哪怕三级全过，`tags:` 匹配、保护分支规则、服务端变量、运行时镜像拉取都不在其中。

还有一类陷阱更反直觉：**退出码 0，输出却是错误信息**。`glab ci status` 与 `glab ci get` 依赖当前 git 分支名，分支对不上时输出 `no pipeline found for branch`，退出码仍是 0。这两条命令读输出，不读退出码；任何 `glab` 命令的输出里出现 `no pipeline`、`not found`、`permission` 时，先按失败处理再复核。

## 静态校验无法捕获什么

以下每一条都只能在真实流水线上确认，静态校验通过时要在报告里点名说尚未验证：

- **`tags:` 是否匹配到 runner。** 语义是调度侧匹配，配置合法但没有任何 runner 认领时，作业会一直 pending。本实例 runner 是 shell executor，`tags: []`。
- **保护分支规则。** `$CI_COMMIT_REF_PROTECTED` 这类条件的求值依赖服务端的分支保护配置，本地无从复现。
- **服务端变量。** `CI_PIPELINE_SOURCE`、`CI_MERGE_REQUEST_*` 由服务端注入，本地文件里看不到实际取值。
- **子流水线。** `trigger: include:` 的下游配置是否有效、是否被触发，本级校验只覆盖父配置里那一行声明。
- **`retry:` 与 `timeout:` 的实际行为。** 静态校验只确认字段写法合法，重试次数、退避与超时是否按预期触发，要等作业真的失败一次。
- **运行时镜像拉取失败。** 镜像标签不存在、私有仓库缺凭据，都在执行期才报错。本实例的 runner 是 shell executor，作业不拉镜像，这类问题在这里根本不会暴露。

## 三种状态的报告

每条结论只取这三种状态之一，不允许第四种模糊说法：

- **通过**：写明是哪一级、命令是什么、捕获到什么，例如「第 1 级 `glab ci lint` 退出 0，语法与 include 引用无报错」。
- **未能验证 + 原因**：原因要落到具体情形，不能写「环境限制」。可用的是：仓库无 GitLab remote、取不到项目上下文、没有推送授权、实例不支持该写法（如跨实例组件）、命令在本实例不可靠（如 `--dry-run --include-jobs`）。
- **未验证**：没运行过就是没运行过，写清这一级本该捕获什么、这次为什么没做。

一份报告长这样，三段缺一段都算没写完：

```
通过：第 1 级 glab ci lint 退出 0，语法与 include 引用无报错；
      第 2 级 config compile 退出 0，extends 与 default 合并结果符合预期。
未能验证：第 3 级 ci/lint API，未取得项目 ID，服务端解析结果未拿到。
未验证：cache 命中、tags 匹配、timeout 行为，只有真实流水线能确认，本次无推送授权。
```

报告里同时给出下一步：要确认 `cache:` 命中就得运行真实流水线，要确认 `tags:` 就得看调度结果。不要用前一级的通过去填补后一级的空缺。`glab ci lint` 通过不等于 `config compile` 通过，更不等于流水线可用。
