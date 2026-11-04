# 起始模板、镜像与部署走向

新建 `.gitlab-ci.yml` 的顺序是：读清单文件定栈，照对应模板起手，把镜像 tag 和运行时版本换成项目自己声明的版本。本文件给六套能直接落地的模板、按栈的镜像取舍、版本探测信号，以及有部署目标时的四种走向。

六套模板共用一套写法：`default:` 收口公共字段，隐藏 job 加 `extends:` 复用，不依赖上游产物的 job 声明 `needs: []`，每个 job 带一行用途注释。模板只保证配置能被解析、作业定义完整；能否真正运行成功以真实流水线为准，静态校验只能确认到对应层级，分级见 [../SKILL.md](../SKILL.md) 第 6 节。

**哪些代码块能整份粘贴。** 六个「模板」小节里以 `default:` 开头的块是完整配置，可以直接作为 `.gitlab-ci.yml` 落盘。其余代码块都是片段，要替换或追加进已有文件。单独粘贴片段会被 `glab ci lint` 判为无效，这是预期结果，不是写法有错：只有隐藏 job 时报「至少需要一个可见 job」，只引用 `.node-base` 时报 `unknown keys in extends`，`needs:` 指向未定义的 `build` 时报 `undefined need`。落盘前按第 6 节执行第 1 级校验确认。

## 先识别技术栈

按仓库根目录的清单文件判定，一栈一套模板，其余文件只补充版本信息：

| 信号文件 | 判定 | 模板 |
| --- | --- | --- |
| `package.json` | Node.js | 模板一 |
| `package.json` 加 `tsconfig.json` | 用 TypeScript 编译的 Node.js，`tsconfig.json` 决定 build 如何编译 | 模板一，`tsconfig.json` 不改变栈判定 |
| `pyproject.toml`、`setup.py`、`requirements.txt` | Python | 模板二 |
| `go.mod` | Go | 模板三 |
| `Gemfile` | Ruby | 模板四 |
| `Cargo.toml` | Rust | 模板五 |
| `Dockerfile`，且无其他强信号 | 镜像构建与推送 | 模板六 |
| `pom.xml`、`build.gradle` | Java | **不提供模板** |
| `*.csproj`、`*.sln` | .NET | **不提供模板** |

`tsconfig.json` 单独出现不构成栈信号，它总是跟着 `package.json`。Java 与 .NET 没有对应模板，遇到时先给出栈判定，说明模板缺失，再问用户构建工具与 JDK / SDK 版本，不要勉强套用 Node 或 Docker 模板。

多个信号并存时（例如 `package.json` 与 `Dockerfile` 同时存在），说出主栈和判断依据，请用户确认后再写。判断错了技术栈，整份配置都要返工。

## 模板一：Node.js

有 `package-lock.json` 时用这套。`build` 产出 `dist/` 供 `deploy` 取用，`lint` 与 `unit-test` 不等构建。

```yaml
default:
  image: node:20-alpine
  interruptible: true

# 依赖安装与缓存:所有 Node 作业共用
.node-base:
  cache:
    key:
      files: [package-lock.json]
    paths: [.npm/]
  before_script:
    - npm ci --cache .npm --prefer-offline

stages: [build, test, deploy]

# 编译,产物给 deploy 用
build:
  extends: .node-base
  stage: build
  script:
    - npm run build
  artifacts:
    paths: [dist/]
    expire_in: 1 week

# 静态检查,流水线一开始就运行,不等 build
lint:
  extends: .node-base
  stage: test
  script:
    - npm run lint
  needs: []

# 单元测试,与 lint 并行
unit-test:
  extends: .node-base
  stage: test
  script:
    - npm test
  needs: []

# 占位:部署目标确认后替换 script
deploy:
  extends: .node-base
  stage: deploy
  script:
    - echo "deploy target not configured"
  needs: [build]
  rules:
    - if: '$CI_COMMIT_BRANCH == $CI_DEFAULT_BRANCH'
      when: manual
      allow_failure: true
```

`unit-test` 与 `lint` 上的 `needs: []` 让两者从流水线第一刻就开始运行，不必等 `build` 结束，这是把测试反馈提前的最便宜做法。

**没有 `package-lock.json` 时**，缓存 key 与安装命令一起换：

```yaml
.node-base:
  cache:
    key:
      files: [package.json]
    paths: [.npm/]
  before_script:
    - npm install --cache .npm --prefer-offline --no-audit --no-fund
```

