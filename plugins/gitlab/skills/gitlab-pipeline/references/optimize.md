# 流水线优化

优化的目标只有一句话：找出流水线里真实存在的一段等待，消除它。判定依据是当前配置和已运行过的流水线数据，不是「这样写通常更快」的经验。一轮只改一处，改完用真实数据对比；拿不到两次数据就只报结构变化，不声称变快。

本文件的代码块都是**替换片段**，用来替换已有配置里的对应部分，不是能整份落盘的完整流水线。例如 `default: {interruptible: true}` 单独做文件会因为没有任何可见 job 而被 `glab ci lint` 拒绝，这是预期结果。改完按 [verification.md](verification.md) 选级校验。

## 先量，再改

改动前留基线，两条命令分别看结构和耗时：

```bash
# 结构：展开后的全部 job、stage、needs
glab ci config compile .gitlab-ci.yml

# 耗时：每个 job 的执行时长与排队时长，单位秒
glab api "projects/<id>/pipelines/<pid>/jobs" \
  | jq -r '.[] | [.name, .stage, .duration, .queued_duration] | @tsv'
```

再算墙钟与各 job 耗时之和的差距，差得越多说明允许并行的空间越大：

```bash
glab api "projects/<id>/pipelines/<pid>/jobs?per_page=100" | jq '
  def ts: sub("\\.[0-9]+Z$";"Z") | fromdateiso8601;
  map({start:(.started_at|ts), end:((.started_at|ts)+.duration)})
  | {sum:(map(.end-.start)|add)}
  | . + {wall:(map(.end)|max - (map(.start)|min))}'
```

改完运行同一条查询比较 `wall`，不要比 `sum`：`sum` 只随 job 增减变化，不会因为并行而变小。`wall` 与 `sum` 的差值就是 job 重叠省下的时间，差值接近 0 说明所有 job 都在串行，差值越大并行空间利用得越充分。

**这两个数必须来自你自己的流水线。** 本实例当前只有一个项目运行过流水线，且只有单个 job（`lint-checker`，约 167 秒），没有可供对比的多 job 数据。不要引用别处看来的耗时数字，也不要拿估算填空。

`duration` 不含排队时间。`queued_duration` 明显偏大时瓶颈在 runner 容量而不是配置，改 YAML 无效，先说明这一点。

## 一、串行改 DAG

**识别信号**：分属不同 stage、彼此没有依赖的 job 因 stage 顺序被迫排队。典型是 lint 与 test 同处 `test` stage，而 build 运行完才轮到它们。

```yaml
# 之前：lint 等整个 build 结束，但它根本不读 build 的产物
build:
  stage: build
  script: [make build]
lint:
  stage: test
  script: [npm run lint]
```

```yaml
# 之后：lint 从第一刻开始运行，test 仍拿 build 的产物
build:
  stage: build
  script: [make build]
  artifacts:
    paths: [dist/]
lint:
  stage: test
  needs: []
  script: [npm run lint]
test:
  stage: test
  needs: [{ job: build, artifacts: true }]
  script: [npm test]
```

`needs: []` 表示没有上游，立即开始；`needs:` 里只写有真实依赖的 job，全写上等于把 DAG 又变回串行。

**不要做**：stage 顺序本身是约束时不要动，例如要等所有测试运行完才允许进入的 deploy。加了 `needs:` 却漏掉 `artifacts: true`，下游会拿到空目录，这是改 `needs:` 最常见的破坏方式；`glab ci config compile` 只看得到拓扑，看不出产物是否接上，必须用真实流水线确认。

## 二、锁文件做 cache key

**识别信号**：`cache:` 缺失，或 key 只用 `$CI_COMMIT_REF_SLUG`。表现为依赖没变也每次重装。

```yaml
# 之前：每次推送都重新装
cache:
  key: $CI_COMMIT_REF_SLUG
  paths: [node_modules/]

# 之后：锁文件不变就命中
cache:
  key:
    files: [package-lock.json]
  paths: [node_modules/]
```

**不要做**：key 里塞 `$CI_COMMIT_SHA`，那等于关掉缓存。各栈路径与命中判断见 [caching.md](caching.md)。

## 三、收窄 artifacts 并设过期

**识别信号**：`artifacts:paths:` 写了 `./` 或整个仓库根，下游却只用其中一个子目录。

```yaml
# 之前：整个工作区打成包
build:
  artifacts:
    paths: ["./"]

# 之后：只传下游要读的
build:
  artifacts:
    paths: [dist/, public/]
    expire_in: 1 week
```

`expire_in` 不写时按实例默认保留期计算，长期积累会占满项目存储配额。构建产物给一到七天，测试报告一周到一个月，部署产物按回滚窗口定。

