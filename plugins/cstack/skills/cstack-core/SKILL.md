---
name: cstack-core
description: 仅当用户手动触发，或任务需要读取共享判断约束、产物类型、ID 约定、共享判据或 Agent 角色边界时使用。
disable-model-invocation: true
---

# cstack-core · 共享内核索引

## 定位

本 Skill **只做索引**：提供共享判断约束、产物字段、共享判据与角色契约，不执行任务、不写产物、不改代码，也不替其他 Skill 做判断。其他 Skill 通过读取本目录文件使用它，不需要调用 Skill；读取本身不扩大任何权限。

## 文档索引

| 文档 | 何时读 | 内容 |
| --- | --- | --- |
| [PRINCIPLES.md](PRINCIPLES.md) | 需要确认判断边界、越权、证据或恢复的强制约束时 | 范围、认知、决策、授权、证据、恢复 6 组不变量；含工作状态与验证状态的区分 |
| [ARTIFACTS.md](ARTIFACTS.md) | 需要写 / 读产物、字段、ID 或交接规则时 | `PROFILE` / `DECISIONS` / `SPEC` / `TECH` / `SLICES` / `EVIDENCE` 的字段、所有权与变化规则；`ADR`、界面设计系统与 `EVIDENCE` 的粒度 |
| [CRITERIA.md](CRITERIA.md) | 需要判断证据是否够、测量是否可比、测试是否有效、问题如何分级时 | 证明层级、可比基线、测试有效性、问题分级与处置 |
| [ROLES.md](ROLES.md) | 需要确定谁执行、是否用独立实例、角色能做什么时 | 5 个核心角色与 3 个可选专业角色的责任契约、产物所有权与独立性规则 |

## 使用规则

- 只按当前任务读取相关部分，不整份加载。
- 读取本目录不改变调用方的职责、授权或完成条件，也不因此获得实现、提交、推送或发布权限。
- 安装整套 Skill 时，以 `PRINCIPLES.md` / `ARTIFACTS.md` / `CRITERIA.md` / `ROLES.md` 为准；只安装单个 Skill 时，以该 Skill 内嵌的「强制约束 / 产物 / 判据」作为最小可用版本。