`npm ci` 要求仓库里有被跟踪的锁文件，缺锁文件时直接以非零码退出，所以无锁项目必须换成 `npm install`。缓存 key 退回 `package.json` 意味着依赖文件一改就整体失效，粒度比锁文件粗，这是无锁项目必须付的代价。

**没有 `build` 脚本时**（纯 JS 库、直接发源码的运行时工具），`build` 有两种合理形态。发布到 npm 的库用 `npm pack` 产出可发布的 tarball：

```yaml
# 打出可发布的 tarball,下游 publish 消费
build:
  extends: .node-base
  stage: build
  script:
    - npm pack
  artifacts:
    paths: ["*.tgz"]
    expire_in: 1 week
```

确实没有构建动作时，删掉 `build` job 并从 `stages:` 里去掉 `build`，只留 `test` 与 `deploy`。这两种形态里 `deploy` 通常是 `npm publish`，规则改成 `if: $CI_COMMIT_TAG`。

什么时候不要用这套：仓库里有 `tsconfig.json` 且要求 `tsc --noEmit` 做类型检查时，`lint` 的 script 要换成类型检查命令，模板里的 `npm run lint` 只是调用项目自己的脚本，不能当作类型检查；仓库用 pnpm 或 yarn 时，锁文件、缓存路径与安装命令三处都要换，不要只改安装命令。

## 模板二：Python

`pyproject.toml`、`setup.py`、`requirements.txt` 任一存在即适用。容器本身已经是隔离环境，不建虚拟环境。

```yaml
default:
  image: python:3.12-slim
  interruptible: true

# 依赖安装与 pip 缓存
.python-base:
  cache:
    key:
      files: [pyproject.toml, requirements.txt]
    paths: [.cache/pip/]
  before_script:
    - pip install --cache-dir .cache/pip -e ".[test]"

stages: [build, test, deploy]

# 打 wheel 与 sdist,只在默认分支和 tag 上运行
build:
  extends: .python-base
  stage: build
  script:
    - python -m build
  artifacts:
    paths: [dist/]
    expire_in: 1 week
  rules:
    - if: '$CI_COMMIT_BRANCH == $CI_DEFAULT_BRANCH'
    - if: '$CI_COMMIT_TAG'

# 静态检查,流水线一开始就运行
lint:
  extends: .python-base
  stage: test
  script:
    - pip install ruff
    - ruff check .
  needs: []

# 单元测试,report.xml 让结果进 GitLab 的测试报告视图
test:
  extends: .python-base
  stage: test
  script:
    - pytest --junitxml=report.xml
  artifacts:
    reports:
      junit: report.xml
  needs: []

# 占位:部署目标确认后替换 script
deploy:
  extends: .python-base
  stage: deploy
  script:
    - echo "deploy target not configured"
  rules:
    - if: '$CI_COMMIT_BRANCH == $CI_DEFAULT_BRANCH'
      when: manual
      allow_failure: true
```

`before_script` 里的 `-e ".[test]"` 依赖 `pyproject.toml` 声明了 `test` 这个 extra；项目只有 `requirements.txt` 时换成 `pip install -r requirements.txt`，两者都有时先装 `requirements.txt` 再装 `-e .`。

什么时候不要用这套：项目需要系统级依赖（`psycopg2`、`lxml`、图像处理库）时，先确认 slim 镜像里有没有对应 wheel，没有就得在 `before_script` 里补 `apt-get install`，此时 `default:` 的镜像也要换成 `python:3.12`（完整 Debian 版）省掉逐个装依赖；用 Poetry 或 uv 的项目要把安装命令换成对应工具，锁文件也换成 `poetry.lock` 或 `uv.lock`。

## 模板三：Go

`go.mod` 存在即适用。`GOPATH` 放进项目目录，缓存才能跟着流水线走。

```yaml
default:
  image: golang:1.23-alpine
  interruptible: true

# 模块缓存与依赖下载
.go-base:
  variables:
    GOPATH: $CI_PROJECT_DIR/.go
  cache:
    key:
      files: [go.sum]
    paths: [.go/pkg/mod/]
  before_script:
    - go mod download

stages: [build, test, deploy]

# 编译检查,产物路径按项目实际情况另加
build:
  extends: .go-base
  stage: build
  script:
    - go build ./...

# 静态检查,换用 golangci-lint 镜像,模块缓存照样继承
lint:
  extends: .go-base
  stage: test
  image: golangci/golangci-lint:v1.61.0-alpine
  script:
    - golangci-lint run
  needs: []

# 单元测试,开 race 检测
test:
  extends: .go-base
  stage: test
  script:
    - go test -race ./...
  needs: []

# 占位:部署目标确认后替换 script
deploy:
  extends: .go-base
  stage: deploy
  script:
    - echo "deploy target not configured"
  needs: [build]
  rules:
    - if: '$CI_COMMIT_BRANCH == $CI_DEFAULT_BRANCH'
      when: manual
      allow_failure: true
```