**不要做**：下游要用整个目录时不要为瘦身硬拆；`expire_in` 短于回滚窗口时，回滚当天可能取不到产物。

## 四、`parallel:matrix` 合并复制粘贴的 job

**识别信号**：同样的脚本按版本或平台抄了三四份，彼此只差 `image:` 或一个变量。

```yaml
# 之前
test-py-311:
  image: python:3.11
  script: [pytest]
test-py-312:
  image: python:3.12
  script: [pytest]

# 之后
test:
  image: python:${PY}
  script: [pytest]
  parallel:
    matrix:
      - PY: ["3.11", "3.12"]
```

展开后的名字是 `test: [3.11]`、`test: [3.12]`，用第 3 级 `ci/lint` API 的 `include_jobs=true` 核对数量，改错时这里最先露出来。

**不要做**：各版本的 `script:`、`rules:`、`variables:` 本来就不同时不要硬合并，把条件分支塞进 matrix 只会更难读；某个版本要 `allow_failure: true` 而其余不要，也不适合合并。

## 五、`interruptible: true`

**识别信号**：往同一分支连续推送两次，两条流水线同时运行，前一条的构建时间被浪费。

```yaml
default:
  interruptible: true
```

写在 `default:` 里给全部 job 打开，同 ref 有新流水线时旧流水线被取消。

**不要做**：部署、发布、数据库迁移这类有副作用的 job 必须显式 `interruptible: false`。中止到一半比多运行几分钟危险得多，这也是下面反模式里重复强调的一条。

## 六、镜像 pin 到具体版本

**识别信号**：`image: node`、`image: python:3` 这类滚动 tag。上游一旦变化，同一个 commit 昨天还能通过，今天就会失败。

```yaml
# 之前
image: node:lts

# 之后：大版本对齐项目，具体 tag 固定
image: node:22-bookworm-slim
```

版本从项目文件读，不要凭记忆：`engines.node`、`requires-python`、`go.mod`、`.ruby-version`、`rust-toolchain`。

**不要做**：不要用 `latest`，也不要停在 `lts` 这类会移动的别名上。反过来，钉到 digest 最稳但安全补丁也进不来，没有自动升版流程时钉到具体 tag 就够。

## 七、`key:files:` 与 `key:prefix:` 的取舍

**识别信号**：缓存有了，但每个新分支都从零装依赖。

```yaml
# A：只按锁文件，跨分支共享，复用率最高
cache:
  key:
    files: [package-lock.json]
  paths: [node_modules/]

# B：分支隔离 + 锁文件失效，适合长期分支
cache:
  key:
    prefix: $CI_COMMIT_REF_SLUG
    files: [package-lock.json]
  paths: [node_modules/]
```

A 适合锁文件稳定、分支生命周期短的项目；B 适合长命分支或依赖会被分支改动污染的项目，代价是每个新分支首次都冷启动。

**不要做**：同时改 key 结构和 paths 内容，两处一起动就分不清收益从哪来。先只改 key，量一次，再动 paths。

## 八、删掉重复的 `before_script`

**识别信号**：每个 job 里都抄了同一段 `npm ci`。

```yaml
# 之前：三处重复
build:
  before_script: [npm ci]
  script: [npm run build]
test:
  before_script: [npm ci]
  script: [npm test]

# 之后：一处定义
default:
  before_script: [npm ci]
build:
  script: [npm run build]
test:
  script: [npm test]
```

**不要做**：合并后行为必须完全不变。`default:` 会被每个 job 继承，包括原本没有 `before_script:` 的 job，合并会把安装扩散到不需要它的地方，这类 job 要么显式写 `before_script: []`，要么这次合并就不值得做。job 数、执行顺序、`duration` 都不该变，变的只是 YAML 长度。

## 反模式

**删掉 `needs:` 让流水线「看起来整齐」**。这是把 DAG 退回串行，墙钟直接变长。除非用户明确要串行执行，否则不做。

**给部署 job 设 `interruptible: true`**。在 `default:` 里统一打开时最容易漏掉这一点，中止到一半的部署可能留下半套状态，回滚比多等几分钟贵得多。

**cache 不设 key**。只剩 `paths:` 的 cache 被所有分支所有 ref 共用一份，内容互相覆盖，通常比不缓存更糟。任何 cache 都要有 key。

**为优化而优化**。没识别到具体等待就改结构，收益是零甚至负的：多出来的 matrix 维度、拆开的 artifact、额外的 cache key 都在增加维护成本。改动必须能指出它消掉了哪一段等待、这段等待值多少秒。

## 报告口径

说清三件事：改了什么（diff 形式）、用哪条命令量的、前后各是多少。只报结构变化时明确说「未测耗时」并给原因，不要用「应该会更快」替代数字。同一处改两轮没拿到收益就停，把数据和当前配置交回，不再叠加改动。
