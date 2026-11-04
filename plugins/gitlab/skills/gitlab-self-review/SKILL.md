---
name: gitlab-self-review
description: 当要在提交评审前自查改动、或要把多条评审意见攒成一次发布时使用。不用于替代他人评审、不用于决定能否合并、不用于逐条验收需求。
---

# gitlab-self-review · 提评审前自查

## 目标

在把 MR 交给别人之前先自查一遍，并把多条发现攒成一次发布，而不是刷出一串碎片评论。

## 强制约束

- 自查的是**自己本次改动**。范围固定为目标分支到当前分支之间，不顺手审别人的代码。
- 只报有证据的问题。自查放过的问题，别人会当成你没看见。
- **发布草稿是写操作。** 攒草稿可以，发布前必须确认发什么、发几条。
- 自查结论不等于他人评审已通过，也不构成合并许可。

## 流程

### 1. 固定自查范围

```bash
TARGET=${1:-origin/HEAD}
git log --oneline "$TARGET"..HEAD        # 本次独有的提交
git diff "$TARGET"...HEAD --stat         # 本次引入的变更
```

`log` 配 `..`，`diff` 配 `...`，两者不能互换；`diff` 若用 `..`，会把目标分支的改动算进自查范围。

工作树有未提交改动时，这部分不在 MR 里，单独说明，不要混进结论。

### 2. 按清单自查

逐项过，不要跳：

- **能否编译或运行**：改动涉及的模块有没有跑过。
- **新增行为是否有测试**：没有就明确说没有，不假设别人会补。
- **错误路径**：异常、超时、空值、并发进入时行为是什么。
- **边界与默认值**：空集合、零值、超大输入。
- **配置与迁移**：新增配置项有没有默认值；数据库变更能否回滚。
- **兼容性**：接口签名、返回结构、序列化格式变了会不会影响调用方。
- **调试残留**：临时代码、注释掉的逻辑、多余的日志、硬编码路径。
- **描述与改动是否一致**：描述里说的和 diff 里做的对不对得上。

### 3. 整理成发现

每条写成：

```
[级别] 标题
path/to/file.ext:42 — 问题、触发条件、影响。
```

级别用 P0 到 P3：

| 级别 | 含义 |
| --- | --- |
| P0 | 会导致故障、数据错误或安全问题，合并前必须改 |
| P1 | 很可能出问题，建议合并前改 |
| P2 | 值得改进，可以后续处理 |
| P3 | 风格与命名偏好，作者可以忽略 |

### 4. 攒草稿而不是逐条发

需要把发现落到 MR 上时，用草稿把多条评论攒起来，一次发布：

```bash
DRAFT=$(mktemp)
cat > "$DRAFT" << 'EOF'
**[P1] 重试分支没有上限**

第三次重试后仍会再次入队，失败任务会持续堆积。
EOF
glab mr note draft create <iid> --file server/src/OrderService.java --line 88 -m "$(cat "$DRAFT")"
```

草稿只有本人可见，攒的时候不会打扰别人。管理草稿：

```bash
glab mr note draft list <iid> -F json
glab mr note draft update <iid> <draft-id> -m "新正文"
glab mr note draft delete <iid> <draft-id> --yes
```

### 5. 发布前确认

```bash
# 先列出全部待发草稿，逐条核对
glab mr note draft list <iid> -F json | jq -r '.[] | "\(.id) \(.position.new_path):\(.position.new_line) \(.note | split("\n")[0])"'
```

**`publish` 会发出该 MR 上你所有的草稿**，包括之前遗留的。确认后执行：

```bash
glab mr note draft publish <iid> -m "自查发现，见上方逐条评论。" --yes
```

发布后回读核对实际落到 MR 上的内容：

```bash
glab api "projects/<encoded-path>/merge_requests/<iid>/discussions?per_page=20" \
  | jq -r '.[] | .notes[0] | select(.position) | "\(.position.new_path):\(.position.new_line) \(.body | split("\n")[0])"'
```

## 产物

- **读**：diff、相关源码与测试、已有讨论。
- **写**：自查发现清单；获授权后写草稿并发布，写后回读。

## 停止条件

- 使用者只要自查结论时，交清单即可，不要建草稿。
- 发现属于需求理解分歧时，交回需求侧确认，不自行判定为缺陷。

## 参考

- 转义写法与 `--unique`：读取 `gitlab-core` 的 `CLI-TRAPS.md`
- 行内评论行号取哪一侧：读取 `gitlab-core` 的 `CLI-TRAPS.md` 第 10 节
- 发布类写操作的安全约束：读取 `gitlab-core` 的 `SAFETY.md`