`build` 只写 `go build ./...` 是因为 `-o` 与 `./...` 一起用、而匹配到多个包时会报错；要产出二进制就写明目标包，例如 `go build -o bin/app ./cmd/app`。起始模板不加覆盖率报告：Go 的 coverprofile 不是 Cobertura 格式，要进 GitLab 的覆盖率视图得额外加转换工具，这属于后续优化，不属于起手配置。

什么时候不要用这套：项目开了 cgo 或依赖 `libgit2` 一类 C 库时，Alpine 的 musl 会编译失败，`default:` 与 `golangci-lint` 两处镜像都要换成 Debian 变体（`golang:1.23`、`golangci/golangci-lint:v1.61.0`）；需要交叉编译多平台时单 job 不够，得按 `GOOS`/`GOARCH` 拆矩阵，那是独立一次改动。

## 模板四：Ruby

`Gemfile` 存在即适用，版本优先取 `.ruby-version`。

```yaml
default:
  image: ruby:3.3-alpine
  interruptible: true

# 依赖安装:原生 gem 需要 build-base
.ruby-base:
  cache:
    key:
      files: [Gemfile.lock]
    paths: [vendor/ruby/]
  before_script:
    - apk add --no-cache build-base
    - bundle config set --local path vendor/ruby
    - bundle install --jobs "$(nproc)"

stages: [build, test, deploy]

# 打包 gem,产物给发布用
build:
  extends: .ruby-base
  stage: build
  script:
    - bundle exec rake build
  artifacts:
    paths: [pkg/]
    expire_in: 1 week

# 风格检查,流水线一开始就运行
rubocop:
  extends: .ruby-base
  stage: test
  script:
    - bundle exec rubocop
  needs: []

# 单元测试,与 rubocop 并行
rspec:
  extends: .ruby-base
  stage: test
  script:
    - bundle exec rspec
  needs: []

# 占位:部署目标确认后替换 script
deploy:
  extends: .ruby-base
  stage: deploy
  script:
    - echo "deploy target not configured"
  rules:
    - if: '$CI_COMMIT_BRANCH == $CI_DEFAULT_BRANCH'
      when: manual
      allow_failure: true
```

`apk add --no-cache build-base` 不能省：`nokogiri`、`pg` 这类 gem 在 Alpine 上没有预编译版本，缺 `gcc` 与 `make` 会直接编译失败。用了 `bundle config set --local deployment true` 的项目，`vendor/ruby/` 变成只读，缓存命中后不要指望 `bundle install` 能就地更新依赖。

什么时候不要用这套：`Gemfile.lock` 没有提交时缓存 key 要退回 `Gemfile`，且 `deployment true` 会直接报错，得先让用户确认锁文件该不该进仓库；Rails 项目还要额外运行 `rails db:setup` 或 `assets:precompile`，需要数据库服务（`services:`）与额外变量，不要直接套模板。

## 模板五：Rust

`Cargo.toml` 存在即适用。`CARGO_HOME` 放进项目目录，并且只缓存 registry，否则每次都要全量下载依赖。

```yaml
default:
  image: rust:1.82-alpine
  interruptible: true

# cargo 缓存与链接依赖
.rust-base:
  variables:
    CARGO_HOME: $CI_PROJECT_DIR/.cargo
  cache:
    key:
      files: [Cargo.lock]
    paths:
      - .cargo/registry/
  before_script:
    - apk add --no-cache musl-dev

stages: [build, test, deploy]

# release 构建,产物给 deploy 用
build:
  extends: .rust-base
  stage: build
  script:
    - cargo build --release
  artifacts:
    paths: [target/release/]
    expire_in: 1 week

# clippy 检查,警告当错误处理
clippy:
  extends: .rust-base
  stage: test
  script:
    - rustup component add clippy
    - cargo clippy -- -D warnings
  needs: []

# 单元测试,与 clippy 并行
test:
  extends: .rust-base
  stage: test
  script:
    - cargo test
  needs: []

# 占位:部署目标确认后替换 script
deploy:
  extends: .rust-base
  stage: deploy
  script:
    - echo "deploy target not configured"
  needs: [build]
  rules:
    - if: '$CI_COMMIT_BRANCH == $CI_DEFAULT_BRANCH'
      when: manual
      allow_failure: true
```

