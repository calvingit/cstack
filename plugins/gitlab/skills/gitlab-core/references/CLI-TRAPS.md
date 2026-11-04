# glab CLI 陷阱手册

以下每一条都在 GitLab CE 16.11 + glab 1.124 上实测过。这些命令失败时不报错，所以逐条说明症状，而不只给结论。

## 1. 消息转义：反引号与 `$` 会被 shell 吃掉

shell 会把 `glab mr note create -m "..."` 里的反引号当作命令替换，并展开 `$变量`，结果是正文被截断，甚至报 `command not found`。

错误的写法：

```bash
glab mr note create 123 -m "这里用了 \`client_name\` 字段"
```

正确的写法：单引号 heredoc 写入文件，再通过 `$(cat)` 传入。

````bash
MSG=$(mktemp)
cat > "$MSG" << 'EOF'
这里用了 `client_name` 字段，示例代码：

```bash
glab mr view 123
```
EOF
glab mr note create 123 -m "$(cat "$MSG")"
````

要点：

- heredoc 定界符必须加单引号（`<< 'EOF'`），否则写入阶段就会展开。
- 三反引号代码块在 `<< 'EOF'` 里是安全的，不需要转义。
- 正文本身含 heredoc 示例时，外层换一个定界符（`OUTEREOF`），否则内层 `EOF` 会提前关闭外层。
- 提交信息同理：含特殊字符用单引号 `git commit -m '...'`。

## 2. `-f` 与 `-F`：类型推断会送错值

`glab api` 的两个传参标志行为不同：

| 标志 | 行为 | 用在哪 |
| --- | --- | --- |
| `-f` / `--raw-field` | 始终按字符串发送 | 正文、GraphQL `String` 变量、任何看起来像数字的标识 |
| `-F` / `--field` | 推断类型；`@` 开头当文件读取 | 需要发数字、布尔或文件内容时 |

把 `iid`、`body` 这类值用 `-F` 发送，会变成 JSON number，服务端可能拒绝（GraphQL 报 `Could not coerce value 2332 to String`）。正文含 `@` 时，还会被当成文件路径读取。

写评论优先写文件再加 `-f`：

```bash
glab api --method POST "projects/org%2Frepo/merge_requests/123/notes" \
  -f "body=$(cat "$MSG")"
```

## 3. 分页：按 `X-Next-Page` 翻，不要按「这一页不满」停

服务端可能先分页再过滤，所以一页少于 `per_page` 不代表是最后一页，`X-Total` 也会偏大。

```bash
# 自动翻页，每条记录一行
glab api --paginate --output ndjson "projects/org%2Frepo/merge_requests/123/notes" | jq -s add
```

手动翻页时循环到 `X-Next-Page` 为空：

```bash
glab api -i "projects/org%2Frepo/merge_requests/123/notes?per_page=100" | grep -i '^x-next-page:'
```

`--paginate` 不加 `--output ndjson` 会输出多个 JSON 数组，`jq length` 得到的是每页条数。

## 4. 静默失败：退出码 0 不等于写对了

已知会静默失败的场景：

- `glab ci status -F json` 与 `glab ci get` 在流水线失败时仍退出 0，要看 `.pipeline.status` 或 `.status` 字段。
- 字段标志写错时，命令可能照样返回成功，但发布的正文是空的或被截断。
- `glab mr diff --raw` 在 16.11 上返回 404，但退出码仍是 0。

写操作之后回读核对：

```bash
glab api "projects/org%2Frepo/merge_requests/123/notes?sort=desc&per_page=1" | jq -r '.[0].body'
```

## 5. 参数名不是 `gh` 那一套

| 需求 | glab 写法 | 常见错误 |
| --- | --- | --- |
| MR 描述 | `--description` | 用 `--body`（那是 `gh` 的） |
| issue 状态过滤 | `--closed` / `--all` | 用 `--state closed`（无此标志） |
| 加标签 | `--label` / `--unlabel` | 用 `+label` / `-label` |
| 目标仓库 | `-R owner/repo` | 只想钉住 head 时也只用 `-R` |

`glab mr list` 与 `glab issue list` 默认只列打开的，没有 `--state` 标志。

## 6. `--jq` 只适用于子命令，`glab api` 没有

```bash
glab mr list -F json --jq '.[].iid'          # 可以
glab api "projects/org%2Frepo/merge_requests" | jq '.[].iid'   # api 要自己接 jq
```

`glab mr list --jq` 不带 `-F json` 会报 `Using --jq requires --output=json`。

## 7. 多实例：靠 remote 自动识别，不要随手设 `GITLAB_HOST`

在仓库内执行 `glab` 命令时，会自动读取 `origin` 的 host、协议和端口。只有在以下情况才需要显式指定：

```bash
# 仓库外，或一次性跨实例
GITLAB_HOST=git.example.com glab api "version"

# 非标准端口要带协议
GITLAB_HOST=http://127.0.0.1:3000 glab mr list
```

`origin` 不是目标实例时，设置次级 remote 别名，而不是每条命令都加 `GITLAB_HOST`：

```bash
git remote add upstream http://gdk.test:3000/group/project.git
glab config set remote_alias upstream      # 本仓库生效
glab config set --global remote_alias upstream   # 全局
```

从 remote URL 推导 API 起点：

```bash
git remote get-url origin | sed -E 's|(https?://[^/]*).*|\1|'
```

URL 形式的 SSH remote（`ssh://git@host:2222/...`）里，SSH 端口不是 API 端口，只能取主机名，协议和端口要单独确认。

## 8. `work_items` 的 URL 要走 issues 端点

界面上的 `/work_items/<iid>` 在 REST 里没有对应端点（16.11 返回 404）。同一 IID 用 issues API：

```bash
glab api "projects/org%2Frepo/issues/539076"
```

## 9. 幂等评论

重复运行同一条评论脚本时加 `--unique`，正文完全相同则跳过：

```bash
glab mr note create 123 -m "$(cat "$MSG")" --unique
```

匹配只看正文，不区分行内位置。

## 10. 行内评论的行号取哪一侧

| 评论对象 | 标志 | 说明 |
| --- | --- | --- |
| 新增或修改行 | `--line` | 取新版本行号 |
| 被删除行 | `--old-line` | 取旧版本行号 |
| 行范围 | `--line 42:48` | 新版本连续区间 |
| 整文件 | 只给 `--file` | 不指定行 |

`--line` 与 `--old-line` 互斥，且都必须配合 `--file`。行号取自该文件在新版本中的位置，不是 diff 块内的偏移。
