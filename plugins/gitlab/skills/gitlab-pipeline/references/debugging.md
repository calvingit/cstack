# 失败流水线的诊断：日志分段、失败签名与归因

作业失败时，日志本身就是证据。先定位失败落在日志的哪一段，再按签名归类，最后才动手改。反复修改一份本来正确的 YAML 是诊断中最常见的浪费。

本文件记录的行为在 GitLab CE 16.11.10 + glab 1.124 上实测。换实例或升版本后，先按 [SERVER-MATRIX.md](../../gitlab-core/references/SERVER-MATRIX.md) 重新探测能力。

## 先拿到可信的日志

按 job ID 取 trace 是唯一不依赖终端形态的入口：

```bash
glab ci trace <job-id>
glab ci trace <job-name> -p <pipeline-id>   # 按名字必须带 -p 或 -b
```

按名字单独解析会报 `invalid job ID`，名字不是 ID。`glab ci view` 强制 TTY，Agent 环境里无法使用。

trace 带 ANSI 转义序列，先清洗再读：

```bash
glab api "projects/<id>/jobs/<job-id>/trace" \
  | sed -e 's/\x1b\[[0-9;]*m//g' > job.log
```

`glab ci get` 与 `glab ci status` 依赖当前 git 分支名，分支对不上时报 `no pipeline found for branch`，退出码仍是 0。判断有没有流水线看输出，不要看退出码。

一次失败通常牵连多个作业，先挑出要看的那个，不要逐个打开日志：

```bash
glab api "projects/<id>/pipelines/<pipeline-id>/jobs?per_page=100" \
  | jq -r '.[] | "\(.status)\t\(.stage)\t\(.name)\t\(.id)"' | sort
```

`status` 为 `failed` 的是失败作业；`allow_failure: true` 的作业失败时带警告标记，不拦住流水线，但仍值得查看。最后一列才是 `glab ci trace` 需要的 ID。同一个作业重试过会出现多行同名记录，取最新的一行。

## 日志的五个分段

一段作业日志按执行顺序分成五段，失败落在哪一段，指向的原因类型完全不同：

| 分段 | 日志特征 | 出错意味着 |
| --- | --- | --- |
| 拉代码 | `Getting source from Git repository`、`Checking out` | 凭据、分支或仓库地址有问题，与脚本无关 |
| `before_script` | 第一批 `$ <命令>` | 环境准备失败：装包、登录 registry、准备目录 |
| `script` | 作业主体的命令输出 | 代码、测试或构建失败，改脚本 |
| `after_script` | `Running after_script` | 收尾工作失败，不改变作业退出码，但现场可能已被破坏 |
| 产物上传 | `Uploading artifacts` 及其后的 `WARNING` | 路径写错或文件没生成，下游会缺产物 |

本实例的 runner 是 shell executor，`tags: []`，日志从拉代码直接开始，没有拉镜像那一段。日志里如果出现拉镜像的行，说明这个作业落在了另一台 runner 上，不要按本实例的行为推断。

`after_script` 这一段的失败不会把作业判为失败：日志里只有一行错误，作业状态仍是 passed。下游报「产物不存在」而当上游显示成功时，先回头查上游的 `after_script`。

## 失败签名目录

每条按「症状或报错 → 分类 → 静态校验能否捕获 → 修法」给出。静态校验指 `glab ci lint`、`glab ci config compile` 或 `ci/lint` API，分级说明见 [verification.md](verification.md)。

**配置错误**：静态校验能提前捕获，不该等到运行流水线才发现。

| 报错内容 | 分类 | 静态校验 | 修法 |
| --- | --- | --- | --- |
| 解析失败，第 1 级会连行列号一起报出 | 配置 | 第 1 级 `lint` | 按报出的行修缩进、引号或块标量 |
| 报 `include: local:` 的文件不存在 | 配置 | 第 1 级 `lint`，文件须已提交 | 路径相对仓库根，不相对当前文件 |
| 报某条 `needs:` 指向的 job 不存在 | 配置 | 第 1 级 `lint` | 补上目标 job，或删掉这条 `needs:` |
| 报 job 的 `stage:` 未定义 | 配置 | 第 1 级 `lint` | 加进 `stages:` 数组，或改用已有 stage |
| 报 job 名冲突 | 配置 | 第 1 级 `lint` | 改名，或合并成一个隐藏 job 配 `extends:` |
| 报 `the component path is not supported` | 配置 | 第 1 级会报出，但结论是实例不支持 | 本实例不支持跨实例组件，改用 `include: template:` 或内联 |
| 某个 job 在流水线里彻底不出现，日志里也没有它 | 配置 | 第 3 级 `jobs` 数组 | 看 `rules:`、`only:`、`workflow:rules:` 的求值结果 |

第 1 级的报错由服务端解析器给出，凡是解析期能判定的错误都在这一层暴露，文案随版本变化。表里列的是本实例实测到的几类；遇到表外的报错，按报错里的行号、job 名或字段名定位，不要先怀疑版本。

**环境错误**：配置没问题，但作业无法运行。

