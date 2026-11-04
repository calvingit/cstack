# 缓存与产物

`cache:` 配错不报错，只是流水线一直慢；`cache:` 与 `artifacts:` 用反了，则会在某个下游 job 上偶发失败且很难归因。

## 依赖进 cache，产物进 artifact

| 维度 | `cache:` | `artifacts:` |
| --- | --- | --- |
| 装什么 | 依赖、包管理器下载物、编译中间结果 | 本流水线产物、测试报告、可部署目录 |
| 生命周期 | 跨流水线，同 key 反复复用 | 单条流水线内，按 `expire_in` 过期 |
| 传递保证 | 无，job 之间不构成依赖 | 上传成功即可被下游取，取不到即失败 |
| 可靠性 | 尽力而为，可被清理、覆盖、跳过 | 缺失立刻暴露 |

判据一句话：下游必须原样拿到、丢了就阻塞的走 artifact；丢了能重装、只为省时间的走 cache。

交叉使用有两个具体后果。依赖塞进 artifact，每个下游 job 都要下载整棵依赖树，产物体积翻几倍，下载时间反而超过重装。产物塞进 cache 更隐蔽：cache 不参与 `needs:` 的依赖解析，也不保证送达，runner 缓存被清理或同一 key 被别的 job 覆盖后，下游拿到空目录，产出错的结果却不报错。凭据与 `.env` 一律不进 cache。

## key 的四种写法

key 决定共享范围，写错只有两个方向：太大互相污染，太小永远冷启动。

| 写法 | 适用 | 不适用 |
| --- | --- | --- |
| `key: { files: [package-lock.json] }` | 默认选择。锁文件不变就命中，跨分支跨流水线复用 | 无锁文件，或锁文件只约束部分依赖时，把清单文件一并列进 `files:` |
| `key: $CI_COMMIT_REF_SLUG` | 分支间依赖差异大，共享缓存互相污染过 | 分支开得勤的仓库：每个新分支都冷启动，只剩上传成本 |
| `key: $CI_JOB_NAME-$CI_COMMIT_REF_SLUG` | 同分支内几批 job 缓存内容确实不同，如 lint 装 tooling、build 装全量 | 不要当作「避免冲突」的默认手段：多一个 key 就多一份存储和一次冷启动 |
| `fallback_keys: [$CI_DEFAULT_BRANCH]` | 主 key 未命中时回退，新分支首次推送可基于默认分支缓存增量更新 | 治不了 key 抖动：key 含每次提交都变的量时，每次仍先读到旧缓存再失效 |

```yaml
cache:
  key:
    files: [package-lock.json]
  fallback_keys: [$CI_DEFAULT_BRANCH]
  paths: [node_modules/]
```

四种写法在 CE 16.11 上 `glab ci lint` 均通过；更老的实例或开了保护分支独立缓存的实例，先按 [SERVER-MATRIX.md](../../gitlab-core/references/SERVER-MATRIX.md) 探测。

## 按栈的缓存路径

| 栈 | `paths:` | 必须配套的变量 |
| --- | --- | --- |
| Node | `node_modules/`、`.npm/` | yarn Berry 换 `.yarn/cache/`，pnpm 换 `.pnpm-store/` |
| Python | `.cache/pip/`、`.cache/pypoetry/` | `PIP_CACHE_DIR`、`POETRY_CACHE_DIR` 指向项目内 |
| Go | `.go/pkg/mod/`、`.cache/go-build/` | `GOPATH: $CI_PROJECT_DIR/.go`、`GOCACHE: $CI_PROJECT_DIR/.cache/go-build` |
| Ruby | `vendor/bundle/` | `BUNDLE_PATH: vendor/bundle`；若项目用 `bundle config set --local path vendor/ruby`，路径随之改成 `vendor/ruby/`，两者只是目录命名不同，不用统一 |
| Rust | `.cargo/registry/` | `CARGO_HOME: $CI_PROJECT_DIR/.cargo`；`target/` 不缓存 |

