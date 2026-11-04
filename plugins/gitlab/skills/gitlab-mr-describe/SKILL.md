---
name: gitlab-mr-describe
description: 当要为 GitLab MR 写或更新描述，需要从实际 diff 提炼意图和影响面时使用。不用于评审代码质量、不用于判断能否合并、不用于生成发布说明。
---

# gitlab-mr-describe · 写 MR 描述

## 目标

从分支实际改动生成 MR 描述，让评审者不读 diff 也能判断这次改动的范围与风险。

## 强制约束

- 描述必须来自实际 diff，不是从提交标题猜测。提交标题与实际改动不一致时以 diff 为准。
- **项目模板优先。** 仓库有 `.gitlab/merge_request_templates/` 时按模板结构填，不要另起一套。
- 没有证据的段落直接省略，不留占位符，不写「待补充」。
- 不写改动没做的事。范围蔓延的顺带改动单独列出，不混进主改动。
- 写入 MR 前读取 `gitlab-core` 的 `SAFETY.md`；生成文本不等于已授权写回。

## 流程

### 1. 取上下文

```bash
TARGET=${TARGET:-origin/HEAD}
git log --oneline "$TARGET"..HEAD          # 本分支独有的提交
git diff "$TARGET"...HEAD --stat           # 本分支引入的变更
```

`origin/HEAD` 指向仓库的默认分支，比写死 `main` 稳妥。该引用缺失时，先运行 `git remote set-head origin --auto`；若仍失败，说明远端仓库没有设置默认分支，改用 `git remote set-head origin <分支名>` 显式指定。

目标分支不是默认分支时显式指定。长期维护分支的常见形式是 `release/<版本>`：

```bash
TARGET="origin/release/<版本>"        # 换成仓库实际的目标分支
git log --oneline "$TARGET"..HEAD
git diff "$TARGET"...HEAD --stat
```

两条命令的范围运算符不同，不能互换。`log` 配 `..`，只列本分支独有的提交；`diff` 配 `...`，取共同祖先到候选之间的变更。`diff` 若用 `..`，会把目标分支自己的改动也算进来，描述里就会出现本次没做过的改动。

已有 MR 时读取当前描述，避免覆盖使用者手写的内容：

```bash
glab mr view <iid>
glab api "projects/<encoded-path>/merge_requests/<iid>" | jq -r '.description'
```

检查项目模板：

```bash
glab api "projects/<encoded-path>/repository/tree?path=.gitlab/merge_request_templates" 2>/dev/null | jq -r '.[].name'
```

### 2. 判断改动形状

先回答四个问题，再动笔：

- 这次改动**增加**了什么能力，或**修掉**了什么缺陷？
- 触发问题的条件是什么，改完后行为如何变化？
- 影响哪些面向用户的界面、接口、数据或配置？
- 有没有需要评审者特别注意的点：迁移、配置变更、兼容性、开关。

### 3. 按结构写

没有项目模板时用下面的骨架，有模板时按模板的标题顺序填。

```markdown
## 这个 MR 做了什么

<一到两句说清目的与手段。>

## 具体改动

- <按关注点分组的能力或行为变化>
- <影响面：接口 / 数据 / 配置 / 界面>

## 怎么验证

<评审者可以照做的步骤，或已执行过的检查及结果。>

## 注意事项

<迁移、兼容性、开关、需要额外部署动作的部分；没有就删掉这一节。>
```

写法要求：

- 标题讲行为和意图，不讲文件名。「修复订单同步在重试时重复写入」比「修改 OrderService.java」有用。
- 具体改动按关注点组织，不按文件罗列。
- 验证一节写实际执行过的检查和观察结果，不写「应该没问题」。
- 有数据库迁移、接口变更、配置项新增时，单独点出来，这类内容评审者最容易漏。

### 4. 自检后交付

交出前逐项确认：

- [ ] 每一条描述都能在 diff 里找到对应改动
- [ ] 没有 diff 里不存在的能力
- [ ] 提交数与 `<目标分支>..<候选>` 一致，没有漏掉的未推送提交
- [ ] 省略的段落是因为不适用，不是因为没查

### 5. 写回 MR（需授权）

使用者确认要写回后：

```bash
DESC=$(mktemp)
cat > "$DESC" << 'EOF'
<描述正文>
EOF
glab mr update <iid> --description "$(cat "$DESC")"
```

写后回读核对：

```bash
glab api "projects/<encoded-path>/merge_requests/<iid>" | jq -r '.description' | head -20
```

## 产物

- **读**：diff、提交记录、项目 MR 模板、已有描述。
- **写**：MR 描述文本；获授权后写回平台，写后回读。

## 参考

- 转义与字段标志：读取 `gitlab-core` 的 `CLI-TRAPS.md`
- diff 端点选择：读取 `gitlab-core` 的 `SERVER-MATRIX.md`