| 症状或日志特征 | 分类 | 静态校验 | 修法 |
| --- | --- | --- | --- |
| `command not found: X` | 环境 | 无法捕获 | X 不在 runner 的 PATH 里，先装再运行 |
| `Permission denied` | 环境 | 无法捕获 | 脚本或缓存目录权限问题，靠改 YAML 绕不过去 |
| `Could not resolve host`、下载卡住 | 环境 | 无法捕获 | runner 出网或 DNS 问题，先确认是否偶发 |
| `No space left on device` | 环境 | 无法捕获 | runner 磁盘满，清缓存与旧构建 |
| `ERROR: Job failed (system failure)` | 环境 | 无法捕获 | runner 侧异常，与配置和脚本都无关；同一 runner 上的作业会一起失败 |
| 作业一直 pending，没有日志 | 环境 | 无法捕获 | `tags:` 没有匹配的 runner；本实例可用标签为空 |
| 每天同一个作业都重新下载全部依赖 | 环境 | 无法捕获 | `cache:key` 太动态，或 `paths` 与依赖的实际写入位置不符 |

**运行时错误**：只有真实执行才暴露。

| 日志特征 | 分类 | 静态校验 | 修法 |
| --- | --- | --- | --- |
| `ERROR: Job failed: exit status 1` | 运行时 | 无法捕获 | 往上看一行，真正失败的是那条命令 |
| 测试断言失败 | 运行时 | 无法捕获 | 作业本身执行成功，问题在测试或代码 |
| `Killed`，或退出码 137 | 运行时 | 无法捕获 | 内存被打满，减少并发或分批运行 |
| `Job exceeded the timeout limit` | 运行时 | 无法捕获 | 作业确实太长，再谈 `timeout:` 或拆分 |
| `Uploading artifacts` 后跟 `no matching files` | 运行时 | 无法捕获 | `artifacts:paths` 与脚本实际产出的路径对不上 |
| 下游报文件不存在，上游状态 passed | 运行时 | 无法捕获 | 上游产物没传成，回看上传段与 `needs:artifacts` |

## 五条常见误判

看起来是版本或能力不支持，实际是用法问题。按顺序排除：

1. **`glab ci lint` 报 `none of the git remotes ... correspond to the GITLAB_HOST`，就认为 lint 不可用。** 实际上 remote 没有指向目标实例：要么指向另一个 GitLab 实例，要么根本不是 GitLab（比如 GitHub）。先运行 `git remote -v` 和 `glab auth status` 对齐 host 再重试；也不要换用别的项目上下文来「让它能运行」，那样校验的是别人的配置。
2. **API 返回 404，就断言实例不支持这个端点。** 先排除两种写法问题：项目路径里的 `/` 要编码成 `%2F`（`projects/group%2Fproject` 能命中，`projects/group/project` 不能）；路径里放的是 IID 还是全局 ID 要对，`pipelines/<iid>` 与 `jobs/<id>` 混用会同样返回 404。两者都对了再怀疑版本。
3. **`glab ci trace` 报 `invalid job ID`，就认为这个作业取不到日志。** 传进去的是 job 名字，不是 ID。按名字解析必须配 `-p <pipeline-id>` 或 `-b <branch>`。
4. **看到 `no pipeline found for branch`，就认为项目里根本没有流水线。** 这条只说明当前分支没有流水线。切到运行过的分支，或用 `-b` 指定。注意它的退出码是 0，按退出码判断会直接漏掉这个信息。
5. **`--dry-run --include-jobs` 报权限不足或 `Reference not found`，就认为配置有错。** 在本实例上保护分支会报 `You do not have sufficient permission to run a pipeline on 'main'`，指定非默认 ref 报 `Reference not found`。两种失败都与配置无关，是这个模式本身不可靠，展开 job 请走 `ci/lint` API。

## 归因：脚本真错还是 runner 环境

分清这两类，才谈得上给修法。配置解析通过、失败落在 `script` 段，优先怀疑脚本本身；失败落在拉代码段，或出现 `system failure`、`No space left`、退出码 137，属于环境面，改 YAML 改不好。

几条可操作的判据：

- **同一提交昨天能通过、今天不能**：属于环境面，runner、网络、缓存或凭据发生了变动，代码本身没动。
- **多个互不相关的作业在同一处一起失败**：共享环节出了问题，不是每个脚本恰好同时在各自的位置失败。
- **只有带 `tags:` 的作业一直 pending**：runner 标签匹配不上，脚本连执行机会都没有。
- **还没执行到脚本就失败的作业，和执行脚本后才失败的作业混在一起**：这是两批失败，按各自所在的分段分别归因，不要合成一个结论。
- **错误信息里出现路径或文件名**：问题多半在路径层面，先核对 `artifacts:paths`、`include: local` 和脚本里的相对路径。

YAML 已通过静态校验、失败又落在 `script` 段时，不要再动 `stages:`、`needs:` 或 `default:`。结构没问题，这些改动只会引入新问题，还会打乱原来的失败现场。

## 修完之后

脚本层面的修复无法靠 `glab ci lint` 证明：它只能证明 YAML 没坏，证明不了脚本已经修好；产物路径、`tags:`、缓存命中这类问题，静态校验连线索都给不出。结论按 [verification.md](verification.md) 的三种状态写：哪一级实际运行过、哪一级没运行及原因、哪些只有真实流水线才能确认。

同一个错误两次修不掉就停下，把报错原文交回用户，给出一到两条可选路径，不再继续尝试。