第三列不是可选优化。容器里的 `$HOME` 通常是 `/root`，不在 `$CI_PROJECT_DIR` 下，而 `cache:paths:` 只认工作目录内的相对路径。Go 的 `GOPATH` 默认 `$HOME/go`、Rust 的 `CARGO_HOME` 默认 `$HOME/.cargo`，不显式改到项目内，paths 写了也不会被缓存，这是「配了却不命中」最常见的原因。Rust 的 `target/` 体积大，跨分支还会拿到别的 feature 组合下的产物，只缓存 registry 足够。

## policy 给哪类 job

`pull-push` 是默认值，给真正安装依赖的那个 job，一般只有它。`pull` 给测试、lint、扫描这类消费依赖但不改依赖的 job。`push` 给 `.pre` 里的专用预热 job。

```yaml
.cache-base:
  cache:
    key: { files: [package-lock.json] }
    paths: [node_modules/, .npm/]

warm-cache:
  extends: .cache-base
  stage: .pre
  cache: { policy: push }

test:
  extends: .cache-base
  cache: { policy: pull }
```

`extends:` 与 `default:` 在这里行为不同：前者深合并，只覆写写出的字段，所以上面只改 `policy` 就够；后者整块替换，job 里只写 `policy: pull` 会丢掉 key，退化成所有分支共用的缓存，比不缓存更糟，此时必须把 `key`、`paths` 一并重写。

## 从日志判断是否命中

展开 `Restoring cache` 与 `archive_cache` 两段，按关键字识别，措辞随 runner 版本和 executor 而变：`Checking cache for <key>...` 开始查找；`Successfully extracted cache` 是命中并解压完成；`Cache file does not exist` 与 `Failed to extract cache` 都是未命中；`Created cache` 是写入成功；`Not uploading cache <key> due to policy` 说明该 job 是 `pull`，不写。

一段未命中的日志大致长这样（措辞由 runner 版本和 executor 决定，按关键字识别，不要逐字比对）：

```
Checking cache for <key>...
WARNING: Cache file does not exist
Failed to extract cache
Not uploading cache <key> due to policy
```

它同时说明两件事：key 后缀带 `-protected` 是 runner 按 ref 保护状态追加的，保护分支与非保护分支各存一份、互不复用；`due to policy` 说明该 job 是 `pull`，从不写缓存。全部 job 都 `pull`，缓存就永远没人写，每次都未命中。

**这些日志行没有在本实例验证过。** 本实例当前只有一个项目配了流水线，其 runner 是 shell executor，实际作业日志里没有任何缓存相关行，因此上面只是按 GitLab 缓存机制的通用形态写的示意，不是本实例实测得到的日志。换到真有缓存的实例后，先运行一次带 `cache:` 的流水线，用实际日志替换这段再引用结论。

## 缓存不命中的常见原因

按排查顺序分三组：先看 key，再看环境，最后看谁在写。

**key 的问题。** key 每次都在变，多半是因为里面含 `$CI_COMMIT_SHA`、`$CI_PIPELINE_ID` 这类每次提交或每条流水线都不同的量，日志里 `Checking cache for` 每行都是新值。另一种是配置退化：job 级 `cache: []` 直接关掉了缓存，或者覆写 cache 时漏写了 `key`。

**环境的问题。** 缓存目录不在声明范围内时，先回看上一节第三列的配套变量，`$HOME` 下的目录不会被缓存。换了机器，命中率也会骤降：缓存只存在于执行过的那台 runner，`tags:` 混用多台非共享 runner 时，命中基本靠运气。保护分支与非保护分支各存一份，跨两者不会复用。缓存体积超过实例上限时，runner 只给一条 WARNING 就不存了，日志里不会报错。

**写的问题。** 全流水线都是 `pull` 时没有任何 job 写缓存，写缓存的那个 job 被 `rules:` 挡掉也是同样的结果。多个 job 同时对同一 key 执行 `push` 会互相覆盖，后完成的赢。

命中也不等于变快：解压几十万文件有时比重新安装还慢，而且这一步的耗时不出现在缓存日志里。要判断缓存是否真的带来了收益，得比较两次完整流水线的 job 时长，按 job 名对齐 `duration` 再下结论；拿不到两次真实数据就只报配置变化，不声称变快：

```bash
glab api "projects/<id>/pipelines/<pid>/jobs" \
  | jq -r '.[] | [.name, .stage, .duration, .queued_duration] | @tsv'
```
