---
name: gitlab-rebase
description: 当要把特性分支变基到已经前进的 release 或主干分支，或合并前需要与目标分支对齐时使用。
---

# gitlab-rebase · 与目标分支对齐

## 目标

把特性分支安全地对齐到已经前进的目标分支，不丢目标分支的改动，也不悄悄丢自己的改动。

## 强制约束

- **绝不静默丢弃目标分支的任何改动。** 每一个目标分支的改动，要么原样保留，要么按当前分支的架构显式重写。拿不准就停下问，不要猜。
- 冲突解决时同时看两侧意图，不是单方面选一边。
- 已推送的分支变基后需要强推，强推前确认没有他人在此分支上工作。
- 不主动改写已合并或他人正在评审的提交。

## 何时适用

- 长期维护分支（如 `release/<版本>`）前进后，特性分支准备合并。
- 分支已经太久没同步，diff 里混入大量与本改动无关的差异。
- 合并前预检冲突。

## 流程

### 1. 看清拓扑

```bash
git branch --show-current
git rev-parse --abbrev-ref --symbolic-full-name @{upstream} 2>/dev/null || echo "无上游"
git symbolic-ref --short refs/remotes/origin/HEAD 2>/dev/null | sed 's|origin/||'
git fetch origin
```

目标分支不一定是默认分支。长期维护分支的常见形式是 `release/<版本>`，必须显式确认：

```bash
TARGET="origin/release/<版本>"        # 换成仓库实际的目标分支
git log --oneline "$TARGET" -5
git merge-base HEAD "$TARGET"
git rev-list --count "$TARGET"..HEAD    # 自己领先几个
git rev-list --count HEAD.."$TARGET"    # 目标领先几个
```

**把拓扑讲给用户听并确认目标分支正确**，再往下走。

### 2. 分类两侧改动

分别看目标分支改了什么、自己改了什么，把每个文件归入四类：

| 类别 | 处理 |
| --- | --- |
| 只有目标分支改了 | 直接跟进，无需干预 |
| 只有自己改了 | 直接保留 |
| 两边都改，但区域不重叠 | 通常能自动合并，仍要检查语义冲突 |
| 两边都改同一区域 | 需要人工判断，逐块处理 |

```bash
git diff --stat $(git merge-base HEAD "$TARGET").."$TARGET"
git diff --stat $(git merge-base HEAD "$TARGET")..HEAD
```

两边都改的文件单独列出，这是冲突高发区：

```bash
comm -12 \
  <(git diff --name-only $(git merge-base HEAD "$TARGET").."$TARGET" | sort) \
  <(git diff --name-only $(git merge-base HEAD "$TARGET")..HEAD | sort)
```

### 3. 无副作用预检

先不改工作区，判断能不能干净合并：

```bash
git merge-tree --write-tree "$TARGET" HEAD
```

返回树对象且退出码 0 表示可自动合并；有冲突时输出会列出冲突文件。

### 4. 变基并逐块解决

```bash
git rebase "$TARGET"
```

冲突时的处理原则：

- 先读冲突两侧的完整上下文，不只看冲突标记之间的几行。
- 问自己：目标分支那块改动想解决什么？我这块想解决什么？
- 两者都要成立时，写出同时满足两者的版本，不选边。
- 判断不了就 `git rebase --abort` 回到干净状态，把情况交回用户。

中止与恢复：

```bash
git rebase --abort      # 整体放弃，回到变基前
git rebase --skip       # 跳过当前提交（谨慎，会丢该提交的改动）
git rebase --continue   # 解决完当前块后继续
```

### 5. 验证必须实际执行

变基后必须实际验证，不能只看「没有冲突标记」：

```bash
git log --oneline -10
git diff "$TARGET"...HEAD --stat    # 确认只剩自己的改动
```

关键检查：**变基后的 diff 里不该出现目标分支已经有的改动**。如果出现了，说明解决方案把目标分支的改动又改回去了。

变基前先记下当前 HEAD，事后用它做对比基准。不要依赖 `HEAD@{1}`，reflog 索引在多次操作后会漂移：

```bash
BEFORE=$(git rev-parse HEAD)
```

变基后与变基前的自身改动比较，确认没有意外丢失或改写：

```bash
# 变基后的本分支提交，与变基前的原始提交逐条对照
git range-diff "$TARGET".."$BEFORE" "$TARGET"..HEAD
```

输出里每个条目前的标记含义：`=` 内容一致，`!` 有差异，`>` 新增提交，`<` 消失提交。出现 `<` 或非预期的 `!` 都要回头查。

## 强推的风险

变基改写了历史。推送前确认：

- 这是个人分支，没有他人在上面工作。
- 没有正在评审的 MR 依赖旧提交（行内评论会失去锚点）。
- 需要时用 `--force-with-lease`，不要用 `--force`：

```bash
git push --force-with-lease
```

已经在评审的 MR 变基后，之前基于旧提交的行内评论位置会失效，主动说明这一点。

## 产物

- **读**：分支拓扑、两侧 diff、冲突上下文、构建与测试结果。
- **写**：变基后的分支状态；推送需单独授权。

## 停止与交接

- 冲突需要产品决策（两个行为二选一）时停下，交回用户。
- 需要拆分或重构才能解决冲突时，先完成拆分再变基，不要在一个变基里混入重构。
- 不主动 `git push`，除非用户明确要求。

## 参考

- 推送与强推的授权边界：读取 `gitlab-core` 的 `SAFETY.md`
- 冲突解决后要拆分提交：使用 `gitlab-commit`
