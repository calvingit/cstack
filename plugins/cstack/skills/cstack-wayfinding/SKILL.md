---
name: cstack-wayfinding
description: 仅当用户手动触发，要求用一张地图和决策工单推进跨会话、方向还看不清的大块工作时使用。已经清楚的小改动不要用。
disable-model-invocation: true
---

# cstack-wayfinding · 跨会话梳理线索并建立地图

## 目标

把跨会话的大工作梳理成线索，画成一张共享地图，一次解决一个决策，直到通往目的地的路清楚。

## 强制约束

- 只做规划，不直接实施：每张决策工单只处理一个决策；地图在通往目的地的路清楚时结束。
- 不在地图之外擅自扩大范围；超出目的地的内容属于 Out of scope，不是尚未说清的项。
- 一次会话最多关闭一张决策工单；`cstack-research` 类工单可以并行派发。
- 地图与工单是共享记录，不是新的运行状态机。

## 产物

- **读**：松散想法、项目现状、已有文档与 ADR。
- **写**：MAP（Destination、Notes、Decisions so far、Not yet specified、Out of scope）和决策工单（Question、类型、blocked-by）。沿用项目已有的任务系统或跟踪工具；不建第二套状态。
- 需要与其他 Skill 统一产物命名、字段或共享判据时，读取 `cstack-core` 的 `ARTIFACTS.md`、`PRINCIPLES.md`、`CRITERIA.md` 对应小节；未安装时以本节作为最小可用版本。

## 地图

- **Destination**：到达终点是什么样（一份 SPEC、一个已经确定的决策，或一次就地改动），一两行；每次会话先确认。
- **Notes**：领域、需要咨询的 Skill、长期偏好。
- **Decisions so far**：已关闭工单的索引，一行摘要加链接，不重复细节。
- **Not yet specified（尚未说清）**：知道要来、但现在还说不清的决策；能说清问题才升成工单。
- **Out of scope**：明确排除的工作，不再转为工单。

## 决策工单类型

- **`cstack-research`**（AFK）：查阅资料，查清决策所依赖的事实。
- **`cstack-prototype`**（HITL）：做一个能回答当前问题的一次性原型，让人对照实物做决定。
- **grilling**（HITL）：通过对话达成决策，调用 `cstack-clarify`。
- **task**（HITL / AFK）：为解锁决策必须先做的手工工作。

## 前沿与阻塞

- 工单声明 blocked-by；无阻塞且无人认领的工单构成前沿。
- 认领时先标记归属再开始，支持多会话并行。
- 未明确项只应出现在通往目的地的路径上：能说清问题就建工单，不能就留在 Not yet specified，不提前切片。

## 两种调用

- **画图**：
  1. 命名目的地（用 `cstack-clarify` / `cstack-domain-model`）。
  2. 广度扫描，找出尚未说清的项。
  3. 建地图，把现在能说清的问题建成工单，并标出依赖关系。
  4. 并行执行 `cstack-research` 类工单后停止。
- **推进**：
  1. 先看地图概览。
  2. 选一张前沿工单并认领。
  3. 按 Notes 调用对应 Skill 处理。
  4. 记录答案、关闭工单、更新 Decisions so far，把新近能说清的事项升级为工单。

## 停止与交接

- 规划本身不授权实现；目的地到达后交给 `cstack-specify` / `cstack-tech-design` / `cstack-slice`。
- 会话中断需要交接时用 `cstack-handoff` 引用地图与工单，不重画。
- 不建立与项目 issue / tracker 并行的持久状态。
