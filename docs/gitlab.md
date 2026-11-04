# GitLab 插件

> 面向日常使用自部署 GitLab 服务器的协作场景，覆盖提交、MR 与评审。工程方法本身见 [Skill 参考](skills.md)。

## 适用与不适用

| 适用 | 不适用 |
| --- | --- |
| 自部署 GitLab 实例上的日常开发 | 给 gitlab.com 上游项目贡献代码（社区贡献流程另有一套） |
| 用 `glab` 完成提交、MR、评审、变基 | 依赖 GitLab 内部系统的工作流（Sentry、GDK 本地库、on-call） |
| 团队协作中的评审与自查 | 依赖 Premium 及以上订阅的功能（Epic、复杂审批规则） |

## 七个技能的分工

| Skill | 用途 | 触发 |
| --- | --- | --- |
| [gitlab-core](../plugins/gitlab/skills/gitlab-core/SKILL.md) | 共享知识索引：glab 陷阱手册、实例能力矩阵、写操作安全约束 | 手动 |
| [gitlab-mr-review](../plugins/gitlab/skills/gitlab-mr-review/SKILL.md) | 两阶段评审：先讲清 MR 想解决什么，确认后再给有证据的发现 | 自动 |
| [gitlab-mr-describe](../plugins/gitlab/skills/gitlab-mr-describe/SKILL.md) | 从实际 diff 生成结构化 MR 描述 | 自动 |
| [gitlab-self-review](../plugins/gitlab/skills/gitlab-self-review/SKILL.md) | 提评审前自查，把多条发现攒成草稿一次发布 | 自动 |
| [gitlab-commit](../plugins/gitlab/skills/gitlab-commit/SKILL.md) | 写提交信息，把改动拆成原子提交 | 自动 |
| [gitlab-rebase](../plugins/gitlab/skills/gitlab-rebase/SKILL.md) | 把特性分支安全对齐到前进的 release 或主干分支 | 自动 |
| [gitlab-stack](../plugins/gitlab/skills/gitlab-stack/SKILL.md) | 把大改动拆成可独立评审的 MR 链 | 自动 |

子代理 [gitlab-reviewer](../plugins/gitlab/agents/gitlab-reviewer.md) 提供只读评审，可独立派发。

### 怎么组合

- **提交前**：`gitlab-commit` 写提交信息 → `gitlab-self-review` 自查 → 需要时 `gitlab-rebase` 对齐目标分支。
- **开 MR**：`gitlab-mr-describe` 生成描述 → `gitlab-stack` 挑太大的先拆。
- **评审**：`gitlab-mr-review` 两阶段，或派 `gitlab-reviewer` 做独立只读评审。
- **命令细节**：随时读 `gitlab-core`，它不自动触发。

## 三条硬规则

1. **评论正文含反引号或 `$` 时，先写文件再 `$(cat)`。** 内联会被 shell 当命令执行，正文静默截断。
2. **`glab api` 传字段值用 `-f` 不用 `-F`。** `-F` 做类型推断，会把看起来像数字的值送错类型。
3. **写操作后回读核对。** 退出码 0 不代表内容正确。

完整陷阱清单见 [CLI-TRAPS.md](../plugins/gitlab/skills/gitlab-core/references/CLI-TRAPS.md)：消息转义、类型推断、分页、静默失败、参数名差异、多实例识别、行号取哪一侧。

## 实例能力与校准基准

技能内容来自 **GitLab CE 16.11 + glab 1.124** 的实测。换实例、升级版本或换订阅级别后，先按 [SERVER-MATRIX.md](../plugins/gitlab/skills/gitlab-core/references/SERVER-MATRIX.md) 的探测步骤确认，不要直接套用旧结论。

常见的版本差异：

| 能力 | 状态 | 替代 |
| --- | --- | --- |
| MR 评论、行内评论、草稿评审、批准、合并 | 可用 | — |
| `glab mr diff --raw` | 不可用 | 用 `glab mr diff` 或 `/changes` 端点 |
| `new_lines` / `old_lines` 字段 | 不返回 | 从 `diff` 文本数增删行 |
| `POST /glql` | 需 18.7+ | 普通 REST 加 `jq` 过滤 |
| Epics、group work_items | 需 Premium | — |
| `/work_items` REST | 不可用 | 用同一 IID 的 issues 端点 |

对照表与排查顺序见 [SERVER-MATRIX.md](../plugins/gitlab/skills/gitlab-core/references/SERVER-MATRIX.md)。

## 写操作安全

审批、评论、发布草稿这类动作会在服务器上留下别人可见的痕迹。默认只读；发布前确认发什么、发到哪、发几条；批量发布尤其要确认，因为它会发出该 MR 上你所有的草稿。

几条容易忽略的限制：

- **系统通知删不掉**。批准再撤销后，MR 上会永久留下两条系统记录，API 删除返回 403。不要在别人的真实 MR 上试批准。
- **`note delete` 的参数顺序与帮助文本相反**，实际是 `<iid> <note-id> --yes`。
- **草稿只有本人可见**，攒的时候不打扰别人；`publish` 一次发出全部。

完整约束、可回滚性与误操作恢复见 [SAFETY.md](../plugins/gitlab/skills/gitlab-core/references/SAFETY.md)。

## 安装

```text
/plugin marketplace add calvingit/cstack
/plugin install gitlab@cstack
```

与 `cstack` 插件没有依赖关系，只装一个也可以。