只缓存 registry 而不缓存 `target/`，是有意的取舍：`target/` 里是编译产物，release 构建动辄几百 MB，跨分支还会拿到别的 feature 组合下的产物，缓存体积与上传下载时间会抵消大部分编译收益。项目确实大到重编成本明显时，再按依赖文件 hash 加前缀单独缓存 `target/`，并接受缓存体积上升。`target/release/` 作为 artifact 同样偏大，只需要二进制时改成 `target/release/<crate 名>`。

什么时候不要用这套：`Cargo.toml` 里依赖了 `openssl-sys`、`libsqlite3-sys` 这类需要系统库的 crate 时，Alpine 上要逐个 `apk add`，缺一个就报 `pkg-config` 找不到；遇到第一个链接错误就换到 `rust:1.82`（Debian 版）并改用 `apt-get install`，不要一直在 Alpine 上补包。

## 模板六：Docker 镜像构建与推送

`Dockerfile` 存在且没有更强的栈信号时适用。推送到项目自己的容器仓库，tag 用 commit SHA，不用 `latest`。

```yaml
default:
  interruptible: true

# dind 与仓库登录:所有需要 docker 的作业共用
.docker-base:
  image: docker:24
  services:
    - docker:24-dind
  variables:
    DOCKER_HOST: tcp://docker:2375
    DOCKER_TLS_CERTDIR: ""
  before_script:
    - docker login -u "$CI_REGISTRY_USER" -p "$CI_REGISTRY_PASSWORD" "$CI_REGISTRY"

stages: [build, test, deploy]

# 构建并推送,只在默认分支和 tag 上产出镜像
build:
  extends: .docker-base
  stage: build
  script:
    - docker build -t "$CI_REGISTRY_IMAGE:$CI_COMMIT_SHA" .
    - docker push "$CI_REGISTRY_IMAGE:$CI_COMMIT_SHA"

# Dockerfile 静态检查,不需要 dind
hadolint:
  stage: test
  image: hadolint/hadolint:v2.12.0-alpine
  script:
    - hadolint Dockerfile
  needs: []

# 占位:部署目标确认后替换 script
deploy:
  extends: .docker-base
  stage: deploy
  script:
    - echo "deploy target not configured"
  needs: [build]
  rules:
    - if: '$CI_COMMIT_BRANCH == $CI_DEFAULT_BRANCH'
      when: manual
      allow_failure: true
```

`$CI_REGISTRY`、`$CI_REGISTRY_IMAGE`、`$CI_REGISTRY_USER`、`$CI_REGISTRY_PASSWORD` 是 GitLab 预定义变量，指向当前项目自己的仓库，不需要手工配置。这套里能收进 `default:` 的只有 `interruptible`，dind 服务与登录动作放在隐藏 job，因为 `hadolint` 这类检查作业不需要容器运行时，为它配置 dind 只会徒增一段启动等待。

`DOCKER_TLS_CERTDIR: ""` 关掉 dind 的 TLS，配 `tcp://docker:2375` 才能连上；只在流水线内部网络里成立，不要把这个端口映射到构建机以外的可达范围。

什么时候不要用这套：需要多架构镜像时单 `docker build` 不够，要装 QEMU 并用 `buildx`，构建时间与资源占用明显上升，属于独立改动；需要镜像签名、SBOM 或漏洞扫描时，`build` 与 `test` 两处都要加步骤与凭据，不要在这里顺手加一半。

## 镜像选择

按栈的默认镜像。tag 一律写具体大版本，不写 `latest`。

| 栈 | 默认镜像 | 说明 |
| --- | --- | --- |
| Node.js | `node:20-alpine` | 大版本对齐 `engines.node`；没有声明就用当前 LTS |
| Python | `python:3.12-slim` | Debian slim，wheel 覆盖最全 |
| Go | `golang:1.23-alpine` | 纯 Go 编译不依赖 glibc |
| Ruby | `ruby:3.3-alpine` | 原生 gem 需要 `build-base` |
| Rust | `rust:1.82-alpine` | 默认 musl，需要 glibc 时换 `rust:1.82` |
| Docker 构建 | `docker:24` 加 `services: [docker:24-dind]` | 客户端与服务端大版本保持一致 |
| 只要 shell | `alpine:3.20` | 运行脚本、装 `curl` 与 `jq` 的轻量作业 |

