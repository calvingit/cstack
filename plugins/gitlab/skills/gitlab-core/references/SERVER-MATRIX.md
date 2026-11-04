# 实例能力矩阵

本文件记录的命令与端点，均在 GitLab CE 16.11.10 + glab 1.124 上逐条实测。换实例、升版本或换订阅级别后，按最后一节的探测步骤重新确认。

## 契约说明

矩阵里的三档含义：

- **可用**：实测成功，可以直接依赖。
- **不可用**：实测失败，且不是用法问题；给出替代方案。
- **条件可用**：依赖订阅级别或版本功能，需要先确认当前实例。

## MR 读写

| 能力 | 状态 | 命令或替代 |
| --- | --- | --- |
| 查看 MR 元数据 | 可用 | `glab mr view <iid>` |
| 查看 diff | 可用 | `glab mr diff <iid>` |
| raw diff | **不可用** | `glab mr diff --raw` 返回 404；用 `glab api "projects/<id>/merge_requests/<iid>/changes"` |
| 发表一般评论 | 可用 | `glab mr note create <iid> -m "$(cat "$MSG")"` |
| 行内 diff 评论 | 可用 | `glab mr note create <iid> --file <path> --line <n> -m ...` |
| 回复讨论 | 可用 | `glab mr note create <iid> --reply <disc-id> -m ...` |
| 解决讨论 | 可用 | `glab mr note resolve <disc-id> <iid>` |
| 列出讨论 | 可用 | `glab mr note list <iid> -F json` |
| 幂等评论 | 可用 | 加 `--unique` |
| 批量草稿评审 | 可用 | `glab mr note draft create/list/update/delete/publish` |
| 批准 / 撤销批准 | 可用 | `glab mr approve <iid>` / `glab mr revoke <iid>` |
| 合并、rebase | 可用 | `glab mr merge` / `glab mr rebase` |
| 代码建议按钮 | 可用 | 评论正文里放 ```` ```suggestion:-0+0 ```` 块 |

**draft notes 一组命令**：`glab mr note draft` 实测全部可用。项目级 REST 端点 `GET projects/<id>/merge_requests/<iid>/draft_notes` 同样返回正常结果。若某次调用返回 404，先确认项目 ID 与 IID 是否正确，再怀疑版本。

## Diff 相关端点

| 端点 | 状态 | 备注 |
| --- | --- | --- |
| `GET .../merge_requests/<iid>/changes` | 可用 | 返回 `changes` 数组，含完整 diff |
| `GET .../merge_requests/<iid>/diffs?per_page=N` | 可用 | 支持分页，推荐用于大 MR |
| `GET .../merge_requests/<iid>/raw_diffs` | **不可用** | 16.11 无此端点 |

大 MR 按文件分批读取，避免一次拉全量：

```bash
glab api "projects/org%2Frepo/merge_requests/123/diffs?per_page=100" \
  | jq -r '.[] | "\(.new_path)  +\([.diff | split("\n")[] | select(startswith("+") and (startswith("+++")|not))] | length)  -\([.diff | split("\n")[] | select(startswith("-") and (startswith("---")|not))] | length)"'
```

**字段坑**：`diffs` 与 `changes` 端点都**不返回** `new_lines` / `old_lines`，只有 `new_path`、`old_path`、`diff`、`new_file`、`deleted_file`、`renamed_file`、`generated_file`、`a_mode`、`b_mode`。增删行数只能从 `diff` 文本里数。

## Issue 与 Work Item

| 能力 | 状态 | 命令或替代 |
| --- | --- | --- |
| issue 增删改查 | 可用 | `glab issue view/create/update/list` |
| issue 评论 | 可用 | `glab issue note <iid> -m "$(cat "$MSG")"` |
| `/work_items` REST 端点 | **不可用** | 用同一 IID 的 issues 端点 |
| 关闭 / 重开 | 可用 | `glab issue close` / `glab issue reopen` |

Work Item 在界面上显示为 `/work_items/<iid>`，但 REST 侧走 `projects/<id>/issues/<iid>`，IID 相同。

## 依赖订阅级别或版本的功能

| 能力 | 状态 | 说明 |
| --- | --- | --- |
| Epics | **不可用**（CE） | `groups/<id>/epics` 返回 404；Premium 及以上才有 |
| group work_items | **不可用**（CE） | 同上，走 epics 或 GraphQL |
| GLQL 查询 | **不可用**（16.11） | `POST /glql` 需 18.7+；用普通 REST + `jq` 过滤 |
| GraphQL | 可用 | `glab api graphql -f query='...'` 实测正常 |
| 审批规则（Approval Rules） | 条件可用 | 基础批准可用；复杂审批规则需 Premium |

GLQL 的替代写法：

```bash
# 原本想用 GLQL 表达：assignee = currentUser() AND state = opened
glab api "merge_requests?scope=assigned_to_me&state=opened&per_page=100" | jq -r '.[] | "\(.references.full) \(.title)"'
```

## 实例探测步骤

换环境后先执行这三条，再决定哪些命令可用：

```bash
# 1. 版本与订阅
glab api "version" | jq '{version, enterprise}'

# 2. GraphQL 是否通
glab api graphql -f query='{ currentUser { username } }'

# 3. 目标端点是否 404
glab api "projects/<id>/merge_requests/<iid>/diffs?per_page=1" >/dev/null && echo "diffs OK"
```

社区版（CE）返回 `"enterprise": false`。

## 把失败误判成版本问题的几种情况

排查顺序很重要，先排除用法错误：

1. **仓库里没有 MR**：`glab mr note list` 会报 `No open merge request available`，这是没有目标，不是版本不支持。
2. **项目路径不对**：`projects/<path>` 里斜杠要编码成 `%2F`，否则 404。
3. **IID 当成了 ID**：路径里用的是项目内的 IID，不是全局 ID。
4. **把项目级端点当成 MR 级端点**：端点层级写错同样返回 404。
5. **remote 指向了别的实例**：先 `glab auth status` 确认当前 host。

只有以上都排除后，才把 404 归因到版本或订阅级别。
