---
name: core
description: 当其他 Skill 或用户需要 CStack 的共享判断硬约束、产物槽位、ID 约定或 Agent 角色边界时使用。本 Skill 只做索引，不自动触发，不执行任务。
---

# CStack Core - 共享内核索引

## 定位

本 Skill **只做索引**：不执行任务、不写产物、不改代码、不成为流程入口。其他 Skill 通过 Skill tool 调用它，用户也可以显式调用。`agents/openai.yaml` 声明了不自动触发。

## 文档

| 文档 | 何时读 | 内容 |
| --- | --- | --- |
| [PRINCIPLES.md](PRINCIPLES.md) | 需要确认判断边界、越权、证据或恢复的硬约束时 | 6 组不变量：范围、认知、决策、授权、证据、恢复 |
| [ARTIFACTS.md](ARTIFACTS.md) | 需要写 / 读产物槽位、字段、ID 或交接规则时 | `PROFILE` / `DECISIONS` / `SPEC` / `TECH` / `SLICES` / `EVIDENCE` 的字段、所有权与变化规则 |
| [ROLES.md](ROLES.md) | 需要确定谁执行、是否用独立实例、角色能做什么时 | 5 个核心角色与 3 个可选专业角色的责任契约、产物所有权与独立性规则 |

## 使用规则

- 只按当前任务读取相关部分，不整份加载。
- 调用本 Skill 不改变调用方的职责、授权或完成条件；它只提供共享词汇与硬约束。
- 装了本 Skill 时，各 Skill 以 `PRINCIPLES.md` / `ARTIFACTS.md` / `ROLES.md` 为准；只安装单个 Skill 时，以该 Skill 内嵌的「硬约束 / 产物」作为最小可用版本。

## 不做什么

- 不替其他 Skill 做判断，不产出任务槽位，不创建任务、状态或执行图。
- 不因为被调用就获得实现、提交、推送或发布权限。