`image:` 放 `default:` 的前提是多数 job 用同一个镜像；只有个别 job 需要不同工具时（linter 镜像、dind、云厂商 CLI），在该 job 上覆盖 `image:`。

**Alpine 与 Debian 的取舍**：Alpine 镜像通常比 Debian 版小一个数量级，拉取快，代价是用 musl libc 而不是 glibc。两类失败最典型：

- Node 原生模块依赖 glibc 的预编译包（`sharp`、`bcrypt`、`canvas`），Alpine 上装不到现成二进制，回退到源码编译又缺头文件。
- Python 的 manylinux wheel 在 musl 上不可用，pip 改走源码构建，缺 `gcc` 时直接失败。

回退动作固定两步：把该 job 的 `image:` 换成 Debian 或 slim 变体，`before_script:` 里的 `apk add --no-cache` 同时换成 `apt-get update && apt-get install -y --no-install-recommends`。只换镜像不改包管理命令，会得到 `apk: not found`。判断该不该回退的依据是报错类型：出现 `gyp ERR!`、`cannot find -l...`、`error: command 'gcc' failed` 这类链接或编译错误才回退；超时、网络错误与认证失败和 libc 无关，换镜像解决不了。

**不要写 `latest`**。上游镜像的 `latest` 会在某次推送后换成新大版本，同一份配置今天能运行、下个月遇到 breaking change 就无法运行，而且失败点落在依赖安装这种与本次改动无关的地方：

| 写法 | 结果 |
| --- | --- |
| `image: node:20-alpine` | 大版本固定，补丁跟着上游走，可复现 |
| `image: node` | 等同于 `latest`，不可用 |
| `image: golangci/golangci-lint:v1.61.0-alpine` | 工具版本钉住，升级是显式改动 |

工具镜像（linter、CLI）比运行时镜像更需要钉版本：它们的输出规则会变，`latest` 会让同一份代码今天过、明天因为在检查项上调严而失败。模板里的工具版本号按项目实际情况替换，但替换目标必须是具体版本。

## 运行时版本探测

镜像 tag 与工具版本从项目文件里读，不凭记忆写。每个栈的读法：

| 栈 | 文件与字段 | 取哪个数 |
| --- | --- | --- |
| Node.js | `package.json` 的 `engines.node` | `>=20 <21` 或 `^20.11.0` 都取 `20` |
| Node.js | `.nvmrc` | 文件内容，`20.11.1` 取 `20` |
| Python | `pyproject.toml` 的 `requires-python` | `>=3.11` 取 `3.11` |
| Python | `.python-version` | 文件内容 |
| Go | `go.mod` 的 `go` 行 | `go 1.23` 取 `1.23` |
| Ruby | `.ruby-version` | 文件内容，`3.3.0` 取 `3.3` |
| Ruby | `Gemfile` 的 `ruby '3.3.0'` | 同 `.ruby-version`，冲突时以 `.ruby-version` 为准 |
| Rust | `rust-toolchain.toml` 的 `channel` | `1.82.0` 取 `1.82` |
| 任意 | `Dockerfile` 的 `FROM` | 取运行阶段的基础镜像版本 |

镜像 tag 跟到小版本就够，不跟到 patch：项目写 `>=20.11.0` 时用 `node:20-alpine`，patch 交给上游。写 `node:20.11.0-alpine` 只会把版本升级变成手工维护，收益是零。

**探测不到时**按三步走：先用当前 LTS 或稳定版填进模板，再在提案里单独写一句「仓库没有版本声明，镜像取 `node:20-alpine`（当前 LTS），实际运行版本不是这个的话请指出」，最后等用户确认。不要静默取最新版，也不要拿本机 `node --version` 或 `python3 --version` 的结果冒充项目声明，本机版本和 CI 无关。

两类特殊情况要单独看：`rust-toolchain.toml` 指定 `channel = "nightly"` 时，镜像也要换成带具体日期的 nightly_tag，`rust:nightly` 这类浮动 tag 与 `latest` 一样不可复现；`Dockerfile` 是多阶段构建时只对齐运行阶段的基础镜像，构建阶段用什么随它。

## 有部署目标时的四种走向

模板里的 `deploy` 只放占位 `echo`，因为部署目标读仓库文件读不出来。用户说出目标后再替换，四类各有一套最小写法。**用户没说目标时任何一类都不要猜**：不写集群地址、不写镜像仓库、不写云账号和区域，把这些列成待确认项交回去，比写一份无法正常运行的配置有用。

### Kubernetes

```yaml
# 集群地址与凭据由 KUBECONFIG 提供,不进 YAML
deploy-k8s:
  stage: deploy
  image: bitnami/kubectl:1.30
  script:
    - sed -i "s|IMAGE_PLACEHOLDER|$CI_REGISTRY_IMAGE:$CI_COMMIT_SHA|" k8s/deployment.yaml
    - kubectl apply -f k8s/deployment.yaml
  needs: [build]
  rules:
    - if: '$CI_COMMIT_BRANCH == $CI_DEFAULT_BRANCH'
```

清单里的镜像地址要能被替换，否则每次上线用的都是同一个旧 tag。`KUBECONFIG` 内容放进 CI/CD 变量（masked 加 protected），不要写进 YAML，也不要从构建机的 `~/.kube/config` 里读。没有明确集群时不要猜目标环境：`staging` 还是 `production`、用哪个 namespace、要不要蓝绿发布，都由用户给出。

### Pages

```yaml
# job 名必须叫 pages,GitLab 按名字找它
pages:
  stage: deploy
  image: node:20-alpine
  script:
    - npm ci
    - npm run build
    - mv dist public
  artifacts:
    paths: [public]
  needs: []
  rules:
    - if: '$CI_COMMIT_BRANCH == $CI_DEFAULT_BRANCH'
```

产物目录必须叫 `public`，放在 `artifacts:paths:` 里，job 名必须是 `pages`，三者缺一个都不会发布。项目不是静态站点（有服务端渲染、需要后端接口）时不要用这条路径，Pages 只发静态文件。默认域名与访问控制取决于实例配置，具体地址让用户从实例上确认，不要照抄示例域名。

### 云 CLI

```yaml
# 云厂商 CLI 随镜像提供,密钥走 CI/CD 变量
deploy-cloud:
  stage: deploy
  image: amazon/aws-cli:2.17.0
  script:
    - aws ecs update-service --cluster "$ECS_CLUSTER" --service "$ECS_SERVICE" --force-new-deployment
  needs: [build]
  rules:
    - if: '$CI_COMMIT_BRANCH == $CI_DEFAULT_BRANCH'
```

这条走向的差异全在凭证与区域变量上，脚本本身很短。变量用 CI/CD 变量（masked 加 protected），写进 YAML 等于把密钥提交进仓库。厂商、区域、资源名都没确认时不要猜：用哪家云、部署到哪个服务、镜像从哪个仓库拉，都要用户给出，猜错方向会做出一份看起来完整却指向别人环境的配置。

### 包仓库

```yaml
# 打 tag 才发布,凭据走 CI/CD 变量
publish:
  stage: deploy
  image: node:20-alpine
  script:
    - npm ci
    - npm config set "//${CI_SERVER_HOST}/api/v4/projects/${CI_PROJECT_ID}/packages/npm/:_authToken" "$CI_JOB_TOKEN"
    - npm publish --registry "$CI_API_V4_URL/projects/$CI_PROJECT_ID/packages/npm/"
  needs: [build]
  rules:
    - if: '$CI_COMMIT_TAG'
```

发布类作业统一挂在 `if: $CI_COMMIT_TAG` 上：包仓库里一个版本只能发一次，重新运行分支流水线就把版本号占了。Python 的 `twine upload`、Ruby 的 `gem push`、Rust 的 `cargo publish` 同理，命令换掉即可。发到哪个仓库（项目级还是实例级、还是外部 registry）没有确认时不要猜，包名与地址的写法三处都不同。

## 交付前自查

模板写完先运行静态校验，确认无误再给出结论：

```bash
glab ci lint .gitlab-ci.yml
glab ci config compile .gitlab-ci.yml
```

`glab ci lint` 覆盖语法、include 引用、job 名冲突，以及 `needs:` 指向的 job 是否存在；`artifacts:` 路径与下游是否对得上，要到真实执行才看得出来。三种状态的结论怎么写、按改动类型选哪一级，见 [verification.md](verification.md) 与 [../SKILL.md](../SKILL.md) 第 7 节。

不要顺手加 `workflow:rules:`。开了 MR 之后每次推送会同时产生分支流水线和 MR 流水线，加不加是用户的决定，理由见 [../SKILL.md](../SKILL.md) 第 4 节。
